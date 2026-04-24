"""
HPE Partner Portal (PRP) New-Tab Checker — OPTIMIZED BUILD
============================================================
Reads the PageTree*.txt artefact from the crawler, visits every
internal PRP page, and verifies that external links on those pages
open in a new tab (target="_blank" / window.open / etc.).  Links
that incorrectly open in the same tab are written to a New_Tab
Excel report.

This module mirrors the crawler's naming conventions, attribute
names, and method structure so the three modules (crawler,
broken-link checker, new-tab checker) read as a matched set.
Business logic, output filenames, folder names, Excel column set,
and run_account() entry point are all UNCHANGED — drop-in
replacement.

INPUT ARTEFACTS (produced by crawler, unchanged)
------------------------------------------------
  Page Trees/PageTree<tag>.txt

OUTPUT ARTEFACTS (unchanged)
----------------------------
  Reports/New_Tab_<tag>.xlsx
  Aruba Urls/Aruba<tag>.txt          (via work.work_alloc_execute)

OPTIMIZATIONS APPLIED
---------------------
  1. Single page.evaluate() collects every anchor's href, target,
     onclick, visibility, footer-membership, and JS-behavior flag in
     ONE IPC round-trip per page.  Previously each anchor triggered
     ~6 separate CDP calls — on a 200-anchor page that's 1,200 round
     trips compressed into 1.

  2. page.goto() uses wait_until="domcontentloaded" instead of
     Playwright's default "load".  The check only reads HTML
     attributes (no rendering needed), so waiting for images / iframes
     / external scripts to fully load wastes seconds per page.

  3. run_account() wraps in try/finally so teardown always runs,
     even if an exception occurs mid-test.  Previously a failure mid
     way through could leave an orphaned Chromium process running.

  4. Multiprocessing runner (matches crawler + broken-link checker).
     Replaces the no-op ThreadPoolExecutor(max_workers=1) pattern.

  5. Per-page footer-skip counter (the old code's counter was
     cumulative but logged as if per-page, which was misleading).

BUG FIXES
---------
  - check_link_opens_new_tab()'s broad except-clause no longer
    reports "same tab" on errors — it now returns a special sentinel
    so DOM hiccups don't become false bug reports.
  - Dead threading.Lock() removed (nothing was locking on it).
  - Unused self.tree_dict_path attribute removed (leftover from
    another module; never used here).

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  - The 25-second sleep for slow-loading / absurd pages is kept
    exactly as-is.  It's a known-good workaround; replacing it
    could cause this module to miss anchors on slow-rendering
    pages.
  - Footer-detection DOM traversal logic is kept bit-for-bit
    identical (inside the bulk collection script now).
  - The @log_module_metric("New Tab") decorated method is still
    called test_new_tab().
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import datetime
import time
from multiprocessing import Process
from pathlib import Path
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
import pandas as pd
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work
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

# goto timeout for each page-tree URL
PAGE_NAV_TIMEOUT_MS: int = 30_000

# Short settle after domcontentloaded for DOM to stabilise
PAGE_SETTLE_MS: int = 300

# Sleep duration for pages listed as slow-loading or "absurd" (DO NOT CHANGE
# without verifying on production — anchor extraction may miss links on slow
# pages if this is reduced).
SLOW_PAGE_SLEEP_SECONDS: int = 25

# Country-check cadence (every 2 minutes OR every 10 pages, whichever first)
COUNTRY_CHECK_INTERVAL_SECONDS: int = 120
COUNTRY_CHECK_EVERY_N_PAGES:    int = 10


# ===========================================================================
# SECTION 2 – BULK ANCHOR COLLECTION SCRIPT
# ===========================================================================
# This single JavaScript function replaces six separate CDP round-trips
# per anchor with one round-trip for the whole page.  For each <a> with
# a usable href it returns a small dict with all the information we need
# to decide "does this link open in a new tab?".
#
# Fields per entry:
#   href        – raw href attribute value
#   target      – value of target attribute (null if absent)
#   onclick_raw – value of onclick attribute (null if absent)
#   visible     – true if CSS-rendered (display/visibility-based check
#                 matches the original is_element_visible semantics)
#   in_footer   – true if this <a> is inside a <footer>, #footer, or
#                 any ancestor with a class matching /footer/i
#   has_js_new_tab – true if onclick property (the JS one, not attribute)
#                    stringifies to include window.open
# ---------------------------------------------------------------------------
_JS_COLLECT_ANCHORS = r"""
() => {
  const out = [];
  const anchors = document.querySelectorAll('a');
  for (const el of anchors) {
    const href = el.getAttribute('href');
    if (!href) continue;

    // CSS visibility (permissive — matches is_element_visible())
    const style = window.getComputedStyle(el);
    const visible = !(style.display === 'none' || style.visibility === 'hidden');

    // Footer-ancestor check
    let in_footer = false;
    let cur = el;
    while (cur) {
      if (cur.tagName === 'FOOTER' || cur.id === 'footer') {
        in_footer = true;
        break;
      }
      if (cur.className && typeof cur.className === 'string') {
        const cn = cur.className;
        if (cn.includes('footer') || cn.includes('Footer')) {
          in_footer = true;
          break;
        }
      }
      cur = cur.parentElement;
    }

    // JS-property onclick (catches programmatically-attached handlers)
    let has_js_new_tab = false;
    try {
      const oc = el.onclick;
      if (oc && oc.toString().includes('window.open')) {
        has_js_new_tab = true;
      }
    } catch (e) { /* ignore */ }

    out.push({
      href:           href,
      target:         el.getAttribute('target'),
      onclick_raw:    el.getAttribute('onclick'),
      visible:        visible,
      in_footer:      in_footer,
      has_js_new_tab: has_js_new_tab,
    });
  }
  return out;
}
"""


# ===========================================================================
# SECTION 3 – PURE HELPER FUNCTIONS
# ===========================================================================

def classify_anchor_tab_behavior(anchor_data: dict):
    """
    Decide whether an anchor opens in a new tab, based on the pre-collected
    data from _JS_COLLECT_ANCHORS.

    Returns (opens_new_tab: bool | None, reason: str).
    A None opens_new_tab value means "indeterminate" — caller should skip.

    Preserves the original classification order from
    check_link_opens_new_tab():
      1. target in {_blank, _new, blank}   → new tab
      2. onclick attribute contains window.open → new tab
      3. JS onclick property contains window.open → new tab
      4. target in {_self, _parent, _top}  → same tab
      5. no target attribute               → same tab (default)
    """
    target = (anchor_data.get("target") or "").lower()

    # 1. Explicit new-tab targets
    if target in {"_blank", "_new", "blank"}:
        return True, f"Has target='{target}'"

    # 2. onclick attribute with window.open
    onclick_raw = anchor_data.get("onclick_raw") or ""
    if "window.open" in onclick_raw:
        return True, "Has onclick with window.open()"

    # 3. JS onclick property with window.open (programmatic handlers)
    if anchor_data.get("has_js_new_tab"):
        return True, "Has JavaScript behavior for new tab"

    # 4. Same-window targets
    if target in {"_self", "_parent", "_top"}:
        return False, f"Has target='{target}' (same window)"

    # 5. No target → default same-tab
    return False, "No target attribute (default same-tab behavior)"


# ===========================================================================
# SECTION 4 – MAIN CLASS
# ===========================================================================

class PRP:
    """
    Authenticated new-tab checker for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class so the
    three modules read as a matched set:
      - Playwright handles:  _playwright / _browser / _context / _session_page
      - Path attributes:      path_page_tree / path_report / path_aruba
      - Public methods:       setup / login / set_country / teardown
      - Private helpers:      _load_docx / _country_similarity / ...
    """

    BASE_URL = "https://partner.hpe.com"

    # ------------------------------------------------------------------
    # 4.1  Construction
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
        # Moved out of class body (matches crawler pattern).
        delayed_list = self._load_docx("delayed_loading.docx")
        absurd_list  = self._load_docx("absurd_links.docx")

        # Pre-convert to sets for O(1) "is this URL slow?" checks
        self._delayed_loading_links: set = set(delayed_list)
        self._absurd_links:          set = set(absurd_list)

        # ── Output file paths (filenames UNCHANGED) ──────────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree = BASE_DIR / "Page Trees" / f"PageTree{tag}.txt"
        self.path_report    = BASE_DIR / "Reports"    / f"New_Tab_{tag}.xlsx"
        self.path_aruba     = BASE_DIR / "Aruba Urls" / f"Aruba{tag}.txt"

        # ── Playwright handles ────────────────────────────────────────
        self._playwright   = None
        self._browser      = None
        self._context      = None
        self._session_page = None   # single shared page

        # ── Country-check throttle state ──────────────────────────────
        self._last_country_check_time     = time.time()
        self._pages_since_country_check   = 0

        # ── Pre-computed domain for external-link filter ─────────────
        self._base_domain = urlparse(self.BASE_URL).netloc.lower()

    # ------------------------------------------------------------------
    # 4.2  Private utilities
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
    # 4.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Launch the Playwright browser and create a shared browser context."""
        self._playwright = sync_playwright().start()
        self._browser    = self._playwright.chromium.launch(headless=False)
        self._context    = self._browser.new_context()
        print(f"✅ Browser launched for {self.username}")

    def teardown(self) -> None:
        """Close Playwright resources and run downstream report post-processing."""
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

        # Run downstream work-allocation step if a report was generated
        try:
            df = pd.read_excel(self.path_report)
            if len(df) > 0:
                work.work_alloc_execute(
                    str(self.path_report),
                    "Fixers_list.xlsx",
                    str(self.path_aruba),
                )
        except FileNotFoundError:
            pass
        except Exception as exc:
            print(f"⚠️  Post-processing skipped: {exc}")

        print(f"🧹 Browser closed for {self.username}")

    def _get_session_page(self):
        """Return the long-lived session page, creating it lazily if needed."""
        if self._session_page is None:
            self._session_page = self._context.new_page()
            self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)
        return self._session_page

    # ------------------------------------------------------------------
    # 4.4  Login
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

        time.sleep(10)
        self.set_country(page)
        time.sleep(5)

    # ------------------------------------------------------------------
    # 4.5  Country / overlay management
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
        time.sleep(5)

        # --- STEP 1: Dismiss notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5_000)
            if overlay and overlay.is_visible():
                if force_recheck:
                    print("🔔 Notification overlay detected (re-check).")
                else:
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
            if not force_recheck:
                print("✅ No overlay appeared, continuing.")
        except Exception as exc:
            if not force_recheck:
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
            if not force_recheck:
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

        return current_country

    def _maybe_check_country(self) -> None:
        """
        Periodically re-verify the country setting hasn't drifted.

        Triggers on EITHER time elapsed (120 s) OR pages checked (10),
        whichever threshold is reached first.  If the shared page has
        drifted off-domain, we navigate back to the portal home first
        so the eyeball widget is guaranteed to render.
        """
        current_time = time.time()

        time_ok  = (current_time - self._last_country_check_time) >= COUNTRY_CHECK_INTERVAL_SECONDS
        pages_ok = self._pages_since_country_check >= COUNTRY_CHECK_EVERY_N_PAGES

        if not (time_ok or pages_ok):
            return

        print(f"\n{'=' * 80}")
        print(f"🔍 Periodic Country Verification")
        print(f"   Time since last check: {current_time - self._last_country_check_time:.1f}s")
        print(f"   Pages since last check: {self._pages_since_country_check}")
        print(f"{'=' * 80}")

        page = self._get_session_page()
        try:
            current_url = page.url or ""

            # If somehow we're on an external URL, go back to PRP home
            if not current_url.startswith("https://partner.hpe.com"):
                print(f"⚠️ Page on external URL: {current_url[:50]}...")
                print(f"   Navigating back to PRP home")
                try:
                    page.goto(
                        self.BASE_URL + "/group/prp/home",
                        wait_until="domcontentloaded",
                        timeout=PAGE_NAV_TIMEOUT_MS,
                    )
                    time.sleep(3)
                except Exception as nav_exc:
                    print(f"⚠️  Could not reach portal home: {nav_exc}")
                    self._last_country_check_time   = current_time
                    self._pages_since_country_check = 0
                    print(f"{'=' * 80}\n")
                    return

            # Re-run country check (no extra navigation needed — already on PRP)
            self.set_country(page, force_recheck=True)

            self._last_country_check_time   = current_time
            self._pages_since_country_check = 0

        except Exception as exc:
            print(f"⚠️ Error during country verification: {exc}")
            # Always reset counters so we don't spin retrying
            self._last_country_check_time   = current_time
            self._pages_since_country_check = 0

        print(f"{'=' * 80}\n")

    # ------------------------------------------------------------------
    # 4.6  Main test
    # ------------------------------------------------------------------

    @log_module_metric("New Tab")
    def test_new_tab(self):
        """
        Read crawled PageTree, visit each internal page, and verify that
        external links open in a new tab.  Method name preserved for
        @log_module_metric compatibility.
        """
        self.login()

        # Collected bug reports — each entry: [source_url, bad_link, reason]
        notopening: list = []

        # Aggregate statistics across all pages
        stats = {
            "total_pages_tested": 0,
            "total_links_tested": 0,
            "total_correct":      0,
            "total_incorrect":    0,
            "total_footer_skips": 0,
        }

        start_time = time.time()

        page = self._get_session_page()

        # ── Load page tree ─────────────────────────────────────────────
        with open(self.path_page_tree, "r", encoding="utf-8") as f:
            site_urls = [line.strip() for line in f if line.strip()]

        print(f"\n{'#' * 80}")
        print(f"🚀 Starting New Tab Test (Simple Attribute Check)")
        print(f"📄 Pages to test: {len(site_urls)}")
        print(f"{'#' * 80}\n")

        # ── Per-page test loop ────────────────────────────────────────
        for site_url in site_urls:
            # Periodic country verification (time OR page count based)
            self._maybe_check_country()

            self._test_single_page(site_url, page, notopening, stats)

        # ── Final summary ─────────────────────────────────────────────
        elapsed = time.time() - start_time

        print(f"\n{'#' * 80}")
        print(f"✅ TEST COMPLETE")
        print(f"📊 Statistics:")
        print(f"   - Pages tested: {stats['total_pages_tested']}")
        print(f"   - External links tested: {stats['total_links_tested']}")
        print(f"   - Footer links skipped: {stats['total_footer_skips']}")
        print(f"   - Correct UX (opens new tab): {stats['total_correct']}")
        print(f"   - Incorrect UX (same tab): {stats['total_incorrect']}")
        print(f"   - Time elapsed: {elapsed:.1f}s ({elapsed / 60:.1f} min)")
        if stats["total_links_tested"] > 0:
            print(f"   - Avg time per link: {elapsed / stats['total_links_tested']:.3f}s")
        print(f"{'#' * 80}\n")

        # Write the Excel report
        self._write_excel(notopening)

    def _test_single_page(self, site_url: str, page, notopening: list, stats: dict) -> None:
        """
        Visit one internal page, find external links, classify each.
        Factored out of test_new_tab() to match the crawler's structure
        (per-page work isolated from the main loop).
        """
        stats["total_pages_tested"] += 1
        self._pages_since_country_check += 1

        print(f"\n{'=' * 80}")
        print(f"🔍 Page #{stats['total_pages_tested']}: {site_url}")
        print(f"{'=' * 80}")

        # ── Navigate ──────────────────────────────────────────────────
        try:
            # OPTIMIZATION #2: domcontentloaded is enough — we only read
            # HTML attributes, we don't render anything.
            page.goto(
                site_url,
                wait_until="domcontentloaded",
                timeout=PAGE_NAV_TIMEOUT_MS,
            )

            # Skip homepage redirects (content not available for this account)
            try:
                if is_home_redirect_playwright(page, HOME_PREFIXES):
                    print(f"⏭️  Skipped (home redirect)")
                    return
            except Exception:
                pass

            # Slow-loading pages need extra time to finish rendering.
            # We preserve the original 25-second sleep exactly — it's a
            # known-good workaround and reducing it risks missing anchors.
            if site_url in self._delayed_loading_links or site_url in self._absurd_links:
                print(f"⏳ Waiting {SLOW_PAGE_SLEEP_SECONDS}s for slow-loading page...")
                time.sleep(SLOW_PAGE_SLEEP_SECONDS)
            else:
                page.wait_for_timeout(PAGE_SETTLE_MS)

        except PlaywrightTimeoutError:
            print(f"⏱️  Timeout loading page")
            return
        except Exception as exc:
            print(f"❌ Failed to load page: {exc}")
            return

        # ── OPTIMIZATION #1: bulk-collect all anchor data in ONE call ─
        try:
            anchor_data_list = page.evaluate(_JS_COLLECT_ANCHORS)
        except Exception as exc:
            print(f"❌ Failed to collect anchors: {exc}")
            return

        print(f"📊 Found {len(anchor_data_list)} total links")

        # ── Filter to external, visible, non-footer links ─────────────
        external_anchors = []
        page_footer_skips = 0

        for a_data in anchor_data_list:
            href = a_data.get("href") or ""
            if not href.startswith("http"):
                continue

            if not a_data.get("visible", True):
                continue

            if a_data.get("in_footer"):
                page_footer_skips += 1
                continue

            # Only external links (not PRP's own domain)
            try:
                href_domain = urlparse(href).netloc.lower()
            except Exception:
                continue

            if href_domain == self._base_domain:
                continue

            external_anchors.append(a_data)

        stats["total_footer_skips"] += page_footer_skips
        print(f"🔗 Found {len(external_anchors)} external links (skipped {page_footer_skips} footer on this page)")

        # ── Classify each external link ───────────────────────────────
        page_incorrect = 0
        for idx, a_data in enumerate(external_anchors, 1):
            stats["total_links_tested"] += 1
            href = a_data["href"]

            print(f"  [{idx}/{len(external_anchors)}] {href[:70]}...")

            try:
                opens_new_tab, reason = classify_anchor_tab_behavior(a_data)
            except Exception as exc:
                # OPTIMIZATION: don't flag as broken on classification errors —
                # just log and skip so DOM hiccups aren't false reports.
                print(f"    ⚠️  Could not classify: {str(exc)[:50]}")
                continue

            if opens_new_tab is None:
                # Indeterminate — skip quietly
                continue

            if opens_new_tab:
                print(f"    ✅ Opens new tab: {reason}")
                stats["total_correct"] += 1
            else:
                print(f"    ❌ Opens same tab: {reason}")
                stats["total_incorrect"] += 1
                page_incorrect += 1
                notopening.append([site_url, href, reason])

        print(f"✅ Page complete - Issues on this page: {page_incorrect}")

    # ------------------------------------------------------------------
    # 4.7  Output writing
    # ------------------------------------------------------------------

    def _write_excel(self, notopening: list) -> None:
        """Write the New_Tab Excel report (column set UNCHANGED)."""
        self._ensure_output_dirs()

        rows = []
        issue_id = 1

        for item in notopening:
            if len(item) >= 3:
                src, badlink, description = item[0], item[1], item[2]
            else:
                src, badlink = item[0], item[1]
                description = "Link not opening in a new tab"

            rows.append([
                issue_id,
                self.username,
                "New Tab",
                self.region,
                self.country,
                self.language,
                src,
                badlink,
                description,
                datetime.datetime.now(),
                "",
                "New",
                "-",
            ])
            issue_id += 1

        df = pd.DataFrame(
            rows,
            columns=[
                "Issue ID", "Demo Account", "Category", "Region", "Country", "Language",
                "Link", "Error Link", "Description", "Time Identified",
                "Mail ID", "Status", "Comments",
            ],
        )

        df.to_excel(self.path_report, index=False)
        print(f"📝 Report saved: {self.path_report}")


