"""
HPE Partner Portal (PRP) Broken-Link Checker — OPTIMIZED BUILD
================================================================
Reads the three artefact files produced by the crawler
(PageTree*.txt, Doclinks*.txt, RevDict*.txt), tests every link, and
writes a Broken_Link_*.xlsx report.

This module deliberately mirrors the naming conventions, attribute
names, and method structure of the crawler module so the two files
read as a matched pair.  Business logic, output filenames, folder
names, Excel column set, and run_account() entry point are all
UNCHANGED — swap this file in without touching anything else.

INPUT ARTEFACTS (produced by crawler, unchanged)
------------------------------------------------
  Page Trees/PageTree<tag>.txt
  DocumentLinks/Doclinks<tag>.txt
  Reverse Dicts/RevDict<tag>.txt

OUTPUT ARTEFACTS (unchanged)
----------------------------
  Reports/Broken_Link_<tag>.xlsx
  Aruba Urls/Aruba<tag>.txt          (via work.work_alloc_execute)

OPTIMIZATIONS APPLIED
---------------------
  1. Internal link checks use wait_until="domcontentloaded" instead of
     "networkidle".  networkidle rarely fires cleanly on this portal
     (long-polling, analytics beacons), so every link used to wait the
     full timeout before moving on.  DOM ready + 400 ms settle is
     enough to scan for the broken-page markers.

  2. External link checks use HEAD first, fall back to GET only if the
     server returns 405 (Method Not Allowed).  HEAD returns headers
     only — no body download — which is much faster on heavy external
     pages and reduces bandwidth.

  3. Transient external failures get one quick retry before being
     marked broken, eliminating single-attempt false positives from
     network blips and DNS slowness.

  4. Country re-verification navigates the shared page to the portal
     home BEFORE running the overlay/eyeball check.  Previously this
     ran against whatever URL was last tested, and the eyeball widget
     isn't rendered on broken pages or random deep pages, so the
     verification often silently no-op'd.

  5. run_account() wraps the pipeline in try/finally so teardown
     always runs — the browser is closed and the Excel report is
     always post-processed, even if an exception occurs mid-test.

  6. Shared-file concurrency fix for work.work_alloc_execute().
     That function reads and writes Fixers_list.xlsx, which is shared
     across ALL account workers.  Under MAX_PARALLEL >= 2 the previous
     teardown could hang indefinitely because two processes were
     racing on the same file (on Windows the Excel/openpyxl lock
     doesn't release cleanly across processes).  The new teardown:
       - closes the browser FIRST (so hangs can't strand Chromium)
       - serialises Fixers_list.xlsx access with a cross-process lock
       - runs the actual call in a child process with a hard timeout,
         so one stuck worker can never block the whole runner.

BUG FIXES
---------
  - Strong-marker "Oops! We can't find that page." is now lowercased
    to match the lowercased body (previously never fired).
  - Dead threading.Lock() removed (nothing was locking on it).
  - Redundant inline `from urllib.parse import urlsplit` removed
    (already imported at module top).
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import ast
import datetime
import sys
import time
from multiprocessing import Process
from pathlib import Path
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# CRITICAL: force unbuffered stdout so worker processes don't deadlock
# waiting for the Windows console lock.  Without this, two parallel workers
# can block each other when calling print() — the last visible output
# becomes "Report saved" and nothing further, because print() buffers are
# stuck waiting for a console lock held by the other process.
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
    sys.stderr.reconfigure(line_buffering=True, write_through=True)
except Exception:
    pass

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pandas as pd
import urllib3
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work
from metric_report import log_module_metric


# ===========================================================================
# SECTION 1 – CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).parent

# HTTP client with short timeouts for external link checks.
# connect=2s, read=3s (read relaxed from 1s to reduce timeout false positives
# on slow-but-working external servers).
_HTTP_TIMEOUT = urllib3.util.Timeout(connect=2.0, read=3.0)
http = urllib3.PoolManager(timeout=_HTTP_TIMEOUT)

# Default Playwright navigation timeout (milliseconds)
PAGE_TIMEOUT_MS: int = 30_000

# Internal-link browser navigation settings
INTERNAL_NAV_TIMEOUT_MS: int = 20_000     # goto timeout for internal links
INTERNAL_SETTLE_MS:      int = 400        # DOM settle after domcontentloaded

# External-link retry settings
EXTERNAL_RETRY_COUNT:    int = 1          # one retry on transient failure
EXTERNAL_RETRY_DELAY_S:  float = 1.5

# Country-check cadence (re-verify every 2 minutes)
COUNTRY_CHECK_INTERVAL_SECONDS: int = 120

# Post-processing (shared-file work_alloc_execute) safety limits
POST_PROCESS_TIMEOUT_S:  int = 120   # kill stuck post-processing after 2 min
FIXERS_LOCK_TIMEOUT_S:   int = 300   # wait up to 5 min for the shared lock

# Homepage patterns used for redirect-skip detection (document links)
HOMEPAGE_PATTERNS: tuple = (
    "https://partner.hpe.com/",
    "https://partner.hpe.com/home",
    "https://partner.hpe.com/group/prp",
    "https://partner.hpe.com/group/prp/home",
    "https://partner.hpe.com/group/prp/home?tutorial=homepage",
)

# Allowed redirect targets for internal-link checks (not considered broken)
INTERNAL_ALLOWED_REDIRECTS: frozenset = frozenset({
    "https://partner.hpe.com/",
    "https://partner.hpe.com/home",
    "https://partner.hpe.com/group/prp",
    "https://partner.hpe.com/group/prp/home",
    "https://partner.hpe.com/group/prp/home?tutorial=homepage",
})

# HTML body markers that indicate a real broken-page template.
# All entries are lowercase because the body is lowercased before matching
# (previously one marker had mixed case and could never fire).
#
# NOTE on false-positive risk: some of these phrases are generic enough
# that they can appear in legitimate page content (e.g. "page not available"
# in a per-region callout).  To mitigate this WITHOUT losing real detections,
# the body scan below uses document.body.innerText (visible text only) — so
# any occurrence inside <script>, <style>, data attributes, or hidden
# elements is ignored.  Keep all markers; the visibility filter is what
# prevents the FPs.
STRONG_BROKEN_MARKERS: tuple = (
    "we can't find the page you're looking for",
    "404 - page not found",
    "page not available",
    "content expired",
    "unable to display the page you have requested",
    "request has invalid parameter",
    "oops! we can't find that page.",
    "the page you are looking for no longer exists",
    "the page you're looking for no longer exists",
)

# Homepage-variant prefixes used to detect crawler-artifact parents.
# When the crawler records a document link discovered while on a page
# that redirected to home, the homepage gets logged as the parent.
# That parent is useless to a human fixing the issue, so we strip
# homepage variants from source-URL resolution in write_excel().
HOMEPAGE_VARIANT_PREFIXES: tuple = (
    "https://partner.hpe.com/home",
    "https://partner.hpe.com/group/prp/home",
    "https://partner.hpe.com/group/prp?",
    "https://partner.hpe.com/?",
)


# ===========================================================================
# SECTION 1B – SHARED-FILE CONCURRENCY HELPERS
# ===========================================================================
# These are needed because work.work_alloc_execute() reads and writes a
# SHARED file (Fixers_list.xlsx) that lives outside any single account's
# output set.  When multiple account processes finish at roughly the same
# time, they would otherwise race on that file.  On Windows this
# manifests as an indefinite hang (the Excel/openpyxl file lock is not
# released cleanly across processes) — which is the symptom that caused
# the runner to freeze after two accounts with no "Process finished"
# line ever appearing.
#
# We solve this with a simple lock file: only one process holds it at a
# time, and the lock is polled with a timeout so we never block forever.
# The lock is released in a `finally` block so crashes don't strand it.
# ---------------------------------------------------------------------------

import os
import errno


def _acquire_fixers_lock(lock_path: Path, timeout_s: int) -> bool:
    """
    Try to acquire an exclusive cross-process lock by creating `lock_path`
    atomically.  Returns True on success, False if timed out.

    We use O_CREAT | O_EXCL which is atomic on both Windows and POSIX:
    two processes racing on the same path will see exactly one succeed.
    """
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                os.write(fd, f"pid={os.getpid()}\ntime={time.time()}\n".encode())
            finally:
                os.close(fd)
            return True
        except FileExistsError:
            # Another worker holds the lock — wait and retry
            time.sleep(1)
        except OSError as exc:
            # Any other OS error: log and keep trying (e.g. temporary
            # access-denied on shared drives)
            if exc.errno not in (errno.EEXIST, errno.EACCES):
                print(f"⚠️  Unexpected error acquiring lock: {exc}")
            time.sleep(1)
    return False


def _release_fixers_lock(lock_path: Path) -> None:
    """Remove the lock file.  Silent if already gone."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except Exception as exc:
        # Never fatal — next acquirer will overwrite it anyway
        print(f"⚠️  Could not remove lock file {lock_path}: {exc}")


