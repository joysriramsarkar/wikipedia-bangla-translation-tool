# -*- coding: utf-8 -*-
"""
Bengali common utilities for Wikipedia translation

Two digit converters live here:

* :func:`to_bengali_digits` — blind conversion of every ASCII digit.
* :func:`to_bengali_digits_safe` — converts only *visible* digits and keeps
  technical spans (URLs, file names, template parameter keys, coordinates,
  ISBN/DOI, CSS) untouched.  Use this one for wikitext.
"""
import re

BN_DIGITS = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
BN_TO_ASCII_DIGITS = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')

# Private-use range used for placeholder tokens.  These characters cannot
# collide with real wikitext and contain no ASCII digits.
_TOKEN_START = 0xE000
_TOKEN_END = 0xF8FF
_TOKEN_RE = re.compile('\x00[\uE000-\uF8FF]\x00')


def to_bengali_digits(text):
    """Convert English/Arabic digits to Bengali digits.

    This converts *everything*, including digits inside URLs and file names.
    For wikitext use :func:`to_bengali_digits_safe` instead.
    """
    if not text:
        return text
    return text.translate(BN_DIGITS)


def to_ascii_digits(text):
    """Convert Bengali digits back to ASCII digits (0-9)."""
    if not text:
        return text
    return text.translate(BN_TO_ASCII_DIGITS)


def normalize_nukta_chars(text):
    """Normalize pre-composed nukta chars. Ensure usage of য়, ড়, ঢ়."""
    # Convert decomposed forms to precomposed
    text = text.replace('\u09AF\u09BC', '\u09DF')  # য + ় -> য়
    text = text.replace('\u09A1\u09BC', '\u09DC')  # ড + ় -> ড়
    text = text.replace('\u09A2\u09BC', '\u09DD')  # ঢ + ় -> ঢ়
    return text


def has_invalid_nukta(text):
    """Check if text has decomposed nukta forms."""
    return ('\u09AF\u09BC' in text or
            '\u09A1\u09BC' in text or
            '\u09A2\u09BC' in text)


def fix_en_dash_years(text):
    """Use en dash for year ranges."""
    return text.replace(' - ', ' – ')


def replace_short_desc(text):
    """Remove {{Short description}} tags."""
    patterns = [
        r'\{\{Short description\|.*?\}\}',
        r'\{\{Short description\|none\}\}',
        r'\{\{short description\|.*?\}\}',
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE | re.DOTALL)
    return text


def fix_r_reigned(text):
    """Convert 'r. YYYY' or 'r. YYYY–YYYY' to 'শাসনকাল: YYYY'."""
    # Match patterns like r. 1202–1203, r. 1143
    # Replace digits in the captured group with Bengali digits
    def repl(match):
        captured = match.group(1)
        return 'শাসনকাল: ' + to_bengali_digits(captured)
    text = re.sub(r'\br\.\s*(\d{1,4}(?:\s*[–-]\s*\d{1,4})?)\b',
                  repl, text)
    return text


def remove_maintenance_templates(text):
    """Remove English maintenance and dialect templates (Rule 13)."""
    patterns = [
        r'\{\{Use (?:British|Indian|American|Australian|Canadian|New Zealand|Irish|Scottish) English\}\}\n?',
        r'\{\{Use (?:dmy|mdy) dates\}\}\n?',
        r'\{\{Use dmy\}\}\n?',
        r'\{\{Use mdy\}\}\n?',
        r'\{\{force cite load\}\}\n?',
    ]
    for p in patterns:
        text = re.sub(p, '', text, flags=re.IGNORECASE)
    return text


# ---------------------------------------------------------------------------
# Ordinals
# ---------------------------------------------------------------------------

def _ordinal_suffix(number: int) -> str:
    if number == 1:
        return 'ম'
    if number in (2, 3):
        return 'য়'
    if number == 4:
        return 'র্থ'
    if number == 6:
        return 'ষ্ঠ'
    return 'ম'


def convert_ordinals(text):
    """Convert English ordinals: 2nd -> ২য়, 4th -> ৪র্থ, 5th -> ৫ম, 6th -> ৬ষ্ঠ."""
    if not text:
        return text

    def _repl(match):
        number = int(match.group(1))
        return match.group(1).translate(BN_DIGITS) + _ordinal_suffix(number)

    # Only one/two digit ordinals so that years (2007) are not touched.
    return re.sub(r'\b(\d{1,2})(st|nd|rd|th)\b', _repl, text, flags=re.IGNORECASE)


