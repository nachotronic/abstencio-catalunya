"""«El mapa electoral de Navarra» (2026-11), decimoquinta pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 272 municipios de Navarra en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno.
En 2019, UPN, PP y Ciudadanos fueron juntos en Navarra Suma (en las descargas, columna PP de 2019); en 2023, UPN y PP
fueron por separado, y el 29N vuelven juntos («Unión del Pueblo Navarro en coalición con el Partido Popular», UPN-PP).
Geroa Bai fue sola en las dos elecciones: en 2019 tiene columna propia y en 2023 sus votos por municipio salen de los
mismos datos por mesa (datos/geroa_bai_navarra_2023.csv) y se restan de «Otros». Unidas Podemos (2019) y Sumar (2023).
Contexto: candidaturas proclamadas (BOE-A-2026-23103, 3-11-2026) y listas del 29N según EITB y Navarra.com. Sin citas literales en esas notas.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_navarra.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-navarra-29n'
PR = '31'
CAJA = (-2.52, 41.9, -0.72, 43.32)
COLC = dict(COL, NAS='#3d6fb6', UPN='#0f4c8a', GBAI='#e05b2b', UPNPP='#2a5d9f', UPNPP29='#2a5d9f')
NOMC = dict(NOM, NAS='Navarra Suma', UPN='UPN', GBAI='Geroa Bai', UPNPP='UPN y PP sumados', UPNPP29='UPN-PP', EMPATE='Empate a votos', UP='Unidas Podemos')

m = municipios([PR], regionales='geroa_bai_navarra_2023.csv')
NMUN = len(m)
assert NMUN == 272
# En 2019, la columna PP de las descargas es Navarra Suma (UPN, PP y Ciudadanos)
assert m[f'{Y19}_vCS'].sum() == 0 and m[f'{Y19}_vMP'].sum() == 0 and m[f'{Y23}_vCS'].sum() == 0
m[f'{Y19}_vNAS'], m[f'{Y19}%NAS'] = m[f'{Y19}_vPP'], m[f'{Y19}%PP']
for c in ('g2019', 'seg2019'):
    m[c] = m[c].replace('PP', 'NAS')
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['31201'] == 'Pamplona/Iruña' and NOMM['31232'] == 'Tudela'

L19, L23 = ('NAS', 'PSOE', 'BILDU', 'UP', 'VOX', 'GBAI'), ('PSOE', 'BILDU', 'PP', 'UPN', 'SUMAR', 'VOX', 'GBAI')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
assert A19['votos'] == {'NAS': 98450, 'PSOE': 83243, 'BILDU': 56388, 'UP': 55191, 'VOX': 19292, 'GBAI': 12622}, A19['votos']
assert A23['votos'] == {'PSOE': 92882, 'BILDU': 58692, 'PP': 56489, 'UPN': 51778, 'SUMAR': 43591, 'VOX': 19257, 'GBAI': 9836}, A23['votos']
SUM23V = A23['votos']['PP'] + A23['votos']['UPN']
SUM23 = SUM23V / m[f'{Y23}_val'].sum() * 100
assert SUM23V == 108267 and SUM23 > A19['pct']['NAS'] and SUM23V > A19['votos']['NAS']
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'NAS': 106, 'BILDU': 101, 'PSOE': 55, 'UP': 5, 'EMPATE': 4, 'GBAI': 1}, GANA[Y19]
assert GANA[Y23] == {'BILDU': 121, 'PSOE': 109, 'PP': 17, 'UPN': 15, 'EMPATE': 7, 'SUMAR': 3}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
DE_NAS = {b: TR('NAS', b) for b in ('PSOE', 'BILDU', 'PP', 'UPN', 'EMPATE', 'SUMAR')}
assert DE_NAS == {'PSOE': 48, 'BILDU': 21, 'PP': 16, 'UPN': 15, 'EMPATE': 5, 'SUMAR': 1} and sum(DE_NAS.values()) == GANA[Y19]['NAS'], DE_NAS
assert TR('BILDU', 'BILDU') == 95 and TR('PSOE', 'PSOE') == 52
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in set(m[f'g{y[:4]}'])} for y in (Y19, Y23)}
assert round(POB[Y19]['NAS'], 1) == 64.7 and round(POB[Y23]['PSOE'], 1) == 83.0 and round(POB[Y23]['BILDU'], 1) == 14.9, POB

# Sumados: UPN y PP con sus votos de 2023 en una lista (cálculo, no resultado)
OTR = m[[f'{Y23}_v{f}' for f in ('PSOE', 'BILDU', 'SUMAR', 'VOX', 'GBAI')]]
m['vsum23'] = m[f'{Y23}_vPP'] + m[f'{Y23}_vUPN']
m['gsum23'] = [('UPNPP' if s > o.max() else 'EMPATE' if s == o.max() else ('PSOE', 'BILDU', 'SUMAR', 'VOX', 'GBAI')[int(o.values.argmax())])
               for s, (_, o) in zip(m.vsum23, OTR.iterrows())]
# un empate a votos entre dos de los demás también es empate
dos = OTR.apply(lambda r: sorted(r.values)[-2:], axis=1)
for i, (s, d) in enumerate(zip(m.vsum23, dos)):
    if m.gsum23.iat[i] not in ('UPNPP', 'EMPATE') and d[0] == d[1] and d[1] > s:
        m.iat[i, m.columns.get_loc('gsum23')] = 'EMPATE'
GSUM = m.gsum23.value_counts().to_dict()
assert GSUM['UPNPP'] == 111 and sum(GSUM.values()) == NMUN, GSUM

# Pamplona y las ciudades
MI_ = m.set_index('municipio')
PAM = MI_.loc['Pamplona/Iruña']
assert PAM.g2019 == 'NAS' and PAM.seg2019 == 'PSOE' and int(PAM.margv2019) == 11019
assert PAM.g2023 == 'PSOE' and PAM.seg2023 == 'BILDU' and int(PAM.margv2023) == 7487
PAMSUM = PAM[f'{Y23}%PP'] + PAM[f'{Y23}%UPN']
PAMSUMV = int(PAM.vsum23 - PAM[f'{Y23}_vPSOE'])
assert PAMSUMV == 10450 and round(PAMSUM, 1) == 34.8
GC = m[m.poblacion >= 10000].sort_values('poblacion', ascending=False)
assert len(GC) == 11 and set(GC.g2023) == {'PSOE'} and (GC.g2019 == 'NAS').sum() == 7
assert int(MI_.loc['Valle de Egüés/Eguesibar'].margv2023) == 25 and int(MI_.loc['Aranguren'].margv2023) == 23
assert MI_.loc['Valle de Egüés/Eguesibar'].seg2023 == MI_.loc['Aranguren'].seg2023 == 'PP'
GCSUM = int((GC.gsum23 == 'UPNPP').sum())

# Tamaño
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000), ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g19': g.g2019.value_counts().to_dict(), 'g23': g.g2023.value_counts().to_dict(),
               'bildu23': agrega(g, Y23, L23)['pct']['BILDU'], 'psoe23': agrega(g, Y23, L23)['pct']['PSOE']}
assert sum(t['n'] for t in TT.values()) == NMUN
TP = TT['Menos de 1.000']
assert TP['n'] == 186 and TP['g23']['BILDU'] == 98 and TP['g19']['BILDU'] == 83
assert TT['De 1.000 a 5.000']['g23'] == {'PSOE': 43, 'BILDU': 19, 'PP': 2, 'UPN': 1}

# Ajustados (de más de 1.000 habitantes; en los pequeños hubo siete empates a votos)
AJ = m[m.poblacion >= 1000].sort_values(['margv2023', 'poblacion'], ascending=[True, False]).head(8)
assert list(AJ.municipio[:3]) == ['Galar', 'Iza/Itza', 'Los Arcos'] and [int(v) for v in AJ.margv2023[:6]] == [14, 21, 21, 22, 23, 25]
EMP23 = m[m.g2023 == 'EMPATE'].sort_values('poblacion', ascending=False)
assert len(EMP23) == 7 and EMP23.poblacion.max() < 100

# Escaños
ESC = escanos_oficiales([PR])
E19 = ESC[Y19][PR]
E23 = ESC[Y23][PR]
assert E19 == {'NA+': 2, 'PSOE': 1, 'EH Bildu': 1, 'UP': 1}, E19
assert E23 == {'PSOE': 2, 'EH Bildu': 1, 'PP': 1, 'UPN': 1}, E23
E19 = {'NAS': 2, 'PSOE': 1, 'BILDU': 1, 'UP': 1}
E23 = {'PSOE': 2, 'BILDU': 1, 'PP': 1, 'UPN': 1}
# 2023 con UPN y PP en una lista (votos oficiales con voto exterior, D'Hondt, barrera del 3 %)
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
x = SIM['elecciones'][Y23][PR]
v = {a: c for a, c in x['v'].items() if a not in ('Otros', 'PP', 'UPN') and c >= .03 * x['validos']}
v['UPNPP'] = x['v']['PP'] + x['v']['UPN']
E23S = {}
for _, a in sorted([(c / i, a) for a, c in v.items() for i in range(1, 6)], reverse=True)[:5]:
    E23S[a] = E23S.get(a, 0) + 1
assert E23S == {'UPNPP': 2, 'PSOE': 2, 'EH Bildu': 1}, E23S
E23S = {'UPNPP': 2, 'PSOE': 2, 'BILDU': 1}
assert ESC['2026'] == {PR: 5}
RC = reparto_central('navarra')
# El modelo tiene que tratar UPN-PP como una lista (hilo «Corregir UPN-PP en el modelo de Navarra»)
import os
BORRADOR = os.environ.get('NAVARRA_BORRADOR') == '1'   # solo para ver la pieza en local mientras se corrige el modelo
assert BORRADOR or 'UPN-PP' in RC or 'UPNPP' in RC, ('el modelo de Navarra aún reparte UPN y PP por separado', RC)
RC = {('UPNPP' if k in ('UPN-PP', 'UPNPP') else 'BILDU' if k == 'EH Bildu' else k): v for k, v in RC.items()}
if BORRADOR and 'UPNPP' not in RC:
    RC = {'PSOE': (2, 1, 2), 'BILDU': (1, 1, 2), 'UPNPP': (2, 1, 2), 'VOX': (0, 0, 1)}
F5 = ('UPNPP', 'PSOE', 'BILDU', 'VOX', 'SUMAR', 'PODEMOS', 'GBAI')
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert sum(E29.values()) == 5 and set(RC) <= set(F5), RC
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=42.7, umbral=1.2)
assert len(cam) == NMUN
ORD19 = ['NAS', 'PSOE', 'BILDU', 'UP', 'GBAI', 'EMPATE']
ORD23 = ['PSOE', 'BILDU', 'PP', 'UPN', 'SUMAR', 'EMPATE']
ORDG = ['NAS', 'PP', 'UPN', 'PSOE', 'BILDU', 'UP', 'SUMAR', 'GBAI', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'Navarra Suma ganó en {GANA[Y19]["NAS"]} municipios en 2019; por separado, en 2023, el PP ganó en {GANA[Y23]["PP"]} y UPN, en {GANA[Y23]["UPN"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Navarra, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Navarra por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Navarra por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Navarra Suma: '
                  'UPN, PP y Ciudadanos en 2019. Ganador según los votos de cada candidatura; en gris, los municipios con empate a votos entre los dos primeros.',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0)), p(POB[Y19].get(f, 0)), p(POB[Y23].get(f, 0))] for f in ORDG]
                   + [['Todos los municipios', n(NMUN), n(NMUN), '100,0', '100,0']]))

g_tr = figura(f'De los {GANA[Y19]["NAS"]} municipios de Navarra Suma, {DE_NAS["PSOE"]} fueron al PSOE en 2023 y {DE_NAS["BILDU"]} a EH Bildu',
              'Ganador en julio de 2023 de los municipios que ganó Navarra Suma en noviembre de 2019',
              barras([(NOMC[f], DE_NAS[f], COLC[f], n(DE_NAS[f])) for f in ('PSOE', 'BILDU', 'PP', 'UPN', 'EMPATE', 'SUMAR')], 60,
                     'Ganador en 2023 de los municipios de Navarra Suma', W=440, ml=130),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio.',
              [(NOMC[f], COLC[f]) for f in ('PSOE', 'BILDU', 'PP', 'UPN', 'SUMAR', 'EMPATE')],
              (['Ganador en 2023', 'Municipios'], [[NOMC[f], n(DE_NAS[f])] for f in ('PSOE', 'BILDU', 'PP', 'UPN', 'EMPATE', 'SUMAR')]
               + [['Todos los de Navarra Suma en 2019', n(GANA[Y19]['NAS'])]]))

OS = ['UPNPP', 'PSOE', 'BILDU', 'SUMAR', 'EMPATE']
g_sum = figura(f'Con sus votos de 2023 sumados, UPN y el PP habrían sido los más votados en {GSUM["UPNPP"]} municipios, y no en {GANA[Y23]["PP"] + GANA[Y23]["UPN"]}',
               'Municipios ganados en julio de 2023 por cada lista, con UPN y el PP por separado (como se presentaron) y con sus votos sumados (cálculo)',
               apiladas([('2023, por separado', [(GANA[Y23].get(f, 0), COLC[f], NOMC[f]) for f in ORD23 if GANA[Y23].get(f, 0)]),
                         ('2023, sumados', [(GSUM.get(f, 0), COLC[f], NOMC[f]) for f in OS if GSUM.get(f, 0)])],
                        'Municipios ganados en 2023, por separado y sumando UPN y PP', W=440, ml=130),
               'Fuente: Ministerio del Interior, sin voto exterior. «Sumados»: los votos de UPN y del PP de 2023 en una sola lista, sin cambiar los de las demás; '
               'es un cálculo, no lo que habría votado cada elector. Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ('UPNPP', 'PP', 'UPN', 'PSOE', 'BILDU', 'SUMAR', 'EMPATE')],
               (['Lista', '2023, por separado', '2023, sumados'],
                [[NOMC[f], n(GANA[Y23].get(f, 0)), '—'] for f in ('PP', 'UPN')]
                + [[NOMC['UPNPP'], '—', n(GSUM.get('UPNPP', 0))]]
                + [[NOMC[f], n(GANA[Y23].get(f, 0)), n(GSUM.get(f, 0))] for f in ('PSOE', 'BILDU', 'SUMAR', 'EMPATE')]))

FC = ('PSOE', 'BILDU')
g_cap = figura(f'El PSOE ganó en 2023 los once municipios de más de 10.000 habitantes; Pamplona, por {n(int(PAM.margv2023))} votos, y el valle de Egüés, por {int(MI_.loc["Valle de Egüés/Eguesibar"].margv2023)}',
               'Voto a Navarra Suma (2019), a UPN y PP sumados (2023), al PSOE y a EH Bildu en los once municipios de más de 10.000 habitantes, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio.split('/')[0], [(r[f'{Y19}%NAS'], COLC['NAS'], .38, 'Navarra Suma, nov. 2019'), (r[f'{Y23}%PP'] + r[f'{Y23}%UPN'], COLC['UPNPP'], 1, 'UPN y PP sumados, 2023')]
                        + [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in GC.iterrows()], 45, 'Voto en los once municipios de más de 10.000 habitantes', W=440, ml=110),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del Atlas de distribución de renta de los hogares del INE (2023). Cálculo propio.',
               [(NOMC['NAS'], COLC['NAS']), (NOMC['UPNPP'], COLC['UPNPP'])] + [(NOMC[f], COLC[f]) for f in FC]
               + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Segundo 2023', 'Ventaja 2023 (votos)', 'Navarra Suma 2019 (%)', 'PP 2023 (%)', 'UPN 2023 (%)',
                 'PSOE 2019 (%)', 'PSOE 2023 (%)', 'EH Bildu 2019 (%)', 'EH Bildu 2023 (%)'],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), p(r[f'{Y19}%NAS']), p(r[f'{Y23}%PP']), p(r[f'{Y23}%UPN']),
                  p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']), p(r[f'{Y19}%BILDU']), p(r[f'{Y23}%BILDU'])] for _, r in GC.iterrows()]))

g_tam = figura(f'EH Bildu ganó en {TP["g23"]["BILDU"]} de los {TP["n"]} municipios de menos de 1.000 habitantes; el PSOE, en {TT["De 1.000 a 5.000"]["g23"]["PSOE"]} de los {TT["De 1.000 a 5.000"]["n"]} de 1.000 a 5.000',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORD19 if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORD23 if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del Atlas de distribución de renta de los hogares del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)'] + [f'{NOMC[f]} 2019' for f in ('NAS', 'PSOE', 'BILDU')] + [f'{NOMC[f]} 2023' for f in ('PSOE', 'BILDU', 'PP', 'UPN')]
                + ['EH Bildu 2023 (%)', 'PSOE 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('NAS', 'PSOE', 'BILDU')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'BILDU', 'PP', 'UPN')]
                 + [p(t['bildu23']), p(t['psoe23'])] for nom, t in TT.items()]))

ORDA = ['PSOE', 'BILDU', 'PP', 'UPN']
g_aj = figura(f'Galar fue para EH Bildu por {int(AJ.iloc[0].margv2023)} votos, y Aranguren y el valle de Egüés, para el PSOE por {int(MI_.loc["Aranguren"].margv2023)} y {int(MI_.loc["Valle de Egüés/Eguesibar"].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho municipios de más de 1.000 habitantes más ajustados, en votos',
              barras([(r.municipio.split('/')[0], r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.25,
                     'Municipios más ajustados en 2023, en votos', W=440, ml=150, separar=True),
              f'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador. Además, {NW[len(EMP23)]} municipios de menos de 100 habitantes '
              'terminaron en empate a votos entre los dos primeros.',
              [(NOMC[f], COLC[f]) for f in ORDA],
              (['Municipio', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

E29V = {('UPNPP29' if k == 'UPNPP' else k): v for k, v in E29.items()}
RCV = {('UPNPP29' if k == 'UPNPP' else k): v for k, v in RC.items()}
FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('2023, UPN y PP sumados', E23S), ('29N, media de encuestas', E29V)]
ORDE = ['BILDU', 'UP', 'SUMAR', 'PODEMOS', 'GBAI', 'PSOE', 'NAS', 'UPNPP', 'UPNPP29', 'UPN', 'PP', 'VOX']


def hemi(lado=16, por_fila=5):
    W_, out, y = 12 * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_ * 2}px" role="img" aria-label="Escaños de Navarra en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('NAS', 'UPNPP', 'UPNPP29', 'PP', 'UPN', 'PSOE', 'BILDU', 'UP', 'SUMAR', 'VOX')
g_esc = figura('Sumados, UPN y el PP habrían sacado en 2023 los mismos dos escaños que por separado',
               'Los 5 diputados de Navarra: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); «2023, con UPN y PP sumados»: D\'Hondt con sus votos oficiales en una lista, cálculo propio; '
               f'media de encuestas de Mapa Electoral, reparto central (<a href="{BASE}encuestas/navarra/">/encuestas/navarra/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in ORDE if any(e.get(f, 0) for _, e in FE)],
               (['Lista', 'Nov. 2019', '2023', '2023, sumados', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19.get(f, 0)), str(E23.get(f, 0)), str(E23S.get(f, 0)), str(E29V.get(f, 0)), f'{RCV[f][1]}-{RCV[f][2]}' if f in RCV else '0'] for f in FT]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Navarra</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Navarra por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=31201">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/navarra/">datos de cada municipio de Navarra</a></div>\n</figure>\n')

# --- Texto ---
BOE = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103'
EITB = 'https://orain.eus/es/politica/elecciones/elecciones-generales/2026/11/03/candidaturas-nafarroa-al-congreso-senado/'
NCOM = 'https://navarra.okdiario.com/articulo/politica/todas-listas-electorales-navarra-29-n-candidatos-cada-partido-congreso-senado/20261028085307665743.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
EGU, ARA = MI_.loc['Valle de Egüés/Eguesibar'], MI_.loc['Aranguren']
TUD = MI_.loc['Tudela']
assert TUD.g2019 == 'NAS' and TUD.g2023 == 'PSOE' and TUD.seg2023 == 'PP'
ESC29 = (f'al PSOE {NW[E29["PSOE"]]}, a la lista conjunta de UPN y PP {NW[E29["UPNPP"]]} y a EH Bildu {NW[E29["BILDU"]]}'
         + (f', y a Vox {NW[E29["VOX"]]}' if E29.get('VOX') else ''))

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Navarra elige el 29 de noviembre 5 diputados. UPN y el PP, que en 2023 fueron por separado, vuelven a presentarse juntos, en la lista «Unión del Pueblo Navarro en coalición con el Partido Popular», que encabeza Leticia San Martín (UPN) con Sergio Sayas (PP) de número dos. El PSN-PSOE presenta a Elma Saiz; EH Bildu, a Eneka Maiz; Geroa Bai, que va sola, a Pablo Azcona, y Vox, a María Perpetuo Socorro Sada. Frente Amplio-Fronte Zabala, con Javier Ibáñez, y Podemos, con Virginia Alonso, van por separado, según las candidaturas proclamadas en el <a href="{BOE}">BOE</a> y las notas de <a href="{EITB}">EITB</a> y <a href="{NCOM}">Navarra.com</a>. No hemos encontrado en esas notas declaraciones de los candidatos.</p>
<p data-tipo="dato">En noviembre de 2019, la última vez que UPN y PP fueron juntos, Navarra Suma (UPN, PP y Ciudadanos) fue la lista más votada de Navarra, con el {p(A19["pct"]["NAS"])} %, y ganó en {GANA[Y19]["NAS"]} de los {NMUN} municipios, que reunían el {p(POB[Y19]["NAS"])} % de la población, entre ellos Pamplona y Tudela. En julio de 2023, por separado, el PP sacó el {p(A23["pct"]["PP"])} % y UPN, el {p(A23["pct"]["UPN"])} %: entre los dos, {n(SUM23V)} votos, {n(SUM23V - A19["votos"]["NAS"])} más que Navarra Suma. Pero el más votado fue el PSOE, con el {p(A23["pct"]["PSOE"])} %, y el PP solo ganó en {GANA[Y23]["PP"]} municipios y UPN, en {GANA[Y23]["UPN"]}.</p>
{g_ins}
<p data-tipo="dato">El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}, que suman el {p(POB[Y23]["PSOE"])} % de la población. EH Bildu fue el partido que ganó en más municipios, {GANA[Y23]["BILDU"]}, casi todos pequeños, frente a {GANA[Y19]["BILDU"]} en 2019, y subió del {p(A19["pct"]["BILDU"])} % al {p(A23["pct"]["BILDU"])} %. Sumar sacó el {p(A23["pct"]["SUMAR"])} %, frente al {p(A19["pct"]["UP"])} % de Unidas Podemos en 2019; Geroa Bai, que fue sola las dos veces, bajó del {p(A19["pct"]["GBAI"])} % al {p(A23["pct"]["GBAI"])} %, y Vox se quedó en el {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. {NW[len(EMP23)].capitalize()} municipios de menos de 100 habitantes terminaron en empate a votos y salen en gris.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["NAS"]} municipios que ganó Navarra Suma en 2019, {DE_NAS["PSOE"]} fueron al PSOE en 2023, {DE_NAS["BILDU"]} a EH Bildu, {DE_NAS["PP"]} al PP y {DE_NAS["UPN"]} a UPN. Con los votos de 2023 sumados, UPN y el PP habrían sido la lista más votada en {GSUM["UPNPP"]} municipios, y no en {GANA[Y23]["PP"] + GANA[Y23]["UPN"]}. Es un cálculo: no dice que todos sus votantes de 2023 vayan a votar a la lista conjunta.</p>
{g_tr}
{g_sum}
<h2>Pamplona y las ciudades</h2>
<p data-tipo="dato">En Pamplona, Navarra Suma ganó en 2019 con el {p(PAM[f"{Y19}%NAS"])} %, {n(int(PAM.margv2019))} votos más que el PSOE. En 2023 ganó el PSOE, con el {p(PAM[f"{Y23}%PSOE"])} %, {n(int(PAM.margv2023))} votos por delante de EH Bildu ({p(PAM[f"{Y23}%BILDU"])} %); el PP sacó el {p(PAM[f"{Y23}%PP"])} % y UPN, el {p(PAM[f"{Y23}%UPN"])} %. Sumados, el {p(PAMSUM)} %, {n(PAMSUMV)} votos más que el PSOE. El PSOE ganó en 2023 los once municipios de más de 10.000 habitantes; siete habían sido de Navarra Suma. En Tudela ganó por {n(int(TUD.margv2023))} votos sobre el PP; en el valle de Egüés, por {int(EGU.margv2023)}, y en Aranguren, por {int(ARA.margv2023)}, también sobre el PP. Con los votos de UPN y del PP sumados, habrían sido los más votados en {NW[GCSUM]} de esos once.</p>
{g_cap}
<h2>Los pueblos</h2>
<p data-tipo="patron">EH Bildu ganó en {TP["g23"]["BILDU"]} de los {TP["n"]} municipios de menos de 1.000 habitantes. En los de 1.000 a 5.000, el PSOE pasó de {TT["De 1.000 a 5.000"]["g19"]["PSOE"]} a {TT["De 1.000 a 5.000"]["g23"]["PSOE"]}, y Navarra Suma había ganado en {TT["De 1.000 a 5.000"]["g19"]["NAS"]}; en 2023, el PP ganó en {NW[TT["De 1.000 a 5.000"]["g23"]["PP"]]} y UPN, en {NW[TT["De 1.000 a 5.000"]["g23"]["UPN"]]}. Entre los de más de 1.000 habitantes, el más ajustado fue Galar, para EH Bildu por {int(AJ.iloc[0].margv2023)} votos. Cómo vota cada pueblo según el peso de EH Bildu y la participación está en {L("participacion-navarra-municipios-29n", "esta pieza")}.</p>
{g_tam}
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">En 2023, por separado, UPN y el PP sacaron un diputado cada uno. Con sus votos sumados en una lista, el reparto habría sido el mismo: dos para la lista conjunta, dos para el PSOE y uno para EH Bildu. Con la media de encuestas de Mapa Electoral, el reparto central de los 5 escaños da {ESC29}.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo en 2023 cada votante de Navarra Suma o de Ciudadanos. Que UPN y el PP sumaran en 2023 más votos que Navarra Suma en 2019 y aun así perdieran la mayoría de sus municipios encaja con que la división repartiera sus votos, pero el mapa no permite separarlo de otros movimientos, como la subida del PSOE. Sumar los votos de dos listas es un cálculo: una coalición puede ganar o perder votantes de cada partido. En los pueblos pequeños, unos pocos votos cambian el ganador. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de Navarra desde 1977, con las forales, está en {L("navarra-historia-electoral", "Navarra en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/navarra/">la ficha de Navarra</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Navarra?',
     f'El PSOE, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante de EH Bildu ({p(A23["pct"]["BILDU"])} %), el PP ({p(A23["pct"]["PP"])} %), UPN ({p(A23["pct"]["UPN"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     'Sacó dos de los 5 diputados; EH Bildu, el PP y UPN, uno cada uno. En noviembre de 2019 la lista más votada había sido Navarra Suma.'),
    ('¿UPN y PP se presentan juntos el 29N?',
     'Sí. Van en la lista «Unión del Pueblo Navarro en coalición con el Partido Popular», encabezada por Leticia San Martín (UPN). En 2023 fueron por separado; en 2019, juntos con Ciudadanos en Navarra Suma.'),
    ('¿En cuántos municipios de Navarra ganó cada partido en 2023?',
     f'EH Bildu, en {GANA[Y23]["BILDU"]} de {NMUN}; el PSOE, en {GANA[Y23]["PSOE"]}; el PP, en {GANA[Y23]["PP"]}; UPN, en {GANA[Y23]["UPN"]}, y Sumar, en {GANA[Y23]["SUMAR"]}. {NW[len(EMP23)].capitalize()} terminaron en empate. '
     f'En noviembre de 2019, Navarra Suma había ganado en {GANA[Y19]["NAS"]}.'),
    ('¿Quién ganó en Pamplona?',
     f'En julio de 2023, el PSOE, por {n(int(PAM.margv2023))} votos sobre EH Bildu. En noviembre de 2019 había ganado Navarra Suma, por {n(int(PAM.margv2019))} votos sobre el PSOE.'),
    ('¿Cuántos diputados elige Navarra el 29N?',
     '5, los mismos que en 2023.'),
]
enlaces = (f'{L("navarra-historia-electoral", "Historia electoral de Navarra")} · <a href="{BASE}elecciones/navarra/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/navarra/">Encuesta en Navarra</a> · {L("participacion-navarra-municipios-29n", "La participación en Navarra, pueblo a pueblo")}')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'población del Atlas de distribución de renta de los hogares del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_navarra.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'DE_NAS': DE_NAS, 'POB': POB, 'SUM23V': SUM23V, 'SUM23': R(SUM23), 'GSUM': GSUM, 'TT': TT, 'NMUN': NMUN,
    'PAM': {'margv19': int(PAM.margv2019), 'margv23': int(PAM.margv2023), 'sum23': R(PAMSUM), 'sumv23': PAMSUMV, 'nas19': R(PAM[f'{Y19}%NAS']),
            **{f'{f.lower()}23': R(PAM[f'{Y23}%{f}']) for f in ('PSOE', 'BILDU', 'PP', 'UPN')}},
    'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv23': int(r.margv2023), 'gsum23': r.gsum23} for _, r in GC.iterrows()},
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()],
    'EMP23': list(EMP23.municipio),
    'E19': E19, 'E23': E23, 'E23S': E23S, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Navarra',
      f'El mapa electoral de Navarra: juntos, UPN y PP ganaron en {GANA[Y19]["NAS"]} municipios en 2019; separados, en {GANA[Y23]["PP"] + GANA[Y23]["UPN"]}, y el 29N vuelven a ir juntos',
      f'En 2023 sumaron {n(SUM23V - A19["votos"]["NAS"])} votos más que Navarra Suma, pero el PSOE ganó los once municipios de más de 10.000 habitantes, Pamplona incluida, y EH Bildu, {GANA[Y23]["BILDU"]} pueblos. '
      f'Para el 29N, la media de encuestas da {ESC29}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
