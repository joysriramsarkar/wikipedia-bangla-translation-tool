# -*- coding: utf-8 -*-
import os, sys, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, "রুশ-বাংলা অনুবাদ")
sys.path.insert(0, FOLDER)
os.chdir(FOLDER)
import importlib
import table_translator as tt

src = open(os.path.join(FOLDER, "রাশিয়ার জেলা.txt"), encoding="utf-8").read()
print("src len:", len(src))
chunks = src.split("\n|-")
print("chunks:", len(chunks), "first chunk len:", len(chunks[0]))
print("chunk[1] head:", repr(chunks[1][:80]))
out = tt.translate_table_row(chunks[1])
print("row out len:", len(out), "head:", repr(out[:60]))

# try the whole table through translate_wikitable
i = src.find("{|")
j = src.find("\n|}", i)
table = src[i:j + 4]
print("table len:", len(table))
tr = tt.translate_wikitable(table)
print("table out len:", len(tr))
print("head:", repr(tr[:120]))
