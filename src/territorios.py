"""Páginas de entrada por territorio y por tema en /elecciones/.

- /elecciones/: índice de comunidades y provincias.
- /elecciones/<comunidad>/ y /elecciones/<comunidad>/<provincia>/: resultado del 23J, serie de las 16 generales
  desde 1977, voto por renta de sus secciones censales, municipios principales y enlaces a las piezas del sitio
  sobre ese territorio. Las comunidades de una sola provincia no tienen página de provincia.
- /elecciones/mapa-electoral-seccion-censal/ y /elecciones/voto-y-renta-por-barrios/: páginas temáticas.

No hay fichas por municipio: el municipio se consulta en el mapa de la portada (?m=<código INE>).
Ninguna cifra se escribe a mano: salen de las descargas públicas del mapa (src/territorios_datos.py).
Cada frase con cifras va marcada como dato o patrón, como en el resto del sitio.

Uso (después de regenerar el mapa y el Atlas):  python3 src/territorios.py && python3 src/seo.py
"""
import datetime, json, pathlib, re, sys
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'atlas' / 'src'))
import territorios_datos as T  # noqa: E402
import esquema  # noqa: E402
import paginas as atlas  # noqa: E402  (estilos, piezas y titulares del Atlas)
from piezas import piezas  # noqa: E402
from piezas2 import piezas2  # noqa: E402
from piezas3 import piezas3  # noqa: E402

BASE = esquema.BASE
OUT = ROOT / 'elecciones'
PUBLICADO = '2026-10-13'
ACTUALIZADO = '2026-10-13'   # cámbiala a mano cuando cambien los datos o el texto
SITIO = 'Mapa Electoral'
LICENCIA = 'https://creativecommons.org/licenses/by/4.0/'

from territorios_rutas import PROV_SLUG, CCAA, PROV_CCAA, PROV_NOMBRE, ruta_provincia, ACTUALIDAD_LUGAR, TEMA_RENTA, TEMA_SECCION  # noqa: E402

# ---------- formato ----------
def pct(x, d=1):
    return '—' if x is None else f'{x * 100:.{d}f}'.replace('.', ',') + ' %'


def num(x):
    return f'{int(round(x)):,}'.replace(',', '.')


def euros(x):
    return num(x) + ' €'


def h1_de(ruta):
    f = ROOT / ruta / 'index.html'
    if not f.exists():
        return None
    m = re.search(r'<h1[^>]*>(.*?)</h1>', f.read_text(encoding='utf-8'), re.S)
    return ' '.join(re.sub(r'<[^>]+>', '', m.group(1)).split()) if m else None


def tipo(t):
    return f'<span class="tipo {"t-patron" if t == "Patrón" else "t-dato"}">{t}</span>'


def p_(t, texto):
    return f'<p>{tipo(t)}{texto}</p>'


# ---------- piezas relacionadas ----------
def piezas_atlas():
    C = json.loads((ROOT / 'atlas' / 'src' / 'cifras.json').read_text())
    todas = [q for q in piezas(C) + piezas2(C) + piezas3(C) if q['revisado']]
    for q in todas:
        q['_provs'] = set(atlas.provincias(q))
    return todas


ATLAS = piezas_atlas()


def relacionadas(provs, nivel):
    """Piezas del Atlas y de Actualidad sobre alguna de esas provincias: (url relativa, titular, sección)."""
    raiz = '../' * nivel
    out = [(f'{raiz}atlas/{atlas.ruta_pieza(q).replace("index.html", "")}', atlas.titular(q), 'Atlas') for q in ATLAS if q['_provs'] & set(provs)]
    for slug, ps in ACTUALIDAD_LUGAR.items():
        if set(ps) & set(provs) and (t := h1_de(f'actualidad/{slug}')):
            out.append((f'{raiz}actualidad/{slug}/', t, 'Actualidad'))
    return out


# ---------- gráficos SVG (sin JavaScript), siempre con el color de cada partido ----------
def barras(r, ref=None):
    fams = [c for c in T.FAM if c != 'OTROS' and (r['pct'][c] or 0) >= 0.01]
    fams.sort(key=lambda c: -r['pct'][c])
    fams.append('OTROS')
    alto, w0, w = 30, 150, 560
    mx = max(r['pct'][c] or 0 for c in fams)
    filas = []
    for i, c in enumerate(fams):
        v = r['pct'][c] or 0
        y = i * alto
        ancho = (w - w0 - 70) * v / mx
        filas.append(f'<text x="{w0 - 8}" y="{y + 19}" text-anchor="end" class="et">{escape(T.NOMBRE[c])}</text>'
                     f'<rect x="{w0}" y="{y + 6}" width="{ancho:.1f}" height="18" rx="2" fill="{T.COLOR[c]}"/>'
                     f'<text x="{w0 + ancho + 6:.1f}" y="{y + 19}" class="va">{pct(v)}</text>')
        if ref is not None and ref['pct'][c] is not None:
            xr = w0 + (w - w0 - 70) * ref['pct'][c] / mx
            if xr <= w - 70:
                filas.append(f'<line x1="{xr:.1f}" x2="{xr:.1f}" y1="{y + 3}" y2="{y + 27}" class="ref"/>')
    h = len(fams) * alto + 4
    return (f'<svg class="graf" viewBox="0 0 {w} {h}" role="img" aria-label="Voto por partido en las generales de 2023">'
            f'<style>.et,.va{{font:13px var(--sans);fill:var(--fg)}}.va{{fill:var(--muted)}}.ref{{stroke:var(--fg);stroke-width:2;stroke-dasharray:3 2}}</style>'
            + ''.join(filas) + '</svg>')


