#!/usr/bin/env python3
"""Local demo preview with MP4 byte-range support and a GitHub Pages prefix."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
import argparse, re
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
    def translate_path(self,path):
        if path.startswith('/sobi-packaging/'):
            path=path[len('/sobi-packaging'):]
        return super().translate_path(path)
    def send_head(self):
        self.byte_range=None
        path=Path(self.translate_path(self.path))
        request_range=self.headers.get('Range')
        if path.is_file() and request_range:
            match=re.fullmatch(r'bytes=(\d*)-(\d*)',request_range.strip())
            if match and (match[1] or match[2]):
                size=path.stat().st_size
                start=int(match[1]) if match[1] else max(0,size-int(match[2]))
                end=min(int(match[2]),size-1) if match[1] and match[2] else size-1
                if start>=size or start>end:
                    self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.send_header('Content-Length','0');self.end_headers();return None
                handle=path.open('rb');handle.seek(start);self.byte_range=(start,end)
                self.send_response(206);self.send_header('Content-type',self.guess_type(str(path)))
                self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length',str(end-start+1));self.end_headers();return handle
        return super().send_head()
    def copyfile(self,source,outputfile):
        if self.byte_range:
            remaining=self.byte_range[1]-self.byte_range[0]+1
            try:
                while remaining:
                    chunk=source.read(min(65536,remaining))
                    if not chunk:break
                    outputfile.write(chunk);remaining-=len(chunk)
            except (BrokenPipeError,ConnectionResetError):pass
        else:
            try:super().copyfile(source,outputfile)
            except (BrokenPipeError,ConnectionResetError):pass
    def send_error(self,code,message=None,explain=None):
        if code==404 and (ROOT/'404.html').is_file():
            page=(ROOT/'404.html').read_bytes()
            self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(page)));self.end_headers()
            if self.command!='HEAD':self.wfile.write(page)
        else:super().send_error(code,message,explain)
    def end_headers(self):
        self.send_header('Cache-Control','no-cache');super().end_headers()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=4173);args=parser.parse_args()
    print(f'Sobi demo: http://127.0.0.1:{args.port}/',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
