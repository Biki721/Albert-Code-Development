def normalize_language(lang):
    """
    Normalize language names used across the project to avoid drift.
    Minimal, targeted fixes as requested:
    - 'LARSpanish' -> 'Spanish'
    - 'Taiwai' -> 'Taiwan'
    """
    if not isinstance(lang, str):
        return lang
    normalized = lang.strip()
    if normalized == 'LARSpanish':
        return 'Spanish'
    if normalized == 'Taiwai':
        return 'Taiwan'
    return normalized
