#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
টেবিল যাচাইকারী (Table Verifier)
===================================
অনূদিত বাংলা উইকিপিডিয়া সারণিতে কলাম সংখ্যার অসামঞ্জস্য,
ইংরেজি সংখ্যা, খালি ঘর ইত্যাদি সমস্যা পরীক্ষা করে।

ব্যবহার:
    python scripts/verify_table.py input.txt
    python scripts/verify_table.py input.txt --expected-cols 5
"""
import sys
import re
import os
import argparse


def analyze_table(path: str, expected_cols: int = None) -> dict:
    """সারণি বিশ্লেষণ করে সমস্যার তালিকা ফেরত দেয়।"""
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    results = {
        'total_rows': 0,
        'bad_col_count': [],
        'english_digits': [],
        'missing_nbsp': [],
        'unclosed_tags': [],
        'broken_separator': [],
    }

    header_cols = None
    in_table = False

    for i, line in enumerate(lines, 1):
        s = line.rstrip()

        if s.startswith('{|'):
            in_table = True
            header_cols = None
            continue
        if s.startswith('|}'):
            in_table = False
            continue
        if not in_table:
            continue

        # হেডার সারি
        if s.startswith('!'):
            cols = [c.strip() for c in re.split(r'!!', s.lstrip('!'))]
            header_cols = len(cols)
            if expected_cols and header_cols != expected_cols:
                results['bad_col_count'].append((i, header_cols, f"হেডারে {header_cols} কলাম (প্রত্যাশিত {expected_cols})"))
            continue

        # বিভাজক লাইন
        if s.startswith('|-'):
            continue

        # ডেটা সারি
        if s.startswith('|') and not s.startswith('|+') and not s.startswith('|}'):
            results['total_rows'] += 1
            parts = [p.strip() for p in re.split(r'\|\|', s.lstrip('|'))]
            col_count = len(parts)

            if header_cols and col_count != header_cols:
                results['bad_col_count'].append((i, col_count, s[:60]))

            if expected_cols and col_count != expected_cols:
                if not header_cols:
                    results['bad_col_count'].append((i, col_count, s[:60]))

            # ইংরেজি সংখ্যা পরীক্ষা (সংরক্ষিত অঞ্চল বাদে)
            clean = re.sub(r'<ref[^>]*>.*?</ref>', '', s, flags=re.DOTALL)
            clean = re.sub(r'colspan="?\d+"?|rowspan="?\d+"?|width="?\d+[%px]*"?', '', clean)
            if re.search(r'[0-9]', clean):
                results['english_digits'].append((i, s[:60]))

            # খালি ঘর পরীক্ষা
            for j, part in enumerate(parts):
                if not part:
                    results['missing_nbsp'].append((i, j+1, "খালি ঘর পাওয়া গেছে — &nbsp; দরকার"))

            # অসম্পূর্ণ ট্যাগ
            if s.count('<ref') != s.count('</ref>') and '<ref' in s and '/>' not in s:
                results['unclosed_tags'].append((i, s[:60]))

    return results


def print_report(path: str, results: dict):
    """বিশ্লেষণ রিপোর্ট মুদ্রণ করে।"""
    print(f"\n{'='*60}")
    print(f"ফাইল: {path}")
    print(f"{'='*60}")
    print(f"মোট ডেটা সারি: {results['total_rows']}")

    categories = [
        ('bad_col_count', 'কলাম সংখ্যা অসামঞ্জস্য'),
        ('english_digits', 'ইংরেজি সংখ্যা'),
        ('missing_nbsp', 'খালি ঘর (nbsp প্রয়োজন)'),
        ('unclosed_tags', 'অসম্পূর্ণ ট্যাগ'),
    ]

    total_issues = 0
    for key, label in categories:
        issues = results[key]
        total_issues += len(issues)
        if issues:
            print(f"\n⚠ {label}: {len(issues)}টি সমস্যা")
            for item in issues[:5]:
                print(f"  লাইন {item[0]}: {item[-1]}")
            if len(issues) > 5:
                print(f"  ... আরও {len(issues)-5}টি")
        else:
            print(f"✓ {label}: কোনো সমস্যা নেই")

    print(f"\nসারসংক্ষেপ: {total_issues}টি সমস্যা পাওয়া গেছে")
    return total_issues


def main():
    parser = argparse.ArgumentParser(
        description='বাংলা উইকিপিডিয়া সারণি যাচাই করে।'
    )
    parser.add_argument('files', nargs='+', help='যাচাই করার ফাইল(সমূহ)')
    parser.add_argument('--expected-cols', type=int, help='প্রত্যাশিত কলাম সংখ্যা')
    args = parser.parse_args()

    total = 0
    for path in args.files:
        if not os.path.exists(path):
            print(f"সতর্কতা: ফাইল নেই: {path}")
            continue
        results = analyze_table(path, args.expected_cols)
        total += print_report(path, results)

    sys.exit(0 if total == 0 else 1)


if __name__ == '__main__':
    main()
