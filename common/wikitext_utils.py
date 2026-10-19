# -*- coding: utf-8 -*-
"""
Wikitext formatting and table utilities for Bengali Wikipedia
"""
import re

from .bengali_utils import to_bengali_digits


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


def _split_cells(line, separator):
    """Split a table line on ``separator`` outside ``[[...]]`` and ``{{...}}``.

    ``[[The Godfather|দ্য গডফাদার]] || 1972`` must yield two cells, not three.
    """
    parts = []
    buffer = []
    link_depth = 0
    template_depth = 0
    i = 0
    length = len(line)

    while i < length:
        pair = line[i:i + 2]
        if pair == '[[':
            link_depth += 1
            buffer.append('[[')
            i += 2
            continue
        if pair == ']]':
            link_depth = max(0, link_depth - 1)
            buffer.append(']]')
            i += 2
            continue
        if pair == '{{':
            template_depth += 1
            buffer.append('{{')
            i += 2
            continue
        if pair == '}}':
            template_depth = max(0, template_depth - 1)
            buffer.append('}}')
            i += 2
            continue
        if link_depth == 0 and template_depth == 0 and line.startswith(separator, i):
            parts.append(''.join(buffer))
            buffer = []
            i += len(separator)
            continue
        buffer.append(line[i])
        i += 1

    parts.append(''.join(buffer))
    return parts


def analyze_wikitable(text):
    """Check wikitable structure (Rule 6: equal columns, no empty cells).

    Returns a dict::

        {
          'tables': 1,
          'rows': 2,
          'header_cols': 4,
          'issues': [
            {'type': 'column_count', 'line': 5, 'count': 3,
             'expected': 4, 'message': '...'},
            {'type': 'empty_cell', 'line': 7, 'column': 4, 'message': '...'},
          ],
        }

    Cells are counted per row (lines between ``|-`` markers); cells that are
    empty are reported because Bengali Wikipedia requires ``&nbsp;`` there.
    Rows using ``colspan`` are skipped for the column check, since they are
    legitimately shorter.
    """
    report = {'tables': 0, 'rows': 0, 'header_cols': None, 'issues': []}
    lines = text.splitlines()

    in_table = False
    header_cols = None
    current_row = None

    def finish_row(row):
        if row is None:
            return
        report['rows'] += 1
        if (header_cols and row['cells'] != header_cols
                and not row['colspan']):
            report['issues'].append({
                'type': 'column_count',
                'line': row['line'],
                'count': row['cells'],
                'expected': header_cols,
                'message': (f"সারিতে {to_bengali_digits(str(row['cells']))}টি ঘর, "
                            f"হেডারে {to_bengali_digits(str(header_cols))}টি "
                            f"— কলাম অসামঞ্জস্য"),
            })
        for column in row['empty']:
            if row['colspan']:
                continue
            report['issues'].append({
                'type': 'empty_cell',
                'line': row['line'],
                'column': column,
                'message': f"{to_bengali_digits(str(column))} নম্বর ঘরটি খালি — &nbsp; ব্যবহার করুন",
            })

    for number, raw in enumerate(lines, 1):
        line = raw.rstrip()

        if not in_table:
            if line.startswith('{|'):
                in_table = True
                report['tables'] += 1
                header_cols = None
                current_row = None
            continue

        if line.startswith('|}'):
            finish_row(current_row)
            current_row = None
            in_table = False
            continue

        if line.startswith('|-'):
            finish_row(current_row)
            current_row = None
            continue

        if line.startswith('|+'):
            continue  # table caption

        if line.startswith('!'):
            cells = _split_cells(line[1:], '!!')
            if header_cols is None:
                header_cols = len(cells)
                report['header_cols'] = header_cols
            else:
                header_cols += len(cells)
                report['header_cols'] = header_cols
            continue

        if line.startswith('|'):
            cells = _split_cells(line[1:], '||')
            if current_row is None:
                current_row = {'line': number, 'cells': 0, 'empty': [],
                               'colspan': False}
            for index, cell in enumerate(cells, start=current_row['cells'] + 1):
                if not cell.strip():
                    current_row['empty'].append(index)
            current_row['cells'] += len(cells)
            if 'colspan' in line:
                current_row['colspan'] = True
            continue

        # Continuation text of the previous cell: nothing to count.

    if in_table:  # unclosed table
        finish_row(current_row)
        report['issues'].append({
            'type': 'unclosed_table',
            'line': len(lines),
            'message': 'সারণি |} দিয়ে বন্ধ করা হয়নি',
        })

    return report
