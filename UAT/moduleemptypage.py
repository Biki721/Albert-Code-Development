"""
moduleemptypage.py — FP-REDUCED BUILD (v2: deployment-proof)
==============================================================
Detects "empty" pages — portal pages whose main content is nothing but
the default "Related content" placeholder, indicating the translation
team hasn't populated content for that region/language.

WHY THIS VERSION EXISTS
-----------------------
The previous v1 fix caught 72+ custom-search FPs on the Apr 18 Indonesian
run BUT required the caller to pass the Playwright `page` handle as a
5th argument.  The Apr 19 run still produced 19 FPs:

  - 18 custom-search URLs (/custom-search?keywords=...&cfp=true)
  - 1 article-display URL   (/article-display-page?id=NNNNNNN)

Root cause diagnosis:
  • Custom-search FPs — the v1 fix DOES work when `page` is passed.
    If 18 slipped through, the caller was either the old
    translation_phase3.py (which never passes `page`), or the fix
    module wasn't deployed.  v2 handles both cases safely.
  • Article-display FPs — v1 didn't cover this URL pattern.  Same
    failure mode: portal renders the chrome + "Related content"
    sidebar FIRST, loads the actual article via AJAX ~1–3 s later.
    The 3-line heuristic ran before the article body rendered.

v2 CHANGES
----------

1. EXPANDED DYNAMIC-URL LIST.
   Now recognizes:
     • /custom-search?...      (as before)
     • /article-display-page?  (NEW)
     • keywords= / cfp=true    (fallback markers)
     • /esm/-/link/            (defensive — slow-loading KB pages)

2. DEPLOYMENT-PROOF FALLBACK.
   If the URL is dynamic but the caller didn't pass `page` (old
   translation_phase3.py), the module returns "" (not empty) WITHOUT
   running the 3-line heuristic.  Rationale: the 3-line heuristic is
   known-unreliable on dynamic pages.  Better to miss a rare
   legitimately-empty dynamic page than to generate 18+ FPs per run.

3. GENERIC "HAS CONTENT" CHECK FOR DYNAMIC URLS.
   Instead of only looking for `.rdt_TableRow` (search-specific), v2
   uses three parallel signals, ANY of which suffices:
     (a) Search result row appears (stable: .rdt_TableBody .rdt_TableRow)
     (b) main-content innerText grows beyond the placeholder
         threshold (works for article pages, news pages, any dynamic
         content container)
     (c) A "no results found" message appears (zero-hit searches)
   First signal to fire wins → fast exit, no unnecessary 15s waits.

4. DIAGNOSTIC LOGGING.
   Every dynamic-URL decision prints one line with the outcome and
   which signal fired.  If v2 FPs persist, the console log will show
   exactly why.

5. NEVER FLAG DYNAMIC URLS.
   Concluded from v1 analysis: there's NO realistic case where a
   /custom-search or /article-display page should be flagged as
   empty.  Zero-hit searches are not empty (search works).  Slow
   loads are not empty (slow is not a translation bug).  Failed
   article loads show error templates, which `no_content_pg` catches
   at the orchestrator level.  So dynamic URLs simply bypass the
   empty-page check entirely in v2.

BEHAVIOUR SUMMARY (v2)
----------------------
  Dynamic URL + page provided  → run AJAX-aware wait for log/debug,
                                 return "" regardless (not empty) ✓
  Dynamic URL + no page        → return "" immediately (not empty) ✓
  Non-dynamic URL              → apply 3-line / zero-line heuristic ✓
  "Related content" only       → flagged as empty ✓

SIGNATURE PRESERVED
-------------------
emptypagecheck(link, phrase, default_phrase, soup, page=None)

Identical to v1.  Callers that pass `page` get diagnostic logging +
AJAX-aware inspection.  Callers that don't still get FP protection on
dynamic URLs.
"""

import sys

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# CRITICAL: unbuffered stdout so worker processes don't deadlock on the
# Windows console lock when they print under MAX_PARALLEL >= 2.
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
    sys.stderr.reconfigure(line_buffering=True, write_through=True)
except Exception:
    pass


# ===========================================================================
# SECTION 1 – TUNING
# ===========================================================================

# How long to wait for dynamic content before giving up and exiting
# with "not empty" anyway (we never flag a dynamic URL, the wait is
# purely diagnostic / to help the 3-line heuristic if it runs later).
DYNAMIC_CONTENT_TIMEOUT_MS: int = 15_000

# Poll interval while waiting for dynamic content signals.
DYNAMIC_POLL_INTERVAL_MS:   int = 500

# If main-content innerText is longer than this many characters, it's
# almost certainly loaded real content (beyond the "Related content"
# placeholder which is ~15 chars).
SUBSTANTIVE_CONTENT_CHARS:  int = 200

# URL fragments that identify a page with dynamic / AJAX-loaded
# content.  Presence of ANY of these in the link triggers the
# dynamic-URL bypass logic.  Order matters only for readability —
# matching is set-membership, any marker suffices.
DYNAMIC_URL_MARKERS: tuple = (
    # Custom-search — search-results portlet, AJAX-loaded table
    "/custom-search?",
    "/custom-search/",
    "cfp=true",
    "keywords=",
    # Article display — article body loaded via AJAX
    "/article-display-page?",
    "article-display-page?id=",
    # Defensive: the PRP also has /esm/-/link/ pages that load
    # slowly; the crawler already handles them via networkidle,
    # but include here as belt-and-suspenders.
    "/esm/-/link/",
)

# Stable selectors.  `rdt_` prefix = react-data-table-component public
# API, stable across portal rebuilds.
SELECTOR_RESULTS_TABLE_ROW: str = ".rdt_TableBody .rdt_TableRow"

