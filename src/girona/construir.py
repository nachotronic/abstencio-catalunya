"""Genera girona.html (castellano) y girona-ca.html (catalán), la pieza de la provincia de Girona.

Parte de abstencion.html, la pieza de toda Cataluña, para compartir su diseño y su código (mapa 3D, vuelos de
cámara, gráficos, buscador de calles), y le cambia:
  - el texto visible: src/girona/es_body.html y src/girona/ca_body.html;
  - los datos incrustados: secciones, evolución, municipales y fotos de las 536 secciones de la provincia 17,
    y el resumen de src/girona/resumen.json (que escribe src/girona/datos.py);
  - las escenas de la cámara, los encuadres y la cabecera SEO.
Los textos del JavaScript se traducen con la misma lista que usa src/build_ca.py.

Uso: python3 src/girona/construir.py   (después de src/build_ca.py si ha cambiado la pieza catalana)
"""
import base64, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
HERE = ROOT / 'src' / 'girona'
BASE = 'https://mapaelectoral.es/'
PUBLISHED, MODIFIED = '2026-10-13', '2026-10-23T22:25:00+02:00'
START, END = '<div class="wide">\n<header class="col">', '<script src="https://unpkg.com/deck.gl'

R = json.load(open(HERE / 'resumen.json', encoding='utf-8'))
FOTOS = json.load(open(HERE / 'fotos.json', encoding='utf-8'))

# ---- escenas: vista de la provincia y vuelos a cada lugar
PROV = 'longitude:2.62, latitude:42.10, zoom:8.7'
PROV3D = 'longitude:2.62, latitude:42.0, zoom:8.7'
SCENES = f"""const SCENES = {{
  cat:     {{view:{{{PROV}, pitch:0, bearing:0}}, c:'abst', h:'none', es:1}},
  cat3d:   {{view:{{{PROV3D}, pitch:52, bearing:-14}}, c:'abst', h:'novota', es:1}},
  sin:     {{view:{{{PROV3D}, pitch:52, bearing:-14}}, c:'sin', h:'sin', es:1}},
  salt:    {{view:at('Salt',12.6,45,-20), c:'sin', h:'novota', es:1, focus:'Salt'}},
  lloret:  {{view:at('Lloret de Mar',12.0,45,-25), c:'sin', h:'novota', es:1, focus:'Lloret de Mar'}},
  figueres:{{view:at('Figueres',12.4,45,-15), c:'abst', h:'novota', es:1, focus:'Figueres', mark:'1706601005'}},
  girona:  {{view:at('Girona',12.1,48,-25), c:'inc', h:'abst', es:1, focus:'Girona', mark:'1707901005'}},
  eu:      {{view:{{longitude:3.02, latitude:42.08, zoom:9.6, pitch:48, bearing:-18}}, c:'sinm', h:'sinm', es:1}},
  rural:   {{view:{{{PROV3D}, pitch:48, bearing:-10}}, c:'mvsg', h:'mgap', es:1}},
  edu:     {{view:{{{PROV3D}, pitch:48, bearing:-20}}, c:'edu', h:'abst', es:1}},
  drop:    {{view:{{{PROV3D}, pitch:48, bearing:12}}, c:'ind', h:'drop', es:1}},
  evol:    {{view:{{{PROV3D}, pitch:50, bearing:-8}}, c:'evo', h:'evo', es:1}},
  explore: {{view:{{{PROV}, pitch:0, bearing:0}}, c:'abst', h:'none', es:1}}
}};"""
# foto de cada paso: «paso:lugar», para que ningún lugar repita foto
STEP_PLACE = {'sin': "Castelló d'Empúries", 'salt': 'Salt', 'lloret': 'Lloret de Mar', 'figueres': 'Figueres', 'girona': 'Girona', 'rural': 'Olot'}

TXT_ES = {'cat': 'Provincia de Girona', 'frank': 'Vota más que el {n}% de las secciones de la provincia de Girona.',
          'faria': 'Participación de la sección y de la provincia en cada elección'}
