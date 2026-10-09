"""La Rioja: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente

IDP19 = 'https://idpbarcelona.net/docs/public/iccaa/2019/larioja_2019.pdf'
IDP23 = 'https://idpbarcelona.net/docs/public/iccaa/2023/larioja_2023.pdf'
ROMERO = 'https://www.publico.es/politica/podemos-e-iu-presidenta-rioja-socialista-concha-andreu-acaban-24-anos-gobiernos-pp.html'
HE = 'https://www.historiaelectoral.com/arioja.html'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">La Rioja es la comunidad de las mayorías absolutas. En siete de sus once elecciones autonómicas, un solo partido sacó más de la mitad de los escaños: el PSOE en 1983 y el PP en 1995, 1999, 2003, 2007, 2011 y 2023. El PP gobernó 24 años seguidos, de 1995 a 2019, veinte de ellos con Pedro Sanz de presidente.</p>
<p>En las generales, La Rioja es también una de las comunidades que más votan: su participación ha quedado por encima de la media española en las dieciséis elecciones desde 1977. Y el PP ha sido la lista más votada en todas desde 1989, salvo las dos de 2019, aunque en cuatro de ellas España votó al PSOE.</p>
<p>Este reportaje recorre esa historia con los resultados de las once elecciones al Parlamento de La Rioja, de 1983 a 2023, y de las dieciséis generales, municipio a municipio.</p>

<h2>Un parlamento pequeño</h2>
<p>El Parlamento de La Rioja tiene 33 diputados (35 en la primera legislatura) y la mayoría absoluta está en 17. El Partido Riojano, regionalista, tuvo dos escaños en las ocho primeras elecciones, de 1983 a 2011, y desde 2015 se ha quedado fuera, por debajo del 5% que exige la ley electoral riojana para entrar.</p>
{F.aut('Escaños en el Parlamento de La Rioja, 1983-2023', 'Diputados de cada partido en las once elecciones autonómicas.')}
<p>El socialista José María de Miguel fue el primer presidente elegido, en 1983, con mayoría absoluta. En 1987 el PSOE volvió a ser el más votado, con 14 escaños, pero Alianza Popular, con 13, sumó a los dos diputados del Partido Riojano Progresista y Joaquín Espert fue investido en segunda votación, con la abstención del CDS. Aquella coalición se rompió en enero de 1989.</p>
<p>Un año después llegó la moción de censura. Según <a href="{HE}">Historia Electoral</a>, el 8 de enero de 1990 el socialista José Ignacio Pérez Sáenz fue elegido con 17 votos, los 14 del PSOE y los 3 del grupo riojano progresista, que había sumado a dos diputados salidos del CDS. Los dos diputados que quedaban en el CDS se ausentaron en protesta contra el transfuguismo. En 1991 Pérez Sáenz revalidó el cargo con el Partido Riojano.</p>
{presidentes([('1983', '1987', 'José María de Miguel', 'PSOE'), ('1987', '1990', 'Joaquín Espert', 'AP / PP'), ('1990', '1995', 'José Ignacio Pérez Sáenz', 'PSOE'),
              ('1995', '2015', 'Pedro Sanz', 'PP'), ('2015', '2019', 'José Ignacio Ceniceros', 'PP'), ('2019', '2023', 'Concha Andreu', 'PSOE'),
              ('2023', 'hoy', 'Gonzalo Capellán', 'PP')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Presidentes de La Rioja desde la primera legislatura (1983). Antes hubo dos presidentes preautonómicos y provisionales. Fuente: <a href="{HE}">Historia Electoral</a>.</p>

<h2>Los veinte años de Pedro Sanz</h2>
<p>En 1995 el PP de Pedro Sanz ganó con 17 escaños y el 49,4% de los votos, y desde entonces encadenó cinco mayorías absolutas. La mayor fue la última, en 2011: 20 diputados y el 52,0%. En 2015 el PP bajó a 15 y necesitó a Ciudadanos, que entró con 4. Ciudadanos se abstuvo en la investidura con una condición, que Sanz no fuera el candidato, y el presidente fue José Ignacio Ceniceros, hasta entonces presidente del Parlamento.</p>
<p>En 2019 el PSOE de Concha Andreu ganó con 15 escaños, su primera victoria desde 1991. La investidura fracasó en julio: Andreu solo tuvo 16 votos, los suyos y el de Izquierda Unida, porque la única diputada de Podemos, Raquel Romero, votó en contra. En agosto, tras un acuerdo de gobierno, fue investida con 17. Romero abrió así su intervención:</p>
{F.cita('Ya era hora, si me permiten el desahogo, tras 24 años por fin nuestra tierra va a conocer la alternancia', 'Raquel Romero', 'diputada de Podemos en el Parlamento de La Rioja, en la investidura de Concha Andreu', ROMERO, 'Público', '27 de agosto de 2019')}
<p>La constitucionalista Amelia Pascual Medrano subrayaba el carácter de aquella investidura:</p>
{F.cita('Es la primera Presidenta y primera candidata socialista que logra volver a ocupar el Gobierno riojano, tras 24 años del PSOE en la oposición', 'Amelia Pascual Medrano', 'Universidad de La Rioja, en el Informe Comunidades Autónomas 2019 del Instituto de Derecho Público', IDP19, 'IDP Barcelona', '2020')}
<p>El cambio duró una legislatura. En mayo de 2023 el PP de Gonzalo Capellán recuperó la mayoría absoluta, con 17 escaños y el 45,4%, y Vox entró por primera vez, con 2. Capellán fue investido solo con los votos de su grupo. Las próximas autonómicas tocan en mayo de 2027.</p>

<h2>En las generales: el PP desde 1989</h2>
<p>UCD ganó en La Rioja las dos primeras generales, con el 41,1% y el 48,3%, y el PSOE las de 1982 y 1986. En 1986 el PSOE sacó en La Rioja el 44,3%, el mismo porcentaje que en el conjunto de España. Desde 1989 el PP ha sido la lista más votada en todas salvo las dos de 2019, como recuerda Pascual Medrano en su <a href="{IDP23}">informe de 2023</a>. Su techo fue el 55,6% de 2011.</p>
{F.gen('PP, PSOE y los demás en La Rioja', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>Por eso La Rioja se separó de España cuatro veces: en 1989 y 1993, y en 2004 y 2008, el PP ganó allí mientras el PSOE ganaba en el país. En las otras doce, el más votado en La Rioja fue el mismo que en el conjunto de España. En abril de 2019 el PSOE ganó con el 32,0%, y en noviembre, por seis décimas (35,2% frente a 34,6%).</p>
{F.esp('PSOE y PP en La Rioja y en España', 'PSOE y AP/PP en La Rioja y en el conjunto de España, en las generales.')}
{F.prov('Quién ganó en La Rioja', 'Lista más votada en las generales de 1977 a 2023.')}
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios riojanos con más electores.')}
<p>Logroño, con casi la mitad de los electores de la comunidad, ha votado lo mismo que La Rioja en las dieciséis generales. Santo Domingo de la Calzada ha votado al PP en todas desde 1982. Arnedo fue socialista de 1982 a 2008, y Haro fue la única de las diez ciudades más grandes donde el PSOE ganó en 2023.</p>
<p>En el mapa por municipios, AP y el PP han ganado en más pueblos que el PSOE en todas las generales desde 1982, también cuando el PSOE fue el más votado en el conjunto. En 1977 UCD ganó en 126 de los 174 municipios. En 1982, cuando el PSOE ganó en el conjunto, AP fue la lista más votada en 111 municipios y el PSOE en 56. El PP llegó a 163 en 2016. En abril de 2019 el reparto fue el más equilibrado: 98 municipios para el PP y 74 para el PSOE, más uno para Ciudadanos (Hornillos de Cameros) y otro para Vox (Torremontalbo). En 2023 el PP ganó en 140, el PSOE en 33 y Vox, otra vez, en Torremontalbo.</p>
{F.mapa('La Rioja, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Solo cinco de los 172 municipios con datos en todas las elecciones han votado siempre al mismo partido, y todos son muy pequeños: Igea, El Rasillo de Cameros y Villarroya, al PP, y Matute y Tobía, al PSOE.</p>

<h2>Votar más que la media</h2>
<p>Sin contar el voto exterior, La Rioja ha votado más que el conjunto de España en las dieciséis generales. En 2023 participó el 74,9% de su censo, frente al 70,4% del país.</p>
{F.part('Participación en las generales: La Rioja y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>La Rioja elige 4 diputados en una sola circunscripción. En 2023 se repartieron a partes iguales: 2 para el PP y 2 para el PSOE. El 29 de noviembre dirá si La Rioja vuelve a coincidir con el ganador de España, como en doce de las dieciséis generales.</p>
"""


