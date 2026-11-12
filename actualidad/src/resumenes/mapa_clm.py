"""«El mapa electoral de Castilla-La Mancha» (2026-11), séptima pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 919 municipios de Castilla-La Mancha en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(listas por separado), el tamaño de los municipios (padrón de 2023), las cinco capitales, las provincias, Vox (65
municipios en 2019, 10 en 2023), los municipios decididos por un voto y el reparto central del modelo de /encuestas/.
Contexto: EFE vía Diario de León (García-Page, 9-10-2026) y ESdiario (Paco Núñez, 5-10-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_clm.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-castilla-la-mancha-29n'
PROV = {'02': 'Albacete', '13': 'Ciudad Real', '16': 'Cuenca', '19': 'Guadalajara', '45': 'Toledo'}
PSLUG = {'02': 'albacete', '13': 'ciudad-real', '16': 'cuenca', '19': 'guadalajara', '45': 'toledo'}
CAPITAL = {'02003': 'Albacete', '19130': 'Guadalajara', '45168': 'Toledo', '13034': 'Ciudad Real', '16078': 'Cuenca'}
CAJA = (-5.45, 37.95, -0.9, 41.35)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 919
NOMM = dict(zip(m.mun_code, m.municipio))
L19, L23 = ('PP', 'PSOE', 'VOX', 'UP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
assert m[f'{Y19}_vMP'].sum() == 0   # Más País no se presentó en Castilla-La Mancha
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 575, 'PP': 253, 'VOX': 65, 'EMPATE': 19, 'UP': 6, 'CS': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 502, 'PSOE': 384, 'EMPATE': 19, 'VOX': 10, 'SUMAR': 4}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, VOX_PP, PP_PSOE, VOX_VOX = TR('PSOE', 'PP'), TR('VOX', 'PP'), TR('PP', 'PSOE'), TR('VOX', 'VOX')
assert (PSOE_PP, VOX_PP, PP_PSOE, VOX_VOX) == (203, 50, 15, 8)
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
assert DPSOE_VOTOS == 30889 and DPP_VOTOS == 153271
assert A23['pct']['PSOE'] > A19['pct']['PSOE'] and A19['pct']['PSOE'] > A19['pct']['PP'] and A23['pct']['PP'] > A23['pct']['PSOE']
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
assert PSOE_SUBE == 476
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE', 'VOX')} for y in (Y19, Y23)}
assert round(POB[Y19]['PSOE'], 1) == 72.9 and round(POB[Y23]['PSOE'], 1) == 24.5 and round(POB[Y23]['PP'], 1) == 74.5
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Vox: los municipios que ganó en 2019
VX19 = m[m.g2019 == 'VOX']
VX19_MED = float(VX19.poblacion.median())
VXG = sorted(VX19[VX19.poblacion >= 20000].municipio)
assert VXG == ['Illescas', 'Seseña'] and VX19_MED > 1000
VX23 = m[m.g2023 == 'VOX']
VX23_MAX = VX23.sort_values('poblacion', ascending=False).iloc[0]
assert VX23_MAX.municipio == 'Pioz'
VXPROV = {pr: int((VX19.prov == pr).sum()) for pr in PROV}
assert VXPROV['19'] == 31 and VXPROV['45'] == 22

# Tamaño de municipio
TAM = [('Menos de 100', 0, 100), ('De 100 a 1.000', 100, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000),
       ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'CS')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert all(t['pp23'] > t['pp19'] and t['vox23'] < t['vox19'] for t in TT.values())
TG, T5K = TT['Más de 20.000'], TT['De 5.000 a 20.000']
assert TG['n'] == 16 and TG['g19'] == {'PSOE': 12, 'PP': 2, 'VOX': 2} and TG['g23'] == {'PP': 12, 'PSOE': 4}
assert T5K['g19']['VOX'] == 16 and T5K['g23'].get('VOX') == 1
G20 = m[m.poblacion >= 20000]
G20PSOE23 = sorted(G20[G20.g2023 == 'PSOE'].municipio)
assert G20PSOE23 == ['Alcázar de San Juan', 'Almansa', 'Azuqueca de Henares', 'Puertollano'], G20PSOE23

# Las cinco capitales
CAP = m[m.mun_code.isin(CAPITAL)].sort_values('poblacion', ascending=False)
CI = CAP.set_index('mun_code')
CAP19 = [CAPITAL[k] for k in CAP.mun_code if CI.at[k, 'g2019'] == 'PSOE']
CAP23 = [CAPITAL[k] for k in CAP.mun_code if CI.at[k, 'g2023'] == 'PSOE']
assert CAP19 == ['Albacete', 'Guadalajara', 'Toledo', 'Cuenca'] and CAP23 == [] and CI.at['13034', 'g2019'] == 'PP'
CUE, ALB = CI.loc['16078'], CI.loc['02003']
assert list(CAP.sort_values('marg2023').mun_code[:1]) == ['16078']
TAL = m[m.mun_code == '45165'].iloc[0]
assert TAL.g2019 == 'PSOE' and TAL.g2023 == 'PP'

# Provincias
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
PRIM = {y: {pr: max(PRS[pr][y]['pct'], key=PRS[pr][y]['pct'].get) for pr in PROV} for y in (Y19, Y23)}
assert all(v == 'PSOE' for v in PRIM[Y19].values()) and all(v == 'PP' for v in PRIM[Y23].values())
assert PRG['02'][Y23].get('PP') == PRG['02'][Y23].get('PSOE') == 43

# Municipios ajustados
UNVOTO = int((m.margv2023 == 1).sum())
UNV = m[m.margv2023 == 1]
UNVG = UNV.g2023.value_counts().to_dict()
UNV_MED = float(UNV.poblacion.median())
assert UNVOTO == 37 and UNVG == {'PP': 17, 'PSOE': 17, 'SUMAR': 2, 'VOX': 1} and UNV_MED < 100
MOTA = m[m.municipio == 'Mota del Cuervo'].iloc[0]
MOTA_V = int(MOTA[f'{Y23}_vPP'])
assert m[m.g2023 == 'EMPATE'].poblacion.idxmax() == MOTA.name and MOTA.g2023 == 'EMPATE' and MOTA_V == int(MOTA[f'{Y23}_vPSOE']) == 1243 and MOTA.poblacion > 6000
AJG = m[(m.poblacion >= 5000) & (m.g2023 != 'EMPATE')].sort_values('marg2023').head(10)
assert AJG.iloc[0].municipio == 'Méntrida' and int(AJG.iloc[0].margv2023) == 4

# Escaños
ESC = escanos_oficiales(list(PROV))
F3 = ('PP', 'PSOE', 'VOX')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F3}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F3}
assert E19 == {'PP': 7, 'PSOE': 9, 'VOX': 5}, E19
assert E23 == {'PP': 10, 'PSOE': 8, 'VOX': 3}, E23
assert ESC['2026'] == {'02': 4, '13': 5, '16': 3, '19': 3, '45': 6}
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F3}
assert sum(E29.values()) == 21 and set().union(*RC.values()) <= set(F3), (E29, RC)
assert E29['VOX'] > E23['VOX'] and E29['PSOE'] == E23['PSOE'] - 1, E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=39.6, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR', 'CS', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}, y Vox, de {GANA[Y19]["VOX"]} a {NW[GANA[Y23]["VOX"]]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Castilla-La Mancha, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Castilla-La Mancha por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Castilla-La Mancha por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  f'votos de cada candidatura. En gris, los municipios en los que los dos primeros empataron a votos ({GANA[Y19]["EMPATE"]} en 2019 y {GANA[Y23]["EMPATE"]} en 2023).',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COL[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COL[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
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
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'Vox 2019', 'PSOE 2023', 'PP 2023', 'Vox 2023'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP', 'VOX')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'PP', 'VOX')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PP subió en todos los tamaños de municipio, y Vox bajó en todos',
                  'Voto al PP, al PSOE y a Vox en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['vox19'], COL['VOX'], .38, 'Vox, nov. 2019'), (t['vox23'], COL['VOX'], 1, 'Vox, 2023')]) for nom, t in TT.items()],
                         50, 'Voto al PP, al PSOE y a Vox según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('Vox', COL['VOX']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox nov. 2019 (%)', 'Vox 2023 (%)', 'Cs nov. 2019 (%)', 'Sumar 2023 (%)'],
                   [[nom, p(t['pp19']), p(t['pp23']), p(t['psoe19']), p(t['psoe23']), p(t['vox19']), p(t['vox23']), p(t['cs19']), p(t['sumar23'])] for nom, t in TT.items()]))

g_cap = figura('El PSOE ganó en cuatro de las cinco capitales en 2019; en 2023, en ninguna',
               'Voto al PP y al PSOE en julio de 2023 en las cinco capitales de provincia, en %',
               grupos([(CAPITAL[r.mun_code], [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PP', 'PSOE')]) for _, r in CAP.iterrows()],
                      50, 'Voto al PP y al PSOE en las capitales en 2023', W=440, ml=100),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)'],
                [[CAPITAL[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y23}%VOX'])] for _, r in CAP.iterrows()]))

g_prov = figura('Albacete se repartió a partes iguales: 43 municipios para el PP y 43 para el PSOE',
                'Municipios ganados por cada partido en julio de 2023, por provincia',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDG if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada provincia en 2023', W=440, ml=100),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ('PSOE', 'PP', 'VOX', 'SUMAR', 'EMPATE')],
                (['Provincia', 'Municipios', 'Más votado nov. 2019', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Municipios PSOE 2019', 'Municipios PSOE 2023', 'Municipios PP 2023', 'Municipios Vox 2019'],
                 [[PROV[pr], n(PRN[pr]), NOMC[PRIM[Y19][pr]]] + [p(PRS[pr][Y23]['pct'][f]) for f in F3]
                  + [n(PRG[pr][Y19].get('PSOE', 0)), n(PRG[pr][Y23].get('PSOE', 0)), n(PRG[pr][Y23].get('PP', 0)), n(PRG[pr][Y19].get('VOX', 0))] for pr in PROV]))

g_aj = figura(f'{UNVOTO} municipios se decidieron en 2023 por un solo voto, y en {GANA[Y23]["EMPATE"]} hubo empate',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios de más de 5.000 habitantes más ajustados, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], max(AJG.marg2023) * 1.15,
                     'Municipios de más de 5.000 habitantes más ajustados en 2023', W=440, ml=170, separar=True),
              f'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador. '
              f'No incluye Mota del Cuervo, donde el PP y el PSOE empataron a {n(MOTA_V)} votos.',
              [(NOMC[f], COL[f]) for f in sorted(set(AJG.g2023), key=['PP', 'PSOE'].index)],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX']


def hemi(lado=16, por_fila=11):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Castilla-La Mancha en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en Castilla-La Mancha; el PP perdería {NW[E23["PP"] - E29["PP"]]} y el PSOE, uno',
               'Los 21 diputados de las cinco provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/toledo/">/encuestas/</a>) {VERSION}.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Provincia', 'PP 2023', 'PSOE 2023', 'Vox 2023'] + [f'{NOMC[f]} 29N' for f in F3],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in F3]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in F3]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in F3] + [str(E29[f]) for f in F3]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Castilla-La Mancha</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Castilla-La Mancha por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=45168">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/castilla-la-mancha/">datos de cada municipio de Castilla-La Mancha</a></div>\n</figure>\n')

# --- Texto ---
PAGE = 'https://www.diariodeleon.es/nacional/261009/2099769/page-admite-mala-relacion-sanchez-dice-psoe-dirigen.html'
NUN = 'https://www.esdiario.com/nacional/261005/199495/nunez-cuestiona-rivalidad-page-sanchez-le-pide-decida-campana-electoral.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Castilla-La Mancha elige el 29 de noviembre 21 diputados: {ESC["2026"]["45"]} en Toledo, {ESC["2026"]["13"]} en Ciudad Real, {ESC["2026"]["02"]} en Albacete y {ESC["2026"]["16"]} en Cuenca y en Guadalajara. Su presidente, el socialista Emiliano García-Page, admitió en octubre que sus relaciones con Pedro Sánchez «objetivamente son muy malas» y defendió, en una entrevista recogida por EFE: «No me he escondido nunca. Soy del Partido Socialista. Es más, creo que soy más del Partido Socialista que algunos que lo dirigen». Sobre el 29N en la comunidad, dijo que «lo más que puede estar en juego es perder un diputado», según <a href="{PAGE}">EFE</a>. El presidente del PP regional, Paco Núñez, le pidió que eligiera en campaña: «hay dos opciones, o el PSOE o España: no hay más», según <a href="{NUN}">ESdiario</a>.</p>
<p data-tipo="dato">El mapa municipio a municipio cambió más que el voto. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios, el PP en {GANA[Y19]["PP"]} y Vox en {GANA[Y19]["VOX"]}; en otros {GANA[Y19]["EMPATE"]}, los dos primeros empataron a votos. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]}, el PSOE en {GANA[Y23]["PSOE"]} y Vox en {NW[GANA[Y23]["VOX"]]}, con {GANA[Y23]["EMPATE"]} empates. Y en las ciudades el vuelco fue completo: el PSOE ganó en 2019 en cuatro de las cinco capitales, todas menos Ciudad Real, y en 2023 en ninguna.</p>
{g_ins}
<p data-tipo="dato">El PSOE no bajó: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DPSOE_VOTOS)} votos más, y subió en {PSOE_SUBE} de los {NMUN} municipios. Pero el PP sumó {n(DPP_VOTOS)} votos y pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. En 2019, el PSOE había sido el más votado en las cinco provincias; en 2023, lo fue el PP.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP. En ellos, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP lo hizo del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %. En sentido contrario, {PP_PSOE} municipios pasaron del PP al PSOE. Como el PSOE perdió sobre todo ciudades, los municipios que ganó pasaron de sumar el {p(POB[Y19]["PSOE"])} % de la población de la comunidad al {p(POB[Y23]["PSOE"])} %.</p>
{g_flip}
<h2>Vox: de 65 municipios a diez</h2>
<p data-tipo="dato">En noviembre de 2019, Vox fue el más votado en {GANA[Y19]["VOX"]} municipios de Castilla-La Mancha, {VXPROV["19"]} en Guadalajara y {VXPROV["45"]} en Toledo, y entre ellos dos de más de 20.000 habitantes, Illescas y Seseña. No eran pueblos pequeños: la mitad tenía más de {n(VX19_MED)} habitantes. En 2023, {VOX_PP} de esos {GANA[Y19]["VOX"]} pasaron al PP y Vox solo conservó {NW[VOX_VOX]}. Ganó en {NW[GANA[Y23]["VOX"]]} en total; el mayor, Pioz (Guadalajara), con {n(VX23_MAX.poblacion)} habitantes.</p>
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">En los {TG["n"]} municipios de más de 20.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]} en 2019 y en {NW[TG["g23"]["PSOE"]]} en 2023: Puertollano, Azuqueca de Henares, Alcázar de San Juan y Almansa. En los de 5.000 a 20.000, Vox había ganado en {T5K["g19"]["VOX"]} en 2019 y en 2023 en {NW[T5K["g23"]["VOX"]]}. El PP subió en todos los tamaños de municipio, y Vox bajó en todos.</p>
{g_tam}
{g_tampct}
<p data-tipo="dato">En las capitales, la más ajustada de 2023 fue Cuenca, que ganó el PP por {p(CUE.marg2023)} puntos, con el {p(CUE[f"{Y23}%PP"])} % frente al {p(CUE[f"{Y23}%PSOE"])} % del PSOE. En Albacete, la mayor, el PP sacó el {p(ALB[f"{Y23}%PP"])} % y el PSOE el {p(ALB[f"{Y23}%PSOE"])} %; en 2019 había ganado el PSOE, con el {p(ALB[f"{Y19}%PSOE"])} %. Talavera de la Reina, la segunda ciudad de la provincia de Toledo, también pasó del PSOE al PP.</p>
{g_cap}
<h2>Cinco provincias</h2>
<p data-tipo="dato">En 2023, el PP fue el más votado en las cinco provincias, pero en número de municipios el reparto fue más igualado: en Albacete, el PP y el PSOE ganaron en {PRG["02"][Y23]["PP"]} cada uno; en Ciudad Real, el PP en {PRG["13"][Y23]["PP"]} y el PSOE en {PRG["13"][Y23]["PSOE"]}. En Guadalajara, la provincia con más municipios ({PRN["19"]}), el PP ganó en {PRG["19"][Y23]["PP"]} y el PSOE en {PRG["19"][Y23]["PSOE"]}.</p>
{g_prov}
<h2>Dónde se decide por un voto</h2>
<p data-tipo="dato">Con tantos pueblos pequeños, muchos municipios se deciden por casi nada. En 2023, en {UNVOTO} el primero sacó un solo voto al segundo ({UNVG["PP"]} para el PP, {UNVG["PSOE"]} para el PSOE, {NW[UNVG["SUMAR"]]} para Sumar y {NW[UNVG["VOX"]]} para Vox), y en {GANA[Y23]["EMPATE"]} los dos primeros empataron. El municipio más grande con empate fue Mota del Cuervo (Cuenca), de más de 6.000 habitantes: {n(MOTA_V)} votos para el PP y {n(MOTA_V)} para el PSOE. Entre los de más de 5.000 habitantes con ganador, el más ajustado fue Méntrida (Toledo), que ganó el PP por {int(AJG.iloc[0].margv2023)} votos. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 21 escaños da al PP {E29["PP"]}, {NW[E23["PP"] - E29["PP"]]} menos que en 2023; al PSOE, {E29["PSOE"]}, uno menos, y a Vox, {E29["VOX"]}, el doble que los {NW[E23["VOX"]]} de 2023. El PP es el más votado en la mayoría de las simulaciones en las cinco provincias.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos más pequeños, unos pocos votos cambian el ganador, y el mapa de colores exagera su peso. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la comunidad desde 1977, con las autonómicas, está en {L("castilla-la-mancha-historia-electoral", "Castilla-La Mancha en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/castilla-la-mancha/">la ficha de Castilla-La Mancha</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Castilla-La Mancha?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     f'Sacó {E23["PP"]} de los 21 diputados; el PSOE, {E23["PSOE"]}, y Vox, {NW[E23["VOX"]]}. En noviembre de 2019 el más votado había sido el PSOE.'),
    ('¿En cuántos municipios de Castilla-La Mancha ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}; Vox, en {NW[GANA[Y23]["VOX"]]}, y Sumar, en {NW[GANA[Y23]["SUMAR"]]}. En otros {GANA[Y23]["EMPATE"]} hubo empate a votos. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]}, el PP en {GANA[Y19]["PP"]} y Vox en {GANA[Y19]["VOX"]}.'),
    ('¿En qué capitales ganó el PSOE?',
     'En noviembre de 2019, en cuatro de las cinco: Albacete, Guadalajara, Toledo y Cuenca; Ciudad Real la ganó el PP. En julio de 2023, el PP ganó en las cinco.'),
    ('¿Cuántos diputados elige Castilla-La Mancha el 29N?',
     f'21, los mismos que en 2023: Toledo elige {ESC["2026"]["45"]}; Ciudad Real, {ESC["2026"]["13"]}; Albacete, {ESC["2026"]["02"]}, y Cuenca y Guadalajara, {ESC["2026"]["16"]} cada una.'),
    ('¿Qué dicen las encuestas en Castilla-La Mancha?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("castilla-la-mancha-historia-electoral", "Historia electoral de Castilla-La Mancha")} · <a href="{BASE}elecciones/castilla-la-mancha/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/toledo/">Encuesta en Toledo</a> · <a href="{BASE}encuestas/ciudad-real/">Encuesta en Ciudad Real</a> · '
           f'<a href="{BASE}encuestas/albacete/">Encuesta en Albacete</a> · <a href="{BASE}encuestas/guadalajara/">Encuesta en Guadalajara</a> · <a href="{BASE}encuestas/cuenca/">Encuesta en Cuenca</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_clm.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'VOX_PP': VOX_PP, 'PP_PSOE': PP_PSOE, 'VOX_VOX': VOX_VOX,
    'DPSOE_VOTOS': DPSOE_VOTOS, 'DPP_VOTOS': DPP_VOTOS, 'PSOE_SUBE': PSOE_SUBE, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'VX19_MED': VX19_MED, 'VXPROV': VXPROV, 'VX23_MAX': int(VX23_MAX.poblacion),
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN,
    'CAP': {CAPITAL[r.mun_code]: {'g19': r.g2019, 'g23': r.g2023, 'pp19': R(r[f'{Y19}%PP']), 'pp23': R(r[f'{Y23}%PP']), 'psoe19': R(r[f'{Y19}%PSOE']),
                                  'psoe23': R(r[f'{Y23}%PSOE']), 'marg23': R(r.marg2023)} for _, r in CAP.iterrows()},
    'NCAP19': len(CAP19), 'NCAP23': len(CAP23),
    'UNVOTO': UNVOTO, 'UNVG': UNVG, 'MOTA_V': MOTA_V, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJG.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Castilla-La Mancha',
      'El mapa electoral de Castilla-La Mancha: el PSOE ganó en cuatro de las cinco capitales en 2019 y en ninguna en 2023, aunque subió en votos',
      f'El PSOE sumó {n(DPSOE_VOTOS)} votos, pero pasó de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]} municipios, y los que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % '
      f'de la población al {p(POB[Y23]["PSOE"])} %. Vox, de {GANA[Y19]["VOX"]} a {NW[GANA[Y23]["VOX"]]}. Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 21 diputados, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'E29', E29, 'FLS', FLS, 'VX19_MED', VX19_MED, 'AJG', [(r.municipio, round(r.marg2023, 2), int(r.margv2023), r.g2023) for _, r in AJG.iterrows()])
