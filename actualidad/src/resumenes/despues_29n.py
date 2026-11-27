"""Después de las elecciones generales del 29N: cuándo se constituyen las Cortes y los plazos de la investidura (pieza de servicio del 23-11-2026).

- Reglas: Constitución, artículos 68.6 (Congreso convocado en 25 días), 99 (investidura) y 101 (Gobierno en funciones), texto
  consolidado del BOE. LOREG, artículo 167.4 (decreto de disolución del artículo 99.5, refrendado por el presidente del Congreso).
- Fecha de las Cortes del 29N: guía de Interior en La Moncloa (6-11-2026), «el 23 de diciembre a las 10.00».
- Fechas de cada legislatura: Congreso de los Diputados, «Sesiones de investidura» (congreso.es/es/cem/sesiones-de-investidura),
  copiadas a datos/investiduras_1982_2023.csv. Fecha de la investidura: la de la votación en que se otorgó la confianza o, si la
  página no la da, el último día de la sesión. 1979 no está: la página da la sesión constitutiva después de la investidura.
Uso, desde la raíz: python3 actualidad/src/resumenes/despues_29n.py
"""
import json
import pathlib
from datetime import date

import pandas as pd

from comun import BASE, barras, esc, figura, n, pieza

AQUI = pathlib.Path(__file__).resolve().parent
SLUG = 'despues-elecciones-generales-29n-investidura'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
CE = 'https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229'
C68, C99, C101 = CE + '#a68', CE + '#a99', CE + '#a101'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#acientosesentaysiete'
GUIA = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/guia-dudas-elecciones-generales-29n.aspx'
CONG = 'https://www.congreso.es/es/cem/sesiones-de-investidura'
MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
f = lambda d: f'{d.day} de {MESES[d.month - 1]}'
fa = lambda d: f'{f(d)} de {d.year}'

# ---------- Datos ----------
H = pd.read_csv(AQUI / 'datos/investiduras_1982_2023.csv', parse_dates=['eleccion', 'constitucion', 'investidura'])
H['a_cortes'] = (H.constitucion - H.eleccion).dt.days
H['a_inv'] = (H.investidura - H.eleccion).dt.days
H['año'] = H.eleccion.dt.year
assert len(H) == 14 and H.a_cortes.between(19, 25).all()
INV = H[H.investidura.notna()].copy()
FALLA = H[H.investidura.isna()]
assert sorted(FALLA.año) == [2015, 2019]
MED = float(INV.a_inv.median())
RAPIDA, LENTA = INV.loc[INV.a_inv.idxmin()], INV.loc[INV.a_inv.idxmax()]
assert (RAPIDA.año, LENTA.año) == (2011, 2016)
ANTES15 = INV[INV.año < 2015]
DESDE15 = INV[INV.año >= 2015]
assert ANTES15.a_inv.max() == 62 and DESDE15.a_inv.min() == 58
SIN_GOB = (pd.Timestamp('2016-10-29') - pd.Timestamp('2015-12-20')).days
H23 = H[H.año == 2023].iloc[0]

ELEC, CORTES = date(2026, 11, 29), date(2026, 12, 23)
DIAS = (CORTES - ELEC).days
LIMITE = date(2026, 12, 24)            # 25 días después del 29 de noviembre (artículo 68.6)
assert (LIMITE - ELEC).days == 25 and DIAS == 24

# ---------- Gráfico ----------
ACC = 'var(--acc)'
filas = []
for r in H.itertuples():
    nom = f'{r.año}' + (' (abril)' if r.eleccion.month == 4 and r.año == 2019 else ' (nov.)' if r.año == 2019 else '')
    if pd.isna(r.investidura):
        filas.append((nom, 0, ACC, 'Sin investidura'))
    else:
        filas.append((nom, r.a_inv, ACC, f'{int(r.a_inv)} días'))
g_dias = figura('Desde 2015, ningún presidente ha sido investido antes de 58 días',
                'Días entre las elecciones generales y la investidura del presidente del Gobierno, de 1982 a 2023',
                barras(filas, 130, 'Días entre las elecciones y la investidura', W=400, ml=110, alto=24),
                f'Fuente: <a href="{CONG}">Congreso de los Diputados, sesiones de investidura</a>. Cálculo propio. En 2015 y en abril de 2019 ningún candidato obtuvo la confianza y se repitieron las elecciones.',
                None,
                (['Elecciones', 'Cortes constituidas', 'Investidura', 'Presidente', 'Días hasta la investidura'],
                 [[fa(r.eleccion), fa(r.constitucion), fa(r.investidura) if pd.notna(r.investidura) else 'No hubo', esc(r.presidente) if isinstance(r.presidente, str) else '—',
                   str(int(r.a_inv)) if pd.notna(r.a_inv) else '—'] for r in H.itertuples()]))

