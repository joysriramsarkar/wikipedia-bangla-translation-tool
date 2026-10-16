# -*- coding: utf-8 -*-
"""
নিরাপদ বাংলা সংখ্যা কনভার্টার (CX পোস্ট-প্রসেসর)।

উদ্দেশ্য:
- CX/Parsoid HTML ও উইকিটেক্সট — দুটোতেই দৃশ্যমান সংখ্যা বাংলায় (০-৯) করা,
  কিন্তু টেকনিক্যাল অংশ (URL, ট্যাগ অ্যাট্রিবিউট, ref, File নাম, coord,
  ISBN/DOI, ম্যাজিক ওয়ার্ড) অক্ষত রাখা।
- ক্রমবাচক (2nd, 5th, 4th), মুদ্রা (R$ 932.166), বছর (2007),
  বন্ধনীর ভেতরের সংখ্যা (ইউটিসি-03) — সব দৃশ্যমান সংখ্যা রূপান্তর করা।
  পুরনো জার্মান কনভার্টারের মতো ল্যাটিন বন্ধনী দেখলেই পুরো অংশ
  সুরক্ষিত করে ফেলা — এই ভুল এখানে করা হয়নি।

বিভাজক নীতি: বাংলা উইকিতে `১৬,১২,০৭৭.২` ধাঁচে কমা/দশমিক অক্ষত থাকে,
শুধু অঙ্ক বদলায়। তাই `,` `.` `%` `–` অক্ষত রাখা হয়।
"""
import re

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

# --- ক্রমবাচক প্রত্যয়: 1st→১ম, 2nd→২য়, 3rd→৩য়, 4th→৪র্থ, বাকি th→ম ---
def _ordinal_suffix(n: int) -> str:
    if n == 1:
        return "ম"
    if n == 2:
        return "য়"
    if n == 3:
        return "য়"
    if n == 4:
        return "র্থ"
    return "ম"


def convert_ordinals(text: str) -> str:
    """`2nd` → `২য়`, `5th` → `৫ম`, `4th` → `৪র্থ`, `2007` অক্ষত।"""

    def _repl(m: re.Match) -> str:
        num = int(m.group(1))
        bn_num = str(m.group(1)).translate(BN_DIGITS)
        return f"{bn_num}{_ordinal_suffix(num)}"

    # শুধু 1-2 অঙ্কের ক্রমবাচক (rank/ক্রম)। সাল (2007) এখানে পড়বে না।
    return re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", _repl, text, flags=re.IGNORECASE)


BN_TO_ASCII_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")


def fix_template_parameter_digits(text: str) -> str:
    """টেমপ্লেট প্যারামিটার নাম ও ভ্যারিয়েবলের ভেতরের অঙ্ক ল্যাটিন/ASCII (0-9) রাখা।
    মিডিয়াউইকি/লুয়া মডিউলে (যেমন Module:Navbox, Module:Infobox) group১, list১,
    subdivision_type১, {{{১|...}}} ইত্যাদি কাজ করে না এবং টেমপ্লেট বাক্স ভেঙে যায়।
    """
    if not text:
        return text

    def _repl_key(m: re.Match) -> str:
        return m.group(0).translate(BN_TO_ASCII_DIGITS)

    # |group১ =, |list১০ =, |১ = ইত্যাদি প্যারামিটার কী
    text = re.sub(
        r"\|\s*[a-zA-Z0-9_\u0980-\u09FF]*[০-৯]+[a-zA-Z0-9_\u0980-\u09FF]*\s*=",
        _repl_key,
        text,
    )

    def _repl_var(m: re.Match) -> str:
        return m.group(0).translate(BN_TO_ASCII_DIGITS)

    # {{{১|..., {{{param১|..., {{{১}}} ভ্যারিয়েবল
    text = re.sub(
        r"\{\{\{\s*[a-zA-Z0-9_\u0980-\u09FF]*[০-৯]+[a-zA-Z0-9_\u0980-\u09FF]*\s*(?:\||\}\}\})",
        _repl_var,
        text,
    )
    return text


