# -*- coding: utf-8 -*-
"""
জাপানিদের তালিকা সম্পূর্ণ পাতা অনুবাদক (List of Japanese People Full Page Translator)
'জাপানিদের তালিকা.txt' পাতাটি প্রমিত বাংলা উইকিপিডিয়া ফরম্যাটে অনুবাদ করে 'জাপানিদের তালিকা (বাংলা).txt' তৈরি করে।
কোনো অবস্থাতেই ব্যক্তিনাম বা তালিকায় রোমান হরফ অবশিষ্ট রাখবে না।
"""
import os
import sys
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from japanese_transliteration import get_bengali_japanese_name
from table_translator import translate_wikitable
from number_converter import to_bengali_digits

HEADINGS_MAP = {
    '==Architects==': '==স্থপতি==',
    '==Artists==': '==শিল্পী==',
    '==Athletes==': '==ক্রীড়াবিদ==',
    '==Authors==': '==লেখক==',
    '==Company founders==': '==কোম্পানির প্রতিষ্ঠাতা==',
    '==Educators==': '==শিক্ষাবিদ==',
    '==Emperors==': '==সম্রাট==',
    '==Historians==': '==ঐতিহাসিক==',
    '==Military leaders==': '== সামরিক নেতা ==',
    '===Samurai===': '===সামুরাই===',
    '====A====': '====এ (A)====',
    '====B====': '====বি (B)====',
    '====C====': '====সি (C)====',
    '====D====': '====ডি (D)====',
    '====E====': '====ই (E)====',
    '====F====': '====এফ (F)====',
    '====G====': '====জি (G)====',
    '====H====': '====এইচ (H)====',
    '====I====': '====আই (I)====',
    '====K====': '====কে (K)====',
    '====M====': '====এম (M)====',
    '====N====': '====এন (N)====',
    '====O====': '====ও (O)====',
    '====R====': '====আর (R)====',
    '====S====': '====এস (S)====',
    '====T====': '====টি (T)====',
    '====U====': '====ইউ (U)====',
    '====W====': '====ডব্লিউ (W)====',
    '====Y====': '====ওয়াই (Y)====',
    "===Kamakura ''shōguns''===": "===কামাকুরা ''শোগুন''===",
    "====Kamakura shikken====": "====কামাকুরা শিক্কেন====",
    "===Ashikaga ''shōguns''===": "===আশিকাগা ''শোগুন''===",
    "===Tokugawa ''shōguns''===": "===তোকুগাওয়া ''শোগুন''===",
    '===Pre-modern===': '===প্রাক-আধুনিক===',
    '====Emperors====': '====সম্রাট====',
    '====Commanders from loyal family====': '====রাজপরিবারের কমান্ডারবৃন্দ====',
    "====Commanders in [[Thirty-Eight Years' War]]====": "====[[Thirty-Eight Years' War|আটত্রিশ বছরের যুদ্ধ]]-এর কমান্ডারবৃন্দ====",
    '===Modern===': '===আধুনিক===',
    '==Musicians==': '==সঙ্গীতজ্ঞ==',
    '==Personalities==': '==তারকা ও ব্যক্তিত্ব==',
    '===Comedians===': '===কমেডিয়ান===',
    '===Idols (male)===': '===আইডল (পুরুষ)===',
    '===Idols (female)===': '===আইডল (নারী)===',
    '===Models===': '===মডেল===',
    '===Musicians and singers (male)===': '===সঙ্গীতশিল্পী ও গায়ক (পুরুষ)===',
    '===Musicians and singers (female)===': '===সঙ্গীতশিল্পী ও গায়িকা (নারী)===',
    '===Tarento===': '===তালেন্তো (ট্যালেন্ট)===',
    '===Actors===': '===অভিনেতা===',
    '===Actresses===': '===অভিনেত্রী===',
    '===TV and radio personalities===': '===টিভি ও রেডিও ব্যক্তিত্ব===',
    '===Others===': '===অন্যান্য===',
    '==Prime Ministers==': '==প্রধানমন্ত্রী==',
    '===Meiji period (1868–1912)===': '===মেইজি যুগ (১৮৬৮–১৯১২)===',
    '===Taishō period (1912–1926)===': '===তাইশো যুগ (১৯১২–১৯২৬)===',
    '===Shōwa period under 1890 Constitution (1926–1947)===': '===১৮৯০ সালের সংবিধানের অধীন শোওয়া যুগ (১৯২৬–১৯৪৭)===',
    '===Shōwa period under 1947 Constitution (1947–1989)===': '===১৯৪৭ সালের সংবিধানের অধীন শোওয়া যুগ (১৯৪৭–১৯৮৯)===',
    '===Heisei period (1989–2019)===': '===হেইসেই যুগ (১৯৮৯–২০১৯)===',
    '===Reiwa period (2019–present)===': '===রেইওয়া যুগ (২০১৯–বর্তমান)===',
    '==Politicians==': '==রাজনীতিবিদ==',
    '==Religious leaders==': '==ধর্মীয় নেতা==',
    '==Scientists==': '==বিজ্ঞানী==',
    '==Mathematicians==': '==গণিতবিদ==',
    '==Economists==': '==অর্থনীতিবিদ==',
    '==Other notables==': '==অন্যান্য বিশিষ্ট ব্যক্তিবর্গ==',
    '== Other Japanese ==': '==অন্যান্য জাপানি==',
    '==See also==': '==আরও দেখুন==',
    '==References==': '==তথ্যসূত্র==',
}

