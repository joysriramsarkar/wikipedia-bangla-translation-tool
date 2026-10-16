# -*- coding: utf-8 -*-
"""
জাপানি-বাংলা প্রতিবর্ণীকরণ ইঞ্জিন (Japanese to Bengali Transliteration Engine)
উইকিপিডিয়া:বাংলা ভাষায় জাপানি শব্দের প্রতিবর্ণীকরণ (সাহায্য:আধ্বব/জাপানি) নির্দেশিকা অনুসারে গঠিত।
হেপবার্ন, কুন্‌রিয়ে-শিকি এবং নিহোন-শিকি রোমাজিকরণ সমর্থন করে।
"""
import os
import re

# জাপানি কানজি/রোমাজি স্বরধ্বনি ও সিলেবল ম্যাপিং
SYLLABLES = [
    # ১. সংকুচিত ধ্বনি (Youon / 拗音) ও কুন্‌রিয়ে/নিহোন-শিকি রূপ
    ('kya', 'কিয়া'), ('kyu', 'কিউ'), ('kyo', 'কিয়ো'),
    ('gya', 'গিয়া'), ('gyu', 'গিউ'), ('gyo', 'গিয়ো'),
    ('sha', 'শা'), ('shu', 'শু'), ('sho', 'শো'), ('she', 'শে'), ('shi', 'শি'),
    ('sya', 'শা'), ('syu', 'শু'), ('syo', 'শো'), ('si', 'শি'),
    ('cha', 'চা'), ('chu', 'চু'), ('cho', 'চো'), ('che', 'চে'), ('chi', 'চি'),
    ('tya', 'চা'), ('tyu', 'চু'), ('tyo', 'চো'), ('ti', 'চি'), ('tu', 'ৎসু'),
    ('tsu', 'ৎসু'), ('tsa', 'ৎসা'), ('tsi', 'ৎসি'), ('tse', 'ৎসে'), ('tso', 'ৎসো'),
    ('ja', 'জা'), ('ju', 'জু'), ('jo', 'জো'), ('je', 'জে'), ('ji', 'জি'),
    ('zya', 'জা'), ('zyu', 'জু'), ('zyo', 'জো'), ('zi', 'জি'),
    ('di', 'জি'), ('du', 'জু'), ('dza', 'জা'), ('dzu', 'জু'),
    ('nya', 'নিয়া'), ('nyu', 'নিউ'), ('nyo', 'নিয়ো'),
    ('hya', 'হিয়া'), ('hyu', 'হিউ'), ('hyo', 'হিয়ো'),
    ('bya', 'বিয়া'), ('byu', 'বিউ'), ('byo', 'বিয়ো'),
    ('pya', 'পিয়া'), ('pyu', 'পিউ'), ('pyo', 'পিয়ো'),
    ('mya', 'মিয়া'), ('myu', 'মিউ'), ('myo', 'মিয়ো'),
    ('rya', 'রিয়া'), ('ryu', 'রিউ'), ('ryo', 'রিয়ো'),

    # ২. মৌলিক ব্যঞ্জন-স্বর সিলেবল (Gojuon / 五十音)
    ('ka', 'কা'), ('ki', 'কি'), ('ku', 'কু'), ('ke', 'কে'), ('ko', 'কো'),
    ('ga', 'গা'), ('gi', 'গি'), ('gu', 'গু'), ('ge', 'গে'), ('go', 'গো'),
    ('sa', 'সা'), ('su', 'সু'), ('se', 'সে'), ('so', 'সো'),
    ('za', 'জা'), ('zu', 'জু'), ('ze', 'জে'), ('zo', 'জো'),
    ('ta', 'তা'), ('te', 'তে'), ('to', 'তো'),
    ('da', 'দা'), ('de', 'দে'), ('do', 'দো'),
    ('na', 'না'), ('ni', 'নি'), ('nu', 'নু'), ('ne', 'নে'), ('no', 'নো'),
    ('ha', 'হা'), ('hi', 'হি'), ('fu', 'ফু'), ('hu', 'হু'), ('he', 'হে'), ('ho', 'হো'),
    ('ba', 'বা'), ('bi', 'বি'), ('bu', 'বু'), ('be', 'বে'), ('bo', 'বো'),
    ('pa', 'পা'), ('pi', 'পি'), ('pu', 'পু'), ('pe', 'পে'), ('po', 'পো'),
    ('ma', 'মা'), ('mi', 'মি'), ('mu', 'মু'), ('me', 'মে'), ('mo', 'মো'),
    ('ya', 'ইয়া'), ('yu', 'ইউ'), ('yo', 'ইয়ো'),
    ('ra', 'রা'), ('ri', 'রি'), ('ru', 'রু'), ('re', 'রে'), ('ro', 'রো'),
    ('wa', 'ওয়া'), ('wo', 'ও'),

    # ৩. যৌগিক ও একক স্বরধ্বনি
    ('ai', 'আই'), ('ei', 'এই'), ('oi', 'ওই'), ('ui', 'উই'),
    ('a', 'আ'), ('i', 'ই'), ('u', 'উ'), ('e', 'এ'), ('o', 'ও'),
]

