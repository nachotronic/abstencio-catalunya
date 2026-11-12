"""«El mapa electoral de La Rioja» (2026-11), pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 174 municipios de La Rioja en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(Unidas Podemos en 2019 y Sumar en 2023; Más País no se presentó en La Rioja en 2019 y no hubo listas regionales con votos
apreciables), Logroño y las ciudades, el tamaño de los municipios, los más ajustados y el reparto central del modelo de
/encuestas/ para el 29N.
Contexto: listas del 29N según COPE La Rioja (26-10-2026), Europa Press en elDiario.es (21-10-2026) y el BOE (Frente Amplio); cita de Gamarra en Europa Press (8-11-2026).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_la_rioja.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-la-rioja-29n'
PR = '26'
CAJA = (-3.16, 41.9, -1.66, 42.66)
COLC = dict(COL)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios([PR])
NMUN = len(m)
assert NMUN == 174
# Población: padrón municipal a 1 de enero de 2023 (INE, tabla 2879), no la del Atlas de renta de las descargas, que en los
# pueblos más pequeños no cuadra. datos/padron_2023_la_rioja.csv.
PAD = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/padron_2023_la_rioja.csv', dtype={'mun_code': str}).set_index('mun_code').padron_2023
assert PAD.sum() == 322490 and set(PAD.index) == set(m.mun_code)
m['poblacion'] = m.mun_code.map(PAD).astype(float)
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['26089'] == 'Logroño' and NOMM['26071'] == 'Haro' and NOMM['26154'] == 'Torremontalbo'
assert m[f'{Y19}_vMP'].sum() == 0 and m[f'{Y23}_vCS'].sum() == 0

L19, L23 = ('PP', 'PSOE', 'VOX', 'UP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
assert A19['votos'] == {'PP': 56208, 'PSOE': 57193, 'VOX': 18772, 'UP': 16119, 'CS': 11584}, A19['votos']
assert A23['votos'] == {'PP': 79113, 'PSOE': 61862, 'VOX': 16876, 'SUMAR': 11309}, A23['votos']
V19 = A19['votos']['PSOE'] - A19['votos']['PP']
assert V19 == 985
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PP': 108, 'PSOE': 61, 'EMPATE': 5}, GANA[Y19]
assert GANA[Y23] == {'PP': 138, 'PSOE': 33, 'EMPATE': 2, 'VOX': 1}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP = TR('PSOE', 'PP')
assert (PSOE_PP, TR('PP', 'PSOE'), TR('PSOE', 'PSOE')) == (31, 3, 29)
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
assert PP_SUBE == 149 and PSOE_SUBE == 80
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert [round(POB[y][f], 1) for y in (Y19, Y23) for f in ('PSOE', 'PP')] == [71.6, 28.3, 5.5, 94.3], POB
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Logroño y las ciudades
MI_ = m.set_index('municipio')
LOG, HAR, TOM = MI_.loc['Logroño'], MI_.loc['Haro'], MI_.loc['Torremontalbo']
assert LOG.g2019 == 'PSOE' and LOG.seg2019 == 'PP' and int(LOG.margv2019) == 1568 and LOG.g2023 == 'PP' and int(LOG.margv2023) == 6822
assert HAR.g2019 == HAR.g2023 == 'PSOE' and int(HAR.margv2023) == 139
assert TOM.g2023 == 'VOX' and int(TOM.margv2023) == 1 and TOM.poblacion < 10
GC = m[m.poblacion >= 5000].sort_values('poblacion', ascending=False)
assert len(GC) == 9 and list(GC[GC.g2023 == 'PSOE'].municipio) == ['Haro'] and (GC.g2019 == 'PSOE').sum() == 5
LOGP = int(LOG.poblacion)
LOGS = LOG.poblacion / m.poblacion.sum() * 100
assert 45 < LOGS < 50, LOGS

# Tamaño
TAM = [('Menos de 500', 0, 500), ('De 500 a 5.000', 500, 5000), ('Más de 5.000', 5000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a23 = agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g19': g.g2019.value_counts().to_dict(), 'g23': g.g2023.value_counts().to_dict(),
               'pp23': a23['PP'], 'psoe23': a23['PSOE']}
assert sum(t['n'] for t in TT.values()) == NMUN
TM = TT['De 500 a 5.000']
assert TM['g19'] == {'PP': 19, 'PSOE': 12} and TM['g23'] == {'PP': 28, 'PSOE': 2, 'EMPATE': 1}, TM

# Ajustados
AJ = m.sort_values(['margv2023', 'poblacion'], ascending=[True, False]).head(12)
UNO = m[m.margv2023 == 1]
assert len(UNO) == 10 and UNO.poblacion.max() < 500
EMP23 = m[m.g2023 == 'EMPATE']
assert sorted(EMP23.municipio) == ['Baños de Rioja', 'Cuzcurrita de Río Tirón']

# Escaños
ESC = escanos_oficiales([PR])
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')
E19 = {f: ESC[Y19][PR].get(f, 0) for f in F5}
E23 = {f: ESC[Y23][PR].get(f, 0) for f in F5}
assert E19 == E23 == {'PP': 2, 'PSOE': 2, 'VOX': 0, 'UP': 0, 'SUMAR': 0}, (E19, E23)
assert ESC['2026'] == {PR: 4}
RC = reparto_central('la-rioja')
assert set(RC) <= set(F5)
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert E29 == {'PP': 2, 'PSOE': 1, 'VOX': 1, 'UP': 0, 'SUMAR': 0} and RC['VOX'] == (1, 0, 1) and RC['PSOE'] == (1, 1, 2), (E29, RC)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=42.3, umbral=1.2)
assert len(cam) == NMUN
ORDG = ['PP', 'PSOE', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PP pasó de ganar en {GANA[Y19]["PP"]} municipios a ganar en {GANA[Y23]["PP"]}; el PSOE, de {GANA[Y19]["PSOE"]} a {GANA[Y23]["PSOE"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de La Rioja, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de La Rioja por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de La Rioja por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  f'votos de cada candidatura; en gris, los municipios con empate a votos entre los dos primeros ({GANA[Y19]["EMPATE"]} en 2019 y {GANA[Y23]["EMPATE"]} en 2023).',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] + ([p(POB[Y19][f]), p(POB[Y23][f])] if f in POB[Y19] else ['', '']) for f in ORDG]
                   + [['Todos los municipios', n(NMUN), n(NMUN), '100,0', '100,0']]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %; el PP, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       50, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos esos municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos (2019) / Sumar (2023)', p(FLS[Y19]['UP']), p(FLS[Y23]['SUMAR'])]]))

FC = ('PP', 'PSOE', 'VOX')
g_cap = figura(f'El PSOE ganó Logroño por {n(int(LOG.margv2019))} votos en 2019 y el PP, por {n(int(LOG.margv2023))} en 2023; de las nueve ciudades, el PSOE solo conservó Haro',
               'Voto al PP, al PSOE y a Vox en los nueve municipios de más de 5.000 habitantes, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in GC.iterrows()], 50, 'Voto en los nueve municipios de más de 5.000 habitantes', W=460, ml=195),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del padrón municipal de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Habitantes', 'Ganador nov. 2019', 'Ventaja 2019 (votos)', 'Ganador 2023', 'Ventaja 2023 (votos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], n(r.margv2019), NOMC[r.g2023], n(r.margv2023)] + [p(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)] for _, r in GC.iterrows()]))

ORDT = ['PP', 'PSOE', 'VOX', 'EMPATE']
g_tam = figura(f'En los {TM["n"]} municipios de 500 a 5.000 habitantes, el PSOE pasó de ganar en {TM["g19"]["PSOE"]} a ganar en {TM["g23"]["PSOE"]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDT if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDT if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=160),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDT],
               (['Población', 'Municipios', 'Electores (2023)', 'PP 2019', 'PSOE 2019', 'PP 2023', 'PSOE 2023', 'PP 2023 (%)', 'PSOE 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PP', 'PSOE')] + [n(t['g23'].get(f, 0)) for f in ('PP', 'PSOE')]
                 + [p(t['pp23']), p(t['psoe23'])] for nom, t in TT.items()]))

AJF = AJ[AJ.margv2023 > 0].head(10)
g_aj = figura(f'{NW[len(UNO)].capitalize()} municipios se decidieron por un solo voto en 2023; Torremontalbo, con {int(TOM.poblacion)} habitantes, fue el único que ganó Vox',
              'Municipios de La Rioja que se decidieron por un voto en julio de 2023, y su población',
              barras([(r.municipio, r.poblacion, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)} · {n(r.poblacion)} hab.') for _, r in UNO.sort_values('poblacion', ascending=False).iterrows()],
                     max(UNO.poblacion) * 1.6, 'Municipios ganados por un voto en 2023, por población', W=440, ml=175),
              f'Fuente: Ministerio del Interior, sin voto exterior; padrón municipal de 2023 (INE). Cálculo propio. La barra es la población y el color, el del ganador. '
              f'Además, {" y ".join(sorted(EMP23.municipio))} terminaron en empate a votos entre el PP y el PSOE.',
              [(NOMC[f], COLC[f]) for f in ('PP', 'PSOE', 'VOX')],
              (['Municipio', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in UNO.sort_values('poblacion', ascending=False).iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX']


def hemi(lado=16, por_fila=4):
    W_, out, y = 12 * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_ * 2}px" role="img" aria-label="Escaños de La Rioja en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura('Con las encuestas, Vox le quitaría al PSOE su segundo diputado por La Rioja',
               'Los 4 diputados de La Rioja: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/la-rioja/">/encuestas/la-rioja/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Partido', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19[f]), str(E23[f]), str(E29[f]), f'{RC[f][1]}-{RC[f][2]}' if f in RC else '0'] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de La Rioja</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de La Rioja por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=26089">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/la-rioja/">datos de cada municipio de La Rioja</a></div>\n</figure>\n')

# --- Texto ---
COPE = 'https://www.cope.es/emisoras/la-rioja/la-rioja-provincia/logrono/noticias/candidaturas-29n-rioja-pp-incorpora-galiana-psoe-cambia-lista-senado-20261026_3462835.html'
EPG = 'https://www.europapress.tv/politica/1132071/1/gamarra-pp-29-noviembre-vamos-decir-fin-fin-sanchismo'
EP = 'https://www.eldiario.es/la-rioja/angel-alda-sera-numero-lista-vox-elecciones-generales-rioja_1_13604417.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La Rioja elige el 29 de noviembre 4 diputados. El PP presenta a Cuca Gamarra, con Alberto Galiana de número dos; el PSOE, a Elisa Garrido; Vox, a Ángel Alda; el Frente Amplio, a Alba Díez Arrea, y Podemos, que va por separado del PSOE y del Frente Amplio, a Arantxa Carrero, según <a href="{COPE}">COPE La Rioja</a>, <a href="{EP}">Europa Press</a> y la <a href="{BASE}listas-electorales-29n/la-rioja/">lista proclamada en el BOE</a>. En un acto en Logroño el 8 de noviembre, Gamarra dijo que «el 29 de noviembre, La Rioja va a votar cambio», según <a href="{EPG}">Europa Press</a>.</p>
<p data-tipo="dato">En noviembre de 2019, el PSOE fue el partido más votado en La Rioja, con {n(V19)} votos más que el PP (sin el voto exterior), y ganó Logroño por {n(int(LOG.margv2019))}. Los {GANA[Y19]["PSOE"]} municipios que ganó reunían el {p(POB[Y19]["PSOE"])} % de la población; los {GANA[Y19]["PP"]} del PP, el {p(POB[Y19]["PP"])} %. En julio de 2023, el PP subió del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} % y ganó en {GANA[Y23]["PP"]} municipios, con el {p(POB[Y23]["PP"])} % de la población. Logroño pasó al PP por {n(int(LOG.margv2023))} votos. El PSOE también subió, del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, pero se quedó en {GANA[Y23]["PSOE"]} municipios.</p>
{g_ins}
<p data-tipo="dato">Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó en 2023, y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. Sumar sacó el {p(A23["pct"]["SUMAR"])} %, frente al {p(A19["pct"]["UP"])} % de Unidas Podemos. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. Los dos partidos grandes quedaron igual en escaños: dos cada uno, en 2019 y en 2023.</p>
{g_mapgan}
<p data-tipo="patron">{PSOE_PP} municipios pasaron del PSOE al PP, y {NW[TR("PP", "PSOE")]} hicieron el camino contrario. En esos {PSOE_PP}, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP subió más, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %.</p>
{g_flip}
<h2>Logroño y las ciudades</h2>
<p data-tipo="dato">Logroño, con {n(LOGP)} habitantes, reúne el {p(LOGS)} % de la población de La Rioja. En 2019, el PSOE sacó allí el {p(LOG[f"{Y19}%PSOE"])} % y el PP, el {p(LOG[f"{Y19}%PP"])} %; en 2023, el PP subió al {p(LOG[f"{Y23}%PP"])} % y el PSOE, al {p(LOG[f"{Y23}%PSOE"])} %. De los nueve municipios de más de 5.000 habitantes, el PSOE había ganado cinco en 2019; en 2023 solo conservó Haro, por {int(HAR.margv2023)} votos. Arnedo, Alfaro y Villamediana de Iregua pasaron al PP, como Logroño.</p>
{g_cap}
<h2>Los pueblos</h2>
<p data-tipo="patron">En los {TM["n"]} municipios de 500 a 5.000 habitantes, el PSOE pasó de ganar en {TM["g19"]["PSOE"]} a ganar en {TM["g23"]["PSOE"]}. En los {TT["Menos de 500"]["n"]} de menos de 500, donde el PSOE conservó más, ganó en {TT["Menos de 500"]["g23"]["PSOE"]}. Muchos se decidieron por muy poco. En 2023, {NW[len(UNO)]} se ganaron por un solo voto: {NW[UNO.g2023.value_counts()["PP"]]} para el PP, {NW[UNO.g2023.value_counts()["PSOE"]]} para el PSOE y uno, Torremontalbo, de {int(TOM.poblacion)} habitantes, para Vox, el único municipio riojano que ganó. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_tam}
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 4 escaños da al PP {NW[E29["PP"]]}, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}: Vox le quitaría al PSOE el segundo diputado que tuvo en 2019 y en 2023. La horquilla del PSOE llega a {NW[RC["PSOE"][2]]} y la de Vox baja a {NW[RC["VOX"][1]]}: con solo 4 escaños, el último se decide por poco.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera en {PP_SUBE} de los {NMUN} municipios a la vez que desaparecía Ciudadanos encaja con que recogiera buena parte de sus votos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos pequeños, un voto cambia el ganador. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de La Rioja desde 1977, con las autonómicas, está en {L("la-rioja-historia-electoral", "La Rioja en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/la-rioja/">la ficha de La Rioja</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en La Rioja?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     'El PP y el PSOE sacaron dos de los 4 diputados cada uno. En noviembre de 2019 el más votado había sido el PSOE.'),
    ('¿En cuántos municipios de La Rioja ganó el PP en 2023?',
     f'En {GANA[Y23]["PP"]} de {NMUN}; el PSOE, en {GANA[Y23]["PSOE"]}, y Vox, en uno. {NW[GANA[Y23]["EMPATE"]].capitalize()} terminaron en empate. En noviembre de 2019, el PP había ganado en {GANA[Y19]["PP"]} y el PSOE en {GANA[Y19]["PSOE"]}.'),
    ('¿Quién ganó en Logroño?',
     f'En julio de 2023, el PP, por {n(int(LOG.margv2023))} votos sobre el PSOE. En noviembre de 2019 había ganado el PSOE, por {n(int(LOG.margv2019))}.'),
    ('¿Cuántos diputados elige La Rioja el 29N?',
     '4, los mismos que en 2023.'),
    ('¿Qué dicen las encuestas en La Rioja?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("la-rioja-historia-electoral", "Historia electoral de La Rioja")} · <a href="{BASE}elecciones/la-rioja/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/la-rioja/">Encuesta en La Rioja</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón municipal de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_la_rioja.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'V19': V19, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PP_PSOE': TR('PP', 'PSOE'), 'LOGP': LOGP, 'LOGS': R(LOGS), 'PP_SUBE': PP_SUBE, 'PSOE_SUBE': PSOE_SUBE, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv19': int(r.margv2019), 'margv23': int(r.margv2023), **{f'{f.lower()}{y[2:4]}': R(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)}} for _, r in GC.iterrows()},
    'UNO': [[r.municipio, r.g2023, r.seg2023, int(r.poblacion)] for _, r in UNO.iterrows()], 'EMP23': sorted(EMP23.municipio),
    'E19': E19, 'E23': E23, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de La Rioja',
      f'El mapa electoral de La Rioja: el PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]} municipios y ganó Logroño por {n(int(LOG.margv2023))} votos; con las encuestas, Vox le quitaría un diputado al PSOE',
      f'En 2019 el PSOE fue el más votado en La Rioja y ganó Logroño; en 2023 solo conservó Haro entre las nueve ciudades. {NW[len(UNO)].capitalize()} pueblos se decidieron por un voto. '
      f'Para el 29N, la media de encuestas da al PP {NW[E29["PP"]]} de los 4 diputados, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
