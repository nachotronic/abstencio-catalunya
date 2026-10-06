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
 'costa-brava': ['Costa Brava beach people', 'Platja Tossa de Mar people', "Platja d'Aro beach summer"],
 'salou': ['Salou beach people', 'Salou passeig people', 'Salou platja Llevant'],
 'guissona': ['Guissona', 'Guissona fira', 'Guissona festa'],
 'vic': ['Vic mercat plaça Major', 'Vic market people', 'Mercat de Vic'],
 'salt': ['Salt Gironès carrer', 'Salt Girona mercat', 'Salt festa major', 'Salt Gironès people'],
 'area-barcelona': ['Barcelona street people', 'Barcelona metro passengers', 'Rambla Barcelona people crowd'],
 'lloret': ['Lloret de Mar beach people', 'Lloret de Mar street', 'Lloret de Mar platja estiu'],
 'figueres': ['Figueres Rambla people', 'Figueres mercat', 'Figueres fira'],
 'roses': ['Roses platja people', 'Roses beach Catalonia people', 'Roses passeig marítim'],
 'castello': ["Castelló d'Empúries fira", "Empuriabrava people", "Castelló d'Empúries festa"],
 'ciutat-vella': ['Raval Barcelona street people', 'Rambla del Raval people', 'Barceloneta people', 'Mercat Sant Antoni people'],
 'nou-barris': ['Nou Barris people', 'Nou Barris festa', 'Via Júlia Barcelona'],
 'sant-adria': ['Sant Adrià de Besòs La Mina', 'Sant Adrià de Besòs festa', 'Sant Adrià de Besòs platja'],
 'badalona': ['Badalona platja people', 'Badalona Rambla people', 'Badalona Sant Roc', 'Badalona festa'],
 'santa-coloma': ['Santa Coloma de Gramenet people', 'Santa Coloma de Gramenet festa', 'Santa Coloma de Gramenet Rambla', 'Santa Coloma de Gramenet mercat'],
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
    seen = seen[:24]
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
    os.makedirs(f'cand2/{slug}', exist_ok=True)
    keep = []
    for k, c in enumerate(cands[:16]):
        b = get(c['thumb'])
        if b:
            c['local'] = f'cand2/{slug}/{k:02d}.jpg'; open(c['local'], 'wb').write(b); keep.append(c)
        time.sleep(0.3)
    out[slug] = keep
    print(slug, len(keep))
json.dump(out, open('cand2/candidates.json', 'w'), ensure_ascii=False, indent=1)
