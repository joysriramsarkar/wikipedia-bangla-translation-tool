#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া অনুবাদ টুলকিট — সম্পূর্ণ টেস্ট সুইট

pytest থাকলে pytest দিয়ে, না থাকলে শুধু পাইথন স্ট্যান্ডার্ড লাইব্রেরি দিয়ে
``tests/test_*.py`` ফাইলের সব ``test_*`` ফাংশন চালায়। ফলে নতুন মেশিনে
অতিরিক্ত কিছু ইনস্টল না করেও টেস্ট চালানো যায়।

ব্যবহার:
    python run_all_tests.py
    python run_all_tests.py --no-pytest     # জোর করে স্ট্যান্ডার্ড রানার
    python run_all_tests.py -v
"""
import argparse
import importlib.util
import inspect
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')

# pyproject.toml-এর [tool.pytest.ini_options] pythonpath-এর সঙ্গে মিলিয়ে রাখা —
# pytest ও স্ট্যান্ডার্ড রানার যেন একই মডিউল খুঁজে পায়।
_LANGUAGE_DIRS = (
    'চীনা-বাংলা অনুবাদ',
    'জাপানি-বাংলা অনুবাদ',
    'রুশ-বাংলা অনুবাদ',
    'জার্মান-বাংলা অনুবাদ',
    'ইংরেজি-বাংলা অনুবাদ',
)


def _add_import_paths():
    for path in (
        BASE_DIR,
        os.path.join(BASE_DIR, 'common'),
        os.path.join(BASE_DIR, 'scripts'),
        os.path.join(BASE_DIR, 'cx_postprocess'),
        *(os.path.join(BASE_DIR, d) for d in _LANGUAGE_DIRS),
        TESTS_DIR,
    ):
        if path not in sys.path:
            sys.path.insert(0, path)


def _requires_fixtures(func):
    """টেস্ট ফাংশনটির আর্গুমেন্ট লাগে কিনা (pytest fixture হলে স্ট্যান্ডার্ড
    রানার তা জোগান দিতে পারে না, তাই সেগুলো বাদ দিয়ে রিপোর্ট করা হয়)।"""
    try:
        params = inspect.signature(func).parameters.values()
    except (TypeError, ValueError):
        return False
    return any(
        p.default is inspect.Parameter.empty
        and p.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        )
        for p in params
    )


def _test_files():
    if not os.path.isdir(TESTS_DIR):
        return []
    return sorted(
        name for name in os.listdir(TESTS_DIR)
        if name.startswith('test_') and name.endswith('.py')
    )


def run_with_pytest(verbose=True):
    import pytest
    args = [TESTS_DIR]
    args.append('-v' if verbose else '-q')
    return pytest.main(args)


def run_with_stdlib(verbose=False):
    """pytest-মুক্ত রানার: প্রতিটি test_* ফাংশন আলাদাভাবে চালায়।"""
    _add_import_paths()
    total = 0
    passed = 0
    failures = []
    skipped = []

    for filename in _test_files():
        path = os.path.join(TESTS_DIR, filename)
        module_name = 'bnwiki_test_' + filename[:-3]
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            total += 1
            failures.append((filename, '<import>', 'মডিউল লোড করা যায়নি'))
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception:
            total += 1
            failures.append((filename, '<import>', traceback.format_exc()))
            continue

        for name in sorted(dir(module)):
            if not name.startswith('test_'):
                continue
            func = getattr(module, name)
            if not callable(func) or getattr(func, '__module__', '') != module_name:
                continue
            total += 1
            if _requires_fixtures(func):
                skipped.append((filename, name))
                print('s', end='', flush=True)
                continue
            try:
                func()
            except Exception:
                failures.append((filename, name, traceback.format_exc()))
                print('F', end='', flush=True)
            else:
                passed += 1
                print('.' if not verbose else f'\n  ✓ {filename}::{name}', end='', flush=True)

    print()
    for filename, name, error in failures:
        print(f"\n{'=' * 65}\n✗ {filename}::{name}\n{'-' * 65}\n{error}")

    if skipped:
        print(f"\n{'=' * 65}\nবাদ দেওয়া টেস্ট (pytest fixture প্রয়োজন, স্ট্যান্ডার্ড রানারে চলে না):")
        for filename, name in skipped:
            print(f"  - {filename}::{name}")

    print('=' * 65)
    if failures:
        print(f"  ✗ {passed}/{total} টেস্ট পাস; {len(failures)}টি ব্যর্থ; {len(skipped)}টি বাদ")
        print('=' * 65)
        return 1

    if skipped:
        print(f"  ✅ {passed}টি টেস্ট উত্তীর্ণ; {len(skipped)}টি বাদ (fixture প্রয়োজন — pytest দিয়ে চালান)")
    else:
        print(f"  ✅ সব {total}টি টেস্ট সফলভাবে উত্তীর্ণ হয়েছে!")
    print('=' * 65)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description='উইকিপিডিয়া অনুবাদ টুলকিট টেস্ট রানার')
    parser.add_argument('--no-pytest', action='store_true',
                        help='pytest থাকলেও স্ট্যান্ডার্ড রানার ব্যবহার করুন')
    parser.add_argument('-v', '--verbose', action='store_true', help='বিস্তারিত আউটপুট')
    args = parser.parse_args(argv)

    print('=' * 65)
    print('  উইকিপিডিয়া অনুবাদ টুলকিট — সম্পূর্ণ টেস্ট সুইট')
    print('  (Wikipedia Translation Toolkit — Full Test Suite)')
    print('=' * 65)

    if not args.no_pytest:
        try:
            import pytest  # noqa: F401
        except ImportError:
            print('\npytest পাওয়া যায়নি — স্ট্যান্ডার্ড রানারে চলছে।\n')
        else:
            print(f"\npytest দিয়ে {TESTS_DIR} চালানো হচ্ছে...\n")
            code = run_with_pytest(verbose=True)
            if code == 0:
                print('\n' + '=' * 65)
                print('  ✅ সমস্ত টেস্ট সফলভাবে উত্তীর্ণ হয়েছে! (All tests passed)')
                print('=' * 65)
            return int(code)

    print('স্ট্যান্ডার্ড রানার দিয়ে টেস্ট চলছে...\n')
    return run_with_stdlib(verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())
