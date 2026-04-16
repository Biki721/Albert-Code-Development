import itertools
from date_detector import Parser
from langdetect import DetectorFactory
DetectorFactory.seed = 0
import pandas as pd
from inscriptis import get_text
import fasttext
import re

model = fasttext.load_model('lid.176.bin')


def postprocess(error):
    """Enhanced postprocessing with better cleaning"""
    # Remove digits
    error = ''.join([i for i in error if not i.isdigit()])
    
    # Remove special characters but keep spaces
    error = re.sub('\W+', ' ', error)
    
    error = error.strip()
    
    if len(error) <= 1:
        return ''
    
    return error


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


def get_language_specific_exclusions(language):
    """
    Get UI terms where FastText commonly misclassifies as English
    Focus: Words that LOOK like English or are transliterations
    """
    exclusions = {
        'Italian': [
            # UI terms that FastText confuses with English
            'crescente', 'decrescente', 'Crescente', 'Decrescente',  # ascending/descending
            'filtra', 'filtro', 'Filtra', 'Filtro',  # filter (looks like English)
            'ordina', 'ordina per', 'Ordina', 'Ordina per',  # sort
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
            # Words that REALLY look like English
            'solo', 'Solo',  # "only" but looks like "solo"
            'cliente', 'Cliente',  # client
            'partner', 'Partner',  # same spelling
            'email', 'Email',  # same
            'online', 'Online',  # same
        ],
        
        'French': [
            # French words that look English or get confused
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
            # Words that look very English
            'email', 'Email',
            'online', 'Online',
            'type', 'Type',  # Same spelling
            'date', 'Date',  # Same spelling
            'client', 'Client',  # Same spelling
            'partner', 'partenaire', 'Partner', 'Partenaire',
            'information', 'Information',  # Same spelling
        ],
        
        'German': [
            # German words FastText confuses (often capitalized like nouns)
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
            # Cognates that look English
            'Partner',  # Same
            'Email', 'E-Mail',
            'Online',
            'Information',
            'Typ', 'Type',
            'Datum', 'Date',
            'Name',
            'Status',
        ],
        
        'Spanish': [
            # Spanish words that FastText mistakes for English
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
            # Cognates/similar to English
            'email', 'Email',
            'online', 'Online',
            'cliente', 'Cliente',  # client
            'información', 'Información',  # information
            'tipo', 'Tipo',  # type
            'fecha', 'Fecha',  # date (but looks like "fetch")
            'nombre', 'Nombre',  # name
            'estado', 'Estado',  # state/status
            'partner', 'Partner',
        ],
        
        'Portuguese': [
            # Portuguese (Brazil) - similar to Spanish but distinct
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
            # Looks English
            'email', 'Email',
            'online', 'Online',
            'cliente', 'Cliente',
            'informação', 'Informação',
            'tipo', 'Tipo',
            'data', 'Data',  # date (literally "data")
            'nome', 'Nome',
            'status', 'Status',  # Same
            'partner', 'parceiro', 'Partner', 'Parceiro',
        ],
        
        'Indonesian': [
            # Indonesian uses many English loanwords, but also has unique terms
            'filter', 'Filter',  # Actually used in Indonesian
            'cari', 'Cari',  # search
            'urutkan', 'Urutkan',  # sort
            'baru', 'Baru',  # new
            'semua', 'Semua',  # all
            'profil', 'Profil',
            'akun', 'Akun',
            'pengaturan', 'Pengaturan',  # settings
            'favorit', 'Favorit',
            'aktif', 'Aktif',
            'tidak aktif', 'Tidak aktif',
            'daftar', 'Daftar',  # list
            'halaman', 'Halaman',  # page
            'kelola', 'Kelola',  # manage
            'konfigurasi', 'Konfigurasi',
            'portal', 'Portal',
            'layanan', 'Layanan',  # service
            'alat', 'Alat',  # tools
            'dukungan', 'Dukungan',  # support
            # English loanwords commonly used
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
            # Turkish words that might confuse FastText
            'artan', 'Artan',  # ascending
            'azalan', 'Azalan',  # descending
            'filtre', 'Filtre',  # filter (borrowed from French)
            'filtrele', 'Filtrele',  # filter (verb)
            'sırala', 'Sırala',  # sort
            'ara', 'Ara',  # search
            'yeni', 'Yeni',  # new
            'tümü', 'Tümü',  # all
            'profil', 'Profil',
            'hesap', 'Hesap',  # account
            'ayarlar', 'Ayarlar',  # settings
            'favoriler', 'Favoriler',
            'aktif', 'Aktif',
            'pasif', 'Pasif',  # inactive
            'liste', 'Liste',
            'sayfa', 'Sayfa',  # page
            'yönet', 'Yönet',  # manage
            'yapılandırma', 'Yapılandırma', # configuration
            'portal', 'Portal',
            'servis', 'Servis',
            'araçlar', 'Araçlar',  # tools
            'destek', 'Destek',  # support
            # English loanwords
            'email', 'Email',
            'online', 'Online',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'status', 'Statü', 'Status',
        ],
        
        'Korean': [
            # Korean has Hangul script, so English loanwords in Hangul get detected as Korean
            # Focus on transliterated words that might appear in mixed content
            # Most UI will be in Hangul, but watch for:
            # Romanized terms that might appear
            'profile', 'Profile',  # Sometimes appears as-is
            'email', 'Email',
            'online', 'Online',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
            # Note: Most Korean UI will be correctly detected, but
            # mixed Korean-English strings might need attention
            # Add specific terms as you encounter false positives
        ],
        
        'Chinese': [  # Simplified
            # Chinese uses characters, English loanwords stand out
            # Focus on terms that might appear in mixed scripts
            'email', 'Email',
            'online', 'Online',  
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
            'PDF', 'Excel', 'Word',
            # Pinyin romanizations (if they appear in UI)
            # Note: Most Chinese UI correctly detected
            # Add specific terms as false positives appear
        ],
        
        'Chinese-Simplified': [  # Alias
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'link', 'Link',
            'login', 'Login',
            'logout', 'Logout',
        ],
        
        'Taiwan': [  # Traditional Chinese
            # Same as simplified but Traditional script
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
            # Japanese uses Kanji/Hiragana/Katakana, but English loanwords appear
            # Katakana words might get detected as mixed
            # Focus on Romaji and direct English inclusions
            'email', 'Email',
            'online', 'Online',
            'offline', 'Offline',
            'dashboard', 'Dashboard',
            'partner', 'Partner',
            'パートナー',  # "partner" in Katakana
            'link', 'Link',
            'login', 'Login',
            'ログイン',  # "login" in Katakana
            'logout', 'Logout',
            'ログアウト',  # "logout" in Katakana
            # Common Katakana IT terms that might appear
            'プロフィール',  # profile
            'アカウント',  # account
            'ダッシュボード',  # dashboard
            'オンライン',  # online
            'オフライン',  # offline
            'メール',  # mail/email
        ],
    }
    
    return exclusions.get(language, [])


