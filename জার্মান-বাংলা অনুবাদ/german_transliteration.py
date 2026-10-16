# -*- coding: utf-8 -*-
"""
জার্মান-বাংলা ধ্বনিতাত্ত্বিক লিপ্যন্তর ইঞ্জিন (German-Bengali Transliteration Engine)
--------------------------------------------------------------------------
জার্মান ভাষার নাম ও পরিভাষা প্রমিত বাংলা লিপ্যন্তরের নিয়ম অনুসরণ করে রূপান্তর করে।
বাধ্যতামূলক নিয়ম: বাংলায় কখনো শব্দ 'ৎ' (খণ্ড-ত) দিয়ে শুরু হতে পারে না;
জার্মান 'Z' দিয়ে শুরু শব্দ সর্বদা 'স' হবে (যেমন: Zimmermann -> সিমারমান)।
"""

import os
import re
import importlib.util

_dict_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "links_dictionary.py")
if os.path.exists(_dict_path):
    _spec = importlib.util.spec_from_file_location("de_links_dict", _dict_path)
    if _spec and _spec.loader:
        _mod = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        DIRECTORS_AND_ACTORS = getattr(_mod, 'DIRECTORS_AND_ACTORS', {})
    else:
        DIRECTORS_AND_ACTORS = {}
else:
    DIRECTORS_AND_ACTORS = {}

