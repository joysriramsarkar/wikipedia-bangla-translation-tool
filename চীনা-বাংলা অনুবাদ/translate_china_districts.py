# -*- coding: utf-8 -*-
"""
চীনা-বাংলা উইকিপিডিয়া নিবন্ধ অনুবাদক: 市辖区 (中华人民共和国) -> নগর জেলা (গণচীন)
সম্পূর্ণ অনুবাদ মডিউল
"""
import sys
import os
import re

_current_dir = os.path.dirname(os.path.abspath(__file__))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from number_converter import to_bengali_digits
from transliteration import hanzi_to_bn, get_bengali_division_name
from links_dictionary import LINK_MAP
from test_cells import split_row_cells, r1, r2
from build_translation_data import get_district_bn, SPECIAL_CITIES

# ১. মাস তালিকা
MONTHS = {
    1: 'জানুয়ারি', 2: 'ফেব্রুয়ারি', 3: 'মার্চ', 4: 'এপ্রিল',
    5: 'মে', 6: 'জুন', 7: 'জুলাই', 8: 'আগস্ট',
    9: 'সেপ্টেম্বর', 10: 'অক্টোবর', 11: 'নভেম্বর', 12: 'ডিসেম্বর'
}

# ২. তারিখ অনুবাদ
def translate_dates(text):
    # Full date: YYYY年M月D日 or YYYY年M月 or YYYY年
    def repl_full(m):
        y, mon, d = m.group(1), m.group(2), m.group(3)
        if y and mon and d:
            return f'{to_bengali_digits(str(int(d)))} {MONTHS[int(mon)]} {to_bengali_digits(str(y))} '
        elif y and mon:
            return f'{MONTHS[int(mon)]} {to_bengali_digits(str(y))} '
        elif y:
            return f'{to_bengali_digits(str(y))} সাল '
        return m.group(0)

    text = re.sub(r'(\d{4})年(?:(\d{1,2})月(?:(\d{1,2})日)?)?', repl_full, text)

    # Partial date: M月D日
    def repl_md(m):
        mon, d = m.group(1), m.group(2)
        return f'{to_bengali_digits(str(int(d)))} {MONTHS[int(mon)]} '

    text = re.sub(r'(\d{1,2})月(\d{1,2})日', repl_md, text)

    # Month only: M月
    def repl_m(m):
        mon = m.group(1)
        return f'{MONTHS[int(mon)]} '

    text = re.sub(r'(\d{1,2})月', repl_m, text)
    return text.strip()

from extra_approvals import EXTRA_APPROVALS, STATIC_APPROVAL_REPLACEMENTS

PROVINCE_GOV_NAMES = {
    '北京市': 'পেইচিং পৌর',
    '天津市': 'থিয়েনচিন পৌর',
    '上海市': 'সাংহাই পৌর',
    '重庆市': 'ছুংছিং পৌর',
    '河北省': 'হেবেই প্রাদেশিক',
    '山西省': 'শানশি প্রাদেশিক',
    '内蒙古自治区': 'অভ্যন্তরীণ মঙ্গোলিয়া স্বায়ত্তশাসিত অঞ্চল',
    '辽宁省': 'লিয়াওনিং প্রাদেশিক',
    '辽东省': 'লিয়াওতুং প্রাদেশিক',
    '辽西省': 'লিয়াওসি প্রাদেশিক',
    '吉林省': 'চিলিন প্রাদেশিক',
    '黑龙江省': 'হেইলুংচিয়াং প্রাদেশিক',
    '江苏省': 'চিয়াংসু প্রাদেশিক',
    '浙江省': 'চচিয়াং প্রাদেশিক',
    '安徽省': 'আনহুই প্রাদেশিক',
    '福建省': 'ফুচিয়ান প্রাদেশিক',
    '江西省': 'চিয়াংশি প্রাদেশিক',
    '山东省': 'শানতুং প্রাদেশিক',
    '河南省': 'হোনান প্রাদেশিক',
    '湖北省': 'হুবেই প্রাদেশিক',
    '湖南省': 'হুনান প্রাদেশিক',
    '广东省': 'কুয়াংতুং প্রাদেশিক',
    '广西壮族自治区': 'কুয়াংশি চুয়াং স্বায়ত্তশাসিত অঞ্চল',
    '海南省': 'হাইনান প্রাদেশিক',
    '四川省': 'সিছুয়ান প্রাদেশিক',
    '贵州省': 'কুয়েইচৌ প্রাদেশিক',
    '云南省': 'ইউন্নান প্রাদেশিক',
    '西藏自治区': 'তিব্বত স্বায়ত্তশাসিত অঞ্চল',
    '陕西省': 'শাআনশি প্রাদেশিক',
    '甘肃省': 'কানসু প্রাদেশিক',
    '青海省': 'ছিংহাই প্রাদেশিক',
    '宁夏回族自治区': 'নিংমিয়া হুই স্বায়ত্তশাসিত অঞ্চল',
    '新疆维吾尔自治区': 'শিনচিয়াং উইগুর স্বায়ত্তশাসিত অঞ্চল',
}

