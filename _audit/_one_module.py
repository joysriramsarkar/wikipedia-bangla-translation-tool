# -*- coding: utf-8 -*-
"""Translate one language module's own sample input in an isolated process."""
import difflib
import os
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANG = sys.argv[1]

SPECS = {
    "en": ("ইংরেজি-বাংলা অনুবাদ", "translate_page", "translate_text", "একাডেমি", False),
    "zh": ("চীনা-বাংলা অনুবাদ", "translate_page", "translate_wikipedia_text", "চীনের জেলা", False),
    "ja": ("জাপানি-বাংলা অনুবাদ", "translate_page", "translate_page", "জাপানিদের তালিকা", False),
    "ru": ("রুশ-বাংলা অনুবাদ", "translate_page", "translate_page", "রাশিয়ার জেলা", False),
    "de": ("জার্মান-বাংলা অনুবাদ", "translate_page", "translate_page", "জার্মান চলচ্চিত্রের তালিকা", False),
}

folder, modname, func, needle, _ = SPECS[LANG]
folder_path = os.path.join(ROOT, folder)


def nfc(s):
    return unicodedata.normalize("NFC", s)


files = os.listdir(folder_path)
inputs = [f for f in files if needle in nfc(f) and "(বাংলা)" not in nfc(f) and f.endswith(".txt")]
outputs = [f for f in files if needle in nfc(f) and "(বাংলা)" in nfc(f)]
print(f"{LANG}: input files={inputs} expected={outputs}")
if not inputs:
    sys.exit(2)
src_path = os.path.join(folder_path, inputs[0])
exp_path = os.path.join(folder_path, outputs[0]) if outputs else None

sys.path.insert(0, folder_path)
os.chdir(folder_path)
mod = __import__(modname)
fn = getattr(mod, func)
src = open(src_path, encoding="utf-8").read()
try:
    # de module signature is translate_page(path); ru/ja take the text
    if func == "translate_page" and LANG == "de":
        import tempfile
        tmp = os.path.join(tempfile.gettempdir(), "regress_input.txt")
        open(tmp, "w", encoding="utf-8").write(src)
        out = fn(tmp)
    else:
        out = fn(src)
except Exception as exc:
    print(f"{LANG}: EXCEPTION {type(exc).__name__}: {str(exc)[:200]}")
    sys.exit(3)

expected = open(exp_path, encoding="utf-8").read() if exp_path and os.path.exists(exp_path) else ""
same = nfc(out.strip()) == nfc(expected.strip())
if expected and max(len(out), len(expected)) > 120_000:
    # SequenceMatcher ৬ লাখ অক্ষরে কয়েক মিনিট নেয় — বড় ফাইলে সস্তা মাপ
    a, b = nfc(out), nfc(expected)
    common = sum(1 for x, y in zip(a, b) if x == y)
    ratio = common / max(len(a), len(b))
else:
    ratio = difflib.SequenceMatcher(None, out, expected).ratio() if expected else 0
print(f"{LANG}: in={len(src)} out={len(out)} expected={len(expected)} "
      f"identical={same} similarity={ratio:.3f}")
if not same and expected and max(len(out), len(expected)) <= 120_000:
    diff = list(difflib.unified_diff(expected.splitlines(), out.splitlines(),
                                     "committed", "regenerated", lineterm="", n=0))
    print(f"   diff lines: {len(diff)}")
    for line in diff[:10]:
        print("   ", line[:120])
