import argparse
import ast
from pathlib import Path
import re
import pandas as pd

from adhocPageTreeExtendedIframe_phase3 import PRP as TreePRP

BASE_DIR = Path(__file__).parent

REV_DICT_PATH = BASE_DIR / "Reverse Dicts" / "AD_HOC_RevDict.txt"
OUTPUT_DIR = BASE_DIR / "Search Results"
LINK_EXCEL_PATH = BASE_DIR / "Ad hoc Requests" / "AD_HOC_Links_To_Search.xlsx"


class PRP:
    def __init__(self, username, password, region, country, language, acc_type):
        self.username = username
        self.password = password
        self.region = region
        self.country = country
        self.language = language
        self.acc_type = acc_type

        # adhoc-specific defaults
        self.links = None
        self.contains = False
        self.regen_tree = False

        self.revdict = {}
        self.targets = []
        self.results = {}

    # ------------------------------------------------------------------
    # Setup: optionally regenerate the tree, then load inputs
    # ------------------------------------------------------------------
    def setUp(self) -> None:
        if self.regen_tree:
            prp = TreePRP(
                self.username, self.password,
                self.region, self.country,
                self.language, self.acc_type,
            )
            try:
                prp.setUp()
                prp.scrapecall_writetrees()
            finally:
                try:
                    prp.tearDown()
                except Exception:
                    pass

        self.targets = self.links if self.links else self._load_links_from_excel()
        self.revdict = self._load_reverse_dict()
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Main execution: search and write results
    # ------------------------------------------------------------------
    def parent(self) -> None:
        self.results = self._search_links()

        out_name = self._sanitize_filename('_'.join(self.targets)) if self.targets else 'links'
        out_file = OUTPUT_DIR / f'link_search_{out_name}.txt'

        with out_file.open('w', encoding='utf-8') as f:
            for target, parents in self.results.items():
                header = f'=== {target} ==='
                print(header)
                f.write(header + '\n')
                if not parents:
                    line = '  (no parent pages found)'
                    print(line)
                    f.write(line + '\n')
                else:
                    for p in sorted(set(parents)):
                        line = f'  {p}'
                        print(line)
                        f.write(line + '\n')
                print()
                f.write('\n')

        print(f'Wrote link search results to: {out_file}')

    # ------------------------------------------------------------------
    # Teardown: nothing to close for a file-based searcher, kept for
    # interface consistency with PRP
    # ------------------------------------------------------------------
    def tearDown(self) -> None:
        pass

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_reverse_dict(self) -> dict[str, list[str]]:
        if not REV_DICT_PATH.exists():
            raise FileNotFoundError(f'Missing reverse dict file: {REV_DICT_PATH}')
        text = REV_DICT_PATH.read_text(encoding='utf-8')
        data = ast.literal_eval(text)
        revdict: dict[str, list[str]] = {}
        for k, v in data.items():
            key = str(k)
            if isinstance(v, (list, set, tuple)):
                revdict[key] = [str(x) for x in v]
            elif v is None:
                revdict[key] = []
            else:
                revdict[key] = [str(v)]
        return revdict

    def _load_links_from_excel(self) -> list[str]:
        if not LINK_EXCEL_PATH.exists():
            raise FileNotFoundError(f'Missing links Excel file: {LINK_EXCEL_PATH}')
        df = pd.read_excel(LINK_EXCEL_PATH)

        preferred_cols = ['Link', 'Links', 'URL', 'Urls', 'Child link']
        values = None
        for col in preferred_cols:
            if col in df.columns:
                values = df[col]
                break
        if values is None:
            values = df.iloc[:, 0]

        links: list[str] = []
        for v in values:
            t = v.strip() if isinstance(v, str) else (str(v).strip() if v is not None else '')
            if t:
                links.append(t)
        return links

    def _search_links(self) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        if self.contains:
            for pattern in self.targets:
                pattern = pattern.strip()
                parents: set[str] = set()
                if not pattern:
                    result[pattern] = []
                    continue
                for child, sources in self.revdict.items():
                    if pattern in child:
                        parents.update(sources)
                result[pattern] = sorted(parents)
        else:
            for link in self.targets:
                key = link.strip()
                result[link] = list(self.revdict.get(key, [])) if key else []
        return result

    @staticmethod
    def _sanitize_filename(text: str) -> str:
        safe = re.sub(r'[^A-Za-z0-9._-]+', '_', text.strip())
        return safe[:80]


# ----------------------------------------------------------------------
# CLI entry point
# ----------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Find pages that contain given links using AD_HOC reverse dict (no re-scraping).'
    )
    parser.add_argument(
        '--link', action='append', required=False,
        help='Link to search for (child URL). Repeatable. Omit to load from Excel.'
    )
    parser.add_argument(
        '--contains', action='store_true',
        help='Treat each --link value as a substring to match against stored child URLs.'
    )
    parser.add_argument(
        '--regen-tree', action='store_true',
        help='Regenerate the AD_HOC page tree and reverse dict before searching.'
    )
    parser.add_argument('--username', default='bot.dec-d001a@hpe.com')
    parser.add_argument('--password', default='Login2PRP!')
    parser.add_argument('--region',   default='NA')
    parser.add_argument('--country',  default='USA')
    parser.add_argument('--language', default='English')
    parser.add_argument('--acc-type', default='T2')
    args = parser.parse_args()

    searcher = PRP(
        args.username,
        args.password,
        args.region,
        args.country,
        args.language,
        args.acc_type,
        )

    searcher.links = args.link
    searcher.contains = args.contains
    searcher.regen_tree = args.regen_tree
    try:
        searcher.setUp()
        searcher.parent()
    finally:
        searcher.tearDown()


if __name__ == '__main__':
    main()