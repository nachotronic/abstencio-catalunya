"""Comunitat Valenciana: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP03 = 'https://www.idpbarcelona.net/docs/public/iccaa/2003/cvalenciana_2003.pdf'
IDP15 = 'https://www.idpbarcelona.net/docs/public/iccaa/2015/cvalenciana_2015.pdf'
IDP19 = 'https://www.idpbarcelona.net/docs/public/iccaa/2019/cvalenciana_2019.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/cvalenciana_2023.pdf'
MAZON = 'https://www.eldiario.es/comunitat-valenciana/mazon-anuncia-dimision-presidente-generalitat-cerrar-sucesor-valide-vox_1_12133992.html'
VAL15 = 'https://www.publico.es/resultados-elecciones/generales/2015/comunitat-valenciana/valencia'
PUB15 = 'https://www.publico.es/resultados-elecciones/generales/2015/comunitat-valenciana'
G19 = wiki('Elecciones generales de España de abril de 2019')
W99 = wiki('Elecciones a las Cortes Valencianas de 1999')
W15 = wiki('Elecciones a las Cortes Valencianas de 2015')
HE = 'https://www.historiaelectoral.com/avalencia.html'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">En las elecciones generales, la Comunitat Valenciana ha ido a veces por delante de España y a veces por detrás. El PP fue aquí la lista más votada por primera vez en 1993, cuando Felipe González todavía ganaba en el conjunto del país, y siguió siéndolo en 2004 y 2008, los dos años en que España eligió a Zapatero. Desde 1993, el PSOE solo ha ganado en la comunidad en las dos generales de 2019.</p>
<p>En las Corts Valencianes, el péndulo ha sido más lento. El PSOE gobernó la Generalitat los doce primeros años, de 1983 a 1995; el PP, los veinte siguientes, con cuatro mayorías absolutas seguidas, y el pacto del Botànic de socialistas y Compromís, de 2015 a 2023. Desde 2023 gobierna otra vez el PP, que tras la dana de 2024 cambió de presidente sin pasar por las urnas.</p>
<p>Este reportaje recorre esa historia con los resultados de las once elecciones autonómicas, de 1983 a 2023, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Doce años del PSOE, veinte del PP</h2>
<p>El Estatuto de Autonomía se aprobó el 1 de julio de 1982 y las primeras Corts se votaron en mayo de 1983. El PSOE de Joan Lerma sacó el 51,4% de los votos y 51 de los 89 escaños. Lerma gobernó doce años: con mayoría absoluta en 1983 y en 1991, cuando se quedó justo en los 45 diputados necesarios, y en 1987 con los votos de la coalición IU-UPV en la investidura, según los registros de Historia Electoral.</p>
{F.aut('Escaños en las Corts Valencianes, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas.')}
<p>En 1995 el PP de Eduardo Zaplana ganó con 42 escaños, a tres de la mayoría, y fue investido con los votos de Unió Valenciana, el partido regionalista que tuvo diputados de 1987 a 1995. A partir de ahí llegaron cuatro mayorías absolutas seguidas del PP: 49 escaños en 1999 y 48 en 2003, sobre 89, y 55 en 2007 y en 2011, ya sobre 99, porque la cámara creció en 2007. En 2002 Zaplana dejó la presidencia a José Luis Olivas, y en 2003 llegó Francisco Camps.</p>
<p>Unió Valenciana, que llegó al 10,4% en 1991, se quedó sin escaños en 1999 con el 4,7%, por debajo del 5% de los votos en toda la comunidad. Es la misma barrera que, según la <a href="{W15}">crónica de 2015</a>, dejó sin diputados a la coalición de Esquerra Unida aquel año. En 2023 se quedaron fuera Podemos, con el 3,6%, y Ciudadanos, con el 1,5%.</p>
{presidentes([('1982', '1995', 'Joan Lerma', 'PSOE'), ('1995', '2002', 'Eduardo Zaplana', 'PP'), ('2002', '2003', 'José Luis Olivas', 'PP'),
              ('2003', '2011', 'Francisco Camps', 'PP'), ('2011', '2015', 'Alberto Fabra', 'PP'), ('2015', '2023', 'Ximo Puig', 'PSOE'),
              ('2023', '2025', 'Carlos Mazón', 'PP'), ('2025', 'hoy', 'Juan Francisco Pérez Llorca', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Generalitat desde diciembre de 1982. Antes hubo dos presidentes preautonómicos, Josep Lluís Albiñana (PSOE, 1978-1979) y Enrique Monsonís (UCD, 1979-1982). Fuente: <a href="{HE}">Historia Electoral</a>.</p>

<h2>2015: el Botànic</h2>
<p>Camps ganó en 2011 su segunda mayoría absoluta, con 55 escaños, pero dimitió en julio, poco después de tomar posesión, por su imputación en el caso Gürtel, y le sustituyó Alberto Fabra. En mayo de 2015 el PP siguió siendo la lista más votada, pero cayó de 55 a 31 escaños. Entraron Ciudadanos y Podemos, con 13 cada uno, y Compromís subió de 6 a 19. El socialista Ximo Puig, segundo con 23 diputados, fue investido con los votos de PSOE, Compromís y parte de Podemos, y formó un gobierno de coalición con Compromís. La constitucionalista Mª Josefa Ridaura, de la Universitat de València, lo explicó así:</p>
{F.cita('por primera vez en 20 años de gobierno autonómico y hegemónico del Partido Popular, se ha producido un cambio en el Gobierno de la Generalitat', 'Mª Josefa Ridaura Martínez', 'Universitat de València, en el Informe Comunidades Autónomas 2015 del Instituto de Derecho Público', IDP15, 'IDP Barcelona', '2016')}
<p>Puig adelantó las elecciones de 2019 al 28 de abril, el mismo día que las generales. El PSOE fue entonces el más votado, con 27 escaños, y el Botànic repitió con Unides Podem dentro del Gobierno.</p>

<h2>2023: el PP vuelve, con Vox</h2>
<p>En mayo de 2023 el PP de Carlos Mazón pasó de 19 a 40 escaños y, con los 13 de Vox, sumó la mayoría. Mazón fue investido con los votos de los dos partidos y formó un gobierno de coalición con Vox. Para Ridaura, aquellas elecciones fueron parte de un cambio más amplio, que llegó también a los ayuntamientos de Valencia, Alicante y Castellón: «Estos datos confirman un movimiento péndulo generalizado en toda la Comunitat Valenciana», escribió en su <a href="{IDP23}">informe de aquel año</a>.</p>
<p>El 29 de octubre de 2024, la dana causó 229 muertos en las comarcas valencianas. Un año después, el 3 de noviembre de 2025, Mazón anunció su dimisión, y apeló a la mayoría parlamentaria para que eligiera a otro presidente:</p>
{F.cita('Por voluntad personal habría dimitido hace tiempo, ha habido momentos insoportables y ya no puedo más', 'Carlos Mazón', 'presidente de la Generalitat, al anunciar su dimisión', MAZON, 'elDiario.es', '3 de noviembre de 2025')}
<p>El 27 de noviembre, Juan Francisco Pérez Llorca fue investido con los mismos 53 votos de PP y Vox. Las próximas autonómicas tocan en 2027.</p>

<h2>En las generales: del PSOE al PP, antes que España</h2>
<p>En las generales, la Comunitat Valenciana votó al PSOE en las cinco primeras, de 1977 a 1989, incluidas las dos que en España ganó UCD; en 1979, por menos de un punto (37,0% frente a 36,3%). Su mejor resultado fue el 53,4% de 1982. En 1993 el PP ya fue el más votado, con el 40,8% frente al 38,5%, y ganó todas las generales hasta 2016. Su máximo llegó en 2011: el 53,9%.</p>
{F.gen('PSOE, UCD, PP y los demás en la Comunitat Valenciana', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>La línea morada suma, en cada elección, a los partidos a la izquierda del PSOE, también a Compromís, vaya solo o en coalición. En 2015 eran dos listas: Podemos-Compromís, que sacó el 25,2% de los votos en la comunidad, y Unidad Popular, la de Izquierda Unida, con el 4,2%, según <a href="{PUB15}">los resultados publicados por Público</a>. En abril de 2019 Compromís también se presentó por su cuenta, separado de Unidas Podemos, y sacó un diputado, según la <a href="{G19}">crónica de aquellas elecciones</a>: Unidas Podemos tuvo el 14,3% y Compromís el 6,5%. En noviembre, de nuevo por separado, Unidas Podemos sacó el 13,5% y Más Compromís, el 7,0%. Los gráficos de ganadores, en cambio, no suman: en las provincias, las ciudades y el mapa municipal cuenta la lista más votada.</p>
{F.esp('PSOE y PP en la Comunitat Valenciana y en España', 'PSOE y AP/PP en la Comunitat Valenciana y en el conjunto de España, en las generales.')}
<p>El gráfico muestra la distancia con el resto del país. En 2004 el PP ganó aquí con el 47,5%, frente al 43,1% del PSOE, y en 2008 con el 52,2%, frente al 41,2%. En total, la comunidad votó distinto que España en cinco de las dieciséis generales: 1977, 1979, 1993, 2004 y 2008. Desde 2011 ha acompañado siempre al ganador nacional.</p>
{F.prov('Quién ganó en cada provincia valenciana', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Las tres provincias se han movido casi siempre juntas. La excepción fue Castellón, que votó a UCD en 1977 y en 1979. En 2015, sumadas, las dos listas a la izquierda del PSOE superaban al PP en la provincia de Valencia, pero la lista más votada fue el PP, con el 30,4%, frente al 27,2% de Compromís-Podemos, según <a href="{VAL15}">los resultados publicados por Público</a>.</p>
<p>Las ciudades grandes también han cambiado a la vez. València votó a UCD en 1979 y al PP de 1993 a 2016, igual que Alicante. Elche siguió con el PSOE en 1993, y Castelló de la Plana volvió a votar socialista en 2004. En 2023 el PP fue el más votado en seis de los diez municipios más grandes, y el PSOE en Paterna, Sagunt, Alcoi y Sant Vicent del Raspeig.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios valencianos con más electores.')}
<p>El mapa municipal sigue el mismo péndulo. En 1977 UCD ganó en 320 de los 540 municipios y el PSOE en 155; en más de cuarenta pueblos del interior de Castellón la más votada fue la Candidatura Independiente de Centro. En 1982 el PSOE ganó en 410. En 1993, el año del primer triunfo del PP en la comunidad, los dos partidos casi empataron en municipios, 282 para el PP y 251 para el PSOE. En 2011 el mapa fue casi entero azul: el PP ganó en 514 municipios y el PSOE en 26. En 2015 la lista de Compromís y Podemos fue la más votada en 113 municipios, y en 2016, ya como única lista a la izquierda del PSOE, en 84. Y en 2023 el PP ganó en 305, casi todo el sur de Alicante y buena parte del interior, y el PSOE en 224, sobre todo en el centro de la provincia de Valencia y en el norte de Castellón.</p>
{F.mapa('La Comunitat Valenciana, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Solo uno de los 527 municipios con datos en las 16 generales ha votado siempre al mismo partido: Soneja, en Castellón, al PSOE.</p>

<h2>Votar más que la media</h2>
<p>La Comunitat Valenciana vota más que el conjunto de España en las generales. Sin contar el voto exterior, su participación ha superado la media en las 16 elecciones. En 2023 votó el 73,6% del censo, frente al 70,4% del país.</p>
{F.part('Participación en las generales: la Comunitat Valenciana y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>La Comunitat Valenciana elige 33 diputados: 16 por Valencia, 12 por Alicante y 5 por Castellón. En 2023 fueron 13 para el PP, 11 para el PSOE, 5 para Vox y 4 para Sumar-Compromís. Como desde 2011 la comunidad ha votado siempre al mismo ganador que España, el 29 de noviembre servirá para ver si la racha sigue, y cuánto pesan en unas generales la dana y el relevo de Mazón por Pérez Llorca, un año después.</p>
"""