# Indonesian / English no-results messages.  If visible in page body
# after AJAX, the search ran but matched nothing — NOT a translation bug.
NO_RESULTS_TEXT_MARKERS: tuple = (
    "tidak ada hasil",            # Indonesian: "no results"
    "tidak menemukan",            # Indonesian: "couldn't find"
    "no results found",           # English
    "no results match",
    "0 of 0",                     # pagination indicator
    "hiçbir sonuç bulunamadı",    # Turkish: "no results found"
    "nessun risultato",           # Italian: "no results"
    "keine ergebnisse",           # German: "no results"
    "aucun résultat",             # French: "no results"
)


# ===========================================================================
# SECTION 2 – PRIVATE HELPERS
# ===========================================================================

def _is_dynamic_url(link: str) -> bool:
    """
    Return True if `link` is a portal page with AJAX-loaded content
    that the 3-line heuristic can't reliably evaluate synchronously.
    """
    if not link:
        return False
    lower = link.lower()
    return any(marker in lower for marker in DYNAMIC_URL_MARKERS)


def _wait_for_dynamic_content(page, timeout_ms: int = DYNAMIC_CONTENT_TIMEOUT_MS) -> tuple:
    """
    Poll the page for up to `timeout_ms` looking for any of three
    content-ready signals:

      (a) A search-results row has rendered.
      (b) main-content innerText is longer than SUBSTANTIVE_CONTENT_CHARS.
      (c) A "no results" message is visible.

    Returns (signal_name, fired_at_ms) if any signal fires, else
    (None, timeout_ms).

    Used for diagnostic logging only — the caller does NOT gate on
    the result (dynamic URLs never flagged regardless).
    """
    import time as _time

    js_probe = """
    () => {
      // Signal A: search result row present?
      const row = document.querySelector('.rdt_TableBody .rdt_TableRow');
      if (row && row.offsetParent !== null) return { signal: 'result-row' };

      // Signal B: main-content text substantive?
      const mc = document.getElementById('main-content');
      if (mc) {
        const txt = (mc.innerText || '').trim();
        if (txt.length > %d) return { signal: 'main-content-grew', chars: txt.length };
      }

      // Signal C: visible "no results" marker?
      const body = (document.body.innerText || '').toLowerCase();
      const markers = %s;
      for (const m of markers) {
        if (body.includes(m)) return { signal: 'no-results-text' };
      }

      return null;
    }
    """ % (SUBSTANTIVE_CONTENT_CHARS, list(NO_RESULTS_TEXT_MARKERS))

    deadline  = _time.time() + (timeout_ms / 1000.0)
    start_ms  = _time.time() * 1000.0

    while _time.time() < deadline:
        try:
            result = page.evaluate(js_probe)
        except Exception:
            # Page navigation / disconnection mid-poll — stop polling.
            return (None, int(_time.time() * 1000.0 - start_ms))

        if result:
            elapsed = int(_time.time() * 1000.0 - start_ms)
            return (result.get("signal"), elapsed)

        try:
            page.wait_for_timeout(DYNAMIC_POLL_INTERVAL_MS)
        except Exception:
            return (None, int(_time.time() * 1000.0 - start_ms))

    return (None, timeout_ms)


# ===========================================================================
# SECTION 3 – PUBLIC API
# ===========================================================================

def emptypagecheck(link, phrase, default_phrase, soup, page=None):
    """
    Return `link` if the page is empty, '' otherwise.

    Signature unchanged from v1.  Callers that pass `page` get
    AJAX-aware inspection + diagnostic logging on dynamic URLs.
    Callers that don't still benefit from the deployment-proof bypass
    on dynamic URLs (no FPs).

    Detection rules:
      • Dynamic URL (/custom-search, /article-display-page, etc.) →
        NEVER flagged as empty.  If `page` is provided, we still wait
        for a content-loaded signal and log which signal fired (for
        audit).  If `page` is None, we return immediately.
      • Non-dynamic URL → 3-line heuristic (unchanged): if main-content
        has exactly 3 visible lines and line 1 is the "Related content"
        placeholder, flag as empty.  If main-content has 0 visible
        lines, also flag as empty.
    """
    # ------------------------------------------------------------------
    # STEP 1: Dynamic-URL bypass (v2 FP guard)
    # ------------------------------------------------------------------
    if _is_dynamic_url(link):
        if page is not None:
            # Diagnostic wait — find out WHICH signal fired (or none).
            # Does not affect the return value; dynamic URLs are never
            # flagged regardless.
            signal, elapsed_ms = _wait_for_dynamic_content(page)
            if signal:
                print(f"  [empty-page] dynamic URL OK ({signal} @ {elapsed_ms} ms): {link}",
                      flush=True)
            else:
                print(f"  [empty-page] dynamic URL, no content signal in "
                      f"{DYNAMIC_CONTENT_TIMEOUT_MS} ms — not flagged: {link}",
                      flush=True)
        else:
            # Old-signature caller (no page handle) — we can't
            # reliably check dynamic content without the page, so
            # suppress flagging to prevent FPs.  This is v2's
            # deployment-proof guarantee.
            print(f"  [empty-page] dynamic URL + no page handle — skipping: {link}",
                  flush=True)
        return ""

    # ------------------------------------------------------------------
    # STEP 2: 3-line / zero-line heuristic for static URLs (unchanged)
    # ------------------------------------------------------------------
    try:
        phrase_caught = soup.find(id="main-content").get_text()
    except Exception:
        phrase_caught = ""

    if phrase_caught != "":
        content = phrase_caught.splitlines()

        for i in range(len(content)):
            content[i] = " ".join(content[i].split())
        content = [line for line in content if line]

        if len(content) == 3:
            if content[0] == phrase or content[0] == default_phrase:
                return link
        elif len(content) == 0:
            return link

    return ""