TITLES_MAP = {
    'emperor': 'সম্রাট',
    'empress': 'সম্রাজ্ঞী',
    'prince': 'যুবরাজ',
    'princess': 'রাজকুমারী',
    'lord': 'লর্ড',
    'lady': 'লেডি',
    'shogun': 'শোগুন',
    'shōgun': 'শোগুন',
    'shikken': 'শিক্কেন',
    'general': 'জেনারেল',
    'admiral': 'এডমিরাল',
    'colonel': 'কর্নেল',
    'captain': 'ক্যাপ্টেন',
    'major': 'মেজর',
    'dr.': 'ড.',
    'dr': 'ড.',
    'professor': 'অধ্যাপক',
    'sir': 'স্যার',
    'the': 'দ্য',
    'of': 'অব',
    'in': 'ইন',
    'and': 'এবং',
    'to': 'টু',
    'novel': 'উপন্যাস',
    'book': 'বুক',
    'tale': 'টেল',
    'road': 'রোড',
    'narrow': 'ন্যারো',
    'deep': 'ডিপ',
    'north': 'নর্থ',
    'woman': 'উওম্যান',
    'dunes': 'ডিউনস',
    'pillow': 'পিলো',
    'essays': 'এসেস',
    'idleness': 'আইডলনেস',
    'kokoro': 'কোকোরো',
    'no': 'নো',
    'mikoto': 'মিকোতো',
    'sumera': 'সুমেরা',
    'sumera-mikoto': 'সুমেরা-মিকোতো',
    'navy': 'নৌবাহিনী',
    'army': 'সেনাবাহিনী',
    'ldp': 'এলডিপি',
    'dpj': 'ডিপিজে',
    'sdp': 'এসডিপি',
    'sdf': 'এসডিএফ',
    'jsp': 'জেএসপি',
    'pcp': 'পিসিপি',
    'nlc': 'এনএলসি',
    'pnp': 'পিএনপি',
    'ncp': 'এনসিপি',
    'lib.': 'লিব.',
    'lisa': 'লিসা',
}

CHAR_FALLBACK = {
    'b': 'ব', 'c': 'ক', 'd': 'দ', 'f': 'ফ', 'g': 'গ', 'h': 'হ', 'j': 'জ',
    'k': 'ক', 'l': 'ল', 'm': 'ম', 'n': 'ন', 'p': 'প', 'q': 'ক', 'r': 'র',
    's': 'স', 't': 'ত', 'v': 'ভ', 'w': 'ভ', 'x': 'ক্স', 'y': 'য়', 'z': 'জ',
    'a': 'া', 'e': 'ে', 'i': 'ি', 'o': 'ো', 'u': 'ু'
}

