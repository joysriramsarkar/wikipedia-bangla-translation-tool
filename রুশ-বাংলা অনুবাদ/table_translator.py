# -*- coding: utf-8 -*-
"""
রুশ-বাংলা সারণী অনুবাদক (Russian-Bengali Table Translator)
উইকিপিডিয়া রাশিয়ার জেলাসমূহের সারণী সম্পূর্ণ প্রমিত বাংলায় অনুবাদ করে।
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
        spec = importlib.util.spec_from_file_location(f"ru_{mod_name}", p)
        if spec and spec.loader:
            m = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(m)
            return m
    return None

_cyr = _load_local_mod("cyrillic_transliteration")
get_bengali_district_name = getattr(_cyr, 'get_bengali_district_name', lambda x, y: "")

_fed = _load_local_mod("federal_subjects")
translate_admin_center = getattr(_fed, 'translate_admin_center', lambda x: x)
translate_municipal_note = getattr(_fed, 'translate_municipal_note', lambda x: x)

_num = _load_local_mod("number_converter")
to_bengali_digits = getattr(_num, 'to_bengali_digits', lambda x: x)


def translate_table_header(header_text: str) -> str:
    """উইকিটেবিল শিরোনাম বাংলায় অনুবাদ করে।"""
    s = header_text
    s = re.sub(r'!\s*District\b', '! জেলা', s)
    s = re.sub(r'!\s*Russian name\b', '! রুশ নাম', s)
    s = re.sub(r'!\s*\[\[Administrative center\]\]', '! [[প্রশাসনিক কেন্দ্র]]', s)
    s = re.sub(r'!\s*\[\[Adyghe language\|Adyghe\]\] name', '! [[Adyghe language|আদিগেয়ীয়]] নাম', s)
    s = re.sub(r'!\s*\[\[Bashkir language\|Bashkir\]\] name', '! [[Bashkir language|বাশকির]] নাম', s)
    s = re.sub(r'!\s*\[\[Buryat language\|Buryat\]\] name', '! [[Buryat language|বুরিয়াত]] নাম', s)
    s = re.sub(r'!\s*\[\[Chechen language\|Chechen\]\] name', '! [[Chechen language|চেচেন]] নাম', s)
    s = re.sub(r'!\s*\[\[Southern Altai language\|Altai\]\] name', '! [[Southern Altai language|আলতাই]] নাম', s)
    s = re.sub(r'!\s*class="unsortable"\s*\|\s*Notes on municipal incorporation', '! class="unsortable" | পৌর নিগম সম্পর্কিত মন্তব্য', s)
    s = re.sub(r'!\s*Population<br />\(\[\[Russian Census \(2010\)\|2010 Census\]\]\)(<ref[^>]*>.*?</ref>|<ref[^>]*/>)', r'! জনসংখ্যা<br />([[Russian Census (2010)|২০১০ আদমশুমারি]])\1', s)
    s = re.sub(r'!\s*Population<br />\(2013 est\.\)(<ref[^>]*>.*?</ref>)', r'! জনসংখ্যা<br />(২০১৩ আনুমানিক)\1', s)
    s = re.sub(r'!\s*Population\b', '! জনসংখ্যা', s)
    return s

def translate_table_row(row_str: str) -> str:
    """একটি সারি অনুবাদ করে।

    সারির শুরুের নিউলাইন/হোয়াইটস্পেস অক্ষত রাখা হয়: সারণিতে `|`-এর আগে
    সারি-বিভাজক `\n|-` বাধ্যতামূলক। আগে `translate_admin_center()`-এর
    `.strip()` ওই নিউলাইন মুছে দিত, ফলে `|-` পরের ঘরের সাথে জুড়ে গিয়ে
    (`|-|[[...`) সারণির সারি ভাঙত।
    """
    s = row_str
    leading = re.match(r'^\s*', s).group(0)
    if leading:
        s = s[len(leading):]

    # ১. প্রথম উইকিলিংকটি জেলা লিঙ্ক, যা বাংলা জেলায় রূপান্তরিত হবে
    m_dist = re.search(r'\[\[([^\]]+)\]\]', s)
    m_ru = re.search(r'\{\{lang\|ru\|([^}]+)\}\}', s)
    if m_dist and m_ru:
        dist_raw = m_dist.group(1)
        base_target = dist_raw.split('|')[0]
        bn_district = get_bengali_district_name(m_ru.group(0), dist_raw)
        new_link = f'[[{base_target}|{bn_district}]]'
        s = s[:m_dist.start()] + new_link + s[m_dist.end():]

    # ২. পৌর নিগম সম্পর্কিত মন্তব্য
    def repl_note(m):
        prefix = m.group(1)
        note_body = m.group(2)
        return prefix + translate_municipal_note(note_body)

    s = re.sub(r'(\|\||\n\|)\s*(Incorporated as [^\n\|]+|Split between [^\n\|]+|Despite being [^\n\|]+)', repl_note, s)

    # ৩. প্রশাসনিক কেন্দ্র
    s = translate_admin_center(s)

    # ৪. প্রযোজ্য নয় (N/A) -> ড্যাশ (—)
    s = re.sub(r'(\|\||\n\|)\s*N/A\s*(\|\||\n|\Z)', r'\1 — \2', s)

    # ৫. সংখ্যা ও জনসংখ্যা রূপান্তর
    s = to_bengali_digits(s)

    return leading + s

def translate_wikitable(table_text: str) -> str:
    """সম্পূর্ণ উইকিটেবিল অনুবাদ করে।"""
    chunks = table_text.split('\n|-')
    if len(chunks) < 2:
        return table_text

    translated_chunks = []
    for i, chunk in enumerate(chunks):
        is_last = False
        if chunk.rstrip().endswith('|}'):
            is_last = True
            chunk = re.sub(r'\n?\|\}$', '', chunk.rstrip())

        if '!' in chunk:
            tr_chunk = translate_table_header(chunk)
        elif i > 0 and chunk.strip() and not chunk.strip().startswith('{'):
            tr_chunk = translate_table_row(chunk)
        else:
            tr_chunk = chunk

        if is_last:
            tr_chunk = tr_chunk + '\n|}'

        translated_chunks.append(tr_chunk)

    return '\n|-'.join(translated_chunks)

