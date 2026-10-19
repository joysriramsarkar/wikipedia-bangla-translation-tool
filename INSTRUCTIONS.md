# উইকিপিডিয়া অনুবাদ টুলকিট - ব্যবহারের নির্দেশনা

## ভূমিকা

এই টুলকিটে ৫টি ভাষার (চীনা, জাপানি, রুশ, জার্মান, ইংরেজি) উইকিপিডিয়া বিষয়বস্তু বাংলা উইকিপিডিয়ার নিয়ম অনুযায়ী অনুবাদ করার জন্য প্রয়োজনীয় টুলস রয়েছে।

## কাঠামোর ব্যাখ্যা

```
উইকিপিডিয়া অনুবাদ/
├── common/                    # সকল মডিউলের জন্য সাধারণ ইউটিলিটি
│   ├── bengali_utils.py      # বাংলা সংখ্যা, 'r.' → 'শাসনকাল:', ইউনিকোড নরমালাইজেশন
│   ├── wikitext_utils.py     # উইকিটেক্সট ফরম্যাটিং
│   └── __init__.py
├── চীনা-বাংলা অনুবাদ/        # চীনা → বাংলা অনুবাদ টুলস
├── জাপানি-বাংলা অনুবাদ/      # জাপানি → বাংলা অনুবাদ টুলস
├── রুশ-বাংলা অনুবাদ/          # রুশ → বাংলা অনুবাদ টুলস
├── জার্মান-বাংলা অনুবাদ/      # জার্মান → বাংলা অনুবাদ টুলস
├── ইংরেজি-বাংলা অনুবাদ/      # ইংরেজি → বাংলা অনুবাদ টুলস
├── .agents/                   # AI agent rules ও skills
├── tests/                    # টেস্ট ফাইল
├── cli.py                    # CLI ইন্টারফেস
└── README.md                 # মূল README
```

## common/ এর ফাংশনসমূহ

### bengali_utils.py
- `to_bengali_digits(text)` - ইংরেজি সংখ্যা → বাংলা সংখ্যা (০-৯), সর্বত্র
- `to_bengali_digits_safe(text)` - শুধু দৃশ্যমান অঙ্ক বাংলা; URL, ফাইলনাম, টেমপ্লেট প্যারামিটার, coord, ISBN অক্ষত
- `strip_technical_spans(text)` - যাচাইয়ের আগে টেকনিক্যাল অংশ আড়াল করা
- `fix_r_reigned(text)` - `r. 1202` → `শাসনকাল: ১২০২`
- `normalize_nukta_chars(text)` - `য+়` → `য়`, `ড+়` → `ড়`, `ঢ+়` → `ঢ়`
- `replace_short_desc(text)` - `{{Short description}}` মুছে ফেলা
- `fix_en_dash_years(text)` - হাইফেন ঠিক করা
- `to_bengali_text(text)` - সকল নিয়ম একসাথে প্রয়োগ

## ব্যবহার

### ১) সরাসরি ইম্পোর্ট করে ব্যবহার
```python
# জার্মান থেকে বাংলা - নাম প্রতিবর্ণীকরণ
import sys
sys.path.insert(0, r'জার্মান-বাংলা অনুবাদ')
from german_transliteration import transliterate_person_name

print(transliterate_person_name("Zimmermann"))  # সিমারমান
```

### ২) common ইউটিলিটি ব্যবহার
```python
from common import bengali_utils

text = "From 2010-2019, r. 1202"
print(bengali_utils.to_bengali_text(text))
# From ২০১০–২০১৯, শাসনকাল: ১২০২
```

### ৩) CLI ব্যবহার
```bash
python cli.py info
python cli.py german --input input.txt --output output.txt
```

### ৪) ইউনিফাইড API
```python
from wikipedia_translation_toolkit import WikipediaTranslator

wt = WikipediaTranslator()
wt.translate_german('input.txt', 'output.txt')
```

## টেস্ট চালানো
```bash
python run_all_tests.py
# pytest না থাকলেও চলবে:
python run_all_tests.py --no-pytest
# অথবা (pytest ইনস্টল থাকলে)
python -m pytest tests/ -v
```

## মূল নীতিমালা (সংক্ষিপ্ত)

১. `{{Short description}}` মুছে ফেলতে হবে
২. সকল সংখ্যা বাংলা (`০-৯`) করতে হবে  
৩. বাংলা বর্ণানুক্রমে সাজাতে হবে (`অ-হ`)
৪. শব্দের শুরুতে 'ৎ' নিষিদ্ধ (ts/z → স)
৫. `r. YYYY` → `শাসনকাল: YYYY`
৬. সারণির কলাম সমতা রাখতে হবে
৭. প্রি-কম্পোজড ইউনিকোড বর্ণ ব্যবহার (`য়`, `ড়`, `ঢ়`)

বিস্তারিত জানতে দেখুন: `বাংলা_উইকিপিডিয়া_সম্পাদনা_নির্দেশিকা.md`
