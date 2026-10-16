# -*- coding: utf-8 -*-
import json, re
from build_mongolia_districts import TRANS_DICT, PROVINCES, bn_sort_key, to_bengali_digits

REPLACEMENTS = {
    '\u09af\u09bc': '\u09df',
    '\u09a1\u09bc': '\u09dc',
    '\u09a2\u09bc': '\u09dd',
}

# Clean TRANS_DICT values initially
for k, v in list(TRANS_DICT.items()):
    for old_c, new_c in REPLACEMENTS.items():
        TRANS_DICT[k] = TRANS_DICT[k].replace(old_c, new_c)

# Load matched pairs
with open('all_matched_pairs.json', encoding='utf-8') as f:
    all_pairs = json.load(f)

# Fix Khovd pair in all_pairs
# In Khovd:
# Jargalant, Khovd|Jargalant (Khovd city) -> mn_name: Жаргалант, mn_raw: Жаргалант сум
# Khovd, Khovd|Khovd (sum) -> mn_name: Ховд, mn_raw: Ховд сум
for it in all_pairs['Khovd']:
    if 'Jargalant' in it['en_raw']:
        it['mn_name'] = 'Жаргалант'
        it['mn_raw'] = 'Жаргалант сум'

# Fix Dundgovi pair
for it in all_pairs['Dundgovi']:
    if 'Saintsagaan' in it['en_raw']:
        it['mn_name'] = 'Сайнцагаан'
        it['mn_raw'] = 'Сайнцагаан сум'

# Fix Zavkhan pair
for it in all_pairs['Zavkhan']:
    if 'Uliastai' in it['en_raw']:
        it['mn_name'] = 'Улиастай'
        it['mn_raw'] = 'Улиастай хот'

TRANS_DICT['Жаргалант'] = 'জার্গালান্ত'
TRANS_DICT['Ховд'] = 'খোভড'
TRANS_DICT['Сайнцагаан'] = 'সাইনসাগান'
TRANS_DICT['Улиастай'] = 'উলিয়াস্তাই'

# Find ambiguous names across provinces
name_prov_map = {}
for p in PROVINCES:
    p_id = p['id']
    for item in all_pairs[p_id]:
        mn = item['mn_name']
        bn = TRANS_DICT[mn]
        name_prov_map.setdefault(bn, set()).add(p['short_name'])

prov_names = set(p['short_name'] for p in PROVINCES)

# Specific manual links where applicable
MANUAL_LINKS = {
    ('Arkhangai', 'Тариат'): 'তারিয়াত',
    ('Arkhangai', 'Эрдэнэбулган'): 'এরদেনেবুলগান',
    ('Bayan-Ölgii', 'Өлгий'): 'ওলগি (শহর)|ওলগি',
    ('Bayankhongor', 'Баянхонгор'): 'বায়ানখোঙ্গর (শহর)|বায়ানখোঙ্গর',
    ('Bayankhongor', 'Заг'): 'জাগ',
    ('Bulgan', 'Булган'): 'বুলগান (শহর)|বুলগান',
    ('Darkhan-Uul', 'Дархан'): 'দারখান (শহর)|দারখান',
    ('Dornod', 'Хэрлэн'): 'খেরলেন, ডরনোড|খেরলেন',
    ('Dornod', 'Чойбалсан'): 'চোইবালসান (সাম)|চোইবালসান',
    ('Dundgovi', 'Сайнцагаан'): 'সাইনসাগান',
    ('Govi-Altai', 'Есөнбулаг'): 'ইয়েসোনবুলাগ',
    ('Govisümber', 'Сүмбэр'): 'সুম্বের, গোভিসুম্বার|সুম্বের',
    ('Khentii', 'Хэрлэн'): 'খেরলেন, খেন্টি|খেরলেন',
    ('Khovd', 'Жаргалант'): 'জার্গালান্ত, খোভড|জার্গালান্ত',
    ('Khovd', 'Ховড'): 'খোভড (সাম)|খোভড',
    ('Khovd', 'Ховд'): 'খোভড (সাম)|খোভড',
    ('Khövsgöl', 'Мөрөн'): 'মরোন (শহর)|মরোন',
    ('Orkhon', 'Баян-Өндөр'): 'বায়ান-ওন্দোর, ওরখোন|বায়ান-ওন্দোর',
    ('Selenge', 'Сүхбаатар'): 'সুখবাতার (শহর)|সুখবাতার',
    ('Sükhbaatar', 'Баруун-Урт'): 'বারুন-উর্ত',
    ('Sükhbaatar', 'Сүхбаатар'): 'সুখবাতার, সুখবাতার|সুখবাতার',
    ('Zavkhan', 'Улиастай'): 'উলিয়াস্তাই'
}

