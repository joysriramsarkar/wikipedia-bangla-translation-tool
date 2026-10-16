# -*- coding: utf-8 -*-
"""
একক / বড় সংখ্যা / তারিখ (প্রোটোটাইপ ধাপ-২)।

স্ক্রিনশটে যা বাকি ছিল:
- `932.166 billion`, `172.917 billion` → শুধু অঙ্ক নয়, `billion → বিলিয়ন`
- `km2 / sq mi`, `/km2` → `বর্গকিমি / বর্গমাইল`
- `October 16, 2026` (আমেরিকান) → `১৬ অক্টোবর ২০২৬`
- মাসের নাম: January → জানুয়ারি …

নীতি: শব্দ বদল আগে, অঙ্ক বদল পরে (bn_digits_safe দিয়ে)।
টেকনিক্যাল টোকেন (URL/ref/coord) এখানে ছোঁয়া হয় না — সেটা
bn_digits_safe-এর দায়িত্ব; এই মডিউল শুধু দৃশ্যমান শব্দে কাজ করে।
"""
import re

LARGE_NUMBERS = {
    "trillion": "ট্রিলিয়ন",
    "billion": "বিলিয়ন",
    "million": "মিলিয়ন",
    "thousand": "হাজার",
}

# একবচন/বহুবচন দুটোই ধরা হয় (billion/billions)
def translate_large_numbers(text: str) -> str:
    def _repl(m: re.Match) -> str:
        return LARGE_NUMBERS[m.group(1).lower()]
    return re.sub(
        r"\b(trillion|billion|million|thousand)s?\b",
        _repl,
        text,
        flags=re.IGNORECASE,
    )


# একক: দীর্ঘ রূপ আগে (sq mi), তারপর সংক্ষিপ্ত (km2, km²)
UNIT_MAP = [
    (r"\bsq\s*\.?\s*mi\b\.?", "বর্গমাইল"),
    (r"\bkm2\b", "বর্গকিমি"),
    (r"km²", "বর্গকিমি"),
    (r"কিমি²", "বর্গকিমি"),
    (r"\bm2\b", "বর্গমিটার"),
    (r"m²", "বর্গমিটার"),
    (r"মি²", "বর্গমিটার"),
    (r"/km2\b", "/বর্গকিমি"),
    (r"/sq\s*mi\b", "/বর্গমাইল"),
    (r"\bkm/h\b", "কিমি/ঘণ্টা"),
    (r"\bkm\b", "কিমি"),
    (r"\bhrs?\b", "ঘণ্টা"),
]

def translate_units(text: str) -> str:
    s = text
    for pat, bn in UNIT_MAP:
        s = re.sub(pat, bn, s, flags=re.IGNORECASE)
    return s


MONTHS = {
    "January": "জানুয়ারি", "February": "ফেব্রুয়ারি", "March": "মার্চ",
    "April": "এপ্রিল", "May": "মে", "June": "জুন",
    "July": "জুলাই", "August": "আগস্ট", "September": "সেপ্টেম্বর",
    "October": "অক্টোবর", "November": "নভেম্বর", "December": "ডিসেম্বর",
    "Jan": "জানুয়ারি", "Feb": "ফেব্রুয়ারি", "Mar": "মার্চ",
    "Apr": "এপ্রিল", "Jun": "জুন", "Jul": "জুলাই",
    "Aug": "আগস্ট", "Sep": "সেপ্টেম্বর", "Sept": "সেপ্টেম্বর",
    "Oct": "অক্টোবর", "Nov": "নভেম্বর", "Dec": "ডিসেম্বর",
}

def translate_months(text: str) -> str:
    """আমেরিকান `October 16, 2026` → `16 অক্টোবর 2026` (অঙ্ক পরে বাংলায় হবে)।"""
    s = text
    # October 16, 2026 → 16 October 2026 (মাস পরে বাংলায়)
    s = re.sub(
        r"\b(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+(\d{1,2}),\s+(\d{4})\b",
        r"\2 \1 \3",
        s,
    )
    for en, bn in MONTHS.items():
        s = re.sub(rf"\b{en}\b", bn, s)
    return s


def fix_units_dates(text: str) -> str:
    """শব্দ-স্তরের ফিক্স (অঙ্ক ছাড়া)। পাইপলাইনে অঙ্ক পরে বসে।"""
    s = translate_large_numbers(text)
    s = translate_units(s)
    s = translate_months(s)
    return s
