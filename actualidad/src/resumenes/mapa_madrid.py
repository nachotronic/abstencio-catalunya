"""«El mapa electoral de la Comunidad de Madrid» (11-11-2026), tercera pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 179 municipios madrileños en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas por
separado: en 2019, Unidas Podemos y Más País), el cambio del PP, lo que pasó en los 61 municipios que ganó Vox en 2019, el
tamaño de los municipios (padrón de 2023, INE vía ineAtlas), las diez ciudades de más de 100.000 habitantes, los municipios
más ajustados y el reparto central del modelo de /encuestas/ para el 29N. Contexto: EFE (8 y 10-11-2026), Europa Press
(6-11-2026) y Telemadrid (reparto de escaños del BOE).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_madrid.py
"""
import json

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, s1, trazados)

A = BASE + 'actualidad/'
NW = {1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-madrid-29n'
CAJA = (-4.62, 39.86, -3.03, 41.18)
COL = dict(COL, FA=COL['SUMAR'], PODEMOS=COLOR['Podemos'])
NOMC = dict(NOM, EMPATE='Empate a votos', FA='Frente Amplio', PODEMOS='Podemos')

m = municipios(['28'])
NMUN = len(m)
assert NMUN == 179
NOMM = dict(zip(m.mun_code, m.municipio))
A19, A23 = agrega(m, Y19), agrega(m, Y23)
A19L = agrega(m, Y19, listas=('PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS'))
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 68, 'VOX': 61, 'PP': 46, 'UP': 3, 'EMPATE': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 158, 'PSOE': 19, 'SUMAR': 2}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
VOX_PP, PSOE_PP, PSOE_PSOE = TR('VOX', 'PP'), TR('PSOE', 'PP'), TR('PSOE', 'PSOE')
assert (VOX_PP, PSOE_PP, PSOE_PSOE) == (61, 48, 19)
PP_PIERDE = int(((m.g2019 == 'PP') & (m.g2023 != 'PP')).sum())
assert PP_PIERDE == 0           # el PP conservó los 46 municipios que ya ganaba
EMP19 = m[m.g2019 == 'EMPATE']
assert list(EMP19.municipio) == ['Puebla de la Sierra'] and list(EMP19.emp2019) == ['PP-PSOE']
SUM23 = m[m.g2023 == 'SUMAR'].sort_values('poblacion', ascending=False)
assert list(SUM23.municipio) == ['Bustarviejo', 'Torremocha de Jarama']
DPP = A23['pct']['PP'] - A19['pct']['PP']
DPP_VOTOS = A23['votos']['PP'] - A19['votos']['PP']
m['dPP'] = m[f'{Y23}%PP'] - m[f'{Y19}%PP']
PP_SUBE = int((m.dPP > 0).sum())
PP_MAS20 = int((m.dPP > 20).sum())
POB = {f: float(m[m.g2023 == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')}
POB_MAD = float(m[m.mun_code == '28079'].poblacion.iloc[0] / m.poblacion.sum() * 100)

# Los municipios de Vox en 2019
VX = m[m.g2019 == 'VOX']
VXS = {y: agrega(VX, y)['pct'] for y in (Y19, Y23)}
VXT = VX.sort_values('poblacion', ascending=False)
assert list(VXT.municipio[:4]) == ['Valdemoro', 'Arroyomolinos', 'Navalcarnero', 'Paracuellos de Jarama']
VX_SEG = VX.seg2019.value_counts().to_dict()
assert VX_SEG == {'PP': 32, 'PSOE': 29}
VX_MED = float(VX.marg2019.median())
VX_5K = int(((VX.poblacion >= 1000) & (VX.poblacion < 20000)).sum())
assert VX_5K == 51
assert (VX.g2023 == 'PP').all()

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
assert all(t['pp23'] > t['pp19'] and t['vox23'] < t['vox19'] and abs(t['psoe23'] - t['psoe19']) < 2 for t in TT.values())
assert TT['De 1.000 a 5.000']['g19']['VOX'] == 28 and TT['De 5.000 a 20.000']['g19']['VOX'] == 23

# La capital y las diez ciudades de más de 100.000 habitantes
MAD = m[m.mun_code == '28079'].iloc[0]
assert MAD.g2019 == 'PP' and MAD.g2023 == 'PP'
assert p(MAD[f'{Y23}%PSOE']) == p(MAD[f'{Y19}%PP'])   # «lo mismo que el PP en 2019», a un decimal
CIU = m[m.poblacion >= 100000].sort_values('poblacion', ascending=False)
assert len(CIU) == 10
CIU_PSOE19, CIU_PSOE23 = int((CIU.g2019 == 'PSOE').sum()), int((CIU.g2023 == 'PSOE').sum())
assert (CIU_PSOE19, CIU_PSOE23) == (8, 4)
assert sorted(CIU[CIU.g2023 == 'PSOE'].municipio) == ['Fuenlabrada', 'Getafe', 'Leganés', 'Parla']
assert sorted(CIU[(CIU.g2019 == 'PSOE') & (CIU.g2023 == 'PP')].municipio) == ['Alcalá de Henares', 'Alcorcón', 'Móstoles', 'Torrejón de Ardoz']
PSOE_GRANDES = sorted(m[(m.g2023 == 'PSOE') & (m.poblacion >= 20000)].municipio)
assert PSOE_GRANDES == ['Ciempozuelos', 'Fuenlabrada', 'Getafe', 'Leganés', 'Parla', 'San Fernando de Henares']

# Municipios ajustados en 2023
AJ2 = int((m.marg2023 < 2).sum())
AJG = m[(m.poblacion >= 20000) & (m.marg2023 < 5)].sort_values('marg2023')
assert len(AJG) == 10 and all({r.g2023, r.seg2023} == {'PP', 'PSOE'} for _, r in AJG.iterrows())
CIEM = m[m.municipio == 'Ciempozuelos'].iloc[0]
assert CIEM.g2023 == 'PSOE' and CIEM.seg2023 == 'PP' and int(CIEM.margv2023) == 4
# Coslada: nuestra descarga da 14.438 votos al PP; el resultado oficial publicado es 14.437 frente a 14.430 (Público)
COSLADA_OFICIAL = {'PP': 14437, 'PSOE': 14430}
COS = m[m.municipio == 'Coslada'].iloc[0]
assert COS.g2023 == 'PP' and int(COS['2023_07_vPSOE']) == COSLADA_OFICIAL['PSOE']
PUB_COS = 'https://www.publico.es/resultados-elecciones/generales/2023/comunidad-de-madrid/madrid/coslada'

# Escaños: oficiales de 2019 y 2023 (con voto exterior) y reparto central del modelo
ESC = escanos_oficiales(['28'])
E19, E23 = ESC[Y19]['28'], ESC[Y23]['28']
assert E19 == {'PSOE': 10, 'PP': 10, 'VOX': 7, 'UP': 5, 'CS': 3, 'MP': 2}, E19
assert E23 == {'PP': 16, 'PSOE': 10, 'SUMAR': 6, 'VOX': 5}, E23
assert ESC['2026']['28'] == 38
RC = reparto_central('madrid')
RC = {('FA' if k == 'SUMAR' else k): v for k, v in RC.items()}
E29 = {f: v[0] for f, v in RC.items()}
assert E29 == {'PP': 16, 'PSOE': 10, 'VOX': 8, 'FA': 3, 'PODEMOS': 1}, E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
# versión del modelo que se usa: la última archivada, que es la misma que escenario-base.json
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'
P1 = {l['lista']: l['p_primera'] for l in MOD['provincias']['28']['listas']}
assert max(P1, key=P1.get) == 'PP'

# --- Gráficos ---
cam, H = caminos(['28'], W=640, lat=40.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'UP', 'SUMAR', 'PP', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'Vox ganó en {GANA[Y19]["VOX"]} municipios madrileños en 2019 y en ninguno en 2023; el PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de la Comunidad de Madrid, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de la Comunidad de Madrid por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COL[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de la Comunidad de Madrid por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Ganador según los votos de cada candidatura: '
                  'en 2019, Unidas Podemos y Más País por separado (Más País no ganó en ninguno). En gris, Puebla de la Sierra, donde en 2019 '
                  'el PP y el PSOE empataron a votos.',
                  [(NOMC[f], COL[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023'],
                   [[NOMC[f], str(GANA[Y19].get(f, 0)), str(GANA[Y23].get(f, 0))] for f in ORDG]
                   + [['Total', str(NMUN), str(NMUN)]]))

TRAMOS = [(-99, 10, '#c5dcf2', 'menos de 10'), (10, 15, '#8fbbe6', '10 a 15'), (15, 20, '#4d8fd1', '15 a 20'),
          (20, 99, '#1d4f8f', '20 o más')]
DPPM = dict(zip(m.mun_code, m.dPP))
tramo = lambda v: next(c for a, b, c, _ in TRAMOS if a < v <= b)
NTR = {e: int(((m.dPP > a) & (m.dPP <= b)).sum()) for a, b, _, e in TRAMOS}
g_mapdpp = figura(f'El PP subió en {PP_SUBE} de los {NMUN} municipios',
                  'Cambio del voto al PP entre noviembre de 2019 y julio de 2023 en cada municipio, en puntos',
                  mapa_svg(cam, H, lambda k: tramo(DPPM[k]), lambda k: f'{s1(DPPM[k])} puntos', 'Subida del PP por municipio entre 2019 y 2023', NOMM),
                  'Fuente: Ministerio del Interior, resultados por municipio, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [(f'{e} puntos', c) for _, _, c, e in TRAMOS],
                  (['Subida del PP', 'Municipios'], [[f'{e} puntos', str(NTR[e])] for _, _, _, e in TRAMOS] + [['Total', str(NMUN)]]))

FV = ('VOX', 'PP', 'PSOE')
g_vox = figura(f'En los {GANA[Y19]["VOX"]} municipios que ganó Vox en 2019, el PP sacó el {p(VXS[Y23]["PP"])} % en 2023',
               'Voto a Vox, al PP y al PSOE en los municipios donde Vox fue el más votado en noviembre de 2019, en %. Barra clara: noviembre de 2019',
               grupos([(NOMC[f], [(VXS[Y19][f], COL[f], .38, 'nov. 2019'), (VXS[Y23][f], COL[f], 1, '2023')]) for f in FV],
                      50, 'Voto en los municipios que ganó Vox en 2019', W=440, ml=60),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. Cálculo propio.',
               [(NOMC[f], COL[f]) for f in FV] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(VXS[Y19][f]), p(VXS[Y23][f])] for f in FV]
                + [['Ciudadanos', p(VXS[Y19]['CS']), '—']]))

ORDT = ['PP', 'PSOE', 'SUMAR', 'EMPATE']
ORDT19 = ['PSOE', 'UP', 'PP', 'VOX', 'EMPATE']
g_tam = figura('Vox había ganado sobre todo en los municipios de 1.000 a 20.000 habitantes; en 2023, el PP ganó en casi todos los tamaños',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COL[f], NOMC[f]) for f in ORDT19 if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COL[f], NOMC[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COL[f]) for f in ['PP', 'PSOE', 'VOX', 'UP', 'SUMAR', 'EMPATE']],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'Vox 2019', 'PP 2019', 'PP 2023', 'PSOE 2023', 'Sumar 2023'],
                [[nom, str(t['n']), n(t['censo'])] + [str(t['g19'].get(f, 0)) for f in ('PSOE', 'VOX', 'PP')] + [str(t['g23'].get(f, 0)) for f in ('PP', 'PSOE', 'SUMAR')]
                 for nom, t in TT.items()]))

