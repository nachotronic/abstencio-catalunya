"""Extremadura: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente, wiki

IDP11 = 'https://www.idpbarcelona.net/docs/public/iccaa/2011/extremadura_2011.pdf'
IDP23 = 'https://www.idpbarcelona.net/docs/public/iccaa/2023/extremadura_2023.pdf'
GUARDIOLA23 = 'https://www.elespanol.com/espana/politica/20230620/guardiola-pp-fracasar-vox-extremadura-iremos-elecciones/772922884_0.html'
PACTO23 = 'https://elpais.com/espana/elecciones-autonomicas/2023-06-30/lea-el-texto-de-la-alianza-de-pp-y-vox-en-extremadura.html'
ADELANTO25 = 'https://www.eldiario.es/extremadura/politica/guardiola-adelanta-elecciones-extremadura-seran-21-diciembre_1_12717035.html'
FALLIDA26 = 'https://www.vozpopuli.com/espana/extremadura/maria-guardiola-no-supera-la-segunda-votacion-de-investidura.html'
INVEST26 = 'https://www.vozpopuli.com/espana/extremadura/maria-guardiola-investida-presidenta-con-el-acuerdo-de-coalicion-con-vox-para-gobernar-extremadura.html'
GEN23 = 'https://www.elsaltodiario.com/elecciones/23-j-extremadura-psoe-es-partido-votado-derechas-suman-mayoria'
BOE26 = 'https://www.boe.es/boe/dias/2026/10/06/pdfs/BOE-A-2026-20742.pdf'
W25 = wiki('Elecciones a la Asamblea de Extremadura de 2025')


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">Durante 28 años, de 1983 a 2011, Extremadura solo tuvo presidentes socialistas, y Juan Carlos Rodríguez Ibarra fue uno de ellos durante 24. El PSOE ha gobernado la Junta en nueve de las doce legislaturas y fue el partido más votado en diez de las doce elecciones a la Asamblea, la última en 2023. Pero aquel año perdió el Gobierno, y en diciembre de 2025 se hundió hasta el 25,8% de los votos, su peor resultado.</p>
<p>Hoy preside la Junta María Guardiola, del PP, que en abril de 2026 fue investida por segunda vez con los votos de Vox, después de fracasar en marzo. En las generales, en cambio, Extremadura sigue siendo una de las comunidades más socialistas: el PSOE ganó allí en 2023, como en 11 de las 16 generales desde 1977.</p>
<p>Este reportaje recorre esa historia con los resultados de las doce elecciones autonómicas, de 1983 a 2025, y de las dieciséis generales, municipio a municipio.</p>

<h2>Los 24 años de Ibarra</h2>
<p>El Estatuto de Autonomía de Extremadura se aprobó en febrero de 1983, y la primera Asamblea se votó en mayo. El PSOE sacó el 53% de los votos y 35 de los 65 escaños, y Rodríguez Ibarra, que ya presidía la Junta preautonómica, fue investido con los votos socialistas y los del PCE. En las siete elecciones de 1983 a 2007, los socialistas tuvieron mayoría absoluta en seis; la más amplia, la de 1991, con el 54,3% y 39 escaños, según Historia Electoral. La excepción fue 1995, cuando se quedaron en 31 y gobernaron en minoría.</p>
{F.aut('Escaños en la Asamblea de Extremadura, 1983-2025', 'Diputados de cada partido en las doce elecciones autonómicas.')}
<p>En los primeros años hubo hueco para un partido regionalista, Extremadura Unida, que sacó 6 escaños en 1983 y 4 en 1987, y para el CDS, con 8 en 1987. De 1999 a 2011, la Asamblea fue cosa de PSOE, PP e Izquierda Unida, que en 2007 se quedó sin escaños. Ibarra dejó la presidencia en 2007 y le sucedió Guillermo Fernández Vara, que ganó aquellas elecciones con 38 escaños.</p>
{presidentes([('1983', '2007', 'Juan Carlos Rodríguez Ibarra', 'PSOE'), ('2007', '2011', 'Guillermo Fernández Vara', 'PSOE'), ('2011', '2015', 'José Antonio Monago', 'PP'),
              ('2015', '2023', 'Guillermo Fernández Vara', 'PSOE'), ('2023', 'hoy', 'María Guardiola', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de la Junta de Extremadura desde el Estatuto de 1983. Rodríguez Ibarra ya presidía la Junta preautonómica desde diciembre de 1982, después de Luis Ramallo y Manuel Bermejo. Fuente: <a href="https://www.historiaelectoral.com/aextremadura.html">Historia Electoral</a>.</p>

<h2>2011: el primer Gobierno del PP</h2>
<p>En mayo de 2011, el PP de José Antonio Monago ganó por primera vez unas autonómicas en Extremadura: el 46,1% de los votos y 32 escaños, uno menos de la mayoría absoluta. El PSOE se quedó en 30, e Izquierda Unida, con 3, tuvo la llave. El jurista Vicente Álvarez García, de la Universidad de Extremadura, lo contaba así:</p>
{F.cita('La formación del nuevo Gobierno ha sido posible gracias a la abstención de IU, que rechazó expresamente cualquier apoyo a un ejecutivo socialista capitaneado por el hasta entonces Presidente de la Junta de Extremadura, don Guillermo Fernández Vara', 'Vicente Álvarez García', 'Universidad de Extremadura, en el Informe Comunidades Autónomas 2011 del Instituto de Derecho Público', IDP11, 'IDP Barcelona', '2012')}
<p>Según el mismo informe, IU tomó esa decisión siguiendo a sus bases y en contra de su dirección federal. Monago fue investido el 5 de julio con los 32 votos del PP. Cuatro años después, en 2015, el PSOE volvió a ganar con 30 escaños y Fernández Vara fue investido con el apoyo de los 6 diputados de Podemos. En 2019 recuperó la mayoría absoluta, con 34.</p>

<h2>2023 y 2025: el PP con Vox</h2>
<p>En mayo de 2023, PSOE y PP empataron a 28 escaños, aunque los socialistas fueron los más votados, con el 39,9% frente al 38,8%. Vox entraba por primera vez en la Asamblea, con 5 diputados. Flor Arias Aparicio, de la Universidad de Extremadura, habla en su <a href="{IDP23}">informe de aquel año</a> de un «ajustado resultado» que abrió un periodo de negociaciones. La candidata del PP llegó a descartar a Vox en público:</p>
{F.cita('No puedo dejar entrar al Gobierno a aquellos que niegan la violencia machista', 'María Guardiola', 'candidata del PP a la Presidencia de la Junta', GUARDIOLA23, 'El Español', '20 de junio de 2023')}
<p>Diez días después, el 30 de junio, PP y Vox firmaron un <a href="{PACTO23}">acuerdo de gobierno</a> que daba a Vox una consejería, y el 14 de julio Guardiola fue investida con 33 votos, los de PP y Vox, frente a 32. Vox salió de aquel Gobierno en julio de 2024 y, sin acuerdo para los presupuestos, Guardiola <a href="{ADELANTO25}">adelantó las elecciones</a> al 21 de diciembre de 2025.</p>
<p>El PP ganó con el 43,1% y 29 escaños, uno más que en 2023 pero lejos de los 33 de la mayoría. El PSOE de Miguel Ángel Gallardo cayó a 18, con el 25,8%, su peor resultado en unas autonómicas extremeñas. Vox pasó de 5 a 11, y Unidas por Extremadura, de 4 a 7, el mayor número de escaños que ha tenido nunca la izquierda a la izquierda del PSOE en la Asamblea. Guardiola se presentó a la investidura sin acuerdo con Vox y perdió las dos votaciones, el 4 y el 6 de marzo de 2026: 29 votos a favor y 36 en contra, los de PSOE, Vox y Unidas, según <a href="{FALLIDA26}">Vozpópuli</a>. El 22 de abril, tras pactar un Gobierno de coalición, fue investida con 40 votos, los del PP y Vox, cuyo líder regional, Óscar Fernández, pasó a ser vicepresidente de la Junta, según <a href="{INVEST26}">la crónica de la investidura</a>.</p>

<h2>En las generales: la comunidad más socialista</h2>
<p>En las generales, Extremadura vota al PSOE más que casi nadie. UCD ganó en 1977 y 1979, pero desde 1982 el PSOE ha sido la lista más votada en 11 de las 14 generales; el PP solo ganó en 2000, 2011 y 2016. En tres ocasiones, 1996, 2015 y 2023, el PSOE ganó en Extremadura mientras el PP ganaba en el conjunto de España. En 2023 la diferencia fue de un punto: 39,4% frente a 38,2%.</p>
{F.gen('UCD, PSOE, PP y los demás en Extremadura', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>El PSOE ha sacado en Extremadura más porcentaje de voto que en el conjunto de España en las 16 generales. Su mejor resultado fue el de 1986, con el 56,2%, y la mayor ventaja sobre su media nacional, la de 1989, de más de catorce puntos.</p>
{F.esp('El PSOE extremeño, siempre por encima del de España', 'PSOE y AP/PP en Extremadura y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en Badajoz y en Cáceres', 'Lista más votada en las generales de 1977 a 2023.')}
<p>Las dos provincias han votado casi siempre igual. Badajoz votó al PSOE en 11 generales y al PP en 3: 2000, 2011 y 2016. Cáceres, al PSOE en 10 y al PP en 4, porque en 2015 se separó de Badajoz y votó al PP.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios con más electores.')}
<p>Las dos ciudades más grandes no se parecen a su comunidad. Badajoz ha votado al PP en todas las generales desde 1993 menos en abril de 2019, y Cáceres, en todas menos en las dos de 2019. Mérida, la capital, es más socialista: el PP solo ganó allí en 1996, 2000, 2011 y 2016. En 2023, el PSOE ganó en Extremadura, pero el PP fue el más votado en seis de sus diez ciudades más grandes; el PSOE se quedó con Mérida, Villanueva de la Serena, Zafra y Montijo.</p>
<p>El mapa municipal ayuda a entenderlo: el PSOE gana en más pueblos. En 1977, UCD fue la lista más votada en 296 municipios y el PSOE en 77; en 1982 el PSOE pasó a 326. En 2000 y en 2016, dos de los tres años en que el PP ganó en la comunidad, el PSOE siguió siendo el más votado en más municipios (241 frente a 141, y 209 frente a 179). Solo en 2011 el PP ganó en más pueblos que el PSOE, 240 frente a 145. En abril de 2019 el PSOE fue primero en 357 de los 388 municipios, y en 2023, en 276; el PP, en 111, y Vox, en uno. Las manchas azules más grandes de ese año son términos municipales muy extensos, como los de Cáceres y Badajoz.</p>
{F.mapa('Extremadura, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>De los 379 municipios con datos en las 16 generales, 31 han votado siempre al PSOE, 21 de ellos en la provincia de Badajoz. El mayor es Cabeza del Buey, seguido de Quintana de la Serena y Valverde de Leganés. Ninguno ha votado siempre al PP.</p>

<h2>Votar algo más que la media</h2>
<p>Extremadura suele votar algo más que el conjunto de España: sin contar el voto exterior, su participación superó la media en 13 de las 16 generales. Quedó por debajo en 1977, en 1982 y en noviembre de 2019. En 2023 fue del 73,7%, frente al 70,4% del país.</p>
{F.part('Participación en las generales: Extremadura y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>Extremadura elige 9 diputados, los mismos que en 2023, según el <a href="{BOE26}">decreto de convocatoria</a>: 5 por Badajoz y 4 por Cáceres. En 2023 fueron 4 para el PSOE, 4 para el PP y 1 para Vox, <a href="{GEN23}">según El Salto</a>. El 29 de noviembre dirá si el PSOE conserva en las generales la primera posición que perdió en las autonómicas de 2025, y cuánto suma Vox siete meses después de entrar en el Gobierno de Guardiola.</p>
"""


