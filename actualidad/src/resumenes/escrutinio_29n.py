"""Escrutinio de las elecciones generales del 29N: cómo seguirlo en directo y cuándo es definitivo (pieza de servicio del 23-11-2026).

- Escrutinio provisional (recuento en cada mesa) y escrutinio definitivo del 4 al 7 de diciembre por las juntas electorales provinciales;
  sesiones constitutivas de las Cortes el 23 de diciembre a las 10.00; electores (38.728.356, 35.958.711 residentes en España y
  2.769.645 en el extranjero): guía de Interior en La Moncloa (6-11-2026).
- Escrutinio general el quinto día siguiente al de la votación (LOREG, art. 103.1) y voto de los residentes en el extranjero
  (art. 75).
- Lo que pasó en Madrid en 2023 (136 y 122 escaños la noche, 137 y 121 tras el voto exterior; recursos del PSOE): Maldita.es (1-8-2023,
  actualizado), con el acta del voto exterior de la Junta Electoral Provincial de Madrid.
- Electores residentes en el extranjero por provincia, 2023 y 2026: data/censo/censo_municipios_2023_2026.csv (INE, Oficina del Censo
  Electoral; src/censo_ine.py). Los totales de 2026 coinciden con los de la guía de Interior.
Uso, desde la raíz: python3 actualidad/src/resumenes/escrutinio_29n.py
"""
import json
from datetime import date, timedelta

import pandas as pd

from comun import BASE, POP_ESTILO, POP_JS, RAIZ, barras, esc, figura, mapa_provincias, n, pieza

SLUG = 'escrutinio-elecciones-generales-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L75, L103 = LOREG + '#asetentaycinco', LOREG + '#acientotres'
GUIA = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/guia-dudas-elecciones-generales-29n.aspx'
MALDITA = 'https://maldita.es/malditateexplica/20230801/elecciones-madrid-psoe-voto-nulo/'
MONCLOA23 = 'https://www.lamoncloa.gob.es/serviciosdeprensa/notasprensa/interior/paginas/2023/200723-seguimiento-resultados-elecciones-generales-23j.aspx'
RES = f'{BASE}elecciones/resultados-elecciones-generales-2026/'
OFICIAL = 'https://29neleccionesgenerales.es/'

# ---------- Fechas ----------
VOTO = date(2026, 11, 29)
ESCR = VOTO + timedelta(days=5)                 # art. 103.1: quinto día siguiente
assert ESCR == date(2026, 12, 4) and ESCR.weekday() == 4
CORTES = date(2026, 12, 23)                      # guía de Interior: sesiones constitutivas, 10.00
assert CORTES.weekday() == 2                     # miércoles

# ---------- Electores (INE) ----------
C = pd.read_csv(RAIZ / 'data/censo/censo_municipios_2023_2026.csv', dtype={'mun_code': str})
C['prov'] = C.mun_code.str[:2]
CER26, CERA26, CER23, CERA23 = (int(C[k].sum()) for k in ('cer_2026', 'cera_2026', 'cer_2023', 'cera_2023'))
assert (CER26, CERA26, CER26 + CERA26) == (35958711, 2769645, 38728356)   # los de la guía de Interior
PCERA = CERA26 / (CER26 + CERA26) * 100
SUBE_CERA = (CERA26 / CERA23 - 1) * 100
assert round(PCERA, 1) == 7.2 and round(SUBE_CERA) == 19

M = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'provincia'])
NOMP = dict(zip(M.mun_code.str[:2], M.provincia.str.split('/').str[0].replace({'Araba': 'Álava'})))
G = C.groupby('prov')[['cer_2026', 'cera_2026', 'cer_2023', 'cera_2023']].sum().reset_index()
G['pct'] = G.cera_2026 / (G.cer_2026 + G.cera_2026) * 100
G['sube'] = (G.cera_2026 / G.cera_2023 - 1) * 100
G['nombre'] = G.prov.map(NOMP)
assert len(G) == 52 and G.nombre.notna().all()
G = G.sort_values('pct', ascending=False).reset_index(drop=True)
OUR, LUG = G.iloc[0], G.iloc[1]
assert (OUR.nombre, LUG.nombre) == ('Ourense', 'Lugo') and round(OUR.pct, 1) == 30.8
MAD = G[G.prov == '28'].iloc[0]
MAS10 = G[G.pct > 10]
N10 = len(MAS10)
assert N10 == 11 and set(MAS10.prov) == {'32', '27', '36', '15', '49', '33', '38', '24', '37', '42', '52'}, N10
assert G.sube.idxmax() == G.index[G.prov == '28'][0]
MIN = G.iloc[-1]
assert MIN.nombre == 'Ciudad Real'

