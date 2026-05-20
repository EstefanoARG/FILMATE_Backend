#!/usr/bin/env python3
"""Simple helper to generate Sphinx API stubs and build HTML docs."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_SRC = os.path.join(ROOT, 'docs', 'source')
API_SRC = os.path.join(DOCS_SRC, 'api')
BUILD_DIR = os.path.join(ROOT, 'docs', '_build', 'html')

PACKAGES = ['app', 'app.models', 'repositories', 'routes', 'schemas', 'services', 'utils']

def run(cmd, **kwargs):
    print('> ' + ' '.join(cmd))
    subprocess.check_call(cmd, **kwargs)

def main():
    os.makedirs(DOCS_SRC, exist_ok=True)
    os.makedirs(API_SRC, exist_ok=True)
    # Generate rst files for the packages into docs/source/api
    cmd = [sys.executable, '-m', 'sphinx.ext.apidoc', '-f', '-o', API_SRC] + PACKAGES
    run(cmd, cwd=ROOT)

    # Post-process generated rst files: ensure modules are importable as 'app.<module>' when needed
    for fname in os.listdir(API_SRC):
        if not fname.endswith('.rst'):
            continue
        path = os.path.join(API_SRC, fname)
        with open(path, 'r', encoding='utf-8') as f:
            txt = f.read()

        # Prefix automodule targets without a dot (e.g. 'main') with 'app.'
        new_txt = []
        for line in txt.splitlines():
            if line.strip().startswith('.. automodule::'):
                parts = line.split()
                if len(parts) >= 3:
                    modname = parts[2]
                    if '.' not in modname:
                        line = line.replace('.. automodule:: ' + modname,
                                            '.. automodule:: app.' + modname)
            # also fix references to top-level 'models.' to 'app.models.'
            line = line.replace('models.', 'app.models.')
            new_txt.append(line)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_txt))

    # Build HTML
    cmd2 = [sys.executable, '-m', 'sphinx', '-b', 'html', DOCS_SRC, BUILD_DIR]
    run(cmd2, cwd=ROOT)

if __name__ == '__main__':
    main()
