# -*- coding: utf-8 -*-
"""Quick checks after the digit-safety wrapper change."""
import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from cx_postprocess.pipeline import fix_text
from cx_postprocess.bn_digits_safe import to_bengali_digits_safe

cases = [
    'Text.<ref>{{cite web|url=http://x|title=T|access-date=2010-07-15|date=24 May 2016}}</ref>',
    '{{Infobox settlement|established_date = 1397|population_total = 1200}}',
    '{{cite web|date={{start date|2010|7|15}}|title=T}}',
    'সূত্র: {{cite book|date=1998-05-01|isbn=7101017193}} আর ১২০ km²',
    '{{Infobox mapframe|zoom=14|frame-latitude=35.0375}}',
]
for c in cases:
    print("IN :", c)
    print("OUT:", to_bengali_digits_safe(c))
    print()
print("fix_text:", fix_text(cases[0])["fixed"])
