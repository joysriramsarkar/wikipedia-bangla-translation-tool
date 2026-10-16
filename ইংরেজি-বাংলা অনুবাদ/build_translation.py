# -*- coding: utf-8 -*-
import json
import re
import os

# 1. Load verified caches
with open('author_bn_map.json', encoding='utf-8') as f:
    author_bn = json.load(f)

with open('book_bn_map.json', encoding='utf-8') as f:
    book_bn = json.load(f)

with open('book_lang.json', encoding='utf-8') as f:
    book_lang = json.load(f)

with open('author_lang.json', encoding='utf-8') as f:
    author_lang = json.load(f)

# Supplementary verified author translations
extra_authors = {
    'Manfred von Richthofen': 'ম্যানফ্রেড ফন রিখথোফেন',
    'Billy Bishop': 'বিলি বিশপ',
    'James McCudden': 'জেমস ম্যাককাডেন',
    'René Fonck': 'রনে ফঙ্ক',
    'Richard E. Byrd': 'রিচার্ড ই. বার্ড',
    'Clarence Chamberlin': 'ক্ল্যারেন্স চেম্বারলিন',
    'Frank Hawks': 'ফ্র্যাঙ্ক হকস',
    'Willy Coppens': 'উইলি কপেনস',
    'Duncan Grinnell-Milne': 'ডানকান গ্রিনেল-মিলনে',
    'C. W. A. Scott': 'সি. ডব্লিউ. এ. স্কট',
    'Beirne Lay Jr.': 'বার্ন লে জুনিয়র',
    'Frank Glasgow Tinker': 'ফ্র্যাঙ্ক গ্লাসগো টিঙ্কার',
    'Louise Thaden': 'লুইস থাডেন',
    'Igor Sikorsky': 'ইগর সিকোরস্কি',
    'Richard Hillary': 'রিচার্ড হিলারি',
    'Beryl Markham': 'বেরিল মারখাম',
    'Ted W. Lawson': 'টেড ডব্লিউ. লসন',
    'Don S. Gentile': 'ডন এস. জেনটাইল',
    'Guy Gibson': 'গাই গিবসন',
    'Sir Arthur Harris, 1st Baronet': 'স্যার আর্থার হ্যারিস',
    'Arthur Harris': 'আর্থার হ্যারিস',
    'Bert Stiles': 'বার্ট স্টাইলস',
    'Henry H. Arnold': 'হেনরি এইচ. আর্নল্ড',
    'Claire Lee Chennault': 'ক্লেয়ার লি শেনল্ট',
    'George Kenney': 'জর্জ কেনি',
    'Ivan Kozhedub': 'ইভান কোঝেদুব',
    'Hans-Ulrich Rudel': 'হান্স-উলরিখ রুডেল',
    'Dick Grace': 'ডিক গ্রেস',
    'William Bushnell Stout': 'উইলিয়াম বুশনেল স্টাউট',
    'Pierre Clostermann': 'পিয়ের ক্লোস্তেরমান',
    'Hanna Reitsch': 'হানা রাইচ',
    'Adolf Galland': 'এডলফ গ্যালান্ড',
    'Ernst Heinkel': 'আর্নস্ট হাইঙ্কেল',
    'Heinz Knoke': 'হাইনৎস ক্নোকে',
    'Nevil Shute': 'নেভিল শুট',
    'Bill Bridgeman': 'বিল ব্রিজম্যান',
    'Eino Luukkanen': 'এইনো লুক্কানেন',
    'Johnnie Johnson': 'জনি জনসন',
    'John Slessor': 'জন স্লেসর',
    'Basil Embry': 'ব্যাসিল এমব্রি',
    'Saburō Sakai': 'সাবুরো সাকাই',
    'Pappy Boyington': 'প্যাপি বোয়িংটন',
    'Robert S. Johnson': 'রবার্ট এস. জনসন',
    'Alexander Sergeyevich Yakovlev': 'আলেকসান্দর সের্গেইয়েভিচ ইয়াকোভলেভ',
    'Igor Kaberov': 'ইগর কাবেরভ',
    'Alexander Lippisch': 'আলেকজান্ডার লিপিশ',
    'Alberto Briganti': 'আলবের্তো ব্রিগান্তি',
    'Takeo Doi': 'তাকেয়ো দোই',
    'Margaret Mead': 'মার্গারেট মিড',
    'Margaret Murray': 'মার্গারেট মারি',
    'Frank Lloyd Wright': 'ফ্র্যাঙ্ক লয়েড রাইট',
    'Salvador Dalí': 'সালভাদোর দালি',
    'Claude Monet': 'ক্লোদ মোনে',
    'Gwen Raverat': 'গোয়েন রাভেরাত',
    'Andrew Carnegie': 'অ্যান্ড্রু কার্নেগি',
    'Henry Ford': 'হেনরি ফোর্ড',
    'Richard DeVos': 'রিচার্ড ডিভোস',
    'Terry-Thomas': 'টেরি-টমাস',
    'Harpo Marx': 'হার্পো মার্ক্স',
    'Charlie Chaplin': 'চার্লি চ্যাপলিন',
    'Isadora Duncan': 'ইসাডোরা ডানকান',
    'Vincent Price': 'ভিনসেন্ট প্রাইস',
    'Fred Astaire': 'ফ্রেড অ্যাস্টেয়ার',
    'Ken Murray': 'কেন মারি',
    'Edward Gibbon': 'এডওয়ার্ড গিবন',
    'Henry Adams': 'হেনরি অ্যাডামস',
    'Martin Latham': 'মার্টিন ল্যাথাম',
    'Mehmood Hashmi': 'মেহমুদ হাশমি',
    'Libanius': 'লিবানিয়াস',
    'Sei Shōnagon': 'সেই শোনাতন',
    'Kamo No Chomei': 'কামো নো চোমেই',
    'G. H. Hardy': 'জি. এইচ. হার্ডি',
    'Norbert Wiener': 'নরবার্ট উইনার',
    'Bertrand Russell': 'বারট্রান্ড রাসেল',
    'Albert Schweitzer': 'আলবার্ট শোয়েইৎজার',
    'Sydney Smith': 'সিডনি স্মিথ',
    'Ulysses S. Grant': 'উইলিসিস এস. গ্রান্ট',
    'Heinz Guderian': 'হাইনৎস গুডেরিয়ান',
    'Hector Berlioz': 'হেক্টর বার্লিওজ',
    'Elsa Reger': 'এলসা রেগার',
    'Billie Holiday': 'বিলি হলিডে',
    'Charles Darwin': 'চার্লস ডারউইন',
    'Jean-Paul Sartre': 'জঁ-পল সার্ত্র',
    'David Hume': 'ডেভিড হিউম',
    'John Stuart Mill': 'জন স্টুয়ার্ট মিল',
    'Philip M. Morse': 'ফিলিপ এম. মোর্স',
    'Richard Feynman': 'রিচার্ড ফাইনম্যান',
    'Luis Walter Alvarez': 'লুইস আলভারেজ',
    'Luis Alvarez': 'লুইস আলভারেজ',
    'Marcus Aurelius': 'মার্কাস অরেলিয়াস',
    'Manuel Belgrano': 'ম্যানুয়েল বেলগ্রানো',
    'Frederick Douglass': 'ফ্রেডেরিক ডগলাস',
    'Sigmund Freud': 'জিগমুন্ট ফ্রয়েড',
    'Carl Jung': 'কার্ল গুস্তাভ ইয়ুং',
    'Babe Ruth': 'বেব রুথ',
    'Joe DiMaggio': 'জো ডিম্যাজিও',
    'Ted Husing': 'টেড হিউসিং',
    'Augustine of Hippo': 'হিপোর অগাস্টিন',
    'Al-Ghazali': 'আল-গাজ্জালি',
    'Peter Abelard': 'পিটার অ্যাবেলার্ড',
    'Firuz Shah Tughlaq': 'ফিরোজ শাহ তুঘলক',
    'Firoz Shah Tuglaq': 'ফিরোজ শাহ তুঘলক',
    'Babur': 'বাবর',
    'Tuzuk-i-Babri': 'বাবর',
    'Adolf Hitler': 'এডলফ হিটলার',
    'Nelson Mandela': 'নেলসন ম্যান্ডেলা',
    'Mahatma Gandhi': 'মহাত্মা গান্ধী',
    'Anne Frank': 'আনা ফ্রাঙ্ক',
    'Frank McCourt': 'ফ্র্যাঙ্ক ম্যাককোর্ট',
    'Jawaharlal Nehru': 'জওহরলাল নেহেরু',
    'A. P. J. Abdul Kalam': 'এ পি জে আব্দুল কালাম',
    'Nirad C. Chaudhuri': 'নীরদচন্দ্র চৌধুরী',
    'Satyajit Ray': 'সত্যজিৎ রায়',
    'Taslima Nasrin': 'তসলিমা নাসরিন',
    'Paramahansa Yogananda': 'পরমহংস যোগানন্দ',
    'Johann Wolfgang von Goethe': 'ইয়োহান ভোলফগাংক ফন গ্যোটে',
    'Leo Tolstoy': 'লেভ তলস্তয়',
    'Maxim Gorky': 'মাক্সিম গোর্কি',
    'Benvenuto Cellini': 'বেনভেনুতো চেল্লিনি',
    'Giacomo Casanova': 'জাকোমো কাসানোভা',
    'Benjamin Franklin': 'বেঞ্জামিন ফ্র্যাঙ্কলিন',
    'Malala Yousafzai': 'মালালা ইউসুফজাই',
    'Jahangir': 'জাহাঙ্গীর',
    'Jean-Jacques Rousseau': 'জঁ-জাক রুশো',
    'Maya Angelou': 'মায়া অ্যাঞ্জেলো',
    'Malcolm X': 'ম্যালকম এক্স',
    'Chuck Yeager': 'চাক ইয়েগার',
    'Curtis LeMay': 'কার্টিস লেমে',
    'Arthur Tedder': 'আর্থার টেডার',
    'Eddie Rickenbacker': 'এডি রিকেনব্যাকার',
    'Jean Batten': 'জিন ব্যাটেন',
    'Stanley Hooker': 'স্ট্যানলি হুকার',
    'Alan Cobham': 'অ্যালান কোবহাম',
    'Donald Wilson': 'ডোনাল্ড উইলসন',
    'Arthur Lee': 'আর্থার লি',
    'Charles Lamb': 'চার্লস ল্যাম্ব',
    'William R. Dunn': 'উইলিয়াম আর. ডান',
    'Robert Mason': 'রবার্ট মেসন',
    'Charles Bond': 'চার্লস বন্ড',
    'Barack Obama': 'বারাক ওবামা',
    'Michelle Obama': 'মিশেল ওবামা',
    'Bill Clinton': 'বিল ক্লিনটন',
    'Hillary Clinton': 'হিলারি ক্লিনটন',
    'Tony Blair': 'টনি ব্লেয়ার',
    'Margaret Thatcher': 'মার্গারেট থ্যাচার',
    'Winston Churchill': 'উইনস্টন চার্চিল',
    'Stephen Hawking': 'স্টিফেন হকিং',
    'Alan Turing': 'অ্যালান টুরিং',
    'Günther Rall': 'গুন্থার রাল',
    'Ricardo Montalbán': 'রিকার্দো মন্টালবান',
    'Leonor López de Córdoba': 'লেওনোর লোপেস দে কর্দোবা',
    'Cédric Villani': 'সেদ্রিক ভিলানি',
    "Sinéad O'Connor": "শিনাড ও'কনর",
    'Emilio Segrè': 'এমিলিও সেগরে',
    'Teresa of Ávila': 'আভিলার তেরেসা',
    'Thérèse of Lisieux': 'লিসিয়ুর তেরেসা',
    'Lizzie Velásquez': 'লিজি ভেলাসকেস',
    'Sei Shōnagon': 'সেই শোনাহোন',
    'Kamo No Chomei': 'কামো নো চোমেই',
    'Margery Kempe': 'মার্জারি কেম্প',
    'Marcus Samuelsson': 'মার্কাস স্যামুয়েলসন',
    'Barry Norman': 'ব্যারি নরম্যান',
    'Zohre Esmaeli': 'জোহরে এসমায়েলি',
    'Ree Drummond': 'রি ড্রামন্ড',
    'Alex Trebek': 'অ্যালেক্স ট্রেবেক',
    'Ranjan Gogoi': 'রঞ্জন গগৈ',
    'Christie Brinkley': 'ক্রিস্টি ব্রিংকলি',
    'Ann B. Carl': 'অ্যান বি. কার্ল'
}

