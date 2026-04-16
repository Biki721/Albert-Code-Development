import time
import datetime
import threading
import ast
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import urllib3
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

import work_phase_3 as work
from metric_report import log_module_metric

from pathlib import Path

BASE_DIR = Path(__file__).parent

# HTTP client with short timeouts
timeout = urllib3.util.Timeout(connect=2.0, read=1.0)
http = urllib3.PoolManager(timeout=timeout)

# -------------------------------------------------------------------
# INTERNAL LINK CHECKER: AUTH + REDIRECT + BODY SCAN
# -------------------------------------------------------------------
def is_internal_broken(page, link):
    """
    Check PRP internal link using authenticated, redirect-aware request.
    """
    # 2) Allowed redirect targets → NOT broken
    allowed_redirects = (
        "https://partner.hpe.com/",
        "https://partner.hpe.com/home",
        "https://partner.hpe.com/group/prp",
        "https://partner.hpe.com/group/prp/home",
        "https://partner.hpe.com/group/prp/home?tutorial=homepage",
    )

    strong_markers = [
        "we can't find the page you're looking for",
        "404 - page not found",
        "page not available",
        "content expired",
        "unable to display the page you have requested",
        "request has invalid parameter",
        "Oops! We can't find that page.",
        "the page you are looking for no longer exists",
        "the page you're looking for no longer exists"
    ]

    try:
        resp = None
        try:
            resp = page.goto(link, wait_until="networkidle")
        except PlaywrightTimeoutError:
            # Even on timeout, page.url may still reflect the final location
            pass

        final_url = page.url or (resp.url if resp is not None else "")

        try:
            split = urlsplit(final_url)
            base_url = f"{split.scheme}://{split.netloc}{split.path}"
        except Exception:
            base_url = final_url

        if base_url in allowed_redirects:
            return False

        # 1) HTTP status check → true broken
        if resp is not None and hasattr(resp, "status") and resp.status >= 400:
            return True

        # 3) Check content for REAL error templates
        try:
            body = page.content().lower()
        except Exception:
            try:
                body = resp.text().lower() if resp is not None else ""
            except Exception:
                body = ""

        for m in strong_markers:
            if m in body:
                return True

        return False
    except Exception:
        return True


