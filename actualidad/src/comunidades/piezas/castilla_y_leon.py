"""Castilla y León: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP19 = 'https://www.idpbarcelona.net/docs/public/iccaa/2019/cyl_2019.pdf'
IDP22 = 'https://www.idpbarcelona.net/docs/public/iccaa/2022/cyl_2022.pdf'
MANUECO22 = 'https://www.publico.es/politica/manueco-dialogar-formar-gobierno-y.html'
INVEST22 = 'https://theobjective.com/espana/2022-04-11/alfonso-fernandez-manueco-investido-presidente-de-castilla-y-leon-con-el-apoyo-de-vox/'
INVEST26 = 'https://www.elespanol.com/castilla-y-leon/region/20260609/manueco-investido-presidente-junta-castilla-leon-votos-pp-vox/1003744279860_0.html'
GEN23 = 'https://www.ultimahora.es/elecciones/23j/congreso/castilla-y-leon.html'
BOE26 = 'https://www.boe.es/boe/dias/2026/10/06/pdfs/BOE-A-2026-20742.pdf'
W87 = wiki('Elecciones a las Cortes de Castilla y León de 1987')
W26 = wiki('Elecciones a las Cortes de Castilla y León de 2026')
LUCAS = wiki('Juan José Lucas')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PP gobierna Castilla y León desde 1987. Son casi cuarenta años seguidos y cinco presidentes, de José María Aznar a Alfonso Fernández Mañueco, que en junio de 2026 fue investido por tercera vez, de nuevo con Vox. En ese tiempo el PSOE ganó en escaños unas autonómicas, las de 2019, y aun así no llegó a gobernar.</p>
<p>En las generales, la comunidad es todavía más del PP. Fue la lista más votada en 11 de las 16 elecciones desde 1977, incluidas cinco que en el conjunto de España ganó el PSOE. Y en todas ha sacado aquí más porcentaje de voto que en el conjunto del país.</p>
<p>Este reportaje recorre esa historia con los resultados de las doce elecciones a las Cortes de Castilla y León, de 1983 a 2026, y de las dieciséis generales, en los más de 2.200 municipios de la comunidad.</p>

<h2>Cuatro años socialistas y un empate</h2>
<p>Las primeras Cortes se votaron en mayo de 1983. El PSOE sacó 42 de los 84 escaños, la mitad justa, y Demetrio Madrid fue investido en segunda votación con los 42 votos socialistas, frente a 39 en contra, según Historia Electoral. Madrid dimitió en 1986 y otro socialista, José Constantino Nalda, terminó la legislatura, según la <a href="{W87}">crónica de aquellos años</a>.</p>
<p>En 1987 AP y PSOE empataron a 32 escaños, aunque AP tuvo unos 5.000 votos más. El CDS, con 18 procuradores, decidió la investidura absteniéndose: José María Aznar fue elegido presidente en la segunda votación, con 34 votos a favor y 32 en contra, según Historia Electoral. En 1989 Aznar dejó la Junta y le sustituyó Jesús Posada, ya con los votos del CDS a favor.</p>
{F.aut('Escaños en las Cortes de Castilla y León, 1983-2026', 'Procuradores de cada partido en las doce elecciones autonómicas.')}
<p>Después llegaron seis mayorías absolutas seguidas del PP, de 1991 a 2011. Juan José Lucas gobernó diez años, hasta que en 2001 pasó al Gobierno de Aznar, según su <a href="{LUCAS}">biografía</a>, y Juan Vicente Herrera fue presidente durante dieciocho, de 2001 a 2019. El mejor resultado del PP en votos fue el de 1995, con el 52,3%; en escaños, el de 2011, con 53. En 2015 el PP se quedó en 42, uno menos de la mayoría, y Herrera fue investido en segunda votación gracias a la abstención de los cinco procuradores de Ciudadanos.</p>
{presidentes([('1983', '1986', 'Demetrio Madrid', 'PSOE'), ('1986', '1987', 'José Constantino Nalda', 'PSOE'), ('1987', '1989', 'José María Aznar', 'AP / PP'),
              ('1989', '1991', 'Jesús Posada', 'PP'), ('1991', '2001', 'Juan José Lucas', 'PP'), ('2001', '2019', 'Juan Vicente Herrera', 'PP'),
              ('2019', 'hoy', 'Alfonso Fernández Mañueco', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Junta de Castilla y León desde el Estatuto de 1983. Antes hubo dos presidentes del Consejo General preautonómico, Juan Manuel Reol y José Manuel García-Verdugo. Fuente: <a href="https://www.historiaelectoral.com/acleon.html">Historia Electoral</a>.</p>
<p>El parlamento ha tenido siempre un hueco para los partidos provinciales. La Unión del Pueblo Leonés (UPL), que defiende una autonomía propia para la región leonesa, ha tenido procuradores en todas las Cortes desde 1995. Se les sumaron Por Ávila en 2019 y Soria ¡Ya! en 2022.</p>

<h2>2019: ganar y no gobernar</h2>
<p>En mayo de 2019 el PSOE de Luis Tudanca ganó las autonómicas con 35 procuradores, seis más que el PP. Pero Ciudadanos, con 12, prefirió pactar con el PP, y Mañueco fue investido el 9 de julio con 41 votos, la mayoría absoluta justa de una cámara que había bajado de 84 a 81 escaños por la pérdida de población, como recuerda Bilbao Ubillos. El constitucionalista Juan María Bilbao Ubillos, de la Universidad de Valladolid, lo resumía así:</p>
{F.cita('el PP, pese a perder las elecciones, acabaría liderando un gobierno de coalición con Ciudadanos, y al PSOE no le sirvió de nada ganar holgadamente los comicios, porque se quedó sin pareja de baile', 'Juan María Bilbao Ubillos', 'Universidad de Valladolid, en el Informe Comunidades Autónomas 2019 del Instituto de Derecho Público', IDP19, 'IDP Barcelona', '2020')}

<h2>2022 y 2026: el PP con Vox</h2>
<p>En diciembre de 2021 Mañueco sacó a Ciudadanos de su Gobierno y adelantó las elecciones al 13 de febrero de 2022, según recoge <a href="{W26}">Wikipedia</a>. El PP ganó con 31 procuradores, lejos de los 41 de la mayoría, y Vox pasó de 1 a 13. La misma noche, Mañueco anunció un gobierno de su partido:</p>
{F.cita('Será un Gobierno del PP con diálogo y acuerdo', 'Alfonso Fernández Mañueco', 'presidente de la Junta y candidato del PP, la noche electoral', MANUECO22, 'Público', '13 de febrero de 2022')}
<p>No fue así. El 11 de abril fue investido con 44 votos, los del PP y los de Vox, que entró en el Ejecutivo con la vicepresidencia, para Juan García-Gallardo, y tres consejerías, según <a href="{INVEST22}">la crónica de la investidura</a>. Bilbao Ubillos lo señalaba como un hecho sin precedentes:</p>
{F.cita('Vox tiene pues la llave de la gobernabilidad y accederá por primera vez a un Gobierno autonómico', 'Juan María Bilbao Ubillos', 'Universidad de Valladolid, en el Informe Comunidades Autónomas 2022 del Instituto de Derecho Público', IDP22, 'IDP Barcelona', '2023')}
<p>Vox salió de aquel Gobierno en julio de 2024, y Mañueco terminó la legislatura en minoría. En las elecciones del 15 de marzo de 2026, el PP subió a 33 procuradores, con el 35,4% de los votos; el PSOE, a 30, y Vox, a 14, con el 18,9%, según Historia Electoral. Soria ¡Ya! bajó de 3 a 1, y Podemos y Ciudadanos se quedaron fuera. El 9 de junio Mañueco fue investido por tercera vez, con 47 votos a favor, los del PP y Vox, y 35 en contra, los del PSOE, la UPL, Soria ¡Ya! y Por Ávila. El portavoz de Vox, Carlos Pollán, será vicepresidente, según <a href="{INVEST26}">El Español</a>.</p>

<h2>En las generales: el PP por encima de la media</h2>
<p>Castilla y León fue la comunidad de UCD en la Transición: el partido de Adolfo Suárez sacó aquí el 51,5% de los votos en 1977 y otra vez en 1979, y fue la lista más votada en 2.039 municipios en 1977. Después, el PSOE ganó en la comunidad solo tres veces: en 1982, en 1986 y en abril de 2019. El PP fue el más votado en todas las demás, también en 1989, 1993, 2004, 2008 y noviembre de 2019, cuando en España ganaba el PSOE.</p>
{F.gen('UCD, PSOE, PP y los demás en Castilla y León', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>La distancia con el resto de España se ve en el gráfico siguiente. El PP ha sacado en Castilla y León más porcentaje de voto que en el conjunto del país en las 16 generales; en 1989, casi quince puntos más. El PSOE estuvo por debajo de su media nacional hasta 2008, y desde 2011 está ligeramente por encima.</p>
{F.esp('El PP de Castilla y León, siempre por encima del de España', 'PSOE y AP/PP en Castilla y León y en el conjunto de España, en las generales.')}
<p>De las nueve provincias, solo León se parece a España: ha votado al ganador nacional en 15 de las 16 generales, todas menos la de 1993, cuando allí ganó el PP. En el otro extremo está Ávila, la única que no ha votado nunca al PSOE: UCD en 1977 y 1979, el CDS de Suárez en 1986 y AP o PP en todas las demás. Segovia votó al PSOE una sola vez, en abril de 2019.</p>
{F.prov('Quién ganó en cada provincia', 'Lista más votada en las generales de 1977 a 2023.')}
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios con más electores.')}
<p>Las ciudades se parecen más entre sí. Valladolid, la mayor, votó al PSOE en 1982, 1986 y las dos de 2019, y al PP en todas las demás desde 1989. Burgos y Ávila ya votaron a AP en 1982, cuando el PSOE arrasaba en España. En 2023 el PP ganó en ocho de las diez ciudades más grandes; el PSOE, en Ponferrada y en Soria.</p>
<p>El mapa municipal enseña cómo se ha repartido el voto entre los pueblos. En 1977 casi todo es del color de UCD. En 1982 el mapa se reparte: AP ganó en 1.052 municipios, el PSOE en 819, UCD aún en 246 y el CDS en 79, casi todos en el sur de la provincia de Ávila. Desde 1993 el PP gana en la gran mayoría: en 2011 fue el más votado en 2.157 de los 2.248 municipios. Ni siquiera cuando el PSOE ganó en la comunidad, en abril de 2019, lo hizo en número de pueblos: el PP fue primero en 1.464 y el PSOE en 691, con su mancha más grande en el norte de la provincia de León. En 2023, el PP ganó en 1.916 municipios, el PSOE en 308 y Vox en 14.</p>
{F.mapa('Castilla y León, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Solo 9 de los 2.209 municipios con datos en las 16 generales han votado siempre al mismo partido. Siete lo han hecho al PSOE, cinco de ellos en la provincia de León: Fabero, el mayor, La Pola de Gordón, Sabero, Vega de Valcarce y La Ercina. Los otros dos, Cerecinos del Carrizal (Zamora) y Villacidaler (Palencia), han votado siempre a AP y al PP.</p>

<h2>Votar más que la media</h2>
<p>Castilla y León vota más que el conjunto de España en las generales: sin contar el voto exterior, su participación ha superado la media en las 16 elecciones. En 2023 fue del 74,4%, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Castilla y León y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Castilla y León elige 31 diputados, los mismos que en 2023, según el <a href="{BOE26}">decreto de convocatoria</a>: 5 por Valladolid; 4 por Burgos, León y Salamanca; 3 por Ávila, Palencia, Segovia y Zamora, y 2 por Soria. En 2023 fueron 18 para el PP, 12 para el PSOE y 1 para Vox, <a href="{GEN23}">según el escrutinio</a>. El 29 de noviembre dirá si el PP repite como primera fuerza en las nueve provincias, si León vuelve a votar al ganador de España y cuánto suma Vox seis meses después de volver a la Junta.</p>
"""


