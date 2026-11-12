"""«El mapa electoral de Canarias» (2026-11), novena pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 88 municipios de Canarias en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas
por separado: en 2019, Unidas Podemos y Más País; Coalición Canaria fue con Nueva Canarias en 2019 y por separado en
2023), las siete islas, el tamaño de los municipios (padrón de 2023), las dos capitales, los más ajustados y el reparto
central del modelo de /encuestas/ para el 29N. En 2023, Vox no tuvo lista en Santa Cruz de Tenerife (vox_tenerife.py).
Contexto: Canarias7 (Cristina Valido, 23-10-2026) y elDiario.es / Canarias Ahora (Teodoro Sosa, 7-11-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_canarias.py
"""
import json
import sys

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

sys.path.insert(0, str(RAIZ / 'generales-2026' / 'src'))
from partidos import PROPIAS  # noqa: E402

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-canarias-29n'
PROV = {'35': 'Las Palmas', '38': 'Santa Cruz de Tenerife'}
PSLUG = {'35': 'las-palmas', '38': 'santa-cruz-de-tenerife'}
CAPITAL = {'35016': 'Las Palmas de Gran Canaria', '38038': 'Santa Cruz de Tenerife'}
CAJA = (-18.2, 27.6, -13.3, 29.45)
COLC = dict(COL, NC=next(c for k, _, c in PROPIAS if k == 'NC'))
NOMC = dict(NOM, EMPATE='Empate a votos', NC='Nueva Canarias', CC='Coalición Canaria')
SIMC = {'Nueva Canarias': 'NC'}
ISLA = {'Tenerife': None, 'Gran Canaria': None,
        'Lanzarote': ['35004', '35010', '35018', '35024', '35028', '35029', '35034'],
        'Fuerteventura': ['35003', '35007', '35014', '35015', '35017', '35030'],
        'La Palma': ['38007', '38008', '38009', '38014', '38016', '38024', '38027', '38029', '38030', '38033', '38037', '38045', '38047', '38053'],
        'La Gomera': ['38002', '38003', '38021', '38036', '38049', '38050'],
        'El Hierro': ['38013', '38048', '38901']}

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 88
NOMM = dict(zip(m.mun_code, m.municipio))
assert all(NOMM[k] == v for k, v in CAPITAL.items())
_resto = {x for v in ISLA.values() if v for x in v}
ISLA['Tenerife'] = sorted(set(m[m.prov == '38'].mun_code) - _resto)
ISLA['Gran Canaria'] = sorted(set(m[m.prov == '35'].mun_code) - _resto)
assert {k: len(v) for k, v in ISLA.items()} == {'Tenerife': 31, 'Gran Canaria': 21, 'Lanzarote': 7, 'Fuerteventura': 6, 'La Palma': 14, 'La Gomera': 6, 'El Hierro': 3}
assert NOMM['35004'] == 'Arrecife' and NOMM['35017'] == 'Puerto del Rosario' and NOMM['38037'] == 'Santa Cruz de la Palma' and NOMM['38013'] == 'Frontera'
m['isla'] = m.mun_code.map({x: k for k, v in ISLA.items() for x in v})
L19, L23 = ('PSOE', 'PP', 'VOX', 'UP', 'MP', 'CS', 'CC'), ('PSOE', 'PP', 'VOX', 'SUMAR', 'CC', 'NC')
assert m[f'{Y19}_vNC'].sum() == 0 if f'{Y19}_vNC' in m else True   # en 2019, NC fue en la lista de CC
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 69, 'PP': 12, 'CC': 7}, GANA[Y19]
assert GANA[Y23] == {'PP': 42, 'PSOE': 41, 'CC': 3, 'NC': 2}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, PP_PSOE, CC_PP = TR('PSOE', 'PP'), TR('PP', 'PSOE'), TR('CC', 'PP')
assert (PSOE_PP, PP_PSOE, CC_PP) == (28, 1, 3)
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
assert DPSOE_VOTOS == 66510 and DPP_VOTOS == 113041
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
assert PSOE_SUBE == 71
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PSOE', 'PP')} for y in (Y19, Y23)}
assert round(POB[Y19]['PSOE'], 1) == 91.6 and round(POB[Y23]['PSOE'], 1) == 59.0 and round(POB[Y23]['PP'], 1) == 38.8
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FL_TF = int((FL.isla == 'Tenerife').sum())
assert FL_TF == 18, FL_TF
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Islas
IS = {}
for isla, cods in ISLA.items():
    g = m[m.mun_code.isin(cods)]
    IS[isla] = {'n': len(g), 'g19': g.g2019.value_counts().to_dict(), 'g23': g.g2023.value_counts().to_dict(),
                'p19': agrega(g, Y19, L19)['pct'], 'p23': agrega(g, Y23, L23)['pct']}