for k, v in extra_authors.items():
    if k not in author_bn:
        author_bn[k] = v

# Additional book title translations
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
    'Nothing Is There': 'নেই কিছু নেই'
}

for k, v in extra_books.items():
    if k not in book_bn:
        book_bn[k] = v

# Phonetic transliteration dictionary for name components
NAME_COMPONENTS = {
    'Billy': 'বিলি', 'Bishop': 'বিশপ', 'James': 'জেমস', 'McCudden': 'ম্যাককাডেন',
    'Ann': 'অ্যান',
    'René': 'রনে', 'Fonck': 'ফঙ্ক', 'Richard': 'রিচার্ড', 'Byrd': 'বার্ড',
    'Clarence': 'ক্ল্যারেন্স', 'Chamberlin': 'চেম্বারলিন', 'Frank': 'ফ্র্যাঙ্ক', 'Hawks': 'হকস',
    'Willy': 'উইলি', 'Coppens': 'কপেনস', 'Duncan': 'ডানকান', 'Grinnell-Milne': 'গ্রিনেল-মিলনে',
    'Scott': 'স্কট', 'Beirne': 'বার্ন', 'Lay': 'লে', 'Tinker': 'টিঙ্কার', 'Glasgow': 'গ্লাসগো',
    'Louise': 'লুইস', 'Thaden': 'থাডেন', 'Igor': 'ইগর', 'Sikorsky': 'সিকোরস্কি',
    'Hillary': 'হিলারি', 'Beryl': 'বেরিল', 'Markham': 'মারখাম', 'Ted': 'টেড', 'Lawson': 'লসন',
    'Don': 'ডন', 'Gentile': 'জেনটাইল', 'Guy': 'গাই', 'Gibson': 'গিবসন', 'Arthur': 'আর্থার',
    'Harris': 'হ্যারিস', 'Bert': 'বার্ট', 'Stiles': 'স্টাইলস', 'Henry': 'হেনরি', 'Arnold': 'আর্নল্ড',
    'Claire': 'ক্লেয়ার', 'Chennault': 'শেনল্ট', 'George': 'জর্জ', 'Kenney': 'কেনি',
    'Ivan': 'ইভান', 'Kozhedub': 'কোঝেদুব', 'Hans-Ulrich': 'হান্স-উলরিখ', 'Rudel': 'রুডেল',
    'Dick': 'ডিক', 'Grace': 'গ্রেস', 'William': 'উইলিয়াম', 'Bushnell': 'বুশনেল', 'Stout': 'স্টাউট',
    'Pierre': 'পিয়ের', 'Clostermann': 'ক্লোস্তেরমান', 'Hanna': 'হানা', 'Reitsch': 'রাইচ',
    'Adolf': 'এডলফ', 'Galland': 'গ্যালান্ড', 'Ernst': 'আর্নস্ট', 'Heinkel': 'হাইঙ্কেল',
    'Heinz': 'হাইনৎস', 'Knoke': 'ক্নোকে', 'Nevil': 'নেভিল', 'Shute': 'শুট',
    'Bill': 'বিল', 'Bridgeman': 'ব্রিজম্যান', 'Eino': 'এইনো', 'Luukkanen': 'লুক্কানেন',
    'Johnnie': 'জনি', 'Johnson': 'জনসন', 'John': 'জন', 'Slessor': 'স্লেসর',
    'Basil': 'ব্যাসিল', 'Embry': 'এমব্রি', 'Saburō': 'সাবুরো', 'Sakai': 'সাকাই',
    'Pappy': 'প্যাপি', 'Boyington': 'বোয়িংটন', 'Robert': 'রবার্ট', 'Alexander': 'আলেকজান্ডার',
    'Yakovlev': 'ইয়াকোভলেভ', 'Sergeyevich': 'সের্গেইয়েভিচ', 'Kaberov': 'কাবেরভ',
    'Lippisch': 'লিপিশ', 'Alberto': 'আলবের্তো', 'Briganti': 'ব্রিগান্তি', 'Takeo': 'তাকেয়ো',
    'Doi': 'দোই', 'Margaret': 'মার্গারেট', 'Mead': 'মিড', 'Murray': 'মারি',
    'Lloyd': 'লয়েড', 'Wright': 'রাইট', 'Salvador': 'সালভাদোর', 'Dalí': 'দালি',
    'Claude': 'ক্লোদ', 'Monet': 'মোনে', 'Gwen': 'গোয়েন', 'Raverat': 'রাভেরাত',
    'Andrew': 'অ্যান্ড্রু', 'Carnegie': 'কার্নেগি', 'Ford': 'ফোর্ড', 'DeVos': 'ডিভোস',
    'Terry-Thomas': 'টেরি-টমাস', 'Harpo': 'হার্পো', 'Marx': 'মার্ক্স', 'Charlie': 'চার্লি',
    'Chaplin': 'চ্যাপলিন', 'Isadora': 'ইসাডোরা', 'Duncan': 'ডানকান', 'Vincent': 'ভিনসেন্ট',
    'Price': 'প্রাইস', 'Fred': 'ফ্রেড', 'Astaire': 'অ্যাস্টেয়ার', 'Ken': 'কেন',
    'Edward': 'এডওয়ার্ড', 'Gibbon': 'এডওয়ার্ড গিবন', 'Henry': 'হেনরি', 'Adams': 'অ্যাডামস',
    'Martin': 'মার্টিন', 'Latham': 'ল্যাথাম', 'Mehmood': 'মেহমুদ', 'Hashmi': 'হাশমি',
    'Libanius': 'লিবানিয়াস', 'Sei': 'সেই', 'Shōnagon': 'শোনাতন', 'Kamo': 'কামো',
    'Hardy': 'হার্ডি', 'Norbert': 'নরবার্ট', 'Wiener': 'উইনার', 'Bertrand': 'বারট্রান্ড',
    'Russell': 'রাসেল', 'Albert': 'আলবার্ট', 'Schweitzer': 'শোয়েইৎজার', 'Sydney': 'সিডনি',
    'Smith': 'স্মিথ', 'Sandra': 'স্যান্ড্রা', 'Lee': 'লি', 'Ulysses': 'উইলিসিস', 'Grant': 'গ্রান্ট',
    'Guderian': 'গুডেরিয়ান', 'Hector': 'হেক্টর', 'Berlioz': 'বার্লিওজ', 'Elsa': 'এলসা',
    'Reger': 'রেগার', 'Billie': 'বিলি', 'Holiday': 'হলিডে', 'Charles': 'চার্লস',
    'Darwin': 'ডারউইন', 'Jean-Paul': 'জঁ-পল', 'Sartre': 'সার্ত্র', 'David': 'ডেভিড',
    'Hume': 'হিউম', 'Stuart': 'স্টুয়ার্ট', 'Mill': 'মিল', 'Philip': 'ফিলিপ', 'Morse': 'মোর্স',
    'Feynman': 'ফাইনম্যান', 'Luis': 'লুইস', 'Walter': 'ওয়াল্টার', 'Alvarez': 'আলভারেজ',
    'Marcus': 'মার্কাস', 'Aurelius': 'অরেলিয়াস', 'Manuel': 'ম্যানুয়েল', 'Belgrano': 'বেলগ্রানো',
    'Frederick': 'ফ্রেডেরিক', 'Douglass': 'ডগলাস', 'Sigmund': 'জিগমুন্ট', 'Freud': 'ফ্রয়েড',
    'Carl': 'কার্ল', 'Jung': 'ইয়ুং', 'Babe': 'বেব', 'Ruth': 'রুথ', 'Joe': 'জো',
    'DiMaggio': 'ডিম্যাজিও', 'Ted': 'テッド', 'Husing': 'হিউসিং', 'Augustine': 'অগাস্টিন',
    'Peter': 'পিটার', 'Abelard': 'অ্যাবেলার্ড', 'Firuz': 'ফিরোজ', 'Shah': 'শাহ',
    'Tughlaq': 'তুঘলক', 'Babur': 'বাবর', 'Hitler': 'হিটলার', 'Mandela': 'ম্যান্ডেলা',
    'Gandhi': 'গান্ধী', 'Anne': 'আনা', 'Frank': 'ফ্র্যাঙ্ক', 'McCourt': 'ম্যাককোর্ট',
    'Nehru': 'নেহেরু', 'Kalam': 'কালাম', 'Chaudhuri': 'চৌধুরী', 'Ray': 'রায়',
    'Nasrin': 'নাসরিন', 'Yogananda': 'যোগানন্দ', 'Goethe': 'গ্যোটে', 'Tolstoy': 'তলস্তয়',
    'Gorky': 'গোর্কি', 'Cellini': 'চেল্লিনি', 'Casanova': 'কাসানোভা', 'Franklin': 'ফ্র্যাঙ্কলিন',
    'Malala': 'মালালা', 'Yousafzai': 'ইউসুফজাই', 'Jahangir': 'জাহাঙ্গীর', 'Rousseau': 'রুশো',
    'Curtis': 'কার্টিস', 'LeMay': 'লেমে', 'Arthur': 'আর্থার', 'Tedder': 'টেডার',
    'Eddie': 'এডি', 'Rickenbacker': 'রিকেনব্যাকার', 'Chuck': 'চাক', 'Yeager': 'ইয়েগার',
    'Jean': 'জিন', 'Batten': 'ব্যাটেন', 'Stanley': 'স্ট্যানলি', 'Hooker': 'হুকার',
    'Alan': 'অ্যালান', 'Cobham': 'কোবহাম', 'Donald': 'ডোনাল্ড', 'Wilson': 'উইলসন',
    'Lamb': 'ল্যাম্ব', 'Dunn': 'ডান', 'Mason': 'মেসন', 'Bond': 'বন্ড',
    'Arch': 'আর্চ', 'Whitehouse': 'হোয়াইটহাউস', 'Benjamin': 'বেঞ্জামিন', 'Foulois': 'ফুলা',
    'Goddard': 'গডার্ড', 'Raymond': 'রেমন্ড', 'Collishaw': 'কলিশ', 'Jan': 'ইয়ান',
    'Zumbach': 'জুমবাখ', 'Cecil': 'সিসিল', 'Lewis': 'লুইস', 'Henshaw': 'হেনশ',
    'Murray': 'মারি', 'Peden': 'পেডেন', 'Władysław': 'ভ্লাদিস্লাভ', 'Gnyś': 'গ্নিস',
    'Duke': 'ডিউক', 'Cunningham': 'কানিংহাম', 'Gerhard': 'গেরহার্ড', 'Neumann': 'নিউম্যান',
    'Al': 'আল', 'Mooney': 'মুনি', 'Haywood': 'হেউড', 'Hansell': 'হ্যানসেল',
    'Paul': 'পল', 'Tibbets': 'টিবেটস', 'Kelly': 'কেলি', 'Johnson': 'জনসন',
    'Kermit': 'কারমিট', 'Tyler': 'টাইলার', 'Robin': 'রবিন', 'Olds': 'ওল্ডস',
    'Noel': 'নোয়েল', 'Wien': 'উইন', 'Jack': 'জ্যাক', 'Broughton': 'ব্রটন',
    'Gordon': 'গর্ডন', 'Baxter': 'ব্যাক্সটার', 'Sam': 'স্যাম', 'Halley': 'হ্যালি',
    'Sammy': 'স্যামি', 'Mason': 'মেসন', 'Gordon': 'গর্ডন', 'Cooper': 'কুপার',
    'Deke': 'ডিক', 'Slayton': 'স্লেইটন', 'Michael': 'মাইকেল', 'Collins': 'কলিন্স',
    'Buzz': 'বাজ', 'Aldrin': 'অলড্রিন', 'Gene': 'জিন', 'Cernan': 'সারনান',
    'Wally': 'ওয়ালি', 'Schirra': 'শিরা', 'Scott': 'স্কট', 'Carpenter': 'কার্পেন্টার',
    'Jim': 'জিম', 'Lovell': 'লাভেল', 'Alan': 'অ্যালান', 'Shepard': 'শেপার্ড',
    'Neil': 'নিল', 'Armstrong': 'আর্মস্ট্রং', 'John': 'জন', 'Glenn': 'গ্লেন',
    'Chris': 'ক্রিস', 'Kraft': 'ক্রাফট', 'Gene': 'জিন', 'Kranz': 'ক্রাঞ্জ',
    'Chuck': 'চাক', 'Sewell': 'সিউয়েল', 'Bob': 'বব', 'Hoover': 'হুভার',
    'Eileen': 'আইলিন', 'Collins': 'কলিন্স', 'Mike': 'মাইক', 'Mullane': 'মুলেন',
    'Jerry': 'জেরি', 'Linenger': 'লিনেনজার', 'Clayton': 'ক্লেটন', 'Anderson': 'অ্যান্ডারসন',
    'Scott': 'স্কট', 'Kelly': 'কেলি', 'Mark': 'মার্ক', 'Kelly': 'কেলি',
    'Chris': 'ক্রিস', 'Hadfield': 'হ্যাডফিল্ড', 'Tim': 'টিম', 'Peake': 'পিক',
    'Thomas': 'টমাস', 'Pesquet': 'পেসকে', 'Alexander': 'আলেকজান্ডার', 'Gerst': 'গার্স্ট',
    'Samantha': 'সামান্থা', 'Cristoforetti': 'ক্রিস্টোফোরেত্তি', 'Luca': 'লুকা', 'Parmitano': 'পারমিতানো',
    'Chesley': 'চেসলি', 'Sullenberger': 'সুলেনবার্গার', 'Jeff': 'জেফ', 'Skiles': 'স্কাইলস',
    'Brian': 'ব্রায়ান', 'Trubshaw': 'ট্রাবশ', 'André': 'আন্দ্রে', 'Turcat': 'তুর্কাত',
    'Sir': 'স্যার', 'Jr.': 'জুনিয়র', 'Sr.': 'সিনিয়র', 'Lord': 'লর্ড', 'Lady': 'লেডি',
    'von': 'ফন', 'van': 'ভান', 'de': 'দ্য', 'di': 'দি', 'du': 'দ্যু', 'la': 'লা', 'le': 'লে', 'el': 'এল'
}

