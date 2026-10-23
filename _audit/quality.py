# -*- coding: utf-8 -*-
"""Shared helpers: safe article slicing + quality metrics for the audit."""
import re

BN = r"\u0980-\u09FF"
LAT = r"A-Za-z"
CJK = r"\u4E00-\u9FFF\u3040-\u30FF\u3400-\u4DBF"
CYR = r"\u0400-\u04FF"

_SCRIPT_RE = {
    "bengali": re.compile(f"[{BN}]"),
    "latin": re.compile(f"[{LAT}]"),
    "cjk": re.compile(f"[{CJK}]"),
    "cyrillic": re.compile(f"[{CYR}]"),
}


def slice_article(text: str, budget: int = 7000) -> str:
    """Cut an article at a safe boundary: a top-level heading with all
    brackets/templates/refs closed.  Keeps the result valid wikitext."""
    lines = text.splitlines()
    depth_t = depth_b = 0
    ref_open = 0
    keep = []
    size = 0
    for line in lines:
        depth_t += line.count("{{") - line.count("}}")
        depth_b += line.count("[[") - line.count("]]")
        ref_open += len(re.findall(r"<ref\b[^>/]*>", line)) - line.count("</ref>")
        keep.append(line)
        size += len(line) + 1
        if (size >= budget and depth_t <= 0 and depth_b <= 0 and ref_open <= 0
                and re.match(r"^==\s*[^=].*?==\s*$", line)):
            break
    return "\n".join(keep)


def strip_markup(text: str) -> str:
    """Rough 'what the reader sees' extraction (good enough for ratio stats)."""
    s = text
    # drop comments
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.DOTALL)
    # drop reference bodies but keep nothing (citations are not prose)
    s = re.sub(r"<ref\b[^>/]*/>", " ", s)
    s = re.sub(r"<ref\b[^>]*>.*?</ref>", " ", s, flags=re.DOTALL | re.IGNORECASE)
    # drop templates (3 nesting passes)
    for _ in range(4):
        s = re.sub(r"\{\{[^{}]*\}\}", " ", s)
    # tables: keep cell text, drop structural bits
    s = re.sub(r"^\s*\{\|.*$", " ", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*\|\}.*$", " ", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*\|-.*$", " ", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*\|[+|]", " ", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*!\s?", " ", s, flags=re.MULTILINE)
    s = re.sub(r"^\s*\|", " ", s, flags=re.MULTILINE)
    # links: keep display text
    s = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"\[\[([^\]]*)\]\]", r"\1", s)
    # external links: keep label
    s = re.sub(r"\[https?://\S+\s+([^\]]*)\]", r"\1", s)
    s = re.sub(r"\[https?://\S+\]", " ", s)
    # files
    s = re.sub(r"\[\[\s*(?:File|Image|চিত্র|ফাইল)\s*:[^\]]*\]\]", " ", s, flags=re.IGNORECASE)
    # tags, urls, entities
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"&[a-zA-Z#0-9]+;", " ", s)
    # headings markers, bold/italic, list markers
    s = re.sub(r"^=+\s*|\s*=+$", " ", s, flags=re.MULTILINE)
    s = re.sub(r"'{2,}", "", s)
    s = re.sub(r"^[*#:;]+\s*", " ", s, flags=re.MULTILINE)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def script_counts(text: str) -> dict:
    return {name: len(rx.findall(text)) for name, rx in _SCRIPT_RE.items()}


def structure(src: str, out: str) -> dict:
    """Compare structural markers: a healthy pass keeps them balanced/equal."""
    def counts(t):
        return {
            "table_open": t.count("{|"),
            "table_close": t.count("|}"),
            "template_open": t.count("{{"),
            "template_close": t.count("}}"),
            "link_open": t.count("[["),
            "link_close": t.count("]]"),
            "ref_open": len(re.findall(r"<ref\b[^>/]*>", t)),
            "ref_close": t.count("</ref>"),
        }
    c_src, c_out = counts(src), counts(out)
    return {"src": c_src, "out": c_out}


def leaked_tokens(text: str) -> list:
    pats = {
        "ZWPHL placeholder": r"ZWPHL\d+Z",
        "file placeholder": r"__FILE_LINK_PLACEHOLDER_\d+__",
        "private-use char": r"[\uE000-\uF8FF]",
        "NUL token": r"\x00",
    }
    found = []
    for name, pat in pats.items():
        hits = re.findall(pat, text)
        if hits:
            found.append((name, len(hits), hits[0]))
    return found


def leftover_words(src: str, out: str, scripts=("latin", "cjk", "cyrillic")) -> list:
    """Words from the source language that survived into the output."""
    pat = "|".join(_SCRIPT_RE[s].pattern.strip("[]") for s in scripts)
    word_re = re.compile(f"[{pat}]{{2,}}")
    out_words = set(w.lower() for w in word_re.findall(out))
    src_words = [w for w in word_re.findall(strip_markup(src))]
    seen = {}
    for w in src_words:
        if w.lower() in out_words and len(w) >= 3:
            seen[w] = seen.get(w, 0) + 1
    top = sorted(seen.items(), key=lambda kv: -kv[1])
    return top


def headings(text: str) -> list:
    return re.findall(r"^(={1,6})\s*([^=\n]+?)\s*\1\s*$", text, flags=re.MULTILINE)
