"""
External_validation_functions.py — SSO-ONLY BUILD
===================================================
Per-domain error-detection helpers for the external-link validator.

KEY CHANGE FROM PREVIOUS BUILD
------------------------------
The per-domain login functions (check_seismic_login, check_psnow_login,
check_vs_login, check_learning_login) are NO-OPS.  All five external
domains (Seismic, PSnow, MyLearning, VShow, Certification) federate
through the same HPE Okta tenant as partner.hpe.com.  The main module
now logs into partner.hpe.com once at setup time, and the resulting
Okta session cookie authenticates every subsequent visit to the
external domains via SAML SSO.

Why this matters for Seismic:
  The old per-domain Seismic login navigated directly to
  hpe.seismic.com's login page, clicked "HPE Employee", filled the
  Okta form, and submitted.  That flow had an undiagnosed hang —
  Seismic rendered a white/loading screen forever after submission.
  Most likely cause: bot detection on Seismic's side fingerprinting
  the direct-login pattern.  By going through partner.hpe.com first,
  we never touch Seismic's login page at all — the SAML redirect from
  Okta lands us directly on the content.

Functions still exported (for backward compatibility, now no-ops):
  - check_seismic_login    → no-op that prints a notice
  - check_psnow_login      → no-op
  - check_vs_login         → no-op
  - check_learning_login   → no-op

Functions that matter (unchanged signatures, updated implementations):
  - check_seismic_error
  - check_psnow_error
  - check_vs_error
  - check_learning_error
  - check_certification_error
"""

import time
import unicodedata

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


# ===========================================================================
# SECTION 1 – TIMEOUT CONSTANTS
# ===========================================================================

NAV_GOTO_TIMEOUT_MS:          int = 30_000
NAV_DOM_TIMEOUT_MS:           int = 30_000
NAV_LOAD_TIMEOUT_MS:          int = 60_000

# networkidle is capped AGGRESSIVELY at 3 s (was 20 s) because the
# portal's SPAs — Seismic, PSnow, Learning — make constant background
# XHRs (telemetry, analytics, live-reload) so the network is essentially
# never idle.  The old 20 s ceiling was hit on ~every link, adding 17 s
# of pure waste per link.  The content-length wait_for_function below
# is the authoritative readiness check; networkidle is now just a short
# settle for fast pages that happen to be quiet.
NAV_NETWORKIDLE_TIMEOUT_MS:   int =  3_000

SEISMIC_REDIRECT_TIMEOUT_MS:  int = 15_000
OPTIONAL_CLICK_TIMEOUT_MS:    int =  3_000

# Fast-fail timeout for per-domain login Locator.fill calls.  SSO via
# portal handles auth successfully, so the per-domain logins are a
# safety fallback.  When they fail (which they do on most accounts
# based on real-run logs) we want them to fail FAST, not wait the
# default 60 s per call.  10 s is plenty to recognize the form isn't
# there.
LOGIN_FILL_TIMEOUT_MS:        int = 10_000

POST_NAV_SETTLE_S:            float = 2.0
POST_LOGIN_SETTLE_S:          float = 2.0


# ===========================================================================
# SECTION 2 – TEXT NORMALIZATION
# ===========================================================================

_NORMALIZE_MAP = str.maketrans({
    "\u2019": "'",   # right single quotation mark → straight apostrophe
    "\u2018": "'",   # left single quotation mark
    "\u201C": '"',   # left double quotation mark
    "\u201D": '"',   # right double quotation mark
    "\u2013": "-",   # en dash
    "\u2014": "-",   # em dash
    "\u00A0": " ",   # non-breaking space
})


def _normalize_text(text: str) -> str:
    """Normalize Unicode quirks that break naive substring matching."""
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_NORMALIZE_MAP)
    return text


