# -*- coding: utf-8 -*-
"""Test the Gemini path: default (1.5) vs working model, quality + structure."""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import quality as Q  # noqa: E402
from cx_postprocess.mt_translate import translate_wikitext_full, translate_paragraph_gemini  # noqa: E402

key = re.match(r'^gemini_api_key\s*[=:]\s*["\']?(.+?)["\']?\s*$',
               open(os.path.join(ROOT, ".env"), "rb").read().decode("utf-8").strip()).group(1)

src = open(os.path.join(HERE, "src", "en.wikitext"), encoding="utf-8").read()
clip = Q.slice_article(src, 2600)
print("clip chars:", len(clip), "lines:", clip.count("\n") + 1)

results = {}
for label, model in (("default-1.5", "gemini-1.5-flash"), ("gemini-3.8", "gemini-3.8-flash")):
    t0 = time.time()
    try:
        out = translate_wikitext_full(clip, sl="en", tl="bn", gemini_key=key, gemini_model=model)
        status = "ok"
    except Exception as exc:
        out, status = "", f"{type(exc).__name__}: {exc}"
    dt = time.time() - t0
    open(os.path.join(HERE, "out", f"gemini_{label}.txt"), "w", encoding="utf-8").write(out)
    sc = Q.script_counts(Q.strip_markup(out))
    tot = sum(sc.values()) or 1
    st = Q.structure(clip, out)
    results[label] = {
        "status": status, "seconds": round(dt, 1), "chars": len(out),
        "bengali_pct": round(100 * sc["bengali"] / tot, 2),
        "structure": st, "leaks": Q.leaked_tokens(out),
    }
    print(f"[{label}] {status} {dt:.1f}s chars={len(out)} bn%={results[label]['bengali_pct']}")
    print("   src struct:", st["src"])
    print("   out struct:", st["out"])
    print("   leaks:", results[label]["leaks"])

json.dump(results, open(os.path.join(HERE, "gemini_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("\n--- direct /translate_ai equivalent (single paragraph, default model) ---")
try:
    r = translate_paragraph_gemini("The temple was built in 1397 and rebuilt in 1955.",
                                   api_key=key, model="gemini-1.5-flash")
    print("returned:", repr(r))
except Exception as exc:
    print("raised:", type(exc).__name__, exc)
