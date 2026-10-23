# -*- coding: utf-8 -*-
"""Show concrete defects in the MT outputs."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quality as Q  # noqa: E402

rep = {e["lang"]: e for e in json.load(open(os.path.join(HERE, "mt_report.json"), encoding="utf-8"))}
PAIRS = [("table_open", "table_close"), ("template_open", "template_close"),
         ("link_open", "link_close"), ("ref_open", "ref_close")]

print("=" * 70)
print("STRUCTURE (source -> output)")
for lang, e in rep.items():
    s, o = e["structure"]["src"], e["structure"]["out"]
    diff = {k: (s[k], o[k]) for k in s if s[k] != o[k]}
    print(f"{lang}: {diff if diff else 'identical counts'}")
    for a, b in PAIRS:
        if o[a] != o[b]:
            print(f"    !! output unbalanced: {a}={o[a]}  {b}={o[b]}")

print("=" * 70)
print("LEFT-OVER SOURCE-LANGUAGE WORDS (top)")
for lang, e in rep.items():
    print(f"{lang}: {e['leftover_words_top']}")

print("=" * 70)
for lang in ("ru", "ja", "zh"):
    out = open(os.path.join(HERE, "out", f"mt_{lang}.txt"), encoding="utf-8").read()
    pat = {"ru": r"[А-Яа-я]", "ja": r"[\u3040-\u30FF\u4E00-\u9FFF]", "zh": r"[\u4E00-\u9FFF]"}[lang]
    lines = [l for l in out.splitlines() if re.match(r"^\s*\|", l) and re.search(pat, l)]
    print(f"\n--- {lang}: {len(lines)} wikitext parameter lines still in source script ---")
    for l in lines[:6]:
        print("   ", l.strip()[:120])

print("=" * 70)
print("EN output: first 1200 chars")
print(open(os.path.join(HERE, "out", "mt_en.txt"), encoding="utf-8").read()[:1200])
