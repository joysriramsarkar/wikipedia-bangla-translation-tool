import json
import re

with open('primary_words_translit.txt', encoding='utf-8') as f:
    words_data = [l.strip().split('\t') for l in f if l.strip()]

with open('title_words_final.json', encoding='utf-8') as f:
    title_words = json.load(f)

print(f'Total words in primary titles: {len(words_data)}')

# Let's inspect words by source: TW, CMU, FALLBACK
tw_words = [w for w in words_data if w[2] == 'TW']
cmu_words = [w for w in words_data if w[2] == 'CMU']
fallback_words = [w for w in words_data if w[2] == 'FALLBACK']

print(f'TW: {len(tw_words)}, CMU: {len(cmu_words)}, FALLBACK: {len(fallback_words)}')

# Let's write fallback words to inspect
with open('review_fallback.txt', 'w', encoding='utf-8') as f:
    for w, bn, src in fallback_words:
        f.write(f'{w:25} -> {bn}\n')

# Let's write CMU words to inspect
with open('review_cmu.txt', 'w', encoding='utf-8') as f:
    for w, bn, src in cmu_words:
        f.write(f'{w:25} -> {bn}\n')

print('Wrote review_fallback.txt and review_cmu.txt')
