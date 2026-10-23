# -*- coding: utf-8 -*-
"""Probe which Gemini models actually work with generateContent for this key."""
import json
import re
import urllib.error
import urllib.request

raw = open(".env", "rb").read().decode("utf-8")
key = re.match(r'^gemini_api_key\s*[=:]\s*["\']?(.+?)["\']?\s*$', raw.strip()).group(1)

body = {"contents": [{"parts": [{"text": "Translate to Bengali: The temple was built in 1397."}]}],
        "generationConfig": {"maxOutputTokens": 256}}

for model in ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest",
              "gemini-2.5-flash-lite", "gemini-3-flash-preview", "gemini-3.1-flash-lite"]:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read().decode())
        txt = data["candidates"][0]["content"]["parts"][0]["text"]
        print(f"{model}: OK -> {txt.strip()[:80]!r}")
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        try:
            msg = json.loads(msg)["error"]["message"]
        except Exception:
            pass
        print(f"{model}: HTTP {e.code} -> {msg[:120]}")
    except Exception as e:
        print(f"{model}: {type(e).__name__} -> {e}")
