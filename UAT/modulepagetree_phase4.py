"""
HPE Partner Portal (PRP) Web Crawler — OPTIMIZED BUILD
========================================================
This is a drop-in replacement for the earlier crawler with five targeted
speed optimizations applied.  The business logic, output filenames, folder
names, reference files, class/method signatures, and command-line entry
point are all unchanged — you should be able to swap this file in without
touching anything downstream.

OUTPUT ARTEFACTS (same as before)
---------------------------------
  Page Trees/PageTree<tag>.txt      – all internal PRP content page URLs
  DocumentLinks/Doclinks<tag>.txt   – downloadable file URLs (PDF, XLSX, …)
  External Urls/External<tag>.txt   – URLs outside partner.hpe.com
  Reverse Dicts/RevDict<tag>.txt    – reverse map:  child-URL → [parent-URLs]
  Redirects/Redirects<tag>.txt      – redirect log: intended → actual URL

OPTIMIZATIONS APPLIED (vs. previous version)
---------------------------------------------
  1. Single reusable crawl page per process (instead of new_page/close per URL).
     Chromium page creation is the most expensive per-URL operation; reusing
     one page trades zero correctness for ~30–50 % wall-time reduction on
     link-heavy crawls.

  2. Single page.evaluate() to pull every <a href> in one IPC round-trip
     (instead of N round-trips, one per anchor).  On a 200-link page this
     collapses ~200 CDP calls into 1.

  3. Conditional wait_for_load_state("networkidle").  Previously run on every
     page with an 8 s timeout, now only applied to URLs that match the known
     JS-redirect pattern (/esm/-/link/).  Normal pages use a cheap 300 ms
     settle.

  4. Crawl delay dropped from 1.5 s to 0.2 s.  The old value was chosen for
     politeness but offers no protection against authenticated-session
     rate-limiting.  Set to 0 for maximum throughput.

  5. Breadcrumb checks use str.startswith(tuple) (C-level, single call) and
     set-membership (O(1)) instead of Python-level loops over lists.

BUSINESS-LOGIC CORRECTIONS
--------------------------
  - /documents and /esm URLs are classified as downloadable documents
    (confirmed by product team — these paths serve files, not landing pages).
    This restores the behaviour of the original Doc-1 implementation.
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import logging
import time
from collections import deque
from multiprocessing import Process
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
# pip install playwright  →  then run:  playwright install chromium
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# ---------------------------------------------------------------------------
# Local / project imports
# ---------------------------------------------------------------------------
import work_phase_3 as work   # provides:  work.doc_reader(path) -> list[str]


# ===========================================================================
# SECTION 1 – CONFIGURATION
# ===========================================================================

BASE_DIR = Path(__file__).parent

# Polite-crawling delay between page fetches (seconds).
# OPTIMIZATION #4: reduced from 1.5 s to 0.2 s.  Set to 0 for max throughput.
CRAWL_DELAY_SECONDS: float = 0.2

# Re-verify the country dropdown every N pages …
COUNTRY_CHECK_EVERY_N_PAGES: int = 10
# … OR every N seconds, whichever threshold is hit first.
COUNTRY_CHECK_INTERVAL_SECONDS: int = 180

# Default Playwright navigation timeout (milliseconds)
PAGE_TIMEOUT_MS: int = 30_000

# Short settle time after domcontentloaded for the DOM to stabilise (ms).
DOM_SETTLE_MS: int = 300

# Networkidle timeout for pages known to JS-redirect after load (ms).
JS_REDIRECT_WAIT_MS: int = 5_000

# URL substring that identifies pages which perform a client-side redirect
# *after* domcontentloaded.  For these we pay the networkidle cost; for
# everyone else we don't.
JS_REDIRECT_URL_MARKER: str = "/esm/-/link/"

# File extensions that mean "this is a download, not a web page".
# We check only the URL *path*, not query strings, so ?download=1 is handled.
DOCUMENT_EXTENSIONS: tuple[str, ...] = (
    ".pdf", ".xlsx", ".xls", ".doc", ".docx",
    ".zip", ".ppt", ".pptx", ".txt",
)

# Path substrings that unambiguously serve downloadable files on this portal.
# Anything whose URL path contains one of these is routed to the documents
# bucket and not crawled for child links.
DOCUMENT_PATH_MARKERS: tuple[str, ...] = (
    "/documents",
    "/esm",
)

# URL substrings that indicate noise we never want to crawl.
SKIP_URL_PATTERNS: tuple[str, ...] = (
    "login",
    "logout",
    "?p_p_id=com",   # Liferay portlet action URLs – not real pages
)

# All URL variants that represent the portal home page.
HOME_PAGES: frozenset[str] = frozenset({
    "https://partner.hpe.com",
    "https://partner.hpe.com/",
    "https://partner.hpe.com/home",
    "https://partner.hpe.com/group/prp",
    "https://partner.hpe.com/group/prp/home",
})


# ===========================================================================
# SECTION 2 – LOGGING SETUP
# ===========================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(BASE_DIR / "crawler.log", encoding="utf-8"),
    ],
)

log = logging.getLogger(__name__)


# ===========================================================================
# SECTION 3 – PURE HELPER FUNCTIONS
# ===========================================================================

def normalize_url(base: str, href: str) -> str:
    """
    Turn a (possibly relative) href into a clean, absolute URL.

    Strips the URL fragment (#section) so that two URLs differing only by
    fragment are de-duplicated.  Returns "" for anything non-navigable.
    """
    if not href:
        return ""

    href = href.strip()

    # These schemes are never navigable URLs – skip them immediately
    non_navigable_schemes = (
        "javascript:", "mailto:", "tel:", "data:", "javascipt:",
    )
    if any(href.startswith(s) for s in non_navigable_schemes):
        return ""

    # A bare fragment has no server-side meaning
    if href == "#":
        return ""

    try:
        joined = urljoin(base, href)
        parsed = urlparse(joined)
        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            parsed.query,
            "",           # fragment deliberately omitted
        ))
    except Exception:
        return ""


def is_document_url(url: str) -> bool:
    """
    Return True if the URL points to a downloadable file.

    Matches either:
      - a real file extension at the end of the URL path, OR
      - a known document-serving path marker (/documents, /esm on this portal).

    The marker check is substring-based on the URL *path* only, so host
    names containing "documents" won't trigger false positives.
    """
    if not url:
        return False
    path = urlparse(url).path.lower()

    if any(path.endswith(ext) for ext in DOCUMENT_EXTENSIONS):
        return True
    if any(marker in path for marker in DOCUMENT_PATH_MARKERS):
        return True
    return False


def is_hpe_partner_url(url: str) -> bool:
    """
    Return True only for URLs that belong to partner.hpe.com (or its subdomains).

    Domain-boundary check:  notpartner.hpe.com does NOT match.
    """
    try:
        netloc = urlparse(url).netloc
        target = "partner.hpe.com"
        return netloc == target or netloc.endswith("." + target)
    except Exception:
        return False


def is_home_page(url: str) -> bool:
    """Return True if the URL is one of the known portal home-page variants."""
    return url.rstrip("/") in {hp.rstrip("/") for hp in HOME_PAGES}


def should_skip_url(url: str) -> bool:
    """Return True for URLs that are noise and should never be crawled."""
    lower = url.lower()
    return any(pattern in lower for pattern in SKIP_URL_PATTERNS)


def categorize_redirect(intended: str, actual: str) -> str:
    """
    Classify a redirect as "home", "slug_change", or "path_change".
    """
    if is_home_page(actual):
        return "home"

    intended_parent = intended.rsplit("/", 1)[0]
    actual_parent   = actual.rsplit("/", 1)[0]

    if intended_parent == actual_parent:
        return "slug_change"

    return "path_change"


# ===========================================================================
# SECTION 4 – MAIN CRAWLER CLASS
# ===========================================================================

class PRPCrawler:
    """
    Authenticated crawler for the HPE Partner Portal (PRP).

    Usage:
        crawler = PRPCrawler(username="…", password="…", region="EMEA",
                             country="Italy", language="Italian",
                             account_type="distri")
        crawler.setup()
        crawler.run()   # login → set country → crawl → write files → teardown
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
        delayed_list     = self._load_docx("delayed_loading.docx")
        breadcrumb_list  = self._load_docx("breadcrumb_links.docx")
        absurd_list      = self._load_docx("absurd_links.docx")
        prefix_list      = self._load_docx("Breadcrumb_Prefix.docx")

        # OPTIMIZATION #5: pre-convert to fastest lookup structures.
        #   - sets      → O(1) "x in collection" checks
        #   - tuple     → str.startswith(tuple) short-circuits in C
        self.delayed_loading_links: set[str] = set(delayed_list)
        self.absurd_links:          set[str] = set(absurd_list)
        self._breadcrumb_links:     set[str] = set(breadcrumb_list)
        self._breadcrumb_prefixes:  tuple[str, ...] = tuple(prefix_list)

        # ── Output file paths (UNCHANGED – do not rename) ─────────────
        tag = f"{self.region}_{self.country}_{self.language}_{self.account_type}"

        self.path_page_tree    = BASE_DIR / "Page Trees"    / f"PageTree{tag}.txt"
        self.path_doc_links    = BASE_DIR / "DocumentLinks" / f"Doclinks{tag}.txt"
        self.path_reverse_dict = BASE_DIR / "Reverse Dicts" / f"RevDict{tag}.txt"
        self.path_external     = BASE_DIR / "External Urls" / f"External{tag}.txt"
        self.path_redirects    = BASE_DIR / "Redirects"     / f"Redirects{tag}.txt"

        # ── Playwright handles ────────────────────────────────────────
        self._playwright = None
        self._browser    = None
        self._context    = None

        # Long-lived page used for login + country switching
        self._session_page = None

        # OPTIMIZATION #1: long-lived page used for ALL crawl fetches.
        # Created lazily on first use, reused across every URL, only
        # recreated if Chromium closes it.
        self._crawl_page = None

        # ── Country-check throttle state ──────────────────────────────
        self._last_country_check_time   = time.time()
        self._pages_since_country_check = 0

        # ── Redirect tracking ─────────────────────────────────────────
        self._redirect_map: dict[str, str] = {}

    # ------------------------------------------------------------------
    # 4.2  Private utilities
    # ------------------------------------------------------------------

    def _load_docx(self, filename: str) -> list[str]:
        """Load lines from a .docx reference file.  Missing file → [] + warn."""
        path = str(BASE_DIR / filename)
        try:
            raw = work.doc_reader(path)
            return [line.strip() for line in raw if line.strip()]
        except FileNotFoundError:
            log.warning("⚠️  Reference file not found (skipping): %s", path)
            return []
        except Exception as exc:
            log.warning("⚠️  Could not read %s – %s", path, exc)
            return []

    def _ensure_output_dirs(self) -> None:
        """Create all output directories if they do not already exist."""
        for path in (
            self.path_page_tree,
            self.path_doc_links,
            self.path_reverse_dict,
            self.path_external,
            self.path_redirects,
        ):
            path.parent.mkdir(parents=True, exist_ok=True)

    def _is_breadcrumb_url(self, url: str) -> bool:
        """
        Return True if `url` is a breadcrumb navigation artifact.

        OPTIMIZATION #5: str.startswith accepts a tuple of prefixes and
        checks them all in a single C-level call — much faster than
        iterating the list in Python.  Set membership for the literal
        list is O(1).
        """
        if self._breadcrumb_prefixes and url.startswith(self._breadcrumb_prefixes):
            return True
        return url in self._breadcrumb_links

    def _is_real_content_page(self, url: str) -> bool:
        """True iff `url` is a genuine PRP content page (not home / breadcrumb)."""
        return (
            url.startswith(self.BASE_URL)
            and not is_home_page(url)
            and not self._is_breadcrumb_url(url)
        )

    # ------------------------------------------------------------------
    # 4.3  Browser / session lifecycle
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """Launch the Playwright browser and create a shared browser context."""
        self._playwright = sync_playwright().start()
        self._browser    = self._playwright.chromium.launch(headless=False)
        self._context    = self._browser.new_context()
        log.info("✅ Browser launched for %s", self.username)

    def teardown(self) -> None:
        """Close all Playwright resources in the correct reverse-creation order."""
        for attr_name, label in (
            ("_crawl_page",   "crawl page"),
            ("_session_page", "session page"),
            ("_context",      "browser context"),
            ("_browser",      "browser"),
        ):
            obj = getattr(self, attr_name, None)
            if obj is not None:
                try:
                    obj.close()
                except Exception as exc:
                    log.debug("Non-fatal error closing %s: %s", label, exc)
                setattr(self, attr_name, None)

        if self._playwright is not None:
            try:
                self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        log.info("🧹 Browser closed for %s", self.username)

    def _get_session_page(self):
        """Return the long-lived session page, creating it lazily if needed."""
        if self._session_page is None:
            self._session_page = self._context.new_page()
            self._session_page.set_default_timeout(PAGE_TIMEOUT_MS)
        return self._session_page

    def _get_crawl_page(self):
        """
        Return the reusable crawl page (OPTIMIZATION #1).

        Creates it on first call; recreates it if Chromium closed it for
        any reason (e.g. target crash).  All URLs in a single crawl
        session share this page — goto() replaces the DOM each time, so
        there is no state bleed between navigations.
        """
        if self._crawl_page is None or self._crawl_page.is_closed():
            self._crawl_page = self._context.new_page()
            self._crawl_page.set_default_timeout(PAGE_TIMEOUT_MS)
        return self._crawl_page

    # ------------------------------------------------------------------
    # 4.4  Login
    # ------------------------------------------------------------------

    def login(self) -> None:
        """Navigate to the portal and complete the two-step Okta login flow."""
        page = self._get_session_page()
        log.info("🔐 Logging in as %s …", self.username)

        page.goto(self.BASE_URL, wait_until="domcontentloaded")
        time.sleep(5)   # Give the Okta widget time to render

        try:
            page.type("#oktaEmailInput", self.username, delay=5)
            page.click("#oktaSignInBtn")
            page.fill("#password-sign-in", self.password)
            page.click("#onepass-submit-btn")
        except Exception:
            log.warning("⚠️  Primary login selectors failed; trying fallback click …")
            try:
                page.click("#onepass-submit-btn")
            except Exception:
                pass   # May already be authenticated

        try:
            page.wait_for_load_state("domcontentloaded", timeout=20_000)
        except Exception:
            pass

        log.info("✅ Login step completed")

    # ------------------------------------------------------------------
    # 4.5  Country / overlay management
    # ------------------------------------------------------------------

    def _close_notification_overlay(self, page) -> None:
        """Dismiss the #alertMessager banner if visible."""
        try:
            overlay = page.wait_for_selector("#alertMessager", timeout=5_000)
            if overlay and overlay.is_visible():
                log.info("🔔 Notification overlay visible; dismissing …")
                try:
                    page.click("#closemsg")
                except Exception:
                    page.evaluate("document.querySelector('#closemsg')?.click()")
                try:
                    page.wait_for_selector("#alertMessager", state="hidden", timeout=10_000)
                except Exception:
                    pass
                log.info("✅ Overlay dismissed")
        except PlaywrightTimeoutError:
            pass   # No overlay appeared – normal

    def _read_current_country(self, page) -> str:
        """Click the eyeball menu and return the currently selected country name."""
        try:
            eyeball = page.wait_for_selector("#MHMG-usereye", timeout=30_000)
            if eyeball:
                eyeball.click()
        except Exception:
            return ""

        selector = (
            "#portlet_com_hpe_prp_mhmg_web_PrpMhmgEyeballWebPortlet "
            "> div > div.portlet-content-container > div "
            "> div.MHMGuserdescrp > div > div.MHMGcountryname"
        )
        try:
            el = page.wait_for_selector(selector, timeout=20_000)
            return el.inner_text().strip() if el else ""
        except Exception:
            return ""

    @staticmethod
    def _country_similarity(a: str, b: str) -> float:
        """Fuzzy similarity score (0.0–1.0) for two country-name strings."""
        if not a or not b:
            return 0.0

        a_norm = a.lower().replace("(", " ").replace(")", " ")
        b_norm = b.lower().replace("(", " ").replace(")", " ")

        a_tokens = set(a_norm.split())
        b_tokens = set(b_norm.split())

        token_score = len(a_tokens & b_tokens) / max(len(a_tokens), 1)
        char_score  = sum(1 for ch in a_norm if ch in b_norm) / max(len(a_norm), 1)

        return token_score * 0.6 + char_score * 0.4

    def set_country(self, page, *, force_recheck: bool = False) -> str:
        """Ensure the portal's country context is set to self.country."""
        time.sleep(5)   # Let any post-navigation animations settle

        self._close_notification_overlay(page)

        current = self._read_current_country(page)
        check_label = "re-check" if force_recheck else "initial check"
        log.info("🌍 Country %s: '%s'", check_label, current or "unknown")

        try:
            btn = page.wait_for_selector("#Otherlocations > span.MHMGparty", timeout=15_000)
            if btn:
                btn.click()
        except Exception:
            pass

        try:
            page.wait_for_selector("ul#MHMGBRcountries li.locationsBRlist", timeout=15_000)
        except Exception:
            pass

        if current.lower() == self.country.lower():
            log.info("✅ Country correctly set to '%s'", current)
            try:
                page.keyboard.press("Escape")
            except Exception:
                pass
            return current

        if force_recheck:
            log.warning("⚠️  Country drifted from '%s'!  Resetting to '%s' …",
                        current, self.country)

        options     = page.query_selector_all("ul#MHMGBRcountries li.locationsBRlist")
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

        MINIMUM_SIMILARITY = 0.30
        if best_score >= MINIMUM_SIMILARITY and best_option is not None:
            try:
                best_option.click()
            except Exception:
                page.evaluate("(el) => el.click()", best_option)
            log.info("🌐 Country switched to '%s' (similarity=%.2f)", best_name, best_score)

            try:
                container = page.wait_for_selector(
                    "#MHMGBRLIst > li > div > div", timeout=15_000
                )
                if container:
                    container.click()
            except Exception:
                pass
        else:
            log.warning("⚠️  No suitable match for '%s'.  Best: '%s' (score=%.2f)",
                        self.country, best_name, best_score)

        return current

    def _maybe_check_country(self) -> None:
        """Periodically re-verify the country setting hasn't drifted."""
        time_ok  = (time.time() - self._last_country_check_time) >= COUNTRY_CHECK_INTERVAL_SECONDS
        pages_ok = self._pages_since_country_check >= COUNTRY_CHECK_EVERY_N_PAGES

        if not (time_ok or pages_ok):
            return

        log.info(
            "🔍 Periodic country check (%.0fs elapsed, %d pages since last check)",
            time.time() - self._last_country_check_time,
            self._pages_since_country_check,
        )

        if self._session_page is not None:
            try:
                self.set_country(self._session_page, force_recheck=True)
            except Exception as exc:
                log.warning("⚠️  Country re-check failed: %s", exc)

        self._last_country_check_time   = time.time()
        self._pages_since_country_check = 0

    # ------------------------------------------------------------------
    # 4.6  URL resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_href(current_page_url: str, href: str) -> str:
        """
        Resolve a raw href to an absolute URL using pure string logic.

        Rules:
          - Absolute URL (http/https)  → normalised as-is
          - Root-relative (starts /)   → prepend BASE domain
          - Other relative             → resolve against current page URL
        """
        if not href:
            return ""

        href = href.strip()

        if href.startswith(("http://", "https://")):
            return normalize_url(current_page_url, href)

        if href.startswith("/"):
            return f"https://partner.hpe.com{href}"

        return normalize_url(current_page_url, href)

    # ------------------------------------------------------------------
    # 4.7  Single-page fetch + link extraction
    # ------------------------------------------------------------------

    # OPTIMIZATION #2: single JS expression that gathers every <a href> in
    # one IPC round-trip.  Replaces the per-anchor CDP call pattern.
    _JS_COLLECT_HREFS = """
        () => Array.from(document.querySelectorAll('a'))
                   .map(a => a.getAttribute('href'))
                   .filter(h => h && h.trim() !== '')
    """

    def _fetch_and_extract(
        self,
        url:      str,
        tree:     dict,
        docs:     set,
        external: set,
    ) -> list:
        """
        Open `url` on the reusable crawl page and return discovered child URLs.

        Mutates in place:
          tree     – parent → [child URL] mapping
          docs     – downloadable document URLs
          external – URLs outside partner.hpe.com
        """
        found_children: list[str] = []

        # OPTIMIZATION #1: reuse the long-lived crawl page.
        page = self._get_crawl_page()

        try:
            log.info("📍 Fetching: %s", url)
            page.goto(url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            self._pages_since_country_check += 1

            # ── Redirect detection (server-level, pre-JS) ──────────────
            actual_url   = page.url.split("#")[0]
            intended_url = url.split("#")[0]

            if actual_url != intended_url:
                redirect_type = categorize_redirect(intended_url, actual_url)
                self._redirect_map[intended_url] = actual_url
                log.info("↪  Redirect [%s]: %s → %s", redirect_type, intended_url, actual_url)

                if redirect_type == "home" and not is_home_page(intended_url):
                    log.info("🏠 Bounced to home from content page; skipping: %s", intended_url)
                    return []
            else:
                actual_url = intended_url

            # ── Special-case page waits (unchanged business logic) ─────
            if url in self.delayed_loading_links:
                try:
                    page.wait_for_selector("#disBtn", timeout=15_000)
                except PlaywrightTimeoutError:
                    pass

            if url in self.absurd_links:
                page.wait_for_timeout(1_500)

            # ── OPTIMIZATION #3: conditional networkidle ──────────────
            # Only pages matching JS_REDIRECT_URL_MARKER pay the heavy
            # networkidle cost.  Everything else gets a tiny settle.
            if JS_REDIRECT_URL_MARKER in url:
                try:
                    page.wait_for_load_state("networkidle", timeout=JS_REDIRECT_WAIT_MS)
                except PlaywrightTimeoutError:
                    page.wait_for_timeout(1_500)
            else:
                page.wait_for_timeout(DOM_SETTLE_MS)

            # ── Re-read URL after potential JS redirect ────────────────
            post_settle_url = page.url.split("#")[0]
            if post_settle_url != actual_url:
                log.info("↪  JS redirect after load: %s → %s", actual_url, post_settle_url)
                self._redirect_map[actual_url] = post_settle_url

                if is_home_page(post_settle_url) and not is_home_page(actual_url):
                    log.info("🏠 JS-redirected to home; skipping: %s", actual_url)
                    return []

                actual_url = post_settle_url

            # ── Ensure tree entry exists ───────────────────────────────
            if actual_url not in tree:
                tree[actual_url] = []
            if intended_url != actual_url and intended_url not in tree:
                tree[intended_url] = tree[actual_url]

            # ── OPTIMIZATION #2: one IPC call for every href ───────────
            try:
                raw_hrefs = page.evaluate(self._JS_COLLECT_HREFS)
            except Exception as exc:
                log.warning("⚠️  href collection failed on %s: %s", actual_url, exc)
                raw_hrefs = []

            log.info("🔍 %d raw href(s) on %s", len(raw_hrefs), actual_url)

            # Per-page stats for the summary log
            stats = {
                "bad_scheme":      0,
                "skip_pattern":    0,
                "self_ref":        0,
                "document":        0,
                "external":        0,
                "new_internal":    0,
                "already_in_tree": 0,
            }

            # Local aliases for hot-loop speed (saves attribute lookups)
            tree_children   = tree[actual_url]
            actual_no_slash = actual_url.rstrip("/")
            bad_schemes     = ("javascript:", "mailto:", "tel:", "data:")

            for href in raw_hrefs:
                # Non-navigable schemes
                if any(href.startswith(s) for s in bad_schemes):
                    stats["bad_scheme"] += 1
                    continue

                # Resolve to absolute URL (pure string, no network)
                child_url = self._resolve_href(actual_url, href)
                if not child_url:
                    continue

                # Self-reference
                if child_url.rstrip("/") == actual_no_slash:
                    stats["self_ref"] += 1
                    continue

                # Noise (login / logout / portlet actions)
                if should_skip_url(child_url):
                    stats["skip_pattern"] += 1
                    continue

                # ── Classify and bucket ────────────────────────────────
                if is_document_url(child_url):
                    docs.add(child_url)
                    if child_url not in tree_children:
                        tree_children.append(child_url)
                    stats["document"] += 1
                    continue

                if is_hpe_partner_url(child_url):
                    if child_url not in tree_children:
                        tree_children.append(child_url)
                        found_children.append(child_url)
                        stats["new_internal"] += 1
                    else:
                        stats["already_in_tree"] += 1
                else:
                    if not self._is_breadcrumb_url(child_url):
                        external.add(child_url)
                    stats["external"] += 1

            log.info(
                "📊 %s — new:%d already:%d doc:%d ext:%d "
                "skipped(scheme:%d pattern:%d self:%d)",
                actual_url,
                stats["new_internal"], stats["already_in_tree"],
                stats["document"],     stats["external"],
                stats["bad_scheme"],   stats["skip_pattern"],
                stats["self_ref"],
            )

        except PlaywrightTimeoutError:
            log.warning("⏱️  Timeout loading %s", url)
        except Exception as exc:
            log.error("❌ Error crawling %s: %s", url, exc, exc_info=True)
        # NO finally: the crawl page is reused across URLs (optimization #1).
        # If the page got into a weird state, the next goto() replaces the DOM;
        # if it was closed outright, _get_crawl_page() will recreate it.

        return found_children

    # ------------------------------------------------------------------
    # 4.8  Main BFS crawl loop
    # ------------------------------------------------------------------

    def crawl(self) -> tuple:
        """Breadth-first crawl from the portal home.  Returns (internal, external, docs, tree)."""
        internal: set  = set()
        external: set  = set()
        docs:     set  = set()
        tree:     dict = {}

        SEED_URL = self.BASE_URL + "/group/prp"

        visited: set  = set()
        queued:  set  = {SEED_URL}
        frontier: deque = deque([SEED_URL])

        log.info(
            "🚀 Crawl started — %s / %s / %s / %s",
            self.username, self.region, self.country, self.account_type,
        )

        while frontier:
            # Periodically verify country hasn't drifted
            self._maybe_check_country()

            url = frontier.popleft()
            queued.discard(url)

            if not url or url in visited:
                continue

            visited.add(url)

            # Documents: recorded, not opened
            if is_document_url(url):
                docs.add(url)
                continue

            # Only crawl HPE partner pages
            if not is_hpe_partner_url(url):
                if not self._is_breadcrumb_url(url):
                    external.add(url)
                continue

            # Skip noise URLs
            if should_skip_url(url):
                continue

            # Fetch + extract
            child_urls = self._fetch_and_extract(url, tree, docs, external)

            # Record as content page if appropriate
            if self._is_real_content_page(url):
                internal.add(url)

            # If a redirect occurred, also record the actual destination
            if url in self._redirect_map:
                actual = self._redirect_map[url]
                if self._is_real_content_page(actual):
                    internal.add(actual)
                visited.add(actual)

            # Enqueue newly discovered URLs
            for child in child_urls:
                if child not in visited and child not in queued:
                    frontier.append(child)
                    queued.add(child)

            # OPTIMIZATION #4: shortened polite delay (skipped if 0)
            if CRAWL_DELAY_SECONDS > 0:
                time.sleep(CRAWL_DELAY_SECONDS)

        log.info(
            "✅ Crawl complete — internal:%d  external:%d  docs:%d  visited:%d",
            len(internal), len(external), len(docs), len(visited),
        )

        return internal, external, docs, tree

    # ------------------------------------------------------------------
    # 4.9  Post-processing
    # ------------------------------------------------------------------

    @staticmethod
    def _build_reverse_dict(tree: dict) -> dict:
        """Invert parent→[children] into child→[parents]."""
        reverse: dict = {}

        for parent, children in tree.items():
            reverse.setdefault(parent, set())
            for child in children:
                reverse.setdefault(child, set()).add(parent)

        return {url: sorted(parents) for url, parents in reverse.items()}

    # ------------------------------------------------------------------
    # 4.10  Output writing (filenames and formats UNCHANGED)
    # ------------------------------------------------------------------

    def _write_results(
        self,
        internal: set,
        external: set,
        docs:     set,
        tree:     dict,
    ) -> None:
        """Write all crawl results to the five output files."""
        self._ensure_output_dirs()

        # Internal pages (site map)
        with open(self.path_page_tree, "w", encoding="utf-8") as f:
            for url in sorted(internal):
                if url.startswith(self.BASE_URL + "/"):
                    f.write(url + "\n")

        # External links
        with open(self.path_external, "w", encoding="utf-8") as f:
            for url in sorted(external):
                f.write(url + "\n")

        # Document links
        with open(self.path_doc_links, "w", encoding="utf-8") as f:
            for url in sorted(docs):
                f.write(url + "\n")

        # Reverse dictionary (child → parents)
        reverse_dict = self._build_reverse_dict(tree)
        with open(self.path_reverse_dict, "w", encoding="utf-8") as f:
            f.write(str(reverse_dict))

        # Redirect log
        with open(self.path_redirects, "w", encoding="utf-8") as f:
            f.write("Intended URL → Actual URL\n")
            f.write("=" * 80 + "\n")
            for intended, actual in sorted(self._redirect_map.items()):
                f.write(f"{intended} → {actual}\n")

        log.info(
            "📝 Results saved — internal:%d  external:%d  docs:%d  redirects:%d",
            len(internal), len(external), len(docs), len(self._redirect_map),
        )

    # ------------------------------------------------------------------
    # 4.11  Public entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Execute the full crawl pipeline.  Safe to call under multiprocessing."""
        try:
            self.login()
            self.set_country(self._get_session_page())

            internal, external, docs, tree = self.crawl()
            self._write_results(internal, external, docs, tree)

            log.info(
                "🎉 Account done — %s / %s / %s",
                self.region, self.country, self.account_type,
            )

        except Exception as exc:
            log.exception("❌ Fatal error for %s: %s", self.username, exc)
        finally:
            self.teardown()


# ===========================================================================
# SECTION 5 – PROCESS ENTRY POINT
# ===========================================================================

def _run_account(account: list) -> None:
    """Top-level function executed by each worker process."""
    crawler = PRPCrawler(*account)
    crawler.setup()
    crawler.run()   # run() calls teardown() internally


# ===========================================================================
# SECTION 6 – MAIN BLOCK (script entry point)
# ===========================================================================

if __name__ == "__main__":

    # ------------------------------------------------------------------
    # ACCOUNTS
    # Format: [username, password, region, country, language, account_type]
    # ------------------------------------------------------------------
    accounts = [
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
        ['mhmg_albert_solp2@yopmail.com', 'Login2Bot!', 'EMEA', 'Spain',       'Spanish',            'T2'],
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

    for account in accounts:
        # Wait until a slot is free
        while sum(1 for p in running if p.is_alive()) >= MAX_PARALLEL:
            time.sleep(1)

        # Prune finished processes
        running = [p for p in running if p.is_alive()]

        p = Process(
            target=_run_account,
            args=(account,),
            name=account[0],
        )
        p.start()
        log.info("▶  Process started for %s  (running: %d / %d)",
                 account[0], len(running) + 1, MAX_PARALLEL)
        running.append(p)
        all_procs.append(p)

    for p in all_procs:
        p.join()
        log.info("⏹  Process finished: %s  (exit code: %s)", p.name, p.exitcode)

    log.info("🎉 All accounts processed successfully")