"""Genera las piezas de la sección Actualidad (/actualidad/).

Cada pieza parte de un HTML de trabajo en esta carpeta (<slug>.html: estilos de los gráficos,
<main> con el texto y <script> con los datos de los gráficos). Este script le pone la cabecera
del sitio (SEO, Open Graph, JSON-LD, analítica), la navegación, el bloque «Método y fuentes»
del estándar de verificación y el pie, y escribe además el índice y el sitemap de la sección.

Uso, desde la raíz del repositorio: python3 actualidad/src/construir.py && node actualidad/src/miniaturas.mjs
También rellena la franja «Actualidad» de la portada (index.html y la plantilla de generales-2026).
"""
import datetime, html, json, os, re, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(RAIZ, 'actualidad', 'src')
BASE = 'https://mapaelectoral.es'
# Editor de todo el sitio: el mismo objeto que atlas/src/paginas.py y src/seo.py
MEDIO = {'@type': 'NewsMediaOrganization', '@id': BASE + '/#medio', 'name': 'Mapa Electoral', 'url': BASE + '/',
         'founder': {'@type': 'Person', 'name': 'Nacho G. del Álamo', 'url': BASE + '/sobre-mi.html'},
         'publishingPrinciples': BASE + '/atlas/politica-editorial/', 'verificationFactCheckingPolicy': BASE + '/atlas/politica-editorial/#verificacion',
         'correctionsPolicy': BASE + '/atlas/correcciones/', 'sameAs': ['https://x.com/nachotronic']}
POLITICA = ' · <a href="https://mapaelectoral.es/atlas/politica-editorial/">Política editorial</a>'
AUTOR = 'Nacho G. del Álamo'
CF = ("<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' "
      "data-cf-beacon='{\"token\": \"cf0453d1d8f247d4a5dd55aff7b685ae\"}'></script><!-- End Cloudflare Web Analytics -->")
INTERIOR = ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/',
            'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)')
INE = ('https://www.ine.es/experimental/atlas/experimental_atlas.htm',
       'INE, Atlas de Distribución de Renta de los Hogares (renta y edad por sección), vía ineAtlas.data')
INE_CENSO = ('https://www.ine.es/censos2021/C2021_Indicadores.csv',
             'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (régimen de tenencia de las viviendas principales)')
EL_ESPANOL = 'https://www.elespanol.com/sociedad/20261007/muere-maricarmen-directo-fallece-anos-dias-despues-desahuciada-madrid/1003744412550_10.html'
EURONEWS = 'https://es.euronews.com/video/2026/09/23/el-desahucio-de-maricarmen-se-consuma-tras-70-anos-en-su-casa-de-retiro'
EXCELSIOR = 'https://www.excelsior.com.mx/internacional/miles-marchan-madrid-contra-desahucio-mujer-87-anos'
VANGUARDIA = 'https://www.vanguardia.com/mundo/2026/09/29/maricarmen-la-anciana-de-87-anos-desalojada-en-madrid-podra-volver-a-la-casa/'
ARA = 'https://es.ara.cat/politica/tc-avala-amnistia-malversacion-no-aplica-todavia-puigdemont_1_5522452.html'
DEMOCRATA = 'https://www.democrata.es/politica/puigdemont-29n-regreso-sin-fecha-sin-cita-con-sanchez/'
PUBLICO_RUFIAN = 'https://www.publico.es/politica/rufian-asegura-quiere-candidato-erc-ojala-erc-quiera.html'
INFOBAE_RUFIAN = 'https://www.infobae.com/espana/agencias/2026/10/08/rufian-asegura-que-quiere-ser-el-candidato-de-erc-pero-acompanado-de-otras-izquierdas/'
DEMOCRATA_ERC = 'https://www.democrata.es/politica/ampliacion-erc-se-decanta-por-rufian-y-fijara-el-17-de-octubre-su-candidatura-tras-unas-primarias/'
INFOBAE_MONTERO = 'https://www.infobae.com/espana/agencias/2026/10/06/maria-jesus-montero-descarta-ir-en-las-listas-del-psoe-el-29n/'
ELMIRA_MONTERO = 'https://www.elmira.es/articulo/andalucia/montero-ira-listas-psoe-congreso-sevilla-pone-vivienda-centro-29n/20261006140351619717.html'
CORDOBABN_MONTERO = 'https://www.cordobabn.com/andalucia/29n-montero-descarta-como-candidata-desea-que-sanchez-acuda-muchas-veces-andalucia-pieza-clave-29n/20261006193152270616.html'
INDEPENDIENTE_ANDALUZAS = 'https://www.elindependiente.com/espana/2026/05/17/elecciones-andalucia-resultados-psoe-montero-sanchez-gobierno/'
WIKI_ANDALUZAS_2022 = 'https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_de_Andaluc%C3%ADa_de_2022'
INE_IPVA = ('https://www.ine.es/jaxiT3/Tabla.htm?t=59060',
            'INE, Índice de Precios de Vivienda en Alquiler (estadística experimental, base 2015), por municipio (tabla 59060) y por distrito de las capitales (tabla 59061)')
PARLAMENT = ('https://analisi.transparenciacatalunya.cat/d/ntc4-rnwr',
             'Generalitat de Catalunya, Transparència Catalunya: resultados de las elecciones al Parlament por sección censal (votos por candidatura, ntc4-rnwr, y participación, irrv-2mfc)')

# Series: agrupan las piezas en el índice, en la portada y en «Sigue leyendo»
SERIES = {'29n': 'Camino al 29N', 'vivienda': 'Vivienda y voto'}
# Ilustración de cada serie: cabecera de las piezas que no tienen una propia y del bloque de la serie en el índice
SERIES_FOTO = {'vivienda': dict(src='img/actualidad/fotos/serie-vivienda.jpg', ancho=1280, alto=720, ia=True,
                                pie='Una urna llena de edificios y unas llaves: la serie «Vivienda y voto».')}

