# -*- coding: utf-8 -*-
"""Run the CX MT engine (Google path) for all five languages on sliced articles."""
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
from cx_postprocess.mt_translate import translate_wikitext_full  # noqa: E402

LANGS = ["en", "zh", "ja", "ru", "de"]
BUDGET = int(sys.argv[1]) if len(sys.argv) > 1 else 6000
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

report = []
for lang in LANGS:
    src = open(os.path.join(HERE, "src", f"{lang}.wikitext"), encoding="utf-8").read()
    clip = Q.slice_article(src, BUDGET)
    t0 = time.time()
    status, err = "ok", ""
    try:
        out = translate_wikitext_full(clip, sl=lang, tl="bn", gemini_key=None)
    except Exception as exc:
        out, status, err = "", "exception", f"{type(exc).__name__}: {exc}"
        traceback.print_exc()
    dt = time.time() - t0
    open(os.path.join(OUT, f"mt_{lang}.txt"), "w", encoding="utf-8").write(out)

    sc_src = Q.script_counts(Q.strip_markup(clip))
    sc_out = Q.script_counts(Q.strip_markup(out))
    tot_out = sum(sc_out.values()) or 1
    struct = Q.structure(clip, out)
    entry = {
        "lang": lang, "status": status, "error": err, "seconds": round(dt, 1),
        "src_chars": len(clip), "out_chars": len(out),
        "out_bengali_pct": round(100 * sc_out["bengali"] / tot_out, 2),
        "out_src_script_pct": round(
            100 * (sc_out["latin"] + sc_out["cjk"] + sc_out["cyrillic"]) / tot_out, 2),
        "structure": struct,
        "leaks": Q.leaked_tokens(out),
        "leftover_words_top": Q.leftover_words(clip, out)[:10],
    }
    report.append(entry)
    print(f"[mt {lang}] {status} {dt:.1f}s in={len(clip)} out={len(out)} "
          f"bn%={entry['out_bengali_pct']} srcscript%={entry['out_src_script_pct']} "
          f"leaks={entry['leaks']}")

json.dump(report, open(os.path.join(HERE, "mt_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("saved _audit/mt_report.json")
