"""«Las provincias que deciden el 29N» (pieza de resumen de fin de semana, 24-10-2026).

Los márgenes del último escaño salen de la pieza «Seis escaños que se decidieron por menos de mil votantes»
(actualidad/src/escanos-en-el-filo-29n.html, objeto F: votos de 2023 con voto exterior y escaños de 2026); el precio del escaño
y los votos sin escaño, de actualidad/src/sistema/cifras.json, a través de sus piezas. Encuestas y modelo, a 23 de octubre.
Uso, desde la raíz: python3 actualidad/src/resumenes/filo.py
"""
import collections
import json
import re

from comun import BASE, COLOR, SRC, barras, esc, figura, mapa_provincias, n, pieza

A = BASE + 'actualidad/'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'

F = json.loads(re.search(r'const F=(\{.*?\});', (SRC / 'escanos-en-el-filo-29n.html').read_text(encoding='utf-8'), re.S).group(1))
orden = sorted(F, key=lambda p: F[p]['c'])
filo = [p for p in orden if F[p]['c'] < 5000]
assert len(filo) == 32 and sum(F[p]['c'] for p in filo) == 75392
assert sum(F[p]['c'] < 1000 for p in F) == 6 and sum(F[p]['c'] < 2000 for p in F) == 13 and sum(F[p]['c'] < 10000 for p in F) == 44
defiende = collections.Counter(F[p]['u'] for p in filo)
aspira = collections.Counter(F[p]['a'] for p in filo)
assert defiende['PP'] == 13 and defiende['PSOE'] == 6 and aspira['PSOE'] == 17 and aspira['PP'] == 9, (defiende, aspira)
print('defiende', defiende, 'aspira', aspira)

ORD = lambda k: {1: 'primer', 2: 'segundo', 3: 'tercer', 4: 'cuarto', 5: 'quinto', 6: 'sexto'}.get(k, f'{k}.º')

top = orden[:20]
fig_top = figura('Los 20 escaños más ajustados',
                 'Votantes que tendrían que pasar del partido que se llevó el último escaño de la provincia al que se quedó a las puertas, con los votos de 2023 y los escaños de 2026. La barra va en el color del partido que habría ganado el escaño',
                 barras([(F[p]['n'], F[p]['c'], COLOR[F[p]['a']], f'{n(F[p]["c"])} · {F[p]["u"]} → {F[p]["a"]}') for p in top], 5600,
                        'Votantes que harían falta para mover el último escaño en las 20 provincias más ajustadas', ml=170),
                 'Fuente: Ministerio del Interior, resultados definitivos de las generales de julio de 2023 por provincia, con voto exterior (CERA); escaños de 2026 (Real Decreto 806/2026). Regla D\'Hondt con barrera del 3 %. Cálculo propio.',
                 tabla=(['Provincia', 'Escaños 2026', 'Último escaño', 'A las puertas', 'Votantes que cambian', 'Votos nuevos que faltan'],
                        [(F[p]['n'], F[p]['e'], f'{F[p]["u"]} ({ORD(F[p]["un"])})', f'{F[p]["a"]} ({ORD(F[p]["an"])})', n(F[p]['c']), n(F[p]['f'])) for p in orden]))

PART = ['PP', 'PSOE', 'Vox', 'Sumar', 'Junts', 'PNV', 'BNG']


def duelo_svg():
    W, ml, alto, c = 640, 70, 30, 320
    H = alto * len(PART) + 30
    u = 14
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Escaños ajustados que defiende y a los que aspira cada partido">',
           f'<text x="{c - 8}" y="14" text-anchor="end" class="lab">Defiende</text><text x="{c + 8}" y="14" class="lab">Aspira a ganar</text>']
    for i, k in enumerate(PART):
        y = 24 + i * alto
        d, a = defiende[k], aspira[k]
        out.append(f'<text x="{ml - 8}" y="{y + 18}" text-anchor="end" class="lab">{k}</text>')
        if d:
            out.append(f'<rect x="{c - d * u:.0f}" y="{y + 5}" width="{d * u}" height="18" fill="{COLOR[k]}" rx="2"><title>{k} defiende {d}</title></rect>'
                       f'<text x="{c - d * u - 6:.0f}" y="{y + 18}" text-anchor="end">{d}</text>')
        if a:
            out.append(f'<rect x="{c}" y="{y + 5}" width="{a * u}" height="18" fill="{COLOR[k]}" fill-opacity=".45" rx="2"><title>{k} aspira a {a}</title></rect>'
                       f'<text x="{c + a * u + 6}" y="{y + 18}">{a}</text>')
    out.append(f'<line x1="{c}" x2="{c}" y1="20" y2="{H}" stroke="var(--fg)"/></svg>')
    return ''.join(out)


