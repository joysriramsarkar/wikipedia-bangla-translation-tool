# -*- coding: utf-8 -*-
"""Write 3000-char-safe slices of all five articles for CLI/e2e runs."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quality as Q  # noqa: E402

out_dir = os.path.join(HERE, "slices")
os.makedirs(out_dir, exist_ok=True)
for lang in ("en", "zh", "ja", "ru", "de"):
    src = open(os.path.join(HERE, "src", f"{lang}.wikitext"), encoding="utf-8").read()
    clip = Q.slice_article(src, 3000)
    path = os.path.join(out_dir, f"{lang}.wikitext")
    open(path, "w", encoding="utf-8").write(clip)
    print(lang, len(clip), "chars ->", path)
