# -*- coding: utf-8 -*-
"""
CX পোস্ট-প্রসেসরের সংখ্যা রূপান্তর।

কেন্দ্রীয় বাস্তবায়ন ``common.bengali_utils.to_bengali_digits_safe``; এখানে
তার উপরে একটি বাড়তি সুরক্ষা স্তর যোগ করা হয়েছে:

* **সূত্র টেমপ্লেটের তারিখ** (``{{cite web|date=2010-07-15}}``) ASCII-ই থাকে।
  নাহলে বাংলা উইকিতে CS1 "তারিখের বিন্যাস" ত্রুটি দেখায় — প্রতি নিবন্ধে
  কয়েক ডজন ত্রুটি তৈরি হত। ২০২৬-১০-২১ যাচাইয়ে ইংরেজি নমুনায় ১২টি ও
  চীনা নমুনায় ৫৪টি এমন ভাঙা তারিখ পাওয়া গিয়েছিল।

সুরক্ষিত থাকে: HTML ট্যাগ/অ্যাট্রিবিউট, URL, File/Image নাম,
টেমপ্লেট প্যারামিটার কী (``|group1 =``, ``{{{1|...}}}``), coord,
ISBN/DOI/PMID, ``NNNpx`` মাপ, CSS রং, HTML এন্টিটি, সূত্রের তারিখ।
দৃশ্যমান লেখা, টেবিল সেল ও ক্যাপশনের অঙ্ক বাংলা হয়; ক্রমবাচকও
(``2nd`` → ``২য়``, ``6th`` → ``৬ষ্ঠ``)।
"""
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from common.bengali_utils import (  # noqa: E402  (path bootstrap first)
    BN_DIGITS,
    BN_TO_ASCII_DIGITS,
    convert_ordinals,
    fix_template_parameter_digits,
    repair_machine_identifiers,
    to_bengali_digits_safe as _to_bengali_digits_safe,
)

__all__ = [
    "BN_DIGITS",
    "BN_TO_ASCII_DIGITS",
    "convert_ordinals",
    "fix_template_parameter_digits",
    "repair_machine_identifiers",
    "to_bengali_digits_safe",
]


#: যে টেমপ্লেটগুলো সূত্র/উদ্ধৃতি — এদের ভিতরের তারিখ ও শনাক্তক যন্ত্রপাঠ্য।
#: `উদ্ধৃত …` সংযোজন: মেশিন অনুবাদে `{{cite web}}` → `{{ওয়েব উদ্ধৃতি}}` বা `{{উদ্ধৃত ওয়েব}}`,
#: `{{cite book}}` → `{{বই উদ্ধৃতি}}` বা `{{উদ্ধৃত বই}}` হয়ে যায়, তাই অনূদিত নামগুলোও পুরোপুরি সমর্থিত।
_CITATION_TEMPLATE_RE = re.compile(
    r'\{\{\s*(?:cite(?=[\s_}|])|citation\b|সাইট|উদ্ধৃত|উদ্ধৃতি|তথ্যসূত্র|'
    r'(?:[^\s_}|]+\s+)?(?:উদ্ধৃতি|উদ্ধৃত)|sfn\b|harvnb\b|harv\b)',
    re.IGNORECASE,
)

#: সূত্র টেমপ্লেটের যে প্যারামিটারগুলো ASCII তারিখ/শনাক্তক রাখতে হয়।
_CITATION_DATE_PARAM_RE = re.compile(
    r'(\|\s*(?:access-?date|accessdate|archive-?date|archivedate|date|'
    r'publication-?date|lay-?date|year|orig-?year|pmc|pmid|doi|isbn|issn|oclc|bibcode|arxiv|'
    r'আইএসবিএন|আইএসএসএন|ডিওআই|পিএমআইডি|পিএমসি|ওসিএলসি|বিবকোড|'
    r'তারিখ|সংগ্রহের-?তারিখ|সংগ্রহেরতারিখ|আর্কাইভের-?তারিখ|আর্কাইভেরতারিখ)\s*=)'
    r'([^|{}\n]+)',
    re.IGNORECASE,
)

#: মানচিত্র/স্থানাঙ্কের প্যারামিটার — Lua মডিউল পড়ে, তাই ASCII থাকতে হবে।
_MACHINE_PARAM_RE = re.compile(
    r'(\|\s*(?:zoom|frame-latitude|frame-longitude|frame-width|frame-height|'
    r'frame-zoom|marker-size|marksize|latd|latm|lats|latns|longd|longm|longs|longew|'
    r'lat_deg|lat_min|lat_sec|lon_deg|lon_min|lon_sec|lat|long)\s*=)'
    r'([^|{}\n]+)',
    re.IGNORECASE,
)