SPECIAL_NOTES = {
    ('Arkhangai', 'Эрдэнэбулган'): ' – প্রাদেশিক রাজধানী [[সেসেরলেগ (শহর)|সেসেরলেগ]]',
    ('Bayan-Ölgii', 'Өлгий'): ' – প্রাদেশিক রাজধানী',
    ('Bayan-Ölgii', 'Цагааннуур'): ' (গ্রাম)',
    ('Bayankhongor', 'Баянхонгор'): ' – প্রাদেশিক রাজধানী',
    ('Bulgan', 'Булган'): ' – প্রাদেশিক রাজধানী',
    ('Darkhan-Uul', 'Дархан'): ' – প্রাদেশিক রাজধানী',
    ('Dornod', 'Хэрлэн'): ' – প্রাদেশিক রাজধানী [[চোইবালসান (শহর)|চোইবালসান]]',
    ('Dornod', 'Чойбалсан'): ' (সাম)',
    ('Dornogovi', 'Сайншанд'): ' – প্রাদেশিক রাজধানী',
    ('Dundgovi', 'Сайнцагаан'): ' – প্রাদেশিক রাজধানী [[মান্দালগোভি]]',
    ('Govi-Altai', 'Есөнбулаг'): ' – প্রাদেশিক রাজধানী [[আলতাই (শহর)|আলতাই]]',
    ('Govisümber', 'Сүмбэр'): ' – প্রাদেশিক রাজধানী [[চোইর (শহর)|চোইর]]',
    ('Khentii', 'Хэрлэн'): ' – প্রাদেশিক রাজধানী [[চেঙ্গিস সিটি]] ([[ওনদোরখান]])',
    ('Khovd', 'Жаргалант'): ' – প্রাদেশিক রাজধানী [[খোভড (শহর)|খোভড]]',
    ('Khovd', 'Ховд'): ' (সাম)',
    ('Khövsgöl', 'Мөрөн'): ' – প্রাদেশিক রাজধানী',
    ('Ömnögovi', 'Даланзадгад'): ' – প্রাদেশিক রাজধানী',
    ('Orkhon', 'Баян-Өндөр'): ' – প্রাদেশিক রাজধানী [[এরদেনেত]]',
    ('Övörkhangai', 'Арвайхээр'): ' – প্রাদেশিক রাজধানী',
    ('Övörkhangai', 'Хархорин'): ' – ঐতিহাসিক [[কারাকোরাম]]',
    ('Selenge', 'Сүхбаатар'): ' – প্রাদেশিক রাজধানী',
    ('Sükhbaatar', 'Баруун-Урт'): ' – প্রাদেশিক রাজধানী',
    ('Töv', 'Зуунмод'): ' – প্রাদেশিক রাজধানী',
    ('Uvs', 'Улаангом'): ' – প্রাদেশিক রাজধানী',
    ('Zavkhan', 'Улиастай'): ' – প্রাদেশিক রাজধানী'
}

