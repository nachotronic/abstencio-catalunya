"""Genera las páginas estáticas del Atlas de las anomalías electorales en atlas/.

Todo el contenido está en el HTML (sin depender de JavaScript): titular, resumen, gráfico SVG, tabla, método,
fuentes, autoría, revisión e historial de correcciones, más los datos estructurados schema.org.
Uso (después de construir.py y controles.py):  python3 atlas/src/paginas.py
"""
import datetime, json, pathlib, sys
from html import escape

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from piezas import piezas, SERIES  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
ATLAS = ROOT / 'atlas'
BASE = 'https://mapaelectoral.es/'
ATLAS_URL = BASE + 'atlas/'
NOMBRE = 'Atlas de las anomalías electorales'
AUTOR = {'@type': 'Person', 'name': 'Nacho', 'url': BASE + 'sobre-mi.html', 'sameAs': ['https://github.com/nachotronic']}
LICENCIA = 'https://creativecommons.org/licenses/by/4.0/'
REPO = 'https://github.com/nachotronic/abstencio-catalunya'
CF = '''<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "d27e4ef550c94f82912044da926a3b0f"}'></script><!-- End Cloudflare Web Analytics -->'''
HOY = datetime.date.today().isoformat()
PUBLICADO = '2026-10-06'
# página de resultados de España (la pieza de las generales); se mueve a /generales-2026/
GENERALES = ''   # el mapa de resultados de España es la portada del sitio (index.html en la raíz)