def fix_template_parameter_digits(text):
    """Keep template parameter names/variables in ASCII digits.

    MediaWiki and Lua modules (Module:Navbox, Module:Infobox, ...) do not
    recognise ``group১``, ``list১০`` or ``{{{১|...}}}``; converting those
    breaks the template box.  Only the *keys* are repaired, values stay as-is.
    """
    if not text:
        return text

    def _repl_key(match):
        return match.group(0).translate(BN_TO_ASCII_DIGITS)

    # |group১ =, |list১০ =, |১ =
    text = re.sub(
        r"\|\s*[a-zA-Z0-9_\-\u0980-\u09FF]*[০-৯]+[a-zA-Z0-9_\-\u0980-\u09FF]*\s*=",
        _repl_key,
        text,
    )

    # {{{১|..., {{{২}}}
    text = re.sub(
        r"\{\{\{\s*[a-zA-Z0-9_\u0980-\u09FF]*[০-৯]+[a-zA-Z0-9_\u0980-\u09FF]*\s*(?:\||\}\}\})",
        _repl_key,
        text,
    )
    return text


# ---------------------------------------------------------------------------
# Safe digit conversion
# ---------------------------------------------------------------------------

#: Spans whose digits are machine-readable and must never become Bengali.
_PROTECTED_PATTERNS = (
    # HTML entities: &nbsp; &#160; &#x00A0;
    r'&(?:#\d+|#x[0-9a-fA-F]+|[a-zA-Z][a-zA-Z0-9]*);',
    # URLs and bare domains (``|`` ends a URL inside a template)
    r'https?://[^\s<>\]\}\|]+',
    r'\bwww\.[^\s<>\]\}\|]+',
    # File/Image link target (caption after the pipe is still converted)
    r'\[\[\s*(?:File|Image|চিত্র|ফাইল)\s*:[^\]\|\n]*',
    # Bare file name in infobox parameters (| image = File:Photo 2020.jpg)
    r'\b(?:File|Image|চিত্র|ফাইল)\s*:\s*[^\|\]\}\n]+',
    # Technical namespace link targets
    r'\[\[\s*(?:Module|মডিউল|Special|বিশেষ|Wikipedia|উইকিপিডিয়া|Help|সাহায্য|'
    r'Template|টেমপ্লেট|Category|বিষয়শ্রেণী|বিষয়শ্রেণী|Portal|প্রবেশদ্বার|'
    r'MediaWiki|মিডিয়াউইকি)\s*:[^\]\|\n]*',
    # <gallery> file lines
    r'(?m)^[ \t]*(?:File|Image|চিত্র|ফাইল)\s*:[^\|\n]*',
    # Coordinate / timezone templates are parsed by machines
    r'\{\{\s*(?:coord|Coord|COORD|ইউটিসি|UTC)\s*\|[^{}]*\}\}',
    # Date templates are parsed by MediaWiki; their numeric args must stay ASCII
    r'\{\{\s*(?:Start date|End date|start date|end date)\s*\|[^{}]*\}\}',
    # Specific parameter line for series links
    r'\|\s*link\d+\s*=[^\n]*',
    # Section/anchor fragments (#Season 17) must keep ASCII digits (not wikitext ordered list items starting with #)
    r'(?<![\n#|\]\}])#[A-Za-z][^\|\]\}\n]*',
    # Identifiers
    r'\bISBN[\s:]*(?:97[89][\d\- ]{10,}|[\dXx][\dXx\- ]{8,})',
    r'\bDOI[\s:]*[^\s<>\]\}]+',
    r'\bPMID[\s:]*\d+',
    # Magic words and signatures
    r'__[A-Z]+__',
    r'~{3,}',
    # Template parameter keys (|group1 =, |list10 =, |editor-last2 =)
    r'\|\s*[A-Za-z0-9_\-\u0980-\u09FF]*\d+[A-Za-z0-9_\-\u0980-\u09FF]*\s*=',
    # Positional template variables ({{{1|...}}})
    r'\{\{\{\s*[A-Za-z0-9_\u0980-\u09FF]*\d+[A-Za-z0-9_\u0980-\u09FF]*\s*(?:\||\}\}\})',
    # Numeric attributes of tables/images
    r'(?:rowspan|colspan|width|height|upright)\s*=\s*["\']?[\d.%]+[a-z%]*["\']?',
    r'\|\s*\d+(?:x\d+)?\s*px\b',
    r'\b\d+(?:x\d+)?px\b',
    r'style\s*=\s*"[^"]*"',
    r"style\s*=\s*'[^']*'",
    # Colours
    r'#[0-9a-fA-F]{3,8}\b',
    r'\b(?:rgb|rgba|hsl|hsla)\([^)]*\)',
)

_HTML_TAG_SPLIT = re.compile(r'(<[^>]*>)')


def _token_for(index: int) -> str:
    return '\x00' + chr(_TOKEN_START + index) + '\x00'


def _protect_spans(text: str):
    """Replace technical spans with opaque tokens; return (text, tokens)."""
    placeholders = []

    def _save(match):
        if len(placeholders) > (_TOKEN_END - _TOKEN_START):
            return match.group(0)
        token = _token_for(len(placeholders))
        placeholders.append((token, match.group(0)))
        return token

    protected = text
    for pattern in _PROTECTED_PATTERNS:
        protected = re.sub(pattern, _save, protected)
    return protected, placeholders


