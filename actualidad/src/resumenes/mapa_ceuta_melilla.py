"""«El mapa electoral de Ceuta y Melilla» (2026-11), última pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Ceuta y Melilla son un municipio cada una, así que el mapa va por secciones censales: 56 en Ceuta y 44 en Melilla, en las
generales de noviembre de 2019 y julio de 2023. Ganador de cada sección con los votos de cada candidatura: Coalición por
Melilla (CPM) en 2019 y 2023 y el MDyC de Ceuta en 2019 se sacan de OTROS (datos/regionalistas_ceuta_melilla_2019_2023.csv,
de los datos por mesa de pollspaindata/Interior, sin voto exterior). Renta por sección: Atlas de Distribución de Renta de los
Hogares del INE (2023). Reparto central del modelo de /encuestas/ para el 29N.
Contexto: listas proclamadas en el BOE; Vox en Ceuta según Ceuta TV (6-11-2026); CPM no se presenta, según COPE Melilla (26-10-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_ceuta_melilla.py
"""
import json
import math

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, pieza
from mapa_ccaa import COL, NOM, Y19, Y23, _c, apiladas, escanos_oficiales, grupos, insertado, p, reparto_central

A = BASE + 'actualidad/'
NW = {0: 'ninguna', 1: 'una', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-ceuta-melilla-29n'
CIU = {'51': 'Ceuta', '52': 'Melilla'}
MUN = {'51': '51001', '52': '52001'}
COLC = dict(COL, CPM='#3f9a5a', MDYC='#2a7f62')
NOMC = dict(NOM, CPM='Coalición por Melilla', MDYC='MDyC', SUMAR='Sumar', EMPATE='Empate a votos')
GAN = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'CPM', 'MDYC']   # en 2019, SUMAR es Unidas Podemos

# --- Datos por sección ---
r = pd.read_csv(RAIZ / 'generales-2026/descargas/resultados_secciones_largo.csv', dtype={'tract_code': str, 'mun_code': str})
r = r[r.mun_code.isin(MUN.values()) & r.eleccion.isin([Y19, Y23])].copy()
r['prov'] = r.tract_code.str[:2]
REG = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/regionalistas_ceuta_melilla_2019_2023.csv', dtype={'tract_code': str})
assert REG.groupby(['eleccion', 'lista']).votos.sum().to_dict() == {(Y19, 'MDYC'): 819, (Y23, 'CPM'): 1279}
for c in GAN + ['RC', 'FO']:
    r[c] = r[c].fillna(0) if c in r else 0.0
r['OTROS'] = r.OTROS.fillna(0) + r.RC + r.FO   # Recortes Cero y Frente Obrero, columnas propias en las descargas
for (y, lista), g in REG.groupby(['eleccion', 'lista']):
    k = r.eleccion == y
    v = r.loc[k, 'tract_code'].map(g.set_index('tract_code').votos).fillna(0)
    assert lista == 'MDYC' or r.loc[k & (r.prov == '52'), lista].sum() == 0
    r.loc[k, lista] = v
    r.loc[k, 'OTROS'] -= v
assert (r.OTROS >= 0).all()
assert (r[GAN + ['OTROS']].sum(axis=1) == r.candidaturas).all()
assert r.groupby(['prov', 'eleccion']).size().to_dict() == {('51', Y19): 56, ('51', Y23): 56, ('52', Y19): 44, ('52', Y23): 44}


def ganador(x):
    v = x[GAN].astype(float).sort_values(ascending=False, kind='stable')
    return ('EMPATE' if v.iloc[0] == v.iloc[1] else v.index[0]), v.index[1], int(v.iloc[0] - v.iloc[1])


r[['g', 'seg', 'marg']] = r.apply(lambda x: pd.Series(ganador(x)), axis=1)
SEC = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str}, usecols=['tract_code', 'mun_code', 'renta_uc'])
SEC = SEC[SEC.mun_code.isin(MUN.values())].set_index('tract_code')
assert SEC.renta_uc.notna().all() and len(SEC) == 100
r['renta'] = r.tract_code.map(SEC.renta_uc)
assert r.renta.notna().all()


