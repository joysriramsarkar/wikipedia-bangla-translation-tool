# -*- coding: utf-8 -*-
import json
import re

# Load curated film titles map
with open('curated_all_654_films.json', encoding='utf-8') as f:
    film_titles_map = json.load(f)

# Load clean parsed film entries
with open('clean_film_titles.json', encoding='utf-8') as f:
    parsed_entries = json.load(f)

# Load notes translations
with open('notes_translations.json', encoding='utf-8') as f:
    notes_dict = json.load(f)

sorted_note_keys = sorted(notes_dict.keys(), key=len, reverse=True)

# Digit converter
BN_DIGITS = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
def to_bn_num(s):
    return ''.join(BN_DIGITS.get(ch, ch) for ch in str(s))

def translate_trailer(trailer):
    if not trailer:
        return ""
    
    # Save references
    refs = []
    def save_ref(m):
        refs.append(m.group(0))
        return f"__REF_{len(refs)-1}__"
    
    text = re.sub(r'<ref[^>]*>.*?</ref>', save_ref, trailer, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', save_ref, text)
    text = text.strip()
    if not text:
        return ''.join(refs)
    
    # Specific handling for notes with mid-sentence refs
    text = re.sub(
        r'\(stop-motion Holochess sequence created by \[\[Tippett Studio\]\],(__REF_\d+__) and CGI-animated \[\[Death Star\]\] attack plan briefing sequence from \[\[Jet Propulsion Laboratory\]\] made by Larry Cuba and Gary Imhoff\)',
        r'([[টিপেট স্টুডিও]] নির্মিত স্টপ-মোশন হোলোচেস দৃশ্য,\1 এবং ল্যারি কিউবা ও গ্যারি ইমহফ নির্মিত [[জেট প্রপালশন ল্যাবরেটরি]] থেকে সিজিআই-অ্যানিমেটেড [[ডেথ স্টার]] আক্রমণ পরিকল্পনার ব্রিফিং দৃশ্য)',
        text
    )
    text = re.sub(
        r'\(animated universe shown when \[\[Stephen Strange \(Marvel Cinematic Universe\)\|Stephen Strange\]\] and \[\[America Chavez \(Marvel Cinematic Universe\)\|America Chavez\]\] travel through the \[\[Multiverse \(Marvel Cinematic Universe\)\|Multiverse\]\]\.(__REF_\d+__) The animated universe was created with 2D animation\.\)',
        r'(যখন [[স্টিভেন স্ট্রেঞ্জ (মার্ভেল সিনেম্যাটিক ইউনিভার্স)|স্টিভেন স্ট্রেঞ্জ]] এবং [[আমেরিকা শ্যাভেজ (মার্ভেল সিনেম্যাটিক ইউনিভার্স)|আমেরিকা শ্যাভেজ]] [[মাল্টিভার্স (মার্ভেল সিনেম্যাটিক ইউনিভার্স)|মাল্টিভার্স]] দিয়ে ভ্রমণ করেন তখন অ্যানিমেটেড মহাবিশ্ব প্রদর্শিত হয়।\1 এই অ্যানিমেটেড মহাবিশ্বটি ২ডি অ্যানিমেশনের মাধ্যমে তৈরি করা হয়েছিল।)',
        text
    )
    
    # Replace notes
    if text in notes_dict:
        translated_text = notes_dict[text]
    else:
        translated_text = text
        for k in sorted_note_keys:
            if k in translated_text:
                translated_text = translated_text.replace(k, notes_dict[k])
                
    # Restore references
    for i, r in enumerate(refs):
        translated_text = translated_text.replace(f"__REF_{i}__", r)
        
    return translated_text

# Map of raw line number to parsed entry
entry_by_line = {e['line']: e for e in parsed_entries}

def format_film_line(entry):
    yr = entry['year']
    yr_bn = to_bn_num(yr).replace('-', '–')
    
    disp = entry['display']
    target = entry['target']
    trailer = entry['trailer']
    
    # Get curated title data
    t_info = film_titles_map.get(disp)
    if not t_info:
        # Fallback to display
        bn_title = disp
        orig_title = disp
        bn_target = target
    else:
        bn_title = t_info['bn_title']
        bn_target = t_info.get('bn_wiki') or target
        orig_title = disp
        
    # Clean original title if it was an ill template
    if '{{ill|' in orig_title:
        m = re.search(r'\{\{ill\|([^\|\}]+)', orig_title)
        if m:
            orig_title = m.group(1).strip()
            bn_target = f":de:{orig_title}"
    elif '{{Interlanguage link|' in orig_title:
        m_tr = re.search(r'\{\{Interlanguage link\|([^\|\}]+)\|([^\|\}]+)', orig_title)
        if m_tr:
            orig_title_raw = m_tr.group(1).strip()
            lang = m_tr.group(2).strip()
            orig_title = orig_title_raw
            if '3=' in orig_title:
                m_sub = re.search(r'3=([^\|\}]+)', disp)
                if m_sub:
                    orig_title = m_sub.group(1).strip()
            bn_target = f":{lang}:{orig_title}"
            
    # Format the title wikilink
    # Rule 10: ''[[লিংক|বাংলা শিরোনাম]]'' (''মূল শিরোনাম'')
    if bn_target:
        if bn_target == bn_title:
            link_str = f"[[{bn_title}]]"
        else:
            link_str = f"[[{bn_target}|{bn_title}]]"
    else:
        link_str = bn_title
        
    title_formatted = f"''{link_str}'' (''{orig_title}'')"
    
    # Format trailer
    trailer_bn = translate_trailer(trailer)
    if trailer_bn:
        # Check spacing
        if trailer_bn.startswith('<ref') or trailer_bn.startswith(' <ref'):
            full_entry = f"* {yr_bn} – {title_formatted}{trailer_bn.strip()}"
        else:
            full_entry = f"* {yr_bn} – {title_formatted} {trailer_bn.strip()}"
    else:
        full_entry = f"* {yr_bn} – {title_formatted}"
        
    return full_entry

# Section translations
SECTION_TRANSLATIONS = {
    "==Short films by decade==": "== দশক অনুযায়ী স্বল্পদৈর্ঘ্য চলচ্চিত্র ==",
    "==Primary animated films by decade== <!-- films by decade -->": "== দশক অনুযায়ী মূলত অ্যানিমেশনভিত্তিক পূর্ণদৈর্ঘ্য চলচ্চিত্র ==",
    "==Primary live-action feature films by decade== <!-- films by decade -->": "== দশক অনুযায়ী মূলত লাইভ-অ্যাকশন পূর্ণদৈর্ঘ্য চলচ্চিত্র ==",
    "==See also==": "== আরও দেখুন ==",
    "==References==": "== তথ্যসূত্র ==",
    "==External links==": "== বহিঃসংযোগ =="
}

def translate_heading(h):
    h_clean = h.strip()
    if h_clean in SECTION_TRANSLATIONS:
        return SECTION_TRANSLATIONS[h_clean]
    
    # Subsection ===1900s=== or === 1980s ===
    m = re.match(r'^===\s*(\d{4})s\s*===$', h_clean)
    if m:
        yr_bn = to_bn_num(m.group(1))
        return f"=== {yr_bn}-এর দশক ==="
    
    return h_clean

# Read raw file and produce output
output_lines = []

with open('List_of_films_with_live_action_and_animation_raw.txt', encoding='utf-8') as f:
    raw_lines = f.readlines()

skip_until_intro = False
for line_idx, line in enumerate(raw_lines, 1):
    s = line.strip()
    
    # 1. Skip short description
    if s.startswith('{{Short description'):
        continue
        
    # 2. Template
    if s.startswith('{{More citations needed'):
        output_lines.append('{{উৎসবিহীন|তারিখ=মার্চ ২০১৯}}\n')
        continue
        
    # 3. Lead sentence
    if 'This is a \'\'\'list of films with' in s:
        output_lines.append("এটি হলো '''[[লাইভ-অ্যাকশন অ্যানিমেশন|লাইভ-অ্যাকশন ও অ্যানিমেশনযুক্ত চলচ্চিত্রের তালিকা]]''', অর্থাৎ এমন সব চলচ্চিত্র যাতে সাধারণত পারস্পরিক মিথস্ক্রিয়াসহ [[লাইভ-অ্যাকশন]] এবং [[অ্যানিমেশন]] উপাদানের সংমিশ্রণ ঘটেছে।\n")
        continue
        
    # 4. Headings
    if s.startswith('='):
        output_lines.append(translate_heading(s) + '\n')
        continue
        
    # 5. Film entries
    if line_idx in entry_by_line:
        entry = entry_by_line[line_idx]
        output_lines.append(format_film_line(entry) + '\n')
        continue
        
    # 6. See also bullets
    if s.startswith('* [[:Category: Television series'):
        output_lines.append('* [[:বিষয়শ্রেণী:লাইভ অ্যাকশন ও অ্যানিমেশনযুক্ত টেলিভিশন ধারাবাহিক]]\n')
        continue
    if s.startswith('* [[List of highest-grossing'):
        output_lines.append('* [[সর্বোচ্চ আয়কারী লাইভ-অ্যাকশন ও অ্যানিমেটেড চলচ্চিত্রের তালিকা]]\n')
        continue
        
    # 7. References tag
    if s == '{{Reflist}}':
        output_lines.append('{{সূত্র তালিকা}}\n')
        continue
        
    # 8. External links bullets
    if s.startswith('* [http://litten.de'):
        output_lines.append('* [http://litten.de/fulltext/mixedpix.pdf আ মিক্সড পিকচার – ১৯৬০ থেকে ১৯৮০-এর দশক পর্যন্ত বিশ্বব্যাপী অঙ্কিত অ্যানিমেশন/লাইভ অ্যাকশন হাইব্রিড (এফ. এস. লিটন রচিত)]\n')
        continue
        
    # 9. Bottom navboxes and categories
    if s == '{{Animation}}':
        output_lines.append('{{অ্যানিমেশন}}\n')
        continue
    if s == '{{Film genres}}':
        output_lines.append('{{চলচ্চিত্রের ধরন}}\n')
        continue
    if s.startswith('{{DEFAULTSORT:'):
        output_lines.append('{{DEFAULTSORT:লাইভ অ্যাকশন ও অ্যানিমেশনযুক্ত চলচ্চিত্রের তালিকা}}\n')
        continue
    if s.startswith('[[Category:Films with live action'):
        output_lines.append('[[বিষয়শ্রেণী:লাইভ অ্যাকশন ও অ্যানিমেশনযুক্ত চলচ্চিত্র|*]]\n')
        continue
    if s.startswith('[[Category:Lists of films]]'):
        output_lines.append('[[বিষয়শ্রেণী:চলচ্চিত্রের তালিকা]]\n')
        continue
    if s.startswith('[[Category:Animation-related lists]]'):
        output_lines.append('[[বিষয়শ্রেণী:অ্যানিমেশন সম্পর্কিত তালিকা]]\n')
        continue
        
    # Empty lines or other lines
    output_lines.append(line)

output_filename = 'লাইভ অ্যাকশন ও অ্যানিমেশনযুক্ত চলচ্চিত্রের তালিকা (বাংলা).txt'
with open(output_filename, 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print(f'Wrote {len(output_lines)} lines to {output_filename}')