def transliterate_japanese_word(w: str) -> str:
    """একটি জাপানি শব্দকে বাংলায় প্রতিবর্ণীকরণ করে। কোনো অবস্থাতেই ইংরেজি হরফ রাখবে না।"""
    if not w:
        return ""

    w_lower = w.lower()

    # পদবি বা ইংরেজি শব্দ ম্যাপিং থাকলে
    if w_lower in TITLES_MAP:
        return TITLES_MAP[w_lower]

    # দীর্ঘস্বর ও বিশেষ চিহ্ন প্রমিতকরণ (Macrons & Circumflexes)
    w_norm = (w_lower.replace('ā', 'a').replace('ī', 'i').replace('ū', 'u')
                     .replace('ē', 'e').replace('ō', 'o')
                     .replace('â', 'a').replace('î', 'i').replace('û', 'u')
                     .replace('ê', 'e').replace('ô', 'o'))

    # বিশেষ পরিচিত জাপানি শব্দ ও নাম
    w_norm = w_norm.replace('honda', 'হোন্ডা')
    w_norm = w_norm.replace('kanda', 'কান্দা')

    # সোকুঅন (দ্বিত্ব ব্যঞ্জনবর্ণ - Sokuon / 促音)
    w_norm = re.sub(r'cch|tch', 'চ্চ', w_norm)
    w_norm = re.sub(r'kk', 'ক্ক', w_norm)
    w_norm = re.sub(r'tt', 'ত্ত', w_norm)
    w_norm = re.sub(r'pp', 'প্প', w_norm)
    w_norm = re.sub(r'ss', 'স্স', w_norm)
    w_norm = re.sub(r'mm', 'ম্ম', w_norm)
    w_norm = re.sub(r'bb', 'ব্ব', w_norm)

    res = []
    i = 0
    n = len(w_norm)

    while i < n:
        # যদি ইতিমধ্যে বাংলা বর্ণ থাকে (সোকুঅন ইত্যাদি থেকে)
        if 0x0980 <= ord(w_norm[i]) <= 0x09FF:
            res.append(w_norm[i])
            i += 1
            continue

        # মোরিক ন (Moraic Nasal / 撥音 - ん)
        if w_norm[i] == 'n' and (i == n - 1 or w_norm[i+1] in "bcdfghjklmnpqrstvwxyz'" or (0x0980 <= ord(w_norm[i+1]) <= 0x09FF)):
            if i + 1 < n and w_norm[i+1] == "'":
                res.append('ন')
                i += 2
                continue
            res.append('ন')
            i += 1
            continue

        # মোরিক ম (p, b, m-এর আগে)
        if w_norm[i] == 'm' and i + 1 < n and w_norm[i+1] in 'bpm':
            res.append('ম')
            i += 1
            continue

        matched = False
        for syl, bn in SYLLABLES:
            l = len(syl)
            if w_norm[i:i+l] == syl:
                if syl in ['a', 'i', 'u', 'e', 'o']:
                    if i > 0 and w_norm[i-1] in 'aiueo':
                        # স্বরধ্বনির পর দ্বিতীয় স্বরধ্বনি (যেমন: Dazai -> দাজাই, Ieyasu -> ইয়েয়াসু)
                        v_map = {'a': 'আ', 'i': 'ই', 'u': 'উ', 'e': 'এ', 'o': 'ও'}
                        res.append(v_map.get(syl, bn))
                    else:
                        res.append(bn)
                elif syl in ['ya', 'yu', 'yo', 'sya', 'syu', 'syo', 'tya', 'tyu', 'tyo']:
                    if i > 0 and not (w_norm[i-1] in ' -'):
                        y_mid = {'ya': 'য়া', 'yu': 'য়ু', 'yo': 'য়ো', 'sya': 'শা', 'syu': 'শু', 'syo': 'শো', 'tya': 'চা', 'tyu': 'চু', 'tyo': 'চো'}
                        res.append(y_mid.get(syl, bn))
                    else:
                        res.append(bn)
                elif syl in ['tsu', 'tu', 'tsa', 'tsi', 'tse', 'tso']:
                    # বাংলায় শব্দের শুরুতে কখনোই 'ৎ' বসে না, উচ্চারণ করা যায় না (যেমন: tsunami -> সুনামি)
                    # শব্দের শুরুতে ts/tu সর্বদা 'সু'/'স' হবে
                    if i == 0 or (i > 0 and w_norm[i-1] in " -/([{\':\"‘“"):
                        ts_init = {'tsu': 'সু', 'tu': 'সু', 'tsa': 'সা', 'tsi': 'সি', 'tse': 'সে', 'tso': 'সো'}
                        res.append(ts_init.get(syl, 'সু'))
                    else:
                        res.append(bn)
                else:
                    res.append(bn)
                i += l
                matched = True
                break

        if not matched:
            # কোনো অবস্থাতেই ইংরেজি বর্ণ সরাসরি যুক্ত করা যাবে না
            c = w_norm[i]
            if c in CHAR_FALLBACK:
                res.append(CHAR_FALLBACK[c])
            elif not c.isascii() or not c.isalpha():
                res.append(c)
            i += 1

    out = ''.join(res)
    # কিছু বিশেষ ধ্বনি বিন্যাস
    out = out.replace('ইএ', 'ইয়ে')
    out = out.replace('আই', 'াই') if len(out) > 3 and out.startswith('কা') else out

    # সর্বশেষ নিরাপত্তা স্তর: কোনো ল্যাটিন বর্ণ থাকলে মুছে ফেলা বা প্রতিস্থাপন
    if re.search(r'[a-zA-Z]', out):
        out = ''.join([CHAR_FALLBACK.get(ch.lower(), '') if ch.isalpha() and ch.isascii() else ch for ch in out])

    # শব্দ শুরুতে বা সীমানায় বাংলায় কখনোই 'ৎ' বসে না (যেমন: tsunami -> সুনামি, Tsunesaburō -> সুনেসাবুরো)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎসু', r'\1সু', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎসা', r'\1সা', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎসি', r'\1সি', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎসে', r'\1সে', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎসো', r'\1সো', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎস', r'\1স', out)
    out = re.sub(r'(^|[^\u0980-\u09FF])ৎ', r'\1স', out)

    return out

