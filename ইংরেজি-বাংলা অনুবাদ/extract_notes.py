# -*- coding: utf-8 -*-
import json
import re

with open('parsed_film_entries.json', encoding='utf-8') as f:
    items = json.load(f)

notes = []
for idx, yr, rest in items:
    m = re.match(r"^('{2,3}\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]'{2,3}|\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]|'{2,3}([^']+)('{2,3}))(.*)$", rest)
    if m:
        idx_to_use = m.lastindex if m.lastindex is not None else 0
        trailer = m.group(idx_to_use).strip()
        if trailer:
            notes.append((idx, yr, trailer))
    else:
        m2 = re.match(r"^([^\(<]+)(.*)$", rest)
        if m2 and m2.group(2).strip():
            notes.append((idx, yr, m2.group(2).strip()))

print(f'Total items with notes: {len(notes)}')
with open('unique_notes.txt', 'w', encoding='utf-8') as out:
    for n in notes:
        out.write(f'L{n[0]} [{n[1]}]: {n[2]}\n')
print('Wrote to unique_notes.txt')
