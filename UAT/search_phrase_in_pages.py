import argparse
import os
import re
import time
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from adhocPageTreeExtendedIframe import PRP


PAGE_TREE_PATH = Path('Page Trees') / 'AD_HOC_PageTree_Internal.txt'
OUTPUT_DIR = Path('Search Results')
BASE_URL = 'https://internal.it.hpe.com/web/internal'
HOME_CANDIDATES = {
    'https://partner.hpe.com',
    'https://partner.hpe.com/home',
    'https://partner.hpe.com/group/prp',
    'https://partner.hpe.com/group/prp/home',
    'https://partner.hpe.com/group/prp/home?tutorial=homepage'
}

def ensure_dirs():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(text: str) -> str:
    safe = re.sub(r'[^A-Za-z0-9._-]+', '_', text.strip())
    return safe[:80] if len(safe) > 80 else safe


def login_internal(driver: webdriver.Chrome, username: str, password: str) -> None:
    wait = WebDriverWait(driver, 30, poll_frequency=1, ignored_exceptions=[NoSuchElementException, StaleElementReferenceException])
    driver.get(BASE_URL)
    wait.until(EC.element_to_be_clickable((By.ID, 'oktaEmailInput'))).send_keys(username)
    wait.until(EC.element_to_be_clickable((By.ID, 'oktaSignInBtn'))).click()
    time.sleep(10)


def load_links() -> list[str]:
    if not PAGE_TREE_PATH.exists():
        raise FileNotFoundError(f'Missing page tree file: {PAGE_TREE_PATH}')
    with PAGE_TREE_PATH.open('r', encoding='utf-8') as f:
        raw = [line.strip() for line in f if line.strip()]
    # de-duplicate while preserving order
    seen = set()
    links: list[str] = []
    for u in raw:
        if u not in seen:
            seen.add(u)
            links.append(u)
    return links


def normalize_url(u: str) -> str:
    try:
        # strip fragment and query, lowercase host and path by simple split
        base = u.split('#', 1)[0].split('?', 1)[0]
        # remove trailing slash except for root
        if base.endswith('/'):
            base = base[:-1]
        return base
    except Exception:
        return u


def is_home_url(u: str) -> bool:
    nu = normalize_url(u)
    # consider home if it equals any candidate (normalized)
    for h in HOME_CANDIDATES:
        if nu == normalize_url(h):
            return True
    return False


def page_match_phrases(driver: webdriver.Chrome, url: str, phrases_ci: list[str]) -> tuple[list[str], str, bool]:
    try:
        driver.get(url)
        time.sleep(10)
        WebDriverWait(driver, 15).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        final_url = driver.current_url
        if is_home_url(final_url):
            return [], final_url, True
        src = driver.page_source
        soup = BeautifulSoup(src, 'html.parser')
        container = soup.find(id='main-content')
        if not container:
            return [], final_url, False
        text = container.get_text(separator='\n', strip=True)
        lt = text.lower()
        matches = [p for p in phrases_ci if p in lt]
        return matches, final_url, False
    except TimeoutException:
        return [], url, False
    except Exception:
        return [], url, False


def run(username: str, password: str, phrases: list[str], headless: bool = False) -> Path:
    ensure_dirs()
    prp = PRP(username, password, 'NA', 'USA', 'English', 'T2')
    prp.setUp()
    driver = prp.driver

    try:
        prp.login_internal()
        time.sleep(15)
        links = load_links()
        phrases_ci = [p.lower() for p in phrases]
        # map original link -> set of matched phrases (dedup), but skip links that redirect to home
        combined: dict[str, set[str]] = {}
        redirects_to_home: set[str] = set()
        for link in links:
            if not (link.startswith('http://') or link.startswith('https://')):
                continue
            matched, final_url, is_home = page_match_phrases(driver, link, phrases_ci)
            if is_home:
                redirects_to_home.add(link)
                continue
            if matched:
                if link not in combined:
                    combined[link] = set()
                combined[link].update(matched)
        out_file = OUTPUT_DIR / f"matches_{sanitize_filename('_'.join(phrases))}.txt"
        with out_file.open('w', encoding='utf-8') as f:
            for link, mset in combined.items():
                f.write(f"{link} | matched: {', '.join(sorted(mset))}\n")
        # Optionally write skipped redirects for visibility (commented out to keep behavior minimal)
        # with (OUTPUT_DIR / 'skipped_redirects_to_home.txt').open('w', encoding='utf-8') as sf:
        #     for l in sorted(redirects_to_home):
        #         sf.write(l + '\n')
        return out_file
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search a phrase across page contents listed in AD_HOC page tree.')
    parser.add_argument('--username', required=False, default='bot.dec-d001a@hpe.com', help='Okta username for internal portal')
    parser.add_argument('--password', required=False, default='want2seePRP!', help='Okta password for internal portal')
    parser.add_argument('--phrase', action='append', required=False, help='Phrase to search (use multiple --phrase flags for multiple terms).')
    parser.add_argument('--headless', action='store_true', help='Run Chrome in headless mode')
    args = parser.parse_args()

    phrases = args.phrase if args.phrase else ['HPE Partner Ready Portal', 'Partner Ready Portal']
    out = run(args.username, args.password, phrases, args.headless)
    print(f'Wrote matches to: {out}')
