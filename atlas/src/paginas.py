"""Genera las páginas estáticas del Atlas de las anomalías electorales en atlas/.

Todo el contenido está en el HTML (sin depender de JavaScript): titular, resumen, gráfico SVG, tabla, método,
fuentes, autoría, revisión e historial de correcciones, más los datos estructurados schema.org.
Uso (después de construir.py y controles.py):  python3 atlas/src/paginas.py
"""
import datetime, json, pathlib, re, sys
from html import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from piezas import piezas, SERIES  # noqa: E402
from piezas2 import piezas2  # noqa: E402
from piezas3 import piezas3  # noqa: E402
from titulares import titular  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / 'atlas'
BASE = 'https://mapaelectoral.es/'
ATLAS_URL = BASE + 'atlas/'
NOMBRE = 'Atlas de las anomalías electorales'
FIRMA = 'Nacho G. del Álamo'
SITIO = 'Mapa Electoral'
AUTOR = {'@type': 'Person', 'name': FIRMA, 'url': BASE + 'sobre-mi.html', 'sameAs': ['https://github.com/nachotronic']}
LICENCIA = 'https://creativecommons.org/licenses/by/4.0/'
REPO = 'https://github.com/nachotronic/abstencio-catalunya'
CF = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "d27e4ef550c94f82912044da926a3b0f"}'></script><!-- End Cloudflare Web Analytics -->'''
HOY = datetime.date.today().isoformat()
PUBLICADO = '2026-10-06'   # fecha de publicación de las piezas que aún no tienen `revisado`
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
# Boletín: URL del formulario de alta (por ejemplo https://buttondown.com/api/emails/embed-subscribe/<usuario>).
# Mientras esté vacío, el bloque «Síguelo» solo ofrece RSS y X.
NEWSLETTER = ''
X_URL = 'https://x.com/nachotronic'


def fecha_txt(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} de {MESES[d.month - 1]} de {d.year}'


def publicado(p):
    # una pieza se publica el día en que se revisa
    return p['revisado'] or PUBLICADO


def recientes():
    # de la más nueva a la más antigua; a igual fecha, la que se añadió después va antes
    return [q for _, q in sorted(enumerate(TODAS), key=lambda iq: (publicado(iq[1]), iq[0]), reverse=True)]


def ruta_pieza(q):
    return f'{q["serie"]}/{q["slug"]}/index.html'


def imagen(q=None):
    # imagen para redes, generada por compartir.mjs (1200 × 630)
    return BASE + 'img/compartir/' + (f'atlas-{q["slug"]}.jpg' if q else 'atlas.jpg')
# página de resultados de España (la pieza de las generales); se mueve a /generales-2026/
GENERALES = ''   # el mapa de resultados de España es la portada del sitio (index.html en la raíz)

