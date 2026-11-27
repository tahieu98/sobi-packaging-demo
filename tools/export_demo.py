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
export_mode = parser.add_mutually_exclusive_group()
export_mode.add_argument('--only', action='append', default=[], help='Export this route only; repeat for a batch. Preserve other page bodies and existing catalogue/blog data.')
export_mode.add_argument('--contacts-only', action='store_true', help='Refresh shared contact blocks from the public WordPress homepage.')
export_mode.add_argument('--sync-catalogue', action='store_true', help='Refresh the public catalogue, products and category navigation.')
export_mode.add_argument('--sync-audit', action='store_true', help='Refresh the shared layout, homepage and public quote form hints.')
parser.add_argument('--catalogue-routes', type=Path, help='Route manifest emitted by order-40-catalogue.php export.')
args = parser.parse_args()
route_manifest = json.loads(args.catalogue_routes.read_text(encoding='utf-8-sig')) if args.catalogue_routes else None
selected_routes = set(args.only)

OUT = Path(__file__).resolve().parents[1]
SITE = 'http://sobi-packaging.test/'
RUNTIME = Path('/Applications/XAMPP/sobi-packaging/website')
THEME = RUNTIME / 'wp-content/themes/sobi-flatsome/assets'
MARKER = '__SOBI_ROOT__'
MEDIA = set()

def fetch_bytes(url, allow_404=False):
    try:
        with urlopen(url, timeout=30) as response:
            return response.read()
    except HTTPError as error:
        if allow_404 and error.code == 404:
            return error.read()
        raise

def fetch(url):
    return fetch_bytes(url, allow_404=True).decode('utf-8')

def api(endpoint):
    return json.loads(fetch(SITE+'wp-json/wp/v2/'+endpoint+'?per_page=100'))

def soup(text): return BeautifulSoup(text, 'html.parser')


def render_static_html(doc):
    # Reparse after moving fragments so adjacent whitespace is serialized consistently.
    return str(soup(re.sub(r'(?m)^[ \t]+$', '', str(doc))))


def refresh_public_contacts():
    """Update shared contact markup without re-exporting pages or assets."""
    selectors = (
        '#header .sobi-business-info',
        '#header .sobi-header-hotline',
        '#footer .sobi-footer-contact',
        '#footer .sobi-footer-social',
    )
    homepage = soup(fetch(SITE))
    fragments = {}
    for selector in selectors:
        block = homepage.select_one(selector)
        if block is None or not block.get_text(strip=True):
            raise RuntimeError(f'Missing public contact markup: {selector}')
        for element in [block, *block.find_all(True)]:
            if element.name not in {'a', 'br', 'div', 'i', 'nav', 'p', 'span'}:
                raise RuntimeError(f'Unexpected element in {selector}: {element.name}')
            if set(element.attrs) - {'aria-hidden', 'aria-label', 'class', 'href', 'rel', 'target'}:
                raise RuntimeError(f'Unexpected contact attributes in {selector}')
            if element.name == 'a' and urlsplit(element.get('href', '')).scheme not in {'https', 'mailto', 'tel'}:
                raise RuntimeError(f'Unexpected contact link in {selector}')
        fragments[selector] = str(block)

    updated = {}
    for output in sorted(OUT.rglob('*.html')):
        raw = output.read_text(encoding='utf-8')
        doc = soup(raw)
        route_meta = doc.select_one('meta[name="sobi-route"]')
        if route_meta is None:
            continue
        for selector, fragment in fragments.items():
            block = doc.select_one(selector)
            if block is None:
                raise RuntimeError(f'Missing contact block in {output}: {selector}')
            block.replace_with(soup(fragment).find())
        sync_quick_contacts(doc, homepage, route_meta['content'])
        rendered = render_static_html(doc)
        if raw != rendered:
            updated[output] = rendered
    for output, rendered in updated.items():
        output.write_bytes(rendered.encode('utf-8'))
    print(f'Updated contact markup on {len(updated)} pages.')


def route(url): return unquote(urlsplit(url).path.removeprefix('/sobi-packaging/')).strip('/')+'/' if urlsplit(url).path.removeprefix('/sobi-packaging/').strip('/') else ''

