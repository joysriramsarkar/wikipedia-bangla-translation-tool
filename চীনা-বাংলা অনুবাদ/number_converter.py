# -*- coding: utf-8 -*-
"""
সংখ্যা ও সারণি টীকা রূপান্তরকারী (Number and Table Notes Converter)
উইকি টেবিলের এইচটিএমএল/সিএসএস কাঠামো অপরিবর্তিত রেখে সংখ্যা ও মন্তব্য বাংলায় রূপান্তর করে।
"""
import re

BENGALI_DIGITS = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
BN_TO_ASCII = str.maketrans('০১২৩৪৫৬৭৮৯', '0123456789')

def restore_ascii_in_attributes(text: str) -> str:
    """
    এইচটিএমএল ও উইকিটেক্সটের গঠনমূলক উপাদানগুলোর (rowspan, colspan, px, width %, URLs, template params)
    বাংলা সংখ্যাকে মিডিয়াউইকি প্রমিত অ্যাসকি সংখ্যায় (0-9) ফিরিয়ে আনে যাতে ছক বা ছবি না ভাঙে।
    """
    def to_ascii(m):
        return m.group(0).translate(BN_TO_ASCII)

    # ১. rowspan এবং colspan
    text = re.sub(r'rowspan\s*=\s*["\']?[০-৯0-9]+["\']?', to_ascii, text)
    text = re.sub(r'colspan\s*=\s*["\']?[০-৯0-9]+["\']?', to_ascii, text)

    # ২. ছবির সাইজ: ২৫৫px -> 255px
    text = re.sub(r'[০-৯0-9]+px', to_ascii, text)

    # ৩. সিএসএস এবং উইকিপ্রস্থ: width: ১২% -> width:12%
    text = re.sub(r'width:\s*[০-৯0-9]+%', to_ascii, text)
    text = re.sub(r'width\s*=\s*["\']?[০-৯0-9]+%?["\']?', to_ascii, text)
    text = re.sub(r'font-size:\s*[০-৯0-9]+%', to_ascii, text)

    # ৪. টেমপ্লেট প্যারামিটারের সংখ্যা: alt_name১ -> alt_name1, author১ -> author1
    text = re.sub(r'(?:alt_name|author)[০-৯0-9]+', to_ascii, text)

    # ৫. ইউআরএল এবং আর্কাইভ লিংক
    def url_clean(m):
        return m.group(0).translate(BN_TO_ASCII)
    text = re.sub(r'(?:url|archive-url)\s*=\s*[^\s\|\}]+', url_clean, text)

    return text

def to_bengali_digits(text: str) -> str:
    """
    যেকোনো টেক্সটের আরবি সংখ্যাকে (0-9) বাংলা সংখ্যায় (০-৯) রূপান্তর করে।
    এইচটিএমএল/মিডিয়াউইকি অ্যাট্রিবিউট (rowspan, colspan, style, hex color ইত্যাদি) অক্ষুণ্ণ রাখে।
    """
    placeholders = []
    
    def repl_save(match):
        idx = len(placeholders)
        tag = f"__NUMTOK_{idx}__"
        placeholders.append((tag, match.group(0)))
        return tag

    s = text
    # সুরক্ষিত রাখার প্যাটার্নসমূহ (HTML, CSS, MediaWiki syntax):
    s = re.sub(r'rowspan\s*=\s*["\']?[0-9]+["\']?', repl_save, s)
    s = re.sub(r'colspan\s*=\s*["\']?[0-9]+["\']?', repl_save, s)
    s = re.sub(r'font-size:\s*[0-9]+%', repl_save, s)
    s = re.sub(r'width:\s*[0-9]+%', repl_save, s)
    s = re.sub(r'width\s*=\s*["\']?[0-9]+%?["\']?', repl_save, s)
    s = re.sub(r'\|[0-9]+px', repl_save, s)
    s = re.sub(r'[0-9]+px', repl_save, s)
    s = re.sub(r'(?:alt_name|author)[0-9]+', repl_save, s)
    s = re.sub(r'#[0-9a-fA-F]{3,8}', repl_save, s)
    s = re.sub(r'(?:url|archive-url)\s*=\s*[^\s\|\}]+', repl_save, s)
    s = re.sub(r'<span style="display:none">0</span>', repl_save, s)
    s = re.sub(r'\[\[2010 Chinese census\|', repl_save, s)
    s = re.sub(r'\[\[Sixth National Population Census of the People\'s Republic of China\|', repl_save, s)
    
    # বাকি সংখ্যাগুলোকে বাংলায় রূপান্তর
    s = s.translate(BENGALI_DIGITS)
    
    # সংরক্ষিত টোকেনগুলো ফিরিয়ে দেওয়া
    for tag, orig in placeholders:
        tag_translated = tag.translate(BENGALI_DIGITS)
        s = s.replace(tag_translated, orig)

    # পরিশেষে কোনো অ্যাট্রিবিউটে ভুলবশত বাংলা সংখ্যা ঢুকে থাকলে তা উদ্ধার করা
    s = restore_ascii_in_attributes(s)
        
    return s

