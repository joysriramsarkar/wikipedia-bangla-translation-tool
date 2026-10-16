# -*- coding: utf-8 -*-
"""
Bengali common utilities for Wikipedia translation
"""
import re

def to_bengali_digits(text):
    """Convert English/Arabic digits to Bengali digits."""
    if not text:
        return text
    mapping = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
    return text.translate(mapping)

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

def normalize_units(text):
    """
    Avoid raw Latin superscript ² and ³ (Rule 12).
    Convert km² -> বর্গকিমি, m² -> বর্গমি, etc.
    """
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
        text = re.sub(pat, rep, text, flags=re.IGNORECASE)
    return text

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
    text = to_bengali_digits(text)
    text = fix_en_dash_years(text)
    return text

