# -*- coding: utf-8 -*-
"""২০২৬-১০-২১ যাচাইয়ে ধরা পড়া ত্রুটিগুলোর রিগ্রেশন টেস্ট।

প্রতিটি টেস্ট একটি নির্দিষ্ট, ডকুমেন্টেড ব্যর্থতার সঙ্গে যুক্ত:

* সূত্র টেমপ্লেটের তারিখ বাংলা হয়ে CS1 ত্রুটি তৈরি করা
* URL-এর ভিতরের মাস/একক বদলে লিংক ভাঙা
* ফাইলের নামে মাস/অঙ্ক বদলে ছবি ভাঙা
* নিয়ম ৫ (`r. 1995`) পাইপলাইনে বাদ পড়া
* রুশ সারণিতে `|-` পরের ঘরের সঙ্গে জুড়ে যাওয়া
* চীনা মডিউল `table_translator` নাম-সংঘর্ষে ImportError
* `.env`-এর পুরোনো `key: "value"` ফরম্যাট পড়তে না পারা
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from cx_postprocess.pipeline import fix_text  # noqa: E402
from common import env_loader  # noqa: E402


def test_citation_dates_stay_ascii():
    src = ('তিনি মন্দির নির্মাণ করেন।<ref>{{cite web|url=http://x|date=24 May 2016'
           '|access-date=2010-07-15}}</ref>')
    out = fix_text(src)["fixed"]
    assert "date=24 May 2016" in out
    assert "access-date=2010-07-15" in out


def test_infobox_dates_become_bengali():
    out = fix_text("{{Infobox settlement|established_date = 1397}}")["fixed"]
    assert "১৩৯৭" in out


def test_url_with_month_and_unit_is_untouched():
    src = "See http://example.com/May/2016.html for details."
    out = fix_text(src)["fixed"]
    assert "http://example.com/May/2016.html" in out


def test_file_name_keeps_month_and_digits_but_caption_translates():
    src = "[[File:May 2016 photo 02.jpg|thumb|Photo taken in May 2016]]"
    out = fix_text(src)["fixed"]
    assert "File:May 2016 photo 02.jpg" in out
    assert "মে" in out.split("|")[-1]


def test_rule5_r_reigned_is_applied_by_pipeline():
    out = fix_text("He was king r. 1995-2005 and Mr. Smith stayed.")["fixed"]
    assert "শাসনকাল: ১৯৯৫" in out
    assert "Mr. Smith" in out


def test_mapframe_numeric_params_stay_ascii():
    src = "{{Infobox mapframe|zoom=14|frame-latitude=35.0375}}"
    out = fix_text(src)["fixed"]
    assert "zoom=14" in out
    assert "frame-latitude=35.0375" in out


def test_russian_table_row_keeps_leading_newline():
    path = os.path.join(ROOT, "রুশ-বাংলা অনুবাদ", "table_translator.py")
    if not os.path.exists(path):
        pytest.skip("রুশ মডিউল নেই")
    import importlib.util
    spec = importlib.util.spec_from_file_location("ru_table_under_test", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    row = "\n|[[Giaginsky District]]||{{lang|ru|Гиагинский район}}"
    out = mod.translate_table_row(row)
    assert out.startswith("\n|"), "সারির শুরুর নিউলাইন হারালে `|-` জোড়া লেগে সারণি ভাঙে"


def test_chinese_module_loads_without_name_clash():
    """চীনা `table_translator` যেন ইংরেজি মডিউলের ছায়ায় না পড়ে।"""
    import wikipedia_translation_toolkit as toolkit
    zh = toolkit._load_module("চীনা-বাংলা অনুবাদ", "table_translator")
    assert hasattr(zh, "translate_main_table")
    en = toolkit._load_module("ইংরেজি-বাংলা অনুবাদ", "table_translator")
    assert hasattr(en, "translate_wikitable")
    assert not hasattr(en, "translate_main_table")


def test_env_loader_accepts_both_formats(tmp_path):
    path = tmp_path / "sample.env"
    path.write_text(
        "# comment\nGEMINI_MODEL=gemini-3.8-flash\nold_style: \"quoted-value\"\n",
        encoding="utf-8",
    )
    values = env_loader._parse_file(str(path))
    assert values["GEMINI_MODEL"] == "gemini-3.8-flash"
    assert values["old_style"] == "quoted-value"


def test_validator_ignores_preserved_citation_dates():
    from wikipedia_translation_toolkit import WikipediaTranslator
    text = ("তিনি ১৩৯৭ সালে মঠটি প্রতিষ্ঠা করেন।"
            "<ref>{{cite web|url=http://x|date=2010-07-15|access-date=2011-01-02}}</ref>")
    report = WikipediaTranslator().validate_rules(text)
    rule_two = report["rules"].get("২")
    assert rule_two is not None
    assert rule_two["ok"], rule_two["issues"]


def test_translatable_script_detection():
    from cx_postprocess.mt_translate import has_translatable_content
    # রাশিয়ান (সিরিলিক)
    assert has_translatable_content("Собор", 2)
    # চীনা (হানজি)
    assert has_translatable_content("西湖", 2)
    # জাপানি (কাঞ্জি/কানা)
    assert has_translatable_content("鹿苑寺", 2)
    # জার্মান (লাতিন বর্ধিত)
    assert has_translatable_content("Kölner Dom", 2)
    # ইংরেজি
    assert has_translatable_content("Temple", 2)
    # বাংলা (উৎস লিপি নয়)
    assert not has_translatable_content("কলকাতা", 2)
    # শুধু সংখ্যা ও চিহ্ন
    assert not has_translatable_content("12345", 2)
    assert not has_translatable_content("|--|", 2)


def test_ai_output_safety_verification():
    from cx_postprocess.mt_translate import is_ai_output_structurally_safe
    src = "মন্দির<ref>বই ১</ref> ছিল এবং {{মূল}} পাতা [[লিংক]] ছিল।"

    # নিরাপদ আউটপুট
    safe_out = "মন্দির<ref>বই ১</ref> ছিল এবং {{মূল}} পাতা [[লিংক]] ছিল।"
    assert is_ai_output_structurally_safe(src, safe_out)

    # তথ্যসূত্র হারিয়ে গেলে ব্যর্থ হবে
    lost_ref = "মন্দির ছিল এবং {{মূল}} পাতা [[লিংক]] ছিল।"
    assert not is_ai_output_structurally_safe(src, lost_ref)

    # টেমপ্লেট হারিয়ে গেলে ব্যর্থ হবে
    lost_tpl = "মন্দির<ref>বই ১</ref> ছিল এবং পাতা [[লিংক]] ছিল।"
    assert not is_ai_output_structurally_safe(src, lost_tpl)

    # টেমপ্লেট বন্ধ না হলে ব্যর্থ হবে
    unbalanced_tpl = "মন্দির<ref>বই ১</ref> ছিল এবং {{মূল পাতা [[লিংক]] ছিল।"
    assert not is_ai_output_structurally_safe(src, unbalanced_tpl)

    # উইকিলিংক নষ্ট হলে ব্যর্থ হবে
    unbalanced_link = "মন্দির<ref>বই ১</ref> ছিল এবং {{মূল}} পাতা [[লিংক ছিল।"
    assert not is_ai_output_structurally_safe(src, unbalanced_link)


def test_multiline_ref_preservation():
    from cx_postprocess.mt_translate import translate_wikitext_full
    src = (
        "Early history.\n"
        "<ref name=\"multi\">\n"
        "{{cite web\n"
        "| url = http://example.com/item\n"
        "| title = Reference Title\n"
        "| date = 2020-05-10\n"
        "}}\n"
        "</ref>\n"
        "The temple was built in 1397."
    )
    # অনুবাদ মক
    original_chunk = None
    try:
        from cx_postprocess import mt_translate
        original_chunk = mt_translate._translate_raw_chunk
        mt_translate._translate_raw_chunk = lambda text, sl="en", tl="bn": text
        out = translate_wikitext_full(src, sl="en", tl="bn")
        assert '<ref name="multi">' in out
        assert "{{cite web" in out
        assert "url = http://example.com/item" in out
        assert "</ref>" in out
    finally:
        if original_chunk is not None:
            mt_translate._translate_raw_chunk = original_chunk


def test_interwiki_link_preservation():
    from cx_postprocess.mt_translate import translate_wikitext_block
    original_chunk = None
    try:
        from cx_postprocess import mt_translate
        original_chunk = mt_translate._translate_raw_chunk
        mt_translate._translate_raw_chunk = lambda text, sl="zh", tl="bn": "«" + text + "»"
        src = "উৎস দেখুন: [[s:漢書/卷028上]] এবং [[s:漢書/卷028上|হানের বই]]।"
        out = translate_wikitext_block(src, sl="zh", tl="bn")
        # মূল ইন্টারউইকি টার্গেট অক্ষত থাকবে
        assert "[[s:漢書/卷028上]]" in out
        assert "[[s:漢書/卷028上|«হানের বই»]]" in out or "[[s:漢書/卷028上|" in out
    finally:
        if original_chunk is not None:
            mt_translate._translate_raw_chunk = original_chunk


def test_bold_italic_cleanup():
    from cx_postprocess.mt_translate import cleanup_bold_italics
    assert cleanup_bold_italics("''''কিনকাকু-জি''''") == "'''কিনকাকু-জি'''"
    assert cleanup_bold_italics("'''''বোল্ড ইটালিক'''''") == "'''''বোল্ড ইটালিক'''''"
    assert cleanup_bold_italics("''ইটালিক''") == "''ইটালিক''"


def test_toolkit_convenience_methods(tmp_path):
    from wikipedia_translation_toolkit import WikipediaTranslator
    wt = WikipediaTranslator()

    assert hasattr(wt, "translate_german")
    assert hasattr(wt, "translate_chinese")
    assert hasattr(wt, "translate_japanese")
    assert hasattr(wt, "translate_russian")
    assert hasattr(wt, "translate_english")

    f = tmp_path / "sample_de.txt"
    f.write_text("Hello 120 km² r. 1995", encoding="utf-8")
    out = wt.translate_german(str(f))
    assert "বর্গকিমি" in out or "১২০" in out


def test_gemini_35_default_and_rate_limit_fallback(monkeypatch):
    import email.message
    import io
    import urllib.error
    import urllib.request
    from common.env_loader import DEFAULT_GEMINI_MODEL, RATE_LIMIT_FALLBACK_MODEL
    from cx_postprocess.mt_translate import translate_paragraph_gemini

    assert DEFAULT_GEMINI_MODEL == "gemini-3.5-flash"
    assert RATE_LIMIT_FALLBACK_MODEL == "gemini-3.1-flash-lite"

    call_history = []
    dummy_headers = email.message.Message()

    def mock_urlopen(req, timeout=30):
        url = req.full_url
        if "gemini-3.5-flash" in url:
            call_history.append("gemini-3.5-flash")
            # Simulate 429 Rate Limit error
            raise urllib.error.HTTPError(url, 429, "Too Many Requests", dummy_headers, io.BytesIO(b'{"error":{"code":429}}'))
        elif "gemini-3.1-flash-lite" in url:
            call_history.append("gemini-3.1-flash-lite")
            # Success with 3.1 flash
            res_payload = b'{"candidates":[{"content":{"parts":[{"text":"\xe0\xa6\x85\xe0\xa6\xa8\xe0\xa7\x82\xe0\xa6\xa6\xe0\xa6\xbf\xe0\xa6\xa4 \xe0\xa6\xaa\xe0\xa6\xbe\xe0\xa6\xa0"}]}}]}'
            return io.BytesIO(res_payload)
        raise urllib.error.HTTPError(url, 404, "Not Found", dummy_headers, None)

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    res = translate_paragraph_gemini("This is a paragraph.", api_key="dummy-key", model="gemini-3.5-flash")
    assert res == "অনূদিত পাঠ"
    assert call_history == ["gemini-3.5-flash", "gemini-3.1-flash-lite"]


def test_gemma_translation_and_scratchpad_stripping(monkeypatch):
    """Gemma মডেলে যাতে systemInstruction ছাড়া এবং রিজনিং ফিল্টারিং কাজ করে তা যাচাই।"""
    import urllib.request
    import json
    import io
    from cx_postprocess.mt_translate import translate_paragraph_gemini

    captured_reqs = []

    def mock_gemma_urlopen(req, timeout=30):
        body = json.loads(req.data.decode("utf-8"))
        captured_reqs.append({"url": req.full_url, "body": body})
        # Simulate Gemma returning thinking scratchpad followed by clean Bengali
        gemma_raw_text = (
            "Role: Bengali Wikipedia Translator\n"
            "Task: Translate\n"
            "* Kinkaku-ji: কিনকাকু-জি\n"
            "* Analysis: clean translation\n"
            "কিনকাকু-জি জাপানের কিয়োটোতে অবস্থিত একটি বিখ্যাত মন্দির।"
        )
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": gemma_raw_text}]
                    }
                }
            ]
        }
        return io.BytesIO(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(urllib.request, "urlopen", mock_gemma_urlopen)

    res = translate_paragraph_gemini("Kinkaku-ji is a famous temple in Kyoto.", api_key="test-key", model="gemma-4-26b")
    assert res == "কিনকাকু-জি জাপানের কিয়োটোতে অবস্থিত একটি বিখ্যাত মন্দির।"
    assert len(captured_reqs) == 1
    assert "gemma-4-26b-a4b-it" in captured_reqs[0]["url"]
    # Gemma মডেলে systemInstruction থাকা যাবে না (HTTP 400 এড়াতে)
    assert "systemInstruction" not in captured_reqs[0]["body"]


def test_doc_ref_placeholder_bengali_digits_restoration():
    """__DOC_REF_PLACEHOLDER_৫৮__ ইত্যাদি বাংলা অঙ্কে রূপান্তর হলেও যেন আসল রেফ ফিরে পায়।"""
    from cx_postprocess.mt_translate import translate_wikitext_full

    src = "In 1925, Kowalska worked as a housemaid.<ref>The Diary of Saint Maria Faustina Kowalska</ref>"
    # এখানে translate_wikitext_full চালালে রেফ ট্যাগ প্লেসহোল্ডারে রূপান্তর এবং আবার পুনঃস্থাপন হবে
    out = translate_wikitext_full(src, sl="en", tl="bn")
    assert "__DOC_REF_PLACEHOLDER_" not in out
    assert "<ref>The Diary of Saint Maria Faustina Kowalska</ref>" in out


def test_infobox_template_name_preservation_and_translation():
    """যাচাইকৃত বাংলা নাম থাকলে তথ্যছক ব্যবহার হবে, নচেৎ ইংরেজি ইনফোবক্সই থাকবে।"""
    from cx_postprocess.mt_translate import translate_wikitext_full
    from cx_postprocess.infobox_map import translate_infobox

    # ১. পরিচিত ইনফোবক্স (settlement ও saint)
    src_known = "{{Infobox settlement\n| name = Paris\n}}"
    out_known, _ = translate_infobox(src_known)
    assert "{{তথ্যছক বসতি" in out_known

    src_saint = "{{Infobox saint\n| name = Faustina\n}}"
    out_saint, _ = translate_infobox(src_saint)
    assert "{{তথ্যছক সাধু" in out_saint

    # ২. অপরিচিত/অযাচাইকৃত ইনফোবক্স ইংরেজি নামেই অক্ষত থাকবে
    src_unknown = "{{Infobox unknown_custom_xyz\n| name = Test\n}}"
    out_unknown, _ = translate_infobox(src_unknown)
    assert "{{Infobox unknown_custom_xyz" in out_unknown
    assert "{{তথ্যছক unknown_custom_xyz" not in out_unknown


def test_isbn_and_identifiers_remain_ascii():
    """ISBN, DOI, PMID এবং সূত্রের আইএসবিএন/তারিখ যেন MediaWiki CS1-এর জন্য বাধ্যতামূলকভাবে ASCII থাকে।"""
    from common.bengali_utils import to_bengali_digits_safe, repair_machine_identifiers
    from cx_postprocess.pipeline import fix_text

    # ১. ইংরেজি cite book টেমপ্লেটে দৃশ্যমান সাল বাংলা হলেও isbn ASCII থাকবে
    src_cite = "{{cite book |author=Drake |year=2002 |title=Saints |isbn=978-1-4033-1039-5}}"
    out_cite = to_bengali_digits_safe(src_cite)
    assert "978-1-4033-1039-5" in out_cite
    assert "year=২০০২" in out_cite

    # ২. বাংলা বই উদ্ধৃতি টেমপ্লেটে বাংলা অঙ্ক ঢুকে গেলেও আইএসবিএন ASCII-তে ঠিক হয়ে যাবে
    src_bn_cite = "{{বই উদ্ধৃতি |লেখক=ড্রেক |বছর=২০০২ |শিরোনাম=সাধু |আইএসবিএন=৯৭৮-১-৪০৩৩-১০৩৯-৫}}"
    out_bn_cite = to_bengali_digits_safe(src_bn_cite)
    assert "আইএসবিএন=978-1-4033-1039-5" in out_bn_cite

    # ৩. স্ট্যান্ডঅ্যালোন আইএসবিএন
    src_standalone = "আইএসবিএন ৯৭৮-১-৪০৩৩-১০৩৯-৫ এবং ISBN 0-8160-4134-2"
    out_standalone = repair_machine_identifiers(src_standalone)
    assert "আইএসবিএন 978-1-4033-1039-5" in out_standalone
    assert "ISBN 0-8160-4134-2" in out_standalone

    # ৪. ডিওআই এবং পিএমআইডি
    src_doi = "{{cite journal |doi=10.1002/9781444395242 |pmid=12345678}}"
    out_doi = to_bengali_digits_safe(src_doi)
    assert "10.1002/9781444395242" in out_doi
    assert "12345678" in out_doi

    # ৫. সম্পূর্ণ পাইপলাইন (fix_text) টেস্ট
    pipeline_res = fix_text(src_cite)
    assert "978-1-4033-1039-5" in pipeline_res["fixed"]



