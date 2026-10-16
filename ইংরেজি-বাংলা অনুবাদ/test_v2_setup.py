# -*- coding: utf-8 -*-
import json
import re

# Load CMU
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

TITLE_WORDS_MAP = {
    'the': 'দ্য', 'of': 'অব', 'in': 'ইন', 'to': 'টু', 'a': 'আ', 'an': 'অ্যান',
    'and': 'অ্যান্ড', 'my': 'মাই', 'for': 'ফর', 'on': 'অন', 'with': 'উইথ',
    'as': 'অ্যাজ', 'at': 'অ্যাট', 'by': 'বাই', 'from': 'ফ্রম', 'up': 'আপ',
    'out': 'আউট', 'about': 'অ্যাবাউট', 'into': 'ইনটু', 'through': 'থ্রু',
    'over': 'ওভার', 'after': 'আফটার', 'before': 'বিফোর', 'between': 'বিটুইন',
    'under': 'আন্ডার', 'behind': 'বিহাইন্ড', 'beyond': 'বিয়ন্ড',
    'against': 'অ্যাগেইনস্ট', 'without': 'উইদাউট', 'within': 'উইদিন',
    'during': 'ডিউরিং', 'than': 'দ্যান', 'but': 'বাট', 'or': 'অর',
    'so': 'সো', 'yet': 'ইয়েট', 'not': 'নট', 'no': 'নো', 'never': 'নেভার',
    'always': 'অলওয়েজ', 'all': 'অল', 'any': 'এনি', 'some': 'সাম',
    'every': 'এভরি', 'each': 'ইচ', 'both': 'বোথ', 'few': 'ফিউ',
    'more': 'মোর', 'most': 'মোস্ট', 'other': 'আদার', 'others': 'আদার্স',
    'such': 'সাচ', 'only': 'অনলি', 'own': 'ওন', 'same': 'সেম',
    'too': 'টু', 'very': 'ভেরি', 'just': 'জাস্ট', 'now': 'নাউ',
    'then': 'দেন', 'there': 'দেয়ার', 'here': 'হিয়ার', 'where': 'হোয়ার',
    'when': 'হোয়েন', 'why': 'হোয়াই', 'how': 'হাউ', 'what': 'হোয়াট',
    'who': 'হু', 'whom': 'হুম', 'whose': 'হুজ', 'which': 'হুইচ',
    'this': 'দিস', 'that': 'দ্যাট', 'these': 'দিজ', 'those': 'দোজ',
    'i': 'আই', 'me': 'মি', 'myself': 'মাইসেলফ', 'we': 'উই',
    'us': 'আস', 'our': 'আওয়ার', 'ours': 'আওয়ার্স', 'ourselves': 'আওয়ারসেলভস',
    'you': 'ইউ', 'your': 'ইউর', 'yours': 'ইউরস', 'yourself': 'ইউরসেলফ',
    'yourselves': 'ইউরসেলভস', 'he': 'হি', 'him': 'হিম', 'his': 'হিজ',
    'himself': 'হিমসেলফ', 'she': 'শি', 'her': 'হার', 'hers': 'হার্স',
    'herself': 'হারসেলফ', 'it': 'ইট', 'its': 'ইটস', 'itself': 'ইটসেলফ',
    "it's": 'ইটস', 'they': 'দে', 'them': 'দেম', 'their': 'দেয়ার',
    'theirs': 'দেয়ার্স', 'themselves': 'দেমসেলভস', 'one': 'ওয়ান',
    'two': 'টু', 'three': 'থ্রি', 'four': 'ফোর', 'five': 'ফাইভ',
    'six': 'সিক্স', 'seven': 'সেভেন', 'eight': 'এইট', 'nine': 'নাইন',
    'ten': 'টেন', 'first': 'ফার্স্ট', 'second': 'সেকেন্ড', 'third': 'থার্ড',
    'fourth': 'ফোর্থ', 'fifth': 'ফিফথ', 'last': 'লাস্ট', 'is': 'ইজ',
    'am': 'অ্যাম', 'are': 'আর', 'was': 'ওয়াজ', 'were': 'ওয়ার',
    'be': 'বি', 'been': 'বিন', 'being': 'বিয়িং', "bein'": 'বিয়িং',
    'have': 'হ্যাভ', 'has': 'হ্যাস', 'had': 'হ্যাড', 'having': 'হ্যাভিং',
    'do': 'ডু', 'does': 'ডাজ', 'did': 'ডিড', 'doing': 'ডুইং', 'done': 'ডান',
    'can': 'ক্যান', 'could': 'কুড', 'will': 'উইল', 'would': 'উড',
    'shall': 'শ্যাল', 'should': 'শুড', 'may': 'মে', 'might': 'মাইট',
    'must': 'মাস্ট', "don't": 'ডোন্ট', "doesn't": 'ডাজন্ট', "didn't": 'ডিডন্ট',
    "won't": 'ওয়োন্ট', "can't": 'ক্যান্ট', "couldn't": 'কুডন্ট',
    "i'm": "আই'ম", "i've": "আই'ভ", "i'll": "আই'ল", "i'd": "আই'ড",
    "you're": "ইউ'র", "you've": "ইউ'ভ", "we're": "উই'র", "they're": "দে'র",
    
    # User examples & key terms
    'causes': 'কজেস', 'cancer': 'ক্যানসার', 'schmancer': 'শ্ম্যান্সার',
    'bigger': 'বিগার', 'better': 'বেটার', 'hitler': 'হিটলার', 'christ': 'ক্রাইস্ট',
    'chong': 'চং', 'meditations': 'মেডিটেশনস', 'joint': 'জয়েন্ট',
    'died': 'ডায়েড', 'prison': 'প্রিজন', 'notes': 'নোটস',
    'clinging': 'ক্লিঙিং', 'wreckage': 'রেকেজ', 'part': 'পার্ট',
    'lives': 'লাইভস', 'bengal': 'বেঙ্গল', 'lancer': 'ল্যান্সার',
    'fighter': 'ফাইটার', 'finland': 'ফিনল্যান্ড',
    'operation': 'অপারেশন', 'overflight': 'ওভারফ্লাইট', 'spy': 'স্পাই',
    'pilot': 'পাইলট', 'tells': 'টেলস', 'story': 'স্টোরি',
    'time': 'টাইম', 'easy': 'ইজি', 'lifetime': 'লাইফটাইম',
    'respect': 'রেসপেক্ট', 'plenty': 'প্লেন্টি', 'sex': 'সেক্স',
    'drugs': 'ড্রাগস', 'hollywood': 'হলিউড', 'u-2': 'ইউ-২',
    'published': 'প্রকাশিত', 'posthumously': 'মরণোত্তর'
}

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
            
            if base_p == 'R' and i + 1 < n and not is_v(phonemes[i+1]):
                c2 = re.sub(r'\d', '', phonemes[i+1])
                res += 'র্' + C_MAP.get(c2, '')
                i += 2
                continue
                
            if base_p == 'NG':
                if i + 1 < n and is_v(phonemes[i+1]):
                    v_next = get_v(phonemes[i+1])
                    res += 'ঙ্গ' + V_SIGN.get(v_next, '')
                    i += 2
                else:
                    res += 'ং'
                    i += 1
                continue
                
            if base_p == 'W' and i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += 'ওয়া' if v_next in ['AA', 'AE', 'AH'] else ('ওয়ে' if v_next in ['EH', 'EY'] else 'উই')
                i += 2
                continue
                
            c_char = C_MAP.get(base_p, '')
            if i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += c_char + V_SIGN.get(v_next, '')
                i += 2
            else:
                res += c_char
                i += 1
    return res

