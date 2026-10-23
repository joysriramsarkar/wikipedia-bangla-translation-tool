# -*- coding: utf-8 -*-
"""
উইকিপিডিয়া অনুবাদ টুলকিট - লোকাল API সার্ভার ও ড্যাশবোর্ড

চালানো:
    python -m cx_postprocess.server
    # → http://127.0.0.1:8765/dashboard

এন্ডপয়েন্ট:
- GET  / or /dashboard → ওয়েব ড্যাশবোর্ড ও খসড়া ট্র্যাকার
- GET  /health         → {"ok": true}
- POST /fix            → {"text": "..."} → {"fixed": "...", "unknown_params": [...]}
- POST /validate       → {"text": "..."} → {"ok": true, "report": {...}}
- GET  /drafts         → [{"title": "...", "created_at": "...", ...}]
- POST /drafts         → খসড়া সংরক্ষণ ও ট্র্যাকিং শুরু
- GET  /v2/list/mt/en/bn
- GET  /v2/translate/en/bn/<text>
"""
import json
import os
import sys
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DRAFTS_FILE = os.path.join(BASE_DIR, "tracked_drafts.json")
DASHBOARD_FILE = os.path.join(PROJECT_DIR, "public", "dashboard.html")


def load_drafts() -> list:
    if os.path.exists(DRAFTS_FILE):
        try:
            with open(DRAFTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_drafts(drafts: list) -> None:
    try:
        with open(DRAFTS_FILE, "w", encoding="utf-8") as f:
            json.dump(drafts, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving drafts: {e}")


def _env_gemini_key() -> str:
    """`.env` / প্রসেস-এনভায়রনমেন্ট থেকে Gemini কী (নতুন লোডার)।"""
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_gemini_key
        return get_gemini_key()
    except Exception:
        return ""


def _env_gemini_model() -> str:
    """`.env`-এ দেওয়া মডেল, না থাকলে যাচাই করা ডিফল্ট।"""
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_gemini_model
        return get_gemini_model()
    except Exception:
        return "gemini-3.5-flash"


def _env_ollama_key() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_ollama_key
        return get_ollama_key()
    except Exception:
        return ""


def _env_ollama_base_url() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_ollama_base_url, DEFAULT_OLLAMA_BASE_URL
        return get_ollama_base_url(DEFAULT_OLLAMA_BASE_URL)
    except Exception:
        return "http://localhost:11434"


def _env_ollama_model() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_ollama_model, DEFAULT_OLLAMA_MODEL
        return get_ollama_model(DEFAULT_OLLAMA_MODEL)
    except Exception:
        return "llama3.1"


def _env_openrouter_key() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_openrouter_key
        return get_openrouter_key()
    except Exception:
        return ""


def _env_openrouter_base_url() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_openrouter_base_url, DEFAULT_OPENROUTER_BASE_URL
        return get_openrouter_base_url(DEFAULT_OPENROUTER_BASE_URL)
    except Exception:
        return "https://openrouter.ai/api/v1"


def _env_openrouter_model() -> str:
    if PROJECT_DIR not in sys.path:
        sys.path.insert(0, PROJECT_DIR)
    try:
        from common.env_loader import get_openrouter_model, DEFAULT_OPENROUTER_MODEL
        return get_openrouter_model(DEFAULT_OPENROUTER_MODEL)
    except Exception:
        return "openai/gpt-4o-mini"


def validate_wikitext(text: str) -> dict:
    """উইকিটেক্সটে বাংলা উইকিপিডিয়ার নীতিমালা যাচাই করে।"""
    root = os.path.dirname(BASE_DIR)
    if root not in sys.path:
        sys.path.insert(0, root)
    from wikipedia_translation_toolkit import WikipediaTranslator
    return WikipediaTranslator().validate_rules(text)


class _Handler(BaseHTTPRequestHandler):
    def _cors(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/", "/dashboard"):
            if os.path.exists(DASHBOARD_FILE):
                with open(DASHBOARD_FILE, "r", encoding="utf-8") as f:
                    content = f.read().encode("utf-8")
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            body = json.dumps({"ok": True, "service": "cx-bn-fix"}).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/health":
            body = json.dumps({"ok": True, "service": "cx-bn-fix"}).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/drafts":
            drafts = load_drafts()
            body = json.dumps(drafts, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/v2/list/mt/en/bn":
            body = json.dumps(
                {"tools": [{"name": "CXBnFix", "providing": "postprocess-en-bn"}]},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path.startswith("/v2/translate/en/bn/"):
            try:
                from .pipeline import fix_text
            except ImportError:
                from pipeline import fix_text  # type: ignore[no-redef]
            raw_text = unquote(path[len("/v2/translate/en/bn/"):])
            result = fix_text(raw_text)
            body = json.dumps(
                {"translation": result["fixed"],
                 "unknown_params": result["unknown_params"]},
                ensure_ascii=False,
            ).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/fetch":
            qs = parse_qs(urlparse(self.path).query)
            url_arg = qs.get("url", [None])[0]
            lang_arg = qs.get("lang", ["en"])[0]
            title_arg = qs.get("title", [None])[0]

            if url_arg:
                import re
                m = re.search(r"https?://([a-z\-]+)\.wikipedia\.org/wiki/([^#?]+)", url_arg)
                if m:
                    lang_arg = m.group(1).lower()
                    title_arg = unquote(m.group(2)).replace("_", " ")

            if not title_arg:
                body = json.dumps({"ok": False, "error": "Missing title"}, ensure_ascii=False).encode("utf-8")
                self.send_response(400)
            else:
                api_url = f"https://{lang_arg}.wikipedia.org/w/api.php?action=parse&page={quote(title_arg)}&prop=wikitext&redirects=1&format=json"
                try:
                    req = urllib.request.Request(api_url, headers={"User-Agent": "WikipediaTranslationBot/1.0"})
                    with urllib.request.urlopen(req, timeout=15) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        if "error" in data:
                            body = json.dumps({"ok": False, "error": data["error"].get("info")}, ensure_ascii=False).encode("utf-8")
                            self.send_response(404)
                        else:
                            wikitext = data.get("parse", {}).get("wikitext", {}).get("*", "")
                            resolved_title = data.get("parse", {}).get("title", title_arg)
                            body = json.dumps({
                                "ok": True,
                                "title": resolved_title,
                                "lang": lang_arg,
                                "wikitext": wikitext
                            }, ensure_ascii=False).encode("utf-8")
                            self.send_response(200)
                except Exception as e:
                    body = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
                    self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/search":
            qs = parse_qs(urlparse(self.path).query)
            q = qs.get("q", [""])[0]
            lang = qs.get("lang", ["en"])[0]
            if not q:
                body = b"[]"
                self.send_response(200)
            else:
                api_url = f"https://{lang}.wikipedia.org/w/api.php?action=opensearch&search={quote(q)}&limit=8&namespace=0&format=json"
                try:
                    req = urllib.request.Request(api_url, headers={"User-Agent": "WikipediaTranslationBot/1.0"})
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        results = []
                        if len(data) >= 2:
                            for i, t in enumerate(data[1]):
                                u = data[3][i] if len(data) > 3 and i < len(data[3]) else ""
                                results.append({"title": t, "url": u})
                        body = json.dumps(results, ensure_ascii=False).encode("utf-8")
                        self.send_response(200)
                except Exception:
                    body = json.dumps([]).encode("utf-8")
                    self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/translate_title":
            qs = parse_qs(urlparse(self.path).query)
            q = qs.get("q", [""])[0]
            sl = qs.get("sl", ["en"])[0]
            tl = qs.get("tl", ["bn"])[0]
            if not q:
                body = json.dumps({"ok": False, "title": ""}).encode("utf-8")
                self.send_response(200)
            else:
                try:
                    from .mt_translate import _translate_raw_chunk
                    from .bn_digits_safe import to_bengali_digits_safe
                except ImportError:
                    from mt_translate import _translate_raw_chunk  # type: ignore[no-redef]
                    from bn_digits_safe import to_bengali_digits_safe  # type: ignore[no-redef]
                tr_title = _translate_raw_chunk(q, sl=sl, tl=tl)
                tr_title = to_bengali_digits_safe(tr_title)
                body = json.dumps({"ok": True, "title": tr_title}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path in ("/fix", "/translate"):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                data = {}

            text = data.get("text", "")
            sl = data.get("sl", "en")
            tl = data.get("tl", "bn")
            do_mt = data.get("translate", True)
            engine = str(data.get("engine") or data.get("provider") or "google").lower()

            if do_mt:
                try:
                    from .mt_translate import translate_wikitext_full
                except ImportError:
                    from mt_translate import translate_wikitext_full  # type: ignore[no-redef]

                # ড্যাশবোর্ডে Gemini বেছে নিলে এখানেও তা মানতে হবে; আগে এই
                # (stdlib) সার্ভার অনুরোধের engine/কী উপেক্ষা করে চুপচাপ
                # গুগল অনুবাদে চলে যেত।
                use_ai = engine in ("gemini", "ollama", "openrouter", "ai")
                gemini_key = ""
                gemini_model = ""
                base_url = None
                if use_ai:
                    if engine == "ollama":
                        gemini_key = str(data.get("ollama_api_key") or data.get("api_key") or "")
                        if not gemini_key:
                            gemini_key = _env_ollama_key()
                        gemini_model = str(data.get("model") or data.get("gemini_model") or "")
                        base_url = data.get("base_url") or data.get("ollama_base_url") or _env_ollama_base_url()
                        if not gemini_model:
                            gemini_model = _env_ollama_model()
                    elif engine == "openrouter":
                        gemini_key = str(data.get("openrouter_api_key") or data.get("api_key") or "")
                        gemini_model = str(data.get("model") or data.get("gemini_model") or "")
                        if not gemini_key:
                            try:
                                from common.env_loader import get_openrouter_key
                                gemini_key = get_openrouter_key()
                            except Exception:
                                gemini_key = ""
                        if not gemini_model:
                            try:
                                from common.env_loader import get_openrouter_model
                                gemini_model = get_openrouter_model()
                            except Exception:
                                gemini_model = "openai/gpt-4o-mini"
                        base_url = data.get("base_url") or data.get("openrouter_base_url") or _env_openrouter_base_url()
                    else:
                        gemini_key = str(data.get("gemini_api_key") or data.get("api_key") or "")
                        gemini_model = str(data.get("model") or data.get("gemini_model") or "")
                        if use_ai and not gemini_key:
                            gemini_key = _env_gemini_key()
                        if not gemini_model:
                            gemini_model = _env_gemini_model()
                try:
                    fixed_text = translate_wikitext_full(
                        text, sl=sl, tl=tl,
                        gemini_key=gemini_key if use_ai else None,
                        gemini_model=gemini_model,
                        title=data.get("title", ""),
                        provider=engine if use_ai else None,
                        api_key=gemini_key if use_ai else None,
                        base_url=base_url,
                    )
                    unknown = []
                except Exception as exc:
                    body = json.dumps({"ok": False, "error": str(exc)},
                                      ensure_ascii=False).encode("utf-8")
                    self.send_response(500)
                    self._cors()
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.end_headers()
                    self.wfile.write(body)
                    return
            else:
                try:
                    from .pipeline import fix_text
                except ImportError:
                    from pipeline import fix_text  # type: ignore[no-redef]
                res = fix_text(text)
                fixed_text = res.get("fixed", "")
                unknown = res.get("unknown_params", [])

            body = json.dumps({"fixed": fixed_text, "unknown_params": unknown}, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/translate_ai":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                data = {}

            text = data.get("text", "")
            provider = str(data.get("provider") or data.get("engine") or "gemini").lower()
            if provider not in ("gemini", "ollama", "openrouter"):
                provider = "gemini"

            raw_key = data.get("api_key")
            if raw_key is None:
                if provider == "ollama":
                    raw_key = data.get("ollama_api_key") or _env_ollama_key()
                elif provider == "openrouter":
                    raw_key = data.get("openrouter_api_key") or _env_openrouter_key()
                else:
                    raw_key = data.get("gemini_api_key") or _env_gemini_key()
            api_key = str(raw_key).strip() if raw_key else ""

            if provider == "ollama":
                model = str(data.get("model") or _env_ollama_model())
                base_url = data.get("base_url") or data.get("ollama_base_url") or _env_ollama_base_url()
            elif provider == "openrouter":
                model = str(data.get("model") or _env_openrouter_model())
                base_url = data.get("base_url") or data.get("openrouter_base_url") or _env_openrouter_base_url()
            else:
                model = str(data.get("model") or data.get("gemini_model") or _env_gemini_model())
                base_url = None
            sl = str(data.get("sl") or "en")
            tl = str(data.get("tl") or "bn")

            if not isinstance(text, str) or not text.strip():
                status = 400
                payload = {"ok": False, "error": "অনুবাদের জন্য কোনো টেক্সট পাওয়া যায়নি।"}
            elif provider != "ollama" and not api_key:
                status = 400
                payload = {"ok": False, "error": "API Key প্রয়োজন।"}
            else:
                try:
                    try:
                        from .mt_translate import translate_paragraph_ai
                    except ImportError:
                        from mt_translate import translate_paragraph_ai  # type: ignore[no-redef]
                    translated = translate_paragraph_ai(
                        text,
                        provider=provider,
                        api_key=api_key or None,
                        model=model,
                        base_url=base_url,
                        sl=sl,
                        tl=tl,
                    )
                    status = 200
                    payload = {"ok": True, "translated": translated, "provider": provider}
                except Exception as exc:
                    status = 500
                    payload = {"ok": False, "error": str(exc)}

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/validate":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                data = {}

            text = data.get("text", "")
            if not isinstance(text, str):
                text = ""
            try:
                report = validate_wikitext(text)
                body = json.dumps({"ok": True, "report": report}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            except Exception as e:
                body = json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False).encode("utf-8")
                self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/drafts":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                data = {}

            if data and data.get("title"):
                drafts = load_drafts()
                # Remove duplicate by title if exists
                drafts = [d for d in drafts if d.get("title") != data.get("title")]
                drafts.insert(0, data)
                save_drafts(drafts)
                body = json.dumps({"ok": True, "saved": data}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            else:
                body = json.dumps({"ok": False, "error": "Missing title"}).encode("utf-8")
                self.send_response(400)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif path == "/preview":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            try:
                data = json.loads(raw.decode("utf-8"))
            except ValueError:
                data = {}

            wikitext = data.get("text", "")
            title = data.get("title", "খসড়া:নিবন্ধ")
            if not wikitext.strip():
                body = json.dumps({"ok": True, "html": "<p><em>প্রাকদর্শনের জন্য কোনো উইকিটেক্সট পাওয়া যায়নি।</em></p>"}, ensure_ascii=False).encode("utf-8")
                self.send_response(200)
            else:
                import urllib.parse
                import urllib.request
                parse_data = urllib.parse.urlencode({
                    "action": "parse",
                    "text": wikitext,
                    "title": title,
                    "prop": "text",
                    "contentmodel": "wikitext",
                    "format": "json"
                }).encode("utf-8")
                try:
                    req = urllib.request.Request(
                        "https://bn.wikipedia.org/w/api.php",
                        data=parse_data,
                        headers={"User-Agent": "WikipediaTranslationBot/1.0 (bnwiki-toolkit)"}
                    )
                    with urllib.request.urlopen(req, timeout=20) as resp:
                        res_json = json.loads(resp.read().decode("utf-8"))
                        html = res_json.get("parse", {}).get("text", {}).get("*", "")
                        # প্রাকদর্শন থেকে [সম্পাদনা | উৎস সম্পাদনা] লিংক মুছে ফেলা
                        import re
                        html = re.sub(r'<span class="mw-editsection"[^>]*>[\s\S]*?</span>', '', html)
                        body = json.dumps({"ok": True, "html": html}, ensure_ascii=False).encode("utf-8")
                        self.send_response(200)
                except Exception as e:
                    body = json.dumps({"ok": False, "error": str(e)}).encode("utf-8")
                    self.send_response(500)
            self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        print("cx-server:", format % args)


def main() -> None:
    server = HTTPServer(("127.0.0.1", PORT), _Handler)
    print(f"উইকিপিডিয়া অনুবাদ টুলকিট সার্ভার চলছে: http://127.0.0.1:{PORT}/dashboard  (থামাতে Ctrl+C)")
    server.serve_forever()


if __name__ == "__main__":
    main()
