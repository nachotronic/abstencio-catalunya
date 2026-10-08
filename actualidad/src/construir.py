"""Genera las piezas de la sección Actualidad (/actualidad/).

Cada pieza parte de un HTML de trabajo en esta carpeta (<slug>.html: estilos de los gráficos,
<main> con el texto y <script> con los datos de los gráficos). Este script le pone la cabecera
del sitio (SEO, Open Graph, JSON-LD, analítica), la navegación, el bloque «Método y fuentes»
del estándar de verificación y el pie, y escribe además el índice y el sitemap de la sección.

Uso, desde la raíz del repositorio: python3 actualidad/src/construir.py
"""
import datetime, html, json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(RAIZ, 'actualidad', 'src')
BASE = 'https://mapaelectoral.es'
# Editor de todo el sitio: el mismo objeto que atlas/src/paginas.py y src/seo.py
MEDIO = {'@type': 'NewsMediaOrganization', '@id': BASE + '/#medio', 'name': 'Mapa Electoral', 'url': BASE + '/',
         'founder': {'@type': 'Person', 'name': 'Nacho G. del Álamo', 'url': BASE + '/sobre-mi.html'},
         'publishingPrinciples': BASE + '/atlas/politica-editorial/', 'verificationFactCheckingPolicy': BASE + '/atlas/politica-editorial/#verificacion',
         'correctionsPolicy': BASE + '/atlas/correcciones/', 'sameAs': ['https://x.com/nachotronic']}
POLITICA = ' · <a href="https://mapaelectoral.es/atlas/politica-editorial/">Política editorial</a>'
AUTOR = 'Nacho G. del Álamo'
CF = ("<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
      "data-cf-beacon='{\"token\": \"cf0453d1d8f247d4a5dd55aff7b685ae\"}'></script><!-- End Cloudflare Web Analytics -->")
INTERIOR = ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/',
            'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)')
INE = ('https://www.ine.es/experimental/atlas/experimental_atlas.htm',
       'INE, Atlas de Distribución de Renta de los Hogares (renta y edad por sección), vía ineAtlas.data')
INE_CENSO = ('https://www.ine.es/censos2021/C2021_Indicadores.csv',
             'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (régimen de tenencia de las viviendas principales)')
EL_ESPANOL = 'https://www.elespanol.com/sociedad/20261007/muere-maricarmen-directo-fallece-anos-dias-despues-desahuciada-madrid/1003744412550_10.html'
EURONEWS = 'https://es.euronews.com/video/2026/09/23/el-desahucio-de-maricarmen-se-consuma-tras-70-anos-en-su-casa-de-retiro'
EXCELSIOR = 'https://www.excelsior.com.mx/internacional/miles-marchan-madrid-contra-desahucio-mujer-87-anos'

