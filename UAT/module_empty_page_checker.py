"""
HPE Partner Portal (PRP) Empty-Page Checker — STANDALONE OPTIMIZED BUILD
============================================================================
Reads the PageTree*.txt artefact from the crawler, visits every internal
PRP page, and runs a single content-quality check:

  EMPTY-PAGE CHECK — flags pages whose main content consists only of
  the "Related content" placeholder, meaning the translation team
  hasn't populated content for this region/language.  Logic lives in
  `moduleemptypage` (mep) and is NOT modified here — treated as a
  black box.  Uses the v2 mep which is deployment-proof and skips
  dynamic-content URLs (custom-search, article-display-page) to
  avoid the FP class reported on Apr 19.

This module is a SIBLING of `translation_checker_optimized.py` and
`spelling_checker_optimized.py`:

  - translation_checker_optimized.py:
        Translation (non-English) + empty-page (all) + spelling
        (English/Singaporean).  The one-stop runner.

  - spelling_checker_optimized.py:
        Spelling ONLY, English/Singaporean ONLY.

  - emptypage_checker_optimized.py    ← THIS FILE:
        Empty-page ONLY, ALL languages.  Use when you want an
        empty-page-only pass without the translation/spelling overhead,
        or when re-running after fixes to mep / the translated
        "Related content" phrases.

Business logic, naming conventions, output format, concurrency model,
and Playwright lifecycle all match `translation_checker_optimized.py`
byte-for-byte so the three modules read as a matched set.

INPUT ARTEFACTS (produced by crawler, unchanged)
------------------------------------------------
  Page Trees/PageTree<tag>.txt
  Reverse Dicts/RevDict<tag>.txt

OUTPUT ARTEFACTS
----------------
  Reports/EmptyPage_<tag>.xlsx         (all languages)
  Aruba Urls/Aruba<tag>.txt            (consumed by work_alloc_execute)

Deliberately NOT produced by this runner:
  Reports/Translation_<tag>.xlsx       (use translation_checker instead)
  Reports/Spelling_<tag>.xlsx          (use spelling_checker instead)

LANGUAGE SCOPE
--------------
The empty-page check runs for EVERY account in the credentials list,
regardless of language.  The mep module uses the account's translated
"Related content" phrase from the TRANSLATED_PHRASES dict — so an
Indonesian account looks for "Konten terkait", a German account
looks for "Verwandter inhalt", etc.  No language gate here.

OPTIMIZATIONS APPLIED (same set as translation_checker_optimized.py)
--------------------------------------------------------------------
  1. _integrate() uses wait_until="domcontentloaded" instead of
     "networkidle".
  2. no_content_pg() uses the shared 9-marker STRONG_BROKEN_MARKERS
     list against document.body.innerText.
  3. Multiprocessing runner with MAX_PARALLEL cap.
  4. run_account wraps teardown in try/finally.
  5. Cross-process-safe work_alloc_execute post-processing with file
     lock + hard timeout.
  6. All lifecycle prints use flush=True.

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  - mep (empty-page heuristic): v2 dynamic-URL bypass, 3-line
    heuristic for static pages.  Tuned to this portal; do not touch
    here — change it in the module itself.
  - 45-second sleep for delayed-loading pages.
  - filter_links() exclusion patterns.
  - TRANSLATED_PHRASES dict — identical to translation_checker's
    so behaviour is consistent between runners.
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import ast
import datetime
import errno
import os
import sys
import time
from multiprocessing import Process
from pathlib import Path

# ---------------------------------------------------------------------------
# CRITICAL: force unbuffered stdout so worker processes don't deadlock
# waiting for the Windows console lock.  Without this, two parallel workers
# can block each other when calling print() — last visible output becomes
# some mid-test line and nothing further.
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
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work
import moduleemptypage as mep                              # empty-page check (black box, v2)
import module_login_lang                                   # login helper
from url_utils import load_home_prefixes, is_home_redirect_playwright
from metric_report import log_module_metric


# ===========================================================================
# SECTION 1 – CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).parent

# Home-page prefixes used by is_home_redirect_playwright()
HOME_PREFIXES = load_home_prefixes(str(BASE_DIR / "config" / "home_pages.txt"))

# Default Playwright navigation timeout (milliseconds)
PAGE_TIMEOUT_MS: int = 30_000

# Per-page goto timeout
PAGE_NAV_TIMEOUT_MS: int = 30_000

# Settle after domcontentloaded for DOM updates
PAGE_SETTLE_MS: int = 400

# Delayed-loading-page sleep duration.  Kept at 45 s to exactly preserve
# the original behaviour for pages known to render very slowly.  Do NOT
# lower this without verifying on production.
SLOW_PAGE_SLEEP_SECONDS: int = 45

# Country-check cadence (every 2 min OR every 15 pages, whichever first)
COUNTRY_CHECK_INTERVAL_SECONDS: int = 120
COUNTRY_CHECK_EVERY_N_PAGES:    int = 15

# Post-processing (shared-file work_alloc_execute) safety limits
POST_PROCESS_TIMEOUT_S: int = 120   # kill stuck post-processing after 2 min
FIXERS_LOCK_TIMEOUT_S:  int = 300   # wait up to 5 min for the shared lock

# Shared broken-page marker list (matches broken-link checker + translation
# + spelling checkers for cross-module consistency).  All lowercase so
# matching against a lowercased page body works.
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


# ===========================================================================
# SECTION 1B – SHARED-FILE CONCURRENCY HELPERS
# ===========================================================================
# work.work_alloc_execute() reads and writes Fixers_list.xlsx, a SHARED file
# across all account workers.  Under MAX_PARALLEL >= 2 two processes racing
# on that file can hang indefinitely (Windows openpyxl lock issue).  We
# solve it the same way as the sibling checkers: cross-process file lock
# + run the call in a child process with a hard timeout.

def _acquire_fixers_lock(lock_path: Path, timeout_s: int) -> bool:
    """Acquire an exclusive cross-process lock by atomically creating lock_path."""
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
            time.sleep(1)
        except OSError as exc:
            if exc.errno not in (errno.EEXIST, errno.EACCES):
                print(f"⚠️  Unexpected error acquiring lock: {exc}", flush=True)
            time.sleep(1)
    return False


def _release_fixers_lock(lock_path: Path) -> None:
    """Remove the lock file.  Silent if already gone."""
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass
    except Exception as exc:
        print(f"⚠️  Could not remove lock file {lock_path}: {exc}", flush=True)


def _run_work_alloc_execute(report_path: str, fixers_path: str, aruba_path: str) -> None:
    """
    Top-level wrapper for work.work_alloc_execute — MUST be at module
    level so multiprocessing.Process can pickle it on Windows.
    """
    try:
        work.work_alloc_execute(report_path, fixers_path, aruba_path)
    except Exception as exc:
        print(f"⚠️  work_alloc_execute failed: {exc}", flush=True)
        raise


# ===========================================================================
# SECTION 2 – EMPTY/BROKEN PAGE DETECTION (orchestrator-level)
# ===========================================================================

def no_content_pg(page) -> bool:
    """
    Return True if `page` is displaying a known broken-page template.

    Used to skip deeper checks on pages that are already known-bad —
    there's no value in running the empty-page check on a 404 template.
    (Note: mep.emptypagecheck handles its own dynamic-URL bypass for
    search and article pages; this is the separate broken-template
    guard.)

    Uses document.body.innerText (visible text only) scanned against
    the shared STRONG_BROKEN_MARKERS list.  Fallback to page.content()
    (raw HTML) if innerText evaluation fails.
    """
    try:
        body = page.evaluate("() => document.body ? document.body.innerText : ''")
        if body:
            body = body.lower()
        else:
            body = ""
    except Exception:
        try:
            body = page.content().lower()
        except Exception:
            return False   # Can't inspect — assume not broken

    for marker in STRONG_BROKEN_MARKERS:
        if marker in body:
            return True
    return False


# ===========================================================================
# SECTION 3 – MAIN CLASS
# ===========================================================================

class PRP:
    """
    Empty-page-only checker for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class + the
    translation_checker_optimized.PRP class + the
    spelling_checker_optimized.PRP class so the project's modules
    read as a matched set.

    parent() is the ONLY method whose original name is preserved —
    @log_module_metric("EmptyPage") identifies it by name.
    """

    BASE_URL = "https://partner.hpe.com"

    # ------------------------------------------------------------------
    # 3.1  Construction
    # ------------------------------------------------------------------

    # Translated "Related content" phrases used by mep.emptypagecheck.
    # Preserved verbatim from translation_checker_optimized.py so the
    # two modules interpret the same account identically.
    TRANSLATED_PHRASES = {
        "French":              "Contenu associé",
        "German":              "Verwandter inhalt",
        "Italian":             "Contenuti correlati",
        "Chinese":             "相关内容",
        "Chinese-Simplified":  "相关内容",
        "Russian":             "Сопутствующая информация",
        "Portugese":           "Conteúdo relacionado",
        "Portuguese-Brazil":   "Conteúdo relacionado",
        "Indonesian":          "Konten terkait",
        "Singaporean":         "Related content",
        "Korean":              "관련 콘텐츠",
        "Turkish":             "İlgili içerik",
        "Japanese":            "関連コンテンツ",
        "Taiwan":              "相關內容",
        "Spanish":             "Contenido relacionado",
        "LARSpanish":          "Contenido relacionado",
        "English":             "Related content",
    }

    DEFAULT_PHRASE = "Related content"

    def __init__(
        self,
        username:     str,
        password:     str,
        region:       str,
        country:      str,
        language:     str,
        account_type: str,
        playwright=None,
        browser=None,
        page=None,
    ) -> None:
        # ── Credentials & locale ─────────────────────────────────────
        self.username     = username
        self.password     = password
        self.region       = "NAR" if region == "NA" else region
        self.country      = country
        self.language     = language
        self.account_type = account_type

        # ── Reference lists loaded from .docx files ───────────────────
        #
        # lte_emptypage.docx — empty-page-specific exclusion list.
        # delayed_loading.docx — still needed by _integrate() for
        # known-slow pages.
        #
        # lte_translation.docx and absurd_links.docx are NOT loaded
        # because no translation check runs here.
        self._lte_emptypage:   list = self._load_docx("lte_emptypage.docx")
        self._delayed_loading: set  = set(self._load_docx("delayed_loading.docx"))

        # ── Output file paths ────────────────────────────────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree        = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_reverse_dict     = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"
        self.path_aruba            = BASE_DIR / "Aruba Urls"    / f"Aruba{tag}.txt"
        self.path_emptypage_report = BASE_DIR / "Reports"       / f"EmptyPage_{tag}.xlsx"

        # ── Phrases for empty-page check ─────────────────────────────
        self.phrase         = self.TRANSLATED_PHRASES.get(language, self.DEFAULT_PHRASE)
        self.default_phrase = self.DEFAULT_PHRASE

        # ── Playwright handles ────────────────────────────────────────
        # Accept pre-built handles from the login module so we don't
        # double-launch the browser.
        self._playwright   = playwright
        self._browser      = browser
        self._context      = None
        self._session_page = page

        # ── Country-check throttle state ──────────────────────────────
        self._last_country_check_time   = time.time()
        self._pages_since_country_check = 0

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
            print(f"⚠️  Reference file not found (skipping): {path}", flush=True)
            return []
        except Exception as exc:
            print(f"⚠️  Could not read {path} – {exc}", flush=True)
            return []

    def _ensure_output_dirs(self) -> None:
        """Create output directories if they do not already exist."""
        for path in (self.path_emptypage_report, self.path_aruba):
            path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 3.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """
        Launch Playwright if not already supplied by an upstream caller.
        When the login module passes in pre-built handles, this is a
        no-op apart from setting the default timeout.
        """
        if self._playwright is None or self._browser is None or self._session_page is None:
            self._playwright   = sync_playwright().start()
            self._browser      = self._playwright.chromium.launch(headless=False)
            self._context      = self._browser.new_context()
            self._session_page = self._browser.new_page()
            print(f"✅ Browser launched for {self.username}", flush=True)
        if self._session_page is not None:
            self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)

    def teardown(self) -> None:
        """
        Close Playwright resources, then run shared-file post-processing
        for the empty-page report.  Browser is closed FIRST so hangs in
        post-processing can't strand Chromium.
        """
        # ── STEP 1: release the browser unconditionally ──────────────
        for attr_name in ("_session_page", "_context", "_browser"):
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

        # ── STEP 2: post-processing for the empty-page report ────────
        self._run_post_processing_safely(self.path_emptypage_report, "empty-page")

    def _run_post_processing_safely(self, report_path: Path, label: str) -> None:
        """
        Call work.work_alloc_execute() safely under multiprocessing.
        Holds a cross-process lock on Fixers_list.xlsx and runs the
        actual call in a child process with a hard timeout so a
        deadlocked Excel I/O can never stall the entire pipeline.
        """
        if not report_path.exists():
            return

        try:
            df = pd.read_excel(report_path)
        except Exception as exc:
            print(f"⚠️  Could not read {report_path.name} for post-processing: {exc}", flush=True)
            return

        if len(df) == 0:
            return

        lock_path = BASE_DIR / "Fixers_list.xlsx.lock"
        acquired  = _acquire_fixers_lock(lock_path, timeout_s=FIXERS_LOCK_TIMEOUT_S)

        if not acquired:
            print(f"⚠️  [{self.username}] Could not acquire Fixers_list lock for {label} "
                  f"after {FIXERS_LOCK_TIMEOUT_S}s — skipping post-processing", flush=True)
            return

        try:
            print(f"🔒 [{self.username}] Running {label} post-processing (allocating fixers)…",
                  flush=True)

            child = Process(
                target=_run_work_alloc_execute,
                args=(
                    str(report_path),
                    str(BASE_DIR / "Fixers_list.xlsx"),
                    str(self.path_aruba),
                ),
                name=f"post_{label}_{self.username}",
            )
            child.start()
            child.join(timeout=POST_PROCESS_TIMEOUT_S)

            if child.is_alive():
                print(f"⚠️  [{self.username}] {label} post-processing timed out after "
                      f"{POST_PROCESS_TIMEOUT_S}s — terminating", flush=True)
                child.terminate()
                child.join(timeout=5)
                if child.is_alive():
                    child.kill()
                    child.join(timeout=5)
            else:
                if child.exitcode == 0:
                    print(f"✅ [{self.username}] {label} post-processing complete", flush=True)
                else:
                    print(f"⚠️  [{self.username}] {label} post-processing exited with code "
                          f"{child.exitcode}", flush=True)

        except Exception as exc:
            print(f"⚠️  [{self.username}] {label} post-processing error: {exc}", flush=True)
        finally:
            _release_fixers_lock(lock_path)

    # ------------------------------------------------------------------
    # 3.4  Login
    # ------------------------------------------------------------------

    def login(self) -> None:
        """
        Navigate to the portal and complete the Okta login.  Mirrors the
        translation checker's login() verbatim.
        """
        page = self._session_page
        page.goto(self.BASE_URL)

        try:
            page.type("#oktaEmailInput", self.username, delay=5)
            page.click("#oktaSignInBtn")
            page.fill("#password-sign-in", self.password)
            page.click("#onepass-submit-btn")
        except Exception:
            try:
                page.click("#onepass-submit-btn")
            except Exception:
                pass

        try:
            page.wait_for_selector('//*[@id="form19"]/div[2]/div[2]/div[2]/a', timeout=40_000)
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except PlaywrightTimeoutError:
            print("Login redirect click failed", flush=True)
        except Exception:
            pass

        time.sleep(5)
        page.goto(self.BASE_URL)

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

    def set_country(self, page=None, *, force_recheck: bool = False) -> str:
        """
        Close overlay, ensure the portal's country is set to self.country,
        and return the previously-displayed country name.  Mirrors the
        translation checker's set_country() exactly — 6-step flow
        preserved.
        """
        if page is None:
            page = self._session_page

        # --- STEP 1: Dismiss notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=10_000)
            if overlay and overlay.is_visible():
                if force_recheck:
                    print("🔔 Notification overlay detected (re-check).", flush=True)
                else:
                    print("⚠️ Notification overlay detected.", flush=True)
                try:
                    close_btn = page.locator("#closemsg")
                    close_btn.wait_for(state="visible", timeout=5_000)
                    close_btn.click()
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                print("✅ Closed the notification overlay.", flush=True)
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=15_000)
                except Exception:
                    pass
        except PlaywrightTimeoutError:
            if not force_recheck:
                print("✅ No overlay appeared, continuing.", flush=True)
        except Exception as exc:
            if not force_recheck:
                print(f"⚠️ Overlay handling error: {exc}", flush=True)

        # --- STEP 2: Click eyeball icon ---
        eyeball = None
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", state="visible", timeout=30_000)
            if eyeball:
                eyeball.click()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=10_000)
                except Exception:
                    pass
                time.sleep(2)
        except Exception as exc:
            if not force_recheck:
                print(f"⚠️ Eyeball icon error: {exc}", flush=True)

        # --- STEP 3: Read current country ---
        try:
            selector = (
                "#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet "
                "> div > div.portlet-content-container > div "
                "> div.MHMGuserdescrp > div > div.MHMGcountryname"
            )
            country_element = page.wait_for_selector(selector, state="visible", timeout=20_000)
            current_country = country_element.inner_text().strip() if country_element else ""
            if force_recheck:
                print(f"🔄 Country re-check: {current_country or 'Unknown'}", flush=True)
            else:
                print(f"🌍 Current Country: {current_country or 'Unknown'}", flush=True)
        except Exception as exc:
            current_country = ""
            if not force_recheck:
                print(f"⚠️ Could not detect current country: {exc}", flush=True)

        # --- STEP 4a: Early exit if already correct ---
        if current_country.lower() == self.country.lower():
            if force_recheck:
                print(f"✅ Country still correctly set to '{current_country}'", flush=True)
            else:
                print(f"✅ Country already set to '{current_country}'", flush=True)
            try:
                page.keyboard.press("Escape")
            except Exception:
                try:
                    if eyeball:
                        eyeball.click()
                        time.sleep(1)
                except Exception:
                    try:
                        page.click("body")
                        time.sleep(1)
                    except Exception:
                        pass
            return current_country

        # --- Country needs to change ---
        if force_recheck:
            print(f"⚠️ COUNTRY CHANGED! Resetting from '{current_country}' to '{self.country}'",
                  flush=True)

        # --- STEP 4b: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty",
                                             state="visible", timeout=15_000)
            if loc_btn:
                loc_btn.click()
                time.sleep(1)
        except Exception as exc:
            if not force_recheck:
                print(f"⚠️ Country dropdown error: {exc}", flush=True)

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist",
                                   state="visible", timeout=20_000)
        except Exception as exc:
            if not force_recheck:
                print(f"⚠️ Country list not loaded: {exc}", flush=True)

        # --- STEP 6: Switch country ---
        try:
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

                print(f"🌐 Country dynamically matched → '{best_name}' (score={best_score:.2f})",
                      flush=True)

                time.sleep(2)
                br_container = page.wait_for_selector("#MHMGBRLIst > li > div > div",
                                                      state="visible", timeout=15_000)
                if br_container:
                    br_container.click()
                    print("⏳ Waiting for country change to complete...", flush=True)
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=30_000)
                        page.wait_for_load_state("networkidle", timeout=90_000)
                    except Exception as exc:
                        print(f"⚠️ Country change load warning: {exc}", flush=True)
                    time.sleep(5)
                    print("✅ Country change completed", flush=True)
            else:
                print(f"⚠️ No strong dynamic match for '{self.country}'. "
                      f"Best score={best_score:.2f}", flush=True)

        except Exception as exc:
            if not force_recheck:
                print(f"⚠️ Country switching error: {exc}", flush=True)

        return current_country

    def _maybe_check_country(self) -> None:
        """
        Periodically re-verify the country setting hasn't drifted.
        Triggers on EITHER time elapsed (120 s) OR pages checked (15),
        whichever threshold is reached first.
        """
        current_time = time.time()

        time_ok  = (current_time - self._last_country_check_time) >= COUNTRY_CHECK_INTERVAL_SECONDS
        pages_ok = self._pages_since_country_check >= COUNTRY_CHECK_EVERY_N_PAGES

        if not (time_ok or pages_ok):
            return

        print(f"\n{'=' * 80}", flush=True)
        print(f"🔍 Periodic Country Verification", flush=True)
        print(f"   Time since last check: {current_time - self._last_country_check_time:.1f}s",
              flush=True)
        print(f"   Pages since last check: {self._pages_since_country_check}", flush=True)
        print(f"{'=' * 80}", flush=True)

        try:
            if self._session_page is None:
                print("⚠️ Page not available for country check", flush=True)
                self._last_country_check_time   = current_time
                self._pages_since_country_check = 0
                print(f"{'=' * 80}\n", flush=True)
                return

            current_url = self._session_page.url or ""

            # If somehow we're on an external URL, go back to PRP home first
            if not current_url.startswith("https://partner.hpe.com"):
                print(f"⚠️ Page on external URL: {current_url[:50]}...", flush=True)
                print(f"   Navigating back to PRP home", flush=True)
                try:
                    self._session_page.goto(
                        self.BASE_URL + "/group/prp/home",
                        wait_until="domcontentloaded",
                        timeout=PAGE_NAV_TIMEOUT_MS,
                    )
                    time.sleep(3)
                except Exception as nav_exc:
                    print(f"⚠️  Could not reach portal home: {nav_exc}", flush=True)
                    self._last_country_check_time   = current_time
                    self._pages_since_country_check = 0
                    print(f"{'=' * 80}\n", flush=True)
                    return

            self.set_country(self._session_page, force_recheck=True)

            self._last_country_check_time   = current_time
            self._pages_since_country_check = 0

        except Exception as exc:
            print(f"⚠️ Error during country verification: {exc}", flush=True)
            self._last_country_check_time   = current_time
            self._pages_since_country_check = 0

        print(f"{'=' * 80}\n", flush=True)

    # ------------------------------------------------------------------
    # 3.6  Page-loading helpers
    # ------------------------------------------------------------------

    def _integrate(self, site: str):
        """
        Navigate to `site` and return (html_source, soup) for content-level
        checks.  Returns (None, None) if the page redirected to the home
        variants or failed to load.
        """
        page = self._session_page

        try:
            page.goto(
                site,
                wait_until="domcontentloaded",
                timeout=PAGE_NAV_TIMEOUT_MS,
            )
        except PlaywrightTimeoutError:
            pass
        except Exception:
            return None, None

        # Slow-loading pages need extra time (45s preserved exactly)
        if site in self._delayed_loading or site.strip() in self._delayed_loading:
            print(f"SLEEPING: {site}", flush=True)
            try:
                self.set_country(self._session_page)
            except Exception:
                pass
            time.sleep(SLOW_PAGE_SLEEP_SECONDS)
        else:
            try:
                page.wait_for_timeout(PAGE_SETTLE_MS)
            except Exception:
                pass

        # Homepage-redirect guard
        final_url = (page.url or "").split("#")[0].rstrip("/")
        for p in HOME_PREFIXES:
            if final_url == p:
                return None, None

        try:
            src = page.content()
        except Exception:
            return None, None

        soup = BeautifulSoup(src, "html.parser")
        return src, soup

    @staticmethod
    def _page_has_aruba_tag(soup) -> bool:
        """Return True if the page has an Aruba-category tag."""
        return bool(soup.find_all("span", class_="arubaTag"))

    def _filter_links(self, list_of_links: list, links_not_to_be_checked: list) -> list:
        """Preserve the original exclusion logic exactly."""
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

        return list(set(list_of_links) - set(actual_excluded_links))

    # ------------------------------------------------------------------
    # 3.7  Main test loop
    # ------------------------------------------------------------------

    @log_module_metric("EmptyPage")
    def parent(self):
        """
        Main function that runs the Empty-Page check only.

        Runs for all languages — the mep module uses the account's
        translated "Related content" phrase, so every language is
        meaningfully checkable.

        Method name "parent" is preserved because @log_module_metric
        identifies it by name.
        """
        # ----------------------------------------------------------------
        # INNER: write_excel — identical column set to translation_checker
        # so both reports can be consumed by the same downstream tooling.
        # ----------------------------------------------------------------
        def write_excel(errors, category):
            """
            Write empty-page errors to Excel.  `category` is always
            "Empty Page" for this module, but we keep the parameter
            so the signature matches translation_checker's write_excel.
            """
            self._ensure_output_dirs()

            with open(self.path_reverse_dict, "r", encoding="utf-8") as f:
                dictionary = ast.literal_eval(f.read())

            published_report_path = self.path_emptypage_report
            iterator = errors
            des = ["Empty page"] * len(errors)

            issue_id = 1
            account  = self.username
            region   = self.region
            country  = self.country
            language = self.language
            fixer_mail = ""
            status     = "New"
            comments   = "-"
            report = []
            i = 0

            for ele in iterator:
                if ele == "https://partner.hpe.com/group/prp/internal":
                    continue

                linkele = [
                    issue_id, account, category, region, country, language,
                ]

                # Parent-link lookup with three fallback spellings
                # (preserved from original behavior).
                if ele in dictionary:
                    parents = dictionary[ele]
                elif ele.strip() in dictionary:
                    parents = dictionary[ele.strip()]
                elif ele + "\n" in dictionary:
                    parents = dictionary[ele + "\n"]
                else:
                    parents = []

                if not parents:
                    linkele.append(ele)
                else:
                    s_url  = parents[-1]
                    s_url2 = parents[0]
                    linkele.append(s_url2 if s_url == ele else s_url)

                linkele.append(ele)
                linkele.append(des[i] if i < len(des) else "")
                linkele.append(datetime.datetime.now())
                linkele.append(fixer_mail)
                linkele.append(status)
                linkele.append(comments)
                report.append(linkele)
                issue_id += 1
                i += 1

            r = pd.DataFrame(report, columns=[
                "Issue ID", "Demo Account", "Category", "Region", "Country", "Language",
                "Link", "Error Link", "Description", "Time Identified",
                "Mail ID", "Status", "Comments",
            ])
            r.to_excel(published_report_path)

        # ----------------------------------------------------------------
        # Load page tree and apply filters
        # ----------------------------------------------------------------
        with open(self.path_page_tree, "r", encoding="utf-8") as f:
            list_of_links = f.read().splitlines()

        all_links_empty = self._filter_links(list_of_links, self._lte_emptypage)

        empty_page_errors: list = []
        aruba_links:       set  = set()

        # ----------------------------------------------------------------
        # Per-page loop
        # ----------------------------------------------------------------
        for link in list_of_links:
            self._maybe_check_country()

            print(f"\nProcessing: {link}", flush=True)

            src, soup = self._integrate(link)
            self._pages_since_country_check += 1

            if src is None:
                # Redirected to home or load failed — skip
                continue

            # Aruba-tag detection for downstream work allocation
            if self._page_has_aruba_tag(soup):
                if link not in (
                    "https://partner.hpe.com",
                    "https://partner.hpe.com/group/prp",
                    "https://partner.hpe.com/group/prp/home",
                ):
                    aruba_links.add(link)

            # Broken-template detection — skip deeper checks if broken
            if no_content_pg(self._session_page):
                empty_page_errors.append(link)
                continue

            # Only check pages that passed the empty-page exclusion filter
            if link not in all_links_empty:
                continue

            # Run the empty-page check.  mep v2 is dynamic-URL-aware:
            # /custom-search and /article-display-page URLs are
            # auto-skipped with a diagnostic log line, so no FPs from
            # those patterns.
            empty_result = mep.emptypagecheck(
                link, self.phrase, self.default_phrase, soup, self._session_page
            )
            if empty_result:
                empty_page_errors.append(empty_result)
                print(f"  ✗ Flagged as empty", flush=True)

            print("─" * 70, flush=True)

        # Cleanup empty-page collection (strip any empty strings)
        empty_page_errors = [e for e in empty_page_errors if e != ""]

        # ----------------------------------------------------------------
        # Write report
        # ----------------------------------------------------------------
        print("\n" + "=" * 70, flush=True)
        print("GENERATING REPORT...", flush=True)
        print("=" * 70, flush=True)

        self._ensure_output_dirs()

        if empty_page_errors:
            print(f"Writing Empty Page report: {len(empty_page_errors)} errors", flush=True)
            write_excel(empty_page_errors, "Empty Page")
        else:
            print("No empty pages found — no report generated", flush=True)

        # Save Aruba links (consumed by work_alloc_execute post-processing)
        with open(self.path_aruba, "w", encoding="utf-8") as filehandle:
            for listitem in aruba_links:
                filehandle.write(f"{listitem}\n")

        print("\nAll reports generated successfully!", flush=True)


# ===========================================================================
# SECTION 4 – RUNNER
# ===========================================================================

def run_account(account):
    """
    Entry point for a single account.  Always wraps teardown in
    try/finally so browsers are never stranded.  Flushes all prints to
    avoid the Windows console-lock deadlock under MAX_PARALLEL >= 2.

    No language gate here — empty-page check runs for every language.
    """
    # Re-apply unbuffered stdout inside each worker process
    try:
        sys.stdout.reconfigure(line_buffering=True, write_through=True)
        sys.stderr.reconfigure(line_buffering=True, write_through=True)
    except Exception:
        pass

    prp_login = None
    prp_main  = None

    try:
        # Step 1: login via the shared login helper
        prp_login = module_login_lang.PRP(*account)
        prp_login.setup()
        login_ok = prp_login.login()

        if not login_ok:
            print(f"DEMO ACCOUNT {account} FAILED TO LOGIN", flush=True)
            return

        # Step 2: run the empty-page check, reusing the login module's
        # browser so we don't re-authenticate.
        prp_main = PRP(
            *account,
            playwright=prp_login.playwright,
            browser=prp_login.browser,
            page=prp_login.page,
        )
        prp_main.setup()
        prp_main.parent()

        print(f"Finished: {account[0]}", flush=True)

    except Exception as exc:
        print(f"Error with {account[0]}: {exc}", flush=True)

    finally:
        # Tear down main first (it owns the post-processing), then login
        if prp_main is not None:
            try:
                prp_main.teardown()
            except Exception as td_exc:
                print(f"⚠️  teardown error for {account[0]}: {td_exc}", flush=True)
        if prp_login is not None:
            try:
                prp_login.teardown()
            except Exception:
                pass


# ===========================================================================
# SECTION 5 – MAIN BLOCK
# ===========================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # ACCOUNTS
    # Format: [username, password, region, country, language, account_type]
    #
    # Empty-page check runs for ALL languages — no pre-filtering needed.
    # The credentials list below mirrors translation_checker's so the
    # two runners process the same account matrix.
    # ------------------------------------------------------------------
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ',  'South Korea', 'Korean',             'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'APJ',  'China',       'Simplified Chinese', 'T2'],
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ',  'China',       'Simplified Chinese', 'distri'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'APJ',  'Japan',       'Japanese',           'T2'],
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'APJ',  'Japan',       'Japanese',           'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy',       'Italian',            'T2'],
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy',       'Italian',            'distri'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'AMS',  'Brazil',      'Portuguese',         'T2'],
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'AMS',  'Brazil',      'Portuguese',         'distri'],
        ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ',  'Taiwan',      'Taiwan',             'distri'],
        ['mhmg_albert_dist2@yopmail.com', 'Login2Bot!', 'APJ',  'Indonesia',   'Indonesian',         'distri'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'APJ',  'Indonesia',   'Indonesian',         'T2'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'France',      'French',             'T2'],
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany',     'German',             'T2'],
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Turkey',      'Turkish',            'T2'],
    ]

    # ------------------------------------------------------------------
    # HOW MANY ACCOUNTS RUN IN PARALLEL
    # ------------------------------------------------------------------
    # 1  → safest; one browser at a time (~500 MB RAM)
    # 2  → good balance (~1 GB RAM)
    # 3+ → faster but each extra process needs ~500 MB RAM
    # ------------------------------------------------------------------
    MAX_PARALLEL = 2

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
        print(f"▶  Process started for {account[0]}  (running: {len(running) + 1} / {MAX_PARALLEL})",
              flush=True)
        running.append(p)
        all_procs.append(p)

    for p in all_procs:
        p.join()
        print(f"⏹  Process finished: {p.name}  (exit code: {p.exitcode})", flush=True)

    print("🎉 All accounts processed successfully", flush=True)