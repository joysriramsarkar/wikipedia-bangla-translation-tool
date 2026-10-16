# -*- coding: utf-8 -*-
"""
রাশিয়ার যুক্তরাষ্ট্রীয় বিষয় ও প্রশাসনিক পরিভাষা মানচিত্র (Russian Federal Subjects & Terminology Map)
"""
import re
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from cyrillic_transliteration import romanized_russian_to_bengali

# রাশিয়ার ৮৪টি যুক্তরাষ্ট্রীয় বিষয়ের প্রমিত বাংলা উইকিপিডিয়া লিঙ্ক মানচিত্র
FEDERAL_SUBJECTS_MAP = {
    '[[Republic of Adygea]]': '[[Republic of Adygea|আদিগেয়া প্রজাতন্ত্র]]',
    '[[Altai Krai]]': '[[Altai Krai|আলতাই ক্রাই]]',
    '[[Altai Republic]]': '[[Altai Republic|আলতাই প্রজাতন্ত্র]]',
    '[[Amur Oblast]]': '[[Amur Oblast|আমুর ওব্লাস্ত]]',
    '[[Arkhangelsk Oblast]]': '[[Arkhangelsk Oblast|আরখানগেলস্ক ওব্লাস্ত]]',
    '[[Astrakhan Oblast]]': '[[Astrakhan Oblast|আস্ত্রাখান ওব্লাস্ত]]',
    '[[Bashkortostan|Republic of Bashkortostan]]': '[[Bashkortostan|বাশকর্তোস্তান প্রজাতন্ত্র]]',
    '[[Belgorod Oblast]]': '[[Belgorod Oblast|বেলগোরোদ ওব্লাস্ত]]',
    '[[Bryansk Oblast]]': '[[Bryansk Oblast|ব্রিয়ানস্ক ওব্লাস্ত]]',
    '[[Republic of Buryatia]]': '[[Republic of Buryatia|বুরিয়াতিয়া প্রজাতন্ত্র]]',
    '[[Chechen Republic]]': '[[Chechen Republic|চেচেন প্রজাতন্ত্র]]',
    '[[Chelyabinsk Oblast]]': '[[Chelyabinsk Oblast|চেলিয়াবিনস্ক ওব্লাস্ত]]',
    '[[Chukotka Autonomous Okrug]]': '[[Chukotka Autonomous Okrug|চুকোতকা স্বায়ত্তশাসিত ওক্রুগ]]',
    '[[Chuvash Republic]]': '[[Chuvash Republic|চুভাশ প্রজাতন্ত্র]]',
    '[[Republic of Crimea (Russia)|Republic of Crimea]]': '[[Republic of Crimea (Russia)|ক্রিমিয়া প্রজাতন্ত্র]]',
    '[[Republic of Dagestan]]': '[[Republic of Dagestan|দাগেস্তান প্রজাতন্ত্র]]',
    '[[Republic of Ingushetia]]': '[[Republic of Ingushetia|ইঙ্গুশেতিয়া প্রজাতন্ত্র]]',
    '[[Irkutsk Oblast]]': '[[Irkutsk Oblast|ইরকুটস্ক ওব্লাস্ত]]',
    '[[Ivanovo Oblast]]': '[[Ivanovo Oblast|ইভানভো ওব্লাস্ত]]',
    '[[Jewish Autonomous Oblast]]': '[[Jewish Autonomous Oblast|ইহুদি স্বায়ত্তশাসিত ওব্লাস্ত]]',
    '[[Kabardino-Balkar Republic]]': '[[Kabardino-Balkar Republic|কাবার্দিনো-বালকার প্রজাতন্ত্র]]',
    '[[Kaliningrad Oblast]]': '[[Kaliningrad Oblast|কালিনিনগ্রাদ ওব্লাস্ত]]',
    '[[Republic of Kalmykia]]': '[[Republic of Kalmykia|কালমিকিয়া প্রজাতন্ত্র]]',
    '[[Kaluga Oblast]]': '[[Kaluga Oblast|কালুগা ওব্লাস্ত]]',
    '[[Kamchatka Krai]]': '[[Kamchatka Krai|কামচাতকা ক্রাই]]',
    '[[Karachay-Cherkess Republic]]': '[[Karachay-Cherkess Republic|কারাচায়-চের্কেস প্রজাতন্ত্র]]',
    '[[Republic of Karelia]]': '[[Republic of Karelia|কারেলিয়া প্রজাতন্ত্র]]',
    '[[Kemerovo Oblast]]': '[[Kemerovo Oblast|কেমেরোভো ওব্লাস্ত]]',
    '[[Khabarovsk Krai]]': '[[Khabarovsk Krai|খাবারভস্ক ক্রাই]]',
    '[[Republic of Khakassia]]': '[[Republic of Khakassia|খাকাসিয়া প্রজাতন্ত্র]]',
    '[[Khanty-Mansi Autonomous Okrug]]': '[[Khanty-Mansi Autonomous Okrug|খান্তি-মান্সি স্বায়ত্তশাসিত ওক্রুগ]]',
    '[[Kirov Oblast]]': '[[Kirov Oblast|কিরোভ ওব্লাস্ত]]',
    '[[Komi Republic]]': '[[Komi Republic|কোমি প্রজাতন্ত্র]]',
    '[[Kostroma Oblast]]': '[[Kostroma Oblast|কোস্ত্রোমা ওব্লাস্ত]]',
    '[[Krasnodar Krai]]': '[[Krasnodar Krai|ক্রাসনোদার ক্রাই]]',
    '[[Krasnoyarsk Krai]]': '[[Krasnoyarsk Krai|ক্রাসনোয়ারস্ক ক্রাই]]',
    '[[Kurgan Oblast]]': '[[Kurgan Oblast|কুরগান ওব্লাস্ত]]',
    '[[Kursk Oblast]]': '[[Kursk Oblast|কুরস্ক ওব্লাস্ত]]',
    '[[Leningrad Oblast]]': '[[Leningrad Oblast|লেনিনগ্রাদ ওব্লাস্ত]]',
    '[[Lipetsk Oblast]]': '[[Lipetsk Oblast|লিপেৎস্ক ওব্লাস্ত]]',
    '[[Magadan Oblast]]': '[[Magadan Oblast|মাগাদান ওব্লাস্ত]]',
    '[[Mari El Republic]]': '[[Mari El Republic|মারি এল প্রজাতন্ত্র]]',
    '[[Republic of Mordovia]]': '[[Republic of Mordovia|মর্ডোভিয়া প্রজাতন্ত্র]]',
    '[[Moscow|Federal city of Moscow]]': '[[Moscow|যুক্তরাষ্ট্রীয় শহর মস্কো]]',
    '[[Murmansk Oblast]]': '[[Murmansk Oblast|মুরমানস্ক ওব্লাস্ত]]',
    '[[Nenets Autonomous Okrug]]': '[[Nenets Autonomous Okrug|নেনিৎস স্বায়ত্তশাসিত ওক্রুগ]]',
    '[[Nizhny Novgorod Oblast]]': '[[Nizhny Novgorod Oblast|নিঝনি নভগোরোদ ওব্লাস্ত]]',
    '[[Republic of North Ossetia–Alania]]': '[[Republic of North Ossetia–Alania|উত্তর ওসেতিয়া-আলানিয়া প্রজাতন্ত্র]]',
    '[[Novgorod Oblast]]': '[[Novgorod Oblast|নভগোরোদ ওব্লাস্ত]]',
    '[[Novosibirsk Oblast]]': '[[Novosibirsk Oblast|নভোসিবির্স্ক ওব্লাস্ত]]',
    '[[Omsk Oblast]]': '[[Omsk Oblast|ওমস্ক ওব্লাস্ত]]',
    '[[Orenburg Oblast]]': '[[Orenburg Oblast|ওরেনবার্গ ওব্লাস্ত]]',
    '[[Oryol Oblast]]': '[[Oryol Oblast|ওরিওল ওব্লাস্ত]]',
    '[[Penza Oblast]]': '[[Penza Oblast|পেনজা ওব্লাস্ত]]',
    '[[Perm Krai]]': '[[Perm Krai|পের্ম ক্রাই]]',
    '[[Primorsky Krai]]': '[[Primorsky Krai|প্রিমোরস্কি ক্রাই]]',
    '[[Pskov Oblast]]': '[[Pskov Oblast|পসকভ ওব্লাস্ত]]',
    '[[Rostov Oblast]]': '[[Rostov Oblast|রস্তভ ওব্লাস্ত]]',
    '[[Ryazan Oblast]]': '[[Ryazan Oblast|রিয়াজান ওব্লাস্ত]]',
    '[[Saint Petersburg|Federal city of Saint Petersburg]]': '[[Saint Petersburg|যুক্তরাষ্ট্রীয় শহর সেন্ট পিটার্সবার্গ]]',
    '[[Sakha Republic]]': '[[Sakha Republic|সাখা প্রজাতন্ত্র]]',
    '[[Sakhalin Oblast]]': '[[Sakhalin Oblast|সাখালিন ওব্লাস্ত]]',
    '[[Samara Oblast]]': '[[Samara Oblast|সামারা ওব্লাস্ত]]',
    '[[Saratov Oblast]]': '[[Saratov Oblast|সারাতভ ওব্লাস্ত]]',
    '[[Sevastopol|Federal city of Sevastopol]]': '[[Sevastopol|যুক্তরাষ্ট্রীয় শহর সেভাস্তোপোল]]',
    '[[Smolensk Oblast]]': '[[Smolensk Oblast|স্মোলেনস্ক ওব্লাস্ত]]',
    '[[Stavropol Krai]]': '[[Stavropol Krai|স্ত্যাভরোপোল ক্রাই]]',
    '[[Sverdlovsk Oblast]]': '[[Sverdlovsk Oblast|স্বার্দলোভস্ক ওব্লাস্ত]]',
    '[[Tambov Oblast]]': '[[Tambov Oblast|তাম্বভ ওব্লাস্ত]]',
    '[[Republic of Tatarstan]]': '[[Republic of Tatarstan|তাতারস্তান প্রজাতন্ত্র]]',
    '[[Tomsk Oblast]]': '[[Tomsk Oblast|তমস্ক ওব্লাস্ত]]',
    '[[Tula Oblast]]': '[[Tula Oblast|তুলা ওব্লাস্ত]]',
    '[[Tuva Republic]]': '[[Tuva Republic|তুভা প্রজাতন্ত্র]]',
    '[[Tver Oblast]]': '[[Tver Oblast|তভের ওব্লাস্ত]]',
    '[[Tyumen Oblast]]': '[[Tyumen Oblast|তিউমেন ওব্লাস্ত]]',
    '[[Udmurt Republic]]': '[[Udmurt Republic|উদমুর্ত প্রজাতন্ত্র]]',
    '[[Ulyanovsk Oblast]]': '[[Ulyanovsk Oblast|উলিয়ানভস্ক ওব্লাস্ত]]',
    '[[Vladimir Oblast]]': '[[Vladimir Oblast|ভ্লাদিমির ওব্লাস্ত]]',
    '[[Volgograd Oblast]]': '[[Volgograd Oblast|ভলগোগ্রাদ ওব্লাস্ত]]',
    '[[Vologda Oblast]]': '[[Vologda Oblast|ভলোগদা ওব্লাস্ত]]',
    '[[Voronezh Oblast]]': '[[Voronezh Oblast|ভোরোনেঝ ওব্লাস্ত]]',
    '[[Yamalo-Nenets Autonomous Okrug]]': '[[Yamalo-Nenets Autonomous Okrug|ইয়ামালো-নেনিৎস স্বায়ত্তশাসিত ওক্রুগ]]',
    '[[Yaroslavl Oblast]]': '[[Yaroslavl Oblast|ইয়ারোস্লাভল ওব্লাস্ত]]',
    '[[Zabaykalsky Krai]]': '[[Zabaykalsky Krai|জাবায়কালস্কি ক্রাই]]',
}

