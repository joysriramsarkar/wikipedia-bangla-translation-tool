# -*- coding: utf-8 -*-
"""ধাপ-২ যাচাই: billion/million, একক, তারিখ, টেমপ্লেট + ফুল পাইপলাইন।"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cx_postprocess.units_dates import fix_units_dates
from cx_postprocess.template_fix import fix_templates
from cx_postprocess.pipeline import fix_text


def test_large_numbers():
    assert "বিলিয়ন" in fix_units_dates("932.166 billion")
    assert "বিলিয়ন" in fix_units_dates("172.917 billions")


def test_units():
    assert fix_units_dates("10/km2") == "10/বর্গকিমি"
    assert "বর্গমাইল" in fix_units_dates("6,234.5 sq mi")


def test_american_date_reorder():
    assert fix_units_dates("October 16, 2026") == "16 অক্টোবর 2026"


def test_template_headings():
    out = fix_templates("== References ==\n{{Reflist}}")
    assert "== তথ্যসূত্র ==" in out
    assert "{{সূত্র তালিকা}}" in out


def test_full_pipeline_screenshot_sentence():
    src = "GDP R$ 932.166 billion (US$ 172.917 billion), 2007. October 16, 2026."
    out = fix_text(src)["fixed"]
    assert "৯৩২.১৬৬" in out and "বিলিয়ন" in out
    assert "১৭২.৯১৭" in out
    assert "২০০৭" in out
    assert "১৬ অক্টোবর ২০২৬" in out


def test_english_maintenance_templates_removal():
    src = (
        "{{Short description|none}}\n"
        "{{Use British English|date=March 2021}}\n"
        "{{Use Indian English}}\n"
        "{{Use British/india English}}\n"
        "{{Use dmy dates|date=July 2020}}\n"
        "{{Use mdy dates}}\n"
        "{{Template:Use American English}}\n"
        "{{টেমপ্লেট:Use British English}}\n"
        "{{EngvarB}}\n"
        "নিবন্ধের মূল টেক্সট।"
    )
    out = fix_templates(src).strip()
    assert "Use British" not in out
    assert "Use Indian" not in out
    assert "Use dmy" not in out
    assert "Short description" not in out
    assert "Engvar" not in out
    assert out == "নিবন্ধের মূল টেক্সট।"
