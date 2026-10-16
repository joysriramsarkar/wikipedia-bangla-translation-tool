#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Run all Wikipedia Translation Toolkit tests
Supports pytest and standalone test runner
"""
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 65)
    print("  উইকিপিডিয়া অনুবাদ টুলকিট — সম্পূর্ণ টেস্ট সুইট")
    print("  (Wikipedia Translation Toolkit — Full Test Suite)")
    print("=" * 65)

    try:
        import pytest
        tests_dir = os.path.join(BASE_DIR, 'tests')
        print(f"\nrunning pytest on {tests_dir}...\n")
        exit_code = pytest.main([tests_dir, '-v'])
        if exit_code == 0:
            print("\n" + "=" * 65)
            print("  ✅ সমস্ত টেস্ট সফলভাবে উত্তীর্ণ হয়েছে! (All tests passed)")
            print("=" * 65)
        return exit_code
    except ImportError:
        print("\npytest লাইব্রেরি ইনস্টল নেই। পাইথন ইউনিট টেস্ট ব্যবহার করুন।")
        return 1

if __name__ == "__main__":
    sys.exit(main())
