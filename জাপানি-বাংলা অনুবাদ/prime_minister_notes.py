# -*- coding: utf-8 -*-
"""
প্রধানমন্ত্রীদের বিবরণ ও ভারপ্রাপ্ত প্রধানমন্ত্রীর মন্তব্য অনুবাদ মানচিত্র (Prime Ministers Table Descriptions Map)
"""

COLSPAN_DESCRIPTIONS = {
    # Meiji, Taisho, early Showa additions:
    "The first Prime Minister of the Empire of Japan.":
    "[[Empire of Japan|জাপান সাম্রাজ্যের]] প্রথম প্রধানমন্ত্রী।",

    "Oversaw promulgation of the [[Meiji Constitution]]. Failed to secure revision of the [[Unequal treaty|unequal treaties]]; resigned.":
    "[[Meiji Constitution|মেইজি সংবিধান]] জারির তত্ত্বাবধান করেন। [[Unequal treaty|অসম চুক্তি]] সংশোধনে ব্যর্থ হয়ে পদত্যাগ করেন।",

    "Upon the resignation of Kuroda’s government, the [[Emperor Meiji|Emperor]] only accepted Kuroda’s resignation and invited Sanjō to head the government for two more months. Today, however, Sanjō’s government is generally regarded as a continuation of Kuroda’s. Held concurrently by the [[Lord Keeper of the Privy Seal of Japan|Lord Keeper of the Privy Seal]].":
    "কুরোদা সরকারের পদত্যাগের পর [[Emperor Meiji|সম্রাট মেইজি]] কেবল কুরোদার পদত্যাগপত্র গ্রহণ করেন এবং সানজোকে আরও দুই মাসের জন্য সরকারের নেতৃত্ব দেওয়ার আমন্ত্রণ জানান। তবে বর্তমানে সানজোর সরকারকে মূলত কুরোদা সরকারের ধারাবাহিকতা হিসেবেই গণ্য করা হয়। একই সাথে [[Lord Keeper of the Privy Seal of Japan|প্রিভি সিলের লর্ড কিপার]] হিসেবেও দায়িত্ব পালন করেন।",

    "Resigned.":
    "পদত্যাগ করেন।",

    "Assassinated.":
    "আততায়ীর হাতে নিহত হন।",

    "Resigned after the “Grand Coalition of the Three Pro-Constitution Parties” collapsed. Katō was then reinvited by the [[Hirohito#Early life|Prince Regent]] to form a new government with his own party, Kenseitō. Today, however, his second term is generally regarded as continuation of his first. Died in office of natural causes.":
    "\"সংবিধানপন্থি তিন দলের মহাজোট\" ভেঙে যাওয়ার পর পদত্যাগ করেন। এরপর অভিভাবক যুবরাজ [[Hirohito#Early life|হিরোহিতো]] কর্তৃক কাতো তাঁর নিজস্ব দল কেনসেইতোর সাথে নতুন সরকার গঠনের জন্য পুনরায় আমন্ত্রিত হন। তবে বর্তমানে তাঁর দ্বিতীয় মেয়াদকে মূলত প্রথম মেয়াদের ধারাবাহিকতা হিসেবে গণ্য করা হয়। দায়িত্বে থাকাকালীন স্বাভাবিক কারণে মৃত্যুবরণ করেন।",

    "Incapacitated due to serious wound from assassination plot on 14 November 1930. Foreign Minister [[Kijūrō Shidehara|Shidehara Kijūrō]] served as Deputy Prime Minister until Hamaguchi’s return to the office on 10 March 1931.":
    "১৪ নভেম্বর ১৯৩০ সালে হত্যা প্রচেষ্টায় গুরুতরভাবে আহত হয়ে কর্মক্ষমতা হারান। ১০ মার্চ ১৯৩১ সালে হামাগুচি দায়িত্বে ফিরে না আসা পর্যন্ত পররাষ্ট্রমন্ত্রী [[Kijūrō Shidehara|শিদেহরা কিজুরো]] উপ-প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।",

    "Thought to be killed by renegade soldiers during the [[February 26 Incident]]. Interior Minister [[Fumio Gotō|Gotō Fumio]] served as Deputy Prime Minister until Okada was found alive on 28 February 1936.":
    "[[February 26 Incident|২৬ ফেব্রুয়ারির ঘটনায়]] বিদ্রোহী সেনাদের হাতে নিহত হয়েছেন বলে ধারণা করা হয়েছিল। ২৮ ফেব্রুয়ারি ১৯৩৬ সালে ওকাদা জীবিত উদ্ধার না হওয়া পর্যন্ত স্বরাষ্ট্রমন্ত্রী [[Fumio Gotō|গোতো ফুমিও]] উপ-প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।",

    "The only member of the Imperial Family to serve as Prime Minister.":
    "প্রধানমন্ত্রী হিসেবে দায়িত্ব পালনকারী রাজপরিবারের একমাত্র সদস্য।",

    # 1. 片山哲 (Katayama Tetsu)
    "Under [[Occupation of Japan|Allied Occupation]]. The first prime minister and the first socialist to serve as Prime Minister of Japan. Member of Diet from 1930 to 1963. Formed a coalition government with the [[Democratic Party (Japan, 1947)|Democratic Party]] and the [[National Cooperative Party]].":
    "[[Occupation of Japan|মিত্রবাহিনীর দখলদারিত্বের]] অধীন। জাপানের প্রথম সমাজতান্ত্রিক প্রধানমন্ত্রী। ১৯৩০ থেকে ১৯৬৩ সাল পর্যন্ত ডায়েট সদস্য। [[Democratic Party (Japan, 1947)|ডেমোক্রেটিক পার্টি]] এবং [[National Cooperative Party|ন্যাশনাল কোঅপারেটিভ পার্টির]] সাথে একটি জোট সরকার গঠন করেন।",

    # 2. 芦田均 (Ashida Hitoshi)
    "Under [[Occupation of Japan|Allied Occupation]]. Ashida's cabinet resigned after seven months in office, due to alleged ministerial corruption in the Showa Electric scandal.":
    "[[Occupation of Japan|মিত্রবাহিনীর দখলদারিত্বের]] অধীন। শোওয়া ডেনকো কেলেঙ্কারিতে মন্ত্রিপরিষদের দুর্নীতির অভিযোগের কারণে মাত্র সাত মাস দায়িত্ব পালনের পর আশিদার মন্ত্রিসভা পদত্যাগ করে।",

    # 3. 吉田茂 (Yoshida Shigeru)
    "Under [[Occupation of Japan|Allied Occupation]] until the [[Treaty of San Francisco]] came into force on 28 April 1952. Developed the [[Yoshida Doctrine]], prioritising economic development and reliance on [[United States]] military protection.":
    "২৮ এপ্রিল ১৯৫২ সালে [[Treaty of San Francisco|সান ফ্রান্সিসকো চুক্তি]] কার্যকর হওয়া পর্যন্ত [[Occupation of Japan|মিত্রবাহিনীর দখলদারিত্বের]] অধীন। [[Yoshida Doctrine|ইয়োশিদা মতবাদ]] প্রণয়ন করেন, যা অর্থনৈতিক উন্নয়ন এবং [[United States|মার্কিন যুক্তরাষ্ট্রের]] সামরিক সুরক্ষার ওপর অগ্রাধিকার দেয়।",

    # 4. 鳩山一郎 (Hatoyama Ichirō)
    "Rebuilt diplomatic ties with the [[Soviet Union]]. Favored parole for some of the Class A war criminals who had been sentenced to life imprisonment at the [[Tokyo Trial]].":
    "[[Soviet Union|সোভিয়েত ইউনিয়নের]] সাথে কূটনৈতিক সম্পর্ক পুনঃপ্রতিষ্ঠা করেন। [[Tokyo Trial|টোকিও বিচারে]] যাবজ্জীবন কারাদণ্ডপ্রাপ্ত কিছু 'ক্লাস এ' যুদ্ধাপরাধীদের প্যারোলে মুক্তির পক্ষে অবস্থান নেন।",

    # 5. 石橋湛山 (Ishibashi Tanzan)
    "Incapacitated due to minor stroke on 31 January 1957. Foreign Minister [[Nobusuke Kishi|Kishi Nobusuke]] served as Deputy Prime Minister until 25 February 1957.":
    "৩১ জানুয়ারি ১৯৫৭ সালে মৃদু স্ট্রোকের কারণে কর্মক্ষমতা হারান। পররাষ্ট্রমন্ত্রী [[Nobusuke Kishi|কিশি নোবুসুকে]] ২৫ ফেব্রুয়ারি ১৯৫৭ পর্যন্ত ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।",

    # 6. 田中角榮 (Tanaka Kakuei)
    'resigned in the midst of scandal. Later, "[[shadow shogun]]".':
    'কেলেঙ্কারির মুখে পদত্যাগ করেন। পরবর্তীতে "[[shadow shogun|ছায়া শোগুন]]" হিসেবে পরিচিত।',

    # 7. 大平正芳 (Ōhira Masayoshi)
    "Died in office of natural causes.":
    "দায়িত্বে থাকাকালীন স্বাভাবিক কারণে মৃত্যুবরণ করেন।",

    # 8. 竹下登 (Takeshita Noboru)
    'The [[Recruit scandal]] forced his resignation in 1989. Later "Shadow Shogun."':
    '১৯৮৯ সালে [[Recruit scandal|রিক্রুট কেলেঙ্কারির]] কারণে পদত্যাগ করতে বাধ্য হন। পরবর্তীতে "ছায়া শোগুন" হিসেবে খ্যাত হন।',

    # 9. 宇野宗佑 (Uno Sōsuke)
    "Soon after he was elected Prime Minister, allegations arose that he had an extramarital relationship with a geisha, which damaged his reputation and his party's bad performance in the [[Japanese House of Councillors election, 1989|1989 House of Councillors election]], for which he resigned. Served as [[Minister of Defense (Japan)|Minister of Defense]] (1974), [[Ministry of Education, Culture, Sports, Science and Technology|Chief of the Science and Technology Agency]] (1976–1977), [[Chief of the Civil Administration Agency]] (1979–1980), [[Minister of Economy, Trade and Industry (Japan)|Minister of Economy, Trade and Industry]] (1983), and [[Minister for Foreign Affairs (Japan)|Minister for Foreign Affairs]] (1987–1989). Member of the Diet from 1960 to 1996.":
    "প্রধানমন্ত্রী নির্বাচিত হওয়ার পরপরই এক গেইশার সাথে বিবাহবহির্ভূত সম্পর্কের অভিযোগ ওঠে, যা তাঁর খ্যাতি ক্ষুণ্ণ করে এবং [[Japanese House of Councillors election, 1989|১৯৮৯ সালের কাউন্সিলর সভা নির্বাচনে]] দলের পরাজয় ডেকে আনে, যার ফলে তিনি পদত্যাগ করেন। তিনি [[Minister of Defense (Japan)|প্রতিরক্ষামন্ত্রী]] (১৯৭৪), বিজ্ঞান ও প্রযুক্তি সংস্থার প্রধান (১৯৭৬–১৯৭৭), বেসামরিক প্রশাসন সংস্থার প্রধান (১৯৭৯–১৯৮০), [[Minister of Economy, Trade and Industry (Japan)|বাণিজ্য ও শিল্পমন্ত্রী]] (১৯৮৩) এবং [[Minister for Foreign Affairs (Japan)|পররাষ্ট্রমন্ত্রী]] (১৯৮৭–১৯৮৯) হিসেবে দায়িত্ব পালন করেন। ১৯৬০ থেকে ১৯৯৬ সাল পর্যন্ত ডায়েট সদস্য ছিলেন।",

    # 10. 海部俊樹 (Kaifu Toshiki)
    "Defeated in 2009, he was the longest-serving member of the lower house of the Diet, and he was also the first former prime minister to be defeated at a re-election since 1963. Served as Deputy Chief Cabinet Secretary (1974–1976), [[Ministry of Education, Culture, Sports, Science and Technology|Minister of Education]] (1976–1977, 1985–1986). Member of the Diet from 1960 to 2009.":
    "২০০৯ সালে পরাজিত হন, তিনি ডায়েটের নিম্নকক্ষের দীর্ঘতম দায়িত্ব পালনকারী সদস্য ছিলেন এবং ১৯৬৩ সালের পর তিনিই প্রথম প্রাক্তন প্রধানমন্ত্রী যিনি নির্বাচনে পরাজিত হন। তিনি উপ-প্রধান মন্ত্রিপরিষদ সচিব (১৯৭৪–১৯৭৬) ও [[Ministry of Education, Culture, Sports, Science and Technology|শিক্ষামন্ত্রী]] (১৯৭৬–১৯৭৭, ১৯৮৫–১৯৮৬) হিসেবে দায়িত্ব পালন করেন। ১৯৬০ থেকে ২০০৯ পর্যন্ত ডায়েট সদস্য ছিলেন।",

    # 11. 宮澤喜一 (Miyazawa Kiichi)
    "Originally a bureaucrat in the Treasury Ministry, he accompanied Prime Minister [[Shigeru Yoshida]] at the [[Treaty of San Francisco]]. A firm critic of the revision of the constitution, he advocated peace throughout his political career. After his party's stunning defeat in the [[Japanese general election, 1993|1993 general election]], he was forced to resign the prime ministership, but became minister of finance in the cabinet of [[Keizo Obuchi]] and [[Yoshiro Mori]] from 1998 to 2001. He died in 2007. Served as [[Minister of Economy, Trade and Industry (Japan)|Minister of Economy, Trade and Industry]] (1962–1964, 1966–1968, 1970–1971, 1977–1978), [[Chief Cabinet Secretary]] (1980–1982), [[Minister of Finance (Japan)|Minister of Finance]] (1986–1988), [[Minister of Posts and Telecommunications (Japan)|Minister of Posts and Telecommunications]] (1993) and [[Minister of Agriculture, Forestry and Fisheries (Japan)|Minister of Agriculture, Forestry and Fisheries]] (1993). Member of the [[House of Councillors]] (1952–1965). Member of the [[House of Representatives of Japan|House of Representatives]] (1967–2003).":
    "মূলত অর্থ মন্ত্রণালয়ের একজন আমলা ছিলেন, তিনি [[Treaty of San Francisco|সান ফ্রান্সিসকো চুক্তিতে]] প্রধানমন্ত্রী [[Shigeru Yoshida|শিগেরু ইয়োশিদার]] সফরসঙ্গী ছিলেন। সংবিধান সংশোধনের কড়া সমালোচক ছিলেন এবং রাজনৈতিক জীবনজুড়ে শান্তির পক্ষে কথা বলেছেন। [[Japanese general election, 1993|১৯৯৩ সালের সাধারণ নির্বাচনে]] দলের পরাজয়ের পর পদত্যাগ করেন, তবে ১৯৯৮ থেকে ২০০১ পর্যন্ত [[Keizo Obuchi|কেইজো ওবুচি]] ও [[Yoshiro Mori|ইয়োশিরো মোরির]] মন্ত্রিসভায় অর্থমন্ত্রী ছিলেন। ২০০৭ সালে মৃত্যুবরণ করেন।",

    # 12. 細川護熙 (Hosokawa Morihiro)
    "He is a member of a noble family that ruled Kumamoto since Medieval times, and during Imperial Japan, his family was part of the aristocracy, his grandfather [[Konoe Fumimaro]] having served as Prime Minister (1937–1939, 1940–1941). Originally member of the [[Liberal Democratic Party (Japan)|Liberal Democratic Party]], he left the party in 1992 to form the [[Japan New Party]], which garnered 35 members in the [[Japanese general election, 1993|1993 general election]]. He served as Prime Minister in 8-party coalition government and spearheaded a reform to change the electoral system. He resigned after allegations arose that he had misused personal funds in the 1980s. Served as Governor of [[Kumamoto Prefecture]] (1983–1991). Member of the [[House of Councilors]] from 1971 to 1983 and 1992 to 1993. Member of the [[House of Representatives of Japan|House of Representatives]] from 1993 to 1998.":
    "মধ্যযুগ থেকে কুমামোতো শাসনকারী অভিজাত পরিবারের সদস্য, তাঁর পিতামহ [[Konoe Fumimaro|কোনোয়ে ফুমিমারো]] প্রধানমন্ত্রী ছিলেন (১৯৩৭–১৯৩৯, ১৯৪০–১৯৪১)। ১৯৯২ সালে এলডিপি ত্যাগ করে [[Japan New Party|জাপান নিউ পার্টি]] গঠন করেন এবং ১৯৯৩ সালের নির্বাচনে ৩৫টি আসন পান। তিনি আট দলীয় জোট সরকারের নেতৃত্ব দেন এবং নির্বাচনী সংস্কার সাধন করেন। ব্যক্তিগত অর্থ অপব্যবহারের অভিযোগে পদত্যাগ করেন। [[Kumamoto Prefecture|কুমামোতো প্রশাসনিক অঞ্চলের]] গভর্নর (১৯৮৩–১৯৯১) ছিলেন।",

    # 13. 羽田孜 (Hata Tsutomu)
    "Originally member of the [[Liberal Democratic Party (Japan)|Liberal Democratic Party]], he left the party in 1993 with [[Ichirō Ozawa]] to establish the [[Japan Renewal Party]], which garnered 44 seats in the [[Japanese general election, 1993|1993 general election]]. He served as minister for foreign affairs in the cabinet of [[Morihiro Hosokawa]], until the latter resigned after his implication in a banking scandal. Hata then assumed the prime ministership, but since the [[Socialist Party of Japan|Socialist Party]] had left the coalition, his minority government was forced to resign in two months as a non-confidence motion against his cabinet was submitted to the House of Representatives. Currently a member of the [[Democratic Party (Japan, 1998)|Democratic Party of Japan]], he is now one of the elder politicians of the party. Served as [[Minister of Agriculture, Forestry and Fisheries (Japan)|minister of agriculture, forestry and fisheries]] (1985–1986, 1988–1989), [[Minister of Finance (Japan)|minister of finance]] (1991–1992), and [[Minister for Foreign Affairs (Japan)|minister for foreign affairs]]. Member of the Diet from 1969 to 2012.":
    "১৯৯৩ সালে [[Ichirō Ozawa|ইচিরো ওজাওয়ার]] সাথে এলডিপি ত্যাগ করে [[Japan Renewal Party|জাপান রিনিউয়াল পার্টি]] গঠন করেন। হোসাকাওয়ার পদত্যাগের পর প্রধানমন্ত্রী হন, কিন্তু সমাজতান্ত্রিক দল জোট ত্যাগ করায় মাত্র দুই মাসের মাথায় অনাস্থা প্রস্তাব আসার মুখে পদত্যাগ করতে বাধ্য হন।",

    # 14. 村山富市 (Murayama Tomiichi)
    "Presided over a coalition that consisted of the [[Liberal Democratic Party (Japan)|Liberal Democratic Party]], the [[Socialist Party of Japan|Socialist Party]], and the [[New Party Sakigake]]. During his tenure, the [[Great Hanshin earthquake]] erupted and a [[Sarin gas attack on the Tokyo subway]] occurred that left 13 dead. He resigned after his party suffered defeat in the [[Japanese general election, 1996|1996 general election]]. Served as General Secretary of the [[Socialist Party of Japan|Socialist Party]]. Member of the Diet from 1972 to 2000.":
    "এলডিপি, সমাজতান্ত্রিক দল এবং নিউ পার্টি সাকিগাকের সমন্বয়ে গঠিত জোট সরকারের নেতৃত্ব দেন। তাঁর মেয়াদকালে [[Great Hanshin earthquake|গ্রেট হানশিন ভূমিকম্প]] এবং [[Sarin gas attack on the Tokyo subway|টোকিও পাতালরেলে সারিন গ্যাস হামলা]] ঘটে। ১৯৯৬ সালের নির্বাচনে দলের পরাজয়ের পর পদত্যাগ করেন।",

    # 15. 橋本龍太郎 (Hashimoto Ryūtarō)
    "He spearheaded widespread reforms during his tenure, including reforms to restructure the health, finance, and the bureaucratic system. He resigned after his party suffered massive defeat in the 1998 House of Councilors Election. He died in 2006. Served as [[Minister of Health]] (1978–1979), [[Minister of Transportation]] (1986–1987), [[Minister of Finance (Japan)|Minister of Finance]] (1989–1991), [[Minister of Economy, Trade and Industry (Japan)|Minister of Economy, Trade and Industry]] (1994–1996). Member of the Diet from 1963 to 2005.":
    "স্বাস্থ্য, অর্থ এবং প্রশাসনিক ব্যবস্থার ব্যাপক সংস্কার সাধন করেন। ১৯৯৮ সালের কাউন্সিলর সভা নির্বাচনে দলের বিপর্যয়ের পর পদত্যাগ করেন। ২০০৬ সালে মৃত্যুবরণ করেন।",

    # 16. 小渕恵三 (Obuchi Keizō)
    "His government was credited with stimulating the economy after a depression caused by the bubble crash. After suffering from a stroke, he fell into a coma on 3 April, and died on 14 May 2000. Chief Cabinet Secretary [[Mikio Aoki|Aoki Mikio]] served as Deputy Prime Minister until 5 April. Served as [[Chief of the Okinawa Development Agency]] (1979–1980), Minister of the Prime Minister's Office (1979–1980), [[Chief Cabinet Secretary]] (1987–1989), and [[Minister for Foreign Affairs (Japan)|Minister for Foreign Affairs]] (1997–1998). Member of the Diet from 1963 to 2000.<!-- Note: Obuchi was brain dead by the morning of 3 April but did not leave the office until the 5th. -->":
    "অর্থনৈতিক মন্দা কাটিয়ে তুলতে ভূমিকা রাখেন। স্ট্রোক করার পর কোমায় চলে যান এবং ১৪ মে ২০০০ সালে মৃত্যুবরণ করেন। প্রধান মন্ত্রিপরিষদ সচিব [[Mikio Aoki|আওকি মিকিও]] ৫ এপ্রিল পর্যন্ত ভারপ্রাপ্ত প্রধানমন্ত্রী ছিলেন।<!-- Note: Obuchi was brain dead by the morning of 3 April but did not leave the office until the 5th. -->",

    # 17. 森喜朗 (Mori Yoshirō)
    "His appointment was decided after a secret meeting by major power brokers within the Liberal Democratic Party after the unexpected death of Prime Minister [[Keizo Obuchi]]. His gaffes and his government's low legitimacy was detrimental to his government's approval ratings, for which he resigned in 2001. Served as [[Ministry of Education, Culture, Sports, Science and Technology|Minister of Education]] (1983–1984), [[Minister of Economy, Trade and Industry (Japan)|Minister of Economy, Trade and Industry]] (1992–1993), [[Minister of Construction]] (1995–1996). Member of the Diet from 1969 to 2012.":
    "প্রধানমন্ত্রী [[Keizo Obuchi|কেইজো ওবুচির]] মৃত্যুর পর এলডিপির শীর্ষ নেতাদের গোপন বৈঠকে তাঁর নিয়োগ চূড়ান্ত হয়। নানা বিতর্কিত মন্তব্য ও জনপ্রিয়তা হ্রাসের কারণে ২০০১ সালে পদত্যাগ করেন।",

    # 18. 小泉純一郎 (Koizumi Jun'ichirō)
    "Resigned due to term limits of the Presidency of the Liberal Democratic Party. Served as Vice Minister of Finance (1979), [[Minister of Health and Welfare (Japan)|Minister of Health and Welfare]] (1988–1989), [[Ministry of Posts and Telecommunications (Japan)|Minister of Posts and Telecommunications]] (1992), [[Ministry of Health, Labour and Welfare (Japan)|Minister of Health and Welfare]] (1996–1998), and [[Minister of Foreign Affairs (Japan)|Minister of Foreign Affairs]] (2002). Member of Diet from 1972 to 2009.":
    "এলডিপির দলীয় সভাপতি পদের মেয়াদ শেষ হওয়ায় পদত্যাগ করেন। ডাক ব্যবস্থার বেসরকারিকরণসহ ব্যাপক সংস্কার করেন। ১৯৭২ থেকে ২০০৯ পর্যন্ত ডায়েট সদস্য ছিলেন।",

    # 19. 安倍晋三 (Abe Shinzō 1)
    "Resigned after suffering from low approval ratings and poor health. Served as [[Chief Cabinet Secretary]] (2005–2006). Member of Diet since 1993.":
    "কম জনপ্রিয়তা ও ভগ্ন স্বাস্থ্যের কারণে পদত্যাগ করেন। ২০০৫–২০০৬ সালে [[Chief Cabinet Secretary|প্রধান মন্ত্রিপরিষদ সচিব]] ছিলেন।",

    # 20. 福田康夫 (Fukuda Yasuo)
    "Resigned after asserting the need to improve the flow of the political process. Served as Minister for Okinawa Development (2000), [[Chief Cabinet Secretary]] (2000–2004), and Minister of State for Gender Equality and Social Affairs (2001–2004). Member of Diet from 1990 to 2012.":
    "রাজনৈতিক প্রক্রিয়া গতিশীল করার প্রয়োজনীয়তা ব্যক্ত করে পদত্যাগ করেন। ২০০০–২০০৪ সালে প্রধান মন্ত্রিপরিষদ সচিব ছিলেন।",

    # 21. 麻生太郎 (Asō Tarō)
    "Resigned after the [[Japanese general election, 2009|2009 general election]] to accept the responsibility for the worst defeat of the history of the Liberal Democratic Party. Served as Director of Economic Planning Agency (1996–1997), Minister in charge of Economic and Financial Policies (2001), [[Minister of Internal Affairs and Communications]] (2003–2005), [[Minister of Foreign Affairs (Japan)|Minister of Foreign Affairs]] (2005–2007), and Deputy Prime Minister and [[Minister of Finance (Japan)|Minister of Finance]] (since 2012). Member of Diet since 1979.":
    "[[Japanese general election, 2009|২০০৯ সালের সাধারণ নির্বাচনে]] এলডিপির ঐতিহাসিক পরাজয়ের দায়ভার কাঁধে নিয়ে পদত্যাগ করেন। পরবর্তীতে উপ-প্রধানমন্ত্রী ও অর্থমন্ত্রী হিসেবে দায়িত্ব পালন করেন।",

    # 22. 鳩山由紀夫 (Hatoyama Yukio)
    "Won a majority in the [[Japanese general election, 2009|2009 general election]] defeating [[Tarō Asō]] (LDP). Resigned after breaking a campaign promise to close [[Marine Corps Air Station Futenma]] in [[Okinawa Prefecture]]. Member of Diet from 1986 to 2012.":
    "[[Japanese general election, 2009|২০০৯ সালের সাধারণ নির্বাচনে]] [[Tarō Asō|তারো আসোকে]] পরাজিত করে বিপুল সংখ্যাগরিষ্ঠতা অর্জন করেন। [[Okinawa Prefecture|ওকিনাওয়ার]] [[Marine Corps Air Station Futenma|ফুতেনমা বিমানঘাঁটি]] অপসারণের প্রতিশ্রুতি ভঙ্গ করায় পদত্যাগ করেন।",

    # 23. 菅直人 (Kan Naoto)
    "Resigned due to poor approval ratings after the [[2011 Tōhoku earthquake and tsunami]] and [[Fukushima Daiichi nuclear disaster]]. Served as [[Ministry of Health, Labour and Welfare (Japan)|Minister of Health and Welfare]] (1996), Deputy Prime Minister of Japan (2009–2010), Minister of State for Economic and Fiscal Policy (2009–2010), Minister of State in charge of National Strategy (2009–2010), [[Ministry of Education, Culture, Sports, Science and Technology|Minister of State for Science and Technology Policy]] (2009–2010), and [[Minister of Finance (Japan)|Minister of Finance]] (2010). Member of Diet since 1980.":
    "[[2011 Tōhoku earthquake and tsunami|২০১১ তোহোকু ভূমিকম্প ও সুনামি]] এবং [[Fukushima Daiichi nuclear disaster|ফুকুশিমা দাইচি পারমাণবিক বিপর্যয়ের]] পর জনপ্রিয়তা হ্রাস পাওয়ায় পদত্যাগ করেন।",

    # 24. 野田佳彦 (Noda Yoshihiko)
    "Resigned after the [[Japanese general election, 2012|2012 general election]] to accept the responsibility for the defeat of the Democratic Party. Served as Senior Vice Minister of Finance (2009–2010) and [[Minister of Finance (Japan)|Minister of Finance]] (2010–2011). Member of Diet since 1993.":
    "[[Japanese general election, 2012|২০১২ সালের সাধারণ নির্বাচনে]] ডেমোক্রেটিক পার্টির পরাজয়ের দায় নিয়ে পদত্যাগ করেন। ২০১০–২০১১ সালে অর্থমন্ত্রী হিসেবে দায়িত্ব পালন করেন।",

    # 25. 安倍晋三 (Abe Shinzō 2)
    "The first prime minister to serve non-consecutive terms since the end of the US occupation. Won a majority in the [[Japanese general election, 2012|2012 general election]] defeating [[Yoshihiko Noda]] (DPJ). Won the [[Japanese general election, 2014|2014]] and [[Japanese general election, 2017|2017]] general elections retaining a majority in the [[House of Representatives (Japan)|House of Representatives]]. Served as the 90th term Prime Minister (2006–2007), [[Chief Cabinet Secretary]] (2005–2006). Member of Diet from 1993 until his death in 2022. Resigned as Prime Minister in 2020":
    "মার্কিন দখলদারিত্বের পর তিনিই প্রথম প্রধানমন্ত্রী যিনি পুনরায় অ-ধারাবাহিক মেয়াদে ফিরে আসেন। ২০১২, ২০১৪ ও ২০১৭ সালের নির্বাচনে বিজয়ী হয়ে দীর্ঘতম মেয়াদে দায়িত্ব পালন করেন। স্বাস্থ্যের অবনতি হওয়ায় ২০২০ সালে পদত্যাগ করেন। ২০২২ সালে আততায়ীর গুলিতে নিহত হন।",

    # 26. 菅義偉 (Suga Yoshihide)
    "He became Prime Minister of Japan after his selection as Leader of the LDP. He served before as the  [[Chief Cabinet Secretary]] (2012–2020). Member of Diet since 1996. Resigned as Prime Minister in 2021":
    "এলডিপির সভাপতি নির্বাচিত হওয়ার পর জাপানের প্রধানমন্ত্রী হন। ইতিপূর্বে ২০১২–২০২০ সাল পর্যন্ত দীর্ঘমেয়াদে [[Chief Cabinet Secretary|প্রধান মন্ত্রিপরিষদ সচিব]] হিসেবে দায়িত্ব পালন করেন। ২০২১ সালে পদত্যাগ করেন।",

    # 27. 岸田文雄 (Kishida Fumio)
    "Kishida is the current prime minister of Japan. Won a majority in the [[2021 Japanese general election|2021 general election]] defeating [[Yukio Edano]] (CDP). He served before  as the [[Minister for Foreign Affairs (Japan)|Minister for Foreign Affairs]] (2012–2017). Member of Diet since 1996.":
    "কিশিদা জাপানের তৎকালীন প্রধানমন্ত্রী। [[2021 Japanese general election|২০২১ সালের সাধারণ নির্বাচনে]] সংখ্যাগরিষ্ঠতা লাভ করেন। ২০১২–২০১৭ সাল পর্যন্ত [[Minister for Foreign Affairs (Japan)|পররাষ্ট্রমন্ত্রী]] ছিলেন।",
}

