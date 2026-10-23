# -*- coding: utf-8 -*-
import json
import re

with open('parsed_film_entries.json', encoding='utf-8') as f:
    items = json.load(f)

extracted_titles = []
for idx, yr, rest in items:
    # Look for the primary title:
    # Usually: ''[[...]]'' or [[...]] or ''...''
    m = re.match(r"^('{2,3}\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]'{2,3}|\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]|'{2,3}([^']+)('{2,3}))(.*)$", rest)
    if m:
        # parsed
        full_match = m.group(1)
        idx_to_use = m.lastindex if m.lastindex is not None else 0
        trailer = m.group(idx_to_use).strip()
        extracted_titles.append((idx, yr, full_match, trailer))
    else:
        # Check if no quotes, e.g. När Kapten Grogg...
        m2 = re.match(r"^([^\(<]+)(.*)$", rest)
        if m2:
            extracted_titles.append((idx, yr, m2.group(1).strip(), m2.group(2).strip()))
        else:
            extracted_titles.append((idx, yr, rest, ''))

print(f'Total extracted titles: {len(extracted_titles)}')
for item in extracted_titles[:25]:
    print(f'L{item[0]:3} [{item[1]}]: TITLE="{item[2]}" | NOTE="{item[3]}"')
