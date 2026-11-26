"""«Lo que las encuestas no dicen» (26-11-2026): cuánto fallaron las encuestas en las 30 elecciones con datos desde 2015.

Pieza histórica: no lleva ninguna encuesta de las generales del 29N (veda, art. 69.7 de la LOREG).

Media simple de la última encuesta de cada empresa publicada en las dos semanas anteriores a la veda, frente al resultado,
para PP, PSOE, Vox y Cs (las familias que se emparejan sin ambigüedad), y solo los partidos con al menos un 3 % de los votos.
- Generales de noviembre de 2019 y julio de 2023: lo mismo que la pieza encuestas-error-2023-2019-29n (encuestas_error_2023.py),
  con sus mismas ventanas (del 20 de octubre al 3 de noviembre de 2019 y del 3 al 17 de julio de 2023) y resultados de Interior
  con voto exterior (actualidad/src/sistema/simulador.json), sobre votos válidos.
- Autonómicas: resumenes/datos/encuestas_autonomicas_2015_2026.csv (encuestas_fallos_preparar.py): encuestas autonómicas de
  Electográfica publicadas entre 20 y 6 días antes de la votación (la última de cada empresa) y resultado sobre votos válidos de la
  ficha de Wikipedia de cada elección. En Navarra no se cuenta el PP, que en 2015-2019 fue con UPN.
Error: media de las encuestas menos resultado, en puntos. No entran (y la pieza lo dice): generales de 2015, 2016 y abril de 2019 y
autonómicas de marzo y mayo de 2015 y de abril y mayo de 2019 (sin encuestas de esas fechas en la recopilación de Electográfica);
Cataluña 2017 (todas las fichas fechadas el día de la votación); La Rioja (sin ficha de resultados descargada).
Uso, desde la raíz: python3 actualidad/src/resumenes/encuestas_fallos.py
"""
import json

import pandas as pd

from comun import BASE, RAIZ, barras, figura, pieza
from mapa_ccaa import COL, p
import types
# Las encuestas y resultados de 2019 y 2023 de la pieza del 17-11, sin su parte «Hoy» ni su pieza (que no se reescribe)
G = types.SimpleNamespace()
_g = {'__name__': 'encuestas_error_2023_base'}
exec(compile((RAIZ / 'actualidad/src/resumenes/encuestas_error_2023.py').read_text(encoding='utf-8').split('# --- Hoy ---')[0],
             'encuestas_error_2023.py', 'exec'), _g)
G.__dict__.update({k: _g[k] for k in ('M19', 'M23', 'RES19', 'RES23', 'R19', 'U19', 'U23')})

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'encuestas-fallos-elecciones-espana-29n'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#a69'
ELECTO = 'https://www.electografica.com/'
UMBRAL = 3.0
NOMBRE = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'CS': 'Cs'}
FAM = ['PP', 'PSOE', 'VOX', 'CS']

# --- Generales (mismas cifras que la pieza del 17-11) ---
E = []   # (elección, fecha, número de encuestas, {familia: (media, resultado)})
G19 = {**{k: (G.M19[k], G.RES19[k]) for k in ('PP', 'PSOE', 'VOX')}}
_cs19 = G.R19['Cs']
if _cs19 >= UMBRAL:
    G19['CS'] = (float(G.U19['CS'].mean()), _cs19)
E.append(('Generales noviembre 2019', '2019-11-10', len(G.U19), G19))
E.append(('Generales 2023', '2023-07-23', len(G.U23), {k: (G.M23[k], G.RES23[k]) for k in ('PP', 'PSOE', 'VOX')}))

# --- Autonómicas ---
d = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/encuestas_autonomicas_2015_2026.csv')
FUENTE_RES = {}
for el, g in d.groupby('eleccion', sort=False):
    res = g[g.tipo == 'resultado'].iloc[0]
    enc = g[g.tipo == 'encuesta']
    assert len(enc) and enc.encuestadora.is_unique, el
    fam = {}
    for k in FAM:
        if pd.notna(res[k]) and res[k] >= UMBRAL and enc[k].notna().any():
            fam[k] = (float(enc[k].mean()), float(res[k]))
    # solo las encuestas que dan algún dato de estos partidos
    E.append((el, res.fecha, int(enc[FAM].notna().any(axis=1).sum()), fam))
    FUENTE_RES[el] = res.fuente
E.sort(key=lambda t: t[1])
assert len(E) == 30, len(E)
assert all(e[2] for e in E), [e[0] for e in E if not e[2]]

