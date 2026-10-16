# -*- coding: utf-8 -*-
import re
from build_translation import transliterate_phonetic, transliterate_word

test_titles = [
    'Uptown Girl', 'Winged Warfare', 'Skyward', 'Record Flights', 'Speed',
    'The Fun of It', 'Wind in the Wires', 'Thirty Seconds Over Tokyo',
    'Enemy Coast Ahead', 'Bomber Offensive', 'Serenade to the Big Bird',
    'Global Mission', 'Visibility Unlimited', 'So Away I Went!',
    'The Lonely Sky', 'Wing Leader', 'Mission Completed', 'Baa Baa Black Sheep',
    'Thunderbolt!', 'Chickenhawk', 'The Day I Owned the Sky',
    'A WASP Among Eagles: A Woman Military Test Pilot in World War II',
    'Yes, Chef: A Memoir', 'See You in the Morning',
    'Frontier Follies: Adventures in Marriage and Motherhood in the Middle of Nowhere',
    'And the Answer Is...Reflections on My Life', 'Justice for the Judge'
]

TITLE_WORDS = {
    'The': 'দ্য', 'the': 'দ্য', 'Of': 'অব', 'of': 'অব', 'My': 'মাই', 'my': 'মাই',
    'Life': 'লাইফ', 'life': 'লাইফ', 'A': 'আ', 'a': 'আ', 'And': 'অ্যান্ড', 'and': 'অ্যান্ড',
    'I': 'আই', 'Autobiography': 'অটোবায়োগ্রাফি', 'In': 'ইন', 'in': 'ইন', 'To': 'টু', 'to': 'টু',
    'Me': 'মি', 'me': 'মি', 'It': 'ইট', 'it': 'ইট', 'Story': 'স্টোরি', 'story': 'স্টোরি',
    'An': 'অ্যান', 'an': 'অ্যান', 'Years': 'ইয়ার্স', 'years': 'ইয়ার্স', 'You': 'ইউ', 'you': 'ইউ',
    'From': 'ফ্রম', 'from': 'ফ্রম', 'Memoirs': 'মেমোয়ার্স', 'Memoir': 'মেমোয়ার',
    'Is': 'ইজ', 'is': 'ইজ', 'Pilot': 'পাইলট', 'All': 'অল', 'all': 'অল', 'On': 'অন', 'on': 'অন',
    'One': 'ওয়ান', 'one': 'ওয়ান', 'Fighter': 'ফাইটার', 'Man': 'ম্যান', 'World': 'ওয়ার্ল্ড',
    'War': 'ওয়ার', 'Hollywood': 'হলিউড', 'With': 'উইথ', 'with': 'উইথ', 'For': 'ফর', 'for': 'ফর',
    'Day': 'ডে', 'Days': 'ডেস', 'Night': 'নাইট', 'Nights': 'নাইটস', 'Girl': 'গার্ল',
    'Boy': 'বয়', 'Uptown': 'আপটাউন', 'Speed': 'স্পিড', 'Skyward': 'স্কাইওয়ার্ড',
    'Winged': 'উইংড', 'Warfare': 'ওয়ারফেয়ার', 'Fun': 'ফান', 'Wind': 'উইন্ড',
    'Wires': 'ওয়্যারস', 'Record': 'রেকর্ড', 'Flights': 'ফ্লাইটস', 'Flight': 'ফ্লাইট',
    'Flying': 'ফ্লাইং', 'Fly': 'ফ্লাই', 'Flew': 'ফ্লু', 'Corps': 'কোর', 'Royal': 'রয়্যাল',
    'Five': 'ফাইভ', 'Wanted': 'ওয়ান্টেড', 'Wings': 'উইংস', 'High': 'হাই', 'Wide': 'ওয়াইড',
    'Frightened': 'ফ্রাইটেন্ড', 'Last': 'লাস্ট', 'Enemy': 'এনিমি', 'West': 'ওয়েস্ট',
    'Thirty': 'থার্টি', 'Seconds': 'সেকেন্ডস', 'Over': 'ওভার', 'Tokyo': 'টোকিও',
    'Ahead': 'অ্যাহেড', 'Coast': 'কোস্ট', 'Bomber': 'বোম্বার', 'Offensive': 'অফেন্সিভ',
    'Serenade': 'সেরেনেড', 'Big': 'বিগ', 'Bird': 'বার্ড', 'Global': 'গ্লোবাল',
    'Mission': 'মিশন', 'Way': 'ওয়ে', 'General': 'জেনারেল', 'Reports': 'রিপোর্টস',
    'Personal': 'পার্সোনাল', 'History': 'হিস্ট্রি', 'Pacific': 'প্যাসিফিক',
    'Visibility': 'ভিজিবিলিটি', 'Unlimited': 'আনলিমিটেড', 'Away': 'অ্যাওয়ে', 'Went': 'ওয়েন্ট',
    'Show': 'শো', 'First': 'ফার্স্ট', 'Stormy': 'স্টর্মি', 'Führer': 'ফুয়েরার',
    'Sea': 'সি', 'Fleet': 'ফ্লিট', 'Arm': 'আর্ম', 'Slide': 'স্লাইড', 'Rule': 'রুল',
    'Engineer': 'ইঞ্জিনিয়ার', 'Lonely': 'লোনলি', 'Sky': 'স্কাই', 'Leader': 'লিডার',
    'Central': 'সেন্ট্রাল', 'Blue': 'ব্লু', 'Recollections': 'রিকলেকশনস',
    'Reflections': 'রিফ্লেকশনস', 'Completed': 'কমপ্লিটেড', 'Black': 'ব্ল্যাক',
    'Sheep': 'শিপ', 'Thunderbolt': 'থান্ডারবোল্ট', 'Forever': 'ফরএভার',
    'Air': 'এয়ার', 'Force': 'ফোর্স', 'Space': 'স্পেস', 'Time': 'টাইম',
    'Love': 'লাভ', 'Good': 'গুড', 'Bad': 'ব্যাড', 'True': 'ট্রু',
    'False': 'ফলস', 'Never': 'নেভার', 'Again': 'অ্যাগেইন', 'Back': 'ব্যাক',
    'Home': 'হোম', 'Heart': 'হার্ট', 'Soul': 'সোল', 'Mind': 'মাইন্ড',
    'Body': 'বডি', 'Frontier': 'ফ্রন্টিয়ার', 'Follies': 'ফলিজ', 'Answer': 'অ্যানসার',
    'Justice': 'জাস্টিস', 'Judge': 'জাজ', 'Shot': 'শট', 'Chef': 'শেফ',
    'Morning': 'মর্নিং', 'Middle': 'মিডল', 'Nowhere': 'নোহোয়ার', 'Marriage': 'ম্যারিজ',
    'Motherhood': 'মাদারহুড', 'Adventures': 'অ্যাডভেঞ্চার্স', 'Among': 'অ্যামং',
    'Eagles': 'ঈগলস', 'Woman': 'উইমেন', 'Military': 'মিলিটারি', 'Test': 'টেস্ট',
    'Two': 'টু', 'Red': 'রেড', 'Owned': 'ওনড', 'Chickenhawk': 'চিকেনহক',
    'Baa': 'বা', 'So': 'সো', 'See': 'সি', 'Yes': 'ইয়েস'
}

def transliterate_title_to_bn(title):
    tokens = re.split(r'(\s+|[.,:;!?\(\)\'\"\-–—])', title)
    out = []
    for t in tokens:
        if not t or t.isspace() or re.match(r'^[.,:;!?\(\)\'\"\-–—]+$', t):
            out.append(t)
        else:
            if t in TITLE_WORDS:
                out.append(TITLE_WORDS[t])
            elif t.capitalize() in TITLE_WORDS:
                out.append(TITLE_WORDS[t.capitalize()])
            else:
                out.append(transliterate_word(t))
    return ''.join(out)

for tit in test_titles:
    print(f"{tit} -> {transliterate_title_to_bn(tit)}")
