# -*- coding: utf-8 -*-
"""
চীনা-বাংলা প্রতিবর্ণীকরণ ইঞ্জিন (Chinese to Bengali Transliteration Engine)
pypinyin এবং উইকিপিডিয়ার প্রমিত ফিনিন রূপান্তর নীতির ভিত্তিতে তৈরি।
"""
import re
from pypinyin import pinyin, Style
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from pinyin_table import FULL_PINYIN_MAP

# চীনের জাতিগোষ্ঠীর বাংলা রূপান্তর মানচিত্র
ETHNIC_MAP = {
    '土家族': 'থুচিয়া',
    '苗族': 'মিয়াও',
    '回族': 'হুই',
    '蒙古族': 'মঙ্গোলীয়',
    '哈萨克族': 'কাজাখ',
    '侗族': 'তুং',
    '布依族': 'পুয়েই',
    '瑶族': 'ইয়াও',
    '白族': 'পাই',
    '哈尼族': 'হানি',
    '黎族': 'লি',
    '傣族': 'তাই',
    '畲族': 'শে',
    '傈僳族': 'লিসু',
    '佤族': 'ভা',
    '拉祜族': 'লাহু',
    '水族': 'শুই',
    '东乡族': 'তুংশিয়াং',
    '纳西族': 'নাশি',
    '土族': 'থু',
    '羌族': 'ছিয়াং',
    '仫佬族': 'মুলাও',
    '锡伯族': 'শিবে',
    '撒拉族': 'সালার',
    '毛南族': 'মাওনান',
    '仡佬族': 'গেলাও',
    '塔吉克族': 'তাজিক',
    '普米族': 'ফুমি',
    '怒族': 'নু',
    '独龙族': 'দেরুং',
    '裕固族': 'ইউগুর',
    '鄂伦春族': 'ওরোকেন',
    '达斡尔族': 'দাউর',
    '鄂温克族': 'এভেন্ক',
    '满族': 'মাঞ্চু',
    '朝鲜族': 'কোরীয়',
    '藏族': 'তিব্বতি',
}

# বিশেষ বা বহুল প্রচলিত ব্যতিক্রমী নামের রূপান্তর তালিকা
KNOWN_SPECIAL_NAMES = {
    'Kinmen': 'কিনমেন কাউন্টি',
    'Kinmen County': 'কিনমেন কাউন্টি',
    'Hualien County': 'হুয়ালিয়েন কাউন্টি',
    'Hualian County': 'হুয়ালিয়েন কাউন্টি',
    'Chiayi County': 'চিয়াই কাউন্টি',
    'Jiayi County': 'চিয়াই কাউন্টি',
    'Miaoli County': 'মিয়াওলি কাউন্টি',
    'Nantou County': 'নান্তৌ কাউন্টি',
    'Penghu': 'পেংহু কাউন্টি',
    'Penghu County': 'পেংহু কাউন্টি',
    'Pingtung County': 'পিংতুং কাউন্টি',
    'Pingdong County': 'পিংতুং কাউন্টি',
    'Taitung County': 'তাইতুং কাউন্টি',
    'Taidong County': 'তাইতুং কাউন্টি',
    'Hsinchu County': 'সিনচু কাউন্টি',
    'Xinzhu County': 'সিনচু কাউন্টি',
    'Yilan County': 'ইলান কাউন্টি',
    'Yunlin County': 'ইউনলিন কাউন্টি',
    'Changhua County': 'চাংহুয়া কাউন্টি',
    'Zhanghua County': 'চাংহুয়া কাউন্টি',
    'Ürümqi': 'উরুমছি',
    'Ürümqi County': 'উরুমছি কাউন্টি',
    'Darhan Muminggan United': 'দারহান মুমিংগান সম্মিলিত ব্যানার',
    'Darhan Muminggan United Banner': 'দারহান মুমিংগান সম্মিলিত ব্যানার',
    'Songling District': 'সংলিং জেলা',
    'Xinlin District': 'শিনলিন জেলা',
    'Huzhong District': 'হুচুং জেলা',
    'Xinshi District, Ürümqi': 'শিনশি জেলা',
}

