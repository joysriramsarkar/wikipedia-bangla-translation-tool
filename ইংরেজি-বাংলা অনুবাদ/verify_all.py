# -*- coding: utf-8 -*-
import re

with open('আত্মজীবনীর তালিকা (বাংলা).txt', encoding='utf-8') as f:
    lines = f.readlines()

english_digits_in_year = []
latin_in_lang = []
broken_cols = []

total_rows = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('|') and not s.startswith('|-') and not s.startswith('|}'):
        total_rows += 1
        parts = [p.strip() for p in s.split('||')]
        if len(parts) != 4:
            broken_cols.append((i+1, len(parts), s))
            continue
        
        auth, tit, lang, yr = parts
        
        # Check english digits in yr
        if re.search(r'[0-9]', yr):
            english_digits_in_year.append((i+1, yr))
        
        # Check latin in lang (except &nbsp;)
        if lang != '&nbsp;' and re.search(r'[a-zA-Z]', lang):
            latin_in_lang.append((i+1, lang))

print(f"Total data rows verified: {total_rows}")
print(f"Rows with column count != 4: {len(broken_cols)}")
print(f"Rows with English digits in year: {len(english_digits_in_year)}")
print(f"Rows with Latin letters in language: {len(latin_in_lang)}")

if english_digits_in_year:
    print("Sample English digits in year:", english_digits_in_year[:5])
if latin_in_lang:
    print("Sample Latin letters in lang:", latin_in_lang[:5])
