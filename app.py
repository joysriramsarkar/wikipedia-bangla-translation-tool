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
    translate_paragraph_ollama,
    translate_paragraph_openrouter,
    translate_paragraph_ai,
    translate_wikitext_full,
)
from common.env_loader import (  # noqa: E402
    DEFAULT_GEMINI_MODEL, get_gemini_key, get_gemini_model,
    DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_BASE_URL, get_ollama_key, get_ollama_base_url, get_ollama_model,
    DEFAULT_OPENROUTER_MODEL, DEFAULT_OPENROUTER_BASE_URL, get_openrouter_key, get_openrouter_base_url, get_openrouter_model,
    get_ai_provider,
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
    title = data.get("title", "")
    sl = data.get("sl", "en")
    tl = data.get("tl", "bn")
    do_mt = data.get("translate", True)
    engine = str(data.get("engine") or data.get("provider") or "google").lower()
    use_ai = engine in ("gemini", "ollama", "openrouter", "ai") or bool(data.get("use_ai"))
    base_url = None
    if engine == "ollama":
        raw_key = data.get("ollama_api_key") or data.get("api_key")
        if not raw_key:
            raw_key = get_ollama_key()
        gemini_model = str(data.get("model") or data.get("gemini_model") or get_ollama_model(DEFAULT_OLLAMA_MODEL))
        base_url = data.get("base_url") or data.get("ollama_base_url") or get_ollama_base_url(DEFAULT_OLLAMA_BASE_URL)
    elif engine == "openrouter":
        raw_key = data.get("openrouter_api_key") or data.get("api_key")
        if not raw_key:
            raw_key = get_openrouter_key()
        gemini_model = str(data.get("model") or data.get("gemini_model") or get_openrouter_model(DEFAULT_OPENROUTER_MODEL))
        base_url = data.get("base_url") or data.get("openrouter_base_url") or get_openrouter_base_url(DEFAULT_OPENROUTER_BASE_URL)
    else:
        raw_key = data.get("gemini_api_key") or data.get("api_key")
        if not raw_key:
            raw_key = get_gemini_key()
        gemini_model = str(data.get("gemini_model") or data.get("model") or get_gemini_model(DEFAULT_GEMINI_MODEL))
    gemini_key: str | None = str(raw_key).strip() if raw_key else None

    try:
        source_text = text if do_mt else data.get("source_text", "")
        if do_mt:
            from cx_postprocess.template_translator import is_template_wikitext, translate_template_wikitext
            from cx_postprocess.pipeline import normalize_nukta
            if is_template_wikitext(text, title=title):
                fixed = normalize_nukta(
                    translate_template_wikitext(
                        text,
                        sl=sl,
                        tl=tl,
                        gemini_key=gemini_key if use_ai else None,
                        gemini_model=gemini_model,
                        provider=engine if use_ai else None,
                        api_key=gemini_key if use_ai else None,
                        base_url=base_url,
                    )
                )
                unknown = []
                citations = {}
                healed = []
            else:
                fixed = translate_wikitext_full(
                    text,
                    sl=sl,
                    tl=tl,
                    gemini_key=gemini_key if use_ai else None,
                    gemini_model=gemini_model,
                    title=title,
                    provider=engine if use_ai else None,
                    api_key=gemini_key if use_ai else None,
                    base_url=base_url,
                )
                # Full translation already ran fix_text with source_text=text
                result = fix_text(fixed, source_text=text)
                fixed = result.get("fixed", "")
                unknown = result.get("unknown_params", [])
                citations = result.get("citations", {})
                healed = result.get("healed_refs", [])
        else:
            result = fix_text(text, source_text=source_text)
            fixed = result.get("fixed", "")
            unknown = result.get("unknown_params", [])
            citations = result.get("citations", {})
            healed = result.get("healed_refs", [])
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500
    return jsonify({
        "fixed": fixed,
        "unknown_params": unknown,
        "citations": citations,
        "healed_refs": healed,
    })


@app.post("/translate_ai")
def translate_ai():
    data = _json_request()
    text = data.get("text", "")
    provider = str(data.get("provider") or data.get("engine") or get_ai_provider("gemini")).lower()
    if "api_key" in data or "gemini_api_key" in data or "openrouter_api_key" in data or "ollama_api_key" in data:
        raw_api_key = data.get("api_key")
        if raw_api_key is None:
            raw_api_key = data.get("gemini_api_key")
        if raw_api_key is None:
            raw_api_key = data.get("openrouter_api_key")
        if raw_api_key is None:
            raw_api_key = data.get("ollama_api_key")
    else:
        if provider == "ollama":
            raw_api_key = get_ollama_key()
        elif provider == "openrouter":
            raw_api_key = get_openrouter_key()
        else:
            raw_api_key = get_gemini_key()
    if raw_api_key is None:
        if provider == "ollama":
            raw_api_key = get_ollama_key()
        elif provider == "openrouter":
            raw_api_key = get_openrouter_key()
        else:
            raw_api_key = get_gemini_key()
    api_key = str(raw_api_key).strip() if raw_api_key else ""
    if provider == "ollama":
        model = str(data.get("model") or get_ollama_model(DEFAULT_OLLAMA_MODEL))
        base_url = data.get("base_url") or data.get("ollama_base_url") or get_ollama_base_url(DEFAULT_OLLAMA_BASE_URL)
    elif provider == "openrouter":
        model = str(data.get("model") or get_openrouter_model(DEFAULT_OPENROUTER_MODEL))
        base_url = data.get("base_url") or data.get("openrouter_base_url") or get_openrouter_base_url(DEFAULT_OPENROUTER_BASE_URL)
    else:
        model = str(data.get("model") or data.get("gemini_model") or get_gemini_model(DEFAULT_GEMINI_MODEL))
        base_url = None
    sl = str(data.get("sl") or "en")
    tl = str(data.get("tl") or "bn")

    if not isinstance(text, str) or not text.strip():
        return jsonify({"ok": False, "error": "অনুবাদের জন্য কোনো টেক্সট পাওয়া যায়নি।"}), 400
    if provider not in ("ollama",) and not api_key:
        return jsonify({"ok": False, "error": "API Key প্রয়োজন।"}), 400

    try:
        if provider == "ollama":
            translated = translate_paragraph_ollama(text, api_key=api_key or None, model=model, sl=sl, tl=tl, base_url=base_url)
        elif provider == "openrouter":
            translated = translate_paragraph_openrouter(text, api_key=api_key, model=model, sl=sl, tl=tl, base_url=base_url)
        else:
            translated = translate_paragraph_gemini(text, api_key=api_key, model=model, sl=sl, tl=tl)
        return jsonify({"ok": True, "translated": translated, "provider": provider})
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


def _search_wiki_smart(lang: str, query: str, limit: int = 10) -> list[dict]:
    query = (query or "").strip()
    if not query:
        return []

    results = []
    seen_titles = set()
    redirect_map = {}

    # ১. উৎস উইকিপিডিয়ায় prefixsearch + redirects + descriptions
    try:
        data1 = _wiki_api(lang, {
            "action": "query",
            "generator": "prefixsearch",
            "gpssearch": query,
            "gpslimit": str(limit),
            "redirects": "1",
            "prop": "description|pageprops",
        }, timeout=8)
        if isinstance(data1, dict) and "query" in data1:
            for r in data1["query"].get("redirects", []):
                redirect_map[r["to"]] = r["from"]
            pages = data1["query"].get("pages", {})
            page_list = list(pages.values())
            page_list.sort(key=lambda p: p.get("index", 99))
            for p in page_list:
                t = p.get("title", "")
                if t and t not in seen_titles:
                    seen_titles.add(t)
                    desc = p.get("description", "")
                    redr = redirect_map.get(t, "")
                    results.append({
                        "title": t,
                        "redirect_from": redr,
                        "description": desc,
                        "lang": lang,
                        "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(t.replace(' ', '_'))}"
                    })
    except Exception:
        pass

    # ২. যদি কোনো ফলাফল না পাওয়া যায়, তবে সাধারণ opensearch
    if not results:
        try:
            os_data = _wiki_api(lang, {"action": "opensearch", "search": query, "limit": str(limit), "namespace": "0"}, timeout=6)
            if isinstance(os_data, list) and len(os_data) >= 2:
                for t in os_data[1]:
                    if t not in seen_titles:
                        seen_titles.add(t)
                        results.append({
                            "title": t,
                            "redirect_from": "",
                            "description": "",
                            "lang": lang,
                            "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(t.replace(' ', '_'))}"
                        })
        except Exception:
            pass

    # ৩. যদি উৎস ভাষা বাংলা না হয় কিন্তু অনুসন্ধানটি বাংলায় টাইপ করা হয়,
    # তবে বাংলা উইকিপিডিয়া থেকে সংশ্লিষ্ট উৎস ভাষার langlinks উদ্ধার করব
    if lang != "bn" and re.search(r"[\u0980-\u09FF]", query):
        try:
            bn_data = _wiki_api("bn", {
                "action": "query",
                "generator": "prefixsearch",
                "gpssearch": query,
                "gpslimit": "6",
                "redirects": "1",
                "prop": "langlinks|description",
                "lllang": lang,
            }, timeout=8)
            if isinstance(bn_data, dict) and "query" in bn_data:
                for pid, p in bn_data["query"].get("pages", {}).items():
                    bn_title = p.get("title", "")
                    ll = p.get("langlinks", [])
                    if ll and ll[0].get("*"):
                        src_title = ll[0]["*"]
                        if src_title not in seen_titles:
                            seen_titles.add(src_title)
                            results.append({
                                "title": src_title,
                                "redirect_from": f"বাংলা: {bn_title}",
                                "description": p.get("description", f"অনুরূপ {lang.upper()} নিবন্ধ"),
                                "lang": lang,
                                "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(src_title.replace(' ', '_'))}"
                            })
        except Exception:
            pass

    return results


@app.get("/search")
def search():
    lang = request.args.get("lang", "en")
    query = request.args.get("q", "")
    if not query:
        return jsonify([])
    return jsonify(_search_wiki_smart(lang, query))


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

    is_template = query.lower().startswith(("template:", "টেমপ্লেট:"))
    base_query = re.sub(r"^(?:template|টেমপ্লেট)\s*:\s*", "", query, flags=re.IGNORECASE).strip() if is_template else query

    try:
        data = _wiki_api(sl, {"action": "query", "titles": query,
                              "prop": "langlinks", "lllang": tl, "redirects": "1"})
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            links = page.get("langlinks") or []
            if links:
                found_title = links[0].get("*", "")
                if is_template and not found_title.startswith("টেমপ্লেট:"):
                    found_title = f"টেমপ্লেট:{found_title}"
                return jsonify({"ok": True, "title": found_title})
    except Exception:
        pass

    tr_title = _translate_google(base_query, sl, tl)
    if is_template and not tr_title.startswith("টেমপ্লেট:"):
        tr_title = f"টেমপ্লেট:{tr_title}"
    return jsonify({"ok": False, "title": tr_title})


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


@app.get("/<path:filename>")
def public_static(filename):
    if os.path.exists(os.path.join(PUBLIC_DIR, filename)):
        return send_from_directory(PUBLIC_DIR, filename)
    return jsonify({"error": "Not found"}), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8765, debug=False)
