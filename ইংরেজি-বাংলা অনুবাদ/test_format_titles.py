# -*- coding: utf-8 -*-
import json, re

with open('book_bn_map.json', encoding='utf-8') as f:
    book_bn = json.load(f)

# Supplementary verified book titles
extra_books = {
    'Confessions (Rousseau)': 'কনফেশনস (রুশো)',
    'The Autobiography of Benjamin Franklin': 'দ্য অটোবায়োগ্রাফি অব বেঞ্জামিন ফ্র্যাঙ্কলিন',
    'Mein Kampf': 'মাইন কাম্পফ',
    'Long Walk to Freedom': 'লং ওয়াক টু ফ্রিডম',
    'Baburnama': 'বাবরনামা',
    'The Story of My Experiments with Truth': 'সত্যের সঙ্গে আমার প্রয়োগ',
    'The Diary of a Young Girl': 'একটি কিশোরীর ডায়েরি',
    'Wings of Fire (autobiography)': 'অগ্নিপক্ষ',
    'Wings of Fire': 'অগ্নিপক্ষ',
    'An Autobiography (Nehru)': 'অ্যান অটোবায়োগ্রাফি (নেহেরু)',
    'The Autobiography of an Unknown Indian': 'দি অটোবায়োগ্রাফি অব অ্যান আননোন ইন্ডিয়ান',
    'Jakhan Choto Chilam': 'যখন ছোট ছিলাম',
    'Autobiography of a Yogi': 'অটোবায়োগ্রাফি অব আ যোগী',
    'Dichtung und Wahrheit': 'ডিকটুং উন্ট ভারহাইট',
    'Childhood, Boyhood, and Youth': 'শৈশব, কৈশোর ও তারুণ্য',
    'A Confession': 'আ কনফেশন',
    'My Childhood': 'আমার ছেলেবেলা',
    'The Autobiography of Benvenuto Cellini': 'বেনভেনুতো চেল্লিনির আত্মজীবনী',
    'Histoire de ma vie': 'হিস্তোয়ার দ্য মা ভি',
    'Tuzk-e-Jahangiri': 'তুজুক-ই-জাহাঙ্গিরি',
    'I Am Malala': 'আই অ্যাম মালালা',
    'Meditations': 'মেডিটেশনস',
    'Confessions (Augustine)': 'কনফেশনস (অগাস্টিন)',
    'The Words (book)': 'দ্য ওয়ার্ডস',
    'Memories, Dreams, Reflections': 'মেমোরিজ, ড্রিমস, রিফ্লেকশনস',
    'A Mathematician\'s Apology': 'আ ম্যাথমেটিশিয়ানস অ্যাপোলজি',
    'Surely You\'re Joking, Mr. Feynman!': 'সিওরলি ইউ আর জোকিং, মি. ফাইনম্যান!',
    'The Red Fighter Pilot': 'দ্য রেড ফাইটার পাইলট',
    'The Fun of It': 'দ্য ফান অব ইট',
    'Enemy Coast Ahead': 'এনিমি কোস্ট অ্যাহেড',
    'My Autobiography': 'মাই অটোবায়োগ্রাফি',
    'Personal Memoirs of Ulysses S. Grant': 'পার্সোনাল মেমোয়ার্স অব উইলিসিস এস. গ্রান্ট',
    'Panzer Leader (book)': 'প্যানজার লিডার',
    'The Autobiography of Charles Darwin': 'চার্লস ডারউইনের আত্মজীবনী',
    'Narrative of the Life of Frederick Douglass, an American Slave': 'ন্যারেটিভ অব দ্য লাইফ অব ফ্রেডেরিক ডগলাস',
    'Kashmir Udaas Hai': 'কাশ্মীর উদাস হ্যায়',
    'Hōjōki': 'হোজোকি',
    'The Pillow Book': 'দ্য পিলো বুক',
    'My Girlhood': 'আমার মেয়েবেলা',
    'Gusty Wind': 'উতাল হাওয়া',
    'Speak Up or Split Into Two': 'দ্বিখণ্ডিত',
    'Those Dark Days': 'সেইসব অন্ধকার',
    'I Am Not Fine, But You Stay Well My Beloved Country': 'আমি ভালো নেই তুমি ভালো থেকো প্রিয় দেশ',
    'Nothing Is There': 'নেই কিছু নেই'
}

