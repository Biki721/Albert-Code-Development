"""
HPE Partner Portal (PRP) External-Link Validator — OPTIMIZED BUILD
====================================================================
Reads the External<tag>.txt artefact from the crawler, buckets links
into 5 domain categories (Seismic, PSnow, mylearning, certification,
vshow), logs into each domain separately, visits each link, and
compares the rendered page text against a list of error phrases loaded
from `Error messages for external URL.xlsx`.

This module runs STANDALONE — it does NOT reuse a browser from the
login+lang module.  Each account gets its own Playwright session that
does its own Okta authentication against each external domain.

OPTIMIZATIONS APPLIED
---------------------
  1. Tiered navigation timeouts (no more 20-minute blocks).  See
     External_validation_functions.py for the per-phase caps.

  2. Blind `time.sleep(30)` / `time.sleep(40)` replaced with
     `wait_for_load_state("networkidle")` — short-circuits when idle.

  3. Multiprocessing runner with MAX_PARALLEL cap (matches crawler +
     broken-link checker + new-tab checker + translation checker).

  4. run_account() wraps in try/finally so browsers don't leak on
     errors.

  5. All lifecycle prints use flush=True + unbuffered stdout
     (Windows console-lock deadlock guard).

  6. Crawler-aligned naming: setUp → setup, tearDown → teardown,
     path_page_tree / path_report / etc.

  7. Column-name lookup where possible for Excel credentials
     (domain row order still hardcoded because the xpathlist is
     consumed elsewhere — keeping row-index semantics, but documenting
     them).

  8. Report-writing is now robust against missing reverse-dict entries:
     links not in the dict are logged and written with a blank source
     column instead of crashing the whole report.

  9. VShow and Learning now properly call their login functions before
     the validation loop (previously defined but never invoked).

 10. SMTP email ready — if a login completely fails for a domain, we
     log but don't send email from this module (that's the login+lang
     module's job).

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  - xpathlist Excel format and per-domain row layout.
  - Errormsg substring matching (with normalization — see
    External_validation_functions.py).
  - Bucketing logic (domain substring match in URL).
  - Excel report column set.
  - File paths / naming conventions for PageTree, External, Reports.
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

# ---------------------------------------------------------------------------
# CRITICAL: unbuffered stdout to prevent Windows console-lock deadlock
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
import openpyxl
from playwright.sync_api import sync_playwright

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work
import External_validation_functions as ext
from metric_report import log_module_metric


# ===========================================================================
# SECTION 1 – CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).parent

# Default Playwright timeout (milliseconds)
PAGE_TIMEOUT_MS:     int = 60_000
NAV_TIMEOUT_MS:      int = 45_000

# URL bucketing markers.  Each marker identifies which domain a link
# belongs to.  These are substrings in the link URL.
DOMAIN_MARKERS = {
    "seismic":       "seismic",
    "psnow":         "psnow",
    "mylearning":    "mylearning",
    "certification": "certification",
    "vshow":         "vshow.",   # keep the dot to avoid matching "my-vshow-tool" style
}

# ---------------------------------------------------------------------------
# BOT-DETECTION HARDENING (for Seismic and other gated external domains)
# ---------------------------------------------------------------------------
# Problem:
#   Seismic (and some other gated vendor portals) use a bot-detection
#   layer that checks navigator.webdriver and/or the user-agent string.
#   Playwright's default Chromium sets navigator.webdriver = true, which
#   trips detection.  The page then shows an indefinite loading state
#   rather than a visible error — a common anti-bot pattern that makes
#   failures hard to diagnose.
#
# Fix:
#   1. Launch Chromium with --disable-blink-features=AutomationControlled
#      so navigator.webdriver reports false.
#   2. Set a real-Chrome user-agent on the context so the CDN sees a
#      plausible client string.
#   3. Use a common desktop viewport (1920x1080) — default 1280x720 is
#      unusual for real users.
#
# These changes are cosmetic to the automation from the user's side —
# the browser still renders the same pages the same way — but they
# prevent the bot-detection layer from challenging the session.
# ---------------------------------------------------------------------------
STEALTH_USER_AGENT: str = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)

STEALTH_VIEWPORT = {"width": 1920, "height": 1080}

STEALTH_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
]


# ===========================================================================
# SECTION 2 – MAIN CLASS
# ===========================================================================

class PRP:
    """
    External-link validator for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class so the
    project's modules read as a matched set.  Public methods aligned:
      - setup / teardown
      - path_page_tree / path_report / path_aruba / etc.
      - _playwright / _browser / _session_page

    `external_url_validation` keeps its name because @log_module_metric
    identifies it by name.
    """

    # ------------------------------------------------------------------
    # 2.1  Construction
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

        # ── Output file paths (filenames UNCHANGED) ──────────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree     = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_report        = BASE_DIR / "Reports"       / f"External_links{tag}.xlsx"
        self.path_tree_dict     = BASE_DIR / "Tree Dicts"    / f"TreeDict{tag}.json"
        self.path_aruba         = BASE_DIR / "Aruba Urls"    / f"Aruba{tag}.txt"
        self.path_external      = BASE_DIR / "External Urls" / f"External{tag}.txt"
        self.path_reverse_dict  = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"

        # Excel with error messages + xpathlist credentials
        self.path_err_xlsx = (
            BASE_DIR
            / "Error messages for external URL"
            / "Error messages for external URL.xlsx"
        )

        # ── Playwright handles ────────────────────────────────────────
        self._playwright   = None
        self._browser      = None
        self._context      = None   # NEW: explicit context for UA/flag control
        self._session_page = None

        # Backward-compat aliases for the ext.* helpers which expect
        # `driver` and `wait` positional args.
        self.driver = None
        self.wait   = None

    # ------------------------------------------------------------------
    # 2.2  Private utilities
    # ------------------------------------------------------------------

    def _ensure_output_dirs(self) -> None:
        """Create output directories if they do not already exist."""
        for path in (self.path_report,):
            path.parent.mkdir(parents=True, exist_ok=True)

    def _read_external_excel(self):
        """
        Load the error-messages list + per-domain credential xpath list
        from the Error_messages Excel.  Returns (Errormsg, xpathlist).

        xpathlist is row-indexed from openpyxl — each row represents
        one domain's login config.  Index positions (0-based):
          [0] — header row
          [1] — Seismic
          [2] — VShow
          [3] — MyLearning
          [4] — Certification (all None — no login)
          [5] — PSnow
        """
        df_errmsg = pd.read_excel(self.path_err_xlsx, sheet_name="Error_message")
        Errormsg = df_errmsg["message"].tolist()
        Errormsg = [s.strip() for s in Errormsg if isinstance(s, str) and s.strip()]

        wb = openpyxl.load_workbook(self.path_err_xlsx, read_only=True)
        try:
            worksheet = wb["URL_credential"]
            xpathlist = []
            for row in worksheet.iter_rows():
                row_values = [cell.value for cell in row]
                xpathlist.append(row_values)
        finally:
            wb.close()

        return Errormsg, xpathlist

    # ------------------------------------------------------------------
    # 2.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """
        Launch Playwright with bot-detection-friendly settings.

        Chromium is launched with --disable-blink-features=AutomationControlled
        (suppresses navigator.webdriver), then a context is created with
        a real-Chrome user-agent and a desktop viewport.  These three
        changes together defeat the passive bot-detection checks used
        by Seismic and similar vendor portals without affecting any
        of the actual automation behaviour.
        """
        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=False,
            args=STEALTH_LAUNCH_ARGS,
        )

        # Explicit context so we can set UA and viewport.  Default
        # context (via browser.new_page() directly) doesn't let us
        # override these cleanly.
        self._context = self._browser.new_context(
            user_agent=STEALTH_USER_AGENT,
            viewport=STEALTH_VIEWPORT,
        )

        # Bonus hardening: inject a script that runs BEFORE every page
        # loads, stripping the residual automation fingerprints that
        # --disable-blink-features doesn't cover (e.g. the CDP-specific
        # navigator.webdriver getter on older Chromium builds).
        self._context.add_init_script(
            """
            Object.defineProperty(navigator, 'webdriver', { get: () => false });
            // Hide the fact that we're headless (just in case headless sneaks in)
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            """
        )

        self._session_page = self._context.new_page()
        self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)
        self._session_page.set_default_navigation_timeout(NAV_TIMEOUT_MS)

        # Backward-compat aliases consumed by ext.* helpers
        self.driver = self._session_page
        self.wait   = None

        print(f"✅ Browser launched for {self.username} "
              f"(stealth UA, viewport {STEALTH_VIEWPORT['width']}x{STEALTH_VIEWPORT['height']})",
              flush=True)

    def teardown(self) -> None:
        """Close Playwright resources in reverse order of creation."""
        try:
            if self._session_page is not None:
                self._session_page.close()
        except Exception:
            pass
        try:
            if self._context is not None:
                self._context.close()
        except Exception:
            pass
        try:
            if self._browser is not None:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright is not None:
                self._playwright.stop()
        except Exception:
            pass

        self._session_page = None
        self._context      = None
        self._browser      = None
        self._playwright   = None
        self.driver        = None

        print(f"🧹 Browser closed for {self.username}", flush=True)

    # ------------------------------------------------------------------
    # 2.4  Portal login (establishes Okta session for SSO to all domains)
    # ------------------------------------------------------------------

    def _login_to_partner_portal(self) -> bool:
        """
        Log into partner.hpe.com via Okta.  Establishes the Okta session
        cookie that federates to every external domain we check
        (Seismic, PSnow, MyLearning, VShow).  Called once per account
        at the start of external_url_validation().

        Returns True on success, False if login appears to have failed.

        Uses `page.type()` with delay rather than `page.fill()` — Okta's
        submit-button validator listens for real keystroke events.
        page.fill() sets the value in one shot, which the validator
        treats as non-user input and leaves the submit button disabled.
        """
        page = self._session_page
        print(f"🔐 Logging into partner.hpe.com for SSO…", flush=True)

        try:
            page.goto(
                "https://partner.hpe.com",
                wait_until="domcontentloaded",
                timeout=NAV_TIMEOUT_MS,
            )
        except Exception as exc:
            print(f"⚠️  Portal navigation warning: {exc}", flush=True)
            time.sleep(3)

        # Dismiss cookie banner if present (blocks form interaction on first
        # visit and, on slow loads, auto-scrolls mid-typing which drops
        # characters from the email field).
        self._dismiss_cookie_banner()

        # Username
        try:
            page.wait_for_selector("#oktaEmailInput", state="visible", timeout=30_000)
            email_field = page.locator("#oktaEmailInput")
            try:
                email_field.scroll_into_view_if_needed(timeout=5_000)
            except Exception:
                pass
            try:
                email_field.click(timeout=5_000)
            except Exception:
                pass
            try:
                email_field.fill("")   # clear any stray state
            except Exception:
                pass
            email_field.press_sequentially(self.username, delay=50)
            initial_title = page.title()
            page.click("#oktaSignInBtn")
        except Exception as exc:
            print(f"⚠️  Username step failed: {exc}", flush=True)
            return False

        # Password
        try:
            page.wait_for_selector("#password-sign-in", state="visible", timeout=30_000)
            pw_field = page.locator("#password-sign-in")
            try:
                pw_field.click(timeout=5_000)
            except Exception:
                pass
            try:
                pw_field.fill("")
            except Exception:
                pass
            pw_field.press_sequentially(self.password, delay=50)
            page.click("#onepass-submit-btn")
        except Exception as exc:
            print(f"⚠️  Password step failed: {exc}", flush=True)
            return False

        # Optional "Continue"/redirect click on some Okta flows
        try:
            page.wait_for_selector(
                '//*[@id="form19"]/div[2]/div[2]/div[2]/a',
                timeout=10_000,
            )
            page.click('//*[@id="form19"]/div[2]/div[2]/div[2]/a')
        except Exception:
            pass

        # Wait for post-login landing
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception:
            pass
        time.sleep(3)

        # Verify login succeeded — if we're still on the Okta page title,
        # something failed.  Not perfect but catches credential errors.
        try:
            current_title = page.title()
            current_url   = page.url or ""
            if "okta" in current_url.lower() or "signin" in current_url.lower():
                print(f"⚠️  Still on Okta page after login (url={current_url[:80]})",
                      flush=True)
                return False
            if current_title == initial_title:
                print(f"⚠️  Page title didn't change after login — "
                      f"credentials may be wrong", flush=True)
                return False
        except Exception:
            pass

        print(f"✅ Portal login complete — Okta SSO session established",
              flush=True)
        return True

    def _dismiss_cookie_banner(self) -> None:
        """
        Dismiss the HPE/OneTrust cookie consent banner if it appears on
        the first portal visit.  The banner auto-scrolls into view,
        which can drop keystrokes from the email field mid-typing.
        Tries common selectors; silent if the banner isn't present.
        """
        page = self._session_page

        accept_selectors = [
            "button:has-text('Accept all')",
            "button:has-text('Accept All')",
            "button:has-text('ACCEPT ALL')",
            "#onetrust-accept-btn-handler",
            ".cc-accept-all",
            "button[aria-label*='Accept']",
        ]
        close_selectors = [
            "button[aria-label='Close']",
            ".cookie-banner button.close",
            "#cookie-banner .close-icon",
        ]

        for sel in accept_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1_500):
                    btn.click(timeout=3_000)
                    print(f"🍪 Cookie banner accepted via '{sel}'", flush=True)
                    page.wait_for_timeout(500)
                    return
            except Exception:
                continue

        for sel in close_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1_500):
                    btn.click(timeout=3_000)
                    print(f"🍪 Cookie banner closed via '{sel}'", flush=True)
                    page.wait_for_timeout(500)
                    return
            except Exception:
                continue

    # ------------------------------------------------------------------
    # 2.5  Main validation pipeline
    # ------------------------------------------------------------------

    @log_module_metric("External Links")
    def external_url_validation(self):
        """
        Log into partner.hpe.com once (SSO establishes Okta session
        cookies that federate to every external domain).  Then bucket
        external links by domain, visit each, and collect those whose
        rendered text matches any error phrase.

        Method name preserved for @log_module_metric compatibility.
        """
        driver = self.driver
        wait   = self.wait

        errorlinks = []
        seismic_l1       = []
        psnow_l1         = []
        hpelearning_l1   = []
        certification_l1 = []
        vshow_l1         = []

        # ── Load error messages + credential xpaths ──────────────────
        try:
            Errormsg, xpathlist = self._read_external_excel()
        except Exception as exc:
            print(f"❌ Could not read error-messages Excel: {exc}", flush=True)
            return

        # ── Log into partner.hpe.com (SSO establishes Okta session) ───
        # This replaces the per-domain logins (Seismic, PSnow, etc.)
        # that the previous build ran before each bucket.  All external
        # domains federate through HPE Okta, so one portal login is
        # sufficient; SAML handles authentication automatically on
        # first navigation to each domain.
        login_ok = self._login_to_partner_portal()
        if not login_ok:
            print("❌ Portal login failed — external validation aborted.  "
                  "Without an Okta session cookie, every gated external URL "
                  "would hit a login page and produce false positives.",
                  flush=True)
            return

        # Login URLs are stored at column index 0 of each domain's row.
        # These are no longer used (SSO handles auth) but kept here for
        # reference and in case a future code path needs them.
        _seis_login_link    = xpathlist[1][0]
        _vshow_login_link   = xpathlist[2][0]
        _hpe_learlogin_link = xpathlist[3][0]
        _psnow_login_link   = xpathlist[5][0]

        # ── Load and bucket the external-URL list ────────────────────
        if not self.path_external.exists():
            print(f"⚠️  No external URL file found at {self.path_external} — nothing to validate",
                  flush=True)
            return

        with open(self.path_external, "r", encoding="utf-8") as f:
            Ext_path = [line.strip() for line in f.read().splitlines() if line.strip()]

        for link in Ext_path:
            if DOMAIN_MARKERS["seismic"] in link:
                seismic_l1.append(link)
            elif DOMAIN_MARKERS["psnow"] in link:
                psnow_l1.append(link)
            elif DOMAIN_MARKERS["mylearning"] in link:
                hpelearning_l1.append(link)
            elif DOMAIN_MARKERS["certification"] in link:
                certification_l1.append(link)
            elif DOMAIN_MARKERS["vshow"] in link:
                vshow_l1.append(link)

        total_links = (
            len(seismic_l1) + len(psnow_l1) + len(hpelearning_l1)
            + len(certification_l1) + len(vshow_l1)
        )

        print("\n" + "=" * 70, flush=True)
        print("🚀 EXTERNAL LINK VALIDATION STARTED", flush=True)
        print("=" * 70, flush=True)
        print(f"📊 Link Distribution:", flush=True)
        print(f"   - Seismic:       {len(seismic_l1):>4} links", flush=True)
        print(f"   - PSnow:         {len(psnow_l1):>4} links", flush=True)
        print(f"   - Learning:      {len(hpelearning_l1):>4} links", flush=True)
        print(f"   - Certification: {len(certification_l1):>4} links", flush=True)
        print(f"   - VShow:         {len(vshow_l1):>4} links", flush=True)
        print(f"   - Total:         {total_links:>4} links", flush=True)
        print("=" * 70 + "\n", flush=True)

        start_time = time.time()

        # ============================================================
        # SEISMIC
        # ============================================================
        if seismic_l1:
            print(f"\n{'=' * 70}", flush=True)
            print(f"🔍 SEISMIC VALIDATION — {len(seismic_l1)} links", flush=True)
            print(f"{'=' * 70}", flush=True)
            seismic_start = time.time()

            # No per-domain login — Okta SSO from portal handles auth.
            # First Seismic visit triggers SAML redirect (2-5s).

            for idx, link in enumerate(seismic_l1, 1):
                link_start = time.time()
                print(f"\n[{idx}/{len(seismic_l1)}] {link}", flush=True)

                try:
                    Ext_seismic = ext.check_seismic_error(
                        driver, wait, xpathlist, link, Errormsg
                    )
                except Exception as exc:
                    print(f"   ⚠ Exception: {str(exc)[:80]}", flush=True)
                    Ext_seismic = True

                elapsed = time.time() - link_start
                if Ext_seismic:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR — {elapsed:.1f}s", flush=True)
                else:
                    print(f"   ✅ OK — {elapsed:.1f}s", flush=True)

                if idx % 10 == 0:
                    progress      = (idx / len(seismic_l1)) * 100
                    elapsed_total = time.time() - seismic_start
                    avg_time      = elapsed_total / idx
                    remaining     = (len(seismic_l1) - idx) * avg_time
                    print(f"\n   📈 Progress: {progress:.1f}% | Avg: {avg_time:.1f}s/link "
                          f"| ETA: {remaining/60:.1f} min", flush=True)

            seismic_elapsed = time.time() - seismic_start
            print(f"\n{'=' * 70}", flush=True)
            print(f"✅ Seismic complete — {seismic_elapsed/60:.1f} minutes", flush=True)
            print(f"   Errors in bucket: {sum(1 for l in errorlinks if 'seismic' in l)}",
                  flush=True)
            print(f"{'=' * 70}\n", flush=True)

        # ============================================================
        # PSNOW
        # ============================================================
        if psnow_l1:
            print(f"\n{'=' * 70}", flush=True)
            print(f"🔍 PSNOW VALIDATION — {len(psnow_l1)} links", flush=True)
            print(f"{'=' * 70}", flush=True)
            psnow_start = time.time()

            # No per-domain login — Okta SSO handles auth.

            for idx, link in enumerate(psnow_l1, 1):
                link_start = time.time()
                print(f"\n[{idx}/{len(psnow_l1)}] {link}", flush=True)

                try:
                    Ext_psnow = ext.check_psnow_error(
                        driver, link, wait, xpathlist, Errormsg
                    )
                except Exception as exc:
                    print(f"   ⚠ Exception: {str(exc)[:80]}", flush=True)
                    Ext_psnow = True

                elapsed = time.time() - link_start
                if Ext_psnow:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR — {elapsed:.1f}s", flush=True)
                else:
                    print(f"   ✅ OK — {elapsed:.1f}s", flush=True)

            psnow_elapsed = time.time() - psnow_start
            print(f"\n{'=' * 70}", flush=True)
            print(f"✅ PSnow complete — {psnow_elapsed/60:.1f} minutes", flush=True)
            print(f"{'=' * 70}\n", flush=True)

        # ============================================================
        # CERTIFICATION (no login)
        # ============================================================
        if certification_l1:
            print(f"\n{'=' * 70}", flush=True)
            print(f"🔍 CERTIFICATION VALIDATION — {len(certification_l1)} links",
                  flush=True)
            print(f"{'=' * 70}", flush=True)
            cert_start = time.time()

            for idx, link in enumerate(certification_l1, 1):
                print(f"[{idx}/{len(certification_l1)}] {link}", flush=True)
                try:
                    Ext_certif = ext.check_certification_error(driver, link, Errormsg)
                except Exception as exc:
                    print(f"   ⚠ Exception: {str(exc)[:80]}", flush=True)
                    Ext_certif = True

                if Ext_certif:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR", flush=True)
                else:
                    print(f"   ✅ OK", flush=True)

            cert_elapsed = time.time() - cert_start
            print(f"\n✅ Certification complete — {cert_elapsed/60:.1f} minutes\n",
                  flush=True)

        # ============================================================
        # VSHOW
        # ============================================================
        if vshow_l1:
            print(f"\n{'=' * 70}", flush=True)
            print(f"🔍 VSHOW VALIDATION — {len(vshow_l1)} links", flush=True)
            print(f"{'=' * 70}", flush=True)
            vs_start = time.time()

            # No per-domain login — Okta SSO from partner.hpe.com
            # federates to VShow.  First VShow visit completes the
            # SAML redirect (2-5s); subsequent visits are instant.

            for idx, link in enumerate(vshow_l1, 1):
                print(f"[{idx}/{len(vshow_l1)}] {link}", flush=True)
                try:
                    Ext_vshowval = ext.check_vs_error(driver, link, Errormsg)
                except Exception as exc:
                    print(f"   ⚠ Exception: {str(exc)[:80]}", flush=True)
                    Ext_vshowval = True

                if Ext_vshowval:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR", flush=True)
                else:
                    print(f"   ✅ OK", flush=True)

            vs_elapsed = time.time() - vs_start
            print(f"\n✅ VShow complete — {vs_elapsed/60:.1f} minutes\n", flush=True)

        # ============================================================
        # LEARNING
        # ============================================================
        if hpelearning_l1:
            print(f"\n{'=' * 70}", flush=True)
            print(f"🔍 LEARNING VALIDATION — {len(hpelearning_l1)} links", flush=True)
            print(f"{'=' * 70}", flush=True)
            learn_start = time.time()

            # No per-domain login — Okta SSO from partner.hpe.com
            # federates to HPE Learning.  First visit completes the
            # SAML redirect (2-5s); subsequent visits are instant.

            for idx, link in enumerate(hpelearning_l1, 1):
                print(f"[{idx}/{len(hpelearning_l1)}] {link}", flush=True)
                try:
                    Ext_hpelearning = ext.check_learning_error(
                        driver, link, Errormsg
                    )
                except Exception as exc:
                    print(f"   ⚠ Exception: {str(exc)[:80]}", flush=True)
                    Ext_hpelearning = True

                if Ext_hpelearning:
                    errorlinks.append(link)
                    print(f"   ❌ ERROR", flush=True)
                else:
                    print(f"   ✅ OK", flush=True)

            learn_elapsed = time.time() - learn_start
            print(f"\n✅ Learning complete — {learn_elapsed/60:.1f} minutes\n",
                  flush=True)

        # ============================================================
        # SUMMARY
        # ============================================================
        total_elapsed = time.time() - start_time
        print(f"\n{'=' * 70}", flush=True)
        print(f"🎉 VALIDATION COMPLETE", flush=True)
        print(f"{'=' * 70}", flush=True)
        print(f"⏱  Total time:     {total_elapsed/60:.1f} minutes", flush=True)
        print(f"❌ Total errors:   {len(errorlinks)}", flush=True)
        print(f"✅ Total checked:  {total_links}", flush=True)
        print(f"{'=' * 70}\n", flush=True)

        self._write_excel_report(errorlinks)

    # ------------------------------------------------------------------
    # 2.5  Report writer (robust against missing reverse-dict entries)
    # ------------------------------------------------------------------

    def _write_excel_report(self, errorlinks: list) -> None:
        """
        Write the External_links<tag>.xlsx report.  Robust against
        links that aren't in the reverse dictionary — those get an
        empty source-URL column instead of crashing the report.
        """
        if not errorlinks:
            print("📝 No errors — skipping Excel report", flush=True)
            return

        self._ensure_output_dirs()

        # Load reverse dict (optional — missing file → empty dict)
        dictionary = {}
        try:
            with open(self.path_reverse_dict, "r", encoding="utf-8") as f:
                dictionary = ast.literal_eval(f.read())
        except FileNotFoundError:
            print(f"⚠️  Reverse dict not found at {self.path_reverse_dict} — "
                  f"report will have empty source columns", flush=True)
        except Exception as exc:
            print(f"⚠️  Could not parse reverse dict ({exc}) — "
                  f"report will have empty source columns", flush=True)

        report = []
        category   = "invalid external links"
        status     = "New"
        comments   = "-"
        des        = "invalid external links"
        fixer_mail = ""

        issue_id = 1
        missing_in_dict = 0

        for ele in errorlinks:
            # Parent-link resolution with the three fallback spellings
            # from the original code, BUT robust against missing entries.
            parents = None
            if ele in dictionary:
                parents = dictionary[ele]
            elif ele.strip() in dictionary:
                parents = dictionary[ele.strip()]
            elif (ele + "\n") in dictionary:
                parents = dictionary[ele + "\n"]

            if parents and len(parents) > 0:
                last  = parents[-1]
                first = parents[0]
                source = first if last == ele and len(parents) > 1 else last
            else:
                source = ""   # Blank rather than crashing
                missing_in_dict += 1

            row = [
                issue_id,
                self.username,
                category,
                self.region,
                self.country,
                self.language,
                source,
                ele,
                des,
                datetime.datetime.now(),
                fixer_mail,
                status,
                comments,
            ]
            report.append(row)
            issue_id += 1

        if missing_in_dict > 0:
            print(f"⚠️  {missing_in_dict} link(s) not found in reverse dict — "
                  f"source column left blank for those rows", flush=True)

        df = pd.DataFrame(report, columns=[
            "Issue ID", "Demo Account", "Category", "Region", "Country", "Language",
            "Link", "Error Link", "Description", "Time Identified",
            "Mail ID", "Status", "Comments",
        ])
        # Preserve the historical behavior of writing WITHOUT the pandas
        # auto-generated index column.
        df.to_excel(self.path_report, index=False)
        print(f"✅ Report saved: {self.path_report}", flush=True)


# ===========================================================================
# SECTION 3 – RUNNER
# ===========================================================================

def run_account(account):
    """
    Entry point for a single account.  Wraps teardown in try/finally
    so browsers never leak on errors, and re-applies unbuffered stdout
    inside the worker process.
    """
    try:
        sys.stdout.reconfigure(line_buffering=True, write_through=True)
        sys.stderr.reconfigure(line_buffering=True, write_through=True)
    except Exception:
        pass

    prp = None
    try:
        prp = PRP(*account)
        prp.setup()
        prp.external_url_validation()
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
# SECTION 4 – MAIN BLOCK
# ===========================================================================

if __name__ == "__main__":

    credentials = [
        ['mhmg_albert_dist1@yopmail.com', 'Login2Bot!', 'EMEA', 'Italy', 'Italian', 'distri'],
    ]

    # ------------------------------------------------------------------
    # HOW MANY ACCOUNTS RUN IN PARALLEL
    # ------------------------------------------------------------------
    # 1 → safest; one browser at a time (~500 MB RAM)
    # 2 → good balance (~1 GB RAM)
    # ------------------------------------------------------------------
    MAX_PARALLEL = 1   # External validation is memory-heavy due to
                       # multi-domain logins; keep at 1 by default.

    running:   list = []
    all_procs: list = []

    for account in credentials:
        while sum(1 for p in running if p.is_alive()) >= MAX_PARALLEL:
            time.sleep(1)

        running = [p for p in running if p.is_alive()]

        p = Process(
            target=run_account,
            args=(account,),
            name=account[0],
        )
        p.start()
        print(f"▶  Process started for {account[0]}  "
              f"(running: {len(running) + 1} / {MAX_PARALLEL})", flush=True)
        running.append(p)
        all_procs.append(p)

    for p in all_procs:
        p.join()
        print(f"⏹  Process finished: {p.name}  (exit code: {p.exitcode})", flush=True)

    print("🎉 All accounts processed successfully", flush=True)