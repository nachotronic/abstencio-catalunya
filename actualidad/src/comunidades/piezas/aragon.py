"""Aragón: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/aragon_2023.pdf'
INVEST26 = 'https://theobjective.com/espana/politica/2026-04-29/azcon-investido-presidente-aragon-apoyo-vox/'
ALEGRIA = 'https://www.ultimahora.es/noticias/comunidades/2026/04/29/2619337/alegria-psoe-alerta-gobierno-vox-basa-segregar-entre-aragoneses-primera-segunda.html'
TERUEL = wiki('Teruel Existe')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Si hay un territorio que se parece a España cuando vota, es Aragón. En las 16 elecciones generales desde 1977, el partido más votado en Aragón ha sido siempre el mismo que ganó en el conjunto del país: UCD en las dos primeras, el PSOE de 1982 a 1993, el PP en 1996 y 2000, y así hasta el PP de 2023. Las provincias de Huesca y Zaragoza han acertado las 16. Teruel solo falló una vez, en noviembre de 2019, cuando ganó allí una lista que no se presentaba en ningún otro sitio.</p>
<p>En las elecciones a las Cortes de Aragón, en cambio, la comunidad ha seguido un camino propio. Durante tres décadas, el Partido Aragonés (PAR), un partido regionalista de centro, fue la llave de casi todos los gobiernos, con la derecha y con la izquierda. En 2026 se quedó fuera del parlamento por primera vez. Y el PP de Jorge Azcón gobierna desde abril con Vox dentro del Ejecutivo, por segunda vez en tres años.</p>

<h2>El parlamento de las coaliciones</h2>
<p>Ningún partido ha tenido nunca mayoría absoluta en las Cortes de Aragón. En las doce elecciones celebradas desde 1983, el más votado se quedó siempre por debajo de los 34 escaños que hacen falta, y en cuatro ocasiones (1987, 1991, 1999 y 2015) gobernó otro.</p>
{F.aut('Escaños en las Cortes de Aragón, 1983-2026', 'Diputados de cada partido en las doce elecciones autonómicas.')}
<p>El PSOE ganó las primeras, en 1983, y Santiago Marraco fue presidente con el apoyo del PCE y del CDS. En 1987 los socialistas volvieron a ser primeros, pero el PAR, con 19 escaños, sumó con AP y su líder, Hipólito Gómez de las Roces, llegó a la presidencia. Su sucesor, Emilio Eiroa, gobernó con el PP desde 1991 hasta que en 1993 una moción de censura dio la presidencia al socialista José Marco con los votos del PSOE, de la coalición de IU y de un diputado independiente.</p>
<p>A partir de ahí, el PAR cambió de socio según el momento: gobernó con el PP de Santiago Lanzuela (1995-1999), con el PSOE de Marcelino Iglesias durante doce años (1999-2011) y otra vez con el PP de Luisa Fernanda Rudi (2011-2015). En 2019 incluso entró en el Gobierno de cuatro partidos de Javier Lambán, con el PSOE, Podemos y Chunta Aragonesista.</p>
{presidentes([('1983', '1987', 'Santiago Marraco', 'PSOE'), ('1987', '1991', 'Hipólito Gómez de las Roces', 'PAR'), ('1991', '1993', 'Emilio Eiroa', 'PAR'),
              ('1993', '1995', 'José Marco', 'PSOE'), ('1995', '1995', 'Ramón Tejedor', 'PSOE'), ('1995', '1999', 'Santiago Lanzuela', 'PP'),
              ('1999', '2011', 'Marcelino Iglesias', 'PSOE'), ('2011', '2015', 'Luisa Fernanda Rudi', 'PP'), ('2015', '2023', 'Javier Lambán', 'PSOE'),
              ('2023', 'hoy', 'Jorge Azcón', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes del Gobierno de Aragón desde la primera legislatura (1983). Fuente: <a href="https://www.historiaelectoral.com/aaragon.html">Historia Electoral</a>.</p>

<h2>Ocho partidos y el declive del PAR</h2>
<p>El PAR llegó a sacar el 28% de los votos en 1987. Desde entonces fue perdiendo escaños en casi todas las elecciones: 10 en 1999, 6 en 2015, 3 en 2019 y uno en 2023. Mientras, el parlamento se llenaba de partidos: Chunta Aragonesista, con un pico de 9 escaños en 2003; Podemos y Ciudadanos desde 2015; Vox desde 2019, y Aragón-Teruel Existe desde 2023. El jurista José Luis Bermejo Latre, de la Universidad de Zaragoza, lo describía así tras las elecciones de 2023:</p>
{F.cita('el parlamento aragonés sigue siendo el más plural del Estado, con ocho partidos sentados en las Cortes de Aragón', 'José Luis Bermejo Latre', 'Universidad de Zaragoza, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>En el mismo informe, Bermejo Latre hablaba del PAR como «una formación histórica que viene sufriendo un deterioro progresivo y una escisión final en tres formaciones». En 2023 aún consiguió un escaño y una presencia en el Gobierno de Azcón en direcciones generales. En las elecciones del 8 de febrero de 2026, con el 1,2% de los votos según Historia Electoral, se quedó sin ninguno.</p>

<h2>2023 y 2026: el PP con Vox, dos veces</h2>
<p>En 2023, el PP ganó con 28 escaños y Azcón fue investido con los votos de Vox y del PAR. Aquella primera alianza con Vox, según <a href="{INVEST26}">The Objective</a>, duró once meses y acabó desembocando en las elecciones anticipadas de febrero de 2026, ante la imposibilidad de aprobar nuevos presupuestos.</p>
<p>El adelanto no le dio al PP lo que buscaba: bajó a 26 escaños, mientras Vox pasó de 7 a 14 y se hizo imprescindible. El PSOE de Pilar Alegría se quedó en 18, los mismos que en 2015, su peor resultado en escaños. Chunta Aragonesista subió de 3 a 6. El 29 de abril, Azcón fue investido con 39 votos, los del PP y 13 de los 14 de Vox, que entró en el Gobierno con tres de las nueve consejerías. En el debate, la socialista Alegría resumió así su rechazo al principio de «prioridad nacional» que recoge el acuerdo:</p>
{F.cita('segregar entre aragoneses de primera y de segunda', 'Pilar Alegría', 'portavoz del PSOE en las Cortes de Aragón, sobre el nuevo Gobierno', ALEGRIA, 'Última Hora (Europa Press)', '29 de abril de 2026')}

<h2>En las generales: el espejo de España</h2>
<p>En las generales, Aragón vota casi como la media. El PSOE sacó allí el 49,7% en 1982, frente al 48,2% en el conjunto de España; el PP, el 36,7% en 2023, frente al 33,5%. La diferencia con el resto del país está en los partidos aragoneses, que en el gráfico van en «Otras listas»: el PAR llegó al 19,2% en las generales de 1993; Chunta Aragonesista, al 10,6% en 2000, y en noviembre de 2019 apareció Teruel Existe.</p>
{F.gen('UCD, PSOE, PP y los demás en Aragón', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
{F.esp('PSOE y PP en Aragón, casi calcados a España', 'PSOE y AP/PP en Aragón y en el conjunto de España, en las generales.')}
<p>El acierto de Huesca y Zaragoza se ve en la rejilla de provincias: cada vez que España cambia de color, cambian ellas. Esa coincidencia baja también a los pueblos. En otra pieza de esta sección contamos que <a href="../plasencia-acierta-siempre/">solo 27 municipios de toda España han votado al ganador en las 16 generales</a>; catorce de ellos son aragoneses.</p>
{F.prov('Quién ganó en cada provincia aragonesa', 'Lista más votada en las generales de 1977 a 2023.')}
<p>La excepción es Teruel en noviembre de 2019. Allí la lista más votada fue <a href="{TERUEL}">Teruel Existe</a>, una plataforma ciudadana nacida para reclamar servicios e inversiones para la provincia, que logró un escaño en el Congreso. En 2023 volvió a ganar el PP.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios aragoneses con más electores.')}
<p>La ciudad de Zaragoza, con medio millón de electores, ha acompañado casi siempre a España. Teruel capital es más conservadora: votó a AP ya en 1982, cuando el PSOE arrasaba en el país. En el otro extremo, Ejea de los Caballeros ha votado al PSOE en todas las generales desde 1979. En 2023, el PP ganó en 477 municipios aragoneses y el PSOE, en 233.</p>
{F.mapa('Aragón, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}

<h2>Votar más que la media</h2>
<p>Aragón vota más que el conjunto de España en casi todas las generales. En 2023, sin contar el voto exterior, participó el 73,0% del censo, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Aragón y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Aragón elige 13 diputados: 7 por Zaragoza y 3 por Huesca y por Teruel. Con dos provincias que han acertado siempre, el 29 de noviembre servirá para ver si la racha sigue. También dirá si Teruel Existe recupera el voto que tuvo en 2019 y cuánto suma Vox seis meses después de volver al Gobierno de Aragón.</p>
"""


