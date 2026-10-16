# -*- coding: utf-8 -*-
from test_all_titles import format_titles_v2

test_titles = [
    "''It's Not Easy Being Me: a Lifetime of No Respect But Plenty of Sex and Drugs'' (published posthumously)",
    "''Hollywood Causes Cancer''",
    "[[Bigger than Hitler – Better than Christ]]",
    "''The I Chong: Meditations From the Joint''",
    "''The Man Died: Prison Notes''",
    "''Clinging to the Wreckage: A Part of Life''",
    "''[[The Lives of a Bengal Lancer (book)|The Lives of a Bengal Lancer]]''",
    "''Fighter Over Finland'' (''Hävittäjälentäjänä Kahdessa Sodassa'')",
    "''Operation Overflight: The U-2 Spy Pilot Tells His Story for the First Time''"
]

print("=== USER EXAMPLES TITLE TEST ===")
for t in test_titles:
    bn, ro = format_titles_v2(t)
    print("RAW:", t)
    print("BN :", bn)
    print("RO :", ro)
    print("-" * 50)
