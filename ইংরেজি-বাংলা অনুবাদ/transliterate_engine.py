# -*- coding: utf-8 -*-
import json
import re
import os

# 1. Load CMU Pronouncing Dictionary
cmu = {}
if os.path.exists('cmudict.dict'):
    with open('cmudict.dict', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            parts = line.split()
            word = parts[0].split('(')[0].lower()
            if word not in cmu:
                cmu[word] = parts[1:]

# 2. Arpabet Phoneme Mapping
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
            # Check 2-consonant cluster
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
                
            c_char = C_MAP.get(base_p, '')
            if i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += c_char + V_SIGN.get(v_next, '')
                i += 2
            else:
                res += c_char
                i += 1
    return res

# 3. Comprehensive Title Words Dictionary
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
    
    # Common Nouns & Adjectives in titles
    'life': 'লাইফ', 'lives': 'লাইভস', 'living': 'লিভিং', 'alive': 'অ্যালাইভ',
    'dead': 'ডেড', 'death': 'ডেথ', 'died': 'ডায়েড', 'story': 'স্টোরি',
    'stories': 'স্টোরিজ', 'history': 'হিস্ট্রি', 'memoir': 'মেমোয়ার',
    'memoirs': 'মেমোয়ার্স', 'autobiography': 'অটোবায়োগ্রাফি',
    'biography': 'বায়োগ্রাফি', 'diary': 'ডায়েরি', 'diaries': 'ডায়েরিজ',
    'journal': 'জার্নাল', 'journals': 'জার্নালস', 'confession': 'কনফেশন',
    'confessions': 'কনফেশনস', 'notes': 'নোটস', 'note': 'নোট',
    'letters': 'লেটার্স', 'letter': 'লেটার', 'book': 'বুক', 'books': 'বুকস',
    'time': 'টাইম', 'times': 'টাইমস', 'day': 'ডে', 'days': 'ডেস',
    'night': 'নাইট', 'nights': 'নাইটস', 'morning': 'মর্নিং', 'evening': 'ইভনিং',
    'year': 'ইয়ার', 'years': 'ইয়ার্স', 'world': 'ওয়ার্ল্ড', 'earth': 'আর্থ',
    'sun': 'সান', 'moon': 'মুন', 'star': 'স্টার', 'stars': 'স্টার্স',
    'sky': 'স্কাই', 'skies': 'স্কাইজ', 'sea': 'সি', 'ocean': 'ওশান',
    'river': 'রিভার', 'water': 'ওয়াটার', 'fire': 'ফায়ার', 'air': 'এয়ার',
    'wind': 'উইন্ড', 'rain': 'রেইন', 'storm': 'স্টর্ম', 'cloud': 'ক্লাউড',
    'clouds': 'ক্লাউডস', 'light': 'লাইট', 'dark': 'ডার্ক', 'darkness': 'ডার্কনেস',
    'shadow': 'শ্যাডো', 'shadows': 'শ্যাডোজ', 'sound': 'সাউন্ড', 'sounds': 'সাউন্ডস',
    'silence': 'সাইলেন্স', 'voice': 'ভয়েস', 'voices': 'ভয়েসেস', 'music': 'মিউজিক',
    'song': 'সং', 'songs': 'সংস', 'dance': 'ড্যান্স', 'play': 'প্লে',
    'game': 'গেম', 'games': 'গেমস', 'war': 'ওয়ার', 'warfare': 'ওয়ারফেয়ার',
    'peace': 'পিস', 'battle': 'ব্যাটল', 'fight': 'ফাইট', 'fighting': 'ফাইটিং',
    'fighter': 'ফাইটার', 'flight': 'ফ্লাইট', 'flights': 'ফ্লাইটস', 'fly': 'ফ্লাই',
    'flying': 'ফ্লাইং', 'flew': 'ফ্লু', 'pilot': 'পাইলট', 'pilots': 'পাইলটস',
    "pilot's": 'পাইলটস', 'wing': 'উইং', 'wings': 'উইংস', 'plane': 'প্লেন',
    'airforce': 'এয়ারফোর্স', 'force': 'ফোর্স', 'army': 'আর্মি', 'navy': 'নেভি',
    'military': 'মিলিটারি', 'soldier': 'সোলজার', 'soldiers': 'সোলজার্স',
    'captain': 'ক্যাপ্টেন', 'general': 'জেনারেল', 'colonel': 'কর্নেল',
    'major': 'মেজর', 'admiral': 'অ্যাডমিরাল', 'enemy': 'এনিমি', 'friend': 'ফ্রেন্ড',
    'friends': 'ফ্রেন্ডস', 'love': 'লাভ', 'hate': 'হেট', 'heart': 'হার্ট',
    'soul': 'সোল', 'mind': 'মাইন্ড', 'body': 'বডি', 'blood': 'ব্লাড',
    'man': 'ম্যান', 'men': 'মেন', 'woman': 'ওম্যান', 'women': 'উইমেন',
    'girl': 'গার্ল', 'girls': 'গার্লস', 'boy': 'বয়', 'boys': 'বয়েজ',
    'child': 'চাইল্ড', 'children': 'চিলড্রেন', 'childhood': 'চাইল্ডহুড',
    'father': 'ফাদার', 'mother': 'মাদার', 'brother': 'ব্রাদার', 'sister': 'সিস্টার',
    'son': 'সান', 'daughter': 'ডটার', 'family': 'ফ্যামিলি', 'home': 'হোম',
    'house': 'হাউস', 'street': 'স্ট্রিট', 'road': 'রোড', 'city': 'সিটি',
    'town': 'টাউন', 'country': 'কান্ট্রি', 'land': 'ল্যান্ড', 'god': 'গড',
    'gods': 'গডস', 'lord': 'লর্ড', 'lady': 'লেডি', 'king': 'কিং',
    'queen': 'কুইন', 'prince': 'প্রিন্স', 'princess': 'প্রিন্সেস',
    'angel': 'অ্যাঞ্জেল', 'angels': 'অ্যাঞ্জেলস', 'devil': 'ডেভিল',
    'saint': 'সেন্ট', 'secret': 'সিক্রেট', 'secrets': 'সিক্রেটস',
    'truth': 'ট্রুথ', 'true': 'ট্রু', 'lie': 'লাই', 'lies': 'লাইজ',
    'false': 'ফলস', 'right': 'রাইট', 'wrong': 'রং', 'good': 'গুড',
    'bad': 'ব্যাড', 'great': 'গ্রেট', 'little': 'লিটল', 'small': 'স্মল',
    'big': 'বিগ', 'bigger': 'বিগার', 'better': 'বেটার', 'best': 'বেস্ট',
    'worst': 'ওয়ার্স্ট', 'long': 'লং', 'short': 'শর্ট', 'high': 'হাই',
    'low': 'লো', 'deep': 'ডিপ', 'wide': 'ওয়াইড', 'far': 'ফার',
    'near': 'নিয়ার', 'old': 'ওল্ড', 'young': 'ইয়াং', 'new': 'নিউ',
    'free': 'ফ্রি', 'freedom': 'ফ্রিডম', 'wild': 'ওয়াইল্ড', 'lost': 'লস্ট',
    'found': 'ফাউন্ড', 'past': 'পাস্ট', 'future': 'ফিউচার', 'present': 'প্রেজেন্ট',
    'happy': 'হ্যাপি', 'sad': 'স্যাড', 'alone': 'অ্যালোন', 'lonely': 'লোনলি',
    'sweet': 'সুইট', 'bitter': 'বিটার', 'cold': 'কোল্ড', 'hot': 'হট',
    'warm': 'ওয়ার্ম', 'hard': 'হার্ড', 'soft': 'সফট', 'fast': 'ফাস্ট',
    'slow': 'স্লো', 'speed': 'স্পিড', 'walk': 'ওয়াক', 'walking': 'ওয়াকিং',
    'run': 'রান', 'running': 'রানিং', 'stand': 'স্ট্যান্ড', 'fall': 'ফল',
    'rise': 'রাইজ', 'climb': 'ক্লাইম্ব', 'jump': 'জাম্প', 'see': 'সি',
    'look': 'লুক', 'watch': 'ওয়াচ', 'hear': 'হিয়ার', 'listen': 'লিসেন',
    'speak': 'স্পিক', 'talk': 'টক', 'tell': 'টেল', 'tells': 'টেলস',
    'say': 'সে', 'said': 'সেড', 'write': 'রাইট', 'writer': 'রাইটার',
    'read': 'রিড', 'think': 'থিংক', 'thought': 'থট', 'know': 'নো',
    'knew': 'নিউ', 'known': 'নোন', 'feel': 'ফিল', 'dream': 'ড্রিম',
    'dreams': 'ড্রিমস', 'hope': 'হোপ', 'fear': 'ফিয়ার', 'faith': 'ফেইথ',
    'courage': 'কারেজ', 'power': 'পাওয়ার', 'glory': 'গ্লোরি', 'honor': 'অনার',
    'shame': 'শেম', 'pain': 'পেইন', 'joy': 'জয়', 'laugh': 'লাফ',
    'laughter': 'লাফটার', 'cry': 'ক্রাই', 'smile': 'স্মাইল', 'tears': 'টিয়ার্স',
    
    # Specific terms flagged by user
    'causes': 'কজেস', 'cancer': 'ক্যানসার', 'schmancer': 'শ্ম্যান্সার',
    'christ': 'ক্রাইস্ট', 'hitler': 'হিটলার', 'chong': 'চং',
    'meditations': 'মেডিটেশনস', 'joint': 'জয়েন্ট', 'prison': 'প্রিজন',
    'clinging': 'ক্লিঙিং', 'wreckage': 'রেকেজ', 'part': 'পার্ট',
    'bengal': 'বেঙ্গল', 'lancer': 'ল্যান্সার', 'finland': 'ফিনল্যান্ড',
    'operation': 'অপারেশন', 'overflight': 'ওভারফ্লাইট', 'spy': 'স্পাই',
    'easy': 'ইজি', 'lifetime': 'লাইফটাইম', 'respect': 'রেসপেক্ট',
    'plenty': 'প্লেন্টি', 'sex': 'সেক্স', 'drugs': 'ড্রাগস',
    'hollywood': 'হলিউড', 'posthumously': 'মরণোত্তর', 'published': 'প্রকাশিত',
    'u-2': 'ইউ-২', 'chickenhawk': 'চিকেনহক', 'uptown': 'আপটাউন',
    'space': 'স্পেস', 'thunderbolt': 'থান্ডারবোল্ট', 'forever': 'ফরএভার',
    'mission': 'মিশন', 'slide': 'স্লাইড', 'rule': 'রুল', 'engineer': 'ইঞ্জিনিয়ার',
    'central': 'সেন্ট্রাল', 'blue': 'ব্লু', 'black': 'ব্ল্যাক', 'sheep': 'শিপ',
    'chef': 'শেফ', 'marriage': 'ম্যারিজ', 'motherhood': 'মাদারহুড',
    'adventures': 'অ্যাডভেঞ্চার্স', 'eagles': 'ঈগলস', 'answer': 'অ্যানসার',
    'justice': 'জাস্টিস', 'judge': 'জাজ', 'shot': 'শট', 'frontier': 'ফ্রন্টিয়ার',
    'follies': 'ফলিজ', 'middle': 'মিডল', 'nowhere': 'নোহোয়ার'
}

