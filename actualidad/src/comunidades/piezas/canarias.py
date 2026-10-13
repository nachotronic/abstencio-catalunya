"""Canarias: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP11 = 'https://www.idpbarcelona.net/docs/public/iccaa/2011/canarias_2011.pdf'
IDP19 = 'https://www.idpbarcelona.net/docs/public/iccaa/2019/canarias_2019.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/canarias_2023.pdf'
CLAVIJO = 'https://diariodeavisos.elespanol.com/2023/07/fernando-clavijo-investido-presidente-de-canarias-con-el-apoyo-de-cc-pp-asg-y-ahi/'
CAND27 = 'https://rtvc.es/cc-proclama-por-unanimidad-fernando-clavijo-candidato-presidencia-canarias-3-octubre-2026/'
W87 = wiki('Elecciones al Parlamento de Canarias de 1987')
W91 = wiki('Elecciones al Parlamento de Canarias de 1991')
W07 = wiki('Elecciones al Parlamento de Canarias de 2007')
W15 = wiki('Elecciones al Parlamento de Canarias de 2015')
W19 = wiki('Elecciones al Parlamento de Canarias de 2019')
W23 = wiki('Elecciones al Parlamento de Canarias de 2023')
G23 = wiki('Elecciones generales de España de 2023')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PSOE ha sido el partido más votado en siete de las once elecciones al Parlamento de Canarias. Solo ha presidido el Gobierno canario en tres etapas: de 1982 a 1987, de 1991 a 1993 y de 2019 a 2023. El resto del tiempo, la presidencia fue para el CDS y, sobre todo, para Coalición Canaria (CC), un partido nacionalista que ha gobernado 26 años seguidos, de 1993 a 2019, y que volvió en 2023 con el PP, aunque los socialistas habían vuelto a ganar.</p>
<p>La clave está en la aritmética de las islas. Cada isla elige sus propios diputados, y durante 36 años las cinco menos pobladas eligieron tantos como Tenerife y Gran Canaria juntas. Ese reparto ha premiado a los partidos fuertes en las islas pequeñas y ha hecho que ganar en votos no baste para gobernar.</p>
<p>En las generales, Canarias se ha repartido entre PSOE y PP a partes iguales: siete victorias cada uno desde 1982. Y es la comunidad donde menos se vota. Este reportaje recorre esa historia con las once autonómicas, de 1983 a 2023, y las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Ganar en votos no basta</h2>
<p>El Estatuto de Autonomía de Canarias se aprobó en agosto de 1982 y el primer Parlamento se eligió en mayo de 1983. El PSOE de Jerónimo Saavedra sacó el 42,4% de los votos y 27 de los 60 escaños, y fue investido con el apoyo de Asamblea Majorera y de las agrupaciones independientes de La Gomera y El Hierro, según Historia Electoral.</p>
{F.aut('Escaños en el Parlamento de Canarias, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas. «CC y predecesores» incluye las AIC y las agrupaciones insulares aliadas.')}
<p>El sistema de la «triple paridad», aplicado en las elecciones de 1983 a 2015, repartía los 60 escaños así: 30 para cada provincia, 15 para Tenerife y 15 para Gran Canaria, y otros 30 para Lanzarote, Fuerteventura, La Palma, La Gomera y El Hierro, aunque en las dos islas mayores vive más de cuatro de cada cinco canarios, según <a href="{W07}">Wikipedia</a>. Además, había que sacar el 30% de los votos en una isla o el 6% en toda Canarias para entrar en el reparto.</p>
<p>Las consecuencias se vieron pronto. En 1987 el PSOE volvió a ser el más votado, pero un pacto del CDS, las Agrupaciones Independientes de Canarias (AIC), AP y la Agrupación Herreña Independiente dio la presidencia a Fernando Fernández, del CDS, relevado a finales de 1988 por Lorenzo Olarte, de su mismo partido, según la <a href="{W87}">crónica de aquellas elecciones</a>. Saavedra volvió en 1991 con el apoyo de las AIC, pero en 1993 Manuel Hermoso, de las propias AIC, ganó una moción de censura contra el Gobierno del que formaba parte, según la <a href="{W91}">crónica de 1991</a>. En 1995, ya como candidato de Coalición Canaria, Hermoso fue el más votado.</p>
{presidentes([('1982', '1987', 'Jerónimo Saavedra', 'PSOE'), ('1987', '1988', 'Fernando Fernández', 'CDS'), ('1988', '1991', 'Lorenzo Olarte', 'CDS'),
              ('1991', '1993', 'Jerónimo Saavedra', 'PSOE'), ('1993', '1999', 'Manuel Hermoso', 'AIC / CC'), ('1999', '2003', 'Román Rodríguez', 'CC'),
              ('2003', '2007', 'Adán Martín', 'CC'), ('2007', '2015', 'Paulino Rivero', 'CC'), ('2015', '2019', 'Fernando Clavijo', 'CC'),
              ('2019', '2023', 'Ángel Víctor Torres', 'PSOE'), ('2023', 'hoy', 'Fernando Clavijo', 'CC')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes del Gobierno de Canarias desde el Estatuto de 1982. Antes hubo cinco presidencias de la Junta preautonómica. Fuente: <a href="https://www.historiaelectoral.com/acanarias.html">Historia Electoral</a>.</p>

<h2>Veintiséis años de Coalición Canaria</h2>
<p>CC fue la lista más votada en 1995, 1999 y 2003, y gobernó con el apoyo del PP. Desde 2007, en cambio, gobernó sin ganar. Aquel año el PSOE de Juan Fernando López Aguilar sacó el 35% y 26 escaños, pero CC y el PP sumaron 34 y Paulino Rivero fue investido presidente. Cuatro años después, en 2011, el PP fue el más votado y empató a 21 escaños con CC, y fueron los socialistas, terceros con 15, quienes entraron en el Gobierno de Rivero. El jurista José Suay Rincón, de la Universidad de Las Palmas de Gran Canaria, señaló la paradoja:</p>
{F.cita('hace cuatro años, en las anteriores elecciones autonómicas y locales el PSOE había triunfado claramente, se había quedado cerca de la mayoría absoluta y sin embargo no alcanzó el Gobierno; ahora, en cambio, que ha ocurrido lo contrario, sí que lo ha hecho, bien que como socio minoritario', 'José Suay Rincón', 'Universidad de Las Palmas de Gran Canaria, en el Informe Comunidades Autónomas 2011 del Instituto de Derecho Público', IDP11, 'IDP Barcelona', '2012')}
<p>En 2015 pasó algo parecido: el PSOE fue primero en votos (19,9%), y CC, tercera en votos, primera en escaños, como recoge <a href="{W15}">Wikipedia</a>. Fernando Clavijo, de CC, fue investido con los votos del PSOE y de la Agrupación Socialista Gomera, entre otros.</p>

<h2>2019 y 2023: el turno del PSOE y la vuelta de CC</h2>
<p>En 2019 se estrenó un sistema nuevo, aprobado con la reforma del Estatuto de 2018: 70 diputados, con una circunscripción regional de 9 escaños para compensar el peso de las islas pequeñas, según la <a href="{W19}">crónica de aquellas elecciones</a>. El PSOE de Ángel Víctor Torres ganó con 25 escaños y formó un Gobierno de cuatro partidos con Nueva Canarias, Podemos y la Agrupación Socialista Gomera. Suay Rincón lo resumió así:</p>
{F.cita('el PSOE alcanza unas cotas de poder como nunca ha tenido en la historia de Canarias. Recupera el gobierno autonómico 26 años después', 'José Suay Rincón', 'Universidad de Las Palmas de Gran Canaria, en el Informe Comunidades Autónomas 2019 del Instituto de Derecho Público', IDP19, 'IDP Barcelona', '2020')}
<p>Duró una legislatura. En mayo de 2023 el PSOE volvió a ser el más votado, con 23 escaños, pero CC (19) y el PP (15) sumaron con la Agrupación Socialista Gomera (3) y la Herreña (1). El 12 de julio, Clavijo fue investido con 38 votos frente a 32, los del PSOE, Nueva Canarias y Vox, según <a href="{CLAVIJO}">Diario de Avisos</a>. Ante el pleno, pidió acuerdos más allá de la legislatura:</p>
{F.cita('Canarias no está condenada a vivir con sus problemas como si fueran enfermedades crónicas', 'Fernando Clavijo', 'candidato de CC, en el debate de investidura', CLAVIJO, 'Diario de Avisos (EFE)', '12 de julio de 2023')}
<p>El 3 de octubre de 2026, CC lo proclamó por unanimidad candidato a la presidencia para las autonómicas de mayo de 2027, según <a href="{CAND27}">RTVC</a>.</p>

<h2>En las generales: un empate a siete</h2>
<p>En las generales, Canarias empezó votando a UCD más que ninguna otra comunidad: el 60,8% en 1977 y el 58,5% en 1979. Desde 1982, el PSOE y el PP han ganado siete veces cada uno, y tres de esas veces la comunidad votó distinto que España: el PP fue el más votado en Canarias en 1993 y en 2004, cuando ganaba el PSOE en el país, y el PSOE ganó en las islas en 2023, cuando en España el más votado fue el PP.</p>
{F.gen('PSOE, PP, CC y los demás en Canarias', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>Coalición Canaria también se presenta a las generales. Su mejor resultado fue en 2000, con el 29,6%, por delante del PSOE; desde 2011 no ha pasado del 16%. En diciembre de 2015, Podemos sacó el 26,5% en la provincia de Las Palmas, a menos de dos puntos del PP (28,2%), según los <a href="https://en.wikipedia.org/wiki/Results_of_the_2015_Spanish_Congress_election">resultados por circunscripción</a>.</p>
{F.esp('PSOE y PP en Canarias y en España', 'PSOE y AP/PP en Canarias y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en cada provincia canaria', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Las dos provincias no siempre votan igual. Santa Cruz de Tenerife se mantuvo con el PSOE en 1993, 1996 y 2004, cuando Las Palmas votaba al PP; en 2023 fue al revés, el PP ganó en Santa Cruz de Tenerife y el PSOE en Las Palmas.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios canarios con más electores.')}
<p>Entre las ciudades grandes, Las Palmas de Gran Canaria y La Laguna votaron al PSOE en 2023, y Santa Cruz de Tenerife, al PP. Arrecife, en Lanzarote, ha votado al PSOE en 12 de las 16 generales. La Orotava es la más nacionalista: CC fue la lista más votada allí en 2000, 2004, 2008 y las dos elecciones de 2019.</p>
<p>El mapa municipal muestra lo rápido que cambia el voto en las islas. En 1977, UCD ganó en los 87 municipios con datos. En 2000, el año de su mejor resultado, CC fue la más votada en 27 municipios, sobre todo en Tenerife. En 2011 el PP ganó en 83 de los 88, y en noviembre de 2019 el PSOE, en 69. En 2023 el mapa quedó casi empatado: 42 municipios para el PP, 41 para el PSOE, 3 para CC y 2 para otras listas. El PSOE ganó en los siete municipios de Lanzarote y en 13 de los 21 de Gran Canaria; el PP, en 23 de los 31 de Tenerife.</p>
{F.mapa('Canarias, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Ninguno de los 85 municipios con datos en las 16 generales ha votado siempre al mismo partido.</p>

<h2>La comunidad que menos vota</h2>
<p>Canarias es, de media, la comunidad autónoma con menos participación en las generales, solo por encima de Ceuta y Melilla. Sin contar el voto exterior, quedó por debajo de la media española en las 16 elecciones. En 2023 votó el 63,6% del censo, frente al 70,4% del conjunto del país.</p>
{F.part('Participación en las generales: Canarias y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Canarias elige 15 diputados: 8 en Las Palmas y 7 en Santa Cruz de Tenerife. En 2023 fueron 6 para el PP, 6 para el PSOE y uno para Vox, Sumar y Coalición Canaria, que lo sacó en Santa Cruz de Tenerife, según los <a href="{G23}">resultados oficiales</a>. El 29 de noviembre dirá si el PSOE repite como lista más votada en las islas, si CC conserva su escaño y si la participación sigue siendo la más baja del país.</p>
"""


