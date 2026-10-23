# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া টেমপ্লেট অনুবাদক (Wikipedia Template Translator)

উইকিপিডিয়ার টেমপ্লেট পাতা (Template: / টেমপ্লেট:) সাধারণ নিবন্ধের মতো নয়;
এতে মিডিয়াউইকির নিজস্ব প্রোগ্রামিং কোড, পার্সার ফাংশন ও ভ্যারিয়েবল থাকে।

এই মডিউলটি:
১. টেমপ্লেট শনাক্ত করে (Template: নামস্থান, #switch, {{{1}}}, <includeonly>, Navbox ইত্যাদি)।
২. মিডিয়াউইকি পার্সার ফাংশন (#switch:, #if:, #ifeq:, #expr: ইত্যাদি) ১০০% অক্ষত রাখে।
   (কখনোই #সুইচ: বা #যদি: হবে না)।
৩. টেমপ্লেট আর্গুমেন্ট ভ্যারিয়েবল ({{{1}}}, {{{2}}}, {{{state|autocollapse}}} ইত্যাদি)
   ১০০% অক্ষত রাখে (কখনোই {টেমপ্লেট:১} হবে না)।
৪. সুইচ কেসের কী (keys) যেমন `AFCBourn`, `AFCBourn2`, `Arsenal` অক্ষত রাখে, যাতে
   অন্য নিবন্ধ বা টেমপ্লেট থেকে ইনপুট দিলে ডেটা যথাযথভাবে ম্যাচ করে।
৫. সুইচ ভ্যালু ও নেভবক্সের উইকিলিংক, মরসুমের সাল ও লিগের নাম প্রমিত বাংলায় রূপান্তর করে:
   `[[2025–26 Premier League|2025–26]]` -> `[[২০২৫-২৬ প্রিমিয়ার লিগ|২০২৫-২৬]]`
৬. অবস্থান, পদমর্যাদা ও প্লে-অফ/উত্তরণ টীকা প্রমিত বাংলায় করে:
   `6th of 20` -> `২০-এর মধ্যে ৬ষ্ঠ`
   `(promoted via play-offs)` -> `(প্লে-অফের মাধ্যমে উন্নীত)`
   `(relegated)` -> `(অবনমিত)`
   `(promoted)` -> `(উন্নীত)`
৭. নেভবক্স (Navbox), সাইডবার ও সাধারণ টেমপ্লেটের ক্ষেত্রে:
   - টেকনিক্যাল প্যারামিটার ও সিএসএস কোড (`name`, `titlestyle`, `groupstyle`, `basestyle`, `bodyclass = hlist`)
     ১০০% অক্ষত রাখে এবং কোনোভাবেই নষ্ট করে না।
   - শিরোনাম (`title`), গ্রুপ নাম (`group1`), লেবেল (`label1`) ও তালিকার ভেতরের লিংক ও বিবরণী
     (`* [[...]]`) প্রমিত ও প্রাঞ্জল বাংলায় রূপান্তর করে।
   - সমস্ত দৃশ্যমান সাল ও সংখ্যা প্রমিত বাংলা সংখ্যায় (০-৯) রূপান্তর করে।
"""
import re
from common.bengali_utils import to_bengali_digits, to_bengali_digits_safe
from cx_postprocess.pipeline import normalize_nukta


_PARSER_FUNCTIONS = [
    "#switch", "#if", "#ifeq", "#ifexpr", "#iferror", "#expr",
    "#time", "#tag", "#invoke", "lc", "uc", "padleft", "formatnum",
    "anchorencode", "defaultsort"
]

ORDINAL_MAP = {
    '1': '১ম', '2': '২য়', '3': '৩য়', '4': '৪র্থ', '5': '৫ম',
    '6': '৬ষ্ঠ', '7': '৭ম', '8': '৮ম', '9': '৯ম', '10': '১০ম',
    '11': '১১তম', '12': '১২তম', '13': '১৩তম', '14': '১৪তম', '15': '১৫তম',
    '16': '১৬তম', '17': '১৭তম', '18': '১৮তম', '19': '১৯তম', '20': '২০তম',
    '21': '২১তম', '22': '২২তম', '23': '২৩তম', '24': '২৪তম', '25': '২৫তম',
    '26': '২৬তম', '27': '২৭তম', '28': '২৮তম', '29': '২৯তম', '30': '৩০তম'
}

COMMON_LEAGUE_MAP = {
    "Premier League": "প্রিমিয়ার লিগ",
    "EFL Championship": "ইএফএল চ্যাম্পিয়নশিপ",
    "EFL League One": "ইএফএল লিগ ওয়ান",
    "EFL League Two": "ইএফএল লিগ টু",
    "National League North": "ন্যাশনাল লিগ নর্থ",
    "National League South": "ন্যাশনাল লিগ সাউথ",
    "National League": "ন্যাশনাল লিগ",
    "FA Cup": "এফএ কাপ",
    "EFL Cup": "ইএফএল কাপ",
    "Champions League": "চ্যাম্পিয়নস লিগ",
    "Europa League": "ইউরোপা লিগ",
    "Bundesliga": "বুন্দেসলিগা",
    "La Liga": "লা লিগা",
    "Serie A": "সেরিয়ে আ",
    "Ligue 1": "লিগ ১",
    "Major League Soccer": "মেজর লিগ সকার",
    "Indian Super League": "ইন্ডিয়ান সুপার লিগ",
    "I-League": "আই-লিগ",
    "Bangladesh Premier League": "বাংলাদেশ প্রিমিয়ার লিগ",
}

NAVBOX_LABEL_MAP = {
    "Clubs": "ক্লাবসমূহ",
    "Seasons": "মৌসুমসমূহ",
    "Teams": "দলসমূহ",
    "Competitions": "প্রতিযোগিতাসমূহ",
    "Managers": "ম্যানেজারবৃন্দ",
    "Players": "খেলোয়াড়বৃন্দ",
    "Former clubs": "সাবেক ক্লাব",
    "Current clubs": "বর্তমান ক্লাব",
    "Current season": "বর্তমান মৌসুম",
    "History": "ইতিহাস",
    "Statistics": "পরিসংখ্যান",
    "Honours": "সম্মাননা",
    "Awards": "পুরস্কারসমূহ",
    "Stadiums": "স্টেডিয়ামসমূহ",
}

CITY_AND_ENTITY_MAP = {
    # আন্তর্জাতিক ক্রীড়া সংস্থা ও সংক্ষিপ্ত রূপ
    "CPISRA": "সিপিসরা",
    "IFCPF": "আইএফসিপিএফ",
    "FESPIC": "ফেসপিক",
    "ASEAN": "আসিয়ান",
    "FIFA": "ফিফা",
    "UEFA": "উয়েফা",
    "CONCACAF": "কনকাকাফ",
    "CONMEBOL": "কনমেবল",
    "AFC": "এএফসি",
    "CAF": "ক্যাফ",
    "OFC": "ওএফসি",
    "IOC": "আইওসি",
    "IPC": "আইপিসি",

    # আন্তর্জাতিক প্রতিযোগিতা ও পর্ব
    "Parapan American Games": "পারাপান আমেরিকান গেমস",
    "Parapan American": "পারাপান আমেরিকান",
    "Asian Para Games": "এশিয়ান প্যারা গেমস",
    "Americas Championships": "আমেরিকাস চ্যাম্পিয়নশিপ",
    "Americas Championship": "আমেরিকাস চ্যাম্পিয়নশিপ",
    "Asia-Oceania Championships": "এশিয়া-ওশেনিয়া চ্যাম্পিয়নশিপ",
    "Asia-Oceania Championship": "এশিয়া-ওশেনিয়া চ্যাম্পিয়নশিপ",
    "European Championships": "ইউরোপীয় চ্যাম্পিয়নশিপ",
    "European Championship": "ইউরোপীয় চ্যাম্পিয়নশিপ",
    "World Championships": "বিশ্ব চ্যাম্পিয়নশিপ",
    "World Championship": "বিশ্ব চ্যাম্পিয়নশিপ",
    "Intercontinental Cup": "আন্তঃমহাদেশীয় কাপ",
    "International Cup": "আন্তর্জাতিক কাপ",
    "International Cups": "আন্তর্জাতিক কাপ",
    "American Cup": "আমেরিকান কাপ",
    "World Cup": "বিশ্বকাপ",
    "World Games": "ওয়ার্ল্ড গেমস",
    "qualification": "যোগ্যতা",
    "Qualification": "যোগ্যতা",
    "Summer Paralympics": "গ্রীষ্মকালীন প্যারালিম্পিক",
    "Winter Paralympics": "শীতকালীন প্যারালিম্পিক",

    # বিশ্বের স্বাগতিক শহর ও স্থানসমূহ (যা মেশিন অনুবাদে সরাসরি ইংরেজিতে থেকে যায়)
    "Sangolquí": "সাঙ্গোলকি",
    "Sangolqui": "সাঙ্গোলকি",
    "Brasschaat": "ব্রাসখাত",
    "Zeist": "জেইস্ট",
    "Oristano": "ওরিস্তানো",
    "Naypyidaw": "নেপিডো",
    "Naypyitaw": "নেপিডো",
    "Nay Pyi Taw": "নেপিডো",
    "Arnheim": "আর্নহেম",
    "Arnhem": "আর্নহেম",
    "Sant Cugat del Vallès": "সান্ত কুগাত দেল ভায়েস",
    "Sant Cugat": "সান্ত কুগাত দেল ভায়েস",
    "San Luis": "সান লুইস",
    "Burton": "বার্টন",
    "Salou": "সালো",
    "Seville": "সেভিল",
    "Sevilla": "সেভিল",
    "Maia": "মাইয়া",
    "Surakarta": "সুরাকার্তা",
    "Nakhon Ratchasima": "নাখোন রাতচাসিমা",
    "Phnom Penh": "ফনম পেন",
    "Kish Island": "কিশ দ্বীপ",
    "Kish": "কিশ",
    "Kyiv": "কিয়েভ",
    "Kiev": "কিয়েভ",
    "Glasgow": "গ্লাসগো",
    "Dublin": "ডাবলিন",
    "Nottingham": "নটিংহাম",
    "New London": "নিউ লন্ডন",
    "Assen": "আসেন",
    "Greve": "গ্রেভ",
    "Santiago": "সান্তিয়াগো",
    "Toronto": "টরন্টো",
    "Lima": "লিমা",
    "Busan": "বুসান",
    "Kuala Lumpur": "কুয়ালালামপুর",
    "Guangzhou": "গুয়াংজু",
    "Incheon": "ইঞ্চিওন",
    "Melbourne": "মেলবোর্ন",
    "Singapore": "সিঙ্গাপুর",
    "Athens": "এথেন্স",
    "Beijing": "বেইজিং",
    "London": "লন্ডন",
    "Atlanta": "আটলান্টা",
    "Sydney": "সিডনি",
    "Barcelona": "বার্সেলোনা",
    "Seoul": "সিউল",
    "New York": "নিউ ইয়র্ক",
    "Edinburgh": "এডিনবরা",
}

TECHNICAL_PARAMS = {
    "name", "navbar", "border", "state", "tracking",
    "bodyclass", "listclass", "groupclass", "aboveclass", "belowclass", "titleclass", "class",
    "style", "bodystyle", "titlestyle", "groupstyle", "basestyle", "abovestyle", "belowstyle",
    "evenstyle", "oddstyle", "imagestyle", "imageleftstyle", "imagerightstyle",
    "image", "imageleft", "imageright", "image_flag", "image_coat",
    "width", "groupwidth", "align", "cellpadding", "cellspacing", "nowrap"
}


def is_technical_param(param_name: str) -> bool:
    """যাচাই করে প্যারামিটারটি সিএসএস বা কারিগরি কিনা যা বাংলায় অনুবাদ করা নিষিদ্ধ।"""
    p = param_name.strip().lower()
    if p in TECHNICAL_PARAMS or p.endswith("style") or p.endswith("class"):
        return True
    if re.match(r"^(?:link|color|image|icon|url)\d*$", p):
        return True
    return False


def is_template_wikitext(text: str, title: str = "") -> bool:
    """উইকিটেক্সট বা শিরোনাম থেকে শনাক্ত করে এটি টেমপ্লেট কিনা।"""
    t_clean = (title or "").strip().lower()
    if t_clean.startswith(("template:", "টেমপ্লেট:", "module:", "মডিউল:")):
        return True

    if not text:
        return False

    strong_patterns = [
        r"\{\{\s*#(?:switch|if|ifeq|expr|time)\b",
        r"\{\{\{[A-Za-z0-9_\-\u0980-\u09FF ]+(?:\|[^\}]*)?\}\}\}",
        r"^\s*\{\{\s*(?:Navbox|Sidebar|Subgroup)\b",
    ]
    for pat in strong_patterns:
        if re.search(pat, text, re.IGNORECASE | re.MULTILINE):
            return True

    return False


def _call_mt(text: str, sl: str = "en", tl: str = "bn") -> str:
    """মেশিন অনুবাদ কল (clients5 বা gtx fallback)।"""
    if not text or not text.strip():
        return text
    try:
        from .mt_translate import _translate_clients5, _translate_gtx
        res = _translate_clients5(text, sl=sl, tl=tl)
        if res and res.strip():
            return res
        res_gtx = _translate_gtx(text, sl=sl, tl=tl)
        return res_gtx if (res_gtx and res_gtx.strip()) else text
    except Exception:
        return text


def _call_gemini_template_batch(
    batch_text: str,
    sl: str = "en",
    tl: str = "bn",
    gemini_key: str | None = None,
    gemini_model: str = "gemini-3.5-flash",
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """Gemini / Ollama / OpenRouter দিয়ে টেমপ্লেটের ব্যাচ অনুবাদ।"""
    prov = (provider or "").lower()
    if not gemini_key and not api_key and prov != "ollama":
        return ""
    try:
        from .mt_translate import translate_paragraph_ai
        custom_inst = (
            "Translate each of the following Wikipedia template text items from English into standard Bengali.\n"
            "CRITICAL: Keep the exact delimiter ' ___MW_SEP___ ' between items without modifying or dropping it.\n"
            "Preserve all wiki syntax [[...]], tags, numbers, and identifiers."
        )
        res = translate_paragraph_ai(
            batch_text,
            provider=prov or "gemini",
            api_key=api_key or gemini_key,
            model=gemini_model,
            base_url=base_url,
            custom_instruction=custom_inst,
        )
        return res if (res and "___MW_SEP___" in res) else ""
    except Exception:
        return ""


def _translate_rank_phrase(match: re.Match) -> str:
    """'6th of 20' -> '২০-এর মধ্যে ৬ষ্ঠ'"""
    rank, total = match.group(1), match.group(2)
    bn_rank = ORDINAL_MAP.get(rank, to_bengali_digits(rank) + "তম")
    bn_total = to_bengali_digits(total)
    return f"{bn_total}-এর মধ্যে {bn_rank}"


def _translate_wikilink_in_template(m: re.Match) -> str:
    """টেমপ্লেটের ভেতরের উইকিলিংক [[2025–26 Premier League|2025–26]] বাংলায় করে।"""
    target = m.group(1).strip()
    label = m.group(2).strip() if m.group(2) else ""

    # Seperate anchor fragment (e.g. #Intro) — anchors must not be translated
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = "#" + anchor

    # মরসুমের সাল ও লিগ অনুবাদ
    season_match = re.match(r"^(\d{4})[–\-](\d{2,4})\s+(.*)$", target)
    if season_match:
        y1, y2, league = season_match.groups()
        bn_years = f"{to_bengali_digits(y1)}–{to_bengali_digits(y2)}"
        bn_league = COMMON_LEAGUE_MAP.get(league, league)
        target_bn = f"{bn_years} {bn_league}"
        label_bn = f"{bn_years}" if label else ""
        if label:
            label_season = re.match(r"^(\d{4})[–\-](\d{2,4})$", label)
            if label_season:
                label_bn = f"{to_bengali_digits(label_season.group(1))}–{to_bengali_digits(label_season.group(2))}"
            else:
                label_bn = to_bengali_digits(label)
            return f"[[{target_bn}{anchor}|{label_bn}]]"
        return f"[[{target_bn}{anchor}]]"

    # সাধারণ পরিচিত লিগ
    if target in COMMON_LEAGUE_MAP:
        target_bn = COMMON_LEAGUE_MAP[target]
        label_bn = COMMON_LEAGUE_MAP.get(label, label) if label else ""
        return f"[[{target_bn}{anchor}|{label_bn}]]" if label_bn and label_bn != target_bn else f"[[{target_bn}{anchor}]]"

    # শুধু সাল রূপান্তর (namespace:page links like WP:JCW/ALPHA preserved as-is)
    target_bn = to_bengali_digits_safe(target)
    label_bn = to_bengali_digits_safe(label) if label else ""
    return f"[[{target_bn}{anchor}|{label_bn}]]" if label_bn else f"[[{target_bn}{anchor}]]"


COMMON_FOOTBALL_NOTES = [
    ("(promoted via play-offs)", "(প্লে-অফের মাধ্যমে উন্নীত)"),
    ("(relegated via play-offs)", "(প্লে-অফের মাধ্যমে অবনমিত)"),
    ("(promoted)", "(উন্নীত)"),
    ("(relegated)", "(অবনমিত)"),
    ("(champions)", "(চ্যাম্পিয়ন)"),
    ("(runners-up)", "(রানার্স-আপ)"),
    ("(resigned)", "(পদত্যাগ)"),
    ("(withdrew)", "(প্রত্যাহার)"),
    ("(folded)", "(বিলুপ্ত)"),
    ("(transferred)", "(স্থানান্তরিত)"),
    ("Senior Division", "সিনিয়র বিভাগ"),
    ("Premier Division", "প্রিমিয়ার বিভাগ"),
    ("First Division", "প্রথম বিভাগ"),
    ("Second Division", "দ্বিতীয় বিভাগ"),
    ("Division One", "বিভাগ এক"),
    ("Division Two", "বিভাগ দুই"),
]


def _translate_switch_value(val: str) -> str:
    """একটি সুইচ কেসের ভ্যালু অংশ অনুবাদ করে।"""
    s = val.strip()

    # ১. সাব-টেমপ্লেট কল সুরক্ষিত করা (যেমন: {{ENGLs|PL}} অক্ষত থাকে)
    sub_tpls = {}
    def _mask_sub_tpl(m: re.Match) -> str:
        tok = f"__SUB_TPL_{len(sub_tpls)}__"
        sub_tpls[tok] = m.group(0)
        return tok

    s = re.sub(r"\{\{[^{}]*\}\}", _mask_sub_tpl, s)

    # ২. উইকিলিংক রূপান্তর
    s = re.sub(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", _translate_wikilink_in_template, s)

    # ৩. অবস্থান / র‍্যাংক রূপান্তর (যেমন: 6th of 20 -> ২০-এর মধ্যে ৬ষ্ঠ)
    s = re.sub(r"\b(\d+)(?:st|nd|rd|th)\s+of\s+(\d+)\b", _translate_rank_phrase, s)

    # ৪. টীকা রূপান্তর
    for eng_note, bn_note in COMMON_FOOTBALL_NOTES:
        s = s.replace(eng_note, bn_note)

    # ৫. দৃশ্যমান সংখ্যা বাংলায়
    s = to_bengali_digits_safe(s)

    # ৬. সুরক্ষিত সাব-টেমপ্লেট পুনঃস্থাপন
    for tok, orig in sub_tpls.items():
        s = s.replace(tok, orig)

    return s


def _split_top_level_pipes(line: str) -> list[str]:
    """একটি লাইনের টপ-লেভেল `|` ধরে ভাগ করে ([[...]] ও {{...}} অক্ষত রেখে)।"""
    parts = []
    buffer = []
    link_depth = 0
    tpl_depth = 0
    i = 0
    n = len(line)

    while i < n:
        if i < n - 1 and line[i:i+2] == "[[":
            link_depth += 1
            buffer.append("[[")
            i += 2
            continue
        if i < n - 1 and line[i:i+2] == "]]":
            link_depth = max(0, link_depth - 1)
            buffer.append("]]")
            i += 2
            continue
        if i < n - 1 and line[i:i+2] == "{{":
            tpl_depth += 1
            buffer.append("{{")
            i += 2
            continue
        if i < n - 1 and line[i:i+2] == "}}":
            tpl_depth = max(0, tpl_depth - 1)
            buffer.append("}}")
            i += 2
            continue

        if line[i] == "|" and link_depth == 0 and tpl_depth == 0:
            if buffer:
                parts.append("".join(buffer))
                buffer = []
            i += 1
            continue

        buffer.append(line[i])
        i += 1

    if buffer:
        parts.append("".join(buffer))

    return parts


def _translate_switch_template(wikitext: str, sl: str = "en", tl: str = "bn") -> str:
    """#switch: ভিত্তিক ডেটা রাউটার টেমপ্লেট অনুবাদ করে (কী অক্ষত, ভ্যালু বাংলায়)।"""
    var_placeholders = {}
    var_idx = 0

    def _mask_var(m: re.Match) -> str:
        nonlocal var_idx
        token = f"__MW_VAR_PH_{var_idx}__"
        var_idx += 1
        var_placeholders[token] = m.group(0)
        return token

    text = re.sub(r"\{\{\{[A-Za-z0-9_\-\u0980-\u09FF ]+(?:\|[^\}]*)?\}\}\}", _mask_var, wikitext)

    pfn_placeholders = {}
    pfn_idx = 0

    def _mask_pfn(m: re.Match) -> str:
        nonlocal pfn_idx
        token = f"__MW_PFN_PH_{pfn_idx}__"
        pfn_idx += 1
        pfn_placeholders[token] = m.group(0)
        return token

    text = re.sub(r"\{\{\s*#(?:" + "|".join(fn.lstrip("#") for fn in _PARSER_FUNCTIONS) + r")\s*:", _mask_pfn, text, flags=re.IGNORECASE)

    lines = text.split("\n")
    out_lines = []
    in_noinclude = False

    for line in lines:
        stripped = line.strip()

        has_cat_or_doc = ("[[category:" in line.lower() or
                          "{{documentation" in line.lower() or
                          "<noinclude>" in line.lower() or
                          "</noinclude>" in line.lower())

        if "<noinclude>" in stripped:
            in_noinclude = True

        if has_cat_or_doc or in_noinclude:
            mod_line = line
            mod_line = re.sub(r"\{\{\s*(?:[Tt]emplate\s*:\s*)?[Dd]ocumentation\s*\}\}", "{{ডকুমেন্টেশন}}", mod_line)
            mod_line = re.sub(r"\[\[\s*Category\s*:\s*([^\]]+)\]\]", r"[[বিষয়শ্রেণী:\1]]", mod_line, flags=re.IGNORECASE)
            mod_line = mod_line.replace("English football updater templates", "ইংরেজি ফুটবল আপডেটার টেমপ্লেট")
            mod_line = mod_line.replace("England football templates", "ইংল্যান্ড ফুটবল টেমপ্লেট")
            mod_line = mod_line.replace("Association football infobox updater templates", "অ্যাসোসিয়েশন ফুটবল তথ্যছক আপডেটার টেমপ্লেট")
            if "</noinclude>" in stripped:
                in_noinclude = False
            out_lines.append(mod_line)
            continue

        if "</noinclude>" in stripped:
            in_noinclude = False

        comment_match = re.search(r"<!--\s*(.*?)\s*-->", line)
        if comment_match:
            c_text = comment_match.group(1).strip()
            c_bn = COMMON_LEAGUE_MAP.get(c_text, c_text)
            line = line.replace(comment_match.group(0), f"<!--{c_bn}-->")

        if stripped == "}}" or stripped.startswith("| #default") or stripped.startswith("|#default"):
            out_lines.append(line)
            continue

        if stripped.startswith("|") and "=" in stripped:
            parts = _split_top_level_pipes(line)
            out_parts = []
            for part in parts:
                p_strip = part.strip()
                if not p_strip:
                    continue
                if "=" in part:
                    k, v = part.split("=", 1)
                    v_translated = _translate_switch_value(v)
                    out_parts.append(f"{k.strip()} = {v_translated}")
                else:
                    if p_strip in NAVBOX_LABEL_MAP:
                        out_parts.append(NAVBOX_LABEL_MAP[p_strip])
                    else:
                        out_parts.append(p_strip)
            if out_parts:
                out_lines.append("| " + " | ".join(out_parts))
            else:
                out_lines.append(line)
            continue

        out_lines.append(line)

    result = "\n".join(out_lines)
    for token, orig in var_placeholders.items():
        result = result.replace(token, orig)
    for token, orig in pfn_placeholders.items():
        result = result.replace(token, orig)

    return result


def _translate_navbox_template(
    wikitext: str,
    sl: str = "en",
    tl: str = "bn",
    gemini_key: str | None = None,
    gemini_model: str = "gemini-3.5-flash",
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """
    নেভবক্স (Navbox), সাইডবার ও সাধারণ উপস্থাপনা টেমপ্লেট অনুবাদ করে।
    - সিএসএস শৈলী ও টেকনিক্যাল প্যারামিটার ১০০% অক্ষত থাকে।
    - শিরোনাম, গ্রুপ, লেবেল ও তালিকার উইকিলিংক প্রমিত বাংলায় অনূদিত হয়।
    - দৃশ্যমান সমস্ত সাল ও সংখ্যা বাংলা ডিজিট (০-৯)-এ রূপান্তরিত হয়।
    """
    # ১. ভ্যারিয়েবল সুরক্ষিত করা ({{{state|autocollapse}}} ইত্যাদি)
    var_map = {}
    v_idx = 0
    def _mask_var(m: re.Match) -> str:
        nonlocal v_idx
        k = f"__MW_VAR_PH_{v_idx}__"
        v_idx += 1
        var_map[k] = m.group(0)
        return k
    text = re.sub(r"\{\{\{[A-Za-z0-9_\-\u0980-\u09FF ]+(?:\|[^\}]*)?\}\}\}", _mask_var, wikitext)

    # ২. মন্তব্য লাইন সুরক্ষিত করা (<!-- [[File:...]] --> ইত্যাদি)
    com_map = {}
    c_idx = 0
    def _mask_com(m: re.Match) -> str:
        nonlocal c_idx
        k = f"__MW_COM_PH_{c_idx}__"
        c_idx += 1
        com_map[k] = m.group(0)
        return k
    text = re.sub(r"<!--[\\s\\S]*?-->", _mask_com, text)

    # 2a. {{#ifexist:...|}} / {{#if:...|}} condition args must not be translated
    cond_map = {}
    cnd_idx = 0
    def _mask_cond(m: re.Match) -> str:
        nonlocal cnd_idx
        k = f"__MW_CND_PH_{cnd_idx}__"
        cnd_idx += 1
        cond_map[k] = m.group(0)
        return k
    text = re.sub(r"\{\{#(?:ifexist|if)\s*:\s*[^|}]*\|", _mask_cond, text, flags=re.IGNORECASE)

    # 2b. Page title dictionary for consistent translation
    JCW_PAGE_TITLE_MAP = {
        "Wikipedia:WikiProject Academic Journals/Journals cited by Wikipedia":
            "উইকিপিডিয়া:উইকিপ্রকল্প একাডেমিক জার্নাল/উইকিপিডিয়া উদ্ধৃত জার্নাল",
        "Journals cited by Wikipedia": "উইকিপিডিয়া দ্বারা উদ্ধৃত জার্নাল",
        "Wikipedia:WikiProject Academic Journals/Journals cited by Wikipedia/A1":
            "উইকিপিডিয়া:উইকিপ্রকল্প একাডেমিক জার্নাল/জার্নাল উদ্ধৃত উইকিপিডিয়া/A১",
        "Wikipedia:WikiProject Academic Journals/Journals cited by Wikipedia/B1":
            "উইকিপিডিয়া:উইকিপ্রকল্প একাডেমিক জার্নাল/জার্নাল উদ্ধৃত উইকিপিডিয়া/B১",
    }
    for en_title, bn_title in JCW_PAGE_TITLE_MAP.items():
        text = text.replace(en_title, bn_title)

    lines = text.splitlines()
    translatable_items = []  # (line_idx, item_type, prefix_info, content)
    out_lines = list(lines)

    for idx, line in enumerate(lines):
        # ডকুমেন্টেশন রূপান্তর
        if re.search(r"\{\{\s*(?:[Tt]emplate\s*:\s*)?(?:[Dd]ocumentation|[Nn]avbox\s+documentation)\s*\}\}", line, re.IGNORECASE):
            out_lines[idx] = re.sub(r"\{\{\s*(?:[Tt]emplate\s*:\s*)?(?:[Dd]ocumentation|[Nn]avbox\s+documentation)\s*\}\}", "{{ডকুমেন্টেশন}}", line, flags=re.IGNORECASE)
            continue

        # বিষয়শ্রেণী রূপান্তর
        cat_match = re.match(r"^(\s*\[\[\s*Category\s*:\s*)([^\]|]+)(\|.*)?(\]\]\s*)$", line, re.IGNORECASE)
        if cat_match:
            c_prefix, c_name, c_pipe, c_suffix = cat_match.groups()
            translatable_items.append((idx, "category", (c_prefix, c_pipe or "", c_suffix), c_name.strip()))
            continue

        # তালিকার বুলেট পয়েন্ট রূপান্তর (* [[...]], ** [[...]])
        b_match = re.match(r"^(\s*[\*\#]+)\s*(.*)$", line)
        if b_match:
            b_prefix, b_content = b_match.groups()
            if b_content.strip():
                translatable_items.append((idx, "bullet", b_prefix + " ", b_content.strip()))
                continue

        # টেমপ্লেট প্যারামিটার লাইন রূপান্তর (| title = ..., | group1 = ...)
        # পুরো লাইনের ভেতরের টপ-লেভেল | দিয়ে ভাগ করা হয় ([[...|...]] ও {{...}} অক্ষত রেখে)।
        param_parts = _split_top_level_pipes(line)
        for part in param_parts:
            p_strip = part.strip()
            if not p_strip:
                continue
            # If the part starts with '|', strip it (leftover from split)
            if p_strip.startswith('|'):
                p_strip = p_strip[1:].lstrip()
            p_match = re.match(r'^([a-zA-Z0-9_\-]+)\s*=\s*(.*)$', p_strip)
            if not p_match:
                continue
            param, val = p_match.groups()
            if is_technical_param(param):
                continue
            # নেভবক্সের ইন্টারনাল কী (| name = ...) অনুবাদ করা যাবে না — ধরে রাখা হয়।
            if param.lower() == "name":
                continue
            v_strip = val.strip()
            # খালি ভ্যালু বা সাবগ্রুপ খোলা লাইন বাদ
            if not v_strip or v_strip.startswith("{{"):
                continue
            translatable_items.append((idx, "param", "|" + param + " = ", v_strip))

    # ৩. ব্যাচ অনুবাদ (লাইনের প্রতিটি অংশ আলাদা আলাদা অনুবাদ করে পুনরস্থাপন)
    batch_size = 20
    # প্রতিটি লাইন মোতায়েক করে অনুবাদ করি — একই লাইনের সব অংশ একসাথে ব্যাচে
    from collections import defaultdict
    line_parts = defaultdict(list)  # {line_idx: [(part_idx_in_line, prefix, orig_val), ...]}

        # বিষয়শ্রেণী ও বুলেট লাইন প্রসেস
    for idx, line in enumerate(lines):
        line = lines[idx]
        # বিষয়শ্রেণী লাইন প্রসেস
        cat_match = re.match(r"^(\s*\[\[\s*Category\s*:\s*)([^\]|]+)(\|.*)?(\]\]\s*)$", line, re.IGNORECASE)
        if cat_match:
            c_prefix, c_name, c_pipe, c_suffix = cat_match.groups()
            # "Category:" কে "বিষয়শ্রেণী:" তে অনুবাদ এবং c_suffix যোগ
            full_prefix = c_prefix.replace("Category:", "বিষয়শ্রেণী:")
            line_parts[idx] = [(0, full_prefix, c_name.strip(), c_name)]
            continue
        # বুলেট লাইন প্রসেস
        b_match = re.match(r"^(\s*[\*\#]+)\s*(.*)$", line)
        if b_match:
            b_prefix, b_content = b_match.groups()
            if b_content.strip():
                line_parts[idx] = [(0, b_prefix + " ", b_content.strip(), b_content)]
            continue
        line = lines[idx]
        param_parts = _split_top_level_pipes(line)
        part_idx_in_parts = 0
        for part in param_parts:
            p_strip = part.strip()
            if not p_strip:
                part_idx_in_parts += 1
                continue
            if p_strip.startswith('|'):
                p_strip = p_strip[1:].lstrip()
            p_match = re.match(r'^([a-zA-Z0-9_\-]+)\s*=\s*(.*)$', p_strip)
            if not p_match:
                part_idx_in_parts += 1
                continue
            param, val = p_match.groups()
            if is_technical_param(param):
                part_idx_in_parts += 1
                continue
            if param.lower() == "name":
                part_idx_in_parts += 1
                continue
            v_strip = val.strip()
            if not v_strip or v_strip.startswith("{{"):
                part_idx_in_parts += 1
                continue
            prefix = "|" + param + " = "
            raw_trailing = part[len(part.rstrip()):]
            line_parts[idx].append((part_idx_in_parts, prefix, v_strip, raw_trailing))
            part_idx_in_parts += 1

    # প্রতিটি লাইনের অংশসমূহ মিলিয়ে ব্যাচ অনুবাদ
    for idx, parts_list in line_parts.items():
        contents = [pv for _, _, pv, _ in parts_list]
        if not contents:
            continue
        sep = "\n___MW_SEP___\n"
        joined = sep.join(contents)

        tr_raw = ""
        if gemini_key or api_key or (provider or "").lower() == "ollama":
            tr_raw = _call_gemini_template_batch(
                joined, sl=sl, tl=tl, gemini_key=gemini_key, gemini_model=gemini_model,
                provider=provider, api_key=api_key, base_url=base_url,
            )

        if not tr_raw or "___MW_SEP___" not in tr_raw:
            tr_raw = _call_mt(joined, sl=sl, tl=tl)

        parts = tr_raw.split("___MW_SEP___") if tr_raw else []

        # প্রতিটি লাইনের অংশগুলো পুনরায় বিন্যস্ত করা
        translated = False
        first_prefix = parts_list[0][1] if parts_list else ""
        if first_prefix.startswith("[["):
            # বিষয়শ্রেণী লাইন
            c_prefix = first_prefix
            clean_val = normalize_nukta(to_bengali_digits_safe(parts[0].strip())) if parts else ""
            # Get c_suffix from original line
            c_suffix = ""
            cat_match2 = re.match(r"^(\s*\[\[\s*Category\s*:\s*)([^\]|]+)(\|.*)?(\]\]\s*)$", lines[idx], re.IGNORECASE)
            if cat_match2:
                c_suffix = cat_match2.group(4) or ""
            out_lines[idx] = f"{c_prefix}{clean_val}{c_suffix}"
            translated = True
        elif not first_prefix.startswith("|"):
            # বুলেট লাইন
            b_prefix = first_prefix
            clean_val = normalize_nukta(to_bengali_digits_safe(parts[0].strip())) if parts else ""
            out_lines[idx] = f"{b_prefix}{clean_val}"
            translated = True
        else:
            # প্যারামিটার লাইন - pipe-split রূপ থেকে পুনর্নির্মাণ
            param_parts = _split_top_level_pipes(out_lines[idx])
            if len(parts) == len(parts_list):
                for (part_idx, prefix, _, raw_trailing), tr_val in zip(parts_list, parts):
                    clean_val = normalize_nukta(to_bengali_digits_safe(tr_val.strip()))
                    clean_val = clean_val + raw_trailing
                    if part_idx < len(param_parts):
                        param_parts[part_idx] = prefix[1:] + clean_val
                        translated = True
            else:
                for part_idx, prefix, orig_val, raw_trailing in parts_list:
                    single_tr = _call_mt(orig_val, sl=sl, tl=tl)
                    clean_val = normalize_nukta(to_bengali_digits_safe(single_tr.strip()))
                    clean_val = clean_val + raw_trailing
                    if part_idx < len(param_parts):
                        param_parts[part_idx] = prefix[1:] + clean_val
                        translated = True
            if translated:
                if param_parts and not param_parts[0].strip():
                    param_parts[0] = ""
                reconstructed = "|".join(param_parts)
                if out_lines[idx].startswith("|") and not reconstructed.startswith("|"):
                    reconstructed = "|" + reconstructed
                out_lines[idx] = reconstructed

    res = "\n".join(out_lines)

    # ৪. প্লেসহোল্ডারগুলো পুনঃস্থাপন
    for k, v in com_map.items():
        res = res.replace(k, v)
    for k, v in var_map.items():
        res = res.replace(k, v)
    for k, v in cond_map.items():
        res = res.replace(k, v)

    # ৫. অবশিষ্ট রোমান শব্দ ও সংস্থা/শহরের নাম প্রমিত বাংলায় রূপান্তর
    res = _clean_template_entities(res)

    return res


def _clean_template_entities(text: str) -> str:
    """টেমপ্লেটের অনুবাদকৃত আউটপুটে কোনো রোমান শব্দ বা আন্তর্জাতিক সংস্থা/শহর বাদ থাকলে তা প্রমিত বাংলায় রূপান্তর করে।"""
    lines = text.split("\n")
    cleaned_lines = []
    for ln in lines:
        if re.match(r"^\s*\|\s*name\s*=", ln, re.IGNORECASE):
            cleaned_lines.append(ln)
            continue
        s_line = ln
        s_line = re.sub(r"\bCPISRA\s*/\s*IFCPF\b", "সিপিসরা/আইএফসিপিএফ", s_line, flags=re.IGNORECASE)
        s_line = re.sub(r"\bCP\b", "সিপি", s_line)
        for eng, bn in sorted(CITY_AND_ENTITY_MAP.items(), key=lambda x: -len(x[0])):
            s_line = re.sub(r"\b" + re.escape(eng) + r"\b", bn, s_line, flags=re.IGNORECASE)
        # যদি উইকিলিংকের লেবেলে [[Target|Label]] এখনই কোনো রোমান শব্দ বাকি থাকে, ফোনেটিক প্রতিবর্ণীকরণ
        def _clean_link_label(m: re.Match) -> str:
            target = m.group(1)
            label = m.group(2)
            if not label:
                return m.group(0)
            if re.search(r"[a-zA-Z]{2,}", label):
                clean_label = label
                for eng, bn in sorted(CITY_AND_ENTITY_MAP.items(), key=lambda x: -len(x[0])):
                    clean_label = re.sub(r"\b" + re.escape(eng) + r"\b", bn, clean_label, flags=re.IGNORECASE)
                if re.search(r"[a-zA-Z]{2,}", clean_label):
                    try:
                        import sys, os
                        epath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ইংরেজি-বাংলা অনুবাদ")
                        if epath not in sys.path:
                            sys.path.insert(0, epath)
                        from transliterate_engine import transliterate_title_phrase
                        clean_label = re.sub(r"[a-zA-Z]+", lambda wm: transliterate_title_phrase(wm.group(0)), clean_label)
                    except Exception:
                        pass
                return f"[[{target}|{clean_label}]]"
            return m.group(0)
        s_line = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", _clean_link_label, ln)
        cleaned_lines.append(s_line)
    s = "\n".join(cleaned_lines)
    s = to_bengali_digits_safe(s)
    return normalize_nukta(s)


def translate_template_wikitext(
    wikitext: str,
    sl: str = "en",
    tl: str = "bn",
    gemini_key: str | None = None,
    gemini_model: str = "gemini-3.5-flash",
    title: str = "",
    provider: str | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
) -> str:
    """উইকিপিডিয়া টেমপ্লেট উইকিটেক্সট সুরক্ষিত ও প্রমিত বাংলায় রূপান্তর করে।"""
    if not wikitext or not wikitext.strip():
        return wikitext

    has_switch = bool(re.search(r"\{\{\s*#switch\b", wikitext, re.IGNORECASE))
    has_navbox_root = bool(re.search(r"^\s*\{\{\s*(?:Navbox|Sidebar|Subgroup)\b", wikitext, re.IGNORECASE | re.MULTILINE))

    # যদি প্রধান কাঠামো #switch হয় এবং Navbox না হয়, তাহলে সুইচ অনুবাদক
    if has_switch and not has_navbox_root:
        return _translate_switch_template(wikitext, sl=sl, tl=tl)

    # অন্যথায় নেভবক্স ও সাধারণ উপস্থাপনা টেমপ্লেট অনুবাদক
    return _translate_navbox_template(
        wikitext, sl=sl, tl=tl, gemini_key=gemini_key, gemini_model=gemini_model,
        provider=provider, api_key=api_key, base_url=base_url,
    )