INITIALS = {
    'A.': 'এ.', 'B.': 'বি.', 'C.': 'সি.', 'D.': 'ডি.', 'E.': 'ই.', 'F.': 'এফ.',
    'G.': 'জি.', 'H.': 'এইচ.', 'I.': 'আই.', 'J.': 'জে.', 'K.': 'কে.', 'L.': 'এল.',
    'M.': 'এম.', 'N.': 'এন.', 'O.': 'ও.', 'P.': 'পি.', 'Q.': 'কিউ.', 'R.': 'আর.',
    'S.': 'এস.', 'T.': 'টি.', 'U.': 'ইউ.', 'V.': 'ভি.', 'W.': 'ডব্লিউ.', 'X.': 'এক্স.',
    'Y.': 'ওয়াই.', 'Z.': 'জেড.',
    'A': 'এ.', 'B': 'বি.', 'C': 'সি.', 'D': 'ডি.', 'E': 'ই.', 'F': 'এফ.',
    'G': 'জি.', 'H': 'এইচ.', 'I': 'আই.', 'J': 'জে.', 'K': 'কে.', 'L': 'এল.',
    'M': 'এম.', 'N': 'এন.', 'O': 'ও.', 'P': 'পি.', 'Q': 'কিউ.', 'R': 'আর.',
    'S': 'এস.', 'T': 'টি.', 'U': 'ইউ.', 'V': 'ভি.', 'W': 'ডব্লিউ.', 'X': 'এক্স.',
    'Y': 'ওয়াই.', 'Z': 'জেড.'
}

