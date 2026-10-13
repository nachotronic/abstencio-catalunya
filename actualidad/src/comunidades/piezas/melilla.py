"""Melilla: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

PONCE = 'https://www.ub.edu/geocrit/sn/sn-320.htm'
CASTRO = 'https://www.elindependiente.com/politica/2019/06/15/enfado-imbroda-al-perder-melilla-llama-traidor-sin-verguenza-sucesor/'
ABERCHAN = 'https://elfarodemelilla.es/?p=358592'
W19 = wiki('Elecciones a la Asamblea de Melilla de 2019')
W23 = wiki('Elecciones a la Asamblea de Melilla de 2023')
PRESI = wiki('Presidente de Melilla')
EP99 = 'https://elpais.com/diario/1999/07/04/espana/931039205_850215.html'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">En junio de 2019, Melilla eligió presidente a un diputado que tenía un solo escaño de los 25 de la Asamblea. Eduardo de Castro, de Ciudadanos, sumó los votos de Coalición por Melilla y del PSOE y desalojó a Juan José Imbroda, del PP, que llevaba 19 años en el cargo. Cuatro años después, Imbroda volvió con mayoría absoluta.</p>
<p>En las generales, Melilla es una de las plazas más fieles del PP: ha ganado allí en todas desde 1996, y ya lo había hecho en 1986 y 1989, cuando Felipe González arrasaba en el resto de España. Pero en noviembre de 2019 estuvo a punto de perder el escaño frente a Coalición por Melilla, el partido de Mustafa Aberchán.</p>
<p>Este reportaje recorre esa historia con los resultados de las elecciones locales desde 1979 y de las dieciséis generales desde 1977. Melilla es un único municipio, así que aquí no hay mapa por municipios.</p>

<h2>De ayuntamiento a ciudad autónoma</h2>
<p>Como Ceuta, Melilla eligió un ayuntamiento hasta 1995, cuando aprobó su Estatuto de Autonomía. Desde entonces sus 25 concejales forman la Asamblea de la ciudad autónoma, que elige al presidente. El gráfico junta las municipales de 1979 a 1991 y las elecciones a la Asamblea desde 1995.</p>
{F.aut('Concejales y diputados de Melilla, 1979-2023', 'Escaños de cada partido en el pleno de 25: ayuntamiento hasta 1991 y Asamblea desde 1995.')}
<p>UCD ganó las primeras municipales, en 1979, con 14 concejales. El PSOE ganó en 1983 y 1987, y el PP desde 1991. En 1995, en las primeras elecciones a la Asamblea, el PP sacó 14 escaños e Ignacio Velázquez fue el primer presidente de la ciudad autónoma.</p>
<p>Ese mismo año apareció Coalición por Melilla (CpM). El geógrafo Gabino Ponce Herrero, de la Universidad de Alicante, lo explicaba así en un estudio sobre los barrios de la ciudad:</p>
{F.cita('los colectivos musulmanes han tendido a organizar sus demandas en torno a un partido político, Coalición por Melilla –CpM-, partido creado en 1995, que surge como una escisión del PSOE', 'Gabino Ponce Herrero', 'Universidad de Alicante, en la revista Scripta Nova', PONCE, 'Scripta Nova (Universidad de Barcelona)', '2010')}

<h2>1999: el año de los cinco partidos</h2>
<p>En 1999 la Asamblea se partió en pedazos. El GIL de Jesús Gil fue el más votado, con 7 escaños; CpM y el PP sacaron 5 cada uno; Unión del Pueblo Melillense (UPM) y el Partido Independiente de Melilla, 3, y el PSOE, 2. Según Ponce, CpM entró entonces en el Gobierno «a partir de una moción de censura y diversos pactos», y Aberchán presidió la ciudad durante un año, con el apoyo del PSOE y del GIL, según contó entonces <a href="{EP99}">El País</a>. Fue el primer presidente musulmán de Melilla. En julio de 2000 una moción de censura dio la presidencia a Juan José Imbroda, entonces en UPM, que en 2003 concurrió ya en una lista conjunta con el PP.</p>
{presidentes([('1995', '1998', 'Ignacio Velázquez', 'PP'), ('1998', '1999', 'Enrique Palacios', 'independiente'), ('1999', '2000', 'Mustafa Aberchán', 'CpM'),
              ('2000', '2019', 'Juan José Imbroda', 'UPM y luego PP'), ('2019', '2023', 'Eduardo de Castro', 'Cs y luego independiente'), ('2023', 'hoy', 'Juan José Imbroda', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Ciudad Autónoma de Melilla desde el Estatuto de 1995. Fuente: <a href="{PRESI}">Wikipedia</a>.</p>
<p>De 2003 a 2011 el PP de Imbroda ganó tres mayorías absolutas seguidas, con 15 escaños y más del 53% de los votos. CpM se asentó como segunda fuerza, con entre 5 y 7 escaños. En 2015 el PP bajó a 12, uno menos de la mayoría, y siguió gobernando.</p>

<h2>2019: un presidente con un escaño</h2>
<p>En mayo de 2019 el PP sacó 10 escaños; CpM, 8; el PSOE, 4; Vox, 2, y Ciudadanos, 1. Ese único diputado, Eduardo de Castro, tenía la llave. En lugar de abstenerse para que gobernara la lista más votada, como le pedía su partido, se presentó él mismo a la investidura y salió elegido con los 13 votos de CpM, PSOE y el suyo, según la <a href="{W19}">crónica de la investidura</a>. Al terminar, resumió lo que pensaba que cambiaba:</p>
{F.cita('Se acabaron las mayorías absolutas en Melilla', 'Eduardo de Castro', 'nuevo presidente de Melilla (Ciudadanos)', CASTRO, 'El Independiente', '15 de junio de 2019')}
<p>Imbroda, que dejó la presidencia tras 19 años, lo llamó ese día «un traidor sin escrúpulos que retuerce la democracia», según la misma crónica. De Castro acabó fuera de Ciudadanos y terminó la legislatura como independiente.</p>
<p>La frase de De Castro duró una legislatura. En 2023 el PP recuperó la mayoría absoluta, con 14 escaños y más del 52% de los votos, e Imbroda volvió a la presidencia, según la <a href="{W23}">crónica de aquellas elecciones</a>. CpM bajó de 8 a 5.</p>

<h2>En las generales: el PP desde 1996</h2>
<p>Melilla elige un solo diputado al Congreso. UCD ganó allí en 1977 y 1979 con más del 50% de los votos, y el PSOE en 1982. En 1986 y 1989, cuando el PSOE ganaba con holgura en España, Melilla votó a AP y al PP. Desde 1996, el PP ha sido el más votado en las diez generales seguidas.</p>
{F.gen('UCD, PSOE, PP y los demás en Melilla', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
{F.esp('PSOE y PP en Melilla y en España', 'PSOE y AP/PP en Melilla y en el conjunto de España, en las generales.')}
<p>La racha estuvo a punto de romperse en noviembre de 2019. Las listas que en el gráfico van en «Otras listas», sobre todo Coalición por Melilla, sumaron el 29,7% de los votos sin contar el exterior, una décima menos que el PP. Según Aberchán, se quedaron a 179 votos del escaño:</p>
{F.cita('fue una oportunidad perdida y debe ser una oportunidad ganada en las próximas', 'Mustafa Aberchán', 'presidente de Coalición por Melilla, sobre las generales de noviembre de 2019', ABERCHAN, 'El Faro de Melilla', '26 de enero de 2022')}
<p>En 2023 el PP volvió a ganar con holgura, con el 49,7%, frente al 25,6% del PSOE y el 16,1% de Vox.</p>
{F.prov('Quién ganó en Melilla', 'Lista más votada en las generales de 1977 a 2023.')}

<h2>La participación más baja</h2>
<p>Melilla vota mucho menos que el conjunto de España. Sin contar el voto exterior, su participación quedó por debajo de la del país en las 16 generales. En 2023 votó el 49,8% del censo, su cifra más baja desde 1977, frente al 70,4% de España.</p>
{F.part('Participación en las generales: Melilla y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>El 29 de noviembre Melilla vuelve a elegir un diputado. El PP lo ha ganado en todas las generales desde 1996. Habrá que ver si alguna lista local vuelve a acercarse al PP como en 2019, y si la participación sale de la cifra más baja de su historia.</p>
"""