for k, v in extra_books.items():
    if k not in book_bn:
        book_bn[k] = v

TITLE_WORDS = {
    'The': 'দ্য', 'the': 'দ্য', 'Of': 'অব', 'of': 'অব', 'My': 'মাই', 'my': 'মাই',
    'Life': 'লাইফ', 'life': 'লাইফ', 'A': 'আ', 'a': 'আ', 'And': 'অ্যান্ড', 'and': 'অ্যান্ড',
    'I': 'আই', 'Autobiography': 'অটোবায়োগ্রাফি', 'In': 'ইন', 'in': 'ইন', 'To': 'টু', 'to': 'টু',
    'Me': 'মি', 'me': 'মি', 'It': 'ইট', 'it': 'ইট', 'Story': 'স্টোরি', 'story': 'স্টোরি',
    'An': 'অ্যান', 'an': 'অ্যান', 'Years': 'ইয়ার্স', 'years': 'ইয়ার্স', 'You': 'ইউ', 'you': 'ইউ',
    'From': 'ফ্রম', 'from': 'ফ্রম', 'Memoirs': 'মেমোয়ার্স', 'Memoir': 'মেমোয়ার',
    'Is': 'ইজ', 'is': 'ইজ', 'Pilot': 'পাইলট', 'All': 'অল', 'all': 'অল', 'On': 'অন', 'on': 'অন',
    'One': 'ওয়ান', 'one': 'ওয়ান', 'Fighter': 'ফাইটার', 'Man': 'ম্যান', 'World': 'ওয়ার্ল্ড',
    'War': 'ওয়ার', 'Hollywood': 'হলিউড', 'With': 'উইথ', 'with': 'উইথ', 'For': 'ফর', 'for': 'ফর',
    'Day': 'ডে', 'Days': 'ডেস', 'Night': 'নাইট', 'Nights': 'নাইটস', 'Girl': 'গার্ল',
    'Boy': 'বয়', 'Uptown': 'আপটাউন', 'Speed': 'স্পিড', 'Skyward': 'স্কাইওয়ার্ড',
    'Winged': 'উইংড', 'Warfare': 'ওয়ারফেয়ার', 'Fun': 'ফান', 'Wind': 'উইন্ড',
    'Wires': 'ওয়্যারস', 'Record': 'রেকর্ড', 'Flights': 'ফ্লাইটস', 'Flight': 'ফ্লাইট',
    'Flying': 'ফ্লাইং', 'Fly': 'ফ্লাই', 'Flew': 'ফ্লু', 'Corps': 'কোর', 'Royal': 'রয়্যাল',
    'Five': 'ফাইভ', 'Wanted': 'ওয়ান্টেড', 'Wings': 'উইংস', 'Wing': 'উইং', 'High': 'হাই', 'Wide': 'ওয়াইড',
    'Frightened': 'ফ্রাইটেন্ড', 'Last': 'লাস্ট', 'Enemy': 'এনিমি', 'West': 'ওয়েস্ট',
    'Thirty': 'থার্টি', 'Seconds': 'সেকেন্ডস', 'Over': 'ওভার', 'Tokyo': 'টোকিও',
    'Ahead': 'অ্যাহেড', 'Coast': 'কোস্ট', 'Bomber': 'বোম্বার', 'Offensive': 'অফেন্সিভ',
    'Serenade': 'সেরেনেড', 'Big': 'বিগ', 'Bird': 'বার্ড', 'Global': 'গ্লোবাল',
    'Mission': 'মিশন', 'Way': 'ওয়ে', 'General': 'জেনারেল', 'Reports': 'রিপোর্টস',
    'Personal': 'পার্সোনাল', 'History': 'হিস্ট্রি', 'Pacific': 'প্যাসিফিক',
    'Visibility': 'ভিজিবিলিটি', 'Unlimited': 'আনলিমিটেড', 'Away': 'অ্যাওয়ে', 'Went': 'ওয়েন্ট',
    'Show': 'শো', 'First': 'ফার্স্ট', 'Stormy': 'স্টর্মি', 'Führer': 'ফুয়েরার',
    'Sea': 'সি', 'Fleet': 'ফ্লিট', 'Arm': 'আর্ম', 'Slide': 'স্লাইড', 'Rule': 'রুল',
    'Engineer': 'ইঞ্জিনিয়ার', 'Lonely': 'লোনলি', 'Sky': 'স্কাই', 'Leader': 'লিডার',
    'Central': 'সেন্ট্রাল', 'Blue': 'ব্লু', 'Recollections': 'রিকলেকশনস',
    'Reflections': 'রিফ্লেকশনস', 'Completed': 'কমপ্লিটেড', 'Black': 'ব্ল্যাক',
    'Sheep': 'শিপ', 'Thunderbolt': 'থান্ডারবোল্ট', 'Forever': 'ফরএভার',
    'Air': 'এয়ার', 'Force': 'ফোর্স', 'Space': 'স্পেস', 'Time': 'টাইম',
    'Love': 'লাভ', 'Good': 'গুড', 'Bad': 'ব্যাড', 'True': 'ট্রু',
    'False': 'ফলস', 'Never': 'নেভার', 'Again': 'অ্যাগেইন', 'Back': 'ব্যাক',
    'Home': 'হোম', 'Heart': 'হার্ট', 'Soul': 'সোল', 'Mind': 'মাইন্ড',
    'Body': 'বডি', 'Frontier': 'ফ্রন্টিয়ার', 'Follies': 'ফলিজ', 'Answer': 'অ্যানসার',
    'Justice': 'জাস্টিস', 'Judge': 'জাজ', 'Shot': 'শট', 'Chef': 'শেফ',
    'Morning': 'মর্নিং', 'Middle': 'মিডল', 'Nowhere': 'নোহোয়ার', 'Marriage': 'ম্যারিজ',
    'Motherhood': 'মাদারহুড', 'Adventures': 'অ্যাডভেঞ্চার্স', 'Among': 'অ্যামং',
    'Eagles': 'ঈগলস', 'Woman': 'উইমেন', 'Military': 'মিলিটারি', 'Test': 'টেস্ট',
    'Two': 'টু', 'Red': 'রেড', 'Owned': 'ওনড', 'Chickenhawk': 'চিকেনহক',
    'Baa': 'বা', 'So': 'সো', 'See': 'সি', 'Yes': 'ইয়েস', 'WASP': 'ওয়াস্প',
    'II': '২য়', 'III': '৩য়', 'IV': '৪র্থ', 'V': '৫ম', 'Baron': 'ব্যারন'
}

