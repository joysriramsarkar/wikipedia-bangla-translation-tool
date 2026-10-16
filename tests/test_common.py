# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common import bengali_utils

def test_to_bengali_digits():
    assert bengali_utils.to_bengali_digits('2010') == '২০১০'
    assert bengali_utils.to_bengali_digits('1234567890') == '১২৩৪৫৬৭৮৯০'

def test_fix_r_reigned():
    assert bengali_utils.fix_r_reigned('r. 1202') == 'শাসনকাল: ১২০২'
    # Also check range without full digit conversion in replacement
    result = bengali_utils.fix_r_reigned('r. 1202-1203')
    assert 'শাসনকাল:' in result

def test_normalize_nukta():
    # Decomposed য+় should become য়
    result = bengali_utils.normalize_nukta_chars('\u09AF\u09BC')
    assert result == '\u09DF'

def test_replace_short_desc():
    text = '{{Short description|test}}'
    assert bengali_utils.replace_short_desc(text) == ''
