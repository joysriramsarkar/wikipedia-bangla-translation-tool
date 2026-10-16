# -*- coding: utf-8 -*-
"""
জার্মান-বাংলা সারণি অনুবাদক (German-Bengali Wikitable Translator)
------------------------------------------------------------
মিডিয়াউইকি চলচ্চিত্র সারণিসমূহ (wikitables) নিখুঁত সমতা ও কলাম বিন্যাস বজায় রেখে
প্রমিত বাংলায় অনুবাদ করে।
"""

import os
import sys
import re
import importlib.util

_curr_dir = os.path.dirname(os.path.abspath(__file__))

def _load_local_mod(mod_name: str):
    p = os.path.join(_curr_dir, f"{mod_name}.py")
    if os.path.exists(p):
        spec = importlib.util.spec_from_file_location(f"de_{mod_name}", p)
        if spec and spec.loader:
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
    return None

_gt = _load_local_mod("german_transliteration")
transliterate_person_name = getattr(_gt, 'transliterate_person_name', lambda x: x)

_ld = _load_local_mod("links_dictionary")
GENRES_DICT = getattr(_ld, 'GENRES_DICT', {})
COUNTRIES_DICT = getattr(_ld, 'COUNTRIES_DICT', {})
FILM_TERMS_DICT = getattr(_ld, 'FILM_TERMS_DICT', {})

_ft = _load_local_mod("film_title_translator")
format_film_title_cell = getattr(_ft, 'format_film_title_cell', lambda x, y="": x)


def split_row_cells(row_text: str) -> list:
    """
    MediaWiki রো-কে সেলে বিভক্ত করে, কিন্তু [[...]], {{...}}, <ref>...</ref> এর ভেতরের পাইপ অক্ষুণ্ণ রাখে।
    """
    cells = []
    curr = []
    
    link_depth = 0
    tmpl_depth = 0
    tag_depth = 0
    
    s = row_text.strip()
    if s.startswith('|'):
        s = s[1:]
        
    i = 0
    n = len(s)
    while i < n:
        # Check [[ or ]]
        if s[i:i+2] == '[[':
            link_depth += 1
            curr.append('[[')
            i += 2
            continue
        elif s[i:i+2] == ']]' and link_depth > 0:
            link_depth -= 1
            curr.append(']]')
            i += 2
            continue
            
        # Check {{ or }}
        if s[i:i+2] == '{{':
            tmpl_depth += 1
            curr.append('{{')
            i += 2
            continue
        elif s[i:i+2] == '}}' and tmpl_depth > 0:
            tmpl_depth -= 1
            curr.append('}}')
            i += 2
            continue
            
        # Check XML/HTML tags
        if s[i] == '<':
            tag_depth += 1
            curr.append('<')
            i += 1
            continue
        elif s[i] == '>' and tag_depth > 0:
            tag_depth -= 1
            curr.append('>')
            i += 1
            continue
            
        # If at root level
        if link_depth == 0 and tmpl_depth == 0 and tag_depth == 0:
            # Inline cell separator ||
            if s[i:i+2] == '||':
                cells.append("".join(curr).strip())
                curr = []
                i += 2
                continue
            # Newline cell separator \n| (excluding row separator \n|-)
            elif s[i] == '\n' and i + 1 < n and s[i+1] == '|' and (i + 2 >= n or s[i+2] != '-'):
                cells.append("".join(curr).strip())
                curr = []
                i += 2
                continue
                
        curr.append(s[i])
        i += 1
        
    if curr:
        cells.append("".join(curr).strip())
        
    return cells


