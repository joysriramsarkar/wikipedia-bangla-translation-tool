# -*- coding: utf-8 -*-
"""
ইংরেজি সংখ্যা রূপান্তরক (Number Converter)
=============================================
ইংরেজি/আরবি সংখ্যা থেকে বাংলা সংখ্যায় রূপান্তর।
কোটি/লাখ/মিলিয়ন/বিলিয়ন শব্দ বাংলায় রূপান্তর করে।
"""
import re

# ইংরেজি → বাংলা সংখ্যা ম্যাপিং
_EN_TO_BN = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')

# বড় সংখ্যার শব্দ অনুবাদ
LARGE_NUM_MAP = {
    r'\btrillion\b': 'লক্ষ কোটি',
    r'\bbillion\b': 'বিলিয়ন',
    r'\bmillion\b': 'মিলিয়ন',
    r'\bthousand\b': 'হাজার',
    r'\bhundred\b': 'শত',
}

# ক্রমবাচক সংখ্যা
ORDINAL_MAP = {
    '1st': '১ম',
    '2nd': '২য়',
    '3rd': '৩য়',
    '4th': '৪র্থ',
    '5th': '৫ম',
    '6th': '৬ষ্ঠ',
    '7th': '৭ম',
    '8th': '৮ম',
    '9th': '৯ম',
    '10th': '১০ম',
}


def to_bengali_digits(text: str) -> str:
    """সরাসরি ইংরেজি সংখ্যাকে বাংলায় রূপান্তর করে।"""
    if not text:
        return text
    return text.translate(_EN_TO_BN)


def convert_ordinals(text: str) -> str:
    """ইংরেজি ক্রমবাচক সংখ্যা বাংলায় রূপান্তর করে।"""
    for en, bn in ORDINAL_MAP.items():
        text = re.sub(r'\b' + re.escape(en) + r'\b', bn, text, flags=re.IGNORECASE)
    # বাকি ক্রমবাচক (Nth → নতম)
    def generic_ordinal(m):
        n = to_bengali_digits(m.group(1))
        suffix = m.group(2).lower()
        bn_sfx = {'st': 'ম', 'nd': 'য়', 'rd': 'য়', 'th': 'তম'}.get(suffix, suffix)
        return f'{n}{bn_sfx}'
    text = re.sub(r'\b(\d+)(st|nd|rd|th)\b', generic_ordinal, text, flags=re.IGNORECASE)
    return text


def convert_large_numbers(text: str) -> str:
    """বড় সংখ্যার ইংরেজি শব্দ বাংলায় রূপান্তর করে।"""
    for pattern, replacement in LARGE_NUM_MAP.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def convert_year_ranges(text: str) -> str:
    """সাল পরিসর রূপান্তর (2010-2019 → ২০১০-২০১৯)।"""
    def year_range_repl(m):
        y1 = to_bengali_digits(m.group(1))
        y2 = to_bengali_digits(m.group(2))
        sep = m.group(3)
        return f'{y1}{sep}{y2}'
    text = re.sub(r'(\d{4})([-–—])(\d{2,4})', year_range_repl, text)
    return text


def convert_all(text: str) -> str:
    """সম্পূর্ণ সংখ্যা রূপান্তর পাইপলাইন প্রয়োগ করে।"""
    text = convert_ordinals(text)
    text = convert_large_numbers(text)
    text = convert_year_ranges(text)
    text = to_bengali_digits(text)
    return text
