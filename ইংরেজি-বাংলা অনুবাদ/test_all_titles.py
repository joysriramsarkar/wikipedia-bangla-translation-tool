# -*- coding: utf-8 -*-
import json
import re
from transliterate_engine import transliterate_title_phrase

with open('book_bn_map.json', encoding='utf-8') as f:
    book_bn = json.load(f)

from build_translation import extra_books
for k, v in extra_books.items():
    if k not in book_bn:
        book_bn[k] = v

def format_titles_v2(title_raw):
    # 1. Cleanly isolate notes (efn or ref)
    efn_pos = title_raw.find('{{efn')
    ref_pos = title_raw.find('<ref')
    cut_pos = -1
    if efn_pos != -1 and ref_pos != -1:
        cut_pos = min(efn_pos, ref_pos)
    elif efn_pos != -1:
        cut_pos = efn_pos
    elif ref_pos != -1:
        cut_pos = ref_pos

    if cut_pos != -1:
        title_core = title_raw[:cut_pos].strip()
        notes = title_raw[cut_pos:].strip()
    else:
        title_core = title_raw.strip()
        notes = ''

    clean_no_italics = re.sub(r"''", "", title_core).strip()

    # Link check
    m_b = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', clean_no_italics)
    has_link = bool(m_b)
    link_target = m_b.group(1).strip() if m_b else ''
    link_disp = m_b.group(2).strip() if (m_b and m_b.group(2)) else link_target
    clean_target = re.sub(r'\s*\([^)]*\)', '', link_target).strip()

    pure_text = re.sub(r'\[\[|\]\]', '', clean_no_italics).strip()

    # Parenthetical subtitle check
    m_paren = re.search(r"^(.+?)\s*\((.+?)\)$", pure_text)

    # Check established conventional Bengali title
    known_bn = None
    if has_link:
        if link_target in book_bn:
            known_bn = book_bn[link_target]
        elif clean_target in book_bn:
            known_bn = book_bn[clean_target]
        elif link_disp in book_bn:
            known_bn = book_bn[link_disp]
    if not known_bn:
        if pure_text in book_bn:
            known_bn = book_bn[pure_text]
        elif m_paren and m_paren.group(1).strip() in book_bn:
            known_bn = book_bn[m_paren.group(1).strip()]

    # 1. Bengali title column
    if known_bn:
        if has_link:
            bn_title = f"''[[{known_bn}]]''"
        else:
            bn_title = f"''{known_bn}''"
    else:
        if m_paren:
            main_part = m_paren.group(1).strip()
            # If main part has a link
            m_main_link = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', main_part)
            if m_main_link:
                t_target = m_main_link.group(1).strip()
                t_disp = m_main_link.group(2).strip() if m_main_link.group(2) else t_target
                trans_bn = transliterate_title_phrase(t_disp)
                bn_title = f"''[[{t_target}|{trans_bn}]]''"
            else:
                trans_bn = transliterate_title_phrase(main_part)
                if has_link:
                    bn_title = f"''[[{link_target}|{trans_bn}]]''"
                else:
                    bn_title = f"''{trans_bn}''"
        elif has_link:
            trans_bn = transliterate_title_phrase(link_disp)
            bn_title = f"''[[{link_target}|{trans_bn}]]''"
        else:
            trans_bn = transliterate_title_phrase(pure_text)
            bn_title = f"''{trans_bn}''"

    # 2. Roman/Original title column
    # Ensure proper formatting of Roman title
    if m_paren:
        eng_part = m_paren.group(1).strip()
        orig_part = m_paren.group(2).strip()
        
        # Check if orig_part is editorial note (like 'published posthumously')
        if 'published posthumously' in orig_part.lower():
            if has_link:
                if link_target == link_disp:
                    roman_title = f"''[[{link_target}]]'' ({orig_part})"
                else:
                    roman_title = f"''[[{link_target}|{link_disp}]]'' ({orig_part})"
            else:
                roman_title = f"''{eng_part}'' ({orig_part})"
        else:
            # Foreign subtitle
            if has_link:
                roman_title = f"''[[{link_target}|{eng_part}]]'' (''{orig_part}'')"
            else:
                roman_title = f"''{eng_part}'' (''{orig_part}'')"
    else:
        if has_link:
            if link_target == link_disp:
                roman_title = f"''[[{link_target}]]''"
            else:
                roman_title = f"''[[{link_target}|{link_disp}]]''"
        else:
            roman_title = f"''{pure_text}''"

    if notes:
        roman_title = f"{roman_title}{notes}"

    return bn_title, roman_title

# Test all titles from List_of_autobiographies_raw.txt
with open('List_of_autobiographies_raw.txt', encoding='utf-8') as f:
    lines = f.readlines()

titles = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line.startswith('|'):
        if '||' not in line:
            if i+2 < len(lines) and lines[i+1].strip().startswith('|') and lines[i+2].strip().startswith('|'):
                titles.append(lines[i+1].strip().lstrip('|').strip())
                i += 3
                continue
        parts = [p.strip() for p in line.lstrip('|').split('||')]
        parts = [p.lstrip('|').strip() for p in parts if p.lstrip('|').strip() != '']
        if len(parts) >= 2:
            titles.append(parts[1].lstrip('|').strip())
    i += 1

print(f"Total titles extracted: {len(titles)}")

# Check for illegal Unicode patterns in Bengali output
illegal_patterns = [
    (r'ং[ােিীুূোৌৈ]', 'ং followed by vowel sign'),
    (r'[ােিীুূোৌৈ]{2,}', 'consecutive vowel signs'),
    (r'[a-zA-Z]{3,}', 'untranslated latin word (3+ chars)')
]

issues = []
for idx, t in enumerate(titles):
    bn_t, ro_t = format_titles_v2(t)
    for pat, desc in illegal_patterns:
        m = re.search(pat, bn_t)
        if m:
            issues.append((idx, t, bn_t, desc, m.group(0)))

print(f"Total issues found: {len(issues)}")
for idx, raw, bn, desc, matched in issues[:20]:
    print(f"Issue: {desc} -> '{matched}' in:\n  RAW: {raw}\n  BN : {bn}\n")
