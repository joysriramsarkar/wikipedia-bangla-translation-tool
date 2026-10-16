---
name: japanese-bengali-translation
description: Translates Japanese Wikipedia articles, biographies, Japanese names, terms, Romaji, and tables into standard Bengali using the local toolkit in জাপানি-বাংলা অনুবাদ/.
---

# Japanese to Bengali Translation Skill

Use this skill whenever translating Japanese text, Japanese people/biographies, emperors, shōguns, prime ministers, terms, Wikipedia tables, or articles into Bengali.

## Toolkit Location
The complete translation tool is located at:
`c:\\Users\\joysr\\Documents\\উইকিপিডিয়া অনুবাদ\\জাপানি-বাংলা অনুবাদ\`

## Core Modules & Capabilities
1. **Transliteration (`japanese_transliteration.py`)**:
   - `transliterate_japanese_word(w)`: Transliterates Japanese words/Romaji into standard Bengali according to `উইকিপিডিয়া:বাংলা ভাষায় জাপানি শব্দের প্রতিবর্ণীকরণ` (`সাহায্য:আধ্বব/জাপানি`).
   - `transliterate_japanese_name(name)`: Transliterates full Japanese personal names and titles.
   - `get_bengali_japanese_name(target, label)`: Formulates standard Bengali names from Wikipedia links or dictionary lookups.
2. **Links & Curated Dictionary (`links_dictionary.py`)**:
   - `JAPANESE_LINKS_MAP`: Over 280 curated Wikipedia mappings for famous Japanese people, emperors, prime ministers, eras, books, and companies.
3. **Numbers & Dates (`number_converter.py`)**:
   - `to_bengali_digits(text)`: Converts 0-9 to ০-৯, formats historical eras (BC, BCE, AD, CE), months, and years while protecting MediaWiki templates, images (`[[File:...]]`), and `<ref>` tags.
4. **Table Translation (`table_translator.py`)**:
   - Directly parses and translates complex wikitables (Emperors of Japan, Tokugawa shoguns, Prime Ministers of all eras) into Bengali.
   - Enforces strict MediaWiki row formatting: each table row separator (`|-`) must start on a separate line (`\n|-`) to prevent table cell collapse.
5. **Full Page Translation (`translate_page.py`)**:
   - `translate_page(content)`: Fully converts entire Wikipedia articles into Bengali Wikipedia format.

## Linguistic & Phonetic Guidelines
- **Word-initial `ts` / `tsu` (つ, ツ)**:
  - In Bengali orthography and phonotactics, no word can begin with `ৎ` (খণ্ড-ত) because it cannot be pronounced at the start of a word.
  - Foreign /ts/ at word onset is transliterated with `স` / `সু` (e.g. *tsunami* $\to$ সুনামি, *Tsunesaburō Makiguchi* $\to$ সুনেসাবুরো মাকিগুচি, *Yukio Tsuda* $\to$ ইউকিও সুদা, *Tsushima* $\to$ সুশিমা, *Tsubasa* $\to$ সুবাসা).
  - Medial `ts` preceded by a vowel retains standard conjuncts (e.g. *Matsuoka* $\to$ মাৎসুওকা, *Katsura* $\to$ কাৎসুরা).

