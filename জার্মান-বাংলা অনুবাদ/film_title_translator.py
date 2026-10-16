# -*- coding: utf-8 -*-
"""
চলচ্চিত্র শিরোনাম রূপান্তরক ও মূল জার্মান নাম সংগ্রাহক
(Film Title Translator & German Title Extractor)
-------------------------------------------------
চলচ্চিত্রের শিরোনাম শতভাগ প্রমিত বাংলায় লিপ্যন্তর করে এবং উইকি লিঙ্ক বাংলায় রূপান্তর করে।
পাশে বন্ধনীতে মূল ভাষার/জার্মান শিরোনাম যুক্ত করে।
ফরম্যাট: ''[[লিংক|বাংলা শিরোনাম]]'' (''মূল শিরোনাম'')
বাধ্যতামূলক:
১. সমস্ত উইকিলিংক বাধ্যতামূলকভাবে বাংলায় হবে (কোনো ইংরেজি পাতা লিংক থাকবে না)।
২. শিরোনাম কলামে কোনো {{ill}} বা [de] থাকবে না (কারণ মূল নাম পাশে বন্ধনীতেই রয়েছে)।
৩. ইংরেজি ও জার্মান উভয় ভাষার জন্য সঠিক ধ্বনিতাত্ত্বিক লিপ্যন্তর নিশ্চিত করা।
৪. কোনো HTML entity (&nbsp;) বা অপ্রয়োজনীয় কোটেশন উইকিলিংকের ভেতর থাকবে না।
"""

import re

try:
    from .german_transliteration import transliterate_token, FIRST_NAMES
except (ImportError, ValueError):
    from german_transliteration import transliterate_token, FIRST_NAMES

BENGALI_DIGITS = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')

# ব্যক্তি, স্থান ও বিশেষ জার্মান নাম যা ইংরেজি বা জার্মান উভয় শিরোনামেই আসতে পারে
SHARED_ENTITIES = {
    "annelie": "আনেলি",
    "jakob": "ইয়াকব",
    "jacob": "ইয়াকব",
    "von": "ফন",
    "vom": "ফম",
    "metzler": "মেৎসলার",
    "leipzig": "লাইপৎসিশ",
    "thomas": "টমাস",
    "stankowski": "স্টানকোভস্কি",
    "stankowski's": "স্টানকোভস্কিস",
    "stankowskis": "স্টানকোভস্কিস",
    "hitler": "হিটলার",
    "berlin": "বার্লিন",
    "münchen": "মিউনিখ",
    "munich": "মিউনিখ",
    "hamburg": "হামবুর্গ",
    "deutschland": "ডয়চল্যান্ড",
    "germany": "জার্মানি",
    "wagner": "ভাগনার",
    "schoenberg": "শ্যোনবার্গ",
    "schubert": "শুবের্ট",
    "mozart": "মোজার্ট",
    "beethoven": "বেটোফেন",
    "bach": "বাখ",
    "goethe": "গ্যোটে",
    "schiller": "শিলার",
    "albert": "আলবার্ট",
    "alina": "আলিনা",
    "arthur": "আর্থার",
    "claire": "ক্লেয়ার",
    "carl": "কার্ল",
    "bertha": "বার্থা",
    "otto": "অটো",
    "karl": "কার্ল",
    "paul": "পাউল",
    "peter": "পেটার",
    "stefan": "স্টেফান",
    "stephan": "স্টেফান",
    "robert": "রবার্ট",
    "richard": "রিচার্ড",
    "walter": "ভাল্টার",
    "wolfgang": "ভলফগাং",
    "christian": "ক্রিশ্চিয়ান",
    "sasha": "সাশা",
    "sascha": "সাশা",
    "ayla": "আয়লা",
    "aghet": "আঘেত",
    "albaner": "আলবানার",
    "albanian": "আলবেনিয়ান",
    "shahada": "শাহাদাহ",
}