FUENTES = {
    'interior': ('Ministerio del Interior, resultados electorales por mesa (Infoelectoral). Congreso 2004-2023 vía pollspaindata, commit ee5ecda; municipales 2007-2023 de los ficheros de Infoelectoral',
                 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/'),
    'pollspain': ('pollspaindata: copia procesada de los ficheros por mesa de Interior', 'https://github.com/dadosdelaplace/pollspaindata'),
    'ine_adrh': ('INE, Atlas de Distribución de Renta de los Hogares 2023 (renta, edad, población), vía ineAtlas.data', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm'),
    'ine_censo': ('INE, Censo de Población y Viviendas 2021 (estudios, paro, extranjeros)', 'https://www.ine.es/censos2021/'),
    'europeas': ('Ministerio del Interior, resultados por mesa de las elecciones al Parlamento Europeo de 2019 y 2024 (Infoelectoral)',
                 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/'),
    'transparencia': ('Generalitat de Catalunya, participación por sección censal (Transparència Catalunya, irrv-2mfc)', 'https://analisi.transparenciacatalunya.cat/d/irrv-2mfc'),
    'decreto29n': ('Real Decreto de disolución de las Cortes y convocatoria de elecciones para el 29 de noviembre de 2026 (BOE, 6 de octubre de 2026): escaños por provincia', None),
}

CSS = """
:root{--bg:#faf8f3;--surface:#fff;--fg:#1a1a1a;--muted:#5f5d58;--rule:#e3dfd6;--accent:#b3261e;--accent2:#b0452c;--pp:#1d6fb8;--psoe:#d1262d;--warn:#fff4d6;--warnfg:#6b4e00;
  --display:"IBM Plex Sans",system-ui,sans-serif;--sans:"IBM Plex Sans",system-ui,sans-serif;--body:"Newsreader",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15161a;--surface:#1e2025;--fg:#ecebe7;--muted:#a5a39b;--rule:#33363d;--accent:#ff8a80;--accent2:#ef8a6a;--pp:#5aa7ee;--psoe:#f06a6f;--warn:#3a3218;--warnfg:#f2d98a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15161a;--surface:#1e2025;--fg:#ecebe7;--muted:#a5a39b;--rule:#33363d;--accent:#ff8a80;--accent2:#ef8a6a;--pp:#5aa7ee;--psoe:#f06a6f;--warn:#3a3218;--warnfg:#f2d98a;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:1.1rem;line-height:1.6;padding:0 16px 64px}
main{max-width:72ch;margin:0 auto}
a{color:var(--accent)}
h1,h2,h3{font-family:var(--display);line-height:1.12;text-wrap:balance}
h1{font-size:clamp(1.9rem,5.5vw,2.9rem);font-weight:700;letter-spacing:-.015em;margin:.3rem 0 .6rem}
h2{font-size:1.35rem;margin:2.4rem 0 .6rem}
h3{font-size:1.1rem;margin:1.6rem 0 .4rem}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.resumen{font-size:1.22rem;line-height:1.5}
.estado{display:inline-block;font-family:var(--mono);font-size:.76rem;border:1px solid var(--rule);border-radius:4px;padding:2px 8px;margin-right:6px;background:var(--surface)}
.aviso{background:var(--warn);color:var(--warnfg);border-radius:6px;padding:10px 14px;font-family:var(--mono);font-size:.82rem;margin:1rem 0}
.tipo{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-right:6px}
figure{margin:1.6rem 0;background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px}
figcaption{font-family:var(--mono);font-size:.78rem;color:var(--muted);margin-top:8px}
.foto{padding:0;overflow:hidden}.foto.apertura{margin:0 0 1.4rem}.foto img{display:block;width:100%;height:auto;max-height:520px;object-fit:cover}.foto figcaption{padding:0 14px 12px}
.fuentes-nota{font-family:var(--mono);font-size:.76rem;color:var(--muted);white-space:nowrap}
svg.graf{width:100%;height:auto;display:block}
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.92rem}
caption{text-align:left;font-family:var(--mono);font-size:.8rem;color:var(--muted);padding-bottom:6px}
th,td{text-align:left;vertical-align:top;padding:7px 10px 7px 0;border-bottom:1px solid var(--rule)}
th{font-family:var(--mono);font-size:.76rem;color:var(--muted);font-weight:500}
td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}
.ficha{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:6px 16px 12px;font-size:.98rem}
.ficha dt{font-family:var(--mono);font-size:.76rem;color:var(--muted);margin-top:10px}
.ficha dd{margin:2px 0 0}
ul{padding-left:1.2rem}li{margin:.35rem 0}
.tarjetas{list-style:none;padding:0;display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr))}
.tarjetas li{margin:0}
a.tarjeta{display:flex;flex-direction:column;height:100%;background:var(--surface);border:1px solid var(--rule);border-radius:8px;overflow:hidden;color:var(--fg);text-decoration:none;transition:border-color .15s,transform .15s}
a.tarjeta img,a.tarjeta .sinfoto{display:block;width:100%;aspect-ratio:3/2;object-fit:cover;background:var(--rule)}
a.tarjeta .sinfoto{display:flex;align-items:flex-end;padding:12px 18px;box-sizing:border-box;font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:linear-gradient(135deg,var(--surface),var(--rule))}
a.tarjeta .txt{display:flex;flex-direction:column;gap:6px;padding:14px 18px 16px;border-top:4px solid var(--accent);flex:1}
a.tarjeta .leer{margin-top:auto}
a.tarjeta:hover,a.tarjeta:focus-visible{border-color:var(--accent);transform:translateY(-1px)}
a.tarjeta .tt{font-family:var(--display);font-weight:700;font-size:1.15rem;line-height:1.25;color:var(--fg)}
a.tarjeta .ent{font-size:1rem;color:var(--muted)}
a.tarjeta .leer{font-family:var(--mono);font-size:.8rem;color:var(--accent);font-weight:600}
.cuerpo h2{font-size:1.25rem;margin:2.2rem 0 .5rem}
.cuerpo p{margin:0 0 1rem}
footer{margin-top:3rem;font-family:var(--mono);font-size:.76rem;color:var(--muted)}
nav.site{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;max-width:72ch;margin:0 auto 1.4rem;padding:12px 0 10px;border-bottom:1px solid var(--rule);font:500 14px/1.4 var(--sans)}
nav.site a{color:var(--muted);text-decoration:none}nav.site a:hover{color:var(--accent)}nav.site a[aria-current]{color:var(--fg);font-weight:700}
@media (max-width:760px){nav.site{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none}nav.site::-webkit-scrollbar{display:none}}
nav.site a.marca{color:var(--fg);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:13px;margin-right:6px}
.subtitulo{font-family:var(--sans);font-size:1.12rem;line-height:1.4;color:var(--muted);margin:0 0 1rem;text-wrap:pretty}
.firma{font-family:var(--sans);font-size:.86rem;color:var(--muted);margin:0 0 1.2rem}.firma a{color:inherit}
a.vermapa{display:inline-block;font-family:var(--sans);font-weight:600;font-size:.92rem;border:1px solid var(--accent);border-radius:999px;padding:5px 14px;margin:0 6px 6px 0;text-decoration:none}
a.vermapa:hover{background:var(--accent);color:var(--bg)}
.tipo{font-family:var(--sans);font-size:.66rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-right:6px;opacity:.8}
.tipo.t-hipotesis,.tipo.t-patron{color:var(--accent)}
@media (min-width:1100px){.cuerpo p,.terreno p,.hipotesis li{position:relative}.cuerpo .tipo,.terreno .tipo,.hipotesis .tipo{position:absolute;right:100%;top:.45em;margin-right:18px;white-space:nowrap}.hipotesis{list-style:none;padding-left:0}}
.leyenda{font-family:var(--sans);font-size:.82rem;color:var(--muted)}
.sigue{list-style:none;padding:0;display:grid;gap:12px}
.sigue a{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:12px 16px;text-decoration:none;color:var(--fg)}
.sigue a:hover{border-color:var(--accent)}.sigue .kicker{display:block;margin-bottom:2px}.sigue b{font-family:var(--sans);font-size:1.05rem}
.siguelo{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px 18px;margin-top:2.4rem;font-family:var(--sans);font-size:.95rem}
.siguelo form{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}.siguelo input{flex:1 1 220px;font:inherit;padding:7px 10px;border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--fg)}
.siguelo button{font:inherit;font-weight:600;padding:7px 14px;border:0;border-radius:6px;background:var(--accent);color:var(--bg);cursor:pointer}
a.destacada{display:grid;gap:0;background:var(--surface);border:1px solid var(--rule);border-radius:8px;overflow:hidden;color:var(--fg);text-decoration:none;margin:1.2rem 0 2rem}
a.destacada img{display:block;width:100%;aspect-ratio:16/9;object-fit:cover}
a.destacada .txt{padding:16px 20px 18px;border-top:4px solid var(--accent);display:flex;flex-direction:column;gap:6px}
a.destacada .tt{font-family:var(--display);font-weight:700;font-size:clamp(1.5rem,4vw,2.1rem);line-height:1.12}
a.destacada .ent{color:var(--muted);font-family:var(--sans);font-size:1.05rem}
a.destacada:hover{border-color:var(--accent)}
h2.serie{display:flex;justify-content:space-between;align-items:baseline;gap:12px;border-top:2px solid var(--fg);padding-top:10px}
h2.serie a{color:var(--fg);text-decoration:none}h2.serie small{font-family:var(--sans);font-weight:400;font-size:.85rem;color:var(--muted)}
p.serie-desc{color:var(--muted);margin:-.2rem 0 1rem}
a.tarjeta .ent{font-family:var(--sans);font-size:.95rem}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
"""


def url(p):
    # URL canónica: la carpeta, sin «index.html», igual que en el sitemap
    return ATLAS_URL + re.sub(r'(^|/)index\.html$', r'\1', p)


def cabeza(titulo, desc, ruta, ld, indexar=True, nivel=0, img=None, actual='atlas'):
    rel = '../' * nivel
    raiz = rel + '../'
    menu = [('resultados', f'{raiz}{GENERALES}', 'Mapa de resultados'), ('atlas', f'{rel}index.html', 'Atlas de las anomalías'),
            ('cataluna', f'{raiz}abstencion.html', '¿Quién no vota en Cataluña?'), ('metodologia', f'{rel}metodologia/index.html', 'Metodología'),
            ('sobre', f'{raiz}sobre-mi.html', 'Sobre mí')]
    nav = (f'<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="{raiz}">{SITIO}</a>' +
           ''.join(f'<a href="{h}"{" aria-current=\"page\"" if k == actual else ""}>{t}</a>' for k, h, t in menu) + '</nav>')
    img = img or imagen()
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="author" content="{FIRMA}">
<meta name="robots" content="{'index, follow, max-image-preview:large' if indexar else 'noindex, follow'}">
<link rel="canonical" href="{url(ruta)}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="{SITIO}">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url(ruta)}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@nachotronic">
<link rel="license" href="{LICENCIA}">
<link rel="alternate" type="application/rss+xml" title="{NOMBRE}" href="{ATLAS_URL}feed.xml">
<link rel="alternate" type="text/plain" title="llms.txt" href="{rel}llms.txt">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
{CF}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
{nav}
<main>
"""


def siguelo():
    """Bloque para seguir el Atlas: boletín (si hay formulario configurado), RSS y X."""
    form = (f'<form action="{NEWSLETTER}" method="post" target="_blank"><label class="sr" for="email">Correo electrónico</label>'
            '<input type="email" name="email" id="email" placeholder="tu@correo.es" required><button type="submit">Apuntarme</button></form>') if NEWSLETTER else ''
    return (f'<aside class="siguelo"><b>Las piezas nuevas del Atlas</b>: '
            + ('recíbelas por correo, o síguelas' if NEWSLETTER else 'síguelas')
            + f' por <a href="{ATLAS_URL}feed.xml">RSS</a> o en <a href="{X_URL}">X</a>.{form}</aside>')


PIE = f"""<footer>{NOMBRE} · Datos con licencia <a href="{LICENCIA}">CC BY 4.0</a> · <a href="{REPO}">Código y datos</a></footer>
</main>
</body>
</html>
"""


def tabla(t):
    def celda(v, tag='td'):
        es_num = isinstance(v, (int, float)) or (isinstance(v, str) and v[:1] in '+-−0123456789' and any(c.isdigit() for c in v[:3]))
        return f'<{tag}{" class=\"n\"" if es_num else ""}>{escape(str(v))}</{tag}>'
    cab = ''.join(f'<th scope="col"{" class=\"n\"" if i else ""}>{escape(h)}</th>' for i, h in enumerate(t['cabecera']))
    filas = ''.join('<tr>' + f'<th scope="row">{escape(str(f[0]))}</th>' + ''.join(celda(v) for v in f[1:]) + '</tr>' for f in t['filas'])
    return f'<div class="tbl"><table><caption>{escape(t["caption"])}</caption><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'


def ld_pieza(p, ruta):
    revisado = bool(p['revisado'])
    art = {'@type': 'NewsArticle', '@id': url(ruta) + '#articulo', 'headline': titular(p), 'alternativeHeadline': p['titulo'], 'description': p['resumen'],
           'url': url(ruta), 'inLanguage': 'es', 'datePublished': publicado(p), 'image': imagen(p), 'dateModified': HOY,
           'author': AUTOR, 'publisher': {'@type': 'Organization', 'name': NOMBRE, 'url': ATLAS_URL},
           'isPartOf': {'@type': 'CollectionPage', 'name': SERIES[p['serie']][0], 'url': url(p['serie'] + '/index.html')},
           'about': [{'@type': 'Place', 'name': l} for l in p['lugares']] + [{'@type': 'Thing', 'name': 'Elecciones en España'}],
           'citation': [n for k in p['fuentes'] for n in [FUENTES[k][0]]],
           'license': LICENCIA, 'isAccessibleForFree': True}
    if revisado:
        art['editor'] = {'@type': 'Person', 'name': FIRMA}
    ds = {'@type': 'Dataset', '@id': url(ruta) + '#datos', 'name': 'Datos de «' + p['titulo'] + '»', 'description': p['compara'],
          'url': url(ruta), 'license': LICENCIA, 'creator': AUTOR, 'temporalCoverage': p['fecha_datos'],
          'spatialCoverage': {'@type': 'Place', 'name': 'España'},
          'isBasedOn': [FUENTES[k][1] for k in p['fuentes'] if FUENTES[k][1]],
          'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': url('datos/' + p['csv'])}]}
    g = [art, ds]
    if p.get('faq'):
        g.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in p['faq']]})
    return {'@context': 'https://schema.org', '@graph': g}


ETIQ = {'dato': 'Dato', 'patrón': 'Patrón'}


# enlaces al mapa de resultados (?m=<código INE>&e=<elección>): un municipio por cada lugar de la pieza
MUN_MAPA = json.loads((ROOT / 'generales-2026' / 'data' / 'municipios.json').read_text(encoding='utf-8'))
MAPA_HOMONIMOS = {'Mieres': '33037'}   # hay otro Mieres en Girona; las piezas hablan del asturiano
MAPA_ELECCION = {'capitales-municipales': 'M2023', 'europeas-2024': 'E2024'}   # el resto abre las generales de 2023


def enlaces_mapa(p):
    if p['serie'] == 'bisagras':   # sus lugares son provincias, no municipios
        return []
    out = []
    for lugar in p['lugares']:
        cods = [MAPA_HOMONIMOS[lugar]] if lugar in MAPA_HOMONIMOS else \
               [c for c, n in zip(MUN_MAPA['cod'], MUN_MAPA['nombre']) if lugar == n or lugar in n.split('/')]
        if len(cods) == 1:
            e = MAPA_ELECCION.get(p['slug'])
            out.append((lugar, f'{cods[0]}' + (f'&amp;e={e}' if e else '')))
    return out


TIPO_CLASE = {'Dato': 't-dato', 'Patrón': 't-patron', 'Hipótesis': 't-hipotesis'}


def tipo(t):
    return f'<span class="tipo {TIPO_CLASE[t]}">{t}</span>'


def sigue_leyendo(p):
    """Dos piezas de la misma serie (las más recientes) y una de otra serie, siempre la misma para cada pieza."""
    misma = [q for q in recientes() if q['serie'] == p['serie'] and q['slug'] != p['slug']][:2]
    otras = [q for q in TODAS if q['serie'] != p['serie']]
    if otras:
        misma.append(otras[sum(map(ord, p['slug'])) % len(otras)])
    return misma


def pagina_pieza(p):
    ruta = ruta_pieza(p)
    rev = p['revisado']
    tt = titular(p)
    h = [cabeza(f'{tt} · {NOMBRE}', p['resumen'], ruta, ld_pieza(p, ruta), indexar=bool(rev), nivel=2, img=imagen(p))]
    if p.get('foto'):
        f = p['foto']
        h.append(f'<figure class="foto apertura"><img src="{escape(f["src"])}" alt="{escape(f["alt"])}" fetchpriority="high">'
                 f'<figcaption>{escape(f["alt"])}. Foto: <a href="{escape(f["url"])}">{escape(f["autor"])}</a>, {escape(f["licencia"])}, Wikimedia Commons.</figcaption></figure>')
    h.append(f'<p class="kicker"><a href="../index.html">{escape(SERIES[p["serie"]][0])}</a> · Elecciones: {escape(p["fecha_datos"])}</p>')
    h.append(f'<h1>{escape(tt)}</h1>')
    if tt != p['titulo']:
        h.append(f'<p class="subtitulo">{escape(p["titulo"])}</p>')
    h.append(f'<p class="firma">Por <a href="../../../sobre-mi.html">{FIRMA}</a> · <time datetime="{publicado(p)}">{fecha_txt(publicado(p))}</time></p>')
    h.append(f'<p class="resumen">{escape(p["resumen"])}</p>')
    h.append(f'<p><span class="estado">{escape(p["estado"])}: {"verificable y reproducible" if p["estado"] == "Dato" else "relación descriptiva, no causa"}</span></p>')
    if not rev:
        h.append('<p class="aviso">Revisión pendiente: los datos y el texto de esta página aún no han pasado la comprobación manual. No se publica en buscadores hasta que se complete.</p>')
    if enlaces_mapa(p):
        h.append('<p class="mapa-enlaces">' + ''.join(f'<a class="vermapa" href="../../../{GENERALES}index.html?m={q}">Ver {escape(l)} en el mapa →</a>' for l, q in enlaces_mapa(p)) + '</p>')
    h.append(f'<p><strong>La pregunta:</strong> {escape(p["pregunta"])}</p>')
    if p.get('grafico'):
        svg, cap = p['grafico']
        h.append(f'<figure>{svg}<figcaption>{escape(cap)} Datos en la tabla de abajo y en <a href="../../datos/{p["csv"]}">CSV</a>.</figcaption></figure>')
    h.append('<div class="cuerpo">')
    for t, texto in p['cuerpo']:
        h.append(f'<h2>{escape(texto)}</h2>' if t == 'sub' else f'<p>{tipo(ETIQ[t])}{escape(texto)}</p>')
    h.append('</div>')
    if p.get('color'):
        h.append('<div class="terreno"><h2>Sobre el terreno</h2>' + ''.join(f'<p>{tipo("Dato")}{escape(t)} <span class="fuentes-nota">Fuentes: ' + ', '.join(f'<a href="{escape(u)}">{i}</a>' for i, u in enumerate(us, 1)) + '</span></p>' for t, us in p['color']) + '</div>')
    h.append('<h2>Lo que no sabemos</h2><ul class="hipotesis">' + ''.join(f'<li>{tipo("Hipótesis")}{escape(x)}</li>' for x in p['no_sabemos']) + '</ul>')
    h.append('<p class="leyenda"><b>Dato</b>: verificable y reproducible. <b>Patrón</b>: relación descriptiva, sin causa. <b>Hipótesis</b>: explicación posible que aún no tiene dos fuentes independientes.</p>')
    h.append('<h2>Los datos</h2>' + tabla(p['tabla']) + f'<p><a href="../../datos/{p["csv"]}">Descargar los datos en CSV</a></p>')
    if p.get('faq'):
        h.append('<h2>Preguntas</h2>' + ''.join(f'<h3>{escape(q)}</h3><p>{escape(a)}</p>' for q, a in p['faq']))
    fuentes = ''.join(f'<li>{f"<a href=\"{FUENTES[k][1]}\">" if FUENTES[k][1] else ""}{escape(FUENTES[k][0])}{"</a>" if FUENTES[k][1] else ""}</li>' for k in p['fuentes'])
    h.append(f"""<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se compara</dt><dd>{escape(p['compara'])}</dd>
<dt>Límites</dt><dd>{escape(p['limites'])}</dd>
<dt>Metodología completa</dt><dd><a href="../../metodologia/index.html">Cómo se calculan los porcentajes, el modelo, los gemelos y los escaños</a></dd>
<dt>Fuentes</dt><dd><ul>{fuentes}</ul></dd>
<dt>Autoría</dt><dd>{FIRMA}</dd>
<dt>Revisión de datos y texto</dt><dd>{f'{FIRMA}, {fecha_txt(rev)}' if rev else 'Pendiente'}</dd>
<dt>Publicado · actualizado</dt><dd>{fecha_txt(publicado(p))} · {fecha_txt(HOY)}</dd>
<dt>Correcciones</dt><dd>{escape(p.get('correcciones') or 'Ninguna.')} <a href="../../correcciones/index.html">Historial del Atlas</a></dd>
</dl>""")
    h.append('<h2>Sigue leyendo</h2><ul class="sigue">' + ''.join(
        f'<li><a href="../../{ruta_pieza(q)}"><span class="kicker">{escape(SERIES[q["serie"]][0])}</span><b>{escape(titular(q))}</b></a></li>' for q in sigue_leyendo(p)) + '</ul>')
    h.append(f'<p><a href="../index.html">Todas las piezas de «{escape(SERIES[p["serie"]][0])}»</a> · <a href="../../index.html">Todo el Atlas</a></p>')
    h.append(siguelo())
    h.append(PIE)
    return ruta, ''.join(h)


def entradilla(resumen):
    """Primera frase del resumen; si es muy corta, las dos primeras."""
    fr = resumen.split('. ')
    return '. '.join(fr[:2 if len(fr[0]) < 60 and len(fr) > 1 else 1]).rstrip('.') + '.'


def tarjetas(lista, pref='', serie=False):
    """Cada pieza es una tarjeta entera enlazada: foto (si la tiene), serie, titular, subtítulo y «Leer la pieza».
    Sin foto, el hueco lleva el nombre de la serie y no se repite encima del titular. En pantallas anchas van en dos columnas."""
    def img(q):
        if not q.get('foto'):
            return f'<span class="sinfoto">{escape(SERIES[q["serie"]][0])}</span>'
        return f'<img src="{pref}img/m/{q["slug"]}.jpg" alt="{escape(q["foto"]["alt"])}" loading="lazy">'
    return '<ul class="tarjetas">' + ''.join(
        f'<li><a class="tarjeta" href="{pref}{ruta_pieza(q)}">{img(q)}<span class="txt">'
        + (f'<span class="kicker">{escape(SERIES[q["serie"]][0])}</span>' if serie and q.get('foto') else '') +
        f'<span class="tt">{escape(titular(q))}</span>'
        f'<span class="ent">{escape(q["titulo"] if titular(q) != q["titulo"] else entradilla(q["resumen"]))}</span>'
        f'<span class="leer">Leer la pieza →{"" if q["revisado"] else " · revisión pendiente"}</span></span></a></li>' for q in lista) + '</ul>'


def destacada(q, pref=''):
    foto = f'<img src="{pref}img/m/{q["slug"]}.jpg" alt="{escape(q["foto"]["alt"])}">' if q.get('foto') else ''
    return (f'<a class="destacada" href="{pref}{ruta_pieza(q)}">{foto}<span class="txt"><span class="kicker">{escape(SERIES[q["serie"]][0])} · {fecha_txt(publicado(q))}</span>'
            f'<span class="tt">{escape(titular(q))}</span><span class="ent">{escape(q["titulo"])}</span></span></a>')


def portada():
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': NOMBRE, 'url': ATLAS_URL, 'inLanguage': 'es', 'author': AUTOR,
          'description': 'Piezas sobre lugares que votan distinto de lo que cabría esperar: excepciones, fronteras, gemelos y escaños decididos por pocos votos.',
          'image': imagen(),
          'hasPart': [{'@type': 'NewsArticle', 'headline': titular(q), 'url': url(ruta_pieza(q))} for q in TODAS if q['revisado']]}
    h = [cabeza(NOMBRE, ld['description'], 'index.html', ld, nivel=0)]
    h.append(f'<p class="kicker">Periodismo de datos electorales · {len(TODAS)} piezas en {len({q["serie"] for q in TODAS})} series</p><h1>{NOMBRE}</h1>')
    h.append('<p class="resumen">Los resultados generales esconden lugares que votan distinto de lo que cabría esperar por sus vecinos, por los municipios que más se les parecen o por su propia historia. Cada pieza parte de una de esas comparaciones, enseña los datos y separa lo que se sabe de lo que todavía es hipótesis.</p>')
    orden = recientes()
    top = next((q for q in orden if q.get('foto')), orden[0])
    h.append(destacada(top))
    h.append('<h2>Lo último</h2>' + tarjetas([q for q in orden if q is not top][:4], serie=True))
    h.append(f'<p>Los resultados de todos los municipios se consultan en el <a href="../{GENERALES}index.html">mapa de resultados de España</a>. El Atlas no tiene fichas municipales: solo piezas con una pregunta y una respuesta.</p>')
    for s, (nombre, desc) in SERIES.items():
        ps = [q for q in orden if q['serie'] == s]
        if ps:
            h.append(f'<h2 class="serie" id="{s}"><a href="{s}/index.html">{escape(nombre)}</a><small>{len(ps)} {"pieza" if len(ps) == 1 else "piezas"}</small></h2>'
                     f'<p class="serie-desc">{escape(desc)}</p>' + tarjetas(ps))
    h.append('<h2>Cómo trabajamos</h2><p>Cada afirmación se marca como <strong>dato</strong> (verificable y reproducible), <strong>patrón</strong> (relación descriptiva, sin causa) o <strong>hipótesis</strong> (explicación posible que aún no tiene dos fuentes independientes). Ninguna pieza se publica sin revisión humana. <a href="metodologia/index.html">Metodología</a> · <a href="correcciones/index.html">Correcciones</a></p>')
    h.append(siguelo())
    h.append(PIE)
    return 'index.html', ''.join(h)


def pagina_serie(s):
    nombre, desc = SERIES[s]
    ps = [q for q in recientes() if q['serie'] == s]
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': nombre, 'description': desc, 'url': url(s + '/index.html'),
          'isPartOf': {'@type': 'CollectionPage', 'name': NOMBRE, 'url': ATLAS_URL},
          'hasPart': [{'@type': 'NewsArticle', 'headline': titular(q), 'url': url(ruta_pieza(q))} for q in ps if q['revisado']]}
    h = [cabeza(f'{nombre} · {NOMBRE}', desc, s + '/index.html', ld, indexar=any(q['revisado'] for q in ps), nivel=1)]
    h.append(f'<p class="kicker"><a href="../index.html">{NOMBRE}</a> · Serie</p><h1>{escape(nombre)}</h1><p class="resumen">{escape(desc)}</p>')
    h.append(tarjetas(ps, '../'))
    otras = [(k, n) for k, (n, _) in SERIES.items() if k != s and any(q['serie'] == k for q in TODAS)]
    h.append('<h2>Otras series</h2><p>' + ' · '.join(f'<a href="../{k}/index.html">{escape(n)}</a>' for k, n in otras) + '</p>')
    h.append(siguelo())
    h.append(PIE)
    return s + '/index.html', ''.join(h)


def metodologia(C):
    ld = {'@context': 'https://schema.org', '@type': 'TechArticle', 'headline': 'Metodología del ' + NOMBRE, 'url': url('metodologia/index.html'),
          'author': AUTOR, 'inLanguage': 'es', 'dateModified': HOY}
    h = [cabeza('Metodología · ' + NOMBRE, 'Cómo se calculan los porcentajes, el modelo de lo previsto, los gemelos, las fronteras y los escaños del Atlas.', 'metodologia/index.html', ld, nivel=1)]
    fam = ', '.join(f'{k} {v}' for k, v in C['escanos_2023_con_cera'].items())
    h.append(f"""<p class="kicker">Metodología</p><h1>Cómo se hace el Atlas</h1>
<p class="resumen">Todas las cifras salen de los resultados oficiales por mesa del Ministerio del Interior y de los indicadores del INE por municipio y sección censal. Ninguna se escribe a mano: un script las calcula y otro las comprueba antes de generar las páginas.</p>
<h2>Porcentajes de voto</h2>
<p>Votos de la candidatura entre voto válido (votos a candidaturas más votos en blanco), como en el escrutinio oficial. La participación es votantes entre censo de residentes en España; no incluye el voto desde el extranjero (CERA) salvo donde se dice, como en el reparto de escaños. Cuando se agrupan varios municipios, el porcentaje es la suma de votos entre la suma de voto válido, no la media de porcentajes.</p>
<h2>Familias de partidos</h2>
<p>Para comparar elecciones, las candidaturas se agrupan en familias: el PP incluye sus coaliciones regionales y UPN; el PSOE, al PSC y sus federaciones; «Sumar» reúne el espacio a la izquierda del PSOE en cada momento (IU, Podemos y sus confluencias, Compromís, Más País, Más Madrid y Sumar). «Derecha» en una pieza significa PP + Vox + Cs, y «izquierda estatal», PSOE + Sumar. PRC, Més per Mallorca y los partidos regionalistas o locales quedan en «Otros». La tabla completa está en <code>generales-2026/partidos.py</code> del repositorio.</p>
<h2>Lo que predicen los datos (serie «Las excepciones»)</h2>
<p>Un modelo de regresión lineal, ponderado por censo, estima el voto a PP + Vox + Cs del 23J en cada municipio a partir de seis indicadores (renta por unidad de consumo en logaritmo, edad media, porcentaje de extranjeros, estudios superiores, paro y tamaño en logaritmo) y de su provincia. Se estima con los {C['modelo_municipal']['n']:,} municipios con todos los datos y explica el {C['modelo_municipal']['r2_derecha'] * 100:.0f} % de las diferencias entre ellos. La diferencia entre el voto real y el previsto señala dónde mirar; no es una explicación.</p>
<h2>Gemelos</h2>
<p>Se estandarizan los seis indicadores anteriores y se buscan pares de municipios de más de 15.000 habitantes, de la misma comunidad autónoma, con una distancia euclídea menor de 0,6 desviaciones típicas. Entre ellos se eligen los pares con mayor diferencia de voto.</p>
<h2>Fronteras</h2>
<p>Pares de municipios de más de 3.000 habitantes cuyos centros están a menos de 7 km, ordenados por la diferencia de voto.</p>
<h2>Escaños</h2>
<p>Reparto D'Hondt por provincia con la barrera del 3 % del voto válido, con los votos por mesa de Interior incluido el CERA. Con los votos de 2023 reproduce los 350 escaños oficiales ({fam}). «Votos que faltaban» es el mínimo de votos adicionales con el que la lista aspirante habría superado el último cociente asignado, sin restar votos a nadie.</p>
<h2>Revisión</h2>
<p>Cada pieza pasa por: datos descargados, controles automáticos (<code>atlas/src/controles.py</code>: totales, escaños oficiales, cifras del texto frente a los datos, valores ausentes), comprobación manual de una muestra de municipios frente a la web oficial de resultados, redacción con cada afirmación etiquetada y revisión de datos y texto. Solo entonces se publica, con la fecha de revisión visible en la página.</p>
<h2>Límites</h2>
<ul><li>Los datos son agregados por municipio o sección: no dicen cómo vota cada persona ni quién cambia su voto.</li>
<li>Paro, estudios y extranjeros por sección son del censo de 2021; renta y edad, de 2023.</li>
<li>En las municipales y europeas el censo incluye a residentes de la Unión Europea; no es directamente comparable con el de las generales.</li></ul>""")
    h.append(PIE)
    return 'metodologia/index.html', ''.join(h)


def datos():
    ld = {'@context': 'https://schema.org', '@type': 'Dataset', 'name': 'Datos del ' + NOMBRE, 'url': url('datos/index.html'), 'license': LICENCIA, 'creator': AUTOR,
          'description': 'Tablas en CSV con las cifras de cada pieza del Atlas de las anomalías electorales, calculadas desde los resultados por mesa de Interior y los indicadores del INE.',
          'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': url('datos/' + f.name)} for f in sorted((ATLAS / 'datos').glob('*.csv'))]}
    h = [cabeza('Datos · ' + NOMBRE, ld['description'], 'datos/index.html', ld, nivel=1)]
    h.append('<p class="kicker">Datos abiertos</p><h1>Datos del Atlas</h1><p class="resumen">Cada pieza publica sus datos en CSV con licencia CC BY 4.0. Los resultados de todos los municipios de España están en el <a href="../../' + GENERALES + 'index.html">mapa de resultados</a> y en sus descargas.</p>')
    usos = {q['csv']: q for q in TODAS}
    h.append('<div class="tbl"><table><caption>Ficheros</caption><thead><tr><th scope="col">Fichero</th><th scope="col">Pieza</th></tr></thead><tbody>' +
             ''.join(f'<tr><th scope="row"><a href="{f.name}">{f.name}</a></th><td>{escape(usos[f.name]["titulo"]) if f.name in usos else "Modelo municipal: voto real y previsto, municipios de más de 10.000 habitantes"}</td></tr>'
                     for f in sorted((ATLAS / 'datos').glob('*.csv'))) + '</tbody></table></div>')
    h.append(PIE)
    return 'datos/index.html', ''.join(h)


def correcciones():
    ld = {'@context': 'https://schema.org', '@type': 'WebPage', 'name': 'Correcciones · ' + NOMBRE, 'url': url('correcciones/index.html')}
    h = [cabeza('Correcciones · ' + NOMBRE, 'Historial de correcciones de datos y conclusiones del Atlas.', 'correcciones/index.html', ld, nivel=1)]
    h.append('<p class="kicker">Transparencia</p><h1>Correcciones</h1><p class="resumen">Si cambia un dato o una conclusión de una pieza ya publicada, se anota aquí y en la propia pieza, con la fecha y qué cambió. La dirección de la página no cambia.</p><p>Todavía no hay correcciones.</p>')
    h.append(PIE)
    return 'correcciones/index.html', ''.join(h)


def sitemap(rutas):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
            ''.join(f'  <url><loc>{url(r).replace("index.html", "")}</loc><lastmod>{HOY}</lastmod></url>\n' for r in rutas) + '</urlset>\n')


def llms():
    l = [f'# {NOMBRE}', '', '> Piezas de periodismo de datos sobre lugares de España que votan distinto de lo esperado. Cada cifra sale de los resultados por mesa del Ministerio del Interior y de indicadores del INE; cada afirmación se etiqueta como dato, patrón o hipótesis.', '',
         '## Piezas', '']
    l += [f'- [{titular(q)}]({url(q["serie"] + "/" + q["slug"] + "/")}): {q["titulo"]}. {q["resumen"]}' for q in recientes() if q['revisado']]
    l += ['', '## Referencia', '', f'- [Metodología]({url("metodologia/")})', f'- [Datos en CSV]({url("datos/")})', f'- [Correcciones]({url("correcciones/")})', '']
    return '\n'.join(l)


def feed():
    """RSS 2.0 con las piezas revisadas, de la más nueva a la más antigua."""
    def rfc(iso):
        d = datetime.date.fromisoformat(iso)
        return d.strftime('%a, %d %b %Y 08:00:00 +0200')
    items = ''.join(
        f"""  <item>
    <title>{escape(titular(q))}</title>
    <link>{url(ruta_pieza(q))}</link>
    <guid isPermaLink="true">{url(ruta_pieza(q))}</guid>
    <pubDate>{rfc(publicado(q))}</pubDate>
    <category>{escape(SERIES[q['serie']][0])}</category>
    <description>{escape(q['titulo'] + '. ' + q['resumen'])}</description>
    <enclosure url="{imagen(q)}" type="image/jpeg" length="0"/>
  </item>
""" for q in recientes() if q['revisado'])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>{NOMBRE} · {SITIO}</title>
  <link>{ATLAS_URL}</link>
  <atom:link href="{ATLAS_URL}feed.xml" rel="self" type="application/rss+xml"/>
  <description>Piezas de periodismo de datos sobre los lugares de España que votan distinto de lo que cabría esperar. Por {FIRMA}.</description>
  <language>es-es</language>
{items}</channel>
</rss>
"""


def franja_portada():
    """Las tres últimas piezas del Atlas en la portada del sitio, entre las marcas <!--atlas:ultimas-->.
    La plantilla de generales-2026 lleva las marcas vacías; este script las rellena cada vez que se regenera el Atlas."""
    ult = [q for q in recientes() if q['revisado']][:3]
    return ('<section class="col del-atlas" aria-labelledby="h-del-atlas"><h2 id="h-del-atlas"><a href="atlas/">Del Atlas de las anomalías</a></h2><ul>' +
            ''.join(f'<li><a href="atlas/{ruta_pieza(q).replace("index.html", "")}"><span class="atlas-k">{escape(SERIES[q["serie"]][0])}</span>'
                    f'<b>{escape(titular(q))}</b><span>{escape(q["titulo"])}</span></a></li>' for q in ult) +
            f'</ul><p><a class="atlas-go" href="atlas/">Las {sum(1 for q in TODAS if q["revisado"])} piezas del Atlas →</a></p></section>')


def compartir():
    """Lista que lee compartir.mjs para dibujar las imágenes de redes (1200 × 630) de cada pieza y del índice."""
    lista = [{'archivo': f'atlas-{q["slug"]}.jpg', 'serie': SERIES[q['serie']][0], 'titular': titular(q), 'subtitulo': q['titulo'],
              'foto': f'atlas/img/m/{q["slug"]}.jpg' if q.get('foto') else None} for q in TODAS]
    lista.append({'archivo': 'atlas.jpg', 'serie': f'{len(TODAS)} piezas en {len({q["serie"] for q in TODAS})} series', 'titular': NOMBRE,
                  'subtitulo': 'Los lugares de España que votan distinto de lo que cabría esperar: excepciones, fronteras, gemelos y escaños decididos por pocos votos.',
                  'foto': next((f'atlas/img/m/{q["slug"]}.jpg' for q in recientes() if q.get('foto')), None)})
    return lista


def main():
    global TODAS
    C = json.loads((ATLAS / 'src' / 'cifras.json').read_text())
    TODAS = piezas(C) + piezas2(C) + piezas3(C)
    paginas = [pagina_pieza(p) for p in TODAS] + [portada(), metodologia(C), datos(), correcciones()]
    paginas += [pagina_serie(s) for s in SERIES if any(q['serie'] == s for q in TODAS)]
    for ruta, html in paginas:
        f = ATLAS / ruta
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html)
    publicables = ['index.html', 'metodologia/index.html', 'datos/index.html', 'correcciones/index.html']
    publicables += [f'{q["serie"]}/{q["slug"]}/index.html' for q in TODAS if q['revisado']]
    publicables += [f'{s}/index.html' for s in SERIES if any(q['serie'] == s and q['revisado'] for q in TODAS)]
    (ATLAS / 'sitemap.xml').write_text(sitemap(publicables))
    (ATLAS / 'llms.txt').write_text(llms())
    (ATLAS / 'feed.xml').write_text(feed())
    (ATLAS / 'src' / 'compartir.json').write_text(json.dumps(compartir(), ensure_ascii=False, indent=1))
    # franja «Del Atlas» de la portada del sitio
    for f in (ROOT / 'index.html', ROOT / 'generales-2026' / 'src' / 'plantilla.html'):
        t = f.read_text(encoding='utf-8')
        if '<!--atlas:ultimas-->' in t:
            pre = '' if f.name == 'index.html' else '../'
            franja = franja_portada().replace('href="atlas/', f'href="{pre}atlas/')
            t = re.sub(r'<!--atlas:ultimas-->.*?<!--/atlas:ultimas-->', lambda m: '<!--atlas:ultimas-->' + franja + '<!--/atlas:ultimas-->', t, flags=re.S)
            f.write_text(t, encoding='utf-8')
    print(len(paginas), 'páginas;', sum(1 for q in TODAS if q['revisado']), 'de', len(TODAS), 'piezas revisadas')


TODAS = []
if __name__ == '__main__':
    main()