def translation_errors_prob(extracted_text, tbi, articletitles, language, target_min_prob=0.5, prefer_target_margin=0.2):
    """Enhanced version with better false positive filtering"""
    
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
    
    # ENHANCED: More comprehensive extras list
    extras = [
        # Original extras
        'ARTIKEL', 'Tools catalog102030', 
        '© Copyright 2023 Hewlett Packard Enterprise Development, L.P.',
        'Competenza', 'Cancella', 'decrescente', 'Presidente', 
        'ARTíCULO', 'Competencia Partner Ready',
        '5000', '6000', 'fors', 'As a Service', 'h',
        '© Copyright 2022 Hewlett Packard Enterprise Development, L.P.',
        
        # Geographic names
        'Norvegia', 'Islanda', 'Liechtenstein', 'Milano', 'MI',
        'SEE', 'UE', 'Italy', 'EMEA', 'APJ', 'NAR', 'LAR',
        
        # Technical abbreviations (case insensitive will be handled)
        'API', 'EDI', 'SEDI', 'ROI', 'VDI', 'MTBF', 'TAT',
        'FAQ', 'Q A', 'RFP', 'NDA', 'UI', 'URL', 'SW', 'HW',
        
        # Product/Brand names (if they intentionally stay in English)
        'GreenLake', 'Greenlake', 'PointNext', 'Aruba',
        'OneView', 'InfoSight', 'Nimble', 'Alletra',
        'Center', 'Tech Center', 'Digital Presales Tech Centers',
        
        # Common English terms that may be intentionally kept
        'Partner Portal', 'Partner Ready', 'Community',
        'Mapbook', 'Quote on Behalf', 'Advisory Tool',
        'Software Renewal', 'My Action Board', 'MAB',
        
        # File formats
        'PDF', 'XLSX', 'DOCX', 'PPTX', 'CSV', 'JSON', 'XML',
        'pdf', 'xlsx', 'docx', 'pptx', 'csv', 'json', 'xml',
        
        # Units and measurements
        'MB', 'KB', 'GB', 'TB', 'mb', 'kb', 'gb', 'tb',
        
        # Common abbreviations
        'Inc', 'Corp', 'Ltd', 'LLC', 'L P', 'Development',
    ]
    
    # Add language-specific UI terms
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
                translation_checks[i].startswith("/") or translation_checks[i].startswith("o ")):
            continue
        
        for k in ignored:
            if translation_checks[i].startswith(k) and translation_checks:
                translation_checks[i] = translation_checks[i].lstrip(k)
                translation_checks[i] = translation_checks[i].strip()
        else:
            for j in range(len(check_list)):
                if check_list[j] in translation_checks[i]:
                    translation_checks[i] = translation_checks[i].replace(check_list[j], '')
        
        if translation_checks[i]:
            probable_errors.append(translation_checks[i])
    
    errors = []
    
    for i in probable_errors:
        # ENHANCED: Pattern-based exclusions
        if should_exclude_pattern(i):
            continue
        
        try:
            labels, predictions = model.predict(i, k=-1, threshold=0.02)
            languages = {label.split("__")[-1]: probability for label, probability in zip(labels, predictions)}
            
            if tbc == 'zh-cn' or tbc == 'zh-tw':
                tbc = 'zh'
            
            target_prob = languages.get(tbc, 0.0)
            en_prob = languages.get('en', 0.0)
            
            max_lang = None
            max_prob = 0.0
            for lang_code, prob in languages.items():
                if prob > max_prob:
                    max_prob = prob
                    max_lang = lang_code
            
            is_error = False
            
            # ENHANCED: Better logic for Portuguese/Spanish similarity
            if tbc == 'pt':
                pt_prob = languages.get('pt', 0.0)
                es_prob = languages.get('es', 0.0)
                # Only flag if neither Portuguese nor Spanish is dominant
                if max_lang not in ('pt', 'es') and (pt_prob < target_min_prob and es_prob < target_min_prob):
                    is_error = True
            else:
                # ENHANCED: More sophisticated detection
                # Flag if target language probability is low
                if target_prob < target_min_prob:
                    # But only if it's not just low confidence overall
                    if max_prob > 0.3:  # Some language is detected with confidence
                        is_error = True
                
                # Flag if English is significantly more likely than target
                if en_prob > target_prob + prefer_target_margin:
                    is_error = True
                
                # ENHANCED: For very long text (50+ words), if English probability > 0.8, definitely an error
                word_count = len(i.split())
                if word_count > 50 and en_prob > 0.8:
                    is_error = True
                
                # ENHANCED: For short text (1-3 words), require higher confidence to flag
                if word_count <= 3:
                    if not (en_prob > 0.9 and target_prob < 0.1):
                        is_error = False
            
            if is_error:
                i_clean = i.strip()
                i_clean = postprocess(i_clean)
                
                # Final check: don't add if it's in check_list after postprocessing
                if len(i_clean) > 1 and i_clean not in check_list:
                    # Case-insensitive check against common exclusions
                    if i_clean.lower() not in [c.lower() for c in check_list]:
                        errors.append(i_clean)
        
        except Exception as e:
            continue
    
    return list(set(errors))