EN_WORDS = {
    # ব্যাকরণিক শব্দ ও অব্যয়
    "the": "দ্য", "a": "আ", "an": "অ্যান", "of": "অব", "in": "ইন", "on": "অন",
    "at": "অ্যাট", "to": "টু", "for": "ফর", "from": "ফ্রম", "by": "বাই",
    "with": "উইথ", "without": "উইদাউট", "and": "অ্যান্ড", "or": "অর",
    "not": "নট", "no": "নো", "is": "ইজ", "are": "আর", "was": "ওয়াজ",
    "were": "ওয়্যার", "be": "বি", "been": "বিন", "being": "বিয়িং",
    "it": "ইট", "its": "ইটস", "it's": "ইটস", "this": "দিস", "that": "দ্যাট",
    "these": "দিজ", "those": "দোজ", "my": "মাই", "your": "ইউর", "his": "হিজ",
    "her": "হার", "our": "আওয়ার", "their": "দেয়ার", "me": "মি", "you": "ইউ",
    "him": "হিম", "he": "হি", "she": "শি", "us": "আস", "them": "দেম", "we": "উই", "they": "দে", "i": "আই",
    "all": "অল", "any": "এনি", "both": "বোথ", "each": "ইচ", "few": "ফিউ",
    "more": "মোর", "most": "মোস্ট", "other": "আদার", "some": "সাম", "such": "সাচ",
    "only": "অনলি", "own": "ওন", "same": "সেম", "so": "সো", "than": "দ্যান",
    "too": "টু", "very": "ভেরি", "just": "জাস্ট", "about": "অ্যাবাউট",
    "into": "ইনটু", "through": "থ্রু", "after": "আফটার", "over": "ওভার",
    "between": "বিটুইন", "out": "আউট", "against": "অ্যাগেইনস্ট", "during": "ডিউরিং",
    "before": "বিফোর", "under": "আন্ডার", "around": "অ্যারাউন্ড", "among": "অ্যামং",
    "have": "হ্যাভ", "has": "হ্যাজ", "had": "হ্যাড", "do": "ডু", "does": "ডাজ",
    "did": "ডিড", "will": "উইল", "would": "উড", "shall": "শ্যাল", "should": "শুড",
    "may": "মে", "might": "মাইট", "must": "মাস্ট", "can": "ক্যান", "could": "কুড",
    "don't": "ডোন্ট", "dont": "ডোন্ট", "can't": "কান্ট", "cant": "কান্ট",
    "won't": "ওন্ট", "wont": "ওন্ট", "isn't": "ইজন্ট", "isnt": "ইজন্ট",
    "what": "হোয়াট", "which": "হুইচ", "who": "হু", "whom": "হুম", "whose": "হুজ",
    "when": "হোয়েন", "where": "হোয়ার", "why": "হোয়াই", "how": "হাউ",
    "last": "লাস্ট", "first": "ফার্স্ট", "second": "সেকেন্ড", "third": "থার্ড",
    "new": "নিউ", "old": "ওল্ড", "good": "গুড", "bad": "ব্যাড", "big": "বিগ",
    "little": "লিটল", "small": "স্মল", "great": "গ্রেট", "one": "ওয়ান",
    "two": "টু", "three": "থ্রি", "four": "ফোর", "five": "ফাইভ", "six": "সিক্স",
    "seven": "সেভেন", "eight": "এইট", "nine": "নাইন", "ten": "টেন",
    "never": "নেভার", "ever": "এভার",

    # পদবি ও উপাধি
    "st": "সেন্ট", "st.": "সেন্ট", "saint": "সেন্ট",
    "dr": "ড.", "dr.": "ড.", "mr": "মিস্টার", "mr.": "মিস্টার",
    "mrs": "মিসেস", "mrs.": "মিসেস", "ms": "মিস", "ms.": "মিস",
    "lord": "লর্ড", "sir": "স্যার", "lady": "লেডি", "king": "কিং", "queen": "কুইন",
    "prince": "প্রিন্স", "princess": "প্রিন্সেস",

    # সাধারণ বিশেষ্য ও বিশেষণ
    "man": "ম্যান", "men": "মেন", "woman": "ওম্যান", "women": "উইমেন",
    "girl": "গার্ল", "girls": "গার্লস", "boy": "বয়", "boys": "বয়েজ",
    "child": "চাইল্ড", "children": "চিলড্রেন", "family": "ফ্যামিলি",
    "friend": "ফ্রেন্ড", "friends": "ফ্রেন্ডস", "friendship": "ফ্রেন্ডশিপ",
    "father": "ফাদার", "mother": "মাদার", "brother": "ব্রাদার", "brothers": "ব্রাদার্স",
    "sister": "সিস্টার", "sisters": "সিস্টার্স", "son": "সান", "daughter": "ডটার",
    "wife": "ওয়াইফ", "husband": "হাজব্যান্ড", "parent": "প্যারেন্ট", "parents": "প্যারেন্টস",
    "house": "হাউস", "home": "হোম", "room": "রুম", "door": "ডোর", "wall": "ওয়াল",
    "city": "সিটি", "town": "টাউন", "street": "স্ট্রিট", "road": "রোড", "way": "ওয়ে",
    "world": "ওয়ার্ল্ড", "earth": "আর্থ", "sun": "সান", "moon": "মুন",
    "star": "স্টার", "stars": "স্টার্স", "sky": "স্কাই", "sea": "সি", "ocean": "ওশান",
    "river": "রিভার", "water": "ওয়াটার", "waters": "ওয়াটার্স", "fire": "ফায়ার",
    "wind": "উইন্ড", "blood": "ব্লাড", "heart": "হার্ট", "hearts": "হার্টস",
    "dark": "ডার্ক", "darkness": "ডার্কনেস", "light": "লাইট", "lights": "লাইটস",
    "white": "হোয়াইট", "black": "ব্ল্যাক", "red": "রেড", "blue": "ব্লু",
    "green": "গ্রিন", "gold": "গোল্ড", "golden": "গোল্ডেন", "silver": "সিলভার",
    "pink": "পিংক", "orange": "অরেঞ্জ", "color": "কালার", "colors": "কালারস",
    "summer": "সামার", "summers": "সামারস", "winter": "উইন্টার", "spring": "স্প্রিং",
    "autumn": "অটাম", "fall": "ফল",
    "day": "ডে", "days": "ডেজ", "night": "নাইট", "nights": "নাইটস",
    "time": "টাইম", "times": "টাইমস", "year": "ইয়ার", "years": "ইয়ার্স",
    "life": "লাইফ", "lives": "লাইভস", "death": "ডেথ", "dead": "ডেড",
    "love": "লাভ", "secret": "সিক্রেট", "secrets": "সিক্রেটস",
    "silent": "সাইলেন্ট", "silence": "সাইলেন্স", "dream": "ড্রিম", "dreams": "ড্রিমস",
    "story": "স্টোরি", "stories": "স্টোরিজ", "tale": "টেল", "tales": "টেলস",
    "song": "সং", "songs": "সংস", "game": "গেম", "games": "গেমস",
    "choir": "কয়ার",
    "joy": "জয়", "father": "ফাদার", "fatherhood": "ফাদারহুড",
    "mother": "মাদার", "motherhood": "মাদারহুড",
    "brother": "ব্রাদার", "brotherhood": "ব্রাদারহুড", "sister": "সিস্টার",

    # সিনেমা ও ক্রিয়া সংক্রান্ত
    "fly": "ফ্লাই", "flying": "ফ্লাইং", "away": "অ্যাওয়ে",
    "run": "রান", "running": "রানিং", "runner": "রানার", "runaway": "রানঅ্যাওয়ে",
    "walk": "ওয়াক", "walking": "ওয়াকিং", "go": "গো", "goes": "গোজ", "going": "গোয়িং", "gone": "গন",
    "come": "কাম", "coming": "কামিং", "look": "লুক", "looking": "লুকিং",
    "wait": "ওয়েট", "waiting": "ওয়েটিং", "kill": "কিল", "killing": "কিলিং", "killer": "কিলার",
    "murder": "মার্ডার", "crime": "ক্রাইম", "police": "পুলিশ",
    "lost": "লস্ট", "found": "ফাউন্ড", "blind": "ব্লাইন্ড", "spot": "স্পট",
    "hunt": "হান্ট", "hunter": "হান্টার", "hunters": "হান্টার্স",
    "truth": "ট্রুথ", "true": "ট্রু", "lie": "লাই", "lies": "লাইজ",
    "soul": "সোল", "abyss": "অ্যাবিস", "freedom": "ফ্রিডম", "free": "ফ্রি",
    "island": "আইল্যান্ড", "journey": "জার্নি", "past": "পাস্ট", "future": "ফিউচার",
    "strange": "স্ট্রেঞ্জ", "case": "কেস", "plan": "প্ল্যান", "back": "ব্যাক", "kiss": "কিস",
    "enemy": "এনিমি", "education": "এডুকেশন", "beginning": "বিগিনিং", "end": "এন্ড",
    "cat": "ক্যাট", "hope": "হোপ", "lucky": "লাকি", "cold": "কোল্ড", "ice": "আইস",
    "invisible": "ইনভিজিবল", "hidden": "হিডেন", "rough": "রাফ", "valley": "ভ্যালি",
    "ahead": "অ্যাহেড", "trail": "ট্রেইল", "trails": "ট্রেইলস", "ball": "বল", "balls": "বলস",
    "head": "হেড", "conspiracy": "কনস্পিরেসি", "alert": "অ্যালার্ট",
    "stopped": "স্টপড", "stop": "স্টপ", "track": "ট্র্যাক", "tracks": "ট্র্যাকস",
    "point": "পয়েন্ট", "blank": "ব্ল্যাঙ্ক", "age": "এজ",
    "cannibal": "ক্যানিবাল", "cannibals": "ক্যানিবালস",
    "bank": "ব্যাংক", "banklady": "ব্যাংকলেডি",
    "half": "হাফ", "country": "কান্ট্রি", "countries": "কান্ট্রিজ",
    "space": "স্পেস", "race": "রেস", "place": "প্লেস", "face": "ফেস",
    "break": "ব্রেক",
    "chapter": "চ্যাপ্টার", "battle": "ব্যাটল", "sneaker": "স্নিকার", "salt": "সল্ট",
    "schrotten": "শ্রোটেন", "seduced": "সিডিয়ুসড", "arms": "আর্মস", "another": "অ্যানাদার",
    "cut": "কাট", "off": "অফ", "get": "গেট", "downstairs": "ডাউনস্টেয়ার্স",
    "ordinary": "অর্ডিনারি", "millions": "মিলিয়নস", "million": "মিলিয়ন",
    "shores": "শোরস", "weekend": "উইকেন্ড", "shark": "শার্ক", "alarm": "অ্যালার্ম", "lake": "লেক",
    "dancing": "ড্যান্সিং", "talk": "টক", "party": "পার্টি", "celebration": "সেলিব্রেশন",
    "pig": "পিগ", "bliss": "ব্লিস", "original": "অরিজিনাল", "young": "ইয়াং",
    "triangle": "ট্রায়াঙ্গেল", "north": "নর্থ", "south": "সাউথ", "east": "ইস্ট", "west": "ওয়েস্ট",
    "promising": "প্রমিজিং", "therapy": "থেরাপি", "crashers": "ক্র্যাশার্স",
    "siberia": "সাইবেরিয়া", "amber": "অ্যাম্বার", "everything": "এভরিথিং", "stone": "স্টোন",
    "escape": "এসকেপ", "hotel": "হোটেল", "robber": "রবার", "route": "রুট",
    "rock": "রক", "resident": "রেসিডেন্ট", "evil": "ইভিল", "afterlife": "আফটারলাইফ",
    "grace": "গ্রেস", "restoring": "রেস্টোরিং", "whale": "হোয়েল", "whales": "হোয়েলস",
    "shared": "শেয়ার্ড", "happiness": "হ্যাপিনেস", "deserved": "ডিজার্ভড", "youth": "ইউথ",
    "sickness": "সিকনেস", "single": "সিঙ্গেল", "contract": "কন্ট্রাক্ট", "sinking": "সিঙ্কিং",
    "sleeper": "স্লিপার", "sleepers": "স্লিপার্স", "snowblind": "স্নোব্লাইন্ড",
    "combat": "কমব্যাট", "crack": "ক্র্যাক", "cracks": "ক্র্যাকস", "shell": "শেল",
    "miracle": "মিরাকল", "born": "বর্ন", "beat": "বিট", "beats": "বিটস",
    "follow": "ফলো", "minute": "মিনিট", "minutes": "মিনিটস", "polish": "পলিশ",
    "woods": "উডস", "wood": "উড", "hut": "হাট", "prime": "প্রাইম", "jungle": "জাঙ্গল",
    "chance": "চান্স", "amigo": "অ্যামিগো", "arrival": "অ্যারাইভাল", "revenge": "রিভেঞ্জ",
    "anatomy": "অ্যানাটমি", "animals": "অ্যানিম্যালস", "united": "ইউনাইটেড", "based": "বেসড",
    "forest": "ফরেস্ট", "blackout": "ব্ল্যাকআউট", "shock": "শক", "electric": "ইলেকট্রিক",
    "happy": "হ্যাপি", "blessed": "ব্লেসড", "events": "ইভেন্টস", "boundaries": "বাউন্ডারিজ",
    "movement": "মুভমেন্ট", "undercover": "আন্ডারকভার", "cave": "কেভ", "forgotten": "ফরগটেন",
    "whisperer": "হুইসপারার", "elephant": "এলিফ্যান্ট", "departure": "ডিপার্চার",
    "reunion": "রিইউনিয়ন", "innocent": "ইনোসেন্ট", "disappearance": "ডিসঅ্যাপিয়ারেন্স",
    "strangers": "স্ট্রেঞ্জার্স", "perfect": "পারফেক্ট", "rabbit": "র‍্যাবিট", "stole": "স্টোল",
    "different": "ডিফারেন্ট", "tell": "টেল", "ground": "গ্রাউন্ড", "relationship": "রিলেশনশিপ",
    "offline": "অফলাইন", "online": "অনলাইন", "hype": "হাইপ", "believe": "বিলিভ",
    "rockstar": "রকস্টার", "tame": "টেম", "keep": "কিপ", "immature": "ইম্যাচিউর",
    "missing": "মিসিং", "twilight": "টোয়াইলাইট", "answer": "অ্যানসার", "envy": "এনভি",
    "monkey": "মাঙ্কি", "philosopher": "ফিলোসফার", "relations": "রিলেশনস",
    "implosion": "ইমপ্লোশন", "scrivener": "স্ক্রিভনার", "hot": "হট", "line": "লাইন",
    "hotline": "হটলাইন", "homies": "হোমিজ", "homevideo": "হোমভিডিও",
    "pain": "পেইন", "pains": "পেইনস", "faith": "ফেইথ", "carinthia": "ক্যারিন্থিয়া",
    "strong": "স্ট্রং", "stronger": "স্ট্রংগার", "mercy": "মার্সি", "art": "আর্ট",
    "ghosthunters": "ঘোস্টহান্টার্স", "icy": "আইসি", "gotta": "গটা", "loop": "লুপ",
    "looping": "লুপিং", "brand": "ব্র্যান্ড", "courageous": "কারেজাস", "solidary": "সলিডারি",
    "burnout": "বার্নআউট", "snowman": "স্নোম্যান", "snowman's": "স্নোম্যানস", "mouse": "মাউস",
    "easter": "ইস্টার", "call": "কল", "istanbul": "ইস্তাম্বুল", "final": "ফাইনাল",
    "roulette": "রুলেট", "land": "ল্যান্ড", "lands": "ল্যান্ডস", "mom": "মম",
    "farewell": "ফেয়ারওয়েল", "frog": "ফ্রগ", "frogs": "ফ্রগস", "am": "এএম", "pm": "পিএম",
    "train": "ট্রেন",
}

