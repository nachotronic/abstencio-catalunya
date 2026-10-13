"""Castilla-La Mancha: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP11 = 'https://www.idpbarcelona.net/docs/public/iccaa/2011/clm_2011.pdf'
IDP15 = 'https://www.idpbarcelona.net/docs/public/iccaa/2015/clm_2015.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/clm_2023.pdf'
PODEMOS17 = 'https://www.elindependiente.com/politica/2017/08/09/podemos-consuma-entrada-gobierno-page-clm-lider-vicepresidente/'
BOE26 = 'https://www.boe.es/boe/dias/2026/10/06/pdfs/BOE-A-2026-20742.pdf'
BONO = wiki('José Bono')
W15 = wiki('Elecciones a las Cortes de Castilla-La Mancha de 2015')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Castilla-La Mancha ha votado once veces su parlamento, las Cortes regionales, y en diez de esas legislaturas el presidente fue del PSOE. José Bono gobernó 21 años seguidos, de 1983 a 2004, siempre con mayoría absoluta. La única interrupción fue la de María Dolores de Cospedal, del PP, entre 2011 y 2015. Desde entonces gobierna Emiliano García-Page, que en 2023 retuvo la mayoría absoluta por un solo escaño.</p>
<p>En las elecciones generales, en cambio, Castilla-La Mancha vota otra cosa. El PP ha sido la lista más votada en ocho de las dieciséis generales desde 1977, incluidas las de 2004 y 2008, que en el conjunto de España ganó José Luis Rodríguez Zapatero. Y en las de julio de 2023, dos meses después de que Page ganara las autonómicas con el 45% de los votos, el PP volvió a quedar primero en la comunidad.</p>
<p>Este reportaje recorre esa doble historia con los resultados de las once elecciones autonómicas, de 1983 a 2023, y de las dieciséis generales, municipio a municipio.</p>

<h2>Siete mayorías absolutas seguidas</h2>
<p>El Estatuto de Autonomía de Castilla-La Mancha se aprobó en agosto de 1982 y las primeras Cortes se votaron en mayo de 1983. El PSOE sacó 23 de los 44 escaños, uno más de la mitad, y Bono fue investido con los votos de su grupo. A partir de ahí, los socialistas encadenaron siete mayorías absolutas, de 1983 a 2007. La más amplia fue la de 2003: el 57,8% de los votos y 29 de los 47 escaños, según Historia Electoral. La más justa, la de 1995, con 24 escaños de 47; Bono fue investido aquel año con 24 votos a favor y 23 en contra, los del PP y el diputado de IU.</p>
{F.aut('Escaños en las Cortes de Castilla-La Mancha, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas.')}
<p>Las Cortes han sido casi siempre un parlamento de dos. Además del PSOE y el PP, solo han tenido diputados el CDS (4 en 1987), Izquierda Unida (1 en 1991 y en 1995), Podemos (2 en 2015), Ciudadanos (4 en 2019) y Vox (4 en 2023). Bono dejó la presidencia en 2004 para ser ministro de Defensa en el primer Gobierno de Zapatero, según su <a href="{BONO}">biografía</a>, y José María Barreda fue investido en abril de ese año con los 29 votos socialistas.</p>
{presidentes([('1982', '1983', 'Jesús Fuentes', 'PSOE'), ('1983', '2004', 'José Bono', 'PSOE'), ('2004', '2011', 'José María Barreda', 'PSOE'),
              ('2011', '2015', 'María Dolores de Cospedal', 'PP'), ('2015', 'hoy', 'Emiliano García-Page', 'PSOE')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Junta de Comunidades desde el Estatuto de 1982. Antes hubo dos presidentes preautonómicos, Antonio Fernández-Galiano y Gonzalo Payo. Fuente: <a href="https://www.historiaelectoral.com/acmancha.html">Historia Electoral</a>.</p>

<h2>2011: el cambio por un escaño</h2>
<p>En mayo de 2011, el PP de Cospedal ganó por primera vez: 25 escaños frente a 24, la mayoría absoluta por la mínima en unas Cortes de 49 diputados. El constitucionalista Francisco Javier Díaz Revorio, de la Universidad de Castilla-La Mancha, explicaba así por qué aquel resultado era excepcional:</p>
{F.cita('Castilla-La Mancha era, hasta este año, la única Comunidad en la que un mismo partido había obtenido siempre mayoría absoluta, y por tanto gobernado cómodamente', 'Francisco Javier Díaz Revorio', 'Universidad de Castilla-La Mancha, en el Informe Comunidades Autónomas 2011 del Instituto de Derecho Público', IDP11, 'IDP Barcelona', '2012')}
<p>El reparto también fue ajustado. Según el mismo informe, el PP fue el más votado en todas las provincias menos en Ciudad Real, donde el PSOE ganó por unos 500 votos, y durante buena parte de la noche electoral el recuento provisional llegó a dar al PP 28 escaños. Cospedal fue investida el 21 de junio con los 25 votos de su grupo.</p>
<p>Antes de las siguientes elecciones, una reforma de la ley electoral aprobada en 2014 redujo el parlamento de 49 a 33 diputados, con un mínimo de tres por provincia, como recoge Díaz Revorio en su <a href="{IDP15}">informe de 2015</a>. Con menos escaños por provincia, Ciudadanos se quedó fuera de las Cortes aquel año pese a sacar el 8,6% de los votos.</p>

<h2>2015: ganar y no gobernar</h2>
<p>En mayo de 2015, el PP volvió a ser el más votado, con el 37,5% y 16 escaños, pero se quedó a uno de la mayoría absoluta. El PSOE de García-Page, con 15, firmó un programa con Podemos, que había entrado en las Cortes con 2 diputados, y fue investido el 1 de julio con 17 votos frente a 16. Al principio el apoyo de Podemos fue externo. En el verano de 2017, después de una consulta a sus bases, Podemos entró en el Gobierno: su líder regional, José García Molina, fue nombrado vicepresidente segundo, según contó <a href="{PODEMOS17}">El Independiente</a>, que lo describía como «el primer ensayo autonómico» de la alianza que Podemos aspiraba a reeditar en toda España. El secretario general del partido lo había defendido así:</p>
{F.cita('Hacemos política para cambiar las cosas. A veces, sólo gobernar garantiza el cambio', 'Pablo Iglesias', 'secretario general de Podemos, en Twitter, sobre la entrada de su partido en el Gobierno de Page', PODEMOS17, 'El Independiente', '9 de agosto de 2017')}

<h2>2019 y 2023: Page, solo</h2>
<p>En 2019 Page recuperó la mayoría absoluta con 19 de los 33 escaños y fue investido solo con los votos socialistas. Podemos, que había bajado del 9,8% al 6,9%, se quedó fuera de las Cortes. En 2023 el PSOE perdió dos diputados, pero conservó los 17 justos para seguir gobernando solo. Díaz Revorio subrayaba lo inusual de aquel resultado en un año muy malo para los socialistas:</p>
{F.cita('Castilla-La Mancha ha sido la única Comunidad en la que el PSOE ha obtenido mayoría absoluta', 'Francisco Javier Díaz Revorio', 'Universidad de Castilla-La Mancha, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>Vox entró aquel año en las Cortes con 4 escaños, los mismos que perdió Ciudadanos. Page fue investido el 6 de julio con 17 votos frente a los 16 de PP y Vox. Las próximas autonómicas tocan en mayo de 2027.</p>

<h2>En las generales: un territorio del PP</h2>
<p>Las generales cuentan otra historia. UCD ganó en Castilla-La Mancha en 1977 y 1979, con más del 42% de los votos. El PSOE fue el más votado de 1982 a 1993, y el PP, en todas las generales de 1996 a 2016: siete seguidas. Esa racha incluye las de 2004 y 2008, en las que España votó al PSOE de Zapatero. En 2004 la diferencia fue de un punto (48,2% frente a 47,2%); en 2008, de cinco. El PSOE solo volvió a ganar en las dos elecciones de 2019, y en 2023 el PP recuperó el primer puesto con el 39,3%.</p>
{F.gen('UCD, PSOE, PP y los demás en Castilla-La Mancha', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>El gráfico de abajo compara la comunidad con España. Los dos grandes partidos sacan aquí más votos, en porcentaje, que en el conjunto del país. El PSOE ha estado por encima de su media nacional en las 16 generales; en 2023 sacó el 34,4%, frente al 32,0% en España. El PP lo ha estado en todas desde 1982, y en 2011 llegó al 56,6%, once puntos más que su media.</p>
{F.esp('PSOE y PP en Castilla-La Mancha y en España', 'PSOE y AP/PP en Castilla-La Mancha y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en cada provincia', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Por provincias, Guadalajara es la más inclinada al PP: lo votó en 11 de las 16 generales, desde 1986 y hasta 2016 sin interrupción. Ciudad Real es la que más veces ha votado al PSOE, en 8 ocasiones, y la única que le dio la victoria en 1996 y en 2004. En 2019 las cinco provincias votaron al PSOE, y en 2023 las cinco volvieron al PP.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios con más electores.')}
<p>Las capitales de provincia se pasaron pronto al PP: Toledo y Ciudad Real lo votaron ya en 1986, y desde 1996 las cinco capitales han votado al PP en todas las generales menos en las de 2019 (Ciudad Real, solo en la de abril). La excepción entre las grandes ciudades es Puertollano, que ha votado al PSOE en 14 de las 16 generales; solo falló en 2000 y en 2011. En 2023, el PSOE ganó en Puertollano y en Alcázar de San Juan, y el PP en las otras ocho ciudades más grandes.</p>
<p>El mapa municipal enseña cómo se ha movido ese voto. En 1977, UCD fue la lista más votada en 730 de los 919 municipios de la comunidad, y el PSOE en 119, casi todos en el sur de Ciudad Real, el sureste de Albacete y el oeste de Toledo. En 1982 el mapa cambió de color: 529 municipios para el PSOE y 265 para AP. El PP pasó por delante en número de municipios en 1993 (471 frente a 442) y llegó a su máximo en 2011, cuando ganó en 823 y el PSOE solo en 96. En abril de 2019 fue al revés: el PSOE ganó en 641 municipios. En 2023, el PP ganó en 518, el PSOE en 387 y Vox, en 10. El voto socialista sigue teniendo su zona más compacta en el sur de la provincia de Ciudad Real.</p>
{F.mapa('Castilla-La Mancha, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Doce de los 899 municipios con datos en las 16 generales han votado siempre al mismo partido. Once lo han hecho al PSOE, cinco de ellos en la provincia de Ciudad Real, como Chillón, Castellar de Santiago o Mestanza; el mayor es Ossa de Montiel, en Albacete. Solo uno, Canredondo, en Guadalajara, ha votado siempre a AP y al PP.</p>

<h2>Votar más que la media</h2>
<p>Castilla-La Mancha vota más que el conjunto de España en las generales. Sin contar el voto exterior, su participación ha superado la media en las 16 elecciones. En 2023 fue del 74,4%, cuatro puntos más que en el conjunto del país.</p>
{F.part('Participación en las generales: Castilla-La Mancha y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Castilla-La Mancha elige 21 diputados, los mismos que en 2023, según el <a href="{BOE26}">decreto de convocatoria</a>: 6 por Toledo, 5 por Ciudad Real, 4 por Albacete y 3 por Cuenca y por Guadalajara. En 2023 fueron 10 para el PP, 8 para el PSOE y 3 para Vox, según el informe de Díaz Revorio. El 29 de noviembre dirá si el PP mantiene la ventaja que sacó en las generales de 2023 en una comunidad que el PSOE gobierna desde 2015, y cuánto pesa Vox, que en las generales de noviembre de 2019 llegó al 22,1% en la comunidad.</p>
"""


