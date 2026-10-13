"""Cataluña: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP03 = 'https://www.idpbarcelona.net/docs/public/iccaa/2003/cataluna_2003.pdf'
IDP17 = 'https://www.idpbarcelona.net/docs/public/iccaa/2017/cataluna_2017.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/cataluna_2023.pdf'
ILLA = 'https://lamarea.com/2024/08/09/salvador-illa-es-investido-presidente-entre-los-fuegos-artificiales-de-puigdemont'
W21 = wiki('Elecciones al Parlamento de Cataluña de 2021')
W24 = wiki('Elecciones al Parlamento de Cataluña de 2024')
ABST = '../../abstencion.html'
PUIG = '../puigdemont-junts-congreso-parlament/'
RUFIAN = '../rufian-erc-comuns/'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Cataluña vota de dos maneras distintas. En las elecciones generales, el PSC ha sido la lista más votada de la comunidad en 11 de las 16 convocatorias desde 1977. En las elecciones al Parlament, en cambio, Convergència i Unió (CiU) gobernó la Generalitat 23 años seguidos con Jordi Pujol, de 1980 a 2003, y los socialistas solo la han presidido en dos etapas: la de Pasqual Maragall y José Montilla, de 2003 a 2010, y la de Salvador Illa, desde agosto de 2024.</p>
<p>Las dos maneras de votar también se ven en el mapa. El PSC gana en el área de Barcelona, donde vive la mayoría de los electores; CiU, y después Junts y ERC, han ganado casi siempre en más municipios. Y desde 2015 el orden de las generales también ha cambiado: en 2015 y 2016 ganó En Comú Podem, y en las dos de 2019, ERC.</p>
<p>Este reportaje recorre esa historia con los resultados de las catorce elecciones al Parlament, de 1980 a 2024, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Veintitrés años de Pujol</h2>
<p>La Generalitat se restableció el 29 de septiembre de 1977, con Josep Tarradellas como presidente, y el primer Parlament se votó en marzo de 1980. Ganó CiU, con el 27,6% de los votos y 43 de los 135 escaños, por delante de los socialistas (33) y del PSUC (25). Jordi Pujol fue investido en la segunda votación con los votos de su grupo, los de Centristes de Catalunya-UCD y los de ERC, según los registros de Historia Electoral.</p>
{F.aut('Escaños en el Parlament de Catalunya, 1980-2024', 'Diputados de cada partido en las catorce elecciones autonómicas.')}
<p>En 1984 llegó la primera mayoría absoluta: 72 escaños, con el 46,8% de los votos. CiU repitió mayoría en 1988 (69) y en 1992 (70), y no ha vuelto a haber otra: ningún partido ha llegado desde entonces a los 68 escaños que hacen falta. En 1995 Pujol gobernó en minoría, y en 1999 con el apoyo del PP.</p>
<p>Las elecciones de 1999 y de 2003 tuvieron algo en común: el PSC sacó más votos que CiU, pero menos escaños. En 2003 fue el 31,2% de los socialistas frente al 30,9% de CiU, y 42 escaños frente a 46. Aquella vez, sin embargo, el resultado sí cambió el Gobierno. Pujol ya no era candidato, y el socialista Pasqual Maragall fue investido con los votos del PSC, ERC e Iniciativa per Catalunya-Verds. El constitucionalista Joan Vintró, de la Universitat de Barcelona, lo resumió así:</p>
{F.cita('los resultados electorales del 16 de noviembre que han permitido, por primera vez desde la vigencia del Estatuto de Autonomía de 1979, un cambio de mayoría parlamentaria y la formación de un Gobierno de coalición de izquierdas (PSC-ERC-IC) presidido por el socialista P. Maragall', 'Joan Vintró', 'Universitat de Barcelona, en el Informe Comunidades Autónomas 2003 del Instituto de Derecho Público', IDP03, 'IDP Barcelona', '2004')}
<p>El tripartito repitió en 2006, ya con José Montilla de presidente, aunque CiU había vuelto a ser la lista más votada. En 2010 CiU recuperó la Generalitat con Artur Mas y 62 escaños, y gobernó en minoría.</p>
{presidentes([('1977', '1980', 'Josep Tarradellas', 'ERC'), ('1980', '2003', 'Jordi Pujol', 'CiU'), ('2003', '2006', 'Pasqual Maragall', 'PSC'),
              ('2006', '2010', 'José Montilla', 'PSC'), ('2010', '2016', 'Artur Mas', 'CiU'), ('2016', '2017', 'Carles Puigdemont', 'Junts pel Sí'),
              ('2018', '2020', 'Quim Torra', 'Independiente, en Junts per Catalunya'), ('2021', '2024', 'Pere Aragonès', 'ERC'), ('2024', 'hoy', 'Salvador Illa', 'PSC')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Generalitat desde su restablecimiento en 1977. Tarradellas, presidente en el exilio, encabezó la Generalitat provisional hasta las elecciones de 1980. De octubre de 2017 a mayo de 2018 el cargo quedó vacante por la aplicación del artículo 155 de la Constitución, y de septiembre de 2020 a mayo de 2021, tras la inhabilitación de Torra, Aragonès lo ejerció en funciones. Fuente: <a href="https://www.historiaelectoral.com/acatalunya.html">Historia Electoral</a>.</p>

<h2>El procés: ganar en votos y no gobernar</h2>
<p>En 2015, CDC y ERC se presentaron juntos en Junts pel Sí, que sacó 62 escaños. Artur Mas no logró ser investido, porque la CUP votó en contra, y en enero de 2016 fue elegido Carles Puigdemont con los votos de Junts pel Sí y de ocho de los diez diputados de la CUP. En octubre de 2017, después del referéndum del 1 de octubre, el Parlament aprobó la declaración de independencia y el Senado autorizó la aplicación del artículo 155 de la Constitución, que cesó al Gobierno catalán y convocó elecciones para el 21 de diciembre.</p>
<p>En ellas, Ciudadanos fue el partido más votado, con el 25,4% y 36 escaños, pero no tenía con quién sumar. El catedrático Joaquín Tornos Mas, de la Universitat de Barcelona, describió así el resultado:</p>
{F.cita('los resultados dieron un 47% de los votos a los partidos soberanistas, no obstante lo cual logran mantener la mayoría parlamentaria con los 70 escaños de Junts per Catalunya, ERC y la CUP', 'Joaquín Tornos Mas', 'Universitat de Barcelona, en el Informe Comunidades Autónomas 2017 del Instituto de Derecho Público', IDP17, 'IDP Barcelona', '2018')}
<p>Quim Torra fue investido en mayo de 2018. En 2021 se repitió la escena con otros protagonistas: el PSC de Salvador Illa fue el más votado, con el 23,0%, y empató a 33 escaños con ERC, pero el investido, el 21 de mayo y tras dos votaciones fallidas en marzo, fue Pere Aragonès, de ERC, según la <a href="{W21}">crónica de aquellas elecciones</a>. Así, en 4 de las 14 elecciones al Parlament (1999, 2006, 2017 y 2021) el partido con más votos no llegó a la presidencia.</p>

<h2>2024: el PSC vuelve a la Generalitat</h2>
<p>Junts salió del Gobierno de Aragonès en octubre de 2022. En marzo de 2024 el Parlament rechazó sus presupuestos y Aragonès adelantó las elecciones al 12 de mayo, según recoge <a href="{W24}">Wikipedia</a>. El PSC ganó con 42 escaños y el 28,0% de los votos; Junts, con Puigdemont de candidato, sacó 35; ERC bajó de 33 a 20. Los partidos independentistas, que sumaban 74 escaños en 2021, se quedaron en 61. El 8 de agosto Illa fue investido con 68 votos, los del PSC, ERC y los Comuns. En su discurso se presentó como el continuador de otras dos etapas:</p>
{F.cita('Después de la primera gran transformación de Cataluña, iniciada por el presidente Tarradellas, y de la segunda transformación que emprendieron Maragall y Montilla, ahora es la hora de la tercera gran transformación de Cataluña', 'Salvador Illa', 'candidato del PSC, en el debate de su investidura como president', ILLA, 'La Marea', '9 de agosto de 2024')}
<p>El Parlament de 2024 también es el de una participación baja. Votó el 57,9% del censo, según Historia Electoral, muy lejos del 79,0% de 2017, el máximo de la serie, y por encima del 51,3% de 2021, el mínimo. Quién deja de votar y dónde lo contamos, sección a sección, en <a href="{ABST}">¿Quién no vota en Cataluña?</a></p>

<h2>En las generales: el PSC por delante</h2>
<p>En el Congreso, la historia es otra. El PSC fue la lista más votada en Cataluña en todas las generales de 1977 a 2008 y otra vez en 2023: 11 de 16. Su mejor resultado fue el de 2008, con el 46,1%. En los gráficos, el PSC va con el PSOE, con el que se presenta, y CiU y Junts van juntos en la misma línea.</p>
{F.gen('PSC, CiU y Junts, ERC y los demás en Cataluña', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>CiU solo fue la más votada una vez, en 2011, con el 29,9%. Su máximo en unas generales fue el 32,9% de 1989, muy por debajo del 46% que llegó a sacar en el Parlament. En 2015 y 2016 ganó En Comú Podem, la candidatura de los comuns con Podemos, y en las dos elecciones de 2019, ERC, con el 24,7% en abril. En 2023 el PSC recuperó el primer puesto con el 34,8%, y ERC (13,3%) y Junts (11,3%) quedaron por detrás de Sumar (14,2%) y del PP (13,4%).</p>
{F.esp('PSC y PP en Cataluña, PSOE y PP en España', 'PSOE (en Cataluña, el PSC) y AP/PP en Cataluña y en el conjunto de España, en las generales.')}
<p>Por eso Cataluña ha coincidido pocas veces con el ganador de España: solo en 6 de las 16 generales (las cuatro de 1982 a 1993, y 2004 y 2008). El PP nunca ha pasado aquí del tercer puesto. Su techo fue el 23,1% de 2000, y en abril de 2019 bajó al 4,9%.</p>
{F.prov('Quién ganó en cada provincia catalana', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Por provincias, Barcelona votó al PSC en 14 de las 16 generales; solo le falló en 2015 y 2016, con En Comú Podem. Girona y Lleida fueron de CiU en casi todas las de los ochenta y los noventa, y de ERC de 2016 a noviembre de 2019. Tarragona fue de los socialistas de 1979 a 2008. El PSC ha ganado en las cuatro provincias en tres elecciones: 2004, 2008 y 2023.</p>
<p>Entre las diez ciudades con más electores, L'Hospitalet de Llobregat, Badalona y Santa Coloma de Gramenet han votado al PSC en todas las generales menos en las de 2015 y 2016. La ciudad de Barcelona ha sido más cambiante: votó a CiU en 1989, 1993 y 2011, a En Comú Podem en 2015 y 2016 y a ERC en las dos de 2019. En 2023 el PSC fue el más votado en las diez.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios catalanes con más electores.')}
<p>El mapa municipal enseña el reverso de esas victorias. Aunque el PSC ganaba en Cataluña, CiU fue la lista que ganó en más municipios de los 947 de Cataluña en todas las generales hasta 2011 menos dos, las de 1979 y 2008, y llegó a ganar en 798 en 1989 y en 827 en 2011. En 1977 el Pacte Democràtic per Catalunya, el antecedente de CiU, ganó en 384, UCD en 260, sobre todo en el oeste de Lleida y en el sur de Tarragona, y los socialistas en 182, la mayoría en la costa y en el área de Barcelona; la lista de Unió fue la más votada en una treintena. En 1979 UCD ganó en 430. Antes de 2023, el PSC solo superó a CiU en número de municipios una vez, en 2008: 515 frente a 414. En abril de 2019 el mapa se volvió casi entero amarillo, con ERC primera en 747 municipios. Y en 2023 el PSC ganó en 471, casi toda la costa, el sur de Tarragona y el oeste de Lleida; Junts, en 297, sobre todo en el interior, y ERC en 162.</p>
{F.mapa('Cataluña, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}

<h2>Votar menos que la media</h2>
<p>Cataluña vota menos que el conjunto de España en las generales. Sin contar el voto exterior, su participación quedó por debajo de la media en 12 de las 16 elecciones; las excepciones fueron 1977, 1982 y las dos de 2019. La mayor distancia se dio en 2000 y en 2023, de unos cinco puntos: en 2023 votó el 65,4% del censo, frente al 70,4% de España.</p>
{F.part('Participación en las generales: Cataluña y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Cataluña elige 48 de los 350 diputados: 32 por Barcelona, 6 por Girona, 6 por Tarragona y 4 por Lleida. En 2023 fueron 19 para el PSC, 7 para Sumar, ERC y Junts, 6 para el PP y 2 para Vox. Después de aquellas elecciones, ERC y Junts, con siete diputados cada uno, fueron decisivos en la investidura de Pedro Sánchez. Tornos Mas lo escribió así en su informe de aquel año:</p>
{F.cita('Los partidos nacionalistas vascos y catalanes se convierten de este modo en la llave del Gobierno del Sr. Pedro Sánchez', 'Joaquín Tornos Mas', 'Universitat de Barcelona, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>El 29 de noviembre se verá si el PSC repite como la lista más votada, como en todas las generales menos cinco, y cuánto recuperan Junts y ERC respecto a 2023. Las dos cosas las hemos medido en otras piezas: <a href="{PUIG}">cómo cambia el voto de Junts con Puigdemont de candidato</a> y <a href="{RUFIAN}">qué pasaría si ERC y los comuns sumaran</a>.</p>
"""


