"""Voto en blanco y voto nulo en las elecciones generales del 29N: qué cuenta y a quién afecta (pieza de servicio del 23-11-2026).

- Reglas: Ley Orgánica del Régimen Electoral General, artículos 96 (nulo y blanco), 97 y 108 (recuento) y 163 (umbral del 3 % y
  reparto), texto consolidado del BOE. Instrucción 1/2012 de la Junta Electoral Central sobre el artículo 96.2.
- Umbral y escaños de 2023 y noviembre de 2019, con voto exterior: actualidad/src/sistema/cifras.json (calcular.py, resultados
  por mesa de Interior). Para cada provincia: votos válidos, votos de candidaturas, blancos, último cociente y votos de cada
  lista sin escaño.
- Blancos y nulos por provincia, sin voto exterior: datos/blancos_nulos_provincias_2019_2023.csv, suma por provincia de
  /mnt/project-files/generales/datos/resultados_secciones_largo.csv (resultados por sección de Interior).
- Candidaturas de Escaños en Blanco el 29N: generales-2026/data/candidatos-congreso-29n.json.
Uso, desde la raíz: python3 actualidad/src/resumenes/blanco_nulo_29n.py
"""
import json
import pathlib

import pandas as pd

from comun import BASE, POP_ESTILO, POP_JS, RAIZ, esc, figura, mapa_provincias, n, pieza

AQUI = pathlib.Path(__file__).resolve().parent
SLUG = 'voto-blanco-nulo-elecciones-generales-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
p2 = lambda v: n(v, 2)
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L96, L163, L108 = LOREG + '#anoventayseis', LOREG + '#acientosesentaytres', LOREG + '#acientoocho'
JEC12 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2012-3859'
GUIA = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/guia-dudas-elecciones-generales-29n.aspx'

# ---------- Datos ----------
CIF = json.load(open(RAIZ / 'actualidad/src/sistema/cifras.json'))
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))
NOM = SIM['provincias']


def umbral(e):
    """Listas sin escaño a las que el voto en blanco dejó por debajo del 3 %, y listas por debajo del 3 % que habrían
    superado el último cociente (es decir, que se quedaron sin escaño por el umbral)."""
    R = CIF[e]['provincias']
    decide = [(R[q]['nombre'], k) for q in R for k, v in R[q]['perdidos_por_partido'].items()
              if 0.03 * R[q]['votos_candidaturas'] <= v < 0.03 * R[q]['validos']]
    quita = [(R[q]['nombre'], k) for q in R for k, v in R[q]['perdidos_por_partido'].items()
             if v < 0.03 * R[q]['validos'] and v > R[q]['ultimo_cociente']]
    activo = sorted(R[q]['nombre'] for q in R if R[q]['ultimo_cociente'] < 0.03 * R[q]['validos'])
    return decide, quita, activo


for e in ('2023_07', '2019_11'):
    d, q, a = umbral(e)
    assert d == [] and q == [] and a == ['Barcelona', 'Madrid'], (e, d, q, a)
C23 = CIF['2023_07']
BL23, VAL23, CAND23 = C23['blancos'], C23['validos'], C23['votos_candidaturas']
BL19 = CIF['2019_11']['blancos']
BCN, MAD = C23['provincias']['08'], C23['provincias']['28']
CUP = BCN['perdidos_por_partido']['CUP']
assert max(BCN['perdidos_por_partido'].values()) == CUP
CUP_PCT = 100 * CUP / BCN['validos']
BCN_UMB, BCN_SUBE = 0.03 * BCN['validos'], 0.03 * BCN['blancos']
BCN_ULT = BCN['ultimo_cociente']
MAD_SUBE = 0.03 * MAD['blancos']
OTRA = sorted((r for r in C23['provincias'].values() if r['nombre'] not in ('Madrid', 'Barcelona')), key=lambda r: r['umbral_efectivo_pct'])[0]
assert OTRA['nombre'] == 'Valencia' and OTRA['umbral_efectivo_pct'] > 5
PP = next(x for x in C23['partidos'] if x['partido'] == 'PP')
PP_VAL, PP_CAND = 100 * PP['votos'] / VAL23, 100 * PP['votos'] / CAND23
EB23 = {C23['provincias'][q]['nombre']: v for q in C23['provincias'] for k, v in C23['provincias'][q]['perdidos_por_partido'].items() if k == 'Escaños en Blanco'}
EB23_TOT = sum(EB23.values())
CAND29 = json.load(open(RAIZ / 'generales-2026/data/candidatos-congreso-29n.json'))
EB29 = sorted(NOM[q] for q, v in CAND29.items() if 'ESCAÑOS EN BLANCO' in v)
assert len(EB23) == 11 and len(EB29) == 12

