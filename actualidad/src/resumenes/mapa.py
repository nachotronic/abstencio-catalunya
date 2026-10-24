"""«Así queda el mapa electoral de España antes del 29N» (pieza de resumen de fin de semana, 24-10-2026).

Cifras: provincias con voto exterior (actualidad/src/sistema/simulador.json, el mismo cálculo que reproduce los 350 escaños
oficiales de 2023); secciones y deciles de renta de las descargas del mapa (generales-2026/descargas/secciones.csv y
generales-2026/data/resumen.json). El resto sale de piezas ya publicadas, enlazadas en el texto.
Uso, desde la raíz: python3 actualidad/src/resumenes/mapa.py
"""
import collections
import unicodedata
import csv
import json

from comun import BASE, COLOR, RAIZ, SRC, barras, esc, figura, mapa_provincias, n, pares, pieza

A = BASE + 'actualidad/'

# --- Provincias, con voto exterior ---
sim = json.load(open(SRC / 'sistema' / 'simulador.json'))
NOM = sim['provincias']
v23 = sim['elecciones']['2023_07']
ESC = sim['escanos']['2023_07']
gana, margen, escanos = {}, {}, collections.Counter()
for p, x in v23.items():
    v = {k: c for k, c in x['v'].items() if k != 'Otros'}
    orden = sorted(v.items(), key=lambda t: -t[1])
    gana[p], margen[p] = orden[0][0], orden[0][1] - orden[1][1]
    validas = {k: c for k, c in v.items() if c >= .03 * x['validos']}
    for _, k in sorted([(c / i, k) for k, c in validas.items() for i in range(1, ESC[p] + 1)], reverse=True)[:ESC[p]]:
        escanos[k] += 1
cuenta = collections.Counter(gana.values())
assert cuenta == {'PP': 40, 'PSOE': 10, 'EH Bildu': 1, 'PNV': 1}, cuenta
assert escanos['PP'] == 137 and escanos['PSOE'] == 121 and escanos['Vox'] == 33 and escanos['Sumar'] == 31, escanos
psoe = sorted((NOM[p] for p in gana if gana[p] == 'PSOE'), key=lambda t: unicodedata.normalize('NFKD', t))
justas = sorted((p for p in gana), key=lambda p: margen[p])[:5]
print('PSOE gana en', psoe)
print('más justas', [(NOM[p], gana[p], margen[p]) for p in justas])

# --- Secciones (sin voto exterior) ---
sec = {'2023_07': collections.Counter(), '2019_11': collections.Counter()}
for fila in csv.DictReader(open(RAIZ / 'generales-2026/descargas/secciones.csv')):
    for e in sec:
        if fila.get(f'{e}_gana'):
            sec[e][fila[f'{e}_gana']] += 1
S23, S19 = sec['2023_07'], sec['2019_11']
assert sum(S23.values()) == 36412 and S23['PP'] == 18407 and S23['PSOE'] == 16073, S23
assert sum(S19.values()) == 36079 and S19['PSOE'] == 19107 and S19['PP'] == 9587, S19

# --- Deciles de renta (mapa de la portada) ---
dec = json.load(open(RAIZ / 'generales-2026/data/resumen.json'))['variables']['renta_uc']['deciles']
d1, d10 = dec[0], dec[-1]
pc = lambda v: n(v * 100, 1)

# --- Gráficos ---
NOMBRE = {'PP': 'PP', 'PSOE': 'PSOE', 'EH Bildu': 'EH Bildu', 'PNV': 'PNV'}
mapa = mapa_provincias({p: COLOR[g] for p, g in gana.items()},
                       {p: f'{NOM[p]}: ganó {g} por {n(margen[p])} votos' for p, g in gana.items()},
                       'Mapa de España por provincias según el partido más votado en las generales de 2023',
                       opacidad={p: (.55 if margen[p] < 5000 else 1) for p in gana})