PIEZA = dict(
    cc='melilla', slug='melilla-historia-electoral', lugar='Melilla', corto='Melilla en las urnas',
    titulo='Melilla tuvo cuatro años un presidente con un solo escaño de 25; en las generales vota al PP desde 1996 y en 2019 rozó el cambio',
    dek='Eduardo de Castro, de Ciudadanos, desalojó a Imbroda en 2019 con los votos de Coalición por Melilla y del PSOE. En 2023 Imbroda volvió con mayoría absoluta. En las generales, el PP ha ganado las diez últimas.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='En 2019 Melilla eligió presidente a un diputado de Ciudadanos con un solo escaño; Imbroda (PP) volvió en 2023 con mayoría absoluta. En las generales, el PP gana desde 1996 y en noviembre de 2019 Coalición por Melilla se quedó a una décima.',
    compara='Las 12 elecciones locales y a la Asamblea de Melilla (1979-2023) y las 16 generales (1977-2023) en Melilla.',
    limites=LIMITES + ' Melilla es un solo municipio: no hay mapa. Las elecciones de 1979 a 1991 fueron municipales; desde 1995, a la Asamblea de la ciudad autónoma.',
    fuentes=FUENTES_COMUNES + [he_fuente('amelilla', 'Melilla'),
                               (PONCE, 'Gabino Ponce Herrero, «La persistencia del urbanismo musulmán: los “pueblos jóvenes” en Melilla y el debate urbanístico», Scripta Nova, vol. XIV, n.º 320 (2010)'),
                               (CASTRO, 'El Independiente, «El enfado de Imbroda al ceder Melilla» (15-6-2019)'),
                               (ABERCHAN, 'El Faro de Melilla, entrevista con Mustafa Aberchán (26-1-2022)'),
                               (W19, 'Wikipedia, Elecciones a la Asamblea de Melilla de 2019'),
                               (W23, 'Wikipedia, Elecciones a la Asamblea de Melilla de 2023'),
                               (EP99, 'El País, «Un musulmán gobernará la ciudad autónoma de Melilla con apoyo socialista y del GIL» (4-7-1999)'),
                               (PRESI, 'Wikipedia, Presidente de Melilla')],
    enlaces=[],
)
