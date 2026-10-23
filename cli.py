#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI interface for Wikipedia Translation Toolkit
"""
import argparse
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from wikipedia_translation_toolkit import WikipediaTranslator, LANG_MODULES
from common.bengali_utils import to_bengali_digits

#: CLI-তে ভাষার নাম → উইকিপিডিয়া ভাষা কোড (মেশিন অনুবাদ ইঞ্জিনের জন্য)
LANG_CODES = {
    'chinese': 'zh',
    'japanese': 'ja',
    'russian': 'ru',
    'german': 'de',
    'english': 'en',
}


def translate_with_mt(
    content: str,
    lang_code: str,
    model: str | None = None,
    gemini_key: str | None = None,
    use_ai: bool = False,
    provider: str | None = None,
) -> str:
    """সাধারণ (যে-কোনো নিবন্ধের) মেশিন অনুবাদ ইঞ্জিন।

    ভাষা-মডিউলগুলো এক-একটি নির্দিষ্ট নিবন্ধের জন্য লেখা (যেমন কেবল
    “রাশিয়ার জেলা”), তাই অপরিচিত নিবন্ধে সেগুলো মূল ভাষাই রেখে দেয়।
    এই ইঞ্জিন WIKITEXT-এর ট্যাগ, <ref>, {{টেমপ্লেট}} ও [[লিংক]] রক্ষা
    করে প্রাকৃতিক ভাষার বাক্য অনুবাদ করে (ঐচ্ছিকভাবে Gemini দিয়ে)।
    """
    from cx_postprocess.mt_translate import translate_wikitext_full
    from common.env_loader import (
        DEFAULT_GEMINI_MODEL, get_gemini_key, get_gemini_model,
        DEFAULT_OLLAMA_MODEL, get_ollama_key, get_ollama_base_url, get_ollama_model,
        DEFAULT_OPENROUTER_MODEL, get_openrouter_key, get_openrouter_base_url, get_openrouter_model,
        get_ai_provider,
    )

    prov = (provider or get_ai_provider("gemini")).lower() if use_ai else "google"
    if prov == "ollama":
        key = gemini_key or (get_ollama_key() if use_ai else None)
        active_model = model or get_ollama_model(DEFAULT_OLLAMA_MODEL)
    elif prov == "openrouter":
        key = gemini_key or (get_openrouter_key() if use_ai else None)
        active_model = model or get_openrouter_model(DEFAULT_OPENROUTER_MODEL)
    else:
        key = gemini_key or (get_gemini_key() if use_ai else None)
        active_model = model or get_gemini_model(DEFAULT_GEMINI_MODEL)

    return translate_wikitext_full(
        content, sl=lang_code, tl='bn',
        gemini_key=key if use_ai else None,
        gemini_model=active_model,
    )


def print_rule_report(report, label):
    """নিয়মভিত্তিক যাচাই রিপোর্ট ছাপে।"""
    print(f"\n🔍 নীতিমালা যাচাই রিপোর্ট ({label}):")
    for rule_id in report.get('checked_rules', list(report['rules'])):
        info = report['rules'][rule_id]
        mark = '✅' if info['ok'] else '⚠️'
        print(f"  {mark} নিয়ম {rule_id} — {info['title']}")
        for message in info['issues']:
            print(f"       • {message}")
    unchecked = report.get('unchecked_rules', [])
    if unchecked:
        print(f"  ℹ️  অর্থগত বিচারের বিষয়: নিয়ম {', '.join(unchecked)}")
    if report['valid']:
        print("  ✅ স্বয়ংক্রিয়ভাবে যাচাইযোগ্য কোনো নিয়ম লঙ্ঘন পাওয়া যায়নি।")
    else:
        count = to_bengali_digits(str(report['issue_count']))
        print(f"  ⚠️ মোট {count}টি সমস্যা পাওয়া গেছে।")


def main(argv=None):
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
  check     - Check Bengali Wikipedia rules on a draft file (নীতিমালা যাচাই)
  info      - System info and module status

Examples:
  python cli.py english -i article.txt -o article_bn.txt
  python cli.py english -i article.txt -o article_bn.txt --engine mt
  python cli.py german -i films.txt -o films_bn.txt --table-only
  python cli.py check -i draft.txt
  python cli.py english -i draft.txt --check-rules
  python cli.py english -i source.txt -o draft.txt --check-rules
        '''
    )
    parser.add_argument('command', choices=['chinese', 'japanese', 'russian', 'german', 'english', 'info', 'check'],
                        help='অনুবাদ কমান্ড, তথ্য বা যাচাই')
    parser.add_argument('--input', '-i', help='ইনপুট ফাইলের পথ')
    parser.add_argument('--output', '-o', help='আউটপুট ফাইলের পথ')
    parser.add_argument('--table-only', '-t', action='store_true', help='কেবল সারণি অনুবাদ করুন')
    parser.add_argument('--check-rules', '-c', action='store_true', help='বাংলা উইকিপিডিয়ার নীতিমালা যাচাই করুন')
    parser.add_argument('--engine', '-e', choices=['module', 'mt'], default='module',
                        help='module = ভাষা-মডিউল (নির্দিষ্ট নিবন্ধের জন্য লেখা); '
                             'mt = যে-কোনো নিবন্ধের জন্য সাধারণ অনুবাদ ইঞ্জিন')
    parser.add_argument('--ai', action='store_true', help='Gemini AI ব্যবহার করে অনুচ্ছেদ অনুবাদ')
    parser.add_argument('--gemini-key', help='Gemini API Key (না দিলে .env থেকে স্বয়ংক্রিয়ভাবে নেওয়া হবে)')
    parser.add_argument('--provider', choices=['gemini', 'ollama', 'openrouter'], default=None, help='AI প্রোভাইডার (Gemini/Ollama/OpenRouter)')
    parser.add_argument('--ollama-url', help='Ollama বেস URL')
    parser.add_argument('--openrouter-key', help='OpenRouter API Key')
    parser.add_argument('--model', help='AI মডেলের নাম (ডিফল্ট: provider অনুযায়ী)')

    args = parser.parse_args(argv)

    if args.command == 'info':
        print("উইকিপিডিয়া অনুবাদ টুলকিট (Wikipedia Translation Toolkit) v1.2.0")
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

    # আলাদা 'check' কমান্ড থাকলে সরাসরি ইনপুট খসড়াটি যাচাই করে প্রস্থান
    if args.command == 'check':
        print_rule_report(translator.validate_rules(content), args.input)
        return 0

    # শুধু যাচাই: কোনো আউটপুট বা এমটি ইঞ্জিন না থাকলে ইনপুট ফাইলটি পরীক্ষা করে থামে (অতীত সামঞ্জস্যতা)
    if args.check_rules and not args.output and not args.table_only and args.engine == 'module' and not args.ai:
        print_rule_report(translator.validate_rules(content), args.input)
        return 0

    print(f"[{args.command}] অনুবাদ শুরু হচ্ছে: {args.input}...")

    if args.engine == 'mt':
        translated = translate_with_mt(
            content,
            LANG_CODES[args.command],
            model=args.model,
            gemini_key=args.gemini_key or args.openrouter_key,
            use_ai=args.ai,
            provider=args.provider,
        )
    elif args.table_only:
        translated = translator.translate_table(content, args.command)
    else:
        translated = translator.translate_text(content, args.command)

    # অনুবাদের সঙ্গে যাচাই চাইলে ফলাফলকেই যাচাই করা হয়, উৎস নয়
    if args.check_rules:
        print_rule_report(translator.validate_rules(translated), 'অনূদিত ফলাফল')

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
