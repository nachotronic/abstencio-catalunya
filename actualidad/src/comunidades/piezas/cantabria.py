"""Cantabria: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP19 = 'https://www.idpbarcelona.net/docs/public/iccaa/2019/cantabria_2019.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/cantabria_2023.pdf'
TUMBA = 'https://www.eldiario.es/cantabria/ultimas-noticias/oposicion-cantabria-tumba-presupuesto-pp-pleno-tenso-suspension-cautelar-habia-solicitado_1_12791775.html'
BURUAGA = 'https://www.eldiario.es/cantabria/ultimas-noticias/buruaga-habra-presupuesto-si-alguien-propuestas-haya_1_12801850.html'
PRESU26 = 'https://www.redaccionmedica.com/autonomias/20260427/aprobado-el-presupuesto-de-la-sanidad-cantabra-millones-un-mas/262074_0.html'
W87 = wiki('Elecciones a la Asamblea Regional de Cantabria de 1987')
W91 = wiki('Elecciones a la Asamblea Regional de Cantabria de 1991')
W95 = wiki('Elecciones a la Asamblea Regional de Cantabria de 1995')
W03 = wiki('Elecciones al Parlamento de Cantabria de 2003')
W23 = wiki('Elecciones al Parlamento de Cantabria de 2023')
G23 = wiki('Elecciones generales de España de 2023')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PP ha sido el partido más votado en nueve de las once elecciones al Parlamento de Cantabria. Pero durante dieciséis años, de 2003 a 2011 y de 2015 a 2023, el presidente fue Miguel Ángel Revilla, del Partido Regionalista de Cantabria (PRC), que solo ganó unas autonómicas, las de 2019. En 2003 llegó al cargo con el tercer grupo de la cámara, gracias a un pacto con el PSOE.</p>
<p>Antes hubo años de inestabilidad: un presidente elegido en las listas de AP que acabó enfrentado a su partido, una moción de censura y una condena del Tribunal Supremo. En las generales, en cambio, Cantabria ha sido mucho más previsible: el PP ha sido el más votado en diez de las dieciséis, también en 2004 y 2008, cuando ganaba Zapatero. Y es una de las comunidades que más votan.</p>
<p>Este reportaje recorre esa historia con los resultados de las once autonómicas, de 1983 a 2023, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Los años de Hormaechea</h2>
<p>El Estatuto de Autonomía de Cantabria se aprobó el 30 de diciembre de 1981, y el primer parlamento, entonces llamado Asamblea Regional, se votó en mayo de 1983. La Coalición Popular sacó 18 de los 35 escaños, la mayoría absoluta, y José Antonio Rodríguez fue investido con sus votos. En 1984 le relevó Ángel Díaz de Entresotos, del mismo grupo.</p>
{F.aut('Escaños en el Parlamento de Cantabria, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas.')}
<p>En 1987, con 39 diputados en juego, AP se quedó en 19, a uno de la mayoría, y fue investido Juan Hormaechea, que se había presentado como independiente en las listas de AP. La legislatura fue muy agitada, según la <a href="{W87}">crónica de aquellas elecciones</a>: en 1989 el PP pidió su dimisión, Hormaechea siguió con un gobierno de independientes y en diciembre de 1990 una moción de censura del PP, el PSOE, el PRC y el CDS le sustituyó por el socialista Jaime Blanco.</p>
<p>Hormaechea volvió en 1991 con su propio partido, la Unión para el Progreso de Cantabria (UPCA). El PSOE fue el más votado, con 16 escaños, pero UPCA sacó 15 y, con el apoyo de los 6 del PP, Hormaechea fue investido de nuevo. En noviembre de 1994 una sentencia firme del Tribunal Supremo le condenó a prisión e inhabilitación; dimitió, pero ningún otro candidato consiguió la mayoría y siguió en funciones hasta julio de 1995, según la <a href="{W91}">crónica de 1991</a>. Uno de los candidatos que lo intentó, en diciembre de 1994, fue Revilla, con el apoyo del PSOE, según Historia Electoral.</p>
{presidentes([('1982', '1984', 'José Antonio Rodríguez', 'UCD, luego Coalición Popular'), ('1984', '1987', 'Ángel Díaz de Entresotos', 'AP'), ('1987', '1990', 'Juan Hormaechea', 'Independiente en las listas de AP'),
              ('1990', '1991', 'Jaime Blanco', 'PSOE'), ('1991', '1995', 'Juan Hormaechea', 'UPCA'), ('1995', '2003', 'José Joaquín Martínez Sieso', 'PP'),
              ('2003', '2011', 'Miguel Ángel Revilla', 'PRC'), ('2011', '2015', 'Ignacio Diego', 'PP'), ('2015', '2023', 'Miguel Ángel Revilla', 'PRC'),
              ('2023', 'hoy', 'María José Sáenz de Buruaga', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de Cantabria desde 1982. José Antonio Rodríguez presidió el ente preautonómico y, tras las elecciones de 1983, el primer Gobierno autonómico. Fuente: <a href="https://www.historiaelectoral.com/acantabria.html">Historia Electoral</a>.</p>

<h2>Revilla: presidente desde el tercer puesto</h2>
<p>En 1995 el PP ganó con 13 escaños y José Joaquín Martínez Sieso fue investido con el apoyo del PRC, que tenía 6, según la <a href="{W95}">crónica de aquellas elecciones</a>. Repitieron la fórmula en 1999. En 2003 el PP volvió a ser el más votado, con el 43,4% y 18 escaños, y el PRC subió a 8. Revilla exigió la presidencia para renovar el pacto; el PP se negó y el PSOE, segundo con 13 diputados, aceptó, según la <a href="{W03}">crónica de 2003</a>. Revilla fue investido con 21 votos, al frente del partido con menos escaños de la cámara.</p>
<p>Desde entonces el PRC no dejó de crecer: 12 escaños en 2007, 2011 y 2015, y 14 en 2019. Con el PSOE gobernó hasta 2011, cuando el PP de Ignacio Diego logró la mayoría absoluta con 20 diputados. En 2015, con el PP primero otra vez pero sin mayoría, regionalistas y socialistas volvieron a sumar. Y en 2019 el PRC fue, por primera vez, el más votado, con el 37,6%. El jurista Luis Martín Rebollo, de la Universidad de Cantabria, lo describió así:</p>
{F.cita('convirtiéndose así, por vez primera, en el partido más votado de la Comunidad, con 122.000 votos, 45.000 más que el segundo, el PP, que había sido tradicionalmente hasta el momento el partido ganador', 'Luis Martín Rebollo', 'Universidad de Cantabria, en el Informe Comunidades Autónomas 2019 del Instituto de Derecho Público', IDP19, 'IDP Barcelona', '2020')}

<h2>2023: el PP gobierna solo y en minoría</h2>
<p>Cuatro años después, el PRC bajó de 14 a 8 escaños, los mismos que el PSOE, y el PP de María José Sáenz de Buruaga ganó con 15, a tres de la mayoría absoluta. Buruaga fue investida el 3 de julio de 2023, en segunda votación, con los votos de su grupo y la abstención del PRC, según la <a href="{W23}">crónica de aquellas elecciones</a>. La jurista Ana Sánchez Lamelas, de la Universidad de Cantabria, explicaba lo que salía de aquel resultado:</p>
{F.cita('un gobierno del PP sin mayoría absoluta y sin pactos de gobierno ni de gobernabilidad, lo que le exige alcanzar pactos concretos en el Parlamento a la hora de adoptar las reformas legales que pretende', 'Ana Sánchez Lamelas', 'Universidad de Cantabria, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>Esa debilidad se vio en noviembre de 2025, cuando PRC, PSOE y Vox devolvieron al Gobierno el proyecto de presupuestos para 2026, según <a href="{TUMBA}">elDiario.es</a>. Tres días después, Buruaga criticó a la oposición:</p>
{F.cita('Los cántabros quieren soluciones, respuestas y políticas útiles para resolver sus problemas, no tacticismo electoral', 'María José Sáenz de Buruaga', 'presidenta de Cantabria', BURUAGA, 'elDiario.es (Europa Press)', '27 de noviembre de 2025')}
<p>Las cuentas salieron adelante en abril de 2026, con los votos del PP y del PRC, que habían firmado un preacuerdo en marzo, según <a href="{PRESU26}">Redacción Médica</a>. Las próximas autonómicas tocan en mayo de 2027.</p>

<h2>En las generales: el PP, diez de dieciséis</h2>
<p>En las generales, Cantabria votó a UCD en 1977 y 1979 y al PSOE en 1982, 1986 y 1989. Desde 1993 el PP ha sido el más votado en todas menos una, la de abril de 2019. Y lo fue también cuando España votaba al PSOE: en 1993, por menos de una décima (37,6% frente a 37,5%), en 2004, en 2008 y en noviembre de 2019. En 2000 llegó al 58,5%, su mejor resultado.</p>
{F.gen('PSOE, PP y los demás en Cantabria', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>Desde 1982, el PP cántabro ha quedado por encima de su media en España en todas las generales. El PRC, que va en «Otras listas», se presentó por primera vez a las generales en abril de 2019 y logró un diputado, que repitió en noviembre con más votos, según Martín Rebollo. En 2023 no se presentó.</p>
{F.esp('PSOE y PP en Cantabria y en España', 'PSOE y AP/PP en Cantabria y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en Cantabria', 'Lista más votada en las generales de 1977 a 2023 en la circunscripción de Cantabria.')}
<p>Santander, con 135.000 electores, votó al PSOE en 1982 y 1986 y desde 1989 ha votado al PP en todas las generales menos en abril de 2019. La izquierda es más fuerte en la cuenca del Besaya: Torrelavega ha votado al PSOE en 11 de las 16 generales, y Los Corrales de Buelna, en 12.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios cántabros con más electores.')}
<p>El mapa municipal confirma el dominio del PP. En 1977 UCD ganó en 90 de los 102 municipios y el PSOE, en 12, entre ellos Torrelavega, Castro-Urdiales y Los Corrales de Buelna. En 2000 y en 2011 el PP fue el más votado en 100 de los 102. Las dos elecciones de 2019 rompieron ese mapa: en abril el PSOE ganó en 40 municipios, Santander incluido, y el PRC en 17; en noviembre, el PRC fue el más votado en 31, sobre todo pueblos pequeños de los valles del interior. En 2023 el PP volvió a ganar en 85 y el PSOE, en 17, repartidos entre el eje del Besaya, de Torrelavega a Los Corrales, el oriente, como Castro-Urdiales, y el extremo occidental.</p>
{F.mapa('Cantabria, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Ninguno de los 102 municipios cántabros ha votado al mismo partido en las 16 generales.</p>

<h2>Votar más que la media</h2>
<p>Cantabria vota más que el conjunto de España: sin contar el voto exterior, su participación quedó por encima de la media en las 16 generales. En 2023 fue la más alta de todas las comunidades, el 75,4%, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Cantabria y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Cantabria elige 5 diputados en una sola circunscripción. En 2023 fueron 2 para el PP, 2 para el PSOE y 1 para Vox, según los <a href="{G23}">resultados oficiales</a>. El 29 de noviembre dirá si el PP mantiene la ventaja de 2023, cuando sacó nueve puntos más que en el conjunto de España, y si Cantabria vuelve a ser la comunidad que más vota.</p>
"""


