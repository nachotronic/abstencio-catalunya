"""Genera /listas-electorales-29n/: buscador de todos los candidatos al Congreso y al Senado del 29N, con una página
por provincia.

Datos (listas-electorales-29n/datos/):
- <año>-presentadas.json / <año>-proclamadas.json: las candidaturas tal como las publica el BOE (las escribe boe.py).
  Se usan las del 29N en cuanto existen (las proclamadas si ya están, si no las presentadas). Antes del BOE del
  28-10-2026 la sección funciona en modo «avance»: enseña las listas oficiales del 23J de 2023 y lo dice arriba.
- diputados-xv.json: quién tuvo escaño en la legislatura que acaba (lo escribe diputados.py).
- puestos-29n.json: probabilidad de salir elegido de cada puesto de cada lista según el modelo de /encuestas/ (la
  misma simulación de la pieza «Las listas del 29N, puesto a puesto»). Solo se aplica a las listas del 29N.

Escribe index.html, <provincia>/index.html (52), candidatos.json (para el buscador), candidatos-29n.csv y sitemap.xml.

Uso, desde la raíz:  python3 listas-electorales-29n/src/construir.py
"""
import csv, html, importlib.util, json, pathlib, re, sys, unicodedata
from collections import Counter, defaultdict
from datetime import date

sys.dont_write_bytecode = True
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'actualidad' / 'src'))
sys.path.insert(0, str(RAIZ / 'src'))
from construir import AUTOR, BASE, CSS_SITIO, MEDIO, cabecera, fecha_larga, nav  # noqa: E402
from territorios_rutas import CCAA, PROV_CCAA, PROV_NOMBRE, PROV_SLUG, ruta_provincia  # noqa: E402

_spec = importlib.util.spec_from_file_location('encuestas_construir', RAIZ / 'encuestas/src/construir.py')
_enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_enc)
ESTILOS = _enc.ESTILOS

CARPETA = RAIZ / 'listas-electorales-29n'
DATOS = CARPETA / 'datos'
URL = BASE + '/listas-electorales-29n/'
PUBLICADO = '2026-10-27'
# Ilustración de cabecera (ChatGPT, buzón, 27-10-2026) y su recorte 1200x630 para redes; la tarjeta de datos va aparte
ILUSTRACION = dict(src='img/listas/listas-electorales-29n.jpg', ancho=1280, alto=720,
                   pie='Un tablón con listas electorales de colores y una lupa sobre uno de los nombres.')
TARJETA_DATOS = 'img/compartir/listas-electorales-29n-datos.jpg'
# Calendario del 29N (LOREG, contado desde la convocatoria del BOE del 6 de octubre de 2026)
CALENDARIO = [('2026-10-26', 'Fin del plazo para presentar candidaturas'),
              ('2026-10-28', 'El BOE publica las candidaturas presentadas'),
              ('2026-11-02', 'Las juntas electorales provinciales proclaman las candidaturas'),
              ('2026-11-03', 'El BOE publica las candidaturas proclamadas'),
              ('2026-11-13', 'Empieza la campaña electoral'),
              ('2026-11-27', 'Termina la campaña'),
              ('2026-11-29', 'Elecciones generales')]

# Partidos: (clave, patrón sobre siglas y denominación, nombre corto, color claro, color oscuro, clave en el modelo).
# Colores de encuestas/src/construir.py (los de cada partido en todo el sitio).
PARTIDOS = [
    ('PP', r'^(PP|P\.P\.|PP-|UPN-PP|PP-UPN|PP-PAR)|PARTIDO POPULAR', 'PP', '#1d84ce', '#4fa8ea', 'PP'),
    ('PSOE', r'PSOE|^PSC\b|^PSE|^PSDEG|^PSIB|^PSN|SOCIALISTA OBRERO|SOCIALISTES DE CATALUNYA', 'PSOE', '#e30613', '#ff5a5f', 'PSOE'),
    ('VOX', r'^VOX$', 'Vox', '#5ac035', '#74d651', 'Vox'),
    ('SUMAR', r'SUMAR|FRENTE AMPLIO|FRONT AMPLI|COMPROM[IÍ]S|EN COM[UÚ]|COMUNS|ECP\b|M[EÉ]S PER MALLORCA|MÁS MADRID|MÁS PAÍS', 'Sumar / Frente Amplio', '#a2275f', '#d0679a', 'Sumar'),
    ('PODEMOS', r'^PODEMOS|^UNIDAS PODEMOS', 'Podemos', '#5a3c8f', '#8a6fe0', 'Podemos'),
    ('SALF', r'SE ACAB[OÓ] LA FIESTA|^SALF', 'SALF', '#785a46', '#a9876f', 'SALF'),
    ('ERC', r'^ERC|ESQUERRA REPUBLICANA', 'ERC', '#f5b324', '#f7c454', 'ERC'),
    ('JUNTS', r'JUNTS|JXCAT|J X CAT', 'Junts', '#20c0b2', '#2fd0c2', 'Junts'),
    ('BILDU', r'BILDU', 'EH Bildu', '#a5c400', '#b9d630', 'EH Bildu'),
    ('PNV', r'PNV|EAJ', 'PNV', '#2b8a3e', '#4caf63', 'PNV'),
    ('BNG', r'^B\.?N\.?G\.?$|BLOQUE NACIONALISTA GALEGO', 'BNG', '#4a9fdc', '#7ab8e6', 'BNG'),
    ('CC', r'^CCA?$|COALICI[OÓ]N CANARIA', 'Coalición Canaria', '#f7d417', '#f9e04a', 'CC'),
    ('NC', r'^NC\b|NUEVA CANARIAS', 'Nueva Canarias', '#e08a2e', '#f0a050', 'Nueva Canarias'),
    ('UPN', r'^UPN$|UNI[OÓ]N DEL PUEBLO NAVARRO', 'UPN', '#0b3d91', '#5b7fd0', 'UPN'),
    ('ALIANCA', r'ALIAN[CÇ]A CATALANA', 'Aliança Catalana', '#064a81', '#4a86c0', 'Aliança'),
    ('CS', r"^(CS|C'S|C´S)$|CIUDADANOS-PARTIDO|CIUTADANS", 'Ciudadanos', '#eb6109', '#f28a45', 'Ciudadanos'),
    ('CUP', r'^CUP', 'CUP', '#d4b200', '#f0d000', 'CUP'),
]
# Coaliciones que el modelo no simula como una sola lista: sin probabilidad por puesto (el modelo da por separado
# PP y UPN en Navarra, y Nueva Canarias y Sumar/Podemos en Canarias)
SIN_MODELO = r'UPN-PP|UNIDAD DEL PUEBLO CANARIO'
OTRO = ('OTROS', '', 'Otros', '#8a8589', '#a9a4a8', None)
# en el modelo, Podemos va dentro de otras listas en estas provincias (encuestas, «PODEMOS_CON_ERC» y «PODEMOS_CON_FA»)


def familia(siglas, denominacion):
    s, d = siglas.upper(), denominacion.upper()
    for p in PARTIDOS:
        if re.search(p[1], s) or re.search(p[1], d):
            return p
    return OTRO


def clave_nombre(n):
    s = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    return ' '.join(re.sub(r'[^a-z ]+', ' ', s).split())


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def prov_de_circ(circ):
    """'Coruña (A)' → '15'; 'S/C Tenerife' → '38'; 'Alicante/Alacant' → '03'."""
    c = re.sub(r'^(.*)\((.*)\)$', r'\2 \1', circ).strip()
    c = {'S/C Tenerife': 'Santa Cruz de Tenerife', 'Araba/Álava': 'Álava'}.get(circ, c).split('/')[0]
    s = slug(c)
    por_slug = {v: k for k, v in PROV_SLUG.items()}
    return por_slug.get(s) or {'balears-illes': '07', 'illes-balears': '07'}.get(s)


