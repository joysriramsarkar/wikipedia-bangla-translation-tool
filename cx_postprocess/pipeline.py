# -*- coding: utf-8 -*-
"""
CX পোস্ট-প্রসেসর পাইপলাইন: এক জায়গায় সব ফিক্স।

ক্রমটা ইচ্ছাকৃত:
1. template_fix (শিরোনাম/টেমপ্লেট নাম + templatestyles সাফাই)
2. translate_infobox (প্যারাম/লেবেল + ভেতরে সংখ্যা)
3. fix_tables (টেবিল গঠন; অ্যাট্রিবিউট সুরক্ষিত)
4. fix_currency (মুদ্রা নাম — চিহ্ন রাখা হয়)
5. fix_units_dates (billion/million, একক, মাস — শব্দ স্তর)
6. to_bengali_digits_safe (শেষে সব দৃশ্যমান অঙ্ক → ০-৯)

`fix_text()` সার্ভার + টেস্ট — দুটোই এটা ব্যবহার করে।
"""
from .bn_digits_safe import to_bengali_digits_safe
from .infobox_map import translate_infobox
from .table_fix import fix_tables
from .currency_fix import fix_currency
from .units_dates import fix_units_dates
from .template_fix import fix_templates
import re

from common.bengali_utils import fix_r_reigned


from .ref_healer import audit_citations, heal_named_references


NUKTA_MAP = {
    '\u09af\u09bc': '\u09df',  # য+় -> য়
    '\u09a1\u09bc': '\u09dc',  # ড+় -> ড়
    '\u09a2\u09bc': '\u09dd',  # ঢ+় -> ঢ়
}


def normalize_nukta(text: str) -> str:
    for decomp, precomp in NUKTA_MAP.items():
        text = text.replace(decomp, precomp)
    return text


def fix_text(text: str, source_text: str = "") -> dict:
    s = fix_templates(text)
    s = re.sub(r'\[\[\s*Category\s*:', '[[বিষয়শ্রেণী:', s, flags=re.IGNORECASE)
    s, unknown = translate_infobox(s)
    s = fix_tables(s)
    s = fix_currency(s)
    s = fix_units_dates(s)
    # নিয়ম ৫: `r. 1995–2005` → `শাসনকাল: ১৯৯৫–২০০৫` (আগে পাইপলাইনে বাদ পড়েছিল)
    s = fix_r_reigned(s)
    s = to_bengali_digits_safe(s)
    s = normalize_nukta(s)

    healed_refs = []
    broken_refs = []
    if source_text:
        s, healed_refs, broken_refs = heal_named_references(s, source_text)

    citations = audit_citations(s, source_text)

    return {
        "fixed": s,
        "unknown_params": unknown,
        "healed_refs": healed_refs,
        "broken_refs": broken_refs,
        "citations": citations,
    }
