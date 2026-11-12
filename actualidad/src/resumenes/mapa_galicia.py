"""«El mapa electoral de Galicia» (2026-11), sexta pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 313 municipios de Galicia en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas
por separado: en 2019, Unidas Podemos y Más País), el tamaño de los municipios (padrón de 2023), las siete ciudades, las
cuatro provincias, el BNG, los municipios más ajustados y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: El Español (Quincemil, 12-11-2026), ESdiario (Rueda, 5-10-2026) y Moncloa.com (listas del BNG, 25-10-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_galicia.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-galicia-29n'
PROV = {'15': 'A Coruña', '27': 'Lugo', '32': 'Ourense', '36': 'Pontevedra'}
PSLUG = {'15': 'a-coruna', '27': 'lugo', '32': 'ourense', '36': 'pontevedra'}
# Las siete ciudades: las cuatro capitales, Vigo, Santiago de Compostela y Ferrol
CIUDAD = {'36057': 'Vigo', '15030': 'A Coruña', '32054': 'Ourense', '27028': 'Lugo', '15078': 'Santiago de Compostela',
          '36038': 'Pontevedra', '15036': 'Ferrol'}
CAJA = (-9.35, 41.8, -6.7, 43.8)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 313
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['15030'] == 'A Coruña' and NOMM['36057'] == 'Vigo' and NOMM['15078'] == 'Santiago de Compostela'
L19, L23 = ('PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS', 'BNG'), ('PP', 'PSOE', 'VOX', 'SUMAR', 'BNG')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PP': 229, 'PSOE': 83, 'BNG': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 298, 'PSOE': 15}, GANA[Y23]   # sin empates a votos en ninguna de las dos
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, PSOE_PSOE, PP_PP = TR('PSOE', 'PP'), TR('PSOE', 'PSOE'), TR('PP', 'PP')
assert (PSOE_PP, PSOE_PSOE, PP_PP) == (68, 15, 229)   # ningún municipio pasó del PP al PSOE
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
assert DPSOE_VOTOS == 19392 and DPP_VOTOS == 229532
assert A23['pct']['PSOE'] < A19['pct']['PSOE'] and A23['part'] > A19['part'] and A23['pct']['VOX'] < A19['pct']['VOX']
# Población de los municipios que ganó cada partido (padrón de 2023)
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert round(POB[Y19]['PSOE'], 1) == 60.9 and round(POB[Y23]['PSOE'], 1) == 13.0
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10 and abs(FLS[Y23]['PSOE'] - FLS[Y19]['PSOE']) < 3, FLS

# Tamaño de municipio (población del padrón de 2023)
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000), ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'BNG')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR', 'BNG')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert all(t['pp23'] > t['pp19'] and t['vox23'] < t['vox19'] and t['psoe23'] < t['psoe19'] for t in TT.values())
TG = TT['Más de 20.000']
assert TG['n'] == 22 and TG['g19'] == {'PSOE': 18, 'PP': 4} and TG['g23'] == {'PP': 20, 'PSOE': 2}
G20 = m[m.poblacion >= 20000]
G20PSOE23 = sorted(G20[G20.g2023 == 'PSOE'].municipio)
assert G20PSOE23 == ['Redondela', 'Vigo'], G20PSOE23
G20PP19 = sorted(G20[G20.g2019 == 'PP'].municipio)
assert G20PP19 == ['A Estrada', 'Marín', 'Ribeira', 'Santiago de Compostela'], G20PP19
T1K = TT['Menos de 1.000']

# Las siete ciudades
CIU = m[m.mun_code.isin(CIUDAD)].sort_values('poblacion', ascending=False)
CI = CIU.set_index('mun_code')
CIU19 = [CIUDAD[k] for k in CIU.mun_code if CI.at[k, 'g2019'] == 'PSOE']
CIU23 = [CIUDAD[k] for k in CIU.mun_code if CI.at[k, 'g2023'] == 'PSOE']
assert len(CIU19) == 6 and CI.at['15078', 'g2019'] == 'PP' and CIU23 == ['Vigo'], (CIU19, CIU23)
VIG, COR, SCQ = CI.loc['36057'], CI.loc['15030'], CI.loc['15078']
assert VIG[f'{Y23}%PSOE'] > VIG[f'{Y23}%PP'] and COR.g2019 == 'PSOE' and COR.g2023 == 'PP'
CIUP = float(CIU.poblacion.sum() / m.poblacion.sum() * 100)
assert 35 < CIUP < 38, CIUP

# El BNG
BNG19 = m[m.g2019 == 'BNG'].iloc[0]
assert BNG19.municipio == 'Allariz' and BNG19.g2023 == 'PP'
ALL = {'bng19': float(BNG19[f'{Y19}%BNG']), 'bng23': float(BNG19[f'{Y23}%BNG']), 'pp23': float(BNG19[f'{Y23}%PP'])}
assert round(ALL['bng19'], 1) == 31.6 and round(ALL['bng23'], 1) == 25.0
BTOP = m.sort_values(f'{Y23}%BNG', ascending=False).head(10)
assert BTOP.iloc[0].municipio == 'Vilar de Santos' and (BTOP.g2023 == 'PP').sum() + (BTOP.g2023 == 'PSOE').sum() == 10
BSEG23 = int((m.seg2023 == 'BNG').sum())
BNG_SUBE = int((m[f'{Y23}%BNG'] > m[f'{Y19}%BNG']).sum())
assert BSEG23 == 3

# Provincias
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
PRIM = {y: {pr: max(PRS[pr][y]['pct'], key=PRS[pr][y]['pct'].get) for pr in PROV} for y in (Y19, Y23)}
assert all(v == 'PP' for v in PRIM[Y23].values())
P19PSOE = [PROV[pr] for pr in PROV if PRIM[Y19][pr] == 'PSOE']
assert P19PSOE == ['Pontevedra'], P19PSOE
P23PSOE = {PROV[pr]: PRG[pr][Y23].get('PSOE', 0) for pr in PROV}

# Municipios ajustados (2023)
UNVOTO = int((m.margv2023 == 1).sum())
AJ2 = int((m.marg2023 < 2).sum())
assert UNVOTO == 0 and AJ2 == 5
AJ = m.sort_values('marg2023').head(10)
assert list(AJ.municipio[:3]) == ['As Pontes de García Rodríguez', 'A Fonsagrada', 'Parada de Sil']
assert list(AJ.margv2023[:3]) == [22, 9, 2]

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(list(PROV))
F19, F23 = ('PP', 'PSOE', 'UP', 'BNG'), ('PP', 'PSOE', 'SUMAR', 'BNG')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F19}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F23}
assert E19 == {'PP': 10, 'PSOE': 10, 'UP': 2, 'BNG': 1}, E19
assert E23 == {'PP': 13, 'PSOE': 7, 'SUMAR': 2, 'BNG': 1}, E23
assert ESC['2026'] == {'15': 8, '27': 4, '32': 4, '36': 7}
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
FT = ('PP', 'PSOE', 'BNG', 'VOX', 'SUMAR')
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in FT}
assert sum(E29.values()) == 23 and set().union(*RC.values()) <= set(FT), (E29, RC)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'
P1 = {pr: {l['lista']: l['p_primera'] for l in MOD['provincias'][pr]['listas']} for pr in PROV}
assert all(max(P1[pr], key=P1[pr].get) == 'PP' for pr in PROV)

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=42.8, umbral=1.2)
assert len(cam) == NMUN
ORDG = ['PP', 'PSOE', 'BNG']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios gallegos a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Galicia, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Galicia por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Galicia por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura (en 2019, Unidas Podemos y Más País por separado). No hubo empates a votos en ningún municipio.',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

FF = ('PP', 'PSOE', 'VOX', 'CS', 'BNG')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE apenas bajó: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox, a Ciudadanos y al BNG en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COL[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COL[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       50, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]))

g_tam = figura(f'En los municipios de más de 20.000 habitantes, el PSOE pasó de ganar en {TG["g19"]["PSOE"]} de {TG["n"]} a ganar en {NW[TG["g23"]["PSOE"]]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COL[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PP 2019', 'PSOE 2019', 'PP 2023', 'PSOE 2023'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PP', 'PSOE')] + [n(t['g23'].get(f, 0)) for f in ('PP', 'PSOE')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PP subió en todos los tamaños de municipio; el PSOE y Vox bajaron en todos',
                  'Voto al PP, al PSOE y al BNG en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['bng19'], COL['BNG'], .38, 'BNG, nov. 2019'), (t['bng23'], COL['BNG'], 1, 'BNG, 2023')]) for nom, t in TT.items()],
                         60, 'Voto al PP, al PSOE y al BNG según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('BNG', COL['BNG']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'BNG nov. 2019 (%)', 'BNG 2023 (%)', 'Vox nov. 2019 (%)', 'Vox 2023 (%)', 'Sumar 2023 (%)'],
                   [[nom, p(t['pp19']), p(t['pp23']), p(t['psoe19']), p(t['psoe23']), p(t['bng19']), p(t['bng23']), p(t['vox19']), p(t['vox23']), p(t['sumar23'])] for nom, t in TT.items()]))

g_ciu = figura('El PSOE ganó en seis de las siete ciudades gallegas en 2019; en 2023, solo en Vigo',
               'Voto al PP y al PSOE en julio de 2023 en las siete ciudades de Galicia, en %',
               grupos([(CIUDAD[r.mun_code], [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PP', 'PSOE')]) for _, r in CIU.iterrows()],
                      55, 'Voto al PP y al PSOE en las siete ciudades en 2023', W=440, ml=150),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Ciudad', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Sumar 2023 (%)', 'BNG 2023 (%)'],
                [[CIUDAD[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y23}%SUMAR']), p(r[f'{Y23}%BNG'])] for _, r in CIU.iterrows()]))

g_bng = figura(f'El BNG pasó del {p(A19["pct"]["BNG"])} % al {p(A23["pct"]["BNG"])} % y no ganó en ningún municipio en 2023',
               'Los diez municipios con más voto al BNG en julio de 2023, en %',
               barras([(r.municipio, r[f'{Y23}%BNG'], COL['BNG'], p(r[f'{Y23}%BNG'])) for _, r in BTOP.iterrows()], 40,
                      'Municipios con más voto al BNG en 2023', W=440, ml=160),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('BNG', COL['BNG'])],
               (['Municipio', 'Provincia', 'BNG nov. 2019 (%)', 'BNG 2023 (%)', 'Ganó en 2023'],
                [[r.municipio, PROV[r.prov], p(r[f'{Y19}%BNG']), p(r[f'{Y23}%BNG']), NOMC[r.g2023]] for _, r in BTOP.iterrows()]))

g_prov = figura('El PP ganó en número de municipios en las cuatro provincias, también en 2019',
                'Municipios ganados por cada partido en julio de 2023, por provincia',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDG if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada provincia en 2023', W=440, ml=100),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ('PP', 'PSOE')],
                (['Provincia', 'Municipios', 'Más votado nov. 2019', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Sumar 2023 (%)', 'BNG 2023 (%)', 'Vox 2023 (%)', 'Municipios PP 2023', 'Municipios PSOE 2023'],
                 [[PROV[pr], n(PRN[pr]), NOMC[PRIM[Y19][pr]]] + [p(PRS[pr][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'SUMAR', 'BNG', 'VOX')]
                  + [n(PRG[pr][Y23].get(f, 0)) for f in ('PP', 'PSOE')] for pr in PROV]))
assert all(max(PRG[pr][y], key=PRG[pr][y].get) == 'PP' for pr in PROV for y in (Y19, Y23))

g_aj = figura(f'As Pontes se decidió por {int(AJ.iloc[0].margv2023)} votos; Parada de Sil, por {int(AJ.iloc[2].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios más ajustados, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJ.iterrows()], max(AJ.marg2023) * 1.15,
                     'Municipios más ajustados en 2023', W=440, ml=190, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in sorted(set(AJ.g2023), key=['PP', 'PSOE'].index)],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'UP', 'SUMAR', 'BNG', 'PP', 'VOX']


def hemi(lado=16, por_fila=12):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Galicia en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, el BNG pasaría de {NW[E23["BNG"]]} a {NW[E29["BNG"]]} diputados en Galicia, y Sumar se quedaría sin ninguno',
               'Los 23 diputados de las cuatro provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/a-coruna/">/encuestas/</a>) {VERSION}. En 2019, Unidas Podemos (En Común); en 2023, Sumar.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Provincia', 'PP 2023', 'PSOE 2023', 'Sumar 2023', 'BNG 2023'] + [f'{NOMC[f]} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in F23]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in F23] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Galicia</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Galicia por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=15078">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/galicia/">datos de cada municipio de Galicia</a></div>\n</figure>\n')

# --- Texto ---
QUIN = 'https://www.elespanol.com/quincemil/actualidad/galicia/20261112/campana-arranca-viernes-galicia-semana-marcada-huelga-general/1003744450971_0.html'
RUE = 'https://www.esdiario.com/galicia/261005/199513/rueda-senala-interes-personal-sanchez-convocar-elecciones-destapa-motivo-ve-detras-movimiento.html'
BNGL = 'https://www.moncloa.com/2026/10/25/bng-listas-29n-olalla-rodil-lugo-3455123/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
T20 = TT['De 5.000 a 20.000']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Galicia elige el 29 de noviembre 23 diputados: {ESC["2026"]["15"]} en A Coruña, {ESC["2026"]["36"]} en Pontevedra y {ESC["2026"]["27"]} en Lugo y en Ourense. La campaña empieza el viernes 13. El presidente de la Xunta, Alfonso Rueda, había recibido el adelanto electoral atribuyéndolo al «interés personal» de Pedro Sánchez: «No podíamos seguir así», dijo tras el Consello da Xunta, según <a href="{RUE}">ESdiario</a>. El PP gallego lleva a Miguel Tellado de cabeza de lista por A Coruña, según <a href="{QUIN}">El Español</a>. El BNG repite con Néstor Rego, su único diputado en el Congreso, y su portavoz nacional, Ana Pontón, presentó las listas con un lema: «Cuanto más fuerte sea el BNG, más fuerte será Galicia», según <a href="{BNGL}">Moncloa.com</a>.</p>
<p data-tipo="dato">El mapa municipio a municipio cambió mucho entre 2019 y 2023. En noviembre de 2019, el PP fue el partido más votado en {GANA[Y19]["PP"]} de los {NMUN} municipios gallegos, el PSOE en {GANA[Y19]["PSOE"]} y el BNG en uno, Allariz. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]} y el PSOE en {GANA[Y23]["PSOE"]}. Ningún municipio pasó del PP al PSOE. El cambio que más pesa es el de las ciudades: el PSOE ganó en 2019 en seis de las siete, todas menos Santiago de Compostela, y en 2023 solo en Vigo.</p>
{g_ins}
<p data-tipo="dato">El PSOE no perdió votos: sumó {n(DPSOE_VOTOS)} más que en 2019, aunque bajó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} % porque votó más gente: la participación subió del {p(A19["part"])} % al {p(A23["part"])} %. El PP sumó {n(DPP_VOTOS)} votos y pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. En 2019 el PSOE había sido el más votado en la provincia de Pontevedra; en 2023, el PP fue el primero en las cuatro.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP. En ellos, el PSOE se quedó casi igual, del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, y el PP subió del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %. Como el PSOE perdió sobre todo ciudades y villas grandes, los municipios que ganó pasaron de sumar el {p(POB[Y19]["PSOE"])} % de la población de Galicia al {p(POB[Y23]["PSOE"])} %.</p>
{g_flip}
<h2>Las ciudades y las villas</h2>
<p data-tipo="patron">En los {TG["n"]} municipios de más de 20.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]} en 2019 y en {NW[TG["g23"]["PSOE"]]} en 2023, Vigo y Redondela. En 2019, el PP solo había ganado en cuatro de ellos: Santiago de Compostela, Ribeira, Marín y A Estrada. En los de 5.000 a 20.000, el PSOE pasó de {T20["g19"]["PSOE"]} a {NW[T20["g23"]["PSOE"]]}, O Grove. En los de menos de 1.000 habitantes, que son {T1K["n"]}, el PP ya ganaba en {T1K["g19"]["PP"]} en 2019 y en {T1K["g23"]["PP"]} en 2023. El PP subió en todos los tamaños de municipio, y el PSOE y Vox bajaron en todos.</p>
{g_tam}
{g_tampct}
<p data-tipo="dato">Las siete ciudades reúnen el {p(CIUP)} % de la población gallega. En Vigo, la mayor, el PSOE sacó el {p(VIG[f"{Y23}%PSOE"])} % y el PP el {p(VIG[f"{Y23}%PP"])} %. En A Coruña, que el PSOE había ganado en 2019 con el {p(COR[f"{Y19}%PSOE"])} %, el PP fue el primero en 2023 con el {p(COR[f"{Y23}%PP"])} %, por delante del PSOE ({p(COR[f"{Y23}%PSOE"])} %). Santiago fue la única que el PP ya ganaba en 2019, y en 2023 lo hizo con el {p(SCQ[f"{Y23}%PP"])} %; allí el BNG sacó el {p(SCQ[f"{Y23}%BNG"])} %, su mejor resultado en una ciudad.</p>
{g_ciu}
<h2>El BNG: más votos y ningún municipio</h2>
<p data-tipo="dato">El BNG subió del {p(A19["pct"]["BNG"])} % al {p(A23["pct"]["BNG"])} % en Galicia, y lo hizo en {BNG_SUBE} de los {NMUN} municipios, pero no fue el más votado en ninguno en 2023. En 2019 había ganado en Allariz (Ourense), con el {p(ALL["bng19"])} %; en 2023 sacó allí el {p(ALL["bng23"])} % y ganó el PP, con el {p(ALL["pp23"])} %. Su mejor resultado de 2023 fue en Vilar de Santos, también en Ourense, con el {p(BTOP.iloc[0][f"{Y23}%BNG"])} %, y solo fue segundo en {NW[BSEG23]} municipios. Mantuvo su único escaño, por A Coruña.</p>
{g_bng}
<p data-tipo="contexto">La historia electoral de Galicia desde 1977, con las autonómicas, en las que el BNG pesa mucho más, está en {L("galicia-historia-electoral", "Galicia en las urnas")}.</p>
<h2>Cuatro provincias</h2>
<p data-tipo="dato">El PP ganó en número de municipios en las cuatro provincias, ya en 2019. En 2023, el PSOE solo ganó en {P23PSOE["Pontevedra"]} municipios de Pontevedra, {P23PSOE["Ourense"]} de Ourense, {P23PSOE["Lugo"]} de Lugo y {P23PSOE["A Coruña"]} de A Coruña. La provincia de Pontevedra, la única que el PSOE había ganado en 2019, la ganó el PP en 2023 con el {p(PRS["36"][Y23]["pct"]["PP"])} %, frente al {p(PRS["36"][Y23]["pct"]["PSOE"])} % del PSOE.</p>
{g_prov}
<h2>Dónde se decide por pocos votos</h2>
<p data-tipo="dato">En 2023 no hubo empates ni municipios decididos por un voto, y solo en {NW[AJ2]} la ventaja fue de menos de dos puntos. El más ajustado fue {AJ.iloc[0].municipio}, que ganó el PP por {int(AJ.iloc[0].margv2023)} votos; después, A Fonsagrada, que ganó el PSOE por {int(AJ.iloc[1].margv2023)}, y Parada de Sil, también para el PSOE, por {int(AJ.iloc[2].margv2023)}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 23 escaños da al PP {E29["PP"]}, uno más que en 2023; al PSOE, {E29["PSOE"]}, {NW[E23["PSOE"] - E29["PSOE"]]} menos; al BNG, {NW[E29["BNG"]]}, uno en A Coruña y otro en Pontevedra, y a Vox, {NW[E29["VOX"]]}, por A Coruña. Sumar, que sacó {NW[E23["SUMAR"]]} en 2023, se quedaría sin ninguno en el reparto central. El PP es el más votado en la mayoría de las simulaciones en las cuatro provincias. Vox no ha tenido nunca diputado por Galicia: lo contamos en {L("vox-galicia-coruna-abascal-29n", "esta pieza")}.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox, mientras el PSOE mantenía sus votos, encaja con que el PP recogiera votos de los dos y de quienes no habían votado en 2019, pero el mapa no permite separarlo. En los municipios pequeños, unos pocos votos cambian el ganador, y el mapa de colores exagera su peso. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/galicia/">la ficha de Galicia</a>. Los pueblos donde el PP saca más del 80 % están en {L("pp-cinco-pueblos-galicia", "Los 5 pueblos de España donde el PP saca hasta el 81,5 %")}.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Galicia?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %), el BNG ({p(A23["pct"]["BNG"])} %) y Vox ({p(A23["pct"]["VOX"])} %). '
     f'Sacó {E23["PP"]} de los 23 diputados; el PSOE, {E23["PSOE"]}; Sumar, {NW[E23["SUMAR"]]}, y el BNG, {NW[E23["BNG"]]}. El PP fue el más votado en las cuatro provincias.'),
    ('¿En cuántos municipios de Galicia ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}, entre ellos Vigo y Redondela; el PP, en los otros {GANA[Y23]["PP"]}. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]}, el PP en {GANA[Y19]["PP"]} y el BNG en uno, Allariz.'),
    ('¿En qué ciudades gallegas ganó el PSOE?',
     'En noviembre de 2019, en seis de las siete: Vigo, A Coruña, Ourense, Lugo, Pontevedra y Ferrol; Santiago de Compostela la ganó el PP. En julio de 2023, el PSOE solo ganó en Vigo.'),
    ('¿Cuántos diputados elige Galicia el 29N?',
     f'23, los mismos que en 2023: A Coruña elige {ESC["2026"]["15"]}; Pontevedra, {ESC["2026"]["36"]}, y Lugo y Ourense, {ESC["2026"]["27"]} cada una.'),
    ('¿Qué dicen las encuestas en Galicia?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]}, al BNG {E29["BNG"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("galicia-historia-electoral", "Historia electoral de Galicia")} · <a href="{BASE}elecciones/galicia/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/a-coruna/">Encuesta en A Coruña</a> · <a href="{BASE}encuestas/pontevedra/">Encuesta en Pontevedra</a> · '
           f'<a href="{BASE}encuestas/lugo/">Encuesta en Lugo</a> · <a href="{BASE}encuestas/ourense/">Encuesta en Ourense</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_galicia.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PSOE_PSOE': PSOE_PSOE, 'PP_PP': PP_PP,
    'DPSOE_VOTOS': DPSOE_VOTOS, 'DPP_VOTOS': DPP_VOTOS, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN, 'P23PSOE': P23PSOE,
    'CIU': {CIUDAD[r.mun_code]: {'g19': r.g2019, 'g23': r.g2023, 'pp19': R(r[f'{Y19}%PP']), 'pp23': R(r[f'{Y23}%PP']), 'psoe19': R(r[f'{Y19}%PSOE']),
                                 'psoe23': R(r[f'{Y23}%PSOE']), 'bng23': R(r[f'{Y23}%BNG']), 'marg23': R(r.marg2023)} for _, r in CIU.iterrows()},
    'NCIU19': len(CIU19), 'NCIU23': len(CIU23), 'CIUP': CIUP,
    'ALL': ALL, 'BTOP': [[r.municipio, R(r[f'{Y23}%BNG'])] for _, r in BTOP.iterrows()], 'BSEG23': BSEG23, 'BNG_SUBE': BNG_SUBE,
    'UNVOTO': UNVOTO, 'AJ2': AJ2, 'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC, 'P1': {pr: P1[pr].get('PP') for pr in PROV},
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Galicia',
      f'El mapa electoral de Galicia: el PSOE ganó en {TG["g19"]["PSOE"]} de las {TG["n"]} ciudades y villas de más de 20.000 habitantes en 2019 y solo en {NW[TG["g23"]["PSOE"]]} en 2023',
      f'El PSOE sumó {n(DPSOE_VOTOS)} votos, pero pasó de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]} municipios, y los que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % '
      f'de la población al {p(POB[Y23]["PSOE"])} %. Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 23 diputados y al BNG {NW[E29["BNG"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'E29', E29, 'POB', POB, 'AJ', [(r.municipio, round(r.marg2023, 2), int(r.margv2023), r.g2023) for _, r in AJ.iterrows()],
      'TT', {k: (v['g19'], v['g23']) for k, v in TT.items()}, 'P23PSOE', P23PSOE, 'BNG_SUBE', BNG_SUBE, 'FLS', FLS)
