#!/usr/bin/env python3
"""Validate exported pages, local links, assets and HTTP byte ranges."""
from pathlib import Path
from urllib.parse import urlsplit,unquote,urljoin
from urllib.request import urlopen,Request
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
BASE='http://localhost:4173/'
failures=[];references=0
pages=sorted(ROOT.rglob('*.html'))
for page in pages:
    doc=BeautifulSoup(page.read_text(),'html.parser')
    if len(doc.select('h1'))!=1:failures.append(f'{page.relative_to(ROOT)}: expected one H1')
    if not doc.select_one('meta[name=robots][content*=noindex]'):failures.append(f'{page}: missing demo noindex')
    for tag in doc.find_all(True):
        for attr in ('href','src','poster','action','data-video-src'):
            value=tag.get(attr,'');parsed=urlsplit(value)
            if parsed.hostname in ('localhost','127.0.0.1') or 'wp-admin' in value:failures.append(f'{page}: runtime URL {value}')
            if not value or value.startswith('#') or parsed.scheme or parsed.netloc:continue
            target=(page.parent/unquote(parsed.path)).resolve();references+=1
            if not target.is_file():failures.append(f'{page.relative_to(ROOT)}: missing {value}')
        if tag.get('srcset'):
            for candidate in tag['srcset'].split(','):
                value=candidate.strip().split()[0];target=(page.parent/unquote(urlsplit(value).path)).resolve();references+=1
                if not target.is_file():failures.append(f'{page}: missing srcset {value}')
    for style in doc.find_all('style'):
        for value in re.findall(r'url\([\'\"]?(.*?)[\'\"]?\)',style.get_text()):
            if urlsplit(value).scheme:continue
            references+=1
            if not (page.parent/unquote(value)).resolve().is_file():failures.append(f'{page}: missing background {value}')
for css in ROOT.rglob('*.css'):
    for value in re.findall(r'url\([\'\"]?(.*?)[\'\"]?\)',css.read_text()):
        if value.startswith(('data:','#')):continue
        if urlsplit(value).scheme:failures.append(f'{css}: external dependency {value}');continue
        references+=1
        if not (css.parent/unquote(urlsplit(value).path)).resolve().is_file():failures.append(f'{css}: missing {value}')
def check_http(page):
    with urlopen(BASE+str(page.relative_to(ROOT)),timeout=15) as response:
        return response.status
with ThreadPoolExecutor(max_workers=5) as pool:statuses=list(pool.map(check_http,pages))
if any(status!=200 for status in statuses):failures.append('Some HTML pages do not return HTTP 200')
video=next(ROOT.rglob('*.mp4'));request=Request(BASE+str(video.relative_to(ROOT)),headers={'Range':'bytes=0-1023'})
with urlopen(request) as response:
    video_status=response.status;video_bytes=len(response.read());content_range=response.headers.get('Content-Range')
if video_status!=206 or video_bytes!=1024:failures.append('MP4 byte-range support failed')
video_source=Path('/Applications/XAMPP/sobi-packaging/website/wp-content/uploads/2026/11/sobi-san-xuat-1080p.mp4')
video_hash_matches=hashlib.sha256(video.read_bytes()).digest()==hashlib.sha256(video_source.read_bytes()).digest()
if not video_hash_matches:failures.append('Video differs from source')
report={'date':'2026-11-17','html_pages':len(pages),'local_references_checked':references,'all_pages_http_200':all(s==200 for s in statuses),'mp4_range':{'http':video_status,'bytes':video_bytes,'content_range':content_range,'matches_original':video_hash_matches},'site_bytes':sum(p.stat().st_size for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts),'failures':failures}
(ROOT/'docs/static-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(failures))
