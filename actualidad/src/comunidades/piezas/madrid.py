"""Comunidad de Madrid: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP21 = 'https://www.idpbarcelona.net/docs/public/iccaa/2021/madrid_2021.pdf'
AYUSO = 'https://www.elsaltodiario.com/partidos-politicos/ayuso-convoca-elecciones-anticipadas-madrid'
BOE26 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742'
W03M = wiki('Elecciones a la Asamblea de Madrid de mayo de 2003')
W03O = wiki('Elecciones a la Asamblea de Madrid de octubre de 2003')
W19 = wiki('Elecciones a la Asamblea de Madrid de 2019')
WG23 = wiki('Elecciones generales de España de 2023')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PP gobierna la Comunidad de Madrid desde 1995, treinta y un años seguidos. Lo ha hecho con mayorías absolutas, en minoría con el apoyo de Ciudadanos y Vox, y también después de perder unas elecciones: en 2019 el PSOE fue la lista más votada, pero Isabel Díaz Ayuso llegó a la presidencia con 30 escaños, el peor resultado de su partido en Madrid. Cuatro años después tenía 70 y mayoría absoluta.</p>
<p>Antes, los socialistas habían gobernado los doce primeros años de la autonomía con Joaquín Leguina. En las generales, Madrid fue del PSOE hasta 1986, y desde 1989 vota casi siempre al PP. Es la comunidad que más vota: su participación ha superado la media española en las dieciséis generales.</p>
<p>Este reportaje recorre esa historia con los resultados de las elecciones a la Asamblea de Madrid, de 1983 a 2023, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Doce años de Leguina, treinta y uno del PP</h2>
<p>El Estatuto de Autonomía de la Comunidad de Madrid se aprobó en febrero de 1983 y la primera Asamblea se votó en mayo de ese año. El PSOE sacó el 50,5% y 51 de los 94 escaños, la única mayoría absoluta socialista en la historia de la cámara. Joaquín Leguina fue investido presidente. En 1987 los socialistas bajaron a 40 escaños y el CDS de Adolfo Suárez entró con 17; Leguina salió elegido en segunda votación. En 1991 el PP ya fue el partido más votado, con 47 escaños, pero Leguina siguió gracias a los 13 diputados de Izquierda Unida, según los registros de Historia Electoral.</p>
{F.aut('Escaños en la Asamblea de Madrid, 1983-2023', 'Diputados de cada partido en las trece elecciones autonómicas, con las dos de 2003.')}
<p>El gráfico muestra también cómo crece la cámara: el número de diputados depende de la población, y ha pasado de 94 en 1983 a 135 en 2023. En 1995 llegó Alberto Ruiz-Gallardón, con 54 escaños y mayoría absoluta, que repitió en 1999.</p>
{presidentes([('1983', '1995', 'Joaquín Leguina', 'PSOE'), ('1995', '2003', 'Alberto Ruiz-Gallardón', 'PP'), ('2003', '2012', 'Esperanza Aguirre', 'PP'),
              ('2012', '2015', 'Ignacio González', 'PP'), ('2015', '2018', 'Cristina Cifuentes', 'PP'), ('2018', '2019', 'Ángel Garrido', 'PP'),
              ('2019', 'hoy', 'Isabel Díaz Ayuso', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Comunidad de Madrid desde el Estatuto de 1983. Fuente: <a href="https://www.historiaelectoral.com/amadrid.html">Historia Electoral</a>.</p>

<h2>2003: las elecciones que hubo que repetir</h2>
<p>En mayo de 2003 el PP de Esperanza Aguirre ganó con 55 escaños, uno menos que la mayoría absoluta de una cámara de 111. El PSOE, con 47, y la coalición de IU, con 9, sumaban 56, y el socialista Rafael Simancas tenía la presidencia al alcance. No llegó: dos diputados de su propia lista, Eduardo Tamayo y María Teresa Sáez, se negaron a integrarse en el grupo socialista y pasaron al grupo mixto. Las dos votaciones de investidura fracasaron, y la Comunidad siguió casi siete meses en funciones, según la <a href="{W03M}">crónica de aquellas elecciones</a>. El caso se conoce como el «tamayazo».</p>
<p>Hubo que repetir las elecciones el 26 de octubre. Esta vez el PP sacó 57 escaños y el 48,5% de los votos, y Aguirre fue presidenta con mayoría absoluta, según los <a href="{W03O}">resultados de la repetición</a>. Volvió a ganarla en 2007 y en 2011, con 67 y 72 escaños.</p>
<p>Aguirre dejó el cargo en 2012 y lo heredó Ignacio González. En 2015 el PP bajó a 48 escaños con Cristina Cifuentes, que gobernó con el apoyo de Ciudadanos, y en 2018 la relevó Ángel Garrido.</p>

<h2>Ayuso: de 30 a 70</h2>
<p>En 2019 el PSOE de Ángel Gabilondo fue el más votado, con el 27,3% y 37 escaños, por primera vez desde 1987. Pero la suma de PP (30), Ciudadanos (26) y Vox (12) daba mayoría, y el 14 de agosto Isabel Díaz Ayuso fue investida con esos votos, según la <a href="{W19}">crónica de aquella investidura</a>. Gobernó en coalición con Ciudadanos.</p>
<p>Aquella coalición se rompió el 10 de marzo de 2021. Esa mañana, Ciudadanos y el PSOE presentaron una moción de censura en la Región de Murcia, y Ayuso disolvió la Asamblea de Madrid y convocó elecciones. Lo explicó así:</p>
{F.cita('Me he visto obligada a tomar esta decisión por el bien de Madrid y de España y contra mi voluntad repetida de agotar la legislatura', 'Isabel Díaz Ayuso', 'presidenta de la Comunidad de Madrid, al convocar elecciones anticipadas', AYUSO, 'El Salto', '10 de marzo de 2021')}
<p>En las elecciones del 4 de mayo de 2021 el PP pasó de 30 a 65 escaños, con el 44,8% de los votos, y Ciudadanos se quedó fuera de la Asamblea. El constitucionalista Ignacio García Vitoria, de la Universidad Complutense de Madrid, subrayaba el otro cambio de aquella noche:</p>
{F.cita('El Partido Socialista perdió la segunda plaza, al ser superado en votos por Más Madrid', 'Ignacio García Vitoria', 'Universidad Complutense de Madrid, en el Informe Comunidades Autónomas 2021 del Instituto de Derecho Público', IDP21, 'IDP Barcelona', '2022')}
<p>Ayuso fue investida con los votos del PP y de Vox y formó un gobierno solo del PP. En mayo de 2023 sacó 70 escaños de 135, dos por encima de la mayoría absoluta, y el 22 de junio fue reelegida solo con los votos de su grupo; Vox se abstuvo. Más Madrid y el PSOE quedaron empatados a 27 escaños. Las próximas autonómicas son en mayo de 2027.</p>

<h2>En las generales: del PSOE al PP</h2>
<p>En las generales, Madrid fue durante los primeros años una plaza socialista. En 1977 UCD ganó por dos décimas (32,0% frente a 31,8%), y desde 1979 el PSOE fue el más votado tres veces seguidas, con su máximo en 1982: el 51,9%. En 1989 el PP ya ganó en Madrid, cuando en España todavía ganaba Felipe González, y lo mismo pasó en 1993, en 2004 y en 2008. Madrid solo volvió a votar al PSOE en las dos generales de 2019.</p>
{F.gen('PSOE, PP y los demás en Madrid', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>Madrid ha sido además el escaparate de los partidos nuevos. UPyD sacó el 10,4% en 2011; en 2015 Podemos llegó al 21,0% y fue segundo (en el gráfico, su línea suma también el 5,3% de IU); Ciudadanos llegó al 21,1% en abril de 2019, y Vox llegó al 18,5% en noviembre de ese año.</p>
{F.esp('PSOE y PP en Madrid y en España', 'PSOE y AP/PP en la Comunidad de Madrid y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en la Comunidad de Madrid', 'Lista más votada en las generales de 1977 a 2023 en la provincia.')}
<p>Dentro de la comunidad, la capital y el cinturón del sur votan distinto. La ciudad de Madrid, con 2,4 millones de electores, vota al PP en todas las generales desde 1989, salvo en abril de 2019. Fuenlabrada, Leganés, Getafe y Parla, en cambio, han votado al PSOE en casi todas: solo se le escaparon en 2011 y 2016, cuando ganó el PP (en Parla, en 2016, Unidos Podemos), y en 2015 en tres de ellas: Leganés y Getafe votaron al PP y Parla, a Podemos. En 2023 fueron las cuatro únicas grandes ciudades donde ganaron los socialistas; Móstoles, Alcalá de Henares, Alcorcón y Torrejón de Ardoz, que en abril y noviembre de 2019 votaron al PSOE, volvieron al PP.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios madrileños con más electores.')}
<p>El mapa por municipios muestra cómo se ha movido el voto. En 1977 UCD fue la lista más votada en 116 municipios, entre ellos la capital y casi toda la sierra, y el PSOE en 54, sobre todo en el sur y en el corredor del Henares. En noviembre de 2019 el mapa se partió en cuatro colores: el PSOE ganó en 68 municipios, sobre todo en el sur y el sureste; Vox, en 61, casi todos pueblos del suroeste y del este; el PP, en 47, con la capital y los municipios del noroeste, y Unidas Podemos, en 3. En 2023 el PP fue el más votado en 158 de los 179 municipios, y el PSOE, en 19, entre ellos las cuatro ciudades del sur y varios pueblos del sureste.</p>
{F.mapa('Madrid, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Solo uno de los 172 municipios con datos en las 16 elecciones ha votado siempre a la misma lista: Fuentidueña de Tajo, al PSOE.</p>

<h2>La comunidad que más vota</h2>
<p>Madrid ha votado más que el conjunto de España en las dieciséis generales, sin contar el voto exterior. En 1977 participó el 85,5% del censo, frente al 79,1% del país; en 2023, el 74,2%, frente al 70,4%.</p>
{F.part('Participación en las generales: Madrid y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Madrid elegirá 38 diputados, uno más que en 2023, según el <a href="{BOE26}">decreto de convocatoria</a>. Es la mayor circunscripción de España. En 2023 fueron 16 para el PP, 10 para el PSOE, 6 para Sumar y 5 para Vox, según los resultados <a href="{WG23}">recogidos en Wikipedia</a>. El 29 de noviembre dirá si el PP repite la ventaja de 2023 y si el cinturón del sur sigue siendo socialista.</p>
"""


