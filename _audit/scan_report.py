# -*- coding: utf-8 -*-
"""Scan the report for stray non-Bengali/non-Latin characters."""
import re
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
ranges = {
    "Devanagari": r"[\u0900-\u097F]",
    "Hangul": r"[\uAC00-\uD7AF]",
    "Han": r"[\u4E00-\u9FFF]",
    "Kana": r"[\u3040-\u30FF]",
    "Cyrillic": r"[\u0400-\u04FF]",
}
for name, pat in ranges.items():
    hits = [(m.start(), m.group(0)) for m in re.finditer(pat, text)]
    if hits:
        print(f"{name}: {len(hits)} hit(s)")
        for pos, ch in hits[:6]:
            line = text.count("\n", 0, pos) + 1
            print(f"   line {line}: {ch!r} context={text[max(0,pos-25):pos+25]!r}")
    else:
        print(f"{name}: none")