ROLE_REPLACEMENTS = [
    # সাহিত্যকর্ম ও গ্রন্থ
    (r"author of \'\'\[\[The Woman in the Dunes \(novel\)\|The Woman in the Dunes\]\]\'\'", "লেখক: ''[[The Woman in the Dunes (novel)|দ্য ওম্যান ইন দ্য ডিউনস]]''"),
    (r"author of \'\'\[\[Oku no Hosomichi\|The Narrow Road to the Deep North\]\]\'\'", "লেখক: ''[[Oku no Hosomichi|ওকু নো হোসোমিচি (দ্য ন্যারো রোড টু দ্য ডিপ নর্থ)]]''"),
    (r"author of \'\'\[\[No Longer Human\]\]\'\'", "লেখক: ''[[No Longer Human|নো লঙ্গার হিউম্যান]]''"),
    (r"author of \'\'\[\[The Tale of Genji\]\]\'\'", "লেখক: ''[[The Tale of Genji|দ্য টেল অব গেনজি]]''"),
    (r"author of \'\'\[\[The Pillow Book\]\]\'\'", "লেখক: ''[[The Pillow Book|দ্য পিলো বুক]]''"),
    (r"author of \'\'\[\[Kokoro\]\]\'\'", "লেখক: ''[[Kokoro|কোকোরো]]''"),
    (r"author of \'\'\[\[Essays in Idleness\]\]\'\'", "লেখক: ''[[Essays in Idleness|এসেস ইন আইডলনেস]]''"),
    (r'\bauthor of\b', 'লেখক:'),

    # নোবেল ও অন্যান্য পুরস্কার
    (r'\bwinner of the\s+\[\[Nobel Prize in Literature\]\]', '[[Nobel Prize in Literature|সাহিত্যে নোবেল পুরস্কার]] বিজয়ী'),
    (r'\bwinner of the\s+\[\[Nobel Prize in Physics\]\]', '[[Nobel Prize in Physics|পদার্থবিজ্ঞানে নোবেল পুরস্কার]] বিজয়ী'),
    (r'\bwinner of the\s+\[\[Nobel Prize in Chemistry\]\]', '[[Nobel Prize in Chemistry|রসায়নে নোবেল পুরস্কার]] বিজয়ী'),
    (r'\bwinner of the\s+\[\[Nobel Prize in Physiology or Medicine\]\]', '[[Nobel Prize in Physiology or Medicine|চিকিৎসাবিজ্ঞানে নোবেল পুরস্কার]] বিজয়ী'),
    (r'\bwinner of the\s+\[\[Fields Medal\]\]', '[[Fields Medal|ফিল্ডস মেডেল]] বিজয়ী'),

    # কোম্পানি প্রতিষ্ঠাতা
    (r'\bfounder of Nissan\b', 'নিসান-এর প্রতিষ্ঠাতা'),
    (r'\bco-founder of the automobile manufacturer Honda\b', 'হোন্ডা অটোমোবাইল কোম্পানির সহ-প্রতিষ্ঠাতা'),
    (r'\bfounder of Mugen Motorsports\b', 'মুগেন মোটরস্পোর্টস-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of Panasonic\b', 'প্যানাসনিক-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of Rakuten\b', 'রাকুতেন-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of Mitsui\b', 'মিৎসুই-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of Mikimoto\b', 'মিকিমোতো-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of Mazda automobile company\b', 'মাজদা অটোমোবাইল কোম্পানির প্রতিষ্ঠাতা'),
    (r'\bfounder of Suzuki\b', 'সুজুকি-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of luxury automobile manufacturer Lexus\b', 'বিলাসবহুল গাড়ি নির্মাতা লেক্সাস-এর প্রতিষ্ঠাতা'),
    (r'\bfounder of automobile manufacturer Toyota in 1937\b', '১৯৩৭ সালে টয়োটা অটোমোবাইল কোম্পানির প্রতিষ্ঠাতা'),
    (r'\bfounder of Toyota Industries and Toyota Group\b', 'টয়োটা ইন্ডাস্ট্রিজ এবং টয়োটা গ্রুপের প্রতিষ্ঠাতা'),
    (r'\bco-founder of the automobile manufacturer\b', 'অটোমোবাইল প্রস্তুতকারক ...-এর সহ-প্রতিষ্ঠাতা:'),
    (r'\bco-founder of\b', 'সহ-প্রতিষ্ঠাতা:'),
    (r'\bfounder of\b', 'প্রতিষ্ঠাতা:'),

    # প্রধানমন্ত্রীদের সাম্রাজ্যিক উপাধি
    (r'\'\'Prime Ministers of \[\[Emperor Meiji\]\]\'\'', "''[[Emperor Meiji|সম্রাট মেইজির]] প্রধানমন্ত্রীবৃন্দ''"),
    (r'\'\'Prime Ministers of \[\[Emperor Taishō\]\]\'\'', "''[[Emperor Taishō|সম্রাট তাইশোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r'\'\'Prime Ministers of \[\[Emperor Shōwa\]\]\'\'', "''[[Emperor Shōwa|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r'\'\'Prime Ministers of \[\[Akihito\|Emperor Akihito\]\]\'\'', "''[[Akihito|সম্রাট আকিহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r'\'\'Prime Ministers of \[\[Naruhito\|Emperor Naruhito\]\]\'\'', "''[[Naruhito|সম্রাট নারুহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),

    # ঐতিহাসিক বংশ ও ব্যক্তিত্ব
    (r'\bSee also\b', 'আরও দেখুন'),
    (r'\(foreign born\)', '(বিদেশী বংশোদ্ভূত)'),
    (r'\(Tawara no Tōda\)', '(তাওয়ারা নো তোদা)'),
    (r'\(Kuroki Tamemoto\)', '(কুরোকি তামেমোতো)'),
    (r'of the \[\[Mito domain\]\]', '[[Mito domain|মিতো ডোমেন]]-এর'),
    (r'of the \[\[Mito domain\|([^\]]+)\]\]', r'[[\1|মিতো ডোমেন]]-এর'),
    (r'of the \[\[Gosankyo\|Hitotsubashi\]\] branch', '[[Gosankyo|হিতোৎসুবাশি]] শাখার'),
    (r'of the \[\[Gosankyo\|Tayasu\]\] branch\.', '[[Gosankyo|তায়াসু]] শাখার।'),
    (r'of the \[\[Aizu\]\] branch\.', '[[Aizu|আইজু]] শাখার।'),
    (r'born into the \[\[Gosankyo\|Tayasu\]\] branch, adopted into the \[\[Hisamatsu clan\|Hisamatsu-Matsudaira\]\] of \[\[Shirakawa han\|Shirakawa\]\]\.',
     '[[Gosankyo|তায়াসু]] শাখায় জন্ম, [[Shirakawa han|শিরাকাওয়ার]] [[Hisamatsu clan|হিসামাৎসু-মাৎসুদাইরা]] পরিবারে দত্তক গৃহীত।'),
    (r',\s*organic farmer\b', ', জৈব কৃষক'),
    (r',\s*engineer\b', ', প্রকৌশলী'),
    (r'#\s*Minamoto no Yoritomo,\s*r\.\s*1192–1199', '# [[Minamoto no Yoritomo|মিনামোতো নো ইয়োরিতোমো]], শাসনকাল: ১১৯২–১১৯৯'),
    (r',\s*r\.\s*(\d+)', r', শাসনকাল: \1'),
    (r',\s*r\.(\d+)', r', শাসনকাল: \1'),
    (r'\br\.\s*(\d+)', r'শাসনকাল: \1'),
    (r'\br\.(\d+)', r'শাসনকাল: \1'),
    (r'#\s*\[\[Ashikaga Takauji\]\],\s*ruled\s*1338–1358', '# [[Ashikaga Takauji|আশিকাগা তাকাউজি]], শাসনকাল: ১৩৩৮–১৩৫৮'),
    (r',\s*ruled\s*1338–1358', ', শাসনকাল: ১৩৩৮–১৩৫৮'),
    (r'Over the course of the Edo period, influential relatives of the shōgun included:', 'এদো যুগে শোগুনের প্রভাবশালী আত্মীয়দের মধ্যে অন্তর্ভুক্ত ছিলেন:'),
    (r"\'\'Prime Ministers of \[\[Hirohito\|Emperor Shōwa\]\] under \[\[Meiji Constitution\|1890 Constitution\]\]\'\'", "''১৮৯০ সালের সংবিধানের অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|Emperor Shōwa\]\] under \[\[Constitution of Japan\|1947 Constitution\]\]\'\'", "''১৯৪৭ সালের সংবিধানের অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|সম্রাট শোওয়া\]\] under \[\[Meiji Constitution\|১৮৯০ সালের সংবিধান\]\]\'\'", "''১৮৯০ সালের সংবিধানের অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|সম্রাট শোওয়া\]\] under \[\[Constitution of Japan\|১৯৪৭ সালের সংবিধান\]\]\'\'", "''১৯৪৭ সালের সংবিধানের অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|Emperor Shōwa\]\] under \[\[Meiji Constitution\]\]\'\'", "''[[Meiji Constitution|মেইজি সংবিধানের]] অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Emperor Shōwa\]\] under \[\[Meiji Constitution\]\]\'\'", "''[[Meiji Constitution|মেইজি সংবিধানের]] অধীন [[Emperor Shōwa|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|সম্রাট শোওয়া\]\] under \[\[Meiji Constitution\|মেইজি সংবিধান\]\]\'\'", "''[[Meiji Constitution|মেইজি সংবিধানের]] অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|Emperor Shōwa\]\] under \[\[Constitution of Japan\]\]\'\'", "''[[Constitution of Japan|জাপানের সংবিধানের]] অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of \[\[Hirohito\|সম্রাট শোওয়া\]\] under \[\[Constitution of Japan\|জাপানের সংবিধান\]\]\'\'", "''[[Constitution of Japan|জাপানের সংবিধানের]] অধীন [[Hirohito|সম্রাট শোওয়ার]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of Emperor \[\[Akihito\]\]\'\'", "''[[Akihito|সম্রাট আকিহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of Emperor \[\[Akihito\|আকিহিতো\]\]\'\'", "''[[Akihito|সম্রাট আকিহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of Emperor \[\[Naruhito\]\]\'\'", "''[[Naruhito|সম্রাট নারুহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r"\'\'Prime Ministers of Emperor \[\[Naruhito\|নারুহিতো\]\]\'\'", "''[[Naruhito|সম্রাট নারুহিতোর]] প্রধানমন্ত্রীবৃন্দ''"),
    (r'<!--more actress, not sure-->', ''),
    (r'<!--borderline gravure, not sure-->', ''),
    (r'<!--He is British-born.*?-->', ''),
]

def translate_bullet_line(line: str) -> str:
    """তালিকাসমূহ অনুবাদ করে। কোনো ইংরেজি হরফ রাখবে না।"""
    s = line

    # ভূমিকা ও পরিভাষা প্রতিস্থাপন
    for pat, rep in ROLE_REPLACEMENTS:
        s = re.sub(pat, rep, s, flags=re.I)

    # উইকিলিংকসমূহ অনুবাদ
    def repl_link(match):
        raw = match.group(1).strip()
        if raw.startswith('File:') or raw.startswith('Image:') or raw.startswith('Category:') or raw.startswith(':Category:'):
            return match.group(0)

        if '|' in raw:
            target, label = raw.split('|', 1)
            # যদি লেবেল ইতিমধ্যে সম্পূর্ণ বাংলা হয়
            if not re.search(r'[a-zA-Z]', label):
                return match.group(0)
            bn_name = get_bengali_japanese_name(target, label)
            return f"[[{target}|{bn_name}]]"
        else:
            if not re.search(r'[a-zA-Z]', raw):
                return match.group(0)
            bn_name = get_bengali_japanese_name(raw, "")
            return f"[[{raw}|{bn_name}]]"

    s = re.sub(r'\[\[([^\]]+)\]\]', repl_link, s)

    # সংখ্যা ও তারিখ রূপান্তর
    s = to_bengali_digits(s)

    return s

def translate_and_sort_samurai_section(text: str) -> str:
    """সামুরাই অংশের নামগুলো ইংরেজি A-Z বাদ দিয়ে প্রমিত বাংলা বর্ণানুক্রমে (অ-হ) সাজায়।"""
    m = re.search(r'(===(?:Samurai|সামুরাই)===\s*\{\{colbegin[^\}]*\}\})(.*?)(\{\{colend\}\})', text, flags=re.DOTALL)
    if not m:
        return text

    prefix = m.group(1)
    body = m.group(2)
    suffix = m.group(3)

    lines = [l.strip() for l in body.splitlines() if l.strip()]
    items = []
    current_item = []
    for l in lines:
        if l.startswith('===='):
            continue
        if l.startswith('* '):
            if current_item:
                items.append('\n'.join(current_item))
                current_item = []
            current_item.append(l)
        elif l.startswith('**'):
            current_item.append(l)
        elif current_item:
            current_item.append(l)
    if current_item:
        items.append('\n'.join(current_item))

    # Translate each item
    tr_items = []
    for it in items:
        tr_lines = [translate_bullet_line(l) for l in it.splitlines()]
        tr_items.append('\n'.join(tr_lines))

    # Bengali collation order
    bn_vowels = 'অআইঈউঊঋএঐওঔ'
    bn_consonants = 'কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়'
    bn_order = bn_vowels + bn_consonants

    def get_sort_key(bn_item):
        match = re.search(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', bn_item)
        name = match.group(1).strip() if match else bn_item.strip('* ').strip()
        char_ranks = []
        for ch in name:
            if ch in bn_order:
                char_ranks.append(bn_order.index(ch))
            else:
                char_ranks.append(1000 + ord(ch))
        return (char_ranks, name)

    tr_items.sort(key=get_sort_key)

    grouped = {}
    for it in tr_items:
        match = re.search(r'\[\[(?:[^|\]]+\|)?([^\]]+)\]\]', it)
        name = match.group(1).strip() if match else it.strip('* ')
        first_char = name[0] if name else 'অন্যান্য'
        grouped.setdefault(first_char, []).append(it)

    res_blocks = []
    sorted_letters = sorted(grouped.keys(), key=lambda ch: bn_order.index(ch) if ch in bn_order else 999)
    for letter in sorted_letters:
        res_blocks.append(f"\n===={letter}====")
        for it in grouped[letter]:
            res_blocks.append(it)

    new_body = '\n'.join(res_blocks) + '\n'
    return text[:m.start()] + prefix + new_body + suffix + text[m.end():]

def translate_page(content: str) -> str:
    """সম্পূর্ণ উইকিপিডিয়া পাতা অনুবাদ করে।"""
    # ১. ভূমিকা অংশ প্রতিস্থাপন
    lead_pattern = r"\{\{Short description\|none\}\}.*?This is a \'\'\'list of notable \[\[Japanese people\]\]\'\'\'\.\s*To be included in this list, the person must have a Wikipedia article showing they are Japanese\.\s*\{\{TOC limit\|3\}\}"

    bn_lead = """এটি বিশিষ্ট '''[[Japanese people|জাপানি ব্যক্তিদের একটি তালিকা]]'''।

এই তালিকায় অন্তর্ভুক্ত হওয়ার জন্য ব্যক্তির একটি উইকিপিডিয়া নিবন্ধ থাকতে হবে যা নির্দেশ করে যে তিনি জাপানি।
{{TOC limit|3}}"""

    s = re.sub(lead_pattern, bn_lead, content, flags=re.DOTALL)

    # ২. সেকশন শিরোনাম প্রতিস্থাপন
    for en_h, bn_h in HEADINGS_MAP.items():
        s = s.replace(en_h, bn_h)

    # ২.১. সামুরাই অংশের নামগুলো বাংলা বর্ণানুক্রমে (অ-হ) সাজানো
    s = translate_and_sort_samurai_section(s)

    # ৩. মূল সারণিসমূহ আলাদা করে অনুবাদ করা
    tables = []
    def save_tbl(m):
        tbl_idx = len(tables)
        tag = f"__TABLE_BLOCK_{tbl_idx}__"
        tables.append(translate_wikitable(m.group(0)))
        return tag

    s = re.sub(r'\{\|.*?\n\|\}', save_tbl, s, flags=re.DOTALL)

    # ৪. সারণির বাইরের প্রতিটি লাইন (বুলেট পয়েন্ট ইত্যাদি) অনুবাদ করা
    lines = s.splitlines()
    tr_lines = []
    for l in lines:
        if l.strip().startswith('__TABLE_BLOCK_'):
            tr_lines.append(l)
        elif l.strip().startswith('*'):
            tr_lines.append(translate_bullet_line(l))
        elif '{{main|' in l or '{{Main|' in l:
            # প্রধান নিবন্ধ লিঙ্ক
            l_tr = l
            l_tr = l_tr.replace('List of Japanese architects', 'List of Japanese architects|l1=জাপানি স্থপতিদের তালিকা')
            l_tr = l_tr.replace('List of Japanese artists', 'List of Japanese artists|l1=জাপানি শিল্পীদের তালিকা')
            l_tr = l_tr.replace('List of Japanese photographers', 'List of Japanese photographers|l2=জাপানি আলোকচিত্রশিল্পীদের তালিকা')
            l_tr = l_tr.replace('List of Japanese sportspeople', 'List of Japanese sportspeople|l1=জাপানি ক্রীড়াবিদদের তালিকা')
            l_tr = l_tr.replace('List of Japanese writers', 'List of Japanese writers|l1=জাপানি লেখকদের তালিকা')
            l_tr = l_tr.replace('List of Japanese entrepreneurs', 'List of Japanese entrepreneurs|l1=জাপানি উদ্যোক্তাদের তালিকা')
            l_tr = l_tr.replace('List of emperors of Japan', 'List of emperors of Japan|l1=জাপানের সম্রাটদের তালিকা')
            tr_lines.append(l_tr)
        else:
            tr_lines.append(translate_bullet_line(l))

    s = '\n'.join(tr_lines)

    # ৫. সারণি পুনরুদ্ধার
    for idx, tbl_tr in enumerate(tables):
        tag = f"__TABLE_BLOCK_{idx}__"
        s = s.replace(tag, tbl_tr)

    # ৬. ফাইল ক্যাপশন অনুবাদ
    s = re.sub(r'\[\[File:Minamoto-no-Yoritomo Grave2-Kamakura\.jpg\|thumb\|Grave of \[\[Minamoto no Yoritomo\]\]\s*\]\]',
               '[[File:Minamoto-no-Yoritomo Grave2-Kamakura.jpg|thumb|[[Minamoto no Yoritomo|মিনামোতো নো ইয়োরিতোমোর]] সমাধি]]', s)
    s = re.sub(r'\[\[File:Hojo Takatoki Harakiri-Yagura\.jpg\|thumb\|right\|Site of Hōjō Takatoki\'s death\]\]',
               '[[File:Hojo Takatoki Harakiri-Yagura.jpg|thumb|right|হোজো তাকাতোকির মৃত্যুর স্থান]]', s)

    # ৭. See also লিঙ্ক অনুবাদ
    s = s.replace('*[[List of people by nationality]]', '*[[List of people by nationality|জাতীয়তা অনুযায়ী ব্যক্তিদের তালিকা]]')

    # ৭. বিষয়শ্রেণী ও ডিফল্ট সর্ট
    s = s.replace('{{DEFAULTSORT:Japanese People}}', '{{DEFAULTSORT:জাপানিদের তালিকা}}\n[[বিষয়শ্রেণী:জাপানি ব্যক্তিদের তালিকা| ]]\n[[বিষয়শ্রেণী:জাতীয়তা অনুযায়ী ব্যক্তিদের তালিকা|জাপানি]]\n[[বিষয়শ্রেণী:জাপান-সম্পর্কিত তালিকা|ব্যক্তি]]')

    # ৮. বাংলায় শব্দের শুরুতে কখনোই 'ৎ' বসে না (যেমন: tsunami -> সুনামি, Tsunesaburō -> সুনেসাবুরো)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসু', r'\1সু', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসা', r'\1সা', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসি', r'\1সি', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসে', r'\1সে', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসো', r'\1সো', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎস', r'\1স', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎ', r'\1স', s)

    return s

def main():
    source_path = os.path.join(_current_dir, 'জাপানিদের তালিকা.txt')
    output_path = os.path.join(_current_dir, 'জাপানিদের তালিকা (বাংলা).txt')
    root_output_path = os.path.abspath(os.path.join(_current_dir, '..', 'জাপানিদের তালিকা (বাংলা).txt'))

    print(f"উৎস ফাইল পড়া হচ্ছে: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_text = f.read()

    print("পাতা অনুবাদ করা হচ্ছে...")
    translated_text = translate_page(source_text)

    print(f"অনূদিত ফাইল সংরক্ষণ করা হচ্ছে: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print(f"ওয়ার্কস্পেস রুটেও অনুলিপি সংরক্ষণ করা হচ্ছে: {root_output_path}")
    with open(root_output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print("অনুবাদ সফলভাবে সম্পন্ন হয়েছে!")

if __name__ == '__main__':
    main()
