# -*- coding: utf-8 -*-
"""
জাপানি-বাংলা অনুবাদ মডিউল টেস্ট
(Japanese-Bengali Translation Module Test Suite)
"""
import sys
import os
import importlib
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
ja_dir = os.path.join(ROOT, 'জাপানি-বাংলা অনুবাদ')
if ja_dir not in sys.path:
    sys.path.insert(0, ja_dir)

import importlib.util

def _load(module_name):
    p = os.path.join(ja_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"ja_{module_name}", p)
    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    raise ImportError(f"Cannot load {p}")

ja_trans = _load('japanese_transliteration')
ja_num = _load('number_converter')
ja_tt = _load('table_translator')


def test_japanese_transliteration_names():
    """জাপানি ব্যক্তিনাম প্রতিবর্ণীকরণ টেস্ট।"""
    assert ja_trans.get_bengali_japanese_name("Kishida") == "কিশিদা"
    assert ja_trans.get_bengali_japanese_name("Fumio") == "ফুমিও"
    assert ja_trans.get_bengali_japanese_name("Tokyo") == "তোকিয়ো"


def test_japanese_rule_4_tsunesaburo():
    """নিয়ম ৪: শব্দের শুরুতে কখনোই 'ৎ' বসবে না (Tsunesaburo -> সুনেসাবুরো)।"""
    res = ja_trans.get_bengali_japanese_name("Tsunesaburo")
    assert res == "সুনেসাবুরো"
    assert not res.startswith("ৎ")


def test_japanese_table_translator():
    """জাপানি সারণি অনুবাদ টেস্ট।"""
    table = """{| class="wikitable"
! Name !! Office !! Term
|-
| [[Fumio Kishida]] || Prime Minister || 2021-2024
|}"""
    translated = ja_tt.translate_wikitable(table)
    assert "! নাম" in translated
    assert "২০২১-২০২৪" in translated
    assert "কিশিদা" in translated or "ফুমিও" in translated