def translate_locality_link(match):
    """উইকিলিংক [[Target|Label]] বা [[Target]] এর ভেতরের নামকে বাংলায় প্রতিবর্ণীকরণ করে।"""
    target = match.group(1)
    if '|' in target:
        link_target, label = target.split('|', 1)
        bn_label = romanized_russian_to_bengali(label)
        return f"[[{link_target}|{bn_label}]]"
    else:
        bn_label = romanized_russian_to_bengali(target)
        return f"[[{target}|{bn_label}]]"

def translate_admin_center(center_text: str) -> str:
    """প্রশাসনিক কেন্দ্র কলাম অনুবাদ করে।"""
    s = center_text.strip()
    if not s or s == '&mdash;' or s == '—' or s == '-':
        return s

    # ১. শহরের ধরন প্রতিস্থাপন (Locality types)
    # stanitsa
    s = re.sub(r"''\[\[stanitsa\]\]''\s+of\s+", "[[স্তানিৎসা]]: ", s, flags=re.I)
    s = re.sub(r"''stanitsa''\s+of\s+", "স্তানিৎসা: ", s, flags=re.I)
    
    # aul
    s = re.sub(r"''\[\[aul\]\]''\s+of\s+", "[[আউল]]: ", s, flags=re.I)
    s = re.sub(r"''aul''\s+of\s+", "আউল: ", s, flags=re.I)

    # selo
    s = re.sub(r"''\[\[village#Russia\|selo\]\]''\s+of\s+", "[[গ্রাম (রাশিয়া)|সেলো]]: ", s, flags=re.I)
    s = re.sub(r"''selo''\s+of\s+", "সেলো: ", s, flags=re.I)

    # urban-type settlement / work settlement
    s = re.sub(r"\[\[urban-type settlement\|work settlement\]\]\s+of\s+", "[[শহুরে ধরনের বসতি|শ্রমিক বসতি]]: ", s, flags=re.I)
    s = re.sub(r"\[\[urban-type settlement\]\]\s+of\s+", "[[শহুরে ধরনের বসতি]]: ", s, flags=re.I)
    s = re.sub(r"urban-type settlement\s+of\s+", "শহুরে ধরনের বসতি: ", s, flags=re.I)

    # settlement
    s = re.sub(r"settlement\s+of\s+", "বসতি: ", s, flags=re.I)
    s = re.sub(r"work settlement\s+of\s+", "শ্রমিক বসতি: ", s, flags=re.I)

    # town / city
    s = re.sub(r"town\s+of\s+", "শহর: ", s, flags=re.I)
    s = re.sub(r"city\s+of\s+", "নগর: ", s, flags=re.I)

    # sloboda
    s = re.sub(r"''sloboda''\s+of\s+", "স্লোবোদা: ", s, flags=re.I)

    # station
    s = re.sub(r"station\s+of\s+", "রেল স্টেশন: ", s, flags=re.I)

    # ২. উইকিলিংকে থাকা এলাকা নাম বাংলায় রূপান্তর
    # কিন্তু স্তানিৎসা, গ্রাম, ইত্যাদি লিংক অক্ষুণ্ণ রাখতে হবে
    def repl_link(m):
        target = m.group(1)
        # যদি ইতোমধ্যে বাংলা বা উইকি বিভাগ লিংক হয়
        if any(w in target for w in ['স্তানিৎসা', 'আউল', 'গ্রাম', 'শহুরে ধরনের বসতি', 'village#Russia']):
            return m.group(0)
        return translate_locality_link(m)

    s = re.sub(r'\[\[([^\]]+)\]\]', repl_link, s)
    return s