fig_duelo = figura('Quién defiende y quién ataca',
                   'De los 32 últimos escaños que se movían con menos de 5.000 votantes en 2023: a la izquierda, los que ganó cada partido; a la derecha, aquellos a los que se quedó a las puertas',
                   duelo_svg(),
                   'Fuente: Ministerio del Interior, generales de 2023 con voto exterior; escaños de 2026. Cálculo propio.',
                   tabla=(['Partido', 'Defiende', 'Aspira a ganar'], [(k, defiende[k], aspira[k]) for k in PART]))

mapa = mapa_provincias({p: (COLOR[F[p]['a']] if F[p]['c'] < 5000 else 'var(--otros)') for p in F},
                       {p: f'{F[p]["n"]}: el {ORD(F[p]["un"])} escaño de {F[p]["u"]} estaba a {n(F[p]["c"])} votantes del {ORD(F[p]["an"])} de {F[p]["a"]}' for p in F},
                       'Mapa de provincias según el partido que se quedó a las puertas del último escaño',
                       opacidad={p: (1 if F[p]['c'] < 2000 else .6) for p in F})
fig_mapa = figura('El mapa del filo',
                  'Partido que habría ganado el último escaño de cada provincia si menos de 5.000 votantes hubieran cambiado su voto en 2023; más intenso, menos de 2.000. En gris, donde hacían falta más',
                  mapa,
                  'Fuente: Ministerio del Interior, generales de 2023 con voto exterior; escaños de 2026 (Real Decreto 806/2026). Cálculo propio. Canarias, en el recuadro.',
                  leyenda=[('PSOE', COLOR['PSOE']), ('PP', COLOR['PP']), ('Sumar', COLOR['Sumar']), ('Vox', COLOR['Vox']), ('Más de 5.000', COLOR['Otros'])])

