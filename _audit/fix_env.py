# -*- coding: utf-8 -*-
"""Rewrite .env to the standard KEY=VALUE form without printing the secret."""
import os
import re

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
raw = open(path, "rb").read().decode("utf-8-sig").strip()
m = re.match(r'^gemini_api_key\s*[=:]\s*["\']?(.+?)["\']?\s*$', raw, re.IGNORECASE)
if not m:
    raise SystemExit("could not parse .env")
key = m.group(1)
new = (
    "# এই ফাইল git-এ কমিট হয় না (.gitignore দেখুন)\n"
    "GEMINI_API_KEY=" + key + "\n"
    "GEMINI_MODEL=gemini-3.8-flash\n"
)
open(path, "w", encoding="utf-8", newline="\n").write(new)
print("rewritten .env, key length:", len(key))
