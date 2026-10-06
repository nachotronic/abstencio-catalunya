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
 'salt': ['Salt, Catalonia', 'Salt Catalunya', 'Coma Cros Salt', 'Devesa de Salt', 'Salt Girona carrer Major', 'Salt Girona plaça', 'Salt Gironès mercat setmanal', 'Salt Girona Ter', 'Hostalets Salt', 'Salt Girona festa', 'Marrecs de Salt'],
 'lloret': ['Lloret de Mar carrer', 'Lloret de Mar Sant Romà', 'Lloret de Mar festa major', 'Lloret de Mar centre', 'Lloret de Mar people street'],
}
out = {}
for slug, qs in PLACES.items():
    files = []
    for q in qs:
        try:
            r = api('https://commons.wikimedia.org/w/api.php', action='query', list='search', srsearch=q + ' filetype:bitmap', srnamespace=6, srlimit=10)
            files += [s['title'] for s in r['query']['search']]
        except Exception as e: print('search', slug, e)
    seen = []
    for f in files:
        if f not in seen and re.search(r'\.(jpe?g)$', f, re.I) and not re.search(r'escut|escudo|bandera|flag|coat|logo|mapa|map|locator|situaci|plano|signature|firma', f, re.I):
            seen.append(f)
    seen = seen[:40]
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
    os.makedirs(f'cand4/{slug}', exist_ok=True)
    keep = []
    for k, c in enumerate(cands[:24]):
        b = get(c['thumb'])
        if b:
            c['local'] = f'cand4/{slug}/{k:02d}.jpg'; open(c['local'], 'wb').write(b); keep.append(c)
        time.sleep(0.3)
    out[slug] = keep
    print(slug, len(keep))
json.dump(out, open('cand4/candidates.json', 'w'), ensure_ascii=False, indent=1)