# Keep the original translation_errors function signature but redirect to enhanced version
def translation_errors(extracted_text, tbi, articletitles, language):
    """Original function - now calls enhanced version"""
    return translation_errors_prob(extracted_text, tbi, articletitles, language)


def articlenamechecker(soupobject, language_translation):
    """Unchanged - keeping original"""
    article_info = {}
    possible_errors = []
    try:
        results = soupobject.find_all('span', class_='articleDownloadHeader')
        res = soupobject.find_all('span', class_='articleformatSize')
    except:
        return possible_errors
    else:
        for (articlename, articledesc) in itertools.zip_longest(results, res):
            if articledesc.get_text().strip() is not None and len(articledesc.get_text().strip()) > 0:
                article_info[articledesc.get_text().strip()] = articlename.get_text().strip()
    
    for ele in article_info:
        if language_translation in ele:
            possible_errors.append(article_info[ele])
    
    return possible_errors


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
    
    if link.strip() == 'https://partner.hpe.com/group/prp' or link.strip() == "https://partner.hpe.com/group/prp/home":
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
        except:
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
        find_all_example = [find_all_example[i] for i in range(len(find_all_example)) if find_all_example[i]]
    
    # Use the enhanced version
    errors = translation_errors_prob(content, find_all_example, art_titles_tocheck, lang)
    
    parser = Parser()
    for i in range(len(errors)):
        for match in parser.parse(errors[i]):
            errors[i] = errors[i].replace(match.text, "")
    errors = [errors[i] for i in range(len(errors)) if errors[i]]
    
    return errors