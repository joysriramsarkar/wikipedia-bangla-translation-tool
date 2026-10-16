#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
নুক্তা সংশোধক (Nukta Normalizer)
=====================================
বাংলা উইকিপিডিয়ার যেকোনো ফাইলে বিশ্লিষ্ট নুক্তাযুক্ত বর্ণ
(য+়, ড+়, ঢ+়) খুঁজে প্রি-কম্পোজড বর্ণে (য়, ড়, ঢ়) রূপান্তর করে।

ব্যবহার:
    python scripts/fix_nukta.py input.txt
    python scripts/fix_nukta.py input.txt -o output.txt
"""
import sys
import os
import argparse

NUKTA_MAP = {
    '\u09af\u09bc': '\u09df',  # য+় -> য়
    '\u09a1\u09bc': '\u09dc',  # ড+় -> ড়
    '\u09a2\u09bc': '\u09dd',  # ঢ+় -> ঢ়
}


def fix_nukta(text: str) -> str:
    """বিশ্লিষ্ট নুক্তাযুক্ত বর্ণ প্রি-কম্পোজড করে।"""
    for decomp, precomp in NUKTA_MAP.items():
        text = text.replace(decomp, precomp)
    return text


def count_issues(text: str) -> int:
    """বিশ্লিষ্ট নুক্তার সংখ্যা গণনা করে।"""
    count = 0
    for decomp in NUKTA_MAP:
        count += text.count(decomp)
    return count


def main():
    parser = argparse.ArgumentParser(
        description='বাংলা ফাইলে বিশ্লিষ্ট নুক্তাযুক্ত বর্ণ সংশোধন করে।'
    )
    parser.add_argument('input', help='ইনপুট ফাইলের পথ')
    parser.add_argument('-o', '--output', help='আউটপুট ফাইলের পথ (ডিফল্ট: ইনপুট ফাইল প্রতিস্থাপন)')
    parser.add_argument('--check', action='store_true', help='শুধু পরীক্ষা করুন, পরিবর্তন করবেন না')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ত্রুটি: ফাইল পাওয়া যায়নি: {args.input}")
        sys.exit(1)

    with open(args.input, encoding='utf-8') as f:
        text = f.read()

    issues = count_issues(text)
    print(f"বিশ্লিষ্ট নুক্তা পাওয়া গেছে: {issues}টি")

    if args.check:
        sys.exit(0 if issues == 0 else 1)

    fixed = fix_nukta(text)
    output_path = args.output or args.input
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    print(f"সংশোধিত ফাইল সংরক্ষিত: {output_path}")


if __name__ == '__main__':
    main()