# -------------------------------------------------------------------
# MAIN CLASS (YOUR ORIGINAL STRUCTURE)
# -------------------------------------------------------------------
class PRP:
    base_url = "https://partner.hpe.com"

    links_to_exclude = work.doc_reader(str(BASE_DIR /"lte_external.docx"))
    links_to_exclude = [s.strip() for s in links_to_exclude if s]

    def __init__(self, username, password, region, country, language, acc_type):
        self.username = username
        self.password = password

        if region == "NA":
            region = "NAR"

        self.region = region
        self.country = country
        self.language = language
        self.account_type = acc_type

        # Path Templates
        self.page_tree_path = BASE_DIR/"Page Trees"/f"PageTree{region}_{country}_{language}_{acc_type}.txt"
        self.document_links = BASE_DIR/"DocumentLinks"/f"Doclinks{region}_{country}_{language}_{acc_type}.txt"
        self.reverse_dict_path = BASE_DIR/"Reverse Dicts"/f"RevDict{region}_{country}_{language}_{acc_type}.txt"
        self.report_path = BASE_DIR/"Reports"/f"Broken_Link_{region}_{country}_{language}_{acc_type}.xlsx"
        self.aruba_links_path = BASE_DIR/"Aruba Urls"/f"Aruba{region}_{country}_{language}_{acc_type}.txt"

        self.lock = threading.Lock()
        self.pw = None
        self.browser = None
        self.page = None
        
        # NEW: Track last country verification time
        self.last_country_check = time.time()
        self.country_check_interval = 120  # Re-verify every 2 minutes

    # ------------------------------------------------------------------
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

        # --- STEP 1: Check and close notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5000)
            if overlay and overlay.is_visible():
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
            if force_recheck:
                print("✅ No overlay appeared, continuing.")
        except Exception as e:
            if force_recheck:
                print("⚠️ Overlay handling error:", e)
         

        # --- STEP 2: Click Eyeball icon ---
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", timeout=30000)
            if eyeball:
                eyeball.click()
        except Exception:
            pass
         

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
            if force_recheck:
                print("⚠️ Could not detect current country during re-check")
            else:
                print("⚠️ Could not detect current country")
         

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", timeout=15000)
            if loc_btn:
                loc_btn.click()
        except Exception:
            pass
         

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", timeout=15000)
        except Exception:
            pass
         

        # --- STEP 6: Switch country if needed ---
        try:
            if current_country.lower() == self.country.lower():
                if force_recheck:
                    print(f"✅ Country still correctly set to '{current_country}'")
                else:
                    print(f"✅ Country already set to '{current_country}'")
                    
                # Close eyeball dropdown even if country is correct
                try:
                    # Click outside or press ESC to close
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

        time.sleep(5)  # Reduced from 8 to 5 for re-checks
        return current_country


    # NEW METHOD: Verify country is still correct
    def verify_country_setting(self):
        """
        Quick check to ensure country hasn't been reset.
        Called periodically during link testing.
        
        Since external links are tested via urllib3 (not browser navigation),
        the page should already be on a PRP page. We just need to check
        the country setting without navigating anywhere.
        """
        current_time = time.time()
        
        # Only check if enough time has passed
        if current_time - self.last_country_check < self.country_check_interval:
            return
        
        print(f"\n{'='*80}")
        print(f"🔍 Periodic Country Verification (every {self.country_check_interval}s)")
        print(f"{'='*80}")
        
        try:
            # Check if we're on an external page (just in case)
            current_url = self.page.url
            
            # If somehow we ended up on external page, go back to PRP
            if current_url.startswith("https://partner.hpe.com"):
                # Re-run country check (no navigation needed - already on PRP)
                self.handle_country_and_overlay(force_recheck=True)
                
                # Update last check time
                self.last_country_check = current_time
            
        except Exception as e:
            print(f"⚠️ Error during country verification: {e}")
        
        print(f"{'='*80}\n")


    # ------------------------------------------------------------------
    def test_load_home_page(self):
        page = self.page

        page.goto(self.base_url)
        page.fill("#oktaEmailInput", self.username)
        page.click("#oktaSignInBtn")
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")

        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except Exception:
            pass
        time.sleep(5)
         # Handle overlay + eyeball + country selection
        current_country = self.handle_country_and_overlay()
        time.sleep(5)


    # ------------------------------------------------------------------
    @log_module_metric("Broken Links")
    def test_multiple_broken(self):
        def brokencheck():
            broken_links = []
            
            # ===== CONSOLE LOGGING: Start =====
            start_time = time.time()
            stats = {
                'total_links': 0,
                'internal_links': 0,
                'external_links': 0,
                'document_links': 0,
                'broken_count': 0,
                'internal_broken': 0,
                'external_broken': 0,
                'document_broken': 0,
                'excluded_links': 0,
                'skipped_download_links': 0
            }
            
            print(f"\n{'#'*80}")
            print(f"🔍 Starting Broken Link Test")
            print(f"{'#'*80}\n")

            with open(self.page_tree_path, encoding="utf-8") as f:
                page_links = f.read().splitlines()

            with open(self.document_links, encoding="utf-8") as f:
                doc_links = f.read().splitlines()

            all_links = page_links + doc_links
            doc_set = {x.strip() for x in doc_links if x.strip()}
            
            print(f"📊 Link Sources:")
            print(f"   - Page links found: {len(page_links)}")
            print(f"   - Document links found: {len(doc_links)}")
            print(f"   - Total raw links: {len(all_links)}")

            # Clean & dedupe
            seen = set()
            final_links = []
            for raw in all_links:
                link = raw.strip()
                if not link:
                    continue
                if link in seen:
                    continue
                if link in self.links_to_exclude:
                    stats['excluded_links'] += 1
                    continue
                seen.add(link)
                final_links.append(link)

            stats['total_links'] = len(final_links)
            
            print(f"   - Excluded links: {stats['excluded_links']}")
            print(f"   - Unique links to test: {stats['total_links']}")
            print(f"\n{'='*80}")
            print(f"🚀 Testing Links...")
            print(f"{'='*80}\n")

            page = self.page

            for idx, link in enumerate(final_links, 1):
                # *** NEW: Periodic country verification ***
                self.verify_country_setting()
                
                # Progress indicator
                elapsed = time.time() - start_time
                avg_time = elapsed / idx if idx > 0 else 0
                
                print(f"[{idx}/{stats['total_links']}] Testing: {link[:70]}...")
                print(f"   ⏱️  Elapsed: {elapsed:.1f}s | Avg: {avg_time:.2f}s/link | Broken: {stats['broken_count']}")
                
                # SKIP DOWNLOAD LINKS - they trigger downloads, not broken!
                if "download=true" in link.lower() or "download=1" in link.lower():
                    stats['skipped_download_links'] += 1
                    print(f"   ⏭️  Skipped: Download link (triggers file download)")
                    continue
                
                # -----------------------------
                # CASE 1: DOCUMENT LINKS
                # -----------------------------
                if link in doc_set:
                    stats['document_links'] += 1
                    print(f"   📄 Type: Document Link")
                    
                    # Homepage patterns - if document redirects here, SKIP (don't mark as broken)
                    homepage_patterns = [
                        "https://partner.hpe.com/",
                        "https://partner.hpe.com/home",
                        "https://partner.hpe.com/group/prp",
                        "https://partner.hpe.com/group/prp/home",
                        "https://partner.hpe.com/group/prp/home?tutorial=homepage",
                    ]
                    
                    try:
                        # Use GET to follow redirects and check final URL
                        resp = page.request.get(link, max_redirects=5)
                        status = resp.status if resp and hasattr(resp, "status") else None
                        final_url = resp.url if resp and hasattr(resp, "url") else ""
                        
                        # Normalize final URL (remove trailing slash and query params for comparison)
                        try:
                            from urllib.parse import urlsplit
                            split = urlsplit(final_url)
                            normalized_final = f"{split.scheme}://{split.netloc}{split.path}".rstrip('/')
                        except:
                            normalized_final = final_url.rstrip('/')
                        
                        # Check if redirected to homepage
                        is_homepage_redirect = False
                        for homepage in homepage_patterns:
                            normalized_homepage = homepage.rstrip('/')
                            if normalized_final == normalized_homepage or normalized_final + '/' == normalized_homepage:
                                is_homepage_redirect = True
                                break
                        
                        # SKIP homepage redirects (expected behavior for deleted/moved documents)
                        if is_homepage_redirect:
                            stats['skipped_download_links'] += 1  # Use same counter for skipped items
                            print(f"   ⏭️  Skipped: Redirects to homepage (document moved/deleted)")
                        elif status is not None:
                            # Check status code only if not homepage redirect
                            if 200 <= status < 300:
                                print(f"   ✅ OK: HTTP {status}")
                            elif 400 <= status < 500:
                                # Check if 404 is actually a homepage redirect
                                # Sometimes 404 pages show homepage content
                                try:
                                    body = resp.text() if hasattr(resp, 'text') else ""
                                    if any(pattern in final_url for pattern in homepage_patterns):
                                        stats['skipped_download_links'] += 1
                                        print(f"   ⏭️  Skipped: 404 redirects to homepage")
                                    else:
                                        broken_links.append(link)
                                        stats['broken_count'] += 1
                                        stats['document_broken'] += 1
                                        print(f"   ❌ BROKEN: HTTP {status}")
                                except:
                                    broken_links.append(link)
                                    stats['broken_count'] += 1
                                    stats['document_broken'] += 1
                                    print(f"   ❌ BROKEN: HTTP {status}")
                            elif status >= 500:
                                print(f"   ⚠️  Server error (not marking as broken): HTTP {status}")
                            else:
                                print(f"   ⚠️  Unexpected status: HTTP {status}")
                        else:
                            print(f"   ⚠️  No status received (network issue)")
                            
                    except Exception as e:
                        # Ignore transient network errors for documents to reduce false positives
                        print(f"   ⚠️  Skipped (transient error): {str(e)[:50]}")
                        pass

                    continue

                # -----------------------------
                # CASE 2: INTERNAL PRP LINKS
                # -----------------------------
                if link.startswith("https://partner.hpe.com"):
                    stats['internal_links'] += 1
                    print(f"   🏠 Type: Internal PRP Link")
                    
                    if is_internal_broken(page, link):
                        broken_links.append(link)
                        stats['broken_count'] += 1
                        stats['internal_broken'] += 1
                        print(f"   ❌ BROKEN: Failed internal validation")
                    else:
                        print(f"   ✅ OK")
                    continue

                # -----------------------------
                # CASE 3: EXTERNAL LINKS
                # -----------------------------
                stats['external_links'] += 1
                print(f"   🌐 Type: External Link")
                
                try:
                    r = http.request("GET", link)
                    if hasattr(r, "status") and r.status >= 400:
                        broken_links.append(link)
                        stats['broken_count'] += 1
                        stats['external_broken'] += 1
                        print(f"   ❌ BROKEN: HTTP {r.status}")
                    else:
                        print(f"   ✅ OK: HTTP {r.status}")
                except Exception as e:
                    broken_links.append(link)
                    stats['broken_count'] += 1
                    stats['external_broken'] += 1
                    print(f"   ❌ BROKEN: {str(e)[:50]}")
                
                print()  # Blank line between links

            # ===== CONSOLE LOGGING: Summary =====
            elapsed = time.time() - start_time
            
            print(f"\n{'#'*80}")
            print(f"✅ TEST COMPLETE")
            print(f"{'#'*80}")
            print(f"\n📊 Final Statistics:")
            print(f"   - Total links tested: {stats['total_links']}")
            print(f"   - Internal links: {stats['internal_links']}")
            print(f"   - External links: {stats['external_links']}")
            print(f"   - Document links: {stats['document_links']}")
            print(f"   - Excluded links: {stats['excluded_links']}")
            print(f"   - Skipped download links: {stats['skipped_download_links']}")
            print(f"\n🔴 Broken Links Found: {stats['broken_count']}")
            print(f"   - Internal broken: {stats['internal_broken']}")
            print(f"   - External broken: {stats['external_broken']}")
            print(f"   - Document broken: {stats['document_broken']}")
            print(f"\n⏱️  Performance:")
            print(f"   - Time elapsed: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
            print(f"   - Avg time per link: {elapsed/stats['total_links']:.2f}s" if stats['total_links'] > 0 else "")
            print(f"   - Success rate: {((stats['total_links'] - stats['broken_count']) / stats['total_links'] * 100):.1f}%" if stats['total_links'] > 0 else "")
            print(f"{'#'*80}\n")

            write_excel(broken_links)

        # ------------------------------------------------------------------
        def write_excel(broken_links):
            print(f"📝 Writing report to Excel...")
            
            with open(self.reverse_dict_path, encoding="utf-8") as f:
                dictionary = ast.literal_eval(f.read())

            norm_dict = {str(k).strip(): v for k, v in dictionary.items()}

            rows = []
            issue_id = 1

            for bad in broken_links:
                parents = norm_dict.get(bad.strip(), [])
                source = ""

                if parents:
                    last = parents[-1]
                    first = parents[0]
                    source = first if last == bad and len(parents) > 1 else last

                rows.append([
                    issue_id,
                    self.username,
                    "Broken Link",
                    self.region,
                    self.country,
                    self.language,
                    source,
                    bad,
                    "Broken link",
                    datetime.datetime.now(),
                    "",
                    "New",
                    "-"
                ])

                issue_id += 1

            df = pd.DataFrame(rows, columns=[
                "Issue ID", "Demo Account", "Category", "Region", "Country",
                "Language", "Link", "Error Link", "Description", "Time Identified",
                "Mail ID", "Status", "Comments"
            ])

            df.to_excel(self.report_path, index=False)
            print(f"✅ Report saved: {self.report_path}")

        brokencheck()

    # ------------------------------------------------------------------
    def tearDown(self):
        try:
            if self.browser:
                self.browser.close()
        except:
            pass

        try:
            if self.pw:
                self.pw.stop()
        except:
            pass

        try:
            df = pd.read_excel(self.report_path)
            if len(df) > 0:
                work.work_alloc_execute(
                    self.report_path, "Fixers_list.xlsx", self.aruba_links_path
                )
        except FileNotFoundError:
            pass


# -------------------------------------------------------------------
# RUNNER
# -------------------------------------------------------------------
def run_account(account):
    try:
        prp = PRP(*account)
        prp.setUp()
        prp.test_load_home_page()
        prp.test_multiple_broken()
        prp.tearDown()

        from playsound3 import playsound
        playsound("Sound\\beep-01a.wav")
        print("Finished:", account[0])

    except Exception as e:
        print("Error with", account[0], ":", e)


if __name__ == "__main__":
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'],
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Brazil', 'English', 'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'APJ', 'China', 'Simplified Chinese', 'T2'],
        # ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ', 'Indonesia', 'Indonesian', 'distri'],
        # ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey', 'Turkish', 'T2']
    ]

    with ThreadPoolExecutor(max_workers=2) as exe:
        exe.map(run_account, credentials)