lines = []
lines.append("[[চিত্র:Mongolia sum map.png|কেন্দ্র|থাম্ব|৪৫০x৪৫০পিক্সেল|'''মঙ্গোলিয়ার জেলাসমূহের মানচিত্র''']]")
lines.append("একটি '''জেলা''' বা '''সাম''' ({{IPA-en|s|ʊ|m}}; {{lang-mn|сум}}, {{MongolUnicode|ᠰᠤᠮᠤ}}, আক্ষরিক অর্থে: ''তীর''; রুশ ভাষায়: ''সোমোন'') হলো [[মঙ্গোলিয়া]]র দ্বিতীয় স্তরের প্রশাসনিক উপবিভাগ। মঙ্গোলিয়ার ২১টি [[মঙ্গোলিয়ার প্রদেশসমূহ|প্রদেশ]] (আইমাগ) মোট ৩৩০টি জেলায় (সাম) বিভক্ত।<ref>{{ওয়েব উদ্ধৃতি |শিরোনাম=21 аймгийн 330 сум, нийслэлийн 152 хороо болон хилийн чанад дахь ДТГ-ын бүртгэлийн үйл ажиллагаанд ашиглаж буй тоног төхөөрөмжийг шинэчлэнэ |ইউআরএল=http://burtgel.gov.mn/archive/index.php/2424-21-6 |সংগ্রহের-তারিখ=২১ সেপ্টেম্বর ২০২৩ |ওয়েবসাইট=burtgel.gov.mn}}</ref>")
lines.append("")
lines.append("গড়ে প্রতিটি জেলার আয়তন প্রায় {{রূপান্তর|৪২০০|বর্গকিমি|abbr=on}} এবং জনসংখ্যা প্রায় ৫,০০০ জন, যাদের অধিকাংশই যাযাবর পশুপালক। একটি জেলার মোট রাজস্ব আয় প্রায় ১২ কোটি [[মঙ্গোলীয় তোগ্রোক|তোগ্রোক]], যার ৯০% আসে জাতীয় সরকারি ভর্তুকি থেকে।")
lines.append("")
lines.append("প্রতিটি জেলা আবার কয়েকটি ''বাঘ'' বা ''ব্যাগে'' ({{lang-mn|баг}}; ব্রিগেড) বিভক্ত।<ref name=\"mongol\">Montsame News Agency. ''Mongolia''. 2006, Foreign Service office of [[Montsame News Agency]], {{ISBN|99929-0-627-8}}, p. 46</ref> অধিকাংশ বাঘের কোনো স্থায়ী ভৌগোলিক সীমানা থাকে না (কার্যত অদৃশ্য বা তথ্যভিত্তিক)। কোনো স্থায়ী মানব বসতি স্থাপন না করেই জেলার যাযাবর পরিবারগুলোকে বিভিন্ন দলে বিভক্ত করাই এগুলোর মূল উদ্দেশ্য।")
lines.append("")
lines.append("দাপ্তরিকভাবে এবং মানচিত্রে অনেক ক্ষেত্রে জেলা সদরের (সাম কেন্দ্র; {{lang-mn|сумын төв}}) নাম মূল জেলার নাম থেকে ভিন্ন হয়ে থাকে। তবে বাস্তবে জেলা সদরকে সাধারণত জেলার নামেই ডাকা হয়; এমনকি অনেক ক্ষেত্রে জেলা সদরের সরকারি নামটি স্থানীয় বাসিন্দাদের কাছেও অপরিচিত থাকে।")
lines.append("")

for p in PROVINCES:
    p_id = p['id']
    short = p['short_name']
    lines.append(f"== {p['title']} ==")
    lines.append(f"[[চিত্র:{p['map']}|ডান|থাম্ব|{p['map_size']}|{p['short_name']} প্রদেশের জেলাসমূহ]]")
    lines.append(f"; {p['count_text']}")
    
    items_formatted = []
    for item in all_pairs[p_id]:
        mn = item['mn_name']
        bn = TRANS_DICT[mn]
        
        # Determine link
        if (p_id, mn) in MANUAL_LINKS:
            link_target = MANUAL_LINKS[(p_id, mn)]
            if '|' in link_target:
                wikilink = f"[[{link_target}]]"
            else:
                wikilink = f"[[{link_target}|{bn}]]" if link_target != bn else f"[[{bn}]]"
        elif len(name_prov_map[bn]) > 1 or bn in prov_names:
            wikilink = f"[[{bn}, {short}|{bn}]]"
        else:
            wikilink = f"[[{bn}]]"
            
        note = SPECIAL_NOTES.get((p_id, mn), '')
        formatted_entry = f"*{wikilink} ({{{{lang-mn|{mn}}}}}){note}"
        for old_c, new_c in REPLACEMENTS.items():
            formatted_entry = formatted_entry.replace(old_c, new_c)
        items_formatted.append(formatted_entry)
        
    # Sort alphabetically in Bengali
    items_formatted.sort(key=bn_sort_key)
    
    # Render with div col if more than 4 items
    if len(items_formatted) > 4:
        lines.append("{{div col|colwidth=18em}}")
        for it in items_formatted:
            lines.append(it)
        lines.append("{{div col end}}")
    else:
        for it in items_formatted:
            lines.append(it)
            
    lines.append("{{Clear}}")
    lines.append("")

