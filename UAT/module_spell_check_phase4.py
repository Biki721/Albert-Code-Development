import work_phase_3 as work
import ast
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import moduleemptypage as mep
import module_spelling_phase4 as msc
import time
from concurrent.futures import ThreadPoolExecutor
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from metric_report import log_module_metric

from pathlib import Path

BASE_DIR = Path(__file__).parent

class PRP:
    base_url = "https://partner.hpe.com"

    # EXCLUSION OF LINKS THAT NEED NOT UNDERGO CHECKS
    links_not_to_be_checked = work.doc_reader(str(BASE_DIR /"lte_translation.docx"))
    links_not_to_be_checked = [s.strip() for s in links_not_to_be_checked if s != ""]

    # EXTRACT LIST OF LINKS THAT NEED LONGER DELAYS
    delayed_loading_links = work.doc_reader(str(BASE_DIR /"delayed_loading.docx"))
    delayed_loading_links = [s.strip() for s in delayed_loading_links if s != ""]

    # EXCLUSION OF EMPTY PAGE
    not_to_check_links = work.doc_reader(str(BASE_DIR /"lte_emptypage.docx"))
    not_to_check_links = [s.strip() for s in not_to_check_links if s != ""]

    # EXCLUSION OF CERTAIN SUB-DOMAINS
    absurd_links = work.doc_reader(str(BASE_DIR /"absurd_links.docx"))
    absurd_links = [s.strip() for s in absurd_links if s != ""]

    def __init__(self, username: str, password: str, region: str, country, language, acc_type):
        self.username = username
        self.password = password
        if region == "NA":
            region = "NAR"
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language
        self.page_tree_path = BASE_DIR/"Page Trees/PageTree{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.all_links_path = BASE_DIR/"All Links/AllLinks{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.tree_dict_path = BASE_DIR/"Tree Dicts/TreeDict{r}_{c}_{l}_{a}.json".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.spell_report_path = BASE_DIR/"Reports/Spelling_{r}_{c}_{l}_{a}.xlsx".format(
            r=self.region, c=self.country, a=self.account_type, l=self.language
        )
        self.emptypage_report_path = BASE_DIR/"Reports/EmptyPage_{r}_{c}_{l}_{a}.xlsx".format(
            r=self.region, c=self.country, a=self.account_type, l=self.language
        )
        self.reverse_dict_path = BASE_DIR/"Reverse Dicts/RevDict{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.aruba_links_path = BASE_DIR/"Aruba Urls/Aruba{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )

        self.pw = None
        self.browser = None
        self.page = None

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
    
    # NEW METHOD: Verify country is still correct
    def verify_country_setting(self):
        """
        Quick check to ensure country hasn't been reset during translation/spelling checks.
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




    def test_load_home_page(self):
        page = self.page
        page.goto(self.base_url)
        page.fill("#oktaEmailInput", self.username)
        page.click("#oktaSignInBtn")
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")
        time.sleep(5)
        # Handle overlay + eyeball + country selection
        current_country = self.handle_country_and_overlay()
        time.sleep(5)
        page.goto(self.base_url)

    @log_module_metric("Spell Check")
    def parent(self):
        if self.language != "English":
            return

        def write_excel(errors):
            fileread1 = open(self.reverse_dict_path).read()
            dictionary = ast.literal_eval(fileread1)

            if isinstance(errors, dict):
                category = "Spelling Error"
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
                published_report_path = self.spell_report_path
            else:
                category = "Empty Page"
                iterator = errors
                des = ["Empty page"] * len(errors)
                published_report_path = self.emptypage_report_path

            issueid = 1

            account = self.username
            region = self.region
            country = self.country
            language = self.language
            Fixers = ""
            Fixer_mail = ""
            status = "New"
            comments = "-"
            report = []
            i = 0
            for ele in iterator:
                if ele == "https://partner.hpe.com/group/prp/internal":
                    continue
                linkele = []
                linkele.append(issueid)
                linkele.append(account)
                linkele.append(category)
                linkele.append(region)
                linkele.append(country)
                linkele.append(language)
                if ele in dictionary:
                    length = len(dictionary[ele])
                    if length > 0:
                        s_url = dictionary[ele][-1]
                        s_url2 = dictionary[ele][0]
                elif ele.strip() in dictionary:
                    length = len(dictionary[ele.strip()])
                    if length > 0:
                        s_url = dictionary[ele.strip()][-1]
                        s_url2 = dictionary[ele.strip()][0]
                elif ele + "\n" in dictionary:
                    length = len(dictionary[ele + "\n"])
                    if length > 0:
                        s_url = dictionary[ele + "\n"][-1]
                        s_url2 = dictionary[ele + "\n"][0]
                else:
                    length = 0

                if length == 0:
                    linkele.append(ele)
                elif s_url == ele:
                    linkele.append(s_url2)
                else:
                    linkele.append(s_url)

                linkele.append(ele)
                linkele.append(des[i])
                linkele.append(datetime.datetime.now())
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid += 1
                i += 1

            r = pd.DataFrame(
                report,
                columns=[
                    "Issue ID",
                    "Demo Account",
                    "Category",
                    "Region",
                    "Country",
                    "Language",
                    "Link",
                    "Error Link",
                    "Description",
                    "Time Identified",
                    "Mail ID",
                    "Status",
                    "Comments",
                ],
            )
            r.to_excel(published_report_path)
            return

        def integrate(site):
            page = self.page
            try:
                page.goto(site, wait_until="networkidle")
            except PlaywrightTimeoutError:
                pass
            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links:
                time.sleep(45)
            src = page.content()
            soup = BeautifulSoup(src, "html.parser")
            return src, soup

        def aruba(soup):
            find_aruba = soup.find_all("span", class_="arubaTag")
            if find_aruba:
                return True
            return False

        def filter(list_of_links, links_not_to_be_checked):
            actual_list_of_links = []
            list_of_links = [link.strip() for link in list_of_links]
            links_not_to_be_checked = [link.strip() for link in links_not_to_be_checked]
            actual_excluded_links = set()
            for lte in links_not_to_be_checked:
                for ptl in list_of_links:
                    if (
                        ptl.startswith(lte)
                        or "products" in ptl
                        or "https://partner.hpe.com/group/prp/settings" in ptl
                        or ptl == "https://partner.hpe.com"
                    ):
                        actual_excluded_links.add(ptl)
            actual_list_of_links = list(set(list_of_links) - set(actual_excluded_links))
            return actual_list_of_links

        f = open(self.page_tree_path, "r")
        list_of_links = f.read().splitlines()

        all_links_spell = filter(list_of_links, self.links_not_to_be_checked)
        all_links_empty = filter(list_of_links, self.not_to_check_links)

        def no_content_pg(soup):
            errmsg = [
                "Oops! We can't find that page",
                "We can't find the page you're looking for",
            ]
            text = soup.get_text()
            for msg in errmsg:
                if msg in text:
                    return True
                else:
                    return False

        spell_errors = {}
        epterrors = []
        aruba_links = set()

        for link in list_of_links:

             # *** NEW: Periodic country verification ***
            self.verify_country_setting()
            
            src, soup = integrate(link)
            aruba_bool = aruba(soup)
            if aruba_bool:
                if (
                    link != "https://partner.hpe.com"
                    and link != "https://partner.hpe.com/group/prp"
                    and link != "https://partner.hpe.com/group/prp/home"
                ):
                    aruba_links.add(link)

            nocontent = no_content_pg(soup)
            if nocontent:
                epterrors.append(link)

            if link in all_links_spell and link in all_links_empty:
                gramm = msc.callable_extract(link, src, soup, self.language)
                if gramm:
                    spell_errors.update({link: gramm})
                epterrors.append(mep.emptypagecheck(link, self.language, "Related content", soup))

            elif link in all_links_empty:
                epterrors.append(mep.emptypagecheck(link, self.language, "Related content", soup))

            elif link in all_links_spell:
                gramm = msc.callable_extract(link, src, soup, self.language)
                if gramm:
                    spell_errors.update({link: gramm})
            else:
                continue

        epterrors = [err for err in epterrors if err != ""]
        write_excel(epterrors)
        write_excel(spell_errors)

        with open(self.aruba_links_path, "w") as filehandle:
            for listitem in aruba_links:
                filehandle.write("%s\n" % listitem)

    def tearDown(self):
        try:
            if self.page is not None:
                self.page.close()
        except Exception:
            pass
        try:
            if self.browser is not None:
                self.browser.close()
        except Exception:
            pass
        try:
            if self.pw is not None:
                self.pw.stop()
        except Exception:
            pass
        df_spell = pd.read_excel(self.spell_report_path)
        dff = pd.read_excel(self.emptypage_report_path)
        if len(df_spell) > 0:
            work.work_alloc_execute(self.spell_report_path, "Fixers_list.xlsx", self.aruba_links_path)
        if len(dff) > 0:
            work.work_alloc_execute(self.emptypage_report_path, "Fixers_list.xlsx", self.aruba_links_path)


def run_account(account):
    try:
        prp_main = PRP(*account)
        prp_main.setUp()
        prp_main.test_load_home_page()
        prp_main.parent()
        prp_main.tearDown()
        from playsound3 import playsound

        playsound("Sound/beep-01a.wav")
        print(f"Finished processing: {account[0]}")
    except Exception as e:
        print(f"Exception while processing {account[0]}: {e}")


if __name__ == "__main__":
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'Japan', 'Japanese', 'distri'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Spain', 'Spanish', 'T2'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'South Korea', 'English', 'T2'],
    ]

    with ThreadPoolExecutor(max_workers=3) as executor:
        executor.map(run_account, credentials)
