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


def is_home_redirect_selenium(driver, home_prefixes):
    try:
        # Ensure page initialization attempted; ignore errors
        _ = driver.execute_script("return document.readyState")
    except Exception:
        pass
    final_url = (driver.current_url or "").split('#')[0].rstrip('/')
    return any(final_url == p or final_url.startswith(p) for p in home_prefixes)
