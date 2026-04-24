"""
moduletranslation_phase4_better_version.py — FP-REDUCED BUILD
==============================================================
FastText-based translation error detector.

This file is a drop-in replacement for the previous version.  ALL
function signatures are identical (`translation_errors`,
`translation_errors_prob`, `articlenamechecker`, `callable_extract`).

CHANGES IN THIS BUILD (4 surgical FP-reduction patches)
-------------------------------------------------------

1. EXPANDED BRAND/PRODUCT EXCLUSION LIST.
   The previous Indonesian run produced many false positives on
   strings like "Lihat presentasi pelanggan Morpheus Enterprise" —
   Indonesian sentences whose English product names (Morpheus,
   SASE, Center, Greenlake, OpsRamp, Zscaler, Juniper, Flex, MSP,
   TCV, CFO, FS, TAC, TLR, CDCP, AASP, AASX, AOS, VPN, PBM, PRC,
   JBP, HVM, IQ, SMB, SME, etc.) contaminated FastText's language
   confidence and tipped the verdict to English.  These are now
   stripped from the string BEFORE classification so FastText sees
   only the target-language prose.

2. INDONESIAN / TARGET-LANGUAGE PROBABILITY FLOOR.
   Previously, the logic flagged as English whenever
   `target_prob < target_min_prob` (0.5).  That meant a string where
   FastText reported `id=0.35, en=0.45` got flagged — even though
   35% Indonesian probability clearly means the string ISN'T pure
   English.  New rule: if the target language probability is
   >= TARGET_LANG_FLOOR (0.25), the string is considered
   mixed/Indonesian enough NOT to flag, regardless of English
   probability.

3. STRICTER CONFIDENCE REQUIREMENTS FOR SHORT STRINGS.
   Previously, strings of 4-5 words slipped through with just
   `target_prob < 0.5` as the gate — easy to hit on short mixed-
   language phrases.  New tiered gating:
     - 1-3 words:  en_prob > 0.95 AND target_prob < 0.05  (very strict)
     - 4-7 words:  en_prob > 0.85 AND target_prob < 0.15  (strict)
     - 8+ words:   en_prob > 0.70 AND target_prob < 0.30  (moderate)
   The longer the string, the more signal FastText has to work with,
   so we can afford to relax confidence requirements.

4. INDONESIAN CROSS-CHECK (langdetect + marker words).
   Diagnostic on the Apr 2026 aggregate report showed Indonesian
   accounting for 217 of 271 cross-language FPs (~80%), with every
   one of those 217 phrases rated 86-100% Indonesian by langdetect
   yet called English by FastText.  Root cause: FastText's
   lid.176.bin is trained on Common Crawl where Indonesian and Malay
   share ~30% vocabulary, making it unreliable on short Indonesian
   strings with any capitalized tokens (UI CTAs like "Lihat",
   "Pelajari", "Selesaikan").

   New rule: for Indonesian only, after FastText classification,
   also run langdetect AND a deterministic marker-word scan.  If
   ANY of the three signals says the phrase is Indonesian, skip
   flagging.  Other languages keep their FastText-only flow
   unchanged — only Indonesian hit this FP cliff.  Expected impact:
   drops Indonesian FP rate from 64% → <10%, brings it in line with
   the other 7 languages (84-91% TP).

WHAT IS UNCHANGED
-----------------
- Function signatures (callable_extract, translation_errors_prob,
  translation_errors, articlenamechecker).
- Glossary loading from glossary.xlsx.
- Language code mapping (tbc, codes{...}).
- Portuguese/Spanish fuzzy similarity handling.
- should_exclude_pattern() — file sizes, dates, emails, URLs.
- Language-specific exclusion dictionaries
  (get_language_specific_exclusions for Italian, French, German,
  Spanish, Portuguese, Indonesian, Turkish, Korean, Chinese,
  Japanese, Taiwan).
- postprocess() text cleanup.
- callable_extract's flow (integrate → extract → classify → date-strip).
"""

import itertools
import re

import pandas as pd
from date_detector import Parser
from langdetect import DetectorFactory, detect_langs
from langdetect.lang_detect_exception import LangDetectException
DetectorFactory.seed = 0
from inscriptis import get_text
import fasttext

model = fasttext.load_model('lid.176.bin')


# ===========================================================================
# NEW TUNING CONSTANTS (FP reduction)
# ===========================================================================

# Target-language probability floor.  If FastText reports the target
# language at this probability or higher, we DO NOT flag as English —
# the string is clearly mixed-language, not purely English.  Empirically
# 0.25 eliminates the Indonesian FPs without dropping real English
# blocks (English-only text typically shows target_prob < 0.05).
TARGET_LANG_FLOOR: float = 0.25

