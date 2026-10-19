# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া উইকিটেক্সট মেশিন ট্রান্সলেশন ইঞ্জিন

উইকিটেক্সট-এর জটিল ট্যাগ, টেমপ্লেট ও লিংক অক্ষত রেখে
প্রাকৃতিক ভাষার বাক্যগুলো বাংলায় অনুবাদ করে।
"""
import re
import urllib.error
import urllib.request
import urllib.parse
import json
import time

from .infobox_map import INFOBOX_TYPE_MAP
from .pipeline import fix_text
from .bn_digits_safe import to_bengali_digits_safe

GOOGLE_TR_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q="
GOOGLE_CLIENT5_URL = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={sl}&tl={tl}&q="
MYMEMORY_URL = "https://api.mymemory.translated.net/get?q={q}&langpair={sl}|{tl}"

_GTX_AVAILABLE = True
_CACHE = {}


def _parse_clients5_payload(data) -> str:
    """clients5 এন্ডপয়েন্টের JSON থেকে অনূদিত লেখা বের করে।"""
    if not isinstance(data, list):
        return ""
    parts = []
    for item in data:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, list) and item and isinstance(item[0], str):
            parts.append(item[0])
    return "".join(parts)


def _translate_gtx(text: str, sl: str, tl: str) -> str:
    global _GTX_AVAILABLE
    if not _GTX_AVAILABLE:
        return ""
    url = GOOGLE_TR_URL.format(sl=sl, tl=tl) + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            _GTX_AVAILABLE = False  # একবার 429 এলে বাকি চাঙ্কে চেষ্টা নয়
        raise
    if data and data[0]:
        return "".join(part[0] for part in data[0] if part and part[0])
    return ""


def _translate_clients5(text: str, sl: str, tl: str) -> str:
    """গুগল অনুবাদের বিকল্প এন্ডপয়েন্ট (gtx বন্ধ/429 হলে)।"""
    url = GOOGLE_CLIENT5_URL.format(sl=sl, tl=tl) + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return _parse_clients5_payload(json.loads(resp.read().decode("utf-8")))


def _translate_mymemory(text: str, sl: str, tl: str) -> str:
    """শেষ ফলব্যাক; দীর্ঘ লেখা পাঠানো হয় না (API সীমা)।"""
    if len(text) > 480:
        return ""
    url = MYMEMORY_URL.format(q=urllib.parse.quote(text), sl=sl, tl=tl)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if int(data.get("responseStatus", 0)) == 200:
        return (data.get("responseData") or {}).get("translatedText", "") or ""
    return ""


def _translate_raw_chunk(text: str, sl: str = "en", tl: str = "bn") -> str:
    """একক টেক্সট চাঙ্ক অনুবাদ করা — একাধিক প্রদানকারীই ব্যর্থ হলে মূল লেখা ফেরত।"""
    if not text or not text.strip():
        return text

    key = (text, sl, tl)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached

    for translator in (_translate_gtx, _translate_clients5, _translate_mymemory):
        try:
            result = translator(text, sl, tl)
        except Exception as e:
            print(f"MT {translator.__name__} error: {e}")
            continue
        if result and result.strip():
            if len(_CACHE) < 1000:
                _CACHE[key] = result
            return result
    return text


def _split_top_level(text: str, sep: str = "|"):
    """Split on ``sep`` outside ``[[...]]`` and ``{{...}}``."""
    parts = []
    buffer = []
    link_depth = 0
    template_depth = 0
    i = 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair == "[[":
            link_depth += 1
            buffer.append(pair)
            i += 2
            continue
        if pair == "]]":
            link_depth = max(0, link_depth - 1)
            buffer.append(pair)
            i += 2
            continue
        if pair == "{{":
            template_depth += 1
            buffer.append(pair)
            i += 2
            continue
        if pair == "}}":
            template_depth = max(0, template_depth - 1)
            buffer.append(pair)
            i += 2
            continue
        if text[i] == sep and link_depth == 0 and template_depth == 0:
            parts.append("".join(buffer))
            buffer = []
            i += 1
            continue
        buffer.append(text[i])
        i += 1
    parts.append("".join(buffer))
    return parts


def _find_link_end(text: str, start: int) -> int:
    """Return the index just after the matching ``]]`` for a link at ``start``."""
    depth = 0
    i = start
    while i < len(text) - 1:
        if text.startswith("[[", i):
            depth += 1
            i += 2
            continue
        if text.startswith("]]", i):
            depth -= 1
            i += 2
            if depth == 0:
                return i
            continue
        i += 1
    return -1


_FILE_OPTION_WORDS = {
    "thumb", "thumbnail", "frame", "framed", "frameless", "border",
    "left", "right", "center", "none", "upright", "baseline", "sub",
    "super", "top", "text-top", "middle", "bottom", "text-bottom",
}


def _is_file_option(part: str) -> bool:
    value = part.strip().lower()
    if value in _FILE_OPTION_WORDS:
        return True
    if re.fullmatch(r"(?:upright\s*=\s*)?[\d.]+(?:x[\d.]+)?\s*px", value):
        return True
    if re.fullmatch(r"\d+x\d+", value):
        return True
    if re.fullmatch(r"(?:alt|link|lang|page|class)\s*=.*", value, re.DOTALL):
        return True
    return False


def _find_template_end(text: str, start: int) -> int:
    depth = 0
    i = start
    while i < len(text) - 1:
        if text.startswith("{{", i):
            depth += 1
            i += 2
            continue
        if text.startswith("}}", i):
            depth -= 1
            i += 2
            if depth == 0:
                return i
            continue
        i += 1
    return -1


_DISPLAY_TEMPLATES = {"about", "other uses", "for", "redirect",
                      "nihongo", "nihongo2", "nihongo3", "literally"}


def _translate_display_templates(text: str, sl: str, tl: str) -> str:
    """Translate reader-facing template arguments (About, Nihongo, ...).

    Template name and Japanese/technical arguments stay untouched; only the
    English display text is translated, so the hatnote is not left in English.
    """
    out = []
    i = 0
    while True:
        match = re.search(r"\{\{\s*([A-Za-z][A-Za-z0-9 ]*?)\s*\|", text[i:])
        if not match:
            out.append(text[i:])
            break
        start = i + match.start()
        end = _find_template_end(text, start)
        if end == -1:
            out.append(text[i:])
            break
        name = match.group(1).strip().lower()
        if name not in _DISPLAY_TEMPLATES:
            out.append(text[i:start + 2])
            i = start + 2
            continue
        out.append(text[i:start])
        parts = _split_top_level(text[start + 2:end - 2])
        translated = [parts[0]]
        for index, part in enumerate(parts[1:], start=1):
            key = None
            value = part
            if "=" in part:
                key, value = part.split("=", 1)
            should_translate = False
            if name.startswith("nihongo"):
                should_translate = (index == 1 or index >= 4
                                    or (key is not None and key.strip().lower() == "lit"))
            elif key is None:
                should_translate = True
            elif key.strip().lower() in {"text", "about"}:
                should_translate = True
            if should_translate and re.search(r"[A-Za-z]{2,}", value):
                stripped = value.strip()
                if stripped.startswith("{{") and stripped.endswith("}}"):
                    # nested display template (যেমন {{literally|...}}) — নাম অক্ষত রেখে ভেতরে ঢুকে অনুবাদ
                    value = _translate_display_templates(stripped, sl=sl, tl=tl)
                else:
                    value = _translate_raw_chunk(stripped, sl=sl, tl=tl)
            translated.append((key + "=" + value) if key is not None else value)
        out.append("{{" + "|".join(translated) + "}}")
        i = end
    return "".join(out)


def _translate_external_links(text: str, sl: str, tl: str) -> str:
    """Translate the visible label of ``[https://... label]`` links only."""
    def repl(match):
        url = match.group(1)
        label = match.group(2)
        if label and re.search(r"[A-Za-z]{2,}", label):
            label = translate_wikitext_block(label.strip(), sl=sl, tl=tl)
        return f"[{url} {label}]" if label else f"[{url}]"

    return re.sub(r"\[(https?://[^\s\]]+)(?:\s+([^\]]+))?\]", repl, text)


def _translate_file_links(text: str, sl: str, tl: str) -> str:
    """Translate only the caption of ``[[File:...|thumb|caption]]`` links.

    File name and options (thumb/left/200px/alt=) stay untouched, so images
    keep working while the visible caption becomes Bengali.
    """
    out = []
    i = 0
    while True:
        match = re.search(r"\[\[\s*(?:File|Image|চিত্র|ফাইল)\s*:", text[i:], re.IGNORECASE)
        if not match:
            out.append(text[i:])
            break
        start = i + match.start()
        end = _find_link_end(text, start)
        if end == -1:
            out.append(text[i:])
            break
        out.append(text[i:start])
        inner = text[start + 2:end - 2]
        parts = _split_top_level(inner)
        rest = parts[1:]
        caption = None
        if rest and not _is_file_option(rest[-1]):
            caption = rest[-1]
            rest = rest[:-1]
        if caption and re.search(r"[A-Za-z\u0980-\u09FF]{2,}", caption):
            caption = translate_wikitext_block(caption.strip(), sl=sl, tl=tl).strip()
        rebuilt = "[[" + parts[0] + "".join(f"|{p}" for p in rest)
        if caption is not None:
            rebuilt += f"|{caption}"
        rebuilt += "]]"
        out.append(rebuilt)
        i = end
    return "".join(out)


def translate_wikitext_block(block: str, sl: str = "en", tl: str = "bn") -> str:
    """
    উইকিটেক্সটের একটি অনুচ্ছেদ সুরক্ষিত রেখে অনুবাদ করে।
    টেমপ্লেট {{...}}, রেফারেন্স <ref>...</ref>, ইমেজ [[File:...]] অক্ষত রাখা হয়।
    """
    if not block.strip():
        return block

    # বিশেষ ব্লক যেগুলো অনুবাদ করার প্রয়োজন নেই (শুধুমাত্র স্ট্রাকচার বা ক্যাটাগরি)
    if block.startswith("{|") or block.startswith("|}") or block.startswith("|-"):
        return block
    if re.match(r"^\[\[(Category|বিষয়শ্রেণী):", block, re.IGNORECASE):
        return block

    placeholders = []

    def make_ph(val: str) -> str:
        idx = len(placeholders)
        placeholders.append(val)
        return f" ZWPHL{idx}Z "

    s = block

    # ১. আগে স্বয়ংসম্পূর্ণ <ref ... /> মাস্ক করা, তারপর <ref>...</ref>।
    #    নাহলে `<ref name="x"/>`-কে খোলা ট্যাগ ধরে পরের </ref> পর্যন্ত সব
    #    টেক্সট গ্রাস হয়ে অনুবাদ বাদ পড়ে।
    s = re.sub(r"<ref\b[^>]*?/\s*>", lambda m: make_ph(m.group(0)), s)
    s = re.sub(r"<ref\b[^>]*?(?<!/)>[\s\S]*?<\/ref>", lambda m: make_ph(m.group(0)), s)
    s = re.sub(r"<\/?(?:includeonly|noinclude|onlyinclude)\s*>", lambda m: make_ph(m.group(0)), s, flags=re.IGNORECASE)

    # ২. ফাইল/চিত্র লিঙ্কের কেবল ক্যাপশন অনুবাদ করা, তারপর বাকিটা মাস্ক করা
    s = _translate_file_links(s, sl, tl)
    s = _translate_external_links(s, sl, tl)
    s = _translate_display_templates(s, sl, tl)
    s = re.sub(r"\[\[(File|Image|চিত্র|ফাইল):[\s\S]*?\]\]", lambda m: make_ph(m.group(0)), s, flags=re.IGNORECASE)

    # ৩. নেস্টেড টেমপ্লেট {{...}} মাস্ক করা (বাইরের স্তর থেকে)
    # প্রথমে ৩-স্তর পর্যন্ত টেমপ্লেট মাস্ক
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]+\}\}", lambda m: make_ph(m.group(0)), s)

    # ৪. এক্সটার্নাল লিঙ্ক [http...] মাস্ক করা
    s = re.sub(r"\[https?://[^\s\]]+(?:\s+[^\]]+)?\]", lambda m: make_ph(m.group(0)), s)

    # ৫. <br/> ও <br> লাইনব্রেক ট্যাগ মাস্ক করা (যাতে গুগল অনুবাদ এটিকে নিউলাইনে ভেঙে না ফেলে)
    s = re.sub(r"<\s*br\s*/?\s*>", lambda m: make_ph(m.group(0)), s, flags=re.IGNORECASE)

    # ৬. উইকিলিংক [[Link|Text]] বা [[Link]] সুরক্ষা
    # [[A|B]] থাকলে B অনুবাদযোগ্য রাখা এবং A লিঙ্ক রাখা
    def link_repl(m):
        full = m.group(0)
        target = m.group(1).strip()
        disp = m.group(2).strip() if m.group(2) else target
        # লিংক টার্গেট মাস্ক করা
        return f"[[{target}|{disp}]]"
    # সোজাসুজি উইকিলিংকও অনেক সময় টেক্সটের অংশ, তাই সরাসরি রাখা নিরাপদ

    # অনুবাদ কল করা (যদি অনুবাদের মতো শব্দ থাকে)
    if re.search(r"[a-zA-Z]{2,}", s):
        # খুব বড় চাঙ্ক হলে ভাগ করা
        if len(s) > 2500:
            parts = s.split(". ")
            translated_parts = []
            for p in parts:
                translated_parts.append(_translate_raw_chunk(p, sl=sl, tl=tl))
            translated = ". ".join(translated_parts)
        else:
            translated = _translate_raw_chunk(s, sl=sl, tl=tl)
    else:
        translated = s

    # প্লেসহোল্ডারগুলো উল্টো ক্রমে পুনরুদ্ধার করা হয়: বাইরের (nested) টেমপ্লেট
    # আগে বসে, তার ভেতরের টোকেনগুলো পরে প্রতিস্থাপিত হয়। নাহলে ZWPHL টোকেন
    # চূড়ান্ত লেখায় থেকে যায়।
    for i in range(len(placeholders) - 1, -1, -1):
        ph = placeholders[i]
        # <br> ট্যাগে অতিরিক্ত স্পেস পরিহার করা
        if ph.lower().startswith("<br"):
            translated = re.sub(rf"\s*ZWPHL{i}Z\s*", ph, translated)
        else:
            translated = re.sub(rf"\s*ZWPHL{i}Z\s*", f" {ph} ", translated)

    # তথ্যবক্ত/তথ্যবক্স পরিহার ও প্রমিত 'তথ্যছক' নিশ্চিতকরণ
    translated = re.sub(r"\{\{\s*(?:তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স)\b", "{{তথ্যছক", translated)
    translated = re.sub(r"\{\{\s*(?:[Ii]nfobox|তথ্যছক)\s+building\b", "{{তথ্যছক ভবন", translated, flags=re.IGNORECASE)
    translated = re.sub(r"\{\{\s*তথ্যবক্ত\s+ভবন\b", "{{তথ্যছক ভবন", translated)

    return translated.strip()


