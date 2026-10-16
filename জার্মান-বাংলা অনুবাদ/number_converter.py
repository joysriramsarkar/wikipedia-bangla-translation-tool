# -*- coding: utf-8 -*-
"""
জার্মান-বাংলা সংখ্যা ও তারিখ রূপান্তরক (German-Bengali Number & Date Converter)
-----------------------------------------------------------------------
আরবি সংখ্যা (0-9) এবং ইংরেজি তারিখকে শতভাগ প্রমিত বাংলা সংখ্যায় (০-৯) রূপান্তর করে,
এইচটিএমএল/মিডিয়াউইকি ট্যাগ, ইউআরএল ও টেকনিক্যাল কোড সম্পূর্ণ অক্ষুণ্ণ রেখে।
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
    """যেকোনো টেক্সটের দৃশ্যমান সংখ্যা ও তারিখ বাংলায় রূপান্তর করে।"""
    placeholders = []

    def repl_save(match):
        idx = len(placeholders)
        tag = f"__GERTOK_{idx}__"
        placeholders.append((tag, match.group(0)))
        return tag

    s = text

    # ১. টেকনিক্যাল কোড ও ট্যাগ সংরক্ষণ
    # স্বয়ংসম্পূর্ণ ref (self-closing) আগে সুরক্ষিত করা যাতে লাইন না গ্রাস করে
    s = re.sub(r'<ref\b[^>/]*?/>', repl_save, s)
    s = re.sub(r'<ref[^>]*>.*?</ref>', repl_save, s, flags=re.DOTALL)
    s = re.sub(r'<ref[^>]*>', repl_save, s)
    s = re.sub(r'</ref>', repl_save, s)
    s = re.sub(r'<!--.*?-->', repl_save, s, flags=re.DOTALL)
    s = re.sub(r'\{\{cite[^}]+\}\}', repl_save, s, flags=re.I)
    s = re.sub(r'\{\{lang\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\[\[File:[^\]]+\]\]', repl_save, s, flags=re.I)
    s = re.sub(r'\[\[Image:[^\]]+\]\]', repl_save, s, flags=re.I)
    s = re.sub(r'url=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'archiveurl=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'style="[^"]*"', repl_save, s)
    s = re.sub(r'class="[^"]*"', repl_save, s)
    s = re.sub(r'rowspan="?[0-9]+"?', repl_save, s)
    s = re.sub(r'colspan="?[0-9]+"?', repl_save, s)
    s = re.sub(r'width="?[0-9%px]+"?', repl_save, s)
    s = re.sub(r'#[0-9a-fA-F]{3,6}\b', repl_save, s)

    # ১.১ মূল বিদেশী/জার্মান/ইংরেজি শিরোনাম ও বন্ধনীতে থাকা টেক্সট সংরক্ষণ (যাতে সংখ্যাগুলো বাংলা না হয়)
    # ক. বন্ধনীতে থাকা উদ্ধৃতিযুক্ত শিরোনাম বা অ-বাংলা সংখ্যা (যেমন: (''3 Days in Quiberon''), (''303''))
    s = re.sub(r"\((?:''|\")?[^)\n]*\d+[^)\n]*(?:''|\")?\)", lambda m: repl_save(m) if not re.search(r'[\u0980-\u09FF]', m.group(0)) else m.group(0), s)
    # খ. বন্ধনীতে থাকা যেকোনো ল্যাটিন হরফের টেক্সট (যেমন: (25 km/h), (actor), (de))
    s = re.sub(r"\([^)\n]*[a-zA-Z][^)\n]*\)", repl_save, s)
    # গ. ইটালিক্সে থাকা ল্যাটিন বা ইংরেজি শিরোনাম (যেমন: ''Sarajevo 1914: The Eve of the Great War'', ''48 Hours...'')
    s = re.sub(r"''(?:[^\u0980-\u09FF'\n]*[a-zA-Z][^\u0980-\u09FF'\n]*)''", repl_save, s)
    # ঘ. ওরফে বা aka-এর পরের ইংরেজি শিরোনাম
    s = re.sub(r"(?:\{\{aka\}\}|ওরফে)\s*(?:''|\")?[-A-Za-z0-9\s.,:!?\'\"&–—]+?(?:''|\")?(?=$|<br|,\s*[A-Z]|\n|\|)", lambda m: repl_save(m) if not re.search(r'[\u0980-\u09FF]', m.group(0).replace('ওরফে', '')) else m.group(0), s)
    # ঙ. ল্যাটিন শব্দের সাথে যুক্ত সংখ্যা (যেমন: 3D, km/h)
    s = re.sub(r'\b\d+[a-zA-Z]+\b', repl_save, s)
    s = re.sub(r'\b[a-zA-Z]+\d+\b', repl_save, s)

    # ২. মাসের নাম রূপান্তর
    for en_m, bn_m in MONTHS_MAP.items():
        s = re.sub(rf'\b{en_m}\b', bn_m, s)

    # ৩. ঐতিহাসিক সাল ও সময়কাল
    s = re.sub(r'\bBCE\b', 'খ্রিস্টপূর্ব', s)
    s = re.sub(r'\bBC\b', 'খ্রিস্টপূর্ব', s)
    s = re.sub(r'\bCE\b', 'খ্রিস্টাব্দ', s)
    s = re.sub(r'\bAD\b', 'খ্রিস্টাব্দ', s)

    # ৪. বাকি আরবি সংখ্যাগুলোকে বাংলা সংখ্যায় রূপান্তর
    s = s.translate(BENGALI_DIGITS)

    # ৫. টোকেন পুনরুদ্ধার
    for tag, orig in reversed(placeholders):
        tag_tr = tag.translate(BENGALI_DIGITS)
        s = s.replace(tag_tr, orig)
        s = s.replace(tag, orig)

    return s
