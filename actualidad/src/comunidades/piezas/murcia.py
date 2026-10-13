"""Región de Murcia: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP15 = 'https://www.idpbarcelona.net/docs/public/iccaa/2015/murcia_2015.pdf'
IDP17 = 'https://www.idpbarcelona.net/docs/public/iccaa/2017/murcia_2017.pdf'
IDP21 = 'https://www.idpbarcelona.net/docs/public/iccaa/2021/murcia_2021.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/murcia_2023.pdf'
MIRAS = 'https://www.infobae.com/espana/2023/09/06/lopez-miras-en-su-sesion-de-investidura-hoy-sigo-pensando-que-el-gobierno-en-solitario-era-lo-mas-adecuado/'
VOX24 = 'https://valenciaplaza.com/valenciaplaza/mirasdejaravacialavicepresidenciadelgobiernodelaregiontraslasalidadevox'
VOX26 = 'https://www.elespanol.com/espana/murcia/20260418/lopez-miras-descarta-negociar-presupuestos-murcia-antelo-martinez-dejar-vox-pp-pacta-partidos/1003744212311_0.html'
BOE26 = 'https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742'
W83 = wiki('Elecciones a la Asamblea Regional de Murcia de 1983')
W19 = wiki('Elecciones a la Asamblea Regional de Murcia de 2019')
W23 = wiki('Elecciones a la Asamblea Regional de Murcia de 2023')
WG23 = wiki('Elecciones generales de España de 2023')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">En noviembre de 2019, la Región de Murcia fue la única provincia de España donde Vox fue la lista más votada en unas generales, con el 28,2% de los votos. Fuera de ella, solo lo consiguió en la ciudad autónoma de Ceuta. Cuatro años antes, Murcia había sido la comunidad donde el PP sacaba sus mejores resultados: lo fue en las seis generales de 2000 a 2016, con un máximo del 64,9% en 2011.</p>
<p>En la Asamblea Regional, el PP gobierna desde 1995 sin interrupción. Ha tenido cinco mayorías absolutas seguidas con Ramón Luis Valcárcel, ha perdido una vez las elecciones, en 2019, y ha sobrevivido a una moción de censura. Desde 2019 su presidente, Fernando López Miras, necesita los votos de Vox. Antes, el PSOE gobernó los doce primeros años de la autonomía con mayoría absoluta.</p>
<p>Este reportaje recorre esa historia con los resultados de las once elecciones autonómicas, de 1983 a 2023, y de las dieciséis generales desde 1977, municipio a municipio.</p>

<h2>Doce años del PSOE, treinta y uno del PP</h2>
<p>El Estatuto de Autonomía de la Región de Murcia se aprobó el 9 de junio de 1982, y la primera Asamblea Regional se votó en mayo de 1983. El PSOE sacó el 52,2% de los votos y 26 de los 43 escaños, según la <a href="{W83}">crónica de aquellas elecciones</a>. Repitió mayoría absoluta en 1987 y en 1991, con 25 y 24 de los 45 escaños. Gobernaron tres presidentes socialistas: Andrés Hernández Ros, Carlos Collado y María Antonia Martínez.</p>
{F.aut('Escaños en la Asamblea Regional de Murcia, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas.')}
<p>En 1995 el PP de Ramón Luis Valcárcel ganó con el 52,4% y 26 escaños, y ya no dejó el Gobierno. Valcárcel encadenó cinco mayorías absolutas, cada una mayor que la anterior en votos: la última, en 2011, con el 58,8% y 33 de los 45 diputados. Ese año el PSOE se quedó en 11. En 2014 Valcárcel se fue al Parlamento Europeo y lo sustituyó Alberto Garre, como «solución transitoria», según el jurista Ignacio González García, de la Universidad de Murcia, en el <a href="{IDP15}">Informe Comunidades Autónomas 2015</a>.</p>
{presidentes([('1982', '1984', 'Andrés Hernández Ros', 'PSOE'), ('1984', '1993', 'Carlos Collado', 'PSOE'), ('1993', '1995', 'María Antonia Martínez', 'PSOE'),
              ('1995', '2014', 'Ramón Luis Valcárcel', 'PP'), ('2014', '2015', 'Alberto Garre', 'PP'), ('2015', '2017', 'Pedro Antonio Sánchez', 'PP'),
              ('2017', 'hoy', 'Fernando López Miras', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Región de Murcia desde el Estatuto de 1982. Hernández Ros ya presidía el Consejo Regional preautonómico desde 1979. Fuente: <a href="https://www.historiaelectoral.com/amurcia.html">Historia Electoral</a>.</p>

<h2>Del bipartidismo a los pactos</h2>
<p>En 2015 el PP bajó a 22 escaños, uno menos que la mayoría absoluta, y Pedro Antonio Sánchez fue investido con los votos de Ciudadanos. No terminó la legislatura. Según González García, en febrero de 2017 el Tribunal Superior de Justicia de Murcia lo declaró investigado por el caso del Auditorio de Puerto Lumbreras, de cuando era alcalde de esa localidad; Ciudadanos dio por roto el pacto y el PSOE registró una moción de censura. El 4 de abril Sánchez dimitió, antes de que se votara, «para evitar que el Partido Popular perdiera el Gobierno de la Región», escribe en el <a href="{IDP17}">informe de 2017</a>. Le sustituyó Fernando López Miras, entonces de 33 años, investido en segunda votación con la abstención de Ciudadanos.</p>
<p>En 2019 el PSOE ganó por primera vez desde 1991: el 32,5% de los votos frente al 32,4% del PP, y 17 escaños frente a 16. Pero PP, Ciudadanos (6) y Vox (4) sumaban mayoría. López Miras perdió dos votaciones de investidura a principios de julio, con Vox en contra, y salió elegido el 26 de julio, cuando los tres partidos cerraron un acuerdo, según la <a href="{W19}">crónica de aquella legislatura</a>.</p>
<p>En marzo de 2021 Ciudadanos, que gobernaba con el PP, presentó con el PSOE una moción de censura para hacer presidenta a su líder regional, Ana Martínez Vidal. Fracasó: tres de los seis diputados de Ciudadanos votaron en contra, junto al PP y a los diputados de Vox, y otro se abstuvo. El resultado fue de 21 votos a favor y 23 en contra. Su efecto llegó lejos, como recuerda González García:</p>
{F.cita('La Comunidad Autónoma de Murcia sufrió un auténtico terremoto político-institucional en el año 2021, con importantes consecuencias no sólo en la Región de Murcia sino también en otras Comunidades Autónomas (singularmente en la Comunidad Autónoma de Madrid)', 'Ignacio González García', 'Universidad de Murcia, en el Informe Comunidades Autónomas 2021 del Instituto de Derecho Público', IDP21, 'IDP Barcelona', '2022')}
<p>Ese mismo día, la presidenta madrileña, Isabel Díaz Ayuso, disolvió la Asamblea de Madrid y convocó elecciones.</p>

<h2>2023: el gobierno con Vox</h2>
<p>En mayo de 2023 el PP subió a 21 escaños, a dos de la mayoría absoluta, y Vox pasó de 4 a 9. López Miras quería gobernar solo con el apoyo externo de Vox, y Vox exigía entrar en el Gobierno. Perdió las dos votaciones de investidura de julio, con los 21 votos de su grupo frente a los 24 del resto, según la <a href="{W23}">crónica de aquellas elecciones</a>. En septiembre llegó el acuerdo:</p>
{F.cita('a tan sólo 6 días para que se pusiera en marcha el proceso de repetición electoral, el PP cedió y alcanzó con Vox un acuerdo de investidura y de Legislatura que incorporaba a Vox al Gobierno regional', 'Ignacio González García', 'Universidad de Murcia, en el Informe Comunidades Autónomas 2023 del Instituto de Derecho Público', IDP23, 'IDP Barcelona', '2024')}
<p>El 7 de septiembre López Miras fue investido con 30 votos, los del PP y Vox, que se quedó la vicepresidencia. En el debate dejó claro que no era la fórmula que había buscado:</p>
{F.cita('Hoy sigo pensando que el gobierno en solitario era lo más adecuado', 'Fernando López Miras', 'presidente de la Región de Murcia, en su debate de investidura', MIRAS, 'Infobae', '6 de septiembre de 2023')}
<p>La coalición duró menos de un año. En julio de 2024 Vox salió del Gobierno murciano, en una crisis con el PP que afectó a cinco gobiernos regionales; en Murcia, el motivo fue la acogida de 16 menores migrantes no acompañados llegados a Canarias. López Miras siguió en minoría y sin vicepresidencia, según <a href="{VOX24}">Valencia Plaza</a>. En abril de 2026, dos diputados de Vox, entre ellos su antiguo líder regional, José Ángel Antelo, pasaron al Grupo Mixto, y el grupo de Vox se quedó en 7, según <a href="{VOX26}">El Español</a>. Las próximas autonómicas son en mayo de 2027.</p>

<h2>En las generales: de rojo a azul</h2>
<p>En las generales, Murcia ha seguido una trayectoria parecida. UCD ganó en 1977, y el PSOE de 1979 a 1989, con un máximo del 51,2% en 1982. En 1993 el PP ya fue el más votado en Murcia, con el 47,7%, cuando en España volvía a ganar el PSOE. Desde entonces la región solo ha votado a otra lista en las dos elecciones de 2019: al PSOE en abril y a Vox en noviembre.</p>
{F.gen('PSOE, PP, Vox y los demás en la Región de Murcia', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>Entre 2000 y 2016, el PP sacó en Murcia su mejor porcentaje de todas las comunidades autónomas en las seis generales: el 58,9% en 2000 y el 64,9% en 2011, casi veinte puntos más que su media en España. Aquella ventaja se ve en el gráfico siguiente, donde la línea azul de Murcia va siempre por encima de la de España desde 1982.</p>
{F.esp('PSOE y PP en Murcia y en España', 'PSOE y AP/PP en la Región de Murcia y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en la Región de Murcia', 'Lista más votada en las generales de 1977 a 2023 en la provincia.')}
<p>En noviembre de 2019 Vox sacó el 28,2%, frente al 26,7% del PP y el 24,9% del PSOE. Fue la lista más votada en Cartagena, Molina de Segura, Alcantarilla, Cieza, Totana y San Javier, seis de las diez mayores ciudades. La capital, Murcia, votó al PP, como en todas las generales desde 1993. En 2023 el PP recuperó el primer puesto con el 41,5%, y Vox se quedó en el 22,0%.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios murcianos con más electores.')}
<p>El mapa municipal enseña lo rápido que cambió el voto. En 1982 el PSOE ganó en 37 de los 43 municipios con datos; solo se le escaparon seis, casi todos pequeños, en la vega del Segura, en el noreste y junto al Mar Menor. Desde 1993 el mapa se fue volviendo azul, y en 2011 el PP fue el más votado en los 45 municipios de la región. Noviembre de 2019 dejó el reparto más igualado de la serie: Vox ganó en 16 municipios, sobre todo en el Campo de Cartagena y la vega del Segura; el PSOE, en 15, casi todos en el oeste y el noroeste, y el PP, en 14, entre ellos la capital. En 2023 el PP volvió a ganar en 41 de los 45, y el PSOE, en 4.</p>
{F.mapa('Región de Murcia, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Ninguno de los 43 municipios con datos en las 16 elecciones ha votado siempre a la misma lista.</p>

<h2>Votar más que la media</h2>
<p>Murcia ha votado más que el conjunto de España en 14 de las 16 generales, sin contar el voto exterior. Las excepciones fueron las de 2015 y abril de 2019, por menos de medio punto. En 2023 participó el 70,8%, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Murcia y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>La Región de Murcia elige 10 diputados en una sola circunscripción, según el <a href="{BOE26}">decreto de convocatoria</a>. En 2023 fueron 4 para el PP, 3 para el PSOE, 2 para Vox y 1 para Sumar, según los resultados <a href="{WG23}">recogidos en Wikipedia</a>. El 29 de noviembre dirá si Vox se acerca otra vez al resultado de 2019, cuando fue el primero, y si el PP mantiene la ventaja que le dio 4 de los 10 escaños murcianos en 2023.</p>
"""


