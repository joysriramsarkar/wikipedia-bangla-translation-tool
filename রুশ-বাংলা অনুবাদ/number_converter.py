# -*- coding: utf-8 -*-
"""
রুশ-বাংলা সংখ্যা ও বিন্যাস রূপান্তরক (Russian-Bengali Number & Format Converter)
জনসংখ্যা এবং সাল বাংলায় রূপান্তর করে, এইচটিএমএল/মিডিয়াউইকি ট্যাগ অক্ষুণ্ণ রেখে।
"""
import re

BENGALI_DIGITS = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')

def format_bengali_number(num_str: str) -> str:
    """একটি পূর্ণসংখ্যা বা দশমিক সংখ্যাকে বাংলা কমা সহ রূপান্তর করে।"""
    s = num_str.strip().replace(',', '')
    if not s.isdigit():
        return s.translate(BENGALI_DIGITS)
    
    # ভারতীয়/আন্তর্জাতিক কমা বিন্যাস: শেষ ৩ ডিজিট, তারপর প্রতি ২ ডিজিট
    # যেমন: 31766 -> ৩১,৭৬৬; 1234567 -> ১২,৩৪,৫৬৭
    n = len(s)
    if n <= 3:
        return s.translate(BENGALI_DIGITS)
    
    last3 = s[-3:]
    remaining = s[:-3]
    parts = []
    while len(remaining) > 2:
        parts.insert(0, remaining[-2:])
        remaining = remaining[:-2]
    if remaining:
        parts.insert(0, remaining)
    parts.append(last3)
    formatted = ','.join(parts)
    return formatted.translate(BENGALI_DIGITS)

def to_bengali_digits(text: str) -> str:
    """যেকোনো টেক্সটের আরবি সংখ্যাকে বাংলা সংখ্যায় রূপান্তর করে (ট্যাগ সুরক্ষিত রেখে)।"""
    placeholders = []

    def repl_save(match):
        idx = len(placeholders)
        tag = f"__RUSTOK_{idx}__"
        placeholders.append((tag, match.group(0)))
        return tag

    s = text
    # সুরক্ষিত প্যাটার্ন: HTML attributes, ref tags, urls, templates
    s = re.sub(r'url=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'archiveurl=[^\s\|\}]+', repl_save, s)
    s = re.sub(r'style="[^"]*"', repl_save, s)
    s = re.sub(r'class="[^"]*"', repl_save, s)
    s = re.sub(r'rowspan="[0-9]+"', repl_save, s)
    s = re.sub(r'colspan="[0-9]+"', repl_save, s)
    s = re.sub(r'<ref[^>]*>.*?</ref>', repl_save, s, flags=re.DOTALL)
    s = re.sub(r'<ref[^>]*/>', repl_save, s)
    s = re.sub(r'<ref[^>]*>', repl_save, s)
    s = re.sub(r'</ref>', repl_save, s)
    s = re.sub(r'\{\{ru-pop-ref\|[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{cite[^}]+\}\}', repl_save, s)
    s = re.sub(r'\{\{lang\|[^}]+\}\}', repl_save, s)

    # যদি কেবল ৪-৮ অঙ্কের জনসংখ্যার সংখ্যা হয়, কমা সহ রূপান্তর
    def repl_pop(m):
        raw_num = m.group(1)
        return format_bengali_number(raw_num)

    s = re.sub(r'\b(\d{4,9})\b', repl_pop, s)

    # বাকি ডিজিটগুলোকে সরাসরি রূপান্তর (যেমন সাল ২০১০)
    s = s.translate(BENGALI_DIGITS)

    # টোকেন পুনরুদ্ধার
    for tag, orig in placeholders:
        tag_tr = tag.translate(BENGALI_DIGITS)
        s = s.replace(tag_tr, orig)

    return s
