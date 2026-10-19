# Wikipedia Translation Toolkit

<p align="center">
  <a href="README.md">বাংলা</a> | <b>English</b> | <a href="README_ZH.md">中文</a>
</p>

A unified, production-grade Python translation and transliteration framework for converting Wikipedia articles, infoboxes, wikitables, and structured lists from **Chinese, Japanese, Russian, German, and English** into Standard Bengali, strictly enforcing the **13 Mandatory Rules of Bengali Wikipedia**.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
- [Language Translation Modules](#-language-translation-modules)
- [Common Components & Architecture](#-common-components--architecture)
- [Content Translation (CX) Post-Processor & Web Dashboard](#-content-translation-cx-post-processor--web-dashboard)
- [The 13 Mandatory Rules of Bengali Wikipedia](#-the-13-mandatory-rules-of-bengali-wikipedia)
- [Installation & Setup](#-installation--setup)
- [Usage & Quickstart](#-usage--quickstart)
  - [1. Command-Line Interface (CLI)](#1-command-line-interface-cli)
  - [2. Python API Usage](#2-python-api-usage)
  - [3. Running the Web Dashboard](#3-running-the-web-dashboard)
  - [4. All-in-One Demo](#4-all-in-one-demo)
- [Testing & Validation](#-testing--validation)
- [Repository Structure](#-repository-structure)
- [License](#-license)

---

## ✨ Key Features

- **Multi-Language Transliteration Engines:** Dedicated linguistic engines for Chinese (Hanzi/Pinyin), Japanese (Kanji/Hepburn/Kunrei-shiki), Russian (Cyrillic phonetics), German (phonology, Rule 4 $Z \to S$), and English.
- **100% Compliance with Bengali Wikipedia Policies:** Automatic enforcement of all 13 official editing rules (100% Bengali digits `০-৯`, no word-initial `ৎ`, pre-composed nukta letters `য়, ড়, ঢ়`, `km²` $\to$ `বর্গকিমি`, removal of English maintenance templates).
- **Wikitable Balancing & Auto-Alignment:** Robust parsing of MediaWiki tables, automatic padding with `&nbsp;` for missing cells to prevent broken table grids.
- **Visual Web Dashboard:** Built-in web editor and management dashboard (`http://127.0.0.1:8765/dashboard`) with dark-mode UI, live draft processing, and instant policy validation.
- **Comprehensive Test Suite:** 89 automated unit tests providing complete test coverage across all languages and processing pipelines.

---

## 🌐 Language Translation Modules

| Language | Directory | Core Features & Implementation |
|---|---|---|
| **Chinese → Bengali** | [`চীনা-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/চীনা-বাংলা%20অনুবাদ/) | • Pinyin syllable mapping and Hanzi-to-Bengali transliteration (`transliteration.py`)<br>• China administrative division codes, counties, and prefecture dictionaries (`links_dictionary.py`)<br>• District table and page translator (`table_translator.py`, `translate_page.py`) |
| **Japanese → Bengali** | [`জাপানি-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/জাপানি-বাংলা%20অনুবাদ/) | • Hepburn and Kunrei-shiki Romaji phonetics (`japanese_transliteration.py`)<br>• 3-tier formatting for Emperors, Shoguns, and Prime Ministers (`prime_minister_notes.py`)<br>• Table translator and Japanese date/number parser (`table_translator.py`, `number_converter.py`) |
| **Russian → Bengali** | [`রুশ-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/রুশ-বাংলা%20অনুবাদ/) | • Cyrillic phonetic transliteration into standard Bengali (`cyrillic_transliteration.py`)<br>• Dictionary of all 85 Russian Federal Subjects and administrative districts (`federal_subjects.py`)<br>• Russian district table and page translator (`table_translator.py`, `translate_page.py`) |
| **German → Bengali** | [`জার্মান-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/জার্মান-বাংলা%20অনুবাদ/) | • German phonology engine (e.g., $Z \to S$, Zimmermann $\to$ সিমারমান)<br>• Bilingual film title formatting: `''[[Link\|Bengali title]]'' (''Original title'')`<br>• Dictionaries for film festivals, genres, directors, and actors (`film_title_translator.py`) |
| **English → Bengali** | [`ইংরেজি-বাংলা অনুবাদ/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/ইংরেজি-বাংলা%20অনুবাদ/) | • Full wikitext article parsing, heading translation, infobox processing (`translate_page.py`)<br>• Filmography, literature, and biography table translator (`table_translator.py`)<br>• Ordinals (1st $\to$ ১ম, 2nd $\to$ ২য়) and large number converter (`number_converter.py`) |

---

## 🛠️ Common Components & Architecture

- [`common/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/common/):
  - `bengali_utils.py`: Centralized digit conversion (`0-9` $\to$ `০-৯`), nukta normalization, reign date transformation (`r. [year]` $\to$ `শাসনকাল: [বছর]`), unit superscripts removal (`km²` $\to$ `বর্গকিমি`), and maintenance template eradication (`{{Use British English}}`, `{{Short description}}`).
- [`cx_postprocess/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/cx_postprocess/):
  - `pipeline.py`: Wikipedia Content Translation (CX) post-processing and sanitization engine.
  - `server.py`: Local HTTP web server providing REST APIs for dashboard operations.
  - `draft_manager.py`: Versioned draft storage, retrieval, and change management.
  - `dashboard.html`: Reactive web dashboard for visual editing and live translation review.
- [`scripts/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/scripts/):
  - `fix_nukta.py`: Converts decomposed combining nuktas to pre-composed Unicode characters.
  - `check_digits.py`: Scans text and wikitables for lingering ASCII digits.
  - `sort_bengali.py`: Sorts items strictly according to standard Bengali alphabetical order (`অ-হ`).
  - `verify_table.py`: Validates column counts and table balance in wikitables.
  - `stats.py`: Measures translation progress and token counts.
- [`wikitext_templates/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/wikitext_templates/):
  - Standard Bengali Wikipedia templates for infoboxes (`তথ্যছক ব্যক্তি`, `তথ্যছক বসতি`, `তথ্যছক চলচ্চিত্র`) and tables.
- [`archive/`](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/archive/):
  - Organized archive of completed article data, raw files, and utility scripts (Mongolia, Libya, Tanzania, Minas Gerais).

---

## 🖥️ Content Translation (CX) Post-Processor & Web Dashboard

The toolkit features a local web-based editing and post-processing studio.

```bash
# Launch the dashboard server:
python cx_postprocess/server.py
```
Open your browser and navigate to: **`http://127.0.0.1:8765/dashboard`**

### Dashboard Capabilities:
1. **Live Post-Processing:** Paste raw drafts directly from Wikipedia Content Translation (CX) and apply all 13 rules in one click.
2. **Infobox & Table Sanitizer:** Auto-formats infobox parameters and prevents broken table markup.
3. **Draft Storage:** Save, restore, and organize ongoing translations locally.
4. **Instant Policy Validator:** Live visual inspection and warning alerts for any rule violations.

---

## 📜 The 13 Mandatory Rules of Bengali Wikipedia

All modules strictly adhere to the following rules:

1. **No `{{Short description}}`:** Never allowed on Bengali Wikipedia (descriptions are pulled dynamically from Wikidata).
2. **100% Bengali Digits:** All visible years, dates, pages, and statistics must use standard Bengali digits (`০-৯`).
3. **Bengali Alphabetical Sorting:** Lists must strictly follow standard Bengali collation order (`অ-হ`), never English A-Z.
4. **No Word-Initial 'ৎ':** Bengali words cannot start with 'ৎ' (e.g., `tsunami` $\to$ `সুনামি`, `Zimmermann` $\to$ `সিমারমান`); 'ৎস' is permitted internally or word-finally.
5. **Reign 'r.' Translation:** Regnal abbreviations like `r. 1200` must be transformed into `শাসনকাল: ১২০০`.
6. **Wikitable Column Balance:** Row column counts must match headers; empty cells must be padded with `&nbsp;`.
7. **Heads of State 3-Tier Format:** (1) Bengali name with wikilink, (2) Native script (Kanji, Cyrillic), (3) Phonetic transliteration with lifespan.
8. **Defaultsort & Categories:** `{{DEFAULTSORT:বাংলা নাম}}` and all categories must be in standard Bengali.
9. **Filmography Table Format:** Headers `! শিরোনাম !! পরিচালক !! অভিনয়ে !! ধরন !! মন্তব্য` with 100% Bengali transliteration for cast and crew.
10. **Bilingual Film Titles:** `''[[Link|Bengali Title]]'' (''Original Title'')`.
11. **Pre-composed Unicode Characters:** Always use pre-composed `য়` (U+09DF), `ড়` (U+09DC), `ঢ়` (U+09DD), never decomposed nukta forms (`য` + `়`).
12. **Unit Superscript Policy:** Latin symbols like `km²` or `কিমি²` are prohibited; use `বর্গকিমি` or `কিমি<sup>২</sup>`.
13. **Removal of English Maintenance Templates:** Strip obsolete templates such as `{{Use British English}}`, `{{Use dmy dates}}`, etc.

---

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/example/wikipedia-translation-toolkit.git
cd "উইকিপিডিয়া অনুবাদ"
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## ⚡ Usage & Quickstart

### 1. Command-Line Interface (CLI)

```bash
# View system info and supported languages:
python cli.py info

# Translate an English Wikipedia article:
python cli.py english -i input_article.txt -o translated_article.txt

# Translate only a German wikitable:
python cli.py german -i film_table.txt -o bn_table.txt --table-only

# Validate a translated draft against the 13 rules:
python cli.py english -i translated_draft.txt --check-rules
```

### 2. Python API Usage

```python
from wikipedia_translation_toolkit import WikipediaTranslator

translator = WikipediaTranslator()

# Translate wikitext from any supported language
wikitext = """
{{Short description|American actress}}
{{Use British English}}
== Early life ==
She was born in 1995 and lived in an area of 500 km².
"""

translated = translator.translate_text(wikitext, source_lang="english")
print(translated)

# Validate against Bengali Wikipedia policies
report = translator.validate_rules(translated)
if report["valid"]:
    print("✅ All rules passed!")
else:
    print("Issues found:", report["issues"])
```

### 3. All-in-One Demo
Run the comprehensive test demo showcasing all 7 subsystem components:
```bash
python examples/demo.py
```

---

## 🧪 Testing & Validation

Run the complete test suite (89 automated tests):
```bash
python run_all_tests.py
# Falls back to a stdlib runner when pytest is not installed:
python run_all_tests.py --no-pytest
# Or using pytest directly:
pytest tests/ -v
```

Install the optional development dependencies for pytest:
```bash
pip install -r requirements-dev.txt
```

Clean build caches and pytest artifacts:
```bash
python clean.py
```

---

## 📂 Repository Structure

```text
উইকিপিডিয়া অনুবাদ/
├── common/                         # Core Bengali utilities & normalizers
├── cx_postprocess/                 # CX post-processor engine & web dashboard
├── scripts/                        # Verification, sorting, and digit scripts
├── wikitext_templates/             # Standard infobox & table wikitext templates
├── examples/                       # Usage examples & all-in-one demo.py
├── docs/                           # Architecture & user documentation
├── tests/                          # 89-test automated unit test suite
├── archive/                        # Completed article data & script archives
├── চীনা-বাংলা অনুবাদ/             # Chinese-to-Bengali translation engine
├── জাপানি-বাংলা অনুবাদ/           # Japanese-to-Bengali translation engine
├── রুশ-বাংলা অনুবাদ/               # Russian-to-Bengali translation engine
├── জার্মান-বাংলা অনুবাদ/            # German-to-Bengali translation engine
├── ইংরেজি-বাংলা অনুবাদ/            # English-to-Bengali translation engine
├── wikipedia_translation_toolkit.py # Unified Python library interface
├── cli.py                          # Command-line interface
├── clean.py                        # Cache cleanup utility
├── run_all_tests.py                # Test runner script
├── README.md                       # Primary README (Bengali)
├── README_EN.md                    # English README
└── README_ZH.md                    # Chinese README
```

---

## 📄 License
This project is open-source under the [MIT License](file:///c:/Users/joysr/Documents/উইকিপিডিয়া%20অনুবাদ/LICENSE).