DE_WORDS = {
    # জার্মান ব্যাকরণিক শব্দ ও অব্যয়
    "der": "ডের", "die": "ডি", "das": "ডাস", "ein": "আইন", "eine": "আইনে",
    "einer": "আইনার", "eines": "আইনেস", "einem": "আইনেম", "einen": "আইনেন",
    "und": "উন্ট", "in": "ইন", "im": "ইম", "von": "ফন", "vom": "ফম",
    "zu": "সু", "zur": "সুর", "zum": "জুম", "mit": "মিট", "auf": "আউফ",
    "aus": "আউস", "nach": "নাখ", "für": "ফুর", "über": "উবার", "unter": "উন্টার",
    "vor": "ফোর", "dem": "ডেম", "den": "ডেন", "des": "ডেস", "nicht": "নিখট",
    "wie": "ভি", "wir": "ভিয়ার", "ich": "ইখ", "du": "ডু", "er": "এর",
    "sie": "জি", "es": "এস", "man": "মান", "mann": "মান", "männer": "মেনার",
    "am": "আম", "an": "আন", "um": "উম", "bei": "বাই",
    "ist": "ইস্ট", "sind": "জিন্ড", "war": "ভার", "haben": "হাবেন", "hat": "হাট",
    "sein": "সাইন", "leben": "লেবেন", "tod": "টোড", "tot": "টোট",
    "liebe": "লিবে", "nacht": "নাখট", "tag": "টাগ", "tage": "টাগে",
    "zeit": "সাইট", "welt": "ভেল্ট", "stadt": "স্টাট", "haus": "হাউস",
    "frau": "ফাউ", "kind": "কিন্ড", "kinder": "কিন্ডার", "mädchen": "মেডশেন",
    "junge": "ইয়ুঙ্গে", "jungen": "ইয়ুঙ্গেন", "sommer": "জোমার",
    "winter": "ভিন্টার", "herbst": "হার্বস্ট", "frühling": "ফ্রুলিং",
    "glück": "গ্লুক", "himmel": "হিমেল", "erde": "এরডে", "sonne": "জোনে",
    "mond": "মন্ড", "sterne": "স্টার্নে", "meer": "মেয়ার", "wasser": "ভাসার",
    "feuer": "ফয়ার", "wind": "ভিন্ড", "herz": "হার্ৎস", "blut": "ব্লুট",
    "schatten": "শাটেন", "licht": "লিশট", "weiß": "ভাইস", "schwarz": "শোয়ার্ৎস",
    "rot": "রোট", "rotes": "রোটেস", "blau": "ব্লাউ", "grün": "গ্রুন", "gold": "গোল্ড",
    "aufstand": "আউফস্টান্ড", "völkermord": "ফলকারমর্ড", "auflehnung": "আউফলেনুং",
    "ausgerechnet": "আউসগেরেশনেট", "afrika": "আফ্রিকা", "spuren": "শপুরেন",
    "bösen": "বোসেন", "alter": "আল্টার", "lügen": "ল্যুগেন", "gelernt": "গেলার্নট",
    "mauer": "মাউয়ার", "menschen": "মেনশেন", "andere": "আনডারে", "weihnachten": "ভাইনাখটেন",
    "schnee": "শ্নে", "beziehung": "বেসিহুং", "deine": "ডাইনে", "gut": "গুট",
    "sag": "জাগ", "mir": "মিয়ার", "freiwillige": "ফ্রাইভিলিগে", "jahr": "ইয়ার",
    "vorname": "ফোরনামে", "schatz": "শাটৎস", "internat": "ইন্টারনাট",
    "schweigen": "শোয়াইগেন", "wunderkinder": "ভুন্ডারকিন্ডার", "liebesjahre": "লিবেসয়ারে",
    "erinnerung": "এরিনেরুং", "schurkenstück": "শুরকেনস্ট্যুক", "sechs": "সেক্স",
    "angst": "আংস্ট", "sennerin": "সেনেরিন", "verlieben": "ফেরলিবেন",
    "geteilte": "গিটাইল্টে", "verdient": "ফারডিন্ট", "dunkle": "ডুনকেল",
    "nest": "নেস্ট", "wunder": "ভুন্ডার", "kärnten": "কার্নটেন",
    "lied": "লিড", "ostern": "ওস্টার্ন", "polnische": "পোলনিশে",
    "satte": "জাটে", "farben": "ফারবেন", "unsichtbare": "উনসিশটবারে",
    "summe": "জুমে", "meiner": "মাইনার", "einzelnen": "আইনসেলনেন",
    "teile": "টাইলে", "habe": "হাবে", "dir": "ডিয়ার", "nie": "নি",
    "erzählt": "এরৎসেল্ট", "besten": "বেস্টেন", "jahren": "ইয়াবেন",
    "habt": "হাবট", "indisch": "ইন্ডিশ", "anfänger": "আনফেঙ্গার",
    "gemeinsam": "গেমাইনসাম", "anders": "আনডার্স", "insel": "ইনসেল",
    "namens": "নামেনস", "mitten": "মিটেন", "jagd": "ইয়াগড",
    "seelenfänger": "সেলেনফেঙ্গার", "vorbei": "ফোরবাই", "jetzt": "ইয়েৎসট",
    "dran": "ড্রান", "kriegerin": "ক্রিগেরিন", "räuber": "রয়বার",
    "räuberin": "রয়বারিন", "verhältnisse": "ফারহেল্টনিসে",
    "festtagsstimmung": "ফেসটটাগসস্টিমুং", "zimmer": "সিমার",
    "geheimnis": "গাহাইম্নিস", "wale": "ভালে",
    "bella": "বেলা", "vita": "ভিটা", "boxhagener": "বক্সহাগেনার",
    "platz": "প্লাৎস", "auch": "আউখ", "will": "ভিল",
    "manchen": "মানখেন", "hilft": "হিলফট", "nur": "নুর",
    "hopfensommer": "হপফেনজোমার", "heiß": "হাইস", "heiße": "হাইসে",
    "nummer": "নুমার", "ganz": "গানৎস", "stadtgeflüster": "স্টাটগেফ্লুস্টার",
    "sex": "সেক্স", "fünf": "ফুনফ", "lux": "লাক্স", "isenhart": "আইজেনহার্ট",
    "jasmin": "ইয়াসমিন", "jonas": "ইয়োনাস", "bankraub": "বাঙ্করাউব",
    "draußen": "ড্রাউসেন", "kopf": "কোফ", "meine": "মাইনে",
    "nachbarn": "নাখবারন", "dicken": "ডিকেন", "hund": "হুনড",
    "familie": "ফামিলিয়ে", "immer": "ইমার", "zurück": "সুরুক",
    "tote": "টোটে", "zwei": "স্বাই", "zweite": "স্বাইটে", "zweiten": "স্বাইটেন",
    "zweiter": "স্বাইটার", "zweites": "স্বাইটেস", "zweimal": "স্বাইমাল", "zoff": "সফ",
    "lichtenbergs": "লিখটেনবের্গস", "lichtenberg": "লিখটেনবের্গ", "letzte": "লেৎসটে", "vater": "ফাটার",
    "allein": "আলাইন", "mein": "মাইন", "keine": "কাইনে", "weg": "ভেগ",
    "alles": "আলেস", "mehr": "মেয়ার", "uns": "উন্স", "ende": "এন্ডে",
    "stille": "স্টিলে", "stilles": "স্টিলেস", "tal": "তাল",
    "keiner": "কাইনার", "geht": "গেট", "kommt": "কমট",
    "tochter": "টোখটার", "strecke": "স্ট্রেক", "freier": "ফ্রাইয়ার",
    "halt": "হাল্ট", "seitenwechsel": "সাইটেনভেকসেল",
    "fall": "ফাল", "bis": "বিস", "horizont": "হোরিৎসোন্ট", "dann": "ডান",
    "links": "লিংক্স", "millionen": "মিলিয়নেন", "fremde": "ফ্রেমডে",
    "kannibalen": "কানিবালেন", "brüder": "ব্রুডার", "bruder": "ব্রুডার",
    "freies": "ফ্রাইয়েস", "freie": "ফ্রাইয়ে", "frei": "ফ্রাই",
    "sibirien": "সিবিরিয়েন", "wollten": "ভলটেন", "blinde": "ব্লিন্ডে",
    "blinder": "ব্লিন্ডার", "fleck": "ফ্লেক", "könig": "কোনিগ", "könige": "কোনিগে",
    "kann": "কান", "können": "কোনেন", "soll": "জল", "sollen": "জলেন",
    "macht": "মাখট", "große": "গ্রোসে", "groß": "গ্রোস", "kleine": "ক্লাইনে",
    "klein": "ক্লাইন", "schöne": "শোনে", "schön": "শোন", "neue": "নয়ে",
    "neu": "নয়", "alte": "আল্টে", "alt": "আল্ট", "gute": "গুটে",
    "böser": "বোসার", "böse": "বোসে", "stunde": "স্টুনডে", "stunden": "স্টুনডেন",
    "minuten": "মিনুটেন", "sekunden": "সেকুনডেন", "gestern": "গেস্টার্ন",
    "heute": "হয়টে", "morgen": "মরগেন", "wieder": "ভিডার", "ohne": "ওনে",
    "durch": "ডুর্খ", "gegen": "গেগেন", "nichts": "নিখটস", "etwas": "এতভাস",
    "jeder": "ইয়েডার", "jede": "ইয়েডে", "jedes": "ইয়েডেস", "jeden": "ইয়েডেন",
}

