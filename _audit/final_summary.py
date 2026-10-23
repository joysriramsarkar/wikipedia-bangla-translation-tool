# -*- coding: utf-8 -*-
"""Final numbers for the report."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

toolkit = {e["lang"]: e for e in json.load(open(os.path.join(HERE, "toolkit_report.json"), encoding="utf-8"))}
mt = {e["lang"]: e for e in json.load(open(os.path.join(HERE, "cli_mt_report.json"), encoding="utf-8"))}
gem = json.load(open(os.path.join(HERE, "gemini_report.json"), encoding="utf-8"))

print("LANG | module bn% | mt bn% | mt seconds | leftover param lines (mt)")
for lang in ("en", "zh", "ja", "ru", "de"):
    out = open(os.path.join(HERE, "out", f"cli_mt_{lang}.txt"), encoding="utf-8").read()
    pat = {"en": r"[A-Za-z]", "ru": r"[А-Яа-я]", "ja": r"[\u3040-\u30FF\u4E00-\u9FFF]",
           "zh": r"[\u4E00-\u9FFF]", "de": r"[A-Za-z]"}[lang]
    if lang in ("en", "de"):
        lines = 0  # همین زبان مقصد نیست
    else:
        lines = len([l for l in out.splitlines()
                     if re.match(r"^\s*\|", l) and re.search(pat, l)])
    print(f"{lang:>4} | {toolkit[lang]['out_bengali_pct']:9.2f} | {mt[lang]['bengali_pct']:6.2f} | "
          f"{mt[lang]['seconds']:9.1f} | {lines}")

print("\nstructure (src -> out) on MT slices:")
for lang in ("en", "zh", "ja", "ru", "de"):
    s, o = mt[lang]["structure"]["src"], mt[lang]["structure"]["out"]
    diffs = {k: (s[k], o[k]) for k in s if s[k] != o[k]}
    print(f"  {lang}: {diffs if diffs else 'ok'}")
    bad = [f"{a}/{b}" for a, b in (("table_open", "table_close"), ("template_open", "template_close"),
                                   ("link_open", "link_close"), ("ref_open", "ref_close"))
           if o[a] != o[b]]
    if bad:
        print(f"     UNBALANCED in output: {bad}")

print("\ngemini run:")
for label, e in gem.items():
    print(f"  {label}: {e['status']} {e['seconds']}s bn%={e['bengali_pct']}")
    s, o = e["structure"]["src"], e["structure"]["out"]
    print(f"     templates {s['template_open']}->{o['template_open']}, "
          f"links {s['link_open']}->{o['link_open']}, refs {s['ref_open']}->{o['ref_open']}, "
          f"tables {s['table_open']}->{o['table_open']}")

print("\ncurrent defaults still in code:")
for path, pattern in (("cx_postprocess/mt_translate.py", "gemini-1.5-flash"),
                      ("app.py", "gemini-1.5-flash"),
                      ("public/dashboard.html", "gemini-1.5-flash")):
    text = open(os.path.join(ROOT, path), encoding="utf-8").read()
    print(f"  {path}: {text.count(pattern)} occurrence(s)")
