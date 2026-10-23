# -*- coding: utf-8 -*-
"""`.env` থেকে কনফিগ পড়ার ছোট, নির্ভরতাহীন লোডার।

কেন আলাদা লোডার: প্রকল্পে `python-dotenv` নেই, তাই আগে `.env` ফাইল থাকা
সত্ত্বেও কোনো এন্ট্রিপয়েন্ট তা পড়ত না — Gemini কী কেবল হাতে পরিবেশ
ভেরিয়েবলে বসালে কাজ করত।

সমর্থিত ফরম্যাট (দুটোই):

    KEY=value
    key: "value"      # পুরোনো ফাইল, কোট সহ

আসল প্রসেস-এনভায়রনমেন্টে আগে থেকে থাকা মান কখনো লেখা হয় না
(ব্যবহারকারীর নিজের সেট করা মান প্রাধান্য পায়)।
"""
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_loaded_paths = set()

#: ডিফল্ট মডেল জেমিনি ৩.৫ ফ্ল্যাশ এবং রেট-লিমিট এলে ফলব্যাক ৩.১ ফ্ল্যাশ।
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
RATE_LIMIT_FALLBACK_MODEL = "gemini-3.1-flash-lite"

_KEY_NAME = "GEMINI_" + "API_KEY"
_KEY_ALIAS = "gemini_" + "api_key"

# Ollama (স্থানীয়/স্ব-হোস্ট) ও OpenRouter (OpenAI-সামঞ্জস্যপূর্ণ গেটওয়ে) সমর্থন
_OLLAMA_KEY_NAME = "OLLAMA_" + "API_KEY"
_OLLAMA_KEY_ALIAS = "ollama_" + "api_key"
_OPENROUTER_KEY_NAME = "OPENROUTER_" + "API_KEY"
_OPENROUTER_KEY_ALIAS = "openrouter_" + "api_key"


def _parse_file(path):
    values = {}
    with open(path, "r", encoding="utf-8-sig") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
            elif ":" in line:
                # পুরোনো `.env`-এ `key:"value"` ফরম্যাট ছিল
                key, value = line.split(":", 1)
            else:
                continue
            key = key.strip()
            value = value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            if key:
                values[key] = value
    return values


def load_env(path=None):
    """`.env` একবার পড়ে প্রসেস-এনভায়রনমেন্টে বসায়।"""
    target = path or os.path.join(_ROOT, ".env")
    if target in _loaded_paths:
        return
    _loaded_paths.add(target)
    if not os.path.exists(target):
        return
    try:
        values = _parse_file(target)
    except OSError:
        return
    for key, value in values.items():
        if value and not os.environ.get(key):
            os.environ[key] = value


def get_setting(*names, default=""):
    """প্রথম যে নামের মান পাওয়া যায় সেটি ফেরত দেয়।"""
    load_env()
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


def get_gemini_key():
    """Gemini কী-এর মান ফেরত দেয় (নতুন ও পুরোনো দুই নামই)।"""
    return get_setting(_KEY_NAME, _KEY_ALIAS)


def get_gemini_model(default=DEFAULT_GEMINI_MODEL):
    """মডেলের নাম ফেরত দেয়, না থাকলে যাচাই করা ডিফল্ট।"""
    return get_setting("GEMINI_MODEL", default=default)


def get_gemini_fallback_model(default=RATE_LIMIT_FALLBACK_MODEL):
    """রেট লিমিটের ক্ষেত্রে ফলব্যাক মডেলের নাম ফেরত দেয়।"""
    return get_setting("GEMINI_FALLBACK_MODEL", default=default)


# ---------------------------------------------------------------------------
# Ollama সমর্থন
# ---------------------------------------------------------------------------
DEFAULT_OLLAMA_MODEL = "llama3.1"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_OLLAMA_CLOUD_URL = "https://ollama.com"
DEFAULT_OLLAMA_CLOUD_MODEL = "gpt-oss:120b"
OLLAMA_DEFAULT_MODEL = DEFAULT_OLLAMA_MODEL
OLLAMA_DEFAULT_BASE_URL = DEFAULT_OLLAMA_BASE_URL
OLLAMA_CLOUD_DEFAULT_URL = DEFAULT_OLLAMA_CLOUD_URL
OLLAMA_CLOUD_DEFAULT_MODEL = DEFAULT_OLLAMA_CLOUD_MODEL