from build_translation import transliterate_word

def transliterate_title_to_bn(title):
    tokens = re.split(r'(\s+|[.,:;!?\(\)\'\"\-–—])', title)
    out = []
    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,:;!?\(\)\'\"\-–—]+$', t):
            out.append(t)
        else:
            if t in TITLE_WORDS:
                out.append(TITLE_WORDS[t])
            elif t.capitalize() in TITLE_WORDS:
                out.append(TITLE_WORDS[t.capitalize()])
            else:
                out.append(transliterate_word(t))
    return ''.join(out)

def format_titles(title_raw):
    # 1. Cleanly isolate notes
    efn_pos = title_raw.find('{{efn')
    ref_pos = title_raw.find('<ref')
    cut_pos = -1
    if efn_pos != -1 and ref_pos != -1:
        cut_pos = min(efn_pos, ref_pos)
    elif efn_pos != -1:
        cut_pos = efn_pos
    elif ref_pos != -1:
        cut_pos = ref_pos

    if cut_pos != -1:
        title_core = title_raw[:cut_pos].strip()
        notes = title_raw[cut_pos:].strip()
    else:
        title_core = title_raw.strip()
        notes = ''

    # Strip surrounding quotes if present
    clean_core = title_core
    if clean_core.startswith("''") and clean_core.endswith("''") and len(clean_core) >= 4:
        clean_core = clean_core[2:-2].strip()

    m_b = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', clean_core)
    has_link = bool(m_b)
    link_target = m_b.group(1).strip() if m_b else ''
    link_disp = m_b.group(2).strip() if (m_b and m_b.group(2)) else link_target
    clean_target = re.sub(r'\s*\([^)]*\)', '', link_target).strip()

    pure_text = re.sub(r'\[\[|\]\]', '', clean_core).strip()
    m_paren = re.search(r"^([^'(]+)\s*\(([^)]+)\)$", pure_text)

    # Check known Bengali title
    known_bn = None
    if has_link:
        if link_target in book_bn:
            known_bn = book_bn[link_target]
        elif clean_target in book_bn:
            known_bn = book_bn[clean_target]
        elif link_disp in book_bn:
            known_bn = book_bn[link_disp]
    if not known_bn:
        if pure_text in book_bn:
            known_bn = book_bn[pure_text]
        elif m_paren and m_paren.group(1).strip() in book_bn:
            known_bn = book_bn[m_paren.group(1).strip()]

    # 2. Bengali title column
    if known_bn:
        if has_link:
            bn_title = f"''[[{known_bn}]]''"
        else:
            bn_title = f"''{known_bn}''"
    else:
        # Transliterate directly to Bengali script
        if m_paren:
            main_part = m_paren.group(1).strip()
            trans_bn = transliterate_title_to_bn(main_part)
        elif has_link:
            trans_bn = transliterate_title_to_bn(link_disp)
        else:
            trans_bn = transliterate_title_to_bn(pure_text)
        
        if has_link:
            bn_title = f"''[[{link_target}|{trans_bn}]]''"
        else:
            bn_title = f"''{trans_bn}''"

    # 3. Roman/Original title column
    if m_paren:
        eng_part = m_paren.group(1).strip()
        orig_part = m_paren.group(2).strip()
        if not orig_part.startswith("''"):
            orig_part = f"''{orig_part}''"
        if has_link:
            roman_title = f"''[[{link_target}|{eng_part}]]'' ({orig_part})"
        else:
            roman_title = f"''{eng_part}'' ({orig_part})"
    else:
        if has_link:
            roman_title = f"''[[{link_target}|{link_disp}]]''"
        else:
            roman_title = f"''{pure_text}''"

    if notes:
        roman_title = f"{roman_title}{notes}"

    return bn_title, roman_title

