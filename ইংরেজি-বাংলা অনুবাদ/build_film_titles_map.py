# -*- coding: utf-8 -*-
import json
import re
import transliterate_engine as te

with open('unique_films_summary.json', encoding='utf-8') as f:
    unique_films = json.load(f)

with open('title_words_final.json', encoding='utf-8') as f:
    dict_words = json.load(f)

# Import extra words from test_dict_setup
from test_dict_setup import EXTRA_WORDS, clean_bn_wiki_title

dict_words.update(EXTRA_WORDS)

# Direct full-title overrides for titles with established Bengali forms or special foreign names
KNOWN_FULL_TITLES = {
    'The Enchanted Drawing': 'দি এনচান্টেড ড্রয়িং',
    'Gertie the Dinosaur': 'গার্টি দ্য ডাইনোসর',
    'När Kapten Grogg skulle porträtteras': 'নার কাপতেন গ্রগ স্কুলে পোরত্রেতেরাস',
    'Out of the Inkwell': 'আউট অব দি ইংকওয়েল',
    'Alice Comedies': 'অ্যালিস কমেডিজ',
    'Bosko, the Talk-Ink Kid': 'বস্কো, দ্য টক-ইংক কিড',
    'Zero for Conduct': 'জিরো ফর কন্ডাক্ট',
    'Puppet Show': 'পাপেট শো',
    'Daffy Duck in Hollywood': 'ড্যাফি ডাক ইন হলিউড',
    'You Ought to Be in Pictures': 'ইউ অট টু বি ইন পিকচার্স',
    "Eatin' on the Cuff or The Moth Who Came to Dinner": "ইটিন অন দ্য কাফ অর দ্য মথ হু কেম টু ডিনার",
    'Who Killed Who?': 'হু কিল্ড হু?',
    "What's Cookin' Doc?": "হোয়াটস কুকিন ডক?",
    'Señor Droopy': 'সিনিয়র ড্রুপি',
    'The House of Tomorrow': 'দ্য হাউস অব টুমরো',
    'Rabbit Hood': 'র‍্যাবিট হুড',
    'My Dream Is Yours': 'মাই ড্রিম ইজ ইয়োরস',
    'Cold Turkey': 'কোল্ড টার্কি',
    'The Three Little Pups': 'দ্য থ্রি লিটল পাপস',
    'Donald in Mathmagic Land': 'ডোনাল্ড ইন ম্যাথম্যাজিক ল্যান্ড',
    'The Mouse That Jack Built': 'দ্য মাউস দ্যাট জ্যাক বিল্ট',
    'Donald and the Wheel': 'ডোনাল্ড অ্যান্ড দ্য হুইল',
    'The Litterbug': 'দ্য লিটারবাগ',
    'Pink Panzer': 'পিঙ্ক প্যানজার',
    'Winnie the Pooh and the Honey Tree': 'উইনি দ্য পুহ অ্যান্ড দ্য হানি ট্রি',
    'Jack and the Beanstalk': 'জ্যাক অ্যান্ড দ্য বিনস্টক',
    'Winnie the Pooh and the Blustery Day': 'উইনি দ্য পুহ অ্যান্ড দ্য ব্লাস্টারি ডে',
    'The Adventures of Milo in the Phantom Tollbooth': 'দি অ্যাডভেঞ্চার্স অব মাইলো ইন দ্য ফ্যান্টম টোলবুথ',
    'Winnie the Pooh and Tigger Too': 'উইনি দ্য পুহ অ্যান্ড টিগার টু',
    "Bugs and Daffy's Carnival of the Animals": 'বাগস অ্যান্ড ড্যাফিস কার্নিভাল অব দি অ্যানিম্যালস',
    'Winnie the Pooh and a Day for Eeyore': 'উইনি দ্য পুহ অ্যান্ড আ ডে ফর ইওর',
    'What Have We Learned, Charlie Brown?': 'হোয়াট হ্যাভ উই লার্নড, চার্লি ব্রাউন?',
    'Deepa & Rupa: A Fairy Tale from India': 'দীপা অ্যান্ড রূপা: আ ফেয়ারি টেল ফ্রম ইন্ডিয়া',
    "Rockin' Through the Decades": "রকিন থ্রু দ্য ডেকেডস",
    'Nilus the Sandman: The Boy Who Dreamed Christmas': 'নিলুস দ্য স্যান্ডম্যান: দ্য বয় হু ড্রিমড ক্রিসমাস',
    "Attack of the 50 Foot Woman": "অ্যাটাক অব দ্য ৫০ ফুট ওম্যান",
    "Stay Tuned": "স্টে টিউনড",
    "Cool World": "কুল ওয়ার্ল্ড",
    "Space Jam": "স্পেস জ্যাম",
    "Space Jam: A New Legacy": "স্পেস জ্যাম: আ নিউ লেগ্যাসি",
    "Who Framed Roger Rabbit": "হু ফ্রেমড রজার র‍্যাবিট",
    "Mary Poppins": "মেরি পপিন্স",
    "Mary Poppins Returns": "মেরি পপিন্স রিটার্নস",
    "Bedknobs and Broomsticks": "বেডনব্স অ্যান্ড ব্রুমস্টিকস",
    "Pete's Dragon": "পিটস ড্রাগন",
    "Song of the South": "সং অব দ্য সাউথ",
    "The Water Babies": "দ্য ওয়াটার বেবিস",
    "James and the Giant Peach": "জেমস অ্যান্ড দ্য জায়ান্ট পিচ",
    "Osmosis Jones": "অসমোসিস জোন্স",
    "The Lego Movie": "দ্য লেগো মুভি",
    "The Lego Movie 2: The Second Part": "দ্য লেগো মুভি ২: দ্য সেকেন্ড পার্ট",
    "The Lego Batman Movie": "দ্য লেগো ব্যাটম্যান মুভি",
    "The Lego Ninjago Movie": "দ্য লেগো নিনজাগো মুভি",
    "Paddington": "প্যাডিংটন",
    "Paddington 2": "প্যাডিংটন ২",
    "Paddington in Peru": "প্যাডিংটন ইন পেরু",
    "Peter Rabbit": "পিটার র‍্যাবিট",
    "Peter Rabbit 2: The Runaway": "পিটার র‍্যাবিট ২: দ্য রানঅ্যাওয়ে",
    "Enchanted": "এনচান্টেড",
    "Disenchanted": "ডিসএনচান্টেড",
    "Ted": "টেড",
    "Ted 2": "টেড ২",
    "The Smurfs": "দ্য স্মার্ফস",
    "The Smurfs 2": "দ্য স্মার্ফস ২",
    "Smurfs: The Lost Village": "স্মার্ফস: দ্য লস্ট ভিলেজ",
    "Alvin and the Chipmunks": "অ্যালভিন অ্যান্ড দ্য চিপমাঙ্কস",
    "Alvin and the Chipmunks: The Squeakquel": "অ্যালভিন অ্যান্ড দ্য চিপমাঙ্কস: দ্য স্ক্যুইককুয়েল",
    "Alvin and the Chipmunks: Chipwrecked": "অ্যালভিন অ্যান্ড দ্য চিপমাঙ্কস: চিপরেকড",
    "Alvin and the Chipmunks: The Road Chip": "অ্যালভিন অ্যান্ড দ্য চিপমাঙ্কস: দ্য রোড চিপ",
    "Garfield": "গারফিল্ড",
    "Garfield: A Tail of Two Kitties": "গারফিল্ড: আ টেইল অব টু কিটিজ",
    "Casper": "ক্যাসপার",
    "Casper: A Spirited Beginning": "ক্যাসপার: আ স্পিরিটেড বিগিনিং",
    "Casper Meets Wendy": "ক্যাসপার মিটস ওয়েন্ডি",
    "Scooby-Doo": "স্কুবি-ডু",
    "Scooby-Doo 2: Monsters Unleashed": "স্কুবি-ডু ২: মনস্টার্স আনলিশড",
    "Stuart Little": "স্টুয়ার্ট লিটল",
    "Stuart Little 2": "স্টুয়ার্ট লিটল ২",
    "Stuart Little 3: Call of the Wild": "স্টুয়ার্ট লিটল ৩: কল অব দ্য ওয়াইল্ড",
    "The Mask": "দ্য মাস্ক",
    "Son of the Mask": "সন অব দ্য মাস্ক",
    "The SpongeBob SquarePants Movie": "দ্য স্পঞ্জবব স্কয়ারপ্যান্টস মুভি",
    "The SpongeBob Movie: Sponge Out of Water": "দ্য স্পঞ্জবব মুভি: স্পঞ্জ আউট অব ওয়াটার",
    "The SpongeBob Movie: Sponge on the Run": "দ্য স্পঞ্জবব মুভি: স্পঞ্জ অন দ্য রান",
    "The SpongeBob Movie: Search for SquarePants": "দ্য স্পঞ্জবব মুভি: সার্চ ফর স্কয়ারপ্যান্টস",
    "Fat Albert": "ফ্যাট অ্যালবার্ট",
    "Clifford the Big Red Dog": "ক্লিফোর্ড দ্য বিগ রেড ডগ",
    "The Adventures of Rocky and Bullwinkle": "দি অ্যাডভেঞ্চার্স অব রকি অ্যান্ড বুলউইঙ্কল",
    "Arthur and the Invisibles": "আর্থার অ্যান্ড দ্য ইনভিজিবলস",
    "Arthur and the Revenge of Maltazard": "আর্থার অ্যান্ড দ্য রিভেঞ্জ অব মালতাজার্ড",
    "Arthur 3: The War of the Two Worlds": "আর্থার ৩: দ্য ওয়ার অব দ্য টু ওয়ার্ল্ডস",
    "Looney Tunes: Back in Action": "লুনি টিউনস: ব্যাক ইন অ্যাকশন",
    "Little Shop of Horrors": "লিটল শপ অব হররস",
    "The Polar Express": "দ্য পোলার এক্সপ্রেস",
    "Transformers": "ট্রান্সফর্মার্স",
    "Transformers: Revenge of the Fallen": "ট্রান্সফর্মার্স: রিভেঞ্জ অব দ্য ফলেন",
    "Transformers: Dark of the Moon": "ট্রান্সফর্মার্স: ডার্ক অব দ্য মুন",
    "Transformers: Age of Extinction": "ট্রান্সফর্মার্স: এজ অব এক্সটিঙ্কশন",
    "Transformers: The Last Knight": "ট্রান্সফর্মার্স: দ্য লাস্ট নাইট",
    "Bumblebee": "বাম্বলবি",
    "Transformers: Rise of the Beasts": "ট্রান্সফর্মার্স: রাইজ অব দ্য বিস্টস",
    "Sonic the Hedgehog": "সনিক দ্য হেজহগ",
    "Sonic the Hedgehog 2": "সনিক দ্য হেজহগ ২",
    "Sonic the Hedgehog 3": "সনিক দ্য হেজহগ ৩",
    "Sonic the Hedgehog 4": "সনিক দ্য হেজহগ ৪",
    "A Minecraft Movie": "আ মাইনক্রাফট মুভি",
    "A Minecraft Movie Squared": "আ মাইনক্রাফট মুভি স্কয়ার্ড",
    "How to Train Your Dragon": "হাউ টু ট্রেইন ইয়োর ড্রাগন",
    "How to Train Your Dragon 2": "হাউ টু ট্রেইন ইয়োর ড্রাগন ২",
    "Moana": "মোয়ানা",
    "Lilo & Stitch": "লিলো অ্যান্ড স্টিচ",
    "Joker: Folie à Deux": "জোকার: ফোলি আ দ্যো",
    "Candy Cane Lane": "ক্যান্ডি কেন লেন",
    "Winnie-the-Pooh: Blood and Honey": "উইনি-দ্য-পুহ: ব্লাড অ্যান্ড হানি",
    "Strays": "স্ট্রেস",
    "Blue Beetle": "ব্লু বিটল",
    "The Mean One": "দ্য মিন ওয়ান",
    "Lyle, Lyle, Crocodile": "লাইল, লাইল, ক্রোকোডাইল",
    "Pinocchio": "পিনোকিও",
    "Better Man": "বেটার ম্যান",
    "IF": "ইফ",
    "Woody Woodpecker Goes to Camp": "উডি উডপেকার গোজ টু ক্যাম্প",
    "Harold and the Purple Crayon": "হ্যারল্ড অ্যান্ড দ্য পার্পল ক্রায়ন",
    "Bambi: The Reckoning": "বাম্বি: দ্য রেকনিং",
    "Gabby's Dollhouse: The Movie": "গ্যাবীয়াস ডলহাউস: দ্য মুভি",
    "Scary Movie": "স্ক্যারি মুভি",
    "Coyote vs. Acme": "কায়োটি ভার্সেস অ্যাকমি",
    "Animal Friends": "অ্যানিম্যাল ফ্রেন্ডস",
    "Saving Bikini Bottom: The Sandy Cheeks Movie": "সেভিং বিকিনি বটম: দ্য স্যান্ডি চিকস মুভি",
    "Ryan's World the Movie: Titan Universe Adventure": "রায়ানস ওয়ার্ল্ড দ্য মুভি: টাইটান ইউনিভার্স অ্যাডভেঞ্চার",
    "Chip 'n Dale: Rescue Rangers": "চিপ অ্যান্ড ডেল: রেসকিউ রেঞ্জার্স",
    "Disenchanted": "ডিসএনচান্টেড",
    "The Guardians of the Galaxy Holiday Special": "দ্য গার্ডিয়ানস অব দ্য গ্যালাক্সি হলিডে স্পেশাল",
    "Mickey: The Story of a Mouse": "মিকি: দ্য স্টোরি অব আ মাউস",
    "Beau Is Afraid": "বো ইজ অ্যাফ্রেইড",
    "Abruptio": "আব্রাপশিও",
    "Shazam! Fury of the Gods": "শাজাম! ফিউরি অব দ্য গডস",
    "Ayalaan": "আয়ালান",
    "Argylle": "আর্গাইল",
    "Everything Everywhere All at Once": "এভরিথিং এভরিওয়েআর অল অ্যাট ওয়ান্স",
    "Doctor Strange in the Multiverse of Madness": "ডক্টর স্ট্রেঞ্জ ইন দ্য মাল্টিভার্স অব ম্যাডনেস",
    "Karthikeya 2": "কার্তিকেয় ২",
    "Spider-Man: No Way Home": "স্পাইডার-ম্যান: নো ওয়ে হোম",
    "Spider-Man: Far From Home": "স্পাইডার-ম্যান: ফার ফ্রম হোম",
    "Spider-Man: Homecoming": "স্পাইডার-ম্যান: হোমকামিং",
    "Spider-Man: Across the Spider-Verse": "স্পাইডার-ম্যান: অ্যাক্রোস দ্য স্পাইডার-ভার্স",
    "Spider-Man: Into the Spider-Verse": "স্পাইডার-ম্যান: ইনটু দ্য স্পাইডার-ভার্স",
    "Blue's Big City Adventure": "ব্লুজ বিগ সিটি অ্যাডভেঞ্চার",
    "Happier Than Ever: A Love Letter to Los Angeles": "হ্যাপিয়ার দ্যান এভার: আ লাভ লেটার টু লস অ্যাঞ্জেলেস",
    "Tom and Jerry": "টম অ্যান্ড জেরি",
    "Tom & Jerry": "টম অ্যান্ড জেরি",
    "The Fantastic Four: First Steps": "দ্য ফ্যান্টাস্টিক ফোর: ফার্স্ট স্টেপস",
    "Street Fighter": "স্ট্রিট ফাইটার",
    "Jurassic Park": "জুরাসিক পার্ক",
    "Titanic": "টাইটানিক",
    "The Suicide Squad": "দ্য সুইসাইড স্কোয়াড",
    "Deadpool": "ডেডপুল",
    "Kick": "কিক",
    "Eega": "ইগা",
    "Amélie": "অ্যামেলি",
    "Annie Hall": "অ্যানি হল",
    "King Kong": "কিং কং",
    "A Fistful of Dollars": "আ ফিস্টফুল অব ডলার্স",
    "Frankenstein": "ফ্রাঙ্কেনস্টাইন",
    "Aliens": "এলিয়েন্স",
    "Aladdin": "আলাদিন",
    "Beauty and the Beast": "বিউটি অ্যান্ড দ্য বিস্ট",
    "Captain America: The First Avenger": "ক্যাপ্টেন আমেরিকা: দ্য ফার্স্ট অ্যাভেঞ্জার",
    "Captain America: The Winter Soldier": "ক্যাপ্টেন আমেরিকা: দ্য উইন্টার সোলজার",
    "Catch Me If You Can": "ক্যাচ মি ইফ ইউ ক্যান",
    "Coolie No. 1": "কুলি নং ১",
    "Curse of the Pink Panther": "কার্স অব দ্য পিঙ্ক প্যান্থার",
    "Inspector Clouseau": "ইনস্পেক্টর ক্লুজো",
    "Kiss Kiss Bang Bang": "কিস কিস ব্যাং ব্যাং",
    "Me and Earl and the Dying Girl": "মি অ্যান্ড আর্ল অ্যান্ড দ্য ডায়িং গার্ল",
    "O Kadhal Kanmani": "ও কাদাল কানমানি",
    "Once Upon a Girl": "ওয়ান্স আপন আ গার্ল",
    "Percy Jackson: Sea of Monsters": "পার্সি জ্যাকসন: সি অব মনস্টার্স",
    "Pink Floyd – The Wall": "পিংক ফ্লয়েড – দ্য ওয়াল",
    "Rascals": "রাস্কেলস",
    "Revenge of the Pink Panther": "রিভেঞ্জ অব দ্য পিঙ্ক প্যান্থার",
    "Son of the Pink Panther": "সন অব দ্য পিঙ্ক প্যান্থার",
    "Snow White and the Seven Dwarfs": "স্নো হোয়াইট অ্যান্ড দ্য সেভেন ডোয়ার্ফস",
    "Star Wars: The Force Awakens": "স্টার ওয়ার্স: দ্য ফোর্স অ্যাওয়েকেন্স",
    "Star Wars": "স্টার ওয়ার্স",
    "Teddy": "টেডি",
    "The Mitchells vs. the Machines": "দ্য মিচেলস ভার্সেস দ্য মেশিনস",
    "The Pink Panther": "দ্য পিঙ্ক প্যান্থার",
    "The Pink Panther Strikes Again": "দ্য পিঙ্ক প্যান্থার স্ট্রাইকস অ্যাগেইন",
    "The Return of the Pink Panther": "দ্য রিটার্ন অব দ্য পিঙ্ক প্যান্থার",
    "Trail of the Pink Panther": "ট্রেইল অব দ্য পিঙ্ক প্যান্থার",
    "A Shot in the Dark": "আ শট ইন দ্য ডার্ক",
    "Venom: Let There Be Carnage": "ভেনম: লেট দেয়ার বি কার্নেজ",
    "Vertigo": "ভার্টিগো",
    "WALL-E": "ওয়াল-ই",
    "İksir": "ইকসির"
}

