# -*- coding: utf-8 -*-
"""
চীনা-বাংলা অনুবাদ প্যাকেজ (Chinese to Bengali Translation Toolkit)
উইকিপিডিয়া ও অন্যান্য চীনা নথিপত্রকে প্রমিত বাংলায় অনুবাদ করার জন্য সম্পূর্ণ টুলকিট।
"""
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from pinyin_table import FULL_PINYIN_MAP, OFFICIAL_PINYIN_MAP
from transliteration import hanzi_to_bn, pinyin_to_bn, get_bengali_division_name
from links_dictionary import LINK_MAP
from number_converter import to_bengali_digits, translate_table_notes
from table_translator import translate_main_table, translate_dissolved_table, translate_renamed_table
from translate_page import translate_wikipedia_page, translate_wikipedia_text

__all__ = [
    'FULL_PINYIN_MAP',
    'OFFICIAL_PINYIN_MAP',
    'hanzi_to_bn',
    'pinyin_to_bn',
    'get_bengali_division_name',
    'LINK_MAP',
    'to_bengali_digits',
    'translate_table_notes',
    'translate_main_table',
    'translate_dissolved_table',
    'translate_renamed_table',
    'translate_wikipedia_page',
    'translate_wikipedia_text',
]
