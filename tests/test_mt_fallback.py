# -*- coding: utf-8 -*-
"""মেশিন অনুবাদ ফলব্যাকের পার্সার টেস্ট (নেটওয়ার্ক ছাড়া)।"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cx_postprocess.mt_translate import _parse_clients5_payload  # noqa: E402


def test_parse_clients5_flat_list():
    assert _parse_clients5_payload(['প্রথম বাক্য। ', 'দ্বিতীয় বাক্য।']) == 'প্রথম বাক্য। দ্বিতীয় বাক্য।'


def test_parse_clients5_nested_list():
    assert _parse_clients5_payload([['এক', 'x'], ['দুই', 'y']]) == 'একদুই'


def test_parse_clients5_invalid_payload():
    assert _parse_clients5_payload({'not': 'a list'}) == ''
    assert _parse_clients5_payload([]) == ''