FIRST_NAMES = {

    "achim": "আখিম",
    "adolf": "আডলফ",
    "albert": "আলবার্ট",
    "albrecht": "আলব্রেখট",
    "alexander": "আলেকজান্ডার",
    "alexandra": "আলেকজান্দ্রা",
    "alfred": "আলফ্রেড",
    "alice": "অ্যালিস",
    "alina": "আলিনা",
    "amelie": "আমেলি",
    "andre": "আন্দ্রে",
    "andré": "আন্দ্রে",
    "andrea": "আন্দ্রেয়া",
    "andreas": "আন্ড্রেয়াস",
    "angela": "আঞ্জেলা",
    "angelika": "আঞ্জেলিকা",
    "anja": "আনিয়া",
    "ann": "অ্যান",
    "anna": "আনা",
    "anne": "আনে",
    "annette": "অ্যানেট",
    "annika": "আনিকা",
    "anton": "আন্তন",
    "antonia": "আন্তোনিয়া",
    "armin": "আরমিন",
    "arno": "আর্নো",
    "arthur": "আর্থার",
    "astrid": "আস্ট্রিড",
    "august": "আউগুস্ট",
    "axel": "আক্সেল",
    "barbara": "বারবারা",
    "bastian": "বাস্টিয়ান",
    "ben": "বেন",
    "benjamin": "বেনিয়ামিন",
    "benno": "বেনো",
    "bernd": "বার্নড",
    "bernhard": "বার্নহার্ড",
    "bettina": "বেটিনা",
    "bjarne": "বিয়ার্নে",
    "boris": "বরিস",
    "brigitte": "ব্রিগিতে",
    "bruno": "ব্রুনো",
    "burghart": "বুর্খার্ট",
    "carl": "কার্ল",
    "carla": "কার্লা",
    "carlo": "কার্লো",
    "carmen": "কারমেন",
    "carolin": "ক্যারোলিন",
    "caroline": "ক্যারোলিন",
    "carsten": "কার্স্টেন",
    "charlotte": "শার্লট",
    "christian": "ক্রিশ্চিয়ান",
    "christiane": "ক্রিশ্চিয়ানে",
    "christina": "ক্রিস্টিনা",
    "christine": "ক্রিস্টিন",
    "christoph": "ক্রিস্টোফ",
    "christopher": "ক্রিস্টোফার",
    "clara": "ক্লারা",
    "claudia": "ক্লাউদিয়া",
    "claudio": "ক্লাউদিও",
    "claus": "ক্লাউস",
    "clemens": "ক্লেমেন্স",
    "constantin": "কনস্টান্টিন",
    "corinna": "করিনা",
    "cornelia": "কর্নেলিয়া",
    "cosma": "কসমা",
    "dagmar": "দাগমার",
    "daniel": "দানিয়েল",
    "daniela": "দানিয়েলা",
    "david": "ডেভিড",
    "denis": "ডেনিস",
    "dennis": "ডেনিস",
    "detlev": "দেতলেভ",
    "devid": "ডেভিড",
    "diana": "ডায়ানা",
    "dieter": "ডিটার",
    "dietmar": "ডিটমার",
    "dietrich": "ডিট্রিশ",
    "dirk": "ডির্ক",
    "dominik": "ডোমিনিক",
    "doris": "ডরিস",
    "edgar": "এডগার",
    "edith": "এডিথ",
    "elena": "এলেনা",
    "eleonore": "এলেওনোর",
    "elias": "এলিয়াস",
    "elisabeth": "এলিজাবেথ",
    "elmar": "এলমার",
    "elsa": "এলসা",
    "elyas": "ইলিয়াস",
    "emil": "এমিল",
    "emilia": "এমিলিয়া",
    "emily": "এমিলি",
    "emma": "এমা",
    "erich": "এরিখ",
    "erik": "এরিক",
    "erika": "এরিকা",
    "ernst": "আর্নস্ট",
    "erwin": "এরভিন",
    "eva": "ইভা",
    "evelyn": "এভলিন",
    "fabian": "ফাবিয়ান",
    "felicitas": "ফেলিসিতাস",
    "felix": "ফেলিক্স",
    "ferdinand": "ফার্ডিনান্ড",
    "florian": "ফ্লোরিয়ান",
    "frank": "ফ্রাঙ্ক",
    "franz": "ফ্রানৎস",
    "franziska": "ফ্রাঞ্জিস্কা",
    "frauke": "ফ্রোকে",
    "frederick": "ফ্রেডেরিক",
    "friederike": "ফ্রিডরিকে",
    "friedrich": "ফ্রিডরিশ",
    "fritz": "ফ্রিৎস",
    "fritzi": "ফ্রিৎসি",
    "gabriele": "গাব্রিয়েলে",
    "georg": "গেয়র্গ",
    "gerald": "জেরাল্ড",
    "gerd": "গের্ড",
    "gerhard": "গেরহার্ড",
    "gerrit": "গেরিট",
    "gert": "গের্ট",
    "gesine": "গেজিনে",
    "gitta": "গিতা",
    "godehard": "গোডেহার্ড",
    "gottfried": "গটফ্রিড",
    "gotthard": "গটহার্ড",
    "gregor": "গ্রেগর",
    "günter": "গুন্টার",
    "günther": "গুন্থার",
    "gustav": "গুস্তাভ",
    "hanna": "হানা",
    "hannah": "হানা",
    "hannelore": "হানেলোরে",
    "hannes": "হানেস",
    "hans": "হান্স",
    "harald": "হারাল্ড",
    "hartmut": "হার্টমুট",
    "heike": "হাইকে",
    "heiko": "হাইকো",
    "heiner": "হাইনার",
    "heino": "হাইনো",
    "heinrich": "হাইনরিশ",
    "heinz": "হাইন্টৎস",
    "helena": "হেলেনা",
    "helene": "হেলেনে",
    "helga": "হেলগা",
    "helge": "হেলগে",
    "helmut": "হেলমুট",
    "hendrik": "হেন্ড্রিক",
    "henning": "হেনিঙ",
    "henriette": "হেনরিয়েট",
    "henrik": "হেনরিক",
    "henry": "হেনরি",
    "herbert": "হারবার্ট",
    "hermann": "হারমান",
    "hermine": "হারমিনে",
    "hilda": "হিল্ডা",
    "hildegard": "হিল্ডেগার্ড",
    "hilmar": "হিলমার",
    "holger": "হোলগার",
    "horst": "হর্স্ট",
    "hubert": "হুবার্ট",
    "hubertus": "হুবার্তুস",
    "ingo": "ইঙ্গো",
    "inka": "ইনকা",
    "ira": "ইরা",
    "irene": "আইরিন",
    "iris": "আইরিস",
    "isabell": "ইসাবেল",
    "isabella": "ইসাবেলা",
    "jan": "ইয়ান",
    "jana": "ইয়ানা",
    "janin": "ইয়ানিন",
    "janina": "ইয়ানিনা",
    "jannik": "ইয়ানিক",
    "jannis": "ইয়ানিস",
    "jasmin": "ইয়াসমিন",
    "jean": "জঁ",
    "jella": "ইয়েলা",
    "jens": "ইয়েন্স",
    "jessica": "জেসিকা",
    "joachim": "জোয়াখিম",
    "jochen": "ইয়োখেন",
    "johann": "ইয়োহান",
    "johanna": "ইয়োহানা",
    "johannes": "ইয়োহানেস",
    "jonas": "জোনাস",
    "jonathan": "জোনাথন",
    "jordan": "জর্ডান",
    "jördis": "ইয়র্ডিস",
    "jörg": "ইয়র্গ",
    "josef": "ইয়োসেফ",
    "joseph": "জোসেফ",
    "josephine": "জোসেফাইন",
    "judith": "জুডিথ",
    "julia": "জুলিয়া",
    "julian": "জুলিয়ান",
    "juliane": "জুলিয়ানে",
    "julie": "জুলি",
    "julius": "জুলিয়াস",
    "jürgen": "ইয়ুর্গেন",
    "justus": "জুস্টাস",
    "jutta": "জুটা",
    "kai": "কাই",
    "karin": "কারিন",
    "karina": "কারিনা",
    "karl": "কার্ল",
    "karla": "কার্লা",
    "karolin": "ক্যারোলিন",
    "karoline": "ক্যারোলিন",
    "kaspar": "কাসপার",
    "katharina": "কাথারিনা",
    "käthe": "কেথে",
    "katia": "কাটিয়া",
    "katja": "কাটিয়া",
    "katrin": "কাটরিন",
    "ken": "কেন",
    "kerstin": "কার্স্টিন",
    "kilian": "কিলিয়ান",
    "kirsten": "কার্স্টিন",
    "klaus": "ক্লাউস",
    "knut": "কনুট",
    "konrad": "কনরাড",
    "konstantin": "কনস্টান্টিন",
    "korbinian": "কোরবিনিয়ান",
    "kostja": "কস্তিয়া",
    "kristian": "ক্রিশ্চিয়ান",
    "kristina": "ক্রিস্টিনা",
    "kurt": "কুর্ট",
    "lars": "লার্স",
    "laura": "লরা",
    "laurenz": "লরেনৎস",
    "lea": "লিয়া",
    "lena": "লেনা",
    "leo": "লিও",
    "leon": "লেওন",
    "leonard": "লিওনার্ড",
    "leonie": "লেওনি",
    "leopold": "লেওপোল্ড",
    "lilith": "লিলিথ",
    "lina": "লিনা",
    "linda": "লিন্ডা",
    "lisa": "লিসা",
    "liv": "লিভ",
    "lorenz": "লোরেনৎস",
    "lothar": "লোথার",
    "louis": "লুই",
    "louisa": "লুইসা",
    "lucas": "লুকাস",
    "lucie": "লুসি",
    "ludwig": "লুডভিগ",
    "luis": "লুইস",
    "luisa": "লুইসা",
    "luise": "লুইসে",
    "luka": "লুকা",
    "lukas": "লুকাস",
    "lutz": "লুটৎস",
    "madita": "মাদিতা",
    "magdalena": "মাগদালেনা",
    "maik": "মাইক",
    "mandy": "ম্যান্ডি",
    "manfred": "মানফ্রেড",
    "manuel": "ম্যানুয়েল",
    "manuela": "ম্যানুয়েলা",
    "mara": "মারা",
    "marc": "মার্ক",
    "marcel": "মার্সেল",
    "marco": "মার্কো",
    "marcus": "মার্কাস",
    "mareike": "মারাইকে",
    "maren": "মারেন",
    "margarethe": "মার্গারেটে",
    "maria": "মারিয়া",
    "marianne": "মারিয়ান",
    "marie": "মারি",
    "marina": "মারিনা",
    "mario": "মারিও",
    "marion": "মারিয়ন",
    "marius": "মারিয়াস",
    "mark": "মার্ক",
    "marko": "মার্কো",
    "markus": "মার্কাস",
    "marlene": "মার্লেন",
    "martin": "মার্টিন",
    "martina": "মার্টিনা",
    "mathieu": "মাথিউ",
    "mathis": "মাথিস",
    "matthias": "মাথিয়াস",
    "max": "ম্যাক্স",
    "maximilian": "ম্যাক্সিমিলিয়ান",
    "maya": "মায়া",
    "mehdi": "মেহদি",
    "melanie": "মেলানি",
    "michael": "মাইকেল",
    "michaela": "মিখায়েলা",
    "michel": "মিশেল",
    "milan": "মিলান",
    "milo": "মিলো",
    "mira": "মিরা",
    "miriam": "মিরিয়াম",
    "mirko": "মিরকো",
    "monika": "মনিকা",
    "moritz": "মরিৎস",
    "nadeschda": "নাদেশদা",
    "nadeshda": "নাদেশদা",
    "nadia": "নাদিয়া",
    "nadja": "নাদিয়া",
    "nicole": "নিকোল",
    "niels": "নিলস",
    "niklas": "নিকলাস",
    "niko": "নিকো",
    "nikolaus": "নিকোলাস",
    "nils": "নিলস",
    "nina": "নিনা",
    "noah": "নোয়া",
    "nora": "নোরা",
    "norman": "নরম্যান",
    "olaf": "ওলাফ",
    "oliver": "অলিভার",
    "olivia": "অলিভিয়া",
    "oskar": "অস্কার",
    "otto": "অটো",
    "patrick": "প্যাট্রিক",
    "paul": "পাউল",
    "paula": "পাওলা",
    "pauline": "পাউলিন",
    "peer": "পিয়ার",
    "peter": "পেটার",
    "petra": "পেত্রা",
    "philip": "ফিলিপ",
    "philipp": "ফিলিপ",
    "pia": "পিয়া",
    "rafael": "রাফায়েল",
    "rainer": "রাইনার",
    "ralf": "রাল্ফ",
    "ralph": "রাল্ফ",
    "ramon": "রামোন",
    "rebecca": "রেবেকা",
    "regina": "রেজিনা",
    "reimer": "রাইমার",
    "reiner": "রাইনার",
    "reinhard": "রাইনহার্ড",
    "reinhold": "রাইনহোল্ড",
    "rené": "রেনে",
    "rene": "রেনে",
    "renate": "রেনাতে",
    "richard": "রিচার্ড",
    "richy": "রিচি",
    "rike": "রিকে",
    "rita": "রিতা",
    "robert": "রবার্ট",
    "robin": "রবিন",
    "roland": "রোলান্ড",
    "rolf": "রোল্ফ",
    "roman": "রোমান",
    "ronald": "রোনাল্ড",
    "rosalie": "রোজালি",
    "ruben": "রুবেন",
    "rüdiger": "রুডিগার",
    "rudolf": "রুডলফ",
    "sabine": "সাবিনে",
    "samuel": "স্যামুয়েল",
    "sandra": "সান্দ্রা",
    "sandro": "সান্দ্রো",
    "sascha": "সাশা",
    "saskia": "সাসকিয়া",
    "sebastian": "সেবাস্টিয়ান",
    "selam": "সেলাম",
    "senta": "সেন্টা",
    "severin": "সেভেরিন",
    "sibylle": "সিবিলে",
    "sidonie": "সিডোনি",
    "siegfried": "জিগফ্রিড",
    "silke": "সিলকে",
    "silvia": "সিলভিয়া",
    "simon": "জিমন",
    "simone": "সিমোনে",
    "sina": "সিনা",
    "sönke": "জ্যোঙ্কে",
    "sonja": "সোনিয়া",
    "sophia": "সোফিয়া",
    "sophie": "সোফি",
    "stefan": "স্টেফান",
    "stefanie": "স্টেফানি",
    "steffen": "স্টেফেন",
    "stephan": "স্টেফান",
    "stephanie": "স্টেফানি",
    "susanne": "জুসানে",
    "sven": "সভেন",
    "svenja": "সভেনিয়া",
    "swantje": "সভান্তিয়ে",
    "tabea": "তাবেয়া",
    "tanja": "তানিয়া",
    "theodor": "থিওডোর",
    "theresa": "থেরেসা",
    "therese": "থেরেসে",
    "thomas": "টমাস",
    "tilo": "টিলো",
    "tim": "টিম",
    "timo": "টিমো",
    "tina": "টিনা",
    "tobias": "টোবিয়াস",
    "tom": "টম",
    "torben": "টরবেন",
    "torsten": "টরস্টেন",
    "udo": "উডো",
    "uli": "উলি",
    "ulrich": "উলরিখ",
    "ulrike": "উলরিকে",
    "ursula": "উরসুলা",
    "uwe": "উভে",
    "valentin": "ভ্যালেন্টিন",
    "valerie": "ভ্যালেরি",
    "vanessa": "ভ্যানেসা",
    "vera": "ভেরা",
    "verena": "ভেরেনা",
    "veronica": "ভেরোনিকা",
    "viktor": "ভিক্টর",
    "vincent": "ভিনসেন্ট",
    "vivian": "ভিভিয়ান",
    "volker": "ভলকার",
    "walter": "ভাল্টার",
    "wanda": "ভান্দা",
    "wanja": "ভানিয়া",
    "werner": "ভার্নার",
    "wilhelm": "ভিলহেল্ম",
    "willi": "ভিলি",
    "willy": "ভিলি",
    "wim": "ভিম",
    "winfried": "ভিনফ্রিড",
    "wladimir": "ভ্লাদিমির",
    "wolf": "ভলফ",
    "wolfgang": "ভলফগাং",
    "wotan": "ভোতান",
    "yannick": "ইয়ানিক",
    "yasemin": "ইয়াসেমিন",
    "yvonne": "ইভন",
    "zimmermann": "সিমারমান",
    "zimmer": "সিমার",
    "zweig": "স্বাইগ",
}