B = pd.read_csv(AQUI / 'datos/blancos_nulos_provincias_2019_2023.csv', dtype={'prov': str})
assert (B.candidaturas + B.blancos + B.nulos == B.votantes).all()
B['pb'] = 100 * B.blancos / B.votantes           # sobre votantes, para comparar blancos y nulos
B['pn'] = 100 * B.nulos / B.votantes
B['pbv'] = 100 * B.blancos / (B.blancos + B.candidaturas)   # sobre válidos, como el dato oficial
B['nombre'] = B.prov.map(NOM)
T = B.groupby('eleccion')[['votantes', 'blancos', 'nulos']].sum()
T23, T19 = T.loc['2023_07'], T.loc['2019_11']
P23 = B[B.eleccion == '2023_07'].set_index('prov')
NULO_GANA = int((P23.nulos > P23.blancos).sum())
MAXB, MINB = P23.loc[P23.pbv.idxmax()], P23.loc[P23.pbv.idxmin()]
MAXN, MINN = P23.loc[P23.pn.idxmax()], P23.loc[P23.pn.idxmin()]
MAXB2 = P23.sort_values('pbv').iloc[-2]
assert (MAXB.nombre, MAXB2.nombre) == ('Lleida', 'Cádiz') and round(MAXB.pbv, 2) == round(MAXB2.pbv, 2)
assert NULO_GANA == 52
ZAR = P23.loc[(P23.nulos - P23.blancos).idxmin()]
assert ZAR.nombre == 'Zaragoza'
P19 = B[B.eleccion == '2019_11']
NULO19 = int((P19.nulos > P19.blancos).sum())
assert (MAXN.nombre, MINN.nombre) == ('Badajoz', 'Gipuzkoa'), (MAXN.nombre, MINN.nombre)
assert MINB.nombre == 'Álava', MINB.nombre
PEN = P23[~P23.index.isin(['51', '52'])]

# ---------- Gráfico ----------
ACC = 'var(--acc)'
TR = [(0, .6, .25, 'Menos del 0,6 %'), (.6, .8, .5, 'Del 0,6 al 0,8 %'), (.8, 1, .75, 'Del 0,8 al 1 %'), (1, 99, 1, 'El 1 % o más')]
op = {k: next(o for a, b, o, _ in TR if a <= r.pbv < b) for k, r in P23.iterrows()}
POP = {k: (f'<b>{esc(r.nombre)}</b><br>En blanco: {n(r.blancos)} ({p2(r.pbv)} % de los válidos)<br>Nulos: {n(r.nulos)} ({p2(r.pn)} % de los votantes)'
           ) for k, r in P23.iterrows()}
g_mapa = figura('El voto en blanco en cada provincia en 2023',
                'Votos en blanco sobre los votos válidos en las generales de julio de 2023. Toca o pasa el ratón por una provincia para ver también los nulos',
                '<div data-pop="prov">' + mapa_provincias({k: ACC for k in P23.index}, {}, 'Voto en blanco por provincia en 2023', op, claves=True) + '</div>',
                'Fuente: Ministerio del Interior, resultados por sección de las generales de 2023, sin el voto de los residentes en el extranjero. Cálculo propio.',
                [(t, f'color-mix(in srgb, {ACC} {round(o * 100)}%, transparent)') for _, _, o, t in TR],
                (['Provincia', 'En blanco', '% de los válidos', 'Nulos', '% de los votantes'],
                 [[esc(r.nombre), n(r.blancos), p2(r.pbv), n(r.nulos), p2(r.pn)] for _, r in P23.sort_values('pbv', ascending=False).iterrows()]))