GERMAN_MARKERS = set(DE_WORDS.keys()) | set([
    'ä', 'ö', 'ü', 'ß', 'jahr', 'jahre', 'jahren', 'kein', 'doch', 'schon',
    'durch', 'hinter', 'neben', 'beim', 'ins', 'ans', 'aufs'
])

ENGLISH_MARKERS = set(EN_WORDS.keys()) | set([
    'the', 'of', 'and', 'to', 'a', 'an', 'in', 'on', 'for', 'from', 'with', 'without',
    'by', 'about', 'into', 'through', 'after', 'over', 'between', 'out', 'against',
    'during', 'before', 'under', 'around', 'among', 'is', 'are', 'was', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'shall',
    'should', 'may', 'might', 'must', 'can', 'could', 'not', 'no', 'nor', 'my', 'your',
    'his', 'her', 'its', 'our', 'their', 'this', 'that', 'these', 'those', 'what', 'which',
    'who', 'whom', 'whose', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'only', 'own', 'same', 'so', 'than',
    'too', 'very', 'just', 'dont', 'cant', 'wont'
])


def detect_language(text: str) -> str:
    """একটি শিরোনাম জার্মান নাকি ইংরেজি তা নিরূপণ করে।"""
    t_lower = text.lower()
    if any(c in t_lower for c in 'äöüß'):
        return 'de'
    words = re.findall(r'[a-z]+', t_lower)
    de_score = sum(2 for w in words if w in GERMAN_MARKERS)
    en_score = sum(2 for w in words if w in ENGLISH_MARKERS)
    if de_score > en_score:
        return 'de'
    return 'en'


