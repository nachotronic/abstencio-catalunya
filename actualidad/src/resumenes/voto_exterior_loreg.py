"""Votar desde el extranjero el 29N, ley en mano (pieza del 26-11-2026).

- Ley Orgánica del Régimen Electoral General (LOREG), texto consolidado del BOE: artículos 31.2, 32.3, 75, 103.1 y 107.2.
- Ley Orgánica 12/2022 (BOE-A-2022-16018), que suprimió el voto rogado: preámbulo.
- Junta Electoral Central, Instrucción 1/2023 (BOE-A-2023-8463), sobre el voto de los electores del CERA.
- Electores del 29N: data/censo/censo_municipios_2023_2026.csv (INE, Oficina del Censo Electoral).
- Participación del CERA de 1986 a 2023 y voto exterior por provincia en 2023: datos/voto_exterior_cera_*.csv, que prepara
  voto_exterior_preparar.py con los resultados por mesa del Ministerio del Interior (municipio 999).
- Ley de nietos: providencia del Supremo del 20-11-2026 (El Independiente, con Europa Press) y auto del 24-11-2026 sobre las
  urnas de cartón (The Objective).
Uso, desde la raíz: python3 actualidad/src/resumenes/voto_exterior_loreg.py
"""
import json
from datetime import date, timedelta

import pandas as pd

from comun import BASE, RAIZ, barras, esc, figura, n, pieza

SLUG = 'voto-exterior-cera-loreg-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L31, L32, L75, L103, L107 = (LOREG + '#a' + k for k in ('treintayuno', 'treintaydos', 'setentaycinco', 'cientotres', 'cientosiete'))
LO12 = 'https://www.boe.es/buscar/doc.php?id=BOE-A-2022-16018'
JEC = 'https://www.boe.es/buscar/doc.php?id=BOE-A-2023-8463'
INDEP = 'https://www.elindependiente.com/espana/2026/11/20/el-ts-exige-a-la-jec-garantizar-que-163-355-nacionalizados-por-la-ley-de-nietos-no-voten-el-29-n/'
TOBJ = 'https://theobjective.com/espana/tribunales/2026-11-24/supremo-tumba-recurso-urnas-carton-nietos/'
RDP = 'https://doi.org/10.5944/rdp.120.2024.41766'
EP = 'https://www.europapress.es/nacional/noticia-gobierno-entrega-ts-listado-mas-160000-afectados-suspension-voto-ley-nietos-20261028160130.html'

# ---------- Fechas (LOREG, art. 75 y 103) ----------
VOTO = date(2026, 11, 29)
assert VOTO.weekday() == 6
d = lambda k: VOTO - timedelta(days=k)
URNA_INI, URNA_FIN = d(8), d(3)                 # 75.4: entre el octavo y el tercer día, ambos inclusive
CORREO_ENVIO, CORREO_LLEGA = d(5), d(2)         # 75.7: enviar no más tarde del quinto; no valen los que lleguen después del segundo
ESCR = VOTO + timedelta(days=5)                 # 103.1: el quinto día siguiente
FIN = VOTO + timedelta(days=8)                  # 107.2: concluir no más tarde del octavo día
assert (URNA_INI, URNA_FIN, CORREO_ENVIO, CORREO_LLEGA, ESCR, FIN) == (
    date(2026, 11, 21), date(2026, 11, 26), date(2026, 11, 24), date(2026, 11, 27), date(2026, 12, 4), date(2026, 12, 7))
assert URNA_FIN.weekday() == 3 and ESCR.weekday() == 4 and FIN.weekday() == 0

# ---------- Electores del 29N (INE) ----------
C = pd.read_csv(RAIZ / 'data/censo/censo_municipios_2023_2026.csv', dtype={'mun_code': str})
CER26, CERA26, CERA23 = (int(C[k].sum()) for k in ('cer_2026', 'cera_2026', 'cera_2023'))
assert (CER26, CERA26) == (35958711, 2769645)
PCERA = CERA26 / (CER26 + CERA26) * 100
assert round(PCERA, 1) == 7.2

