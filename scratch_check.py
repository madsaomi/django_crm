import os
import glob

missing = []
for file in glob.glob('templates/**/*.html', recursive=True):
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        if '<div class="page-header' in content or '<h1 class="page-title' in content:
            if '{% extends' not in content:
                missing.append(file)

print('FILES MISSING EXTENDS:')
for f in missing:
    print(f)
