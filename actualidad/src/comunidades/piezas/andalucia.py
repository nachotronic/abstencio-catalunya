"""Andalucía: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

DIAZ = 'https://theobjective.com/susana-diaz-descarta-dimitir/'
MORENO = 'https://www.eldebate.com/espana/andalucia/20260517/andalucia-tiene-lio-moreno-no-logra-revalidar-mayoria-lleva-delante-psoe-montero_418505.html'
IDP22 = 'https://www.idpbarcelona.net/docs/public/iccaa/2022/andalucia_2022.pdf'
INVEST26 = 'https://www.diariodeleon.es/nacional/260702/2090035/juanma-moreno-elegido-presidente-junta-andalucia-votos-pp-vox.html'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Durante 36 años, decir «Junta de Andalucía» era decir PSOE. Los socialistas ganaron las once primeras elecciones al Parlamento andaluz, de 1982 a 2018, y gobernaron sin interrupción desde la primera legislatura hasta enero de 2019. Seis presidentes seguidos, todos del mismo partido, en la comunidad más poblada de España: hoy tiene 6,4 millones de electores, casi uno de cada cinco del país.</p>
<p>Siete años después, el mapa es otro. El PP gobierna desde 2019, ganó con mayoría absoluta en 2022 y volvió a ganar en mayo de 2026, aunque con 53 escaños, dos menos de los necesarios para gobernar solo. El 2 de julio Juanma Moreno fue investido presidente con los votos del PP y de Vox, que por primera vez entra en el Gobierno andaluz, con una vicepresidencia para su líder, Manuel Gavira, según <a href="{INVEST26}">la crónica de la investidura</a>. El PSOE, con 28 escaños, firmó su peor resultado en unas autonómicas andaluzas.</p>
<p>Este reportaje recorre esa historia con los resultados de todas las elecciones desde 1977: las trece autonómicas, de las que salen los gobiernos de la Junta, y las dieciséis generales, en las que Andalucía ha pesado siempre más que ninguna otra comunidad en el reparto del Congreso.</p>

<h2>Once victorias seguidas del PSOE</h2>
<p>Andalucía llegó a la autonomía por la vía rápida del artículo 151 de la Constitución, tras el referéndum del 28 de febrero de 1980, y votó su primer Parlamento el 23 de mayo de 1982. El PSOE de Rafael Escuredo sacó 66 de los 109 escaños, con más de la mitad de los votos. Cinco meses después, Felipe González ganaba las generales con mayoría absoluta.</p>
<p>De ahí en adelante, el PSOE ganó todas las elecciones autonómicas hasta 2018. Tuvo mayoría absoluta en cinco de esas diez legislaturas y, cuando no la tuvo, buscó apoyos: el Partido Andalucista votó a Manuel Chaves en 1996 y en 2000; Izquierda Unida entró en el Gobierno de José Antonio Griñán en 2012, y Ciudadanos facilitó la investidura de Susana Díaz en 2015. La legislatura de 1994, con 45 escaños socialistas, duró menos de dos años: Chaves perdió las dos primeras votaciones de investidura, con el PP y la coalición de IU en contra, y salió elegido en la tercera, en la que IU no votó. En 1996 hubo elecciones anticipadas, el mismo día que las generales.</p>
{F.aut('Escaños en el Parlamento de Andalucía, 1982-2026', 'Diputados de cada partido en las trece elecciones autonómicas.')}
<p>El gráfico muestra cómo el bloque rojo se encoge desde 2012. El PSOE bajó de 61 escaños en 2004 a 47 en 2012 y 2015, a 33 en 2018, a 30 en 2022 y a 28 en 2026. En su lugar crecen primero los partidos nuevos, Podemos y Ciudadanos en 2015, y después el PP.</p>

<h2>2018: perder ganando</h2>
<p>Las elecciones del 2 de diciembre de 2018 fueron las primeras que el PSOE ganó sin poder gobernar. Susana Díaz quedó primera con 33 escaños, pero PP (26), Ciudadanos (21) y Vox (12), que entraba por primera vez en un parlamento autonómico, sumaron 59, cuatro más que la mayoría absoluta. Al día siguiente, Díaz reconoció el golpe sin dar un paso atrás:</p>
{F.cita('todo el PSOE debe hacer una reflexión para fortalecer el papel de las instituciones', 'Susana Díaz', 'entonces presidenta en funciones de la Junta', DIAZ, 'The Objective', '3 de diciembre de 2018')}
<p>El 16 de enero de 2019, Juanma Moreno fue investido con 59 votos: los de su partido, los de Ciudadanos, con el que formó Gobierno, y los de Vox, que se quedó fuera del Ejecutivo. Para la politóloga Mª Reyes Pérez Alberdi, de la Universidad Pablo de Olavide, el cambio tuvo una paradoja de origen:</p>
{F.cita('paradójicamente el PP, alcanzó entonces el Gobierno de la Comunidad Autónoma con uno de sus peores resultados electorales, 26 escaños, igualando a los obtenidos en 1990', 'Mª Reyes Pérez Alberdi', 'Universidad Pablo de Olavide, en el Informe Comunidades Autónomas 2022 del Instituto de Derecho Público', IDP22, 'IDP Barcelona', '2023')}

<h2>2022 y 2026: la mayoría y su pérdida</h2>
<p>En junio de 2022, el PP de Moreno sacó 58 escaños y la primera mayoría absoluta de su historia en Andalucía. Fue más que un cambio de Gobierno: el PP quedó primero en las ocho provincias. Pérez Alberdi lo resume así en el mismo informe: «El PSOE, pierde 3 escaños y la posición hegemónica que había disfrutado siempre en Andalucía».</p>
<p>Cuatro años después, el 17 de mayo de 2026, Moreno volvió a ganar con holgura, con el 41,6% de los votos según Historia Electoral, pero bajó a 53 escaños. Vox subió a 15 y Adelante Andalucía, a 8. La misma noche, el presidente lo explicó con una imagen escolar:</p>
{F.cita('Buscábamos la matrícula de honor, pero nos hemos quedado en el sobresaliente', 'Juanma Moreno', 'presidente de la Junta y candidato del PP', MORENO, 'El Debate', '17 de mayo de 2026')}
<p>Vox votó en contra en la primera votación de investidura, el 30 de junio, y Moreno solo salió elegido el 2 de julio, en la segunda, tras firmar con Vox un acuerdo de gobierno. Andalucía tiene así, por primera vez, un Gobierno con Vox dentro.</p>
{presidentes([('1982', '1984', 'Rafael Escuredo', 'PSOE'), ('1984', '1990', 'José Rodríguez de la Borbolla', 'PSOE'), ('1990', '2009', 'Manuel Chaves', 'PSOE'),
              ('2009', '2013', 'José Antonio Griñán', 'PSOE'), ('2013', '2019', 'Susana Díaz', 'PSOE'), ('2019', 'hoy', 'Juan Manuel Moreno', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Junta desde la primera legislatura autonómica (1982). Escuredo ya presidía la Junta preautonómica desde 1979. Fuente: <a href="https://www.historiaelectoral.com/aandalucia.html">Historia Electoral</a>.</p>

<h2>En las generales: el granero que dejó de serlo</h2>
<p>En las elecciones generales, el voto andaluz ha seguido un camino parecido, pero con otro ritmo. El PSOE fue la lista más votada en Andalucía en 13 de las 16 generales desde 1977, incluidas las de 1977 y 1979, que en el conjunto de España ganó UCD, y las de 1996 y 2000, que ganó el PP. Solo perdió en 2011, en 2016 y en 2023.</p>
{F.gen('PSOE, UCD, PP y los demás en Andalucía', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>El mejor momento socialista fue 1982: el 60,4% de los votos en Andalucía, doce puntos más que en el conjunto de España. Esa ventaja sobre la media nacional se mantuvo durante tres décadas y es lo que convirtió a Andalucía en el principal granero de votos del PSOE. En las generales de 2023, en cambio, el PSOE sacó el 33,8%, menos de dos puntos por encima de su media en España, y el PP ganó con el 36,8%.</p>
{F.esp('El PSOE andaluz ya casi no vota distinto que el de España', 'PSOE y AP/PP en Andalucía y en el conjunto de España, en las generales.')}

<h2>Sevilla, la provincia que nunca ha cambiado</h2>
<p>Por provincias, solo una ha votado siempre al PSOE en las generales: <strong>Sevilla</strong>, en las 16 elecciones. Jaén lo hizo en todas menos en 2011 y 2023. Almería es la que antes giró: el PP ganó allí por primera vez en 2000 y desde entonces ha ganado en seis de las nueve generales.</p>
{F.prov('Quién ganó en cada provincia andaluza', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Entre los municipios, la fidelidad es todavía más visible. De los 743 municipios andaluces con datos en las 16 generales, <strong>121 han votado siempre al PSOE</strong> como primera fuerza. El mayor es Dos Hermanas, con 107.888 electores, seguido de Alcalá de Guadaíra, Utrera y La Rinconada, todos en Sevilla. No hay ninguno que haya votado siempre al PP.</p>
{F.mapa('Andalucía, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>En el mapa se ve cómo se movió el voto. En 1977, UCD fue la lista más votada en 461 municipios andaluces y el PSOE, en 256, concentrados sobre todo en la provincia de Sevilla y en la de Cádiz. En 1982 el mapa se volvió casi entero rojo: el PSOE ganó en 692. Lo llamativo es lo que pasa en 2011 y en 2023: el PP ganó en Andalucía en votos, pero el PSOE siguió siendo el más votado en más municipios (450 frente a 317 en 2011, y 467 frente a 307 en 2023). El voto del PP se concentra en las ciudades, en la costa y en buena parte de Almería; el del PSOE, en los pueblos del interior.</p>
<p>Las grandes ciudades cambiaron antes que los pueblos. Granada y Almería votan al PP en casi todas las generales desde 1993, y Córdoba desde 1996; las excepciones son las elecciones de 2019 (en Granada, solo la de abril). En 2023 el PP ganó en ocho de los diez municipios más grandes de Andalucía, todos menos Dos Hermanas y Cádiz, mientras que en el conjunto de los municipios andaluces el PSOE ganó en 467 y el PP en 307.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios andaluces con más electores.')}

<h2>Votar menos que la media</h2>
<p>Andalucía suele votar algo menos que el resto de España en las generales. En 2023, la participación sin voto exterior fue del 69,0%, frente al 70,4% del conjunto. La diferencia es mayor en las autonómicas que se celebran solas: en las de 2022 votó el 56,1% del censo, según los resultados oficiales <a href="{wiki('Elecciones al Parlamento de Andalucía de 2022')}">recogidos en Wikipedia</a>, frente al 77,9% de 1996, cuando las andaluzas coincidieron con las generales.</p>
{F.part('Participación en las generales: Andalucía y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>En las generales de 2023, Andalucía repartió 61 de los 350 escaños del Congreso, más que ninguna otra comunidad. El 29 de noviembre, los datos permitirán seguir tres cosas: si el PP mantiene la ventaja de 2023 en las grandes ciudades; si el PSOE conserva Sevilla, la única provincia que nunca le ha fallado, y cuánto pesa Vox seis meses después de entrar en el Gobierno de la Junta.</p>
"""


