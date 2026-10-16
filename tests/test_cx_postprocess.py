# -*- coding: utf-8 -*-
"""স্ক্রিনশট কেস (Central-West Region, Brazil) দিয়ে প্রোটোটাইপ যাচাই।"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cx_postprocess.bn_digits_safe import to_bengali_digits_safe
from cx_postprocess.infobox_map import translate_infobox


def test_ordinals():
    assert to_bengali_digits_safe("2nd") == "২য়"
    assert to_bengali_digits_safe("5th") == "৫ম"
    assert to_bengali_digits_safe("4th") == "৪র্থ"


def test_currency_and_year():
    assert to_bengali_digits_safe("R$ 932.166 billion") == "R$ ৯৩২.১৬৬ billion"
    assert to_bengali_digits_safe("(US$ 172.917 billion)") == "(US$ ১৭২.৯১৭ billion)"
    assert to_bengali_digits_safe("2007") == "২০০৭"


def test_bracket_bengali_digits():
    # পুরনো বাগ: বন্ধনীতে ল্যাটিন থাকলে সংখ্যা বাদ যেত। এখানে বদলাতে হবে।
    assert to_bengali_digits_safe("BRT (ইউটিসি-03)") == "BRT (ইউটিসি-০৩)"


def test_html_attrs_protected():
    html = '<a href="https://example.com/2007/x">2007</a>'
    out = to_bengali_digits_safe(html)
    assert 'href="https://example.com/2007/x"' in out  # URL অক্ষত
    assert ">২০০৭<" in out  # দৃশ্যমান অংশ বাংলা


def test_infobox_settlement():
    src = (
        "{{Infobox settlement\n"
        "| name = Central-West Region\n"
        "| subdivision_type = Country\n"
        "| subdivision_name = Brazil\n"
        "| population_total = 16504003\n"
        "| timezone = BRT\n"
        "| utc_offset = -03\n"
        "| custom_param = 2007\n"
        "}}\n"
    )
    out, unknown = translate_infobox(src)
    assert "{{তথ্যছক বসতি" in out
    assert "উপবিভাগের_ধরন" in out
    assert "দেশ" in out  # Country → দেশ
    assert "১৬৫০৪০০৩" in out  # জনসংখ্যার সংখ্যা বাংলা
    assert "custom_param" in out  # অচেনা প্যারাম ফেলা হয়নি
    assert "custom_param" in unknown  # কিন্তু রিপোর্ট হয়েছে


def test_infobox_building():
    src = (
        "{{infobox building\n"
        "| name = JLOS Towers\n"
        "| building_type = Government Offices\n"
        "| floor_count = 11\n"
        "| cost = 256\n"
        "}}\n"
    )
    out, unknown = translate_infobox(src)
    assert "{{তথ্যছক ভবন" in out
    assert "তলার_সংখ্যা = ১১" in out
    assert "নির্মাণব্যয় = ২৫৬" in out
    assert "তথ্যবক্ত" not in out
    assert "infobox" not in out


def test_totthobokto_eradication():
    # গুগল ট্রান্সলেট বা অন্য কোনো সোর্স থেকে যদি ভুলবশত 'তথ্যবক্ত ভবন' বা 'তথ্যবক্স' আসে
    src = (
        "{{তথ্যবক্ত ভবন\n"
        "| name = জেএলওএস টাওয়ার\n"
        "| floor_count = 11\n"
        "}}\n"
    )
    out, unknown = translate_infobox(src)
    assert "{{তথ্যছক ভবন" in out
    assert "তথ্যবক্ত" not in out
    assert "১১" in out


def test_template_parameter_digits_preserved():
    src = (
        "{{Navbox\n"
        "|name = Joseph Stalin\n"
        "|state = {{{state|<includeonly>{{{1|collapsed}}}</includeonly>}}}\n"
        "|group1 = History<br/>and politics\n"
        "|list1 = 1922\n"
        "|group10 = Residences\n"
        "|list10 = 2007\n"
        "|subdivision_type1 = District 5\n"
        "}}\n"
    )
    out = to_bengali_digits_safe(src)
    # প্যারামিটার কী ও ভ্যারিয়েবলে ল্যাটিন ডিজিট বহাল থাকবে
    assert "|group1 =" in out
    assert "|list1 =" in out
    assert "|group10 =" in out
    assert "|list10 =" in out
    assert "|subdivision_type1 =" in out
    assert "{{{1|collapsed}}}" in out
    # মানগুলোর সংখ্যা বাংলায় হবে
    assert "১৯২২" in out
    assert "২০০৭" in out
    assert "৫" in out


def test_fix_template_parameter_digits_repair():
    from cx_postprocess.bn_digits_safe import fix_template_parameter_digits
    mangled = (
        "|group১ = ইতিহাস\n"
        "|list১ = ওভারভিউ\n"
        "|group১০ = বাসস্থান\n"
        "|১ = মান\n"
        "{{{১|collapsed}}}\n"
        "{{{২}}}\n"
    )
    repaired = fix_template_parameter_digits(mangled)
    assert "|group1 = ইতিহাস" in repaired
    assert "|list1 = ওভারভিউ" in repaired
    assert "|group10 = বাসস্থান" in repaired
    assert "|1 = মান" in repaired
    assert "{{{1|collapsed}}}" in repaired
    assert "{{{2}}}" in repaired

