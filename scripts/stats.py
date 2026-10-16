#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
অনুবাদ পরিসংখ্যান (Translation Statistics)
============================================
প্রজেক্টের সমস্ত অনূদিত ফাইলের পরিসংখ্যান প্রদর্শন করে:
লাইন সংখ্যা, ইংরেজি অবশিষ্ট, সংখ্যা রূপান্তরের অবস্থা ইত্যাদি।

ব্যবহার:
    python scripts/stats.py
    python scripts/stats.py --lang japanese
"""
import sys
import os
import re
import argparse
from pathlib import Path


ROOT = Path(__file__).parent.parent

LANG_DIRS = {
    'chinese':  'চীনা-বাংলা অনুবাদ',
    'japanese': 'জাপানি-বাংলা অনুবাদ',
    'russian':  'রুশ-বাংলা অনুবাদ',
    'german':   'জার্মান-বাংলা অনুবাদ',
    'english':  'ইংরেজি-বাংলা অনুবাদ',
}

BN_DIGIT_RE = re.compile(r'[০-৯]')
EN_DIGIT_RE = re.compile(r'[0-9]')
LATIN_LETTER_RE = re.compile(r'[a-zA-Z]{3,}')  # 3+ ল্যাটিন অক্ষর


def analyze_file(path: Path) -> dict:
    try:
        text = path.read_text(encoding='utf-8')
    except Exception:
        return {}
    lines = text.splitlines()
    bn_digits = len(BN_DIGIT_RE.findall(text))
    en_digits = len(EN_DIGIT_RE.findall(text))
    # ইংরেজি অক্ষর শুধু (URL/ref বাদে)
    clean = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
    clean = re.sub(r'https?://\S+', '', clean)
    latin_words = len(LATIN_LETTER_RE.findall(clean))
    return {
        'lines': len(lines),
        'bn_digits': bn_digits,
        'en_digits': en_digits,
        'latin_words': latin_words,
        'digit_ratio': round(bn_digits / (bn_digits + en_digits) * 100, 1) if (bn_digits + en_digits) > 0 else 100.0,
    }


def show_stats(lang_filter: str = None):
    langs = {k: v for k, v in LANG_DIRS.items() if not lang_filter or k == lang_filter}
    grand_total = {'files': 0, 'lines': 0, 'en_digits': 0, 'latin_words': 0}

    for lang, dirname in langs.items():
        lang_dir = ROOT / dirname
        if not lang_dir.exists():
            continue
        txt_files = list(lang_dir.glob('*(বাংলা).txt')) + list(lang_dir.glob('*বাংলা*.txt'))
        if not txt_files:
            continue

        print(f"\n{'='*60}")
        print(f"ভাষা: {dirname}")
        print(f"{'='*60}")
        print(f"{'ফাইল':<40} {'লাইন':>6} {'বাংলা%':>7} {'লাতিন':>7}")
        print('-' * 60)

        for fp in sorted(txt_files):
            stats = analyze_file(fp)
            if not stats:
                continue
            grand_total['files'] += 1
            grand_total['lines'] += stats['lines']
            grand_total['en_digits'] += stats['en_digits']
            grand_total['latin_words'] += stats['latin_words']
            status = '✓' if stats['en_digits'] == 0 and stats['latin_words'] < 10 else '⚠'
            print(f"{status} {fp.name[:38]:<38} {stats['lines']:>6} "
                  f"{stats['digit_ratio']:>6}% {stats['latin_words']:>7}")

    print(f"\n{'='*60}")
    print(f"সারসংক্ষেপ: {grand_total['files']}টি ফাইল, "
          f"{grand_total['lines']}টি লাইন, "
          f"অবশিষ্ট ইংরেজি সংখ্যা: {grand_total['en_digits']}, "
          f"লাতিন শব্দ: {grand_total['latin_words']}")


def main():
    parser = argparse.ArgumentParser(
        description='অনুবাদ প্রকল্পের পরিসংখ্যান প্রদর্শন করে।'
    )
    parser.add_argument('--lang', choices=list(LANG_DIRS.keys()),
                        help='নির্দিষ্ট ভাষার পরিসংখ্যান দেখান')
    args = parser.parse_args()
    show_stats(args.lang)


if __name__ == '__main__':
    main()
