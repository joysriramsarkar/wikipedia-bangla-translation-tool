# -*- coding: utf-8 -*-
"""Which links / refs / templates are lost, and under what line shape?"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import quality as Q  # noqa: E402


def refs(text):
    bodies = re.findall(r"<ref\b[^>/]*>(.*?)</ref>", text, flags=re.DOTALL)
    named = set(re.findall(r'<ref\b[^>]*name\s*=\s*["\']?([^"\'\s/>]+)', text))
    return bodies, named


for lang in ("de", "zh", "ja", "ru", "en"):
    clip = Q.slice_article(open(os.path.join(HERE, "src", f"{lang}.wikitext"), encoding="utf-8").read(), 5000)
    out = open(os.path.join(HERE, "out", f"mt_{lang}.txt"), encoding="utf-8").read()
    print("=" * 72)
    print(f"LANG {lang}: clip {len(clip)} chars / out {len(out)} chars")

    src_links = re.findall(r"\[\[([^\]\|#]+)", clip)
    out_links = re.findall(r"\[\[([^\]\|#]+)", out)
    from collections import Counter
    c_src, c_out = Counter(src_links), Counter(out_links)
    lost = [t for t in c_src if c_out[t] < c_src[t]]
    print(f"  links: {sum(c_src.values())} -> {sum(c_out.values())}; distinct lost = {len(lost)}")
    for t in lost[:8]:
        print(f"    lost x{c_src[t]-c_out[t]}: {t.strip()[:60]!r}")

    b_src, n_src = refs(clip)
    b_out, n_out = refs(out)
    missing_names = sorted(n_src - n_out)
    print(f"  refs: bodies {len(b_src)} -> {len(b_out)}; names {len(n_src)} -> {len(n_out)}; "
          f"missing names={missing_names[:6]}")

    # Which source lines vanished entirely (normalised)?
    def norms(t):
        return [re.sub(r"\s+", " ", l).strip() for l in t.splitlines() if l.strip()]
    src_lines, out_text = norms(clip), re.sub(r"\s+", " ", out)
    vanished = [l for l in src_lines if len(l) > 40 and l[:40] not in out_text]
    print(f"  source lines >40 chars not found in output: {len(vanished)}/{len(src_lines)}")
    for l in vanished[:4]:
        print("    gone:", l[:100])
