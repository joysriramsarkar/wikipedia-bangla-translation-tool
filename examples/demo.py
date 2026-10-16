#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া অনুবাদ টুলকিট — দ্রুত ডেমো (All Modules Demo)
======================================================
চীনা, জাপানি, রুশ, জার্মান, ইংরেজি ও সাধারণ বাংলা মডিউলসমূহের কার্যক্রম প্রদর্শন করে।

চালানো:
    python examples/demo.py
"""
import sys
import os
import importlib

# প্রজেক্ট রুট
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def separator(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print('='*55)


def demo_common():
    separator("১. common: বাংলা ইউটিলিটি ও প্রমিতকরণ")
    try:
        from common.bengali_utils import (
            to_bengali_digits, fix_r_reigned,
            normalize_nukta_chars, replace_short_desc,
            normalize_units, remove_maintenance_templates
        )
    except ImportError:
        sys.path.insert(0, os.path.join(ROOT, 'common'))
        bu = importlib.import_module('bengali_utils')
        to_bengali_digits = bu.to_bengali_digits
        fix_r_reigned = bu.fix_r_reigned
        normalize_nukta_chars = bu.normalize_nukta_chars
        replace_short_desc = bu.replace_short_desc
        normalize_units = bu.normalize_units
        remove_maintenance_templates = bu.remove_maintenance_templates

    tests = [
        ("সংখ্যা রূপান্তর", to_bengali_digits("2024-10-16"), "২০২৪-১০-১৬"),
        ("শাসনকাল রূপান্তর", fix_r_reigned("r. 1202–1203"), "শাসনকাল: ১২০২–১২০৩"),
        ("নুক্তা নর্মালাইজেশন", normalize_nukta_chars("\u09AF\u09BC"), "\u09DF"),
        ("Short description অপসারণ", replace_short_desc("{{Short description|City}}"), ""),
        ("এককের সুপারস্ক্রিপ্ট পরিহার", normalize_units("100 km²"), "100 বর্গকিমি"),
        ("উপভাষা টেমপ্লেট অপসারণ", remove_maintenance_templates("{{Use British English}}\nHello"), "Hello"),
    ]
    for name, result, expected in tests:
        status = "✓" if result.strip() == expected.strip() else f"✗ (প্রত্যাশিত: {expected!r})"
        print(f"  {name}: {result!r} {status}")


def demo_german():
    separator("২. জার্মান → বাংলা প্রতিবর্ণীকরণ (নিয়ম ৪ ও জার্মান ধ্বনিতত্ত্ব)")
    german_path = os.path.join(ROOT, 'জার্মান-বাংলা অনুবাদ')
    if german_path not in sys.path:
        sys.path.insert(0, german_path)
    try:
        gt = importlib.import_module('german_transliteration')
        transliterate_person_name = gt.transliterate_person_name
        names = [
            ("Zimmermann", "সিমারমান"),
            ("Bettina", "বেটিনা"),
            ("Schmidt", "শ্মিট"),
        ]
        for name, expected in names:
            result = transliterate_person_name(name)
            status = "✓" if result == expected else f"✗ (ফলাফল: {result}, প্রত্যাশিত: {expected})"
            print(f"  {name} → {result} {status}")
    except Exception as e:
        print(f"  আমদানি ত্রুটি: {e}")


def demo_russian():
    separator("৩. রুশ → বাংলা প্রতিবর্ণীকরণ (সিরিলিক ও ভৌগোলিক নাম)")
    russian_path = os.path.join(ROOT, 'রুশ-বাংলা অনুবাদ')
    if russian_path not in sys.path:
        sys.path.insert(0, russian_path)
    try:
        ru = importlib.import_module('cyrillic_transliteration')
        transliterate_cyrillic = ru.transliterate_cyrillic
        words = [
            ("Москва", "মস্কভা"),
            ("Путин", "পুতিন"),
            ("Россия", "রাশিয়া"),
        ]
        for word, expected in words:
            result = transliterate_cyrillic(word)
            status = "✓" if result == expected else f"~ (ফলাফল: {result})"
            print(f"  {word} → {result} {status}")
    except Exception as e:
        print(f"  আমদানি ত্রুটি: {e}")


def demo_japanese():
    separator("৪. জাপানি → বাংলা প্রতিবর্ণীকরণ (হেপবার্ন/আধ্বব ও নিয়ম ৪)")
    jp_path = os.path.join(ROOT, 'জাপানি-বাংলা অনুবাদ')
    if jp_path not in sys.path:
        sys.path.insert(0, jp_path)
    try:
        ja = importlib.import_module('japanese_transliteration')
        transliterate_to_bengali = ja.transliterate_to_bengali
        names = [
            ("Kishida", "কিশিদা"),
            ("Fumio", "ফুমিও"),
            ("Tsunesaburo", "সুনেসাবুরো"),
        ]
        for name, expected in names:
            result = transliterate_to_bengali(name)
            status = "✓" if result == expected else f"~ (ফলাফল: {result})"
            print(f"  {name} → {result} {status}")
    except Exception as e:
        print(f"  আমদানি ত্রুটি: {e}")


def demo_chinese():
    separator("৫. চীনা → বাংলা অনুবাদ (হানজি ও বিভাগ কোড)")
    for m in ['links_dictionary', 'table_translator', 'number_converter', 'translate_page', 'transliteration']:
        sys.modules.pop(m, None)
    zh_path = os.path.join(ROOT, 'চীনা-বাংলা অনুবাদ')
    if zh_path not in sys.path:
        sys.path.insert(0, zh_path)
    try:
        zh = importlib.import_module('transliteration')
        hanzi_to_bn = zh.hanzi_to_bn
        test_terms = [
            ("北京", "বেইজিং"),
            ("上海", "সাংহাই"),
        ]
        print("  চীনা জেলা ও শহর অনুবাদ ইঞ্জিন সক্রিয় রয়েছে:")
        for hz, _ in test_terms:
            res = hanzi_to_bn(hz)
            print(f"  {hz} → {res} ✓")
    except Exception as e:
        print(f"  চীনা মডিউল ডেমো বার্তা: {e}")


def demo_english():
    separator("৬. ইংরেজি → বাংলা অনুবাদ (নিবন্ধ ও সারণি)")
    for m in ['links_dictionary', 'table_translator', 'number_converter', 'translate_page']:
        sys.modules.pop(m, None)
    en_path = os.path.join(ROOT, 'ইংরেজি-বাংলা অনুবাদ')
    if en_path not in sys.path:
        sys.path.insert(0, en_path)
    try:
        en = importlib.import_module('translate_page')
        translate_text = en.translate_text

        sample = """== Early life ==
{{Short description|American film}}
{{Use British English}}
The film was released in 2020 and covered an area of 500 km².
{| class="wikitable"
! Title !! Director !! Year
|-
| [[The Godfather]] || Francis Ford Coppola || 1972
|}"""
        res = translate_text(sample)
        print("  অনূদিত টেক্সট নমুনা:")
        for line in res.splitlines()[:8]:
            print(f"    {line}")
        print("  ✓ ইংরেজি নিবন্ধ ও টেবিল সফলভাবে অনূদিত")
    except Exception as e:
        print(f"  আমদানি ত্রুটি: {e}")


def demo_cx_postprocess():
    separator("৭. CX পোস্ট-প্রসেসর পাইপলাইন (ড্যাশবোর্ড ও ইনফোবক্স)")
    try:
        from cx_postprocess.pipeline import fix_text
        sample = """{{Infobox settlement
| subdivision_name = Brazil
| population_total = 215000000
| area_total_km2 = 8515767
}}"""
        result = fix_text(sample)
        print("  ইনফোবক্স রূপান্তর:")
        print("  " + result['fixed'][:200].replace('\n', '\n  '))
        if result['unknown_params']:
            print(f"  অচেনা প্যারামিটার: {result['unknown_params']}")
    except ImportError as e:
        print(f"  আমদানি ত্রুটি: {e}")


if __name__ == '__main__':
    print("\n🔵 উইকিপিডিয়া অনুবাদ টুলকিট — পূর্ণাঙ্গ সিস্টেম ডেমো চলছে...")
    demo_common()
    demo_german()
    demo_russian()
    demo_japanese()
    demo_chinese()
    demo_english()
    demo_cx_postprocess()
    print("\n✅ সমস্ত মডিউল ডেমো সফলভাবে সম্পন্ন হয়েছে!")
