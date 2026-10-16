# -*- coding: utf-8 -*-
"""
রুশ-বাংলা অনুবাদ মডিউল টেস্ট
(Russian-Bengali Translation Module Test Suite)
"""
import sys
import os
import importlib
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
ru_dir = os.path.join(ROOT, 'রুশ-বাংলা অনুবাদ')
if ru_dir not in sys.path:
    sys.path.insert(0, ru_dir)

import importlib.util

def _load(module_name):
    p = os.path.join(ru_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"ru_{module_name}", p)
    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    raise ImportError(f"Cannot load {p}")

ru_trans = _load('cyrillic_transliteration')
ru_fed = _load('federal_subjects')
ru_tt = _load('table_translator')


def test_russian_cyrillic_transliteration():
    """রুশ সিরিলিক প্রতিবর্ণীকরণ টেস্ট।"""
    assert ru_trans.cyrillic_to_bengali("Путин") == "পুতিন"
    assert ru_trans.transliterate_cyrillic("Ленин") == "লেনিন" or "লিনিন" in ru_trans.transliterate_cyrillic("Ленин")


def test_russian_federal_subjects():
    """রুশ যুক্তরাষ্ট্রীয় বিষয় ম্যাপিং টেস্ট।"""
    assert "[[Republic of Adygea]]" in ru_fed.FEDERAL_SUBJECTS_MAP
    assert "আদিগেয়া প্রজাতন্ত্র" in ru_fed.FEDERAL_SUBJECTS_MAP["[[Republic of Adygea]]"]


def test_russian_table_translator():
    """রুশ জেলা সারণি অনুবাদ টেস্ট।"""
    table = """{| class="wikitable sortable"
! District !! Russian name !! [[Administrative center]]
|-
| [[Giaginsky District]] || {{lang|ru|Гиагинский район}} || Giaginskaya
|}"""
    translated = ru_tt.translate_wikitable(table)
    assert "! জেলা !! রুশ নাম !! [[প্রশাসনিক কেন্দ্র]]" in translated
    assert "জেলা" in translated
