# -*- coding: utf-8 -*-
"""
ইনফোবক্স/টেমপ্লেট ম্যাপ (প্রোটোটাইপ): Infobox settlement → তথ্যছক বসতি।

স্ক্রিনশট কেস: Central-West Region, Brazil — `{{Infobox settlement}}`-এর
লেবেল (Country, Largest city, States, Region, Total, Year) ইংরেজিতে
রয়ে গিয়েছিল। এই মডিউল:
1. টেমপ্লেটের নাম বদলায়,
2. পরিচিত প্যারাম (`subdivision_name`, `population_total` …) বাংলায় করে,
3. পরিচিত লেবেল-মান (`Country` → `দেশ`) বাংলায় করে,
4. মানের ভেতরের সংখ্যা `bn_digits_safe` দিয়ে বাংলায় করে,
5. অচেনা প্যারাম ফেলে না দিয়ে রেখে দেয় + রিপোর্ট করে।
"""
import re
from .bn_digits_safe import to_bengali_digits_safe

INFOBOX_TYPE_MAP = {
    "building": "ভবন",
    "settlement": "বসতি",
    "region": "অঞ্চল",
    "country": "দেশ",
    "person": "ব্যক্তি",
    "officeholder": "রাজনীতিবিদ",
    "politician": "রাজনীতিবিদ",
    "organization": "সংস্থা",
    "company": "কোম্পানি",
    "railway line": "রেলপথ",
    "rail line": "রেলপথ",
    "station": "স্টেশন",
    "rail service": "রেল পরিষেবা",
    "bridge": "সেতু",
    "road": "সড়ক",
    "highway": "মহাসড়ক",
    "film": "চলচ্চিত্র",
    "book": "বই",
    "album": "অ্যালবাম",
    "single": "একক",
    "musical artist": "সঙ্গীতশিল্পী",
    "actor": "অভিনেতা",
    "writer": "লেখক",
    "scientist": "বিজ্ঞানী",
    "athlete": "ক্রীড়াবিদ",
    "sportsperson": "ক্রীড়াবিদ",
    "football biography": "ফুটবল জীবনী",
    "cricketer": "ক্রিকেটার",
    "university": "বিশ্ববিদ্যালয়",
    "school": "বিদ্যালয়",
    "college": "কলেজ",
    "hospital": "হাসপাতাল",
    "airport": "বিমানবন্দর",
    "airline": "বিমান সংস্থা",
    "aircraft": "উড়োজাহাজ",
    "river": "নদী",
    "mountain": "পর্বত",
    "lake": "হ্রদ",
    "island": "দ্বীপ",
    "park": "উদ্যান",
    "protected area": "সংরক্ষিত এলাকা",
    "stadium": "স্টেডিয়াম",
    "event": "ঘটনা",
    "military conflict": "সামরিক সংঘর্ষ",
    "military unit": "সামরিক ইউনিট",
    "election": "নির্বাচন",
    "city": "শহর",
    "district": "জেলা",
    "monument": "স্মারক",
    "museum": "জাদুঘর",
    "software": "সফটওয়্যার",
    "website": "ওয়েবসাইট",
    "video game": "ভিডিও গেম",
    "dam": "বাঁধ",
    "power station": "বিদ্যুৎ কেন্দ্র",
    "shopping mall": "শপিং মল",
    "hotel": "হোটেল",
    "temple": "মন্দির",
    "mosque": "মসজিদ",
    "church": "গির্জা",
    "religious building": "ধর্মীয় ভবন",
    "saint": "সাধু",
    "christian leader": "খ্রিস্টান নেতা",
    "religious biography": "ধর্মীয় ব্যক্তি",
    "philosopher": "দার্শনিক",
    "monarch": "শাসক",
    "royalty": "রাজপরিবার",
    "noble": "অভিজাত",
    "military person": "সামরিক ব্যক্তিত্ব",
    "cardinal": "কার্ডিনাল",
    "pope": "পোপ",
    "bishop": "বিশপ",
    "priest": "যাজক",
    "theologian": "ধর্মতত্ত্ববিদ",
    "artist": "শিল্পী",
    "painter": "চিত্রশিল্পী",
    "sculptor": "ভাস্কর",
    "body of water": "জলাশয়",
    "waterfall": "জলপ্রপাত",
    "valley": "উপত্যকা",
    "forest": "বন",
    "volcano": "আগ্নেয়গিরি",
    "spacecraft": "মহাকাশযান",
    "telescope": "দূরবীক্ষণ যন্ত্র",
    "weapon": "অস্ত্র",
    "battle": "যুদ্ধ",
    "treaty": "চুক্তি",
    "medical condition": "চিকিৎসা অবস্থা",
    "disease": "রোগ",
    "drug": "ঔষধ",
}

