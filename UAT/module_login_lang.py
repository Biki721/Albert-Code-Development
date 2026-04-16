# THIS MODULE LOGS INTO THE SETTINGS PAGE AND DETECTS THE DISPLAY LANGUAGE.
# IF THE DISPLAY LANGUAGE IS NOT THE LOCAL LANGUAGE, THE LOCAL LANGUAGE IS CHOSEN

import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import work_phase_3 as work
import win32com.client as win32
from bs4 import BeautifulSoup
import datetime
from metric_report import metric_report, log_login_metric, log_language_metric
from concurrent.futures import ThreadPoolExecutor


class PRP():
    base_url = 'https://partner.hpe.com'

    delayed_loading_links = work.doc_reader("delayed_loading.docx")
    delayed_loading_links = [s.strip() for s in delayed_loading_links if s != '']
    breadcrumblinks = work.doc_reader("breadcrumb_links.docx")
    breadcrumblinks = [s.strip() for s in breadcrumblinks if s != '']
    absurd_links = work.doc_reader("absurd_links.docx")
    absurd_links = [s.strip() for s in absurd_links if s != '']
    breadcrumb_prefix = work.doc_reader("Breadcrumb_Prefix.docx")
    breadcrumb_prefix = [s.strip() for s in breadcrumb_prefix if s != '']

    COUNTRY_MAP = {
        "United Kingdom": "GB", "South Korea": "KR", "China": "CN", "Japan": "JP",
        "Italy": "IT", "Brazil": "BR", "Taiwan": "TW", "Indonesia": "ID",
        "France": "FR", "Germany": "DE", "Spain": "ES", "Turkey": "TR"
    }

    LANG_VALUE_MAP = {
        "English": "EN", "Simplified Chinese": "ZH", "Chinese": "ZH",
        "Korean": "KO", "Japanese": "JA", "Italian": "IT", "Portuguese": "PT",
        "Taiwan": "ZH", "Indonesian": "IN", "Spanish": "ES", "Turkish": "TR",
        "German": "DE", "French": "FR"
    }

    LANG_CODE_MAP = {
        "English": "en_US", "Korean": "ko_KR", "Japanese": "ja_JP", "Chinese": "zh_CN",
        "Simplified Chinese": "zh_CN", "Italian": "it_IT", "German": "de_DE",
        "French": "fr_FR", "Spanish": "es_ES", "Portuguese": "pt_BR",
        "Turkish": "tr_TR", "Indonesian": "id_ID"
    }

    def __init__(self, username: str, password: str, region: str, country, language, acc_type):

        self.username = username
        self.password = password

        if region == "NA":
            region = "NAR"
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language

        if language == 'Taiwan':
            self.language = 'Chinese'
        elif language == "Simplified Chinese":
            self.language = "Chinese"
        elif language == 'LARSpanish':
            self.language = 'Spanish'

        self.page_tree_path = f'Page Trees\\PageTree{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.doc_link_path = f'DocumentLinks\\Doclinks{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.reverse_dict_path = f'Reverse Dicts\\RevDict{self.region}_{self.country}_{self.language}_{self.account_type}.txt'
        self.external_urls_path = f'External Urls\\External{self.region}_{self.country}_{self.language}_{self.account_type}.txt'

        self.login_errmsg = [
            'Albert demo account login error',
            f'Hi there!\n\nThe demo account {self.username} has a login error.\nPlease fix it.\n\nThank you,\nAlbert salutes you.'
        ]
        self.lang_errmsg = [
            'Demo account preferred language issue - Fixed',
            f'Hi there!\n\nAlbert updated the preferred language for {self.username}.\n\nThank you,\nAlbert salutes you.'
        ]

        self.lang = {
            'en-US': 'English', 'fr-FR': 'French', 'de-DE': 'German', 'it-IT': 'Italian',
            'ja-JA': 'Japanese', 'ko-KO': 'Korean', 'pt-PT': 'Portuguese', 'pt-BR': 'Portuguese',
            'ru-RU': 'Russian', 'es-ES': 'Spanish', 'zh-TW': 'Chinese', 'zh-CN': 'Chinese',
            'tr-TR': 'Turkish', 'id-ID': 'Indonesian', "ZH": "Simplified Chinese"
        }

        self.current_datetime = datetime.datetime.now()
        self.current_date = None
        self.current_month = None
        self.current_time = None

        self.playwright = None
        self.browser = None
        self.page = None

    # -------------------------------------------------------------
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(60000)  # Set default timeout to 60 seconds
        self.page.wait_for_load_state("domcontentloaded")
        self.page.wait_for_load_state("networkidle", timeout=90000)

    # -------------------------------------------------------------
    def email(self, errmsg):
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = 'biki.dey1@hpe.com'
        mail.Subject = errmsg[0]
        mail.Body = errmsg[1]
        mail.Send()

    # -------------------------------------------------------------
    def test_load_home_page(self):
        page = self.page

        try:
            page.goto(self.base_url, wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print(f"⚠️ Home page navigation warning: {e}")
            time.sleep(3)
        
        page.wait_for_selector("#oktaEmailInput", state="visible", timeout=30000)
        page.fill("#oktaEmailInput", self.username)
        self.login_title = page.title()
        page.click("#oktaSignInBtn")
        page.wait_for_selector("#password-sign-in", state="visible", timeout=30000)
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")
        
        try:
            page.wait_for_load_state("networkidle", timeout=90000)
        except Exception as e:
            print(f"⚠️ Post-login load warning: {e}")
            time.sleep(5)

    # -------------------------------------------------------------
    def tearDown(self):
        try: self.page.close()
        except: pass
        try: self.browser.close()
        except: pass
        try: self.playwright.stop()
        except: pass

    # -------------------------------------------------------------
    @log_login_metric
    def login(self):
        self.test_load_home_page()
        page = self.page
        current_country = self.handle_country_and_overlay()
        
        # Critical: Wait longer after country selection as it may trigger session/redirect
        print("⏳ Stabilizing after country selection...")
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=90000)
        except Exception as e:
            print(f"⚠️ Network idle timeout (continuing anyway): {e}")
        
        # Additional wait for any session updates
        time.sleep(5)

        self._open_settings_page(page)
        try:
            page.wait_for_url("**/settings*", wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print(f"Settings page URL check warning: {e}")

        new_title = page.title()

        if hasattr(self, 'login_title') and self.login_title == new_title:
            print("DEMO ACCOUNT FAILED:", self.username)
            try: self.email(self.login_errmsg)
            except: pass
            return False

        self.disp_lang = self._detect_lang()

        self.current_date = self.current_datetime.date()
        self.current_month = self.current_date.strftime("%B")
        self.current_time = self.current_datetime.strftime("%H:%M:%S")

        if self.disp_lang != self.language:
            self._change_lang()

        return True

    # -------------------------------------------------------------
    def _detect_lang(self):
        html = self.page.content()
        soup = BeautifulSoup(html, 'html.parser')
        disp_lang = soup.html.get('lang') if soup.html else None
        disp_lang = self.lang.get(disp_lang)
        print("DISPLAY LANGUAGE:", disp_lang, " PREFERRED:", self.language)
        return disp_lang

    # -------------------------------------------------------------
    def select_country(self, page, country_name):
        iso_value = self.COUNTRY_MAP.get(country_name)
        selector = "#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_INSTANCE_WIWF7MxPXFUm_country"
        page.wait_for_selector(selector, state="visible", timeout=30000)
        page.select_option(selector, iso_value)
        # Wait for any AJAX calls to complete
        page.wait_for_load_state("networkidle", timeout=30000)
        print("Country selected:", country_name)

    # -------------------------------------------------------------
    def country_similarity(self, a, b):
        if not a or not b:
            return 0
        a = a.lower()
        b = b.lower()

        a_tokens = set(a.replace("(", " ").replace(")", " ").split())
        b_tokens = set(b.replace("(", " ").replace(")", " ").split())
        token_overlap = len(a_tokens & b_tokens)
        token_score = token_overlap / max(len(a_tokens), 1)

        matches = sum(1 for ch in a if ch in b)
        char_score = matches / max(len(a), 1)

        return token_score * 0.6 + char_score * 0.4

    # -------------------------------------------------------------------------------------
    # HANDLE OVERLAY, EYEBALL, AND COUNTRY SELECTION
    # -------------------------------------------------------------------------------------
    def handle_country_and_overlay(self):
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
                # Wait for eyeball panel to appear
                page.wait_for_load_state("domcontentloaded", timeout=10000)
                time.sleep(2)  # Small delay for animations
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

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", state="visible", timeout=15000)
            if loc_btn:
                loc_btn.click()
                # Wait for dropdown to appear
                time.sleep(1)
        except Exception as e:
            print("⚠️ Country dropdown error:", e)
        

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", state="visible", timeout=20000)
        except Exception as e:
            print("⚠️ Country list not loaded:", e)
        

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

                    # Wait for country change to process
                    time.sleep(2)
                    br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div", state="visible", timeout=15000)
                    if br_container:
                        br_container.click()
                        print("⏳ Waiting for country change to complete...")
                        # Wait for page reload after country change - this is critical!
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=30000)
                            page.wait_for_load_state("networkidle", timeout=90000)
                        except Exception as e:
                            print(f"⚠️ Country change load warning: {e}")
                        
                        # Additional wait to ensure all redirects and session updates complete
                        time.sleep(5)
                        print("✅ Country change completed")
                else:
                    print(f"⚠️ No strong dynamic match for '{self.country}'. Best score={best_score:.2f}")
                
        except Exception as e:
            print("⚠️ Country switching error:", e)

        return current_country

    # ======================================================================
    # --------------------- LANGUAGE CHANGE HELPERS ------------------------
    # ======================================================================

    def _open_settings_page(self, page):
        print("📄 Navigating to settings page...")
        
        # Check current URL first
        current_url = page.url
        print(f"Current URL before navigation: {current_url}")
        
        try:
            # Use a more lenient wait strategy
            page.goto("https://partner.hpe.com/group/prp/settings", wait_until="commit", timeout=90000)
            print("✅ Navigation committed")
        except Exception as e:
            print(f"⚠️ Navigation error (may be normal for redirects): {e}")
        
        # Wait for page to stabilize after navigation
        time.sleep(3)
        
        # Ensure settings page is fully loaded
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception as e:
            print(f"⚠️ DOM load warning: {e}")
        
        try:
            page.wait_for_load_state("networkidle", timeout=60000)
        except Exception as e:
            print(f"⚠️ Network idle warning: {e}")
        
        # Verify we're on settings page
        final_url = page.url
        print(f"Final URL: {final_url}")
        
        if "settings" in final_url.lower():
            print("✅ Successfully navigated to settings page")
        else:
            print(f"⚠️ May not be on settings page. Current URL: {final_url}")

    def _select_country_block(self, page):
        print("Selecting country:", self.country)
        self.select_country(page, self.country)
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

    def _select_language_block(self, page, value):
        lang_selector = "#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_INSTANCE_WIWF7MxPXFUm_preferredLanguage"
        page.wait_for_selector(lang_selector, state="visible", timeout=30000)
        page.select_option(lang_selector, value=value)
        # Wait for any dependent fields to update
        time.sleep(1)
        print("✔ Language selected:", self.language)

    def _select_job_title_block(self, page):
        title_selector = "#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_INSTANCE_WIWF7MxPXFUm_title"
        page.wait_for_selector(title_selector, state="visible", timeout=30000)
        
        try:
            # Wait for options to be populated
            page.wait_for_function(
                f"document.querySelector('{title_selector}').options.length > 1",
                timeout=10000
            )
            
            # Get the first option that has a non-empty value (skip "Select One")
            first_option = page.locator(f"{title_selector} option[value]:not([value=''])").first
            first_option.wait_for(state="attached", timeout=10000)
            first_value = first_option.get_attribute("value")
            
            # Select the first valid option
            page.select_option(title_selector, value=first_value)
            time.sleep(0.5)  # Small delay after selection
            print(f"✔ Job Title selected: {first_value}")
        except Exception as e:
            print(f"⚠️ Error selecting job title, trying fallback: {e}")
            # Fallback: select by index
            page.select_option(title_selector, index=1)
            time.sleep(0.5)
            print("✔ Job Title selected (fallback method)")

    def _fill_phone_block(self, page):
        phone_selector = "#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_INSTANCE_WIWF7MxPXFUm_workNumber"
        phone = page.locator(phone_selector)
        phone.wait_for(state="visible", timeout=30000)
        phone.scroll_into_view_if_needed()
        time.sleep(0.5)  # Wait for scroll to complete
        phone.fill("88888866666")
        time.sleep(0.5)
        print("✔ Work Number entered")

    def _save_profile_block(self, page):
        save_btn = page.locator("#personal-save-personal-cancel")
        save_btn.wait_for(state="visible", timeout=30000)
        save_btn.scroll_into_view_if_needed()
        time.sleep(0.5)
        save_btn.click(force=True)
        print("✔ SAVE clicked")

        # Wait for popup with multiple strategies
        popup = page.locator(".settings-warningModal-content")
        try:
            popup.wait_for(state="visible", timeout=30000)
            print("✔ Success popup appeared")
        except:
            # Try alternate selector
            popup = page.locator(".modal-content")
            popup.wait_for(state="visible", timeout=10000)
            print("✔ Success popup appeared (alternate selector)")

        time.sleep(1)  # Let popup fully render
        
        close_btn = page.locator(".modal-footer button")
        close_btn.wait_for(state="visible", timeout=10000)
        close_btn.click(force=True)
        print("✔ Success popup closed")

        # Wait for popup to close and page to stabilize
        try:
            popup.wait_for(state="hidden", timeout=10000)
        except:
            pass
        page.wait_for_load_state("domcontentloaded", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=30000)

    def _apply_language_update(self, page, lang_code):
        update_url = (
            "https://partner.hpe.com/c/portal/update_language?"
            f"p_l_id=493064269&redirect=%2Fgroup%2Fprp%2Fsettings&"
            f"languageId={lang_code}&persistState=false&"
            "showUserLocaleOptionsMessage=false"
        )
        try:
            page.goto(update_url, wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print(f"⚠️ Language update navigation warning: {e}")
            time.sleep(3)
        
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=60000)
        except Exception as e:
            print(f"⚠️ Language page load warning: {e}")
        
        print("✔ Language updated")

    # ======================================================================
    # MAIN FUNCTION (SAME LOGIC, JUST SPLIT INTO FUNCTIONS)
    # ======================================================================
    @log_language_metric
    def _change_lang(self):
        page = self.page
        try:

            value = self.LANG_VALUE_MAP.get(self.language)
            lang_code = self.LANG_CODE_MAP.get(self.language)

            self._select_country_block(page)
            self._select_language_block(page, value)
            self._select_job_title_block(page)
            self._fill_phone_block(page)
            self._save_profile_block(page)

            print(f"Changing language → {self.language} ({lang_code})")
            self._apply_language_update(page, lang_code)

            try:
                self.email(self.lang_errmsg)
            except:
                pass

        except Exception as e:
            print("ERROR in _change_lang:", e)


# ======================================================================
def run_account(account):
    try:
        prp = PRP(*account)
        prp.setUp()
        prp.login()
        prp.tearDown()
        from playsound3 import playsound
        playsound(r"Sound\\beep-01a.wav")
        print("Finished:", account[0])
    except Exception as e:
        print("Error:", account[0], "→", e)

# ======================================================================

if __name__=='__main__':
    credentials = [
    ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ', 'Japan', 'Japanese', 'distri'],
]
    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(run_account, credentials)