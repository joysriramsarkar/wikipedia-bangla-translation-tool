#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
বাংলা বর্ণানুক্রম সাজানো (Bengali Alphabetical Sort)
=======================================================
বাংলা উইকিপিডিয়া তালিকায় পঙক্তি/এন্ট্রি বাংলা বর্ণানুক্রমে
(অ-হ) সাজায়। উইকিটেক্সট সারণির সারি সরাসরি সাজানো যায়।

ব্যবহার:
    python scripts/sort_bengali.py input.txt
    python scripts/sort_bengali.py input.txt --column 1
"""
import sys
import re
import os
import argparse
import unicodedata

# বাংলা বর্ণানুক্রম (স্বরবর্ণ → ব্যঞ্জনবর্ণ)
BN_COLLATION_ORDER = (
    'অ আ ই ঈ উ ঊ ঋ এ ঐ ও ঔ '
    'ক খ গ ঘ ঙ '
    'চ ছ জ ঝ ঞ '
    'ট ঠ ড ঢ ণ '
    'ত থ দ ধ ন '
    'প ফ ব ভ ম '
    'য র ল শ ষ স হ '
    'ড় ঢ় য় ৎ ং ঃ ঁ'
).split()

BN_RANK = {c: i for i, c in enumerate(BN_COLLATION_ORDER)}


def bn_sort_key(text: str) -> list:
    """বাংলা বর্ণানুক্রমে তুলনার জন্য কী তৈরি করে।"""
    # উইকিমার্কআপ পরিষ্কার করা
    clean = re.sub(r'\[\[([^|\]]+\|)?([^\]]+)\]\]', r'\2', text)  # [[A|B]] -> B
    clean = re.sub(r"'{2,3}", '', clean)  # italic/bold মার্কআপ
    clean = clean.strip()
    key = []
    for ch in clean:
        cat = unicodedata.category(ch)
        if ch in BN_RANK:
            key.append((0, BN_RANK[ch]))
        elif cat.startswith('L'):
            key.append((1, ord(ch)))
        elif cat.startswith('N'):
            key.append((2, ord(ch)))
        else:
            key.append((3, ord(ch)))
    return key


def sort_wikitext_rows(rows: list, col_index: int = 0) -> list:
    """উইকিটেক্সট সারণির সারি বাংলা বর্ণানুক্রমে সাজায়।"""
    def row_key(row):
        parts = re.split(r'\|\|', row.lstrip('|').lstrip())
        if col_index < len(parts):
            return bn_sort_key(parts[col_index].strip())
        return []
    return sorted(rows, key=row_key)


def process_file(path: str, col_index: int = 0) -> str:
    """ফাইল পড়ে সারি সাজিয়ে আউটপুট টেক্সট ফেরত দেয়।"""
    with open(path, encoding='utf-8') as f:
        lines = f.readlines()

    # সারণির সারি আলাদা করা
    output = []
    data_rows = []
    in_table = False
    header_done = False

    for line in lines:
        stripped = line.rstrip()
        if stripped.startswith('{|'):
            in_table = True
            header_done = False
            output.append(line)
        elif stripped.startswith('|}'):
            # সারণির শেষে সাজানো সারি যোগ
            if data_rows:
                for row in sort_wikitext_rows(data_rows, col_index):
                    output.append(row)
                data_rows = []
            output.append(line)
            in_table = False
        elif in_table and not header_done and (stripped.startswith('!') or stripped.startswith('|-')):
            output.append(line)
            if stripped.startswith('|-'):
                header_done = True
        elif in_table and header_done and stripped.startswith('|') and not stripped.startswith('|-'):
            data_rows.append(line)
        elif in_table and stripped.startswith('|-') and data_rows:
            # মধ্যবর্তী বিভাজক
            for row in sort_wikitext_rows(data_rows, col_index):
                output.append(row)
            data_rows = []
            output.append(line)
        else:
            output.append(line)

    return ''.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='বাংলা উইকিপিডিয়া সারণির সারি বর্ণানুক্রমে সাজায়।'
    )
    parser.add_argument('input', help='ইনপুট ফাইলের পথ')
    parser.add_argument('-o', '--output', help='আউটপুট ফাইলের পথ')
    parser.add_argument('--column', type=int, default=0,
                        help='সাজানোর কলাম ইন্ডেক্স (০ থেকে শুরু, ডিফল্ট: ০)')
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"ত্রুটি: ফাইল পাওয়া যায়নি: {args.input}")
        sys.exit(1)

    result = process_file(args.input, args.column)
    output_path = args.output or args.input
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"বর্ণানুক্রমে সাজানো সম্পন্ন: {output_path}")


if __name__ == '__main__':
    main()