PIEZA = dict(
    cc='murcia', slug='murcia-historia-electoral', lugar='Región de Murcia', corto='Murcia en las urnas',
    titulo='Murcia es la única provincia donde Vox ha ganado unas generales; el PP la gobierna desde 1995 y ahora depende de Vox',
    dek='El PSOE gobernó los doce primeros años con mayoría absoluta. Valcárcel encadenó cinco mayorías del PP, y de 2000 a 2016 Murcia fue la comunidad donde el PP sacaba más votos. '
        'Desde 2019, López Miras ha perdido unas elecciones, sobrevivido a una moción de censura y gobernado con Vox.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='En noviembre de 2019, Murcia fue la única provincia de España donde Vox fue la lista más votada. El PP gobierna la región desde 1995; López Miras perdió en 2019, superó una moción de censura en 2021 y gobernó con Vox desde 2023.',
    compara='Las 11 elecciones a la Asamblea Regional de Murcia (1983-2023) y las 16 generales (1977-2023) en la Región de Murcia, por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('amurcia', 'la Región de Murcia'),
                               (IDP15, 'Ignacio González García, «Murcia», Informe Comunidades Autónomas 2015, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP17, 'Ignacio González García, «Murcia», Informe Comunidades Autónomas 2017, IDP Barcelona'),
                               (IDP21, 'Ignacio González García, «Murcia», Informe Comunidades Autónomas 2021, IDP Barcelona'),
                               (IDP23, 'Ignacio González García, «Murcia», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (MIRAS, 'Infobae, «López Miras en su sesión de investidura: “Hoy sigo pensando que el gobierno en solitario era lo más adecuado”» (6-9-2023)'),
                               (VOX24, 'Valencia Plaza, «Miras dejará vacía la vicepresidencia del Gobierno de la Región de Murcia tras la salida de Vox» (julio de 2024)'),
                               (VOX26, 'El Español, López Miras descarta negociar los presupuestos con Antelo y Martínez (18-4-2026)'),
                               (W83, 'Wikipedia, Elecciones a la Asamblea Regional de Murcia de 1983'),
                               (W19, 'Wikipedia, Elecciones a la Asamblea Regional de Murcia de 2019'),
                               (W23, 'Wikipedia, Elecciones a la Asamblea Regional de Murcia de 2023'),
                               (WG23, 'Wikipedia, Elecciones generales de España de 2023'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones')],
    enlaces=[],
)