TECHNICAL_PARAM_KEYS = {
    "state", "navbar", "border", "aboveclass", "belowclass", 
    "listclass", "groupstyle", "bodystyle", "titlestyle", "abovestyle", 
    "belowstyle", "evenodd", "evenstyle", "oddstyle", "style", "class",
    "imageclass", "image_class"
}

# মান অনুবাদ করা হলে টেমপ্লেট/চিত্র/মানচিত্র ভেঙে যায় — এগুলো অক্ষত রাখতে হবে।
UNTRANSLATABLE_PARAM_KEYS = {
    "image", "image_name", "image_size", "image_upright", "image_alt",
    "logo", "logo_size", "logo_alt",
    "map", "map_size", "map_alt", "map_name",
    "mapframe", "mapframe-zoom", "mapframe-width", "mapframe-height",
    "mapframe-wikidata", "mapframe-geomask",
    "pushpin_map", "pushpin_mapsize", "pushpin_label_position",
    "coordinates", "coord", "latd", "latm", "lats", "latns",
    "longd", "longm", "longs", "longew", "coordinates_type",
    "coordinates_region", "coordinates_display", "coordinates_format",
    "website", "url", "grid_ref_uk", "os_grid_reference", "iso_code",
    "iso_region", "subdivision_code", "embedded",
}