PIEZA = dict(
    cc='comunidad-valenciana', slug='comunidad-valenciana-historia-electoral', lugar='Comunitat Valenciana', corto='La Comunitat Valenciana en las urnas',
    titulo='La Comunitat Valenciana votó al PP en las generales de 1993, 2004 y 2008, cuando España eligió al PSOE; en la Generalitat, el PP gobernó 20 años seguidos',
    dek='El PSOE gobernó los doce primeros años; el PP, de 1995 a 2015, y el Botànic de socialistas y Compromís, hasta 2023. '
        'Desde entonces gobierna el PP con Vox, con un presidente nuevo tras la dimisión de Mazón por la dana. En las generales, la comunidad vota siempre más que la media.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='La Comunitat Valenciana votó al PP en las generales de 1993, 2004 y 2008, mientras España elegía al PSOE. En las Corts, el PSOE gobernó doce años, el PP veinte y el Botànic ocho. Desde 2023 gobierna el PP con Vox.',
    compara='Las 11 elecciones a las Corts Valencianes (1983-2023) y las 16 generales (1977-2023) en la Comunitat Valenciana, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('avalencia', 'la Comunitat Valenciana'),
                               (IDP15, 'Mª Josefa Ridaura Martínez, «Comunidad Valenciana», Informe Comunidades Autónomas 2015, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP19, 'Mª Josefa Ridaura Martínez, «Comunitat Valenciana», Informe Comunidades Autónomas 2019, IDP Barcelona'),
                               (IDP23, 'Mª Josefa Ridaura Martínez, «Comunitat Valenciana», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (MAZON, 'elDiario.es, «Mazón anuncia su dimisión…» (3-11-2025)'),
                               (VAL15, 'Público, resultados de las generales de 2015 en la provincia de Valencia'),
                               (PUB15, 'Público, resultados de las generales de 2015 en la Comunitat Valenciana'),
                               (G19, 'Wikipedia, Elecciones generales de España de abril de 2019'),
                               (W99, 'Wikipedia, Elecciones a las Cortes Valencianas de 1999'),
                               (W15, 'Wikipedia, Elecciones a las Cortes Valencianas de 2015')],
    enlaces=[],
)
