# Cloudflare-এ ডেপ্লয়মেন্ট: বর্তমান অবস্থা

## সংক্ষেপে

ড্যাশবোর্ড এখন `public/`-এ স্ট্যাটিক ফাইল হিসেবে আছে এবং `wrangler.toml`
`[assets]` কনফিগ সহ। তাই `npx wrangler deploy` সফল হবে এবং
`https://<worker>/dashboard.html` খুলবে।

তবে **Cloudflare ডেপ্লয়ে API নেই**: `/fix`, `/validate`, `/fetch`,
`/preview` রুট Flask/Python-এ চলে, যা শুধু Vercel বা লোকাল সার্ভারে আছে।
Cloudflare-এ যাচাই ও অনুবাদ বোতামগুলো `/fix`/`/validate`-এ ৪০৪ পাবে;
ড্যাশবোর্ডের কিছু ক্লায়েন্ট-সাইড ফলব্যাক থাকলেও পূর্ণ কার্যকারিতা নেই।

## বিকল্প

### ১. পূর্ণ অ্যাপ: Vercel

`app.py` (Flask) + `public/` — Vercel-এ সব API কাজ করে। বিস্তারিত
`docs/VERCEL.md`-এ।

### ২. Cloudflare Tunnel (লোকাল Python সার্ভার)

```bash
python -m cx_postprocess.server
cloudflared tunnel --url http://127.0.0.1:8765
```

`cloudflared` ইনস্টল নেই; ইনস্টল ও Cloudflare লগইন লাগবে। কম্পিউটার চালু
থাকতে হবে।

### ৩. Cloudflare-এ Pages Functions পোর্ট

`/fix` ও `/validate`-এর যুক্তি JavaScript-এ পোর্ট করে `functions/api/...`
বানালে Cloudflare-ও পূর্ণ কার্যকর হবে। এটি এখন করা হয়নি; Python-ই
canonical implementation।

## স্ট্যাটিক ডেপ্লয়

```bash
npx wrangler deploy
```

`public/index.html` → `/dashboard.html` রিডাইরেক্ট করে। স্ট্যাটিক মোডেও
ক্লায়েন্ট-সাইড পথে দৃশ্যমান অঙ্ক বাংলা, ছবির ক্যাপশন অনূদিত এবং
`{{Series overview}}`-জাতীয় টেবিল-টেমপ্লেটের নাম/প্যারামিটার অক্ষত থাকে।
সম্পাদনা/যাচাইয়ের API-র জন্য Vercel বা Tunnel ব্যবহার করুন।
