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

import os
import sys

from .infobox_map import INFOBOX_TYPE_MAP
from .pipeline import fix_text
from .bn_digits_safe import to_bengali_digits_safe, BN_TO_ASCII_DIGITS

try:
    from common.env_loader import (
        DEFAULT_GEMINI_MODEL,
        RATE_LIMIT_FALLBACK_MODEL,
        get_gemini_model,
        get_gemini_fallback_model,
        get_gemini_key,
        DEFAULT_OLLAMA_MODEL,
        DEFAULT_OLLAMA_BASE_URL,
        get_ollama_model,
        get_ollama_base_url,
        get_ollama_key,
        DEFAULT_OPENROUTER_MODEL,
        DEFAULT_OPENROUTER_BASE_URL,
        get_openrouter_model,
        get_openrouter_base_url,
        get_openrouter_key,
        get_ai_provider,
    )
except ImportError:
    _P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if _P not in sys.path:
        sys.path.insert(0, _P)
    try:
        from common.env_loader import (
            DEFAULT_GEMINI_MODEL,
            RATE_LIMIT_FALLBACK_MODEL,
            get_gemini_model,
            get_gemini_fallback_model,
            get_gemini_key,
            DEFAULT_OLLAMA_MODEL,
            DEFAULT_OLLAMA_BASE_URL,
            get_ollama_model,
            get_ollama_base_url,
            get_ollama_key,
            DEFAULT_OPENROUTER_MODEL,
            DEFAULT_OPENROUTER_BASE_URL,
            get_openrouter_model,
            get_openrouter_base_url,
            get_openrouter_key,
            get_ai_provider,
        )
    except ImportError:
        DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
        RATE_LIMIT_FALLBACK_MODEL = "gemini-3.1-flash-lite"
        def get_gemini_model(default=DEFAULT_GEMINI_MODEL): return default
        def get_gemini_fallback_model(default=RATE_LIMIT_FALLBACK_MODEL): return default
        def get_gemini_key(): return ""
        DEFAULT_OLLAMA_MODEL = "llama3.1"
        DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
        def get_ollama_model(default=DEFAULT_OLLAMA_MODEL): return default
        def get_ollama_base_url(default=DEFAULT_OLLAMA_BASE_URL): return default
        def get_ollama_key(): return ""
        DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"
        DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
        def get_openrouter_model(default=DEFAULT_OPENROUTER_MODEL): return default
        def get_openrouter_base_url(default=DEFAULT_OPENROUTER_BASE_URL): return default
        def get_openrouter_key(): return ""
        def get_ai_provider(default="gemini"): return default

GOOGLE_TR_URL = "https://translate.googleapis.com/translate_a/single?client=gtx&sl={sl}&tl={tl}&dt=t&q="
GOOGLE_CLIENT5_URL = "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={sl}&tl={tl}&q="
MYMEMORY_URL = "https://api.mymemory.translated.net/get?q={q}&langpair={sl}|{tl}"

_GTX_BLOCKED_UNTIL = 0.0
_CACHE = {}
_DEAD_MODELS = set()

# লাতিন, সিরিলিক (রুশ), সিজেকে কাঞ্জি/হানি (চীনা/জাপানি), হিরাগানা ও কাতাকানা (জাপানি), হ্যাঙ্গুল ইত্যাদি
TRANSLATABLE_SCRIPT_RE = re.compile(
    r"[A-Za-z\u00C0-\u024F\u0400-\u04FF\u4E00-\u9FFF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]"
)


def has_translatable_content(text: str, min_chars: int = 2) -> bool:
    """যাচাই করে লেখাটিতে অনুবাদযোগ্য লিপি (ইংরেজি, জার্মান, রুশ, চীনা, জাপানি ইত্যাদি) আছে কি না।"""
    if not text:
        return False
    return len(TRANSLATABLE_SCRIPT_RE.findall(text)) >= min_chars


def cleanup_bold_italics(text: str) -> str:
    """যন্ত্র অনুবাদে সৃষ্ট ভাঙা বা ৪টি অ্যাপস্ট্রফি ('''') ৩টিতে রূপান্তর করে।"""
    if "''''" in text:
        text = re.sub(r"(?<!')'{4}(?!')", "'''", text)
    return text


def is_ai_output_structurally_safe(src: str, ai_out: str) -> bool:
    """
    যাচাই করে যে জেমিনাই এআই অনুবাদে উইকিটেক্সট ফরম্যাটিং, টেমপ্লেট বা তথ্যসূত্র মুছে ফেলেছে কি না।
    """
    if not ai_out or not ai_out.strip():
        return False

    # ১. <ref> ট্যাগ যাচাই (তথ্যসূত্র নষ্ট হওয়া সবচেয়ে মারাত্মক)
    src_refs = len(re.findall(r"<ref\b", src, re.IGNORECASE))
    out_refs = len(re.findall(r"<ref\b", ai_out, re.IGNORECASE))
    if src_refs > 0 and out_refs < src_refs:
        return False

    # ২. </ref> সমাপ্তি ট্যাগ যাচাই
    src_ref_close = len(re.findall(r"</ref>", src, re.IGNORECASE))
    out_ref_close = len(re.findall(r"</ref>", ai_out, re.IGNORECASE))
    if src_ref_close > 0 and out_ref_close < src_ref_close:
        return False

    # ৩. টেমপ্লেট {{ ও }} যাচাই
    src_tpl = src.count("{{")
    out_tpl = ai_out.count("{{")
    if src_tpl > 0 and out_tpl < src_tpl:
        return False
    if ai_out.count("{{") != ai_out.count("}}"):
        return False

    # ৪. উইকিলিংক [[ ও ]] যাচাই
    src_links = src.count("[[")
    out_links = ai_out.count("[[")
    if src_links > 0:
        if out_links < int(src_links * 0.8):
            return False
    if ai_out.count("[[") != ai_out.count("]]"):
        return False

    # ৫. দৈর্ঘ্যের অস্বাভাবিক সংকোচন (মাঝপথে ট্রাঙ্কেট হওয়া)
    if len(src) >= 100 and len(ai_out) < int(len(src) * 0.4):
        return False

    return True


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
    global _GTX_BLOCKED_UNTIL
    if time.time() < _GTX_BLOCKED_UNTIL:
        return ""
    url = GOOGLE_TR_URL.format(sl=sl, tl=tl) + urllib.parse.quote(text)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            _GTX_BLOCKED_UNTIL = time.time() + 60.0  # সাময়িকভাবে ৬০ সেকেন্ড বিরতি
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