# ---------- Participación del CERA, 2000-2023 ----------
DIR = RAIZ / 'actualidad/src/resumenes/datos'
S = pd.read_csv(DIR / 'voto_exterior_cera_1986_2023.csv')
S['anio'] = S.eleccion.str[9:13].astype(int)
S['mes'] = S.eleccion.str[14:16]
S = S[S.anio >= 2000].reset_index(drop=True)   # el preámbulo de la LO 12/2022 compara con las «elecciones generales recientes» desde 2000
ETQ = {(2019, '04'): 'Abril 2019', (2019, '11'): 'Noviembre 2019'}
S['etq'] = [ETQ.get((r.anio, r.mes), str(r.anio)) for r in S.itertuples()]
PART = {r.etq: r.participacion for r in S.itertuples()}
assert [round(PART[k], 2) for k in ('2000', '2008', '2011', '2015', 'Noviembre 2019', '2023')] == [22.96, 31.74, 4.95, 4.73, 6.85, 8.95]
R23 = S[S.anio == 2023].iloc[0]
assert (R23.censo_cera, R23.votantes_cera) == (2328260, 208431)
ANTES = S[S.anio < 2011]
MEDIA_ANTES = ANTES.participacion.mean()
ROGADO = S[(S.anio >= 2011) & (S.anio < 2023)]
assert len(ANTES) == 3 and len(ROGADO) == 5 and ROGADO.participacion.max() < 7

COL = {True: 'var(--muted)', False: 'var(--acc)'}
g_part = figura('Con el voto rogado, la participación de fuera se hundió y aún no se ha recuperado',
                'Votantes residentes en el extranjero sobre su censo en cada elección al Congreso, en porcentaje. En gris, las elecciones con voto rogado (2011-2019)',
                barras([(r.etq, r.participacion, COL[2011 <= r.anio < 2023], f'{p(r.participacion)} %') for r in S.itertuples()], 35,
                       'Participación de los electores residentes en el extranjero', W=400, ml=120, alto=22),
                'Fuente: Ministerio del Interior, resultados por mesa (voto CERA, municipio 999). Cálculo propio: votos a candidaturas, en blanco y nulos sobre el censo.',
                [('Sin voto rogado', 'var(--acc)'), ('Con voto rogado', 'var(--muted)')],
                (['Elección', 'Censo en el extranjero', 'Votantes', 'Participación (%)'],
                 [[r.etq, n(r.censo_cera), n(r.votantes_cera), p(r.participacion)] for r in S.itertuples()]))

# ---------- Provincias de 2023 donde el voto de fuera superaba la distancia del último escaño ----------
M = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'provincia'])
NOMP = dict(zip(M.mun_code.str[:2], M.provincia.str.split('/').str[0].replace({'Araba': 'Álava'})))
NOMP.update({'07': 'Baleares', '35': 'Las Palmas', '38': 'Santa Cruz de Tenerife'})
SIG = {'JXCAT - JUNTS': 'Junts', 'EAJ-PNV': 'PNV', 'SUMAR': 'Sumar', 'VOX': 'Vox', 'PSC': 'PSC', 'PP': 'PP', 'PSOE': 'PSOE'}
P = pd.read_csv(DIR / 'voto_exterior_cera_provincias_2023.csv', dtype={'prov': str}).fillna({'cambio_por_cera': ''})
assert len(P) == 52 and int(P.votantes_cera.sum()) == R23.votantes_cera
P['nombre'] = P.prov.map(NOMP)
J = P[P.votos_nuevos < P.validos_cera].sort_values('votos_nuevos').reset_index(drop=True)
assert len(J) == 9 and set(J.prov) == {'17', '20', '28', '29', '33', '37', '38', '39', '43'}
CAMBIO = P[P.cambio_por_cera != '']
assert list(CAMBIO.prov) == ['28'] and CAMBIO.iloc[0].cambio_por_cera == 'PP 15→16; PSOE 11→10'
J['u'] = J.ultimo.map(SIG)
J['a'] = J.aspirante.map(SIG)
assert J.u.notna().all() and J.a.notna().all()
GIR = J.iloc[0]
assert GIR.prov == '17' and GIR.votos_nuevos == 285
tabla9 = ('<div class="tbl"><table><thead><tr><th>Provincia</th><th>Último escaño</th><th>Siguiente</th>'
          '<th>Le faltaban</th><th>Válidos de fuera</th></tr></thead><tbody>'
          + ''.join(f'<tr><td>{esc(r.nombre)}</td><td>{r.u}</td><td>{r.a}</td><td>{n(r.votos_nuevos)}</td><td>{n(r.validos_cera)}</td></tr>'
                    for r in J.itertuples())
          + '</tbody></table></div>'
          '<p class="src">Fuente: Ministerio del Interior, resultados por mesa de las generales de 2023. Le faltaban: los votos que habría necesitado '
          'el siguiente partido, con el resto igual, para superar (no empatar) al último escaño en el reparto D\'Hondt con el voto exterior incluido. Cálculo propio.</p>')

