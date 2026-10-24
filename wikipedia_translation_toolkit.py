#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Main entry point for Wikipedia Translation Toolkit
Unified interface for all language modules (Chinese, Japanese, Russian, German, English)
"""
import sys
import os
import re
import importlib.util

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LANG_MODULES = [
    'চীনা-বাংলা অনুবাদ',
    'জাপানি-বাংলা অনুবাদ',
    'রুশ-বাংলা অনুবাদ',
    'জার্মান-বাংলা অনুবাদ',
    'ইংরেজি-বাংলা অনুবাদ',
]

for mod in LANG_MODULES:
    mod_path = os.path.join(BASE_DIR, mod)
    if os.path.exists(mod_path) and mod_path not in sys.path:
        sys.path.insert(0, mod_path)

#: পাঁচ ভাষার ফোল্ডারে একই নামের এই মডিউলগুলো আছে — লোডের সময় আলাদা করতে হয়।
_SHARED_MODULE_NAMES = (
    'table_translator', 'number_converter', 'links_dictionary', 'pinyin_table',
    'transliteration', 'transliterate_engine', 'federal_subjects',
    'prime_minister_notes', 'film_title_translator', 'german_transliteration',
    'japanese_transliteration', 'cyrillic_transliteration', 'translate_page',
)
_LANG_DIRS = [os.path.join(BASE_DIR, name) for name in LANG_MODULES]
_LOADED_MODULES = {}

common_path = os.path.join(BASE_DIR, 'common')
if os.path.exists(common_path) and common_path not in sys.path:
    sys.path.insert(0, common_path)

try:
    from common.bengali_utils import (
        to_bengali_text, to_bengali_digits, normalize_nukta_chars, has_invalid_nukta,
        strip_technical_spans,
    )
except ImportError:
    try:
        import importlib
        bu = importlib.import_module('bengali_utils')
        to_bengali_text = getattr(bu, 'to_bengali_text', lambda x: x)
        to_bengali_digits = getattr(bu, 'to_bengali_digits', lambda x: x)
        normalize_nukta_chars = getattr(bu, 'normalize_nukta_chars', lambda x: x)
        has_invalid_nukta = getattr(bu, 'has_invalid_nukta', lambda x: False)
        strip_technical_spans = getattr(bu, 'strip_technical_spans', lambda x: x)
    except ImportError:
        to_bengali_text = lambda x: x
        to_bengali_digits = lambda x: x
        normalize_nukta_chars = lambda x: x
        has_invalid_nukta = lambda x: False
        strip_technical_spans = lambda x: x

try:
    from common.wikitext_utils import analyze_wikitable
except ImportError:
    def analyze_wikitable(text):
        return {'tables': 0, 'rows': 0, 'header_cols': None, 'issues': []}


RULE_TITLES = {
    '১': '{{Short description}} পরিহার',
    '২': 'শতভাগ বাংলা সংখ্যা',
    '৩': 'বাংলা বর্ণানুক্রমিক তালিকা',
    '৪': 'শব্দের শুরুতে ৎ নিষিদ্ধ',
    '৫': 'শাসনকালের r. অনুবাদ',
    '৬': 'সারণির কলাম সমতা ও খালি ঘর',
    '৭': 'রাষ্ট্রপ্রধান ও প্রধানমন্ত্রীর নাম বিন্যাস',
    '৮': 'ডিফল্ট সর্ট ও বিষয়শ্রেণী',
    '৯': 'চলচ্চিত্র তালিকা ও লিপ্যন্তর',
    '১০': 'চলচ্চিত্র শিরোনাম উপস্থাপন',
    '১১': 'প্রি-কম্পোজড বর্ণ',
    '১২': 'এককের সুপারস্ক্রিপ্ট পরিহার',
    '১৩': 'রক্ষণাবেক্ষণ ও উপভাষা টেমপ্লেট বর্জন',
}

#: সূত্র টেমপ্লেটে ASCII রাখা হয় এমন প্যারামিটার — নিয়ম ২-এর গণনায় বাদ।
_CITATION_MACHINE_PARAM_RE = re.compile(
    r'\|\s*(?:access-?date|accessdate|archive-?date|archivedate|date|'
    r'publication-?date|lay-?date|year|orig-?year|pmc|pmid|doi|isbn|oclc)\s*=[^|{}\n]+',
    re.IGNORECASE,
)


def _load_module(folder_name: str, module_name: str):
    """গতিশীলভাবে নির্দিষ্ট ভাষা ফোল্ডার থেকে পাইথন মডিউল লোড করে।

    সমস্যা: পাঁচটি ভাষা-ফোল্ডারে একই নামের মডিউল আছে (`table_translator.py`,
    `number_converter.py`, `links_dictionary.py` …)। সব ফোল্ডার একসঙ্গে
    `sys.path`-এ থাকায় প্রথমটি পরেরগুলোকে ছায়া করত — ফলে
    `python cli.py chinese` ImportError দিয়ে ক্র্যাශ করত
    (`translate_main_table` পাওয়া যায়নি)। এখন শুধু লক্ষ্য ফোল্ডারই
    সাময়িকভাবে `sys.path`-এ রাখা হয়, আর একই নামের মডিউলগুলো পরস্পরকে
    ছায়া না করার জন্য ধারে সরিয়ে রাখা হয়।
    """
    cache_key = (folder_name, module_name)
    cached = _LOADED_MODULES.get(cache_key)
    if cached is not None:
        return cached

    path = os.path.join(BASE_DIR, folder_name, f"{module_name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"মডিউল ফাইলটি পাওয়া যায়নি: {path}")
    folder = os.path.join(BASE_DIR, folder_name)
    spec = importlib.util.spec_from_file_location(f"bnwiki_{folder_name}_{module_name}", path)
    if not (spec and spec.loader):
        raise ImportError(f"মডিউল লোড করা সম্ভব হয়নি: {path}")

    mod = importlib.util.module_from_spec(spec)
    saved_path = list(sys.path)
    shadowed = {}
    try:
        for directory in _LANG_DIRS:
            while directory in sys.path:
                sys.path.remove(directory)
        sys.path.insert(0, folder)
        for name in _SHARED_MODULE_NAMES:
            if name in sys.modules:
                shadowed[name] = sys.modules.pop(name)
        spec.loader.exec_module(mod)
    finally:
        for name in _SHARED_MODULE_NAMES:
            sys.modules.pop(name, None)
        sys.modules.update(shadowed)
        sys.path[:] = saved_path

    _LOADED_MODULES[cache_key] = mod
    return mod


class WikipediaTranslator:
    """Unified Wikipedia translator interface supporting Chinese, Japanese, Russian, German, English."""

    def __init__(self):
        self.available_languages = {
            'chinese': 'চীনা-বাংলা অনুবাদ',
            'japanese': 'জাপানি-বাংলা অনুবাদ',
            'russian': 'রুশ-বাংলা অনুবাদ',
            'german': 'জার্মান-বাংলা অনুবাদ',
            'english': 'ইংরেজি-বাংলা অনুবাদ',
            'zh': 'চীনা-বাংলা অনুবাদ',
            'ja': 'জাপানি-বাংলা অনুবাদ',
            'ru': 'রুশ-বাংলা অনুবাদ',
            'de': 'জার্মান-বাংলা অনুবাদ',
            'en': 'ইংরেজি-বাংলা অনুবাদ',
        }

    def _resolve_lang(self, lang: str) -> str:
        key = lang.lower().strip()
        if key not in self.available_languages:
            raise ValueError(f"অজানা ভাষা: {lang}। সমর্থিত ভাষাসমূহ: {list(self.available_languages.keys())}")
        return self.available_languages[key]

    def translate_text(self, text: str, source_lang: str, engine: str = 'module') -> str:
        """যেকোনো সমর্থিত ভাষার উইকিটেক্সট প্রমিত বাংলায় অনুবাদ করে।"""
        if engine == 'mt':
            lang_code = {
                'chinese': 'zh', 'japanese': 'ja', 'russian': 'ru', 'tamil': 'ta',
                'german': 'de', 'english': 'en',
                'zh': 'zh', 'ja': 'ja', 'ru': 'ru', 'de': 'de', 'en': 'en'
            }.get(source_lang.lower().strip(), source_lang)
            from cx_postprocess.mt_translate import translate_wikitext_full
            return translate_wikitext_full(text, sl=lang_code, tl='bn')

        mod_name = self._resolve_lang(source_lang)

        if mod_name == 'চীনা-বাংলা অনুবাদ':
            zh_tp = _load_module(mod_name, 'translate_page')
            return zh_tp.translate_wikipedia_text(text)

        elif mod_name == 'জাপানি-বাংলা অনুবাদ':
            ja_tt = _load_module(mod_name, 'table_translator')
            def repl_ja_table(m):
                return ja_tt.translate_wikitable(m.group(0))
            translated = re.sub(r'\{\| class="wikitable.*?\|\}', repl_ja_table, text, flags=re.DOTALL)
            return to_bengali_text(translated)

        elif mod_name == 'রুশ-বাংলা অনুবাদ':
            ru_tp = _load_module(mod_name, 'translate_page')
            return ru_tp.translate_page(text)

        elif mod_name == 'জার্মান-বাংলা অনুবাদ':
            de_tt = _load_module(mod_name, 'table_translator')
            def repl_de_table(m):
                return de_tt.translate_film_table(m.group(0))
            translated = re.sub(r'\{\| class="wikitable.*?\|\}', repl_de_table, text, flags=re.DOTALL)
            return to_bengali_text(translated)

        elif mod_name == 'ইংরেজি-বাংলা অনুবাদ':
            en_tp = _load_module(mod_name, 'translate_page')
            return en_tp.translate_text(text)

        return to_bengali_text(text)

    def translate_table(self, table_text: str, source_lang: str) -> str:
        """যেকোনো সমর্থিত ভাষার উইকিটেবিল বাংলায় অনুবাদ করে।"""
        mod_name = self._resolve_lang(source_lang)

        if mod_name == 'চীনা-বাংলা অনুবাদ':
            zh_tt = _load_module(mod_name, 'table_translator')
            return zh_tt.translate_main_table(table_text)
        elif mod_name == 'জাপানি-বাংলা অনুবাদ':
            ja_tt = _load_module(mod_name, 'table_translator')
            return ja_tt.translate_wikitable(table_text)
        elif mod_name == 'রুশ-বাংলা অনুবাদ':
            ru_tt = _load_module(mod_name, 'table_translator')
            return ru_tt.translate_wikitable(table_text)
        elif mod_name == 'জার্মান-বাংলা অনুবাদ':
            de_tt = _load_module(mod_name, 'table_translator')
            return de_tt.translate_film_table(table_text)
        elif mod_name == 'ইংরেজি-বাংলা অনুবাদ':
            en_tt = _load_module(mod_name, 'table_translator')
            return en_tt.translate_wikitable(table_text)

        return table_text

    def translate_file(self, input_path: str, output_path: str | None = None, source_lang: str = 'english', engine: str = 'module') -> str:
        """ফাইল পড়ে অনুবাদ করে এবং ঐচ্ছিকভাবে ফলাফল সংরক্ষণ করে।"""
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        translated = self.translate_text(content, source_lang, engine=engine)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated)

        return translated

    def translate_german(self, input_path: str, output_path: str | None = None, engine: str = 'module') -> str:
        """জার্মান নিবন্ধ ফাইল বাংলায় অনুবাদ করে (INSTRUCTIONS.md অনুযায়ী)।"""
        return self.translate_file(input_path, output_path, source_lang='german', engine=engine)

    def translate_chinese(self, input_path: str, output_path: str | None = None, engine: str = 'module') -> str:
        """চীনা নিবন্ধ ফাইল বাংলায় অনুবাদ করে।"""
        return self.translate_file(input_path, output_path, source_lang='chinese', engine=engine)

    def translate_japanese(self, input_path: str, output_path: str | None = None, engine: str = 'module') -> str:
        """জাপানি নিবন্ধ ফাইল বাংলায় অনুবাদ করে।"""
        return self.translate_file(input_path, output_path, source_lang='japanese', engine=engine)

    def translate_russian(self, input_path: str, output_path: str | None = None, engine: str = 'module') -> str:
        """রুশ নিবন্ধ ফাইল বাংলায় অনুবাদ করে।"""
        return self.translate_file(input_path, output_path, source_lang='russian', engine=engine)

    def translate_english(self, input_path: str, output_path: str | None = None, engine: str = 'module') -> str:
        """ইংরেজি নিবন্ধ ফাইল বাংলায় অনুবাদ করে।"""
        return self.translate_file(input_path, output_path, source_lang='english', engine=engine)

    def validate_rules(self, text: str) -> dict:
        """বাংলা উইকিপিডিয়ার নীতিমালা যাচাই করে বিস্তারিত রিপোর্ট দেয়।

        যন্ত্রে যাচাইযোগ্য ৯টি নিয়ম (১, ২, ৪, ৫, ৬, ৮, ১১, ১২, ১৩) পরীক্ষা
        করা হয়। বাকি নিয়মগুলো অর্থগত বিচারের বিষয়, তাই `unchecked_rules`-এ
        আলাদা রাখা হয়।

        রিপোর্টের কী: ``valid``, ``issue_count``, ``issues`` (সমান-সরল তালিকা),
        ``rules`` (নিয়মভিত্তিক ফল), ``table_report`` (সারণি বিশ্লেষণ)।
        """
        text = text or ''
        issues = []
        rules = {}

        def check(rule_id, message=None):
            entry = rules.setdefault(rule_id, {
                'title': RULE_TITLES.get(rule_id, ''),
                'ok': True,
                'issues': [],
            })
            if message:
                entry['ok'] = False
                entry['issues'].append(message)
                issues.append(f"নিয়ম {rule_id}: {message}")

        # দৃশ্যমান লেখা (URL, ফাইলনাম, টেমপ্লেট কী বাদ) — নিয়ম ২ ও ১২ এর জন্য
        visible = strip_technical_spans(text)
        # সূত্র টেমপ্লেটের তারিখ/ISBN ইচ্ছাকৃতভাবে ASCII রাখা হয় (CS1 ত্রুটি
        # এড়াতে) — তাই সেগুলো নিয়ম ২-এর “ইংরেজি অঙ্ক” গণনায় ধরবে না।
        visible = _CITATION_MACHINE_PARAM_RE.sub(' ', visible)

        # ১. Short description
        check('১', '{{Short description}} বিদ্যমান'
              if re.search(r'\{\{\s*short\s+description', text, flags=re.I) else None)

        # ২. শতভাগ বাংলা সংখ্যা (শুধু ASCII 0-9; বাংলা অঙ্ক ০-৯ বাদ যাবে না)
        latin_digits = re.findall(r'[0-9]', visible)
        check('২', f'{to_bengali_digits(str(len(latin_digits)))}টি ইংরেজি অঙ্ক অবশিষ্ট আছে'
              if latin_digits else None)

        # ৪. শব্দের শুরুতে ৎ নিষিদ্ধ
        check('৪', 'শব্দের শুরুতে খণ্ড-ত (ৎ) পাওয়া গেছে'
              if re.search(r'(^|[\s\(\[\{])ৎ[ক-হ]', text) else None)

        # ৫. শাসনকালের 'r.'
        check('৫', "শাসনকালের 'r. YYYY' অবশিষ্ট আছে"
              if re.search(r'\br\.\s*\d', visible) else None)

        # ৬. সারণির কলাম সমতা ও খালি ঘর
        check('৬')
        table_report = analyze_wikitable(text)
        table_issues = table_report.get('issues') if isinstance(table_report, dict) else []
        if isinstance(table_issues, list):
            for item in table_issues[:10]:
                if isinstance(item, dict):
                    line = to_bengali_digits(str(item.get('line', '')))
                    check('৬', f"{item.get('message', '')} (লাইন {line})")
            if len(table_issues) > 10:
                extra = to_bengali_digits(str(len(table_issues) - 10))
                check('৬', f'আরও {extra}টি সারণি সমস্যা আছে')

        # ৮. বিষয়শ্রেণী
        check('৮', 'ইংরেজি [[Category:...]] উপসর্গ বিদ্যমান'
              if re.search(r'\[\[\s*Category\s*:', text, flags=re.I) else None)

        # ১১. প্রি-কম্পোজড বর্ণ
        check('১১', 'বিশ্লিষ্ট নুক্তাযুক্ত বর্ণ বিদ্যমান (য়/ড়/ঢ় প্রিকম্পোজড নয়)'
              if has_invalid_nukta(text) else None)

        # ১২. এককের সুপারস্ক্রিপ্ট
        check('১২', 'এককের সুপারস্ক্রিপ্ট ²/³ পাওয়া গেছে (বর্গকিমি/ঘনকিমি ব্যবহার করুন)'
              if re.search(r'(?:km|কিমি|m|মি)\s*[²³23](?!\d)', visible) else None)

        # ১৩. ইংরেজি রক্ষণাবেক্ষণ ও উপভাষা টেমপ্লেট
        check('১৩', 'ইংরেজি উপভাষা/রক্ষণাবেক্ষণ টেমপ্লেট বিদ্যমান'
              if re.search(
                  r'\{\{\s*(?:Use\s+(?:British|Indian|American|Australian|Canadian|'
                  r'New Zealand|Irish|Scottish)\s+English|Use\s+(?:dmy|mdy)(?:\s+dates)?|'
                  r'force cite load)\s*\}\}',
                  text, flags=re.I) else None)

        checked = set(rules)
        return {
            'valid': len(issues) == 0,
            'issue_count': len(issues),
            'issues': issues,
            'rules': rules,
            'checked_rules': [r for r in RULE_TITLES if r in checked],
            'unchecked_rules': [r for r in RULE_TITLES if r not in checked],
            'table_report': table_report,
        }


def main():
    print("উইকিপিডিয়া অনুবাদ টুলকিট (Wikipedia Translation Toolkit)")
    print("=" * 60)
    print("\nAvailable language modules:")
    for i, mod in enumerate(LANG_MODULES, 1):
        print(f"  {i}. {mod}")
    print("\nCommon utilities: common/")
    print("\nUse cli.py or import modules directly.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