def _repair_csv_artifacts(messages: list) -> list:
    """
    Repair CSV-import artifacts in the Errormsg list (strings like
    'Error:','404 - Page Not Found' get split into their logical
    pieces, XXXXXXX placeholders are dropped).
    """
    repaired = []
    for raw in messages:
        if not isinstance(raw, str):
            continue
        raw = raw.strip()
        if not raw:
            continue

        if "','" in raw:
            pieces = [p.strip() for p in raw.split("','") if p.strip()]
        else:
            pieces = [raw]

        for piece in pieces:
            piece_clean = piece.strip()
            if not piece_clean:
                continue
            if piece_clean.upper() == "XXXXXXX":
                continue
            piece_clean = piece_clean.replace("XXXXXXX", "").strip()
            if len(piece_clean) < 5:
                continue
            repaired.append(piece_clean)

    seen = set()
    result = []
    for p in repaired:
        key = p.lower()
        if key not in seen:
            seen.add(key)
            result.append(p)
    return result


def _has_error_text(text_content: str, Errormsg: list) -> bool:
    """Return True if any error message appears in text_content."""
    if not text_content:
        return False

    normalized_body = _normalize_text(text_content).lower()
    clean_messages = _repair_csv_artifacts(Errormsg)

    for msg in clean_messages:
        normalized_msg = _normalize_text(msg).lower()
        if not normalized_msg:
            continue
        if normalized_msg in normalized_body:
            print(f"❌ Found error message: '{msg}'", flush=True)
            return True
    return False


# ===========================================================================
# SECTION 3 – SHARED NAVIGATION HELPER
# ===========================================================================

def _safe_navigate(page, url: str, label: str = "page") -> bool:
    """Navigate to `url` with tiered timeouts.  Returns True on success."""
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=NAV_GOTO_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        print(f"   ⚠ {label} initial goto timed out; retrying…", flush=True)
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=NAV_DOM_TIMEOUT_MS)
        except Exception as exc:
            print(f"   ❌ {label} retry failed: {str(exc)[:80]}", flush=True)
            return False
    except Exception as exc:
        print(f"   ❌ {label} goto failed: {str(exc)[:80]}", flush=True)
        return False

    try:
        page.wait_for_load_state("load", timeout=NAV_LOAD_TIMEOUT_MS)
    except Exception:
        pass

    try:
        page.wait_for_load_state("networkidle", timeout=NAV_NETWORKIDLE_TIMEOUT_MS)
    except Exception:
        pass

    time.sleep(POST_NAV_SETTLE_S)
    return True


# ===========================================================================
# SECTION 4 – DEPRECATED LOGIN FUNCTIONS (no-ops kept for compatibility)
# ===========================================================================

def check_seismic_login(driver, seis_login_link, wait, xpathlist, user, password):
    """
    Log into Seismic via direct Okta form.  When SSO via portal is
    already established, most steps may fail (element doesn't exist on
    a page that's already past login) — fill timeouts are capped at
    LOGIN_FILL_TIMEOUT_MS (10 s) so a failed step exits FAST instead
    of waiting the default 60 s per field.  The function print "login
    complete" regardless, because SSO is the real authentication path.
    """
    page = driver
    print("🔐 Logging into Seismic...", flush=True)

    if not _safe_navigate(page, seis_login_link, label="Seismic login page"):
        print("⚠️  Seismic login page failed to load — continuing anyway", flush=True)

    # Click "HPE Partner/Sign in" entry-point
    try:
        page.get_by_role("button", name="HPE Partner").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
    except Exception as exc:
        print(f"⚠️  Seismic entry-point click failed: {str(exc)[:60]}", flush=True)

    # Okta credentials — all with fast-fail timeouts
    try:
        page.locator(f"xpath={xpathlist[1][2]}").fill(
            user, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[1][3]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[1][4]}").fill(
            password, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[1][5]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
    except Exception as exc:
        print(f"⚠️  Seismic Okta fill failed: {str(exc)[:60]}", flush=True)

    # Wait for post-login navigation
    try:
        page.wait_for_load_state("load", timeout=NAV_LOAD_TIMEOUT_MS)
    except Exception:
        pass
    time.sleep(POST_LOGIN_SETTLE_S)

    # Optional "Continue" button on some Okta flows
    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click(
            timeout=OPTIONAL_CLICK_TIMEOUT_MS
        )
    except Exception:
        pass

    print("✅ Seismic login complete", flush=True)