def lineas(serie):
    """Voto de las familias que alguna vez pasan del 10 % en el territorio, en las 16 generales."""
    ys = T.GENERALES
    fams = [c for c in T.FAM if c != 'OTROS' and max((serie[y]['pct'][c] or 0) for y in ys) >= 0.10]
    w, h, x0, x1, y0, y1 = 640, 300, 36, 560, 14, 270
    mx = max(max((serie[y]['pct'][c] or 0) for y in ys) for c in fams)
    tope = min(1, (int(mx * 10) + 1) / 10)
    X = lambda i: x0 + (x1 - x0) * i / (len(ys) - 1)
    Y = lambda v: y1 - (y1 - y0) * v / tope
    g = []
    for k in range(0, int(round(tope * 100)) + 1, 10):
        g.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(k / 100):.1f}" y2="{Y(k / 100):.1f}" class="rej"/><text x="{x0 - 6}" y="{Y(k / 100) + 4:.1f}" text-anchor="end" class="ej">{k}</text>')
    for i, y in enumerate(ys):
        if i % 3 == 0 or i == len(ys) - 1:
            g.append(f'<text x="{X(i):.1f}" y="{y1 + 18}" text-anchor="middle" class="ej">{y[:4]}</text>')
    finales = []
    for c in fams:
        pts = [(X(i), Y(serie[y]['pct'][c])) for i, y in enumerate(ys) if serie[y]['pct'][c]]
        tramos, actual = [], []
        for i, y in enumerate(ys):   # sin línea donde la familia no se presentó
            v = serie[y]['pct'][c]
            if v:
                actual.append(f'{X(i):.1f},{Y(v):.1f}')
            elif actual:
                tramos.append(actual); actual = []
        if actual:
            tramos.append(actual)
        for t in tramos:
            g.append(f'<polyline points="{" ".join(t)}" fill="none" stroke="{T.COLOR[c]}" stroke-width="2.5" stroke-linejoin="round"/>')
        if pts:
            ult = serie[ys[-1]]['pct'][c]
            if ult:
                finales.append([Y(ult), c])
            else:   # partido desaparecido (UCD, CDS, Cs...): etiqueta donde acaba su línea
                xa, ya = pts[-1]
                g.append(f'<text x="{xa:.1f}" y="{ya - 6:.1f}" text-anchor="middle" class="lb" fill="{T.COLOR[c]}">{escape(T.NOMBRE[c].split(" /")[0])}</text>')
    finales.sort()
    for i in range(1, len(finales)):   # que no se monten las etiquetas
        finales[i][0] = max(finales[i][0], finales[i - 1][0] + 14)
    for yy, c in finales:
        g.append(f'<text x="{x1 + 6}" y="{yy + 4:.1f}" class="lb" fill="{T.COLOR[c]}">{escape(T.NOMBRE[c].split(" /")[0])}</text>')
    return (f'<svg class="graf" viewBox="0 0 {w} {h}" role="img" aria-label="Voto por partido en las generales de 1977 a 2023">'
            '<style>.ej{font:12px var(--sans);fill:var(--muted)}.rej{stroke:var(--rule)}.lb{font:600 12px var(--sans)}</style>'
            + ''.join(g) + '</svg>')


# ---------- bloques de texto y tablas ----------
def tabla(caption, cab, filas, num_desde=1):
    th = ''.join(f'<th scope="col"{" class=\"n\"" if i >= num_desde else ""}>{c}</th>' for i, c in enumerate(cab))
    tr = ''.join('<tr><th scope="row">' + f[0] + '</th>' + ''.join(f'<td class="n">{x}</td>' for x in f[1:]) + '</tr>' for f in filas)
    return f'<div class="tbl"><table><caption>{caption}</caption><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'


# Nombre propio de la familia en la comunidad, para el texto (las tablas usan el de la familia)
REGIONAL = {'cataluna': {'PSOE': 'PSC', 'JUNTS': 'Junts'}}


def entradilla(nombre, en, r, serie, ccaa=None):
    g = T.ganador(r)
    resto = sorted((c for c in T.FAM if c not in (g, 'OTROS') and r['pct'][c]), key=lambda c: -r['pct'][c])
    seg = resto[0]
    veces = {}
    for y in T.GENERALES:
        gg = T.ganador(serie[y])
        veces[gg] = veces.get(gg, 0) + 1
    top = max(veces, key=veces.get)
    reg = REGIONAL.get(ccaa, {})
    art = lambda c: reg[c] if c in reg and ' ' in reg[c] else ('el ' if c in ('PP', 'PSOE', 'PNV', 'BNG', 'CDS', 'PSC') or reg.get(c) == 'PSC' else '') + reg.get(c, T.NOMBRE[c].split(' /')[0])
    nom_top = {'SUMAR': 'el espacio a la izquierda del PSOE', 'BILDU': 'la izquierda abertzale', 'JUNTS': 'CiU y después Junts'}.get(top, art(top))
    comp = 'más que' if r['part'] > T.ESPANA['part'] + 0.005 else ('menos que' if r['part'] < T.ESPANA['part'] - 0.005 else 'casi lo mismo que')
    if ccaa == 'navarra' and g == 'PP':   # en 2023 UPN y PP fueron por separado: la familia suma las dos listas
        return (f'En las elecciones generales del 23 de julio de 2023, UPN y el PP, que se presentaron por separado, sumaron el {pct(r["pct"]["PP"])} del voto válido en Navarra '
                f'(en el mapa cuentan juntos porque en otras elecciones fueron en coalición); la lista más votada fue la del {art(seg)[3:]} ({pct(r["pct"][seg])}). '
                f'Votó el {pct(r["part"])} del censo, {comp} en el conjunto de España ({pct(T.ESPANA["part"])}).')
    return (f'En las elecciones generales del 23 de julio de 2023, {art(g)} fue la fuerza más votada {en}, con el {pct(r["pct"][g])} del voto válido, '
            f'seguido {"del " + art(seg)[3:] if art(seg).startswith("el ") else "de " + art(seg)} ({pct(r["pct"][seg])}). Votó el {pct(r["part"])} del censo, {comp} en el conjunto de España ({pct(T.ESPANA["part"])}). '
            f'Desde 1977, {nom_top} ha sido el partido más votado en {veces[top]} de las {len(T.GENERALES)} elecciones generales.')


