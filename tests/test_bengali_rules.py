# -*- coding: utf-8 -*-
"""
বাংলা উইকিপিডিয়া ১৩টি বাধ্যতামূলক নিয়মাবলির ইউনিট টেস্ট
(Bengali Wikipedia Mandatory 13 Rules Test Suite)
"""
import sys
import os
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
common_dir = os.path.join(ROOT, 'common')
if common_dir not in sys.path:
    sys.path.insert(0, common_dir)

try:
    from common.bengali_utils import (
        replace_short_desc,
        to_bengali_digits,
        bengali_sort_key,
        fix_initial_khandatta,
        fix_r_reigned,
        normalize_nukta_chars,
        has_invalid_nukta,
        normalize_units,
        remove_maintenance_templates,
        to_bengali_text,
    )
except ImportError:
    import importlib
    bu = importlib.import_module('bengali_utils')
    replace_short_desc = bu.replace_short_desc
    to_bengali_digits = bu.to_bengali_digits
    bengali_sort_key = bu.bengali_sort_key
    fix_initial_khandatta = bu.fix_initial_khandatta
    fix_r_reigned = bu.fix_r_reigned
    normalize_nukta_chars = bu.normalize_nukta_chars
    has_invalid_nukta = bu.has_invalid_nukta
    normalize_units = bu.normalize_units
    remove_maintenance_templates = bu.remove_maintenance_templates
    to_bengali_text = bu.to_bengali_text



def test_rule_1_no_short_description():
    """নিয়ম ১: {{Short description}} সম্পূর্ণরূপে পরিহার/অপসারণ।"""
    text = "{{Short description|A famous historic building}}\n{{short description|none}}\nএটি একটি নিবন্ধ।"
    cleaned = replace_short_desc(text)
    assert 'Short description' not in cleaned
    assert 'short description' not in cleaned
    assert 'এটি একটি নিবন্ধ।' in cleaned


def test_rule_2_bengali_digits():
    """নিয়ম ২: শতভাগ বাংলা সংখ্যা (০-৯)।"""
    raw = "সাল 2024, পৃষ্ঠা 142, মোট 1000 জন।"
    converted = to_bengali_digits(raw)
    assert converted == "সাল ২০২৪, পৃষ্ঠা ১৪২, মোট ১০০০ জন।"
    assert not any(ch in converted for ch in '0123456789')


def test_rule_3_bengali_alphabetical_sort():
    """নিয়ম ৩: বাংলা বর্ণানুক্রমিক তালিকা সাজানো (অ-হ)।"""
    names = ["রহিম", "অমর", "করিম", "জাহেদ", "বিকাশ"]
    sorted_names = sorted(names, key=bengali_sort_key)
    assert sorted_names == ["অমর", "করিম", "জাহেদ", "বিকাশ", "রহিম"]


def test_rule_4_no_initial_khandatta():
    """নিয়ম ৪: শব্দের শুরুতে 'ৎ' নিষিদ্ধ (ৎ -> স/সু)। শব্দের মাঝে বা শেষে ৎস বৈধ।"""
    assert fix_initial_khandatta("ৎসু") == "সু"
    assert fix_initial_khandatta("ৎসুনেসাবুরো") == "সুনেসাবুরো"
    assert fix_initial_khandatta("ৎসুনামি") == "সুনামি"
    assert fix_initial_khandatta("উৎসব ও মৎস্য") == "উৎসব ও মৎস্য"  # শব্দের মাঝে ৎ বা ৎস বৈধ


def test_rule_5_reign_r_conversion():
    """নিয়ম ৫: শাসনকালের 'r.' অনুবাদ (শাসনকাল: [সাল])।"""
    assert fix_r_reigned("সম্রাট আকবর (r. 1556–1605)") == "সম্রাট আকবর (শাসনকাল: ১৫৫৬–১৬০৫)"
    assert fix_r_reigned("r. 1202") == "শাসনকাল: ১২০২"


def test_rule_11_precomposed_nukta():
    """নিয়ম ১১: প্রি-কম্পোজড বাংলা বর্ণ (য়, ড়, ঢ়)।"""
    decomposed_ya = '\u09AF\u09BC'
    decomposed_da = '\u09A1\u09BC'
    decomposed_dha = '\u09A2\u09BC'

    assert has_invalid_nukta(f"হ{decomposed_ya}ল") is True
    fixed = normalize_nukta_chars(f"হ{decomposed_ya}ল এবং গা{decomposed_da} এবং আ{decomposed_dha}া")
    assert has_invalid_nukta(fixed) is False
    assert '\u09DF' in fixed
    assert '\u09DC' in fixed
    assert '\u09DD' in fixed


def test_rule_12_unit_superscripts_avoidance():
    """নিয়ম ১২: এককের সুপারস্ক্রিপ্ট ও প্রতীক (কিমি² পরিহার -> বর্গকিমি)।"""
    assert normalize_units("আয়তন ৫০ km²") == "আয়তন ৫০ বর্গকিমি"
    assert normalize_units("আয়তন ১০০ কিমি²") == "আয়তন ১০০ বর্গকিমি"
    assert normalize_units("১০ m²") == "১০ বর্গমি"


def test_rule_13_maintenance_templates_removal():
    """নিয়ম ১৩: ইংরেজি রক্ষণাবেক্ষণ ও উপভাষা টেমপ্লেট বর্জন।"""
    text = "{{Use British English}}\n{{Use dmy dates}}\n{{force cite load}}\nনিবন্ধের মূল অংশ।"
    cleaned = remove_maintenance_templates(text)
    assert 'Use British English' not in cleaned
    assert 'Use dmy dates' not in cleaned
    assert 'force cite load' not in cleaned
    assert 'নিবন্ধের মূল অংশ।' in cleaned


def test_full_pipeline_rules():
    """পূর্ণাঙ্গ বাংলা প্রমিতকরণ পাইপলাইন টেস্ট।"""
    decomp_da = '\u09A1\u09BC'
    sample = (
        "{{Short description|List of places}}\n"
        "{{Use British English}}\n"
        "The emperor (r. 1100-1120) ruled 450 km².\n"
        "দে" + decomp_da + "ল"
    )
    result = to_bengali_text(sample)
    assert 'Short description' not in result
    assert 'Use British English' not in result
    assert 'শাসনকাল: ১১০০-১১২০' in result
    assert 'বর্গকিমি' in result
    assert '৪৫০' in result
    assert not has_invalid_nukta(result)

