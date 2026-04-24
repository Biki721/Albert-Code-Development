"""
HPE Partner Portal (PRP) Login + Language Setter — OPTIMIZED BUILD
====================================================================
Authentication front-door for the PRP automation pipeline.

Responsibilities:
  1. Log in via Okta.
  2. Handle notification overlay and set the correct country via the
     eyeball widget.
  3. Navigate to the portal's Settings page.
  4. Detect the display language.
  5. If the display language doesn't match the required language, fill
     out the personal-details form (country / language / job title /
     phone) and submit, then call the update-language endpoint.
  6. Send SMTP notification emails on login failure or language change.

This module is a one-shot setup.  It does NOT run a full test loop.
Downstream modules (translation checker, etc.) consume the browser
handles produced here by calling:

    prp_login = module_login_lang.PRP(*account)
    prp_login.setup()
    ok = prp_login.login()
    # then pass prp_login._playwright / ._browser / ._session_page
    # to the next stage, and finally call prp_login.teardown()

IMPORTANT for callers
---------------------
Public attribute names have been renamed to match the crawler
convention used by the rest of the project:

    self.playwright     →  self._playwright
    self.browser        →  self._browser
    self.page           →  self._session_page

Method names likewise:

    setUp()                        →  setup()
    tearDown()                     →  teardown()
    test_load_home_page()          →  folded into login() as private _load_home_page()
    handle_country_and_overlay()   →  set_country()
    country_similarity()           →  _country_similarity()

The `login()` method keeps its name because @log_login_metric
identifies it by name.  The `_change_lang()` method likewise keeps
its name for @log_language_metric.

OPTIMIZATIONS APPLIED
---------------------
  1. BASE_DIR for all file paths — no more CWD dependency bug that
     broke reference-file loading when callers ran from a different
     working directory.
  2. Removed four unused .docx loads (delayed_loading, breadcrumb,
     absurd, breadcrumb_prefix) that were re-parsed on every import
     for no reason.
  3. Replaced win32com/Outlook email with SMTP (utils.smtp_email).
     Windows/Outlook dependency gone; COM-threading gotchas gone;
     works under multiprocessing.
  4. Removed the useless 90-second wait_for_load_state("networkidle")
     from setup() — it ran on a blank page that had no URL yet.
  5. Trimmed excessive timeouts in _open_settings_page (was ~240 s
     cumulative, now ~45 s).
  6. networkidle waits replaced with domcontentloaded where safe
     (same optimization as the other modules).
  7. login_title initialized to None in __init__ — removes the
     fragile hasattr() check.
  8. Multiprocessing runner with MAX_PARALLEL cap (matches crawler /
     broken-link / new-tab / translation modules).
  9. try/finally in run_account so browsers never leak on errors.
 10. Unbuffered stdout + flush=True on all lifecycle prints so Windows
     console-lock contention can't deadlock parallel workers.

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  - Liferay portlet selector IDs (country / language / job title /
    phone / save) — framework-generated, portal-specific.
  - Country/language/job-title/phone/save sequence and timings —
    tuned against the portal's form-validation behaviour.
  - The phone number "88888866666" — likely bypasses a validation rule.
  - LANG_VALUE_MAP, LANG_CODE_MAP, COUNTRY_MAP dictionaries.
  - _apply_language_update's hardcoded p_l_id=493064269 portlet layout.
  - Okta login selectors.
  - The detect → change flow in login().
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import datetime
import sys
import time
from multiprocessing import Process
from pathlib import Path

# ---------------------------------------------------------------------------
# CRITICAL: force unbuffered stdout so parallel workers don't deadlock on
# the Windows console lock.
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
    sys.stderr.reconfigure(line_buffering=True, write_through=True)
except Exception:
    pass

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work
from metric_report import metric_report, log_login_metric, log_language_metric

# SMTP email — soft import.  If the utility isn't present (non-HPE
# environment, development machine), the login module still works;
# email sends are skipped with a warning.
try:
    from utils.smtp_email import send_email as _smtp_send_email, get_email_recipients as _smtp_get_recipients
    _SMTP_AVAILABLE = True
except Exception as _imp_exc:
    _smtp_send_email      = None
    _smtp_get_recipients  = None
    _SMTP_AVAILABLE       = False
    print(f"⚠️  SMTP email utility not available ({_imp_exc}); "
          f"email notifications will be skipped", flush=True)


# ===========================================================================
# SECTION 1 – CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).parent

# Default Playwright navigation timeout (milliseconds)
PAGE_TIMEOUT_MS: int = 60_000

# Timeouts used during login flow
LOGIN_NAV_TIMEOUT_MS:  int = 90_000
POST_LOGIN_WAIT_MS:    int = 30_000
SETTINGS_NAV_TIMEOUT:  int = 45_000   # was ~240_000 cumulative


# ===========================================================================
# SECTION 2 – MAIN CLASS
# ===========================================================================

class PRP:
    """
    Login + language-setter for the HPE Partner Portal.

    Naming conventions mirror the crawler's PRPCrawler class so the
    project's modules read as a matched set.  See module docstring
    for migration notes when calling this from downstream modules.
    """

    BASE_URL = "https://partner.hpe.com"

    # ------------------------------------------------------------------
    # 2.1  Class-level lookup tables — portal-specific, leave alone
    # ------------------------------------------------------------------

    COUNTRY_MAP = {
        "United States":  "US",   # ADDED — needed for English accounts
        "Singapore":      "SG",   # ADDED — needed for Singaporean accounts
        "United Kingdom": "GB", "South Korea": "KR", "China": "CN", "Japan": "JP",
        "Italy": "IT", "Brazil": "BR", "Taiwan": "TW", "Indonesia": "ID",
        "France": "FR", "Germany": "DE", "Spain": "ES", "Turkey": "TR",
    }

    LANG_VALUE_MAP = {
        "English": "EN", "Singaporean": "EN",   # Singaporean maps to EN
        "Simplified Chinese": "ZH", "Chinese": "ZH",
        "Korean": "KO", "Japanese": "JA", "Italian": "IT", "Portuguese": "PT",
        "Taiwan": "ZH", "Indonesian": "IN", "Spanish": "ES", "Turkish": "TR",
        "German": "DE", "French": "FR",
    }

    LANG_CODE_MAP = {
        "English": "en_US", "Singaporean": "en_US",
        "Korean": "ko_KR", "Japanese": "ja_JP",
        "Chinese": "zh_CN", "Simplified Chinese": "zh_CN",
        "Italian": "it_IT", "German": "de_DE", "French": "fr_FR",
        "Spanish": "es_ES", "Portuguese": "pt_BR",
        "Turkish": "tr_TR", "Indonesian": "id_ID",
    }

    # Mapping of HTML lang attribute → language label used in credentials list.
    # FIXED: ja-JA → ja-JP, ko-KO → ko-KR (incorrect codes meant Japanese/Korean
    # accounts always tripped _change_lang() even when already correct).
    HTML_LANG_TO_LABEL = {
        "en-US": "English", "fr-FR": "French", "de-DE": "German", "it-IT": "Italian",
        "ja-JP": "Japanese", "ko-KR": "Korean",
        "pt-PT": "Portuguese", "pt-BR": "Portuguese",
        "ru-RU": "Russian", "es-ES": "Spanish", "zh-TW": "Chinese", "zh-CN": "Chinese",
        "tr-TR": "Turkish", "id-ID": "Indonesian", "ZH": "Simplified Chinese",
    }

    # ------------------------------------------------------------------
    # 2.2  Construction
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
        self.account_type = account_type

        # Canonical-language normalisation (preserves original behaviour)
        self.language = language
        if language == "Taiwan":
            self.language = "Chinese"
        elif language == "Simplified Chinese":
            self.language = "Chinese"
        elif language == "LARSpanish":
            self.language = "Spanish"

        # ── Output file paths (UNCHANGED so downstream tooling keeps working) ──
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree    = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_doc_links    = BASE_DIR / "DocumentLinks" / f"Doclinks{tag}.txt"
        self.path_reverse_dict = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"
        self.path_external     = BASE_DIR / "External Urls" / f"External{tag}.txt"

        # ── Timestamp helpers ─────────────────────────────────────────
        # Initialized BEFORE the email templates (which interpolate the
        # timestamp into their body).  current_date / _month / _time get
        # their real values later, inside login(), once we know the run
        # has actually started.
        self.current_datetime = datetime.datetime.now()
        self.current_date  = None
        self.current_month = None
        self.current_time  = None

        # ── Email subject/body templates ─────────────────────────────
        # Recipients and SMTP delivery happen through utils.smtp_email.
        # Subject/body pairs are stored as [subject, body] to match the
        # original interface of email().
        timestamp = self.current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        self.login_errmsg = [
            # Subject
            f"[Albert Automation] ⚠️  Login failed for demo account: {self.username}",
            # Body
            f"""Hello,

