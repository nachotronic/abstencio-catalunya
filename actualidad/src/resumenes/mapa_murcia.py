"""«El mapa electoral de la Región de Murcia» (2026-11), undécima pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 45 municipios de la Región de Murcia en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno
(listas por separado: en 2019, Unidas Podemos y Más País), los 16 municipios que ganó Vox en 2019 (todos al PP en 2023),
el tamaño de los municipios (padrón municipal del INE, 2023), las ciudades grandes, los municipios más ajustados y el reparto central del
modelo de /encuestas/ para el 29N.
Contexto: Murcia Plaza (listas de Vox, 30-10-2026, y del PP, 27-10-2026). No hay nota de agencia con citas sobre las listas.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_murcia.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-murcia-29n'
PR = '30'
CAJA = (-2.4, 37.35, -0.65, 38.76)
COLC = dict(COL)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios([PR])
NMUN = len(m)
assert NMUN == 45
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['30030'] == 'Murcia' and NOMM['30016'] == 'Cartagena'
L19, L23 = ('VOX', 'PP', 'PSOE', 'UP', 'MP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'VOX': 16, 'PSOE': 15, 'PP': 14}, GANA[Y19]
assert GANA[Y23] == {'PP': 41, 'PSOE': 4}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
VOX_PP, PSOE_PP, PSOE_PSOE, PP_PP = TR('VOX', 'PP'), TR('PSOE', 'PP'), TR('PSOE', 'PSOE'), TR('PP', 'PP')
assert (VOX_PP, PSOE_PP, PSOE_PSOE, PP_PP) == (16, 11, 4, 14)
PSOE23 = sorted(m[m.g2023 == 'PSOE'].municipio)
assert PSOE23 == ['Bullas', 'Calasparra', 'Campos del Río', 'Moratalla']
DV = {f: int(A23['votos'][f] - A19['votos'][f]) for f in ('PP', 'PSOE', 'VOX')}
assert DV == {'PP': 117933, 'PSOE': 11569, 'VOX': -36844}, DV
assert round(A19['pct']['VOX'], 1) == 28.2 and round(A23['pct']['PP'], 1) == 41.5 and A23['part'] > A19['part']
assert m[f'{Y23}_vCS'].sum() == 0
VOX_BAJA = int((m[f'{Y23}%VOX'] < m[f'{Y19}%VOX']).sum())
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
assert VOX_BAJA == NMUN and PSOE_SUBE == 22 and PP_SUBE == NMUN
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('VOX', 'PP', 'PSOE')} for y in (Y19, Y23)}
assert [round(POB[Y19][f], 1) for f in ('VOX', 'PP', 'PSOE')] == [41.5, 39.7, 18.8] and round(POB[Y23]['PP'], 1) == 98.0, POB

# Circunscripciones en las que Vox fue el más votado en noviembre de 2019 (sin voto exterior)
ES = municipios([f'{i:02d}' for i in range(1, 53)])
VOX1 = sorted(pr for pr, g in ES.groupby(ES.mun_code.str[:2]) if (lambda a: max(a, key=a.get))(agrega(g, Y19, L19)['pct']) == 'VOX')
assert VOX1 == ['30', '51'], VOX1
del ES

# Los 16 municipios de Vox en 2019
VX = m[m.g2019 == 'VOX']
FLS = {y: agrega(VX, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert round(FLS[Y19]['VOX'], 1) == 31.1 and round(FLS[Y23]['VOX'], 1) == 23.9 and round(FLS[Y23]['PP'], 1) == 40.7, FLS
VXMAX19 = m.sort_values(f'{Y19}%VOX', ascending=False).iloc[0]
VXMAX23 = m.sort_values(f'{Y23}%VOX', ascending=False).iloc[0]
assert VXMAX19.municipio == 'Torre-Pacheco' and VXMAX23.municipio == 'Fuente Álamo de Murcia'
VX_SEG23 = int((VX.seg2023 == 'VOX').sum())

# Tamaño de municipio
TAM = [('Menos de 5.000', 0, 5000), ('De 5.000 a 20.000', 5000, 20000), ('De 20.000 a 50.000', 20000, 50000), ('Más de 50.000', 50000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'CS')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
assert TT['De 20.000 a 50.000']['g19'] == {'VOX': 9, 'PSOE': 3, 'PP': 3} and TT['De 20.000 a 50.000']['g23'] == {'PP': 15}
assert TT['Más de 50.000']['g19'] == {'VOX': 2, 'PSOE': 1, 'PP': 1} and TT['Más de 50.000']['g23'] == {'PP': 4}
assert all(t['vox23'] < t['vox19'] and t['pp23'] > t['pp19'] for t in TT.values())

# Ciudades grandes
GR = m.sort_values('poblacion', ascending=False).head(8)
assert list(GR.municipio) == ['Murcia', 'Cartagena', 'Lorca', 'Molina de Segura', 'Alcantarilla', 'Torre-Pacheco', 'Águilas', 'Yecla']
assert set(GR.g2023) == {'PP'} and list(GR.g2019) == ['PP', 'VOX', 'PSOE', 'VOX', 'VOX', 'VOX', 'PSOE', 'PP']
GI = GR.set_index('municipio')
CTG, MUR = GI.loc['Cartagena'], GI.loc['Murcia']

# Ajustados
AJ = m[m.g2023 != 'EMPATE'].sort_values('margv2023').head(8)
assert list(AJ.municipio[:5]) == ['Albudeite', 'Ulea', 'Ricote', 'Moratalla', 'Lorquí'] and int(AJ.iloc[0].margv2023) == 5
MOR = AJ.set_index('municipio').loc['Moratalla']
assert MOR.g2023 == 'PSOE' and int(MOR.margv2023) == 104 and MOR.g2019 == 'PSOE'
LAL = m.set_index('municipio').loc['Los Alcázares']
G10 = m[m.poblacion >= 10000].sort_values('margv2023')
assert G10.iloc[0].municipio == 'Los Alcázares'
PS = m[m.g2023 == 'PSOE'].set_index('municipio').poblacion
assert PS.max() < 12000 and 7000 < PS.drop('Campos del Río').min() and round(PS['Campos del Río'], -2) == 2100
assert TT['De 5.000 a 20.000']['g19'] == {'PSOE': 9, 'PP': 5, 'VOX': 4}
assert LAL.g2019 == 'PSOE' and LAL.g2023 == 'PP' and int(LAL.margv2023) == 270

# Escaños
ESC = escanos_oficiales([PR])
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')
E19 = {f: ESC[Y19][PR].get(f, 0) for f in F5}
E23 = {f: ESC[Y23][PR].get(f, 0) for f in F5}
assert E19 == {'PP': 3, 'PSOE': 3, 'VOX': 3, 'UP': 1, 'SUMAR': 0}, E19
assert E23 == {'PP': 4, 'PSOE': 3, 'VOX': 2, 'UP': 0, 'SUMAR': 1}, E23
assert ESC['2026'] == {PR: 10}
RC = reparto_central('murcia')
assert set(RC) <= set(F5)
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert E29 == {'PP': 4, 'PSOE': 2, 'VOX': 4, 'UP': 0, 'SUMAR': 0} and sum(E29.values()) == 10, E29
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=38.0, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PP', 'PSOE', 'VOX', 'EMPATE']
MI = m.set_index('mun_code')
g_mapgan = figura(f'Vox ganó en {GANA[Y19]["VOX"]} municipios en 2019 y en ninguno en 2023; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} municipios de la Región de Murcia, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Municipios de la Región de Murcia por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Municipios de la Región de Murcia por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por municipio, sin voto exterior. Ganador según los '
                  'votos de cada candidatura. Ningún municipio terminó en empate.',
                  [(NOMC[f], COLC[f]) for f in ORDG[:3]],
                  (['Partido', 'Municipios en nov. 2019', 'Municipios en 2023', 'Población de esos municipios, 2019 (%)', 'Población de esos municipios, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19].get(f, 0)), n(GANA[Y23].get(f, 0)), p(POB[Y19][f]), p(POB[Y23][f])] for f in ('VOX', 'PP', 'PSOE')]
                   + [['Total', n(NMUN), n(NMUN), '100,0', '100,0']]))

FF = ('VOX', 'PP', 'PSOE', 'CS')
g_flip = figura(f'En los {GANA[Y19]["VOX"]} municipios de Vox en 2019, Vox bajó del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} % y el PP subió del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %',
                'Voto a Vox, al PP, al PSOE y a Ciudadanos en los municipios que ganó Vox en 2019, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los municipios que ganó Vox en 2019', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con los 16 municipios sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos y Más País (2019) / Sumar (2023)', p(FLS[Y19]['UP'] + FLS[Y19]['MP']), p(FLS[Y23]['SUMAR'])]]))

g_tam = figura(f'En los {TT["De 20.000 a 50.000"]["n"]} municipios de 20.000 a 50.000 habitantes, Vox ganó en {TT["De 20.000 a 50.000"]["g19"]["VOX"]} en 2019; en 2023, el PP ganó en los {TT["De 20.000 a 50.000"]["n"]}',
               'Municipios ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Municipios ganados por cada partido según su tamaño', W=440, ml=180),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG[:3]],
               (['Población', 'Municipios', 'Electores (2023)', 'Vox 2019', 'PP 2019', 'PSOE 2019', 'PP 2023', 'PSOE 2023', 'Vox 2019 (%)', 'Vox 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('VOX', 'PP', 'PSOE')] + [n(t['g23'].get(f, 0)) for f in ('PP', 'PSOE')]
                 + [p(t['vox19']), p(t['vox23']), p(t['pp23'])] for nom, t in TT.items()]))

FC = ('PP', 'PSOE', 'VOX')
g_cap = figura('El PP ganó en 2023 en las ocho ciudades más pobladas; en 2019, Vox había ganado en cuatro de ellas',
               'Voto al PP, al PSOE y a Vox en julio de 2023 en los ocho municipios más poblados, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in GR.iterrows()], 50, 'Voto en los ocho municipios más poblados', W=440, ml=120),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Municipio', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (puntos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], n(r.marg2023, 2)] + [p(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)] for _, r in GR.iterrows()]))

g_aj = figura(f'Albudeite se decidió en 2023 por {int(AJ.iloc[0].margv2023)} votos, y Moratalla, uno de los cuatro municipios del PSOE, por {int(MOR.margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho municipios más ajustados, en votos',
              barras([(r.municipio, r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.2,
                     'Municipios más ajustados en 2023, en votos', W=440, ml=175, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in sorted(set(AJ.g2023), key=ORDG.index)],
              (['Municipio', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ventaja (puntos)', 'Ganador nov. 2019'],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), n(r.marg2023, 2), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR']


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
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de la Región de Murcia en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, Vox pasaría de {NW[E23["VOX"]]} a {NW[E29["VOX"]]} diputados en la Región de Murcia y empataría con el PP',
               'Los 10 diputados de la Región de Murcia: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/murcia/">/encuestas/murcia/</a>) {VERSION}.',
               [(NOMC[f], COLC[f]) for f in ORDE if E19[f] or E23[f] or E29[f]],
               (['Partido', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19[f]), str(E23[f]), str(E29[f]), f'{RC[f][1]}-{RC[f][2]}' if f in RC else '0'] for f in ('PP', 'VOX', 'PSOE', 'UP', 'SUMAR')]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada municipio y cada sección censal de la Región de Murcia</span>'
         '<span class="s">Pasa por encima o toca un municipio para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de la Región de Murcia por municipio y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=30030">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/murcia/">datos de cada municipio de la Región de Murcia</a></div>\n</figure>\n')

# --- Texto ---
VXL = 'https://murciaplaza.com/murciaplaza/region/vox-anuncia-en-murcia-a-los-candidatos-murcianos-para-el-29n-arropados-por-centenares-de-fieles'
PPL = 'https://murciaplaza.com/murciaplaza/region/la-lista-completa-del-pp-por-murcia-al-29n-estos-son-los-10-candidatos-al-congreso-y-los-3-aspirantes-al-senado'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La Región de Murcia elige el 29 de noviembre 10 diputados, los mismos que en 2023. Vox los busca con Joaquín Robles, de Moratalla, que se estrena como cabeza de lista tras ocho años como diputado: «Estamos hartos de aguantar la ideología progresista que ha contaminado todo», dijo en la presentación, según <a href="{VXL}">Murcia Plaza</a>. El candidato de Vox al Senado, José Manuel Pancorbo, añadió que «cuando el PP ha tenido oportunidad de derogar las políticas del PSOE, no lo ha hecho». La lista del PP la encabeza la diputada Miriam Guardiola, de Cieza, según el mismo <a href="{PPL}">medio</a>. No hemos encontrado notas de EFE o Europa Press con citas de esas presentaciones.</p>
<p data-tipo="dato">En noviembre de 2019, la Región de Murcia fue, con Ceuta, una de las dos circunscripciones en las que Vox fue el partido más votado, con el {p(A19["pct"]["VOX"])} %. Ganó en {GANA[Y19]["VOX"]} de sus {NMUN} municipios, entre ellos Cartagena, Molina de Segura y Alcantarilla; el PSOE ganó en {GANA[Y19]["PSOE"]} y el PP en {GANA[Y19]["PP"]}, entre ellos la capital. En julio de 2023, el PP ganó en {GANA[Y23]["PP"]} y el PSOE en {NW[GANA[Y23]["PSOE"]]}: Bullas, Calasparra, Campos del Río y Moratalla. Vox no ganó en ninguno.</p>
{g_ins}
<p data-tipo="dato">El PP pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, con {n(DV["PP"])} votos más, y subió en los {NMUN} municipios. Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %, con {n(-DV["VOX"])} votos menos, y bajó también en los {NMUN}. Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó. El PSOE apenas se movió, del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, y subió en {PSOE_SUBE} municipios. La participación pasó del {p(A19["part"])} % al {p(A23["part"])} %. Los municipios que ganó el PP pasaron de reunir el {p(POB[Y19]["PP"])} % de la población al {p(POB[Y23]["PP"])} %.</p>
{g_mapgan}
<p data-tipo="patron">Los {GANA[Y19]["VOX"]} municipios de Vox en 2019 pasaron los {VOX_PP} al PP. En ellos, Vox bajó del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} % y el PP subió del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %; el PSOE pasó del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %. En 2019, el municipio con más voto a Vox fue Torre-Pacheco, con el {p(VXMAX19[f"{Y19}%VOX"])} %; en 2023, Fuente Álamo de Murcia, con el {p(VXMAX23[f"{Y23}%VOX"])} %. De los {GANA[Y19]["PSOE"]} municipios del PSOE, {PSOE_PP} pasaron al PP y {NW[PSOE_PSOE]} siguieron con el PSOE. Los {GANA[Y19]["PP"]} del PP siguieron todos con el PP.</p>
{g_flip}
<h2>Las ciudades y los pueblos</h2>
<p data-tipo="patron">Vox ganó en 2019 sobre todo en los municipios medianos y grandes: en {TT["De 20.000 a 50.000"]["g19"]["VOX"]} de los {TT["De 20.000 a 50.000"]["n"]} de 20.000 a 50.000 habitantes y en {NW[TT["Más de 50.000"]["g19"]["VOX"]]} de los {NW[TT["Más de 50.000"]["n"]]} de más de 50.000, Cartagena y Molina de Segura. En los de 5.000 a 20.000, el más votado fue más a menudo el PSOE: en {TT["De 5.000 a 20.000"]["g19"]["PSOE"]} de {TT["De 5.000 a 20.000"]["n"]}. En 2023, el PP ganó en todos los municipios de más de 20.000 habitantes, y los cuatro del PSOE tienen menos de 12.000: Bullas, Calasparra y Moratalla, entre 7.000 y 12.000, y Campos del Río, unos 2.100.</p>
{g_tam}
<p data-tipo="dato">En Cartagena, la segunda ciudad, Vox pasó del {p(CTG[f"{Y19}%VOX"])} % al {p(CTG[f"{Y23}%VOX"])} % y el PP, del {p(CTG[f"{Y19}%PP"])} % al {p(CTG[f"{Y23}%PP"])} %. En Murcia, la capital, el PP ganó en las dos elecciones y en 2023 sacó {n(MUR.marg2023, 2)} puntos al segundo. Lorca y Águilas pasaron del PSOE al PP, y Yecla fue del PP las dos veces. Cómo votó la ciudad de Murcia barrio a barrio está en {L("murcia-barrio-a-barrio-29n", "esta pieza")}.</p>
{g_cap}
<h2>Dónde se decidió por poco</h2>
<p data-tipo="dato">El municipio más ajustado de 2023 fue Albudeite, que ganó el PP por {int(AJ.iloc[0].margv2023)} votos al PSOE. Moratalla, el municipio de Joaquín Robles y uno de los cuatro que ganó el PSOE, se decidió por {int(MOR.margv2023)}. Entre los de más de 10.000 habitantes, el más ajustado fue Los Alcázares, que pasó del PSOE al PP por {n(int(LAL.margv2023))} votos. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 10 escaños da al PP {NW[E29["PP"]]}, los mismos que en 2023; a Vox, {NW[E29["VOX"]]}, frente a {NW[E23["VOX"]]}, y al PSOE, {NW[E29["PSOE"]]}, uno menos. Sumar, que sacó uno en 2023, no tendría ninguno. Las horquillas van de {RC["PP"][1]} a {RC["PP"][2]} escaños para el PP, de {RC["VOX"][1]} a {RC["VOX"][2]} para Vox y de {RC["PSOE"][1]} a {RC["PSOE"][2]} para el PSOE.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por municipio, no de personas: no dicen qué hizo cada votante de Vox o de Ciudadanos en 2023. Que el PP subiera a la vez que bajaba Vox y desaparecía Ciudadanos encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de la región desde 1977, con las autonómicas, está en {L("murcia-historia-electoral", "la Región de Murcia en las urnas")}. Los datos de cada municipio, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/murcia/">la ficha de la Región de Murcia</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en la Región de Murcia?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Vox ({p(A23["pct"]["VOX"])} %) y Sumar ({p(A23["pct"]["SUMAR"])} %). '
     f'Sacó {NW[E23["PP"]]} de los 10 diputados; el PSOE, {NW[E23["PSOE"]]}; Vox, {NW[E23["VOX"]]}, y Sumar, uno. En noviembre de 2019 el más votado había sido Vox.'),
    ('¿En cuántos municipios de la Región de Murcia ganó Vox?',
     f'En noviembre de 2019, en {GANA[Y19]["VOX"]} de {NMUN}, entre ellos Cartagena; en julio de 2023, en ninguno. Los {VOX_PP} pasaron al PP.'),
    ('¿Dónde ganó el PSOE en la Región de Murcia en 2023?',
     'En cuatro municipios: Bullas, Calasparra, Campos del Río y Moratalla. El PP ganó en los otros 41.'),
    ('¿Cuántos diputados elige la Región de Murcia el 29N?',
     '10, los mismos que en 2023.'),
    ('¿Qué dicen las encuestas en la Región de Murcia?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, a Vox {E29["VOX"]} y al PSOE {E29["PSOE"]}, con un margen amplio.'),
]
enlaces = (f'{L("murcia-historia-electoral", "Historia electoral de la Región de Murcia")} · <a href="{BASE}elecciones/murcia/">Datos de cada municipio</a> · '
           f'<a href="{BASE}encuestas/murcia/">Encuesta en la Región de Murcia</a> · {L("murcia-barrio-a-barrio-29n", "Murcia, barrio a barrio")}')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por municipio (sin voto exterior); '
        'población del padrón municipal del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_murcia.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'VOX_PP': VOX_PP, 'PSOE_PP': PSOE_PP, 'PSOE_PSOE': PSOE_PSOE, 'PP_PP': PP_PP, 'DV': DV,
    'VOX_BAJA': VOX_BAJA, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE, 'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN,
    'VXMAX19': R(VXMAX19[f'{Y19}%VOX']), 'VXMAX23': R(VXMAX23[f'{Y23}%VOX']),
    'GR': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'marg23': R(r.marg2023), **{f'{f.lower()}{y[2:4]}': R(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)}} for _, r in GR.iterrows()},
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()], 'LAL_V': int(LAL.margv2023),
    'E19': E19, 'E23': E23, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de la Región de Murcia',
      f'El mapa electoral de la Región de Murcia: Vox ganó en {GANA[Y19]["VOX"]} municipios en 2019, Cartagena incluida, y en ninguno en 2023',
      f'Los {VOX_PP} pasaron al PP, que subió en los {NMUN} municipios y ganó en {GANA[Y23]["PP"]}; el PSOE se quedó con {NW[GANA[Y23]["PSOE"]]}. '
      f'Para el 29N, la media de encuestas da a Vox {NW[E29["VOX"]]} de los 10 diputados, tantos como al PP, y al PSOE {NW[E29["PSOE"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