# ---------- Ley de nietos ----------
NIETOS, EXILIO, TRAS_COMPROBAR = 163355, 901, 113326

CALEND = [
    (f'Del sábado 21 al jueves 26 de noviembre', 'Voto en urna en los consulados',
     f'«Entre el octavo y el tercer día, ambos inclusive, anteriores al día de la elección», en horario de mañana y tarde (<a href="{L75}">art. 75.4</a>). La ley dice que el plazo es «improrrogable».'),
    ('Hasta el martes 24 de noviembre', 'Último día para mandar el voto por correo al consulado',
     f'«No más tarde del quinto día anterior al día de la elección» (<a href="{L75}">art. 75.7</a>).'),
    ('Hasta el viernes 27 de noviembre', 'Último día en que puede llegar al consulado',
     f'No valen los sobres «que lleguen después del segundo día anterior al de la elección» (<a href="{L75}">art. 75.7</a>).'),
    ('Domingo 29 de noviembre', 'Votación en España y recuento provisional',
     'El voto de fuera no está en las urnas de los colegios ni en los resultados de esa noche.'),
    ('Viernes 4 de diciembre, 8.00', 'Escrutinio del voto de fuera',
     f'Cada junta electoral provincial se constituye en mesa, mete en la urna los sobres recibidos y suma el resultado al escrutinio general (<a href="{L75}">art. 75.10 y 11</a>, <a href="{L103}">art. 103.1</a>).'),
    ('Hasta el lunes 7 de diciembre', 'Fin del escrutinio general',
     f'Debe concluir «no más tarde del octavo día posterior al de las elecciones» (<a href="{L107}">art. 107.2</a>).'),
]
tcal = ('<div class="tbl"><table><thead><tr><th>Cuándo</th><th>Qué pasa</th></tr></thead><tbody>'
        + ''.join(f'<tr><td><strong>{h}</strong></td><td><strong>{q}</strong>. {t}</td></tr>' for h, q, t in CALEND)
        + '</tbody></table></div>')