def carga():
    """Candidaturas de la elección que se enseña, y si es el avance (listas del 23J)."""
    for f, avance in (('2026-proclamadas', False), ('2026-presentadas', False), ('2023-proclamadas', True)):
        if (DATOS / f'{f}.json').exists():
            return json.loads((DATOS / f'{f}.json').read_text()), avance
    raise SystemExit('Faltan los datos: python3 listas-electorales-29n/src/boe.py 2023 BOE-A-2023-15066 proclamadas')


def diputados():
    d = json.loads((DATOS / 'diputados-xv.json').read_text())
    out = defaultdict(list)
    for x in d['diputados']:
        out[prov_de_circ(x['circ'])].append(x)
    return out, d['descargado']


def es_diputado(nombre, prov, dips):
    """Diputado de la XV legislatura en esa circunscripción: mismo nombre normalizado, o uno contiene al otro
    (el BOE a veces da el nombre completo y el Congreso el abreviado) con al menos tres palabras en común."""
    k = clave_nombre(nombre)
    t = set(k.split())
    for x in dips.get(prov, []):
        kx = clave_nombre(x['nombre'])
        tx = set(kx.split())
        if k == kx or (len(t & tx) >= 3 and (tx <= t or t <= tx)):
            return x
    return None


def pct(p):
    if p is None:
        return ''
    if p >= 0.995:
        return 'más del 99\u00a0%'
    if p < 0.005:
        return 'menos del 1\u00a0%'
    return f'{round(p * 100)}\u00a0%'


def nivel(p):
    if p is None:
        return ''
    return 'seguro' if p >= 0.9 else ('aire' if p >= 0.1 else 'dificil')


NIVEL = {'seguro': 'Casi seguro', 'aire': 'En el aire', 'dificil': 'Difícil'}


def prepara(datos, avance):
    """Candidaturas enriquecidas: familia, probabilidad de cada puesto (solo 29N), diputados que ya lo son y si
    repiten de 2023."""
    dips, _ = diputados()
    pu = json.loads((DATOS / 'puestos-29n.json').read_text())
    prev = {}
    if not avance and (DATOS / '2023-proclamadas.json').exists():   # quién ya fue candidato el 23J
        cuenta = Counter()
        for c in json.loads((DATOS / '2023-proclamadas.json').read_text())['candidaturas']:
            for p in c['titulares']:
                k = clave_nombre(p['nombre'])
                cuenta[k] += 1
                prev.setdefault(k, (c['prov'], c['camara'], c['siglas'], p['n']))
        prev = {k: v for k, v in prev.items() if cuenta[k] == 1}   # un nombre repetido en 2023 no se sabe a quién corresponde
    cands = []
    for c in datos['candidaturas']:
        if c.get('no_proclamada') or not c['titulares']:
            continue
        f = familia(c['siglas'], c['denominacion'])
        corto = f[2] if f[0] != 'OTROS' else (c['siglas'] or c['denominacion'])
        if avance and f[0] == 'SUMAR':   # en 2023 no existía el Frente Amplio
            corto = 'Sumar'
        c = dict(c, fam=f[0], corto=corto, color=f[3], oscuro=f[4])
        sin = re.search(SIN_MODELO, c['denominacion'].upper())
        probs = None if avance or sin or c['camara'] != 'congreso' or not f[5] else pu['puestos'].get(c['prov'], {}).get(f[5], [])
        for p in c['titulares']:
            if probs is not None:
                p['p'] = probs[p['n'] - 1] if p['n'] - 1 < len(probs) else 0.0
            d = es_diputado(p['nombre'], c['prov'], dips)
            if d:
                p['dip'] = d['formacion'] + (' (de baja)' if d['baja'] and not d['baja'].startswith('06/10/2026') else '')
            if prev:
                k = clave_nombre(p['nombre'])
                if k in prev and (prev[k][0] == c['prov'] or len(k.split()) >= 3):
                    p['en23'] = prev[k]
        cands.append(c)
    return cands


def escanos():
    """Escaños por provincia y reparto central del modelo de /encuestas/."""
    e = json.loads((RAIZ / 'previsiones/datos/publico/escenario-base.json').read_text())
    m = json.loads((RAIZ / 'previsiones/datos/publico/meta.json').read_text())
    return e['provincias'], m['generado']


def miles(n):
    return f'{n:,}'.replace(',', '.')


def orden_listas(cs, modelo_prov):
    """Primero las listas con más escaños esperados en el modelo; luego, el orden del BOE."""
    esc = {}
    for l in (modelo_prov or {}).get('listas', []):
        esc[l['lista']] = (l['escanos'][1], l['voto'][1])
    def k(c):
        f = familia(c['siglas'], c['denominacion'])
        e = esc.get(f[5]) if f[5] else None
        return (-(e[0] if e else -1), -(e[1] if e else 0), c['orden'])
    return sorted(cs, key=k)


def chip(p):
    if 'p' not in p:
        return ''
    return f'<span class="pr {nivel(p["p"])}" title="Probabilidad de salir elegido según el modelo">{pct(p["p"])}</span>'


def marcas(p):
    out = ''
    if p.get('dip'):
        out += '<span class="mk dip" title="Tuvo escaño en el Congreso en la legislatura que acaba">diputado/a</span>'
    if p.get('en23'):
        pv, cam, sig, n = p['en23']
        out += f'<span class="mk r23" title="Candidato en 2023: {html.escape(sig)}, {"Congreso" if cam == "congreso" else "Senado"}, {html.escape(PROV_NOMBRE.get(pv, pv))}, n.º {n}">repite</span>'
    return out


def bloque_lista(c, total):
    e = html.escape
    filas = ''
    for p in c['titulares']:
        corte = ' class="corte"' if c['camara'] == 'congreso' and p['n'] == total else ''
        sup = ''
        if p.get('suplentes'):
            sup = f'<small>Suplentes: {e(", ".join(p["suplentes"]))}</small>'
        filas += f'<li{corte}><span class="nm">{e(p["nombre"])}</span>{marcas(p)}{chip(p)}{sup}</li>'
    sup = ''
    if c['suplentes']:
        sup = (f'<details><summary>{len(c["suplentes"])} suplente{"s" if len(c["suplentes"]) != 1 else ""}</summary><ol>'
               + ''.join(f'<li>{e(p["nombre"])}{marcas(p)}</li>' for p in c['suplentes']) + '</ol></details>')
    circ = f' · {e(c["circ"])}' if c['circ'] else ''
    return (f'<section class="lista" style="--c:{c["color"]};--co:{c["oscuro"]}" id="{c["camara"]}-{slug(c["siglas"] or c["denominacion"])}-{c["orden"]}">'
            f'<h3><span class="sg">{e(c["siglas"] or c["corto"])}</span> <span class="den">{e(c["denominacion"])}{circ}</span></h3>'
            f'<ol>{filas}</ol>{sup}</section>')