PIEZA = dict(
    cc='andalucia', slug='andalucia-historia-electoral', lugar='Andalucía', corto='Andalucía en las urnas',
    titulo='El PSOE gobernó Andalucía 36 años seguidos; desde 2019 la Junta es del PP, que ahora gobierna con Vox dentro',
    dek='Los socialistas ganaron las once primeras autonómicas y 13 de las 16 generales. Sevilla es la única provincia que nunca les ha fallado. '
        'El PP ganó con mayoría absoluta en 2022, la perdió en 2026 y Moreno fue investido con los votos de Vox, que por primera vez entra en el Gobierno andaluz.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSOE ganó las once primeras elecciones andaluzas y gobernó de 1982 a 2019. El PP ganó con mayoría absoluta en 2022 y en 2026 se quedó en 53 escaños; Moreno gobierna con Vox. En las generales, solo Sevilla ha votado siempre al PSOE.',
    compara='Las 13 elecciones al Parlamento de Andalucía (1982-2026) y las 16 generales (1977-2023) en Andalucía, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('aandalucia', 'Andalucía'),
                               (IDP22, 'Mª Reyes Pérez Alberdi, «Andalucía», Informe Comunidades Autónomas 2022, Instituto de Derecho Público (IDP Barcelona)'),
                               (DIAZ, 'The Objective, «Susana Díaz descarta dimitir…» (3-12-2018)'),
                               (MORENO, 'El Debate, «Andalucía tiene “lío”…» (Roberto Marbán, 17-5-2026)'),
                               (INVEST26, 'Diario de León / Europa Press, investidura de Juanma Moreno (2-7-2026)'),
                               (wiki('Elecciones al Parlamento de Andalucía de 2022'), 'Wikipedia, Elecciones al Parlamento de Andalucía de 2022')],
    enlaces=[],
)