g_tampct = figura('El PP subió y Vox bajó en todos los tamaños de municipio; el PSOE se quedó casi igual',
                  'Voto al PP, al PSOE y a Vox en %, según la población del municipio. Barra clara: noviembre de 2019',
                  grupos([(nom, [(t['pp19'], COL['PP'], .38, 'PP, nov. 2019'), (t['pp23'], COL['PP'], 1, 'PP, 2023'),
                                 (t['psoe19'], COL['PSOE'], .38, 'PSOE, nov. 2019'), (t['psoe23'], COL['PSOE'], 1, 'PSOE, 2023'),
                                 (t['vox19'], COL['VOX'], .38, 'Vox, nov. 2019'), (t['vox23'], COL['VOX'], 1, 'Vox, 2023')]) for nom, t in TT.items()],
                         50, 'Voto al PP, al PSOE y a Vox según la población del municipio', W=440, ml=128),
                  'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                  [('PP', COL['PP']), ('PSOE', COL['PSOE']), ('Vox', COL['VOX']), ('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                  (['Población', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox nov. 2019 (%)', 'Vox 2023 (%)', 'Sumar 2023 (%)'],
                   [[nom, p(t['pp19']), p(t['pp23']), p(t['psoe19']), p(t['psoe23']), p(t['vox19']), p(t['vox23']), p(t['sumar23'])] for nom, t in TT.items()]))

g_ciu = figura(f'De las diez ciudades de más de 100.000 habitantes, el PSOE ganó en {NW[CIU_PSOE19]} en 2019 y en {NW[CIU_PSOE23]} en 2023',
               'Voto al PP y al PSOE en julio de 2023, en %, en los municipios de más de 100.000 habitantes',
               grupos([(r.municipio, [(r[f'{Y23}%{f}'], COL[f], 1, NOMC[f]) for f in ('PP', 'PSOE')]) for _, r in CIU.iterrows()],
                      50, 'Voto al PP y al PSOE en las ciudades de más de 100.000 habitantes en 2023', W=440, ml=118),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [('PP', COL['PP']), ('PSOE', COL['PSOE'])],
               (['Municipio', 'Ganador nov. 2019', 'Ganador 2023', 'PP nov. 2019 (%)', 'PP 2023 (%)', 'PSOE nov. 2019 (%)', 'PSOE 2023 (%)', 'Vox 2023 (%)', 'Sumar 2023 (%)'],
                [[r.municipio, NOMC[r.g2019], NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y23}%VOX']), p(r[f'{Y23}%SUMAR'])] for _, r in CIU.iterrows()]))

g_aj = figura(f'{NW[len(AJG)].capitalize()} municipios de más de 20.000 habitantes se decidieron en 2023 por menos de cinco puntos, todos entre el PP y el PSOE',
              'Ventaja del partido más votado sobre el segundo en julio de 2023, en puntos',
              barras([(r.municipio, r.marg2023, COL[r.g2023], f'{NOMC[r.g2023]} +{n(r.marg2023, 2)}') for _, r in AJG.iterrows()], 5.5,
                     'Municipios de más de 20.000 habitantes decididos por menos de cinco puntos', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COL[f]) for f in ('PP', 'PSOE')],
              (['Municipio', 'Ganó', 'Segundo', 'Ventaja (puntos)', 'Ganador nov. 2019'],
               [[r.municipio, NOMC[r.g2023], NOMC[r.seg2023], n(r.marg2023, 2), NOMC[r.g2019]] for _, r in AJG.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'SUMAR', 'UP', 'MP', 'FA', 'PODEMOS', 'PP', 'CS', 'VOX']


def hemi(lado=16, por_fila=19):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COL[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Madrid en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PP', 'PSOE', 'VOX', 'SUMAR', 'FA', 'PODEMOS', 'UP', 'MP', 'CS')
# listas que se presentaron en cada elección (las demás, «—»)
L19M, L23M, L29M = {'PP', 'PSOE', 'VOX', 'UP', 'MP', 'CS'}, {'PP', 'PSOE', 'VOX', 'SUMAR'}, {'PP', 'PSOE', 'VOX', 'FA', 'PODEMOS'}
g_esc = figura(f'Con las encuestas, el PP y el PSOE repetirían escaños y Vox pasaría de {E23["VOX"]} a {E29["VOX"]}',
               'Los diputados de Madrid: un cuadrado por escaño. En 2019 y 2023 eligió 37; el 29N elige 38',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/madrid/">/encuestas/madrid/</a>), {VERSION}. En el modelo, Frente Amplio continúa la serie de Sumar.',
               [(NOMC[f], COL[f]) for f in ORDE],
               (['Lista', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f]] + [str(e.get(f, 0)) if f in corre else '—' for e, corre in ((E19, L19M), (E23, L23M), (E29, L29M))]
                 + [f'{RC[f][1]}-{RC[f][2]}' if f in RC else '—'] for f in FT]
                + [['Total', str(sum(E19.values())), str(sum(E23.values())), str(sum(E29.values())), '']]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de la Comunidad de Madrid</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de la Comunidad de Madrid por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=28079">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/madrid/">datos de cada municipio de la Comunidad de Madrid</a></div>\n</figure>\n')

# --- Texto ---
EFE_LOP = 'https://www.infobae.com/espana/agencias/2026/11/08/oscar-lopez-augura-en-mayo-un-gobierno-en-madrid-que-defienda-la-educacion-publica/'
EP_AY = 'https://www.infobae.com/espana/agencias/2026/11/06/ayuso-augura-que-feijoo-cambiara-espana-de-raiz-desde-el-comienzo-y-eliminara-a-activistas-de-instituciones/'
TM = 'https://www.telemadrid.es/elecciones/generales/2026/madrid-gana-diputado-tendra-38_1_2714252.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
TP = TT['De 1.000 a 5.000']
TM5 = TT['De 5.000 a 20.000']

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La Comunidad de Madrid elige el 29 de noviembre 38 diputados, uno más que en 2023, según el reparto del real decreto de convocatoria publicado en el BOE que recoge <a href="{TM}">Telemadrid</a>. Es la circunscripción que más elige. Óscar López, secretario general del PSOE de Madrid, unió en la presentación de la candidatura socialista las dos citas, el 29N y las autonómicas de mayo: «Vamos a ganarles en España, pero vamos a ganarles también en Madrid», según <a href="{EFE_LOP}">EFE</a>.</p>
<blockquote class="cita"><p>«Tiene que haber una reforma porque los partidos reformistas tienen que ir a la raíz de los temas y volver a encauzar las cosas»</p><footer>Isabel Díaz Ayuso, presidenta de la Comunidad de Madrid, sobre lo que haría Feijóo si gobierna, en Telecinco el 6 de noviembre de 2026, según <a href="{EP_AY}">Europa Press</a></footer></blockquote>
<p data-tipo="dato">El mapa municipio a municipio cuenta cómo llegó el PP a esa posición. En noviembre de 2019, el PSOE fue el partido más votado en {GANA[Y19]["PSOE"]} de los {NMUN} municipios madrileños, Vox en {GANA[Y19]["VOX"]}, el PP en {GANA[Y19]["PP"]} y Unidas Podemos en {GANA[Y19]["UP"]}; en Puebla de la Sierra, el PP y el PSOE empataron a votos. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]}, el PSOE en {GANA[Y23]["PSOE"]} y Sumar en {GANA[Y23]["SUMAR"]}, Bustarviejo y Torremocha de Jarama. Vox no ganó en ninguno.</p>
{g_ins}
<p data-tipo="dato">El PP pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} % de los votos, {p(DPP)} puntos más, con {n(DPP_VOTOS)} votos más. Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó en 2023. Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. El PSOE subió algo, del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, y Sumar sacó el {p(A23["pct"]["SUMAR"])} %, por debajo de lo que sumaron en 2019 Unidas Podemos ({p(A19L["pct"]["UP"])} %) y Más País ({p(A19L["pct"]["MP"])} %). La participación apenas cambió: del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<p data-tipo="patron">Los {GANA[Y19]["VOX"]} municipios de Vox pasaron todos al PP, y también {PSOE_PP} de los {GANA[Y19]["PSOE"]} del PSOE. El PP conservó los {GANA[Y19]["PP"]} que ya tenía y subió en {PP_SUBE} de los {NMUN} municipios; en {PP_MAS20}, más de 20 puntos.</p>
{g_mapdpp}
<h2>Los pueblos que ganó Vox</h2>
<p data-tipo="dato">Vox no ganó en 2019 en la capital ni en las grandes ciudades, sino en municipios medianos y pequeños: {VX_5K} de sus {GANA[Y19]["VOX"]} tenían entre 1.000 y 20.000 habitantes. Los más poblados eran Valdemoro, Arroyomolinos, Navalcarnero y Paracuellos de Jarama. Fueron victorias ajustadas: la mitad, por menos de {p(VX_MED)} puntos, con el PP segundo en {VX_SEG["PP"]} y el PSOE en {VX_SEG["PSOE"]}. Sumados, Vox sacó allí el {p(VXS[Y19]["VOX"])} % en 2019 y el {p(VXS[Y23]["VOX"])} % en 2023; el PP pasó del {p(VXS[Y19]["PP"])} % al {p(VXS[Y23]["PP"])} %.</p>
{g_vox}
<p data-tipo="patron">El patrón se repite por tamaño. En los municipios de 1.000 a 5.000 habitantes, Vox había ganado en {TP["g19"]["VOX"]} de {TP["n"]} y el PP en {TP["g19"]["PP"]}; en 2023, el PP ganó en {TP["g23"]["PP"]}. En los de 5.000 a 20.000, Vox había ganado en {TM5["g19"]["VOX"]} de {TM5["n"]}; en 2023, el PP ganó en {TM5["g23"]["PP"]}. El PP subió y Vox bajó en todos los tamaños de municipio, mientras el PSOE se movió menos de dos puntos en cada uno.</p>
{g_tam}
{g_tampct}
<h2>La capital y el sur</h2>
<p data-tipo="dato">Madrid capital, donde vive el {p(POB_MAD)} % de la población de la Comunidad, la ganó el PP en las dos elecciones, con el {p(MAD[f"{Y19}%PP"])} % en 2019 y el {p(MAD[f"{Y23}%PP"])} % en 2023. El PSOE sacó en 2023 el {p(MAD[f"{Y23}%PSOE"])} %, lo mismo que el PP en 2019. Lo contamos sección a sección en {L("madrid-barrio-a-barrio-29n", "Madrid barrio a barrio")}. De las diez ciudades de más de 100.000 habitantes, el PSOE ganó en {NW[CIU_PSOE19]} en 2019 y en {NW[CIU_PSOE23]} en 2023: Leganés, Getafe, Fuenlabrada y Parla. Móstoles, Alcalá de Henares, Alcorcón y Torrejón de Ardoz pasaron al PP. Con los municipios del PP vive el {p(POB["PP"])} % de la población madrileña.</p>
{g_ciu}
<p data-tipo="contexto">Lo que queda del cinturón rojo, con la serie desde 1977 de los 24 municipios de más de 50.000 habitantes, está en {L("cinturon-rojo-madrid-29n", "El cinturón rojo")}.</p>
<h2>Dónde se decide por unos pocos votos</h2>
<p data-tipo="dato">En {AJ2} municipios madrileños, el primero sacó al segundo menos de dos puntos en 2023. Entre los de más de 20.000 habitantes, {NW[len(AJG)]} se decidieron por menos de cinco puntos, todos entre el PP y el PSOE. En Ciempozuelos, el PSOE ganó por {n(CIEM.margv2023)} votos; en Coslada, el PP ganó por siete, {n(COSLADA_OFICIAL["PP"])} frente a {n(COSLADA_OFICIAL["PSOE"])}, según los <a href="{PUB_COS}">resultados oficiales</a>.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 38 escaños da al PP {E29["PP"]}, los mismos que en 2023; al PSOE, {E29["PSOE"]}, también los mismos; a Vox, {E29["VOX"]}, {NW[E29["VOX"] - E23["VOX"]]} más; a Frente Amplio, {E29["FA"]}, y a Podemos, {E29["PODEMOS"]}. En 2023, Sumar había sacado {E23["SUMAR"]} con las dos candidaturas juntas. El PP es el más votado en el {n(P1["PP"] * 100)} % de las simulaciones.</p>
{g_esc}
<p data-tipo="contexto">A la izquierda del PSOE, Frente Amplio y Podemos se presentan por separado; qué pasaría con los escaños de Sumar si su voto se partiera lo calculamos en {L("frente-amplio-podemos-madrid-escanos-29n", "Delgado contra Montero en Madrid")}.</p>
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Vox o de Ciudadanos en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 18 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la Comunidad desde 1977, con las autonómicas, está en {L("madrid-historia-electoral", "Madrid en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/madrid/">la ficha de la Comunidad de Madrid</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en la Comunidad de Madrid?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %) y Vox ({p(A23["pct"]["VOX"])} %). '
     f'Sacó {E23["PP"]} de los 37 diputados; el PSOE, {E23["PSOE"]}; Sumar, {E23["SUMAR"]}, y Vox, {E23["VOX"]}.'),
    ('¿En cuántos municipios madrileños ganó el PP en 2023?',
     f'En {GANA[Y23]["PP"]} de {NMUN}; el PSOE, en {GANA[Y23]["PSOE"]}, y Sumar, en {GANA[Y23]["SUMAR"]}. En noviembre de 2019, el PP había ganado en {GANA[Y19]["PP"]}, el PSOE en {GANA[Y19]["PSOE"]} y Vox en {GANA[Y19]["VOX"]}.'),
    ('¿Cuántos diputados elige Madrid el 29N?',
     '38, uno más que en 2023, según el reparto del real decreto de convocatoria publicado en el BOE.'),
    ('¿Qué dicen las encuestas en Madrid?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]}, a Vox {E29["VOX"]}, a Frente Amplio {E29["FA"]} y a Podemos {E29["PODEMOS"]}, con un margen amplio.'),
]
enlaces = (f'{L("madrid-historia-electoral", "Historia electoral de Madrid")} · {L("madrid-barrio-a-barrio-29n", "Madrid barrio a barrio")} · '
           f'{L("cinturon-rojo-madrid-29n", "El cinturón rojo")} · <a href="{BASE}elecciones/madrid/">Datos de cada municipio</a> · <a href="{BASE}encuestas/madrid/">Encuesta en Madrid</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por municipio (sin voto exterior); resultado oficial de Coslada en 2023 (Público); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_madrid.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'A19L': A19L, 'GANA': GANA, 'VOX_PP': VOX_PP, 'PSOE_PP': PSOE_PP, 'PSOE_PSOE': PSOE_PSOE,
    'DPP': DPP, 'DPP_VOTOS': DPP_VOTOS, 'POB': POB, 'POB_MAD': POB_MAD, 'PP_SUBE': PP_SUBE, 'PP_MAS20': PP_MAS20, 'NTR': NTR,
    'VXS': VXS, 'VX_SEG': VX_SEG, 'VX_MED': VX_MED, 'VX_5K': VX_5K, 'TT': TT,
    'MAD': {f'{k.lower()}{y[2:4]}': R(MAD[f'{y}%{k}']) for k in ('PP', 'PSOE') for y in (Y19, Y23)},
    'CIU': [[r.municipio, r.g2019, r.g2023, R(r[f'{Y23}%PP']), R(r[f'{Y23}%PSOE'])] for _, r in CIU.iterrows()],
    'CIU_PSOE19': CIU_PSOE19, 'CIU_PSOE23': CIU_PSOE23,
    'AJ2': AJ2, 'AJG': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023)] for _, r in AJG.iterrows()],
    'CIEM': int(CIEM.margv2023), 'COSLADA': COSLADA_OFICIAL,
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026']['28'], 'RC': RC, 'P1': P1.get('PP'),
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de la Comunidad de Madrid',
      f'El mapa electoral de Madrid: Vox ganó en {GANA[Y19]["VOX"]} municipios en 2019 y en ninguno en 2023; el PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
      f'El PP ganó en {GANA[Y23]["PP"]} de los {NMUN} municipios madrileños en 2023, también en todos los que había ganado Vox; el PSOE resiste en Leganés, Getafe, Fuenlabrada y Parla. '
      f'Para el 29N, la media de encuestas da al PP {E29["PP"]} de los 38 diputados, y a Vox, {E29["VOX"]}.',
      '11 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('GANA', GANA, 'TR', VOX_PP, PSOE_PP, 'DPP', DPP, DPP_VOTOS, 'POB', POB, POB_MAD, 'VXS', VXS, VX_MED, 'E29', E29, 'AJ', AJ2, list(AJG.municipio), 'NTR', NTR, PP_SUBE, PP_MAS20, 'P1', P1)