INFOBOX_NAME_MAP = {
    "Infobox settlement": "তথ্যছক বসতি",
    "Infobox region": "তথ্যছক অঞ্চল",
    "Infobox country": "তথ্যছক দেশ",
    "Infobox building": "তথ্যছক ভবন",
}
for k, v in INFOBOX_TYPE_MAP.items():
    INFOBOX_NAME_MAP[f"Infobox {k}"] = f"তথ্যছক {v}"
    INFOBOX_NAME_MAP[f"infobox {k}"] = f"তথ্যছক {v}"

# en প্যারাম → bn প্যারাম (bn:তথ্যছক বসতি ও তথ্যছক ভবন-এ প্রচলিত নাম)
PARAM_MAP = {
    "name": "নাম",
    "native_name": "স্থানীয়_নাম",
    "settlement_type": "ধরন",
    "building_name": "নাম",
    "building_type": "ধরন",
    "architectural_style": "স্থাপত্যশৈলী",
    "structural_system": "কাঠামোগত_পদ্ধতি",
    "cost": "নির্মাণব্যয়",
    "location": "অবস্থান",
    "address": "ঠিকানা",
    "client": "গ্রাহক",
    "owner": "মালিক",
    "current_tenants": "বর্তমান_ভাড়াটিয়া",
    "landlord": "বাড়িওয়ালা",
    "start_date": "শুরুর_তারিখ",
    "construction_start_date": "নির্মাণ_শুরু",
    "completion_date": "সমাপ্তির_তারিখ",
    "opening": "উদ্বোধন",
    "demolition_date": "ধ্বংসের_তারিখ",
    "height": "উচ্চতা",
    "roof": "ছাদ",
    "top_floor": "শীর্ষ_তলা",
    "antenna_spire": "অ্যান্টেনা_স্পায়ার",
    "floor_count": "তলার_সংখ্যা",
    "floor_area": "তলার_আয়তন",
    "elevator_count": "লিফটের_সংখ্যা",
    "architect": "স্থপতি",
    "architecture_firm": "স্থাপত্য_প্রতিষ্ঠান",
    "developer": "বিকাশকারী",
    "engineer": "প্রকৌশলী",
    "structural_engineer": "কাঠামোগত_প্রকৌশলী",
    "services_engineer": "পরিষেবা_প্রকৌশলী",
    "civil_engineer": "পুরকৌশলী",
    "main_contractor": "প্রধান_ঠিকাদার",
    "awards": "পুরস্কার",
    "image_map": "মানচিত্র",
    "map_caption": "মানচিত্রের_ব্যাখ্যা",
    "pushpin_map": "পুশপিন_মানচিত্র",
    "coordinates": "স্থানাঙ্ক",
    "subdivision_type": "উপবিভাগের_ধরন",
    "subdivision_name": "উপবিভাগের_নাম",
    "subdivision_type1": "উপবিভাগের_ধরন১",
    "subdivision_name1": "উপবিভাগের_নাম১",
    "subdivision_type2": "উপবিভাগের_ধরন২",
    "subdivision_name2": "উপবিভাগের_নাম২",
    "leader_title": "নেতার_পদবি",
    "area_total_km2": "আয়তন_মোট_বর্গকিমি",
    "area_land_km2": "আয়তন_স্থল_বর্গকিমি",
    "population_total": "জনসংখ্যা_মোট",
    "population_as_of": "জনসংখ্যা_হিসাবকাল",
    "population_density_km2": "জনসংখ্যা_ঘনত্ব_বর্গকিমি",
    "population_rank": "জনসংখ্যা_ক্রম",
    "area_rank": "আয়তন_ক্রম",
    "timezone": "সময়_অঞ্চল",
    "utc_offset": "ইউটিসি_অফসেট",
    "elevation_m": "উচ্চতা_মিটার",
    "postal_code": "ডাক_সঙ্কেত",
    "area_code": "এলাকা_কোড",
    "website": "ওয়েবসাইট",
    "gdp_total": "মোট_দেশজ_উৎপাদন",
    "hdi_year": "মানব_উন্নয়ন_সূচক_বছর",
}

