# translation_validator.py

import re
import pandas as pd
import itertools
from inscriptis import get_text
from bs4 import BeautifulSoup
from date_detector import Parser
from lingua import Language, LanguageDetectorBuilder

###############################################
# 1. Modern Language Detector Initialization
###############################################

SUPPORTED_LANGS = [
    Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.SPANISH,
    Language.PORTUGUESE, Language.ITALIAN, Language.CHINESE, Language.JAPANESE,
    Language.KOREAN, Language.RUSSIAN, Language.TURKISH, Language.INDONESIAN
]

detector = LanguageDetectorBuilder.from_languages(*SUPPORTED_LANGS) \
                                  .with_preloaded_language_models() \
                                  .build()

LANG_MAP = {
    'French': 'fr', 'German': 'de', 'Italian': 'it', 'Chinese': 'zh', 'Chinese-Simplified': 'zh',
    'Russian': 'ru', 'Portugese': 'pt', 'Portuguese-Brazil': 'pt', 'Indonesian': 'id', 'Singaporean': 'en',
    'Korean': 'ko', 'Turkish': 'tr', 'Japanese': 'ja', 'Taiwan': 'zh',
    'Spanish': 'es', 'LARSpanish': 'es', 'English': 'en'
}

TRANS_TERMS = {
    'French': 'Français', 'German': 'Deutsch', 'Italian': "Italiano",
    'Chinese': '简体中文', 'Chinese-Simplified': '简体中文', 'Russian': 'Русский',
    'Portugese': 'Português', 'Portuguese-Brazil': 'Português',
    'Indonesian': 'Bahasa indonesia', 'Korean': "한국어",
    'Turkish': "Türkçe", 'Japanese': "日本語",
    'Taiwan': "中文（台灣)", 'Spanish': 'Español',
    "LARSpanish": 'Español'
}

EXTRACT_TAGS = ["span", "h1", "h2", "a", "div", "tr"]

CLASS_FILTERS = [
    'portlet-title-text', 'hide', 'hide-accessible', 'hide User',
    'sr-only', 'iconText', 'hide isPureHPE', 'dateFormat', 'size',
    'categoryName', 'categoryDescription', 'boldContent',
    'detailedContentText', 'articleSummary', 'articleDeails row',
    'controlsPagination pull-right', 'articleDownloadHeader',
    'articleformatSize', 'border_bottom', 'articleDownloadContent'
]

EXTRA_ALLOWED = [
    'ARTIKEL', 'Tools catalog102030',
    '© Copyright 2023 Hewlett Packard Enterprise Development, L.P.',
    'Competenza', 'Cancella', 'decrescente', 'Presidente',
    'ARTíCULO', 'Competencia Partner Ready', '5000', '6000',
    'fors', 'As a Service', 'h',
    '© Copyright 2022 Hewlett Packard Enterprise Development, L.P.'
]

_GLOSSARY_CACHE = {}


def _load_glossary_for_language(target_code: str):
    if target_code in _GLOSSARY_CACHE:
        return _GLOSSARY_CACHE[target_code]

    df = pd.read_excel('glossary.xlsx')
    col_name = f"{target_code}-{target_code.upper()}"
    if col_name not in df.columns:
        glossary = set()
    else:
        glossary = {x.strip() for x in df[col_name] if isinstance(x, str) and x.strip()}

    _GLOSSARY_CACHE[target_code] = glossary
    return glossary


###############################################
# 2. Utility: Clean text
###############################################

def postprocess(error: str) -> str:
    error = ''.join([c for c in error if not c.isdigit()])
    error = re.sub(r'\W+', ' ', error)
    error = error.strip()

    return error if len(error) > 1 else ""


###############################################
# 3. Extract article name translation errors
###############################################

def articlenamechecker(soup: BeautifulSoup, language_translation: str):
    article_info = {}
    possible_errors = []

    try:
        names = soup.find_all('span', class_='articleDownloadHeader')
        descs = soup.find_all('span', class_='articleformatSize')
    except:
        return possible_errors

    for name, desc in itertools.zip_longest(names, descs):
        if desc and desc.get_text().strip():
            article_info[desc.get_text().strip()] = name.get_text().strip()

    for key in article_info:
        if language_translation in key:
            possible_errors.append(article_info[key])

    return possible_errors


###############################################
# 4. Translation Error Detection (Lingua)
###############################################

