#!/usr/bin/env python3
"""Export public Sobi content; runtime output is plain HTML/CSS/JavaScript.
Optional regeneration: /tmp/sobi-demo-tools/bin/python tools/export_demo.py
Requires beautifulsoup4. Reads only public HTTP pages and public theme/media files.
"""
from pathlib import Path
from urllib.parse import urlsplit, urljoin, unquote, quote, parse_qs, urlencode
from urllib.request import urlopen
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import json, re, shutil, posixpath, datetime, hashlib, argparse

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--only', action='append', default=[], help='Export this route only; repeat for a batch. Preserve other page bodies and existing catalogue/blog data.')
selected_routes = set(parser.parse_args().only)

OUT = Path(__file__).resolve().parents[1]
SITE = 'http://sobi-packaging.test/'
RUNTIME = Path('/Applications/XAMPP/sobi-packaging/website')
THEME = RUNTIME / 'wp-content/themes/sobi-flatsome/assets'
MARKER = '__SOBI_ROOT__'
MEDIA = set()

def fetch(url):
    try:
        with urlopen(url, timeout=30) as response: return response.read().decode('utf-8')
    except HTTPError as error:
        if error.code == 404: return error.read().decode('utf-8')
        raise

def api(endpoint):
    return json.loads(fetch(SITE+'wp-json/wp/v2/'+endpoint+'?per_page=100'))

def soup(text): return BeautifulSoup(text, 'html.parser')
def route(url): return unquote(urlsplit(url).path.removeprefix('/sobi-packaging/')).strip('/')+'/' if urlsplit(url).path.removeprefix('/sobi-packaging/').strip('/') else ''

pages=api('pages'); posts=api('posts'); categories=api('categories')
categories=[c for c in categories if c['slug']!='uncategorized']
seed=['san-pham/','san-pham/?trang=2']+[route(c['link']) for c in categories]
with ThreadPoolExecutor(max_workers=4) as pool:
    seed_html=dict(zip(seed,pool.map(lambda p:fetch(SITE+p),seed)))
product_cards=[]
for key in seed[:2]: product_cards+=soup(seed_html[key]).select('.sobi-product-card')
product_routes=list(dict.fromkeys(route(c.select_one('a')['href']) for c in product_cards))
base_routes=list(dict.fromkeys([route(p['link']) for p in pages]+product_routes+[route(p['link']) for p in posts]+[route(c['link']) for c in categories]))
with ThreadPoolExecutor(max_workers=5) as pool:
    documents=dict(zip(base_routes,pool.map(lambda p:fetch(SITE+p),base_routes)))
error_html=fetch(SITE+'sobi-demo-missing-page/')
documents['404.html']=error_html
known=set(base_routes)|{'search/'}
if selected_routes - known:
    raise RuntimeError('Unknown export routes: '+', '.join(sorted(selected_routes - known)))

# Sobi assets only: no Flatsome parent runtime, WordPress JS or admin files.
shutil.copytree(THEME, OUT/'assets/theme', dirs_exist_ok=True, ignore=shutil.ignore_patterns('sobi.js','.DS_Store'))
(OUT/'assets/theme/sobi.js').unlink(missing_ok=True)
shutil.copyfile(RUNTIME/'wp-content/plugins/sobi-tables/assets/tables.css',OUT/'assets/css/tables.css')
js=(THEME/'sobi.js').read_text()
start=js.index("    form.addEventListener('submit', async (event) => {")
end=js.index('    if (inBuilder) {',start)
js=js[:start]+"    // Demo submissions are handled by demo.js without a network request.\n"+js[end:]
# Share the actual demo URL, including a GitHub project subpath.
js=js.replace('navigator.clipboard.writeText(button.dataset.copyUrl)', 'navigator.clipboard.writeText(location.href.split("?")[0])')
(OUT/'assets/js/sobi.js').write_text(js)

def relative_root(path):
    if path=='404.html' or not path:return './'
    return '../'*len(path.strip('/').split('/'))

