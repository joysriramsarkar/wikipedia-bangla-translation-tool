# -*- coding: utf-8 -*-
"""
CX পোস্ট-প্রসেসরের সংখ্যা রূপান্তর — এখন কেন্দ্রীয় বাস্তবায়নের পাতলা মোড়ক।

আগে এই ফাইলে আলাদা (প্রায় একই) সুরক্ষা-তালিকা ছিল; ফলে toolkit API আর
CX পাইপলাইন ভিন্ন ফল দিত। এখন একটাই বাস্তবায়ন:
``common.bengali_utils.to_bengali_digits_safe``।

সুরক্ষিত থাকে: HTML ট্যাগ/অ্যাট্রিবিউট, URL, File/Image নাম,
টেমপ্লেট প্যারামিটার কী (``|group1 =``, ``{{{1|...}}}``), coord,
ISBN/DOI/PMID, ``NNNpx`` মাপ, CSS রং, HTML এনটিটি।
দৃশ্যমান লেখা, টেবিল সেল ও ক্যাপশনের অঙ্ক বাংলা হয়; ক্রমবাচকও
(``2nd`` → ``২য়``, ``6th`` → ``৬ষ্ঠ``)।
"""
import os
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from common.bengali_utils import (  # noqa: E402  (path bootstrap first)
    BN_DIGITS,
    BN_TO_ASCII_DIGITS,
    convert_ordinals,
    fix_template_parameter_digits,
    to_bengali_digits_safe,
)

__all__ = [
    "BN_DIGITS",
    "BN_TO_ASCII_DIGITS",
    "convert_ordinals",
    "fix_template_parameter_digits",
    "to_bengali_digits_safe",
]
