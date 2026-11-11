"""«El mapa electoral de la Comunitat Valenciana» (11-11-2026), cuarta pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 542 municipios valencianos en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas por
separado: en 2019, Unidas Podemos y Más Compromís), el cambio del PSOE y del PP, el tamaño de los municipios (padrón de 2023,
INE vía ineAtlas), las cuatro ciudades de más de 100.000 habitantes, las provincias, los municipios más ajustados y el reparto
central del modelo de /encuestas/ para el 29N. Contexto: EFE (11-11-2026). El reparto de escaños por provincia, con detalle,
está en comunitat-valenciana-escanos-29n (comunitat_valenciana.py); aquí solo se resume.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_valencia.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, s1, trazados)

A = BASE + 'actualidad/'
NW = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-comunitat-valenciana-29n'
PROV = {'46': 'Valencia', '03': 'Alicante', '12': 'Castellón'}
PSLUG = {'46': 'valencia', '03': 'alicante', '12': 'castellon'}
CAJA = (-1.55, 37.83, 0.75, 40.82)
COMP = '#e8850c'   # Compromís, naranja (como en comunitat_valenciana.py)
# En la Comunitat, Más País se presentó en 2019 como Más Compromís; en 2023, Compromís fue con Sumar; el 29N, la lista
# «Sumar» del modelo es Compromís-Front Valencià (Compromís, Podem, EUPV y ERPV), según EFE
COL = dict(COL, MP=COMP, CFV=COMP)
NOMC = dict(NOM, MP='Más Compromís', SUMAR='Sumar-Compromís', CFV='Compromís-Front Valencià', EMPATE='Empate a votos')


def bonito(nombre):
    """«Vila Joiosa, la/Villajoyosa» → «La Vila Joiosa/Villajoyosa», como en las fichas de municipio."""
    partes = []
    for t in nombre.split('/'):
        base, coma, art = t.rpartition(', ')
        if coma and art.lower() in ('la', 'el', 'les', 'els', "l'", 'los', 'las'):
            t = art.capitalize() + ('' if art.endswith("'") else ' ') + base
        partes.append(t)
    return '/'.join(partes)


corto = lambda nombre: bonito(nombre).split('/')[0]   # en gráficos, la primera forma oficial
assert bonito('Vila Joiosa, la/Villajoyosa') == 'La Vila Joiosa/Villajoyosa' and bonito("Alfàs del Pi, l'") == "L'Alfàs del Pi"

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 542
NOMM = {k: bonito(v) for k, v in zip(m.mun_code, m.municipio)}
A19, A23 = agrega(m, Y19), agrega(m, Y23)
A19L = agrega(m, Y19, listas=('PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS'))
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 353, 'PP': 148, 'VOX': 24, 'EMPATE': 9, 'UP': 5, 'MP': 3}, GANA[Y19]
assert GANA[Y23] == {'PP': 303, 'PSOE': 224, 'SUMAR': 10, 'EMPATE': 4, 'VOX': 1}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, VOX_PP, PSOE_PSOE = TR('PSOE', 'PP'), TR('VOX', 'PP'), TR('PSOE', 'PSOE')
assert (PSOE_PP, VOX_PP, PSOE_PSOE) == (138, 24, 208)
PSOE_PIERDE = int(((m.g2019 == 'PSOE') & (m.g2023 != 'PSOE')).sum())
PSOE_GANA = int(((m.g2019 != 'PSOE') & (m.g2023 == 'PSOE')).sum())
assert (PSOE_PIERDE, PSOE_GANA) == (145, 16)
VOX23 = list(m[m.g2023 == 'VOX'].municipio)
assert VOX23 == ['Vilar de Canes']
EMP = {y: m[m[f'g{y[:4]}'] == 'EMPATE'] for y in (Y19, Y23)}
assert len(EMP[Y19]) == 9 and set(EMP[Y23].emp2023) == {'PP-PSOE'} and len(EMP[Y23]) == 4
DPSOE, DPP = A23['pct']['PSOE'] - A19['pct']['PSOE'], A23['pct']['PP'] - A19['pct']['PP']
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
assert DPSOE_VOTOS == 148135 and DPSOE > 0 and DPP > DPSOE
assert A23['part'] > A19['part'] and A23['pct']['VOX'] < A19['pct']['VOX']
assert A23['pct']['SUMAR'] < A19L['pct']['UP'] + A19L['pct']['MP']
m['dPSOE'] = m[f'{Y23}%PSOE'] - m[f'{Y19}%PSOE']
m['dPP'] = m[f'{Y23}%PP'] - m[f'{Y19}%PP']
PSOE_SUBE, PP_SUBE = int((m.dPSOE > 0).sum()), int((m.dPP > 0).sum())
assert (PSOE_SUBE, PP_SUBE) == (459, 523)
POB = {f: float(m[m.g2023 == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')}
# Los municipios que pasaron del PSOE al PP
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10

# Provincias
PR = {pr: {y: agrega(m[m.prov == pr], y) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
assert PRG['46'][Y23]['PSOE'] == 134 and PRG['46'][Y23]['PP'] == 128
assert all(max(PR[pr][Y23]['pct'], key=PR[pr][Y23]['pct'].get) == 'PP' for pr in PROV)
assert all(max(PR[pr][Y19]['pct'], key=PR[pr][Y19]['pct'].get) == 'PSOE' for pr in PROV)

# Tamaño de municipio (población del padrón de 2023)
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000),
       ('De 20.000 a 100.000', 20000, 100000), ('Más de 100.000', 100000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19)['pct'], agrega(g, Y23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert all(t['pp23'] > t['pp19'] and t['psoe23'] > t['psoe19'] and t['vox23'] < t['vox19'] for t in TT.values())
G20 = m[m.poblacion >= 20000]
G20G = {y: G20[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert G20G == {Y19: {'PSOE': 57, 'PP': 5, 'VOX': 5}, Y23: {'PP': 39, 'PSOE': 28}}, G20G

# Las cuatro ciudades de más de 100.000 habitantes (las tres capitales y Elche)
CIU = m[m.poblacion >= 100000].sort_values('poblacion', ascending=False)
CORTO = {'46250': 'Valencia', '03014': 'Alicante', '03065': 'Elche', '12040': 'Castellón de la Plana'}
assert set(CIU.mun_code) == set(CORTO) and (CIU.g2019 == 'PSOE').all() and (CIU.g2023 == 'PP').all()
VLC = m[m.mun_code == '46250'].iloc[0]

# Municipios ajustados en 2023
AJ2 = int((m.marg2023 < 2).sum())
AJG = m[(m.poblacion >= 20000) & (m.marg2023 < 2)].sort_values('marg2023')
assert len(AJG) == 14 and all({r.g2023, r.seg2023} == {'PP', 'PSOE'} for _, r in AJG.iterrows())
# Gandia y La Vila Joiosa: el PP ganó por 28 votos en cada una (12.834 a 12.806 y 5.406 a 5.378), lo mismo que publica Público
GAN = m[m.municipio == 'Gandia'].iloc[0]
VJ = m[m.mun_code == '03139'].iloc[0]
assert int(GAN.margv2023) == 28 and int(VJ.margv2023) == 28 and GAN.g2023 == VJ.g2023 == 'PP'
assert int(GAN['2023_07_vPP']) == 12834 and int(VJ['2023_07_vPP']) == 5406
PUB_GAN = 'https://www.publico.es/resultados-elecciones/generales/2023/comunitat-valenciana/valencia/gandia'
PUB_VJ = 'https://www.publico.es/resultados-elecciones/generales/2023/comunitat-valenciana/alicante/villajoyosa-vila-joiosa-la'

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(list(PROV))
F19, F23 = ('PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F19}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F23}
assert E19 == {'PP': 8, 'PSOE': 10, 'VOX': 7, 'UP': 4, 'MP': 1, 'CS': 2}, E19
assert E23 == {'PP': 13, 'PSOE': 11, 'VOX': 5, 'SUMAR': 4}, E23
assert sum(ESC['2026'].values()) == 33
RC = {pr: {('CFV' if k == 'SUMAR' else k): v for k, v in reparto_central(PSLUG[pr]).items()} for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in ('PP', 'PSOE', 'VOX', 'CFV')}
assert sum(E29.values()) == 33, E29
assert E29['PSOE'] == E23['PSOE'] and E29['CFV'] == E23['SUMAR'] - 1 and E29['PP'] < E23['PP'] and E29['VOX'] > E23['VOX'], E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'
P1 = {pr: {l['lista']: l['p_primera'] for l in MOD['provincias'][pr]['listas']} for pr in PROV}
assert all(max(P1[pr], key=P1[pr].get) == 'PP' for pr in PROV)

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=39.3)
assert len(cam) == NMUN
ORDG = ['PSOE', 'UP', 'MP', 'SUMAR', 'PP', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
EMPN = lambda y: ', '.join(bonito(x) for x in EMP[y].municipio)
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de la Comunitat Valenciana, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de la Comunitat Valenciana por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de la Comunitat Valenciana por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Ganador según los votos de cada candidatura: '
                  'en 2019, Unidas Podemos y Más Compromís por separado; en 2023, Sumar, que iba con Compromís. En gris, los municipios en los que '
                  f'los dos primeros empataron a votos: en 2019, {EMPN(Y19)}; en 2023, {EMPN(Y23)}.',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], str(GANA[Y19].get(f, 0)), str(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', str(NMUN), str(NMUN)]]))

TRAMOS = [(-99, 0, '#d9d4cf', 'bajó'), (0, 3, '#fbd5d3', '0 a 3'), (3, 6, '#f4a29d', '3 a 6'), (6, 10, '#e8645c', '6 a 10'),
          (10, 99, '#a51d16', '10 o más')]
DM = dict(zip(m.mun_code, m.dPSOE))
tramo = lambda v: next(c for a, b, c, _ in TRAMOS if a < v <= b)
NTR = {e: int(((m.dPSOE > a) & (m.dPSOE <= b)).sum()) for a, b, _, e in TRAMOS}
g_mapdpsoe = figura(f'El PSOE subió en {PSOE_SUBE} de los {NMUN} municipios, también en muchos de los que perdió',
                    'Cambio del voto al PSOE entre noviembre de 2019 y julio de 2023 en cada municipio, en puntos',
                    mapa_svg(cam, H, lambda k: tramo(DM[k]), lambda k: f'PSOE {s1(DM[k])} puntos', 'Cambio del PSOE por municipio entre 2019 y 2023', NOMM),
                    'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                    [(f'{e} puntos' if e != 'bajó' else 'Bajó', c) for _, _, c, e in TRAMOS],
                    (['Cambio del PSOE', 'Municipios'], [[f'{e} puntos' if e != 'bajó' else 'Bajó', str(NTR[e])] for _, _, _, e in TRAMOS] + [['Total', str(NMUN)]]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COL[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COL[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]))

ORDT = ['PP', 'PSOE', 'SUMAR', 'VOX', 'EMPATE']
ORDT19 = ['PSOE', 'UP', 'MP', 'PP', 'VOX', 'EMPATE']
g_tam = figura(f'En los municipios de más de 20.000 habitantes, el PSOE pasó de ganar en {G20G[Y19]["PSOE"]} a ganar en {G20G[Y23]["PSOE"]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COL[f], NOMC[f]) for f in ORDT19 if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ['PP', 'PSOE', 'VOX', 'UP', 'MP', 'SUMAR', 'EMPATE']],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'Vox 2019', 'PP 2023', 'PSOE 2023', 'Sumar-Compromís 2023'],
                [[nom, str(t['n']), n(t['censo'])] + [str(t['g19'].get(f, 0)) for f in ('PSOE', 'PP', 'VOX')] + [str(t['g23'].get(f, 0)) for f in ('PP', 'PSOE', 'SUMAR')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PP y el PSOE subieron en todos los tamaños de municipio; el PP, más',
                  'Voto al PP, al PSOE y a Vox en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['vox19'], COL['VOX'], .38, 'Vox, nov. 2019'), (t['vox23'], COL['VOX'], 1, 'Vox, 2023')]) for nom, t in TT.items()],
                         45, 'Voto al PP, al PSOE y a Vox según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('Vox', COL['VOX']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox nov. 2019 (%)', 'Vox 2023 (%)', 'Sumar-Compromís 2023 (%)'],
                   [[nom, p(t['pp19']), p(t['pp23']), p(t['psoe19']), p(t['psoe23']), p(t['vox19']), p(t['vox23']), p(t['sumar23'])] for nom, t in TT.items()]))

g_ciu = figura('El PSOE ganó en 2019 en las cuatro ciudades de más de 100.000 habitantes; el PP, en 2023',
               'Voto al PP y al PSOE en julio de 2023, en %, en Valencia, Alicante, Elche y Castellón de la Plana',
               grupos([(CORTO[r.mun_code], [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PP', 'PSOE')]) for _, r in CIU.iterrows()],
                      45, 'Voto al PP y al PSOE en las ciudades de más de 100.000 habitantes en 2023', W=440, ml=130),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Municipio', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Sumar-Compromís 2023 (%)'],
                [[CORTO[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y23}%VOX']), p(r[f'{Y23}%SUMAR'])] for _, r in CIU.iterrows()]))

g_prov = figura('El PP ganó en votos en las tres provincias; en número de municipios, el PSOE sigue por delante en Valencia',
                'Municipios ganados por cada partido en julio de 2023, por provincia',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDT if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada provincia en 2023', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ORDT],
                (['Provincia', 'Municipios', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Sumar-Compromís 2023 (%)', 'Municipios PP', 'Municipios PSOE'],
                 [[PROV[pr], str(PRN[pr])] + [p(PR[pr][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]
                  + [str(PRG[pr][Y23].get(f, 0)) for f in ('PP', 'PSOE')] for pr in PROV]))

g_aj = figura(f'{len(AJG)} municipios de más de 20.000 habitantes se decidieron en 2023 por menos de dos puntos, todos entre el PP y el PSOE',
              'Ventaja del partido más votado sobre el segundo en julio de 2023, en puntos',
              barras([(corto(r.municipio), r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], 2.2,
                     'Municipios de más de 20.000 habitantes decididos por menos de dos puntos', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in ('PP', 'PSOE')],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ganador nov. 2019'],
               [[bonito(r.municipio), PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'UP', 'MP', 'SUMAR', 'CFV', 'PP', 'CS', 'VOX']


def hemi(lado=16, por_fila=17):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de la Comunitat Valenciana en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PP', 'PSOE', 'VOX', 'CFV')
g_esc = figura(f'Con las encuestas, el PP pasaría de {E23["PP"]} a {E29["PP"]} diputados valencianos y Vox, de {E23["VOX"]} a {E29["VOX"]}',
               'Los 33 diputados de las tres provincias valencianas: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/valencia/">/encuestas/</a>) {VERSION}. En 2019, Más Compromís; en 2023, Sumar con Compromís; el 29N, Compromís-Front Valencià.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Provincia', 'PP 2023', 'PSOE 2023', 'Vox 2023', 'Sumar-Compromís 2023'] + [f'{NOMC[f]} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in F23]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in F23] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de la Comunitat Valenciana</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de la Comunitat Valenciana por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=46250">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/comunidad-valenciana/">datos de cada municipio de la Comunitat Valenciana</a></div>\n</figure>\n')

# --- Texto ---
EFE = 'https://www.infobae.com/espana/agencias/2026/11/11/la-comunitat-valenciana-pieza-clave-que-el-pp-y-psoe-ambicionan-para-gobernar-en-espana/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
TPQ = TT['De 1.000 a 5.000']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La Comunitat Valenciana elige el 29 de noviembre 33 diputados: 16 por Valencia, 12 por Alicante y 5 por Castellón. Según <a href="{EFE}">EFE</a>, el PP ha ganado en la Comunitat todas las elecciones generales desde 1993 salvo las dos de 2019, en las que ganaron los socialistas. Para el 29N, el PP aspira a ampliar sus votos de 2023 para «echar al sanchismo», y Compromís-Front Valencià, la candidatura de Compromís con Podem, EUPV y ERPV, se ofrece para «no resignarse a votar con miedo o con la nariz tapada», según la misma agencia.</p>
<p data-tipo="dato">El mapa municipio a municipio muestra lo que cambió entre una victoria y otra. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios valencianos, el PP en {GANA[Y19]["PP"]} y Vox en {GANA[Y19]["VOX"]}; en otros {GANA[Y19]["EMPATE"]}, los dos primeros empataron a votos. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]}, el PSOE en {GANA[Y23]["PSOE"]}, Sumar-Compromís en {GANA[Y23]["SUMAR"]} y Vox en {NW[len(VOX23)]}, Vilar de Canes; en {NW[GANA[Y23]["EMPATE"]]} hubo empate entre el PP y el PSOE.</p>
{g_ins}
<p data-tipo="dato">El PSOE no perdió votos: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DPSOE_VOTOS)} votos más, y subió en {PSOE_SUBE} de los {NMUN} municipios. Pero el PP subió más, del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, {p(DPP)} puntos, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. Sumar-Compromís sacó el {p(A23["pct"]["SUMAR"])} %, menos de lo que sumaron en 2019 Unidas Podemos ({p(A19L["pct"]["UP"])} %) y Más Compromís ({p(A19L["pct"]["MP"])} %). La participación subió del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP; los {GANA[Y19]["VOX"]} de Vox, también. En los {PSOE_PP} que el PSOE perdió frente al PP, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, y el PP, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %.</p>
{g_flip}
{g_mapdpsoe}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">El vuelco fue mayor cuanto más grande el municipio. En los de más de 20.000 habitantes, el PSOE había ganado en {G20G[Y19]["PSOE"]} de {len(G20)} en 2019 y ganó en {G20G[Y23]["PSOE"]} en 2023; el PP pasó de {G20G[Y19]["PP"]} a {G20G[Y23]["PP"]}. En los de 1.000 a 5.000, el PSOE ganó en {TPQ["g23"]["PSOE"]} de {TPQ["n"]} y el PP en {TPQ["g23"]["PP"]}, casi un empate. El PP y el PSOE subieron en todos los tamaños de municipio, y Vox bajó en todos. Como los municipios grandes concentran la población, los ganados por el PP en 2023 suman el {p(POB["PP"])} % de los habitantes.</p>
{g_tam}
{g_tampct}
<p data-tipo="dato">Las cuatro ciudades de más de 100.000 habitantes, Valencia, Alicante, Elche y Castellón de la Plana, las ganó el PSOE en 2019 y el PP en 2023. En Valencia, el PP sacó el {p(VLC[f"{Y23}%PP"])} % y el PSOE el {p(VLC[f"{Y23}%PSOE"])} %; en 2019, el PSOE había ganado con el {p(VLC[f"{Y19}%PSOE"])} %, por delante del PP ({p(VLC[f"{Y19}%PP"])} %). Lo contamos barrio a barrio en {L("valencia-barrio-a-barrio-29n", "Valencia")}.</p>
{g_ciu}
<h2>Tres provincias: el PP gana en votos, el PSOE resiste en los pueblos de Valencia</h2>
<p data-tipo="dato">En 2019, el PSOE fue el más votado en las tres provincias; en 2023, el PP. En número de municipios, el PP ganó en más en Alicante ({PRG["03"][Y23]["PP"]} de {PRN["03"]}) y en Castellón ({PRG["12"][Y23]["PP"]} de {PRN["12"]}). En la provincia de Valencia, el PSOE siguió ganando en más municipios que el PP: {PRG["46"][Y23]["PSOE"]} frente a {PRG["46"][Y23]["PP"]} de {PRN["46"]}.</p>
{g_prov}
<h2>Dónde se decide por unos pocos votos</h2>
<p data-tipo="dato">En {AJ2} municipios valencianos, el primero sacó al segundo menos de dos puntos en 2023. Entre los de más de 20.000 habitantes fueron {len(AJG)}, todos entre el PP y el PSOE. Los dos más ajustados se decidieron por {n(GAN.margv2023)} votos cada uno, y los dos a favor del PP: Gandia, {n(GAN["2023_07_vPP"])} a {n(GAN["2023_07_vPSOE"])}, y La Vila Joiosa, {n(VJ["2023_07_vPP"])} a {n(VJ["2023_07_vPSOE"])}, las mismas cifras que publica Público para <a href="{PUB_GAN}">Gandia</a> y <a href="{PUB_VJ}">La Vila Joiosa</a>.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 33 escaños da al PP {E29["PP"]}, {NW[E23["PP"] - E29["PP"]]} menos que en 2023; al PSOE, {E29["PSOE"]}, los mismos; a Vox, {E29["VOX"]}, {NW[E29["VOX"] - E23["VOX"]]} más, y a Compromís-Front Valencià, {E29["CFV"]}, uno menos de los {E23["SUMAR"]} que sacó Sumar con Compromís. El PP es el más votado en la mayoría de las simulaciones en las tres provincias. El reparto provincia a provincia, con los escaños que se juegan por pocos votos, está en {L("comunitat-valenciana-escanos-29n", "la pieza sobre los 33 escaños valencianos")}.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 18 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la Comunitat desde 1977, con las autonómicas, está en {L("comunidad-valenciana-historia-electoral", "La Comunitat Valenciana en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/comunidad-valenciana/">la ficha de la Comunitat Valenciana</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en la Comunitat Valenciana?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar-Compromís ({p(A23["pct"]["SUMAR"])} %). '
     f'Sacó {E23["PP"]} de los 33 diputados; el PSOE, {E23["PSOE"]}; Vox, {E23["VOX"]}, y Sumar-Compromís, {E23["SUMAR"]}.'),
    ('¿En cuántos municipios valencianos ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}; Sumar-Compromís, en {GANA[Y23]["SUMAR"]}, y Vox, en {NW[GANA[Y23]["VOX"]]}. En otros {NW[GANA[Y23]["EMPATE"]]} hubo empate a votos. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} y el PP en {GANA[Y19]["PP"]}.'),
    ('¿Cuántos diputados elige la Comunitat Valenciana el 29N?',
     '33, los mismos que en 2023: Valencia elige 16; Alicante, 12, y Castellón, 5.'),
    ('¿Qué dicen las encuestas en la Comunitat Valenciana?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]}, a Vox {E29["VOX"]} y a Compromís-Front Valencià {E29["CFV"]}, con un margen amplio.'),
]
enlaces = (f'{L("comunidad-valenciana-historia-electoral", "Historia electoral de la Comunitat Valenciana")} · {L("comunitat-valenciana-escanos-29n", "Los 33 escaños valencianos")} · '
           f'{L("valencia-barrio-a-barrio-29n", "Valencia barrio a barrio")} · <a href="{BASE}elecciones/comunidad-valenciana/">Datos de cada municipio</a> · <a href="{BASE}encuestas/valencia/">Encuesta en Valencia</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_valencia.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'A19L': A19L, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'VOX_PP': VOX_PP, 'PSOE_PIERDE': PSOE_PIERDE, 'PSOE_GANA': PSOE_GANA,
    'DPSOE': DPSOE, 'DPP': DPP, 'DPSOE_VOTOS': DPSOE_VOTOS, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE, 'POB': POB, 'NTR': NTR, 'NVOX23': len(VOX23),
    'FLS': FLS, 'TT': TT, 'G20': len(G20), 'G20G': G20G,
    'PR': {pr: {y: PR[pr][y]['pct'] for y in PR[pr]} for pr in PR}, 'PRG': PRG, 'PRN': PRN,
    'VLC': {f'{k.lower()}{y[2:4]}': R(VLC[f'{y}%{k}']) for k in ('PP', 'PSOE') for y in (Y19, Y23)},
    'CIU': [[CORTO[r.mun_code], r.g2019, r.g2023, R(r[f'{Y23}%PP']), R(r[f'{Y23}%PSOE'])] for _, r in CIU.iterrows()],
    'AJ2': AJ2, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023)] for _, r in AJG.iterrows()],
    'GANDIA': [int(GAN['2023_07_vPP']), int(GAN['2023_07_vPSOE'])], 'VILAJOIOSA': [int(VJ['2023_07_vPP']), int(VJ['2023_07_vPSOE'])],
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC, 'P1': {pr: P1[pr].get('PP') for pr in PROV},
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de la Comunitat Valenciana',
      f'El mapa electoral de la Comunitat Valenciana: el PSOE sumó {n(DPSOE_VOTOS)} votos y aun así pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}',
      f'El PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]} municipios y ganó en las cuatro ciudades de más de 100.000 habitantes, mientras desaparecía Ciudadanos. '
      f'Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 33 diputados, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}.',
      '11 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'E29', E29, 'FLS', {y: {k: round(v, 1) for k, v in FLS[y].items() if v} for y in FLS}, 'POB', POB, 'AJ', AJ2, len(AJG), 'G20G', G20G)