c = lambda p: n(F[p]['c'])
cuerpo = f'''<div class="resumen"><b>En corto</b><ul>
<li>Con los votos de 2023 y los escaños de 2026, 32 últimos escaños habrían cambiado de partido con menos de 5.000 votantes cambiando de papeleta; seis, con menos de mil.</li>
<li>El más ajustado, Cantabria: bastaban 101 votantes de Vox que votaran al PP. Después, Girona (190) y Tarragona (312).</li>
<li>El PP defiende 13 de esos escaños y el PSOE aspira a 17. Vox defiende seis.</li>
<li>Casi todos están en provincias que eligen menos de ocho diputados, donde un escaño cuesta hasta cuatro veces menos votos que en Madrid.</li>
</ul></div>
<p data-tipo="contexto">El 28 de julio de 2023, cinco días después de las generales, la Junta Electoral Provincial de Cantabria abrió las cajas con el voto de los cántabros que viven en el extranjero. Eran algo más de 3.000 papeletas, y entre Vox y el PP había 428 votos de diferencia en la pugna por el quinto diputado, según <a href="https://theobjective.com/espana/politica/2023-07-28/vox-diputado-cantabria-voto-cera/">Europa Press</a>. Esa tarde se supo que el escaño seguía siendo de Vox.</p>
<p data-tipo="dato">Con el escrutinio cerrado, la distancia era aún más corta de lo que parecía. Al PP le faltaban 404 votos, pero no hacía falta que aparecieran 404 votantes nuevos: bastaba con que {c("39")} personas que votaron a Vox hubieran cogido la papeleta del PP. En una comunidad de unos 348.000 votos válidos.</p>
<p data-tipo="contexto">Ese es el tamaño de las cosas que deciden unas generales en España. El 29 de noviembre se eligen 350 diputados en 52 elecciones a la vez, una por provincia y en Ceuta y Melilla, y la mayoría de los escaños de cada una están decididos de antemano por el tamaño de cada partido. Lo que se mueve es el último. Este texto reúne lo que hemos publicado sobre esos últimos escaños: dónde están, quién los defiende y por qué ahí pesa tanto un puñado de votos. No es una previsión: es la foto de lo cerca que estuvo cada asiento la última vez.</p>
<h2>Treinta y dos escaños en el filo</h2>
<p data-tipo="dato">Con los votos oficiales de julio de 2023, voto exterior incluido, y los escaños que reparte cada provincia en 2026, el último escaño de seis provincias habría cambiado de partido si menos de mil votantes hubieran cambiado su voto: Cantabria ({c("39")}), Girona ({c("17")}), Tarragona ({c("43")}), Ceuta ({c("51")}), Salamanca ({c("37")}) y Albacete ({c("02")}). Con menos de 2.000 son 13. Con menos de 5.000, 32, y entre todos bastarían 75.392 personas, menos que los votos válidos de la provincia de Palencia. Lo contamos con detalle en {L("escanos-en-el-filo-29n", "los seis escaños que se decidieron por menos de mil votantes")}.</p>
{fig_top}
<p data-tipo="dato">En Girona, el último de los seis escaños fue el segundo de Junts, y quien se quedó a las puertas fue el PP, que no sacó ninguno: le faltaron 285 votos, o 190 votantes de Junts que se hubieran pasado al PP. En Tarragona, el escaño en juego era el único de Junts y el aspirante, el tercero del PSOE. En Ceuta, que elige un solo diputado, el PP ganó al PSOE por 1.587 votos. En Albacete pasó al revés: el segundo diputado del PSOE se salvó frente al primero de Vox por 1.412 votos.</p>
<p data-tipo="contexto">La cifra de votantes que cambian de papeleta es la más baja posible, la del mejor caso para el aspirante. Otra pieza anterior, {L("ultimo-escano-29n", "la del último escaño")}, mide los votos nuevos que le faltaron a cada aspirante, y con esa cuenta salen 17 provincias por debajo de 5.000. Las dos miden lo mismo desde lados distintos: lo poco que separó un escaño de otro.</p>
<h2>Quién defiende y quién ataca</h2>
<p data-tipo="dato">De esos 32 escaños, el PP es el que más tiene que perder: defiende 13. El PSOE defiende 6 y aspira a 17. Vox defiende seis y solo aspiraba a dos, el de Albacete y el de Ávila. Sumar defendía dos, en Granada y Córdoba, y aspiraba a cuatro. Junts, el PNV y el BNG solo aparecen defendiendo.</p>
{fig_duelo}
<p data-tipo="patron">Los duelos se repiten. Donde el escaño ajustado es del PP, el aspirante suele ser el PSOE: Ceuta, Salamanca, Málaga, Cuenca, Teruel, Huesca, Las Palmas, Melilla, Palencia, Ourense, Lugo y Asturias. Donde es de Vox, el aspirante suele ser el PP: Cantabria, Guadalajara, Valladolid o Huelva. Por eso la pelea entre PP y Vox no solo decide quién lidera la derecha: también mueve escaños sueltos.</p>
{fig_mapa}
<p data-tipo="contexto">Los partidos ya hacen esa cuenta. El Independiente repasó el 14 de octubre las provincias que mira Santiago Abascal y recordaba la de Albacete: «A las puertas tuvo Vox el quitar un diputado al PSOE por menos de 1.300 papeletas», según <a href="https://www.elindependiente.com/espana/2026/10/14/abascal-15-provincias-clave-crecimiento-vox-desgaste-psoe-division-izquierda/">El Independiente</a>. Con el escrutinio definitivo, nuestro cálculo da 1.412 votos.</p>
<h2>Por qué el filo está en las provincias pequeñas</h2>
<p data-tipo="dato">El filo no está en Madrid ni en Barcelona. A Madrid le harían falta 35.114 votantes para que su último escaño cambiara de dueño; a Barcelona, 22.957. Casi todas las provincias del filo eligen menos de ocho diputados. De las 52 circunscripciones, 29 eligen cinco o menos: juntas reparten 108 escaños, el 30,9 % del Congreso, aunque solo viven en ellas el 22,1 % de los electores residentes.</p>
<p data-tipo="dato">En ellas, cada voto pesa más y el primero se lleva más. En 2023, un diputado costó 25.304 votos en Teruel y 97.532 en Madrid, casi cuatro veces más, como contamos en {L("precio-del-escano-29n", "el precio del escaño")}. En esas 29 provincias pequeñas, el PP sacó el 37,4 % de los votos y 53 de los 108 escaños; Sumar, con el 8,2 %, ninguno. Y 1,9 millones de votos, el 7,8 % de los válidos, fueron a listas que no sacaron ningún diputado en su provincia: el 35,2 % en Teruel y el 1,3 % en Madrid, según {L("votos-sin-escano-29n", "los votos que no eligieron a nadie")}.</p>
<blockquote class="cita"><p>«La falta de proporcionalidad del sistema español no se debe tanto a la regla d’Hondt (o al umbral electoral) sino al elevado número de pequeños distritos.»</p><footer>Annick Laruelle, Ikerbasque y Universidad del País Vasco, en <a href="https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso">Campusa</a> (2019).</footer></blockquote>
<p data-tipo="contexto">Alberto Penadés y Salvador Santiuste lo resumieron en la <a href="https://recyt.fecyt.es/index.php/recp/article/download/37589/21106">Revista Española de Ciencia Política</a>: «La competición electoral en España no tiene lugar en condiciones iguales en todas las circunscripciones, y los votos no cuentan todos lo mismo». Y los partidos lo usan para pedir el voto útil. La portavoz del PSOE, Montse Mínguez, lo dijo de Lleida, que elige cuatro diputados: «Ojalá no fuera así, ojalá no fuera así, pero las matemáticas son lo que son y los números son lo que son», según <a href="https://www.democrata.es/politica/el-psoe-reclama-el-voto-util-en-provincias-pequenas-para-que-apoyos-a-la-izquierda-no-vayan-a-la-basura/">Europa Press</a>.</p>
<h2>Lo que puede mover el filo antes de votar</h2>
<p data-tipo="dato">Hay un cambio que ya está hecho. El <a href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742">Real Decreto 806/2026</a> da a Madrid un diputado más, 38, y deja a Cádiz con 8. Con los votos de 2023, el escaño nuevo de Madrid sería para el PSOE, el undécimo de su lista, y el que pierde Cádiz sería el cuarto del PP: 136 diputados para el PP y 122 para el PSOE, en lugar de 137 y 121.</p>
<p data-tipo="dato">Y está el voto que llega de fuera. En 2023, el voto exterior le dio al PP el último escaño de Madrid, que la noche electoral era del PSOE. Para el 29N, el Supremo ha dejado sin voto a 163.020 nacionalizados por la ley de nietos, y el censo de residentes en el extranjero ha crecido un 19 %, como contamos en {L("ley-nietos-voto-exterior-29n", "la pieza sobre el voto exterior")}.</p>
<p data-tipo="contexto">Las divisiones también mueven el filo. En ocho provincias, Sumar ganó o perdió en 2023 un escaño por menos de 5.000 votos, y en seis de ellas el Frente Amplio y Podemos irán ahora por separado, como contamos en {L("coaliciones-quien-va-con-quien-29n", "quién va con quién el 29N")}. Y en el Senado, la lista conjunta de PSOE y Frente Amplio y la negociación entre PP y Vox se juegan sobre todo en 19 provincias.</p>
<h2>Lo que dicen hoy las encuestas</h2>
<p data-tipo="hipotesis">Las encuestas mueven a todos los partidos varios puntos respecto a 2023, y cuando se mueven los votos, el filo cambia de sitio. El modelo de Mapa Electoral, que reparte la media de encuestas por provincia, señalaba el 23 de octubre como las provincias con el primer puesto menos claro a Bizkaia, Ceuta, Sevilla, Lleida, Las Palmas, Girona, Santa Cruz de Tenerife y Guadalajara, donde Vox aparece como segundo. En el conjunto, daba a PP y Vox 195 escaños en el escenario central, entre 174 y 218 en el 80 % de las simulaciones. Es una estimación, no un resultado: está, actualizada, en {f'<a href="{BASE}encuestas/provincias.html">la encuesta por provincias</a>'}.</p>
<p data-tipo="hipotesis">Lo que la foto de 2023 sí dice es dónde mirar. La noche del 29 de noviembre, el recuento dará un reparto provisional, y si se parece en algo al de entonces, el último escaño de Cantabria, de Girona o de Tarragona podría quedar pendiente, otra vez, del voto que llega del extranjero cinco días después.</p>
<p data-tipo="dato">Para el 29N, la cuenta de partida queda así: 32 escaños a menos de 5.000 votantes, 13 de ellos defendidos por el PP y 17 al alcance del PSOE. Ciento un votantes en Cantabria. Menos de los que caben en un vagón de tren.</p>
'''