PIEZA = dict(
    cc='madrid', slug='madrid-historia-electoral', lugar='Comunidad de Madrid', corto='Madrid en las urnas',
    titulo='El PP gobierna Madrid desde 1995, también tras perder en 2019; Ayuso pasó de 30 a 70 escaños en cuatro años',
    dek='Leguina gobernó los doce primeros años de la autonomía. Después llegaron Gallardón, el «tamayazo» de 2003, Aguirre y Ayuso. '
        'En las generales, Madrid vota al PP desde 1989 casi sin excepción, mientras el cinturón del sur sigue con el PSOE. Y es la comunidad que más vota.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PP gobierna la Comunidad de Madrid desde 1995. En 2019 el PSOE fue el más votado, pero Ayuso fue investida con 30 escaños; en 2023 tenía 70 y mayoría absoluta. En las generales, Madrid vota al PP desde 1989, salvo en 2019.',
    compara='Las elecciones a la Asamblea de Madrid (1983-2023) y las 16 generales (1977-2023) en la Comunidad de Madrid, por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('amadrid', 'la Comunidad de Madrid'),
                               (IDP21, 'Ignacio García Vitoria, «Madrid», Informe Comunidades Autónomas 2021, Instituto de Derecho Público (IDP Barcelona)'),
                               (AYUSO, 'El Salto, «Ayuso convoca elecciones anticipadas en Madrid…» (10-3-2021)'),
                               (W03M, 'Wikipedia, Elecciones a la Asamblea de Madrid de mayo de 2003'),
                               (W03O, 'Wikipedia, Elecciones a la Asamblea de Madrid de octubre de 2003'),
                               (W19, 'Wikipedia, Elecciones a la Asamblea de Madrid de 2019'),
                               (WG23, 'Wikipedia, Elecciones generales de España de 2023'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones')],
    enlaces=[],
)
