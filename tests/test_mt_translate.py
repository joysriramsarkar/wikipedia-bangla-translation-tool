# -*- coding: utf-8 -*-
"""মেশিন অনুবাদ ব্লক প্রসেসিংয়ের টেস্ট (নেটওয়ার্ক ছাড়া, mock অনুবাদক)।"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cx_postprocess import mt_translate  # noqa: E402


def _with_mock(func):
    original = mt_translate._translate_raw_chunk
    mt_translate._translate_raw_chunk = lambda text, sl="en", tl="bn": "«" + text + "»"
    try:
        return func()
    finally:
        mt_translate._translate_raw_chunk = original


def test_self_closing_ref_does_not_swallow_following_sentence():
    src = 'A.<ref name="x"/> When he died the temple became a Zen temple.<ref name="y">Book</ref>'
    out = _with_mock(lambda: mt_translate.translate_wikitext_block(src))
    inside = out.split("«", 1)[1].split("»", 1)[0]
    assert "When he died" in inside


def test_file_caption_is_translated_and_name_kept():
    src = '[[File:A 2020.jpg|thumb|left|Caption 2020 with [[gold leaf]]]]'
    out = _with_mock(lambda: mt_translate.translate_wikitext_block(src))
    assert "File:A 2020.jpg" in out
    assert "|thumb|left|" in out
    assert "«Caption" in out
    assert "[[gold leaf]]" in out


def test_multiline_file_link_name_kept_and_caption_translated():
    src = (
        "[[File:Germany Name European Languages.png|thumb|350px|European languages - name derived from:\n"
        "{{legend|#5599ff|[[Proto-Germanic language|Proto-Germanic]] ''*þeudiskaz''}}\n"
        "{{legend|#7ecb60|[[Latin]] {{lang|la|Germania}}}}\n"
        "]]"
    )
    out = _with_mock(lambda: mt_translate.translate_wikitext_full(src))
    assert "File:Germany Name European Languages.png" in out
    assert "thumb|350px" in out
    assert "«European languages - name derived from:»" in out or "«European languages" in out
    assert "{{legend|#5599ff|[[Proto-Germanic language|Proto-Germanic]] ''*þeudiskaz''}}" in out
    assert "জার্মানি নাম" not in out


def test_gallery_file_name_kept_caption_translated():
    src = "<gallery>\nFile:A 2020.jpg|Caption 2020\n</gallery>"
    out = _with_mock(lambda: mt_translate.translate_wikitext_full(src))
    assert "File:A 2020.jpg" in out
    assert "«Caption" in out


def test_external_link_label_translated_url_kept():
    src = "* [https://example.com/2020 Official site of Kinkaku-ji]"
    out = _with_mock(lambda: mt_translate.translate_wikitext_block(src))
    assert "https://example.com/2020" in out
    assert "«Official site" in out


def test_about_and_nihongo_display_text_translated():
    about = _with_mock(lambda: mt_translate.translate_wikitext_block(
        "{{About|a Buddhist temple|other topics}}"))
    assert "{{About|«a Buddhist temple»|«other topics»}}" in about

    nihongo = _with_mock(lambda: mt_translate.translate_wikitext_block(
        "{{Nihongo|Kinkaku-ji|金閣寺||lit=Temple of the Golden Pavilion}}"))
    assert "{{Nihongo|«Kinkaku-ji»|金閣寺" in nihongo
    assert "lit=«Temple of the Golden Pavilion»" in nihongo


def test_nested_literally_template_name_is_kept():
    src = "{{Nihongo|Kinkaku-ji|金閣寺||{{literally|Temple of the Golden Pavilion}}}}"
    out = _with_mock(lambda: mt_translate.translate_wikitext_block(src))
    assert "{{literally|«Temple of the Golden Pavilion»}}" in out
    assert "{{আক্ষরিক" not in out
