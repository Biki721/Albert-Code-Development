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

    links_to_exclude = work.doc_reader("lte_external.docx")
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
        self.page_tree_path = f"Page Trees\\PageTree{region}_{country}_{language}_{acc_type}.txt"
        self.document_links = f"DocumentLinks\\Doclinks{region}_{country}_{language}_{acc_type}.txt"
        self.reverse_dict_path = f"Reverse Dicts\\RevDict{region}_{country}_{language}_{acc_type}.txt"
        self.report_path = f"Reports\\Broken_Link_{region}_{country}_{language}_{acc_type}.xlsx"
        self.aruba_links_path = f"Aruba Urls\\Aruba{region}_{country}_{language}_{acc_type}.txt"

        self.lock = threading.Lock()
        self.pw = None
        self.browser = None
        self.page = None

    # ------------------------------------------------------------------
    def setUp(self):
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.set_default_timeout(30000)

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

    # ------------------------------------------------------------------
    def test_multiple_broken(self):
        def brokencheck():
            broken_links = []

            with open(self.page_tree_path, encoding="utf-8") as f:
                page_links = f.read().splitlines()

            with open(self.document_links, encoding="utf-8") as f:
                doc_links = f.read().splitlines()

            all_links = page_links + doc_links
            doc_set = {x.strip() for x in doc_links if x.strip()}

            # Clean & dedupe
            seen = set()
            final_links = []
            for raw in all_links:
                link = raw.strip()
                if not link or link in seen or link in self.links_to_exclude:
                    continue
                seen.add(link)
                final_links.append(link)

            page = self.page

            for link in final_links:
                # -----------------------------
                # CASE 1: DOCUMENT LINKS
                # -----------------------------
                if link in doc_set:
                    try:
                        resp = page.request.get(link, max_redirects=5)
                        if resp.status >= 400:
                            broken_links.append(link)
                    except:
                        broken_links.append(link)
                    continue

                # -----------------------------
                # CASE 2: INTERNAL PRP LINKS
                # -----------------------------
                if link.startswith("https://partner.hpe.com"):
                    if is_internal_broken(page, link):
                        broken_links.append(link)
                    continue

                # -----------------------------
                # CASE 3: EXTERNAL LINKS
                # -----------------------------
                try:
                    r = http.request("GET", link)
                    if hasattr(r, "status") and r.status >= 400:
                        broken_links.append(link)
                except:
                    broken_links.append(link)

            write_excel(broken_links)

        # ------------------------------------------------------------------
        def write_excel(broken_links):
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
        ["mhmg_albert_dist1@yopmail.com", "Login2Bot!", "EMEA", "Turkey", "Turkish", "T2"],
    ]

    with ThreadPoolExecutor(max_workers=1) as exe:
        exe.map(run_account, credentials)