def strip_outer_quotes(s: str) -> str:
    """উইকিলিংক ও শিরোনামের ভেতরের এবং বাইরের অনাকাঙ্ক্ষিত উদ্ধৃতি চিহ্ন পরিষ্কার করে।"""
    s = s.strip()
    while True:
        changed = False
        if (s.startswith("''") and s.endswith("''") and len(s) >= 4) or \
           (s.startswith('""') and s.endswith('""') and len(s) >= 4):
            s = s[2:-2].strip()
            changed = True
        elif (s.startswith('"') and s.endswith('"') and len(s) >= 2) or \
             (s.startswith("'") and s.endswith("'") and len(s) >= 2) or \
             (s.startswith('“') and s.endswith('”') and len(s) >= 2) or \
             (s.startswith('‘') and s.endswith('’') and len(s) >= 2):
            s = s[1:-1].strip()
            changed = True
        if not changed:
            break
    return s


def transliterate_english_phonetic(clean: str) -> str:
    """ইংরেজি শব্দের নিয়মভিত্তিক ধ্বনিতাত্ত্বিক প্রতিবর্ণীকরণ।"""
    w = clean.lower()
    
    # বিশেষ একক সিলেবল শব্দ যা y দিয়ে শেষ হয়
    monosyllable_y = {
        'fly': 'ফ্লাই', 'sky': 'স্কাই', 'spy': 'স্পাই', 'dry': 'ড্রাই',
        'try': 'ট্রাই', 'cry': 'ক্রাই', 'why': 'হোয়াই', 'by': 'বাই',
        'my': 'মাই', 'shy': 'শাই'
    }
    if w in monosyllable_y:
        return monosyllable_y[w]

    # বিভক্তি ও প্রত্যয়
    w = re.sub(r'cation\b', 'কেশন', w)
    w = re.sub(r'tion\b', 'শন', w)
    w = re.sub(r'sion\b', 'শন', w)
    w = re.sub(r'ture\b', 'চার', w)
    w = re.sub(r'ous\b', 'আস', w)
    w = re.sub(r'age\b', 'এজ', w)
    w = re.sub(r'ace\b', 'এস', w)
    w = re.sub(r'ake\b', 'এক', w)
    w = re.sub(r'ame\b', 'এম', w)
    w = re.sub(r'ate\b', 'য়েট', w)
    w = re.sub(r'ave\b', 'এভ', w)
    w = re.sub(r'ight\b', 'াইট', w)
    w = re.sub(r'rough\b', 'রাফ', w)
    w = re.sub(r'tough\b', 'টাফ', w)
    w = re.sub(r'laugh', 'লাফ', w)
    w = re.sub(r'augh', 'অট', w)
    w = re.sub(r'alk\b', 'অক', w)
    w = re.sub(r'all\b', 'অল', w)
    w = re.sub(r'air\b', 'এয়ার', w)
    w = re.sub(r'are\b', 'এয়ার', w)

    # অতীত কালের -ed
    w = re.sub(r'pped\b', 'পড', w)
    w = re.sub(r'tted\b', 'টেড', w)
    w = re.sub(r'cked\b', 'কড', w)
    w = re.sub(r'ssed\b', 'সড', w)
    w = re.sub(r'shed\b', 'শড', w)
    w = re.sub(r'ched\b', 'চড', w)
    w = re.sub(r'led\b', 'ল্ড', w)
    w = re.sub(r'red\b', 'র্ড', w)
    w = re.sub(r'med\b', 'ম্ড', w)
    w = re.sub(r'ned\b', 'ন্ড', w)
    w = re.sub(r'ed\b', 'ড', w)

    # সাধারণ গুচ্ছ ও ব্যঞ্জনধ্বনি
    w = re.sub(r'^wh', 'হোয়া', w)
    w = re.sub(r'^wr', 'র', w)
    w = re.sub(r'^kn', 'ন', w)
    w = re.sub(r'^ps', 'স', w)
    w = re.sub(r'sh', 'শ', w)
    w = re.sub(r'ch', 'চ', w)
    w = re.sub(r'th', 'থ', w)
    w = re.sub(r'ph', 'ফ', w)
    w = re.sub(r'ck', 'ক', w)
    w = re.sub(r'qu', 'কোয়া', w)

    # দ্বিস্বর ও স্বরধ্বনি
    w = re.sub(r'ee', 'ই', w)
    w = re.sub(r'ea', 'ই', w)
    w = re.sub(r'oo', 'উ', w)
    w = re.sub(r'ou', 'আউ', w)
    w = re.sub(r'ow\b', 'ও', w)
    w = re.sub(r'ow', 'আউ', w)
    w = re.sub(r'ai', 'এ', w)
    w = re.sub(r'ay', 'এ', w)
    w = re.sub(r'oa', 'ও', w)
    w = re.sub(r'oi', 'অয়', w)
    w = re.sub(r'([bcdfghjklmnpqrstvwxyz])oy\b', r'\1য়', w)
    w = re.sub(r'oy', 'অয়', w)
    w = re.sub(r'father', 'ফাদার', w)
    w = re.sub(r'mother', 'মাদার', w)
    w = re.sub(r'brother', 'ব্রাদার', w)
    w = re.sub(r'hood\b', 'হুড', w)

    # প্রাথমিক গুচ্ছ
    w = re.sub(r'^str', 'স্ট্র', w)
    w = re.sub(r'^spr', 'স্প্র', w)
    w = re.sub(r'^scr', 'স্ক্র', w)
    w = re.sub(r'^spl', 'স্প্ল', w)
    w = re.sub(r'^br', 'ব্র', w)
    w = re.sub(r'^cr', 'ক্র', w)
    w = re.sub(r'^dr', 'ড্র', w)
    w = re.sub(r'^fr', 'ফ্র', w)
    w = re.sub(r'^gr', 'গ্র', w)
    w = re.sub(r'^pr', 'প্র', w)
    w = re.sub(r'^tr', 'ট্র', w)
    w = re.sub(r'^cl', 'ক্ল', w)
    w = re.sub(r'^fl', 'ফ্ল', w)
    w = re.sub(r'^gl', 'গ্ল', w)
    w = re.sub(r'^pl', 'প্ল', w)
    w = re.sub(r'^bl', 'ব্ল', w)
    w = re.sub(r'^sl', 'স্ল', w)
    w = re.sub(r'^sm', 'স্ম', w)
    w = re.sub(r'^sn', 'স্ন', w)
    w = re.sub(r'^sp', 'স্প', w)
    w = re.sub(r'^st', 'স্ট', w)
    w = re.sub(r'^sw', 'সোয়', w)
    w = re.sub(r'^sk', 'স্ক', w)
    w = re.sub(r'^sc', 'স্ক', w)
    w = re.sub(r'^gh', 'ঘ', w)

    # দ্বৈত ব্যঞ্জনবর্ণ সরলীকরণ
    w = re.sub(r'bb', 'ব', w)
    w = re.sub(r'dd', 'ড', w)
    w = re.sub(r'ff', 'ফ', w)
    w = re.sub(r'gg', 'গ', w)
    w = re.sub(r'kk', 'ক', w)
    w = re.sub(r'll', 'ল', w)
    w = re.sub(r'mm', 'ম', w)
    w = re.sub(r'nn', 'ন', w)
    w = re.sub(r'pp', 'প', w)
    w = re.sub(r'rr', 'র', w)
    w = re.sub(r'ss', 'স', w)
    w = re.sub(r'tt', 'ট', w)

    # c ও g
    w = re.sub(r'c([eiy])', r'স\1', w)
    w = re.sub(r'c', 'ক', w)
    w = re.sub(r'j', 'জ', w)
    w = re.sub(r'g([eiy])', r'জ\1', w)
    w = re.sub(r'g', 'গ', w)

    # একক ব্যঞ্জনবর্ণ
    w = re.sub(r'^s([bcdfghjklmnpqrstvwxyz])', r'স্\1', w)
    w = re.sub(r's', 'স', w)
    w = re.sub(r'z', 'জ', w)
    w = re.sub(r'x', 'ক্স', w)
    w = re.sub(r'b', 'ব', w)
    w = re.sub(r'd', 'ড', w)
    w = re.sub(r'f', 'ফ', w)
    w = re.sub(r'h', 'হ', w)
    w = re.sub(r'k', 'ক', w)
    w = re.sub(r'l', 'ল', w)
    w = re.sub(r'm', 'ম', w)
    w = re.sub(r'n', 'ন', w)
    w = re.sub(r'p', 'প', w)
    w = re.sub(r'r', 'র', w)
    w = re.sub(r't', 'ট', w)
    w = re.sub(r'v', 'ভ', w)
    w = re.sub(r'w', 'ওয়', w)
    w = re.sub(r'y\b', 'ি', w)
    w = re.sub(r'y', 'ইয়', w)

    w = re.sub(r'er\b', 'ার', w)
    w = re.sub(r'ers\b', 'ার্স', w)
    w = re.sub(r'ing\b', 'িং', w)
    w = re.sub(r'nd\b', 'ন্ড', w)
    w = re.sub(r'nt\b', 'ন্ট', w)
    w = re.sub(r'ct\b', 'ক্ট', w)
    w = re.sub(r'ld\b', 'ল্ড', w)
    w = re.sub(r'st\b', 'স্ট', w)
    w = re.sub(r'rk\b', 'র্ক', w)
    w = re.sub(r'rt\b', 'র্ট', w)
    w = re.sub(r'rn\b', 'র্ন', w)
    w = re.sub(r'rm\b', 'র্ম', w)
    w = re.sub(r'ia\b', 'িয়া', w)

    # স্বরবর্ণ
    w = re.sub(r'a', 'আ', w)
    if len(w) > 2:
        w = re.sub(r'e\b', '', w)
    w = re.sub(r'e', 'এ', w)
    w = re.sub(r'i', 'ই', w)
    w = re.sub(r'o', 'ও', w)
    w = re.sub(r'u', 'আ', w)

    VOWEL_TO_KAR = {'আ': 'া', 'ই': 'ি', 'উ': 'ু', 'এ': 'ে', 'ও': 'ো'}
    CONSONANTS = set('কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎ')
    out_c = []
    for ch in w:
        if ch in VOWEL_TO_KAR and out_c and out_c[-1] in CONSONANTS:
            out_c.append(VOWEL_TO_KAR[ch])
        else:
            out_c.append(ch)
    bn = "".join(out_c)

    # দ্বৈত ব্যঞ্জনবর্ণ পরিহার
    for c in 'কগটডতদপবমসলনরফ':
        bn = re.sub(c + c, c, bn)

    if bn.startswith('ৎস'):
        bn = 'স' + bn[2:]
    elif bn.startswith('ৎ'):
        bn = 'স' + bn[1:]
    return bn


