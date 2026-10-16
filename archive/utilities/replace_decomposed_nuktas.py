# -*- coding: utf-8 -*-
import os

workspace_root = r'c:\Users\joysr\Documents\উইকিপিডিয়া অনুবাদ'

REPLACEMENTS = {
    '\u09af\u09bc': '\u09df',  # য় -> য়
    '\u09a1\u09bc': '\u09dc',  # ড় -> ড়
    '\u09a2\u09bc': '\u09dd',  # ঢ় -> ঢ়
}

def clean_text(text):
    for old_char, new_char in REPLACEMENTS.items():
        text = text.replace(old_char, new_char)
    return text

# 1. Rename files/dirs with decomposed nuktas (bottom-up so children renamed before parents)
renamed_items = []
for root, dirs, files in os.walk(workspace_root, topdown=False):
    if '.git' in root or '__pycache__' in root:
        continue
    for name in files + dirs:
        new_name = clean_text(name)
        if new_name != name:
            old_path = os.path.join(root, name)
            new_path = os.path.join(root, new_name)
            os.rename(old_path, new_path)
            renamed_items.append((name, new_name))

# 2. Clean contents of text files
modified_files = []
for root, dirs, files in os.walk(workspace_root):
    if '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if file.endswith(('.txt', '.py', '.json', '.md', '.wikitext', '.yaml', '.yml')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                new_content = content
                file_replacements = {}
                for old_char, new_char in REPLACEMENTS.items():
                    cnt = new_content.count(old_char)
                    if cnt > 0:
                        file_replacements[old_char] = cnt
                        new_content = new_content.replace(old_char, new_char)
                
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    rel_path = os.path.relpath(path, workspace_root)
                    modified_files.append((rel_path, file_replacements))
            except Exception as e:
                print(f'Error processing {path}: {e}')

if renamed_items:
    print(f'Renamed {len(renamed_items)} files/directories.')
    for old, new in renamed_items:
        print(f'  {old} -> {new}')

print(f'Done! Successfully updated content of {len(modified_files)} files.')
for fpath, reps in modified_files:
    rep_desc = ', '.join([f'{hex(ord(k[0]))}+{hex(ord(k[1]))} -> {hex(ord(REPLACEMENTS[k]))} ({reps[k]} times)' for k in reps])
    print(f'{fpath:65} : {rep_desc}')
