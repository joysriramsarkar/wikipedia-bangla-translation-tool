# -*- coding: utf-8 -*-
"""
জার্মান-বাংলা অনুবাদ মডিউল টেস্ট
(German-Bengali Translation Module Test Suite)
"""
import sys
import os
import importlib
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
de_dir = os.path.join(ROOT, 'জার্মান-বাংলা অনুবাদ')
if de_dir not in sys.path:
    sys.path.insert(0, de_dir)

import importlib.util

def _load(module_name):
    p = os.path.join(de_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"de_{module_name}", p)
    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    raise ImportError(f"Cannot load {p}")

de_trans = _load('german_transliteration')
de_tt = _load('table_translator')


def test_german_transliteration_names():
    """জার্মান ব্যক্তিনাম প্রতিবর্ণীকরণ টেস্ট।"""
    assert de_trans.transliterate_person_name("Bettina") == "বেটিনা"
    assert de_trans.transliterate_person_name("Schmidt") == "শ্মিট"
    assert de_trans.transliterate_person_name("Wolfgang") == "ভলফগাং"


def test_german_rule_4_zimmermann():
    """নিয়ম ৪: জার্মান 'Z' দিয়ে শুরু শব্দ সর্বদা 'স' হবে (Zimmermann -> সিমারমান)।"""
    res = de_trans.transliterate_person_name("Zimmermann")
    assert res == "সিমারমান"
    assert not res.startswith("ৎ")


def test_german_film_table():
    """জার্মান চলচ্চিত্র সারণি অনুবাদ টেস্ট।"""
    table = """{| class="wikitable sortable"
! Title !! Director !! Cast !! Genre !! Notes
|-
| [[Barbara (2012 film)|Barbara]] || Christian Petzold || Nina Hoss || Drama || Entered into Berlinale
|}"""
    translated = de_tt.translate_film_table(table)
    assert "! শিরোনাম !! পরিচালক !! অভিনয়ে !! ধরন !! মন্তব্য" in translated
    assert "পেৎসোল্ড" in translated or "ক্রিশ্চিয়ান" in translated
    assert "বারবারা" in translated or "ড্রামা" in translated or "নাট্য" in translated
