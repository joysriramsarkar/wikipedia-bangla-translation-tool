# Vercel-এ ডেপ্লয়মেন্ট

## কী আছে

- `app.py` — Flask অ্যাপ, top-level `app` অবজেক্ট (WSGI)।
- `vercel.json` — `app.py` ফাংশনের `maxDuration: 60`।
- `public/index.html` — `/` থেকে `/dashboard.html`-এ রিডাইরেক্ট।
- `public/dashboard.html` — ড্যাশবোর্ড (স্ট্যাটিক অ্যাসেট)।
- `requirements.txt` — `flask`, `pypinyin`, `requests` ইত্যাদি।
- `pyproject.toml` — `[tool.vercel] entrypoint = "app:app"`।

Vercel Flask preset শনাক্ত করে সব অনুরোধ Flask অ্যাপে পাঠায়; `public/**`
আগে CDN থেকে সার্ভ হয়। তাই `/dashboard.html` স্ট্যাটিক, আর `/fix`,
`/validate`, `/fetch`, `/preview` ইত্যাদি Flask রুটে চলে।

## রুট

| রুট | কাজ |
|---|---|
| `/health` | স্বাস্থ্য |
| `/fix` | পোস্ট-প্রসেস / মেশিন অনুবাদ |
| `/validate` | ৯ নিয়মের যাচাই |
| `/fetch` | উইকিপিডিয়া থেকে উইকিটেক্সট |
| `/search` | শিরোনাম সার্চ |
| `/preview` | বাংলা উইকি API দিয়ে প্রাকদর্শন |
| `/translate_title` | langlinks/Google |
| `/drafts` | খসড়া (Vercel-এ `/tmp`, স্থায়ী নয়) |

## স্থানীয় পরীক্ষা

```bash
python -m pip install -r requirements.txt
python app.py
# http://127.0.0.1:8765/dashboard
```

অথবা টেস্ট:

```bash
python run_all_tests.py
```

## সীমা

- Vercel Function সর্বোচ্চ ৬০ সেকেন্ড (`vercel.json`)। খুব বড় নিবন্ধের
  মেশিন অনুবাদ সময়সীমা ছাড়াতে পারে; ছোট/মাঝারি নিবন্ধ নিরাপদ।
- Vercel-এ ফাইলসিস্টেম read-only; খসড়া `/tmp`-এ যায়, redeploy/নতুন
  instance-এ থাকবে না। স্থায়ী খসড়ার জন্য ডেটাবেস দরকার।
- `demo/`, `tests/`, `archive/` `.vercelignore`-এ বাদ দেওয়া হয়েছে।
