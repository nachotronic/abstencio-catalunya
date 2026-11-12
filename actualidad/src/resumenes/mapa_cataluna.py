"""«El mapa electoral de Cataluña» (10-11-2026), segunda pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 947 municipios catalanes en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas por
separado: en 2019, En Comú Podem/Unidas Podemos y Más País; la CUP, con sus votos por municipio), el cambio del PSC, el
tamaño de los municipios (padrón municipal del INE, 2023), las capitales, los municipios más ajustados y el reparto
central del modelo de /encuestas/ para el 29N. Contexto: EFE (8-11-2026), Crónica Global (9-11-2026) y ElNacional.cat.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_cataluna.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, s1, trazados)

A = BASE + 'actualidad/'
NW = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve'}
SLUG = 'mapa-electoral-cataluna-29n'
PROV = {'08': 'Barcelona', '17': 'Girona', '25': 'Lleida', '43': 'Tarragona'}
PSLUG = {'08': 'barcelona', '17': 'girona', '25': 'lleida', '43': 'tarragona'}
CAP = {'08019': 'Barcelona', '17079': 'Girona', '25120': 'Lleida', '43148': 'Tarragona'}
CAJA = (0.1, 40.5, 3.4, 42.9)
# En Cataluña, la candidatura socialista es el PSC y la de Sumar, Sumar (En Comú Podem en 2019, con Unidas Podemos)
NOMC = dict(NOM, PSOE='PSC', UP='En Comú Podem', EMPATE='Empate a votos')

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 947
NOMM = dict(zip(m.mun_code, m.municipio))
A19, A23 = agrega(m, Y19), agrega(m, Y23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'ERC': 619, 'JUNTS': 241, 'PSOE': 75, 'CUP': 5, 'EMPATE': 4, 'PP': 2, 'UP': 1}, GANA[Y19]
assert GANA[Y23] == {'PSOE': 462, 'JUNTS': 295, 'ERC': 159, 'EMPATE': 15, 'SUMAR': 8, 'CUP': 4, 'PP': 3, 'VOX': 1}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
ERC_PSC, ERC_JUNTS, JUNTS_PSC = TR('ERC', 'PSOE'), TR('ERC', 'JUNTS'), TR('JUNTS', 'PSOE')
assert (ERC_PSC, ERC_JUNTS, JUNTS_PSC) == (351, 105, 35)
ERC_PIERDE = int(((m.g2019 == 'ERC') & (m.g2023 != 'ERC')).sum())
assert ERC_PIERDE == GANA[Y19]['ERC'] - TR('ERC', 'ERC') == 477
PSC_PIERDE = int(((m.g2019 == 'PSOE') & (m.g2023 != 'PSOE')).sum())
assert PSC_PIERDE == 0          # el PSC conservó los 75 municipios que ya ganaba
# Empates (mismo número de votos entre los dos primeros): gris en los mapas
EMP = {y: m[m[f'g{y[:4]}'] == 'EMPATE'] for y in (Y19, Y23)}
EMP23 = EMP[Y23].emp2023.value_counts().to_dict()
assert len(EMP[Y19]) == 4 and EMP23 == {'PSOE-ERC': 7, 'ERC-JUNTS': 4, 'SUMAR-JUNTS': 2, 'PSOE-JUNTS': 2}, EMP23
assert set(EMP[Y23][EMP[Y23].emp2023 == 'PSOE-ERC'].municipio) >= {'Albesa', 'Bràfim'}
# Independentistas (ERC, Junts y CUP) y PSC
IND = {y: A['pct']['ERC'] + A['pct']['JUNTS'] + A['pct']['CUP'] for y, A in ((Y19, A19), (Y23, A23))}
DPSC = A23['pct']['PSOE'] - A19['pct']['PSOE']
DPSC_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
POB = {f: float(m[m.g2023 == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PSOE', 'JUNTS', 'ERC')}
m['dPSC'] = m[f'{Y23}%PSOE'] - m[f'{Y19}%PSOE']
PSC_SUBE = int((m.dPSC > 0).sum())
PSC_MAS20 = int((m.dPSC > 20).sum())

# Provincias
PR = {pr: {y: agrega(m[m.prov == pr], y) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
assert PRG['17'][Y23]['JUNTS'] == 110 and PRG['25'][Y23]['JUNTS'] == 87 and PRG['08'][Y23]['PSOE'] == 197 and PRG['43'][Y23]['PSOE'] == 109
assert all(max(PR[pr][Y23]['pct'], key=PR[pr][Y23]['pct'].get) == 'PSOE' for pr in PROV)
assert [max(PR[pr][Y19]['pct'], key=PR[pr][Y19]['pct'].get) for pr in PROV] == ['PSOE', 'ERC', 'ERC', 'ERC']

# Capitales
CA = m[m.mun_code.isin(CAP)].set_index('mun_code')
assert (CA.g2023 == 'PSOE').all() and list(CA.g2019) == ['ERC', 'JUNTS', 'ERC', 'PSOE']

# Tamaño de municipio (padrón municipal del INE, 2023)
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000),
       ('De 20.000 a 100.000', 20000, 100000), ('Más de 100.000', 100000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19)['pct'], agrega(g, Y23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               'psc19': a19['PSOE'], 'psc23': a23['PSOE'], 'ind19': a19['ERC'] + a19['JUNTS'] + a19['CUP'], 'ind23': a23['ERC'] + a23['JUNTS'] + a23['CUP'],
               'erc23': a23['ERC'], 'junts23': a23['JUNTS'], 'pp23': a23['PP']}
assert sum(t['n'] for t in TT.values()) == NMUN
assert TT['Más de 100.000']['g23'] == {'PSOE': 11} and TT['De 20.000 a 100.000']['g23'] == {'PSOE': 56, 'JUNTS': 2}
assert TT['Menos de 1.000']['g23']['JUNTS'] == 217 and TT['Menos de 1.000']['g23']['PSOE'] == 109
GRANDES = TT['Más de 100.000']['n'] + TT['De 20.000 a 100.000']['n']
GRANDES_PSC = TT['Más de 100.000']['g23'].get('PSOE', 0) + TT['De 20.000 a 100.000']['g23'].get('PSOE', 0)
assert (GRANDES, GRANDES_PSC) == (69, 67)   # padrón 2023: Sant Quirze del Vallès pasa de 20.000
GJ = m[(m.poblacion >= 20000) & (m.g2023 != 'PSOE')]
assert sorted(GJ.municipio) == ['Banyoles', 'Vic'], list(GJ.municipio)

# Municipios ajustados en 2023
AJ2 = int((m.marg2023 < 2).sum())
AJ10 = int((m.margv2023 < 10).sum())
AJG = m[(m.poblacion >= 10000) & (m.marg2023 < 5)].sort_values('marg2023')
assert len(AJG) == 6 and all({r.g2023, r.seg2023} == {'PSOE', 'JUNTS'} for _, r in AJG.iterrows())
VIC = m[m.municipio == 'Vic'].iloc[0]
assert VIC.g2023 == 'JUNTS' and VIC.seg2023 == 'PSOE' and VIC.g2019 == 'JUNTS'

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(list(PROV))
F19, F23 = ('PSOE', 'ERC', 'JUNTS', 'UP', 'PP', 'VOX', 'CUP', 'CS'), ('PSOE', 'ERC', 'JUNTS', 'SUMAR', 'PP', 'VOX', 'CUP')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F19}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F23}
assert E19 == {'PSOE': 12, 'ERC': 13, 'JUNTS': 8, 'UP': 7, 'PP': 2, 'VOX': 2, 'CUP': 2, 'CS': 2}, E19
assert E23 == {'PSOE': 19, 'ERC': 7, 'JUNTS': 7, 'SUMAR': 7, 'PP': 6, 'VOX': 2, 'CUP': 0}, E23
assert sum(ESC['2026'].values()) == 48
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F23}
assert sum(E29.values()) == 48, E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
# versión del modelo que se usa: la última archivada, que es la misma que escenario-base.json
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'
CC = {l['lista']: l for l in MOD['ccaa']['Cataluña']['listas']}
assert MOD['ccaa']['Cataluña']['escanos_total'] == 48
P1 = {pr: {l['lista']: l['p_primera'] for l in MOD['provincias'][pr]['listas']} for pr in PROV}
assert all(max(P1[pr], key=P1[pr].get) == 'PSOE' for pr in PROV)

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=41.7)
assert len(cam) == NMUN
ORDG = ['PSOE', 'ERC', 'JUNTS', 'CUP', 'UP', 'SUMAR', 'PP', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
EMPN = lambda y: ', '.join(EMP[y].municipio)
g_mapgan = figura(f'ERC pasó de ganar en {GANA[Y19]["ERC"]} municipios a ganar en {GANA[Y23]["ERC"]}; el PSC, de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Cataluña, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Cataluña por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Cataluña por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Ganador según los votos de cada candidatura: '
                  'en 2019, En Comú Podem y Más País por separado (Más País no ganó en ninguno). En gris, los municipios en los que los dos primeros '
                  f'empataron a votos: en 2019, {EMPN(Y19)}; en 2023, {EMPN(Y23)}.',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], str(GANA[Y19].get(f, 0)), str(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', str(NMUN), str(NMUN)]]))

ORDT = ['PSOE', 'JUNTS', 'ERC', 'CUP', 'SUMAR', 'PP', 'VOX', 'EMPATE']
g_tam = figura(f'El PSC ganó en {GRANDES_PSC} de los {GRANDES} municipios de más de 20.000 habitantes; Junts, en {TT["Menos de 1.000"]["g23"]["JUNTS"]} de los pueblos de menos de 1.000',
               'Municipios ganados por cada partido en julio de 2023, según su población',
               apiladas([(nom, [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=128),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ORDT],
               (['Población', 'Municipios', 'Electores (2023)'] + [f'Ganó {NOMC[f]}' if f != 'EMPATE' else 'Empate' for f in ORDT],
                [[nom, str(t['n']), n(t['censo'])] + [str(t['g23'].get(f, 0)) for f in ORDT] for nom, t in TT.items()]))

COLIND = '#e7b416'
g_tampct = figura('El PSC subió en todos los tamaños de municipio; los independentistas bajaron en todos',
                  'Voto al PSC y a ERC, Junts y la CUP sumados, en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['psc19'], COL['PSOE'], .38, 'PSC, nov. 2019'), (t['psc23'], COL['PSOE'], 1, 'PSC, 2023'),
                                 (t['ind19'], COLIND, .38, 'ERC + Junts + CUP, nov. 2019'), (t['ind23'], COLIND, 1, 'ERC + Junts + CUP, 2023')]) for nom, t in TT.items()],
                         70, 'Voto al PSC y a los independentistas según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PSC', COL['PSOE']), ('ERC + Junts + CUP', COLIND), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PSC nov. 2019 (%)', 'PSC 2023 (%)', 'ERC+Junts+CUP nov. 2019 (%)', 'ERC+Junts+CUP 2023 (%)', 'ERC 2023 (%)', 'Junts 2023 (%)', 'PP 2023 (%)'],
                   [[nom, p(t['psc19']), p(t['psc23']), p(t['ind19']), p(t['ind23']), p(t['erc23']), p(t['junts23']), p(t['pp23'])] for nom, t in TT.items()]))

g_cap = figura('El PSC ganó en las cuatro capitales; en 2019 solo había ganado en Tarragona',
               'Voto al PSC, a ERC y a Junts en julio de 2023, en %, en cada capital de provincia',
               grupos([(NOMM[k], [(CA.at[k, f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PSOE', 'ERC', 'JUNTS')]) for k in CAP],
                      40, 'Voto al PSC, a ERC y a Junts en las capitales en 2023', W=440, ml=80),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ('PSOE', 'ERC', 'JUNTS')],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'PSC nov. 2019 (%)', 'PSC 2023 (%)', 'ERC nov. 2019 (%)', 'ERC 2023 (%)', 'Junts 2023 (%)', 'Sumar 2023 (%)', 'PP 2023 (%)'],
                [[NOMM[k], NOMC[CA.at[k, 'g2019']], NOMC[CA.at[k, 'g2023']], p(CA.at[k, f'{Y19}%PSOE']), p(CA.at[k, f'{Y23}%PSOE']),
                  p(CA.at[k, f'{Y19}%ERC']), p(CA.at[k, f'{Y23}%ERC']), p(CA.at[k, f'{Y23}%JUNTS']), p(CA.at[k, f'{Y23}%SUMAR']), p(CA.at[k, f'{Y23}%PP'])] for k in CAP]))

g_prov = figura('El PSC ganó en votos en las cuatro provincias, pero Junts ganó en más municipios en Girona y en Lleida',
                'Municipios ganados por cada partido en julio de 2023, por provincia',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDT if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada provincia en 2023', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ORDT],
                (['Provincia', 'Municipios', 'PSC 2023 (%)', 'ERC 2023 (%)', 'Junts 2023 (%)', 'Sumar 2023 (%)', 'PP 2023 (%)', 'Vox 2023 (%)', 'Municipios PSC', 'Municipios Junts', 'Municipios ERC'],
                 [[PROV[pr], str(PRN[pr])] + [p(PR[pr][Y23]['pct'][f]) for f in ('PSOE', 'ERC', 'JUNTS', 'SUMAR', 'PP', 'VOX')]
                  + [str(PRG[pr][Y23].get(f, 0)) for f in ('PSOE', 'JUNTS', 'ERC')] for pr in PROV]))

TRAMOS = [(-99, 10, '#fbd5d3', 'menos de 10'), (10, 15, '#f4a29d', '10 a 15'), (15, 20, '#e8645c', '15 a 20'),
          (20, 25, '#c9281f', '20 a 25'), (25, 99, '#7d120c', '25 o más')]
DPSCM = dict(zip(m.mun_code, m.dPSC))
tramo = lambda v: next(c for a, b, c, _ in TRAMOS if a < v <= b)
NTR = {e: int(((m.dPSC > a) & (m.dPSC <= b)).sum()) for a, b, _, e in TRAMOS}
g_mapdpsc = figura(f'El PSC subió en {PSC_SUBE} de los {NMUN} municipios',
                   'Cambio del voto al PSC entre noviembre de 2019 y julio de 2023 en cada municipio, en puntos',
                   mapa_svg(cam, H, lambda k: tramo(DPSCM[k]), lambda k: f'{s1(DPSCM[k])} puntos', 'Subida del PSC por municipio entre 2019 y 2023', NOMM),
                   'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                   [(f'{e} puntos', c) for _, _, c, e in TRAMOS],
                   (['Subida del PSC', 'Municipios'], [[f'{e} puntos', str(NTR[e])] for _, _, _, e in TRAMOS] + [['Total', str(NMUN)]]))

g_aj = figura(f'{NW[len(AJG)].capitalize()} municipios de más de 10.000 habitantes se decidieron en 2023 por menos de cinco puntos, todos entre el PSC y Junts',
              'Ventaja del partido más votado sobre el segundo en julio de 2023, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], 5.5,
                     'Municipios de más de 10.000 habitantes decididos por menos de cinco puntos', W=440, ml=110, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in dict.fromkeys(AJG.g2023)],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ventaja (puntos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), n(r.marg2023, 2), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'SUMAR', 'UP', 'ERC', 'CUP', 'JUNTS', 'PP', 'CS', 'VOX']


def hemi(lado=16, por_fila=24):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Cataluña en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PSOE', 'ERC', 'JUNTS', 'SUMAR', 'PP', 'VOX')
g_esc = figura(f'Con las encuestas, ERC pasaría de {E23["ERC"]} a {E29["ERC"]} diputados catalanes y Vox, de {E23["VOX"]} a {E29["VOX"]}',
               'Los 48 diputados de las cuatro provincias catalanas: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/barcelona/">/encuestas/</a>) {VERSION}. En 2019, En Comú Podem; en 2023, Sumar.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Provincia'] + [f'{NOMC[f]} 2023' for f in FT] + [f'{NOMC[f]} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in FT]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in FT] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Cataluña</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Cataluña por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=08019">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/cataluna/">datos de cada municipio de Cataluña</a></div>\n</figure>\n')

# --- Texto ---
EFE = 'https://www.infobae.com/espana/agencias/2026/11/08/rufian-apela-al-apoyo-de-los-socialistas-decepcionados-el-psc-no-merece-vuestro-voto/'
CG = 'https://cronicaglobal.elespanol.com/politica/20261109/illa-convencer-cataluna-indecisa-sanchez-pp-vox/1003742810327_0.html'
ELN = 'https://www.elnacional.cat/es/politica/nogueras-responde-illa-molesta-no-es-estemos-en-medio-sino-cada-dia-somos-mas_1722392_102.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
BCN = CA.loc['08019']
GIR = CA.loc['17079']
TP = TT['Menos de 1.000']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Cataluña elige el 29 de noviembre 48 de los 350 diputados del Congreso, los mismos que en 2023: 32 en Barcelona, 6 en Girona, 4 en Lleida y 6 en Tarragona. La campaña se juega entre el PSC de Salvador Illa, que gobierna la Generalitat, ERC y Junts. En un acto en Badalona, Gabriel Rufián pidió el voto a los socialistas «decepcionados» y dijo que el PSC «no merece» su voto, según <a href="{EFE}">EFE</a>.</p>
<blockquote class="cita"><p>«Está en juego el modelo del mundo que queremos y el futuro de nuestros hijos»</p><footer>Lluïsa Moret, viceprimera secretaria y portavoz del PSC, sobre el 29N, el 9 de noviembre de 2026, según <a href="{CG}">Crónica Global</a></footer></blockquote>
<p data-tipo="dato">Para saber de dónde parte cada uno, el mapa municipio a municipio cuenta un vuelco que el resultado global solo apunta. En noviembre de 2019, ERC fue el partido más votado en {GANA[Y19]["ERC"]} de los {NMUN} municipios catalanes, Junts en {GANA[Y19]["JUNTS"]} y el PSC en {GANA[Y19]["PSOE"]}. En julio de 2023, el PSC ganó en {GANA[Y23]["PSOE"]}, Junts en {GANA[Y23]["JUNTS"]} y ERC en {GANA[Y23]["ERC"]}. En otros {GANA[Y23]["EMPATE"]}, los dos primeros empataron a votos.</p>
{g_ins}
<p data-tipo="dato">El PSC pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} % de los votos, {p(DPSC)} puntos más, con {n(DPSC_VOTOS)} votos más pese a que votó menos gente: la participación bajó del {p(A19["part"])} % al {p(A23["part"])} %. ERC cayó del {p(A19["pct"]["ERC"])} % al {p(A23["pct"]["ERC"])} %, Junts del {p(A19["pct"]["JUNTS"])} % al {p(A23["pct"]["JUNTS"])} % y la CUP del {p(A19["pct"]["CUP"])} % al {p(A23["pct"]["CUP"])} %. De los {ERC_PIERDE} municipios que ERC dejó de ganar, {ERC_PSC} fueron para el PSC y {ERC_JUNTS} para Junts. El PSC conservó los {GANA[Y19]["PSOE"]} que ya tenía.</p>
{g_mapgan}
<p data-tipo="patron">Sumados, ERC, Junts y la CUP tenían en 2019 el {p(IND[Y19])} % de los votos catalanes; en 2023, el {p(IND[Y23])} %. El PSC subió en {PSC_SUBE} de los {NMUN} municipios, y en {PSC_MAS20} lo hizo más de 20 puntos.</p>
{g_mapdpsc}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">El mapa de 2023 tiene dos geografías. El PSC ganó en {GRANDES_PSC} de los {GRANDES} municipios de más de 20.000 habitantes, todos salvo Vic y Banyoles, que fueron de Junts. En los de menos de 1.000, en cambio, Junts ganó en {TP["g23"]["JUNTS"]} de {TP["n"]}, ERC en {TP["g23"]["ERC"]} y el PSC en {TP["g23"]["PSOE"]}. Como en los pueblos vive poca gente, los municipios ganados por el PSC suman el {p(POB["PSOE"])} % de la población catalana, y los de Junts, el {p(POB["JUNTS"])} %: más superficie en el mapa no significa más votantes.</p>
{g_tam}
<p data-tipo="dato">En los municipios de menos de 1.000 habitantes, ERC, Junts y la CUP sumaron el {p(TP["ind23"])} % en 2023, frente al {p(TP["ind19"])} % de 2019, y el PSC sacó el {p(TP["psc23"])} %. En las ciudades de más de 100.000, el PSC llegó al {p(TT["Más de 100.000"]["psc23"])} % y los tres partidos independentistas se quedaron en el {p(TT["Más de 100.000"]["ind23"])} %. El PSC subió y los independentistas bajaron en todos los tamaños de municipio.</p>
{g_tampct}
<p data-tipo="dato">En las capitales, el cambio fue completo. En 2019, ERC había ganado en Barcelona y en Lleida, Junts en Girona y el PSC solo en Tarragona. En 2023, el PSC ganó en las cuatro. En Barcelona sacó el {p(BCN[f"{Y23}%PSOE"])} %, frente al {p(BCN[f"{Y23}%SUMAR"])} % de Sumar y el {p(BCN[f"{Y23}%PP"])} % del PP; ERC, que había ganado con el {p(BCN[f"{Y19}%ERC"])} % en 2019, se quedó en el {p(BCN[f"{Y23}%ERC"])} %. En Girona, el PSC ganó con el {p(GIR[f"{Y23}%PSOE"])} % y Junts sacó el {p(GIR[f"{Y23}%JUNTS"])} %. Lo contamos barrio a barrio en {L("barcelona-barrio-a-barrio-29n", "Barcelona")} y en {L("girona-barri-a-barri-29n", "Girona")}.</p>
{g_cap}
<h2>Cuatro provincias: el PSC gana en votos, Junts en pueblos</h2>
<p data-tipo="dato">Por provincias, el PSC fue el más votado en las cuatro. En 2019 había ganado ERC en Girona, Lleida y Tarragona, y el PSC, por {p(PR["08"][Y19]["pct"]["PSOE"] - PR["08"][Y19]["pct"]["ERC"])} puntos, en Barcelona. En número de municipios, el PSC ganó en más que nadie en Barcelona ({PRG["08"][Y23]["PSOE"]} de {PRN["08"]}) y en Tarragona ({PRG["43"][Y23]["PSOE"]} de {PRN["43"]}). En Girona ganó en más Junts: en {PRG["17"][Y23]["JUNTS"]} de {PRN["17"]}, frente a {PRG["17"][Y23]["PSOE"]} del PSC. Y en Lleida, también Junts: {PRG["25"][Y23]["JUNTS"]} de {PRN["25"]}, frente a {PRG["25"][Y23]["PSOE"]} del PSC y {PRG["25"][Y23]["ERC"]} de ERC.</p>
{g_prov}
<h2>Dónde se decide por unos pocos votos</h2>
<p data-tipo="dato">En {AJ2} municipios catalanes, el primero sacó al segundo menos de dos puntos en 2023, y en {AJ10}, menos de diez votos, casi todos pueblos pequeños. En {GANA[Y23]["EMPATE"]}, los dos primeros sacaron exactamente los mismos votos: en {NW[EMP23["PSOE-ERC"]]}, el PSC y ERC, como en Albesa, en Lleida, o en Bràfim, en Tarragona; en {NW[EMP23["ERC-JUNTS"]]}, ERC y Junts, y en otros cuatro, Junts y el PSC o Sumar. Entre las ciudades, la más ajustada fue Vic: Junts ganó al PSC por {n(VIC.margv2023)} votos, {p(VIC.marg2023)} puntos. De los municipios de más de 10.000 habitantes, {NW[len(AJG)]} se decidieron por menos de cinco puntos, y en todos el duelo fue entre el PSC y Junts.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central da al PSC {E29["PSOE"]} de los 48 diputados catalanes, {NW.get(E23["PSOE"] - E29["PSOE"], E23["PSOE"] - E29["PSOE"])} menos que en 2023; a ERC, {E29["ERC"]}, {E29["ERC"] - E23["ERC"]} más; a Junts, {E29["JUNTS"]}; al PP, {E29["PP"]}; a Vox, {E29["VOX"]}, y a Sumar, {E29["SUMAR"]}, {NW[E23["SUMAR"] - E29["SUMAR"]]} menos. La CUP no tiene diputado en el reparto central. En las cuatro provincias, el PSC es el más votado en la mayoría de las simulaciones: en Barcelona, en el {n(P1["08"]["PSOE"] * 100)} %; en Lleida, en el {n(P1["25"]["PSOE"] * 100)} %.</p>
{g_esc}
<p data-tipo="contexto">Junts discute al PSC el centro político. Míriam Nogueras, de Junts, respondió a Illa en un acto de presentación de sus candidatos: «Quizás lo que le molesta al señor Illa no es que estemos en medio, quizás lo que le molesta es que los del medio cada día somos más», según <a href="{ELN}">ElNacional.cat</a>. Y Oriol Junqueras presentó a ERC en Badalona como «el único partido político que siempre ha plantado cara a la extrema derecha y la derecha extrema», según <a href="{EFE}">EFE</a>.</p>
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de ERC en 2023. Que el PSC subiera mientras bajaban ERC y la participación encaja con un trasvase, pero también con votantes independentistas que se quedaron en casa y otros que votaron por primera vez. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 18 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de Cataluña desde 1977, con las autonómicas, está en {L("cataluna-historia-electoral", "Cataluña en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/cataluna/">la ficha de Cataluña</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Cataluña?',
     f'El PSC, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante de Sumar ({p(A23["pct"]["SUMAR"])} %), el PP ({p(A23["pct"]["PP"])} %) y ERC ({p(A23["pct"]["ERC"])} %). Sacó {E23["PSOE"]} diputados; ERC, Junts y Sumar, {E23["ERC"]} cada uno; el PP, {E23["PP"]}, y Vox, {E23["VOX"]}.'),
    ('¿En cuántos municipios catalanes ganó el PSC en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; Junts, en {GANA[Y23]["JUNTS"]}; ERC, en {GANA[Y23]["ERC"]}; Sumar, en {GANA[Y23]["SUMAR"]}; la CUP, en {GANA[Y23]["CUP"]}; el PP, en {GANA[Y23]["PP"]}, y Vox, en {GANA[Y23]["VOX"]}. En otros {GANA[Y23]["EMPATE"]} hubo empate a votos. En noviembre de 2019, el PSC había ganado en {GANA[Y19]["PSOE"]} y ERC en {GANA[Y19]["ERC"]}.'),
    ('¿Cuántos diputados elige Cataluña el 29N?',
     '48, los mismos que en 2023: Barcelona elige 32; Girona y Tarragona, 6 cada una, y Lleida, 4.'),
    ('¿Qué dicen las encuestas en Cataluña?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PSC {E29["PSOE"]} escaños, a ERC {E29["ERC"]}, a Junts {E29["JUNTS"]}, al PP {E29["PP"]}, a Vox {E29["VOX"]} y a Sumar {E29["SUMAR"]}, con un margen amplio.'),
]
enlaces = (f'{L("cataluna-historia-electoral", "Historia electoral de Cataluña")} · {L("barcelona-barrio-a-barrio-29n", "Barcelona barrio a barrio")} · '
           f'<a href="{BASE}elecciones/cataluna/">Datos de cada municipio</a> · <a href="{BASE}encuestas/barcelona/">Encuesta en Barcelona</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio (sin voto exterior); población del padrón municipal del INE (2023); '
        'media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_cataluna.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'ERC_PSC': ERC_PSC, 'ERC_JUNTS': ERC_JUNTS, 'JUNTS_PSC': JUNTS_PSC, 'ERC_PIERDE': ERC_PIERDE,
    'IND': IND, 'DPSC': DPSC, 'DPSC_VOTOS': DPSC_VOTOS, 'POB': POB, 'PSC_SUBE': PSC_SUBE, 'PSC_MAS20': PSC_MAS20, 'NTR': NTR,
    'TT': TT, 'GRANDES': GRANDES, 'GRANDES_PSC': GRANDES_PSC, 'AJ2': AJ2, 'AJ10': AJ10, 'EMP23': EMP23,
    'EMPM': {y[:4]: list(EMP[y].municipio) for y in EMP},
    'PR': {pr: {y: PR[pr][y]['pct'] for y in PR[pr]} for pr in PR}, 'PRG': PRG, 'PRN': PRN,
    'CAP': {k: {'nombre': NOMM[k], 'g19': CA.at[k, 'g2019'], 'g23': CA.at[k, 'g2023'], **{f'{f.lower()}{y[2:4]}': R(CA.at[k, f'{y}%{f}'])
                                                                                   for f in ('PSOE', 'ERC', 'JUNTS', 'SUMAR', 'PP') for y in (Y19, Y23)}} for k in CAP},
    'AJG': [[r.municipio, r.g2023, r.seg2023, int(r.margv2023), R(r.marg2023)] for _, r in AJG.iterrows()],
    'VIC': [VIC.municipio, int(VIC.margv2023), R(VIC.marg2023)],
    'E19': E19, 'E23': E23, 'ESC23': ESC[Y23], 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC, 'P1': {pr: P1[pr].get('PSOE') for pr in PROV},
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Cataluña',
      f'El mapa electoral de Cataluña: ERC pasó de ganar en {GANA[Y19]["ERC"]} municipios a ganar en {GANA[Y23]["ERC"]}, y el PSC, de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]}',
      f'En 2023, el PSC ganó en {GRANDES_PSC} de los {GRANDES} municipios de más de 20.000 habitantes y en las cuatro capitales; Junts, en {GANA[Y23]["JUNTS"]} pueblos, sobre todo de Girona y Lleida. '
      f'Para el 29N, la media de encuestas da al PSC {E29["PSOE"]} de los 48 diputados, y a ERC, {E29["ERC"]}.',
      '11 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'TR', ERC_PSC, ERC_JUNTS, JUNTS_PSC, 'IND', IND, 'POB', POB, 'E29', E29, 'AJ', AJ2, AJ10, list(AJG.municipio), 'EMP23', EMP23, 'NTR', NTR, PSC_SUBE, PSC_MAS20)
