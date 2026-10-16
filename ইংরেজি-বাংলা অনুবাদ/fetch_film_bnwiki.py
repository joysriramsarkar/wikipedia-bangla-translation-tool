# -*- coding: utf-8 -*-
import json
import urllib.request
import urllib.parse
import time

with open('extracted_film_links.json', encoding='utf-8') as f:
    film_links = json.load(f)

bn_wiki_map = {}

def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

print(f'Querying Bengali Wikipedia interwiki links for {len(film_links)} titles...')

chunks = list(chunked(film_links, 50))
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
    req = urllib.request.Request(url, headers={'User-Agent': 'WikipediaTranslationBot/1.0 (contact: user@example.com)'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            
            # Map normalized/redirected titles back
            normalized = {item['to']: item['from'] for item in data['query'].get('normalized', [])}
            redirects = {item['to']: item['from'] for item in data['query'].get('redirects', [])}
            
            pages = data['query'].get('pages', {})
            for pid, pdata in pages.items():
                cur_title = pdata.get('title')
                ll = pdata.get('langlinks', [])
                if ll:
                    bn_title = ll[0]['*']
                    # Trace back to original chunk title
                    orig = cur_title
                    if orig in redirects:
                        orig = redirects[orig]
                    if orig in normalized:
                        orig = normalized[orig]
                    
                    bn_wiki_map[cur_title] = bn_title
                    bn_wiki_map[orig] = bn_title
                    for c in chunk:
                        if c.lower() == cur_title.lower() or c.lower() == orig.lower():
                            bn_wiki_map[c] = bn_title
    except Exception as e:
        print(f'Error on chunk {idx}: {e}')
    
    print(f'Processed batch {idx}/{len(chunks)} - Found so far: {len(bn_wiki_map)}')
    time.sleep(0.5)

print(f'Finished! Found Bengali Wikipedia articles for {len(bn_wiki_map)} titles.')

with open('film_bn_wiki_map.json', 'w', encoding='utf-8') as f:
    json.dump(bn_wiki_map, f, ensure_ascii=False, indent=2)

print('Saved to film_bn_wiki_map.json')