PIEZA = dict(
    cc='castilla-la-mancha', slug='castilla-la-mancha-historia-electoral', lugar='Castilla-La Mancha', corto='Castilla-La Mancha en las urnas',
    titulo='El PSOE ha gobernado Castilla-La Mancha en diez de sus once legislaturas; en las generales, el PP ganó allí incluso en 2004 y 2008, con Zapatero',
    dek='Bono encadenó seis mayorías absolutas y Page retuvo la suya en 2023 por un escaño. Pero en las generales la comunidad se inclina al PP: '
        'fue la lista más votada en ocho de las dieciséis desde 1977, también en 2023.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSOE ha gobernado Castilla-La Mancha en diez de sus once legislaturas, con la única excepción de Cospedal (2011-2015). En las generales, el PP ganó allí ocho veces, también en 2004 y 2008.',
    compara='Las 11 elecciones a las Cortes de Castilla-La Mancha (1983-2023) y las 16 generales (1977-2023) en Castilla-La Mancha, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('acmancha', 'Castilla-La Mancha'),
                               (IDP11, 'Francisco Javier Díaz Revorio, «Castilla-La Mancha», Informe Comunidades Autónomas 2011, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP15, 'Francisco Javier Díaz Revorio, «Castilla-La Mancha», Informe Comunidades Autónomas 2015, IDP Barcelona'),
                               (IDP23, 'Francisco Javier Díaz Revorio, «Castilla-La Mancha», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (PODEMOS17, 'El Independiente, «Podemos consuma su entrada en el Gobierno de Page» (9-8-2017)'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones (6-10-2026)'),
                               (BONO, 'Wikipedia, José Bono'),
                               (W15, 'Wikipedia, Elecciones a las Cortes de Castilla-La Mancha de 2015')],
    enlaces=[],
)
