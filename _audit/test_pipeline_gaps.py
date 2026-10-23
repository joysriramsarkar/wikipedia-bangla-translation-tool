# -*- coding: utf-8 -*-
"""Check pipeline gaps (rules 1/5/13) and the langlinks title lookup."""
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from cx_postprocess.pipeline import fix_text  # noqa: E402

sample = (
    "{{Short description|Temple in Kyoto}}\n"
    "{{Use dmy dates}}\n"
    "{{Use British English}}\n"
    "He was king r. 1995–2005 and lived on 120 km².\n"
    "{{Infobox building}}"
)
out = fix_text(sample)["fixed"]
print("--- fix_text output ---")
print(out)
print("\nr. kept?      ", "r. ১৯৯৫" in out)
print("Short desc?   ", "Short description" in out)
print("Use dmy?      ", "Use dmy" in out)
print("Use British?  ", "Use British" in out)

# langlinks lookup exactly as app.py does it
print("\n--- langlinks probe ---")
for query in ["Kyoto", "Kinkaku-ji"]:
    params = {"action": "query", "titles": query, "prop": "langlinks",
              "lllang": "bn", "redirects": "1", "format": "json", "origin": "*"}
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "audit/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        links = page.get("langlinks") or []
        print(f"  {query!r}: title={page.get('title')!r} langlinks={ [l.get('*') for l in links] }")