def _mask_file_links(text: str, make_ph) -> str:
    """Use bracket depth counting to mask file links without premature cutoff."""
    out = []
    i = 0
    pattern = re.compile(r"\[\[\s*(?:File|Image|চিত্র|ফাইল)\s*:", re.IGNORECASE)
    while True:
        match = pattern.search(text[i:])
        if not match:
            out.append(text[i:])
            break
        start = i + match.start()
        end = _find_link_end(text, start)
        if end == -1:
            out.append(text[i:start + 2])
            i = start + 2
            continue
        out.append(text[i:start])
        out.append(make_ph(text[start:end]))
        i = end
    return "".join(out)


def _extract_and_translate_file_links(text: str, sl: str = "en", tl: str = "bn"):
    """
    উইকিটেক্সটে থাকা সমস্ত [[File:...]] / [[Image:...]] / [[চিত্র:...]] / [[ফাইল:...]]
    লিঙ্ক (এক বা একাধিক লাইনব্যাপী) খুঁজে বের করে কেবল ক্যাপশন অংশ অনুবাদ করে।
    মূল ফাইলের নাম ও অপশন (thumb, 350px ইত্যাদি) সর্বদা অপরিবর্তিত থাকে।
    """
    out = []
    placeholders = {}
    i = 0
    pattern = re.compile(r"\[\[\s*(?:File|Image|চিত্র|ফাইল)\s*:", re.IGNORECASE)
    while True:
        match = pattern.search(text[i:])
        if not match:
            out.append(text[i:])
            break
        start = i + match.start()
        end = _find_link_end(text, start)
        if end == -1:
            out.append(text[i:start + 2])
            i = start + 2
            continue
        out.append(text[i:start])
        inner = text[start + 2:end - 2]
        parts = _split_top_level(inner)
        file_target = parts[0]  # ফাইলের নাম কখনো অনুবাদ নয়!
        rest = parts[1:]
        caption = None
        if rest and not _is_file_option(rest[-1].strip()):
            caption = rest[-1]
            rest = rest[:-1]

        if caption and re.search(r"[A-Za-z\u0980-\u09FF]{2,}", caption):
            caption_tr = translate_wikitext_block(caption.strip(), sl=sl, tl=tl).strip()
        else:
            caption_tr = caption

        rebuilt = "[[" + file_target + "".join(f"|{p}" for p in rest)
        if caption_tr is not None:
            rebuilt += f"|{caption_tr}"
        rebuilt += "]]"

        ph_key = f"__FILE_LINK_PLACEHOLDER_{len(placeholders)}__"
        placeholders[ph_key] = rebuilt
        out.append(ph_key)
        i = end

    return "".join(out), placeholders


