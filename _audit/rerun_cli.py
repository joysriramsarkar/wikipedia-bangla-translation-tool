# -*- coding: utf-8 -*-
"""Re-run only the given languages through the CLI MT path."""
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
import cli  # noqa: E402

COMMANDS = {"en": "english", "zh": "chinese", "ja": "japanese",
            "ru": "russian", "de": "german"}
langs = sys.argv[1:] or ["en", "ru"]
for lang in langs:
    src_path = os.path.join(HERE, "slices", f"{lang}.wikitext")
    out_path = os.path.join(HERE, "out", f"cli_mt_{lang}.txt")
    t0 = time.time()
    cli.main([COMMANDS[lang], "--engine", "mt", "-i", src_path, "-o", out_path])
    out = open(out_path, encoding="utf-8").read()
    bad = re.findall(r"\|\s*(?:access-?date|archive-date|date)\s*=\s*[০-৯]", out)
    sc = Q.script_counts(Q.strip_markup(out))
    tot = sum(sc.values()) or 1
    print(f"[{lang}] {time.time()-t0:.1f}s bn%={100*sc['bengali']/tot:.2f} broken_dates={len(bad)}")
