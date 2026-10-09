"""Galicia: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP20 = 'https://www.idpbarcelona.net/docs/public/iccaa/2020/galicia_2020.pdf'
PONTON = 'https://www.elsaltodiario.com/elecciones/mejor-resultado-historico-bng-insuficiente-quitar-mayoria-PP'
BOE26 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742'
W85 = wiki('Elecciones al Parlamento de Galicia de 1985')
W24 = wiki('Elecciones al Parlamento de Galicia de 2024')
WG23 = wiki('Elecciones generales de España de 2023')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PP ha ganado las doce elecciones al Parlamento de Galicia, desde la primera, en 1981, hasta la última, en febrero de 2024. En nueve de ellas sacó mayoría absoluta. Solo dos veces perdió la Xunta: en 1987, por una moción de censura, y en 2005, cuando se quedó a un escaño de la mayoría y el PSdeG y el BNG sumaron para gobernar juntos.</p>
<p>En las generales, la regla es casi la misma. Desde 1982 la lista más votada en Galicia ha sido AP o el PP en todas las elecciones menos una, la de abril de 2019. Galicia votó a AP en 1982, 1986, 1989 y 1993, cuando España votaba al PSOE de Felipe González. Lo que ha cambiado es quién ocupa el segundo puesto: el BNG ha superado a los socialistas en las dos últimas autonómicas y en 2024 logró su mejor resultado.</p>
<p>Este reportaje recorre esa historia con los resultados de las doce elecciones autonómicas, de 1981 a 2024, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Doce victorias del PP</h2>
<p>El Estatuto de Autonomía de Galicia se aprobó en referéndum el 21 de diciembre de 1980, y el primer Parlamento se votó el 20 de octubre de 1981, con una participación del 46,3%, según los datos de <a href="{wiki('Elecciones al Parlamento de Galicia de 1981')}">Wikipedia</a>. Alianza Popular fue la lista más votada, con 26 de los 71 escaños, por delante de UCD, con 24. Xerardo Fernández Albor fue investido presidente en enero de 1982 con los votos de AP y de UCD, según los registros de Historia Electoral.</p>
{F.aut('Escaños en el Parlamento de Galicia, 1981-2024', 'Diputados de cada partido en las doce elecciones autonómicas.')}
<p>Albor repitió como el más votado en 1985, con 34 escaños, dos menos que la mayoría absoluta de aquella cámara de 71. En octubre de 1986 su vicepresidente, Xosé Luis Barreiro, fue destituido y expulsado de AP, y formó grupo propio con otros cuatro diputados. En noviembre de 1987 una moción de censura hizo presidente al socialista Fernando González Laxe, con el apoyo de PSdeG, Coalición Galega, el PNG y el PSG-EG y la abstención del BNG, según <a href="{W85}">la crónica de aquella legislatura</a>.</p>
<p>En 1989 llegó <a href="{wiki('Manuel Fraga')}">Manuel Fraga</a>. El exministro y fundador de AP ganó con 38 de los 75 escaños, justo la mayoría absoluta, y fue investido en enero de 1990 solo con los votos de su grupo. Repitió mayoría en 1993, 1997 y 2001, siempre por encima del 51% de los votos. Gobernó quince años seguidos.</p>
{presidentes([('1981', '1982', 'José Quiroga', 'UCD'), ('1982', '1987', 'Xerardo Fernández Albor', 'AP'), ('1987', '1990', 'Fernando González Laxe', 'PSdeG-PSOE'),
              ('1990', '2005', 'Manuel Fraga', 'PP'), ('2005', '2009', 'Emilio Pérez Touriño', 'PSdeG-PSOE'), ('2009', '2022', 'Alberto Núñez Feijóo', 'PP'),
              ('2022', 'hoy', 'Alfonso Rueda', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Xunta de Galicia desde el Estatuto de 1981. Quiroga ya presidía el ente preautonómico desde 1979. Fuente: <a href="https://www.historiaelectoral.com/agalicia.html">Historia Electoral</a>.</p>

<h2>2005: el PSdeG y el BNG, juntos</h2>
<p>En 2005 el PP de Fraga bajó a 37 escaños, uno menos que la mayoría absoluta. El PSdeG de Emilio Pérez Touriño, con 25, y el BNG de Anxo Quintana, con 13, sumaron justo 38. Touriño fue investido el 29 de julio con esos 38 votos frente a los 37 del PP, y Quintana fue su vicepresidente. Es la única vez que el BNG ha entrado en la Xunta.</p>
<p>Duró una legislatura. En 2009 el PP de Alberto Núñez Feijóo recuperó la mayoría absoluta con 38 escaños, y la amplió después: 41 en 2012, 41 en 2016 y 42 en 2020. En mayo de 2022 Feijóo dejó la Xunta para presidir el PP en toda España, y el Parlamento invistió a Alfonso Rueda, según recoge <a href="{W24}">Wikipedia</a>.</p>

<h2>La oposición cambia de manos</h2>
<p>Lo que sí se ha movido es el segundo puesto. El BNG pasó de 1 escaño en 1985 a 18 en 1997, por delante de los socialistas, que sacaron 15, y empató con ellos a 17 en 2001. En 2012 y 2016 irrumpieron las candidaturas de la izquierda alternativa, AGE con 9 escaños y En Marea con 14. En 2020 el BNG de Ana Pontón saltó de 6 a 19 diputados. El constitucionalista Roberto L. Blanco Valdés, de la Universidad de Santiago de Compostela, explicaba que la ventaja del BNG sobre los socialistas aquel año fue «la mayor que el BNG había conseguido sobre los socialistas desde el establecimiento del sistema autonómico».</p>
<p>En febrero de 2024 el PP de Rueda volvió a ganar, con 40 escaños, dos menos que en 2020, y el 47,4% de los votos. El BNG llegó a 25 diputados y el 31,3%, su récord; el PSdeG se quedó en 9, su peor resultado. Pontón lo resumió así la noche electoral:</p>
{F.cita('Hemos tenido un resultado que rompe con todos los techos electorales del BNG y que nos sitúa como la esperanza de todas las personas que creen que Galicia necesita más', 'Ana Pontón', 'candidata del BNG a la Presidencia de la Xunta', PONTON, 'El Salto', '18 de febrero de 2024')}
<p>Rueda fue investido el 11 de abril de 2024 con los 40 votos del PP; el BNG y el PSdeG votaron en contra, y el diputado de Democracia Ourensana se abstuvo. Las próximas autonómicas tocan en 2028.</p>

<h2>En las generales: azul desde 1982</h2>
<p>En las dos primeras generales, las de 1977 y 1979, UCD ganó en Galicia con mucha ventaja: el 53,8% y el 48,6% de los votos. Desde 1982 la lista más votada ha sido siempre AP o el PP, con una sola excepción. Su mejor resultado fue el 54,5% de 2000. El BNG, que en el gráfico tiene su propia línea, llegó ese mismo año al 19,4%, su máximo en unas generales.</p>
{F.gen('PP, PSOE, UCD, BNG y los demás en Galicia', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>La excepción fue abril de 2019, cuando el PSOE sacó el 32,5% y el PP, el 27,7%. Blanco Valdés lo recordaba en su informe del año siguiente:</p>
{F.cita('se produjo un hecho desconocido en Galicia hasta la fecha: el Partido de los Socialistas de Galicia fue el ganador de los comicios', 'Roberto L. Blanco Valdés', 'Universidad de Santiago de Compostela, en el Informe Comunidades Autónomas 2020 del Instituto de Derecho Público', IDP20, 'IDP Barcelona', '2021')}
<p>Siete meses después, en noviembre de 2019, el PP volvió a ganar por siete décimas. En 2023 sacó el 43,9%, casi catorce puntos más que el PSOE.</p>
{F.esp('PSOE y PP en Galicia y en España', 'PSOE y AP/PP en Galicia y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en cada provincia gallega', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Por provincias, Lugo y Ourense han votado a AP o al PP en todas las generales desde 1982, y a UCD en las dos anteriores. Pontevedra solo se pasó al PSOE en las dos elecciones de 2019. A Coruña es la más cambiante: votó a los socialistas en 1982, 1986 y 1989, y en abril de 2019.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios gallegos con más electores.')}
<p>Las ciudades votan algo distinto que el resto. Vigo, la mayor, votó al PSOE en 2004, 2008 y en las tres últimas generales, y en 2015 eligió a la candidatura de Podemos y las mareas. A Coruña votó a los socialistas en los ochenta. Santiago de Compostela, en cambio, ha votado al PP en todas las generales desde 1982 salvo la de abril de 2019. En 2023 el PP ganó en nueve de las diez mayores ciudades: todas menos Vigo.</p>
<p>El mapa municipio a municipio muestra hasta qué punto el voto de la derecha cubre casi todo el territorio. En 1977, UCD fue la lista más votada en 297 de los 309 municipios gallegos con datos. En 1982 el mapa se partió: AP ganó en 153; UCD resistió en 94, sobre todo en el interior de Ourense y de Pontevedra, y el PSOE fue primero en 58, en la costa norte de A Coruña, en la ría de Arousa y en algunos municipios de la montaña del este de Lugo y de Ourense. En abril de 2019, el año en que el PSOE ganó en Galicia, el PP siguió siendo el más votado en 195 municipios, frente a 117 de los socialistas, que ganaron alrededor de A Coruña y de Ferrol, en el sur de Pontevedra, cerca de Vigo, y en la montaña del este de Lugo. Y en 2023 el PP fue primero en 298 de los 313, y el PSOE, en 15.</p>
{F.mapa('Galicia, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Solo tres de los 307 municipios con datos en las 16 elecciones han votado siempre a la misma lista: Vilalba, Riotorto y Beade, los tres a AP o al PP, también en 1977 y 1979, cuando en casi toda Galicia ganaba UCD. Vilalba es la villa natal de Manuel Fraga, según su <a href="{wiki('Manuel Fraga')}">biografía</a>.</p>

<h2>Votar menos que la media</h2>
<p>Galicia votaba mucho menos que el resto de España en las primeras generales: en 1979 participó el 50,8% del censo, frente al 67,6% del conjunto, sin contar el voto exterior. La distancia se fue cerrando y en 2023, por primera vez desde 2011, Galicia votó más que la media: el 73,2% frente al 70,4%.</p>
{F.part('Participación en las generales: Galicia y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Galicia elige 23 diputados: 8 por A Coruña, 7 por Pontevedra y 4 por Lugo y por Ourense, según el <a href="{BOE26}">decreto de convocatoria</a>. En 2023 fueron 13 para el PP, 7 para el PSOE, 2 para Sumar y 1 para el BNG, según los resultados <a href="{WG23}">recogidos en Wikipedia</a>. El 29 de noviembre dirá si el BNG traslada a las generales el récord que logró en las autonómicas de 2024 y si Vigo, la única gran ciudad gallega donde el PP no ganó en 2023, sigue con los socialistas.</p>
"""


