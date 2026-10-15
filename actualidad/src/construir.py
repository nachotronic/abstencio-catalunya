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
sys.path.insert(0, os.path.join(RAIZ, 'src'))
from territorios_rutas import enlaces_actualidad  # noqa: E402  páginas por territorio y tema de /elecciones/
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
        descripcion='En las generales de 2023 Junts sacó en Cataluña el 11,2 % (392.609 votos) y ganó en 465 secciones. En las autonómicas de 2024, con Puigdemont como candidato, el 21,6 % y 681.470 votos, y ganó en 1.936, aunque votó menos gente.',
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
                 ('https://www.ccoo.es/noticia:769574--Convocamos_huelga_general_para_el_11_de_noviembre&opc_id=8c53f4de8f8f09d2e54f19daf8d8ed95', 'CCOO, «Convocamos huelga general para el 11 de noviembre» (octubre de 2026)'),
                 ('https://www.diariodeleon.es/economia/261007/2099577/ugt-confirma-huelga-general-sera-11-noviembre.html', 'Diario de León, UGT confirma que la huelga general será el 11 de noviembre (7 de octubre de 2026)'),
                 ('https://es.euronews.com/2026/10/07/huelga-general-vivienda-espana-11-noviembre-ccoo-ugt', 'Euronews, España afronta una huelga general por la crisis de la vivienda el 11 de noviembre (7 de octubre de 2026)'),
                 ('https://diariodeavisos.elespanol.com/2026/10/huelga-general-11-noviembre-vivienda-espana/', 'Diario de Avisos, La huelga general por la vivienda se celebrará el 11 de noviembre (7 de octubre de 2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/07/la-primera-gran-huelga-general-desde-2012-y-la-unica-con-elecciones-generales/', 'EFE vía Infobae, La primera gran huelga general desde 2012 y la única con elecciones generales (7 de octubre de 2026)'),
                 ('https://recyt.fecyt.es/index.php/RevEsPol/article/view/38732', 'Revista de Estudios Políticos, Caínzos y Voces: Paro y voto: ¿afecta al voto la experiencia de desempleo? (2015)'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Fundación FOESSA, VIII Informe, Trujillo y Gómez: La segregación electoral interurbana en España (2019)'),
                 ('https://www.ine.es/dyngs/Prensa/EPA2T26.htm', 'INE, Encuesta de Población Activa, segundo trimestre de 2026 (28 de julio de 2026)'),
                 ('https://www.ine.es/prensa/anexo_tablas/es/EPA2T26_PRO.xlsx', 'INE, EPA 2T 2026: resultados por comunidad autónoma y provincia (28 de julio de 2026)'),
                 ('https://www.articulo14.es/economia/los-sindicatos-convocan-la-huelga-general-por-la-vivienda-el-11-de-noviembre-20261007.html', 'Artículo14, Los sindicatos convocan la huelga general por la vivienda el 11 de noviembre (7 de octubre de 2026)'),
                 ('https://forbes.es/ultima-hora/1036424/sordo-ccoo-aboga-por-una-movilizacion-amplia-que-reivindique-la-vivienda-pero-tambien-los-salarios/', 'Forbes España, Sordo (CCOO) aboga por una movilización «amplia» que reivindique la vivienda, pero también los salarios (4 de octubre de 2026)')],
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
                 ('https://www.infobae.com/espana/agencias/2026/10/08/tenso-enfrentamiento-entre-ayuso-y-mas-madrid-en-la-asamblea-tras-la-muerte-de-maricarmen/', 'Infobae / EFE, tenso enfrentamiento entre Ayuso y Más Madrid en la Asamblea (8-10-2026)'),
                 ('https://rtvc.es/muere-maricarmen-mujer-87-anos-desahuciada-madrid-avivo-protestas-7-octubre-2026/', 'RTVC, Muere Maricarmen, la mujer de 87 años desahuciada en Madrid que avivó las protestas (8-10-2026)'),
                 ('https://es.euronews.com/2026/09/27/la-manifestacion-por-maricarmen-y-el-problema-de-la-vivienda-acaba-en-una-acampada-en-sol-', 'Euronews, La manifestación por Maricarmen y el problema de la vivienda en España acaba en una acampada al estilo 15-M (27-9-2026)'),
                 ('https://www.esdiario.com/nacional/261001/199176/ayuso-yolanda-diaz-acampada-sol-maricarmen.html', 'ESdiario, Ayuso desarma a Yolanda Díaz y su apoyo a la acampada (1-10-2026)'),
                 ('https://www.newtral.es/elecciones-municipales-madrid-mapa-almeida/20230510/', 'Newtral, El mapa teñido de azul que usa Almeida es de los resultados autonómicos de 2021 y no de las municipales (10-5-2023)'),
                 ('https://www.ultimahora.es/noticias/elecciones-2019/2019/05/26/1082105/manuela-carmena-pierde-ayuntamiento-madrid-favor-del-anuncia-va.html', 'Última Hora, Resultados elecciones municipales 2019 Madrid: Carmena dice adiós (26-5-2019)'),
                 ('https://maldita.es/malditodato/20210506/mas-madrid-sorpaso-psoe-capital-otros-municipios-mira-donde', 'Maldita.es, Más Madrid da el sorpaso al PSOE gracias a Madrid capital y otros 82 municipios (6-5-2021)'),
                 ('https://maldita.es/malditodato/20230529/resultados-comunidad-madrid/', 'Maldita.es, Resultados Comunidad de Madrid: Ayuso logra la mayoría absoluta (29-5-2023)'),
                 ('https://www.moncloa.com/2023/06/04/psoe-madrid-lobato-gonzalez-2012397/', 'Moncloa.com, El PSOE de Madrid se prepara para una revolución interna contra Juan Lobato (4-6-2023)'),
                 ('https://www.elindependiente.com/espana/2023/07/24/el-pp-pierde-155-000-votos-en-madrid-respecto-a-las-autonomicas/amp/', 'El Independiente, El PP pierde 155.000 votos en Madrid respecto a las autonómicas (24-7-2023)'),
                 ('https://maldita.es/malditodato/20240418/voto-dual-pais-vasco/', 'Maldita.es, Votar al PSOE en las generales y al PNV y EH Bildu en las autonómicas: los efectos del voto dual vasco (18-4-2024)'),
                 ('https://recyt.fecyt.es/index.php/recp/article/view/84141', 'Revista Española de Ciencia Política, Dual voting and second-order effects in the quasi-simultaneous 2019 Spanish regional and national elections (2021)'),
                 ('https://www.eldiario.es/madrid/manuela-bergerot-activista-memoria-democratica-sustituye-monica-garcia-enfrentarse-ayuso_1_10702164.amp.html', 'elDiario.es, Manuela Bergerot, la activista por la memoria democrática que sustituye a Mónica García para enfrentarse a Ayuso (20-11-2023)'),
                 ('https://theobjective.com/espana/politica/2024-12-07/oscar-lopez-lider-psoe-madrid/', 'The Objective, Óscar López, elegido nuevo líder del PSOE en Madrid sin oposición (7-12-2024)'),
                 ('https://www.esdiario.com/nacional/260711/193015/oscar-lopez-rival-ayuso-almeida-espera-primarias-enma-lopez-reyes-maroto_amp.html', 'ESdiario, Óscar López, rival de Ayuso; Almeida espera a las primarias entre Enma López y Reyes Maroto (11-7-2026)'),
                 ('https://www.eldebate.com/espana/madrid/20260719/reyes-maroto-impone-enma-lopez-minima-primarias-psoe-sera-candidata-madrid_441075.html', 'El Debate, Reyes Maroto se impone a Enma López por la mínima en las primarias del PSOE y será la candidata en Madrid (19-7-2026)')],
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
                 ('https://www.lavanguardia.com/politica/20261008/11654274/antepone-primarias-aleja-entrada-frente-amplio-pesar-colau.html', 'La Vanguardia, Podemos antepone sus primarias y se aleja del Frente Amplio (8-10-2026)'),
                 ('https://www.elsaltodiario.com/politica/podemos-anuncia-primarias-abiertas-construir-candidatura', 'El Salto, Podemos ofrece primarias abiertas para elegir una candidatura de izquierdas (5/10/2026)'),
                 ('https://www.democrata.es/politica/sumar-tiende-la-mano-a-podemos-pero-enfria-las-primarias-mejor-acordar-que-competir-entre-nosotros/', 'Demócrata, Sumar tiende la mano a Podemos pero enfría las primarias: “Mejor acordar que competir entre nosotros” (6/10/2026)'),
                 ('https://www.elsaltodiario.com/elecciones/monica-garcia-ira-al-congreso-deja-puerta-abierta-candidata-del-frente-sea-colau', 'El Salto, Mónica García irá al Congreso y deja la puerta abierta a que la candidata del frente sea Colau (6/10/2026)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_2015', 'Wikipedia, Elecciones generales de España de 2015 (consultado 9/10/2026)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_2016', 'Wikipedia, Elecciones generales de España de 2016 (consultado 9/10/2026)'),
                 ('https://www.elindependiente.com/espana/2023/07/24/belarra-ajusta-cuentas-con-yolanda-diaz-ha-perdido-700-000-votos-por-invisibilizar-a-podemos/', 'El Independiente, Belarra ajusta cuentas con Yolanda Díaz: "Ha perdido 700.000 votos por invisibilizar a Podemos" (24/7/2023)'),
                 ('https://www.elsaltodiario.com/podemos/podemos-oficializa-ruptura-sumar-pasa-al-grupo-mixto', 'El Salto, Podemos oficializa su ruptura con Sumar y pasa al Grupo Mixto (5/12/2023)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-13092', 'BOE, Acuerdo de 27 de junio de 2024, de la Junta Electoral Central, de publicación de los resultados de las elecciones al Parlamento Europeo (2024)'),
                 ('https://maldita.es/malditodato/20240610/claves-elecciones-europeas-resultados-espana/', 'Maldita.es, Claves de las elecciones europeas 2024: datos y resultados en España (10/6/2024)'),
                 ('https://www.elsaltodiario.com/elecciones/yolanda-diaz-debe-sumar-provincias-medianas-revalidar-gobierno-coalicion', 'El Salto, Yolanda Díaz debe sumar en las provincias medianas para revalidar el Gobierno de coalición (11/6/2023)'),
                 ('https://maldita.es/malditodato/20191116/si-todos-los-votantes-de-mas-pais-hubieran-votado-a-unidas-podemos-el-bloque-de-izquierdas-habria-obtenido-dos-diputados-mas-en-las-elecciones-generales-2', 'Maldita.es, Si todos los votantes de Más País hubieran votado a Unidas Podemos el bloque de izquierdas habría obtenido dos diputados más en las elecciones generales (16/11/2019)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='vox-poblacion-nacida-fuera', fecha='2026-10-09',
        titulo='Vox saca casi lo mismo donde uno de cada tres vecinos nació fuera que donde casi nadie lo hizo', serie='29n',
        descripcion='La inmigración a Euskadi bajó ligeramente en 2025, según los datos que publica esta semana la prensa vasca. Euskadi es también donde menos vota a Vox: el 2,6% en 2023. En el resto de España, el voto a Vox apenas cambia entre las secciones con menos del 5% y con más del 30% de población nacida en el extranjero.',
        compara='El voto a Vox en las generales de julio de 2023 por sección censal, agrupado por el porcentaje de residentes nacidos en el extranjero del censo de 2021, en Cataluña, Euskadi, Navarra y el resto de España.',
        limites='Es un dato por sección, no por persona: no dice si quienes votan a Vox viven cerca de población inmigrante ni si la votan por eso. «Nacidos fuera» incluye a españoles nacidos en el extranjero, y los extranjeros sin nacionalidad no votan en generales. Censo de 2021 frente a voto de 2023. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.naiz.eus/info/noticia/20261007/la-foto-real-de-la-inmigracion-en-la-cav-en-2025-bajo-y-los-magrebies-solo-fueron-el-12', 'Naiz, la inmigración en la CAV en 2025 (7-10-2026)'),
                 ('https://es.eustat.eus/estad/id_51/ti_estadistica-de-movimientos-migratorios/ultima-nota-prensa.html', 'Eustat, Movimientos migratorios de la C.A. de Euskadi. 2025 (7/10/2026)'),
                 ('https://www.ine.es/dyngs/Prensa/ECP2T26.htm', 'INE, Estadística Continua de Población. 1 de julio de 2026. Datos provisionales (6/8/2026)'),
                 ('https://es.euronews.com/2026/08/06/espana-50-millones-habitantes-1-cada-5-nacio-extranjero', 'Euronews, España está a un paso de los 50 millones de habitantes: más de 1 de cada 5 nació en el extranjero (6/8/2026)'),
                 ('https://ine.es/dyngs/Prensa/ECP4T25.pdf', 'INE, Estadística Continua de Población. 1 de enero de 2026. Datos provisionales (12/2/2026)'),
                 ('https://upo.es/upotec/contenidos/noticias/2021/feb/26/un-estudio-liderado-por-la-upo-analiza-las-causas-/', 'Universidad Pablo de Olavide, Un estudio liderado por la UPO analiza las causas del ascenso de VOX en las elecciones andaluzas de 2018 (26/2/2021)'),
                 ('https://www.eldiario.es/piedrasdepapel/Vox-derecha-populista-escision-PP_6_850474947.html', 'elDiario.es (Piedras de Papel), Vox: nueva derecha populista o escisión radical del PP (26/12/2018)'),
                 ('https://doi.org/10.1177/2053168019851680', 'Turnbull-Dugarte, «Explaining the end of Spanish exceptionalism and electoral support for Vox», Research & Politics (2019)'),
                 ('https://es.ara.cat/politica/radiografia-votante-vox-catalunya_1_3879014.html', 'Ara, radiografía del votante de Vox en Cataluña (2021)'),
                 ('https://www.ondavasca.com/inflacion-y-sanidad-las-dos-principales-preocupaciones/', 'Onda Vasca, Inflación y sanidad, las dos principales preocupaciones (24/6/2023)'),
                 ('https://www.boe.es/boe/dias/2019/05/30/pdfs/BOE-A-2019-8070.pdf', 'BOE, Junta Electoral Central: resumen de resultados de las generales del 28 de abril de 2019 (30/5/2019)'),
                 ('https://www.boe.es/boe/dias/2019/12/02/pdfs/BOE-A-2019-17344.pdf', 'BOE, Junta Electoral Central: resumen de resultados de las generales del 10 de noviembre de 2019 (2/12/2019)'),
                 ('https://www.boe.es/boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf', 'BOE, Junta Electoral Central: resumen de resultados de las generales del 23 de julio de 2023 (1/9/2023)'),
                 ('https://www.democrata.es/encuestas/elecciones-generales/abascal-elecciones-29-n-ultima-oportunidad-vox-remigracion/', 'Demócrata, Abascal presenta el 29-N como la "última oportunidad" de los españoles y promete "remigración" y prioridad nacional (5 de octubre de 2026)'),
                 ('https://www.eldebate.com/espana/pais-vasco/20260211/lendakari-cifra-937-aumento-inmigracion-ultimos-25-anos-pide-afrontar-problema-honestidad_384163.html', 'El Debate, El lendakari cifra en un 937 % el aumento de la inmigración en los últimos 25 años y pide afrontar el problema «con honestidad» (11 de febrero de 2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/vox-poblacion-nacida-fuera.jpg', ancho=1280, alto=720, ia=True,
                  pie='Vecinos de distintos orígenes en una calle, junto a una urna.'),
    ),
    dict(
        slug='almeida-feijoo-madrid', fecha='2026-10-13',
        titulo='Tras el saludo gélido de Sánchez en el 12‑O: en Madrid, el PP de Almeida sacó más votos que el de Feijóo, con 85.000 votantes menos', serie='29n',
        descripcion='Sánchez apenas cruzó palabras con Ayuso y Almeida en el desfile, a siete semanas del 29N. En la capital, el PP sacó 729.304 votos en las municipales de mayo de 2023 y 720.547 en las generales de julio, cuando votó más gente. Vox subió del 9,1% al 12,4%.',
        compara='El voto al PP y a Vox en la ciudad de Madrid en las municipales y en las generales de 2011, 2015, 2019 y 2023, en total, por distrito y en las 2.450 secciones censales de 2023.',
        limites='Son elecciones distintas con electorados distintos: en las municipales votan también los residentes de la UE y la participación fue 5 puntos más baja. Los datos no dicen cuántos votantes cambiaron de papeleta ni por qué. En 2019 se compara con las generales de abril; con las de noviembre el resultado es el contrario. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.infobae.com/espana/agencias/2026/10/12/arranca-el-desfile-del-12-de-octubre-con-abucheos-a-sanchez-en-plena-precampana-electoral/', 'EFE vía Infobae, Arranca el desfile del 12 de octubre con abucheos a Sánchez en plena precampaña electoral (12-10-2026)'),
                 ('https://okdiario.com/espana/tenso-saludo-sanchez-ayuso-almeida-desfile-del-12-o-20531484', 'OKDiario, tenso saludo de Sánchez a Ayuso y Almeida en el desfile del 12-O (12-10-2026)'),
                 ('https://www.libertaddigital.com/espana/2026-10-12/asi-ha-sido-el-saludo-de-sanchez-a-ayuso-y-almeida-en-el-desfile-del-12-o-7474154/', 'Libertad Digital, Así ha sido el saludo de Sánchez a Ayuso y Almeida en el desfile del 12-O (12-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261012/pedro-sanchez-recibido-insultos-pitos-abucheos-llegada-desfile-militar/1003744417117_0.html', 'El Español, Pedro Sánchez, recibido con insultos, pitos y abucheos a su llegada al desfile militar (12-10-2026)'),
                 ('https://libertaddigital.com/espana/2026-10-10/feijoo-ayuso-y-almeida-se-conjuran-para-una-reconstruccion-nacional-tras-el-29n-no-propongo-una-simple-alternancia-7473700', 'Libertad Digital, Feijóo, Ayuso y Almeida se conjuran para una reconstrucción nacional tras el 29N (10-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-10/almeida-campana-electoral/', 'The Objective, Almeida en el mitin del PP en Ifema (10-10-2026)'),
                 ('https://okdiario.com/espana/almeida-presentacion-candidatos-feijoo-municipales-tenemos-mejor-equipo-mejor-seleccionador-19022224', 'OKDiario, presentación de candidatos municipales del PP en Santiago (18-7-2026)'),
                 ('https://www.eldiariodemadrid.es/articulo/politica/almeida-victoria-municipal-pp-feijoo-moncloa-elecciones-2027/20260718144908137740.html', 'El Diario de Madrid, Almeida: la victoria municipal, primer paso hacia la Moncloa (18-7-2026)'),
                 ('https://www.eldebate.com/espana/madrid/20260615/almeida-ampliaria-mayoria-absoluta-escano-hoy-hubiera-elecciones-segun-encuesta-gad3_428643.html', 'El Debate, encuesta de GAD3 para el grupo municipal del PP (15-6-2026)'),
                 ('https://elpais.com/ccaa/2019/06/15/madrid/1560578298_100220.html', 'El País, investidura de Almeida como alcalde (15-6-2019)'),
                 ('https://www.ultimahora.es/noticias/elecciones-28m/2023/06/17/1958799/madrid-ose-luis-martinez-almeida-proclamado-alcalde-mayoria-absoluta.html', 'Última Hora / Europa Press, Almeida proclamado alcalde con mayoría absoluta (17-6-2023)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_municipales_de_2011_en_Madrid', 'Wikipedia, Elecciones municipales de 2011 en Madrid (consultado 13-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_municipales_de_2015_en_Madrid', 'Wikipedia, Elecciones municipales de 2015 en Madrid (consultado 13-10-2026)'),
                 ('https://e-archivo.uc3m.es/bitstream/handle/10016/34931/elecciones_RIS_2017.pdf?sequence=1', 'Riera, Gómez, Mayoral, Barberá y Montero, Elecciones municipales en España. La personalización del voto, Revista Internacional de Sociología (2017)'),
                 ('https://reis.cis.es/index.php/reis/article/view/1002', 'Clara Riba, Voto dual y abstención diferencial, REIS 91 (2000)'),
                 ('https://www.democrata.es/encuestas/elecciones-generales/encuesta-elecciones-generales-pp-vox-pierden-cuatro-escanos-pero-mantienen-198-frente-107-psoe-segun-gad3/', 'Demócrata, encuesta de GAD3 para ABC (12-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-09/encuestas-pp-vox-200-escanos/', 'The Objective, encuestas para el 29N (9-10-2026)')],
        enlaces=[],
        lugar='Madrid',
        foto=dict(src='img/actualidad/fotos/almeida-feijoo-madrid.jpg', ancho=1280, alto=720, ia=True,
                  pie='Material militar, el Congreso y una urna.'),
    ),
    dict(
        slug='aceituna-de-mesa-pueblos', fecha='2026-10-13',
        titulo='La aceituna de mesa, por debajo de coste: en sus dos grandes comarcas, el PP no ganó en ninguno de los 23 pueblos en 2023', serie='29n',
        descripcion='Los agricultores denuncian que se les paga la aceituna por debajo de lo que cuesta recogerla. En las comarcas de Osuna y Marchena, las de más olivar de mesa de Andalucía, el PSOE sacó el 43,7% en las generales de 2023, diez puntos más que en el conjunto de la comunidad. Vox se quedó en el 11,1%.',
        compara='El voto en las generales de 2004 a 2023 y en las municipales de 2023 de los 23 municipios de las dos comarcas agrarias con más olivar de aceituna de mesa de Andalucía (Campiña-Sierra Sur, con sede en Osuna, y Serranía Sudoeste, con sede en Marchena), frente a Andalucía y España.',
        limites='No hay datos oficiales de cultivo por municipio: la selección usa la superficie de olivar de mesa de 2019 por comarca agraria de la Junta, que no cuenta la hojiblanca de doble aptitud, así que deja fuera zonas de verdeo de Córdoba y Antequera. Son datos por municipio: no dicen cómo votan los agricultores, que son una parte de los vecinos. No se puede atribuir ningún cambio de voto a los precios de la aceituna. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.juntadeandalucia.es/organismos/agapa/areas/agricultura-ganaderia/caracterizacion-agraria/informes-comarcales.html', 'Junta de Andalucía (AGAPA), informes de caracterización agraria por oficina comarcal (2023): Campiña-Sierra Sur y Serranía Sudoeste'),
                 ('https://cordopolis.eldiario.es/cordoba-hoy/provincia/situacion-insostenible-aceituna-mesa-cordoba-agricultores-plantean-recoger-cosecha_1_13575103.html', 'Cordópolis, situación insostenible de la aceituna de mesa en Córdoba (12-10-2026)'),
                 ('https://www.cordobahoy.es/articulo/provincia/asaja-cordoba-llama-agricultores-denunciar-precios-aceituna-hojiblanca-verdeo-debajo-costes/20261013111506204040.html', 'Córdoba Hoy, ASAJA Córdoba llama a denunciar precios de la hojiblanca de verdeo por debajo de costes (13-10-2026)'),
                 ('https://agroinformacion.com/preparan-una-denuncia-tras-detectarse-operaciones-comerciales-sospechosas-con-ofertas-por-debajo-de-costes-en-el-sector-de-la-aceituna-de-mesa', 'Agroinformación / Europa Press, denuncia por ofertas por debajo de costes en la aceituna de mesa (9-10-2026)'),
                 ('https://www.elpespunte.es/articulo/agro/verdeo-que-llega/20260924195138153340.html', 'El Pespunte, El verdeo que llega (24-9-2026)'),
                 ('https://www.asaja.com/asaja-coag-y-union-de-uniones-convocan-una-gran-tractorada-en-madrid-el-28-de-octubre-por-un-campo-con-futuro/', 'ASAJA, ASAJA, COAG y Unión de Uniones convocan una gran tractorada en Madrid el 28 de octubre (9-10-2026)'),
                 ('https://www.eldiario.es/economia/campo-anuncia-gran-tractorada-madrid-28-octubre-organizaciones-agrarias-divididas_1_13574700.html', 'elDiario.es, el campo anuncia una gran tractorada en Madrid el 28 de octubre con las organizaciones divididas (9-10-2026)'),
                 ('https://www.agroalimentarias-andalucia.coop/sectores/aceituna-de-mesa', 'Cooperativas Agro-alimentarias de Andalucía, sector de la aceituna de mesa'),
                 ('https://www.juntadeandalucia.es/presidencia/portavoz/tierraymar/219127/ConsejeriadeAgriculturaPescaAguayDesarrolloRural/aforo/produccion/olivar/campana/20262027/aceite/oliva/aceituna/Jaen/agricultura/Fernandez/Pacheco', 'Junta de Andalucía, aforo de aceituna de mesa 2026/27'),
                 ('https://financialfood.es/upa-andalucia-denuncia-crisis-de-precios-en-aceituna-de-mesa/', 'Financial Food, UPA Andalucía denuncia crisis de precios en aceituna de mesa (3-9-2026)'),
                 ('https://agroinformacion.com/se-cumplen-siete-anos-de-aranceles-para-la-aceituna-negra-en-eeuu-con-260-millones-en-perdidas-y-aun-todo-por-solucionar/', 'Agroinformación, siete años de aranceles a la aceituna negra en EE. UU. (28-11-2024)'),
                 ('https://www.agrodigital.com/2026/01/16/la-aceituna-europea-tiene-aranceles-en-eeuu-que-sus-competidores/', 'Agrodigital, la aceituna europea tiene más aranceles en EE. UU. que sus competidores (16-1-2026)'),
                 ('https://www.menorca.info/actualidad/nacional/2024/02/14/2105937/agricultores-colapsan-sevilla-bloquean-entrada-salida-andalucia-jaen.html', 'EFE vía Menorca.info, los agricultores colapsan Sevilla (14-2-2024)'),
                 ('https://www.eldiario.es/politica/ultraderecha-enciende-cosechadora-recoger-votos-perdidos-agitando-campo_1_10909992.html', 'elDiario.es, la ultraderecha enciende la cosechadora (10-2-2024)'),
                 ('https://aecpa.es/files/view/pdf/congress-papers/16-0/2833/', 'Negral y Sánchez-García, La semilla de Vox, ¿quién votó a la derecha radical populista en Castilla y León? (ponencia AECPA)')],
        enlaces=[],
        lugar='Sevilla',
    ),
    dict(
        slug='ultimo-escano-29n', fecha='2026-10-14',
        titulo='Qué provincias pueden decidir el 29N: en 17, el último escaño se resolvió en 2023 por menos de 5.000 votos', serie='29n',
        descripcion='En Girona, al PP le faltaron 285 votos para quitarle el último escaño a Junts; en Cantabria, 404 para quitárselo a Vox. Repasamos el último diputado de cada provincia en 2023 y el margen con el que se decidió, sin proyectar el resultado de 2026.',
        compara='El último escaño de cada una de las 52 circunscripciones en las generales de julio de 2023 y los votos que le faltaron al aspirante más cercano para quitárselo.',
        limites='No es una proyección de 2026: usa los votos de 2023. El margen mide los votos adicionales que necesitaba el aspirante, sin que nadie más cambie; en la práctica los votos se mueven entre varios partidos a la vez. Incluye el voto exterior (CERA), por eso difiere de las cifras de la noche electoral. Las cifras son cálculo propio con la regla D\'Hondt y la barrera del 3% sobre voto válido.',
        fuentes=[(INTERIOR[0], 'Ministerio del Interior, resultados electorales (Infoelectoral), vía pollspaindata, con voto exterior (CERA)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742', 'BOE, Real Decreto 806/2026, de 5 de octubre, de disolución del Congreso y del Senado y de convocatoria de elecciones (6-10-2026)'),
                 ('https://www.diariodeleon.es/nacional/261006/2099442/elecciones-generales-2026-reparto-escanos-circunscripcciones.html', 'Europa Press vía Diario de León, Madrid sumará un escaño y Cádiz perderá uno (6-10-2026)'),
                 ('https://www.elindependiente.com/espana/madrid/2023/07/29/recuento-de-voto-cera-en-madrid-el-pp-casi-duplica-al-psoe-y-sumar-gana-a-vox/amp/', 'El Independiente, recuento del voto CERA en Madrid (29-7-2023)'),
                 ('https://www.eldiario.es/politica/psoe-recurrira-supremo-negativa-junta-electoral-revisar-30-000-votos-nulos-23j_1_10439216.html', 'elDiario.es, el PSOE recurrirá al Supremo la negativa a revisar 30.000 votos nulos (10-8-2023)'),
                 ('https://theobjective.com/espana/politica/2023-07-28/vox-diputado-cantabria-voto-cera/', 'The Objective, Vox mantiene su diputado en Cantabria tras el voto CERA (28-7-2023)'),
                 ('https://www.eldiario.es/politica/ultimo-escano-provincia-ganadores-perderdores-en-directo_1_10394283.html', 'elDiario.es, el último escaño en cada provincia (23-7-2023)'),
                 ('https://maldita.es/malditodato/las-batallas-mas-ajustadas-de-estas-elecciones-generales-el-voto-extranjero-podria-cambiar-el-ultimo-escano-en-algunas-provincias/', 'Maldita.es, las batallas más ajustadas de las generales (10-11-2019)'),
                 ('https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso', 'Annick Laruelle, El reparto de los escaños en el Congreso, Campusa UPV/EHU (24-5-2019)'),
                 ('https://recyt.fecyt.es/index.php/recp/article/download/37589/21106', 'Penadés y Santiuste, La desigualdad en el sistema electoral español y el premio a la localización del voto, Revista Española de Ciencia Política 32 (2013)'),
                 ('https://valenciaplaza.com/valenciaplaza/asi-esta-en-10n-segun-el-politologo-pablo-simon', 'Valencia Plaza, así está el 10N según el politólogo Pablo Simón (29-9-2019)'),
                 ('https://www.esdiario.com/nacional/261013/200153/aun-dudas-votar-provincias-ultimo-escano-29-n-decidirse-punado-votos.html', 'ESdiario, las provincias donde el último escaño del 29-N puede decidirse por un puñado de votos (13-10-2026)'),
                 ('https://www.elplural.com/politica/espana/lucha-ultimo-escano-provincias-estaran-juego-elecciones_801043102', 'El Plural, la lucha por el último escaño (12-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='izquierda-dividida-29n', fecha='2026-10-14',
        titulo='Dónde puede costar más la división a la izquierda: en ocho provincias, Sumar ganó o perdió un escaño en 2023 por menos de 5.000 votos', serie='29n',
        descripcion='El Frente Amplio, Podemos, ERC y Compromís negocian sus papeletas antes del cierre de coaliciones del 16 de octubre. En Tarragona, Sumar habría perdido su escaño con 1.343 votos menos; en Santa Cruz de Tenerife se quedó a 1.565 de ganarlo. Datos de 2023 y de 2019, separando lo medido de lo hipotético.',
        compara='Los escaños que Sumar ganó o perdió por menos de 10.000 votos en julio de 2023, las provincias donde dos listas de izquierda se quedaron sin escaño, el mismo cálculo para noviembre de 2019 y una simulación cerrada de Unidas Podemos y Más País juntos en 2019.',
        limites='No es una proyección de 2026. Los márgenes son votos adicionales necesarios sin que nadie más cambie. La simulación de 2019 suma los votos sin pérdidas, por eso es un límite superior: los estudios citados indican que las coaliciones suelen sumar menos que sus partes. Cálculo propio con D\'Hondt, barrera del 3% sobre voto válido y voto exterior (CERA) incluido.',
        fuentes=[(INTERIOR[0], 'Ministerio del Interior, resultados electorales (Infoelectoral), vía pollspaindata, con voto exterior (CERA)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#acuarentaycuatro', 'BOE, Ley Orgánica del Régimen Electoral General, artículo 44 (plazo de coaliciones)'),
                 ('https://cadenaser.com/nacional/2026/10/12/la-nueva-coalicion-de-izquierdas-frente-amplio-acuerda-proponer-a-ada-colau-como-candidata-para-las-elecciones-del-29-n-cadena-ser/', 'Cadena SER, el Frente Amplio propone a Ada Colau como candidata (12-10-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/13/colau-insiste-en-la-candidatura-unica-de-las-izquierdas-para-el-29-n-hay-tiempo-para-llegar-a-un-acuerdo-cadena-ser/', 'Cadena SER, Colau insiste en la candidatura única (13-10-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/13/irene-montero-evita-polemizar-sobre-la-candidatura-de-ada-colau-con-el-frente-amplio-y-confirma-que-siguen-las-conversaciones-cadena-ser/', 'Cadena SER, Irene Montero confirma que siguen las conversaciones (13-10-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/12/erc-y-podemos-confirman-su-acuerdo-de-colaboracion-para-las-elecciones-del-29-n-cadena-ser/', 'Cadena SER, ERC y Podemos confirman su acuerdo de colaboración (12-10-2026)'),
                 ('https://cadenaser.com/cataluna/2026/10/13/erc-vuelve-a-cerrar-la-puerta-a-un-acuerdo-para-el-frente-amplio-que-reclama-rufian-porque-diluiria-las-siglas-del-partido-sercat/', 'SER Catalunya, ERC vuelve a cerrar la puerta al Frente Amplio (13-10-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/11/el-problema-electoral-de-la-izquierda-alternativa-uno-de-cada-cuatro-votantes-de-ese-espacio-votaria-ahora-al-psoe-cadena-ser/', 'Cadena SER, el problema electoral de la izquierda alternativa (11-10-2026)'),
                 ('https://www.eldiario.es/comunitat-valenciana/politica/izquierda-valenciana-negocia-candidatura-unica-liderada-compromis-e-evitar-espectaculo-madrid-barcelona_1_13581226.html', 'elDiario.es, la izquierda valenciana negocia una candidatura única liderada por Compromís'),
                 ('https://maldita.es/malditodato/20191116/si-todos-los-votantes-de-mas-pais-hubieran-votado-a-unidas-podemos-el-bloque-de-izquierdas-habria-obtenido-dos-diputados-mas-en-las-elecciones-generales-2/', 'Maldita.es, si los votantes de Más País hubieran votado a Unidas Podemos (16-11-2019)'),
                 ('https://cordopolis.eldiario.es/cordoba-hoy/sociedad/politologo-demuestra-coalicion-e-iu-provoco-perdida-votos_1_12725560.html', 'Cordópolis, Víctor Gago Rivas (USAL) sobre la pérdida de votos de la coalición de Podemos e IU en 2016'),
                 ('https://dialnet.unirioja.es/descarga/articulo/8166654.pdf', 'Miguel Ángel Sevilla Duro, El sistema electoral del Congreso en las generales del 10 de noviembre de 2019, Revista de Derecho Electoral 32 (2021)'),
                 ('https://www.redalyc.org/pdf/997/99715164005.pdf', 'Jorge Urdánoz Ganuza, Umbrales de representación y proporcionalidad, REIS 121 (2008)'),
                 ('https://ara.cat/es/articulo-pablo-simon-manipulacion-electoral_0_1481252043.html', 'Pablo Simón, Una obra maestra de la manipulación electoral, Ara (30-11-2015)'),
                 ('https://www.eldiario.es/piedrasdepapel/efecto-par-impar-sistema-electoral_132_11298372.html', 'Ferran Martínez i Coma e Ignacio Lago, el efecto par e impar del sistema electoral, Piedras de Papel (17-4-2024)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='vivienda-inmigracion-economia-cis', fecha='2026-10-14',
        titulo='Vivienda, inmigración y economía: en el CIS de octubre la vivienda salta del 37,5% al 55,7% y ya es el problema más citado por los votantes de PP, PSOE y Sumar', serie='29n',
        descripcion='PP y PSOE abren la campaña del 29N hablando de vivienda. En el barómetro de octubre, la vivienda va del 81% de los votantes de Sumar al 35% de los de Vox, para quienes solo la supera el Gobierno; la inmigración apenas se mueve y la economía es la que menos distingue a los electorados.',
        compara='El porcentaje de votantes de cada partido en 2023 que cita la vivienda, la inmigración y la crisis económica entre los tres principales problemas de España, según el avance del barómetro del CIS de octubre de 2026, con septiembre y julio como referencia. El mapa muestra el porcentaje de hogares de alquiler por provincia en el censo de 2021, como contexto.',
        limites='Las entrevistas de octubre son del 1 al 6 de octubre. En octubre, la pregunta por los problemas llegó después de siete preguntas sobre vivienda; en septiembre, después de preguntas sobre Ceuta, los incendios y el clima. Parte de la subida de la vivienda puede deberse a ese orden, y no se puede separar. El recuerdo de voto agrupa en Sumar a los votantes de Podemos; los microdatos de octubre, que permitirían separarlos por intención de voto, aún no están publicados. Las respuestas son espontáneas y las codifica el CIS. El mapa provincial y las cifras por sección son contexto territorial: no describen a votantes individuales.',
        fuentes=[('https://www.cis.es/documents/d/guest/3582-multi_a-xlsx', 'CIS, estudio 3582, barómetro de octubre de 2026 (avance), resultados y cruces por recuerdo de voto (hoja RV EG23)'),
                 ('https://www.cis.es/documents/d/guest/es3582mar_a-pdf', 'CIS, estudio 3582, marginales y ficha técnica'),
                 ('https://www.cis.es//documents/20117/14250083/3577-multi.xlsx/fc673352-aef6-cdf6-f73c-8ca58e1471c7?version=1.0&t=1790163563423&download=true', 'CIS, estudio 3577, barómetro de septiembre de 2026, resultados y cruces por recuerdo de voto (hoja RV EG23)'),
                 ('https://www.cis.es/documents/20117/14250083/MD3577.zip/71da2723-5a10-0e95-7127-8531f06a816d?version=1.0&t=1790163543856', 'CIS, estudio 3577, microdatos'),
                 ('https://www.cis.es//documents/20117/14189298/3571-multi.xlsx/5f2e2f9b-af18-0c6c-54c3-656bb42fc8ee?version=1.0&t=1788779949743&download=true', 'CIS, estudio 3571, barómetro de julio de 2026, cruces por recuerdo de voto'),
                 ('https://www.cis.es/en/w/avance-de-resultados-del-estudio-3582-bar%C3%B3metro-de-octubre-2026-', 'CIS, avance de resultados del estudio 3582 (14-10-2026)'),
                 ('https://www.ine.es/censos2021/', 'INE, censo de población y viviendas de 2021 (régimen de tenencia de los hogares)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/05/feijoo-la-vivienda-ha-sido-el-fracaso-de-este-gobierno-y-debe-ser-el-exito-del-siguiente/', 'EFE vía Infobae, Feijóo: la vivienda ha sido el fracaso de este Gobierno (5-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-05/sanchez-elecciones-decretos/', 'The Objective, Sánchez convoca elecciones (5-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/10/10/feijoo-sube-el-tono-para-una-campana-dura-con-la-corrupcion-y-la-inmigracion-como-ejes/', 'El Independiente, Feijóo sube el tono para una campaña dura (10-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/abascal-promete-pagar-pensiones-y-garantizar-vivienda-como-sea-y-refuerza-su-llamamiento-al-voto-presencial/', 'Demócrata, Abascal en Estepona (11-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/09/14/la-vivienda-sigue-como-primer-problema-y-la-inmigracion-baja-a-la-tercera-plaza-pese-a-la-crisis-de-ceuta/', 'Infobae, la vivienda sigue como primer problema (14-9-2026)'),
                 ('https://www.articulo14.es/economia/siete-de-cada-diez-electores-de-vox-culpa-a-la-inmigracion-del-problema-de-la-vivienda-20261004.html', 'Artículo 14 y Winston, siete de cada diez electores de Vox culpan a la inmigración del problema de la vivienda (4-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/preocupaciones-votantes-elecciones-29n/', 'Demócrata, resumen de un análisis de El País sobre las prioridades de los votantes (11-10-2026)'),
                 ('https://theobjective.com/economia/2026-10-13/estefania-molina-politologa-sobre-las-elecciones-si-la-gente-pone-sus-ahorros-en-una-vivienda-pp-y-psoe-no-promocionaran-que-caiga-el-precio-es-el-patrimonio-de-su-votante/', 'The Objective, entrevista a la politóloga Estefanía Molina (13-10-2026)')],
        enlaces=[],
        lugar='España',
        actualizado='2026-10-14',
        correcciones='14-10-2026: actualizada con el avance del barómetro de octubre (estudio 3582), publicado a las 12:30. La versión anterior usaba el de septiembre. Se retira la cifra de Podemos por intención de voto, calculada con los microdatos de septiembre.',
        foto=dict(src='img/actualidad/fotos/vivienda-inmigracion-economia-cis.jpg', ancho=1280, alto=720, ia=True,
                  pie='Unas llaves y fachadas de edificios de viviendas.'),
    ),
    dict(
        slug='pensiones-barrios-envejecidos', fecha='2026-10-14',
        titulo='Abascal promete pagar las pensiones «como sea», pero Vox saca su peor resultado en los barrios más envejecidos: 9,8%, frente al 16,2% en los más jóvenes', serie='29n',
        descripcion='Las pensiones entran en la campaña del 29N. En el 10% de secciones con más vecinos de 65 años o más, el PP sacó el 43,6% en 2023 y Vox, el 9,8%. El patrón se repite en las grandes ciudades y a igual renta.',
        compara='El voto en las generales de 2023 (y de 2015) en las 34.737 secciones censales de España, agrupadas en diez tramos según el porcentaje de vecinos de 65 años o más en el censo de 2021; la misma comparación en las ciudades de más de 75.000 electores y dentro de cada quinto de renta.',
        limites='Son datos de secciones, no de personas: no dicen cómo votan los mayores, sino cómo votan los barrios donde viven más mayores. El peso de los mayores es el del censo de 2021. Porcentajes sobre votos a candidaturas, sin voto exterior. Las citas de Feijóo en esRadio, Saiz y Figaredo llegan a través de otros medios.',
        fuentes=[INTERIOR, INE_CENSO, INE,
                 ('https://www.ine.es/dyngs/Prensa/es/EG2026.htm', 'INE, nota de prensa del censo electoral para las generales de 2026 (9-10-2026)'),
                 ('https://www.ine.es/oficina_censo/elecgen2026/Elecgral_2026_cc_tab9.xlsx', 'INE, Oficina del Censo Electoral, electores por edad, generales de 2026 (cálculo propio de los de 65 años o más)'),
                 ('https://www.inclusion.gob.es/en/w/la-pension-media-del-sistema-de-la-seguridad-social-alcanza-los-1.374-6-euros-en-septiembre-un-4-6-mas-alta-que-hace-un-ano', 'Ministerio de Inclusión y Seguridad Social, nómina de pensiones de septiembre de 2026'),
                 ('https://www.eleconomista.es/economia/noticias/14020309/10/26/ramiro-trabajador-con-43-anos-cotizados-me-han-recortado-la-pension-de-por-vida-un-24-por-jubilarme-antes-de-lo-previsto-en-contra-de-mi-voluntad.html', 'elEconomista, Ramiro, 43 años cotizados y un recorte del 24% (12-10-2026)'),
                 ('https://www.eldiario.es/economia/congreso-aprueba-tramitar-jubilacion-anticipada-40-anos-cotizados-penalizaciones_1_13530745.html', 'elDiario.es, el Congreso aprueba tramitar la jubilación anticipada sin penalizaciones con 40 años cotizados (22-9-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/abascal-promete-pagar-pensiones-y-garantizar-vivienda-como-sea-y-refuerza-su-llamamiento-al-voto-presencial/', 'Demócrata, Abascal en Estepona (11-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261014/feijoo-promete-revalorizar-pensiones-actuales-ipc-crear-sistema-publico-viable-garantizarlas-jovenes/1003744417956_0.html', 'El Español, Feijóo en Huesca (14-10-2026)'),
                 ('https://www.infobae.com/economia/2026/10/13/feijoo-despeja-la-duda-sobre-que-hara-con-las-pensiones-si-llega-a-la-moncloa-las-subira-con-el-ipc/', 'Infobae y Europa Press, Feijóo en esRadio (13-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-07/saiz-revalorizacion-pensiones-pp-vox/', 'The Objective y Europa Press, Elma Saiz sobre la revalorización (7-10-2026)'),
                 ('https://www.eldiario.es/economia/vox-defiende-reforma-privatizacion-pensiones-da-muerto-sistema-publico-actual_1_13565422.html', 'elDiario.es, Figaredo (Vox) en El Debate sobre las pensiones (6-10-2026)'),
                 ('https://www.articulo14.es/economia/el-voto-del-miedo-los-ingresos-de-casi-la-mitad-del-censo-depende-del-gobierno-20261013.html', 'Artículo 14, declaraciones de Luis Miller (CSIC) (13-10-2026)'),
                 ('https://fedea.net/instituciones-envejecimiento-y-equidad-intergeneracional/', 'José Ignacio Conde-Ruiz, Instituciones, envejecimiento y equidad intergeneracional, Fedea (julio de 2026)'),
                 ('https://www.eldiario.es/piedrasdepapel/edad-voto-european-edition_132_4867767.html', 'Piedras de Papel, Dime tu edad y te diré qué votas (20-5-2014)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pensiones-barrios-envejecidos.jpg', ancho=1280, alto=720, ia=True,
                  pie='Unas gafas, una carta de la pensión y un jubilado en el balcón.'),
    ),
    dict(
        slug='acampada-sol-distrito-centro', fecha='2026-10-14',
        titulo='Almeida pone a los acampados de Sol «en el mismo plano» que los ultras: Centro, el distrito con más inquilinos de Madrid, es donde Más Madrid y Podemos-IU sacaron su mejor resultado, el 41%', serie='vivienda',
        descripcion='La acampada por la vivienda sigue en la Puerta del Sol desde el 26 de septiembre. Centro es el distrito de Madrid con más hogares de alquiler, el 37,9%, y donde Más Madrid y Podemos-IU sacaron su mejor resultado en las municipales de 2023: el 41,0%.',
        compara='El porcentaje de hogares de alquiler (censo de 2021) y el voto en las municipales de 2015, 2019 y 2023 y en las generales de 2023 en los 21 distritos de Madrid, agregando las secciones censales.',
        limites='Son datos de distritos y secciones, no de personas: no dicen quién acampa ni a quién vota. Más Madrid y Podemos-IU se suman como espacio a la izquierda del PSOE. Porcentajes sobre votos a candidaturas; el PP sale con un 44,3% en la ciudad frente al 44,5% oficial, por la diferencia de denominador. Las palabras de Almeida llegan a través de Europa Press y otros medios.',
        fuentes=[INTERIOR, INE_CENSO,
                 ('https://www.diariodeleon.es/nacional/260927/2098519/miles-personas-claman-medidas-vivienda-desahucio-maricarmen.html', 'Diario de León, miles de personas claman por la vivienda tras el desahucio de Maricarmen (27-9-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/12/crece-la-tension-en-sol-tras-la-llegada-de-colectivos-ultras-para-increpar-a-los-acampados-cadena-ser/', 'Cadena SER, tensión en Sol tras la llegada de ultras (12-10-2026)'),
                 ('https://cadenaser.com/cmadrid/2026/10/13/cuatro-detenidos-por-desobediencia-y-altercados-publicos-en-los-enfrentamientos-provocados-por-grupos-ultras-en-la-acampada-de-sol-radio-madrid/', 'Cadena SER, cuatro detenidos en Sol (13-10-2026)'),
                 ('https://www.eldiario.es/madrid/somos/almeida-afea-acampados-sol-privaticen-espacio-publico-alcalde-sigue-aprobando-enajenaciones_1_13582073.html', 'elDiario.es y Europa Press, Almeida sobre los acampados (13-10-2026)'),
                 ('https://www.diariosigloxxi.com/texto-s/mostrar/678191/almeida-estudiara-ayudas-comerciantes-sol-preocupa-presencia-ultras-otro-signo', 'Diario Siglo XXI, Almeida y la Navidad en Sol (13-10-2026)'),
                 ('https://cadenaser.com/nacional/2026/10/13/sastre-despues-de-las-acusaciones-de-almeida-a-los-acampados-de-sol-prometio-semper-que-el-pp-iba-a-desterrar-el-insulto-cadena-ser/', 'Cadena SER, comentario de José Luis Sastre (13-10-2026)'),
                 ('https://www.moncloa.com/2026/10/13/acampada-sol-desalojo-comercios-madrid-3447744/', 'Moncloa.com, Ayuntamiento y Comunidad piden el desalojo (13-10-2026)'),
                 ('https://www.eldiariodemadrid.es/articulo/vivienda/pisos-turisticos-madrid-distritos-centro-viviendas-uso-turistico-2026/20260301135559122894.html', 'El Diario de Madrid, pisos turísticos por distrito con datos del INE (1-3-2026)'),
                 ('https://www.elsaltodiario.com/gentrificacion/nomadas-ciudad-madrid', 'El Salto, Eva García Pérez sobre gentrificación (24-11-2022)'),
                 ('https://www.lamarea.com/2026/03/12/javier-gil-generacion-inquilina/', 'La Marea, entrevista a Javier Gil, Generación inquilina (12-3-2026)'),
                 ('https://www.moncloa.com/2026/10/05/acampada-sol-vivienda-huelga-general-3442949/', 'Moncloa.com, Alicia del Río (Sindicato de Inquilinas) (5-10-2026)'),
                 ('https://www.elespanol.com/madrid/20261003/valeria-racu-portavoz-sindicato-inquilinas-apunta-huelga-general-termino-tiempo-politicos/1003744407409_0.html', 'El Español, Valeria Racu (Sindicato de Inquilinas de Madrid) (3-10-2026)'),
                 ('https://www.eldiario.es/economia/mayoria-espanoles-apoya-huelga-general-64-dice-crisis-vivienda-le-anima-votar_1_13582090.html', 'elDiario.es y Ateneo del Dato, encuesta sobre vivienda y voto (13-10-2026)')],
        enlaces=[],
        lugar='Madrid',
    ),
    dict(
        slug='pobreza-participacion-barrios', fecha='2026-10-15',
        titulo='EAPN presenta su informe sobre pobreza y territorio: en los barrios más pobres se vota 15 puntos menos que en los más ricos, el doble de distancia que en 2004', serie='29n',
        descripcion='En el 10% de secciones censales con menos renta votó el 62,1% en las generales de 2023; en el 10% más rico, el 77,4%. En las grandes ciudades la brecha llega a 22,5 puntos. El PSOE gana en los barrios pobres y el PP, en los ricos.',
        compara='La participación y el voto en las generales de 2004 a 2023 en las 34.590 secciones censales de España, agrupadas en diez tramos de igual tamaño según la renta media por unidad de consumo de 2023; la misma comparación dentro de cada provincia y dentro de las 64 ciudades de más de 75.000 electores.',
        limites='Son datos de secciones, no de personas: dicen cómo votan los barrios con menos o más renta, no cómo votan los pobres o los ricos. La renta es la de 2023 y se aplica también a elecciones anteriores, con las secciones actuales. Sin voto exterior. La presentación del informe de EAPN del 15 de octubre consta en la agenda de EFE; las cifras de pobreza son las de la Encuesta de Condiciones de Vida 2025 y los informes publicados de EAPN. Las citas de Abascal y Díaz llegan a través de otros medios.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/dyngs/Prensa/es/ECV2025.htm', 'INE, Encuesta de Condiciones de Vida 2025 (5-2-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/temas-del-dia-de-efe-espana-del-jueves-15-de-octubre-de-2026/', 'EFE vía Infobae, agenda del jueves 15 de octubre de 2026'),
                 ('https://www.plataformaong.org/ARCHIVO/documentos/noticias/4924/1780480085_informe-xvi-el-estado-de-la-pobreza-2026.pdf', 'EAPN España, XVI informe El Estado de la Pobreza 2026 (junio de 2026)'),
                 ('https://www.eapn.es/ARCHIVO/documentos/noticias/1760593879_xv_informe_pobreza-y-territorio-ccaa-ue_eapn2025.pdf', 'EAPN España, XV informe Pobreza y territorio (octubre de 2025)'),
                 ('https://www.eapn.es/actualidad/1979/eapn-es-lamenta-la-incapacidad-de-los-grupos-parlamentarios-para-adoptar-medidas-de-proteccion-del-derecho-a-la-vivienda', 'EAPN España, nota tras el rechazo de los decretos de vivienda (2-10-2026)'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)'),
                 ('https://www.oxfamintermon.org/hubfs/Oxfam-Website/oi-informes/dominio6_participacion_politica.pdf', 'María Ramos y Pablo Simón, Participación, influencia y voz, Oxfam Intermón (2019)'),
                 ('https://www.eldebate.com/espana/andalucia/20260519/vox-supera-toda-izquierda-psoe-zonas-rentas-bajas_418557.html', 'El Debate, Vox en las zonas de rentas bajas en las andaluzas (19-5-2026)'),
                 ('https://www.diariodeleon.es/nacional/261002/2099067/abascal-cree-gobierno-vivienda-tapar-ceuta.html', 'Europa Press vía Diario de León, Abascal sobre la vivienda (2-10-2026)'),
                 ('https://www.elsaltodiario.com/desahucios/reacciones-muerte-maricarmen-abascal', 'El Salto, reacciones a la muerte de Maricarmen (8-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pobreza-participacion-barrios.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una nómina, una cesta de la compra, monedas y un reloj de fichar.'),
    ),
    dict(
        slug='ministros-listas-29n', fecha='2026-10-15',
        titulo='Once ministros en las listas del PSOE: con los votos de 2023, el puesto más ajustado es el de Ana Redondo en Valladolid, que caería si el PSOE perdiera el 17% de sus votos', serie='29n',
        descripcion='Robles irá de número dos por Madrid y Albares encabezará Cádiz. Hemos calculado cuánto voto podría perder el PSOE en cada provincia sin que el ministro se quedara fuera: en diez de los once casos, más del 60%.',
        compara='Para cada ministro en las listas del PSOE, los votos que el partido podría perder en su provincia, con los resultados de las generales de 2023 (voto exterior incluido) y los escaños del 29N, antes de que el puesto del ministro dejara de dar escaño.',
        limites='Es aritmética con los votos de 2023, no una previsión: supone que el resto de partidos saca los mismos votos y que solo cambia el voto del PSOE. Los puestos son las propuestas conocidas el 14 de octubre, pendientes de ratificación por el Comité Federal el 17 de octubre. Los puestos que ocuparon en 2023 Ana Redondo y Arcadi España no se han podido verificar. Ningún estudio citado mide el efecto de un ministro como cabeza de lista.',
        fuentes=[INTERIOR,
                 ('https://www.infobae.com/espana/agencias/2026/10/14/sanchez-situa-a-robles-numero-2-del-psoe-por-madrid-y-a-sus-ministros-en-puestos-de-salida/', 'EFE vía Infobae, Sánchez sitúa a Robles número 2 por Madrid (14-10-2026)'),
                 ('https://www.elconstitucional.es/es/nacional/sanchez-refuerza-listas-psoe-elecciones-29n-con-once-ministros-situa-margarita-robles-como-numero-dos-por-madrid_8924_102.html', 'El Constitucional, once ministros en las listas del PSOE (14-10-2026)'),
                 ('https://www.eldiario.es/castilla-y-leon/politica/psoe-castilla-leon-mantiene-puente-redondo-frente-valladolid-propone-burgos-tudanca-senado_1_13586478.html', 'elDiario.es, Puente y Redondo en Valladolid (14-10-2026)'),
                 ('https://www.clm24.es/articulo/actualidad/rodriguez-tolon-encabezan-candidaturas-psoe-clm-29n/20261014210043484162.html', 'CLM24, Rodríguez y Tolón encabezan las listas (14-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/ministros-psoe-listas-elecciones-29n/', 'Demócrata, ministros en las listas del 29N (14-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-13/albares-marlaska-psoe-cadiz-elecciones/', 'The Objective, Albares sustituye a Marlaska en Cádiz (13-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/el-psoe-de-cadiz-ratifica-al-ministro-albares-como-cabeza-de-lista-para-el-congreso-y-a-ruiz-boix-para-el-senado/', 'Europa Press vía Infobae, el PSOE de Cádiz ratifica a Albares (14-10-2026)'),
                 ('https://dialnet.unirioja.es/descarga/articulo/7038484.pdf', 'Carlos Fernández Esquer, Las listas desbloqueadas en España, Apuntes Electorales 61 (2019)'),
                 ('https://nadaesgratis.es/bagues/la-papeleta-del-senado-otra-vuelta-de-tuerca-a-la-partitocracia', 'Manuel Bagues, La papeleta del Senado, Nada es Gratis (11-11-2009)'),
                 ('https://www.uc3m.es/ss/Satellite/UC3MInstitucional/es/Detalle/Comunicacion_C/1371356932884/1371216001705/Un_estudio_analiza_caracteristicas_de_los_sistemas_electorales_que_afectan_', 'UC3M, estudio de Pedro Riera y Francisco Cantú sobre sistemas electorales y voto ideológico (2022)'),
                 ('https://www.newtral.es/candidatos-cuneros-elecciones-generales-23-j/20230629/', 'Newtral, candidatos cuneros en el 23J (29-6-2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ministros-listas-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='El hemiciclo del Congreso, una mesa con carpetas y un ayuntamiento.'),
    ),
    dict(
        slug='ciudadanos-democracia21-29n', fecha='2026-10-15',
        titulo='Ciudadanos se suma a Democracia 21 en Madrid y Barcelona: en los barrios madrileños donde Cs fue más fuerte en 2019, el PP pasó del 18,2% al 49,2% en 2023', serie='29n',
        descripcion='Miriam González encabezará una lista con Ciudadanos y UCIN solo en Madrid y Barcelona. En el 10% de secciones de Madrid con más voto a Cs en abril de 2019 (29,5%), el PP ganó 31,1 puntos en 2023. En Barcelona, el mapa naranja era otro: subieron a la vez el PSC y el PP.',
        compara='El voto al PP, al PSOE y a Vox en abril de 2019 y en 2023 en las secciones censales de las provincias de Madrid y Barcelona, agrupadas en diez tramos de igual tamaño según el porcentaje de voto a Ciudadanos en abril de 2019.',
        limites='Son datos de secciones, no de personas: no dicen adónde fueron los votantes de Ciudadanos, solo cómo cambió el voto donde Cs era fuerte. Sin voto exterior. El nombre y la fórmula de la candidatura conjunta no están confirmados oficialmente. Las cifras de transferencia de voto vienen de encuestas con métodos distintos (CIS y NC Report).',
        fuentes=[INTERIOR, INE,
                 ('https://www.infobae.com/espana/agencias/2026/10/14/miriam-gonzalez-anuncia-que-democracia21-y-ciudadanos-concurren-juntos-a-las-elecciones/', 'EFE vía Infobae, Democracia21 y Ciudadanos concurren juntos (14-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-14/miriam-ciudadanos-democracia-21/', 'The Objective, el vídeo de Miriam González (14-10-2026)'),
                 ('https://www.publico.es/politica/partidos/ciudadanos-ucin-suman-nuevo-partido-democracia-21-miriam-gonzalez.html', 'Europa Press vía Público, Ciudadanos y UCIN se suman a Democracia 21 (14-10-2026)'),
                 ('https://www.eldiario.es/politica/miriam-gonzalez-anuncia-ciudadanos-suma-lista-democracia-21_1_13584121.html', 'elDiario.es, listas solo en Madrid y Barcelona (14-10-2026)'),
                 ('https://www.eldiario.es/politica/abogada-miriam-gonzalez-anuncia-candidatura-congreso-democracia-21-presentara-listas-madrid-barcelona_1_13577548.html', 'elDiario.es, presentación de Democracia 21 (10-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/07/13/miriam-gonzalez/', 'El Independiente, entrevista a Miriam González (13-7-2026)'),
                 ('https://es.wikipedia.org/wiki/Ciudadanos_(Espa%C3%B1a)', 'Wikipedia, resultados electorales de Ciudadanos'),
                 ('https://www.eldiario.es/piedrasdepapel/caida-ciudadanos_132_1066441.html', 'Ignacio Jurado, la caída de Ciudadanos, Piedras de Papel (22-1-2020)'),
                 ('https://ncreport.es/wp-content/uploads/2023/09/Encuesta-nacional.pdf', 'NC Report, encuesta postelectoral de 2023')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ciudadanos-democracia21-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mano deposita un sobre en una urna transparente, frente a un colegio electoral vacío.'),
    ),
    dict(
        slug='alianca-catalana-ceo-mapa', fecha='2026-10-15',
        titulo='El CEO da a Aliança Catalana hasta 25 escaños: en el Parlament de 2024 sacó el 3,8%, pero el 24,9% en el Ripollès y el 7,8% en los pueblos de menos de 1.000 electores', serie='29n',
        descripcion='Aliança no se presenta el 29N, pero el barómetro del CEO la sitúa como tercera fuerza en Cataluña. Su único resultado oficial dibuja un mapa con centro en el Ripollès, fuerte en el norte de Girona y el interior, y débil en el área de Barcelona.',
        compara='El voto a Aliança Catalana en las elecciones al Parlament de 2024 en los 947 municipios de Cataluña, por comarca, provincia y tamaño del municipio, junto al de Junts y Vox.',
        limites='El barómetro del CEO es una encuesta con un margen de error de ±2,19 puntos. El mapa es el de 2024, cuando Aliança sacó el 3,8%: no dice dónde crecería. Sin voto exterior. Varias citas académicas llegan a través de otros medios y se reproducen en catalán, como se publicaron.',
        fuentes=[('https://analisi.transparenciacatalunya.cat/resource/ntc4-rnwr', 'Generalitat de Catalunya, resultados de las elecciones al Parlament de 2024 por municipio (datos abiertos)'),
                 ('https://govern.cat/salapremsa/notes-premsa/880300/el-ceo-publica-els-resultats-de-la-2a-onada-del-bar-metre-de-2026', 'Govern, el CEO publica la segunda ola del barómetro de 2026 (14-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/el-psc-vence-pero-retrocede-en-el-parlament-y-alianca-estabiliza-su-ascenso-segun-el-ceo/', 'EFE vía Infobae, el PSC vence pero retrocede, según el CEO (14-10-2026)'),
                 ('https://www.diaridetarragona.com/catalunya/273081/psc-18-19-ganaria-elecciones-generales-catalunya-seguido-erc-10-11-ppc-vox.html', 'EFE vía Diari de Tarragona, presentación del CEO (14-10-2026)'),
                 ('https://es.ara.cat/politica/alianca-catalana-no-presenta-elecciones-espanolas_1_5870081.html', 'Ara, por qué Aliança no se presenta a las generales (5-10-2026)'),
                 ('https://www.ara.cat/politica/l-eix-transversal-l-extrema-dreta-l-herencia-carlista-xenofobia_130_5741966.html', 'Jordi Muñoz, L’eix transversal de l’extrema dreta, Ara (23-5-2026)'),
                 ('https://www.ara.cat/politica/enquestes/alianca-catalana-sedueix-comarques-mes-desateses-lleida-girona_1_5575399.html', 'Ara, Aliança sedueix les comarques més desateses (29-11-2025)'),
                 ('https://www.ara.cat/politica/eleccions-catalunya/barris-pobres-rics-vox-classe-mitjana-alianca-catalana_1_5032813.html', 'Ara, análisis por sección censal del 12-M (19-5-2024)'),
                 ('https://naciodigital.cat/politica/on-anira-vot-alianca-catalana-29-n.html', 'Nació Digital, on anirà el vot d’Aliança el 29-N (10-10-2026)'),
                 ('https://naciodigital.cat/politica/la-immigracio-i-no-la-independencia-explica-la-fuga-de-vots-de-junts-cap-a-alianca-catalana.html', 'Nació Digital, estudio de Martínez-Cantó y Tudó en el ICPS (10-6-2026)')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/alianca-catalana-ceo-mapa.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una persiana bajada en una calle de pueblo y un vecino sentado frente a las montañas.'),
    ),
    dict(
        slug='como-voto-tu-calle', fecha='2026-10-15',
        titulo='Cómo votó tu calle: una de cada cuatro secciones censales eligió en 2023 un ganador distinto al de su municipio', serie='29n',
        descripcion='Guía para buscar tu dirección en el mapa electoral calle a calle: qué es una sección censal, qué dice la ficha de cada una (voto, participación, renta, edad) y qué no dice.',
        compara='El partido más votado en las generales de 2023 en cada una de las 30.587 secciones censales de municipios con más de una sección, frente al partido más votado en su municipio.',
        limites='Son datos de secciones, no de personas. Una calle puede estar repartida entre varias secciones. Las secciones cambian de límites: las elecciones anteriores a 2023 solo se muestran en las secciones que conservan el código. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/prensa/adrh_2020.pdf', 'INE, Atlas de Distribución de Renta de los Hogares 2020, definición de sección censal (7-10-2022)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Ley Orgánica del Régimen Electoral General, artículo 23'),
                 ('https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout', 'INE, Cartografía de secciones censales y callejero del Censo Electoral'),
                 ('https://www.cartociudad.es/', 'CartoCiudad (IGN), geocodificador de direcciones'),
                 ('https://elpais.com/espana/elecciones-generales/2023-07-24/el-mapa-con-los-resultados-de-las-elecciones-generales-del-23-j-calle-a-calle.html', 'El País, el mapa del 23J calle a calle (24-7-2023)'),
                 ('https://maldita.es/malditateexplica/20230727/elecciones-mapas-resultados-elecciones-representacion/', 'Maldita.es, el mapa perfecto de resultados no existe (27-7-2023)'),
                 ('https://maldita.es/malditateexplica/20240610/mapas-calle-a-calle-anomalias-resultados-elecciones/', 'Maldita.es, anomalías en los mapas calle a calle (10-6-2024)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/como-voto-tu-calle.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una maleta, un portero automático y un plano en la mano, entre calles estrechas.'),
    ),
    dict(
        slug='calle-que-parte-el-voto', fecha='2026-10-15',
        titulo='La calle que parte el voto: el PP sacó el 55,9% a un lado de la avenida de Francia, en València, y el 16,4% al otro', serie='29n',
        descripcion='En nueve grandes ciudades, una de cada cinco parejas de secciones censales vecinas eligió un ganador distinto en 2023. Seis calles donde se ve, de El Palo a la Diagonal, y un patrón de renta.',
        compara='Las 16.154 parejas de secciones censales contiguas (al menos 80 metros de límite común y 400 electores cada una) de Madrid, Barcelona, València, Sevilla, Zaragoza, Málaga, Murcia, Palma y Bilbao en las generales de 2023, y su renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada lado vota distinto. Los seis casos se han elegido entre los saltos más grandes de cada ciudad en los que el límite es una calle con viviendas a los dos lados; no son una muestra al azar. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.openstreetmap.org/', 'OpenStreetMap, callejero para comprobar los límites'),
                 ('https://www.cartociudad.es/', 'CartoCiudad (IGN), geocodificador inverso'),
                 ('https://valenciaplaza.com/precio-alquiler-valencia-calle-calle-avenida-francia-barrio-natzaret', 'Valencia Plaza, el alquiler en València calle a calle (25-12-2021)'),
                 ('https://www.elespanol.com/malaga/malaga-ciudad/20220430/verguenza-separacion-pobres-palo-tiraron-propios-vecinos/668683598_0.html', 'El Español de Málaga, el muro de El Palo (30-4-2022)'),
                 ('https://www.elpalo.org/el-barrio/', 'Asociación de Vecinos de El Palo, El barrio (31-10-2021)'),
                 ('https://www.eldiario.es/madrid/somos/estudio-descubre-influye-voto-madrid-efecto-alquiler-barrio-vivas_1_12961596.html', 'elDiario.es, Álvaro Sánchez García sobre alquiler y voto en Madrid (9-2-2026)'),
                 ('https://www.eldiario.es/politica/barrios-pobres-van-votar-elecciones_1_1162754.html', 'elDiario.es, por qué los barrios pobres no van a votar (7-4-2019)'),
                 ('https://www.publico.es/economia/brecha-ricos-pobres-agranda-ciudades-espana.html', 'Público, la brecha entre ricos y pobres en las ciudades (3-2-2019)'),
                 ('https://www.ultimahora.es/noticias/palma/2019/09/08/1105145/inversiones-lujo-llegan-terreno-para-frenar-degradacion.html', 'Ultima Hora, las inversiones de lujo llegan a El Terreno (8-9-2019)'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2-4-2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/calle-que-parte-el-voto.jpg', ancho=1280, alto=720, ia=True,
                  pie='Bloques antiguos, torres nuevas, un tren y un pueblo: un collage de contrastes.'),
    ),
    dict(
        slug='madrid-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Madrid llega al 29N teñida de azul: el PP ganó en 1.603 de sus 2.450 secciones y el PSOE solo resiste en cuatro distritos del sur', serie='29n',
        descripcion='En 2023, 521 secciones censales de la capital pasaron del PSOE al PP. Doscientas se decidieron por menos de dos puntos, la mitad en Latina, Carabanchel, Ciudad Lineal y Centro.',
        compara='Las 2.450 secciones censales de Madrid en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://datos.comunidad.madrid/catalogo/dataset/secciones_censales', 'Comunidad de Madrid, secciones censales y distritos'),
                 ('https://www.esdiario.com/nacional/261010/199937/almeida-firme-izquierda-echaran-calles-ganaran-elecciones.html', 'ESdiario, Almeida en el acto del PP (10-10-2026)'),
                 ('https://www.ultimahora.es/noticias/comunidades/2026/10/07/2724735/oscar-lopez-confirma-ira-lista-del-psoe-del-congreso-quiero-centrarme-conseguir-cambio-madrid.html', 'Europa Press en Última Hora, Óscar López (7-10-2026)'),
                 ('https://www.eldiario.es/1_cf3194', 'elDiario.es, Emilio Delgado (11-10-2026)'),
                 ('https://www.eldebate.com/espana/20261014/nucleo-duro-sanchez-ocupa-primeros-puestos-listas-psoe_469756.html', 'El Debate, listas del PSOE (14-10-2026)'),
                 ('https://www.eldiario.es/politica/barrios-pobres-van-votar-elecciones_1_1162754.html', 'elDiario.es, por qué los barrios pobres no van a votar (7-4-2019)')],
        enlaces=[],
        lugar='Madrid',
        foto=dict(src='img/actualidad/fotos/madrid-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un andén, un autobús y un billete: el viaje diario de la ciudad, en collage.'),
    ),
    dict(
        slug='barcelona-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Barcelona pasó del amarillo al rojo: ERC ganó en 563 secciones en 2019 y en ninguna en 2023', serie='29n',
        descripcion='El PSC fue el más votado en nueve de cada diez secciones censales de la ciudad en las últimas generales. Solo Sarrià-Sant Gervasi se le resistió, y allí el que ganó fue el PP.',
        compara='Las 1.068 secciones censales de Barcelona en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/catalunya/anatomia-reves-independentista-700-000-votos-perdidos-abstencion-psc-sumar_1_10414031.html', 'elDiario.es, anatomía del revés independentista (29-7-2023)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2-4-2023)'),
                 ('https://www.3cat.cat/3catinfo/hereu-sera-el-candidat-del-psc-a-les-eleccions-del-29n-us-demano-que-sortim-a-guanyar-amb-contundencia/noticia/3433548/', '3CatInfo, Hereu candidato del PSC (11-10-2026)'),
                 ('https://www.totbarcelona.cat/politica/eleccions-espanyoles-29-n-precampanya-barcelona-744522/', 'Tot Barcelona, precampaña en Barcelona (5-10-2026)'),
                 ('https://www.3cat.cat/3catinfo/gabriel-rufian-sera-el-cap-de-llista-desquerra-a-les-eleccions-generals-del-29n/noticia/3433559/', '3CatInfo, Rufián cabeza de lista de ERC (11-10-2026)'),
                 ('https://naciodigital.cat/politica/junts-repetira-equip-a-madrid-sota-el-lideratge-de-miriam-nogueras.html', 'NacióDigital, Nogueras repite (8-10-2026)')],
        enlaces=[],
        lugar='Barcelona',
        foto=dict(src='img/actualidad/fotos/barcelona-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Azoteas, árboles y una fuente: una ciudad mediterránea en collage.'),
    ),
    dict(
        slug='valencia-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='València borró a Compromís del mapa: ganaba en 101 secciones en 2019 y en 15 en 2023', serie='29n',
        descripcion='El PP pasó a ser el más votado en 335 de las 591 secciones censales de la ciudad. El PSOE resiste en un arco de barrios del norte, el oeste y el mar, y 64 secciones se decidieron por menos de dos puntos.',
        compara='Las 591 secciones censales de València en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://www.valencia.es/estadistica/CatPub/files/Elecciones/Muni2023.pdf', "Ajuntament de València, Oficina d'Estadística, municipales 2023"),
                 ('https://diariodealicante.net/pilar-bernabe-lista-pspv-congreso-valencia/', 'Diario de Alicante, lista del PSPV (14-10-2026)'),
                 ('https://www.eldebate.com/espana/comunidad-valenciana/20261005/pilar-bernabe-ante-29-esta-democracia-costo-demasiado-dejarla-manos-quienes-desprecian_466084.html', 'El Debate, Pilar Bernabé (5-10-2026)'),
                 ('https://www.eldebate.com/espana/comunidad-valenciana/20261005/maria-jose-catala-sobre-elecciones-generales-hay-demostrar-espana-esta-encima-cualquier-etapa-politica_466024.html', 'El Debate, María José Catalá (5-10-2026)'),
                 ('https://www.eldiario.es/comunitat-valenciana/baldovi-entrada-frente-amplio-apostamos-marca-valiente-valenciana-compromis-aparecer_1_13562115.html', 'elDiario.es, Baldoví y el Frente Amplio (5-10-2026)'),
                 ('https://www.eldiario.es/comunitat-valenciana/politica/batalla-interna-compromis-numero-1-valencia-pone-riesgo-gran-acuerdo-izquierda-valenciana_1_13586534.html', 'elDiario.es, el número uno de Compromís (14-10-2026)'),
                 ('https://recyt.fecyt.es/index.php/CyTET/article/view/116702', 'Mazorra-Rodríguez y Villalón-Ogáyar, El Cabanyal, CyTET (2026)')],
        enlaces=[],
        lugar='València',
        foto=dict(src='img/actualidad/fotos/valencia-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un mercado, monedas y un tique: la economía de cada día, en collage.'),
    ),
    dict(
        slug='sevilla-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Sevilla tiene dos mapas: el PP ganó en votos el 23J, pero el PSOE fue el primero en 286 de sus 521 secciones', serie='29n',
        descripcion='El PSOE ganó en todas las secciones de Cerro-Amate y Norte. Allí se vota mucho menos que en Los Remedios o Nervión, y la diferencia de participación entre barrios ricos y pobres es, con la de Málaga, la mayor de las grandes ciudades.',
        compara='Las 521 secciones censales de Sevilla en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://www.sevilla.org/servicios/servicio-de-estadistica/datos-estadisticos/anuarios/anuario-estadistico-de-la-ciudad-de-sevilla-2022/publicacion/anuario-estadistico-completo.pdf', 'Ayuntamiento de Sevilla, Anuario Estadístico 2022'),
                 ('https://www.ine.es/dyngs/Prensa/UA2025.htm', 'INE, Indicadores Urbanos 2025'),
                 ('https://www.elcorreogallego.es/espana/2026/05/22/pajaritos-torreblanca-tres-mil-izquierda-barrios-mas-pobres-espana-130523399.html', 'El Correo de Andalucía, en El Correo Gallego (22-5-2026)'),
                 ('https://www.vivasevilla.es/articulo/sevilla/partidos-miran-29n-ojo-puesto-municipales-sevilla/20261005193726012446.html', 'Viva Sevilla, los partidos ante el 29N (5-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/gomez-de-celis-encabezara-la-lista-del-psoe-al-congreso-por-sevilla-para-el-29n/', 'EFE, Gómez de Celis encabeza la lista del PSOE (14-10-2026)')],
        enlaces=[],
        lugar='Sevilla',
        foto=dict(src='img/actualidad/fotos/sevilla-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una persiana a medio subir, unas llaves y una tienda de barrio: un collage.'),
    ),
    dict(
        slug='zaragoza-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Zaragoza, empate barrio a barrio: el PSOE ganó en 250 secciones y el PP en 245, y 53 se decidieron por menos de dos puntos', serie='29n',
        descripcion='El PP sacó seis puntos más en votos, pero el mapa de Zaragoza es el más igualado de las grandes ciudades. En Delicias, el PSOE ganó por dos décimas.',
        compara='Las 497 secciones censales de Zaragoza en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://ebropolis.es/wp-content/uploads/2023/05/Renta-zgz-2022-web.pdf', 'Ebrópolis, renta de Zaragoza por distrito censal (2023)'),
                 ('https://www.zaragoza.es/contenidos/urbanismo/pgouz/TR2024/TRPGOU_2002_MEM_INF_Anejo_2.pdf', 'Ayuntamiento de Zaragoza, PGOU, distritos censales'),
                 ('https://www.eldiario.es/aragon/politica/david-pac-sociologo-votantes-proximos-lamban-optaron-8f-no-apoyar-pp-acto-vito-quiles_1_12990394.html', 'elDiario.es, entrevista a David Pac (14-2-2026)'),
                 ('https://www.aragondigital.es/articulo/politica/natalia-chueca-celebra-convocatoria-elecciones-han-sido-anos-muy-tristes-democracia/202610051224451012703.html', 'Aragón Digital, Natalia Chueca (5-10-2026)'),
                 ('https://www.aragondigital.es/articulo/politica/sanchez-zaragoza-nietos-exilio-tienen-mismo-derecho-votar-que-franquismo/202610141947111015534.html', 'Aragón Digital, Sánchez en Zaragoza (14-10-2026)'),
                 ('https://www.aragondigital.es/articulo/politica/alegria-pide-votar-perro-alusion-carinosa-sanchez-es-mejor-amigo-hombre/202610142003081015543.html', 'Aragón Digital, Pilar Alegría (14-10-2026)'),
                 ('https://www.aragondigital.es/articulo/politica/chunta-quiere-liderar-candidatura-unica-aragon-iu-sumar-podemos-teruel-existe/202610051233101012708.html', 'Servimedia en Aragón Digital, CHA (5-10-2026)'),
                 ('https://www.eldiario.es/aragon/politica/mitin-sanchez-zaragoza-retrasa-jueves-eleccion-candidatos-socialistas-congreso-senado_1_13581432.html', 'elDiario.es, calendario de las listas del PSOE (13-10-2026)')],
        enlaces=[],
        lugar='Zaragoza',
        foto=dict(src='img/actualidad/fotos/zaragoza-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Guantes, herramientas y un reloj de fichar: el turno de trabajo, en collage.'),
    ),
    dict(
        slug='malaga-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='En Málaga, la renta decide quién vota: el 46,7% en los barrios más pobres y el 80,6% en los más ricos', serie='29n',
        descripcion='Es la mayor brecha de participación de las ocho grandes ciudades analizadas. En 2023, 116 secciones censales de Málaga pasaron del PSOE al PP, y el PP ganó en 223 de las 435.',
        compara='Las 435 secciones censales de Málaga en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados. Los distritos censales del INE no coinciden con los municipales; su descripción es un cálculo propio o sale de documentos que no están pensados para eso.',
        fuentes=[INTERIOR, INE,
                 ('https://datosabiertos.malaga.eu/dataset/sistema-de-informacion-cartografica-distrito-censal', 'Ayuntamiento de Málaga, cartografía de distritos censales'),
                 ('https://www.elespanol.com/malaga/20260518/vox-dispara-barrios-pobres-malaga-gana-zonas-vulnerables-sube-puntos/1003744249420_0.html', 'El Español de Málaga, barrios vulnerables (18-5-2026)'),
                 ('https://www.eldebate.com/espana/andalucia/malaga/20260511/cinco-distritos-malaga-superan-70-abstencion-aqui-no-llega-ningun-politico_416174.html', 'El Debate, la abstención en Málaga (11-5-2026)'),
                 ('https://www.ine.es/dyngs/Prensa/UA2025.htm', 'INE, Indicadores Urbanos 2025'),
                 ('https://www.andaluciainformacion.es/articulo/malaga-sociedad/bendodo-repetira-como-numero-uno-pp-malaga-congreso-generales-29n/202610061631193499205.html', 'Andalucía Información, Bendodo repite (6-10-2026)'),
                 ('https://www.elespanol.com/malaga/20261014/jose-bernal-numero-psoe-malaga-congreso-elecciones-noviembre/1003744420700_0.html', 'El Español de Málaga, lista del PSOE (14-10-2026)'),
                 ('https://revistalugardeencuentro.com/2026/10/14/el-psoe-de-malaga-aprueba-sus-candidaturas-para-el-29n-con-un-llamamiento-a-la-movilizacion-de-los-progresistas/', 'Lugar de Encuentro, Josele Aguilar (14-10-2026)')],
        enlaces=[],
        lugar='Málaga',
        foto=dict(src='img/actualidad/fotos/malaga-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Redes, cajas de pescado y un puerto: un collage costero.'),
    ),
    dict(
        slug='murcia-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Murcia, de verde a azul: Vox ganó en 164 secciones en 2019 y en una en 2023', serie='29n',
        descripcion='El PP fue el más votado en 376 de las 387 secciones censales del municipio. Pero Vox sigue sacando en las pedanías de la huerta y el campo su mejor resultado, y el PSOE solo ganó en diez.',
        compara='Las 387 secciones censales de Murcia en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados. Los distritos censales del INE no coinciden con los municipales; su descripción es un cálculo propio o sale de documentos que no están pensados para eso.',
        fuentes=[INTERIOR, INE,
                 ('https://www.borm.es/services/anuncio/ano/2009/numero/7092/pdf', 'BORM, Mapa Sanitario de la Región de Murcia (2009)'),
                 ('https://murciaplaza.com/murciaplaza/region/la-region-de-murcia-ante-el-29-n-asi-afrontan-las-elecciones-y-todo-lo-que-esta-en-juego', 'Murcia Plaza, la Región ante el 29N (6-10-2026)'),
                 ('https://revistas.ucm.es/index.php/POSO/article/view/75974', 'Crespo y Mora, Vox en la Región de Murcia, Política y Sociedad (2022)'),
                 ('https://www.eldiario.es/murcia/politica/racismo-campo-redes-sociales-metamorfosis-torre-pacheco-caceria-ultras-mitin-vox_1_12465316.html', 'elDiario.es, Torre Pacheco (15-7-2025)'),
                 ('https://www.murciadiario.com/entrevistas-md/entrevista-rebeca-perez/20260628104818146596.html', 'Murcia Diario, entrevista a Rebeca Pérez (28-6-2026)'),
                 ('https://www.elespanol.com/espana/murcia/20261003/miras-postula-reeleccion-pp-murcia-moviliza-militancia-elecciones-gobierno-moribundo/1003744407522_0.html', 'El Español, López Miras (3-10-2026)'),
                 ('https://murciaplaza.com/murciaplaza/region/vox-pide-a-los-murcianos-que-el-29-n-voten-presencialmente', 'Murcia Plaza, Vox pide el voto presencial (5-10-2026)'),
                 ('https://murciaplaza.com/murciaplaza/region/la-lista-del-psoe-al-29-n-maria-gonzalez-veracruz-es-la-candidata-con-miguel-angel-ortega-y-caridad-rives-como-escuderos', 'Murcia Plaza, lista del PSOE (14-10-2026)'),
                 ('https://www.murcia.com/region/noticias/2026/10/13-candidatura-elecciones-generales-2026-region-de-murcia.asp', 'IU-Verdes Región de Murcia, nota en murcia.com (13-10-2026)')],
        enlaces=[],
        lugar='Murcia',
        foto=dict(src='img/actualidad/fotos/murcia-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Tierra seca, un embalse y un grifo: el agua en el paisaje, en collage.'),
    ),
    dict(
        slug='palma-barrio-a-barrio-29n', fecha='2026-10-15',
        titulo='Palma, la gran ciudad que menos vota: el 62,5% en 2023, y menos del 35% en algunas secciones del este', serie='29n',
        descripcion='El PP pasó de ganar en 50 secciones censales a ganar en 134, y el PSOE resiste en el este, donde menos se vota. En el norte, el PP ganó por una décima.',
        compara='Las 253 secciones censales de Palma en las generales de noviembre de 2019 y julio de 2023, agrupadas por distrito censal del INE y por tramos de renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. Sin voto exterior, así que la participación sale más alta que la oficial. La comparación con noviembre de 2019 solo incluye las secciones que conservan el código. La renta de las secciones más ricas está topada en 58.752 euros. Los límites de sección están simplificados. Los distritos censales del INE no coinciden con los municipales; su descripción es un cálculo propio o sale de documentos que no están pensados para eso.',
        fuentes=[INTERIOR, INE,
                 ('https://intranet.caib.es/eboibfront/pdf/es/2015/118/927659', 'BOIB, distritos municipales de Palma (2015)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/14/2728645/psib-cierra-nombres-lista-congreso-espero-acuerdo-mes-senado.html', 'Última Hora, lista del PSIB (14-10-2026)'),
                 ('https://es.arabalears.cat/politica/partidos-baleares-toman-posiciones-elecciones-generales_1_5875548.html', 'Ara Balears, los partidos ante el 29N (10-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/14/2728283/choque-podemos-mes-por-lista-congreso-complica-candidatura-unica.html', 'Última Hora, Podemos y Més (14-10-2026)'),
                 ('https://www.eldebate.com/espana/baleares/20261014/soberanistas-baleares-plantan-cara-podemos-exigen-encabezar-lista-izquierda-congreso_469724.html', 'El Debate, Ara Més (14-10-2026)'),
                 ('https://theconversation.com/mallorca-se-revuelve-contra-el-turismo-que-despoja-al-habitante-de-su-territorio-288566', 'The Conversation, Julio Batle (29-7-2026)'),
                 ('https://www.eldiario.es/illes-balears/sociedad/son-gotleu-barrio-lucha-estigmatizacion_1_11507051.html', 'elDiario.es, Son Gotleu (9-7-2024)')],
        enlaces=[],
        lugar='Palma',
        foto=dict(src='img/actualidad/fotos/palma-barrio-a-barrio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una maleta, mapas y una calle con balcones: un collage.'),
    ),
    dict(
        slug='minguez-lleida-29n', fecha='2026-10-15',
        titulo='Montse Mínguez, entre los pisos de su pareja y un escaño en el aire: el PSC duplicó su voto en Lleida y le ganó el cuarto diputado al PP por unos 3.500 votos', serie='29n',
        descripcion='La portavoz del PSOE repite como número uno del PSC por Lleida en plena polémica por los negocios inmobiliarios de su pareja. En 2023, el PSC pasó del 14,6% al 29,8% en la provincia y ganó en 79 municipios, frente a 8 en 2019.',
        compara='El voto en la provincia de Lleida en las 16 generales desde 1977, los 231 municipios en noviembre de 2019 y julio de 2023, el reparto D\'Hondt de los cuatro escaños de 2023 y las 81 secciones censales de la ciudad de Lleida agrupadas en tres tramos de renta.',
        limites='No analiza los negocios de la pareja de Mínguez: las citas sobre la polémica son de la prensa que se enlaza. Son datos de territorios, no de personas, y no dicen por qué votó así cada municipio o barrio ni cómo afectará la polémica. Los porcentajes de la serie y de la ciudad son sin voto exterior y sobre votos a candidaturas; el reparto de escaños usa los resultados oficiales, con voto exterior. La comparación de la ciudad solo incluye las secciones que conservan el código entre 2019 y 2023.',
        fuentes=[INTERIOR, INE, INE_IPVA,
                 ('https://en.wikipedia.org/wiki/Lleida_(Congress_of_Deputies_constituency)', 'Wikipedia, circunscripción de Lleida: resultados oficiales de 2023'),
                 ('https://es.wikipedia.org/wiki/Montse_M%C3%ADnguez', 'Wikipedia, Montse Mínguez'),
                 ('https://www.eldebate.com/espana/20261013/portavoz-psoe-reconoce-pareja-gran-tenedor-alquila-casas-desahuciado-inquilinos_469056.html', 'El Debate, Mínguez reconoce que su pareja es gran tenedor (13-10-2026)'),
                 ('https://www.elespanol.com/espana/20261014/pareja-montse-minguez-portavoz-psoe-sociedades-panama-ademas-pisos-espana/1003744419108_0.html', 'El Español, la pareja de Mínguez tiene dos sociedades en Panamá (14-10-2026)'),
                 ('https://www.esdiario.com/nacional/261014/200198/30-pisos-sociedades-panama-pareja-montse-minguez-amplia-problema-ferraz.html', 'ESdiario, 30 pisos y sociedades en Panamá (14-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-14/oscar-lopez-pareja-montse-minguez-licita/', 'The Objective, Óscar López defiende a la pareja de Mínguez (14-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/pp-ve-incoherencia-e-hipocresia-en-el-psoe-tras-el-caso-de-la-pareja-de-montse-minguez/', 'EFE en Infobae, el PP ve incoherencia e hipocresía (14-10-2026)'),
                 ('https://naciodigital.cat/lleida/politica/el-psc-de-lleida-ratifica-montse-minguez-com-a-cap-de-llista-al-congres-per-al-29-n.html', 'NacióDigital, el PSC ratifica a Mínguez (14-10-2026)'),
                 ('https://naciodigital.cat/lleida/politica/lenigma-de-lleida-lultim-esco-no-te-amo.html', 'NacióDigital, l\'enigma de Lleida (8-10-2026)'),
                 ('https://lamanyana.cat/montse-minguez-cap-de-llista-del-psc-per-lleida-al-congres/', 'La Mañana, la lista del PSC por Lleida (15-10-2026)'),
                 ('https://lamanyana.cat/quatre-escons-en-joc-a-lleida/', 'La Mañana, cuatro escaños en juego en Lleida (7-10-2026)'),
                 ('https://laciutat.cat/laciutatdelleida/ines-granollers-proclamada-cap-llista-esquerra-republicana-catalunya-congres-demarcacio-lleida-eleccions-generals_902682_102.html', 'La Ciutat, Inés Granollers, candidata de ERC (12-10-2026)'),
                 ('https://ebredigital.cat/2026/10/08/josep-maria-cruset-tornara-a-ncapcalar-la-llista-de-junts-al-congres-el-29n/', 'EbreDigital, las listas de Junts (8-10-2026)'),
                 ('https://lamanyana.cat/vuit-pobles-lleidatans-entren-a-la-regulacio-del-lloguer-del-govern/', 'La Mañana, Lleida sale de las zonas tensionadas (29-7-2026)'),
                 ('https://www.eldiario.es/madrid/somos/estudio-descubre-influye-voto-madrid-efecto-alquiler-barrio-vivas_1_12961596.html', 'elDiario.es, Álvaro Sánchez García sobre alquiler y voto en Madrid (9-2-2026)')],
        enlaces=[],
        lugar='Lleida',
        foto=dict(src='img/actualidad/fotos/minguez-lleida-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Unas llaves que cambian de mano, un bloque de pisos y una urna: un collage.'),
    ),
    dict(
        slug='ceuta-melilla-participacion-29n', fecha='2026-10-15',
        titulo='El Rey visita las dos ciudades que menos votan: en Melilla votó el 49,8% en 2023, y en una sección de la periferia, el 19%', serie='29n',
        descripcion='Ceuta y Melilla reciben a Felipe VI a mes y medio del 29N. Son las dos circunscripciones con menos participación de España, y dentro de cada una la brecha entre barrios supera los 20 puntos: en el tercio de secciones con menos renta de Melilla votó el 32%; en el de más renta, el 60%.',
        compara='La participación de las 19 comunidades y ciudades autónomas en las generales de 2023, las 56 secciones censales de Ceuta y las 44 de Melilla agrupadas por distrito y en tres tramos de renta por unidad de consumo, y el partido más votado en cada una de las 16 generales desde 1977.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada barrio vota como vota. No hay datos de religión ni de origen por sección: la pieza no los usa. Sin voto exterior. Los nombres de barrio de cada distrito salen de la prensa local, no de una relación oficial. Los límites de sección están simplificados.',
        fuentes=[INTERIOR, INE,
                 ('https://es.euronews.com/2026/10/13/los-reyes-visitan-una-ceuta-que-los-recibe-con-los-brazos-abiertos', 'Euronews, los Reyes visitan Ceuta (13-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261014/discurso-integro-rey-felipe-vi-historica-visita-ciudad-autonoma-melilla/1003744420505_0.html', 'El Español, discurso íntegro del Rey en Melilla (14-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/14/imbroda-entrega-al-rey-la-llave-de-oro-de-melilla-y-reclama-al-gobierno-respuestas-mas-contundentes-nadie-puede-violar-la-soberania-nacional-y-no-esperar-consecuencias/', 'Infobae, Imbroda entrega al Rey la llave de oro de Melilla (14-10-2026)'),
                 ('https://www.moncloa.com/2026/10/14/marruecos-reyes-melilla-3447827', 'Moncloa.com, Marruecos ante la visita (14-10-2026)'),
                 ('https://www.elcorreogallego.es/mundo/2026/10/13/marruecos-silencio-prensa-visita-reyes-ceuta-melilla-135298696.html', 'El Correo Gallego, Rabat guarda silencio (13-10-2026)'),
                 ('https://teleceuta.com/ceuta-decidira-un-diputado-y-dos-senadores-en-las-elecciones-generales-de-noviembre-de-2026/', 'Teleceuta, Ceuta elige un diputado y dos senadores (6-10-2026)'),
                 ('https://www.ceutaldia.com/articulo/politica/votos-generales-mesa-mesa-dibujan-mapa-desigualdad-2-ceutas-claridad/20230725004623266945.html', 'Ceuta al Día, el voto mesa a mesa (25-7-2023)'),
                 ('https://elfarodeceuta.es/el-pp-gano-en-todos-los-distritos-salvo-principe-benzu-y-en-73-de-las-93-mesas/', 'El Faro de Ceuta, el voto por distritos (28-6-2016)'),
                 ('https://elfarodemelilla.es/radiografia-elecciones-generales-voto-melilla-distritos/', 'El Faro de Melilla, radiografía del voto por distritos (6-5-2019)'),
                 ('https://elfarodemelilla.es/melilla-donde-el-pp-pierde-mas-votos-respecto-a-las-generales/', 'El Faro de Melilla, las europeas por colegios (11-6-2024)'),
                 ('https://www.cepc.gob.es/sites/default/files/2021-12/27094carmengonzalezenriquezrep140.pdf', 'Carmen González Enríquez, Los frenos al pluralismo cultural en territorios de soberanía discutida: los casos de Ceuta y Melilla, Revista de Estudios Políticos 140 (2008)'),
                 ('https://seguridadinternacional.es/resi/html/representacion-politica-e-identidad-local-en-ceuta-1975-2023/', 'Alicia Fernández, Representación política e identidad local en Ceuta (1975-2023), Revista de Estudios en Seguridad Internacional 11-1 (2025)')],
        enlaces=[],
        lugar='Ceuta y Melilla',
        foto=dict(src='img/actualidad/fotos/ceuta-melilla-participacion-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un radar, un buque, un mapa y un hemiciclo: un collage.'),
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
# Serie «Las comunidades en las urnas»: un reportaje largo por comunidad (comunidades/, reportajes.py escribe los <slug>.html).
sys.path.insert(0, os.path.join(SRC, 'comunidades'))
from reportajes import piezas as piezas_comunidades  # noqa: E402
SERIES['comunidades'] = 'Las comunidades en las urnas'
COMUNIDADES = []
for h in piezas_comunidades():
    q = {k: h[k] for k in ('slug', 'titulo', 'descripcion', 'compara', 'limites', 'fuentes', 'lugar')}
    q.update(fecha=h.get('fecha', '2026-10-09'), serie='comunidades', enlaces=[])
    if os.path.exists(os.path.join(SRC, '..', '..', 'img', 'actualidad', 'fotos', h['slug'] + '.jpg')):
        q['foto'] = dict(src=f"img/actualidad/fotos/{h['slug']}.jpg", ancho=1280, alto=720, ia=True,
                         pie=f"Collage sobre las elecciones en {h['lugar']}: la bandera, el mapa y vecinos votando.")
    COMUNIDADES.append(q)

PIEZAS = COMUNIDADES + HISTORIA + PIEZAS

# Antetítulo de cada pieza (portada, cabecera y «Sigue leyendo»): el tema o el gancho de actualidad de esa pieza,
# no el nombre de la serie, que se repetiría en todas. Las que no tienen uno usan la comunidad o la serie.
ANTETITULOS = {
    'ceuta-melilla-participacion-29n': 'Dos ciudades en cada ciudad',
    'minguez-lleida-29n': 'Un escaño por 3.500 votos',
    'madrid-barrio-a-barrio-29n': 'El sur aguanta, el resto cambia',
    'barcelona-barrio-a-barrio-29n': 'Adiós al amarillo',
    'valencia-barrio-a-barrio-29n': 'La izquierda que se encogió',
    'sevilla-barrio-a-barrio-29n': 'Ganar calles, perder votos',
    'zaragoza-barrio-a-barrio-29n': 'Una ciudad a cara o cruz',
    'malaga-barrio-a-barrio-29n': 'Dos Málagas en las urnas',
    'murcia-barrio-a-barrio-29n': 'Vox se queda en la huerta',
    'palma-barrio-a-barrio-29n': 'La abstención manda',
    'como-voto-tu-calle': 'Tu sección, en el mapa',
    'calle-que-parte-el-voto': 'Vecinos que votan distinto',
    'pobreza-participacion-barrios': 'Pobreza y territorio',
    'ministros-listas-29n': 'Los ministros, a las listas',
    'ciudadanos-democracia21-29n': 'Ciudadanos, con otro nombre',
    'alianca-catalana-ceo-mapa': 'El CEO y Aliança',
    'pensiones-barrios-envejecidos': 'Las pensiones, en campaña',
    'acampada-sol-distrito-centro': 'La acampada de Sol',
    'ultimo-escano-29n': 'El último escaño',
    'izquierda-dividida-29n': 'La izquierda, ¿junta o separada?',
    'vivienda-inmigracion-economia-cis': 'Barómetro del CIS',
    'beiras-nacionalismo-gallego': 'Adiós a Beiras',
    'colau-barcelona-comuns': 'Colau y Barcelona',
    'votar-en-noviembre': 'Elecciones en noviembre',
    'maricarmen-alquiler-y-voto': 'Inquilinos y voto',
    'alquiler-ciudad-a-ciudad': 'El alquiler, ciudad a ciudad',
    'pisos-turisticos-y-votantes': 'Pisos turísticos',
    'psoe-barrios-de-alquiler': 'El PSOE y el alquiler',
    'precio-del-alquiler-y-voto': 'El precio del alquiler',
    'puigdemont-junts-congreso-parlament': 'Puigdemont y Junts',
    'rufian-erc-comuns': 'Rufián y ERC',
    'psoe-andalucia-generales-autonomicas': 'El PSOE en Andalucía',
    'huelga-11n-paro-participacion': 'Huelga del 11N',
    'psoe-madrid-municipales-generales': 'El PSOE en Madrid',
    'izquierda-del-psoe-secciones': 'La izquierda del PSOE',
    'vox-poblacion-nacida-fuera': 'Vox e inmigración',
    'almeida-feijoo-madrid': 'Almeida y Feijóo',
    'aceituna-de-mesa-pueblos': 'La aceituna de mesa',
}


def antetitulo(q):
    return ANTETITULOS.get(q['slug']) or (q['lugar'] if q['serie'] == 'comunidades' else SERIES[q['serie']])

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

    main = re.sub(r'<span class="draft">.*?</span>\n?', f'<p class="kicker"><a href="../index.html">Actualidad</a> · {antetitulo(p)}{"" if antetitulo(p) == p["lugar"] else " · " + p["lugar"]}</p>\n', main)
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
        main = main.replace(texto, f'<a href="../{slug}/">{texto}</a>', 1)
    fuentes = ''.join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u, t in p['fuentes'])
    # la serie entera, en orden, con la pieza actual marcada; después, las últimas de otras series
    serie = [q for q in todas if q['serie'] == p['serie']]
    lista = ''.join(f'<li aria-current="page"><span class="kicker">Estás aquí</span><b>{html.escape(q["titulo"])}</b></li>' if q is p else
                    f'<li><a href="../{q["slug"]}/"><b>{html.escape(q["titulo"])}</b></a></li>' for q in serie)
    otras = [q for q in todas if q['serie'] != p['serie']][::-1][:3]
    sigue = ''.join(f'<li><a href="../{q["slug"]}/"><span class="kicker">{antetitulo(q)}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in otras)
    terr = enlaces_actualidad(p['slug'], '../../')
    mas = ('<p class="mas-datos">Más datos: ' + ' · '.join(f'<a href="{u}">{html.escape(t)}</a>' for u, t in terr) + '.</p>') if terr else ''
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
{mas}
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
    # «Preguntas rápidas» (comunidades/faq.py): además de NewsArticle, FAQPage con las mismas preguntas y respuestas
    qs = re.findall(r'<h3>(.*?)</h3><p>(.*?)</p>', re.search(r'<div class="faq">(.*?)</div>', main, re.S).group(1)) if '<div class="faq">' in main else []
    if qs:
        jsonld = [jsonld, {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
                           'isPartOf': {'@id': url + '#articulo'},
                           'mainEntity': [{'@type': 'Question', 'name': html.unescape(q), 'acceptedAnswer': {'@type': 'Answer', 'text': html.unescape(r)}}
                                          for q, r in qs]}]
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
                ''.join(f'<li><a href="{q["slug"]}/">{imagen_tarjeta(q)}<span class="txt"><span class="kicker">{fecha_larga(q["fecha"])} · {q["lugar"]}</span><b>{html.escape(q["titulo"])}</b><span class="d">{html.escape(q["descripcion"])}</span></span></a></li>'
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
                    f'<span class="atlas-k">{antetitulo(q)}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in ult) +
            f'<li class="todas"><a href="{pre}actualidad/"><b>Las {len(todas)} piezas de actualidad →</b><span>{" · ".join(SERIES[k] for k in SERIES)}</span></a></li></ul>'
            '<style>.del-actualidad .carrusel img{object-fit:contain;background:#fff}.del-actualidad .carrusel img.ilu{background:none}</style>'
            '<script>document.querySelectorAll(".del-actualidad").forEach(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})</script></section>')


FRANJAS = (('historia', 'Historia electoral · desde 1977', 'Todas las elecciones generales desde 1977'),
           ('comunidades', 'Las comunidades en las urnas', 'Un reportaje por comunidad, con su mapa municipal'))


def franja_serie(todas, clave, cabecera, sub, pre=''):
    """Carrusel de una serie en la portada, debajo del de Actualidad: la serie entera, en su orden."""
    serie = [q for q in todas if q['serie'] == clave]
    return (f'<section class="wide del-atlas del-actualidad" aria-labelledby="h-del-{clave}"><div class="da-cab"><h2 id="h-del-{clave}"><a href="{pre}actualidad/#{clave}">{cabecera}</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Piezas anteriores">←</button><button type="button" class="da-next" aria-label="Más piezas">→</button></span></div>'
            '<ul class="carrusel">' +
            ''.join(f'<li><a href="{pre}actualidad/{q["slug"]}/">{imagen_carrusel(q, pre)}'
                    f'<span class="atlas-k">{q["lugar"]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in serie) +
            f'<li class="todas"><a href="{pre}actualidad/#{clave}"><b>Las {len(serie)} piezas de la serie →</b><span>{sub}</span></a></li></ul>'
            '<script>(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})(document.currentScript.parentNode)</script></section>')


def portada(todas):
    for f, pre in ((os.path.join(RAIZ, 'index.html'), ''), (os.path.join(RAIZ, 'generales-2026', 'src', 'plantilla.html'), '../')):
        t = open(f, encoding='utf-8').read()
        if '<!--actualidad:ultimas-->' not in t:   # la franja va justo encima de la del Atlas
            t = t.replace('<!--atlas:ultimas-->', '<!--actualidad:ultimas--><!--/actualidad:ultimas-->\n<!--atlas:ultimas-->', 1)
        ancla = '<!--/actualidad:ultimas-->'
        for clave, cabecera, sub in FRANJAS:   # cada serie, en su carrusel, debajo de Actualidad y de la serie anterior
            if f'<!--actualidad:{clave}-->' not in t:
                t = t.replace(ancla, f'{ancla}\n<!--actualidad:{clave}--><!--/actualidad:{clave}-->', 1)
            t = re.sub(rf'<!--actualidad:{clave}-->.*?<!--/actualidad:{clave}-->',
                       lambda m: f'<!--actualidad:{clave}-->' + franja_serie(todas, clave, cabecera, sub, pre) + f'<!--/actualidad:{clave}-->', t, flags=re.S)
            ancla = f'<!--/actualidad:{clave}-->'
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
    import esquema   # autor común, Dataset y migas de pan en todas las páginas (src/esquema.py)
    esquema.main()
    print('Actualidad:', len(PIEZAS), 'piezas')
