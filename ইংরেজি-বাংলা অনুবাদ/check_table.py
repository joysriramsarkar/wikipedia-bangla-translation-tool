# -*- coding: utf-8 -*-
with open('আত্মজীবনীর তালিকা (বাংলা).txt', encoding='utf-8') as f:
    lines = f.readlines()

bad = []
total = 0
for i, l in enumerate(lines):
    s = l.strip()
    if s.startswith('|') and not s.startswith('|-') and not s.startswith('|}'):
        total += 1
        parts = s.split('||')
        if len(parts) != 4:
            bad.append((i+1, len(parts), s))

print(f"Total data rows: {total}")
print(f"Bad rows with != 4 columns: {len(bad)}")
for b in bad:
    print(b)