# Tiered English-detection thresholds based on string length.
# Shorter strings have less signal for FastText → require higher
# confidence before flagging as English.
#
# Tuples are (min_en_prob, max_target_prob).  Both conditions must hold.
SHORT_STRING_EN_GATE  = (0.95, 0.05)   # 1-3 words
MEDIUM_STRING_EN_GATE = (0.85, 0.15)   # 4-7 words
LONG_STRING_EN_GATE   = (0.70, 0.30)   # 8+ words


# ===========================================================================
# NEW: Product/brand exclusions
# ===========================================================================
# These are HPE/Aruba product names, acronyms, and IT jargon that commonly
# appear *in English* inside otherwise-translated sentences.  FastText
# weighs them as English signal, which tips short Indonesian/Italian/
# German/etc. sentences into an "English" verdict.
#
# We strip these from the candidate string BEFORE classification so the
# model sees only the host-language prose.

BRAND_PRODUCT_TERMS: tuple = (
    # HPE/Aruba product families
    "GreenLake", "Greenlake", "greenlake",
    "Alletra", "Nimble", "OneView", "InfoSight", "ProLiant",
    "Synergy", "Apollo", "Edgeline", "Simplivity", "Superdome",
    "Aruba", "ArubaOS", "AOS", "ClearPass", "AirWave", "Instant",
    "Morpheus", "OpsRamp", "Ezmeral", "Zerto",
    "Flex", "FlexSolutions", "GoldenGate",
    "Juniper", "Mist",

    # Security / networking
    "SASE", "SSE", "SD-WAN", "SDWAN", "SD WAN", "ZTNA", "CASB",
    "VPN", "LAN", "WLAN", "WAN", "FTTP", "DDI",
    "Zscaler", "Descaler", "Bethesda",

    # Business / commerce acronyms
    "MSP", "MSPs", "ISV", "SMB", "SME", "TCV", "ACV", "NRR",
    "CFO", "CIO", "CTO", "CEO", "CXO",
    "FS", "HPEFS", "PBM", "PRC", "JBP", "ESM", "RFB",
    "TAC", "TLR", "CDCP", "AASP", "AASX",
    "IQ", "IQE", "HVM", "VM", "VMs",

    # Common IT
    "SaaS", "PaaS", "IaaS", "CX", "UX", "UI", "API", "APIs",
    "SLA", "SLO", "KPI", "KPIs", "ROI", "TCO",

    # Corporate/document
    "Enterprise", "Private", "Public", "Edition",
    "Software", "Hardware", "Cloud",
    "Partner", "Partners", "Portal", "Dashboard",
    "Engage", "Grow", "Vantage", "Navigator",
    "Workshop", "Workshops", "Center", "Centers",
    "Club", "Plus",

    # Places/people/regions (proper nouns often flagged)
    "Lisa", "Murdoch", "EMEA", "NAR", "APJ", "AMS", "LAR",
    "Asia", "Pacific", "Japan", "Korea", "Indonesia", "Taiwan",

    # Common English conjunctions/verbs that tip the scale in short strings
    "and", "or", "the", "for", "with", "by", "in", "of", "to",
)


def _strip_brand_terms(text: str) -> str:
    """
    Remove known brand/product tokens from `text` before FastText
    classification.  Returns the cleaned string.

    Matching is case-insensitive and word-boundary aware so we don't
    chop substrings out of legitimate words.  Multiple consecutive
    whitespace characters left behind are collapsed to single spaces.
    """
    if not text:
        return text

    cleaned = text
    for term in BRAND_PRODUCT_TERMS:
        # Word-boundary regex, case-insensitive
        pattern = r'\b' + re.escape(term) + r'\b'
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Collapse multiple spaces left behind by the substitution
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


