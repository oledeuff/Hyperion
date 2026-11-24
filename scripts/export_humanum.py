#!/usr/bin/env python3
"""Prepare a portable Huma-Num release without connecting to the server."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
dirty = subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,text=True).strip()
if dirty:
    raise SystemExit('Enregistrer les modifications dans Git avant de préparer une version Huma-Num traçable.')
source = ROOT / 'docs'
output = ROOT / 'dist' / 'humanum'
if output.exists():
    shutil.rmtree(output)
shutil.copytree(source, output, ignore=shutil.ignore_patterns('.qa-*', '.DS_Store'))
for path in output.rglob('*.html'):
    html = path.read_text(encoding='utf-8')
    html = re.sub(r'<meta name="robots" content="noindex,follow">', '<meta name="robots" content="index,follow">', html)
    html = re.sub(r'<div class="test-notice">.*?</div>', '', html, flags=re.S)
    path.write_text(html, encoding='utf-8')
version = json.loads((output/'version.json').read_text())
version['environment'] = 'humanum'
version['source_commit'] = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
(output/'version.json').write_text(json.dumps(version,ensure_ascii=False,indent=2)+'\n')
archive = ROOT/'dist'/f"hyperion-humanum-{version['version']}.zip"
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as handle:
    for path in sorted(output.rglob('*')):
        if path.is_file(): handle.write(path,path.relative_to(output))
print(f'Release directory: {output}')
print(f'ZIP: {archive}')
print('No upload was performed. Upload the contents only after validating GitHub Pages.')