# উইকিটেক্সটের ভেতরে সুরক্ষিত রাখার প্যাটার্ন (টেক্সট-নোডের ভেতরেও)
_WIKI_PROTECT = [
    r"https?://[^\s<>\|\]\}]+",          # URL
    r"www\.[^\s<>\|\]\}]+",              # bare URL
    r"\[\[(?:File|Image):[^\]]+\]\]",    # File/Image লিঙ্ক (পুরোটা)
    r"\{\{[Cc]oord\|[^}]+\}\}",          # coord টেমপ্লেট
    r"\bISBN[\s:]*[0-9Xx\- ]{10,}",      # ISBN
    r"\bDOI[\s:]*[^\s<>\|\}]+",          # DOI
    r"\bPMID[\s:]*\d+",                  # PMID
    r"__[A-Z]+__",                       # __TOC__ ইত্যাদি
    r"~~~~+",                            # স্বাক্ষর
    # উইকিটেমপ্লেট প্যারামিটার নাম (যেমন |group1 =, |list10 =, |1 =, |leader_title2 =)
    # কোড বা মডিউল আইডেন্টিফায়ারে ল্যাটিন অঙ্ক না থাকলে টেমপ্লেট বক্স ভেঙে যায়
    r"\|\s*[a-zA-Z0-9_\u0980-\u09FF]*\d+[a-zA-Z0-9_\u0980-\u09FF]*\s*=",
    # উইকিটেমপ্লেট পজিশনাল ভ্যারিয়েবল (যেমন {{{1|...}}}, {{{2}}})
    r"\{\{\{\s*[a-zA-Z0-9_\u0980-\u09FF]*\d+[a-zA-Z0-9_\u0980-\u09FF]*\s*(?:\||\}\}\})",
    # উইকিটেবিল ও স্টাইল অ্যাট্রিবিউট (ল্যাটিন থাকবে যাতে সিএসএস/টেবিল না ভাঙে)
    r'rowspan\s*=\s*["\']?\d+["\']?',
    r'colspan\s*=\s*["\']?\d+["\']?',
    r'width\s*=\s*["\']?[\d%empx\.]+["\']?',
    r'height\s*=\s*["\']?[\d%empx\.]+["\']?',
    r'style\s*=\s*"[^"]*"',
    r"style\s*=\s*'[^']*'",
    r'font-size\s*:\s*\d+[%empxpt]+',
    r'#[0-9a-fA-F]{3,8}\b',
    r'\b(?:rgb|rgba|hsl|hsla)\([^)]+\)',
    r'<\s*br\s*/?\s*>',
]

_HTML_TAG_SPLIT = re.compile(r"(<[^>]*>)")


def _convert_text_node(node: str) -> str:
    """একটা প্লেইন টেক্সট অংশে সুরক্ষা + ordinal + অঙ্ক রূপান্তর।"""
    placeholders: list[tuple[str, str]] = []

    def _save(m: re.Match) -> str:
        tag = f"__CXTOK{len(placeholders)}__"
        placeholders.append((tag, m.group(0)))
        return tag

    s = node
    for pat in _WIKI_PROTECT:
        s = re.sub(pat, _save, s)
    s = convert_ordinals(s)
    s = s.translate(BN_DIGITS)
    for tag, orig in reversed(placeholders):
        # placeholder-এর ভেতরের অঙ্কও বাংলায় বদলে গিয়ে থাকতে পারে, দুটোই ফেরাই
        s = s.replace(tag.translate(BN_DIGITS), orig).replace(tag, orig)
    return s


def to_bengali_digits_safe(text: str) -> str:
    """HTML ট্যাগ অক্ষত রেখে দৃশ্যমান টেক্সটের সংখ্যা বাংলায় করে।

    - `<...>` ট্যাগ (অ্যাট্রিবিউট: href/src/style/rowspan/...) অপরিবর্তিত।
    - ট্যাগের বাইরের টেক্সটে `_convert_text_node` প্রয়োগ হয়।
    - তাই `BRT (ইউটিসি-03)`, `R$ 932.166 billion`, `(US$ 172.917 billion)`
      — সব ক্ষেত্রে অঙ্ক বাংলা হয়; URL/coord/ref ভাঙে না।
    """
    if not text:
        return text
    parts = _HTML_TAG_SPLIT.split(text)
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        if p.startswith("<") and p.endswith(">"):
            out.append(p)  # ট্যাগ অক্ষত
        else:
            out.append(_convert_text_node(p))
    res = "".join(out)
    return fix_template_parameter_digits(res)

