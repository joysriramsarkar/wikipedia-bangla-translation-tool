# -*- coding: utf-8 -*-
"""Try different Gemini endpoints/models to see which one answers."""
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from common.env_loader import get_gemini_key

key = get_gemini_key()
body = json.dumps({"contents": [{"parts": [{"text": "Say hi in Bengali."}]}],
                   "generationConfig": {"maxOutputTokens": 32}}).encode()

urls = [
    ("v1beta gemini-3.8-flash", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"),
    ("v1 gemini-3.8-flash", "https://generativelanguage.googleapis.com/v1/models/gemini-3.8-flash:generateContent"),
    ("v1beta gemini-flash-latest", "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"),
    ("v1beta gemini-3.5-flash", "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent"),
]
for label, url in urls:
    try:
        req = urllib.request.Request(url, data=body, headers={
            "Content-Type": "application/json", "x-goog-api-key": key})
        with urllib.request.urlopen(req, timeout=20) as r:
            out = json.loads(r.read().decode())
        print(label, "OK ->", out["candidates"][0]["content"]["parts"][0]["text"][:40])
    except urllib.error.HTTPError as exc:
        print(label, "HTTP", exc.code, exc.read().decode()[:90])
    except Exception as exc:
        print(label, type(exc).__name__, exc)