def transliterate_title_word(w):
    if not w:
        return ''
    w_clean = w.strip()
    low = w_clean.lower()
    
    # Check manual map
    if low in TITLE_WORDS_MAP:
        return TITLE_WORDS_MAP[low]
    
    # Check digits
    if re.match(r'^\d+$', w_clean):
        digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
        return ''.join(digits.get(d, d) for d in w_clean)
    
    # Check CMU
    if low in cmu:
        return arpabet_to_bn(cmu[low])
        
    return w_clean

def transliterate_title_phrase(phrase):
    # Handle U-2 or similar
    phrase = re.sub(r'\bU-2\b', 'ইউ-২', phrase)
    
    # Split on whitespace and punctuation, but preserve internal apostrophes like It's, don't, I'm
    tokens = re.split(r'(\s+|[.,:;!?\(\)\"–—]|(?<!\w)\'|\'(?!\w))', phrase)
    out = []
    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,:;!?\(\)\"–—\']+$', t):
            out.append(t)
        else:
            out.append(transliterate_title_word(t))
    return ''.join(out)

# Test user examples
test_phrases = [
    "It's Not Easy Being Me: a Lifetime of No Respect But Plenty of Sex and Drugs",
    "Hollywood Causes Cancer",
    "Bigger than Hitler – Better than Christ",
    "The I Chong: Meditations From the Joint",
    "The Man Died: Prison Notes",
    "Clinging to the Wreckage: A Part of Life",
    "The Lives of a Bengal Lancer",
    "Fighter Over Finland",
    "Operation Overflight: The U-2 Spy Pilot Tells His Story for the First Time"
]

print("=== TRANSLITERATION TEST ===")
for p in test_phrases:
    res = transliterate_title_phrase(p)
    print(f"EN: {p}")
    print(f"BN: {res}\n")
