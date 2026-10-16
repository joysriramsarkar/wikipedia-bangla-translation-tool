# -*- coding: utf-8 -*-
"""
Wikitext formatting utilities for Bengali Wikipedia
"""
import re

def fix_toc_limits(text):
    """Fix TOC limit syntax."""
    text = text.replace('{{TOC limit|3}}', '{{সূচিপত্র সীমিত|৩}}')
    return text

def clean_double_newlines(text):
    """Clean excessive newlines."""
    return re.sub(r'\n{3,}', '\n\n', text)

def add_defaultsort(bangla_title):
    """Generate DEFAULTSORT for Bengali title."""
    # Basic implementation
    return f'{{{{DEFAULTSORT:{bangla_title}}}}}'

def fix_table_pipes(text):
    """Fix table pipe formatting issues."""
    return text