PIEZAS = [
    dict(
        slug='beiras-nacionalismo-gallego', fecha='2026-10-08',
        titulo='Del 12% al 2,9% y de vuelta al 9,5%: el nacionalismo gallego que deja Beiras', serie='29n',
        descripcion='El BNG pasó del 12,0 % en Galicia en 2004 al 2,9 % en 2016, cuando En Marea sacó el 22,4 %, y en 2023 volvió al 9,5 %. Mapas por municipio y sección.',
        compara='La lista nacionalista (BNG; NÓS en 2015) y la gran lista a su izquierda en cada elección general en Galicia, de 2004 a 2023, candidatura a candidatura. Voto por municipio y por sección, cruzado con edad, estudios y renta.',
        limites='Solo elecciones generales: no incluye las autonómicas, donde el BNG obtiene sus mejores resultados. Las listas a la izquierda del BNG cambian de socios en cada elección. Los quintiles mezclan edad, estudios y tamaño de municipio, que van juntos en Galicia. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/galicia/muere-90-anos-xose-manuel-beiras-intelectual-dirigente-nacionalismo-gallego-importante-castelao_1_13565454.html', 'elDiario.es, obituario de Xosé Manuel Beiras (Daniel Salgado, 8-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Xos%C3%A9_Manuel_Beiras', 'Wikipedia, «Xosé Manuel Beiras» (consultada el 8-10-2026)')],
        enlaces=[('El País', 'https://elpais.com/espana/2026-10-08/muere-a-los-90-anos-xose-manuel-beiras-historico-dirigente-del-nacionalismo-gallego.html')],
        lugar='Galicia',
        actualizado='2026-10-09',
        correcciones='9-10-2026: el récord de 18 escaños del BNG en 1997 se superó en 2020 (19), no en 2024 (25). Se retira una cita sin fuente. Dos municipios creados después de 2004 (Oza-Cesuras y Cerdedo-Cotobade) aparecían en el mapa de 2004 con «NaN %»; ahora figuran sin dato.',
        foto=dict(src='img/actualidad/fotos/beiras-nacionalismo-gallego.jpg', ancho=1280, alto=720, ia=True,
                  pie='Xosé Manuel Beiras, con la bandera gallega y una urna.'),
    ),
    dict(
        slug='colau-barcelona-comuns', fecha='2026-10-08',
        titulo='La Barcelona que tendría que reconquistar Colau: los comuns ganaban en 837 secciones y ahora en 23', serie='29n',
        descripcion='En Comú Podem ganó en 837 de las 1.068 secciones de Barcelona en 2015 (26,7 %). En 2023, Sumar-En Comú Podem ganó en 23 (17,0 %). La caída fue mayor en los barrios de renta baja.',
        compara='La candidatura de la que formaban parte los comuns en cada elección en la ciudad de Barcelona (generales 2011-2023 y municipales 2011-2023), por distrito y por sección censal, y su relación con la renta de la sección.',
        limites='Las candidaturas cambian de nombre y de socios; se cuenta solo la lista de los comuns, sin sumar otras (Front Republicà en abril de 2019, Más País en noviembre de 2019). Las secciones se comparan con los límites de 2023. Los quintiles de renta son medias simples de secciones. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/politica/monica-garcia-renuncia-candidata-frente-amplio-favor-ada-colau-pide-liderar-lista-madrid_1_13569737.html', 'elDiario.es, «Mónica García renuncia a ser candidata del Frente Amplio…» (7-10-2026)'),
                 ('https://civio.es/el-boe-nuestro-de-cada-dia/2026/10/06/llega-al-boe-la-convocatoria-de-elecciones-para-el-29-de-noviembre-todas-las-fechas-y-pasos-hasta-ese-dia/', 'Civio, calendario y escaños del decreto de convocatoria (6-10-2026)')],
        enlaces=[],
        lugar='Barcelona',
        foto=dict(src='img/actualidad/fotos/colau-barcelona-comuns.jpg', ancho=1280, alto=720, ia=True,
                  pie='Ada Colau, con Barcelona al fondo.'),
    ),
    dict(
        slug='votar-en-noviembre', fecha='2026-10-08',
        titulo='El 29N repite mes con mal recuerdo: el último noviembre dejó la participación más baja de la democracia', serie='29n',
        descripcion='El 10N de 2019 dejó un 66,2 % de participación, el mínimo desde 1977; el máximo, 80,0 %, también fue en otoño, en octubre de 1982. Entre abril y noviembre de 2019 la participación cayó en el 98 % de las secciones.',
        compara='La participación oficial en las 16 elecciones generales desde 1977 y, por sección censal, la de abril y noviembre de 2019, por provincia y por decil de renta.',
        limites='Con solo dos elecciones en noviembre no se puede aislar el efecto del mes. La participación oficial de 2011 a 2019 está rebajada por el voto rogado de los residentes en el extranjero; los datos por sección no incluyen voto exterior. Los deciles son medias simples de secciones con la renta de un solo año.',
        fuentes=[('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a', 'Junta Electoral Central, participación oficial 1977-2023 (tabla recopilada en Wikipedia, consultada el 8-10-2026)'),
                 INTERIOR, INE,
                 ('https://civio.es/el-boe-nuestro-de-cada-dia/2026/10/06/llega-al-boe-la-convocatoria-de-elecciones-para-el-29-de-noviembre-todas-las-fechas-y-pasos-hasta-ese-dia/', 'Civio, calendario electoral del 29N (6-10-2026)'),
                 ('https://www.canarias7.es/elecciones/generales/convocatoria-elecciones-generales-obliga-cancelar-eventos-programados-20261007131300-nt.html', 'Canarias7, eventos cancelados por el 29N (7-10-2026)')],
        enlaces=[],
        lugar='España',
        actualizado='2026-10-09',
        correcciones='9-10-2026: el BOE publicó el decreto el martes 6 de octubre, no el lunes.',
    ),
    dict(
        slug='maricarmen-alquiler-y-voto', fecha='2026-10-08',
        titulo='Después de Maricarmen: los barrios de inquilinos votan diez puntos menos', serie='vivienda', figura=1,
        descripcion='En el 10 % de secciones con más hogares de alquiler votó el 64,6 % en 2023; en el 10 % con menos, el 74,1 %. Entre los barrios más pobres, la distancia llega a 16 puntos.',
        compara='El porcentaje de hogares de alquiler de cada sección censal (censo de 2021) y su participación y voto en las generales de julio de 2023, en toda España y dentro de cada quintil de renta; la ciudad de Madrid por distritos; la distancia en las generales desde 2004.',
        limites='Son datos agregados por sección: que un barrio con mucho alquiler vote menos no prueba que los inquilinos voten menos que sus vecinos propietarios. El alquiler es el del censo de 2021, también para elecciones anteriores. La regresión describe una asociación, no una causa. Las explicaciones (movilidad, empadronamiento) son hipótesis. Sin voto exterior.',
        fuentes=[INE_CENSO, INTERIOR, INE,
                 (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)'),
                 (EURONEWS, 'Euronews, «El desahucio de Maricarmen se consuma tras 70 años en su casa de Retiro» (23-9-2026)'),
                 (EXCELSIOR, 'Excélsior, «Miles marchan en Madrid contra desahucio de mujer de 87 años» (26-9-2026)'),
                 ('https://doi.org/10.2307/1960778', 'Squire, Wolfinger y Glass, «Residential Mobility and Voter Turnout», American Political Science Review, 1987')],
        enlaces=[],
        lugar='España',
        actualizado='2026-10-09',
        correcciones='9-10-2026: en participación, Retiro va solo por detrás de Chamartín, no de Salamanca.',
        foto=dict(src='img/actualidad/fotos/maricarmen-alquiler-y-voto.jpg', ancho=1280, alto=720, ia=True,
                  pie='Unas llaves, un contrato de alquiler y una urna.'),
    ),
    dict(
        slug='alquiler-ciudad-a-ciudad', fecha='2026-10-08',
        titulo='Sin excepción: en las 25 mayores ciudades de España, los barrios de alquiler votan menos', serie='vivienda',
        descripcion='En las 25 ciudades con más electores, el 20 % de secciones con más alquiler votó menos en 2023 que el 20 % con menos. En Alicante, 15 puntos menos; en Vigo, 1,9.',
        compara='En cada una de las 25 ciudades con más electores, la participación en las generales de julio de 2023 del 20 % de secciones con menos hogares de alquiler y del 20 % con más (censo de 2021), y la renta de cada grupo.',
        limites='Son datos agregados por sección, no de personas. El alquiler es el del censo de 2021. En muchas ciudades los barrios de alquiler son también más pobres, y parte de la diferencia puede deberse a la renta. Los quintiles de las ciudades menores tienen unas 30 secciones. Sin voto exterior.',
        fuentes=[INE_CENSO, INTERIOR, INE, (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='25 ciudades',
        actualizado='2026-10-09',
        correcciones='9-10-2026: Terrassa, una de las 25 ciudades con más electores, faltaba en la comparación y en su lugar aparecía Sabadell. Ya está incluida (4,3 puntos de diferencia). Las conclusiones no cambian.',
        foto=dict(src='img/actualidad/fotos/alquiler-ciudad-a-ciudad.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna llena de edificios de viviendas.'),
    ),
    dict(
        slug='pisos-turisticos-y-votantes', fecha='2026-10-08',
        titulo='Los barrios de pisos turísticos de Barcelona han perdido uno de cada diez electores desde 2015', serie='vivienda',
        descripcion='En las 25 mayores ciudades, las secciones con un 5 % o más de pisos turísticos perdieron el 2,9 % de sus electores entre 2015 y 2023, frente al 1,0 % de las que apenas tienen. En Barcelona, el 10,6 %.',
        compara='El peso de los pisos turísticos en cada sección censal (INE, agosto de 2023) y la variación de su censo electoral entre las generales de 2015 y 2023 en las 25 mayores ciudades; en toda España, la participación de 2004 y 2023 según ese peso.',
        limites='La estadística de viviendas turísticas del INE es experimental y cuenta anuncios en plataformas. El censo electoral solo incluye a españoles y cambia también por envejecimiento, defunciones y mudanzas: los datos muestran que ambas cosas van juntas, no que una cause la otra. Se usa el peso de agosto de 2023 para toda la serie. Sin voto exterior.',
        fuentes=[('https://www.ine.es/experimental/viv_turistica/exp_viv_turistica_tablas.htm', 'INE, Medición del número de viviendas turísticas en España y su capacidad (estadística experimental), tabla por secciones censales, agosto de 2023'),
                 INTERIOR, (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='Grandes ciudades',
        actualizado='2026-10-09',
        correcciones='9-10-2026: se reescribe una frase que podía leerse como una afirmación causal sobre la abstención.',
        foto=dict(src='img/actualidad/fotos/pisos-turisticos-y-votantes.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una maleta de viaje, edificios de viviendas y una urna.'),
    ),
    dict(
        slug='psoe-barrios-de-alquiler', fecha='2026-10-08',
        titulo='El PSOE sube en los barrios de alquiler casi el triple que en los de propietarios desde 2015', serie='vivienda',
        descripcion='Fuera de Cataluña, en el 10 % de secciones con más alquiler el PSOE pasó del 19,6 % en 2015 al 31,0 % en 2023 (+11,4); en las de menos alquiler, del 29,5 % al 33,5 % (+4,0). El espacio a su izquierda cayó allí del 27,0 % al 14,4 %.',
        compara='El voto al PSOE y a la familia de partidos a su izquierda (IU, Podemos y confluencias, Compromís, Más País, Sumar) en las generales de 2004 a 2023, en las secciones censales ordenadas en diez grupos por hogares de alquiler (censo de 2021), sin Cataluña; por quintil de renta; en la ciudad de Madrid y, aparte, en Cataluña.',
        limites='Son datos agregados por sección: no dicen que los votos pasaran de un partido a otro ni que los inquilinos voten distinto que sus vecinos. El alquiler es el del censo de 2021 para toda la serie. La familia de partidos a la izquierda del PSOE cambia de composición en cada elección. Cataluña va aparte porque su sistema de partidos es distinto. Sin voto exterior.',
        fuentes=[INE_CENSO, INTERIOR, INE, (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='España sin Cataluña',
        foto=dict(src='img/actualidad/fotos/psoe-barrios-de-alquiler.jpg', ancho=1280, alto=720, ia=True,
                  pie='Pedro Sánchez, con el Congreso de los Diputados y una urna.'),
    ),
    dict(
        slug='precio-del-alquiler-y-voto', fecha='2026-10-08',
        titulo='El alquiler sube un 29% en València desde 2015, pero el voto apenas lo refleja', serie='vivienda',
        descripcion='Entre 2015 y 2023 el alquiler subió un 18,7 % en España según el INE: un 28,9 % en València, un 26,1 % en Málaga y un 26,0 % en Palma. Donde más subió, la participación cayó algo más y el PSOE creció algo más, pero dentro de cada provincia la relación casi desaparece.',
        compara='La subida del Índice de Precios de Vivienda en Alquiler del INE entre 2015 y 2023 en 703 municipios de más de 10.000 habitantes y en los distritos de las capitales, frente al cambio de participación y de voto por partido entre las generales de 2015 y 2023.',
        limites='El índice mide el precio de los contratos, no quién vive en cada casa, y el voto de un municipio mezcla inquilinos y propietarios. Los municipios donde más subió se concentran en pocas provincias, y al comparar dentro de cada provincia la relación es muy débil. No incluye País Vasco ni Navarra. Es en buena parte un resultado nulo, y así se cuenta. Sin voto exterior.',
        fuentes=[INE_IPVA, INTERIOR,
                 (VANGUARDIA, 'Vanguardia, «Maricarmen, la anciana de 87 años desalojada en Madrid, podrá volver a la casa» (29-9-2026)'),
                 (EL_ESPANOL, 'El Español, directo sobre la muerte de Maricarmen Abascal (7-10-2026)')],
        enlaces=[],
        lugar='703 municipios',
        actualizado='2026-10-09',
        correcciones='9-10-2026: la correlación dentro de cada ciudad va de 0,08 a 0,14, no «no llega a 0,1». La conclusión, que la relación es muy débil, no cambia.',
    ),
    dict(
        slug='puigdemont-junts-congreso-parlament', fecha='2026-10-08',
        titulo='Con Puigdemont de candidato, Junts duplica su voto: del 11% en el Congreso al 22% en el Parlament', serie='29n',
        descripcion='En las generales de 2023 Junts sacó en Cataluña el 11,2 % y ganó en 465 secciones. En las autonómicas de 2024, con Puigdemont como candidato, el 21,6 % y 681.470 votos, y ganó en 1.936, aunque votó menos gente.',
        compara='El voto a Junts (y antes a CiU) en Cataluña en las generales de 2004 a 2023 y en las autonómicas de 2024, por sección censal, por tamaño de municipio y por provincia.',
        limites='Generales y autonómicas tienen distinto electorado votante, distintos candidatos y eligen cosas distintas: la comparación no dice quién cambió su voto ni por qué. CiU incluía a Unió hasta 2015. Porcentajes sobre voto válido. Sin voto exterior.',
        fuentes=[INTERIOR, PARLAMENT,
                 (ARA, 'Ara, el TC avala la amnistía de la malversación pero aún no la aplica a Puigdemont (6-10-2026)'),
                 (DEMOCRATA, 'Demócrata, el regreso de Puigdemont, sin fecha (octubre de 2026)')],
        enlaces=[],
        lugar='Cataluña',
        actualizado='2026-10-09',
        correcciones='8-10-2026: Junts ganó en 465 secciones en las generales de 2023, no en 444 (se habían contado solo las secciones con datos del Parlament de 2024). En Lleida, del 18,1%, no del 18,0%. Las conclusiones no cambian. 9-10-2026: CiU no tuvo su máximo en 2011 (29,5%): en 1989 superó el 32%.',
        foto=dict(src='img/actualidad/fotos/puigdemont-junts-congreso-parlament.jpg', ancho=1280, alto=720, ia=True,
                  pie='Carles Puigdemont, con la senyera, una urna y gráficos.'),
    ),
    dict(
        slug='rufian-erc-comuns', fecha='2026-10-08',
        titulo='Sumados, ERC y los comuns habrían sido la lista más votada en 1.431 secciones de Cataluña en 2023; por separado, en 232', serie='29n',
        descripcion='Rufián quiere ser el candidato de ERC «acompañado de otras fuerzas de izquierdas». En 2023 ERC sacó en Cataluña el 13,2 %, casi la mitad que en 2019. Con los votos de los comuns sumados sección a sección, el mapa cambia, aunque el PSC sigue por delante.',
        compara='El voto a ERC en Cataluña en las generales de 2004 a 2023, las secciones censales donde cada lista fue la más votada en 2023 y la suma aritmética de ERC y los comuns (Sumar-En Comú Podem) sección a sección, en Cataluña y en la ciudad de Barcelona.',
        limites='La suma es aritmética: no estima lo que sacaría una lista conjunta, porque no todos los votantes de una y otra votarían la misma papeleta. La lista de los comuns cambia de nombre en cada elección. Porcentajes sobre voto a candidaturas. Sin voto exterior.',
        fuentes=[INTERIOR,
                 (PUBLICO_RUFIAN, 'Público, «Rufián asegura que quiere ser candidato de ERC» (8-10-2026)'),
                 (INFOBAE_RUFIAN, 'Infobae / EFE, Rufián quiere ser el candidato de ERC, pero acompañado de otras izquierdas (8-10-2026)'),
                 (DEMOCRATA_ERC, 'Demócrata, ERC fijará el 17 de octubre su candidatura (octubre de 2026)')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/rufian-erc-comuns.jpg', ancho=1280, alto=720, ia=True,
                  pie='Gabriel Rufián, con el Congreso de los Diputados y una urna.'),
    ),
    dict(
        slug='psoe-andalucia-generales-autonomicas', fecha='2026-10-08',
        titulo='Andalucía vota casi diez puntos más al PSOE cuando elige al Gobierno que cuando elige a la Junta', serie='29n',
        descripcion='Montero no irá en las listas del 29N tras el peor resultado del PSOE en unas andaluzas, el 22,7 % de mayo. En las generales de 2023 el PSOE andaluz sacó el 33,5 %. Lo que sí ha perdido es el mapa: en 2004 ganaba en tres de cada cuatro secciones; en 2023, en menos de la mitad.',
        compara='El voto al PSOE y al PP en Andalucía en las generales de 2004 a 2023, por sección censal, por provincia y por renta, frente a los resultados de las autonómicas de 2022 y 2026.',
        limites='Las generales vienen de Interior, por mesa y sin voto exterior; las autonómicas son los totales publicados con su propio escrutinio, así que la diferencia de 9,4 puntos compara fuentes distintas. Los datos no dicen quién vota distinto en cada elección. Las secciones cambian de límites entre elecciones.',
        fuentes=[INTERIOR, INE,
                 (INFOBAE_MONTERO, 'Infobae / Europa Press, Montero descarta ir en las listas del PSOE el 29N (6-10-2026)'),
                 (ELMIRA_MONTERO, 'elmira.es, Montero y las listas del PSOE por Sevilla (6-10-2026)'),
                 (CORDOBABN_MONTERO, 'Córdoba BN, Montero pide que Sánchez acuda a Andalucía, «pieza clave» del 29N (6-10-2026)'),
                 (INDEPENDIENTE_ANDALUZAS, 'El Independiente, resultados de las elecciones andaluzas del 17 de mayo de 2026'),
                 (WIKI_ANDALUZAS_2022, 'Wikipedia, elecciones al Parlamento de Andalucía de 2022 (resultados oficiales)')],
        enlaces=[],
        lugar='Andalucía',
        foto=dict(src='img/actualidad/fotos/psoe-andalucia-generales-autonomicas.jpg', ancho=1280, alto=720, ia=True,
                  pie='María Jesús Montero, con el Congreso de los Diputados, una urna y papeles de Hacienda.'),
    ),
    dict(
        slug='huelga-11n-paro-participacion', fecha='2026-10-09',
        titulo='La huelga del 11N apela a los barrios que menos votan: donde más paro hay, la participación cae al 61%', serie='29n',
        descripcion='CCOO, UGT y el Sindicato de Inquilinas convocan la primera huelga general conjunta desde 2012 a 18 días de las generales. En julio de 2023, el 10% de secciones con más paro votó quince puntos menos que el 10% con menos paro. A igual renta, la distancia se mantiene.',
        compara='La participación en las generales de julio de 2023 de las 34.737 secciones censales de España, agrupadas por la tasa de paro del censo de 2021 (deciles) y, dentro de cada quintil de renta, el 20% con menos y con más paro.',
        limites='El paro es el del censo de 2021, no el de 2023. Es una asociación entre secciones: no dice que los parados voten menos ni explica por qué. Nada dice sobre quién secundará la huelga. Medias ponderadas por censo, sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ccoo.es/noticia:769574--Convocamos_huelga_general_para_el_11_de_noviembre&opc_id=8c53f4de8f8f09d2e54f19daf8d8ed95', 'CCOO, «Convocamos huelga general para el 11 de noviembre» (octubre de 2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/huelga-11n-paro-participacion.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una nómina, monedas y herramientas de trabajo junto a una urna.'),
    ),
    dict(
        slug='psoe-madrid-municipales-generales', fecha='2026-10-09',
        titulo='En Madrid, el PSOE saca diez puntos más cuando se vota al Gobierno que cuando se vota al alcalde', serie='29n',
        descripcion='La bronca entre Ayuso y Más Madrid en la Asamblea vuelve a enfrentar a las dos fuerzas que dominan la política madrileña. En la ciudad de Madrid, el PSOE sacó el 16,8% en las municipales de mayo de 2023 y el 27,4% en las generales de julio. Fue más alto en las generales en todas las secciones menos una.',
        compara='El voto a PP, PSOE, Vox y la izquierda del PSOE en la ciudad de Madrid en las municipales del 28 de mayo de 2023 y en las generales del 23 de julio, en total, por distrito y en las 2.450 secciones censales.',
        limites='Son dos elecciones con electorados distintos: la participación fue 5 puntos más alta en julio y en las municipales votan también residentes de la UE. Los datos no dicen cuántos votantes cambiaron de papeleta. En las municipales Más Madrid y Podemos-IU fueron por separado y en las generales los dos iban en Sumar. Porcentajes sobre voto válido, sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.infobae.com/espana/agencias/2026/10/08/tenso-enfrentamiento-entre-ayuso-y-mas-madrid-en-la-asamblea-tras-la-muerte-de-maricarmen/', 'Infobae / EFE, tenso enfrentamiento entre Ayuso y Más Madrid en la Asamblea (8-10-2026)')],
        enlaces=[],
        lugar='Madrid',
        foto=dict(src='img/actualidad/fotos/psoe-madrid-municipales-generales.jpg', ancho=1280, alto=720, ia=True,
                  pie='Isabel Díaz Ayuso, con la Puerta del Sol y una urna.'),
    ),
    dict(
        slug='izquierda-del-psoe-secciones', fecha='2026-10-09',
        titulo='El espacio a la izquierda del PSOE fue el más votado en 9.810 secciones en 2015; en 2023, en 182', serie='29n',
        descripcion='Podemos antepone sus primarias y se aleja del Frente Amplio. Antes de saber cuántas papeletas habrá a la izquierda del PSOE, los datos por sección muestran de dónde parte ese espacio: del 24,4% de 2015 al 12,3% de 2023, con caídas en todo tipo de municipios.',
        compara='El voto a las listas a la izquierda del PSOE en las generales de 2015, 2016, abril y noviembre de 2019 y 2023, las secciones censales donde fueron primeras, y su voto por tamaño de municipio y por provincia.',
        limites='La composición del espacio cambia en cada elección (Podemos y confluencias, IU, Compromís, Más País, Sumar). En 2023 no se puede separar a Podemos de Sumar. Las secciones cambian de límites entre elecciones. Sin voto exterior.',
        fuentes=[INTERIOR,
                 ('https://www.lavanguardia.com/politica/20261008/11654274/antepone-primarias-aleja-entrada-frente-amplio-pesar-colau.html', 'La Vanguardia, Podemos antepone sus primarias y se aleja del Frente Amplio (8-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='vox-poblacion-nacida-fuera', fecha='2026-10-09',
        titulo='Vox saca casi lo mismo donde uno de cada tres vecinos nació fuera que donde casi nadie lo hizo', serie='29n',
        descripcion='La inmigración en Euskadi bajó en 2025, según los datos que publica esta semana la prensa vasca. Euskadi es también donde menos vota a Vox: el 2,6% en 2023. En el resto de España, el voto a Vox apenas cambia entre las secciones con menos del 5% y con más del 30% de población nacida en el extranjero.',
        compara='El voto a Vox en las generales de julio de 2023 por sección censal, agrupado por el porcentaje de residentes nacidos en el extranjero del censo de 2021, en Cataluña, Euskadi, Navarra y el resto de España.',
        limites='Es un dato por sección, no por persona: no dice si quienes votan a Vox viven cerca de población inmigrante ni si la votan por eso. «Nacidos fuera» incluye a españoles nacidos en el extranjero, y los extranjeros sin nacionalidad no votan en generales. Censo de 2021 frente a voto de 2023. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.naiz.eus/info/noticia/20261007/la-foto-real-de-la-inmigracion-en-la-cav-en-2025-bajo-y-los-magrebies-solo-fueron-el-12', 'Naiz, la inmigración en la CAV en 2025 (7-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/vox-poblacion-nacida-fuera.jpg', ancho=1280, alto=720, ia=True,
                  pie='Vecinos de distintos orígenes en una calle, junto a una urna.'),
    ),
]

# Enlaces a las fuentes dentro del texto: (texto exacto, url)
ENLACES_TEXTO = {
    'beiras-nacionalismo-gallego': [
        ('según el obituario de elDiario.es', PIEZAS[0]['fuentes'][2][0]),
    ],
    'colau-barcelona-comuns': [
        ('Según elDiario.es, Más Madrid', PIEZAS[1]['fuentes'][2][0]),
        ('según el decreto de convocatoria publicado en el BOE', PIEZAS[1]['fuentes'][3][0]),
    ],
    'votar-en-noviembre': [
        ('según el calendario que ha desgranado Civio', PIEZAS[2]['fuentes'][3][0]),
        ('la convocatoria ya está obligando a cancelar eventos', PIEZAS[2]['fuentes'][4][0]),
    ],
    'maricarmen-alquiler-y-voto': [
        ('según ha contado El Español', EL_ESPANOL),
        ('al cuarto intento', EURONEWS),
        ('miles de personas marcharon por Madrid', EXCELSIOR),
        ('El Gobierno defiende que sus dos decretos', EL_ESPANOL),
    ],
    'alquiler-ciudad-a-ciudad': [
        ('La muerte de Maricarmen Abascal', EL_ESPANOL),
    ],
    'pisos-turisticos-y-votantes': [
        ('El desahucio y la muerte de Maricarmen Abascal', EL_ESPANOL),
    ],
    'psoe-barrios-de-alquiler': [
        ('La muerte de Maricarmen Abascal', EL_ESPANOL),
    ],
    'precio-del-alquiler-y-voto': [
        ('según la prensa', VANGUARDIA),
    ],
    'puigdemont-junts-congreso-parlament': [
        ('avaló el martes que la amnistía alcance la malversación', ARA),
        ('Su regreso a Cataluña sigue sin fecha', DEMOCRATA),
    ],
    'rufian-erc-comuns': [
        ('escribió en X', PUBLICO_RUFIAN),
        ('cerrar su candidatura el 17 de octubre', DEMOCRATA_ERC),
    ],
    'psoe-andalucia-generales-autonomicas': [
        ('Lo confirmó el martes', INFOBAE_MONTERO),
        ('«pieza clave»', CORDOBABN_MONTERO),
        ('su peor resultado en Andalucía', INDEPENDIENTE_ANDALUZAS),
    ],
}

# Enlaces entre piezas dentro del texto: (texto exacto, slug de la pieza enlazada)
ENLACES_INTERNOS = {
    'maricarmen-alquiler-y-voto': [
        ('Y el PSOE apenas se mueve', 'psoe-barrios-de-alquiler'),
        ('El patrón se repite', 'alquiler-ciudad-a-ciudad'),
        ('La vivienda puede ser el tema de esta campaña', 'precio-del-alquiler-y-voto'),
    ],
    'alquiler-ciudad-a-ciudad': [
        ('las secciones censales con más alquiler votan menos', 'maricarmen-alquiler-y-voto'),
        ('El alquiler es ya un tema de campaña', 'precio-del-alquiler-y-voto'),
    ],
    'pisos-turisticos-y-votantes': [
        ('si la campaña sobre vivienda moviliza a los que quedan', 'maricarmen-alquiler-y-voto'),
    ],
    'psoe-barrios-de-alquiler': [
        ('como ya se ha contado en esta sección', 'maricarmen-alquiler-y-voto'),
    ],
    'precio-del-alquiler-y-voto': [
        ('los barrios con más hogares de alquiler votan menos', 'maricarmen-alquiler-y-voto'),
        ('el PSOE ha recuperado terreno desde 2015', 'psoe-barrios-de-alquiler'),
    ],
}

# Serie «Historia electoral»: textos, datos y gráficos en historia/ (paginas.py escribe los <slug>.html de trabajo).
# Van delante en la lista para que la franja de portada siga mostrando las piezas del día.
sys.path.insert(0, os.path.join(SRC, 'historia'))
from textos import PIEZAS_HISTORIA  # noqa: E402
SERIES['historia'] = 'Historia electoral'
HISTORIA = []
for h in PIEZAS_HISTORIA:
    q = {k: h[k] for k in ('slug', 'titulo', 'descripcion', 'compara', 'limites', 'fuentes', 'lugar')}
    q.update(fecha=h.get('fecha', '2026-10-08'), serie='historia', enlaces=[])
    if h.get('foto'):
        q['foto'] = {k: v for k, v in h['foto'].items() if k != 'origen'}
    HISTORIA.append(q)
    for texto, destino in h.get('enlaces', []):
        if destino.startswith('http'):
            ENLACES_TEXTO.setdefault(h['slug'], []).append((texto, destino))
        else:
            ENLACES_INTERNOS.setdefault(h['slug'], []).append((texto, destino))
PIEZAS = HISTORIA + PIEZAS

FUENTES_WEB = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
               '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700'
               '&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">')
CSS_SITIO = """<style>
:root{--serif:"Newsreader",Georgia,serif;--ui:"IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;--surface:#fff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--surface:#1e2025}}
:root[data-theme="dark"]{--surface:#1e2025}
body{margin:0}
h1,h2{font-family:var(--ui);letter-spacing:-.01em}
h1{font-weight:700}
.kicker{font-family:var(--mono);font-size:.76rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0}
.kicker a{color:var(--muted);text-decoration:none}
.firma{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);padding-top:.6rem}
.firma a{color:var(--muted)}
.ficha{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:6px 16px 12px;font-size:.98rem;margin:0}
.ficha dt{font-family:var(--mono);font-size:.76rem;color:var(--muted);margin-top:10px}
.ficha dd{margin:2px 0 0}
.ficha ul{margin:.2rem 0 0;padding-left:1.1rem}
nav.site{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;max-width:46rem;margin:0 auto;padding:12px 16px 10px;border-bottom:1px solid var(--rule);font:500 14px/1.4 var(--ui)}
nav.site a{color:var(--muted);text-decoration:none}nav.site a:hover{color:var(--fg)}nav.site a[aria-current]{color:var(--fg);font-weight:700}
nav.site a.marca{color:var(--fg);font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:13px;margin-right:6px}
@media (max-width:760px){nav.site{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none}nav.site::-webkit-scrollbar{display:none}}
.sigue{list-style:none;padding:0;display:grid;gap:12px}
.sigue a{display:block;background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:12px 16px;text-decoration:none;color:var(--fg);font-family:var(--ui)}
.sigue .kicker{display:block;margin-bottom:2px}
figure.foto{margin:1.4rem 0 0}figure.foto img{display:block;width:100%;height:auto;border-radius:6px}
figure.foto figcaption{font-family:var(--ui);font-size:.85rem;color:var(--muted);margin-top:6px}figure.foto a{color:var(--muted)}
ol.serie{padding-left:1.6rem;font-family:var(--ui);display:grid;gap:8px}
ol.serie li::marker{font-family:var(--mono);color:var(--muted)}
ol.serie a{color:var(--fg)}
ol.serie li[aria-current] b{font-weight:500;color:var(--muted)}
ol.serie .kicker{display:block}
footer{margin-top:3rem;font-family:var(--mono);font-size:.76rem;color:var(--muted)}
</style>"""


def fecha_larga(f):
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    a, m, d = f.split('-')
    return f'{int(d)} de {meses[int(m) - 1]} de {a}'


def nav(prefijo, actual):
    items = [('', 'Mapa de resultados'), ('atlas/index.html', 'Atlas'), ('actualidad/index.html', 'Actualidad'),
             ('abstencion.html', 'Cataluña'), ('sobre-mi.html', 'Sobre mí')]
    out = f'<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="{prefijo}">Mapa Electoral</a>'
    for href, txt in items:
        cur = ' aria-current="page"' if txt == actual else ''
        out += f'<a href="{prefijo}{href}"{cur}>{txt}</a>'
    return out + '</nav>'


def cabecera(titulo, descripcion, url, imagen, jsonld, robots='index, follow, max-image-preview:large'):
    e = html.escape
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo)} · Mapa Electoral</title>
<meta name="description" content="{e(descripcion)}">
<meta name="author" content="{AUTOR}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Mapa Electoral">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descripcion)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{imagen}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="es_ES">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:site" content="@nachotronic">
<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">
<script type="application/ld+json">
{json.dumps(jsonld, ensure_ascii=False, indent=1)}
</script>
{CF}
{FUENTES_WEB}
"""


def pieza(p, todas):
    src = open(os.path.join(SRC, p['slug'] + '.html'), encoding='utf-8').read()
    estilos = ''.join(re.findall(r'<style>.*?</style>', src, re.S))
    main = re.search(r'<main>.*?</main>', src, re.S).group(0)
    script = re.search(r'<script>.*?</script>', src, re.S).group(0)
    h1 = re.search(r'<h1>(.*?)</h1>', main, re.S).group(1)
    url = f"{BASE}/actualidad/{p['slug']}/"
    imagen = f"{BASE}/img/compartir/actualidad-{p['slug']}.jpg"
    f = fecha_larga(p['fecha'])

    main = re.sub(r'<span class="draft">.*?</span>\n?', f'<p class="kicker"><a href="../index.html">Actualidad</a> · {SERIES[p["serie"]]} · {p["lugar"]}</p>\n', main)
    main = re.sub(r'<div class="byline">.*?</div>',
                  f'<p class="firma">Por <a href="../../sobre-mi.html">{AUTOR}</a> · <time datetime="{p["fecha"]}">{f}</time></p>', main)
    fo = p.get('foto') or SERIES_FOTO.get(p['serie'])
    if fo:
        # fotos de Commons con autor y licencia; ilustraciones hechas con IA, siempre señaladas (política editorial, #ia)
        cred = (f'Ilustración generada con IA para Mapa Electoral. <a href="../../atlas/politica-editorial/#ia">Uso de IA</a>' if fo.get('ia')
                else f'Foto: <a href="{fo["url"]}">{html.escape(fo["credito"])}</a>')
        main = main.replace('</time></p>', f'</time></p>\n<figure class="foto"><img src="../../{fo["src"]}" alt="{html.escape(fo["pie"]) if fo.get("ia") else ""}" width="{fo["ancho"]}" height="{fo["alto"]}">'
                            f'<figcaption>{html.escape(fo["pie"])} {cred}.</figcaption></figure>', 1)
    for texto, href in ENLACES_TEXTO.get(p['slug'], []):
        assert texto in main, (p['slug'], texto)
        main = main.replace(texto, f'<a href="{href}">{texto}</a>', 1)
    for texto, slug in ENLACES_INTERNOS.get(p['slug'], []):
        assert texto in main and any(q['slug'] == slug for q in todas), (p['slug'], texto)
        main = main.replace(texto, f'<a href="../{slug}/index.html">{texto}</a>', 1)
    fuentes = ''.join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u, t in p['fuentes'])
    # la serie entera, en orden, con la pieza actual marcada; después, las últimas de otras series
    serie = [q for q in todas if q['serie'] == p['serie']]
    lista = ''.join(f'<li aria-current="page"><span class="kicker">Estás aquí</span><b>{html.escape(q["titulo"])}</b></li>' if q is p else
                    f'<li><a href="../{q["slug"]}/index.html"><b>{html.escape(q["titulo"])}</b></a></li>' for q in serie)
    otras = [q for q in todas if q['serie'] != p['serie']][::-1][:3]
    sigue = ''.join(f'<li><a href="../{q["slug"]}/index.html"><span class="kicker">{SERIES[q["serie"]]} · {q["lugar"]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in otras)
    ficha = f"""<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se compara</dt><dd>{p['compara']}</dd>
