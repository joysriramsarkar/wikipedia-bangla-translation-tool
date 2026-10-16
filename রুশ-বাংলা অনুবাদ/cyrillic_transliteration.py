# -*- coding: utf-8 -*-
"""
রুশ-বাংলা প্রতিবর্ণীকরণ ইঞ্জিন (Russian to Bengali Transliteration Engine)
উইকিপিডিয়া:বাংলা ভাষায় রুশ শব্দের প্রতিবর্ণীকরণ নির্দেশিকা অনুসারে তৈরি।
"""
import re

VOWELS_CYR = set('аеёиоуыэюяАЕЁИОУЫЭЮЯ')

C_BASE = {
    'б': 'ব', 'в': 'ভ', 'г': 'গ', 'д': 'দ', 'ж': 'ঝ', 'з': 'য',
    'й': 'য়', 'к': 'ক', 'л': 'ল', 'м': 'ম', 'н': 'ন', 'п': 'প',
    'р': 'র', 'с': 'স', 'т': 'ত', 'ф': 'ফ', 'х': 'খ', 'ц': 'ৎস',
    'ч': 'চ', 'ш': 'শ', 'щ': 'শ্চ',
}

CONSONANT_CLUSTERS = {
    'кр': 'ক্র', 'бр': 'ব্র', 'гр': 'গ্র', 'пр': 'প্র', 'тр': 'ত্র', 'др': 'দ্র', 'фр': 'ফ্র',
    'хр': 'খ্র', 'вр': 'ভ্র',
    'кл': 'ক্ল', 'бл': 'ব্ল', 'гл': 'গ্ল', 'пл': 'প্ল', 'фл': 'ফ্ল', 'вл': 'ভ্ল',
    'ск': 'স্ক', 'ст': 'স্ত', 'сп': 'স্প', 'кт': 'ক্ত', 'пт': 'প্ত',
    'хт': 'খত', 'зд': 'যদ', 'зв': 'যভ', 'см': 'স্ম', 'сн': 'স্ন',
}

DIPHTHONGS = {
    'ай': 'াই', 'ей': 'েই', 'ой': 'োই', 'уй': 'ুই', 'ий': 'ি', 'ый': 'ি',
}

INITIAL_DIPHTHONGS = {
    'ай': 'আই', 'ей': 'এই', 'ой': 'ওই', 'уй': 'উই',
}

INITIAL_VOWEL_MAP = {
    'а': 'আ', 'е': 'ইয়ে', 'ё': 'ইয়ো', 'и': 'ই', 'о': 'ও',
    'у': 'উ', 'ы': 'ই', 'э': 'এ', 'ю': 'ইউ', 'я': 'ইয়া',
}

DEP_VOWEL_MAP = {
    'а': 'া',
    'е': 'ে',
    'ё': 'ো',
    'и': 'ি',
    'о': 'ো',
    'у': 'ু',
    'ы': 'ি',
    'э': 'ে',
    'ю': 'িউ',
    'я': 'িয়া',
}

