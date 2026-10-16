import json
import re

with open('title_words_final.json', encoding='utf-8') as f:
    title_words = json.load(f)

cmu = {}
with open('cmudict.dict', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        parts = line.split()
        w = parts[0].lower()
        ph = parts[1:]
        if w not in cmu:
            cmu[w] = ph

from generate_final import transliterate_rule_based, arpabet_to_bn, INITIALS

with open('List_of_autobiographies_raw.txt', encoding='utf-8') as f:
    raw_lines = f.readlines()

fallbacks = set()

for line in raw_lines:
    if line.startswith('|') and '||' in line:
        parts = [p.strip() for p in line.split('||')]
        if len(parts) >= 2:
            tit = parts[1]
            pure = re.sub(r'\[\[|\]\]|\'\'', '', tit)
            for cut in ['{{efn', '<ref']:
                if cut in pure:
                    pure = pure[:pure.find(cut)]
            tokens = re.findall(r"[A-Za-z0-9À-ÿ'\-]+", pure)
            for t in tokens:
                low = t.lower()
                if low in title_words or t in INITIALS or re.match(r'^\d+$', t):
                    continue
                if low.endswith("'s") and (low[:-2] in title_words or low[:-2] in cmu):
                    continue
                if low in cmu:
                    continue
                fallbacks.add((t, low))

print(f'Total fallback words: {len(fallbacks)}')
with open('fallback_words.txt', 'w', encoding='utf-8') as out:
    for orig, low in sorted(fallbacks):
        rule_bn = transliterate_rule_based(orig)
        out.write(f'{orig}\t{low}\t{rule_bn}\n')
print('Wrote to fallback_words.txt')
