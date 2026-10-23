# -*- coding: utf-8 -*-
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
s = open(os.path.join(HERE, "out", "cli_mt_ru.txt"), encoding="utf-8").read()
for m in re.finditer(r"\|[^|{}\n]*(?:access-?date|archive-date|\bdate)\s*=\s*[০-৯][^|}\n]*", s):
    ctx = s[max(0, m.start() - 260):m.start() + len(m.group(0))]
    print("HIT:", m.group(0))
    print("  ctx:", repr(ctx[-260:]))
    print()
