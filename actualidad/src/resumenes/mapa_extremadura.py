"""«El mapa electoral de Extremadura» (2026-11), duodécima pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 388 municipios de Extremadura en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(listas por separado: en 2019, Unidas Podemos y Más País), el tamaño de los municipios (padrón de 2023), las 13 ciudades
de más de 10.000 habitantes, las dos provincias, los municipios decididos por menos de diez votos y el reparto central del
modelo de /encuestas/ para el 29N.
Contexto: Onda Cero Sur Extremadura (listas del PSOE, 18-10-2026, y del PP, 21-10-2026, esta según Europa Press).
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_extremadura.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-extremadura-29n'
PROV = {'06': 'Badajoz', '10': 'Cáceres'}
PSLUG = {'06': 'badajoz', '10': 'caceres'}
CAPITAL = {'06015': 'Badajoz', '10037': 'Cáceres', '06083': 'Mérida'}
CAJA = (-7.6, 37.9, -4.6, 40.5)
COLC = dict(COL)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios(list(PROV))
NMUN = len(m)
assert NMUN == 388
NOMM = dict(zip(m.mun_code, m.municipio))
assert all(NOMM[k] == v for k, v in CAPITAL.items())
L19, L23 = ('PSOE', 'PP', 'VOX', 'UP', 'MP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 344, 'PP': 39, 'VOX': 3, 'EMPATE': 2}, GANA[Y19]
assert GANA[Y23] == {'PSOE': 276, 'PP': 110, 'EMPATE': 1, 'VOX': 1}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP, PP_PSOE = TR('PSOE', 'PP'), TR('PP', 'PSOE')
assert (PSOE_PP, PP_PSOE) == (71, 2)
DV = {f: int(A23['votos'][f] - A19['votos'][f]) for f in ('PP', 'PSOE', 'VOX')}
assert DV == {'PP': 82970, 'PSOE': 17313, 'VOX': -14372}, DV
assert A23['pct']['PSOE'] > A23['pct']['PP'] and A23['part'] > A19['part'] and m[f'{Y23}_vCS'].sum() == 0
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
assert PSOE_SUBE == 160 and PP_SUBE == 373
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert [round(POB[y][f], 1) for y in (Y19, Y23) for f in ('PSOE', 'PP')] == [82.4, 16.9, 47.8, 51.9], POB
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Tamaño de municipio
TAM = [('Menos de 500', 0, 500), ('De 500 a 2.000', 500, 2000), ('De 2.000 a 10.000', 2000, 10000), ('Más de 10.000', 10000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'CS')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
TG = TT['Más de 10.000']
assert TG['n'] == 13 and TG['g19'] == {'PSOE': 12, 'PP': 1} and TG['g23'] == {'PP': 8, 'PSOE': 5}, TG
assert all(t['psoe23'] > t['pp23'] for k, t in TT.items() if k != 'Más de 10.000') and TG['pp23'] > TG['psoe23']
G10 = m[m.poblacion >= 10000].sort_values('poblacion', ascending=False)
PSOE10 = list(G10[G10.g2023 == 'PSOE'].municipio)
assert PSOE10 == ['Mérida', 'Villanueva de la Serena', 'Zafra', 'Montijo', 'Olivenza'] and list(G10[G10.g2019 == 'PP'].municipio) == ['Badajoz']
GI = G10.set_index('municipio')
DB = GI.loc['Don Benito']
assert DB.g2019 == 'PSOE' and DB.g2023 == 'PP' and int(DB.margv2023) == 89
MER = GI.loc['Mérida']
assert int(MER.margv2023) == 548 and MER.seg2023 == 'PP'

# Provincias
PRS = {pr: {y: agrega(m[m.prov == pr], y, L19 if y == Y19 else L23) for y in (Y19, Y23)} for pr in PROV}
PRG = {pr: {y: m[m.prov == pr][f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)} for pr in PROV}
PRN = {pr: int((m.prov == pr).sum()) for pr in PROV}
assert PRN == {'06': 165, '10': 223}
assert all(PRS[pr][Y23]['pct']['PSOE'] > PRS[pr][Y23]['pct']['PP'] for pr in PROV)
assert PRG['06'][Y19]['PP'] == 11 and PRG['06'][Y23]['PP'] == 35 and PRG['10'][Y19]['PP'] == 28 and PRG['10'][Y23]['PP'] == 75

# Ajustados
AJ = m[(m.poblacion >= 5000) & (m.g2023 != 'EMPATE')].sort_values('margv2023').head(8)
assert list(AJ.municipio[:3]) == ['Miajadas', 'Zafra', 'Villafranca de los Barros']
assert [int(v) for v in AJ.margv2023[:3]] == [4, 4, 5] and list(AJ.g2023[:3]) == ['PSOE', 'PSOE', 'PP']
UNVOTO = int((m.margv2023 == 1).sum())
assert UNVOTO == 3
EMP = m[m.g2023 == 'EMPATE']
assert list(EMP.municipio) == ['Guadiana'] and EMP.iloc[0].emp2023 == 'PP-PSOE'
VX23 = m[m.g2023 == 'VOX']
assert set(m[m.g2019 == 'VOX'].prov) == {'10'} and 'Talayuela' in set(m[m.g2019 == 'VOX'].municipio)
assert list(VX23.municipio) == ['Valdehúncar'] and VX23.poblacion.iloc[0] < 200

# Comunidades en las que el PSOE sacó más votos que el PP en 2023
CCAA = {'04': 'AN', '11': 'AN', '14': 'AN', '18': 'AN', '21': 'AN', '23': 'AN', '29': 'AN', '41': 'AN', '22': 'AR', '44': 'AR', '50': 'AR', '33': 'AS', '07': 'IB',
        '35': 'CN', '38': 'CN', '39': 'CB', '02': 'CM', '13': 'CM', '16': 'CM', '19': 'CM', '45': 'CM', '05': 'CL', '09': 'CL', '24': 'CL', '34': 'CL', '37': 'CL',
        '40': 'CL', '42': 'CL', '47': 'CL', '49': 'CL', '08': 'CT', '17': 'CT', '25': 'CT', '43': 'CT', '03': 'VC', '12': 'VC', '46': 'VC', '06': 'EX', '10': 'EX',
        '15': 'GA', '27': 'GA', '32': 'GA', '36': 'GA', '28': 'MD', '30': 'MU', '31': 'NC', '01': 'PV', '20': 'PV', '48': 'PV', '26': 'RI', '51': 'CE', '52': 'ML'}
ES = municipios([f'{i:02d}' for i in range(1, 53)])
ES['cc'] = ES.mun_code.str[:2].map(CCAA)
assert ES.cc.notna().all() and ES.cc.nunique() == 19
CC_PSOE = sorted(cc for cc, g in ES.groupby('cc') if (lambda a: a['PSOE'] > a['PP'])(agrega(g, Y23, L23)['pct']))
assert CC_PSOE == ['CN', 'CT', 'EX', 'NC', 'PV'], CC_PSOE
del ES

# Escaños
ESC = escanos_oficiales(list(PROV))
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')
E19 = {f: sum(ESC[Y19][pr].get(f, 0) for pr in PROV) for f in F5}
E23 = {f: sum(ESC[Y23][pr].get(f, 0) for pr in PROV) for f in F5}
assert E19 == {'PP': 3, 'PSOE': 5, 'VOX': 2, 'UP': 0, 'SUMAR': 0}, E19
assert E23 == {'PP': 4, 'PSOE': 4, 'VOX': 1, 'UP': 0, 'SUMAR': 0}, E23
assert ESC['2026'] == {'06': 5, '10': 4}
assert sum(ESC[Y19]['06'].values()) == 6 and sum(ESC[Y23]['06'].values()) == 5
RC = {pr: reparto_central(PSLUG[pr]) for pr in PROV}
assert set().union(*RC.values()) <= set(F5)
E29 = {f: sum(RC[pr].get(f, (0,))[0] for pr in PROV) for f in F5}
assert E29 == {'PP': 4, 'PSOE': 3, 'VOX': 2, 'UP': 0, 'SUMAR': 0}, E29
assert RC['10']['PSOE'] == (1, 1, 2) and RC['10']['VOX'] == (1, 0, 1)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos(list(PROV), W=640, lat=39.2, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} municipios a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de Extremadura, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de Extremadura por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de Extremadura por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  f'votos de cada candidatura. En gris, los municipios en los que los dos primeros empataron a votos ({NW[GANA[Y19]["EMPATE"]]} en 2019 y {NW[GANA[Y23]["EMPATE"]]} en 2023).',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0))] + ([p(POB[Y19][f]), p(POB[Y23][f])] if f in ('PP', 'PSOE') else ['—', '—']) for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN), '', '']]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} municipios que pasaron del PSOE al PP, el PSOE subió: del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los municipios que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos y Más País (2019) / Sumar (2023)', p(FLS[Y19]['UP'] + FLS[Y19]['MP']), p(FLS[Y23]['SUMAR'])]]))

g_tam = figura(f'En las {TG["n"]} ciudades de más de 10.000 habitantes, el PSOE pasó de ganar en {TG["g19"]["PSOE"]} a ganar en {NW[TG["g23"]["PSOE"]]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Municipios', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'PSOE 2023', 'PP 2023', 'PSOE 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'PP')]
                 + [p(t['psoe23']), p(t['pp23'])] for nom, t in TT.items()]))

FC = ('PP', 'PSOE', 'VOX')
GC = G10.head(7)
g_cap = figura('El PP ganó en 2023 en Badajoz, Cáceres, Plasencia, Don Benito y Almendralejo; el PSOE conservó Mérida y Villanueva de la Serena',
               'Voto al PP, al PSOE y a Vox en julio de 2023 en los siete municipios de más de 20.000 habitantes, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in GC.iterrows()], 50, 'Voto en los siete municipios de más de 20.000 habitantes', W=440, ml=175),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del padrón de 2023 (INE). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (votos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], n(r.margv2023)] + [p(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)] for _, r in GC.iterrows()]))
assert len(GC) == 7 and GC.poblacion.min() >= 20000 and G10.iloc[7].poblacion < 20000

g_prov = figura(f'El PSOE fue el más votado en 2023 en las dos provincias, pero el PP pasó de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]} municipios',
                'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, por provincia',
                apiladas([(f'{PROV[pr]} · {y[:4]}', [(PRG[pr][y].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if PRG[pr][y].get(f, 0)]) for pr in PROV for y in (Y19, Y23)],
                         'Municipios ganados por cada partido en cada provincia', W=440, ml=120),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in ORDG],
                (['Provincia', 'Municipios', 'PSOE 2019 (%)', 'PP 2019 (%)', 'PSOE 2023 (%)', 'PP 2023 (%)', 'Vox 2023 (%)',
                  'Municipios PSOE 2019', 'Municipios PSOE 2023', 'Municipios PP 2019', 'Municipios PP 2023'],
                 [[PROV[pr], n(PRN[pr])] + [p(PRS[pr][Y19]['pct'][f]) for f in ('PSOE', 'PP')] + [p(PRS[pr][Y23]['pct'][f]) for f in ('PSOE', 'PP', 'VOX')]
                  + [n(PRG[pr][y].get(f, 0)) for f in ('PSOE', 'PP') for y in (Y19, Y23)] for pr in PROV]))

g_aj = figura(f'Miajadas y Zafra fueron para el PSOE por {int(AJ.iloc[0].margv2023)} votos, y Villafranca de los Barros, para el PP por {int(AJ.iloc[2].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho municipios de más de 5.000 habitantes más ajustados, en votos',
              barras([(r.municipio, r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.2,
                     'Municipios de más de 5.000 habitantes más ajustados en 2023, en votos', W=440, ml=175, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in sorted(set(AJ.g2023), key=ORDG.index)],
              (['Municipio', 'Provincia', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, PROV[r.prov], n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX']


def hemi(lado=16, por_fila=10):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Extremadura en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


FT = ('PP', 'PSOE', 'VOX')
g_esc = figura(f'Con las encuestas, el PSOE pasaría de {NW[E23["PSOE"]]} a {NW[E29["PSOE"]]} diputados en Extremadura y Vox, de {NW[E23["VOX"]]} a {NW[E29["VOX"]]}',
               'Los 9 diputados de las dos provincias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central de cada provincia '
               f'(<a href="{BASE}encuestas/badajoz/">/encuestas/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Provincia'] + [f'{NOMC[f]} 2023' for f in FT] + [f'{NOMC[f]} 29N' for f in FT],
                [[f'{PROV[pr]} ({ESC["2026"][pr]})'] + [str(ESC[Y23][pr].get(f, 0)) for f in FT]
                 + [f'{RC[pr].get(f, (0, 0, 0))[0]}' + (f' ({RC[pr][f][1]}-{RC[pr][f][2]})' if f in RC[pr] and RC[pr][f][1] != RC[pr][f][2] else '') for f in FT]
                 for pr in PROV]
                + [['Total'] + [str(E23[f]) for f in FT] + [str(E29[f]) for f in FT]]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de Extremadura</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Extremadura por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=06083">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/extremadura/">datos de cada municipio de Extremadura</a></div>\n</figure>\n')

# --- Texto ---
PSL = 'https://ondacerosur.es/2026/10/aprobada-la-lista-del-psoe-del-29n-que-encabeza-yolanda-garcia-seco-al-congreso-por-badajoz-e-irene-pozas-por-caceres/'
PPL = 'https://ondacerosur.es/2026/10/cristina-teniente-y-teresa-tortonda-encabezaran-las-listas-del-pp-al-congreso-por-caceres-y-badajoz-para-el-29n/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Extremadura elige el 29 de noviembre 9 diputados: {ESC["2026"]["06"]} en Badajoz y {ESC["2026"]["10"]} en Cáceres. El PSOE presenta a Yolanda García Seco en Badajoz y a Irene Pozas en Cáceres, según <a href="{PSL}">Onda Cero Sur Extremadura</a>. El PP repite con Cristina Teniente en Cáceres y cambia en Badajoz, donde Teresa Tortonda, diputada autonómica, sustituye a Antonio Cavacasillas, según la misma emisora, que cita a <a href="{PPL}">Europa Press</a>. No hemos encontrado declaraciones de los candidatos en esas notas.</p>
<p data-tipo="dato">Extremadura es una de las {NW[len(CC_PSOE)]} comunidades en las que el PSOE sacó en 2023 más votos que el PP (las otras son Canarias, Cataluña, Navarra y el País Vasco): sacó el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas, frente al {p(A23["pct"]["PP"])} % del PP, y fue el primero en las dos provincias. Ganó en {GANA[Y23]["PSOE"]} de los {NMUN} municipios. Pero el PP ganó en las ciudades: de las {TG["n"]} de más de 10.000 habitantes, el PSOE ganó en {TG["g19"]["PSOE"]} en noviembre de 2019 y en {NW[TG["g23"]["PSOE"]]} en julio de 2023. Por eso los municipios que ganó el PP, {GANA[Y23]["PP"]}, reúnen el {p(POB[Y23]["PP"])} % de la población extremeña, y los del PSOE, el {p(POB[Y23]["PSOE"])} %.</p>
{g_ins}
<p data-tipo="dato">En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} municipios, el PP en {GANA[Y19]["PP"]} y Vox en {NW[GANA[Y19]["VOX"]]}, con {NW[GANA[Y19]["EMPATE"]]} empates. Entre una elección y otra, el PSOE pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DV["PSOE"])} votos más, y subió en {PSOE_SUBE} municipios. El PP sumó {n(DV["PP"])} votos y pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} %, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %.</p>
{g_mapgan}
<p data-tipo="patron">{PSOE_PP} municipios pasaron del PSOE al PP, y solo {NW[PP_PSOE]}, El Carrascalejo y Castilblanco, hicieron el camino contrario. En esos {PSOE_PP}, el PSOE no bajó: pasó del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %. El PP subió más, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %.</p>
{g_flip}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">El PSOE siguió siendo el más votado en los pueblos: en los municipios de menos de 10.000 habitantes sacó más votos que el PP en cada tramo de tamaño. En los {TT["De 500 a 2.000"]["n"]} de 500 a 2.000 habitantes, ganó en {TT["De 500 a 2.000"]["g23"]["PSOE"]}. En las {TG["n"]} ciudades de más de 10.000, en cambio, el PP fue el más votado en conjunto, con el {p(TG["pp23"])} % frente al {p(TG["psoe23"])} %, y ganó en {NW[TG["g23"]["PP"]]}. El PSOE conservó Mérida, Villanueva de la Serena, Zafra, Montijo y Olivenza.</p>
{g_tam}
<p data-tipo="dato">De las tres ciudades más pobladas, el PP ganó en 2023 en Badajoz, que ya había ganado en 2019, y en Cáceres; el PSOE se quedó con Mérida, la capital autonómica, por {n(int(MER.margv2023))} votos. Plasencia, Don Benito y Almendralejo pasaron del PSOE al PP; Don Benito, por {int(DB.margv2023)} votos. Plasencia, que ha votado al ganador en todas las generales desde 1977, tiene {L("plasencia-acierta-siempre", "su propia pieza")}.</p>
{g_cap}
<h2>Las dos provincias</h2>
<p data-tipo="dato">El PSOE fue el más votado en las dos provincias en 2023: en Badajoz, con el {p(PRS["06"][Y23]["pct"]["PSOE"])} % frente al {p(PRS["06"][Y23]["pct"]["PP"])} % del PP, y en Cáceres, con el {p(PRS["10"][Y23]["pct"]["PSOE"])} % frente al {p(PRS["10"][Y23]["pct"]["PP"])} %. Pero el PP ganó en más municipios que en 2019 en las dos: en Badajoz pasó de {PRG["06"][Y19]["PP"]} a {PRG["06"][Y23]["PP"]}, de {PRN["06"]}, y en Cáceres, de {PRG["10"][Y19]["PP"]} a {PRG["10"][Y23]["PP"]}, de {PRN["10"]}. Vox, que en 2019 ganó en {NW[GANA[Y19]["VOX"]]} municipios de Cáceres, entre ellos Talayuela, se quedó en 2023 con uno, Valdehúncar, de menos de 200 habitantes.</p>
{g_prov}
<h2>Dónde se decidió por cuatro votos</h2>
<p data-tipo="dato">Entre los municipios de más de 5.000 habitantes, tres se decidieron en 2023 por menos de diez votos. Miajadas (Cáceres) y Zafra (Badajoz) fueron para el PSOE por {int(AJ.iloc[0].margv2023)} votos cada uno, y Villafranca de los Barros (Badajoz), para el PP por {int(AJ.iloc[2].margv2023)}. En los pueblos pequeños, {NW[UNVOTO]} municipios se decidieron por un solo voto y en Guadiana (Badajoz) el PP y el PSOE empataron. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 9 escaños da al PP {NW[E29["PP"]]}, los mismos que en 2023; al PSOE, {NW[E29["PSOE"]]}, uno menos, y a Vox, {NW[E29["VOX"]]}, uno más. El escaño en juego está en Cáceres, donde el modelo da al PSOE entre {RC["10"]["PSOE"][1]} y {RC["10"]["PSOE"][2]} diputados y a Vox entre {RC["10"]["VOX"][1]} y {RC["10"]["VOX"][2]}.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los pueblos pequeños, unos pocos votos cambian el ganador, y el mapa de colores exagera su peso. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la comunidad desde 1977, con las autonómicas, está en {L("extremadura-historia-electoral", "Extremadura en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/extremadura/">la ficha de Extremadura</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Extremadura?',
     f'El PSOE, con el {p(A23["pct"]["PSOE"])} % de los votos a candidaturas (sin voto exterior), por delante del PP ({p(A23["pct"]["PP"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     f'El PSOE y el PP sacaron {NW[E23["PSOE"]]} diputados cada uno, y Vox, uno.'),
    ('¿En cuántos municipios de Extremadura ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}. En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} y el PP en {GANA[Y19]["PP"]}.'),
    ('¿Quién ganó en Badajoz, Cáceres y Mérida?',
     'En julio de 2023, el PP ganó en Badajoz y en Cáceres, y el PSOE, en Mérida. En noviembre de 2019, el PP había ganado en Badajoz, y el PSOE, en Cáceres y en Mérida.'),
    ('¿Cuántos diputados elige Extremadura el 29N?',
     f'9, los mismos que en 2023 (en 2019 eran 10: Badajoz perdió uno): Badajoz elige {ESC["2026"]["06"]} y Cáceres, {ESC["2026"]["10"]}.'),
    ('¿Qué dicen las encuestas en Extremadura?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("extremadura-historia-electoral", "Historia electoral de Extremadura")} · <a href="{BASE}elecciones/extremadura/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/badajoz/">Encuesta en Badajoz</a> · <a href="{BASE}encuestas/caceres/">Encuesta en Cáceres</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'padrón de 2023 (INE); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_extremadura.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'PP_PSOE': PP_PSOE, 'DV': DV, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE,
    'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'PR': {pr: {y: PRS[pr][y]['pct'] for y in PRS[pr]} for pr in PRS}, 'PRG': PRG, 'PRN': PRN,
    'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv23': int(r.margv2023)} for _, r in G10.iterrows()},
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()], 'UNVOTO': UNVOTO,
    'E19': E19, 'E23': E23, 'E29': E29, 'ESC26': ESC['2026'], 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Extremadura',
      f'El mapa electoral de Extremadura: el PSOE ganó en {GANA[Y23]["PSOE"]} de los {NMUN} municipios en 2023, pero el PP ganó en {NW[TG["g23"]["PP"]]} de las {TG["n"]} ciudades de más de 10.000 habitantes',
      f'El PSOE fue el más votado y subió en votos, pero los municipios que ganó pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población al {p(POB[Y23]["PSOE"])} %. '
      f'Miajadas y Zafra se decidieron por cuatro votos. Para el 29N, la media de encuestas da al PP {NW[E29["PP"]]} de los 9 diputados, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
