# -*- coding: utf-8 -*-
import re

with open('আত্মজীবনীর তালিকা (বাংলা).txt', encoding='utf-8') as f:
    lines = f.readlines()

bad_rows = []
english_digits_in_year = []
latin_in_lang = []
broken_notes = []

total_rows = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('|') and not s.startswith('|-') and not s.startswith('|}'):
        total_rows += 1
        parts = [p.strip() for p in s.split('||')]
        if len(parts) != 5:
            bad_rows.append((i+1, len(parts), s))
            continue
        
        auth, tit_bn, tit_ro, lang, yr = parts
        
        # Check english digits in yr (ignoring inside ref or efn)
        yr_clean = re.sub(r'\{\{efn.*?\}\}|<ref.*?</ref>|<ref.*?/>', '', yr)
        if re.search(r'[0-9]', yr_clean):
            english_digits_in_year.append((i+1, yr_clean))
            
        # Check latin in lang
        if lang != '&nbsp;' and re.search(r'[a-zA-Z]', lang):
            latin_in_lang.append((i+1, lang))
            
        # Check if unclosed ref or mangled note exists
        if '</ref>}}' in tit_ro and not '{{efn' in tit_ro:
            broken_notes.append((i+1, 'Unmatched </ref>}}', tit_ro))
        if '<ref>' in s and not '</ref>' in s:
            broken_notes.append((i+1, 'Unclosed <ref>', s))
        if '{{efn' in s and not '}}' in s:
            broken_notes.append((i+1, 'Unclosed {{efn', s))

print(f"Total data rows verified: {total_rows}")
print(f"Rows with column count != 5: {len(bad_rows)}")
print(f"Rows with English digits in year: {len(english_digits_in_year)}")
print(f"Rows with Latin letters in language: {len(latin_in_lang)}")
print(f"Rows with broken notes / unclosed tags: {len(broken_notes)}")
if english_digits_in_year:
    print(f"English digits in year: {english_digits_in_year}")

# Let's inspect Basil Embry and Ann Carl rows
print("\n--- Inspecting Line with Basil Embry ---")
for i, l in enumerate(lines):
    if 'ব্যাসিল এমব্রি' in l:
        print(f"Line {i+1}:\n{l}\n")
        break

print("--- Inspecting Line with Ann Carl ---")
for i, l in enumerate(lines):
    if 'Ann B. Carl' in l or 'অ্যান বি. কার্ল' in l or 'WASP' in l:
        print(f"Line {i+1}:\n{l}\n")
        break

print("--- Inspecting Uptown Girl ---")
for i, l in enumerate(lines):
    if 'Uptown Girl' in l:
        print(f"Line {i+1}:\n{l}\n")
        break

print("--- Inspecting Anne Frank ---")
for i, l in enumerate(lines):
    if 'আনা ফ্রাঙ্ক' in l:
        print(f"Line {i+1}:\n{l}\n")
        break
