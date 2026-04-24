"""
HPE Partner Portal (PRP) Translation + Spelling + Empty-Page Checker
============================================================================
Reads the PageTree*.txt artefact from the crawler, visits every internal
PRP page, and runs three content-quality checks:

  1. TRANSLATION CHECK — FastText-based scan for text that appears in
     English when it should be in the account's target language.  Only
     runs for non-English / non-Singaporean accounts.  Logic lives in
     the external module `moduletranslation_phase4_better_version`
     (mtrans) and is NOT modified here — it is treated as a black box.

  2. SPELLING CHECK — SymSpell-based scan for misspelled English words.
     Runs ONLY for English / Singaporean accounts (where translation is
     not meaningful).  Logic lives in `module_spelling_phase4` (msc)
     and is NOT modified here — treated as a black box.  Translation
     and spelling are mutually exclusive per account: an account runs
     one or the other, never both.

  3. EMPTY-PAGE CHECK — flags pages whose main content consists only
     of the "Related content" placeholder, meaning the translation
     team hasn't populated content for this region/language.  Logic
     lives in `moduleemptypage` (mep) and is NOT modified here.

This module mirrors the crawler's naming conventions, attribute names,
and method structure so the project's four modules (crawler, broken-
link checker, new-tab checker, translation checker) read as a matched
set.  Business logic, output filenames, folder names, Excel column
sets, and run_account() entry point are all UNCHANGED — drop-in
replacement.

INPUT ARTEFACTS (produced by crawler, unchanged)
------------------------------------------------
  Page Trees/PageTree<tag>.txt
  Reverse Dicts/RevDict<tag>.txt

OUTPUT ARTEFACTS (unchanged)
----------------------------
  Reports/Translation_<tag>.xlsx       (non-English / non-Singaporean only)
  Reports/Spelling_<tag>.xlsx          (English / Singaporean only)
  Reports/EmptyPage_<tag>.xlsx         (all languages)
  Aruba Urls/Aruba<tag>.txt            (consumed by work.work_alloc_execute)

OPTIMIZATIONS APPLIED
---------------------
  1. integrate() uses wait_until="domcontentloaded" instead of
     "networkidle" — same win as the broken-link checker (networkidle
     rarely fires cleanly on this portal).

  2. no_content_pg() now uses the same 9-marker list as the broken-link
     checker (STRONG_BROKEN_MARKERS) and scans document.body.innerText
     rather than raw HTML.  This catches broken pages the previous 3-
     marker list missed, AND avoids false positives from markers
     embedded in <script>/<style>/hidden content.

  3. Multiprocessing runner with MAX_PARALLEL cap (matches crawler +
     broken-link checker + new-tab checker).  Replaces the no-op
     ThreadPoolExecutor(max_workers=1).

  4. run_account wraps in try/finally so teardown always runs, even if
     an exception occurs mid-test.

  5. Cross-process-safe work_alloc_execute post-processing — holds a
     file-lock on Fixers_list.xlsx and runs the actual call in a child
     process with a hard timeout, so a stuck worker can never block the
     whole pipeline.  Same pattern as the broken-link checker.

  6. All lifecycle prints use flush=True to avoid the Windows console-
     lock deadlock that occurs when two parallel workers print without
     flushing.

BUG FIXES
---------
  - no_content_pg's 3-phrase list replaced with 9-marker list (one of
    the old phrases was "We cant find..." missing an apostrophe and
    would never match real content).

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  - mtrans (translation logic): language-specific exclusion lists,
    confidence thresholds, Portuguese/Spanish fuzzing, word-count
    heuristics.  Tuned to this portal over time; do not touch.
  - mep (empty-page heuristic): precise 3-line "Related content" match.
  - 45-second sleep for delayed-loading pages — known-good workaround.
  - filter_links() exclusion patterns — account-type-specific.
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
import moduletranslation_phase4_better_version as mtrans   # translation check (black box)
import module_spelling_phase4 as msc                       # spelling check (English/Singaporean, black box)
import moduleemptypage as mep                              # empty-page check (black box)
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
# lower this without verifying on production — anchor extraction and
# content scans may miss content on slow pages if reduced.
SLOW_PAGE_SLEEP_SECONDS: int = 45

# Country-check cadence (every 2 min OR every 15 pages, whichever first)
COUNTRY_CHECK_INTERVAL_SECONDS: int = 120
COUNTRY_CHECK_EVERY_N_PAGES:    int = 15

# Post-processing (shared-file work_alloc_execute) safety limits
POST_PROCESS_TIMEOUT_S: int = 120   # kill stuck post-processing after 2 min
FIXERS_LOCK_TIMEOUT_S:  int = 300   # wait up to 5 min for the shared lock

# Shared broken-page marker list (matches broken-link checker for
# cross-module consistency).  All lowercase so matching against a
# lowercased page body works.
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
# solve it the same way as the broken-link checker: cross-process file lock
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
# SECTION 2 – EMPTY/BROKEN PAGE DETECTION
# ===========================================================================

def no_content_pg(page) -> bool:
    """
    Return True if `page` is displaying a known broken-page template.

    Uses document.body.innerText (visible text only) scanned against
    the shared STRONG_BROKEN_MARKERS list.  This replaces the old
    3-phrase hard-coded list which missed most real broken-page
    templates AND had a typo ("We cant find") that would never match
    real content.

    Fallback to page.content() (raw HTML) if innerText evaluation
    fails for any reason.
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
    Translation + Empty-Page checker for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class so the
    project's modules read as a matched set:
      - Playwright handles:  _playwright / _browser / _context / _session_page
      - Path attributes:      path_page_tree / path_translation_report / ...
      - Public methods:       setup / login / set_country / teardown / parent
      - Private helpers:      _load_docx / _country_similarity / ...

    parent() is the ONLY method whose original name is preserved —
    @log_module_metric("Translation+Spelling+Empty") identifies it by name.
    """

    BASE_URL = "https://partner.hpe.com"

    # ------------------------------------------------------------------
    # 3.1  Construction
    # ------------------------------------------------------------------

    # Translated "Related content" phrases used by the empty-page check.
    # Preserved verbatim from the original module.
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
        self._lte_translation:    list = self._load_docx("lte_translation.docx")
        self._lte_emptypage:      list = self._load_docx("lte_emptypage.docx")
        self._delayed_loading:    set  = set(self._load_docx("delayed_loading.docx"))
        self._absurd_links:       set  = set(self._load_docx("absurd_links.docx"))

        # ── Output file paths (filenames UNCHANGED) ──────────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree         = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_reverse_dict      = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"
        self.path_aruba             = BASE_DIR / "Aruba Urls"    / f"Aruba{tag}.txt"

        # NOTE: the original uses the tag pattern {r}_{c}_{l}_{a} consistently.
        # Keep exact original filenames to preserve downstream consumers.
        self.path_translation_report = BASE_DIR / "Reports" / f"Translation_{tag}.xlsx"
        self.path_spelling_report    = BASE_DIR / "Reports" / f"Spelling_{tag}.xlsx"
        self.path_emptypage_report   = BASE_DIR / "Reports" / f"EmptyPage_{tag}.xlsx"

        # ── Phrases for empty-page check ─────────────────────────────
        self.phrase         = self.TRANSLATED_PHRASES.get(language, self.DEFAULT_PHRASE)
        self.default_phrase = self.DEFAULT_PHRASE

        # ── Playwright handles ────────────────────────────────────────
        # Accept pre-built handles from the login module so we don't
        # double-launch the browser.  When provided, setup() is a no-op
        # except for the default timeout.
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
        for path in (
            self.path_translation_report,
            self.path_spelling_report,
            self.path_emptypage_report,
            self.path_aruba,
        ):
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
        for both the translation report and the empty-page report.
        Browser is closed FIRST so hangs in post-processing can't strand
        Chromium.
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

        # ── STEP 2: post-processing for each generated report ────────
        # Each call is independently locked and timeout-guarded.
        self._run_post_processing_safely(self.path_translation_report, "translation")
        self._run_post_processing_safely(self.path_spelling_report,    "spelling")
        self._run_post_processing_safely(self.path_emptypage_report,   "empty-page")

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
        original test_load_home_page() but renamed to match the crawler's
        public-method conventions.
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
        and return the previously-displayed country name.  Preserves the
        original 6-step flow exactly.
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

        OPTIMIZATION: uses wait_until="domcontentloaded" instead of
        "networkidle" — same rationale as the broken-link checker.
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

    @log_module_metric("Translation+Spelling+Empty")
    def parent(self):
        """
        Main function that runs Translation, Spelling, and Empty-Page
        checks.

        Translation vs. spelling dispatch is account-language-driven:
          - language in ("English", "Singaporean") → spelling via msc
          - any other language                     → translation via mtrans
        An account runs one or the other, never both.  Empty-page runs
        for all languages regardless.

        Method name "parent" is preserved because @log_module_metric
        identifies it by name.
        """
        # ----------------------------------------------------------------
        # INNER: write_excel — unchanged column set, unchanged behavior,
        # just wrapped in an output-dirs guarantee for safety.
        # ----------------------------------------------------------------
        def write_excel(errors, category):
            """
            Write errors to Excel.  category is one of:
              - "Translation Error"
              - "Spelling Error"
              - "Empty Page"
            """
            self._ensure_output_dirs()

            with open(self.path_reverse_dict, "r", encoding="utf-8") as f:
                dictionary = ast.literal_eval(f.read())

            # Select report path + iterator + description source
            if category == "Translation Error":
                published_report_path = self.path_translation_report
                iterator = errors.keys()
                des = [errors[err] for err in errors.keys()]
            elif category == "Spelling Error":
                published_report_path = self.path_spelling_report
                iterator = errors.keys() if isinstance(errors, dict) else errors
                des = (
                    [errors[err] for err in errors.keys()]
                    if isinstance(errors, dict)
                    else ["Spelling error"] * len(errors)
                )
            else:   # Empty Page
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

        all_links_trans = self._filter_links(list_of_links, self._lte_translation)
        all_links_empty = self._filter_links(list_of_links, self._lte_emptypage)

        translation_errors: dict = {}
        spelling_errors:    dict = {}
        empty_page_errors:  list = []
        aruba_links:        set  = set()

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

            # Broken-template / empty-content detection
            # (uses the shared STRONG_BROKEN_MARKERS list now via
            # no_content_pg() against the live page.)
            if no_content_pg(self._session_page):
                empty_page_errors.append(link)
                continue   # Skip deeper checks on known-broken pages

            # --- Dispatch to the right check(s) ---
            in_trans = link in all_links_trans
            in_empty = link in all_links_empty

            if in_trans and in_empty:
                # Translation (or spelling) AND empty-page checks.
                # Translation vs. spelling is mutually exclusive per
                # account — driven by self.language.
                if self.language not in ("English", "Singaporean"):
                    print("  → Running translation check...", flush=True)
                    err = mtrans.callable_extract(link, src, soup, self.language)
                    if err:
                        translation_errors[link] = err
                        print(f"  ✗ Found {len(err)} translation errors", flush=True)
                else:
                    print("  → Running spelling check...", flush=True)
                    gramm = msc.callable_extract(link, src, soup, self.language)
                    if gramm:
                        spelling_errors[link] = gramm
                        print(f"  ✗ Found {len(gramm)} spelling errors", flush=True)

                empty_result = mep.emptypagecheck(
                    link, self.phrase, self.default_phrase, soup, self._session_page
                )
                if empty_result:
                    empty_page_errors.append(empty_result)

            elif in_empty:
                empty_result = mep.emptypagecheck(
                    link, self.phrase, self.default_phrase, soup, self._session_page
                )
                if empty_result:
                    empty_page_errors.append(empty_result)

            elif in_trans:
                # Translation (or spelling) only, no empty-page check.
                if self.language not in ("English", "Singaporean"):
                    print("  → Running translation check...", flush=True)
                    err = mtrans.callable_extract(link, src, soup, self.language)
                    if err:
                        translation_errors[link] = err
                        print(f"  ✗ Found {len(err)} translation errors", flush=True)
                else:
                    print("  → Running spelling check...", flush=True)
                    gramm = msc.callable_extract(link, src, soup, self.language)
                    if gramm:
                        spelling_errors[link] = gramm
                        print(f"  ✗ Found {len(gramm)} spelling errors", flush=True)

            print("─" * 70, flush=True)

        # Cleanup empty-page collection
        empty_page_errors = [e for e in empty_page_errors if e != ""]

        # ----------------------------------------------------------------
        # Write reports
        # ----------------------------------------------------------------
        print("\n" + "=" * 70, flush=True)
        print("GENERATING REPORTS...", flush=True)
        print("=" * 70, flush=True)

        self._ensure_output_dirs()

        if empty_page_errors:
            print(f"Writing Empty Page report: {len(empty_page_errors)} errors", flush=True)
            write_excel(empty_page_errors, "Empty Page")

        if self.language not in ("English", "Singaporean") and translation_errors:
            print(f"Writing Translation report: {len(translation_errors)} errors", flush=True)
            write_excel(translation_errors, "Translation Error")

        if self.language in ("English", "Singaporean") and spelling_errors:
            print(f"Writing Spelling report: {len(spelling_errors)} errors", flush=True)
            write_excel(spelling_errors, "Spelling Error")

        # Save Aruba links
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
        prp_login.setUp()
        login_ok = prp_login.login()

        if not login_ok:
            print(f"DEMO ACCOUNT {account} FAILED TO LOGIN", flush=True)
            return

        # Step 2: run the translation + empty-page checks, reusing the
        # login module's browser so we don't re-authenticate.
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
                prp_login.tearDown()
            except Exception:
                pass


# ===========================================================================
# SECTION 5 – MAIN BLOCK
# ===========================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # ACCOUNTS
    # Format: [username, password, region, country, language, account_type]
    # ------------------------------------------------------------------
    credentials = [
        ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany', 'German', 'T2'],
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