cuerpo = f'''
<p data-tipo="dato">Para las elecciones generales del 29 de noviembre hay {n(CERA26)} electores que viven en el extranjero, el {p(PCERA)} % del censo, según el INE. Su voto sigue un camino propio, escrito en el <a href="{L75}">artículo 75 de la Ley Orgánica del Régimen Electoral General (LOREG)</a>: vota antes que nadie, en los consulados o por correo, y se cuenta después que nadie, el viernes 4 de diciembre. Esta es la ley, artículo por artículo, y lo que queda abierto por la ley de nietos.</p>
<h2>Quién vota desde fuera</h2>
<p data-tipo="contexto">La ley divide el censo en dos. «El censo electoral está compuesto por el censo de los electores residentes en España y por el censo de los electores residentes-ausentes que viven en el extranjero. Ningún elector podrá figurar inscrito simultáneamente en ambos censos», dice el <a href="{L31}">artículo 31.2</a>. El segundo es el CERA, el censo electoral de residentes ausentes. La inscripción la hacen los consulados: «tramitarán de oficio la inscripción de los españoles residentes en su demarcación» (<a href="{L32}">artículo 32.3</a>). Cada elector de fuera vota por la provincia en la que está inscrito.</p>
<p data-tipo="contexto">Quien está inscrito como residente en España no es del CERA, aunque el 29N esté fuera: vota como residente en España. El voto por correo de los residentes se explica en {L("voto-correo-29n", "esta pieza")}.</p>
<h2>Cómo se vota desde 2022: sin pedirlo</h2>
<p data-tipo="contexto">Hasta 2022, quien vivía fuera tenía que pedir el voto en cada elección. Era el voto rogado, que «introdujo» la reforma de 2011, según el preámbulo de la <a href="{LO12}">Ley Orgánica 12/2022</a>, que lo suprimió. El mismo preámbulo da la razón: en las generales de 2011, 2015, 2016 y 2019, «menos del 10 por ciento de los electores solicitaron o rogaron el voto como consecuencia de la complejidad del procedimiento».</p>
<p data-tipo="contexto">Ahora es al revés. Las delegaciones de la Oficina del Censo Electoral «remitirán de oficio» a cada elector del CERA la documentación (<a href="{L75}">art. 75.1</a>): los sobres, dos certificados de inscripción, los sobres con la dirección de la junta electoral y del consulado, una hoja con las instrucciones y la lista de lugares donde votar en urna. Las papeletas llegan en un segundo envío y también se pueden descargar, pero solo el juego completo, «con el fin de garantizar el secreto del voto» (<a href="{L75}">art. 75.2 y 3</a>).</p>
<p data-tipo="contexto">Hay dos maneras de votar. En urna, en la embajada, el consulado o el lugar habilitado, enseñando el pasaporte, el DNI o un certificado de nacionalidad y entregando uno de los certificados (<a href="{L75}">art. 75.4 y 5</a>). O por correo al consulado, con el sobre de la junta, uno de los certificados firmado y una fotocopia del pasaporte o del DNI (<a href="{L75}">art. 75.7</a>). En los dos casos, «será indispensable para la validez de estos votos» el sello del consulado en el sobre (<a href="{L75}">art. 75.9</a>). El envío es gratuito para el elector (<a href="{L75}">art. 75.12</a>).</p>
<h2>Los plazos del 29N</h2>
{tcal}
<p data-tipo="contexto">Los votos que lleguen tarde al consulado no se tiran: según la <a href="{JEC}">Instrucción 1/2023 de la Junta Electoral Central</a>, se mandan a la junta «haciendo constar su recepción fuera del plazo legalmente establecido», y la junta no los mete en la urna. Si alguien vota dos veces, la junta solo cuenta «el voto que se hubiese emitido con antelación».</p>
<h2>Por qué se cuenta el viernes</h2>
<p data-tipo="contexto">Las urnas de los consulados se cierran el jueves 26, se levanta un acta y los sobres viajan por valija diplomática al Ministerio de Asuntos Exteriores, que los reparte entre las juntas electorales (<a href="{L75}">art. 75.8</a>). Para que lleguen, la misma reforma de 2022 retrasó el escrutinio general: ahora «se realiza el quinto día siguiente al de la votación» (<a href="{L103}">art. 103.1</a>). Ese día, «a las ocho horas de la mañana», cada junta provincial «se constituye en Mesa Electoral», mete en la urna «los sobres de votación de los residentes ausentes recibidos hasta ese día» y, «una vez escrutados los votos», «incorpora los resultados al escrutinio general» (<a href="{L75}">art. 75.10 y 11</a>).</p>
<p data-tipo="dato">Por eso el reparto de escaños de la noche del domingo es provisional. En 2023, el voto de fuera cambió el último diputado de Madrid: el PP pasó de 15 a 16 y el PSOE, de 11 a 10. Lo contamos en {L("escrutinio-elecciones-generales-29n", "la pieza del escrutinio")}. Al final, la Junta Electoral Central publica el voto de fuera por consulado y por provincia (<a href="{L75}">art. 75.14</a>).</p>
<h2>Cuánta gente vota desde fuera</h2>
<p data-tipo="dato">Poca, y menos que antes. En las generales de 2000, 2004 y 2008 votó entre el {p(PART["2000"])} % y el {p(PART["2008"])} % de los electores de fuera. Con el voto rogado, de 2011 a 2019, nunca pasó del {p(ROGADO.participacion.max())} %. En 2023, las primeras generales sin voto rogado, votó el {p(PART["2023"])} %: {n(R23.votantes_cera)} de {n(R23.censo_cera)}. Son datos de Interior por mesa; el preámbulo de la ley de 2022 da cifras muy parecidas, del 22,99 % en 2000 y el 31,88 % en 2008.</p>
{g_part}
<h2>Dónde puede decidir un escaño</h2>
<p data-tipo="dato">Con los votos de 2023, el voto de fuera solo cambió un escaño, el de Madrid. Pero en otras ocho provincias el último escaño se decidió por menos votos de los que llegaron de fuera. En Girona, al PP le faltaban {n(GIR.votos_nuevos)} votos para quitarle a Junts su último diputado; de fuera llegaron {n(GIR.validos_cera)} votos válidos. Esos votos se reparten entre todos los partidos, así que no basta con que sean más que la distancia: tienen que inclinarse mucho hacia uno.</p>
{tabla9}
<p data-tipo="contexto">Las mismas nueve provincias aparecen en el estudio de María Isabel Álvarez Vélez y María Corres-Illera en la <a href="{RDP}">Revista de Derecho Político</a>: «En las elecciones celebradas en julio de 2023 el voto CERA pudo alterar el reparto de un último escaño en nueve provincias, donde los repartos fueron muy ajustados».</p>
<h2>Los nietos: lo que ha decidido el Supremo</h2>
<p data-tipo="contexto">La ley de Memoria Democrática abrió en 2022 la nacionalidad a hijos y nietos de exiliados y emigrantes, y muchos de ellos entraron en el CERA. En septiembre, la Sala Tercera del Supremo suspendió de forma cautelar el voto de los nacionalizados por esa ley que no acrediten que descienden de exiliados. El Gobierno entregó una lista de {n(NIETOS)} personas, de las que {n(EXILIO)} tenían el exilio acreditado, según <a href="{EP}">Europa Press</a>. Una suspensión cautelar no decide el fondo: el pleito sigue abierto. Lo contamos en {L("ley-nietos-voto-exterior-29n", "la pieza del voto de fuera")} y en {L("ley-nietos-donde-estan-29n", "la de dónde están los nietos")}.</p>
<p data-tipo="dato">El 20 de noviembre, en una providencia recogida por Europa Press, el Supremo ordenó a la Junta Electoral Central y a la Oficina del Censo que ninguna de esas {n(NIETOS)} personas pueda figurar como elector, «sea en el de electores residentes-ausentes que viven en el extranjero, sea en el de electores residentes en España», según <a href="{INDEP}">El Independiente</a>. Quedan fuera de la prohibición «las 901 personas que presentaron certificación consular» y «cualesquiera otras que, con anterioridad al día de la votación, aporten dicha certificación consular». Es decir, quien viva en España tampoco puede votar en su colegio si está en la lista. El mismo medio cuenta que la Abogacía del Estado rebajó la cifra a {n(TRAS_COMPROBAR)} «como resultado de las comprobaciones realizadas».</p>
<p data-tipo="contexto">El 24 de noviembre, el Supremo no entró en la denuncia de una asociación contra las «mesas específicas y urnas de cartón» para el voto de quienes no están en el CERA, y dijo que le corresponde a la Junta Electoral Central, según <a href="{TOBJ}">The Objective</a>.</p>
<h2>Lo que queda abierto</h2>
<p data-tipo="hipotesis">El fondo del pleito de los nietos sigue sin resolver: lo que rige el 29N es una suspensión cautelar. Lo de las urnas de cartón queda en manos de la Junta Electoral Central. Y cualquier partido que pierda un escaño por pocos votos el viernes 4 podrá reclamar, como hizo el PSOE en Madrid en 2023, primero ante la junta provincial y luego ante la Junta Electoral Central y los tribunales. Lo que sí fija la ley son los plazos: el voto que llegue al consulado después del viernes 27 no vale.</p>
'''