def cyrillic_to_bengali(text: str) -> str:
    """সিরিলীয় রুশ শব্দ বা বাক্যাংশকে বাংলায় প্রতিবর্ণীকরণ করে।"""
    w = text.strip()
    if not w:
        return ""

    is_district = False
    if w.endswith(' район') or w.endswith(' Район'):
        w = re.sub(r'\s+[рР]айон$', '', w)
        is_district = True
    elif w.lower().startswith('район '):
        w = re.sub(r'^[рР]айон\s+', '', w)
        is_district = True

    w_lower = w.lower()
    n = len(w_lower)
    res = []
    i = 0

    while i < n:
        # ১. বিশেষ চার-বর্ণের প্রত্যয় (adjectival endings)
        if w_lower[i:i+4] == 'ский':
            res.append('স্কি')
            i += 4
            continue
        elif w_lower[i:i+4] == 'ская':
            res.append('স্কায়া')
            i += 4
            continue
        elif w_lower[i:i+4] == 'ское':
            res.append('স্কোয়ে')
            i += 4
            continue
        elif w_lower[i:i+4] == 'ской':
            res.append('স্কোই')
            i += 4
            continue

        # ২. দ্বিস্বরধ্বনি (Diphthongs with й)
        if i + 1 < n and w_lower[i:i+2] in DIPHTHONGS:
            pair = w_lower[i:i+2]
            is_initial = (i == 0) or (w_lower[i-1] in [' ', '-'])
            if is_initial and pair in INITIAL_DIPHTHONGS:
                res.append(INITIAL_DIPHTHONGS[pair])
            else:
                res.append(DIPHTHONGS[pair])
            i += 2
            continue

        # ৩. পাশাপাশি স্বরধ্বনি (Vowel hiatus)
        if i + 1 < n and w_lower[i] == 'и' and w_lower[i+1] == 'а':
            res.append('িয়া')
            i += 2
            continue
        if i + 1 < n and w_lower[i] == 'и' and w_lower[i+1] == 'е':
            res.append('িয়ে')
            i += 2
            continue
        if i + 1 < n and w_lower[i] == 'а' and w_lower[i+1] == 'е':
            res.append('ায়ে')
            i += 2
            continue

        # ৪. যুক্তব্যঞ্জন (Consonant clusters)
        if i + 1 < n and w_lower[i:i+2] in CONSONANT_CLUSTERS:
            cluster = CONSONANT_CLUSTERS[w_lower[i:i+2]]
            res.append(cluster)
            i += 2
            continue

        ch = w_lower[i]

        # ৫. নরম/কঠিন চিহ্ন (Soft / hard signs)
        if ch == 'ь' or ch == 'ъ':
            if i + 1 < n and w_lower[i+1] in VOWELS_CYR:
                nxt_v = w_lower[i+1]
                soft_vowels = {
                    'е': 'িয়ে', 'ё': 'িয়ো', 'я': 'িয়া', 'ю': 'িউ',
                    'и': 'ি', 'а': 'িয়া', 'о': 'িয়ো', 'у': 'িউ', 'э': 'িয়ে'
                }
                res.append(soft_vowels.get(nxt_v, INITIAL_VOWEL_MAP.get(nxt_v, '')))
                i += 2
                continue
            i += 1
            continue

        # ৬. স্বরবর্ণ (Vowels)
        if ch in VOWELS_CYR:
            is_initial = (i == 0) or (w_lower[i-1] in VOWELS_CYR) or (w_lower[i-1] in [' ', '-', 'ъ', 'ь'])
            if is_initial:
                res.append(INITIAL_VOWEL_MAP.get(ch, ''))
            else:
                res.append(DEP_VOWEL_MAP.get(ch, ''))
            i += 1
            continue

        # ৭. ব্যঞ্জনবর্ণ (Consonants)
        if ch in C_BASE:
            res.append(C_BASE[ch])
            i += 1
            continue

        res.append(ch)
        i += 1

    out = ''.join(res)
    # ধ্বনিতাত্ত্বিক সমন্বয়
    out = out.replace('োস্কি', 'স্কি')
    out = out.replace('াাস্কি', 'াস্কি')
    out = out.replace('িয়োস্কি', 'স্কি')
    out = out.replace('্ ', ' ')
    out = out.replace('াা', 'া')
    out = out.replace('িি', 'ি')
    out = out.replace('েে', 'ে')

    if is_district:
        out += ' জেলা'
    return out