def _restore_spans(text: str, placeholders) -> str:
    for token, original in reversed(placeholders):
        text = text.replace(token, original)
    return text


def _convert_text_node(node: str) -> str:
    protected, placeholders = _protect_spans(node)
    protected = convert_ordinals(protected)
    protected = protected.translate(BN_DIGITS)
    return _restore_spans(protected, placeholders)


def to_bengali_digits_safe(text):
    """Convert visible digits to Bengali while keeping wikitext working.

    Protected: ``<...>`` tags and attributes, URLs, ``[[File:...]]`` targets,
    template parameter names, coordinates, ISBN/DOI/PMID, ``NNNpx`` sizes,
    CSS colours and HTML entities.  Everything else — prose, table cells,
    captions — is converted, including ordinals (``2nd`` -> ``২য়``).
    """
    if not text:
        return text

    parts = _HTML_TAG_SPLIT.split(text)
    out = []
    for part in parts:
        if not part:
            continue
        if part.startswith('<') and part.endswith('>'):
            out.append(part)  # tag/attribute: untouched
        else:
            out.append(_convert_text_node(part))
    return fix_template_parameter_digits(''.join(out))


def strip_technical_spans(text):
    """Blank out technical spans so a digit check only sees visible text.

    Used by rule validators: digits inside a URL or a file name are legal and
    must not be reported as "English digits remain".
    """
    if not text:
        return text

    parts = _HTML_TAG_SPLIT.split(text)
    out = []
    for part in parts:
        if not part:
            continue
        if part.startswith('<') and part.endswith('>'):
            out.append(' ')
        else:
            protected, _ = _protect_spans(part)
            out.append(_TOKEN_RE.sub(' ', protected))
    return ''.join(out)


# ---------------------------------------------------------------------------
# Units and sorting
# ---------------------------------------------------------------------------

def normalize_units(text):
    """
    Avoid raw Latin superscript ² and ³ (Rule 12).
    Convert km² -> বর্গকিমি, m² -> বর্গমি, etc.

    URLs are masked first so ``.../km2`` is not rewritten.
    """
    protected, placeholders = _protect_spans(text)
    replacements = [
        (r'\b(?:km|কিমি)[²2]\b', 'বর্গকিমি'),
        (r'\b(?:sq\s*km|sq\.?\s*km|square\s+kilometers?)\b', 'বর্গকিমি'),
        (r'\b(?:sq\s*mi|sq\.?\s*mi|square\s+miles?)\b', 'বর্গমাইল'),
        (r'\b(?:m|মি)[²2]\b', 'বর্গমি'),
        (r'\b(?:km|কিমি)[³3]\b', 'ঘনকিমি'),
        (r'\b(?:m|মি)[³3]\b', 'ঘনমি'),
        (r'কিমি²', 'বর্গকিমি'),
        (r'মি²', 'বর্গমি'),
        (r'কিমি³', 'ঘনকিমি'),
        (r'মি³', 'ঘনমি'),
    ]
    for pat, rep in replacements:
        protected = re.sub(pat, rep, protected, flags=re.IGNORECASE)
    return _restore_spans(protected, placeholders)


def fix_initial_khandatta(text):
    """
    Bangla words cannot start with ৎ (Rule 4).
    Replace initial ৎ with স/সু.
    """
    text = re.sub(r'(^|[\s\(\[\{])ৎসু', r'\1সু', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎসা', r'\1সা', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎসি', r'\1সি', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎসে', r'\1সে', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎসো', r'\1সো', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎস', r'\1স', text)
    text = re.sub(r'(^|[\s\(\[\{])ৎ', r'\1স', text)
    return text


_BN_ORDER = "অআইঈউঊঋএঐওঔকখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎংঃঁ"
_BN_CHAR_RANK = {ch: i for i, ch in enumerate(_BN_ORDER)}


def bengali_sort_key(word: str):
    """
    Generate sort key for Bengali alphabetical order (Rule 3).
    অ-হ, ড়, ঢ়, য়, ৎ, ং, ঃ, ঁ
    """
    cleaned = re.sub(r'^[\[\'"]+|[\]\'"]+$', '', str(word)).strip()
    return [_BN_CHAR_RANK.get(c, 1000 + ord(c)) for c in cleaned]


def to_bengali_text(text):
    """Apply common Bengali Wikipedia normalization rules."""
    text = replace_short_desc(text)
    text = remove_maintenance_templates(text)
    text = fix_r_reigned(text)
    text = normalize_nukta_chars(text)
    text = fix_initial_khandatta(text)
    text = normalize_units(text)
    text = to_bengali_digits_safe(text)
    text = fix_en_dash_years(text)
    return text
