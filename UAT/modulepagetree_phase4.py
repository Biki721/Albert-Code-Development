import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse, urlunparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import work_phase_3 as work
import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent

# Enhanced logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / 'crawler.log', encoding='utf-8')
    ]
)


# -------------------------
# Helper Functions
# -------------------------
def normalize_url(base: str, href: str) -> str:
    """
    Normalize href relative to base using urljoin and strip fragments.
    Returns empty string for invalid hrefs.
    """
    if not href:
        return ""
    href = href.strip()
    
    # Skip non-URL patterns
    if href.startswith(('javascript:', 'mailto:', 'tel:', 'data:')):
        return ""
    
    # Skip just hash fragments
    if href == '#':
        return ""
    
    try:
        joined = urljoin(base, href)
        parsed = urlparse(joined)
        # Remove fragment but keep query parameters
        cleaned = urlunparse((parsed.scheme, parsed.netloc, parsed.path, 
                            parsed.params, parsed.query, ""))
        return cleaned
    except Exception:
        return ""


def looks_like_doc(url: str) -> bool:
    """Check if URL points to a document/file."""
    if not url:
        return False
    lower = url.lower()
    return any(ext in lower for ext in [
        ".pdf", ".xlsx", ".xls", ".doc", ".docx", ".zip", 
        ".ppt", ".pptx", ".txt", "/documents", "/esm"
    ])


def is_same_domain(url: str, domain: str = "partner.hpe.com") -> bool:
    """Check if URL belongs to specified domain."""
    try:
        return urlparse(url).netloc.endswith(domain)
    except Exception:
        return False


def is_element_visible(element) -> bool:
    """Advanced visibility detection - permissive for modern web apps."""
    try:
        visible = element.evaluate("""
            el => {
                // Skip Playwright's strict visibility - use real-world heuristics
                const rect = el.getBoundingClientRect();
                const style = window.getComputedStyle(el);
                
                // ❌ DON'T reject these common patterns:
                // - opacity < 1 (animations, hover states)
                // - overflow: hidden parents (modern layouts)
                // - position: absolute (cards, modals)
                
                // Only reject truly invisible elements
                if (style.display === 'none') return false;
                if (style.visibility === 'hidden') return false;
                if (rect.width <= 0 || rect.height <= 0) return false;
                
                // Accept ANY clickable area > 1x1px
                return rect.width > 1 && rect.height > 1;
            }
        """)
        return visible
    except Exception:
        # ✅ BE SUPER PERMISSIVE - include if check fails
        return True


