def load_home_prefixes(txt_path):
    prefixes = []
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith('#'):
                    continue
                prefixes.append(s.rstrip('/'))
    except FileNotFoundError:
        # Fall back to empty list if config missing
        prefixes = []
    return prefixes


def is_home_redirect_playwright(page, home_prefixes):
    try:
        # Ensure page initialization attempted; ignore errors
        final_url = (page.url or "").split('#')[0].rstrip('/')
    except Exception:
        final_url = ""
    return any(final_url == p for p in home_prefixes)
