# -*- coding: utf-8 -*-
"""In-process smoke test for the stdlib handler (no background server needed)."""
import json
import os
import sys
import threading
import urllib.request
from http.server import HTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import cx_postprocess.server as srv  # noqa: E402

PORT = 8799
BASE = f"http://127.0.0.1:{PORT}"
httpd = HTTPServer(("127.0.0.1", PORT), srv._Handler)
threading.Thread(target=httpd.serve_forever, daemon=True).start()


def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        return r.status, r.read()


try:
    print("GET /health:", get("/health")[0], get("/health")[1][:50])
    print("GET /dashboard:", get("/dashboard")[0])
    print("POST /validate:", post("/validate", {"text": "{{Short description|x}} 120 km2"})[1]["report"]["issues"][:2])
    print("POST /fix no-mt:", post("/fix", {"text": "r. 1995 and 120 km2", "translate": False}))
    print("POST /fix mt:", post("/fix", {"text": "The temple was built in 1397.", "translate": True}))
    print("POST /fix gemini(env key):",
          post("/fix", {"text": "The temple was built in 1397.", "translate": True, "engine": "gemini"}))
finally:
    httpd.shutdown()
