# -*- coding: utf-8 -*-
"""
চীনা-বাংলা অনুবাদ মডিউল টেস্ট
(Chinese-Bengali Translation Module Test Suite)
"""
import sys
import os
import importlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
zh_dir = os.path.join(ROOT, 'চীনা-বাংলা অনুবাদ')
if zh_dir not in sys.path:
    sys.path.insert(0, zh_dir)

import importlib.util

def _load(module_name):
    p = os.path.join(zh_dir, f"{module_name}.py")
    spec = importlib.util.spec_from_file_location(f"zh_{module_name}", p)
    if spec and spec.loader:
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m
    raise ImportError(f"Cannot load {p}")

zh_trans = _load('transliteration')
zh_num = _load('number_converter')
zh_links = _load('links_dictionary')


def test_chinese_transliteration():
    """চীনা হানজি ও ফিনিন থেকে বাংলা প্রতিবর্ণীকরণ টেস্ট।"""
    assert zh_trans.hanzi_to_bn("北京") == "পেইচিং"
    assert zh_trans.hanzi_to_bn("上海") == "শাংহাই"


def test_chinese_number_converter():
    """চীনা মডিউলের সংখ্যা রূপান্তরক টেস্ট।"""
    assert zh_num.to_bengali_digits("110101") == "১১০১০১"
    assert zh_num.to_bengali_digits("2020") == "২০২০"


def test_chinese_links_dict():
    """চীনা লিংক ও বিভাগ ম্যাপিং টেস্ট।"""
    assert "Beijing" in zh_links.LINK_MAP
    assert "বেইজিং" in zh_links.LINK_MAP["Beijing"]
    assert "CLPRC|District" in zh_links.LINK_MAP