ACTING_PM_NOTES = [
    (r"During this interval, the Chairman of the Privy Council \[\[Kuroda Kiyotaka\]\] was acting prime minister\.",
     "এই অন্তর্বর্তীকালে প্রিভি কাউন্সিলের চেয়ারম্যান [[Kuroda Kiyotaka|কুরোদা কিওতাকা]] ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।"),
    (r"During this interval, \[\[Saionji Kinmochi\]\] was acting prime minister\.",
     "এই অন্তর্বর্তীকালে [[Saionji Kinmochi|সায়নজি কিনমোচি]] ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।"),
    (r"During this interval, the Minister of Foreign Affairs \[\[Uchida Kōsai\]\] was acting prime minister\.",
     "এই অন্তর্বর্তীকালে পররাষ্ট্রমন্ত্রী [[Uchida Kōsai|উচিদা কোসাই]] ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।"),
    (r"During this interval, the Minister of the Interior \[\[Wakatsuki Reijirō\]\] was acting prime minister\.",
     "এই অন্তর্বর্তীকালে স্বরাষ্ট্রমন্ত্রী [[Wakatsuki Reijirō|ওয়াকাৎসুকি রেইজিরো]] ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।"),
    (r"During this interval, the Minister of Finance \[\[Takahashi Korekiyo\]\] was acting prime minister\.",
     "এই অন্তর্বর্তীকালে অর্থমন্ত্রী [[Takahashi Korekiyo|তাকাহাশি কোরেকিয়ো]] ভারপ্রাপ্ত প্রধানমন্ত্রী হিসেবে দায়িত্ব পালন করেন।"),
]