def transliterate_word(word: str, lang: str = 'en') -> str:
    """একক ইংরেজি বা জার্মান শব্দকে বাংলায় লিপ্যন্তর করে।"""
    clean = word.strip(" '\"-–—:;,!?./()[]{}#*`“”‘’")
    if not clean:
        return word
    if clean.isdigit():
        return word.replace(clean, clean.translate(BENGALI_DIGITS))
    
    cl_lower = clean.lower()

    # ১. বিশেষ সাধারণ সত্তা ও নাম (উভয় ভাষার জন্য প্রযোজ্য)
    if cl_lower in SHARED_ENTITIES:
        return word.replace(clean, SHARED_ENTITIES[cl_lower])

    # ২. ভাষা অনুযায়ী শব্দভাণ্ডার
    if lang == 'de':
        if cl_lower in DE_WORDS:
            return word.replace(clean, DE_WORDS[cl_lower])
        if cl_lower in EN_WORDS:
            return word.replace(clean, EN_WORDS[cl_lower])
        try:
            bn = transliterate_token(clean)
            return word.replace(clean, bn)
        except Exception:
            return word.replace(clean, transliterate_english_phonetic(clean))
    else:
        if cl_lower in EN_WORDS:
            return word.replace(clean, EN_WORDS[cl_lower])
        if cl_lower in DE_WORDS:
            return word.replace(clean, DE_WORDS[cl_lower])
        try:
            if cl_lower in FIRST_NAMES:
                return word.replace(clean, FIRST_NAMES[cl_lower])
        except Exception:
            pass
        return word.replace(clean, transliterate_english_phonetic(clean))


