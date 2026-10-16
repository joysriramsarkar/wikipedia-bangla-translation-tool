# -*- coding: utf-8 -*-
"""
জার্মান চলচ্চিত্র পাতা পূর্ণাঙ্গ অনুবাদক (German Film List Page Translator)
------------------------------------------------------------------
২০১০-এর দশকের জার্মান চলচ্চিত্রের সম্পূর্ণ তালিকা উইকিপিডিয়া নিবন্ধটি
প্রমিত বাংলা উইকিপিডিয়ার নিয়মাবলি অনুযায়ী অনুবাদ করে।
"""

import os
import re
import sys

# প্যাকেজ ও মডিউল পাথ নিশ্চিতকরণ
curr_dir = os.path.dirname(os.path.abspath(__file__))
if curr_dir not in sys.path:
    sys.path.insert(0, curr_dir)

from table_translator import translate_film_table
from number_converter import to_bengali_digits

def translate_page(input_path: str) -> str:
    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # ১. বাংলা উইকিপিডিয়ার নিয়ম ১: {{Short description}} সম্পূর্ণ মুছে ফেলা
    text = re.sub(r'\{\{Short description\|[^\}]*\}\}\n?', '', text, flags=re.I)
    text = re.sub(r'\{\{force cite load\}\}\n?', '', text, flags=re.I)

    # ২. ভূমিকা ও নেভিগেশনাল হেডার রূপান্তর
    text = text.replace('{{Germany film list}}', '{{জার্মান চলচ্চিত্র তালিকা}}')
    
    lead_en = (
        "This is a list of some of the most notable [[films]] produced in "
        "'''[[Cinema of Germany]]''' in the 2010s.\n\n"
        "For an alphabetical list of articles on German films, see [[:Category:2010s German films]]."
    )
    lead_bn = (
        "এটি ২০১০-এর দশকে '''[[জার্মানির চলচ্চিত্র|জার্মান চলচ্চিত্র শিল্পে]]''' "
        "নির্মিত সবচেয়ে উল্লেখযোগ্য কিছু [[চলচ্চিত্রের তালিকা|চলচ্চিত্রের একটি তালিকা]]।\n\n"
        "জার্মান চলচ্চিত্রের নিবন্ধসমূহের একটি বর্ণানুক্রমিক তালিকার জন্য দেখুন "
        "[[:বিষয়শ্রেণী:২০১০-এর দশকের জার্মান চলচ্চিত্র]]।"
    )
    text = text.replace(lead_en, lead_bn)

    # ৩. সালভিত্তিক অনুচ্ছেদ ও সারণি রূপান্তর
    # ==2010== থেকে ==2019== পর্যন্ত বিভাজন
    sections = re.split(r'(?===201[0-9]==)', text)
    
    out_parts = []
    # ভূমিকার অংশ
    out_parts.append(sections[0].strip())

    bengali_year_digits = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')

    for sec in sections[1:]:
        m = re.match(r'==(201[0-9])==', sec)
        if not m:
            continue
        year_en = m.group(1)
        year_bn = year_en.translate(bengali_year_digits)
        
        # টেবিল অংশ ও পরবর্তী অংশ আলাদা করা
        t_start = sec.find('{|\n' if '{|\n' in sec else '{|')
        t_end = sec.rfind('|}')
        
        if t_start != -1 and t_end != -1:
            table_raw = sec[t_start:t_end+2]
            post_table = sec[t_end+2:].strip()
            
            # সারণি অনুবাদ
            translated_table = translate_film_table(table_raw)
            
            sec_out = f"=={year_bn}==\n{translated_table}"
            if post_table:
                sec_out += f"\n\n{post_table}"
            out_parts.append(sec_out)
        else:
            out_parts.append(sec.replace(f"=={year_en}==", f"=={year_bn}=="))

    full_translated = "\n\n".join(out_parts)

    # ৪. পাদটীকা, তথ্যসূত্র, ডিফল্টসর্ট ও বিষয়শ্রেণী রূপান্তর
    full_translated = full_translated.replace('{{Cinema of Germany}}', '{{জার্মানির চলচ্চিত্র}}')
    full_translated = re.sub(r'==\s*References\s*==', '== তথ্যসূত্র ==', full_translated, flags=re.I)
    full_translated = full_translated.replace('{{Reflist}}', '{{সূত্র তালিকা}}')
    full_translated = full_translated.replace('{{reflist}}', '{{সূত্র তালিকা}}')
    
    full_translated = re.sub(
        r'\{\{DEFAULTSORT:[^\}]+\}\}',
        '{{DEFAULTSORT:২০১০-এর দশকের জার্মান চলচ্চিত্রের তালিকা}}',
        full_translated
    )

    full_translated = full_translated.replace(
        '[[Category:Lists of German films by decade|2010s]]',
        '[[বিষয়শ্রেণী:দশক অনুযায়ী জার্মান চলচ্চিত্রের তালিকা|২০১০]]'
    )
    full_translated = full_translated.replace(
        '[[Category:Lists of 2010s films]]',
        '[[বিষয়শ্রেণী:২০১০-এর দশকের চলচ্চিত্রের তালিকা]]'
    )
    full_translated = full_translated.replace(
        '[[Category:2010s in German cinema|Films]]',
        '[[বিষয়শ্রেণী:জার্মান চলচ্চিত্রে ২০১০-এর দশক|চলচ্চিত্র]]'
    )

    # ৫. সংখ্যা রূপান্তর (শতভাগ বাংলা সংখ্যা নিশ্চিতকরণ)
    final_output = to_bengali_digits(full_translated)

    return final_output


if __name__ == "__main__":
    input_file = os.path.join(curr_dir, "২০১০-এর দশকের জার্মান চলচ্চিত্রের তালিকা.txt")
    output_local = os.path.join(curr_dir, "২০১০-এর দশকের জার্মান চলচ্চিত্রের তালিকা (বাংলা).txt")
    output_root = os.path.abspath(os.path.join(curr_dir, "..", "২০১০-এর দশকের জার্মান চলচ্চিত্রের তালিকা (বাংলা).txt"))

    print("অনুবাদ প্রক্রিয়া শুরু হচ্ছে...")
    result = translate_page(input_file)

    with open(output_local, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"স্থানীয় ফোল্ডারে সংরক্ষিত: {output_local}")

    with open(output_root, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f"রুট ফোল্ডারে সংরক্ষিত: {output_root}")

    print("অনুবাদ সফলভাবে সম্পন্ন হয়েছে!")