FILAS = []   # una por elección y partido
for el, f, ne, fam in E:
    for k, (m, r) in fam.items():
        FILAS.append({'el': el, 'f': f, 'k': k, 'media': m, 'res': r, 'err': m - r})
F = pd.DataFrame(FILAS)
MAYOR = F.loc[F.err.abs().groupby(F.el).idxmax()].set_index('el')   # el mayor fallo de cada elección
MAYOR = MAYOR.loc[[e[0] for e in E]]
N_EL = len(E)
N_3 = int((MAYOR.err.abs() > UMBRAL).sum())
N_2 = int((MAYOR.err.abs() > 2).sum())
N_1 = int((MAYOR.err.abs() <= 1).sum())
TOP = MAYOR.reindex(MAYOR.err.abs().sort_values(ascending=False).index)
T1, T2, T3, T4 = (TOP.iloc[i] for i in range(4))
assert (T1.name, T1.k) == ('Andalucía 2022', 'PP') and (T2.name, T2.k) == ('Andalucía 2018', 'VOX'), TOP.head()
NE = dict((e[0], e[2]) for e in E)

# Hacia dónde: en cuántas elecciones se quedaron cortas con cada partido
DIR = {k: (int((F[F.k == k].err < 0).sum()), int((F[F.k == k].err > 0).sum()), int(len(F[F.k == k])), float(F[F.k == k].err.mean()))
       for k in FAM}
MEDIO = float(F.err.abs().mean())
SUB_DER = int(((F.k.isin(['PP', 'VOX'])) & (F.err < 0)).sum())
N_DER = int((F.k.isin(['PP', 'VOX'])).sum())
# el bloque de la derecha (PP + Vox) en las elecciones donde se presentan los dos con más del 3 %
B = F[F.k.isin(['PP', 'VOX'])].groupby('el').filter(lambda g: len(g) == 2).groupby('el').err.sum()
B_CORTA, B_N = int((B < 0).sum()), int(len(B))
B_NO = [e[0] for e in E if e[0] in B.index and B[e[0]] >= 0]
assert all(e[1] >= '2023' for e in E if e[0] in B_NO)
NOMB = lambda el: 'las generales de ' + el[10:].replace(' ', ' de ') if el.startswith('Generales') and ' ' in el[10:] else ('las generales de ' + el[-4:] if el.startswith('Generales') else el)
assert 'Generales 2023' in B_NO
POCAS = [e[0] for e in E if e[2] <= 3]
PAL = {4: 'cuatro', 5: 'cinco', 6: 'seis', 9: 'nueve'}
w = lambda v: PAL.get(v, str(v))

# --- Gráficos ---
COLS = {'PP': COL['PP'], 'PSOE': COL['PSOE'], 'VOX': COL['VOX'], 'CS': COL['CS']}
s1 = lambda v: ('+' if v > 0 else '−') + p(abs(v))
g_mayor = figura(f'En {N_3} de {N_EL} elecciones, las encuestas fallaron por más de {p(UMBRAL)[:-2]} puntos con algún partido',
                 'El mayor error de la media de encuestas en cada elección, en puntos: media de la última encuesta de cada empresa antes de la veda menos el resultado. '
                 'Partido con el que más se equivocaron: «+» si le dieron de más, «−» si de menos',
                 barras([(el.replace('Comunitat Valenciana', 'C. Valenciana'), abs(r.err), COLS[r.k], f'{NOMBRE[r.k]} {s1(r.err)}') for el, r in TOP.iterrows()], 8,
                        'Mayor error de las encuestas en cada elección desde 2015', W=400, ml=150, alto=22, linea=(UMBRAL, '3 puntos'), separar=True),
                 f'Fuente: encuestas recopiladas por <a href="{ELECTO}">Electográfica</a>; resultados de Ministerio del Interior (generales, con voto exterior) '
                 'y de la ficha de cada elección autonómica en Wikipedia, sobre votos válidos. PP, PSOE, Vox y Cs, cuando sacaron al menos el 3 %. Cálculo propio.',
                 [(NOMBRE[k], COLS[k]) for k in FAM],
                 (['Elección', 'Encuestas', 'PP', 'PSOE', 'Vox', 'Cs'],
                  [[el, str(ne)] + [s1(fam[k][0] - fam[k][1]) if k in fam else '–' for k in FAM] for el, f, ne, fam in E]))