CAL = [('Domingo 29 de noviembre', 'Elecciones. Al cierre de los colegios, a las 20.00, empieza el recuento en las mesas.'),
       ('Del 4 al 7 de diciembre', 'Escrutinio general en las juntas electorales provinciales, con el voto de los residentes en el extranjero.'),
       ('Miércoles 23 de diciembre, 10.00', 'Sesión constitutiva del Congreso y del Senado: cada cámara elige su Mesa y su presidente.'),
       ('Después', 'El Rey consulta a los representantes de los grupos y propone un candidato a través del presidente del Congreso.'),
       ('Primera votación', 'El candidato necesita mayoría absoluta: 176 votos a favor.'),
       ('48 horas después', 'Segunda votación: basta con más síes que noes.'),
       ('Dos meses después de la primera votación', 'Si nadie ha sido investido, el Rey disuelve las Cortes y convoca nuevas elecciones.')]
t_cal = ('<div class="tbl"><table><thead><tr><th>Cuándo</th><th>Qué pasa</th></tr></thead><tbody>'
         + ''.join(f'<tr><td>{esc(a)}</td><td>{esc(b)}</td></tr>' for a, b in CAL) + '</tbody></table></div>')

cuerpo = f'''
<p data-tipo="dato">Las elecciones del 29N eligen a las Cortes, no al presidente del Gobierno. Al presidente lo elige después el Congreso, y para eso hay un calendario fijado por la Constitución. Las nuevas Cortes se constituyen el miércoles 23 de diciembre a las 10.00, según la <a href="{GUIA}">guía de Interior</a>. A partir de ahí no hay fecha para la investidura, pero sí un plazo: si dos meses después de la primera votación nadie la ha ganado, se repiten las elecciones.</p>
<h2>El calendario</h2>
{t_cal}
<p data-tipo="contexto">Fuente: <a href="{GUIA}">guía de Interior para el 29N</a> y artículos <a href="{C68}">68</a> y <a href="{C99}">99</a> de la Constitución.</p>
<h2>Las Cortes, el 23 de diciembre</h2>
<p data-tipo="dato">La Constitución dice que «el Congreso electo deberá ser convocado dentro de los veinticinco días siguientes a la celebración de las elecciones» (<a href="{C68}">artículo 68.6</a>). El 23 de diciembre son {DIAS} días después del 29N; el último posible sería el {f(LIMITE)}. Es lo habitual: desde 1982, las Cortes se han constituido siempre entre {int(H.a_cortes.min())} y {int(H.a_cortes.max())} días después de las elecciones. Ese día se elige al presidente del Congreso, que es quien después transmite al Congreso la propuesta del Rey y fija la fecha del debate.</p>
<h2>La investidura</h2>
<p data-tipo="dato">«El Rey, previa consulta con los representantes designados por los Grupos políticos con representación parlamentaria, y a través del Presidente del Congreso, propondrá un candidato a la Presidencia del Gobierno» (<a href="{C99}">artículo 99</a>). El candidato expone su programa y pide la confianza de la cámara. En la primera votación necesita «la mayoría absoluta de sus miembros», 176 de 350 diputados. Si no la consigue, se vota otra vez «cuarenta y ocho horas después» y basta «la mayoría simple»: más votos a favor que en contra.</p>
<p data-tipo="dato">Si el candidato pierde, se pueden proponer otros. El reloj empieza con la primera votación: «si transcurrido el plazo de dos meses, a partir de la primera votación de investidura, ningún candidato hubiere obtenido la confianza del Congreso, el Rey disolverá ambas Cámaras y convocará nuevas elecciones con el refrendo del Presidente del Congreso». Como no hay plazo para esa primera votación, el calendario completo depende de cuándo se celebre.</p>
<h2>Cuánto ha tardado otras veces</h2>
<p data-tipo="dato">De 1982 a 2011, la investidura llegó entre {int(ANTES15.a_inv.min())} y {int(ANTES15.a_inv.max())} días después de las elecciones; la más rápida fue la de {RAPIDA.presidente} en {RAPIDA.año}, a los {int(RAPIDA.a_inv)} días, según los datos del <a href="{CONG}">Congreso</a>. Desde 2015 ha tardado mucho más. Tras las elecciones de diciembre de 2015 y de abril de 2019, ningún candidato obtuvo la confianza y hubo que repetirlas. Mariano Rajoy fue investido en octubre de 2016, {int(LENTA.a_inv)} días después de las elecciones de junio y {SIN_GOB} después de las de diciembre de 2015. Pedro Sánchez lo fue en 2020, a los {int(INV[INV.año == 2019].a_inv.iloc[0])} días, y en 2023, a los {int(H23.a_inv)}, después de que Alberto Núñez Feijóo perdiera las dos votaciones de septiembre.</p>
{g_dias}
<h2>Mientras tanto, un Gobierno en funciones</h2>
<p data-tipo="dato">«El Gobierno cesa tras la celebración de elecciones generales» y «continuará en funciones hasta la toma de posesión del nuevo Gobierno» (<a href="{C101}">artículo 101</a>). Mientras no haya investidura, el Gobierno sigue, pero en funciones. Si hubiera que repetir las elecciones, el decreto de disolución lo refrenda el presidente del Congreso y no el del Gobierno (<a href="{LOREG}">artículo 167 de la LOREG</a>).</p>
<p data-tipo="contexto">Los diputados que salgan elegidos en cada provincia y los escaños de cada partido estarán en el mapa la noche del 29N. Cuántos votos hacen falta para un escaño en cada provincia, en {L("precio-del-escano-29n", "el precio del escaño")}.</p>
<p data-tipo="contexto">Actualización del 27 de noviembre. Antes de votar, a cuántos votos estuvo cada escaño en 2023, provincia a provincia: el <a href="{BASE}elecciones/voto-util-29n/">voto útil en cada provincia el 29N</a>.</p>
'''

