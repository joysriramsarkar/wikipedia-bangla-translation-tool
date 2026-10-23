# -*- coding: utf-8 -*-
"""Probe the Gemini API with the key found in .env (value never printed)."""
import json
import re
import urllib.error
import urllib.request

raw = open(".env", "rb").read().decode("utf-8")
m = re.match(r'^gemini_api_key\s*[=:]\s*["\']?(.+?)["\']?\s*$', raw.strip())
key = m.group(1) if m else None
print("parsed key:", bool(key), "len:", len(key) if key else 0)


def call(model, body):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return "OK", json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}", json.loads(e.read().decode() or "{}")
    except Exception as e:
        return type(e).__name__, str(e)


# 1) list models
try:
    with urllib.request.urlopen(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}", timeout=30) as r:
        data = json.loads(r.read().decode())
    models = [x["name"].split("/")[-1] for x in data.get("models", [])]
    print("list models OK, count:", len(models))
    print("  flash-ish:", [x for x in models if "flash" in x][:15])
    print("  has 1.5-flash:", "gemini-1.5-flash" in models)
except urllib.error.HTTPError as e:
    print("list models HTTP", e.code, e.read().decode()[:300])
except Exception as e:
    print("list models FAIL", type(e).__name__, e)

# 2) generate with the toolkit's default model
body = {"contents": [{"parts": [{"text": "Say hello in Bengali, one word."}]}]}
for model in ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash"]:
    status, resp = call(model, body)
    if status == "OK":
        try:
            txt = resp["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            txt = "<no text>"
        print(f"{model}: {status} -> {txt[:60]!r}")
    else:
        snippet = resp if isinstance(resp, str) else resp.get("error", {}).get("message", resp)
        print(f"{model}: {status} -> {str(snippet)[:200]}")