PIEZA = dict(
    cc='cataluna', slug='cataluna-historia-electoral', lugar='Cataluña', corto='Cataluña en las urnas',
    titulo='El PSC ha sido el más votado en Cataluña en 11 de las 16 generales; la Generalitat la presidió CiU 23 años seguidos',
    dek='En el Congreso, Cataluña vota sobre todo a los socialistas; en el Parlament, CiU fue la más votada en ocho de las diez elecciones hasta 2012, y en cuatro elecciones el partido con más votos no llegó a gobernar. '
        'En el mapa municipal, CiU, Junts y ERC han ganado casi siempre en más pueblos que el PSC.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSC fue la lista más votada en Cataluña en 11 de las 16 generales, pero CiU gobernó la Generalitat de 1980 a 2003. En cuatro elecciones al Parlament, el partido con más votos no gobernó. Illa preside desde 2024.',
    compara='Las 14 elecciones al Parlament de Catalunya (1980-2024) y las 16 generales (1977-2023) en Cataluña, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('acatalunya', 'Cataluña'),
                               (IDP03, 'Joan Vintró, «Cataluña», Informe Comunidades Autónomas 2003, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP17, 'Joaquín Tornos Mas, «Cataluña», Informe Comunidades Autónomas 2017, IDP Barcelona'),
                               (IDP23, 'Joaquín Tornos Mas, «Cataluña», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (ILLA, 'La Marea, «Salvador Illa es investido presidente entre los fuegos artificiales de Puigdemont» (9-8-2024)'),
                               (W21, 'Wikipedia, Elecciones al Parlamento de Cataluña de 2021'),
                               (W24, 'Wikipedia, Elecciones al Parlamento de Cataluña de 2024')],
    enlaces=[],
)
