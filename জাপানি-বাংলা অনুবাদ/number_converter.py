# -*- coding: utf-8 -*-
"""
জাপানি-বাংলা সংখ্যা ও তারিখ রূপান্তরক (Japanese-Bengali Number & Date Converter)
আরবি সংখ্যা ও ইংরেজি তারিখকে বাংলায় রূপান্তর করে, এইচটিএমএল/মিডিয়াউইকি ট্যাগ অক্ষুণ্ণ রেখে।
"""
import re

BENGALI_DIGITS = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')

MONTHS_MAP = {
    'January': 'জানুয়ারি',
    'February': 'ফেব্রুয়ারি',
    'March': 'মার্চ',
    'April': 'এপ্রিল',
    'May': 'মে',
    'June': 'জুন',
    'July': 'জুলাই',
    'August': 'আগস্ট',
    'September': 'সেপ্টেম্বর',
    'October': 'অক্টোবর',
    'November': 'নভেম্বর',
    'December': 'ডিসেম্বর',
}

def to_bengali_digits(text: str) -> str:
    """যেকোনো টেক্সটের আরবি সংখ্যাকে বাংলা সংখ্যায় রূপান্তর করে (ট্যাগ ও ফাইল সুরক্ষিত রেখে)।"""
    placeholders = []

    def repl_save(match):
        idx = len(placeholders)
        tag = f"__JAPTOK_{idx}__"
        placeholders.append((tag, match.group(0)))
        return tag

    s = text

    # ০. {{sort|key|display}} টেমপ্লেটের ডিসপ্লে সংখ্যা বাংলা করা
    def repl_sort_template(m):
        key = m.group(1)
        val = m.group(2)
        bn_val = val.translate(BENGALI_DIGITS)
        return f"{{{{sort|{key}|{bn_val}}}}}"

    s = re.sub(r'\{\{sort\|([^|]+)\|([^}]+)\}\}', repl_sort_template, s)

    # ১. সুরক্ষিত প্যাটার্ন: স্বয়ংসম্পূর্ণ ref (self-closing) আগে সুরক্ষিত করা যাতে লাইন না গ্রাস করে
    s = re.sub(r'<ref\b[^>/]*?/>', repl_save, s)
    s = re.sub(r'<ref[^>]*>.*?</ref>', repl_save, s, flags=re.DOTALL)
    s = re.sub(r'<ref[^>]*>', repl_save, s)
    s = re.sub(r'</ref>', repl_save, s)
    s = re.sub(r'\{\{cite[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{lang\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{sort\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{hs\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{TOC limit\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\[\[File:[^\]]+\]\]', repl_save, s)
    s = re.sub(r'\[\[Image:[^\]]+\]\]', repl_save, s)
    s = re.sub(r'url=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'archiveurl=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'isbn=[0-9X\-]+', repl_save, s, flags=re.I)
    s = re.sub(r'style="[^"]*"', repl_save, s)
    s = re.sub(r'class="[^"]*"', repl_save, s)
    s = re.sub(r'rowspan="?[0-9]+"?', repl_save, s)
    s = re.sub(r'colspan="?[0-9]+"?', repl_save, s)
    s = re.sub(r'width="?[0-9%px]+"?', repl_save, s)
    s = re.sub(r'#[0-9a-fA-F]{3,6}\b', repl_save, s)

    # ২. মাসের নাম রূপান্তর
    for en_m, bn_m in MONTHS_MAP.items():
        s = re.sub(rf'\b{en_m}\b', bn_m, s)

    # ৩. ঐতিহাসিক সাল ও সময়কাল পরিভাষা
    s = re.sub(r'\bBCE\b', 'খ্রিস্টপূর্ব', s)
    s = re.sub(r'\bBC\b', 'খ্রিস্টপূর্ব', s)
    s = re.sub(r'\bCE\b', 'খ্রিস্টাব্দ', s)
    s = re.sub(r'\bAD\b', 'খ্রিস্টাব্দ', s)
    s = re.sub(r'\bborn\s+(\d{4})\b', r'জন্ম \1', s, flags=re.I)
    s = re.sub(r'\bdied\s+(\d{4})\b', r'মৃত্যু \1', s, flags=re.I)
    s = re.sub(r',\s*r\.\s*(\d+)', r', শাসনকাল: \1', s)
    s = re.sub(r'\br\.\s*(\d+)', r'শাসনকাল: \1', s)

    # ৪. বাকি আরবি সংখ্যাগুলোকে বাংলা সংখ্যায় রূপান্তর
    s = s.translate(BENGALI_DIGITS)

    # ৫. টোকেন পুনরুদ্ধার (বিপরীত ক্রমে যাতে নেস্টেড টোকেনসমূহ সুরক্ষিত থাকে)
    for tag, orig in reversed(placeholders):
        tag_tr = tag.translate(BENGALI_DIGITS)
        s = s.replace(tag_tr, orig)
        s = s.replace(tag, orig)

    return s