def transliterate_title_text(text: str) -> str:
    """সম্পূর্ণ শিরোনামের টেক্সটকে প্রমিত বাংলা হরফে রূপান্তর করে।"""
    # &nbsp; ও অতিরিক্ত চিহ্ন দূরীকরণ
    clean = re.sub(r'(&nbsp;|&#160;)', ' ', text)
    clean = re.sub(r'\s*\(\d{4}\s+film\)', '', clean, flags=re.I)
    clean = re.sub(r'\s*\(film\)', '', clean, flags=re.I)
    clean = re.sub(r'\s*\(\d{4}\)', '', clean)
    clean = strip_outer_quotes(clean)
    
    lang = detect_language(clean)
    tokens = re.split(r'(\s+|[–—\-:;,!?./\(\)\[\]\"`“”‘’]|(?<![a-zA-Z0-9])\'|\'(?![a-zA-Z0-9]))', clean)
    out = []
    for t in tokens:
        if not t:
            continue
        if re.match(r'^\s+$', t) or t in "–—-–:;,!?./()[]'\"`“”‘’":
            out.append(t)
        else:
            out.append(transliterate_word(t, lang=lang))
            
    res = "".join(out).strip()
    res = res.translate(BENGALI_DIGITS)
    res = re.sub(r'(^|[\s\-\(])ৎ[স]?', r'\1স', res)
    # সেন্ট. -> সেন্ট
    res = re.sub(r'\bসেন্ট\.\s*', 'সেন্ট ', res)
    res = re.sub(r'\.\.+', '.', res)
    return res


