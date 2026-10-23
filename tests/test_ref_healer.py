# -*- coding: utf-8 -*-
"""
Tests for Wikipedia Citation Auto-Healer and Infobox Key Preservation.
"""
from cx_postprocess.ref_healer import (
    extract_reference_definitions,
    heal_named_references,
    audit_citations,
)
from cx_postprocess.infobox_map import translate_infobox
from cx_postprocess.pipeline import fix_text


def test_extract_reference_definitions():
    text = 'Some text<ref name="test1">Definition 1</ref> and more<ref name="test2">Definition 2</ref>.'
    defs = extract_reference_definitions(text)
    assert defs.get("test1") == "Definition 1"
    assert defs.get("test2") == "Definition 2"


def test_heal_orphaned_named_reference():
    source_text = '''{{Infobox football biography
| name = Leon Lobjoit
| height = {{convert|1.88|m|order=flip}}<ref name="soccerway">{{soccerway|217734|accessdate=29 March 2020}}</ref>
}}
Born in Hatfield,<ref name="soccerway" /> played youth football.
'''
    # Suppose target translation only has the self-closing call:
    target_text = 'হার্টফিল্ডে জন্মগ্রহণকারী,<ref name="soccerway" /> যুব ফুটবল খেলেন।'

    healed, healed_names, broken = heal_named_references(target_text, source_text)
    assert "soccerway" in healed_names
    assert len(broken) == 0
    assert '<ref name="soccerway">{{soccerway|217734|accessdate=29 March 2020}}</ref>' in healed


def test_audit_citations_detects_orphans_and_healthy():
    broken_text = 'কোনো সংজ্ঞা ছাড়া সূত্র<ref name="orphan1" /> এবং <ref>সাধারণ সূত্র</ref>।'
    audit1 = audit_citations(broken_text)
    assert not audit1["is_healthy"]
    assert "orphan1" in audit1["orphaned_refs"]

    healthy_text = '<ref name="def1">পূর্ণ সংজ্ঞা</ref> এবং পরবর্তীতে ব্যবহার <ref name="def1" />।'
    audit2 = audit_citations(healthy_text)
    assert audit2["is_healthy"]
    assert len(audit2["orphaned_refs"]) == 0


def test_football_biography_preserves_height_and_english_keys():
    wikitext = '''{{Infobox football biography
| name = Leon Lobjoit
| height = {{convert|1.88|m|order=flip}}<ref name="soccerway">test</ref>
| position = Striker
}}'''
    translated, unknown = translate_infobox(wikitext)
    assert "{{তথ্যছক ফুটবল জীবনী" in translated
    # height must be preserved so Lua Module does not drop it
    assert "| height =" in translated
    assert "| উচ্চতা =" not in translated


def test_pipeline_fixes_and_heals_end_to_end():
    source = 'Data<ref name="src_ref">Source Definition</ref>.'
    target = 'অনূদিত তথ্য<ref name="src_ref" />।'
    res = fix_text(target, source_text=source)
    assert '<ref name="src_ref">Source Definition</ref>' in res["fixed"]
    assert "src_ref" in res["healed_refs"]
    assert res["citations"]["is_healthy"]