def translation_errors(extracted_text, allowed_text, article_titles, language):
    """
    Lingua-based translation error detection, tuned to behave like the old
    fastText-based implementation in moduletranslation_part2.
    Signature is unchanged.
    """
    target_code = LANG_MAP[language]          # e.g. 'fr', 'de', 'pt', 'zh', 'ko', ...
    glossary = _load_glossary_for_language(target_code)

    # Characters treated as ignorable at the start of a line (same idea as part2)
    ignored_chars = "*+^#%$),(!@_}{[]?><~=\\|-:;"

    # ------------------------------------------------------------------
    # 1) Build allowed / whitelist set  (allowed_text + EXTRA_ALLOWED)
    # ------------------------------------------------------------------
    allowed_clean = []
    for txt in itertools.chain(allowed_text, EXTRA_ALLOWED):
        if not txt:
            continue
        s = txt.strip()
        if s:
            allowed_clean.append(s)
    allowed_set = set(allowed_clean)

    # ------------------------------------------------------------------
    # 2) Collect candidate lines from page content + article titles
    # ------------------------------------------------------------------
    candidates = []

    for line in extracted_text:
        if not line:
            continue
        s = line.strip()
        if s:
            candidates.append(s)

    for title in article_titles:
        if not title:
            continue
        s = title.strip()
        if s:
            candidates.append(s)

    # ------------------------------------------------------------------
    # 3) Apply text-level filters similar to part2 and remove glossary
    #    substrings, producing probable error fragments
    # ------------------------------------------------------------------
    probable_errors = []

    for line in candidates:
        text = line.strip()
        if not text:
            continue

        # Skip obvious non-content patterns
        if text == "*" or text.startswith("/") or text.startswith("o "):
            continue

        # Strip leading punctuation (similar to old lstrip over "ignored")
        if not text[0].isalnum() and text[0] != "/":
            text = text.lstrip(ignored_chars).strip()
            if not text:
                continue

        # Skip exact allowed UI strings etc.
        if text in allowed_set:
            continue

        # Remove glossary terms as substrings (like part2 did)
        reduced = text
        for term in glossary:
            if term and term in reduced:
                reduced = reduced.replace(term, "")
        reduced = reduced.strip()
        if not reduced:
            continue

        probable_errors.append(reduced)

    # ------------------------------------------------------------------
    # 4) Prepare Language enums for confidence computation
    # ------------------------------------------------------------------
    target_lang = None
    spanish_lang = None
    for lang_enum in SUPPORTED_LANGS:
        code = lang_enum.iso_code_639_1.name.lower()
        if code == target_code:
            target_lang = lang_enum
        if code == "es":
            spanish_lang = lang_enum

    # Rough analogue of fastText's 0.02 presence threshold,
    # but on Lingua's 0–1 confidence scale (tunable if needed)
    MIN_TARGET_CONF = 0.20

    errors = set()

    # ------------------------------------------------------------------
    # 5) Use Lingua confidences to decide if target language is "present"
    #    (or Spanish for Portuguese), otherwise flag as translation error
    # ------------------------------------------------------------------
    for text in probable_errors:
        if len(text) < 2:
            continue
        if not any(ch.isalpha() for ch in text):
            continue

        try:
            if target_lang is None:
                # Fallback: use top language only if we somehow
                # couldn't map to a Language enum (should not happen)
                detected = detector.detect_language_of(text)
                if detected is None:
                    continue
                lang_code = detected.iso_code_639_1.name.lower()
                conf = detector.compute_language_confidence(text, detected)

                if lang_code != target_code and conf >= MIN_TARGET_CONF:
                    cleaned = postprocess(text)
                    if cleaned and cleaned not in glossary:
                        errors.add(cleaned)
                continue

            # Primary path: check confidence for the *target* language directly
            target_conf = detector.compute_language_confidence(text, target_lang)

            # Special-case for Portuguese: accept Spanish as "close enough"
            if target_code == "pt" and spanish_lang is not None:
                spanish_conf = detector.compute_language_confidence(text, spanish_lang)
            else:
                spanish_conf = 0.0

            # Decide if this text is OK in the page's language
            if target_code == "pt":
                is_ok = max(target_conf, spanish_conf) >= MIN_TARGET_CONF
            else:
                is_ok = target_conf >= MIN_TARGET_CONF

            if not is_ok:
                cleaned = postprocess(text)
                if cleaned and cleaned not in glossary:
                    errors.add(cleaned)

        except Exception:
            # Be robust to any detector issues and keep scanning other lines
            continue

    return list(errors)

###############################################
# 5. Master Function: Extract + Validate Page
###############################################

def callable_extract(link: str, html_page: str, soup: BeautifulSoup, lang: str):

    allowed_text = []
    article_titles = articlenamechecker(soup, TRANS_TERMS[lang])

    #####################
    # CASE 1: PRP HOME
    #####################
    if link.strip() in ['https://partner.hpe.com/group/prp', 
                        "https://partner.hpe.com/group/prp/home"]:

        content = get_text(html_page).splitlines()
        content = [c.strip().lstrip("+").strip() for c in content if c.strip()]

        for tag in EXTRACT_TAGS:
            for element in soup.find_all(tag):
                text = element.get_text().strip()
                if text:
                    allowed_text.append(text)

            for cls in CLASS_FILTERS:
                for element in soup.find_all(tag, class_=cls):
                    text = element.get_text().strip()
                    if text:
                        allowed_text.append(text)

    ###########################
    # CASE 2: DOCUMENT PAGES
    ###########################
    else:
        try:
            content = soup.find(id='main-content').get_text().splitlines()
        except:
            content = []

        content = [" ".join(c.split()) for c in content if c.strip()]

        for tag in EXTRACT_TAGS:
            for element in soup.find_all(tag):
                allowed_text.extend(element.get_text().splitlines())

            for cls in CLASS_FILTERS:
                for element in soup.find_all(tag, class_=cls):
                    allowed_text.extend(element.get_text().splitlines())

        for p in soup.find_all("p", id="qsUserData"):
            allowed_text.extend(p.get_text().splitlines())

        allowed_text = [" ".join(t.split()) for t in allowed_text if t.strip()]

    #############################
    # LANGUAGE ERROR DETECTION
    #############################

    errors = translation_errors(content, allowed_text, article_titles, lang)

    #############################
    # REMOVE DATE PATTERNS
    #############################
    parser = Parser()
    cleaned = []

    for e in errors:
        cleaned_error = e
        for match in parser.parse(e):
            cleaned_error = cleaned_error.replace(match.text, "")
        cleaned_error = cleaned_error.strip()
        if cleaned_error:
            cleaned.append(cleaned_error)

    return cleaned

