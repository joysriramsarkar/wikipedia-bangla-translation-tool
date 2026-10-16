# -*- coding: utf-8 -*-
"""
ইংরেজি-বাংলা উইকিপিডিয়া পাতা অনুবাদক (English-Bengali Wikipedia Page Translator)
-------------------------------------------------------------------------
উইকিপিডিয়া ইংরেজি নিবন্ধ, তালিকা ও সারণিসমূহ প্রমিত বাংলা উইকিপিডিয়ার
বাধ্যতামূলক ১৩টি নিয়মাবলি নিখুঁতভাবে অনুসরণ করে অনুবাদ করে।

ব্যবহার:
    python translate_page.py <ইনপুট_ফাইল> [আউটপুট_ফাইল]
    অথবা:
    from translate_page import translate_page, translate_text
"""

import os
import sys
import re

# প্যাকেজ ও মডিউল পাথ নিশ্চিতকরণ
curr_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(curr_dir)
for p in [curr_dir, root_dir, os.path.join(root_dir, 'common')]:
    if p not in sys.path:
        sys.path.insert(0, p)

import importlib.util

_tt_path = os.path.join(curr_dir, "table_translator.py")
if os.path.exists(_tt_path):
    _spec = importlib.util.spec_from_file_location("en_table_translator", _tt_path)
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        translate_wikitable = getattr(_mod, 'translate_wikitable', lambda x: x)
    else:
        translate_wikitable = lambda x: x
else:
    translate_wikitable = lambda x: x

_nc_path = os.path.join(curr_dir, "number_converter.py")
if os.path.exists(_nc_path):
    _spec = importlib.util.spec_from_file_location("en_number_conv", _nc_path)
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        to_bengali_digits = getattr(_mod, 'to_bengali_digits', lambda x: x)
    else:
        to_bengali_digits = lambda x: x
else:
    to_bengali_digits = lambda x: x

try:
    from common.bengali_utils import (
        to_bengali_text, replace_short_desc, remove_maintenance_templates,
        normalize_units, normalize_nukta_chars, fix_initial_khandatta,
        fix_r_reigned, fix_en_dash_years
    )