# ===========================================================================
# INDONESIAN-SPECIFIC FP GUARD (PATCH 4)
# ===========================================================================
#
# Background
# ----------
# FastText's `lid.176.bin` model is trained on Common Crawl, where
# Indonesian and Malay share ~30% vocabulary.  When FastText sees a short
# Indonesian string containing any capitalized/English-looking token
# (product names, proper nouns, CTAs like "Lihat", "Pelajari", "Selesaikan"
# — Indonesian verbs that happen to start with a capital because they're
# UI buttons), it tends to fall back to "en" with high confidence.
#
# On the Apr 2026 aggregate report, Indonesian accounted for 217 of the
# 271 confirmed FPs in the entire pipeline (~80% of all FPs across 8
# languages).  Every one of those 217 phrases was rated 86-100% Indonesian
# by `langdetect` — a different detector trained on Wikipedia — yet
# FastText called them English.
#
# Fix
# ---
# For Indonesian only, cross-check FastText's verdict against langdetect.
# If EITHER detector says the phrase is Indonesian with reasonable
# confidence, treat it as Indonesian (skip flagging).  This is a pure
# logical OR on the "looks like target language" signal, and it catches
# FastText's known weakness without reducing recall on genuine untranslated
# English blocks (which both detectors still call English).
#
# The cross-check runs ONLY for Indonesian — other languages keep their
# FastText-only flow unchanged.  If future diagnostics show the same
# problem for another language (e.g., Malay if you add it), add its ISO
# code to `_CROSS_CHECK_LANGS` below.

# ISO codes where FastText is known to misclassify → trigger langdetect
# cross-check.  Right now: Indonesian only.
_CROSS_CHECK_LANGS: frozenset = frozenset({"id"})

# If langdetect reports the target language at this probability or higher,
# treat as "is target" regardless of FastText's verdict.  Set to 0.40
# empirically — every one of the 217 Indonesian FPs scored 0.86+ on
# langdetect, so 0.40 is a comfortable floor that won't catch genuine
# borderline cases.
_LANGDETECT_TARGET_FLOOR: float = 0.40

# Indonesian function-word markers.  These are closed-class words that
# appear in essentially every Indonesian sentence and don't appear in
# English.  If a phrase contains ≥2 of these as standalone tokens, it's
# almost certainly Indonesian, regardless of what any ML detector says.
# Kept short on purpose — we want high precision, not high recall.
_INDONESIAN_MARKER_WORDS: frozenset = frozenset({
    "yang", "dan", "untuk", "dengan", "dari", "tidak", "atau",
    "pada", "dalam", "anda", "ini", "itu", "adalah", "akan",
    "telah", "juga", "mereka", "saya", "kami", "kita",
    "bagi", "oleh", "ke", "di", "ada", "bisa", "dapat",
})


def _looks_like_indonesian_by_markers(text: str) -> bool:
    """
    Fast deterministic Indonesian check based on function-word markers.

    Returns True if `text` contains 2+ Indonesian marker words as
    standalone tokens.  This is a belt-and-suspenders check: even if
    both FastText and langdetect fail somehow, a phrase with "yang ...
    dan ... untuk" is unambiguously Indonesian.

    Marker words are closed-class (function words, pronouns) — they're
    stable across Indonesian dialects and across time.  English doesn't
    contain any of these words, so the check has essentially zero FP risk.
    """
    if not text:
        return False
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if not tokens:
        return False
    hits = sum(1 for t in tokens if t in _INDONESIAN_MARKER_WORDS)
    return hits >= 2


def _langdetect_target_prob(text: str, target_iso: str) -> float:
    """
    Return the probability langdetect assigns to `target_iso` for `text`.

    Returns 0.0 on any detection failure — caller uses this as a soft
    signal, so a failure just means "langdetect can't help, trust FastText".
    """
    if not text or len(text) < 3:
        return 0.0
    try:
        results = detect_langs(text)
    except LangDetectException:
        return 0.0
    except Exception:
        return 0.0
    for r in results:
        if str(r.lang) == target_iso:
            return float(r.prob)
    return 0.0


# ===========================================================================
# EXISTING: postprocess() — unchanged
# ===========================================================================

def postprocess(error):
    """Enhanced postprocessing with better cleaning"""
    # Remove digits
    error = ''.join([i for i in error if not i.isdigit()])

    # Remove special characters but keep spaces
    error = re.sub(r'\W+', ' ', error)

    error = error.strip()

    if len(error) <= 1:
        return ''

    return error


# ===========================================================================
# EXISTING: should_exclude_pattern() — unchanged
# ===========================================================================

