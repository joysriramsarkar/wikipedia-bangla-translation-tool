# -*- coding: utf-8 -*-
"""CX post-processor: সংখ্যা + মুদ্রা + টেবিল + ইনফোবক্স (Parsoid-HTML ও উইকিটেক্সট সচেতন)।"""
from .bn_digits_safe import to_bengali_digits_safe, convert_ordinals
from .infobox_map import translate_infobox, INFOBOX_NAME_MAP, PARAM_MAP
from .units_dates import fix_units_dates
from .template_fix import fix_templates, clean_templatestyles_remnants
from .currency_fix import fix_currency
from .table_fix import fix_tables, fix_table_block
from .pipeline import fix_text

__all__ = [
    "to_bengali_digits_safe",
    "convert_ordinals",
    "translate_infobox",
    "INFOBOX_NAME_MAP",
    "PARAM_MAP",
    "fix_units_dates",
    "fix_templates",
    "clean_templatestyles_remnants",
    "fix_currency",
    "fix_tables",
    "fix_table_block",
    "fix_text",
]
