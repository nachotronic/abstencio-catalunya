"""Páginas de entrada por territorio y por tema en /elecciones/.

- /elecciones/: índice de comunidades y provincias.
- /elecciones/<comunidad>/ y /elecciones/<comunidad>/<provincia>/: resultado del 23J, serie de las 16 generales
  desde 1977, voto por renta de sus secciones censales, municipios principales y enlaces a las piezas del sitio
  sobre ese territorio. Las comunidades de una sola provincia no tienen página de provincia.
- /elecciones/mapa-electoral-seccion-censal/ y /elecciones/voto-y-renta-por-barrios/: páginas temáticas.

- /municipio/<provincia>/<municipio>/: una página por municipio de más de 1.000 habitantes (y cada capital), con índices
  en /municipio/ y /municipio/<provincia>/. Hasta octubre de 2026 estaban en /elecciones/<comunidad>/<provincia>/<municipio>/;
  ahí queda una redirección (meta refresh inmediato + canonical, lo más parecido a un 301 que permite GitHub Pages).
- /temas/<tema>/: páginas nodales que reúnen las piezas de Actualidad y del Atlas de cada tema, las páginas de datos
  y los municipios que esas piezas citan (src/territorios_rutas.py, TEMAS).
Ninguna cifra se escribe a mano: salen de las descargas públicas del mapa (src/territorios_datos.py).
Cada frase con cifras va marcada como dato o patrón, como en el resto del sitio.

Uso (después de regenerar el mapa y el Atlas):  python3 src/territorios.py && python3 src/seo.py
"""
import datetime, json, pathlib, re, sys, unicodedata
import pandas as pd
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'atlas' / 'src'))
import territorios_datos as T  # noqa: E402
import mapas_svg as MS  # noqa: E402
import territorios_barrios as TB  # noqa: E402
import esquema  # noqa: E402
import paginas as atlas  # noqa: E402  (estilos, piezas y titulares del Atlas)
from piezas import piezas  # noqa: E402
from piezas2 import piezas2  # noqa: E402
from piezas3 import piezas3  # noqa: E402

BASE = esquema.BASE
OUT = ROOT / 'elecciones'
PUBLICADO = '2026-10-13'
ACTUALIZADO = '2026-10-26'   # cámbiala a mano cuando cambien los datos o el texto
BARRIOS_PUBLICADO = '2026-10-22'   # fichas de barrio
SITIO = 'Mapa Electoral'
LICENCIA = 'https://creativecommons.org/licenses/by/4.0/'

from territorios_rutas import PROV_SLUG, CCAA, PROV_CCAA, PROV_NOMBRE, ruta_provincia, ACTUALIDAD_LUGAR, ACTUALIDAD_MUNICIPIO, TEMA_RENTA, TEMA_SECCION, \
    TEMA_PARTICIPACION, TEMA_MUNICIPIOS, ESCANOS_2023, ESCANOS_2026, es_29n, TEMAS, slug, ruta_municipio, ruta_municipio_antigua  # noqa: E402

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
        q['_muns'] = set(atlas.municipios(q))   # se consulta en cada una de las 3.133 páginas de municipio
    return todas


ATLAS = piezas_atlas()


def publicada(slug):
    """Fecha de publicación (ISO) de una pieza de Actualidad, leída de su JSON-LD."""
    f = ROOT / 'actualidad' / slug / 'index.html'
    m = re.search(r'"datePublished": *"([0-9-]{10})', f.read_text(encoding='utf-8')) if f.exists() else None
    return m.group(1) if m else ''


def actualidad_de(slugs, raiz):
    """Piezas de Actualidad, la más reciente primero y con su fecha: (url relativa, titular, sección)."""
    out = [(publicada(s), s, t) for s in slugs if (t := h1_de(f'actualidad/{s}'))]
    out.sort(reverse=True)
    return [(f'{raiz}actualidad/{s}/', t, f'Actualidad · {fecha(d)}' if d else 'Actualidad') for d, s, t in out]


def relacionadas(provs, nivel):
    """Piezas de Actualidad (las nuevas primero) y del Atlas sobre alguna de esas provincias: (url relativa, titular, sección)."""
    raiz = '../' * nivel
    out = actualidad_de([s for s, ps in ACTUALIDAD_LUGAR.items() if set(ps) & set(provs)], raiz)
    out += [(f'{raiz}atlas/{atlas.ruta_pieza(q).replace("index.html", "")}', atlas.titular(q), 'Atlas') for q in ATLAS if q['_provs'] & set(provs)]
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
        if gg:   # municipios sin datos en alguna elección (creados después o huecos de 1982)
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
            + desde_1977(veces, nom_top, art))


def desde_1977(veces, nom_top, art):
    n = max(veces.values())
    total = sum(veces.values())
    de = f'de las {len(T.GENERALES)} elecciones generales' if total == len(T.GENERALES) else f'de las {total} elecciones generales con datos del municipio'
    empate = [c for c, v in veces.items() if v == n]
    if len(empate) > 1:
        nombres = ' y '.join(art(c) for c in empate)
        return f'Desde 1977, {nombres} han sido los más votados en {n} {de} cada uno.'
    return f'Desde 1977, {nom_top} ha sido el partido más votado en {n} {de}.'


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


def bloque_renta(nombre, en, sec, ciudad=False):
    q = T.por_renta(sec)
    if not q and ciudad:   # ciudades con pocas secciones: tres grupos en vez de cinco
        q = T.por_renta(sec, 3, 6)
    if not q:
        return ''
    partes = len(q)
    cuota = {5: '20 %', 3: 'tercio'}[partes]
    grupo = lambda extremo: f'el {cuota} del censo'
    r1, r5 = q[0], q[-1]
    fams = [c for c in T.FAM if c != 'OTROS' and max(x['pct'][c] for x in q) >= 0.05]
    fams.sort(key=lambda c: -sum(x['pct'][c] for x in q))
    principales = fams[:2]
    frases = '; '.join(f'{T.NOMBRE[c]}, {pct(r5["pct"][c])} frente a {pct(r1["pct"][c])}' for c in principales)
    filas = [[f'{x["q"]}.º' + (' (menos renta)' if x['q'] == 1 else ' (más renta)' if x['q'] == len(q) else ''),
              f'{euros(x["desde"])} – {euros(x["hasta"])}', num(x['secciones']), pct(x['part'])] + [pct(x['pct'][c]) for c in fams] for x in q]
    return ('<h2 id="renta">Voto y renta por barrios</h2>'
            + p_('Patrón', f'En {grupo(1)} que vive en las secciones censales con más renta {en} (más de {euros(r5["desde"])} por unidad de consumo) votó el {pct(r5["part"])}; '
                 f'en {grupo(0)} con menos renta (menos de {euros(r1["hasta"])}), el {pct(r1["part"])}.')
            + p_('Patrón', f'Voto en las secciones con más renta frente a las de menos: {frases}.')
            + '<p class="leyenda">Es una relación entre barrios, no entre personas: no dice cómo vota cada vecino. '
              f'Más sobre cómo se cruza el voto con la renta en <a href="{RAIZ_REL}elecciones/voto-y-renta-por-barrios/">voto y renta por barrios en toda España</a>.</p>'
            + tabla(f'Generales de 2023 {en}: secciones censales ordenadas por renta neta por unidad de consumo (INE, 2023) y agrupadas en {"cinco" if partes == 5 else "tres"} grupos con el mismo censo',
                    ['Grupo', 'Renta', 'Secciones', 'Participación'] + [escape(T.NOMBRE[c]) for c in fams], filas))


def bloque_municipios(nombre, df, nivel, n=15):
    y = T.ULTIMA
    raiz = '../' * nivel
    d = df[df.poblacion.notna()].sort_values('poblacion', ascending=False).head(n)
    filas = []
    for _, m in d.iterrows():
        r = T.resultado(m.to_frame().T, y)
        g = T.ganador(r)
        nom = (f'<a href="{raiz}{CIUDADES[m.mun_code]}">{escape(m.municipio)}</a> · <a href="{raiz}?m={m.mun_code}">mapa</a>' if m.mun_code in CIUDADES
               else f'<a href="{raiz}?m={m.mun_code}">{escape(m.municipio)}</a>')
        filas.append([nom, num(m.poblacion), pct(m[f"{y}_part"]),
                      f'{escape(T.NOMBRE[g])} ({pct(r["pct"][g])})' if g else '—'])
    out = ('<h2>Municipios</h2>'
           + p_('Dato', f'Los {len(d)} municipios con más habitantes de {escape(nombre)} en las generales de 2023. Los municipios de más de 1.000 habitantes y las capitales tienen página propia; '
                f'«mapa» abre el municipio en el <a href="{raiz}">mapa de resultados por sección censal</a>, donde se ve barrio a barrio y en cualquier elección desde 1977.')
           + tabla(f'Municipios más poblados de {escape(nombre)}, generales de 2023', ['Municipio', 'Habitantes', 'Participación', 'Más votado'], filas))
    grandes = df[df[f'{y}_censo'] >= 1000].dropna(subset=[f'{y}_part'])
    if len(grandes) >= 10:
        alto, bajo = grandes.nlargest(3, f'{y}_part'), grandes.nsmallest(3, f'{y}_part')
        lista = lambda g: ', '.join(f'<a href="{raiz}{CIUDADES[m.mun_code] if m.mun_code in CIUDADES else "?m=" + m.mun_code}">{escape(m.municipio)}</a> ({pct(m[f"{y}_part"])})' for _, m in g.iterrows())
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
def cabeza(titulo, desc, ruta, ld, nivel, miga, imagen=None):
    global RAIZ_REL
    RAIZ_REL = '../' * nivel
    raiz = RAIZ_REL
    menu = [('', 'Mapa de resultados'), ('elecciones/', 'Por territorio'), ('municipio/', 'Municipios'), ('municipio/barrios/', 'Barrios'), ('temas/', 'Temas'), ('encuestas/', 'Encuestas'),
            ('atlas/', 'Atlas'), ('actualidad/', 'Actualidad'), ('actualidad/#comunidades', 'Comunidades'), ('actualidad/#historia', 'Historia electoral'),
            ('sobre-mi.html', 'Sobre mí')]
    actual = ruta.split('/')[0] + '/'
    nav = (f'<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="{raiz or "./"}">{SITIO}</a>'
           + ''.join(f'<a href="{raiz}{h}"{" aria-current=\"page\"" if h == actual else ""}>{t}</a>' for h, t in menu) + '</nav>')
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
<meta property="og:image" content="{BASE}{imagen or "img/compartir/portada.jpg"}">
<meta property="og:image:width" content="{1280 if imagen else 1200}">
<meta property="og:image:height" content="{720 if imagen else 630}">
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
{MS.CSS}
.faq h3{{font-size:1.05rem;margin:1.2rem 0 .3rem}}.sigue .d{{display:block;color:var(--muted);font-weight:400;font-size:.95rem;margin-top:4px}}.foto img{{width:100%;height:auto}}
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


# Páginas publicadas después que el resto
PUBLICADA = {'elecciones/elecciones-29n-2026/': '2026-10-15', 'elecciones/participacion-electoral-por-barrio/': '2026-10-15',
             'elecciones/resultados-elecciones-por-municipio/': '2026-10-15', 'elecciones/censo-electoral-2026/': '2026-10-20', 'elecciones/como-se-vota/': '2026-10-20', 'elecciones/resultados-elecciones-generales-2026/': '2026-10-21', 'elecciones/votar-29n/': '2026-10-26'}