PIEZA = dict(
    cc='la-rioja', slug='la-rioja-historia-electoral', lugar='La Rioja', corto='La Rioja en las urnas',
    titulo='La Rioja ha votado más que la media de España en las 16 generales, y el PP la gobernó 24 años seguidos',
    dek='Siete de las once elecciones riojanas dieron mayoría absoluta a un partido. Pedro Sanz encadenó cinco y Capellán la recuperó en 2023. '
        'En las generales, el PP es el más votado desde 1989 salvo en 2019.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='La Rioja ha dado mayoría absoluta a un partido en siete de sus once elecciones autonómicas, y el PP la gobernó de 1995 a 2019. En las generales vota más que la media y el PP es el más votado desde 1989, salvo en 2019.',
    compara='Las 11 elecciones al Parlamento de La Rioja (1983-2023) y las 16 generales (1977-2023) en La Rioja, por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('arioja', 'La Rioja'),
                               (IDP19, 'Amelia Pascual Medrano, «La Rioja», Informe Comunidades Autónomas 2019, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP23, 'Amelia Pascual Medrano, «La Rioja», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (ROMERO, 'Público, «Podemos e IU hacen presidenta de La Rioja a la socialista Concha Andreu y acaban 24 años de gobiernos del PP» (27-8-2019)')],
    enlaces=[],
)