preguntas = [
    ('¿Hasta cuándo se puede votar en los consulados para el 29N?',
     f'En urna, hasta el jueves 26 de noviembre: «entre el octavo y el tercer día, ambos inclusive, anteriores al día de la elección» (<a href="{L75}">art. 75.4 de la LOREG</a>). Por correo, el voto debía salir hacia el consulado como tarde el martes 24 y no vale si llega después del viernes 27 (<a href="{L75}">art. 75.7</a>).'),
    ('¿Hay que pedir el voto para votar desde el extranjero?',
     f'No. Desde la <a href="{LO12}">Ley Orgánica 12/2022</a>, la Oficina del Censo Electoral envía la documentación «de oficio» a todos los inscritos en el CERA (<a href="{L75}">art. 75.1</a>).'),
    ('¿Cuándo se cuenta el voto de los españoles en el extranjero?',
     f'En el escrutinio general, el viernes 4 de diciembre a las 8.00, en cada junta electoral provincial (<a href="{L75}">art. 75.10</a> y <a href="{L103}">art. 103.1</a>). No entra en los resultados de la noche del domingo.'),
    ('¿Puede cambiar un escaño el voto de fuera?',
     f'Sí. En 2023 cambió el último diputado de Madrid, del PSOE al PP. En otras ocho provincias el último escaño se decidió por menos votos de los que llegaron de fuera, aunque no cambió.'),
    ('¿Pueden votar el 29N los nacionalizados por la ley de nietos?',
     f'Los {n(NIETOS)} de la lista entregada al Supremo, no, salvo los {n(EXILIO)} con certificación consular de exilio y quienes la aporten antes de votar, según la providencia del 20 de noviembre que recoge <a href="{INDEP}">El Independiente</a>. La prohibición vale para el CERA y para el censo de residentes en España.'),
]
enlaces = (f'{L("escrutinio-elecciones-generales-29n", "Escrutinio del 29N")} · {L("ley-nietos-voto-exterior-29n", "El voto de fuera")} · '
           f'{L("ley-nietos-donde-estan-29n", "Dónde están los nietos")} · {L("voto-correo-29n", "Voto por correo")}')