g_dir = figura('No fallan siempre hacia el mismo lado',
               'Elecciones en las que la media de encuestas dio a cada partido menos de lo que sacó (barra de arriba) y más (barra de abajo), de las 30 desde 2015',
               barras([(f'{NOMBRE[k]} · menos', DIR[k][0], COLS[k], f'{DIR[k][0]} de {DIR[k][2]}') for k in FAM] +
                      [(f'{NOMBRE[k]} · más', DIR[k][1], 'var(--muted)', f'{DIR[k][1]} de {DIR[k][2]}') for k in FAM], 30,
                      'Elecciones en que las encuestas dieron a cada partido menos o más de lo que sacó', W=400, ml=110, alto=22, separar=True),
               'Fuente: Electográfica, Ministerio del Interior y Wikipedia. Cálculo propio.',
               None,
               (['Partido', 'Elecciones', 'Le dieron menos', 'Le dieron más', 'Error medio (puntos)'],
                [[NOMBRE[k], str(DIR[k][2]), str(DIR[k][0]), str(DIR[k][1]), s1(DIR[k][3])] for k in FAM]))

# --- Texto ---
fr = lambda r: f'{NOMBRE[r.k]}: {p(r.media)} % en las encuestas y {p(r.res)} % en las urnas'
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">Desde el martes 24 no se puede publicar ninguna encuesta de las elecciones generales del 29N: la <a href="{LOREG}">ley electoral</a> lo prohíbe en los cinco días anteriores a la votación. Las últimas que se publicaron dicen dónde estaba cada partido cuando se hicieron. Lo que no dicen es cuánto se equivocan las encuestas en España. Aquí está la cuenta de las {N_EL} elecciones desde 2015 de las que tengo encuestas y resultado: las generales de noviembre de 2019 y de 2023 y {N_EL - 2} autonómicas.</p>
<p data-tipo="contexto">No son todas. Faltan las generales de 2015, 2016 y abril de 2019, las andaluzas de marzo de 2015, las valencianas de abril de 2019 y las autonómicas de mayo de 2015 y de mayo de 2019, porque la recopilación de encuestas de Electográfica que uso no tiene encuestas de esas fechas. Faltan también las catalanas de 2017, porque todas sus fichas llevan la fecha del día de la votación y no se puede saber cuál fue la última de cada empresa, y las riojanas de 2023, de las que no tengo el resultado en los mismos datos.</p>
<p data-tipo="dato">Para cada elección, tomo la última encuesta de cada empresa publicada en las dos semanas anteriores a la veda, hago la media y la comparo con el resultado de PP, PSOE, Vox y Cs. En <strong>{N_3} de las {N_EL}</strong>, la media se equivocó en más de tres puntos con al menos uno de ellos. En {N_2}, en más de dos. Solo en {w(N_1)} acertó con todos por un punto o menos.</p>
{g_mayor}
<h2>Los mayores sustos</h2>
<p data-tipo="dato">El mayor fallo fue en <strong>Andalucía en 2022</strong>: las {NE[T1.name]} encuestas daban de media al PP el {p(T1.media)} % y sacó el {p(T1.res)} %, {p(abs(T1.err))} puntos más, con mayoría absoluta. Le sigue <strong>Andalucía en 2018</strong>, cuando Vox entró en un parlamento por primera vez: le daban el {p(T2.media)} % y sacó el {p(T2.res)} %, {p(abs(T2.err))} puntos más. Detrás vienen {T3.name} ({fr(T3)}) y {T4.name} ({fr(T4)}).</p>
<p data-tipo="dato">En las generales, el mayor error de 2023 fue con el PSOE: las {NE["Generales 2023"]} empresas le daban de media el {p(G.M23["PSOE"])} % y sacó el {p(G.RES23["PSOE"])} %. En noviembre de 2019, con Vox: le daban el {p(G.M19["VOX"])} % y sacó el {p(G.RES19["VOX"])} %.</p>
<h2>Hacia qué lado fallan</h2>
<p data-tipo="dato">Partido a partido, no hay un lado fijo. En las {DIR["VOX"][2]} elecciones en que Vox pasó del 3 %, las encuestas le dieron menos de lo que sacó en {DIR["VOX"][0]} y más en {w(DIR["VOX"][1])}. Con el PP, menos en {DIR["PP"][0]} de {DIR["PP"][2]}. Con el PSOE, menos en {DIR["PSOE"][0]} de {DIR["PSOE"][2]}.</p>
<p data-tipo="dato">Sumados, el patrón es más claro. En las {B_N} elecciones en que PP y Vox pasaron los dos del 3 %, la media de encuestas se quedó corta con lo que sacaron juntos en <strong>{B_CORTA}</strong>. Las {w(len(B_NO))} excepciones son de 2023 en adelante: {", ".join(NOMB(x) for x in B_NO[:-1])} y {NOMB(B_NO[-1])}. Que haya pasado tantas veces no quiere decir que vaya a repetirse, y en las generales de 2023 las encuestas les dieron más de lo que sacaron.</p>
{g_dir}
<p data-tipo="dato">De media, el error con cada partido fue de {p(MEDIO)} puntos, arriba o abajo. Es lo que cabe esperar: la media de varias encuestas recoge el ruido de cada muestra, pero no los errores que comparten todas, como la gente que decide su voto en la última semana o la que no contesta.</p>
<h2>Qué no dicen estos datos</h2>
<p data-tipo="contexto">Que las encuestas fallaran en un sentido en una elección no dice hacia dónde fallarán en la siguiente: en 2019 se quedaron cortas con Vox y en 2023, con el PSOE. Las empresas, además, cambian sus métodos después de cada error. Y en algunas autonómicas hubo muy pocas encuestas en las dos últimas semanas: {w(len(POCAS))} elecciones tienen tres o menos ({", ".join(POCAS[:-1])} y {POCAS[-1]}).</p>
<p data-tipo="contexto">Lo que sí dicen es cuánto margen conviene darles. Un error de tres puntos con un partido no es raro, y en una elección ajustada basta para cambiar quién queda primero o si un bloque llega a la mayoría absoluta.</p>
'''

preguntas = [
    ('¿Cuánto fallan las encuestas electorales en España?',
     f'En {N_3} de las {N_EL} elecciones con datos desde 2015, la media de las últimas encuestas se equivocó en más de tres puntos con al menos un partido. De media, el error con cada partido fue de {p(MEDIO)} puntos.'),
    ('¿Cuál ha sido el mayor fallo de las encuestas en España?',
     f'Andalucía 2022: las encuestas daban al PP el {p(T1.media)} % y sacó el {p(T1.res)} %. Le sigue Andalucía 2018, con Vox: {p(T2.media)} % en las encuestas y {p(T2.res)} % en las urnas.'),
    ('¿Las encuestas se quedan cortas con la derecha?',
     f'A menudo, pero no siempre. Sumados PP y Vox, la media de encuestas se quedó corta en {B_CORTA} de las {B_N} elecciones en que los dos pasaron del 3 %. En las generales de 2023 fue al revés: les dieron más de lo que sacaron.'),
]
enlaces = (f'{L("veda-encuestas-29n", "Veda de encuestas")} · '
           f'<a href="{BASE}elecciones/resultados-elecciones-generales-2026/">Resultados de las elecciones generales 2026</a>')
foot = ('Datos: encuestas recopiladas por Electográfica, con la fuente original de cada una; Ministerio del Interior, resultados de las generales de noviembre de 2019 y de 2023 con voto exterior; '
        'resultados de las autonómicas de la ficha de cada elección en Wikipedia. Cálculo: actualidad/src/resumenes/encuestas_fallos.py.')

DATOS = {'E': [[el, f, ne, {k: [round(m, 3), round(r, 3)] for k, (m, r) in fam.items()}] for el, f, ne, fam in E],
         'N_EL': N_EL, 'B_NO': B_NO, 'N_3': N_3, 'N_2': N_2, 'N_1': N_1, 'MEDIO': MEDIO,
         'DIR': {k: list(v) for k, v in DIR.items()}, 'B_CORTA': B_CORTA, 'B_N': B_N, 'POCAS': POCAS,
         'TOP': [[el, r.k, r.media, r.res, r.err] for el, r in TOP.head(4).iterrows()],
         'G': {'M23': G.M23, 'RES23': G.RES23, 'M19': G.M19, 'RES19': G.RES19}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Lo que las encuestas no dicen',
      f'Las encuestas fallaron por más de 3 puntos en {N_3} de {N_EL} elecciones analizadas desde 2015: Andalucía 2022 y 2018, los mayores sustos',
      f'Lo que las encuestas no dicen: cuánto se equivocan. En {N_3} de las {N_EL} elecciones analizadas desde 2015 fallaron por más de tres puntos con algún partido; '
      f'en Andalucía 2022, el PP sacó {p(abs(T1.err))} más de lo previsto.',
      '26 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('N', N_EL, 'N3', N_3, 'N2', N_2, 'N1', N_1, 'MEDIO', round(MEDIO, 2), 'DIR', DIR, 'B', B_CORTA, B_N, 'POCAS', POCAS)
print(TOP[['k', 'media', 'res', 'err']].round(2).to_string())
