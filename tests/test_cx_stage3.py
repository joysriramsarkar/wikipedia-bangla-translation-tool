# -*- coding: utf-8 -*-
"""ধাপ-৩ যাচাই: মুদ্রা, টেবিল-অ্যাট্রিবিউট, templatestyles, ref-name, cxserver চুক্তি।"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cx_postprocess.currency_fix import fix_currency
from cx_postprocess.table_fix import fix_table_block
from cx_postprocess.template_fix import clean_templatestyles_remnants
from cx_postprocess.bn_digits_safe import to_bengali_digits_safe
from cx_postprocess.pipeline import fix_text


def test_currency_symbols_kept_names_translated():
    # চিহ্ন থাকে, সংখ্যা পরে বাংলায় হয়; নাম বাংলায় হয়
    assert fix_currency("R$ 932.166 billion") == "R$ 932.166 billion"
    assert fix_currency("100 dollars") == "100 ডলার"
    assert fix_currency("USD 100") == "মার্কিন ডলার 100"
    out = fix_text("GDP R$ 932.166 billion (US$ 172.917 billion)")["fixed"]
    assert "R$ ৯৩২.১৬৬ বিলিয়ন" in out
    assert "US$ ১৭২.৯১৭ বিলিয়ন" in out


def test_table_attrs_protected_structure_fixed():
    src = '{| class="wikitable"\n|+ Title| cell|-'
    out = fix_table_block(src)
    assert 'rowspan' not in out or 'rowspan="২"' not in out
    # `|-` পৃথক লাইনে
    assert "\n|-\n" in out


def test_table_rowspan_colspan_latin():
    src = '{| \n| rowspan="2" | 2007 || 5th |\n|}'
    out = fix_table_block(src)
    assert 'rowspan="2"' in out  # অ্যাট্রিবিউট ল্যাটিন
    assert "২০০৭" in out and "৫ম" in out  # ঘরের মান বাংলা


def test_templatestyles_valid_kept_broken_removed():
    valid = '<templatestyles src="Infobox settlement/styles.css"/>'
    assert valid in clean_templatestyles_remnants(valid + "\nhello")
    assert clean_templatestyles_remnants("</> templatestyles\nhello") == "hello"
    assert clean_templatestyles_remnants("templatestyles\nhello") == "hello"


def test_ref_name_protected_content_converted():
    src = '<ref name="pop2007">population 16504003</ref>'
    out = to_bengali_digits_safe(src)
    assert 'name="pop2007"' in out  # অ্যাঙ্কর অক্ষত
    assert "১৬৫০৪০০৩" in out  # ভেতরের সংখ্যা বাংলা
