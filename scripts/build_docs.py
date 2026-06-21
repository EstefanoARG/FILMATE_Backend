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

def _process_rst_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        txt = f.read()
    new_txt = []
    for line in txt.splitlines():
        if line.strip().startswith('.. automodule::'):
            parts = line.split()
            if len(parts) >= 3:
                modname = parts[2]
                if '.' not in modname:
                    line = line.replace('.. automodule:: ' + modname,
                                        '.. automodule:: app.' + modname)
        line = line.replace('models.', 'app.models.')
        new_txt.append(line)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_txt))


def _fix_automodule_refs(api_src: str):
    for fname in os.listdir(api_src):
        if not fname.endswith('.rst'):
            continue
        _process_rst_file(os.path.join(api_src, fname))

def main():
    os.makedirs(DOCS_SRC, exist_ok=True)
    os.makedirs(API_SRC, exist_ok=True)
    cmd = [sys.executable, '-m', 'sphinx.ext.apidoc', '-f', '-o', API_SRC] + PACKAGES
    run(cmd, cwd=ROOT)
    _fix_automodule_refs(API_SRC)
    cmd2 = [sys.executable, '-m', 'sphinx', '-b', 'html', DOCS_SRC, BUILD_DIR]
    run(cmd2, cwd=ROOT)

if __name__ == '__main__':
    main()
