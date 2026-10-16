# -*- coding: utf-8 -*-
"""
Patches generate_final.py with robust transliteration, complete dictionaries, and pristine table output.
"""

new_code = '''# -*- coding: utf-8 -*-
import json
import re
import os

# 1. Load verified caches
with open('author_bn_complete.json', encoding='utf-8') as f:
    author_bn = json.load(f)

with open('book_bn_map.json', encoding='utf-8') as f:
    book_bn = json.load(f)

with open('book_lang.json', encoding='utf-8') as f:
    book_lang = json.load(f)

with open('author_lang.json', encoding='utf-8') as f:
    author_lang = json.load(f)

with open('title_words_final.json', encoding='utf-8') as f:
    title_words = json.load(f)

# Supplementary verified established Bengali book titles
extra_books = {
    'Confessions (Rousseau)': 'কনফেশনস (রুশো)',
    'The Autobiography of Benjamin Franklin': 'দ্য অটোবায়োগ্রাফি অব বেঞ্জামিন ফ্র্যাঙ্কলিন',
    'Mein Kampf': 'মাইন কাম্পফ',
    'Long Walk to Freedom': 'লং ওয়াক টু ফ্রিডম',
    'Baburnama': 'বাবরনামা',
    'The Story of My Experiments with Truth': 'সত্যের সঙ্গে আমার প্রয়োগ',
    'The Diary of a Young Girl': 'একটি কিশোরীর ডায়েরি',
    'Wings of Fire (autobiography)': 'অগ্নিপক্ষ',
    'Wings of Fire': 'অগ্নিপক্ষ',
    'An Autobiography (Nehru)': 'অ্যান অটোবায়োগ্রাফি (নেহেরু)',
    'The Autobiography of an Unknown Indian': 'দি অটোবায়োগ্রাফি অব অ্যান আননোন ইন্ডিয়ান',
    'Jakhan Choto Chilam': 'যখন ছোট ছিলাম',
    'Autobiography of a Yogi': 'অটোবায়োগ্রাফি অব আ যোগী',
    'Dichtung und Wahrheit': 'ডিকটুং উন্ট ভারহাইট',
    'Childhood, Boyhood, and Youth': 'শৈশব, কৈশোর ও তারুণ্য',
    'A Confession': 'আ কনফেশন',
    'My Childhood': 'আমার ছেলেবেলা',
    'The Autobiography of Benvenuto Cellini': 'বেনভেনুতো চেল্লিনির আত্মজীবনী',
    'Histoire de ma vie': 'হিস্তোয়ার দ্য মা ভি',
    'Tuzk-e-Jahangiri': 'তুজুক-ই-জাহাঙ্গিরি',
    'Tuzuk-i-Jahangiri': 'তুজুক-ই-জাহাঙ্গিরি',
    'I Am Malala': 'আই অ্যাম মালালা',
    'Meditations': 'মেডিটেশনস',
    'Confessions (Augustine)': 'কনফেশনস (অগাস্টিন)',
    'The Words (book)': 'দ্য ওয়ার্ডস',
    'Memories, Dreams, Reflections': 'মেমোরিজ, ড্রিমস, রিফ্লেকশনস',
    'A Mathematician\'s Apology': 'আ ম্যাথমেটিশিয়ানস অ্যাপোলজি',
    'Surely You\'re Joking, Mr. Feynman!': 'সিওরলি ইউ আর জোকিং, মি. ফাইনম্যান!',
    'The Red Fighter Pilot': 'দ্য রেড ফাইটার পাইলট',
    'The Fun of It': 'দ্য ফান অব ইট',
    'Enemy Coast Ahead': 'এনিমি কোস্ট অ্যাহেড',
    'My Autobiography': 'মাই অটোবায়োগ্রাফি',
    'Personal Memoirs of Ulysses S. Grant': 'পার্সোনাল মেমোয়ার্স অব উইলিসিস এস. গ্রান্ট',
    'Panzer Leader (book)': 'প্যানজার লিডার',
    'The Autobiography of Charles Darwin': 'চার্লস ডারউইনের আত্মজীবনী',
    'Narrative of the Life of Frederick Douglass, an American Slave': 'ন্যারেটিভ অব দ্য লাইফ অব ফ্রেডেরিক ডগলাস',
    'Kashmir Udaas Hai': 'কাশ্মীর উদাস হ্যায়',
    'Hōjōki': 'হোজোকি',
    'The Pillow Book': 'দ্য পিলো বুক',
    'My Girlhood': 'আমার মেয়েবেলা',
    'Gusty Wind': 'উতাল হাওয়া',
    'Speak Up or Split Into Two': 'দ্বিখণ্ডিত',
    'Those Dark Days': 'সেইসব অন্ধকার',
    'I Am Not Fine, But You Stay Well My Beloved Country': 'আমি ভালো নেই তুমি ভালো থেকো প্রিয় দেশ',
    'Nothing Is There': 'নেই কিছু নেই',
    'Biographia Literaria': 'বায়োগ্রাফিয়া লিটারারিয়া',
    'Confessions of an English Opium-Eater': 'কনফেশনস অব অ্যান ইংলিশ ওপিয়াম-ইটার',
    'Historia Calamitatum': 'হিস্টোরিয়া কালামিতাতুম',
    'De Vita Propria': 'দে ভিতা প্রোপ্রিয়া',
    'Apologia Pro Vita Sua': 'অ্যাপোলজি প্রো ভাইটা সুয়া',
    'Memoria autógrafa': 'মেমোরিয়া অটোগ্রাফা',
    'Memorias': 'মেমোরিয়াস',
    'Praeterita': 'প্রিটেরিটা',
    'Memoirs of a Geisha': 'মেমোয়ার্স অব আ গেইশা',

    # Specific user-flagged titles & well-known titles
    "It's Not Easy Being Me: a Lifetime of No Respect But Plenty of Sex and Drugs": "ইটস নট ইজি বিয়িং মি: আ লাইফটাইম অব নো রেসপেক্ট বাট প্লেন্টি অব সেক্স অ্যান্ড ড্রাগস",
    "Hollywood Causes Cancer": "হলিউড কজেস ক্যানসার",
    "Cancer Schmancer": "ক্যানসার শ্ম্যান্সার",
    "Bigger than Hitler – Better than Christ": "বিগার দ্যান হিটলার – বেটার দ্যান ক্রাইস্ট",
    "The I Chong: Meditations From the Joint": "দ্য আই চং: মেডিটেশনস ফ্রম দ্য জয়েন্ট",
    "The Man Died: Prison Notes": "দ্য ম্যান ডায়েড: প্রিজন নোটস",
    "Clinging to the Wreckage: A Part of Life": "ক্লিঙিং টু দ্য রেকেজ: আ পার্ট অব লাইফ",
    "The Lives of a Bengal Lancer": "দ্য লাইভস অব আ বেঙ্গল ল্যান্সার",
    "The Lives of a Bengal Lancer (book)": "দ্য লাইভস অব আ বেঙ্গল ল্যান্সার",
    "Fighter Over Finland": "ফাইটার ওভার ফিনল্যান্ড",
    "Operation Overflight: The U-2 Spy Pilot Tells His Story for the First Time": "অপারেশন ওভারফ্লাইট: দ্য ইউ-২ স্পাই পাইলট টেলস হিজ স্টোরি ফর দ্য ফার্স্ট টাইম",
    "Aké: The Years of Childhood": "আকে: দ্য ইয়ার্স অব চাইল্ডহুড",
    "The Secret Life of Salvador Dalí": "দ্য সিক্রেট লাইফ অব সালভাদর দালি",
    "Lizzie Beautiful, The Lizzie Velásquez Story": "লিজি বিউটিফুল, দ্য লিজি ভেলাসকেস স্টোরি",
    "The Diary of Anaïs Nin": "দ্য ডায়েরি অব আনাইস নিন",
    "I Flew for the Führer": "আই ফ্লু ফর দ্য ফিউরার",
    "Baa Baa Black Sheep": "বা বা ব্ল্যাক শিপ",
    "Swastika in the Gunsight": "স্বস্তিকা ইন দ্য গানসাইট",
    "A Triangle Flies: The Development of Delta Aircraft Until 1945": "আ ট্রায়াঙ্গল ফ্লাইজ: দ্য ডেভেলপমেন্ট অব ডেল্টা এয়ারক্রাফট আনটিল ১৯৪৫",
    "War in a Stringbag": "ওয়ার ইন আ স্ট্রিংব্যাগ",
    "Testing the Spitfire": "টেস্টিং দ্য স্পিটফায়ার",
    "Sigh for a Merlin: Testing the Spitfire": "সাই ফর আ মার্লিন: টেস্টিং দ্য স্পিটফায়ার",
    "Spitfire: A Test Pilot's Story": "স্পিটফায়ার: আ টেস্ট পাইলটস স্টোরি",
    "Dustoff: The Memoir of an Army Aviator": "ডাস্টঅফ: দ্য মেমোয়ার অব অ্যান আর্মি অ্যাভিয়েটর",
    "Whistling Death: The Test Pilot's Story of the F4U Corsair": "হুইসলিং ডেথ: দ্য টেস্ট পাইলটস স্টোরি অব দ্য এফ৪ইউ করসেয়ার",
    "The Jolly Rogers: The Story of Tom Blackburn and Navy Fighting Squadron VF-17": "দ্য জলি রজার্স: দ্য স্টোরি অব টম ব্ল্যাকবার্ন অ্যান্ড নেভি ফাইটিং স্কোয়াড্রন ভিএফ-১৭",
    "A MiG-15 to Freedom: Memoir of the Wartime North Korean Defector Who First Delivered the Secret Fighter Jet to the Americans in 1953": "আ মিগ-১৫ টু ফ্রিডম: মেমোয়ার অব দ্য ওয়ারটাইম নর্থ কোরিয়ান ডিফেক্টর হু ফার্স্ট ডেলিভার্ড দ্য সিক্রেট ফাইটার জেট টু দ্য আমেরিকানস ইন ১৯৫৩",
    "Forever Flying: Fifty Years of High-flying Adventures, From Barnstorming in Prop Planes to Dogfighting Germans to Testing Supersonic Jets": "ফরএভার ফ্লাইং: ফিফটি ইয়ার্স অব হাই-ফ্লাইং অ্যাডভেঞ্চার্স, ফ্রম বার্নস্টর্মিং ইন প্রপ প্লেনস টু ডগফাইটিং জার্মানস টু টেস্টিং সুপারসনিক জেটস",
    "Moab Is My Washpot": "মোয়াব ইজ মাই ওয়াশপট",
    "Timebends: A Life": "টাইমবেন্ডস: আ লাইফ",
    "Trainwreck: My Life as an Idiot": "ট্রেনরেক: মাই লাইফ অ্যাজ অ্যান ইডিয়ট",
    "Rupert Red Two: A Fighter Pilot's Life from Thunderbolts to Thunderchiefs": "রুপার্ট রেড টু: আ ফাইটার পাইলটস লাইফ ফ্রম থান্ডারবোল্টস টু থান্ডারচিফস",
    "Moonwalk": "মুনওয়াক",
    "Moe Howard and the Three Stooges": "মো হাওয়ার্ড অ্যান্ড দ্য থ্রি স্টুজেস",
    "Moe Howard and the Three Stooges, AKA I Came, I Stooged, I Conquered": "মো হাওয়ার্ড অ্যান্ড দ্য থ্রি স্টুজেস, ওরফে আই কেম, আই স্টুজড, আই কনকার্ড",
    "Pryor Convictions": "প্রায়র কনভিকশনস",
    "Killing Willis, AKA Thatswhatimtalkinbout": "কিলিং উইলিস, ওরফে দ্যাটস হোয়াট আই অ্যাম টকিং অ্যাবাউট",
    "Dyn-o-mite!": "ডাইন-ও-মাইট!",
    "Rubber Balls & Liquor": "রাবার বলস অ্যান্ড লিকার",
    "Here Comes Trouble": "হিয়ার কামস ট্রাবল",
    "Is My Bow Too Big? How I Went from SNL to the Tea Party": "ইজ মাই বো টু বিগ? হাউ আই ওয়েন্ট ফ্রম এসএনএল টু দ্য টি পার্টি",
    "All About Me: My Remarkable Life In Show Business": "অল অ্যাবাউট মি: মাই রিমার্কেবল লাইফ ইন শো বিজনেস",
    "Ernie: The Autobiography": "আর্নি: দ্য অটোবায়োগ্রাফি",
    "Autobiography of Andrew Carnegie: with Illustrations": "অটোবায়োগ্রাফি অব অ্যান্ড্রু কার্নেগি: উইথ ইলাস্ট্রেশনস",
    "Failure Is Not an Option: Mission Control from Mercury to Apollo 13 and Beyond": "ফেইলিউর ইজ নট অ্যান অপশন: মিশন কন্ট্রোল ফ্রম মার্কারি টু অ্যাপোলো ১৩ অ্যান্ড বিয়ন্ড",
    "The Man Who Flew the Memphis Belle: Memoir of a WWII Bomber Pilot": "দ্য ম্যান হু ফ্লু দ্য মেমফিস বেল: মেমোয়ার অব আ দ্বিতীয় বিশ্বযুদ্ধ বোম্বার পাইলট",
    "Smell of Kerosene: A Test Pilot's Odyssey": "স্মেল অব কেরোসিন: আ টেস্ট পাইলটস ওডিসি",
    "747: Creating the World's First Jumbo Jet and Other Adventures from a Life in Aviation": "৭৪৭: ক্রিয়েটিং দ্য ওয়ার্ল্ডস ফার্স্ট জাম্বো জেট অ্যান্ড আদার অ্যাডভেঞ্চার্স ফ্রম আ লাইফ ইন অ্যাভিয়েশন",
    "Putting Dreams to Flight": "পুটিং ড্রিমস টু ফ্লাইট",
    "For That One Day: The Memoirs of Mitsuo Fuchida, the Commander of the Attack on Pearl Harbor": "ফর দ্যাট ওয়ান ডে: দ্য মেমোয়ার্স অব মিৎসুবো ফুচিদা, দ্য কমান্ডার অব দ্য অ্যাটাক অন পার্ল হারবার",
    "Never Call Me a Hero: A Legendary American Dive-Bomber Pilot Remembers the Battle of Midway": "নেভার কল মি আ হিরো: আ লেজেন্ডারি আমেরিকান ডাইভ-বোম্বার পাইলট রিমেম্বারস দ্য ব্যাটল অব মিডওয়ে",
    "Nerves of Steel: How I Followed My Dreams, Earned My Wings, and Faced My Greatest Challenge": "নার্ভস অব স্টিল: হাউ আই ফলোড মাই ড্রিমস, আর্নড মাই উইংস, অ্যান্ড ফেসড মাই গ্রেটেস্ট চ্যালেঞ্জ",
    "No Parachute: A Fighter Pilot in World War I": "নো প্যারাস্যুট: আ ফাইটার পাইলট ইন প্রথম বিশ্বযুদ্ধ",
    "Overview: A Lifelong Adventure in Aerial Photography": "ওভারভিউ: আ লাইফলং অ্যাডভেঞ্চার ইন অ্যারিয়াল ফটোগ্রাফি",
    "Wooing Peponi: My Odyssey through Many Years": "উয়িং পেপনি: মাই ওডিসি থ্রু মেনি ইয়ার্স",
    "From the Wright Brothers to the Astronauts: The Memoirs of Benjamin D. Foulois": "ফ্রম দ্য রাইট ব্রাদার্স টু দ্য অ্যাস্ট্রোনটস: দ্য মেমোয়ার্স অব বেঞ্জামিন ডি. ফু্যালোয়া",
    "Yeager: An Autobiography": "ইয়েগার: অ্যান অটোবায়োগ্রাফি",
    "The Strategic Air War Against Germany and Japan: A Memoir": "দ্য স্ট্র্যাটেজিক এয়ার ওয়ার অ্যাগেইনস্ট জার্মানি অ্যান্ড জাপান: আ মেমোয়ার",
    "Jackie Cochran: An Autobiography": "জ্যাকি ককরান: অ্যান অটোবায়োগ্রাফি",
    "C. W. A. Scott's Book: The Life and Mildenhall-Melbourne Flight of C.W.A. Scott": "সি. ডব্লিউ. এ. স্কটস বুক: দ্য লাইফ অ্যান্ড মিলডেনহল-মেলবোর্ন ফ্লাইট অব সি. ডব্লিউ. এ. স্কট",
    "The Story of the Winged-S": "দ্য স্টোরি অব দ্য উইংড-এস",
    "Way of a Fighter: The Memoirs of Claire Lee Chennault": "ওয়ে অব আ ফাইটার: দ্য মেমোয়ার্স অব ক্লেয়ার লি শেনল্ট",
    "General Kenney Reports: A Personal History of the Pacific War": "জেনারেল কেনি রিপোর্টস: আ পার্সোনাল হিস্ট্রি অব দ্য প্যাসিফিক ওয়ার",
    "Stormy Life": "স্টর্মি লাইফ",
    "Flying is My Life": "ফ্লাইং ইজ মাই লাইফ",
    "The Big Show": "দ্য বিগ শো",
    "Days Gone: Memories": "ডেস গন: মেমোরিজ",
    "A Wing and a Prayer: The \"Bloody 100th\" Bomb Group of the U.S. Eighth Air Force in Action over Europe in World War II": "আ উইং অ্যান্ড আ প্রেয়ার: দ্য \"ব্লাডি ১০০তম\" বোম গ্রুপ অব দ্য ইউ.এস. এইটথ এয়ার ফোর্স ইন অ্যাকশন ওভার ইউরোপ ইন দ্বিতীয় বিশ্বযুদ্ধ",
    "Call Me Pat: The Autobiography of the Man Howard Hughes Chose to Lead Hughes Aircraft": "কল মি প্যাট: দ্য অটোবায়োগ্রাফি অব দ্য ম্যান হাওয়ার্ড হিউজ চোজ টু লিড হিউজ এয়ারক্রাফট",
    "Spreading My Wings: One of Britain's Top Women Pilots Tells Her Remarkable Story": "স্প্রেডিং মাই উইংস: ওয়ান অব ব্রিটানস টপ উইমেন পাইলটস টেলস হার রিমার্কেবল স্টোরি",
    "From One Stripe to Four Stars": "ফ্রম ওয়ান স্ট্রাইপ টু ফোর স্টার্স",
    "The Years Flew Past: 40 Years at the Leading Edge of Aviation": "দ্য ইয়ার্স ফ্লু পাস্ট: ৪০ ইয়ার্স অ্যাট দ্য লিডিং এজ অব অ্যাভিয়েশন",
    "Flight Path: The Autobiography of Sir Peter Masefield": "ফ্লাইট পাথ: দ্য অটোবায়োগ্রাফি অব স্যার পিটার মেসফিল্ড",
    "Live Bait: WWII Memories of an Undefeated Fighter Ace": "লাইভ বেইট: দ্বিতীয় বিশ্বযুদ্ধ মেমোরিজ অব অ্যান আনডিফিটেড ফাইটার এস",
    "My Logbook: Reminiscences, 1938-2006": "মাই লগবুক: রেমিনিসেন্সেস, ১৯৩৮-২০০৬",
    "Red Sky, Black Death: A Soviet Woman Pilot's Memoir of the Eastern Front": "রেড স্কাই, ব্ল্যাক ডেথ: আ সোভিয়েত ওম্যান পাইলটস মেমোয়ার অব দ্য ইস্টার্ন ফ্রন্ট",
    "A WASP Among Eagles: A Woman Military Test Pilot in World War II": "আ ওয়াস্প অ্যামাং ঈগলস: আ ওম্যান মিলিটারি টেস্ট পাইলট ইন দ্বিতীয় বিশ্বযুদ্ধ",
    "Keep Your Airspeed Up: The Story of a Tuskegee Airman": "কিপ ইউর এয়ারস্পিড আপ: দ্য স্টোরি অব আ টাস্কাগি এয়ারম্যান",
    "Blackberry Winter: My Earlier Years": "ব্ল্যাকবেরি উইন্টার: মাই আর্লিয়ার ইয়ার্স",
    "My First Hundred Years with Ammu": "মাই ফার্স্ট হান্ড্রেড ইয়ার্স উইথ আম্মু",
    "Simply Rich: Life and Lessons from the Cofounder of Amway: A Memoir": "সিম্পলি রিচ: লাইফ অ্যান্ড লেসনস ফ্রম দ্য কোফাউন্ডার অব অ্যামওয়ে: আ মেমোয়ার",
    "A Memoir: Swimming Across": "আ মেমোয়ার: সুইমিং অ্যাক্রস",
    "The Custard Stops at Hatfield": "দ্য কাস্টার্ড স্টপস অ্যাট হ্যাটফিল্ড",
    "How Men Have Babies: a New Father's Survival Guide": "হাউ মেন হ্যাভ বেবিজ: আ নিউ ফাদারস সারভাইভাল গাইড",
    "I Shouldn't Even Be Doing This!": "আই শুডন্ট ইভেন বি ডুইং দিস!",
    "How to Raise Kids Who Won't Hate You": "হাউ টু রেইজ কিডস হু ওন্ট হেট ইউ",
    "Tough Sh*t: Life Advice from a Fat, Lazy Slob Who Still Made Good": "টাফ শিট: লাইফ অ্যাডভাইস ফ্রম আ ফ্যাট, লেজি স্লব হু স্টিল মেড গুড",
    "Only Fools and Stories": "অনলি ফুলস অ্যান্ড স্টোরিজ",
    "Cheech Is Not My Real Name...But Don't Call Me Chong!": "চিচ ইজ নট মাই রিয়েল নেম...বাট ডোন্ট কল মি চং!",
    "Always Look On the Bright Side Of Life": "অলওয়েজ লুক অন দ্য ব্রাইট সাইড অব লাইফ",
    "Random Acts of Badness": "র‍্যান্ডম অ্যাক্টস অব ব্যাডনেস",
    "BW: In Person and Here We Go Again: My Life In Television": "বিডব্লিউ: ইন পার্সন অ্যান্ড হিয়ার উই গো অ্যাগেইন: মাই লাইফ ইন টেলিভিশন",
    "Jen-X: My Open Book": "জেন-এক্স: মাই ওপেন বুক",
    "To the Is-land": "টু দ্য আইল্যান্ড",
    "Looking Back: A Chronicle of Growing Up Old in the Sixties": "লুকিং ব্যাক: আ ক্রনিকল অব গ্রোয়িং আপ ওল্ড ইন দ্য সিক্সটিজ",
    "The Godfather Papers & Other Confessions": "দ্য গডফাদার পেপার্স অ্যান্ড আদার কনফেশনস",
    "Mémoires pour servir à la vie de M. de Voltaire, écrits par lui-même": "মেমোয়ার্স পুর সের্ভির আ লা ভি দ্য এম. দ্য ভলতেয়ার, এক্রি পার লুই-মেম",
    "Mes Mémoires": "মে মেমোয়ার্স",
    "War Hentou an Tremened": "ওয়ার হেনতু আন ত্রেমেনেদ",
    "Mein Leben mit und für Max Reger": "মাইন লেবেন মিত উন্ড ফুর মাক্স রেগার",
    "Minha Formação": "মিনিয়া ফরমাসাঁও",
    "Mémoires d'Outre-Tombe": "মেমোয়ার্স দোত্র-তোম্ব",
    "Meine neue Freiheit. Von Kabul über den Laufsteg zu mir selbst": "মাইন নয়ে ফ্রাইহাইট: ফন কাবুল উবার ডেন লাউফস্টেগ সু মির সেলবস্ট",
}

for k, v in extra_books.items():
    book_bn[k] = v

# CMU Dictionary
cmu = {}
if os.path.exists('cmudict.dict'):
    with open('cmudict.dict', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';'):
                continue
            parts = line.split()
            word = parts[0].split('(')[0].lower()
            if word not in cmu:
                cmu[word] = parts[1:]

VOWELS = {'AA', 'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

C_MAP = {
    'B': 'ব', 'CH': 'চ', 'D': 'ড', 'DH': 'দ', 'F': 'ফ', 'G': 'গ', 'HH': 'হ',
    'JH': 'জ', 'K': 'ক', 'L': 'ল', 'M': 'ম', 'N': 'ন', 'NG': 'ং', 'P': 'প',
    'R': 'র', 'S': 'স', 'SH': 'শ', 'T': 'ট', 'TH': 'থ', 'V': 'ভ', 'W': 'উ',
    'Y': 'য়', 'Z': 'জ', 'ZH': 'ঝ'
}

V_INIT = {
    'AA': 'আ', 'AE': 'অ্যা', 'AH': 'আ', 'AO': 'অ', 'AW': 'আউ', 'AY': 'আই',
    'EH': 'এ', 'ER': 'আর', 'EY': 'এ', 'IH': 'ই', 'IY': 'ই', 'OW': 'ও',
    'OY': 'অয়', 'UH': 'উ', 'UW': 'উ'
}

V_SIGN = {
    'AA': 'া', 'AE': '্যা', 'AH': 'া', 'AO': 'ো', 'AW': 'াউ', 'AY': 'াই',
    'EH': 'ে', 'ER': 'ার', 'EY': 'ে', 'IH': 'ি', 'IY': 'ি', 'OW': 'ো',
    'OY': 'য়', 'UH': 'ু', 'UW': 'ু'
}

TRIPLE_CONJUNCTS = {
    ('S', 'T', 'R'): 'স্ট্র',
    ('S', 'P', 'R'): 'স্প্র',
    ('S', 'K', 'R'): 'স্ক্র',
    ('K', 'S', 'T'): 'ক্সট',
}

CONJUNCTS = {
    ('S', 'P'): 'স্প', ('S', 'T'): 'স্ট', ('S', 'K'): 'স্ক', ('S', 'M'): 'স্ম',
    ('S', 'N'): 'স্ন', ('S', 'L'): 'স্ল',
    ('K', 'R'): 'ক্র', ('K', 'L'): 'ক্ল',
    ('P', 'R'): 'প্র', ('P', 'L'): 'প্ল',
    ('B', 'R'): 'ব্র', ('B', 'L'): 'ব্ল',
    ('G', 'R'): 'গ্র', ('G', 'L'): 'গ্ল',
    ('T', 'R'): 'ট্র', ('D', 'R'): 'ড্র',
    ('F', 'R'): 'ফ্র', ('F', 'L'): 'ফ্ল',
    ('N', 'D'): 'ন্ড', ('N', 'T'): 'ন্ট', ('N', 'S'): 'ন্স', ('N', 'JH'): 'ঞ্জ',
    ('L', 'D'): 'ল্ড', ('L', 'T'): 'ল্ট', ('L', 'M'): 'ল্ম',
    ('K', 'T'): 'ক্ট', ('P', 'T'): 'প্ট', ('F', 'T'): 'ফ্ট'
}

def is_v(p):
    return re.sub(r'\\d', '', p) in VOWELS

def get_v(p):
    return re.sub(r'\\d', '', p)

def arpabet_to_bn(phonemes):
    n = len(phonemes)
    res = ''
    i = 0
    while i < n:
        p = phonemes[i]
        base_p = re.sub(r'\\d', '', p)
        
        # Word-final Z -> স (English plural/possessive/verb -s)
        if base_p == 'Z' and i == n - 1:
            res += 'স'
            i += 1
            continue

        # Common English suffixes
        # -tion(s) / -sion(s): SH AH N (Z) -> শন / শনস
        if base_p == 'SH':
            if i + 2 < n and get_v(phonemes[i+1]) in ['AH', 'IH'] and re.sub(r'\\d', '', phonemes[i+2]) == 'N':
                if i + 3 < n and re.sub(r'\\d', '', phonemes[i+3]) in ['Z', 'S'] and i + 3 == n - 1:
                    res += 'শনস'
                    i += 4
                    continue
                elif i + 2 == n - 1:
                    res += 'শন'
                    i += 3
                    continue
        
        # -ment(s): M AH N T (S) -> মেন্ট / মেন্টস
        if base_p == 'M':
            if i + 3 < n and get_v(phonemes[i+1]) in ['AH', 'IH'] and re.sub(r'\\d', '', phonemes[i+2]) == 'N' and re.sub(r'\\d', '', phonemes[i+3]) == 'T':
                if i + 4 < n and re.sub(r'\\d', '', phonemes[i+4]) in ['S', 'Z'] and i + 4 == n - 1:
                    res += 'মেন্টস'
                    i += 5
                    continue
                elif i + 3 == n - 1:
                    res += 'মেন্ট'
                    i += 4
                    continue

        if is_v(p):
            v = get_v(p)
            if i == 0 or is_v(phonemes[i-1]):
                res += V_INIT.get(v, '')
            else:
                res += V_SIGN.get(v, '')
            i += 1
        else:
            # Check 3-consonant cluster first
            if i + 2 < n and not is_v(phonemes[i+1]) and not is_v(phonemes[i+2]):
                c2 = re.sub(r'\\d', '', phonemes[i+1])
                c3 = re.sub(r'\\d', '', phonemes[i+2])
                triple = (base_p, c2, c3)
                if triple in TRIPLE_CONJUNCTS:
                    conj = TRIPLE_CONJUNCTS[triple]
                    if i + 3 < n and is_v(phonemes[i+3]):
                        v_next = get_v(phonemes[i+3])
                        res += conj + V_SIGN.get(v_next, '')
                        i += 4
                        continue
                    else:
                        res += conj
                        i += 3
                        continue

            # Check 2-consonant cluster
            if i + 1 < n and not is_v(phonemes[i+1]):
                c2 = re.sub(r'\\d', '', phonemes[i+1])
                pair = (base_p, c2)
                if pair in CONJUNCTS:
                    conj = CONJUNCTS[pair]
                    if i + 2 < n and is_v(phonemes[i+2]):
                        v_next = get_v(phonemes[i+2])
                        res += conj + V_SIGN.get(v_next, '')
                        i += 3
                        continue
                    else:
                        res += conj
                        i += 2
                        continue
            
            # Reph: R before consonant
            if base_p == 'R' and i + 1 < n and not is_v(phonemes[i+1]):
                c2 = re.sub(r'\\d', '', phonemes[i+1])
                res += 'র্' + C_MAP.get(c2, '')
                i += 2
                continue
                
            # NG before vowel -> ঙ্গ, else ং
            if base_p == 'NG':
                if i + 1 < n and is_v(phonemes[i+1]):
                    v_next = get_v(phonemes[i+1])
                    res += 'ঙ্গ' + V_SIGN.get(v_next, '')
                    i += 2
                else:
                    res += 'ং'
                    i += 1
                continue
                
            # W before vowel
            if base_p == 'W' and i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += 'ওয়া' if v_next in ['AA', 'AE', 'AH'] else ('ওয়ে' if v_next in ['EH', 'EY'] else 'উই')
                i += 2
                continue
                
            c_char = C_MAP.get(base_p, '')
            if i + 1 < n and is_v(phonemes[i+1]):
                v_next = get_v(phonemes[i+1])
                res += c_char + V_SIGN.get(v_next, '')
                i += 2
            else:
                res += c_char
                i += 1
    return res

INITIALS = {
    'A.': 'এ.', 'B.': 'বি.', 'C.': 'সি.', 'D.': 'ডি.', 'E.': 'ই.', 'F.': 'এফ.',
    'G.': 'জি.', 'H.': 'এইচ.', 'I.': 'আই.', 'J.': 'জে.', 'K.': 'কে.', 'L.': 'এল.',
    'M.': 'এম.', 'N.': 'এন.', 'O.': 'ও.', 'P.': 'পি.', 'Q.': 'কিউ.', 'R.': 'আর.',
    'S.': 'এস.', 'T.': 'টি.', 'U.': 'ইউ.', 'V.': 'ভি.', 'W.': 'ডব্লিউ.', 'X.': 'এক্স.',
    'Y.': 'ওয়াই.', 'Z.': 'জেড.',
    'A': 'এ.', 'B': 'বি.', 'C': 'সি.', 'D': 'ডি.', 'E': 'ই.', 'F': 'এফ.',
    'G': 'জি.', 'H': 'এইচ.', 'I': 'আই.', 'J': 'জে.', 'K': 'কে.', 'L': 'এল.',
    'M': 'এম.', 'N': 'এন.', 'O': 'ও.', 'P': 'পি.', 'Q': 'কিউ.', 'R': 'আর.',
    'S': 'এস.', 'T': 'টি.', 'U': 'ইউ.', 'V': 'ভি.', 'W': 'ডব্লিউ.', 'X': 'এক্স.',
    'Y': 'ওয়াই.', 'Z': 'জেড.'
}

def transliterate_rule_based(w):
    low = w.lower()
    if low.startswith('ts'):
        return 'সু' + transliterate_rule_based(w[2:])
    if low.startswith('z'):
        return 'স' + transliterate_rule_based(w[1:])
    if low.startswith('wr'):
        return 'র' + transliterate_rule_based(w[2:])
    if low.startswith('kn'):
        return 'ন' + transliterate_rule_based(w[2:])
    if low.startswith('ps'):
        return 'স' + transliterate_rule_based(w[2:])
        
    mapping = [
        ('tion', 'শন'), ('sion', 'শন'), ('tch', 'চ'), ('ch', 'চ'),
        ('sh', 'শ'), ('ph', 'ফ'), ('th', 'থ'), ('wh', 'হোয়'),
        ('ck', 'ক'), ('qu', 'ক্ব'), ('gh', 'ঘ'), ('kh', 'খ'),
        ('igh', 'আই'), ('ee', 'ি'), ('oo', 'ু'), ('ea', 'ি'),
        ('ai', 'াই'), ('ay', 'ে'), ('ey', 'ি'), ('oy', 'য়'),
        ('oi', 'য়'), ('ou', 'াউ'), ('au', 'অ'), ('aw', 'অ'),
        ('cl', 'ক্ল'), ('cr', 'ক্র'), ('pl', 'প্ল'), ('pr', 'প্র'),
        ('bl', 'ব্ল'), ('br', 'ব্র'), ('gl', 'গ্ল'), ('gr', 'গ্র'),
        ('fl', 'ফ্ল'), ('fr', 'ফ্র'), ('tr', 'ট্র'), ('dr', 'ড্র'),
        ('sp', 'স্প'), ('st', 'স্ট'), ('sk', 'স্ক'), ('sm', 'স্ম'),
        ('sn', 'স্ন'), ('sl', 'স্ল'),
        ('b', 'ব'), ('c', 'ক'), ('d', 'ড'), ('f', 'ফ'),
        ('g', 'গ'), ('h', 'হ'), ('j', 'জ'), ('k', 'ক'),
        ('l', 'ল'), ('m', 'ম'), ('n', 'ন'), ('p', 'প'),
        ('q', 'ক'), ('r', 'র'), ('s', 'স'), ('t', 'ট'),
        ('v', 'ভ'), ('w', 'উ'), ('x', 'ক্স'), ('y', 'য়'),
        ('z', 'জ'), ('a', 'া'), ('e', 'ে'), ('i', 'ি'),
        ('o', 'ো'), ('u', 'ু')
    ]
    res = ''
    i = 0
    while i < len(low):
        matched = False
        for pat, rep in mapping:
            if low[i:i+len(pat)] == pat:
                res += rep
                i += len(pat)
                matched = True
                break
        if not matched:
            res += low[i]
            i += 1
            
    vowel_initial = {
        'া': 'আ', 'ে': 'এ', 'ি': 'ই', 'ী': 'ঈ', 'ু': 'উ', 'ূ': 'ঊ', 'ো': 'ও', 'ৌ': 'ঔ', 'ৈ': 'ঐ'
    }
    if res and res[0] in vowel_initial:
        res = vowel_initial[res[0]] + res[1:]
    return res

def transliterate_title_word(w):
    if not w:
        return ''
    w_clean = w.strip()
    low = w_clean.lower()
    
    if low in title_words:
        return title_words[low]
        
    if w_clean in INITIALS:
        return INITIALS[w_clean]
        
    if re.match(r'^\\d+$', w_clean):
        digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
        return ''.join(digits.get(d, d) for d in w_clean)
        
    if low.endswith("'s"):
        root = low[:-2]
        if root in title_words:
            return title_words[root] + 'স'
        if root in cmu:
            return arpabet_to_bn(cmu[root]) + 'স'
            
    if low in cmu:
        return arpabet_to_bn(cmu[low])
        
    return transliterate_rule_based(w_clean)

def fix_consecutive_vowels(s):
    s = re.sub(r'\\bWWII\\b', 'দ্বিতীয় বিশ্বযুদ্ধ', s, flags=re.I)
    s = re.sub(r'\\bWorld War II\\b', 'দ্বিতীয় বিশ্বযুদ্ধ', s, flags=re.I)
    s = re.sub(r'\\bWW1\\b', 'প্রথম বিশ্বযুদ্ধ', s, flags=re.I)
    s = re.sub(r'\\bWorld War I\\b', 'প্রথম বিশ্বযুদ্ধ', s, flags=re.I)
    s = re.sub(r'িে', 'িয়ে', s)
    s = re.sub(r'িা', 'িয়া', s)
    s = re.sub(r'িো', 'িও', s)
    s = re.sub(r'িু', 'িউ', s)
    s = re.sub(r'ুো', 'ুও', s)
    s = re.sub(r'ুা', 'ুয়া', s)
    s = re.sub(r'ুি', 'ুই', s)
    s = re.sub(r'াে', 'ায়ে', s)
    s = re.sub(r'োা', 'োয়া', s)
    s = re.sub(r'েো', 'েও', s)
    s = re.sub(r'িি', 'ি', s)
    s = re.sub(r'\\.\\.+', '.', s)  # fix double dots like সি.. ডব্লিউ..
    return s

def transliterate_title_phrase(phrase):
    phrase = re.sub(r'\\bU-2\\b', 'ইউ-২', phrase)
    phrase = re.sub(r'\\bWWII\\b', 'দ্বিতীয় বিশ্বযুদ্ধ', phrase)
    phrase = re.sub(r'\\bWorld War II\\b', 'দ্বিতীয় বিশ্বযুদ্ধ', phrase)
    phrase = re.sub(r'\\bWWI\\b', 'প্রথম বিশ্বযুদ্ধ', phrase)
    phrase = re.sub(r'\\bWorld War I\\b', 'প্রথম বিশ্বযুদ্ধ', phrase)
    phrase = re.sub(r'\\bF4U\\b', 'এফ৪ইউ', phrase)
    phrase = re.sub(r'\\bVF-17\\b', 'ভিএফ-১৭', phrase)
    phrase = re.sub(r'\\bMiG-15\\b', 'মিগ-১৫', phrase, flags=re.I)
    phrase = re.sub(r'\\b100th\\b', '১০০তম', phrase)
    phrase = re.sub(r'\\bA-Train\\b', 'এ-ট্রেন', phrase)
    phrase = re.sub(r'\\bAKA\\b', 'ওরফে', phrase)
    phrase = re.sub(r'\\bBW\\b', 'বিডব্লিউ', phrase)
    phrase = re.sub(r'\\bSNL\\b', 'এসএনএল', phrase)
    phrase = re.sub(r'\\bU\\.S\\.\\b', 'ইউ.এস.', phrase)
    phrase = re.sub(r'C\\.\\s*W\\.\\s*A\\.', 'সি. ডব্লিউ. এ.', phrase)

    tokens = re.split(r'(\\s+|[.,:;!?\\(\\)\\"–—]|(?<!\\w)\\'|\\'(?!\\w))', phrase)
    out = []
    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,:;!?\\(\\)\\"–—\\']+$', t):
            out.append(t)
        else:
            out.append(transliterate_title_word(t))
    res = ''.join(out)
    return fix_consecutive_vowels(res)

def format_author(author_raw):
    m = re.search(r'\\[\\[([^\\]\\|]+)(?:\\|([^\\]]+))?\\]\\]', author_raw)
    if m:
        target = m.group(1).strip()
        disp = m.group(2).strip() if m.group(2) else target
        clean_target = re.sub(r'\\s*\\([^)]*\\)', '', target).strip()
        clean_disp = re.sub(r'\\s*\\([^)]*\\)', '', disp).strip()
        
        bn_name = None
        for k in [target, clean_target, disp, clean_disp]:
            if k in author_bn:
                bn_name = author_bn[k]
                break
        if not bn_name:
            bn_name = transliterate_title_phrase(clean_disp)
            
        if target == bn_name:
            return f"[[{bn_name}]]"
        if re.search(r'[\\u0980-\\u09FF]', target):
            return f"[[{target}]]" if target == bn_name else f"[[{target}|{bn_name}]]"
        return f"[[{target}|{bn_name}]]"
    else:
        clean = re.sub(r'\\[\\[|\\]\\]', '', author_raw).strip()
        clean_disp = re.sub(r'\\s*\\([^)]*\\)', '', clean).strip()
        if clean in author_bn:
            return author_bn[clean]
        if clean_disp in author_bn:
            return author_bn[clean_disp]
        return transliterate_title_phrase(clean_disp)

def format_titles(title_raw):
    # Cleanly isolate notes
    efn_pos = title_raw.find('{{efn')
    ref_pos = title_raw.find('<ref')
    cut_pos = -1
    if efn_pos != -1 and ref_pos != -1:
        cut_pos = min(efn_pos, ref_pos)
    elif efn_pos != -1:
        cut_pos = efn_pos
    elif ref_pos != -1:
        cut_pos = ref_pos

    if cut_pos != -1:
        title_core = title_raw[:cut_pos].strip()
        notes = title_raw[cut_pos:].strip()
    else:
        title_core = title_raw.strip()
        notes = ''

    clean_no_italics = re.sub(r"''", "", title_core).strip()

    m_b = re.search(r'\\[\\[([^\\]\\|]+)(?:\\|([^\\]]+))?\\]\\]', clean_no_italics)
    has_link = bool(m_b)
    link_target = m_b.group(1).strip() if m_b else ''
    link_disp = m_b.group(2).strip() if (m_b and m_b.group(2)) else link_target
    clean_target = re.sub(r'\\s*\\([^)]*\\)', '', link_target).strip()

    pure_text = re.sub(r'\\[\\[|\\]\\]', '', clean_no_italics).strip()
    m_paren = re.search(r"^(.+?)\\s*\\((.+?)\\)$", pure_text)

    # Check established conventional Bengali title
    known_bn = None
    if has_link:
        if link_target in book_bn:
            known_bn = book_bn[link_target]
        elif clean_target in book_bn:
            known_bn = book_bn[clean_target]
        elif link_disp in book_bn:
            known_bn = book_bn[link_disp]
    if not known_bn:
        if pure_text in book_bn:
            known_bn = book_bn[pure_text]
        elif m_paren and m_paren.group(1).strip() in book_bn:
            known_bn = book_bn[m_paren.group(1).strip()]

    # 1. Bengali title column
    if known_bn:
        if has_link:
            bn_title = f"''[[{known_bn}]]''" if link_target == known_bn else f"''[[{link_target}|{known_bn}]]''"
        else:
            bn_title = f"''{known_bn}''"
    else:
        if m_paren:
            main_part = m_paren.group(1).strip()
            m_main_link = re.search(r'\\[\\[([^\\]\\|]+)(?:\\|([^\\]]+))?\\]\\]', main_part)
            if m_main_link:
                t_target = m_main_link.group(1).strip()
                t_disp = m_main_link.group(2).strip() if m_main_link.group(2) else t_target
                trans_bn = transliterate_title_phrase(t_disp)
                bn_title = f"''[[{t_target}|{trans_bn}]]''"
            else:
                trans_bn = transliterate_title_phrase(main_part)
                if has_link:
                    bn_title = f"''[[{link_target}|{trans_bn}]]''"
                else:
                    bn_title = f"''{trans_bn}''"
        elif has_link:
            trans_bn = transliterate_title_phrase(link_disp)
            bn_title = f"''[[{link_target}|{trans_bn}]]''"
        else:
            trans_bn = transliterate_title_phrase(pure_text)
            bn_title = f"''{trans_bn}''"

    # 2. Roman/Original title column
    if m_paren:
        eng_part = m_paren.group(1).strip()
        orig_part = m_paren.group(2).strip()
        
        if 'published posthumously' in orig_part.lower():
            if has_link:
                if link_target == link_disp:
                    roman_title = f"''[[{link_target}]]'' ({orig_part})"
                else:
                    roman_title = f"''[[{link_target}|{link_disp}]]'' ({orig_part})"
            else:
                roman_title = f"''{eng_part}'' ({orig_part})"
        else:
            if has_link:
                roman_title = f"''[[{link_target}|{eng_part}]]'' (''{orig_part}'')"
            else:
                roman_title = f"''{eng_part}'' (''{orig_part}'')"
    else:
        if has_link:
            if link_target == link_disp:
                roman_title = f"''[[{link_target}]]''"
            else:
                roman_title = f"''[[{link_target}|{link_disp}]]''"
        else:
            roman_title = f"''{pure_text}''"

    if notes:
        bn_title += notes
        roman_title += notes

    return bn_title, roman_title

def to_bn_num(s):
    digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
    return ''.join(digits.get(c, c) for c in s)

def get_language(author_raw, title_raw):
    m_a = re.search(r'\\[\\[([^\\]\\|]+)(?:\\|([^\\]]+))?\\]\\]', author_raw)
    target_a = m_a.group(1).strip() if m_a else author_raw.strip()
    clean_target_a = re.sub(r'\\s*\\([^)]*\\)', '', target_a).strip()
    
    m_t = re.search(r'\\[\\[([^\\]\\|]+)(?:\\|([^\\]]+))?\\]\\]', title_raw)
    target_t = m_t.group(1).strip() if m_t else title_raw.strip()
    clean_target_t = re.sub(r'\\s*\\([^)]*\\)', '', target_t).strip()
    
    # 1. Book specific
    for k in [target_t, clean_target_t]:
        if k in book_lang:
            return book_lang[k]
            
    # 2. Author specific
    for k in [target_a, clean_target_a]:
        if k in author_lang:
            return author_lang[k]
            
    # Fallback to English
    return 'ইংরেজি'

# Read raw file and translate
with open('List_of_autobiographies_raw.txt', encoding='utf-8') as f:
    raw_lines = f.readlines()

output_lines = [
    '{{ছোট বিবরণ নেই}}',
    '\'\'\'আত্মজীবনীর তালিকা\'\'\' হলো বিশিষ্ট ব্যক্তিবর্গের রচিত ও প্রকাশিত গুরুত্বপূর্ণ [[আত্মজীবনী]] ও স্মৃতিকথামূলক গ্রন্থের একটি সংকলন।',
    '',
    '{| class="wikitable sortable"',
    '! লেখক !! বাংলা শিরোনাম !! মূল/রোমান শিরোনাম !! মূল ভাষা !! প্রকাশনার বছর'
]

total_translated = 0
i = 0
n_lines = len(raw_lines)

while i < n_lines:
    line = raw_lines[i].strip()
    if not line:
        i += 1
        continue
    if line.startswith('|-'):
        i += 1
        continue
    if line.startswith('|') and not line.startswith('|}'):
        if i + 2 < n_lines and not ('||' in line):
            l1 = line.strip()
            l2 = raw_lines[i+1].strip()
            l3 = raw_lines[i+2].strip()
            if l1.startswith('|') and l2.startswith('|') and l3.startswith('|') and not l2.startswith('|-') and not l3.startswith('|-'):
                auth_raw = l1.lstrip('|').strip()
                tit_raw = l2.lstrip('|').strip()
                yr_raw = l3.lstrip('|').strip()
                
                auth_bn = format_author(auth_raw)
                tit_bn, tit_ro = format_titles(tit_raw)
                lang_bn = get_language(auth_raw, tit_raw)
                
                efn_pos = yr_raw.find('{{efn')
                ref_pos = yr_raw.find('<ref')
                cut_pos = -1
                if efn_pos != -1 and ref_pos != -1:
                    cut_pos = min(efn_pos, ref_pos)
                elif efn_pos != -1:
                    cut_pos = efn_pos
                elif ref_pos != -1:
                    cut_pos = ref_pos

                if cut_pos != -1:
                    yr_clean = yr_raw[:cut_pos].strip()
                    yr_note = yr_raw[cut_pos:].strip()
                else:
                    yr_clean = yr_raw.strip()
                    yr_note = ''
                
                yr_bn = f"{to_bn_num(yr_clean)}{yr_note}"
                
                output_lines.append('|-')
                output_lines.append(f'|{auth_bn} ||{tit_bn} ||{tit_ro} ||{lang_bn} ||{yr_bn}')
                total_translated += 1
                i += 3
                continue
        
        parts = [p.strip() for p in line.lstrip('|').split('||')]
        parts = [p.lstrip('|').strip() for p in parts if p.lstrip('|').strip() != '']
        if len(parts) >= 2:
            auth_raw = parts[0]
            tit_raw = parts[1].lstrip('|').strip()
            yr_raw = parts[2].lstrip('|').strip() if len(parts) >= 3 else '&nbsp;'
            
            auth_bn = format_author(auth_raw)
            tit_bn, tit_ro = format_titles(tit_raw)
            lang_bn = get_language(auth_raw, tit_raw)
            
            # Check note in year
            efn_pos = yr_raw.find('{{efn')
            ref_pos = yr_raw.find('<ref')
            cut_pos = -1
            if efn_pos != -1 and ref_pos != -1:
                cut_pos = min(efn_pos, ref_pos)
            elif efn_pos != -1:
                cut_pos = efn_pos
            elif ref_pos != -1:
                cut_pos = ref_pos

            if cut_pos != -1:
                yr_clean = yr_raw[:cut_pos].strip()
                yr_note = yr_raw[cut_pos:].strip()
            else:
                yr_clean = yr_raw.strip()
                yr_note = ''
            
            yr_bn = f"{to_bn_num(yr_clean)}{yr_note}"
            
            output_lines.append('|-')
            output_lines.append(f'|{auth_bn} ||{tit_bn} ||{tit_ro} ||{lang_bn} ||{yr_bn}')
            total_translated += 1
    i += 1

output_lines.append('|}')
output_lines.append('')
output_lines.append('== আরও দেখুন ==')
output_lines.append('* [[বইয়ের তালিকা]]')
output_lines.append('')
output_lines.append('== তথ্যসূত্র ==')
output_lines.append('=== পাদটীকা ===')
output_lines.append('{{Notelist}}')
output_lines.append('')
output_lines.append('=== নোট ===')
output_lines.append('{{সূত্র তালিকা}}')
output_lines.append('')
output_lines.append('{{DEFAULTSORT:আত্মজীবনীর তালিকা}}')
output_lines.append('[[বিষয়শ্রেণী:আত্মজীবনী|*]]')
output_lines.append('[[বিষয়শ্রেণী:বইয়ের তালিকা]]')
output_lines.append('[[বিষয়শ্রেণী:অ-কাল্পনিক বইয়ের তালিকা]]')

final_text = '\\n'.join(output_lines)
with open('আত্মজীবনীর তালিকা (বাংলা).txt', 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f'Successfully generated আত্মজীবনীর তালিকা (বাংলা).txt with 5 columns and {total_translated} entries!')
'''

with open('generate_final.py', 'w', encoding='utf-8') as f:
    f.write(new_code)
print('Successfully overwritten generate_final.py with robust transliteration engine!')
