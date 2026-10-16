# -*- coding: utf-8 -*-
import re

filename = 'লাইভ অ্যাকশন ও অ্যানিমেশনযুক্ত চলচ্চিত্রের তালিকা (বাংলা).txt'

with open(filename, encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines in translated file: {len(lines)}')

errors = []
warnings = []

# 1. Check Short description
for idx, line in enumerate(lines, 1):
    if '{{Short description' in line:
        errors.append(f'L{idx}: Short description found!')

# 2. Check film entries count & digits
film_count = 0
for idx, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith('* ') and re.match(r'^\*\s*[০-৯]', s):
        film_count += 1
        
        # Check visible year has no English digits
        m_yr = re.match(r'^\*\s*([^\s–]+)\s*–', s)
        if m_yr:
            yr_str = m_yr.group(1)
            if re.search(r'[0-9]', yr_str):
                errors.append(f'L{idx}: English digits in year: {yr_str}')
        else:
            errors.append(f'L{idx}: Year prefix not recognized: {s[:30]}')
            
        # Check title formatting: should have ''...'' (''...'')
        if not re.search(r"''\[\[.*?\]\]''\s*\(''.*?''\)|''.*?''\s*\(''.*?''\)", s):
            warnings.append(f'L{idx}: Title format check: {s[:50]}')
            
    elif s.startswith('* 1') or s.startswith('* 2') or s.startswith('*1') or s.startswith('*2'):
        errors.append(f'L{idx}: Film entry started with English digits: {s[:30]}')

print(f'Total recognized film entries: {film_count}')

# 3. Check for word starting with 'ৎ' (Rule 4)
for idx, line in enumerate(lines, 1):
    # Word starting with ৎ
    matches = re.findall(r'(?:\s|^)(ৎ[অ-হ্]+)', line)
    if matches:
        errors.append(f'L{idx}: Word starts with ৎ: {matches}')

# 4. Check for broken links [[[[ or ]]]]
for idx, line in enumerate(lines, 1):
    if '[[[[' in line or ']]]]' in line:
        errors.append(f'L{idx}: Broken brackets in line: {line[:50]}')

# 5. Check ref tag balance across file
full_text = ''.join(lines)
open_refs = len(re.findall(r'<ref(?:\s+[^/>]*)?>', full_text))
close_refs = len(re.findall(r'</ref>', full_text))
self_close_refs = len(re.findall(r'<ref[^>]*/>', full_text))
print(f'Refs: open={open_refs}, close={close_refs}, self_close={self_close_refs}')
if open_refs != close_refs:
    errors.append(f'Ref tag mismatch! open={open_refs} vs close={close_refs}')

# 6. Check section headings
for idx, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith('='):
        if re.search(r'[0-9]s', s) or 'by decade' in s or 'See also' in s or 'References' in s:
            errors.append(f'L{idx}: Untranslated heading: {s}')

print(f'Validation complete: {len(errors)} errors, {len(warnings)} warnings.')
if errors:
    print('ERRORS:')
    for e in errors:
        print(' ', e)
if warnings:
    print('WARNINGS (first 10):')
    for w in warnings[:10]:
        print(' ', w)