INITIALS = {
    'A.': 'এ.', 'B.': 'বি.', 'C.': 'সি.', 'D.': 'ডি.', 'E.': 'ই.', 'F.': 'এফ.',
    'G.': 'জি.', 'H.': 'এইচ.', 'I.': 'আই.', 'J.': 'জে.', 'K.': 'কে.', 'L.': 'এল.',
    'M.': 'এম.', 'N.': 'এন.', 'O.': 'ও.', 'P.': 'পি.', 'Q.': 'কিউ.', 'R.': 'আর.',
    'S.': 'এস.', 'T.': 'টি.', 'U.': 'ইউ.', 'V.': 'ভি.', 'W.': 'ডব্লিউ.', 'X.': 'এক্স.',
    'Y.': 'ওয়াই.', 'Z.': 'জেড.'
}

def transliterate_word(w):
    if not w:
        return ''
    if w in INITIALS:
        return INITIALS[w]
    if w in NAME_COMPONENTS:
        return NAME_COMPONENTS[w]
    
    # Clean non-alpha
    clean_w = re.sub(r'[^a-zA-ZÀ-ÿ]', '', w)
    if clean_w in NAME_COMPONENTS:
        return NAME_COMPONENTS[clean_w]

    # Rule 4.1: words never start with 'ts' or 'z' in Bengali -> 'স' / 'সু'
    low = w.lower()
    if low.startswith('ts'):
        return 'সু' + transliterate_phonetic(w[2:])
    if low.startswith('z'):
        return 'স' + transliterate_phonetic(w[1:])
    
    return transliterate_phonetic(w)

