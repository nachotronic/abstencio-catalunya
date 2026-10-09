"""País Vasco: reportaje de la serie «Las comunidades en las urnas»."""
from comunes import FUENTES_COMUNES, PIE, LIMITES, he_fuente

IDP09 = 'https://idpbarcelona.net/docs/public/iccaa/2009/pvasco_2009.pdf'
IDP16 = 'https://idpbarcelona.net/docs/public/iccaa/2016/pvasco_2016.pdf'
IDP23 = 'https://idpbarcelona.net/docs/public/iccaa/2023/pvasco_2023.pdf'
LOPEZ = 'https://www.ambito.com/mundo/dia-historico-el-pais-vasco-un-socialista-asume-primera-vez-la-presidencia-n3558940'
HE = 'https://www.historiaelectoral.com/aeuzkadi.html'


def cuerpo(F, presidentes):
    return f"""
<p style="margin-top:1.4rem">El PNV ha sido la lista más votada en las trece elecciones al Parlamento Vasco celebradas desde 1980, y todos los lehendakaris de este periodo han sido suyos salvo uno: el socialista Patxi López, entre 2009 y 2012. Pero nunca ha tenido mayoría absoluta, y en 2024 EH Bildu lo igualó en escaños por primera vez, 27 a 27.</p>
<p>En las generales, el PNV también ha sido la primera lista en once de las dieciséis elecciones desde 1977. Las excepciones dicen mucho del País Vasco: el PSOE ganó en 1993, en 2008 y en 2023, y Podemos en 2015 y 2016. Los vascos, además, votan menos que el resto de España en las generales: su participación ha quedado por debajo de la media en las dieciséis.</p>
<p>Este reportaje recorre esa historia con los resultados de las trece elecciones autonómicas, de 1980 a 2024, y de las dieciséis generales, municipio a municipio.</p>

<h2>Trece elecciones y un solo ganador</h2>
<p>El Parlamento Vasco tiene 75 escaños, 25 por cada territorio histórico (Álava, Bizkaia y Gipuzkoa), aunque Bizkaia tiene más de tres veces y media los electores de Álava. En la primera legislatura, la de 1980, fueron 60. La mayoría absoluta exige 38 diputados, y nadie ha pasado de los 33 que sacó en 2001 la coalición del PNV con Eusko Alkartasuna.</p>
{F.aut('Escaños en el Parlamento Vasco, 1980-2024', 'Diputados de cada partido en las trece elecciones autonómicas. En 2001 y 2005 el PNV se presentó con EA; en 2020, el PP con Ciudadanos.')}
<p>Carlos Garaikoetxea fue el primer lehendakari, en 1980, en un gobierno solo del PNV. En 1986 el partido se partió: Garaikoetxea fundó Eusko Alkartasuna (EA), que sacó 13 escaños en su estreno. Ese año el PNV fue la lista más votada, con el 23,6% frente al 22,0% de los socialistas, pero el PSE tuvo más diputados, 19 frente a 17. José Antonio Ardanza, que había sustituido a Garaikoetxea en 1985, siguió de lehendakari en un gobierno de coalición con el PSE.</p>
<p>Desde entonces, el PNV ha gobernado con unos socios u otros: con el PSE la mayor parte de los años de Ardanza, con EA y Ezker Batua en los de Juan José Ibarretxe (1999-2009) y otra vez con el PSE, que votó la investidura de Urkullu en 2016 y tiene una vicepresidencia en el Gobierno de Pradales. Herri Batasuna y sus sucesoras tuvieron entre 7 y 14 escaños hasta 2001; en las elecciones de 2009 sus listas no pudieron presentarse.</p>
{presidentes([('1980', '1985', 'Carlos Garaikoetxea', 'PNV'), ('1985', '1999', 'José Antonio Ardanza', 'PNV'), ('1999', '2009', 'Juan José Ibarretxe', 'PNV'),
              ('2009', '2012', 'Patxi López', 'PSE-EE'), ('2012', '2024', 'Iñigo Urkullu', 'PNV'), ('2024', 'hoy', 'Imanol Pradales', 'PNV')])}
<p style="font-family:var(--ui);font-size:.9rem;color:var(--muted)">Lehendakaris desde el Estatuto de Gernika. Garaikoetxea ya presidía el Consejo General Vasco desde 1979. Fuente: <a href="{HE}">Historia Electoral</a>.</p>

<h2>2009: el único lehendakari no nacionalista</h2>
<p>En marzo de 2009 el PNV volvió a ganar, con 30 escaños. Las listas de la izquierda abertzale habían sido excluidas por el Tribunal Supremo, y Batasuna pidió el voto nulo: hubo 100.939 votos nulos, según <a href="{HE}">Historia Electoral</a>. El PSE sacó 25 escaños y el PP, 13, y entre los dos sumaban mayoría. El jurista José Manuel Castells lo contaba así:</p>
{F.cita('La diferencia de 5 escaños entre PNV y PSE quedaba compensada por los 13 escaños del PP, puesto que era un secreto a voces la confluencia de los dos partidos cara a la Presidencia del Gobierno', 'José Manuel Castells', 'Universidad del País Vasco, en el Informe Comunidades Autónomas 2009 del Instituto de Derecho Público', IDP09, 'IDP Barcelona', '2010')}
<p>Patxi López fue investido el 5 de mayo con 39 votos, los del PSE, el PP y el diputado de UPyD, y juró el cargo dos días después en la Casa de Juntas de Gernika con una fórmula nueva, sin la mención a Dios de sus predecesores del PNV, según la crónica de <a href="{LOPEZ}">Ámbito</a>:</p>
{F.cita('De pie, en tierra vasca, bajo el árbol de Gernika, ante vosotros representantes de la ciudadanía vasca, en recuerdo de los antepasados, prometo desde el respeto a la Ley, desempeñar fielmente mi cargo de lehendakari', 'Patxi López', 'al jurar como lehendakari en Gernika', LOPEZ, 'Ámbito', '7 de mayo de 2009')}
<p>Fue un paréntesis. En 2012 el PNV recuperó el Gobierno con Iñigo Urkullu, y EH Bildu, la nueva coalición de la izquierda abertzale, entró como segunda fuerza con 21 escaños. En 2016 Elkarrekin Podemos sacó 11, y en julio de 2020, con la pandemia, la participación cayó al 50,8%, la más baja de la serie según Historia Electoral. En abril de 2024, con Imanol Pradales de candidato, el PNV bajó a 27 escaños y EH Bildu subió a 27; el PNV sacó más votos (34,8% frente a 32,1%) y Pradales fue investido con los 39 votos del PNV y el PSE. Las próximas autonómicas tocan en 2028.</p>

<h2>En las generales: el PNV gana, pero menos</h2>
<p>En las generales, el PNV gana con porcentajes más bajos que en las autonómicas, y otros partidos llegan a ser primeros. El constitucionalista Alberto López Basaguren lo apuntaba en 2016, cuando Podemos fue la lista más votada en las generales y quedó tercero en las vascas tres meses después:</p>
{F.cita('Las elecciones al Parlamento Vasco volvieron a poner de relieve un comportamiento diferenciado respecto a las elecciones generales', 'Alberto López Basaguren', 'Universidad del País Vasco, en el Informe Comunidades Autónomas 2016 del Instituto de Derecho Público', IDP16, 'IDP Barcelona', '2017')}
{F.gen('PNV, PSOE, EH Bildu y los demás en el País Vasco', 'Porcentaje de voto en las 16 elecciones generales, sobre votos a candidaturas.')}
<p>El PSOE ganó en 1993 por medio punto y en 2008 con el 38,8%, su máximo. En 2015 y 2016, la lista de Podemos fue la primera, con el 26,2% y el 29,2%. En 2023 los tres primeros quedaron casi empatados: el PSE con el 25,4%, el PNV con el 24,2% y EH Bildu con el 24,1%. Del espacio de Herri Batasuna no hubo ninguna candidatura en las generales de 2000, 2004 y 2008; en 2011 Amaiur volvió con el 24,4%. Eusko Alkartasuna y Euskadiko Ezkerra van en «Otras listas»: por eso esa línea supera al PNV en 1989, aunque el PNV fue la lista más votada aquel año.</p>
{F.esp('PSOE y PP en el País Vasco y en España', 'PSOE y AP/PP en el País Vasco y en el conjunto de España, en las generales.')}
<p>El PP no ha ganado nunca en el conjunto del País Vasco. Su mejor resultado fue el 29,1% de 2000, cuando fue segundo, y desde 2019 no ha pasado del 12%.</p>
{F.prov('Quién ganó en cada territorio', 'Lista más votada en las generales de 1977 a 2023. Hasta 2000, la candidatura más votada; desde 2004, por familias.')}
<p>Los tres territorios votan distinto. Bizkaia ha votado al PNV en casi todas las generales; también en 2015, cuando la lista de Podemos se quedó cerca (28,1% frente a 26,3%). Álava es la más cambiante: UCD, PSOE, PP, Podemos, PNV y otra vez PSOE en 2023. Gipuzkoa es el único territorio donde ha ganado la izquierda abertzale: Herri Batasuna en 1989, Amaiur en 2011 y EH Bildu en 2023. López Basaguren hablaba ese año de «el diferente comportamiento de una parte significativa del electorado según el tipo de elección» en su <a href="{IDP23}">informe de 2023</a>.</p>
{F.ciu('Las diez mayores ciudades, elección a elección', 'Lista más votada en las generales en los diez municipios vascos con más electores.')}
<p>Entre las ciudades grandes hay de todo. Barakaldo, Irun y Portugalete han votado al PSOE en todas las generales salvo en 2015 y 2016, cuando ganó Podemos. Vitoria no ha votado nunca al PNV como primera opción. Bilbao y Getxo, en cambio, son del PNV casi siempre: Getxo solo le falló en 2000, cuando ganó el PP, y Bilbao votó al PP en 2000 y al PSE en 2008 y en 2023.</p>
<p>El mapa por municipios muestra cómo ha cambiado el voto nacionalista. En 1977 el PNV ganó en 149 de los 251 municipios actuales, todos en Bizkaia y Gipuzkoa, mientras UCD fue primera en 34 de los 51 municipios de Álava. En 2004 el PNV llegó a 210. En 2011 Amaiur fue la lista más votada en 125 municipios, entre ellos 83 de los 88 de Gipuzkoa. Y en 2023 EH Bildu ganó en 140, frente a 76 del PNV, que resiste sobre todo en Bizkaia (55 municipios); el PSE fue primero en 29, entre ellos Vitoria y Bilbao, y el PP en 6, todos en Álava, en la Rioja Alavesa y junto al Ebro.</p>
{F.mapa('El País Vasco, municipio a municipio', 'Lista más votada en cada municipio en las generales.')}
<p>Veintiocho municipios han votado al PNV en las 16 generales, entre ellos Mungia, Bermeo y Gernika-Lumo. Ningún otro partido ha sido fiel en ninguno.</p>

<h2>Votar menos que la media</h2>
<p>Sin contar el voto exterior, la participación vasca ha quedado por debajo de la española en las dieciséis generales. La mayor diferencia fue la de 2008: el 64,9% frente al 75,3%. En 2023 votó el 67,6%, frente al 70,4%.</p>
{F.part('Participación en las generales: País Vasco y España', 'Porcentaje de votantes sobre el censo de residentes en España.')}

<h2>Qué mirar el 29N</h2>
<p>El País Vasco elige 18 diputados: 8 por Bizkaia, 6 por Gipuzkoa y 4 por Álava. En 2023 hubo un triple empate a cinco escaños entre el PSE, el PNV y EH Bildu; el PP sacó 2 y Sumar, 1. El 29 de noviembre dirá si EH Bildu, que empató con el PNV en el Parlamento Vasco en 2024, pasa por primera vez a ser la lista más votada del País Vasco en unas generales.</p>
"""


