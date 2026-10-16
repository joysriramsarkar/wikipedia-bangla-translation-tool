# -*- coding: utf-8 -*-
import json
import re
from collections import Counter

with open('clean_film_titles.json', encoding='utf-8') as f:
    titles = json.load(f)

# Extract notes without <ref>...</ref> tags
notes = []
for t in titles:
    raw_note = t['trailer'].strip()
    if not raw_note:
        continue
    # Remove <ref> tags
    clean = re.sub(r'<ref[^>]*>.*?</ref>', '', raw_note, flags=re.DOTALL)
    clean = re.sub(r'<ref[^>]*/>', '', clean)
    clean = clean.strip()
    if clean:
        notes.append(clean)

print(f'Total non-empty notes: {len(notes)}')

# Find unique notes
unique_notes = sorted(list(set(notes)))
print(f'Total unique notes (excluding refs): {len(unique_notes)}')

with open('notes_clean_unique.txt', 'w', encoding='utf-8') as f:
    for n in unique_notes:
        f.write(n + '\n')

print('Saved notes_clean_unique.txt')