def transliterate_phonetic(s):
    # Rule 4.2: Foreign words never use 'ষ' or 'ণ'; use 'স' and 'ন'
    mapping = [
        ('tion', 'শন'), ('sion', 'শন'), ('tch', 'চ'), ('ch', 'চ'),
        ('sh', 'শ'), ('ph', 'ফ'), ('th', 'থ'), ('wh', 'হোয়'),
        ('ck', 'ক'), ('qu', 'ক্ব'), ('gh', 'ঘ'), ('kh', 'খ'),
        ('ng', 'ং'), ('ee', 'ি'), ('oo', 'ু'), ('ea', 'ি'),
        ('ai', 'াই'), ('ay', 'ে'), ('ey', 'ি'), ('oy', 'য়'),
        ('oi', 'য়'), ('ou', 'াউ'), ('au', 'অ'), ('aw', 'অ'),
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
    low = s.lower()
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
    
    # Fix initial vowel signs
    vowel_initial = {
        'া': 'আ', 'ে': 'এ', 'ি': 'ই', 'ী': 'ঈ', 'ু': 'উ', 'ূ': 'ঊ', 'ো': 'ও', 'ৌ': 'ঔ', 'ৈ': 'ঐ'
    }
    if res and res[0] in vowel_initial:
        res = vowel_initial[res[0]] + res[1:]
    return res

def transliterate_full_name(name):
    # Split on spaces and hyphens
    tokens = re.split(r'(\s+|-)', name)
    out = []
    for t in tokens:
        if t.isspace() or t == '-':
            out.append(t)
        elif t:
            out.append(transliterate_word(t))
    return ''.join(out)

def format_author(author_raw):
    # Extract link if any
    m = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', author_raw)
    if m:
        target = m.group(1).strip()
        disp = m.group(2).strip() if m.group(2) else target
        clean_target = re.sub(r'\s*\([^)]*\)', '', target).strip()
        clean_disp = re.sub(r'\s*\([^)]*\)', '', disp).strip()
        
        # Check author_bn
        if target in author_bn:
            return f"[[{author_bn[target]}]]"
        if clean_target in author_bn:
            return f"[[{author_bn[clean_target]}]]"
        if disp in author_bn:
            return f"[[{author_bn[disp]}]]"
        if clean_disp in author_bn:
            return f"[[{author_bn[clean_disp]}]]"
        
        # Transliterate disp
        bn_name = transliterate_full_name(clean_disp)
        return f"[[{target}|{bn_name}]]"
    else:
        clean = re.sub(r'\[\[|\]\]', '', author_raw).strip()
        clean_disp = re.sub(r'\s*\([^)]*\)', '', clean).strip()
        if clean_disp in author_bn:
            return author_bn[clean_disp]
        return transliterate_full_name(clean_disp)

def to_bn_num(s):
    if not s or s.strip() == '' or s.strip() == '&nbsp;':
        return '&nbsp;'
    s = s.strip()
    # Handle range or dates
    digits = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
    s = re.sub(r'\b0+(\d+)\b', r'\1', s)
    res = ''
    for char in s:
        res += digits.get(char, char)
    res = res.replace('-', '–')
    if 'xx' in res or 'XX' in res:
        res = res.replace('xx', '০০').replace('XX', '০০')
    return res

def get_language(author_raw, title_raw):
    # 1. Check book_lang
    m_b = re.search(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]', title_raw)
    btitle = m_b.group(1).strip() if m_b else None
    if btitle and btitle in book_lang:
        return book_lang[btitle]
    
    # Clean title
    clean_b = re.sub(r"''|\[\[|\]\]", '', title_raw).strip()
    if clean_b in book_lang:
        return book_lang[clean_b]

    # 2. Check explicit foreign scripts
    if re.search(r'[\u0400-\u04FF]', title_raw):
        return 'রুশ'
    if re.search(r'[\u3040-\u30FF\u4E00-\u9FFF]', title_raw):
        return 'জাপানি'
    if re.search(r'[\u0600-\u06FF]', title_raw):
        if 'Kashmir' in title_raw or 'Hashmi' in author_raw:
            return 'উর্দু'
        return 'আরবি'
    
    # 3. Specific historic authors
    if 'Augustine' in author_raw or 'Abelard' in author_raw:
        return 'লাতিন'
    if 'Libanius' in author_raw or 'Marcus Aurelius' in author_raw:
        return 'প্রাচীন গ্রিক'
    if 'Firuz Shah' in author_raw or 'Tughlaq' in author_raw or 'Jahangir' in author_raw or 'Gulbadan' in author_raw:
        return 'ফার্সি'
    if 'Babur' in author_raw or 'Tuzuk-i-Babri' in author_raw:
        return 'চাগাতাই'
    if 'Al-Ghazali' in author_raw:
        return 'আরবি'
    if 'Gandhi' in author_raw:
        return 'গুজরাতি'
    if 'Satyajit' in author_raw or 'Taslima' in author_raw:
        return 'বাংলা'
    if 'Kierkegaard' in author_raw:
        return 'ডেনীয়'
    if 'Nietzsche' in author_raw or 'Goethe' in author_raw or 'Hitler' in author_raw:
        return 'জার্মান'
    if 'Rousseau' in author_raw or 'Sartre' in author_raw or 'Berlioz' in author_raw or 'Dalí' in author_raw:
        return 'ফরাসি'
    if 'Cellini' in author_raw:
        return 'ইতালীয়'
    if 'Casanova' in author_raw:
        return 'ফরাসি'
    if 'Luukkanen' in author_raw or 'Hävittäjälentäjänä' in title_raw:
        return 'ফিনীয়'
    if 'Briganti' in author_raw or 'Oltre le Nubi' in title_raw:
        return 'ইতালীয়'
    if 'Rudel' in author_raw or 'Trotzdem' in title_raw or 'Heinkel' in author_raw or 'Reitsch' in author_raw:
        return 'জার্মান'
    if 'Fonck' in author_raw or 'Mes Combats' in title_raw or 'Clostermann' in author_raw or 'Coppens' in author_raw:
        return 'ফরাসি'
    if 'Belgrano' in author_raw:
        return 'স্পেনীয়'
    if 'Freud' in author_raw or 'Jung' in author_raw or 'Schweitzer' in author_raw or 'Guderian' in author_raw or 'Reger' in author_raw:
        return 'জার্মান'
    if 'Yakovlev' in author_raw or 'Kaberov' in author_raw or 'Kozhedub' in author_raw or 'Tolstoy' in author_raw or 'Gorky' in author_raw:
        return 'রুশ'
    if 'Doi' in author_raw or 'Sakai' in author_raw or 'Kurosawa' in author_raw:
        return 'জাপানি'

    # 4. Check author_lang
    m_a = re.search(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]', author_raw)
    aname = m_a.group(1).strip() if m_a else re.sub(r'\[\[|\]\]', '', author_raw).strip()
    clean_aname = re.sub(r'\s*\([^)]*\)', '', aname).strip()
    if aname in author_lang:
        return author_lang[aname]
    if clean_aname in author_lang:
        return author_lang[clean_aname]
    
    # 5. Otherwise leave empty with &nbsp;
    return '&nbsp;'

def format_title(title_raw):
    # Check if there are notes (efn or ref)
    notes = ''
    m_efn = re.search(r'(\{\{efn\|.*?\}\}|\{\{efn\|.*?$|<ref>.*?</ref>|<ref\s+name=.*?/>|<ref\s+name=.*?>.*?</ref>)', title_raw, re.DOTALL)
    if m_efn:
        notes = m_efn.group(1)
        title_core = title_raw.replace(notes, '').strip()
    else:
        title_core = title_raw.strip()

    # Check book_bn
    m_b = re.search(r'\[\[([^\]\|]+)(?:\|([^\]]+))?\]\]', title_core)
    if m_b:
        target = m_b.group(1).strip()
        disp = m_b.group(2).strip() if m_b.group(2) else target
        clean_target = re.sub(r'\s*\([^)]*\)', '', target).strip()
        
        if target in book_bn:
            res = f"''[[{book_bn[target]}]]''"
        elif clean_target in book_bn:
            res = f"''[[{book_bn[clean_target]}]]''"
        elif disp in book_bn:
            res = f"''[[{book_bn[disp]}]]''"
        else:
            # Keep link, transliterate disp or use standard title
            res = f"''[[{target}|{disp}]]''"
    else:
        # Check if bilingual with parentheses
        m_paren = re.search(r"^''([^'(]+)''\s*\(([^)]+)\)$", title_core)
        if not m_paren:
            m_paren = re.search(r"^''([^'(]+)\s*\(([^)]+)\)''$", title_core)
        
        if m_paren:
            eng_part = m_paren.group(1).strip()
            foreign_part = m_paren.group(2).strip()
            if not foreign_part.startswith("''"):
                foreign_part = f"''{foreign_part}''"
            res = f"''{eng_part}'' ({foreign_part})"
        else:
            clean_t = title_core
            if not clean_t.startswith("''"):
                clean_t = f"''{clean_t}''"
            res = clean_t

    if notes:
        res = f"{res}{notes}"
    return res

print('Helper functions defined.')

SECTION_MAP = {
    'Aerospace': 'মহাকাশ ও বিমান চালনা',
    'Anthropology': 'নৃবিজ্ঞান',
    'Archaeology': 'প্রত্নতত্ত্ব',
    'Architecture': 'স্থাপত্য',
    'Art': 'চারুকলা',
    'Business': 'ব্যবসা ও বাণিজ্য',
    'Comedy': 'হাস্যরস ও কৌতুক',
    'Dance': 'নৃত্য',
    'Drama': 'নাট্যকলা ও অভিনয়',
    'History': 'ইতিহাস',
    'Journalism': 'সাংবাদিকতা',
    'Law': 'আইন',
    'Literature': 'সাহিত্য',
    'Mathematics': 'গণিত',
    'Medicine': 'চিকিৎসা বিজ্ঞান',
    'Military': 'সামরিক',
    'Music': 'সঙ্গীত',
    'Natural History': 'প্রাকৃতিক ইতিহাস',
    'Philosophy': 'দর্শন',
    'Physics': 'পদার্থবিজ্ঞান',
    'Politics': 'রাজনীতি',
    'Psychology': 'মনোবিজ্ঞান',
    'Sports': 'ক্রীড়া',
    'Religion/Theology': 'ধর্ম ও ধর্মতত্ত্ব',
    'Uncategorized': 'বিবিধ'
}

NEW_ENTRIES = {
    'Literature': [
        ('[[রবীন্দ্রনাথ ঠাকুর]]', "''[[জীবনস্মৃতি]]''", 'বাংলা', '১৯১২'),
        ('[[রাসসুন্দরী দেবী]]', "''[[আমার জীবন (আত্মজীবনী)|আমার জীবন]]''", 'বাংলা', '১৮৭৬'),
        ('[[ঈশ্বরচন্দ্র বিদ্যাসাগর]]', "''[[আত্মচরিত]]''", 'বাংলা', '১৮৯১'),
        ('[[দেবেন্দ্রনাথ ঠাকুর]]', "''[[আত্মজীবনী (দেবেন্দ্রনাথ ঠাকুর)|আত্মজীবনী]]''", 'বাংলা', '১৮৯৮'),
        ('[[বিনোদিনী দাসী]]', "''[[আমার কথা (আত্মজীবনী)|আমার কথা]]''", 'বাংলা', '১৯১২'),
        ('[[শিবনাথ শাস্ত্রী]]', "''[[আত্মচরিত (শিবনাথ শাস্ত্রী)|আত্মচরিত]]''", 'বাংলা', '১৯১৮'),
        ('[[অবনীন্দ্রনাথ ঠাকুর]]', "''[[আপন কথা]]''", 'বাংলা', '১৯৪৬'),
        ('[[হুমায়ূন আহমেদ]]', "''[[আমার ছেলেবেলা]]''", 'বাংলা', '১৯৯৩'),
        ('[[সুনীল গঙ্গোপাধ্যায়]]', "''[[অর্ধেক জীবন]]''", 'বাংলা', '২০০২'),
        ('[[শামসুর রাহমান]]', "''[[কালের ধুলোয় লেখা]]''", 'বাংলা', '২০০৪')
    ],
    'Politics': [
        ('[[শেখ মুজিবুর রহমান]]', "''[[অসমাপ্ত আত্মজীবনী]]''", 'বাংলা', '২০১২'),
        ('[[আবুল মনসুর আহমদ]]', "''[[আত্মকথা (আবুল মনসুর আহমদ)|আত্মকথা]]''", 'বাংলা', '১৯৭৮'),
        ('[[সুভাষচন্দ্র বসু]]', "''[[অ্যান ইন্ডিয়ান পিলগ্রিম]]'' (''An Indian Pilgrim'')", 'ইংরেজি', '১৯৪৮'),
        ('[[বি. আর. আম্বেদকর]]', "''[[ওয়েটিং ফর আ ভিসা]]'' (''Waiting for a Visa'')", 'ইংরেজি', '১৯৩৬'),
        ('[[ভগৎ সিং]]', "''[[হোয়াই আই অ্যাম অ্যান অ্যাথিস্ট]]'' (''Why I Am an Atheist'')", 'ইংরেজি', '১৯৩০'),
        ('[[আবুল কালাম আজাদ]]', "''[[ইন্ডিয়া উইনস ফ্রিডম]]'' (''India Wins Freedom'')", 'ইংরেজি', '১৯৫৯'),
        ('[[মিশেল ওবামা]]', "''[[বিকামিং (বই)|বিকামিং]]'' (''Becoming'')", 'ইংরেজি', '২০১৮'),
        ('[[এডওয়ার্ড স্নোডেন]]', "''[[পার্মানেন্ট রেকর্ড (বই)|পার্মানেন্ট রেকর্ড]]'' (''Permanent Record'')", 'ইংরেজি', '২০১৯'),
        ('[[জুলিয়ান অ্যাসাঞ্জ]]', "''[[জুলিয়ান অ্যাসাঞ্জ: দি আনঅথোরাইজড অটোবায়োগ্রাফি]]''", 'ইংরেজি', '২০১১')
    ],
    'History': [
        ('[[গুলবদন বেগম]]', "''[[হুমায়ুননামা]]''", 'ফার্সি', '১৫৮৭')
    ],
    'Philosophy': [
        ('[[সোরেন কিয়ের্কেগার্ড]]', "''[[দ্য পয়েন্ট অব ভিউ অব মাই ওয়ার্ক অ্যাজ অ্যান অথর]]''", 'ডেনীয়', '১৮৫৯'),
        ('[[ফ্রিডরিখ নিচে]]', "''[[এক্কে হোমো (বই)|এক্কে হোমো]]'' (''Ecce Homo'')", 'জার্মান', '১৮৮৮')
    ]
}

with open('List_of_autobiographies_raw.txt', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
output_lines.append("এটি উল্লেখযোগ্য '''[[আত্মজীবনী|আত্মজীবনীর একটি তালিকা]]'''।")
output_lines.append("")
output_lines.append("== পেশাভিত্তিক তালিকা ==")
output_lines.append('{| class="wikitable sortable" style="text-align: left;"')
output_lines.append('|-')
output_lines.append('! style="width:25%;"| লেখক')
output_lines.append('! style="width:45%;"| বইয়ের শিরোনাম')
output_lines.append('! style="width:15%;"| মূল ভাষা')
output_lines.append('! style="width:15%;"| প্রকাশনার বছর')

current_section = ''
i = 0
total_translated = 0

while i < len(lines):
    line = lines[i].strip()
    if line.startswith('! colspan=3|'):
        sec_raw = line.split('|')[1].strip()
        current_section = sec_raw
        bn_sec = SECTION_MAP.get(sec_raw, sec_raw)
        output_lines.append('|-')
        output_lines.append(f'! colspan=4|{bn_sec}')
        
        # Add new entries for this section at the start if any
        if sec_raw in NEW_ENTRIES:
            for n_auth, n_tit, n_lang, n_yr in NEW_ENTRIES[sec_raw]:
                output_lines.append('|-')
                output_lines.append(f'|{n_auth} ||{n_tit} ||{n_lang} ||{n_yr}')
                total_translated += 1
        i += 1
        continue
    
    if line.startswith('|-') or line.startswith('{|') or line.startswith('|}') or line.startswith('!') or not line:
        i += 1
        continue
    
    if line.startswith('|'):
        # Check split lines
        if '||' not in line:
            if i+2 < len(lines) and lines[i+1].strip().startswith('|') and lines[i+2].strip().startswith('|'):
                auth_raw = line.lstrip('|').strip()
                tit_raw = lines[i+1].strip().lstrip('|').strip()
                yr_raw = lines[i+2].strip().lstrip('|').strip()
                
                auth_bn = format_author(auth_raw)
                tit_bn = format_title(tit_raw)
                lang_bn = get_language(auth_raw, tit_raw)
                yr_bn = to_bn_num(yr_raw)
                
                output_lines.append('|-')
                output_lines.append(f'|{auth_bn} ||{tit_bn} ||{lang_bn} ||{yr_bn}')
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
            tit_bn = format_title(tit_raw)
            lang_bn = get_language(auth_raw, tit_raw)
            yr_bn = to_bn_num(yr_raw)
            
            output_lines.append('|-')
            output_lines.append(f'|{auth_bn} ||{tit_bn} ||{lang_bn} ||{yr_bn}')
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

final_text = '\n'.join(output_lines)
with open('আত্মজীবনীর তালিকা (বাংলা).txt', 'w', encoding='utf-8') as f:
    f.write(final_text)

print(f'Successfully generated আত্মজীবনীর তালিকা (বাংলা).txt with {total_translated} entries!')

