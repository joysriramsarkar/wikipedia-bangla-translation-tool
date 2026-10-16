# -*- coding: utf-8 -*-
"""
স্ক্রিপ্টসমূহ টেস্ট
(Project Scripts Test Suite)
"""
import sys
import os
from pathlib import Path
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
scripts_dir = os.path.join(ROOT, 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

try:
    from scripts import fix_nukta, check_digits, sort_bengali, verify_table, stats
except ImportError:
    import importlib
    fix_nukta = importlib.import_module('fix_nukta')
    check_digits = importlib.import_module('check_digits')
    sort_bengali = importlib.import_module('sort_bengali')
    verify_table = importlib.import_module('verify_table')
    stats = importlib.import_module('stats')



def test_script_fix_nukta():
    """fix_nukta.py স্ক্রিপ্ট ফাংশন টেস্ট।"""
    decomposed = "পা\u09A1\u09BCাকা"
    fixed = fix_nukta.fix_nukta(decomposed)
    assert '\u09DC' in fixed
    assert fix_nukta.count_issues(decomposed) == 1
    assert fix_nukta.count_issues(fixed) == 0


def test_script_check_digits():
    """check_digits.py স্ক্রিপ্ট ফাংশন টেস্ট।"""
    converted = check_digits.to_bn_digits("2024")
    assert converted == "২০২৪"
    masked, tokens = check_digits.mask_protected("সাল 2024 <ref>note 1</ref>")
    assert "<ref>note 1</ref>" in tokens


def test_script_sort_bengali():
    """sort_bengali.py বর্ণানুক্রমিক সাজানো টেস্ট।"""
    rows = [
        "| রহিম || ছাত্র",
        "| অমর || শিক্ষক",
        "| করিম || প্রকৌশলী",
    ]
    sorted_rows = sort_bengali.sort_wikitext_rows(rows, col_index=0)
    assert "অমর" in sorted_rows[0]
    assert "করিম" in sorted_rows[1]
    assert "রহিম" in sorted_rows[2]


def test_script_stats():
    """stats.py পরিসংখ্যান টেস্ট।"""
    readme_path = Path(ROOT) / "README.md"
    if readme_path.exists():
        analysis = stats.analyze_file(readme_path)
        assert 'lines' in analysis
        assert analysis['lines'] > 0
        assert 'bn_digits' in analysis
