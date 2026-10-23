"""Cifras y mapas de las fichas de barrio (/municipio/<provincia>/<municipio>/<barrio>/), que escribe src/territorios.py.

Qué secciones censales forman cada barrio sale de data/barrios/secciones_barrio.csv (src/barrios_osm.py, límites de
OpenStreetMap o, en algunas ciudades, del ayuntamiento: fuentes.json); los votos, de las descargas del mapa (resultados por sección desde 2004, con las secciones de hoy),
y la renta y la población, del Atlas de Distribución de Renta de los Hogares del INE y del censo de 2021.
"""
import json, pathlib
import pandas as pd
from html import escape

import territorios_datos as T
from territorios_rutas import slug

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / 'data' / 'barrios'
MINIMO = 3   # secciones para tener ficha propia; con menos, el barrio solo aparece en la lista de su ciudad
ELEC = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
DEMO = ['poblacion', 'renta_uc', 'renta_pc', 'edad_media', 'menores18', 'mayores65', 'pobreza', 'extranjeros',
        'nacidos_fuera_2021', 'estudios_sup_2021', 'paro_2021']


def _carga():
    if not (D / 'secciones_barrio.csv').exists():
        return None, None, None
    b = pd.read_csv(D / 'secciones_barrio.csv', dtype=str)
    b['nivel'] = b.nivel.astype(int)
    b['distrito'] = b.distrito.where(b.distrito.notna() & (b.distrito != 'nan'), None)
    demo = pd.read_csv(T.D / 'secciones.csv', dtype={'tract_code': str, 'mun_code': str}, usecols=['tract_code'] + DEMO)
    lar = pd.read_csv(T.D / 'resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
    lar = lar[lar.mun_code.isin(set(b.mun_code))]
    return b, demo.set_index('tract_code'), lar


SB, DEMOS, LARGO = _carga()
# ciudades cuyos límites no salen de OSM sino del ayuntamiento (o de otra recopilación): {mun_code: {'fuente', 'web'}}
FUENTES = json.loads((D / 'fuentes.json').read_text()) if (D / 'fuentes.json').exists() else {}


def resultado(lar):
    """Voto por familia sobre voto válido (candidaturas + blancos) y participación de un conjunto de secciones de una elección."""
    val = (lar.candidaturas + lar.blancos).sum()
    votos = {c: lar[c].sum() for c in T.FAM}
    return {'pct': {c: votos[c] / val if val else None for c in T.FAM}, 'votos': votos, 'validos': val,
            'part': lar.votantes.sum() / lar.censo.sum() if lar.censo.sum() else None,
            'censo': lar.censo.sum(), 'votantes': lar.votantes.sum(), 'secciones': len(lar)}


def demografia(cods):
    """Medias ponderadas por población de las secciones (la renta, por habitante de cada sección)."""
    d = DEMOS.loc[DEMOS.index.intersection(list(cods))]
    out = {'poblacion': d.poblacion.sum()}
    for c in DEMO[1:]:
        ok = d[c].notna() & d.poblacion.notna()
        out[c] = (d[c][ok] * d.poblacion[ok]).sum() / d.poblacion[ok].sum() if ok.any() else None
    return out


def barrios(cod):
    """Barrios de una ciudad: [{'nombre', 'slug', 'distrito', 'secciones', ...}] con las cifras de 2023, de más a menos población."""
    if SB is None or cod not in set(SB.mun_code):
        return []
    s = SB[SB.mun_code == cod]
    lar = LARGO[LARGO.eleccion == T.ULTIMA]
    out = []
    for (nombre, osm), g in s.groupby(['barrio', 'osm_id']):
        cods = g.tract_code.tolist()
        r = resultado(lar[lar.tract_code.isin(cods)])
        out.append({'nombre': nombre, 'osm_id': osm, 'distrito': g.distrito.mode().iloc[0] if g.distrito.notna().any() else None,
                    'nivel': int(g.nivel.iloc[0]), 'secciones': cods, 'r': r, 'demo': demografia(cods)})
    vistos = {}
    for b in sorted(out, key=lambda b: -len(b['secciones'])):   # dos barrios con el mismo nombre: el pequeño lleva el distrito
        sl = slug(b['nombre'])
        if sl in vistos or sl in ('barrios', 'distritos'):
            sl = slug(f'{b["nombre"]} {b["distrito"] or b["osm_id"]}')
        vistos[sl] = 1
        b['slug'] = sl
        b['ficha'] = len(b['secciones']) >= MINIMO and b['r']['censo'] > 0
    return sorted(out, key=lambda b: -(b['demo']['poblacion'] or 0))


def serie(cods):
    """Resultado de las generales desde 2004 con las secciones de hoy; None en las elecciones en que falta más del 20 % del censo de 2023
    (secciones creadas o renumeradas después)."""
    lar = LARGO[LARGO.tract_code.isin(cods)]
    c23 = lar[lar.eleccion == T.ULTIMA].censo.sum()
    out = {}
    for y in ELEC:
        g = lar[lar.eleccion == y]
        hoy = lar[(lar.eleccion == T.ULTIMA) & lar.tract_code.isin(g.tract_code)].censo.sum()
        out[y] = resultado(g) if len(g) and hoy >= 0.8 * c23 else None
    return out


def secciones(cods):
    """Una fila por sección de 2023: código, censo, participación, ganador y su voto, renta."""
    lar = LARGO[(LARGO.eleccion == T.ULTIMA) & LARGO.tract_code.isin(cods)].copy()
    lar['val'] = lar.candidaturas + lar.blancos
    fams = [c for c in T.FAM if c != 'OTROS']
    filas = []
    for x in lar.itertuples():
        g = max(fams, key=lambda c: getattr(x, c))
        filas.append({'cod': x.tract_code, 'censo': x.censo, 'part': x.votantes / x.censo if x.censo else None,
                      'gana': g, 'pct': getattr(x, g) / x.val if x.val else None,
                      'renta': DEMOS.renta_uc.get(x.tract_code)})
    return sorted(filas, key=lambda f: f['cod'])


# ---------- mapa de las secciones del barrio, con las de alrededor en gris ----------
_GEO = {}


def _geo(cod):
    if cod not in _GEO:
        d = json.loads((D / 'geo' / f'{cod}.json').read_text())
        _GEO[cod] = dict(zip(d['cod'], d['poly']))
    return _GEO[cod]


def mapa(mun, cods, colores, titulo, ancho=640):
    """SVG: secciones del barrio de su color (`colores`: {tract_code: color}); las vecinas que entran en el encuadre, en gris."""
    g = _geo(mun)
    pts = [p for c in cods if c in g for r in g[c] for p in r]
    if not pts:
        return ''
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    m = max(x1 - x0, y1 - y0) * 0.12 + 60
    x0, x1, y0, y1 = x0 - m, x1 + m, y0 - m, y1 + m
    esc = ancho / (x1 - x0)
    alto = min(int((y1 - y0) * esc), int(ancho * 1.1))
    if (y1 - y0) * esc > alto:   # barrios alargados de norte a sur: se encuadra por el alto
        esc = alto / (y1 - y0)
        dx = (ancho / esc - (x1 - x0)) / 2
        x0, x1 = x0 - dx, x1 + dx
    P = lambda p: ((p[0] - x0) * esc, (y1 - p[1]) * esc)

    def d(rs):
        out = []
        for r in rs:
            q = [P(p) for p in r]
            if all(not (-50 < x < ancho + 50 and -50 < y < alto + 50) for x, y in q):
                continue
            out.append('M' + 'L'.join(f'{x:.0f},{y:.0f}' for x, y in q) + 'Z')
        return ''.join(out)
    dentro = set(cods)
    fondo = ''.join(d(rs) for c, rs in g.items() if c not in dentro)
    por_color = {}
    for c in cods:
        if c in g:
            por_color.setdefault(colores.get(c, '#bbb'), []).append(d(g[c]))
    # `colores` puede traer (color, opacidad): más intenso cuanto más voto tiene el ganador
    capas = ''.join(f'<path d="{"".join(v)}" fill="{col[0] if isinstance(col, tuple) else col}"'
                    + (f' fill-opacity="{col[1]}"' if isinstance(col, tuple) and col[1] < 1 else '') + '/>' for col, v in por_color.items())
    return (f'<svg viewBox="0 0 {ancho} {alto}" role="img" aria-label="{escape(titulo)}" class="graf mapa">'
            f'<path d="{fondo}" style="fill:var(--rule,#e4e4e4);stroke:var(--surface,#fff)" stroke-width="0.8"/>'
            f'<g style="stroke:var(--surface,#fff)" stroke-width="1.2" stroke-linejoin="round">{capas}</g></svg>')