ACC = 'var(--acc)'
TOP = G.head(15)
g_bar = figura(f'En Ourense, casi uno de cada tres electores vive en el extranjero',
               'Electores residentes en el extranjero sobre el censo total de cada provincia para el 29N, en porcentaje. Las 15 provincias con más',
               barras([(r.nombre, r.pct, ACC, f'{p(r.pct)} %') for r in TOP.itertuples()], 35, 'Electores en el extranjero por provincia',
                      W=400, ml=130, alto=22),
               'Fuente: INE, Oficina del Censo Electoral, censo para las elecciones del 29N (cerrado el 1 de agosto de 2026). Cálculo propio.',
               None,
               (['Provincia', 'En el extranjero', 'Total', '% en el extranjero', 'Cambio desde 2023 (%)'],
                [[esc(r.nombre), n(r.cera_2026), n(r.cer_2026 + r.cera_2026), p(r.pct), ('+' if r.sube >= 0 else '−') + p(abs(r.sube))] for r in G.itertuples()]))
TR = [(0, 4, .3, 'Menos del 4 %'), (4, 7, .55, 'Del 4 al 7 %'), (7, 12, .8, 'Del 7 al 12 %'), (12, 101, 1, 'El 12 % o más')]
op = {r.prov: next(o for a, b, o, _ in TR if a <= r.pct < b) for r in G.itertuples()}
g_mapa = figura('Donde más pesa el voto de fuera: Galicia, Asturias y Castilla y León',
                'Electores residentes en el extranjero sobre el censo total de cada provincia para el 29N. Toca o pasa el ratón por una provincia para ver sus datos',
                '<div data-pop="prov">' + mapa_provincias({r.prov: ACC for r in G.itertuples()}, {}, 'Electores en el extranjero por provincia', op, claves=True) + '</div>',
                'Fuente: INE, Oficina del Censo Electoral. Cálculo propio.',
                [(t, f'color-mix(in srgb, {ACC} {round(o * 100)}%, transparent)') for _, _, o, t in TR])
POP = {r.prov: (f'<b>{esc(r.nombre)}</b><br>Electores en el extranjero: {n(r.cera_2026)}<br>{p(r.pct)} % del censo de la provincia<br>'
                f'En 2023: {n(r.cera_2023)} ({"+" if r.sube >= 0 else "−"}{p(abs(r.sube))} %)') for r in G.itertuples()}
GAL_AST = G[G.prov.isin(['32', '27', '36', '15', '33'])]
assert set(G.head(6).prov) == {'32', '27', '36', '15', '49', '33'}

# ---------- Madrid, 2023 (Maldita.es, con el acta de la Junta Electoral Provincial) ----------
M23 = dict(pp_noche=136, psoe_noche=122, pp_def=137, psoe_def=121, mad_pp=(15, 16), mad_psoe=(11, 10), dif_noche=1700, dif_def=1323,
           nulos=30241, cera_pp=19006, cera_psoe=10411)
assert M23['pp_def'] - M23['pp_noche'] == 1 and M23['psoe_noche'] - M23['psoe_def'] == 1

JORNADA = [
    ('Domingo 29, 20.00', 'Cierran los colegios y empieza el recuento en cada mesa',
     'Es el escrutinio provisional: el presidente de la mesa lee en voz alta cada papeleta y al final publica el acta con el resultado.'),
    ('Domingo 29, desde las 21.00', 'Interior publica los resultados provisionales',
     f'En 2023 empezó a esa hora, tras el cierre en Canarias. Aquí, en <a href="{RES}">la página de resultados</a>.'),
    ('Del viernes 4 al lunes 7 de diciembre', 'Escrutinio definitivo',
     f'Las juntas electorales provinciales revisan las actas de todas las mesas y cuentan el voto de los residentes en el extranjero (<a href="{L103}">artículo 103 de la LOREG</a>).'),
    ('Después del escrutinio', 'Proclamación de los electos y posibles recursos',
     'Los partidos pueden reclamar ante la junta provincial y, después, ante la Junta Electoral Central y los tribunales.'),
    ('Miércoles 23 de diciembre, 10.00', 'Se constituyen el Congreso y el Senado', f'La fecha la fija el decreto de convocatoria (<a href="{GUIA}">guía de Interior</a>).'),
]
tabla = ('<div class="tbl"><table><thead><tr><th>Cuándo</th><th>Qué pasa</th></tr></thead><tbody>'
         + ''.join(f'<tr><td><strong>{h}</strong></td><td><strong>{q}</strong>. {d}</td></tr>' for h, q, d in JORNADA)
         + '</tbody></table></div>')

