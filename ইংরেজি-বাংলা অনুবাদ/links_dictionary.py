# -*- coding: utf-8 -*-
"""
ইংরেজি-বাংলা লিংক ও শব্দ অভিধান
===================================
পরিচিত ইংরেজি শব্দ ও নাম থেকে বাংলা উইকিলিংক অভিধান।
চলচ্চিত্র, আত্মজীবনী, সাহিত্য সংক্রান্ত বাংলা অনুবাদ।
"""

# পরিচিত ইংরেজি → বাংলা নাম অভিধান
PERSON_NAMES_MAP = {
    # বিশ্ব নেতা
    "Abraham Lincoln": "আব্রাহাম লিংকন",
    "Franklin D. Roosevelt": "ফ্র্যাংকলিন ডি. রুজভেল্ট",
    "Winston Churchill": "উইনস্টন চার্চিল",
    "Mahatma Gandhi": "মহাত্মা গান্ধী",
    "Nelson Mandela": "নেলসন মান্দেলা",
    "Barack Obama": "বারাক ওবামা",
    "Vladimir Putin": "ভ্লাদিমির পুতিন",

    # লেখক/সাহিত্যিক
    "William Shakespeare": "উইলিয়াম শেক্সপিয়ার",
    "Charles Dickens": "চার্লস ডিকেন্স",
    "Leo Tolstoy": "লেভ তলস্তয়",
    "Mark Twain": "মার্ক টোয়েন",
    "Ernest Hemingway": "আর্নেস্ট হেমিংওয়ে",
    "Franz Kafka": "ফ্রানৎস কাফকা",
    "Gabriel García Márquez": "গাব্রিয়েল গার্সিয়া মার্কেস",

    # বিজ্ঞানী
    "Albert Einstein": "আলবার্ট আইনস্টাইন",
    "Isaac Newton": "আইজ্যাক নিউটন",
    "Marie Curie": "মারি কুরি",
    "Charles Darwin": "চার্লস ডারউইন",
    "Stephen Hawking": "স্টিফেন হকিং",
}

# চলচ্চিত্র শিরোনাম অনুবাদ (ইংরেজি → বাংলা)
FILM_TITLES_MAP = {
    "The Godfather": "দ্য গডফাদার",
    "Schindler's List": "শিন্ডলারের তালিকা",
    "Casablanca": "কাসাব্লাংকা",
    "The Dark Knight": "দ্য ডার্ক নাইট",
    "Forrest Gump": "ফরেস্ট গাম্প",
    "Titanic": "টাইটানিক",
    "Inception": "ইনসেপশন",
    "The Matrix": "দ্য ম্যাট্রিক্স",
    "Parasite": "পরজীবী",
    "Spirited Away": "স্পিরিটেড অ্যাওয়ে",
}

# বই শিরোনাম অনুবাদ
BOOK_TITLES_MAP = {
    "The Diary of a Young Girl": "একটি তরুণ মেয়ের ডায়েরি",
    "To Kill a Mockingbird": "একটি মকিংবার্ড মারতে",
    "1984": "১৯৮৪",
    "Animal Farm": "এনিমাল ফার্ম",
    "The Great Gatsby": "দ্য গ্রেট গ্যাটসবি",
    "Don Quixote": "দন কিহোতে",
    "One Hundred Years of Solitude": "নিঃসঙ্গতার একশ বছর",
}

# সাধারণ ইংরেজি শব্দ → বাংলা অনুবাদ
COMMON_WORDS_MAP = {
    "autobiography": "আত্মজীবনী",
    "biography": "জীবনী",
    "memoirs": "স্মৃতিকথা",
    "novel": "উপন্যাস",
    "poetry": "কবিতা",
    "memoir": "স্মৃতিকথা",
    "diary": "ডায়েরি",
    "letters": "চিঠিপত্র",
    "essays": "প্রবন্ধ",
}

# ভাষার নাম → বাংলা
LANGUAGE_NAMES_MAP = {
    "English": "ইংরেজি",
    "French": "ফরাসি",
    "German": "জার্মান",
    "Spanish": "স্পেনীয়",
    "Italian": "ইতালীয়",
    "Portuguese": "পর্তুগিজ",
    "Russian": "রুশ",
    "Chinese": "চীনা",
    "Japanese": "জাপানি",
    "Arabic": "আরবি",
    "Hindi": "হিন্দি",
    "Bengali": "বাংলা",
    "Dutch": "ডাচ",
    "Swedish": "সুয়েডীয়",
    "Norwegian": "নরওয়েজীয়",
    "Danish": "ডেনিশ",
    "Finnish": "ফিনিশ",
    "Polish": "পোলিশ",
    "Czech": "চেক",
    "Hungarian": "হাঙ্গেরীয়",
    "Turkish": "তুর্কি",
    "Greek": "গ্রিক",
    "Hebrew": "হিব্রু",
    "Korean": "কোরীয়",
}


def lookup_person(name: str) -> str:
    """ব্যক্তির নাম বাংলায় অনুবাদ করে।"""
    return PERSON_NAMES_MAP.get(name, name)


def lookup_film(title: str) -> str:
    """চলচ্চিত্রের শিরোনাম বাংলায় অনুবাদ করে।"""
    return FILM_TITLES_MAP.get(title, title)


def lookup_book(title: str) -> str:
    """বইয়ের শিরোনাম বাংলায় অনুবাদ করে।"""
    return BOOK_TITLES_MAP.get(title, title)


def lookup_language(lang: str) -> str:
    """ভাষার নাম বাংলায় অনুবাদ করে।"""
    return LANGUAGE_NAMES_MAP.get(lang, lang)
