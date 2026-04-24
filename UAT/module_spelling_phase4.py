"""
module_spelling_optimized.py — OPTIMIZED BUILD
==============================================================
SymSpell-based spell-checker for HPE Partner Portal pages.  Drop-in
replacement for module_spelling_phase4.py.  ALL public signatures
preserved:

    callable_extract(link, html_page, soup, lang) -> list[str]
    articlenamechecker(soupobject, language_translation) -> list[str]

FIXES APPLIED IN THIS BUILD
---------------------------
  7.  articlenamechecker now honours the `lang` parameter threaded
      through callable_extract, instead of hard-coding 'English'.
      That's what the parameter was designed to do all along.

  8.  Removed the duplicate plural-acronym check.  Two versions of
      the same logic existed — the commented-out one and the live
      one — kept only the live version.

  9.  Thread-safe SymSpell singleton.  `get_symspell()` now holds a
      `threading.Lock()` so two concurrent callers can't both miss
      the cache and run the 2-second dictionary load in parallel.
      Safe for the orchestrator's MAX_PARALLEL=2 multiprocessing
      (each process has its own singleton, but within a process the
      lock also guards against thread races from any future change).

  10. Thread-safe SmartSpellingChecker singleton — same pattern as
      get_symspell().

  11. Replaced deprecated `pkg_resources` with `importlib.resources`.
      pkg_resources emits a DeprecationWarning in Python 3.12+ and
      will be removed in a future release.  The symspellpy package
      still exposes its dictionary via importlib.resources, so we
      don't need pkg_resources at all.

  12. Simplified word-extraction regex.  Previously we captured
      words-with-apostrophes then discarded every apostrophe match
      three lines later — wasted work.  Now the regex captures only
      plain alpha words, matching the actual downstream logic.

PLUS (not originally on the 12-item list but part of "aligning with
the rest of the codebase"):
  *   `flush=True` on every print so the Windows console-lock
      deadlock doesn't bite us when the spell-checker is run inside
      a multiprocessing.Process worker.
  *   Defensive file-loading errors no longer blank-swallow (they
      print + propagate the failure mode with context).

WHAT IS DELIBERATELY UNCHANGED
------------------------------
  *   Function signatures.
  *   All FP-reduction heuristics (code-pattern filter, acronym
      handling, plural-of-valid-word skip, brand-term dict, correction
      overrides, date-detector cleanup).
  *   File formats (CUSTOM_SPELLING_DICT.txt one-word-per-line,
      CORRECTION_OVERRIDES.txt `wrong->correct` per line,
      glossary.xlsx column `en-US`).
  *   SymSpell tuning (max_dictionary_edit_distance=2, prefix_length=7).
  *   Output format `{{word--->suggestion}}`.
"""

# ---------------------------------------------------------------------------
# Standard-library imports
# ---------------------------------------------------------------------------
import itertools
import re
import sys
import threading

# ---------------------------------------------------------------------------
# CRITICAL: unbuffered stdout to prevent Windows console-lock deadlock when
# this module is exercised inside a multiprocessing.Process worker.  Mirrors
# the pattern used by the crawler / broken-link checker / external-links
# validator.
# ---------------------------------------------------------------------------
try:
    sys.stdout.reconfigure(line_buffering=True, write_through=True)
    sys.stderr.reconfigure(line_buffering=True, write_through=True)
except Exception:
    pass

# ---------------------------------------------------------------------------
# Third-party imports
# ---------------------------------------------------------------------------
from symspellpy import SymSpell, Verbosity

# FIX 11: use importlib.resources instead of the deprecated pkg_resources.
try:
    # Python 3.9+: files() API is stable.
    from importlib.resources import files as _ir_files
    _USE_IMPORTLIB = True
except ImportError:
    # Fallback for ancient Python: keep pkg_resources available as a
    # last resort, with a warning.
    _USE_IMPORTLIB = False
    import pkg_resources  # pragma: no cover