PUBLIC_THEME = 'wp-content/themes/sobi-flatsome/assets/'
STYLE_FILES = ['assets/css/base.css', 'assets/css/tables.css', 'assets/theme/sobi.css',
               'assets/theme/conversion.css', 'assets/theme/header-audit.css',
               'assets/theme/quick-contact.css', 'assets/theme/home-audit.css', 'assets/css/demo.css']
SCRIPT_FILES = ['assets/js/data.js', 'assets/js/sobi.js', 'assets/theme/quick-contact.js', 'assets/js/demo.js']


def make_demo_script(js):
    start = js.index("    form.addEventListener('submit', async (event) => {")
    end = js.index('    if (inBuilder) {', start)
    js = js[:start] + '    // Demo submissions are handled by demo.js without a network request.\n' + js[end:]
    return js.replace('navigator.clipboard.writeText(button.dataset.copyUrl)',
                      'navigator.clipboard.writeText(location.href.split("?")[0])')

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
        target=OUT/'assets/media'/suffix
        if not target.exists():
            target.parent.mkdir(parents=True,exist_ok=True)
            if source.is_file():
                shutil.copyfile(source,target)
            elif args.sync_audit or args.sync_catalogue:
                target.write_bytes(fetch_bytes(SITE+'wp-content/uploads/'+quote(suffix,safe='/.-_')))
            else:
                raise RuntimeError(f'Missing public media: {suffix}')
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
    if route_manifest:
        target = route_manifest['aliases'].get(dest)
        fields = parse_qs(query, keep_blank_values=True)
        if dest == 'san-pham/' and fields.get('nhom'):
            target = route_manifest['groups'].get(fields['nhom'][0])
            if target:
                fields.pop('nhom', None)
                if fields.get('tim'):
                    fields['tim_mau'] = fields.pop('tim')
        if target:
            redirect = urlsplit(target)
            dest = redirect.path
            fields.update(parse_qs(redirect.query))
            query = urlencode(fields, doseq=True)
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
    tags = tree.find_all(True)
    if not isinstance(tree, BeautifulSoup):
        tags.insert(0, tree)
    for tag in tags:
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


def static_quote_forms(doc):
    for form in doc.select('.sobi-quote-form'):
        form['data-demo-form'] = 'quote'
        form['action'] = '#'
        form['method'] = 'get'
        for field in form.select('input[type="hidden"]'):
            field.unwrap()
        for honeypot in form.select('.sobi-honeypot'):
            honeypot.decompose()
        note = doc.new_tag('p', attrs={'class': 'sobi-demo-form-note'})
        note.string = 'Bản demo: thông tin và file chỉ được xử lý trên thiết bị của bạn, không gửi đến Sobi.'
        form.insert_before(note)


def copy_quote_hints(doc, source):
    for form, source_form in zip(doc.select('.sobi-quote-form'), source.select('.sobi-quote-form'), strict=True):
        for field in source_form.select('[name][placeholder], [name][pattern]'):
            target = form.find(attrs={'name': field['name']})
            for attribute in ('placeholder', 'pattern'):
                if field.has_attr(attribute):
                    target[attribute] = field[attribute]
        form.select_one('[name="province"] option[value=""]').string = source_form.select_one(
            '[name="province"] option[value=""]').get_text()


def stabilize_builder_ids(main, prefix='sobi-home-layout'):
    """Give generated layout IDs stable names and keep their inline styles."""
    ids = {}
    for element in main.find_all(id=re.compile(r'^(section_|image_|row-|col-|text-)\d+$')):
        source_id = element['id']
        static_id = f'{prefix}-{len(ids) + 1}'
        ids[source_id] = static_id
        element['id'] = static_id
    for style in main.find_all('style'):
        style.string = re.sub(r'#([\w-]+)', lambda match: '#' + ids.get(match[1], match[1]),
                              style.get_text())


def sync_quick_contacts(doc, source, path):
    back_top = doc.select_one('[data-back-top]')
    for old_bar in doc.select('.sobi-mobile-quote'):
        old_bar.decompose()
    for selector in ('[data-quick-desktop]', '[data-quick-mobile]'):
        existing = doc.select_one(selector)
        block = source.select_one(selector)
        if block:
            copy = rewrite_tree(soup(str(block)).find(), path)
            if existing:
                existing.replace_with(copy)
            else:
                back_top.insert_before(copy)
                back_top.insert_before('\n')
        elif existing:
            existing.decompose()


def versioned_asset(path, asset):
    version = hashlib.sha256((OUT/asset).read_bytes()).hexdigest()[:12]
    return relative_root(path) + asset + '?v=' + version


