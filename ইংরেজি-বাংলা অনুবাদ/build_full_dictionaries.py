# -*- coding: utf-8 -*-
import json
import re

# Load existing caches
with open('author_bn_map.json', encoding='utf-8') as f:
    author_bn = json.load(f)

with open('book_bn_map.json', encoding='utf-8') as f:
    book_bn = json.load(f)

# Load found wiki langlinks
try:
    with open('author_bn_wiki_found.json', encoding='utf-8') as f:
        wiki_found = json.load(f)
except Exception:
    wiki_found = {}

# CMU dict
cmu = {}
with open('cmudict.dict', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        parts = line.split()
        word = parts[0].split('(')[0].lower()
        if word not in cmu:
            cmu[word] = parts[1:]

print(f"Loaded CMU dict: {len(cmu)} words")
