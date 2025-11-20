import time
import datetime
import threading
import ast
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import urllib3
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

import work_phase_3 as work

# HTTP client with short timeouts
timeout = urllib3.util.Timeout(connect=2.0, read=1.0)
http = urllib3.PoolManager(timeout=timeout)


class PRP:
    base_url = "https://partner.hpe.com"
    webdriver_path = "Webdrivers\\chromedriver.exe"
    links_to_exclude = work.doc_reader("lte_external.docx")
    links_to_exclude = [s.strip() for s in links_to_exclude if s != ""]

    def __init__(self, username: str, password: str, region: str, country, language, acc_type):
        self.username = username
        self.password = password
        if region == "NA":
            region = "NAR"
        self.region = region
        self.country = country
        self.account_type = acc_type
        self.language = language

        self.page_tree_path = "Page Trees\\PageTree{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, a=self.account_type, l=self.language
        )
        self.report_path = "Reports\\Broken_Link_{r}_{c}_{l}_{a}.xlsx".format(
            r=self.region, c=self.country, a=self.account_type, l=self.language
        )
        self.tree_dict_path = "Tree Dicts\\TreeDict{r}_{c}_{l}_{a}.json".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.external_urls_path = "External Urls\\External{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.document_links = "DocumentLinks\\Doclinks{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.reverse_dict_path = "Reverse Dicts\\RevDict{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )
        self.aruba_links_path = "Aruba Urls\\Aruba{r}_{c}_{l}_{a}.txt".format(
            r=self.region, c=self.country, l=self.language, a=self.account_type
        )

        self.lock = threading.Lock()
        self.pw = None
        self.browser = None
        self.page = None

    # ------------------------------------------------------------------
    # SETUP (Playwright)
    # ------------------------------------------------------------------
    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)

    # ------------------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------------------
    def test_load_home_page(self):
        page = self.page

        page.goto(self.base_url)
        page.fill("#oktaEmailInput", self.username)
        page.click("#oktaSignInBtn")
        page.fill("#password-sign-in", self.password)
        page.click("#onepass-submit-btn")

        # Wait for post-login redirect link, if present
        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except TimeoutError:
            print("Login redirect click failed")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # BROKEN LINK CHECK
    # ------------------------------------------------------------------
    def test_multiple_broken(self):
        def brokencheck():
            broken_links = []

            # Read links from page tree and document links
            with open(self.page_tree_path, "r", encoding="utf-8") as f1:
                l1 = f1.read().splitlines()
            with open(self.document_links, "r", encoding="utf-8") as f3:
                l3 = f3.read().splitlines()

            l4 = l1 + l3
            doc_links_set = {s.strip() for s in l3 if s.strip()}

            # Known error messages that indicate the page is effectively broken
            error_markers = [
                "not found the requested resource could not be found",
                "service unavailable the server is temporarily unable to service your request. please try again later",
                "service unavailable the server is temporarily unable to service your request due to maintenance downtime capacity",
                "this site can't be reached cf-passport.it.hpe.com's server ip address could not be found",
                "400 bad request",
                "http status 403 request forbidden.",
                "service unavailable dns failure the server is temporarily unable to service your request. please try again later",
                "We can't find the page you're looking for",
                "Content expired",
                "There's nothing here",
                "400 Bad Request",
                "You are attempting to access an unknown show. Please check the URL and try again.",
                "Error:",
                "404 - Page Not Found",
                "The requested Certification is no longer active, please",
                "connection error",
                "Error downloading XXXXXXX",
                "Request has invalid parameter(s)",
                "This partnercommunications.hpe.com page can't be found",
                "Page Expired",
                "Unable to display the page you have requested.",
                "This site can't be reached",
                "Your connection is not private",
                "Error logging into Litmos, please contact your administrator.",
                "This recording does not exist.",
                "404 - File or directory not found",
                "You don't have permission to view this page",
                "Content not found",
                "Error downloading"

            ]

            all_links_to_be_checked = []
            seen = set()
            for raw in l4:
                link = raw.strip()
                if not link or link in self.links_to_exclude:
                    continue
                if link in seen:
                    continue
                seen.add(link)
                all_links_to_be_checked.append(link)

            page = self.page

            for link in all_links_to_be_checked:
                is_doc_link = link in doc_links_set

                # Internal PRP links: Playwright + login session
                if link.startswith("https://partner.hpe.com"):
                    try:
                        resp = None
                        try:
                            resp = page.goto(link, wait_until="networkidle")
                        except PlaywrightTimeoutError:
                            # Even on timeout, page.url may still reflect the final location
                            pass

                        final_url = page.url
                        # Ignore links that end up on the portal home page variants
                        if final_url in {
                            "https://partner.hpe.com/group/prp",
                            "https://partner.hpe.com/",
                            "https://partner.hpe.com/group/prp/home",
                            "https://partner.hpe.com/home",
                            "https://partner.hpe.com/group/prp/home?tutorial=homepage",
                        }:
                            continue

                        # HTTP error status
                        if resp is not None and hasattr(resp, "status"):
                            if resp.status >= 400 and link not in broken_links:
                                broken_links.append(link)

                        # Additional check for document links: error messages in page content
                        if is_doc_link:
                            try:
                                content = page.content().lower()
                                for msg in error_markers:
                                    if msg in content:
                                        if link not in broken_links:
                                            broken_links.append(link)
                                        break
                            except Exception:
                                # If content can't be read, fall back to status behaviour only
                                pass
                        # If resp is None but navigation did not clearly fail, do not mark as broken
                    except Exception:
                        # Navigation failed entirely; treat as broken
                        if link not in broken_links:
                            broken_links.append(link)

                # External links: simple HTTP status check
                else:
                    try:
                        r = http.request("GET", link)
                        if hasattr(r, "status") and r.status >= 400:
                            if link not in broken_links:
                                broken_links.append(link)
                    except Exception as e:
                        ee = str(e)
                        if "NewConnectionError" in ee or "MaxRetryError" in ee:
                            if link not in broken_links:
                                broken_links.append(link)

            write_excel(broken_links)

        def write_excel(broken_links):
            with open(self.reverse_dict_path, "r", encoding="utf-8") as file4:
                a = file4.read()
            dictionary = ast.literal_eval(a)

            # Normalize keys by trimming whitespace for robust matching
            normalized_dict = {str(k).strip(): v for k, v in dictionary.items()}

            issueid = 1
            category = "Broken Link"
            account = self.username
            region = self.region
            country = self.country
            language = self.language
            Fixers = ""
            Fixer_mail = ""
            status = "New"
            comments = "-"
            report = []

            for ele in broken_links:
                linkele = []
                linkele.append(issueid)
                linkele.append(account)
                linkele.append(category)
                linkele.append(region)
                linkele.append(country)
                linkele.append(language)

                key = str(ele).strip()
                parents = normalized_dict.get(key)
                source_link = ""
                if parents:
                    # Use last parent, but if it equals the child and there are multiple,
                    # fall back to the first parent
                    try:
                        s_url = parents[-1]
                        s_url2 = parents[0]
                        if str(s_url).strip() == key and len(parents) > 1:
                            source_link = s_url2
                        else:
                            source_link = s_url
                    except Exception:
                        source_link = ""

                # If no parents found or an error occurred, leave source_link blank
                linkele.append(source_link)
                des = "Broken link"
                linkele.append(ele)
                linkele.append(des)
                linkele.append(datetime.datetime.now())
                linkele.append(Fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issueid += 1

            df_report = pd.DataFrame(
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
            df_report.to_excel(self.report_path, index=False)

        brokencheck()

    # ------------------------------------------------------------------
    # TEARDOWN
    # ------------------------------------------------------------------
    def tearDown(self):
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

        # Work allocation on generated report, if any
        try:
            df = pd.read_excel(self.report_path)
            if len(df) > 0:
                work.work_alloc_execute(self.report_path, "Fixers_list.xlsx", self.aruba_links_path)
        except FileNotFoundError:
            pass


def run_account(account):
    try:
        prp = PRP(*account)
        prp.setUp()
        prp.test_load_home_page()
        prp.test_multiple_broken()
        prp.tearDown()
        from playsound3 import playsound

        playsound(r"Sound\beep-01a.wav")
        print("Finished processing:", account[0])
    except Exception as e:
        print(f"Error while processing {account[0]}: {e}")


if __name__ == "__main__":
    credentials = [
        ["mhmg_albert_dist1@yopmail.com", "Login2Bot!", "EMEA", "Turkey", "Turkish", "T2"],
    ]

    with ThreadPoolExecutor(max_workers=1) as executor:
        executor.map(run_account, credentials)