TABLE_NOTES_REPLACEMENTS = [
    # সাধারণ উইকি মন্তব্য ও টীকা
    (r"\{\{small\|''Direct administration''\}\}", "{{small|''সরাসরি শাসিত''}}"),
    (r"\{\{small\|''Directly administered''\}\}", "{{small|''সরাসরি শাসিত''}}"),
    (r"\{\{small\|''not established''\}\}", "{{small|''প্রতিষ্ঠিত হয়নি''}}"),
    (r"\{\{small\|\(''claimed''\)\}\}", "{{small|(''দাবিকৃত'')}}"),
    (r"\{\{small\|\(''Various''\)\}\}", "{{small|(''বিভিন্ন'')}}"),

    # বিলুপ্ত কাউন্টি সংশ্লিষ্ট বিশেষ টীকা
    (r"<span style=\"display:none\">0</span>\{\{small\|অন্তর্ভুক্ত Xicheng''\}\}", "<span style=\"display:none\">0</span>{{small|''শিছেং জেলায় একীভূত''}}"),
    (r"<span style=\"display:none\">0</span>\{\{small\|অন্তর্ভুক্ত Dongcheng''\}\}", "<span style=\"display:none\">0</span>{{small|''তুংছেং জেলায় একীভূত''}}"),
    (r"<span style=\"display:none\">0</span>\{\{small\|বিভক্ত Shapingba ও Yuzhong''\}\}", "<span style=\"display:none\">0</span>{{small|''শাথিংপা ও ইউচুং জেলায় বিভক্ত''}}"),
    (r"\(county level\)", "(কাউন্টি স্তর)"),
    (r"\(entity becomes a prefecture level division\)", "(সংস্থাটি প্রিফেকচার স্তরের বিভাগে পরিণত হয়)"),
    (r"\[\[CPRC\|Administrative office\]\]", "[[CPRC|প্রশাসনিক দপ্তর]]"),
    (r"\(part\)", "(অংশ)"),

    # জাতিগোষ্ঠীর বন্ধনী টীকা
    (r"\(Bai & Pumi\)", "(বাই ও পুমি)"),
    (r"\(Bonan, Dongxiang & Salar\)", "(পোনান, তুংশিয়াং ও সালার)"),
    (r"\(Buyei & Miao\)", "(বুয়েই ও মিয়াও)"),
    (r"\(Dai & Va\)", "(দাই ও ভা)"),
    (r"\(Dai & Yi\)", "(দাই ও ই)"),
    (r"\(Dai, Lahu, & Va\)", "(দাই, লাহু ও ভা)"),
    (r"\(Derung & Nu\)", "(তেরুং ও নু)"),
    (r"\(Dongxiang\)", "(তুংশিয়াং)"),
    (r"\(Dong\)", "(তুং)"),
    (r"\(Gelao & Maio\)", "(কেলাও ও মিয়াও)"),
    (r"\(Gelao & Miao\)", "(কেলাও ও মিয়াও)"),
    (r"\(Hani, Yi, & Dai\)", "(হানি, ই ও দাই)"),
    (r"\(Hani & Yi\)", "(হানি ও ই)"),
    (r"\(Hani\)", "(হানি)"),
    (r"\(Hui & Tu\)", "(হুই ও থু)"),
    (r"\(Hui & Yi\)", "(হুই ও ই)"),
    (r"\(Hui\)", "(হুই)"),
    (r"\(Kazakh\)", "(কাজাখ)"),
    (r"\(Korean\)", "(কোরীয়)"),
    (r"\(Lahu, Va, Blang, & Dai\)", "(লাহু, ভা, বুলাং ও দাই)"),
    (r"\(Lahu\)", "(লাহু)"),
    (r"\(Li & Miao\)", "(লি ও মিয়াও)"),
    (r"\(Li\)", "(লি)"),
    (r"\(Lisu\)", "(লিসু)"),
    (r"\(Manchu & Mongol\)", "(মাঞ্চু ও মঙ্গোল)"),
    (r"\(Manchu\)", "(মাঞ্চু)"),
    (r"\(Maonan\)", "(মাওনান)"),
    (r"\(Miao & Buyei\)", "(মিয়াও ও বুয়েই)"),
    (r"\(Miao & Dong\)", "(মিয়াও ও তুং)"),
    (r"\(Miao & Tujia\)", "(মিয়াও ও থুচিয়া)"),
    (r"\(Miao, Yao, & Dai\)", "(মিয়াও, ইয়াও ও দাই)"),
    (r"\(Miao\)", "(মিয়াও)"),
    (r"\(Mongol\)", "(মঙ্গোল)"),
    (r"\(Mulao\)", "(মুলাও)"),
    (r"\(Naxi\)", "(নাশি)"),
    (r"\(Qiang\)", "(ছিয়াং)"),
    (r"\(Salar\)", "(সালার)"),
    (r"\(She\)", "(শে)"),
    (r"\(Shui\)", "(শুই)"),
    (r"\(Tajik\)", "(তাজিক)"),
    (r"\(Tibetan\)", "(তিব্বতি)"),
    (r"\(Tu\)", "(থু)"),
    (r"\(Tujia & Miao\)", "(থুচিয়া ও মিয়াও)"),
    (r"\(Tujia\)", "(থুচিয়া)"),
    (r"\(Va\)", "(ভা)"),
    (r"\(Xibe\)", "(শিবে)"),
    (r"\(Yao\)", "(ইয়াও)"),
    (r"\(Yi, Hani, & Lahu\)", "(ই, হানি ও লাহু)"),
    (r"\(Yi, Hui, & Miao\)", "(ই, হুই ও মিয়াও)"),
    (r"\(Yi & Dai\)", "(ই ও দাই)"),
    (r"\(Yi & Hui\)", "(ই ও হুই)"),
    (r"\(Yi & Miao\)", "(ই ও মিয়াও)"),
    (r"\(Yi\)", "(ই)"),
    (r"\(Yugur\)", "(ইউগুর)"),
    (r"\(Zhuang & Yao\)", "(চুয়াং ও ইয়াও)"),
]

def translate_table_notes(text: str) -> str:
    """সারণির অবশিষ্ট ইংরেজি মন্তব্য ও জাতিগোষ্ঠীর নাম বাংলায় রূপান্তর করে।"""
    s = text
    for pat, rep in TABLE_NOTES_REPLACEMENTS:
        s = re.sub(pat, rep, s)
    return s
