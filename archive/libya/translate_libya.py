# -*- coding: utf-8 -*-
import re

def to_bn_digits(s):
    t = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
    return str(s).translate(t)

# Let's inspect the evolution table rows and prepare them properly
