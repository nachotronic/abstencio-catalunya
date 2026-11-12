"""«El mapa electoral de Asturias» (2026-11), decimocuarta pieza de la serie «El mapa electoral de…» (mapa_ccaa.py).

Los 78 concejos de Asturias en las generales de noviembre de 2019 y julio de 2023, con el ganador de cada uno (listas
por separado: en 2019, Unidas Podemos y Más País), Oviedo y Gijón, las cuencas mineras del Nalón y del Caudal, el tamaño
de los concejos (padrón municipal del INE, 2023), los más ajustados y el reparto central del modelo de /encuestas/ para el 29N.
Contexto: elDiario.es Asturias (listas, 28-10-2026). Sin citas literales en esa nota.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa_asturias.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import (COL, NOM, Y19, Y23, agrega, apiladas, caminos, escanos_oficiales, grupos, insertado, mapa_svg,
                       municipios, p, reparto_central, trazados)

A = BASE + 'actualidad/'
NW = {0: 'ninguno', 1: 'uno', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez'}
SLUG = 'mapa-electoral-asturias-29n'
PR = '33'
CAJA = (-7.2, 42.85, -4.5, 43.68)
COLC = dict(COL)
NOMC = dict(NOM, EMPATE='Empate a votos')

m = municipios([PR])
NMUN = len(m)
assert NMUN == 78
NOMM = dict(zip(m.mun_code, m.municipio))
assert NOMM['33044'] == 'Oviedo' and NOMM['33024'] == 'Gijón'
CUENCAS = ['Aller', 'Caso', 'Langreo', 'Laviana', 'Lena', 'Mieres', 'Morcín', 'Riosa', 'San Martín del Rey Aurelio', 'Sobrescobio']
assert set(CUENCAS) <= set(m.municipio)

L19, L23 = ('PSOE', 'PP', 'VOX', 'UP', 'MP', 'CS'), ('PP', 'PSOE', 'VOX', 'SUMAR')
A19, A23 = agrega(m, Y19, L19), agrega(m, Y23, L23)
GANA = {y: m[f'g{y[:4]}'].value_counts().to_dict() for y in (Y19, Y23)}
assert GANA[Y19] == {'PSOE': 70, 'PP': 8}, GANA[Y19]
assert GANA[Y23] == {'PSOE': 40, 'PP': 38}, GANA[Y23]
TR = lambda a, b: int(((m.g2019 == a) & (m.g2023 == b)).sum())
PSOE_PP = TR('PSOE', 'PP')
assert (PSOE_PP, TR('PP', 'PSOE'), TR('PP', 'PP')) == (30, 0, 8)
DV = {f: int(A23['votos'][f] - A19['votos'][f]) for f in ('PP', 'PSOE', 'VOX')}
assert DV == {'PP': 80872, 'PSOE': 18220, 'VOX': -14580}, DV
assert A23['part'] > A19['part'] and m[f'{Y23}_vCS'].sum() == 0 and A23['pct']['PP'] > A23['pct']['PSOE']
PSOE_SUBE = int((m[f'{Y23}%PSOE'] > m[f'{Y19}%PSOE']).sum())
PP_SUBE = int((m[f'{Y23}%PP'] > m[f'{Y19}%PP']).sum())
assert PSOE_SUBE == 30 and PP_SUBE == NMUN
POB = {y: {f: float(m[m[f'g{y[:4]}'] == f].poblacion.sum() / m.poblacion.sum() * 100) for f in ('PP', 'PSOE')} for y in (Y19, Y23)}
assert [round(POB[y][f], 1) for y in (Y19, Y23) for f in ('PSOE', 'PP')] == [97.3, 2.7, 55.0, 45.0], POB
FL = m[(m.g2019 == 'PSOE') & (m.g2023 == 'PP')]
FLS = {y: agrega(FL, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert FLS[Y23]['PSOE'] > FLS[Y19]['PSOE'] and FLS[Y23]['PP'] > FLS[Y19]['PP'] + 10, FLS

# Oviedo y Gijón
MI_ = m.set_index('municipio')
OVI, GIJ = MI_.loc['Oviedo'], MI_.loc['Gijón']
OVI19 = int(OVI[f'{Y19}_vPSOE'] - OVI[f'{Y19}_vPP'])
assert p(OVI[f'{Y19}%PP']) == p(OVI[f'{Y19}%PSOE'])
assert OVI.g2019 == 'PSOE' and OVI.seg2019 == 'PP' and OVI19 == 42 and OVI.g2023 == 'PP' and int(OVI.margv2023) == 15256
assert GIJ.g2019 == GIJ.g2023 == 'PSOE' and GIJ.seg2023 == 'PP' and int(GIJ.margv2023) == 622

# Cuencas mineras
CU = m[m.municipio.isin(CUENCAS)]
CUS = {y: agrega(CU, y, L19 if y == Y19 else L23)['pct'] for y in (Y19, Y23)}
assert set(CU.g2019) == {'PSOE'} and list(CU[CU.g2023 == 'PP'].municipio) == ['Caso'] and int(MI_.loc['Caso'].margv2023) == 14
assert CUS[Y23]['PSOE'] > CUS[Y19]['PSOE'] and CUS[Y23]['SUMAR'] > CUS[Y23]['PP'] - 5

# Tamaño
TAM = [('Menos de 1.000', 0, 1000), ('De 1.000 a 5.000', 1000, 5000), ('De 5.000 a 20.000', 5000, 20000), ('Más de 20.000', 20000, 10 ** 9)]
assert m.poblacion.notna().all()
TT = {}
for nom, a, b in TAM:
    g = m[(m.poblacion >= a) & (m.poblacion < b)]
    a19, a23 = agrega(g, Y19, L19)['pct'], agrega(g, Y23, L23)['pct']
    TT[nom] = {'n': len(g), 'censo': int(g[f'{Y23}_censo'].sum()), 'g23': g.g2023.value_counts().to_dict(), 'g19': g.g2019.value_counts().to_dict(),
               **{f'{f.lower()}19': a19[f] for f in ('PP', 'PSOE', 'VOX', 'UP')}, **{f'{f.lower()}23': a23[f] for f in ('PP', 'PSOE', 'VOX', 'SUMAR')}}
assert sum(t['n'] for t in TT.values()) == NMUN
TG, TM = TT['Más de 20.000'], TT['De 1.000 a 5.000']
assert TG['n'] == 7 and TG['g19'] == {'PSOE': 7} and TG['g23'] == {'PSOE': 4, 'PP': 3}, TG
assert TM['g19'] == {'PSOE': 27, 'PP': 4} and TM['g23'] == {'PP': 16, 'PSOE': 15}, TM
GC = m[m.poblacion >= 20000].sort_values('poblacion', ascending=False)
assert list(GC[GC.g2023 == 'PSOE'].municipio) == ['Gijón', 'Avilés', 'Langreo', 'Mieres'] and list(GC[GC.g2023 == 'PP'].municipio) == ['Oviedo', 'Siero', 'Castrillón']

# Ajustados
AJ = m.sort_values('margv2023').head(8)
assert list(AJ.municipio[:4]) == ['Pesoz', 'Yernes y Tameza', 'Tapia de Casariego', 'Ponga'] and [int(v) for v in AJ.margv2023[:4]] == [4, 5, 6, 6]
assert list(AJ.g2023[:4]) == ['PP', 'PP', 'PP', 'PSOE'] and set(AJ.g2019) == {'PSOE'}

# Escaños
ESC = escanos_oficiales([PR])
F5 = ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')
E19 = {f: ESC[Y19][PR].get(f, 0) for f in F5}
E23 = {f: ESC[Y23][PR].get(f, 0) for f in F5}
assert E19 == {'PP': 2, 'PSOE': 3, 'VOX': 1, 'UP': 1, 'SUMAR': 0}, E19
assert E23 == {'PP': 3, 'PSOE': 2, 'VOX': 1, 'UP': 0, 'SUMAR': 1}, E23
assert ESC['2026'] == {PR: 7}
RC = reparto_central('asturias')
assert set(RC) <= set(F5)
E29 = {f: RC.get(f, (0,))[0] for f in F5}
assert E29 == {'PP': 3, 'PSOE': 3, 'VOX': 1, 'UP': 0, 'SUMAR': 0} and RC['SUMAR'] == (0, 0, 1), (E29, RC)
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
MESES = {'10': 'octubre', '11': 'noviembre', '12': 'diciembre'}
VERSION = f'a las {int(_hm[:2])}.{_hm[2:]} del {int(_d)} de {MESES[_m]} de {_a}'

# --- Gráficos ---
cam, H = caminos([PR], W=640, lat=43.3, umbral=1.4)
assert len(cam) == NMUN
ORDG = ['PSOE', 'PP']
MI = m.set_index('mun_code')
g_mapgan = figura(f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} concejos a ganar en {GANA[Y23]["PSOE"]}; el PP, de {GANA[Y19]["PP"]} a {GANA[Y23]["PP"]}',
                  f'Partido más votado en cada uno de los {NMUN} concejos de Asturias, en noviembre de 2019 y en julio de 2023',
                  mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2019']], lambda k: NOMC[MI.at[k, 'g2019']],
                           'Concejos de Asturias por partido más votado en noviembre de 2019', NOMM, rotulo='Noviembre de 2019')
                  + mapa_svg(cam, H, lambda k: COLC[MI.at[k, 'g2023']], lambda k: NOMC[MI.at[k, 'g2023']],
                             'Concejos de Asturias por partido más votado en julio de 2023', NOMM, rotulo='Julio de 2023'),
                  'Fuente: Ministerio del Interior, resultados por mesa (vía pollspaindata) sumados por concejo, sin voto exterior. Ganador según los '
                  'votos de cada candidatura. Ningún concejo terminó en empate.',
                  [(NOMC[f], COLC[f]) for f in ORDG],
                  (['Partido', 'Concejos en nov. 2019', 'Concejos en 2023', 'Población de esos concejos, 2019 (%)', 'Población de esos concejos, 2023 (%)'],
                   [[NOMC[f], n(GANA[Y19][f]), n(GANA[Y23][f]), p(POB[Y19][f]), p(POB[Y23][f])] for f in ORDG]
                   + [['Total', n(NMUN), n(NMUN), '100,0', '100,0']]))

FF = ('PP', 'PSOE', 'VOX', 'CS')
g_flip = figura(f'En los {PSOE_PP} concejos que pasaron del PSOE al PP, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %; el PP, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %',
                'Voto al PP, al PSOE, a Vox y a Ciudadanos en los concejos que ganó el PSOE en 2019 y el PP en 2023, en %. Barra clara: noviembre de 2019',
                grupos([(NOMC[f], [(FLS[Y19][f], COLC[f], .38, 'nov. 2019')] + ([(FLS[Y23][f], COLC[f], 1, '2023')] if f != 'CS' else [])) for f in FF],
                       45, 'Voto en los concejos que pasaron del PSOE al PP', W=440, ml=80),
                'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas, con todos los concejos sumados. '
                'Ciudadanos no se presentó en 2023. Cálculo propio.',
                [(NOMC[f], COLC[f]) for f in FF] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
                (['Partido', 'Nov. 2019 (%)', '2023 (%)'], [[NOMC[f], p(FLS[Y19][f]), p(FLS[Y23][f]) if f != 'CS' else '—'] for f in FF]
                 + [['Unidas Podemos y Más País (2019) / Sumar (2023)', p(FLS[Y19]['UP'] + FLS[Y19]['MP']), p(FLS[Y23]['SUMAR'])]]))

FC = ('PP', 'PSOE', 'VOX')
g_cap = figura(f'El PSOE ganó Oviedo por {OVI19} votos en 2019 y el PP, por {n(int(OVI.margv2023))} en 2023; Gijón siguió con el PSOE por {int(GIJ.margv2023)}',
               'Voto al PP, al PSOE y a Vox en julio de 2023 en los siete concejos de más de 20.000 habitantes, en %. Barra clara: noviembre de 2019',
               grupos([(r.municipio, [x for f in FC for x in ((r[f'{Y19}%{f}'], COLC[f], .38, f'{NOMC[f]}, nov. 2019'), (r[f'{Y23}%{f}'], COLC[f], 1, f'{NOMC[f]}, 2023'))])
                       for _, r in GC.iterrows()], 50, 'Voto en los siete concejos de más de 20.000 habitantes', W=440, ml=110),
               'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. Población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in FC] + [('Barra clara: noviembre de 2019', 'color-mix(in srgb, var(--muted) 40%, var(--bg))')],
               (['Concejo', 'Habitantes', 'Ganador nov. 2019', 'Ganador 2023', 'Ventaja 2023 (votos)'] + [f'{NOMC[f]} {y} (%)' for f in FC for y in ('2019', '2023')],
                [[r.municipio, n(r.poblacion), NOMC[r.g2019], NOMC[r.g2023], n(r.margv2023)] + [p(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)] for _, r in GC.iterrows()]))

FCU = ('PSOE', 'PP', 'SUMAR', 'VOX')
g_cu = figura(f'En las cuencas mineras, el PSOE sacó el {p(CUS[Y23]["PSOE"])} % en 2023 y ganó en {NW[int((CU.g2023 == "PSOE").sum())]} de los {len(CUENCAS)} concejos',
              'Voto en julio de 2023 en los diez concejos de las cuencas del Nalón y del Caudal, en %',
              barras([(r.municipio, r[f'{Y23}%PSOE'], COLC[r.g2023], f'{NOMC[r.g2023]} · PSOE {p(r[f"{Y23}%PSOE"])} %') for _, r in CU.sort_values(f'{Y23}%PSOE', ascending=False).iterrows()],
                     60, 'Voto al PSOE en los concejos de las cuencas en 2023', W=440, ml=175),
              'Fuente: Ministerio del Interior, sin voto exterior. Porcentajes sobre votos a candidaturas. La barra es el voto al PSOE y el color, el del ganador del concejo. Cálculo propio.',
              [(NOMC[f], COLC[f]) for f in ORDG],
              (['Concejo', 'Habitantes', 'Ganador 2023', 'Ventaja 2023 (votos)'] + [f'{NOMC[f]} 2023 (%)' for f in FCU],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], n(r.margv2023)] + [p(r[f'{Y23}%{f}']) for f in FCU] for _, r in CU.sort_values(f'{Y23}%PSOE', ascending=False).iterrows()]
               + [['Los diez concejos, en conjunto', n(int(CU.poblacion.sum())), '', ''] + [p(CUS[Y23][f]) for f in FCU]]))

g_tam = figura(f'En los {TM["n"]} concejos de 1.000 a 5.000 habitantes, el PSOE pasó de ganar en {TM["g19"]["PSOE"]} a ganar en {TM["g23"]["PSOE"]}',
               'Concejos ganados por cada partido en noviembre de 2019 y en julio de 2023, según su población',
               apiladas([(f'{nom} · 2019', [(t['g19'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g19'].get(f, 0)]) for nom, t in TT.items()]
                        + [(f'{nom} · 2023', [(t['g23'].get(f, 0), COLC[f], NOMC[f]) for f in ORDG if t['g23'].get(f, 0)]) for nom, t in TT.items()],
                        'Concejos ganados por cada partido según su tamaño', W=440, ml=170),
               'Fuente: Ministerio del Interior, sin voto exterior; población del padrón municipal del INE (2023). Cálculo propio.',
               [(NOMC[f], COLC[f]) for f in ORDG],
               (['Población', 'Concejos', 'Electores (2023)', 'PSOE 2019', 'PP 2019', 'PSOE 2023', 'PP 2023', 'PSOE 2023 (%)', 'PP 2023 (%)'],
                [[nom, n(t['n']), n(t['censo'])] + [n(t['g19'].get(f, 0)) for f in ('PSOE', 'PP')] + [n(t['g23'].get(f, 0)) for f in ('PSOE', 'PP')]
                 + [p(t['psoe23']), p(t['pp23'])] for nom, t in TT.items()]))

g_aj = figura(f'Pesoz fue para el PP por {int(AJ.iloc[0].margv2023)} votos, y Ponga, para el PSOE por {int(AJ.iloc[3].margv2023)}',
              'Ventaja del partido más votado sobre el segundo en julio de 2023 en los ocho concejos más ajustados, en votos',
              barras([(r.municipio, r.margv2023, COLC[r.g2023], f'{NOMC[r.g2023]} +{n(r.margv2023)}') for _, r in AJ.iterrows()], max(AJ.margv2023) * 1.25,
                     'Concejos más ajustados en 2023, en votos', W=440, ml=150, separar=True),
              'Fuente: Ministerio del Interior, sin voto exterior. Cálculo propio. El color es el del ganador.',
              [(NOMC[f], COLC[f]) for f in ORDG],
              (['Concejo', 'Habitantes', 'Ganó', 'Segundo', 'Ventaja (votos)', 'Ganador nov. 2019'],
               [[r.municipio, n(r.poblacion), NOMC[r.g2023], NOMC[r.seg2023], n(r.margv2023), NOMC[r.g2019]] for _, r in AJ.iterrows()]))

FE = [('Noviembre de 2019', E19), ('Julio de 2023', E23), ('29N, media de encuestas', E29)]
ORDE = ['PSOE', 'PP', 'VOX', 'UP', 'SUMAR']


def hemi(lado=16, por_fila=7):
    W_, out, y = por_fila * (lado + 3), [], 0
    for nom, e in FE:
        out.append(f'<text x="0" y="{y + 13}" class="lab">{esc(nom)} · {sum(e.values())} escaños</text>')
        y += 20; k = 0
        for f in ORDE:
            for _ in range(e.get(f, 0)):
                out.append(f'<rect x="{(k % por_fila) * (lado + 3)}" y="{y + (k // por_fila) * (lado + 3)}" width="{lado}" height="{lado}" rx="2" fill="{COLC[f]}"><title>{esc(nom)}: {NOMC[f]}</title></rect>')
                k += 1
        y += -(-sum(e.values()) // por_fila) * (lado + 3) + 12
    return f'<svg viewBox="0 0 {W_} {y}" style="max-width:{W_}px" role="img" aria-label="Escaños de Asturias en 2019, 2023 y según la media de encuestas">' + ''.join(out) + '</svg>'


g_esc = figura(f'Con las encuestas, el PSOE recuperaría el tercer diputado y el Frente Ampliu se quedaría sin escaño',
               'Los 7 diputados de Asturias: un cuadrado por escaño',
               hemi(),
               f'Fuente: Ministerio del Interior (2019 y 2023, con voto exterior); media de encuestas de Mapa Electoral, reparto central '
               f'(<a href="{BASE}encuestas/asturias/">/encuestas/asturias/</a>) {VERSION}. Sumar incluye en 2026 la candidatura del Frente Ampliu por Asturies.',
               [(NOMC[f], COLC[f]) for f in ORDE],
               (['Partido', 'Nov. 2019', '2023', '29N (reparto central)', '29N (horquilla)'],
                [[NOMC[f], str(E19[f]), str(E23[f]), str(E29[f]), f'{RC[f][1]}-{RC[f][2]}' if f in RC else '0'] for f in ('PP', 'PSOE', 'VOX', 'UP', 'SUMAR')]))

g_ins = ('<figure>\n<figcaption><span class="t">El mapa: cómo votó cada concejo y cada sección censal de Asturias</span>'
         '<span class="s">Pasa por encima o toca un concejo para ver su resultado; acércate para ver las secciones censales y cambia de elección en el selector</span></figcaption>\n'
         f'<div class="chart">{insertado(CAJA, "Mapa electoral de Asturias por concejo y sección censal")}</div>\n'
         f'<div class="src">Fuente: Ministerio del Interior. <a href="{BASE}?m=33044">Abrir el mapa a pantalla completa</a> · '
         f'<a href="{BASE}elecciones/asturias/">datos de cada concejo de Asturias</a></div>\n</figure>\n')

# --- Texto ---
EDA = 'https://www.eldiario.es/asturias/once-candidaturas-congreso-siete-senado-concurriran-elecciones-generales-asturias_1_13621582.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
NCU_PSOE = int((CU.g2023 == 'PSOE').sum())

cuerpo = f'''{trazados(cam)}<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Asturias elige el 29 de noviembre 7 diputados entre once candidaturas. El PSOE y Vox repiten cabezas de lista, Adriana Lastra y José María Figaredo; el PP presenta a la concejala gijonesa Ángela Pumariega; el Frente Ampliu por Asturies, en el que se integran IU, Sumar y Somos, a Juan Ponte, y Podemos, que va por separado, a Manuel Pravia, según <a href="{EDA}">elDiario.es</a>. No hemos encontrado en esa nota declaraciones de los candidatos.</p>
<p data-tipo="dato">El PSOE fue el más votado en noviembre de 2019 en {GANA[Y19]["PSOE"]} de los {NMUN} concejos asturianos, incluidos los siete de más de 20.000 habitantes. Oviedo lo ganó por {OVI19} votos sobre el PP. En julio de 2023, el PSOE se quedó con {GANA[Y23]["PSOE"]} concejos y el PP subió a {GANA[Y23]["PP"]}: Oviedo pasó al PP por {n(int(OVI.margv2023))} votos y Gijón siguió con el PSOE por {int(GIJ.margv2023)}. El PSOE no bajó en votos: pasó del {p(A19["pct"]["PSOE"])} % al {p(A23["pct"]["PSOE"])} %, con {n(DV["PSOE"])} votos más, pero el PP pasó del {p(A19["pct"]["PP"])} % al {p(A23["pct"]["PP"])} %, con {n(DV["PP"])} más, y fue el más votado en Asturias.</p>
{g_ins}
<p data-tipo="dato">El PP subió en los {NMUN} concejos, en un año en que Ciudadanos, que había sacado el {p(A19["pct"]["CS"])} % en 2019, no se presentó y Vox bajó del {p(A19["pct"]["VOX"])} % al {p(A23["pct"]["VOX"])} %. La participación subió del {p(A19["part"])} % al {p(A23["part"])} %. Los concejos que ganó el PSOE pasaron de reunir el {p(POB[Y19]["PSOE"])} % de la población al {p(POB[Y23]["PSOE"])} %, y los del PP, del {p(POB[Y19]["PP"])} % al {p(POB[Y23]["PP"])} %.</p>
{g_mapgan}
<p data-tipo="patron">{PSOE_PP} concejos pasaron del PSOE al PP, y ninguno hizo el camino contrario. En esos {PSOE_PP}, el PSOE subió del {p(FLS[Y19]["PSOE"])} % al {p(FLS[Y23]["PSOE"])} %, pero el PP subió más, del {p(FLS[Y19]["PP"])} % al {p(FLS[Y23]["PP"])} %, mientras desaparecía Ciudadanos, que allí había sacado el {p(FLS[Y19]["CS"])} %, y Vox bajaba del {p(FLS[Y19]["VOX"])} % al {p(FLS[Y23]["VOX"])} %.</p>
{g_flip}
<h2>Oviedo, Gijón y las ciudades</h2>
<p data-tipo="dato">De los siete concejos de más de 20.000 habitantes, que el PSOE ganó todos en 2019, el PP se llevó en 2023 Oviedo, Siero y Castrillón. El PSOE conservó Gijón, Avilés, Langreo y Mieres. En Oviedo, el PP y el PSOE sacaron en 2019 el {p(OVI[f"{Y19}%PP"])} % cada uno, con {OVI19} votos de diferencia; en 2023, el PP subió al {p(OVI[f"{Y23}%PP"])} % y el PSOE, al {p(OVI[f"{Y23}%PSOE"])} %. En Gijón, el PSOE sacó el {p(GIJ[f"{Y23}%PSOE"])} % y el PP, el {p(GIJ[f"{Y23}%PP"])} %.</p>
{g_cap}
<h2>Las cuencas mineras</h2>
<p data-tipo="dato">En los {len(CUENCAS)} concejos de las cuencas del Nalón y del Caudal, el PSOE sacó en 2023 el {p(CUS[Y23]["PSOE"])} %, más que en 2019 ({p(CUS[Y19]["PSOE"])} %), y ganó en {NW[NCU_PSOE]}. El único que pasó al PP fue Caso, por {int(MI_.loc["Caso"].margv2023)} votos. Sumar sacó allí el {p(CUS[Y23]["SUMAR"])} %, frente al {p(A23["pct"]["SUMAR"])} % de toda Asturias, y el PP, el {p(CUS[Y23]["PP"])} %. Cómo votaron las cuencas en 1936, tras la revolución de 1934, está en {L("asturias-1934-1936-revolucion-urnas", "esta pieza")}.</p>
{g_cu}
<h2>Los pueblos</h2>
<p data-tipo="patron">El vuelco fue mayor en los concejos medianos y pequeños. En los {TM["n"]} de 1.000 a 5.000 habitantes, el PSOE pasó de {TM["g19"]["PSOE"]} a {TM["g23"]["PSOE"]} y el PP, de {TM["g19"]["PP"]} a {TM["g23"]["PP"]}. Algunos se decidieron por muy poco: Pesoz y Yernes y Tameza, por {int(AJ.iloc[0].margv2023)} y {int(AJ.iloc[1].margv2023)} votos para el PP; Tapia de Casariego, por {int(AJ.iloc[2].margv2023)}, también para el PP, y Ponga, por {int(AJ.iloc[3].margv2023)} para el PSOE. Los pueblos que se ganaron por un voto en toda España están en {L("ganar-por-un-voto-29n", "esta pieza")}.</p>
{g_tam}
{g_aj}
<h2>Lo que puede cambiar el 29N</h2>
<p data-tipo="dato">Con la media de encuestas de Mapa Electoral, el reparto central de los 7 escaños da al PP {NW[E29["PP"]]}, los mismos que en 2023; al PSOE, {NW[E29["PSOE"]]}, uno más, y a Vox, {NW[E29["VOX"]]}. El escaño que sacó Sumar en 2023 iría al PSOE, aunque la horquilla del Frente Ampliu llega a uno. El modelo trata el Frente Ampliu como Sumar; Podemos se presenta por separado.</p>
{g_esc}
<h2>Lo que estos datos no dicen</h2>
<p data-tipo="hipotesis">Estos datos son por concejo, no de personas: no dicen qué hizo cada votante de Ciudadanos o de Vox en 2023. Que el PP subiera en todos los concejos a la vez que desaparecía Ciudadanos y bajaba Vox encaja con que recogiera votos de los dos, pero el mapa no permite separarlo de otros movimientos, como el de la participación, que subió. En los concejos pequeños, unos pocos votos cambian el ganador. Los porcentajes son sobre votos a candidaturas y sin el voto exterior, por eso no coinciden con los oficiales. Las encuestas tienen un margen amplio a 17 días de la votación.</p>
<p data-tipo="contexto">La historia electoral de Asturias desde 1977, con las autonómicas, está en {L("asturias-historia-electoral", "Asturias en las urnas")}. Los datos de cada concejo, su censo y su serie desde 1977 están en <a href="{BASE}elecciones/asturias/">la ficha de Asturias</a>.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Asturias?',
     f'El PP, con el {p(A23["pct"]["PP"])} % de los votos a candidaturas (sin voto exterior), por delante del PSOE ({p(A23["pct"]["PSOE"])} %), Sumar ({p(A23["pct"]["SUMAR"])} %) y Vox ({p(A23["pct"]["VOX"])} %). '
     f'Sacó {NW[E23["PP"]]} de los 7 diputados; el PSOE, {NW[E23["PSOE"]]}; Sumar y Vox, uno. En noviembre de 2019 el más votado había sido el PSOE.'),
    ('¿En cuántos concejos de Asturias ganó el PSOE en 2023?',
     f'En {GANA[Y23]["PSOE"]} de {NMUN}; el PP, en {GANA[Y23]["PP"]}. En noviembre de 2019, el PSOE había ganado en {GANA[Y19]["PSOE"]} y el PP en {GANA[Y19]["PP"]}.'),
    ('¿Quién ganó en Oviedo y en Gijón?',
     f'En julio de 2023, el PP ganó en Oviedo por {n(int(OVI.margv2023))} votos y el PSOE en Gijón por {int(GIJ.margv2023)}. En noviembre de 2019, el PSOE había ganado en los dos; en Oviedo, por {OVI19} votos.'),
    ('¿Cuántos diputados elige Asturias el 29N?',
     '7, los mismos que en 2023.'),
    ('¿Qué dicen las encuestas en Asturias?',
     f'Con la media de encuestas de Mapa Electoral, el reparto central da al PP {E29["PP"]} escaños, al PSOE {E29["PSOE"]} y a Vox {E29["VOX"]}, con un margen amplio.'),
]
enlaces = (f'{L("asturias-historia-electoral", "Historia electoral de Asturias")} · <a href="{BASE}elecciones/asturias/">Datos de cada concejo</a> · '
           f'<a href="{BASE}encuestas/asturias/">Encuesta en Asturias</a> · {L("asturias-1934-1936-revolucion-urnas", "Asturias, 1934-1936")}')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y julio de 2023 por mesa (vía pollspaindata) y por concejo (sin voto exterior); '
        'población del padrón municipal del INE (2023); media de encuestas de Mapa Electoral. Cálculo: actualidad/src/resumenes/mapa_asturias.py.')

R = lambda v: round(float(v), 4)
DATOS = {
    'A19': A19, 'A23': A23, 'GANA': GANA, 'PSOE_PP': PSOE_PP, 'DV': DV, 'PSOE_SUBE': PSOE_SUBE, 'PP_SUBE': PP_SUBE,
    'POB': POB, 'FLS': FLS, 'TT': TT, 'NMUN': NMUN, 'CUS': CUS, 'NCU': len(CUENCAS), 'NCU_PSOE': NCU_PSOE,
    'OVI19': OVI19, 'GC': {r.municipio: {'g19': r.g2019, 'g23': r.g2023, 'margv23': int(r.margv2023), **{f'{f.lower()}{y[2:4]}': R(r[f'{y}%{f}']) for f in FC for y in (Y19, Y23)}} for _, r in GC.iterrows()},
    'CASO': int(MI_.loc['Caso'].margv2023),
    'AJ': [[r.municipio, r.g2023, r.seg2023, R(r.marg2023), int(r.margv2023)] for _, r in AJ.iterrows()],
    'E19': E19, 'E23': E23, 'E29': E29, 'RC': RC,
}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')

pieza(SLUG, 'El mapa electoral de Asturias',
      f'El mapa electoral de Asturias: el PSOE ganó Oviedo por {OVI19} votos en 2019 y lo perdió por {n(int(OVI.margv2023))} en 2023; Gijón lo retuvo por {int(GIJ.margv2023)}',
      f'El PSOE pasó de ganar en {GANA[Y19]["PSOE"]} de los {NMUN} concejos a ganar en {GANA[Y23]["PSOE"]}, aunque subió en votos; en las cuencas mineras ganó en {NW[NCU_PSOE]} de diez. '
      f'Para el 29N, la media de encuestas da al PP {NW[E29["PP"]]} de los 7 diputados, al PSOE {NW[E29["PSOE"]]} y a Vox {NW[E29["VOX"]]}.',
      '12 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ok')
