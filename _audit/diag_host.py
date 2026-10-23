# -*- coding: utf-8 -*-
"""Is it the endpoint or the whole host? List models vs generateContent."""
import json
import os
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from common.env_loader import get_gemini_key

key = get_gemini_key()

t0 = time.time()
try:
    with urllib.request.urlopen(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}", timeout=30) as r:
        data = json.loads(r.read().decode())
    print(f"list models: OK {time.time()-t0:.1f}s, {len(data.get('models', []))} models")
except Exception as exc:
    print("list models:", type(exc).__name__, exc)

# invalid key => should be a fast 400 if the host is reachable for POST
body = json.dumps({"contents": [{"parts": [{"text": "hi"}]}]}).encode()
t0 = time.time()
try:
    req = urllib.request.Request(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key=invalid",
        data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=25) as r:
        print("invalid key: OK?", r.status)
except urllib.error.HTTPError as exc:
    print(f"invalid key: HTTP {exc.code} in {time.time()-t0:.1f}s -> {exc.read().decode()[:80]}")
except Exception as exc:
    print("invalid key:", type(exc).__name__, f"{time.time()-t0:.1f}s", exc)
