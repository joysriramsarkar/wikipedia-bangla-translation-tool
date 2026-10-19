# -*- coding: utf-8 -*-
"""
সুরক্ষিত সংখ্যা রূপান্তর ও বিস্তৃত নীতিমালা যাচাইয়ের টেস্ট
(Safe digit conversion + expanded rule validator tests)

মূল প্রতিরক্ষা: নিবন্ধের দৃশ্যমান অঙ্ক বাংলা হবে, কিন্তু URL, ফাইলনাম,
টেমপ্লেট প্যারামিটার, coord, ISBN — অক্ষত থাকবে।
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from common.bengali_utils import (  # noqa: E402
    fix_template_parameter_digits,
    strip_technical_spans,
    to_bengali_digits_safe,
    to_bengali_text,
)
from common.wikitext_utils import analyze_wikitable  # noqa: E402
from wikipedia_translation_toolkit import WikipediaTranslator  # noqa: E402


def _load_english(module_name):
    folder = os.path.join(ROOT, 'ইংরেজি-বাংলা অনুবাদ')
    path = os.path.join(folder, f'{module_name}.py')
    spec = importlib.util.spec_from_file_location(f'en_{module_name}', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Sate digit conversion
# ---------------------------------------------------------------------------

def test_url_digits_are_preserved():
    src = '{{cite web|url=https://example.com/2020/05|title=Report 2020}}'
    out = to_bengali_digits_safe(src)
    assert 'https://example.com/2020/05' in out
    assert 'Report ২০২০' in out


def test_url_inside_template_stops_at_pipe():
    # URL যেন টেমপ্লেটের পরের প্যারামিটার গিলে না ফেলে
    src = '{{cite web|url=https://y.com/1999|title=1999}}'
    out = to_bengali_digits_safe(src)
    assert 'url=https://y.com/1999' in out
    assert 'title=১৯৯৯' in out


def test_file_name_preserved_but_caption_converted():
    src = '[[File:Photo 2020.jpg|thumb|200px|ক্যাপশন 2020]]'
    out = to_bengali_digits_safe(src)
    assert 'Photo 2020.jpg' in out          # ফাইলের নাম অক্ষত
    assert '200px' in out                   # মাপ অক্ষত
    assert 'ক্যাপশন ২০২০' in out            # ক্যাপশন বাংলা


def test_identifiers_and_coordinates_preserved():
    text = 'ISBN 978-3-16-148410-0; {{coord|23|45|N|90|22|E}}; DOI 10.1000/xyz123'
    out = to_bengali_digits_safe(text)
    assert '978-3-16-148410-0' in out
    assert '{{coord|23|45|N|90|22|E}}' in out
    assert '10.1000/xyz123' in out


def test_template_keys_and_ref_names_preserved():
    src = '{{Navbox|group1 = ইতিহাস|list10 = 2007}}\n<ref name="a2020">Book 2020</ref>'
    out = to_bengali_digits_safe(src)
    assert '|group1 =' in out
    assert '|list10 =' in out
    assert 'name="a2020"' in out
    assert 'Book ২০২০' in out


def test_ordinals_converted():
    assert to_bengali_digits_safe('2nd') == '২য়'
    assert to_bengali_digits_safe('4th') == '৪র্থ'
    assert to_bengali_digits_safe('6th') == '৬ষ্ঠ'


def test_html_entities_preserved():
    assert to_bengali_digits_safe('a&#160;b') == 'a&#160;b'


def test_hyphenated_template_keys_preserved():
    src = '{{cite|editor-last2=Kindaichi|date=2024}}'
    out = to_bengali_digits_safe(src)
    assert 'editor-last2=Kindaichi' in out
    assert 'date=২০২৪' in out
    repaired = fix_template_parameter_digits('|editor-last২ = Kindaichi')
    assert repaired == '|editor-last2 = Kindaichi'


def test_date_templates_and_anchors_keep_ascii_digits():
    src = '{{Start date|2020|4|13}} #Season 17 (2020)'
    out = to_bengali_digits_safe(src)
    assert '{{Start date|2020|4|13}}' in out
    assert '#Season 17 (2020)' in out


def test_ordered_list_with_digits_converted():
    src = '# 1999 সালের ঘটনা\n# 2020 সালে মুক্তিপ্রাপ্ত'
    out = to_bengali_digits_safe(src)
    assert '# ১৯৯৯ সালের ঘটনা' in out
    assert '# ২০২০ সালে মুক্তিপ্রাপ্ত' in out


def test_to_bengali_text_keeps_technical_spans():
    src = '[[File:Photo 2020.jpg|thumb|ছবি 2020]] ওয়েবসাইট https://x.com/2020 এবং সাল 2020'
    out = to_bengali_text(src)
    assert 'Photo 2020.jpg' in out
    assert 'https://x.com/2020' in out
    assert 'সাল ২০২০' in out


def test_normalize_units_does_not_touch_urls():
    out = to_bengali_text('দেখুন https://example.com/map/km2 এবং 50 km²')
    assert 'https://example.com/map/km2' in out
    assert '৫০ বর্গকিমি' in out


def test_strip_technical_spans_hides_machine_digits():
    visible = strip_technical_spans(
        '[[File:Photo 2020.jpg|thumb]] https://x.com/2020 দাম 500'
    )
    assert '2020' not in visible
    assert '500' in visible


# ---------------------------------------------------------------------------
# Table structure (Rule 6)
# ---------------------------------------------------------------------------

def test_analyze_wikitable_balanced_table_has_no_issues():
    table = (
        '{| class="wikitable"\n'
        '! ক !! খ !! গ\n'
        '|-\n'
        '| ১ || ২ || ৩\n'
        '|}'
    )
    report = analyze_wikitable(table)
    assert report['header_cols'] == 3
    assert report['rows'] == 1
    assert report['issues'] == []


def test_analyze_wikitable_reports_missing_cells_and_empty_cell():
    table = (
        '{| class="wikitable"\n'
        '! ক !! খ !! গ\n'
        '|-\n'
        '| ১ || ২ || ৩\n'
        '|-\n'
        '| ১ || ২ ||\n'
        '|-\n'
        '| ১ || ২\n'
        '|}'
    )
    issues = analyze_wikitable(table)['issues']
    kinds = {issue['type'] for issue in issues}
    assert 'empty_cell' in kinds
    assert 'column_count' in kinds


def test_analyze_wikitable_skips_colspan_rows():
    table = (
        '{| class="wikitable"\n'
        '! ক !! খ !! গ\n'
        '|-\n'
        '| colspan="3" | একসাথে\n'
        '|}'
    )
    assert analyze_wikitable(table)['issues'] == []


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------

def test_validator_accepts_clean_bengali_text():
    text = '== ইতিহাস ==\nতিনি ২০২০ সালে ২৫০ বর্গকিমি অঞ্চলে শাসন করেন।'
    report = WikipediaTranslator().validate_rules(text)
    assert report['valid'] is True
    assert report['issue_count'] == 0
    assert report['checked_rules'] == ['১', '২', '৪', '৫', '৬', '৮', '১১', '১২', '১৩']


def test_validator_ignores_digits_inside_urls_and_files():
    text = 'ছবি [[File:Photo 2020.jpg|thumb]] ও https://x.com/2020 দেখুন।'
    report = WikipediaTranslator().validate_rules(text)
    assert report['rules']['২']['ok'] is True


def test_validator_detects_latin_digits_only_in_visible_text():
    report = WikipediaTranslator().validate_rules('সাল 2020')
    assert report['rules']['২']['ok'] is False
    assert '2020' not in report['issues'][0]  # বার্তায় বাংলা অঙ্ক


def test_validator_detects_table_and_category_problems():
    text = (
        '[[Category:Films]]\n'
        '{| class="wikitable"\n'
        '! ক !! খ\n'
        '|-\n'
        '| ১\n'
        '|}'
    )
    report = WikipediaTranslator().validate_rules(text)
    assert report['rules']['৬']['ok'] is False
    assert report['rules']['৮']['ok'] is False
    assert report['unchecked_rules'] == ['৩', '৭', '৯', '১০']


# ---------------------------------------------------------------------------
# English module integration
# ---------------------------------------------------------------------------

def test_english_module_keeps_file_and_url_intact():
    module = _load_english('translate_page')
    src = (
        '{{Short description|x}}\n'
        'Pic [[File:Photo 2020.jpg|thumb|2020]]\n'
        'Source https://example.com/2020 and year 2020.\n'
    )
    out = module.translate_text(src)
    assert 'Photo 2020.jpg' in out
    assert 'https://example.com/2020' in out
    assert 'year ২০২০' in out