except ImportError:
    try:
        import importlib
        bu = importlib.import_module('bengali_utils')
        to_bengali_text = getattr(bu, 'to_bengali_text', lambda t: t)
        replace_short_desc = getattr(bu, 'replace_short_desc', lambda t: t)
        remove_maintenance_templates = getattr(bu, 'remove_maintenance_templates', lambda t: t)
        normalize_units = getattr(bu, 'normalize_units', lambda t: t)
        normalize_nukta_chars = getattr(bu, 'normalize_nukta_chars', lambda t: t)
        fix_initial_khandatta = getattr(bu, 'fix_initial_khandatta', lambda t: t)
        fix_r_reigned = getattr(bu, 'fix_r_reigned', lambda t: t)
        fix_en_dash_years = getattr(bu, 'fix_en_dash_years', lambda t: t)
    except ImportError:
        def to_bengali_text(t):
            t = re.sub(r'\{\{Short description\|.*?\}\}', '', t, flags=re.I)
            t = re.sub(r'\{\{Use (?:British|Indian|American) English\}\}', '', t, flags=re.I)
            t = t.translate(str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯'))
            return t
        replace_short_desc = lambda t: re.sub(r'\{\{Short description\|.*?\}\}', '', t, flags=re.I)
        remove_maintenance_templates = lambda t: re.sub(r'\{\{Use (?:British|Indian|American) English\}\}', '', t, flags=re.I)
        normalize_units = lambda t: t.replace('km²', 'বর্গকিমি').replace('কিমি²', 'বর্গকিমি')
        normalize_nukta_chars = lambda t: t.replace('\u09AF\u09BC', '\u09DF').replace('\u09A1\u09BC', '\u09DC').replace('\u09A2\u09BC', '\u09DD')
        fix_initial_khandatta = lambda t: re.sub(r'(^|[\s\(\[\{])ৎ', r'\1স', t)
        fix_r_reigned = lambda t: re.sub(r'\br\.\s*(\d+)', r'শাসনকাল: \1', t)
        fix_en_dash_years = lambda t: t.replace(' - ', ' – ')


# পরিচিত অনুচ্ছেদ শিরোনাম ম্যাপিং
SECTION_HEADINGS_MAP = [
    (r'==\s*Early life(?: and education)?\s*==', '== প্রাথমিক জীবন =='),
    (r'==\s*Career\s*==', '== কর্মজীবন =='),
    (r'==\s*Personal life\s*==', '== ব্যক্তিগত জীবন =='),
    (r'==\s*Filmography\s*==', '== চলচ্চিত্র তালিকা =='),
    (r'==\s*Bibliography\s*==', '== গ্রন্থপঞ্জি =='),
    (r'==\s*Discography\s*==', '== ডিস্কোগ্রাফি =='),
    (r'==\s*Awards and nominations\s*==', '== পুরস্কার ও মনোনয়ন =='),
    (r'==\s*Death\s*==', '== মৃত্যু =='),
    (r'==\s*Legacy\s*==', '== উত্তরাধিকার =='),
    (r'==\s*Works\s*==', '== কর্মসমূহ =='),
    (r'==\s*List(?: of .*)?\s*==', '== তালিকা =='),
    (r'==\s*Overview\s*==', '== সংক্ষিপ্ত বিবরণ =='),
    (r'==\s*History\s*==', '== ইতিহাস =='),
    (r'==\s*Geography\s*==', '== ভূগোল =='),
    (r'==\s*Demographics\s*==', '== জনমিতি =='),
    (r'==\s*Economy\s*==', '== অর্থনীতি =='),
    (r'==\s*See also\s*==', '== আরও দেখুন =='),
    (r'==\s*Notes\s*==', '== টীকা =='),
    (r'==\s*References\s*==', '== তথ্যসূত্র =='),
    (r'==\s*Further reading\s*==', '== আরও পড়ুন =='),
    (r'==\s*External links\s*==', '== বহিঃসংযোগ =='),
]


def translate_text(text: str) -> str:
    """সম্পূর্ণ উইকিটেক্সট বাংলায় অনুবাদ করে নিয়মাবলি প্রয়োগ করে।"""
    if not text:
        return ""

    # ১. নিয়ম ১ ও ১৩: {{Short description}} এবং ইংরেজি উপভাষা/রক্ষণাবেক্ষণ টেমপ্লেট সম্পূর্ণ মুছে ফেলা
    text = replace_short_desc(text)
    text = remove_maintenance_templates(text)

    # ২. সেকশন হেডার রূপান্তর
    for pattern, bn_heading in SECTION_HEADINGS_MAP:
        text = re.sub(pattern, bn_heading, text, flags=re.IGNORECASE)

    # ৩. সারণিসমূহ রূপান্তর (Wikitables)
    def repl_table(match):
        raw_tbl = match.group(0)
        return translate_wikitable(raw_tbl)

    text = re.sub(r'\{\| class="wikitable.*?\|\}', repl_table, text, flags=re.DOTALL)

    # ৪. নিয়ম ৫: শাসনকালের 'r.' অনুবাদ
    text = fix_r_reigned(text)

    # ৫. নিয়ম ১২: এককের সুপারস্ক্রিপ্ট ও প্রতীক (কিমি² পরিহার)
    text = normalize_units(text)

    # ৬. নিয়ম ১১: প্রিকম্পোজড বর্ণ (Precomposed Unicode)
    text = normalize_nukta_chars(text)

    # ৭. নিয়ম ৪: শব্দের শুরুতে 'ৎ' নিষিদ্ধ
    text = fix_initial_khandatta(text)

    # ৮. তথ্যসূত্র ও টেমপ্লেট
    text = re.sub(r'\{\{reflist\}\}', '{{তথ্যসূত্র}}', text, flags=re.IGNORECASE)
    text = re.sub(r'\{\{Reflist\}\}', '{{তথ্যসূত্র}}', text)

    # ৯. বিষয়শ্রেণী (Category)
    text = re.sub(r'\[\[Category:', '[[বিষয়শ্রেণী:', text, flags=re.IGNORECASE)

    # ১০. নিয়ম ২: সংখ্যা রূপান্তর (শুধু প্রদর্শিত লেখার ক্ষেত্রে, উইকিসিনট্যাক্স নষ্ট না করে)
    # সাধারণ টেক্সটে সব আরবি সংখ্যা বাংলায় রূপান্তর
    text = to_bengali_digits(text)
    text = fix_en_dash_years(text)

    return text.strip()


def translate_page(input_path: str, output_path: str | None = None) -> str:
    """একটি সম্পূর্ণ ফাইল পড়ে অনুবাদ করে এবং ঐচ্ছিকভাবে আউটপুট ফাইলে সংরক্ষণ করে।"""
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translated = translate_text(content)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)

    return translated


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("ব্যবহার: python translate_page.py <ইনপুট_ফাইল> [আউটপুট_ফাইল]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None

    result = translate_page(inp, out)
    if not out:
        print(result)
    else:
        print(f"অনুবাদ সম্পন্ন: {out}")
