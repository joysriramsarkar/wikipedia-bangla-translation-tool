# Common Utilities

Shared utilities for all language translation modules.

## Modules

- `bengali_utils.py` — Bengali text processing (digits, nukta normalization, rules)
- `wikitext_utils.py` — Wikitext formatting helpers and table structure analysis

## Safe digit conversion

`to_bengali_digits()` converts every ASCII digit, including digits inside URLs
and file names. For wikitext always prefer `to_bengali_digits_safe()`:

```python
from common.bengali_utils import to_bengali_digits_safe

src = '[[File:Photo 2020.jpg|200px|ছবি 2020]] {{cite web|url=https://x.com/2020|title=2020}}'
print(to_bengali_digits_safe(src))
# [[File:Photo 2020.jpg|200px|ছবি ২০২০]] {{cite web|url=https://x.com/2020|title=২০২০}}
```

Protected spans: `<...>` tags and attributes, URLs, `[[File:...]]` targets,
template parameter keys (`|group1 =`, `{{{1|...}}}`), `{{coord}}`,
ISBN/DOI/PMID, `NNNpx` sizes, CSS colours and HTML entities.

`strip_technical_spans(text)` blanks those spans; validators use it so a URL's
digits are not reported as leftover English digits.

## Usage

```python
from common import bengali_utils, wikitext_utils

text = "In 2010, r. 1202"
text = bengali_utils.to_bengali_text(text)
print(text)  # In ২০১০, শাসনকাল: ১২০২

report = wikitext_utils.analyze_wikitable(wikitext)
for issue in report['issues']:
    print(issue['type'], issue['line'], issue['message'])
```

`analyze_wikitable()` checks Rule 6: every row has the same number of cells as
the header, and empty cells are reported because they need `&nbsp;`.
