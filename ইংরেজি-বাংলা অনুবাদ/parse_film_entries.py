# -*- coding: utf-8 -*-
import re
import json

with open('List_of_films_with_live_action_and_animation_raw.txt', encoding='utf-8') as f:
    raw_lines = f.readlines()

parsed_items = []

for idx, line in enumerate(raw_lines, 1):
    s = line.strip()
    if s.startswith('*') and not s.startswith('* [[:Category:') and not s.startswith('* [[List of highest') and not s.startswith('* [http'):
        # Match * Year - Rest
        m = re.match(r'^\*\s*(\d{4}(?:\s*[-–—]\s*\d{4})?|\d{4})\s*[-–—]+\s*(.*)$', s)
        if m:
            yr = m.group(1).strip()
            rest = m.group(2).strip()
            parsed_items.append((idx, yr, rest))
        else:
            print(f'Line {idx} did not match: {s}')

print(f'Total parsed items: {len(parsed_items)}')
with open('parsed_film_entries.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_items, f, ensure_ascii=False, indent=2)
