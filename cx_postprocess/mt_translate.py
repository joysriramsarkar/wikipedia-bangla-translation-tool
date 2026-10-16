# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া উইকিটেক্সট মেশিন ট্রান্সলেশন ইঞ্জিন

উইকিটেক্সট-এর জটিল ট্যাগ, টেমপ্লেট ও লিংক অক্ষত রেখে
প্রাকৃতিক ভাষার বাক্যগুলো বাংলায় অনুবাদ করে।
"""
import re
import urllib.request
import urllib.parse
import json
import time

from .infobox_map import INFOBOX_TYPE_MAP
from .pipeline import fix_text

GOOGLE_TR_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q="


def _translate_raw_chunk(text: str, sl: str = "en", tl: str = "bn") -> str:
    """একক টেক্সট চাঙ্ক অনুবাদ করা"""
    if not text or not text.strip():
        return text
    
    url = GOOGLE_TR_URL.format(sl=sl, tl=tl) + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data[0]:
                return "".join([part[0] for part in data[0] if part and part[0]])
    except Exception as e:
        print(f"MT chunk error: {e}")
    return text


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

    # ১. <ref>...</ref> ও স্বয়ংসম্পূর্ণ <ref ... /> ট্যাগ মাস্ক করা
    s = re.sub(r"<ref\b[^>]*>[\s\S]*?<\/ref>", lambda m: make_ph(m.group(0)), s)
    s = re.sub(r"<ref\b[^>]*\/>", lambda m: make_ph(m.group(0)), s)

    # ২. ফাইল/চিত্র লিঙ্ক [[File:...]] বা [[চিত্র:...]] মাস্ক করা
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

    # প্লেসহোল্ডারগুলো পুনরুদ্ধার করা
    for i, ph in enumerate(placeholders):
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

    for line in lines:
        stripped = line.strip()

        # খালি লাইন সরাসরি রাখা
        if not stripped:
            translated_lines.append("")
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

            # প্রযুক্তিগত প্যারামিটার (CSS ক্লাস, স্টেট ইত্যাদি) অক্ষত রাখা
            if param_clean in TECHNICAL_PARAM_KEYS:
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