cuerpo = f'''
<p data-tipo="contexto">Lo que se verá en las pantallas la noche del domingo 29 de noviembre es el escrutinio provisional de las elecciones generales: el recuento que hace cada una de las mesas al cerrar los colegios. El resultado oficial llega después. Según la <a href="{GUIA}">guía de Interior para el 29N</a>, «el escrutinio definitivo de las elecciones a Cortes Generales del 29 de noviembre se realizará del 4 al 7 de diciembre por las Juntas Electorales Provinciales». En medio quedan por contar los votos de {n(CERA26)} electores que viven en el extranjero.</p>
<h2>El calendario, del recuento a las Cortes</h2>
{tabla}
<h2>La noche: el escrutinio provisional</h2>
<p data-tipo="contexto">A las 20.00, el presidente de cada mesa anuncia el final de la votación. Si aún queda gente en el local o en la puerta, la deja votar. Luego saca los sobres de la urna uno a uno, lee en voz alta el nombre de la candidatura y enseña cada papeleta a los vocales, interventores y apoderados. Al terminar, se resuelven las dudas y las protestas, se lee el resultado y se publica en un acta, de la que reciben copia los representantes de los partidos, según describe la guía de Interior.</p>
<p data-tipo="contexto">Ese recuento llega al Ministerio del Interior, que lo va publicando. En 2023 empezó «desde las 21 horas, tras el cierre de los colegios electorales en Canarias», según <a href="{MONCLOA23}">su nota de aquella campaña</a>; el horario de toda la noche está en {L("a-que-hora-resultados-elecciones-generales-29n", "la guía de a qué hora se sabrán los resultados")}. Desde esa hora, en esta web, el recuento de cada municipio en el mapa y el reparto de escaños en <a href="{RES}">la página de resultados de las elecciones generales 2026</a>. La web oficial de Interior para estas elecciones es <a href="{OFICIAL}">29neleccionesgenerales.es</a>.</p>
<h2>Por qué no es el definitivo</h2>
<p data-tipo="dato">El recuento de la noche no incluye el voto de los españoles que viven en el extranjero. Para el 29N son {n(CERA26)} electores, el {p(PCERA)} % del censo, un {p(SUBE_CERA)} % más que en 2023. Su voto llega a las juntas electorales y se cuenta en el escrutinio general, el quinto día después de la votación, que este año cae en viernes 4 de diciembre (<a href="{L75}">artículo 75</a> y <a href="{L103}">artículo 103 de la LOREG</a>).</p>
<p data-tipo="dato">Ese voto no pesa igual en todas partes. En Ourense, el {p(OUR.pct)} % de los electores vive fuera; en Lugo, el {p(LUG.pct)} %. En {N10} provincias pasa del 10 %: las cuatro gallegas, Asturias, Zamora, León, Salamanca, Soria, Santa Cruz de Tenerife y Melilla. En Madrid es el {p(MAD.pct)} %, pero es donde más ha crecido desde 2023, un {p(MAD.sube)} %. En Ciudad Real, la que menos, es el {p(MIN.pct)} %. Cuánta de esa gente vota y a quién, provincia a provincia, en {L("ley-nietos-voto-exterior-29n", "la pieza sobre el voto de fuera")}.</p>
{g_bar}
{g_mapa}
<h2>Lo que pasó en 2023</h2>
<p data-tipo="contexto">En julio de 2023, el PP sacó {M23["pp_noche"]} escaños la noche electoral y el PSOE, {M23["psoe_noche"]}. En Madrid, el último diputado quedó para el PSOE por unos {n(M23["dif_noche"])} votos. En el escrutinio general, el voto de los electores de Madrid que viven en el extranjero dio al PP {n(M23["cera_pp"])} votos y al PSOE {n(M23["cera_psoe"])}, y el escaño cambió de manos: el PP pasó de {M23["mad_pp"][0]} a {M23["mad_pp"][1]} diputados en Madrid y el PSOE, de {M23["mad_psoe"][0]} a {M23["mad_psoe"][1]}. En el conjunto de España, {M23["pp_def"]} y {M23["psoe_def"]}, según <a href="{MALDITA}">Maldita.es</a>, que publicó el acta del voto exterior de la Junta Electoral Provincial.</p>
<p data-tipo="contexto">El PSOE pidió revisar los {n(M23["nulos"])} votos nulos de Madrid, con una diferencia final de {n(M23["dif_def"])} votos. La junta provincial lo rechazó, y después también la Junta Electoral Central, el Tribunal Supremo y el Tribunal Constitucional. El resultado de Madrid no cambió. Es el camino que tiene cualquier partido que no esté de acuerdo con el escrutinio.</p>
<h2>Qué mirar la noche del 29N</h2>
<p data-tipo="contexto">Si el último escaño de una provincia se decide por pocos votos, sobre todo en las que tienen mucho censo en el extranjero, puede cambiar del 4 al 7 de diciembre. Lo mismo vale para el Senado, que se cuenta a la vez. Los votos por correo de los residentes en España sí entran en el recuento de la noche: se entregan en las mesas y se cuentan con el resto, como se explica en {L("voto-correo-29n", "la pieza del voto por correo")}.</p>
'''

