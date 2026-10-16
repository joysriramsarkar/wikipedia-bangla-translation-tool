# -*- coding: utf-8 -*-
import json
import re

with open('clean_film_titles.json', encoding='utf-8') as f:
    titles = json.load(f)

with open('notes_translations.json', encoding='utf-8') as f:
    notes_dict = json.load(f)

# Sort note keys by length descending to match longest phrases first
sorted_keys = sorted(notes_dict.keys(), key=len, reverse=True)

untranslated_segments = []

def translate_trailer(trailer):
    if not trailer:
        return ""
    
    # Extract references and replace with placeholders
    refs = []
    def save_ref(m):
        refs.append(m.group(0))
        return f"__REF_{len(refs)-1}__"
    
    # Match both <ref>...</ref> and <ref ... />
    text = re.sub(r'<ref[^>]*>.*?</ref>', save_ref, trailer, flags=re.DOTALL)
    text = re.sub(r'<ref[^>]*/>', save_ref, text)
    
    # Strip whitespace
    text = text.strip()
    if not text:
        # Only refs
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
    
    # Check if exact match in notes_dict
    if text in notes_dict:
        translated_text = notes_dict[text]
    else:
        # Replace known note fragments
        translated_text = text
        for k in sorted_keys:
            if k in translated_text:
                translated_text = translated_text.replace(k, notes_dict[k])
        
        # If any English characters remain (excluding placeholder __REF_...__)
        clean_check = re.sub(r'__REF_\d+__', '', translated_text)
        if re.search(r'[A-Za-z]', clean_check):
            untranslated_segments.append((trailer, clean_check))
            
    # Restore references
    for i, r in enumerate(refs):
        translated_text = translated_text.replace(f"__REF_{i}__", r)
        
    return translated_text

test_results = []
for t in titles:
    raw_tr = t['trailer']
    bn_tr = translate_trailer(raw_tr)
    test_results.append({
        'line': t['line'],
        'raw': raw_tr,
        'bn': bn_tr
    })

print(f'Tested {len(test_results)} trailers.')
print(f'Untranslated segments count: {len(untranslated_segments)}')
if untranslated_segments:
    print('Sample untranslated:')
    for orig, un in untranslated_segments[:10]:
        print(f'ORIG: {orig}\nUNTRANSLATED: {un}\n---')