PIEZA = dict(
    cc='pais-vasco', slug='pais-vasco-historia-electoral', lugar='País Vasco', corto='El País Vasco en las urnas',
    titulo='El PNV ha sido el más votado en las trece elecciones vascas; en las generales perdió el primer puesto cinco veces, ante el PSE y Podemos',
    dek='Todos los lehendakaris han sido del PNV salvo Patxi López, investido en 2009 con el PP. En 2024 EH Bildu lo igualó a 27 escaños. '
        'En las generales, el PNV fue primero en once de dieciséis; en 2023, PSE, PNV y EH Bildu sacaron cinco diputados cada uno.',
    cuerpo=cuerpo, pie=PIE,
    descripcion='El PNV ha sido la lista más votada en las trece elecciones al Parlamento Vasco y solo dejó de gobernar con Patxi López (2009-2012). En las generales fue primero en once de dieciséis; el PSE ganó en 1993, 2008 y 2023, y Podemos en 2015 y 2016.',
    compara='Las 13 elecciones al Parlamento Vasco (1980-2024) y las 16 generales (1977-2023) en el País Vasco, por territorio y por municipio.',
    limites=LIMITES,
    fuentes=FUENTES_COMUNES + [he_fuente('aeuzkadi', 'el País Vasco'),
                               (IDP09, 'José Manuel Castells, «País Vasco», Informe Comunidades Autónomas 2009, Instituto de Derecho Público (IDP Barcelona)'),
                               (IDP16, 'Alberto López Basaguren, «País Vasco», Informe Comunidades Autónomas 2016, IDP Barcelona'),
                               (IDP23, 'Alberto López Basaguren, «País Vasco», Informe Comunidades Autónomas 2023, IDP Barcelona'),
                               (LOPEZ, 'Ámbito, «Día histórico: en el País Vasco un socialista asume por primera vez la presidencia» (7-5-2009)'),
                               ('https://github.com/dadosdelaplace/pollspaindata', 'pollspaindata (datos de Interior por mesa): votos de cada candidatura en las generales de 2004 a 2023')],
    enlaces=[],
)
