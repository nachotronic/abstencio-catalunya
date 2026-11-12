"""Serie «El mapa electoral de…» (desde el 10-11-2026): una pieza por comunidad autónoma para el 29N, municipio a municipio.

Este módulo reúne lo común a todas: los votos por municipio de noviembre de 2019 y julio de 2023, con las listas por
separado (en 2019, Unidas Podemos y Más País; nunca familias sumadas), el ganador de cada municipio, los escaños por
provincia, el reparto central del modelo de /encuestas/ y los gráficos (mapas municipales en SVG, barras, tablas) con
colores de partido y leyenda. Cada pieza (mapa_andalucia.py…) pone el texto.

Voto: generales-2026/descargas/municipios.csv (Ministerio del Interior, sin voto exterior). Más País en 2019:
listas_separadas.csv (columna sumar_b, por sección), sumado por municipio. Porcentajes sobre votos a candidaturas.
Escaños de 2019 y 2023: actualidad/src/sistema/simulador.json (con voto exterior), D'Hondt y barrera del 3 %, los
oficiales. Escaños del 29N: reparto central publicado en /encuestas/<provincia>/ (D'Hondt sobre el voto central).
"""
import json
import math
import re
import sys

import numpy as np
import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, n

Y19, Y23 = '2019_11', '2023_07'
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
# Listas que pueden ganar un municipio: en 2019, UP y Más País por separado
L19 = ['PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS', 'ERC', 'JUNTS', 'CUP', 'PNV', 'BILDU', 'BNG', 'CC']
L23 = ['PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS', 'CUP', 'PNV', 'BILDU', 'BNG', 'CC']
NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'UP': 'Unidas Podemos', 'MP': 'Más País', 'SUMAR': 'Sumar', 'CS': 'Ciudadanos',
       'ERC': 'ERC', 'JUNTS': 'Junts', 'CUP': 'CUP', 'PNV': 'PNV', 'BILDU': 'EH Bildu', 'BNG': 'BNG', 'CC': 'CC', 'EMPATE': 'Empate'}
COL = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'VOX': COLOR['Vox'], 'UP': COLOR['Podemos'], 'MP': '#0fb5a8',
       'SUMAR': COLOR['Sumar'], 'CS': '#eb6109', 'ERC': COLOR['ERC'], 'JUNTS': COLOR['Junts'], 'CUP': '#ffe100', 'PNV': COLOR['PNV'],
       'BILDU': COLOR['EH Bildu'], 'BNG': COLOR['BNG'], 'CC': COLOR['CC'], 'EMPATE': '#8a8486'}
# Nombres de las listas del simulador y del modelo, a las claves de arriba
SIM = {'PP': 'PP', 'PSOE': 'PSOE', 'Vox': 'VOX', 'Unidas Podemos': 'UP', 'Más País': 'MP', 'Sumar': 'SUMAR', 'Cs': 'CS',
       'ERC': 'ERC', 'Junts': 'JUNTS', 'CUP': 'CUP', 'ECP': 'UP', 'En Comú Podem': 'UP', 'JxCat': 'JUNTS',
       'Podemos': 'PODEMOS', 'SALF': 'SALF'}
p = lambda v: n(v, 1)
s1 = lambda v: f'{v:+.1f}'.replace('.', ',').replace('-', '−')