def bloque_resultado(nombre, r):
    filas = [[escape(T.NOMBRE[c]), pct(r['pct'][c]), num(r['votos'][c]), pct(T.ESPANA['pct'][c])]
             for c in sorted(T.FAM, key=lambda c: -(r['pct'][c] or 0)) if (r['pct'][c] or 0) >= 0.005 or c == 'OTROS']
    return ('<h2>Resultado de las generales de 2023</h2>'
            + p_('Dato', f'Voto por partido sobre voto válido (candidaturas más blancos) en {escape(nombre)}. La línea discontinua marca el resultado del conjunto de España. '
                 f'Votaron {num(r["votantes"])} de {num(r["censo"])} electores residentes.')
            + f'<figure>{barras(r, T.ESPANA)}<figcaption>Elecciones generales del 23 de julio de 2023, sin voto desde el extranjero (CERA). Fuente: Ministerio del Interior.</figcaption></figure>'
            + tabla(f'Voto por partido en {escape(nombre)}, 23J 2023', ['Partido', 'Voto', 'Votos', 'España'], filas))


def bloque_serie(nombre, serie):
    fams = [c for c in T.FAM if c != 'OTROS' and max((serie[y]['pct'][c] or 0) for y in T.GENERALES) >= 0.05]
    filas = []
    for y in T.GENERALES:
        r = serie[y]
        g = T.ganador(r)
        filas.append([T.etiqueta(y), pct(r['part']), escape(T.nombre_familia(g, y)) if g else '—'] + [pct(r['pct'][c]) if r['pct'][c] else '—' for c in fams])
    falta = [T.etiqueta(y) for y in T.GENERALES if serie[y]['sin_dato']]
    nota = (f' En {", ".join(falta)} faltan en los ficheros de Interior los resultados de algún municipio de {escape(nombre)}; se calcula con los que hay.' if falta else '')
    return ('<h2>De 1977 a 2023: las 16 elecciones generales</h2>'
            + p_('Dato', f'Voto de los partidos que han pasado alguna vez del 10 % en {escape(nombre)}. Las familias agrupan a cada partido con sus antecesores y coaliciones: '
                 'el PP incluye a AP (hasta 1986) y a UPN; «Sumar / Podemos / IU», al PCE y el PSUC, IU y Unidas Podemos; «Junts / CiU», a CiU. '
                 'Cuando una familia reúne listas que se presentaron por separado (Podemos e IU en 2015, UPN y el PP en 2023), su porcentaje es la suma de las dos. '
                 f'Detalle en la <a href="{RAIZ_REL}generales-2026/metodologia.html">metodología del mapa</a>.{nota}')
            + f'<figure>{lineas(serie)}<figcaption>Porcentaje de voto válido en las elecciones al Congreso. Sin voto desde el extranjero (CERA).</figcaption></figure>'
            + tabla(f'Participación, partido más votado y voto por partido en {escape(nombre)}', ['Elección', 'Participación', 'Más votado'] + [escape(T.NOMBRE[c]) for c in fams], filas, num_desde=1))


def bloque_renta(nombre, en, sec):
    q = T.por_renta(sec)
    if not q:
        return ''
    r1, r5 = q[0], q[-1]
    fams = [c for c in T.FAM if c != 'OTROS' and max(x['pct'][c] for x in q) >= 0.05]
    fams.sort(key=lambda c: -sum(x['pct'][c] for x in q))
    principales = fams[:2]
    frases = '; '.join(f'{T.NOMBRE[c]}, {pct(r5["pct"][c])} frente a {pct(r1["pct"][c])}' for c in principales)
    filas = [[f'{x["q"]}.º' + (' (menos renta)' if x['q'] == 1 else ' (más renta)' if x['q'] == len(q) else ''),
              f'{euros(x["desde"])} – {euros(x["hasta"])}', num(x['secciones']), pct(x['part'])] + [pct(x['pct'][c]) for c in fams] for x in q]
    return ('<h2 id="renta">Voto y renta por barrios</h2>'
            + p_('Patrón', f'En el 20 % del censo que vive en las secciones censales con más renta {en} (más de {euros(r5["desde"])} por unidad de consumo) votó el {pct(r5["part"])}; '
                 f'en el 20 % con menos renta (menos de {euros(r1["hasta"])}), el {pct(r1["part"])}.')
            + p_('Patrón', f'Voto en las secciones con más renta frente a las de menos: {frases}.')
            + '<p class="leyenda">Es una relación entre barrios, no entre personas: no dice cómo vota cada vecino. '
              f'Más sobre cómo se cruza el voto con la renta en <a href="{RAIZ_REL}elecciones/voto-y-renta-por-barrios/">voto y renta por barrios en toda España</a>.</p>'
            + tabla(f'Generales de 2023 {en}: secciones censales ordenadas por renta neta por unidad de consumo (INE, 2023) y agrupadas en cinco grupos con el mismo censo',
                    ['Grupo', 'Renta', 'Secciones', 'Participación'] + [escape(T.NOMBRE[c]) for c in fams], filas))


def bloque_municipios(nombre, df, nivel, n=15):
    y = T.ULTIMA
    raiz = '../' * nivel
    d = df[df.poblacion.notna()].sort_values('poblacion', ascending=False).head(n)
    filas = []
    for _, m in d.iterrows():
        r = T.resultado(m.to_frame().T, y)
        g = T.ganador(r)
        filas.append([f'<a href="{raiz}?m={m.mun_code}">{escape(m.municipio)}</a>', num(m.poblacion), pct(m[f"{y}_part"]),
                      f'{escape(T.NOMBRE[g])} ({pct(r["pct"][g])})' if g else '—'])
    out = ('<h2>Municipios</h2>'
           + p_('Dato', f'Los {len(d)} municipios con más habitantes de {escape(nombre)} en las generales de 2023. Cada nombre abre el municipio en el '
                f'<a href="{raiz}">mapa de resultados por sección censal</a>, donde se ve barrio a barrio y en cualquier elección desde 1977.')
           + tabla(f'Municipios más poblados de {escape(nombre)}, generales de 2023', ['Municipio', 'Habitantes', 'Participación', 'Más votado'], filas))
    grandes = df[df[f'{y}_censo'] >= 1000].dropna(subset=[f'{y}_part'])
    if len(grandes) >= 10:
        alto, bajo = grandes.nlargest(3, f'{y}_part'), grandes.nsmallest(3, f'{y}_part')
        lista = lambda g: ', '.join(f'<a href="{raiz}?m={m.mun_code}">{escape(m.municipio)}</a> ({pct(m[f"{y}_part"])})' for _, m in g.iterrows())
        out += p_('Dato', f'Entre los municipios con al menos 1.000 electores, donde más se votó fue en {lista(alto)}, y donde menos, en {lista(bajo)}.')
    return out


