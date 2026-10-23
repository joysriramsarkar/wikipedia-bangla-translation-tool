# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া তথ্যসূত্র অটো-হিলার ও অখণ্ডতা পরীক্ষক (Wikipedia Citation Auto-Healer & Auditor).

কন্টেন্ট ট্রান্সলেশন (CX) টুলের অন্যতম প্রধান শক্তি হলো: কোনো তথ্যসূত্র কখনো
হারিয়ে যায় না বা ভেঙে যায় না।

সমস্যা:
১. মূল নিবন্ধে হয়তো ইনফোবক্সে বা অন্য কোনো অনুচ্ছেদে `<ref name="foo">পূর্ণ সূত্র</ref>` সংজ্ঞায়িত ছিল।
২. অনুবাদের সময় যদি সেই অনুচ্ছেদ বা ইনফোবক্সের প্যারামিটার ড্রপ হয়, তবে পরবর্তী `<ref name="foo" />`
   উইকিপিডিয়ায় মারাত্মক লাল ত্রুটি দেয়:
   "উদ্ধৃতি ত্রুটি: <ref> ট্যাগ বৈধ নয়; 'foo' নামের সূত্রের জন্য কোন লেখা প্রদান করা হয়নি"।
৩. এই মডিউল:
   - অনূদিত উইকিটেক্সটে সব `<ref name="...">` স্ক্যান করে।
   - কোনো নামের পূর্ণ সংজ্ঞা অনুপস্থিত থাকলে তা উৎস নিবন্ধের মূল উইকিটেক্সট থেকে খুঁজে বের করে
     প্রথম `<ref name="foo" />`-এর স্থানে পূর্ণ `<ref name="foo">...</ref>` প্রতিস্থাপন করে।
   - তথ্যসূত্রের পরিসংখ্যান (উৎস vs অনূদিত) হিসাব করে।
"""
import re


_REF_DEF_RE = re.compile(
    r'<ref\b[^>]*?\bname\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^\s/>]+))[^>]*?(?<!/)>([\s\S]*?)</ref>',
    re.IGNORECASE,
)

_REF_EMPTY_RE = re.compile(
    r'<ref\b[^>]*?\bname\s*=\s*(?:"([^"]+)"|\'([^\']+)\'|([^\s/>]+))\s*(?:/>|>\s*</ref>)',
    re.IGNORECASE,
)

_ANY_REF_RE = re.compile(r'<ref\b[^>]*?(?:/>|>.*?</ref>)', re.IGNORECASE | re.DOTALL)


def extract_reference_definitions(wikitext: str) -> dict[str, str]:
    """উইকিটেক্সটে সংজ্ঞায়িত সমস্ত `<ref name="NAME">CONTENT</ref>` খুঁজে অভিধান আকারে দেয়।"""
    defs = {}
    for m in _REF_DEF_RE.finditer(wikitext):
        name = m.group(1) or m.group(2) or m.group(3)
        content = m.group(4)
        if name and content and content.strip():
            clean_name = name.strip()
            # যদি ইতিমধ্যে সংরক্ষিত না থাকে বা নতুনটিতে বেশি কনটেন্ট থাকে
            if clean_name not in defs or len(content) > len(defs[clean_name]):
                defs[clean_name] = content.strip()
    return defs


def extract_used_ref_names(wikitext: str) -> set[str]:
    """উইকিটেক্সটে ব্যবহৃত সমস্ত রেফারেন্স নাম (সংজ্ঞা ও ফাঁকা উভয়ই) সংগ্রহ করে।"""
    names = set()
    for m in _REF_DEF_RE.finditer(wikitext):
        n = m.group(1) or m.group(2) or m.group(3)
        if n:
            names.add(n.strip())
    for m in _REF_EMPTY_RE.finditer(wikitext):
        n = m.group(1) or m.group(2) or m.group(3)
        if n:
            names.add(n.strip())
    return names


def heal_named_references(target_wikitext: str, source_wikitext: str = "") -> tuple[str, list[str], list[str]]:
    """অনাথ/ভাঙা রেফারেন্স নিরাময় করে।

    যদি অনূদিত টেক্সটে `<ref name="foo" />` থাকে কিন্তু তার কোনো পূর্ণ সংজ্ঞা না থাকে,
    তবে সোর্স উইকিটেক্সট থেকে পূর্ণ সংজ্ঞা নিয়ে প্রথম ব্যবহারের স্থানে বসিয়ে দেয়।

    Returns:
        (healed_wikitext, healed_names_list, broken_unrecoverable_list)
    """
    if not target_wikitext:
        return target_wikitext, [], []

    target_defs = extract_reference_definitions(target_wikitext)
    source_defs = extract_reference_definitions(source_wikitext) if source_wikitext else {}

    # ফাঁকা ব্যবহারগুলো খুঁজে বের করি
    empty_calls: list[tuple[str, int, int, str]] = []
    for m in _REF_EMPTY_RE.finditer(target_wikitext):
        name = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if name:
            empty_calls.append((name, m.start(), m.end(), m.group(0)))

    healed_names = []
    broken_names = []
    replacements: dict[str, str] = {}

    for name, _, _, _ in empty_calls:
        if name not in target_defs and name not in replacements:
            if name in source_defs:
                # সোর্সে পূর্ণ সংজ্ঞা পাওয়া গেছে — নিরাময় করব!
                replacements[name] = f'<ref name="{name}">{source_defs[name]}</ref>'
                healed_names.append(name)
            else:
                broken_names.append(name)

    if not replacements:
        return target_wikitext, [], broken_names

    # প্রথম ব্যবহারের স্থানে পূর্ণ সংজ্ঞা প্রতিস্থাপন করি
    healed_text = target_wikitext
    for name, full_ref in replacements.items():
        pattern = re.compile(
            rf'<ref\b[^>]*?\bname\s*=\s*["\']?{re.escape(name)}["\']?\s*(?:/>|>\s*</ref>)',
            re.IGNORECASE,
        )
        # শুধুমাত্র প্রথম উপস্থিতিটি প্রতিস্থাপন করব
        healed_text = pattern.sub(full_ref, healed_text, count=1)

    return healed_text, healed_names, broken_names


def audit_citations(target_wikitext: str, source_wikitext: str = "") -> dict:
    """উৎস ও লক্ষ্য উইকিটেক্সটের তথ্যসূত্র নিরীক্ষা করে পরিসংখ্যান তৈরি করে।"""
    target_defs = extract_reference_definitions(target_wikitext)
    source_defs = extract_reference_definitions(source_wikitext) if source_wikitext else {}

    target_all_refs = _ANY_REF_RE.findall(target_wikitext)
    source_all_refs = _ANY_REF_RE.findall(source_wikitext) if source_wikitext else []

    # খালি/অনাথ রেফারেন্স শনাক্তকরণ
    orphans = []
    for m in _REF_EMPTY_RE.finditer(target_wikitext):
        name = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if name and name not in target_defs:
            orphans.append(name)

    orphans = sorted(set(orphans))

    return {
        "source_ref_count": len(source_all_refs),
        "target_ref_count": len(target_all_refs),
        "source_named_defs": len(source_defs),
        "target_named_defs": len(target_defs),
        "orphaned_refs": orphans,
        "is_healthy": len(orphans) == 0,
    }