def municipios(provs, regionales=None):
    """Tabla de municipios de las provincias dadas, con votos por lista, porcentajes y ganador.

    regionales: CSV de datos/ con votos por municipio de listas que en las descargas van en OTROS (columnas
    <año>_v<LISTA>, de los mismos datos por mesa de pollspaindata/Interior); se restan de OTROS y pueden ganar municipios.
    """
    m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
    m = m[m.mun_code.str[:2].isin(provs)].copy()
    b = pd.read_csv(RAIZ / 'generales-2026/descargas/listas_separadas.csv', dtype={'tract_code': str})
    b = b[b.eleccion == Y19]
    mp = b.groupby(b.tract_code.str[:5]).sumar_b.sum()
    m[f'{Y19}_vMP'] = m.mun_code.map(mp).fillna(0)
    m[f'{Y19}_vUP'] = m[f'{Y19}_vSUMAR'] - m[f'{Y19}_vMP']
    assert (m[f'{Y19}_vUP'] >= 0).all()
    # La CUP va en OTROS en las descargas del mapa: sus votos por municipio salen de los mismos datos por mesa
    # (pollspaindata, Ministerio del Interior), en datos/cup_municipios_2019_2023.csv, y se restan de OTROS.
    # Desde el arreglo de los ganadores (generales-2026/src/mapa_listas_propias.py, 11-11-2026), municipios.csv ya trae
    # esas listas con columna propia en 2019-N y 2023 (CUP, Por Ávila, Soria ¡Ya!, Frente Obrero...), restadas de OTROS:
    # se usan tal cual (y se comprueba que cuadran con los ficheros de datos/), y cualquier otra lista propia con votos en
    # estas provincias entra también en el cálculo del ganador. UPN (Navarra 2023) va aparte del PP.
    sys.path.insert(0, str(RAIZ / 'generales-2026' / 'src'))
    from partidos import PROPIAS
    cup = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/cup_municipios_2019_2023.csv', dtype={'mun_code': str}).set_index('mun_code')
    for y in (Y19, Y23):
        if f'{y}_vCUP' in m:
            m[f'{y}_vCUP'] = m[f'{y}_vCUP'].fillna(0)
            assert (m[f'{y}_vCUP'] - m.mun_code.map(cup[f'{y}_vCUP']).fillna(0)).abs().max() < .5, y
        else:
            m[f'{y}_vCUP'] = m.mun_code.map(cup[f'{y}_vCUP']).fillna(0)
            m[f'{y}_vOTROS'] = m[f'{y}_vOTROS'] - m[f'{y}_vCUP']
        assert (m[f'{y}_vOTROS'] >= 0).all()
    REG = {Y19: [], Y23: []}
    for y in (Y19, Y23):
        for k in [k for k, _, _ in PROPIAS if k != 'CUP']:
            if f'{y}_v{k}' in m and m[f'{y}_v{k}'].fillna(0).sum() > 0:
                m[f'{y}_v{k}'] = m[f'{y}_v{k}'].fillna(0)
                REG[y].append(k)
    if regionales:
        rg = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos' / regionales, dtype={'mun_code': str}).set_index('mun_code')
        for col in rg.columns:
            y, k = col.split('_v')
            if k in REG[y]:   # ya en las descargas: tienen que ser los mismos votos
                assert (m[col] - m.mun_code.map(rg[col]).fillna(0)).abs().max() < .5, col
                continue
            REG[y].append(k)
            m[col] = m.mun_code.map(rg[col]).fillna(0)
            m[f'{y}_vOTROS'] = m[f'{y}_vOTROS'] - m[col]
        for y in (Y19, Y23):
            assert (m[f'{y}_vOTROS'] >= 0).all()
            for k in REG[Y19] + REG[Y23]:
                if f'{y}_v{k}' not in m:
                    m[f'{y}_v{k}'] = 0
    for y in (Y19, Y23):
        m[f'{y}_val'] = m[[f'{y}_v{f}' for f in F + ['CUP'] + REG[y]]].sum(axis=1)
        for f in F + ['CUP'] + REG[y] + (['UP', 'MP'] if y == Y19 else []):
            m[f'{y}%{f}'] = m[f'{y}_v{f}'] / m[f'{y}_val'] * 100
    for y, L in ((Y19, L19 + REG[Y19]), (Y23, L23 + REG[Y23])):
        v = m[[f'{y}_v{f}' for f in L]]
        o = np.argsort(-v.values, axis=1, kind='stable')
        s = np.take_along_axis(v.values, o, axis=1)
        m[f'marg{y[:4]}'] = (s[:, 0] - s[:, 1]) / m[f'{y}_val'] * 100          # ventaja del primero sobre el segundo, en puntos
        m[f'margv{y[:4]}'] = s[:, 0] - s[:, 1]                                 # en votos
        # Empate a votos entre los dos primeros: no hay ganador (antes se le daba a la lista que iba antes en L19/L23)
        m[f'g{y[:4]}'] = [L[i] if d > 0 else 'EMPATE' for i, d in zip(o[:, 0], s[:, 0] - s[:, 1])]
        m[f'seg{y[:4]}'] = [L[i] for i in o[:, 1]]
        m[f'emp{y[:4]}'] = [f'{L[i]}-{L[j]}' if d == 0 else '' for i, j, d in zip(o[:, 0], o[:, 1], s[:, 0] - s[:, 1])]
    m['prov'] = m.mun_code.str[:2]
    return m