def install_assets(doc, path):
    icon = doc.head.select_one('link[rel="icon"]')
    noscript = doc.body.find('noscript', recursive=False)
    catalogue_styles = []
    if doc.select_one('.sobi-category-content, .sobi-product-detail, .sobi-catalog'):
        catalogue_styles = ['assets/theme/product-category.css', 'assets/theme/catalog-pages.css', 'assets/theme/ux-layouts.css']
    if doc.select_one('.sobi-archive, .sobi-catalogue-facets'):
        catalogue_styles.append('assets/theme/category-archive.css')
    for asset in [*STYLE_FILES, *catalogue_styles]:
        if asset.endswith('home-audit.css') and path:
            continue
        link = doc.new_tag('link', rel='stylesheet', href=versioned_asset(path, asset))
        if icon:
            icon.insert_before(link)
        else:
            doc.head.append(link)
    scripts = list(SCRIPT_FILES)
    if doc.select_one('.sobi-archive'):
        scripts.extend(['assets/js/category-archive.js', 'assets/theme/category-archive.js'])
    for asset in scripts:
        script = doc.new_tag('script', src=versioned_asset(path, asset), defer='')
        if noscript:
            noscript.insert_before(script)
        else:
            doc.body.append(script)


def sync_public_audit():
    """Update the audited public UI using the export's existing route map."""
    exports = {}
    for output in sorted(OUT.rglob('*.html')):
        doc = soup(output.read_text(encoding='utf-8'))
        route_meta = doc.select_one('meta[name="sobi-route"]')
        if route_meta:
            exports[route_meta['content']] = (output, doc)
    known.update(exports)
    # Share the homepage chrome on the demo-only search page.
    sources = {
        path: {'search/': '', '404.html': 'sobi-demo-missing-page/'}.get(path, path)
        for path in exports
    }
    source_paths = list(dict.fromkeys(sources.values()))
    with ThreadPoolExecutor(max_workers=5) as pool:
        snapshots = dict(zip(source_paths, pool.map(lambda path: soup(fetch(SITE+path)), source_paths)))

    for name in ('sobi.css', 'conversion.css', 'header-audit.css', 'quick-contact.css',
                 'home-audit.css', 'quick-contact.js', 'icons/messenger.svg', 'sobi.js'):
        content = fetch_bytes(SITE+PUBLIC_THEME+name)
        if name == 'sobi.js':
            (OUT/'assets/js/sobi.js').write_bytes(make_demo_script(content.decode('utf-8')).encode('utf-8'))
        else:
            (OUT/'assets/theme'/name).write_bytes(content.rstrip() + b'\n')

    # Homepage snippets should reflect the audited page in site-wide search.
    data_file = OUT/'assets/js/data.js'
    data = json.loads(data_file.read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
    native_main = snapshots[''].select_one('main')
    homepage = next(entry for entry in data['search'] if entry['route'] == '')
    homepage['title'] = native_main.select_one('h1').get_text(' ', strip=True)
    homepage['text'] = native_main.get_text(' ', strip=True)[:25000]
    data_file.write_bytes(('window.SOBI_DATA = ' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + ';\n').encode('utf-8'))

    rendered = {}
    for path, (output, doc) in exports.items():
        source = snapshots[sources[path]]
        for selector in ('#header', '#footer'):
            source_node = source.select_one(selector)
            if source_node is None:
                raise RuntimeError(f'Missing {selector} on public route {path}')
            fragment = soup(str(source_node)).find()
            doc.select_one(selector).replace_with(rewrite_tree(fragment, path))
        sync_quick_contacts(doc, source, path)

        if path == '':
            main = source.select_one('main')
            for tag in main.select('script, #wpadminbar, #main-menu, .post-edit-link, link, meta'):
                tag.decompose()
            static_quote_forms(source)
            stabilize_builder_ids(main)
            doc.select_one('main').replace_with(rewrite_tree(main, path))
        elif path == 'lien-he/':
            copy_quote_hints(doc, source)
        for tag in doc.select('head link[rel="stylesheet"], script[src]'):
            tag.decompose()
        install_assets(doc, path)
        rendered[output] = render_static_html(doc)

    for output, html in rendered.items():
        output.write_bytes(html.encode('utf-8'))
    print(f'Synchronized the public audit across {len(exports)} pages.')


def sync_catalogue():
    """Refresh category and product pages from the public site and keep the demo shell."""
    exports = {}
    existing_aliases = set()
    for output in sorted(OUT.glob('**/*.html')):
        doc = soup(output.read_text(encoding='utf-8'))
        route_meta = doc.select_one('meta[name="sobi-route"]')
        if route_meta:
            exports[route_meta['content']] = (output, doc)
        elif doc.select_one('#catalogue-destination') and output.name == 'index.html':
            existing_aliases.add(output.relative_to(OUT).as_posix().removesuffix('index.html'))
    home = soup(fetch(SITE))
    menu = home.select_one('#sobi-mega')
    groups = {
        route(link['href']) for link in menu.select('a[href]')
        if urlsplit(link['href']).path.strip('/') not in ('', 'san-pham')
    }
    products = set(route_manifest['products']) if route_manifest else {r for r in exports if r.startswith('mau-tui/')}
    categories = set(route_manifest['categories']) if route_manifest else groups
    paths = sorted(categories | products | {'san-pham/'})
    redirects = route_manifest['aliases'].copy() if route_manifest else {}
    for path in existing_aliases:
        redirects.setdefault(path, 'san-pham/')
    if any(not urlsplit(target).path for target in redirects.values()):
        raise RuntimeError('The catalogue route manifest contains an empty alias destination.')
    for path in paths:
        redirects.pop(path, None)
    for path in exports:
        if route_manifest and path.startswith(('danh-muc-san-pham/', 'mau-tui/')) and path not in paths:
            redirects.setdefault(path, 'san-pham/')
    for path in redirects:
        exports.pop(path, None)
    known.update(exports.keys() | set(paths) | {'search/'})
    with ThreadPoolExecutor(max_workers=5) as pool:
        snapshots = dict(zip(paths, pool.map(lambda path: soup(fetch_bytes(SITE + path)), paths)))

    for name in ('sobi.css', 'conversion.css', 'home-audit.css', 'product-category.css', 'catalog-pages.css',
                 'category-archive.css', 'ux-layouts.css', 'category-archive.js', 'sobi.js'):
        content = fetch_bytes(SITE + PUBLIC_THEME + name)
        if name == 'sobi.js':
            (OUT / 'assets/js/sobi.js').write_bytes(make_demo_script(content.decode('utf-8')).encode('utf-8'))
        else:
            (OUT / 'assets/theme' / name).write_bytes(content.rstrip() + b'\n')

    def catalogue_pages(first):
        yield first
        for link in first.select('#sobi-archive-results .sobi-pagination a.page-numbers:not(.next):not(.prev)'):
            yield soup(fetch(link['href'].split('#')[0]))

    def archive_snapshot(main, path):
        if not main.select_one('.sobi-archive'):
            return
        grid = main.select_one('#sobi-archive-results .sobi-product-grid')
        if grid is None:
            return
        source_url = SITE + path
        for page in catalogue_pages(main):
            if page is main:
                continue
            for card in page.select('#sobi-archive-results .sobi-product-card'):
                grid.append(card.extract())
        cards = {route(card.select_one('a')['href']): card for card in grid.select('.sobi-product-card')}
        if route_manifest:
            for card in cards.values():
                card['data-archive-options'] = card.attrs.pop('data-catalogue-options', '')
        else:
            for card in cards.values():
                card['data-archive-options'] = []
            for field in main.select('.sobi-archive-options input'):
                query = urlencode({field['name']: field['value']})
                filtered = soup(fetch(source_url + '?' + query))
                for page in catalogue_pages(filtered):
                    for anchor in page.select('#sobi-archive-results .sobi-product-card a.sobi-product-card-link'):
                        key = route(anchor['href'])
                        if key in cards:
                            cards[key]['data-archive-options'].append(field['value'])
            for card in cards.values():
                card['data-archive-options'] = ' '.join(card['data-archive-options'])
        popular = soup(fetch(source_url + '?sort=popular'))
        order = 0
        for page in catalogue_pages(popular):
            for anchor in page.select('#sobi-archive-results .sobi-product-card a.sobi-product-card-link'):
                key = route(anchor['href'])
                if key in cards:
                    cards[key]['data-archive-order'] = str(order)
                    order += 1
        # The browser provides pagination and sort/view URLs for static hosting.
        for nav in main.select('#sobi-archive-results .sobi-pagination'):
            nav.decompose()

    data_file = OUT / 'assets/js/data.js'
    data = json.loads(data_file.read_text(encoding='utf-8').split(' = ', 1)[1].rstrip(';\n'))
    search = {entry['route']: entry for entry in data['search']}
    catalog = snapshots['san-pham/']
    next_pages = dict.fromkeys(link['href'] for link in catalog.select('.sobi-catalog .sobi-pagination a[href]'))
    fresh_products = {}
    for page in [catalog, *(soup(fetch(url)) for url in next_pages)]:
        for card in page.select('.sobi-catalog .sobi-product-card'):
            key = route(card.select_one('a')['href'])
            html = str(rewrite_tree(soup(str(card)), template=True))
            if route_manifest:
                code = card.select_one('.sobi-product-code')
                fresh_products[key] = {'route': key, 'title': card.select_one('h2,h3').get_text(' ', strip=True),
                                       'code': code.get_text(strip=True) if code else '', 'html': html,
                                       'options': card.get('data-catalogue-options', '').split()}
            else:
                for entry in data['products']:
                    if entry['route'] == key:
                        entry['html'] = html
    if route_manifest:
        data['products'] = list(fresh_products.values())
        if set(fresh_products) != products:
            raise RuntimeError(f'Catalogue listing and route manifest differ: {set(fresh_products) ^ products}')
        data.pop('catalogGroups', None)
        data['catalogueAliases'] = route_manifest['groups']
        search = {key: value for key, value in search.items() if key not in redirects}
    with ThreadPoolExecutor(max_workers=5) as pool:
        list(pool.map(lambda pair: archive_snapshot(pair[1].select_one('main'), pair[0]), snapshots.items()))

    for path, snapshot in snapshots.items():
        output, demo = exports.get(path, (OUT / path / 'index.html', None))
        if demo is None:
            demo = soup(str(exports['san-pham/'][1]))
        main = snapshot.select_one('main')
        if main is None or not main.select_one('h1'):
            raise RuntimeError(f'Missing catalogue page {path}')
        search[path] = {
            'route': path, 'title': main.select_one('h1').get_text(' ', strip=True),
            'text': main.get_text(' ', strip=True)[:25000],
        }
        stabilize_builder_ids(main, 'sobi-demo-layout')
        for tag in main.select('script, #wpadminbar, .post-edit-link, link, meta'):
            tag.decompose()
        for number, title in enumerate(main.select('.accordion-title'), start=1):
            panel = main.find(id=title.get('aria-controls'))
            title.name = 'button'
            title['type'] = 'button'
            title['id'] = f'demo-faq-{number}-title'
            title.attrs.pop('href', None)
            for toggle in title.select('button.toggle'):
                toggle.name = 'span'
                toggle['aria-hidden'] = 'true'
                toggle.attrs.pop('aria-label', None)
            if panel:
                panel['id'] = f'demo-faq-{number}'
                title['aria-controls'] = panel['id']
                panel['aria-labelledby'] = title['id']
                panel['role'] = 'region'
                if title.get('aria-expanded') != 'true':
                    panel['hidden'] = ''
        for anchor in main.select('.sobi-article-share a[href*="facebook.com/sharer/"]'):
            anchor['data-demo-share'] = 'facebook'
            anchor['href'] = 'https://www.facebook.com/sharer/sharer.php'
        demo.select_one('main').replace_with(rewrite_tree(main, path))
        demo.title.string = snapshot.title.get_text() + ' · Demo'
        demo.body['class'] = [*snapshot.body.get('class', []), 'sobi-static-demo']
        demo.select_one('meta[name="sobi-route"]')['content'] = path
        demo.select_one('meta[name="sobi-root"]')['content'] = relative_root(path)
        demo.select_one('link[rel="icon"]')['href'] = relative_root(path) + 'assets/theme/images/sobi-site-icon.png'
        description = snapshot.select_one('meta[name="description"]')
        demo.select_one('meta[name="description"]')['content'] = description.get('content', '') if description else ''
        # Rebuild shared chrome for new route depths, including footer and contact links.
        for selector in ('#header', '#footer'):
            node = soup(str(snapshot.select_one(selector))).find()
            demo.select_one(selector).replace_with(rewrite_tree(node, path))
        sync_quick_contacts(demo, snapshot, path)
        exports[path] = (output, demo)

    homepage = exports[''][1]
    homepage.select_one('.sobi-picks .sobi-product-grid').replace_with(
        rewrite_tree(home.select_one('.sobi-picks .sobi-product-grid'), '')
    )
    data['search'] = list(search.values())
    data_file.write_bytes(('window.SOBI_DATA = ' + json.dumps(data, ensure_ascii=False).replace('<', '\\u003c') + ';\n').encode('utf-8'))

    for path, (output, demo) in exports.items():
        existing = demo.select_one('#sobi-mega')
        if path not in snapshots and existing:
            existing.replace_with(rewrite_tree(soup(str(menu)).find(), path))
        if route_manifest and path not in snapshots and demo.select_one('#footer'):
            demo.select_one('#footer').replace_with(rewrite_tree(soup(str(home.select_one('#footer'))).find(), path))
        for form in demo.select('#header form.searchform'):
            form['action'] = rewrite_url(SITE + 'search/', path)
        for tag in demo.select('head link[rel="stylesheet"], script[src]'):
            tag.decompose()
        install_assets(demo, path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(render_static_html(demo).encode('utf-8'))

    for path, destination in sorted(redirects.items()):
        url = rewrite_url(SITE + destination, path)
        alias = soup('<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="robots" content="noindex"><title>Trang Sobi đã chuyển</title></head><body><p><a id="catalogue-destination">Mở trang mới trên Sobi</a></p></body></html>')
        alias.select_one('a')['href'] = url
        alias.head.append(alias.new_tag('link', rel='canonical', href=url))
        script = alias.new_tag('script', src=versioned_asset(path, 'assets/js/catalogue-redirect.js'), defer='')
        alias.body.append(script)
        output = OUT / path / 'index.html'
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(render_static_html(alias).encode('utf-8'))

    manifest_file = OUT / 'docs/content-manifest.json'
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    manifest['generated'] = datetime.date.today().isoformat()
    manifest['pages'] = sorted(str(output.relative_to(OUT).as_posix()) for output, _ in exports.values())
    if route_manifest:
        manifest['catalogue_redirects'] = sorted(redirects)
        manifest['products'] = len(products)
        manifest['product_categories'] = len(categories)
    manifest['media_files'] = sum(asset.is_file() for asset in (OUT / 'assets/media').rglob('*'))
    manifest_file.write_bytes((json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(f'Synchronized {len(paths)} catalogue pages and shared navigation across {len(exports)} pages.')


known = set()
if args.contacts_only:
    known.update(json.loads((OUT/'docs/content-manifest.json').read_text(encoding='utf-8'))['pages'])
    known = {path.removesuffix('index.html') for path in known}
    refresh_public_contacts()
    raise SystemExit(0)
if args.sync_catalogue:
    sync_catalogue()
    raise SystemExit(0)
if args.sync_audit:
    sync_public_audit()
    raise SystemExit(0)


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
js = make_demo_script((THEME/'sobi.js').read_text(encoding='utf-8'))
(OUT/'assets/js/sobi.js').write_bytes(js.encode('utf-8'))

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
    head.append(doc.new_tag('link',rel='icon',href=relative_root(r)+'assets/theme/images/sobi-site-icon.png'))
    if r=='404.html':
        bootstrap=doc.new_tag('script')
        bootstrap.string="const demoProject=location.pathname.split('/')[1];const demoBase=document.createElement('base');demoBase.href=new URL(['sobi-packaging','sobi-packaging-demo'].includes(demoProject)?'/'+demoProject+'/':'/',location.href).href;document.head.prepend(demoBase);"
        bootstrap.string="if(location.protocol!=='file:'){"+bootstrap.string+"}"
        head.insert(0,bootstrap)
    doc.head.replace_with(head)
    doc.html['lang']='vi'
    doc.body['class']=list(doc.body.get('class',[]))+['sobi-static-demo']
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
    static_quote_forms(doc)
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
    # Order 38: the static demo no longer adds a demo banner.
    rewrite_tree(doc,r)
    # Replace stale source-site URLs in third-party share parameters.
    for anchor in doc.select('.sobi-article-share a'):
        if 'facebook.com/sharer/' in anchor.get('href',''):
            anchor['data-demo-share']='facebook'
            anchor['href']='https://www.facebook.com/sharer/sharer.php'
    install_assets(doc, r)
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
