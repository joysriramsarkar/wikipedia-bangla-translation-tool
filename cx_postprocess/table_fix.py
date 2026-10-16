# -*- coding: utf-8 -*-
"""
উইকিটেবিল ফিক্স (ধাপ-৩)।

সমস্যা:
- `rowspan="2"`, `colspan="3"`, `width="25em"`-এর সংখ্যা বাংলায় বদলে গেলে
  টেবিল ভাঙে। এগুলো ল্যাটিন থাকতে হবে।
- CX থেকে আসা টেবিলে `|-` একই লাইনে আটকে থাকে (`| cell|-`),
  খালি ঘর থাকে (ডানে ভাঙা বাক্স হয়)।

কাজ:
1. টেবিল-অ্যাট্রিবিউট সুরক্ষা: rowspan/colspan/width/style/class-এর মান
   placeholder-এ সরিয়ে রাখা, শেষে ফেরত দেওয়া।
2. গঠন: `|-` পৃথক লাইনে আনা; সম্পূর্ণ খালি `||` ঘরে `&nbsp;` বসানো।
3. ঘরের দৃশ্যমান লেখায় সংখ্যা বাংলা করা (bn_digits_safe দিয়ে)।
"""
import re
from .bn_digits_safe import to_bengali_digits_safe

_ATTR_PATS = [
    r'rowspan\s*=\s*["\']?\d+["\']?',
    r'colspan\s*=\s*["\']?\d+["\']?',
    r'width\s*=\s*["\']?[\d%empx\.]+["\']?',
    r'style\s*=\s*"[^"]*"',
    r'class\s*=\s*"[^"]*"',
]


def _protect_attrs(block: str) -> tuple[str, list[str]]:
    saved: list[str] = []

    def _save(m: re.Match) -> str:
        saved.append(m.group(0))
        return f"__TBLATTR{len(saved) - 1}__"

    s = block
    for pat in _ATTR_PATS:
        s = re.sub(pat, _save, s)
    return s, saved


def _restore_attrs(block: str, saved: list[str]) -> str:
    from .bn_digits_safe import BN_DIGITS

    s = block
    for i in reversed(range(len(saved))):
        tag = f"__TBLATTR{i}__"
        # placeholder-এর অঙ্ক বাংলায় বদলে গিয়ে থাকলে দুটো রূপই ফেরাও
        s = s.replace(tag.translate(BN_DIGITS), saved[i]).replace(tag, saved[i])
    return s


def fix_table_block(block: str) -> str:
    """একটা `{| … |}` ব্লকের গঠন + সংখ্যা ঠিক করা।"""
    s, saved = _protect_attrs(block)
    # 1. `|-` পৃথক লাইনে (`| cell|-` → `| cell\n|-`)
    s = re.sub(r"[ \t]*\|\-[ \t]*", "\n|-\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    # 2. সম্পূর্ণ খালি ঘর: `||` / `||\n` → `|| &nbsp;`
    s = re.sub(r"\|\|[ \t]*(\n|\|\-|$)", r"|| &nbsp; \1", s)
    s = re.sub(r"^\|[ \t]*$", "| &nbsp;", s, flags=re.MULTILINE)
    # 3. ঘরের দৃশ্যমান সংখ্যা বাংলা (অ্যাট্রিবিউট সুরক্ষিত আছে)
    s = to_bengali_digits_safe(s)
    s = _restore_attrs(s, saved)
    return s


_TABLE_RE = re.compile(r"\{\|.*?\|\}", re.DOTALL)


def fix_tables(text: str) -> str:
    """টেক্সটের সব `{| … |}` ব্লকে fix_table_block প্রয়োগ।"""
    return _TABLE_RE.sub(lambda m: fix_table_block(m.group(0)), text)
