# -*- coding: utf-8 -*-
from parse_test import r1, r2
import re

def split_row_cells(row_lines):
    # Join row lines
    text = '\n'.join(row_lines).strip()
    # Cells can be separated by \n| or ||
    # But beware: [[link|label]] also has |
    # So we must NOT split on | inside [[...]] or {{...}}
    
    cells = []
    current = []
    
    # Simple tokenizer
    i = 0
    # Strip leading '|'
    if text.startswith('|'):
        text = text[1:]
        
    bracket_depth = 0
    brace_depth = 0
    
    curr = ""
    while i < len(text):
        if text[i:i+2] == '[[':
            bracket_depth += 1
            curr += '[['
            i += 2
        elif text[i:i+2] == ']]':
            bracket_depth -= 1
            curr += ']]'
            i += 2
        elif text[i:i+2] == '{{':
            brace_depth += 1
            curr += '{{'
            i += 2
        elif text[i:i+2] == '}}':
            brace_depth -= 1
            curr += '}}'
            i += 2
        elif text[i:i+2] == '||' and bracket_depth == 0 and brace_depth == 0:
            cells.append(curr.strip())
            curr = ""
            i += 2
        elif text[i] == '\n' and i + 1 < len(text) and text[i+1] == '|' and bracket_depth == 0 and brace_depth == 0:
            cells.append(curr.strip())
            curr = ""
            i += 2 # skip \n and |
        else:
            curr += text[i]
            i += 1
    if curr.strip():
        cells.append(curr.strip())
        
    return cells

print('Testing cell splitting on first 5 rows of Table 1:')
for style, lines in r1[2:7]:
    c = split_row_cells(lines)
    print(f'Row has {len(c)} cells:')
    for idx, cell in enumerate(c):
        print(f'  Cell {idx+1}: {cell[:50]}...')

print('\nTesting cell splitting on first 5 rows of Table 2:')
for style, lines in r2[2:7]:
    c = split_row_cells(lines)
    print(f'Row has {len(c)} cells:')
    for idx, cell in enumerate(c):
        print(f'  Cell {idx+1}: {cell[:50]}...')
