"""«El mapa electoral de Aragón» (2026-11), décima pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 731 municipios de Aragón en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas
por separado: en 2019, Unidas Podemos y Más País; Teruel Existe y el PAR con columna propia), el tamaño de los municipios
(padrón de 2023), las tres capitales, las provincias, Teruel Existe (40 municipios en 2019, 5 en 2023), Vox en el
entorno de Zaragoza, los empates y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: Onda Aragonesa (Tomás Guitarte, 5-10-2026; lista del PSOE de Zaragoza, 25-10-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_aragon.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-aragon-29n'
PROV = {'50': 'Zaragoza', '22': 'Huesca', '44': 'Teruel'}
PSLUG = {'50': 'zaragoza', '22': 'huesca', '44': 'teruel'}
CAPITAL = {'50297': 'Zaragoza', '22125': 'Huesca', '44216': 'Teruel'}
CAJA = (-2.2, 39.8, 0.8, 42.95)
import sys  # noqa: E402
sys.path.insert(0, str(RAIZ / 'generales-2026' / 'src'))
from partidos import PROPIAS  # noqa: E402
PC = {k: c for k, _, c in PROPIAS}
COLC = dict(COL, TE=PC['TE'], PAR=PC['PAR'])
NOMC = dict(NOM, EMPATE='Empate a votos', TE='Teruel Existe', PAR='PAR')
SIMC = {'Teruel Existe': 'TE'}

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 731
NOMM = dict(zip(m.mun_code, m.municipio))
assert all(NOMM[k] == v for k, v in CAPITAL.items())
L19, L23 = ('PSOE', 'PP', 'VOX', 'UP', 'MP', 'CS', 'TE'), ('PP', 'PSOE', 'VOX', 'SUMAR', 'TE', 'PAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 379, 'PP': 259, 'TE': 40, 'VOX': 22, 'EMPATE': 19, 'UP': 9, 'CS': 3}, GANA[Y19]
assert GANA[Y23] == {'PP': 455, 'PSOE': 232, 'EMPATE': 23, 'SUMAR': 8, 'VOX': 7, 'TE': 5, 'PAR': 1}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, PP_PSOE, TE_PP, VOX_PP = TR('PSOE', 'PP'), TR('PP', 'PSOE'), TR('TE', 'PP'), TR('VOX', 'PP')
assert (PSOE_PP, PP_PSOE, TE_PP, VOX_PP) == (151, 13, 30, 19)
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
assert DPSOE_VOTOS == 6554 and DPP_VOTOS == 91042
assert A23['pct']['PSOE'] > A19['pct']['PSOE'] and A23['part'] > A19['part'] and A23['pct']['VOX'] < A19['pct']['VOX']
assert m[f'{Y23}_vCS'].sum() == 0
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
assert PSOE_SUBE == 338
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PSOE', 'PP')} for y in (Y19, Y23)}
assert round(POB[Y19]['PSOE'], 1) == 85.0 and round(POB[Y23]['PSOE'], 1) == 11.3 and round(POB[Y23]['PP'], 1) == 88.2
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert abs(FLS[Y23]['PSOE'] - FLS[Y19]['PSOE']) < .5 and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Teruel Existe
TE19 = m[m.g2019 == 'TE']
assert set(TE19.prov) == {'44'} and m[m.prov != '44'][f'{Y19}_vTE'].sum() == 0 and TE19.g2023.value_counts().to_dict() == {'PP': 30, 'PSOE': 6, 'EMPATE': 3, 'VOX': 1}
TE19_MED = float(TE19.poblacion.median())
TE23 = sorted(m[m.g2023 == 'TE'].municipio)
assert len(TE23) == 5 and m[m.g2023 == 'TE'].poblacion.max() < 100
TEP = {y: float(m[m.prov == '44'][f'{y}_vTE'].sum() / m[m.prov == '44'][f'{y}_val'].sum() * 100) for y in (Y19, Y23)}
assert round(TEP[Y19], 1) == 26.9 and round(TEP[Y23], 1) == 15.0

# Vox en 2019
VX19 = m[m.g2019 == 'VOX']
VXZ = sorted(VX19[VX19.poblacion >= 3000].municipio)
assert VXZ == ['Cadrete', 'Cuarte de Huerva', 'La Muela', 'La Puebla de Alfindén', 'María de Huerva', 'Villanueva de Gállego']
assert set(VX19[VX19.poblacion >= 3000].prov) == {'50'} and set(VX19[VX19.poblacion >= 3000].g2023) == {'PP'}
VX19_PROV = {pr: int((VX19.prov == pr).sum()) for pr in PROV}

# Tamaño de municipio
TAM = [('Menos de 100', 0, 100), ('De 100 a 1.000', 100, 1000), ('De 1.000 a 10.000', 1000, 10000), ('Más de 10.000', 10000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'CS', 'TE')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR', 'TE')}}
assert sum(t['n'] for t in TT.values()) == NMUN
TG = TT['Más de 10.000']
assert TG['n'] == 15 and TG['g19'] == {'PSOE': 12, 'PP': 1, 'TE': 1, 'VOX': 1} and TG['g23'] == {'PP': 14, 'PSOE': 1}, TG
G10 = m[m.poblacion >= 10000]
assert list(G10[G10.g2023 == 'PSOE'].municipio) == ['Ejea de los Caballeros'] and list(G10[G10.g2019 == 'PP'].municipio) == ['Fraga']
assert all(t['pp23'] > t['pp19'] for t in TT.values())

# Capitales
CAP = m[m.mun_code.isin(CAPITAL)].sort_values('poblacion', ascending=False)
CI = CAP.set_index('mun_code')
ZGZ, HUE, TER = CI.loc['50297'], CI.loc['22125'], CI.loc['44216']
assert (ZGZ.g2019, HUE.g2019, TER.g2019) == ('PSOE', 'PSOE', 'TE') and set(CAP.g2023) == {'PP'}
assert ZGZ.seg2023 == HUE.seg2023 == TER.seg2023 == 'PSOE'

# Provincias
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
PRIM = {y: {pr: max(PRS[pr][y]['pct'], key=PRS[pr][y]['pct'].get) for pr in PROV} for y in (Y19, Y23)}
assert PRIM[Y19] == {'50': 'PSOE', '22': 'PSOE', '44': 'TE'} and set(PRIM[Y23].values()) == {'PP'}, PRIM
assert PRN == {'50': 293, '22': 202, '44': 236}
assert PRG['22'][Y19]['PSOE'] == 129 and PRG['22'][Y23]['PP'] == 131 and PRG['50'][Y19]['PSOE'] == 175 and PRG['50'][Y23]['PP'] == 170

# Empates y municipios ajustados
UNVOTO = int((m.margv2023 == 1).sum())
UNVG = m[m.margv2023 == 1].g2023.value_counts().to_dict()
UNV_MED = float(m[m.margv2023 == 1].poblacion.median())
assert UNVOTO == 31 and UNVG == {'PSOE': 15, 'PP': 11, 'TE': 2, 'VOX': 1, 'SUMAR': 1, 'PAR': 1} and UNV_MED < 100
EMP = m[m.g2023 == 'EMPATE'].sort_values('poblacion', ascending=False)
assert EMP.iloc[0].municipio == 'Maluenda' and EMP.iloc[0].emp2023 == 'PP-PSOE' and EMP.poblacion.max() < 1000
AJG = m[(m.poblacion >= 2000) & (m.g2023 != 'EMPATE')].sort_values('marg2023').head(10)
assert list(AJG.municipio[:3]) == ['Cella', 'Calatorao', 'El Burgo de Ebro'] and int(AJG.iloc[0].margv2023) == 6 and int(AJG.iloc[1].margv2023) == 5
assert list(AJG.g2023[:2]) == ['PP', 'PP'] and list(AJG.prov[:2]) == ['44', '50']
assert list(G10[G10.g2019 == 'VOX'].municipio) == ['Cuarte de Huerva'] and list(G10[G10.g2019 == 'TE'].municipio) == ['Teruel']
JACA = AJG[AJG.municipio == 'Jaca'].iloc[0]
assert JACA.g2023 == 'PP' and JACA.g2019 == 'PSOE' and int(JACA.margv2023) == 64

# Escaños
ESC = escanos_oficiales(list(PROV))
for y in (Y19, Y23):
    ESC[y] = {pr: {SIMC.get(k, k): v for k, v in d.items()} for pr, d in ESC[y].items()}
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR', 'TE')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F5}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F5}
assert E19 == {'PP': 4, 'PSOE': 6, 'VOX': 1, 'UP': 1, 'SUMAR': 0, 'TE': 1}, E19
assert E23 == {'PP': 7, 'PSOE': 4, 'VOX': 1, 'UP': 0, 'SUMAR': 1, 'TE': 0}, E23
assert ESC['2026'] == {'50': 7, '22': 3, '44': 3}
RC = {pr: {SIMC.get(k, k): v for k, v in reparto_central(PSLUG[pr]).items()} for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F5}
assert sum(E29.values()) == 13 and set().union(*RC.values()) <= set(F5), (E29, RC)
assert E29 == {'PP': 5, 'PSOE': 4, 'VOX': 4, 'UP': 0, 'SUMAR': 0, 'TE': 0}, E29
assert all(RC[pr]['VOX'][0] >= 1 for pr in PROV) and 'TE' not in RC['44']
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=41.4, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP', 'VOX', 'TE', 'UP', 'SUMAR', 'CS', 'PAR', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}, y Teruel Existe, de {GANA[Y19]["TE"]} a {NW[GANA[Y23]["TE"]]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Aragón, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Aragón por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Aragón por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  f'votos de cada candidatura. En gris, los municipios en los que los dos primeros empataron a votos ({GANA[Y19]["EMPATE"]} en 2019 y {GANA[Y23]["EMPATE"]} en 2023).',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE se quedó igual: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos y Más País (2019) / Sumar (2023)', p(FLS[Y19]['UP'] + FLS[Y19]['MP']), p(FLS[Y23]['SUMAR'])]]))

g_tam = figura(f'En las {TG["n"]} ciudades de más de 10.000 habitantes, el PSOE pasó de ganar en {TG["g19"]["PSOE"]} a ganar en una, Ejea de los Caballeros',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'Teruel Existe 2019', 'PSOE 2023', 'PP 2023', 'PSOE 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP', 'TE')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'PP')]
                 + [p(t['psoe23']), p(t['pp23'])] for nom, t in TT.items()]))

FC = ('PP', 'PSOE', 'VOX', 'TE')
g_cap = figura('El PP ganó en las tres capitales en 2023; en 2019, ninguna',
               'Voto al PP, al PSOE, a Vox y a Teruel Existe en julio de 2023 en las tres capitales, en %. Barra clara: noviembre de 2019',
               grupos([(CAPITAL[r.mun_code], [x for f in FC for x in (((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'),) if r[f'{Y19}_v{f}'] else ()) + ((r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'),)])
                       for _, r in CAP.iterrows()], 45, 'Voto en las tres capitales', W=440, ml=80),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. En 2019, Teruel Existe solo se presentó en Teruel. Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (puntos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[CAPITAL[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], n(r.marg2023, 2)] + [p(r[f'{y}%{f}']) if r[f'{y}_v{f}'] else '—' for f in FC for y in (Y19, Y23)] for _, r in CAP.iterrows()]))

g_prov = figura(f'Teruel Existe, el más votado en Teruel en 2019, pasó del {p(TEP[Y19])} % al {p(TEP[Y23])} % en la provincia',
                'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, por provincia',
                apiladas([(f'{PROV[pr]} · {y[:4]}', [(PRG[pr][y].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if PRG[pr][y].get(f, 0)]) for pr in PROV for y in (Y19, Y23)],
                         'Municipios ganados por cada partido en cada provincia', W=440, ml=120),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in ORDG],
                (['Provincia', 'Municipios', 'Más votado nov. 2019', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Teruel Existe 2023 (%)',
                  'Municipios PSOE 2019', 'Municipios PSOE 2023', 'Municipios PP 2019', 'Municipios PP 2023'],
                 [[PROV[pr], n(PRN[pr]), NOMC[PRIM[Y19][pr]]] + [p(PRS[pr][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'VOX', 'TE')]
                  + [n(PRG[pr][y].get(f, 0)) for f in ('PSOE', 'PP') for y in (Y19, Y23)] for pr in PROV]))

g_aj = figura(f'{UNVOTO} municipios se decidieron en 2023 por un solo voto, y en {GANA[Y23]["EMPATE"]} hubo empate',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios de más de 2.000 habitantes más ajustados, en puntos',
              barras([(r.municipio, r.marg2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], max(AJG.marg2023) * 1.15,
                     'Municipios de más de 2.000 habitantes más ajustados en 2023', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in sorted(set(AJG.g2023), key=ORDG.index)],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'TE']


def hemi(lado=16, por_fila=7):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Aragón en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PP', 'PSOE', 'VOX', 'SUMAR')
g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en Aragón: uno en Huesca, uno en Teruel y dos en Zaragoza',
               'Los 13 diputados de las tres provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/zaragoza/">/encuestas/</a>) {VERSION}. El modelo no incluye a Teruel Existe, que vuelve a presentarse.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Provincia'] + [f'{NOMC[f]} 2023' for f in FT] + [f'{NOMC[f]} 29N' for f in FT[:3]],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in FT]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT[:3]]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in FT] + [str(E29[f]) for f in FT[:3]]]))
assert RC['50']['VOX'][0] == 2 and RC['22']['VOX'][0] == RC['44']['VOX'][0] == 1

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Aragón</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Aragón por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=50297">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/aragon/">datos de cada municipio de Aragón</a></div>\n</figure>\n')

# --- Texto ---
GUI = 'https://www.ondaaragonesa.com/noticias/teruel-existe-afronta-29n-objetivo-recuperar-voz-propia-madrid/20261005182703011631.html'
PSZ = 'https://www.ondaaragonesa.com/noticias/pilar-alegria-presenta-candidatura-psoe-zaragoza/20261025194546012211.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Aragón elige el 29 de noviembre 13 diputados: {ESC["2026"]["50"]} en Zaragoza y {ESC["2026"]["22"]} en Huesca y en Teruel. Teruel Existe, que tuvo diputado entre 2019 y 2023, vuelve a presentarse. Su portavoz, Tomás Guitarte, lo justificó así: «Los diputados de todos los partidos que han estado en Madrid se limitan a seguir la voz de su amo. Nosotros no tenemos amo, solo nos manda el votante de Teruel», según <a href="{GUI}">Onda Aragonesa</a>. El PSOE presentó con Pilar Alegría su lista de Zaragoza, encabezada por Fernando Beltrán, según el mismo <a href="{PSZ}">medio</a>. En Teruel, la Chunta no se presenta, como se cuenta en {L("teruel-cha-izquierda-escano-29n", "esta pieza")}.</p>
<p data-tipo="dato">El mapa municipio a municipio cambió más que el voto. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios aragoneses, el PP en {GANA[Y19]["PP"]}, Teruel Existe en {GANA[Y19]["TE"]} y Vox en {GANA[Y19]["VOX"]}; en otros {GANA[Y19]["EMPATE"]}, los dos primeros empataron a votos. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]}, el PSOE en {GANA[Y23]["PSOE"]}, Sumar en {NW[GANA[Y23]["SUMAR"]]}, Vox en {NW[GANA[Y23]["VOX"]]} y Teruel Existe en {NW[GANA[Y23]["TE"]]}, con {GANA[Y23]["EMPATE"]} empates. Y en las ciudades el vuelco fue completo: de las {TG["n"]} de más de 10.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]} en 2019 y en 2023 solo en Ejea de los Caballeros.</p>
{g_ins}
<p data-tipo="dato">El PSOE no bajó: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DPSOE_VOTOS)} votos más, y subió en {PSOE_SUBE} de los {NMUN} municipios. Pero el PP sumó {n(DPP_VOTOS)} votos y pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. En 2019, el PSOE había sido el más votado en Zaragoza y en Huesca, y Teruel Existe, en Teruel; en 2023, el PP lo fue en las tres.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP. En ellos, el PSOE se quedó casi igual, del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP pasó del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %. En sentido contrario, {PP_PSOE} municipios pasaron del PP al PSOE. Como el PSOE perdió las ciudades, los municipios que ganó pasaron de sumar el {p(POB[Y19]["PSOE"])} % de la población aragonesa al {p(POB[Y23]["PSOE"])} %; los del PP, del {p(POB[Y19]["PP"])} % al {p(POB[Y23]["PP"])} %.</p>
{g_flip}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">En 2019, de las {TG["n"]} ciudades de más de 10.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]}; el PP, solo en Fraga; Teruel Existe, en Teruel, y Vox, en Cuarte de Huerva. En 2023, el PP ganó en {TG["g23"]["PP"]} y el PSOE solo conservó Ejea de los Caballeros. En los pueblos el cambio fue menor: en los {TT["De 100 a 1.000"]["n"]} de 100 a 1.000 habitantes, el PSOE pasó de {TT["De 100 a 1.000"]["g19"]["PSOE"]} a {TT["De 100 a 1.000"]["g23"]["PSOE"]}, y el PP, de {TT["De 100 a 1.000"]["g19"]["PP"]} a {TT["De 100 a 1.000"]["g23"]["PP"]}. El PP subió en todos los tamaños de municipio.</p>
{g_tam}
<p data-tipo="dato">El PP ganó en 2023 las tres capitales, y en las tres el PSOE quedó segundo. En Zaragoza, la mayor, sacó {n(ZGZ.marg2023, 2)} puntos al PSOE; en Huesca, {n(HUE.marg2023, 2)}, y en Teruel, {n(TER.marg2023, 2)}. En 2019, Zaragoza y Huesca las había ganado el PSOE, y Teruel, Teruel Existe, con el {p(TER[f"{Y19}%TE"])} %; en 2023, Teruel Existe bajó allí al {p(TER[f"{Y23}%TE"])} %. Cómo votó Zaragoza barrio a barrio está en {L("zaragoza-barrio-a-barrio-29n", "esta pieza")}.</p>
{g_cap}
<h2>Teruel Existe y Vox</h2>
<p data-tipo="dato">En noviembre de 2019, Teruel Existe fue el más votado en {GANA[Y19]["TE"]} municipios, todos de la provincia de Teruel, y en el conjunto de la provincia, con el {p(TEP[Y19])} %. En 2023 bajó al {p(TEP[Y23])} % y ganó en {NW[GANA[Y23]["TE"]]} municipios, todos de menos de 100 habitantes. De sus {GANA[Y19]["TE"]} municipios de 2019, {TE_PP} pasaron al PP. Vox, que en 2019 ganó en {GANA[Y19]["VOX"]} municipios, entre ellos seis del entorno de Zaragoza de más de 3.000 habitantes, como Cuarte de Huerva, La Muela o María de Huerva, perdió los seis frente al PP: en total, {VOX_PP} de sus {GANA[Y19]["VOX"]} pasaron al PP.</p>
{g_prov}
<h2>Dónde se decide por un voto</h2>
<p data-tipo="dato">Con tantos pueblos pequeños, muchos municipios se deciden por casi nada. En 2023, en {UNVOTO} el primero sacó un solo voto al segundo ({UNVG["PSOE"]} para el PSOE, {UNVG["PP"]} para el PP y el resto para Teruel Existe, Vox, Sumar y el PAR), y en {GANA[Y23]["EMPATE"]} los dos primeros empataron; el mayor con empate fue Maluenda (Zaragoza), de menos de 1.000 habitantes. Entre los de más de 2.000 habitantes, los más ajustados fueron Cella (Teruel), que ganó el PP por {int(AJG.iloc[0].margv2023)} votos, y Calatorao (Zaragoza), por {int(AJG.iloc[1].margv2023)}. Jaca pasó del PSOE al PP por {int(JACA.margv2023)} votos. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 13 escaños da al PP {E29["PP"]}, {NW[E23["PP"] - E29["PP"]]} menos que en 2023; al PSOE, {E29["PSOE"]}, los mismos, y a Vox, {E29["VOX"]}, frente a {NW[E23["VOX"]]} en 2023. Sumar, que sacó uno en Zaragoza en 2023, no tendría ninguno. El modelo no incluye a Teruel Existe, que en 2023 se quedó sin escaño, así que el reparto de Teruel es más incierto.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos, de Vox o de Teruel Existe en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaban Vox y Teruel Existe encaja con que recogiera votos de los tres, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos más pequeños, unos pocos votos cambian el ganador, y el mapa de colores exagera su peso. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la comunidad desde 1977, con las autonómicas, está en {L("aragon-historia-electoral", "Aragón en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/aragon/">la ficha de Aragón</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Aragón?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %) y Teruel Existe ({p(A23["pct"]["TE"])} %). '
     f'Sacó {E23["PP"]} de los 13 diputados; el PSOE, {NW[E23["PSOE"]]}; Vox, uno, y Sumar, uno. En noviembre de 2019 el más votado había sido el PSOE.'),
    ('¿En cuántos municipios de Aragón ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}. En otros {GANA[Y23]["EMPATE"]} hubo empate a votos. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]}, el PP en {GANA[Y19]["PP"]} y Teruel Existe en {GANA[Y19]["TE"]}.'),
    ('¿Quién ganó en Zaragoza, Huesca y Teruel?',
     f'El PP, en las tres, en julio de 2023. En noviembre de 2019, el PSOE había ganado en Zaragoza y en Huesca, y Teruel Existe en Teruel.'),
    ('¿Cuántos diputados elige Aragón el 29N?',
     f'13, los mismos que en 2023: Zaragoza elige {ESC["2026"]["50"]}, y Huesca y Teruel, {ESC["2026"]["22"]} cada una.'),
    ('¿Qué dicen las encuestas en Aragón?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio. El modelo no incluye a Teruel Existe.'),
]
enlaces = (f'{L("aragon-historia-electoral", "Historia electoral de Aragón")} · <a href="{BASE}elecciones/aragon/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/zaragoza/">Encuesta en Zaragoza</a> · <a href="{BASE}encuestas/huesca/">Encuesta en Huesca</a> · <a href="{BASE}encuestas/teruel/">Encuesta en Teruel</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_aragon.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PP_PSOE': PP_PSOE, 'TE_PP': TE_PP, 'VOX_PP': VOX_PP,
    'DPSOE_VOTOS': DPSOE_VOTOS, 'DPP_VOTOS': DPP_VOTOS, 'PSOE_SUBE': PSOE_SUBE, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN, 'TEP': TEP,
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN,
    'CAP': {CAPITAL[r.mun_code]: {'g19': r.g2019, 'g23': r.g2023, 'marg23': R(r.marg2023), 'te19': R(r[f'{Y19}%TE']), 'te23': R(r[f'{Y23}%TE'])} for _, r in CAP.iterrows()},
    'UNVOTO': UNVOTO, 'UNVG': UNVG, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJG.iterrows()], 'JACA_V': int(JACA.margv2023),
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Aragón',
      f'El mapa electoral de Aragón: el PSOE ganó en {TG["g19"]["PSOE"]} de las {TG["n"]} ciudades de más de 10.000 habitantes en 2019 y solo en Ejea en 2023, aunque subió en votos',
      f'El PSOE sumó {n(DPSOE_VOTOS)} votos, pero pasó de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]} municipios, y los que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % '
      f'de la población al {p(POB[Y23]["PSOE"])} %. Teruel Existe, de {GANA[Y19]["TE"]} a {NW[GANA[Y23]["TE"]]}. Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 13 diputados, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