def transliterate_title_word(w):
    if not w:
        return ''
    w_clean = w.strip()
    low = w_clean.lower()
    
    if low in TITLE_WORDS_MAP:
        return TITLE_WORDS_MAP[low]
        
    if w_clean in INITIALS:
        return INITIALS[w_clean]
        
    if re.match(r'^\d+$', w_clean):
        digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
        return ''.join(digits.get(d, d) for d in w_clean)
        
    if low in cmu:
        return arpabet_to_bn(cmu[low])
        
    # Fallback rule-based
    return transliterate_rule_based(w_clean)

def transliterate_rule_based(w):
    # Rule 4.1: words never start with 'ts' or 'z' -> 'সু'/'স'
    low = w.lower()
    if low.startswith('ts'):
        return 'সু' + transliterate_rule_based(w[2:])
    if low.startswith('z'):
        return 'স' + transliterate_rule_based(w[1:])
    if low.startswith('wr'):
        return 'র' + transliterate_rule_based(w[2:])
    if low.startswith('kn'):
        return 'ন' + transliterate_rule_based(w[2:])
    if low.startswith('ps'):
        return 'স' + transliterate_rule_based(w[2:])
        
    mapping = [
        ('tion', 'শন'), ('sion', 'শন'), ('tch', 'চ'), ('ch', 'চ'),
        ('sh', 'শ'), ('ph', 'ফ'), ('th', 'থ'), ('wh', 'হোয়'),
        ('ck', 'ক'), ('qu', 'ক্ব'), ('gh', 'ঘ'), ('kh', 'খ'),
        ('igh', 'আই'), ('ee', 'ি'), ('oo', 'ু'), ('ea', 'ি'),
        ('ai', 'াই'), ('ay', 'ে'), ('ey', 'ি'), ('oy', 'য়'),
        ('oi', 'য়'), ('ou', 'াউ'), ('au', 'অ'), ('aw', 'অ'),
        ('cl', 'ক্ল'), ('cr', 'ক্র'), ('pl', 'প্ল'), ('pr', 'প্র'),
        ('bl', 'ব্ল'), ('br', 'ব্র'), ('gl', 'গ্ল'), ('gr', 'গ্র'),
        ('fl', 'ফ্ল'), ('fr', 'ফ্র'), ('tr', 'ট্র'), ('dr', 'ড্র'),
        ('sp', 'স্প'), ('st', 'স্ট'), ('sk', 'স্ক'), ('sm', 'স্ম'),
        ('sn', 'স্ন'), ('sl', 'স্ল'),
        ('b', 'ব'), ('c', 'ক'), ('d', 'ড'), ('f', 'ফ'),
        ('g', 'গ'), ('h', 'হ'), ('j', 'জ'), ('k', 'ক'),
        ('l', 'ল'), ('m', 'ম'), ('n', 'ন'), ('p', 'প'),
        ('q', 'ক'), ('r', 'র'), ('s', 'স'), ('t', 'ট'),
        ('v', 'ভ'), ('w', 'উ'), ('x', 'ক্স'), ('y', 'য়'),
        ('z', 'জ'), ('a', 'া'), ('e', 'ে'), ('i', 'ি'),
        ('o', 'ো'), ('u', 'ু')
    ]
    res = ''
    i = 0
    while i < len(low):
        matched = False
        for pat, rep in mapping:
            if low[i:i+len(pat)] == pat:
                res += rep
                i += len(pat)
                matched = True
                break
        if not matched:
            res += low[i]
            i += 1
            
    vowel_initial = {
        'া': 'আ', 'ে': 'এ', 'ি': 'ই', 'ী': 'ঈ', 'ু': 'উ', 'ূ': 'ঊ', 'ো': 'ও', 'ৌ': 'ঔ', 'ৈ': 'ঐ'
    }
    if res and res[0] in vowel_initial:
        res = vowel_initial[res[0]] + res[1:]
    return res

def transliterate_title_phrase(phrase):
    phrase = re.sub(r'\bU-2\b', 'ইউ-২', phrase)
    tokens = re.split(r'(\s+|[.,:;!?\(\)\"–—]|(?<!\w)\'|\'(?!\w))', phrase)
    out = []
    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,:;!?\(\)\"–—\']+$', t):
            out.append(t)
        else:
            out.append(transliterate_title_word(t))
    return ''.join(out)


transliterate_word = transliterate_title_word

if __name__ == "__main__":
    print("transliterate_engine.py ready.")
