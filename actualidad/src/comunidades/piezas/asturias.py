"""Asturias: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP11 = 'https://www.idpbarcelona.net/docs/public/iccaa/2011/asturias_2011.pdf'
IDP12 = 'https://www.idpbarcelona.net/docs/public/iccaa/2012/asturias_2012.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/asturias_2023.pdf'
CASCOS = 'https://www.publico.es/actualidad/cascos-convoca-elecciones-asturias-seis-meses-gobierno.html'
W95 = wiki('Elecciones a la Junta General del Principado de Asturias de 1995')
W11 = wiki('Elecciones a la Junta General del Principado de Asturias de 2011')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Asturias ha elegido doce veces su parlamento, la Junta General del Principado, y en diez de ellas el presidente salió del PSOE. Los socialistas fueron los más votados en todas las autonómicas menos una, la de 1995. Las dos excepciones a su gobierno duraron poco y acabaron en crisis: el popular Sergio Marqués terminó la legislatura de 1995 fuera de su partido, y Francisco Álvarez-Cascos, que había ganado en escaños con un partido fundado unos meses antes, disolvió la cámara a los seis meses de llegar al cargo.</p>
<p>En las generales, en cambio, Asturias es mucho menos fiel. El PP ganó allí en 1996, en 2000, en 2004, cuando España votó a Zapatero, de 2011 a 2016 y otra vez en 2023. Y en 2015 Podemos sacó el 21,5%, a dos puntos del PSOE.</p>
<p>Este reportaje recorre esa historia con los resultados de las doce elecciones autonómicas, de 1983 a 2023, y de las dieciséis generales desde 1977, concejo a concejo.</p>

<h2>Diez de doce para el PSOE</h2>
<p>El Estatuto de Autonomía de Asturias se aprobó el 30 de diciembre de 1981, y la primera Junta General se votó en mayo de 1983. El PSOE sacó el 52% de los votos y 26 de los 45 escaños; Pedro de Silva fue investido con los votos de su grupo. Solo hubo otra mayoría absoluta en estos cuarenta años, la de Vicente Álvarez Areces en 1999, con 24 diputados.</p>
{F.aut('Escaños en la Junta General del Principado, 1983-2023', 'Diputados de cada partido en las doce elecciones autonómicas.')}
<p>El resto del tiempo, los socialistas gobernaron en minoría o con Izquierda Unida. En 1987, con 20 escaños, De Silva fue investido en segunda votación con solo los votos del PSOE: AP, el CDS y la coalición de IU se abstuvieron, según los registros de Historia Electoral. Hoy, además, el reglamento de la Junta General no permite votar en contra de un candidato: solo a favor o abstenerse, como recuerda Paloma Requejo en el <a href="{IDP23}">Informe Comunidades Autónomas 2023</a>.</p>
<p>Juan Luis Rodríguez Vigil, presidente desde 1991, dimitió en 1993 por el escándalo del «petromocho», según recoge <a href="{W95}">Wikipedia</a>, y Antonio Trevín terminó la legislatura. Areces gobernó doce años, de 1999 a 2011, y en su último mandato metió a Izquierda Unida en el Gobierno. Javier Fernández (2012-2019) y Adrián Barbón, presidente desde 2019, completaron la lista socialista.</p>
{presidentes([('1982', '1983', 'Rafael Fernández', 'PSOE'), ('1983', '1991', 'Pedro de Silva', 'PSOE'), ('1991', '1993', 'Juan Luis Rodríguez Vigil', 'PSOE'),
              ('1993', '1995', 'Antonio Trevín', 'PSOE'), ('1995', '1999', 'Sergio Marqués', 'PP, luego URAS'), ('1999', '2011', 'Vicente Álvarez Areces', 'PSOE'),
              ('2011', '2012', 'Francisco Álvarez-Cascos', 'Foro'), ('2012', '2019', 'Javier Fernández', 'PSOE'), ('2019', 'hoy', 'Adrián Barbón', 'PSOE')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes del Consejo de Gobierno del Principado desde el Estatuto de 1981. Rafael Fernández ya presidía el ente preautonómico desde 1978. Fuente: <a href="https://www.historiaelectoral.com/aasturias.html">Historia Electoral</a>.</p>

<h2>Las dos excepciones</h2>
<p>La primera llegó en 1995. El PP de Sergio Marqués sacó el 42% y 21 escaños, y fue el único año en que el PSOE no fue el más votado en unas autonómicas asturianas. La legislatura acabó rota: en noviembre de 1998 Marqués y otros cuatro diputados abandonaron el grupo popular y fundaron Unión Renovadora Asturiana (URAS). Marqués gobernó en minoría hasta el final y superó una moción de censura presentada por su antiguo partido, según la <a href="{W95}">crónica de aquellas elecciones</a>. En 1999, URAS sacó el 7% y tres escaños, y el PSOE volvió con mayoría absoluta.</p>
<p>La segunda fue todavía más corta. Francisco Álvarez-Cascos, exsecretario general del PP y exministro de Aznar, dejó el partido a finales de 2010 y fundó Foro Asturias. En mayo de 2011, Foro obtuvo 16 escaños con el 29,7% de los votos; el PSOE sacó algo más de votos, el 29,9%, pero un escaño menos. El jurista Leopoldo Tolivar Alas, de la Universidad de Oviedo, señalaba una coincidencia en aquel resultado:</p>
{F.cita('Curiosamente, Foro Asturias obtuvo 16 representantes; la suma exacta de los dejados por el camino por las dos grandes fuerzas estatales', 'Leopoldo Tolivar Alas', 'Universidad de Oviedo, en el Informe Comunidades Autónomas 2011 del Instituto de Derecho Público', IDP11, 'IDP Barcelona', '2012')}
<p>El PP había perdido 10 diputados y el PSOE, 6. Cascos fue investido el 15 de julio solo con los votos de su grupo, mientras el resto se abstenía, según la <a href="{W11}">crónica de la investidura</a>. Sin acuerdo con nadie, no consiguió aprobar los presupuestos de 2012 y a finales de enero disolvió la cámara. Culpó a PP y PSOE de una alianza para impedirle gobernar:</p>
{F.cita('no he venido aquí para volver, a la fuerza, al mismo sitio ni para ser cómplice pasivo de una trama para la que Asturias es su cortijo', 'Francisco Álvarez-Cascos', 'presidente del Principado, al anunciar las elecciones anticipadas', CASCOS, 'Público', '30 de enero de 2012')}
<p>En las elecciones de marzo de 2012, el PSOE volvió a ser primero. El último escaño se decidió con el voto del extranjero: según la constitucionalista Paloma Requejo, de la Universidad de Oviedo, en el recuento inicial el PSOE tenía 16 escaños y Foro 13, y con los votos de los residentes ausentes un escaño de la circunscripción occidental pasó de Foro al PSOE. «Los verdaderos protagonistas fueron los votos desde el extranjero», escribió en su <a href="{IDP12}">informe de aquel año</a>. Foro lo recurrió y el Tribunal Constitucional acabó confirmando el reparto. Javier Fernández fue investido por mayoría absoluta.</p>

<h2>2023: el PSOE gana, pero necesita a otros</h2>
<p>Desde entonces el PSOE no ha dejado de gobernar. En 2015 la Junta se llenó de partidos nuevos, con Podemos en 9 escaños y Ciudadanos en 3. En 2023, Barbón ganó con 19 diputados, el PP subió de 10 a 17 y Vox, de 2 a 4. Requejo resumió así aquellas elecciones:</p>
{F.cita('triunfo del PSOE, aunque necesitando a otras fuerzas para asegurar la estabilidad del futuro Gobierno, fuerte avance de la derecha con gran subida de los Populares y desplome de Cs y de Podemos', 'Paloma Requejo Rodríguez', 'Universidad de Oviedo, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>Barbón fue investido en primera votación con 23 votos, los de los socialistas, los tres de Convocatoria por Asturias (IU, Más País e IAS) y la diputada de Podemos. Después firmó un gobierno de coalición con Convocatoria, la fórmula que ya había probado Areces. Las próximas autonómicas tocan en mayo de 2027.</p>

<h2>En las generales: un país más disputado</h2>
<p>En las generales, el mapa asturiano cambia más. En 1977 y 1979 el PSOE ganó en Asturias cuando en España ganaba UCD, con el voto de la zona central, minera e industrial, como se ve en el mapa de más abajo. Desde los noventa, la comunidad se ha movido más o menos con el país, con una excepción: en 2004 el PP fue el más votado en Asturias por siete décimas (44,8% frente a 44,1%) mientras Zapatero ganaba en España.</p>
{F.gen('PSOE, PP y los demás en Asturias', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>La izquierda a la izquierda del PSOE siempre ha sido fuerte aquí. El PCE sacó el 13,8% en 1979, IU pasó del 15% en las generales de 1989 a 1996, y en diciembre de 2015 Podemos sacó el 21,5% e IU, el 8,5%; en el gráfico, la línea de PCE / IU / Podemos / Sumar suma las dos listas. Ese año Podemos fue la lista más votada en Mieres y en Carreño.</p>
{F.esp('PSOE y PP en Asturias y en España', 'PSOE y AP/PP en Asturias y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en Asturias', 'Lista más votada en las generales de 1977 a 2023 en la provincia.')}
<p>Las ciudades no votan igual. Oviedo, la capital, se pasó al PP en 1989 y desde entonces solo ha votado al PSOE en las dos generales de 2019. Gijón, con más electores, ha votado al PSOE en la mayoría de elecciones. En las cuencas mineras, Langreo, Mieres y San Martín del Rey Aurelio, solo ha ganado otra lista que no fuera el PSOE de forma puntual, sobre todo Podemos en Mieres en 2015 y Unidos Podemos en Langreo y Mieres en 2016.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez concejos asturianos con más electores.')}
<p>El mapa por concejos enseña de dónde sale cada voto. En 1977, UCD ganó en 47 concejos, casi todo el occidente y el oriente, y el PSOE en 26, los de la zona central: Gijón, Avilés y las cuencas mineras. En 1996 y en 2004, los dos años en que el PP ganó en Asturias con poca ventaja, el PSOE siguió siendo el más votado en más concejos (56 frente a 22, y 44 frente a 34). En 2015, Podemos solo ganó en dos concejos, Mieres y Carreño; el PP fue el más votado en 45, entre ellos Gijón, Avilés y Siero, y el PSOE, en 31, como Langreo y San Martín del Rey Aurelio. Y en 2023 el reparto quedó casi empatado: 40 concejos para el PSOE y 38 para el PP.</p>
{F.mapa('Asturias, concejo a concejo', 'Lista más votada en cada concejo en las generales.')}
<p>Solo tres de los 78 concejos han votado al mismo partido en las 16 generales: Ribera de Arriba, Quirós y Sobrescobio, los tres al PSOE.</p>

<h2>Votar menos que la media</h2>
<p>Asturias vota algo menos que el conjunto de España en las generales. Sin contar el voto exterior, su participación quedó por debajo de la media en 15 de las 16 elecciones. La excepción fue 2023, con el 71,1% frente al 70,4%.</p>
{F.part('Participación en las generales: Asturias y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Asturias elige 7 diputados en una sola circunscripción. En 2023 fueron 3 para el PP, 2 para el PSOE y 1 para Sumar y Vox. El 29 de noviembre dirá si el PP repite como lista más votada, como en 2023, o si el PSOE, que gobierna el Principado desde 2012, vuelve a ser el más votado en unas generales.</p>
"""