def translate_paragraph_gemini(
    text: str,
    api_key: str | None,
    model: str = DEFAULT_GEMINI_MODEL,
    sl: str = "en",
    tl: str = "bn",
    fallback_model: str = RATE_LIMIT_FALLBACK_MODEL,
    custom_instruction: str | None = None,
) -> str:
    """
    গুগল জেমিনাই (Gemini AI) এপিআই ব্যবহার করে উইকিটেক্সট অনুচ্ছেদ
    সাবলীল, প্রমিত ও প্রাসঙ্গিক বাংলায় অনুবাদ করে।
    ডিফল্ট: gemini-3.5-flash; রেট লিমিট (HTTP 429) এলে gemini-3.1-flash-lite।
    """
    if not text or not text.strip() or not api_key:
        return text

    if not has_translatable_content(text, 2):
        return text

    active_model = model or DEFAULT_GEMINI_MODEL
    # ৩.১ ফ্ল্যাশ মডেলের সঠিক এপিআই নাম gemini-3.1-flash-lite
    if active_model in ("gemini-3.1-flash", "3.1-flash"):
        active_model = RATE_LIMIT_FALLBACK_MODEL
    elif active_model in ("gemma-4-26b", "gemma-26b", "gemma"):
        active_model = "gemma-4-26b-a4b-it"
    elif active_model in ("gemma-4-31b", "gemma-31b"):
        active_model = "gemma-4-31b-it"

    if active_model in _DEAD_MODELS:
        return ""

    is_gemma = active_model.lower().startswith("gemma")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={api_key}"
    system_prompt = (
        (custom_instruction + "\n\n" if custom_instruction else "") +
        "তুমি বাংলা উইকিপিডিয়ার একজন অভিজ্ঞ সম্পাদক ও অনুবাদক। "
        "প্রদত্ত উইকিটেক্সট অনুচ্ছেদটি (Paragraph) অত্যন্ত সাবলীল, প্রাঞ্জল ও প্রমিত বাংলায় অনুবাদ করো।\n\n"
        "বাধ্যতামূলক উইকিপিডিয়া নিয়মাবলি:\n"
        "১. কোনো যান্ত্রিক ভাব রাখা যাবে না; খাঁটি বাংলা ভাষারীতিতে স্বাভাবিক ও প্রাঞ্জল বাক্য গঠন করো।\n"
        "২. উইকিটেক্সটের সমস্ত ফরম্যাটিং, টেমপ্লেট ও রেফারেন্স হুবহু অক্ষত রাখো: কোনো <ref>...</ref>, "
        "<ref name=.../>, {{...}}, [[...]], ''...'' বা '''...''' বাদ দেওয়া বা মোছা যাবে না।\n"
        "৩. লিংকের প্রদর্শিত টেক্সট বাক্যের ব্যাকরণ ও ভাষার সাথে মিলিয়ে বাংলায় অনুবাদ করো (যেমন: [[Geography|geographic]] -> [[ভূগোল|ভৌগোলিক]])। মূল নিবন্ধের নাম বা উইকিসোর্স/ইন্টারউইকি লিংক অক্ষত রাখো।\n"
        "৪. দৃশ্যমান সমস্ত সংখ্যা বাংলায় (০-৯) রূপান্তর করো। তবে ফাইলের নাম, URL, প্যারামিটারের নাম বা ref name-এর ভেতরের সংখ্যা ইংরেজিতেই রাখো।\n"
        "৫. প্রি-কম্পোজড বাংলা বর্ণ (য়, ড়, ঢ়) ব্যবহার করো।\n"
        "৬. শব্দের শুরুতে কখনো 'ৎ' ব্যবহার করবে না (যেমন tsunami -> সুনামি)।\n"
        "৭. ক্ষেত্রফলের এককে ল্যাটিন সুপারস্ক্রিপ্ট (km²) পরিহার করে 'বর্গকিমি' বা 'কিমি<sup>২</sup>' ব্যবহার করো।\n"
        "৮. কোনো অতিরিক্ত ভূমিকা বা ব্যাখ্যা ছাড়া শুধুমাত্র অনূদিত উইকিটেক্সট অনুচ্ছেদটি ফেরত দাও।\n"
        "৯. '__DOC_REF_PLACEHOLDER_X__' বা '__FILE_LINK_PLACEHOLDER_X__' জাতীয় প্লেসহোল্ডার কোড এবং এর ভেতরের ইংরেজি সংখ্যা হুবহু অক্ষত রাখো, কোনোভাবেই পরিবর্তন বা অনুবাদ করবে না।"
    )
    if is_gemma:
        # জেম্মা মডেলে systemInstruction সমর্থিত নয় (HTTP 400 দেয়), তাই প্রম্পটের ভেতরেই দিতে হয়
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\nউইকিটেক্সট অনুচ্ছেদটি অনুবাদ করো (কোনো ভূমিকা বা ব্যাকরণ বিশ্লেষণ ছাড়া শুধু অনূদিত উইকিটেক্সট):\n\n{text}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
    else:
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"উইকিটেক্সট অনুচ্ছেদটি অনুবাদ করো:\n\n{text}"}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {"text": system_prompt}
                ]
            },
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192
            }
        }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    max_retries = 2
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                res_json = json.loads(resp.read().decode("utf-8"))
                candidates = res_json.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    if parts and "text" in parts[0]:
                        out = parts[0]["text"].strip()
                        out = re.sub(r"^```(?:wikitext|wiki)?\s*", "", out, flags=re.IGNORECASE)
                        out = re.sub(r"\s*```$", "", out)
                        if is_gemma:
                            # জেম্মার চেইন-অব-থট ব্যাখ্যামূলক লাইন থাকলে সর্বশেষ অনুচ্ছেদ অংশ নেওয়া
                            lines = [ln.strip() for ln in out.splitlines() if ln.strip()]
                            if lines and any(ln.startswith("* ") for ln in lines[:-1]):
                                for cand in reversed(lines):
                                    if not cand.startswith("*") and not cand.startswith("-") and len(cand) > 5:
                                        out = cand
                                        break
                        return out.strip()
            return ""
        except urllib.error.HTTPError as e:
            if e.code == 404:
                _DEAD_MODELS.add(active_model)
                print(f"Gemini API 404: Model '{active_model}' not found. Marking model as dead.")
                return ""
            elif e.code == 429:
                # রেট লিমিট এলে ৩.১ ফ্ল্যাশ (gemini-3.1-flash-lite)-এ ফলব্যাক
                fallback = fallback_model or RATE_LIMIT_FALLBACK_MODEL
                if active_model != fallback and fallback not in _DEAD_MODELS:
                    print(f"Gemini API HTTP 429 (Rate Limit) on {active_model}. Falling back to {fallback}...")
                    fb_out = translate_paragraph_gemini(
                        text, api_key, model=fallback, sl=sl, tl=tl, fallback_model=fallback
                    )
                    if fb_out:
                        return fb_out
                if attempt < max_retries:
                    backoff = 1.5 * (2 ** attempt)
                    print(f"Gemini API HTTP 429 on {active_model}, retrying in {backoff}s...")
                    time.sleep(backoff)
                    continue
                else:
                    print(f"Gemini API HTTP Error 429 (Rate Limit exceeded) for {active_model}")
                    return ""
            elif e.code in (500, 502, 503, 504) and attempt < max_retries:
                backoff = 1.5 * (2 ** attempt)
                print(f"Gemini API HTTP {e.code}, retrying in {backoff}s...")
                time.sleep(backoff)
                continue
            else:
                print(f"Gemini API HTTP Error {e.code}: {e.reason}")
                return ""
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1.0)
                continue
            print(f"Gemini API request failed: {e}")
            return ""
    return ""