Albert Automation attempted to log in to the HPE Partner Ready Portal
using one of the configured demo accounts, but the login did not
succeed.  The account may be locked, the password may have expired,
or the account credentials may have changed.

────────────────────────────────────────────────────────────────
ACCOUNT DETAILS
────────────────────────────────────────────────────────────────
  Demo account   : {self.username}
  Region         : {self.region}
  Country        : {self.country}
  Language       : {self.language}
  Account type   : {self.account_type}
  Detected at    : {timestamp}

────────────────────────────────────────────────────────────────
WHAT HAPPENED
────────────────────────────────────────────────────────────────
After submitting the Okta login form, the portal did NOT navigate
past the login page — the page title remained the same as before
the submit.  This almost always indicates one of the following:

  1. The password is incorrect or has expired.
  2. The account has been locked after repeated failures.
  3. The account is disabled or deprovisioned.
  4. Okta or the portal is enforcing an additional MFA step that
     the automation cannot handle.

────────────────────────────────────────────────────────────────
ACTION REQUIRED
────────────────────────────────────────────────────────────────
Please verify the credentials above and unlock / reset the account
as needed, then run the pipeline again for this account.

This account was skipped for the current run; all other accounts
continued normally.

Thanks,
Albert Automation
""",
        ]

        self.lang_errmsg = [
            # Subject
            f"[Albert Automation] ✅  Preferred language updated for {self.username}",
            # Body
            f"""Hello,

