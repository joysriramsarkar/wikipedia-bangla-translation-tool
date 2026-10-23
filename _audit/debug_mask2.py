# -*- coding: utf-8 -*-
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from cx_postprocess.bn_digits_safe import protect_machine_spans, _CITATION_TEMPLATE_RE

s = open(os.path.join(ROOT, "_audit", "out", "cli_mt_ru.txt"), encoding="utf-8").read()
i = s.find("|date=২০১৬")
ctx = s[max(0, i - 200):i + 60]
print("CTX:", ctx)
start = ctx.rfind("{{")
print("template head:", repr(ctx[start:start + 16]))
print("codepoints:", [hex(ord(c)) for c in ctx[start:start + 10]])
print("regex match:", bool(_CITATION_TEMPLATE_RE.match(ctx[start:])))
masked, saved = protect_machine_spans(ctx)
print("masked tail:", repr(masked[-80:]))
print("saved count:", len(saved))