def format_film_title_cell(title_cell: str, notes_cell: str) -> str:
    """
    চলচ্চিত্রের শিরোনাম শতভাগ প্রমিত বাংলায় লেখে এবং উইকি লিঙ্ক বাংলায় রাখে।
    সাথে মূল জার্মান নাম পাশে বন্ধনীতে রাখে।
    ফরম্যাট: ''[[লিংক|বাংলা শিরোনাম]]'' (''মূল শিরোনাম'') বা ''[[বাংলা শিরোনাম]]'' (''মূল শিরোনাম'')
    """
    raw = re.sub(r'(&nbsp;|&#160;)', ' ', title_cell).strip()
    clean_notes = re.sub(r'(&nbsp;|&#160;)', ' ', notes_cell).strip()
    
    target = ""
    display = ""
    german_from_ill = ""
    
    ill_m = re.search(r'\{\{(?:ill|Interlanguage link)\|([^|}]+)(?:\|([^}]+))?\}\}', raw, re.I)
    if ill_m:
        full_tmpl = ill_m.group(0)
        target = strip_outer_quotes(ill_m.group(1))
        lt_m = re.search(r'\|lt=([^|}]+)', full_tmpl)
        display = strip_outer_quotes(lt_m.group(1)) if lt_m else target
        
        # de প্যারামিটার থেকে মূল জার্মান শিরোনাম বের করা
        params = [strip_outer_quotes(p) for p in re.sub(r'\|\s*\}\}', '}}', full_tmpl)[2:-2].split('|')]
        for idx, p in enumerate(params):
            if p.lower() == 'de' and idx + 1 < len(params):
                nxt = params[idx+1]
                if nxt and not nxt.startswith(('lt=', 'display=', 'fr', 'en', 'ar', 'arz', 'pl', 'it', 'es', 'nl')):
                    german_from_ill = nxt
                    break
        if not german_from_ill and 'de' in [p.lower() for p in params]:
            german_from_ill = target
    else:
        wiki_m = re.search(r'\[\[([^|\]]+)(?:\|([^\]]+))?\]\]', raw)
        if wiki_m:
            target = strip_outer_quotes(wiki_m.group(1))
            display = strip_outer_quotes(wiki_m.group(2)) if wiki_m.group(2) else target
        else:
            raw_clean = strip_outer_quotes(raw)
            target = raw_clean
            display = raw_clean
            
    clean_disp = re.sub(r'\s*\(\d{4}\s+film\)', '', display, flags=re.I)
    clean_disp = re.sub(r'\s*\(film\)', '', clean_disp, flags=re.I)
    clean_disp = re.sub(r'\s*\(\d{4}\)', '', clean_disp)
    clean_disp = strip_outer_quotes(clean_disp)
    
    # মূল জার্মান শিরোনাম নির্বাচন
    german_title = ""
    if german_from_ill:
        german_title = german_from_ill
    elif detect_language(clean_disp) == 'de':
        german_title = clean_disp
    elif target and detect_language(target) == 'de':
        german_title = target
    else:
        # aka থেকে মূল জার্মান শিরোনাম সন্ধান
        akas = re.findall(r"\{\{aka\}\}\s*(?:''|\"|')?([^'\"\n]+?)(?:''|\"|')?(?:\s*<br|\s*,\s*|\s*$)", clean_notes, re.I)
        if akas:
            for a in akas:
                a_clean = strip_outer_quotes(a)
                if detect_language(a_clean) == 'de' or any(c in a_clean for c in 'äöüß'):
                    german_title = a_clean
                    break
                    
    if not german_title:
        german_title = clean_disp
        
    # ডিসঅ্যাম্বিগুয়েশন ও উদ্ধৃতি পরিষ্কার
    german_title = re.sub(r'\s*\(\d{4}\s+film\)', '', german_title, flags=re.I)
    german_title = re.sub(r'\s*\(film\)', '', german_title, flags=re.I)
    german_title = re.sub(r'\s*\(\d{4}\)', '', german_title)
    german_title = strip_outer_quotes(german_title)
    
    # মূল জার্মান শিরোনাম থেকেই প্রধান বাংলা শিরোনাম তৈরি করা
    bn_title = transliterate_title_text(german_title)
    bn_title = strip_outer_quotes(bn_title)
    
    # উইকি লিঙ্ক বাংলায় গঠন
    bn_link = bn_title
    y_m = re.search(r'\((\d{4})\s+film\)', target, re.I)
    if not y_m:
        y_m = re.search(r'\((\d{4})\)', target)
    if y_m:
        year_bn = y_m.group(1).translate(BENGALI_DIGITS)
        bn_link = f"{bn_title} ({year_bn}-এর চলচ্চিত্র)"
    elif re.search(r'\(film\)', target, re.I):
        bn_link = f"{bn_title} (চলচ্চিত্র)"
        
    # প্রমিত ফলাফল গঠন (শতভাগ বাংলা উইকিলিংক, কোনো [de] বা {{ill}} নেই)
    if bn_link == bn_title:
        return f"''[[{bn_title}]]'' (''{german_title}'')"
    else:
        return f"''[[{bn_link}|{bn_title}]]'' (''{german_title}'')"
