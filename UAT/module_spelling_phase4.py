#THIS MODULE IDENTIFIES ONLY SPELLING ERRORS, NOT GRAMMATICAL ERRORS

# from spellchecker import SpellChecker
'''
import enchant

import itertools
from date_detector import Parser
#import VaultSample
from langdetect import DetectorFactory
DetectorFactory.seed = 0
import pandas as pd
import work_phase_3 as work
from inscriptis import get_text
import re

def postprocess(error):
    error = ''.join([i for i in error if not i.isdigit()])
    
    error = re.sub('\W+',' ',error)
    
    error=error.strip()
    if len(error)<=1:
        return ''
    #print(type(error))
    return error 

def grammatical_errors(extracted_text,tbi,articletitles,language): #    errors = grammatical_errors(content,find_all_example,art_titles_tocheck,lang)
    # print("EXTRACTED TEXT:,",extracted_text)
    codes= {'French':'fr','German':'de','Italian':"it",'Chinese':'zh-cn','Russian':'ru','Portugese':'pt','Indonesian':'id','Singaporean':'en','Korean':"ko",'Turkish':"tr",'Japanese':"ja",'Taiwan':"zh-tw",'Spanish':'es',"LARSpanish":'es','English':'en'}
    df = pd.read_excel('glossary.xlsx')
    tbc = 'en'
    col_name = 'en-US'
    check_list = list(df[col_name])
    ignored = "*+^#%$),(!@_}{[]?><~=\|-:;"
    extras = ['ARTIKEL','Tools catalog102030','© Copyright 2022 Hewlett Packard Enterprise Development, L.P.','Competenza','Cancella','decrescente','Presidente','ARTíCULO','Competencia Partner Ready','5000','6000']
    check_list = [check_list[i] for i in range(len(check_list)) if type(check_list[i])==str]
    tbi.extend(extras)
    tbi = [tbi[i] for i in range(len(tbi)) if tbi[i].strip()]
    gramm_checks = []

    for line in extracted_text:
        if line!='':
            gramm_checks.append(line)
        
    gramm_res = []
    gramm_checks_new=[]


    for i in range(len(gramm_checks)):
        if not gramm_checks[i][0]=="/" and not gramm_checks[i][0].isalnum():
            for m in ignored:
                gramm_checks[i]=gramm_checks[i].lstrip(m)
        flag = False
        for k in range(len(tbi)):
            if tbi[k].strip() == gramm_checks[i].strip():
                flag = True
        if flag == False:
            gramm_checks_new.append(gramm_checks[i])
    gramm_checks = gramm_checks_new
    gramm_checks.extend(articletitles)


    # print('GRAMM CHECKS LIST',gramm_checks)

    # try:
    #     for i in gramm_checks:
    #         #print (i)
    #         lst = i.split('.')
    #         for j in lst:
    #             if j and len(j)>2:
    #                 res = spell_gramm(j, check_list)
    #                 gramm_res.append(res)
    try:
        gramm_res = spell_gramm(gramm_checks, check_list)
        #print(gramm_res)
    except Exception as e:
        print('\nEXCEPTION-------------------------', e,'\n')

    # for i in range(len(gramm_checks)):
    #     gramm_checks[i]=gramm_checks[i].strip()

    #     if (gramm_checks[i]=="*"   or gramm_checks[i]=="" or gramm_checks[i].startswith("/") or gramm_checks[i].startswith("o ")):
    #         continue
    #     for k in ignored:
    #         if gramm_checks[i].startswith(k) and gramm_checks:
    #             gramm_checks[i]=gramm_checks[i].lstrip(k)
    #             gramm_checks[i]=gramm_checks[i].strip()

    #     else:
    #         for j in range(len(check_list)):
    #             if check_list[j] in gramm_checks[i]:
    #                 gramm_checks[i]=gramm_checks[i].replace(check_list[j],'')
    #     if (gramm_checks[i]):
    #         probable_errors.append(gramm_checks[i])
    # #probable_errors.extend(articletitles)
    # errors=[]
    # for i in probable_errors:
    #     gramm_res = spell_gramm(i)
    #     try:
    #         gramm_res = spell_gramm(i)
    #         if gramm_res:
    #             errors.append(gramm_res)

    #     except:
    #         print('\nERROR IN GRAMMAR CHECK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n')
    # print("PROBABLE ERRORS",probable_errors)
    # for i in probable_errors:
    #     try:
    #         #lang = model.predict(i)[0][0][9:]
    #         if lang=='en':
    #             i=i.strip()
    #             i = postprocess(i)
    #             if i!='':
                
                   
    #                 errors.append(i)
        
    #     except:
    #         #print("error in language prediction")
    #         continue

    #print("****************************************************************")
    # final_res = []
    # for i in gramm_res:
    #     fin_err = i.split('.')
    #     for ii in fin_err:
    #         if '{{' in ii:
    #             final_res.append(ii) 

    print("ERRORS BEFORE FINALLY RETURNING",gramm_res)
    
    return gramm_res

def callable_extract(link,html_page,soup,lang):
    content=''
    #trans_terms={'French':'Français','German':'Deutsch','Italian':"Italiano",'Chinese':'简体中文','Russian':'Русский','Portugese':'Português','Indonesian':'Bahasa indonesia','Korean':"한국어",'Turkish':"Türkçe",'Japanese':"日本語",'Taiwan':"中文（台灣)",'Spanish':'Español',"LARSpanish":'Español'}
    #trans_errors={}
    find_all_example=[]
    tbi = ["span","h1","h2","a",'div',"tr"]
    tb = ['portlet-title-text','hide','hide-accessible','hide User','sr-only','iconText','hide isPureHPE','dateFormat','size','categoryName','categoryDescription','boldContent','detailedContentText','articleSummary','articleDeails row','controlsPagination pull-right','articleDownloadHeader','articleformatSize',"border_bottom",'articleDownloadContent']
    errors = []
    art_titles_tocheck=[]
    #html_page = self.driver.page_source
    #soup=BeautifulSoup(html_page,'html.parser')
    #art_titles_tocheck=articlenamechecker(soup, 'English')
    art_titles_tocheck = articlenamechecker(soup, 'English')
    # print("doctitles",art_titles_tocheck)
    if link.strip()=='https://partner.hpe.com/group/prp' or link.strip()=="https://partner.hpe.com/group/prp/home":
        # print("inscriptis called")
        content = get_text(html_page)
        content=content.splitlines()
        for element in tbi:
            if element=='a':
                for word in soup.find_all(element):
                    find_all_example.append(word.get_text().strip())
            for ele in tb:
                for word in soup.find_all(element,class_= ele):
                        find_all_example.append(word.get_text())
        for i in range(len(content)):
            content[i]=content[i].strip()
            if content[i].startswith("+"):
                content[i]=content[i].lstrip("+")
                content[i]=content[i].strip()

    else:
        
        try:
            content=soup.find(id='main-content').get_text()
        except:

            pass
        content=content.splitlines()
        for i in range(len(content)):
            content[i]=" ".join(content[i].split())
        content=[content[i] for i in range(len(content)) if content[i]]

        for element in tbi:
            if element=='a':
                for word in soup.find_all(element):
                    temp=word.get_text()
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
            for ele in tb:
                for word in soup.find_all(element,class_= ele):
                    temp=word.get_text()
                    temp=temp.splitlines()
                    find_all_example.extend(temp)
        for word in soup.find_all("p",id="qsUserData"):
            temp=word.get_text()
            temp=temp.splitlines()
            find_all_example.extend(temp)
        for i in range(len(find_all_example)):
            find_all_example[i]=" ".join(find_all_example[i].split())
        find_all_example=[find_all_example[i] for i in range(len(find_all_example)) if find_all_example[i]]
    # content.extend(art_titles_tocheck)
    #print("LINK:",link)
    errors = grammatical_errors(content,find_all_example,art_titles_tocheck,lang)
    
    parser=Parser()
    for i in range(len(errors)):
        for match in parser.parse(errors[i]):
            errors[i] = errors[i].replace(match.text,"")
    errors=[errors[i] for i in range(len(errors)) if errors[i]]

        
    # print("FINAL",errors)  
    return errors
    
###################### Function to check for spelling errors #######################
def spell_gramm(content, check_list):
    # print('CONTENT---------',content)
    # print(matches)
    error_list = []
    spell = enchant.DictWithPWL("en_US", "CUSTOM_SPELLING_DICT.txt")       
    for i in content:
        sentence = i.split('.')

        for i in sentence:
            words = i.split()
            corrected_text = i
            for word in words:
                if not any(char.isupper() for char in word[1:]): #Treat all words which have uppercase letters after the first letter as abbreviations or product names
                    # print('WORD:---',word)
                    if word.isalpha() and not spell.check(word) and word not in check_list:
                        suggestions = spell.suggest(word)
                        corrected_word = suggestions[0] if suggestions else word
                        corrected_text = corrected_text.replace(word, '{{' + word + "--->" + corrected_word + '}}')
                        if corrected_text not in error_list and '{{' in corrected_text:
                            error_list.append(corrected_text)


    return error_list


def articlenamechecker(soupobject,language_translation):
    article_info={}
    possible_errors=[]
    try:
        results=soupobject.find_all('span',class_='articleDownloadHeader')
        res=soupobject.find_all('span',class_='articleformatSize')
    except:
        #print("Donno")
        return possible_errors
    else:
        for (articlename,articledesc) in itertools.zip_longest(results,res):
            if articledesc.get_text().strip() is not None and len(articledesc.get_text().strip())>0 :
                article_info[articledesc.get_text().strip()]=articlename.get_text().strip()
    for ele in article_info:
        if language_translation in ele:
            possible_errors.append(article_info[ele])
    # print(article_info)
    return possible_errors
'''


