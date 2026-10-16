# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া সারণি ১ ও ২ অনুবাদক
"""
import sys
import os
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from number_converter import to_bengali_digits
from transliteration import hanzi_to_bn, get_bengali_division_name
from links_dictionary import LINK_MAP
from test_cells import split_row_cells, r1, r2
from build_translation_data import get_district_bn, SPECIAL_CITIES
from translate_china_districts import (
    translate_dates, translate_approvals,
    translate_wikilinks_in_text, translate_remarks_and_methods
)

# প্রদেশসমূহের প্রমিত বাংলা নাম ও লিঙ্ক
PROVINCE_MAP = {
    '北京市': ('বেইজিং', 'বেইজিং পৌরসভা'),
    '天津市': ('থিয়েনচিন', 'থিয়েনচিন পৌরসভা'),
    '上海市': ('সাংহাই', 'সাংহাই পৌরসভা'),
    '重庆市': ('ছুংছিং', 'ছুংছিং পৌরসভা'),
    '河北省': ('হেবেই', 'হেবেই প্রদেশ'),
    '山西省': ('শানশি', 'শানশি প্রদেশ'),
    '内蒙古自治区': ('অভ্যন্তরীণ মঙ্গোলিয়া', 'অভ্যন্তরীণ মঙ্গোলিয়া স্বায়ত্তশাসিত অঞ্চল'),
    '辽宁省': ('লিয়াওনিং', 'লিয়াওনিং প্রদেশ'),
    '吉林省': ('চিলিন', 'চিলিন প্রদেশ'),
    '黑龙江省': ('হেইলুংচিয়াং', 'হেইলুংচিয়াং প্রদেশ'),
    '江苏省': ('চিয়াংসু', 'চিয়াংসু প্রদেশ'),
    '浙江省': ('চচিয়াং', 'চচিয়াং প্রদেশ'),
    '安徽省': ('আনহুই', 'আনহুই প্রদেশ'),
    '福建省': ('ফুচিয়ান', 'ফুচিয়ান প্রদেশ'),
    '江西省': ('চিয়াংশি', 'চিয়াংশি প্রদেশ'),
    '山东省': ('শানতুং', 'শানতুং প্রদেশ'),
    '河南省': ('হোনান', 'হোনান প্রদেশ'),
    '湖北省': ('হুবেই', 'হুবেই প্রদেশ'),
    '湖南省': ('হুনান', 'হুনান প্রদেশ'),
    '广东省': ('কুয়াংতুং', 'কুয়াংতুং প্রদেশ'),
    '广西壮族自治区': ('কুয়াংশি', 'কুয়াংশি চুয়াং স্বায়ত্তশাসিত অঞ্চল'),
    '海南省': ('হাইনান', 'হাইনান প্রদেশ'),
    '四川省': ('সিছুয়ান', 'সিছুয়ান প্রদেশ'),
    '贵州省': ('কুয়েইচৌ', 'কুয়েইচৌ প্রদেশ'),
    '云南省': ('ইউন্নান', 'ইউন্নান প্রদেশ'),
    '西藏自治区': ('তিব্বত', 'তিব্বত স্বায়ত্তশাসিত অঞ্চল'),
    '陕西省': ('শাআনশি', 'শাআনশি প্রদেশ'),
    '甘肃省': ('কানসু', 'কানসু প্রদেশ'),
    '青海省': ('ছিংহাই', 'ছিংহাই প্রদেশ'),
    '宁夏回族自治区': ('নিংমিয়া', 'নিংমিয়া হুই স্বায়ত্তশাসিত অঞ্চল'),
    '新疆维吾尔自治区': ('শিনচিয়াং', 'শিনচিয়াং উইগুর স্বায়ত্তশাসিত অঞ্চল'),
}

def extract_cell_attrs(cell):
    """রৌস্প্যান, কোলস্প্যান বা স্টাইল থাকলে পৃথক করে।"""
    cell = cell.strip()
    if '|' in cell and not cell.startswith('[['):
        parts = cell.split('|', 1)
        if any(k in parts[0] for k in ['rowspan', 'colspan', 'style', 'width', 'align']):
            return parts[0].strip() + ' | ', parts[1].strip()
    return '', cell

def translate_district_cell(raw_content):
    """Col 0 (District Name) অনুবাদ করে।"""
    # Look for [[Target|Label]] or [[Target]]
    m = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', raw_content)
    if not m:
        return raw_content

    target = m.group(1).strip()
    label = m.group(2).strip() if m.group(2) else target

    # Check disambiguator in target: e.g. 东城区 (北京市)
    m_dis = re.match(r'^(.*?)\s*\((.*?)\)$', target)
    if m_dis:
        base_t = m_dis.group(1).strip()
        disam = m_dis.group(2).strip()
        disam_bn = SPECIAL_CITIES.get(disam, hanzi_to_bn(disam.replace('市', '').replace('省', '')))
        base_bn = get_district_bn(base_t)
        lbl_bn = get_district_bn(label)
        bn_link = f'[[{base_bn} ({disam_bn})|{lbl_bn}]]'
    else:
        base_bn = get_district_bn(target)
        lbl_bn = get_district_bn(label)
        bn_link = f'[[{base_bn}|{lbl_bn}]]' if lbl_bn != base_bn else f'[[{base_bn}]]'

    hz_display = label if label else target
    return f'{bn_link}<br /><small>{{{{lang|zh-Hans|{hz_display}}}}}</small>'

def translate_city_cell(raw_content):
    """Col 1 in Table 2 (Prefecture City) অনুবাদ করে।"""
    m = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', raw_content)
    if not m:
        return raw_content

    target = m.group(1).strip()
    label = m.group(2).strip() if m.group(2) else target

    bn_target = SPECIAL_CITIES.get(target, hanzi_to_bn(target.replace('市', '')))
    bn_label = SPECIAL_CITIES.get(label, bn_target)
    if not bn_target.endswith('শহর') and not bn_label.endswith('শহর'):
        bn_display = f'{bn_label} শহর'
    else:
        bn_display = bn_label

    return f'[[{bn_target}|{bn_display}]]'

def translate_table(rows, num_cols, t_name):
    """উইকিটেবিলকে বাংলা উইকিপিডিয়া ফরম্যাটে নিখুঁতভাবে অনুবাদ করে।"""
    output_lines = []
    
    if num_cols == 5:
        # Table 1: Direct-Administered
        output_lines.append('{| class="wikitable sortable" style="margin: 1em auto 1em auto; width:90%; font-size:smaller"')
        output_lines.append('|-')
        output_lines.append('! style="width:12%;" | নগর জেলার নাম')
        output_lines.append('! style="width:15%;" | প্রতিষ্ঠার তারিখ')
        output_lines.append('! style="width:28%;" | প্রতিষ্ঠার পদ্ধতি')
        output_lines.append('! style="width:15%;" | সংশ্লিষ্ট অনুমোদন')
        output_lines.append('! style="width:30%;" | মন্তব্য')
    else:
        # Table 2: Prefecture-Level
        output_lines.append('{| class="wikitable sortable" style="margin: 1em auto 1em auto; width:90%; font-size:smaller"')
        output_lines.append('|-')
        output_lines.append('! style="width:12%;" | নগর জেলার নাম')
        output_lines.append('! style="width:12%;" | সংশ্লিষ্ট প্রিফেকচার-স্তরের শহর')
        output_lines.append('! style="width:15%;" | প্রতিষ্ঠার তারিখ')
        output_lines.append('! style="width:23%;" | প্রতিষ্ঠার পদ্ধতি')
        output_lines.append('! style="width:15%;" | সংশ্লিষ্ট অনুমোদন')
        output_lines.append('! style="width:23%;" | মন্তব্য')

    active_spans = [0] * num_cols

    for style, r_lines in rows:
        combined = '\n'.join(r_lines).strip()
        if combined.startswith('!'):
            continue
            
        if 'colspan=' in combined:
            # Province subheader: e.g. | colspan=5 | [[北京市]]（共16个）
            # Reset active spans for new province
            active_spans = [0] * num_cols
            
            m_p = re.search(r'colspan\s*=\s*\d+\s*\|\s*\[\[([^\]]+)\]\](?:（共?(\d+)个）)?', combined)
            if m_p:
                p_zh = m_p.group(1).strip()
                p_count = m_p.group(2)
                p_t, p_lbl = PROVINCE_MAP.get(p_zh, (hanzi_to_bn(p_zh), p_zh))
                count_str = f' (মোট {to_bengali_digits(p_count)}টি)' if p_count else ''
                header_line = f'| colspan={num_cols} | [[{p_t}|{p_lbl}]]{count_str}'
            else:
                header_line = to_bengali_digits(combined)
                
            output_lines.append('|- style="text-align:center; font-weight:bold;"')
            output_lines.append(header_line)
            continue

        # Data row
        cells = split_row_cells(r_lines)
        translated_row_cells = []
        col_idx = 0
        
        for cell in cells:
            while col_idx < num_cols and active_spans[col_idx] > 0:
                col_idx += 1
                
            if col_idx >= num_cols:
                break
                
            attrs, raw_content = extract_cell_attrs(cell)
            m_span = re.search(r'rowspan\s*=\s*(\d+)', attrs)
            span_val = int(m_span.group(1)) if m_span else 1
            active_spans[col_idx] = span_val

            # Translate cell according to logical column
            if col_idx == 0:
                # District Name
                tr_content = translate_district_cell(raw_content)
            elif num_cols == 6 and col_idx == 1:
                # Prefecture City
                tr_content = translate_city_cell(raw_content)
            elif (num_cols == 5 and col_idx == 1) or (num_cols == 6 and col_idx == 2):
                # Date
                tr_content = translate_dates(raw_content)
            elif (num_cols == 5 and col_idx == 3) or (num_cols == 6 and col_idx == 4):
                # Approval
                tr_content = translate_approvals(raw_content)
            else:
                # Method or Notes
                tr_content = translate_remarks_and_methods(raw_content)

            if not tr_content or tr_content.strip() == '':
                tr_content = '&nbsp;'

            # Preserve cell attrs
            cell_str = f'{attrs}{tr_content}' if attrs else tr_content
            translated_row_cells.append(cell_str)
            col_idx += 1

        # Check if remaining unspanned columns in this row need &nbsp;
        while col_idx < num_cols:
            if active_spans[col_idx] == 0:
                translated_row_cells.append('&nbsp;')
            col_idx += 1

        # Decrement spans for next row
        for c in range(num_cols):
            if active_spans[c] > 0:
                active_spans[c] -= 1

        # Assemble row
        output_lines.append('|-')
        row_text = ' || '.join(translated_row_cells)
        output_lines.append(f'| {row_text}')

    output_lines.append('|}')
    return '\n'.join(output_lines)

print('Testing table 1 translation...')
t1_translated = translate_table(r1, 5, 'Table 1')
print(f'Table 1 translated lines: {len(t1_translated.splitlines())}')
print('Sample Table 1 top lines:')
for l in t1_translated.splitlines()[:20]:
    print('  ', l)

print('\nTesting table 2 translation...')
t2_translated = translate_table(r2, 6, 'Table 2')
print(f'Table 2 translated lines: {len(t2_translated.splitlines())}')
print('Sample Table 2 top lines:')
for l in t2_translated.splitlines()[:20]:
    print('  ', l)