def _run_work_alloc_execute(report_path: str, fixers_path: str, aruba_path: str) -> None:
    """
    Top-level wrapper for work.work_alloc_execute — MUST be at module
    level so multiprocessing.Process can pickle it on Windows.
    Invoked as the target of a child process so we can impose a hard
    timeout on it.
    """
    try:
        work.work_alloc_execute(report_path, fixers_path, aruba_path)
    except Exception as exc:
        # Print so the parent can see the cause in the log before the
        # child exits with a non-zero code.
        print(f"⚠️  work_alloc_execute failed: {exc}")
        raise


# ===========================================================================
# SECTION 2 – INTERNAL LINK CHECKER
# ===========================================================================

def is_internal_broken(page, link: str) -> bool:
    """
    Check whether a PRP internal link is broken.

    Decision logic (in order):
      1. If the final landing URL is in the "allowed redirects" set
         (home-page variants) → NOT broken (intentional redirect).
      2. Read the visible body text (innerText).
         - If it contains a strong broken-page marker → BROKEN.
         - Note: scanning innerText (not raw HTML) avoids matching
           phrases inside <script>/<style>/hidden content.
      3. Otherwise, inspect HTTP status:
         - 4xx/5xx AND no discernible visible content → BROKEN
           (the server clearly failed and the page has nothing useful).
         - 4xx/5xx BUT visible content is substantial → NOT broken.
           Rationale: some portal pages return non-200 status codes
           for the document response while still rendering a fully
           usable page via client-side logic.  A status code alone
           is no longer sufficient to declare a FP.
      4. If everything above passed → NOT broken.

    Any unexpected exception during the check → conservative BROKEN.
    """
    resp = None
    try:
        try:
            resp = page.goto(
                link,
                wait_until="domcontentloaded",
                timeout=INTERNAL_NAV_TIMEOUT_MS,
            )
        except PlaywrightTimeoutError:
            pass

        # Short settle for any DOM updates immediately after load
        try:
            page.wait_for_timeout(INTERNAL_SETTLE_MS)
        except Exception:
            pass

        final_url = page.url or (resp.url if resp is not None else "")

        # Normalize final URL (strip query/fragment) for comparison
        try:
            split = urlsplit(final_url)
            base_url = f"{split.scheme}://{split.netloc}{split.path}"
        except Exception:
            base_url = final_url

        # (1) Allowed home-page redirect → intentional, not broken
        if base_url in INTERNAL_ALLOWED_REDIRECTS:
            return False

        # (2) Visible-text body marker scan.  innerText gives us only what
        # the user actually sees — scripts, hidden elements, and CSS drop
        # out automatically, which eliminates the most common FP source
        # (markers appearing in code or hidden containers).
        body = ""
        try:
            body = page.evaluate("() => document.body ? document.body.innerText : ''")
            if body:
                body = body.lower()
        except Exception:
            # Fallback to raw HTML if innerText fails — less precise but
            # better than no check at all.
            try:
                body = page.content().lower()
            except Exception:
                try:
                    body = resp.text().lower() if resp is not None else ""
                except Exception:
                    body = ""

        for marker in STRONG_BROKEN_MARKERS:
            if marker in body:
                return True

        # (3) HTTP status is no longer trusted on its own.  The portal
        # sometimes returns a 4xx for the document response while still
        # serving a fully-rendered usable page via JS — a status-only
        # check would mark these as broken (false positive).  Only
        # declare broken on bad status if the visible content is so
        # sparse that there's clearly nothing useful to the user.
        #
        # "Sparse" = fewer than 200 visible characters after stripping.
        # A real portal page has thousands of visible characters (nav,
        # breadcrumbs, banners, footers, content).  Genuine 404 pages
        # tend to be short.  This threshold catches error pages that
        # DON'T match one of our hard-coded markers while still letting
        # legitimate pages with bad status codes through.
        MIN_PAGE_LENGTH = 200
        visible_len = len((body or "").strip())

        if resp is not None and hasattr(resp, "status") and resp.status >= 400:
            if visible_len < MIN_PAGE_LENGTH:
                return True
            # Substantial content present → trust the page, ignore status
            # (the server's 4xx code was misleading or the content was
            # rendered client-side after the initial bad response).

        return False

    except Exception:
        # Any unexpected exception → treat as broken (conservative)
        return True


