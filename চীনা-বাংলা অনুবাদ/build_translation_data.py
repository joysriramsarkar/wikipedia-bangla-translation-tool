# -*- coding: utf-8 -*-
"""
Build complete dictionary of all Chinese district names, establishment methods,
approvals, dates, and historical notes.
"""
import re
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from transliteration import hanzi_to_bn, get_bengali_division_name
from links_dictionary import LINK_MAP
from test_cells import r1, r2, split_row_cells
from verify_all_cities import SPECIAL_CITIES

# 1. District names mapping
# Read from চীনের জেলা (বাংলা).txt first for established names
with open('চীনের জেলা (বাংলা).txt', 'r', encoding='utf-8') as f:
    bn_sample = f.read()

pattern = r'\|([^\n\|]+)\n\|\[\[([^\]\n]+)\]\]\s*\n\|\s*(?:\{\{lang\|zh\|)?([^\|\}]+?)(?:\}\})?\s*(?:\|\||\n\|)'
m = re.findall(pattern, bn_sample)
hz_to_bn_district = {}
for bn, en, zh in m:
    hz_to_bn_district[zh.strip()] = bn.strip()

print(f'Loaded {len(hz_to_bn_district)} district names from চীনের জেলা (বাংলা).txt')

# Add special polyphonic or manual overrides
DISTRICT_OVERRIDES = {
    '朝阳区': 'ছাওইয়াং জেলা',
    '长春区': 'ছাংছুন জেলা',
    '长清区': 'ছাংছিং জেলা',
    '黄陂区': 'হুয়াংফি জেলা',
    '番禺区': 'ফানইউ জেলা',
    '六合区': 'লুহে জেলা',
    '竞秀区': 'চিংসিউ জেলা',
    '潞城区': 'লুছেং জেলা',
    '铁锋区': 'থিয়েফেং জেলা',
    '爱辉区': 'আইহুই জেলা',
    '叙州区': 'সিউচৌ জেলা',
    '新市区': 'শিনশি জেলা',
    '管城回族区': 'কুয়ানছেং হুই জেলা',
    '瀍河回族区': 'ছানহে হুই জেলা',
    '顺河回族区': 'শুনহে হুই জেলা',
    '回民区': 'হুইমিন জেলা',
    '梅里斯达斡尔族区': 'মেইরিসি তাউর জেলা',
    '井陉矿区': 'চিংশিং খনি জেলা',
    '鹰手营子矿区': 'ইংশৌইংসি খনি জেলা',
    '贾汪区': 'চিয়াওয়াং জেলা',
    '邗江区': 'হানচিয়াং জেলা',
    '江都区': 'চিয়াংতু জেলা',
    '海陵区': 'হাইলিং জেলা',
    '高港区': 'কাওকাং জেলা',
    '姜堰区': 'চিয়াংইয়েন জেলা',
    '吴江区': 'উচিয়াং জেলা',
    '吴中区': 'উচুং জেলা',
    '相城区': 'শিয়াংছেং জেলা',
    '姑苏区': 'কুসু জেলা',
    '虎丘区': 'হুছিউ জেলা',
    '武进区': 'উচিন জেলা',
    '新北区': 'শিনপেই জেলা',
    '天宁区': 'থিয়েননিং জেলা',
    '钟楼区': 'চুংলৌ জেলা',
    '金坛区': 'চিনথান জেলা',
    '梁溪区': 'লিয়াংশি জেলা',
    '锡山区': 'শিশান জেলা',
    '惠山区': 'হুইশান জেলা',
    '滨湖区': 'পিনহু জেলা',
    '新吴区': 'শিনউ জেলা',
    '玄武区': 'শুয়ানউ জেলা',
    '秦淮区': 'ছিনহুয়াই জেলা',
    '建邺区': 'চিয়েনইয়ে জেলা',
    '鼓楼区': 'কুলৌ জেলা',
    '浦口区': 'ফুখৌ জেলা',
    '栖霞区': 'ছিশিয়া জেলা',
    '雨花台区': 'ইউহুয়াথাই জেলা',
    '江宁区': 'চিয়াংনিং জেলা',
    '溧水区': 'লিশুই জেলা',
    '高淳区': 'কাওছুয়ান জেলা',
}

hz_to_bn_district.update(DISTRICT_OVERRIDES)

def get_district_bn(hz_clean):
    if hz_clean in hz_to_bn_district:
        return hz_to_bn_district[hz_clean]
    # Fallback to get_bengali_division_name
    return get_bengali_division_name(hz_clean)

print("Sample district conversions:")
for test in ['朝阳区', '海淀区', '丰台区', '竞秀区', '井陉矿区', '管城回族区']:
    print(f'  {test} -> {get_district_bn(test)}')