TXT_CA = {'cat': 'Província de Girona', 'frank': 'Vota més que el {n}% de les seccions de la província de Girona.',
          'faria': 'Participació de la secció i de la província a cada elecció'}

TEXTS = {
    'es': dict(title='Girona, la provincia catalana donde menos adultos votan · Abstención por sección censal',
               headline='Girona, la provincia catalana donde menos adultos votan',
               desc='De cada 100 adultos de la provincia de Girona, 49 votaron el 23J de 2023, 21 no tenían derecho a voto y 30 se abstuvieron. Mapa 3D de las 536 secciones censales cruzado con renta, estudios, paro y población extranjera: Salt, Lloret, Castelló d\'Empúries, Figueres y Girona.',
               url='girona.html', locale='es_ES', place='Provincia de Girona',
               kw=['abstención', 'participación electoral', 'provincia de Girona', 'sección censal', 'renta', 'población extranjera', 'Salt', 'Lloret de Mar', "Castelló d'Empúries", 'Figueres']),
    'ca': dict(title='Girona, la província catalana on menys adults voten · Abstenció per secció censal',
               headline='Girona, la província catalana on menys adults voten',
               desc='De cada 100 adults de la província de Girona, 49 van votar el 23J de 2023, 21 no tenien dret a vot i 30 es van abstenir. Mapa 3D de les 536 seccions censals creuat amb renda, estudis, atur i població estrangera: Salt, Lloret, Castelló d\'Empúries, Figueres i Girona.',
               url='girona-ca.html', locale='ca_ES', place='Província de Girona',
               kw=['abstenció', 'participació electoral', 'província de Girona', 'secció censal', 'renda', 'població estrangera', 'Salt', 'Lloret de Mar', "Castelló d'Empúries", 'Figueres']),
}


def const_line(s, name):
    """Posición de la línea «const NAME = ...;» (una sola línea en la pieza)."""
    i = s.index(f'const {name} = '); j = s.index('\n', i)
    return i, j


def get_const(s, name):
    i, j = const_line(s, name)
    return json.loads(s[i + len(f'const {name} = '):j].rstrip().rstrip(';'))


def set_const(s, name, value, **kw):
    i, j = const_line(s, name)
    return s[:i] + f'const {name} = ' + json.dumps(value, **kw) + ';' + s[j:]


def sub_once(s, pattern, repl, flags=re.S):
    out, n = re.subn(pattern, lambda m: repl, s, count=1, flags=flags)
    if n != 1:
        sys.exit(f'No encuentro en la pieza: {pattern[:60]}')
    return out


def replace_once(s, old, new):
    if s.count(old) != 1:
        sys.exit(f'{s.count(old)} apariciones (esperaba 1): {old[:70]}')
    return s.replace(old, new)


def filter_geo(s):
    G = get_const(s, 'G')
    tc = G['cols']['tract_code']
    keep = [i for i, c in enumerate(tc) if c.startswith('17')]
    newi = {o: n for n, o in enumerate(keep)}
    names = sorted({G['names'][G['cols']['mun_name'][i]] for i in keep if G['cols']['mun_name'][i] >= 0})
    ni = {n: k for k, n in enumerate(names)}
    cols = {k: [v[i] for i in keep] for k, v in G['cols'].items()}
    cols['mun_name'] = [ni.get(G['names'][x], -1) if x >= 0 else -1 for x in cols['mun_name']]
    polys = [[newi[i], f] for i, f in G['polys'] if i in newi]
    cent = {n: c for n, c in G['cent'].items() if n in ni}
    G2 = {'S': G['S'], 'names': names, 'cols': cols, 'polys': polys, 'cent': cent}
    EVO = get_const(s, 'EVO')
    EVO2 = {'el': EVO['el'], 'cat': R['evo_prov'], 'q': R['evo_q'], 't': [EVO['t'][i] for i in keep]}
    ELM = get_const(s, 'ELM')
    km = [i for i, c in enumerate(ELM['code']) if c.startswith('17')]

    def cut(v):
        if isinstance(v, list) and len(v) == len(ELM['code']):
            return [v[i] for i in km]
        if isinstance(v, dict):
            return {k: cut(x) for k, x in v.items()}
        return v
    ELM2 = {k: cut(v) for k, v in ELM.items()}
    return G2, EVO2, ELM2, len(keep)


