# -*- coding: utf-8 -*-
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
for lang in ("en", "ru"):
    s = open(os.path.join(HERE, "out", f"cli_mt_{lang}.txt"), encoding="utf-8").read()
    print("="*30, lang)
    for m in re.finditer(r"\|[^|{}\n]*(?:access-date|archive-date|\bdate)\s*=\s*[০-৯][^|}\n]*", s):
        print("  ", repr(m.group(0)[:120]))
    for m in re.finditer(r"\{\{(?:[Cc]ite|[Ss]itation|উদ্ধৃতি)[^{}\n]{0,80}", s):
        print("  cite:", repr(m.group(0)[:100]))