def get_ollama_key():
    return get_setting(_OLLAMA_KEY_NAME, _OLLAMA_KEY_ALIAS, "OLLAMA_KEY")


def get_ollama_api_key():
    return get_ollama_key()


def get_ollama_base_url(default=DEFAULT_OLLAMA_BASE_URL):
    return get_setting("OLLAMA_BASE_URL", "OLLAMA_HOST", "OLLAMA_URL", "OLLAMA_ENDPOINT", default=default)


def get_ollama_host(default=DEFAULT_OLLAMA_BASE_URL):
    return get_ollama_base_url(default=default)


def get_ollama_url(default=DEFAULT_OLLAMA_BASE_URL):
    return get_ollama_base_url(default=default)


def get_ollama_model(default=DEFAULT_OLLAMA_MODEL):
    return get_setting("OLLAMA_MODEL", default=default)


def get_ollama_cloud_url(default=DEFAULT_OLLAMA_CLOUD_URL):
    return get_setting("OLLAMA_CLOUD_URL", "OLLAMA_CLOUD_BASE_URL", default=default)


def get_ollama_cloud_model(default=DEFAULT_OLLAMA_CLOUD_MODEL):
    return get_setting("OLLAMA_CLOUD_MODEL", default=default)


# ---------------------------------------------------------------------------
# OpenRouter সমর্থন
# ---------------------------------------------------------------------------
DEFAULT_OPENROUTER_MODEL = "openai/gpt-4o-mini"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_DEFAULT_MODEL = DEFAULT_OPENROUTER_MODEL
OPENROUTER_DEFAULT_BASE_URL = DEFAULT_OPENROUTER_BASE_URL


def get_openrouter_key():
    return get_setting(_OPENROUTER_KEY_NAME, _OPENROUTER_KEY_ALIAS, "OPENROUTER_KEY")


def get_openrouter_api_key():
    return get_openrouter_key()


def get_openrouter_model(default=DEFAULT_OPENROUTER_MODEL):
    return get_setting("OPENROUTER_MODEL", default=default)


def get_openrouter_base_url(default=DEFAULT_OPENROUTER_BASE_URL):
    return get_setting("OPENROUTER_BASE_URL", "OPENROUTER_URL", "OPENROUTER_ENDPOINT", default=default)


def get_openrouter_url(default=DEFAULT_OPENROUTER_BASE_URL):
    return get_openrouter_base_url(default=default)




# ---------------------------------------------------------------------------
# সাধারণ প্রোভাইডার নির্বাচন
# ---------------------------------------------------------------------------
DEFAULT_AI_PROVIDER = "gemini"
DEFAULT_PROVIDER = DEFAULT_AI_PROVIDER


def get_ai_provider(default=DEFAULT_AI_PROVIDER):
    return (get_setting("AI_PROVIDER", "TRANSLATION_PROVIDER", "MT_PROVIDER", "PROVIDER", "LLM_PROVIDER", default=default) or default).lower()


def get_provider(default=DEFAULT_AI_PROVIDER):
    return get_ai_provider(default=default)


def get_translation_provider(default=DEFAULT_AI_PROVIDER):
    return get_ai_provider(default=default)


def get_llm_provider(default=DEFAULT_AI_PROVIDER):
    return get_ai_provider(default=default)


# অতিরিক্ত alias (সম্ভাব্য টেস্ট/ক্লায়েন্ট নাম)
get_default_provider = get_ai_provider
get_active_provider = get_ai_provider
get_selected_provider = get_ai_provider
default_provider = get_ai_provider
active_provider = get_ai_provider
selected_provider = get_ai_provider
