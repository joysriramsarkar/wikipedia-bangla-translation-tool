# -*- coding: utf-8 -*-
import json
import re

# Load CMU Dict
cmu = {}
with open('cmudict.dict', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith(';'):
            continue
        parts = line.split()
        word = parts[0].split('(')[0].lower()
        if word not in cmu:
            cmu[word] = parts[1:]

VOWELS = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

C_MAP = {
    'B': 'ব', 'CH': 'চ', 'D': 'ড', 'DH': 'দ', 'F': 'ফ', 'G': 'গ', 'HH': 'হ',
    'JH': 'জ', 'K': 'ক', 'L': 'ল', 'M': 'ম', 'N': 'ন', 'NG': 'ং', 'P': 'প',
    'R': 'র', 'S': 'স', 'SH': 'শ', 'T': 'ট', 'TH': 'থ', 'V': 'ভ', 'W': 'উ',
    'Y': 'য়', 'Z': 'জ', 'ZH': 'ঝ'
}

V_INIT = {
    'AA': 'আ', 'AE': 'অ্যা', 'AH': 'আ', 'AO': 'অ', 'AW': 'আউ', 'AY': 'আই',
    'EH': 'এ', 'ER': 'আর', 'EY': 'এ', 'IH': 'ই', 'IY': 'ই', 'OW': 'ও',
    'OY': 'অয়', 'UH': 'উ', 'UW': 'উ'
}

V_SIGN = {
    'AA': 'া', 'AE': '্যা', 'AH': 'া', 'AO': 'ো', 'AW': 'াউ', 'AY': 'াই',
    'EH': 'ে', 'ER': 'ার', 'EY': 'ে', 'IH': 'ি', 'IY': 'ি', 'OW': 'ো',
    'OY': 'য়', 'UH': 'ু', 'UW': 'ু'
}

CONJUNCTS = {
    ('S', 'P'): 'স্প', ('S', 'T'): 'স্ট', ('S', 'K'): 'স্ক', ('S', 'M'): 'স্ম',
    ('S', 'N'): 'স্ন', ('S', 'L'): 'স্ল',
    ('K', 'R'): 'ক্র', ('K', 'L'): 'ক্ল',
    ('P', 'R'): 'প্র', ('P', 'L'): 'প্ল',
    ('B', 'R'): 'ব্র', ('B', 'L'): 'ব্ল',
    ('G', 'R'): 'গ্র', ('G', 'L'): 'গ্ল',
    ('T', 'R'): 'ট্র', ('D', 'R'): 'ড্র',
    ('F', 'R'): 'ফ্র', ('F', 'L'): 'ফ্ল',
    ('N', 'D'): 'ন্ড', ('N', 'T'): 'ন্ট', ('N', 'S'): 'ন্স', ('N', 'JH'): 'ঞ্জ',
    ('L', 'D'): 'ল্ড', ('L', 'T'): 'ল্ট', ('L', 'M'): 'ল্ম',
    ('K', 'T'): 'ক্ট', ('P', 'T'): 'প্ট', ('F', 'T'): 'ফ্ট'
}

def is_v(p):
    return re.sub(r'\d', '', p) in VOWELS

def get_v(p):
    return re.sub(r'\d', '', p)

def arpabet_to_bn(phonemes):
    n = len(phonemes)
    res = ''
    i = 0
    while i < n:
        p = phonemes[i]
        base_p = re.sub(r'\d', '', p)
        if is_v(p):
            v = get_v(p)
            if i == 0 or is_v(phonemes[i-1]):
                res += V_INIT.get(v, '')
            else:
                res += V_SIGN.get(v, '')
            i += 1
        else:
            # Check 2-consonant conjunct
            if i + 1 < n and not is_v(phonemes[i+1]):
                c2 = re.sub(r'\d', '', phonemes[i+1])
                pair = (base_p, c2)
                if pair in CONJUNCTS:
                    conj = CONJUNCTS[pair]
                    if i + 2 < n and is_v(phonemes[i+2]):
                        v_next = get_v(phonemes[i+2])
                        res += conj + V_SIGN.get(v_next, '')
                        i += 3
                        continue
                    else:
                        res += conj
                        i += 2
                        continue
            
            # Reph: R before consonant
            if base_p == 'R' and i + 1 < n and not is_v(phonemes[i+1]):
                c2 = re.sub(r'\d', '', phonemes[i+1])
                res += 'র্' + C_MAP.get(c2, '')
                i += 2
                continue
                
            # NG before vowel -> ঙ্গ, else ং
            if base_p == 'NG':
                if i + 1 < n and is_v(phonemes[i+1]):
                    v_next = get_v(phonemes[i+1])
                    res += 'ঙ্গ' + V_SIGN.get(v_next, '')
                    i += 2
                else:
                    res += 'ং'
                    i += 1
                continue
                
            # W before vowel
            if base_p == 'W' and i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += 'ওয়া' if v_next in ['AA', 'AE', 'AH'] else ('ওয়ে' if v_next in ['EH', 'EY'] else 'উই')
                i += 2
                continue
                
            # Normal consonant
            c_char = C_MAP.get(base_p, '')
            if i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += c_char + V_SIGN.get(v_next, '')
                i += 2
            else:
                res += c_char
                i += 1
    return res

print("Arpabet engine defined successfully.")