def agr(g, listas=GAN):
    val = g.candidaturas.sum()
    return {'pct': {f: float(g[f].sum() / val * 100) for f in listas}, 'votos': {f: int(g[f].sum()) for f in listas},
            'part': float(g.votantes.sum() / g.censo.sum() * 100), 'censo': int(g.censo.sum())}


AG = {pr: {y: agr(r[(r.prov == pr) & (r.eleccion == y)]) for y in (Y19, Y23)} for pr in CIU}
assert AG['51'][Y19]['votos']['VOX'] == 11734 and AG['51'][Y19]['votos']['PSOE'] == 10405 and AG['51'][Y19]['votos']['PP'] == 7407
assert AG['51'][Y23]['votos']['PP'] == 12887 and AG['51'][Y23]['votos']['PSOE'] == 11299 and AG['51'][Y23]['votos']['VOX'] == 7742
assert AG['52'][Y19]['votos']['PP'] == 9105 and AG['52'][Y19]['votos']['CPM'] == 8927
assert AG['52'][Y23]['votos']['PP'] == 13371 and AG['52'][Y23]['votos']['PSOE'] == 6892 and AG['52'][Y23]['votos']['CPM'] == 1279
M19 = {'51': AG['51'][Y19]['votos']['VOX'] - AG['51'][Y19]['votos']['PSOE'], '52': AG['52'][Y19]['votos']['PP'] - AG['52'][Y19]['votos']['CPM']}
assert M19 == {'51': 1329, '52': 178}
M23 = {'51': AG['51'][Y23]['votos']['PP'] - AG['51'][Y23]['votos']['PSOE'], '52': AG['52'][Y23]['votos']['PP'] - AG['52'][Y23]['votos']['PSOE']}

GS = {pr: {y: r[(r.prov == pr) & (r.eleccion == y)].g.value_counts().to_dict() for y in (Y19, Y23)} for pr in CIU}
assert GS == {'51': {Y19: {'VOX': 32, 'PSOE': 20, 'PP': 4}, Y23: {'PP': 33, 'PSOE': 23}},
              '52': {Y19: {'PP': 27, 'CPM': 17}, Y23: {'PP': 31, 'PSOE': 13}}}, GS
W = r.pivot(index='tract_code', columns='eleccion', values='g').rename(columns={Y19: 'g19', Y23: 'g23'})
W['prov'] = W.index.str[:2]
W['renta'] = W.index.map(SEC.renta_uc)
TRN = {pr: {f'{a}>{b}': int(((W.prov == pr) & (W.g19 == a) & (W.g23 == b)).sum()) for a in GAN for b in GAN
            if ((W.prov == pr) & (W.g19 == a) & (W.g23 == b)).any()} for pr in CIU}
assert TRN['51'] == {'PP>PP': 4, 'PSOE>PP': 1, 'PSOE>PSOE': 19, 'VOX>PP': 28, 'VOX>PSOE': 4}, TRN['51']
assert TRN['52'] == {'PP>PP': 27, 'CPM>PP': 4, 'CPM>PSOE': 13}, TRN['52']
# Renta mediana de las secciones según quién las ganó
RM = {pr: {y: {f: float(W[(W.prov == pr) & (W[y] == f)].renta.median()) for f in W[W.prov == pr][y].unique()} for y in ('g19', 'g23')} for pr in CIU}
assert RM['51']['g23']['PSOE'] < RM['51']['g23']['PP'] / 2 + 1000 and RM['52']['g23']['PSOE'] < RM['52']['g23']['PP'] * .6, RM
# Voto por tercios de renta (secciones ordenadas por renta; tercios por número de secciones)
TER = {}
for pr in CIU:
    s = SEC[SEC.index.str[:2] == pr].renta_uc.sort_values(kind='stable')
    k = len(s)
    corte = {c: ('Renta baja' if i < round(k / 3) else 'Renta media' if i < round(2 * k / 3) else 'Renta alta') for i, c in enumerate(s.index)}
    TER[pr] = {}
    for t in ('Renta baja', 'Renta media', 'Renta alta'):
        cs = [c for c, v in corte.items() if v == t]
        TER[pr][t] = {'n': len(cs), 'rmin': float(s[cs].min()), 'rmax': float(s[cs].max()),
                      **{y: agr(r[(r.eleccion == y) & r.tract_code.isin(cs)]) for y in (Y19, Y23)}}
