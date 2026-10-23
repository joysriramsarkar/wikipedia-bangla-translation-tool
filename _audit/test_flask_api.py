# -*- coding: utf-8 -*-
"""Exercise the Flask app (app.py) endpoints with Flask's test client."""
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import app  # noqa: E402

client = app.test_client()
SAMPLE = "He lived on 120 km² of land and was active r. 1995–2005.<ref>{{cite web|url=http://x|title=T|access-date=2010-07-15}}</ref>"

print("GET /health:", client.get("/health").get_json())
print("GET /:", client.get("/").status_code)

r = client.post("/validate", json={"text": "{{Short description|x}} 120 km²"})
rep = r.get_json().get("report", {})
print("POST /validate:", r.status_code, "valid=", rep.get("valid"), "issues=", rep.get("issues")[:3])

t0 = time.time()
r = client.post("/fix", json={"text": SAMPLE, "translate": False})
print("POST /fix (no MT):", r.status_code, round(time.time() - t0, 2), "s ->", r.get_json().get("fixed"))

r = client.post("/fix", json={"text": "The temple was built in 1397.", "translate": True})
print("POST /fix (MT):", r.status_code, "->", r.get_json())

r = client.post("/translate_ai", json={"text": "The temple was built in 1397.", "api_key": "dummy"})
print("POST /translate_ai (bad key):", r.status_code, "->", str(r.get_json())[:160])

r = client.get("/v2/translate/en/bn/120%20km%C2%B2")
print("GET /v2/translate:", r.status_code, "->", r.get_json())

r = client.get("/translate_title?q=Kyoto&sl=en&tl=bn")
print("GET /translate_title:", r.status_code, "->", r.get_json())

r = client.get("/drafts")
print("GET /drafts:", r.status_code, type(r.get_json()).__name__)