def pinyin_to_bn(pinyin_syllable: str) -> str:
    """একটি একক ফিনিন সিলেবলকে প্রমিত বাংলায় রূপান্তর করে।"""
    s = pinyin_syllable.strip().lower()
    return FULL_PINYIN_MAP.get(s, s)

def hanzi_to_bn(hanzi_str: str) -> str:
    """যেকোনো চীনা হানজি (Hanzi) টেক্সটকে প্রমিত বাংলায় প্রতিবর্ণীকরণ করে।"""
    if not hanzi_str:
        return ""
    # pypinyin এর মাধ্যমে ফিনিনে রূপান্তর
    py = pinyin(hanzi_str, style=Style.NORMAL)
    syls = [p[0].lower() for p in py]
    bn_parts = [FULL_PINYIN_MAP.get(s, s) for s in syls]
    return ''.join(bn_parts)

def clean_hanzi_division(hz: str) -> str:
    """উইকি সিনট্যাক্স থেকে চীনা নাম পরিষ্কার করে।"""
    m = re.search(r'\{\{lang\|zh\|([^}]+)\}\}', hz)
    if m:
        hz = m.group(1)
    return hz.strip().replace('\n', '').lstrip('|').strip()

def get_bengali_division_name(hz: str, en_link: str = "", type_str: str = "") -> str:
    """
    চীনা প্রশাসনিক উপবিভাগের পূর্ণ বাংলা নাম প্রস্তুত করে।
    (যেমন: 瑶海区 -> ইয়াওহাই জেলা, 肥东县 -> ফেইতুং কাউন্টি, 巢湖市 -> ছাওহু শহর)
    """
    clean_en = en_link.replace('|', ' ').replace('[', '').replace(']', '').strip()
    for kn, v in KNOWN_SPECIAL_NAMES.items():
        if kn in en_link or kn in clean_en:
            return v

    hz = clean_hanzi_division(hz)
    if hz.endswith('自治旗'):
        base = hz[:-3]
        for eth, eth_bn in ETHNIC_MAP.items():
            if base.endswith(eth):
                p_base = base[:-len(eth)]
                return f'{hanzi_to_bn(p_base)} {eth_bn} স্বায়ত্তশাসিত ব্যানার'
        return f'{hanzi_to_bn(base)} স্বায়ত্তশাসিত ব্যানার'
    elif hz.endswith('自治县'):
        base = hz[:-3]
        for eth, eth_bn in ETHNIC_MAP.items():
            if base.endswith(eth):
                p_base = base[:-len(eth)]
                return f'{hanzi_to_bn(p_base)} {eth_bn} স্বায়ত্তশাসিত কাউন্টি'
        return f'{hanzi_to_bn(base)} স্বায়ত্তশাসিত কাউন্টি'
    elif hz.endswith('联合旗'):
        base = hz[:-3]
        return f'{hanzi_to_bn(base)} সম্মিলিত ব্যানার'
    elif hz.endswith('旗'):
        base = hz[:-1]
        return f'{hanzi_to_bn(base)} ব্যানার'
    elif hz.endswith('林区'):
        base = hz[:-2]
        return f'{hanzi_to_bn(base)} বন জেলা'
    elif hz.endswith('特区'):
        base = hz[:-2]
        return f'{hanzi_to_bn(base)} বিশেষ জেলা'
    elif hz.endswith('行政区') or hz.endswith('行政委员会'):
        base = hz[:-3] if hz.endswith('行政区') else hz[:-5]
        return f'{hanzi_to_bn(base)} জেলা'
    elif hz.endswith('区'):
        base = hz[:-1]
        return f'{hanzi_to_bn(base)} জেলা'
    elif hz.endswith('县'):
        base = hz[:-1]
        return f'{hanzi_to_bn(base)} কাউন্টি'
    elif hz.endswith('市'):
        base = hz[:-1]
        return f'{hanzi_to_bn(base)} শহর'
    else:
        if 'County' in type_str:
            return f'{hanzi_to_bn(hz)} কাউন্টি'
        elif 'City' in type_str:
            return f'{hanzi_to_bn(hz)} শহর'
        elif 'Banner' in type_str:
            return f'{hanzi_to_bn(hz)} ব্যানার'
        else:
            return f'{hanzi_to_bn(hz)} জেলা'
