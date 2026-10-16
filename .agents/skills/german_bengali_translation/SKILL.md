---
name: german-bengali-translation
description: Translates German Wikipedia articles, films, biographies, German names, terms, and tables into standard Bengali using the local toolkit in জার্মান-বাংলা অনুবাদ/.
---

# German to Bengali Translation Skill

Use this skill whenever translating German text, German cinema/film lists, directors, actors, places, Wikipedia tables, or articles into Bengali.

## Toolkit Location
The complete translation tool is located at:
`c:\\Users\\joysr\\Documents\\উইকিপিডিয়া অনুবাদ\\জার্মান-বাংলা অনুবাদ\`

## Core Modules & Capabilities
1. **Transliteration (`german_transliteration.py`)**:
   - `transliterate_german_word(w)`: Transliterates German words into standard Bengali according to German phonology and standard Bengali Wikipedia transliteration guidelines.
   - `transliterate_german_name(name)`: Transliterates full German personal names and surnames.
   - Initial `Z-` is strictly transliterated as `স-` (e.g., *Zimmermann* $\to$ সিমারমান, *Zengel* $\to$ সেঙ্গেল, *Zirner* $\to$ সিরনার). Medial/final `-z` / `-tz` transliterated as `-ৎস` (e.g., *Moritz* $\to$ মরিৎস, *Fitz* $\to$ ফিৎস).
2. **Film Title Translation (`film_title_translator.py`)**:
   - Translates German film titles and styles them with Bengali script followed by authentic German titles in parentheses: `''[[Target|বাংলা শিরোনাম]]'' (''মূল জার্মান নাম'')` or `''{{ill|Target|de|...|lt=বাংলা শিরোনাম}}'' (''মূল জার্মান নাম'')`.
3. **Links & Curated Dictionary (`links_dictionary.py`)**:
   - Curated mappings for prominent German directors, actors, historical personalities, and places.
4. **Numbers & Dates (`number_converter.py`)**:
   - `to_bengali_digits(text)`: Converts 0-9 to ০-৯, formats months, years, and dates into standard Bengali while protecting MediaWiki templates and `<ref>` tags.
5. **Table Translation (`table_translator.py`)**:
   - Parses wikitables, maps film headers (`! শিরোনাম !! পরিচালক !! অভিনয়ে !! ধরন !! মন্তব্য`), translates film genres, and balances all 5 columns with `&nbsp;` to prevent broken empty boxes.
6. **Full Page Translation (`translate_page.py`)**:
   - Converts entire German cinema or biography articles into Bengali Wikipedia format.