PIEZA = dict(
    cc='extremadura', slug='extremadura-historia-electoral', lugar='Extremadura', corto='Extremadura en las urnas',
    titulo='El PSOE ha ganado 11 de las 16 generales en Extremadura y gobernó la Junta nueve legislaturas; en 2025 cayó al 25,8%',
    dek='Rodríguez Ibarra presidió la Junta 24 años. Desde 2023 gobierna el PP de María Guardiola, investida en abril de 2026 con los votos de Vox. '
        'En las generales, el PSOE siempre ha sacado en Extremadura más que en el conjunto de España.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PSOE gobernó Extremadura en nueve de doce legislaturas y ha ganado allí 11 de las 16 generales. En diciembre de 2025 cayó al 25,8%, su peor resultado, y Guardiola gobierna con Vox.',
    compara='Las 12 elecciones a la Asamblea de Extremadura (1983-2025) y las 16 generales (1977-2023) en Extremadura, por provincia y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('aextremadura', 'Extremadura'),
                               (IDP11, 'Vicente Álvarez García, «Extremadura», Informe Comunidades Autónomas 2011, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP23, 'Flor Arias Aparicio, «Extremadura», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (GUARDIOLA23, 'El Español, «Guardiola (PP), tras fracasar el pacto con Vox en Extremadura: "Iremos a elecciones si hay que ir"» (20-6-2023)'),
                               (PACTO23, 'El País, texto del acuerdo de PP y Vox en Extremadura (30-6-2023)'),
                               (ADELANTO25, 'elDiario.es, «Guardiola adelanta las elecciones en Extremadura al 21 de diciembre» (27-10-2025)'),
                               (FALLIDA26, 'Vozpópuli, «María Guardiola no supera la segunda votación de investidura» (6-3-2026)'),
                               (INVEST26, 'Vozpópuli, investidura de María Guardiola con el acuerdo de coalición con Vox (22-4-2026)'),
                               (GEN23, 'El Salto, «23J en Extremadura: el PSOE es el partido más votado, pero las derechas suman mayoría» (2023)'),
                               (BOE26, 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución de las Cortes y convocatoria de elecciones (6-10-2026)'),
                               (W25, 'Wikipedia, Elecciones a la Asamblea de Extremadura de 2025')],
    enlaces=[],
)
