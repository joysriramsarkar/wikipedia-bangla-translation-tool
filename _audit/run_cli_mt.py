# -*- coding: utf-8 -*-
"""End-to-end: CLI `--engine mt` for all five languages, with metrics."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)

import quality as Q  # noqa: E402
import cli  # noqa: E402

COMMANDS = {"en": "english", "zh": "chinese", "ja": "japanese",
            "ru": "russian", "de": "german"}
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

report = []
for lang, command in COMMANDS.items():
    src_path = os.path.join(HERE, "slices", f"{lang}.wikitext")
    out_path = os.path.join(OUT, f"cli_mt_{lang}.txt")
    src = open(src_path, encoding="utf-8").read()
    t0 = time.time()
    code = cli.main([command, "--engine", "mt", "-i", src_path, "-o", out_path])
    dt = time.time() - t0
    out = open(out_path, encoding="utf-8").read() if os.path.exists(out_path) else ""
    sc = Q.script_counts(Q.strip_markup(out))
    total = sum(sc.values()) or 1
    entry = {
        "lang": lang, "exit_code": code, "seconds": round(dt, 1),
        "src_chars": len(src), "out_chars": len(out),
        "bengali_pct": round(100 * sc["bengali"] / total, 2),
        "source_script_pct": round(
            100 * (sc["latin"] + sc["cjk"] + sc["cyrillic"]) / total, 2),
        "structure": Q.structure(src, out),
        "leaks": Q.leaked_tokens(out),
        "citation_dates_bengali": len(__import__("re").findall(
            r"\|\s*(?:access-date|date|archive-date)\s*=\s*[০-৯]", out)),
    }
    report.append(entry)
    print(f"[cli mt {lang}] exit={code} {dt:.1f}s bn%={entry['bengali_pct']} "
          f"src%={entry['source_script_pct']} broken_dates={entry['citation_dates_bengali']} "
          f"leaks={entry['leaks']}")

json.dump(report, open(os.path.join(HERE, "cli_mt_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("\nsaved _audit/cli_mt_report.json")
