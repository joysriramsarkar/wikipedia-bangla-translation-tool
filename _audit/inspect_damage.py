# -*- coding: utf-8 -*-
"""Pinpoint concrete wikitext damage in the MT outputs."""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def show(path, label, pattern, limit=4, pad=70):
    s = open(path, encoding="utf-8").read()
    hits = list(re.finditer(pattern, s))
    print(f"\n### {label}: {len(hits)} hit(s)  [{os.path.basename(path)}]")
    for m in hits[:limit]:
        print("   ...", repr(s[max(0, m.start() - pad):m.start() + pad]))


for lang in ("en", "zh", "ja", "ru", "de"):
    out = os.path.join(HERE, "out", f"mt_{lang}.txt")
    src = os.path.join(HERE, "src", f"{lang}.wikitext")
    if not os.path.exists(out):
        continue
    print("=" * 72)
    print("LANG", lang)
    show(out, "stray table close |}", r"\|}")
    show(out, "quadruple apostrophes", r"'{4,}")
    show(out, "bengali access-date / date param (CS1 break)", r"\|\s*(?:access-date|date|archive-date|publication-date)\s*=\s*[০-৯]")
    show(out, "bengali digits in numeric params (zoom/lat/px)",
         r"\|\s*(?:zoom|width|height|frame-latitude|frame-longitude|latd|longd|upright)\s*=\s*[০-৯]")
    # ref / link loss
    s = open(src, encoding="utf-8").read()
    print(f"\n-- refs: src={len(re.findall(r'<ref', s))} out={len(re.findall(r'<ref', open(out, encoding='utf-8').read()))}")
    print(f"-- links: src={s.count('[[')} out={open(out, encoding='utf-8').read().count('[[')}")
