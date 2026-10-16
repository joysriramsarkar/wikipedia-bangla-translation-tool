# -*- coding: utf-8 -*-
"""
রুশ-বাংলা অনুবাদ প্যাকেজ (Russian to Bengali Translation Toolkit)
উইকিপিডিয়া ও অন্যান্য রুশ নথিপত্রকে প্রমিত বাংলায় অনুবাদ করার জন্য সম্পূর্ণ টুলকিট।
উইকিপিডিয়া:বাংলা ভাষায় রুশ শব্দের প্রতিবর্ণীকরণ নির্দেশিকা অনুসারে গঠিত।
"""
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from cyrillic_transliteration import (
    cyrillic_to_bengali,
    romanized_russian_to_bengali,
    get_bengali_district_name,
)
from federal_subjects import (
    FEDERAL_SUBJECTS_MAP,
    translate_admin_center,
    translate_municipal_note,
)
from number_converter import (
    format_bengali_number,
    to_bengali_digits,
)
from table_translator import (
    translate_table_header,
    translate_table_row,
    translate_wikitable,
)
from translate_page import (
    translate_page,
)

__all__ = [
    'cyrillic_to_bengali',
    'romanized_russian_to_bengali',
    'get_bengali_district_name',
    'FEDERAL_SUBJECTS_MAP',
    'translate_admin_center',
    'translate_municipal_note',
    'format_bengali_number',
    'to_bengali_digits',
    'translate_table_header',
    'translate_table_row',
    'translate_wikitable',
    'translate_page',
]