FUENTES = {
    'interior': ('Ministerio del Interior, resultados electorales por mesa (Infoelectoral). Congreso 2004-2023 vía pollspaindata, commit ee5ecda; municipales 2007-2023 de los ficheros de Infoelectoral',
                 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/'),
    'pollspain': ('pollspaindata: copia procesada de los ficheros por mesa de Interior', 'https://github.com/dadosdelaplace/pollspaindata'),
    'ine_adrh': ('INE, Atlas de Distribución de Renta de los Hogares 2023 (renta, edad, población), vía ineAtlas.data', 'https://www.ine.es/experimental/atlas/experimental_atlas.htm'),
    'ine_censo': ('INE, Censo de Población y Viviendas 2021 (estudios, paro, extranjeros)', 'https://www.ine.es/censos2021/'),
    'transparencia': ('Generalitat de Catalunya, participación por sección censal (Transparència Catalunya, irrv-2mfc)', 'https://analisi.transparenciacatalunya.cat/d/irrv-2mfc'),
    'decreto29n': ('Real Decreto de disolución de las Cortes y convocatoria de elecciones para el 29 de noviembre de 2026 (BOE, 6 de octubre de 2026): escaños por provincia', None),
}

CSS = """
:root{--bg:#f4f5f8;--surface:#fff;--fg:#161a2b;--muted:#5b6178;--rule:#d9dce6;--accent:#3846a0;--accent2:#b0452c;--pp:#1d6fb8;--psoe:#d1262d;--warn:#fff4d6;--warnfg:#6b4e00;
  --display:"Bricolage Grotesque","Arial Narrow",system-ui,sans-serif;--body:"Newsreader",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12141d;--surface:#1a1d29;--fg:#e8eaf2;--muted:#9aa0b8;--rule:#2c3042;--accent:#8f9cf0;--accent2:#ef8a6a;--pp:#5aa7ee;--psoe:#f06a6f;--warn:#3a3218;--warnfg:#f2d98a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#12141d;--surface:#1a1d29;--fg:#e8eaf2;--muted:#9aa0b8;--rule:#2c3042;--accent:#8f9cf0;--accent2:#ef8a6a;--pp:#5aa7ee;--psoe:#f06a6f;--warn:#3a3218;--warnfg:#f2d98a;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--body);font-size:1.1rem;line-height:1.6;padding:0 16px 64px}
main{max-width:72ch;margin:0 auto}
nav.top{display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;padding:20px 0;font-family:var(--mono);font-size:.8rem}
a{color:var(--accent)}
h1,h2,h3{font-family:var(--display);line-height:1.12;text-wrap:balance}
h1{font-size:clamp(1.9rem,5.5vw,2.9rem);font-weight:800;margin:.3rem 0 1rem}
h2{font-size:1.35rem;margin:2.4rem 0 .6rem}
h3{font-size:1.1rem;margin:1.6rem 0 .4rem}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.resumen{font-size:1.22rem;line-height:1.5}
.estado{display:inline-block;font-family:var(--mono);font-size:.76rem;border:1px solid var(--rule);border-radius:4px;padding:2px 8px;margin-right:6px;background:var(--surface)}
.aviso{background:var(--warn);color:var(--warnfg);border-radius:6px;padding:10px 14px;font-family:var(--mono);font-size:.82rem;margin:1rem 0}
.tipo{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-right:6px}
figure{margin:1.6rem 0;background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:14px}
figcaption{font-family:var(--mono);font-size:.78rem;color:var(--muted);margin-top:8px}
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
.tarjetas{list-style:none;padding:0;display:grid;gap:12px}
.tarjetas li{margin:0}
a.tarjeta{display:flex;flex-direction:column;gap:6px;background:var(--surface);border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:8px;padding:14px 18px;color:var(--fg);text-decoration:none;transition:border-color .15s,transform .15s}
a.tarjeta:hover,a.tarjeta:focus-visible{border-color:var(--accent);transform:translateY(-1px)}
a.tarjeta .tt{font-family:var(--display);font-weight:700;font-size:1.15rem;line-height:1.25;color:var(--fg)}
a.tarjeta .ent{font-size:1rem;color:var(--muted)}
a.tarjeta .leer{font-family:var(--mono);font-size:.8rem;color:var(--accent);font-weight:600}
.cuerpo h2{font-size:1.25rem;margin:2.2rem 0 .5rem}
.cuerpo p{margin:0 0 1rem}
footer{margin-top:3rem;font-family:var(--mono);font-size:.76rem;color:var(--muted)}
"""


def url(p):
    return ATLAS_URL + p


def cabeza(titulo, desc, ruta, ld, indexar=True, nivel=0):
    rel = '../' * nivel
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="author" content="Nacho">
<meta name="robots" content="{'index, follow, max-image-preview:large' if indexar else 'noindex, follow'}">
<link rel="canonical" href="{url(ruta)}">
<meta property="og:type" content="article">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url(ruta)}">
<meta property="og:locale" content="es_ES">
<link rel="license" href="{LICENCIA}">
<link rel="alternate" type="text/plain" title="llms.txt" href="{rel}llms.txt">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1)}
</script>
{CF}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800&family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main>
<nav class="top"><a href="{rel}index.html">{NOMBRE}</a><span><a href="{rel}metodologia/index.html">Metodología</a> · <a href="{rel}datos/index.html">Datos</a> · <a href="{rel}../{GENERALES}index.html">Resultados de España</a></span></nav>
"""


PIE = f"""<footer>{NOMBRE} · Datos con licencia <a href="{LICENCIA}">CC BY 4.0</a> · <a href="{REPO}">Código y datos</a></footer>
</main>
</body>
</html>
"""


def tabla(t):
    def celda(v, tag='td'):
        es_num = isinstance(v, (int, float)) or (isinstance(v, str) and v[:1] in '+-0123456789' and any(c.isdigit() for c in v[:3]))
        return f'<{tag}{" class=\"n\"" if es_num else ""}>{escape(str(v))}</{tag}>'
    cab = ''.join(f'<th scope="col"{" class=\"n\"" if i else ""}>{escape(h)}</th>' for i, h in enumerate(t['cabecera']))
    filas = ''.join('<tr>' + f'<th scope="row">{escape(str(f[0]))}</th>' + ''.join(celda(v) for v in f[1:]) + '</tr>' for f in t['filas'])
    return f'<div class="tbl"><table><caption>{escape(t["caption"])}</caption><thead><tr>{cab}</tr></thead><tbody>{filas}</tbody></table></div>'


def ld_pieza(p, ruta):
    revisado = bool(p['revisado'])
    art = {'@type': 'NewsArticle', '@id': url(ruta) + '#articulo', 'headline': p['titulo'], 'description': p['resumen'],
           'url': url(ruta), 'inLanguage': 'es', 'datePublished': PUBLICADO, 'dateModified': HOY,
           'author': AUTOR, 'publisher': {'@type': 'Organization', 'name': NOMBRE, 'url': ATLAS_URL},
           'isPartOf': {'@type': 'CollectionPage', 'name': SERIES[p['serie']][0], 'url': url(p['serie'] + '/index.html')},
           'about': [{'@type': 'Place', 'name': l} for l in p['lugares']] + [{'@type': 'Thing', 'name': 'Elecciones en España'}],
           'citation': [n for k in p['fuentes'] for n in [FUENTES[k][0]]],
           'license': LICENCIA, 'isAccessibleForFree': True}
    if revisado:
        art['editor'] = {'@type': 'Person', 'name': 'Nacho'}
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


def pagina_pieza(p):
    ruta = f'{p["serie"]}/{p["slug"]}/index.html'
    rev = p['revisado']
    h = [cabeza(p['titulo'], p['resumen'], ruta, ld_pieza(p, ruta), indexar=bool(rev), nivel=2)]
    h.append(f'<p class="kicker"><a href="../index.html">{escape(SERIES[p["serie"]][0])}</a> · Elecciones: {escape(p["fecha_datos"])}</p>')
    h.append(f'<h1>{escape(p["titulo"])}</h1>')
    h.append(f'<p class="resumen">{escape(p["resumen"])}</p>')
    h.append(f'<p><span class="estado">{escape(p["estado"])}: {"verificable y reproducible" if p["estado"] == "Dato" else "relación descriptiva, no causa"}</span></p>')
    if not rev:
        h.append('<p class="aviso">Revisión pendiente: los datos y el texto de esta página aún no han pasado la comprobación manual. No se publica en buscadores hasta que se complete.</p>')
    h.append(f'<p><strong>La pregunta:</strong> {escape(p["pregunta"])}</p>')
    if p.get('grafico'):
        svg, cap = p['grafico']
        h.append(f'<figure>{svg}<figcaption>{escape(cap)} Datos en la tabla de abajo y en <a href="../../datos/{p["csv"]}">CSV</a>.</figcaption></figure>')
    h.append('<div class="cuerpo">')
    for tipo, texto in p['cuerpo']:
        h.append(f'<h2>{escape(texto)}</h2>' if tipo == 'sub' else f'<p><span class="tipo">{ETIQ[tipo]}</span>{escape(texto)}</p>')
    h.append('</div>')
    h.append('<h2>Lo que no sabemos</h2><ul>' + ''.join(f'<li><span class="tipo">Hipótesis</span>{escape(x)}</li>' for x in p['no_sabemos']) + '</ul>')
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
<dt>Autoría</dt><dd>Nacho</dd>
<dt>Revisión de datos y texto</dt><dd>{f'Nacho, {rev}' if rev else 'Pendiente'}</dd>
<dt>Publicado · actualizado</dt><dd>{PUBLICADO} · {HOY}</dd>
<dt>Correcciones</dt><dd>{escape(p.get('correcciones') or 'Ninguna.')} <a href="../../correcciones/index.html">Historial del Atlas</a></dd>
</dl>""")
    otras = [q for q in TODAS if q['serie'] == p['serie'] and q['slug'] != p['slug']]
    if otras:
        h.append('<h2>En esta serie</h2><ul>' + ''.join(f'<li><a href="../{q["slug"]}/index.html">{escape(q["titulo"])}</a></li>' for q in otras) + '</ul>')
    h.append(PIE)
    return ruta, ''.join(h)


