# -*- coding: utf-8 -*-
"""CLI আচরণের টেস্ট (নীতিমালা যাচাই ও আউটপুট)।"""
import contextlib
import io
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import cli  # noqa: E402


def _write(path, text):
    with open(path, 'w', encoding='utf-8') as handle:
        handle.write(text)


def _run(argv):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = cli.main(argv)
    return code, buffer.getvalue()


def test_check_rules_only_reads_input():
    with tempfile.TemporaryDirectory() as folder:
        path = os.path.join(folder, 'draft.txt')
        _write(path, '== তালিকা ==\n{| class="wikitable"\n! ক !! খ\n|-\n| ১ ||\n|}\n')
        code, out = _run(['english', '-i', path, '--check-rules'])
    assert code == 0
    assert 'নীতিমালা যাচাই রিপোর্ট' in out
    assert 'নিয়ম ৬' in out
    assert '⚠️' in out


def test_check_rules_after_translation_validates_output():
    with tempfile.TemporaryDirectory() as folder:
        src = os.path.join(folder, 'source.txt')
        dst = os.path.join(folder, 'output.txt')
        _write(src, '== Early life ==\nBorn in 2020.\n')
        code, out = _run(['english', '-i', src, '-o', dst, '--check-rules'])
        with open(dst, encoding='utf-8') as handle:
            translated = handle.read()
    assert code == 0
    assert 'অনূদিত ফলাফল' in out
    assert '২০২০' in translated


def test_missing_input_returns_error():
    code, out = _run(['english', '-i', 'no_such_file_12345.txt', '--check-rules'])
    assert code == 1
    assert 'পাওয়া যায়নি' in out
