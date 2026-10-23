# -*- coding: utf-8 -*-
"""Minimal reproduction: where do refs / links / templates disappear?"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cx_postprocess.mt_translate import translate_wikitext_block, translate_wikitext_full  # noqa: E402
from cx_postprocess.pipeline import fix_text  # noqa: E402

CASES = {
    "two refs + one self-closing ref": (
        'The temple <ref name="a">{{cite web|url=http://example.org/1|title=First}}</ref> '
        'was rebuilt <ref name="a" /> after the fire <ref>{{cite book|title=Second}}</ref> in 1955.'
    ),
    "three links with display text": (
        'It is a [[Zen]] [[Buddhist temples in Japan|Buddhist temple]] in [[Kyoto]], '
        'part of the [[Historic Monuments of Ancient Kyoto|monuments]].'
    ),
    "nested template with two refs": (
        "{{nihongo|'''Kinkaku-ji'''|金閣寺||{{IPA|ja|kʲiꜜŋ}} <ref>{{cite book|title=A}}</ref>}} "
        "is a temple <ref>{{cite web|url=http://x|title=B}}</ref>."
    ),
    "citation with date params": (
        'Text.<ref>{{cite web|url=http://x|title=T|access-date=2010-07-15|date=24 May 2016}}</ref>'
    ),
}

for name, text in CASES.items():
    print("=" * 72)
    print("CASE:", name)
    print("SRC :", text)
    block = translate_wikitext_block(text, sl="en", tl="bn")
    print("BLK :", block)
    full = translate_wikitext_full(text, sl="en", tl="bn")
    print("FULL:", full)
    pipe = fix_text(text)["fixed"]
    print("FIX :", pipe)
    for label, out in (("BLK", block), ("FULL", full), ("FIX", pipe)):
        print(f"   {label}: refs {text.count('<ref')}->{out.count('<ref')}  "
              f"links {text.count('[[')}->{out.count('[[')}  "
              f"templates {text.count('{{')}->{out.count('{{')}  "
              f"selfclosing {text.count('/>')}->{out.count('/>')}")