TB, TA = TER['51']['Renta baja'][Y23]['pct'], TER['51']['Renta alta'][Y23]['pct']
assert TB['PSOE'] > 60 and TA['PP'] > 40, (TB, TA)

# Secciones más ajustadas
AJ = r[r.eleccion == Y23].sort_values(['marg', 'censo'], ascending=[True, False]).head(6)
AJ19 = r[r.eleccion == Y19].sort_values(['marg', 'censo'], ascending=[True, False]).head(6)

# Escaños
ESC = escanos_oficiales(list(CIU))
assert ESC[Y19] == {'51': {'VOX': 1}, '52': {'PP': 1}} and ESC[Y23] == {'51': {'PP': 1}, '52': {'PP': 1}} and ESC['2026'] == {'51': 1, '52': 1}
RC = {'51': reparto_central('ceuta'), '52': reparto_central('melilla')}
assert RC['51'] == {'PP': (1, 0, 1), 'VOX': (0, 0, 1), 'PSOE': (0, 0, 1)} and RC['52'] == {'PP': (1, 1, 1)}, RC
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
SIMK = {'PP': 'PP', 'PSOE': 'PSOE', 'Vox': 'VOX'}
PRIM = {pr: {SIMK[x['lista']]: x['p_primera'] * 100 for x in MOD['provincias'][pr]['listas'] if x['lista'] in SIMK} for pr in CIU}
VC = {pr: {SIMK[x['lista']]: x['voto'][1] for x in MOD['provincias'][pr]['listas'] if x['lista'] in SIMK} for pr in CIU}
assert abs(VC['51']['PP'] - VC['51']['VOX']) < 1 and 40 < PRIM['51']['PP'] < 55 and 35 < PRIM['51']['VOX'] < 50 and PRIM['52']['PP'] > 90, (PRIM, VC)
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'


# --- Mapas por sección ---
def caminos_sec(pr, W_=640, umbral=.8):
    g = json.load(open(RAIZ / f'generales-2026/data/sec/{pr}.json'))
    S, kx = g['S'], math.cos(math.radians(35.6))
    AN = []
    for cod, partes in zip(g['cod'], g['poly']):
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            AN.append((cod, [(px / S * kx, -py / S) for px, py in pts]))
    XS = [x for _, q in AN for x, _ in q]; YS = [y for _, q in AN for _, y in q]
    s = W_ / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    cam = {}
    for cod, q in AN:
        d, ult = '', None
        for i, (x, y) in enumerate(q):
            t = (round((x - min(XS)) * s * 10), round((y - min(YS)) * s * 10))
            if ult and i < len(q) - 1 and abs(t[0] - ult[0]) + abs(t[1] - ult[1]) < umbral * 10:
                continue
            if ult is None:
                d = f'M{t[0] / 10:g},{t[1] / 10:g}l'
            else:
                dx, dy = _c((t[0] - ult[0]) / 10), _c((t[1] - ult[1]) / 10)
                d += (dx if dx[0] == '-' or d.endswith('l') else ' ' + dx) + (dy if dy[0] == '-' else ' ' + dy)
            ult = t
        cam[cod] = cam.get(cod, '') + d + 'z'
    return cam, H


CAM = {pr: caminos_sec(pr) for pr in CIU}
assert len(CAM['51'][0]) == 56 and len(CAM['52'][0]) == 44
RI = r.set_index(['eleccion', 'tract_code'])


