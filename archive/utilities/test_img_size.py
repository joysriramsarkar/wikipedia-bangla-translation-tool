import urllib.request, urllib.parse, json, re

samples = [
    '[[চিত্র:Example.jpg|থাম্ব|300px|টেস্ট]]',
    '[[চিত্র:Example.jpg|থাম্ব|300পিক্সেল|টেস্ট]]',
    '[[চিত্র:Example.jpg|থাম্ব|৩০০পিক্সেল|টেস্ট]]',
    '[[চিত্র:Example.jpg|থাম্ব|300x300px|টেস্ট]]',
    '[[চিত্র:Example.jpg|থাম্ব|৩০০x৩০০পিক্সেল|টেস্ট]]',
    '[[চিত্র:Example.jpg|থাম্ব|300x300পিক্সেল|টেস্ট]]'
]

url = 'https://bn.wikipedia.org/w/api.php'

for s in samples:
    data = urllib.parse.urlencode({
        'action': 'parse',
        'text': s,
        'contentmodel': 'wikitext',
        'format': 'json'
    }).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'AntigravityMediaWikiBot/1.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            res = json.loads(resp.read().decode('utf-8'))
            html = res['parse']['text']['*']
            m = re.search(r'width="(\d+)"', html)
            w = m.group(1) if m else 'NOT PARSED / DEFAULT'
            # Also check if caption is treated as caption or param
            caption_m = re.findall(r'thumbcaption">(.*?)</div>', html, re.DOTALL)
            cap = caption_m[0].strip() if caption_m else ''
            print(f'{s} -> width: {w} | caption: {cap[:30]}')
    except Exception as e:
        print(f'{s} -> error: {e}')
