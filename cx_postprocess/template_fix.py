# -*- coding: utf-8 -*-
"""
টেমপ্লেট / শিরোনাম ফিক্স (প্রোটোটাইপ ধাপ-২ + ধাপ-৩)।

- `{{Reflist}}` → `{{সূত্র তালিকা}}`
- `== References ==` → `== তথ্যসূত্র ==`
- `== See also ==` → `== আরও দেখুন ==`
- `== External links ==` → `== বহিঃসংযোগ ==`
- `{{Short description|...}}` মুছে ফেলা
- `{{DEFAULTSORT:English 123}}` → মানের অঙ্ক বাংলা (নাম একই থাকে)
- CX-এর ভাঙা `templatestyles` অবশেষ সাফাই: বৈধ
  `<templatestyles src="…"/>` রাখা হয়, খালি `</> templatestyles`
  ধরনের ভাঙা লাইন মুছে ফেলা হয়।
"""
import re
from .bn_digits_safe import to_bengali_digits_safe

HEADING_MAP = {
    "References": "তথ্যসূত্র",
    "See also": "আরও দেখুন",
    "External links": "বহিঃসংযোগ",
    "Further reading": "আরও পড়ুন",
}

SHORT_DESC = re.compile(
    r"\{\{\s*(?:(?:Template|টেমপ্লেট)\s*:\s*)?[Ss]hort description\s*(?:\|[^}]*)?\}\}\s*\n?",
    re.IGNORECASE,
)

# ইংরেজি উপভাষা ও রক্ষণাবেক্ষণ টেমপ্লেট বর্জন (যেমন Use British/Indian English, Use dmy dates ইত্যাদি)
ENGLISH_MAINT_TEMPLATES = re.compile(
    r"\{\{\s*(?:(?:Template|টেমপ্লেট)\s*:\s*)?"
    r"(?:Use\s+[^|}]*?(?:English|spelling|dates)|Engvar[A-Za-z]*"
    r"|[^|}]*?(?:ব্রিটিশ|আমেরিকান|ভারতীয়|অস্ট্রেলীয়)\s+ইংরেজি\s*(?:ব্যবহার)?)\s*"
    r"(?:\|[^}]*)?\}\}\s*\n?",
    re.IGNORECASE,
)


def fix_templates(text: str) -> str:
    s = text
    s = SHORT_DESC.sub("", s)
    s = ENGLISH_MAINT_TEMPLATES.sub("", s)
    s = re.sub(r"\{\{\s*(?:(?:Template|টেমপ্লেট)\s*:\s*)?[Rr]eflist\s*\}\}", "{{সূত্র তালিকা}}", s)

    # তথ্যবক্ত, তথ্যবক্স, তথ্যবাক্স, ইনফোবক্স পরিহার করে প্রমিত 'তথ্যছক'-এ রূপান্তর
    s = re.sub(r"\{\{\s*(?:[Ii]nfobox|তথ্যছক)\s+building\b", "{{তথ্যছক ভবন", s, flags=re.IGNORECASE)
    s = re.sub(r"\{\{\s*তথ্যবক্ত\s+ভবন\b", "{{তথ্যছক ভবন", s)
    s = re.sub(r"\{\{\s*(?:তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স)\b", "{{তথ্যছক", s)

    def _heading(m: re.Match) -> str:
        inner = m.group(1).strip()
        bn = HEADING_MAP.get(inner, HEADING_MAP.get(inner.title()))
        if bn is None:
            return m.group(0)
        return f"== {bn} =="

    s = re.sub(r"^==\s*(.+?)\s*==\s*$", _heading, s, flags=re.MULTILINE)

    def _defaultsort(m: re.Match) -> str:
        val = to_bengali_digits_safe(m.group(1))
        return "{{DEFAULTSORT:" + val + "}}"

    s = re.sub(r"\{\{\s*DEFAULTSORT\s*:\s*([^}]+)\}\}", _defaultsort, s)
    s = clean_templatestyles_remnants(s)
    return s


def clean_templatestyles_remnants(text: str) -> str:
    """CX-এর ভাঙা templatestyles অবশেষ সাফ করা।

    রাখা হয়: বৈধ `<templatestyles src="…"/>` ট্যাগ (স্টাইলিংয়ের জন্য দরকারি)।
    মোছা হয়: `</> templatestyles` ধরনের ভাঙা মার্কার, খালি
    `templatestyles` লাইন — এগুলো CX ভিজ্যুয়াল ভিউতে খালি ব্লক হিসেবে
    দেখা যায় (আপনার স্ক্রিনশটের নিচের দুটো খালি ব্লক)।
    """
    s = text
    # ভাঙা মার্কার: `</> templatestyles`, `<>templatestyles`, একা `templatestyles` লাইন
    # (লাইনসহ পরের newline-ও খাওয়া হয়, যাতে খালি `\n` না থাকে)
    s = re.sub(r"^[ \t]*</?>\s*templatestyles[ \t]*\n?", "", s, flags=re.MULTILINE)
    s = re.sub(r"^[ \t]*templatetstyles[ \t]*\n?", "", s, flags=re.MULTILINE)
    s = re.sub(r"^[ \t]*templatestyles[ \t]*\n?", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s
