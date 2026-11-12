"""«El mapa electoral de las Illes Balears» (2026-11), decimotercera pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 67 municipios de Baleares en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas
por separado: en 2019, Unidas Podemos y Más País), las islas (Mallorca, Menorca, Eivissa y Formentera), el tamaño de
los municipios (población del Atlas de renta del INE, 2023), las 11 ciudades de más de 30.000 habitantes, los municipios de Sumar y los más
ajustados, y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: EFE vía Última Hora (12-11-2026) y Última Hora (26-10-2026), cabezas de lista. Sin citas literales en esas notas.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_baleares.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez', 11: 'once'}
SLUG = 'mapa-electoral-baleares-29n'
PR = '07'
CAJA = (1.1, 38.6, 4.4, 40.15)
COLC = dict(COL)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios([PR])
NMUN = len(m)
assert NMUN == 67
NOMM = dict(zip(m.mun_code, m.municipio))
ISLA = {'Mallorca': None,
        'Menorca': ['07002', '07015', '07023', '07032', '07037', '07052', '07064', '07902'],
        'Eivissa': ['07026', '07046', '07048', '07050', '07054'],
        'Formentera': ['07024']}
assert [NOMM[k] for k in ISLA['Menorca']] == ['Alaior', 'Ciutadella de Menorca', 'Ferreries', 'Maó', 'Mercadal, Es', 'Sant Lluís', 'Castell, Es', 'Migjorn Gran, Es']
assert [NOMM[k] for k in ISLA['Eivissa']] == ['Eivissa', 'Sant Antoni de Portmany', 'Sant Josep de sa Talaia', 'Sant Joan de Labritja', 'Santa Eulària des Riu']
ISLA['Mallorca'] = sorted(set(m.mun_code) - {x for v in ISLA.values() if v for x in v})
m['isla'] = m.mun_code.map({x: k for k, v in ISLA.items() for x in v})
assert m.isla.value_counts().to_dict() == {'Mallorca': 53, 'Menorca': 8, 'Eivissa': 5, 'Formentera': 1}

L19, L23 = ('PSOE', 'PP', 'VOX', 'UP', 'MP', 'MES', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')   # 2019: Més-Esquerra fue por su cuenta (en 2023, dentro de Sumar)
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 32, 'PP': 30, 'UP': 4, 'EMPATE': 1}, GANA[Y19]
assert GANA[Y23] == {'PP': 54, 'PSOE': 10, 'SUMAR': 3}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, PP_PP, UP_PP = TR('PSOE', 'PP'), TR('PP', 'PP'), TR('UP', 'PP')
assert (PSOE_PP, PP_PP, UP_PP, TR('PP', 'PSOE')) == (21, 30, 3, 0)
DV = {f: int(A23['votos'][f] - A19['votos'][f]) for f in ('PP', 'PSOE', 'VOX')}
assert DV == {'PP': 75101, 'PSOE': 35756, 'VOX': -1095}, DV
assert A23['part'] > A19['part'] and m[f'{Y23}_vCS'].sum() == 0
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
assert PSOE_SUBE == 64 and PP_SUBE == NMUN
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert [round(POB[y][f], 1) for y in (Y19, Y23) for f in ('PSOE', 'PP')] == [78.3, 20.1, 9.2, 90.1], POB
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
IZQ19 = A19['pct']['UP'] + A19['pct']['MP'] + A19['pct']['MES']
assert round(A19['pct']['MES'], 1) == 4.1 and round(IZQ19, 1) == 24.7, IZQ19   # de votos brutos (18,3 + 2,4 + 4,1 redondeados darían 24,8)
assert 'MES' not in set(m.g2019)
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Islas
IS = {i: {y: agrega(m[m.isla == i], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for i in ISLA}
ISG = {i: {y: m[m.isla == i][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for i in ISLA}
assert ISG['Eivissa'][Y23] == {'PP': 5} and ISG['Menorca'][Y19] == {'PP': 4, 'PSOE': 4} and ISG['Menorca'][Y23] == {'PP': 5, 'PSOE': 3}
assert ISG['Mallorca'][Y19] == {'PSOE': 24, 'PP': 24, 'UP': 4, 'EMPATE': 1} and ISG['Mallorca'][Y23] == {'PP': 43, 'PSOE': 7, 'SUMAR': 3}
PRIM = {y: {i: max(IS[i][y]['pct'], key=IS[i][y]['pct'].get) for i in ISLA} for y in (Y19, Y23)}
assert set(PRIM[Y19].values()) == {'PSOE'} and set(PRIM[Y23].values()) == {'PP'}
assert max(ISLA, key=lambda i: IS[i][Y23]['pct']['SUMAR']) == 'Menorca'

# Tamaño
TAM = [('Menos de 2.000', 0, 2000), ('De 2.000 a 10.000', 2000, 10000), ('De 10.000 a 30.000', 10000, 30000), ('Más de 30.000', 30000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'UP')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
TG = TT['Más de 30.000']
assert TG['n'] == 11 and TG['g19'] == {'PSOE': 9, 'PP': 2} and TG['g23'] == {'PP': 10, 'PSOE': 1}, TG
GC = m[m.poblacion >= 30000].sort_values('poblacion', ascending=False)
assert list(GC[GC.g2023 == 'PSOE'].municipio) == ['Maó'] and set(GC[GC.g2019 == 'PP'].municipio) == {'Santa Eulària des Riu', 'Ciutadella de Menorca'}
GI = GC.set_index('municipio')
PAL, MAO = GI.loc['Palma'], GI.loc['Maó']
assert PAL.g2019 == 'PSOE' and PAL.g2023 == 'PP' and int(PAL.margv2023) == 7658 and int(MAO.margv2023) == 170

# Sumar y ajustados
SU = m[m.g2023 == 'SUMAR'].set_index('municipio')
assert sorted(SU.index) == ['Campanet', 'Deià', 'Esporles'] and SU.loc['Deià'].g2019 == 'EMPATE' and SU.loc['Esporles'].g2019 == 'UP'
assert int(SU.loc['Deià'].margv2023) == 12 and int(SU.loc['Campanet'].margv2023) == 39 and SU.loc['Campanet'].g2019 == 'PSOE'
UP19 = sorted(m[m.g2019 == 'UP'].municipio)
AJ = m.sort_values('margv2023').head(8)
assert list(AJ.municipio[:3]) == ['Deià', 'Migjorn Gran, Es', 'Santa Eugènia'] and [int(v) for v in AJ.margv2023[:3]] == [12, 13, 19]

# Escaños
ESC = escanos_oficiales([PR])
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')
E19 = {f: ESC[Y19][PR].get(f, 0) for f in F5}
E23 = {f: ESC[Y23][PR].get(f, 0) for f in F5}
assert E19 == {'PP': 2, 'PSOE': 2, 'VOX': 2, 'UP': 2, 'SUMAR': 0}, E19
assert E23 == {'PP': 3, 'PSOE': 3, 'VOX': 1, 'UP': 0, 'SUMAR': 1}, E23
assert ESC['2026'] == {PR: 8}
RC = reparto_central('illes-balears')
assert set(RC) <= set(F5)
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert E29 == {'PP': 3, 'PSOE': 3, 'VOX': 2, 'UP': 0, 'SUMAR': 0} and RC['SUMAR'] == (0, 0, 1), (E29, RC)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=39.5, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP', 'UP', 'SUMAR', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de las Illes Balears, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Baleares por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Baleares por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura. En gris, Deià en 2019, donde el PSOE y Unidas Podemos empataron a votos.',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], '—' if f == 'SUMAR' else n(GANA[Y19].get(f, 0)), '—' if f == 'UP' else n(GANA[Y23].get(f, 0))] + ([p(POB[Y19][f]), p(POB[Y23][f])] if f in ('PP', 'PSOE') else ['—', '—']) for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN), '', '']]))
assert m.set_index('municipio').loc['Deià'].emp2019 == 'PSOE-UP'

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. En 2019, Més-Esquerra fue por su cuenta; en 2023, dentro de Sumar. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos, Más País y Més-Esquerra (2019) / Sumar (2023)', p(FLS[Y19]['UP'] + FLS[Y19]['MP'] + FLS[Y19]['MES']), p(FLS[Y23]['SUMAR'])]]))

ORDI = list(ISLA)
g_isla = figura('En 2019, el PSOE fue el más votado en las cuatro islas; en 2023, el PP',
                'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, por isla',
                apiladas([(f'{i} · {y[:4]}', [(ISG[i][y].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if ISG[i][y].get(f, 0)]) for i in ORDI for y in (Y19, Y23)],
                         'Municipios ganados por cada partido en cada isla', W=440, ml=130),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in ORDG],
                (['Isla', 'Municipios', 'PSOE 2019 (%)', 'PP 2019 (%)', 'PP 2023 (%)', 'PSOE 2023 (%)', 'Sumar 2023 (%)', 'Vox 2023 (%)'],
                 [[i, n(len(ISLA[i])), p(IS[i][Y19]['pct']['PSOE']), p(IS[i][Y19]['pct']['PP'])] + [p(IS[i][Y23]['pct'][f]) for f in ('PP', 'PSOE', 'SUMAR', 'VOX')] for i in ORDI]))

g_tam = figura(f'De las {TG["n"]} ciudades de más de 30.000 habitantes, el PSOE ganó en {NW[TG["g19"]["PSOE"]]} en 2019 y solo en Maó en 2023',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=180),
               'Fuente: Ministerio del Interior, sin voto exterior; población del Atlas de distribución de renta de los hogares del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'PSOE 2023', 'PP 2023', 'PSOE 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'PP')]
                 + [p(t['psoe23']), p(t['pp23'])] for nom, t in TT.items()]))

FC = ('PP', 'PSOE', 'VOX')
G8 = GC.head(8)
g_cap = figura(f'Palma pasó del PSOE al PP por {n(int(PAL.margv2023))} votos',
               'Voto al PP, al PSOE y a Vox en julio de 2023 en los ocho municipios más poblados, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in G8.iterrows()], 45, 'Voto en los ocho municipios más poblados', W=440, ml=175),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del Atlas de distribución de renta de los hogares del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Isla', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (votos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[r.municipio, r.isla, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], n(r.margv2023)] + [p(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)] for _, r in G8.iterrows()]))

g_aj = figura(f'Deià fue para Sumar por {int(AJ.iloc[0].margv2023)} votos y Es Migjorn Gran, para el PP por {int(AJ.iloc[1].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho municipios más ajustados, en votos',
              barras([(r.municipio, r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.2,
                     'Municipios más ajustados en 2023, en votos', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in sorted(set(AJ.g2023), key=ORDG.index)],
              (['Municipio', 'Isla', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, r.isla, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR']


def hemi(lado=16, por_fila=8):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{max(W_, 200)}px" role="img" aria-label="Escaños de Baleares en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en Baleares y la izquierda alternativa se quedaría sin escaño',
               'Los 8 diputados de las Illes Balears: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/illes-balears/">/encuestas/illes-balears/</a>) {VERSION}. Sumar incluye en 2026 la candidatura de Ara Més-Front Ampli.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Partido', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19[f]), str(E23[f]), str(E29[f]), f'{RC[f][1]}-{RC[f][2]}' if f in RC else '0'] for f in ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de las Illes Balears</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de las Illes Balears por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=07040">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/baleares/">datos de cada municipio de Baleares</a></div>\n</figure>\n')

# --- Texto ---
EFE = 'https://www.ultimahora.es/noticias/elecciones-29n/2026/11/12/2748183/29n-primer-asalto-pugna-entre-derecha-izquierda-por-govern-balear-2027.html'
UH = 'https://www.ultimahora.es/noticias/elecciones-29n/2026/10/26/2736393/baleares-pone-nombre-batalla-electoral-del-29n.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Las Illes Balears eligen el 29 de noviembre 8 diputados. El PP presenta a José Vicente Marí Bosó; el PSOE repite con Francina Armengol, presidenta del Congreso en la legislatura que acaba; Vox presenta a María Isabel Cerezo, y Carme Gomila encabeza Ara Més-Front Ampli, que reúne a Més per Mallorca, Més per Menorca, Sumar, Podemos y Esquerra Unida, según <a href="{EFE}">EFE</a>. Podemos se sumó a esa lista al final, con Lucía Muñoz de número tres, según <a href="{UH}">Última Hora</a>. No hemos encontrado en esas notas declaraciones literales de los candidatos.</p>
<p data-tipo="dato">El PSOE subió en Baleares entre noviembre de 2019 y julio de 2023: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} % de los votos a candidaturas, con {n(DV["PSOE"])} votos más, y subió en {PSOE_SUBE} de los {NMUN} municipios. Pero el mapa se le volvió azul. En 2019 fue el más votado en {GANA[Y19]["PSOE"]} municipios, entre ellos Palma; en 2023, en {GANA[Y23]["PSOE"]}. Los municipios que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población de las islas al {p(POB[Y23]["PSOE"])} %. El PP pasó de {GANA[Y19]["PP"]} municipios a {GANA[Y23]["PP"]}, y del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, con {n(DV["PP"])} votos más.</p>
{g_ins}
<p data-tipo="dato">El PP subió en los {NMUN} municipios, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó. Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. A la izquierda del PSOE, Unidas Podemos, Más País y Més-Esquerra, que se presentó por su cuenta y sacó el {p(A19["pct"]["MES"])} %, habían sumado el {p(IZQ19)} % en 2019; en 2023, Sumar, con Més dentro, sacó el {p(A23["pct"]["SUMAR"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<p data-tipo="patron">De los {GANA[Y19]["PSOE"]} municipios del PSOE en 2019, {PSOE_PP} pasaron al PP, y ninguno hizo el camino contrario. En esos {PSOE_PP}, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP subió más, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %. De los {GANA[Y19]["UP"]} municipios de Unidas Podemos en 2019, {NW[UP_PP]} pasaron al PP y Esporles, a Sumar.</p>
{g_flip}
<h2>Las islas</h2>
<p data-tipo="dato">En 2019, el PSOE fue el más votado en las cuatro islas; en 2023, el PP. En Eivissa, el PP ganó en 2023 los {len(ISLA["Eivissa"])} municipios, y también en Formentera. En Menorca, el PP pasó de {ISG["Menorca"][Y19]["PP"]} a {ISG["Menorca"][Y23]["PP"]} de los {len(ISLA["Menorca"])} municipios, y el PSOE conservó {NW[ISG["Menorca"][Y23]["PSOE"]]}, entre ellos Maó; es la isla en la que más votó a Sumar, con el {p(IS["Menorca"][Y23]["pct"]["SUMAR"])} %. En Mallorca, el PP pasó de {ISG["Mallorca"][Y19]["PP"]} municipios a {ISG["Mallorca"][Y23]["PP"]}, de {len(ISLA["Mallorca"])}.</p>
{g_isla}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">El cambio fue mayor en las ciudades. De las {TG["n"]} de más de 30.000 habitantes, el PSOE ganó en {NW[TG["g19"]["PSOE"]]} en 2019 y solo en Maó en 2023, por {int(MAO.margv2023)} votos. Palma pasó del PSOE al PP por {n(int(PAL.margv2023))} votos: el PP sacó allí el {p(PAL[f"{Y23}%PP"])} % y el PSOE, el {p(PAL[f"{Y23}%PSOE"])} %. Calvià, Eivissa, Manacor, Marratxí, Llucmajor, Inca y Sant Josep de sa Talaia también pasaron del PSOE al PP. Cómo votó Palma barrio a barrio está en {L("palma-barrio-a-barrio-29n", "esta pieza")}.</p>
{g_tam}
{g_cap}
<h2>Los tres municipios de Sumar</h2>
<p data-tipo="dato">Sumar fue el más votado en 2023 en {NW[GANA[Y23]["SUMAR"]]} municipios, los tres de Mallorca: Esporles, que había ganado Unidas Podemos en 2019; Deià, donde en 2019 empataron el PSOE y Unidas Podemos, y Campanet, que había ganado el PSOE. Deià fue el municipio más ajustado de Baleares en 2023: Sumar sacó {int(SU.loc["Deià"].margv2023)} votos al PP. En Es Migjorn Gran (Menorca), el PP ganó por {int(AJ.iloc[1].margv2023)}. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 8 escaños da al PP {NW[E29["PP"]]} y al PSOE {NW[E29["PSOE"]]}, los mismos que en 2023, y a Vox {NW[E29["VOX"]]}, uno más. El escaño que pierde la izquierda alternativa, que en 2023 sacó Sumar, iría a Vox, aunque la horquilla de Sumar llega a uno. El modelo trata la candidatura de Ara Més-Front Ampli como la de Sumar.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos en 2023. Que el PP subiera en todos los municipios a la vez que desaparecía Ciudadanos encaja con que recogiera buena parte de sus votos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos pequeños, unos pocos votos cambian el ganador. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de las islas desde 1977, con las autonómicas, está en {L("baleares-historia-electoral", "las Illes Balears en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/baleares/">la ficha de Baleares</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Baleares?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %) y Vox ({p(A23["pct"]["VOX"])} %). '
     f'El PP y el PSOE sacaron {NW[E23["PP"]]} diputados cada uno; Sumar y Vox, uno. En noviembre de 2019 el más votado había sido el PSOE.'),
    ('¿En cuántos municipios de Baleares ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}, y Sumar, en tres (Esporles, Deià y Campanet). En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} y el PP en {GANA[Y19]["PP"]}.'),
    ('¿Quién ganó en Palma?',
     f'El PP, en julio de 2023, por {n(int(PAL.margv2023))} votos sobre el PSOE. En noviembre de 2019 había ganado el PSOE.'),
    ('¿Cuántos diputados eligen las Illes Balears el 29N?',
     '8, los mismos que en 2023.'),
    ('¿Qué dicen las encuestas en Baleares?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("baleares-historia-electoral", "Historia electoral de Baleares")} · <a href="{BASE}elecciones/baleares/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/illes-balears/">Encuesta en Baleares</a> · {L("palma-barrio-a-barrio-29n", "Palma, barrio a barrio")}')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'población del Atlas de distribución de renta de los hogares del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_baleares.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'UP_PP': UP_PP, 'DV': DV, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE,
    'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'IS': {i: {y: IS[i][y]['pct'] for y in IS[i]} for i in IS}, 'ISG': ISG, 'ISN': {i: len(v) for i, v in ISLA.items()},
    'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv23': int(r.margv2023), 'pp23': R(r[f'{Y23}%PP']), 'psoe23': R(r[f'{Y23}%PSOE'])} for _, r in GC.iterrows()},
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de las Illes Balears',
      f'El mapa electoral de Baleares: el PSOE subió en {PSOE_SUBE} de los {NMUN} municipios, pero pasó de ganar en {NW[TG["g19"]["PSOE"]]} de las {NW[TG["n"]]} ciudades de más de 30.000 habitantes a ganar solo en Maó',
      f'El PSOE sumó {n(DV["PSOE"])} votos, pero los municipios que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población al {p(POB[Y23]["PSOE"])} %; Palma pasó al PP. '
      f'Para el 29N, la media de encuestas da al PP {NW[E29["PP"]]} de los 8 diputados, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