def local_asset(url):
    parts=urlsplit(url)
    path=unquote(parts.path)
    if parts.netloc and parts.netloc!=urlsplit(SITE).netloc:return None
    if '/wp-content/themes/sobi-flatsome/assets/' in path:
        return 'assets/theme/'+path.split('/wp-content/themes/sobi-flatsome/assets/',1)[1]
    if '/wp-content/uploads/' in path:
        suffix=path.split('/wp-content/uploads/',1)[1]
        source=RUNTIME/'wp-content/uploads'/suffix
        if not source.is_file(): raise RuntimeError(f'Missing public media: {suffix}')
        target=OUT/'assets/media'/suffix
        target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists(): shutil.copyfile(source,target)
        MEDIA.add('assets/media/'+suffix)
        return 'assets/media/'+suffix
    return None

def rewrite_url(url,path='',template=False):
    if not url or url.startswith(('#','mailto:','tel:','data:')): return url
    if url.startswith('/') and not url.startswith('//'):
        url = SITE + url.lstrip('/').removeprefix('sobi-packaging/')
    prefix=MARKER if template else relative_root(path)
    asset=local_asset(url)
    if asset:return prefix+quote(asset,safe='/.-_')
    parts=urlsplit(url)
    if parts.netloc!=urlsplit(SITE).netloc:return url
    if not parts.path.startswith(urlsplit(SITE).path):return url
    dest=route(url);query=parts.query
    # Blog numbered URLs use the same HTML and browser-side pagination.
    m=re.search(r'^(.*?)/?page/(\d+)/$',dest)
    if m:
        dest=m.group(1).strip('/')+'/'
        q=parse_qs(query);q['trang']=[m.group(2)];query=urlencode(q,doseq=True)
    if dest not in known:
        if dest=='':pass
        elif dest.startswith(('wp-admin','wp-json')) or dest.endswith('.php'):return '#'
        else:return prefix+'404.html'
    result=prefix+(quote(dest,safe='/.-_') if dest else '')+'index.html'
    if query:result+='?'+query
    if parts.fragment:result+='#'+parts.fragment
    return result

def rewrite_tree(tree,path='',template=False):
    for tag in tree.find_all(True):
        for attr in ['href','src','poster','action','data-video-src','data-copy-url']:
            if tag.has_attr(attr):tag[attr]=rewrite_url(tag[attr],path,template)
        if tag.has_attr('srcset'):
            pieces=[]
            for entry in tag['srcset'].split(','):
                p=entry.strip().split()
                if p:pieces.append(rewrite_url(p[0],path,template)+(' '+p[1] if len(p)>1 else ''))
            tag['srcset']=', '.join(pieces)
        if tag.has_attr('style'):
            tag['style']=re.sub(r'url\([\'\"]?(.*?)[\'\"]?\)',lambda m:'url("'+rewrite_url(m.group(1),path,template)+'")',tag['style'])
    for style in tree.find_all('style'):
        style.string=re.sub(r'url\([\'\"]?(.*?)[\'\"]?\)',lambda m:'url("'+rewrite_url(m.group(1),path,template)+'")',style.get_text())
    return tree

# Gather cards from every category, so the Blog demo remains complete even if
# the source Blog shortcode currently has an empty context on its landing page.
blog_cards=[]
for c in categories:
    for card in soup(seed_html[route(c['link'])]).select('.sobi-blog-card'):
        blog_cards.append((card,c['slug']))
post_by_route={route(p['link']):p for p in posts}
products=[]
for i,card in enumerate(product_cards):
    r=route(card.select_one('a')['href'])
    title=card.select_one('h2,h3').get_text(' ',strip=True)
    category=card.select_one('.sobi-card-category').get_text(' ',strip=True)
    group={'Túi cửa sổ':'tui-cua-so','Túi giấy kraft':'tui-giay-kraft','Túi Ivory':'tui-ivory'}.get(category,'')
    products.append({'route':r,'title':title,'code':card.select_one('.sobi-product-code').get_text(strip=True),'category':group,'html':str(rewrite_tree(soup(str(card)),template=True))})
blogs=[]
for card,category in blog_cards:
    anchor=card.select_one('h2 a');r=route(anchor['href']);post=post_by_route[r]
    blogs.append({'route':r,'title':anchor.get_text(' ',strip=True),'category':category,'date':post['date'],'search':soup(post['content']['rendered']).get_text(' ',strip=True),'html':str(rewrite_tree(soup(str(card)),template=True))})