def photos(lang):
    out = {}
    for place, f in FOTOS.items():
        step = [k for k, v in STEP_PLACE.items() if v == place][0]
        b64 = base64.b64encode((ROOT / f['img']).read_bytes()).decode()
        out[f'{step}:{place}'] = {'src': 'data:image/webp;base64,' + b64, 'alt': f['alt'] if lang == 'es' else f['alt_ca'], 'a': f['a'], 'l': f['l'], 'u': f['u']}
    return out


def summary():
    keys = ['quint', 'compare', 'size_hist', 'indep', 'reg', 'corr', 'low', 'totals']
    return {k: R[k] for k in keys}


def seo(lang, analytics, verif):
    t = TEXTS[lang]; other = TEXTS['ca' if lang == 'es' else 'es']
    url = BASE + t['url']
    ld = {'@context': 'https://schema.org', '@graph': [{
        '@type': 'AnalysisNewsArticle', '@id': url + '#article', 'headline': t['headline'], 'description': t['desc'], 'inLanguage': lang,
        'url': url, 'mainEntityOfPage': url, 'image': BASE + 'img/compartir/girona.jpg', 'datePublished': PUBLISHED, 'dateModified': MODIFIED,
        'author': {'@type': 'Person', '@id': BASE + 'sobre-mi.html#person', 'name': 'Nacho G. del Álamo', 'url': BASE + 'sobre-mi.html'},
        'publisher': {'@type': 'NewsMediaOrganization', '@id': BASE + '#medio', 'name': 'Mapa Electoral', 'url': BASE,
                      'publishingPrinciples': BASE + 'atlas/politica-editorial/', 'correctionsPolicy': BASE + 'atlas/correcciones/'},
        'license': 'https://creativecommons.org/licenses/by/4.0/', 'isAccessibleForFree': True, 'keywords': t['kw'],
        'contentLocation': {'@type': 'Place', 'name': t['place']},
        'citation': ['https://github.com/dadosdelaplace/pollspain', 'https://github.com/pablogguz/ineAtlas.data', 'https://analisi.transparenciacatalunya.cat/d/irrv-2mfc',
                     'https://www.ciemen.cat/wp-content/uploads/2026/10/El-dret-de-vot-de-les-persones-immigrades-a-Catalunya.pdf'],
        'isPartOf': {'@id': BASE + ('abstencion.html' if lang == 'es' else 'ca.html') + '#article'},
        'workTranslation' if lang == 'es' else 'translationOfWork': {'@id': BASE + other['url'] + '#article'}}]}
    e = lambda x: x.replace('&', '&amp;').replace('"', '&quot;')
    return '\n'.join([
        '<!-- seo -->',
        f'<meta name="description" content="{e(t["desc"])}">',
        '<meta name="author" content="Nacho G. del Álamo">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="canonical" href="{url}">', *verif,
        f'<link rel="alternate" hreflang="es" href="{BASE}girona.html">',
        f'<link rel="alternate" hreflang="ca" href="{BASE}girona-ca.html">',
        f'<link rel="alternate" hreflang="x-default" href="{BASE}girona.html">',
        '<meta property="og:type" content="article">',
        f'<meta property="og:title" content="{e(t["headline"])}">',
        f'<meta property="og:description" content="{e(t["desc"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{BASE}img/compartir/girona.jpg">',
        f'<meta property="og:locale" content="{t["locale"]}">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">',
        '<script type="application/ld+json">', json.dumps(ld, ensure_ascii=False, indent=1), '</script>',
        analytics, '<!-- /seo -->'])


