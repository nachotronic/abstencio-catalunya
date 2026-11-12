"""«El mapa electoral del País Vasco» (2026-11), octava pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 251 municipios del País Vasco en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(listas por separado: en 2019, Unidas Podemos y Más País, que solo se presentó en Bizkaia), el tamaño de los municipios
(padrón municipal del INE, 2023), las tres capitales, los tres territorios, los 60 municipios que pasaron del PNV a EH Bildu, los más
ajustados y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: Moncloa.com (listas del PNV, 17-10-2026; candidatura de EH Bildu, 16-10 y 19-10-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_pais_vasco.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-pais-vasco-29n'
PROV = {'48': 'Bizkaia', '20': 'Gipuzkoa', '01': 'Álava'}
PSLUG = {'48': 'bizkaia', '20': 'gipuzkoa', '01': 'alava'}
CAPITAL = {'48020': 'Bilbao', '01059': 'Vitoria-Gasteiz', '20069': 'Donostia/San Sebastián'}
CAJA = (-3.5, 42.45, -1.7, 43.45)
NOMC = dict(NOM, EMPATE='Empate a votos')
EHB = lambda d: {('BILDU' if k == 'EH Bildu' else k): v for k, v in d.items()}   # el simulador y el modelo dicen «EH Bildu»

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 251
NOMM = dict(zip(m.mun_code, m.municipio))
assert all(NOMM[k] == v for k, v in CAPITAL.items())
L19, L23 = ('PNV', 'BILDU', 'PSOE', 'PP', 'UP', 'MP', 'VOX', 'CS'), ('PNV', 'BILDU', 'PSOE', 'PP', 'SUMAR', 'VOX')
assert {pr for pr, v in m.groupby('prov')[f'{Y19}_vMP'].sum().items() if v > 0} == {'48'}   # Más País, solo en Bizkaia
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PNV': 152, 'BILDU': 79, 'PSOE': 13, 'PP': 4, 'UP': 2, 'EMPATE': 1}, GANA[Y19]
assert GANA[Y23] == {'BILDU': 140, 'PNV': 76, 'PSOE': 29, 'PP': 6}, GANA[Y23]
EMP19 = m[m.g2019 == 'EMPATE'].iloc[0]
assert EMP19.municipio == 'Gaintza' and EMP19.emp2019 == 'PNV-BILDU'
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PNV_BILDU, PNV_PSOE, PNV_PP, PNV_PNV, BILDU_BILDU = TR('PNV', 'BILDU'), TR('PNV', 'PSOE'), TR('PNV', 'PP'), TR('PNV', 'PNV'), TR('BILDU', 'BILDU')
assert (PNV_BILDU, PNV_PSOE, PNV_PP, PNV_PNV, BILDU_BILDU) == (60, 14, 3, 75, 79)   # EH Bildu conservó sus 79
assert A23['pct']['PSOE'] > A23['pct']['PNV'] > A23['pct']['BILDU'] and A19['pct']['PNV'] > A19['pct']['PSOE']
PNV_SUBE = int((m[f'{Y23}%PNV'] > m[f'{Y19}%PNV']).sum())
BILDU_SUBE = int((m[f'{Y23}%BILDU'] > m[f'{Y19}%BILDU']).sum())
PNV_BAJA = int((m[f'{Y23}%PNV'] < m[f'{Y19}%PNV']).sum())
PNV_IGUAL = m[(m[f'{Y23}_vPNV'] * m[f'{Y19}_val'] == m[f'{Y19}_vPNV'] * m[f'{Y23}_val'])]
assert PNV_SUBE == 4 and BILDU_SUBE == 245 and PNV_BAJA == 246 and list(PNV_IGUAL.mun_code) == ['48033'] and PNV_SUBE + PNV_BAJA + 1 == NMUN
DPNV_VOTOS = A19['votos']['PNV'] - A23['votos']['PNV']
DBILDU_VOTOS = A23['votos']['BILDU'] - A19['votos']['BILDU']
assert DPNV_VOTOS > 0 and DBILDU_VOTOS > 0
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PNV', 'BILDU', 'PSOE')} for y in (Y19, Y23)}
assert round(POB[Y19]['PNV'], 1) == 63.5 and round(POB[Y23]['PNV'], 1) == 17.1 and round(POB[Y23]['PSOE'], 1) == 59.6
FL = m[(m.g2019 == 'PNV') & (m.g2023 == 'BILDU')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PNV'] < FLS[Y19]['PNV'] and FLS[Y23]['BILDU'] > FLS[Y19]['BILDU'], FLS
FL_MED = float(FL.poblacion.median())

# Tamaño de municipio (padrón municipal del INE, 2023)
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000), ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PNV', 'BILDU', 'PSOE', 'PP', 'UP')}, **{f'{f.lower()}23': a23[f] for f in ('PNV', 'BILDU', 'PSOE', 'PP', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert all(t['pnv23'] < t['pnv19'] and t['bildu23'] > t['bildu19'] and t['psoe23'] > t['psoe19'] for t in TT.values())
TG = TT['Más de 20.000']
assert TG['n'] == 20 and TG['g19'] == {'PNV': 13, 'PSOE': 6, 'BILDU': 1} and TG['g23'] == {'PSOE': 12, 'BILDU': 5, 'PNV': 3}, TG   # padrón 2023: Tolosa pasa de 20.000
TP = TT['Menos de 1.000']
assert TP['n'] == 99 and TP['g23']['BILDU'] == 60 and TP['g19']['PNV'] == 54
G20 = m[m.poblacion >= 20000]
G20B19 = sorted(G20[G20.g2019 == 'BILDU'].municipio)
G20B23 = sorted(G20[G20.g2023 == 'BILDU'].municipio)
G20P23 = sorted(G20[G20.g2023 == 'PNV'].municipio)
assert G20B19 == ['Hernani'] and G20B23 == ['Arrasate/Mondragón', 'Durango', 'Hernani', 'Tolosa', 'Zarautz'] and G20P23 == ['Galdakao', 'Getxo', 'Leioa'], (G20B23, G20P23)

# Las tres capitales
CAP = m[m.mun_code.isin(CAPITAL)].sort_values('poblacion', ascending=False)
CI = CAP.set_index('mun_code')
assert list(CAP.g2023) == ['PSOE'] * 3 and list(CAP.g2019) == ['PNV', 'PSOE', 'PNV']
BIL, VIT, DON = CI.loc['48020'], CI.loc['01059'], CI.loc['20069']
assert BIL.seg2023 == 'PNV' and DON.seg2023 == 'BILDU' and VIT.seg2023 == 'PP'
CAP_POB = float(CAP.poblacion.sum() / m.poblacion.sum() * 100)

# Territorios
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
PRIM = {y: {pr: max(PRS[pr][y]['pct'], key=PRS[pr][y]['pct'].get) for pr in PROV} for y in (Y19, Y23)}
assert all(v == 'PNV' for v in PRIM[Y19].values()), PRIM
assert PRIM[Y23] == {'48': 'PNV', '20': 'BILDU', '01': 'PSOE'}, PRIM
assert PRN == {'48': 112, '20': 88, '01': 51}
assert PRG['20'][Y19]['BILDU'] == 53 and PRG['20'][Y23]['BILDU'] == 77 and PRG['48'][Y19]['PNV'] == 92 and PRG['48'][Y23]['PNV'] == 55
assert PRG['01'][Y23] == {'BILDU': 20, 'PNV': 16, 'PSOE': 9, 'PP': 6} and PRG['01'][Y19]['PNV'] == 30

# Municipios ajustados
UNVOTO = int((m.margv2023 == 1).sum())
UNV = sorted(m[m.margv2023 == 1].municipio)
assert UNVOTO == 3 and UNV == ['Añana', 'Garai', 'Leza']
AJG = m[m.poblacion >= 5000].sort_values('marg2023').head(10)
assert AJG.iloc[0].municipio == 'Arrigorriaga' and int(AJG.iloc[0].margv2023) == 3 and AJG.iloc[0].g2023 == 'PSOE'
AJ_PNV = sorted(AJG[AJG.g2023 == 'PNV'].municipio)
assert AJ_PNV == ['Beasain', 'Elgoibar', 'Galdakao', 'Gernika-Lumo'] and AJG[AJG.g2023 == 'PNV'].marg2023.max() < 3, AJ_PNV
AJ_BILDU1 = sorted(AJG[(AJG.g2023 == 'BILDU') & (AJG.marg2023 < 1)].municipio)
assert AJ_BILDU1 == ['Amorebieta-Etxano', 'Zarautz'] and all(AJG[AJG.municipio.isin(AJ_BILDU1)].g2019 == 'PNV')

# Escaños
ESC = escanos_oficiales(list(PROV))
for y in (Y19, Y23):
    ESC[y] = {pr: EHB(v) for pr, v in ESC[y].items()}
F5 = ('PNV', 'BILDU', 'PSOE', 'PP', 'UP', 'SUMAR')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F5}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F5}
assert E19 == {'PNV': 6, 'BILDU': 4, 'PSOE': 4, 'PP': 1, 'UP': 3, 'SUMAR': 0}, E19
assert E23 == {'PNV': 5, 'BILDU': 5, 'PSOE': 5, 'PP': 2, 'UP': 0, 'SUMAR': 1}, E23
assert ESC['2026'] == {'48': 8, '20': 6, '01': 4}
RC = {pr: EHB(reparto_central(PSLUG[pr])) for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F5}
assert sum(E29.values()) == 18 and set().union(*RC.values()) <= set(F5), (E29, RC)
assert E29 == {'PNV': 3, 'BILDU': 6, 'PSOE': 7, 'PP': 2, 'UP': 0, 'SUMAR': 0}, E29
assert RC['01']['PNV'] == (0, 0, 1) and ESC[Y23]['48']['SUMAR'] == 1
assert E29['BILDU'] - E23['BILDU'] == 1 and E29['PP'] == E23['PP']
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=43.0, umbral=1.2)
assert len(cam) == NMUN
ORDG = ['PNV', 'BILDU', 'PSOE', 'PP', 'UP', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PNV pasó de ganar en {GANA[Y19]["PNV"]} municipios a ganar en {GANA[Y23]["PNV"]}; EH Bildu, de {GANA[Y19]["BILDU"]} a {GANA[Y23]["BILDU"]}, y el PSOE, de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios del País Vasco, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios del País Vasco por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios del País Vasco por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura. En gris, Gaintza (Gipuzkoa), donde en 2019 el PNV y EH Bildu empataron a votos.',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

FF = ('PNV', 'BILDU', 'PSOE', 'PP')
g_flip = figura(f'En los {PNV_BILDU} municipios que pasaron del PNV a EH Bildu, el PNV bajó del {p(FLS[Y19]["PNV"])} % al {p(FLS[Y23]["PNV"])} %',
                'Voto al PNV, a EH Bildu, al PSOE y al PP en los municipios que ganó el PNV en 2019 y EH Bildu en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COL[f], .38, 'nov. 2019'), (FLS[Y23][f], COL[f], 1, '2023')]) for f in FF],
                       50, 'Voto en los municipios que pasaron del PNV a EH Bildu', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f])] for f in FF]
                 + [['Unidas Podemos (2019) / Sumar (2023)', p(FLS[Y19]['UP']), p(FLS[Y23]['SUMAR'])]]))

g_tam = figura(f'En los municipios de más de 20.000 habitantes, el PSOE pasó de ganar en {NW[TG["g19"]["PSOE"]]} de {TG["n"]} a ganar en {TG["g23"]["PSOE"]}, y el PNV, de {TG["g19"]["PNV"]} a {NW[TG["g23"]["PNV"]]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COL[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PNV 2019', 'EH Bildu 2019', 'PSOE 2019', 'PNV 2023', 'EH Bildu 2023', 'PSOE 2023'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PNV', 'BILDU', 'PSOE')] + [n(t['g23'].get(f, 0)) for f in ('PNV', 'BILDU', 'PSOE')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PNV bajó en todos los tamaños de municipio; EH Bildu y el PSOE subieron en todos',
                  'Voto al PNV, a EH Bildu y al PSOE en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pnv19'], COL['PNV'], .38, 'PNV, nov. 2019'), (t['pnv23'], COL['PNV'], 1, 'PNV, 2023'),
                                 (t['bildu19'], COL['BILDU'], .38, 'EH Bildu, nov. 2019'), (t['bildu23'], COL['BILDU'], 1, 'EH Bildu, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023')]) for nom, t in TT.items()],
                         45, 'Voto al PNV, a EH Bildu y al PSOE según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PNV', COL['PNV']), ('EH Bildu', COL['BILDU']), ('PSOE', COL['PSOE']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PNV nov. 2019 (%)', 'PNV 2023 (%)', 'EH Bildu nov. 2019 (%)', 'EH Bildu 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'PP 2023 (%)', 'Sumar 2023 (%)'],
                   [[nom, p(t['pnv19']), p(t['pnv23']), p(t['bildu19']), p(t['bildu23']), p(t['psoe19']), p(t['psoe23']), p(t['pp23']), p(t['sumar23'])] for nom, t in TT.items()]))

FC = ('PSOE', 'PNV', 'BILDU', 'PP')
g_cap = figura('El PSOE ganó en las tres capitales en 2023; en 2019, solo en Vitoria-Gasteiz',
               'Voto al PSOE, al PNV, a EH Bildu y al PP en julio de 2023 en las tres capitales, en %',
               grupos([(CAPITAL[r.mun_code].split('/')[0], [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in FC]) for _, r in CAP.iterrows()],
                      35, 'Voto en las tres capitales en 2023', W=440, ml=100),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [(NOMC[f], COL[f]) for f in FC],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'Segundo 2023', 'Ventaja 2023 (puntos)', 'PSOE 2023 (%)', 'PNV nov. 2019 (%)', 'PNV 2023 (%)', 'EH Bildu 2023 (%)', 'PP 2023 (%)'],
                [[CAPITAL[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), p(r[f'{Y23}%PSOE']), p(r[f'{Y19}%PNV']), p(r[f'{Y23}%PNV']),
                  p(r[f'{Y23}%BILDU']), p(r[f'{Y23}%PP'])] for _, r in CAP.iterrows()]))

g_prov = figura(f'En Gipuzkoa, EH Bildu ganó en {PRG["20"][Y23]["BILDU"]} de los {PRN["20"]} municipios en 2023',
                'Municipios ganados por cada partido en julio de 2023, por territorio',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDG if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada territorio en 2023', W=440, ml=100),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ('PNV', 'BILDU', 'PSOE', 'PP')],
                (['Territorio', 'Municipios', 'Más votado nov. 2019', 'Más votado 2023', 'PNV 2023 (%)', 'EH Bildu 2023 (%)', 'PSOE 2023 (%)', 'PP 2023 (%)',
                  'Municipios PNV 2019', 'Municipios PNV 2023', 'Municipios EH Bildu 2019', 'Municipios EH Bildu 2023'],
                 [[PROV[pr], n(PRN[pr]), NOMC[PRIM[Y19][pr]], NOMC[PRIM[Y23][pr]]] + [p(PRS[pr][Y23]['pct'][f]) for f in FC[1:3] + ('PSOE', 'PP')]
                  + [n(PRG[pr][y].get(f, 0)) for f in ('PNV', 'BILDU') for y in (Y19, Y23)] for pr in PROV]))

g_aj = figura(f'Arrigorriaga se decidió por {NW[int(AJG.iloc[0].margv2023)]} votos; Bilbao, por {n(BIL.marg2023, 2)} puntos',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios de más de 5.000 habitantes más ajustados, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], max(AJG.marg2023) * 1.15,
                     'Municipios de más de 5.000 habitantes más ajustados en 2023', W=440, ml=170, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in sorted(set(AJG.g2023), key=ORDG.index)],
              (['Municipio', 'Territorio', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'BILDU', 'PNV', 'PP', 'UP', 'SUMAR']


def hemi(lado=16, por_fila=9):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños del País Vasco en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, el PSOE pasaría de {NW[E23["PSOE"]]} a {NW[E29["PSOE"]]} diputados en el País Vasco, y el PNV, de {NW[E23["PNV"]]} a {NW[E29["PNV"]]}',
               'Los 18 diputados de los tres territorios: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada territorio '
               f'(<a href="{BASE}encuestas/bizkaia/">/encuestas/</a>) {VERSION}.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Territorio'] + [f'{NOMC[f]} 2023' for f in ('PNV', 'BILDU', 'PSOE', 'PP', 'SUMAR')] + [f'{NOMC[f]} 29N' for f in ('PNV', 'BILDU', 'PSOE', 'PP')],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in ('PNV', 'BILDU', 'PSOE', 'PP', 'SUMAR')]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in ('PNV', 'BILDU', 'PSOE', 'PP')]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in ('PNV', 'BILDU', 'PSOE', 'PP', 'SUMAR')] + [str(E29[f]) for f in ('PNV', 'BILDU', 'PSOE', 'PP')]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal del País Vasco</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral del País Vasco por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=48020">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/pais-vasco/">datos de cada municipio del País Vasco</a></div>\n</figure>\n')

# --- Texto ---
PNVL = 'https://www.moncloa.com/2026/10/17/listas-pnv-congreso-29n-3450355/'
EHBC = 'https://www.moncloa.com/2026/10/16/eh-bildu-candidatos-generales-29n-3449751/'
EHBP = 'https://www.moncloa.com/2026/10/19/eh-bildu-elecciones-generales-29n-2-3451602/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El País Vasco elige el 29 de noviembre 18 diputados: {ESC["2026"]["48"]} en Bizkaia, {ESC["2026"]["20"]} en Gipuzkoa y {ESC["2026"]["01"]} en Álava. El PNV ratificó el 17 de octubre a sus cabezas de lista, Idoia Sagastizabal en Bizkaia, Maribel Vaquero en Gipuzkoa y Gorka Urtaran en Álava, y su presidente, Aitor Esteban, defendió que había que enviarlos a Madrid «porque hay mucho en juego hoy en Madrid», según <a href="{PNVL}">Moncloa.com</a>. EH Bildu propuso a Oskar Matute en Bizkaia, Oihana Etxebarrieta en Gipuzkoa y Mikel Otero en Álava, según <a href="{EHBC}">Moncloa.com</a>, y Arnaldo Otegi la presentó como «la izquierda kilómetro cero», según el mismo <a href="{EHBP}">medio</a>.</p>
<p data-tipo="dato">El mapa municipio a municipio cambió de color. En noviembre de 2019, el PNV fue el partido más votado en {GANA[Y19]["PNV"]} de los {NMUN} municipios vascos, EH Bildu en {GANA[Y19]["BILDU"]}, el PSOE en {GANA[Y19]["PSOE"]}, el PP en {NW[GANA[Y19]["PP"]]} y Unidas Podemos en {NW[GANA[Y19]["UP"]]}; en Gaintza, el PNV y EH Bildu empataron a votos. En julio de 2023, EH Bildu ganó en {GANA[Y23]["BILDU"]}, el PNV en {GANA[Y23]["PNV"]}, el PSOE en {GANA[Y23]["PSOE"]} y el PP en {NW[GANA[Y23]["PP"]]}. Y el PSOE ganó en las tres capitales: en 2019 solo había ganado en Vitoria-Gasteiz.</p>
{g_ins}
<p data-tipo="dato">El más votado en el conjunto del País Vasco en 2023 fue el PSOE, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante del PNV ({p(A23["pct"]["PNV"])} %) y de EH Bildu ({p(A23["pct"]["BILDU"])} %). En 2019, el PNV había sacado el {p(A19["pct"]["PNV"])} %, EH Bildu el {p(A19["pct"]["BILDU"])} % y el PSOE el {p(A19["pct"]["PSOE"])} %. El PNV perdió {n(DPNV_VOTOS)} votos y bajó en {PNV_BAJA} de los {NMUN} municipios (en uno, Ibarrangelu, repitió el mismo porcentaje); EH Bildu ganó {n(DBILDU_VOTOS)} y subió en {BILDU_SUBE}. El PP pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, y Sumar sacó el {p(A23["pct"]["SUMAR"])} %, frente al {p(A19["pct"]["UP"])} % de Unidas Podemos en 2019. La participación bajó del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PNV"]} municipios del PNV en 2019, {PNV_BILDU} pasaron a EH Bildu, {PNV_PSOE} al PSOE y {NW[PNV_PP]} al PP; conservó {PNV_PNV}. EH Bildu mantuvo los {BILDU_BILDU} que había ganado en 2019. En los {PNV_BILDU} que pasaron del PNV a EH Bildu, el PNV bajó del {p(FLS[Y19]["PNV"])} % al {p(FLS[Y23]["PNV"])} % y EH Bildu subió del {p(FLS[Y19]["BILDU"])} % al {p(FLS[Y23]["BILDU"])} %. Como el PSOE ganó las ciudades, los municipios que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población al {p(POB[Y23]["PSOE"])} %, y los del PNV, del {p(POB[Y19]["PNV"])} % al {p(POB[Y23]["PNV"])} %.</p>
{g_flip}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">En los {TG["n"]} municipios de más de 20.000 habitantes, el PNV ganó en {TG["g19"]["PNV"]} en 2019 y en {NW[TG["g23"]["PNV"]]} en 2023: Getxo, Leioa y Galdakao. El PSOE pasó de {NW[TG["g19"]["PSOE"]]} a {TG["g23"]["PSOE"]}, y EH Bildu, que en 2019 solo ganó en Hernani, sumó en 2023 Durango, Zarautz, Arrasate/Mondragón y Tolosa. En los pueblos, el mapa es de EH Bildu: en los {TP["n"]} de menos de 1.000 habitantes, ganó en {TP["g23"]["BILDU"]} en 2023; el PNV había ganado en {TP["g19"]["PNV"]} en 2019. El PNV bajó en todos los tamaños de municipio, y EH Bildu y el PSOE subieron en todos.</p>
{g_tam}
{g_tampct}
<p data-tipo="dato">En las capitales, que reúnen el {p(CAP_POB)} % de la población vasca, el PSOE ganó en 2023 en Bilbao por {n(BIL.marg2023, 2)} puntos sobre el PNV; en Donostia/San Sebastián, por {n(DON.marg2023, 2)} sobre EH Bildu, y en Vitoria-Gasteiz, por {n(VIT.marg2023, 2)} sobre el PP. Bilbao y Donostia/San Sebastián las había ganado el PNV en 2019. Cómo cambiaron las dos ciudades sección a sección está en {L("derbi-vasco-bilbao-donostia-29n", "El derbi en las urnas")}.</p>
{g_cap}
<h2>Tres territorios</h2>
<p data-tipo="dato">En 2019, el PNV fue el más votado en los tres territorios; en 2023, solo en Bizkaia, mientras EH Bildu lo fue en Gipuzkoa y el PSOE en Álava. En Gipuzkoa, EH Bildu pasó de ganar en {PRG["20"][Y19]["BILDU"]} de los {PRN["20"]} municipios a ganar en {PRG["20"][Y23]["BILDU"]}. En Bizkaia, el PNV pasó de {PRG["48"][Y19]["PNV"]} a {PRG["48"][Y23]["PNV"]}, como se cuenta en {L("bizkaia-pnv-bildu-encuestas-29n", "esta pieza")}. En Álava, el mapa de 2023 quedó repartido entre cuatro: EH Bildu ganó en {PRG["01"][Y23]["BILDU"]} municipios, el PNV en {PRG["01"][Y23]["PNV"]}, el PSOE en {NW[PRG["01"][Y23]["PSOE"]]} y el PP en {NW[PRG["01"][Y23]["PP"]]}; en 2019, el PNV había ganado en {PRG["01"][Y19]["PNV"]} de los {PRN["01"]}.</p>
{g_prov}
<h2>Los más ajustados</h2>
<p data-tipo="dato">Entre los municipios de más de 5.000 habitantes, el más ajustado de 2023 fue Arrigorriaga (Bizkaia), que ganó el PSOE por {NW[int(AJG.iloc[0].margv2023)]} votos sobre el PNV. Gernika-Lumo, Galdakao, Elgoibar y Beasain los retuvo el PNV por menos de tres puntos, y Zarautz y Amorebieta-Etxano pasaron a EH Bildu por menos de uno. En {NW[UNVOTO]} municipios pequeños, Añana, Garai y Leza, el primero sacó un solo voto al segundo.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 18 escaños da al PSOE {E29["PSOE"]}, {NW[E29["PSOE"] - E23["PSOE"]]} más que en 2023; a EH Bildu, {E29["BILDU"]}, uno más; al PNV, {E29["PNV"]}, {NW[E23["PNV"] - E29["PNV"]]} menos, y al PP, {E29["PP"]}, los mismos. Sumar, que sacó uno en Bizkaia en 2023, no tendría ninguno. En Álava, el PNV se quedaría sin diputado en el reparto central, aunque en algunas simulaciones conserva uno.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen cuántos votantes del PNV de 2019 votaron a EH Bildu o al PSOE en 2023. Que el PNV bajara en casi todos los municipios a la vez que subían EH Bildu y el PSOE encaja con un trasvase hacia los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que bajó. Un municipio pequeño pesa en el mapa lo mismo que una ciudad: EH Bildu gana muchos pueblos, y el PSOE, pocos municipios pero muy poblados. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral del País Vasco desde 1977, con las autonómicas, está en {L("pais-vasco-historia-electoral", "El País Vasco en las urnas")}; la guía del 29N, en {L("euskadi-29n-guia", "esta pieza")}, y los pueblos donde más votan el PNV y EH Bildu, en {L("pnv-cinco-pueblos-bermeo", "Bermeo y la costa")} y {L("bildu-cinco-pueblos-lizartza", "de Lizartza a Goizueta")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/pais-vasco/">la ficha del País Vasco</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en el País Vasco?',
     f'El PSOE, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante del PNV ({p(A23["pct"]["PNV"])} %), EH Bildu ({p(A23["pct"]["BILDU"])} %), el PP ({p(A23["pct"]["PP"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     f'El PNV, EH Bildu y el PSOE sacaron {NW[E23["PNV"]]} diputados cada uno; el PP, {NW[E23["PP"]]}, y Sumar, uno. En noviembre de 2019, el más votado había sido el PNV.'),
    ('¿En cuántos municipios del País Vasco ganó EH Bildu en 2023?',
     f'En {GANA[Y23]["BILDU"]} de {NMUN}; el PNV, en {GANA[Y23]["PNV"]}; el PSOE, en {GANA[Y23]["PSOE"]}, y el PP, en {NW[GANA[Y23]["PP"]]}. '
     f'En noviembre de 2019, el PNV había ganado en {GANA[Y19]["PNV"]} y EH Bildu en {GANA[Y19]["BILDU"]}.'),
    ('¿Quién ganó en Bilbao, Donostia y Vitoria?',
     f'El PSOE, en las tres, en julio de 2023: en Bilbao, por {n(BIL.marg2023, 2)} puntos sobre el PNV; en Donostia/San Sebastián, por {n(DON.marg2023, 2)} sobre EH Bildu, y en Vitoria-Gasteiz, por {n(VIT.marg2023, 2)} sobre el PP. '
     'En noviembre de 2019, el PNV había ganado en Bilbao y en Donostia/San Sebastián.'),
    ('¿Cuántos diputados elige el País Vasco el 29N?',
     f'18, los mismos que en 2023: Bizkaia elige {ESC["2026"]["48"]}; Gipuzkoa, {ESC["2026"]["20"]}, y Álava, {ESC["2026"]["01"]}.'),
    ('¿Qué dicen las encuestas en el País Vasco?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PSOE {E29["PSOE"]} escaños, a EH Bildu {E29["BILDU"]}, al PNV {E29["PNV"]} y al PP {E29["PP"]}, con un margen amplio.'),
]
enlaces = (f'{L("pais-vasco-historia-electoral", "Historia electoral del País Vasco")} · <a href="{BASE}elecciones/pais-vasco/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/bizkaia/">Encuesta en Bizkaia</a> · <a href="{BASE}encuestas/gipuzkoa/">Encuesta en Gipuzkoa</a> · '
           f'<a href="{BASE}encuestas/alava/">Encuesta en Álava</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'población del padrón municipal del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_pais_vasco.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PNV_BILDU': PNV_BILDU, 'PNV_PSOE': PNV_PSOE, 'PNV_PP': PNV_PP, 'PNV_PNV': PNV_PNV, 'BILDU_BILDU': BILDU_BILDU,
    'DPNV_VOTOS': DPNV_VOTOS, 'DBILDU_VOTOS': DBILDU_VOTOS, 'PNV_SUBE': PNV_SUBE, 'PNV_BAJA': PNV_BAJA, 'BILDU_SUBE': BILDU_SUBE,
    'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN, 'CAP_POB': CAP_POB,
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN,
    'CAP': {CAPITAL[r.mun_code]: {'g19': r.g2019, 'g23': r.g2023, 'seg23': r.seg2023, 'marg23': R(r.marg2023), 'psoe23': R(r[f'{Y23}%PSOE']),
                                  'pnv19': R(r[f'{Y19}%PNV']), 'pnv23': R(r[f'{Y23}%PNV'])} for _, r in CAP.iterrows()},
    'UNVOTO': UNVOTO, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJG.iterrows()],
    'AJ_PNV_MAX': R(AJG[AJG.g2023 == 'PNV'].marg2023.max()),
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral del País Vasco',
      f'El mapa electoral del País Vasco: el PNV pasó de ganar en {GANA[Y19]["PNV"]} municipios a {GANA[Y23]["PNV"]}, y EH Bildu, de {GANA[Y19]["BILDU"]} a {GANA[Y23]["BILDU"]}',
      f'El PNV bajó en {PNV_BAJA} de los {NMUN} municipios (en uno repitió). EH Bildu le quitó {PNV_BILDU} y el PSOE, más votado en 2023, ganó en las tres capitales. '
      f'Para el 29N, la media de encuestas da al PSOE {E29["PSOE"]} de los 18 diputados, a EH Bildu {E29["BILDU"]} y al PNV {E29["PNV"]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'E29', E29, 'FLS', {y: {k: round(v, 1) for k, v in FLS[y].items()} for y in FLS}, 'AJG', [(r.municipio, round(r.marg2023, 2), int(r.margv2023), r.g2023) for _, r in AJG.iterrows()])
print('CAP_POB', CAP_POB, 'DPNV', DPNV_VOTOS, 'DBILDU', DBILDU_VOTOS, 'A', {k: round(v, 1) for k, v in A23['pct'].items()}, A19['part'], A23['part'])
