# -*- coding: utf-8 -*-
"""Measure how the Chinese module scales with input size (its own sample)."""
import importlib.util
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOLDER = os.path.join(ROOT, "চীনা-বাংলা অনুবাদ")
sys.path.insert(0, FOLDER)
os.chdir(FOLDER)

spec = importlib.util.spec_from_file_location("zh_tp_scale", os.path.join(FOLDER, "translate_page.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

src = open(os.path.join(FOLDER, "চীনের জেলা.txt"), encoding="utf-8").read()
print("full size:", len(src))
for size in (5000, 10000, 20000, 40000, 80000):
    clip = src[:size]
    t0 = time.time()
    mod.translate_wikipedia_text(clip)
    print(f"{size:>7} chars -> {time.time() - t0:6.2f}s")