def mapa_sec(pr, y, rot):
    cam, H = CAM[pr]
    def tit(k):
        x = RI.loc[(y, k)]
        return f'Sección {k[5:7]}-{k[7:]}: {NOMC[x.g]} +{n(x.marg)} votos sobre {NOMC[x.seg]}'
    out = ''.join(f'<path d="{d}" fill="{COLC[RI.at[(y, k), "g"]]}"><title>{esc(tit(k))}</title></path>' for k, d in cam.items())
    caja = '<div style="flex:1 1 0;min-width:0">' if H > 640 else '<div>'   # Melilla, alargada: los dos mapas uno al lado del otro
    return (f'{caja}<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{esc(rot)}</p>'
            f'<svg viewBox="0 0 640 {H}" role="img" aria-label="{esc(f"Secciones censales de {CIU[pr]} por partido más votado, {rot}")}" '
            f'style="max-width:640px;margin:0 auto;display:block"><g stroke="var(--bg)" stroke-width="{.6 if H <= 640 else 1.2}" stroke-linejoin="round">{out}</g></svg></div>')


ORDG = ['PP', 'PSOE', 'VOX', 'CPM']
TRANS = lambda pr: [[f'{NOMC[a]} → {NOMC[b]}', str(v)] for k, v in TRN[pr].items() for a, b in [k.split('>')]]


def fig_mapa(pr, titulo, sub):
    return figura(titulo, sub,
                  ('<div style="display:flex;gap:12px">' if CAM[pr][1] > 640 else '<div>') + mapa_sec(pr, Y19, 'Noviembre de 2019') + mapa_sec(pr, Y23, 'Julio de 2023') + '</div>',
                  f'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por sección censal, sin voto exterior. Ganador según los votos de cada candidatura. Cálculo propio.',
                  [(NOMC[f], COLC[f]) for f in ORDG if any(f in GS[pr][y] for y in (Y19, Y23))],
                  (['Ganador en 2019 → ganador en 2023', 'Secciones'], TRANS(pr)))


g_ceu = fig_mapa('51', f'Vox ganó {GS["51"][Y19]["VOX"]} de las 56 secciones de Ceuta en 2019 y ninguna en 2023: {TRN["51"]["VOX>PP"]} pasaron al PP y {NW[TRN["51"]["VOX>PSOE"]]} al PSOE',
                 'Partido más votado en cada una de las 56 secciones censales de Ceuta, en noviembre de 2019 y en julio de 2023')
g_mel = fig_mapa('52', f'Coalición por Melilla ganó {GS["52"][Y19]["CPM"]} de las 44 secciones de Melilla en 2019; en 2023, {TRN["52"]["CPM>PSOE"]} de ellas fueron del PSOE',
                 'Partido más votado en cada una de las 44 secciones censales de Melilla, en noviembre de 2019 y en julio de 2023')

FV = {'51': ('PP', 'PSOE', 'VOX', 'SUMAR', 'CS'), '52': ('PP', 'PSOE', 'VOX', 'CPM', 'SUMAR', 'CS')}
NOMV = dict(NOMC, SUMAR='Unidas Podemos / Sumar')
g_vot = figura(f'En Ceuta, Vox bajó del {p(AG["51"][Y19]["pct"]["VOX"])} % al {p(AG["51"][Y23]["pct"]["VOX"])} %; en Melilla, el PSOE subió del {p(AG["52"][Y19]["pct"]["PSOE"])} % al {p(AG["52"][Y23]["pct"]["PSOE"])} %, con Coalición por Melilla en el {p(AG["52"][Y23]["pct"]["CPM"])} %',
               'Voto a cada partido en noviembre de 2019 y en julio de 2023, en %. Barra clara: noviembre de 2019',
               ''.join(f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{CIU[pr]}</p>'
                       + grupos([(NOMC[f] if f != 'SUMAR' else 'UP / Sumar', [(AG[pr][Y19]['pct'][f], COLC[f], .38, 'nov. 2019')] + ([(AG[pr][Y23]['pct'][f], COLC[f], 1, '2023')] if f != 'CS' else []))
                                for f in FV[pr]], 50, f'Voto en {CIU[pr]} en 2019 y 2023', W=440, ml=150) for pr in CIU),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Ciudadanos no se presentó en 2023. '
               f'Coalición por Melilla se presentó en 2023 con el {p(AG["52"][Y23]["pct"]["CPM"])} % y no se presenta el 29N. Cálculo propio.',
               [(NOMV[f], COLC[f]) for f in ('PP', 'PSOE', 'VOX', 'CPM', 'SUMAR', 'CS')] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Ciudad', 'Partido', 'Nov. 2019 (%)', '2023 (%)'],
                [[CIU[pr], NOMV[f], p(AG[pr][Y19]['pct'][f]), p(AG[pr][Y23]['pct'][f]) if f != 'CS' else '—'] for pr in CIU for f in FV[pr]]
                + [[CIU[pr], 'Participación', p(AG[pr][Y19]['part']), p(AG[pr][Y23]['part'])] for pr in CIU]))
