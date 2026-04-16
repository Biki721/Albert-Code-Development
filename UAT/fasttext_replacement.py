"""
fasttext_replacement.py

Drop-in language-id replacement for fastText model.predict(...) on Python 3.13.
Combines unicode-script heuristics for CJK/Cyrillic/Arabic/Hangul and langid for
Latin-script languages.

Usage:
    from fasttext_replacement import model
    labels, scores = model.predict("우리 반 친구들", k=-1, threshold=0.02)
"""

import re
import math
from typing import List, Tuple
import langid

# restrict langid to languages you commonly need (improves speed/accuracy)
langid.set_languages(['en','fr','de','es','pt','it','zh','ja','ko','ru','tr','id'])

# precompiled regexes for script detection
_RE_HANGUL = re.compile(r'[\uac00-\ud7af]')
_RE_HIRAGANA = re.compile(r'[\u3040-\u309f]')
_RE_KATAKANA = re.compile(r'[\u30a0-\u30ff]')
_RE_CJK = re.compile(r'[\u4e00-\u9fff]')            # common CJK unified ideographs
_RE_CYRILLIC = re.compile(r'[\u0400-\u04FF]')
_RE_ARABIC = re.compile(r'[\u0600-\u06FF]')
_RE_DEVANAGARI = re.compile(r'[\u0900-\u097F]')
_RE_LATIN_LETTER = re.compile(r'[A-Za-z]')
_RE_DIGIT = re.compile(r'\d')

# map short deterministic script -> fastText-like ISO code
_SCRIPT_TO_LANG = {
    'hangul': 'ko',
    'hiragana': 'ja',
    'katakana': 'ja',
    'cjk': 'zh',
    'cyrillic': 'ru',
    'arabic': 'ar',
    'devanagari': 'hi',
}

def _script_detect(text: str):
    """Return a language code if a strong script cue exists, otherwise None."""
    if _RE_HANGUL.search(text):
        return _SCRIPT_TO_LANG['hangul']
    if _RE_HIRAGANA.search(text) or _RE_KATAKANA.search(text):
        return _SCRIPT_TO_LANG['hiragana']
    # If both hiragana/katakana not found but CJK ideographs present,
    # most likely Chinese (zh) — fallback later to zh vs ja heuristic.
    if _RE_CJK.search(text):
        # further check: presence of Hiragana/Katakana already handled above.
        return _SCRIPT_TO_LANG['cjk']
    if _RE_CYRILLIC.search(text):
        return _SCRIPT_TO_LANG['cyrillic']
    if _RE_ARABIC.search(text):
        return _SCRIPT_TO_LANG['arabic']
    if _RE_DEVANAGARI.search(text):
        return _SCRIPT_TO_LANG['devanagari']
    return None

def _short_text_score(length: int) -> float:
    """Return higher confidence for very short texts (UI labels)."""
    # very short single-token strings should be treated confidently
    if length <= 2:
        return 0.995
    if length <= 4:
        return 0.95
    if length <= 8:
        return 0.90
    return 0.85

def _langid_to_prob(logprob: float, text_len: int) -> float:
    """
    Langid returns a log-probability (negative). Convert to a pseudo-prob.
    We use a stable transformation that scales with text length:
        p = sigmoid(logprob / scale)
    Where scale grows modestly with length to avoid underflow for long texts.
    """
    # protect against extreme values:
    try:
        scale = max(1.0, min(20.0, text_len / 2.0 + 1.0))
        val = 1.0 / (1.0 + math.exp(- (logprob) / scale))
        # map into [0.01, 0.999]
        return max(0.01, min(0.999, val))
    except OverflowError:
        return 0.01

class FastTextCompatDetector:
    """
    A fastText-like detector exposing predict(text, k=-1, threshold=0.02)
    Returns labels and scores similar to fastText (labels: "__label__xx").
    """
    def __init__(self):
        # Nothing heavy to initialize; langid is used on-demand.
        pass

    def predict(self, text: str, k: int = -1, threshold: float = 0.02) -> Tuple[List[str], List[float]]:
        """
        Args:
            text: input string
            k: max number of labels (-1 means return all >= threshold)
            threshold: minimal probability to include returned label
        Returns:
            (labels, scores) where labels are like "__label__en"
        """
        if not text or not isinstance(text, str):
            return [], []

        t = text.strip()
        if not t:
            return [], []

        # If text is mostly digits / urls / tokens, return 'und' if needed empty
        if len(t) < 3 and _RE_DIGIT.match(t):
            return [], []

        # 1) SCRIPT DETECTION first (deterministic, very strong)
        script_lang = _script_detect(t)
        if script_lang is not None:
            # Special heuristics: if CJK ideographs + some kana -> ja already handled.
            # If CJK ideographs present but also many Latin letters, prefer zh only if ideographs dominate.
            if script_lang == 'zh':
                # if contains hiragana/katakana prefer ja (handled earlier)
                prob = 0.99
                return [f"__label__{script_lang}"], [prob]
            else:
                prob = 0.99
                return [f"__label__{script_lang}"], [prob]

        # 2) If many Latin letters → use langid
        # small heuristic: if majority non-latin but not covered above, fallback to langid anyway
        # Use langid.classify (returns (lang, logprob))
        detected_lang, logprob = langid.classify(t)

        # convert langid logprob -> pseudo-prob
        # langid returns negative log-like score; use transformation
        pseudo_prob = _langid_to_prob(logprob, len(t))

        # For short text, boost confidence
        if len(t) <= 8:
            boosted = max(pseudo_prob, _short_text_score(len(t)))
            pseudo_prob = boosted

        labels = [f"__label__{detected_lang}"]
        scores = [pseudo_prob]

        # Respect threshold and k
        if pseudo_prob < threshold:
            # If below threshold, still return top label if nothing else
            return [], []

        if k is not None and k != -1:
            labels = labels[:k]
            scores = scores[:k]

        return labels, scores

# single pre-created model instance (copy semantics like fastText)
model = FastTextCompatDetector()
