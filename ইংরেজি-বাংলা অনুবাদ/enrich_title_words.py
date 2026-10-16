# -*- coding: utf-8 -*-
import json

with open('title_words_final.json', encoding='utf-8') as f:
    tw = json.load(f)

MORE = {
    'audacity': 'অডাসিটি', 'hope': 'হোপ', 'anchorwoman': 'অ্যাঙ্করওম্যান',
    'atomic': 'অ্যাটমিক', 'attitude': 'অ্যাটিটিউড', 'attraction': 'অ্যাট্রাকশন',
    'attractions': 'অ্যাট্রাকশনস', 'astronaut': 'অ্যাস্ট্রোনট', 'astronauts': 'অ্যাস্ট্রোনটস',
    "astronaut's": 'অ্যাস্ট্রোনটস', 'armageddon': 'আর্মাগেডন', 'adams': 'অ্যাডামস',
    'above': 'অ্যাবাভ', 'across': 'অ্যাক্রস', 'according': 'অ্যাকর্ডিং',
    'appearance': 'অ্যাপিয়ারেন্স', 'andrew': 'অ্যান্ড্রু', 'augustine': 'অগাস্টিন',
    'alice': 'অ্যালিস', 'angelou': 'অ্যাঞ্জেলো', 'becoming': 'বিকামিং',
    'permanent': 'পার্মানেন্ট', 'record': 'রেকর্ড', 'unauthorised': 'আনঅথোরাইজড',
    'unauthorized': 'আনঅথোরাইজড', 'pilgrim': 'পিলগ্রিম', 'visa': 'ভিসা',
    'waiting': 'ওয়েটিং', 'atheist': 'অ্যাথিস্ট', 'wins': 'উইনস',
    'freedom': 'ফ্রিডম', 'unfinished': 'আনফিনিশড', 'memoirs': 'মেমোয়ার্স',
    'confessions': 'কনফেশনস', 'apology': 'অ্যাপোলজি', 'autobiography': 'অটোবায়োগ্রাফি',
    'memoir': 'মেমোয়ার', 'diary': 'ডায়েরি', 'life': 'লাইফ', 'story': 'স্টোরি',
    'joking': 'জোকিং', 'surely': 'সিওরলি', 'enemy': 'এনিমি', 'coast': 'কোস্ট',
    'ahead': 'অ্যাহেড', 'panzer': 'প্যানজার', 'leader': 'লিডার', 'personal': 'পার্সোনাল',
    'narrative': 'ন্যারেটিভ', 'american': 'আমেরিকান', 'slave': 'স্লেভ',
    'pillow': 'পিলো', 'book': 'বুক', 'girlhood': 'গার্লহুড', 'gusty': 'গাস্টি',
    'wind': 'উইন্ড', 'dark': 'ডার্ক', 'days': 'ডেস', 'nothing': 'নাথিং'
}

for k, v in MORE.items():
    tw[k] = v

with open('title_words_final.json', 'w', encoding='utf-8') as f:
    json.dump(tw, f, ensure_ascii=False, indent=2)

print('Updated title_words_final.json. Total words:', len(tw))
