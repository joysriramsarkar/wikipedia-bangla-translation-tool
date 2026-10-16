# -*- coding: utf-8 -*-
"""
জাপানি-বাংলা অনুবাদ প্যাকেজ (Japanese to Bengali Translation Toolkit)
উইকিপিডিয়া ও অন্যান্য জাপানি নথিপত্রকে প্রমিত বাংলায় অনুবাদ করার জন্য সম্পূর্ণ টুলকিট।
উইকিপিডিয়া:বাংলা ভাষায় জাপানি শব্দের প্রতিবর্ণীকরণ (সাহায্য:আধ্বব/জাপানি) নির্দেশিকা অনুসারে গঠিত।
"""
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from japanese_transliteration import (
    transliterate_japanese_word,
    transliterate_japanese_name,
    get_bengali_japanese_name,
)
from links_dictionary import (
    JAPANESE_LINKS_MAP,
)
from number_converter import (
    to_bengali_digits,
)
from table_translator import (
    translate_table_headers,
    translate_table_content,
    translate_wikitable,
)
from translate_page import (
    translate_page,
)

__all__ = [
    'transliterate_japanese_word',
    'transliterate_japanese_name',
    'get_bengali_japanese_name',
    'JAPANESE_LINKS_MAP',
    'to_bengali_digits',
    'translate_table_headers',
    'translate_table_content',
    'translate_wikitable',
    'translate_page',
]
