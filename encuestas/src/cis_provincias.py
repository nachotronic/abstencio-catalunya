"""Bloque «El CIS preelectoral en <provincia>» de las páginas /encuestas/<provincia>/ (Nacho, 13-11-2026: «Yo haría páginas por provincia»).

Datos: horquillas de escaños P5-P95 del CIS por provincia y entrevistas de cada una (estudio 3584), copiadas en
actualidad/src/resumenes/datos/cis_3584_provincias.json desde el PDF «3584_estimacion» y el Excel «3584-multi_A» de cis.es.
Se comparan por espacio con el reparto central del modelo y con los escaños de julio de 2023 (D'Hondt sobre los votos
oficiales de actualidad/src/sistema/simulador.json): Frente Amplio, Compromís, Ara Més-Front Ampli y la Unidad del Pueblo
Canario frente a Sumar / Frente Amplio; ERC-Podemos frente a ERC; en Navarra, el PP del CIS frente a UPN-PP (en 2023, UPN + PP).
"""
import html
import json
import math
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]
DATOS = RAIZ / 'actualidad/src/resumenes/datos/cis_3584_provincias.json'
SIM = RAIZ / 'actualidad/src/sistema/simulador.json'
PDF = 'https://www.cis.es/documents/d/guest/3584_estimacion-pdf'
XLSX = 'https://www.cis.es/documents/d/guest/3584-multi_A-xlsx'
PIEZA = '../../actualidad/cis-preelectoral-provincias-29n/'
ESP = {'PSOE': 'PSOE', 'PP': 'PP', 'Vox': 'Vox', 'Frente Amplio': 'Sumar', 'Compromís': 'Sumar', 'Ara Més-Front Ampli': 'Sumar', 'UPC': 'Sumar',
       'ERC-Podemos': 'ERC', 'Junts': 'Junts', 'BNG': 'BNG', 'PNV': 'PNV', 'EH Bildu': 'EH Bildu', 'Podemos': 'Podemos', 'Adelante Andalucía': 'Adelante Andalucía'}
NOMBRE_CIS = {'Compromís': 'Compromís: Front Valencià', 'UPC': 'Unidad del Pueblo Canario', 'ERC-Podemos': 'ERC-Podemos'}
# nombre con el que el CIS mide el espacio de Sumar / Frente Amplio en cada provincia (candidaturas del BOE del 3-11-2026)
SUMAR_CIS = {'03': 'Compromís', '12': 'Compromís', '46': 'Compromís', '07': 'Ara Més-Front Ampli', '35': 'UPC', '38': 'UPC'}


def _carga():
    if not DATOS.exists():
        return None, None
    cis = json.load(open(DATOS, encoding='utf-8'))['provincias']
    sim = json.load(open(SIM, encoding='utf-8'))
    e23 = {}
    for c in cis:
        v, val, k = sim['elecciones']['2023_07'][c]['v'], sim['elecciones']['2023_07'][c]['validos'], sim['escanos']['2023_07'][c]
        vv = {q: x for q, x in v.items() if x >= 0.03 * val}
        e = {}
        for _, q in sorted(((x / d, q) for q, x in vv.items() for d in range(1, k + 1)), reverse=True)[:k]:
            e[q] = e.get(q, 0) + 1
        if c == '31':   # Navarra: UPN-PP
            e['PP'] = e.get('PP', 0) + e.pop('UPN', 0)
        e23[c] = (e, k)
    return cis, e23


CIS, E23 = _carga()
f1 = lambda x: f'{x:.1f}'.replace('.', ',')
miles = lambda v: f'{v:,}'.replace(',', '.')
tramo = lambda a, b: str(a) if a == b else f'{a}–{b}'