fig_mapa = figura('El partido más votado en cada provincia en 2023',
                  'Generales de julio de 2023, con voto exterior. En tono claro, donde el primero ganó por menos de 5.000 votos',
                  mapa,
                  'Fuente: Ministerio del Interior, resultados por mesa con voto exterior (CERA), vía pollspaindata. Cálculo propio. Canarias, en el recuadro.',
                  leyenda=[('PP (40)', COLOR['PP']), ('PSOE (10)', COLOR['PSOE']), ('EH Bildu (1)', COLOR['EH Bildu']), ('PNV (1)', COLOR['PNV'])],
                  tabla=(['Provincia', 'Más votado', 'Ventaja sobre el segundo (votos)'],
                         [(NOM[p], gana[p], n(margen[p])) for p in sorted(gana, key=lambda p: NOM[p])]))

FAM = [('PP', 'PP'), ('PSOE', 'PSOE'), ('ERC', 'ERC'), ('VOX', 'Vox'), ('SUMAR', 'Sumar'), ('PNV', 'PNV'), ('BILDU', 'EH Bildu'), ('JUNTS', 'Junts')]
fig_sec = figura('Secciones censales ganadas por cada partido, en 2019 y en 2023',
                 'Número de secciones donde cada partido fue el más votado. Arriba, noviembre de 2019 (tono claro); abajo, julio de 2023. Sumar: en 2019, Unidas Podemos y sus confluencias',
                 pares([(nom, S19[k], S23[k], COLOR[nom]) for k, nom in FAM], 20000,
                       'Secciones ganadas por partido en noviembre de 2019 y julio de 2023', ['2019', '2023']),
                 'Fuente: Ministerio del Interior, resultados por mesa sumados por sección censal (sin voto exterior). Familias de partidos del mapa de la portada.',
                 tabla=(['Partido', 'Noviembre de 2019', 'Julio de 2023'], [(nom, n(S19[k]), n(S23[k])) for k, nom in FAM]))


def renta_svg():
    W, H, ml, mr, mt, mb = 640, 300, 44, 70, 14, 40
    x = lambda i: ml + i / 9 * (W - ml - mr)
    y = lambda v: mt + (1 - (v - .15) / (.30)) * (H - mt - mb)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto al PP y al PSOE por deciles de renta de la sección, generales de 2023">']
    for v in (.20, .30, .40):
        out.append(f'<line x1="{ml}" x2="{W - mr}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/><text x="{ml - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{int(v * 100)} %</text>')
    for i, d in enumerate(dec):
        out.append(f'<text x="{x(i):.1f}" y="{H - 20}" text-anchor="middle">{d["d"]}</text>')
    out.append(f'<text x="{ml}" y="{H - 2}">Más pobres</text><text x="{W - mr}" y="{H - 2}" text-anchor="end">Más ricas</text>')
    for k, nom in (('PP', 'PP'), ('PSOE', 'PSOE')):
        pts = ' '.join(f'{x(i):.1f},{y(d[k]):.1f}' for i, d in enumerate(dec))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{COLOR[nom]}" stroke-width="3"/>')
        for i, d in enumerate(dec):
            out.append(f'<circle cx="{x(i):.1f}" cy="{y(d[k]):.1f}" r="4" fill="{COLOR[nom]}"><title>Decil {d["d"]}: {nom} {pc(d[k])} %</title></circle>')
        out.append(f'<text x="{x(9) + 8:.1f}" y="{y(dec[-1][k]) + 4:.1f}" class="lab">{nom} {pc(dec[-1][k])} %</text>')
    out.append('</svg>')
    return ''.join(out)


fig_renta = figura('El PSOE gana abajo y el PP, arriba',
                   'Voto al PP y al PSOE en 2023 según la renta de la sección censal, en diez grupos del más pobre (1) al más rico (10)',
                   renta_svg(),
                   'Fuente: Ministerio del Interior (resultados por sección, sin voto exterior) e INE, Atlas de Distribución de Renta de los Hogares 2023 (renta por unidad de consumo). Datos del mapa de la portada.',
                   tabla=(['Decil de renta', 'PP', 'PSOE', 'Participación'],
                          [(str(d['d']), pc(d['PP']) + ' %', pc(d['PSOE']) + ' %', pc(d['part']) + ' %') for d in dec]))