# Ulaanbaatar Düüregs
lines.append("== উলানবাটরের পৌর জেলাসমূহ ==")
lines.append("[[চিত্র:Districts of Ulaanbaatar.svg|ডান|থাম্ব|৩০০x৩০০পিক্সেল|উলানবাটরের পৌর জেলাসমূহের মানচিত্র]]")
lines.append("মঙ্গোলিয়ার রাজধানী [[উলানবাটর]] কোনো প্রদেশের (আইমাগ) অংশ নয়, বরং এটি একটি পৃথক পৌরসভা হিসেবে পরিচালিত হয়। দ্বিতীয় স্তরের প্রশাসনিক উপবিভাগ হিসেবে উলানবাটর ৯টি পৌর জেলায় ({{lang-mn|дүүрэг}}, ''দূরগ'') বিভক্ত, যা আবার ১৫২টি [[খোরা]]-য় ({{lang-mn|хороо}}; ওয়ার্ড) বিভক্ত:")
lines.append("")

ub_items = [
    "*[[খান-উল]] ({{lang-mn|Хан-Уул}})",
    "*[[চিংগেলতেই]] ({{lang-mn|Чингэлтэй}})",
    "*[[নালাইখ]] ({{lang-mn|Наলাইх}})",
    "*[[বাগাবাখানগাই]] ({{lang-mn|Багахангай}})",
    "*[[বাগানুউর]] ({{lang-mn|Багануур}})",
    "*[[বায়ানগোল (উলানবাটর)|বায়ানগোল]] ({{lang-mn|Баянгол}})",
    "*[[বায়ানজুরখ]] ({{lang-mn|Баянзүрх}})",
    "*[[সুখবাতার (উলানবাটর)|সুখবাতার]] ({{lang-mn|Сүхбаатар}})",
    "*[[সোঙ্গিনো খাইরখান]] ({{lang-mn|Сонгинохайрхан}})"
]
ub_items.sort(key=bn_sort_key)

lines.append("{{div col|colwidth=18em}}")
for it in ub_items:
    lines.append(it)
lines.append("{{div col end}}")
lines.append("{{Clear}}")
lines.append("")

# Footer
lines.append("== তথ্যসূত্র ==")
lines.append("{{সূত্র তালিকা}}")
lines.append("")
lines.append("== বহিঃসংযোগ ==")
lines.append("* [http://www.msrm.mn/PDF/2009%20population,%20by%20sum.pdf ২০০৯ সালের ৩১ ডিসেম্বর অনুযায়ী সমস্ত মঙ্গোলীয় সমষ্টির জনসংখ্যা]{{অকার্যকর সংযোগ|date=December 2016}}")
lines.append("")
lines.append("{{Mongolia topics}}")
lines.append("")
lines.append("{{DEFAULTSORT:মঙ্গোলিয়ার জেলা}}")
lines.append("[[বিষয়শ্রেণী:মঙ্গোলিয়ার জেলা| ]]")
lines.append("[[বিষয়শ্রেণী:মঙ্গোলিয়ার উপবিভাগ]]")
lines.append("[[বিষয়শ্রেণী:দেশের দ্বিতীয় স্তরের প্রশাসনিক উপবিভাগ]]")
lines.append("[[বিষয়শ্রেণী:এশিয়ার দেশের প্রশাসনিক উপবিভাগ]]")
lines.append("[[বিষয়শ্রেণী:দেশের প্রশাসনিক উপবিভাগের তালিকা]]")
lines.append("[[বিষয়শ্রেণী:মঙ্গোলিয়ার ভূগোল-সম্পর্কিত তালিকা]]")

output_wikitext = '\n'.join(lines)

# Clean decomposed nuktas
REPLACEMENTS = {
    '\u09af\u09bc': '\u09df',
    '\u09a1\u09bc': '\u09dc',
    '\u09a2\u09bc': '\u09dd',
}
for old_c, new_c in REPLACEMENTS.items():
    output_wikitext = output_wikitext.replace(old_c, new_c)

with open('মঙ্গোলিয়ার জেলা (বাংলা).txt', 'w', encoding='utf-8') as f:
    f.write(output_wikitext)

print('Generated মঙ্গোলিয়ার জেলা (বাংলা).txt successfully!')
print('Total characters:', len(output_wikitext))