preguntas = [
    ('¿Cuándo se constituyen las Cortes después del 29N?',
     f'El miércoles 23 de diciembre a las 10.00, según la <a href="{GUIA}">guía de Interior</a>. La Constitución da como máximo 25 días tras las elecciones.'),
    ('¿Cuántos votos necesita un candidato para ser investido?',
     f'En la primera votación, mayoría absoluta: 176 de 350. En la segunda, 48 horas después, basta con más votos a favor que en contra (<a href="{C99}">artículo 99</a>).'),
    ('¿Qué pasa si nadie consigue la investidura?',
     'Si dos meses después de la primera votación ningún candidato ha obtenido la confianza, el Rey disuelve las Cortes y convoca nuevas elecciones.'),
    ('¿Cuánto tardó la investidura en 2023?',
     f'{int(H23.a_inv)} días: Pedro Sánchez fue investido el 16 de noviembre de 2023, tras las elecciones del 23 de julio.'),
    ('¿Quién gobierna hasta la investidura?',
     f'El Gobierno que había, en funciones, hasta que tome posesión el nuevo (<a href="{C101}">artículo 101 de la Constitución</a>).'),
]
enlaces = (f'<a href="{BASE}elecciones/elecciones-29n-2026/">Elecciones 29N 2026</a> · {L("precio-del-escano-29n", "El precio del escaño")} · '
           f'{L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")}')
foot = ('Datos: Constitución (artículos 68, 99 y 101) y LOREG (artículo 167), BOE; Congreso de los Diputados, sesiones de investidura; '
        'Ministerio del Interior, guía de las elecciones del 29N. Cálculo: despues_29n.py, en actualidad/src/resumenes.')

DATOS = {'DIAS': DIAS, 'MED': MED, 'SIN_GOB': SIN_GOB,
         'H': [{'año': int(r.año), 'eleccion': r.eleccion.strftime('%Y-%m-%d'), 'constitucion': r.constitucion.strftime('%Y-%m-%d'),
                'a_cortes': int(r.a_cortes), 'a_inv': None if pd.isna(r.a_inv) else int(r.a_inv)} for r in H.itertuples()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = 'Después de las elecciones generales del 29N: cuándo se constituyen las Cortes y los plazos de la investidura'
DEK = ('Las Cortes se constituyen el 23 de diciembre. Para la investidura no hay fecha, pero sí un plazo: dos meses desde la primera votación. '
       f'Desde 2015, ningún presidente ha sido investido antes de {int(DESDE15.a_inv.min())} días.')
pieza(SLUG, 'Después del 29N', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print(H[['año', 'a_cortes', 'a_inv']].to_string())