def build(lang, base, geo):
    G2, EVO2, ELM2, n = geo
    s = base
    # cabecera
    i, j = s.index('<!-- seo -->'), s.index('<!-- /seo -->') + len('<!-- /seo -->')
    old = s[i:j]
    analytics = next(l for l in old.split('\n') if 'Cloudflare Web Analytics' in l)
    verif = [l for l in old.split('\n') if 'site-verification' in l or 'msvalidate' in l]
    s = s[:i] + seo(lang, analytics, verif) + s[j:]
    s = sub_once(s, r'<title>.*?</title>', f'<title>{TEXTS[lang]["title"]}</title>')
    # texto
    i = s.index(START); j = s.index(END, i)
    s = s[:i] + (HERE / f'{lang}_body.html').read_text(encoding='utf-8') + '\n' + s[j:]
    # datos
    s = set_const(s, 'S', summary(), default=float)
    s = set_const(s, 'G', G2, separators=(',', ':'))
    s = set_const(s, 'EVO', EVO2, separators=(',', ':'))
    s = set_const(s, 'ELM', ELM2, separators=(',', ':'))
    s = set_const(s, 'PHOTOS', photos(lang), ensure_ascii=False, separators=(',', ':'))
    txt = json.loads((ROOT / 'src' / 'i18n' / f'txt_{lang}.js').read_text(encoding='utf-8').strip()[len('const TXT = '):].rstrip(';'))
    txt.update(TXT_ES if lang == 'es' else TXT_CA)
    s = set_const(s, 'TXT', txt, ensure_ascii=False, separators=(',', ':'))
    # cámara y encuadres
    s = sub_once(s, r'const SCENES = \{.*?\n\};', SCENES)
    s = sub_once(s, r'const PLACES = \{.*?\n\};', 'const PLACES = {};')
    s = sub_once(s, r'const STEP_PLACE = \{[^\n]*\};', 'const STEP_PLACE = ' + json.dumps(STEP_PLACE, ensure_ascii=False) + ';')
    s = replace_once(s, 'const HMAX = 14000;', 'const HMAX = 6000;')
    s = replace_once(s, 'let baseZoom = 7.15;', 'let baseZoom = 8.7;')
    s = replace_once(s, '{ longitude:1.72, latitude:41.72, zoom:7.15, pitch:0, bearing:0 }', '{ ' + PROV + ', pitch:0, bearing:0 }')
    s = replace_once(s, "fetch('calles.json')", "fetch('calles-girona.json')")
    s = sub_once(s, r'const D = \[.*?\];', 'const D = ' + json.dumps([{k: d[k] for k in ['d', 'lo', 'hi', 'g', 'm', 'p']} for d in R['deciles']]) + ';')
    if lang == 'ca':
        src = (ROOT / 'src' / 'build_ca.py').read_text(encoding='utf-8')
        pairs = {}
        exec(src[src.index('JS = ['):src.index('\n]\n', src.index('JS = [')) + 3], {'I18N': ROOT / 'src' / 'i18n', 'open': open}, pairs)
        for old, new, _ in pairs['JS']:
            if old.startswith('<title>') or old.startswith('const TXT'):
                continue
            s = s.replace(old, new)
        s = s.replace('"name": "Provincia de Girona"', '"name": "Prov\\u00edncia de Girona"')
    out = ROOT / TEXTS[lang]['url']
    out.write_text(s, encoding='utf-8')
    print(out.name, len(s), 'bytes,', n, 'secciones')


def calles(base):
    """calles-girona.json: el índice del buscador (calles.json, de toda Cataluña) solo con los municipios de la
    provincia y con los índices de sección renumerados a las 536 secciones de la pieza."""
    tc = get_const(base, 'G')['cols']['tract_code']
    newi = {o: n for n, o in enumerate(i for i, c in enumerate(tc) if c.startswith('17'))}
    d = json.load(open(ROOT / 'calles.json', encoding='utf-8'))
    tr = lambda t: newi[t] if isinstance(t, int) else [[newi[x[0]]] + x[1:] for x in t]
    m = {k: [[n, t, tr(x)] for n, t, x in v] for k, v in d['m'].items() if k.startswith('17')}
    (ROOT / 'calles-girona.json').write_text(json.dumps({'t': d['t'], 'm': m}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def main():
    base = (ROOT / 'abstencion.html').read_text(encoding='utf-8')
    geo = filter_geo(base)
    calles(base)
    for lang in sys.argv[1:] or ('es', 'ca'):
        build(lang, base, geo)


main()
