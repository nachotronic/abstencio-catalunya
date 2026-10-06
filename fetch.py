import json, os, re, time, urllib.parse, urllib.request
UA = {'User-Agent': 'abstencio-catalunya/1.0 (https://github.com/nachotronic/abstencio-catalunya)'}
def get(url):
    for i in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
        except Exception as e:
            print('retry', url[:90], e); time.sleep(3 * (i + 1))
    return None
def api(base, **p):
    p.update(format='json', formatversion=2)
    return json.loads(get(base + '?' + urllib.parse.urlencode(p)))
PLACES = {
 'costa-brava': ('Costa Brava', 'Costa Brava cala'),
 'salou': ('Salou', 'Salou platja'),
 'guissona': ('Guissona', 'Guissona'),
 'vic': ('Vic', 'Vic plaça Major'),
 'salt': ('Salt', 'Salt Gironès'),
 'area-barcelona': ('Àrea metropolitana de Barcelona', 'Barcelona skyline'),
 'lloret': ('Lloret de Mar', 'Lloret de Mar'),
 'figueres': ('Figueres', 'Figueres'),
 'roses': ('Roses', 'Roses Alt Empordà'),
 'castello': ("Castelló d'Empúries", "Castelló d'Empúries"),
 'ciutat-vella': ('Ciutat Vella (Barcelona)', 'Raval Barcelona'),
 'nou-barris': ('Nou Barris', 'Nou Barris'),
 'sant-adria': ('Sant Adrià de Besòs', 'Sant Adrià de Besòs'),
 'badalona': ('Badalona', 'Badalona'),
 'santa-coloma': ('Santa Coloma de Gramenet', 'Santa Coloma de Gramenet'),
}
out = {}
for slug, (title, q) in PLACES.items():
    files = []
    for wiki in ('ca', 'es'):
        try:
            r = api(f'https://{wiki}.wikipedia.org/w/api.php', action='query', prop='pageimages|images', piprop='name', titles=title, redirects=1, imlimit=40)
            pg = r['query']['pages'][0]
            if pg.get('pageimage'): files.append('File:' + pg['pageimage'])
            files += [i['title'] for i in pg.get('images', [])]
        except Exception as e: print('wiki', slug, e)
    try:
        r = api('https://commons.wikimedia.org/w/api.php', action='query', list='search', srsearch=q + ' filetype:bitmap', srnamespace=6, srlimit=12)
        files += [s['title'] for s in r['query']['search']]
    except Exception as e: print('search', slug, e)
    seen = []
    for f in files:
        f = re.sub(r'^(Fitxer|Archivo|Imatge|Imagen):', 'File:', f)
        if f not in seen and re.search(r'\.(jpe?g|png)$', f, re.I) and not re.search(r'escut|escudo|bandera|flag|coat|logo|mapa|map|locator|situaci|plano|signature|firma|\.svg', f, re.I):
            seen.append(f)
    seen = seen[:14]
    cands = []
    for i in range(0, len(seen), 10):
        r = api('https://commons.wikimedia.org/w/api.php', action='query', titles='|'.join(seen[i:i+10]), prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=960)
        for pg in r['query']['pages']:
            ii = (pg.get('imageinfo') or [None])[0]
            if not ii or ii['width'] < 900 or ii['width'] < ii['height']: continue
            m = ii.get('extmetadata', {})
            v = lambda k: re.sub('<[^>]+>', '', m.get(k, {}).get('value', '')).strip()
            cands.append(dict(file=pg['title'], page=ii['descriptionurl'], thumb=ii['thumburl'], w=ii['width'], h=ii['height'],
                              artist=v('Artist'), license=v('LicenseShortName'), license_url=v('LicenseUrl'), desc=v('ImageDescription')[:200]))
    os.makedirs(f'cand/{slug}', exist_ok=True)
    keep = []
    for k, c in enumerate(cands[:10]):
        b = get(c['thumb'])
        if b:
            c['local'] = f'cand/{slug}/{k:02d}.jpg'; open(c['local'], 'wb').write(b); keep.append(c)
        time.sleep(0.3)
    out[slug] = keep
    print(slug, len(keep))
json.dump(out, open('cand/candidates.json', 'w'), ensure_ascii=False, indent=1)