Albert Automation detected that the display language for the demo
account below did not match the required language for its assigned
region, and has automatically updated it in the portal's personal-
details settings.

────────────────────────────────────────────────────────────────
ACCOUNT DETAILS
────────────────────────────────────────────────────────────────
  Demo account        : {self.username}
  Region              : {self.region}
  Country             : {self.country}
  Required language   : {self.language}
  Account type        : {self.account_type}
  Updated at          : {timestamp}

────────────────────────────────────────────────────────────────
WHAT ALBERT DID
────────────────────────────────────────────────────────────────
  1. Opened the Settings → Personal Details page for the account.
  2. Selected country       : {self.country}
  3. Selected language      : {self.language}
  4. Auto-filled the required job title and contact fields.
  5. Saved the profile and confirmed the success dialog.
  6. Called the portal's update-language endpoint to lock the
     preference into the user's session.

────────────────────────────────────────────────────────────────
NO ACTION REQUIRED
────────────────────────────────────────────────────────────────
This message is for visibility only.  The pipeline is continuing
for this account using the newly-set language.  Downstream reports
(translation, broken links, new-tab, etc.) should now appear in
the correct language.

Thanks,
Albert Automation
""",
        ]

        # ── Playwright handles ────────────────────────────────────────
        # Naming matches the other modules so downstream code can reuse
        # the same attribute names after rename.
        self._playwright   = None
        self._browser      = None
        self._session_page = None

        # ── Login state trackers ──────────────────────────────────────
        self.login_title = None   # Initialized (removes fragile hasattr check)
        self.disp_lang   = None

        # ---- Backwards-compat aliases ----
        # Downstream callers that still read prp_login.playwright /
        # .browser / .page can find the same objects here.  These are
        # populated inside setup() and cleared inside teardown().
        self.playwright = None
        self.browser    = None
        self.page       = None

    # ------------------------------------------------------------------
    # 2.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """
        Launch Playwright and the shared session page.

        Removed the original 90-second wait_for_load_state("networkidle")
        on the blank page — it had no URL, no network activity, and could
        block for the full timeout on some Chromium versions.
        """
        self._playwright   = sync_playwright().start()
        self._browser      = self._playwright.chromium.launch(headless=False)
        self._session_page = self._browser.new_page()
        self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)

        # Populate backwards-compat aliases
        self.playwright = self._playwright
        self.browser    = self._browser
        self.page       = self._session_page

        print(f"✅ Browser launched for {self.username}", flush=True)

    def teardown(self) -> None:
        """Close Playwright resources in reverse order of creation."""
        try:
            if self._session_page is not None:
                self._session_page.close()
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
        self._browser      = None
        self._playwright   = None
        self.playwright    = None
        self.browser       = None
        self.page          = None

        print(f"🧹 Browser closed for {self.username}", flush=True)

    # ------------------------------------------------------------------
    # 2.4  Email (via SMTP; no more Outlook dependency)
    # ------------------------------------------------------------------

    def email(self, errmsg) -> None:
        """
        Send a notification email via the SMTP utility.

        errmsg: [subject, body]

        Email is best-effort: any failure (SMTP unreachable, recipients
        file missing, send failure) is logged but never re-raised, so it
        can't break the login pipeline.
        """
        if not _SMTP_AVAILABLE:
            print(f"📧 (skipped — SMTP not available) would have sent: {errmsg[0]}",
                  flush=True)
            return

        try:
            subject, body = errmsg[0], errmsg[1]
            to_recipients, cc_recipients = _smtp_get_recipients()
            _smtp_send_email(
                subject=subject,
                body=body,
                to_recipient=to_recipients,
                cc_recipient=cc_recipients,
            )
            print(f"📧 Email sent: {subject}", flush=True)
        except Exception as exc:
            print(f"⚠️  Email send failed ({exc}); continuing", flush=True)

    # ------------------------------------------------------------------
    # 2.5  Login flow
    # ------------------------------------------------------------------

    def _dismiss_cookie_banner(self) -> None:
        """
        Close the HPE cookie-consent banner if present.

        Why this matters: the banner lives at the bottom of the page
        but auto-scrolls into view on first render.  If we try to type
        into the username field while that scroll is happening, the
        page moves mid-typing — characters get dropped, focus shifts,
        and only the first letter (e.g. "m") ends up in the field.
        Dismissing the banner BEFORE touching the form keeps the page
        stationary.

        Tries "Accept all" first (the positive action); falls back to
        the X close button; silent if neither is present.
        """
        page = self._session_page

        # Multiple possible selectors for the banner — HPE has rotated
        # these over the years.  Try each until one works.
        accept_selectors = [
            "button:has-text('Accept all')",
            "button:has-text('Accept All')",
            "button:has-text('ACCEPT ALL')",
            "#onetrust-accept-btn-handler",          # OneTrust default
            ".cc-accept-all",                        # common class name
            "button[aria-label*='Accept']",
        ]
        close_selectors = [
            "button[aria-label='Close']",
            ".cookie-banner button.close",
            "#cookie-banner .close-icon",
        ]

        # Try accept-all first
        for sel in accept_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1_500):
                    btn.click(timeout=3_000)
                    print(f"🍪 Cookie banner: accepted via '{sel}'", flush=True)
                    page.wait_for_timeout(500)   # let the banner animate out
                    return
            except Exception:
                continue

        # Fall back to close (X) button
        for sel in close_selectors:
            try:
                btn = page.locator(sel).first
                if btn.is_visible(timeout=1_500):
                    btn.click(timeout=3_000)
                    print(f"🍪 Cookie banner: closed via '{sel}'", flush=True)
                    page.wait_for_timeout(500)
                    return
            except Exception:
                continue

        # Not present — fine, continue silently.  No log spam.

    def _load_home_page(self) -> None:
        """
        Navigate to the portal home and complete the Okta two-step login.
        Internal helper — called from login().
        """
        page = self._session_page

        try:
            page.goto(self.BASE_URL, wait_until="domcontentloaded",
                      timeout=LOGIN_NAV_TIMEOUT_MS)
        except Exception as exc:
            print(f"⚠️ Home page navigation warning: {exc}", flush=True)
            time.sleep(3)

        # STEP 1: Dismiss the cookie banner before anything else.
        # If we skip this, the banner's auto-scroll moves the page
        # mid-typing and characters get dropped (observed symptom:
        # only the first letter "m" gets typed before the field
        # loses focus).
        self._dismiss_cookie_banner()

        # STEP 2: Username.
        #
        # IMPORTANT: use press_sequentially() (or page.type()) with a
        # real inter-key delay, NOT page.fill().  Okta's submit button
        # is gated by JavaScript that listens for keydown/keyup events
        # to mark the form as "user-interacted" — page.fill() sets the
        # value in one shot and fires only a synthetic `input` event,
        # which the framework treats as non-user input.  The submit
        # button then stays disabled and the click silently no-ops.
        #
        # We also click() the field before typing to guarantee focus.
        # Without this, focus can be stolen by background elements
        # (cookie banner, analytics scripts, late-loading widgets) and
        # only the first one or two characters make it in.
        page.wait_for_selector("#oktaEmailInput", state="visible", timeout=30_000)
        email_field = page.locator("#oktaEmailInput")

        # Scroll field into view and clear any stray state, then focus
        try:
            email_field.scroll_into_view_if_needed(timeout=5_000)
        except Exception:
            pass
        try:
            email_field.click(timeout=5_000)
        except Exception:
            pass

        # Clear just in case — fill('') is safe for emptying
        try:
            email_field.fill("")
        except Exception:
            pass

        # Type with per-character delay — Okta needs real keystrokes
        email_field.press_sequentially(self.username, delay=50)

        self.login_title = page.title()
        page.click("#oktaSignInBtn")

        # STEP 3: Password.  Same reasoning — same widget, same validator.
        page.wait_for_selector("#password-sign-in", state="visible", timeout=30_000)
        password_field = page.locator("#password-sign-in")
        try:
            password_field.click(timeout=5_000)
        except Exception:
            pass
        try:
            password_field.fill("")
        except Exception:
            pass
        password_field.press_sequentially(self.password, delay=50)
        page.click("#onepass-submit-btn")

        try:
            page.wait_for_load_state("domcontentloaded", timeout=POST_LOGIN_WAIT_MS)
        except Exception as exc:
            print(f"⚠️ Post-login load warning: {exc}", flush=True)
            time.sleep(5)

    @log_login_metric
    def login(self) -> bool:
        """
        Full login flow: navigate home → Okta → set country → settings page
        → detect language → change language if needed.

        Returns True on success, False if the login title didn't change
        (i.e. we're still on the Okta screen — login failed).
        """
        self._load_home_page()
        page = self._session_page

        # Country selection via the eyeball overlay
        current_country = self.set_country()

        # Critical stabilisation pause after country selection —
        # the portal triggers session rebuild + redirect.
        print("⏳ Stabilizing after country selection...", flush=True)
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception as exc:
            print(f"⚠️ Stabilization warning: {exc}", flush=True)
        time.sleep(5)

        # Navigate to Settings
        self._open_settings_page(page)
        try:
            page.wait_for_url("**/settings*", wait_until="domcontentloaded",
                              timeout=SETTINGS_NAV_TIMEOUT)
        except Exception as exc:
            print(f"Settings page URL check warning: {exc}", flush=True)

        new_title = page.title()

        # Login-failure detection: if the page title never changed from
        # the initial Okta screen, credentials were rejected.
        if self.login_title is not None and self.login_title == new_title:
            print(f"DEMO ACCOUNT FAILED: {self.username}", flush=True)
            self.email(self.login_errmsg)   # email() is best-effort
            return False

        # Detect display language + decide if we need to change it
        self.disp_lang = self._detect_lang()

        self.current_date  = self.current_datetime.date()
        self.current_month = self.current_date.strftime("%B")
        self.current_time  = self.current_datetime.strftime("%H:%M:%S")

        if self.disp_lang != self.language:
            self._change_lang()

        return True

    # ------------------------------------------------------------------
    # 2.6  Country / overlay management
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

    def set_country(self) -> str:
        """
        Close overlay, ensure the portal's country is set to self.country,
        and return the previously-displayed country name.

        Preserves the original 6-step flow exactly — only print-flushing
        and minor defensive tweaks changed.
        """
        page = self._session_page

        # --- STEP 1: Dismiss notification overlay ---
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=10_000)
            if overlay and overlay.is_visible():
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
            print("✅ No overlay appeared, continuing.", flush=True)
        except Exception as exc:
            print(f"⚠️ Overlay handling error: {exc}", flush=True)

        # --- STEP 2: Click Eyeball icon ---
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
            print(f"🌍 Current Country: {current_country or 'Unknown'}", flush=True)
        except Exception as exc:
            current_country = ""
            print(f"⚠️ Could not detect current country: {exc}", flush=True)

        # --- STEP 4: Open country dropdown ---
        try:
            loc_btn = page.wait_for_selector("#Otherlocations > span.MHMGparty",
                                             state="visible", timeout=15_000)
            if loc_btn:
                loc_btn.click()
                time.sleep(1)
        except Exception as exc:
            print(f"⚠️ Country dropdown error: {exc}", flush=True)

        # --- STEP 5: Wait for country list ---
        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist",
                                   state="visible", timeout=20_000)
        except Exception as exc:
            print(f"⚠️ Country list not loaded: {exc}", flush=True)

        # --- STEP 6: Switch country if needed ---
        try:
            if current_country.lower() == self.country.lower():
                print(f"✅ Country already set to '{current_country}'", flush=True)
            else:
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

                    print(f"🌐 Country dynamically matched → '{best_name}' "
                          f"(score={best_score:.2f})", flush=True)

                    time.sleep(2)
                    br_container = page.wait_for_selector(
                        "#MHMGBRLIst > li > div > div",
                        state="visible",
                        timeout=15_000,
                    )
                    if br_container:
                        br_container.click()
                        print("⏳ Waiting for country change to complete...", flush=True)
                        try:
                            page.wait_for_load_state("domcontentloaded", timeout=30_000)
                        except Exception as exc:
                            print(f"⚠️ Country change load warning: {exc}", flush=True)
                        time.sleep(5)
                        print("✅ Country change completed", flush=True)
                else:
                    print(f"⚠️ No strong dynamic match for '{self.country}'. "
                          f"Best score={best_score:.2f}", flush=True)

        except Exception as exc:
            print(f"⚠️ Country switching error: {exc}", flush=True)

        return current_country

    # ------------------------------------------------------------------
    # 2.7  Display-language detection
    # ------------------------------------------------------------------

    def _detect_lang(self) -> str:
        """Read the <html lang="…"> attribute and map it to the display name."""
        html = self._session_page.content()
        soup = BeautifulSoup(html, "html.parser")
        attr = soup.html.get("lang") if soup.html else None
        disp_lang = self.HTML_LANG_TO_LABEL.get(attr)
        print(f"DISPLAY LANGUAGE: {disp_lang}  PREFERRED: {self.language}", flush=True)
        return disp_lang

    # ------------------------------------------------------------------
    # 2.8  Language-change helpers — selector IDs are portal-specific
    # ------------------------------------------------------------------

    def _open_settings_page(self, page) -> None:
        """
        Navigate to the Settings page.

        OPTIMIZATION: cumulative timeouts trimmed from ~240 s to ~45 s
        (original values were extreme and blocked on networkidle which
        rarely fires on this portal).
        """
        print("📄 Navigating to settings page...", flush=True)
        print(f"Current URL before navigation: {page.url}", flush=True)

        try:
            page.goto(
                "https://partner.hpe.com/group/prp/settings",
                wait_until="commit",
                timeout=SETTINGS_NAV_TIMEOUT,
            )
            print("✅ Navigation committed", flush=True)
        except Exception as exc:
            print(f"⚠️ Navigation error (may be normal for redirects): {exc}",
                  flush=True)

        time.sleep(3)

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception as exc:
            print(f"⚠️ DOM load warning: {exc}", flush=True)

        final_url = page.url
        print(f"Final URL: {final_url}", flush=True)

        if "settings" in final_url.lower():
            print("✅ Successfully navigated to settings page", flush=True)
        else:
            print(f"⚠️ May not be on settings page. Current URL: {final_url}",
                  flush=True)

    def _select_country_in_form(self, page) -> None:
        """
        Select country in the Settings form.

        After selecting, the portal's JavaScript repopulates the
        preferred-language dropdown because available languages depend
        on the country.  We wait a beat so that AJAX finishes before
        _select_language_in_form() tries to use the new options.

        DEFENSIVE: fails loudly if self.country isn't in COUNTRY_MAP.
        Previously this would silently pass iso_value=None to
        page.select_option(), which either errored or selected the
        placeholder — leading to the 'Enter a valid country' validation
        error downstream.
        """
        iso_value = self.COUNTRY_MAP.get(self.country)
        if not iso_value:
            available = ", ".join(sorted(self.COUNTRY_MAP.keys()))
            raise RuntimeError(
                f"Country '{self.country}' is not in COUNTRY_MAP. "
                f"Add it to module_login_lang.PRP.COUNTRY_MAP with the "
                f"2-letter ISO code.  Available keys: {available}"
            )

        selector = ("#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_"
                    "INSTANCE_WIWF7MxPXFUm_country")
        page.wait_for_selector(selector, state="visible", timeout=30_000)
        page.select_option(selector, iso_value)

        # Also dispatch 'change' and 'blur' events explicitly.  The portal's
        # validation runs on blur; without the explicit blur the field
        # sometimes stays in its pre-existing error state even though the
        # value is now correct.  This is what caused the 'Geçerli bir ülke
        # girin' error with country TR already selected.
        page.evaluate(
            f"""() => {{
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.value = '{iso_value}';
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('blur',   {{ bubbles: true }}));
                }}
            }}"""
        )

        # Capture a snapshot of the language dropdown's option count
        # BEFORE waiting — we'll use it to detect that the dropdown has
        # been rebuilt, not just left as-is.
        lang_selector = ("#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_"
                         "INSTANCE_WIWF7MxPXFUm_preferredLanguage")
        try:
            page.wait_for_load_state("domcontentloaded", timeout=10_000)
        except Exception:
            pass

        # Give the country-change AJAX time to repopulate the language
        # list.  3 seconds is empirically reliable on this portal —
        # shorter values risk a race where select_option runs against
        # the stale (or emptied) dropdown.
        time.sleep(3)

        # Wait for the language dropdown to be populated with at least
        # one real option beyond the "Selezionare la lingua" placeholder.
        try:
            page.wait_for_function(
                f"document.querySelector('{lang_selector}') && "
                f"document.querySelector('{lang_selector}').options.length > 1",
                timeout=15_000,
            )
        except Exception as exc:
            print(f"⚠️ Language dropdown never populated after country change: {exc}",
                  flush=True)

        # Verify the country selection actually stuck (field-error class
        # gone, value still correct).  If it didn't, log the failure
        # state so diagnosis is easy.
        try:
            state = page.evaluate(
                f"""() => {{
                    const el = document.querySelector('{selector}');
                    if (!el) return {{ ok: false, reason: 'select not found' }};
                    const wrapper = el.closest('.form-group');
                    return {{
                        ok: el.value === '{iso_value}',
                        actual_value: el.value,
                        field_error: wrapper ? wrapper.classList.contains('field-error') : null,
                    }};
                }}"""
            )
            if not state.get("ok"):
                print(f"⚠️ Country selection didn't stick. State: {state}", flush=True)
            elif state.get("field_error"):
                print(f"⚠️ Country value is correct but field-error class is still "
                      f"applied.  Dispatching blur again.", flush=True)
                page.evaluate(
                    f"document.querySelector('{selector}')"
                    f".dispatchEvent(new Event('blur', {{ bubbles: true }}))"
                )
        except Exception:
            pass

        print(f"Country selected: {self.country} ({iso_value})", flush=True)

    def _select_language_in_form(self, page, value: str) -> None:
        """
        Select the preferred language in the Settings form.

        CRITICAL BEHAVIOUR:
          - The language dropdown is rebuilt by JavaScript when the
            country changes, and the available values depend on the
            country (e.g. for "Corea (Rep.)" only EN and KO appear).
          - Browser selection can silently fail if:
              (a) the target option hasn't been added yet (race with
                  the country-change AJAX), or
              (b) another late-firing AJAX overwrites the selection
                  after we set it.
          - So we: wait for the target option to exist → select it →
            read the value back → retry once if it didn't stick.
        """
        lang_selector = ("#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_"
                         "INSTANCE_WIWF7MxPXFUm_preferredLanguage")
        page.wait_for_selector(lang_selector, state="visible", timeout=30_000)

        # Wait for the specific option value we need to exist in the
        # dropdown.  This protects against the case where the dropdown
        # repopulates in stages (placeholder → full list).
        try:
            page.wait_for_function(
                f"""() => {{
                    const sel = document.querySelector('{lang_selector}');
                    if (!sel) return false;
                    return Array.from(sel.options).some(o => o.value === '{value}');
                }}""",
                timeout=15_000,
            )
        except Exception as exc:
            # Log the available options so we can diagnose if the value
            # we're trying to set isn't among them for this country.
            try:
                options = page.evaluate(
                    f"""() => Array.from(
                        document.querySelectorAll('{lang_selector} option')
                    ).map(o => o.value + ':' + o.text)"""
                )
                print(f"⚠️ Target language value '{value}' not in dropdown. "
                      f"Available options: {options}", flush=True)
            except Exception:
                pass
            raise RuntimeError(
                f"Language '{self.language}' (value='{value}') is not "
                f"available for country '{self.country}'.  "
                f"The portal doesn't offer this combination."
            )

        # First attempt
        page.select_option(lang_selector, value=value)
        time.sleep(1)

        # Verify the selection actually stuck.  If another AJAX fires
        # and wipes our choice, the select's value reverts to "".
        actual = page.evaluate(
            f"document.querySelector('{lang_selector}').value"
        )

        if actual != value:
            print(f"⚠️ Language selection didn't stick (got '{actual}', "
                  f"wanted '{value}').  Retrying…", flush=True)
            time.sleep(2)   # let any late AJAX finish first

            page.select_option(lang_selector, value=value)

            # Also dispatch the change event manually, in case the
            # framework's listener bailed out on the first attempt.
            page.evaluate(
                f"""() => {{
                    const sel = document.querySelector('{lang_selector}');
                    sel.value = '{value}';
                    sel.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}"""
            )
            time.sleep(1)

            actual = page.evaluate(
                f"document.querySelector('{lang_selector}').value"
            )
            if actual != value:
                raise RuntimeError(
                    f"Language selection refuses to stick even after retry. "
                    f"Wanted '{value}', dropdown shows '{actual}'."
                )

        print(f"✔ Language selected: {self.language} (value={value})", flush=True)

    def _select_job_title_in_form(self, page) -> None:
        title_selector = ("#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_"
                          "INSTANCE_WIWF7MxPXFUm_title")
        page.wait_for_selector(title_selector, state="visible", timeout=30_000)

        try:
            page.wait_for_function(
                f"document.querySelector('{title_selector}').options.length > 1",
                timeout=10_000,
            )
            first_option = page.locator(
                f"{title_selector} option[value]:not([value=''])"
            ).first
            first_option.wait_for(state="attached", timeout=10_000)
            first_value = first_option.get_attribute("value")

            page.select_option(title_selector, value=first_value)
            time.sleep(0.5)
            print(f"✔ Job Title selected: {first_value}", flush=True)
        except Exception as exc:
            print(f"⚠️ Error selecting job title, trying fallback: {exc}",
                  flush=True)
            page.select_option(title_selector, index=1)
            time.sleep(0.5)
            print("✔ Job Title selected (fallback method)", flush=True)

    def _fill_phone_in_form(self, page) -> None:
        phone_selector = ("#_com_hpe_prp_opr_personal_details_OprPersonalDetailsPortlet_"
                          "INSTANCE_WIWF7MxPXFUm_workNumber")
        phone = page.locator(phone_selector)
        phone.wait_for(state="visible", timeout=30_000)
        phone.scroll_into_view_if_needed()
        time.sleep(0.5)
        phone.fill("88888866666")
        time.sleep(0.5)
        print("✔ Work Number entered", flush=True)

    def _save_profile_form(self, page) -> None:
        save_btn = page.locator("#personal-save-personal-cancel")
        save_btn.wait_for(state="visible", timeout=30_000)
        save_btn.scroll_into_view_if_needed()
        time.sleep(0.5)
        save_btn.click(force=True)
        print("✔ SAVE clicked", flush=True)

        popup = page.locator(".settings-warningModal-content")
        try:
            popup.wait_for(state="visible", timeout=30_000)
            print("✔ Success popup appeared", flush=True)
        except Exception:
            popup = page.locator(".modal-content")
            popup.wait_for(state="visible", timeout=10_000)
            print("✔ Success popup appeared (alternate selector)", flush=True)

        time.sleep(1)

        close_btn = page.locator(".modal-footer button")
        close_btn.wait_for(state="visible", timeout=10_000)
        close_btn.click(force=True)
        print("✔ Success popup closed", flush=True)

        try:
            popup.wait_for(state="hidden", timeout=10_000)
        except Exception:
            pass
        try:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception:
            pass

    def _apply_language_update(self, page, lang_code: str) -> None:
        """Hit the update-language endpoint to lock in the preference."""
        update_url = (
            "https://partner.hpe.com/c/portal/update_language?"
            f"p_l_id=493064269&redirect=%2Fgroup%2Fprp%2Fsettings&"
            f"languageId={lang_code}&persistState=false&"
            "showUserLocaleOptionsMessage=false"
        )
        try:
            page.goto(update_url, wait_until="domcontentloaded",
                      timeout=LOGIN_NAV_TIMEOUT_MS)
        except Exception as exc:
            print(f"⚠️ Language update navigation warning: {exc}", flush=True)
            time.sleep(3)

        try:
            page.wait_for_load_state("domcontentloaded", timeout=30_000)
        except Exception as exc:
            print(f"⚠️ Language page load warning: {exc}", flush=True)

        print("✔ Language updated", flush=True)

    @log_language_metric
    def _change_lang(self) -> None:
        """
        Execute the full language-change flow: country → language → job title
        → phone → save → update-language endpoint → notification email.

        Method name preserved because @log_language_metric identifies it
        by name.
        """
        page = self._session_page
        try:
            value     = self.LANG_VALUE_MAP.get(self.language)
            lang_code = self.LANG_CODE_MAP.get(self.language)

            self._select_country_in_form(page)
            self._select_language_in_form(page, value)
            self._select_job_title_in_form(page)
            self._fill_phone_in_form(page)
            self._save_profile_form(page)

            print(f"Changing language → {self.language} ({lang_code})", flush=True)
            self._apply_language_update(page, lang_code)

            self.email(self.lang_errmsg)   # best-effort

        except Exception as exc:
            print(f"ERROR in _change_lang: {exc}", flush=True)


# ===========================================================================
# SECTION 3 – RUNNER
# ===========================================================================

def run_account(account):
    """
    Entry point for a single account.  Wraps teardown in try/finally so
    browsers are never stranded on errors, and re-applies unbuffered
    stdout inside the worker process.
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
        prp.login()
        print(f"Finished: {account[0]}", flush=True)
    except Exception as exc:
        print(f"Error: {account[0]} → {exc}", flush=True)
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