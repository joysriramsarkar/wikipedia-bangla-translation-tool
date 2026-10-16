# -*- coding: utf-8 -*-
import re

def parse_title_parts(title_raw):
    # Remove notes
    efn_pos = title_raw.find('{{efn')
    ref_pos = title_raw.find('<ref')
    cut_pos = -1
    if efn_pos != -1 and ref_pos != -1:
        cut_pos = min(efn_pos, ref_pos)
    elif efn_pos != -1:
        cut_pos = efn_pos
    elif ref_pos != -1:
        cut_pos = ref_pos

    if cut_pos != -1:
        title_core = title_raw[:cut_pos].strip()
        notes = title_raw[cut_pos:].strip()
    else:
        title_core = title_raw.strip()
        notes = ''

    # Clean italic markers
    clean_no_italics = re.sub(r"''", "", title_core).strip()
    
    # Check if there is a parenthetical part at the end
    m_paren = re.search(r"^(.+?)\s*\((.+?)\)$", clean_no_italics)
    
    return title_core, clean_no_italics, m_paren, notes

test_cases = [
    "''Fighter Over Finland'' (''Hävittäjälentäjänä Kahdessa Sodassa'')",
    "''It's Not Easy Being Me: a Lifetime of No Respect But Plenty of Sex and Drugs'' (published posthumously)",
    "''Hollywood Causes Cancer''",
    "[[Bigger than Hitler – Better than Christ]]",
    "''The I Chong: Meditations From the Joint''",
    "''The Man Died: Prison Notes''",
    "''Clinging to the Wreckage: A Part of Life''",
    "''[[The Lives of a Bengal Lancer (book)|The Lives of a Bengal Lancer]]''",
    "''Operation Overflight: The U-2 Spy Pilot Tells His Story for the First Time''"
]

for t in test_cases:
    core, clean, mp, notes = parse_title_parts(t)
    print("RAW:", t)
    print("CLEAN:", clean)
    if mp:
        print("  MAIN:", mp.group(1))
        print("  PAREN:", mp.group(2))
    print()
