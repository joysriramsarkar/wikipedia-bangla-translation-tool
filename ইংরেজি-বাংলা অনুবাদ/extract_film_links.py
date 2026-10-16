# -*- coding: utf-8 -*-
import re
import json

with open('List_of_films_with_live_action_and_animation_raw.txt', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')

# Extract all wikilinks inside bulleted lines
film_links = set()
entries = []

for line in lines:
    s = line.strip()
    if s.startswith('*') and not s.startswith('* [[:Category:') and not s.startswith('* [[List of highest') and not s.startswith('* [http'):
        # extract links
        links = re.findall(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', s)
        if links:
            # First link is usually the film link
            film_links.add(links[0][0].strip())
        entries.append(s)

print(f'Total film entries: {len(entries)}')
print(f'Total unique first links: {len(film_links)}')

with open('extracted_film_links.json', 'w', encoding='utf-8') as f:
    json.dump(sorted(list(film_links)), f, ensure_ascii=False, indent=2)

print('Saved to extracted_film_links.json')