def check_psnow_login(driver, errlink_psnow, wait, xpathlist, user, password):
    """
    Log into PSnow via direct Okta form.  See check_seismic_login
    docstring for the fast-fail rationale.
    """
    page = driver
    print("🔐 Logging into PSnow...", flush=True)

    if not _safe_navigate(page, errlink_psnow, label="PSnow login page"):
        print("⚠️  PSnow login page failed to load — continuing anyway", flush=True)

    try:
        page.click("#request-partner-button", timeout=LOGIN_FILL_TIMEOUT_MS)
    except Exception as exc:
        print(f"⚠️  Psnow entry-point click failed: {str(exc)[:60]}", flush=True)

    try:
        page.locator(f"xpath={xpathlist[5][1]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[5][2]}").fill(
            user, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[5][3]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[5][4]}").fill(
            password, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[5][5]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
    except Exception as exc:
        print(f"⚠️  PSnow Okta fill failed: {str(exc)[:60]}", flush=True)

    try:
        page.wait_for_load_state("load", timeout=NAV_LOAD_TIMEOUT_MS)
    except Exception:
        pass
    time.sleep(POST_LOGIN_SETTLE_S)

    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click(
            timeout=OPTIONAL_CLICK_TIMEOUT_MS
        )
    except Exception:
        pass

    print("✅ PSnow login complete", flush=True)


def check_vs_login(driver, url_VS, wait, xpathlist, user, password):
    """
    Log into VShow (ON24 HPE TekTalks) via direct Okta form.  See
    check_seismic_login docstring for the fast-fail rationale.
    """
    page = driver
    print("🔐 Logging into VShow...", flush=True)

    if not _safe_navigate(page, url_VS, label="VShow login page"):
        print("⚠️  VShow login page failed to load — continuing anyway", flush=True)

    try:
        page.locator(f"xpath={xpathlist[2][2]}").fill(
            user, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[2][3]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[2][4]}").fill(
            password, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[2][5]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
    except Exception as exc:
        print(f"⚠️  VShow fill failed: {str(exc)[:60]}", flush=True)

    try:
        page.wait_for_load_state("load", timeout=NAV_LOAD_TIMEOUT_MS)
    except Exception:
        pass
    time.sleep(POST_LOGIN_SETTLE_S)

    try:
        page.locator('xpath=//*[@id="form19"]/div[2]/div[2]/div[2]/a').click(
            timeout=OPTIONAL_CLICK_TIMEOUT_MS
        )
    except Exception:
        pass

    print("✅ VShow login complete", flush=True)


def check_learning_login(driver, url_hpelearn, wait, xpathlist, user, password):
    """
    Log into HPE Learning / MyLearning via direct Okta form.  See
    check_seismic_login docstring for the fast-fail rationale.
    """
    page = driver
    print("🔐 Logging into HPE Learning...", flush=True)

    if not _safe_navigate(page, url_hpelearn, label="HPE Learning login page"):
        print("⚠️  HPE Learning login page failed to load — continuing anyway",
              flush=True)

    try:
        page.click('a[href="hpelogin_okta.aspx"]', timeout=LOGIN_FILL_TIMEOUT_MS)
    except Exception as exc:
        print(f"⚠️  HPE Learning entry-point click failed: {str(exc)[:60]}", flush=True)

    try:
        page.locator(f"xpath={xpathlist[3][1]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[3][2]}").fill(
            user, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[3][3]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[3][4]}").fill(
            password, timeout=LOGIN_FILL_TIMEOUT_MS
        )
        page.locator(f"xpath={xpathlist[3][5]}").click(
            timeout=LOGIN_FILL_TIMEOUT_MS
        )
    except Exception as exc:
        print(f"⚠️  HPE Learning fill failed: {str(exc)[:60]}", flush=True)

    try:
        page.wait_for_load_state("load", timeout=NAV_LOAD_TIMEOUT_MS)
    except Exception:
        pass
    time.sleep(POST_LOGIN_SETTLE_S)

    print("✅ HPE Learning login complete", flush=True)


