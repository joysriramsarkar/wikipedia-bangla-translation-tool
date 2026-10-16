# -*- coding: utf-8 -*-
"""
যাচাইকরণ স্ক্রিপ্ট (Validation & Verification Script)
চীনের নগর জেলা (বাংলা).txt ফাইলের সমস্ত নিয়মাবলি ও গুণগত মান বারবার যাচাই করে।
"""
import sys
import os
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(_current_dir, 'চীনের নগর জেলা (বাংলা).txt'), 'r', encoding='utf-8') as f:
    text = f.read()

print(f'Total length of translated article: {len(text)} characters')
print(f'Total lines: {len(text.splitlines())}')

errors = []
warnings = []

# ১. Rule 1: {{Short description}} পরিহার
if '{{short description' in text.lower():
    errors.append("Rule 1 VIOLATION: {{Short description}} found!")
else:
    print("Rule 1 PASSED: No {{Short description}} template found.")

# ২. Rule 4: শব্দের শুরুতে 'ৎ' নিষিদ্ধ
initial_t_words = re.findall(r'\bৎ[^\s,।;!|]+', text)
if initial_t_words:
    errors.append(f"Rule 4 VIOLATION: Words starting with 'ৎ': {initial_t_words[:10]}")
else:
    print("Rule 4 PASSED: No words starting with 'ৎ' found.")

# ৩. Rule 11: প্রি-কম্পোজড বাংলা বর্ণ (Pre-composed Unicode)
decomposed = {
    'য+়': text.count('\u09af\u09bc'),
    'ড+়': text.count('\u09a1\u09bc'),
    'ঢ+়': text.count('\u09a2\u09bc'),
}
if any(v > 0 for v in decomposed.values()):
    errors.append(f"Rule 11 VIOLATION: Decomposed nuktas found: {decomposed}")
else:
    print("Rule 11 PASSED: 100% Pre-composed Unicode (য়, ড়, ঢ়).")

# ৪. Rule 2: দৃশ্যমান সংখ্যাসমূহ বাংলা সংখ্যায় (০-৯)
# Find ASCII digits not in HTML attributes or template names
ascii_digits_outside_attrs = []
lines = text.splitlines()
for l_idx, line in enumerate(lines, start=1):
    # Strip HTML attributes like rowspan="12", width:12%, 255px, #FFC0CB, etc.
    l_clean = re.sub(r'(?:rowspan|colspan|width|style|size|font-size|border)=["\'][^"\']*["\']', '', line)
    l_clean = re.sub(r'style="[^"]*"', '', l_clean)
    l_clean = re.sub(r'\|\s*\d+px\s*\]\]', '|px]]', l_clean) # image size
    l_clean = re.sub(r'width:\s*\d+%', '', l_clean)
    l_clean = re.sub(r'url=[^\s|]+', '', l_clean) # URLs in refs
    l_clean = re.sub(r'archive-url=[^\s|]+', '', l_clean)
    l_clean = re.sub(r'colspan=\d+', '', l_clean)
    l_clean = re.sub(r'rowspan=\d+', '', l_clean)
    l_clean = re.sub(r'\{\{lang\|zh-Hans\|[^}]+\}\}', '', l_clean)
    l_clean = re.sub(r'\{\{[Cc]ite web\|[^}]+\}\}', '', l_clean) # references might have year/access-date in ascii or en
    l_clean = re.sub(r'(?:alt_name|author)\d+', '', l_clean) # template params
    l_clean = re.sub(r'\|\s*\d+px', '', l_clean) # image dimensions
    
    # Check for remaining ASCII digits
    m_digits = re.findall(r'[0-9]+', l_clean)
    if m_digits:
        ascii_digits_outside_attrs.append((l_idx, m_digits, line[:60]))

if ascii_digits_outside_attrs:
    warnings.append(f"Rule 2 NOTE: {len(ascii_digits_outside_attrs)} lines have ASCII digits outside standard attributes: sample {ascii_digits_outside_attrs[:5]}")
else:
    print("Rule 2 PASSED: All visible digits converted to Bengali digits (০-৯).")

# ৫. সারণির সমতা ও খালি বাক্স রোধ (Rule 6)
# Check table 1 and table 2 rows for empty strings without &nbsp;
empty_cells = []
for l_idx, line in enumerate(lines, start=1):
    if line.startswith('|') and not line.startswith('|-') and not line.startswith('|}'):
        parts = [p.strip() for p in line.split('||')]
        for p_idx, p in enumerate(parts):
            # check if cell is completely empty or just whitespace
            if p == '' or p == '|':
                empty_cells.append((l_idx, p_idx, line))

if empty_cells:
    warnings.append(f"Rule 6 WARNING: {len(empty_cells)} empty cells without &nbsp; found: sample {empty_cells[:5]}")
else:
    print("Rule 6 PASSED: No empty cells found, all cells have content or &nbsp;.")

# ৬. অনাকাঙ্ক্ষিত চীনা বর্ণ অনুসন্ধান (Chinese characters outside {{lang|...}} and citations)
text_no_lang = re.sub(r'\{\{lang\|zh(?:-Hans)?\|([^}]+)\}\}', '', text)
text_no_lang = re.sub(r'\{\{[Cc]ite web\s*\|[^}]+\}\}', '', text_no_lang, flags=re.IGNORECASE)
text_no_lang = re.sub(r'<!--.*?-->', '', text_no_lang)

remaining_zh = re.findall(r'[\u4e00-\u9fa5]+', text_no_lang)
if remaining_zh:
    warnings.append(f"CHINESE TEXT WARNING: {len(remaining_zh)} Chinese words found outside lang templates: sample {remaining_zh[:15]}")
else:
    print("Chinese Text Check PASSED: No stray Chinese characters found outside lang templates.")

print("\n" + "="*50)
print(f"VERIFICATION SUMMARY: {len(errors)} ERRORS, {len(warnings)} WARNINGS")
if errors:
    print("ERRORS:")
    for e in errors:
        print("  -", e)
if warnings:
    print("WARNINGS:")
    for w in warnings:
        print("  -", w)
print("="*50)