# মান হিসেবে আসা পরিচিত লেবেল
LABEL_MAP = {
    "Country": "দেশ",
    "Largest city": "বৃহত্তম শহর",
    "States": "রাজ্য",
    "Region": "অঞ্চল",
    "Total": "মোট",
    "Year": "বছর",
    "Rural": "গ্রামীণ",
    "Urban": "শহুরে",
    "Government Offices": "সরকারি অফিস",
    "Expected": "প্রত্যাশিত",
}

TEMPLATE_MAP = {
    "Reflist": "সূত্র তালিকা",
    "DEFAULTSORT": "DEFAULTSORT",  # নাম একই, মান বাংলায় হয়
}

_INFOBOX_PATTERN = re.compile(
    r"\{\{\s*(?:[Ii]nfobox|তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স|তথ্যছক)\b(?:\s+([a-zA-Z0-9_\u0980-\u09FF ]+?))?(?=\s*[\n|\|\}])",
    re.IGNORECASE,
)


def _translate_value(value: str) -> str:
    v = value.strip()
    if v in LABEL_MAP:
        return LABEL_MAP[v]
    return to_bengali_digits_safe(value)


# বাংলা টেমপ্লেটে এই প্যারামিটারগুলো নেই — রাখলে "অসমর্থিত প্যারামিটার" সতর্কবার্তা হয়।
RELIGIOUS_DROP_KEYS = {"mapframe", "mapframe-zoom", "mapframe-width",
                       "mapframe-height", "mapframe-wikidata", "pushpin_map"}


KEEP_ENGLISH_KEYS_INFOBOXES = {
    # Sports & Biography
    "football biography", "ফুটবল জীবনী",
    "cricketer", "ক্রিকেটার",
    "athlete", "ক্রীড়াবিদ",
    "sportsperson",
    "person", "ব্যক্তি",
    "officeholder", "রাজনীতিবিদ",
    "politician",
    "actor", "অভিনেতা",
    "actress", "অভিনেত্রী",
    "writer", "লেখক",
    "scientist", "বিজ্ঞানী",
    "military person", "সামরিক ব্যক্তিত্ব",
    "artist", "শিল্পী",
    "painter", "চিত্রশিল্পী",
    "sculptor", "ভাস্কর",
    "noble", "অভিজাত",
    "monarch", "শাসক",
    "royalty", "রাজপরিবার",
    "cardinal", "কার্ডিনাল",
    "pope", "পোপ",
    "bishop", "বিশপ",
    "priest", "যাজক",
    "theologian", "ধর্মতত্ত্ববিদ",
    # Media & Arts
    "film", "চলচ্চিত্র",
    "television", "টেলিভিশন",
    "album", "অ্যালবাম",
    "single", "একক",
    "musical artist", "সঙ্গীতশিল্পী",
    # Tech
    "software", "সফটওয়্যার",
    "video game", "ভিডিও গেম",
    # Religious
    "saint", "সাধু",
    "christian leader", "খ্রিস্টান নেতা",
    "religious biography", "ধর্মীয় ব্যক্তি",
}