def transliterate_japanese_name(name: str) -> str:
    """পূর্ণ জাপানি নাম প্রতিবর্ণীকরণ করে। স্ল্যাশ ও বন্ধনী সুন্দরভাবে পরিচালনা করে।"""
    s = name.strip()
    if not s:
        return ""

    def tr_part(text_part: str) -> str:
        words = text_part.split()
        words_tr = []
        for w in words:
            if '-' in w:
                sub_tr = [transliterate_japanese_word(sw) for sw in w.split('-')]
                words_tr.append('-'.join(sub_tr))
            else:
                words_tr.append(transliterate_japanese_word(w))
        return ' '.join(words_tr)

    # বন্ধনী অংশ সংরক্ষণ ও ভেতরের অংশও অনুবাদ করা
    parts = re.split(r'(\([^)]+\))', s)
    res_parts = []
    for p in parts:
        if p.startswith('(') and p.endswith(')'):
            inner = p[1:-1]
            sub_parts = inner.split('/')
            tr_sub = [tr_part(sp) for sp in sub_parts]
            res_parts.append('(' + '/'.join(tr_sub) + ')')
        else:
            sub_parts = p.split('/')
            tr_sub = [tr_part(sp) for sp in sub_parts]
            res_parts.append('/'.join(tr_sub))

    res = ''.join(res_parts)
    # শব্দ শুরুতে বা সীমানায় বাংলায় কখনোই 'ৎ' বসে না
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎসু', r'\1সু', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎসা', r'\1সা', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎসি', r'\1সি', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎসে', r'\1সে', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎসো', r'\1সো', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎস', r'\1স', res)
    res = re.sub(r'(^|[^\u0980-\u09FF])ৎ', r'\1স', res)
    return res

