#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI interface for Wikipedia Translation Toolkit
"""
import argparse
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from wikipedia_translation_toolkit import WikipediaTranslator, LANG_MODULES


def main():
    parser = argparse.ArgumentParser(
        description='Wikipedia Translation Toolkit — বাংলা উইকিপিডিয়া অনুবাদ টুলকিট',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Available tools:
  chinese   - Chinese to Bengali translation (চীনা-বাংলা)
  japanese  - Japanese to Bengali translation (জাপানি-বাংলা)
  russian   - Russian to Bengali translation (রুশ-বাংলা)
  german    - German to Bengali translation (জার্মান-বাংলা)
  english   - English to Bengali translation (ইংরেজি-বাংলা)
  info      - System info and module status

Examples:
  python cli.py english -i article.txt -o article_bn.txt
  python cli.py german -i films.txt -o films_bn.txt --table-only
  python cli.py english -i draft.txt --check-rules
        '''
    )
    parser.add_argument('command', choices=['chinese', 'japanese', 'russian', 'german', 'english', 'info'],
                        help='অনুবাদ কমান্ড বা তথ্য')
    parser.add_argument('--input', '-i', help='ইনপুট ফাইলের পথ')
    parser.add_argument('--output', '-o', help='আউটপুট ফাইলের পথ')
    parser.add_argument('--table-only', '-t', action='store_true', help='কেবল সারণি অনুবাদ করুন')
    parser.add_argument('--check-rules', '-c', action='store_true', help='বাংলা উইকিপিডিয়ার নীতিমালা যাচাই করুন')

    args = parser.parse_args()

    if args.command == 'info':
        print("উইকিপিডিয়া অনুবাদ টুলকিট (Wikipedia Translation Toolkit) v1.0.0")
        print("অবস্থান:", BASE_DIR)
        print("\nউপলব্ধ ভাষা মডিউলসমূহ:")
        for mod in LANG_MODULES:
            path = os.path.join(BASE_DIR, mod)
            status = "সক্রিয়" if os.path.exists(path) else "অনুপস্থিত"
            print(f"  - {mod}: {status}")
        return 0

    if not args.input:
        print("ত্রুটি: অনুবাদ বা যাচাইয়ের জন্য --input (-i) আবশ্যক।")
        parser.print_help()
        return 1

    if not os.path.exists(args.input):
        print(f"ত্রুটি: ফাইলটি খুঁজে পাওয়া যায়নি: {args.input}")
        return 1

    translator = WikipediaTranslator()

    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()

    # নিয়মাবলি পরীক্ষা
    if args.check_rules:
        report = translator.validate_rules(content)
        print(f"\n🔍 নীতিমালা যাচাই রিপোর্ট ({args.input}):")
        if report['valid']:
            print("  ✅ কোনো নিয়ম লঙ্ঘন পাওয়া যায়নি! ফাইলটি মানসম্মত।")
        else:
            print(f"  ⚠️ {report['issue_count']}টি সমস্যা/সতর্কতা পাওয়া গেছে:")
            for issue in report['issues']:
                print(f"    - {issue}")
        if not args.output and not args.table_only:
            return 0

    print(f"[{args.command}] অনুবাদ শুরু হচ্ছে: {args.input}...")

    if args.table_only:
        translated = translator.translate_table(content, args.command)
    else:
        translated = translator.translate_text(content, args.command)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(translated)
        print(f"✅ অনুবাদ সফলভাবে সংরক্ষিত হয়েছে: {args.output}")
    else:
        print("\n" + "=" * 50)
        print(translated[:1000] + ("\n... [আরো আছে]" if len(translated) > 1000 else ""))
        print("=" * 50)

    return 0


if __name__ == '__main__':
    sys.exit(main())
