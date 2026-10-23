# -*- coding: utf-8 -*-
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from cx_postprocess.bn_digits_safe import protect_machine_spans, _CITATION_TEMPLATE_RE
from cx_postprocess.pipeline import fix_text

sample = "<ref name=x>{{উদ্ধৃত ওয়েব\n|url=https://x\n|title=T\n|date=2016-07-12\n|accessdate=2017-10-27}}</ref>"
print("template regex on block:", bool(_CITATION_TEMPLATE_RE.match(sample.split("<ref name=x>")[1])))
print("masked:", protect_machine_spans(sample)[0].replace("\n", " "))
print("fix_text:", fix_text(sample)["fixed"].replace("\n", " "))
print()
s = open(os.path.join(ROOT, "_audit", "out", "cli_mt_ru.txt"), encoding="utf-8").read()
i = s.find("উদ্ধৃত ওয়েব")
print("repr of template name from output:", repr(s[i - 4:i + 14]))
print("codepoints:", [hex(ord(c)) for c in s[i:i + 12]])
print("my literal codepoints:", [hex(ord(c)) for c in "উদ্ধৃত"])