PIEZAS = [
    dict(
        slug='beiras-nacionalismo-gallego', fecha='2026-10-08',
        titulo='El mapa que deja Beiras: el nacionalismo gallego en las generales',
        descripcion='El BNG pasó del 12,0 % en Galicia en 2004 al 2,9 % en 2016, cuando En Marea sacó el 22,4 %, y en 2023 volvió al 9,5 %. Mapas por municipio y sección.',
        compara='La lista nacionalista (BNG; NÓS en 2015) y la gran lista a su izquierda en cada elección general en Galicia, de 2004 a 2023, candidatura a candidatura. Voto por municipio y por sección, cruzado con edad, estudios y renta.',
        limites='Solo elecciones generales: no incluye las autonómicas, donde el BNG obtiene sus mejores resultados. Las listas a la izquierda del BNG cambian de socios en cada elección. Los quintiles mezclan edad, estudios y tamaño de municipio, que van juntos en Galicia. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/galicia/muere-90-anos-xose-manuel-beiras-intelectual-dirigente-nacionalismo-gallego-importante-castelao_1_13565454.html', 'elDiario.es, obituario de Xosé Manuel Beiras (Daniel Salgado, 8-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Xos%C3%A9_Manuel_Beiras', 'Wikipedia, «Xosé Manuel Beiras» (consultada el 8-10-2026)')],
        enlaces=[('El País', 'https://elpais.com/espana/2026-10-08/muere-a-los-90-anos-xose-manuel-beiras-historico-dirigente-del-nacionalismo-gallego.html')],
        lugar='Galicia',
    ),
    dict(
        slug='colau-barcelona-comuns', fecha='2026-10-08',
        titulo='La Barcelona que espera a Colau: de 837 secciones a 23',
        descripcion='En Comú Podem ganó en 837 de las 1.068 secciones de Barcelona en 2015 (26,7 %). En 2023, Sumar-En Comú Podem ganó en 23 (17,0 %). La caída fue mayor en los barrios de renta baja.',
        compara='La candidatura de la que formaban parte los comuns en cada elección en la ciudad de Barcelona (generales 2011-2023 y municipales 2011-2023), por distrito y por sección censal, y su relación con la renta de la sección.',
        limites='Las candidaturas cambian de nombre y de socios; se cuenta solo la lista de los comuns, sin sumar otras (Front Republicà en abril de 2019, Más País en noviembre de 2019). Las secciones se comparan con los límites de 2023. Los quintiles de renta son medias simples de secciones. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/politica/monica-garcia-renuncia-candidata-frente-amplio-favor-ada-colau-pide-liderar-lista-madrid_1_13569737.html', 'elDiario.es, «Mónica García renuncia a ser candidata del Frente Amplio…» (7-10-2026)'),
                 ('https://civio.es/el-boe-nuestro-de-cada-dia/2026/10/06/llega-al-boe-la-convocatoria-de-elecciones-para-el-29-de-noviembre-todas-las-fechas-y-pasos-hasta-ese-dia/', 'Civio, calendario y escaños del decreto de convocatoria (6-10-2026)')],
        enlaces=[],
        lugar='Barcelona',
    ),
    dict(
        slug='votar-en-noviembre', fecha='2026-10-08',
        titulo='Votar en noviembre: el 10N de 2019 tuvo la participación más baja de la democracia',
        descripcion='El 10N de 2019 dejó un 66,2 % de participación, el mínimo desde 1977; el máximo, 80,0 %, también fue en otoño, en octubre de 1982. Entre abril y noviembre de 2019 la participación cayó en el 98 % de las secciones.',
        compara='La participación oficial en las 16 elecciones generales desde 1977 y, por sección censal, la de abril y noviembre de 2019, por provincia y por decil de renta.',
        limites='Con solo dos elecciones en noviembre no se puede aislar el efecto del mes. La participación oficial de 2011 a 2019 está rebajada por el voto rogado de los residentes en el extranjero; los datos por sección no incluyen voto exterior. Los deciles son medias simples de secciones con la renta de un solo año.',
        fuentes=[('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a', 'Junta Electoral Central, participación oficial 1977-2023 (tabla recopilada en Wikipedia, consultada el 8-10-2026)'),
                 INTERIOR, INE,
                 ('https://civio.es/el-boe-nuestro-de-cada-dia/2026/10/06/llega-al-boe-la-convocatoria-de-elecciones-para-el-29-de-noviembre-todas-las-fechas-y-pasos-hasta-ese-dia/', 'Civio, calendario electoral del 29N (6-10-2026)'),
                 ('https://www.canarias7.es/elecciones/generales/convocatoria-elecciones-generales-obliga-cancelar-eventos-programados-20261007131300-nt.html', 'Canarias7, eventos cancelados por el 29N (7-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='maricarmen-alquiler-y-voto', fecha='2026-10-08',
        titulo='Después de Maricarmen: en los barrios donde más se alquila se vota diez puntos menos',
        descripcion='En el 10 % de secciones con más hogares de alquiler votó el 64,6 % en 2023; en el 10 % con menos, el 74,1 %. Entre los barrios más pobres, la distancia llega a 16 puntos.',
        compara='El porcentaje de hogares de alquiler de cada sección censal (censo de 2021) y su participación y voto en las generales de julio de 2023, en toda España y dentro de cada quintil de renta; la ciudad de Madrid por distritos; la distancia en las generales desde 2004.',
        limites='Son datos agregados por sección: que un barrio con mucho alquiler vote menos no prueba que los inquilinos voten menos que sus vecinos propietarios. El alquiler es el del censo de 2021, también para elecciones anteriores. La regresión describe una asociación, no una causa. Las explicaciones (movilidad, empadronamiento) son hipótesis. Sin voto exterior.',
        fuentes=[INE_CENSO, INTERIOR, INE,
                 (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)'),
                 (EURONEWS, 'Euronews, «El desahucio de Maricarmen se consuma tras 70 años en su casa de Retiro» (23-9-2026)'),
                 (EXCELSIOR, 'Excélsior, «Miles marchan en Madrid contra desahucio de mujer de 87 años» (26-9-2026)'),
                 ('https://doi.org/10.2307/1960778', 'Squire, Wolfinger y Glass, «Residential Mobility and Voter Turnout», American Political Science Review, 1987')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='alquiler-ciudad-a-ciudad', fecha='2026-10-08',
        titulo='Tu ciudad, barrio a barrio: en las 25 más grandes, donde más se alquila se vota menos',
        descripcion='En las 25 ciudades con más electores, el 20 % de secciones con más alquiler votó menos en 2023 que el 20 % con menos. En Alicante, 15 puntos menos; en Vigo, 1,9.',
        compara='En cada una de las 25 ciudades con más electores, la participación en las generales de julio de 2023 del 20 % de secciones con menos hogares de alquiler y del 20 % con más (censo de 2021), y la renta de cada grupo.',
        limites='Son datos agregados por sección, no de personas. El alquiler es el del censo de 2021. En muchas ciudades los barrios de alquiler son también más pobres, y parte de la diferencia puede deberse a la renta. Los quintiles de las ciudades menores tienen unas 30 secciones. Sin voto exterior.',
        fuentes=[INE_CENSO, INTERIOR, INE, (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='25 ciudades',
    ),
    dict(
        slug='pisos-turisticos-y-votantes', fecha='2026-10-08',
        titulo='Los barrios de pisos turísticos se quedan sin votantes',
        descripcion='En las 25 mayores ciudades, las secciones con un 5 % o más de pisos turísticos perdieron el 2,9 % de sus electores entre 2015 y 2023, frente al 1,0 % de las que apenas tienen. En Barcelona, el 10,6 %.',
        compara='El peso de los pisos turísticos en cada sección censal (INE, agosto de 2023) y la variación de su censo electoral entre las generales de 2015 y 2023 en las 25 mayores ciudades; en toda España, la participación de 2004 y 2023 según ese peso.',
        limites='La estadística de viviendas turísticas del INE es experimental y cuenta anuncios en plataformas. El censo electoral solo incluye a españoles y cambia también por envejecimiento, defunciones y mudanzas: los datos muestran que ambas cosas van juntas, no que una cause la otra. Se usa el peso de agosto de 2023 para toda la serie. Sin voto exterior.',
        fuentes=[('https://www.ine.es/experimental/viv_turistica/exp_viv_turistica_tablas.htm', 'INE, Medición del número de viviendas turísticas en España y su capacidad (estadística experimental), tabla por secciones censales, agosto de 2023'),
                 INTERIOR, (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='Grandes ciudades',
    ),
]

# Enlaces a las fuentes dentro del texto: (texto exacto, url)
ENLACES_TEXTO = {
    'beiras-nacionalismo-gallego': [
        ('según el obituario de elDiario.es', PIEZAS[0]['fuentes'][2][0]),
    ],
    'colau-barcelona-comuns': [
        ('Según elDiario.es, Más Madrid', PIEZAS[1]['fuentes'][2][0]),
        ('según el decreto de convocatoria publicado en el BOE', PIEZAS[1]['fuentes'][3][0]),
    ],
    'votar-en-noviembre': [
        ('según el calendario que ha desgranado Civio', PIEZAS[2]['fuentes'][3][0]),
        ('la convocatoria ya está obligando a cancelar eventos', PIEZAS[2]['fuentes'][4][0]),
    ],
    'maricarmen-alquiler-y-voto': [
        ('según ha contado El Español', EL_ESPANOL),
        ('al cuarto intento', EURONEWS),
        ('miles de personas marcharon por Madrid', EXCELSIOR),
        ('El Gobierno defiende que sus dos decretos', EL_ESPANOL),
    ],
    'alquiler-ciudad-a-ciudad': [
        ('La muerte de Maricarmen Abascal', EL_ESPANOL),
    ],
    'pisos-turisticos-y-votantes': [
        ('El desahucio y la muerte de Maricarmen Abascal', EL_ESPANOL),
    ],
}

FUENTES_WEB = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
               '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700'
               '&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')
CSS_SITIO = """<style>
:root{--serif:"Newsreader",Georgia,serif;--ui:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;--surface:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--surface:#1e2025}}
:root[data-theme="dark"]{--surface:#1e2025}
body{margin:0}
h1,h2{font-family:var(--ui);letter-spacing:-.01em}
h1{font-weight:700}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0}
.kicker a{color:var(--muted);text-decoration:none}
.firma{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);padding-top:.6rem}
.firma a{color:var(--muted)}
.ficha{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:6px 16px 12px;font-size:.98rem;margin:0}
.ficha dt{font-family:var(--mono);font-size:.76rem;color:var(--muted);margin-top:10px}
.ficha dd{margin:2px 0 0}
.ficha ul{margin:.2rem 0 0;padding-left:1.1rem}
nav.site{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;max-width:46rem;margin:0 auto;padding:12px 16px 10px;border-bottom:1px solid var(--rule);font:500 14px/1.4 var(--ui)}
nav.site a{color:var(--muted);text-decoration:none}nav.site a:hover{color:var(--fg)}nav.site a[aria-current]{color:var(--fg);font-weight:700}
nav.site a.marca{color:var(--fg);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:13px;margin-right:6px}
@media (max-width:760px){nav.site{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none}nav.site::-webkit-scrollbar{display:none}}
.sigue{list-style:none;padding:0;display:grid;gap:12px}
.sigue a{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:12px 16px;text-decoration:none;color:var(--fg);font-family:var(--ui)}
.sigue .kicker{display:block;margin-bottom:2px}
footer{margin-top:3rem;font-family:var(--mono);font-size:.76rem;color:var(--muted)}
</style>"""


def fecha_larga(f):
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    a, m, d = f.split('-')
    return f'{int(d)} de {meses[int(m) - 1]} de {a}'


def nav(prefijo, actual):
    items = [('', 'Mapa de resultados'), ('atlas/index.html', 'Atlas'), ('actualidad/index.html', 'Actualidad'),
             ('abstencion.html', 'Cataluña'), ('sobre-mi.html', 'Sobre mí')]
    out = f'<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="{prefijo}">Mapa Electoral</a>'
    for href, txt in items:
        cur = ' aria-current="page"' if txt == actual else ''
        out += f'<a href="{prefijo}{href}"{cur}>{txt}</a>'
    return out + '</nav>'


def cabecera(titulo, descripcion, url, imagen, jsonld, robots='index, follow, max-image-preview:large'):
    e = html.escape
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} · Mapa Electoral</title>
<meta name="description" content="{e(descripcion)}">
<meta name="author" content="{AUTOR}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Mapa Electoral">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@nachotronic">
<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=1)}
</script>
{CF}
{FUENTES_WEB}
"""


def pieza(p, todas):
    src = open(os.path.join(SRC, p['slug'] + '.html'), encoding='utf-8').read()
    estilos = ''.join(re.findall(r'<style>.*?</style>', src, re.S))
    main = re.search(r'<main>.*?</main>', src, re.S).group(0)
    script = re.search(r'<script>.*?</script>', src, re.S).group(0)
    h1 = re.search(r'<h1>(.*?)</h1>', main, re.S).group(1)
    url = f"{BASE}/actualidad/{p['slug']}/"
    imagen = f"{BASE}/img/compartir/actualidad-{p['slug']}.jpg"
    f = fecha_larga(p['fecha'])

    main = re.sub(r'<span class="draft">.*?</span>\n?', f'<p class="kicker"><a href="../index.html">Actualidad</a> · {p["lugar"]}</p>\n', main)
    main = re.sub(r'<div class="byline">.*?</div>',
                  f'<p class="firma">Por <a href="../../sobre-mi.html">{AUTOR}</a> · <time datetime="{p["fecha"]}">{f}</time></p>', main)
    for texto, href in ENLACES_TEXTO.get(p['slug'], []):
        assert texto in main, (p['slug'], texto)
        main = main.replace(texto, f'<a href="{href}">{texto}</a>', 1)
    fuentes = ''.join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u, t in p['fuentes'])
    otras = [q for q in todas if q is not p]
    sigue = ''.join(f'<li><a href="../{q["slug"]}/index.html"><span class="kicker">Actualidad · {q["lugar"]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in otras)
    ficha = f"""<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se compara</dt><dd>{p['compara']}</dd>
<dt>Límites</dt><dd>{p['limites']}</dd>
<dt>Cómo se calcula</dt><dd>Porcentajes sobre votos a candidaturas, salvo la participación, que es sobre el censo. Cifras reproducibles con los scripts del expediente de la pieza. <a href="../../atlas/metodologia/index.html">Metodología del Atlas</a></dd>
<dt>Fuentes</dt><dd><ul>{fuentes}</ul></dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
<dt>Revisión de datos y texto</dt><dd>{AUTOR}, {f}</dd>
<dt>Publicado · actualizado</dt><dd>{f} · {f}</dd>
<dt>Correcciones</dt><dd>Ninguna.</dd>
</dl>
<h2>Sigue leyendo</h2><ul class="sigue">{sigue}<li><a href="../../atlas/index.html"><span class="kicker">Atlas</span><b>Atlas de las anomalías electorales</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>{POLITICA}</footer>"""
    main = re.sub(r'<div class="foot">.*?</div>', ficha, main, flags=re.S)

    jsonld = {'@context': 'https://schema.org', '@type': 'NewsArticle', '@id': url + '#articulo',
              'headline': p['titulo'], 'alternativeHeadline': re.sub('<[^>]+>', '', h1), 'description': p['descripcion'],
              'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': p['fecha'], 'dateModified': p['fecha'],
              'image': [imagen],
              'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html', 'sameAs': ['https://x.com/nachotronic', 'https://github.com/nachotronic']},
              'publisher': MEDIO,
              'isPartOf': {'@type': 'CollectionPage', 'name': 'Actualidad', 'url': BASE + '/actualidad/'},
              'isAccessibleForFree': True, 'license': 'https://creativecommons.org/licenses/by/4.0/'}
    out = (cabecera(p['titulo'], p['descripcion'], url, imagen, jsonld) + estilos + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../../', 'Actualidad') + '\n' + main + '\n' + script + '\n</body>\n</html>\n')
    d = os.path.join(RAIZ, 'actualidad', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


def indice(todas):
    url = BASE + '/actualidad/'
    desc = 'Piezas cortas que cruzan la actualidad del día con los datos electorales por sección censal. Cada cifra, con su fuente.'
    jsonld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Actualidad', 'url': url, 'description': desc,
              'hasPart': [{'@type': 'NewsArticle', 'headline': p['titulo'], 'url': f"{url}{p['slug']}/", 'datePublished': p['fecha']} for p in todas]}
    items = ''.join(f'<li><a href="{p["slug"]}/index.html"><span class="kicker">{fecha_larga(p["fecha"])} · {p["lugar"]}</span><b>{html.escape(p["titulo"])}</b><span class="d">{html.escape(p["descripcion"])}</span></a></li>'
                    for p in sorted(todas, key=lambda p: p['fecha'], reverse=True))
    css = """<style>
:root{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.6}
main{max-width:46rem;margin:0 auto;padding-block:2rem 4rem;padding-inline:16px}
h1{font-size:clamp(1.8rem,5vw,2.4rem);margin:.6rem 0}
.sigue .d{display:block;color:var(--muted);font-family:var(--serif);font-size:1rem;margin-top:4px}
.sigue b{display:block;font-size:1.1rem;line-height:1.3}
a{color:var(--fg)}
</style>"""
    out = (cabecera('Actualidad', desc, url, BASE + '/img/compartir/atlas.jpg', jsonld) + css + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../', 'Actualidad')
           + f'\n<main><p class="kicker">Mapa Electoral</p><h1>Actualidad</h1><p>{desc} Para las piezas de fondo, el <a href="../atlas/index.html">Atlas de las anomalías electorales</a>.</p>'
           + f'<ul class="sigue">{items}</ul><footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>'
           + POLITICA + '</footer></main>\n</body>\n</html>\n')
    open(os.path.join(RAIZ, 'actualidad', 'index.html'), 'w', encoding='utf-8').write(out)
    urls = [f'  <url><loc>{url}</loc><lastmod>{max(p["fecha"] for p in todas)}</lastmod></url>']
    urls += [f'  <url><loc>{url}{p["slug"]}/</loc><lastmod>{p["fecha"]}</lastmod></url>' for p in todas]
    open(os.path.join(RAIZ, 'actualidad', 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    # Google News: solo piezas de los dos últimos días (norma de Google), como atlas/sitemap-noticias.xml
    lim = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    noticias = ''.join(f'  <url>\n    <loc>{url}{p["slug"]}/</loc>\n    <news:news>\n      <news:publication><news:name>Mapa Electoral</news:name><news:language>es</news:language></news:publication>\n'
                       f'      <news:publication_date>{p["fecha"]}</news:publication_date>\n      <news:title>{html.escape(p["titulo"])}</news:title>\n    </news:news>\n  </url>\n'
                       for p in todas if p['fecha'] >= lim)
    open(os.path.join(RAIZ, 'actualidad', 'sitemap-noticias.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + noticias + '</urlset>\n')


if __name__ == '__main__':
    for p in PIEZAS:
        pieza(p, PIEZAS)
    indice(PIEZAS)
    print('Actualidad:', len(PIEZAS), 'piezas')