assert IS['Tenerife']['g19'] == {'PSOE': 26, 'CC': 3, 'PP': 2} and IS['Tenerife']['g23'] == {'PP': 23, 'PSOE': 8}
assert IS['Gran Canaria']['g19'] == {'PSOE': 15, 'PP': 6} and IS['Gran Canaria']['g23'] == {'PSOE': 13, 'PP': 6, 'NC': 2}
assert IS['Lanzarote']['g23'] == {'PSOE': 7} and IS['La Palma']['g23'] == {'PP': 7, 'PSOE': 5, 'CC': 2}
assert IS['La Gomera']['g19'] == {'PSOE': 6} and IS['La Gomera']['g23'] == {'PSOE': 4, 'PP': 2} and IS['El Hierro']['g23'] == {'PP': 2, 'PSOE': 1}
assert IS['El Hierro']['g19'] == {'PSOE': 3} and IS['Lanzarote']['n'] == 7 and IS['La Palma']['g19']['PP'] == 3
assert m[f'{Y23}_vCS'].sum() == 0
assert IS['Tenerife']['p23']['VOX'] == 0 and IS['Gran Canaria']['p23']['VOX'] > IS['Gran Canaria']['p19']['VOX']
NC23 = sorted(m[m.g2023 == 'NC'].municipio)
assert NC23 == ['Gáldar', 'Santa María de Guía de Gran Canaria'] and set(m[m.g2023 == 'NC'].g2019) == {'PSOE'}
CC23 = sorted(m[m.g2023 == 'CC'].municipio)
assert CC23 == ['Betancuria', 'El Paso', 'Fuencaliente de la Palma']