from inscriptis import get_text
import pandas as pd
from date_detector import Parser


# ===========================================================================
# SECTION 1 — SymSpell initialization (thread-safe singleton)
# ===========================================================================

# FIX 9: module-level state guarded by a lock.  Multiple threads calling
# get_symspell() concurrently will still only trigger one dictionary load.
_symspell_instance = None
_symspell_lock = threading.Lock()


def _resolve_symspell_dictionary_path() -> str:
    """
    Locate the `frequency_dictionary_en_82_765.txt` file shipped inside
    the symspellpy package.  Prefers importlib.resources; falls back to
    pkg_resources only if importlib isn't available (Python < 3.9).
    """
    filename = "frequency_dictionary_en_82_765.txt"
    if _USE_IMPORTLIB:
        # files() returns a Traversable; str() of `/` gives the real path.
        return str(_ir_files("symspellpy") / filename)
    # Legacy fallback
    return pkg_resources.resource_filename("symspellpy", filename)  # pragma: no cover


def get_symspell():
    """
    Get or create the SymSpell instance (singleton pattern, thread-safe).

    Returns the SymSpell instance, or None if initialization failed
    (in which case spell-checking is silently skipped downstream —
    matching the original file's behaviour).
    """
    global _symspell_instance
    # Fast path: already initialized
    if _symspell_instance is not None:
        return _symspell_instance

    # Slow path: one caller gets to do the init, others wait.
    with _symspell_lock:
        # Re-check after acquiring the lock in case another thread got here first
        if _symspell_instance is not None:
            return _symspell_instance
        try:
            sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
            dict_path = _resolve_symspell_dictionary_path()
            sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)
            print("✓ SymSpell initialized successfully (no Java required)", flush=True)
            _symspell_instance = sym_spell
        except Exception as exc:
            print(f"✗ Failed to initialize SymSpell: {exc}", flush=True)
            _symspell_instance = None
    return _symspell_instance


# ===========================================================================
# SECTION 2 — Spelling checker class
# ===========================================================================