PIEZA = dict(
    cc='castilla-y-leon', slug='castilla-y-leon-historia-electoral', lugar='Castilla y León', corto='Castilla y León en las urnas',
    titulo='El PP gobierna Castilla y León desde 1987 y ha ganado allí 11 de las 16 generales; el PSOE ganó las autonómicas de 2019 y no gobernó',
    dek='Seis mayorías absolutas seguidas, de 1991 a 2011, y desde 2022 gobiernos con Vox: Mañueco fue investido por tercera vez en junio de 2026. '
        'En las generales, el PP saca aquí más que en el conjunto de España en todas las elecciones.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PP gobierna Castilla y León desde 1987. El PSOE ganó las autonómicas de 2019 y no gobernó; Mañueco ha gobernado con Ciudadanos y después con Vox. En las generales, el PP ganó allí 11 de 16.',
    compara='Las 12 elecciones a las Cortes de Castilla y León (1983-2026) y las 16 generales (1977-2023) en Castilla y León, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('acleon', 'Castilla y León'),
                               (IDP19, 'Juan María Bilbao Ubillos, «Castilla y León», Informe Comunidades Autónomas 2019, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP22, 'Juan María Bilbao Ubillos, «Castilla y León», Informe Comunidades Autónomas 2022, IDP Barcelona'),
                               (MANUECO22, 'Público, «Mañueco: "Voy a dialogar con todos para formar un Gobierno de todos y para todos"» (13-2-2022)'),
                               (INVEST22, 'The Objective, «Alfonso Fernández Mañueco, investido presidente de Castilla y León con el apoyo de Vox» (11-4-2022)'),
                               (INVEST26, 'El Español, investidura de Mañueco con los votos de PP y Vox (9-6-2026)'),
                               (GEN23, 'Última Hora, escrutinio de las generales de 2023 en Castilla y León'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones (6-10-2026)'),
                               (W87, 'Wikipedia, Elecciones a las Cortes de Castilla y León de 1987'),
                               (W26, 'Wikipedia, Elecciones a las Cortes de Castilla y León de 2026'),
                               (LUCAS, 'Wikipedia, Juan José Lucas')],
    enlaces=[],
)