assert abs(AG['52'][Y23]['pct']['CPM'] - 4.75) < .05, AG['52'][Y23]['pct']['CPM']

FR = ('PP', 'PSOE', 'VOX')
g_ren = figura(f'En el tercio de secciones con menos renta de Ceuta, el PSOE sacó el {p(TB["PSOE"])} % en 2023; en el de más renta, el PP, el {p(TA["PP"])} %',
               'Voto al PP, al PSOE y a Vox en julio de 2023 según la renta de la sección: cada ciudad, partida en tres grupos con el mismo número de secciones, en %',
               ''.join(f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{CIU[pr]}</p>'
                       + grupos([(t, [(TER[pr][t][Y23]['pct'][f], COLC[f], 1, NOMC[f]) for f in FR]) for t in TER[pr]], 80, f'Voto por renta en {CIU[pr]}', W=440, ml=110)
                       for pr in CIU),
               'Fuente: Ministerio del Interior, sin voto exterior; renta por unidad de consumo del Atlas de Distribución de Renta de los Hogares del INE (2023). Cálculo propio. '
               'Son secciones, no personas: no dicen quién vota a quién dentro de cada una.',
               [(NOMC[f], COLC[f]) for f in FR],
               (['Ciudad', 'Grupo', 'Secciones', 'Renta por unidad de consumo (€)', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Participación 2023 (%)'],
                [[CIU[pr], t, str(x['n']), f'{n(x["rmin"])}-{n(x["rmax"])}', p(x[Y23]['pct']['PP']), p(x[Y23]['pct']['PSOE']), p(x[Y23]['pct']['VOX']), p(x[Y23]['part'])]
                 for pr in CIU for t, x in TER[pr].items()]))

FE = [('Noviembre de 2019', {pr: ESC[Y19][pr] for pr in CIU}), ('Julio de 2023', {pr: ESC[Y23][pr] for pr in CIU}),
      ('29N, media de encuestas', {pr: {max(RC[pr], key=lambda f: RC[pr][f][0]): 1} for pr in CIU})]


def cuadros(lado=22):
    out, y = [], 0
    for j, (nom, e) in enumerate(FE):
        out.append(f'<text x="0" y="{y + 14}" class="lab">{esc(nom)}</text>')
        y += 22
        for i, pr in enumerate(CIU):
            f = list(e[pr])[0]
            if j == 2 and pr == '51':   # Ceuta, 29N: empate técnico entre el PP y Vox, medio cuadrado cada uno
                out.append(f'<rect x="0" y="{y}" width="{lado / 2}" height="{lado}" fill="{COLC["PP"]}"><title>Ceuta, 29N: PP, primero en el {p(PRIM["51"]["PP"])} % de las simulaciones</title></rect>'
                           f'<rect x="{lado / 2}" y="{y}" width="{lado / 2}" height="{lado}" fill="{COLC["VOX"]}"><title>Ceuta, 29N: Vox, primero en el {p(PRIM["51"]["VOX"])} % de las simulaciones</title></rect>'
                           f'<text x="{lado + 8}" y="{y + 16}" class="lab">Ceuta: PP o Vox</text>')
                continue
            out.append(f'<rect x="{i * 150}" y="{y}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{CIU[pr]}, {esc(nom)}: {NOMC[f]}</title></rect>'
                       f'<text x="{i * 150 + lado + 8}" y="{y + 16}" class="lab">{CIU[pr]}: {NOMC[f]}</text>')
        y += lado + 14
    return f'<svg viewBox="0 0 320 {y}" style="max-width:640px" role="img" aria-label="Diputado de Ceuta y de Melilla en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, el PP tiene Melilla casi segura; en Ceuta, el PP y Vox están prácticamente empatados',
               f'El diputado de Ceuta y el de Melilla: un cuadrado por escaño. En Ceuta, el PP queda primero en el {p(PRIM["51"]["PP"])} % de las simulaciones y Vox, en el {p(PRIM["51"]["VOX"])} %',
               cuadros(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, voto central y 2.000 simulaciones '
               f'(<a href="{BASE}encuestas/ceuta/">/encuestas/ceuta/</a> y <a href="{BASE}encuestas/melilla/">/encuestas/melilla/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in FR],
               (['Ciudad', 'Nov. 2019', '2023', '29N: voto central (%)', '29N: primero en las simulaciones (%)'],
                [[CIU[pr], NOMC[list(ESC[Y19][pr])[0]], NOMC[list(ESC[Y23][pr])[0]],
                  ', '.join(f'{NOMC[f]} {p(VC[pr][f])}' for f in ('PP', 'VOX', 'PSOE')),
                  ', '.join(f'{NOMC[f]} {p(PRIM[pr][f])}' for f in ('PP', 'VOX', 'PSOE'))] for pr in CIU]))

CAJA = {'51': (-5.38, 35.86, -5.27, 35.92), '52': (-2.98, 35.26, -2.92, 35.32)}
g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada sección censal de Ceuta y de Melilla</span>'
         '<span class="s">Pasa por encima o toca una sección para ver su resultado y cambia de elección en el selector</span></figcaption>\n'
         + ''.join(f'<p style="margin:.8em 0 .2em;font-weight:700;font-size:.95em">{CIU[pr]}</p><div class="chart">{insertado(CAJA[pr], f"Mapa electoral de {CIU[pr]} por sección censal", alto=440)}</div>\n' for pr in CIU)
         + f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=51001">Ceuta</a> y <a href="{BASE}?m=52001">Melilla</a> a pantalla completa · '
         f'datos de <a href="{BASE}elecciones/ceuta/">Ceuta</a> y de <a href="{BASE}elecciones/melilla/">Melilla</a></div>\n</figure>\n')