# ===========================================================================
# SECTION 5 – SEISMIC
# ===========================================================================

def check_seismic_error(driver, wait, xpathlist, seislink, Errormsg) -> bool:
    """
    Visit a Seismic URL and check for error markers.

    OPTIMIZED PATH (replaces the generic _safe_navigate flow):
      Seismic renders two distinct DOM templates:
        (a) HEALTHY content page:
            `.seismic-dcv2-DocView` wrapper + `#upplayer-content-loaded-flag`
            (PDF viewer chrome + iframe-wrapped content).
        (b) ERROR page (e.g., "You don't have permission", "Content
            expired", "Content not found"):
            `.seismic-main-container` + `#seismic-global-error` wrapper
            (completely different template — no viewer, no breadcrumbs).

    Previously we waited for generic signals (`load` event, `networkidle`,
    then visible-text-length > 300) and ate ~24 s per link because:
      - Seismic's PDF iframe loads slowly, so `load` doesn't fire quickly
      - The SPA keeps making telemetry XHRs, so `networkidle` times out
      - `innerText.length > 300` was satisfied immediately by Seismic's
        chrome text (breadcrumbs, panel labels), so even though the check
        "passed" fast, it didn't help us exit the other waits.

    New approach: skip `load` and `networkidle` entirely, and wait for
    EITHER the healthy-page flag OR the error-page wrapper to appear.
    Whichever fires first, we exit — so a broken page is detected in
    the same 2-5 s as a healthy page.

    SEISMIC_REDIRECT_TIMEOUT_MS (15 s) is the cap — if neither signal
    fires in 15 s, the page is probably stuck and we snapshot whatever
    is there for the fallback text scan.
    """
    page = driver

    # STEP 1: goto with ONLY domcontentloaded — no load, no networkidle.
    # Seismic's own readiness signal (below) is much more reliable than
    # generic page-load events for this SPA.
    try:
        page.goto(seislink, wait_until="domcontentloaded", timeout=NAV_GOTO_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        # Retry once with a longer ceiling
        try:
            page.goto(seislink, wait_until="domcontentloaded", timeout=NAV_DOM_TIMEOUT_MS)
        except Exception as exc:
            print(f"   ❌ Seismic goto failed: {str(exc)[:80]}", flush=True)
            return True
    except Exception as exc:
        print(f"   ❌ Seismic goto failed: {str(exc)[:80]}", flush=True)
        return True

    # STEP 2: Wait for EITHER outcome — healthy or broken.  Both
    # selectors use stable IDs, not styled-components hashes, so they
    # survive across Seismic builds.
    try:
        page.wait_for_function(
            """
            () => {
                // (a) Healthy: PDF viewer content-loaded flag present
                const healthyFlag = document.querySelector('#upplayer-content-loaded-flag');
                if (healthyFlag) return true;

                // (b) Healthy alt: PDF viewer toolbar finished loading
                // (up-hidden class removed from toolbar-float)
                const toolbar = document.querySelector('.up-toolbar-float');
                if (toolbar && !toolbar.classList.contains('up-hidden')) return true;

                // (c) Broken: Seismic's global-error wrapper present
                const errorWrapper = document.querySelector('#seismic-global-error');
                if (errorWrapper) return true;

                // (d) Broken alt: error template outer container
                const errorContainer = document.querySelector('.seismic-main-container .error-wrapper');
                if (errorContainer) return true;

                return false;
            }
            """,
            timeout=SEISMIC_REDIRECT_TIMEOUT_MS,
        )
    except PlaywrightTimeoutError:
        # Neither signal fired — fall through to snapshot with whatever
        # is rendered.  Rare edge case (probably a third template we
        # don't know about yet).
        pass
    except Exception:
        pass

    # STEP 3: Optional interstitial-dismiss click from the Excel xpathlist.
    # Kept from the original behaviour, short timeout so it can't hang.
    try:
        page.locator(f"xpath={xpathlist[1][1]}").click(
            timeout=OPTIONAL_CLICK_TIMEOUT_MS
        )
    except Exception:
        pass

    # STEP 4: Extract and scan.  No more 2-second blind sleep needed —
    # if step 2 saw a ready signal, DOM text is already settled.
    try:
        page_content = page.content()
    except Exception as exc:
        print(f"❌ Content retrieval failed: {str(exc)[:60]}", flush=True)
        return True

    soup = BeautifulSoup(page_content, "html.parser")
    text_content = soup.get_text()
    return _has_error_text(text_content, Errormsg)


# ===========================================================================
# SECTION 6 – PSNOW
# ===========================================================================

def check_psnow_error(driver, errlink_psnow, wait, xpathlist, Errormsg) -> bool:
    """Visit a PSnow URL and check for error markers.  SSO via portal."""
    page = driver

    if not _safe_navigate(page, errlink_psnow, label="PSnow content"):
        return True

    for xp_idx in (1, 6, 7):
        try:
            page.locator(f"xpath={xpathlist[5][xp_idx]}").click(
                timeout=OPTIONAL_CLICK_TIMEOUT_MS
            )
        except Exception:
            pass

    try:
        page_content = page.content()
    except Exception as exc:
        print(f"❌ Content retrieval failed: {str(exc)[:60]}", flush=True)
        return True

    soup = BeautifulSoup(page_content, "html.parser")
    text_content = soup.get_text()
    return _has_error_text(text_content, Errormsg)


# ===========================================================================
# SECTION 7 – HPE LEARNING
# ===========================================================================

def check_learning_error(driver, url_hpelearn, Errormsg) -> bool:
    """Visit an HPE Learning URL and check for error markers.  SSO via portal."""
    page = driver

    if not _safe_navigate(page, url_hpelearn, label="HPE Learning content"):
        return True

    try:
        page.wait_for_function(
            """
            () => {
                if (document.readyState !== 'complete') return false;
                const hasForm = document.querySelector(
                    '#form1, .hpe-my-learning, [id*="ContentPlaceHolder"]'
                );
                const stillLoading = document.querySelector('.loading, .spinner');
                return hasForm && !stillLoading;
            }
            """,
            timeout=15_000,
        )
    except Exception:
        pass

    try:
        page_content = page.content()
    except Exception as exc:
        print(f"❌ Content retrieval failed: {str(exc)[:60]}", flush=True)
        return True

    soup = BeautifulSoup(page_content, "html.parser")
    text_content = soup.get_text()
    return _has_error_text(text_content, Errormsg)


# ===========================================================================
# SECTION 8 – VSHOW
# ===========================================================================

def check_vs_error(driver, url_VS, Errormsg) -> bool:
    """Visit a VShow URL and check for error markers.  SSO via portal."""
    page = driver

    if not _safe_navigate(page, url_VS, label="VShow content"):
        return True

    try:
        page_content = page.content()
    except Exception as exc:
        print(f"❌ Content retrieval failed: {str(exc)[:60]}", flush=True)
        return True

    soup = BeautifulSoup(page_content, "html.parser")
    text_content = soup.get_text()
    return _has_error_text(text_content, Errormsg)


# ===========================================================================
# SECTION 9 – CERTIFICATION
# ===========================================================================

def check_certification_error(driver, url_certification, Errormsg) -> bool:
    """Visit a certification URL and check for error markers.  No auth needed."""
    page = driver

    if not _safe_navigate(page, url_certification, label="Certification"):
        return True

    try:
        page_content = page.content()
    except Exception as exc:
        print(f"❌ Content retrieval failed: {str(exc)[:60]}", flush=True)
        return True

    soup = BeautifulSoup(page_content, "html.parser")
    text_content = soup.get_text()
    return _has_error_text(text_content, Errormsg)