# Tamaño de municipio
TAM = [('Menos de 5.000', 0, 5000), ('De 5.000 a 20.000', 5000, 20000), ('De 20.000 a 100.000', 20000, 100000), ('Más de 100.000', 100000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'CC')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'CC', 'NC', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
G20 = m[m.poblacion >= 20000]
G20N = len(G20)
G20G = {y: G20[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert G20N == 30 and G20G[Y19] == {'PSOE': 28, 'PP': 1, 'CC': 1} and G20G[Y23] == {'PSOE': 15, 'PP': 14, 'NC': 1}, G20G
TM = TT['Más de 100.000']
assert TM['n'] == 4 and TM['g19'] == {'PSOE': 4} and TM['g23'] == {'PSOE': 3, 'PP': 1}, TM

# Capitales y La Laguna
CAP = m[m.mun_code.isin(list(CAPITAL) + ['38023'])].sort_values('poblacion', ascending=False)
CI = CAP.set_index('mun_code')
LPA, SCT, LAG = CI.loc['35016'], CI.loc['38038'], CI.loc['38023']
assert (LPA.g2019, LPA.g2023, SCT.g2019, SCT.g2023, LAG.g2019, LAG.g2023) == ('PSOE', 'PSOE', 'PSOE', 'PP', 'PSOE', 'PSOE')
assert SCT.seg2023 == 'PSOE' and LPA.seg2023 == 'PP' and LAG.seg2023 == 'PP'

# Provincias
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}

assert PRS['35'][Y23]['pct']['VOX'] > PRS['35'][Y19]['pct']['VOX'] and PRS['38'][Y23]['pct']['VOX'] == 0
assert sorted(G20[(G20.poblacion >= 100000) & (G20.g2023 == 'PSOE')].municipio) == ['Las Palmas de Gran Canaria', 'San Cristóbal de La Laguna', 'Telde']

# Municipios ajustados
AJG = m[m.poblacion >= 5000].sort_values('marg2023').head(10)
assert AJG.iloc[0].municipio == 'La Oliva' and int(AJG.iloc[0].margv2023) == 17 and AJG.iloc[1].municipio == 'Valsequillo de Gran Canaria' and int(AJG.iloc[1].margv2023) == 17
ORO = m[m.municipio == 'La Orotava'].iloc[0]
assert ORO.g2019 == 'CC' and ORO.g2023 == 'PP' and ORO.seg2023 == 'PSOE' and int(ORO.margv2023) == 118
UNVOTO = int((m.margv2023 == 1).sum())
GAR = m[m.margv2023 == 1].iloc[0]
assert UNVOTO == 1 and GAR.municipio == 'Garafía' and GAR.g2023 == 'PP' and GAR.seg2023 == 'PSOE'

# Escaños
ESC = escanos_oficiales(list(PROV))
F6 = ('PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'CC', 'NC')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F6}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F6}
assert E19 == {'PSOE': 5, 'PP': 4, 'VOX': 2, 'UP': 2, 'SUMAR': 0, 'CC': 2, 'NC': 0}, E19
assert E23 == {'PSOE': 6, 'PP': 6, 'VOX': 1, 'UP': 0, 'SUMAR': 1, 'CC': 1, 'NC': 0}, E23
assert ESC['2026'] == {'35': 8, '38': 7} and ESC[Y23]['38'].get('VOX', 0) == 0
RC = {pr: {SIMC.get(k, k): v for k, v in reparto_central(PSLUG[pr]).items()} for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F6}
assert sum(E29.values()) == 15 and set().union(*RC.values()) <= set(F6), (E29, RC)
assert E29 == {'PSOE': 5, 'PP': 4, 'VOX': 4, 'UP': 0, 'SUMAR': 1, 'CC': 1, 'NC': 0}, E29
assert RC['38']['VOX'][0] == 2 and RC['35']['VOX'][0] == 2 and RC['35']['NC'] == (0, 0, 1)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=28.3, umbral=1.0)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP', 'CC', 'NC']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}, y el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Canarias, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Canarias por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Canarias por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura. En 2019, Coalición Canaria se presentó con Nueva Canarias (CCa-PNC-NC); en 2023, por separado. '
                  'En 2023, Vox no tuvo lista en Santa Cruz de Tenerife.',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f] + (' (en 2019, con NC)' if f == 'CC' else ''), n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

ORDI = list(ISLA)
g_isla = figura(f'En Tenerife, el PP pasó de ganar en {NW[IS["Tenerife"]["g19"]["PP"]]} municipios a ganar en {IS["Tenerife"]["g23"]["PP"]}; en Gran Canaria, el PSOE conservó {IS["Gran Canaria"]["g23"]["PSOE"]} de {IS["Gran Canaria"]["n"]}',
                'Municipios ganados por cada partido en cada isla, en noviembre de 2019 y en julio de 2023',
                apiladas([(f'{isla} · {y[:4]}', [(IS[isla][g].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if IS[isla][g].get(f, 0)])
                          for isla in ORDI for y, g in ((Y19, 'g19'), (Y23, 'g23'))],
                         'Municipios ganados por cada partido en cada isla', W=440, ml=150),
                'Fuente: Ministerio del Interior, sin voto exterior. En 2019, Coalición Canaria fue con Nueva Canarias. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in ORDG],
                (['Isla', 'Municipios', 'PSOE 2019', 'PP 2019', 'CC 2019', 'PSOE 2023', 'PP 2023', 'CC 2023', 'NC 2023',
                  'PSOE 2023 (%)', 'PP 2023 (%)', 'CC 2023 (%)', 'Vox 2023 (%)'],
                 [[isla, n(IS[isla]['n'])] + [n(IS[isla]['g19'].get(f, 0)) for f in ('PSOE', 'PP', 'CC')] + [n(IS[isla]['g23'].get(f, 0)) for f in ORDG]
                  + [p(IS[isla]['p23'][f]) for f in ('PSOE', 'PP', 'CC')] + [p(IS[isla]['p23']['VOX']) if IS[isla]['p23']['VOX'] else 'sin lista'] for isla in ORDI]))

FF = ('PSOE', 'PP', 'VOX', 'CC')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PSOE, al PP, a Vox y a Coalición Canaria en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f] if f != 'CC' else 'CC', [(FLS[Y19][f], COLC[f], .38, 'nov. 2019'), (FLS[Y23][f], COLC[f], 1, '2023')]) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                f'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. {FL_TF} de los {PSOE_PP} '
                'están en Tenerife, donde Vox no tuvo lista en 2023. CC fue con Nueva Canarias en 2019. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f])] for f in FF]
                 + [['Ciudadanos', p(FLS[Y19]['CS']), '—'], ['Unidas Podemos (2019) / Sumar (2023)', p(FLS[Y19]['UP']), p(FLS[Y23]['SUMAR'])]]))