def romanized_russian_to_bengali(name: str) -> str:
    """রোমানীয়/ইংরেজি অক্ষরের রুশ ভৌগোলিক নামকে বাংলায় রূপান্তর করে।"""
    s = name.strip()
    if not s:
        return ""
    
    clean = re.sub(r',\s*[^)]+$', '', s)
    clean = re.sub(r'\s*\([^)]+\)', '', clean)
    clean = clean.strip()
    
    w_lower = clean.lower()
    res = []
    i = 0
    n = len(w_lower)

    REPLACEMENTS = [
        ('shch', 'শ্চ'),
        ('kh', 'খ'),
        ('ts', 'ৎস'),
        ('ch', 'চ'),
        ('sh', 'শ'),
        ('zh', 'ঝ'),
        ('sky', 'স্কি'),
        ('skaya', 'স্কায়া'),
        ('skoye', 'স্কোয়ে'),
        ('skoy', 'স্কোই'),
        ('ovsk', 'োভস্ক'),
        ('yevo', 'য়েভো'),
        ('evo', 'য়েভো'),
        ('ovo', 'োভো'),
        ('kr', 'ক্র'),
        ('br', 'ব্র'),
        ('gr', 'গ্র'),
        ('pr', 'প্র'),
        ('tr', 'ত্র'),
        ('dr', 'দ্র'),
        ('fr', 'ফ্র'),
        ('kl', 'ক্ল'),
        ('bl', 'ব্ল'),
        ('gl', 'গ্ল'),
        ('pl', 'প্ল'),
        ('fl', 'ফ্ল'),
        ('sk', 'স্ক'),
        ('st', 'স্ত'),
        ('sp', 'স্প'),
        ('kt', 'ক্ত'),
        ('ay', 'াই'),
        ('ey', 'েই'),
        ('oy', 'োই'),
        ('uy', 'ুই'),
        ('iy', 'ি'),
        ('yy', 'ি'),
        ('ya', 'িয়া'),
        ('ye', 'িয়ে'),
        ('yo', 'িয়ো'),
        ('yu', 'িউ'),
        ('ia', 'িয়া'),
        ('ie', 'িয়ে'),
        ('io', 'িয়ো'),
        ('iu', 'িউ'),
    ]

    C_MAP = {
        'b': 'ব', 'v': 'ভ', 'g': 'গ', 'd': 'দ', 'z': 'য',
        'k': 'ক', 'l': 'ল', 'm': 'ম', 'n': 'ন', 'p': 'প',
        'r': 'র', 's': 'স', 't': 'ত', 'f': 'ফ', 'h': 'হ',
        'c': 'ক', 'j': 'ঝ', 'w': 'ভ', 'x': 'ক্স', 'q': 'ক',
    }

    V_MAP_INIT = {
        'a': 'আ', 'e': 'ইয়ে', 'i': 'ই', 'o': 'ও', 'u': 'উ', 'y': 'ই',
    }

    V_MAP_DEP = {
        'a': 'া', 'e': 'ে', 'i': 'ি', 'o': 'ো', 'u': 'ু', 'y': 'ি',
    }

    while i < n:
        matched = False
        for pat, bn in REPLACEMENTS:
            if w_lower[i:i+len(pat)] == pat:
                if pat in ['ya', 'ye', 'yo', 'yu', 'ia', 'ie', 'io', 'iu', 'ay', 'ey', 'oy', 'uy']:
                    is_init = (i == 0) or (w_lower[i-1] in [' ', '-'])
                    if is_init:
                        init_map = {
                            'ya': 'ইয়া', 'ye': 'ইয়ে', 'yo': 'ইয়ো', 'yu': 'ইউ',
                            'ia': 'ইয়া', 'ie': 'ইয়ে', 'io': 'ইয়ো', 'iu': 'ইউ',
                            'ay': 'আই', 'ey': 'এই', 'oy': 'ওই', 'uy': 'উই'
                        }
                        res.append(init_map.get(pat, bn))
                    else:
                        res.append(bn)
                else:
                    res.append(bn)
                i += len(pat)
                matched = True
                break
        if matched:
            continue

        ch = w_lower[i]

        if ch in V_MAP_INIT:
            is_init = (i == 0) or (w_lower[i-1] in ['a', 'e', 'i', 'o', 'u', 'y', ' ', '-'])
            if is_init:
                res.append(V_MAP_INIT[ch])
            else:
                res.append(V_MAP_DEP[ch])
            i += 1
            continue

        if ch in C_MAP:
            res.append(C_MAP[ch])
            i += 1
            continue

        res.append(ch)
        i += 1

    out = ''.join(res)
    out = out.replace('োস্কি', 'স্কি')
    out = out.replace('াাস্কি', 'াস্কি')
    out = out.replace('্ ', ' ')
    out = out.replace('াা', 'া')
    out = out.replace('িি', 'ি')
    out = out.replace('েে', 'ে')
    return out

def get_bengali_district_name(cyr_text: str = "", en_text: str = "") -> str:
    """সিরিলীয় অথবা ইংরেজি নাম থেকে প্রমিত বাংলা জেলার নাম তৈরি করে।"""
    # যদি সিরিলীয় নাম উপস্থিত থাকে (যেমন: {{lang|ru|Гиагинский район}})
    m = re.search(r'\{\{lang\|ru\|([^}]+)\}\}', cyr_text)
    if m:
        cyr_clean = m.group(1).strip()
        return cyrillic_to_bengali(cyr_clean)
    
    if cyr_text and re.search(r'[\u0400-\u04FF]', cyr_text):
        return cyrillic_to_bengali(cyr_text)

    # অন্যথায় ইংরেজি নাম থেকে
    clean_en = en_text.replace('[', '').replace(']', '').strip()
    if '|' in clean_en:
        clean_en = clean_en.split('|')[0].strip()
    clean_en = re.sub(r'\s+District$', '', clean_en)
    clean_en = re.sub(r',\s*[^)]+$', '', clean_en)
    
    bn_base = romanized_russian_to_bengali(clean_en)
    return f"{bn_base} জেলা"

# সুবিধাজনক এলিয়াস
transliterate_cyrillic = cyrillic_to_bengali
transliterate_russian = cyrillic_to_bengali