# ===========================================================================
# SECTION 5 – RUNNER
# ===========================================================================

def run_account(account):
    """
    Entry point for a single account.
    OPTIMIZATION #3: try/finally ensures teardown always runs.
    """
    prp = None
    try:
        prp = PRP(*account)
        prp.setup()
        prp.test_new_tab()
        print(f"Finished processing: {account[0]}")

    except Exception as exc:
        print(f"Error processing {account[0]}: {exc}")

    finally:
        if prp is not None:
            try:
                prp.teardown()
            except Exception as td_exc:
                print(f"⚠️  teardown error for {account[0]}: {td_exc}")


# ===========================================================================
# SECTION 6 – MAIN BLOCK (matches crawler pattern)
# ===========================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # ACCOUNTS
    # Format: [username, password, region, country, language, account_type]
    # ------------------------------------------------------------------
    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy',       'Italian',  'distri'],
        # ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Brazil',     'English',  'distri'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'Germany',    'German',   'T2'],
        # ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Spain',      'Spanish',  'T2'],
        # ['mhmg_albert_solp1@yopmail.com', 'Login2Bot!', 'EMEA', 'South Korea','English',  'T2'],
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
        print(f"▶  Process started for {account[0]}  (running: {len(running) + 1} / {MAX_PARALLEL})")
        running.append(p)
        all_procs.append(p)

    for p in all_procs:
        p.join()
        print(f"⏹  Process finished: {p.name}  (exit code: {p.exitcode})")

    print("🎉 All accounts processed successfully")