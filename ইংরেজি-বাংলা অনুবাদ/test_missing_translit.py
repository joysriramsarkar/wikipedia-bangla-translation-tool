# -*- coding: utf-8 -*-
import json
import transliterate_engine as te

with open('missing_film_words.txt', encoding='utf-8') as f:
    words = [line.strip() for line in f if line.strip()]

results = {}
for w in words:
    bn = te.transliterate_title_word(w)
    results[w] = bn

with open('missing_film_words_translit.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f'Transliterated {len(results)} words.')
for w in list(results.keys())[:30]:
    print(f'{w:20} -> {results[w]}')