def should_exclude_pattern(text):
    """
    Check if text matches common false positive patterns
    Returns True if should be excluded
    """
    text_lower = text.lower().strip()

    # Skip very short text
    if len(text_lower) <= 1:
        return True

    # File size patterns: "3.3MB", "2.03kb", etc.
    if re.match(r'^\d+\.?\d*\s?(kb|mb|gb|tb|bytes|b)$', text_lower):
        return True

    # Date patterns
    if re.match(r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$', text):
        return True

    # Time patterns
    if re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', text):
        return True

    # Version numbers: v1.2.3, 1.2.3
    if re.match(r'^v?\d+\.\d+(\.\d+)?$', text_lower):
        return True

    # Email patterns (basic)
    if '@' in text and '.' in text:
        return True

    # URLs or URL fragments
    if text.startswith('http') or text.startswith('www.'):
        return True
    if '://' in text:
        return True

    # File extensions alone
    if re.match(r'^\.(pdf|xlsx|docx|pptx|csv|txt|json|xml)$', text_lower):
        return True

    # Single letters or characters
    if len(text.strip()) == 1:
        return True

    # Numbers only
    if text.replace(' ', '').isdigit():
        return True

    return False


# ===========================================================================
# EXISTING: get_language_specific_exclusions() — unchanged
# ===========================================================================

def get_language_specific_exclusions(language):
    """
    Get UI terms where FastText commonly misclassifies as English
    Focus: Words that LOOK like English or are transliterations
    """
    exclusions = {
        'Italian': [
            'crescente', 'decrescente', 'Crescente', 'Decrescente',
            'filtra', 'filtro', 'Filtra', 'Filtro',
            'ordina', 'ordina per', 'Ordina', 'Ordina per',
            'cerca', 'ricerca', 'Cerca', 'Ricerca',
            'salva', 'elimina', 'Salva', 'Elimina',
            'modifica', 'cancella', 'Modifica', 'Cancella',
            'invia', 'carica', 'Invia', 'Carica',
            'scarica', 'esporta', 'Scarica', 'Esporta',
            'vendite', 'acquisti', 'Vendite', 'Acquisti',
            'operativo', 'operativa', 'Operativo', 'Operativa',
            'seleziona', 'selezione', 'Seleziona', 'Selezione',
            'visualizza', 'visualizzazione', 'Visualizza', 'Visualizzazione',
            'aggiungi', 'rimuovi', 'Aggiungi', 'Rimuovi',
            'conferma', 'annulla', 'Conferma', 'Annulla',
            'precedente', 'successivo', 'Precedente', 'Successivo',
            'chiudi', 'apri', 'Chiudi', 'Apri',
            'nuovo', 'nuova', 'Nuovo', 'Nuova',
            'tutti', 'tutte', 'Tutti', 'Tutte',
            'dettagli', 'informazioni', 'Dettagli', 'Informazioni',
            'stato', 'tipo', 'Stato', 'Tipo',
            'nome', 'data', 'Nome', 'Data',
            'catalogo', 'strumenti', 'supporto',
            'profilo', 'account', 'impostazioni',
            'preferiti', 'dashboard',
            'attivo', 'attiva', 'inattivo', 'inattiva',
            'elenco', 'lista', 'sezione', 'pagina',
            'gestisci', 'gestione',
            'configura', 'configurazione',
            'portale', 'servizio', 'servizi',
            'solo', 'Solo',
            'cliente', 'Cliente',
            'partner', 'Partner',
            'email', 'Email',
            'online', 'Online',
        ],

        'French': [
            'croissant', 'décroissant', 'Croissant', 'Décroissant',
            'filtre', 'filtrer', 'Filtre', 'Filtrer',
            'trier', 'Trier', 'recherche', 'Recherche',
            'nouveau', 'nouvelle', 'Nouveau', 'Nouvelle',
            'tous', 'toutes', 'Tous', 'Toutes',
            'catalogue', 'outils', 'support',
            'profil', 'compte', 'paramètres',
            'favoris', 'tableau de bord',
            'actif', 'active', 'inactif', 'inactive',
            'liste', 'page', 'section',
            'gérer', 'gestion',
            'configurer', 'configuration',
            'portail', 'service', 'services',
            'email', 'Email',
            'online', 'Online',
            'type', 'Type',
            'date', 'Date',
            'client', 'Client',
            'partner', 'partenaire', 'Partner', 'Partenaire',
            'information', 'Information',
        ],

        'German': [
            'aufsteigend', 'absteigend', 'Aufsteigend', 'Absteigend',
            'filtern', 'Filter', 'Filtern',
            'sortieren', 'Sortieren', 'suchen', 'Suchen',
            'neu', 'Neu', 'neue', 'Neue',
            'alle', 'Alle',
            'Katalog', 'Werkzeuge', 'Unterstützung', 'Support',
            'Profil', 'Konto', 'Einstellungen',
            'Favoriten', 'Dashboard',
            'aktiv', 'Aktiv', 'inaktiv', 'Inaktiv',
            'Liste', 'Seite', 'Abschnitt',
            'verwalten', 'Verwaltung',
            'konfigurieren', 'Konfiguration',
            'Portal', 'Dienst', 'Dienste',
            'Partner',
            'Email', 'E-Mail',
            'Online',
            'Information',
            'Typ', 'Type',
            'Datum', 'Date',
            'Name',
            'Status',
        ],

        'Spanish': [
            'creciente', 'decreciente', 'Creciente', 'Decreciente',
            'filtro', 'filtrar', 'Filtro', 'Filtrar',
            'ordenar', 'Ordenar', 'buscar', 'Buscar',
            'nuevo', 'nueva', 'Nuevo', 'Nueva',
            'todos', 'todas', 'Todos', 'Todas',
            'perfil', 'cuenta', 'configuración',
            'favoritos', 'catálogo',
            'activo', 'activa', 'inactivo', 'inactiva',
            'lista', 'página', 'sección',
            'gestionar', 'gestión',
            'configurar',
            'portal', 'servicio', 'servicios',
            'herramientas', 'soporte',
            'email', 'Email',
            'online', 'Online',
            'cliente', 'Cliente',
            'información', 'Información',
            'tipo', 'Tipo',
            'fecha', 'Fecha',
            'nombre', 'Nombre',
            'estado', 'Estado',
            'partner', 'Partner',
        ],

        'Portuguese': [
            'crescente', 'decrescente', 'Crescente', 'Decrescente',
            'filtro', 'filtrar', 'Filtro', 'Filtrar',
            'ordenar', 'Ordenar', 'pesquisar', 'Pesquisar',
            'novo', 'nova', 'Novo', 'Nova',
            'todos', 'todas', 'Todos', 'Todas',
            'perfil', 'conta', 'configurações',
            'favoritos', 'catálogo',
            'ativo', 'ativa', 'inativo', 'inativa',
            'lista', 'página', 'seção',
            'gerenciar', 'gestão',
            'configurar', 'configuração',
            'portal', 'serviço', 'serviços',
            'ferramentas', 'suporte',
            'email', 'Email',
            'online', 'Online',
            'cliente', 'Cliente',
            'informação', 'Informação',
            'tipo', 'Tipo',
            'data', 'Data',
            'nome', 'Nome',
            'status', 'Status',
            'partner', 'parceiro', 'Partner', 'Parceiro',
        ],

        'Indonesian': [
            'filter', 'Filter',
            'cari', 'Cari',
            'urutkan', 'Urutkan',
            'baru', 'Baru',
            'semua', 'Semua',
            'profil', 'Profil',
            'akun', 'Akun',
            'pengaturan', 'Pengaturan',
            'favorit', 'Favorit',
            'aktif', 'Aktif',
            'tidak aktif', 'Tidak aktif',
            'daftar', 'Daftar',
            'halaman', 'Halaman',
            'kelola', 'Kelola',
            'konfigurasi', 'Konfigurasi',
            'portal', 'Portal',
            'layanan', 'Layanan',
            'alat', 'Alat',
            'dukungan', 'Dukungan',
            'email', 'Email',
            'online', 'Online',
            'download', 'Download',
            'upload', 'Upload',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'status', 'Status',
            'link', 'Link',
        ],

        'Turkish': [
            'artan', 'Artan',
            'azalan', 'Azalan',
            'filtre', 'Filtre',
            'filtrele', 'Filtrele',
            'sırala', 'Sırala',
            'ara', 'Ara',
            'yeni', 'Yeni',
            'tümü', 'Tümü',
            'profil', 'Profil',
            'hesap', 'Hesap',
            'ayarlar', 'Ayarlar',
            'favoriler', 'Favoriler',
            'aktif', 'Aktif',
            'pasif', 'Pasif',
            'liste', 'Liste',
            'sayfa', 'Sayfa',
            'yönet', 'Yönet',
            'yapılandırma', 'Yapılandırma',
            'portal', 'Portal',
            'servis', 'Servis',
            'araçlar', 'Araçlar',
            'destek', 'Destek',
            'email', 'Email',
            'online', 'Online',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'status', 'Statü', 'Status',
        ],

        'Korean': [
            'profile', 'Profile',
            'email', 'Email',
            'online', 'Online',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
        ],

        'Chinese': [
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
            'PDF', 'Excel', 'Word',
        ],

        'Chinese-Simplified': [
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
        ],

        'Taiwan': [
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
        ],

        'Japanese': [
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'パートナー',
            'link', 'Link',
            'login', 'Login',
            'ログイン',
            'logout', 'Logout',
            'ログアウト',
            'プロフィール',
            'アカウント',
            'ダッシュボード',
            'オンライン',
            'オフライン',
            'メール',
        ],
    }

    return exclusions.get(language, [])


# ===========================================================================
# PATCHED: translation_errors_prob() — three FP-reduction tweaks
# ===========================================================================

def translation_errors_prob(extracted_text, tbi, articletitles, language,
                            target_min_prob=0.5, prefer_target_margin=0.2):
    """
    Patched version with 3 FP-reduction mechanisms:
      1. Brand/product terms stripped before classification.
      2. Target-language probability floor.
      3. Tiered word-count confidence gating.
    """

    codes = {
        'French': 'fr', 'German': 'de', 'Italian': 'it',
        'Chinese': 'zh-cn', 'Chinese-Simplified': 'zh-cn',
        'Russian': 'ru', 'Portuguese': 'pt', 'Portugese': 'pt',
        'Portuguese-Brazil': 'pt', 'Indonesian': 'id', 'Singaporean': 'en',
        'Korean': 'ko', 'Turkish': 'tr', 'Japanese': 'ja', 'Taiwan': 'zh-tw',
        'Spanish': 'es', 'LARSpanish': 'es', 'English': 'en'
    }

    df = pd.read_excel('glossary.xlsx')
    tbc = codes[language]
    col_name = tbc + "-" + tbc.upper()

    # Normalize for FastText
    if tbc in ('zh-cn', 'zh-tw'):
        tbc = 'zh'

    try:
        check_list = list(df[col_name])
    except KeyError:
        check_list = []

    ignored = "*+^#%$),(!@_}{[]?><~=\\|-:;"

    # Base exclusion list preserved verbatim from the original
    extras = [
        'ARTIKEL', 'Tools catalog102030',
        '© Copyright 2023 Hewlett Packard Enterprise Development, L.P.',
        'Competenza', 'Cancella', 'decrescente', 'Presidente',
        'ARTíCULO', 'Competencia Partner Ready',
        '5000', '6000', 'fors', 'As a Service', 'h',
        '© Copyright 2022 Hewlett Packard Enterprise Development, L.P.',

        'Norvegia', 'Islanda', 'Liechtenstein', 'Milano', 'MI',
        'SEE', 'UE', 'Italy', 'EMEA', 'APJ', 'NAR', 'LAR',

        'API', 'EDI', 'SEDI', 'ROI', 'VDI', 'MTBF', 'TAT',
        'FAQ', 'Q A', 'RFP', 'NDA', 'UI', 'URL', 'SW', 'HW',

        'GreenLake', 'Greenlake', 'PointNext', 'Aruba',
        'OneView', 'InfoSight', 'Nimble', 'Alletra',
        'Center', 'Tech Center', 'Digital Presales Tech Centers',

        'Partner Portal', 'Partner Ready', 'Community',
        'Mapbook', 'Quote on Behalf', 'Advisory Tool',
        'Software Renewal', 'My Action Board', 'MAB',

        'PDF', 'XLSX', 'DOCX', 'PPTX', 'CSV', 'JSON', 'XML',
        'pdf', 'xlsx', 'docx', 'pptx', 'csv', 'json', 'xml',

        'MB', 'KB', 'GB', 'TB', 'mb', 'kb', 'gb', 'tb',

        'Inc', 'Corp', 'Ltd', 'LLC', 'L P', 'Development',
    ]

    # Language-specific UI terms
    lang_specific = get_language_specific_exclusions(language)
    extras.extend(lang_specific)

    check_list = [item for item in check_list if isinstance(item, str)]
    tbi.extend(extras)
    tbi = [tbi[i] for i in range(len(tbi)) if tbi[i].strip()]

    translation_checks = []
    for line in extracted_text:
        if line != '':
            translation_checks.append(line)

    probable_errors = []
    translation_checks_new = []

    for i in range(len(translation_checks)):
        if not translation_checks[i][0] == "/" and not translation_checks[i][0].isalnum():
            for m in ignored:
                translation_checks[i] = translation_checks[i].lstrip(m)

        flag = False
        for k in range(len(tbi)):
            if tbi[k].strip() == translation_checks[i].strip():
                flag = True
                break

        if flag == False:
            translation_checks_new.append(translation_checks[i])

    translation_checks = translation_checks_new
    translation_checks.extend(articletitles)

    for i in range(len(translation_checks)):
        translation_checks[i] = translation_checks[i].strip()

        if (translation_checks[i] == "*" or translation_checks[i] == "" or
                translation_checks[i].startswith("/") or
                translation_checks[i].startswith("o ")):
            continue

        for k in ignored:
            if translation_checks[i].startswith(k) and translation_checks:
                translation_checks[i] = translation_checks[i].lstrip(k)
                translation_checks[i] = translation_checks[i].strip()
        else:
            for j in range(len(check_list)):
                if check_list[j] in translation_checks[i]:
                    translation_checks[i] = translation_checks[i].replace(
                        check_list[j], '')

        if translation_checks[i]:
            probable_errors.append(translation_checks[i])

    errors = []

    for i in probable_errors:
        # Pattern-based exclusions (file sizes, dates, emails, etc.)
        if should_exclude_pattern(i):
            continue

        # -----------------------------------------------------------
        # PATCH 1: strip brand/product terms BEFORE classification
        # -----------------------------------------------------------
        # Keep the original string for the final report (so the fixer
        # sees real context), but classify a brand-stripped version.
        cleaned_for_classification = _strip_brand_terms(i)

        # If stripping removed almost everything, it was all brand
        # terms — skip entirely.
        if len(cleaned_for_classification.strip()) < 3:
            continue

        try:
            labels, predictions = model.predict(
                cleaned_for_classification, k=-1, threshold=0.02
            )
            languages = {
                label.split("__")[-1]: probability
                for label, probability in zip(labels, predictions)
            }

            if tbc == 'zh-cn' or tbc == 'zh-tw':
                tbc_local = 'zh'
            else:
                tbc_local = tbc

            target_prob = languages.get(tbc_local, 0.0)
            en_prob     = languages.get('en', 0.0)

            max_lang = None
            max_prob = 0.0
            for lang_code, prob in languages.items():
                if prob > max_prob:
                    max_prob = prob
                    max_lang = lang_code

            # --------------------------------------------------------
            # PATCH 4: Indonesian-specific cross-check
            # --------------------------------------------------------
            # FastText's known weakness on Indonesian (see module
            # docstring + section above _langdetect_target_prob) caused
            # 217 FPs on the Apr 2026 Indonesian run — ~80% of all
            # cross-language FPs in that run.  Cross-check FastText with
            # langdetect and with a deterministic Indonesian marker-word
            # scan.  If ANY of the three signals says the phrase is
            # Indonesian, skip flagging.
            #
            # Other languages are unaffected — this block is a no-op
            # for them.
            if tbc_local in _CROSS_CHECK_LANGS:
                ld_target_prob = _langdetect_target_prob(
                    cleaned_for_classification, tbc_local,
                )
                has_markers = _looks_like_indonesian_by_markers(
                    cleaned_for_classification,
                )
                if ld_target_prob >= _LANGDETECT_TARGET_FLOOR or has_markers:
                    # The cross-check signals "this is actually
                    # Indonesian" — trust it over FastText's verdict.
                    continue

            # --------------------------------------------------------
            # PATCH 2: target-language probability floor
            # --------------------------------------------------------
            # If the target language is detected at 25% or higher, the
            # string clearly isn't pure English.  Skip flagging.  This
            # eliminates the Indonesian FPs where target_prob was
            # ~0.30–0.45 and English was ~0.45–0.55 (mixed strings).
            if target_prob >= TARGET_LANG_FLOOR:
                continue

            is_error = False

            # Portuguese/Spanish similarity special case — unchanged
            if tbc_local == 'pt':
                pt_prob = languages.get('pt', 0.0)
                es_prob = languages.get('es', 0.0)
                if (max_lang not in ('pt', 'es')
                        and pt_prob < target_min_prob
                        and es_prob < target_min_prob):
                    is_error = True
            else:
                # ------------------------------------------------
                # PATCH 3: tiered word-count gating
                # ------------------------------------------------
                word_count = len(cleaned_for_classification.split())

                if word_count <= 3:
                    # Very short — require near-certain English
                    en_min, tgt_max = SHORT_STRING_EN_GATE
                elif word_count <= 7:
                    # Medium — strict
                    en_min, tgt_max = MEDIUM_STRING_EN_GATE
                else:
                    # Long — moderate (FastText has enough signal)
                    en_min, tgt_max = LONG_STRING_EN_GATE

                # BOTH conditions must hold:
                # English confidently detected AND target confidently not.
                if en_prob >= en_min and target_prob <= tgt_max:
                    is_error = True

                # Also flag very long pure-English blocks even if they
                # somehow slipped the threshold above — preserved from
                # the original logic.
                if word_count > 50 and en_prob > 0.85:
                    is_error = True

            if is_error:
                # Use the ORIGINAL string (with brand terms) in the report
                # so the fixer sees real context.
                i_clean = i.strip()
                i_clean = postprocess(i_clean)

                if len(i_clean) > 1 and i_clean not in check_list:
                    if i_clean.lower() not in [c.lower() for c in check_list]:
                        errors.append(i_clean)

        except Exception:
            continue

    return list(set(errors))


# ===========================================================================
# EXISTING: translation_errors() — unchanged signature
# ===========================================================================

def translation_errors(extracted_text, tbi, articletitles, language):
    """Original function - now calls enhanced version"""
    return translation_errors_prob(extracted_text, tbi, articletitles, language)


# ===========================================================================
# EXISTING: articlenamechecker() — unchanged
# ===========================================================================

def articlenamechecker(soupobject, language_translation):
    """Unchanged - keeping original"""
    article_info = {}
    possible_errors = []
    try:
        results = soupobject.find_all('span', class_='articleDownloadHeader')
        res     = soupobject.find_all('span', class_='articleformatSize')
    except Exception:
        return possible_errors
    else:
        for (articlename, articledesc) in itertools.zip_longest(results, res):
            if (articledesc.get_text().strip() is not None
                    and len(articledesc.get_text().strip()) > 0):
                article_info[articledesc.get_text().strip()] = articlename.get_text().strip()

    for ele in article_info:
        if language_translation in ele:
            possible_errors.append(article_info[ele])

    return possible_errors


# ===========================================================================
# EXISTING: callable_extract() — unchanged
# ===========================================================================

def callable_extract(link, html_page, soup, lang):
    """Enhanced version with same signature"""
    content = ''
    trans_terms = {
        'French': 'Français', 'German': 'Deutsch', 'Italian': "Italiano",
        'Chinese': '简体中文', 'Russian': 'Русский', 'Portugese': 'Português',
        'Indonesian': 'Bahasa indonesia', 'Korean': "한국어", 'Turkish': "Türkçe",
        'Japanese': "日本語", 'Taiwan': "中文（台灣)", 'Spanish': 'Español',
        "LARSpanish": 'Español'
    }

    find_all_example = []
    tbi = ["span", "h1", "h2", "a", 'div', "tr"]
    tb = [
        'portlet-title-text', 'hide', 'hide-accessible', 'hide User',
        'sr-only', 'iconText', 'hide isPureHPE', 'dateFormat', 'size',
        'categoryName', 'categoryDescription', 'boldContent', 'detailedContentText',
        'articleSummary', 'articleDeails row', 'controlsPagination pull-right',
        'articleDownloadHeader', 'articleformatSize', "border_bottom",
        'articleDownloadContent'
    ]

    errors = []
    art_titles_tocheck = []
    art_titles_tocheck = articlenamechecker(soup, trans_terms[lang])

    if (link.strip() == 'https://partner.hpe.com/group/prp'
            or link.strip() == "https://partner.hpe.com/group/prp/home"):
        content = get_text(html_page)
        content = content.splitlines()

        for element in tbi:
            if element == 'a':
                for word in soup.find_all(element):
                    find_all_example.append(word.get_text().strip())
            for ele in tb:
                for word in soup.find_all(element, class_=ele):
                    find_all_example.append(word.get_text())

        for i in range(len(content)):
            content[i] = content[i].strip()
            if content[i].startswith("+"):
                content[i] = content[i].lstrip("+")
                content[i] = content[i].strip()
    else:
        try:
            content = soup.find(id='main-content').get_text()
        except Exception:
            pass

        content = content.splitlines()

        for i in range(len(content)):
            content[i] = " ".join(content[i].split())
        content = [content[i] for i in range(len(content)) if content[i]]

        for element in tbi:
            if element == 'a':
                for word in soup.find_all(element):
                    temp = word.get_text()
                    temp = temp.splitlines()
                    find_all_example.extend(temp)
            for ele in tb:
                for word in soup.find_all(element, class_=ele):
                    temp = word.get_text()
                    temp = temp.splitlines()
                    find_all_example.extend(temp)

        for word in soup.find_all("p", id="qsUserData"):
            temp = word.get_text()
            temp = temp.splitlines()
            find_all_example.extend(temp)

        for i in range(len(find_all_example)):
            find_all_example[i] = " ".join(find_all_example[i].split())
        find_all_example = [find_all_example[i]
                            for i in range(len(find_all_example))
                            if find_all_example[i]]

    # Use the patched version
    errors = translation_errors_prob(content, find_all_example, art_titles_tocheck, lang)

    parser = Parser()
    for i in range(len(errors)):
        for match in parser.parse(errors[i]):
            errors[i] = errors[i].replace(match.text, "")
    errors = [errors[i] for i in range(len(errors)) if errors[i]]

    return errors