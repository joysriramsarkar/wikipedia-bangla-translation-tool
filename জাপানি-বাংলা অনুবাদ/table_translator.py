# -*- coding: utf-8 -*-
"""
জাপানি উইকিপিডিয়া সারণী অনুবাদক (Japanese Wikipedia Table Translator)
সম্রাটগণ, শোগুন ও প্রধানমন্ত্রীদের সারণীসমূহ প্রমিত বাংলায় রূপান্তর করে।
কোনো অবস্থাতেই রোমান/ইংরেজি বর্ণ অবশিষ্ট রাখবে না।
"""
import os
import sys
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

import importlib.util

def _load_local_mod(mod_name: str):
    p = os.path.join(_current_dir, f"{mod_name}.py")
    if os.path.exists(p):
        spec = importlib.util.spec_from_file_location(f"ja_{mod_name}", p)
        if spec and spec.loader:
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
    return None

_jt = _load_local_mod("japanese_transliteration")
get_bengali_japanese_name = getattr(_jt, 'get_bengali_japanese_name', lambda x, y="": x)
transliterate_japanese_name = getattr(_jt, 'transliterate_japanese_name', lambda x: x)

_nc = _load_local_mod("number_converter")
to_bengali_digits = getattr(_nc, 'to_bengali_digits', lambda x: x)

_pn = _load_local_mod("prime_minister_notes")
COLSPAN_DESCRIPTIONS = getattr(_pn, 'COLSPAN_DESCRIPTIONS', {})

MONTHS_MAP = [
    (r'\bJanuary\b', 'জানুয়ারি'),
    (r'\bFebruary\b', 'ফেব্রুয়ারি'),
    (r'\bMarch\b', 'মার্চ'),
    (r'\bApril\b', 'এপ্রিল'),
    (r'\bMay\b', 'মে'),
    (r'\bJune\b', 'জুন'),
    (r'\bJuly\b', 'জুলাই'),
    (r'\bAugust\b', 'আগস্ট'),
    (r'\bSeptember\b', 'সেপ্টেম্বর'),
    (r'\bOctober\b', 'অক্টোবর'),
    (r'\bNovember\b', 'নভেম্বর'),
    (r'\bDecember\b', 'ডিসেম্বর'),
    (r'\{\{small\|Mar\.\}\}', '{{small|মার্চ}}'),
    (r'\{\{small\|Sept\.\}\}', '{{small|সেপ্টেম্বর}}'),
]

PARTY_COLOR_MAP = [
    (r'\{\{color\|lightgrey\|LDP<br\s*/?><small>Jimintō</small>\}\}', '{{color|lightgrey|এলডিপি<br/><small>জিমিন্তো</small>}}'),
    (r'\{\{color\|lightgrey\|DPJ<br\s*/?><small>Minshutō</small>\}\}', '{{color|lightgrey|ডিপিজে<br/><small>মিনশুতো</small>}}'),
    (r'\{\{color\|white\|JDP<br\s*/?><small>Nihon Minshutō</small>\}\}', '{{color|white|জেডিপি<br/><small>নিহোন মিনশুতো</small>}}'),
    (r'\{\{color\|white\|DP<br\s*/?><small>Minshutō</small>\}\}', '{{color|white|ডিপি<br/><small>মিনশুতো</small>}}'),
    (r'\{\{color\|lightgrey\|Japan Liberal\}\}', '{{color|lightgrey|জাপান লিবারেল}}'),
    (r'\{\{color\|lightgrey\|JNP<br\s*/?><small>Nihon Shintō</small>\}\}', '{{color|lightgrey|জেএনপি<br/><small>নিহোন শিন্তো</small>}}'),
    (r'\{\{color\|lightgrey\|Taisei Yokusankai\}\}', '{{color|lightgrey|তাইসেই ইয়োকুসানকাই}}'),
    (r'\{\{color\|white\|JSP<br\s*/?><small>Nihon Shakaitō</small>\}\}', '{{color|white|জেএসপি<br/><small>নিহোন শাকাইতো</small>}}'),
    (r'\{\{color\|white\|JRP<br\s*/?><small>Shinseitō</small>\}\}', '{{color|white|জেআরপি<br/><small>শিনসেইতো</small>}}'),
]