PIEZA = dict(
    cc='asturias', slug='asturias-historia-electoral', lugar='Asturias', corto='Asturias en las urnas',
    titulo='El PSOE ha gobernado Asturias en diez de sus doce legislaturas; en las generales, el PP ganó allí en 2004 aunque España votó a Zapatero',
    dek='Las dos excepciones al gobierno socialista, Sergio Marqués en 1995 y Álvarez-Cascos en 2011, acabaron en crisis. '
        'En las generales Asturias es más disputada: el PP ganó en siete de las dieciséis y Podemos sacó el 21,5% en 2015.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSOE ha gobernado Asturias en diez de las doce legislaturas autonómicas. Las dos excepciones, Marqués y Álvarez-Cascos, acabaron en crisis. En las generales, el PP ganó allí siete veces, también en 2004.',
    compara='Las 12 elecciones a la Junta General del Principado (1983-2023) y las 16 generales (1977-2023) en Asturias, por concejo.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('aasturias', 'Asturias'),
                               (IDP11, 'Leopoldo Tolivar Alas, «Asturias», Informe Comunidades Autónomas 2011, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP12, 'Paloma Requejo Rodríguez, «Asturias», Informe Comunidades Autónomas 2012, IDP Barcelona'),
                               (IDP23, 'Paloma Requejo Rodríguez, «Asturias», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (CASCOS, 'Público, «Cascos convoca elecciones en Asturias tras sólo seis meses en el Gobierno» (30-1-2012)'),
                               (W95, 'Wikipedia, Elecciones a la Junta General del Principado de Asturias de 1995'),
                               (W11, 'Wikipedia, Elecciones a la Junta General del Principado de Asturias de 2011')],
    enlaces=[],
)