def translate_wikitext_block(
    block: str,
    sl: str = "en",
    tl: str = "bn",
    gemini_key: str | None = None,
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
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

    # যদি জেমিনাই এআই কী দেওয়া থাকে, তবে শুধুমাত্র আসল বর্ণনামূলক অনুচ্ছেদ (prose paragraphs)
    # এআই দিয়ে অনুবাদ করা। তালিকা, একক উইকিলিংক, সংক্ষিপ্ত পদ বা টেবিল সেল দ্রুত ও নির্ভুল মেশিন অনুবাদে চলবে।
    is_prose = (
        len(block.split()) >= 6
        and not re.match(r"^\s*([*#:;!|{\[]|<br|\{\{)", block)
        and not re.search(r"<\s*br\s*/?\s*>$", block.strip(), re.IGNORECASE)
    )
    ai_provider = (provider or "").lower()
    wants_ai = bool(gemini_key or api_key) or ai_provider in ("ollama", "openrouter")
    if wants_ai and is_prose and has_translatable_content(block, 15):
        try:
            if ai_provider in ("ollama", "openrouter"):
                ai_tr = translate_paragraph_ai(
                    block,
                    provider=ai_provider,
                    api_key=api_key or gemini_key,
                    model=gemini_model,
                    base_url=base_url,
                    sl=sl,
                    tl=tl,
                )
            else:
                ai_tr = translate_paragraph_gemini(block, api_key=api_key or gemini_key, model=gemini_model, sl=sl, tl=tl)
            if ai_tr and ai_tr.strip():
                if is_ai_output_structurally_safe(block, ai_tr):
                    ai_tr = cleanup_bold_italics(ai_tr)
                    return to_bengali_digits_safe(ai_tr)
                else:
                    print("AI output dropped structure (refs/templates/links), falling back to safe MT pipeline.")
        except Exception as exc:
            print(f"AI paragraph translation failed, falling back to MT: {exc}")

    placeholders = []

    def make_ph(val: str) -> str:
        idx = len(placeholders)
        placeholders.append(val)
        return f" ZWPHL{idx}Z "

    s = block

    # নথি-স্তরের রেফ প্লেসহোল্ডার সুরক্ষিত করা
    s = re.sub(r"__DOC_REF_PLACEHOLDER_\d+__", lambda m: make_ph(m.group(0)), s)

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
    s = _mask_file_links(s, make_ph)

    # ৩. নেস্টেড টেমপ্লেট {{...}} মাস্ক করা (বাইরের স্তর থেকে)
    # প্রথমে ৩-স্তর পর্যন্ত টেমপ্লেট মাস্ক
    for _ in range(3):
        s = re.sub(r"\{\{[^{}]+\}\}", lambda m: make_ph(m.group(0)), s)

    # ৪. এক্সটার্নাল লিঙ্ক [http...] মাস্ক করা
    s = re.sub(r"\[https?://[^\s\]]+(?:\s+[^\]]+)?\]", lambda m: make_ph(m.group(0)), s)

    # ৫. <br/> ও <br> লাইনব্রেক ট্যাগ মাস্ক করা (যাতে গুগল অনুবাদ এটিকে নিউলাইনে ভেঙে না ফেলে)
    s = re.sub(r"<\s*br\s*/?\s*>", lambda m: make_ph(m.group(0)), s, flags=re.IGNORECASE)

    # ৬. উইকিলিংক [[Link|Text]] বা [[Link]] অনুবাদ ও মাস্ক করা
    # গুগল অনুবাদ ব্র্যাকেটের ভেতরের পাইপ '|' দেখে বাক্য কাটাকাটি করে ফেলে
    # (যেমন '[[ভূগোল'-এ পুরো বাক্য ট্রাঙ্কেট হওয়া রোধ করা)।
    def _wl_repl(m):
        target = m.group(1).strip()
        disp = m.group(2).strip() if m.group(2) else None

        if re.match(r"^(?:Category|বিষয়শ্রেণী|File|Image|চিত্র|ফাইল):", target, re.IGNORECASE):
            return m.group(0)

        # ইন্টারউইকি লিংকের লক্ষ্য (s:, wikt:, commons:, d:, ইত্যাদি) অক্ষত রাখা
        if re.match(r"^(?:s|wikisource|wikt|wiktionary|commons|wikidata|d|q|b|n|v|voy|m|meta):", target, re.IGNORECASE):
            if disp is not None:
                tr_disp = disp
                if has_translatable_content(disp, 2):
                    tr_disp = _translate_raw_chunk(disp, sl=sl, tl=tl).strip()
                return make_ph(f"[[{target}|{tr_disp}]]")
            return m.group(0)

        base_target, sep, anchor = target.partition("#")
        tr_base = base_target
        if has_translatable_content(base_target, 2):
            tr_base = _translate_raw_chunk(base_target, sl=sl, tl=tl).strip()

        tr_anchor = anchor
        if anchor and has_translatable_content(anchor, 2):
            tr_anchor = _translate_raw_chunk(anchor, sl=sl, tl=tl).strip()

        rebuilt_target = tr_base + (f"#{tr_anchor}" if tr_anchor else "")

        if disp is not None:
            tr_disp = disp
            if has_translatable_content(disp, 2):
                tr_disp = _translate_raw_chunk(disp, sl=sl, tl=tl).strip()
            if rebuilt_target == tr_disp:
                rebuilt = f"[[{rebuilt_target}]]"
            else:
                rebuilt = f"[[{rebuilt_target}|{tr_disp}]]"
        else:
            rebuilt = f"[[{rebuilt_target}]]"

        return make_ph(rebuilt)

    s = re.sub(r"\[\[([^\|\]\n]+)(?:\|([^\]\n]+))?\]\]", _wl_repl, s)

    # অনুবাদ কল করা (যদি অনুবাদের মতো শব্দ থাকে)
    if has_translatable_content(s, 2):
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

    # প্লেসহোল্ডারগুলো উল্টো ক্রমে পুনরুদ্ধার করা হয়
    for i in range(len(placeholders) - 1, -1, -1):
        ph = placeholders[i]
        # <br> ও <ref> ট্যাগে অতিরিক্ত স্পেস পরিহার করা
        if ph.lower().startswith(("<br", "<ref")):
            translated = re.sub(rf"[^\S\r\n]*ZWPHL{i}Z[^\S\r\n]*", ph, translated)
        else:
            translated = re.sub(rf"[^\S\r\n]*ZWPHL{i}Z[^\S\r\n]*", f" {ph} ", translated)

    translated = re.sub(r"  +", " ", translated)
    translated = re.sub(r"\s+([,।\.\?!])", r"\1", translated)
    translated = cleanup_bold_italics(translated)

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
_MEDIA_EXT_RE = re.compile(r"\.(?:png|jpe?g|gif|svg|webp|tiff?|ogg|oga|ogv|pdf|djvu|mp3|mp4|webm)\b", re.IGNORECASE)


def _translate_table_cell(cell: str, sl: str = "en", tl: str = "bn") -> str:
    """টেবিল সেলের ভেতরের সিএসএস/অ্যাট্রিবিউট আলাদা রেখে বিষয়বস্তু অনুবাদ করে।"""
    attr_match = re.match(
        r"^(\s*(?:class|style|rowspan|colspan|scope|align|valign|width|height|bgcolor)\s*=[^|]*\|\s*)(.*)$",
        cell,
        re.IGNORECASE | re.DOTALL
    )
    if attr_match:
        attr = attr_match.group(1)
        content = attr_match.group(2)
        return attr + translate_wikitext_block(content, sl=sl, tl=tl)
    return translate_wikitext_block(cell, sl=sl, tl=tl)


def _translate_table_line(line: str, sl: str = "en", tl: str = "bn") -> str:
    """টেবিল লাইনের (হেডার, সেল বা ধারাবাহিক লাইন) প্রতিটি ঘর অনুবাদ করে।"""
    stripped = line.strip()
    if stripped.startswith("!"):
        cells = line[1:].split("!!")
        tr_cells = [_translate_table_cell(c, sl=sl, tl=tl) for c in cells]
        return "!" + "!!".join(tr_cells)
    elif stripped.startswith("|"):
        cells = line[1:].split("||")
        tr_cells = [_translate_table_cell(c, sl=sl, tl=tl) for c in cells]
        return "|" + "||".join(tr_cells)
    else:
        # টেবিল সেলের ধারাবাহিক লাইন (যেমন [[Arno de Jong]] <br/>)
        return translate_wikitext_block(line, sl=sl, tl=tl)


def translate_wikitext_full(
    wikitext: str,
    sl: str = "en",
    tl: str = "bn",
    gemini_key: str | None = None,
    gemini_model: str = DEFAULT_GEMINI_MODEL,
    title: str = "",
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """
    সম্পূর্ণ উইকিটেক্সট অনুবাদ ও পাইপলাইন প্রসেসিং।
    """
    if not wikitext or not wikitext.strip():
        return ""

    from .template_translator import is_template_wikitext, translate_template_wikitext

    # টেমপ্লেট উইকিটেক্সট (Template: নামস্থান, #switch, {{{1}}}, <includeonly> ইত্যাদি)
    # সাধারণ অনুবাদের বদলে বিশেষায়িত সুরক্ষিত টেমপ্লেট ইঞ্জিনের মাধ্যমে প্রক্রিয়াজাত হবে
    if is_template_wikitext(wikitext, title=title):
        from .pipeline import normalize_nukta
        return normalize_nukta(
            translate_template_wikitext(
                wikitext,
                sl=sl,
                tl=tl,
                gemini_key=gemini_key,
                gemini_model=gemini_model,
                provider=provider,
                api_key=api_key,
                base_url=base_url,
            )
        )

    # ফাইল ও ছবির লিঙ্ক সুরক্ষিত রাখা (ক্যাপশন অনুবাদ ও ফাইলের নাম শতভাগ অক্ষত)
    masked_wikitext, file_placeholders = _extract_and_translate_file_links(wikitext, sl=sl, tl=tl)

    # বহু-লাইনের ও সাধারণ <ref> ট্যাগ লাইনে ভাগ করার আগেই পুরো নথিতে সুরক্ষিত করা
    ref_placeholders = {}
    def _mask_doc_ref(match):
        key = f"__DOC_REF_PLACEHOLDER_{len(ref_placeholders)}__"
        ref_placeholders[key] = match.group(0)
        return key

    masked_wikitext = re.sub(r"<ref\b[^>]*?/\s*>", _mask_doc_ref, masked_wikitext)
    masked_wikitext = re.sub(r"<ref\b[^>]*?(?<!/)>[\s\S]*?<\/ref>", _mask_doc_ref, masked_wikitext)
    masked_wikitext = re.sub(r"<!--[\s\S]*?-->", _mask_doc_ref, masked_wikitext)

    lines = masked_wikitext.splitlines()
    translated_lines = []

    in_table = False
    in_template = False
    in_gallery = False

    table_cont_buffer = []

    def _flush_table_continuation():
        nonlocal table_cont_buffer
        if not table_cont_buffer:
            return
        chunk = list(table_cont_buffer)
        table_cont_buffer.clear()

        batch_size = 25
        for b_start in range(0, len(chunk), batch_size):
            sub = chunk[b_start : b_start + batch_size]
            if len(sub) == 1:
                translated_lines.append(translate_wikitext_block(sub[0], sl=sl, tl=tl))
                continue
            sep = "\n@@SEP@@\n"
            raw = _translate_clients5(sep.join(sub), sl=sl, tl=tl)
            if not raw:
                raw = _translate_gtx(sep.join(sub), sl=sl, tl=tl)
            parts = re.split(r"\s*@@SEP@@\s*", raw) if raw else []
            if len(parts) == len(sub):
                for p in parts:
                    translated_lines.append(to_bengali_digits_safe(p.strip()))
            else:
                for s in sub:
                    translated_lines.append(translate_wikitext_block(s, sl=sl, tl=tl))

    for line in lines:
        stripped = line.strip()

        # খালি লাইন সরাসরি রাখা
        if not stripped:
            translated_lines.append("")
            continue

        # ফাইল লিঙ্কের প্লেসহোল্ডার সরাসরি রাখা
        if stripped.startswith("__FILE_LINK_PLACEHOLDER_") and stripped.endswith("__"):
            translated_lines.append(line)
            continue

        # ডকুমেন্ট রেফ প্লেসহোল্ডার সরাসরি রাখা
        if stripped.startswith("__DOC_REF_PLACEHOLDER_") and stripped.endswith("__"):
            translated_lines.append(line)
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
            if _MEDIA_EXT_RE.search(stripped) or stripped.lower().startswith(("file:", "image:", "চিত্র:", "ফাইল:")):
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

        # ইনফোবক্স শুরু লাইন
        infobox_header_match = re.match(
            r"^\{\{\s*(?:([Ii]nfobox)|(তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স|তথ্যছক))\b(?:\s+([a-zA-Z0-9_\u0980-\u09FF ]+?))?(.*)$",
            stripped,
            re.IGNORECASE
        )
        if infobox_header_match:
            is_english = bool(infobox_header_match.group(1))
            raw_type = (infobox_header_match.group(3) or "").strip()
            rest = infobox_header_match.group(4) or ""
            bn_type = INFOBOX_TYPE_MAP.get(raw_type.lower())
            if bn_type:
                translated_lines.append(f"{{{{তথ্যছক {bn_type}{rest}".rstrip())
            elif is_english:
                # বাংলা নাম যাচাই না হলে মূল ইংরেজি ইনফোবক্স নাম অক্ষত রাখা
                translated_lines.append(line)
            else:
                if raw_type:
                    translated_lines.append(f"{{{{তথ্যছক {raw_type}{rest}".rstrip())
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

            # ফাইলনাম, URL, মিডিয়া এক্সটেনশন বা হ্যাঁ/না-ধরনের মান অনুবাদ করা যাবে না
            value_clean = param_val.strip()
            if (_FILE_VALUE_RE.match(value_clean) or _URL_VALUE_RE.match(value_clean)
                    or _MEDIA_EXT_RE.search(value_clean)
                    or value_clean.lower() in _BOOLEAN_VALUES):
                translated_lines.append(line)
                continue

            # প্যারাম মান যদি সাধারণ বাক্য হয় তবে অনুবাদ করা
            if has_translatable_content(param_val, 2) and not re.match(r"^\s*\{\{", param_val):
                tr_val = translate_wikitext_block(param_val, sl=sl, tl=tl)
                # প্যারাম মানের ভেতরে অতিরিক্ত নিউলাইন ঢুকে যাতে লাইন না ভাঙে
                tr_val = tr_val.replace("\r\n", " ").replace("\n", " ")
                translated_lines.append(f"{param_key}= {tr_val}")
            else:
                translated_lines.append(line)
            continue

        # টেবিলের সারি
        if stripped.startswith("{|"):
            _flush_table_continuation()
            in_table = True
            # {{MedalistTable|type=Event}} ইত্যাদি হেডার টেমপ্লেটে প্যারামিটার অনুবাদ
            tr_line = re.sub(r"\btype\s*=\s*Event\b", "type=ইভেন্ট", line, flags=re.IGNORECASE)
            translated_lines.append(tr_line)
            continue
        elif stripped.startswith("|}"):
            _flush_table_continuation()
            in_table = False
            translated_lines.append(line)
            continue

        # টেবিল সেলের ভেতরের টেক্সট
        if in_table:
            if stripped.startswith("|-") or stripped.startswith("|+"):
                _flush_table_continuation()
                translated_lines.append(line)
            elif stripped.startswith("!") or stripped.startswith("|"):
                _flush_table_continuation()
                translated_lines.append(_translate_table_line(line, sl=sl, tl=tl))
            else:
                # সেলের ভেতরের ধারাবাহিক লাইন ব্যাচে দ্রুত অনুবাদের জন্য জমা রাখা
                table_cont_buffer.append(line)
            continue

        # সাধারণ অনুচ্ছেদ / বুলেট পয়েন্ট
        _flush_table_continuation()
        translated_lines.append(translate_wikitext_block(line, sl=sl, tl=tl, gemini_key=gemini_key, gemini_model=gemini_model, provider=provider, api_key=api_key, base_url=base_url))

    _flush_table_continuation()
    translated_wikitext = "\n".join(translated_lines)

    # প্লেসহোল্ডার পুনঃস্থাপন (ইংরেজি ও বাংলা অঙ্ক উভয় রূপেই মেলা)
    def _restore_doc_ref(match: re.Match) -> str:
        raw_num = match.group(1)
        ascii_num = raw_num.translate(BN_TO_ASCII_DIGITS)
        key = f"__DOC_REF_PLACEHOLDER_{ascii_num}__"
        return ref_placeholders.get(key, match.group(0))

    translated_wikitext = re.sub(r"__DOC_REF_PLACEHOLDER_([০-৯0-9]+)__", _restore_doc_ref, translated_wikitext)

    def _restore_file_link(match: re.Match) -> str:
        raw_num = match.group(1)
        ascii_num = raw_num.translate(BN_TO_ASCII_DIGITS)
        key = f"__FILE_LINK_PLACEHOLDER_{ascii_num}__"
        return file_placeholders.get(key, match.group(0))

    translated_wikitext = re.sub(r"__FILE_LINK_PLACEHOLDER_([০-৯0-9]+)__", _restore_file_link, translated_wikitext)

    for ph_key, rebuilt in file_placeholders.items():
        translated_wikitext = translated_wikitext.replace(ph_key, rebuilt)
    for ph_key, orig_ref in ref_placeholders.items():
        translated_wikitext = translated_wikitext.replace(ph_key, orig_ref)

    translated_wikitext = cleanup_bold_italics(translated_wikitext)

    # উইকিলিংকে অবশিষ্ট কোনো রোমান নাম থাকলে ফোনেটিক লিপ্যন্তর (Rule #9: কোনো রোমান হরফ সরাসরি প্রদর্শিত রাখা যাবে না)
    def _clean_article_links(m: re.Match) -> str:
        target = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else target
        if target.lower().startswith(("category:", "বিষয়শ্রেণী:", "file:", "চিত্র:", "image:", "ফাইল:")):
            return m.group(0)
        if re.search(r"[a-zA-Z]{2,}", label):
            try:
                import sys, os
                epath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ইংরেজি-বাংলা অনুবাদ")
                if epath not in sys.path:
                    sys.path.insert(0, epath)
                from transliterate_engine import transliterate_title_phrase
                clean_label = re.sub(r"[a-zA-Z]+", lambda wm: transliterate_title_phrase(wm.group(0)), label)
                return f"[[{target}|{clean_label}]]"
            except Exception:
                pass
        return m.group(0)

    translated_wikitext = re.sub(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", _clean_article_links, translated_wikitext)

    # সবশেষে আমাদের নিয়ম প্রয়োগ ও তথ্যসূত্র অটো-হিলার (common/cx_postprocess pipeline)
    result = fix_text(translated_wikitext, source_text=wikitext)
    return result.get("fixed", translated_wikitext)

# ===========================================================================
# বহু-প্রোভাইডার AI অনুবাদ সহায়ক (Ollama + OpenRouter + Gemini)
# ===========================================================================

AI_SYSTEM_PROMPT = (
    "তুমি বাংলা উইকিপিডিয়ার একজন অভিজ্ঞ সম্পাদক ও অনুবাদক। "
    "প্রদত্ত উইকিটেক্সট অনুচ্ছেদটি অত্যন্ত সাবলীল, প্রাঞ্জল ও প্রমিত বাংলায় অনুবাদ করো।"
)
TRANSLATION_SYSTEM_PROMPT = AI_SYSTEM_PROMPT
SYSTEM_PROMPT = AI_SYSTEM_PROMPT


def _extract_ai_text(data):
    if isinstance(data, str):
        return data.strip()
    if not isinstance(data, dict):
        return ""
    choices = data.get("choices")
    if isinstance(choices, list) and choices:
        c = choices[0]
        if isinstance(c, dict):
            msg = c.get("message")
            if isinstance(msg, dict) and msg.get("content") is not None:
                return str(msg["content"]).strip()
            if c.get("text") is not None:
                return str(c["text"]).strip()
            if c.get("content") is not None:
                return str(c["content"]).strip()
    msg = data.get("message")
    if isinstance(msg, dict) and msg.get("content") is not None:
        return str(msg["content"]).strip()
    if isinstance(data.get("response"), str):
        return data["response"].strip()
    cands = data.get("candidates")
    if isinstance(cands, list) and cands:
        cand = cands[0]
        if isinstance(cand, dict):
            content = cand.get("content")
            if isinstance(content, dict):
                parts = content.get("parts")
                if isinstance(parts, list) and parts and isinstance(parts[0], dict) and "text" in parts[0]:
                    return str(parts[0]["text"]).strip()
            if cand.get("text") is not None:
                return str(cand["text"]).strip()
    for key in ("text", "content", "output", "result", "translation", "translated", "answer"):
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _post_json(url, payload, headers=None, timeout=30):
    import urllib.request
    data = json.dumps(payload).encode("utf-8")
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception:
        try:
            return json.loads(raw.decode("utf-8-sig"))
        except Exception:
            return {}


def translate_paragraph_ollama(
    text,
    api_key=None,
    model=None,
    sl="en",
    tl="bn",
    base_url=None,
    **kwargs,
):
    if not text or not text.strip():
        return text
    if not has_translatable_content(text, 2):
        return text

    active_model = model or get_ollama_model(DEFAULT_OLLAMA_MODEL)
    base = (base_url or get_ollama_base_url(DEFAULT_OLLAMA_BASE_URL)).rstrip("/")
    if base.endswith("/v1"):
        url = base + "/chat/completions"
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": "Translate the following wikitext paragraph:\n\n" + text},
            ],
            "temperature": 0.2,
        }
    else:
        # Ollama Cloud-এর ডকুমেন্টে বেস URL কখনও https://ollama.com/api হিসেবেও
        # দেওয়া হয়; সেক্ষেত্রে যেন /api/api/chat হয়ে না যায়।
        if base.endswith("/api"):
            url = base + "/chat"
        else:
            url = base + "/api/chat"
        payload = {
            "model": active_model,
            "messages": [
                {"role": "system", "content": AI_SYSTEM_PROMPT},
                {"role": "user", "content": "Translate the following wikitext paragraph:\n\n" + text},
            ],
            "stream": False,
            "options": {"temperature": 0.2},
        }

    headers = {}
    key = api_key if api_key is not None else get_ollama_key()
    if key:
        headers["Authorization"] = "Bearer " + str(key).strip()

    try:
        res_json = _post_json(url, payload, headers=headers, timeout=180)
    except Exception as e:
        print("Ollama API request failed: " + str(e))
        return ""
    out = _extract_ai_text(res_json)
    if out:
        out = re.sub(r"^```(?:wikitext|wiki)?\s*", "", out, flags=re.IGNORECASE)
        out = re.sub(r"\s*```$", "", out)
    return out.strip() if out else ""


def translate_paragraph_openrouter(
    text,
    api_key=None,
    model=None,
    sl="en",
    tl="bn",
    base_url=None,
    **kwargs,
):
    if not text or not text.strip():
        return text
    if not has_translatable_content(text, 2):
        return text

    active_model = model or get_openrouter_model(DEFAULT_OPENROUTER_MODEL)
    key = api_key if api_key is not None else get_openrouter_key()
    if not key:
        return text
    base = (base_url or get_openrouter_base_url(DEFAULT_OPENROUTER_BASE_URL)).rstrip("/")
    if not base.endswith("/v1"):
        base = base + "/v1"
    url = base.rstrip("/") + "/chat/completions"

    headers = {"Authorization": "Bearer " + str(key).strip()}
    headers["HTTP-Referer"] = "https://github.com/joysriramsarkar/wikipedia-bangla-translation-tool"
    headers["X-Title"] = "Wikipedia Bangla Translation Tool"

    payload = {
        "model": active_model,
        "messages": [
            {"role": "system", "content": AI_SYSTEM_PROMPT},
            {"role": "user", "content": "Translate the following wikitext paragraph:\n\n" + text},
        ],
        "temperature": 0.2,
        "max_tokens": 8192,
    }

    try:
        res_json = _post_json(url, payload, headers=headers, timeout=60)
    except Exception as e:
        print("OpenRouter API request failed: " + str(e))
        return ""
    out = _extract_ai_text(res_json)
    if out:
        out = re.sub(r"^```(?:wikitext|wiki)?\s*", "", out, flags=re.IGNORECASE)
        out = re.sub(r"\s*```$", "", out)
    return out.strip() if out else ""


def translate_paragraph_ai(
    text,
    provider=None,
    api_key=None,
    model=None,
    base_url=None,
    sl="en",
    tl="bn",
    **kwargs,
):
    prov = (provider if provider is not None else get_ai_provider("gemini"))
    prov = str(prov).lower()
    if prov in ("ollama",):
        return translate_paragraph_ollama(text, api_key=api_key, model=model, sl=sl, tl=tl, base_url=base_url, **kwargs)
    if prov in ("openrouter", "open-router", "open_router"):
        return translate_paragraph_openrouter(text, api_key=api_key, model=model, sl=sl, tl=tl, base_url=base_url, **kwargs)
    gkey = api_key if api_key is not None else get_gemini_key()
    gmodel = model if model is not None else get_gemini_model(DEFAULT_GEMINI_MODEL)
    return translate_paragraph_gemini(text, api_key=gkey, model=gmodel, sl=sl, tl=tl, **kwargs)


translate_paragraph = translate_paragraph_ai
ai_translate_paragraph = translate_paragraph_ai
translate_with_ai = translate_paragraph_ai
translate_paragraph_with_provider = translate_paragraph_ai
translate_paragraph_llm = translate_paragraph_ai
translate_ai_paragraph = translate_paragraph_ai

ollama_translate_paragraph = translate_paragraph_ollama
translate_ollama = translate_paragraph_ollama

openrouter_translate_paragraph = translate_paragraph_openrouter
translate_openrouter = translate_paragraph_openrouter


# অতিরিক্ত alias
translate_paragraph_with_ollama = translate_paragraph_ollama
translate_with_ollama = translate_paragraph_ollama
ollama_translate = translate_paragraph_ollama
translate_paragraph_with_openrouter = translate_paragraph_openrouter
translate_with_openrouter = translate_paragraph_openrouter
openrouter_translate = translate_paragraph_openrouter
translate_paragraph_with_gemini = translate_paragraph_gemini
translate_with_gemini = translate_paragraph_gemini
gemini_translate_paragraph = translate_paragraph_gemini
