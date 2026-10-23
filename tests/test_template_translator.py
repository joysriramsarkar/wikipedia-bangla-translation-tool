# -*- coding: utf-8 -*-
"""
টেমপ্লেট অনুবাদক টেস্ট (Unit tests for Template Translator)
"""
import pytest
from cx_postprocess.template_translator import is_template_wikitext, translate_template_wikitext
from cx_postprocess.mt_translate import translate_wikitext_full
from app import app


def test_is_template_wikitext_detection():
    # টাইটেল দিয়ে শনাক্তকরণ
    assert is_template_wikitext("", title="Template:English football updater") is True
    assert is_template_wikitext("", title="টেমপ্লেট:প্রিমিয়ার লিগ") is True
    assert is_template_wikitext("", title="Module:Navbox") is True

    # উইকিটেক্সট সিনট্যাক্স দিয়ে শনাক্তকরণ
    assert is_template_wikitext("{{#switch: {{{1}}}\n| a = b\n}}") is True
    assert is_template_wikitext("<includeonly>{{#if: {{{name|}}} | ... }}</includeonly>") is True
    assert is_template_wikitext("{{Navbox\n| name = Premier League\n| title = ...\n}}") is True

    # সাধারণ নিবন্ধ টেমপ্লেট হিসেবে ভুল শনাক্ত হবে না
    article_text = (
        "'''লিওন লোবিয়োর''' (জন্ম: ১ জানুয়ারি ১৯৪৫) একজন বিশিষ্ট ব্যক্তি।\n"
        "== ইতিহাস ==\n"
        "তিনি ১৯৪৫ সালে জন্মগ্রহণ করেন।"
    )
    assert is_template_wikitext(article_text, title="লিওন লোবিয়োর") is False


def test_translate_switch_template():
    src = (
        "{{#switch: {{{1}}}\n"
        "<!--Premier League-->\n"
        "| AFCBourn = {{ENGLs|PL}} | AFCBourn2 = [[2025–26 Premier League|2025–26]] | AFCBourn3 = {{ENGLs|PL}}, 6th of 20\n"
        "| Arsenal  = {{ENGLs|PL}} | Arsenal2  = [[2025–26 Premier League|2025–26]] | Arsenal3  = {{ENGLs|PL}}, 1st of 20\n"
        "| CoventrC = {{ENGLs|PL}} | CoventrC2 = [[2025–26 EFL Championship|2025–26]] | CoventrC3 = {{ENGLs|EFLC}}, 1st of 24 (promoted)\n"
        "| WolverhU = {{ENGLs|WMRL2}} | WolverhU2 = [[2018–19 {{ENGLs|WMRL}}|2018–19]] | WolverhU3 = {{ENGLs|WMRL2}}, 10th of 11 (resigned)\n"
        "| default = 0}}\n"
        "<noinclude>\n"
        "{{documentation}}\n"
        "[[Category:English football updater templates]]\n"
        "</noinclude>"
    )

    out = translate_template_wikitext(src)

    # ১. পার্সার ফাংশন ও ভ্যারিয়েবল ১০০% সুরক্ষিত
    assert "{{#switch: {{{1}}}" in out
    assert "{{#সুইচ:" not in out
    assert "{টেমপ্লেট:১}" not in out

    # ২. কী (keys) অক্ষত (ASCII) যাতে কলিং না ভাঙে
    assert "AFCBourn2 =" in out
    assert "AFCBourn3 =" in out
    assert "Arsenal2 =" in out
    assert "CoventrC3 =" in out
    assert "WolverhU2 =" in out
    assert "AFCBourn২" not in out
    assert "Arsenal২" not in out

    # ৩. সাব-টেমপ্লেট আর্গুমেন্ট অক্ষত
    assert "{{ENGLs|WMRL2}}" in out
    assert "{{ENGLs|WMRL২}}" not in out

    # ৪. উইকিলিংক ও লিগের নাম প্রমিত বাংলায় রূপান্তর
    assert ("[[বিষয়শ্রেণী:" in out) or ("[[বিষয়শ্রেণী:" in out)
    assert "[[২০২৫–২৬ ইএফএল চ্যাম্পিয়নশিপ|২০২৫–২৬]]" in out

    # ৫. র‍্যাংক ও টীকা প্রমিত বাংলায় রূপান্তর
    assert "২০-এর মধ্যে ৬ষ্ঠ" in out
    assert "২০-এর মধ্যে ১ম" in out
    assert "২৪-এর মধ্যে ১ম (উন্নীত)" in out
    assert "১১-এর মধ্যে ১০ম (পদত্যাগ)" in out

    # ৬. ডকুমেন্টেশন ও বিষয়শ্রেণী বাংলায় রূপান্তর
    assert "{{ডকুমেন্টেশন}}" in out
    assert ("[[বিষয়শ্রেণী:" in out) or ("[[বিষয়শ্রেণী:" in out)


