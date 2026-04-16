import argparse
import re
import time
from pathlib import Path
import pandas as pd

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from adhocPageTreeExtendedIframe_phase3 import PRP as TreePRP

BASE_DIR = Path(__file__).parent

PAGE_TREE_PATH = BASE_DIR / "Page Trees" / "AD_HOC_PageTree_Internal.txt"
OUTPUT_DIR = BASE_DIR / "Search Results"
PHRASE_EXCEL_PATH = BASE_DIR / "Ad hoc Requests" / "Aruba Series names - Adhoc request.xlsx"

BASE_URL = 'https://internal.it.hpe.com/web/internal'
HOME_CANDIDATES = {
    'https://partner.hpe.com',
    'https://partner.hpe.com/home',
    'https://partner.hpe.com/group/prp',
    'https://partner.hpe.com/group/prp/home',
    'https://partner.hpe.com/group/prp/home?tutorial=homepage',
}


class PRP:
    def __init__(self, username, password, region, country, language, acc_type):
        self.username = username
        self.password = password
        self.region = region
        self.country = country
        self.language = language
        self.acc_type = acc_type

        self.phrases = None
        self.regen_tree = False
        self.headless = False

        self._prp: TreePRP | None = None
        self._targets: list[str] = []
        self._links: list[str] = []
        self.results: dict[str, set[str]] = {}
        self.redirects_to_home: set[str] = set()
        self.out_file: Path | None = None

    # ------------------------------------------------------------------
    # Setup: launch browser, log in, load inputs
    # ------------------------------------------------------------------
    def setUp(self) -> None:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self._prp = TreePRP(
            self.username, self.password,
            self.region, self.country,
            self.language, self.acc_type,
        )
        self._prp.setUp()

        if self.regen_tree:
            self._prp.scrapecall_writetrees()
        else:
            self._prp.login_internal()
            time.sleep(15)

        self._targets = self.phrases if self.phrases else self._load_phrases_from_excel()
        self._links = self._load_links()

    # ------------------------------------------------------------------
    # Main execution: iterate links, match phrases, write results
    # ------------------------------------------------------------------
    def parent(self) -> None:
        print("Targets:", self._targets)
        print("Links count:", len(self._links))
        page = self._prp.page
        phrases_ci = [p.lower() for p in self._targets]

        for link in self._links:
            if not (link.startswith('http://') or link.startswith('https://')):
                continue
            matched, _final_url, is_home = self._page_match_phrases(page, link, phrases_ci)
            if is_home:
                self.redirects_to_home.add(link)
                continue
            if matched:
                self.results.setdefault(link, set()).update(matched)

        safe_name = self._sanitize_filename('_'.join(self._targets))
        self.out_file = OUTPUT_DIR / f'matches_{safe_name}.txt'
        with self.out_file.open('w', encoding='utf-8') as f:
            for link, mset in self.results.items():
                f.write(f"{link} | matched: {', '.join(sorted(mset))}\n")

        print(f'Wrote matches to: {self.out_file}')

    # ------------------------------------------------------------------
    # Teardown: close the browser session
    # ------------------------------------------------------------------
    def tearDown(self) -> None:
        if self._prp is not None:
            try:
                self._prp.tearDown()
            except Exception:
                pass
            self._prp = None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_links(self) -> list[str]:
        if not PAGE_TREE_PATH.exists():
            raise FileNotFoundError(f'Missing page tree file: {PAGE_TREE_PATH}')
        with PAGE_TREE_PATH.open('r', encoding='utf-8') as f:
            raw = [line.strip() for line in f if line.strip()]
        seen: set[str] = set()
        links: list[str] = []
        for u in raw:
            if u not in seen:
                seen.add(u)
                links.append(u)
        return links

    def _load_phrases_from_excel(self) -> list[str]:
        if not PHRASE_EXCEL_PATH.exists():
            raise FileNotFoundError(f'Missing phrase file: {PHRASE_EXCEL_PATH}')
        df = pd.read_excel(PHRASE_EXCEL_PATH)
        column = 'Active Series name'
        values = df[column] if column in df.columns else df.iloc[:, 0]
        phrases: list[str] = []
        for v in values:
            t = v.strip() if isinstance(v, str) else (str(v).strip() if v is not None else '')
            if t:
                phrases.append(t)
        return phrases

    def _page_match_phrases(self, page, url: str, phrases_ci: list[str]) -> tuple[list[str], str, bool]:
        try:
            page.goto(url, wait_until='networkidle')
            final_url = page.url
            if self._is_home_url(final_url):
                return [], final_url, True
            src = page.content()
            soup = BeautifulSoup(src, 'html.parser')
            container = soup.find(id='main-content')
            if not container:
                return [], final_url, False
            text = container.get_text(separator='\n', strip=True)
            lt = text.lower()
            matches = [p for p in phrases_ci if p in lt]
            return matches, final_url, False
        except PlaywrightTimeoutError:
            return [], url, False
        except Exception:
            return [], url, False

    @staticmethod
    def _normalize_url(u: str) -> str:
        try:
            base = u.split('#', 1)[0].split('?', 1)[0]
            return base.rstrip('/')
        except Exception:
            return u

    def _is_home_url(self, u: str) -> bool:
        nu = self._normalize_url(u)
        return any(nu == self._normalize_url(h) for h in HOME_CANDIDATES)

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        safe = re.sub(r'[^A-Za-z0-9._-]+', '_', text.strip())
        return safe[:80]


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Search phrases across page contents listed in AD_HOC page tree.'
    )
    parser.add_argument('--username', default='bot.dec-d001a@hpe.com')
    parser.add_argument('--password', default='want2seePRP!')
    parser.add_argument(
        '--phrase', action='append', required=False,
        help='Phrase to search (repeatable). Omit to load from Excel.'
    )
    parser.add_argument('--headless',   action='store_true', help='Run Chrome in headless mode')
    parser.add_argument('--regen-tree', action='store_true', help='Regenerate the AD_HOC page tree before searching')
    args = parser.parse_args()

    phrases = args.phrase if args.phrase else None  # None → load from Excel inside setUp

    searcher = PRP(
        phrases=phrases,
        regen_tree=args.regen_tree,
        headless=args.headless,
        username=args.username,
        password=args.password,
    )

    searcher.phrases = phrases
    searcher.regen_tree = args.regen_tree
    searcher.headless = args.headless
    try:
        searcher.setUp()
        searcher.parent()
    finally:
        searcher.tearDown()


if __name__ == '__main__':
    main()