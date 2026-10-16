# -*- coding: utf-8 -*-
import re

with open('市辖区_(中华人民共和国).wikitext', 'r', encoding='utf-8') as f:
    text = f.read()

# Split out the 2 tables
pos1 = text.find('=== 直辖市市辖区 ===')
pos2 = text.find('=== 地级市市辖区 ===')
pos_end = text.find('== 杂学 ==')

t1_raw = text[pos1:pos2]
t2_raw = text[pos2:pos_end]

def parse_wikitable(t_raw):
    # Find table
    start = t_raw.find('{|')
    end = t_raw.find('|}')
    content = t_raw[start:end+2]
    
    rows = []
    current_row = []
    
    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('{|'):
            i += 1
            continue
        if line.startswith('|}'):
            break
        if line.startswith('|-'):
            # row separator
            row_style = line[2:].strip()
            # start new row
            i += 1
            row_lines = []
            while i < len(lines) and not lines[i].strip().startswith('|-') and not lines[i].strip().startswith('|}'):
                row_lines.append(lines[i])
                i += 1
            rows.append((row_style, row_lines))
        else:
            # Header or pre-separator
            i += 1
            
    return rows

r1 = parse_wikitable(t1_raw)
r2 = parse_wikitable(t2_raw)

print(f'Table 1 rows: {len(r1)}')
print(f'Table 2 rows: {len(r2)}')

# Inspect header rows vs province headers vs data rows
def analyze_rows(rows, t_name):
    headers = []
    prov_headers = []
    data_rows = []
    other = []
    for style, r_lines in rows:
        combined = '\n'.join(r_lines).strip()
        if combined.startswith('!'):
            headers.append((style, combined))
        elif 'colspan=' in combined:
            prov_headers.append((style, combined))
        elif combined.startswith('|'):
            data_rows.append((style, combined))
        else:
            other.append((style, combined))
    print(f'[{t_name}] Headers: {len(headers)}, Province headers: {len(prov_headers)}, Data rows: {len(data_rows)}, Other: {len(other)}')
    return data_rows

d1 = analyze_rows(r1, 'Table 1 (Direct-Administered)')
d2 = analyze_rows(r2, 'Table 2 (Prefecture-Level)')

print(f'Total data rows: {len(d1)} + {len(d2)} = {len(d1) + len(d2)}')