def translate_infobox(wikitext: str) -> tuple[str, list[str]]:
    """উইকিটেক্সটের Infobox (যেমন Infobox settlement, Infobox building ইত্যাদি) বাংলায় করে।

    Returns:
        (নতুন_টেক্সট, অচেনা_প্যারামের_তালিকা)
    """
    unknown: list[str] = []

    def _repl_box(body: str) -> str:
        # ১. নাম ও ধরন প্রমিত বাংলায় রূপান্তর
        open_match = re.match(
            r"^\{\{\s*(?:([Ii]nfobox)|(তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স|তথ্যছক))\b(?:\s+([a-zA-Z0-9_\u0980-\u09FF ]+?))?(?=\s*[\n|\|\}])",
            body,
            re.IGNORECASE,
        )
        raw_type = ""
        bn_type = ""
        if open_match:
            is_en = bool(open_match.group(1))
            raw_type = (open_match.group(3) or "").strip()
            bn_type = INFOBOX_TYPE_MAP.get(raw_type.lower(), "")
            if bn_type:
                header_repl = f"{{{{তথ্যছক {bn_type}"
                body = header_repl + body[open_match.end():]
            elif is_en:
                # বাংলা নাম যাচাই না হলে মূল ইংরেজি নাম অক্ষত থাকবে (যেমন {{Infobox ...}})
                pass
            else:
                header_repl = f"{{{{তথ্যছক {raw_type}".strip() if raw_type else "{{তথ্যছক"
                body = header_repl + body[open_match.end():]
        else:
            raw_type = ""
            body = re.sub(
                r"^\{\{\s*(?:তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স)\b",
                "{{তথ্যছক",
                body,
                flags=re.IGNORECASE,
            )

        type_key = (raw_type or "").strip().lower()
        bn_type_lower = (bn_type or "").strip().lower()
        is_religious = (
            "religious" in type_key or "ধর্ম" in type_key
            or type_key in {"church", "mosque", "temple", "monastery", "synagogue", "hindu temple", "saint", "christian leader"}
            or bn_type_lower in {"গির্জা", "মসজিদ", "মন্দির", "সাধু"}
        )
        keep_english_keys = is_religious or type_key in KEEP_ENGLISH_KEYS_INFOBOXES or bn_type_lower in KEEP_ENGLISH_KEYS_INFOBOXES
        dropped = RELIGIOUS_DROP_KEYS if is_religious else set()

        # ২. প্যারাম: প্রতিটি `| key = value` লাইন
        def _repl_param(pm: re.Match) -> str:
            key = pm.group(1).strip()
            val = pm.group(2)
            if key.lower() in dropped:
                return ""
            bn_key = None if keep_english_keys else PARAM_MAP.get(key, PARAM_MAP.get(key.lower()))
            if bn_key is None:
                if not keep_english_keys and any("a" <= c.lower() <= "z" for c in key):
                    unknown.append(key)
                return f"| {key} = {_translate_value(val)}"
            return f"| {bn_key} = {_translate_value(val)}"

        body = re.sub(
            r"^\s*\|\s*([A-Za-z0-9_\-\u0980-\u09FF ]+?)\s*=\s*(.*?)\s*$",
            _repl_param,
            body,
            flags=re.MULTILINE,
        )
        return body

    out_parts: list[str] = []
    i = 0
    while True:
        m = _INFOBOX_PATTERN.search(wikitext, i)
        if not m:
            out_parts.append(wikitext[i:])
            break
        out_parts.append(wikitext[i:m.start()])
        # ব্রেস ব্যালান্স গুনে বক্সের শেষ খোঁজো
        depth = 0
        j = m.start()
        while j < len(wikitext) - 1:
            if wikitext[j:j+2] == "{{":
                depth += 1
                j += 2
            elif wikitext[j:j+2] == "}}":
                depth -= 1
                j += 2
                if depth == 0:
                    break
            else:
                j += 1
        box = wikitext[m.start():j]
        out_parts.append(_repl_box(box))
        i = j

    res = "".join(out_parts)
    # যে কোনো অবশিষ্ট 'তথ্যবক্ত', 'তথ্যবক্স', 'তথ্যবাক্স', 'ইনফোবক্স' থাকলে তা বাধ্যতামূলকভাবে 'তথ্যছক'-এ রূপান্তর
    res = re.sub(r"\{\{\s*(?:তথ্যবক্ত|তথ্যবক্স|তথ্যবাক্স|ইনফোবক্স)\b", "{{তথ্যছক", res)
    res = re.sub(r"\{\{\s*তথ্যছক\s+building\b", "{{তথ্যছক ভবন", res, flags=re.IGNORECASE)
    res = re.sub(r"\{\{\s*তথ্যবক্ত\s+ভবন\b", "{{তথ্যছক ভবন", res)
    return res, sorted(set(unknown))
