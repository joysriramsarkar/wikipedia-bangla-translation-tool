# -*- coding: utf-8 -*-
"""সার্ভার এন্ডপয়েন্ট ও প্রিভিউ টেস্ট"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cx_postprocess.server import load_drafts, save_drafts, DRAFTS_FILE, validate_wikitext


def test_drafts_load_and_save():
    # খসড়া সংরক্ষণ ও লোড পরীক্ষা
    original = load_drafts()
    try:
        sample = [{"title": "খসড়া:পরীক্ষা নিবন্ধ", "main_title": "পরীক্ষা নিবন্ধ", "created_at": "2026-10-16T12:00:00Z"}]
        save_drafts(sample)
        loaded = load_drafts()
        assert len(loaded) >= 1
        assert loaded[0]["title"] == "খসড়া:পরীক্ষা নিবন্ধ"
    finally:
        save_drafts(original)


def test_validate_wikitext_helper():
    report = validate_wikitext('সাল 2020 এবং https://x.com/2020')
    assert report['valid'] is False
    assert report['rules']['২']['ok'] is False
    assert 'rules' in report and 'checked_rules' in report
