"""A qué hora se sabrán los resultados de las elecciones generales del 29N (pieza de servicio del 20-11-2026).

- Horario de votación: LOREG, arts. 80 y 84. Escrutinio general y voto de los residentes en el extranjero: arts. 75.10-11 y 103.1
  (quinto día siguiente al de la votación, desde la Ley Orgánica 12/2022).
- Horarios de la noche de 2023: nota del Ministerio del Interior en La Moncloa (20-7-2023): avances de las 14.00 y las 18.00,
  ruedas de prensa a las 14.30 y 18.30, primeros resultados desde las 21.00 tras el cierre en Canarias, comparecencia hacia las 22.30.
- Avances de participación por elección: data/censo/avances_participacion.csv (src/avances_participacion.py, ficheros por mesa
  de Interior), sobre el censo residente en España, sin voto por correo en los avances.
Uso, desde la raíz: python3 actualidad/src/resumenes/resultados_hora_29n.py
"""
import json
from datetime import date, timedelta

import pandas as pd

from comun import BASE, RAIZ, barras, figura, n, pieza

SLUG = 'a-que-hora-resultados-elecciones-generales-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L75 = LOREG + '#asetentaycinco'
L80 = LOREG + '#aochenta'
L84 = LOREG + '#aochentaycuatro'
L103 = LOREG + '#acientotres'
MONCLOA23 = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/2023/200723-seguimiento-resultados-elecciones-generales-23j.aspx'
PART = f'{BASE}elecciones/participacion-29n-hora-a-hora/'
RES = f'{BASE}elecciones/resultados-elecciones-generales-2026/'

# ---------- Fechas ----------
VOTO = date(2026, 11, 29)
ESCR = VOTO + timedelta(days=5)            # art. 103.1: quinto día siguiente
assert ESCR == date(2026, 12, 4) and ESCR.weekday() == 4      # viernes 4 de diciembre

# ---------- Avances (Interior, por mesa) ----------
AV = pd.read_csv(RAIZ / 'data/censo/avances_participacion.csv', dtype={'mun_code': str})
G = AV.groupby('eleccion')[['censo', 'a14', 'a18', 'votantes']].sum()
PC = {e: {'14': 100 * r.a14 / r.censo, '18': 100 * r.a18 / r.censo, 'final': 100 * r.votantes / r.censo} for e, r in G.iterrows()}
P23, P19 = PC['2023_07'], PC['2019_11']
assert (round(P23['14'], 1), round(P23['18'], 1), round(P23['final'], 1)) == (40.5, 53.1, 70.4)
assert (round(P19['14'], 1), round(P19['18'], 1), round(P19['final'], 1)) == (37.9, 56.9, 69.9)
SALTO23 = P23['final'] - P23['18']
SALTO19 = P19['final'] - P19['18']

JORNADA = [
    ('8.00', 'Se constituyen las mesas', f'El presidente y los dos vocales se reúnen en el colegio (<a href="{L80}">artículo 80 de la LOREG</a>).'),
    ('9.00', 'Empieza la votación', f'Sigue sin interrupción hasta las 20.00 (<a href="{L84}">artículo 84</a>).'),
    ('14.00', 'Primer avance de participación', 'Votantes que han pasado por las mesas hasta esa hora. En 2023, Interior lo dio en rueda de prensa a las 14.30.'),
    ('18.00', 'Segundo avance', 'En 2023, a las 18.30. En Canarias, los avances se toman a las 13.00 y a las 17.00, hora local.'),
    ('20.00', 'Cierran los colegios en la Península, Baleares, Ceuta y Melilla', 'Empieza el recuento en cada mesa. En Canarias queda una hora.'),
    ('21.00', 'Cierran en Canarias y empiezan los resultados', 'En 2023, Interior empezó a publicar los resultados provisionales a esa hora, tras el cierre en Canarias.'),
    ('22.30', 'Comparecencia del Gobierno', 'En 2023, la comparecencia con los resultados provisionales fue hacia esa hora.'),
    ('Viernes 4 de diciembre', 'Escrutinio general', f'Las juntas electorales cuentan el voto de los residentes en el extranjero y lo suman (<a href="{L75}">artículo 75</a> y <a href="{L103}">artículo 103</a>).'),
]
tabla = ('<div class="tbl"><table><thead><tr><th>Hora (peninsular)</th><th>Qué pasa</th></tr></thead><tbody>'
         + ''.join(f'<tr><td><strong>{h}</strong></td><td><strong>{q}</strong>. {d}</td></tr>' for h, q, d in JORNADA)
         + '</tbody></table></div>')

filas = []
for et, k in (('14.00', '14'), ('18.00', '18'), ('Final', 'final')):
    filas.append((f'2023 · {et}', P23[k], 'var(--acc)', f'{p(P23[k])} %'))
for et, k in (('14.00', '14'), ('18.00', '18'), ('Final', 'final')):
    filas.append((f'Nov. 2019 · {et}', P19[k], 'var(--muted)', f'{p(P19[k])} %'))
g_av = figura(f'En 2023, a las 18.00 había votado el {p(P23["18"])} % del censo; al final, el {p(P23["final"])} %',
              'Participación sobre el censo residente en España en los avances de las 14.00 y las 18.00 y al cierre, en las generales de julio de 2023 y de noviembre de 2019. Los avances no cuentan el voto por correo',
              barras(filas, 80, 'Avances de participación en 2023 y 2019', W=380, ml=130, fmt=lambda v: f'{p(v)} %'),
              f'Fuente: Ministerio del Interior, avances de participación por mesa (recogidos en <a href="{PART}">la participación del 29N hora a hora</a>). Cálculo propio.')

