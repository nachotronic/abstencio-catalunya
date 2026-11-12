"""«El mapa electoral de Andalucía» (10-11-2026), primera pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 785 municipios andaluces en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas por
separado: en 2019, Unidas Podemos y Más País), el cambio del PP, el tamaño de los municipios (padrón municipal del INE de
2023), las capitales, los municipios más ajustados y el reparto central del modelo de /encuestas/ para
el 29N. Contexto: EFE (10-11-2026) y El Mira (6-11-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_andalucia.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, s1, trazados)

A = BASE + 'actualidad/'
NW = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve'}
SLUG = 'mapa-electoral-andalucia-29n'
PROV = {'04': 'Almería', '11': 'Cádiz', '14': 'Córdoba', '18': 'Granada', '21': 'Huelva', '23': 'Jaén', '29': 'Málaga', '41': 'Sevilla'}
PSLUG = {'04': 'almeria', '11': 'cadiz', '14': 'cordoba', '18': 'granada', '21': 'huelva', '23': 'jaen', '29': 'malaga', '41': 'sevilla'}
CAP = {'04013': 'Almería', '11012': 'Cádiz', '14021': 'Córdoba', '18087': 'Granada', '21041': 'Huelva', '23050': 'Jaén', '29067': 'Málaga', '41091': 'Sevilla'}
CAJA = (-7.7, 35.8, -1.5, 39.0)

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 785
NOMM = dict(zip(m.mun_code, m.municipio))
A19, A23 = agrega(m, Y19), agrega(m, Y23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 699, 'PP': 37, 'VOX': 33, 'UP': 12, 'EMPATE': 3, 'CS': 1}, GANA[Y19]
assert GANA[Y23] == {'PSOE': 466, 'PP': 307, 'SUMAR': 10, 'EMPATE': 1, 'VOX': 1}, GANA[Y23]
PSOE_PP = int(((m.g2019 == 'PSOE') & (m.g2023 == 'PP')).sum())
VOX_PP = int(((m.g2019 == 'VOX') & (m.g2023 == 'PP')).sum())
assert PSOE_PP == 233 and VOX_PP == 33
# Empates (mismo número de votos entre los dos primeros): gris en los mapas
EMP = {y: m[m[f'g{y[:4]}'] == 'EMPATE'] for y in (Y19, Y23)}
assert list(EMP[Y19].municipio) == ['Bayarque', 'Beires', 'Huécija'] and set(EMP[Y19].emp2019) == {'PP-PSOE'}
assert list(EMP[Y23].municipio) == ['Doña Mencía'] and EMP[Y23].iloc[0].emp2023 == 'PSOE-SUMAR' and EMP[Y23].iloc[0].g2019 == 'PSOE'
PSOE_PIERDE = int(((m.g2019 == 'PSOE') & (m.g2023 != 'PSOE')).sum())
PSOE_GANA = int(((m.g2019 != 'PSOE') & (m.g2023 == 'PSOE')).sum())
assert (PSOE_PIERDE, PSOE_GANA) == (237, 4) and PSOE_PIERDE - PSOE_GANA == GANA[Y19]['PSOE'] - GANA[Y23]['PSOE']
PSOE_MENOS = GANA[Y19]['PSOE'] - GANA[Y23]['PSOE']
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP = A23['pct']['PP'] - A19['pct']['PP']
DPSOE = A23['pct']['PSOE'] - A19['pct']['PSOE']
assert abs(DPSOE) < .1 and DPSOE_VOTOS > 0
DER19 = A19['pct']['PP'] + A19['pct']['VOX'] + A19['pct']['CS']
DER23 = A23['pct']['PP'] + A23['pct']['VOX']
POB = {f: float(m[m.g2023 == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')}
m['dPP'] = m[f'{Y23}%PP'] - m[f'{Y19}%PP']
PP_SUBE = int((m.dPP > 0).sum())
PP_MAS20 = int((m.dPP > 20).sum())

# Provincias
PR = {pr: {y: agrega(m[m.prov == pr], y) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
assert PRG['04'][Y23] == {'PP': 69, 'PSOE': 34} and PRG['41'][Y23]['PSOE'] == 84
NPSOE_MAS = sum(PRG[pr][Y23].get('PSOE', 0) > PRG[pr][Y23].get('PP', 0) for pr in PROV)
assert NPSOE_MAS == 7
assert sum(PR[pr][Y23]['pct']['PP'] > PR[pr][Y23]['pct']['PSOE'] for pr in PROV) == 7 and PR['41'][Y23]['pct']['PSOE'] > PR['41'][Y23]['pct']['PP']

# Capitales
CA = m[m.mun_code.isin(CAP)].set_index('mun_code')
CAP_PP = int((CA.g2023 == 'PP').sum())
assert CAP_PP == 7 and CA.loc['11012', 'g2023'] == 'PSOE' and (CA.g2019 == 'PSOE').sum() == 7

# Tamaño de municipio (padrón municipal del INE, 2023)
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000),
       ('De 20.000 a 100.000', 20000, 100000), ('Más de 100.000', 100000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(),
               'pp23': agrega(g, Y23)['pct']['PP'], 'psoe23': agrega(g, Y23)['pct']['PSOE'],
               'pp19': agrega(g, Y19)['pct']['PP'], 'psoe19': agrega(g, Y19)['pct']['PSOE'], 'vox23': agrega(g, Y23)['pct']['VOX']}
assert sum(t['n'] for t in TT.values()) == NMUN
assert TT['Más de 100.000']['g23'] == {'PP': 11, 'PSOE': 2}
assert [t['psoe23'] < t['psoe19'] for t in TT.values()] == [True, True, True, False, False] and all(t['pp23'] > t['pp19'] for t in TT.values())
PEQ = TT['Menos de 1.000']['g23'].get('PSOE', 0) + TT['De 1.000 a 5.000']['g23'].get('PSOE', 0)
NPEQ = TT['Menos de 1.000']['n'] + TT['De 1.000 a 5.000']['n']

# Municipios ajustados en 2023
AJ2 = int((m.marg2023 < 2).sum())
AJ10 = int((m.margv2023 < 10).sum())
AJG = m[(m.poblacion >= 20000) & (m.marg2023 < 1)].sort_values('marg2023')
assert list(AJG.municipio) == ['Barbate', 'Puente Genil', 'San Roque', 'Motril', 'San Fernando', 'Almonte'], list(AJG.municipio)
PUENTE = m[m.municipio == 'Puente de Génave'].iloc[0]
assert PUENTE.g2023 == 'VOX' and PUENTE.seg2023 == 'PSOE'
assert AJG.iloc[0].g2023 == 'PSOE' and AJG.iloc[0].seg2023 == 'PP'

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(list(PROV))
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in ('PP', 'PSOE', 'VOX', 'UP', 'CS')}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}
assert E19 == {'PP': 15, 'PSOE': 25, 'VOX': 12, 'UP': 6, 'CS': 3} and E23 == {'PP': 25, 'PSOE': 21, 'VOX': 9, 'SUMAR': 6}
assert sum(ESC['2026'].values()) == 60 and ESC['2026']['11'] == 8
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}
assert sum(E29.values()) == 60, E29
assert all(sum(v[0] for v in RC[pr].values()) == ESC['2026'][pr] for pr in PROV)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
CC = {l['lista']: l for l in MOD['ccaa']['Andalucía']['listas']}
assert MOD['ccaa']['Andalucía']['escanos_total'] == 60
SEV = {l['lista']: l for l in MOD['provincias']['41']['listas']}
assert SEV['PP']['p_primera'] > .5 > SEV['PSOE']['p_primera'] > .45
# Desde el 11-11-2026 el modelo incluye a Adelante Andalucía; la pieza conserva el reparto del 10 de noviembre
# (sin ella) y cita aparte lo que le da el del 11. Volver a ejecutar este script cambiaría las cifras del reparto.

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=37.4)
assert len(cam) == NMUN
GNOM = {k: NOM[k] for k in NOM}
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}, y el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Andalucía, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[m.set_index('mun_code').at[k, 'g2019']], lambda k: NOM[m.set_index('mun_code').at[k, 'g2019']],
                           'Municipios de Andalucía por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[m.set_index('mun_code').at[k, 'g2023']], lambda k: NOM[m.set_index('mun_code').at[k, 'g2023']],
                             'Municipios de Andalucía por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Ganador según los votos de cada candidatura: '
                  'en 2019, Unidas Podemos y Más País por separado (Más País no ganó en ninguno). En gris, los empates: en 2019, Bayarque, Beires y Huécija '
                  '(PP y PSOE con los mismos votos); en 2023, Doña Mencía (PSOE y Sumar).',
                  [(NOM[f], COL[f]) for f in ('PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'CS', 'EMPATE')],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOM[f], str(GANA[Y19].get(f, 0)), str(GANA[Y23].get(f, 0))] for f in ('PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'CS', 'EMPATE')]
                   + [['Total', str(NMUN), str(NMUN)]]))

ORDT = ['PSOE', 'PP', 'SUMAR', 'VOX', 'EMPATE']
g_tam = figura(f'El PSOE ganó en {PEQ} de los {NPEQ} municipios de menos de 5.000 habitantes; el PP, en 11 de las 13 ciudades de más de 100.000',
               'Municipios ganados por cada partido en julio de 2023, según su población',
               apiladas([(nom, [(t['g23'].get(f, 0), COL[f], NOM[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=128),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOM[f], COL[f]) for f in ORDT],
               (['Población', 'Municipios', 'Electores (2023)', 'Ganó el PSOE', 'Ganó el PP', 'Ganó Sumar', 'Ganó Vox', 'Empate'],
                [[nom, str(t['n']), n(t['censo'])] + [str(t['g23'].get(f, 0)) for f in ORDT] for nom, t in TT.items()]))

g_tampct = figura('El PSOE saca más en los pueblos; el PP, en las ciudades',
                  'Voto al PSOE y al PP en julio de 2023, en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023')]) for nom, t in TT.items()],
                         50, 'Voto al PSOE y al PP según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PSOE', COL['PSOE']), ('PP', COL['PP']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'Vox 2023 (%)'],
                   [[nom, p(t['psoe19']), p(t['psoe23']), p(t['pp19']), p(t['pp23']), p(t['vox23'])] for nom, t in TT.items()]))

ORDP = sorted(PROV, key=lambda pr: -(PR[pr][Y23]['pct']['PP'] - PR[pr][Y23]['pct']['PSOE']))
g_prov = figura('El PP ganó en votos en siete provincias; el PSOE, en Sevilla',
                'Voto al PP, al PSOE y a Vox en julio de 2023, en %, por provincia',
                grupos([(PROV[pr], [(PR[pr][Y23]['pct'][f], COL[f], 1, NOM[f]) for f in ('PP', 'PSOE', 'VOX')]) for pr in ORDP],
                       45, 'Voto al PP, al PSOE y a Vox por provincia en 2023', W=440, ml=72),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('Vox', COL['VOX'])],
                (['Provincia', 'Municipios', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Sumar 2023 (%)', 'Municipios PSOE', 'Municipios PP'],
                 [[PROV[pr], str(PRN[pr])] + [p(PR[pr][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]
                  + [str(PRG[pr][Y23].get('PSOE', 0)), str(PRG[pr][Y23].get('PP', 0))] for pr in ORDP]))

TRAMOS = [(-99, 10, '#dbe9f6', 'menos de 10'), (10, 14, '#a9cbe8', '10 a 14'), (14, 18, '#6aa6d6', '14 a 18'),
          (18, 22, '#2f7cc0', '18 a 22'), (22, 99, '#0d4a8a', '22 o más')]
DPPM = dict(zip(m.mun_code, m.dPP))
tramo = lambda v: next(c for a, b, c, _ in TRAMOS if a < v <= b)
NTR = {e: int(((m.dPP > a) & (m.dPP <= b)).sum()) for a, b, _, e in TRAMOS}
g_mapdpp = figura(f'El PP subió en {PP_SUBE} de los {NMUN} municipios',
                  'Cambio del voto al PP entre noviembre de 2019 y julio de 2023 en cada municipio, en puntos',
                  mapa_svg(cam, H, lambda k: tramo(DPPM[k]), lambda k: f'{s1(DPPM[k])} puntos', 'Subida del PP por municipio entre 2019 y 2023', NOMM),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [(f'{e} puntos', c) for _, _, c, e in TRAMOS],
                  (['Subida del PP', 'Municipios'], [[f'{e} puntos', str(NTR[e])] for _, _, _, e in TRAMOS] + [['Total', str(NMUN)]]))

g_cap = figura(f'El PP ganó en {NW[CAP_PP]} de las ocho capitales; en 2019, el PSOE había ganado en siete',
               'Voto al PP y al PSOE en julio de 2023, en %, en cada capital de provincia',
               grupos([(NOMM[k], [(CA.at[k, f'{Y23}%PP'], COL['PP'], 1, 'PP'), (CA.at[k, f'{Y23}%PSOE'], COL['PSOE'], 1, 'PSOE')])
                       for k in sorted(CAP, key=lambda k: -(CA.at[k, f'{Y23}%PP'] - CA.at[k, f'{Y23}%PSOE']))],
                      50, 'Voto al PP y al PSOE en las capitales en 2023', W=440, ml=72),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)'],
                [[NOMM[k], NOM[CA.at[k, 'g2019']], NOM[CA.at[k, 'g2023']], p(CA.at[k, f'{Y19}%PP']), p(CA.at[k, f'{Y23}%PP']),
                  p(CA.at[k, f'{Y19}%PSOE']), p(CA.at[k, f'{Y23}%PSOE'])] for k in sorted(CAP, key=lambda k: NOMM[k])]))

g_aj = figura(f'Seis municipios de más de 20.000 habitantes se decidieron en 2023 por menos de un punto',
              'Ventaja del partido más votado sobre el segundo en julio de 2023, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOM[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], 1.2,
                     'Municipios de más de 20.000 habitantes decididos por menos de un punto', W=440, ml=100, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOM[f], COL[f]) for f in ('PSOE', 'PP')],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ventaja (puntos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOM[r.g2023], NOM[r.seg2023], n(r.margv2023), n(r.marg2023, 2), NOM[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PP', 'PSOE', 'VOX', 'SUMAR', 'UP', 'CS']


def hemi(lado=16, por_fila=21):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOM[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Andalucía en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, Vox pasaría de {E23["VOX"]} a {E29["VOX"]} diputados andaluces y Sumar, de {E23["SUMAR"]} a {E29["SUMAR"]}',
               'Los diputados de las ocho provincias andaluzas: un cuadrado por escaño. En 2026, Andalucía elige 60, uno menos: Cádiz pasa de 9 a 8',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/sevilla/">/encuestas/</a>) a las 2.31 del 10 de noviembre de 2026. En 2019, Unidas Podemos; en 2023, Sumar.',
               [(NOM[f], COL[f]) for f in ORDE],
               (['Provincia', 'PP 2023', 'PSOE 2023', 'Vox 2023', 'Sumar 2023', 'PP 29N', 'PSOE 29N', 'Vox 29N', 'Sumar 29N'],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')] + [str(E29[f]) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Andalucía</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Andalucía por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=41091">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/andalucia/">datos de cada municipio de Andalucía</a></div>\n</figure>\n')

# --- Texto ---
EFE = 'https://www.infobae.com/espana/agencias/2026/11/10/el-pp-busca-su-segunda-victoria-en-andalucia-donde-adelante-podria-tener-representacion/'
MIRA = 'https://www.elmira.es/articulo/andalucia/montero-pone-cifra-escanos-psoe-29n-asegura-que-mejorara-resultado-2023-seguira-gobernando/20261106102033627014.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
SEVR = RC['41']
ALM = PR['04'][Y23]['pct']
SEVP = PR['41'][Y23]['pct']
CAD = CA.loc['11012']
BAR = AJG.iloc[0]

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Andalucía elige el 29 de noviembre 60 de los 350 diputados del Congreso, uno menos que en 2023, y es la comunidad que más aporta. Pedro Sánchez empieza la campaña en Sevilla, «provincia en la que siempre han ganado los socialistas», y el PP «busca repetir» como la fuerza más votada en Andalucía en unas generales, algo que logró por primera vez en 2023, según <a href="{EFE}">EFE</a>. Serán seis meses después de las autonómicas del 17 de mayo, en las que el PP de Juanma Moreno perdió por poco la mayoría absoluta y pactó un gobierno con Vox.</p>
<blockquote class="cita"><p>«Va a mejorar los resultados respecto a los que tenía»</p><footer>María Jesús Montero, secretaria general del PSOE de Andalucía, sobre el PSOE el 29N, el 5 de noviembre de 2026 en Sevilla, según <a href="{MIRA}">El Mira</a></footer></blockquote>
<p data-tipo="dato">Para saber de dónde parte cada uno, el mapa municipio a municipio cuenta algo que el resultado global esconde. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios andaluces. En julio de 2023 ganó en {GANA[Y23]["PSOE"]}, {PSOE_MENOS} menos, y en otro, Doña Mencía, empató a votos con Sumar. Y sin embargo su voto no bajó: sacó el {p(A19["pct"]["PSOE"])} % en 2019 y el {p(A23["pct"]["PSOE"])} % en 2023, con {n(DPSOE_VOTOS)} votos más.</p>
{g_ins}
<p data-tipo="dato">Lo que cambió fue el resto del tablero. El PP pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, {p(DPP)} puntos más, y de ganar en {GANA[Y19]["PP"]} municipios a ganar en {GANA[Y23]["PP"]}. Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó en 2023, y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. De los {PSOE_PIERDE} municipios que el PSOE dejó de ganar, {PSOE_PP} fueron para el PP (a cambio, el PSOE ganó en {NW[PSOE_GANA]} que en 2019 habían sido de Unidas Podemos), y en los {VOX_PP} que había ganado Vox en 2019, sobre todo en Málaga y Almería, ganó el PP.</p>
{g_mapgan}
<p data-tipo="patron">Sumados, PP, Vox y Ciudadanos tenían en 2019 el {p(DER19)} % de los votos andaluces; PP y Vox, en 2023, el {p(DER23)} %. El bloque creció menos de tres puntos; lo que más cambió es que casi todo ese voto se concentró en una papeleta, y con eso el PP adelantó al PSOE en {PSOE_PP} municipios. El PP subió en {PP_SUBE} de los {NMUN} municipios, y en {PP_MAS20} lo hizo más de 20 puntos.</p>
{g_mapdpp}
<h2>Los pueblos y las ciudades</h2>
<p data-tipo="patron">El mapa de 2023 tiene dos colores con dos geografías. El PSOE ganó en {PEQ} de los {NPEQ} municipios de menos de 5.000 habitantes, y el PP, en 11 de las 13 ciudades de más de 100.000. Como en los pueblos vive poca gente, los municipios ganados por el PSOE suman el {p(POB["PSOE"])} % de la población andaluza, y los ganados por el PP, el {p(POB["PP"])} %: más rojo en el mapa no significa más votantes.</p>
{g_tam}
<p data-tipo="dato">En los municipios de menos de 1.000 habitantes, el PSOE sacó el {p(TT["Menos de 1.000"]["psoe23"])} % en 2023 y el PP, el {p(TT["Menos de 1.000"]["pp23"])} %. En las ciudades de más de 100.000 fue al revés: PP {p(TT["Más de 100.000"]["pp23"])} %, PSOE {p(TT["Más de 100.000"]["psoe23"])} %. El PP subió en todos los tamaños de municipio. El PSOE bajó en los de menos de 20.000 habitantes y subió algo en los mayores, y por eso su voto total quedó igual.</p>
{g_tampct}
<p data-tipo="dato">En las capitales, el cambio fue completo. En 2019, el PSOE había ganado en siete de las ocho; solo Granada fue del PP. En 2023, el PP ganó en {NW[CAP_PP]}, todas salvo Cádiz, donde el PSOE sacó el {p(CAD[f"{Y23}%PSOE"])} % y el PP, el {p(CAD[f"{Y23}%PP"])} %. Sevilla, la mayor, pasó del PSOE al PP con un {p(CA.at["41091", f"{Y23}%PP"])} % frente a un {p(CA.at["41091", f"{Y23}%PSOE"])} %.</p>
{g_cap}
<h2>Ocho provincias: el PP gana en votos, el PSOE en municipios</h2>
<p data-tipo="dato">Por provincias, el PP fue el más votado en siete y el PSOE en una, Sevilla, donde sacó el {p(SEVP["PSOE"])} % frente al {p(SEVP["PP"])} % del PP. La mayor ventaja del PP fue la de Almería, con el {p(ALM["PP"])} % frente al {p(ALM["PSOE"])} % del PSOE y el {p(ALM["VOX"])} % de Vox. Aun así, en número de municipios, el PSOE ganó en más que el PP en {NW[NPSOE_MAS]} de las ocho provincias, todas salvo Almería: en Sevilla, en {PRG["41"][Y23]["PSOE"]} de los {PRN["41"]}; en Jaén, en {PRG["23"][Y23]["PSOE"]} de los {PRN["23"]}.</p>
{g_prov}
<h2>Dónde se decide por unos pocos votos</h2>
<p data-tipo="dato">En {AJ2} municipios andaluces, el primero sacó al segundo menos de dos puntos en 2023, y en {AJ10}, menos de diez votos, casi todos pueblos pequeños. Entre los de más de 20.000 habitantes, seis se decidieron por menos de un punto. En {BAR.municipio}, el PSOE ganó al PP por {n(BAR.margv2023)} votos. En Puente de Génave, en Jaén, Vox fue el más votado: el único municipio andaluz que ganó en 2023, por {n(PUENTE.margv2023)} votos sobre el PSOE.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} de los 60 diputados andaluces, los mismos que en 2023; al PSOE, {E29["PSOE"]}, dos menos; a Vox, {E29["VOX"]}, seis más, y a Sumar, {E29["SUMAR"]}. En Sevilla, el modelo da casi las mismas opciones al PP y al PSOE de ser el más votado: el PP lo es en el {n(SEV["PP"]["p_primera"] * 100)} % de las simulaciones y el PSOE, en el {n(SEV["PSOE"]["p_primera"] * 100)} %. Cádiz elige ocho diputados en lugar de nueve, y con los votos de 2023 el que pierde habría sido el cuarto del PP, como se contó en {L("cadiz-madrid-29n", "Cádiz pierde un escaño y Madrid lo gana").replace(A + "cadiz-madrid-29n/", BASE + "atlas/bisagras/cadiz-madrid-29n/")}.</p>
{g_esc}
<p data-tipo="contexto">La gran incógnita andaluza está a la izquierda del PSOE. Adelante Andalucía, que en mayo sacó ocho diputados autonómicos, se presenta sola, sin el Frente Amplio, y «la mayoría de las encuestas» le dan representación en el Congreso, según <a href="{EFE}">EFE</a>. El reparto de arriba es el del modelo del 10 de noviembre, que todavía no la incluía como lista propia. Desde el 11 de noviembre la incluye: con la media de encuestas de ese día, le da 3 de los 60 diputados andaluces, uno en Cádiz, otro en Málaga y otro en Sevilla (<a href="{BASE}encuestas/provincias.html">reparto por provincia</a>). Qué votantes se llevó en las autonómicas lo contamos en {L("adelante-andalucia-psoe-29n", "Uno de cada tres votantes de Adelante venía del PSOE")}.</p>
<blockquote class="cita"><p>«A lo mejor» lo «está pensando el señor Moreno Bonilla»</p><footer>María Jesús Montero, sobre «quién es el que está pensando en coger la maleta para Madrid» si el PP pierde, el 5 de noviembre de 2026, según <a href="{MIRA}">El Mira</a></footer></blockquote>
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP creciera casi lo mismo que perdieron los otros dos encaja con un trasvase, pero también pudo haber votantes que se quedaran en casa y otros nuevos. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales que cita EFE (36,41 % para el PP y 33,5 % para el PSOE, con el voto exterior y sobre votos válidos). Las encuestas tienen un margen amplio a 19 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la comunidad desde 1977, con las autonómicas, está en {L("andalucia-historia-electoral", "¿Quién gobierna Andalucía?")}, y lo que pasó entre el PP de Moreno y el de Feijóo, en {L("pp-andalucia-autonomicas-generales-29n", "Moreno y Feijóo en Andalucía")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/andalucia/">la ficha de Andalucía</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Andalucía?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %). Sacó {E23["PP"]} diputados, el PSOE {E23["PSOE"]}, Vox {E23["VOX"]} y Sumar {E23["SUMAR"]}.'),
    ('¿En cuántos municipios andaluces ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}; Sumar, en {GANA[Y23]["SUMAR"]}, y Vox, en {GANA[Y23]["VOX"]}. En otro, Doña Mencía, empataron el PSOE y Sumar. En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]}.'),
    ('¿Cuántos diputados elige Andalucía el 29N?',
     f'60, uno menos que en 2023: Cádiz pasa de 9 a 8. Sevilla elige 12; Málaga, 11; Cádiz, 8; Granada, 7; Almería y Córdoba, 6, y Huelva y Jaén, 5.'),
    ('¿Qué dicen las encuestas en Andalucía?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]}, a Vox {E29["VOX"]} y a Sumar {E29["SUMAR"]}, con un margen amplio.'),
]
enlaces = (f'{L("andalucia-historia-electoral", "Historia electoral de Andalucía")} · {L("adelante-andalucia-psoe-29n", "Adelante y el PSOE")} · '
           f'<a href="{BASE}elecciones/andalucia/">Datos de cada municipio</a> · <a href="{BASE}encuestas/sevilla/">Encuesta en Sevilla</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio (sin voto exterior); población del padrón municipal del INE (2023); '
        'media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_andalucia.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PSOE_PIERDE': PSOE_PIERDE, 'PSOE_GANA': PSOE_GANA, 'VOX_PP': VOX_PP, 'PP_SUBE': PP_SUBE, 'PP_MAS20': PP_MAS20, 'POB': POB,
    'TT': TT, 'NPSOE_MAS': NPSOE_MAS, 'DER19': DER19, 'DER23': DER23, 'PEQ': PEQ, 'NPEQ': NPEQ, 'AJ2': AJ2, 'AJ10': AJ10, 'NTR': NTR,
    'PR': {pr: {y: PR[pr][y]['pct'] for y in PR[pr]} for pr in PR}, 'PRG': PRG, 'PRN': PRN,
    'CAP': {k: {'nombre': NOMM[k], 'g19': CA.at[k, 'g2019'], 'g23': CA.at[k, 'g2023'], 'pp19': R(CA.at[k, f'{Y19}%PP']), 'pp23': R(CA.at[k, f'{Y23}%PP']),
                'psoe19': R(CA.at[k, f'{Y19}%PSOE']), 'psoe23': R(CA.at[k, f'{Y23}%PSOE'])} for k in CAP},
    'AJG': [[r.municipio, r.g2023, r.seg2023, int(r.margv2023), R(r.marg2023)] for _, r in AJG.iterrows()],
    'PUENTE': [PUENTE.municipio, int(PUENTE.margv2023)],
    'E19': E19, 'E23': E23, 'ESC23': ESC[Y23], 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC, 'SEV_P1': {k: SEV[k]['p_primera'] for k in ('PP', 'PSOE')},
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Andalucía',
      f'El mapa electoral de Andalucía: el PSOE ganó en {PSOE_MENOS} municipios menos en 2023 sin perder votos',
      f'En noviembre de 2019 ganó en {GANA[Y19]["PSOE"]} de los {NMUN} municipios andaluces; en 2023, en {GANA[Y23]["PSOE"]}, con el mismo {p(A23["pct"]["PSOE"])} %. '
      f'El PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]} y ganó en {NW[CAP_PP]} de las ocho capitales. Para el 29N, la media de encuestas le da {E29["PP"]} de los 60 diputados, y a Vox, {E29["VOX"]}.',
      '10 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('PSOE', GANA, 'POB', POB, 'TT', {k: (v['n'], v['g23']) for k, v in TT.items()}, 'E29', E29, 'AJ', AJ2, AJ10, 'NTR', NTR, PP_SUBE, PP_MAS20)
