# -*- coding: utf-8 -*-
"""Fetch five real Wikipedia articles (en/zh/ja/ru/de) for the translation audit."""
import json
import os
import urllib.parse
import urllib.request

ARTICLES = [
    ("en", "Kinkaku-ji"),
    ("zh", "西湖"),
    ("ja", "金閣寺"),
    ("ru", "Собор Василия Блаженного"),
    ("de", "Kölner Dom"),
]

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
os.makedirs(OUT, exist_ok=True)
UA = "WikipediaTranslationToolkit-Audit/1.0"


def fetch(lang, title):
    params = urllib.parse.urlencode({
        "action": "parse", "page": title, "prop": "wikitext",
        "format": "json", "formatversion": "2", "redirects": "1",
    })
    url = f"https://{lang}.wikipedia.org/w/api.php?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "error" in data:
        raise RuntimeError(data["error"].get("info"))
    return data["parse"]["title"], data["parse"]["wikitext"]


manifest = []
for lang, title in ARTICLES:
    try:
        real_title, text = fetch(lang, title)
    except Exception as exc:
        print(f"{lang}:{title} FAIL {type(exc).__name__} {exc}")
        continue
    path = os.path.join(OUT, f"{lang}.wikitext")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    lines = text.count("\n") + 1
    print(f"{lang}:{real_title}  chars={len(text)}  lines={lines}  -> {path}")
    manifest.append({"lang": lang, "title": real_title, "chars": len(text), "lines": lines, "path": path})

with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
    json.dump(manifest, fh, ensure_ascii=False, indent=2)