def agrega(g, y, listas=('PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'ERC', 'JUNTS', 'CUP')):
    val, vot, cen = g[f'{y}_val'].sum(), g[f'{y}_votantes'].sum(), g[f'{y}_censo'].sum()
    return {'pct': {f: float(g[f'{y}_v{f}'].sum() / val * 100) for f in listas}, 'part': float(vot / cen * 100),
            'votos': {f: int(g[f'{y}_v{f}'].sum()) for f in listas}, 'censo': int(cen), 'votantes': int(vot)}


def escanos_oficiales(provs):
    """Escaños por provincia en 2019-N y 2023, con voto exterior (simulador.json, iguales a los oficiales)."""
    sim = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
    out = {}
    for y in (Y19, Y23):
        out[y] = {}
        for pr in provs:
            x, k = sim['elecciones'][y][pr], sim['escanos'][y][pr]
            v = {a: c for a, c in x['v'].items() if a != 'Otros' and c >= .03 * x['validos']}
            r = {}
            for _, a in sorted([(c / i, a) for a, c in v.items() for i in range(1, k + 1)], reverse=True)[:k]:
                r[SIM.get(a, a)] = r.get(SIM.get(a, a), 0) + 1
            out[y][pr] = r
    out['2026'] = {pr: sim['escanos']['2026'][pr] for pr in provs} if '2026' in sim['escanos'] else {}
    return out


def reparto_central(slug):
    """Reparto central y horquilla publicados en /encuestas/<slug>/: {lista: (central, mín, máx)}."""
    t = (RAIZ / f'encuestas/{slug}/index.html').read_text(encoding='utf-8')
    dsc = re.search(r'"description": "Escaños de [^:]+: ([^"]+?)\. Modelo', t).group(1)
    out = {}
    for a, b, c, d in re.findall(r'\s*([^,]+?) (\d+)(?: \(entre (\d+) y (\d+)\))?(?:,|$)', dsc):
        out[SIM.get(a, a)] = (int(b), int(c or b), int(d or b))
    return out


# --- Mapas municipales en SVG ---
def _c(v):
    """Número corto para un trazado: 0.4 → .4, −0.4 → −.4."""
    t = f'{v:g}'
    return t.replace('0.', '.', 1) if t.startswith(('0.', '-0.')) else t


def caminos(provs, W=640, lat=37.5, umbral=1.2):
    """Trazados SVG de los municipios de las provincias dadas (geometría del mapa, generales-2026/data/municipios.json),
    simplificados: se salta un punto si está a menos de `umbral` píxeles del anterior."""
    g = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
    S, kx = g['S'], math.cos(math.radians(lat))
    AN = []
    for cod, partes in zip(g['cod'], g['poly']):
        if cod[:2] not in provs:
            continue
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            AN.append((cod, [(px / S * kx, -py / S) for px, py in pts]))
    XS = [x for _, r in AN for x, _ in r]; YS = [y for _, r in AN for _, y in r]
    s = W / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    cam = {}
    for cod, r in AN:
        d, ult = '', None        # coordenadas relativas (l dx,dy) en décimas de píxel: la mitad de bytes
        for i, (x, y) in enumerate(r):
            q = (round((x - min(XS)) * s * 10), round((y - min(YS)) * s * 10))
            if ult and i < len(r) - 1 and abs(q[0] - ult[0]) + abs(q[1] - ult[1]) < umbral * 10:
                continue
            if ult is None:
                d = f'M{q[0] / 10:g},{q[1] / 10:g}l'
            else:
                dx, dy = _c((q[0] - ult[0]) / 10), _c((q[1] - ult[1]) / 10)
                d += (dx if dx[0] == '-' or d.endswith('l') else ' ' + dx) + (dy if dy[0] == '-' else ' ' + dy)
            ult = q
        cam[cod] = cam.get(cod, '') + d + 'z'
    return cam, H


def trazados(cam):
    """Los trazados, una sola vez por página: cada mapa los reutiliza con <use> (tres mapas pesan casi como uno)."""
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>'
            + ''.join(f'<path id="mu{k}" d="{d}"/>' for k, d in cam.items()) + '</defs></svg>')


def mapa_svg(cam, H, relleno, titulo, etiqueta, nombres, W=640, rotulo=''):
    """Mapa municipal: relleno(cod) da el color y titulo(cod) el texto al pasar por encima. Necesita trazados(cam) en la página."""
    out = ''.join(f'<use href="#mu{k}" fill="{relleno(k)}"><title>{esc(nombres[k])}: {esc(titulo(k))}</title></use>' for k in cam)
    rot = f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{esc(rotulo)}</p>' if rotulo else ''
    return (f'{rot}<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}" style="max-width:{W}px;margin:0 auto;display:block">'
            f'<g stroke="var(--bg)" stroke-width=".35" stroke-linejoin="round">{out}</g></svg>')


# --- Barras ---
def grupos(filas, maximo, etiqueta, W=640, ml=130, fmt=None):
    """Varias barras por fila: filas = [(nombre, [(valor, color, opacidad, texto_title)])]."""
    fmt = fmt or (lambda v: p(v))
    k = max(len(b) for _, b in filas)
    alto = 15 * k + 14
    H = alto * len(filas) + 4
    x = lambda v: ml + v / maximo * (W - ml - 52)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom, bs) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + (15 * len(bs)) / 2 + 4:.1f}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for j, (v, col, op, tt) in enumerate(bs):
            yy = y + j * 15
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="12" fill="{col}" fill-opacity="{op}" rx="2"><title>{esc(nom)}, {esc(tt)}: {fmt(v)}</title></rect>')
            out.append(f'<text x="{x(v) + 5:.1f}" y="{yy + 10.5}" style="font-size:12px">{fmt(v)}</text>')
    out.append('</svg>')
    return ''.join(out)