foot = ('Datos: Ley Orgánica del Régimen Electoral General, artículos 31, 32, 75, 103 y 107 (texto consolidado del BOE); Ley Orgánica 12/2022; '
        'Junta Electoral Central, Instrucción 1/2023; INE, censo electoral del 29N; Ministerio del Interior, resultados por mesa de las generales de 2000 a 2023. '
        'Cálculo: voto_exterior_loreg.py y voto_exterior_preparar.py, en actualidad/src/resumenes.')

DATOS = {'CER26': CER26, 'CERA26': CERA26, 'PCERA': round(PCERA, 3),
         'PART': [{'eleccion': r.etq, 'censo': int(r.censo_cera), 'votantes': int(r.votantes_cera), 'pct': r.participacion} for r in S.itertuples()],
         'MAX_ROGADO': float(ROGADO.participacion.max()),
         'P9': [{'prov': r.nombre, 'ultimo': r.u, 'siguiente': r.a, 'faltaban': int(r.votos_nuevos), 'validos_cera': int(r.validos_cera)} for r in J.itertuples()],
         'MAD': {k: [int(x) for x in v.split('→')] for k, v in (t.split(' ') for t in CAMBIO.iloc[0].cambio_por_cera.split('; '))},
         'N9': len(J), 'NIETOS': NIETOS, 'EXILIO': EXILIO, 'TRAS_COMPROBAR': TRAS_COMPROBAR,
         'FECHAS': {k: v.isoformat() for k, v in dict(urna_ini=URNA_INI, urna_fin=URNA_FIN, correo_envio=CORREO_ENVIO, correo_llega=CORREO_LLEGA,
                                                       escrutinio=ESCR, fin=FIN).items()}}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = 'Votar desde el extranjero el 29N, ley en mano: la urna de los consulados cierra el jueves 26 y esos votos no se cuentan hasta el viernes 4 de diciembre'
DEK = (f'Son {n(CERA26)} electores. Desde 2022 no tienen que pedir el voto, pero en 2023 solo votó el {p(PART["2023"])} %. '
       'El Supremo deja fuera a los nacionalizados por la ley de nietos que no acrediten el exilio, también si viven en España.')
pieza(SLUG, 'Voto exterior y LOREG', TITULO, DEK, '26 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(TITULO); print(DEK); print(J[['nombre', 'u', 'a', 'votos_nuevos', 'validos_cera']].to_string())
