# -*- coding: utf-8 -*-
"""Raw response shape for gemini-3.5-flash."""
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from common.env_loader import get_gemini_key

key = get_gemini_key()
for model in ("gemini-3.5-flash", "gemini-3.1-flash-lite", "gemini-3-flash-preview"):
    body = json.dumps({"contents": [{"parts": [{"text": "Say hi in Bengali."}]}],
                       "generationConfig": {"maxOutputTokens": 64}}).encode()
    try:
        req = urllib.request.Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            data=body, headers={"Content-Type": "application/json", "x-goog-api-key": key})
        with urllib.request.urlopen(req, timeout=25) as r:
            data = json.loads(r.read().decode())
        print(model, "->", json.dumps(data, ensure_ascii=False)[:220])
    except Exception as exc:
        print(model, type(exc).__name__, exc)
