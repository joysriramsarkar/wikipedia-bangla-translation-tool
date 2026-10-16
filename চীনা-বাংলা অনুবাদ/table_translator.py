# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া সারণি অনুবাদক (Wikipedia Table Translator)
উইকিটেবিল পার্স করে চীনা ও ইংরেজি নাম, প্রিফেকচার, প্রদেশ, ধরন, আয়তন, জনসংখ্যা এবং কোড অনুবাদ করে।
"""
import re

import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from transliteration import get_bengali_division_name, hanzi_to_bn
from links_dictionary import LINK_MAP
from number_converter import to_bengali_digits, translate_table_notes

def replace_links_in_line(line: str) -> str:
    """লাইনের সব উইকিলিংক ([[Link]]) ডিকশনারি অনুযায়ী বাংলায় রূপান্তর করে।"""
    # বিশেষ ক্ষেত্র
    line = line.replace("''Directly administered''", "সরাসরি শাসিত")
    line = line.replace("{{small|''claimed''}}", "{{small|(''দাবিকৃত'')}}")
    line = line.replace(" and ", " ও ")

    def repl(m):
        target = m.group(1)
        if target in LINK_MAP:
            return f'[[{LINK_MAP[target]}]]'
        # যদি পাইপ সহ থাকে: [[Target|Label]]
        if '|' in target:
            base, label = target.split('|', 1)
            if target in LINK_MAP:
                return f'[[{LINK_MAP[target]}]]'
            if base in LINK_MAP:
                return f'[[{LINK_MAP[base]}]]'
        return m.group(0)

    return re.sub(r'\[\[([^\]]+)\]\]', repl, line)

def translate_main_table(table_text: str) -> str:
    """প্রধান প্রশাসনিক উপবিভাগ সারণি অনুবাদ করে।"""
    rows = table_text.split('\n|-')
    header = rows[0]
    
    # হেডার অনুবাদ
    header_tr = header
    header_tr = header_tr.replace('!English name', '!বাংলা নাম\n! rowspan="2" |ইংরেজি নাম')
    header_tr = header_tr.replace('!Chinese name', '!চীনা নাম')
    header_tr = header_tr.replace('!Prefecture', '!প্রিফেকচার')
    header_tr = header_tr.replace('!Province', '!প্রদেশ')
    header_tr = header_tr.replace('!Type', '!ধরন')
    header_tr = header_tr.replace('!Area (km²)', '!আয়তন (বর্গকিমি)')
    header_tr = header_tr.replace('!Population (2010 Census)', '!জনসংখ্যা ([[2010 Chinese census|২০১০]] আদমশুমারি)')
    header_tr = header_tr.replace('!Division code', '![[Administrative division codes of the People\'s Republic of China|বিভাগ কোড]]')
    header_tr = header_tr.replace('!Numeric', '!সংখ্যাগত')
    header_tr = header_tr.replace('!Alpha', '!বর্ণানুক্রমিক')

    new_rows = [header_tr]

    for r in rows[1:]:
        lines = r.split('\n')
        # প্রথম লাইনে স্টাইল থাকতে পারে: |-style="..."
        # lines[0] = style বা খালি
        # lines[1] = ইংরেজি নাম (|[[...]])
        # lines[2] = চীনা নাম ও অন্যান্য কলাম
        style_prefix = ""
        content_lines = []
        for idx, l in enumerate(lines):
            if idx == 0 and l.startswith('style='):
                style_prefix = l
            elif l.strip():
                content_lines.append(l)

        if not content_lines:
            continue

        en_link_line = content_lines[0]
        zh_line = content_lines[1] if len(content_lines) > 1 else ""

        # চীনা হানজি ও বিভাগের ধরন বের করা
        zh_parts = zh_line.split('||')
        zh_hz = zh_parts[0].strip() if zh_parts else ""
        type_str = zh_parts[-1].strip() if len(zh_parts) > 1 else ""

        # বাংলা নাম নির্ণয়
        bn_name = get_bengali_division_name(zh_hz, en_link_line, type_str)

        # সারি পুনর্গঠন
        translated_lines = []
        # ১. বাংলা নাম
        translated_lines.append(f'|{bn_name}')
        # ২. ইংরেজি নাম
        translated_lines.append(en_link_line)
        # ৩. বাকি লাইনগুলো রূপান্তর
        for cl in content_lines[1:]:
            cl_tr = replace_links_in_line(cl)
            cl_tr = translate_table_notes(cl_tr)
            cl_tr = to_bengali_digits(cl_tr)
            translated_lines.append(cl_tr)

        row_content = '\n'.join(translated_lines)
        if style_prefix:
            new_rows.append(f'{style_prefix}\n{row_content}')
        else:
            new_rows.append(row_content)

    return '\n|-'.join(new_rows)

def translate_dissolved_table(table_text: str) -> str:
    """বিলুপ্ত কাউন্টি সারণি অনুবাদ করে।"""
    # হেডার রূপান্তর
    t = table_text
    t = t.replace('!Name', '!বাংলা নাম\n!ইংরেজি নাম')
    t = t.replace('!Chinese', '!চীনা নাম')
    t = t.replace('!Now part of', '!বর্তমানে যে অংশের অন্তর্ভুক্ত')
    t = t.replace('!Prefecture', '!প্রিফেকচার')
    t = t.replace('!Province', '!প্রদেশ')
    t = t.replace('!Type', '!ধরন')
    t = t.replace('!Population (2010 census)', '!জনসংখ্যা ([[Sixth National Population Census of the People\'s Republic of China|২০১০]] আদমশুমারি)')
    t = t.replace('!Year dissolved', '!বিলুপ্তির বছর')

    rows = t.split('\n|-')
    new_rows = [rows[0]]

    for r in rows[1:]:
        lines = [l for l in r.split('\n') if l.strip()]
        if not lines:
            continue

        en_line = lines[0] # |[[Sanshan District]]
        zh_line = lines[1] if len(lines) > 1 else "" # |三山区
        zh_hz = zh_line.strip().lstrip('|').strip()

        bn_name = get_bengali_division_name(zh_hz, en_line, 'District')

        translated_lines = [f'|{bn_name}', en_line]
        for cl in lines[1:]:
            cl_tr = replace_links_in_line(cl)
            cl_tr = translate_table_notes(cl_tr)
            cl_tr = to_bengali_digits(cl_tr)
            translated_lines.append(cl_tr)

        new_rows.append('\n'.join(translated_lines))

    return '\n|-'.join(new_rows)

def translate_renamed_table(table_text: str) -> str:
    """নাম পরিবর্তন সারণি অনুবাদ করে।"""
    t = table_text
    t = t.replace('!Former → Current name', '!পুরাতন→নতুন নাম (বাংলা)\n!পুরাতন→নতুন নাম (ইংরেজি)')
    t = t.replace('!Chinese', '!চীনা নাম')
    t = t.replace('!Prefecture', '!প্রিফেকচার')
    t = t.replace('!Province', '!প্রদেশ')
    t = t.replace('!Type', '!ধরন')

    rows = t.split('\n|-')
    new_rows = [rows[0]]

    for r in rows[1:]:
        lines = [l for l in r.split('\n') if l.strip()]
        if not lines:
            continue

        en_line = lines[0] # |[[Meixian District|Mei(xian) → Meixian]]
        zh_line = lines[1] if len(lines) > 1 else "" # |梅区→梅县区
        zh_hz = zh_line.strip().lstrip('|').strip()

        if '→' in zh_hz:
            parts = zh_hz.split('→')
            bn_former = get_bengali_division_name(parts[0], '', '')
            bn_current = get_bengali_division_name(parts[1], '', '')
            bn_line = f'|{bn_former} → {bn_current}'
        else:
            bn_line = f'|{hanzi_to_bn(zh_hz)}'

        translated_lines = [bn_line, en_line]
        for cl in lines[1:]:
            cl_tr = replace_links_in_line(cl)
            cl_tr = translate_table_notes(cl_tr)
            cl_tr = to_bengali_digits(cl_tr)
            translated_lines.append(cl_tr)

        new_rows.append('\n'.join(translated_lines))

    return '\n|-'.join(new_rows)