<dt>Límites</dt><dd>{p['limites']}</dd>
<dt>Cómo se calcula</dt><dd>Porcentajes sobre votos a candidaturas, salvo la participación, que es sobre el censo. Cifras reproducibles con los scripts del expediente de la pieza. <a href="../../atlas/metodologia/index.html">Metodología del Atlas</a></dd>
<dt>Fuentes</dt><dd><ul>{fuentes}</ul></dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
<dt>Revisión de datos y texto</dt><dd>{AUTOR}, {f}</dd>
<dt>Publicado · actualizado</dt><dd>{f} · {fecha_larga(p.get('actualizado', p['fecha']))}</dd>
<dt>Correcciones</dt><dd>{html.escape(p.get('correcciones', 'Ninguna.'))}</dd>
</dl>
<h2>Serie «{SERIES[p['serie']]}»: {len(serie)} piezas</h2><ol class="serie">{lista}</ol>
<h2>Sigue leyendo</h2><ul class="sigue">{sigue}<li><a href="../index.html"><span class="kicker">Actualidad</span><b>Todas las piezas de actualidad</b></a></li><li><a href="../../atlas/index.html"><span class="kicker">Atlas</span><b>Atlas de las anomalías electorales</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>{POLITICA}</footer>"""
    main = re.sub(r'<div class="foot">.*?</div>', ficha, main, flags=re.S)

    jsonld = {'@context': 'https://schema.org', '@type': 'NewsArticle', '@id': url + '#articulo',
              'headline': p['titulo'], 'alternativeHeadline': re.sub('<[^>]+>', '', h1), 'description': p['descripcion'],
              'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': p['fecha'], 'dateModified': p.get('actualizado', p['fecha']),
              'image': [imagen],
              'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html', 'sameAs': ['https://x.com/nachotronic', 'https://github.com/nachotronic']},
              'publisher': MEDIO,
              'isPartOf': {'@type': 'CollectionPage', 'name': 'Actualidad', 'url': BASE + '/actualidad/'},
              'isAccessibleForFree': True, 'license': 'https://creativecommons.org/licenses/by/4.0/'}
    out = (cabecera(p['titulo'], p['descripcion'], url, imagen, jsonld) + estilos + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../../', 'Actualidad') + '\n' + main + '\n' + script + '\n</body>\n</html>\n')
    d = os.path.join(RAIZ, 'actualidad', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out)


def indice(todas):
    url = BASE + '/actualidad/'
    desc = 'Piezas cortas que cruzan la actualidad del día con los datos electorales por sección censal. Cada cifra, con su fuente.'
    jsonld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Actualidad', 'url': url, 'description': desc,
              'hasPart': [{'@type': 'NewsArticle', 'headline': p['titulo'], 'url': f"{url}{p['slug']}/", 'datePublished': p['fecha']} for p in todas]}
    def bloque(serie):
        qs = [q for q in todas if q['serie'] == serie]
        fo = SERIES_FOTO.get(serie)
        img = (f'<figure class="foto"><img src="../{fo["src"]}" alt="{html.escape(fo["pie"])}" width="{fo["ancho"]}" height="{fo["alto"]}" loading="lazy">'
               f'<figcaption>Ilustración generada con IA para Mapa Electoral. <a href="../atlas/politica-editorial/#ia">Uso de IA</a>.</figcaption></figure>') if fo else ''
        return (f'<h2 id="{serie}">{SERIES[serie]}</h2>{img}<ul class="sigue tarjetas">' +
                ''.join(f'<li><a href="{q["slug"]}/index.html">{imagen_tarjeta(q)}<span class="txt"><span class="kicker">{fecha_larga(q["fecha"])} · {q["lugar"]}</span><b>{html.escape(q["titulo"])}</b><span class="d">{html.escape(q["descripcion"])}</span></span></a></li>'
                        for q in sorted(qs, key=lambda q: q['fecha'], reverse=True)) + '</ul>')

    def imagen_tarjeta(q):
        # la ilustración propia de la pieza o, si no tiene, la miniatura de su primer gráfico
        fo = q.get('foto') or SERIES_FOTO.get(q['serie'])
        if fo:
            return f'<img class="ilu" src="../{fo["src"]}" alt="" width="{fo["ancho"]}" height="{fo["alto"]}" loading="lazy">'
        return f'<img class="graf" src="../img/actualidad/{q["slug"]}.jpg" alt="" width="600" height="400" loading="lazy">'
    # primero la serie con la pieza más reciente
    orden = sorted(SERIES, key=lambda k: max((i for i, q in enumerate(todas) if q['serie'] == k), default=-1), reverse=True)
    items = ''.join(bloque(k) for k in orden if any(q['serie'] == k for q in todas))
    css = """<style>