def bloque(cod, nombre, rc, total, c, nom_lista):
    """HTML del bloque del CIS para una provincia. rc: reparto central del modelo {lista: escaños}."""
    if not CIS or cod not in CIS:
        return ''
    d = CIS[cod]
    assert all(b == 0 for p, (a_, b) in d['escanos'].items() if ESP[p] == 'Sumar' and p != SUMAR_CIS.get(cod, 'Frente Amplio')), cod
    ent = d['entrevistas']
    err = 2 * math.sqrt(0.25 / ent) * 100
    e23, k23 = E23[cod]
    # una fila por candidatura del CIS con escaños posibles, más los espacios con escaños en el modelo o en 2023
    filas, vistos = [], set()
    for p, (a, b) in sorted(d['escanos'].items(), key=lambda x: (-x[1][1], -x[1][0], x[0])):
        s = ESP[p]
        if s == 'Sumar' and p != SUMAR_CIS.get(cod, 'Frente Amplio'):
            continue   # el espacio de Sumar va con un solo nombre por provincia en el CIS
        if b == 0 and not rc.get(s) and not e23.get(s):
            continue
        vistos.add(s)
        filas.append((NOMBRE_CIS.get(p, p), s, a, b))
    for s in sorted(set(k for k, v in rc.items() if v) | set(k for k, v in e23.items() if v)):
        if s not in vistos:
            filas.append((nom_lista(s), s, 0, 0))
    fuera = []
    tr = ''
    for etq, s, a, b in filas:
        m = rc.get(s, 0)
        marca = ''
        if m < a:
            marca = ' ▲'; fuera.append((etq, a, b, m))
        elif m > b:
            marca = ' ▼'; fuera.append((etq, a, b, m))
        v23 = '–' if s in ('Sumar', 'Podemos') else e23.get(s, 0)   # en 2023, Podemos fue dentro de Sumar
        tr += (f'<tr><td><i class="pt" style="background:{c.color_lista(s)}"></i>{html.escape(etq)}</td>'
               f'<td class="n">{tramo(a, b)}{marca}</td><td class="n">{m}</td><td class="n">{v23}</td></tr>')
    if fuera:
        resumen = ('La horquilla del CIS no incluye el reparto central del modelo para ' + '; '.join(
            f'{html.escape(e)} (CIS {tramo(a, b)}, media {m})' for e, a, b, m in fuera) + '.')
    else:
        resumen = 'El reparto central del modelo cae dentro de la horquilla del CIS para todos los partidos.'
    pequena = ent < 300
    aviso = (f'<p class="propio"><b>Muestra muy pequeña: {ent} entrevistas.</b> El CIS fijó un mínimo de 50 entrevistas en Ceuta y Melilla; '
             f'con una muestra así, el error teórico es de ±{f1(err)} puntos. Es una indicación, no una medida fiable de la ciudad.</p>' if pequena else '')
    s23 = e23.get('Sumar', 0)
    leyenda = ('CIS: tramo del percentil 5 al 95 de escaños; ▲, el CIS da más que la media de encuestas (reparto central del modelo); ▼, menos. '
               + (f'2023: en julio de 2023, Podemos se presentó dentro de Sumar, que sacó {s23} escaño{"" if s23 == 1 else "s"} en {html.escape(nombre)}; por eso no se comparan por separado. '
                  if any(f[1] in ('Sumar', 'Podemos') for f in filas) else ''))
    navarra = '; en Navarra, el PP del CIS se compara con UPN-PP del modelo y, en 2023, con UPN + PP' if cod == '31' else ''
    cambio = (f' En 2023, {html.escape(nombre)} elegía {k23} diputado{"s" if k23 > 1 else ""}; el 29N, {total}.' if k23 != total else '')
    return f"""<h2>El CIS preelectoral en {html.escape(nombre)}</h2>
<p data-tipo="contexto">El CIS publicó el 12 de noviembre su encuesta preelectoral (estudio 3584), con una horquilla de escaños para cada partido en cada provincia: el tramo que va del percentil 5 al 95 de sus simulaciones. En {html.escape(nombre)} hizo <b>{miles(ent)} entrevistas</b>, de las 45.074 del estudio; con esa muestra, el error teórico es de ±{f1(err)} puntos. El CIS no publica el porcentaje de voto estimado por provincia.</p>
{aviso}<p data-tipo="dato">{resumen}{cambio}</p>
<div class="tbl"><table><thead><tr><th>Partido</th><th class="n">CIS</th><th class="n">Media</th><th class="n">2023</th></tr></thead><tbody>{tr}</tbody></table></div>
<p class="src">{leyenda}Fuente: CIS, estudio 3584, <a href="{PDF}">estimación de escaños por provincias</a> y <a href="{XLSX}">entrevistas por provincia</a>; 2023, Ministerio del Interior (D'Hondt sobre los votos oficiales). El Frente Amplio, Compromís, Ara Més-Front Ampli y la Unidad del Pueblo Canario se comparan con Sumar / Frente Amplio del modelo; ERC-Podemos, con ERC{navarra}. Los partidos llevan el nombre con el que los mide el CIS. Error teórico: la fórmula del CIS (95,5 %, p = q) con las entrevistas de la provincia. <a href="{PIEZA}">Las 52 provincias, comparadas</a>.</p>
"""


