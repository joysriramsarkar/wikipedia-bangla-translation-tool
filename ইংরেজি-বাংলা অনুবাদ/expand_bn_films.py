# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import time

with open('clean_film_titles.json', encoding='utf-8') as f:
    titles = json.load(f)

with open('film_bn_wiki_map.json', encoding='utf-8') as f:
    bn_map = json.load(f)

# Collect all unique targets and clean display names
targets_to_check = set()
for t in titles:
    tgt = t['target']
    disp = t['display']
    if tgt and tgt not in bn_map:
        targets_to_check.add(tgt)
    # Also check if disp + ' (film)' or disp itself has a page
    if disp and disp not in bn_map:
        targets_to_check.add(disp)
        targets_to_check.add(f"{disp} (film)")

print(f'Checking {len(targets_to_check)} candidate titles against bnwiki...')

def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# Check bnwiki directly
found_bn = {}
chunks = list(chunked(list(targets_to_check), 50))
for idx, chunk in enumerate(chunks, 1):
    params = {
        'action': 'query',
        'titles': '|'.join(chunk),
        'prop': 'langlinks',
        'lllang': 'bn',
        'redirects': '1',
        'format': 'json'
    }
    url = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'WikiFilmTranslator/1.0 (contact: user@example.com)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            pages = data['query'].get('pages', {})
            for pid, pdata in pages.items():
                cur = pdata.get('title')
                ll = pdata.get('langlinks', [])
                if ll:
                    bn_val = ll[0]['*']
                    found_bn[cur] = bn_val
    except Exception as e:
        print(f'Error batch {idx}: {e}')
    time.sleep(0.3)

print(f'Direct query found {len(found_bn)} more titles!')
for k, v in list(found_bn.items())[:20]:
    print(f'{k} -> {v}')

bn_map.update(found_bn)
with open('film_bn_wiki_map_expanded.json', 'w', encoding='utf-8') as f:
    json.dump(bn_map, f, ensure_ascii=False, indent=2)
