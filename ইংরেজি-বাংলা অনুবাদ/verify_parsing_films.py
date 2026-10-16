# -*- coding: utf-8 -*-
import json
import re

with open('parsed_film_entries.json', encoding='utf-8') as f:
    items = json.load(f)

print(f'Total items: {len(items)}')

clean_titles = []
for idx, yr, rest in items:
    m = re.match(r"^(('{2,3}\[\[.*?\]\]'{2,3})|(\[\[.*?\]\])|('{2,3}.*?'{2,3}))(.*)$", rest)
    if not m:
        print(f'Line {idx} did not match: {rest}')
        continue
    
    title_raw = m.group(1).strip()
    trailer = m.group(5).strip()
    
    # Extract link target (if any) and clean title text
    # Case 1: ''[[Target|Display]]'' or ''[[Target]]''
    m_wikilink_italic = re.match(r"^'{2,3}\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]'{2,3}$", title_raw)
    # Case 2: [[Target|''Display'']] or [[Target|Display]] or [[Target]]
    m_wikilink_plain = re.match(r"^\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]$", title_raw)
    # Case 3: ''Display'' (no link)
    m_no_link = re.match(r"^'{2,3}(.*?)'{2,3}$", title_raw)
    
    target = None
    display = None
    
    if m_wikilink_italic:
        target = m_wikilink_italic.group(1).strip()
        display = (m_wikilink_italic.group(2) or target).strip()
    elif m_wikilink_plain:
        target = m_wikilink_plain.group(1).strip()
        raw_disp = (m_wikilink_plain.group(2) or target).strip()
        # strip inner italics if present
        display = re.sub(r"^'{2,3}|'{2,3}$", '', raw_disp).strip()
    elif m_no_link:
        target = None
        display = m_no_link.group(1).strip()
    else:
        print(f'Line {idx} weird title: {title_raw}')
        target = None
        display = title_raw
        
    clean_titles.append({
        'line': idx,
        'year': yr,
        'title_raw': title_raw,
        'target': target,
        'display': display,
        'trailer': trailer
    })

print(f'Successfully parsed {len(clean_titles)} titles')

with open('clean_film_titles.json', 'w', encoding='utf-8') as f:
    json.dump(clean_titles, f, ensure_ascii=False, indent=2)

for t in clean_titles[:15]:
    print(f"L{t['line']:3} [{t['year']}]: Target='{t['target']}' | Display='{t['display']}' | Note='{t['trailer'][:30]}...'")
