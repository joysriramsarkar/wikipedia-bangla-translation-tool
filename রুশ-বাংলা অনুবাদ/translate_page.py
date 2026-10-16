# -*- coding: utf-8 -*-
"""
রাশিয়ার জেলা পূর্ণাঙ্গ পাতা অনুবাদক (Russian Districts Full Page Translator)
'রাশিয়ার জেলা.txt' ফাইলটি প্রমিত বাংলা উইকিপিডিয়া ফরম্যাটে অনুবাদ করে 'রাশিয়ার জেলা (বাংলা).txt' তৈরি করে।
"""
import os
import sys
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from federal_subjects import FEDERAL_SUBJECTS_MAP
from table_translator import translate_wikitable

LEAD_TRANSLATION = """এটি '''[[districts of Russia|রাশিয়ার জেলাসমূহের একটি তালিকা]]'''। একটি জেলা ([[raion|রায়োন]]) হলো [[Russia|রাশিয়ার]] একটি [[federal subjects of Russia|যুক্তরাষ্ট্রীয় বিষয়ের]] প্রশাসনিক ও পৌর বিভাগ।

[[subdivisions of Russia#Administrative divisions|প্রশাসনিক বিভাগের কাঠামোর]] মধ্যে, প্রশাসনিক জেলাগুলো [[city of federal subject significance|যুক্তরাষ্ট্রীয় তাৎপর্যপূর্ণ শহরের]] সমমানের মর্যাদাসম্পন্ন এবং এগুলোকে পরবর্তীতে [[town of district significance|জেলা তাৎপর্যপূর্ণ শহর]], [[urban-type settlement#Administrative division|জেলা তাৎপর্যপূর্ণ শহুরে ধরনের বসতি]] এবং [[selsoviet|সেলসোভেতে]] বিভক্ত করা হতে পারে; তবে এই সত্তাগুলোর সুনির্দিষ্ট পরিভাষা এক যুক্তরাষ্ট্রীয় বিষয় থেকে অন্যটিতে ভিন্ন হতে পারে।

[[subdivisions of Russia#Municipal divisions|পৌর বিভাগের কাঠামোর]] মধ্যে, পৌর জেলাগুলো নগর ওক্রুগের সমমানের মর্যাদাসম্পন্ন এবং এগুলো শহুরে বসতি, গ্রামীণ বসতি অথবা উভয়টিতে উপবিভক্ত। সাধারণত বিদ্যমান প্রশাসনিক জেলার সীমানার ভেতরেই পৌর জেলাগুলো গঠিত হয়, যদিও বাস্তবে এই নিয়মের কিছু ব্যতিক্রম রয়েছে।

রাশিয়ার প্রধান প্রধান শহরগুলো [[city district|নগর জেলায়]] বিভক্ত। পরিভাষাগত মিল থাকা সত্ত্বেও এগুলো ভিন্ন প্রকৃতির বিভাগ এবং তা এই নিবন্ধের আওতাভুক্ত নয়।

রাশিয়ার অন্যান্য [[federal subjects of Russia|যুক্তরাষ্ট্রীয় বিষয়ের]] মতো নয়, বরং [[federal cities of Russia|যুক্তরাষ্ট্রীয় শহরগুলোর]] প্রশাসনিক-আঞ্চলিক কাঠামোর এক অনন্য রূপ রয়েছে। বিশেষ করে যুক্তরাষ্ট্রীয় শহর [[Moscow|মস্কোর]] প্রশাসনিক-আঞ্চলিক বিভাগের মধ্যে [[administrative divisions of Moscow|জেলা এবং বসতিসমূহ]] অন্তর্ভুক্ত, যেগুলো আবার প্রশাসনিক ওক্রুগে বিভক্ত। নিচে কেবল জেলাগুলোই অন্তর্ভুক্ত করা হয়েছে। তবে মস্কো কিংবা [[Saint Petersburg|সেন্ট পিটার্সবার্গ]] কোনোটির জেলাই কোনো বসতি এলাকা অন্তর্ভুক্ত না করায় এগুলোর কোনো প্রশাসনিক কেন্দ্র নেই।

[[Republic of Crimea (Russia)|ক্রিমিয়া প্রজাতন্ত্র]] হলো [[Crimean Peninsula|ক্রিমীয় উপদ্বীপের]] ভূখণ্ডে গঠিত রাশিয়ার একটি যুক্তরাষ্ট্রীয় বিষয়, যা রাশিয়া ও [[Ukraine|ইউক্রেনের]] মধ্যে বিরোধপূর্ণ। রাশিয়ার আইনি কাঠামোর অধীনে [[Autonomous Republic of Crimea|স্বায়ত্তশাসিত ক্রিমিয়া প্রজাতন্ত্রের]] (ইউক্রেনের একটি প্রশাসনিক বিভাগ) জেলাগুলো এখনো প্রচলিত রয়েছে এবং নিচের সারণীগুলোতে অন্তর্ভুক্ত করা হয়েছে। যুক্তরাষ্ট্রীয় শহর [[Sevastopol|সেভাস্তোপোল]]-ও এই উপদ্বীপে অবস্থিত এবং এর জেলাগুলোর মর্যাদা মস্কো ও সেন্ট পিটার্সবার্গের জেলাগুলোর অনুরূপ।

২০১৪ সালের হিসাব অনুযায়ী, মস্কো, সেন্ট পিটার্সবার্গ এবং সেভাস্তোপোল বাদ দিয়ে রাশিয়ায় ১,৮৭৩টি প্রশাসনিক জেলা (ক্রিমিয়া প্রজাতন্ত্রের ১৪টি সহ) এবং ১,৮২৩টি পৌর জেলা (ক্রিমিয়া প্রজাতন্ত্রের ১৪টি সহ) রয়েছে। এই সমস্ত জেলার একটি করে [[administrative center|প্রশাসনিক কেন্দ্র]] রয়েছে, যা সাধারণত উভয় প্রশাসনিক ও পৌর সত্তার জন্য একই এলাকা।

==প্রশাসনিক জেলাসমূহ==
নিচের সারণীগুলোতে যুক্তরাষ্ট্রীয় বিষয়গুলোর প্রশাসনিক জেলাসমূহ তালিকাভুক্ত করা হয়েছে এবং এগুলোতে তাদের প্রশাসনিক কেন্দ্র ও জনসংখ্যার তথ্য অন্তর্ভুক্ত রয়েছে। অন্যথায় উল্লেখ না থাকলে, প্রশাসনিক জেলাগুলো পৌরগতভাবে পৌর জেলা হিসেবে নিগমিত এবং উভয় সত্তার সীমানা অভিন্ন।"""