EXACT_ACTING_PM_NOTES = [
    (r'\|colspan=10\|\s*During this interval, Privy Council Chairman \[\[Kuroda Kiyotaka\]\] \(<span lang="ja"><span style="font-size:125%;">黑田 清隆</span></span> \'\'Kuroda Kiyotaka\'\'\) was the acting prime minister\.',
     '|colspan=10| এই অন্তর্বর্তীকালে প্রিভি কাউন্সিলের চেয়ারম্যান [[Kuroda Kiyotaka|কুরোদা কিওতাকা]] (<span lang="ja"><span style="font-size:125%;">黑田 清隆</span></span> \'\'কুরোদা কিওতাকা\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
    (r'\|colspan=10\s*\|\s*During this interval, Privy Council Chairman \[\[Saionji Kinmochi\]\] \(<span lang="ja"><span style="font-size:125%;">西園寺 公望</span></span> \'\'Saionji Kinmochi\'\'\) was the acting prime minister\.',
     '|colspan=10| এই অন্তর্বর্তীকালে প্রিভি কাউন্সিলের চেয়ারম্যান [[Saionji Kinmochi|সায়নজি কিনমোচি]] (<span lang="ja"><span style="font-size:125%;">西園寺 公望</span></span> \'\'সায়নজি কিনমোচি\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
    (r'\|colspan=10\s*\|\s*During this interval, Foreign Minister \[\[Uchida Kosai\]\] \(<span lang="ja"><span style="font-size:125%;">内田 康哉</span></span> \'\'Uchida Kōsai\'\'\) was the acting prime minister\.',
     '|colspan=10| এই অন্তর্বর্তীকালে পররাষ্ট্রমন্ত্রী [[Uchida Kosai|উচিদা কোসাই]] (<span lang="ja"><span style="font-size:125%;">内田 康哉</span></span> \'\'উচিদা কোসাই\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
    (r'\|colspan=10\s*\|\s*During this interval, Interior Minister \[\[Wakatsuki Reijirō\]\] \(<span lang="ja"><span style="font-size:125%;">若槻 禮次郎</span></span> \'\'Wakatsuki Reijirō\'\'\) was the acting prime minister\.',
     '|colspan=10| এই অন্তর্বর্তীকালে স্বরাষ্ট্রমন্ত্রী [[Wakatsuki Reijirō|ওয়াকাৎসুকি রেইজিরো]] (<span lang="ja"><span style="font-size:125%;">若槻 禮次郎</span></span> \'\'ওয়াকাৎসুকি রেইজিরো\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
    (r'\|colspan=10\s*\|\s*During this interval, Finance Minister \[\[Takahashi Korekiyo\]\] \(<span lang="ja"><span style="font-size:125%;">高橋 是清</span></span> \'\'Takahashi Korekiyo\'\'\) was the acting prime minister\.',
     '|colspan=10| এই অন্তর্বর্তীকালে অর্থমন্ত্রী [[Takahashi Korekiyo|তাকাহাশি কোরেকিয়ো]] (<span lang="ja"><span style="font-size:125%;">高橋 是清</span></span> \'\'তাকাহাশি কোরেকিয়ো\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
    (r'\|colspan=11\s*\|\s*During this interval, Chief Cabinet Secretary \[\[Masayoshi Ito\]\] \(<span lang="ja"><span style="font-size:125%;">伊東 正義</span></span> \'\'Itō Masayoshi\'\'\) was the acting prime minister\.',
     '|colspan=11| এই অন্তর্বর্তীকালে প্রধান মন্ত্রিপরিষদ সচিব [[Masayoshi Ito|মাসায়োশি ইতো]] (<span lang="ja"><span style="font-size:125%;">伊東 正義</span></span> \'\'মাসায়োশি ইতো\'\') ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।'),
]

def translate_table_headers(text: str) -> str:
    """টেবিলের হেডার ও যুগ শিরোনামসমূহ অনুবাদ করে।"""
    s = text

    # যুগসমূহ (Periods in Emperor table)
    s = re.sub(r'\[\[:Category:Legendary Emperors of Japan\|Legendary Emperors\]\]', '[[:Category:Legendary Emperors of Japan|পৌরাণিক সম্রাটগণ]]', s)
    s = re.sub(r'\[\[Kofun period\]\]', '[[কোফুন যুগ]]', s)
    s = re.sub(r'\[\[Asuka period\]\]', '[[আসুক যুগ]]', s)
    s = re.sub(r'\[\[Nara period\]\]', '[[নারা যুগ]]', s)
    s = re.sub(r'\[\[Heian period\]\]', '[[হেইআন যুগ]]', s)
    s = re.sub(r'\[\[Kamakura period\]\]', '[[কামাকুরা যুগ]]', s)
    s = re.sub(r'\[\[Nanboku-chō period\]\]', '[[নানবোকু-চো যুগ]]', s)
    s = re.sub(r'\[\[Muromachi period\]\]', '[[মুরোমাচি যুগ]]', s)
    s = re.sub(r'\[\[Azuchi–Momoyama period\]\]', '[[আজুচি-মোমোয়ামা যুগ]]', s)
    s = re.sub(r'\[\[Edo period\]\]', '[[এদো যুগ]]', s)
    s = re.sub(r'\[\[Meiji period\]\]', '[[মেইজি যুগ]]', s)
    s = re.sub(r'\[\[Taishō period\]\]', '[[তাইশো যুগ]]', s)
    s = re.sub(r'\[\[Shōwa period\]\]', '[[শোওয়া যুগ]]', s)
    s = re.sub(r'\[\[Heisei period\]\]', '[[হেইসেই যুগ]]', s)
    s = re.sub(r'\[\[Reiwa period\]\]', '[[রেইওয়া যুগ]]', s)
    s = re.sub(r'\[\[Northern Court\]\]\s*\(1333–1392\)', '[[Northern Court|উত্তর রাজদরবার]] (১৩৩৩–১৩৯২)', s)

    # কলাম হেডার (যেকোনো style/attribute সহ)
    s = re.sub(r'!\s*rowspan="?2"?\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?No\.', '! rowspan="2" style="width:25px;" | নং', s)
    s = re.sub(r'!\s*scope="col"\s*\|\s*Number', '! scope="col" | নং', s)
    s = re.sub(r'!\s*style="width:3%;"\s*\|\s*No\.', '! style="width:3%;" | নং', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?No\.', '! নং', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?\[\[Reign\]\]', '! style="width:13%;"| [[Reign|শাসনকাল]]', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?\[\[Posthumous name\]\]', '! style="width:21%;"| [[Posthumous name|মরণোত্তর নাম]]', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?\[\[Japanese name\|Personal name\]\]\s*\(\'\'imina\'\'\)', "! style=\"width:30%;\"| [[Japanese name|ব্যক্তিগত নাম]] (''ইমিনা'')", s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Notes\b', '! style="width:33%;"| মন্তব্য', s)
    s = re.sub(r'!\s*(?:width=\d+\s*\|\s*)?Portrait', '! width=60 | প্রতিকৃতি', s)
    s = re.sub(r'!\s*colspan="?2"?\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Prime Minister', '! colspan=2 style="width:280px;" | প্রধানমন্ত্রী', s)
    s = re.sub(r'!\s*colspan="?3"?\s*\|\s*Term of office', '! colspan=3 | মেয়াদকাল', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Political Party', '! style="width:100px;" rowspan="2" | রাজনৈতিক দল', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Government', '! style="width:160px;" rowspan="2" | সরকার', s)
    s = re.sub(r'!\s*colspan="?2"?\s*\|\s*Elected', '! colspan="2" | নির্বাচিত', s)
    s = re.sub(r'!\s*(?:rowspan="?2"?\s*\|\s*)?Elected', '! rowspan="2" | নির্বাচিত', s)
    s = re.sub(r'!\s*rowspan="?2"?\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Ref\b', '! rowspan="2" style="width:20px;" | তথ্যসূত্র', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Ref\b', '! তথ্যসূত্র', s)
    s = re.sub(r'!\s*(?:[a-zA-Z0-9_\-=";%: ]+\|\s*)?Name(?:<br\s*/>|<br>)?(?:<small>\(Birth–Death\)</small>)?', '! নাম<br /><small>(জন্ম–মৃত্যু)</small>', s)
    s = re.sub(r'\bTook office\b', 'দায়িত্ব গ্রহণ', s)
    s = re.sub(r'\bLeft office\b', 'দায়িত্ব ত্যাগ', s)
    s = re.sub(r'!\s*Days\b', '! দিন', s)
    s = re.sub(r'!\s*Gen\.', '! সাধারণ', s)
    s = re.sub(r'!\s*Coun\.', '! কাউন্সিলর', s)
    s = re.sub(r'!\s*scope="col"\s*colspan="?2"?\s*\|\s*Tokugawas', '! scope="col" colspan="2" | তোকুগাওয়াগণ', s)

    # টেবিলের বিশেষ হেডার ও সাব-হেডিং
    s = re.sub(r'!colspan="6"\|Modern Japan \(\[\[Empire of Japan\|[^\]]+\]\] and \[\[Postwar Japan\|[^\]]+\]\]\) \([^\)]+\)',
               '!colspan="6"|আধুনিক জাপান ([[Empire of Japan|জাপান সাম্রাজ্য]] এবং [[Postwar Japan|যুদ্ধোত্তর জাপান]]) (১৮৬৭–বর্তমান)', s)
    s = re.sub(r'\(\'\'Reigning monarch\'\'\)', "(''বর্তমান ক্ষমতাসীন সম্রাট'')", s)
    s = re.sub(r'\(\'\'interim\'\'\)', "(''ভারপ্রাপ্ত'')", s)
    s = re.sub(r'\(Go-Minoo\)', "(গো-মিনোও)", s)
    s = re.sub(r'\|\s*Incumbent\b', '| বর্তমান', s)
    s = re.sub(r'\(until\s*(?:1950|১৯৫০)\)', '(১৯৫০ পর্যন্ত)', s)
    s = re.sub(r'\bpresent\b', 'বর্তমান', s)

    return s

def translate_emperor_table_rows(text: str) -> str:
    """সম্রাটদের টেবিলের ব্যক্তিগত নাম (৫ম সেল) ও মন্তব্য (৬ষ্ঠ সেল) অনুবাদ করে।"""
    chunks = re.split(r'(?=\n\|-)', text)
    new_chunks = []

    for chunk in chunks:
        lines = chunk.splitlines(keepends=True)
        sort_idx = -1
        for idx, l in enumerate(lines):
            stripped = l.strip()
            if stripped.startswith('| {{sort|') or stripped.startswith('| {{hs|'):
                sort_idx = idx
                break

        if sort_idx != -1 and len(lines) > sort_idx + 4:
            p_line = lines[sort_idx + 4]
            p_stripped = p_line.strip()
            if p_stripped.startswith('|') and not p_stripped.startswith('| [['):
                p_val = p_stripped[1:].strip()
                tr_val = transliterate_japanese_name(p_val)
                lines[sort_idx + 4] = f"| {tr_val}\n"

        # ১৮৪৬–১৮৬৭ শাসনকালের সম্রাট কোমেই-এর মন্তব্যের ঘর (৬ষ্ঠ সেল) ফাঁকা থাকায় টেবিল ভাঙা রোধ
        if sort_idx != -1 and len(lines) == sort_idx + 5:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
            lines.append('| &nbsp;\n')

        new_chunks.append(''.join(lines))

    s = ''.join(new_chunks)

    # উত্তর রাজদরবারের অন্তর্বর্তীকালীন শাসনকালে ৪টি কলাম জুড়ে থাকা (colspan=4)
    s = re.sub(r'\|colspan="?3"?\s*\|\s*\[\[Interregnum', '|colspan="4"|[[Interregnum|অন্তর্বর্তীকালীন শাসনকাল', s)

    # নোট ও মন্তব্য পরিভাষা প্রতিস্থাপন
    EMPEROR_NOTES_REPLACEMENTS = [
        (r'\bpresumed legendary; claimed descent from the \[\[solar deity\|sun goddess\]\], \[\[Amaterasu\]\]',
         'পৌরাণিক বলে অনুমিত; [[solar deity|সূর্যদেবী]] [[Amaterasu|আমাতেরাসু]]-এর বংশধর বলে দাবি করা হয়'),
        (r'(?:3rd|৩rd)\s+son of Jimmu\b', 'জিম্মুর ৩য় পুত্র'),
        (r'son and heir of Suizei\b', 'সুইজেইয়ের পুত্র ও উত্তরাধিকারী'),
        (r'(?:2nd|২nd)\s+son of Annei\b', 'আন্নেইয়ের ২য় পুত্র'),
        (r'son and heir of Itoku\b', 'ইতোকুর পুত্র ও উত্তরাধিকারী'),
        (r'(?:2nd|২nd)\s+son of Kōshō\b', 'কোশোর ২য় পুত্র'),
        (r'Served as regent for Emperor Ōjin; not counted among the officially numbered emperors',
         'সম্রাট ওজিনের অভিভাবক হিসেবে দায়িত্ব পালন করেন; আনুষ্ঠানিকভাবে গণনাভুক্ত সম্রাটদের অন্তর্ভুক্ত নন'),
        (r'Genealogy from this point is considered accurate\.', 'এই সময় থেকে বংশলতিকা সঠিক বলে বিবেচিত।'),
        (r'reigned twice\b', 'দুইবার রাজত্ব করেন'),
        (r'Posthumously named \((?:1870|১৮৭০)\)', 'মরণোত্তর নামাঙ্কিত (১৮৭০)'),
        (r'usurped by Temmu\b', 'তেম্মু কর্তৃক সিংহাসনচ্যুত'),
        (r'dethroned by Shōtoku\b', 'শোতোকু কর্তৃক ক্ষমতাচ্যুত'),
        (r'Reunified courts in (?:1392|১৩৯২), see (?:100|১০০) below', '১৩৯২ সালে রাজদরবার পুনরেকত্রিত হয়, নিচে ১০০ নং দেখুন'),
        (r'\bpresumed legendary\b', 'পৌরাণিক বলে অনুমিত'),
        (r'\bTraditional dates, reigned twice\b', 'ঐতিহ্যবাহী তারিখ, দুইবার রাজত্ব করেন'),
        (r'\bTraditional dates; Southern Court\b', 'ঐতিহ্যবাহী তারিখ; দক্ষিণ রাজদরবার'),
        (r'\bTraditional dates\.\b', 'ঐতিহ্যবাহী তারিখ।'),
        (r'\bTraditional dates\b', 'ঐতিহ্যবাহী তারিখ'),
        (r'\bInaccurate dates\.\b', 'ত্রুটিপূর্ণ তারিখ।'),
        (r'\bInaccurate dates\b', 'ত্রুটিপূর্ণ তারিখ'),
        (r'\bSouthern Court\b', 'দক্ষিণ রাজদরবার'),
        (r'\bfirst emperor with a direct possibility of existence\b', 'অস্তিত্বের প্রত্যক্ষ সম্ভাবনা থাকা প্রথম সম্রাট'),
        (r'\bLast proto-historical emperor, deified as \[\[Hachiman\]\]', 'সর্বশেষ প্রাক-ঐতিহাসিক সম্রাট, [[Hachiman|হাচিমান]] হিসেবে দেবত্বারোপিত'),
        (r'\bFirst non-legendary female emperor \(\[\[Prince Shotoku\]\] acted as her regent\); traditional dates\.',
         'প্রথম অ-পৌরাণিক নারী সম্রাট ([[Prince Shotoku|যুবরাজ শোতোকু]] তাঁর অভিভাবক হিসেবে দায়িত্ব পালন করেন); ঐতিহ্যবাহী তারিখ।'),
        (r'\bSecond reign of Empress Kōgyoku \(35\), traditional dates\.', 'সম্রাজ্ঞী কোগিয়োকুর (৩৫) দ্বিতীয় শাসনকাল, ঐতিহ্যবাহী তারিখ।'),
        (r'\bSecond reign of Empress Kōken \(46\), traditional dates\.', 'সম্রাজ্ঞী কোকেনের (৪৬) দ্বিতীয় শাসনকাল, ঐতিহ্যবাহী তারিখ।'),
        (r'\bReunified courts, see also entry in Northern Court section\.', 'পুনরেকত্রিত রাজদরবার, উত্তর রাজদরবার অংশের অন্তর্ভুক্তিও দেখুন।'),
        (r'\bFirst Emperor of the \[\[Empire of Japan\]\]\.', '[[Empire of Japan|জাপান সাম্রাজ্যের]] প্রথম সম্রাট।'),
        (r"Crown Prince Hirohito served as \'\'\[\[Sesshō and Kampaku\|Sesshō\]\]\'\' \(Prince Regent\) 1921–1926\.",
         "যুবরাজ হিরোহিতো ১৯২১–১৯২৬ সালে ''[[Sesshō and Kampaku|সেস্‌শো]]'' (অভিভাবক যুবরাজ) হিসেবে দায়িত্ব পালন করেন।"),
        (r"Served as \'\'Sesshō\'\' \(Prince Regent\) 1921–1926\. Last Emperor of the \[\[Empire of Japan\]\]\.",
         "১৯২১–১৯২৬ সালে ''সেস্‌শো'' (অভিভাবক যুবরাজ) হিসেবে দায়িত্ব পালন করেন। [[Empire of Japan|জাপান সাম্রাজ্যের]] সর্বশেষ সম্রাট।"),
        (r"Referred to as 'the Emperor Emeritus' or \[\[Daijō Tennō\]\] \(i\.e\. \'\'His Majesty the Emperor Emeritus\'\'\) in Japanese and as Emperor Akihito in English\. His posthumous name is likely to be Emperor \[\[Heisei period\|Heisei\]\]\. He abdicated in 2019 in favor of his eldest son\s+\[\[Naruhito\]\]\. He was the first monarch since \[\[Emperor Kōkaku\]\] to do so\.",
         "জাপানিতে 'দাইজোরিও' বা [[Daijō Tennō|দাইজৌ তেন্নো]] (অর্থাৎ ''হিজ ম্যাজেস্টি দ্য এম্পেরর ইমেরিটাস'') এবং ইংরেজিতে সম্রাট আকিহিতো নামে পরিচিত। তাঁর মরণোত্তর নাম সম্রাট [[Heisei period|হেইসেই]] হওয়ার সম্ভাবনা রয়েছে। তিনি ২০১৯ সালে তাঁর জ্যেষ্ঠ পুত্র [[Naruhito|নারুহিতোর]] অনুকূলে সিংহাসন ত্যাগ করেন। [[Emperor Kōkaku|সম্রাট কোকাকুর]] পর তিনিই প্রথম কোনো সম্রাট যিনি সিংহাসন ত্যাগ করেন।"),
        (r"Referred to as 'the Present Emperor' or \'\'\[\[Emperor of Japan\|Tenno Heika\]\]\'\' \(i\.e\. \'\'His Majesty the Emperor\'\'\) in Japanese and as Emperor Naruhito in English\. His posthumous name is likely to be Emperor \[\[Reiwa period\|Reiwa\]\]\.",
         "জাপানিতে 'বর্তমান সম্রাট' বা ''[[Emperor of Japan|তেন্নো হেইকা]]'' (অর্থাৎ ''হিজ ম্যাজেস্টি দ্য এম্পেরর'') এবং ইংরেজিতে সম্রাট নারুহিতো নামে পরিচিত। তাঁর মরণোত্তর নাম সম্রাট [[Reiwa period|রেইওয়া]] হওয়ার সম্ভাবনা রয়েছে।"),
        (r'\bBCE\b', 'খ্রিস্টপূর্ব'),
        (r'\bBC\b', 'খ্রিস্টপূর্ব'),
    ]

    for pat, rep in EMPEROR_NOTES_REPLACEMENTS:
        s = re.sub(pat, rep, s)

    return s

def translate_table_content(text: str) -> str:
    """টেবিল অভ্যন্তরের কোষ, প্রতিকৃতি, লেবেল ও লিংকসমূহ বাংলায় রূপান্তর করে।"""
    s = text

    # ১. রাজনৈতিক দলের স্টাইল ও কালার টেমপ্লেট ভেতরে টেক্সট অনুবাদ (উইকিলিংকের আগে)
    for pat, rep in PARTY_COLOR_MAP:
        s = re.sub(pat, rep, s)

    # ২. প্রতিকৃতির নিচে রোমান হরফে থাকা নামের উচ্চারণ (হেপবার্ন/আইপিএ) অক্ষুণ্ণ রাখা ও তারিখ বাংলা করা
    def repl_portrait_romaji(match):
        raw_name = match.group(1).strip()
        raw_dates = match.group(2).strip()
        bn_dates = to_bengali_digits(raw_dates)
        return f"{{{{small|''{raw_name}''<br/>({bn_dates})}}}}"

    s = re.sub(r"\{\{small\|''([A-Za-z\s\.\u0100-\u017F]+)''<br\s*/>\(([^)]+)\)\}\}", repl_portrait_romaji, s)

    # হাতোয়ামা ইচিরো প্রতিকৃতির বিশেষ লাইন (বাংলা-জাপানি-ipa ফরম্যাট)
    s = s.replace('Hatoyama Ichirō<br/>(1883–1959)<br/>Rep for', "''Hatoyama Ichirō''<br/>(১৮৮৩–১৯৫৯)<br/>প্রতিনিধি:")

    # ৩. ভারপ্রাপ্ত প্রধানমন্ত্রীদের মন্তব্য অনুবাদ
    for pat, rep in EXACT_ACTING_PM_NOTES:
        s = re.sub(pat, rep, s)

    # ৪. colspan=7 বিবরণসমূহ অনুবাদ
    for en_desc, bn_desc in COLSPAN_DESCRIPTIONS.items():
        s = s.replace(en_desc, bn_desc)

    # ৫. নির্বাচন লিঙ্ক ও লেবেল অনুবাদ
    s = re.sub(r'1989 House of Councillors election', '১৯৮৯ কাউন্সিলর সভা নির্বাচন', s)
    s = re.sub(r'2009 general election', '২০০৯ সাধারণ নির্বাচন', s)
    s = re.sub(r'2012 general election', '২০১২ সাধারণ নির্বাচন', s)
    s = re.sub(r'1996 general election', '১৯৯৬ সাধারণ নির্বাচন', s)
    s = re.sub(r'1993 general election', '১৯৯৩ সাধারণ নির্বাচন', s)
    s = re.sub(r'2021 general election', '২০২১ সাধারণ নির্বাচন', s)

    # ৬. রাজনৈতিক দলসমূহের নাম ও পরিভাষা রূপান্তর
    PARTIES_REPLACEMENTS = [
        (r'\bIndependent \(politician\)\b', 'স্বতন্ত্র'),
        (r'\bIndependent\b', 'স্বতন্ত্র'),
        (r'\|\s*None\b', '| নেই'),
        (r'\bMilitary\b', 'সামরিক'),
        (r'\bLiberal Democratic Party \(Japan\)\b', 'লিবারেল ডেমোক্রেটিক পার্টি'),
        (r'\bDemocratic Party of Japan\b', 'ডেমোক্রেটিক পার্টি অব জাপান'),
        (r'\bDemocratic Party \(Japan, 1947\)\b', 'ডেমোক্রেটিক পার্টি (১৯৪৭)'),
        (r'\bDemocratic Party \(Japan, 1998\)\b', 'ডেমোক্রেটিক পার্টি (১৯৯৮)'),
        (r'\bDemocratic Liberal Party \(Japan\)\b', 'ডেমোক্রেটিক লিবারেল পার্টি'),
        (r'\bDemocratic Socialist Party \(Japan\)\b', 'ডেমোক্রেটিক সোশ্যালিস্ট পার্টি'),
        (r'\bSocial Democratic Party \(Japan\)\b', 'সোশ্যাল ডেমোক্রেটিক পার্টি'),
        (r'\bSocial Democratic Federation \(Japan\)\b', 'সোশ্যাল ডেমোক্রেটিক ফেডারেশন'),
        (r'\bJapan Socialist Party\b', 'জাপান সোশ্যালিস্ট পার্টি'),
        (r'\bSocialist Party of Japan\b', 'জাপান সোশ্যালিস্ট পার্টি'),
        (r'\bSocialist Party\b', 'সমাজতান্ত্রিক দল'),
        (r'\bLiberal Party \(Japan, 1945\)\b', 'লিবারেল পার্টি (১৯৪৫)'),
        (r'\bLiberal Party \(Japan, 1950\)\b', 'লিবারেল পার্টি (১৯৫০)'),
        (r'\bLiberal Party \(Japan, 1998\)\b', 'লিবারেল পার্টি (১৯৯৮)'),
        (r'\bNational Cooperative Party\b', 'ন্যাশনাল কোঅপারেটিভ পার্টি'),
        (r'\bNew Conservative Party \(Japan\)\b', 'নিউ কনজারভেটিভ পার্টি'),
        (r'\bNew Liberal Club\b', 'নিউ লিবারেল ক্লাব'),
        (r'\bPeople\'s New Party\b', 'পিপলস নিউ পার্টি'),
        (r'\bJapan New Party\b', 'জাপান নিউ পার্টি'),
        (r'\bJapan Renewal Party\b', 'জাপান রিনিউয়াল পার্টি'),
        (r'\bNew Party Sakigake\b', 'নতুন দল সাকিগাকে'),
        (r'\bRikken Seiyūkai\b', 'রিক্কেন সেইয়ুকাই'),
        (r'\bKenseikai\b', 'কেনসেইকাই'),
        (r'\bRikken Minseitō\b', 'রিক্কেন মিনসেইতো'),
        (r'\bTaisei Yokusankai\b', 'তাইসেই ইয়োকুসানকাই'),
    ]

    for pat, rep in PARTIES_REPLACEMENTS:
        s = re.sub(pat, rep, s)

    # ৭. উইকিলিংকসমূহ রূপান্তর (File এবং Category বাদে, :ja: অন্তর্ভুক্ত)
    def repl_link(match):
        raw = match.group(1).strip()
        if raw.startswith('File:') or raw.startswith('Image:') or raw.startswith('Category:') or raw.startswith(':Category:'):
            return match.group(0)

        if '|' in raw:
            target, label = raw.split('|', 1)
            # কালার টেমপ্লেট ও HTML ট্যাগ বাদে ভেতরের টেক্সট বাংলা কিনা চেক করা
            clean_label = re.sub(r'<[^>]+>', '', label)
            clean_label = re.sub(r'\{\{color\|[^|]+\|', '', clean_label)
            clean_label = re.sub(r'\}\}', '', clean_label)
            if not re.search(r'[a-zA-Z]', clean_label):
                return match.group(0)
            bn_name = get_bengali_japanese_name(target, label)
            return f"[[{target}|{bn_name}]]"
        else:
            if not re.search(r'[a-zA-Z]', raw):
                return match.group(0)
            bn_name = get_bengali_japanese_name(raw, "")
            return f"[[{raw}|{bn_name}]]"

    s = re.sub(r'\[\[([^\]]+)\]\]', repl_link, s)

    # ৮. মাস ও তারিখ রূপান্তর
    for pat, rep in MONTHS_MAP:
        s = re.sub(pat, rep, s)

    # ৯. সংখ্যা ও তারিখ রূপান্তর
    s = to_bengali_digits(s)

    return s

def translate_wikitable(table_text: str) -> str:
    """সম্পূর্ণ উইকিটেবিল অনুবাদ করে।"""
    s = translate_table_headers(table_text)

    # যদি সম্রাটদের টেবিল হয় (table 0)
    if 'Legendary Emperors' in table_text or 'পৌরাণিক সম্রাটগণ' in s:
        s = translate_emperor_table_rows(s)

    s = translate_table_content(s)

    # সারণির প্রতিটি |- পৃথক নতুন লাইনে থাকা নিশ্চিত করা
    s = re.sub(r'([^\n])\s*\|-', r'\1\n|-', s)

    # বাংলায় শব্দের শুরুতে কখনোই 'ৎ' বসে না (যেমন: tsunami -> সুনামি, Tsunesaburō -> সুনেসাবুরো)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসু', r'\1সু', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসা', r'\1সা', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসি', r'\1সি', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসে', r'\1সে', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎসো', r'\1সো', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎস', r'\1স', s)
    s = re.sub(r'(^|[^\u0980-\u09FF])ৎ', r'\1স', s)

    return s
