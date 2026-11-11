"""«El mapa electoral de Castilla y León» (2026-11), quinta pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 2.248 municipios de Castilla y León en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(listas por separado: en 2019, Unidas Podemos y Más País; y las listas provinciales, Por Ávila, UPL, Soria ¡Ya! y la
Plataforma del Pueblo Soriano, que en las descargas del mapa van en «otros»: datos/regionalistas_cyl_2019_2023.csv, de los
mismos datos por mesa de pollspaindata/Interior), el tamaño de los municipios (padrón de 2023), las nueve capitales, las
provincias, los municipios decididos por un voto y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: El Debate (Mañueco, 25-10-2026; Carlos Martínez, 5-10-2026, con Ical), EFE (Soria ¡Ya!, 5-10-2026), BOE y
El Español (candidaturas proclamadas, 3-11-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_cyl.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, s1, trazados)

A = BASE + 'actualidad/'
NW = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-castilla-y-leon-29n'
PROV = {'05': 'Ávila', '09': 'Burgos', '24': 'León', '34': 'Palencia', '37': 'Salamanca', '40': 'Segovia', '42': 'Soria',
        '47': 'Valladolid', '49': 'Zamora'}
PSLUG = {'05': 'avila', '09': 'burgos', '24': 'leon', '34': 'palencia', '37': 'salamanca', '40': 'segovia', '42': 'soria',
         '47': 'valladolid', '49': 'zamora'}
CAPITAL = {'05019': 'Ávila', '09059': 'Burgos', '24089': 'León', '34120': 'Palencia', '37274': 'Salamanca', '40194': 'Segovia',
           '42173': 'Soria', '47186': 'Valladolid', '49275': 'Zamora'}
CAJA = (-7.1, 40.05, -1.75, 43.25)
# Colores de las listas provinciales, los mismos que en «Castilla y León en las urnas» (comunidades/datos.py)
COL = dict(COL, XAV='#2e6d4f', UPL='#b0124a', SY='#2f9e62', PPSO='#9c7a3c')
NOMC = dict(NOM, XAV='Por Ávila', UPL='UPL', SY='Soria ¡Ya!', PPSO='Plataforma del Pueblo Soriano', EMPATE='Empate a votos')


def bonito(nombre):
    """«Aldehuelas, Las» → «Las Aldehuelas», como en las fichas de municipio."""
    base, coma, art = nombre.rpartition(', ')
    if coma and art.lower() in ('la', 'el', 'los', 'las'):
        return art.capitalize() + ' ' + base
    return nombre


assert bonito('Aldehuelas, Las') == 'Las Aldehuelas'

m = municipios(list(PROV), regionales='regionalistas_cyl_2019_2023.csv')
NMUN = len(m)
assert NMUN == 2248
NOMM = {k: bonito(v) for k, v in zip(m.mun_code, m.municipio)}
A19, A23 = agrega(m, Y19, ('PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'XAV', 'UPL', 'PPSO')), agrega(m, Y23, ('PP', 'PSOE', 'VOX', 'SUMAR', 'XAV', 'UPL', 'SY'))
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PP': 1546, 'PSOE': 592, 'VOX': 52, 'EMPATE': 45, 'UP': 9, 'XAV': 3, 'PPSO': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 1886, 'PSOE': 307, 'EMPATE': 33, 'VOX': 14, 'SY': 4, 'XAV': 3, 'SUMAR': 1}, GANA[Y23]
assert GANA[Y23].get('UPL', 0) == 0 and GANA[Y19].get('UPL', 0) == 0
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, VOX_PP, PSOE_PSOE = TR('PSOE', 'PP'), TR('VOX', 'PP'), TR('PSOE', 'PSOE')
assert (PSOE_PP, VOX_PP, PSOE_PSOE) == (311, 43, 267)
DPSOE_VOTOS = A23['votos']['PSOE'] - A19['votos']['PSOE']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
assert DPSOE_VOTOS == 26886 and DPP_VOTOS == 152770
DPSOE, DPP = A23['pct']['PSOE'] - A19['pct']['PSOE'], A23['pct']['PP'] - A19['pct']['PP']
assert 0 < DPSOE < DPP and A23['pct']['VOX'] < A19['pct']['VOX'] and A23['part'] > A19['part']
assert A19['pct']['PP'] > A19['pct']['PSOE']   # en 2019 el PP ya fue el más votado de la comunidad, por poco
m['dPSOE'] = m[f'{Y23}%PSOE'] - m[f'{Y19}%PSOE']
m['dPP'] = m[f'{Y23}%PP'] - m[f'{Y19}%PP']
PSOE_SUBE, PP_SUBE = int((m.dPSOE > 0).sum()), int((m.dPP > 0).sum())
assert (PSOE_SUBE, PP_SUBE) == (1070, 1927)
# Población de los municipios que ganó cada partido (padrón de 2023)
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert round(POB[Y19]['PSOE'], 1) == 61.6 and round(POB[Y23]['PSOE'], 1) == 15.1 and round(POB[Y23]['PP'], 1) == 84.7
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10
VX19 = m[m.g2019 == 'VOX']
assert len(VX19) == 52 and (VX19.g2023 == 'PP').sum() == 43 and (VX19.g2023 == 'VOX').sum() == 6
VX19_MED = float(VX19.poblacion.median())
assert VX19_MED < 100

# Listas provinciales: Por Ávila, Soria ¡Ya! y la Plataforma del Pueblo Soriano
REG = m[m.g2019.isin(['XAV', 'PPSO']) | m.g2023.isin(['XAV', 'SY'])].sort_values(['prov', 'municipio'])
assert len(REG) == 8 and REG.poblacion.max() < 200
XAV3 = sorted(bonito(x) for x in m[m.g2023 == 'XAV'].municipio)
assert XAV3 == ['Chamartín', 'Niharra', 'Poveda'] and set(m[m.g2019 == 'XAV'].municipio) == set(m[m.g2023 == 'XAV'].municipio)
SY4 = sorted(bonito(x) for x in m[m.g2023 == 'SY'].municipio)
assert SY4 == ['Aliud', 'Blacos', 'Las Aldehuelas', 'Villar del Campo'], SY4
PRS = {pr: {y: agrega(m[m.prov == pr], y, ('PP', 'PSOE', 'VOX', 'SUMAR', 'XAV', 'UPL', 'SY', 'CS')) for y in (Y19, Y23)} for pr in PROV}
SY_SORIA = PRS['42'][Y23]['pct']['SY']
UPL_LEON = PRS['24'][Y23]['pct']['UPL']
XAV_AVILA = PRS['05'][Y23]['pct']['XAV']
assert 19 < SY_SORIA < 20 and 8 < UPL_LEON < 9 and 7 < XAV_AVILA < 8

# Provincias
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
PRIM = {y: {pr: max(PRS[pr][y]['pct'], key=PRS[pr][y]['pct'].get) for pr in PROV} for y in (Y19, Y23)}
assert all(v == 'PP' for v in PRIM[Y23].values())
P19PSOE = [PROV[pr] for pr in PROV if PRIM[Y19][pr] == 'PSOE']
assert P19PSOE == ['Burgos', 'León', 'Soria', 'Valladolid'], P19PSOE

# Tamaño de municipio (población del padrón de 2023)
TAM = [('Menos de 100', 0, 100), ('De 100 a 1.000', 100, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000),
       ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19)['pct'], agrega(g, Y23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert all(t['pp23'] > t['pp19'] and t['vox23'] < t['vox19'] for t in TT.values())
T100 = TT['Menos de 100']
assert T100['n'] == 746 and T100['censo'] == 40443
CAPV = m[m.mun_code == '05019'].iloc[0]
assert T100['censo'] < CAPV[f'{Y23}_censo']   # los 746 pueblos de menos de 100 habitantes tienen menos electores que la ciudad de Ávila
TG = TT['Más de 20.000']
assert TG['n'] == 15 and TG['g19'] == {'PSOE': 11, 'PP': 4} and TG['g23'] == {'PP': 11, 'PSOE': 4}

# Las nueve capitales
CAP = m[m.mun_code.isin(CAPITAL)].sort_values('poblacion', ascending=False)
CAP19 = [CAPITAL[k] for k in CAP.mun_code if CAP.set_index('mun_code').at[k, 'g2019'] == 'PSOE']
CAP23 = [CAPITAL[k] for k in CAP.mun_code if CAP.set_index('mun_code').at[k, 'g2023'] == 'PSOE']
assert sorted(CAP19) == ['Burgos', 'León', 'Palencia', 'Soria', 'Valladolid', 'Zamora'] and CAP23 == ['Soria'], (CAP19, CAP23)
assert (CAP.g2023[CAP.mun_code != '42173'] == 'PP').all() and (CAP.g2019[~CAP.mun_code.isin(['05019', '37274', '40194'])] == 'PSOE').all()
SOR = CAP[CAP.mun_code == '42173'].iloc[0]
assert SOR[f'{Y23}%PSOE'] > SOR[f'{Y23}%PP'] and SOR.marg2023 < 2.5
PAL = CAP[CAP.mun_code == '34120'].iloc[0]
VLL = CAP[CAP.mun_code == '47186'].iloc[0]
assert list(CAP.sort_values('marg2023').mun_code[:2]) == ['34120', '42173'] and PAL.g2019 == 'PSOE' and PAL.g2023 == 'PP'
PONF = m[m.mun_code == '24115'].iloc[0]
assert PONF.municipio == 'Ponferrada' and PONF.g2019 == PONF.g2023 == 'PSOE'
G20 = m[m.poblacion >= 20000]
G20PSOE23 = sorted(bonito(x) for x in G20[G20.g2023 == 'PSOE'].municipio)
assert G20PSOE23 == ['Miranda de Ebro', 'Ponferrada', 'San Andrés del Rabanedo', 'Soria'], G20PSOE23

# Municipios ajustados: los decididos por un voto y los empates
UNVOTO = int((m.margv2023 == 1).sum())
AJ2 = int((m.marg2023 < 2).sum())
assert UNVOTO == 53 and GANA[Y23]['EMPATE'] == 33
UNV = m[m.margv2023 == 1]
UNVG = UNV.g2023.value_counts().to_dict()
UNV_POB = float(UNV.poblacion.median())
assert UNV_POB < 200
# Por tamaño, los más ajustados entre los de más de 5.000 habitantes
AJG = m[(m.poblacion >= 5000)].sort_values('marg2023').head(10)
assert set(AJG.g2023) <= {'PP', 'PSOE'}

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(list(PROV))
F19, F23 = ('PP', 'PSOE', 'VOX'), ('PP', 'PSOE', 'VOX')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F19}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F23}
assert E19 == {'PP': 13, 'PSOE': 12, 'VOX': 6}, E19
assert E23 == {'PP': 18, 'PSOE': 12, 'VOX': 1}, E23
assert ESC[Y23]['47'].get('VOX') == 1   # el único escaño de Vox en 2023, por Valladolid
assert sum(ESC['2026'].values()) == 31 and sum(E19.values()) == 31 and sum(E23.values()) == 31
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in ('PP', 'PSOE', 'VOX')}
assert sum(E29.values()) == 31 and set().union(*RC.values()) <= {'PP', 'PSOE', 'VOX'}, (E29, RC)
assert E29['PP'] < E23['PP'] and E29['PSOE'] < E23['PSOE'] and E29['VOX'] > E23['VOX'], E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'
P1 = {pr: {l['lista']: l['p_primera'] for l in MOD['provincias'][pr]['listas']} for pr in PROV}
assert all(max(P1[pr], key=P1[pr].get) == 'PP' for pr in PROV)
# El modelo no tiene a Soria ¡Ya! como lista propia; UPL y Por Ávila no se presentan el 29N (BOE de 3-11-2026)
assert not any(l['lista'] in ('Soria ¡Ya!', 'UPL', 'Por Ávila') for pr in PROV for l in MOD['provincias'][pr]['listas'])

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=41.7, umbral=1.8)
assert len(cam) == NMUN
ORDG = ['PP', 'PSOE', 'VOX', 'UP', 'SUMAR', 'XAV', 'SY', 'PPSO', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {n(GANA[Y19]["PP"])} a {n(GANA[Y23]["PP"])}',
                  f'Partido más votado en cada uno de los {n(NMUN)} municipios de Castilla y León, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Castilla y León por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Castilla y León por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura: en 2019, Unidas Podemos y Más País por separado; Por Ávila, UPL, Soria ¡Ya! y la Plataforma del Pueblo '
                  f'Soriano, con sus votos. En gris, los municipios en los que los dos primeros empataron a votos ({GANA[Y19]["EMPATE"]} en 2019 y '
                  f'{GANA[Y23]["EMPATE"]} en 2023).',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN)]]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COL[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COL[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]))

ORDT = ['PP', 'PSOE', 'VOX', 'SUMAR', 'XAV', 'SY', 'EMPATE']
ORDT19 = ['PP', 'PSOE', 'VOX', 'UP', 'XAV', 'PPSO', 'EMPATE']
g_tam = figura(f'En los pueblos de menos de 100 habitantes, el PP ya ganaba; el vuelco llegó en los municipios grandes',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COL[f], NOMC[f]) for f in ORDT19 if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ['PP', 'PSOE', 'VOX', 'UP', 'SUMAR', 'XAV', 'SY', 'PPSO', 'EMPATE']],
               (['Población', 'Municipios', 'Electores (2023)', 'PP 2019', 'PSOE 2019', 'PP 2023', 'PSOE 2023'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PP', 'PSOE')] + [n(t['g23'].get(f, 0)) for f in ('PP', 'PSOE')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PP subió en todos los tamaños de municipio, y Vox bajó en todos',
                  'Voto al PP, al PSOE y a Vox en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['vox19'], COL['VOX'], .38, 'Vox, nov. 2019'), (t['vox23'], COL['VOX'], 1, 'Vox, 2023')]) for nom, t in TT.items()],
                         55, 'Voto al PP, al PSOE y a Vox según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('Vox', COL['VOX']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox nov. 2019 (%)', 'Vox 2023 (%)', 'Sumar 2023 (%)'],
                   [[nom, p(t['pp19']), p(t['pp23']), p(t['psoe19']), p(t['psoe23']), p(t['vox19']), p(t['vox23']), p(t['sumar23'])] for nom, t in TT.items()]))

g_cap = figura(f'El PSOE ganó en seis de las nueve capitales en 2019; en 2023, solo en Soria',
               'Voto al PP y al PSOE en julio de 2023 en las nueve capitales de provincia, en %',
               grupos([(CAPITAL[r.mun_code], [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PP', 'PSOE')]) for _, r in CAP.iterrows()],
                      55, 'Voto al PP y al PSOE en las capitales en 2023', W=440, ml=90),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Capital', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)'],
                [[CAPITAL[r.mun_code], NOMC[r.g2019], NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y23}%VOX'])] for _, r in CAP.iterrows()]))

g_prov = figura('El PP ganó en número de municipios en las nueve provincias, también en 2019',
                'Municipios ganados por cada partido en julio de 2023, por provincia',
                apiladas([(PROV[pr], [(PRG[pr][Y23].get(f, 0), COL[f], NOMC[f]) for f in ORDT if PRG[pr][Y23].get(f, 0)]) for pr in PROV],
                         'Municipios ganados por cada partido en cada provincia en 2023', W=440, ml=90),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COL[f]) for f in ORDT],
                (['Provincia', 'Municipios', 'Más votado nov. 2019', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Lista provincial 2023 (%)', 'Municipios PP 2023', 'Municipios PSOE 2023'],
                 [[PROV[pr], n(PRN[pr]), NOMC[PRIM[Y19][pr]]] + [p(PRS[pr][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'VOX')]
                  + [{'05': f'Por Ávila {p(XAV_AVILA)}', '24': f'UPL {p(UPL_LEON)}', '42': f'Soria ¡Ya! {p(SY_SORIA)}'}.get(pr, '—')]
                  + [n(PRG[pr][Y23].get(f, 0)) for f in ('PP', 'PSOE')] for pr in PROV]))
assert all(max(PRG[pr][y], key=PRG[pr][y].get) == 'PP' for pr in PROV for y in (Y19, Y23))

g_aj = figura(f'{UNVOTO} municipios se decidieron en 2023 por un solo voto, y en {GANA[Y23]["EMPATE"]} hubo empate',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los diez municipios de más de 5.000 habitantes más ajustados, en puntos',
              barras([(bonito(r.municipio), r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], max(AJG.marg2023) * 1.15,
                     'Municipios de más de 5.000 habitantes más ajustados en 2023', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in sorted(set(AJG.g2023), key=['PP', 'PSOE'].index)],
              (['Municipio', 'Provincia', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[bonito(r.municipio), PROV[r.prov], NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), n(r.margv2023), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX']


def hemi(lado=16, por_fila=16):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Castilla y León en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PP', 'PSOE', 'VOX')
g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en Castilla y León, y el PP y el PSOE perderían escaños',
               'Los 31 diputados de las nueve provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/valladolid/">/encuestas/</a>) {VERSION}. El modelo no incluye a Soria ¡Ya! como lista propia.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Provincia', 'PP 2023', 'PSOE 2023', 'Vox 2023'] + [f'{NOMC[f]} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in F23]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in F23] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Castilla y León</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Castilla y León por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=47186">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/castilla-y-leon/">datos de cada municipio de Castilla y León</a></div>\n</figure>\n')

# --- Texto ---
MANU = 'https://www.eldebate.com/espana/castilla-y-leon/20261025/manueco-asegura-elecciones-29n-pondran-fin-ocho-anos-mentiras-corrupcion_473577.html'
MART = 'https://www.eldebate.com/espana/castilla-y-leon/20261005/lider-psoe-castilla-leon-respalda-adelanto-electoral-acusa-pp-ejercer-antipolitica_466209.html'
SYA = 'https://www.diariodeleon.es/castilla-y-leon/261005/2099365/soria-avanza-concurrira-elecciones-ejercer-presion-provincia.html'
BOE = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-23103'
ESP = 'https://www.elespanol.com/castilla-y-leon/region/20261103/partidos-concurren-elecciones-castilla-leon-oscar-puente-sigue-candidaturas-eliminadas/1003744443810_0.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
T1K = TT['De 1.000 a 5.000']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Castilla y León tiene {n(NMUN)} municipios, más que ninguna otra comunidad, y elige el 29 de noviembre 31 diputados en sus nueve provincias. Alfonso Fernández Mañueco, presidente de la Junta y del PP de Castilla y León, lo contó a su manera en Salamanca, en un acto con Alberto Núñez Feijóo: de allí, dijo, «van a salir nueve caravanas provinciales y 2.248 caravanas locales en cada rincón», porque su objetivo es que «Sánchez se vaya por fin de la Moncloa», según <a href="{MANU}">El Debate</a>. El secretario general del PSOE de Castilla y León, Carlos Martínez, había recibido el adelanto electoral como «un deseo concedido» para el Partido Popular, en declaraciones recogidas por Ical y publicadas por <a href="{MART}">El Debate</a>.</p>
<p data-tipo="dato">El mapa municipio a municipio muestra cuánto cambió entre 2019 y 2023. En noviembre de 2019, el PP fue el partido más votado en {n(GANA[Y19]["PP"])} de los {n(NMUN)} municipios, el PSOE en {GANA[Y19]["PSOE"]} y Vox en {GANA[Y19]["VOX"]}; en otros {GANA[Y19]["EMPATE"]}, los dos primeros empataron a votos. En julio de 2023, el PP ganó en {n(GANA[Y23]["PP"])}, el PSOE en {GANA[Y23]["PSOE"]} y Vox en {GANA[Y23]["VOX"]}, y hubo {GANA[Y23]["EMPATE"]} empates. Pero el cambio que más pesa es el de las ciudades: el PSOE ganó en 2019 en seis de las nueve capitales, Burgos, León, Palencia, Soria, Valladolid y Zamora, y en 2023 solo en Soria.</p>
{g_ins}
<p data-tipo="dato">El PSOE no perdió votos: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DPSOE_VOTOS)} votos más. El PP sumó {n(DPP_VOTOS)} y subió del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. En 2019 el PP ya había sido el más votado en el conjunto de la comunidad, por {p(A19["pct"]["PP"] - A19["pct"]["PSOE"])} puntos; el PSOE lo había sido en cuatro provincias, Burgos, León, Soria y Valladolid. En 2023, el PP fue el primero en las nueve.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP. En ellos, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, y el PP, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %. De los {GANA[Y19]["VOX"]} pueblos que había ganado Vox, casi todos muy pequeños (la mitad tenían menos de {n(100)} habitantes), {VOX_PP} pasaron al PP. Como el PSOE perdió sobre todo ciudades, los municipios que ganó pasaron de sumar el {p(POB[Y19]["PSOE"])} % de la población de la comunidad al {p(POB[Y23]["PSOE"])} %.</p>
{g_flip}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">El mapa de Castilla y León está hecho de pueblos muy pequeños: {T100["n"]} de los {n(NMUN)} municipios tienen menos de 100 habitantes, y entre todos suman {n(T100["censo"])} electores, menos que la ciudad de Ávila sola ({n(CAPV[f"{Y23}_censo"])}). En esos pueblos el PP ya ganaba en 2019 ({T100["g19"]["PP"]} de {T100["n"]}). El vuelco llegó en los municipios grandes: en los de más de 20.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]} de {TG["n"]} en 2019 y en {TG["g23"]["PSOE"]} en 2023, Ponferrada, Miranda de Ebro, San Andrés del Rabanedo y Soria. En los de 1.000 a 5.000, el PSOE pasó de {T1K["g19"]["PSOE"]} a {T1K["g23"]["PSOE"]} de {T1K["n"]}. El PP subió en todos los tamaños de municipio, y Vox bajó en todos.</p>
{g_tam}
{g_tampct}
<p data-tipo="dato">En las capitales, la más ajustada de 2023 fue Palencia, que ganó el PP por {p(PAL.marg2023)} puntos tras haberla ganado el PSOE en 2019. Le siguió Soria, la única que conservó el PSOE, con el {p(SOR[f"{Y23}%PSOE"])} % frente al {p(SOR[f"{Y23}%PP"])} % del PP. En Valladolid, la mayor, el PP sacó el {p(VLL[f"{Y23}%PP"])} % y el PSOE el {p(VLL[f"{Y23}%PSOE"])} %; en 2019 había ganado el PSOE con el {p(VLL[f"{Y19}%PSOE"])} %, por delante del PP ({p(VLL[f"{Y19}%PP"])} %).</p>
{g_cap}
<h2>Nueve provincias y tres listas provinciales</h2>
<p data-tipo="dato">El PP ganó en número de municipios en las nueve provincias, ya en 2019. Las listas provinciales sacaron votos, pero apenas municipios: en 2023, Soria ¡Ya! obtuvo el {p(SY_SORIA)} % en la provincia de Soria y ganó en {NW[len(SY4)]} pueblos, {", ".join(SY4[:-1])} y {SY4[-1]}; Por Ávila, el {p(XAV_AVILA)} % en Ávila y ganó en {NW[len(XAV3)]}, {", ".join(XAV3[:-1])} y {XAV3[-1]}, los mismos que en 2019; la UPL, el {p(UPL_LEON)} % en León, sin ganar en ninguno. Ninguna sacó escaño. Para el 29N, Soria ¡Ya! vuelve a presentarse al Congreso por Soria, según <a href="{ESP}">El Español</a>; la UPL y Por Ávila no figuran entre las candidaturas proclamadas en León y Ávila que publicó el <a href="{BOE}">BOE</a> el 3 de noviembre.</p>
{g_prov}
<p data-tipo="contexto">Soria ¡Ya! calificó la legislatura que termina como «una de las peores para la provincia» y anunció que concurriría para tener más capacidad de presión por Soria, según <a href="{SYA}">EFE</a>.</p>
<h2>Dónde se decide por un voto</h2>
<p data-tipo="dato">Con tantos pueblos pequeños, muchos municipios se deciden por casi nada. En 2023, en {UNVOTO} el primero sacó un solo voto al segundo, y en {GANA[Y23]["EMPATE"]} los dos primeros empataron. En {n(AJ2)} la ventaja fue de menos de dos puntos. Entre los de más de 5.000 habitantes, el más ajustado fue {bonito(AJG.iloc[0].municipio)}, que ganó el {NOMC[AJG.iloc[0].g2023]} por {n(AJG.iloc[0].margv2023)} votos.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 31 escaños da al PP {E29["PP"]}, {NW[E23["PP"] - E29["PP"]]} menos que en 2023; al PSOE, {E29["PSOE"]}, {NW[E23["PSOE"] - E29["PSOE"]]} menos, y a Vox, {E29["VOX"]}, frente al {NW[E23["VOX"]]} que sacó en 2023 por Valladolid. El PP es el más votado en la mayoría de las simulaciones en las nueve provincias. El modelo no incluye a Soria ¡Ya! como lista propia, así que no recoge si puede disputar uno de los dos escaños de Soria.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos más pequeños, unos pocos votos cambian el ganador, y el mapa de colores exagera su peso. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 18 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la comunidad desde 1977, con las autonómicas, está en {L("castilla-y-leon-historia-electoral", "Castilla y León en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/castilla-y-leon/">la ficha de Castilla y León</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Castilla y León?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     f'Sacó {E23["PP"]} de los 31 diputados; el PSOE, {E23["PSOE"]}, y Vox, {NW[E23["VOX"]]}. El PP fue el más votado en las nueve provincias.'),
    ('¿En cuántos municipios de Castilla y León ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {n(NMUN)}; el PP, en {n(GANA[Y23]["PP"])}; Vox, en {GANA[Y23]["VOX"]}; Soria ¡Ya!, en {NW[GANA[Y23]["SY"]]}; Por Ávila, en {NW[GANA[Y23]["XAV"]]}, y Sumar, en {NW[GANA[Y23]["SUMAR"]]}. En otros {GANA[Y23]["EMPATE"]} hubo empate a votos. '
     f'En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} y el PP en {n(GANA[Y19]["PP"])}.'),
    ('¿En qué capitales ganó el PSOE?',
     'En noviembre de 2019, en seis de las nueve: Burgos, León, Palencia, Soria, Valladolid y Zamora. En julio de 2023, solo en Soria.'),
    ('¿Cuántos diputados elige Castilla y León el 29N?',
     f'31, los mismos que en 2023: Valladolid elige {ESC["2026"]["47"]}; Burgos, León y Salamanca, {ESC["2026"]["09"]} cada una; Ávila, Palencia, Segovia y Zamora, {ESC["2026"]["05"]}, y Soria, {ESC["2026"]["42"]}.'),
    ('¿Qué dicen las encuestas en Castilla y León?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio. El modelo no incluye a Soria ¡Ya! como lista propia.'),
]
assert ESC['2026'] == {'05': 3, '09': 4, '24': 4, '34': 3, '37': 4, '40': 3, '42': 2, '47': 5, '49': 3}
enlaces = (f'{L("castilla-y-leon-historia-electoral", "Historia electoral de Castilla y León")} · <a href="{BASE}elecciones/castilla-y-leon/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/valladolid/">Encuesta en Valladolid</a> · <a href="{BASE}encuestas/leon/">Encuesta en León</a> · <a href="{BASE}encuestas/soria/">Encuesta en Soria</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_cyl.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'VOX_PP': VOX_PP, 'PSOE_PSOE': PSOE_PSOE,
    'DPSOE': DPSOE, 'DPP': DPP, 'DPSOE_VOTOS': DPSOE_VOTOS, 'DPP_VOTOS': DPP_VOTOS, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE, 'POB': POB,
    'FLS': FLS, 'TT': TT, 'VX19_MED': VX19_MED, 'NMUN': NMUN,
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN,
    'SY_SORIA': SY_SORIA, 'UPL_LEON': UPL_LEON, 'XAV_AVILA': XAV_AVILA, 'NSY': len(SY4), 'NXAV': len(XAV3),
    'CAP': {CAPITAL[r.mun_code]: {'g19': r.g2019, 'g23': r.g2023, 'pp19': R(r[f'{Y19}%PP']), 'pp23': R(r[f'{Y23}%PP']), 'psoe19': R(r[f'{Y19}%PSOE']),
                                  'psoe23': R(r[f'{Y23}%PSOE']), 'marg23': R(r.marg2023), 'censo23': int(r[f'{Y23}_censo'])} for _, r in CAP.iterrows()},
    'NCAP19': len(CAP19), 'NCAP23': len(CAP23),
    'UNVOTO': UNVOTO, 'AJ2': AJ2, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJG.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC, 'P1': {pr: P1[pr].get('PP') for pr in PROV},
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Castilla y León',
      'El mapa electoral de Castilla y León: el PSOE ganó en seis de las nueve capitales en 2019 y solo en Soria en 2023',
      f'El PSOE sumó {n(DPSOE_VOTOS)} votos, pero pasó de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]} municipios, y los que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % '
      f'de la población al {p(POB[Y23]["PSOE"])} %. Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 31 diputados, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}.',
      '11 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'E29', E29, 'POB', POB, 'UNVOTO', UNVOTO, 'AJ2', AJ2, 'AJG', [(r.municipio, round(r.marg2023, 2), int(r.margv2023), r.g2023) for _, r in AJG.iterrows()],
      'VX19_MED', VX19_MED, 'SOR', round(SOR.marg2023, 2), 'PAL', round(PAL.marg2023, 2))