def entradilla(resumen):
    """Primera frase del resumen; si es muy corta, las dos primeras."""
    fr = resumen.split('. ')
    return '. '.join(fr[:2 if len(fr[0]) < 60 and len(fr) > 1 else 1]).rstrip('.') + '.'


def tarjetas(lista, pref='', serie=False):
    """Cada pieza es una tarjeta entera enlazada: serie, titular, entradilla y «Leer la pieza»."""
    return '<ul class="tarjetas">' + ''.join(
        f'<li><a class="tarjeta" href="{pref}{q["serie"]}/{q["slug"]}/index.html">'
        + (f'<span class="kicker">{escape(SERIES[q["serie"]][0])}</span>' if serie else '') +
        f'<span class="tt">{escape(q["titulo"])}</span>'
        f'<span class="ent">{escape(entradilla(q["resumen"]))}</span>'
        f'<span class="leer">Leer la pieza →{"" if q["revisado"] else " · revisión pendiente"}</span></a></li>' for q in lista) + '</ul>'


def portada():
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': NOMBRE, 'url': ATLAS_URL, 'inLanguage': 'es', 'author': AUTOR,
          'description': 'Piezas sobre lugares que votan distinto de lo que cabría esperar: excepciones, fronteras, gemelos y escaños decididos por pocos votos.',
          'hasPart': [{'@type': 'NewsArticle', 'headline': q['titulo'], 'url': url(f'{q["serie"]}/{q["slug"]}/index.html')} for q in TODAS if q['revisado']]}
    h = [cabeza(NOMBRE, ld['description'], 'index.html', ld, nivel=0)]
    h.append(f'<p class="kicker">Periodismo de datos electorales</p><h1>{NOMBRE}</h1>')
    h.append('<p class="resumen">Los resultados generales esconden lugares que votan distinto de lo que cabría esperar por sus vecinos, por los municipios que más se les parecen o por su propia historia. Cada pieza parte de una de esas comparaciones, enseña los datos y separa lo que se sabe de lo que todavía es hipótesis.</p>')
    h.append(f'<p>Los resultados de todos los municipios se consultan en el <a href="../{GENERALES}index.html">mapa de resultados de España</a>. El Atlas no tiene fichas municipales: solo piezas con una pregunta y una respuesta.</p>')
    h.append('<h2>Las piezas</h2>' + tarjetas(TODAS, serie=True))
    h.append('<h2>Las series</h2><ul class="series">' + ''.join(
        f'<li><a href="{s}/index.html">{escape(nombre)}</a>: {escape(desc)}</li>'
        for s, (nombre, desc) in SERIES.items() if any(q['serie'] == s for q in TODAS)) + '</ul>')
    h.append('<h2>Cómo trabajamos</h2><p>Cada afirmación se marca como <strong>dato</strong> (verificable y reproducible), <strong>patrón</strong> (relación descriptiva, sin causa) o <strong>hipótesis</strong> (explicación posible que aún no tiene dos fuentes independientes). Ninguna pieza se publica sin revisión humana. <a href="metodologia/index.html">Metodología</a> · <a href="correcciones/index.html">Correcciones</a></p>')
    h.append(PIE)
    return 'index.html', ''.join(h)