PAPELETA = [('Sobre vacío', 'En blanco, y válido'),
            ('Dos o más papeletas del mismo partido en un sobre', 'Un voto válido para ese partido'),
            ('Papeletas de partidos distintos en un sobre', 'Nulo'),
            ('Papeleta sin sobre, o sobre o papeleta que no son los oficiales', 'Nulo'),
            ('Nombres tachados, añadidos o cambiados de orden, o una frase escrita', 'Nulo'),
            ('Papeleta rota o rasgada', 'Nulo'),
            ('Una pequeña cruz junto a un candidato, sin tachar nada', 'Válido para ese partido'),
            ('Senado: papeleta sin ninguna cruz', 'En blanco, y válido'),
            ('Senado: más cruces de las permitidas (tres en la mayoría de provincias)', 'Nulo')]
t_pap = ('<div class="tbl"><table><thead><tr><th>Qué hay en el sobre</th><th>Cómo cuenta</th></tr></thead><tbody>'
         + ''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>' for a, b in PAPELETA) + '</tbody></table></div>')

cuerpo = f'''
<p data-tipo="dato">El voto en blanco cuenta como voto válido; el nulo, no. Esa es toda la diferencia, y tiene una sola consecuencia para el reparto de escaños: el blanco entra en la cuenta del 3 % que necesita una lista para tener diputado en su provincia, y el nulo no entra en ninguna. Ninguno de los dos elige a nadie ni deja escaños vacíos. En las dos últimas generales, ningún escaño dependió del voto en blanco.</p>
<h2>Qué es blanco y qué es nulo</h2>
<p data-tipo="dato">La ley lo dice así: «Se considera voto en blanco, pero válido, el sobre que no contenga papeleta» y, en el Senado, «las papeletas que no contengan indicación a favor de ninguno de los candidatos» (<a href="{L96}">artículo 96 de la LOREG</a>). Es nulo el voto «emitido en sobre o papeleta diferente del modelo oficial», el de la papeleta sin sobre y el del sobre «que contenga más de una papeleta de distinta candidatura». Si hay dos papeletas del mismo partido, «se computará como un solo voto válido».</p>
<p data-tipo="dato">También anula el voto cualquier cambio en la papeleta del Congreso: nombres tachados, añadidos o en otro orden, o una «leyenda o expresión». La Junta Electoral Central precisó en su <a href="{JEC12}">Instrucción 1/2012</a> que es nula la papeleta con «cualquier tipo de alteración que no sea accidental», también si está «rota o rasgada», pero que vale la que tenga «una señal, cruz o aspa al lado de alguno de los candidatos» si no altera la papeleta ni expresa «reproche» a un candidato o partido. Cómo se rellena la del Senado, en {L("como-votar-elecciones-generales-29n", "la guía para votar el 29N")}.</p>
{t_pap}
<p data-tipo="contexto">Fuente: <a href="{L96}">artículo 96 de la LOREG</a> e <a href="{JEC12}">Instrucción 1/2012 de la Junta Electoral Central</a>. Si hay dudas sobre una papeleta, decide la mesa, y los apoderados pueden reclamar; el recuento oficial, con los blancos y los nulos de cada mesa, lo cierra la junta electoral provincial en el escrutinio general (<a href="{L108}">artículo 108</a>).</p>
<h2>A quién afecta el voto en blanco</h2>
<p data-tipo="dato">Los escaños se reparten por la ley D'Hondt entre las listas que tienen al menos «el 3 por 100 de los votos válidos emitidos en la circunscripción» (<a href="{L163}">artículo 163</a>). Como el blanco es válido, cada 100 votos en blanco suben ese listón en 3 votos. En la práctica, el 3 % solo pesa en Madrid y en Barcelona, las dos provincias que más diputados eligen. En las demás, el último escaño exige más votos que el umbral: en 2023, como poco, en torno al {p(OTRA['umbral_efectivo_pct'])} % de los válidos, en {OTRA['nombre']}. Así que allí el 3 % no llega a decidir nada.</p>
<p data-tipo="dato">En 2023, los {n(MAD['blancos'])} votos en blanco de Madrid subieron el listón {n(round(MAD_SUBE))} votos, y los {n(BCN['blancos'])} de Barcelona, {n(round(BCN_SUBE))}. De las listas que se quedaron sin escaño en esas dos provincias, la que más cerca estuvo del 3 % fue la CUP en Barcelona: {n(CUP)} votos, el {p2(CUP_PCT)} % de los válidos, cuando el 3 % eran {n(round(BCN_UMB))}. Sin los blancos, habría seguido por debajo, y le faltaban unos {n(round(BCN_ULT - CUP, -3))} votos para el último escaño aunque no hubiera umbral. Con los resultados por mesa de Interior, en julio de 2023 y en noviembre de 2019 no hubo ninguna lista que tuviera el escaño a su alcance y se quedara sin él por el 3 %, ni ninguna a la que los blancos dejaran por debajo.</p>
<p data-tipo="dato">El voto en blanco también baja el porcentaje oficial de todos los partidos, que se calcula sobre los válidos. En 2023, el PP sacó el {p(PP_VAL)} % de los votos válidos; sin contar los {n(BL23)} votos en blanco, habría sido el {p(PP_CAND)} %. A todos los partidos les quita lo mismo en proporción, y no les cambia los escaños.</p>
<p data-tipo="contexto">Votar a Escaños en Blanco no es votar en blanco: es una candidatura, y su papeleta cuenta como voto a esa lista. El 29N se presenta al Congreso en {len(EB29)} provincias; en 2023 se presentó en {len(EB23)} y sacó {n(EB23_TOT)} votos, frente a {n(BL23)} votos en blanco, con el voto exterior incluido.</p>
<h2>Y el voto nulo</h2>
<p data-tipo="dato">El nulo cuenta para la participación, porque es un votante más, pero no para el reparto: con los escaños pasa lo mismo que si esa persona se hubiera quedado en casa. En las generales de 2023 hubo {n(T23.nulos)} votos nulos y {n(T23.blancos)} en blanco, sin contar a los que votan desde el extranjero. Hubo más nulos que blancos en las 52 circunscripciones, aunque en {ZAR.nombre} la diferencia fue de {int(ZAR.nulos - ZAR.blancos)} votos. En noviembre de 2019 fueron {n(T19.nulos)} nulos y {n(T19.blancos)} blancos, y los nulos ganaron en {NULO19} circunscripciones. Cómo han cambiado desde 1977, en {L("voto-en-blanco", "la historia del voto en blanco")}.</p>
<p data-tipo="dato">El voto en blanco fue más alto en {MAXB.nombre} y {MAXB2.nombre}, el {p2(MAXB.pbv)} % de los válidos, y más bajo en {MINB.nombre}, el {p2(MINB.pbv)} %. El nulo pesó más en {MAXN.nombre}, el {p2(MAXN.pn)} % de los votantes, y menos en {MINN.nombre}, el {p2(MINN.pn)} %. Los datos no dicen por qué: un nulo puede ser una protesta o un error, y en el recuento no se distinguen.</p>
{g_mapa}
<p data-tipo="contexto">La noche del 29N, los blancos y los nulos de cada mesa aparecerán en el recuento provisional; el escrutinio definitivo es del 4 al 7 de diciembre, según la <a href="{GUIA}">guía de Interior</a>. Cuántos votos no eligieron a nadie en 2023, provincia a provincia, en {L("votos-sin-escano-29n", "los votos sin escaño")}.</p>
'''

preguntas = [
    ('¿Qué diferencia hay entre el voto en blanco y el voto nulo?',
     f'El voto en blanco, un sobre vacío, es válido y cuenta para el 3 % que necesita una lista para tener escaño. El nulo no cuenta para el reparto (<a href="{L96}">artículo 96 de la LOREG</a>).'),
    ('¿A quién beneficia el voto en blanco?',
     f'Sube un poco el listón del 3 %, que solo pesa en Madrid y Barcelona. En 2023 y en noviembre de 2019 no cambió ningún escaño.'),
    ('¿El voto en blanco deja escaños vacíos?',
     'No. Los escaños se reparten entre las listas con votos; el voto en blanco no elige a nadie. Escaños en Blanco es una candidatura, no el voto en blanco.'),
    ('¿Es nulo el voto si marco una cruz en la papeleta del Congreso?',
     f'Una pequeña cruz junto a un candidato vale si no altera la papeleta ni expresa reproche; tachar o añadir nombres o escribir algo la anula (<a href="{JEC12}">Instrucción 1/2012 de la Junta Electoral Central</a>).'),
    ('¿Cuántos votos en blanco y nulos hubo en 2023?',
     f'{n(T23.blancos)} en blanco y {n(T23.nulos)} nulos, sin contar el voto exterior; con él, {n(BL23)} en blanco.'),
]
enlaces = (f'{L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")} · {L("voto-en-blanco", "Historia del voto en blanco")} · '
           f'{L("votos-sin-escano-29n", "Votos sin escaño")} · <a href="{BASE}elecciones/elecciones-29n-2026/">Elecciones 29N 2026</a>')
foot = ('Datos: LOREG (artículos 96, 108 y 163) e Instrucción 1/2012 de la Junta Electoral Central, BOE; Ministerio del Interior, resultados por mesa '
        'de las generales de 2023 y noviembre de 2019 (con voto exterior) y por sección (sin él); candidaturas proclamadas para el 29N. '
        'Cálculo: blanco_nulo_29n.py, en actualidad/src/resumenes.')

DATOS = {'BL23': BL23, 'VAL23': VAL23, 'CAND23': CAND23, 'BL19': BL19, 'CUP': CUP, 'BCN_UMB': round(BCN_UMB), 'BCN_SUBE': round(BCN_SUBE),
         'BCN_ULT': BCN_ULT, 'MAD_SUBE': round(MAD_SUBE), 'PP_VAL': round(PP_VAL, 3), 'PP_CAND': round(PP_CAND, 3), 'EB23': EB23, 'EB29': EB29,
         'T23': {k: int(v) for k, v in T23.items()}, 'T19': {k: int(v) for k, v in T19.items()}, 'NULO_GANA': NULO_GANA, 'MAD_BL': MAD['blancos'], 'BCN_BL': BCN['blancos'], 'BCN_VAL': BCN['validos'], 'OTRA_PCT': OTRA['umbral_efectivo_pct'], 'NULO19': NULO19,
         'PROV': [{'prov': k, 'nombre': r.nombre, 'blancos': int(r.blancos), 'nulos': int(r.nulos), 'pbv': round(r.pbv, 3), 'pn': round(r.pn, 3)}
                  for k, r in P23.iterrows()],
         'POP': {'prov': POP}}
datos_js = POP_ESTILO + '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';' + POP_JS + '</script>\n'

TITULO = 'Voto en blanco y voto nulo en las elecciones generales del 29N: qué cuenta y a quién afecta'
DEK = (f'El blanco es válido y sube el listón del 3 %; el nulo no cuenta para el reparto. En 2023 hubo {n(T23.nulos)} nulos y '
       f'{n(T23.blancos)} blancos, y ningún escaño dependió de ellos.')
pieza(SLUG, 'Voto en blanco y nulo', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK)
print(NULO_GANA, MAXB.nombre, MAXB.pbv, MINB.nombre, MINB.pbv, MAXN.nombre, MAXN.pn, MINN.nombre, MINN.pn, CUP_PCT, BCN_ULT - CUP, PP_VAL, PP_CAND, EB23_TOT, EB29)