preguntas = [
    ('¿Qué es el escrutinio provisional?',
     f'El recuento que hace cada mesa al cerrar los colegios, el domingo a partir de las 20.00. Es el resultado que se publica esa noche. No incluye el voto de los residentes en el extranjero (<a href="{GUIA}">guía de Interior</a>).'),
    ('¿Cuándo es el escrutinio definitivo de las elecciones generales del 29N?',
     f'Del 4 al 7 de diciembre, a cargo de las juntas electorales provinciales, según la <a href="{GUIA}">guía de Interior</a>. Empieza el quinto día después de la votación (<a href="{L103}">artículo 103 de la LOREG</a>).'),
    ('¿Puede cambiar el reparto de escaños tras la noche electoral?',
     f'Sí. En 2023, el voto de los residentes en el extranjero cambió el último diputado de Madrid, del PSOE al PP (<a href="{MALDITA}">Maldita.es</a>).'),
    ('¿Cuántos españoles en el extranjero pueden votar el 29N?',
     f'{n(CERA26)}, el {p(PCERA)} % de los {n(CER26 + CERA26)} electores, según el INE.'),
    ('¿Cuándo se constituyen las nuevas Cortes?',
     f'El miércoles 23 de diciembre, a las 10.00 (<a href="{GUIA}">guía de Interior</a>).'),
]
enlaces = (f'<a href="{RES}">Resultados de las elecciones generales 2026</a> · {L("a-que-hora-resultados-elecciones-generales-29n", "A qué hora se sabrán los resultados")} · '
           f'{L("ley-nietos-voto-exterior-29n", "El voto de fuera")} · {L("como-votar-elecciones-generales-29n", "Cómo votar el 29N")}')
foot = ('Datos: Ministerio del Interior, guía de las elecciones generales del 29N (6-11-2026); Ley Orgánica del Régimen Electoral General, artículos 75 y 103; '
        'INE, censo electoral por municipio para 2023 y para el 29N; Maldita.es, escrutinio de Madrid en 2023. Cálculo: escrutinio_29n.py, en actualidad/src/resumenes.')

DATOS = {'CER26': CER26, 'CERA26': CERA26, 'CER23': CER23, 'CERA23': CERA23, 'PCERA': round(PCERA, 3), 'SUBE_CERA': round(SUBE_CERA, 3), 'N10': N10,
         'PROV': [{'nombre': r.nombre, 'cera': int(r.cera_2026), 'pct': round(r.pct, 3), 'sube': round(r.sube, 3)} for r in G.itertuples()],
         'M23': M23, 'POP': {'prov': POP}, 'MAD': {'pct': round(MAD.pct, 3), 'sube': round(MAD.sube, 3)}}
datos_js = POP_ESTILO + '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';' + POP_JS + '</script>\n'

TITULO = 'Escrutinio de las elecciones generales del 29N: cómo seguirlo en directo y cuándo es definitivo'
DEK = (f'La noche del domingo se verá el recuento de las mesas. El definitivo llega del 4 al 7 de diciembre, con el voto de {n(CERA26)} electores que viven fuera: '
       'en 2023 cambió un escaño en Madrid.')
pieza(SLUG, 'Escrutinio del 29N', TITULO, DEK, '23 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print(G.head(14)[['nombre', 'pct', 'sube']].to_string())