# ===========================================================================
# SECTION 3 – MAIN CLASS
# ===========================================================================

class PRP:
    """
    Authenticated broken-link checker for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class so the
    two modules read as a matched pair:
      - Playwright handles:  _playwright / _browser / _context / _session_page
      - Path attributes:      path_page_tree / path_doc_links / ...
      - Public methods:       setup / login / set_country / teardown
      - Private helpers:      _load_docx / _country_similarity / ...
    """

    BASE_URL = "https://partner.hpe.com"

    # ------------------------------------------------------------------
    # 3.1  Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        username:     str,
        password:     str,
        region:       str,
        country:      str,
        language:     str,
        account_type: str,
    ) -> None:
        # ── Credentials & locale ─────────────────────────────────────
        self.username     = username
        self.password     = password
        self.region       = "NAR" if region == "NA" else region
        self.country      = country
        self.language     = language
        self.account_type = account_type

        # ── Reference lists loaded from .docx files ───────────────────
        # Moved out of class body (matches crawler pattern) so a missing
        # file fails only the account that needs it, with a clear warning,
        # instead of crashing at import time.
        exclude_list = self._load_docx("lte_external.docx")

        # Pre-convert to a set for O(1) membership checks in the hot loop
        self._exclude_set: set = set(exclude_list)

        # ── Output file paths (filenames UNCHANGED) ──────────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree    = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_doc_links    = BASE_DIR / "DocumentLinks" / f"Doclinks{tag}.txt"
        self.path_reverse_dict = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"
        self.path_report       = BASE_DIR / "Reports"       / f"Broken_Link_{tag}.xlsx"
        self.path_aruba        = BASE_DIR / "Aruba Urls"    / f"Aruba{tag}.txt"

        # ── Playwright handles ────────────────────────────────────────
        self._playwright   = None
        self._browser      = None
        self._context      = None
        self._session_page = None   # single shared page for login + testing

        # ── Country-check throttle state ──────────────────────────────
        self._last_country_check_time = time.time()

    # ------------------------------------------------------------------
    # 3.2  Private utilities
    # ------------------------------------------------------------------

    def _load_docx(self, filename: str) -> list:
        """Load lines from a .docx reference file.  Missing file → [] + warn."""
        path = str(BASE_DIR / filename)
        try:
            raw = work.doc_reader(path)
            return [line.strip() for line in raw if line.strip()]
        except FileNotFoundError:
            print(f"⚠️  Reference file not found (skipping): {path}")
            return []
        except Exception as exc:
            print(f"⚠️  Could not read {path} – {exc}")
            return []

    def _ensure_output_dirs(self) -> None:
        """Create output directories if they do not already exist."""
        for path in (self.path_report, self.path_aruba):
            path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 3.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """
        Launch the Playwright browser and create a shared browser context.
        Matches the crawler pattern: browser + context here, page on demand.
        """
        self._playwright = sync_playwright().start()
        self._browser    = self._playwright.chromium.launch(headless=False)
        self._context    = self._browser.new_context()
        print(f"✅ Browser launched for {self.username}", flush=True)

    def teardown(self) -> None:
        """
        Close Playwright resources and run downstream report post-processing.

        IMPORTANT (concurrency bug fix):
        work.work_alloc_execute() reads and writes a SHARED file
        (Fixers_list.xlsx) which lives outside this account's output set.
        When MAX_PARALLEL >= 2, two processes can race on that file and
        lock each other out — on Windows this manifests as an indefinite
        hang, leaving the browsers open and blocking the runner from
        starting the next account.

        This implementation:
          1. Closes the browser FIRST so it is always released even if
             the post-processing step hangs.
          2. Serialises access to Fixers_list.xlsx with a cross-process
             lock file — only one worker at a time performs the merge.
          3. Runs the post-processing in a child process with a bounded
             timeout; if it doesn't finish within POST_PROCESS_TIMEOUT_S
             the child is terminated and we move on, so one stuck
             worker can never block the whole pipeline.
        """
        # ------------------------------------------------------------------
        # STEP 1 — release the browser UNCONDITIONALLY, before any other
        # work, so a hang later can never leave Chromium zombies behind.
        # ------------------------------------------------------------------
        for attr_name, label in (
            ("_session_page", "session page"),
            ("_context",      "browser context"),
            ("_browser",      "browser"),
        ):
            obj = getattr(self, attr_name, None)
            if obj is not None:
                try:
                    obj.close()
                except Exception:
                    pass
                setattr(self, attr_name, None)

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        print(f"🧹 Browser closed for {self.username}", flush=True)

        # ------------------------------------------------------------------
        # STEP 2 — run the shared-file post-processing under a lock and
        # with a timeout.  Never allowed to hang the whole runner.
        # ------------------------------------------------------------------
        self._run_post_processing_safely()

    def _run_post_processing_safely(self) -> None:
        """
        Call work.work_alloc_execute() in a way that is safe under
        multiprocessing.  Holds a cross-process file-based lock so only
        one worker at a time touches Fixers_list.xlsx, and runs the
        actual call in a child process with a timeout so a deadlocked
        Excel I/O can never stall the entire pipeline.
        """
        # Skip immediately if the per-account report was never written
        if not self.path_report.exists():
            return

        try:
            df = pd.read_excel(self.path_report)
        except Exception as exc:
            print(f"⚠️  Could not read {self.path_report.name} for post-processing: {exc}")
            return

        if len(df) == 0:
            return   # Nothing to allocate

        # --- Acquire a cross-process lock on Fixers_list.xlsx -------------
        lock_path = BASE_DIR / "Fixers_list.xlsx.lock"
        acquired  = _acquire_fixers_lock(lock_path, timeout_s=FIXERS_LOCK_TIMEOUT_S)

        if not acquired:
            print(f"⚠️  [{self.username}] Could not acquire Fixers_list lock after "
                  f"{FIXERS_LOCK_TIMEOUT_S}s — skipping post-processing")
            return

        try:
            print(f"🔒 [{self.username}] Running post-processing (allocating fixers)…")

            # Run in a child process so we can impose a hard timeout.
            # Spawn is cheap compared to the Excel I/O itself.
            child = Process(
                target=_run_work_alloc_execute,
                args=(
                    str(self.path_report),
                    str(BASE_DIR / "Fixers_list.xlsx"),
                    str(self.path_aruba),
                ),
                name=f"post_{self.username}",
            )
            child.start()
            child.join(timeout=POST_PROCESS_TIMEOUT_S)

            if child.is_alive():
                print(f"⚠️  [{self.username}] Post-processing timed out after "
                      f"{POST_PROCESS_TIMEOUT_S}s — terminating worker")
                child.terminate()
                child.join(timeout=5)
                if child.is_alive():
                    child.kill()
                    child.join(timeout=5)
            else:
                if child.exitcode == 0:
                    print(f"✅ [{self.username}] Post-processing complete")
                else:
                    print(f"⚠️  [{self.username}] Post-processing exited with code {child.exitcode}")

        except Exception as exc:
            print(f"⚠️  [{self.username}] Post-processing error: {exc}")
        finally:
            _release_fixers_lock(lock_path)

    def _get_session_page(self):
        """Return the long-lived session page, creating it lazily if needed."""
        if self._session_page is None:
            self._session_page = self._context.new_page()
            self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)
        return self._session_page

    # ------------------------------------------------------------------
    # 3.4  Login
    # ------------------------------------------------------------------

    def login(self) -> None:
        """Navigate to the portal, complete Okta login, set initial country."""
        page = self._get_session_page()

        page.goto(self.BASE_URL)

        try:
            page.type("#oktaEmailInput", self.username, delay=5)
            page.click("#oktaSignInBtn")
            page.fill("#password-sign-in", self.password)
            page.click("#onepass-submit-btn")
        except Exception:
            # Fallback: try the submit button alone (session may already be live)
            try:
                page.click("#onepass-submit-btn")
            except Exception:
                pass

        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40_000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except Exception:
            pass

        time.sleep(5)
        self.set_country(page)
        time.sleep(5)

    # ------------------------------------------------------------------
    # 3.5  Country / overlay management
    # ------------------------------------------------------------------

    @staticmethod
    def _country_similarity(a: str, b: str) -> float:
        """Fuzzy similarity score (0.0–1.0) for two country-name strings."""
        if not a or not b:
            return 0.0

        a = a.lower()
        b = b.lower()

        a_tokens = set(a.replace("(", " ").replace(")", " ").split())
        b_tokens = set(b.replace("(", " ").replace(")", " ").split())

        token_overlap = len(a_tokens & b_tokens)
        token_total   = max(len(a_tokens), 1)
        token_score   = token_overlap / token_total

        matches    = sum(1 for ch in a if ch in b)
        char_score = matches / max(len(a), 1)

        return (token_score * 0.6) + (char_score * 0.4)

    def set_country(self, page, *, force_recheck: bool = False) -> str:
        """
        Close overlay, ensure the portal's country is set to self.country,
        and return the previously-displayed country name.
        """
        # --- STEP 1: Dismiss notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5_000)
            if overlay and overlay.is_visible():
                print("⚠️ Notification overlay detected.")
                try:
                    page.click("#closemsg")
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                print("✅ Closed the notification overlay.")
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=10_000)
                except Exception:
                    pass
        except PlaywrightTimeoutError:
            if force_recheck:
                print("✅ No overlay appeared, continuing.")
        except Exception as exc:
            if force_recheck:
                print(f"⚠️ Overlay handling error: {exc}")

        # --- STEP 2: Click eyeball icon ---
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", timeout=30_000)
            if eyeball:
                eyeball.click()
        except Exception:
            pass

        # --- STEP 3: Read current country ---
        try:
            selector = (
                "#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet "
                "> div > div.portlet-content-container > div "
                "> div.MHMGuserdescrp > div > div.MHMGcountryname"
            )
            country_element = page.wait_for_selector(selector, timeout=20_000)
            current_country = country_element.inner_text().strip() if country_element else ""

            if force_recheck:
                print(f"🔄 Country re-check: {current_country or 'Unknown'}")
            else:
                print(f"🌍 Current Country: {current_country or 'Unknown'}")
        except Exception:
            current_country = ""
            if force_recheck:
                print("⚠️ Could not detect current country during re-check")
            else:
                print("⚠️ Could not detect current country")

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", timeout=15_000)
            if loc_btn:
                loc_btn.click()
        except Exception:
            pass

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", timeout=15_000)
        except Exception:
            pass

        # --- STEP 6: Switch country if needed ---
        try:
            if current_country.lower() == self.country.lower():
                if force_recheck:
                    print(f"✅ Country still correctly set to '{current_country}'")
                else:
                    print(f"✅ Country already set to '{current_country}'")

                try:
                    page.keyboard.press("Escape")
                except Exception:
                    pass
            else:
                if force_recheck:
                    print(f"⚠️ COUNTRY CHANGED! Resetting from '{current_country}' to '{self.country}'")

                options = page.query_selector_all("ul#MHMGBRcountries li.locationsBRlist")

                best_score  = 0.0
                best_option = None
                best_name   = ""

                for opt in options:
                    try:
                        cname = opt.get_attribute("countryname") or opt.inner_text().strip()
                    except Exception:
                        continue

                    score = self._country_similarity(self.country, cname)
                    if score > best_score:
                        best_score, best_option, best_name = score, opt, cname

                if best_score >= 0.30 and best_option is not None:
                    try:
                        best_option.click()
                    except Exception:
                        page.evaluate("(el) => el.click()", best_option)

                    print(f"🌐 Country dynamically matched → '{best_name}' (score={best_score:.2f})")

                    br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div", timeout=15_000)
                    if br_container:
                        br_container.click()
                else:
                    print(f"⚠️ No strong dynamic match for '{self.country}'. Best score={best_score:.2f}")

        except Exception:
            pass

        time.sleep(5)
        return current_country

    def _maybe_check_country(self) -> None:
        """
        Periodically re-verify the country setting hasn't drifted.

        OPTIMIZATION #4: navigate the shared page to the portal home
        BEFORE running set_country().  Previously this ran against
        whatever URL was last tested — the eyeball widget isn't
        rendered on broken/deep pages so the check often silently
        no-op'd.
        """
        current_time = time.time()

        if current_time - self._last_country_check_time < COUNTRY_CHECK_INTERVAL_SECONDS:
            return

        print(f"\n{'=' * 80}")
        print(f"🔍 Periodic Country Verification (every {COUNTRY_CHECK_INTERVAL_SECONDS}s)")
        print(f"{'=' * 80}")

        page = self._get_session_page()
        try:
            try:
                page.goto(
                    "https://partner.hpe.com/group/prp",
                    wait_until="domcontentloaded",
                    timeout=INTERNAL_NAV_TIMEOUT_MS,
                )
                page.wait_for_timeout(1_000)
            except Exception as nav_exc:
                print(f"⚠️  Could not reach portal home for country check: {nav_exc}")
                self._last_country_check_time = current_time   # avoid tight-loop retries
                print(f"{'=' * 80}\n")
                return

            self.set_country(page, force_recheck=True)
            self._last_country_check_time = current_time

        except Exception as exc:
            print(f"⚠️ Error during country verification: {exc}")
            self._last_country_check_time = current_time

        print(f"{'=' * 80}\n")

    # ------------------------------------------------------------------
    # 3.6  External link check helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _check_external_once(link: str):
        """
        Single attempt at checking an external link.
        HEAD first, fall back to GET if HEAD is rejected (405) or fails.
        Returns the urllib3 response object, or raises on complete failure.
        """
        try:
            r = http.request("HEAD", link, redirect=True)
            if r is not None and hasattr(r, "status") and r.status == 405:
                # Server doesn't allow HEAD — retry with GET
                r = http.request("GET", link)
            return r
        except Exception:
            # HEAD failed entirely — fall back to GET
            return http.request("GET", link)

    def _check_external(self, link: str):
        """
        Check an external link with one retry on transient failure.
        Returns (response_or_None, error_message_or_None).
        """
        last_exc = None

        for attempt in range(EXTERNAL_RETRY_COUNT + 1):
            try:
                resp = self._check_external_once(link)
                return resp, None
            except Exception as exc:
                last_exc = exc
                if attempt < EXTERNAL_RETRY_COUNT:
                    time.sleep(EXTERNAL_RETRY_DELAY_S)

        return None, str(last_exc) if last_exc else "unknown error"

    @staticmethod
    def _is_homepage_redirect(final_url: str) -> bool:
        """Return True if `final_url` matches any known home-page pattern."""
        try:
            split = urlsplit(final_url)
            normalized_final = f"{split.scheme}://{split.netloc}{split.path}".rstrip("/")
        except Exception:
            normalized_final = final_url.rstrip("/")

        for homepage in HOMEPAGE_PATTERNS:
            normalized_homepage = homepage.rstrip("/")
            if (
                normalized_final == normalized_homepage
                or normalized_final + "/" == normalized_homepage
            ):
                return True
        return False

    def _verify_document_via_browser(self, link: str) -> bool:
        """
        Secondary check: fetch a document URL through the full authenticated
        browser context instead of the lighter page.request.get().

        Why this exists:
            page.request.get() uses Playwright's HTTP client, which carries
            cookies but not the full browser fingerprint (referrer header,
            sec-fetch headers, user-agent quirks, etc.).  Some HPE/Aruba
            document URLs gate on those headers and return 4xx to the bare
            request client while serving HTTP 200 to a real browser hit.
            When this happens the document is actually accessible — flagging
            it broken is a false positive.

        Returns True if the browser confirms the document is reachable
        (2xx / 3xx landing, or a homepage redirect which we already treat
        as "not broken"), False if it genuinely fails.
        """
        verify_page = None
        try:
            verify_page = self._context.new_page()
            verify_page.set_default_timeout(INTERNAL_NAV_TIMEOUT_MS)

            try:
                resp = verify_page.goto(
                    link,
                    wait_until="domcontentloaded",
                    timeout=INTERNAL_NAV_TIMEOUT_MS,
                )
            except PlaywrightTimeoutError:
                # Timeout on a PDF-style response is common (browser can't
                # render the binary); page.url still reflects the landing
                resp = None

            # Allow a moment for final URL to settle
            try:
                verify_page.wait_for_timeout(300)
            except Exception:
                pass

            # Homepage redirect → not broken, treat as reachable
            final_url = verify_page.url or ""
            if self._is_homepage_redirect(final_url):
                return True

            # Status check: if the browser got a 2xx/3xx/binary response it's fine
            if resp is not None and hasattr(resp, "status"):
                status = resp.status
                # 2xx = OK; 3xx = redirect already handled above;
                # files served as attachments often come back with 200
                if status < 400:
                    return True
                # Real 4xx/5xx → broken
                return False

            # No response object but URL did land somewhere non-home → assume OK
            # (downloads often abort the navigation without a response)
            return bool(final_url) and not final_url.startswith("about:")

        except Exception:
            # On any unexpected error, fall back to the original classification
            # (i.e. don't accidentally un-break a truly broken link)
            return False
        finally:
            if verify_page is not None:
                try:
                    verify_page.close()
                except Exception:
                    pass

    # ------------------------------------------------------------------
    # 3.7  Main test loop
    # ------------------------------------------------------------------

    @log_module_metric("Broken Links")
    def test_multiple_broken(self):
        """
        Read crawled artefacts, test every link, write the Broken_Link Excel
        report.  Method name preserved for @log_module_metric compatibility.
        """

        # ==============================================================
        # INNER FUNCTION: brokencheck
        # ==============================================================
        def brokencheck():
            broken_links: list = []
            start_time = time.time()

            stats = {
                "total_links":            0,
                "internal_links":         0,
                "external_links":         0,
                "document_links":         0,
                "broken_count":           0,
                "internal_broken":        0,
                "external_broken":        0,
                "document_broken":        0,
                "excluded_links":         0,
                "skipped_download_links": 0,
            }

            print(f"\n{'#' * 80}")
            print(f"🔍 Starting Broken Link Test")
            print(f"{'#' * 80}\n")

            # ── Load input artefacts ───────────────────────────────────
            with open(self.path_page_tree, encoding="utf-8") as f:
                page_links = f.read().splitlines()

            with open(self.path_doc_links, encoding="utf-8") as f:
                doc_links = f.read().splitlines()

            all_links = page_links + doc_links
            doc_set = {x.strip() for x in doc_links if x.strip()}

            print(f"📊 Link Sources:")
            print(f"   - Page links found: {len(page_links)}")
            print(f"   - Document links found: {len(doc_links)}")
            print(f"   - Total raw links: {len(all_links)}")

            # ── Clean & dedupe in a single pass ────────────────────────
            seen: set = set()
            final_links: list = []
            for raw in all_links:
                link = raw.strip()
                if not link or link in seen:
                    continue
                if link in self._exclude_set:
                    stats["excluded_links"] += 1
                    continue
                seen.add(link)
                final_links.append(link)

            stats["total_links"] = len(final_links)

            print(f"   - Excluded links: {stats['excluded_links']}")
            print(f"   - Unique links to test: {stats['total_links']}")
            print(f"\n{'=' * 80}")
            print(f"🚀 Testing Links...")
            print(f"{'=' * 80}\n")

            page = self._get_session_page()

            # ── Main loop ──────────────────────────────────────────────
            for idx, link in enumerate(final_links, 1):
                # Periodic country verification
                self._maybe_check_country()

                # Progress indicator
                elapsed  = time.time() - start_time
                avg_time = elapsed / idx if idx > 0 else 0.0

                print(f"[{idx}/{stats['total_links']}] Testing: {link[:70]}...")
                print(f"   ⏱️  Elapsed: {elapsed:.1f}s | Avg: {avg_time:.2f}s/link | Broken: {stats['broken_count']}")

                # Skip download URLs — they trigger file downloads, not pages
                lower = link.lower()
                if "download=true" in lower or "download=1" in lower:
                    stats["skipped_download_links"] += 1
                    print(f"   ⏭️  Skipped: Download link (triggers file download)")
                    continue

                # ========================================================
                # CASE 1: DOCUMENT LINKS
                # ========================================================
                if link in doc_set:
                    stats["document_links"] += 1
                    print(f"   📄 Type: Document Link")

                    try:
                        resp = page.request.get(link, max_redirects=5)
                        status    = resp.status if resp and hasattr(resp, "status") else None
                        final_url = resp.url    if resp and hasattr(resp, "url")    else ""

                        if self._is_homepage_redirect(final_url):
                            # Expected behavior for moved/deleted documents
                            stats["skipped_download_links"] += 1
                            print(f"   ⏭️  Skipped: Redirects to homepage (document moved/deleted)")
                        elif status is not None:
                            if 200 <= status < 300:
                                print(f"   ✅ OK: HTTP {status}")
                            elif 400 <= status < 500:
                                # Some 404 pages redirect to homepage — recheck
                                if self._is_homepage_redirect(final_url):
                                    stats["skipped_download_links"] += 1
                                    print(f"   ⏭️  Skipped: 404 redirects to homepage")
                                else:
                                    # FP-reduction: Playwright's request
                                    # client sometimes gets 4xx on documents
                                    # that a real browser can fetch (missing
                                    # sec-fetch headers / referrer quirks).
                                    # Do a second check via the full browser
                                    # before marking broken.
                                    print(f"   🔎 HTTP {status} from request client; verifying via browser…")
                                    if self._verify_document_via_browser(link):
                                        print(f"   ✅ OK: browser-verified reachable (request client got {status})")
                                    else:
                                        broken_links.append(link)
                                        stats["broken_count"]    += 1
                                        stats["document_broken"] += 1
                                        print(f"   ❌ BROKEN: HTTP {status} (browser verification also failed)")
                            elif status >= 500:
                                # Transient server error — not marked broken
                                print(f"   ⚠️  Server error (not marking as broken): HTTP {status}")
                            else:
                                print(f"   ⚠️  Unexpected status: HTTP {status}")
                        else:
                            print(f"   ⚠️  No status received (network issue)")

                    except Exception as exc:
                        # Transient network errors for documents → ignore
                        print(f"   ⚠️  Skipped (transient error): {str(exc)[:50]}")

                    continue

                # ========================================================
                # CASE 2: INTERNAL PRP LINKS
                # ========================================================
                if link.startswith(self.BASE_URL):
                    stats["internal_links"] += 1
                    print(f"   🏠 Type: Internal PRP Link")

                    if is_internal_broken(page, link):
                        broken_links.append(link)
                        stats["broken_count"]    += 1
                        stats["internal_broken"] += 1
                        print(f"   ❌ BROKEN: Failed internal validation")
                    else:
                        print(f"   ✅ OK")
                    continue

                # ========================================================
                # CASE 3: EXTERNAL LINKS
                # ========================================================
                stats["external_links"] += 1
                print(f"   🌐 Type: External Link")

                resp, err = self._check_external(link)

                if resp is not None and hasattr(resp, "status"):
                    if resp.status >= 400:
                        broken_links.append(link)
                        stats["broken_count"]    += 1
                        stats["external_broken"] += 1
                        print(f"   ❌ BROKEN: HTTP {resp.status}")
                    else:
                        print(f"   ✅ OK: HTTP {resp.status}")
                else:
                    broken_links.append(link)
                    stats["broken_count"]    += 1
                    stats["external_broken"] += 1
                    print(f"   ❌ BROKEN: {(err or 'no response')[:50]}")

                print()   # Blank line between link results

            # ── Final summary ─────────────────────────────────────────
            elapsed = time.time() - start_time

            print(f"\n{'#' * 80}")
            print(f"✅ TEST COMPLETE")
            print(f"{'#' * 80}")
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
            print(f"   - Time elapsed: {elapsed:.1f}s ({elapsed / 60:.1f} minutes)")
            if stats["total_links"] > 0:
                print(f"   - Avg time per link: {elapsed / stats['total_links']:.2f}s")
                success_rate = (stats["total_links"] - stats["broken_count"]) / stats["total_links"] * 100
                print(f"   - Success rate: {success_rate:.1f}%")
            print(f"{'#' * 80}\n")

            write_excel(broken_links)

        # ==============================================================
        # INNER FUNCTION: write_excel
        # ==============================================================
        def write_excel(broken_links: list):
            print(f"📝 Writing report to Excel...")

            # Ensure output directories exist (matches crawler's _ensure_output_dirs)
            self._ensure_output_dirs()

            with open(self.path_reverse_dict, encoding="utf-8") as f:
                dictionary = ast.literal_eval(f.read())

            norm_dict = {str(k).strip(): v for k, v in dictionary.items()}

            rows = []
            issue_id = 1

            for bad in broken_links:
                parents = norm_dict.get(bad.strip(), [])

                # FP-reduction: strip homepage-variant parents.  When
                # the crawler encountered a doc link on a page that
                # redirected to home, the homepage gets recorded as a
                # parent — a useless breadcrumb for whoever fixes the
                # issue.  Prefer the most specific non-homepage parent.
                non_home_parents = [
                    p for p in parents
                    if not any(p.startswith(prefix) for prefix in HOMEPAGE_VARIANT_PREFIXES)
                    and p.rstrip("/") not in ("https://partner.hpe.com",
                                              "https://partner.hpe.com/group/prp")
                ]

                source = ""
                use_parents = non_home_parents if non_home_parents else parents

                if use_parents:
                    last  = use_parents[-1]
                    first = use_parents[0]
                    # If last parent equals the broken URL itself, use the first instead
                    source = first if last == bad and len(use_parents) > 1 else last

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
                    "-",
                ])
                issue_id += 1

            df = pd.DataFrame(rows, columns=[
                "Issue ID", "Demo Account", "Category", "Region", "Country",
                "Language", "Link", "Error Link", "Description", "Time Identified",
                "Mail ID", "Status", "Comments",
            ])

            df.to_excel(self.path_report, index=False)
            print(f"✅ Report saved: {self.path_report}")

        # Run the two inner functions
        brokencheck()