# ৩. অনুমোদন ও দলিল অনুবাদ
def translate_approvals(text):
    # Provincial and municipal authorities
    def repl_prov_auth(m):
        place = m.group(1)
        body = m.group(2)
        if place in PROVINCE_GOV_NAMES:
            place_bn = PROVINCE_GOV_NAMES[place]
        elif place in SPECIAL_CITIES or place.replace('市', '') in SPECIAL_CITIES:
            base = SPECIAL_CITIES.get(place, SPECIAL_CITIES.get(place.replace('市', '')))
            place_bn = f'{base} পৌর'
        else:
            base = hanzi_to_bn(place.replace('省', '').replace('市', '').replace('自治区', ''))
            suffix = ' প্রাদেশিক' if '省' in place else (' পৌর' if '市' in place else '')
            place_bn = f'{base}{suffix}'

        if '人民政府' in body:
            return f'{place_bn} জনসরকার কর্তৃক অনুমোদিত'
        elif '人民委员会' in body:
            return f'{place_bn} গণকমিটি কর্তৃক অনুমোদিত'
        elif '革命委员会' in body:
            return f'{place_bn} বিপ্লবী কমিটি কর্তৃক অনুমোদিত'
        return m.group(0)

    text = re.sub(r'([\u4e00-\u9fa5]+(?:省|市|自治区))(人民政府批准|人民委员会批准|革命委员会批准)', repl_prov_auth, text)

    # Static replacements
    for zh_s, bn_s in STATIC_APPROVAL_REPLACEMENTS:
        text = text.replace(zh_s, bn_s)

    # Regex extra approvals
    for pattern, repl in EXTRA_APPROVALS:
        text = re.sub(pattern, repl, text)

    # Documents
    text = re.sub(r'国函〔(\d+)〕(\d+)号', lambda m: f'স্টেট কাউন্সিল পত্র〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'民行批〔(\d+)〕(\d+)号', lambda m: f'বেসামরিক প্রশাসন অনুমোদন〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'民发〔(\d+)〕(\d+)号', lambda m: f'বেসামরিক বিষয়ক প্রকাশনা〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'民〔(\d+)〕行批(\d+)号', lambda m: f'বেসামরিক বিষয়ক প্রশাসন অনুমোদন〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'国发〔(\d+)〕(\d+)号', lambda m: f'স্টেট কাউন্সিল প্রকাশনা〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'（(\d+)）国函字(\d+)号', lambda m: f'স্টেট কাউন্সিল পত্র ({to_bengali_digits(m.group(1))}) {to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'（(\d+)）内简字(\d+)号', lambda m: f'অভ্যন্তরীণ বিষয়ক পত্র ({to_bengali_digits(m.group(1))}) {to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'鄂革文〔(\d+)〕(\d+)号', lambda m: f'হুবেই বিপ্লবী নথি〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'浙政发〔(\d+)〕(\d+)号', lambda m: f'চচিয়াং সরকার আদেশ〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'川府函〔(\d+)〕(\d+)号', lambda m: f'সিছুয়ান সরকার পত্র〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)
    text = re.sub(r'黑政函〔(\d+)〕(\d+)号', lambda m: f'হেইলুংচিয়াং সরকার পত্র〔{to_bengali_digits(m.group(1))}〕{to_bengali_digits(m.group(2))} নম্বর', text)

    # Authorities
    text = text.replace('国务院批准', 'স্টেট কাউন্সিল কর্তৃক অনুমোদিত')
    text = text.replace('民政部批准', 'বেসামরিক বিষয়ক মন্ত্রণালয় কর্তৃক অনুমোদিত')
    text = text.replace('内务部批准', 'অভ্যন্তরীণ বিষয়ক মন্ত্রণালয় কর্তৃক অনুমোদিত')
    text = text.replace('政务院批准', 'সরকারি প্রশাসনিক পরিষদ কর্তৃক অনুমোদিত')
    text = text.replace('民政部批复', 'বেসামরিক বিষয়ক মন্ত্রণালয় কর্তৃক অনুমোদিত')
    text = text.replace('国务院批复', 'স্টেট কাউন্সিল কর্তৃক অনুমোদিত')
    text = text.replace('民政部备案', 'বেসামরিক বিষয়ক মন্ত্রণালয়ে নথিবদ্ধ')
    text = text.replace('华东军政委员会批准', 'পূর্ব চীন সামরিক ও প্রশাসনিক কমিটি কর্তৃক অনুমোদিত')
    text = text.replace('中南军政委员会批准', 'মধ্য-দক্ষিণ সামরিক ও প্রশাসনিক কমিটি কর্তৃক অনুমোদিত')
    text = text.replace('西南军政委员会批准', 'দক্ষিণ-পশ্চিম সামরিক ও প্রশাসনিক কমিটি কর্তৃক অনুমোদিত')
    text = text.replace('西北军政委员会批准', 'উত্তর-পশ্চিম সামরিক ও প্রশাসনিক কমিটি কর্তৃক অনুমোদিত')
    text = text.replace('东北人民政府批准', 'উত্তর-পূর্ব জনসরকার কর্তৃক অনুমোদিত')
    text = text.replace('华北人民政府批准', 'উত্তর চীন জনসরকার কর্তৃক অনুমোদিত')

    return text

# ৪. উইকিলিংক অনুবাদ (টেক্সটের মধ্যে থাকা লিংক)
def translate_wikilinks_in_text(text):
    def repl(m):
        full = m.group(1).strip()
        if '|' in full:
            target, label = full.split('|', 1)
        else:
            target, label = full, full

        target = target.strip()
        label = label.strip()

        # Check special cities
        if target in SPECIAL_CITIES:
            bn_t = SPECIAL_CITIES[target]
            bn_l = SPECIAL_CITIES.get(label, bn_t)
            return f'[[{bn_t}|{bn_l}]]' if bn_l != bn_t else f'[[{bn_t}]]'

        # Check if target has disambiguator: e.g. '大港区 (天津市)'
        m_dis = re.match(r'^(.*?)\s*\((.*?)\)$', target)
        if m_dis:
            base_t = m_dis.group(1).strip()
            disam = m_dis.group(2).strip()
            disam_bn = SPECIAL_CITIES.get(disam, hanzi_to_bn(disam.replace('市', '').replace('省', '')))
            base_bn = get_district_bn(base_t) if base_t.endswith('区') else get_bengali_division_name(base_t)
            lbl_bn = get_district_bn(label) if label.endswith('区') else get_bengali_division_name(label)
            return f'[[{base_bn} ({disam_bn})|{lbl_bn}]]'

        # Standard district, county, city
        if target.endswith('区'):
            base_bn = get_district_bn(target)
            lbl_bn = get_district_bn(label) if label != target else base_bn
            return f'[[{base_bn}|{lbl_bn}]]' if lbl_bn != base_bn else f'[[{base_bn}]]'
        elif target.endswith('县') or target.endswith('旗') or target.endswith('市'):
            base_bn = get_bengali_division_name(target)
            lbl_bn = get_bengali_division_name(label) if label != target else base_bn
            return f'[[{base_bn}|{lbl_bn}]]' if lbl_bn != base_bn else f'[[{base_bn}]]'
        elif target == '中国抗日战争':
            return '[[দ্বিতীয় চীন-জাপান যুদ্ধ|চীন-জাপান যুদ্ধ]]'

        return m.group(0)

    return re.sub(r'\[\[([^\]]+)\]\]', repl, text)

# ৫. অবশিষ্ট চীনা হানজি অনুবাদ
def transliterate_remaining_hanzi(text):
    # Don't touch wiki tags, attributes, or templates
    def repl_hz(m):
        w = m.group(0)
        if w in SPECIAL_CITIES:
            return SPECIAL_CITIES[w]
        if w.endswith('街道'):
            return f'{hanzi_to_bn(w[:-2])} উপজেলা'
        elif w.endswith('镇'):
            return f'{hanzi_to_bn(w[:-1])} শহর'
        elif w.endswith('乡'):
            return f'{hanzi_to_bn(w[:-1])} জনপদ'
        elif w.endswith('矿区'):
            return f'{hanzi_to_bn(w[:-2])} খনি জেলা'
        elif w.endswith('区'):
            return get_district_bn(w)
        elif w.endswith('县'):
            return get_bengali_division_name(w)
        elif w.endswith('市'):
            return get_bengali_division_name(w)
        else:
            return hanzi_to_bn(w)

    # Protect templates like {{lang|zh-Hans|...}} or {{NoteTag|...}}
    protected = []
    def save_prot(m):
        protected.append(m.group(0))
        return f'__PROT_{len(protected)-1}__'

    text = re.sub(r'\{\{[^}]+\}\}', save_prot, text)
    text = re.sub(r'\[\[[^\]]+\]\]', save_prot, text)

    text = re.sub(r'[\u4e00-\u9fa5]+', repl_hz, text)

    for idx, p in enumerate(protected):
        text = text.replace(f'__PROT_{idx}__', p)

    return text

# ৬. পূর্ণাঙ্গ মন্তব্য ও প্রতিষ্ঠা পদ্ধতি অনুবাদ
def translate_remarks_and_methods(text):
    if not text or text.strip() == '&nbsp;' or text.strip() == '':
        return '&nbsp;'

    # ১. নোট ট্যাগ আলাদা অনুবাদ
    def repl_notetag(m):
        inner = m.group(1)
        tr_inner = translate_remarks_and_methods(inner)
        return f'{{{{NoteTag|{tr_inner}}}}}'
    text = re.sub(r'\{\{noteTag\|([^}]+)\}\}', repl_notetag, text)

    # ২. তারিখ রূপান্তর
    text = translate_dates(text)

    # ৩. অনুমোদন রূপান্তর
    text = translate_approvals(text)

    # ৪. উইকিলিংক রূপান্তর
    text = translate_wikilinks_in_text(text)

    # ৫. প্রশাসনিক ক্রিয়াপদ ও বাক্যাংশ রূপান্তর
    PHRASE_REPLACEMENTS = [
        ('抗日战争结束后，市区分划为', 'চীন-জাপান যুদ্ধ শেষে শহরাঞ্চল বিভক্ত করা হয়: '),
        ('将市区划分为', 'পৌর এলাকা বিভক্ত করে গঠিত: '),
        ('市区分划为', 'পৌর এলাকা বিভক্ত করে গঠিত: '),
        ('划分为', 'বিভক্ত করে গঠিত: '),
        ('重组为', 'পুনর্গঠন করে '),
        ('调整为', 'পুনর্গঠন করে '),
        ('撤县设区（原县级', 'কাউন্টি বিলুপ্ত করে জেলা প্রতিষ্ঠা (সাবেক কাউন্টি-স্তরের '),
        ('撤市设区（原县级', 'শহর বিলুপ্ত করে জেলা প্রতিষ্ঠা (সাবেক কাউন্টি-স্তরের '),
        ('撤县设区（原', 'কাউন্টি বিলুপ্ত করে জেলা প্রতিষ্ঠা (সাবেক '),
        ('撤市设区（原', 'শহর বিলুপ্ত করে জেলা প্রতিষ্ঠা (সাবেক '),
        ('撤县设区', 'কাউন্টি বিলুপ্ত করে জেলা প্রতিষ্ঠা'),
        ('撤市设区', 'শহর বিলুপ্ত করে জেলা প্রতিষ্ঠা'),
        ('撤盟设市', 'লীগ বিলুপ্ত করে শহর প্রতিষ্ঠা'),
        ('撤地设市', 'প্রিফেকচার বিলুপ্ত করে শহর প্রতিষ্ঠা'),
        ('撤销', 'বিলুপ্ত করে '),
        ('撤', 'বিলুপ্ত করে '),
        ('合并设立', 'একীভূত করে প্রতিষ্ঠা করা হয় '),
        ('并入', '-র সাথে একীভূত করা হয়'),
        ('分别更名为', 'যথাক্রমে নাম পরিবর্তন করে '),
        ('更名为', '-র নাম পরিবর্তন করে '),
        ('更名', 'নাম পরিবর্তন করা হয়'),
        ('改嵩山', 'নাম পরিবর্তন করে সুংশান'),
        ('改卢湾', 'নাম পরিবর্তন করে লুওয়ান'),
        ('改徐汇', 'নাম পরিবর্তন করে শ্যুহুই'),
        ('改新市', 'নাম পরিবর্তন করে শিনশি'),
        ('10月置', 'অক্টোবরে প্রতিষ্ঠিত'),
        ('月置', ' মাসে প্রতিষ্ঠিত'),
        ('改为回民区', 'নাম পরিবর্তন করে হুইমিন জেলা'),
        ('改为', 'নাম পরিবর্তন করে '),
        ('改设为', 'রূপান্তর করে '),
        ('改设', 'রূপান্তর করে '),
        ('改置', 'রূপান্তর করে প্রতিষ্ঠা করা হয়'),
        ('析置', 'থেকে পৃথক করে প্রতিষ্ঠা করা হয়'),
        ('分别设立', 'যথাক্রমে প্রতিষ্ঠা করা হয় '),
        ('设立', 'প্রতিষ্ঠা করা হয়'),
        ('设置', 'প্রতিষ্ঠা করা হয়'),
        ('恢复', 'পুনর্বহাল করা হয়'),
        ('分别', 'যথাক্রমে '),
        ('同年', 'একই বছর '),
        ('由', ''),
        ('管辖', 'নিয়ন্ত্রণাধীন'),
        ('划归', '-র অধীনে হস্তান্তর করা হয়'),
        ('原县级', 'সাবেক কাউন্টি-স্তরের '),
        ('原', 'সাবেক '),
        ('县级', 'কাউন্টি-স্তরের '),
        ('地级', 'প্রিফেকচার-স্তরের '),
        ('郊区', 'শহরতলি জেলা'),
        ('城区', 'শহরাঞ্চল জেলা'),
        ('矿区', 'খনি জেলা'),
        ('个区', 'টি জেলা'),
        ('个县', 'টি কাউন্টি'),
        ('第一至十六区', '১ম থেকে ১৬শ জেলা'),
        ('第一至十五区', '১ম থেকে ১৫শ জেলা'),
        ('第一至十二区', '১ম থেকে ১২শ জেলা'),
        ('第一至十一区', '১ম থেকে ১১শ জেলা'),
        ('第一至十区', '১ম থেকে ১০ম জেলা'),
        ('第一至九区', '১ম থেকে ৯ম জেলা'),
        ('第一至八区', '১ম থেকে ৮ম জেলা'),
        ('第一至第八区', '১ম থেকে ৮ম জেলা'),
        ('第一至七区', '১ম থেকে ৭ম জেলা'),
        ('第一至六区', '১ম থেকে ৬ষ্ঠ জেলা'),
        ('第一至五区', '১ম থেকে ৫ম জেলা'),
        ('第一至四区', '১ম থেকে ৪র্থ জেলা'),
        ('第一至三区', '১ম থেকে ৩য় জেলা'),
        ('第二至六区', '২য় থেকে ৬ষ্ঠ জেলা'),
        ('1至8区', '১ম থেকে ৮ম জেলা'),
        ('第一区', '১ম জেলা'),
        ('第二区', '২য় জেলা'),
        ('第三区', '৩য় জেলা'),
        ('第四区', '৪র্থ জেলা'),
        ('第五区', '৫ম জেলা'),
        ('第六区', '৬ষ্ঠ জেলা'),
        ('第七区', '৭ম জেলা'),
        ('第八区', '৮ম জেলা'),
        ('第九区', '৯ম জেলা'),
        ('第十区', '১০ম জেলা'),
        ('第十一区', '১১শ জেলা'),
        ('第十二区', '১২শ জেলা'),
        ('第十三区', '১৩শ জেলা'),
        ('第十四区', '১৪শ জেলা'),
        ('第十五区', '১৫শ জেলা'),
        ('第十六区', '১৬শ জেলা'),
        ('第1区', '১ম জেলা'),
        ('第2区', '২য় জেলা'),
        ('第3区', '৩য় জেলা'),
        ('第4区', '৪র্থ জেলা'),
        ('第5区', '৫ম জেলা'),
        ('第6区', '৬ষ্ঠ জেলা'),
        ('第7区', '৭ম জেলা'),
        ('第8区', '৮ম জেলা'),
        ('第9区', '৯ম জেলা'),
        ('第10区', '১০ম জেলা'),
        ('，', ', '),
        ('；', '; '),
        ('、', ', '),
        ('（', ' ('),
        ('）', ')'),
    ]

    for zh_p, bn_p in PHRASE_REPLACEMENTS:
        text = text.replace(zh_p, bn_p)

    # ৬. অবশিষ্ট নামসমূহ প্রতিবর্ণীকরণ
    text = transliterate_remaining_hanzi(text)

    # Clean double spaces or punctuation
    text = re.sub(r'\s+', ' ', text)
    text = text.replace(' ,', ',').replace(' ;', ';').replace(', ;', ';').replace(', ,', ',').replace('; ;', ';').strip()

    # ৭. সংখ্যা বাংলায় রূপান্তর
    text = to_bengali_digits(text)

    return text if text else '&nbsp;'

print('Refined translation components loaded.')
