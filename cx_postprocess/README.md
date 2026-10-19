# CX পোস্ট-প্রসেসর (প্রোটোটাইপ)

ContentTranslation ড্রপডাউনে ঢোকার আগের ধাপ: CX ড্রাফটের সংখ্যা + ইনফোবক্স ঠিক করা।

## মডিউল

- `bn_digits_safe.py` — `to_bengali_digits_safe(text)`:
  কেন্দ্রীয় বাস্তবায়ন `common/bengali_utils.py`-এর পাতলা মোড়ক।
  HTML ট্যাগ অক্ষত রেখে দৃশ্যমান `0-9 → ০-৯`, `2nd → ২য়`।
  URL / `<ref>` / File / coord / ISBN সুরক্ষিত।
- `infobox_map.py` — `translate_infobox(wikitext)`:
  `{{Infobox settlement}} → {{তথ্যছক বসতি}}`, পরিচিত প্যারাম + লেবেল
  (`Country → দেশ`), মানের সংখ্যা বাংলা। অচেনা প্যারাম ফেলে না,
  রিপোর্ট করে। ধর্মীয় ভবন-জাতীয় টেমপ্লেটে ইংরেজি প্যারাম কী অক্ষত থাকে
  (bnwiki টেমপ্লেট ইংরেজি কী ব্যবহার করে) এবং অসমর্থিত `mapframe*` বাদ যায়।
- `mt_translate.py` — উইকিটেক্সট-সচেতন মেশিন অনুবাদ। গুগল gtx ব্যর্থ/429 হলে
  `clients5` ও শেষে MyMemory ফলব্যাক; প্লেসহোল্ডার উল্টো ক্রমে পুনরুদ্ধার হয়,
  তাই nested টেমপ্লেটের টোকেন লিক করে না। চিত্র/মানচিত্রের নাম, URL ও
  হ্যাঁ/না মান অনূদিত হয় না।
- `currency_fix.py` — চিহ্ন (`R$`, `US$`) রাখা হয় (bn রীতি), নাম বাংলায়:
  `dollars → ডলার`, `USD → মার্কিন ডলার`, `BRL → ব্রাজিলীয় রিয়াল`।
- `table_fix.py` — `rowspan`/`colspan` ল্যাটিন রাখা, `|-` পৃথক লাইনে,
  খালি ঘরে `&nbsp;`, ঘরের মান বাংলা।
- `template_fix.clean_templatestyles_remnants` — বৈধ
  `<templatestyles src="…"/>` রাখা, ভাঙা `</> templatestyles` লাইন মোছা।

## চালানো

```bash
python -m pytest tests/test_cx_postprocess.py tests/test_cx_stage2.py tests/test_cx_stage3.py -v
```

## লোকাল API + ইউজারস্ক্রিপ্ট (ধাপ-২)

```bash
python -m cx_postprocess.server
# → http://127.0.0.1:8765  (GET /health, POST /fix, POST /validate)
```

- `pipeline.py` — `fix_text(text)` → `{"fixed", "unknown_params"}`।
  ক্রম: টেমপ্লেট → ইনফোবক্স → টেবিল → মুদ্রা → একক/তারিখ → বাংলা অঙ্ক।
- `server.py` — লোকাল `/fix` ছাড়াও cxserver-সামঞ্জস্য:
  `GET /v2/list/mt/en/bn`, `GET /v2/translate/en/bn/<text>`।
  নিজের cxserver-এর সামনে বসানো যায়; WMF প্রোডাকশন ড্রপডাউনে ওঠা
  আলাদা অনুমোদন (Phabricator + `MTSERVICE.yaml` + SRE) সাপেক্ষ।
- `userscript.js` — Tampermonkey-তে ইনস্টল করুন (শুধু
  `bn.wikipedia.org/wiki/Special:ContentTranslation*`-এ চলে)।
  CX পেজে নিচে-ডানে প্যানেল আসে: ড্রাফট পেস্ট → ঠিক করো → কপি।
  v0.1 ইচ্ছা করে CX এডিটরে সরাসরি হাত দেয় না, যাতে VE না ভাঙে।