def ld_pagina(titulo, desc, ruta, about=None, partes=None):
    o = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': BASE + ruta + '#pagina', 'name': titulo, 'description': desc, 'url': BASE + ruta,
         'inLanguage': 'es', 'datePublished': PUBLICADA.get(ruta, PUBLICADO), 'dateModified': ACTUALIZADO, 'author': esquema.AUTOR, 'publisher': {'@id': BASE + '#medio'},
         'isPartOf': {'@id': BASE + '#website'}, 'license': LICENCIA, 'isAccessibleForFree': True,
         'isBasedOn': dict(esquema.DATASET_REF),
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
    titulo = f'Elecciones 29N 2026 en {nombre}: censo electoral y cómo votó cada municipio'
    ambito = 'la ciudad' if provs[0] in ('51', '52') else ('la comunidad' if tipo_txt == 'Comunidad' else 'la provincia')
    cods = CENSO.index[CENSO.index.str[:2].isin(provs)]   # del INE, con los municipios nuevos que aún no tienen resultados
    b_censo, q_censo = bloque_censo(nombre, cods, ambito,
                                    [(p, f'<a href="{"../" * nivel}{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a>') for p in provs] if len(provs) > 1 else (), en)
    desc = ((f'Censo electoral para el 29N en {nombre}: {num(censo_29n(cods)[2])} electores. ' if q_censo else '')
            + f'Así votó en las generales de 1977 a 2023: en 2023, {T.NOMBRE[g]} {pct(r["pct"][g])} y participación del {pct(r["part"])}. '
            + 'Voto por renta de los barrios y municipios principales.')
    about = lugar(nombre, contenido or ESPANA)
    faq_html, faq_ld = faq([q_censo]) if q_censo else ('', None)
    ld = ld_pagina(titulo, desc, ruta, about)
    h = [cabeza(titulo, desc, ruta, [ld, faq_ld] if faq_ld else ld, nivel, nombre)]
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
    h.append(b_censo)
    h.append(bloque_serie(nombre, serie))
    if len(provs) == 1 and provs[0] in MAPA_EVOLUCION:
        h.append(bloque_evolucion(nombre, provs))
    h.append(bloque_renta(nombre, en, sec))
    h.append(bloque_municipios(nombre, df, nivel))
    pob = T.MUN.set_index('mun_code').poblacion
    cs = sorted((c for c in CIUDADES if c[:2] in provs), key=lambda c: slug(T.MUN.loc[T.MUN.mun_code == c, 'municipio'].iloc[0]))
    if len(provs) > 1:   # en las comunidades, solo las ciudades; el resto de municipios, en su provincia
        cs = [c for c in cs if c in CAPITALES or pob[c] >= GRANDE]
        intro = 'Capitales y municipios de más de 50.000 habitantes; los de más de 1.000 están en la página de cada provincia'
    else:
        intro = f'Los {num(len(cs))} municipios de más de 1.000 habitantes{" y la capital" if any(c in CAPITALES and pob[c] < UMBRAL for c in cs) else ""}'
    if cs:
        h.append(f'<h2>Municipios con página propia</h2><p>{intro}, con el voto por sección censal y desde 1977: '
                 + ' · '.join(f'<a href="{raiz}{CIUDADES[c]}">elecciones en {escape(T.MUN.loc[T.MUN.mun_code == c, "municipio"].iloc[0])}</a>' for c in cs) + '.</p>')
    h.append(faq_html)
    h.append(bloque_relacionadas(provs, nivel, extra))
    h.append(f'<h2>Más datos</h2><ul><li><a href="{raiz}elecciones/elecciones-29n-2026/">Elecciones generales del 29N de 2026: diputados por provincia</a></li>'
             f'<li><a href="{raiz}elecciones/censo-electoral-2026/">Censo electoral de 2026 en toda España</a></li>'
             f'<li><a href="{raiz}elecciones/">Elecciones por comunidad autónoma y provincia</a></li>'
             f'<li><a href="{raiz}elecciones/participacion-electoral-por-barrio/">Participación electoral por barrio</a></li>'
             f'<li><a href="{raiz}elecciones/mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li>'
             f'<li><a href="{raiz}elecciones/voto-y-renta-por-barrios/">Voto y renta por barrios en toda España</a></li>'
             f'<li><a href="{raiz}atlas/">Atlas de las anomalías electorales</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h), {'nombre': nombre, 'ganador': g, 'r': r}


# ---------- mapa que cambia de elección con botones (provincias de MAPA_EVOLUCION) ----------
MAPA_EVOLUCION = {'17'}   # provincias con el mapa animado; para extenderlo, añade su código

EVOL_CSS = ('.evol-bot{display:flex;flex-wrap:wrap;gap:.3rem;margin:.2rem 0 .6rem}.evol-bot button{font-family:var(--sans);font-size:.8rem;padding:.3rem .55rem;'
            'border:1px solid #bbb;border-radius:3px;background:var(--bg,#fff);color:inherit;cursor:pointer}'
            '.evol-bot button[aria-pressed=true]{background:#111;color:#fff;border-color:#111}'
            '.evol-tit{font-family:var(--sans);font-weight:600;margin:.2rem 0}.evol-info{font-family:var(--sans);font-size:.85rem;min-height:1.3em;margin:.3rem 0 0}'
            '.evol-svg path{transition:fill .5s;cursor:pointer}.evol-svg path:hover{opacity:.75}')

EVOL_JS = """
var fig=document.currentScript.parentNode,ps=fig.querySelectorAll('.evol-svg path'),bs=fig.querySelectorAll('.evol-bot button[data-i]'),
play=fig.querySelector('.evol-play'),tit=fig.querySelector('.evol-tit'),info=fig.querySelector('.evol-info'),ley=fig.querySelector('.evol-ley'),
cur=D.y.length-1,sel=-1,t=null;
function pc(x){return (x/10).toFixed(1).replace('.',',')+' %'}
function txt(k){var v=D.d[cur][k];info.textContent=D.mun[k]+' · '+D.et[cur]+': '+(v?D.nom[cur][v[0]]+', '+pc(v[1]):'sin datos')}
function pinta(i){cur=i;var n={},d=D.d[i],k;for(k=0;k<ps.length;k++){var v=d[k];ps[k].setAttribute('fill',v?D.col[v[0]]:'#e4e4e4');if(v)n[v[0]]=(n[v[0]]||0)+1}
for(k=0;k<bs.length;k++)bs[k].setAttribute('aria-pressed',k==i?'true':'false');
tit.textContent='Generales del '+D.f[i];
ley.innerHTML=Object.keys(n).sort(function(a,b){return n[b]-n[a]}).map(function(c){return '<span><i style="background:'+D.col[c]+'"></i>'+D.nom[i][c]+' ('+n[c]+')</span>'}).join(' ');
if(sel>=0)txt(sel)}
function para(){clearInterval(t);t=null;play.textContent='\\u25B6';play.setAttribute('aria-label','Reproducir')}
for(var k=0;k<bs.length;k++)bs[k].addEventListener('click',function(){para();pinta(+this.dataset.i)});
play.addEventListener('click',function(){if(t){para();return}play.textContent='\\u275A\\u275A';play.setAttribute('aria-label','Pausa');if(cur==D.y.length-1)pinta(0);
t=setInterval(function(){if(cur>=D.y.length-1){para();return}pinta(cur+1)},1400)});
for(k=0;k<ps.length;k++)(function(k){ps[k].addEventListener('click',function(){sel=k;txt(k)});ps[k].addEventListener('mouseenter',function(){txt(k)})})(k);
pinta(cur)})();"""


def bloque_evolucion(nombre, provs):
    """Mapa de municipios con un botón por elección general (1977-2023): cada municipio, del color del más votado."""
    trazos, alto = MS.municipios_zona(provs)
    df = T.MUN.set_index('mun_code')
    trazos = [(c, d) for c, d in trazos if c in df.index]
    cods = [c for c, _ in trazos]
    fams = sorted({g for y in T.GENERALES for g in df.loc[cods, f'{y}_gana'].dropna()}, key=T.FAM.index)
    datos = []
    for y in T.GENERALES:
        datos.append([[fams.index(v), round(float(df.at[c, f'{y}_{v}']) * 1000)] if isinstance(v, str) else None
                      for c, v in df.loc[cods, f'{y}_gana'].items()])

    def frase(y):
        n = df.loc[cods, f'{y}_gana'].value_counts()
        return f'{escape(T.nombre_familia(n.index[0], y))} fue el más votado en {num(n.iloc[0])} de los {num(len(cods))} municipios'
    primera, ultima = T.GENERALES[0], T.ULTIMA
    js = {'y': T.GENERALES, 'et': [T.etiqueta(y) for y in T.GENERALES], 'f': [T.FECHA[y] for y in T.GENERALES], 'col': [T.COLOR[c] for c in fams],
          'nom': [[T.nombre_familia(c, y) for c in fams] for y in T.GENERALES], 'mun': [df.at[c, 'municipio'] for c in cods], 'd': datos}
    paths = ''.join(f'<path d="{d}"/>' for _, d in trazos)
    botones = ''.join(f'<button type="button" data-i="{i}" aria-pressed="{"true" if y == ultima else "false"}">{T.etiqueta(y)}</button>'
                      for i, y in enumerate(T.GENERALES))
    return ('<h2 id="mapa-eleccion">El mapa, elección a elección</h2>'
            + p_('Dato', f'Cada municipio de {escape(nombre)}, del color del partido más votado en cada elección general desde 1977. '
                 f'En {T.etiqueta(primera)}, {frase(primera)}; en {T.etiqueta(ultima)}, {frase(ultima)}. '
                 'Pulsa un año, o el botón de reproducir para verlo cambiar; toca un municipio para ver su resultado.')
            + '<figure class="evol"><div class="evol-bot" role="group" aria-label="Elección">'
            + '<button type="button" class="evol-play" aria-label="Reproducir">&#9654;</button>' + botones + '</div>'
            + '<p class="evol-tit" aria-live="polite"></p>'
            + f'<svg viewBox="0 0 {MS.W} {alto}" class="graf mapa evol-svg" role="img" aria-label="Partido más votado en cada municipio de {escape(nombre)}, por elección general">'
            + f'<g stroke="var(--bg, #fff)" stroke-width="0.5" stroke-linejoin="round">{paths}</g></svg>'
            + '<p class="evol-info">Toca un municipio.</p><p class="leyenda-mapa evol-ley"></p>'
            + '<figcaption>Partido más votado en cada municipio en las elecciones al Congreso de 1977 a 2023, con las familias de partidos del resto de la página. '
              'En gris, municipios sin datos en los ficheros de Interior. Fuente: Ministerio del Interior.</figcaption>'
            + f'<style>{EVOL_CSS}</style>'
            + '<script>(function(){var D=' + json.dumps(js, ensure_ascii=False, separators=(',', ':')) + ';' + EVOL_JS + '</script></figure>')


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


# ---------- ciudades: capitales de provincia y municipios de más de 1.000 habitantes ----------
CAPITALES = {'01059', '02003', '03014', '04013', '05019', '06015', '07040', '08019', '09059', '10037', '11012', '12040', '13034', '14021',
             '15030', '16078', '17079', '18087', '19130', '20069', '21041', '22125', '23050', '24089', '25120', '26089', '27028', '28079',
             '29067', '30030', '31201', '32054', '33044', '34120', '35016', '36038', '37274', '38038', '39075', '40194', '41091', '42173',
             '43148', '44216', '45168', '46250', '47186', '48020', '49275', '50297'}   # Ceuta y Melilla ya tienen su página de comunidad
UMBRAL = 1000
GRANDE = 50000   # el índice general solo lista capitales y municipios de más de 50.000; el resto, en su provincia


def nombre_visible(t):
    """'Alfàs del Pi, l'' -> 'L'Alfàs del Pi'; 'Pinós, el/Pinoso' -> 'El Pinós/Pinoso'."""
    m = re.fullmatch(r"(.+?), (l'|el|la|els|les|es|sa|ses|los|las|o|a|os|as)(/.*)?", t, re.I)
    if not m:
        return t
    art = m.group(2)[0].upper() + m.group(2)[1:]
    sep = '' if art.endswith("'") else ' '
    return f'{art}{sep}{m.group(1)}{m.group(3) or ""}'


T.MUN['municipio'] = T.MUN.municipio.map(nombre_visible)


def _ciudades():
    m = T.MUN[((T.MUN.poblacion >= UMBRAL) | T.MUN.mun_code.isin(CAPITALES)) & ~T.MUN.prov.isin(['51', '52'])]
    return {r.mun_code: ruta_municipio(r.prov, r.municipio) for r in m.itertuples()}


CIUDADES = _ciudades()
BARRIOS = {c: TB.barrios(c) for c in sorted(set(TB.SB.mun_code)) if c in CIUDADES} if TB.SB is not None else {}


def distrito_seccion(tc):
    return f'distrito {int(tc[5:7])}, sección {int(tc[7:10])}'


def pagina_ciudad(cod):
    m = T.MUN[T.MUN.mun_code == cod]
    fila = m.iloc[0]
    nombre, p = fila.municipio, fila.prov
    ccaa = PROV_CCAA[p]
    ruta = CIUDADES[cod]
    nivel = ruta.count('/')
    global RAIZ_REL
    RAIZ_REL = '../' * nivel   # los bloques de abajo se escriben antes que la cabecera
    sec = T.SEC[T.SEC.mun_code == cod]
    serie = T.serie(m)
    r = serie[T.ULTIMA]
    g = T.ganador(r)
    prov_df = T.MUN[T.MUN.prov == p]
    rp = T.resultado(prov_df, T.ULTIMA)
    uni = len(CCAA[ccaa][2]) == 1
    nprov = CCAA[ccaa][0] if uni else PROV_NOMBRE[p]
    b_sec = bloque_secciones(nombre, sec)
    b_renta = bloque_renta(nombre, f'en {nombre}', sec, ciudad=True)
    b_censo, q_censo = bloque_censo(nombre, cod)
    titulo = (f'Elecciones 29N 2026 en {nombre}: {"censo electoral y " if q_censo else ""}'
              + ('cómo votó cada barrio' if b_sec else 'resultados desde 1977'))
    desc = ((f'Censo electoral para el 29N en {nombre}: {num(censo_29n(cod)[2])} electores. ' if q_censo else '')
            + f'Así votó en las generales de 1977 a 2023: en 2023, {T.NOMBRE[g]} {pct(r["pct"][g])} y participación del {pct(r["part"])}. '
            + (f'Voto por renta de sus {num(len(sec))} secciones censales y municipales frente a generales.' if b_renta else
               (f'Resultados de sus {num(len(sec))} secciones censales y municipales frente a generales.' if len(sec) > 1 else
                'Resultados de la serie completa y municipales frente a generales.')))
    about = lugar(nombre, lugar(nprov, ESPANA))
    about['@type'] = 'City'
    faq_html, faq_ld = faq([q_censo]) if q_censo else ('', None)
    h = [cabeza(titulo, desc, ruta, [ld_pagina(titulo, desc, ruta, about), faq_ld] if faq_ld else ld_pagina(titulo, desc, ruta, about), nivel, nombre)]
    raiz = RAIZ_REL
    h.append(migas_html([(raiz, 'Inicio'), (raiz + 'municipio/', 'Municipios'), (raiz + f'municipio/{PROV_SLUG[p]}/', PROV_NOMBRE[p])]))
    h.append(f'<p class="kicker">{"Capital de provincia" if cod in CAPITALES else "Municipio"} · Elecciones generales 1977-2023</p>'
             f'<h1 data-miga="{escape(nombre)}">Elecciones en {escape(nombre)}</h1>')
    h.append(f'<p class="subtitulo">{"Censo para el 29N, r" if b_censo else "R"}esultados por {"barrio y " if b_sec else ""}sección censal, {"voto por renta, " if b_renta else ""}municipales frente a generales y las 16 generales desde 1977</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(f'<p class="resumen">{tipo("Dato")}{entradilla(nombre, f"en {nombre}", r, serie, ccaa)}</p>')
    comp = 'más' if r['part'] > rp['part'] + 0.005 else ('menos' if r['part'] < rp['part'] - 0.005 else 'casi lo mismo')
    conjunto = CCAA[ccaa][1][3:] if uni else f'la provincia de {nprov}'
    h.append(p_('Dato', f'{escape(nombre)} votó {comp} que el conjunto de {escape(conjunto)} ({pct(rp["part"])}). '
                f'Tiene {num(fila.poblacion)} habitantes y {num(len(sec)) + " secciones censales" if len(sec) > 1 else "una sola sección censal"}.'))
    h.append(f'<p><a class="vermapa" href="{raiz}?m={cod}">Ver {escape(nombre)} {"calle a calle " if b_sec else ""}en el mapa por sección censal</a></p>')
    h.append(bloque_resultado(nombre, r))
    h.append(b_censo)
    h.append(b_sec)
    h.append(bloque_barrios(cod, nombre, BARRIOS.get(cod, [])))
    h.append(b_renta)
    h.append(bloque_ocupacion(nombre, cod, p, PROV_NOMBRE[p], RANKING_OCUP))
    h.append(bloque_municipales(nombre, m, r))
    h.append(bloque_serie(nombre, serie))
    h.append(faq_html)
    rel = actualidad_de([s for s, (c, _) in ACTUALIDAD_MUNICIPIO.items() if c == cod], raiz)
    rel += [(f'{raiz}atlas/{atlas.ruta_pieza(q).replace("index.html", "")}', atlas.titular(q), 'Atlas') for q in ATLAS if cod in q['_muns']]
    h.append(bloque_relacionadas([], nivel, rel) if rel else '')
    pob = T.MUN.set_index('mun_code').poblacion
    otras = sorted((c for c in CIUDADES if c[:2] == p and c != cod), key=lambda c: -pob[c])[:10]   # los diez más poblados; el resto, en la provincia
    otras.sort(key=lambda c: slug(T.MUN.loc[T.MUN.mun_code == c, 'municipio'].iloc[0]))
    li = [f'<li><a href="{raiz}{ruta_provincia(p)}">Elecciones en {"la provincia de " if not uni else ""}{escape(nprov)}</a></li>']
    if not uni:
        li.append(f'<li><a href="{raiz}elecciones/{ccaa}/">Elecciones en {escape(CCAA[ccaa][0])}</a></li>')
    li.append(f'<li><a href="{raiz}municipio/{PROV_SLUG[p]}/">Todos los municipios de {escape(PROV_NOMBRE[p])} con página propia</a></li>')
    li += [f'<li><a href="{raiz}{CIUDADES[c]}">Elecciones en {escape(T.MUN.loc[T.MUN.mun_code == c, "municipio"].iloc[0])}</a></li>' for c in otras]
    li += [f'<li><a href="{raiz}elecciones/voto-y-renta-por-barrios/">Voto y renta por barrios en toda España</a></li>',
           f'<li><a href="{raiz}elecciones/mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li>']
    h.append('<h2>Más datos</h2><ul>' + ''.join(li) + '</ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


# ---------- fichas de barrio: /municipio/<provincia>/<municipio>/<barrio>/ ----------
def ordinal(n):
    return f'{n}.º'


def puesto(valor, todos, alto=True):
    """Puesto de `valor` entre `todos` (1 = el más alto si alto)."""
    vs = sorted((v for v in todos if v is not None), reverse=alto)
    return vs.index(valor) + 1 if valor in vs else None


def art_partido(c, ccaa):
    reg = REGIONAL.get(ccaa, {})
    n = reg.get(c, T.NOMBRE[c].split(' /')[0])
    return ('el ' if c in ('PP', 'PSOE', 'PNV', 'BNG') or n == 'PSC' else '') + n


def cap(t):
    return t[0].upper() + t[1:]


def con_de(t):
    return 'del ' + t[3:] if t.startswith('el ') else 'de ' + t


def puntos(x):
    return f'{abs(x) * 100:.1f}'.replace('.', ',')


# Ilustración de cabecera de las fichas de barrio, una por ciudad (collages con IA de Nacho); el resto, la genérica
FOTOS_BARRIO = {
    '28079': ('barrios-madrid.jpg', 'Bloques de ladrillo de un barrio obrero frente a fachadas señoriales de Madrid, con una urna en medio y el plano de calles al fondo: un collage.'),
    '08019': ('barrios-barcelona.jpg', 'La cuadrícula del Eixample vista desde arriba, entre torres de pisos y casas con jardín, con sobres de votación volando: un collage.'),
    '46250': ('barrios-valencia.jpg', 'La catedral y los tejados de Ciutat Vella, fincas de la periferia y la huerta, con una urna en primer plano: un collage.'),
    '41091': ('barrios-sevilla.jpg', 'Una calle encalada del centro de Sevilla frente a bloques de pisos junto al Guadalquivir, con una urna: un collage.'),
    '29067': ('barrios-malaga.jpg', 'Edificios del centro de Málaga, torres de la costa y el puerto al fondo, con una urna en primer plano: un collage.'),
}
FOTO_BARRIO_GENERICA = ('barrios-generica.jpg', 'Un bloque de pisos, casas bajas y un edificio antiguo cosidos como un mosaico urbano, con una urna en el centro: un collage.')


def foto_barrio(cod, raiz):
    f, alt = FOTOS_BARRIO.get(cod, FOTO_BARRIO_GENERICA)   # cod None: la genérica (portada de barrios)
    return (f'<figure class="foto"><img src="{raiz}img/elecciones/{f}" alt="{escape(alt)}" width="1280" height="720" loading="eager">'
            f'<figcaption>{escape(alt)} Ilustración generada con IA para Mapa Electoral. <a href="{raiz}atlas/politica-editorial/#ia">Uso de IA</a>.</figcaption></figure>')


def intensidad(v):
    return 0.45 if v < 0.30 else 0.65 if v < 0.40 else 0.85 if v < 0.50 else 1


def ruta_barrio(cod, b):
    return CIUDADES[cod] + b['slug'] + '/'


def dato_demo(v, fmt):
    return '—' if v is None or v != v else fmt(v)


def pagina_barrio(cod, b, todos):
    m = T.MUN[T.MUN.mun_code == cod]
    ciudad, p = m.iloc[0].municipio, m.iloc[0].prov
    ccaa = PROV_CCAA[p]
    ruta = ruta_barrio(cod, b)
    nivel = ruta.count('/')
    global RAIZ_REL
    RAIZ_REL = '../' * nivel
    raiz = RAIZ_REL
    nombre, r, dm, cods = b['nombre'], b['r'], b['demo'], b['secciones']
    fichas = [x for x in todos if x['ficha']]
    n = len(fichas)
    tipo_b = 'barrio' if b['nivel'] == 10 else 'distrito'
    tipos = 'barrios' if b['nivel'] == 10 else 'distritos'
    rc = TB.resultado(TB.LARGO[(TB.LARGO.eleccion == T.ULTIMA) & TB.LARGO.mun_code.eq(cod)])
    dc = TB.demografia(TB.LARGO[(TB.LARGO.eleccion == T.ULTIMA) & TB.LARGO.mun_code.eq(cod)].tract_code)
    g = T.ganador(r)
    resto = sorted((c for c in T.FAM if c not in (g, 'OTROS') and r['pct'][c]), key=lambda c: -r['pct'][c])
    seg = resto[0]
    gc = T.ganador(rc)
    nom_g, nom_s = art_partido(g, ccaa), art_partido(seg, ccaa)
    zona = ZONAS.get(b['distrito'])
    dist = (zona[0].format(ciudad=ciudad) if zona else f', en el distrito de {b["distrito"]}') if b['distrito'] and slug(b['distrito']) != slug(nombre) else ''
    p_part = puesto(r['part'], [x['r']['part'] for x in fichas])
    p_renta = puesto(dm['renta_uc'], [x['demo']['renta_uc'] for x in fichas]) if dm['renta_uc'] else None
    # el partido que más se separa de la ciudad
    dif = {c: (r['pct'][c] or 0) - (rc['pct'][c] or 0) for c in T.FAM if c != 'OTROS'}
    lejos = max(dif, key=lambda c: abs(dif[c]))

    titulo = f'Elecciones en {nombre} ({ciudad}): así vota el {tipo_b}, sección a sección'
    desc = (f'{cap(nombre)}{dist} ({ciudad}): en las generales de 2023, {nom_g} ganó con el {pct(r["pct"][g])} y votó el {pct(r["part"])} del censo. '
            f'Renta, edad, población extranjera y voto de sus {num(len(cods))} secciones censales desde 2004.')
    about = {'@type': 'Place', 'name': f'{nombre} ({ciudad})', 'containedInPlace': {'@type': 'City', 'name': ciudad, 'url': BASE + CIUDADES[cod],
             'containedInPlace': lugar(PROV_NOMBRE[p], ESPANA)}}
    ld = ld_pagina(titulo, desc, ruta, about)
    ld['datePublished'] = BARRIOS_PUBLICADO
    ld['dateModified'] = max(ACTUALIZADO, BARRIOS_PUBLICADO)
    pasos = [(raiz, 'Inicio'), (raiz + 'municipio/', 'Municipios'), (raiz + f'municipio/{PROV_SLUG[p]}/', PROV_NOMBRE[p]), (raiz + CIUDADES[cod], ciudad)]
    ld['primaryImageOfPage'] = BASE + 'img/elecciones/' + FOTOS_BARRIO.get(cod, FOTO_BARRIO_GENERICA)[0]
    h = [cabeza(titulo, desc, ruta, ld, nivel, nombre, imagen='img/elecciones/' + FOTOS_BARRIO.get(cod, FOTO_BARRIO_GENERICA)[0])]   # las migas de pan en JSON-LD las añade esquema.py
    h.append(migas_html(pasos))
    antetitulo = (f'Pedanía de {ciudad}' if zona and zona[1] == 'pedanía' else
                  f'{tipo_b.capitalize()} de {ciudad}' + (" · " + zona[1] if zona else dist.replace(", en el distrito de", " · distrito")))
    h.append(f'<p class="kicker">{escape(antetitulo)} · Generales 2004-2023</p>'
             f'<h1 data-miga="{escape(nombre)}">Elecciones en {escape(nombre)}</h1>')
    h.append(f'<p class="subtitulo">Cómo vota este {tipo_b} de {escape(ciudad)}, quién vive en él y en qué se separa del resto de la ciudad</p>')
    act = max(ACTUALIZADO, BARRIOS_PUBLICADO)
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{act}">{fecha(act)}</time></p>')
    h.append(foto_barrio(cod, raiz))

    # entradilla
    comp_part = r['part'] - rc['part']
    t_part = (f'{puntos(comp_part)} puntos {"más" if comp_part > 0 else "menos"} que el conjunto de {escape(ciudad)} ({pct(rc["part"])})'
              if abs(comp_part) >= 0.005 else f'casi lo mismo que el conjunto de {escape(ciudad)} ({pct(rc["part"])})')
    lead = (f'En {escape(nombre)}{escape(dist)}, {nom_g} fue la fuerza más votada en las elecciones generales del 23 de julio de 2023, con el {pct(r["pct"][g])} del voto válido, '
            f'por delante {con_de(nom_s)} ({pct(r["pct"][seg])}). Votó el {pct(r["part"])} de sus {num(r["censo"])} electores, {t_part}')
    lead += (f': es el {ordinal(p_part)} de los {num(n)} {tipos} de la ciudad con más participación.' if p_part and n >= 5 else '.')
    h.append(f'<p class="resumen">{tipo("Dato")}{lead}</p>')
    if g != gc:
        h.append(p_('Dato', f'En el conjunto de la ciudad ganó {art_partido(gc, ccaa)} ({pct(rc["pct"][gc])}); aquí, {nom_g} le saca a {art_partido(gc, ccaa) if gc != seg else "ese partido"} '
                    f'{puntos(r["pct"][g] - r["pct"][gc])} puntos.'))
    if abs(dif[lejos]) >= 0.03:
        h.append(p_('Dato', f'Donde más se separa {escape(nombre)} del resto de {escape(ciudad)} es en el voto {con_de(art_partido(lejos, ccaa))}: '
                    f'{pct(r["pct"][lejos])}, frente al {pct(rc["pct"][lejos])} de la ciudad, {puntos(dif[lejos])} puntos {"más" if dif[lejos] > 0 else "menos"}.'))
    # quién vive
    frases = [f'Viven en {escape(nombre)} {num(dm["poblacion"])} personas (padrón de 2023)']
    if dm['edad_media']:
        frases.append(f'con una edad media de {dm["edad_media"]:.1f} años ({dc["edad_media"]:.1f} en {escape(ciudad)})'.replace('.', ','))
    txt = ', '.join(frases) + '. '
    if dm['extranjeros'] is not None:
        txt += f'El {pct(dm["extranjeros"])} tiene nacionalidad extranjera, frente al {pct(dc["extranjeros"])} de la ciudad. '
    if dm['estudios_sup_2021'] is not None:
        txt += f'Según el censo de 2021, el {pct(dm["estudios_sup_2021"])} de los adultos tiene estudios superiores ({pct(dc["estudios_sup_2021"])} en la ciudad)'
        txt += (f' y la tasa de paro era del {pct(dm["paro_2021"])} ({pct(dc["paro_2021"])}).' if dm['paro_2021'] is not None else '.')
    h.append(p_('Dato', txt))
    if dm['renta_uc']:
        h.append(p_('Dato', f'La renta neta media por unidad de consumo es de {euros(dm["renta_uc"])} al año ({euros(dc["renta_uc"])} en {escape(ciudad)})'
                    + (f': el {ordinal(p_renta)} {tipo_b} con más renta de los {num(n)} de la ciudad' if p_renta and n >= 5 else '')
                    + (f'. El {pct(dm["pobreza"])} de la población vive por debajo del umbral de pobreza relativa (menos del 60 % de la renta mediana).' if dm['pobreza'] is not None else '.')))
    h.append(f'<p><a class="vermapa" href="{raiz}?m={cod}">Ver {escape(nombre)} calle a calle en el mapa de {escape(ciudad)}</a></p>')

    # mapa
    secs = TB.secciones(cods)
    col = {s['cod']: (T.COLOR[s['gana']], intensidad(s['pct'])) for s in secs}
    svg = TB.mapa(cod, cods, col, f'Partido más votado en cada sección censal de {nombre} en 2023')
    if svg:
        cuenta = {}
        for s in secs:
            cuenta[s['gana']] = cuenta.get(s['gana'], 0) + 1
        reparto = '; '.join(f'{art_partido(c, ccaa)}, en {num(k)}' for c, k in sorted(cuenta.items(), key=lambda x: -x[1]))
        h.append('<h2>Sección a sección</h2>'
                 + p_('Dato', f'{escape(cap(nombre))} tiene {num(len(cods))} secciones censales, la unidad más pequeña con resultados electorales (entre 500 y 2.500 electores cada una). '
                      f'En 2023 ganó {reparto}.')
                 + figura(svg, f'Partido más votado en cada sección censal de {escape(nombre)}, generales de 2023; el color es más intenso cuanto mayor es su voto (menos del 30 %, 30-40 %, 40-50 %, 50 % o más). En gris, las secciones vecinas. '
                          'Límites de las secciones: INE; del barrio: '
                          + (escape(TB.FUENTES[cod]['fuente']) if cod in TB.FUENTES else '© colaboradores de OpenStreetMap (ODbL)') + '.', leyenda_partidos(cuenta)))
    con_part = [s for s in secs if s['part'] is not None and s['censo'] >= 200]
    if len(con_part) >= 4:
        a, z = max(con_part, key=lambda s: s['part']), min(con_part, key=lambda s: s['part'])
        frase = (f'Dentro del {tipo_b} también hay distancia: en la sección que más votó ({distrito_seccion(a["cod"])}) participó el {pct(a["part"])}, '
                 f'y en la que menos ({distrito_seccion(z["cod"])}), el {pct(z["part"])}')
        if a['renta'] and z['renta'] and a['renta'] == a['renta'] and z['renta'] == z['renta']:
            frase += f'. La primera tiene una renta de {euros(a["renta"])} por unidad de consumo; la segunda, de {euros(z["renta"])}'
        h.append(p_('Dato', frase + '.'))
    filas = [[distrito_seccion(s['cod']).capitalize(), num(s['censo']), pct(s['part']),
              f'<span style="color:{T.COLOR[s["gana"]]}">■</span> {escape(T.NOMBRE[s["gana"]])} ({pct(s["pct"])})',
              euros(s['renta']) if s['renta'] and s['renta'] == s['renta'] else '—'] for s in secs]
    t_sec = tabla(f'Secciones censales de {escape(nombre)}: generales de 2023 y renta por unidad de consumo (INE, 2023)',
                  ['Sección', 'Censo', 'Participación', 'Más votado', 'Renta'], filas)
    h.append(t_sec if len(filas) <= 12 else f'<details><summary>Las {num(len(filas))} secciones de {escape(nombre)}, una a una</summary>{t_sec}</details>')

    # resultado
    filas = [[escape(T.NOMBRE[c]), pct(r['pct'][c]), num(r['votos'][c]), pct(rc['pct'][c])]
             for c in sorted(T.FAM, key=lambda c: -(r['pct'][c] or 0)) if (r['pct'][c] or 0) >= 0.005 or c == 'OTROS']
    h.append('<h2>Resultado de las generales de 2023</h2>'
             + p_('Dato', f'Voto por partido sobre voto válido (candidaturas más blancos) en las {num(len(cods))} secciones de {escape(nombre)}. '
                  f'La línea discontinua marca el resultado del conjunto de {escape(ciudad)}.')
             + f'<figure>{barras(r, rc)}<figcaption>Elecciones generales del 23 de julio de 2023, sin voto desde el extranjero (CERA). Fuente: Ministerio del Interior.</figcaption></figure>'
             + tabla(f'Voto por partido en {escape(nombre)}, 23J 2023', ['Partido', 'Voto', 'Votos', escape(ciudad)], filas))

    # serie desde 2004
    s = TB.serie(cods)
    ys = [y for y in TB.ELEC if s[y]]
    if len(ys) >= 4:
        fams = [c for c in T.FAM if c != 'OTROS' and max((s[y]['pct'][c] or 0) for y in ys) >= 0.05]
        filas = [[T.etiqueta(y), pct(s[y]['part']), escape(T.nombre_familia(T.ganador(s[y]), y))] + [pct(s[y]['pct'][c]) if s[y]['pct'][c] else '—' for c in fams] for y in ys]
        ganadores = [T.ganador(s[y]) for y in ys]
        cambios = sum(1 for i in range(1, len(ganadores)) if ganadores[i] != ganadores[i - 1])
        if cambios == 0:
            t = f'{art_partido(ganadores[0], ccaa)[0].upper() + art_partido(ganadores[0], ccaa)[1:]} ha ganado en {escape(nombre)} todas las generales desde {T.etiqueta(ys[0])}.'
        else:
            veces = {c: ganadores.count(c) for c in set(ganadores)}
            t = (f'Desde {T.etiqueta(ys[0])}, el {tipo_b} ha cambiado de partido más votado {cambios} {"vez" if cambios == 1 else "veces"}: '
                 + ', '.join(f'{art_partido(c, ccaa)} ganó en {k}' for c, k in sorted(veces.items(), key=lambda x: -x[1])) + f' de {len(ys)} elecciones.')
        dp = s[ys[-1]]['part'] - s[ys[0]]['part']
        t += f' La participación ha pasado del {pct(s[ys[0]]["part"])} en {T.etiqueta(ys[0])} al {pct(s[ys[-1]]["part"])} en 2023.'
        falta = [T.etiqueta(y) for y in TB.ELEC if not s[y]]
        h.append('<h2>De 2004 a 2023</h2>' + p_('Dato', t)
                 + tabla(f'Participación, partido más votado y voto por partido en {escape(nombre)}, generales de 2004 a 2023',
                         ['Elección', 'Participación', 'Más votado'] + [escape(T.NOMBRE[c]) for c in fams], filas)
                 + '<p class="leyenda">Con las secciones censales de 2023: los resultados de cada elección son los de las secciones que ya existían con el mismo código. '
                 + (f'No se muestran {", ".join(falta)} porque entonces faltaba más del 20 % del censo actual (secciones creadas o renumeradas después). ' if falta else '')
                 + 'Las familias agrupan a cada partido con sus antecesores y coaliciones (Podemos, IU y Sumar; Junts y CiU).</p>')

    # quién vive: tabla
    filas = [['Habitantes (2023)', num(dm['poblacion']), num(dc['poblacion'])],
             ['Edad media', dato_demo(dm['edad_media'], lambda v: f'{v:.1f}'.replace('.', ',')), dato_demo(dc['edad_media'], lambda v: f'{v:.1f}'.replace('.', ','))],
             ['Menores de 18 años', dato_demo(dm['menores18'], pct), dato_demo(dc['menores18'], pct)],
             ['65 años o más', dato_demo(dm['mayores65'], pct), dato_demo(dc['mayores65'], pct)],
             ['Nacionalidad extranjera', dato_demo(dm['extranjeros'], pct), dato_demo(dc['extranjeros'], pct)],
             ['Nacidos fuera de España (2021)', dato_demo(dm['nacidos_fuera_2021'], pct), dato_demo(dc['nacidos_fuera_2021'], pct)],
             ['Con estudios superiores (2021)', dato_demo(dm['estudios_sup_2021'], pct), dato_demo(dc['estudios_sup_2021'], pct)],
             ['Tasa de paro (2021)', dato_demo(dm['paro_2021'], pct), dato_demo(dc['paro_2021'], pct)],
             ['Renta neta por unidad de consumo', dato_demo(dm['renta_uc'], euros), dato_demo(dc['renta_uc'], euros)],
             ['Renta neta por habitante', dato_demo(dm['renta_pc'], euros), dato_demo(dc['renta_pc'], euros)],
             ['Bajo el umbral de pobreza relativa', dato_demo(dm['pobreza'], pct), dato_demo(dc['pobreza'], pct)]]
    h.append('<h2>Quién vive en el ' + tipo_b + '</h2>'
             + tabla(f'Población, edad, origen, estudios y renta de {escape(nombre)} y de {escape(ciudad)}', ['', escape(nombre), escape(ciudad)], filas)
             + '<p class="leyenda">Medias de las secciones del barrio ponderadas por su población. Padrón y Atlas de Distribución de Renta de los Hogares del INE (2023); '
               'estudios, paro y lugar de nacimiento, del censo de población de 2021. La relación entre estas cifras y el voto es entre barrios, no entre personas.</p>')

    # otros barrios
    mismos = [x for x in fichas if x is not b and b['distrito'] and x['distrito'] == b['distrito']]
    li = [f'<li><a href="{raiz}{ruta_barrio(cod, x)}">{escape(x["nombre"])}</a>: {art_partido(T.ganador(x["r"]), ccaa)}, participación del {pct(x["r"]["part"])}</li>' for x in mismos]
    if li:
        h.append(f'<h2>{escape(zona[2].format(ciudad=ciudad)) if zona else "Otros barrios del distrito de " + escape(b["distrito"])}</h2><ul>' + ''.join(li) + '</ul>')
    h.append(f'<h2>Más datos</h2><ul><li><a href="{raiz}{CIUDADES[cod]}#barrios">Todos los {tipos} de {escape(ciudad)}</a></li>'
             f'<li><a href="{raiz}municipio/barrios/">Barrios de las grandes ciudades de España</a></li>'
             f'<li><a href="{raiz}{CIUDADES[cod]}">Elecciones en {escape(ciudad)}, desde 1977</a></li>'
             f'<li><a href="{raiz}elecciones/participacion-electoral-por-barrio/">Participación electoral por barrio en toda España</a></li>'
             f'<li><a href="{raiz}elecciones/voto-y-renta-por-barrios/">Voto y renta por barrios en toda España</a></li></ul>')
    h.append(bloque_metodo_barrio(tipo_b, cod))
    h.append(PIE)
    return ruta, ''.join(h)


# agrupaciones que no son distritos (Murcia: casco urbano y pedanías): frase, antetítulo y título de «otros barrios»
ZONAS = {'Pedanías': (', una de las pedanías de {ciudad}', 'pedanía', 'Otras pedanías de {ciudad}'),
         'Casco urbano': (', en el casco urbano', 'casco urbano', 'Otros barrios del casco urbano de {ciudad}')}


def bloque_metodo_barrio(tipo_b, cod=None):
    if cod in TB.FUENTES:
        f = TB.FUENTES[cod]
        limites = (f'Los límites de los barrios de {escape(_nom(cod))} salen de <a href="{escape(f["web"])}">{escape(f["fuente"])}</a>, '
                   'porque OpenStreetMap no tiene los barrios de esta ciudad. ')
    else:
        limites = ('Los límites de barrios y distritos son los de OpenStreetMap (© colaboradores de OpenStreetMap, '
                   '<a href="https://opendatacommons.org/licenses/odbl/">licencia ODbL</a>), que en la mayoría de ciudades copian la división oficial del ayuntamiento'
                   + (f'; en {", ".join(escape(_nom(c)) for c in sorted(TB.FUENTES, key=_nom))}, que no los tienen en OpenStreetMap, se usan los del ayuntamiento '
                      'o la mejor recopilación disponible (cada ficha lo indica)' if cod is None and TB.FUENTES else '') + '. ')
    return (f'<h2>Método y fuentes</h2><dl class="ficha">'
            f'<dt>Qué es el {tipo_b}</dt><dd>{limites}'
            'Cada sección censal del INE se asigna al barrio con el que comparte más superficie; las que caen menos de la mitad dentro de un barrio no se asignan. '
            'Como las secciones no siempre siguen los límites de los barrios, alguna manzana del borde puede quedar en el barrio vecino.</dd>'
            '<dt>Datos</dt><dd>Resultados oficiales por mesa del Ministerio del Interior (Infoelectoral) agregados por sección censal, sin el voto de los residentes en el extranjero (CERA). '
            'Renta y población: Atlas de Distribución de Renta de los Hogares y padrón del INE (2023); estudios, paro y lugar de nacimiento: censo de población de 2021.</dd>'
            '<dt>Cómo se calcula</dt><dd>Porcentajes sobre voto válido (candidaturas más votos en blanco), sumando votos de las secciones, no promediando porcentajes. '
            f'Participación: votantes entre censo. Agrupación de partidos y límites: <a href="{RAIZ_REL}generales-2026/metodologia.html">metodología del mapa</a>.</dd>'
            f'<dt>Datos abiertos</dt><dd>Las cifras salen de las <a href="{RAIZ_REL}generales-2026/metodologia.html#descargas">descargas del mapa</a> (CSV, licencia <a href="{LICENCIA}">CC BY 4.0</a>); '
            f'la relación entre secciones y barrios está en <a href="{atlas.REPO}/blob/main/data/barrios/secciones_barrio.csv">data/barrios/secciones_barrio.csv</a>.</dd>'
            f'<dt>Autoría y revisión</dt><dd><a href="{RAIZ_REL}sobre-mi.html">{esquema.FIRMA}</a>. Publicado el {fecha(BARRIOS_PUBLICADO)}; actualizado el {fecha(max(ACTUALIZADO, BARRIOS_PUBLICADO))}. '
            f'<a href="{RAIZ_REL}atlas/politica-editorial/">Política editorial</a> · <a href="{RAIZ_REL}atlas/correcciones/">Correcciones</a></dd></dl>')


def bloque_barrios(cod, nombre, todos):
    """Bloque de la ficha del municipio con la tabla de sus barrios y el enlace a cada ficha."""
    fichas = [b for b in todos if b['ficha']]
    if len(fichas) < 2:
        return ''
    tipos = 'barrios' if fichas[0]['nivel'] == 10 else 'distritos'
    ccaa = PROV_CCAA[cod[:2]]
    con_d = any(b['distrito'] for b in fichas)
    orden = sorted(fichas, key=lambda b: (slug(b['distrito'] or ''), slug(b['nombre'])))
    filas = []
    for b in orden:
        g = T.ganador(b['r'])
        filas.append([f'<a href="{b["slug"]}/">{escape(b["nombre"])}</a>'] + ([escape(b['distrito'] or '—')] if con_d else [])
                     + [pct(b['r']['part']), f'<span style="color:{T.COLOR[g]}">■</span> {escape(T.NOMBRE[g])} ({pct(b["r"]["pct"][g])})',
                        euros(b['demo']['renta_uc']) if b['demo']['renta_uc'] else '—'])
    part = sorted(fichas, key=lambda b: -b['r']['part'])
    sin = [b['nombre'] for b in todos if not b['ficha']]
    txt = (f'{escape(nombre)} tiene ficha propia para {num(len(fichas))} {tipos}, con el voto de cada sección censal, la renta y quién vive en ellos. '
           f'En 2023 el que más votó fue <a href="{part[0]["slug"]}/">{escape(part[0]["nombre"])}</a> ({pct(part[0]["r"]["part"])}) y el que menos, '
           f'<a href="{part[-1]["slug"]}/">{escape(part[-1]["nombre"])}</a> ({pct(part[-1]["r"]["part"])}).')
    return (f'<h2 id="barrios">{tipos.capitalize()} de {escape(nombre)}</h2>' + p_('Dato', txt)
            + tabla(f'Generales de 2023 en cada {tipos[:-1]} de {escape(nombre)}', ['Barrio' if tipos == 'barrios' else 'Distrito'] + (['Distrito'] if con_d else [])
                    + ['Participación', 'Más votado', 'Renta por u. c.'], filas, num_desde=2 if con_d else 1)
            + (f'<p class="leyenda">Sin ficha propia, por tener menos de {TB.MINIMO} secciones censales: {escape(", ".join(sorted(sin)))}.</p>' if sin else ''))


CENSO = pd.read_csv(ROOT / 'data' / 'censo' / 'censo_municipios_2023_2026.csv', dtype={'mun_code': str}).set_index('mun_code')
CENSO_INE = 'https://www.ine.es/oficina_censo/elecgen2026/Elecgral_2026_cc_tab4.xlsx'


def censo_29n(cods):
    """Electores para el 29N (residentes, CERA, total) y total de 2023 de uno o varios municipios, del censo de consulta del INE."""
    c = CENSO.loc[CENSO.index.intersection([cods] if isinstance(cods, str) else list(cods))]
    if c.empty:
        return None
    t23 = None if c.cer_2023.isna().all() else int(c.cer_2023.sum() + c.cera_2023.sum())
    return int(c.cer_2026.sum()), int(c.cera_2026.sum()), int(c.cer_2026.sum() + c.cera_2026.sum()), t23


def variacion(total, t23):
    v = (total - t23) / t23 * 100
    return f'{f"{v:+.{2 if abs(v) < 0.1 else 1}f}".replace(".", ",").replace("-", "−")} %'


def bloque_censo(nombre, cods, ambito='el municipio', provincias=(), en=None):
    """Bloque «Censo electoral para el 29N» y su pregunta frecuente. provincias: [(código, enlace)] para la tabla de una comunidad."""
    c = censo_29n(cods)
    if not c:
        return '', None
    cer, cera, total, t23 = c
    en = en or f'en {nombre}'
    de = re.sub(r'^de el ', 'del ', 'de ' + en[3:])
    en_el = 'en él' if ambito.startswith('el ') else 'en ella'
    txt = (f'Para las generales del 29 de noviembre de 2026, el censo electoral {escape(de)} es de {num(total)} electores: '
           f'{num(cer)} viven en {ambito} y {num(cera)} están inscritos {en_el} pero viven en el extranjero (CERA).')
    if t23:
        d = total - t23
        txt += (f' En las generales de 2023 eran {num(t23)}, así que el censo tiene {num(abs(d))} electores {"más" if d >= 0 else "menos"} ({variacion(total, t23)}).'
                if d else f' En las generales de 2023 eran los mismos, {num(t23)}.')
    tab = ''
    if provincias:
        filas = []
        for pc, enlace in provincias:
            cp = censo_29n(CENSO.index[CENSO.index.str[:2] == pc])
            filas.append([enlace, num(cp[0]), num(cp[1]), num(cp[2]), variacion(cp[2], cp[3]) if cp[3] else '—'])
        tab = tabla(f'Censo electoral de las generales de 2026 {escape(en)}, por provincia', ['Provincia', 'Residentes en España', 'En el extranjero', 'Total', 'Cambio desde 2023'], filas)
    html_ = ('<h2 id="censo">Censo electoral para el 29N</h2>' + p_('Dato', txt) + tab
             + f'<p class="leyenda">Fuente: INE, Oficina del Censo Electoral, <a href="{CENSO_INE}">censo de consulta de las generales de 2026</a> y el de 2023, por municipio. '
               'Es el censo que se expone para consultas y reclamaciones antes de la votación; el definitivo puede variar ligeramente. '
               'Los electores que viven en el extranjero votan desde allí y su voto se suma al de la provincia, no al resultado de cada municipio.</p>')
    q = (f'¿Cuántos electores hay {en} para las elecciones del 29N?',
         f'{num(total)}, según el censo de consulta del INE: {num(cer)} residentes en {ambito} y {num(cera)} residentes en el extranjero.')
    return html_, q


OCUP = pd.read_csv(ROOT / 'data' / 'censo' / 'censo_municipios.csv', dtype={'mun_code': str}).query('anyo == 2023').set_index('mun_code')
OCUP_INE = 'https://www.ine.es/jaxiT3/Tabla.htm?t=70004'
GRUPOS = [('ocup_alta', 'Alta cualificación', 'directivos, profesionales y técnicos'),
          ('ocup_media', 'Cualificación media', 'administrativos, comercio, hostelería, agricultura, oficios y operadores'),
          ('ocup_elemental', 'Elementales', 'peones, limpieza, reparto y otras tareas sin cualificación')]


def reparto_ocup(df):
    """Reparto de los ocupados con ocupación conocida entre los tres grandes grupos del INE (fracciones)."""
    t = df[[g for g, _, _ in GRUPOS]].sum()
    return t / t.sum()


OCUP_ESP = reparto_ocup(OCUP)


def disimilitud(a, b):
    """Índice de disimilitud: parte de los ocupados que tendría que cambiar de grupo para igualar los dos repartos."""
    return float((a - b).abs().sum() / 2)


_d = {c: disimilitud(reparto_ocup(OCUP.loc[[c]]), OCUP_ESP) for c in CIUDADES if c in OCUP.index and pd.notna(OCUP.loc[c, 'ocup_alta'])}
RANKING_OCUP = {c: i + 1 for i, c in enumerate(sorted(_d, key=_d.get))}   # 1 = mezcla de ocupaciones más parecida a la de España


def bloque_ocupacion(nombre, cod, p, nprov, ranking):
    if cod not in OCUP.index or pd.isna(OCUP.loc[cod, 'ocup_alta']):
        return ''
    r = reparto_ocup(OCUP.loc[[cod]])
    rp = reparto_ocup(OCUP[OCUP.index.str[:2] == p])
    d = disimilitud(r, OCUP_ESP)
    puesto, total = ranking[cod], len(ranking)
    lejos = max(GRUPOS, key=lambda g: abs(r[g[0]] - OCUP_ESP[g[0]]))
    dif = (r[lejos[0]] - OCUP_ESP[lejos[0]]) * 100
    if puesto <= total // 10:
        frase = f'está entre el 10 % de los {num(total)} municipios con página propia cuya mezcla se parece más a la de España (puesto {num(puesto)})'
    elif puesto > total - total // 10:
        frase = f'está entre el 10 % de los {num(total)} municipios con página propia cuya mezcla se aleja más de la de España (puesto {num(puesto)})'
    else:
        frase = f'ocupa el puesto {num(puesto)} de {num(total)} municipios con página propia, ordenados de más a menos parecidos a España'
    filas = [[f'{n} <span class="leyenda">({ej})</span>', pct(r[g]), pct(rp[g]), pct(OCUP_ESP[g])] for g, n, ej in GRUPOS]
    return ('<h2 id="ocupacion">En qué trabajan sus vecinos, frente a España</h2>'
            + p_('Dato', f'De los {num(OCUP.loc[cod, "ocupados"])} vecinos de {escape(nombre)} con empleo, el {pct(r["ocup_alta"])} tiene una ocupación de alta cualificación, '
                 f'el {pct(r["ocup_media"])} una de cualificación media y el {pct(r["ocup_elemental"])} una ocupación elemental. '
                 f'En el conjunto de España son el {pct(OCUP_ESP["ocup_alta"])}, el {pct(OCUP_ESP["ocup_media"])} y el {pct(OCUP_ESP["ocup_elemental"])}.')
            + p_('Dato', f'Para tener el mismo reparto que España, el {pct(d)} de sus ocupados tendría que cambiar de grupo; {escape(nombre)} {frase}. '
                 f'La mayor diferencia está en las ocupaciones {"de " if lejos[0] != "ocup_elemental" else ""}{lejos[1].lower()}: '
                 f'{f"{abs(dif):.1f}".replace(".", ",")} puntos {"más" if dif > 0 else "menos"} que en España.')
            + tabla(f'Ocupados residentes en {escape(nombre)}, la provincia de {escape(nprov)} y España por grupo de ocupación (Censo anual del INE, 2023)',
                    ['Grupo de ocupación', escape(nombre), f'Provincia de {escape(nprov)}', 'España'], filas)
            + f'<p class="leyenda">Fuente: INE, Censo anual de población 2023, <a href="{OCUP_INE}">ocupados por grupo de ocupación</a>, por lugar de residencia '
              '(no de trabajo). Porcentajes sobre los ocupados cuya ocupación consta. Los grupos agregan la Clasificación Nacional de Ocupaciones: 1 a 3 (alta), 4 a 8 (media) y 9 (elemental).</p>')


def bloque_secciones(nombre, sec):
    s = sec[sec.censo >= 200].copy()
    if len(s) < 6:
        return ''
    s['part'] = s.votantes / s.censo
    gana = s[[c for c in T.FAM if c != 'OTROS']].idxmax(axis=1).value_counts()
    alto, bajo = s.nlargest(3, 'part'), s.nsmallest(3, 'part')
    lista = lambda g: ', '.join(f'{distrito_seccion(x.tract_code)} ({pct(x.part)})' for x in g.itertuples())
    reparto = '; '.join(f'{T.NOMBRE[c].split(" /")[0]}, en {num(n)}' for c, n in gana.items())
    return ('<h2>Barrio a barrio</h2>'
            + p_('Dato', f'En las generales de 2023, partido más votado en cada una de las {num(len(s))} secciones censales de {escape(nombre)}: {reparto}.')
            + p_('Dato', f'La participación fue más alta en {lista(alto)} y más baja en {lista(bajo)}. '
                 f'Entre la sección que más votó y la que menos hay {(alto.part.iloc[0] - bajo.part.iloc[0]) * 100:.0f} puntos.')
            + f'<p class="leyenda">Las secciones se identifican por su distrito y número del INE; en el <a href="{RAIZ_REL}?m={s.mun_code.iloc[0]}">mapa</a> se ven sobre las calles.</p>')


def bloque_municipales(nombre, m, rg):
    y = 'M2023'
    if m[f'{y}_part'].isna().all():
        return ''
    rm = T.resultado(m, y)
    gm = max(rm['pct'], key=lambda c: rm['pct'][c] or 0)
    quien = ('las listas locales y otros partidos' if gm == 'OTROS' else
             ('el ' if gm in ('PP', 'PSOE', 'PNV', 'BNG') else '') + T.NOMBRE[gm].split(' /')[0])
    dif = (rg['part'] - rm['part']) * 100
    puntos = f'{abs(dif):.1f}'.replace('.', ',')
    return ('<h2>Municipales frente a generales</h2>'
            + p_('Dato', f'En las municipales del 28 de mayo de 2023 votó el {pct(rm["part"])} del censo de {escape(nombre)}, y en las generales de dos meses después, el {pct(rg["part"])}: '
                 f'{puntos} puntos {"más" if dif > 0 else "menos"} para elegir al Gobierno que para elegir el ayuntamiento. '
                 f'En las municipales, el voto más alto fue para {quien} ({pct(rm["pct"][gm])}).')
            + '<p class="leyenda">En las municipales también votan los residentes de la Unión Europea, así que el censo no es idéntico. Las listas locales cuentan en «Otros».</p>')


# ---------- índice y páginas temáticas ----------
def tema_como_se_vota():
    """Guía «Cómo se vota»: las reglas que convierten votos en escaños, con las dos piezas de Actualidad."""
    ruta = 'elecciones/como-se-vota/'
    titulo = 'Cómo se vota: el precio de un escaño y los votos que no eligen a nadie'
    desc = ('Cuántos votos cuesta un escaño en cada provincia en las generales de 2023 y 2019, con el simulador de reparto, '
            'y cuántos votos se pierden en la barrera del 3 % y en el reparto por provincia. Datos de Interior.')
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Cómo se vota')]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Sistema electoral</p><h1 data-miga="Cómo se vota">Cómo se vota: el precio de un escaño</h1>')
    h.append('<p class="subtitulo">Por qué el mismo número de votos da más o menos diputados según la provincia, y qué pasa con los votos que no eligen a nadie</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append('<p class="resumen">Las elecciones al Congreso no reparten escaños por voto directo: se reparten por provincia, y cada provincia tiene un número fijo de diputados. '
             'Esta guía reúne las dos piezas que explican cómo ese reparto convierte votos en escaños.</p>')
    h.append('<h2>Las piezas</h2><ul>'
             f'<li><a href="{raiz}actualidad/precio-del-escano-29n/">El precio de un escaño por provincia</a>: cuántos votos cuesta un diputado en cada provincia, con el simulador de reparto (provincia, comunidad o España entera, con o sin barrera del 3 %).</li>'
             f'<li><a href="{raiz}actualidad/votos-sin-escano-29n/">Los votos que no eligen a nadie</a>: los votos perdidos en la barrera y en el reparto por provincia, y en qué provincias se decide el último escaño.</li>'
             '</ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
INE_PLAZOS = 'https://www.ine.es/dyngs/CEL/index.htm?cid=1702'
INE_SEDE = 'https://sede.ine.gob.es/'
CORREOS_29N = 'https://www.correos.com/sala-prensa/ya-se-puede-solicitar-el-voto-por-correo-para-las-elecciones-generales-del-29-de-noviembre/'
PUBLICO_MESA = 'https://www.publico.es/sociedad/tengo-votar-elecciones-generales-29n-consultar-colegio-mesa-electoral.html'
LEGALITAS_29N = 'https://www.legalitas.com/actualidad/elecciones-2026'


def tema_votar():
    """Guía práctica «Cómo votar el 29N»: colegio, documentos, voto por correo y permisos, con fuentes oficiales."""
    ruta = 'elecciones/votar-29n/'
    titulo = 'Dónde y cómo votar el 29N: colegio electoral, voto por correo y plazos'
    desc = ('Guía práctica para votar en las elecciones generales del 29 de noviembre de 2026: cómo saber tu colegio y tu mesa, qué documento llevar, '
            'hasta cuándo pedir y enviar el voto por correo y qué permisos tienes si trabajas. Con los plazos oficiales del INE.')
    qs = [('¿Dónde me toca votar el 29N?',
           f'En el colegio y la mesa que indica la tarjeta censal, que la Oficina del Censo Electoral envía del 2 al 10 de noviembre. '
           f'También se puede consultar en la <a href="{INE_SEDE}">sede electrónica del INE</a> o en el teléfono gratuito 900 343 232.'),
          ('¿A qué hora abren los colegios electorales?',
           f'La votación empieza a las 9.00 y sigue sin interrupción hasta las 20.00 (<a href="{LOREG}">artículo 84 de la LOREG</a>).'),
          ('¿Qué documento hay que llevar para votar?',
           f'El DNI, el pasaporte o el permiso de conducir, con fotografía y en original (<a href="{LOREG}">artículo 85 de la LOREG</a>). No sirven fotocopias.'),
          ('¿Hasta cuándo se puede pedir el voto por correo?',
           f'Hasta el 19 de noviembre, en cualquier oficina de Correos o en su web con certificado digital o DNI electrónico. Hay que mandarlo antes del 25 de noviembre (<a href="{INE_PLAZOS}">INE</a>).'),
          ('¿Tengo derecho a horas libres para votar si trabajo el domingo?',
           f'Sí: hasta cuatro horas retribuidas, según cuánto coincida tu jornada con el horario de votación (<a href="{LEGALITAS_29N}">Legálitas</a>).')]
    faq_html, faq_ld = faq(qs)
    ld = ld_pagina(titulo, desc, ruta, ESPANA)
    h = [cabeza(titulo, desc, ruta, [ld, faq_ld], 2, 'Cómo votar el 29N')]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Guía práctica · 29 de noviembre de 2026</p><h1 data-miga="Cómo votar el 29N">Dónde y cómo votar el 29N</h1>')
    h.append('<p class="subtitulo">Tu colegio y tu mesa, qué llevar, el voto por correo paso a paso y los permisos si trabajas o te toca mesa</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(f'<p class="resumen">{tipo("Dato")}Las generales se votan el domingo 29 de noviembre de 2026, de 9.00 a 20.00, en el colegio que asigna la Oficina del Censo Electoral. '
             'Quien no pueda ir ese día puede pedir el voto por correo hasta el 19 de noviembre y enviarlo hasta el 25.</p>')

    h.append('<h2 id="colegio">Dónde me toca votar</h2>'
             + p_('Dato', 'La Oficina del Censo Electoral manda a cada elector, del 2 al 10 de noviembre, la tarjeta censal con su colegio, su mesa y la dirección. '
                  f'Si cambian, lo comunica del 10 al 23 de noviembre (<a href="{INE_PLAZOS}">calendario del INE</a>).')
             + p_('Dato', f'No hace falta esperar a la carta: en la <a href="{INE_SEDE}">sede electrónica del INE</a> se consulta con la provincia, el municipio y la primera letra del primer apellido, '
                  'o con Cl@ve, que muestra directamente tus datos censales. Para dudas, la Oficina del Censo tiene el teléfono gratuito 900 343 232. '
                  f'Y el mismo domingo cada colegio tiene un callejero con la mesa que corresponde a cada calle (<a href="{PUBLICO_MESA}">Público</a>).')
             + f'<p>Si quieres ver cuántos electores hay en tu municipio y cómo votó tu barrio en 2023, búscalo en el <a href="{raiz}municipio/">índice de municipios</a> o en el <a href="{raiz}">mapa</a>.</p>')

    h.append('<h2 id="documentos">Qué llevar</h2>'
             + p_('Dato', f'El DNI, el pasaporte o el permiso de conducir, con tu fotografía y en original (<a href="{LOREG}">artículo 85 de la LOREG</a>). '
                  'La tarjeta censal no es obligatoria: sirve para saber tu mesa, no para votar.'))

    filas = [['Residentes en España', 'del 6 de octubre al 19 de noviembre', 'del 9 al 22 de noviembre', 'del 9 al 25 de noviembre'],
             ['Residentes temporalmente en el extranjero', 'del 6 al 31 de octubre', 'del 3 al 17 de noviembre', 'del 3 al 25 de noviembre'],
             ['Residentes en el extranjero (CERA)', 'no hace falta, la documentación llega sin pedirla', 'del 24 de octubre al 14 de noviembre', 'por correo al consulado del 4 al 24 de noviembre, o en la urna del consulado del 21 al 26']]
    h.append('<h2 id="correo">Voto por correo</h2>'
             + p_('Dato', 'Se pide en cualquier oficina de Correos, con el DNI, el pasaporte o el permiso de conducir originales, o en la web de Correos con certificado digital o DNI electrónico. '
                  'Tiene que pedirlo cada elector en persona; solo en caso de enfermedad o discapacidad, acreditada con certificado médico oficial, puede hacerlo otra persona con un poder notarial o consular. '
                  f'La documentación llega a la dirección que indiques en la solicitud (<a href="{CORREOS_29N}">Correos</a>).')
             + ''.join(f'<h3>{q}</h3><ul><li><b>Pedirlo</b>: {x}</li><li><b>Recibir la documentación</b>: {y}</li><li><b>Enviar el voto</b>: {z}</li></ul>'
                       for q, x, y, z in filas)
             + f'<p class="leyenda">Fuente: <a href="{INE_PLAZOS}">INE, Oficina del Censo Electoral, plazos de interés para los electores</a>. '
               'Para los residentes temporales y los CERA, la documentación sale antes o después según haya o no impugnación de candidaturas.</p>'
             + f'<p>Cuánto se ha usado el voto por correo y quién lo pide: <a href="{raiz}actualidad/voto-correo-29n/">siete de cada cien electores lo pidieron en 2023</a>.</p>')

    h.append('<h2 id="trabajo">Si trabajas el domingo o te toca mesa</h2>'
             + p_('Dato', 'Quien trabaje el 29 de noviembre tiene derecho a hasta cuatro horas libres y retribuidas para votar, según cuánto coincida su jornada con el horario de votación; '
                  'la empresa puede decidir en qué momento se toman.')
             + p_('Dato', 'Formar parte de una mesa electoral es obligatorio salvo que la Junta Electoral acepte una excusa justificada; no presentarse puede castigarse con prisión de tres meses a un año o multa '
                  f'(<a href="{LOREG}">artículo 143 de la LOREG</a>). Presidentes y vocales tienen permiso retribuido toda la jornada del domingo y cinco horas menos de trabajo el lunes '
                  f'(<a href="{LEGALITAS_29N}">Legálitas</a>).'))

    h.append('<h2>Y por la noche</h2>'
             f'<p>Desde las 20.00, el <a href="{raiz}">mapa de resultados</a> irá mostrando el recuento en directo, y la página de <a href="../resultados-elecciones-generales-2026/">resultados de las generales de 2026</a> el reparto de escaños. '
             f'El calendario de campaña y los diputados de cada provincia están en <a href="../elecciones-29n-2026/">la guía del 29N</a>; cómo se convierten los votos en escaños, en <a href="../como-se-vota/">Cómo se vota</a>.</p>')
    h.append(faq_html)
    h.append('<h2>Fuentes</h2><ul>'
             f'<li><a href="{INE_PLAZOS}">INE, Oficina del Censo Electoral: plazos de interés para los electores, generales del 29 de noviembre de 2026</a></li>'
             f'<li><a href="{LOREG}">Ley Orgánica 5/1985, del Régimen Electoral General (LOREG)</a>, artículos 84, 85 y 143</li>'
             f'<li><a href="{CORREOS_29N}">Correos: ya se puede solicitar el voto por correo para las elecciones generales del 29 de noviembre</a></li>'
             f'<li><a href="{PUBLICO_MESA}">Público: dónde tengo que votar en las elecciones generales del 29N</a> (14 de octubre de 2026)</li>'
             f'<li><a href="{LEGALITAS_29N}">Legálitas: guía legal para votar, trabajar y formar parte de una mesa electoral el 29N</a> (5 de octubre de 2026)</li>'
             f'<li><a href="{BOE_29N}">Real Decreto 806/2026</a>, de convocatoria</li></ul>'
             '<p class="leyenda">Esta guía resume la norma y los plazos oficiales; ante cualquier duda manda lo que digan el INE, la Junta Electoral Central y el BOE. Si ves un error, escríbeme y lo corrijo.</p>')
    h.append(PIE)
    return ruta, ''.join(h)


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
    h.append(f'<p><a class="vermapa" href="../">Abrir el mapa electoral calle a calle, por sección censal</a></p>')
    filas = [fila_resumen(f'<a href="{s}/">{escape(i["nombre"])}</a>', i['r']) for s, i in resumen.items()]
    h.append('<h2>Comunidades autónomas</h2>' + tabla('Generales de 2023 por comunidad autónoma', ['Comunidad', 'Participación', 'Más votado', 'Segundo'], filas))
    li = []
    for p in sorted(PROV_SLUG, key=lambda p: PROV_SLUG[p]):
        u = ruta_provincia(p)[len('elecciones/'):]
        li.append(f'<li><a href="{u}">Elecciones en {escape(PROV_NOMBRE[p])}</a></li>')
    h.append('<h2>Provincias</h2><ul class="cols">' + ''.join(li) + '</ul>')
    pob = T.MUN.set_index('mun_code').poblacion
    cs = sorted((c for c in CIUDADES if c in CAPITALES or pob[c] >= GRANDE), key=lambda c: slug(T.MUN.loc[T.MUN.mun_code == c, 'municipio'].iloc[0]))
    h.append(f'<h2>Ciudades</h2><p>Las {len(cs)} capitales de provincia y municipios de más de 50.000 habitantes, con el voto barrio a barrio. '
             f'Los {num(len(CIUDADES) - len(cs))} municipios de entre 1.000 y 50.000 habitantes con página propia están en la página de su provincia.</p><ul class="cols">'
             + ''.join(f'<li><a href="../{CIUDADES[c]}">Elecciones en {escape(T.MUN.loc[T.MUN.mun_code == c, "municipio"].iloc[0])}</a></li>' for c in cs) + '</ul>')
    h.append('<p>Todos los municipios con página propia, provincia a provincia: <a href="../municipio/">elecciones por municipio</a>. '
             'Las piezas agrupadas por tema: <a href="../temas/">temas</a>.</p>')
    h.append('<h2>Por tema</h2><ul>'
             '<li><a href="elecciones-29n-2026/">Elecciones generales del 29N de 2026</a>: fecha, campaña y diputados por provincia</li>'
             '<li><a href="resultados-elecciones-generales-2026/">Resultados de las elecciones generales de 2026</a>: el escrutinio del 29N en directo y el resultado de 2023</li>'
             '<li><a href="resultados-elecciones-por-municipio/">Resultados de las elecciones por municipio</a>: quién ganó en cada pueblo y ciudad desde 1977</li>'
             '<li><a href="censo-electoral-2026/">Censo electoral de 2026</a>: cuántos electores votan el 29N en cada provincia y municipio</li>'
             '<li><a href="participacion-electoral-por-barrio/">Participación electoral por barrio</a>: dónde se vota más y dónde menos</li>'
             '<li><a href="mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a>: qué es una sección, qué datos tiene cada una y cómo consultarlas</li>'
             '<li><a href="voto-y-renta-por-barrios/">Voto y renta por barrios</a>: participación y voto de cada partido según la renta de la sección</li>'
             '<li><a href="votar-29n/">Dónde y cómo votar el 29N</a>: tu colegio electoral, qué llevar, el voto por correo y los plazos</li>'
             '<li><a href="como-se-vota/">Cómo se vota</a>: el precio de un escaño por provincia y los votos que no eligen a nadie</li>'
             '<li><a href="../abstencion.html">Participación por sección censal en Cataluña</a>: quién no vota y dónde</li>'
             '<li><a href="../atlas/">Atlas de las anomalías electorales</a>: los lugares que votan distinto de lo que cabría esperar</li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return 'elecciones/', ''.join(h)


def lista_piezas(slugs, nivel):
    raiz = '../' * nivel
    li = [f'<li><a href="{u}"><span class="kicker">{k}</span><b>{escape(t)}</b></a></li>' for u, t, k in actualidad_de(slugs, raiz)]
    return '<ul class="sigue">' + ''.join(li) + '</ul>'


def tema_renta(resumen):
    ruta = 'elecciones/voto-y-renta-por-barrios/'
    titulo = 'Voto y renta por barrios: cómo vota cada sección censal de España según su renta'
    desc = ('Participación y voto a cada partido en las 36.000 secciones censales de España ordenadas por renta, en las generales de 2023 y desde 2004. '
            'Datos del Ministerio del Interior y del INE.')
    q10 = T.por_renta(T.SEC, 10)
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Voto y renta', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Generales 2023</p><h1 data-miga="Voto y renta por barrios">Voto y renta por barrios</h1>')
    h.append('<p class="subtitulo">Cómo votan las secciones censales de España según su renta: participación y voto a cada partido, del 10 % más pobre al 10 % más rico</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
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
    titulo = 'Mapa electoral de España por sección censal: resultados calle a calle y barrio a barrio desde 2004'
    desc = ('Qué es una sección censal y cómo consultar los resultados de las generales, municipales y europeas en las 36.462 secciones de España, '
            'con renta, edad y población extranjera. Datos abiertos.')
    y = T.ULTIMA
    sec = T.SEC
    gana = sec[[c for c in T.FAM if c != 'OTROS']].idxmax(axis=1)
    cuenta = gana.value_counts()
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Mapa por sección censal', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Datos abiertos</p><h1 data-miga="Mapa por sección censal">Mapa electoral de España por sección censal</h1>')
    h.append('<p class="subtitulo">Resultados de las elecciones barrio a barrio en las 36.462 secciones censales de España, cruzados con renta, edad y población extranjera</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    top = cuenta.index[:4]
    h.append(f'<p class="resumen">{tipo("Dato")}En las generales de 2023 el PP fue la lista más votada en {num(cuenta.get("PP", 0))} de las {num(len(sec))} secciones censales de España; '
             f'el PSOE, en {num(cuenta.get("PSOE", 0))}. ' + ', '.join(f'{T.NOMBRE[c]}, en {num(cuenta[c])}' for c in top if c not in ('PP', 'PSOE')) + '.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Abrir el mapa electoral calle a calle</a> <a class="vermapa" href="{raiz}generales-2026/metodologia.html#descargas">Descargar los datos</a></p>')
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
             '<li>Escribe tu calle y número, o tu municipio, en el buscador del mapa; al acercarte aparecen las secciones sobre el callejero, calle a calle.</li>'
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


# ---------- páginas de entrada por intención de búsqueda ----------
def slugs_actualidad():
    return sorted(p.parent.name for p in (ROOT / 'actualidad').glob('*/index.html'))


def faq(qs):
    """Bloque visible de preguntas frecuentes y su FAQPage."""
    html_ = '<h2>Preguntas frecuentes</h2><div class="faq">' + ''.join(f'<h3>{escape(q)}</h3><p>{a}</p>' for q, a in qs) + '</div>'
    ld = {'@context': 'https://schema.org', '@type': 'FAQPage',
          'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': re.sub(r'<[^>]+>', '', a)}} for q, a in qs]}
    return html_, ld


def r_prov(p, y=None):
    return T.resultado(T.MUN[T.MUN.prov == p], y or T.ULTIMA)


BOE_29N = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742'
# Ilustración de cabecera de cada página de entrada (collages con IA de Nacho; los mapas y gráficos, nunca)
FOTOS = {
    'elecciones/elecciones-29n-2026/': ('congreso-urna-calendario-29n.jpg',
                                       'El hemiciclo del Congreso, una urna con papeletas y un calendario con el 29 marcado: un collage.'),
    'elecciones/participacion-electoral-por-barrio/': ('colegio-electoral-cola-y-bloques.jpg',
                                                       'Una cola a la puerta de un colegio electoral y, enfrente, bloques de pisos de un barrio: un collage.'),
    'elecciones/resultados-elecciones-por-municipio/': ('libros-plazas-y-arquitectura-de-espana.jpg',
                                                        'Libros, plazas y arquitectura de pueblos y ciudades de España: un collage.'),
    'elecciones/censo-electoral-2026/': ('listas-censo-sobre-pasaporte.jpg',
                                         'Listas del censo con los nombres tapados, un sobre, un pasaporte, el mapa de España y el Congreso: un collage.'),
    'elecciones/voto-y-renta-por-barrios/': ('urna-entre-bloques-y-chalets.jpg',
                                             'Una urna entre bloques de pisos humildes y chalés con jardín, y monedas y billetes al pie: un collage.'),
    'elecciones/mapa-electoral-seccion-censal/': ('plano-secciones-lupa.jpg',
                                                  'Un plano de calles dividido en teselas de colores y una lupa sobre una de ellas: un collage.'),
}
# Escala neutra para la participación (no es de ningún partido)
RAMPA_PART = [(0.60, '#e9eef2', 'menos del 60 %'), (0.65, '#c3d2dc', '60-65 %'), (0.70, '#93aec0', '65-70 %'),
              (0.75, '#6489a3', '70-75 %'), (0.80, '#3d6683', '75-80 %'), (9, '#1f4560', '80 % o más')]


def color_part(v):
    return next(c for tope, c, _ in RAMPA_PART if v < tope)


def foto_html(ruta, raiz):
    if ruta not in FOTOS:
        return ''
    f, alt = FOTOS[ruta]
    return (f'<figure class="foto"><img src="{raiz}img/elecciones/{f}" alt="{escape(alt)}" width="1280" height="720" loading="eager">'
            f'<figcaption>{escape(alt)} Ilustración generada con IA para Mapa Electoral. <a href="{raiz}atlas/politica-editorial/#ia">Uso de IA</a>.</figcaption></figure>')


def imagen_og(ruta):
    return f'img/elecciones/{FOTOS[ruta][0]}' if ruta in FOTOS else None


def svg_fichero(nombre, svg):
    """Guarda un mapa grande como fichero aparte (se carga con <img> y pesa menos en la página)."""
    d = OUT / 'img'
    d.mkdir(exist_ok=True)
    (d / nombre).write_text(svg, encoding='utf-8')
    return f'../img/{nombre}'


def figura(svg_o_img, pie, items=None):
    return f'<figure>{svg_o_img}{MS.leyenda(items) if items else ""}<figcaption>{pie}</figcaption></figure>'


def leyenda_partidos(cods):
    orden = [c for c in T.FAM if c in set(cods)]
    return [(T.COLOR[c], T.NOMBRE[c]) for c in orden]


SIS = json.loads((ROOT / 'actualidad' / 'src' / 'sistema' / 'cifras.json').read_text(encoding='utf-8'))['2023_07']   # escaños de 2023 (actualidad/src/sistema/calcular.py)
R26 = json.loads((ROOT / 'actualidad' / 'src' / 'sistema' / 'cifras.json').read_text(encoding='utf-8'))['votos_2023_reparto_2026']


def diputados_por_provincia():
    grupos = {}
    for p, n in ESCANOS_2026.items():
        grupos.setdefault(n, []).append(PROV_NOMBRE[p])
    y = lambda v: v[0] if len(v) == 1 else ', '.join(v[:-1]) + ' y ' + v[-1]
    return '; '.join(f'{y(sorted(v, key=slug))}, {n}' for n, v in sorted(grupos.items(), reverse=True)) + '.'


def tema_29n(resumen):
    ruta = 'elecciones/elecciones-29n-2026/'
    titulo = 'Elecciones generales 29N 2026: escaños por provincia, fecha, campaña y resultados de 2023'
    desc = ('Las elecciones generales se celebran el domingo 29 de noviembre de 2026. Fechas de la campaña, los 350 diputados provincia a provincia '
            '(Madrid gana uno y Cádiz lo pierde), mapas del resultado de 2023 y lo que puede decidirse en cada territorio.')
    qs = [('¿Cuándo son las elecciones generales de 2026?',
           f'El domingo 29 de noviembre de 2026. Las convoca el <a href="{BOE_29N}">Real Decreto 806/2026</a>, publicado en el BOE el 6 de octubre, que disuelve el Congreso y el Senado elegidos el 23 de julio de 2023.'),
          ('¿Cuándo empieza la campaña electoral?',
           'La campaña dura quince días: empieza a las cero horas del viernes 13 de noviembre y termina a las doce de la noche del viernes 27 de noviembre.'),
          ('¿Cuántos diputados se eligen y qué cambia respecto a 2023?',
           'Se eligen 350 diputados en 52 circunscripciones. Respecto a 2023, Madrid pasa de 37 a 38 y Cádiz de 9 a 8; el resto de provincias reparte los mismos escaños.'),
          ('¿Cuántos diputados elige cada provincia en 2026?',
           'De mayor a menor: ' + diputados_por_provincia()),
          ('¿Cuántos diputados tiene cada partido?',
           'En el Congreso elegido en 2023: ' + '; '.join(f'{x["partido"]}, {x["escanos"]}' for x in SIS['partidos'] if x['escanos']) + '. '
           'Son los escaños de cada candidatura el día de las elecciones; algunos diputados cambiaron después de grupo parlamentario.'),
          ('¿Cuántos senadores elige cada provincia?',
           'Cuatro en cada provincia; tres en Gran Canaria, Mallorca y Tenerife; uno en Ibiza-Formentera, Menorca, Fuerteventura, La Gomera, El Hierro, Lanzarote y La Palma, y dos en Ceuta y en Melilla.'),
          ('¿Cuándo se constituyen las nuevas Cortes?',
           'El 23 de diciembre de 2026, a las diez de la mañana, según el decreto de convocatoria.'),
          ('¿Dónde puedo ver cómo votó mi barrio?',
           'En el mapa de Mapa Electoral: escribe tu calle y número en el buscador y pulsa en tu sección censal. La noche del 29N el mapa mostrará el recuento en directo.')]
    faq_html, faq_ld = faq(qs)
    ld = ld_pagina(titulo, desc, ruta, ESPANA)
    h = [cabeza(titulo, desc, ruta, [ld, faq_ld], 2, 'Elecciones 29N 2026', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Elecciones generales · 29 de noviembre de 2026</p><h1 data-miga="Elecciones 29N 2026">Elecciones generales del 29N de 2026</h1>')
    h.append('<p class="subtitulo">Cuándo se vota, cuántos diputados elige cada provincia y cómo votó cada territorio en 2023, el punto de partida</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    e = T.ESPANA
    h.append(f'<p class="resumen">{tipo("Dato")}Las elecciones al Congreso y al Senado se celebran el domingo 29 de noviembre de 2026, convocadas por el '
             f'<a href="{BOE_29N}">Real Decreto 806/2026</a> (BOE del 6 de octubre). La campaña va del viernes 13 al viernes 27 de noviembre. '
             f'Se eligen 350 diputados: Madrid gana uno, hasta 38, y Cádiz pierde uno, hasta 8. En 2023 votó el {pct(e["part"])} del censo residente y el PP fue el más votado, con el {pct(e["pct"]["PP"])}.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Abrir el mapa electoral calle a calle</a> <a class="vermapa" href="{raiz}generales-2026/metodologia.html#descargas">Descargar los datos</a></p>')
    h.append('<p>Son las decimosextas elecciones generales desde 1977 y las primeras desde las del 23 de julio de 2023, que dejaron un Congreso sin mayoría de dos bloques. '
             'Esta página reúne lo que se sabe del calendario y del reparto de escaños, y el resultado de 2023 provincia a provincia, que es el punto de partida de cada partido. '
             'Cada provincia, comunidad y municipio de más de 1.000 habitantes tiene su propia página con el voto barrio a barrio y la serie desde 1977.</p>')
    h.append('<h2>Calendario</h2><ul>'
             '<li><b>6 de octubre</b>: el BOE publica la disolución de las Cortes y la convocatoria.</li>'
             '<li><b>13 de noviembre</b>, a las 0.00: empieza la campaña electoral.</li>'
             '<li><b>27 de noviembre</b>, a las 24.00: termina la campaña.</li>'
             '<li><b>19 de noviembre</b>: último día para pedir el voto por correo (<a href="../votar-29n/">cómo votar el 29N</a>).</li>'
             '<li><b>29 de noviembre</b>: jornada electoral.</li>'
             '<li><b>23 de diciembre</b>, a las 10.00: sesiones constitutivas del Congreso y del Senado.</li></ul>'
             + p_('Dato', f'Fuente: <a href="{BOE_29N}">Real Decreto 806/2026, de 5 de octubre</a>. El mapa de resultados tendrá en directo el recuento de la noche del 29N, sección a sección.'))
    # mapa de provincias: más votado en 2023 y diputados en 2026
    rp = {p: r_prov(p) for p in ESCANOS_2026}
    gp = {p: T.ganador(r) for p, r in rp.items()}
    epd = {p: rp[p]['censo'] / ESCANOS_2026[p] for p in ESCANOS_2026}   # electores por diputado
    filas = []
    for p in sorted(ESCANOS_2026, key=lambda p: (-ESCANOS_2026[p], PROV_NOMBRE[p])):
        r, g = rp[p], gp[p]
        d = ESCANOS_2026[p] - ESCANOS_2023[p]
        esc = SIS['provincias'][p]['esc']
        filas.append([f'<a href="../../{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a>', str(ESCANOS_2026[p]), str(ESCANOS_2023[p]),
                      (f'{d:+d}'.replace('-', '−') if d else '='), ' · '.join(f'{escape(k)} {v}' for k, v in sorted(esc.items(), key=lambda kv: -kv[1])),
                      num(round(epd[p], -2)), pct(r['part'])])
    h.append('<h2 id="escanos">Escaños por provincia en 2026</h2>'
             + p_('Dato', 'Diputados que elige cada circunscripción el 29N y en 2023, cómo se repartieron en 2023, electores residentes por diputado y participación del censo residente. '
                  'Cada provincia enlaza a su página, con el voto por municipio y por barrio desde 1977.')
             + tabla('Escaños por circunscripción en las generales de 2026 y de 2023', ['Provincia', '2026', '2023', 'Cambio', 'Reparto en 2023', 'Electores por diputado', 'Participación 2023'], filas))
    pt = SIS['partidos']
    h.append('<h2 id="partidos">Escaños de cada partido</h2>'
             + p_('Dato', 'En las generales de 2023 el PP obtuvo ' + num(pt[0]['escanos']) + ' diputados; '
                  + '; '.join(f'{escape(x["partido"])}, {num(x["escanos"])}' for x in pt[1:] if x['escanos']) + '. '
                  f'Con los mismos votos y el reparto de 2026, en el que Madrid gana un diputado y Cádiz lo pierde, el PP tendría {num(R26["PP"])} y el PSOE {num(R26["PSOE"])}; el resto, igual.')
             + tabla('Votos y escaños de cada partido en las generales de 2023', ['Partido', 'Votos', '% del voto válido', 'Escaños', 'Con el reparto de 2026'],
                     [[escape(x['partido']), num(x['votos']), f'{x["pct"]:.1f}'.replace('.', ',') + ' %', str(x['escanos']), str(R26.get(x['partido'], 0))] for x in pt if x['escanos']])
             + f'<p class="leyenda">Fuente: Ministerio del Interior. Votos y escaños por candidatura. Cálculo del reparto con la regla D\'Hondt en <a href="{raiz}actualidad/precio-del-escano-29n/">el precio del escaño</a>.</p>')
    cuenta = {}
    for g in gp.values():
        cuenta[g] = cuenta.get(g, 0) + 1
    orden = sorted(cuenta, key=lambda c: -cuenta[c])
    h.append('<h2>Quién ganó en cada provincia en 2023</h2>'
             + p_('Dato', 'En las generales de 2023 el PP fue la lista más votada en ' + num(cuenta.get('PP', 0)) + ' de las 52 circunscripciones; '
                  + '; '.join(f'{T.NOMBRE[c]}, en {num(cuenta[c])}' for c in orden if c != 'PP') + '. '
                  'El número de cada provincia es el de diputados que elige el 29N.')
             + figura(MS.mapa({p: T.COLOR[g] for p, g in gp.items()}, 'Partido más votado en cada provincia en las generales de 2023 y diputados que elige en 2026',
                              etiquetas=ESCANOS_2026),
                      'Partido más votado en cada provincia en las generales del 23 de julio de 2023, sin voto desde el extranjero, y diputados que elige cada una el 29N. '
                      'Canarias, en el recuadro. Fuente: Ministerio del Interior y Real Decreto 806/2026.', leyenda_partidos(gp.values())))
    r19 = {p: T.ganador(r_prov(p, '2019_11')) for p in ESCANOS_2026}
    cambian = [p for p in ESCANOS_2026 if r19[p] != gp[p]]
    if cambian:
        h.append(p_('Dato', f'Entre noviembre de 2019 y julio de 2023 cambió el partido más votado en {num(len(cambian))} provincias: '
                    + ', '.join(f'<a href="../../{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a> ({T.NOMBRE[r19[p]]} → {T.NOMBRE[gp[p]]})' for p in sorted(cambian, key=lambda p: PROV_NOMBRE[p])) + '.'))
    mn, mx = min(epd, key=epd.get), max(epd, key=epd.get)
    h.append('<h2>Cuánto vale cada voto</h2>'
             + p_('Dato', f'Con el censo residente de 2023, en {escape(PROV_NOMBRE[mn])} hay un diputado por cada {num(round(epd[mn], -2))} electores, y en {escape(PROV_NOMBRE[mx])}, '
                  f'uno por cada {num(round(epd[mx], -2))}: {str(round(epd[mx] / epd[mn], 1)).replace(".", ",")} veces más. La ley electoral da a cada provincia un mínimo de dos diputados y reparte el resto por población, '
                  'así que las provincias pequeñas eligen más diputados por elector.')
             + f'<p>Cuántos votos costó cada escaño en 2023, provincia a provincia y partido a partido, está en <a href="{raiz}actualidad/precio-del-escano-29n/">el precio del escaño</a>; '
               f'dónde se decidió el último diputado por pocos votos, en <a href="{raiz}actualidad/ultimo-escano-29n/">qué provincias pueden decidir el 29N</a>, '
               f'y cuántos votos se quedaron sin representación, en <a href="{raiz}actualidad/votos-sin-escano-29n/">votos sin escaño</a>.</p>')
    h.append(bloque_resultado('España', e))
    gm = T.MUN.set_index('mun_code')['2023_07_gana'].dropna()
    img = svg_fichero('ganador-municipios-2023.svg', MS.mapa({c: T.COLOR[v] for c, v in gm.items() if v in T.COLOR},
                                                            'Partido más votado en cada municipio en las generales de 2023', 'mun', xmlns=True))
    h.append('<h2>Municipio a municipio</h2>'
             + p_('Dato', f'Por municipios, el mapa de 2023 es más variado que el de provincias: el PSOE fue el más votado en {num((gm == "PSOE").sum())} de los {num(len(gm))} municipios, '
                  f'sobre todo en Andalucía, Extremadura, Asturias y Cataluña, y el PP en {num((gm == "PP").sum())}.')
             + figura(f'<img class="mapa" src="{img}" alt="Mapa de España con el partido más votado en cada uno de sus {num(len(gm))} municipios en las generales de 2023" width="800" loading="lazy">',
                      f'Partido más votado en cada municipio en las generales de 2023. Más detalle, en <a href="../resultados-elecciones-por-municipio/">resultados por municipio</a>. Fuente: Ministerio del Interior.',
                      leyenda_partidos(gm.unique())))
    filas = [fila_resumen(f'<a href="../{s}/">{escape(i["nombre"])}</a>', i['r']) for s, i in resumen.items()]
    h.append('<h2>Por comunidad autónoma</h2>' + tabla('Generales de 2023 por comunidad autónoma', ['Comunidad', 'Participación', 'Más votado', 'Segundo'], filas))
    h.append(faq_html)
    h.append('<h2>Piezas sobre el 29N</h2>' + lista_piezas([s for s in slugs_actualidad() if es_29n(s)], 2))
    h.append('<h2>Más datos</h2><ul><li><a href="../resultados-elecciones-generales-2026/">Resultados de las elecciones generales de 2026, en directo la noche del 29N</a></li>'
             '<li><a href="../censo-electoral-2026/">Censo electoral de 2026 por provincia y municipio</a></li>'
             '<li><a href="../participacion-electoral-por-barrio/">Participación electoral por barrio</a></li>'
             '<li><a href="../resultados-elecciones-por-municipio/">Resultados de las elecciones por municipio desde 1977</a></li>'
             '<li><a href="../mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li>'
             '<li><a href="../voto-y-renta-por-barrios/">Voto y renta por barrios</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def tema_participacion(resumen):
    ruta = 'elecciones/participacion-electoral-por-barrio/'
    titulo = 'Participación electoral por barrio: dónde se vota más y dónde menos en España, sección a sección'
    desc = ('Participación en las generales en las 36.000 secciones censales de España: mapas por provincia y municipio, los barrios que más y menos votan, '
            'la brecha por renta, las provincias y ciudades con más y menos participación y su evolución desde 1977.')
    sec = T.SEC[T.SEC.censo > 0].copy()
    sec['p'] = sec.votantes / sec.censo
    q10 = T.por_renta(T.SEC, 10)
    serie_esp = {y: T.resultado(T.MUN, y)['part'] for y in T.GENERALES}
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Participación por barrio', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Generales 2023</p><h1 data-miga="Participación por barrio">Participación electoral por barrio</h1>')
    h.append('<p class="subtitulo">Cuánta gente vota en cada sección censal de España, de qué depende y cómo ha cambiado desde 1977</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    bajo, alto = (sec.p < 0.5).sum(), (sec.p >= 0.8).sum()
    h.append(f'<p class="resumen">{tipo("Dato")}En las generales de 2023 votó el {pct(T.ESPANA["part"])} del censo residente en España. '
             f'Pero en {num(bajo)} de las {num(len(sec))} secciones censales votó menos de la mitad del censo, y en {num(alto)} votó el 80 % o más. '
             f'En el 10 % del censo que vive en los barrios con menos renta votó el {pct(q10[0]["part"])}; en el 10 % con más renta, el {pct(q10[-1]["part"])}.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Ver la participación de tu barrio en el mapa</a></p>')
    h.append('<p>Busca tu calle en el mapa y pulsa en tu sección: la ficha da la participación de cada elección desde 2004 junto a la renta, la edad y la población extranjera del barrio. '
             'La participación se calcula sobre el censo de residentes en España; el voto desde el extranjero (CERA) no se asigna a ninguna sección, '
             'por eso las cifras de esta página son algo más altas que las oficiales, que lo incluyen.</p>')
    rp = {p: r_prov(p) for p in PROV_NOMBRE}
    h.append('<h2>El mapa de la participación</h2>'
             + p_('Dato', 'Participación en las generales de 2023 por provincia. Se vota más en el interior de la península y en el norte, y menos en Canarias, Ceuta, Melilla y Cataluña.')
             + figura(MS.mapa({p: color_part(r['part']) for p, r in rp.items()}, 'Participación por provincia en las generales de 2023',
                              etiquetas={p: f'{r["part"] * 100:.0f}' for p, r in rp.items()}),
                      'Participación del censo residente por provincia, generales del 23 de julio de 2023. Fuente: Ministerio del Interior.',
                      [(c, t) for _, c, t in RAMPA_PART]))
    pm = T.MUN.set_index('mun_code')
    pm = (pm['2023_07_votantes'] / pm['2023_07_censo']).dropna()
    img = svg_fichero('participacion-municipios-2023.svg', MS.mapa({c: color_part(v) for c, v in pm.items()},
                                                                   'Participación por municipio en las generales de 2023', 'mun', xmlns=True))
    h.append(figura(f'<img class="mapa" src="{img}" alt="Mapa de España con la participación de cada municipio en las generales de 2023" width="800" loading="lazy">',
                    'Participación del censo residente en cada municipio, generales de 2023. Fuente: Ministerio del Interior.', [(c, t) for _, c, t in RAMPA_PART]))
    filas = [[f'{x["q"]}.º', f'{euros(x["desde"])} – {euros(x["hasta"])}', pct(x['part'])] for x in q10]
    h.append('<h2>La renta del barrio y la participación</h2>'
             + p_('Patrón', f'De los barrios más pobres a los más ricos, la participación sube en cada escalón: {pct(q10[0]["part"])}, {pct(q10[4]["part"])} en el grupo central y {pct(q10[-1]["part"])} arriba. '
                  'Es una relación entre barrios, no entre personas.')
             + tabla('Participación en las generales de 2023 por decil de renta de la sección censal (grupos con el mismo censo)', ['Decil', 'Renta por unidad de consumo', 'Participación'], filas)
             + f'<p>Con el voto a cada partido por decil, en <a href="../voto-y-renta-por-barrios/">voto y renta por barrios</a>. La brecha es mayor en las grandes ciudades: '
               f'en Málaga va del 46,7 % al 80,6 %, según <a href="{raiz}actualidad/malaga-barrio-a-barrio-29n/">la pieza de Málaga barrio a barrio</a>.</p>')
    # los barrios que menos votan
    s5 = sec[sec.censo >= 500].sort_values('p')
    nombres = T.MUN.set_index('mun_code').municipio
    def lbar(d):
        out = []
        for tc, mc, v in zip(d.tract_code, d.mun_code, d.p):
            n = escape(nombres.get(mc, mc))
            n = f'<a href="../../{CIUDADES[mc]}">{n}</a>' if mc in CIUDADES else n
            out.append(f'<li>{n}, {distrito_seccion(tc)}: {pct(v)}</li>')
        return '<ul>' + ''.join(out) + '</ul>'
    h.append('<h2>Los barrios que menos y más votan</h2>'
             + p_('Dato', 'Secciones censales con al menos 500 electores y la participación más baja de España en las generales de 2023. Muchas están en las periferias de Ceuta y Melilla, '
                  'en Canarias y en barrios con mucha población joven o de llegada reciente.')
             + lbar(s5.head(10))
             + p_('Dato', 'Y las diez secciones con al menos 500 electores donde más se votó:') + lbar(s5.tail(10).iloc[::-1])
             + '<p class="leyenda">El número de distrito y sección es el del INE; en el mapa se busca escribiendo la calle o pulsando en el municipio.</p>')
    srt = sorted(rp.items(), key=lambda x: -x[1]['part'])
    li = lambda xs: ', '.join(f'<a href="../../{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a> ({pct(r["part"])})' for p, r in xs)
    h.append('<h2>Provincias que más y menos votan</h2>'
             + p_('Dato', f'Donde más se votó en 2023: {li(srt[:5])}. Donde menos: {li(srt[::-1][:5])}.'))
    d19 = {p: rp[p]['part'] - r_prov(p, '2019_11')['part'] for p in PROV_NOMBRE}
    sube = sorted(d19, key=lambda p: -d19[p])
    pp = lambda v: f'{v * 100:+.1f}'.replace('.', ',').replace('-', '−') + ' p.'
    h.append(p_('Dato', 'Entre noviembre de 2019 y julio de 2023, la participación subió en ' + num(sum(1 for v in d19.values() if v > 0)) + ' de las 52 provincias. Donde más subió: '
                + ', '.join(f'{escape(PROV_NOMBRE[p])} ({pp(d19[p])})' for p in sube[:3]) + '; donde menos, '
                + ', '.join(f'{escape(PROV_NOMBRE[p])} ({pp(d19[p])})' for p in sube[::-1][:3]) + '.'))
    pob = T.MUN.set_index('mun_code').poblacion
    m = T.MUN[T.MUN.mun_code.isin([c for c in CIUDADES if pob[c] >= GRANDE]) & T.MUN['2023_07_part'].notna()]
    m = m.assign(pp=m['2023_07_votantes'] / m['2023_07_censo']).sort_values('pp')
    lm = lambda d: ', '.join(f'<a href="../../{CIUDADES[c]}">{escape(n)}</a> ({pct(v)})' for c, n, v in zip(d.mun_code, d.municipio, d.pp))
    h.append('<h2>Ciudades que más y menos votan</h2>'
             + p_('Dato', f'Entre los {num(len(m))} municipios de más de 50.000 habitantes, donde menos se votó en 2023 fue en {lm(m.head(5))}; '
                  f'donde más, en {lm(m.tail(5).iloc[::-1])}. Cada ciudad tiene su página con la participación de cada barrio.'))
    filas = [[T.etiqueta(y), pct(serie_esp[y])] for y in T.GENERALES]
    mx = max(T.GENERALES, key=lambda y: serie_esp[y]); mn = min(T.GENERALES, key=lambda y: serie_esp[y])
    h.append('<h2>La participación desde 1977</h2>'
             + p_('Dato', f'Entre los residentes en España, la participación más alta de las 16 generales fue en {T.etiqueta(mx)} ({pct(serie_esp[mx])}) y la más baja en {T.etiqueta(mn)} ({pct(serie_esp[mn])}). '
                  'Contando también el voto desde el extranjero, que aquí no entra, el mínimo oficial es el de noviembre de 2019, con el 66,2 %: '
                  f'<a href="{raiz}actualidad/votar-en-noviembre/">el último noviembre electoral</a>.')
             + tabla('Participación del censo residente en España en las elecciones al Congreso', ['Elección', 'Participación'], filas))
    filas = []
    for s, i in resumen.items():
        r19 = T.resultado(T.MUN[T.MUN.prov.isin(CCAA[s][2])], '2019_11')
        filas.append([f'<a href="../{s}/">{escape(i["nombre"])}</a>', pct(i['r']['part']), pct(r19['part'])])
    h.append('<h2>Por comunidad autónoma</h2>' + tabla('Participación del censo residente por comunidad autónoma', ['Comunidad', '2023', 'Noviembre 2019'], filas))
    h.append('<h2>Piezas sobre quién vota y quién no</h2>' + lista_piezas(TEMA_PARTICIPACION, 2)
             + f'<ul class="sigue"><li><a href="{raiz}abstencion.html"><span class="kicker">Reportaje</span><b>¿Quién no vota en Cataluña? La abstención en las 5.115 secciones censales catalanas</b></a></li></ul>')
    h.append('<h2>Más datos</h2><ul><li><a href="../elecciones-29n-2026/">Elecciones generales del 29N de 2026</a></li>'
             '<li><a href="../voto-y-renta-por-barrios/">Voto y renta por barrios</a></li>'
             '<li><a href="../mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


RAMPA_CENSO = [(0.0, '#f2e6dc', 'pierde electores'), (0.02, '#e9eef2', '0-2 %'), (0.04, '#93aec0', '2-4 %'), (9, '#3f6c8c', 'más del 4 %')]
SEGREGADOS = {'48916': '48036'}   # Usansolo se separó de Galdakao después de 2023: se comparan juntos


def tema_censo(resumen):
    ruta = 'elecciones/censo-electoral-2026/'
    c = CENSO.copy()
    c['prov'] = c.index.str[:2]
    c['t23'], c['t26'] = c.cer_2023 + c.cera_2023, c.cer_2026 + c.cera_2026
    cer, cera, total, t23 = censo_29n(c.index)
    d = total - t23
    titulo = f'Censo electoral 2026: {str(round(total / 1e6, 1)).replace(".", ",")} millones de electores para el 29N, provincia a provincia'
    desc = (f'El censo de las elecciones generales del 29 de noviembre de 2026 tiene {num(total)} electores, {num(d)} más que en 2023: '
            f'{num(cer)} viven en España y {num(cera)} en el extranjero. Por provincia, comunidad y municipio, con datos del INE.')
    qs = [('¿Cuántos electores hay en España para las elecciones del 29N?',
           f'{num(total)}, según el censo de consulta del INE: {num(cer)} residentes en España y {num(cera)} residentes en el extranjero.'),
          ('¿Cuántos españoles que viven en el extranjero pueden votar?',
           f'{num(cera)}, inscritos en el Censo de Españoles Residentes Ausentes (CERA): {num(c.cera_2026.sum() - c.cera_2023.sum())} más que en 2023. '
           'Votan desde su país de residencia y su voto se suma al de la provincia en la que están inscritos.'),
          ('¿Dónde puedo comprobar si estoy en el censo?',
           'En la <a href="https://www.ine.es/oficina_censo/">Oficina del Censo Electoral del INE</a>, que expone el censo antes de cada elección para consultas y reclamaciones.')]
    faq_html, faq_ld = faq(qs)
    h = [cabeza(titulo, desc, ruta, [ld_pagina(titulo, desc, ruta, ESPANA), faq_ld], 2, 'Censo electoral 2026', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Elecciones generales del 29N</p><h1 data-miga="Censo electoral 2026">Censo electoral de las generales de 2026</h1>')
    h.append('<p class="subtitulo">Cuántos electores pueden votar el 29N en cada provincia, comunidad y municipio, y cuánto ha cambiado el censo desde 2023</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    h.append(f'<p class="resumen">{tipo("Dato")}Para las elecciones generales del 29 de noviembre de 2026 hay {num(total)} electores, {num(d)} más que en las de julio de 2023 '
             f'({variacion(total, t23)}). {num(cer)} viven en España y {num(cera)} en el extranjero, el {pct(cera / total)} del censo; '
             f'los del extranjero han crecido un {variacion(c.cera_2026.sum(), c.cera_2023.sum())[1:]}, y los residentes, un {variacion(cer, c.cer_2023.sum())[1:]}.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Abrir el mapa electoral calle a calle</a> <a class="vermapa" href="{CENSO_INE}">Datos del INE</a></p>')
    # provincias
    P = c.groupby('prov')[['cer_2023', 'cera_2023', 'cer_2026', 'cera_2026', 't23', 't26']].sum()
    P['v'] = P.t26 / P.t23 - 1
    P['ce'] = P.cera_2026 / P.t26
    sube, baja = P.v.nlargest(4), P[P.v < 0].v.sort_values()
    lista = lambda ser: ', '.join(f'{escape(PROV_NOMBRE[p])} ({variacion(P.t26[p], P.t23[p])})' for p in ser.index)
    color = lambda v: next(col for tope, col, _ in RAMPA_CENSO if v < tope)
    h.append('<h2>Provincia a provincia</h2>'
             + p_('Dato', f'El censo crece más en {lista(sube)}. '
                  + (f'Solo pierde electores en {num(len(baja))} provincias: {lista(baja)}.' if len(baja) else 'No baja en ninguna provincia.'))
             + figura(MS.mapa({p: color(v) for p, v in P.v.items()}, 'Cambio del censo electoral entre las generales de 2023 y las de 2026, por provincia'),
                      'Variación del número de electores, residentes en España y en el extranjero, entre el censo de 2023 y el de 2026. Canarias, en el recuadro. Fuente: INE.',
                      [(col, et) for _, col, et in RAMPA_CENSO])
             + p_('Dato', 'Donde más pesan los electores que viven en el extranjero es en ' + ', '.join(f'{escape(PROV_NOMBRE[p])} ({pct(P.ce[p])})' for p in P.ce.nlargest(5).index)
                  + '.'))
    filas = [[f'<a href="../../{ruta_provincia(p)}#censo">{escape(PROV_NOMBRE[p])}</a>', num(r.cer_2026), num(r.cera_2026), num(r.t26), variacion(r.t26, r.t23),
              num(round(r.t26 / ESCANOS_2026[p], -2))] for p, r in sorted(P.iterrows(), key=lambda x: -x[1].t26)]
    h.append(tabla('Censo electoral de las generales de 2026 por provincia', ['Provincia', 'Residentes en España', 'En el extranjero', 'Total', 'Cambio desde 2023', 'Electores por diputado'], filas))
    # comunidades
    filas = []
    for slug_c, (nombre, _, provs) in CCAA.items():
        q = P.loc[[p for p in provs if p in P.index]].sum()
        filas.append([f'<a href="../{slug_c}/#censo">{escape(nombre)}</a>', num(q.t26), variacion(q.t26, q.t23)])
    h.append('<h2>Por comunidad autónoma</h2>' + tabla('Censo electoral de las generales de 2026 por comunidad autónoma', ['Comunidad', 'Electores', 'Cambio desde 2023'], filas))
    # municipios
    m = c.rename(index=lambda x: SEGREGADOS.get(x, x)).groupby(level=0)[['t23', 't26']].sum()
    m = m[m.t23 >= 10000]
    m['v'] = m.t26 / m.t23 - 1
    nom = T.MUN.set_index('mun_code').municipio
    enl = lambda x: f'<a href="../../{CIUDADES[x]}#censo">{escape(nom[x])}</a>' if x in CIUDADES else escape(nom.get(x, x))
    fila = lambda x: [enl(x), num(m.t23[x]), num(m.t26[x]), variacion(m.t26[x], m.t23[x])]
    cab = ['Municipio', 'Electores 2023', 'Electores 2026', 'Cambio']
    baja = c[c.t26 < c.t23]
    h.append('<h2>Municipio a municipio</h2>'
             + p_('Dato', f'De los {num(len(c))} municipios, el censo baja en {num(len(baja))}; el {pct((baja.t23 < 1000).mean(), 0)} de ellos tenía menos de 1.000 electores en 2023. '
                  f'Entre los de más de 10.000 electores, el que más crece es {escape(nom[m.v.idxmax()])} ({variacion(m.t26[m.v.idxmax()], m.t23[m.v.idxmax()])}). '
                  'Cada municipio de más de 1.000 habitantes tiene su censo en su propia página.')
             + tabla('Municipios de más de 10.000 electores donde más crece el censo entre 2023 y 2026', cab, [fila(x) for x in m.v.nlargest(10).index])
             + tabla('Municipios de más de 10.000 electores donde más baja el censo entre 2023 y 2026', cab, [fila(x) for x in m.v.nsmallest(10).index])
             + '<p class="leyenda">Galdakao y Usansolo, que se separó de él después de 2023, se comparan juntos.</p>')
    h.append('<p class="leyenda">Fuente: INE, Oficina del Censo Electoral, censo de consulta de las '
             f'<a href="{CENSO_INE}">generales de 2026</a> y de 2023, por municipio. Es el censo que se expone para consultas y reclamaciones antes de la votación; '
             'el definitivo puede variar ligeramente. Electores por diputado: censo total entre los diputados que elige cada provincia el 29N.</p>')
    h.append(faq_html)
    h.append('<h2>Más datos</h2><ul>'
             f'<li><a href="{raiz}actualidad/censo-electoral-desde-1977/">El censo electoral desde 1977</a></li>'
             f'<li><a href="{raiz}actualidad/pensiones-censo-mayores-29n/">Electores de 65 años o más frente a los de 18 a 34, provincia a provincia</a></li>'
             '<li><a href="../elecciones-29n-2026/">Elecciones generales del 29N de 2026: escaños por provincia</a></li>'
             '<li><a href="../participacion-electoral-por-barrio/">Participación electoral por barrio</a></li>'
             '<li><a href="../resultados-elecciones-por-municipio/">Resultados de las elecciones por municipio desde 1977</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def tema_resultados(resumen):
    """Página fija para «resultados elecciones generales 2026»: hoy, el resultado de 2023 como punto de partida;
    la noche del 29N, el escrutinio en directo (mapa insertado de insertar/, que lee el directo de la portada)."""
    ruta = 'elecciones/resultados-elecciones-generales-2026/'
    titulo = 'Resultados de las elecciones generales 2026 (29N): escrutinio en directo y resultados de 2023 por provincia'
    desc = ('Resultados de las elecciones generales del 29 de noviembre de 2026: el escrutinio en directo en el mapa, provincia a provincia y barrio a barrio, '
            'y el resultado de 2023, el punto de partida de cada partido.')
    pt = SIS['partidos']
    e = T.ESPANA
    pc = lambda v: f'{v:.1f}'.replace('.', ',') + ' %'   # % de Interior, con el voto CERA, como en la tabla de escaños
    qs = [('¿Cuándo se conocen los resultados de las elecciones del 29N?',
           'La noche del domingo 29 de noviembre de 2026. Los colegios cierran a las 20.00, hora de cada lugar (las 21.00 en la Península cuando cierran en Canarias), '
           'y el Ministerio del Interior publica el escrutinio provisional a medida que se cuentan las mesas. Esta página y el mapa lo muestran en directo.'),
          ('¿Cuántos escaños hacen falta para gobernar?',
           'La mayoría absoluta del Congreso es de 176 de los 350 diputados. Es la que necesita un candidato en la primera votación de investidura; en la segunda le basta con más síes que noes.'),
          ('¿Quién ganó las elecciones generales de 2023?',
           f'El PP fue el partido más votado el 23 de julio de 2023, con {num(pt[0]["escanos"])} diputados; el PSOE obtuvo {num(pt[1]["escanos"])}. '
           'Pedro Sánchez (PSOE) fue investido presidente en noviembre de 2023 con el apoyo de Sumar, ERC, Junts, EH Bildu, PNV, BNG y Coalición Canaria.'),
          ('¿A qué hora se sabe quién ha ganado?',
           'Depende de lo ajustado que sea. Los primeros datos del escrutinio llegan poco después del cierre de los colegios y, en las últimas generales, el reparto de escaños '
           'estaba claro antes de medianoche. Durante el día, el Ministerio del Interior publica avances de participación, habitualmente a las 14.00 y a las 18.00.'),
          ('¿Cuántos electores pueden votar el 29N?',
           f'{num(38728356)}, según el censo de consulta del INE: los residentes en España y los españoles que viven en el extranjero. '
           'Por provincia y municipio, en el <a href="../censo-electoral-2026/">censo electoral de 2026</a>.'),
          ('¿Cómo se reparten los escaños?',
           'En cada provincia, con la regla D\'Hondt entre las candidaturas que superan el 3 % de los votos válidos de esa provincia. Ceuta y Melilla eligen un diputado cada una, '
           'que gana la lista más votada. Cada provincia tiene un mínimo de dos diputados; el resto se reparte por población. '
           'Cuántos diputados elige cada una, en <a href="../elecciones-29n-2026/#escanos">escaños por provincia</a>.'),
          ('¿Qué pasa si ningún partido tiene mayoría absoluta?',
           'El Rey propone un candidato tras consultar a los grupos, y el Congreso vota su investidura: en la primera votación necesita mayoría absoluta (176) y, '
           'en la segunda, más síes que noes. Si en dos meses desde la primera votación ningún candidato es investido, las Cortes se disuelven y se repiten las elecciones '
           '(artículo 99 de la Constitución).'),
          ('¿Cuándo son definitivos los resultados?',
           'Los de la noche electoral son provisionales. El escrutinio general lo hacen las juntas electorales provinciales desde el tercer día después de la votación, '
           'y en él se suma el voto de los españoles que viven en el extranjero, que puede cambiar algún escaño ajustado. Después se proclaman los electos.'),
          ('¿Hasta cuándo se pueden publicar encuestas?',
           'La ley electoral prohíbe publicar o difundir sondeos electorales en los cinco días anteriores a la votación, del martes 24 al sábado 28 de noviembre. '
           'Mapa Electoral no publica encuestas ni estimaciones: solo resultados oficiales.'),
          ('¿Dónde veo los resultados de mi municipio o de mi barrio?',
           'En el mapa de Mapa Electoral: escribe tu calle y número en el buscador. Cada provincia y cada municipio de más de 1.000 habitantes tiene además su página, '
           'con los resultados desde 1977, enlazada en la tabla de esta página.')]
    faq_html, faq_ld = faq(qs)
    ld = ld_pagina(titulo, desc, ruta, ESPANA)
    h = [cabeza(titulo, desc, ruta, [ld, faq_ld], 2, 'Resultados 29N', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Elecciones generales · 29 de noviembre de 2026</p><h1 data-miga="Resultados 29N">Resultados de las elecciones generales del 29N</h1>')
    h.append('<p class="subtitulo">El escrutinio en directo la noche electoral y, hasta entonces, el resultado de 2023 provincia a provincia</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    h.append(f'<p class="resumen">{tipo("Dato")}Las elecciones generales se celebran el domingo 29 de noviembre de 2026. Esa noche, en cuanto el Ministerio del Interior '
             'empiece a publicar el escrutinio, esta página y el mapa mostrarán los votos y los escaños en directo, en toda España y en cada provincia, municipio y barrio. '
             f'Hasta entonces, recogen el resultado de las generales del 23 de julio de 2023: el PP fue el más votado, con el {pc(pt[0]["pct"])} del voto válido y {num(pt[0]["escanos"])} diputados, '
             f'y el PSOE el segundo, con el {pc(pt[1]["pct"])} y {num(pt[1]["escanos"])}. La mayoría absoluta es de 176 escaños.</p>')
    h.append('<h2 id="directo">El mapa, en directo la noche del 29N</h2>'
             + p_('Dato', 'El mapa muestra hoy el partido más votado en cada sección censal en 2023. La noche electoral cambiará al recuento del 29N a medida que llegue. '
                  'Busca tu calle o tu municipio, o elige otra elección en el desplegable.')
             + f'<iframe class="mapa-vivo" src="{raiz}insertar/" title="Mapa electoral de España: resultados por sección censal" loading="lazy" '
               'style="width:100%;height:640px;border:1px solid #ddd;border-radius:6px"></iframe>'
             + f'<p><a class="vermapa" href="{raiz}">Abrir el mapa a pantalla completa</a></p>')
    h.append('<h2 id="escanos">Escaños de cada partido en 2023</h2>'
             + p_('Dato', 'Votos y diputados de cada candidatura en las generales de 2023, y los que tendría con los mismos votos y el reparto de 2026, '
                  'en el que Madrid gana un diputado y Cádiz lo pierde.')
             + tabla('Votos y escaños de cada partido en las generales de 2023', ['Partido', 'Votos', '% del voto válido', 'Escaños', 'Con el reparto de 2026'],
                     [[escape(x['partido']), num(x['votos']), f'{x["pct"]:.1f}'.replace('.', ',') + ' %', str(x['escanos']), str(R26.get(x['partido'], 0))] for x in pt if x['escanos']])
             + '<p class="leyenda">Fuente: Ministerio del Interior.</p>')
    h.append(bloque_resultado('España', e))
    rp = {p: r_prov(p) for p in ESCANOS_2026}
    gp = {p: T.ganador(r) for p, r in rp.items()}
    filas = []
    for p in sorted(ESCANOS_2026, key=lambda p: PROV_NOMBRE[p]):
        r = rp[p]
        orden = sorted((c for c in T.FAM if c != 'OTROS'), key=lambda c: -(r['pct'][c] or 0))
        esc = SIS['provincias'][p]['esc']
        filas.append([f'<a href="../../{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a>', str(ESCANOS_2026[p]),
                      f'{escape(T.NOMBRE[orden[0]])} {pct(r["pct"][orden[0]])}', f'{escape(T.NOMBRE[orden[1]])} {pct(r["pct"][orden[1]])}',
                      ' · '.join(f'{escape(k)} {v}' for k, v in sorted(esc.items(), key=lambda kv: -kv[1])), pct(r['part'])])
    h.append('<h2 id="provincias">Resultados por provincia</h2>'
             + p_('Dato', 'Partido más votado, segundo y reparto de escaños de cada circunscripción en 2023, y diputados que elige el 29N. '
                  'Cada provincia enlaza a su página, con el voto por municipio y por barrio desde 1977.')
             + figura(MS.mapa({p: T.COLOR[g] for p, g in gp.items()}, 'Partido más votado en cada provincia en las generales de 2023 y diputados que elige en 2026',
                              etiquetas=ESCANOS_2026),
                      'Partido más votado en cada provincia en las generales del 23 de julio de 2023, sin voto desde el extranjero, y diputados que elige cada una el 29N. '
                      'Canarias, en el recuadro. Fuente: Ministerio del Interior.', leyenda_partidos(gp.values()))
             + tabla('Resultados de las generales de 2023 por provincia', ['Provincia', 'Diputados 2026', 'Más votado 2023', 'Segundo', 'Reparto en 2023', 'Participación'], filas))
    filas = [fila_resumen(f'<a href="../{s}/">{escape(i["nombre"])}</a>', i['r']) for s, i in resumen.items()]
    h.append('<h2 id="comunidades">Resultados por comunidad autónoma</h2>' + tabla('Generales de 2023 por comunidad autónoma', ['Comunidad', 'Participación', 'Más votado', 'Segundo'], filas))
    h.append(faq_html)
    h.append('<h2>Más datos</h2><ul><li><a href="../elecciones-29n-2026/">Elecciones del 29N: fecha, campaña y escaños por provincia</a></li>'
             '<li><a href="../resultados-elecciones-por-municipio/">Resultados de las elecciones por municipio desde 1977</a></li>'
             '<li><a href="../censo-electoral-2026/">Censo electoral de 2026 por provincia y municipio</a></li>'
             '<li><a href="../votar-29n/">Dónde y cómo votar el 29N: colegio, voto por correo y plazos</a></li>'
             '<li><a href="../como-se-vota/">Cómo se vota: el precio de un escaño</a></li>'
             '<li><a href="../participacion-electoral-por-barrio/">Participación electoral por barrio</a></li></ul>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def tema_municipios(resumen):
    ruta = 'elecciones/resultados-elecciones-por-municipio/'
    titulo = 'Resultados de las elecciones generales por municipio: cómo votó cada pueblo y ciudad de España desde 1977'
    desc = (f'Resultados de las 16 elecciones generales desde 1977 en los {num(len(T.MUN))} municipios de España: mapas de quién ganó en cada uno, '
            f'los que cambiaron de color en 2023, los que siempre votan igual y páginas propias para los {num(len(CIUDADES))} de más de 1.000 habitantes.')
    gana = T.MUN['2023_07_gana'].dropna()
    cuenta = gana.value_counts()
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA), 2, 'Resultados por municipio', imagen_og(ruta))]
    raiz = RAIZ_REL
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Elecciones')]))
    h.append('<p class="kicker">Tema · Generales 1977-2023</p><h1 data-miga="Resultados por municipio">Resultados de las elecciones por municipio</h1>')
    h.append('<p class="subtitulo">Quién ganó en cada pueblo y ciudad de España, cómo ha cambiado desde 1977 y dónde consultar el voto de cada barrio</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(foto_html(ruta, raiz))
    top = [c for c in cuenta.index if c not in ('PP', 'PSOE')][:3]
    h.append(f'<p class="resumen">{tipo("Dato")}En las generales de 2023 el PP fue la lista más votada en {num(cuenta.get("PP", 0))} de los {num(len(gana))} municipios de España, '
             f'y el PSOE, en {num(cuenta.get("PSOE", 0))}. ' + ', '.join(f'{T.NOMBRE[c]}, en {num(cuenta[c])}' for c in top) + '. '
             f'Los {num(len(CIUDADES))} municipios de más de 1.000 habitantes tienen página propia con las 16 generales desde 1977 y el voto de cada sección censal.</p>')
    h.append(f'<p><a class="vermapa" href="{raiz}">Buscar un municipio en el mapa</a></p>')
    gm = T.MUN.set_index('mun_code')['2023_07_gana'].dropna()
    img = svg_fichero('ganador-municipios-2023.svg', MS.mapa({c: T.COLOR[v] for c, v in gm.items() if v in T.COLOR},
                                                            'Partido más votado en cada municipio en las generales de 2023', 'mun', xmlns=True))
    h.append('<h2>El mapa de 2023, municipio a municipio</h2>'
             + p_('Dato', 'Cada municipio, del color del partido más votado en las generales del 23 de julio de 2023. La mayoría de los municipios son pequeños: '
                  'el mapa pesa más el campo que las ciudades, donde vive la mayor parte del censo.')
             + figura(f'<img class="mapa" src="{img}" alt="Mapa de España con el partido más votado en cada uno de sus {num(len(gm))} municipios en las generales de 2023" width="800" loading="lazy">',
                      'Partido más votado en cada municipio, generales de 2023. Canarias, en el recuadro. Fuente: Ministerio del Interior.', leyenda_partidos(gm.unique())))
    g19 = T.MUN.set_index('mun_code')['2019_11_gana']
    cambio = gm[(g19.reindex(gm.index) != gm) & g19.reindex(gm.index).notna()]
    trans = cambio.groupby([g19.reindex(cambio.index), cambio]).size().sort_values(ascending=False)
    img2 = svg_fichero('cambio-ganador-2019-2023.svg', MS.mapa({c: T.COLOR[v] for c, v in cambio.items() if v in T.COLOR},
                                                              'Municipios donde cambió el partido más votado entre noviembre de 2019 y 2023', 'mun', xmlns=True))
    h.append('<h2>Los que cambiaron de color en 2023</h2>'
             + p_('Dato', f'En {num(len(cambio))} municipios el partido más votado en 2023 no fue el de noviembre de 2019. Los cambios más frecuentes: '
                  + '; '.join(f'de {T.NOMBRE[a]} a {T.NOMBRE[b]}, en {num(n)}' for (a, b), n in trans.head(4).items()) + '.')
             + figura(f'<img class="mapa" src="{img2}" alt="Mapa de España con los municipios donde cambió el partido más votado entre 2019 y 2023" width="800" loading="lazy">',
                      'Municipios donde cambió el partido más votado entre las generales de noviembre de 2019 y las de 2023, del color del ganador de 2023; en gris, los que no cambiaron. Fuente: Ministerio del Interior.',
                      leyenda_partidos(cambio.unique()) + [('#e4e4e4', 'Sin cambio')]))
    # siempre el mismo ganador
    cols = [f'{y}_gana' for y in T.GENERALES]
    G = T.MUN.set_index('mun_code')[cols]
    completos = G.dropna()
    fieles = completos[completos.nunique(axis=1) == 1].iloc[:, 0].value_counts()
    h.append('<h2>Los que siempre votan igual</h2>'
             + p_('Dato', f'De los {num(len(completos))} municipios con resultado en las 16 generales, {num(int(fieles.sum()))} han votado siempre como primera fuerza a la misma familia política: '
                  + ', '.join(f'{num(int(n))} a {T.NOMBRE[c]}' for c, n in fieles.items()) + '. '
                  f'Los municipios que nunca han dado la victoria al PSOE o a la derecha estatal están en <a href="{raiz}actualidad/nunca-gano-el-psoe/">dónde nunca ha ganado el PSOE</a> y '
                  f'<a href="{raiz}actualidad/nunca-gano-la-derecha/">dónde nunca ha ganado la derecha</a>.'))
    # los mayores municipios ganados por cada partido
    pob = T.MUN.set_index('mun_code').poblacion
    nom = T.MUN.set_index('mun_code').municipio
    li = []
    for c in [c for c in cuenta.index if c != 'OTROS'][:8]:
        cs = sorted(gm[gm == c].index, key=lambda x: -pob.get(x, 0))[:3]
        enl = ', '.join(f'<a href="../../{CIUDADES[x]}">{escape(nom[x])}</a>' if x in CIUDADES else escape(nom[x]) for x in cs)
        li.append(f'<li><b>{escape(T.NOMBRE[c])}</b> ({num(int(cuenta[c]))} municipios): {enl}</li>')
    h.append('<h2>Los municipios más poblados que ganó cada partido</h2>'
             + p_('Dato', 'Para cada partido, el número de municipios donde fue el más votado en 2023 y los tres más poblados de ellos.') + '<ul>' + ''.join(li) + '</ul>')
    h.append('<h2>Cómo encontrar tu municipio</h2><ol>'
             '<li>Escribe el nombre del municipio, o tu calle, en el buscador del mapa: verás el resultado de cada sección y, al pulsar, la ficha del municipio.</li>'
             '<li>O entra en su provincia en la tabla de abajo: cada página de provincia lista sus municipios de más de 1.000 habitantes, con enlace a la página de cada uno.</li>'
             '<li>En la página de cada municipio están el resultado de 2023, la serie desde 1977, las municipales frente a las generales y, si tiene más de una sección, el voto barrio a barrio.</li></ol>')
    filas = []
    for p in sorted(PROV_NOMBRE, key=lambda p: slug(PROV_NOMBRE[p])):
        g = T.MUN[T.MUN.prov == p]['2023_07_gana'].dropna().value_counts()
        filas.append([f'<a href="../../{ruta_provincia(p)}">{escape(PROV_NOMBRE[p])}</a>', num(int((T.MUN.prov == p).sum())),
                      num(sum(1 for c in CIUDADES if c[:2] == p)), num(int(g.get('PP', 0))), num(int(g.get('PSOE', 0))), num(int(g.sum() - g.get('PP', 0) - g.get('PSOE', 0)))])
    h.append('<h2>Municipios por provincia</h2>'
             + p_('Dato', 'Número de municipios de cada provincia, cuántos tienen página propia (más de 1.000 habitantes o capital) y en cuántos fue la lista más votada cada partido en 2023.')
             + tabla('Municipios por provincia y partido más votado en las generales de 2023', ['Provincia', 'Municipios', 'Con página', 'Ganó el PP', 'Ganó el PSOE', 'Ganó otro'], filas))
    h.append('<h2>Piezas municipio a municipio</h2>' + lista_piezas(TEMA_MUNICIPIOS, 2)
             + f'<ul class="sigue"><li><a href="{raiz}atlas/"><span class="kicker">Atlas</span><b>Atlas de las anomalías electorales: los municipios que votan distinto de lo esperado</b></a></li></ul>')
    h.append('<h2>Más datos</h2><ul><li><a href="../elecciones-29n-2026/">Elecciones generales del 29N de 2026</a></li>'
             '<li><a href="../participacion-electoral-por-barrio/">Participación electoral por barrio</a></li>'
             '<li><a href="../mapa-electoral-seccion-censal/">Mapa electoral de España por sección censal</a></li></ul>')
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
    bar = '\n'.join(f'- [Barrios de {_nom(c)}]({BASE}{CIUDADES[c]}#barrios): {num(sum(b["ficha"] for b in bs))} fichas de barrio con el voto de cada sección censal, renta, edad y población extranjera.'
                     for c, bs in BARRIOS.items() if any(b['ficha'] for b in bs))
    return f"""# Elecciones en España por comunidad, provincia y sección censal

> Páginas de entrada de Mapa Electoral: una por comunidad autónoma y por provincia con el resultado de las generales de 2023, la serie de las 16 elecciones al Congreso desde 1977, el voto por renta de las secciones censales y los municipios principales. Más páginas temáticas: el 29N, resultados por municipio, participación por barrio, sección censal y renta. Autor: {esquema.FIRMA}. Datos: Ministerio del Interior e INE, licencia CC BY 4.0.

## Temas
- [Elecciones generales del 29N de 2026: fecha, campaña y diputados por provincia]({BASE}elecciones/elecciones-29n-2026/)
- [Resultados de las elecciones generales de 2026 (29N): escrutinio en directo y resultados de 2023 por provincia]({BASE}elecciones/resultados-elecciones-generales-2026/)
- [Resultados de las elecciones generales por municipio desde 1977]({BASE}elecciones/resultados-elecciones-por-municipio/)
- [Censo electoral de las generales de 2026 por provincia y municipio]({BASE}elecciones/censo-electoral-2026/)
- [Participación electoral por barrio]({BASE}elecciones/participacion-electoral-por-barrio/)
- [Mapa electoral de España por sección censal]({BASE}elecciones/mapa-electoral-seccion-censal/)
- [Voto y renta por barrios]({BASE}elecciones/voto-y-renta-por-barrios/)

## Comunidades autónomas
{li}

## Barrios de las grandes ciudades
{bar}
"""


def franja_portada():
    """Bloque de la portada con enlaces a las páginas por territorio y por tema (anclas descriptivas)."""
    ccaa = ' · '.join(f'<a href="elecciones/{c}/">{escape(n)}</a>' for c, (n, _, _) in CCAA.items())
    return ('<section class="col explora" aria-labelledby="h-explora"><h2 id="h-explora">Elecciones por comunidad y provincia</h2>'
            '<p>Resultados de las 16 generales desde 1977, voto por renta de los barrios y municipios principales de cada territorio: ' + ccaa + '. '
            '<a href="elecciones/">Todas las provincias</a>.</p>'
            '<p>Por tema: <a href="elecciones/elecciones-29n-2026/">elecciones generales del 29N de 2026</a> · '
            '<a href="elecciones/resultados-elecciones-generales-2026/">resultados de las elecciones generales de 2026</a> · '
            '<a href="elecciones/resultados-elecciones-por-municipio/">resultados de las elecciones por municipio</a> · '
            '<a href="elecciones/censo-electoral-2026/">censo electoral de 2026</a> · '
            '<a href="elecciones/participacion-electoral-por-barrio/">participación electoral por barrio</a> · '
            '<a href="elecciones/voto-y-renta-por-barrios/">voto y renta por barrios</a> · '
            '<a href="elecciones/mapa-electoral-seccion-censal/">mapa electoral por sección censal</a> · '
            '<a href="abstencion.html">participación por sección censal en Cataluña</a> · '
            '<a href="atlas/">anomalías electorales municipio a municipio</a></p></section>')


# Guías temáticas de elecciones/, en tarjetas en la portada, debajo de Actualidad
GUIAS = [('elecciones-29n-2026/', 'img/elecciones/congreso-urna-calendario-29n.jpg', '29N', 'Elecciones del 29N: fecha, campaña y escaños por provincia'),
         ('resultados-elecciones-por-municipio/', 'img/elecciones/libros-plazas-y-arquitectura-de-espana.jpg', 'Municipios', 'Cómo votó cada pueblo y ciudad de España desde 1977'),
         ('participacion-electoral-por-barrio/', 'img/elecciones/colegio-electoral-cola-y-bloques.jpg', 'Participación', 'Dónde se vota más y dónde menos, barrio a barrio'),
         ('censo-electoral-2026/', 'img/elecciones/listas-censo-sobre-pasaporte.jpg', 'Censo', 'Cuántos electores votan el 29N en cada provincia y municipio'),
         ('voto-y-renta-por-barrios/', 'img/elecciones/urna-entre-bloques-y-chalets.jpg', 'Renta', 'Cómo vota cada barrio según su renta'),
         ('mapa-electoral-seccion-censal/', 'img/elecciones/plano-secciones-lupa.jpg', 'Sección censal', 'El mapa electoral calle a calle: qué es una sección censal')]


# texto alternativo de las ilustraciones de las guías (describen la imagen, no repiten el titular)
ALT_GUIAS = {'elecciones-29n-2026/': 'Urna ante el Congreso de los Diputados con un calendario marcado en el 29 de noviembre',
             'resultados-elecciones-por-municipio/': 'Plazas, calles y edificios de pueblos y ciudades de España',
             'participacion-electoral-por-barrio/': 'Cola de votantes ante un colegio electoral entre bloques de pisos',
             'censo-electoral-2026/': 'Listas del censo electoral, un sobre de votación y un pasaporte',
             'voto-y-renta-por-barrios/': 'Urna entre bloques de pisos y chalets',
             'mapa-electoral-seccion-censal/': 'Plano de secciones censales bajo una lupa'}


def guias_portada():
    li = ''.join(f'<li><a href="elecciones/{r}"><img src="{img}" alt="{ALT_GUIAS.get(r, "")}" loading="lazy" width="300" height="200"><span class="atlas-k">{k}</span><b>{titulo}</b></a></li>'
                 for r, img, k, titulo in GUIAS)
    li += '<li class="todas"><a href="elecciones/"><b>Por comunidad y provincia</b><span>Resultados, renta y participación de cada territorio</span></a></li>'
    return ('<section class="wide del-atlas del-guias" aria-labelledby="h-del-guias"><div class="da-cab"><h2 id="h-del-guias"><a href="elecciones/">Guías de las elecciones</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Guías anteriores">←</button><button type="button" class="da-next" aria-label="Más guías">→</button></span></div>'
            f'<ul class="carrusel">{li}</ul></section>')


def portada():
    """Rellena la franja entre <!--territorios--> y las guías entre <!--elecciones:guias--> (debajo de Actualidad)
    en la portada y en la plantilla del mapa (rutas desde generales-2026/)."""
    for f in (ROOT / 'index.html', ROOT / 'generales-2026' / 'src' / 'plantilla.html'):
        t = f.read_text(encoding='utf-8')
        if '<!--territorios-->' not in t:
            t = t.replace('<!--/atlas:ultimas-->', '<!--/atlas:ultimas-->\n<!--territorios--><!--/territorios-->', 1)
        if '<!--elecciones:guias-->' not in t:
            t = t.replace('<!--/actualidad:ultimas-->', '<!--/actualidad:ultimas-->\n<!--elecciones:guias--><!--/elecciones:guias-->', 1)
        pre = '' if f.name == 'index.html' else '../'
        rel = lambda s: re.sub(r'(href|src)="(?!https?:)', lambda m: f'{m.group(1)}="{pre}', s)
        franja = re.sub(r'href="(?!https?:)', 'href="' + pre, franja_portada())
        guias = rel(guias_portada())
        t = re.sub(r'<!--territorios-->.*?<!--/territorios-->', lambda m: '<!--territorios-->' + franja + '<!--/territorios-->', t, flags=re.S)
        t = re.sub(r'<!--elecciones:guias-->.*?<!--/elecciones:guias-->', lambda m: '<!--elecciones:guias-->' + guias + '<!--/elecciones:guias-->', t, flags=re.S)
        f.write_text(t, encoding='utf-8')


# ---------- índices de municipios (/municipio/) ----------
def _nom(c):
    return T.MUN.loc[T.MUN.mun_code == c, 'municipio'].iloc[0]


def fila_municipio(c, raiz):
    m = T.MUN[T.MUN.mun_code == c].iloc[0]
    g = m['2023_07_gana']
    gana = (f'<span style="color:{T.COLOR[g]}">■</span> {escape(T.NOMBRE[g])} ({pct(m[f"2023_07_{g}"])})'
            if isinstance(g, str) and g in T.COLOR and pd.notna(m.get(f'2023_07_{g}')) else '—')
    part = pct(m['2023_07_part']) if pd.notna(m['2023_07_part']) else '—'
    return [f'<a href="{raiz}{CIUDADES[c]}">{escape(m.municipio)}</a>', num(m.poblacion), gana, part]


def buscador_html(ejemplo='Getafe o Lavapiés'):
    """Buscador de municipios y barrios con ficha; carga municipio/buscador.json (src/pagina_404.py) al primer uso."""
    return ('<form class="busca-mun" role="search" onsubmit="return false"><label for="bq">Busca tu municipio o tu barrio</label>'
            f'<input id="bq" type="search" autocomplete="off" placeholder="Por ejemplo, {ejemplo}" aria-controls="bres">'
            '<ul id="bres" aria-live="polite"></ul><p id="bvacio" hidden>No hay ningún municipio ni barrio con ficha con ese nombre.</p></form>'
            '<style>.busca-mun{margin:1.2rem 0 1.6rem;font-family:var(--sans,system-ui)}.busca-mun label{display:block;font-weight:600;font-size:15px;margin-bottom:6px}'
            '.busca-mun input{width:100%;box-sizing:border-box;font:17px var(--sans,system-ui);padding:11px 13px;border:1.5px solid var(--rule);border-radius:6px;background:var(--surface,#fff);color:var(--fg)}'
            '.busca-mun input:focus{outline:none;border-color:var(--accent)}.busca-mun ul{list-style:none;margin:6px 0 0;padding:0}'
            '.busca-mun li a{display:flex;justify-content:space-between;gap:12px;padding:8px 12px;border-bottom:1px solid var(--rule);text-decoration:none;color:var(--fg);font-size:16px}'
            '.busca-mun li a:hover,.busca-mun li a:focus{color:var(--accent)}.busca-mun li span{color:var(--muted);font-size:14px}.busca-mun p{color:var(--muted);font-size:15px}</style>'
            '<script>(()=>{const norm=s=>s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/[^a-z0-9]+/g," ").trim();'
            'let d=null,c=null;const carga=()=>c||(c=fetch("/municipio/buscador.json").then(r=>r.json()).then(x=>d=x.map(y=>[y,norm(y[0])])));'
            'const q=document.getElementById("bq"),res=document.getElementById("bres"),v=document.getElementById("bvacio");'
            'const busca=t=>{t=norm(t);if(!t||!d)return[];const a=[],b=[];for(const[x,n]of d){if(n.startsWith(t))a.push(x);else if(n.includes(" "+t)||(t.length>3&&n.includes(t)))b.push(x)}'
            'const o=(p,r)=>p[3]-r[3]||p[0].length-r[0].length;return a.sort(o).concat(b.sort(o)).slice(0,10)};'
            'const pinta=()=>{const r=busca(q.value);res.replaceChildren(...r.map(x=>{const li=document.createElement("li"),a=document.createElement("a"),s=document.createElement("span");'
            'a.href=x[2];a.textContent=x[0];s.textContent=x[3]?"barrio de "+x[1]:x[1];a.append(s);li.append(a);return li}));v.hidden=!(q.value.trim().length>1&&!r.length)};'
            'q.addEventListener("focus",carga,{once:true});q.addEventListener("input",()=>carga().then(pinta));})()</script>')


def municipios_indice():
    ruta = 'municipio/'
    titulo = 'Elecciones por municipio: resultados de cada pueblo y ciudad de España desde 1977'
    desc = (f'Una página por cada uno de los {num(len(CIUDADES))} municipios de más de 1.000 habitantes y por cada capital: '
            'resultados por sección censal, voto por renta y las 16 elecciones generales desde 1977, provincia a provincia.')
    provs = sorted({c[:2] for c in CIUDADES}, key=lambda p: PROV_SLUG[p])
    partes = [{'@type': 'CollectionPage', 'name': f'Municipios de {PROV_NOMBRE[p]}', 'url': BASE + f'municipio/{PROV_SLUG[p]}/'} for p in provs]
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, ESPANA, partes), 1, 'Municipios')]
    h.append(migas_html([('../', 'Inicio')]))
    h.append('<p class="kicker">Elecciones generales 1977-2023</p><h1 data-miga="Municipios">Elecciones por municipio</h1>')
    h.append(f'<p class="firma">Por <a href="../sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    pob = T.MUN.set_index('mun_code').poblacion
    h.append(f'<p class="resumen">{tipo("Dato")}Los {num(len(CIUDADES))} municipios de España con más de 1.000 habitantes, y las capitales de provincia que no llegan, '
             f'tienen página propia con el resultado de cada sección censal, el voto por renta de sus barrios y las 16 elecciones generales desde 1977. '
             f'Reúnen a {num(pob[list(CIUDADES)].sum())} de los {num(pob.sum())} habitantes de los municipios con datos. '
             'Los demás se consultan en el <a href="../">mapa de la portada</a>.</p>')
    h.append(buscador_html())
    filas = []
    for p in provs:
        cs = [c for c in CIUDADES if c[:2] == p]
        mayor = max(cs, key=lambda c: pob[c])
        filas.append([f'<a href="{PROV_SLUG[p]}/">{escape(PROV_NOMBRE[p])}</a>', num(len(cs)), f'<a href="../{CIUDADES[mayor]}">{escape(_nom(mayor))}</a>'])
    h.append('<h2>Provincia a provincia</h2>' + tabla('Municipios con página propia en cada provincia', ['Provincia', 'Municipios', 'El más poblado'], filas, num_desde=1))
    h.append(f'<p>Las grandes ciudades tienen además una ficha por barrio: <a href="barrios/">elecciones barrio a barrio en {num(sum(1 for bs in BARRIOS.values() if any(b["ficha"] for b in bs)))} ciudades</a>.</p>')
    h.append('<p>Por comunidad y provincia, con la serie completa y el voto por renta: <a href="../elecciones/">elecciones por territorio</a>. '
             'Por tema: <a href="../temas/">renta y voto, participación, historia electoral y más</a>.</p>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def barrios_indice():
    ruta = 'municipio/barrios/'
    cs = sorted((c for c, bs in BARRIOS.items() if any(b['ficha'] for b in bs)), key=lambda c: slug(_nom(c)))
    todas = [(c, b) for c in cs for b in BARRIOS[c] if b['ficha']]
    titulo = f'Elecciones barrio a barrio: {num(len(todas))} barrios de {num(len(cs))} grandes ciudades de España'
    desc = (f'Cómo vota cada barrio de Madrid, Barcelona, València, Sevilla, Málaga y {num(len(cs) - 5)} ciudades más: voto por sección censal, '
            'participación, renta, edad y población extranjera, con ficha propia para cada barrio.')
    partes = [{'@type': 'CollectionPage', 'name': f'Barrios de {_nom(c)}', 'url': BASE + CIUDADES[c] + '#barrios'} for c in cs]
    ld = ld_pagina(titulo, desc, ruta, ESPANA, partes)
    ld['datePublished'] = BARRIOS_PUBLICADO
    ld['dateModified'] = max(ACTUALIZADO, BARRIOS_PUBLICADO)
    h = [cabeza(titulo, desc, ruta, ld, 2, 'Barrios', imagen='img/elecciones/' + FOTO_BARRIO_GENERICA[0])]
    raiz = '../../'
    act = max(ACTUALIZADO, BARRIOS_PUBLICADO)
    h.append(migas_html([(raiz, 'Inicio'), ('../', 'Municipios')]))
    h.append('<p class="kicker">Barrios · Elecciones generales 2004-2023</p><h1 data-miga="Barrios">Elecciones barrio a barrio</h1>')
    h.append('<p class="subtitulo">Una ficha por barrio de las grandes ciudades: cómo vota, quién vive en él y en qué se separa del resto de su ciudad</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{act}">{fecha(act)}</time></p>')
    h.append(foto_barrio(None, raiz))
    con = [(c, b) for c, b in todas if b['r']['censo'] >= 3000]
    alto = sorted(con, key=lambda x: -x[1]['r']['part'])
    enl = lambda c, b: f'<a href="{raiz}{ruta_barrio(c, b)}">{escape(cap(b["nombre"]))}</a> ({escape(_nom(c))}, {pct(b["r"]["part"])})'
    h.append(f'<p class="resumen">{tipo("Dato")}{num(len(todas))} barrios de {num(len(cs))} ciudades tienen ficha propia, con el voto de cada una de sus secciones censales en las generales desde 2004, '
             f'la renta y quién vive en ellos. En las generales de 2023, el barrio que más votó fue {enl(*alto[0])} y el que menos, {enl(*alto[-1])}: '
             f'{puntos(alto[0][1]["r"]["part"] - alto[-1][1]["r"]["part"])} puntos de distancia.</p>')
    h.append(buscador_html('Lavapiés, Gràcia o Triana'))
    h.append('<h2>Ciudad a ciudad</h2>')
    filas = []
    for c in cs:
        fb = [b for b in BARRIOS[c] if b['ficha']]
        rico = max((b for b in fb if b['demo']['renta_uc']), key=lambda b: b['demo']['renta_uc'])
        pobre = min((b for b in fb if b['demo']['renta_uc']), key=lambda b: b['demo']['renta_uc'])
        tipos = 'barrios' if fb[0]['nivel'] == 10 else 'distritos'
        filas.append([f'<a href="{raiz}{CIUDADES[c]}#barrios">{escape(_nom(c))}</a>', f'{num(len(fb))} {tipos}',
                      f'<a href="{raiz}{ruta_barrio(c, rico)}">{escape(cap(rico["nombre"]))}</a> ({euros(rico["demo"]["renta_uc"])})',
                      f'<a href="{raiz}{ruta_barrio(c, pobre)}">{escape(cap(pobre["nombre"]))}</a> ({euros(pobre["demo"]["renta_uc"])})'])
    h.append(tabla('Ciudades con fichas de barrio: el barrio con más y con menos renta neta por unidad de consumo (INE, 2023)',
                   ['Ciudad', 'Fichas', 'Más renta', 'Menos renta'], filas, num_desde=9))
    fila = lambda c, b: [f'<a href="{raiz}{ruta_barrio(c, b)}">{escape(cap(b["nombre"]))}</a>', escape(_nom(c)), pct(b['r']['part']),
                         f'<span style="color:{T.COLOR[T.ganador(b["r"])]}">■</span> {escape(T.NOMBRE[T.ganador(b["r"])])}',
                         euros(b['demo']['renta_uc']) if b['demo']['renta_uc'] else '—']
    cab = ['Barrio', 'Ciudad', 'Participación', 'Más votado', 'Renta por u. c.']
    h.append('<h2>Donde más y donde menos se vota</h2>'
             + p_('Dato', 'Los diez barrios con más participación en las generales de 2023 y los diez con menos, entre los que tienen al menos 3.000 electores.')
             + tabla('Los diez barrios con más participación, generales de 2023', cab, [fila(*x) for x in alto[:10]], num_desde=2)
             + tabla('Los diez barrios con menos participación, generales de 2023', cab, [fila(*x) for x in alto[::-1][:10]], num_desde=2))
    h.append('<h2>Todos los barrios</h2>' + ''.join(
        f'<details><summary>{escape(_nom(c))}: {num(sum(b["ficha"] for b in BARRIOS[c]))} fichas</summary><p>'
        + ' · '.join(f'<a href="{raiz}{ruta_barrio(c, b)}">{escape(cap(b["nombre"]))}</a>' for b in sorted((b for b in BARRIOS[c] if b['ficha']), key=lambda b: slug(b['nombre'])))
        + '</p></details>' for c in cs))
    h.append(f'<p>El resto de municipios, con el voto por sección censal: <a href="../">elecciones por municipio</a>. '
             f'Por tema: <a href="{raiz}elecciones/participacion-electoral-por-barrio/">participación por barrio</a> y <a href="{raiz}elecciones/voto-y-renta-por-barrios/">voto y renta por barrios</a>.</p>')
    global RAIZ_REL
    RAIZ_REL = raiz
    h.append(bloque_metodo_barrio('barrio'))
    h.append(PIE)
    return ruta, ''.join(h)


def municipios_provincia(p):
    ruta = f'municipio/{PROV_SLUG[p]}/'
    pob = T.MUN.set_index('mun_code').poblacion
    cs = sorted((c for c in CIUDADES if c[:2] == p), key=lambda c: -pob[c])
    nombre = PROV_NOMBRE[p]
    en = en_provincia_txt(p)
    titulo = f'Elecciones por municipio {en}: resultados de sus {num(len(cs))} municipios con página propia'
    desc = (f'Resultados de las generales de 2023 y enlaces a la página de cada municipio de más de 1.000 habitantes {en}: '
            'voto por sección censal, por renta y desde 1977.')
    partes = [{'@type': 'WebPage', 'name': f'Elecciones en {_nom(c)}', 'url': BASE + CIUDADES[c]} for c in cs]
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, lugar(nombre, ESPANA), partes), 2, nombre)]
    h.append(migas_html([('../../', 'Inicio'), ('../', 'Municipios')]))
    h.append(f'<p class="kicker">Municipios · Elecciones generales 1977-2023</p><h1 data-miga="{escape(nombre)}">Elecciones por municipio {escape(en)}</h1>')
    h.append(f'<p class="firma">Por <a href="../../sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    df = T.MUN[T.MUN.mun_code.isin(cs)]
    gana = df['2023_07_gana'].value_counts()
    resto = len(T.MUN[T.MUN.prov == p]) - len(cs)
    h.append(f'<p class="resumen">{tipo("Dato")}{"Los " + num(len(cs)) + " municipios" if len(cs) > 1 else "El municipio"} {escape(en)} con página propia, '
             f'del más poblado al menos. En las generales de 2023 el más votado fue '
             + ', '.join(f'{T.NOMBRE[g]} en {num(n)}' for g, n in gana.items() if g in T.NOMBRE) + '. '
             + (f'Los otros {num(resto)} municipios de la provincia, con menos de 1.000 habitantes, se consultan en el <a href="../../?m={cs[0]}">mapa</a>.' if resto > 0 else '')
             + '</p>')
    h.append(tabla(f'Generales de 2023 en cada municipio {escape(en)}', ['Municipio', 'Habitantes', 'Más votado', 'Participación'],
                   [fila_municipio(c, '../../') for c in cs]))
    h.append(f'<p>La provincia entera, con la serie desde 1977 y el voto por renta: <a href="../../{ruta_provincia(p)}">elecciones {escape(en)}</a>.</p>')
    h.append(bloque_metodo())
    h.append(PIE)
    return ruta, ''.join(h)


def en_provincia_txt(p):
    c = PROV_CCAA[p]
    return CCAA[c][1] if len(CCAA[c][2]) == 1 else f'en la provincia de {PROV_NOMBRE[p]}'


REDIRECCION = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Elecciones en {nombre}</title>
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={rel}">
<script>location.replace({rel_js} + location.search + location.hash)</script>
</head>
<body style="font-family:system-ui,sans-serif;padding:16px">
<p>La página de {nombre} se ha movido a <a href="{rel}">{url}</a>.</p>
</body>
</html>
"""


def redirecciones():
    """Páginas en las rutas antiguas de cada municipio que llevan a la nueva."""
    out = []
    for c, nueva in CIUDADES.items():
        m = T.MUN[T.MUN.mun_code == c].iloc[0]
        vieja = ruta_municipio_antigua(m.prov, m.municipio)
        rel = '../' * vieja.count('/') + nueva
        out.append((vieja, REDIRECCION.format(nombre=escape(m.municipio), url=BASE + nueva, rel=rel, rel_js=json.dumps(rel))))
    return out


# ---------- páginas nodales por tema (/temas/) ----------
def descripcion_de(ruta):
    f = ROOT / ruta / 'index.html'
    m = re.search(r'<meta name="description" content="([^"]*)"', f.read_text(encoding='utf-8')) if f.exists() else None
    return m.group(1) if m else ''


def municipios_de_pieza(s):
    """Municipios que cita una pieza de Actualidad publicada (su bloque «Ver datos de estos municipios»)."""
    f = ROOT / 'actualidad' / s / 'index.html'
    if not f.exists():
        return []
    b = re.search(r'<aside class="municipios-pieza">.*?</aside>', f.read_text(encoding='utf-8'), re.S)
    return re.findall(r'data-mun="(\d{5})"', b.group(0)) if b else []


def tema_hub(t, d):
    ruta = f'temas/{t}/'
    raiz = '../../'
    slugs = [s for s in dict.fromkeys(d['piezas']) if h1_de(f'actualidad/{s}')]
    piezas_ = sorted(((publicada(s), s) for s in slugs), reverse=True)
    titulo = d['titulo']
    desc = f'{d["intro"].split(":")[0].split(".")[0]}. {num(len(slugs))} piezas de Mapa Electoral, con sus datos y los municipios que analizan.'
    partes = [{'@type': 'NewsArticle', 'headline': h1_de(f'actualidad/{s}'), 'url': BASE + f'actualidad/{s}/'} for _, s in piezas_]
    ld = ld_pagina(titulo, desc, ruta, None, partes)
    ld['@type'] = 'CollectionPage'
    h = [cabeza(titulo, desc, ruta, ld, 2, d['nombre'])]
    h.append(migas_html([(raiz, 'Inicio'), ('../', 'Temas')]))
    h.append(f'<p class="kicker">Tema</p><h1 data-miga="{escape(d["nombre"])}">{escape(d["nombre"])}</h1>')
    h.append(f'<p class="subtitulo">{escape(titulo.split(": ", 1)[-1][0].upper() + titulo.split(": ", 1)[-1][1:])}</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{esquema.FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADO}">{fecha(ACTUALIZADO)}</time></p>')
    h.append(f'<p class="resumen">{escape(d["intro"])}</p>')
    datos = d['datos'] + d['atlas']
    h.append('<h2>Los datos</h2><ul>' + ''.join(f'<li><a href="{raiz}{u}">{escape(n)}</a></li>' for u, n in datos) + '</ul>')
    li = []
    for fch, s in piezas_:
        li.append(f'<li><a href="{raiz}actualidad/{s}/"><span class="kicker">Actualidad{" · " + fecha(fch) if fch else ""}</span>'
                  f'<b>{escape(h1_de(f"actualidad/{s}"))}</b><span class="d">{escape(descripcion_de(f"actualidad/{s}"))}</span></a></li>')
    h.append(f'<h2>Las piezas</h2><ul class="sigue">' + ''.join(li) + '</ul>')
    cuenta = {}
    for s in slugs:
        for c in municipios_de_pieza(s):
            if c in CIUDADES:
                cuenta.setdefault(c, []).append(s)
    if cuenta:
        orden = sorted(cuenta, key=lambda c: (-len(cuenta[c]), slug(_nom(c))))[:40]
        h.append('<h2>Ver datos de estos municipios en el mapa</h2>'
                 f'<p>Los municipios que aparecen en las piezas de este tema{", los más citados primero" if len(orden) > 1 else ""}. Cada uno tiene su página con '
                 'el voto por sección censal, por renta y desde 1977.</p><ul class="cols">'
                 + ''.join(f'<li><a href="{raiz}{CIUDADES[c]}">{escape(_nom(c))}</a> ({escape(PROV_NOMBRE[c[:2]])})'
                           f'{" · " + str(len(cuenta[c])) + " piezas" if len(cuenta[c]) > 1 else ""} · <a href="{raiz}?m={c}">mapa</a></li>' for c in orden)
                 + '</ul>')
    otros = [f'<a href="../{o}/">{escape(TEMAS[o]["nombre"])}</a>' for o in TEMAS if o != t]
    h.append('<h2>Otros temas</h2><p>' + ' · '.join(otros) + '</p>')
    h.append(PIE)
    return ruta, ''.join(h)


def temas_indice():
    ruta = 'temas/'
    titulo = 'Temas: renta y voto, participación, historia electoral, vivienda e inmigración'
    desc = 'Las piezas de Mapa Electoral agrupadas por tema, con las páginas de datos de cada uno y los municipios que analizan.'
    partes = [{'@type': 'CollectionPage', 'name': d['nombre'], 'url': BASE + f'temas/{t}/'} for t, d in TEMAS.items()]
    h = [cabeza(titulo, desc, ruta, ld_pagina(titulo, desc, ruta, None, partes), 1, 'Temas')]
    h.append(migas_html([('../', 'Inicio')]))
    h.append('<p class="kicker">Mapa Electoral</p><h1 data-miga="Temas">Temas</h1>')
    h.append(f'<p class="resumen">{escape(desc)}</p>')
    li = []
    for t, d in TEMAS.items():
        n = sum(1 for s in dict.fromkeys(d['piezas']) if h1_de(f'actualidad/{s}'))
        li.append(f'<li><a href="{t}/"><span class="kicker">{num(n)} piezas</span><b>{escape(d["nombre"])}</b><span class="d">{escape(d["intro"])}</span></a></li>')
    h.append('<ul class="sigue">' + ''.join(li) + '</ul>')
    h.append('<p>Por territorio: <a href="../elecciones/">elecciones por comunidad y provincia</a> · <a href="../municipio/">elecciones por municipio</a>.</p>')
    h.append(PIE)
    return ruta, ''.join(h)


def main():
    pags, resumen = territorios()
    pags += [pagina_ciudad(c) for c in CIUDADES]
    pags += [pagina_barrio(c, b, bs) for c, bs in BARRIOS.items() for b in bs if b['ficha']]
    rutas_b = [(b['nombre'], ruta_barrio(c, b)) for c, bs in BARRIOS.items() for b in bs if b['ficha']]
    idx = {r: k for k, (_, r) in enumerate(rutas_b)}
    (ROOT / 'generales-2026' / 'data' / 'barrios.json').write_text(json.dumps(   # para el enlace «Ver el barrio» de la ficha del mapa
        {'r': rutas_b, 's': {t: idx[ruta_barrio(c, b)] for c, bs in BARRIOS.items() for b in bs if b['ficha'] for t in b['secciones']}},
        ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (ROOT / 'src' / 'ciudades.json').write_text(json.dumps(CIUDADES, ensure_ascii=False, indent=0, sort_keys=True), encoding='utf-8')
    (ROOT / 'src' / 'ciudades_nombres.json').write_text(json.dumps({c: [_nom(c), c[:2]] for c in CIUDADES}, ensure_ascii=False, indent=0, sort_keys=True), encoding='utf-8')
    pags += [indice(resumen), tema_renta(resumen), tema_seccion(resumen), tema_29n(resumen), tema_participacion(resumen), tema_municipios(resumen), tema_censo(resumen), tema_como_se_vota(), tema_votar(), tema_resultados(resumen)]
    pags += [municipios_indice(), barrios_indice()] + [municipios_provincia(p) for p in sorted({c[:2] for c in CIUDADES})]
    pags += [temas_indice()] + [tema_hub(t, d) for t, d in TEMAS.items()]
    for ruta, html in pags + redirecciones():
        f = ROOT / ruta / 'index.html'
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(html, encoding='utf-8')
    for sec in ('elecciones', 'municipio', 'temas'):   # un sitemap por carpeta: solo puede listar URL de su carpeta
        rutas = sorted(r for r, _ in pags if r.startswith(sec + '/'))
        (ROOT / sec / 'sitemap.xml').write_text(sitemap(rutas), encoding='utf-8')
    (OUT / 'llms.txt').write_text(llms(resumen), encoding='utf-8')
    portada()
    esquema.main()
    print(f'territorios: {len(pags)} páginas en elecciones/, municipio/ y temas/')


if __name__ == '__main__':
    main()