# SPELLING CHECK MODULE - SymSpellPy Based (NO JAVA REQUIRED!)
# Drop-in replacement for module_spelling_phase4.py
# Uses CUSTOM_SPELLING_DICT.txt as primary ignore source
# MUCH FASTER than LanguageTool, no Java dependency

from symspellpy import SymSpell, Verbosity
import pkg_resources
import re
from inscriptis import get_text
from bs4 import BeautifulSoup
import pandas as pd
import itertools
from date_detector import Parser

# Initialize SymSpell once (fast operation)
_symspell_instance = None

def get_symspell():
    """Get or create SymSpell instance (singleton pattern)"""
    global _symspell_instance
    if _symspell_instance is None:
        try:
            sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
            
            # Load default dictionary (comes with symspellpy)
            dictionary_path = pkg_resources.resource_filename(
                "symspellpy", "frequency_dictionary_en_82_765.txt"
            )
            sym_spell.load_dictionary(dictionary_path, term_index=0, count_index=1)
            
            print("✓ SymSpell initialized successfully (NO Java required!)")
            _symspell_instance = sym_spell
        except Exception as e:
            print(f"✗ Failed to initialize SymSpell: {e}")
            _symspell_instance = None
    return _symspell_instance

class SmartSpellingChecker:
    """
    Enhanced spelling checker using SymSpell (No Java dependency!)
    
    Primary ignore source: CUSTOM_SPELLING_DICT.txt (one word per line)
    Optional: glossary.xlsx (column 'en-US')
    
    MUCH FASTER than enchant or LanguageTool!
    """
    
    def __init__(self):
        self.sym_spell = get_symspell()
        
        # Load glossary terms from Excel
        self.glossary_terms = self._load_glossary()
        
        # Load custom dictionary from text file (PRIMARY SOURCE)
        self.custom_dict_terms = self._load_custom_dictionary()
        
        # Minimal critical code/template terms that must be ignored
        self.code_terms = {
            'href', 'src', 'iframe', 'onclick', 'onload', 'validator',
            'impl', 'frameborder', 'allowfullscreen', 'idlang',
            'prpartic', 'relatedarticle', 'dlfileentryid', 'languagefinish',
        }
        
        # Code/template patterns to skip entirely
        self.code_patterns = [
            r'<#[^>]+>',              # FreeMarker tags
            r'\$\{[^}]+\}',           # Variable expressions
            r'<%[^%]+%>',             # JSP tags
            r'<[a-z]+\s+[^>]*>',      # HTML tags
            r'</[a-z]+>',             # Closing HTML tags
            r'function\s*\([^)]*\)',  # JavaScript functions
            r'var\s+\w+\s*=',         # Variable declarations
            r'const\s+\w+\s*=',       # Const declarations
            r'import\s+',             # Import statements
            r'\d+<#',                 # Line numbers with code
            r'^\s*\d+\s*$',           # Just numbers
            r'[a-z]+\([^)]*\)',       # Function calls
            r'\w+\.\w+\(',            # Method calls
            r'^\s*[-=]{3,}\s*$',      # Separator lines
        ]
        
        # Load correction overrides
        self.correction_overrides = self._load_correction_overrides()

        print(f"✓ Loaded {len(self.correction_overrides)} correction overrides")
        print(f"ℹ Using CUSTOM_SPELLING_DICT.txt as primary ignore source")
        print(f"ℹ Total terms loaded: {len(self.custom_dict_terms)} custom + {len(self.glossary_terms)} glossary")
    
    def _load_glossary(self):
        """Load glossary terms from Excel file"""
        try:
            df = pd.read_excel('glossary.xlsx')
            col_name = 'en-US'
            if col_name in df.columns:
                terms = set()
                for term in df[col_name]:
                    if pd.notna(term):
                        terms.add(str(term).lower())
                print(f"✓ Loaded {len(terms)} terms from glossary")
                return terms
        except Exception as e:
            print(f"ℹ Could not load glossary: {e}")
        return set()
    
    def _load_custom_dictionary(self):
        """
        Load custom dictionary from CUSTOM_SPELLING_DICT.txt
        This is your PRIMARY source for ignore terms!
        Format: One word per line, case-insensitive
        """
        try:
            with open('CUSTOM_SPELLING_DICT.txt', 'r', encoding='utf-8') as f:
                terms = set()
                for line in f:
                    # Strip whitespace and ignore empty lines and comments
                    term = line.strip()
                    if term and not term.startswith('#'):
                        # Add lowercase version for case-insensitive matching
                        terms.add(term.lower())
                print(f"✓ Loaded {len(terms)} custom terms from CUSTOM_SPELLING_DICT.txt")
                return terms
        except FileNotFoundError:
            print("⚠ WARNING: CUSTOM_SPELLING_DICT.txt not found!")
            print("  Create this file to add your custom terms (one per line)")
        except Exception as e:
            print(f"✗ Error loading CUSTOM_SPELLING_DICT.txt: {e}")
        return set()
    
    def _load_correction_overrides(self):
        """Load word corrections that SymSpell gets wrong"""
        overrides = {}
        try:
            with open('CORRECTION_OVERRIDES.txt', 'r', encoding='utf-8') as f:
                for line in f:
                    if '->' in line and not line.startswith('#'):
                        wrong, correct = line.strip().split('->')
                        overrides[wrong.strip().lower()] = correct.strip()
        except FileNotFoundError:
            print("ℹ No CORRECTION_OVERRIDES.txt file found (optional)")
        return overrides
    
    def _is_code_or_template(self, text):
        """Check if text is code or template syntax"""
        if not text or len(text.strip()) < 3:
            return True
        
        # Check for code patterns
        for pattern in self.code_patterns:
            if re.search(pattern, text):
                return True
        
        # High density of special characters = code
        special_chars = sum(1 for c in text if c in '{}[]()<>=;:$#@%&|\\')
        if len(text) > 0 and special_chars / len(text) > 0.15:
            return True
        
        return False
    
    def _should_ignore_word(self, word):
        """Determine if a word should be ignored"""
        if not word or len(word) < 2:
            return True
        
        word_lower = word.lower()

        # ✅ FIX #1: Check custom dictionary FIRST (BEFORE everything else)
        if word_lower in self.custom_dict_terms:
            return True
        
        # ✅ FIX #2: File extensions SECOND (BEFORE plural logic)
        if word_lower in {'xlsx', 'docx', 'pptx', 'pdf', 'jpg', 'png', 'gif', 'csv', 'zip', 'xls'}:
            return True
        
        # Check glossary (optional)
        if word_lower in self.glossary_terms:
            return True
        
        # Check critical code terms
        if word_lower in self.code_terms:
            return True
        
        # All uppercase (acronym)?
        if len(word) > 1 and word.isupper():
            return True
        
        # ✅ IMPROVED: Plural acronyms (SEs, APIs, PDFs, etc.)
        # if len(word) >= 2 and word[-1].lower() == 's':
        #     # Check if removing 's' leaves uppercase letters
        #     without_s = word[:-1]
        #     if len(without_s) > 0 and without_s.isupper():
        #         return True
        
        # 6️⃣ PLURAL ACRONYMS (SEs, APIs, PDFs) - FIXED
        if (len(word) >= 2 and 
            word[-1].lower() == 's' and 
            word[:-1].isupper()):
            return True
        
        # Multiple uppercase letters (product name like "GreenLake")?
        uppercase_count = sum(1 for c in word[1:] if c.isupper())
        if uppercase_count >= 2:
            return True
        
        # Contains numbers?
        if any(c.isdigit() for c in word):
            return True
        
        # Contains special characters (except hyphen)?
        if any(c in word for c in '@#$%^&*()+={}[]|\\:;"<>?/'):
            return True
        
        # Too short?
        if len(word) < 3:
            return True
        
        return False
    
    def _clean_word(self, word):
        """Clean word by removing surrounding punctuation"""
        return re.sub(r'^[^\w-]+|[^\w-]+$', '', word)
    
    def check_text(self, text):
        """
        Check text for spelling errors using SymSpell
        
        Args:
            text: String to check
            
        Returns:
            String with errors marked as {{word--->suggestion}} or empty string
        """
        if not self.sym_spell or not text:
            return ""
        
        # FIXED LINE 298: Use OR condition to catch nested errors
        if '{{' in text or '--->' in text:
            return ""
        
        # Skip if looks like code/template
        if self._is_code_or_template(text):
            return ""
        
        # Skip very short text
        if len(text.strip()) < 10:
            return ""
        
        try:
            # Split camelCase/PascalCase before extraction
            text_normalized = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
            
            # ✅ FIX: Extract words INCLUDING apostrophes for proper handling
            # This captures "Starshot's" as a single word
            words = re.findall(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", text_normalized)
            
            errors = []
            word_positions = {}
            
            for word in words:
                # Clean word
                clean_word = self._clean_word(word)
                if not clean_word:
                    continue
                
                # ✅ FIX: Skip ALL words with apostrophes (possessives and contractions)
                if "'" in word:
                    continue
                
                # Skip if should be ignored
                if self._should_ignore_word(clean_word):
                    continue

                # CHECK 1: Check overrides FIRST
                if clean_word.lower() in self.correction_overrides:
                    if clean_word not in word_positions:
                        errors.append({
                            'word': clean_word,
                            'suggestion': self.correction_overrides[clean_word.lower()]
                        })
                        word_positions[clean_word] = True
                    continue
                
                # CHECK 2: Check if word is already correct (edit_distance=0)
                exact_match = self.sym_spell.lookup(
                    clean_word.lower(),
                    Verbosity.TOP,
                    max_edit_distance=0
                )
                
                if exact_match and len(exact_match) > 0:
                    # Word exists in dictionary - skip it
                    continue

                # CHECK 3: Check plural form if word ends in 's'
                if clean_word.lower().endswith('s') and len(clean_word) > 3:
                    singular = clean_word[:-1]
                    singular_match = self.sym_spell.lookup(
                        singular.lower(),
                        Verbosity.TOP,
                        max_edit_distance=0
                    )
                    if singular_match and len(singular_match) > 0:
                        # Plural of valid word - skip it
                        continue
                
                # CHECK 4: Get spelling suggestions
                suggestions = self.sym_spell.lookup(
                    clean_word,
                    Verbosity.CLOSEST,
                    max_edit_distance=2,
                    include_unknown=False
                )
                
                if suggestions:
                    suggested_word = suggestions[0].term
                    
                    # Only flag if suggestion is different and has reasonable confidence
                    if (suggested_word.lower() != clean_word.lower() and
                        suggestions[0].distance > 0 and
                        suggestions[0].count > 50):
                        
                        if clean_word not in word_positions:
                            errors.append({
                                'word': clean_word,
                                'suggestion': suggested_word
                            })
                            word_positions[clean_word] = True
            
            if not errors:
                return ""
            
            # Build result string with {{word--->suggestion}} format
            result_text = text
            for error in errors:
                word = error['word']
                suggestion = error['suggestion']
                
                # Use word boundary to avoid partial replacements
                pattern = r'\b' + re.escape(word) + r'\b'
                result_text = re.sub(
                    pattern,
                    f"{{{{{word}--->{suggestion}}}}}",
                    result_text,
                    count=1,
                    flags=re.IGNORECASE
                )
            
            return result_text if '{{' in result_text else ""
            
        except Exception as e:
            print(f"✗ Error checking text: {e}")
            return ""

# Global checker instance
_checker_instance = None

def get_checker():
    """Get or create checker instance"""
    global _checker_instance
    if _checker_instance is None:
        _checker_instance = SmartSpellingChecker()
    return _checker_instance

def callable_extract(link, html_page, soup, lang):
    """
    Main function to extract and check spelling on a page.
    EXACT SAME SIGNATURE as original module_spelling_phase4.py
    
    Args:
        link: URL of the page
        html_page: Raw HTML content
        soup: BeautifulSoup object
        lang: Language code (e.g., 'English', 'Singaporean')
    
    Returns:
        List of error strings in {{word--->suggestion}} format
    """
    # Get checker instance
    checker = get_checker()
    
    if not checker.sym_spell:
        print("✗ SymSpell not available, skipping spell check")
        return []
    
    content = []
    find_all_example = []
    
    # Elements to extract text from
    tbi = ["span", "h1", "h2", "a", 'div', "tr"]
    
    # Classes to exclude
    tb = [
        'portlet-title-text', 'hide', 'hide-accessible', 'hide User',
        'sr-only', 'iconText', 'hide isPureHPE', 'dateFormat', 'size',
        'categoryName', 'categoryDescription', 'boldContent',
        'detailedContentText', 'articleSummary', 'articleDeails row',
        'controlsPagination pull-right', 'articleDownloadHeader',
        'articleformatSize', 'articleDownloadContent', 'border_bottom'
    ]
    
    # Special handling for homepage
    if link.strip() in ['https://partner.hpe.com/group/prp',
                        'https://partner.hpe.com/group/prp/home']:
        try:
            # ✅ FIX #2 (PRIMARY): Use inscriptis with proper text extraction
            content = get_text(html_page, display_links='none').splitlines()
            
            # Extract elements to ignore
            for element in tbi:
                if element == 'a':
                    for word in soup.find_all(element):
                        # ✅ Add separator=' ' to prevent word concatenation
                        find_all_example.append(word.get_text(separator=' ', strip=True))
                for ele in tb:
                    for word in soup.find_all(element, class_=ele):
                        # ✅ Add separator=' ' to prevent word concatenation
                        find_all_example.append(word.get_text(separator=' ', strip=True))
            
            # Clean content
            content = [c.strip().lstrip('+').strip() for c in content if c.strip()]
        except Exception as e:
            print(f"✗ Error processing homepage: {e}")
            return []
    
    else:
        # Extract main content
        try:
            main_content = soup.find(id='main-content')
            if main_content:
                # ✅ FIX #2 (PRIMARY): Add separator=' ' to prevent word concatenation
                content = main_content.get_text(separator=' ', strip=True).splitlines()
        except:
            pass
        
        # Clean and normalize content
        content = [" ".join(c.split()) for c in content if c]
        
        # Extract elements to ignore
        for element in tbi:
            if element == 'a':
                for word in soup.find_all(element):
                    # ✅ Add separator=' ' to prevent word concatenation
                    temp = word.get_text(separator=' ', strip=True).splitlines()
                    find_all_example.extend(temp)
            
            for ele in tb:
                for word in soup.find_all(element, class_=ele):
                    # ✅ Add separator=' ' to prevent word concatenation
                    temp = word.get_text(separator=' ', strip=True).splitlines()
                    find_all_example.extend(temp)
        
        # Extract user data elements
        for word in soup.find_all("p", id="qsUserData"):
            # ✅ Add separator=' ' to prevent word concatenation
            temp = word.get_text(separator=' ', strip=True).splitlines()
            find_all_example.extend(temp)
        
        # Clean ignore list
        find_all_example = [" ".join(f.split()) for f in find_all_example if f]
    
    # Get article titles
    art_titles = articlenamechecker(soup, 'English')
    
    # Combine ignore lists
    ignore_list = set(find_all_example + art_titles)
    
    # Filter content
    filtered_content = []
    for text in content:
        text_clean = text.strip()
        if text_clean in ignore_list:
            continue
        if len(text_clean) < 10:
            continue
        filtered_content.append(text_clean)
    
    # Check each piece of content
    errors = []
    for text in filtered_content:
        error_text = checker.check_text(text)
        if error_text:
            errors.append(error_text)
    
    # Remove date strings from errors
    parser = Parser()
    cleaned_errors = []
    
    for error in errors:
        cleaned = error
        try:
            for match in parser.parse(error):
                cleaned = cleaned.replace(match.text, "")
        except:
            pass
        
        if cleaned.strip() and '{{' in cleaned:
            cleaned_errors.append(cleaned.strip())
    
    # Remove duplicates
    seen = set()
    unique_errors = []
    for error in cleaned_errors:
        if error not in seen:
            seen.add(error)
            unique_errors.append(error)
    
    return unique_errors

def articlenamechecker(soupobject, language_translation):
    """
    Check article names for language-specific documents
    EXACT SAME SIGNATURE as original
    """
    article_info = {}
    possible_errors = []
    
    try:
        results = soupobject.find_all('span', class_='articleDownloadHeader')
        res = soupobject.find_all('span', class_='articleformatSize')
    except:
        return possible_errors
    
    for (articlename, articledesc) in itertools.zip_longest(results, res):
        if articledesc and articledesc.get_text().strip():
            desc_text = articledesc.get_text().strip()
            name_text = articlename.get_text().strip() if articlename else ""
            if desc_text and name_text:
                article_info[desc_text] = name_text
    
    for desc, name in article_info.items():
        if language_translation in desc:
            possible_errors.append(name)
    
    return possible_errors

# Cleanup function (optional)
def cleanup():
    """Clean up resources"""
    global _symspell_instance, _checker_instance
    _symspell_instance = None
    _checker_instance = None
    print("✓ SymSpell resources cleaned up")
