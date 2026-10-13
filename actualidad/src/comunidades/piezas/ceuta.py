"""Ceuta: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

RESI = 'https://seguridadinternacional.es/resi/html/representacion-politica-e-identidad-local-en-ceuta-1975-2023/'
VIVAS19 = 'https://www.moncloa.com/2019/05/24/pp-ceuta-vox-convivencia-26737/'
ARA = 'https://en.ara.cat/politics/the-president-of-ceuta-who-does-not-get-along-with-vox-and-stopped-the-expansion-of-jesus-gil_1_5830064.html'
W95 = wiki('Elecciones a la Asamblea de Ceuta de 1995')
SAMPIETRO = wiki('Antonio Sampietro')
PRESI = wiki('Presidente de Ceuta')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">En noviembre de 2019, Vox fue la lista más votada en unas elecciones generales en dos circunscripciones de toda España: la Región de Murcia y Ceuta. En Ceuta sacó el 35,6% de los votos, cuatro puntos más que el PSOE, que solo seis meses antes había ganado allí por primera vez desde 1989. En 2023 volvió a ganar el PP, como había hecho en todas las generales de 1993 a 2016.</p>
<p>En su propia Asamblea, Ceuta ha tenido una historia más agitada que casi ninguna comunidad: cuatro presidentes en sus primeros seis años como ciudad autónoma, dos mociones de censura y un gobierno del partido de Jesús Gil. Desde febrero de 2001 preside la ciudad el mismo hombre, el popular Juan Jesús Vivas.</p>
<p>Este reportaje recorre esa historia con los resultados de las elecciones locales desde 1979 y de las dieciséis generales desde 1977. Ceuta es un único municipio, así que aquí no hay mapa por municipios.</p>

<h2>De ayuntamiento a ciudad autónoma</h2>
<p>Hasta 1995, Ceuta elegía un ayuntamiento como cualquier otro municipio. Ese año aprobó su Estatuto de Autonomía, y desde entonces sus 25 concejales forman también la Asamblea de la ciudad autónoma, que elige al presidente (alcalde-presidente). El gráfico junta las dos etapas: las municipales de 1979 a 1991 y las de la Asamblea desde 1995.</p>
{F.aut('Concejales y diputados de Ceuta, 1979-2023', 'Escaños de cada partido en el pleno de 25: ayuntamiento hasta 1991 y Asamblea desde 1995.')}
<p>En las primeras municipales, en 1979, ganó una agrupación local, la Agrupación Electoral Ceutí por un Ayuntamiento Democrático, con 12 de los 25 concejales. En 1983 llegó el PSOE, con 12. En 1991 la lista más votada fue otro partido local, Progreso y Futuro de Ceuta (PFC), con 11.</p>
<p>La investigadora Alicia Fernández, de la Universidad de París 8, que ha estudiado la política ceutí entre 1975 y 2023, describe una constante en esas décadas:</p>
{F.cita('la volatilidad electoral de sus votantes y la vitalidad de la oferta política local han fragmentado el sistema de partidos', 'Alicia Fernández', 'Universidad de París 8, en la Revista de Estudios en Seguridad Internacional', RESI, 'RESI, vol. 11, n.º 1', '2025')}

<h2>Cuatro presidentes en seis años</h2>
<p>En las primeras elecciones a la Asamblea, en mayo de 1995, el PP fue el más votado, con 9 escaños, pero el primer presidente fue Basilio Fernández, del PFC, con el apoyo de Ceuta Unida y el PSOE. En julio de 1996 el PFC cambió de socio y la presidencia pasó al popular Jesús Fortes, según la <a href="{W95}">crónica de aquellas elecciones</a>.</p>
<p>En 1999 ganó el Grupo Independiente Liberal (GIL), el partido del entonces alcalde de Marbella, Jesús Gil, con el 38% de los votos y 12 de los 25 escaños. Un pacto de PP, PSOE y PDSC mantuvo primero a Fortes, pero en agosto prosperó una moción de censura con el voto de una diputada que había salido del PSOE, y el candidato del GIL, Antonio Sampietro, llegó a la presidencia. En febrero de 2001 otra moción, esta vez con una tránsfuga del propio GIL, le sacó del cargo y lo dio al popular Juan Jesús Vivas, según recoge <a href="{SAMPIETRO}">Wikipedia</a>. Para Alicia Fernández, fue la única vez que un partido local mandó en la ciudad:</p>
{F.cita('solo llegaron al poder en 1999 cuando el GIL, un partido regionalista y populista, gobernó Ceuta entre 1999 y 2001', 'Alicia Fernández', 'Universidad de París 8', RESI, 'RESI, vol. 11, n.º 1', '2025')}
{presidentes([('1995', '1996', 'Basilio Fernández', 'PFC'), ('1996', '1999', 'Jesús Fortes', 'PP'), ('1999', '2001', 'Antonio Sampietro', 'GIL'),
              ('2001', 'hoy', 'Juan Jesús Vivas', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Ciudad Autónoma de Ceuta desde el Estatuto de 1995. Fuente: <a href="{PRESI}">Wikipedia</a>.</p>

<h2>Vivas, 25 años</h2>
<p>Con Vivas llegaron las mayorías absolutas: 19 escaños en 2003 y en 2007, 18 en 2011 y 13 en 2015, con más del 62% de los votos en las tres primeras. Fernández apunta como una de las causas el conflicto de la isla de Perejil con Marruecos, en 2002, y la respuesta del Gobierno de Aznar, que según ella dio origen a un «efecto Perejil» que «explica, en cierto modo, la hegemonía de la que aún disfruta el PP en Ceuta». Es su interpretación; los datos solo muestran el salto del PP del 28% en 1999 al 63% en 2003.</p>
<p>Al mismo tiempo crecían los partidos encabezados por ceutíes musulmanes, que se convirtieron en la oposición: la UDCe en 2003 y 2007, Caballas desde 2011, el Movimiento por la Dignidad y la Ciudadanía (MDyC) desde 2015 y Ceuta Ya!, heredero de Caballas, en 2023. En el gráfico, Ceuta Ya! va en la misma fila que Caballas.</p>
<p>En 2019 el PP bajó a 9 escaños, y Vox entró con 6. Vivas se negó a pactar con Vox. En la campaña había anunciado que solo optaría a la presidencia si su lista era la más votada:</p>
{F.cita('El PP solo optará a la Presidencia de la Ciudad si es la lista más votada', 'Juan Jesús Vivas', 'presidente de Ceuta y candidato del PP', VIVAS19, 'Europa Press, en Moncloa.com', '24 de mayo de 2019')}
<p>Rechazó cualquier pacto con Vox «no por razones ideológicas», sino porque, a su juicio, sus discursos «atentan contra la convivencia» entre las culturas de la ciudad. En 2023 repitió con 9 escaños, frente a 6 del PSOE, 5 de Vox, 3 del MDyC y 2 de Ceuta Ya!, y sigue presidiendo la ciudad con 9 de los 25 escaños. En febrero de 2026 cumplió 25 años en el cargo.</p>

<h2>En las generales: casi siempre con el que gana en España</h2>
<p>Ceuta elige un solo diputado al Congreso. En las generales ganó UCD en 1977 y 1979, el PSOE de 1982 a 1989 y el PP de 1993 a 2016, incluido 1993, cuando en España todavía ganaba Felipe González. En 2000, el GIL quedó segundo con el 29,4% de los votos, por delante del PSOE.</p>
{F.gen('UCD, PSOE, PP, Vox y los demás en Ceuta', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
{F.esp('PSOE y PP en Ceuta y en España', 'PSOE y AP/PP en Ceuta y en el conjunto de España, en las generales.')}
<p>El PP llegó al 67% en 2011. En abril de 2019 el PSOE ganó con el 36,6%, y en noviembre fue el turno de Vox. En 2023 el PP recuperó el primer puesto con el 39,2%, por delante del PSOE (34,3%) y de Vox (23,5%).</p>
{F.prov('Quién ganó en Ceuta', 'Lista más votada en las generales de 1977 a 2023.')}

<h2>Votar mucho menos que la media</h2>
<p>Ceuta es uno de los territorios que menos vota. Sin contar el voto exterior, su participación quedó por debajo de la de España en las 16 generales, y desde 1986 la diferencia ha sido siempre de más de diez puntos. En 2023 votó el 55,7% del censo, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Ceuta y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>El 29 de noviembre Ceuta vuelve a elegir un diputado, y se lo lleva la lista más votada. El PP lo ganó en 2023 con casi cinco puntos de ventaja sobre el PSOE. Habrá que ver si Vox repite su resultado de 2019 o el de 2023, y si sube una participación que lleva décadas muy por debajo de la media.</p>
"""


