---
name: chinese-bengali-translation
description: Translates Chinese Wikipedia articles, tables, administrative divisions, and Hanzi text into standard Bengali using the local toolkit in চীনা-বাংলা অনুবাদ/.
---

# Chinese to Bengali Translation Skill

Use this skill whenever translating Chinese text, Chinese administrative divisions, Wikipedia tables, or articles into Bengali.

## Toolkit Location
The complete translation tool is located at:
`c:\Users\joysr\Documents\উইকিপিডিয়া অনুবাদ\চীনা-বাংলা অনুবাদ\`

## Core Modules & Capabilities
1. **Transliteration (`transliteration.py`)**:
   - `hanzi_to_bn(hanzi_str)`: Transliterates Chinese Hanzi into standard Bengali using `pypinyin` and the official 416-syllable Bengali Wikipedia Pinyin table.
   - `get_bengali_division_name(hz, en_link, type_str)`: Formulates official Bengali names for counties, districts, cities, banners, and autonomous divisions.
2. **Numbers & Formatting (`number_converter.py`)**:
   - `to_bengali_digits(text)`: Converts 0-9 to ০-৯ while strictly preserving HTML/CSS attributes (`rowspan`, `colspan`, `font-size`, hex colors `#FFC0CB`, etc.).
   - `translate_table_notes(text)`: Translates standard table notes and ethnic parentheticals.
3. **Links & Geographic Names (`links_dictionary.py`)**:
   - `LINK_MAP`: Over 390 curated Wikipedia division and prefecture target-to-label links.
4. **Table Translation (`table_translator.py`)**:
   - Directly parses and translates wikitables into Bengali Wikipedia format.
5. **Full Page Translation (`translate_page.py`)**:
   - `translate_wikipedia_page(input_path, output_path)`: Fully converts raw English/Chinese Wikipedia articles into Bengali Wikipedia format.