# --- Texto ---
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
cuerpo = f'''<div class="resumen"><b>En corto</b><ul>
<li>En las generales de julio de 2023, el PP fue el más votado en 40 de las 52 circunscripciones; el PSOE, en 10; EH Bildu y el PNV, en una cada uno.</li>
<li>Por secciones censales, el PP ganó en 18.407 y el PSOE en 16.073. En noviembre de 2019 había sido al revés: 19.107 para el PSOE y 9.587 para el PP.</li>
<li>En el 10 % de secciones más pobres, el PSOE sacó el {pc(d1["PSOE"])} % y votó el {pc(d1["part"])} %; en el 10 % más rico, el PP sacó el {pc(d10["PP"])} % y votó el {pc(d10["part"])} %.</li>
<li>A 23 de octubre, 15 de las 16 encuestadoras con sondeo reciente dan ganador al PP; el CIS, al PSOE.</li>
</ul></div>
<p data-tipo="contexto">El sábado 10 de octubre, Pedro Sánchez abrió la precampaña en el auditorio Los del Río de Dos Hermanas, ante unas 5.000 personas, según el PSOE, que recogió <a href="https://es.euronews.com/2026/10/10/sanchez-abre-la-campana-electoral-del-29n-en-su-ciudad-talisman-con-la-vivienda-como-eje-p">Euronews</a>. No eligió el sitio al azar. En Dos Hermanas había anunciado en enero de 2017 que volvería a pelear por la secretaría general del PSOE, y allí lo recordó: «Nos dijeron "no se puede" y el resto ya es historia», según <a href="https://www.diariodeleon.es/nacional/261011/2099933/sanchez-talisman-dos-hermanas-maricarmen_amp.html">Diario de León</a>. Ese mismo día, Alberto Núñez Feijóo prometía en IFEMA, en Madrid, un «cambio sereno pero contundente», según <a href="https://www.la7tv.es/articulo/politica/feijoo-sanchez-abren-precampana-29n-promesas-cambio-llamamientos-movilizacion/20261010140623074323.html">La 7</a>.</p>
<p data-tipo="dato">Los dos escenarios son dos mapas. Dos Hermanas, con 107.888 electores, es el mayor de los 190 municipios donde el PSOE ha sido el partido más votado en las 16 generales celebradas desde 1977, como contamos en {L("municipios-fieles", "los municipios que siempre votan igual")}. Madrid capital es casi lo contrario: en 2023, el PP ganó en 1.603 de sus 2.450 secciones censales y el PSOE {L("madrid-barrio-a-barrio-29n", "solo resistió en cuatro distritos del sur")}.</p>
<p data-tipo="contexto">A cinco semanas de las elecciones del 29 de noviembre, este texto recorre el mapa electoral de España tal como lo dejaron las generales de julio de 2023, de la provincia a la calle, y lo cose con lo que Mapa Electoral ha ido publicando estas semanas. No es una previsión. Es el punto de partida, la foto que las urnas tendrán que mover.</p>
<h2>Cuarenta provincias azules</h2>
<p data-tipo="dato">En julio de 2023, el PP fue la lista más votada en 40 de las 52 circunscripciones, con el voto exterior incluido. El PSOE ganó en diez: {", ".join(psoe[:-1])} y {psoe[-1]}. EH Bildu fue el primero en Gipuzkoa y el PNV, en Bizkaia. En Navarra, el PSOE quedó primero porque UPN y el PP se presentaron por separado.</p>
{fig_mapa}
<p data-tipo="dato">Varias de esas victorias fueron por muy poco. En Huelva, el PP le sacó al PSOE {n(margen["21"])} votos; en Ceuta, {n(margen["51"])}; en Cuenca, {n(margen["16"])}, y en Jaén, {n(margen["23"])}. En Cáceres fue al revés: el PSOE ganó por {n(margen["10"])}. Ser el primero, además, no siempre da más diputados: en Huelva, Jaén y Cáceres, el PP y el PSOE se repartieron los escaños a partes iguales.</p>
<p data-tipo="dato">En escaños, el resultado fue de 137 diputados para el PP, 121 para el PSOE, 33 para Vox y 31 para Sumar. El PP sacó el 33,1 % de los votos y el 39,1 % de los escaños; el PSOE, el 31,7 % de los votos y el 34,6 % de los escaños. La diferencia la explica el tamaño de las provincias, que contamos en {L("precio-del-escano-29n", "el precio del escaño, provincia a provincia")}.</p>
<p data-tipo="contexto">El mapa de 2026 tendrá además una pieza cambiada antes de votar. El <a href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742">Real Decreto 806/2026</a> da a Madrid un diputado más, 38, y deja a Cádiz con 8. Con los votos de 2023, ese escaño nuevo habría sido del PSOE y el que pierde Cádiz, del PP.</p>
<h2>Calle a calle, el mapa se parte</h2>
<p data-tipo="dato">Si se baja de la provincia a las secciones censales, los trozos de barrio de unos cientos o pocos miles de electores en que se organiza el voto, el mapa se vuelve mucho más fino. De las 36.412 secciones con resultados en 2023, el PP fue el más votado en {n(S23["PP"])} y el PSOE en {n(S23["PSOE"])}. Después vienen EH Bildu ({n(S23["BILDU"])}), Junts ({n(S23["JUNTS"])}), el PNV ({n(S23["PNV"])}), ERC ({n(S23["ERC"])}), Sumar ({n(S23["SUMAR"])}), Vox ({n(S23["VOX"])}), Coalición Canaria ({n(S23["CC"])}) y el BNG, con una.</p>
<p data-tipo="dato">Cuatro años antes, el mapa era otro. En noviembre de 2019, el PSOE fue el primero en {n(S19["PSOE"])} secciones y el PP en {n(S19["PP"])}. ERC ganaba en {n(S19["ERC"])}, Vox en {n(S19["VOX"])} y Unidas Podemos en {n(S19["SUMAR"])}. En 2023, el PP casi duplicó sus secciones, Vox pasó de {n(S19["VOX"])} a {n(S23["VOX"])} y ERC, de {n(S19["ERC"])} a {n(S23["ERC"])}.</p>
{fig_sec}
<p data-tipo="contexto">A esa escala aparecen las fronteras que la provincia esconde. «Si bajamos al nivel de secciones censales —áreas de apenas 1.000 personas, a veces tan pequeñas como una manzana— aparecen contrastes y matices», escribían Borja Andrino, Luis Sevillano y Kiko Llaneras en <a href="https://elpais.com/espana/elecciones-generales/2023-07-24/el-mapa-con-los-resultados-de-las-elecciones-generales-del-23-j-calle-a-calle.html">El País</a> al publicar su mapa del 23J. En 2023, una de cada cuatro secciones eligió un ganador distinto del de su municipio, como explicamos en {L("como-voto-tu-calle", "cómo buscar tu calle en el mapa")}.</p>
<p data-tipo="dato">Las grandes ciudades lo enseñan bien. En Barcelona, el PSC fue el más votado en nueve de cada diez secciones, y ERC, que ganaba en 563 en 2019, {L("barcelona-barrio-a-barrio-29n", "no ganó en ninguna")}. En Sevilla, el PP ganó en votos, pero el PSOE fue primero en {L("sevilla-barrio-a-barrio-29n", "286 de sus 521 secciones")}. En Zaragoza hubo {L("zaragoza-barrio-a-barrio-29n", "empate barrio a barrio")}: 250 secciones para el PSOE y 245 para el PP. Y en Murcia, Vox pasó de ganar en 164 secciones a {L("murcia-barrio-a-barrio-29n", "ganar en una")}.</p>
<p data-tipo="patron">No todas las ciudades se parten igual. Con un índice que mide si los barrios vecinos votan parecido, Sevilla, Barcelona, Madrid, Bilbao o Granada votan por bloques de barrios, y Soria, Lugo o Cuenca, mezcladas. Lo que más se repite detrás de esos bloques es la distancia de renta entre barrios, como contamos en {L("capitales-partidas-por-barrios", "las capitales partidas por el voto")}.</p>
<h2>La renta dibuja el mapa</h2>
<p data-tipo="dato">Ordenadas las secciones de España por la renta de sus hogares, en el 10 % más pobre el PSOE sacó en 2023 el {pc(d1["PSOE"])} % de los votos y el PP, el {pc(d1["PP"])} %. En el 10 % más rico, el PP sacó el {pc(d10["PP"])} % y el PSOE, el {pc(d10["PSOE"])} %. Entre medias, en las secciones de renta media, los dos quedaron a menos de un punto.</p>
{fig_renta}
<p data-tipo="dato">Lo mismo pasa con quién vota. En el 10 % de secciones más pobres votó el {pc(d1["part"])} % del censo; en el 10 % más rico, el {pc(d10["part"])} %. En 2004 esa distancia era de 7,9 puntos; en 2023, de 15,2. Y en {L("barrios-donde-vota-menos-de-la-mitad", "534 secciones")} no votó ni la mitad del censo, tres de cada cuatro entre las más pobres.</p>
<p data-tipo="hipotesis">Son datos de lugares, no de personas: que un barrio rico vote más al PP no quiere decir que cada vecino con más renta lo haga. Y la renta no explica sola el mapa: {L("barrios-pobres-derecha-ricos-izquierda", "en la Región de Murcia, nueve de cada diez secciones pobres")} votaron más a PP y Vox que a PSOE y Sumar, y en Cataluña y el País Vasco hay barrios ricos que votan a la izquierda o a partidos nacionalistas.</p>
<h2>Lo que no se mueve desde 1977</h2>
<p data-tipo="dato">Debajo del mapa de cada elección hay otro que casi no cambia. De los 7.870 municipios con datos en las 16 generales, {L("municipios-fieles", "239 han tenido siempre el mismo ganador")}: 190 el PSOE, 28 el PNV, 11 AP y después el PP, y 10 CiU y después Junts. En el otro extremo, hay {L("nunca-gano-el-psoe", "1.932 municipios donde el PSOE nunca ha ganado")}, con Pozuelo de Alarcón como el mayor, y {L("nunca-gano-la-derecha", "864 donde la derecha estatal nunca ha sido la más votada")}, con Barcelona a la cabeza.</p>
<p data-tipo="patron">El mapa del conjunto de la derecha también se parece mucho al de hace casi medio siglo. En los municipios de más de 5.000 electores, el voto a UCD y AP de 1977 y el voto a PP y Vox de 2023 tienen una correlación de 0,59. Pero el de Vox no sigue al de AP: ahí la correlación es de 0,03, prácticamente ninguna, como explicamos en {L("mapa-derecha-1977-2023", "el mapa de la derecha de 1977 a 2023")}.</p>
<p data-tipo="dato">Hay, aun así, cambios de fondo. En {L("municipios-izquierda-1977-derecha-2023", "172 municipios")} con 2,23 millones de electores, la izquierda estatal sumó más que la derecha en todas las generales de 1977 a 2008 y en 2023 fue al revés. Son Sevilla, Jerez, Móstoles, Algeciras o Chiclana. El camino contrario lo han hecho 147, casi todos pequeños.</p>
<h2>Lo que dicen hoy las encuestas</h2>
<p data-tipo="dato">Ese es el mapa de partida. El de llegada lo dibujan, por ahora, las encuestas. A 23 de octubre, 16 encuestadoras habían publicado al menos un sondeo con trabajo de campo de los últimos 30 días: 15 dan ganador al PP y el CIS, al PSOE. Las 14 que publican escaños dan a PP y Vox juntos 176 o más, la mayoría absoluta. Están todas, con su fuente, en {f'<a href="{BASE}encuestas/">la página de encuestas</a>'}, que se actualiza cada día.</p>
<p data-tipo="hipotesis">El modelo de Mapa Electoral, que reparte la media de esas encuestas por provincia y simula el resultado miles de veces, daba el 23 de octubre al PP como primero en 43 provincias, al PSOE en 7, a EH Bildu en una y a ERC en otra. Las más disputadas eran Bizkaia, Ceuta, Sevilla, Lleida, Las Palmas y Girona. Es una estimación, no un resultado, y a cinco semanas el error típico de la media de encuestas es de unos cinco puntos para un partido del 30 %. Está, provincia a provincia, en {f'<a href="{BASE}encuestas/provincias.html">la encuesta por provincias</a>'}.</p>
<p data-tipo="contexto">Las encuestas también fallan. En las tres generales desde 2019, el CIS sobrestimó la ventaja del PSOE sobre el PP entre 1 y 6,9 puntos, como contamos en {L("cis-tezanos-estimacion-29n", "la pieza sobre el CIS de Tezanos")}. Los partidos lo saben. El jueves, en València, Feijóo pidió que «ningún voto del cambio se quede en casa», según Efe, que recogió <a href="https://www.infobae.com/espana/2026/10/23/elecciones-generales-en-espana-29-n-en-directo-ultima-hora-de-los-sondeos-los-debates-y-las-entrevistas-a-pedro-sanchez-y-feijoo/">Infobae</a>.</p>
<p data-tipo="patron">Donde se decidirá de verdad no es en el color de cada provincia, sino en el último escaño de cada una. En 2023, 32 escaños habrían cambiado de partido con menos de 5.000 votantes, y el Frente Amplio y Podemos no compartirán papeleta en 47 provincias. Lo contamos en dos piezas de este fin de semana: {L("provincias-en-el-filo-29n", "las provincias que deciden el 29N")} y {L("coaliciones-quien-va-con-quien-29n", "quién va con quién")}.</p>
<p data-tipo="dato">Para el 29N, el mapa de partida queda así: 40 provincias para el PP, 10 para el PSOE, una para EH Bildu y otra para el PNV; 18.407 secciones azules y 16.073 rojas. Y en Dos Hermanas, la cuenta de la serie va por 16 de 16.</p>
'''