PIEZA = dict(
    cc='ceuta', slug='ceuta-historia-electoral', lugar='Ceuta', corto='Ceuta en las urnas',
    titulo='Ceuta es uno de los dos sitios donde Vox ha ganado unas generales; en su Asamblea, Vivas gobierna desde 2001 tras dos mociones de censura',
    dek='Cuatro presidentes en seis años, un gobierno del GIL de Jesús Gil y, desde 2001, Juan Jesús Vivas. En las generales, Ceuta pasó del PSOE en abril de 2019 a Vox en noviembre y al PP en 2023.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='Vox ganó las generales de noviembre de 2019 en Ceuta y en Murcia. En la Asamblea de Ceuta hubo cuatro presidentes en seis años y dos mociones de censura; Juan Jesús Vivas (PP) gobierna desde 2001.',
    compara='Las 12 elecciones locales y a la Asamblea de Ceuta (1979-2023) y las 16 generales (1977-2023) en Ceuta.',
    limites=LIMITES + ' Ceuta es un solo municipio: no hay mapa. Las elecciones de 1979 a 1991 fueron municipales; desde 1995, a la Asamblea de la ciudad autónoma.',
    fuentes=FUENTES_COMUNES + [he_fuente('aceuta', 'Ceuta'),
                               (RESI, 'Alicia Fernández, «Representación política e identidad local en Ceuta (1975-2023)», Revista de Estudios en Seguridad Internacional, vol. 11, n.º 1 (2025), pp. 33-61'),
                               (VIVAS19, 'Europa Press (en Moncloa.com), «El PP de Ceuta no pactará con Vox» (24-5-2019)'),
                               (ARA, 'Ara, perfil de Juan Jesús Vivas y la moción de censura de 2001'),
                               (W95, 'Wikipedia, Elecciones a la Asamblea de Ceuta de 1995'),
                               (SAMPIETRO, 'Wikipedia, Antonio Sampietro'),
                               (PRESI, 'Wikipedia, Presidente de Ceuta')],
    enlaces=[],
)
