# -*- coding: utf-8 -*-
import sys
import re
sys.path.insert(0, 'c:/Users/joysr/Documents/উইকিপিডিয়া অনুবাদ/চীনা-বাংলা অনুবাদ')
from number_converter import to_bengali_digits
from test_cells import r1, r2, split_row_cells
from build_translation_data import get_district_bn, SPECIAL_CITIES

# Let's inspect all method phrases
methods = []
for style, lines in r1 + r2:
    text = '\n'.join(lines).strip()
    if 'colspan=' in text or text.startswith('!'): continue
    cells = split_row_cells(lines)
    # in Table 1, cell 2 or 3 might be method
    for c in cells:
        clean = re.sub(r'^(?:rowspan|colspan|style|width|align)=[^|]*\|', '', c).strip()
        if any(k in clean for k in ['设区', '析置', '改置', '恢复', '撤']):
            if clean not in methods:
                methods.append(clean)

print(f'Total unique method phrases: {len(methods)}')
print('Sample methods (first 20):')
for m in methods[:20]:
    print('  ', m)
