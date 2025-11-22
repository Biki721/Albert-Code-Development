import time
import threading
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import work_phase_3 as work


class PRP():
    base_url = "https://partner.hpe.com"
    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links = [s.strip() for s in delayed_loading_links if s != '']
    breadcrumblinks = work.doc_reader("breadcrumb_links.docx")
    breadcrumblinks = [s.strip() for s in breadcrumblinks if s != '']
    absurd_links = work.doc_reader("absurd_links.docx")
    absurd_links = [s.strip() for s in absurd_links if s != '']
    breadcrumb_prefix = work.doc_reader("Breadcrumb_Prefix.docx")
    breadcrumb_prefix = [s.strip() for s in breadcrumb_prefix if s != '']

    def __init__(self, username: str, password: str, region: str, country, language, acc_type):
        self.username = username
        self.password = password
        if region == "NA":
            region = 'NAR'
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language
        self.page_tree_path = 'Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        # self.tree_dict_path='Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.txt'.format(r=self.region,c=self.country,l=self.language,a=self.account_type)
        self.doc_link_path = 'DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.reverse_dict_path = 'Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.external_urls_path = 'External Urls\\External{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.prp_links = None
        self.lock = threading.Lock()

        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    # -------------------------------------------------------------------------------------
    # SETUP (using Playwright)
    # -------------------------------------------------------------------------------------
    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)

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

        # Wait for post-login page
        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except Exception:
            print("No digital badge found")

        time.sleep(5)

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
    def handle_country_and_overlay(self):
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
            print("✅ No overlay appeared, continuing.")
        except Exception as e:
            print("⚠️ Overlay handling error:", e)
        time.sleep(10)

        # --- STEP 2: Click Eyeball icon ---
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", timeout=30000)
            if eyeball:
                eyeball.click()
        except Exception:
            pass
        time.sleep(10)

        # --- STEP 3: Extract current country ---
        try:
            selector = (
                '#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet '
                '> div > div.portlet-content-container > div > div.MHMGuserdescrp '
                '> div > div.MHMGcountryname'
            )
            country_element = page.wait_for_selector(selector, timeout=20000)
            current_country = country_element.inner_text().strip() if country_element else ""
            print("🌍 Current Country:", current_country if current_country else "Unknown")
        except Exception:
            current_country = ""
            print("⚠️ Could not detect current country")
        time.sleep(10)

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", timeout=15000)
            if loc_btn:
                loc_btn.click()
        except Exception:
            pass
        time.sleep(10)

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", timeout=15000)
        except Exception:
            pass
        time.sleep(10)

        # --- STEP 6: Switch country if needed ---
        try:
            if current_country.lower() == self.country.lower():
                print(f"✅ Country already set to '{current_country}'")
            else:
        
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

        time.sleep(10)
        return current_country



    def filter_breadcrumbs(self, link):
        status = True
        for li in self.breadcrumb_prefix:
            if link.startswith(li):
                status = False
        if link in self.breadcrumblinks:
            status = False
        return status

    def scrape(self, queue, internal, external, allurls, doclinks, tree_dict):
        page = self.page
        self.test_load_home_page()

         # Handle overlay + eyeball + country selection
        current_country = self.handle_country_and_overlay()

        visited = set(allurls)
        url_queue = deque(queue)

        while url_queue:
            link = url_queue.popleft()
            if not link:
                continue
            link = link.strip().strip('\n')
            if not link or link in visited:
                continue
            visited.add(link)

            if '/documents' in link or '/esm' in link or '.pdf' in link or '.xlsx' in link or '.zip' in link:
                doclinks.add(link)
                allurls.add(link)
                continue

            if link.startswith('http'):
                allurls.add(link)
                if link.startswith("https://partner.hpe.com"):

                    if link not in tree_dict:
                        tree_dict[link] = []

                    try:
                        page.goto(link, wait_until="networkidle")
                        if link in self.delayed_loading_links or link.strip() in self.delayed_loading_links:
                            try:
                                page.wait_for_selector("#disBtn", timeout=15000)
                            except PlaywrightTimeoutError:
                                pass
                        if link in self.absurd_links:
                            time.sleep(15)
                    except Exception:
                        pass

                    if self.filter_breadcrumbs(link):
                        internal.add(link)

                    try:
                        ahref = page.query_selector_all("a")
                        inputval = page.query_selector_all("input")

                        for ele in ahref:
                            url = ele.get_attribute("href")
                            if url is None:
                                continue
                            url = url.strip()
                            if (
                                not url
                                or url in allurls
                                or 'login' in url
                                or 'logout' in url
                                or '#' in url
                                or '?p_p_id=com' in url
                            ):
                                continue
                            if (
                                not url.startswith('http')
                                and not url.startswith('https://partner.hpe.com')
                                and ('article-display-page?' in url or 'group/prp' in url)
                            ):
                                if url.startswith("/group/prp"):
                                    url = 'https://partner.hpe.com' + url
                                else:
                                    url = 'https://partner.hpe.com/group/prp' + url
                            if url.startswith('http'):
                                if url not in tree_dict[link]:
                                    tree_dict[link].append(url)
                                if url not in visited:
                                    url_queue.append(url)

                        for ele in inputval:
                            url = ele.get_attribute("value")
                            if url is None:
                                continue
                            url = url.strip()
                            if (
                                not url
                                or url in allurls
                                or 'login' in url
                                or 'logout' in url
                                or '#' in url
                                or '?p_p_id=com' in url
                            ):
                                continue
                            if (
                                not url.startswith('http')
                                and not url.startswith('https://partner.hpe.com')
                                and ('article-display-page?' in url or 'group/prp' in url)
                            ):
                                if url.startswith("/group/prp"):
                                    url = 'https://partner.hpe.com' + url
                                else:
                                    url = 'https://partner.hpe.com/group/prp' + url
                            if url.startswith('http'):
                                if url not in tree_dict[link]:
                                    tree_dict[link].append(url)
                                if url not in visited:
                                    url_queue.append(url)

                    except Exception:
                        continue

                else:
                    if self.filter_breadcrumbs(link):
                        external.add(link)

        return allurls, internal, external, doclinks, tree_dict

    def reverse_dict_builder(self, treedict, allurls):
        revdict = {}

        for parent, children in treedict.items():
            for child in children:
                if child not in revdict:
                    revdict[child] = set()
                revdict[child].add(parent)

        for p in allurls:
            if p not in revdict:
                revdict[p] = set()

        final_revdict = {k: list(v) for k, v in revdict.items()}
        return final_revdict

    def scrapecall_writetrees(self):
        internal = set()
        external = set()
        docs = set()
        all_links = set()
        tree_dict = {}
        queue = [self.base_url]
        all_links, internal, external, docs, tree_dict = self.scrape(
            queue, internal, external, all_links, docs, tree_dict
        )
        self.prp_links = len(internal) + len(all_links) + len(external) + len(docs)
        with open(self.page_tree_path, 'w') as filehandle:
            for item in internal:
                if item.startswith("https://partner.hpe.com/group/prp"):
                    filehandle.write('%s\n' % item)
        with open(self.external_urls_path, 'w') as filehandle:
            for listitem in external:
                filehandle.write('%s\n' % listitem)
        with open(self.doc_link_path, 'w') as filehandle:
            for listitem in docs:
                filehandle.write('%s\n' % listitem)
        revdict = self.reverse_dict_builder(tree_dict, all_links)
        with open(self.reverse_dict_path, 'w') as filehandle:
            filehandle.write(str(revdict))

    def tearDown(self):
        try:
            if self.context is not None:
                self.context.close()
        except Exception:
            pass
        try:
            if self.browser is not None:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.playwright is not None:
                self.playwright.stop()
        except Exception:
            pass


def run_account(account):
    prp = PRP(*account)
    try:
        prp.setUp()
        prp.scrapecall_writetrees()
        from playsound3 import playsound
        playsound(r"Sound\beep-01a.wav")
        print(f"Finished processing: {account[0]}")
    except Exception as e:
        print(f"Error in processing {account[0]}: {e}")
    finally:
        try:
            prp.tearDown()
        except Exception:
            pass

if __name__ == '__main__':
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'South Korea', 'Korean', 'distri'],
    ]

    # Adjust max_workers based on your system capability (e.g., RAM, CPU, browser limits)
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(run_account, credentials)