# -*- coding: utf-8 -*-
import re

with open('আত্মজীবনীর তালিকা (বাংলা).txt', encoding='utf-8') as f:
    lines = f.readlines()

latin = []
for i, l in enumerate(lines):
    if l.startswith('|') and '||' in l and not l.startswith('|-') and not l.startswith('|}'):
        parts = l.split('||')
        author_cell = parts[0]
        m = re.search(r'\[\[[^\]\|]+\|([^\]]+)\]\]', author_cell)
        disp = m.group(1) if m else re.sub(r'\[\[|\]\]', '', author_cell).strip()
        if re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜàèìòùÀÈÌÒÙ]', disp):
            latin.append((i+1, disp))

print(f"Latin in author display: {len(latin)}")
for x in latin:
    print(x)
