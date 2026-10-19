# -*- coding: utf-8 -*-
"""
Vercel (ও যেকোনো WSGI হোস্ট)-এর জন্য Flask এন্ট্রিপয়েন্ট।

স্থানীয় ডেভেলপমেন্টে আগের `cx_postprocess/server.py` (stdlib HTTP সার্ভার)
ব্যবহার করা যায়; Vercel-এ `app.py`-র `app` WSGI অবজেক্টটাই চলে।

Routes:
    GET  /health
    POST /fix                 {"text", "translate", "sl", "tl"}
    POST /validate            {"text"}
    GET  /fetch?lang=&title=
    GET  /search?lang=&q=
    POST /preview             {"text", "title"}
    GET  /translate_title?q=&sl=&tl=
    GET/POST /drafts
    GET  /v2/list/mt/en/bn
    GET  /v2/translate/en/bn/<text>
"""
import json
import os
import re
import sys
import tempfile
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, send_from_directory  # noqa: E402

from cx_postprocess.pipeline import fix_text  # noqa: E402
from cx_postprocess.server import DRAFTS_FILE, validate_wikitext  # noqa: E402
from cx_postprocess.mt_translate import (  # noqa: E402
    _translate_clients5,
    translate_paragraph_gemini,
    translate_wikitext_full,
)

PUBLIC_DIR = os.path.join(BASE_DIR, "public")
USER_AGENT = "WikipediaTranslationBot/1.0 (+https://github.com/joysriramsarkar/wikipedia-bangla-translation-tool)"

app = Flask(__name__, static_folder=None)


@app.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


def _json_request():
    data = request.get_json(silent=True)
    return data if isinstance(data, dict) else {}


def _http_json(url, data=None, timeout=20):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _wiki_api(lang, params, timeout=20):
    query = urllib.parse.urlencode({**params, "format": "json", "origin": "*"})
    return _http_json(f"https://{lang}.wikipedia.org/w/api.php?{query}", timeout=timeout)


def _translate_google(text, sl="en", tl="bn"):
    if not text or not text.strip():
        return text
    try:
        result = _translate_clients5(text, sl, tl)
        if result and result.strip():
            return result
    except Exception:
        pass
    return text


def _drafts_path():
    # Vercel-এর ফাইলসিস্টেম read-only; /tmp ছাড়া লেখা যায় না।
    if os.environ.get("VERCEL"):
        return os.path.join(tempfile.gettempdir(), "bnwiki_tracked_drafts.json")
    return DRAFTS_FILE


def _load_drafts():
    path = _drafts_path()
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return []
    return []


def _save_drafts(drafts):
    try:
        with open(_drafts_path(), "w", encoding="utf-8") as handle:
            json.dump(drafts, handle, ensure_ascii=False, indent=2)
    except Exception as exc:
        print(f"draft save error: {exc}")


@app.get("/health")
def health():
    return jsonify({"ok": True, "service": "cx-bn-fix", "runtime": "wsgi"})


@app.post("/fix")
def fix():
    data = _json_request()
    text = data.get("text", "")
    if not isinstance(text, str):
        text = ""
    sl = data.get("sl", "en")
    tl = data.get("tl", "bn")
    do_mt = data.get("translate", True)
    raw_key = data.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    gemini_key: str | None = str(raw_key).strip() if raw_key else None
    gemini_model = str(data.get("gemini_model") or "gemini-1.5-flash")
    engine = data.get("engine", "google")
    use_ai = engine == "gemini" or bool(data.get("use_ai"))

    try:
        if do_mt:
            fixed = translate_wikitext_full(
                text,
                sl=sl,
                tl=tl,
                gemini_key=gemini_key if use_ai else None,
                gemini_model=gemini_model
            )
            unknown = []
        else:
            result = fix_text(text)
            fixed = result.get("fixed", "")
            unknown = result.get("unknown_params", [])
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500
    return jsonify({"fixed": fixed, "unknown_params": unknown})


@app.post("/translate_ai")
def translate_ai():
    data = _json_request()
    text = data.get("text", "")
    raw_api_key = data.get("api_key") or data.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    api_key = str(raw_api_key).strip() if raw_api_key else ""
    model = str(data.get("model") or "gemini-1.5-flash")
    sl = str(data.get("sl") or "en")
    tl = str(data.get("tl") or "bn")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"ok": False, "error": "অনুবাদের জন্য কোনো টেক্সট পাওয়া যায়নি।"}), 400
    if not api_key:
        return jsonify({"ok": False, "error": "Gemini API Key প্রয়োজন। aistudio.google.com থেকে বিনামূল্যে তৈরি করুন।"}), 400

    try:
        translated = translate_paragraph_gemini(text, api_key=api_key, model=model, sl=sl, tl=tl)
        return jsonify({"ok": True, "translated": translated})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.post("/validate")