PIEZA = dict(
    cc='canarias', slug='canarias-historia-electoral', lugar='Canarias', corto='Canarias en las urnas',
    titulo='El PSOE ha ganado siete de las once autonómicas canarias, pero solo ha gobernado tres legislaturas',
    dek='Coalición Canaria presidió el Gobierno 26 años seguidos y volvió en 2023 con el PP, aunque los socialistas habían vuelto a ser los más votados. '
        'En las generales, PSOE y PP llevan siete victorias cada uno, y Canarias es la comunidad donde menos se vota.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSOE ha sido el más votado en siete de las once autonómicas canarias, pero solo ha gobernado tres legislaturas: Coalición Canaria presidió el Gobierno de 1993 a 2019 y desde 2023. En las generales, PSOE y PP empatan a siete victorias.',
    compara='Las 11 elecciones al Parlamento de Canarias (1983-2023) y las 16 generales (1977-2023) en Canarias, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('acanarias', 'Canarias'),
                               (IDP11, 'José Suay Rincón, «Canarias», Informe Comunidades Autónomas 2011, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP19, 'José Suay Rincón, «Canarias», Informe Comunidades Autónomas 2019, IDP Barcelona'),
                               (IDP23, 'José Suay Rincón, «Canarias», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (CLAVIJO, 'Diario de Avisos / EFE, «Fernando Clavijo, investido presidente de Canarias con el apoyo de CC, PP, ASG y AHI» (12-7-2023)'),
                               (CAND27, 'RTVC, «CC proclama por unanimidad a Fernando Clavijo candidato a la Presidencia de Canarias en 2027» (3-10-2026)'),
                               (W87, 'Wikipedia, Elecciones al Parlamento de Canarias de 1987'),
                               (W91, 'Wikipedia, Elecciones al Parlamento de Canarias de 1991'),
                               (W07, 'Wikipedia, Elecciones al Parlamento de Canarias de 2007'),
                               (W15, 'Wikipedia, Elecciones al Parlamento de Canarias de 2015'),
                               (W19, 'Wikipedia, Elecciones al Parlamento de Canarias de 2019'),
                               (W23, 'Wikipedia, Elecciones al Parlamento de Canarias de 2023'),
                               (G23, 'Wikipedia, Elecciones generales de España de 2023 (escaños por circunscripción)')],
    enlaces=[],
)