# ক্যাশ মেমরি
_TRANSLIT_CACHE = {}

INITIALS_MAP = {
    'A': 'এ', 'B': 'বি', 'C': 'সি', 'D': 'ডি', 'E': 'ই', 'F': 'এফ',
    'G': 'জি', 'H': 'এইচ', 'I': 'আই', 'J': 'জে', 'K': 'কে', 'L': 'এল',
    'M': 'এম', 'N': 'এন', 'O': 'ও', 'P': 'পি', 'Q': 'কিউ', 'R': 'আর',
    'S': 'এস', 'T': 'টি', 'U': 'ইউ', 'V': 'ভি', 'W': 'ডব্লিউ', 'X': 'এক্স',
    'Y': 'ওয়াই', 'Z': 'জেড'
}

def transliterate_token(token, is_start=True):
    """একক শব্দ বা পদবি ধ্বনিতাত্ত্বিকভাবে লিপ্যন্তর করে।"""
    raw_clean = token.strip(" ,.-'\"()[]{}")
    if not raw_clean:
        return ""
    
    # সংক্ষেপিত আদ্যক্ষর (Initials: যেমন H., S., W., A., B. ইত্যাদি)
    if len(raw_clean) == 1 and raw_clean.isalpha():
        letter = raw_clean.upper()
        bn_init = INITIALS_MAP.get(letter, letter)
        has_dot = '.' in token
        return bn_init + ('.' if has_dot else '')
    
    t_lower = raw_clean.lower()
    
    # ইউরোপীয় ভাষার ডায়াক্রিটিক্স প্রমিতকরণ
    DIACRITICS_MAP = {
        'ă': 'a', 'â': 'a', 'á': 'a', 'à': 'a', 'å': 'o', 'ą': 'a',
        'é': 'e', 'è': 'e', 'ë': 'e', 'ê': 'e', 'ę': 'e', 'ě': 'e',
        'í': 'i', 'î': 'i', 'ï': 'i', 'ı': 'i', 'İ': 'i',
        'ó': 'o', 'ò': 'o', 'ô': 'o', 'ø': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 's', 'ć': 'ch', 'č': 'ch', 'ğ': 'g', 'ł': 'l',
        'ş': 'sh', 'š': 'sh', 'ș': 'sh', 'ż': 'z', 'ž': 'z'
    }
    for d_char, norm in DIACRITICS_MAP.items():
        t_lower = t_lower.replace(d_char, norm)
    t_lower = t_lower.replace('q', 'k')
    
    # পদবি বা প্রথম নাম চেক
    if t_lower in FIRST_NAMES:
        return FIRST_NAMES[t_lower]
        
    # জার্মান উপসর্গ ও পদান্বয়ী অব্যয়
    if t_lower == 'von':
        return 'ফন'
    if t_lower == 'der':
        return 'ডার'
    if t_lower == 'den':
        return 'ডেন'
    if t_lower == 'dem':
        return 'ডেম'
    if t_lower == 'zu':
        return 'সু' if is_start else 'ৎসু'
    if t_lower == 'zum':
        return 'সুম'
    if t_lower == 'zur':
        return 'সুর'
    if t_lower == 'van':
        return 'ভান'
    if t_lower == 'de':
        return 'দ্য'
    if t_lower == 'du':
        return 'দ্যু'
    if t_lower == 'mc' or t_lower == "m'":
        return 'ম্যাক'
    if t_lower in ['jr.', 'jr']:
        return 'জুনিয়র'
    if t_lower in ['sr.', 'sr']:
        return 'সিনিয়র'

    # প্রমিত জার্মান প্রত্যয় (Suffixes)
    sfx_map = [
        (r'mann$', 'মান'), (r'männer$', 'মেনার'),
        (r'bergs$', 'বার্গস'), (r'berg$', 'বার্গ'), (r'berger$', 'বার্গার'),
        (r'burgs$', 'বুর্গস'), (r'burg$', 'বুর্গ'), (r'burger$', 'বুর্গার'),
        (r'anderson$', 'অ্যান্ডারসন'),
        (r'stein$', 'স্টাইন'), (r'steiner$', 'স্টাইনার'),
        (r'dorf$', 'ডর্ফ'), (r'dorfer$', 'ডর্ফার'),
        (r'thal$', 'তাল'), (r'tal$', 'তাল'),
        (r'feld$', 'ফেল্ড'), (r'felder$', 'ফেল্ডার'),
        (r'bach$', 'বাখ'), (r'bacher$', 'বাখার'),
        (r'bauer$', 'বাউয়ার'), (r'hoff$', 'হফ'), (r'hof$', 'হফ'),
        (r'hofer$', 'হোফার'), (r'heim$', 'হাইম'), (r'heimer$', 'হাইমার'),
        (r'haus$', 'হাউস'), (r'hauser$', 'হাউজার'),
        (r'holz$', 'হোলৎস'), (r'holzer$', 'হোলৎসার'),
        (r'schmidt$', 'শ্মিট'), (r'schmied$', 'শ্মিড'),
        (r'schneider$', 'শ্নাইডার'), (r'müller$', 'মুলার'),
        (r'mueller$', 'মুলার'), (r'weber$', 'ভেবার'),
        (r'fischer$', 'ফিশার'), (r'richter$', 'রিখটার'),
        (r'becker$', 'বেকার'), (r'koch$', 'কখ'),
        (r'schulz$', 'শুলৎস'), (r'schulze$', 'শুলৎসে'),
        (r'meier$', 'মায়ার'), (r'mayer$', 'মায়ার'),
        (r'meyer$', 'মায়ার'), (r'maier$', 'মায়ার'),
        (r'wagner$', 'ভাগনার'), (r'schäfer$', 'শেফার'),
        (r'hoffmann$', 'হফমান'), (r'bauer$', 'বাউয়ার'),
        (r'ner$', 'নার'), (r'ler$', 'লার'), (r'ter$', 'টার'),
        (r'ser$', 'সার'), (r'der$', 'ডার'), (r'ger$', 'গার'),
        (r'ber$', 'বার'), (r'per$', 'পার'), (r'mer$', 'মার'),
        (r'fer$', 'ফার'), (r'wer$', 'ভার'), (r'zer$', 'ৎসার'),
        (r'er$', 'ার'),
    ]
    
    token = t_lower
    for pat, rep in sfx_map:
        if re.search(pat, token):
            token = re.sub(pat, rep, token)
            break

    # শব্দ শুরুর যুক্তবর্ণ ও ধ্বনি রূপান্তর
    # নিয়ম: বাংলায় কখনো শব্দ 'ৎ' দিয়ে শুরু হয় না! Z -> স
    prefix = ""
    if token.startswith('zw'):
        prefix = 'স্ব'
        token = token[2:]
    elif token.startswith('schw'):
        prefix = 'শোয়'
        token = token[4:]
    elif token.startswith('tsch'):
        prefix = 'চ'
        token = token[4:]
    elif token.startswith('zsch'):
        prefix = 'শ'
        token = token[4:]
    elif token.startswith('sch'):
        prefix = 'শ'
        token = token[3:]
    elif token.startswith('str'):
        prefix = 'স্ট্র'
        token = token[3:]
    elif token.startswith('spr'):
        prefix = 'স্প্র'
        token = token[3:]
    elif token.startswith('st') and len(token) > 2 and token[2] in 'aeiouyäöü':
        prefix = 'স্ট'
        token = token[2:]
    elif token.startswith('sp') and len(token) > 2 and token[2] in 'aeiouyäöü':
        prefix = 'স্প'
        token = token[2:]
    elif token.startswith('br'):
        prefix = 'ব্র'
        token = token[2:]
    elif token.startswith('fr'):
        prefix = 'ফ্র'
        token = token[2:]
    elif token.startswith('kr'):
        prefix = 'ক্র'
        token = token[2:]
    elif token.startswith('tr'):
        prefix = 'ট্র'
        token = token[2:]
    elif token.startswith('gr'):
        prefix = 'গ্র'
        token = token[2:]
    elif token.startswith('dr'):
        prefix = 'ড্র'
        token = token[2:]
    elif token.startswith('pr'):
        prefix = 'প্র'
        token = token[2:]
    elif token.startswith('kl'):
        prefix = 'ক্ল'
        token = token[2:]
    elif token.startswith('fl'):
        prefix = 'ফ্ল'
        token = token[2:]
    elif token.startswith('gl'):
        prefix = 'গ্ল'
        token = token[2:]
    elif token.startswith('pl'):
        prefix = 'প্ল'
        token = token[2:]
    elif token.startswith('bl'):
        prefix = 'ব্ল'
        token = token[2:]
    elif token.startswith('chr') or token.startswith('chl'):
        prefix = 'ক্র' if token.startswith('chr') else 'ক্ল'
        token = token[3:]
    elif token.startswith('ch') and len(token) > 2 and token[2] in 'aouäöü':
        prefix = 'খ'
        token = token[2:]
    elif token.startswith('z'):
        # বাধ্যতামূলক: Initial Z = 'স' (কখনোই 'ৎ' নয়!)
        prefix = 'স'
        token = token[1:]
    elif token.startswith('tz'):
        prefix = 'স'
        token = token[2:]
    elif token.startswith('j') and len(token) > 1 and token[1] in 'aeiouäöü':
        prefix = 'ইয়'
        token = token[1:]
    elif token.startswith('v') and len(token) > 1:
        prefix = 'ফ'
        token = token[1:]
    elif token.startswith('w'):
        prefix = 'ভ'
        token = token[1:]
    elif token.startswith('s') and len(token) > 1 and token[1] in 'aeiouyäöü':
        prefix = 'জ'
        token = token[1:]

    # শব্দের অভ্যন্তরীণ রূপান্তর
    token = re.sub(r'tsch', 'চ', token)
    token = re.sub(r'schw', 'শোয়', token)
    token = re.sub(r'sch', 'শ', token)
    token = re.sub(r'tz', 'ৎস', token)
    token = re.sub(r'ck', 'ক', token)
    token = re.sub(r'chs', 'ক্স', token)
    token = re.sub(r'dt$', 'ট', token)
    token = re.sub(r'dt', 'ট', token)
    token = re.sub(r'ph', 'ফ', token)
    token = re.sub(r'pf', 'ফ', token)
    token = re.sub(r'qu', 'কোয়া', token)
    token = re.sub(r'ss', 'স', token)
    token = re.sub(r'ß', 'স', token)
    token = re.sub(r'ng$', 'ং', token)
    token = re.sub(r'ng', 'ঙ্গ', token)
    token = re.sub(r'nk', 'ঙ্ক', token)
    token = re.sub(r'th', 'ট', token)

    # দ্বিস্বরধ্বনি (Diphthongs)
    token = re.sub(r'ei|ey|ai|ay', 'আই', token)
    token = re.sub(r'ie', 'ই', token)
    token = re.sub(r'eu|äu', 'অয়', token)
    token = re.sub(r'au', 'আউ', token)
    token = re.sub(r'ee', 'এ', token)
    token = re.sub(r'oo', 'ও', token)
    token = re.sub(r'aa', 'আ', token)

    # Ch ও Z অভ্যন্তরীণ
    token = re.sub(r'ch', 'খ', token)
    token = re.sub(r'z', 'ৎস', token)
    token = re.sub(r'v', 'ফ', token)
    token = re.sub(r'w', 'ভ', token)

    # সাধারণ ব্যঞ্জনধ্বনি
    token = re.sub(r'b', 'ব', token)
    token = re.sub(r'c', 'ক', token)
    token = re.sub(r'd', 'ড', token)
    token = re.sub(r'f', 'ফ', token)
    token = re.sub(r'g', 'গ', token)
    token = re.sub(r'h', 'হ', token)
    token = re.sub(r'k', 'ক', token)
    token = re.sub(r'l', 'ল', token)
    token = re.sub(r'm', 'ম', token)
    token = re.sub(r'n', 'ন', token)
    token = re.sub(r'p', 'প', token)
    token = re.sub(r'r', 'র', token)
    token = re.sub(r's', 'স', token)
    token = re.sub(r't', 'ট', token)
    token = re.sub(r'x', 'ক্স', token)
    token = re.sub(r'j', 'ইয়', token)

    # স্বরধ্বনি
    token = re.sub(r'ä', 'এ', token)
    token = re.sub(r'ö', 'ও', token)
    token = re.sub(r'ü', 'উ', token)
    token = re.sub(r'a', 'আ', token)
    token = re.sub(r'e', 'এ', token)
    token = re.sub(r'i', 'ই', token)
    token = re.sub(r'o', 'ও', token)
    token = re.sub(r'u', 'উ', token)
    token = re.sub(r'y', 'ই', token)

    # একত্রীকরণ ও কার-চিহ্ন সংযোজন
    full = prefix + token

    VOWEL_TO_KAR = {
        'আ': 'া', 'ই': 'ি', 'ঈ': 'ী',
        'উ': 'ু', 'ঊ': 'ূ', 'ঋ': 'ৃ',
        'এ': 'ে', 'ঐ': 'ৈ', 'ও': 'ো', 'ঔ': 'ৌ',
    }
    
    out = []
    CONSONANTS = set('কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎ')
    for ch in full:
        if ch in VOWEL_TO_KAR:
            if out and out[-1] in CONSONANTS:
                out.append(VOWEL_TO_KAR[ch])
            else:
                out.append(ch)
        else:
            out.append(ch)
            
    final_str = "".join(out)
    
    # অতিরিক্ত কার ও পুনরাবৃত্তি দূরীকরণ
    final_str = re.sub(r'ে[াো]', 'ো', final_str)
    final_str = re.sub(r'া+', 'া', final_str)
    final_str = re.sub(r'ি+', 'ি', final_str)
    final_str = re.sub(r'ু+', 'ু', final_str)
    final_str = re.sub(r'ে+', 'ে', final_str)
    final_str = re.sub(r'ো+', 'ো', final_str)
    final_str = re.sub(r'্রর', '্র', final_str)
    for c in 'কগটডতদপবমসলনরফ':
        final_str = re.sub(c + c, c, final_str)
        
    return final_str