# ===========================================================================
# SECTION 4 – RUNNER
# ===========================================================================

def run_account(account):
    """
    Entry point for a single account.
    OPTIMIZATION #5: try/finally ensures teardown always runs — the
    browser is closed and the Excel report is post-processed even
    if an exception occurs mid-test.

    Every print here uses flush=True so the Windows console doesn't
    deadlock between parallel workers.
    """
    # Re-apply unbuffered stdout inside this worker process
    try:
        sys.stdout.reconfigure(line_buffering=True, write_through=True)
        sys.stderr.reconfigure(line_buffering=True, write_through=True)
    except Exception:
        pass

    prp = None
    try:
        prp = PRP(*account)
        prp.setup()
        prp.login()
        prp.test_multiple_broken()

        # NOTE: The completion-sound call (playsound) was REMOVED here.
        # playsound3 is synchronous and opens the Windows audio device;
        # when two parallel workers finish at nearly the same time, one
        # blocks waiting for the device held by the other, which
        # deadlocks run_account() right before the "Finished:" print
        # and prevents teardown() from running — the root cause of the
        # "browsers stay open, no next account starts" hang.
        #
        # If you want a completion beep, use a NON-blocking approach:
        #   import winsound
        #   winsound.Beep(1000, 200)  # frequency, duration_ms
        # or launch a detached sound process that doesn't block the worker.

        print(f"Finished: {account[0]}", flush=True)

    except Exception as exc:
        print(f"Error with {account[0]}: {exc}", flush=True)

    finally:
        if prp is not None:
            try:
                prp.teardown()
            except Exception as td_exc:
                print(f"⚠️  teardown error for {account[0]}: {td_exc}", flush=True)