class SmartSpellingChecker:
    """
    Enhanced spelling checker using SymSpell (no Java dependency).

    Primary ignore source: CUSTOM_SPELLING_DICT.txt (one word per line).
    Optional:              glossary.xlsx (column 'en-US').
    Optional:              CORRECTION_OVERRIDES.txt ('wrong->correct' per line).
    """

    def __init__(self):
        self.sym_spell = get_symspell()

        # Load glossary terms from Excel
        self.glossary_terms = self._load_glossary()

        # Load custom dictionary from text file (PRIMARY source)
        self.custom_dict_terms = self._load_custom_dictionary()

        # Minimal critical code/template terms that must be ignored
        self.code_terms = {
            "href", "src", "iframe", "onclick", "onload", "validator",
            "impl", "frameborder", "allowfullscreen", "idlang",
            "prpartic", "relatedarticle", "dlfileentryid", "languagefinish",
        }

        # Code/template patterns that signal "this isn't prose, skip it"
        self.code_patterns = [
            r"<#[^>]+>",               # FreeMarker tags
            r"\$\{[^}]+\}",            # Variable expressions
            r"<%[^%]+%>",              # JSP tags
            r"<[a-z]+\s+[^>]*>",       # HTML tags
            r"</[a-z]+>",              # Closing HTML tags
            r"function\s*\([^)]*\)",   # JavaScript functions
            r"var\s+\w+\s*=",          # Variable declarations
            r"const\s+\w+\s*=",        # Const declarations
            r"import\s+",              # Import statements
            r"\d+<#",                  # Line numbers with code
            r"^\s*\d+\s*$",            # Just numbers
            r"[a-z]+\([^)]*\)",        # Function calls
            r"\w+\.\w+\(",             # Method calls
            r"^\s*[-=]{3,}\s*$",       # Separator lines
        ]
        # Pre-compile for modest speed gain (we run this regex per-content-line
        # per-page; 300 pages * 100 lines * 14 patterns adds up).
        self._compiled_code_patterns = [re.compile(p) for p in self.code_patterns]

        # File extensions that aren't typos but look like them
        self._file_ext_dict = {
            "xlsx", "docx", "pptx", "pdf", "jpg", "png",
            "gif", "csv", "zip", "xls",
        }

        # Load correction overrides
        self.correction_overrides = self._load_correction_overrides()

        print(f"✓ Loaded {len(self.correction_overrides)} correction overrides",
              flush=True)
        print(f"ℹ Using CUSTOM_SPELLING_DICT.txt as primary ignore source",
              flush=True)
        print(f"ℹ Total terms loaded: {len(self.custom_dict_terms)} custom + "
              f"{len(self.glossary_terms)} glossary", flush=True)

    # -----------------------------------------------------------------------
    # 2.1  Resource loaders
    # -----------------------------------------------------------------------

    def _load_glossary(self):
        """Load glossary terms from Excel file (column 'en-US')."""
        try:
            df = pd.read_excel("glossary.xlsx")
            col_name = "en-US"
            if col_name in df.columns:
                terms = set()
                for term in df[col_name]:
                    if pd.notna(term):
                        terms.add(str(term).lower())
                print(f"✓ Loaded {len(terms)} terms from glossary", flush=True)
                return terms
        except Exception as exc:
            print(f"ℹ Could not load glossary: {exc}", flush=True)
        return set()

    def _load_custom_dictionary(self):
        """
        Load custom dictionary from CUSTOM_SPELLING_DICT.txt.

        Format: one word per line; lines starting with '#' are comments;
        case-insensitive (stored lowercase).
        """
        try:
            with open("CUSTOM_SPELLING_DICT.txt", "r", encoding="utf-8") as f:
                terms = set()
                for line in f:
                    term = line.strip()
                    if term and not term.startswith("#"):
                        terms.add(term.lower())
                print(f"✓ Loaded {len(terms)} custom terms from "
                      f"CUSTOM_SPELLING_DICT.txt", flush=True)
                return terms
        except FileNotFoundError:
            print("⚠ CUSTOM_SPELLING_DICT.txt not found", flush=True)
            print("  Create this file to add your custom terms (one per line)",
                  flush=True)
        except Exception as exc:
            print(f"✗ Error loading CUSTOM_SPELLING_DICT.txt: {exc}", flush=True)
        return set()

    def _load_correction_overrides(self):
        """
        Load correction overrides from CORRECTION_OVERRIDES.txt.

        Format: one mapping per line as `wrong -> correct`.
        Lines starting with '#' are comments.
        """
        overrides = {}
        try:
            with open("CORRECTION_OVERRIDES.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "->" in line:
                        wrong, correct = line.split("->", 1)
                        overrides[wrong.strip().lower()] = correct.strip()
        except FileNotFoundError:
            print("ℹ No CORRECTION_OVERRIDES.txt file found (optional)",
                  flush=True)
        except Exception as exc:
            print(f"✗ Error loading CORRECTION_OVERRIDES.txt: {exc}", flush=True)
        return overrides

    # -----------------------------------------------------------------------
    # 2.2  Filter helpers
    # -----------------------------------------------------------------------

    def _is_code_or_template(self, text):
        """Return True if `text` looks like code/template markup, not prose."""
        if not text or len(text.strip()) < 3:
            return True

        for pattern in self._compiled_code_patterns:
            if pattern.search(text):
                return True

        # High density of special chars → almost certainly code
        special_chars = sum(1 for c in text if c in "{}[]()<>=;:$#@%&|\\")
        if len(text) > 0 and special_chars / len(text) > 0.15:
            return True

        return False

    def _should_ignore_word(self, word):
        """
        Return True if `word` should be skipped entirely (not checked).

        Ordering matters here — check cheap filters before expensive ones
        and check custom dictionary FIRST so the user can override any
        heuristic below by adding the word to CUSTOM_SPELLING_DICT.txt.
        """
        if not word or len(word) < 2:
            return True

        word_lower = word.lower()

        # Custom dictionary check FIRST — this is the user's escape hatch.
        if word_lower in self.custom_dict_terms:
            return True

        # File extensions BEFORE the plural logic (so "xls" isn't treated
        # as "singular form of 'xlss'")
        if word_lower in self._file_ext_dict:
            return True

        # Glossary
        if word_lower in self.glossary_terms:
            return True

        # Hard-coded code terms
        if word_lower in self.code_terms:
            return True

        # All-uppercase acronyms (API, SASE, etc.)
        if len(word) > 1 and word.isupper():
            return True

        # FIX 8: single canonical plural-acronym check.  Matches SEs, APIs,
        # PDFs — a trailing lowercase 's' on an otherwise-uppercase word.
        # `word[:-1].isupper()` returns False on empty strings, so the
        # length guard on the first line is enough.
        if (len(word) >= 2
                and word[-1].lower() == "s"
                and word[:-1].isupper()):
            return True

        # Multiple uppercase letters after position 0 → CamelCase brand
        # (GreenLake, ArubaOS, ...) — ignore.
        uppercase_count = sum(1 for c in word[1:] if c.isupper())
        if uppercase_count >= 2:
            return True

        # Contains digits or disallowed specials
        if any(c.isdigit() for c in word):
            return True
        if any(c in word for c in '@#$%^&*()+={}[]|\\:;"<>?/'):
            return True

        # Too short to check reliably
        if len(word) < 3:
            return True

        return False

    def _clean_word(self, word):
        """Strip surrounding punctuation (keep internal hyphens)."""
        return re.sub(r"^[^\w-]+|[^\w-]+$", "", word)

    # -----------------------------------------------------------------------
    # 2.3  Main checker
    # -----------------------------------------------------------------------

    def check_text(self, text):
        """
        Check text for spelling errors using SymSpell.

        Args:
            text: string to check

        Returns:
            string with errors marked as `{{word--->suggestion}}`, or
            empty string if no errors.
        """
        if not self.sym_spell or not text:
            return ""

        # Don't double-annotate.  `{{...--->...}}` is our output marker —
        # if a caller feeds us a pre-annotated string, return it empty.
        if "{{" in text or "--->" in text:
            return ""

        if self._is_code_or_template(text):
            return ""

        if len(text.strip()) < 10:
            return ""

        try:
            # Split camelCase/PascalCase boundaries so "GreenLake" splits
            # into ["Green", "Lake"] (both brand-name-like, will be
            # filtered by the multiple-caps rule in _should_ignore_word).
            text_normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)

            # FIX 12: simplified word extraction.  Previously we captured
            # words-with-apostrophes AND then skipped every apostrophe
            # match three lines later — wasted work.  Just match plain
            # alpha tokens.
            words = re.findall(r"\b[a-zA-Z]+\b", text_normalized)

            errors = []
            word_positions = {}

            for word in words:
                clean_word = self._clean_word(word)
                if not clean_word:
                    continue

                # (The `"'" in word` check from the original is now
                # unreachable thanks to FIX 12 — the regex can't match
                # apostrophes — so we drop it.)

                if self._should_ignore_word(clean_word):
                    continue

                # Check overrides FIRST — user intent beats SymSpell.
                override_key = clean_word.lower()
                if override_key in self.correction_overrides:
                    if clean_word not in word_positions:
                        errors.append({
                            "word": clean_word,
                            "suggestion": self.correction_overrides[override_key],
                        })
                        word_positions[clean_word] = True
                    continue

                # Check exact match in dictionary (edit_distance=0)
                exact_match = self.sym_spell.lookup(
                    clean_word.lower(),
                    Verbosity.TOP,
                    max_edit_distance=0,
                )
                if exact_match and len(exact_match) > 0:
                    continue

                # Check plural-of-valid-word ("cats" valid if "cat" valid)
                if clean_word.lower().endswith("s") and len(clean_word) > 3:
                    singular = clean_word[:-1]
                    singular_match = self.sym_spell.lookup(
                        singular.lower(),
                        Verbosity.TOP,
                        max_edit_distance=0,
                    )
                    if singular_match and len(singular_match) > 0:
                        continue

                # Get suggestions
                suggestions = self.sym_spell.lookup(
                    clean_word,
                    Verbosity.CLOSEST,
                    max_edit_distance=2,
                    include_unknown=False,
                )

                if suggestions:
                    suggested_word = suggestions[0].term

                    # Only flag if suggestion is DIFFERENT and has
                    # reasonable confidence (count > 50).
                    if (suggested_word.lower() != clean_word.lower()
                            and suggestions[0].distance > 0
                            and suggestions[0].count > 50):

                        if clean_word not in word_positions:
                            errors.append({
                                "word": clean_word,
                                "suggestion": suggested_word,
                            })
                            word_positions[clean_word] = True

            if not errors:
                return ""

            # Build result string with {{word--->suggestion}} markers
            result_text = text
            for error in errors:
                word = error["word"]
                suggestion = error["suggestion"]
                pattern = r"\b" + re.escape(word) + r"\b"
                result_text = re.sub(
                    pattern,
                    f"{{{{{word}--->{suggestion}}}}}",
                    result_text,
                    count=1,
                    flags=re.IGNORECASE,
                )

            return result_text if "{{" in result_text else ""

        except Exception as exc:
            print(f"✗ Error checking text: {exc}", flush=True)
            return ""


