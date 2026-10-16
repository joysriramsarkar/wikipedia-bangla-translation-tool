#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ইংরেজি সংখ্যা পরীক্ষক (English Digit Checker)
================================================
অনূদিত বাংলা উইকিপিডিয়া ফাইলে অবশিষ্ট ইংরেজি সংখ্যা খুঁজে
তালিকাবদ্ধ করে। HTML অ্যাট্রিবিউট, URL ও ref-এর ভেতরের সংখ্যা বাদ দেওয়া হয়।

ব্যবহার:
    python scripts/check_digits.py input.txt
    python scripts/check_digits.py *.txt --fix
"""
import sys
import re
import os
import argparse

# সংরক্ষিত অঞ্চল: URL, HTML অ্যাট্রিবিউট, <ref>, ISBN,좌표
PROTECTED_PATTERNS = [
    r'https?://[^\s\]|]+',
    r'<ref\b[^>]*>.*?</ref>',
    r'<ref\b[^>]*/\s*>',
    r'\bISBN\s*[\d-]+',
    r'colspan="?\d+"?',
    r'rowspan="?\d+"?',
    r'width="?\d+[%px]*"?',
    r'style="[^"]*"',
]

EN_DIGIT_RE = re.compile(r'[0-9]')
ORDINAL_RE = re.compile(r'\b(\d+)(st|nd|rd|th)\b')
BENGALI_ORDINAL = ['', 'ম', 'য়', 'র', 'ম', 'ম', 'ষ্ঠ', 'ম', 'ম', 'ম', 'ম']

BN_MAP = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
ORDINAL_MAP = {'st': '১ম', 'nd': '২য়', 'rd': '৩য়', 'th': 'তম'}


def to_bn_digits(text: str) -> str:
    return text.translate(BN_MAP)


def mask_protected(text: str):
    """সংরক্ষিত অঞ্চল মাস্ক করে টোকেন তালিকা ফেরত দেয়।"""
    tokens = []
    masked = text
    for pat in PROTECTED_PATTERNS:
        def repl(m, store=tokens):
            idx = len(store)
            store.append(m.group(0))
            return f'\x00PROT{idx}\x00'
        masked = re.sub(pat, repl, masked, flags=re.DOTALL)
    return masked, tokens


def restore_protected(text: str, tokens: list) -> str:
    for i, tok in enumerate(tokens):
        text = text.replace(f'\x00PROT{i}\x00', tok)
    return text


def check_file(path: str) -> list:
    """ফাইলে ইংরেজি সংখ্যার অবস্থান তালিকা ফেরত দেয়।"""
    issues = []
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        masked, _ = mask_protected(line)
        if EN_DIGIT_RE.search(masked):
            issues.append((i, line.rstrip()))
    return issues


def fix_file(path: str) -> int:
    """ফাইলে ইংরেজি সংখ্যা বাংলায় রূপান্তর করে; পরিবর্তনের সংখ্যা ফেরত দেয়।"""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    masked, tokens = mask_protected(text)
    fixed_masked = to_bn_digits(masked)
    # Ordinals: 1st -> ১ম, 2nd -> ২য়, 3rd -> ৩য়, Nth -> Nতম
    def ordinal_repl(m):
        n = to_bn_digits(m.group(1))
        suffix = m.group(2)
        bn_sfx = {'st': 'ম', 'nd': 'য়', 'rd': 'য়', 'th': 'তম'}.get(suffix, suffix)
        return f'{n}{bn_sfx}'
    fixed_masked = ORDINAL_RE.sub(ordinal_repl, fixed_masked)
    fixed = restore_protected(fixed_masked, tokens)
    count = sum(1 for a, b in zip(text, fixed) if a != b)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    return count


def main():
    parser = argparse.ArgumentParser(
        description='বাংলা উইকিপিডিয়া ফাইলে ইংরেজি সংখ্যা পরীক্ষা করে।'
    )
    parser.add_argument('files', nargs='+', help='পরীক্ষা করার ফাইল(সমূহ)')
    parser.add_argument('--fix', action='store_true', help='স্বয়ংক্রিয়ভাবে বাংলায় রূপান্তর করুন')
    args = parser.parse_args()

    total_issues = 0
    for path in args.files:
        if not os.path.exists(path):
            print(f"সতর্কতা: ফাইল পাওয়া যায়নি: {path}")
            continue
        if args.fix:
            changed = fix_file(path)
            print(f"{path}: {changed}টি অক্ষর পরিবর্তিত")
        else:
            issues = check_file(path)
            total_issues += len(issues)
            if issues:
                print(f"\n=== {path} ===")
                for lineno, line in issues[:10]:
                    print(f"  লাইন {lineno}: {line[:80]}")
                if len(issues) > 10:
                    print(f"  ... আরও {len(issues) - 10}টি লাইন")

    if not args.fix:
        print(f"\nমোট সমস্যাযুক্ত লাইন: {total_issues}")
        sys.exit(0 if total_issues == 0 else 1)


if __name__ == '__main__':
    main()