def translate_people_cell(cell_text: str) -> str:
    """পরিচালক বা অভিনয়শিল্পীদের নাম বাংলায় লিপ্যন্তর করে।"""
    if not cell_text or cell_text.strip() in ['{{n/a}}', '{{N/A}}', 'n/a', 'N/A']:
        return '{{প্র/না}}'
        
    s = cell_text.strip()
    
    # ১. {{ill|Target|de|...}} ও {{Interlanguage link|...}} হ্যান্ডলিং
    def repl_ill(m):
        full = m.group(0)
        # টেমপ্লেটের শেষের অতিরিক্ত পাইপ পরিষ্কার করা (|}})
        full = re.sub(r'\|\s*\}\}', '}}', full)
        target = m.group(1).strip()
        lt_m = re.search(r'\|lt=([^|}]+)', full)
        if lt_m:
            label = lt_m.group(1).strip()
            bn_label = transliterate_person_name(label)
            return re.sub(r'\|lt=[^|}]+', f'|lt={bn_label}', full)
        else:
            bn_label = transliterate_person_name(target)
            return full[:-2] + f'|lt={bn_label}' + '}}'
            
    s = re.sub(r'\{\{(?:ill|Interlanguage link)\|([^|}]+)(?:\|[^}]+)?\}\}', repl_ill, s, flags=re.I)
    
    # ২. [[Target|Label]] বা [[Target]] হ্যান্ডলিং
    def repl_link(m):
        target = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else target
        if target.startswith('File:') or target.startswith('Category:'):
            return m.group(0)
        bn_label = transliterate_person_name(label)
        return f"[[{target}|{bn_label}]]"
        
    s = re.sub(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', repl_link, s)
    
    # ৩. উইকিসংযোগ, টেমপ্লেট ও এইচটিএমএল ট্যাগের বাইরের সাধারণ টেক্সটের নামসমূহ
    parts = []
    tokens = re.split(r'(\[\[[^\]]+\]\]|\{\{[^}]+\}\}|<[^>]+>)', s)
    for tok in tokens:
        if tok.startswith('[[') or tok.startswith('{{') or tok.startswith('<'):
            parts.append(tok)
        else:
            subparts = re.split(r'(,\s*|<br\s*/?>\s*|/\s*)', tok)
            for sp in subparts:
                clean_p = sp.strip(" ,/-")
                if clean_p and re.search(r'[A-Za-z]', clean_p):
                    if clean_p.lower() in ['and others', 'others']:
                        parts.append(sp.replace(clean_p, 'ও অন্যান্য'))
                    else:
                        bn_name = transliterate_person_name(clean_p)
                        parts.append(sp.replace(clean_p, bn_name))
                else:
                    parts.append(sp)
                    
    return "".join(parts)


def translate_genre_cell(cell_text: str) -> str:
    """চলচ্চিত্রের ধরন প্রমিত বাংলায় অনুবাদ করে।"""
    if not cell_text:
        return ""
    s = cell_text.strip()
    
    s = s.replace('[[Anthology film|Anthology]]', '[[সংকলন চলচ্চিত্র|সংকলন]]')
    s = s.replace('[[Black comedy]]', '[[ডার্ক কমেডি]]')
    
    parts = re.split(r'(,\s*|/\s*|<br\s*/?>\s*)', s)
    res = []
    for p in parts:
        clean = p.strip()
        if clean in GENRES_DICT:
            res.append(p.replace(clean, GENRES_DICT[clean]))
        else:
            res.append(p)
    return "".join(res)


def _translate_coprod(match) -> str:
    countries_str = match.group(1).strip()
    c_tokens = re.split(r'(-|\s+)', countries_str)
    bn_tokens = []
    for tok in c_tokens:
        tok_clean = tok.strip()
        if tok_clean in COUNTRIES_DICT:
            bn_tokens.append(COUNTRIES_DICT[tok_clean])
        elif tok_clean == '-':
            bn_tokens.append('-')
        else:
            bn_tokens.append(tok)
    return "".join(bn_tokens) + " যৌথ প্রযোজনা"


def translate_notes_cell(cell_text: str) -> str:
    """মন্তব্য কলামের যৌথ প্রযোজনা, উৎসব ও পুরস্কার অনুবাদ করে।"""
    if not cell_text or not cell_text.strip():
        return "&nbsp;"
    s = cell_text.strip()
    
    # যৌথ প্রযোজনা
    s = re.sub(r'([A-Za-z\-\s]+?)\s+co-production', _translate_coprod, s)
    s = re.sub(r'([A-Za-z\-\s]+?)‐co‐production', _translate_coprod, s)
    
    # চলচ্চিত্র উৎসব ও আন্তর্জাতিক পুরস্কার
    s = s.replace('Premiered at the [[60th Berlin International Film Festival]]', '[[৬০তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসব|৬০তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসবে]] প্রিমিয়ার')
    s = s.replace('Entered into the [[63rd Berlin International Film Festival]]', '[[৬৩তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসব|৬৩তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসবে]] অংশ নিয়েছিল')
    s = s.replace('Entered into the [[64th Berlin International Film Festival]]', '[[৬৪তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসব|৬৪তম বার্লিন আন্তর্জাতিক চলচ্চিত্র উৎসবে]] অংশ নিয়েছিল')
    s = s.replace('Shortlisted for the German nomination for the [[Academy Award for Best Foreign Language Film]]', '[[শ্রেষ্ঠ আন্তর্জাতিক ফিচার চলচ্চিত্র বিভাগে একাডেমি পুরস্কার|সেরা বিদেশি ভাষার চলচ্চিত্র বিভাগে একাডেমি পুরস্কারের]] জন্য জার্মানির সংক্ষিপ্ত তালিকায় অন্তর্ভুক্ত')
    s = s.replace('Entered into the [[2012 Toronto International Film Festival|37th Toronto International Film Festival]], two awards at the [[Saturn Awards]]', '[[২০১২ টরন্টো আন্তর্জাতিক চলচ্চিত্র উৎসব|৩৭তম টরন্টো আন্তর্জাতিক চলচ্চিত্র উৎসবে]] অংশ নিয়েছিল, [[স্যাটার্ন পুরস্কার|স্যাটার্ন পুরস্কারে]] দুটি পুরস্কার জিতেছিল')
    s = s.replace('Premiered at the 2010 [[Fantastic Fest]]', '২০১০ [[ফ্যান্টাস্টিক ফেস্ট|ফ্যান্টাস্টিক ফেস্টে]] প্রিমিয়ার')
    s = s.replace('Winner of the [[DEFA (film studio)|DEFA]] prize at [[Dok Leipzig]]', '[[ডক লাইপৎসিশ|ডক লাইপৎসিশে]] [[ডিইএফএ (চলচ্চিত্র স্টুডিও)|ডিইএফএ]] পুরস্কার বিজয়ী')
    s = s.replace('Released by [[Netflix]]', '[[নেটফ্লিক্স|নেটফ্লিক্স]] কর্তৃক মুক্তিপ্রাপ্ত')
    s = s.replace("Adaptation of [[Arnold Schoenberg]]'s ''[[Pierrot Lunaire]]''", "[[আর্নল্ড শ্যোনবার্গ|আর্নল্ড শ্যোনবার্গের]] ''[[পিয়েরো ল্যুনার|পিয়েরো ল্যুনার]]''-এর রূপান্তর")
    s = s.replace('(Shot in 2007)', '(২০০৭ সালে ধারণকৃত)')
    
    # রিমেক
    def repl_remake(m):
        target = m.group(1).strip()
        year = m.group(2) if m.group(2) else ""
        if year:
            return f"{target} ({year})-এর পুনর্নির্মাণ"
        return f"{target}-এর পুনর্নির্মাণ"
    s = re.sub(r'Remake of\s+([^\(\n]+?)(?:\s+\((\d{4})\))?', repl_remake, s)
    
    return s


def translate_film_table(table_text: str) -> str:
    """
    একটি সম্পূর্ণ উইকিটেবিলকে বাংলায় রূপান্তর করে এবং কলাম সমতা নিশ্চিত করে।
    """
    t_start = table_text.find('{|\n' if '{|\n' in table_text else '{|')
    t_end = table_text.rfind('|}')
    if t_start == -1 or t_end == -1:
        return table_text
        
    table_tag = table_text[:table_text.find('\n')+1].strip()
    if not table_tag:
        table_tag = '{| class="wikitable"'
        
    inner = table_text[table_text.find('\n')+1 : t_end].strip()
    raw_rows = re.split(r'\n\|-(?:[^\n]*)', '\n' + inner)
    
    out_rows = []
    # প্রমিত বাংলা হেডার
    bengali_header = '! শিরোনাম !! পরিচালক !! অভিনয়ে !! ধরন !! মন্তব্য'
    out_rows.append(bengali_header)
    
    for r in raw_rows:
        r = r.strip()
        if not r or r.startswith('!'):
            continue
            
        cells = split_row_cells(r)
        if len(cells) < 4:
            continue
            
        notes_raw = cells[4].strip() if len(cells) >= 5 else ""
        title = format_film_title_cell(cells[0].strip(), notes_raw)
        director = translate_people_cell(cells[1].strip())
        cast = translate_people_cell(cells[2].strip())
        genre = translate_genre_cell(cells[3].strip())
        notes = translate_notes_cell(notes_raw)
        
        # প্রতিটি সারিতে ঠিক ৫টি কলাম নিশ্চিত করা
        formatted_row = f"| {title} || {director} || {cast} || {genre} || {notes}"
        out_rows.append(formatted_row)
        
    # নিখুঁত সারির বিভাজক |- নতুন লাইনে রেখে টেবিল তৈরি
    res = table_tag + "\n|-\n" + "\n|-\n".join(out_rows) + "\n|}"
    return res
