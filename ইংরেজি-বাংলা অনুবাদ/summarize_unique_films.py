# -*- coding: utf-8 -*-
import json

with open('clean_film_titles.json', encoding='utf-8') as f:
    titles = json.load(f)

with open('film_bn_wiki_map.json', encoding='utf-8') as f:
    bn_map = json.load(f)

unique_films = {}
for t in titles:
    disp = t['display']
    tgt = t['target']
    if disp not in unique_films:
        # check if target or disp in bn_map
        bn_wiki_title = bn_map.get(tgt) or bn_map.get(disp)
        unique_films[disp] = {
            'target': tgt,
            'bn_wiki': bn_wiki_title,
            'occurrences': 1,
            'years': [t['year']]
        }
    else:
        unique_films[disp]['occurrences'] += 1
        unique_films[disp]['years'].append(t['year'])

print(f'Total unique films: {len(unique_films)}')
found_bn_count = sum(1 for v in unique_films.values() if v['bn_wiki'])
print(f'Films with verified bnwiki page: {found_bn_count}')

with open('unique_films_summary.json', 'w', encoding='utf-8') as f:
    json.dump(unique_films, f, ensure_ascii=False, indent=2)