# --- Texto ---
CTV = 'https://www.ceutatv.com/politica/vox-presenta-candidatos-situa-soberania-seguridad-centro-29n/20261106185851259905.html'
COPEM = 'https://copemelilla.com/actualidad/coalicion-por-melilla-cpm-ha-anunciado-que-no-concurrira-a-las-elecciones-generales-y-ha-pedido-a-los-melillenses-que-respalden-la-candidatura-de-pedro-sanchez/224198'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
A51, A52 = AG['51'], AG['52']
TM = TER['52']

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Ceuta y Melilla eligen el 29 de noviembre un diputado cada una, el que más votos saque. En Ceuta se presentan, entre otros, Rafael Martínez Peñalver por el PP, Luis Manuel Tovar por el PSOE y Ana Belén Cifuentes por Vox; en Melilla, Sofía Acedo por el PP, Riduan Moh por el PSOE y José Miguel Tasende por Vox, según las <a href="{BASE}listas-electorales-29n/">listas proclamadas en el BOE</a>. Coalición por Melilla no se presenta y ha pedido el voto para Pedro Sánchez, según <a href="{COPEM}">COPE Melilla</a>. Al presentar su candidatura, Cifuentes dijo que «está en juego no solo recuperar la normalidad, sino la propia soberanía española de Ceuta», según <a href="{CTV}">Ceuta TV</a>.</p>
<p data-tipo="dato">En noviembre de 2019, Vox fue el partido más votado en Ceuta, con {n(M19["51"])} votos más que el PSOE (sin el voto exterior), y ganó en {GS["51"][Y19]["VOX"]} de sus 56 secciones censales. En julio de 2023 bajó del {p(A51[Y19]["pct"]["VOX"])} % al {p(A51[Y23]["pct"]["VOX"])} % y no ganó en ninguna: {TRN["51"]["VOX>PP"]} pasaron al PP y {NW[TRN["51"]["VOX>PSOE"]]} al PSOE. El PP, que en 2019 había sacado el {p(A51[Y19]["pct"]["PP"])} %, subió al {p(A51[Y23]["pct"]["PP"])} % y ganó el escaño por {n(M23["51"])} votos sobre el PSOE.</p>
{g_ins}
{g_ceu}
<p data-tipo="dato">En Melilla, el PP ganó en 2019 por {n(M19["52"])} votos a Coalición por Melilla, que sacó el {p(A52[Y19]["pct"]["CPM"])} % y fue la más votada en {GS["52"][Y19]["CPM"]} de las 44 secciones. En 2023, Coalición por Melilla bajó al {p(A52[Y23]["pct"]["CPM"])} % y no ganó ninguna. De sus {GS["52"][Y19]["CPM"]} secciones, {TRN["52"]["CPM>PSOE"]} fueron al PSOE y {NW[TRN["52"]["CPM>PP"]]} al PP. El PSOE subió del {p(A52[Y19]["pct"]["PSOE"])} % al {p(A52[Y23]["pct"]["PSOE"])} %, y el PP, del {p(A52[Y19]["pct"]["PP"])} % al {p(A52[Y23]["pct"]["PP"])} %, que le dio el escaño por {n(M23["52"])} votos. La participación bajó del {p(A52[Y19]["part"])} % al {p(A52[Y23]["part"])} %.</p>
{g_mel}
{g_vot}
<h2>La renta de cada sección</h2>
<p data-tipo="patron">En las dos ciudades, las secciones que ganó el PSOE en 2023 tienen mucha menos renta que las del PP. En Ceuta, la renta mediana por unidad de consumo de las secciones del PSOE era de {n(RM["51"]["g23"]["PSOE"])} euros y la de las del PP, de {n(RM["51"]["g23"]["PP"])}; en Melilla, de {n(RM["52"]["g23"]["PSOE"])} y {n(RM["52"]["g23"]["PP"])}. En el tercio de secciones con menos renta de Ceuta, el PSOE sacó el {p(TB["PSOE"])} %; en el de más renta, el PP sacó el {p(TA["PP"])} % y Vox, el {p(TA["VOX"])} %. En Melilla, el PSOE sacó el {p(TM["Renta baja"][Y23]["pct"]["PSOE"])} % en el tercio de menos renta, donde en 2019 Coalición por Melilla había sacado el {p(TM["Renta baja"][Y19]["pct"]["CPM"])} %. Cuánto vota cada barrio de las dos ciudades está en {L("ceuta-melilla-participacion-29n", "esta pieza")}.</p>
{g_ren}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el PP tiene Melilla casi segura: queda primero en el {p(PRIM["52"]["PP"])} % de las simulaciones. En Ceuta, el PP y Vox están prácticamente empatados: el voto central es del {p(VC["51"]["PP"])} % para el PP y del {p(VC["51"]["VOX"])} % para Vox, y el PP queda primero en el {p(PRIM["51"]["PP"])} % de las simulaciones, Vox en el {p(PRIM["51"]["VOX"])} % y el PSOE en el {p(PRIM["51"]["PSOE"])} %. Con un solo escaño no hay reparto: se lo lleva la lista más votada, aunque sea por pocos votos, como los {n(M19["52"])} con que el PP ganó Melilla en 2019.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por sección, no de personas: no dicen qué hizo en 2023 cada votante de Vox en Ceuta o de Coalición por Melilla en Melilla. Que el PSOE ganara en 2023 las secciones donde Coalición por Melilla había sido la más votada encaja con que recogiera parte de sus votos, pero el mapa no permite separarlo de otros movimientos, como la participación, que en Melilla bajó. La relación entre renta y voto es entre secciones, no entre personas. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de las dos ciudades desde 1977 está en {L("ceuta-historia-electoral", "Ceuta en las urnas")} y {L("melilla-historia-electoral", "Melilla en las urnas")}. Los datos de cada sección y su serie desde 1977 están en las fichas de <a href="{BASE}elecciones/ceuta/">Ceuta</a> y de <a href="{BASE}elecciones/melilla/">Melilla</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Ceuta?',
     f'El PP, con el {p(A51[Y23]["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A51[Y23]["pct"]["PSOE"])} %) y Vox ({p(A51[Y23]["pct"]["VOX"])} %). '
     f'En noviembre de 2019 había ganado Vox, con el {p(A51[Y19]["pct"]["VOX"])} %.'),
    ('¿Quién ganó las elecciones generales de 2023 en Melilla?',
     f'El PP, con el {p(A52[Y23]["pct"]["PP"])} %, por delante del PSOE ({p(A52[Y23]["pct"]["PSOE"])} %) y Vox ({p(A52[Y23]["pct"]["VOX"])} %). En noviembre de 2019 también ganó el PP, por {n(M19["52"])} votos sobre Coalición por Melilla.'),
    ('¿Cuántos diputados eligen Ceuta y Melilla el 29N?',
     'Uno cada una. Gana el escaño la lista más votada.'),
    ('¿Se presenta Coalición por Melilla el 29N?',
     'No. Ha pedido el voto para Pedro Sánchez, según COPE Melilla.'),
    ('¿Qué dicen las encuestas en Ceuta y Melilla?',
     f'Con la media de encuestas de Mapa Electoral, el PP queda primero en Melilla en el {p(PRIM["52"]["PP"])} % de las simulaciones. En Ceuta, el PP y Vox están prácticamente empatados: el PP queda primero en el {p(PRIM["51"]["PP"])} % y Vox, en el {p(PRIM["51"]["VOX"])} %.'),
]
enlaces = (f'{L("ceuta-historia-electoral", "Historia electoral de Ceuta")} · {L("melilla-historia-electoral", "Historia electoral de Melilla")} · '
           f'<a href="{BASE}encuestas/ceuta/">Encuesta en Ceuta</a> · <a href="{BASE}encuestas/melilla/">Encuesta en Melilla</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata), sumados por sección censal (sin voto exterior); '
        'renta del Atlas de Distribución de Renta de los Hogares del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_ceuta_melilla.py.')