cuerpo = f'''
<p data-tipo="contexto">Los colegios de las elecciones generales del 29N cierran a las 20.00 del domingo 29 de noviembre, pero los primeros resultados no llegarán hasta las 21.00 si el Ministerio del Interior repite el horario de 2023. Entonces empezó a publicarlos «desde las 21 horas, tras el cierre de los colegios electorales en Canarias», que votan con una hora menos, según su <a href="{MONCLOA23}">nota de aquella campaña</a>. Antes habrá dos datos de participación, a las 14.00 y a las 18.00. Y el resultado de la noche todavía no será el definitivo: el voto de los españoles que viven fuera se cuenta el viernes 4 de diciembre.</p>
<h2>La jornada, hora a hora</h2>
{tabla}
<p data-tipo="contexto">Horas de la Península. Las de 2023 son las de la nota de Interior; el horario de la votación y el del escrutinio general los fija la ley.</p>
<h2>Los avances de participación</h2>
<p data-tipo="dato">Los dos avances cuentan a los electores que han votado en persona en las mesas, sobre el censo de residentes en España. En julio de 2023, a las 14.00 había votado el {p(P23["14"])} % y a las 18.00, el {p(P23["18"])} %. La participación final fue del {p(P23["final"])} %: subió {p(SALTO23)} puntos entre las 18.00 y el cierre, porque el voto por correo, que aquel verano batió récords, se suma al final. En noviembre de 2019 subió {p(SALTO19)} puntos. Los avances de cada provincia y de cada municipio, y los del 29N cuando se conozcan, en <a href="{PART}">la participación del 29N hora a hora</a>.</p>
{g_av}
<h2>Por qué el resultado de la noche no es el definitivo</h2>
<p data-tipo="contexto">Lo que se publica el domingo es el escrutinio provisional: el recuento de cada mesa, sin el voto de los residentes en el extranjero. Esos votos llegan a las juntas electorales y se cuentan el día del escrutinio general, el quinto día después de la votación, que este año cae en viernes 4 de diciembre (<a href="{L103}">artículo 103</a> y <a href="{L75}">artículo 75</a>). No es un trámite: en 2023, el voto de fuera cambió el último diputado de Madrid, del PSOE al PP ({L("ley-nietos-voto-exterior-29n", "el voto de fuera que le dio un escaño al PP")}).</p>
<p data-tipo="contexto">Desde las 21.00, el mapa de esta web irá mostrando el recuento de cada municipio, y la página de <a href="{RES}">resultados de las elecciones generales 2026</a>, el reparto de escaños. Cómo votar y qué llevar, en {L("como-votar-elecciones-generales-29n", "la guía para votar el 29N")}.</p>
'''

preguntas = [
    ('¿A qué hora se sabrán los resultados de las elecciones generales del 29N?',
     f'Los colegios cierran a las 20.00. En 2023, Interior empezó a publicar los resultados provisionales a las 21.00, tras el cierre en Canarias, según su <a href="{MONCLOA23}">nota de prensa</a>.'),
    ('¿A qué hora se dan los datos de participación?',
     'Interior da dos avances, con los votantes hasta las 14.00 y hasta las 18.00. En 2023 los anunció a las 14.30 y a las 18.30.'),
    ('¿Cuándo es definitivo el resultado?',
     f'Tras el escrutinio general, el viernes 4 de diciembre, cuando se cuenta el voto de los residentes en el extranjero (<a href="{L103}">artículo 103 de la LOREG</a>).'),
    ('¿Por qué Canarias retrasa los resultados?',
     'Porque vota con una hora menos: sus colegios cierran a las 20.00 hora canaria, las 21.00 en la Península, y en 2023 Interior esperó a ese cierre para publicar resultados.'),
]
enlaces = (f'<a href="{PART}">Participación del 29N hora a hora</a> · <a href="{RES}">Resultados de las elecciones generales 2026</a> · '
           f'{L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")}')
foot = ('Datos: Ley Orgánica del Régimen Electoral General, artículos 75, 80, 84 y 103; Ministerio del Interior, nota sobre el seguimiento de los resultados del 23J (20-7-2023) '
        'y avances de participación por mesa de 2019 y 2023. Cálculo: actualidad/src/resumenes/resultados_hora_29n.py.')

DATOS = {'P23': {k: round(v, 3) for k, v in P23.items()}, 'P19': {k: round(v, 3) for k, v in P19.items()},
         'SALTO23': round(SALTO23, 3), 'SALTO19': round(SALTO19, 3)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'A qué hora los resultados',
      'A qué hora se sabrán los resultados de las elecciones generales del 29N',
      'Los colegios cierran a las 20.00, pero en 2023 los primeros resultados llegaron a las 21.00, al cerrar Canarias. '
      'Antes, dos avances de participación, a las 14.00 y a las 18.00. El voto de fuera se cuenta el viernes 4 de diciembre.',
      '20 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('P23', {k: round(v, 2) for k, v in P23.items()}, 'P19', {k: round(v, 2) for k, v in P19.items()}, round(SALTO23, 2), round(SALTO19, 2))