def get_bengali_japanese_name(link_target: str, link_label: str = "") -> str:
    """উইকিপিডিয়া লিঙ্ক বা লেবেল থেকে প্রমিত বাংলা নাম প্রদান করে। কোনো ল্যাটিন হরফ রাখবে না।"""
    target = link_target.strip()
    label = link_label.strip()

    # ১. যদি লিঙ্ক ডিকশনারি উপস্থিত থাকে
    try:
        dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "links_dictionary.py")
        if os.path.exists(dict_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("ja_links_dict", dict_path)
            if spec and spec.loader:
                _mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(_mod)
                JAPANESE_LINKS_MAP = getattr(_mod, 'JAPANESE_LINKS_MAP', {})
            else:
                JAPANESE_LINKS_MAP = {}
        else:
            JAPANESE_LINKS_MAP = {}

        # সরাসরি লিঙ্ক টার্গেট পরীক্ষা
        if target in JAPANESE_LINKS_MAP:
            return JAPANESE_LINKS_MAP[target]


        # সংখ্যা স্বাভাবিকীকরণ করে পরীক্ষা (ASCII vs Bengali digits)
        target_norm_digits = target.replace('1', '১').replace('2', '২').replace('3', '৩').replace('4', '৪').replace('5', '৫')
        if target_norm_digits in JAPANESE_LINKS_MAP:
            return JAPANESE_LINKS_MAP[target_norm_digits]

        target_ascii_digits = target.replace('১', '1').replace('২', '2').replace('৩', '3').replace('৪', '4').replace('৫', '5')
        if target_ascii_digits in JAPANESE_LINKS_MAP:
            return JAPANESE_LINKS_MAP[target_ascii_digits]

        # নোঙ্গর অংশ (#) বাদ দিয়ে পরীক্ষা
        if '#' in target:
            base = target.split('#')[0].strip()
            if base in JAPANESE_LINKS_MAP:
                return JAPANESE_LINKS_MAP[base]

        # বন্ধনী বাদ দিয়ে পরীক্ষা
        clean_target = re.sub(r'\s*\([^)]+\)', '', target).strip()
        if clean_target in JAPANESE_LINKS_MAP:
            return JAPANESE_LINKS_MAP[clean_target]

        # লেবেল সরাসরি ডিকশনারিতে আছে কিনা পরীক্ষা
        if label and label in JAPANESE_LINKS_MAP:
            return JAPANESE_LINKS_MAP[label]
    except ImportError:
        pass

    # ২. বিশেষ পরিচিত সংক্ষিপ্ত রূপ ও পরিভাষা
    SPECIAL_LABELS = {
        'LDP': 'এলডিপি',
        'DPJ': 'ডিপিজে',
        'SDP': 'এসডিপি',
        'SDF': 'এসডিএফ',
        'JSP': 'জেএসপি',
        'PCP': 'পিসিপি',
        'NLC': 'এনএলসি',
        'PNP': 'পিএনপি',
        'NCP': 'এনসিপি',
        'Lib.': 'লিব.',
        'Navy': 'নৌবাহিনী',
        'Army': 'সেনাবাহিনী',
        'Reshuffle': 'পুনর্গঠিত',
        'Reshuffle 1': '১ম পুনর্গঠন',
        '2': '২য় পুনর্গঠন',
        '3': '৩য় পুনর্গঠন',
        'has been deleted': 'অপসারণ করা হয়েছে',
    }

    if label in SPECIAL_LABELS:
        return SPECIAL_LABELS[label]

    # ৩. মন্ত্রিসভার নাম ও অর্ডিনাল প্যাটার্ন (যেমন: Itō I, Yamagata II, Abe S. III)
    CABINET_ORDINALS = {
        'I': '১ম', 'II': '২য়', 'III': '৩য়', 'IV': '৪র্থ', 'V': '৫ম'
    }

    ord_match = re.match(r'^([A-Za-z\s\.\u0100-\u017F]+?)\s+(I|II|III|IV|V)$', label if label else target)
    if ord_match:
        name_part = ord_match.group(1).strip()
        ord_part = ord_match.group(2)
        bn_ord = CABINET_ORDINALS.get(ord_part, ord_part)
        bn_name = transliterate_japanese_name(name_part)
        return f"{bn_ord} {bn_name}"

    # ৪. অন্যথায় প্রতিবর্ণীকরণ ইঞ্জিন
    text_to_trans = label if label else target

    # টেমপ্লেট থাকলে (যেমন: {{color|...|...}})
    if '{{' in text_to_trans:
        color_match = re.search(r'\{\{color\|([^|]+)\|(.*?)\}\}', text_to_trans)
        if color_match:
            c_code = color_match.group(1)
            inner_text = color_match.group(2)
            # inner_text অনুবাদ করা
            inner_tr = inner_text
            for k, v in SPECIAL_LABELS.items():
                inner_tr = re.sub(rf'\b{re.escape(k)}\b', v, inner_tr)
            inner_tr = transliterate_japanese_name(inner_tr)
            return f"{{{{color|{c_code}|{inner_tr}}}}}"

    clean_text = re.sub(r'\s*\([^)]+\)', '', text_to_trans).strip()
    result = transliterate_japanese_name(clean_text)

    # চূড়ান্ত সুরক্ষা: কোনো ল্যাটিন বর্ণ যেন না থাকে
    if re.search(r'[a-zA-Z]', result):
        result = ''.join([CHAR_FALLBACK.get(ch.lower(), '') if ch.isalpha() and ch.isascii() else ch for ch in result])

    # শব্দ শুরুতে বা সীমানায় বাংলায় কখনোই 'ৎ' বসে না
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎসু', r'\1সু', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎসা', r'\1সা', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎসি', r'\1সি', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎসে', r'\1সে', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎসো', r'\1সো', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎস', r'\1স', result)
    result = re.sub(r'(^|[^\u0980-\u09FF])ৎ', r'\1স', result)

    return result

# সুবিধাজনক এলিয়াস
transliterate_to_bengali = get_bengali_japanese_name
transliterate_japanese = get_bengali_japanese_name