PIEZA = dict(
    cc='aragon', slug='aragon-historia-electoral', lugar='Aragón', corto='Aragón en las urnas',
    titulo='Huesca y Zaragoza han votado al ganador de España en las 16 generales; en sus Cortes nadie ha tenido nunca mayoría absoluta',
    dek='Aragón es el espejo electoral de España en las generales. En las autonómicas, el PAR fue durante 30 años la llave de casi todos los gobiernos, '
        'con la derecha y con la izquierda, y en 2026 se quedó fuera. El PP de Azcón gobierna con Vox por segunda vez.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='Huesca y Zaragoza han votado al ganador de España en las 16 generales desde 1977. En las Cortes de Aragón nadie ha tenido mayoría absoluta; el PAR fue la llave de casi todos los gobiernos y en 2026 se quedó fuera. Azcón gobierna con Vox.',
    compara='Las 12 elecciones a las Cortes de Aragón (1983-2026) y las 16 generales (1977-2023) en Aragón, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('aaragon', 'Aragón'),
                               (IDP23, 'José Luis Bermejo Latre, «Aragón», Informe Comunidades Autónomas 2023, Instituto de Derecho Público (IDP Barcelona)'),
                               (INVEST26, 'The Objective, «Azcón, investido de nuevo presidente de Aragón con el apoyo de Vox» (29-4-2026)'),
                               (ALEGRIA, 'Última Hora / Europa Press, intervención de Pilar Alegría en la investidura (29-4-2026)'),
                               (TERUEL, 'Wikipedia, Teruel Existe')],
    enlaces=[],
)
