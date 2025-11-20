from playwright.sync_api import sync_playwright, TimeoutError
import time
import pandas as pd
import datetime
import threading
from concurrent.futures import ThreadPoolExecutor
import work_phase_3 as work
from url_utils import load_home_prefixes, is_home_redirect_selenium   # Replace selenium func later
HOME_PREFIXES = load_home_prefixes('config/home_pages.txt')


class PRP:
    base_url = "https://partner.hpe.com"
    delayed_loading_links = [s.strip() for s in work.doc_reader("delayed_loading.docx") if s.strip()]
    absurd_links = [s.strip() for s in work.doc_reader("absurd_links.docx") if s.strip()]

    def __init__(self, username, password, region, country, language, acc_type):
        self.username = username
        self.password = password
        if region == "NA":
            region = "NAR"
        self.region = region
        self.country = country
        self.language = language
        self.account_type = acc_type
        self.page_tree_path = f'Page Trees\\PageTree{region}_{country}_{language}_{acc_type}.txt'
        self.report_path = f'Reports\\New_Tab_{region}_{country}_{language}_{acc_type}.xlsx'
        self.aruba_links_path = f'Aruba Urls\\Aruba{region}_{country}_{language}_{acc_type}.txt'
        self.tree_dict_path = f'Tree Dicts\\TreeDict{region}_{country}_{language}_{acc_type}.json'
        self.lock = threading.Lock()

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
        except TimeoutError:
            print("Login redirect click failed")

        time.sleep(5)

    # -------------------------------------------------------------------------------------
    # MAIN TEST
    # -------------------------------------------------------------------------------------
    def test_new_tab(self):
        self.test_load_home_page()

        notopening = []

        page = self.page

        # Helper function
        def demo_test(site_url):
            site_url = site_url.strip()
            if not site_url:
                return

            try:
                page.goto(site_url)

                # Skip homepage redirects
                try:
                    if any(prefix in page.url for prefix in HOME_PREFIXES):
                        return
                except:
                    pass

                # Delay for slow links
                if site_url in self.delayed_loading_links or site_url in self.absurd_links:
                    time.sleep(25)

            except Exception:
                return

            # Collect all <a> tags
            try:
                anchors = page.query_selector_all("a")
            except:
                return

            for a in anchors:
                try:
                    href = a.get_attribute("href")
                    target = a.get_attribute("target")

                    if not href:
                        continue
                    if not href.startswith("http"):
                        continue

                    # internal links that **should open in new tab but don’t**
                    if target is None or target.lower() not in ['_blank', 'blank', 'new', '_new']:
                        notopening.append([site_url, href])

                except:
                    continue

        # Read tree
        with open(self.page_tree_path, "r") as f:
            lines = f.readlines()

        for line in lines:
            demo_test(line)

        # Write Excel
        self.write_excel(notopening)

    # -------------------------------------------------------------------------------------
    def write_excel(self, notopening):
        rows = []
        issueid = 1

        for src, badlink in notopening:
            rows.append([
                issueid,
                self.username,
                "New Tab",
                self.region,
                self.country,
                self.language,
                src,
                badlink,
                "Link not opening in a new tab",
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
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey', 'Turkish', 'T2'],
    ]

    with ThreadPoolExecutor(max_workers=3) as exe:
        exe.map(run_account, credentials)
