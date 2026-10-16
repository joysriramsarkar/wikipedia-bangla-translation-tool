#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Clean __pycache__ and pyc files"""
import os
import shutil

def clean():
    # Remove .pytest_cache
    if os.path.exists('.pytest_cache'):
        shutil.rmtree('.pytest_cache', ignore_errors=True)
    
    for root, dirs, files in os.walk('.'):
        # Remove __pycache__
        for d in dirs[:]:
            if d in ('__pycache__', '.pytest_cache'):
                shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                dirs.remove(d)
        # Remove pyc/pyo files
        for f in files:
            if f.endswith(('.pyc', '.pyo', '.py.class')):
                try:
                    os.remove(os.path.join(root, f))
                except OSError:
                    pass
    print("Cleaned cache files and .pytest_cache")

if __name__ == '__main__':
    clean()