def _clave_cis(cod, lista):
    """Candidatura del CIS que corresponde a una lista del modelo en la provincia (la misma equivalencia que la tabla)."""
    if lista == 'Sumar':
        return SUMAR_CIS.get(cod, 'Frente Amplio')
    if lista == 'ERC':
        return 'ERC-Podemos'
    return lista


def titular(cod, lista_primera):
    """Coletilla del titular de /encuestas/<provincia>/ con el CIS (Nacho, 13-11-2026: «¿en el titular?»).
    Nombra a la lista que el modelo pone primera y a la que el CIS pone por delante de ella o, si es la misma, a la
    siguiente del CIS. Devuelve (coletilla corta para el h1, frase con las horquillas P5-P95 para el subtítulo); con un
    solo escaño, a quién se lo da el CIS. Nacho, 13-11-2026: «Recorta titulares» (las horquillas, al subtítulo)."""
    if not CIS or cod not in CIS:
        return '', ''
    esc = CIS[cod]['escanos']
    inv = {}
    for p in esc:
        s = ESP[p]
        if s == 'Sumar' and p != SUMAR_CIS.get(cod, 'Frente Amplio'):
            continue
        inv[p] = s
    # con el nombre con el que mide cada candidatura el CIS, como en la tabla (en Navarra, PP; en Cataluña, ERC-Podemos)
    a_ = lambda s: 'al ' if s in ('PP', 'PSOE', 'PNV', 'BNG') else 'a '
    etq = lambda p: NOMBRE_CORTO.get(p, p)
    n_esc = lambda ab: tramo(*ab) + (' escaño' if ab[1] == 1 else ' escaños')
    # orden del CIS: punto medio de la horquilla; a igualdad, primero la lista que el modelo pone primera
    orden = sorted((p for p in inv if esc[p][1] > 0),
                   key=lambda p: (-(esc[p][0] + esc[p][1]), p != _clave_cis(cod, lista_primera), -esc[p][1]))
    mia = _clave_cis(cod, lista_primera)
    if len(orden) == 1:   # Ceuta y Melilla: un escaño, una sola lista con opciones en el CIS
        p = orden[0]
        if p == mia:
            return 'el CIS también le da el escaño', f'El CIS preelectoral también da el escaño {a_(inv[p])}{etq(p)}'
        return f'el CIS da el escaño {a_(inv[p])}{etq(p)}', f'El CIS preelectoral da el escaño {a_(inv[p])}{etq(p)}'
    otra = next(p for p in orden if p != mia)
    pm = lambda q: esc[q][0] + esc[q][1] if q in esc else 0
    # Editor, 13-11-2026: el CIS da horquillas, no un orden. Solo «da más» si no se solapan; idénticas, empate;
    # solapadas pero distintas, «horquilla más alta» (por el punto medio)
    if mia not in orden or pm(otra) > pm(mia):
        x, y = otra, mia
    else:
        x, y = mia, otra
    ax, ay = esc[x], esc.get(y, [0, 0])
    art_o = 'el ' if inv[otra] in ('PP', 'PSOE', 'PNV', 'BNG') else ''
    if ax == ay:
        corta = f'el CIS lo empata con {art_o}{etq(otra)}'
    elif pm(x) == pm(y):
        corta = f'el CIS les da horquillas parecidas a él y a {art_o}{etq(otra)}'
    elif ax[0] > ay[1]:
        corta = 'el CIS también lo pone primero' if x == mia else f'el CIS da más escaños {a_(inv[x])}{etq(x)}'
    else:
        corta = 'el CIS también le da la horquilla más alta' if x == mia else f'el CIS da una horquilla más alta {a_(inv[x])}{etq(x)}'
    return corta, f'El CIS preelectoral da {a_(inv[x])}{etq(x)} {n_esc(esc[x])} y {a_(inv[y])}{etq(y)}, {tramo(*esc[y])}'


NOMBRE_CORTO = {'UPC': 'la Unidad del Pueblo Canario'}


def entrevistas(cod):
    return CIS[cod]['entrevistas'] if CIS and cod in CIS else None
