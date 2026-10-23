# -*- coding: utf-8 -*-
"""Run the 5-language toolkit translation and store outputs + metrics."""
import json
import os
import sys
import time
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import quality as Q  # noqa: E402
from wikipedia_translation_toolkit import WikipediaTranslator  # noqa: E402

LANGS = [("en", "english"), ("zh", "chinese"), ("ja", "japanese"),
         ("ru", "russian"), ("de", "german")]
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

tr = WikipediaTranslator()
report = []

for lang, cmd in LANGS:
    src_path = os.path.join(HERE, "src", f"{lang}.wikitext")
    src = open(src_path, encoding="utf-8").read()
    t0 = time.time()
    status = "ok"
    err = ""
    try:
        out = tr.translate_text(src, cmd)
    except Exception as exc:
        out = ""
        status = "exception"
        err = f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    dt = time.time() - t0
    open(os.path.join(OUT, f"toolkit_{lang}.txt"), "w", encoding="utf-8").write(out)

    vis_src, vis_out = Q.strip_markup(src), Q.strip_markup(out)
    sc_src, sc_out = Q.script_counts(vis_src), Q.script_counts(vis_out)
    total_src = sum(sc_src.values()) or 1
    total_out = sum(sc_out.values()) or 1
    struct = Q.structure(src, out)
    rules = tr.validate_rules(out)

    entry = {
        "lang": lang,
        "status": status,
        "error": err,
        "seconds": round(dt, 2),
        "src_chars": len(src),
        "out_chars": len(out),
        "identical": src.strip() == out.strip(),
        "src_script": sc_src,
        "out_script": sc_out,
        "src_bengali_pct": round(100 * sc_src["bengali"] / total_src, 2),
        "out_bengali_pct": round(100 * sc_out["bengali"] / total_out, 2),
        "out_src_script_pct": round(100 * (sc_out["latin"] + sc_out["cjk"] + sc_out["cyrillic"]) / total_out, 2),
        "structure": struct,
        "leaks": Q.leaked_tokens(out),
        "leftover_words_top": Q.leftover_words(src, out)[:8],
        "headings_src": [h[1] for h in Q.headings(src)][:6],
        "headings_out": [h[1] for h in Q.headings(out)][:6],
        "rules_valid": rules["valid"],
        "rules_issue_count": rules["issue_count"],
        "rules_issues": rules["issues"][:6],
    }
    report.append(entry)
    print(f"[{lang}] {status} {dt:.1f}s in={len(src)} out={len(out)} "
          f"bn%={entry['out_bengali_pct']} srcscript%={entry['out_src_script_pct']} "
          f"identical={entry['identical']}")

json.dump(report, open(os.path.join(HERE, "toolkit_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("saved _audit/toolkit_report.json")