blogs.sort(key=lambda p:p['date'],reverse=True)
assert len(products)==9 and len(blogs)==18,(len(products),len(blogs))
search_entries=[]
for r,raw in documents.items():
    if r=='404.html':continue
    doc=soup(raw);main=doc.select_one('main');title=main.select_one('h1') if main else None
    if title:search_entries.append({'route':r,'title':title.get_text(' ',strip=True),'text':main.get_text(' ',strip=True)[:25000]})
data={'products':products,'posts':blogs,'categories':[{'slug':c['slug'],'name':c['name'],'route':route(c['link'])} for c in categories],'search':search_entries}
if selected_routes:
    previous=json.loads((OUT/'assets/js/data.js').read_text().split(' = ',1)[1].rstrip(';\n'))
    updates={entry['route']:entry for entry in search_entries if entry['route'] in selected_routes}
    previous['search']=[updates.pop(entry['route'],entry) for entry in previous['search']]+list(updates.values())
    data=previous
(OUT/'assets/js/data.js').write_text('window.SOBI_DATA = '+json.dumps(data,ensure_ascii=False).replace('<','\\u003c')+';\n')

# An extra native static search page supports site-wide search widgets.
search_doc=soup(documents[''])
search_doc.select_one('main').clear()
search_doc.select_one('main').append(soup('<section class="sobi-shell sobi-editorial"><p class="sobi-eyebrow">KHÁM PHÁ SOBI</p><h1>Tìm kiếm nội dung</h1><form class="sobi-demo-search" role="search"><label for="demo-site-search">Từ khóa</label><div class="sobi-demo-search-row"><input id="demo-site-search" name="s" type="search" placeholder="Chất liệu, mẫu túi, bài viết..."><button class="button primary" type="submit">Tìm kiếm</button></div></form><div id="demo-site-results" aria-live="polite"></div></section>'))
search_doc.title.string='Tìm kiếm nội dung | Sobi Packaging Demo'
documents['search/']=str(search_doc)