g_tam = figura(f'En los {G20N} municipios de más de 20.000 habitantes, el PSOE pasó de ganar en {G20G[Y19]["PSOE"]} a ganar en {G20G[Y23]["PSOE"]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=180),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'CC 2019', 'PSOE 2023', 'PP 2023', 'CC 2023', 'NC 2023',
                 'PSOE 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP', 'CC')] + [n(t['g23'].get(f, 0)) for f in ORDG]
                 + [p(t['psoe23']), p(t['pp23'])] for nom, t in TT.items()]))

g_cap = figura('El PP ganó en Santa Cruz de Tenerife en 2023; el PSOE conservó Las Palmas de Gran Canaria y La Laguna',
               'Voto al PSOE y al PP en julio de 2023 en las tres ciudades más pobladas, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio.replace('San Cristóbal de ', '').replace(' de Gran Canaria', ''),
                        [(r[f'{Y19}%PSOE'], COLC['PSOE'], .38, 'PSOE, nov. 2019'), (r[f'{Y23}%PSOE'], COLC['PSOE'], 1, 'PSOE, 2023'),
                         (r[f'{Y19}%PP'], COLC['PP'], .38, 'PP, nov. 2019'), (r[f'{Y23}%PP'], COLC['PP'], 1, 'PP, 2023')]) for _, r in CAP.iterrows()],
                      45, 'Voto al PSOE y al PP en las tres ciudades más pobladas', W=440, ml=150),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. En 2023, Vox no tuvo lista en Santa Cruz de Tenerife ni en La Laguna. Cálculo propio.',
               [('PSOE', COLC['PSOE']), ('PP', COLC['PP']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (puntos)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'PP nov. 2019 (%)', 'PP 2023 (%)',
                 'Vox nov. 2019 (%)', 'Vox 2023 (%)'],
                [[r.municipio, NOMC[r.g2019], NOMC[r.g2023], n(r.marg2023, 2), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']), p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']),
                  p(r[f'{Y19}%VOX']), p(r[f'{Y23}%VOX']) if r[f'{Y23}%VOX'] else 'sin lista'] for _, r in CAP.iterrows()]))