PIEZA = dict(
    cc='cantabria', slug='cantabria-historia-electoral', lugar='Cantabria', corto='Cantabria en las urnas',
    titulo='El PP ha ganado nueve de las once autonómicas en Cantabria, pero Revilla, del PRC, la presidió dieciséis años',
    dek='Revilla llegó al Gobierno en 2003 desde el tercer puesto, con el apoyo del PSOE, y solo ganó unas elecciones, las de 2019. '
        'En las generales, el PP ha sido el más votado diez veces, también en 2004 y 2008. Y Cantabria vota más que la media española.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PP ha sido el más votado en nueve de las once autonómicas cántabras, pero Revilla, del PRC, presidió Cantabria de 2003 a 2011 y de 2015 a 2023. En las generales, el PP ganó diez de dieciséis, y la participación supera siempre la media.',
    compara='Las 11 elecciones al Parlamento de Cantabria (1983-2023) y las 16 generales (1977-2023) en Cantabria, por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('acantabria', 'Cantabria'),
                               (IDP19, 'Luis Martín Rebollo, «Cantabria», Informe Comunidades Autónomas 2019, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP23, 'Ana Sánchez Lamelas, «Cantabria», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (TUMBA, 'elDiario.es, «La oposición en Cantabria tumba el Presupuesto del PP…» (24-11-2025)'),
                               (BURUAGA, 'elDiario.es / Europa Press, «Buruaga: “Habrá otro presupuesto si alguien hace propuestas para que lo haya”» (27-11-2025)'),
                               (PRESU26, 'Redacción Médica, aprobación del presupuesto de Cantabria para 2026 (27-4-2026)'),
                               (W87, 'Wikipedia, Elecciones a la Asamblea Regional de Cantabria de 1987'),
                               (W91, 'Wikipedia, Elecciones a la Asamblea Regional de Cantabria de 1991'),
                               (W95, 'Wikipedia, Elecciones a la Asamblea Regional de Cantabria de 1995'),
                               (W03, 'Wikipedia, Elecciones al Parlamento de Cantabria de 2003'),
                               (W23, 'Wikipedia, Elecciones al Parlamento de Cantabria de 2023'),
                               (G23, 'Wikipedia, Elecciones generales de España de 2023 (escaños por circunscripción)')],
    enlaces=[],
)