_BOOLEAN_VALUES = {"yes", "no", "true", "false"}
_FILE_VALUE_RE = re.compile(r"^\s*(?:File|Image|চিত্র|ফাইল)\s*:", re.IGNORECASE)
_URL_VALUE_RE = re.compile(r"^\s*(?:https?://|www\.)", re.IGNORECASE)


def translate_wikitext_full(wikitext: str, sl: str = "en", tl: str = "bn") -> str:
    """
    সম্পূর্ণ উইকিটেক্সট অনুবাদ ও পাইপলাইন প্রসেসিং।
    """
    if not wikitext or not wikitext.strip():
        return ""

    lines = wikitext.splitlines()
    translated_lines = []

    in_table = False
    in_template = False
    in_gallery = False

    for line in lines:
        stripped = line.strip()

        # খালি লাইন সরাসরি রাখা
        if not stripped:
            translated_lines.append("")
            continue

        # <gallery> ফাইল লাইন: File: নাম অক্ষত, ক্যাপশন অনুবাদ
        if stripped.lower().startswith("<gallery"):
            in_gallery = True
            translated_lines.append(line)
            continue
        if in_gallery:
            if stripped.lower().startswith("</gallery"):
                in_gallery = False
                translated_lines.append(line)
                continue
            if stripped.lower().startswith(("file:", "image:", "চিত্র:", "ফাইল:")):
                parts = _split_top_level(line)
                rest = parts[1:]
                if rest and not _is_file_option(rest[-1].strip()):
                    rest[-1] = translate_wikitext_block(rest[-1].strip(), sl=sl, tl=tl)
                translated_lines.append("|".join([parts[0]] + rest))
                continue
            translated_lines.append(line)
            continue

        # short description বাংলা উইকিপিডিয়ায় নিষিদ্ধ — সম্পূর্ণ মুছে ফেলা
        if re.match(r"^\{\{\s*(?:(?:Template|টেমপ্লেট)\s*:\s*)?[Ss]hort description\b", stripped, re.IGNORECASE):
            continue

        # ইংরেজি উপভাষা ও রক্ষণাবেক্ষণ টেমপ্লেট বর্জন (যেমন Use British/Indian English, Use dmy dates ইত্যাদি)
        if re.match(r"^\{\{\s*(?:(?:Template|টেমপ্লেট)\s*:\s*)?(?:Use\s+[^|}]*?(?:English|spelling|dates)|Engvar[A-Za-z]*|[^|}]*?(?:ব্রিটিশ|আমেরিকান|ভারতীয়|অস্ট্রেলীয়)\s+ইংরেজি\s*(?:ব্যবহার)?)", stripped, re.IGNORECASE):
            continue

        # টেমপ্লেট ডিক্লারেশন লাইন (যেমন {{Navbox |child ... বা {{subgroup ...) সরাসরি রাখা
        if re.match(r"^\{\{\s*(?:[Nn]avbox|[Ss]ubgroup|[Ss]idebar|[Tt]axonbar|[Cc]hild|[Cc]ollapsible)", stripped):
            translated_lines.append(line)
            continue

        # যেকোনো অ-ইনফোবক্স টেমপ্লেটের নাম অক্ষত (যেমন {{Series overview)
        if re.match(r"^(?:<onlyinclude>|<noinclude>)?\{\{\s*[A-Za-z][A-Za-z0-9 _]*\s*$", stripped):
            translated_lines.append(line)
            continue

        # ইনফোবক্স শুরু লাইন (যেমন: {{infobox building বা {{Infobox settlement বা {{তথ্যবক্ত ভবন)
        infobox_header_match = re.match(
            r"^\{\{\s*(?:[Ii]nfobox|তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স|তথ্যছক)\b(?:\s+([a-zA-Z0-9_\u0980-\u09FF ]+?))?(.*)$",
            stripped,
            re.IGNORECASE
        )
        if infobox_header_match:
            raw_type = (infobox_header_match.group(1) or "").strip()
            rest = infobox_header_match.group(2) or ""
            bn_type = INFOBOX_TYPE_MAP.get(raw_type.lower(), raw_type)
            if bn_type:
                translated_lines.append(f"{{{{তথ্যছক {bn_type}{rest}".rstrip())
            else:
                translated_lines.append(f"{{{{তথ্যছক{rest}".rstrip())
            continue

        # হেডিং যেমন == History ==
        heading_match = re.match(r"^(={1,6})\s*(.*?)\s*(={1,6})$", stripped)
        if heading_match:
            eq1, h_text, eq2 = heading_match.groups()
            tr_h = _translate_raw_chunk(h_text, sl=sl, tl=tl).strip()
            translated_lines.append(f"{eq1} {tr_h} {eq2}")
            continue

        # ইনফোবক্স বা টেমপ্লেটের লাইন যেমন | native_name = ... বা | group1 = ...
        if stripped.startswith("|") and "=" in stripped and not in_table:
            parts = stripped.split("=", 1)
            param_key = parts[0]
            param_val = parts[1]
            param_clean = param_key.lstrip("|").strip().lower()

            # প্রযুক্তিগত প্যারামিটার (CSS ক্লাস, স্টেট, চিত্র/মানচিত্রের নাম) অক্ষত রাখা
            if param_clean in TECHNICAL_PARAM_KEYS or param_clean in UNTRANSLATABLE_PARAM_KEYS:
                translated_lines.append(line)
                continue

            # Series overview-এর link/start/end/color/season/series মান যন্ত্র-পাঠ্য; অনুবাদ নয়
            if re.match(r"^(?:link|episodes|start|end|color|season|series)\d+$", param_clean):
                if re.match(r"^episodes\d+$", param_clean):
                    translated_lines.append(f"{param_key}={to_bengali_digits_safe(param_val)}")
                else:
                    translated_lines.append(line)
                continue

            if param_val.strip().startswith("<includeonly>"):
                translated_lines.append(line)
                continue

            # ফাইলনাম, URL ও হ্যাঁ/না-ধরনের মান অনুবাদ করা যাবে না
            value_clean = param_val.strip()
            if (_FILE_VALUE_RE.match(value_clean) or _URL_VALUE_RE.match(value_clean)
                    or value_clean.lower() in _BOOLEAN_VALUES):
                translated_lines.append(line)
                continue

            # প্যারাম মান যদি সাধারণ বাক্য হয় তবে অনুবাদ করা
            if re.search(r"[a-zA-Z]{3,}", param_val) and not re.match(r"^\s*\{\{", param_val):
                tr_val = translate_wikitext_block(param_val, sl=sl, tl=tl)
                # প্যারাম মানের ভেতরে অতিরিক্ত নিউলাইন ঢুকে যাতে লাইন না ভাঙে
                tr_val = tr_val.replace("\r\n", " ").replace("\n", " ")
                translated_lines.append(f"{param_key}= {tr_val}")
            else:
                translated_lines.append(line)
            continue

        # টেবিলের সারি
        if stripped.startswith("{|"):
            in_table = True
            translated_lines.append(line)
            continue
        elif stripped.startswith("|}"):
            in_table = False
            translated_lines.append(line)
            continue

        # টেবিল সেলের ভেতরের টেক্সট
        if in_table:
            if stripped.startswith("|-") or stripped.startswith("|+"):
                translated_lines.append(line)
            elif stripped.startswith("!") or stripped.startswith("|"):
                # টেবিল সেল
                translated_lines.append(translate_wikitext_block(line, sl=sl, tl=tl))
            else:
                translated_lines.append(line)
            continue

        # সাধারণ অনুচ্ছেদ / বুলেট পয়েন্ট
        translated_lines.append(translate_wikitext_block(line, sl=sl, tl=tl))

    translated_wikitext = "\n".join(translated_lines)

    # সবশেষে আমাদের নিয়ম প্রয়োগ (common/cx_postprocess pipeline)
    result = fix_text(translated_wikitext)
    return result.get("fixed", translated_wikitext)
