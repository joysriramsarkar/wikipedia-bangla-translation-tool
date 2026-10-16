# -*- coding: utf-8 -*-
"""
চীনা-বাংলা উইকিপিডিয়া পাতা অনুবাদক (Chinese-Bengali Wikipedia Page Translator)
ব্যবহার:
    python translate_page.py <ইনপুট_ফাইল> [আউটপুট_ফাইল]
    অথবা পাইথন কোড থেকে:
    from translate_page import translate_wikipedia_page
    translate_wikipedia_page("ইনপুট.txt", "আউটপুট.txt")
"""
import sys
import os

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from table_translator import translate_main_table, translate_dissolved_table, translate_renamed_table
from number_converter import to_bengali_digits

def translate_wikipedia_text(full_text: str) -> str:
    """সম্পূর্ণ উইকিপিডিয়া পাতা বাংলা উইকিপিডিয়া ফরম্যাটে অনুবাদ করে।"""
    # ভূমিকা প্যারাগ্রাফ অনুবাদ / প্রতিস্থাপন
    intro_old = "This is a list of all [[Counties of China|counties]]"
    intro_new = "এটি চীনের সব [[Counties of China|কাউন্টি]]-র (স্বায়ত্তশাসিত কাউন্টি, স্বায়ত্তশাসিত ব্যানার ও ব্যানারসহ) পাশাপাশি [[county-level city|কাউন্টি-স্তরের শহর]] ({{zh|s=县级市 |p=xianjí shì}}) ও [[district (China)|নগর জেলা]] ({{zh|s=(市辖)区 |p=(shìxiá) qū}})-র তালিকা। তালিকাটি প্রথমে প্রদেশের নাম, তারপর ক্রমবর্ধমান [[administrative division codes of the People's Republic of China|বিভাগ কোড]] অনুযায়ী সাজানো। কিছু নম্বর বাদ গেছে কারণ সেই কোডগুলো এখন অন্য কাউন্টি-স্তরের বিভাগের অংশ হওয়া সাবেক বিভাগ ব্যবহার করত। এই তালিকায় [[Free area of the Republic of China|চীন প্রজাতন্ত্র (ROC) দ্বারা শাসিত কাউন্টিগুলোও]] অন্তর্ভুক্ত, যা PRC তার [[Taiwan Province, People's Republic of China|তাইওয়ান]] ও [[Fujian|ফুচিয়ান]] প্রদেশে দাবি করে।"

    if intro_old in full_text:
        lead_end = full_text.find("== List ==")
        if lead_end == -1:
            lead_end = full_text.find("==List==")
        if lead_end != -1:
            full_text = intro_new + "\n\n" + full_text[lead_end:]

    # সেকশন হেডার অনুবাদ
    full_text = full_text.replace("== List ==", "==তালিকা==")
    full_text = full_text.replace("==List==", "==তালিকা==")
    full_text = full_text.replace("=== Dissolved Counties ===", "=== বিলুপ্ত কাউন্টি ===")
    full_text = full_text.replace("=== Dissolved counties ===", "=== বিলুপ্ত কাউন্টি ===")
    full_text = full_text.replace("=== Name Changes ===", "=== নাম পরিবর্তন ===")
    full_text = full_text.replace("=== Name changes ===", "=== নাম পরিবর্তন ===")
    full_text = full_text.replace("== See also ==", "== আরও দেখুন ==")
    full_text = full_text.replace("== References ==", "== তথ্যসূত্র ==")

    # আরও দেখুন অনুচ্ছেদ
    see_also_en = "* [[List of cities in China]]\n* [[List of prefectures in China]]\n* [[Counties of China]]"
    see_also_bn = "* [[চীনের শহরের তালিকা]]\n* [[চীনের প্রিফেকচারের তালিকা]]\n* [[চীনের কাউন্টি]]"
    full_text = full_text.replace(see_also_en, see_also_bn)

    # তথ্যসূত্র
    full_text = full_text.replace("{{reflist}}", "{{তথ্যসূত্র}}")
    full_text = full_text.replace("{{Reflist}}", "{{তথ্যসূত্র}}")

    # ক্যাটাগরি
    full_text = full_text.replace("[[Category:Lists of county-level divisions of China| ]]", "[[বিষয়শ্রেণী:চীনের প্রশাসনিক উপবিভাগের তালিকা|কাউন্টি]]\n[[বিষয়শ্রেণী:এশিয়ার প্রশাসনিক উপবিভাগ|চীন ৩]]")
    full_text = full_text.replace("[[Category:Territorial disputes of China]]", "[[বিষয়শ্রেণী:চীনের আঞ্চলিক বিরোধ]]")
    full_text = full_text.replace("[[Category:Territorial disputes of Taiwan]]", "[[বিষয়শ্রেণী:তাইওয়ানের আঞ্চলিক বিরোধ]]")
    full_text = full_text.replace("<!--These counties are claimed by the ROC.-->", "<!--এই কাউন্টিগুলো আরওসি দ্বারা দাবিকৃত।-->")

    # সারণিসমূহ বিভাজন ও অনুবাদ
    t1_end = full_text.find('|}\n\n=== বিলুপ্ত কাউন্টি ===')
    if t1_end == -1:
        t1_end = full_text.find('|}\n=== বিলুপ্ত কাউন্টি ===')
    
    if t1_end != -1:
        main_sec = full_text[:t1_end]
        rest = full_text[t1_end:]
        
        # ১. প্রধান সারণি অনুবাদ
        main_table_idx = main_sec.find('{|')
        if main_table_idx != -1:
            pre_table = main_sec[:main_table_idx]
            table_content = main_sec[main_table_idx:]
            translated_main = translate_main_table(table_content)
            main_sec = pre_table + translated_main

        # ২. বিলুপ্ত কাউন্টি সারণি অনুবাদ
        t2_end = rest.find('|}\n\n=== নাম পরিবর্তন ===')
        if t2_end == -1:
            t2_end = rest.find('|}\n=== নাম পরিবর্তন ===')
        
        if t2_end != -1:
            dissolved_sec = rest[:t2_end]
            rest2 = rest[t2_end:]

            d_table_idx = dissolved_sec.find('{|')
            if d_table_idx != -1:
                pre_d = dissolved_sec[:d_table_idx]
                d_table = dissolved_sec[d_table_idx:]
                dissolved_sec = pre_d + translate_dissolved_table(d_table)

            # ৩. নাম পরিবর্তন সারণি অনুবাদ
            t3_end = rest2.find('|}\n\n== আরও দেখুন ==')
            if t3_end == -1:
                t3_end = rest2.find('|}\n== আরও দেখুন ==')
            
            if t3_end != -1:
                renamed_sec = rest2[:t3_end]
                trailer = rest2[t3_end:]

                r_table_idx = renamed_sec.find('{|')
                if r_table_idx != -1:
                    pre_r = renamed_sec[:r_table_idx]
                    r_table = renamed_sec[r_table_idx:]
                    renamed_sec = pre_r + translate_renamed_table(r_table)

                full_text = main_sec + dissolved_sec + renamed_sec + trailer
            else:
                full_text = main_sec + dissolved_sec + rest2
        else:
            full_text = main_sec + rest
    else:
        # যদি একটাই সারণি থাকে
        tbl_idx = full_text.find('{|')
        if tbl_idx != -1:
            pre_tbl = full_text[:tbl_idx]
            tbl_cnt = full_text[tbl_idx:]
            full_text = pre_tbl + translate_main_table(tbl_cnt)

    return full_text

def translate_wikipedia_page(input_path: str, output_path: str = None) -> str:
    """ইনপুট উইকিপাতা পড়ে সম্পূর্ণ অনুবাদ করে আউটপুট ফাইলে লিখে।"""
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"ইনপুট ফাইল পাওয়া যায়নি: {input_path}")

    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    translated = translate_wikipedia_text(content)

    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        print(f"অনুবাদ সফলভাবে সম্পন্ন হয়েছে: {output_path}")

    return translated

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("ব্যবহার: python translate_page.py <ইনপুট_ফাইল> [আউটপুট_ফাইল]")
        sys.exit(1)

    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace('.txt', ' (অনূদিত).txt')
    translate_wikipedia_page(inp, out)
