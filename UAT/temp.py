import work_phase_3 as work
import ast
import datetime
import moduletranslation_phase4_better_version as mtrans
import module_spelling_phase4 as msc
from bs4 import BeautifulSoup
import pandas as pd
import moduleemptypage as mep
import time
import module_login_lang
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from metric_report import log_module_metric
from concurrent.futures import ThreadPoolExecutor
from url_utils import load_home_prefixes, is_home_redirect_playwright

# NEW: Import country manager utilities
from module_country_manager import ( 
    ensure_country_for_delayed,
    initialize_country_manager
)

HOME_PREFIXES = load_home_prefixes('config/home_pages.txt')


class PRP():
    base_url = "https://partner.hpe.com"
    
    # EXCLUSION OF LINKS THAT NEED NOT UNDERGO TRANSLATION CHECKS
    links_not_to_be_checked = work.doc_reader("lte_translation.docx")
    links_not_to_be_checked = [s.strip() for s in links_not_to_be_checked if s != '']

    translated_phrases = {
        "French": "Contenu associé",
        'German': 'Verwandter inhalt',
        'Italian': "Contenuti correlati",
        'Chinese': '相关内容',
        'Chinese-Simplified': '相关内容',
        'Russian': 'Сопутствующая информация',
        'Portugese': 'Conteúdo relacionado',
        'Portuguese-Brazil': 'Conteúdo relacionado',
        'Indonesian': 'Konten terkait',
        'Singaporean': 'Related content',
        'Korean': "관련 콘텐츠",
        'Turkish': "İlgili içerik",
        'Japanese': "関連コンテンツ",
        'Taiwan': "相關內容",
        'Spanish': 'Contenido relacionado',
        "LARSpanish": 'Contenido relacionado',
        'English': 'Related content'
    }

    # EXTRACT LIST OF LINKS THAT NEED LONGER DELAYS
    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links = [s.strip() for s in delayed_loading_links if s != '']

    # EXCLUSION OF EMPTY PAGE
    not_to_check_links = work.doc_reader("lte_emptypage.docx")
    not_to_check_links = [s.strip() for s in not_to_check_links if s != '']

    # EXCLUSION OF CERTAIN SUB-DOMAINS
    absurd_links = work.doc_reader("absurd_links.docx")
    absurd_links = [s.strip() for s in absurd_links if s != '']

    
    def __init__(self, username: str, password: str, region: str, country, language, acc_type, 
                 playwright=None, browser=None, page=None):
        self.username = username
        self.password = password
        if region == "NA":
            region = 'NAR'
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language

        # Report paths
        self.page_tree_path = 'Page Trees\\PageTree{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.all_links_path = 'All Links\\AllLinks{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.tree_dict_path = 'Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        
        # FIXED: Separate report paths for each check type
        self.translation_report_path = 'Reports\\Translation_{r}_{c}_{l}_{a}.xlsx'.format(
            r=self.region, c=self.country, a=self.account_type, l=self.language)
        self.spelling_report_path = 'Reports\\Spelling_{r}_{c}_{l}_{a}.xlsx'.format(
            r=self.region, c=self.country, a=self.account_type, l=self.language)
        self.emptypage_report_path = 'Reports\\EmptyPage_{r}_{c}_{l}_{a}.xlsx'.format(
            r=self.region, c=self.country, a=self.account_type, l=self.language)
        
        self.phrase = self.translated_phrases[language]
        self.defaultphrase = "Related content"
        self.reverse_dict_path = 'Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)
        self.aruba_links_path = 'Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt'.format(
            r=self.region, c=self.country, l=self.language, a=self.account_type)

        # Playwright objects
        self.playwright = playwright
        self.browser = browser
        self.context = None
        self.page = page
        
        # NEW: Country manager will be initialized in setUp()
        self.country_manager = None


    def setUp(self):
        if self.playwright is None or self.browser is None or self.page is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)
        
        # NEW: Initialize country manager
        initialize_country_manager(self)

    
    def country_similarity(self, a: str, b: str):
        """
        Fully dynamic similarity score between two country names.
        (Kept for backward compatibility, but CountryManager has its own)
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
    # SIMPLIFIED: This is now mainly used at initial login
    # -------------------------------------------------------------------------------------
    def handle_country_and_overlay(self):
        """
        Initial country setup (used during login).
        For ongoing checks, use country_manager.verify_and_fix_country() instead.
        """
        page = self.page

        # --- STEP 1: Check and close notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=10000)
            if overlay and overlay.is_visible():
                print("⚠️ Notification overlay detected.")
                try:
                    close_btn = page.locator("#closemsg")
                    close_btn.wait_for(state="visible", timeout=5000)
                    close_btn.click()
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                print("✅ Closed the notification overlay.")
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=15000)
                except Exception:
                    pass
        except PlaywrightTimeoutError:
            print("✅ No overlay appeared, continuing.")
        except Exception as e:
            print("⚠️ Overlay handling error:", e)
        

        # --- STEP 2: Click Eyeball icon ---
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", state="visible", timeout=30000)
            if eyeball:
                eyeball.click()
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)
        except Exception as e:
            print("⚠️ Eyeball icon error:", e)
        

        # --- STEP 3: Extract current country ---
        try:
            selector = (
                '#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet '
                '> div > div.portlet-content-container > div > div.MHMGuserdescrp '
                '> div > div.MHMGcountryname'
            )
            country_element = page.wait_for_selector(selector, state="visible", timeout=20000)
            current_country = country_element.inner_text().strip() if country_element else ""
            print("🌍 Current Country:", current_country if current_country else "Unknown")
        except Exception as e:
            current_country = ""
            print("⚠️ Could not detect current country:", e)

        # --- STEP 4: Check if already correct ---
        if current_country.lower() == self.country.lower():
            print(f"✅ Country already set to '{current_country}'")
            try:
                if eyeball:
                    eyeball.click()
                    page.wait_for_load_state("domcontentloaded", timeout=10000)
                    time.sleep(2)
            except:
                page.click("body")
                time.sleep(1)
            return current_country

        # --- STEP 5: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", 
                                            state="visible", timeout=15000)
            if loc_btn:
                loc_btn.click()
                time.sleep(1)
        except Exception as e:
            print("⚠️ Country dropdown error:", e)
        

        # --- STEP 6: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", 
                                  state="visible", timeout=20000)
        except Exception as e:
            print("⚠️ Country list not loaded:", e)
        

        # --- STEP 7: Switch country ---
        try:
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

            if best_score >= 0.30 and best_option:
                try:
                    best_option.click()
                except Exception:
                    page.evaluate("(el)=>el.click()", best_option)

                print(f"🌐 Country dynamically matched → '{best_name}' (score={best_score:.2f})")

                time.sleep(2)
                br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div", 
                                                     state="visible", timeout=15000)
                if br_container:
                    br_container.click()
                    print("⏳ Waiting for country change to complete...")
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=30000)
                        page.wait_for_load_state("networkidle", timeout=90000)
                    except Exception as e:
                        print(f"⚠️ Country change load warning: {e}")
                    
                    time.sleep(5)
                    print("✅ Country change completed")
            else:
                print(f"⚠️ No strong dynamic match for '{self.country}'. Best score={best_score:.2f}")
                
        except Exception as e:
            print("⚠️ Country switching error:", e)

        return current_country


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
        except PlaywrightTimeoutError:
            print("Login redirect click failed")
        except Exception:
            pass

        time.sleep(5)
        page.goto(self.base_url)

    
    @log_module_metric("Translation+Spelling+Empty")
    def parent(self):
        """Main function that runs all three checks: Translation, Spelling, and Empty Page"""
        
        def write_excel(errors, category):
            """Write errors to Excel report"""
            with open(self.reverse_dict_path, "r") as f:
                dictionary = ast.literal_eval(f.read())

            if category == 'Translation Error':
                published_report_path = self.translation_report_path
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
            elif category == 'Spelling Error':
                published_report_path = self.spelling_report_path
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
            else:  # Empty Page
                published_report_path = self.emptypage_report_path
                iterator = errors
                des = ['Empty page'] * len(errors)

            issueid = 1
            account = self.username
            region = self.region
            country = self.country
            language = self.language
            Fixer_mail = ''
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

                # Find parent link
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

            r = pd.DataFrame(report, columns=[
                'Issue ID', 'Demo Account', 'Category', 'Region', 'Country', 
                'Language', 'Link', 'Error Link', 'Description', 
                'Time Identified', 'Mail ID', 'Status', 'Comments'
            ])
            r.to_excel(published_report_path)
            return

        # NEW: Decorator applied to integrate function
        @ensure_country_for_delayed
        def integrate(site):
            """Navigate to a site and return HTML source and BeautifulSoup object"""
            page = self.page
            try:
                resp = page.goto(site, wait_until="networkidle", timeout=60000)
            except PlaywrightTimeoutError:
                resp = None
            except Exception:
                return None, None

            if site in self.delayed_loading_links or site.strip() in self.delayed_loading_links:
                print('SLEEPING:', site)
                from playsound3 import playsound
                playsound("Sound/beep-01a.wav")
                # Decorator handles country check automatically
                time.sleep(45)

            # Check for homepage redirects
            final_url = (page.url or "").split('#')[0].rstrip('/')
            for p in HOME_PREFIXES:
                if final_url == p:
                    return None, None

            try:
                src = page.content()
            except Exception:
                return None, None
            
            soup = BeautifulSoup(src, 'html.parser')
            return src, soup


        def aruba(soup):
            """Check if page has Aruba tag"""
            find_aruba = soup.find_all('span', class_='arubaTag')
            return bool(find_aruba)


        def filter_links(list_of_links, links_not_to_be_checked):
            """Filter out links that should not be checked"""
            actual_list_of_links = []
            list_of_links = [link.strip() for link in list_of_links]
            links_not_to_be_checked = [link.strip() for link in links_not_to_be_checked]
            actual_excluded_links = set()
            
            for lte in links_not_to_be_checked:
                for ptl in list_of_links:
                    if ptl.startswith(lte) or "products" in ptl or \
                       'https://partner.hpe.com/group/prp/settings' in ptl or \
                       ptl == 'https://partner.hpe.com':
                        actual_excluded_links.add(ptl)
            
            actual_list_of_links = list(set(list_of_links) - set(actual_excluded_links))
            return actual_list_of_links


        def no_content_pg(soup):
            """Check if page has error message"""
            errmsg = ["Oops! We can't find that page", "We cant find the page you're looking for", 
                     "the page you're looking for no longer exists"]
            text = soup.get_text()
            for msg in errmsg:
                if msg in text:
                    return True
            return False


        # Load links from page tree
        f = open(self.page_tree_path, 'r')
        list_of_links = f.read().splitlines()

        all_links_trans = filter_links(list_of_links, self.links_not_to_be_checked)
        all_links_empty = filter_links(list_of_links, self.not_to_check_links)

        # Initialize error collections
        translation_errors = {}
        spelling_errors = {}
        empty_page_errors = []
        aruba_links = set()

        # NEW: Periodic country verification
        link_counter = 0
        
        # Process each link
        for link in list_of_links:
            link_counter += 1
            
            # NEW: Periodic check every 10 links
            if link_counter % 10 == 0:
                print(f"\n🔄 Periodic country verification (link #{link_counter})...")
                self.country_manager.verify_and_fix_country(force=True)
            
            print(f'\nProcessing ({link_counter}/{len(list_of_links)}): {link}')
            
            src, soup = integrate(link)
            if src is None:
                # Redirected to homepage, skip this link
                continue

            # Check for Aruba tag
            aruba_bool = aruba(soup)
            if aruba_bool:
                if (link != 'https://partner.hpe.com' and 
                    link != 'https://partner.hpe.com/group/prp' and 
                    link != 'https://partner.hpe.com/group/prp/home'):
                    aruba_links.add(link)

            # Check for error pages
            nocontent = no_content_pg(soup)
            if nocontent:
                empty_page_errors.append(link)
                continue

            # Run checks based on link filters
            if link in all_links_trans and link in all_links_empty:
                # Translation check for non-English languages
                if self.language != 'English' and self.language != 'Singaporean':
                    print('  → Running translation check...')
                    err = mtrans.callable_extract(link, src, soup, self.language)
                    if err:
                        translation_errors.update({link: err})
                        print(f'  ✗ Found {len(err)} translation errors')
                else:
                    print('  → Running spelling check...')
                    gramm = msc.callable_extract(link, src, soup, self.language)
                    if gramm:
                        spelling_errors.update({link: gramm})
                        print(f'  ✗ Found {len(gramm)} spelling errors')
                
                # Empty page check
                empty_result = mep.emptypagecheck(link, self.phrase, self.defaultphrase, soup)
                if empty_result:
                    empty_page_errors.append(empty_result)

            elif link in all_links_empty:
                empty_result = mep.emptypagecheck(link, self.phrase, self.defaultphrase, soup)
                if empty_result:
                    empty_page_errors.append(empty_result)

            elif link in all_links_trans:
                if self.language != 'English' and self.language != 'Singaporean':
                    print('  → Running translation check...')
                    err = mtrans.callable_extract(link, src, soup, self.language)
                    if err:
                        translation_errors.update({link: err})
                        print(f'  ✗ Found {len(err)} translation errors')
                else:
                    print('  → Running spelling check...')
                    gramm = msc.callable_extract(link, src, soup, self.language)
                    if gramm:
                        spelling_errors.update({link: gramm})
                        print(f'  ✗ Found {len(gramm)} spelling errors')

            print('─' * 70)

        # Clean empty page errors
        empty_page_errors = [err for err in empty_page_errors if err != '']

        # Write reports
        print('\n' + '=' * 70)
        print('GENERATING REPORTS...')
        print('=' * 70)
        
        if empty_page_errors:
            print(f'Writing Empty Page report: {len(empty_page_errors)} errors')
            write_excel(empty_page_errors, 'Empty Page')
        
        if self.language != 'English' and self.language != 'Singaporean':
            if translation_errors:
                print(f'Writing Translation report: {len(translation_errors)} errors')
                write_excel(translation_errors, 'Translation Error')
        else:
            if spelling_errors:
                print(f'Writing Spelling report: {len(spelling_errors)} errors')
                write_excel(spelling_errors, 'Spelling Error')

        # Save Aruba links
        with open(self.aruba_links_path, 'w') as filehandle:
            for listitem in aruba_links:
                filehandle.write('%s\n' % listitem)

        print('\nAll reports generated successfully!')

    
    def tearDown(self):
        """Clean up Playwright resources"""
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

        # Allocate work to fixers
        try:
            df_trans = pd.read_excel(self.translation_report_path)
            if len(df_trans) > 0:
                work.work_alloc_execute(self.translation_report_path, 'Fixers_list.xlsx', 
                                       self.aruba_links_path)
        except FileNotFoundError:
            pass

        try:
            df_spell = pd.read_excel(self.spelling_report_path)
            if len(df_spell) > 0:
                work.work_alloc_execute(self.spelling_report_path, 'Fixers_list.xlsx', 
                                       self.aruba_links_path)
        except FileNotFoundError:
            pass

        try:
            df_empty = pd.read_excel(self.emptypage_report_path)
            if len(df_empty) > 0:
                work.work_alloc_execute(self.emptypage_report_path, 'Fixers_list.xlsx', 
                                       self.aruba_links_path)
        except FileNotFoundError:
            pass


def run_account(account):
    """Run all checks for a single account"""
    try:
        prp_login = module_login_lang.PRP(*account)
        prp_login.setUp()
        login_bool = prp_login.login()

        if not login_bool:
            print('DEMO ACCOUNT', account, 'FAILED TO LOGIN')
            prp_login.tearDown()
            return

        prp_main = PRP(*account, playwright=prp_login.playwright, 
                       browser=prp_login.browser, page=prp_login.page)
        prp_main.setUp()
        prp_main.parent()
        prp_main.tearDown()
        
        from playsound3 import playsound
        playsound("Sound/beep-01a.wav")
        print(f"✓ Finished processing: {account[0]}")
    except Exception as e:
        print(f"✗ Exception while processing {account[0]}: {e}")


if __name__ == '__main__':
    credentials = [
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
    ]

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(run_account, credentials)