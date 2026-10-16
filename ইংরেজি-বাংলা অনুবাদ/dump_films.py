# -*- coding: utf-8 -*-
import json

with open('clean_film_titles.json', encoding='utf-8') as f:
    titles = json.load(f)

with open('all_720_films.txt', 'w', encoding='utf-8') as f:
    for t in titles:
        f.write(f"{t['line']}\t{t['year']}\t{t['target'] or ''}\t{t['display']}\t{t['trailer']}\n")

print(f"Wrote {len(titles)} films to all_720_films.txt")