samples = [
    "''[[The Diary of a Young Girl]]''",
    "''Uptown Girl''",
    "''Mission Completed''{{efn|1=A previous book, ''Wingless Victory'' (alternately known as ''Alone He Went''), was published in 1950. However, it was it was \"written by an R.A.F. colleague of Embry's, and thus [does not have] the personal touch of autobiography\" according to a review.<ref>{{cite magazine |date=27 August 1951 |title=Books: Flyer's Flight |url=https://content.time.com/time/subscriber/article/0,33009,815296,00.html |magazine=Time  |access-date=28 January 2024}}</ref>}}",
    "''[[The Red Fighter Pilot]]''",
    "''My Fights (Mes Combats)''",
    "''[[Some Still Live]]''",
    "''[[The Fun of It]]''",
    "''Thirty Seconds Over Tokyo''",
    "''I Serve the Motherland (Служу Родиনে)''",
    "''[[The Story of My Experiments with Truth]]''",
    "''[[Mein Kampf]]''",
    "''[[Long Walk to Freedom]]''",
    "''[[Wings of Fire (autobiography)|Wings of Fire]]''",
    "''[[Jakhan Choto Chilam]]''"
]

for s in samples:
    bn_col, ro_col = format_titles(s)
    print("--------------------------------------------------")
    print(f"RAW:   {s[:70]}")
    print(f"BN:    {bn_col}")
    print(f"ROMAN: {ro_col[:70]}")