preguntas = [
    ('¿Qué provincias pueden decidir las elecciones del 29N?',
     'Con los votos de 2023 y los escaños de 2026, el último escaño de Cantabria, Girona, Tarragona, Ceuta, Salamanca y Albacete habría cambiado de partido con menos de mil votantes cambiando su voto. Con menos de 5.000 hay 32 escaños, casi todos en provincias que eligen menos de ocho diputados.'),
    ('¿Cuál fue el escaño más ajustado de las generales de 2023?',
     'El quinto de Cantabria, que ganó Vox: al PP le faltaron 404 votos, o 101 votantes de Vox que hubieran votado al PP.'),
    ('¿Qué partido tiene más escaños en juego?',
     'De los 32 últimos escaños a menos de 5.000 votantes, el PP defiende 13, Vox 6 y el PSOE 6. El PSOE es el que más aspira a ganar: estuvo a las puertas de 17.'),
    ('¿Cuántos votos cuesta un diputado?',
     'Depende de la provincia. En 2023, un escaño costó 25.304 votos válidos en Teruel y 97.532 en Madrid.'),
    ('¿Cuántos diputados elige cada provincia en 2026?',
     'Los mismos que en 2023 salvo dos: Madrid elige 38, uno más, y Cádiz 8, uno menos (Real Decreto 806/2026). Las provincias más pequeñas eligen entre dos y cinco.'),
    ('¿Puede el voto exterior cambiar un escaño?',
     'Sí. En 2023, el voto de los residentes en el extranjero, que se cuenta días después, le dio al PP el último escaño de Madrid, que la noche electoral era del PSOE.'),
]

enlaces = (f'<a href="{BASE}">Explora el mapa por sección</a> · <a href="{BASE}encuestas/provincias.html">Encuesta por provincias</a> · '
           f'{L("asi-queda-el-mapa-29n", "Así queda el mapa electoral antes del 29N")} · {L("coaliciones-quien-va-con-quien-29n", "Quién va con quién el 29N")}')
foot = ('Datos: Ministerio del Interior, resultados definitivos de las generales de julio de 2023 por provincia con voto exterior (vía pollspaindata); '
        'escaños de 2026 según el Real Decreto 806/2026. Reparto D\'Hondt con barrera del 3 %. Modelo de encuestas, a 23 de octubre de 2026. Cálculo propio.')

pieza('provincias-en-el-filo-29n', 'Las provincias que deciden el 29N',
      'Las provincias que deciden el 29N: 32 escaños se movían en 2023 con menos de 5.000 votantes, y el PP defiende 13',
      'De Cantabria, donde bastaban 101 votantes, a Girona y Tarragona: dónde están los últimos escaños más ajustados, quién los defiende, por qué casi todos están en provincias pequeñas y qué puede moverlos antes de votar.',
      '24 de octubre de 2026', cuerpo, preguntas, enlaces, foot)
