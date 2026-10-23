# -*- coding: utf-8 -*-
"""Checks for units/dates masking + citation dates."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from cx_postprocess.pipeline import fix_text

cases = [
    'See http://example.com/May/2016.html for the km data.',
    'He was born on October 16, 2026 in Kyoto (120 km²).',
    'Text.<ref>{{cite web|url=http://x|date=24 May 2016|access-date=2010-07-15}}</ref>',
    '[[File:May 2016 photo 02.jpg|thumb|Photo taken in May 2016]]',
    'Population 932.166 billion and area 120 km2.',
]
for c in cases:
    print("IN :", c)
    print("OUT:", fix_text(c)["fixed"])
    print()
