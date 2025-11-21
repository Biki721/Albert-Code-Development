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


###############################################
# 2. Utility: Clean text
###############################################

def postprocess(error: str) -> str:
    error = ''.join([c for c in error if not c.isdigit()])
    error = re.sub('\W+', ' ', error)
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

    LANG_MAP = {
        'French': 'fr', 'German': 'de', 'Italian': 'it', 'Chinese': 'zh',
        'Russian': 'ru', 'Portugese': 'pt', 'Indonesian': 'id', 'Singaporean': 'en',
        'Korean': 'ko', 'Turkish': 'tr', 'Japanese': 'ja', 'Taiwan': 'zh',
        'Spanish': 'es', 'LARSpanish': 'es', 'English': 'en'
    }

    target_code = LANG_MAP[language]

    df = pd.read_excel('glossary.xlsx')
    col_name = f"{target_code}-{target_code.upper()}"
    glossary = [x for x in df[col_name] if isinstance(x, str)]

    ignored_chars = "*+^#%$),(!@_}{[]?><~=\|-:;"
    extra_allowed = [
        'ARTIKEL', 'Tools catalog102030',
        '© Copyright 2023 Hewlett Packard Enterprise Development, L.P.',
        'Competenza', 'Cancella', 'decrescente', 'Presidente',
        'ARTíCULO', 'Competencia Partner Ready', '5000', '6000',
        'fors', 'As a Service', 'h',
        '© Copyright 2022 Hewlett Packard Enterprise Development, L.P.'
    ]

    allowed_text.extend(extra_allowed)
    allowed_text = [x.strip() for x in allowed_text if x.strip()]

    text_lines = [line.strip() for line in extracted_text if line.strip()]
    text_lines.extend(article_titles)

    probable_errors = []

    for line in text_lines:
        clean = line.strip()

        if clean in allowed_text:
            continue
        if clean in glossary:
            continue

        probable_errors.append(clean)

    final_errors = []

    for line in probable_errors:

        if len(line) < 2:
            continue

        detected = detector.detect_language_of(line)
        if detected is None:
            continue

        lang_code = detected.iso_code_639_1.value   # "en"
        confidence = detector.compute_language_confidence(line, detected)

        if lang_code != target_code and confidence > 0.40:
            cleaned = postprocess(line)
            if cleaned and cleaned not in glossary:
                final_errors.append(cleaned)

    return list(set(final_errors))


###############################################
# 5. Master Function: Extract + Validate Page
###############################################

def callable_extract(link: str, html_page: str, soup: BeautifulSoup, lang: str):

    TRANS_TERMS = {
        'French': 'Français', 'German': 'Deutsch', 'Italian': "Italiano",
        'Chinese': '简体中文', 'Russian': 'Русский', 'Portugese': 'Português',
        'Indonesian': 'Bahasa indonesia', 'Korean': "한국어",
        'Turkish': "Türkçe", 'Japanese': "日本語",
        'Taiwan': "中文（台灣)", 'Spanish': 'Español',
        "LARSpanish": 'Español'
    }

    extract_tags = ["span", "h1", "h2", "a", "div", "tr"]
    class_filters = [
        'portlet-title-text','hide','hide-accessible','hide User',
        'sr-only','iconText','hide isPureHPE','dateFormat','size',
        'categoryName','categoryDescription','boldContent',
        'detailedContentText','articleSummary','articleDeails row',
        'controlsPagination pull-right','articleDownloadHeader',
        'articleformatSize','border_bottom','articleDownloadContent'
    ]

    allowed_text = []
    article_titles = articlenamechecker(soup, TRANS_TERMS[lang])

    #####################
    # CASE 1: PRP HOME
    #####################
    if link.strip() in ['https://partner.hpe.com/group/prp', 
                        "https://partner.hpe.com/group/prp/home"]:

        content = get_text(html_page).splitlines()
        content = [c.strip().lstrip("+").strip() for c in content if c.strip()]

        for tag in extract_tags:
            for element in soup.find_all(tag):
                allowed_text.append(element.get_text().strip())

            for cls in class_filters:
                for element in soup.find_all(tag, class_=cls):
                    allowed_text.append(element.get_text().strip())

    ###########################
    # CASE 2: DOCUMENT PAGES
    ###########################
    else:
        try:
            content = soup.find(id='main-content').get_text().splitlines()
        except:
            content = []

        content = [" ".join(c.split()) for c in content if c.strip()]

        for tag in extract_tags:
            for element in soup.find_all(tag):
                allowed_text.extend(element.get_text().splitlines())

            for cls in class_filters:
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

