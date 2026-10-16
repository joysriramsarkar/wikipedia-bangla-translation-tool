---
name: russian-bengali-translation
description: Translates Russian Wikipedia articles, districts, federal subjects, Cyrillic text, and tables into standard Bengali using the local toolkit in রুশ-বাংলা অনুবাদ/.
---

# Russian to Bengali Translation Skill

Use this skill whenever translating Russian text, Russian federal subjects, administrative districts (raions), Cyrillic localities, Wikipedia tables, or articles into Bengali.

## Toolkit Location
The complete translation tool is located at:
`c:\\Users\\joysr\\Documents\\উইকিপিডিয়া অনুবাদ\\রুশ-বাংলা অনুবাদ\`

## Core Modules & Capabilities
1. **Transliteration (`cyrillic_transliteration.py`)**:
   - `cyrillic_to_bengali(text)`: Transliterates Cyrillic Russian names into standard Bengali according to `উইকিপিডিয়া:বাংলা ভাষায় রুশ শব্দের প্রতিবর্ণীকরণ`.
   - `romanized_russian_to_bengali(name)`: Transliterates Romanized/English Russian locality names into Bengali.
   - `get_bengali_district_name(cyr_text, en_text)`: Formulates standard Bengali names for Russian districts (`-স্কি জেলা`).
2. **Federal Subjects & Municipal Terms (`federal_subjects.py`)**:
   - `FEDERAL_SUBJECTS_MAP`: Mapping of all 84 Russian federal subjects to Bengali Wikipedia piped links.
   - `translate_admin_center(center_text)`: Translates administrative centers and locality types (স্তানিৎসা, আউল, সেলো, শহুরে ধরনের বসতি, শ্রমিক বসতি, নগর, শহর).
   - `translate_municipal_note(note_text)`: Translates municipal incorporation notes.
3. **Numbers & Formatting (`number_converter.py`)**:
   - `format_bengali_number(num_str)`: Formats population figures with Indian/Bengali comma groupings.
   - `to_bengali_digits(text)`: Converts 0-9 to ০-৯ while strictly protecting HTML/CSS attributes, ref tags, and `{{ru-pop-ref}}` templates.
4. **Table Translation (`table_translator.py`)**:
   - `translate_wikitable(table_text)`: Parses and translates Russian district wikitables.
5. **Full Page Translation (`translate_page.py`)**:
   - `translate_page(content)`: Fully converts entire Russian Wikipedia pages (lead section, all 84 tables, categories, references) into Bengali Wikipedia format.