def test_translate_wikitext_full_routes_templates():
    src = (
        "{{#switch: {{{1}}}\n"
        "| Chelsea = {{ENGLs|PL}} | Chelsea2 = [[2025–26 Premier League|2025–26]] | Chelsea3 = {{ENGLs|PL}}, 4th of 20\n"
        "}}"
    )
    # translate_wikitext_full-এ পাস করলে এটি স্বয়ংক্রিয়ভাবে টেমপ্লেট অনুবাদকে যাবে
    out = translate_wikitext_full(src, title="Template:English football updater")
    assert "{{#switch: {{{1}}}" in out
    assert "Chelsea2 =" in out
    assert "Chelsea২" not in out
    assert "২০-এর মধ্যে ৪র্থ" in out


def test_api_fix_handles_template():
    client = app.test_client()
    payload = {
        "text": (
            "{{#switch: {{{1}}}\n"
            "| Brentfor = {{ENGLs|PL}} | Brentfor2 = [[2025–26 Premier League|2025–26]] | Brentfor3 = {{ENGLs|PL}}, 9th of 20\n"
            "}}"
        ),
        "translate": True,
        "sl": "en",
        "tl": "bn",
        "title": "Template:English football updater"
    }
    resp = client.post("/fix", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    fixed = data.get("fixed", "")

    assert "{{#switch: {{{1}}}" in fixed
    assert "Brentfor2 =" in fixed
    assert "Brentfor২" not in fixed
    assert "২০-এর মধ্যে ৯ম" in fixed


def test_translate_navbox_template():
    src = (
        "{{Navbox\n"
        "| name = CP Football Championships\n"
        "| title = [[CP football]] major competitions\n"
        "| titlestyle = background:#BFD7FF\n"
        "| groupstyle = text-align:center;\n"
        "| basestyle = background:#D5E6FF;text-align:center\n"
        "| state = {{{state|autocollapse}}}\n"
        "| group1 = [[Football 7-a-side at the Summer Paralympics|Summer Paralympics]]\n"
        "| list1 = \n"
        "* [[Football 7-a-side at the 1984 Summer Paralympics|New York 1984]]\n"
        "* [[Football 7-a-side at the 1988 Summer Paralympics|Seoul 1988]]\n"
        "| group2 = World championships\n"
        "| list2 = \n"
        "  {{Navbox|subgroup\n"
        "  | groupstyle = background:#D5E6FF;text-align:center\n"
        "  | group1 = CP Games / World Games\n"
        "  | list1 = \n"
        "* [[1978 CP World Championship|Edinburgh 1978]]\n"
        "  }}\n"
        "}}\n"
        "<noinclude>\n"
        "{{documentation}}\n"
        "[[Category:Disability football competitions| ]]\n"
        "</noinclude>"
    )
    out = translate_template_wikitext(src, title="Template:CP Football Championships")

    # ১. সিএসএস ও কারিগরি প্যারামিটার ১০০% সুরক্ষিত
    assert "background:#BFD7FF" in out
    assert "text-align:center" in out
    assert "background:#D5E6FF" in out
    assert "{{{state|autocollapse}}}" in out
    assert "name = CP Football Championships" in out
    assert "{{Navbox|subgroup" in out

    # ২. শিরোনাম, গ্রুপ ও তালিকা বাংলায় অনূদিত
    assert ("সিপি ফুটবল" in out) or ("প্রধান প্রতিযোগিতা" in out)
    assert "গ্রীষ্মকালীন প্যারালিম্পিক" in out
    assert ("নিউ ইয়র্ক" in out) or ("নিউ ইয়র্ক" in out)
    assert "সিউল" in out

    # ৩. দৃশ্যমান সাল বাংলা সংখ্যায়
    assert "১৯৮৪" in out
    assert "১৯৮৮" in out

    # ৪. ডকুমেন্টেশন ও বিষয়শ্রেণী বাংলায়
    assert "{{ডকুমেন্টেশন}}" in out
    assert ("[[বিষয়শ্রেণী:" in out) or ("[[বিষয়শ্রেণী:" in out)


def test_api_fix_handles_navbox_template():
    client = app.test_client()
    payload = {
        "text": (
            "{{Navbox\n"
            "| name = CP Football Championships\n"
            "| title = [[CP football]] major competitions\n"
            "| titlestyle = background:#BFD7FF\n"
            "| group1 = Summer Paralympics\n"
            "| list1 = \n"
            "* [[1984 Summer Paralympics|New York 1984]]\n"
            "}}"
        ),
        "translate": True,
        "sl": "en",
        "tl": "bn",
        "title": "Template:CP Football Championships"
    }
    resp = client.post("/fix", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    fixed = data.get("fixed", "")

    assert "background:#BFD7FF" in fixed
    assert "গ্রীষ্মকালীন প্যারালিম্পিক" in fixed
    assert "১৯৮৪" in fixed

