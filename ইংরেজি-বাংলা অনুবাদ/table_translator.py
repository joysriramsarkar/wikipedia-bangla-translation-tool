# -*- coding: utf-8 -*-
"""
ইংরেজি-বাংলা সারণি অনুবাদক (English-Bengali Wikitable Translator)
------------------------------------------------------------
উইকিপিডিয়া ইংরেজি সারণিসমূহ (wikitables) নিখুঁত সমতা, কলাম সংখ্যা ও বিন্যাস বজায় রেখে
প্রমিত বাংলা উইকিপিডিয়ার নিয়মাবলি অনুযায়ী অনুবাদ করে।
"""

import re
import os
import sys

# রুট ও মডিউল পাথ নিশ্চিতকরণ
curr_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(curr_dir)
for p in [curr_dir, root_dir, os.path.join(root_dir, 'common')]:
    if p not in sys.path:
        sys.path.insert(0, p)

import importlib.util

dict_path = os.path.join(curr_dir, "links_dictionary.py")
if os.path.exists(dict_path):
    spec = importlib.util.spec_from_file_location("en_links_dict", dict_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        PERSON_NAMES_MAP = getattr(mod, 'PERSON_NAMES_MAP', {})
        FILM_TITLES_MAP = getattr(mod, 'FILM_TITLES_MAP', {})
        BOOK_TITLES_MAP = getattr(mod, 'BOOK_TITLES_MAP', {})
    else:
        PERSON_NAMES_MAP, FILM_TITLES_MAP, BOOK_TITLES_MAP = {}, {}, {}
else:
    PERSON_NAMES_MAP, FILM_TITLES_MAP, BOOK_TITLES_MAP = {}, {}, {}

nc_path = os.path.join(curr_dir, "number_converter.py")
if os.path.exists(nc_path):
    spec = importlib.util.spec_from_file_location("en_num_conv", nc_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        to_bengali_digits = getattr(mod, 'to_bengali_digits', lambda x: x)
    else:
        to_bengali_digits = lambda x: x
else:
    to_bengali_digits = lambda x: x

try:
    from common.bengali_utils import normalize_nukta_chars, normalize_units, fix_r_reigned
except ImportError:
    try:
        import importlib
        bu = importlib.import_module('bengali_utils')
        normalize_nukta_chars = getattr(bu, 'normalize_nukta_chars', lambda t: t)
        normalize_units = getattr(bu, 'normalize_units', lambda t: t)
        fix_r_reigned = getattr(bu, 'fix_r_reigned', lambda t: t)
    except ImportError:
        def normalize_nukta_chars(t):
            return t.replace('\u09AF\u09BC', '\u09DF').replace('\u09A1\u09BC', '\u09DC').replace('\u09A2\u09BC', '\u09DD')
        def normalize_units(t):
            return t.replace('km²', 'বর্গকিমি').replace('কিমি²', 'বর্গকিমি')
        def fix_r_reigned(t):
            return re.sub(r'\br\.\s*(\d+)', r'শাসনকাল: \1', t)


# সারণি হেডার ম্যাপিং (English -> Bengali)
TABLE_HEADERS_MAP = {
    'title': 'শিরোনাম',
    'film': 'শিরোনাম',
    'film title': 'চলচ্চিত্রের শিরোনাম',
    'movie': 'চলচ্চিত্র',
    'director': 'পরিচালক',
    'directors': 'পরিচালকবৃন্দ',
    'cast': 'অভিনয়ে',
    'cast and crew': 'অভিনয়শিল্পী ও কলাকুশলী',
    'starring': 'অভিনয়ে',
    'producer': 'প্রযোজক',
    'producers': 'প্রযোজকবৃন্দ',
    'writer': 'লেখক',
    'writers': 'লেখকবৃন্দ',
    'author': 'লেখক',
    'genre': 'ধরন',
    'genres': 'ধরন',
    'type': 'ধরন',
    'notes': 'মন্তব্য',
    'remarks': 'মন্তব্য',
    'comments': 'মন্তব্য',
    'description': 'বিবরণ',
    'year': 'সাল',
    'release date': 'মুক্তির তারিখ',
    'date': 'তারিখ',
    'country': 'দেশ',
    'language': 'ভাষা',
    'budget': 'বাজেট',
    'box office': 'বক্স অফিস',
    'gross': 'মোট আয়',
    'rank': 'ক্রম',
    'no.': 'নং',
    'name': 'নাম',
    'person': 'ব্যক্তি',
    'office': 'পদবি',
    'position': 'পদ',
    'term': 'মেয়াদকাল',
    'tenure': 'মেয়াদকাল',
    'party': 'রাজনৈতিক দল',
    'political party': 'রাজনৈতিক দল',
    'population': 'জনসংখ্যা',
    'area': 'আয়তন',
    'density': 'ঘনত্ব',
    'capital': 'রাজধানী',
    'admin center': 'প্রশাসনিক কেন্দ্র',
    'administrative center': 'প্রশাসনিক কেন্দ্র',
    'ref.': 'তথ্যসূত্র',
    'ref': 'তথ্যসূত্র',
    'refs': 'তথ্যসূত্র',
    'references': 'তথ্যসূত্র',
    'source': 'উৎস',
}


def split_row_cells(row_text: str) -> list:
    """
    মিডিয়াউইকি রো-কে সেলে বিভক্ত করে, কিন্তু [[...]], {{...}}, <ref>...</ref> এর ভেতরের পাইপ অক্ষুণ্ণ রাখে।
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
            
        if link_depth == 0 and tmpl_depth == 0 and tag_depth == 0:
            if s[i:i+2] == '||':
                cells.append(''.join(curr).strip())
                curr = []
                i += 2
                continue
            elif s[i] == '\n' and i + 1 < n and s[i+1] == '|':
                cells.append(''.join(curr).strip())
                curr = []
                i += 2
                continue
                
        curr.append(s[i])
        i += 1
        
    cells.append(''.join(curr).strip())
    return cells


def translate_cell_content(cell: str) -> str:
    """একটি সেলের ভেতরের তথ্য বাংলায় অনুবাদ করে।"""
    c = cell.strip()
    if not c or c == "''" or c == '""':
        return '&nbsp;'

    # পরিচিত নাম ও শিরোনাম প্রতিস্থাপন
    for en_name, bn_name in PERSON_NAMES_MAP.items():
        c = re.sub(rf'\[\[{re.escape(en_name)}\]\]', f'[[{en_name}|{bn_name}]]', c)
        c = re.sub(rf'\[\[{re.escape(en_name)}\|([^\]]+)\]\]', f'[[{en_name}|{bn_name}]]', c)

    for en_film, bn_film in FILM_TITLES_MAP.items():
        c = re.sub(rf'\[\[{re.escape(en_film)}\]\]', f"''[[{en_film}|{bn_film}]]'' (''{en_film}'')", c)

    for en_book, bn_book in BOOK_TITLES_MAP.items():
        c = re.sub(rf'\[\[{re.escape(en_book)}\]\]', f"''[[{en_book}|{bn_book}]]''", c)

    # শাসনকাল রূপান্তর
    c = fix_r_reigned(c)
    # একক ও সুপারস্ক্রিপ্ট রূপান্তর (km² -> বর্গকিমি)
    c = normalize_units(c)
    # নুক্তা রূপান্তর
    c = normalize_nukta_chars(c)
    # সংখ্যা রূপান্তর
    c = to_bengali_digits(c)

    return c if c else '&nbsp;'


def translate_wikitable(table_text: str) -> str:
    """
    একটি সম্পূর্ণ উইকিটেবিল বাংলায় অনুবাদ করে।
    কলাম সমতা বজায় রাখে এবং নিয়মাবলি অনুসরণ করে।
    """
    lines = table_text.strip().splitlines()
    out_lines = []
    
    header_count = 0
    in_header = False

    for line in lines:
        s = line.strip()

        # টেবিল শুরু
        if s.startswith('{'):
            out_lines.append(line)
            continue

        # টেবিল শেষ
        if s.startswith('|}'):
            out_lines.append('|}')
            continue

        # রো ডিভাইডার
        if s.startswith('|-'):
            out_lines.append('|-')
            continue

        # হেডার লাইন
        if s.startswith('!'):
            header_parts = re.split(r'\s*!!\s*', s[1:])
            translated_headers = []
            for h in header_parts:
                clean_h = re.sub(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', r'\1', h).strip()
                h_lower = clean_h.lower()
                bn_h = TABLE_HEADERS_MAP.get(h_lower, clean_h)
                translated_headers.append(bn_h)
            
            header_count = len(translated_headers)
            out_lines.append('! ' + ' !! '.join(translated_headers))
            continue

        # সাধারণ ডাটা লাইন
        if s.startswith('|'):
            cells = split_row_cells(s)
            translated_cells = [translate_cell_content(c) for c in cells]

            # কলাম সমতা নিশ্চিতকরণ (Rule 6)
            if header_count > 0:
                while len(translated_cells) < header_count:
                    translated_cells.append('&nbsp;')

            out_lines.append('| ' + ' || '.join(translated_cells))
            continue

        out_lines.append(line)

    return '\n'.join(out_lines)