for r,raw in documents.items():
    if selected_routes and r not in selected_routes: continue
    doc=soup(raw)
    # Keep content-level builder styles; replace the CMS head/runtime entirely.
    title=doc.title.get_text() if doc.title else 'Sobi Packaging'
    description=doc.select_one('meta[name="description"]')
    description=description.get('content','') if description else ''
    for tag in doc.find_all('script'):tag.decompose()
    head=soup('<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><meta name="robots" content="noindex,nofollow"><meta name="color-scheme" content="light"></head>').head
    title_tag=doc.new_tag('title');title_tag.string=title+' · Demo';head.append(title_tag)
    head.append(doc.new_tag('meta',attrs={'name':'description','content':description}))
    head.append(doc.new_tag('meta',attrs={'name':'sobi-root','content':relative_root(r)}))
    head.append(doc.new_tag('meta',attrs={'name':'sobi-route','content':r}))
    for css in ['assets/css/base.css','assets/css/tables.css','assets/theme/sobi.css','assets/theme/conversion.css','assets/css/demo.css']:
        version = hashlib.sha256((OUT/css).read_bytes()).hexdigest()[:12]
        head.append(doc.new_tag('link',rel='stylesheet',href=relative_root(r)+css+'?v='+version))
    head.append(doc.new_tag('link',rel='icon',href=relative_root(r)+'assets/theme/images/sobi-site-icon.png'))
    if r=='404.html':
        bootstrap=doc.new_tag('script')
        bootstrap.string="const demoProject=location.pathname.split('/')[1];const demoBase=document.createElement('base');demoBase.href=new URL(['sobi-packaging','sobi-packaging-demo'].includes(demoProject)?'/'+demoProject+'/':'/',location.href).href;document.head.prepend(demoBase);"
        bootstrap.string="if(location.protocol!=='file:'){"+bootstrap.string+"}"
        head.insert(0,bootstrap)
    doc.head.replace_with(head)
    doc.html['lang']='vi'
    doc.body['class']=list(doc.body.get('class',[]))+['sobi-static-demo']
    # Reuse the public channels already present in the homepage content when
    # migrated Settings happen to render empty in the source header/footer.
    public_home=soup(documents[''])
    channels={}
    for anchor in public_home.select('.sobi-social-section a[href]'):
        value=anchor.get('href','')
        for channel,host in [('facebook','facebook.com'),('shopee','shopee.vn'),('tiktok','tiktok.com')]:
            if host in value:channels[channel]=value
    labels={'facebook':'Facebook','shopee':'Shopee','tiktok':'TikTok'}
    top=doc.select_one('.sobi-top-social')
    if top is not None and not top.select('a'):
        for channel,value in channels.items():
            top.append(soup('<a class="sobi-top-social-'+channel+'" href="'+value+'" target="_blank" rel="noopener noreferrer" aria-label="'+labels[channel]+'"><span class="sobi-top-social-icon" aria-hidden="true"></span><span class="sobi-top-social-label" aria-hidden="true">'+labels[channel]+'</span></a>'))
    # The hotline is explicitly documented and is already used by the Zalo CTA.
    if not doc.select_one('.sobi-header-hotline'):
        def hotline(placement):
            return soup('<a class="sobi-header-hotline sobi-header-hotline--'+placement+'" href="tel:0708010662" aria-label="Hotline 0708 010 662"><i class="icon-phone" aria-hidden="true"></i><span class="sobi-hotline-label">Hotline:</span><span>0708 010 662</span></a>')
        doc.select_one('.sobi-header-actions').insert(0,hotline('mainbar'))
        doc.select_one('.sobi-business-topbar .sobi-shell').append(hotline('mobile'))
    footer_social=doc.select_one('.sobi-footer-social')
    if footer_social is not None and not footer_social.select('a'):
        for channel,value in channels.items():
            footer_social.append(soup('<a href="'+value+'" class="sobi-top-social-'+channel+'" target="_blank" rel="noopener noreferrer" aria-label="'+labels[channel]+'"><span class="sobi-top-social-icon" aria-hidden="true"></span></a>'))
        footer_social.append(soup('<a href="https://zalo.me/0708010662" class="sobi-top-social-zalo" target="_blank" rel="noopener noreferrer" aria-label="Zalo"><span class="sobi-top-social-icon" aria-hidden="true"></span></a>'))
    for tag in doc.select('#wpadminbar, #main-menu, .post-edit-link, link, meta'):
        if tag.find_parent('head') is None:tag.decompose()
    # Rebuild missing Blog landing listing using public category card markup.
    if r=='blog/' and not doc.select_one('.sobi-blog-list'):
        target=doc.select_one('.sobi-blog-body .col-inner')
        listing=soup(seed_html[route(categories[0]['link'])]).select_one('.sobi-blog-list')
        target.append(listing)
    for avatar in doc.select('img.avatar'):
        avatar['src']=SITE+'wp-content/themes/sobi-flatsome/assets/images/sobi-logo.jpg'
        avatar.attrs.pop('srcset',None)
        avatar['alt']='Ảnh đại diện minh họa'
    for form in doc.select('.sobi-quote-form'):
        form['data-demo-form']='quote';form['action']='#';form['method']='get'
        for hidden in form.select('input[type="hidden"]'):hidden.decompose()
        for phone in form.select('[name="phone"]'):phone['pattern']=r'[+0-9 \(\)\-]{9,20}'
        note=doc.new_tag('p',attrs={'class':'sobi-demo-form-note'})
        note.string='Bản demo: thông tin và file chỉ được xử lý trên thiết bị của bạn, không gửi đến Sobi.'
        form.insert_before(note)
    if r in post_by_route and not doc.select_one('#commentform'):
        article=doc.select_one('main article')
        if article:
            article.append(soup('<section class="sobi-article-comments" id="comments"><h2>Bình luận</h2><p>Chia sẻ ý kiến của bạn</p><form id="commentform" class="comment-form"><p><label for="comment">Bình luận</label><textarea id="comment" name="comment" rows="5" maxlength="3000" required></textarea></p><p><label for="author">Tên hiển thị</label><input id="author" name="author" maxlength="100" required></p><p><label for="email">Email (không hiển thị)</label><input id="email" name="email" type="email" maxlength="160" required></p><button class="button primary" type="submit">Gửi bình luận thử</button></form></section>'))
    for form in doc.select('#commentform'):
        form['data-demo-form']='comment';form['action']='#';form['method']='get'
        for hidden in form.select('input[type="hidden"]'):hidden.decompose()
        for field in form.select('[name="author"], [name="email"]'):field['required']=''
        for field in form.select('.comment-form-cookies-consent'):field.decompose()
        note=doc.new_tag('p',attrs={'class':'sobi-demo-form-note'})
        note.string='Bình luận mô phỏng, chỉ hiển thị trong phiên xem này và không được đăng lên website thật.'
        form.insert_before(note)
    for form in doc.select('form.searchform'):
        form['action']=SITE+'search/'
    for title_el in doc.select('.accordion-title'):
        title_el.name='button';title_el['type']='button';title_el.attrs.pop('href',None)
        for toggle in title_el.select('button.toggle'):toggle.name='span'
        panel=doc.find(id=title_el.get('aria-controls'))
        if panel:panel['hidden']='';panel['role']='region'
    for text in doc.select('.sobi-article-byline'):
        # Public marketing demo does not need an internal WordPress login name.
        text.string=re.sub(r'Bởi .*? ·','Bởi Sobi ·',text.get_text(' ',strip=True))
    banner=doc.new_tag('aside',attrs={'class':'sobi-demo-banner','aria-label':'Thông tin bản demo'})
    banner.append(soup('<span><strong>DEMO GIAO DIỆN</strong> · Khám phá nội dung và trải nghiệm tương tác Sobi.</span><a href="'+SITE+'lien-he/#yeu-cau-bao-gia">Thử form báo giá <span aria-hidden="true">→</span></a>'))
    doc.body.insert(0,banner)
    rewrite_tree(doc,r)
    # Replace stale source-site URLs in third-party share parameters.
    for anchor in doc.select('.sobi-article-share a'):
        if 'facebook.com/sharer/' in anchor.get('href',''):
            anchor['data-demo-share']='facebook'
            anchor['href']='https://www.facebook.com/sharer/sharer.php'
    for jsfile in ['data.js','sobi.js','demo.js']:
        version=hashlib.sha256((OUT/'assets/js'/jsfile).read_bytes()).hexdigest()[:12]
        doc.body.append(doc.new_tag('script',src=relative_root(r)+'assets/js/'+jsfile+'?v='+version,defer=''))
    noscript=doc.new_tag('noscript');noscript.string='Bật JavaScript để dùng bộ lọc, menu và form mô phỏng. Nội dung trang vẫn có thể đọc trực tiếp.';doc.body.append(noscript)
    output=OUT/('404.html' if r=='404.html' else r+'index.html')
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(str(doc))