g_aj = figura(f'La Oliva y Valsequillo se decidieron por {int(AJG.iloc[0].margv2023)} votos cada uno',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios de más de 5.000 habitantes más ajustados, en puntos',
              barras([(r.municipio.replace(' de Gran Canaria', ''), r.marg2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()],
                     max(AJG.marg2023) * 1.15, 'Municipios de más de 5.000 habitantes más ajustados en 2023', W=440, ml=170, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in sorted(set(AJG.g2023), key=ORDG.index)],
              (['Municipio', 'Isla', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, r.isla, NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'CC', 'NC']


def hemi(lado=16, por_fila=8):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Canarias en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PSOE', 'PP', 'VOX', 'SUMAR', 'CC', 'NC')
g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en Canarias, con lista otra vez en Santa Cruz de Tenerife',
               'Los 15 diputados de las dos provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/las-palmas/">/encuestas/</a>) {VERSION}. En 2019, Coalición Canaria fue con Nueva Canarias; el modelo reparte '
               'por separado a Sumar y a Nueva Canarias, que el 29N van juntas en Unidad del Pueblo Canario.',
               [(NOMC[f], COLC[f]) for f in ORDE if any(e.get(f, 0) for _, e in FE)],
               (['Provincia'] + [f'{NOMC[f] if f not in ("CC", "NC") else f} 2023' for f in FT] + [f'{NOMC[f] if f not in ("CC", "NC") else f} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in FT]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in FT] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Canarias</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Canarias por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=35016">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/canarias/">datos de cada municipio de Canarias</a></div>\n</figure>\n')

# --- Texto ---
VAL = 'https://www.canarias7.es/elecciones/generales/valido-unica-mision-unica-causa-canarias-izquierda-20261023170635-nt.html'
SOS = 'https://www.eldiario.es/canariasahora/politica/cc-canarias-presenta-candidaturas-29n-objetivo-recuperar-grupo-propio-congreso_1_13646935.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
TF, GC = IS['Tenerife'], IS['Gran Canaria']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Canarias elige el 29 de noviembre 15 diputados: {ESC["2026"]["35"]} en Las Palmas y {ESC["2026"]["38"]} en Santa Cruz de Tenerife. Coalición Canaria se presenta con Primero Canarias, con Cristina Valido al frente en Santa Cruz de Tenerife, que resumió su campaña así: «nuestra única misión y nuestra única causa es Canarias. Ni la izquierda ni la derecha, Canarias es nuestro único objetivo», según <a href="{VAL}">Canarias7</a>. En Las Palmas encabeza la lista Teodoro Sosa, que prometió: «No haremos ministro a Santiago Abascal ni a la extrema derecha», según <a href="{SOS}">Canarias Ahora</a>. Nueva Canarias, que en 2023 fue sola, va ahora con Podemos, IU y Sumar en Unidad del Pueblo Canario, como se cuenta en {L("canarias-unidad-pueblo-canario-29n", "esta pieza")}.</p>
<p data-tipo="dato">El mapa municipio a municipio cambió de color. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios canarios, el PP en {GANA[Y19]["PP"]} y Coalición Canaria, que entonces iba con Nueva Canarias, en {NW[GANA[Y19]["CC"]]}. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]}, el PSOE en {GANA[Y23]["PSOE"]}, Coalición Canaria en {NW[GANA[Y23]["CC"]]} y Nueva Canarias en {NW[GANA[Y23]["NC"]]}, Gáldar y Santa María de Guía. El vuelco se concentró en Tenerife: el PP pasó de ganar en {NW[TF["g19"]["PP"]]} de sus {TF["n"]} municipios a ganar en {TF["g23"]["PP"]}, incluida la capital, Santa Cruz de Tenerife.</p>
{g_ins}
<p data-tipo="dato">El PSOE no bajó: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DPSOE_VOTOS)} votos más, y subió en {PSOE_SUBE} de los {NMUN} municipios. Pero el PP sumó {n(DPP_VOTOS)} votos y pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %. Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} % en el conjunto de Canarias, pero porque en 2023 no tuvo lista en Santa Cruz de Tenerife: en Las Palmas subió, como se cuenta en {L("vox-vuelve-tenerife-29n", "Vox vuelve a la papeleta en Santa Cruz de Tenerife")}. Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<h2>Siete islas</h2>
<p data-tipo="patron">En Tenerife, el PSOE pasó de {TF["g19"]["PSOE"]} municipios a {NW[TF["g23"]["PSOE"]]}, y Coalición Canaria perdió los {NW[TF["g19"]["CC"]]} que tenía. En Gran Canaria, en cambio, el PSOE conservó {GC["g23"]["PSOE"]} de los {GC["n"]} municipios y el PP se quedó en los mismos {NW[GC["g23"]["PP"]]}. En Lanzarote, el PSOE ganó en los {NW[IS["Lanzarote"]["n"]]}. En La Palma, el PP pasó de {NW[IS["La Palma"]["g19"]["PP"]]} a {NW[IS["La Palma"]["g23"]["PP"]]} municipios, y en La Gomera y en El Hierro, donde el PSOE había ganado en todos en 2019, el PP ganó en {NW[IS["La Gomera"]["g23"]["PP"]]} y en {NW[IS["El Hierro"]["g23"]["PP"]]}.</p>
{g_isla}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP, {FL_TF} de ellos en Tenerife; solo {NW[PP_PSOE]} hizo el camino contrario. En esos {PSOE_PP}, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP lo hizo del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecían Ciudadanos y, en Tenerife, la papeleta de Vox. Como el PSOE perdió sobre todo en Tenerife, los municipios que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población de Canarias al {p(POB[Y23]["PSOE"])} %, y los del PP, del {p(POB[Y19]["PP"])} % al {p(POB[Y23]["PP"])} %.</p>
{g_flip}
<h2>Las ciudades</h2>
<p data-tipo="dato">En los {G20N} municipios de más de 20.000 habitantes, el PSOE ganó en {G20G[Y19]["PSOE"]} en 2019 y en {G20G[Y23]["PSOE"]} en 2023; el PP, en {NW[G20G[Y19]["PP"]]} y en {G20G[Y23]["PP"]}. De las cuatro ciudades de más de 100.000, el PSOE conservó Las Palmas de Gran Canaria, La Laguna y Telde, y perdió Santa Cruz de Tenerife, que ganó el PP por {n(SCT.marg2023, 2)} puntos. En Las Palmas de Gran Canaria, el PSOE sacó {n(LPA.marg2023, 2)} puntos al PP, y en La Laguna, {n(LAG.marg2023, 2)}.</p>
{g_tam}
{g_cap}
<h2>Los más ajustados</h2>
<p data-tipo="dato">Entre los municipios de más de 5.000 habitantes, los más ajustados de 2023 fueron La Oliva (Fuerteventura), que ganó el PP, y Valsequillo de Gran Canaria, que ganó el PSOE, los dos por {int(AJG.iloc[0].margv2023)} votos. La Orotava, que en 2019 había ganado Coalición Canaria, la ganó el PP por {int(ORO.margv2023)} votos sobre el PSOE. En Garafía (La Palma), el PP sacó un solo voto al PSOE.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 15 escaños da al PSOE {E29["PSOE"]}, uno menos que en 2023; al PP, {E29["PP"]}, {NW[E23["PP"] - E29["PP"]]} menos; a Vox, {E29["VOX"]}, {NW[RC["35"]["VOX"][0]]} en cada provincia, frente a {NW[E23["VOX"]]} en 2023; a Sumar, {NW[E29["SUMAR"]]}, y a Coalición Canaria, {NW[E29["CC"]]}. El modelo aún trata por separado a Sumar y a Nueva Canarias, que el 29N concurren juntos en Unidad del Pueblo Canario, así que su reparto en Canarias es más incierto que en otras comunidades.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hicieron en 2023 los votantes de Vox en Tenerife, donde no tuvo lista, ni los de Ciudadanos. Que el PP subiera mucho más en Tenerife que en Gran Canaria encaja con que recogiera parte de ese voto, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. Coalición Canaria y Nueva Canarias fueron juntas en 2019 y separadas en 2023, así que sus cifras no se pueden comparar directamente. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de Canarias desde 1977, con las autonómicas, está en {L("canarias-historia-electoral", "Canarias en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/canarias/">la ficha de Canarias</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Canarias?',
     f'El PSOE, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante del PP ({p(A23["pct"]["PP"])} %), Coalición Canaria ({p(A23["pct"]["CC"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %), Vox ({p(A23["pct"]["VOX"])} %, solo en Las Palmas) y Nueva Canarias ({p(A23["pct"]["NC"])} %). '
     f'El PSOE y el PP sacaron {NW[E23["PSOE"]]} diputados cada uno, y Vox, Sumar y Coalición Canaria, uno.'),
    ('¿En cuántos municipios de Canarias ganó el PP en 2023?',
     f'En {GANA[Y23]["PP"]} de {NMUN}; el PSOE, en {GANA[Y23]["PSOE"]}; Coalición Canaria, en {NW[GANA[Y23]["CC"]]}, y Nueva Canarias, en {NW[GANA[Y23]["NC"]]}. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]}, el PP en {GANA[Y19]["PP"]} y Coalición Canaria (con Nueva Canarias) en {NW[GANA[Y19]["CC"]]}.'),
    ('¿Quién ganó en Las Palmas de Gran Canaria y en Santa Cruz de Tenerife?',
     f'En julio de 2023, el PSOE ganó en Las Palmas de Gran Canaria, por {n(LPA.marg2023, 2)} puntos sobre el PP, y el PP en Santa Cruz de Tenerife, por {n(SCT.marg2023, 2)} sobre el PSOE. '
     'En noviembre de 2019, el PSOE había ganado en las dos.'),
    ('¿Cuántos diputados elige Canarias el 29N?',
     f'15, los mismos que en 2023: Las Palmas elige {ESC["2026"]["35"]} y Santa Cruz de Tenerife, {ESC["2026"]["38"]}.'),
    ('¿Qué dicen las encuestas en Canarias?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PSOE {E29["PSOE"]} escaños, al PP {E29["PP"]}, a Vox {E29["VOX"]}, a Sumar {NW[E29["SUMAR"]]} y a Coalición Canaria {NW[E29["CC"]]}, con un margen amplio.'),
]
enlaces = (f'{L("canarias-historia-electoral", "Historia electoral de Canarias")} · <a href="{BASE}elecciones/canarias/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/las-palmas/">Encuesta en Las Palmas</a> · <a href="{BASE}encuestas/santa-cruz-de-tenerife/">Encuesta en Santa Cruz de Tenerife</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_canarias.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PP_PSOE': PP_PSOE, 'FL_TF': FL_TF,
    'DPSOE_VOTOS': DPSOE_VOTOS, 'DPP_VOTOS': DPP_VOTOS, 'PSOE_SUBE': PSOE_SUBE, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'IS': IS, 'G20N': G20N, 'G20G': G20G,
    'CAP': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'marg23': R(r.marg2023)} for _, r in CAP.iterrows()},
    'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJG.iterrows()], 'ORO_V': int(ORO.margv2023), 'UNVOTO': UNVOTO,
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Canarias',
      f'El mapa electoral de Canarias: el PP pasó de ganar en {NW[TF["g19"]["PP"]]} municipios de Tenerife a {TF["g23"]["PP"]}, y el PSOE resistió en Gran Canaria',
      f'El PSOE subió en votos, pero pasó de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]} de los {NMUN} municipios canarios, y perdió Santa Cruz de Tenerife. '
      f'Para el 29N, la media de encuestas da al PSOE {E29["PSOE"]} de los 15 diputados, al PP {E29["PP"]} y a Vox {E29["VOX"]}, que vuelve a tener lista en Tenerife.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('FLS', {y: {k: round(v, 1) for k, v in FLS[y].items()} for y in FLS}, 'AJG', [(r.municipio, round(r.marg2023, 2), int(r.margv2023), r.g2023) for _, r in AJG.iterrows()])
print('TT', {k: (v['n'], v['g19'], v['g23']) for k, v in TT.items()})