PIEZA = dict(
    cc='galicia', slug='galicia-historia-electoral', lugar='Galicia', corto='Galicia en las urnas',
    titulo='El PP ha ganado las doce elecciones gallegas y solo perdió la Xunta dos veces; en las generales, el PSOE ganó allí una sola vez, en 2019',
    dek='AP y el PP han sido la lista más votada en todas las autonómicas desde 1981, con nueve mayorías absolutas. '
        'En las generales, Galicia votó a AP incluso cuando España votaba a Felipe González. El BNG es hoy la segunda fuerza en el Parlamento, con su récord de 25 escaños.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PP ha ganado las doce elecciones al Parlamento de Galicia y solo perdió la Xunta en 1987 y en 2005. En las generales, el PSOE fue el más votado en Galicia una sola vez, en abril de 2019. El BNG logró su récord en 2024.',
    compara='Las 12 elecciones al Parlamento de Galicia (1981-2024) y las 16 generales (1977-2023) en Galicia, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('agalicia', 'Galicia'),
                               (IDP20, 'Roberto L. Blanco Valdés, «Galicia», Informe Comunidades Autónomas 2020, Instituto de Derecho Público (IDP Barcelona)'),
                               (PONTON, 'El Salto, «El mejor resultado histórico del BNG es insuficiente para quitar la mayoría al PP» (18-2-2024)'),
                               (W85, 'Wikipedia, Elecciones al Parlamento de Galicia de 1985'),
                               (W24, 'Wikipedia, Elecciones al Parlamento de Galicia de 2024'),
                               (WG23, 'Wikipedia, Elecciones generales de España de 2023'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones')],
    enlaces=[],
)