R = lambda v: round(float(v), 4)
DATOS = {'AG': AG, 'M19': M19, 'M23': M23, 'GS': GS, 'TRN': TRN, 'RM': {pr: {y: {f: R(v) for f, v in d.items()} for y, d in x.items()} for pr, x in RM.items()},
         'TER': TER, 'RC': RC, 'PRIM': PRIM, 'VC': VC, 'ESC': {y: ESC[y] for y in (Y19, Y23)},
         'AJ': [[x.tract_code, x.g, x.seg, int(x.marg)] for _, x in AJ.iterrows()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Ceuta y Melilla',
      f'El mapa electoral de Ceuta y Melilla: Vox pasó de ganar {GS["51"][Y19]["VOX"]} secciones de Ceuta a ninguna, y {TRN["52"]["CPM>PSOE"]} de las {GS["52"][Y19]["CPM"]} de Coalición por Melilla fueron al PSOE',
      f'En 2019, Vox ganó el escaño de Ceuta y Coalición por Melilla se quedó a {n(M19["52"])} votos del de Melilla. En 2023, el PP ganó los dos. '
      f'Para el 29N, con la media de encuestas, el PP tiene Melilla casi segura ({p(PRIM["52"]["PP"])} % de las simulaciones) y en Ceuta está prácticamente empatado con Vox ({p(VC["51"]["PP"])} % frente a {p(VC["51"]["VOX"])} %).',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
