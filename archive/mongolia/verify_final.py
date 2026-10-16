# -*- coding: utf-8 -*-
import re
from build_mongolia_districts import bn_sort_key

with open('মঙ্গোলিয়ার জেলা (বাংলা).txt', encoding='utf-8') as f:
    text = f.read()

sections = re.findall(r'== (.*?) ==\n(.*?)(?===|\Z)', text, re.DOTALL)
print(f'Total sections to check: {len(sections)}')

all_sorted = True
for title, body in sections:
    items = re.findall(r'^\*(.*?)$', body, re.MULTILINE)
    if not items:
        continue
    sorted_items = sorted(items, key=bn_sort_key)
    if items != sorted_items:
        all_sorted = False
        print('NOT SORTED:', title)
        for i, (a, b) in enumerate(zip(items, sorted_items)):
            if a != b:
                print(f'  pos {i}: got "{a}", expected "{b}"')
                break

if all_sorted:
    print('PASS: All sections are 100% strictly sorted in Bengali alphabetical order!')