def pagina_serie(s):
    nombre, desc = SERIES[s]
    ps = [q for q in TODAS if q['serie'] == s]
    ld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': nombre, 'description': desc, 'url': url(s + '/index.html'),
          'isPartOf': {'@type': 'CollectionPage', 'name': NOMBRE, 'url': ATLAS_URL},
          'hasPart': [{'@type': 'NewsArticle', 'headline': q['titulo'], 'url': url(f'{s}/{q["slug"]}/index.html')} for q in ps if q['revisado']]}
    h = [cabeza(f'{nombre} · {NOMBRE}', desc, s + '/index.html', ld, indexar=any(q['revisado'] for q in ps), nivel=1)]
    h.append(f'<p class="kicker">Serie</p><h1>{escape(nombre)}</h1><p class="resumen">{escape(desc)}</p>')
    h.append(tarjetas(ps, '../'))
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
    l += [f'- [{q["titulo"]}]({url(q["serie"] + "/" + q["slug"] + "/")}): {q["resumen"]}' for q in TODAS if q['revisado']]
    l += ['', '## Referencia', '', f'- [Metodología]({url("metodologia/")})', f'- [Datos en CSV]({url("datos/")})', f'- [Correcciones]({url("correcciones/")})', '']
    return '\n'.join(l)


def main():
    global TODAS
    C = json.loads((ATLAS / 'src' / 'cifras.json').read_text())
    TODAS = piezas(C)
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
    print(len(paginas), 'páginas;', sum(1 for q in TODAS if q['revisado']), 'de', len(TODAS), 'piezas revisadas')


TODAS = []
if __name__ == '__main__':
    main()