def apiladas(filas, etiqueta, W=640, ml=130):
    """Una barra al 100 % por fila, partida por partidos: filas = [(nombre, [(n, color, partido)])]."""
    alto = 30
    H = alto * len(filas) + 4
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom, ps) in enumerate(filas):
        y = 4 + i * alto
        tot = sum(c for c, _, _ in ps)
        out.append(f'<text x="{ml - 8}" y="{y + 15}" text-anchor="end" class="lab">{esc(nom)}</text>')
        x0 = ml
        for c, col, par in ps:
            w = c / tot * (W - ml - 4)
            out.append(f'<rect x="{x0:.1f}" y="{y}" width="{w:.1f}" height="20" fill="{col}"><title>{esc(nom)}: {esc(par)}, {c} de {tot}</title></rect>')
            if w > 22:
                out.append(f'<text x="{x0 + w / 2:.1f}" y="{y + 14.5}" text-anchor="middle" style="fill:#fff;font-weight:600;font-size:12px">{c}</text>')
            x0 += w
    out.append('</svg>')
    return ''.join(out)


def insertado(caja, titulo, alto=620):
    """El mapa interactivo de la portada, insertado y encajado en la caja (lon0, lat0, lon1, lat1). Debajo del iframe, un
    enlace de respaldo: si el mapa no carga, no queda un hueco vacío."""
    b = ','.join(f'{v:g}' for v in caja)
    return (f'<div style="position:relative;min-height:{alto}px;background:color-mix(in srgb, var(--muted) 10%, var(--bg));border-radius:6px">'
            f'<a href="{BASE}" style="position:absolute;top:50%;left:0;right:0;text-align:center;transform:translateY(-50%)">Abrir el mapa electoral</a>'
            f'<iframe src="{BASE}insertar/?b={b}" width="100%" height="{alto}" '
            f'style="position:relative;border:0;max-width:100%;display:block" loading="lazy" title="{esc(titulo)}"></iframe></div>')