def translate_municipal_note(note_text: str) -> str:
    """পৌর নিগম সম্পর্কিত মন্তব্য অনুবাদ করে।"""
    s = note_text.strip()
    if not s or s == '&mdash;' or s == '—' or s == '-':
        return s

    if 'Despite being' in s:
        return '[[city of federal subject significance|প্রশাসনিক জেলা থেকে পৃথকভাবে অন্তর্ভুক্ত হওয়া]] সত্ত্বেও, [[Kropotkin, Krasnodar Krai|ক্রপোটকিন]] শহরটি কাভকাজস্কি পৌর জেলার অন্তর্ভুক্ত এবং এর প্রশাসনিক কেন্দ্র হিসেবে কাজ করে'

    if 'Solovetskoye' in s:
        return 'প্রিমোরস্কি পৌর জেলার অধীন সোলোভেৎস্কোয়ে গ্রামীণ বসতি হিসেবে নিগমিত'

    m_split = re.match(r'Split between (.*?) Urban Okrug and (.*?) Urban Okrug', s)
    if m_split:
        okrug1 = romanized_russian_to_bengali(m_split.group(1))
        okrug2 = romanized_russian_to_bengali(m_split.group(2))
        return f'{okrug1} নগর ওক্রুগ এবং {okrug2} নগর ওক্রুগের মধ্যে বিভক্ত'

    if '[[Anapa Urban Okrug]]' in s:
        return '[[Anapa Urban Okrug|আনাপা নগর ওক্রুগ]]-এর অংশ হিসেবে নিগমিত'

    m_part = re.match(r'Incorporated as a part of (.*?) Urban Okrug', s)
    if m_part:
        okrug = romanized_russian_to_bengali(m_part.group(1))
        return f'{okrug} নগর ওক্রুগের অংশ হিসেবে নিগমিত'

    if 'Novaya Zemlya' in s:
        return 'নোভায়া জেমলিয়া [[Subdivisions of Russia#Municipal divisions|নগর ওক্রুগ]] হিসেবে নিগমিত'

    m_inc = re.match(r'Incorporated as (.*?) Urban Okrug', s)
    if m_inc:
        okrug = romanized_russian_to_bengali(m_inc.group(1))
        return f'{okrug} নগর ওক্রুগ হিসেবে নিগমিত'

    return s