#: ফাইল লিংকের লক্ষ্য (নামস্থান) — নামের ভিতরে শব্দ/অঙ্ক বদলায় না।
_FILE_LINK_RE = re.compile(
    r'(\[\[\s*(?:File|Image|চিত্র|ফাইল|画像|ファイル|Файл|Файлы|Datei|Bild|Fichier|'
    r'Archivo|Immagine|Bestand|Plik|Soubor|Датотека|파일|文件|图像|圖片)\s*:)'
    r'([^\]|\n]+)'
)

#: URL — ভিতরের শব্দ/অঙ্ক কোনোটাই অনুবাদ বা রূপান্তর হয় না।
_URL_RE = re.compile(r'(https?://[^\s<>\]\}\|]+)')

#: `\x01` + প্রাইভেট-ইউজ চিহ্ন + `\x01` — কেন্দ্রীয় বাস্তবায়নের `\x00…\x00`
#: টোকেনের সঙ্গে সংঘর্ষ হয় না।
_MARK_BASE = 0xF000
_MARK_LIMIT = 0x700


def _template_span_end(text: str, start: int) -> int:
    """`{{` থেকে শুরু করে সমতুল্য `}}`-এর ঠিক পরের ইনডেক্স; না মিললে -1।"""
    depth = 0
    i = start
    while i < len(text) - 1:
        if text.startswith('{{', i):
            depth += 1
            i += 2
            continue
        if text.startswith('}}', i):
            depth -= 1
            i += 2
            if depth == 0:
                return i
            continue
        i += 1
    return -1


def protect_machine_spans(text: str):
    """যন্ত্রপাঠ্য অংশ (ফাইলনাম, মানচিত্র প্যারাম, সূত্রের তারিখ) ASCII রাখে।

    ফেরত দেয় ``(আড়াল_করা_লেখা, [(চিহ্ন, আসল_মান), ...])``।
    """
    saved = []

    def _make(match, group_index, _saved=saved):
        if len(_saved) >= _MARK_LIMIT:
            return match.group(0)
        marker = '\x01' + chr(_MARK_BASE + len(_saved)) + '\x01'
        _saved.append((marker, match.group(group_index)))
        lead = ''.join(
            match.group(i) for i in range(1, group_index)
        )
        return lead + marker

    def _save_date(match, _saved=saved):
        if len(_saved) >= _MARK_LIMIT:
            return match.group(0)
        marker = '\x01' + chr(_MARK_BASE + len(_saved)) + '\x01'
        _saved.append((marker, match.group(2)))
        return match.group(1) + marker

    text = _URL_RE.sub(lambda m: _make(m, 1), text)
    text = _FILE_LINK_RE.sub(lambda m: _make(m, 2), text)
    text = _MACHINE_PARAM_RE.sub(lambda m: _make(m, 2), text)

    out = []
    i = 0
    while True:
        start = text.find('{{', i)
        if start == -1:
            out.append(text[i:])
            break
        end = _template_span_end(text, start)
        if end == -1:
            # অসমাপ্ত `{{` — মেশিন অনুবাদে টেমপ্লেট বন্ধ হওয়ার `}}` হারিয়ে যায়।
            # এখানেই থামলে বাকি নথির সব তারিখ অরক্ষিত থাকত, তাই সূত্র হলে
            # শেষ পর্যন্ত বিয়োজন করে আর অন্য হলে সামনে এগোই।
            if _CITATION_TEMPLATE_RE.match(text[start:start + 40]):
                out.append(text[i:start])
                out.append(_CITATION_DATE_PARAM_RE.sub(_save_date, text[start:]))
                break
            out.append(text[i:start + 2])
            i = start + 2
            continue
        block = text[start:end]
        if _CITATION_TEMPLATE_RE.match(block):
            out.append(text[i:start])
            out.append(_CITATION_DATE_PARAM_RE.sub(_save_date, block))
            i = end
            continue
        # অন্য টেমপ্লেটের ভিতরেও সূত্র ({{cite ...}}) থাকতে পারে — ভিতরে ঢুকে খুঁজি,
        # নতুবা {{nihongo|...<ref>{{cite book|date=...}}</ref>}}-এর তারিখ বাদ পড়ে।
        out.append(text[i:start + 2])
        i = start + 2
    return ''.join(out), saved


#: পুরোনো নাম (সংগতির জন্য)
protect_citation_dates = protect_machine_spans


def restore_spans(text: str, saved) -> str:
    for marker, original in reversed(saved):
        text = text.replace(marker, original)
    return text


def to_bengali_digits_safe(text):
    """দৃশ্যমান অঙ্ক বাংলায়; সূত্রের তারিখ, URL, ফাইলনাম, coord, ISBN/DOI অক্ষত।"""
    if not text:
        return text
    masked, saved = protect_machine_spans(text)
    converted = _to_bengali_digits_safe(masked)
    restored = restore_spans(converted, saved)
    return repair_machine_identifiers(restored)