if selected_routes:
    # Shared navigation/styles change everywhere; preserve existing editorial bodies.
    native_menu=soup(documents['']).select_one('#sobi-mega')
    for output in OUT.rglob('*.html'):
        doc=soup(output.read_text())
        route_meta=doc.select_one('meta[name="sobi-route"]')
        if route_meta is None: continue
        r=route_meta['content']
        existing_menu=doc.select_one('#sobi-mega')
        if existing_menu:
            existing_menu.replace_with(rewrite_tree(soup(str(native_menu)),r))
        for link in doc.select('link[rel="stylesheet"]'):
            path=link['href'].split('?',1)[0]
            css=(output.parent/unquote(path)).resolve()
            link['href']=path+'?v='+hashlib.sha256(css.read_bytes()).hexdigest()[:12]
        for script in doc.select('script[src]'):
            path=script['src'].split('?',1)[0]
            asset=(output.parent/unquote(path)).resolve()
            if asset.is_file(): script['src']=path+'?v='+hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        output.write_text(str(doc))

(OUT/'.nojekyll').touch()
(OUT/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
manifest={'generated':'2026-11-17','source':SITE,'pages':[r+'index.html' if r!='404.html' else r for r in documents],'products':len(products),'blog_posts':len(blogs),'categories':len(categories),'media_files':len(MEDIA),'video':[{'file':str(p.relative_to(OUT)),'bytes':p.stat().st_size} for p in (OUT/'assets').rglob('*.mp4')],'source_blog_landing_rebuilt':not bool(soup(documents['blog/']).select_one('.sobi-blog-list'))}
(OUT/'docs/content-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({**manifest,'pages':len(manifest['pages'])},ensure_ascii=False,indent=2))
