# -*- coding: utf-8 -*-
"""Environment + network diagnostics for the audit."""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("python:", sys.version.split()[0])

# --- .env inspection (masked) ---
env_path = ".env"
if os.path.exists(env_path):
    raw = open(env_path, "rb").read()
    print(".env bytes:", len(raw), "starts with BOM:", raw[:3] == b"\xef\xbb\xbf")
    for line in raw.decode("utf-8-sig").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            print(f"  key={k.strip()!r} len={len(v)} quoted={v[:1] in ('\"', chr(39))} "
                  f"space={(' ' in v)} prefix={v[:4]!r}")
else:
    print(".env missing")

key = None
for line in open(env_path, "rb").read().decode("utf-8-sig").splitlines():
    if line.startswith("gemini_api_key="):
        key = line.split("=", 1)[1].strip().strip('"').strip("'")
print("GEMINI key len:", len(key) if key else None, "prefix:", (key or "")[:6])

def http(url, data=None, headers=None, timeout=20):
    hdr = {"User-Agent": "Mozilla/5.0"}
    if headers:
        hdr.update(headers)
    req = urllib.request.Request(url, data=data, headers=hdr)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

# --- Network probes ---
probes = {
    "gtx": "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=bn&dt=t&q=hello",
    "clients5": "https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl=bn&q=hello",
    "mymemory": "https://api.mymemory.translated.net/get?q=hello&langpair=en|bn",
    "en.wikipedia": "https://en.wikipedia.org/w/api.php?action=query&titles=Bengali_language&format=json",
}
for name, url in probes.items():
    try:
        status, body = http(url, timeout=15)
        print(f"NET {name}: OK {status} {body[:90]!r}")
    except Exception as exc:
        print(f"NET {name}: FAIL {type(exc).__name__}: {exc}")

# --- Gemini model listing ---
if key:
    try:
        status, body = http(
            f"https://generativelanguage.googleapis.com/v1beta/models?key={key}", timeout=25)
        data = json.loads(body.decode("utf-8"))
        names = [m["name"].split("/")[-1] for m in data.get("models", [])]
        print("GEMINI models count:", len(names))
        print("GEMINI models:", ", ".join(sorted(names)))
    except Exception as exc:
        print("GEMINI list FAIL", type(exc).__name__, exc)