preguntas = [
    ('¿Qué partido ganó en más provincias en las generales de 2023?',
     'El PP, que fue la lista más votada en 40 de las 52 circunscripciones. El PSOE ganó en 10, EH Bildu en Gipuzkoa y el PNV en Bizkaia.'),
    ('¿En qué provincias ganó el PSOE en 2023?',
     f'En {", ".join(psoe[:-1])} y {psoe[-1]}, con el voto exterior incluido.'),
    ('¿Cuántos barrios ganó cada partido en 2023?',
     f'De las 36.412 secciones censales con resultados, el PP fue el más votado en {n(S23["PP"])} y el PSOE en {n(S23["PSOE"])}. En noviembre de 2019, el PSOE había ganado en {n(S19["PSOE"])} y el PP en {n(S19["PP"])}.'),
    ('¿Cómo votan los barrios ricos y los pobres?',
     f'En el 10 % de secciones con menos renta, el PSOE sacó el {pc(d1["PSOE"])} % en 2023 y votó el {pc(d1["part"])} %. En el 10 % con más renta, el PP sacó el {pc(d10["PP"])} % y votó el {pc(d10["part"])} %.'),
    ('¿Qué municipios han votado siempre al mismo partido desde 1977?',
     'Son 239: 190 al PSOE, 28 al PNV, 11 a AP y luego al PP y 10 a CiU y luego a Junts. El mayor es Dos Hermanas (Sevilla), que ha votado al PSOE en las 16 generales.'),
    ('¿Qué dicen las encuestas para el 29N?',
     'A 23 de octubre, 15 de las 16 encuestadoras con sondeo reciente daban ganador al PP y el CIS, al PSOE. Las que publican escaños daban a PP y Vox juntos la mayoría absoluta. Son encuestas, no resultados.'),
    ('¿Dónde puedo ver cómo votó mi calle?',
     f'En el <a href="{BASE}">mapa electoral de la portada</a>: se escribe la dirección y el mapa enseña la sección censal, quién ganó en cada elección desde 2004 y su renta.'),
]

enlaces = (f'<a href="{BASE}">Explora el mapa por sección</a> · <a href="{BASE}encuestas/">Encuestas del 29N</a> · '
           f'{L("provincias-en-el-filo-29n", "Las provincias que deciden el 29N")} · {L("coaliciones-quien-va-con-quien-29n", "Quién va con quién el 29N")}')
foot = ('Datos: Ministerio del Interior, generales de 2019 y 2023 por mesa (con voto exterior para las provincias, sin él para las secciones), '
        'vía pollspaindata; INE, Atlas de Distribución de Renta de los Hogares 2023. Encuestas, a 23 de octubre de 2026. Cálculo propio.')

pieza('asi-queda-el-mapa-29n', 'Así queda el mapa electoral de España antes del 29N',
      'Así queda el mapa electoral de España antes del 29N: el PP ganó en 40 provincias y el PSOE, en 10',
      'Del Dos Hermanas que siempre vota al PSOE al Madrid teñido de azul: el mapa de 2023 provincia a provincia y barrio a barrio, lo que no ha cambiado desde 1977 y lo que dicen hoy las encuestas.',
      '24 de octubre de 2026', cuerpo, preguntas, enlaces, foot)
