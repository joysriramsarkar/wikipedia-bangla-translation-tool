# -*- coding: utf-8 -*-
"""Diagnose the Gemini timeout: query key vs header key, 30s vs 60s."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from common.env_loader import get_gemini_key, get_gemini_model

key = get_gemini_key()
model = get_gemini_model()
body = {"contents": [{"parts": [{"text": "Say hi in Bengali, one word."}]}],
        "generationConfig": {"maxOutputTokens": 64}}
data = json.dumps(body).encode()

variants = [
    ("query-key 30s", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
     {"Content-Type": "application/json"}, 30),
    ("query-key 60s", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
     {"Content-Type": "application/json"}, 60),
    ("header-key 60s", f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
     {"Content-Type": "application/json", "x-goog-api-key": key}, 60),
]
for label, url, headers, timeout in variants:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = json.loads(r.read().decode())
        txt = out["candidates"][0]["content"]["parts"][0]["text"].strip()
        print(f"{label}: OK {time.time()-t0:.1f}s -> {txt[:40]!r}")
    except urllib.error.HTTPError as exc:
        print(f"{label}: HTTP {exc.code} {time.time()-t0:.1f}s -> {exc.read().decode()[:100]}")
    except Exception as exc:
        print(f"{label}: {type(exc).__name__} {time.time()-t0:.1f}s -> {exc}")