def bloque_relacionadas(provs, nivel, extra=()):
    rel = list(extra) + relacionadas(provs, nivel)
    if not rel:
        return ''
    vistos, li = set(), []
    for u, t, s in rel:
        if u not in vistos:
            vistos.add(u)
            li.append(f'<li><a href="{u}"><span class="kicker">{s}</span><b>{escape(t)}</b></a></li>')
    return '<h2>Piezas sobre este territorio</h2><ul class="sigue">' + ''.join(li) + '</ul>'


def bloque_metodo():
    return (f'<h2>Método y fuentes</h2><dl class="ficha">'
            '<dt>Datos</dt><dd>Resultados oficiales por mesa y por municipio del Ministerio del Interior (Infoelectoral) para las elecciones al Congreso de 1977 a 2023, '
            'sin el voto de los residentes en el extranjero (CERA), que no se asigna a ningún municipio. Renta neta por unidad de consumo de cada sección censal: '
            'Atlas de Distribución de Renta de los Hogares del INE (2023).</dd>'
            '<dt>Cómo se calcula</dt><dd>Porcentajes sobre voto válido (candidaturas más votos en blanco), sumando votos, no promediando porcentajes. '
            'Participación: votantes entre censo. Los grupos de renta reúnen secciones con el mismo censo electoral cada uno. '
            f'Agrupación de partidos y límites: <a href="{RAIZ_REL}generales-2026/metodologia.html">metodología del mapa</a>.</dd>'
            f'<dt>Datos abiertos</dt><dd>Todas las cifras de esta página salen de las <a href="{RAIZ_REL}generales-2026/metodologia.html#descargas">descargas del mapa</a> '
            f'(CSV, licencia <a href="{LICENCIA}">CC BY 4.0</a>).</dd>'
            f'<dt>Autoría y revisión</dt><dd><a href="{RAIZ_REL}sobre-mi.html">{esquema.FIRMA}</a>. Publicado el {fecha(PUBLICADO)}; actualizado el {fecha(ACTUALIZADO)}. '
            f'<a href="{RAIZ_REL}atlas/politica-editorial/">Política editorial</a> · <a href="{RAIZ_REL}atlas/correcciones/">Correcciones</a></dd></dl>')


def fecha(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d.day} de {atlas.MESES[d.month - 1]} de {d.year}'


RAIZ_REL = ''   # se fija en cada página (ruta relativa a la raíz del sitio)


