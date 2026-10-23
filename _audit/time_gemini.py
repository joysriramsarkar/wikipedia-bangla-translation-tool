# -*- coding: utf-8 -*-
"""Time the Gemini paragraph call through the configured model."""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from common.env_loader import get_gemini_key, get_gemini_model
from cx_postprocess.mt_translate import translate_paragraph_gemini

key = get_gemini_key()
print("key loaded:", bool(key), "model:", get_gemini_model())
text = ("The temple was built in 1397 by Yoshimitsu as a retirement villa, "
        "and it was converted into a Zen temple after his death.<ref name=\"a\">"
        "{{cite book|title=Kyoto|year=1999}}</ref>")
for attempt in (1, 2):
    t0 = time.time()
    try:
        out = translate_paragraph_gemini(text, api_key=key, model=get_gemini_model())
        print(f"attempt {attempt}: {time.time()-t0:.1f}s -> {out[:120]!r}")
    except Exception as exc:
        print(f"attempt {attempt}: {time.time()-t0:.1f}s FAIL {type(exc).__name__}: {exc}")
