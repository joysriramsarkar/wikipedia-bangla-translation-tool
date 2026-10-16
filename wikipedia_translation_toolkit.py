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

common_path = os.path.join(BASE_DIR, 'common')
if os.path.exists(common_path) and common_path not in sys.path:
    sys.path.insert(0, common_path)

try:
    from common.bengali_utils import to_bengali_text, to_bengali_digits, normalize_nukta_chars, has_invalid_nukta
except ImportError:
    try:
        import importlib
        bu = importlib.import_module('bengali_utils')
        to_bengali_text = getattr(bu, 'to_bengali_text', lambda x: x)
        to_bengali_digits = getattr(bu, 'to_bengali_digits', lambda x: x)
        normalize_nukta_chars = getattr(bu, 'normalize_nukta_chars', lambda x: x)
        has_invalid_nukta = getattr(bu, 'has_invalid_nukta', lambda x: False)
    except ImportError:
        to_bengali_text = lambda x: x
        to_bengali_digits = lambda x: x
        normalize_nukta_chars = lambda x: x
        has_invalid_nukta = lambda x: False


def _load_module(folder_name: str, module_name: str):
    """গতিশীলভাবে নির্দিষ্ট ভাষা ফোল্ডার থেকে পাইথন মডিউল লোড করে।"""
    path = os.path.join(BASE_DIR, folder_name, f"{module_name}.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"মডিউল ফাইলটি পাওয়া যায়নি: {path}")
    spec = importlib.util.spec_from_file_location(f"{folder_name}_{module_name}", path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    raise ImportError(f"মডিউল লোড করা সম্ভব হয়নি: {path}")


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

    def translate_text(self, text: str, source_lang: str) -> str:
        """যেকোনো সমর্থিত ভাষার উইকিটেক্সট প্রমিত বাংলায় অনুবাদ করে।"""
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

    def translate_file(self, input_path: str, output_path: str | None = None, source_lang: str = 'english') -> str:
        """ফাইল পড়ে অনুবাদ করে এবং ঐচ্ছিকভাবে ফলাফল সংরক্ষণ করে।"""
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        translated = self.translate_text(content, source_lang)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated)

        return translated

    def validate_rules(self, text: str) -> dict:
        """বাংলা উইকিপিডিয়ার নিয়মাবলি যাচাই করে রিপোর্ট দেয়।"""
        issues = []

        if '{{Short description' in text or '{{short description' in text:
            issues.append("নিয়ম ১ লঙ্ঘন: {{Short description}} বিদ্যমান")

        latin_digits = re.findall(r'\b\d+\b', re.sub(r'\[\[(?:File|চিত্র):.*?\]\]', '', text))
        if latin_digits:
            issues.append(f"নিয়ম ২ সতর্কতা: {len(latin_digits)}টি ল্যাটিন সংখ্যা পাওয়া গেছে")

        if re.search(r'(^|[\s\(\[\{])ৎ[ক-হ]', text):
            issues.append("নিয়ম ৪ লঙ্ঘন: শব্দের শুরুতে খণ্ড-ত (ৎ) পাওয়া গেছে")

        if re.search(r'\br\.\s*\d+', text):
            issues.append("নিয়ম ৫ সতর্কতা: শাসনকাল 'r. YYYY' পাওয়া গেছে")

        if has_invalid_nukta(text):
            issues.append("নিয়ম ১১ লঙ্ঘন: বিশ্লিষ্ট নুক্তাযুক্ত বর্ণ বিদ্যমান (ড়/ঢ়/য় প্রিকম্পোজড নয়)")

        if re.search(r'(?:km|কিমি)[²2]|(?:m|মি)[²2]', text):
            issues.append("নিয়ম ১২ লঙ্ঘন: এককের সুপারস্ক্রিপ্ট ² পাওয়া গেছে (বর্গকিমি ব্যবহার করুন)")

        if re.search(r'\{\{Use (?:British|Indian|American) English\}\}', text, flags=re.I):
            issues.append("নিয়ম ১৩ লঙ্ঘন: ইংরেজি উপভাষা/রক্ষণাবেক্ষণ টেমপ্লেট বিদ্যমান")

        return {
            'valid': len(issues) == 0,
            'issue_count': len(issues),
            'issues': issues,
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