def validate():
    data = _json_request()
    text = data.get("text", "")
    if not isinstance(text, str):
        text = ""
    try:
        return jsonify({"ok": True, "report": validate_wikitext(text)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/fetch")
def fetch():
    lang = request.args.get("lang", "en")
    title = request.args.get("title")
    url_arg = request.args.get("url")
    if url_arg:
        match = re.search(r"https?://([a-z\-]+)\.wikipedia\.org/wiki/([^#?]+)", url_arg)
        if match:
            lang = match.group(1).lower()
            title = urllib.parse.unquote(match.group(2)).replace("_", " ")
    if not title:
        return jsonify({"ok": False, "error": "Missing title"}), 400
    try:
        data = _wiki_api(lang, {"action": "parse", "page": title,
                                "prop": "wikitext", "redirects": "1"})
        if "error" in data:
            return jsonify({"ok": False, "error": data["error"].get("info")}), 404
        parsed = data.get("parse", {})
        return jsonify({"ok": True, "title": parsed.get("title", title),
                        "lang": lang, "wikitext": parsed.get("wikitext", {}).get("*", "")})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/search")
def search():
    lang = request.args.get("lang", "en")
    query = request.args.get("q", "")
    if not query:
        return jsonify([])
    try:
        data = _wiki_api(lang, {"action": "opensearch", "search": query,
                                "limit": "8", "namespace": "0"}, timeout=10)
        results = []
        if isinstance(data, list) and len(data) >= 2:
            urls = data[3] if len(data) > 3 else []
            for index, title in enumerate(data[1]):
                results.append({"title": title,
                                "url": urls[index] if index < len(urls) else ""})
        return jsonify(results)
    except Exception:
        return jsonify([])


@app.post("/preview")
def preview():
    data = _json_request()
    wikitext = data.get("text", "")
    title = data.get("title", "খসড়া:নিবন্ধ")
    if not isinstance(wikitext, str) or not wikitext.strip():
        return jsonify({"ok": True, "html": "<p><em>প্রাকদর্শনের জন্য কোনো উইকিটেক্সট পাওয়া যায়নি।</em></p>"})
    payload = urllib.parse.urlencode({
        "action": "parse", "text": wikitext, "title": title,
        "prop": "text", "contentmodel": "wikitext",
        "format": "json", "formatversion": "2",
    }).encode("utf-8")
    try:
        req = urllib.request.Request("https://bn.wikipedia.org/w/api.php", data=payload,
                                     headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=30) as response:
            parsed = json.loads(response.read().decode("utf-8"))
        html = parsed.get("parse", {}).get("text", "")
        return jsonify({"ok": True, "html": html})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/translate_title")
def translate_title():
    query = request.args.get("q", "").strip()
    sl = request.args.get("sl", "en")
    tl = request.args.get("tl", "bn")
    if not query:
        return jsonify({"ok": False, "title": ""})
    try:
        data = _wiki_api(sl, {"action": "query", "titles": query,
                              "prop": "langlinks", "lllang": tl, "redirects": "1"})
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            links = page.get("langlinks") or []
            if links:
                return jsonify({"ok": True, "title": links[0].get("*", "")})
    except Exception:
        pass
    return jsonify({"ok": False, "title": _translate_google(query, sl, tl)})


@app.get("/drafts")
def get_drafts():
    return jsonify(_load_drafts())


@app.post("/drafts")
def post_draft():
    data = _json_request()
    if not data.get("title"):
        return jsonify({"ok": False, "error": "Missing title"}), 400
    drafts = [item for item in _load_drafts() if item.get("title") != data["title"]]
    drafts.insert(0, data)
    _save_drafts(drafts)
    return jsonify({"ok": True, "saved": data})


@app.get("/v2/list/mt/en/bn")
def mt_list():
    return jsonify({"tools": [{"name": "CXBnFix", "providing": "postprocess-en-bn"}]})


@app.get("/v2/translate/en/bn/<path:text>")
def mt_translate_path(text):
    result = fix_text(text)
    return jsonify({"translation": result.get("fixed", ""),
                    "unknown_params": result.get("unknown_params", [])})


@app.get("/")
@app.get("/dashboard")
@app.get("/dashboard.html")
def dashboard():
    if os.path.exists(os.path.join(PUBLIC_DIR, "dashboard.html")):
        return send_from_directory(PUBLIC_DIR, "dashboard.html")
    return jsonify({"ok": True, "service": "cx-bn-fix"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
