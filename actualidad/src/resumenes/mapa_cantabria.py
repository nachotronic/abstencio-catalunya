"""«El mapa electoral de Cantabria» (2026-11), pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 102 municipios de Cantabria en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno.
El PRC se presentó en 2019 (columna propia en las descargas) y no en 2023 ni el 29N; Unidas Podemos (2019) y Sumar (2023);
Más País no se presentó en Cantabria en 2019. Santander, Torrelavega y las ciudades, los municipios del PRC, los más
ajustados y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: listas del 29N (BOE del 28-10-2026) según elDiario Cantabria (Público) e ifomo. Sin citas literales en esas notas.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_cantabria.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-cantabria-29n'
PR = '39'
CAJA = (-4.86, 42.75, -3.14, 43.52)
COLC = dict(COL, PRC='#a8c11c')
NOMC = dict(NOM, PRC='PRC', EMPATE='Empate a votos')

m = municipios([PR])
NMUN = len(m)
assert NMUN == 102
# Población: padrón municipal a 1 de enero de 2023 (INE, tabla 2893), no la del Atlas de renta de las descargas, que en los
# pueblos más pequeños no cuadra (Tresviso: 5 en el Atlas, 58 en el padrón). datos/padron_2023_cantabria.csv.
PAD = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/padron_2023_cantabria.csv', dtype={'mun_code': str}).set_index('mun_code').padron_2023
assert PAD.sum() == 588419 and set(PAD.index) == set(m.mun_code)
m['poblacion'] = m.mun_code.map(PAD).astype(float)
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['39075'] == 'Santander' and NOMM['39087'] == 'Torrelavega' and NOMM['39008'] == 'El Astillero'
assert m[f'{Y19}_vMP'].sum() == 0 and m.get(f'{Y23}_vPRC', m[f'{Y23}_vCS'] * 0).sum() == 0 and m[f'{Y23}_vCS'].sum() == 0

L19, L23 = ('PP', 'PSOE', 'PRC', 'VOX', 'UP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
assert A19['votos'] == {'PP': 84158, 'PSOE': 75430, 'PRC': 68580, 'VOX': 48536, 'UP': 28075, 'CS': 15459}, A19['votos']
assert A23['votos'] == {'PP': 145994, 'PSOE': 115564, 'VOX': 48768, 'SUMAR': 29267}, A23['votos']
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PP': 55, 'PRC': 31, 'PSOE': 15, 'EMPATE': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 85, 'PSOE': 17}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
assert (TR('PRC', 'PP'), TR('PRC', 'PSOE'), TR('PSOE', 'PP'), TR('PP', 'PSOE'), TR('PSOE', 'PSOE')) == (25, 6, 5, 1, 10)
PRC_PP, PRC_PSOE = TR('PRC', 'PP'), TR('PRC', 'PSOE')
DV = {f: int(A23['votos'][f] - A19['votos'][f]) for f in ('PP', 'PSOE', 'VOX')}
assert DV == {'PP': 61836, 'PSOE': 40134, 'VOX': 232}, DV
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
assert PP_SUBE == NMUN and PSOE_SUBE == NMUN - 1
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE', 'PRC')} for y in (Y19, Y23)}
assert [round(POB[y][f], 1) for y in (Y19, Y23) for f in ('PP', 'PSOE', 'PRC')] == [62.7, 25.6, 11.5, 79.3, 20.7, 0.0], POB

# Los municipios del PRC
PRM = m[m.g2019 == 'PRC']
PRS = {y: agrega(PRM, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert PRS[Y23]['PP'] - PRS[Y19]['PP'] > PRS[Y23]['PSOE'] - PRS[Y19]['PSOE'] > 10, PRS
FUE = m.sort_values(f'{Y19}%PRC', ascending=False).head(10)
assert list(FUE.municipio[:2]) == ['Valderredible', 'Soba'] and set(FUE.g2019) == {'PRC'}
assert (FUE.g2023 == 'PP').sum() == 7, FUE.g2023

# Ciudades
MI_ = m.set_index('municipio')
STD, TOR, AST = MI_.loc['Santander'], MI_.loc['Torrelavega'], MI_.loc['El Astillero']
assert STD.g2019 == STD.g2023 == 'PP' and int(STD.margv2019) == 6512 and int(STD.margv2023) == 13259
assert TOR.g2019 == TOR.g2023 == 'PSOE' and TOR.seg2019 == 'PRC' and int(TOR.margv2019) == 1414 and int(TOR.margv2023) == 1590
assert AST.g2019 == 'PSOE' and AST.g2023 == 'PP' and int(AST.margv2023) == 5 and AST.seg2023 == 'PSOE'
GC = m[m.poblacion >= 10000].sort_values('poblacion', ascending=False)
assert len(GC) == 10 and list(GC[GC.g2023 == 'PSOE'].municipio) == ['Torrelavega', 'Castro-Urdiales', 'Los Corrales de Buelna']
LAR = MI_.loc['Laredo']
assert LAR.g2019 == 'PRC' and int(LAR.margv2019) == 69 and LAR.g2023 == 'PP'

# Ajustados
AJ = m.sort_values(['margv2023', 'poblacion'], ascending=[True, False]).head(8)
assert list(AJ.municipio[:2]) == ['Peñarrubia', 'El Astillero'] and [int(v) for v in AJ.margv2023[:2]] == [2, 5]
assert (AJ.g2019 == 'PRC').sum() == 4

# Escaños
ESC = escanos_oficiales([PR])
F5 = ('PP', 'PSOE', 'PRC', 'VOX', 'UP', 'SUMAR')
E19 = {f: ESC[Y19][PR].get(f, 0) for f in F5}
E23 = {f: ESC[Y23][PR].get(f, 0) for f in F5}
assert E19 == {'PP': 2, 'PSOE': 1, 'PRC': 1, 'VOX': 1, 'UP': 0, 'SUMAR': 0}, E19
assert E23 == {'PP': 2, 'PSOE': 2, 'PRC': 0, 'VOX': 1, 'UP': 0, 'SUMAR': 0}, E23
assert ESC['2026'] == {PR: 5}
RC = reparto_central('cantabria')
assert set(RC) <= set(F5)
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert E29 == {'PP': 2, 'PSOE': 2, 'PRC': 0, 'VOX': 1, 'UP': 0, 'SUMAR': 0} and RC['PP'] == (2, 2, 3) and RC['PSOE'] == (2, 1, 2), (E29, RC)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=43.2, umbral=1.2)
assert len(cam) == NMUN
ORDG = ['PP', 'PSOE', 'PRC', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PP pasó de ganar en {GANA[Y19]["PP"]} municipios a ganar en {GANA[Y23]["PP"]}; los {GANA[Y19]["PRC"]} del PRC, que no se presentó en 2023, fueron {PRC_PP} al PP y {PRC_PSOE} al PSOE',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Cantabria, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Cantabria por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Cantabria por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura; en gris, Rionansa, que en 2019 terminó en empate a votos entre el PP y el PSOE.',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0)), p(POB[Y19][f]), p(POB[Y23][f])] for f in ('PP', 'PSOE', 'PRC')]
                   + [['Empate a votos', n(GANA[Y19]['EMPATE']), '0', p(100 - sum(POB[Y19].values())), '0,0']]))

FF = ('PP', 'PSOE', 'PRC', 'VOX', 'CS')
g_prc = figura(f'En los {GANA[Y19]["PRC"]} municipios que ganó el PRC en 2019, el PP subió del {p(PRS[Y19]["PP"])} % al {p(PRS[Y23]["PP"])} %; el PSOE, del {p(PRS[Y19]["PSOE"])} % al {p(PRS[Y23]["PSOE"])} %',
               'Voto al PP, al PSOE, al PRC, a Vox y a Ciudadanos en los municipios que ganó el PRC en 2019, en %. Barra clara: noviembre de 2019',
               grupos([(NOMC[f], [(PRS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(PRS[Y23][f], COLC[f], 1, '2023')] if f in L23 else [])) for f in FF],
                      45, 'Voto en los municipios que ganó el PRC en 2019', W=440, ml=80),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos esos municipios sumados. '
               'El PRC y Ciudadanos no se presentaron en 2023. Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(PRS[Y19][f]), p(PRS[Y23][f]) if f in L23 else '—'] for f in FF]
                + [['Unidas Podemos (2019) / Sumar (2023)', p(PRS[Y19]['UP']), p(PRS[Y23]['SUMAR'])]]))

g_fue = figura(f'De los diez municipios donde más votó al PRC en 2019, {NW[int((FUE.g2023 == "PP").sum())]} fueron al PP en 2023',
               'Voto al PRC en noviembre de 2019 en los diez municipios donde más sacó, en %; el color es el del ganador en julio de 2023',
               barras([(r.municipio, r[f'{Y19}%PRC'], COLC[r.g2023], f'{p(r[f"{Y19}%PRC"])} % → {NOMC[r.g2023]}') for _, r in FUE.iterrows()],
                      80, 'Voto al PRC en 2019 y ganador en 2023', W=440, ml=165),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ('PP', 'PSOE')],
               (['Municipio', 'Habitantes', 'PRC 2019 (%)', 'Ganador 2023', 'PP 2019 (%)', 'PP 2023 (%)', 'PSOE 2019 (%)', 'PSOE 2023 (%)'],
                [[r.municipio, n(r.poblacion), p(r[f'{Y19}%PRC']), NOMC[r.g2023], p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE'])]
                 for _, r in FUE.iterrows()]))

FC = ('PP', 'PSOE', 'PRC')
g_cap = figura(f'El PP ganó El Astillero por {int(AST.margv2023)} votos en 2023; Santander, por {n(int(STD.margv2023))}, y el PSOE retuvo Torrelavega por {n(int(TOR.margv2023))}',
               'Voto al PP, al PSOE y al PRC en los diez municipios de más de 10.000 habitantes, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'),) + (((r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'),) if f != 'PRC' else ())])
                       for _, r in GC.iterrows()], 50, 'Voto en los diez municipios de más de 10.000 habitantes', W=440, ml=150),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. El PRC no se presentó en 2023. Población del padrón municipal de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (votos)', 'PP 2019 (%)', 'PP 2023 (%)', 'PSOE 2019 (%)', 'PSOE 2023 (%)', 'PRC 2019 (%)'],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], n(r.margv2023), p(r[f'{Y19}%PP']), p(r[f'{Y23}%PP']), p(r[f'{Y19}%PSOE']), p(r[f'{Y23}%PSOE']),
                  p(r[f'{Y19}%PRC'])] for _, r in GC.iterrows()]))

g_aj = figura(f'Peñarrubia fue para el PSOE por {int(AJ.iloc[0].margv2023)} votos, y El Astillero, con más de 18.000 habitantes, para el PP por {int(AJ.iloc[1].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho municipios más ajustados, en votos',
              barras([(r.municipio, r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.25,
                     'Municipios más ajustados en 2023, en votos', W=440, ml=165, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in ('PP', 'PSOE')],
              (['Municipio', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PRC', 'PP', 'VOX']


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
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_ * 2}px" role="img" aria-label="Escaños de Cantabria en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura('Con las encuestas, el reparto de 2023 se repetiría: dos diputados para el PP, dos para el PSOE y uno para Vox',
               'Los 5 diputados de Cantabria: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/cantabria/">/encuestas/cantabria/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Partido', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19[f]), str(E23[f]), str(E29[f]), f'{RC[f][1]}-{RC[f][2]}' if f in RC else '0'] for f in ('PP', 'PSOE', 'VOX', 'PRC')]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Cantabria</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Cantabria por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=39075">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/cantabria/">datos de cada municipio de Cantabria</a></div>\n</figure>\n')

# --- Texto ---
EDC = 'https://eldiariocantabria.publico.es/cantabria/politica/siete-partidos-presentan-candidaturas-cantabria-elecciones-generales/20261028201515200693.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Cantabria elige el 29 de noviembre 5 diputados entre siete candidaturas, dos menos que en 2023. El PP presenta a Isabel Urrutia; el PSOE, a Susana Herrán; Vox, a Emilio del Valle; Frente Amplio, a Carmen Martín, y Podemos, que va por separado, a Pablo Gómez, según la relación de las listas publicadas en el BOE de <a href="{EDC}">elDiario Cantabria</a>. Entre las siete no está el PRC, que en 2019 sacó un diputado y en 2023 tampoco se presentó a las generales. No hemos encontrado en esa nota declaraciones de los candidatos.</p>
<p data-tipo="dato">En noviembre de 2019, el PRC sacó el {p(A19["pct"]["PRC"])} % de los votos a candidaturas y fue el más votado en {GANA[Y19]["PRC"]} de los {NMUN} municipios. El PP ganó en {GANA[Y19]["PP"]}, entre ellos Santander, y el PSOE, en {GANA[Y19]["PSOE"]}, entre ellos Torrelavega. En julio de 2023, sin el PRC en la papeleta, el PP subió del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} % y ganó en {GANA[Y23]["PP"]} municipios; el PSOE, del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, y ganó en {GANA[Y23]["PSOE"]}. Vox se quedó casi igual, del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %.</p>
{g_ins}
<p data-tipo="dato">El PP subió en los {NMUN} municipios y el PSOE, en {PSOE_SUBE}. La participación pasó del {p(A19["part"])} % al {p(A23["part"])} %. Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, tampoco se presentó, y Sumar sacó el {p(A23["pct"]["SUMAR"])} %, frente al {p(A19["pct"]["UP"])} % de Unidas Podemos. Los municipios que ganó el PP en 2023 reúnen el {p(POB[Y23]["PP"])} % de la población.</p>
{g_mapgan}
<h2>Dónde estaba el PRC</h2>
<p data-tipo="patron">De los {GANA[Y19]["PRC"]} municipios que ganó el PRC en 2019, {PRC_PP} fueron al PP en 2023 y {PRC_PSOE} al PSOE. En esos {GANA[Y19]["PRC"]}, donde el PRC había sacado el {p(PRS[Y19]["PRC"])} %, el PP subió del {p(PRS[Y19]["PP"])} % al {p(PRS[Y23]["PP"])} % y el PSOE, del {p(PRS[Y19]["PSOE"])} % al {p(PRS[Y23]["PSOE"])} %. De los diez donde más votó al PRC, como Valderredible ({p(FUE.iloc[0][f"{Y19}%PRC"])} %) y Soba ({p(FUE.iloc[1][f"{Y19}%PRC"])} %), {NW[int((FUE.g2023 == "PP").sum())]} fueron al PP.</p>
{g_prc}
{g_fue}
<h2>Santander, Torrelavega y El Astillero</h2>
<p data-tipo="dato">El PP ganó Santander las dos veces: por {n(int(STD.margv2019))} votos sobre el PSOE en 2019 y por {n(int(STD.margv2023))} en 2023, con el {p(STD[f"{Y23}%PP"])} %. El PSOE ganó Torrelavega las dos veces, en 2019 por {n(int(TOR.margv2019))} votos sobre el PRC, que sacó allí el {p(TOR[f"{Y19}%PRC"])} %, y en 2023 por {n(int(TOR.margv2023))} sobre el PP. De los diez municipios de más de 10.000 habitantes, el PSOE ganó en 2023 Torrelavega, Castro-Urdiales y Los Corrales de Buelna, este último por {int(MI_.loc["Los Corrales de Buelna"].margv2023)} votos. El Astillero, que había sido del PSOE, pasó al PP por {int(AST.margv2023)} votos, y Laredo, que el PRC había ganado por {int(LAR.margv2019)}, también fue al PP.</p>
{g_cap}
<p data-tipo="dato">Además de El Astillero, otros municipios se decidieron por muy poco en 2023: Peñarrubia, por {int(AJ.iloc[0].margv2023)} votos para el PSOE, y, de los ocho más ajustados, {NW[int((AJ.g2019 == "PRC").sum())]} habían sido del PRC en 2019. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 5 escaños da al PP {NW[E29["PP"]]}, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}, como en 2023. La horquilla del PP llega a {NW[RC["PP"][2]]} y la del PSOE baja a {NW[RC["PSOE"][1]]}: el quinto escaño se lo disputan los dos.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen a quién votó en 2023 cada votante del PRC o de Ciudadanos. Que el PP y el PSOE subieran a la vez en casi todos los municipios cuando el PRC no se presentó encaja con que se repartieran sus votos, con más para el PP, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos pequeños, unos pocos votos cambian el ganador. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de Cantabria desde 1977, con las autonómicas, está en {L("cantabria-historia-electoral", "Cantabria en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/cantabria/">la ficha de Cantabria</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Cantabria?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     'Sacó dos de los 5 diputados; el PSOE, dos, y Vox, uno.'),
    ('¿Se presenta el PRC a las elecciones generales del 29N?',
     'No está entre las siete candidaturas al Congreso publicadas en el BOE. Tampoco se presentó en julio de 2023; en noviembre de 2019 sacó un diputado.'),
    ('¿En cuántos municipios de Cantabria ganó el PP en 2023?',
     f'En {GANA[Y23]["PP"]} de {NMUN}; el PSOE, en {GANA[Y23]["PSOE"]}. En noviembre de 2019, el PP había ganado en {GANA[Y19]["PP"]}, el PRC en {GANA[Y19]["PRC"]} y el PSOE en {GANA[Y19]["PSOE"]}.'),
    ('¿Quién ganó en Santander y en Torrelavega?',
     f'En julio de 2023, el PP ganó en Santander por {n(int(STD.margv2023))} votos y el PSOE en Torrelavega por {n(int(TOR.margv2023))}. Los dos habían ganado también en 2019.'),
    ('¿Cuántos diputados elige Cantabria el 29N?',
     '5, los mismos que en 2023.'),
]
enlaces = (f'{L("cantabria-historia-electoral", "Historia electoral de Cantabria")} · <a href="{BASE}elecciones/cantabria/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/cantabria/">Encuesta en Cantabria</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón municipal de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_cantabria.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PRC_PP': PRC_PP, 'PRC_PSOE': PRC_PSOE, 'DV': DV, 'PP_SUBE': PP_SUBE, 'PSOE_SUBE': PSOE_SUBE,
    'POB': POB, 'PRS': PRS, 'NMUN': NMUN,
    'FUE': [[r.municipio, R(r[f'{Y19}%PRC']), r.g2023] for _, r in FUE.iterrows()],
    'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv19': int(r.margv2019), 'margv23': int(r.margv2023), 'pp23': R(r[f'{Y23}%PP']), 'prc19': R(r[f'{Y19}%PRC'])} for _, r in GC.iterrows()},
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023), r.g2019] for _, r in AJ.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Cantabria',
      f'El mapa electoral de Cantabria: sin el PRC en la papeleta, el PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]} municipios y ganó El Astillero por {int(AST.margv2023)} votos',
      f'El PRC ganó en {GANA[Y19]["PRC"]} municipios en 2019 y no se presentó en 2023: {PRC_PP} fueron al PP y {PRC_PSOE} al PSOE. Tampoco está en las listas del 29N. '
      f'La media de encuestas da al PP {NW[E29["PP"]]} de los 5 diputados, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
