"""Datos estructurados comunes a todo el sitio: autor (Person), editor (NewsMediaOrganization),
conjunto de datos principal (Dataset) y migas de pan (BreadcrumbList).

Los generadores de cada sección (src/seo.py, atlas/src/paginas.py, actualidad/src/construir.py,
generales-2026/src/pagina.py, src/territorios.py) escriben su propio JSON-LD. Este script pasa
después por todas las páginas publicadas y:

- sustituye cada `Person` con el nombre del autor por el mismo objeto completo (con `@id`, cargo,
  universidad y perfiles), para que Google vea una sola persona detrás de todas las piezas;
- da `@id` al Dataset de la portada y lo enlaza desde las piezas de Actualidad (`isBasedOn`);
- marca las piezas como `AnalysisNewsArticle` (subtipo de NewsArticle para análisis e interpretación de datos)
  en vez de `NewsArticle`, también en las páginas que aún no se han regenerado con el tipo nuevo;
- añade a cada página un bloque `BreadcrumbList` (Inicio › Sección › Pieza), sacado de la ruta
  y del <h1> de cada nivel.

Es idempotente: se puede ejecutar tantas veces como haga falta. Se ejecuta al final de cualquier
regeneración (src/seo.py lo llama al terminar; también se puede lanzar solo):

    python3 src/esquema.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://mapaelectoral.es/'
FIRMA = 'Nacho G. del Álamo'
PERFILES = [('Universitat de Girona', 'https://www.udg.edu/ca/directori/pagina-personal?ID=240543&language=es-ES'),
            ('LinkedIn', 'https://www.linkedin.com/in/ignacio-garc%C3%ADa-del-%C3%A1lamo-a289418/'),
            ('X', 'https://x.com/nachotronic'), ('GitHub', 'https://github.com/nachotronic')]
AUTOR = {'@type': 'Person', '@id': BASE + 'sobre-mi.html#person', 'name': FIRMA, 'url': BASE + 'sobre-mi.html',
         'jobTitle': 'Periodista de datos',
         'affiliation': {'@type': 'CollegeOrUniversity', 'name': 'Universitat de Girona', 'url': 'https://www.udg.edu/'},
         'knowsAbout': ['Periodismo de datos', 'Elecciones en España', 'Geografía electoral', 'Visualización de datos'],
         'sameAs': [u for _, u in PERFILES]}
# Editor de todo el sitio. Los generadores tienen su copia; este script deja el fundador igual en todas.
MEDIO = {'@type': 'NewsMediaOrganization', '@id': BASE + '#medio', 'name': 'Mapa Electoral', 'url': BASE,
         'founder': AUTOR,
         'publishingPrinciples': BASE + 'atlas/politica-editorial/', 'verificationFactCheckingPolicy': BASE + 'atlas/politica-editorial/#verificacion',
         'correctionsPolicy': BASE + 'atlas/correcciones/', 'sameAs': ['https://x.com/nachotronic']}
# Conjunto de datos del mapa de resultados: está descrito en la portada y en su metodología
DATASET_ID = BASE + 'generales-2026/metodologia.html#datos'
# Referencia completa a ese Dataset: Google exige name y description (50 caracteres o más) en cada
# Dataset que encuentra, también cuando solo se cita desde otra página (isBasedOn)
DATASET_REF = {'@type': 'Dataset', '@id': DATASET_ID,
               'name': 'Elecciones generales 2004-2023 por sección censal con renta, edad y población extranjera',
               'description': 'Votos al Congreso, municipales y europeas por familia política, participación y censo por sección censal '
                              '(desde 1977 por municipio), con renta, pobreza, edad y población extranjera del INE. Datos del Ministerio del Interior y del INE.',
               'url': BASE + 'generales-2026/metodologia.html'}

# Nombre corto de cada página en las migas (si no está aquí, se usa su <h1>)
NOMBRES = {
    '': 'Inicio',
    'abstencion.html': '¿Quién no vota en Cataluña?',
    'ca.html': 'Qui no vota a Catalunya?',
    'mapa.html': 'Mapa interactivo',
    'mapa-ca.html': 'Mapa interactiu',
    'metodologia.html': 'Metodología',
    'metodologia-ca.html': 'Metodologia',
    'sobre-mi.html': 'Sobre mí',
    'sobre-mi-ca.html': 'Sobre mi',
    'atlas/': 'Atlas de las anomalías electorales',
    'actualidad/': 'Actualidad',
    'generales-2026/metodologia.html': 'Metodología del mapa',
    'encuestas/': 'Encuestas',
    'listas-electorales-29n/': 'Listas electorales del 29N',
}
# Página de la que cuelga cada página suelta (las de carpeta cuelgan de la carpeta superior)
PADRE = {
    'ca.html': '', 'mapa.html': 'abstencion.html', 'mapa-ca.html': 'ca.html', 'metodologia.html': 'abstencion.html', 'metodologia-ca.html': 'ca.html',
    'generales-2026/metodologia.html': '',
}
INICIO_CA = {'ca.html', 'mapa-ca.html', 'metodologia-ca.html', 'sobre-mi-ca.html'}
NO_TOCAR = ('insertar/', 'generales-2026/index.html', '29n/', 'generales/')


def h1(ruta):
    """Texto del <h1> de una página publicada (ruta relativa al sitio, como en la URL)."""
    f = ROOT / (ruta + 'index.html' if ruta.endswith('/') or ruta == '' else ruta)
    if not f.exists():
        return None
    t = f.read_text(encoding='utf-8')
    corto = re.search(r'<h1[^>]*data-miga="([^"]+)"', t)   # nombre corto para las migas, si la página lo da
    if corto:
        return html.unescape(corto.group(1))
    m = re.search(r'<h1[^>]*>(.*?)</h1>', t, re.S)
    return ' '.join(html.unescape(re.sub(r'<[^>]+>', '', m.group(1))).split()) if m else None


def nombre(ruta):
    return NOMBRES.get(ruta) or h1(ruta) or ruta


def cadena(ruta):
    """Rutas desde la portada hasta la página: ['', 'atlas/', 'atlas/excepciones/', 'atlas/excepciones/x/']."""
    if ruta == '':
        return ['']
    if ruta in PADRE:
        return cadena(PADRE[ruta]) + [ruta]
    partes = ruta.rstrip('/').split('/')
    if len(partes) == 1:
        return ['', ruta]
    return cadena('/'.join(partes[:-1]) + '/') + [ruta]


def migas(ruta):
    pasos = cadena(ruta)
    if len(pasos) < 2:
        return None
    items = []
    for i, r in enumerate(pasos):
        n = 'Inici' if r == '' and ruta in INICIO_CA else nombre(r)
        items.append({'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': BASE + r})
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': items}


def es_autor(o):
    return isinstance(o, dict) and o.get('@type') == 'Person' and o.get('name') == FIRMA


def normaliza(o, ruta):
    """Recorre el JSON-LD: autor completo, @id del Dataset de la portada y enlace de Actualidad al Dataset."""
    if isinstance(o, list):
        return [normaliza(x, ruta) for x in o]
    if not isinstance(o, dict):
        return o
    if es_autor(o):
        extra = {k: v for k, v in o.items() if k in ('jobTitle', 'description')}   # la página «Sobre mí» los da en su idioma
        return {**AUTOR, **extra}
    o = {k: normaliza(v, ruta) for k, v in o.items()}
    if o.get('@type') == 'NewsArticle':
        o['@type'] = 'AnalysisNewsArticle'
    if o.get('@type') == 'Dataset' and ruta in ('', 'generales-2026/metodologia.html') and 'generales-2026/descargas/' in json.dumps(o):
        o = {'@id': DATASET_ID, **{k: v for k, v in o.items() if k != '@id'}}
    if o.get('@type') == 'AnalysisNewsArticle' and ruta.startswith('actualidad/') and ruta != 'actualidad/' and 'isBasedOn' not in o:
        o['isBasedOn'] = dict(DATASET_REF)
    if isinstance(o.get('isBasedOn'), dict) and o['isBasedOn'].get('@id') == DATASET_ID:
        o['isBasedOn'] = dict(DATASET_REF)   # las citas incompletas de páginas anteriores también
    return o


LD = re.compile(r'(<script type="application/ld\+json"(?: id="[^"]*")?>)(.*?)(</script>)', re.S)


def serializa(obj, original):
    if '\n ' in original:
        s = json.dumps(obj, ensure_ascii=False, indent=1)
        return ('\n' if original.startswith('\n') else '') + s.replace('</', '<\\/') + ('\n' if original.endswith('\n') else '')
    return json.dumps(obj, ensure_ascii=False).replace('</', '<\\/')


def procesa(f):
    ruta = f.relative_to(ROOT).as_posix()
    ruta = ruta[:-len('index.html')] if ruta.endswith('index.html') else ruta
    if any(ruta.startswith(x) for x in NO_TOCAR) or '/src/' in '/' + ruta:
        return False
    s0 = s = f.read_text(encoding='utf-8')
    if 'http-equiv="refresh"' in s or 'noindex' in s[:s.find('</head>')]:
        return False
    s = re.sub(r'\n?<script type="application/ld\+json" id="migas">.*?</script>', '', s, flags=re.S)

    def cambia(m):
        try:
            obj = json.loads(m.group(2).replace('<\\/', '</'))
        except json.JSONDecodeError:
            return m.group(0)
        return m.group(1) + serializa(normaliza(obj, ruta), m.group(2)) + m.group(3)
    s = LD.sub(cambia, s)
    if ruta == 'generales-2026/metodologia.html' and '"Dataset"' not in s:
        # el Dataset del mapa se describe en la portada; su página propia es la metodología
        m = re.search(r'<script type="application/ld\+json">(\{[^<]*?"@type": "Dataset".*?)</script>', (ROOT / 'index.html').read_text(encoding='utf-8'), re.S)
        if m:
            s = s.replace('</head>', m.group(0) + '\n</head>', 1)
    b = migas(ruta)
    if b:
        s = s.replace('</head>', '<script type="application/ld+json" id="migas">' + json.dumps(b, ensure_ascii=False) + '</script>\n</head>', 1)
    if s != s0:
        f.write_text(s, encoding='utf-8')
        return True
    return False


def paginas():
    yield from sorted(ROOT.glob('*.html'))
    for d in ('atlas', 'actualidad', 'elecciones', 'municipio', 'temas', 'generales-2026', 'encuestas', 'listas-electorales-29n'):
        yield from sorted((ROOT / d).rglob('*.html'))


def main():
    n = sum(procesa(f) for f in paginas())
    print(f'esquema: {n} páginas actualizadas (autor, Dataset y migas de pan)')


if __name__ == '__main__':
    main()
