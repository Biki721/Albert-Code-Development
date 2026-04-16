from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import pandas as pd
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import work_phase_3 as work
from url_utils import load_home_prefixes, is_home_redirect_playwright
from metric_report import log_module_metric
from urllib.parse import urlparse

from pathlib import Path

BASE_DIR = Path(__file__).parent

HOME_PREFIXES = load_home_prefixes(str(BASE_DIR /'config/home_pages.txt'))

def is_element_visible(element) -> bool:
    """
    Check if element is rendered via CSS (not hidden).
    More permissive than is_visible() - doesn't require viewport visibility.
    Returns True if visible, False if hidden.
    If check fails, returns True (permissive approach).
    """
    try:
        is_displayed = element.evaluate("""
            el => {
                const style = window.getComputedStyle(el);
                if (style.display === 'none') return false;
                if (style.visibility === 'hidden') return false;
                return true;
            }
        """)
        return is_displayed
    except Exception:
        return True


class PRP:
    base_url = "https://partner.hpe.com"
    delayed_loading_links = [s.strip() for s in work.doc_reader(str(BASE_DIR /"delayed_loading.docx")) if s.strip()]
    absurd_links = [s.strip() for s in work.doc_reader(str(BASE_DIR /"absurd_links.docx")) if s.strip()]

    def __init__(self, username, password, region, country, language, acc_type):
        self.username = username
        self.password = password
        if region == "NA":
            region = "NAR"
        self.region = region
        self.country = country
        self.language = language
        self.account_type = acc_type
        self.page_tree_path = BASE_DIR / "Page Trees" / f"PageTree{self.region}_{self.country}_{self.language}_{self.account_type}.txt"
        self.report_path = BASE_DIR /'Reports'/f'New_Tab_{self.region}_{self.country}_{self.language}_{self.account_type}.xlsx'
        self.aruba_links_path = BASE_DIR/'Aruba Urls'/f'Aruba{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.tree_dict_path = BASE_DIR/'Tree Dicts'/f'TreeDict{self.region}_{self.country}_{self.language}_{self.account_type}.json'
        self.lock = threading.Lock()
        
        # NEW: Country verification tracking
        self.last_country_check = time.time()
        self.country_check_interval = 120  # Re-verify every 2 minutes
        self.pages_checked_since_last = 0
        self.check_every_n_pages = 10  # Also check every 10 pages

    # -------------------------------------------------------------------------------------
    # SETUP (using Playwright)
    # -------------------------------------------------------------------------------------
    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)

    
    def country_similarity(self, a: str, b: str):
        """
        Fully dynamic similarity score between two country names.
        No static list, no mappings, no assumptions.
        Uses:
        - token overlap
        - partial character similarity
        """
        if not a or not b:
            return 0

        a = a.lower()
        b = b.lower()

        # Token-based similarity
        a_tokens = set(a.replace("(", " ").replace(")", " ").split())
        b_tokens = set(b.replace("(", " ").replace(")", " ").split())

        token_overlap = len(a_tokens & b_tokens)
        token_total = max(len(a_tokens), 1)

        token_score = token_overlap / token_total  # 0.0 → 1.0

        # Character similarity (dynamic)
        matches = sum(1 for ch in a if ch in b)
        char_score = matches / max(len(a), 1)

        # Weighted final score
        return (token_score * 0.6) + (char_score * 0.4)


    # -------------------------------------------------------------------------------------
    # HANDLE OVERLAY, EYEBALL, AND COUNTRY SELECTION
    # -------------------------------------------------------------------------------------
    def handle_country_and_overlay(self, force_recheck=False):
        page = self.page
        time.sleep(5)
        # --- STEP 1: Check and close notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5000)
            if overlay and overlay.is_visible():
                if force_recheck:
                    print("🔔 Notification overlay detected (re-check).")
                else:
                    print("⚠️ Notification overlay detected.")
                try:
                    page.click("#closemsg")
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                print("✅ Closed the notification overlay.")
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=10000)
                except Exception:
                    pass
        except PlaywrightTimeoutError:
            if not force_recheck:
                print("✅ No overlay appeared, continuing.")
        except Exception as e:
            if not force_recheck:
                print("⚠️ Overlay handling error:", e)
        
        # time.sleep(3 if force_recheck else 10)

        # --- STEP 2: Click Eyeball icon ---
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", timeout=30000)
            if eyeball:
                eyeball.click()
        except Exception:
            pass
        # time.sleep(2 if force_recheck else 10)

        # --- STEP 3: Extract current country ---
        try:
            selector = (
                '#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet '
                '> div > div.portlet-content-container > div > div.MHMGuserdescrp '
                '> div > div.MHMGcountryname'
            )
            country_element = page.wait_for_selector(selector, timeout=20000)
            current_country = country_element.inner_text().strip() if country_element else ""
            
            if force_recheck:
                print(f"🔄 Country re-check: {current_country if current_country else 'Unknown'}")
            else:
                print(f"🌍 Current Country: {current_country if current_country else 'Unknown'}")
        except Exception:
            current_country = ""
            if not force_recheck:
                print("⚠️ Could not detect current country")
        
        # time.sleep(2 if force_recheck else 10)

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", timeout=15000)
            if loc_btn:
                loc_btn.click()
        except Exception:
            pass
        # time.sleep(2 if force_recheck else 10)

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", timeout=15000)
        except Exception:
            pass
        # time.sleep(2 if force_recheck else 10)

        # --- STEP 6: Switch country if needed ---
        try:
            if current_country.lower() == self.country.lower():
                if force_recheck:
                    print(f"✅ Country still correctly set to '{current_country}'")
                else:
                    print(f"✅ Country already set to '{current_country}'")
                
                # Close eyeball dropdown
                try:
                    page.keyboard.press("Escape")
                except:
                    pass
            else:
                if force_recheck:
                    print(f"⚠️ COUNTRY CHANGED! Resetting from '{current_country}' to '{self.country}'")
                
                options = page.query_selector_all("ul#MHMGBRcountries li.locationsBRlist")

                best_score = 0
                best_option = None
                best_name = ""

                for opt in options:
                    try:
                        cname = opt.get_attribute("countryname") or opt.inner_text().strip()
                    except:
                        continue

                    score = self.country_similarity(self.country, cname)

                    if score > best_score:
                        best_score = score
                        best_option = opt
                        best_name = cname

                # Threshold ensures we don't pick a completely unrelated country
                if best_score >= 0.30 and best_option:
                    try:
                        best_option.click()
                    except Exception:
                        page.evaluate("(el)=>el.click()", best_option)

                    print(f"🌐 Country dynamically matched → '{best_name}' (score={best_score:.2f})")

                    br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div", timeout=15000)
                    if br_container:
                        br_container.click()
                else:
                    print(f"⚠️ No strong dynamic match for '{self.country}'. Best score={best_score:.2f}")

        except Exception:
            pass

        # time.sleep(3 if force_recheck else 10)
        return current_country

    # NEW METHOD: Verify country is still correct
    def verify_country_setting(self):
        """
        Quick check to ensure country hasn't been reset during new tab checks.
        Called periodically based on time AND page count.
        
        Since we navigate to internal PRP pages for checks, we don't need to 
        navigate anywhere - just check the country setting directly.
        """
        current_time = time.time()
        
        # Check based on EITHER time elapsed OR pages checked
        time_check = (current_time - self.last_country_check) >= self.country_check_interval
        page_check = self.pages_checked_since_last >= self.check_every_n_pages
        
        if not (time_check or page_check):
            return
        
        print(f"\n{'='*80}")
        print(f"🔍 Periodic Country Verification")
        print(f"   Time since last check: {current_time - self.last_country_check:.1f}s")
        print(f"   Pages since last check: {self.pages_checked_since_last}")
        print(f"{'='*80}")
        
        try:
            # Check if page exists and is on PRP domain
            if self.page is None:
                print("⚠️ Page not available for country check")
                return
            
            current_url = self.page.url
            
            # If somehow we ended up on external page, go back to PRP
            if not current_url.startswith("https://partner.hpe.com"):
                print(f"⚠️ Page on external URL: {current_url[:50]}...")
                print(f"   Navigating back to PRP home")
                self.page.goto(self.base_url + "/group/prp/home", timeout=20000)
                time.sleep(3)
            
            # Re-run country check (no additional navigation needed - already on PRP)
            self.handle_country_and_overlay(force_recheck=True)
            
            # Update last check time and reset page counter
            self.last_country_check = current_time
            self.pages_checked_since_last = 0
            
        except Exception as e:
            print(f"⚠️ Error during country verification: {e}")
        
        print(f"{'='*80}\n")


    # -------------------------------------------------------------------------------------
    # LOGIN
    # -------------------------------------------------------------------------------------
    def test_load_home_page(self):
        page = self.page

        page.goto(self.base_url)

        page.fill("#oktaEmailInput", self.username)
        page.click("#oktaSignInBtn")
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")

        time.sleep(10)
        # Handle overlay + eyeball + country selection
        current_country = self.handle_country_and_overlay()
        time.sleep(5)


    # -------------------------------------------------------------------------------------
    # SIMPLE AND RELIABLE: CHECK TARGET ATTRIBUTE
    # -------------------------------------------------------------------------------------
    def check_link_opens_new_tab(self, anchor, href):
        """
        SIMPLE APPROACH: Check if link will open in new tab based on HTML attributes.
        
        Returns: (opens_new_tab: bool, reason: str)
        """
        try:
            # Get target attribute
            target = anchor.get_attribute('target')
            
            # Check for explicit new tab/window targets
            if target and target.lower() in ['_blank', '_new', 'blank']:
                return (True, f"Has target='{target}'")
            
            # Check for JavaScript onclick that opens new window
            onclick = anchor.get_attribute('onclick')
            if onclick and 'window.open' in onclick:
                return (True, "Has onclick with window.open()")
            
            # Check if link has any JavaScript event that might open new tab
            # This catches frameworks that add behavior dynamically
            has_js_behavior = anchor.evaluate("""
                el => {
                    // Check for event listeners that might open new tabs
                    const onclick = el.onclick;
                    if (onclick && onclick.toString().includes('window.open')) {
                        return true;
                    }
                    return false;
                }
            """)
            
            if has_js_behavior:
                return (True, "Has JavaScript behavior for new tab")
            
            # If no target attribute or it's _self, it opens same tab
            if target and target.lower() in ['_self', '_parent', '_top']:
                return (False, f"Has target='{target}' (same window)")
            
            # No target attribute = opens in same tab by default
            return (False, "No target attribute (default same-tab behavior)")
            
        except Exception as e:
            # If we can't determine, assume it's an issue
            return (False, f"Could not determine behavior: {str(e)[:50]}")


    # -------------------------------------------------------------------------------------
    # MAIN TEST - SIMPLE ATTRIBUTE-BASED VALIDATION
    # -------------------------------------------------------------------------------------
    @log_module_metric("New Tab")
    def test_new_tab(self):
        self.test_load_home_page()

        notopening = []
        page = self.page
        
        total_links_tested = 0
        total_pages_tested = 0
        total_correct = 0
        total_incorrect = 0
        skipped_footer = 0
        start_time = time.time()

        def demo_test(site_url):
            nonlocal total_links_tested, total_pages_tested, total_correct, total_incorrect, skipped_footer
            
            site_url = site_url.strip()
            if not site_url:
                return

            total_pages_tested += 1
            
            # *** NEW: Increment page counter for country verification ***
            self.pages_checked_since_last += 1
            
            print(f"\n{'='*80}")
            print(f"🔍 Page #{total_pages_tested}: {site_url}")
            print(f"{'='*80}")

            try:
                page.goto(site_url)

                # Skip homepage redirects
                try:
                    if is_home_redirect_playwright(page, HOME_PREFIXES):
                        print(f"⏭️  Skipped (home redirect)")
                        return
                except Exception:
                    pass

                # Delay for slow links
                if site_url in self.delayed_loading_links or site_url in self.absurd_links:
                    print(f"⏳ Waiting 25s for slow-loading page...")
                    time.sleep(25)

            except Exception as e:
                print(f"❌ Failed to load page: {e}")
                return

            # Collect all <a> tags
            try:
                anchors = page.query_selector_all("a")
                print(f"📊 Found {len(anchors)} total links")
            except:
                print(f"❌ Failed to query anchors")
                return

            # Filter external links and skip footer
            external_links = []
            for a in anchors:
                try:
                    href = a.get_attribute("href")
                    if not href or not href.startswith("http"):
                        continue

                    # Only visible links
                    if not is_element_visible(a):
                        continue

                    # Skip footer links
                    try:
                        is_in_footer = a.evaluate("""
                            el => {
                                let current = el;
                                while (current) {
                                    if (current.tagName === 'FOOTER' || 
                                        current.id === 'footer' ||
                                        current.className && (
                                            current.className.includes('footer') ||
                                            current.className.includes('Footer')
                                        )) {
                                        return true;
                                    }
                                    current = current.parentElement;
                                }
                                return false;
                            }
                        """)
                        if is_in_footer:
                            skipped_footer += 1
                            continue
                    except Exception:
                        pass

                    # Only external links
                    href_domain = urlparse(href).netloc.lower()
                    base_domain = urlparse(self.base_url).netloc.lower()

                    if href_domain == base_domain:
                        continue

                    external_links.append((a, href))
                except Exception:
                    continue

            print(f"🔗 Found {len(external_links)} external links (skipped {skipped_footer} footer)")

            # Test each external link - SIMPLE APPROACH
            for idx, (a, href) in enumerate(external_links, 1):
                total_links_tested += 1
                
                print(f"  [{idx}/{len(external_links)}] {href[:70]}...")
                
                try:
                    # SIMPLE: Just check the HTML attributes
                    opens_new_tab, reason = self.check_link_opens_new_tab(a, href)
                    
                    if opens_new_tab:
                        print(f"    ✅ Opens new tab: {reason}")
                        total_correct += 1
                    else:
                        print(f"    ❌ Opens same tab: {reason}")
                        total_incorrect += 1
                        notopening.append([site_url, href, reason])
                
                except Exception as e:
                    print(f"    ⚠️  Error: {e}")
                    continue

            print(f"✅ Page complete - Issues: {sum(1 for x in notopening if x[0] == site_url)}")

        # Read tree
        with open(self.page_tree_path, "r") as f:
            lines = f.readlines()

        print(f"\n{'#'*80}")
        print(f"🚀 Starting New Tab Test (Simple Attribute Check)")
        print(f"📄 Pages to test: {len(lines)}")
        print(f"{'#'*80}\n")

        for line in lines:
            # *** NEW: Periodic country verification ***
            self.verify_country_setting()
            
            demo_test(line)

        # Final summary
        elapsed = time.time() - start_time
        print(f"\n{'#'*80}")
        print(f"✅ TEST COMPLETE")
        print(f"📊 Statistics:")
        print(f"   - Pages tested: {total_pages_tested}")
        print(f"   - External links tested: {total_links_tested}")
        print(f"   - Footer links skipped: {skipped_footer}")
        print(f"   - Correct UX (opens new tab): {total_correct}")
        print(f"   - Incorrect UX (same tab): {total_incorrect}")
        print(f"   - Time elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"   - Avg time per link: {elapsed/total_links_tested:.3f}s" if total_links_tested > 0 else "")
        print(f"{'#'*80}\n")

        # Write Excel
        self.write_excel(notopening)

    # -------------------------------------------------------------------------------------
    def write_excel(self, notopening):
        rows = []
        issueid = 1

        for item in notopening:
            if len(item) >= 3:
                src, badlink, description = item[0], item[1], item[2]
            else:
                src, badlink = item[0], item[1]
                description = "Link not opening in a new tab"
            
            rows.append([
                issueid,
                self.username,
                "New Tab",
                self.region,
                self.country,
                self.language,
                src,
                badlink,
                description,
                datetime.datetime.now(),
                "",
                "New",
                "-"
            ])
            issueid += 1

        df = pd.DataFrame(
            rows,
            columns=[
                'Issue ID','Demo Account','Category','Region','Country','Language',
                'Link','Error Link','Description','Time Identified',
                'Mail ID','Status','Comments'
            ]
        )

        df.to_excel(self.report_path, index=False)
        print(f"📝 Report saved: {self.report_path}")

    # -------------------------------------------------------------------------------------
    def tearDown(self):
        self.browser.close()
        self.pw.stop()

        df = pd.read_excel(self.report_path)

        if len(df) > 0:
            work.work_alloc_execute(
                self.report_path,
                'Fixers_list.xlsx',
                self.aruba_links_path
            )

# -----------------------------------------------------------------------------------------
# RUN MULTIPLE ACCOUNTS IN PARALLEL
# -----------------------------------------------------------------------------------------
def run_account(account):
    try:
        bot = PRP(*account)
        bot.setUp()
        bot.test_new_tab()
        bot.tearDown()
        print(f"Finished processing: {account[0]}")
    except Exception as e:
        print(f"Error processing {account[0]}: {e}")


if __name__ == '__main__':
    credentials = [
         ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'],
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Brazil', 'English', 'distri'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
        # ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Spain', 'Spanish', 'T2'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'South Korea', 'English', 'T2'],
    ]

    with ThreadPoolExecutor(max_workers=1) as exe:
        exe.map(run_account, credentials)