def translate_page(content: str) -> str:
    """সম্পূর্ণ উইকিটেক্সট পাতা বাংলায় অনুবাদ করে।"""
    # ১. ভূমিকা অংশ প্রতিস্থাপন (প্রথম === সেকশনের পূর্ব পর্যন্ত)
    idx_first_sec = content.find('===[[')
    if idx_first_sec != -1:
        rest = content[idx_first_sec:]
    else:
        rest = content

    # ২. সেকশন শিরোনাম প্রতিস্থাপন
    for en_subj, bn_subj in FEDERAL_SUBJECTS_MAP.items():
        rest = rest.replace(f'==={en_subj}===', f'==={bn_subj}===')

    # ৩. প্রতিটি টেবিল খুঁজে বের করে অনুবাদ করা
    def repl_tbl(match):
        orig_tbl = match.group(0)
        return translate_wikitable(orig_tbl)

    rest = re.sub(r'\{\| class="wikitable sortable".*?\n\|\}', repl_tbl, rest, flags=re.DOTALL)

    # ৪. তথ্যসূত্র এবং বিষয়শ্রেণী অনুবাদ
    rest = rest.replace('==References==', '==তথ্যসূত্র==')
    rest = rest.replace('[[Category:Districts of Russia]]', '[[বিষয়শ্রেণী:রাশিয়ার জেলা]]')
    rest = rest.replace('[[Category:Municipalities of Russia]]', '[[বিষয়শ্রেণী:রাশিয়ার পৌরসভা]]')

    # ৫. সম্পূর্ণ পৃষ্ঠা একত্রিতকরণ
    full_translated = LEAD_TRANSLATION + '\n\n' + rest
    return full_translated

def main():
    source_path = os.path.join(_current_dir, 'রাশিয়ার জেলা.txt')
    output_path = os.path.join(_current_dir, 'রাশিয়ার জেলা (বাংলা).txt')
    root_output_path = os.path.abspath(os.path.join(_current_dir, '..', 'রাশিয়ার জেলা (বাংলা).txt'))

    print(f"উৎস ফাইল পড়া হচ্ছে: {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        source_text = f.read()

    print("পৃষ্ঠা অনুবাদ করা হচ্ছে...")
    translated_text = translate_page(source_text)

    print(f"অনূদিত ফাইল সংরক্ষণ করা হচ্ছে: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print(f"ওয়ার্কস্পেস রুটেও অনুলিপি সংরক্ষণ করা হচ্ছে: {root_output_path}")
    with open(root_output_path, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    print("অনুবাদ সফলভাবে সম্পন্ন হয়েছে!")

if __name__ == '__main__':
    main()
