#!/usr/bin/env python3
"""Check navigation, local assets and public-page invariants before a release."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
PUBLIC=['index.html','presentation.html','epistemologie.html','typologie.html','recherches.html','travaux.html','publications.html','ressources.html','explorations.html','accessibilite.html']

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.ids=[]; self.refs=[]; self.meta={}; self.mains=0; self.h1s=0
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if d.get('id'): self.ids.append(d['id'])
        if tag in ['a','link'] and d.get('href'): self.refs.append(d['href'])
        if tag in ['img','script'] and d.get('src'): self.refs.append(d['src'])
        if tag=='meta': self.meta[d.get('name')]=d.get('content')
        if tag=='main': self.mains+=1
        if tag=='h1': self.h1s+=1

errors=[]
pages={p:Page((DOCS/p).read_text()) for p in PUBLIC}
for name,p in pages.items():
    if p.mains!=1: errors.append(f'{name}: expected exactly one main landmark')
    if p.h1s<1: errors.append(f'{name}: missing page title')
    if p.meta.get('robots')!='noindex,follow': errors.append(f'{name}: test site must be marked noindex')
    if not p.meta.get('hyperion-version'): errors.append(f'{name}: missing release version')
    duplicate=[id for id,count in Counter(p.ids).items() if count>1]
    if duplicate: errors.append(f'{name}: duplicate IDs {duplicate}')
    for ref in p.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc: continue
        if ref=='#': errors.append(f'{name}: placeholder link')
        target=(DOCS/name).parent/unquote(url.path) if url.path else DOCS/name
        target=target.resolve()
        if target.is_dir(): target=target/'index.html'
        if not target.exists(): errors.append(f'{name}: missing {ref}'); continue
        if url.fragment and target.suffix=='.html':
            other=pages.get(str(target.relative_to(DOCS))) or Page(target.read_text())
            if unquote(url.fragment) not in other.ids: errors.append(f'{name}: missing fragment {ref}')
data=json.loads((DOCS/'data/publications.json').read_text())
if len(data['publications'])!=7: errors.append('Expected seven verified references')
for pub in data['publications']:
    if not pub.get('source','').startswith('https://'): errors.append('Publication lacks a public source')
    if not pub.get('links'): errors.append('Publication lacks a reading link')
    if not pub.get('year') or not pub.get('authors'): errors.append('Incomplete publication metadata')
for script in (DOCS/'assets').glob('*.js'):
    result=subprocess.run(['node','--check',str(script)],capture_output=True,text=True)
    if result.returncode: errors.append(result.stderr)
for path in DOCS.rglob('*.html'):
    if path.name.startswith('.qa-'): continue
    content=Page(path.read_text())
    for ref in content.refs:
        url=urlsplit(ref)
        if url.scheme or url.netloc or not url.path: continue
        # Historical page navigation remains experimental; all local media must exist.
        if Path(url.path).suffix.lower() not in ['.js','.css','.png','.svg','.jpg','.webp']: continue
        if not (path.parent/unquote(url.path)).resolve().exists(): errors.append(f'{path.relative_to(DOCS)}: missing asset {ref}')
for name in PUBLIC:
    html=(DOCS/name).read_text()
    if 'docs.google.com' in html or 'mail.google.com' in html: errors.append(f'{name}: private workspace link in public page')
    if 'sysadmin@huma-num' in html: errors.append(f'{name}: administrative access details must not be published')
if errors:
    for error in errors: print('ERROR:',error)
    raise SystemExit(1)
print(f'PASS: {len(PUBLIC)} public pages; local links, fragments, assets, metadata and JavaScript syntax.')
print(f'PASS: {len(data["publications"])} bibliographic references with public provenance.')