def transliterate_person_name(name):
    """
    একজন ব্যক্তির সম্পূর্ণ নাম বাংলায় লিপ্যন্তর করে।
    প্রথমে ডিকশনারি দেখে, না পেলে অ্যালগরিদমিক নিয়মে রূপান্তর করে।
    """
    if not name or not isinstance(name, str):
        return ""
        
    # ডিসঅ্যাম্বিগুয়েশন পরিষ্কার করা (যেমন: "(actor)", "(director)")
    clean = re.sub(r'\s*\([^)]*\)', '', name).strip()
    clean = clean.replace('<small>', '').replace('</small>', '').strip()
    
    # সংক্ষেপিত আদ্যক্ষর পৃথকীকরণ (যেমন: W.S. -> W. S.)
    clean = re.sub(r'([A-Za-z])\.([A-Za-z])', r'\1. \2', clean)
    
    if clean in DIRECTORS_AND_ACTORS:
        return DIRECTORS_AND_ACTORS[clean]
        
    if clean in _TRANSLIT_CACHE:
        return _TRANSLIT_CACHE[clean]
        
    # শব্দে ভাগ করে প্রতিটির জন্য লিপ্যন্তর
    # হাইফেন এবং স্পেস উভয়টি বিবেচনা করা
    parts = []
    tokens = re.split(r'(\s+|-)', clean)
    for i, t in enumerate(tokens):
        if not t:
            continue
        if t in [' ', '-', '  ']:
            parts.append(t)
        else:
            is_start = (i == 0 or tokens[i-1] in [' ', '  '])
            bn_t = transliterate_token(t, is_start=is_start)
            parts.append(bn_t)
            
    res = "".join(parts).strip()
    
    # চূড়ান্ত নিরাপত্তা যাচাই: শব্দ 'ৎ' দিয়ে শুরু হওয়া সম্পূর্ণ নিষিদ্ধ
    # যদি কোথাও শব্দের শুরুতে 'ৎ' বা 'ৎস' থাকে, তা 'স' করে দেওয়া
    words = res.split()
    sanitized_words = []
    for w in words:
        while w.startswith('ৎস'):
            w = 'স' + w[2:]
        while w.startswith('ৎ'):
            w = 'স' + w[1:]
        sanitized_words.append(w)
    res = " ".join(sanitized_words)
    res = re.sub(r'(^|[\s\-\(\[\{])ৎ[স]?', r'\1স', res)
    
    _TRANSLIT_CACHE[clean] = res
    return res
