# -*- coding: utf-8 -*-
"""
ইংরেজি-বাংলা অনুবাদ মডিউল টেস্ট
(English-Bengali Translation Module Test Suite)
"""
import sys
import os
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
eng_dir = os.path.join(ROOT, 'ইংরেজি-বাংলা অনুবাদ')
if eng_dir not in sys.path:
    sys.path.insert(0, eng_dir)

import importlib.util

def _load(module_name):
    p = os.path.join(eng_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"en_{module_name}", p)
    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    raise ImportError(f"Cannot load {p}")

en_links = _load('links_dictionary')
en_nums = _load('number_converter')
en_tt = _load('table_translator')
en_tp = _load('translate_page')


def test_links_dictionary():
    """ইংরেজি পরিচিত নাম ও শিরোনাম অভিধান টেস্ট।"""
    assert "Abraham Lincoln" in en_links.PERSON_NAMES_MAP
    assert en_links.PERSON_NAMES_MAP["Abraham Lincoln"] == "আব্রাহাম লিংকন"
    assert "The Godfather" in en_links.FILM_TITLES_MAP
    assert en_links.FILM_TITLES_MAP["The Godfather"] == "দ্য গডফাদার"
    assert "1984" in en_links.BOOK_TITLES_MAP


def test_number_converter():
    """ইংরেজি সংখ্যা ও ক্রমবাচক সংখ্যা রূপান্তরক টেস্ট।"""
    assert en_nums.to_bengali_digits("2024") == "২০২৪"
    assert en_nums.convert_ordinals("1st place") == "১ম place"
    assert en_nums.convert_ordinals("2nd") == "২য়"
    assert en_nums.convert_ordinals("5th") == "৫ম"
    assert en_nums.convert_large_numbers("10 million") == "10 মিলিয়ন"


def test_table_translator():
    """ইংরেজি সারণি অনুবাদ ও কলাম সমতা টেস্ট (Rule 6)।"""
    sample_table = """{| class="wikitable"
! Title !! Director !! Year !! Notes
|-
| [[The Godfather]] || Francis Ford Coppola || 1972 || Classic film
|-
| [[Casablanca]] || Michael Curtiz || 1942 ||
|}"""
    translated = en_tt.translate_wikitable(sample_table)
    assert "! শিরোনাম !! পরিচালক !! সাল !! মন্তব্য" in translated
    assert "দ্য গডফাদার" in translated
    assert "১৯৭২" in translated
    assert "১৯৪২" in translated
    # খালি ঘরের জন্য &nbsp; নিশ্চিতকরণ (Rule 6)
    assert "&nbsp;" in translated


def test_translate_text():
    """ইংরেজি নিবন্ধ পাতা অনুবাদ ও বিধিমালা প্রয়োগ টেস্ট।"""
    article = """{{Short description|Biography of an artist}}
{{Use British English}}
== Early life ==
He was born in 1950 and ruled (r. 1980–1990) over 250 km².

== Filmography ==
{| class="wikitable"
! Title !! Year
|-
| [[The Dark Knight]] || 2008
|}

== References ==
{{reflist}}

[[Category:English actors]]"""
    translated = en_tp.translate_text(article)
    assert "{{Short description" not in translated
    assert "{{Use British English}}" not in translated
    assert "== প্রাথমিক জীবন ==" in translated
    assert "== চলচ্চিত্র তালিকা ==" in translated
    assert "== তথ্যসূত্র ==" in translated
    assert "শাসনকাল: ১৯৮০–১৯৯০" in translated
    assert "২৫০ বর্গকিমি" in translated
    assert "[[বিষয়শ্রেণী:English actors]]" in translated
    assert "২০০৮" in translated