def resumen_salida(cs, modelo_prov):
    """Para cada partido con opciones: hasta qué puesto es casi seguro y qué puestos quedan en el aire (modelo)."""
    frases = []
    for c in orden_listas(cs, modelo_prov):
        ps = [p for p in c['titulares'] if 'p' in p]
        if not ps:
            continue
        seguros = [p for p in ps if p['p'] >= 0.9]
        aire = [p for p in ps if 0.1 <= p['p'] < 0.9]
        if not seguros and not aire:
            continue
        t = f'{c["corto"]}: '
        if seguros:
            t += (f'{seguros[0]["nombre"]} casi seguro' if len(seguros) == 1 else f'los {len(seguros)} primeros casi seguros')
        if aire:
            t += (', y ' if seguros else '') + 'en el aire ' + ', '.join(f'{p["nombre"]} (n.º {p["n"]}, {pct(p["p"])})' for p in aire[:3])
        frases.append(t)
    return frases


def pagina_provincia(cod, cs, modelo, generado, avance, datos, todas):
    e = html.escape
    nombre, sl = PROV_NOMBRE[cod], PROV_SLUG[cod]
    corto = nombre.split('/')[0]
    mp = modelo.get(cod)
    total = mp['escanos_total'] if mp else 0
    cong = orden_listas([c for c in cs if c['camara'] == 'congreso'], mp)
    sen = [c for c in cs if c['camara'] == 'senado']
    sen = [c for circ in sorted({c['circ'] for c in sen}) for c in orden_listas([x for x in sen if x['circ'] == circ], mp)]
    n_cong = sum(len(c['titulares']) for c in cong)
    n_sen = sum(len(c['titulares']) for c in sen)
    anio = '2023' if avance else '2026'
    cabezas = [(c['corto'], c['titulares'][0]['nombre']) for c in cong if c['titulares'] and c['fam'] != 'OTROS'][:8]
    if avance:
        titular = f'Listas del 29N en {corto}: el BOE publica los candidatos el 28 de octubre'
        dek = (f'{corto} elige {total} diputados el 29 de noviembre. Mientras llegan las listas oficiales, aquí están las del 23J de 2023, '
               f'con quién sigue siendo diputado, y los puestos que dan escaño según las encuestas de hoy.')
    else:
        titular = f'Listas del 29N en {corto}: {len(cong)} candidaturas y {miles(n_cong)} candidatos al Congreso'
        dek = (f'Todos los candidatos al Congreso y al Senado por {corto}, puesto a puesto, con las opciones de salir elegido de cada uno '
               f'según la media de encuestas. {total} escaños en juego.')
    fase = 'proclamadas' if datos['fase'] == 'proclamadas' else 'presentadas'
    fuente_boe = f'<a href="{datos["url"]}">BOE del {fecha_larga(datos["fecha_boe"])}</a>, candidaturas {fase}'
    salida = resumen_salida(cong, mp) if not avance else []
    # en el avance, los puestos de salida salen del modelo sin nombres
    puestos_modelo = []
    if mp:
        pu = json.loads((DATOS / 'puestos-29n.json').read_text())['puestos'].get(cod, {})
        for fam in PARTIDOS:
            ps = pu.get(fam[5]) if fam[5] else None
            if not ps:
                continue
            seg = sum(1 for x in ps if x >= 0.9)
            aire = [(i + 1, x) for i, x in enumerate(ps) if 0.1 <= x < 0.9]
            if seg or aire:
                puestos_modelo.append((fam, seg, aire))
    p_modelo = ''
    if puestos_modelo:
        partes = []
        for fam, seg, aire in puestos_modelo:
            t = fam[2].replace('Sumar / ', '') + ': '
            t += ({1: 'el n.º 1 casi seguro', 2: 'el 1 y el 2 casi seguros'}.get(seg, f'del 1 al {seg} casi seguros') if seg else 'ningún puesto seguro')
            if aire:
                t += '; en el aire, ' + ', '.join(f'el {i} ({pct(x)})' for i, x in aire[:3])
            partes.append(t)
        p_modelo = ('Con la media de las encuestas, estos son los puestos de cada lista que salen elegidos: ' + '. '.join(partes) + '.')
    faq = [(f'¿Cuántos diputados elige {corto} el 29N?',
            f'{total}. Se reparten con la ley D\'Hondt entre las candidaturas que superan el 3 % de los votos válidos de la provincia.' if total else ''),
           (f'¿Cuándo se publican las listas oficiales del 29N en {corto}?',
            'El BOE publica las candidaturas presentadas el 28 de octubre y las proclamadas por la junta electoral provincial el 3 de noviembre. '
            'Esta página se actualiza con cada publicación.')]
    if not avance and cabezas:
        faq.insert(1, (f'¿Quién encabeza las listas al Congreso por {corto}?', '; '.join(f'{p}: {n}' for p, n in cabezas) + '.'))
    if salida:
        faq.insert(2, (f'¿Qué candidatos de {corto} tienen el escaño en el aire?', '; '.join(salida[:5]) + '. Probabilidades según el modelo de Mapa Electoral con la media de encuestas.'))
    if cod in ('07', '35', '38'):
        faq.append(('¿Cómo se elige el Senado en las islas?', 'En Baleares y Canarias cada isla o agrupación de islas elige sus propios senadores: tres Mallorca, Gran Canaria y Tenerife, y uno cada una de las demás.'))
    elif cod in ('51', '52'):
        faq.append((f'¿Cuántos senadores elige {corto}?', 'Dos. Cada elector puede votar a uno.'))
    else:
        faq.append((f'¿Cuántos senadores elige {corto}?', 'Cuatro. Cada elector puede marcar hasta tres nombres, de una o de varias candidaturas, y salen los cuatro más votados.'))
    faq = [(q, a) for q, a in faq if a]
    url = f'{URL}{sl}/'
    desc = (f'Listas electorales del 29N en {corto}: candidatos al Congreso y al Senado de cada partido, puesto a puesto, y quién tiene opciones de salir. '
            + ('Avance con las listas de 2023 hasta el BOE del 28 de octubre.' if avance else f'{len(cong)} candidaturas, {total} escaños.'))[:300]
    imagen = f'{BASE}/img/compartir/listas-electorales-29n.jpg'
    jsonld = [{'@context': 'https://schema.org', '@type': 'WebPage', '@id': url + '#pagina', 'name': titular, 'description': desc, 'url': url,
               'inLanguage': 'es', 'datePublished': PUBLICADO, 'dateModified': date.today().isoformat(), 'isPartOf': {'@id': URL + '#pagina'},
               'about': [{'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'}, {'@type': 'AdministrativeArea', 'name': nombre}],
               'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'}, 'publisher': MEDIO},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    vecinas = [(PROV_SLUG[p], PROV_NOMBRE[p].split('/')[0]) for p in CCAA[PROV_CCAA[cod]][2] if p != cod]
    aviso = ''
    if avance:
        aviso = (f'<p class="propio"><b>Avance.</b> Las listas del 29N se publican en el BOE el miércoles 28 de octubre; hasta entonces, '
                 f'esta página enseña las listas oficiales con las que se votó el 23J de 2023 en {e(corto)} ({fuente_boe}). '
                 'Las probabilidades de salir elegido se añaden en cuanto haya nombres.</p>')
    menu = ''.join(f'<a href="#{c["camara"]}-{slug(c["siglas"] or c["denominacion"])}-{c["orden"]}" style="--c:{c["color"]};--co:{c["oscuro"]}">{e(c["siglas"] or c["corto"])}</a>' for c in cong)
    cuerpo = f"""<main>
<p class="kicker"><a href="../">Listas electorales del 29N</a> · {e(CCAA[PROV_CCAA[cod]][0])}</p>
<h1 data-miga="{e(corto)}">{e(titular)}</h1>
<p class="dek">{e(dek)}</p>
<p class="firma">Por <a href="../../sobre-mi.html">{AUTOR}</a> · Actualizado el <time datetime="{date.today().isoformat()}">{fecha_larga(date.today().isoformat())}</time></p>
{aviso}
<form class="buscar-prov" action="../" method="get" role="search"><label for="q">Buscar un candidato en toda España</label><input id="q" name="q" type="search" placeholder="Nombre o apellido" autocomplete="off"><input type="hidden" name="provincia" value="{cod}"><button>Buscar</button></form>
{f'<p data-tipo="dato">{e(p_modelo)} <a href="../../encuestas/{sl}/">Escaños de {e(corto)} según las encuestas</a>.</p>' if p_modelo else ''}
<h2>Candidatos al Congreso por {e(corto)} ({anio})</h2>
<p>{len(cong)} candidaturas con {miles(n_cong)} titulares{'' if not avance else ''}. {'Cada nombre lleva la probabilidad de salir elegido según la media de encuestas: <span class="pr seguro">casi seguro</span> (90 % o más), <span class="pr aire">en el aire</span> (10-90 %) y <span class="pr dificil">difícil</span>. ' if not avance else ''}La raya marca el puesto {total}: los escaños que reparte la provincia. <span class="mk dip">diputado/a</span>: tuvo escaño en la legislatura que acaba.{' <span class="mk r23">repite</span>: ya fue candidato en 2023.' if not avance else ''}</p>
<nav class="menu-listas" aria-label="Candidaturas al Congreso">{menu}</nav>
<div class="listas">{''.join(bloque_lista(c, total) for c in cong)}</div>
<h2>Candidatos al Senado por {e(corto)} ({anio})</h2>
<p>{len(sen)} candidaturas y {n_sen} candidatos{', por islas' if cod in ('07', '35', '38') else ''}. Junto a cada nombre, sus dos suplentes.</p>
<div class="listas">{''.join(bloque_lista(c, 0) for c in sen)}</div>
<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{e(q)}</h3></summary><p>{e(a)}</p></details>' for q, a in faq)}</div>
<h2>Fuentes</h2>
<dl class="ficha">
<dt>Listas</dt><dd>{fuente_boe}. Nombres tal como los publica la junta electoral.</dd>
<dt>Probabilidad de salir elegido</dt><dd>Modelo de Mapa Electoral con la media de encuestas del {fecha_larga(json.loads((DATOS / 'puestos-29n.json').read_text())['modelo'])}: reparte el voto por provincia y simula 2.000 resultados; cada puesto sale elegido en una parte de ellos. <a href="../../encuestas/metodo-modelo.html">Cómo se calcula</a>. Es una estimación, no un resultado.</dd>
<dt>Diputados</dt><dd><a href="https://www.congreso.es/es/opendata/diputados">Datos abiertos del Congreso</a> (XV legislatura), comparando nombres.</dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
</dl>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../"><span class="kicker">Buscador</span><b>Todos los candidatos del 29N, en las 52 provincias</b></a></li><li><a href="../../encuestas/{sl}/"><span class="kicker">Encuestas</span><b>Los escaños de {e(corto)} según las encuestas</b></a></li><li><a href="../../{ruta_provincia(cod)}"><span class="kicker">Resultados</span><b>Cómo votó {e(corto)} en 2023, sección a sección</b></a></li>{''.join(f'<li><a href="../{s}/"><span class="kicker">Listas</span><b>Candidatos del 29N en {e(n)}</b></a></li>' for s, n in vecinas[:3])}</ul>
<footer>Mapa Electoral · <a href="../candidatos-29n.csv">Descargar todas las listas (CSV)</a> · <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/listas-electorales-29n">Código y datos</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    pagina = (cabecera(f'Listas electorales 29N en {corto}: candidatos al Congreso y Senado', desc, url, imagen, jsonld)
              .replace('<meta property="og:title" content="' + html.escape(f'Listas electorales 29N en {corto}: candidatos al Congreso y Senado') + '">', f'<meta property="og:title" content="{e(titular)}">')
              + ESTILOS + ESTILOS_LISTAS + CSS_SITIO + '\n</head>\n<body>\n' + nav('../../', '') + '\n' + cuerpo + '\n</body>\n</html>\n')
    (CARPETA / sl).mkdir(exist_ok=True)
    (CARPETA / sl / 'index.html').write_text(pagina, encoding='utf-8')


ESTILOS_LISTAS = """<style>
.listas{display:grid;grid-template-columns:repeat(auto-fill,minmax(17rem,1fr));gap:12px;margin:1rem 0 1.5rem}
.lista{border:1px solid var(--rule);border-top:4px solid var(--c);border-radius:6px;padding:.4rem .8rem .6rem;font-family:var(--ui);font-size:.92rem;background:var(--surface)}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) .lista{border-top-color:var(--co)}}
:root[data-theme="dark"] .lista{border-top-color:var(--co)}
.lista h3{font-size:1rem;margin:.2rem 0 .4rem;line-height:1.25}.lista .den{display:block;font-weight:400;color:var(--muted);font-size:.78rem}
.lista ol{margin:0;padding-left:1.7rem}.lista li{margin:.12rem 0;line-height:1.35}.lista li.corte{border-bottom:2px dashed var(--muted);padding-bottom:.25rem;margin-bottom:.35rem}
.lista li small{display:block;color:var(--muted);font-size:.78rem}.lista details{margin-top:.3rem;font-size:.85rem}
.pr{display:inline-block;font-size:.72rem;font-weight:600;border-radius:9px;padding:0 .45rem;margin-left:.35rem;white-space:nowrap;vertical-align:1px}
.pr.seguro{background:#1f7a3a;color:#fff}.pr.aire{background:#f0c53a;color:#1d1a1c}.pr.dificil{background:var(--grid);color:var(--muted)}
.mk{display:inline-block;font-size:.68rem;font-weight:600;text-transform:uppercase;letter-spacing:.04em;border:1px solid var(--rule);border-radius:3px;padding:0 .3rem;margin-left:.35rem;color:var(--muted);vertical-align:1px}
.mk.dip{border-color:var(--fg);color:var(--fg)}
.menu-listas{display:flex;flex-wrap:wrap;gap:6px;font-family:var(--ui);font-size:.85rem}.menu-listas a{border:1px solid var(--rule);border-left:4px solid var(--c);border-radius:4px;padding:.1rem .5rem;text-decoration:none;color:var(--fg)}
form.buscar-prov,.filtros{font-family:var(--ui);display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:1rem 0}
form.buscar-prov label{width:100%;font-size:.9rem;color:var(--muted)}
input[type=search],select{font:inherit;font-size:16px;padding:.45rem .6rem;border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--fg);min-width:0}
input[type=search]{flex:1 1 14rem}
button{font:inherit;font-size:.95rem;padding:.45rem .9rem;border:0;border-radius:6px;background:var(--acc);color:#fff;cursor:pointer}
.filtros label{font-size:.85rem;color:var(--muted);display:flex;align-items:center;gap:4px}
#res td .pt{width:9px;height:9px}#res td.nm b{font-weight:600}
.cuenta{font-family:var(--ui);font-size:.9rem;color:var(--muted)}
.provs{columns:3 10rem;font-family:var(--ui);font-size:.95rem;padding-left:0;list-style:none}.provs li{margin:.15rem 0;break-inside:avoid}.provs small{color:var(--muted)}
.cal{font-family:var(--ui);font-size:.92rem;list-style:none;padding:0;margin:0 0 1rem}.cal li{display:flex;gap:.8rem;border-bottom:1px solid var(--rule);padding:.25rem 0}.cal b{min-width:7.5rem;font-variant-numeric:tabular-nums}.cal li.hoy{font-weight:700}.cal li.pasado{color:var(--muted)}
.cifras{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:10px;font-family:var(--ui);margin:1rem 0}.cifras div{border:1px solid var(--rule);border-radius:6px;padding:.5rem .7rem}.cifras b{display:block;font-size:1.7rem;line-height:1.1;font-variant-numeric:tabular-nums}.cifras span{color:var(--muted);font-size:.85rem}
</style>"""


BUSCADOR = """<script>
(()=>{const P=__PARTIDOS__,PROV=__PROV__,AV=__AVANCE__;let D=[];const $=s=>document.querySelector(s);
const norm=s=>s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase();
const q=$('#q'),fp=$('#fprov'),fpa=$('#fpart'),fc=$('#fcam'),fcab=$('#fcab'),fsal=$('#fsal'),res=$('#res tbody'),cuenta=$('#cuenta'),mas=$('#mas');
let lim=100;
const pc=p=>p==null?'':p>=.995?'más del 99\u00a0%':p<.005?'menos del 1\u00a0%':Math.round(p*100)+'\u00a0%';
const nv=p=>p==null?'':p>=.9?'seguro':p>=.1?'aire':'dificil';
function pinta(){const t=norm(q.value.trim()),pv=fp.value,pa=fpa.value,c=fc.value,cab=fcab.checked,sal=fsal&&fsal.checked;
 const out=[];for(const r of D){ // r: [nombre, prov, camara, partido, puesto, suplente, prob, diputado, circ, k]
  if(pv&&r[1]!==pv)continue;if(c&&r[2]!==+c)continue;if(pa&&P[r[3]][0]!==pa)continue;if(cab&&(r[4]!==1||r[5]))continue;
  if(sal&&!(r[6]>=.1))continue;if(t&&!r[9].includes(t))continue;out.push(r)}
 if(!t&&!pv&&!pa&&!cab&&!sal){out.sort((a,b)=>(b[6]??-1)-(a[6]??-1))}
 cuenta.textContent=out.length.toLocaleString('es-ES')+(out.length===1?' candidato':' candidatos')+(AV?' (listas de 2023)':'');
 res.innerHTML=out.slice(0,lim).map(r=>{const p=P[r[3]];return `<tr><td class="nm"><b>${r[0]}</b>${r[7]?'<span class="mk dip">diputado/a</span>':''}${r[5]?' <small>suplente</small>':''}</td>`+
 `<td class="n">${r[4]}</td><td><i class="pt" style="background:${p[2]}"></i>${p[1]}<small>${r[2]?'Senado':'Congreso'}${r[8]?' · '+r[8]:''}</small></td>`+
 `<td><a href="${PROV[r[1]][0]}/">${PROV[r[1]][1]}</a></td><td class="n">${r[6]==null?'–':`<span class="pr ${nv(r[6])}">${pc(r[6])}</span>`}</td></tr>`}).join('');
 mas.hidden=out.length<=lim;
 const u=new URLSearchParams();if(q.value.trim())u.set('q',q.value.trim());if(pv)u.set('provincia',pv);if(pa)u.set('partido',pa);if(c)u.set('camara',c==='1'?'senado':'congreso');
 history.replaceState(null,'',u.toString()?'?'+u:location.pathname)}
const u=new URLSearchParams(location.search);q.value=u.get('q')||'';fp.value=u.get('provincia')||'';fpa.value=u.get('partido')||'';
fc.value=u.get('camara')==='senado'?'1':u.get('camara')==='congreso'?'0':'';
[q,fp,fpa,fc,fcab,fsal].forEach(x=>x&&x.addEventListener('input',()=>{lim=100;pinta()}));mas.addEventListener('click',()=>{lim+=200;pinta()});
fetch('candidatos.json?v=__VERSION__').then(r=>r.json()).then(j=>{D=j.map(r=>(r.push(norm(r[0])),r));pinta()});
})();
</script>"""


def tarjeta(destino, titular, sub, barras):
    """Imagen para redes (1200x630): titular, subtítulo y una barra por partido con su número de candidaturas."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    fuentes = RAIZ / 'encuestas/src/fuentes'
    f = lambda peso, t: ImageFont.truetype(str(fuentes / f'IBMPlexSans-{peso}.ttf'), t)
    im = Image.new('RGB', (1200, 630), '#fbfaf8')
    d = ImageDraw.Draw(im)
    d.text((60, 48), 'MAPA ELECTORAL · LISTAS DEL 29N', font=f('Bold', 22), fill='#5d585b')

    def parte(texto, fnt, ancho):
        lineas, l = [], ''
        for w in texto.split():
            if d.textlength(f'{l} {w}'.strip(), font=fnt) <= ancho or not l:
                l = f'{l} {w}'.strip()
            else:
                lineas.append(l); l = w
        return lineas + [l]
    y = 92
    for l in parte(titular, f('Bold', 54), 1080)[:3]:
        d.text((60, y), l, font=f('Bold', 54), fill='#1d1a1c'); y += 64
    for l in parte(sub, f('Regular', 28), 1080)[:2]:
        d.text((60, y + 8), l, font=f('Regular', 28), fill='#5d585b'); y += 38
    y0, alto = 430, 110
    mx = max(n for _, n, _ in barras) or 1
    ancho = (1080 - 14 * (len(barras) - 1)) / len(barras)
    for i, (nom, n, col) in enumerate(barras):
        x = 60 + i * (ancho + 14)
        h = max(6, alto * n / mx)
        d.rectangle([x, y0 + alto - h, x + ancho, y0 + alto], fill=col)
        d.text((x, y0 + alto + 8), nom, font=f('Bold', 20), fill='#1d1a1c')
        d.text((x, y0 + alto - h - 28), str(n), font=f('Regular', 20), fill='#5d585b')
    d.text((60, 598), 'mapaelectoral.es/listas-electorales-29n', font=f('Regular', 20), fill='#5d585b')
    destino.parent.mkdir(parents=True, exist_ok=True)
    im.save(destino, quality=88)


def franja_portada(pre, titular, n_cong, n_listas, n_sen, n_dip, avance, fecha_boe):
    """Franja «Listas del 29N» de la portada, justo debajo del mapa: titular, cifras y buscador."""
    e = html.escape
    opts = ''.join(f'<option value="{c}">{e(PROV_NOMBRE[c].split("/")[0])}</option>' for c in sorted(PROV_SLUG, key=lambda c: slug(PROV_NOMBRE[c])))
    cifras = ('' if avance else
              f'<ul class="li-cif"><li><b>{miles(n_cong)}</b> candidatos al Congreso</li><li><b>{n_listas}</b> listas</li>'
              f'<li><b>{miles(n_sen)}</b> al Senado</li><li><b>{n_dip}</b> diputados que se presentan</li></ul>')
    act = 'Listas del 23J hasta que salgan las del BOE' if avance else f'BOE del {fecha_larga(fecha_boe)}'
    # tres cards en fila en escritorio (en móvil, una debajo de otra): buscador, simulador de pactos y listas por provincia
    return (f'<section class="wide del-atlas del-listas" aria-labelledby="h-del-listas"><div class="da-cab"><h2 id="h-del-listas">'
            f'<a href="{pre}listas-electorales-29n/">Listas electorales del 29N</a></h2><span class="li-act">{e(act)}</span></div>'
            f'<div class="li-fila"><div class="atlas li-main"><span class="atlas-k">Buscador de candidatos</span><a class="li-tit" href="{pre}listas-electorales-29n/">{e(titular)}</a>{cifras}'
            f'<form class="li-bus" action="{pre}listas-electorales-29n/" method="get" role="search"><input name="q" type="search" placeholder="Busca un candidato" aria-label="Nombre del candidato">'
            f'<select name="provincia" aria-label="Provincia"><option value="">Todas las provincias</option>{opts}</select><button>Buscar</button></form></div>'
            f'<a class="atlas" href="{pre}encuestas/simulador-pactos/"><span class="atlas-k">Simulador de pactos</span><b>¿Quién suma 176 escaños el 29N?</b>'
            '<span>Elige qué partidos votan sí, se abstienen o votan no y mira si sale la investidura, a partir de la media de encuestas.</span>'
            '<span class="atlas-go">Simulador de pactos del 29N →</span></a>'
            f'<a class="atlas" href="{pre}listas-electorales-29n/#provincias"><span class="atlas-k">Candidatos por provincia</span><b>Las listas de tu provincia, una a una</b>'
            '<span>Las 52 circunscripciones, al Congreso y al Senado, con las opciones de salir elegido de cada candidato.</span>'
            '<span class="atlas-go">Listas provincia a provincia →</span></a></div>'
            '<style>.del-listas .li-act{font:13px var(--sans);color:var(--muted)}.del-listas .li-tit{display:block;font:600 21px/1.25 var(--serif);color:var(--ink);text-decoration:none;margin:0 0 6px}'
            '.del-listas .li-tit:hover{text-decoration:underline}.del-listas .li-cif{list-style:none;margin:0 0 10px;padding:0;display:flex;flex-wrap:wrap;gap:2px 14px;font:13.5px var(--sans);color:var(--muted)}'
            '.del-listas .li-cif b{color:var(--ink);font-size:15px}.del-listas .li-bus{display:flex;flex-wrap:wrap;gap:8px;font:15px var(--sans)}'
            '.del-listas .li-bus input{flex:1 1 12rem;min-width:0;font:inherit;font-size:16px;padding:8px 10px;border:1px solid var(--rule,#ccc);border-radius:6px;background:transparent;color:var(--ink)}'
            '.del-listas .li-bus select{flex:1 1 9rem;font:inherit;font-size:16px;padding:8px;border:1px solid var(--rule,#ccc);border-radius:6px;background:transparent;color:var(--ink);max-width:100%}'
            '.del-listas .li-bus button{font:inherit;font-weight:600;padding:8px 16px;border:0;border-radius:6px;background:var(--ink);color:var(--bg,#fff);cursor:pointer}'
            '.del-listas .li-fila{display:grid;gap:12px}.del-listas .li-fila .atlas{margin:0}.del-listas .li-main:hover{border-color:var(--line)}'
            '@media(min-width:900px){.del-listas .li-fila{grid-template-columns:minmax(0,1.6fr) minmax(0,1fr) minmax(0,1fr)}}</style></section>')


def portada(*args):
    """Pone la franja en la portada (y en la plantilla de generales-2026/) entre <!--listas:portada-->, debajo del mapa
    y encima de la de encuestas."""
    for f, pre in ((RAIZ / 'index.html', ''), (RAIZ / 'generales-2026/src/plantilla.html', '../')):
        if not f.exists():
            continue
        t = f.read_text(encoding='utf-8')
        t = re.sub(r'\n?<!--listas:portada-->.*?<!--/listas:portada-->', '', t, flags=re.S)
        bloque = '<!--listas:portada-->' + franja_portada(pre, *args) + '<!--/listas:portada-->\n'
        t = t.replace('<!--encuestas:portada-->', bloque + '<!--encuestas:portada-->', 1)
        f.write_text(t, encoding='utf-8')


def main():
    datos, avance = carga()
    cands = prepara(datos, avance)
    modelo, generado = escanos()
    _, dips_fecha = diputados()
    pu_meta = json.loads((DATOS / 'puestos-29n.json').read_text())
    por_prov = defaultdict(list)
    for c in cands:
        por_prov[c['prov']].append(c)
    for cod in PROV_SLUG:
        pagina_provincia(cod, por_prov.get(cod, []), modelo, generado, avance, datos, cands)

    # datos del buscador: una fila por persona
    partidos, idx = [], {}
    filas, csv_filas = [], []
    for c in cands:
        k = (c['fam'], c['siglas'] if c['fam'] == 'OTROS' else c['fam'])
        if k not in idx:
            idx[k] = len(partidos)
            partidos.append([c['fam'], c['corto'] if c['fam'] != 'OTROS' else (c['siglas'] or c['denominacion'])[:40], c['color']])
        i = idx[k]
        cam = 0 if c['camara'] == 'congreso' else 1
        for p in c['titulares']:
            filas.append([p['nombre'], c['prov'], cam, i, p['n'], 0, p.get('p'), 1 if p.get('dip') else 0, c['circ']])
            csv_filas.append([PROV_NOMBRE[c['prov']], c['circ'], c['camara'], c['siglas'], c['denominacion'], p['n'], 'titular', p['nombre'],
                              '' if 'p' not in p else round(p['p'], 3), 'sí' if p.get('dip') else ''])
            for s in p.get('suplentes', []):
                csv_filas.append([PROV_NOMBRE[c['prov']], c['circ'], c['camara'], c['siglas'], c['denominacion'], p['n'], 'suplente', s, '', ''])
        for p in c['suplentes']:
            filas.append([p['nombre'], c['prov'], cam, i, p['n'], 1, None, 1 if p.get('dip') else 0, c['circ']])
            csv_filas.append([PROV_NOMBRE[c['prov']], c['circ'], c['camara'], c['siglas'], c['denominacion'], p['n'], 'suplente', p['nombre'], '', 'sí' if p.get('dip') else ''])
    (CARPETA / 'candidatos.json').write_text(json.dumps(filas, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    nombre_csv = 'candidatos-29n.csv'
    with open(CARPETA / nombre_csv, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['provincia', 'circunscripcion_senado', 'camara', 'siglas', 'candidatura', 'puesto', 'tipo', 'nombre', 'prob_salir_modelo', 'diputado_xv'])
        w.writerows(csv_filas)

    cong = [c for c in cands if c['camara'] == 'congreso']
    n_cong = sum(len(c['titulares']) for c in cong)
    n_sen = sum(len(c['titulares']) for c in cands if c['camara'] == 'senado')
    n_sup = sum(len(c['suplentes']) for c in cong)
    n_dip = sum(1 for c in cong for p in c['titulares'] if p.get('dip'))
    en_las_52 = sorted({c['corto'] for c in cong if c['fam'] != 'OTROS' and sum(1 for x in cong if x['fam'] == c['fam']) >= 50})
    mas_listas = max(PROV_SLUG, key=lambda p: sum(1 for c in cong if c['prov'] == p))
    n_mas = sum(1 for c in cong if c['prov'] == mas_listas)
    aire = sorted(((p['p'], p['nombre'], c) for c in cong for p in c['titulares'] if 'p' in p and 0.1 <= p['p'] < 0.9), key=lambda x: -x[0])
    hoy = date.today().isoformat()
    e = html.escape
    fuente_boe = f'<a href="{datos["url"]}">BOE del {fecha_larga(datos["fecha_boe"])}</a>'
    if avance:
        titular = 'Listas electorales del 29N: busca a cualquier candidato, provincia a provincia'
        dek = ('Las listas oficiales del 29N salen en el BOE el miércoles 28 de octubre y estarán aquí ese mismo día, con las opciones de salir elegido de cada candidato. '
               'Mientras, puedes buscar en las listas con las que se votó el 23J y ver quién sigue en el Congreso.')
    else:
        titular = f'Listas del 29N: {miles(n_cong)} candidatos al Congreso, y quién tiene opciones de salir'
        dek = (f'Busca por nombre, provincia o partido entre los {miles(n_cong + n_sup + n_sen)} nombres de las listas al Congreso y al Senado del {fecha_larga(datos["fecha_boe"])}, '
               'con la probabilidad de salir elegido de cada puesto según la media de encuestas.')
    aviso = ''
    if avance:
        aviso = (f'<p class="propio"><b>Avance.</b> Hasta que el BOE publique las listas del 29N (miércoles 28 de octubre), el buscador enseña las {len(cong)} candidaturas '
                 f'al Congreso y las {len(cands) - len(cong)} al Senado proclamadas para el 23J de 2023 ({fuente_boe}). Se sustituyen por las del 29N en cuanto salgan.</p>')
    cal = ''.join(f'<li class="{"pasado" if f < hoy else ("hoy" if f == hoy else "")}"><b>{fecha_larga(f).replace(" de 2026", "")}</b><span>{e(t)}</span></li>' for f, t in CALENDARIO)
    prov_opts = ''.join(f'<option value="{c}">{e(PROV_NOMBRE[c].split("/")[0])}</option>' for c in sorted(PROV_SLUG, key=lambda c: slug(PROV_NOMBRE[c])))
    part_opts = ''.join(f'<option value="{p[0]}">{e("Sumar" if avance and p[0] == "SUMAR" else p[2])}</option>' for p in PARTIDOS if any(c['fam'] == p[0] for c in cands)) + '<option value="OTROS">Otros</option>'
    provs = ''.join(f'<li><a href="{PROV_SLUG[c]}/">{e(PROV_NOMBRE[c].split("/")[0])}</a> <small>{sum(1 for x in cong if x["prov"] == c)} listas · {modelo[c]["escanos_total"]} escaños</small></li>'
                    for c in sorted(PROV_SLUG, key=lambda c: slug(PROV_NOMBRE[c])))
    p1 = (f'{"El 23J de 2023 se votaron" if avance else "Al 29N se presentan"} {len(cong)} candidaturas al Congreso en las 52 provincias, con {miles(n_cong)} candidatos titulares y {miles(n_sup)} suplentes. '
          f'{"Concurrían" if avance else "Concurren"} en todas o casi todas {", ".join(en_las_52)}. La provincia con más listas es {PROV_NOMBRE[mas_listas].split("/")[0]}, con {n_mas}.')
    p2 = ''
    if not avance and aire:
        p2 = (f'Con la media de las encuestas, {len(aire)} candidatos tienen el escaño en el aire (salen elegidos en entre el 10 % y el 90 % de las simulaciones). '
              'Entre los más cerca del cara o cruz: ' + '; '.join(f'{n} ({c["corto"]}, {PROV_NOMBRE[c["prov"]].split("/")[0]}, {pct(p)})'
                                                                 for p, n, c in sorted(aire, key=lambda x: abs(x[0] - 0.5))[:5]) + '.')
    p3 = (f'{n_dip} de los titulares {"fueron" if avance else "son"} diputados en la legislatura que acaba (XV), según los datos abiertos del Congreso.' if n_dip else '')
    faq = [('¿Cuándo se publican las listas electorales del 29N?',
            'Las candidaturas presentadas, en el BOE del 28 de octubre de 2026. Las proclamadas, tras revisarlas cada junta electoral provincial, en el BOE del 3 de noviembre. '
            'Entre una y otra puede caer alguna lista o algún nombre.'),
           ('¿Dónde puedo consultar los candidatos de mi provincia?',
            'En esta página: elige tu provincia en el buscador o entra en su página, donde están todas las listas al Congreso y al Senado, puesto a puesto.'),
           ('¿Qué significa la probabilidad de salir elegido?',
            f'Es el porcentaje de simulaciones del modelo de Mapa Electoral (media de encuestas repartida por provincia, {pu_meta["simulaciones"]:,} simulaciones) en que ese puesto de la lista consigue escaño. '
            'No es una encuesta ni un resultado: cambia con las encuestas.'.replace(',', '.')),
           ('¿Cómo se reparten los escaños del Congreso?', 'Cada provincia elige un número fijo de diputados (Madrid 38 y Barcelona 32; Soria, 2; Ceuta y Melilla, 1). '
            'Se reparten con la ley D\'Hondt entre las listas que superan el 3 % de los votos válidos de la provincia, y salen los primeros de cada lista por orden.'),
           ('¿Cómo se vota al Senado?', 'Con listas abiertas: en cada provincia peninsular se eligen cuatro senadores y el elector puede marcar hasta tres nombres de cualquier candidatura. En las islas, cada isla elige los suyos.')]
    url = URL
    titulo = 'Listas electorales 29N: buscador de candidatos al Congreso y Senado por provincia'
    desc = ('Buscador de las listas electorales del 29N: todos los candidatos al Congreso y al Senado por provincia y partido, con el BOE y las opciones de salir elegido de cada uno.')
    imagen = f'{BASE}/img/compartir/listas-electorales-29n.jpg'
    jsonld = [{'@context': 'https://schema.org', '@type': 'WebPage', '@id': url + '#pagina', 'name': titular, 'description': desc, 'url': url, 'inLanguage': 'es',
               'datePublished': PUBLICADO, 'dateModified': hoy, 'image': [f'{BASE}/{ILUSTRACION["src"]}', imagen], 'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'}, 'publisher': MEDIO,
               'about': {'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'}},
              {'@context': 'https://schema.org', '@type': 'Dataset', '@id': url + '#datos', 'name': 'Listas electorales al Congreso y al Senado' + (' (23J de 2023)' if avance else ' del 29N de 2026'),
               'description': 'Candidatos de cada candidatura, provincia y cámara, tal como los publica el BOE.', 'url': url, 'license': 'https://creativecommons.org/licenses/by/4.0/',
               'isBasedOn': datos['url'], 'creator': MEDIO, 'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv', 'contentUrl': url + nombre_csv}]},
              {'@context': 'https://schema.org', '@type': 'ItemList', '@id': url + '#provincias', 'name': 'Listas del 29N por provincia',
               'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'url': f'{url}{PROV_SLUG[c]}/', 'name': f'Listas del 29N en {PROV_NOMBRE[c].split("/")[0]}'}
                                   for i, c in enumerate(sorted(PROV_SLUG, key=lambda c: slug(PROV_NOMBRE[c])))]},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    cuerpo = f"""<main>
<p class="kicker"><a href="../elecciones/elecciones-29n-2026/">Elecciones del 29N</a> · Candidatos</p>
<h1 data-miga="Listas electorales del 29N">{e(titular)}</h1>
<p class="dek">{e(dek)}</p>
<p class="firma">Por <a href="../sobre-mi.html">{AUTOR}</a> · Actualizado el <time datetime="{hoy}">{fecha_larga(hoy)}</time></p>
<figure class="foto"><img src="../{ILUSTRACION['src']}" alt="{e(ILUSTRACION['pie'])}" width="{ILUSTRACION['ancho']}" height="{ILUSTRACION['alto']}"><figcaption>{e(ILUSTRACION['pie'])} Ilustración generada con IA para Mapa Electoral. <a href="../atlas/politica-editorial/#ia">Uso de IA</a>.</figcaption></figure>
{aviso}
<form class="filtros" role="search" onsubmit="return false">
<input id="q" type="search" placeholder="Busca un candidato: nombre o apellido" aria-label="Nombre del candidato" autocomplete="off">
<select id="fprov" aria-label="Provincia"><option value="">Todas las provincias</option>{prov_opts}</select>
<select id="fpart" aria-label="Partido"><option value="">Todos los partidos</option>{part_opts}</select>
<select id="fcam" aria-label="Cámara"><option value="">Congreso y Senado</option><option value="0">Congreso</option><option value="1">Senado</option></select>
<label><input id="fcab" type="checkbox"> Solo cabezas de lista</label>
{'' if avance else '<label><input id="fsal" type="checkbox"> Solo con opciones de salir</label>'}
</form>
<p class="cuenta" id="cuenta" aria-live="polite">Cargando las listas…</p>
<div class="tbl"><table id="res"><thead><tr><th>Candidato</th><th class="n">Puesto</th><th>Candidatura</th><th>Provincia</th><th class="n">{'Opciones de salir' if not avance else ''}</th></tr></thead><tbody></tbody></table></div>
<p><button id="mas" hidden>Ver más</button></p>
<div class="cifras"><div><b>{len(cong)}</b><span>candidaturas al Congreso</span></div><div><b>{miles(n_cong)}</b><span>candidatos titulares al Congreso</span></div><div><b>{miles(n_sen)}</b><span>candidatos al Senado</span></div><div><b>{n_dip}</b><span>titulares {"que eran" if avance else "que son"} diputados</span></div></div>
<p data-tipo="dato">{e(p1)}</p>
{f'<p data-tipo="dato">{e(p2)}</p>' if p2 else ''}
{f'<p data-tipo="dato">{e(p3)}</p>' if p3 else ''}
<h2>Fechas clave de las listas del 29N</h2>
<ul class="cal">{cal}</ul>
<h2 id="provincias">Listas del 29N por provincia</h2>
<p>Cada provincia tiene su página con todas las candidaturas al Congreso y al Senado, puesto a puesto{', y los puestos que dan escaño según las encuestas' if avance else ', con las opciones de cada candidato'}.</p>
<ul class="provs">{provs}</ul>
<h2>Preguntas frecuentes sobre las listas del 29N</h2>
<div class="faq">{''.join(f'<details><summary><h3>{e(q)}</h3></summary><p>{e(a)}</p></details>' for q, a in faq)}</div>
<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Listas</dt><dd>{fuente_boe}, candidaturas {datos['fase']}{' para el 23J de 2023' if avance else ''}. Se leen del XML oficial (<a href="https://github.com/nachotronic/abstencio-catalunya/blob/main/listas-electorales-29n/src/boe.py">código</a>) y se comprueba que estén las 52 juntas provinciales y que cada lista tenga sus puestos completos.</dd>
<dt>Opciones de salir elegido</dt><dd>Modelo de Mapa Electoral con la media de encuestas del {fecha_larga(pu_meta['modelo'])} ({pu_meta['simulaciones']:,} simulaciones). La misma simulación de <a href="../actualidad/listas-29n-quien-encabeza/">Las listas del 29N, puesto a puesto</a>. Solo para el Congreso y para las listas que mide el modelo.</dd>
<dt>Diputados de la legislatura que acaba</dt><dd><a href="https://www.congreso.es/es/opendata/diputados">Datos abiertos del Congreso</a>, descargados el {fecha_larga(dips_fecha)}: altas y bajas de la XV legislatura, comparadas por nombre en la misma provincia. Un nombre escrito de otra forma puede quedarse sin marcar.</dd>
{'<dt>Listas de 2023</dt><dd>Las proclamadas en el BOE del 27 de junio de 2023, sin las correcciones posteriores ni las listas que los tribunales readmitieron después.</dd>' if avance else ''}
<dt>Límites</dt><dd>Entre las listas presentadas (28 de octubre) y las proclamadas (3 de noviembre) las juntas pueden excluir candidaturas o nombres. Los colores agrupan a cada partido con sus marcas territoriales (PSC con PSOE, Compromís con Frente Amplio).</dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
</dl>
<p class="descargas">Descargar: <a href="{nombre_csv}">todas las listas en CSV</a> (una fila por candidato, con suplentes) · <a href="candidatos.json">JSON</a> · <a href="../{TARJETA_DATOS}">resumen en imagen</a></p>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../actualidad/listas-29n-quien-encabeza/"><span class="kicker">Puesto a puesto</span><b>Qué puestos de cada lista dan escaño</b></a></li><li><a href="../encuestas/"><span class="kicker">Encuestas</span><b>Todas las encuestas del 29N y su media</b></a></li><li><a href="../actualidad/ministros-listas-29n/"><span class="kicker">Ministros</span><b>Dónde van los ministros en las listas</b></a></li><li><a href="../"><span class="kicker">Mapa</span><b>El mapa de las generales, sección a sección</b></a></li></ul>
<footer>Mapa Electoral · Datos del BOE · <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/listas-electorales-29n">Código y datos</a> · <a href="../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    script = (BUSCADOR.replace('__PARTIDOS__', json.dumps(partidos, ensure_ascii=False))
              .replace('__PROV__', json.dumps({c: [PROV_SLUG[c], PROV_NOMBRE[c].split('/')[0]] for c in PROV_SLUG}, ensure_ascii=False))
              .replace('__AVANCE__', 'true' if avance else 'false').replace('__VERSION__', f'{datos["boe"]}-{hoy}'))
    pagina = (cabecera(titulo, desc, url, imagen, jsonld).replace('<meta property="og:title" content="' + e(titulo) + '">', f'<meta property="og:title" content="{e(titular)}">')
              + ESTILOS + ESTILOS_LISTAS + CSS_SITIO + '\n</head>\n<body>\n' + nav('../', '') + '\n' + cuerpo + '\n' + script + '\n</body>\n</html>\n')
    (CARPETA / 'index.html').write_text(pagina, encoding='utf-8')
    (CARPETA / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                         f'  <url><loc>{URL}</loc><lastmod>{hoy}</lastmod></url>\n'
                                         + ''.join(f'  <url><loc>{URL}{s}/</loc><lastmod>{hoy}</lastmod></url>\n' for s in PROV_SLUG.values()) + '</urlset>\n', encoding='utf-8')
    barras = []
    for p in PARTIDOS:
        n = sum(1 for c in cong if c['fam'] == p[0])
        if n >= 3:
            barras.append(('Sumar' if avance and p[0] == 'SUMAR' else p[2].replace('Sumar / ', ''), n, p[3]))
    barras = sorted(barras, key=lambda b: -b[1])[:8]
    tarjeta(RAIZ / TARJETA_DATOS, titular,
            f'{len(cong)} candidaturas al Congreso{" en 2023" if avance else ""}, {miles(n_cong)} candidatos titulares. Candidaturas por partido:', barras)
    portada(titular, n_cong, len(cong), n_sen, n_dip, avance, datos['fecha_boe'])
    import esquema
    for f in [CARPETA / 'index.html'] + [CARPETA / s / 'index.html' for s in PROV_SLUG.values()]:
        esquema.procesa(f)
    print(f'listas: {"avance con 2023" if avance else datos["fase"] + " 29N"}; {len(cong)} candidaturas al Congreso, {n_cong} titulares, {n_dip} diputados; {titular}')


if __name__ == '__main__':
    main()
