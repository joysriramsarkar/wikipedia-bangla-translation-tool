# Common Utilities

Shared utilities for all language translation modules.

## Modules

- `bengali_utils.py` - Bengali text processing (digits, nukta normalization, rules)
- `wikitext_utils.py` - Wikitext formatting helpers

## Usage

```python
from common import bengali_utils

text = "In 2010, r. 1202"
text = bengali_utils.to_bengali_digits(text)
text = bengali_utils.fix_r_reigned(text)
print(text)  # In ২০১০, শাসনকাল: ১২০২
```