def transliterate_token(tok):
    if not tok:
        return ""
    # Check dict
    if tok in dict_words:
        return dict_words[tok]
    if tok.capitalize() in dict_words:
        return dict_words[tok.capitalize()]
    if tok.lower() in dict_words:
        return dict_words[tok.lower()]
    # Roman numerals
    roman_map = {'I': '১ম', 'II': '২য়', 'III': '৩য়', 'IV': '৪র্থ', 'V': '৫ম', 'VI': '৬ষ্ঠ', 'VII': '৭ম', 'VIII': '৮ম', 'IX': '৯ম', 'X': '১০ম'}
    if tok.upper() in roman_map:
        return roman_map[tok.upper()]
    # Numbers
    num_map = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}
    if tok.isdigit():
        return ''.join(num_map.get(d, d) for d in tok)
    # Phonetic engine
    try:
        res = te.transliterate_title_word(tok)
        return res
    except Exception:
        return tok

def transliterate_title(title_text):
    if title_text in KNOWN_FULL_TITLES:
        return KNOWN_FULL_TITLES[title_text]
    
    # Tokenize preserving delimiters
    # e.g., words, apostrophes, hyphens, colons
    parts = re.split(r'([A-Za-z0-9]+)', title_text)
    out = []
    for p in parts:
        if re.match(r'^[A-Za-z0-9]+$', p):
            out.append(transliterate_token(p))
        else:
            # Punctuation / delimiters
            # Convert English digits if any
            p_bn = p.replace('&', 'অ্যান্ড')
            p_bn = p_bn.replace(' vs. ', ' ভার্সেস ').replace(' vs ', ' ভার্সেস ')
            out.append(p_bn)
    res = ''.join(out)
    # Clean up whitespace
    res = re.sub(r'\s+', ' ', res).strip()
    return res

final_film_map = {}
for disp, data in unique_films.items():
    tgt = data['target']
    bn_wiki = data['bn_wiki']
    
    if disp in KNOWN_FULL_TITLES:
        bn_title = KNOWN_FULL_TITLES[disp]
    elif bn_wiki and not any(w in bn_wiki for w in ['উপন্যাস', 'বিভ্রম', 'ধারাবাহিক']):
        bn_title = clean_bn_wiki_title(bn_wiki)
    else:
        bn_title = transliterate_title(disp)
        
    final_film_map[disp] = {
        'target': tgt,
        'bn_wiki': bn_wiki,
        'bn_title': bn_title,
        'original': disp
    }

print(f'Mapped {len(final_film_map)} titles.')
with open('final_film_titles_map.json', 'w', encoding='utf-8') as f:
    json.dump(final_film_map, f, ensure_ascii=False, indent=2)

with open('inspection_film_titles.txt', 'w', encoding='utf-8') as f:
    for k in sorted(final_film_map.keys(), key=str.lower):
        f.write(f"{k:45} -> {final_film_map[k]['bn_title']}\n")

print('Saved final_film_titles_map.json and inspection_film_titles.txt')