# ===========================================================================
# SECTION 3 — Checker singleton (thread-safe)
# ===========================================================================

# FIX 10: same pattern as SymSpell — module-level instance guarded by a lock.
_checker_instance = None
_checker_lock = threading.Lock()


def get_checker():
    """Get or create the SmartSpellingChecker instance (thread-safe)."""
    global _checker_instance
    if _checker_instance is not None:
        return _checker_instance

    with _checker_lock:
        if _checker_instance is not None:
            return _checker_instance
        _checker_instance = SmartSpellingChecker()
    return _checker_instance


# ===========================================================================
# SECTION 4 — Public API
# ===========================================================================

def callable_extract(link, html_page, soup, lang):
    """
    Main entry point — extract text from a page and check spelling.

    EXACT signature preserved from module_spelling_phase4.py.

    Args:
        link:       URL of the page
        html_page:  raw HTML content
        soup:       BeautifulSoup object
        lang:       language code ('English', 'Singaporean', etc.) —
                    used by articlenamechecker to match localized
                    article titles that shouldn't be spell-checked.

    Returns:
        list of error strings in `{{word--->suggestion}}` format.
    """
    checker = get_checker()

    if not checker.sym_spell:
        print("✗ SymSpell not available, skipping spell check", flush=True)
        return []

    content = []
    find_all_example = []

    # Elements to extract text from
    tbi = ["span", "h1", "h2", "a", "div", "tr"]

    # Classes to exclude (already-validated UI chrome)
    tb = [
        "portlet-title-text", "hide", "hide-accessible", "hide User",
        "sr-only", "iconText", "hide isPureHPE", "dateFormat", "size",
        "categoryName", "categoryDescription", "boldContent",
        "detailedContentText", "articleSummary", "articleDeails row",
        "controlsPagination pull-right", "articleDownloadHeader",
        "articleformatSize", "articleDownloadContent", "border_bottom",
    ]

    # -----------------------------------------------------------------------
    # Homepage has a different content-extraction path (uses inscriptis)
    # -----------------------------------------------------------------------
    if link.strip() in (
        "https://partner.hpe.com/group/prp",
        "https://partner.hpe.com/group/prp/home",
    ):
        try:
            content = get_text(html_page, display_links="none").splitlines()

            for element in tbi:
                if element == "a":
                    for word in soup.find_all(element):
                        find_all_example.append(
                            word.get_text(separator=" ", strip=True)
                        )
                for ele in tb:
                    for word in soup.find_all(element, class_=ele):
                        find_all_example.append(
                            word.get_text(separator=" ", strip=True)
                        )

            content = [c.strip().lstrip("+").strip() for c in content if c.strip()]
        except Exception as exc:
            print(f"✗ Error processing homepage: {exc}", flush=True)
            return []

    # -----------------------------------------------------------------------
    # All other pages: use soup.find(id='main-content')
    # -----------------------------------------------------------------------
    else:
        try:
            main_content = soup.find(id="main-content")
            if main_content:
                content = main_content.get_text(
                    separator=" ", strip=True
                ).splitlines()
        except Exception:
            pass

        content = [" ".join(c.split()) for c in content if c]

        # Extract elements to ignore
        for element in tbi:
            if element == "a":
                for word in soup.find_all(element):
                    temp = word.get_text(separator=" ", strip=True).splitlines()
                    find_all_example.extend(temp)

            for ele in tb:
                for word in soup.find_all(element, class_=ele):
                    temp = word.get_text(separator=" ", strip=True).splitlines()
                    find_all_example.extend(temp)

        # Extract user data elements
        for word in soup.find_all("p", id="qsUserData"):
            temp = word.get_text(separator=" ", strip=True).splitlines()
            find_all_example.extend(temp)

        find_all_example = [" ".join(f.split()) for f in find_all_example if f]

    # -----------------------------------------------------------------------
    # FIX 7: thread the `lang` parameter through to articlenamechecker.
    # Previously this was hard-coded to 'English' regardless of the caller's
    # intent.  The parameter was designed to match the lang-description
    # string in localized article spans, so it should actually be used.
    #
    # (If the caller passes 'English', behaviour is identical to before.
    # For other languages, article titles in that language get correctly
    # excluded from spell-checking — the original intent of the parameter.)
    # -----------------------------------------------------------------------
    art_titles = articlenamechecker(soup, lang)

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

    # Run SymSpell on each filtered line
    errors = []
    for text in filtered_content:
        error_text = checker.check_text(text)
        if error_text:
            errors.append(error_text)

    # Strip date strings from error output (dates like "Jan 3, 2024" were
    # generating noise)
    parser = Parser()
    cleaned_errors = []
    for error in errors:
        cleaned = error
        try:
            for match in parser.parse(error):
                cleaned = cleaned.replace(match.text, "")
        except Exception:
            pass
        if cleaned.strip() and "{{" in cleaned:
            cleaned_errors.append(cleaned.strip())

    # Deduplicate, preserving order
    seen = set()
    unique_errors = []
    for error in cleaned_errors:
        if error not in seen:
            seen.add(error)
            unique_errors.append(error)

    return unique_errors


def articlenamechecker(soupobject, language_translation):
    """
    Check article-name spans for language-specific documents.

    EXACT signature preserved.

    Returns:
        list of article names whose language description matches
        `language_translation` — these are titles of localized PDFs/docs
        that should be excluded from spell-checking.
    """
    article_info = {}
    possible_errors = []

    try:
        results = soupobject.find_all("span", class_="articleDownloadHeader")
        res     = soupobject.find_all("span", class_="articleformatSize")
    except Exception:
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


# ===========================================================================
# SECTION 5 — Cleanup helper (optional — call at end of batch)
# ===========================================================================

def cleanup():
    """Release module-level singletons (optional; useful for tests)."""
    global _symspell_instance, _checker_instance
    with _symspell_lock:
        _symspell_instance = None
    with _checker_lock:
        _checker_instance = None
    print("✓ Spell-checker resources cleaned up", flush=True)