:root{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.6}
main{max-width:46rem;margin:0 auto;padding-block:2rem 4rem;padding-inline:16px}
h1{font-size:clamp(1.8rem,5vw,2.4rem);margin:.6rem 0}
h2{font-size:1.3rem;margin:2.2rem 0 .8rem}
.sigue .d{display:block;color:var(--muted);font-family:var(--serif);font-size:1rem;margin-top:4px}
.sigue b{display:block;font-size:1.1rem;line-height:1.3}
a{color:var(--fg)}
.sigue.tarjetas a{display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:start;padding:12px}
.tarjetas img{display:block;width:100%;height:auto;aspect-ratio:16/9;border-radius:5px;border:1px solid var(--rule)}
.tarjetas img.ilu{object-fit:cover}
.tarjetas img.graf{object-fit:contain;background:#fff}
@media (max-width:560px){.sigue.tarjetas a{grid-template-columns:1fr;gap:10px}}
</style>"""
    out = (cabecera('Actualidad', desc, url, BASE + '/img/compartir/atlas.jpg', jsonld) + css + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../', 'Actualidad')
           + f'\n<main><p class="kicker">Mapa Electoral</p><h1>Actualidad</h1><p>{desc} Para las piezas de fondo, el <a href="../atlas/index.html">Atlas de las anomalías electorales</a>.</p>'
           + f'{items}<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>'
           + POLITICA + '</footer></main>\n</body>\n</html>\n')
    open(os.path.join(RAIZ, 'actualidad', 'index.html'), 'w', encoding='utf-8').write(out)
    urls = [f'  <url><loc>{url}</loc><lastmod>{max(p["fecha"] for p in todas)}</lastmod></url>']
    urls += [f'  <url><loc>{url}{p["slug"]}/</loc><lastmod>{p["fecha"]}</lastmod></url>' for p in todas]
    open(os.path.join(RAIZ, 'actualidad', 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    # Google News: solo piezas de los dos últimos días (norma de Google), como atlas/sitemap-noticias.xml
    lim = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    noticias = ''.join(f'  <url>\n    <loc>{url}{p["slug"]}/</loc>\n    <news:news>\n      <news:publication><news:name>Mapa Electoral</news:name><news:language>es</news:language></news:publication>\n'
                       f'      <news:publication_date>{p["fecha"]}</news:publication_date>\n      <news:title>{html.escape(p["titulo"])}</news:title>\n    </news:news>\n  </url>\n'
                       for p in todas if p['fecha'] >= lim)
    open(os.path.join(RAIZ, 'actualidad', 'sitemap-noticias.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + noticias + '</urlset>\n')


def imagen_carrusel(q, pre):
    # la ilustración de la pieza (o la de su serie) entera, sin recortar; si no hay, la miniatura del gráfico
    fo = q.get('foto') or SERIES_FOTO.get(q['serie'])
    if fo:
        return f'<img class="ilu" src="{pre}{fo["src"]}" alt="" loading="lazy" width="300" height="200">'
    return f'<img src="{pre}img/actualidad/{q["slug"]}.jpg" alt="" loading="lazy" width="300" height="200">'


def franja_portada(todas, pre=''):
    """Carrusel «Actualidad» de la portada del sitio, entre las marcas <!--actualidad:ultimas-->, encima del del Atlas.
    Mismo formato que la franja del Atlas (atlas/src/paginas.py): miniatura, serie y titular. Las miniaturas las hace miniaturas.mjs."""
    ult = todas[::-1][:10]
    return (f'<section class="wide del-atlas del-actualidad" aria-labelledby="h-del-actualidad"><div class="da-cab"><h2 id="h-del-actualidad"><a href="{pre}actualidad/">Actualidad</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Piezas anteriores">←</button><button type="button" class="da-next" aria-label="Más piezas">→</button></span></div>'
            '<ul class="carrusel">' +
            ''.join(f'<li><a href="{pre}actualidad/{q["slug"]}/">{imagen_carrusel(q, pre)}'
                    f'<span class="atlas-k">{SERIES[q["serie"]]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in ult) +
            f'<li class="todas"><a href="{pre}actualidad/"><b>Las {len(todas)} piezas de actualidad →</b><span>{" · ".join(SERIES[k] for k in SERIES)}</span></a></li></ul>'
            '<style>.del-actualidad .carrusel img{object-fit:contain;background:#fff}.del-actualidad .carrusel img.ilu{background:none}</style>'
            '<script>document.querySelectorAll(".del-actualidad").forEach(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})</script></section>')


def franja_historia(todas, pre=''):
    """Carrusel «Historia electoral» de la portada, debajo del de Actualidad: la serie entera, en su orden."""
    serie = [q for q in todas if q['serie'] == 'historia']
    return (f'<section class="wide del-atlas del-actualidad" aria-labelledby="h-del-historia"><div class="da-cab"><h2 id="h-del-historia"><a href="{pre}actualidad/#historia">Historia electoral · desde 1977</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Piezas anteriores">←</button><button type="button" class="da-next" aria-label="Más piezas">→</button></span></div>'
            '<ul class="carrusel">' +
            ''.join(f'<li><a href="{pre}actualidad/{q["slug"]}/">{imagen_carrusel(q, pre)}'
                    f'<span class="atlas-k">{q["lugar"]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in serie) +
            f'<li class="todas"><a href="{pre}actualidad/#historia"><b>Las {len(serie)} piezas de la serie →</b><span>Todas las elecciones generales desde 1977</span></a></li></ul>'
            '<script>(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})(document.currentScript.parentNode)</script></section>')


def portada(todas):
    for f, pre in ((os.path.join(RAIZ, 'index.html'), ''), (os.path.join(RAIZ, 'generales-2026', 'src', 'plantilla.html'), '../')):
        t = open(f, encoding='utf-8').read()
        if '<!--actualidad:ultimas-->' not in t:   # la franja va justo encima de la del Atlas
            t = t.replace('<!--atlas:ultimas-->', '<!--actualidad:ultimas--><!--/actualidad:ultimas-->\n<!--atlas:ultimas-->', 1)
        if '<!--actualidad:historia-->' not in t:   # la serie «Historia electoral», justo debajo de Actualidad
            t = t.replace('<!--/actualidad:ultimas-->', '<!--/actualidad:ultimas-->\n<!--actualidad:historia--><!--/actualidad:historia-->', 1)
        t = re.sub(r'<!--actualidad:historia-->.*?<!--/actualidad:historia-->',
                   lambda m: '<!--actualidad:historia-->' + franja_historia(todas, pre) + '<!--/actualidad:historia-->', t, flags=re.S)
        t = re.sub(r'<!--actualidad:ultimas-->.*?<!--/actualidad:ultimas-->',
                   lambda m: '<!--actualidad:ultimas-->' + franja_portada(todas, pre) + '<!--/actualidad:ultimas-->', t, flags=re.S)
        open(f, 'w', encoding='utf-8').write(t)
    json.dump([{'slug': q['slug'], 'figura': q.get('figura', 0)} for q in todas],
              open(os.path.join(SRC, 'miniaturas.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    for p in PIEZAS:
        pieza(p, PIEZAS)
    indice(PIEZAS)
    portada(PIEZAS)
    print('Actualidad:', len(PIEZAS), 'piezas')