# ---------- cabecera y pie ----------
def cabeza(titulo, desc, ruta, ld, nivel, miga):
    global RAIZ_REL
    RAIZ_REL = '../' * nivel
    raiz = RAIZ_REL
    menu = [('', 'Mapa de resultados'), ('elecciones/', 'Por territorio'), ('atlas/', 'Atlas'), ('actualidad/', 'Actualidad'),
            ('abstencion.html', 'Cataluña'), ('sobre-mi.html', 'Sobre mí')]
    nav = (f'<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="{raiz or "./"}">{SITIO}</a>'
           + ''.join(f'<a href="{raiz}{h}"{" aria-current=\"page\"" if h == "elecciones/" else ""}>{t}</a>' for h, t in menu) + '</nav>')
    url = BASE + ruta
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="author" content="{esquema.FIRMA}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITIO}">
<meta property="og:title" content="{escape(titulo)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}img/compartir/portada.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@nachotronic">
<link rel="license" href="{LICENCIA}">
<link rel="alternate" type="text/plain" title="llms.txt" href="{BASE}elecciones/llms.txt">
<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/')}
</script>
{atlas.CF}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{atlas.CSS}
.migas{{font-family:var(--sans);font-size:.85rem;color:var(--muted);margin:0 0 .4rem}}.migas a{{color:inherit}}
.cols{{columns:2 14rem;column-gap:2rem}}td.n{{white-space:nowrap}}.cols li{{break-inside:avoid}}
</style>
</head>
<body>
{nav}
<main>
"""


def migas_html(pasos):
    return '<p class="migas">' + ' › '.join(f'<a href="{u}">{escape(n)}</a>' for u, n in pasos) + '</p>'


PIE = f"""<footer>{SITIO} · Datos con licencia <a href="{LICENCIA}">CC BY 4.0</a> · <a href="{atlas.REPO}">Código y datos</a> · Por {esquema.FIRMA}</footer>
</main>
</body>
</html>
"""


def ld_pagina(titulo, desc, ruta, about=None, partes=None):
    o = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': BASE + ruta + '#pagina', 'name': titulo, 'description': desc, 'url': BASE + ruta,
         'inLanguage': 'es', 'datePublished': PUBLICADO, 'dateModified': ACTUALIZADO, 'author': esquema.AUTOR, 'publisher': {'@id': BASE + '#medio'},
         'isPartOf': {'@id': BASE + '#website'}, 'license': LICENCIA, 'isAccessibleForFree': True,
         'isBasedOn': {'@type': 'Dataset', '@id': esquema.DATASET_ID, 'url': BASE + 'generales-2026/metodologia.html'},
         'primaryImageOfPage': BASE + 'img/compartir/portada.jpg'}
    if about:
        o['about'] = about
    if partes:
        o['hasPart'] = partes
    return o


def lugar(nombre, dentro=None):
    o = {'@type': 'AdministrativeArea', 'name': nombre}
    if dentro:
        o['containedInPlace'] = dentro
    return o


ESPANA = {'@type': 'Country', 'name': 'España'}


# ---------- páginas de territorio ----------
def pagina_territorio(nombre, en, provs, ruta, nivel, pasos, hijos=(), extra=(), tipo_txt='Comunidad', contenido=None, ccaa=None):
    df = T.MUN[T.MUN.prov.isin(provs)]
    sec = T.SEC[T.SEC.prov.isin(provs)]
    serie = T.serie(df)
    r = serie[T.ULTIMA]
    g = T.ganador(r)
    titulo = f'Elecciones en {nombre}: resultados por municipio y sección censal desde 1977'
    desc = (f'Resultados de las elecciones generales {en} de 1977 a 2023: en 2023, {T.NOMBRE[g]} {pct(r["pct"][g])} y participación del {pct(r["part"])}. '
            'Voto por renta de los barrios y municipios principales.')
    about = lugar(nombre, contenido or ESPANA)
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, about), nivel, nombre)]
    raiz = RAIZ_REL
    h.append(migas_html(pasos))
    h.append(f'<p class="kicker">{tipo_txt} · Elecciones generales 1977-2023</p><h1 data-miga="{escape(nombre)}">Elecciones en {escape(nombre)}</h1>')
    h.append(f'<p class="subtitulo">Resultados por municipio y por sección censal, voto por renta de los barrios y las 16 generales desde 1977</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(f'<p class="resumen">{tipo("Dato")}{entradilla(nombre, en, r, serie, ccaa)}</p>')
    mayor = df.sort_values('poblacion', ascending=False).iloc[0]
    h.append(f'<p><a class="vermapa" href="{raiz}?m={mayor.mun_code}">Ver {escape(mayor.municipio)} y el resto de {escape(nombre)} en el mapa por sección censal</a></p>')
    if hijos:
        h.append('<h2>Provincias</h2>' + tabla(f'Generales de 2023 {en}, por provincia', ['Provincia', 'Participación', 'Más votado', 'Segundo'],
                                                [hijo for hijo in hijos]))
    h.append(bloque_resultado(nombre, r))
    h.append(bloque_serie(nombre, serie))
    h.append(bloque_renta(nombre, en, sec))
    h.append(bloque_municipios(nombre, df, nivel))
    h.append(bloque_relacionadas(provs, nivel, extra))
    h.append(f'<h2>Más datos</h2><ul><li><a href="{raiz}elecciones/">Elecciones por comunidad autónoma y provincia</a></li>'
             f'<li><a href="{raiz}elecciones/mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li>'
             f'<li><a href="{raiz}elecciones/voto-y-renta-por-barrios/">Voto y renta por barrios en toda España</a></li>'
             f'<li><a href="{raiz}atlas/">Atlas de las anomalías electorales</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h), {'nombre': nombre, 'ganador': g, 'r': r}


def fila_resumen(enlace, r):
    orden = sorted((c for c in T.FAM if c != 'OTROS' and r['pct'][c]), key=lambda c: -r['pct'][c])
    return [enlace, pct(r['part']), f'{escape(T.NOMBRE[orden[0]])} ({pct(r["pct"][orden[0]])})', f'{escape(T.NOMBRE[orden[1]])} ({pct(r["pct"][orden[1]])})']


def territorios():
    paginas, resumen = [], {}
    for slug, (nombre, en, provs) in CCAA.items():
        hist = f'actualidad/{slug}-historia-electoral'
        extra = [(f'../../{hist}/', h1_de(hist), 'Historia electoral')] if h1_de(hist) else []
        if slug == 'cataluna':
            extra.append(('../../abstencion.html', '¿Quién no vota en Cataluña? La abstención por sección censal, cruzada con renta, edad y origen', 'Reportaje'))
        hijos, contenido = [], lugar(nombre, ESPANA)
        if len(provs) > 1:
            for p in provs:
                pn = PROV_NOMBRE[p]
                ruta = f'elecciones/{slug}/{PROV_SLUG[p]}/'
                pasos = [('../../../', 'Inicio'), ('../../', 'Elecciones'), ('../', nombre)]
                ex = ([(f'../../../{hist}/', h1_de(hist), 'Historia electoral')] if h1_de(hist) else [])
                if slug == 'cataluna':
                    ex.append(('../../../abstencion.html', '¿Quién no vota en Cataluña? La abstención por sección censal, cruzada con renta, edad y origen', 'Reportaje'))
                ruta, html, info = pagina_territorio(pn, f'en la provincia de {pn}', [p], ruta, 3, pasos, extra=ex, tipo_txt='Provincia', contenido=contenido, ccaa=slug)
                paginas.append((ruta, html))
                hijos.append(fila_resumen(f'<a href="{PROV_SLUG[p]}/">{escape(pn)}</a>', info['r']))
        ruta = f'elecciones/{slug}/'
        ruta, html, info = pagina_territorio(nombre, en, provs, ruta, 2, [('../../', 'Inicio'), ('../', 'Elecciones')], hijos=hijos, extra=extra, ccaa=slug)
        paginas.append((ruta, html))
        resumen[slug] = info
    return paginas, resumen


# ---------- índice y páginas temáticas ----------
def indice(resumen):
    titulo = 'Elecciones en España por comunidad autónoma, provincia y sección censal'
    desc = 'Resultados de las elecciones generales de 1977 a 2023 en cada comunidad autónoma y provincia, con el voto por renta de los barrios y enlaces al mapa por sección censal.'
    partes = [{'@type': 'WebPage', 'name': f'Elecciones en {i["nombre"]}', 'url': BASE + f'elecciones/{s}/'} for s, i in resumen.items()]
    h = [cabeza(titulo, desc, 'elecciones/', ld_pagina(titulo, desc, 'elecciones/', ESPANA, partes), 1, 'Elecciones')]
    h.append(migas_html([('../', 'Inicio')]))
    h.append(f'<p class="kicker">Elecciones generales 1977-2023</p><h1 data-miga="Elecciones por territorio">Elecciones en España por comunidad y provincia</h1>')
    h.append(f'<p class="resumen">{tipo("Dato")}Una página por comunidad autónoma y por provincia con el resultado de las generales de 2023, la serie de las 16 elecciones '
             f'al Congreso desde 1977, cómo vota cada grupo de barrios según su renta y los municipios principales. En el conjunto de España, en 2023 votó el '
             f'{pct(T.ESPANA["part"])} del censo residente y el PP fue el más votado con el {pct(T.ESPANA["pct"]["PP"])}.</p>')
    h.append(f'<p><a class="vermapa" href="../">Abrir el mapa de resultados por sección censal</a></p>')
    filas = [fila_resumen(f'<a href="{s}/">{escape(i["nombre"])}</a>', i['r']) for s, i in resumen.items()]
    h.append('<h2>Comunidades autónomas</h2>' + tabla('Generales de 2023 por comunidad autónoma', ['Comunidad', 'Participación', 'Más votado', 'Segundo'], filas))
    li = []
    for p in sorted(PROV_SLUG, key=lambda p: PROV_SLUG[p]):
        u = ruta_provincia(p)[len('elecciones/'):]
        li.append(f'<li><a href="{u}">Elecciones en {escape(PROV_NOMBRE[p])}</a></li>')
    h.append('<h2>Provincias</h2><ul class="cols">' + ''.join(li) + '</ul>')
    h.append('<h2>Por tema</h2><ul>'
             '<li><a href="mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a>: qué es una sección, qué datos tiene cada una y cómo consultarlas</li>'
             '<li><a href="voto-y-renta-por-barrios/">Voto y renta por barrios</a>: participación y voto de cada partido según la renta de la sección</li>'
             '<li><a href="../abstencion.html">Participación por sección censal en Cataluña</a>: quién no vota y dónde</li>'
             '<li><a href="../atlas/">Atlas de las anomalías electorales</a>: los lugares que votan distinto de lo que cabría esperar</li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return 'elecciones/', ''.join(h)


def lista_piezas(slugs, nivel):
    raiz = '../' * nivel
    li = [f'<li><a href="{raiz}actualidad/{s}/"><span class="kicker">Actualidad</span><b>{escape(t)}</b></a></li>' for s in slugs if (t := h1_de(f'actualidad/{s}'))]
    return '<ul class="sigue">' + ''.join(li) + '</ul>'


def tema_renta(resumen):
    ruta = 'elecciones/voto-y-renta-por-barrios/'
    titulo = 'Voto y renta por barrios: cómo vota cada sección censal de España según su renta'
    desc = ('Participación y voto a cada partido en las 36.000 secciones censales de España ordenadas por renta, en las generales de 2023 y desde 2004. '
            'Datos del Ministerio del Interior y del INE.')
    q10 = T.por_renta(T.SEC, 10)
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Voto y renta')]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Generales 2023</p><h1 data-miga="Voto y renta por barrios">Voto y renta por barrios</h1>')
    h.append('<p class="subtitulo">Cómo votan las secciones censales de España según su renta: participación y voto a cada partido, del 10 % más pobre al 10 % más rico</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    a, b = q10[0], q10[-1]
    h.append(f'<p class="resumen">{tipo("Patrón")}En el 10 % del censo que vive en las secciones censales con menos renta de España (menos de {euros(a["hasta"])} por unidad de consumo) '
             f'votó el {pct(a["part"])} en las generales de 2023; en el 10 % con más renta (más de {euros(b["desde"])}), el {pct(b["part"])}. '
             f'El PP pasó del {pct(a["pct"]["PP"])} en las secciones más pobres al {pct(b["pct"]["PP"])} en las más ricas, y el PSOE, del {pct(a["pct"]["PSOE"])} al {pct(b["pct"]["PSOE"])}.</p>')
    h.append('<p>La renta no se conoce para cada votante, pero sí para cada sección censal, el barrio de unas 1.000 a 2.500 personas en el que se organiza el censo. '
             'Ordenando las 36.000 secciones de España por la renta neta por unidad de consumo que publica el INE y agrupándolas en diez grupos con el mismo censo, '
             'se ve cómo cambian la participación y el voto de un extremo a otro.</p>')
    fams = ['PP', 'PSOE', 'VOX', 'SUMAR']
    filas = [[f'{x["q"]}.º', f'{euros(x["desde"])} – {euros(x["hasta"])}', pct(x['part'])] + [pct(x['pct'][c]) for c in fams] for x in q10]
    h.append('<h2>Diez grupos de barrios, del más pobre al más rico</h2>' + svg_deciles(q10, fams)
             + tabla('Generales de 2023: secciones censales de España agrupadas por renta en diez grupos con el mismo censo electoral',
                     ['Decil', 'Renta', 'Participación'] + [T.NOMBRE[c] for c in fams], filas))
    h.append('<p class="leyenda">Es una relación entre barrios, no entre personas (lo que en estadística se llama falacia ecológica): que un barrio rico vote más al PP no significa que cada vecino rico lo haga.</p>')
    # brecha por comunidad
    filas = []
    for slug, (nombre, en, provs) in CCAA.items():
        q = T.por_renta(T.SEC[T.SEC.prov.isin(provs)])
        if q:
            filas.append([f'<a href="../{slug}/#renta">{escape(nombre)}</a>', pct(q[0]['part']), pct(q[-1]['part']),
                          f'{(q[-1]["part"] - q[0]["part"]) * 100:+.1f}'.replace('.', ',').replace('-', '−') + ' p.'])
    h.append('<h2>La brecha en cada comunidad</h2>'
             + p_('Patrón', 'Participación en las generales de 2023 del 20 % del censo que vive en las secciones con menos renta de cada comunidad y del 20 % que vive en las de más renta. '
                  'Cada comunidad se ordena con sus propias secciones.')
             + tabla('Participación por grupo de renta dentro de cada comunidad, generales de 2023', ['Comunidad', 'Menos renta', 'Más renta', 'Diferencia'], filas))
    h.append('<h2>Piezas sobre renta, vivienda y voto</h2>' + lista_piezas(TEMA_RENTA, 2))
    h.append(f'<ul class="sigue"><li><a href="{raiz}abstencion.html"><span class="kicker">Reportaje</span><b>¿Quién no vota en Cataluña? La abstención por sección censal, cruzada con renta, edad y origen</b></a></li>'
             f'<li><a href="{raiz}atlas/quien-no-vota/paro-renta-participacion/"><span class="kicker">Atlas</span><b>{escape(h1_de("atlas/quien-no-vota/paro-renta-participacion") or "Paro, renta y participación")}</b></a></li></ul>')
    h.append(f'<p>Los mismos datos, sección a sección, en el <a href="{raiz}">mapa de resultados por sección censal</a>, con gráficos por decil de renta, edad, pobreza y población extranjera.</p>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def svg_deciles(q, fams):
    w, h, x0, x1, y0, y1 = 640, 280, 36, 560, 14, 250
    tope = 0.9
    X = lambda i: x0 + (x1 - x0) * i / (len(q) - 1)
    Y = lambda v: y1 - (y1 - y0) * v / tope
    g = [f'<line x1="{x0}" x2="{x1}" y1="{Y(k / 100):.1f}" y2="{Y(k / 100):.1f}" class="rej"/><text x="{x0 - 6}" y="{Y(k / 100) + 4:.1f}" text-anchor="end" class="ej">{k}</text>' for k in range(0, 91, 10)]
    g += [f'<text x="{X(i):.1f}" y="{y1 + 18}" text-anchor="middle" class="ej">{x["q"]}.º</text>' for i, x in enumerate(q)]
    series = [('Participación', 'var(--fg)', [x['part'] for x in q])] + [(T.NOMBRE[c], T.COLOR[c], [x['pct'][c] for x in q]) for c in fams]
    finales = []
    for n, col, vs in series:
        g.append(f'<polyline points="{" ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vs))}" fill="none" stroke="{col}" stroke-width="2.5"{" stroke-dasharray=\"5 3\"" if n == "Participación" else ""}/>')
        finales.append([Y(vs[-1]), n, col])
    finales.sort()
    for i in range(1, len(finales)):
        finales[i][0] = max(finales[i][0], finales[i - 1][0] + 14)
    g += [f'<text x="{x1 + 6}" y="{yy + 4:.1f}" class="lb" fill="{col}">{escape(n.split(" /")[0])}</text>' for yy, n, col in finales]
    return (f'<figure><svg class="graf" viewBox="0 0 {w} {h}" role="img" aria-label="Participación y voto por decil de renta">'
            '<style>.ej{font:12px var(--sans);fill:var(--muted)}.rej{stroke:var(--rule)}.lb{font:600 12px var(--sans)}</style>' + ''.join(g)
            + '</svg><figcaption>Porcentaje por decil de renta (1.º, el 10 % del censo con menos renta; 10.º, el 10 % con más). Participación sobre censo; voto sobre voto válido. '
              'Generales de 2023. Fuente: Ministerio del Interior e INE.</figcaption></figure>')


def tema_seccion(resumen):
    ruta = 'elecciones/mapa-electoral-seccion-censal/'
    titulo = 'Mapa electoral de España por sección censal: resultados barrio a barrio desde 2004'
    desc = ('Qué es una sección censal y cómo consultar los resultados de las generales, municipales y europeas en las 36.462 secciones de España, '
            'con renta, edad y población extranjera. Datos abiertos.')
    y = T.ULTIMA
    sec = T.SEC
    gana = sec[[c for c in T.FAM if c != 'OTROS']].idxmax(axis=1)
    cuenta = gana.value_counts()
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Mapa por sección censal')]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Datos abiertos</p><h1 data-miga="Mapa por sección censal">Mapa electoral de España por sección censal</h1>')
    h.append('<p class="subtitulo">Resultados de las elecciones barrio a barrio en las 36.462 secciones censales de España, cruzados con renta, edad y población extranjera</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    top = cuenta.index[:4]
    h.append(f'<p class="resumen">{tipo("Dato")}En las generales de 2023 el PP fue la lista más votada en {num(cuenta.get("PP", 0))} de las {num(len(sec))} secciones censales de España; '
             f'el PSOE, en {num(cuenta.get("PSOE", 0))}. ' + ', '.join(f'{T.NOMBRE[c]}, en {num(cuenta[c])}' for c in top if c not in ('PP', 'PSOE')) + '.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Abrir el mapa por sección censal</a> <a class="vermapa" href="{raiz}generales-2026/metodologia.html#descargas">Descargar los datos</a></p>')
    h.append('<h2>Qué es una sección censal</h2>'
             '<p>Es la unidad más pequeña en la que se organiza el censo electoral: cada municipio se divide en distritos y cada distrito en secciones, de entre unas 500 y 2.500 personas con derecho a voto. '
             'Cada sección vota en sus propias mesas, así que su resultado se conoce, y el INE publica para cada una la renta, la edad media, la población extranjera y, con el censo de 2021, los estudios y el paro. '
             'Por eso la sección es la mejor escala para ver cómo vota un barrio sin bajar a las personas.</p>'
             '<p>Las secciones cambian con el tiempo: se parten cuando crecen y se unen cuando se vacían. El mapa usa las de 2023 y lleva a ellas los resultados desde 2004; las elecciones anteriores se ven por municipio.</p>')
    h.append('<h2>Qué hay en el mapa</h2><ul>'
             '<li>Elecciones al Congreso por sección censal de 2004 a 2023, y por municipio desde 1977.</li>'
             '<li>Municipales por sección de 2011 a 2023 y europeas por sección de 2004 a 2024.</li>'
             '<li>Para cada sección: participación, voto de cada partido y partido más votado; renta neta por unidad de consumo, población en riesgo de pobreza, edad media y población extranjera (INE, 2023), estudios y paro (Censo 2021).</li>'
             '<li>Gráficos por decil de renta, edad, pobreza y población extranjera, y el modo en directo para la noche electoral del 29 de noviembre de 2026.</li></ul>')
    h.append('<h2>Cómo usarlo</h2><ol>'
             '<li>Busca tu municipio en el buscador del mapa o haz clic en él; al acercarte aparecen las secciones y las calles.</li>'
             '<li>Cambia de elección con el selector para ver cómo ha cambiado el voto del barrio.</li>'
             '<li>Pulsa en una sección para ver su ficha: voto por partido con el nombre real de la candidatura (PSC, UPN, En Comú Podem…), renta, edad y población extranjera.</li>'
             f'<li>Para usarlo en otra web, el mapa se puede <a href="{raiz}insertar/">insertar</a> con un iframe.</li></ol>')
    filas = [fila_resumen(f'<a href="../{s}/">{escape(i["nombre"])}</a>', i['r']) for s, i in resumen.items()]
    h.append('<h2>Por comunidad y provincia</h2>' + tabla('Generales de 2023 por comunidad autónoma', ['Comunidad', 'Participación', 'Más votado', 'Segundo'], filas)
             + '<p>Cada comunidad tiene su página con sus provincias, la serie desde 1977 y el voto por renta de sus secciones: <a href="../">elecciones por comunidad y provincia</a>.</p>')
    h.append('<h2>Piezas hechas con las secciones censales</h2>' + lista_piezas(TEMA_SECCION, 2)
             + f'<ul class="sigue"><li><a href="../voto-y-renta-por-barrios/"><span class="kicker">Tema</span><b>Voto y renta por barrios: cómo vota cada sección según su renta</b></a></li>'
               f'<li><a href="{raiz}abstencion.html"><span class="kicker">Reportaje</span><b>¿Quién no vota en Cataluña? La abstención en las 5.115 secciones censales catalanas</b></a></li></ul>')
    h.append('<h2>Datos abiertos</h2>'
             f'<p>Todas las tablas se descargan en CSV con licencia <a href="{LICENCIA}">CC BY 4.0</a>: se pueden reutilizar citando la fuente. '
             f'Columnas, fuentes y límites, en la <a href="{raiz}generales-2026/metodologia.html">metodología del mapa</a>; el código está en <a href="{atlas.REPO}">GitHub</a>.</p>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


# ---------- sitemap y llms.txt ----------
def sitemap(rutas):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + ''.join(f'  <url><loc>{BASE}{r}</loc><lastmod>{ACTUALIZADO}</lastmod></url>\n' for r in rutas) + '</urlset>\n')


def llms(resumen):
    li = '\n'.join(f'- [Elecciones en {i["nombre"]}]({BASE}elecciones/{s}/): en 2023, {T.NOMBRE[i["ganador"]]} {pct(i["r"]["pct"][i["ganador"]])}; participación {pct(i["r"]["part"])}.'
                   for s, i in resumen.items())
    return f"""# Elecciones en España por comunidad, provincia y sección censal