# -------------------------
# PRP Crawler Class
# -------------------------
class PRP():
    base_url = "https://partner.hpe.com"
    
    # Load configuration files
    delayed_loading_links = work.doc_reader(str(BASE_DIR / "delayed_loading.docx"))
    delayed_loading_links = [s.strip() for s in delayed_loading_links if s != '']
    
    breadcrumblinks = work.doc_reader(str(BASE_DIR / "breadcrumb_links.docx"))
    breadcrumblinks = [s.strip() for s in breadcrumblinks if s != '']
    
    absurd_links = work.doc_reader(str(BASE_DIR / "absurd_links.docx"))
    absurd_links = [s.strip() for s in absurd_links if s != '']
    
    breadcrumb_prefix = work.doc_reader(str(BASE_DIR / "Breadcrumb_Prefix.docx"))
    breadcrumb_prefix = [s.strip() for s in breadcrumb_prefix if s != '']
    
    # Known home page patterns
    HOME_PAGES = [
        "https://partner.hpe.com",
        "https://partner.hpe.com/",
        "https://partner.hpe.com/home",
        "https://partner.hpe.com/group/prp",
        "https://partner.hpe.com/group/prp/home",
    ]

    def __init__(self, username: str, password: str, region: str, country, language, acc_type):
        self.username = username
        self.password = password
        
        if region == "NA":
            region = 'NAR'
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language
        
        # Output file paths
        self.page_tree_path = BASE_DIR/'Page Trees'/f'PageTree{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.doc_link_path = BASE_DIR/'DocumentLinks'/f'Doclinks{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.reverse_dict_path = BASE_DIR/'Reverse Dicts'/f'RevDict{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.external_urls_path = BASE_DIR/'External Urls'/f'External{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.redirect_log_path = BASE_DIR/'Redirects'/f'Redirects{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        
        self.prp_links = None
        self.lock = threading.Lock()
        self.redirect_map = {}  # Track all redirects for analysis

        # Playwright objects
        self.pw = None
        self.browser = None
        self.context = None
        self.session_page = None
        
        # NEW: Country verification tracking
        self.last_country_check = time.time()
        self.country_check_interval = 180  # Re-verify every 3 minutes (crawling is slower)
        self.pages_crawled_since_check = 0
        self.check_every_n_pages = 10  # Also check every 10 pages
    

    def setUp(self):
        """Initialize Playwright browser and context."""
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.session_page = None
        logging.info("✅ Playwright started successfully")
    
    def is_home_page(self, url: str) -> bool:
        return any(url.rstrip('/') == hp.rstrip('/') for hp in self.HOME_PAGES)
    
    def is_valid_prp_page(self, url: str) -> bool:
        return (
            url.startswith("https://partner.hpe.com") and
            not self.is_home_page(url) and
            self.filter_breadcrumbs(url)
        )

    def smart_resolve_relative(self, page, href: str) -> str:
        """
        Resolve ambiguous relative links by probing the server.
        Returns the correct absolute URL.
        """

        if href.startswith('/'):
            # Absolute path → root always wins
            return f"https://partner.hpe.com{href}"

        # Candidate 1: PRP-scoped
        prp_candidate = urljoin(page.url, href)

        # Candidate 2: Root-scoped
        root_candidate = f"https://partner.hpe.com/{href.lstrip('/')}"

        try:
            # Lightweight HEAD probe (no DOM load)
            resp = page.request.head(prp_candidate, timeout=8000)
            if resp.ok:
                # Check if it silently redirects to home
                final_url = resp.url
                if not self.is_home_page(final_url):
                    return prp_candidate
        except Exception:
            pass

        # Fallback to root
        return root_candidate


    def test_load_home_page(self):
        """Perform login using persistent session page."""
        if self.session_page is None:
            self.session_page = self.context.new_page()
            self.session_page.set_default_timeout(30000)

        page = self.session_page
        
        try:
            logging.info("🔐 Attempting login...")
            page.goto(self.base_url, wait_until="domcontentloaded")
            
            try:
                page.fill("#oktaEmailInput", self.username)
                page.click("#oktaSignInBtn")
                page.fill("#password-sign-in", self.password)
                page.click("#onepass-submit-btn")
            except Exception:
                try:
                    page.click("#onepass-submit-btn")
                except Exception:
                    pass
                logging.warning("⚠️ Primary login selectors failed, trying fallback")
                pass

            # try:
            #     page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40000)
            #     try:
            #         page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
            #     except Exception:
            #         page.evaluate("document.querySelector('//*[@id=\"form19\"]/div[2]/div[2]/div[2]/a')?.click()")
            # except Exception:
            #     logging.debug("No digital badge found (non-fatal)")

            try:
                page.wait_for_load_state("domcontentloaded", timeout=20000)
            except Exception:
                pass

            logging.info("✅ Login completed successfully")

        except Exception as e:
            logging.warning(f"⚠️ Login flow error: {e}")

    def country_similarity(self, a: str, b: str) -> float:
        """Calculate similarity score between two country names."""
        if not a or not b:
            return 0.0

        a = a.lower()
        b = b.lower()

        # Token-based similarity
        a_tokens = set(a.replace("(", " ").replace(")", " ").split())
        b_tokens = set(b.replace("(", " ").replace(")", " ").split())

        token_overlap = len(a_tokens & b_tokens)
        token_total = max(len(a_tokens), 1)
        token_score = token_overlap / token_total

        # Character similarity
        matches = sum(1 for ch in a if ch in b)
        char_score = matches / max(len(a), 1)

        return (token_score * 0.6) + (char_score * 0.4)

    def handle_country_and_overlay(self, force_recheck=False):
        page = self.session_page
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
        Quick check to ensure country hasn't been reset during crawling.
        Called periodically based on time AND page count.
        
        Since crawler navigates to many internal pages, we just check
        the country setting without additional navigation.
        """
        current_time = time.time()
        
        # Check based on EITHER time elapsed OR pages crawled
        time_check = (current_time - self.last_country_check) >= self.country_check_interval
        page_check = self.pages_crawled_since_check >= self.check_every_n_pages
        
        if not (time_check or page_check):
            return
        
        logging.info(f"\n{'='*80}")
        logging.info(f"🔍 Periodic Country Verification")
        logging.info(f"   Time since last check: {current_time - self.last_country_check:.1f}s")
        logging.info(f"   Pages since last check: {self.pages_crawled_since_check}")
        logging.info(f"{'='*80}")
        
        try:
            # Check if session page exists and is on PRP domain
            if self.session_page is None:
                logging.warning("⚠️ Session page not available for country check")
                return
            
            current_url = self.session_page.url
            
            # If somehow we ended up on external page, go back to PRP
            if current_url.startswith("https://partner.hpe.com"):
                # Re-run country check (no additional navigation needed - already on PRP)
                self.handle_country_and_overlay(force_recheck=True)
                
                # Update last check time and reset page counter
                self.last_country_check = current_time
                self.pages_crawled_since_check = 0
            
        except Exception as e:
            logging.warning(f"⚠️ Error during country verification: {e}")
        
        logging.info(f"{'='*80}\n")

    def filter_breadcrumbs(self, link: str) -> bool:
        """Check if link should be included (not a breadcrumb link)."""
        status = True
        for prefix in self.breadcrumb_prefix:
            try:
                if link.startswith(prefix):
                    status = False
                    break
            except Exception:
                continue
        
        if link in self.breadcrumblinks:
            status = False
        
        return status

    def categorize_redirect(self, intended: str, actual: str) -> dict:
        """
        Categorize the type of redirect that occurred.
        Returns dict with redirect information.
        """
        redirect_info = {
            'intended': intended,
            'actual': actual,
            'category': 'unknown'
        }
        
        # Check if redirected to home page
        actual_normalized = actual.rstrip('/')
        if any(actual_normalized == hp.rstrip('/') for hp in self.HOME_PAGES):
            redirect_info['category'] = 'home'
            return redirect_info
        
        # Check if same path with slug change (e.g., /competencies-prv → /competencies)
        intended_parts = intended.rsplit('/', 1)
        actual_parts = actual.rsplit('/', 1)
        
        if len(intended_parts) > 1 and len(actual_parts) > 1:
            if intended_parts[0] == actual_parts[0]:
                redirect_info['category'] = 'slug_change'
                return redirect_info
        
        # Different path entirely
        redirect_info['category'] = 'path_change'
        return redirect_info

    def scrape(self, queue, internal, external, allurls, doclinks, tree_dict):
        """
        Main crawling logic with smart redirect handling.
        Uses fresh page per URL to prevent DOM bleed.
        """
        # Ensure login completed
        if self.session_page is None:
            self.test_load_home_page()
        
        try:
            self.handle_country_and_overlay()
        except Exception as e:
            logging.warning(f"⚠️ Overlay/country handler issue: {e}")

        
        
        logging.info(f"🚀 Starting crawl with {len(queue)} seed URLs")
        time.sleep(8)

        visited = set(allurls)
        url_queue = deque(queue)

        # ✅ Track what's already queued to prevent duplicates
        queued = set(queue)

        while url_queue:
            # *** NEW: Periodic country verification ***
            self.verify_country_setting()
            
            raw_link = url_queue.popleft()

            # Remove from queued tracker when processing
            queued.discard(raw_link)

            if not raw_link:
                continue
            
            # Normalize URL
            link = normalize_url(self.base_url, raw_link)
            if not link or link in visited:
                continue

            visited.add(link)

            # Quick classification for documents
            if looks_like_doc(link):
                doclinks.add(link)
                allurls.add(link)
                continue

            allurls.add(link)

            if not link.startswith('http'):
                continue

            # Only crawl same-domain links
            if is_same_domain(link):
                # Initialize tree entry for intended URL
                if link not in tree_dict:
                    tree_dict[link] = []

                page = None
                try:
                    # Create fresh page for this URL (prevents DOM bleed)
                    page = self.context.new_page()
                    page.set_default_timeout(30000)
                    
                    logging.info(f"📍 Navigating to: {link}")
                    
                    # Navigate and capture response
                    page.goto(link, wait_until="domcontentloaded", timeout=30000)
                    
                    # Increment pages crawled counter
                    self.pages_crawled_since_check += 1
                    
                    # Get where we actually landed
                    actual_url = page.url.split('#')[0]  # Remove fragment
                    expected_url = link.split('#')[0]
                    
                    # Handle redirects intelligently
                    redirect_info = None
                    scrape_url = link  # Default to intended URL
                    
                    if actual_url != expected_url:
                        redirect_info = self.categorize_redirect(link, actual_url)
                        scrape_url = actual_url  # Use actual URL for scraping
                        
                        # Log redirect
                        self.redirect_map[link] = actual_url

                        # ✅ ADD redirected URL to tree + internal IF NOT homepage
                        if self.is_valid_prp_page(actual_url):
                            if actual_url not in tree_dict:
                                tree_dict[actual_url] = []

                            if self.filter_breadcrumbs(actual_url):
                                internal.add(actual_url)

                            visited.add(actual_url)
                        else:
                            logging.info(f"🏠 Redirected to homepage, skipping tree add: {actual_url}")
                        
                        if redirect_info['category'] == 'home':
                            logging.info(f"🏠 Home redirect: {link} → {actual_url}")
                            
                            # Skip if home page already processed
                            if actual_url in visited:
                                logging.info(f"⏩ Skipping duplicate home page")
                                continue
                            
                            visited.add(actual_url)
                            
                        elif redirect_info['category'] == 'slug_change':
                            logging.info(f"🔄 Slug change: {link} → {actual_url}")
                            
                            # Create tree entry for actual URL
                            if actual_url not in tree_dict:
                                tree_dict[actual_url] = []
                            
                            visited.add(actual_url)
                            
                        elif redirect_info['category'] == 'path_change':
                            logging.info(f"🔀 Path redirect: {link} → {actual_url}")
                            
                            # Create tree entry for actual URL
                            if actual_url not in tree_dict:
                                tree_dict[actual_url] = []
                            
                            visited.add(actual_url)
                        else:
                            logging.info(f"🔀 Unknown redirect: {link} → {actual_url}")
                            
                            if actual_url not in tree_dict:
                                tree_dict[actual_url] = []
                            
                            visited.add(actual_url)
                    
                    if scrape_url not in tree_dict:
                        tree_dict[scrape_url] = []
                    logging.info(f"✅ Page loaded, scraping: {scrape_url}")
                    
                    # Handle delayed loading pages
                    if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                        try:
                            page.wait_for_selector("#disBtn", timeout=15000)
                        except PlaywrightTimeoutError:
                            pass

                    # Handle slow pages
                    if link in self.absurd_links:
                        page.wait_for_timeout(1500)

                    # Wait for page to fully stabilize after navigation/country switch
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=5000)
                        # Wait for the focused banner component to render
                        try:
                            page.wait_for_selector("div.focused_X a", timeout=10000)
                            logging.info("✅ focused_X banner loaded")
                        except PlaywrightTimeoutError:
                            logging.debug("No focused_X banner on this page")

                        page.wait_for_timeout(1500)

                    except Exception:
                        pass
                    
                    # Extract anchor elements
                    try:
                        anchors = page.query_selector_all("a")
                        logging.info(f"🔍 Found {len(anchors)} total anchor elements on page")
                    except Exception as e:
                        logging.warning(f"⚠️ Anchor collection error: {e}")
                        anchors = []

                    found_children = []
                    skipped_counts = {
                        'no_href': 0,
                        'normalization_failed': 0,
                        'unwanted_pattern': 0,
                        'not_visible': 0,
                        'document': 0,
                        'already_in_tree': 0,
                        'already_queued': 0,
                        'exception': 0
                    }

                    # Process each anchor
                    for ele in anchors:
                        try:
                            href = ele.get_attribute("href")
                            if not href:
                                skipped_counts['no_href'] += 1
                                continue

                            if href.startswith(('javascript:', 'mailto:', 'tel:', 'data:', 'javascipt')):
                                skipped_counts['unwanted_pattern'] += 1
                                continue
                            
                            # Resolve URL against ACTUAL page URL (critical for redirects)
                            if href.startswith('/') or not href.startswith(('http', 'https')):
                                norm = self.smart_resolve_relative(page, href)
                            else:
                                norm = normalize_url(page.url, href)

                            if not norm:
                                skipped_counts['normalization_failed'] += 1
                                logging.debug(f"Failed to normalize: {href}")
                                continue

                            if norm.rstrip('/') == page.url.rstrip('/'):
                                continue

                            
                            # Skip unwanted patterns
                            if ('login' in norm.lower() or 
                                'logout' in norm.lower() or 
                                norm.endswith('#') or 
                                '?p_p_id=com' in norm):
                                skipped_counts['unwanted_pattern'] += 1
                                continue
                            
                            # Check CSS visibility - make this more permissive
                            try:
                                # if not is_element_visible(ele):
                                #     skipped_counts['not_visible'] += 1
                                #     continue
                                pass  # Skipped visibility check
                            except Exception as vis_error:
                                # If visibility check fails, INCLUDE the link (be permissive)
                                logging.debug(f"Visibility check failed for {norm}, including anyway")
                                pass

                            # Classify documents
                            if looks_like_doc(norm):
                                doclinks.add(norm)
                                allurls.add(norm)

                                parent_url = scrape_url  # ACTUAL page where the doc link exists

                                # ✅ ADD DOCUMENT → PARENT RELATIONSHIP
                                if parent_url in tree_dict and norm not in tree_dict[parent_url]:
                                    tree_dict[parent_url].append(norm)

                                skipped_counts['document'] += 1
                                continue

                            # Add to tree_dict under ACTUAL page URL
                            # This ensures links are attributed to the page they're actually on
                            parent_url = scrape_url
                            
                            if norm not in tree_dict[parent_url]:
                                tree_dict[parent_url].append(norm)
                                found_children.append(norm)
                            else:
                                skipped_counts['already_in_tree'] += 1
                            
                            # ✅ CRITICAL FIX: Check both visited AND queued before adding
                            if norm not in visited and norm not in queued:
                                url_queue.append(norm)
                                queued.add(norm)  # ✅ Mark as queued immediately
                            elif norm in queued:
                                skipped_counts['already_queued'] += 1
                                
                        except Exception as e:
                            skipped_counts['exception'] += 1
                            logging.warning(f"⚠️ Error processing anchor on {scrape_url}: {e} (href: {href if 'href' in locals() else 'unknown'})")
                            continue
                    
                    # Log detailed statistics
                    logging.info(f"📊 Link extraction stats for {scrape_url}:")
                    logging.info(f"   ✅ New links found: {len(found_children)}")
                    logging.info(f"   ⏭️  Skipped breakdown:")
                    logging.info(f"      - No href: {skipped_counts['no_href']}")
                    logging.info(f"      - Normalization failed: {skipped_counts['normalization_failed']}")
                    logging.info(f"      - Unwanted pattern: {skipped_counts['unwanted_pattern']}")
                    logging.info(f"      - Not visible: {skipped_counts['not_visible']}")
                    logging.info(f"      - Document: {skipped_counts['document']}")
                    logging.info(f"      - Already in tree: {skipped_counts['already_in_tree']}")
                    logging.info(f"      - Already Queued: {skipped_counts['already_queued']}")
                    logging.info(f"      - Exception: {skipped_counts['exception']}")

                    logging.info(f"📊 Extracted {len(found_children)} new links from {scrape_url}")

                    # Add to internal set if passes breadcrumb filter
                    if self.filter_breadcrumbs(link):
                        internal.add(link)
                    
                    # Also add actual URL if different (for redirect cases)
                    if redirect_info and scrape_url != link:
                        if self.filter_breadcrumbs(scrape_url):
                            internal.add(scrape_url)

                except PlaywrightTimeoutError:
                    logging.warning(f"⏱️ Timeout: {link}")
                except Exception as e:
                    logging.error(f"❌ Error crawling {link}: {e}")
                finally:
                    # Always close page to prevent memory leaks
                    if page is not None:
                        try:
                            page.close()
                        except Exception:
                            pass

            else:
                # External link
                if self.filter_breadcrumbs(link):
                    external.add(link)

        # Ensure all visited URLs are in allurls
        for v in visited:
            allurls.add(v)

        logging.info(f"✅ Crawl complete: {len(visited)} URLs visited, {len(internal)} internal, {len(external)} external, {len(doclinks)} documents")
        
        return allurls, internal, external, doclinks, tree_dict

    def reverse_dict_builder(self, treedict, allurls):
        """Build reverse mapping: child URL → list of parent URLs."""
        revdict = {}

        for parent, children in treedict.items():
            for child in children:
                if child not in revdict:
                    revdict[child] = set()
                revdict[child].add(parent)

        # Ensure all URLs have an entry (even if no parents)
        for url in allurls:
            if url not in revdict:
                revdict[url] = set()

        # Convert sets to lists for serialization
        final_revdict = {k: list(v) for k, v in revdict.items()}
        return final_revdict

    def scrapecall_writetrees(self):
        """Execute crawl and write results to files."""
        internal = set()
        external = set()
        docs = set()
        all_links = set()
        tree_dict = {}
        queue = [self.base_url]
        
        # Execute crawl
        all_links, internal, external, docs, tree_dict = self.scrape(
            queue, internal, external, all_links, docs, tree_dict
        )
        
        # Calculate total links
        self.prp_links = len(internal) + len(all_links) + len(external) + len(docs)

        # Ensure output directories exist
        os.makedirs(os.path.dirname(self.page_tree_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(self.external_urls_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(self.doc_link_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(self.reverse_dict_path) or '.', exist_ok=True)
        os.makedirs(os.path.dirname(self.redirect_log_path) or '.', exist_ok=True)

        # Write internal links (PRP pages)
        with open(self.page_tree_path, 'w', encoding='utf-8') as f:
            for item in sorted(internal):
                # if item.startswith("https://partner.hpe.com/group/prp"):
                if item.startswith("https://partner.hpe.com/"):
                    f.write(f'{item}\n')
        
        # Write external links
        with open(self.external_urls_path, 'w', encoding='utf-8') as f:
            for item in sorted(external):
                f.write(f'{item}\n')
        
        # Write document links
        with open(self.doc_link_path, 'w', encoding='utf-8') as f:
            for item in sorted(docs):
                f.write(f'{item}\n')
        
        # Build and write reverse dictionary
        revdict = self.reverse_dict_builder(tree_dict, all_links)
        with open(self.reverse_dict_path, 'w', encoding='utf-8') as f:
            f.write(str(revdict))
        
        # Write redirect log for analysis
        with open(self.redirect_log_path, 'w', encoding='utf-8') as f:
            f.write("Intended URL → Actual URL\n")
            f.write("=" * 80 + "\n")
            for intended, actual in sorted(self.redirect_map.items()):
                f.write(f"{intended} → {actual}\n")

        logging.info(f"📝 Results written to files:")
        logging.info(f"   Internal: {len(internal)} links")
        logging.info(f"   External: {len(external)} links")
        logging.info(f"   Documents: {len(docs)} links")
        logging.info(f"   Total: {len(all_links)} links")
        logging.info(f"   Redirects: {len(self.redirect_map)} detected")

    def tearDown(self):
        """Clean up Playwright resources."""
        try:
            if self.session_page is not None:
                self.session_page.close()
                self.session_page = None
        except Exception:
            pass
        
        try:
            if self.context is not None:
                self.context.close()
                self.context = None
        except Exception:
            pass
        
        try:
            if self.browser is not None:
                self.browser.close()
                self.browser = None
        except Exception:
            pass
        
        try:
            if self.pw is not None:
                self.pw.stop()
                self.pw = None
        except Exception:
            pass
        
        logging.info("🧹 Cleanup complete")


# -------------------------
# Execution Functions
# -------------------------
def run_account(account):
    """Run crawler for a single account."""
    prp = PRP(*account)
    
    try:
        prp.setUp()
        prp.scrapecall_writetrees()
        
        # Optional: Play completion sound
        try:
            from playsound3 import playsound
            playsound(r"Sound\beep-01a.wav")
        except Exception:
            pass
        
        logging.info(f"✅ Finished processing: {account[0]}")
        
    except Exception as e:
        logging.exception(f"❌ Error processing {account[0]}: {e}")
    
    finally:
        try:
            prp.tearDown()
        except Exception:
            pass

from multiprocessing import Process

if __name__ == '__main__':
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'],
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Brazil', 'English', 'distri'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'France', 'French', 'T2'],
        # Add more accounts as needed:
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'APJ', 'China', 'Simplified Chinese', 'T2'],
        # ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ', 'Indonesia', 'Indonesian', 'distri'],
        # ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey', 'Turkish', 'T2']
    ]

    # Adjust max_workers based on system capability
    # Recommended: 1-2 for stability, 3-4 for speed (if sufficient RAM)
    # with ThreadPoolExecutor(max_workers=2) as executor:
    #     executor.map(run_account, credentials)
    
    # logging.info("🎉 All accounts processed successfully")
    processes = []
    for account in credentials:
        p = Process(target=run_account, args=(account,))
        p.start()
        processes.append(p)
    
    for p in processes:
        p.join()
    
    logging.info("🎉 All accounts processed successfully")