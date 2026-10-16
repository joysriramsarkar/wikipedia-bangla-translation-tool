# -*- coding: utf-8 -*-
import json
import re
from transliterate_engine import cmu, arpabet_to_bn, transliterate_rule_based

with open('title_words_final.json', encoding='utf-8') as f:
    title_words = json.load(f)

with open('unique_title_words.txt', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

unmapped = [w for w in words if w.lower() not in title_words]

def trans_w(w):
    low = w.lower()
    if low.endswith("'s"):
        root = low[:-2]
        if root in title_words:
            return title_words[root] + 'স'
        if root in cmu:
            return arpabet_to_bn(cmu[root]) + 'স'
    if low in cmu:
        return arpabet_to_bn(cmu[low])
    return transliterate_rule_based(w)

for w in unmapped[:50]:
    print(f"{w:20} -> {trans_w(w)}")