> Páginas de entrada de Mapa Electoral: una por comunidad autónoma y por provincia con el resultado de las generales de 2023, la serie de las 16 elecciones al Congreso desde 1977, el voto por renta de las secciones censales y los municipios principales. Más dos páginas temáticas. Autor: {esquema.FIRMA}. Datos: Ministerio del Interior e INE, licencia CC BY 4.0.

## Temas
- [Mapa electoral de España por sección censal]({BASE}elecciones/mapa-electoral-seccion-censal/)
- [Voto y renta por barrios]({BASE}elecciones/voto-y-renta-por-barrios/)

## Comunidades autónomas
{li}
"""


def franja_portada():
    """Bloque de la portada con enlaces a las páginas por territorio y por tema (anclas descriptivas)."""
    ccaa = ' · '.join(f'<a href="elecciones/{c}/">{escape(n)}</a>' for c, (n, _, _) in CCAA.items())
    return ('<section class="col explora" aria-labelledby="h-explora"><h2 id="h-explora">Elecciones por comunidad y provincia</h2>'
            '<p>Resultados de las 16 generales desde 1977, voto por renta de los barrios y municipios principales de cada territorio: ' + ccaa + '. '
            '<a href="elecciones/">Todas las provincias</a>.</p>'
            '<p>Por tema: <a href="elecciones/voto-y-renta-por-barrios/">voto y renta por barrios</a> · '
            '<a href="elecciones/mapa-electoral-seccion-censal/">mapa electoral por sección censal</a> · '
            '<a href="abstencion.html">participación por sección censal en Cataluña</a> · '
            '<a href="atlas/">anomalías electorales municipio a municipio</a></p></section>')


def portada():
    """Rellena la franja entre <!--territorios--> en la portada y en la plantilla del mapa (rutas desde generales-2026/)."""
    for f in (ROOT / 'index.html', ROOT / 'generales-2026' / 'src' / 'plantilla.html'):
        t = f.read_text(encoding='utf-8')
        if '<!--territorios-->' not in t:
            t = t.replace('<!--/atlas:ultimas-->', '<!--/atlas:ultimas-->\n<!--territorios--><!--/territorios-->', 1)
        pre = '' if f.name == 'index.html' else '../'
        franja = re.sub(r'href="(?!https?:)', 'href="' + pre, franja_portada())
        t = re.sub(r'<!--territorios-->.*?<!--/territorios-->', lambda m: '<!--territorios-->' + franja + '<!--/territorios-->', t, flags=re.S)
        f.write_text(t, encoding='utf-8')


def main():
    pags, resumen = territorios()
    pags += [indice(resumen), tema_renta(resumen), tema_seccion(resumen)]
    for ruta, html in pags:
        f = ROOT / ruta / 'index.html'
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html, encoding='utf-8')
    rutas = sorted(r for r, _ in pags)
    (OUT / 'sitemap.xml').write_text(sitemap(rutas), encoding='utf-8')
    (OUT / 'llms.txt').write_text(llms(resumen), encoding='utf-8')
    portada()
    esquema.main()
    print(f'territorios: {len(pags)} páginas en elecciones/')


if __name__ == '__main__':
    main()