# ===========================================================================
# SECTION 5 – MAIN BLOCK
# ===========================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # ACCOUNTS
    # Format: [username, password, region, country, language, account_type]
    # ------------------------------------------------------------------
    credentials = [
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy',    'Italian',            'distri'],
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Brazil',   'English',            'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany',  'German',             'T2'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'APJ',  'China',    'Simplified Chinese', 'T2'],
        # ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ',  'Indonesia','Indonesian',         'distri'],
        # ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey',   'Turkish',            'T2'],
    ]

    # ------------------------------------------------------------------
    # HOW MANY ACCOUNTS RUN IN PARALLEL
    # ------------------------------------------------------------------
    # 1  → safest; one browser at a time (~500 MB RAM)
    # 2  → good balance (~1 GB RAM)
    # 3+ → faster but each extra process needs ~500 MB RAM
    # ------------------------------------------------------------------
    MAX_PARALLEL = 2

    # ------------------------------------------------------------------
    # Process runner — matches the crawler module's main block
    # ------------------------------------------------------------------
    running:   list = []
    all_procs: list = []

    for account in credentials:
        # Wait until a slot is free
        while sum(1 for p in running if p.is_alive()) >= MAX_PARALLEL:
            time.sleep(1)

        # Prune finished processes
        running = [p for p in running if p.is_alive()]

        p = Process(
            target=run_account,
            args=(account,),
            name=account[0],
        )
        p.start()
        print(f"▶  Process started for {account[0]}  (running: {len(running) + 1} / {MAX_PARALLEL})", flush=True)
        running.append(p)
        all_procs.append(p)

    for p in all_procs:
        p.join()
        print(f"⏹  Process finished: {p.name}  (exit code: {p.exitcode})", flush=True)

    print("🎉 All accounts processed successfully", flush=True)