# -*- coding: utf-8 -*-
import binascii
raw = open(".env", "rb").read()
print("bytes:", len(raw))
print("hex:", binascii.hexlify(raw).decode()[:200])
print("repr:", repr(raw)[:300])
for enc in ("utf-8", "utf-16", "utf-16-le", "utf-16-be"):
    try:
        txt = raw.decode(enc)
        print(f"--- decoded as {enc} ---")
        for line in txt.splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                print("  key:", repr(k), "value_len:", len(v), "prefix:", repr(v[:4]))
            elif line.strip():
                print("  line:", repr(line[:20]))
    except Exception as exc:
        print(f"{enc}: {type(exc).__name__}")
