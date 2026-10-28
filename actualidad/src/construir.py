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
from territorios_rutas import enlaces_actualidad, bloque_municipios_pieza  # noqa: E402  páginas por territorio, municipio y tema
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
INTERIOR_CERA = ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/',
                 'Ministerio del Interior, resultados electorales por mesa y voto CERA (municipio 999), vía pollspaindata')
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
# Piezas sin ilustración ni foto: su primer gráfico como imagen principal (1280x720) en NewsArticle y en el RSS, para Google Discover.
# Las hace actualidad/src/graficos_principales.py desde la pieza publicada; pie y fuente, en graficos_principales.json
GRAFICO_PRINCIPAL = {s: dict(src=f'img/actualidad/fotos/{s}-grafico.jpg', ancho=1280, alto=720, grafico=True, **v)
                     for s, v in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'graficos_principales.json'), encoding='utf-8')).items()}

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
        actualizado='2026-10-20',
        correcciones='20-10-2026: la lista de fuentes decía «sin voto exterior (CERA)», pero los cálculos sí incluyen el voto exterior, como indican los gráficos y los límites. Se corrige la fuente. Las cifras no cambian.',
        fuentes=[INTERIOR_CERA,
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
        slug='alianca-catalana-ceo-mapa', fecha='2026-10-15', actualizado='2026-10-23 23:05',
        titulo='El CEO da a Aliança Catalana hasta 25 escaños: en el Parlament de 2024 sacó el 3,8%, pero el 24,9% en el Ripollès y el 7,8% en los pueblos de menos de 1.000 electores', serie='29n',
        descripcion='Aliança no se presenta el 29N, pero el barómetro del CEO la sitúa como tercera fuerza en unas elecciones al Parlament. Su único resultado oficial dibuja un mapa con centro en el Ripollès, fuerte en el norte de Girona y el interior, y débil en el área de Barcelona.',
        compara='El voto a Aliança Catalana en las elecciones al Parlament de 2024 en los 947 municipios de Cataluña, por comarca, provincia y tamaño del municipio, junto al de Junts y Vox.',
        limites='El barómetro del CEO es una encuesta con un margen de error de ±2,19 puntos y pregunta por unas elecciones al Parlament: no es una previsión para el 29N, donde Aliança no se presenta. El mapa es el de 2024, cuando Aliança sacó el 3,8%: no dice dónde crecería. Sin voto exterior. Varias citas académicas llegan a través de otros medios y se reproducen en catalán, como se publicaron.',
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
                  pie='Sílvia Orriols, un ayuntamiento, unas barras y un mapa de Cataluña: un collage.'),
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
                  pie='La Gran Vía y el edificio Metrópolis junto a un mapa de Madrid y un plano de calles, en collage.'),
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
        actualizado='2026-10-20',
        correcciones='17-10-2026: actualizada tras la dimisión de Mínguez como portavoz del PSOE; Cristina Morón la sustituye como cabeza de lista del PSC por Lleida. Titular y entradilla cambiados en consecuencia. 20-10-2026: el primer párrafo aún decía que Mínguez «encabezará otra vez la lista»; ahora dice que fue ratificada y dimitió el 16 de octubre. «Lo que se juega Mínguez» pasa a «lo que se juega el PSC».',
        titulo='Montse Mínguez dimite y deja la lista de Lleida: el PSC duplicó allí su voto en 2023 y le ganó el cuarto diputado al PP por unos 3.500 votos', serie='29n',
        descripcion='La portavoz del PSOE dimitió el 16 de octubre por la polémica de los negocios inmobiliarios de su pareja, y Cristina Morón la sustituye como número uno del PSC por Lleida. En 2023, el PSC pasó del 14,6% al 29,8% en la provincia y ganó en 79 municipios, frente a 8 en 2019.',
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
                 ('https://www.infobae.com/espana/agencias/2026/10/16/la-dimision-de-la-portavoz-socialista-trastoca-el-comite-federal-del-psoe/', 'Efe en Infobae, la dimisión de la portavoz socialista trastoca el Comité Federal del PSOE (16-10-2026)'),
                 ('https://lamanyana.cat/montse-minguez-cap-de-llista-del-psc-per-lleida-al-congres/', 'La Mañana, la lista del PSC por Lleida (15-10-2026)'),
                 ('https://lamanyana.cat/quatre-escons-en-joc-a-lleida/', 'La Mañana, cuatro escaños en juego en Lleida (7-10-2026)'),
                 ('https://laciutat.cat/laciutatdelleida/ines-granollers-proclamada-cap-llista-esquerra-republicana-catalunya-congres-demarcacio-lleida-eleccions-generals_902682_102.html', 'La Ciutat, Inés Granollers, candidata de ERC (12-10-2026)'),
                 ('https://ebredigital.cat/2026/10/08/josep-maria-cruset-tornara-a-ncapcalar-la-llista-de-junts-al-congres-el-29n/', 'EbreDigital, las listas de Junts (8-10-2026)'),
                 ('https://lamanyana.cat/vuit-pobles-lleidatans-entren-a-la-regulacio-del-lloguer-del-govern/', 'La Mañana, Lleida sale de las zonas tensionadas (29-7-2026)'),
                 ('https://www.eldiario.es/madrid/somos/estudio-descubre-influye-voto-madrid-efecto-alquiler-barrio-vivas_1_12961596.html', 'elDiario.es, Álvaro Sánchez García sobre alquiler y voto en Madrid (9-2-2026)')],
        enlaces=[],
        lugar='Lleida',
        foto=dict(src='img/actualidad/fotos/minguez-lleida-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Montse Mínguez, unas llaves, un bloque de pisos y la Seu Vella de Lleida sobre el Segre: un collage.'),
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
    dict(
        slug='senado-29n', fecha='2026-10-20',
        actualizado='2026-10-23 23:15',
        titulo='El Senado de 2023: 120 senadores para el PP con un tercio de los votos', serie='29n',
        descripcion='Con el voto limitado, el PP ganó el 57,7 % de los 208 senadores de 2023 con el 33,1 % del voto al Congreso. Vox y Sumar, con más del 12 % cada uno, no ganaron ninguno.',
        compara='El porcentaje de voto al Congreso y el de senadores por partido en las elecciones de julio de 2023, y el reparto por circunscripción (provincias de cuatro escaños, insulares, Ceuta y Melilla).',
        limites='El Senado no es proporcional por diseño: cada provincia elige cuatro senadores con voto limitado, de modo que el peso del voto en el Congreso y en el Senado no es el mismo. Los datos son los de la elección de julio de 2023; la del 29N no cambia esas reglas.',
        fuentes=[(INTERIOR[0], 'Ministerio del Interior, resultados del Senado de julio de 2023 (Infoelectoral), ficheros de candidaturas, candidatos y votos'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229#a69', 'Constitución Española, artículo 69'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#acientosesentayseis', 'BOE, Ley Orgánica del Régimen Electoral General, artículo 166')],
        enlaces=[],
        lugar='España',
        figura=0,
        foto=dict(src='img/actualidad/fotos/senado-2023-infografia.png', ancho=900, alto=900, grafico=True,
                  pie='Barras por partido: voto al Congreso frente a senadores, julio de 2023.', fuente='Ministerio del Interior'),
    ),
    dict(
        slug='precio-del-escano-29n', fecha='2026-10-15',
        titulo='Un diputado cuesta 25.300 votos en Teruel y 97.500 en Madrid: el precio del escaño, provincia a provincia', serie='29n',
        descripcion='En 2023, un escaño en Madrid costó casi cuatro veces más votos que en Teruel o Soria, y Sumar pagó cada diputado a 98.225 votos frente a los 59.570 del PP. Con un simulador que reparte los votos de 2023 y 2019 por comunidades o en una circunscripción única.',
        compara='Los votos válidos por escaño en las 52 circunscripciones y los votos por escaño de cada partido en las generales de julio de 2023 (y de noviembre de 2019 y 2015 como contraste), y el reparto de los mismos votos con circunscripción autonómica o única, con y sin barrera del 3 % y con D\'Hondt o Sainte-Laguë.',
        limites='El simulador es un cálculo mecánico, no una previsión: con otras reglas los electores y los partidos se habrían comportado de otra manera (voto útil, listas, coaliciones). La circunscripción autonómica o única exigiría reformar la Constitución (artículo 68.2). «Por comunidad» conserva los escaños actuales de cada provincia; las listas con menos del 0,1 % en España van juntas como «Otros» y no reciben escaños. Votos con voto exterior (CERA); los electores residentes excluyen el censo CERA.',
        fuentes=[(INTERIOR[0], 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata, con voto exterior (CERA)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229#a68', 'Constitución Española, artículo 68'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#acientosesentaydos', 'BOE, Ley Orgánica del Régimen Electoral General, artículos 162 y 163'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742', 'BOE, Real Decreto 806/2026, de convocatoria de elecciones (6-10-2026)'),
                 ('https://www.gutierrez-rubi.es/wp-content/uploads/2010/03/regimen-electoral.pdf', 'Consejo de Estado, Informe sobre las propuestas de modificación del régimen electoral general (24-2-2009), copia en PDF'),
                 ('https://recyt.fecyt.es/index.php/recp/article/download/37589/21106', 'Penadés y Santiuste, La desigualdad en el sistema electoral español y el premio a la localización del voto, Revista Española de Ciencia Política 32 (2013)'),
                 ('https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso', 'Annick Laruelle, El reparto de los escaños en el Congreso, Campusa UPV/EHU (24-5-2019)'),
                 ('https://www.lamarea.com/2015/12/21/garzon-se-desploma-pero-mantiene-con-vida-a-iu/', 'La Marea, Garzón se desploma pero mantiene con vida a IU (21-12-2015)'),
                 ('https://www.eldiario.es/politica/alberto-garzon-pedro-sanchez-manifesto_1_2804718.html', 'elDiario.es, entrevista a Alberto Garzón (Aitor Riveiro, 8-2-2018)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='votos-sin-escano-29n', fecha='2026-10-15',
        titulo='1,9 millones de votos no eligieron a nadie en 2023: en Teruel, Lleida y Soria, uno de cada tres', serie='29n',
        descripcion='Fueron el 7,8 % del voto válido, frente al 10,6 % de noviembre de 2019. Sumar dejó sin escaño el 19,9 % de sus votos y Vox, el 16,1 %; el PSOE, el 0,2 %. Por partido y provincia, con los escaños que se decidieron por menos de mil votos.',
        compara='Los votos de las candidaturas que no obtuvieron ningún escaño en su circunscripción, por partido y por provincia, en las generales de julio de 2023 y de noviembre de 2019, y los últimos escaños que se decidieron por menos de 1.000 votos.',
        limites='No es una proyección de 2026. Solo cuenta como voto sin escaño el de las listas que no sacaron ningún diputado en la provincia; los votos en blanco van aparte. Los márgenes son los votos adicionales que necesitaba el aspirante sin que nadie más cambie. Cálculo propio con D\'Hondt, barrera del 3 % sobre voto válido y voto exterior (CERA) incluido, por eso puede diferir de las cifras de la noche electoral.',
        fuentes=[(INTERIOR[0], 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata, con voto exterior (CERA)'),
                 ('https://www.democrata.es/politica/el-psoe-reclama-el-voto-util-en-provincias-pequenas-para-que-apoyos-a-la-izquierda-no-vayan-a-la-basura/', 'Europa Press vía Demócrata, el PSOE reclama el voto útil en provincias pequeñas (13-10-2026)'),
                 ('https://www.gutierrez-rubi.es/wp-content/uploads/2010/03/regimen-electoral.pdf', 'Consejo de Estado, Informe sobre las propuestas de modificación del régimen electoral general (24-2-2009), copia en PDF'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672#acientosesentaytres', 'BOE, Ley Orgánica del Régimen Electoral General, artículo 163 (barrera del 3 % y regla D\'Hondt)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='pensiones-censo-mayores-29n', fecha='2026-10-16',
        titulo='Feijóo y Sánchez chocan por las pensiones en un censo con 10,2 millones de electores de 65 años o más: superan a los de 18 a 34 en 49 de las 52 provincias', serie='29n',
        descripcion='En Zamora, Ourense y Lugo hay casi tres electores mayores por cada joven. Las nueve provincias donde los mayores doblan a los jóvenes eligen 34 diputados, y en todas ganó el PP en 2023.',
        compara='Los electores residentes en España de 65 años o más y de 18 a 34 en cada una de las 52 provincias, según el censo de consulta de las generales del 29N y el de 2023, junto al partido más votado en cada provincia en 2023 y los escaños que elige el 29N.',
        limites='El censo cuenta electores, no votantes ni preferencias: no dice a quién vota cada generación ni cuánto pesan las pensiones en el voto. No incluye a los electores residentes en el extranjero. El partido más votado en 2023 se calcula sin voto exterior; en Navarra, UPN y PP, que concurrieron por separado, aparecen sumados en nuestros datos, y se usa el resultado oficial (PSOE). Las citas de los protagonistas son de la prensa que se enlaza.',
        fuentes=[('https://www.ine.es/oficina_censo/elecgen2026/Elecgral_2026_cc_tab11.xlsx', 'INE, Oficina del Censo Electoral: electores por edad y provincia, generales de 2026'),
                 ('https://www.ine.es/oficina_censo/elecgen2023/Elecgral_2023_cc_tab11.xlsx', 'INE, Oficina del Censo Electoral: electores por edad y provincia, generales de 2023'),
                 INTERIOR,
                 ('https://www.lavanguardia.com/politica/20261016/11660046/feijoo-garantiza-revalorizara-pensiones-sanchez-le-acusa-mentir.html', 'La Vanguardia, Feijóo garantiza que revalorizará las pensiones y Sánchez le acusa de mentir (16-10-2026)'),
                 ('https://www.eldiario.es/economia/vox-defiende-reforma-privatizacion-pensiones-da-muerto-sistema-publico-actual_1_13565422.html', 'elDiario.es, Vox y la reforma de las pensiones (6-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/abascal-promete-pagar-pensiones-y-garantizar-vivienda-como-sea-y-refuerza-su-llamamiento-al-voto-presencial/', 'Demócrata, Abascal en Estepona (11-10-2026)'),
                 ('https://www.infobae.com/economia/2026/10/13/feijoo-despeja-la-duda-sobre-que-hara-con-las-pensiones-si-llega-a-la-moncloa-las-subira-con-el-ipc/', 'Infobae, Feijóo en esRadio (13-10-2026)'),
                 ('https://www.inclusion.gob.es/en/w/la-pension-media-del-sistema-de-la-seguridad-social-alcanza-los-1.374-6-euros-en-septiembre-un-4-6-mas-alta-que-hace-un-ano', 'Ministerio de Inclusión, Seguridad Social y Migraciones, pensiones de septiembre de 2026'),
                 ('https://www.articulo14.es/economia/el-voto-del-miedo-los-ingresos-de-casi-la-mitad-del-censo-depende-del-gobierno-20261013.html', 'Artículo 14, el calendario de la revalorización (13-10-2026)'),
                 ('https://fedea.net/instituciones-envejecimiento-y-equidad-intergeneracional/', 'Fedea, José Ignacio Conde-Ruiz, Instituciones, envejecimiento y equidad intergeneracional (julio de 2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pensiones-censo-mayores-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Electores de 65 años o más por cada elector de 18 a 34 en las 20 provincias más envejecidas, coloreadas por el partido más votado en 2023.',
                  fuente='INE, censo electoral del 29N; Ministerio del Interior'),
    ),
    dict(
        slug='cis-tezanos-estimacion-29n', fecha='2026-10-16',
        titulo='El CIS de Tezanos da al PSOE 11,8 puntos de ventaja: en las tres generales desde 2019 sobrestimó su margen sobre el PP entre 1 y 6,9 puntos', serie='29n',
        descripcion='En noviembre de 2019, el CIS de octubre daba al PSOE 14,1 puntos sobre el PP y fueron 7,2. En 2023, la última encuesta ponía al PSOE 1,4 puntos por delante y ganó el PP por 1,4.',
        compara='La estimación de voto de PSOE y PP en el último gran estudio del CIS antes de cada una de las cinco generales desde 2015 (seis estimaciones, dos de ellas de 2023) frente al resultado oficial, y la estimación del barómetro de octubre de 2026.',
        limites='No es una previsión del 29N ni una estimación propia: compara estimaciones publicadas por el CIS con resultados oficiales. Solo mide la ventaja entre PSOE y PP, no el resto de partidos. Se toma el último gran estudio con estimación de cada elección; en noviembre de 2019 es el macrobarómetro de octubre. Cinco elecciones son una muestra pequeña y los datos no dicen por qué se desvió la estimación.',
        fuentes=[('https://www.cis.es/documents/d/guest/3582_estimacion-pdf', 'CIS, estudio 3582, barómetro de octubre de 2026: estimación de voto'),
                 ('https://www.cis.es/documents/d/cis/3411_estimacion', 'CIS, estudio 3411, preelectoral de las generales de 2023'),
                 ('https://www.cis.es/documents/d/cis/es3415marmt_a', 'CIS, estudio 3415, encuesta flash de las generales de 2023'),
                 ('https://www.cis.es/documents/d/cis/3263_estimacion', 'CIS, estudio 3263, macrobarómetro de octubre de 2019'),
                 ('https://www.cis.es/documents/d/cis/es3242mar_a', 'CIS, estudio 3242, preelectoral de las generales de abril de 2019'),
                 ('https://www.cis.es/documents/d/cis/es3141mar_a', 'CIS, estudio 3141, preelectoral de las generales de 2016'),
                 ('https://www.cis.es/documents/d/cis/es3117mar_a', 'CIS, estudio 3117, preelectoral de las generales de 2015'),
                 INTERIOR,
                 ('https://www.elindependiente.com/espana/2023/07/25/tezanos-saca-pecho-por-haberse-desviado-solo-unas-decimas-con-las-encuestas-del-cis/', 'El Independiente, Tezanos tras el 23J (25-7-2023)'),
                 ('https://www.eldebate.com/espana/20260217/datos-cis-analizados-sociologo-independiente-pp-sacaria-24-puntos-psoe-vox-superaria-20_385845.html', 'El Debate, la reestimación de Target Point (17-2-2026)'),
                 ('https://es.wikipedia.org/wiki/Jos%C3%A9_F%C3%A9lix_Tezanos', 'Wikipedia, José Félix Tezanos')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/cis-tezanos-estimacion-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='José Félix Tezanos entre un cuestionario, unas barras y una oficina: un collage.'),
    ),
    dict(
        slug='rufian-fracaso-lista-unitaria-29n', fecha='2026-10-16',
        titulo='Rufián admite «He fracasado»: con los votos de 2023, ERC y Sumar juntos habrían sacado un solo diputado más en Cataluña, y por 126 votos', serie='29n',
        descripcion='El escaño habría salido de Barcelona y se lo habrían quitado al PSC. En Girona, Lleida y Tarragona, la suma no habría cambiado nada.',
        compara='El reparto de escaños de 2023 en las cuatro provincias catalanas tal como fue y el que habría salido si los votos de ERC y Sumar se hubieran sumado en una sola lista, con la regla D\'Hondt.',
        limites='Es una simulación aritmética, no una previsión: supone que todos los votantes de ERC y de Sumar en 2023 habrían votado la lista conjunta, y en la realidad una coalición gana y pierde votos. Se usan los votos sin el voto exterior (CERA), por lo que pueden diferir en unas decenas de los oficiales; con un margen de 126 votos, el resultado de Barcelona es frágil. Sumar concurrió en 2023 con Podemos y los Comuns en su lista; en 2026 el espacio va dividido de otra forma.',
        fuentes=[INTERIOR,
                 ('https://www.que.es/2026/10/16/unidad-izquierda-29n-sin-pacto/', 'Qué!, Rufián en RAC1: «He fracasado y hemos fracasado» (16-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/16/elecciones-generales-espana-29-n-en-directo-ultima-hora-del-frente-amplio-y-del-viernes-clave-para-la-izquierda/', 'Infobae, directo del 16-10-2026: Colau y Bustinduy'),
                 ('https://ara.cat/es/articulo-pablo-simon-manipulacion-electoral_0_1481252043.html', 'Ara, entrevista a Pablo Simón')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/rufian-fracaso-lista-unitaria-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Gabriel Rufián e Irene Montero, con el hemiciclo del Congreso y dos papeles en blanco entre ambos: un collage.'),
    ),
    dict(
        slug='desahucios-ocupaciones-cgpj-29n', fecha='2026-10-16',
        titulo='Ocupación: en las provincias con más demandas ante los juzgados, Vox sacó el 15,9% en 2023, frente al 11,5% en las que menos', serie='29n',
        descripcion='Los datos del CGPJ publicados hoy: los desahucios por alquiler caen un 57,7% y las demandas por ocupación, un 9%. Por habitante, Ávila, Baleares y Girona encabezan las demandas; el cruce con el voto de 2023 apenas dibuja un patrón.',
        compara='Los lanzamientos practicados y las demandas por ocupación ilegal de vivienda ingresadas en los juzgados por trimestre desde 2025, y por provincia en 2025 por cada 100.000 habitantes, junto al voto de 2023 en cada provincia.',
        limites='Lanzamientos y demandas no son la misma cosa: los primeros son desalojos ya ejecutados por cualquier causa y las segundas, procedimientos que empiezan y pueden no acabar en desalojo. La estadística de ocupación del CGPJ solo recoge los juicios verbales que pueden iniciar personas físicas, entidades sin ánimo de lucro y administraciones con vivienda social (Ley 5/2018); no incluye las ocupaciones que denuncian bancos o fondos ni la vía penal. Las tasas usan la población oficial del padrón a 1 de enero de 2021 (INE), la última serie provincial que hemos podido descargar; desde entonces la población ha crecido y las tasas actuales serían algo más bajas; Ceuta y Melilla no figuran en la tabla provincial del CGPJ. En provincias pequeñas, unas pocas demandas mueven mucho la tasa. El cruce con el voto es entre provincias, no entre personas, y no permite conclusiones causales. Vox no tuvo lista al Congreso en Santa Cruz de Tenerife en 2023, por lo que esa provincia no aparece en el gráfico de Vox. El partido más votado se calcula sin voto exterior; en Navarra se usa el resultado oficial (PSOE).',
        fuentes=[('https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Consejo-General-del-Poder-Judicial/Oficina-de-Comunicacion/Notas-de-prensa/Los-organos-judiciales-practicaron-4-474-lanzamientos-en-el-segundo-trimestre--un-35-7---menos-que-en-el-mismo-periodo-del-ano-pasado', 'CGPJ, nota de prensa del 2.º trimestre de 2026 (16-10-2026)'),
                 ('https://www.poderjudicial.es/cgpj/es/Temas/Estadistica-Judicial/Estudios-e-Informes/Efecto-de-la-Crisis-en-los-organos-judiciales/', 'CGPJ, Datos sobre el efecto de la crisis en los órganos judiciales (2.º trimestre de 2026 y anual de 2025)'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=2852', 'INE, cifras oficiales de población por provincia (padrón a 1 de enero de 2021)'),
                 INTERIOR,
                 ('https://www.eldebate.com/espana/cataluna/20221021/feijoo-propone-el-desalojo-en-24-horas-de-las-viviendas-okupadas_67662.html', 'El Debate, Feijóo propone el desalojo en 24 horas (21-10-2022)'),
                 ('https://forbes.es/ultima-hora/408900/rodriguez-sobre-ley-antiokupa-pide-a-pp-que-se-centre-en-el-problema-de-acceso-a-la-vivienda/', 'Forbes, Isabel Rodríguez sobre la ley antiokupa (8-2-2024)'),
                 ('https://www.ultimahora.es/noticias/nacional/2024/09/11/2239237/ministra-cifra-riesgo-ocupacion-vivienda-espana.html', 'Última Hora, la ministra cifra el riesgo de ocupación en el 0,06% (11-9-2024)'),
                 ('https://www.boe.es/biblioteca_juridica/anuarios_derecho/abrir_pdf.php?id=ANU-V-2025-13000000060', 'Matilde Cuena Casas, El problema de la ocupación ilegal en España, Tratado de Derecho de la vivienda (BOE, 2025)'),
                 ('https://www.pp.es/storage/2024/02/240207_ley_antiokupacion_la_primera_de_las_leyes_feijoo_-_titulares.pdf', 'PP, el Senado toma en consideración la ley antiokupación (7-2-2024)'),
                 ('https://rtvc.es/rechazan-recursos-vox-por-candidatura-santa-cruz-de-tenerife/', 'RTVC, Vox sin candidatura al Congreso en Santa Cruz de Tenerife en 2023')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/desahucios-ocupaciones-cgpj-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Dos policías acompañan a una mujer con una caja hasta un portal; en el suelo, un juego de llaves: un collage.'),
    ),
    dict(
        slug='pactos-izquierda-mapa-final-29n', fecha='2026-10-17',
        titulo='Frente Amplio y Podemos solo irán juntos en cinco provincias: en las otras 47, Sumar sacó 26 de sus 31 diputados en 2023', serie='29n',
        descripcion='Se cerró el plazo de coaliciones. Habrá papeleta común en Canarias y la Comunitat Valenciana; en Baleares y Aragón, el Frente Amplio va con partidos territoriales y sin Podemos, y en Cataluña Podemos entra en las listas de ERC.',
        compara='Las coaliciones registradas por el Frente Amplio y Podemos para el 29N en cada provincia, junto a los votos y escaños que Sumar, que en 2023 los reunía a todos, sacó en esas provincias en las generales de 2023.',
        limites='Las coaliciones salen de la prensa del 16 y 17 de octubre (Público, elDiario.es, Europa Press y Efe), no de la publicación oficial de la Junta Electoral, que puede matizar algún caso; en Extremadura, la información es menos clara. Que no haya coalición no significa que Podemos vaya a presentar lista en todas las provincias: las candidaturas se registran más tarde. Sumar se presentó en 2023 con Podemos, IU, Compromís, Más Madrid, los comuns y otros partidos; sus votos de 2023 describen dónde estaba ese voto, no cómo se repartirá ahora. No calculamos escaños para el 29N. Los votos de 2023 incluyen el voto exterior.',
        actualizado='2026-10-20',
        correcciones='20-10-2026: la lista de fuentes decía «sin voto exterior (CERA)», pero los cálculos sí incluyen el voto exterior, como indican los gráficos y los límites. Se corrige la fuente. Las cifras no cambian.',
        fuentes=[INTERIOR_CERA,
                 ('https://www.publico.es/politica/frente-amplio-podemos-concurriran-separado-29-noviembre-salvo-canarias-pais-valencia.html', 'Público, Frente Amplio y Podemos concurrirán por separado salvo en Canarias y País Valencià (16-10-2026)'),
                 ('https://www.eldiario.es/politica/son-acuerdos-izquierda-alternativa-territorio-territorio_1_13589702.html', 'elDiario.es, así han quedado las candidaturas de la izquierda alternativa, territorio a territorio (17-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/17/2730679/frente-amplio-podemos-consuman-fractura-llegar-acuerdo-global-para-coaliciones-29n.html', 'Última Hora (Europa Press y Efe), Frente Amplio y Podemos consuman su fractura (17-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/16/frente-amplio-y-podemos-consuman-su-choque-y-naufragan-en-el-intento-de-lograr-una-candidatura-unitaria/', 'Infobae (Europa Press), Frente Amplio y Podemos consuman su choque (16-10-2026)'),
                 ('https://www.mundiario.com/articulo/politica/izquierda-divide-29-n-une-disputar-senado-pp/20261017002549447277.html', 'Mundiario, la izquierda se divide para el 29-N pero se une en el Senado (17-10-2026)'),
                 ('https://www.nuevatribuna.es/articulo/actualidad/union-division-frente-amplio-elecciones-podemos-sumar-politica/20221227165009206442.html', 'Antonio Antón, La unión y la división del frente amplio, Nueva Tribuna (27-12-2022)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pactos-izquierda-mapa-final-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las coaliciones de la izquierda a la izquierda del PSOE para el 29N, provincia a provincia.',
                  fuente='Público, elDiario.es, Europa Press y Efe; elaboración propia'),
    ),
    dict(
        slug='ley-nietos-voto-exterior-29n', fecha='2026-10-20',
        titulo='El voto de fuera, el del «pucherazo», le dio un escaño al PP en 2023', serie='29n',
        descripcion='En 2023 el voto exterior cambió el último diputado de Madrid, del PSOE al PP. Para el 29N, el censo de fuera ha crecido un 19%, el Supremo mantiene sin voto a 163.020 nacionalizados por la ley de nietos y un estudio del CEU estima que los nietos inscritos son unos 250.000.',
        compara='El voto de los residentes en el extranjero (CERA) en las generales de 2023 por provincia frente al voto emitido en España, el reparto del último escaño de Madrid con y sin ese voto, y el censo de residentes en el extranjero de 2023 frente al del 29N.',
        limites='Interior asigna el voto exterior a cada provincia como municipio 999; se usa así. El censo de 2023 es el que figura en los ficheros de Interior y el de 2026 el que publica el INE, que pueden no medir exactamente lo mismo. No hay datos públicos de cuántos de los 163.020 suspendidos hay en cada provincia ni de cómo votarían, así que no se puede calcular a quién afecta la suspensión. Los porcentajes de PSOE incluyen al PSC y a sus federaciones, y los de Sumar todas sus marcas; el PP no incluye a UPN.',
        actualizado='2026-10-27 09:30',
        correcciones='20-10-2026: el aumento del censo exterior en Madrid (122.370) es el 27,7% del total (441.385), más de una cuarta parte, no «casi un tercio». Además, la lista de fuentes decía «sin voto exterior (CERA)», pero los cálculos sí incluyen el voto exterior, como indican los gráficos y los límites. Se corrige la fuente. Las cifras no cambian. También se corrige la nota de método, que decía «votos a candidaturas»: los porcentajes son sobre voto válido, como indica el gráfico, y la fuente del gráfico de Madrid, que ahora cita el voto CERA.',
        calculo='Porcentajes sobre voto válido (votos a candidaturas más votos en blanco), salvo la participación, que es sobre el censo.',
        fuentes=[INTERIOR_CERA,
                 ('https://www.ine.es/dyngs/Prensa/EG2026.htm', 'INE, Elecciones a Cortes Generales de 29 de noviembre de 2026, nota de prensa (9-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/10/12/el-tribunal-supremo-suspende-el-voto-de-los-nacionalizados-por-la-ley-de-nietos-para-las-elecciones-del-29n/', 'El Independiente, El Supremo suspende el voto de los nacionalizados por la ley de nietos (12-10-2026)'),
                 ('https://www.que.es/2026/10/13/ley-nietos-voto-supremo-29n-2/', 'Que.es, El Supremo deja sin voto el 29N a 163.020 nacionalizados (13-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-18/vox-constitucional-recurso-gabilondo-ley-de-nietos/', 'The Objective (Efe), Vox pide al Constitucional que inadmita el recurso de Gabilondo (18-10-2026)'),
                 ('https://www.infobae.com/america/agencias/2026/10/11/sanchez-pide-frenar-el-intento-de-atropello-que-impediria-votar-a-nietos-de-exiliados/', 'Infobae (Efe), Sánchez pide frenar el «intento de atropello» (11-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/12/vox-celebra-que-el-supremo-le-de-la-razon-con-la-ley-de-nietos-y-que-las-elecciones-se-celebren-sin-fraude/', 'Infobae (Europa Press), Vox celebra que el Supremo le dé la razón (12-10-2026)'),
                 ('https://www.publico.es/politica/1-26-millones-electores-incorporan-censo-29-n.html', 'Público (agencias), Más de 1,26 millones de electores se incorporan al censo (9-10-2026)'),
                 ('https://doi.org/10.5944/rdp.120.2024.41766', 'Álvarez Vélez y Corres-Illera, La relevancia del voto CERA, Revista de Derecho Político 120 (2024)'),
                 ('https://efe.com/espana/2026-10-26/jueces-lesion-irreparable-constitucional-ley-de-nietos/', 'Efe, Dos jueces advierten de una lesión «irreparable» ante el fallo del Constitucional por la ley de nietos (26-10-2026)'),
                 ('https://efe.com/espana/2026-10-26/albares-identificacion-afectados-ley-nietos/', 'Efe, Albares confía en que el miércoles estén identificados los afectados por la ley de nietos (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-hazte-oir-pide-supremo-extienda-suspension-voto-ley-nietos-hijos-beneficiados-20261026190143.html', 'Europa Press, Hazte Oír pide al Supremo que extienda la suspensión a los hijos de los beneficiados (26-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/10/26/ley-nietos-suma-250-000-electores-voto-exterior-estudio-ceu-cefas/', 'El Independiente (Europa Press), La ley de nietos suma 250.000 electores al voto exterior, según CEU-CEFAS (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-milei-vuelve-llamar-ladron-corrupto-sanchez-le-acusa-tratar-amanar-elecciones-ley-nietos-20261024160259.html', 'Europa Press, Milei acusa a Sánchez de tratar de amañar las elecciones con la ley de nietos (24-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ley-nietos-voto-exterior-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un pasaporte, un sobre que cruza el mapa de España y una urna ante el Congreso: un collage.'),
    ),
    dict(
        slug='senado-psoe-frente-amplio-29n', fecha='2026-10-20',
        titulo='PSOE y Frente Amplio, juntos al Senado: con los votos de 2023, su lista habría ganado al PP en 17 provincias donde este sacó tres senadores', serie='29n',
        descripcion='El PP habría bajado de 120 a 82 senadores elegidos, y el PSOE con la lista conjunta habría pasado de la mitad. Albacete queda empatada; Murcia, tres provincias gallegas y casi toda Castilla y León siguen siendo del PP.',
        compara='Los votos por candidato del PP frente a la suma de los del PSOE y Sumar en las elecciones al Senado de 2023, en las 40 provincias de cuatro senadores que entran en la lista conjunta.',
        limites='Es una simulación aritmética, no una previsión. Usa los votos por candidato (suma de votos de los candidatos de cada partido dividida entre los que presentó) y hace una suma mecánica con transferencia perfecta: supone que todos los votantes de PSOE y Sumar votarían a los tres candidatos de la lista conjunta, lo que en el voto limitado del Senado no está garantizado, y que no cambian la participación ni la estrategia de los demás partidos. Los votos son los oficiales de la Junta Electoral Central publicados en el BOE, con la corrección de un candidato del PSOE en Madrid. Los 72 senadores del PSOE de 2023 incluyen los del PSC y el PSE, que no entran en el pacto. No se modelan las islas, Ceuta y Melilla ni los senadores de designación autonómica.',
        actualizado='2026-10-20',
        correcciones='20-10-2026: la simulación usaba los votos por candidato de Wikipedia; ahora usa los oficiales de la Junta Electoral Central (BOE-A-2023-18907, con la corrección BOE-A-2023-19537). Con ellos entra Zaragoza, que antes quedaba fuera por falta de datos de Sumar, y donde la lista conjunta también habría ganado: son 17 provincias, no 16, y el PP bajaría a 82 senadores, no a 84. Se aclara que los 110 senadores (antes 108) suman los del PSOE de 2023, incluidos PSC y PSE, y los que ganaría la lista conjunta. Cambian ligeramente las cifras de Valencia, Málaga, Pontevedra y Toledo.',
        fuentes=[('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907', 'Junta Electoral Central, resumen de los resultados de las elecciones al Congreso y al Senado de 23 de julio de 2023, BOE de 1-9-2023'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-19537', 'Junta Electoral Central, corrección de errores, BOE de 16-9-2023'),
                 ('https://www.infobae.com/espana/2026/10/19/elecciones-generales-29-n-en-directo-ultima-hora-de-los-sondeos-la-ley-de-nietos-o-los-anuncios-sobre-pensiones/', 'Infobae (Efe), directo del 19-10-2026: orden de las listas conjuntas'),
                 ('https://www.publico.es/politica/partidos/psoe-frente-amplio-e-izquierdas-territoriales-unen-listas-conjuntas-senado.html', 'Público, El PSOE, el Frente Amplio e izquierdas territoriales se unen para el Senado (16-10-2026)'),
                 ('https://www.moncloa.com/2026/10/19/pacto-senado-psoe-frente-amplio-3451456/', 'Moncloa.com, PSOE y Frente Amplio sellan su pacto en 43 provincias (19-10-2026)'),
                 ('https://www.laregion.es/espana/presentara-pais-choque-frente_1_20261019-4457477.html', 'La Región, Podemos se presentará en todo el país (19-10-2026)'),
                 ('https://revista.cortesgenerales.es/rcg/article/download/98/91', 'Fabio Pascua Mateo, Cuarenta años de elecciones a las Cortes Generales, Revista de las Cortes Generales 103 (2018)'),
                 ('https://agendapublica.es/noticia/21546/45-senadores-plan-cambiar-mayoria-senado', 'Emilia Sánchez Pantoja, 45 senadores, Agenda Pública (8-10-2026)'),
                 ('https://www.vozpopuli.com/espana/politica/elecciones-generales-del-29-n-en-directo-ultima-hora-de-las-listas-electorales-sanchez-y-feijoo.html', 'Vozpópuli, directo del 17-10-2026'),
                 ('https://elespanol.com/espana/politica/20261019/derecha-conservaria-quintos-senado-vox-no-presenta-provincias-va-listas-pp/1003744425410_0.html', 'El Español, simulación del Senado (19-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/senado-psoe-frente-amplio-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Papeletas del Senado, un mapa de provincias y la fachada del Senado: un collage.'),
    ),
    dict(
        slug='albiol-badalona-pp-29n', fecha='2026-10-20', actualizado='2026-10-28 06:30',
        titulo='Albiol saca en Badalona tres veces los votos del PP', serie='29n',
        descripcion='En las municipales de 2023 le votaron 50.163 vecinos; dos meses después, el PP sacó 16.405 en las generales. Su ventaja es mayor en los barrios socialistas. Pero Badalona es el 4% del censo de la provincia: aunque arrastrara a todos sus votantes, el PP sumaría 1,3 puntos.',
        compara='El voto al PP en Badalona en las municipales de 2011, 2015, 2019 y 2023, con Xavier García Albiol de cabeza de lista, frente al voto al PP en las generales de abril y noviembre de 2019 y julio de 2023, en total y por sección censal.',
        limites='Los datos agregados por sección no permiten saber qué votantes cambiaron su voto ni cuántos se abstuvieron en una de las dos elecciones. El censo de las municipales incluye a residentes de la UE, que no votan en generales. No es una previsión: en 2026 Albiol se presenta al Congreso, no a la alcaldía. Los quintiles por voto al PSOE describen barrios, no personas. El techo de 1,3 puntos supone que todos los votantes municipales de Albiol votan al PP; no es una previsión. El modelo de encuestas es del 22 de octubre de 2026.',
        calculo='Porcentajes sobre voto válido (votos a candidaturas más votos en blanco), salvo la participación, que es sobre el censo. Quintiles: las 149 secciones ordenadas por voto al PSOE en julio de 2023, en cinco grupos de igual número de secciones, con porcentajes sobre la suma de votos de cada grupo. Correlación de Pearson por sección entre la diferencia del PP (municipales menos generales) y el voto a ERC más Junts en las generales.',
        fuentes=[INTERIOR,
                 ('https://www.europapress.es/catalunya/noticia-29n-albiol-dice-pp-tiene-claro-quien-vulnerable-verdad-jeta-20261024150522.html', 'Europa Press, Albiol: el PP tiene claro «quién es vulnerable de verdad» (24-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-albiol-pp-ve-absoluto-desprecio-sanchez-afectados-disturbios-barcelona-20261026131018.html', 'Europa Press, Albiol ve «absoluto desprecio» de Sánchez a los afectados por los disturbios (26-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_de_Catalu%C3%B1a_de_2015', 'Elecciones al Parlamento de Cataluña de 2015, resultados'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños'),
                 ('https://cronicaglobal.elespanol.com/politica/20261017/pp-confirma-albiol-cabeza-lista-barcelona-congreso/1003742803654_0.html', 'Crónica Global, El PP confirma a Albiol como cabeza de lista por Barcelona (17-10-2026)'),
                 ('https://www.democrata.es/politica/garcia-albiol-encabezara-la-lista-del-pp-por-barcelona-al-congreso/', 'Demócrata, García Albiol, número uno del PP por Barcelona (17-10-2026)'),
                 ('https://www.moncloa.com/2026/10/17/albiol-candidato-pp-barcelona-29n-3450251', 'Moncloa.com, Feijóo confirma a Albiol como candidato por Barcelona (17-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/19/albiol-reclama-controlar-la-inmigracion-irregular-si-no-acabaremos-como-francia/', 'Infobae (Europa Press), Albiol reclama controlar la inmigración irregular (19-10-2026)'),
                 ('https://econ-papers.upf.edu/papers/465.pdf', 'Clara Riba, Voto dual y abstención diferencial, Universitat Pompeu Fabra'),
                 ('https://www.3cat.cat/3catinfo/per-que-ripoll-badalona-berga-manresa-o-solsona-han-votat-tan-diferent-el-28m-i-el-23j/noticia/3242688/', '3Cat, Per què Ripoll, Badalona, Berga, Manresa o Solsona han votat tan diferent el 28M i el 23J (24-7-2023)')],
        enlaces=[],
        lugar='Badalona',
        foto=dict(src='img/actualidad/fotos/albiol-badalona-pp-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Xavier García Albiol, con el paseo marítimo y el plano de Badalona: un collage.'),
    ),
    dict(
        slug='palencia-psoe-lista-29n', fecha='2026-10-20',
        titulo='Dimite la lista del PSOE en Palencia tras imponer Ferraz a Martínez Seijo: en 2023 al partido le faltaron 7.097 votos para un segundo diputado', serie='29n',
        descripcion='El PSOE solo ha sacado dos de los tres diputados de Palencia en 1982 y 1986. En abril de 2019 fue el más votado y se quedó a 478 votos del segundo escaño.',
        compara='El voto al PSOE y al PP en la circunscripción de Palencia en las generales de 2004 a 2023, los escaños de cada uno y los votos que le faltaron al PSOE para un segundo diputado.',
        limites='En 2011, 2015 y 2016 los votos que faltaron son una aproximación hecha con los cuatro primeros partidos. Los porcentajes de 2004 a 2016 no incluyen el voto en blanco en el voto válido porque no hay datos por mesa de esos años. No es una previsión: no dice si el cambio de candidata moverá votos.',
        calculo='Porcentajes sobre voto válido (votos a candidaturas más votos en blanco), salvo la participación, que es sobre el censo.',
        fuentes=[INTERIOR,
                 ('https://www.elespanol.com/castilla-y-leon/region/palencia/20261019/rebelion-psoe-palencia-ferraz-toda-lista-renuncia-imposicion-martinez-seijo/1003744426904_0.html', 'El Español, Rebelión en el PSOE de Palencia contra Ferraz (19-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-19/psoe-palencia-guerra-ferraz-candidato/', 'The Objective, El PSOE de Palencia, en guerra con Ferraz por el candidato (19-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/19/elecciones-generales-29-n-en-directo-ultima-hora-de-los-sondeos-la-ley-de-nietos-o-los-anuncios-sobre-pensiones/', 'Infobae, directo de las elecciones del 29N (19-10-2026)'),
                 ('https://www.vozpopuli.com/espana/elecciones-generales-2023/renuncia-lista-psoe-avila-no-ir-junto-no1-impuesto-ferraz-vinculado-tito-berni.html', 'Vozpópuli, Renuncia la lista del PSOE de Ávila (2023)'),
                 ('https://reis.cis.es/index.php/reis/article/view/94', 'C. Pamies, Selección diferencial de candidatos en estados multinivel, REIS 182 (2024)')],
        enlaces=[],
        lugar='Palencia',
        foto=dict(src='img/actualidad/fotos/palencia-psoe-lista-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='La catedral y el puente de Palencia, con una urna: un collage.'),
    ),
    dict(
        slug='canarias-unidad-pueblo-canario-29n', fecha='2026-10-17',
        titulo='Nueva Canarias, Podemos, IU y Sumar se unen en Canarias: con los votos de 2023, la suma habría pasado de uno a tres diputados', serie='29n',
        descripcion='Juntos le habrían quitado un escaño al PP en Las Palmas y otro al PSOE en Santa Cruz de Tenerife, este por unos 1.600 votos. Canarias es una de las dos comunidades donde el Frente Amplio y Podemos irán juntos el 29N.',
        compara='El reparto de escaños de 2023 en Las Palmas y Santa Cruz de Tenerife tal como fue y el que habría salido si los votos de Sumar y de Nueva Canarias-Bloque Canarista se hubieran sumado en una sola lista, con la regla D\'Hondt.',
        limites='Es una simulación aritmética, no una previsión: supone que todos los votantes de Sumar y de NC-BC en 2023 votarían la lista conjunta. En 2023 Sumar ya incluía a Podemos e IU. Drago Canarias se presenta por separado y no se puede separar qué parte del voto de Sumar en 2023 podría irse con ella. Se usan los votos por mesa de Interior con el voto exterior, que pueden diferir en unos pocos votos del escrutinio oficial.',
        actualizado='2026-10-20',
        correcciones='20-10-2026: la lista de fuentes decía «sin voto exterior (CERA)», pero los cálculos sí incluyen el voto exterior, como indican los gráficos y los límites. Se corrige la fuente. Las cifras no cambian.',
        fuentes=[INTERIOR_CERA,
                 ('https://rtvc.es/podemos-nueva-canarias-iu-sumar-juntos-29n-bajo-nombre-unidad-pueblo-canario-15-octubre-2026/', 'RTVC, Podemos, Nueva Canarias, IU y Sumar irán juntos al 29N (15-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/17/2730679/frente-amplio-podemos-consuman-fractura-llegar-acuerdo-global-para-coaliciones-29n.html', 'Última Hora (Europa Press y Efe), Frente Amplio y Podemos consuman su fractura (17-10-2026)'),
                 ('https://diariodeavisos.elespanol.com/2026/02/nueva-canarias-plan-rufian-dos-diputados-congreso-izquierdas/', 'Diario de Avisos (Efe), Nueva Canarias aspira a dos diputados (19-2-2026)'),
                 ('https://www.moncloa.com/2026/10/16/unidad-pueblo-canario-confluencia-canarias-3449401', 'Moncloa.com, Unidad del Pueblo Canario (16-10-2026)'),
                 ('https://www.canarias7.es/opinion/firmas/roman-rodriguez-sola-papeleta-20261004060000-nt.html', 'Román Rodríguez, Una sola papeleta, Canarias7 (4-10-2026)'),
                 ('https://ara.cat/es/articulo-pablo-simon-manipulacion-electoral_0_1481252043.html', 'Ara, entrevista a Pablo Simón')],
        enlaces=[],
        lugar='Canarias',
        foto=dict(src='img/actualidad/fotos/canarias-unidad-pueblo-canario-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Los 15 diputados de Canarias en 2023 y con los votos de Sumar y Nueva Canarias sumados en una sola lista.',
                  fuente='Ministerio del Interior, generales de 2023. Simulación D\'Hondt de mapaelectoral.es'),
    ),
    dict(
        slug='mapa-coaliciones-izquierda-29n', fecha='2026-10-20',
        titulo='Separados el 29N, como en 2015: con los votos de aquel año, una sola papeleta de Podemos e IU habría sacado 86 diputados, no 71', serie='29n',
        descripcion='El mapa de las coaliciones de la izquierda a la izquierda del PSOE en cada elección general desde 2015, con su hemiciclo. Cuando fueron juntos, en 2016, perdieron un millón de votos y se quedaron en los mismos 71 escaños.',
        compara='Las listas de la izquierda a la izquierda del PSOE (Podemos y sus confluencias, IU-Unidad Popular, Unidos y Unidas Podemos, Compromís, En Marea, Más País y Sumar) en cada provincia en las generales de 2015, 2016, abril y noviembre de 2019 y 2023, con sus votos y escaños, y el reparto D\'Hondt que habría salido sumando en cada provincia los votos de las listas que fueron por separado. Para el 29N, las coaliciones registradas por el Frente Amplio y Podemos.',
        limites='El reparto «sumando sus votos» es un cálculo, no una previsión ni lo que habría pasado: supone que todos los votantes de las listas separadas habrían votado la lista conjunta y que el resto de votos no cambia. 2016 muestra que no es así. Se cuentan dentro del espacio las confluencias con partidos territoriales (En Comú Podem, Compromís, En Marea) y, en noviembre de 2019, Més Compromís con Más País; no el BNG, la CUP ni EH Bildu. Para el 29N, las coaliciones salen de la prensa del 16 y 17 de octubre; las candidaturas se registran más tarde. No calculamos escaños para el 29N.',
        calculo='Votos por provincia de las cinco generales, con voto exterior, y reparto D\'Hondt con la barrera del 3% y los escaños de cada convocatoria (2015 y 2016: Madrid 36, Barcelona 31, Valencia 16; 2019: 37, 32 y 15; 2023: 37, 32 y 16). El cálculo con los votos reales reproduce los escaños oficiales de las cinco elecciones. Porcentajes sobre votos válidos; la participación, sobre el censo con residentes en el extranjero. Scripts: actualidad/src/coaliciones/.',
        fuentes=[INTERIOR_CERA,
                 ('https://www.lamarea.com/2015/12/21/garzon-se-desploma-pero-mantiene-con-vida-a-iu/', 'La Marea, Garzón se desploma pero mantiene con vida a IU (21-12-2015)'),
                 ('https://orain.eus/es/politica/2016/05/12/iglesias-garzon-logran-aval-su-militancia-coalicion/', 'Orain, Iglesias y Garzón logran el aval de su militancia para la coalición (12-5-2016)'),
                 ('https://www.publico.es/politica/suma-unidos-pierde-mas-millon.html', 'Público, la suma de Unidos Podemos pierde más de un millón de votos (26-6-2016)'),
                 ('https://theobjective.com/errejon-se-presenta-a-las-generales-para-que-no-haya-un-solo-voto-progresista-que-se-quede-en-casa/', 'The Objective, Errejón se presenta a las generales (25-9-2019)'),
                 ('https://www.periodicodeibiza.es/noticias/elecciones-23j/2023/06/10/1954315/sumar-yolanda-diaz-vamos-ganar-elecciones-generales.html', 'Periódico de Ibiza (agencias, vídeo de Europa Press), Yolanda Díaz: «Vamos a ganar las elecciones generales» (10-6-2023)'),
                 ('https://www.nuevatribuna.es/articulo/actualidad/union-division-frente-amplio-elecciones-podemos-sumar-politica/20221227165009206442.html', 'Antonio Antón, La unión y la división del frente amplio, Nueva Tribuna (27-12-2022)'),
                 ('https://www.publico.es/politica/frente-amplio-podemos-concurriran-separado-29-noviembre-salvo-canarias-pais-valencia.html', 'Público, Frente Amplio y Podemos concurrirán por separado salvo en Canarias y País Valencià (16-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/17/2730679/frente-amplio-podemos-consuman-fractura-llegar-acuerdo-global-para-coaliciones-29n.html', 'Última Hora (Europa Press y Efe), Frente Amplio y Podemos consuman su fractura (17-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/mapa-coaliciones-izquierda-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='El hemiciclo del Congreso partido en dos bloques morados, Podemos y Frente Amplio, con una papeleta rota en medio: un collage.'),
    ),
    dict(
        slug='frente-amplio-podemos-madrid-escanos-29n', fecha='2026-10-20',
        titulo='Delgado contra Montero en Madrid: con los votos de 2023, Podemos necesitaría uno de cada cinco votos de Sumar para sacar escaño', serie='29n',
        descripcion='Separados, el Frente Amplio y Podemos habrían sacado entre cinco y seis de los seis diputados que Sumar logró en Madrid en 2023. El escaño que se pierde iría al PSOE; el PP se queda en 16 en todos los casos.',
        compara='El reparto de los 37 escaños de Madrid en 2023 tal como fue y el que habría salido si los votos de Sumar se hubieran partido en dos listas, el Frente Amplio y Podemos, en todas las proporciones del 0% al 50%, con la regla D\'Hondt y la barrera del 3%. Se añade el precedente de noviembre de 2019, con Unidas Podemos y Más País por separado.',
        limites='Es una simulación aritmética, no una previsión: supone que los votantes de Sumar en 2023 votan a una de las dos listas y que el resto de partidos saca lo mismo. No hay un dato oficial de qué parte del voto de Sumar en 2023 era de Podemos, por eso se muestran todos los repartos. No recoge votantes que se vayan al PSOE o a la abstención. Se usan los votos por mesa de Interior con el voto exterior, que pueden diferir en unos pocos votos del escrutinio oficial.',
        fuentes=[INTERIOR_CERA,
                 ('https://www.telemadrid.es/noticias/madrid/Frente-Amplio-elige-a-Emilio-Delgado-como-cabeza-de-lista-por-Madrid-0-2934306575--20261013081543.html', 'Telemadrid (Europa Press), Frente Amplio elige a Emilio Delgado como cabeza de lista por Madrid (13-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/16/24136-personas-respaldan-en-primarias-que-irene-montero-sea-candidata-y-vaya-en-el-primer-puesto-por-madrid/', 'Infobae (Europa Press), 24.136 personas respaldan a Irene Montero en primarias (16-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/16/29n-delgado-reitera-la-generosidad-de-frente-amplio-con-montero-en-madrid-se-le-ofrece-el-puesto-2-y-3-en-la-lista/', 'Infobae (Europa Press), Delgado reitera la generosidad de Frente Amplio con Montero (16-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/15/emilio-delgado-ve-dificil-el-acuerdo-con-podemos-pero-mantiene-la-mano-tendida-para-integrarles-en-el-frente-amplio/', 'Infobae (Europa Press), Emilio Delgado ve difícil el acuerdo con Podemos (15-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/13/2727755/irene-montero-asegura-podemos-integrara-frente-amplio-sigue-moviendo-baza-primarias.html', 'Última Hora (Efe), Irene Montero asegura que Podemos no se integrará en Frente Amplio (13-10-2026)'),
                 ('https://x.com/EFEnoticias/status/2111229781916197346', 'Efe en X, cabezas de lista de Podemos y Frente Amplio en Madrid'),
                 ('https://www.laregion.es/espana/presentara-pais-choque-frente_1_20261019-4457477.html', 'La Región, Podemos se presentará en todo el país (19-10-2026)'),
                 ('https://dialnet.unirioja.es/descarga/articulo/8166654.pdf', 'Miguel Ángel Sevilla Duro, El sistema electoral del Congreso en las elecciones de 2019, Revista de Derecho Electoral (2021)'),
                 ('https://cordopolis.eldiario.es/cordoba-hoy/sociedad/politologo-demuestra-coalicion-e-iu-provoco-perdida-votos_1_12725560.html', 'Cordópolis, estudio de Víctor Gago Rivas sobre la coalición de Podemos e IU')],
        enlaces=[],
        lugar='Madrid',
        foto=dict(src='img/actualidad/fotos/frente-amplio-podemos-madrid-escanos-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Escaños del Frente Amplio y de Podemos en Madrid según cómo se repartan los votos que Sumar sacó en 2023.',
                  fuente='Ministerio del Interior, generales de 2023. Simulación D\'Hondt de mapaelectoral.es'),
    ),
    dict(
        slug='vox-pp-senado-pacto-29n', fecha='2026-10-21',
        titulo='PP y Vox negocian el Senado: con los votos de 2023, sumar a Vox le devolvería a la derecha 19 provincias frente a la lista de PSOE y Frente Amplio', serie='29n',
        descripcion='Por separado, el PP bajaría de 120 a 82 senadores elegidos; con los votos de Vox, la derecha volvería a 120. Sevilla, Valencia y Asturias seguirían siendo de la izquierda incluso juntos.',
        compara='Los votos por candidato del PP, del PP más Vox y de PSOE más Sumar en las elecciones al Senado de 2023, en las 39 provincias de cuatro senadores con lista conjunta de la izquierda (sin Navarra), y los senadores elegidos que saldrían en cada caso.',
        limites='Es una simulación aritmética, no una previsión. Usa los votos por candidato (suma de votos de los candidatos de cada partido dividida entre los que presentó) y hace una suma mecánica con transferencia perfecta: todos los votantes de Vox votarían al PP y todos los de PSOE y Sumar a la lista conjunta, sin cambios de participación. No dice cuántos senadores serían de Vox con la fórmula 2+1. No incluye las islas, Ceuta, Melilla, Cataluña, el País Vasco ni Navarra (que se dejan como en 2023), ni los senadores autonómicos. Las fórmulas de pacto proceden de la prensa y no están cerradas.',
        calculo='Votos por candidato: suma de los votos de los candidatos de cada partido en la provincia dividida entre el número de candidatos que presentó. Gana tres senadores la opción con más votos por candidato y uno la segunda.',
        fuentes=[('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907', 'Junta Electoral Central, resumen de los resultados de las elecciones al Congreso y al Senado de 23 de julio de 2023, BOE de 1-9-2023'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-19537', 'Junta Electoral Central, corrección de errores, BOE de 16-9-2023'),
                 ('https://www.elespanol.com/espana/politica/20261020/formulas-acuerdo-pp-vox-senado-retirada-listas-via-cesion-senadores-autonomicos/1003744427480_0.html', 'El Español, Las fórmulas para un acuerdo de PP y Vox en el Senado (20-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261019/derecha-conservaria-quintos-senado-vox-no-presenta-provincias-va-listas-pp/1003744425410_0.html', 'El Español, La derecha conservaría tres quintos del Senado si Vox no se presenta en 19 provincias (19-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261018/vox-dispuesto-demostrar-altura-miras-frente-popular-senado-lunes-decidira-pacta-pp/1003744424775_0.html', 'El Español, Vox, dispuesto a demostrar «altura de miras» en el Senado (18-10-2026)'),
                 ('https://www.elplural.com/politica/espana/vox-debate-si-retirarse-batalla-senado-algunas-provincias-facilitar-camino-pp_801756102', 'El Plural, Vox debate si retirarse de la batalla por el Senado en algunas provincias (19-10-2026)'),
                 ('https://revista.cortesgenerales.es/rcg/article/download/98/91', 'Fabio Pascua Mateo, Cuarenta años de elecciones a las Cortes Generales, Revista de las Cortes Generales 103 (2018)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/vox-pp-senado-pacto-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Senadores elegidos en 2023 y en dos simulaciones con los mismos votos: con PP y Vox por separado y con sus votos sumados, frente a la lista de PSOE y Frente Amplio.',
                  fuente='Junta Electoral Central, Senado de 2023 por candidato. Simulación de mapaelectoral.es'),
    ),
    dict(
        slug='trump-espana-invadida-inmigracion-29n', fecha='2026-10-21',
        titulo='Trump dice que España fue «invadida»: los vecinos nacidos fuera pasaron de 6,5 a 10 millones en siete años, y donde más crecieron Vox no sacó más votos', serie='29n',
        descripcion='La «invasión» de la que habla son las 72.000 personas que entraron en Ceuta en dos días de julio, casi todas de vuelta en Marruecos poco después, según Interior. El cambio de fondo está en el padrón: 572.678 residentes nacidos fuera más solo en 2025. En los municipios donde más subió su peso, Vox sacó el 12,3% en 2023; donde menos, el 13%.',
        compara='La población residente nacida en el extranjero en España de 2002 a 2026; las entradas en Ceuta de julio y las llegadas irregulares de 2026; y el voto al Congreso en noviembre de 2019 y julio de 2023 en los 8.131 municipios, agrupados en cinco quintos de población según cuánto subió el peso de los nacidos fuera entre 2021 y 2025. Y el voto en Ceuta.',
        limites='Son datos por municipio, no por persona: no dicen quién vota a quién ni por qué. «Nacidos fuera» incluye a españoles nacidos en el extranjero, y los extranjeros sin nacionalidad no votan en generales. La población es de 2021 y 2025 y el voto, de 2019 y 2023, así que los periodos no coinciden. Sin la provincia de Santa Cruz de Tenerife, donde Vox no tuvo lista al Congreso en 2023. Las entradas de Ceuta y el aumento de residentes no son la misma medida: unas son entradas, casi todas con vuelta, y el otro es un saldo neto. Ningún dato de población recoge aún lo ocurrido en Ceuta en julio. Sin voto exterior.',
        fuentes=[INTERIOR,
                 ('https://www.infobae.com/america/agencias/2026/10/20/trump-afirma-que-espana-fue-invadida-por-migrantes-y-no-esta-haciendo-nada-al-respecto/', 'EFE vía Infobae, Trump afirma que España fue «invadida» por migrantes y «no está haciendo nada al respecto» (20-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/16/se-reducen-las-llegadas-irregulares-de-migrantes-a-espana-sin-contar-la-entrada-a-ceuta/', 'EFE vía Infobae, Se reducen las llegadas irregulares de migrantes a España, sin contar la entrada a Ceuta (16-10-2026)'),
                 ('https://elfarodeceuta.es/marlaska-niega-cni-avisara-entrada-masiva-ceuta-confirma-72-000-personas-cruzaron-marruecos/', 'El Faro de Ceuta, Marlaska niega que el CNI avisara de la entrada masiva y confirma que 72.000 personas cruzaron desde Marruecos (4-8-2026)'),
                 ('https://www.eldebate.com/espana/20260917/cuales-son-verdaderas-cifras-invasion-ceuta-numero-entradas-salidas-alojados-calle_459327.html', 'El Debate, ¿Cuáles son las verdaderas cifras de la invasión de Ceuta? (17-9-2026)'),
                 ('https://www.ine.es/dyngs/Prensa/ECP2T26.htm', 'INE, Estadística Continua de Población. 1 de julio de 2026. Datos provisionales (6-8-2026)'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=56943', 'INE, Estadística Continua de Población: población residente por lugar de nacimiento, 2002-2026'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=69131', 'INE, Censo anual de población: población por municipio y país de nacimiento, 2021-2025 (una tabla por provincia)'),
                 ('https://www.realinstitutoelcano.org/comentarios/la-opinion-publica-espanyola-sobre-la-inmigracion-en-contexto/', 'Rut Bermejo Casado y Carmen González Enríquez, La opinión pública española sobre la inmigración en contexto, Real Instituto Elcano (3-10-2024)'),
                 ('https://www.deia.eus/actualidad/sociedad/2026/10/14/vivienda-principal-problema-55-7-cis-11647698.html', 'Deia, La vivienda es el principal problema para más de la mitad de la ciudadanía (barómetro del CIS de octubre, 14-10-2026)'),
                 ('https://www.leon24horas.net/politica/abascal-lanza-advertencia-ponferrada-que-pasa-francia-puede-pasar-espana/20261020221218212080.html', 'León 24 Horas, Abascal en Ponferrada (20-10-2026)'),
                 ('https://www.eldiario.es/piedrasdepapel/Vox-derecha-populista-escision-PP_6_850474947.html', 'Héctor Meleiro, Vox: nueva derecha populista o escisión radical del PP, Piedras de Papel, elDiario.es (26-12-2018)'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/trump-espana-invadida-inmigracion-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Donald Trump, una maleta y una cabina de votación.'),
    ),
    dict(
        slug='pensiones-revalorizacion-29n', fecha='2026-10-22',
        titulo='Feijóo y Saiz se pelean por la hucha de las pensiones: donde más pesan en la renta, PP y PSOE se llevaron el 72,8% del voto, casi diez puntos más que donde menos', serie='29n',
        descripcion='En las secciones donde las pensiones son un tercio de la renta, el bipartidismo resiste y Vox saca su peor dato. Pero no votan en bloque: en las más pobres gana el PSOE por 6,6 puntos y en las más ricas, el PP por 10,2.',
        compara='El peso de las pensiones en la renta bruta de cada sección censal en 2023, según el atlas de renta del INE, y el voto al Congreso en julio de 2023, con las secciones agrupadas en cinco grupos con el mismo número de votantes. El grupo donde más pesan, partido en tres según su renta. Y el voto de esos mismos grupos en 2011, 2015 y noviembre de 2019.',
        limites='Son datos por sección, no por persona: no dicen quién vota a quién ni por qué. El peso de las pensiones en la renta no es el porcentaje de pensionistas. Sin el País Vasco, donde el atlas no desglosa las fuentes de renta, ni la provincia de Santa Cruz de Tenerife, donde Vox no tuvo lista al Congreso en 2023. Las comparaciones con elecciones anteriores usan los grupos de 2023, y las secciones cambian de vecinos con el tiempo. Sin voto exterior.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ondavasca.com/feijoo-garantiza-que-las-pensiones-subiran-con-el-ipc-si-gobierna-son-innegociables/', 'Europa Press vía Ondavasca, Feijóo garantiza que las pensiones subirán con el IPC si gobierna: «Son innegociables» (15-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/20/elma-saiz-contraataca-a-feijoo-con-la-hucha-de-las-pensiones-de-vaciarse-hasta-5000-millones-con-el-pp-a-cerrar-2026-con-20000/', 'Infobae, Elma Saiz contraataca a Feijóo con la hucha de las pensiones (20-10-2026)'),
                 ('https://www.moncloa.com/2026/10/14/feijoo-pensiones-ipc-pp-psoe-3448623/', 'Moncloa.com, Feijóo, las pensiones y el IPC (14-10-2026)'),
                 ('https://documentos.fedea.net/pubs/fpp/2023/06/FPP2023-03.pdf', 'José Ignacio Conde-Ruiz y Vincenzo Galasso, Efectos económicos de la demografía política, Fedea Policy Paper 2023/03 (junio de 2023)'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pensiones-revalorizacion-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Dos jubilados en un banco, de espaldas, ante un edificio oficial con la bandera de España y dos pilas de monedas.'),
    ),
    dict(
        slug='vox-galicia-coruna-abascal-29n', fecha='2026-10-22',
        titulo='Abascal llama a Galicia «espina clavada»: Vox no llegó al 5% en seis de cada diez secciones gallegas en 2023, y en el resto de España, en una de cada nueve', serie='29n',
        descripcion='Las cargas en María Pita fueron contra la protesta; en las urnas, A Coruña le dio el 4,8%. En toda Galicia, Vox sacó lo mismo en los barrios ricos que en los pobres, en las ciudades que en las aldeas: un mapa sin manchas.',
        compara='El voto a Vox en las generales de noviembre de 2019 y julio de 2023 por comunidad, por sección censal y por municipio, en Galicia y en el resto de España, con las secciones agrupadas por renta y por tamaño de municipio. Y la ciudad de A Coruña, sección a sección.',
        limites='Son datos por sección, no por persona: no dicen quién vota a quién ni por qué. Sin voto exterior. «Resto de España» no incluye la provincia de Santa Cruz de Tenerife, donde Vox no tuvo lista al Congreso en 2023. Las explicaciones de los expertos citados son suyas: los datos casan con ellas, pero no las prueban.',
        fuentes=[INTERIOR, INE,
                 ('https://www.infobae.com/espana/2026/10/21/la-protesta-contra-el-acto-de-santiago-abascal-en-a-coruna-deriva-en-cargas-policiales-a-los-manifestantes-y-momentos-de-tension/', 'Infobae, La protesta contra el acto de Santiago Abascal en A Coruña deriva en cargas policiales (21-10-2026)'),
                 ('https://www.publico.es/politica/anzuelo-ultra-vox-cala-galicia.html', 'Lois Pérez (Luzes) en Público, El anzuelo ultra: por qué Vox no cala en Galicia (10-10-2026)'),
                 ('https://www.eldebate.com/espana/galicia/20240114/vox-lanza-precampana-gallega-entrar-unico-parlamento-no-tiene-representacion_166757.html', 'El Debate, Vox lanza su precampaña gallega para entrar en el único parlamento en el que no tiene representación (14-1-2024)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_al_Parlamento_de_Galicia_de_2024', 'Elecciones al Parlamento de Galicia de 2024, resultados'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)')],
        enlaces=[],
        lugar='Galicia',
        foto=dict(src='img/actualidad/fotos/vox-galicia-coruna-abascal-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Santiago Abascal, cabizbajo, ante la Torre de Hércules de A Coruña.'),
    ),
    dict(
        slug='funcionarios-pagas-extra-29n', fecha='2026-10-22',
        titulo='El 29N deja en el aire la subida de tres millones de empleados públicos: en Teruel o Soria hay el doble por habitante que en Barcelona, y donde más pesan, Sumar sacó un tercio menos', serie='29n',
        descripcion='El Gobierno promete el 4,5% en enero, pero no dice si lo aprobará antes de las elecciones. En las provincias con más empleo público, sobre todo del interior, Sumar sacó el 9,7% en 2023; donde menos, el 14,3%. Del PP, la diferencia casi desaparece sin Cataluña.',
        compara='Los empleados públicos por cada 100 habitantes en cada provincia, según el registro de enero de 2026, y el voto al Congreso en julio de 2023, con las provincias agrupadas en tres grupos con la misma población. También sin Cataluña, el País Vasco ni Navarra.',
        limites='Son datos por provincia, no por persona: no dicen a quién votan los empleados públicos. Los empleados se cuentan en la provincia donde trabajan, no donde viven ni donde votan, y la estadística de la administración local puede ser incompleta. La población es la del padrón. Sin Ceuta y Melilla en los grupos, por el peso de la Administración del Estado, ni la provincia de Santa Cruz de Tenerife, donde Vox no tuvo lista al Congreso en 2023. Sin voto exterior.',
        fuentes=[INTERIOR,
                 ('https://digital.gob.es/content/dam/portal-mtdfp/funcion-publica/rcp/boletin/2026_01/revision-agosto-2026/EPSAP_Enero_2026%20.pdf', 'Ministerio para la Transformación Digital y de la Función Pública, Estadística del Personal al Servicio de las Administraciones Públicas, enero de 2026 (tabla 1.6)'),
                 ('https://www.infobae.com/espana/2026/10/21/el-29-n-reabre-la-incertidumbre-sobre-la-subida-salarial-de-los-funcionarios-y-la-recuperacion-de-las-pagas-extra-que-cambia-con-el-adelanto-electoral/', 'Infobae, El 29-N reabre la incertidumbre sobre la subida salarial de los funcionarios y la recuperación de las pagas extra (21-10-2026)'),
                 ('https://www.csif.es/es/articulo/galicia/general/98521', 'CSIF, valoración de las subidas salariales previstas en los presupuestos de la Xunta para 2027 (16-10-2026)'),
                 ('https://forbes.es/economia/813125/dos-de-cada-tres-espanoles-cree-que-el-empleo-publico-permite-mas-conciliacion-pero-dudan-de-las-oposiciones/', 'Forbes, barómetro del CIS de octubre de 2025 sobre empleo público (13-10-2025)'),
                 ('https://ws168.juntadeandalucia.es/revistaselectronicas/raap/article/download/1442/1390/2748', 'Reseña de Carles Ramió, El colapso de la Administración en España (Catarata, 2024), Revista Andaluza de Administración Pública'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/funcionarios-pagas-extra-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una empleada pública ante su ordenador, de espaldas, junto a pilas de expedientes y de monedas.'),
    ),
    dict(
        slug='ley-nietos-donde-estan-29n', fecha='2026-10-22', actualizado='2026-10-23 21:37',
        titulo='El Constitucional deja sin voto a los nietos: los españoles adultos de América Latina crecen casi cinco veces más rápido y uno de cada tres está inscrito en Madrid', serie='29n',
        descripcion='Desde 2023 hay 259.711 españoles más en América nacidos allí. México manda a Madrid el 58% de los suyos; Cuba, a Canarias la mitad; Uruguay, a Galicia. En Ourense, el 31% del censo ya vive fuera.',
        compara='Los españoles residentes en el extranjero nacidos en su país de residencia, por país, entre el 1 de enero de 2021 y el de 2026, y los de 16 años o más residentes en 19 países de América Latina por provincia de inscripción, entre 2019 y 2026. Con el censo electoral de residentes en el extranjero de las generales del 29N por provincia.',
        limites='El padrón de españoles en el extranjero cuenta residentes inscritos en los consulados a 1 de enero, no electores ni nacionalizados por la ley de nietos: su aumento incluye también nacimientos y nacionalidades por otras vías. Los adultos son los de 16 años o más, porque el INE agrupa así las edades por provincia. No hay datos públicos de cuántos de los 163.020 suspendidos hay en cada provincia ni de cómo votarían. Las explicaciones del reparto por provincias son hipótesis.',
        fuentes=[('https://theobjective.com/espana/tribunales/2026-10-23/supremo-bolanos-albares-afectados-ley-nietos/', 'The Objective, El Supremo da cinco días a Bolaños y Albares para remitir los afectados por la ley de nietos (23-10-2026)'),
                 ('https://www.elespanol.com/espana/tribunales/20261023/supremo-da-dias-albares-bolanos-entregar-lista-nietos-riesgo-multas-posible-delito/1003744431038_0.html', 'El Español, El Supremo da 5 días a Albares y Bolaños para entregar la lista de los 163.020 nietos (23-10-2026)'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=79676', 'INE, Padrón de Españoles Residentes en el Extranjero, población por país de residencia y lugar de nacimiento'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=79677', 'INE, Padrón de Españoles Residentes en el Extranjero, población por país de residencia y provincia de inscripción'),
                 ('https://www.ine.es/dyngs/Prensa/EG2026.htm', 'INE, Elecciones a Cortes Generales de 29 de noviembre de 2026, nota de prensa (9-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/21/el-tribunal-constitucional-rechaza-el-recurso-del-defensor-del-pueblo-para-devolver-el-voto-a-163020-nacionalizados-por-la-ley-de-nietos/', 'Infobae, El Constitucional rechaza el recurso del Defensor del Pueblo (21-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/10/21/el-constitucional-de-pumpido-inadmite-el-recurso-de-gabilondo-por-la-ley-de-nietos-y-mantiene-la-suspension-del-supremo/', 'El Independiente, El Constitucional inadmite el recurso de Gabilondo (21-10-2026)'),
                 ('https://maldita.es/prebunking/20261016/nacionalizacion-ley-nietos-derecho-voto/', 'Maldita.es, La nacionalización a través de la «Ley de Nietos» y su derecho a voto (16-10-2026)'),
                 ('https://www.elindependiente.com/espana/2026/07/16/ley-nietos-cera-voto-provincia-junta-electoral-central/', 'Europa Press en El Independiente, La Junta Electoral y la provincia de voto de la ley de nietos (16-7-2026)'),
                 ('https://www.elcorreogallego.es/galicia/2026/07/13/ley-nietos-dispara-diaspora-derecho-132384738.html', 'El Correo Gallego, La ley de nietos dispara la diáspora con derecho a voto (13-7-2026)'),
                 ('https://maldita.es/control-del-poder/20260630/cuando-feijoo-defendia-hijos-nietos-espanoles-extranjero-derecho-nacionalidad/', 'Maldita.es, Cuando Feijóo defendía que los hijos y nietos de españoles en el extranjero tenían derecho a la nacionalidad (30-6-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ley-nietos-donde-estan-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Aumento de los españoles de 16 años o más que viven en América Latina, por provincia de inscripción, entre el 1 de enero de 2023 y el de 2026.',
                  fuente='INE, Padrón de Españoles Residentes en el Extranjero'),
    ),
    dict(
        slug='voto-autonomos-secciones-29n', fecha='2026-10-22',
        titulo='En los barrios con más autónomos, el PP saca 13 puntos al PSOE', serie='29n',
        descripcion='En los barrios con más trabajadores por cuenta propia, el PP sacó en 2023 un 41% y el PSOE un 28%; donde menos, al revés. Pasa con la misma renta, en Sevilla y en los pueblos. En Cataluña ese voto va a Junts. Vox, en cambio, no se mueve.',
        compara='El porcentaje de ocupados por cuenta propia de cada una de las 34.257 secciones censales (Censo anual 2023, por lugar de residencia) con el voto de cada sección en las generales de julio de 2023, en cinco grupos con el mismo número de votantes; dentro de cada nivel de renta; en siete ciudades, en los municipios de menos de 10.000 habitantes, en Galicia, Cataluña y el País Vasco. Y el recuerdo de voto de asalariados y trabajadores por cuenta propia en la encuesta postelectoral del CIS.',
        limites='Son datos por sección, no por persona: no dicen cómo vota cada autónomo. El censo cuenta a los ocupados donde viven, no donde trabajan. Cuenta propia incluye empresarios con asalariados, cooperativistas y ayudas familiares, y no equivale al alta en el RETA. Solo se ha separado la renta; la edad, el tamaño del municipio o los estudios pueden explicar parte de la diferencia. Se excluye Santa Cruz de Tenerife, donde Vox no presentó lista en 2023. La encuesta del CIS tiene 828 trabajadores por cuenta propia que recuerdan su voto.',
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=70006', 'INE, Censo anual de población, ocupados por situación profesional y sección censal'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de distribución de renta de los hogares'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales del 23 de julio de 2023 por sección'),
                 ('https://www.cis.es/en/surveys/barometro-de-septiembre-2023.-postelectoral-elecciones-generales-2023', 'CIS, estudio 3420, Barómetro de septiembre de 2023, postelectoral de las generales'),
                 ('https://www.bolsamania.com/noticias/economia/economia--amor-ata-sobre-las-cuentas-del-estado-de-2026-si-no-hay-presupuestos-hay-que-convocar-elecciones--20608152.html', 'Europa Press en Bolsamanía, entrevista a Lorenzo Amor (10-8-2025)'),
                 ('https://www.infobae.com/espana/2025/10/13/el-gobierno-propone-nuevas-cuotas-de-autonomos-para-2026-desde-217-hasta-796-euros-al-mes/', 'Infobae, El Gobierno propone nuevas cuotas de autónomos para 2026 (13-10-2025)'),
                 ('https://www.eldiario.es/opinion/tribuna-abierta/vota-clase-trabajadora-espana_129_1401496.html', 'Alberto Garzón, ¿A quién vota la clase trabajadora en España?, eldiario.es (9-8-2019)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/voto-autonomos-secciones-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mujer con delantal hace cuentas con una calculadora y un libro junto a una urna, ante una persiana de comercio.'),
    ),
    dict(
        slug='escanos-en-el-filo-29n', fecha='2026-10-22',
        titulo='Seis escaños que se decidieron por menos de mil votantes', serie='29n',
        descripcion='Con los votos de 2023 y los escaños de 2026, el último escaño de Cantabria, Girona, Tarragona, Ceuta, Salamanca y Albacete habría cambiado de partido si menos de mil personas hubieran cambiado su voto. En Cantabria bastaban 101. Con menos de 5.000, hay 32 escaños en el filo.',
        compara='Para cada una de las 52 circunscripciones, el último escaño que se reparte y la candidatura que se queda a las puertas, con los votos definitivos de las generales de julio de 2023 (voto exterior incluido) y los escaños por provincia de 2026; y cuántos votantes tendrían que pasar de una a otra, cuántos votos nuevos necesitaría la aspirante y cuántos podría perder la ganadora para que el escaño cambiara de partido.',
        limites='Es aritmética sobre el resultado de 2023, no una previsión del 29 de noviembre. El número de votantes que cambian de papeleta es el mínimo en el mejor caso para la aspirante; los votantes no se mueven en bloque. Solo se mira el último escaño y la primera aspirante de cada provincia. Reparto D\'Hondt con barrera del 3% y desempate por más votos; las candidaturas agrupadas como «otros» no compiten.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados definitivos de las generales de julio de 2023 por provincia'),
                 ('https://www.articulo14.es/politica/el-boe-lo-hace-oficial-asi-es-el-decreto-que-convoca-las-elecciones-generales-del-29n-20261006.html', 'Artículo 14, El BOE lo hace oficial: así es el decreto que convoca las generales del 29N (6-10-2026)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Ley Orgánica 5/1985, del Régimen Electoral General, artículo 163'),
                 ('https://theobjective.com/espana/politica/2023-07-28/vox-diputado-cantabria-voto-cera/', 'Europa Press en The Objective, Vox mantiene su escaño en Cantabria tras el voto CERA (28-7-2023)'),
                 ('https://theobjective.com/espana/politica/2023-07-28/pp-escano-madrid-sanchez-puigdemont/', 'The Objective, El voto CERA da al PP un escaño más en Madrid (28-7-2023)'),
                 ('https://www.menorca.info/actualidad/elecciones-23j/2023/07/28/1985413/resultados-elecciones-generales-punto-quitar-psoe-escano-por-madrid.html', 'EFE en Menorca.info, El PP quita al PSOE un escaño por Madrid (28-7-2023)'),
                 ('https://maldita.es/malditobulo/20230927/directo-investidura-feijoo-datos-contexto', 'Maldita, investidura de Feijóo (27-9-2023)'),
                 ('https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso', 'Annick Laruelle, El reparto de los escaños en el Congreso, Campusa, UPV/EHU (24-5-2019)'),
                 ('https://www.elindependiente.com/espana/2026/10/14/abascal-15-provincias-clave-crecimiento-vox-desgaste-psoe-division-izquierda/', 'El Independiente, Las provincias clave de Abascal (14-10-2026)'),
                 ('https://www.eldebate.com/espana/20261020/mapa-provincias-donde-ley-nietos-puede-dar-escanos-psoe-elecciones-generales-cns_471397.html', 'El Debate, El mapa de las provincias donde la ley de nietos puede dar más escaños al PSOE (20-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/auge-vox-costa-pp-pone-en-juego-ultimos-escanos-en-provincias-pequenas/', 'Demócrata, El auge de Vox a costa del PP pone en juego últimos escaños en provincias pequeñas (8-10-2026)'),
                 ('https://orain.eus/es/politica/elecciones/elecciones-generales/2019/05/01/el-voto-alaveses-residentes-extranjero-confirma-escano-eh-bildu-/', 'EITB, El voto de los alaveses en el extranjero confirma el escaño de EH Bildu (1-5-2019)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/escanos-en-el-filo-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Votantes que tendrían que cambiar de papeleta para que el último escaño de cada provincia cambiara de partido, en las ocho provincias más ajustadas de las generales de 2023.',
                  fuente='Ministerio del Interior y Real Decreto 806/2026. Cálculo propio'),
    ),
    dict(
        slug='voto-jubilados-secciones-29n', fecha='2026-10-22',
        titulo='Vox nunca ha llegado al 12% en los barrios de jubilados', serie='29n',
        descripcion='En la quinta parte de las secciones con más pensionistas, Vox sacó el 9,5% en 2023 y no pasó del 11,6% ni en su mejor año; donde menos hay, llegó al 20,5%. El PP gana esos barrios en 40 de 51 provincias. El PSOE, en Sevilla, Huelva, Cáceres y Cataluña.',
        compara='El porcentaje de residentes de 16 años o más que cobran una pensión de incapacidad, jubilación o prejubilación en cada una de las 34.257 secciones censales (Censo anual 2023) con el voto de cada sección en las generales de 2015 a 2023, en cinco grupos con el mismo número de votantes; con la misma proporción de mayores de 65 años; por provincia; y el recuerdo de voto de jubilados y trabajadores en la encuesta postelectoral del CIS.',
        limites='Son datos por sección, no por persona: no dicen cómo vota cada pensionista. El censo cuenta a la gente donde vive. La categoría del INE es la de perceptores de pensión de incapacidad, jubilación o prejubilación y no menciona las de viudedad. Al separar la edad y la provincia, la diferencia del PP entre secciones con más y menos pensionistas se queda en torno a un punto. Las elecciones de 2015 a 2019 solo se comparan en secciones con el mismo código. Se excluye Santa Cruz de Tenerife, donde Vox no presentó lista en 2023. En la encuesta del CIS, el recuerdo de voto favorece al PSOE frente al resultado real.',
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=66594', 'INE, Censo anual de población, población de 16 y más años por relación con la actividad y sección censal'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2015 a 2023 por sección'),
                 ('https://www.cis.es/en/surveys/barometro-de-septiembre-2023.-postelectoral-elecciones-generales-2023', 'CIS, estudio 3420, Barómetro de septiembre de 2023, postelectoral de las generales'),
                 ('https://www.que.es/2026/10/19/recortes-pensiones-pp-vox-29n/', 'Qué!, Los recortes de pensiones que PP y Vox abren en campaña (19-10-2026)'),
                 ('https://www.eldiario.es/politica/pp-patina-pensiones-precampana-29n_1_13586089.html', 'elDiario.es, El PP patina con las pensiones en la precampaña del 29N (14-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/abascal-promete-pagar-pensiones-y-garantizar-vivienda-como-sea-y-refuerza-su-llamamiento-al-voto-presencial/', 'Demócrata, Abascal promete pagar pensiones y garantizar vivienda «como sea» (11-10-2026)'),
                 ('https://theobjective.com/espana/politica/2026-10-07/saiz-revalorizacion-pensiones-pp-vox/', 'Europa Press en The Objective, Saiz y la revalorización de las pensiones (7-10-2026)'),
                 ('https://www.articulo14.es/economia/el-voto-del-miedo-los-ingresos-de-casi-la-mitad-del-censo-depende-del-gobierno-20261013.html', 'Artículo 14, El voto del miedo (13-10-2026)'),
                 ('https://documentos.fedea.net/pubs/fpp/2023/06/FPP2023-03.pdf', 'José Ignacio Conde-Ruiz y Vincenzo Galasso, Efectos económicos de la demografía política, Fedea Policy Paper 2023/03 (junio de 2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/voto-jubilados-secciones-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Cartas, gafas y monedas sobre una mesa; un hombre mayor mira la ciudad desde su balcón.'),
    ),
    dict(
        slug='casas-vacias-segundas-residencias', fecha='2026-10-22',
        actualizado='2026-10-23 23:15',
        titulo='En 4.441 municipios hay más casas sin vecinos que con ellos', serie='vivienda',
        descripcion='En 4.441 de los 8.131 municipios, más de la mitad de las viviendas no son residencia habitual. Mapas de las casas vacías (Galicia) y de temporada (costa y sierras). Ávila (59,4%), Teruel y Soria encabezan el interior; Oropesa del Mar (85%) y Peníscola, la costa. El PP saca más donde hay más casas vacías, pero por edad y provincia. Los pueblos de segunda residencia votan cuatro puntos menos.',
        compara='El porcentaje de viviendas no principales de cada municipio (Censo 2021) y, en los municipios con datos de consumo eléctrico, el de viviendas vacías y de uso esporádico, con el voto y la participación de cada municipio en las generales de julio de 2023: en cinco grupos con el mismo número de votantes, en toda España y dentro de cada provincia; una regresión con provincia, edad media, renta y tamaño; y, por sección censal, la comparación dentro de cada municipio con renta, edad y población extranjera.',
        limites='Son datos por municipio y por sección, no por persona: los dueños de segundas residencias votan donde están empadronados. La vivienda vacía y la de uso esporádico se miden por el consumo eléctrico (umbral de 15 días de uso; 251-750 kWh para el uso esporádico), que puede clasificar mal casas con contador compartido o autoconsumo; esa separación solo existe para unos 3.100 municipios, en general de más de 1.000 habitantes. El censo es de enero de 2021 y el voto, de julio de 2023. La diferencia de participación es una asociación; sus explicaciones son hipótesis. Sin voto exterior.',
        fuentes=[('https://www.ine.es/jaxi/Tabla.htm?tpx=59525', 'INE, Censo de Población y Viviendas 2021, viviendas principales y no principales por municipio (tabla 59525)'),
                 ('https://www.ine.es/jaxi/Tabla.htm?tpx=59531', 'INE, Censo de Población y Viviendas 2021, viviendas según consumo eléctrico por municipio (tabla 59531)'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (viviendas principales y no principales)'),
                 ('https://ine.es/prensa/censo_2021_jun.pdf', 'INE, nota de prensa «Censos de Población y Viviendas 2021. Resultados sobre hogares y viviendas» (30-6-2023)'),
                 INTERIOR, INE,
                 ('https://valenciaplaza.com/ine-cifra-numero-viviendas-vacias-mas-de-3-8-millones', 'Europa Press en Valencia Plaza, «El INE cifra el número de viviendas vacías en más de 3,8 millones» (30-6-2023)'),
                 ('https://ddd.uab.cat/record/175915', 'Julián López Colás y Juan Antonio Módenes, «Vivienda secundaria y residencia múltiple en España: una aproximación sociodemográfica», Scripta Nova, VIII-178 (2004)'),
                 ('https://www.bde.es/f/webbe/SES/Secciones/Publicaciones/PublicacionesAnuales/InformesAnuales/23/Fich/InfAnual_2023_Cap4.pdf', 'Banco de España, Informe Anual 2023, capítulo 4 (abril de 2024)'),
                 ('https://www.bolsamania.com/noticias_print/empresas/economia--iu-asegura-que-hay-un-millon-de-casas-vacias-que-pueden-resolver-la-falta-de-vivienda-en-espana--21031678.html', 'Europa Press en Bolsamanía, «IU asegura que hay un millón de casas vacías…» (13-10-2025)'),
                 ('https://doi.org/10.2307/1960778', 'Squire, Wolfinger y Glass, «Residential Mobility and Voter Turnout», American Political Science Review, 1987')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/casas-vacias-segundas-residencias.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Porcentaje de viviendas que no son residencia habitual (vacías, secundarias o de uso esporádico) en cada municipio, Censo 2021.',
                  fuente='INE, Censo 2021. Cálculo propio'),
    ),
    dict(
        slug='vox-barrios-obreros-clase-29n', fecha='2026-10-22',
        titulo='Vox no gana en los barrios obreros: saca casi lo mismo donde viven peones que donde viven directivos, y el que sube es el PSOE', serie='29n',
        descripcion='En la quinta parte de las secciones con más peones, limpiadoras y repartidores, Vox sacó en 2023 el 14,2%; en la de directivos y profesionales, el 12,6%. El PSOE pasa del 23,7% al 38,6%. Con la misma renta, donde hay más empleos elementales Vox saca lo mismo o menos. La excepción: el campo de Murcia y Almería.',
        compara='El porcentaje de ocupados con una ocupación elemental (gran grupo 9 de la CNO: peones, limpieza, reparto, empleo doméstico) y de alta cualificación (grupos 1 a 3) en cada una de las 32.715 secciones censales con al menos cien ocupados (Censo anual 2023, por lugar de residencia) con el voto de cada sección en las generales de noviembre de 2019 y julio de 2023: en cinco grupos con el mismo número de votantes; dentro de cada nivel de renta; en Madrid ciudad y en Murcia y Almería; y con una regresión con efectos fijos de provincia, errores agrupados por municipio y controles de renta, edad media y nacidos fuera de España.',
        limites='Son datos por sección, no por persona: no dicen cómo vota cada trabajador, y los extranjeros que trabajan en el barrio no votan en las generales. El censo cuenta a los ocupados donde viven, no donde trabajan, y deja fuera a parados y jubilados. Los tres grupos de ocupación del INE son amplios. El reparto de ocupaciones es de 2023 y se usa también para 2019. Se excluye Santa Cruz de Tenerife, donde Vox no presentó lista en 2023. Las encuestas de 2025 y 2026 pueden reflejar cambios que los votos de 2023 no recogen.',
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=70004', 'INE, Censo anual de población, ocupados por grupo de ocupación y sección censal'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de distribución de renta de los hogares'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de noviembre de 2019 y julio de 2023 por sección'),
                 ('https://www.publico.es/politica/abascal-anuncia-formacion-sindicato-vinculado-vox.html', 'Europa Press, Abascal anuncia la formación de un sindicato vinculado a Vox (5-7-2020)'),
                 ('https://theobjective.com/espana/politica/2025-08-24/vox-obreros-parados-jovenes/', 'The Objective, Vox se erige en partido de los «desesperados»: Abascal atrae a obreros, parados y jóvenes (24-8-2025)'),
                 ('https://doi.org/10.3389/fpos.2025.1717586', 'Rosa Roig, Priscila Espinosa y José M. Pavía, Who votes for Vox? Socioeconomic profiles and electoral shifts in the region of Madrid, Frontiers in Political Science (2025)'),
                 ('https://www.eldiario.es/opinion/tribuna-abierta/vota-clase-trabajadora-espana_129_1401496.html', 'Alberto Garzón, ¿A quién vota la clase trabajadora en España?, eldiario.es (9-8-2019)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='oficios-y-voto-municipios-29n', fecha='2026-10-22',
        titulo='Donde abundan los despachos, el PP saca siete puntos más y el PSOE, cinco menos', serie='29n',
        descripcion='En los municipios con más ocupados en finanzas y despachos profesionales de cada provincia, el PP sacó en 2023 el 35,8% y el PSOE el 29%; donde menos, el 28,3% y el 34,2%. Donde más gente vive del comercio, Vox saca un tercio más. Donde se vive de la hostelería, se vota menos. El mapa de los oficios de 4.090 municipios.',
        compara='El porcentaje de ocupados de cada rama de actividad (21 secciones de la CNAE-2009) en los municipios de 500 habitantes o más (Censo anual 2023, por lugar de residencia) con el voto de cada municipio en las generales de julio de 2023: en cinco grupos con el mismo número de votantes, de menos a más peso de la rama frente a la media de su provincia; dentro de cada tercio de renta; por comunidad; y con una regresión dentro de cada provincia que descuenta renta, tamaño, edad media, nacidos fuera de España, estudios superiores y paro.',
        limites='Son datos por municipio, no por persona: no dicen cómo vota quien trabaja en cada rama. El censo cuenta a los ocupados donde viven, no donde trabajan, y solo da las ramas en los 4.144 municipios de 500 habitantes o más. Se excluye Santa Cruz de Tenerife, donde Vox no presentó lista en 2023. Las ramas de la CNAE mezclan empleo público y privado, y el comercio incluye el mayorista. Con todos los controles, las diferencias son de uno a dos puntos y medio. La renta es de 2022 y los estudios, el paro y el origen, del censo de 2021.',
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=69992', 'INE, Censo anual de población, ocupados por sexo y actividad, municipios de 500 habitantes o más'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de distribución de renta de los hogares'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales del 23 de julio de 2023 por municipio'),
                 ('https://confecomerc.es/wp-content/uploads/2023/07/CEC_ELECCIONESGENERALES_20231107.pdf', 'Confederación Española de Comercio, Propuestas del sector comercio para las elecciones generales de 2023'),
                 ('https://www.elsaltodiario.com/almeria/mar-de-plastico-desierto-institucional', 'María Usero, Un mar de plástico en un desierto institucional, El Salto (2018)'),
                 ('https://doi.org/10.3389/fpos.2025.1717586', 'Rosa Roig, Priscila Espinosa y José M. Pavía, Who votes for Vox? Socioeconomic profiles and electoral shifts in the region of Madrid, Frontiers in Political Science (2025)'),
                 ('https://www.eldiario.es/castilla-y-leon/politica/voto-vox-castilla-leon-hombres-jovenes-autonomos-clase-alta_1_9085508.html', 'elDiario.es, Quién votó a Vox en Castilla y León: hombres jóvenes, autónomos y de clase alta (18-6-2022)'),
                 ('https://torrijostoday.com/castilla-la-mancha/funez-pp-propone-bajadas-de-impuestos-menos-burocracia-mas-conciliacion-y-facilitar-el-relevo-generacional/', 'Europa Press en Torrijos Today, Fúnez (PP) propone bajadas de impuestos para los autónomos (22-10-2026)'),
                 ('https://www.cronista.com/espana/politica-es/feijoo-propone-un-plan-integral-de-autonomos-y-eximir-por-dos-anos-la-cuota-para-nuevos-emprendedores/', 'EFE en El Cronista, Feijóo propone un Plan Integral de Autónomos (27-10-2025)'),
                 ('https://elbierzo.eldiario.es/ponferrada/vox-confirma-pablo-calvo-cabeza-lista-vox-congreso-leon-mitin-abascal-ponferrada_1_13601490.html', 'elDiario.es El Bierzo, mitin de Abascal en Ponferrada (20-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/oficios-y-voto-municipios-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un obrero con casco y planos, una sanitaria que vota en una urna transparente y una tendera tras el mostrador.'),
    ),
    dict(
        slug='vivienda-preocupa-voto-sumar-29n', fecha='2026-10-22',
        titulo='Donde más preocupa la vivienda, más se votó a Sumar', serie='29n',
        descripcion='En Baleares, el País Vasco y Madrid más de la mitad de los entrevistados por el CIS cita la vivienda como problema; en Murcia, el 36%. Son las comunidades donde Sumar sacó más votos en 2023. Entre los votantes de Vox, solo uno de cada cuatro la nombra.',
        compara='El porcentaje de entrevistados que cita la vivienda entre los tres principales problemas de España en los nueve barómetros del CIS de diciembre de 2025 a octubre de 2026 (37.191 entrevistas, ponderadas), por mes, edad, recuerdo de voto de 2023 y comunidad autónoma; el voto real de 2023 en cada comunidad; la fidelidad de voto de quienes la citan y quienes no; y el voto de 2023 en las secciones censales ordenadas por el precio del alquiler (SERPAVI 2023).',
        limites='Es una encuesta: dice qué piensan los entrevistados, no cómo votará cada comunidad. Las muestras de las comunidades pequeñas son reducidas, y las de Ceuta y Melilla, mínimas. La correlación entre comunidades no prueba que la preocupación por la vivienda cause el voto a Sumar. El recuerdo de voto del CIS favorece al PSOE frente al resultado real. El precio del alquiler por sección solo existe donde hay suficientes contratos declarados; dentro de cada provincia y nivel de renta, el alquiler apenas separa el voto.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, barómetros de diciembre de 2025 a octubre de 2026 (estudios 3536, 3540, 3544, 3546, 3557, 3562, 3567, 3577 y 3582), microdatos'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2023 por sección'),
                 ('https://www.mivau.gob.es/vivienda/alquila-con-garantias/sistema-estatal-de-referencia-del-precio-del-alquiler-de-vivienda', 'Ministerio de Vivienda, Sistema Estatal de Referencia del Precio del Alquiler (SERPAVI), 2023'),
                 ('https://es.euronews.com/2026/10/10/sanchez-abre-la-campana-electoral-del-29n-en-su-ciudad-talisman-con-la-vivienda-como-eje-p', 'Euronews, Sánchez abre la campaña del 29N con la vivienda como eje (10-10-2026)'),
                 ('https://www.esdiario.com/nacional/261005/199512/feijoo-vivienda-ases-29n-sanchez-busca-rescatar-decretos-tumbados-su-manera.html', 'ESdiario, Feijóo y la vivienda (5-10-2026)'),
                 ('https://www.emol.com/noticias/Internacional/2026/10/05/1213240/pedro-sanchez-adelanta-elecciones.html', 'AP en Emol, Pedro Sánchez adelanta las elecciones (5-10-2026)'),
                 ('https://www.diariodeleon.es/nacional/261009/2099728/vivienda-pasa-factura-feijoo.html', 'Diario de León, encuesta DYM: la vivienda pasa factura (9-10-2026)'),
                 ('https://www.funcas.es/wp-content/uploads/2024/09/Estudios104_Torres_3.pdf', 'Raymond Torres, Funcas, estudio sobre jóvenes y vivienda (2024)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/vivienda-preocupa-voto-sumar-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un edificio de viviendas con una maleta en el portal y una urna con una papeleta.'),
    ),
    dict(
        slug='termometro-temas-inmigracion-29n', fecha='2026-10-22',
        titulo='La inmigración preocupa más, salvo a los votantes de Vox', serie='29n',
        descripcion='Desde septiembre la cita como problema el 20,4% de los entrevistados por el CIS, tres puntos más que en la primera mitad del año. Sube entre los votantes del PP, del 23,6% al 29%, y del PSOE, del 11% al 14,8%. Entre los de Vox baja, del 41,5% al 31,5%.',
        compara='Los problemas que citan los entrevistados en los nueve barómetros del CIS de diciembre de 2025 a octubre de 2026 (37.191 entrevistas, ponderadas), mes a mes; la intención de voto más simpatía de quienes citan cada problema; los problemas que cita cada electorado según su recuerdo de voto de 2023; la preocupación por la inmigración antes y después del verano; y por comunidad autónoma, frente al voto real a Vox en 2023.',
        limites='Es una encuesta: dice qué problemas nombran los entrevistados, no qué decidirá su voto. La intención de voto del CIS sobrestima al PSOE; por eso se comparan distancias con el conjunto y se ha repetido el cálculo ajustando el recuerdo de voto al resultado de 2023. Las muestras de los votantes de Vox y de las comunidades pequeñas son reducidas, y por eso se comparan periodos y no meses. Que un cambio coincida con un hecho no prueba que ese hecho lo causara.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, barómetros de diciembre de 2025 a octubre de 2026 (estudios 3536, 3540, 3544, 3546, 3557, 3562, 3567, 3577 y 3582), microdatos'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2023'),
                 ('https://www.infobae.com/espana/agencias/2026/10/20/abascal-urge-a-elegir-entre-prosperidad-libertad-y-orden-o-inmigracion-caos-y-subdesarrollo-en-las-elecciones/', 'Europa Press en Infobae, Abascal urge a elegir entre «prosperidad, libertad y orden» o «inmigración, caos y subdesarrollo» (20-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/20/feijoo-cree-que-sanchez-convoca-elecciones-para-que-no-le-investiguen-y-apunta-a-dinero-de-prostitucion-en-sus-primarias/', 'Europa Press en Infobae, entrevista de Feijóo en la Cadena COPE (20-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/feijoo-promete-una-ley-antiokupaciones-tras-el-29n-y-se-la-encarga-a-xavier-garcia-albiol/', 'Infobae, Feijóo promete una ley antiokupaciones tras el 29N (18-10-2026)'),
                 ('https://es.euronews.com/2026/10/10/sanchez-abre-la-campana-electoral-del-29n-en-su-ciudad-talisman-con-la-vivienda-como-eje-p', 'Euronews, Sánchez abre la campaña del 29N con la vivienda como eje (10-10-2026)'),
                 ('https://maldita.es/desinfo/20260520/preguntas-y-respuestas-imputacion-zapatero-plus-ultra/', 'Maldita.es, Preguntas y respuestas sobre la imputación de Zapatero en el caso Plus Ultra (20-5-2026)'),
                 ('https://colmenadedatos.com/encuesta-cis-el-psoe-se-desploma-junio-2026/', 'Colmena de Datos, análisis del barómetro del CIS de junio de 2026'),
                 ('https://eprints.gla.ac.uk/197637', 'Laura Morales, Sergi Pardos-Prado y Virginia Ros, Issue emergence and the dynamics of electoral competition around immigration in Spain, Acta Politica (2015)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/termometro-temas-inmigracion-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Porcentaje que cita la inmigración entre los tres principales problemas de España, según el voto en 2023, de diciembre a junio y en septiembre y octubre.',
                  fuente='CIS. Cálculo propio'),
    ),
    dict(
        slug='inmigracion-preocupa-voto-vox-29n', fecha='2026-10-22', actualizado='2026-10-26 10:08',
        titulo='Donde más preocupa la inmigración, más votó Vox, salvo en Cataluña', serie='29n',
        descripcion='Fuera de Cataluña, el País Vasco, Navarra y Galicia, en las provincias donde Vox pasó del 15% en 2023 el 20% de los entrevistados por el CIS cita la inmigración como problema; donde no llegó al 14%, el 15%. Hasta los votantes del PP la citan más allí: el 29%, frente al 21,5%. Tarragona y Girona, con poco voto a Vox, son las que más la citan.',
        compara='El porcentaje de entrevistados que cita la inmigración entre los tres principales problemas de España en los nueve barómetros del CIS de diciembre de 2025 a octubre de 2026 (37.191 entrevistas, ponderadas), por provincia, frente al voto real a Vox en las generales de 2023 y al porcentaje de extranjeros empadronados (INE, enero de 2025); por recuerdo de voto del entrevistado; un modelo con efectos fijos de comunidad autónoma y errores agrupados por provincia; un modelo logístico multinivel (entrevistados dentro de provincias dentro de comunidades); modelos espaciales de retardo y de error entre provincias vecinas; y pruebas de no linealidad (tramos, términos cuadráticos y regresión sobre la mediana).',
        calculo='Porcentaje de entrevistados que citan la inmigración entre los tres principales problemas de España, con los datos ponderados del CIS. Multinivel: regresión logística con interceptos aleatorios de provincia y comunidad (lme4), controlando el recuerdo de voto de 2023, la edad, el sexo, el tamaño de municipio y el barómetro; el efecto se da como cambio medio en puntos. Espaciales: modelos de retardo (SAR) y de error (SEM) por máxima verosimilitud (spreg), con matriz de las cinco provincias más cercanas, sobre la preocupación de cada provincia ajustada por la composición de sus entrevistados; índice de Moran con 9.999 permutaciones. Se comprobó también con cuatro y seis vecinas. No linealidad: regresiones por tramos con cortes en el 10%, 15% y 20% de extranjeros y en el 13%, 15% y 17% de voto a Vox, términos cuadráticos y regresión cuantílica (cuartiles y mediana). Margen de error al 95%.',
        correcciones='26-10-2026: se añaden un modelo multinivel, modelos espaciales y pruebas de no linealidad. El efecto del voto a Vox es menor que el de la primera versión: de +0,4 a +0,8 puntos por cada punto de Vox, no +1,2. Se matiza que el aumento dentro de cada electorado solo se distingue con claridad entre los votantes del PSOE. Santa Cruz de Tenerife, que faltaba también en el mapa y en la tabla, aparece ahora con sus datos (22,4%); sigue fuera del cruce con el voto porque Vox no se presentó allí en 2023.',
        limites='Es una encuesta repartida por provincias: las muestras de las provincias pequeñas son reducidas (68 entrevistas en Soria). El voto a Vox es el de 2023 y la preocupación, la de este año. Es una correlación: no prueba que la preocupación lleve al voto ni al revés. Santa Cruz de Tenerife queda fuera del cruce con el voto porque Vox no presentó lista allí en 2023. Al tener en cuenta el porcentaje de extranjeros, la relación se debilita. El modelo espacial trabaja con 39 o 51 provincias, pocas para detectar curvas: que no aparezca una saturación no prueba que no exista. El CIS no publica el municipio ni la sección del entrevistado, así que el modelo multinivel no puede bajar de la provincia.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, barómetros de diciembre de 2025 a octubre de 2026 (estudios 3536, 3540, 3544, 3546, 3557, 3562, 3567, 3577 y 3582), microdatos'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2023'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=56949', 'INE, Estadística Continua de Población, población por provincia y nacionalidad, 1 de enero de 2025'),
                 ('https://www.realinstitutoelcano.org/comentarios/la-opinion-publica-espanyola-sobre-la-inmigracion-en-contexto/', 'Rut Bermejo Casado y Carmen González Enríquez, La opinión pública española sobre la inmigración en contexto, Real Instituto Elcano (3-10-2024)'),
                 ('https://dx.doi.org/10.5209/poso.75974', 'Ismael Crespo Martínez y Alberto Mora Rodríguez, El auge de la extrema derecha en Europa: el caso de Vox en la Región de Murcia, Política y Sociedad 59(3) (2022)'),
                 ('https://democrata.es/elecciones-generales-espana/visita-abascal-aviles-desata-protestas-obliga-establecer-cordon-policial', 'Demócrata, Abascal defiende en Avilés la «remigración» y la prioridad nacional (21-10-2026)'),
                 ('https://www.elindependiente.com/sociedad/2025/07/14/detenidos-autor-agresion-torre-pacheco/amp/', 'El Independiente, Torre Pacheco (14-7-2025)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/inmigracion-preocupa-voto-vox-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Porcentaje que cita la inmigración entre los tres principales problemas de España, según el voto en 2023 del entrevistado y el voto a Vox en su provincia.',
                  fuente='CIS e Interior. Cálculo propio'),
    ),
    dict(
        slug='barrios-rentistas-pp-psoe-29n', fecha='2026-10-22',
        titulo='En los barrios de rentistas, el PP saca el 51% y el PSOE, el 21%', serie='29n',
        descripcion='En los códigos postales donde dividendos, intereses y alquileres son más del 10% de la renta declarada a Hacienda, el PP dobló al PSOE en 2023. Donde no llegan al 4%, ganó el PSOE. Vox sacó lo mismo en unos y otros. Del barrio de Salamanca a Entrevías, de Pedralbes a Torreblanca.',
        compara='El peso de las rentas del capital (capital mobiliario e inmuebles no afectos a actividades) en la renta bruta declarada en el IRPF de 2023, en 859 códigos postales de 66 grandes municipios y en 2.910 municipios de más de 1.000 habitantes, con el voto de las generales de julio de 2023: por código postal (sumando las secciones censales que caen en cada uno), en cinco grupos de menos a más peso del capital; por municipio, en diez tramos; dentro de cada ciudad y provincia, a igual renta media, con regresiones con efectos fijos de ciudad o provincia y errores estándar agrupados.',
        limites='Son datos de barrios y municipios, no de personas: no dicen cómo vota quien cobra rentas del capital. Hacienda no publica datos por sección censal; el código postal solo existe en las grandes ciudades y agrupa los códigos con menos de 900 declaraciones. Las secciones se asignan al código postal donde cae la mayor parte de su superficie, con contornos del CNIG de 2015 (en el 88% de las secciones, más del 80% del área cae en un solo código). Son cifras de declarantes, no de toda la población. No incluye el País Vasco ni Navarra, con Hacienda propia, ni los municipios de menos de 1.000 habitantes. Los inmuebles incluyen la renta imputada por segundas viviendas. Cataluña se analiza aparte por su sistema de partidos. En Madrid y Sevilla, a igual renta, el capital no añade diferencia.',
        calculo='Voto: porcentaje sobre votos válidos; participación, sobre el censo. Rentas del capital: capital mobiliario más rentas de bienes inmuebles no afectos a actividades económicas, sobre la renta bruta. Grupos: códigos postales con al menos 1.000 declaraciones fuera de Cataluña (662 de 54 ciudades) en cinco grupos de tamaño parecido; municipios fuera de Cataluña (2.441) en diez tramos. Regresiones por mínimos cuadrados con efectos fijos de ciudad (códigos postales) o de provincia (municipios) y errores estándar agrupados por ciudad o provincia; margen de error al 95%.',
        fuentes=[('https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfCodPostal/2023/home.html', 'Agencia Tributaria, Estadística de los declarantes del IRPF de los mayores municipios por código postal, 2023'),
                 ('https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2023/home.html', 'Agencia Tributaria, Estadística de los declarantes del IRPF por municipios, 2023'),
                 INTERIOR,
                 ('https://centrodedescargas.cnig.es/CentroDescargas/', 'CNIG, códigos postales (CartoCiudad), vía github.com/inigoflores/ds-codigos-postales'),
                 ('https://www.ine.es/ss/Satellite?L=es_ES&c=Page&cid=1259952026632&p=1259952026632&pagename=ProductosYServicios%2FPYSLayout', 'INE, contornos de las secciones censales 2023'),
                 ('http://piketty.pse.ens.fr/files/Piketty2018.pdf', 'Thomas Piketty, Brahmin Left vs Merchant Right, World Inequality Lab WP 2018/7'),
                 ('https://forbes.es/ultima-hora/991239/sumar-lleva-una-propuesta-al-congreso-para-subir-el-irpf-a-las-rentas-del-ahorro-a-partir-de-los-50-000-euros/', 'Europa Press en Forbes, Sumar lleva al Congreso subir el IRPF a las rentas del ahorro desde 50.000 euros (30-7-2026)'),
                 ('https://www.bolsamania.com/noticias_print/economia/economia--feijoo-organiza-hoy-un-acto-contra-el-infierno-fiscal-de-sanchez-el-mismo-dia-que-se-inicia-la-renta--22254324.html', 'Europa Press en Bolsamanía, Feijóo organiza un acto contra «el infierno fiscal» de Sánchez (8-4-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/barrios-rentistas-pp-psoe-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mano recoge unas llaves junto a un fajo de contratos, un edificio de viviendas y una urna transparente.'),
    ),
    dict(
        slug='frontera-renta-pp-junts-pnv-29n', fecha='2026-10-22',
        titulo='El PP ya gana a Junts en seis de cada diez barrios catalanes', serie='29n',
        descripcion='En 2011, CiU sacaba más votos que el PP en el 65% de las secciones de Cataluña; en 2023, Junts, en el 40%. La frontera de renta entre la derecha catalana y la estatal ha subido: el PP gana ahora en los barrios de renta baja y media y en los más ricos. En el País Vasco, el PNV solo pierde terreno arriba del todo, y en Canarias el PP gana en toda la escala.',
        compara='El voto a CiU o Junts, al PNV y a Coalición Canaria frente al PP en las generales de 2011 a 2023, por sección censal, en Cataluña, el País Vasco y Canarias, con las secciones ordenadas en diez grupos por renta neta media por unidad de consumo (INE, 2023); por municipio; y un modelo con efectos fijos de provincia (o de municipio), el porcentaje de vecinos nacidos en otra comunidad o en el extranjero y la edad media, con errores agrupados por municipio.',
        limites='Son datos agregados por sección: no siguen a los votantes ni dicen que los de CiU se pasaran al PP. La renta es la de 2023 para todas las elecciones, porque el INE solo la publica desde 2015 (en Álava, desde 2022). Junts no es el mismo partido que CiU, y en 2023 no se presentó Ciudadanos. Navarra queda fuera porque UPN fue con el PP en 2011 y 2019. Es una correlación, no una relación de causa.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=65033', 'INE, población por sección censal según lugar de nacimiento y residencia, 2023 (tabla 65033)'),
                 ('https://reis.cis.es/index.php/reis/article/view/1002', 'Clara Riba, Voto dual y abstención diferencial. Un estudio sobre el comportamiento electoral en Cataluña, REIS 91 (2000)'),
                 ('https://www.democrata.es/politica/nogueras-ensalza-el-papel-de-junts-para-plantar-cara-a-los-dos-bloques-espanoles/', 'Demócrata, Nogueras reivindica a Junts frente a los dos bloques (17-10-2026)'),
                 ('https://www.democrata.es/euskadi/garrido-pp-afirma-que-los-votantes-del-pnv-estan-preocupados-por-las-decisiones-y-la-trayectoria-del-partido/', 'Demócrata, con Europa Press, Garrido (PP) afirma que los votantes del PNV están preocupados (21-10-2026)'),
                 ('https://www.canarias7.es/politica/clavijo-psoe-pp-estrategia-madrid-sacrificar-canarias-20260927070937-nt.html', 'Canarias7, entrevista a Fernando Clavijo (27-9-2026)'),
                 ('https://es.ara.cat/politica/estrategia-feijoo-pescar-votos-psc-junts-vox-vez_1_5803420.html', 'Ara, La estrategia de Feijóo para pescar votos al PSC, Junts y Vox a la vez (20-7-2026)')],
        enlaces=[],
        lugar='Cataluña, País Vasco y Canarias',
        foto=dict(src='img/actualidad/fotos/frontera-renta-pp-junts-pnv-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Peso de CiU o Junts en el voto que suman con el PP, de las secciones más pobres a las más ricas de Cataluña, en 2011, 2019 y 2023.',
                  fuente='Interior e INE. Cálculo propio'),
    ),
    dict(
        slug='sanchez-revuelta-broncano-voto-joven-29n', fecha='2026-10-23',
        titulo='Sánchez en La Revuelta: entre los hombres jóvenes, Vox casi dobla al PSOE', serie='29n',
        descripcion='Sánchez fue a La Revuelta de Broncano a buscar el voto joven. En los nueve barómetros del CIS desde diciembre, Vox y el PSOE empatan entre los menores de 35, pero entre los hombres de esa edad Vox saca un 24,6% y el PSOE un 13,3%. La vivienda preocupa a la mitad de los jóvenes y la inmigración, más que a sus abuelos.',
        compara='La intención de voto más simpatía de los nueve barómetros del CIS de diciembre de 2025 a octubre de 2026 (37.191 entrevistas, ponderadas), por edad, sexo y comunidad; los problemas que los entrevistados citan como principales de España; y el voto de 2023 por sección censal según el peso de los mayores de 65, con efectos fijos de provincia o de municipio y errores agrupados por municipio.',
        limites='Las encuestas tienen margen de error, que se muestra en los gráficos; por comunidad, las muestras de menores de 35 son pequeñas y por debajo de 100 entrevistas no se pintan. La intención de voto no es voto: los jóvenes votan menos y deciden más tarde. Los datos por sección son agregados y no dicen cómo vota cada persona. Nada de esto mide el efecto de la entrevista en La Revuelta. Son correlaciones, no causas.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, barómetros de diciembre de 2025 a octubre de 2026 (estudios 3536, 3540, 3544, 3546, 3557, 3562, 3567, 3577 y 3582), microdatos'),
                 INTERIOR, INE,
                 ('https://www.rtve.es/noticias/20261023/pedro-sanchez-revuelta-frases-entrevista/17279243.shtml', 'RTVE, las frases de Pedro Sánchez en La Revuelta (23-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/22/sanchez-promete-que-si-sigue-gobernando-la-revuelta-seguira-en-tve-y-alerta-de-que-pp-y-vox-impondran-censura/', 'Europa Press, Sánchez promete que si sigue gobernando La Revuelta seguirá en TVE (22-10-2026)'),
                 ('https://www.publico.es/politica/partidos/sanchez-revuelta-acuerdan-madre-suyas-subo-pensiones.html', 'Público, Sánchez en La Revuelta (23-10-2026)'),
                 ('https://www.centroreinasofia.org/download/13929/', 'Kuric Kardelis, Gómez Miguel y Sanmartín Ortí, Barómetro Juventud y Género 2025, Centro Reina Sofía de Fad Juventud')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/sanchez-revuelta-broncano-voto-joven-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Pedro Sánchez, sentado en un sofá antiguo, frente a David Broncano en su mesa.'),
    ),
    dict(
        slug='teruel-cha-izquierda-escano-29n', fecha='2026-10-23',
        titulo='CHA se retira en Teruel: la única vez que la izquierda tuvo votos para un escaño fue en 2015, y fue dividida', serie='29n',
        descripcion='Desde 1977, ninguna lista a la izquierda del PSOE ha ganado un diputado por Teruel. En 2015, Podemos e IU-CHA sumaron 15.689 votos por separado, más que los 14.112 con los que el PP ganó el tercer escaño. En 2023, aunque todos los votantes de Sumar hubieran votado al PSOE, le habrían faltado 235 votos.',
        compara='El reparto de los tres escaños de Teruel con la ley D\'Hondt en las generales de 2004 a 2023, con voto exterior, y de 1977 a 2000 por municipio; los votos de las listas a la izquierda del PSOE frente a los que costó el tercer escaño; y el voto a Sumar en 2023 en los 236 municipios de la provincia.',
        limites='Los votos de una elección no son los de la siguiente. Sumar votos de listas distintas supone que sus votantes habrían votado igual a una lista conjunta, y en 2016 no fue así. El cálculo de 2023 supone que todos los votantes de Sumar se pasan al PSOE y que nadie más cambia. Los datos de 1977 a 2000 son por municipio y no incluyen el voto exterior. El mapa no incluye el voto exterior.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 1977 a 2023 en la provincia de Teruel, por mesa y municipio, con voto exterior desde 2004 (vía pollspaindata)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/22/iu-asegura-que-el-29n-habra-papeletas-de-la-izquierda-transformadora-en-teruel/', 'EFE, IU asegura que el 29N habrá papeletas de la izquierda transformadora en Teruel (22-10-2026)'),
                 ('https://www.publico.es/politica/cha-frente-amplio-aragon-anuncia-presentara-congreso-teruel.html', 'Público, CHA-Frente Amplio Aragón anuncia que no se presentará al Congreso por Teruel (21-10-2026)'),
                 ('https://www.eldiario.es/aragon/politica/cha-frente-amplio-renuncian-presentarse-congreso-teruel-evitar-dispersion-voto_1_13604566.html', 'elDiario.es, CHA y el Frente Amplio renuncian a presentarse al Congreso por Teruel e IU Aragón se desmarca (21-10-2026)'),
                 ('https://arainfo.org/teruel-existe-29n-recuperar-voz-propia-congreso/', 'AraInfo, Teruel Existe irá al 29N (5-10-2026)'),
                 ('https://www.redalyc.org/pdf/997/99715164005.pdf', 'Jorge Urdánoz Ganuza, Umbrales de representación y proporcionalidad, REIS 121 (2008)'),
                 ('https://recyt.fecyt.es/index.php/recp/article/download/37589/21106', 'Penadés y Santiuste, La desigualdad en el sistema electoral español y el premio a la localización del voto, Revista Española de Ciencia Política 32 (2013)')],
        enlaces=[],
        lugar='Teruel',
        foto=dict(src='img/actualidad/fotos/teruel-cha-izquierda-escano-29n-ilustracion.jpg', ancho=1280, alto=720, ia=True,
                  pie='La torre mudéjar de San Martín, en Teruel, dos papeletas separadas por un desgarro y un escaño junto a una urna.'),
    ),
    dict(
        slug='salario-minimo-provincias-feijoo-29n', fecha='2026-10-23',
        titulo='Huelva, Almería y Jaén: más de la mitad de sus asalariados cobró en 2024 menos de un salario mínimo al año', serie='29n', figura=1,
        descripcion='Mientras Feijóo y Díaz discuten sobre el salario mínimo y el IRPF, los datos de Hacienda dicen que el 37% de los asalariados de España no llegó en 2024 a 15.876 euros en todo el año. En Huelva fue el 56%; en Madrid, el 30%. Las diez provincias con más sueldos bajos reparten 69 escaños el 29N.',
        compara='Los asalariados de cada provincia según lo que cobraron en todo 2024, en múltiplos del salario mínimo (Agencia Tributaria, modelo 190), frente al voto de las generales de 2023 y al reparto de escaños; con una comparación dentro de cada comunidad autónoma (efectos fijos de comunidad y errores agrupados por comunidad).',
        limites='Cobrar menos de un salario mínimo en el año no es cobrar el salario mínimo: incluye a quien trabajó solo unos meses o a tiempo parcial. Los datos son por provincia y no dicen cómo vota cada trabajador. Faltan el País Vasco y Navarra, con Hacienda foral. Los salarios son de 2024 y los votos, de 2023. La relación con el voto de Sumar se apoya en 48 provincias de 17 comunidades, varias con una sola provincia.',
        fuentes=[('https://www.boe.es/eli/es/o/2026/03/30/pjc297', 'Orden PJC/297/2026, normas de cotización a la Seguridad Social para 2026 (BOE)'),
                 ('https://www.sercomunicacion.com/aimar-bretos-entrevista-a-alberto-nunez-feijoo-en-hoy-por-hoy/', 'Cadena SER, Aimar Bretos entrevista a Alberto Núñez Feijóo en Hoy por Hoy (23-10-2026)'),
                 ('https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/mercado/2024/home.html', 'Agencia Tributaria, Mercado de trabajo y pensiones en las fuentes tributarias 2024 y 2023: asalariados por provincia y tramos de salario'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2023 por provincia, con voto exterior (vía pollspaindata)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/23/feijoo-precisa-que-su-objetivo-es-subir-tanto-el-salario-minimo-como-el-medio/', 'EFE, Feijóo precisa que su objetivo es subir tanto el salario mínimo como el medio (23-10-2026)'),
                 ('https://www.publico.es/politica/feijoo-equivoca-directo-dice-personas-cobran-salario-minimo-deben-pagar-irpf.html', 'Público, Feijóo se equivoca en directo sobre el IRPF del salario mínimo (23-10-2026)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-3815', 'Real Decreto 126/2026, por el que se fija el salario mínimo interprofesional para 2026'),
                 ('https://repositorio.bde.es/handle/123456789/16842', 'Barceló y otros, Los efectos del salario mínimo interprofesional en el empleo: nueva evidencia para España, Banco de España, Documento Ocasional 2113 (2021)'),
                 ('https://www.bolsamania.com/noticias/economia/economialaboral--el-crecimiento-del-empleo-disminuyo-45-puntos-por-la-subida-del-smi-de-2019-segun-fedea--19728150.html', 'Europa Press, El crecimiento del empleo disminuyó 4,5 puntos por la subida del SMI de 2019, según Fedea (19-5-2025)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/salario-minimo-provincias-feijoo-29n.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Porcentaje de asalariados de cada provincia que cobró en 2024 menos de un salario mínimo en todo el año.',
                  fuente='Agencia Tributaria. Cálculo propio'),
    ),
    dict(
        slug='ivan-redondo-12-millones-derecha-29n', fecha='2026-10-23', actualizado='2026-10-25 08:56',
        titulo='Los 12 millones de la derecha que cita Iván Redondo solo existieron una vez: en 2011', serie='29n', figura=0,
        descripcion='Desde entonces, PP, Vox, Ciudadanos y UPyD han sumado entre 10,45 y 11,33 millones de votos. La ecuación de Redondo, con Vox en el 20% y el PP en el 27-28%, exige un bloque más grande que el de 2023, y con los votos de entonces daría a la derecha 177 escaños: mayoría absoluta.',
        compara='Los votos del bloque de la derecha (PP, Vox, Ciudadanos, UPyD y UPN o Navarra Suma) en las generales de 2004 a 2023, con voto exterior; y una simulación mecánica de escaños con los votos de 2023 por provincia y el reparto de 2026 en varios escenarios de PP y Vox.',
        limites='La simulación mueve votos en la misma proporción en todas las provincias, algo que nunca ocurre, y no es una previsión. En Santa Cruz de Tenerife Vox no se presentó en 2023. Incluir a Ciudadanos y UPyD en el bloque es una elección; los nacionalistas quedan fuera. Los porcentajes son sobre los votos a candidaturas, sin el voto en blanco, y son unas décimas más altos que los oficiales. Las frases de Redondo se citan de su cuenta de X y de la prensa que las recogió. Los trasvases salen del recuerdo de voto del CIS: son lo que dicen los encuestados, con un margen de error de en torno a punto y medio, y el recuerdo de voto al PP y a Vox tiende a quedarse corto.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2004 a 2023 por mesa, con voto exterior (vía pollspaindata)'),
                 ('https://www.eldebate.com/espana/20261014/ivan-redondo-suma-discurso-remontada-psoe-sanchez-tiene-posibilidades-feijoo_469316.html', 'El Debate, Iván Redondo se suma al discurso de la remontada (14-10-2026)'),
                 ('https://www.elespanol.com/alicante/20261022/ivan-redondo-desembarca-alicante-teoria-remontada-psoe/1003744430892_0.html', 'El Español, Iván Redondo desembarca en Alicante con su teoría de la remontada del PSOE el 29-N (22-10-2026)'),
                 ('https://x.com/thewarroomblog', 'Iván Redondo, cuenta de X @thewarroomblog'),
                 ('https://doi.org/10.3389/fpos.2021.688130', 'Rama, Cordero y Zagórski, Three Is a Crowd? Podemos, Ciudadanos, and Vox: The End of Bipartisanship in Spain, Frontiers in Political Science 3 (2021)'),
                 ('https://recyt.fecyt.es/index.php/recp/article/download/37589/21106', 'Penadés y Santiuste, La desigualdad en el sistema electoral español y el premio a la localización del voto, Revista Española de Ciencia Política 32 (2013)'),
                 ('https://www.cis.es/documents/d/cis/es3420vpMT_a', 'CIS, estudio 3420, poselectoral de las generales de 2023, tabulación por recuerdo de voto'),
                 ('https://www.cis.es/documents/d/cis/es3269rei_a', 'CIS, estudio 3269, poselectoral de las generales de noviembre de 2019'),
                 ('https://www.cis.es/documents/d/cis/es3248rei_a', 'CIS, estudio 3248, poselectoral de las generales de abril de 2019'),
                 ('https://www.cis.es/documents/d/cis/es3145rei_a', 'CIS, estudio 3145, poselectoral de las generales de 2016'),
                 ('https://www.cis.es/documents/d/cis/es3126rei_a', 'CIS, estudio 3126, poselectoral de las generales de 2015'),
                 ('https://www.cis.es/documents/d/cis/es2920rei_a', 'CIS, estudio 2920, poselectoral de las generales de 2011'),
                 ('https://doi.org/10.5477/cis/reis.192.27-46', 'Alaminos y Alaminos-Fernández, Recuerdo de voto y distorsiones analíticas: el caso español tras las elecciones generales de 2023, REIS 192 (2025)'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ivan-redondo-12-millones-derecha-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Iván Redondo, junto a una lupa sobre tablas de resultados.'),
    ),
    dict(
        slug='feijoo-aborto-eutanasia-sanidad-publica-29n', fecha='2026-10-23',
        titulo='Feijóo y el aborto «en la pública»: 77% en Galicia, 0,5% en Madrid', serie='29n', figura=0,
        descripcion='Tres de cada cuatro abortos ya se hacen en hospitales públicos en la Galicia del PP; en Madrid, menos de uno de cada doscientos, y en Extremadura, ninguno. Con la eutanasia pasa lo mismo: en Baleares se pide casi siete veces más que en Murcia.',
        compara='El porcentaje de abortos hechos en centros públicos en cada comunidad de 2015 a 2024 y las solicitudes de eutanasia resueltas en 2024 por cada 100.000 habitantes (Ministerio de Sanidad), junto al gobierno autonómico de 2024 y el voto de las generales de 2023.',
        limites='Los porcentajes de aborto son los del informe de Sanidad de octubre de 2025, que pueden diferir unas décimas de las tablas por comunidad de residencia del informe IVE 2024. Las tasas de eutanasia cuentan solicitudes resueltas en 2024, no personas que murieron por eutanasia. Las correlaciones son entre 17 comunidades, sin Ceuta ni Melilla, y no permiten conclusiones causales ni dicen nada de cada votante. Las frases de Feijóo proceden de la Cadena SER y de Público.',
        fuentes=[('https://www.sanidad.gob.es/areas/promocionPrevencion/embarazo/docs/Informe_IVEs_Publico_Privado_2015_2024.pdf', 'Ministerio de Sanidad, Situación del aborto en la sanidad pública (octubre de 2025)'),
                 ('https://www.sanidad.gob.es/areas/promocionPrevencion/embarazo/docs/IVE_2024.pdf', 'Ministerio de Sanidad, Interrupción voluntaria del embarazo, datos 2024'),
                 ('https://www.sanidad.gob.es/areas/calidadAsistencial/eutanasia/docs/Informe_Anual_2024_Prestacion_de_Ayuda_para_Morir.pdf', 'Ministerio de Sanidad, Informe anual 2024 de la prestación de ayuda para morir'),
                 ('https://doi.org/10.1344/rbd2025.64.49218', 'Toro Flores, Análisis de la aplicación de la Ley de Eutanasia en España: primeros tres años (2021-2023), Revista de Bioética y Derecho 64 (2025)'),
                 ('https://www.sercomunicacion.com/aimar-bretos-entrevista-a-alberto-nunez-feijoo-en-hoy-por-hoy/', 'Cadena SER, Aimar Bretos entrevista a Alberto Núñez Feijóo en Hoy por Hoy (23-10-2026)'),
                 ('https://www.publico.es/tremending/despues-pensiones-ahora-feijoo-retrata-aborto-muerte-digna-ninguna-mujer-quede-escuchar-esto.html', 'Público, Feijóo se retrata con el aborto o la muerte digna (23-10-2026)'),
                 ('https://www.publico.es/politica/feijoo-deja-sola-ayuso-desafio-ley-aborto.html', 'Público, Feijóo deja sola a Ayuso en su desafío a la ley del aborto (9-10-2025)'),
                 ('https://www.eldiario.es/politica/constitucional-censura-sanidad-publica-envie-mujer-abortar-privada-comunidad-autonoma_1_10346676.html', 'elDiario.es, El Constitucional censura que la sanidad pública envíe a una mujer a abortar a la privada en otra comunidad (2023)'),
                 ('https://valenciaplaza.com/valenciaplaza/el-tribunal-constitucional-rechaza-el-recurso-del-pp-contra-la-ley-de-la-eutanasia', 'Valencia Plaza, El Tribunal Constitucional rechaza el recurso del PP contra la ley de la eutanasia (2023)'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2023')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/feijoo-aborto-eutanasia-sanidad-publica-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Alberto Núñez Feijóo, ante el micrófono de un estudio de radio frente a su entrevistador: un collage.'),
    ),
    dict(
        slug='pueblos-unanimes-empates-29n', fecha='2026-10-23',
        titulo='Mota del Cuervo, 1.243 a 1.243: los pueblos del empate y los del voto unánime', serie='29n', figura=1,
        descripcion='En 94 municipios los dos primeros partidos empataron en las generales de 2023; en tres de ellos, con más de mil votos. En otros cinco, un solo partido se llevó todos los votos, y en Orexa fueron 62 de 62 para EH Bildu.',
        compara='Los votos de cada partido en cada municipio en las generales de 2023, y la serie de empates y de votos unánimes en todas las generales desde 1977.',
        limites='Un empate es que los dos partidos más votados del municipio tengan exactamente los mismos votos; la unanimidad cuenta solo votos a candidaturas, sin blancos ni nulos. Los partidos se agrupan en familias comparables entre elecciones, lo que puede alterar algún empate antiguo, y por eso la serie histórica se limita a los empates entre PP y PSOE. La explicación del aumento de empates es una hipótesis.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales al Congreso de 1977 a 2023 por municipio'),
                 ('https://www.ultimahora.es/elecciones/23j/congreso/mota-del-cuervo.html', 'Última Hora, resultados del 23J en Mota del Cuervo'),
                 ('https://www.ultimahora.es/elecciones/23j/congreso/guadiana-del-caudillo.html', 'Última Hora, resultados del 23J en Guadiana'),
                 ('https://www.ultimahora.es/elecciones/23j/congreso/dona-mencia.html', 'Última Hora, resultados del 23J en Doña Mencía'),
                 ('https://www.eldiario.es/euskadi/orexa-fortin-guipuzcoano-eleccion-eleccion-pueblo-vota-bloque-eh-bildu_1_10404176.html', 'elDiario.es, Orexa, el fortín guipuzcoano (25-7-2023)'),
                 ('https://www.elespanol.com/reportajes/20260315/villamedianilla-tinieblas-jaramillo-pueblos-burgos-llamaron-vecinos-formar-mesas/1003744170262_0.html', 'El Español, los pueblos de Burgos que llamaron a vecinos de fuera para formar mesas (15-3-2026)'),
                 ('https://boe.es/boe/dias/2020/03/09/pdfs/BOE-A-2020-3329.pdf', 'BOE, cambio de denominación de Guadiana del Caudillo por Guadiana (9-3-2020)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Ley Orgánica 5/1985 del Régimen Electoral General, artículos 163 y 196')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pueblos-unanimes-empates-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un pueblo con su campanario y una lluvia de papeletas iguales: un collage.'),
    ),
    dict(
        slug='ganar-por-un-voto-29n', fecha='2026-10-23',
        titulo='Santa Cruz de Mudela, 874 a 873: los 185 pueblos que se ganaron por un voto', serie='29n', figura=0,
        descripcion='En las generales de 2023, en 185 municipios el partido más votado ganó por un solo voto. El récord de la democracia es de Almoradí, en 2019: el PP le sacó un voto a Vox con más de nueve mil votantes.',
        compara='Los votos de cada partido en cada municipio en las generales de 2023, y los municipios ganados por un voto en todas las generales desde 1977.',
        limites='Ganar por un voto es que el partido más votado del municipio saque exactamente un voto más que el segundo, con el escrutinio definitivo del Ministerio del Interior; los recuentos provisionales publicados la noche electoral pueden diferir en algún voto. Los partidos se agrupan en familias comparables entre elecciones, lo que puede alterar algún caso antiguo. La explicación del aumento es una hipótesis.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales al Congreso de 1977 a 2023 por municipio'),
                 ('https://www.ultimahora.es/elecciones/23j/congreso/santa-cruz-de-mudela.html', 'Última Hora, resultados del 23J en Santa Cruz de Mudela'),
                 ('https://www.naciodigital.cat/eleccionscongres10N2019/municipi/03015', 'Nació Digital, resultados del 10N de 2019 en Almoradí'),
                 ('https://www.vozpopuli.com/espana/pueblo-alcalde-cara-cruz.html', 'Vozpópuli, el pueblo que eligió alcalde a cara o cruz (6-6-2023)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Ley Orgánica 5/1985 del Régimen Electoral General, artículo 196')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/ganar-por-un-voto-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mano mete el último sobre en una urna transparente, con una lupa al lado: un collage.'),
    ),
    dict(
        slug='barcelona-madrid-clasico-del-voto-29n', fecha='2026-10-25',
        titulo='El otro Clásico: en los barrios de renta media, el PP saca el triple de votos en Madrid que en Barcelona', serie='29n',
        descripcion='Barcelona y Madrid, sección a sección, el día del Barça-Madrid. Con la misma renta, el PP sacó en 2023 el 38,1 % en Madrid y el 12,7 % en Barcelona; el voto socialista cae con la renta al mismo ritmo en las dos. En 16 generales desde 1977, el PP nunca ha ganado en Barcelona y Madrid siempre ha votado más. Los barrios del Camp Nou y del Bernabéu.',
        compara='El voto al PP, al PSC/PSOE, a Vox y a Junts en las secciones censales de Barcelona y de Madrid agrupadas por tramos de renta comunes, en las generales de julio de 2023; una regresión con efecto fijo de ciudad; el partido más votado y la participación en cada ciudad en las 16 generales desde 1977; los barrios de los dos estadios, y los cambios de ganador por sección entre noviembre de 2019 y julio de 2023.',
        limites='Son datos de lugares, no de personas: que un barrio rico vote más al PP no quiere decir que cada vecino con más renta lo haga, y nada aquí habla del voto de los aficionados de cada equipo. La renta es la del INE de 2023 por unidad de consumo, topada en 58.752 euros. Las secciones no incluyen el voto exterior y antes de 2004 la serie es por municipio. La explicación de los dos ejes es una hipótesis compatible con los datos, no demostrada. Los barrios salen de OpenStreetMap, no de los límites oficiales de cada ayuntamiento.',
        calculo='Porcentajes sobre votos a candidaturas, ponderados por votantes de cada sección; participación sobre el censo. Regresión por mínimos cuadrados ponderados por censo del voto de cada sección sobre el logaritmo de su renta, con pendiente distinta para cada ciudad y efecto fijo de ciudad, errores agrupados por barrio (73 en Barcelona, 131 en Madrid); se informa el efecto de doblar la renta. Script: actualidad/src/resumenes/clasico.py.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, generales de 1977 a 2023 por municipio y por mesa, vía Infoelectoral y pollspaindata'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares 2023, renta por sección censal'),
                 ('https://www.fcbarcelona.es/es/noticias/4570226/el-horario-del-clasico-de-liga-en-el-spotify-camp-nou-confirmado', 'FC Barcelona, El horario del Clásico de Liga en el Spotify Camp Nou, confirmado'),
                 ('https://guia.barcelona.cat/en/detall/spotify-camp-nou_95152103742.html', 'Ajuntament de Barcelona, guía de la ciudad: Spotify Camp Nou'),
                 ('https://www.timeout.es/madrid/es/que-hacer/descubre-hispanoamerica-el-barrio-del-buen-vivir', 'Time Out Madrid, Hispanoamérica, el barrio del buen vivir'),
                 ('https://www.fcbarcelona.es/es/ficha/778212/manuel-vazquez-montalban-barca-cultura-i-esport', 'FC Barcelona, Manuel Vázquez Montalbán. Barça, cultura i esport (Editorial Base, 2019)'),
                 ('https://www.ultimahora.es/noticias/comunidades/2023/02/24/1888457/ayuso-defiende-madrid-eleva-muros-derriba-aniversario-del-estatuto-espana-dentro-otra.html', 'Europa Press, Ayuso: Madrid, «una España dentro de otra» (24-2-2023)'),
                 ('https://maldita.es/malditodato/20191115/vox-obtiene-peores-resultados-en-los-lugares-con-rentas-intermedias-y-logra-los-mejores-en-las-zonas-mas-pobres-y-en-las-mas-ricas/', 'Maldita.es, Vox obtiene peores resultados en los lugares con rentas intermedias (15-11-2019)'),
                 ('https://es.ara.cat/politica/elecciones-catalunya/barrios-pobres-ricos-vox-clase-media-alianca-catalana_1_5034199.html', 'Aleix Moldes, Barrios pobres y ricos para Vox y de clase media para Aliança Catalana, Ara (20-5-2024)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (UPF) sobre segregación y voto'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742', 'BOE, Real Decreto 806/2026 de convocatoria de las elecciones generales'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap, límites de barrios de Barcelona y Madrid')],
        enlaces=[],
        lugar='Barcelona y Madrid',
        foto=dict(src='img/actualidad/fotos/barcelona-madrid-clasico-del-voto-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una avenida arbolada de Barcelona partida en dos, con el cielo azul a un lado y rojo al otro: un collage.'),
    ),
    dict(
        slug='asi-queda-el-mapa-29n', fecha='2026-10-24',
        titulo='Así queda el mapa electoral de España antes del 29N: el PP ganó en 40 provincias y el PSOE, en 10', serie='29n',
        descripcion='Resumen del mapa de partida del 29N: en 2023 el PP fue el más votado en 40 de las 52 circunscripciones y en 18.407 secciones censales; el PSOE, en 10 y en 16.073. En 2019 el PSOE ganaba en 19.107 secciones. La renta, los municipios que votan igual desde 1977 y lo que dicen hoy las encuestas.',
        compara='El partido más votado en cada provincia en las generales de julio de 2023 (con voto exterior) y en cada sección censal en noviembre de 2019 y julio de 2023 (sin él); el voto al PP y al PSOE y la participación por deciles de renta de la sección; y las cifras de piezas anteriores sobre municipios fieles, ciudades y encuestas.',
        limites='Es un resumen del resultado de 2023, no una previsión del 29 de noviembre. Las secciones no incluyen el voto exterior y sus límites cambian entre elecciones; se cuentan las que tienen resultados en cada una. Familias de partidos del mapa de la portada: Sumar incluye en 2019 a Unidas Podemos y sus confluencias; en Navarra, UPN se cuenta aparte del PP en las provincias. Los datos por sección describen lugares, no personas. Las cifras de encuestas y del modelo son las del 23 de octubre de 2026 y cambian cada día.',
        calculo='Partido más votado por provincia con los votos oficiales y el voto exterior (el mismo cálculo reproduce los 350 escaños de 2023); por sección, con los resultados por mesa sumados. Porcentajes sobre votos a candidaturas, salvo la participación, que es sobre el censo. Script: actualidad/src/resumenes/mapa.py.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de julio de 2023 por mesa, con voto exterior (CERA), vía pollspaindata'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares 2023, renta por sección censal'),
                 ('https://es.euronews.com/2026/10/10/sanchez-abre-la-campana-electoral-del-29n-en-su-ciudad-talisman-con-la-vivienda-como-eje-p', 'Euronews, Sánchez abre la campaña del 29N en su ciudad talismán (10-10-2026)'),
                 ('https://www.diariodeleon.es/nacional/261011/2099933/sanchez-talisman-dos-hermanas-maricarmen_amp.html', 'Diario de León, Sánchez, el talismán de Dos Hermanas y Maricarmen (11-10-2026)'),
                 ('https://www.la7tv.es/articulo/politica/feijoo-sanchez-abren-precampana-29n-promesas-cambio-llamamientos-movilizacion/20261010140623074323.html', 'La 7, Feijóo y Sánchez abren la precampaña del 29N (10-10-2026)'),
                 ('https://elpais.com/espana/elecciones-generales/2023-07-24/el-mapa-con-los-resultados-de-las-elecciones-generales-del-23-j-calle-a-calle.html', 'Borja Andrino, Luis Sevillano y Kiko Llaneras, El mapa del 23J calle a calle, El País (24-7-2023)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742', 'BOE, Real Decreto 806/2026 de convocatoria de las elecciones generales'),
                 ('https://www.infobae.com/espana/2026/10/23/elecciones-generales-en-espana-29-n-en-directo-ultima-hora-de-los-sondeos-los-debates-y-las-entrevistas-a-pedro-sanchez-y-feijoo/', 'Efe, Feijóo en València (23-10-2026)'),
                 ('https://mapaelectoral.es/encuestas/', 'Mapa Electoral, encuestas de las generales y modelo por provincia (23-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/asi-queda-el-mapa-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna transparente llena de sobres sobre el contorno de España, entre una ciudad y un pueblo con campanario: un collage.'),
    ),
    dict(
        slug='coaliciones-quien-va-con-quien-29n', fecha='2026-10-24',
        titulo='Quién va con quién el 29N: Frente Amplio y Podemos, separados en 47 provincias; en 2015, juntos habrían sacado 15 diputados más', serie='29n',
        descripcion='El mapa de las alianzas para el 29N: el Frente Amplio y Podemos solo comparten papeleta en Canarias y la Comunitat Valenciana; el PSOE y el Frente Amplio van juntos al Senado en 43 provincias, y PP y Vox negocian hasta el cierre de listas del 26 de octubre. Lo que valen esas alianzas con los votos de 2015 a 2023.',
        compara='Las coaliciones registradas para el Congreso y el Senado del 29N, con los escaños de Sumar en 2023 agrupados por la coalición de cada provincia; los escaños del espacio a la izquierda del PSOE en cada generales desde 2015, reales y sumando los votos de sus listas; y los senadores de 2023 con la lista conjunta de PSOE y Frente Amplio y con los votos de PP y Vox sumados.',
        limites='Los cálculos «sumando sus votos» son techos, no previsiones: suponen que ningún votante cambia de papeleta ni se abstiene cuando las listas se juntan o se separan, y 2016 muestra que no es así. Las simulaciones del Senado suman votos por candidato con transferencia perfecta. Las coaliciones salen de la prensa; las candidaturas se cierran el 26 de octubre y se publican en el BOE el 28. El estado de la negociación entre PP y Vox es el del 24 de octubre de 2026.',
        calculo='Reparto D\'Hondt con la barrera del 3 % y los escaños de cada convocatoria, con voto exterior; el cálculo con los votos reales reproduce los escaños oficiales. Senado: votos por candidato de cada partido (suma de sus candidatos dividida entre los que presentó). Script: actualidad/src/resumenes/coaliciones.py; cifras de actualidad/src/coaliciones/ y actualidad/src/senado/.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, generales de 2015 a 2023 por mesa con voto exterior (CERA), vía pollspaindata'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907', 'Junta Electoral Central, resultados del Congreso y el Senado de 2023, BOE de 1-9-2023'),
                 ('https://www.publico.es/politica/frente-amplio-podemos-concurriran-separado-29-noviembre-salvo-canarias-pais-valencia.html', 'Público, Frente Amplio y Podemos concurrirán por separado salvo en Canarias y País Valencià (16-10-2026)'),
                 ('https://www.ultimahora.es/noticias/elecciones-29n/2026/10/17/2730679/frente-amplio-podemos-consuman-fractura-llegar-acuerdo-global-para-coaliciones-29n.html', 'Europa Press y Efe, Frente Amplio y Podemos consuman su fractura (17-10-2026)'),
                 ('https://www.que.es/2026/10/16/unidad-izquierda-29n-sin-pacto/', 'Qué!, Rufián: «He fracasado y hemos fracasado» (16-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/22/iu-asegura-que-el-29n-habra-papeletas-de-la-izquierda-transformadora-en-teruel/', 'Efe, IU asegura que habrá papeletas de la izquierda en Teruel (22-10-2026)'),
                 ('https://www.lamarea.com/2015/12/21/garzon-se-desploma-pero-mantiene-con-vida-a-iu/', 'La Marea, Garzón se desploma pero mantiene con vida a IU (21-12-2015)'),
                 ('https://www.nuevatribuna.es/articulo/actualidad/union-division-frente-amplio-elecciones-podemos-sumar-politica/20221227165009206442.html', 'Antonio Antón, La unión y la división del frente amplio, Nueva Tribuna (27-12-2022)'),
                 ('https://cordopolis.eldiario.es/cordoba-hoy/sociedad/politologo-demuestra-coalicion-e-iu-provoco-perdida-votos_1_12725560.html', 'Cordópolis, Víctor Gago Rivas (USAL) sobre la coalición de Podemos e IU en 2016'),
                 ('https://revista.cortesgenerales.es/rcg/article/download/98/91', 'Fabio Pascua Mateo, Cuarenta años de elecciones a las Cortes Generales, Revista de las Cortes Generales 103 (2018)'),
                 ('https://www.elespanol.com/espana/politica/20261020/formulas-acuerdo-pp-vox-senado-retirada-listas-via-cesion-senadores-autonomicos/1003744427480_0.html', 'El Español, Las fórmulas para un acuerdo de PP y Vox en el Senado (20-10-2026)'),
                 ('https://www.moncloa.com/2026/10/22/pacto-pp-vox-senado-listas-3453557', 'Moncloa.com, El pacto PP-Vox para el Senado (22-10-2026)'),
                 ('https://www.esdiario.com/nacional/261023/201078/vox-pone-nueva-condicion-feijoo-pactar-senado-pp-retire-dos-provincias.html', 'ESdiario, Vox pone una nueva condición a Feijóo para pactar el Senado (23-10-2026)'),
                 ('https://rtvc.es/comienza-el-plazo-para-presentar-las-candidaturas-para-el-29n-21-octubre-2026/', 'RTVC, Comienza el plazo para presentar las candidaturas para el 29N (21-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/coaliciones-quien-va-con-quien-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Sobres electorales, dos de ellos sujetos con una pinza y otro aparte, ante el hemiciclo del Congreso: un collage.'),
    ),
    dict(
        slug='provincias-en-el-filo-29n', fecha='2026-10-24',
        titulo='Las provincias que deciden el 29N: 32 escaños se movían en 2023 con menos de 5.000 votantes, y el PP defiende 13', serie='29n',
        descripcion='Con los votos de 2023 y los escaños de 2026, el último escaño de 32 circunscripciones habría cambiado de partido con menos de 5.000 votantes; en Cantabria bastaban 101. El PP defiende 13 y el PSOE aspira a 17. Por qué casi todos están en provincias pequeñas y qué puede moverlos antes de votar.',
        compara='Para cada circunscripción, el último escaño que se reparte y la candidatura que se queda a las puertas, con los votos definitivos de 2023 (voto exterior incluido) y los escaños de 2026; cuántos votantes tendrían que pasar de una a otra; qué partido defiende y cuál aspira a cada uno; el precio del escaño y los votos sin escaño por provincia; y el modelo de encuestas por provincia del 23 de octubre.',
        limites='Es aritmética sobre el resultado de 2023, no una previsión. El número de votantes que cambian de papeleta es el mínimo en el mejor caso para la aspirante; los votantes no se mueven en bloque. Solo se mira el último escaño y la primera aspirante de cada provincia. El modelo de encuestas es una estimación con un error típico de unos cinco puntos para un partido del 30 % a cinco semanas, y cambia cada día.',
        calculo='Reparto D\'Hondt con barrera del 3 % y desempate por más votos, con los votos definitivos de 2023 y los escaños del Real Decreto 806/2026; las candidaturas agrupadas como «otros» no compiten. Script: actualidad/src/resumenes/filo.py, con los datos de la pieza «Seis escaños que se decidieron por menos de mil votantes».',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de julio de 2023 por mesa, con voto exterior (CERA), vía pollspaindata'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742', 'BOE, Real Decreto 806/2026 de convocatoria de las elecciones generales'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Ley Orgánica 5/1985, del Régimen Electoral General, artículo 163'),
                 ('https://theobjective.com/espana/politica/2023-07-28/vox-diputado-cantabria-voto-cera/', 'Europa Press, Vox mantiene su escaño en Cantabria tras el voto CERA (28-7-2023)'),
                 ('https://www.elindependiente.com/espana/2026/10/14/abascal-15-provincias-clave-crecimiento-vox-desgaste-psoe-division-izquierda/', 'El Independiente, Las provincias clave de Abascal (14-10-2026)'),
                 ('https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso', 'Annick Laruelle, El reparto de los escaños en el Congreso, Campusa, UPV/EHU (24-5-2019)'),
                 ('https://recyt.fecyt.es/index.php/recp/article/download/37589/21106', 'Alberto Penadés y Salvador Santiuste, La desigualdad del sistema electoral, Revista Española de Ciencia Política (2013)'),
                 ('https://www.democrata.es/politica/el-psoe-reclama-el-voto-util-en-provincias-pequenas-para-que-apoyos-a-la-izquierda-no-vayan-a-la-basura/', 'Europa Press, El PSOE reclama el voto útil en provincias pequeñas'),
                 ('https://mapaelectoral.es/encuestas/provincias.html', 'Mapa Electoral, encuesta por provincias según el modelo (23-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/provincias-en-el-filo-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un sillón vacío al borde de un acantilado de papel, entre una calle de ciudad y un pueblo de interior, con sobres y una lupa sobre una mesa: un collage.'),
    ),
    dict(
        slug='cinco-semanas-29n-la-semana-en-el-mapa', fecha='2026-10-24',
        titulo='Un voto en Santa Cruz de Mudela, 101 en Cantabria, 7.097 en Palencia: la semana en que el 29N se contó en márgenes', serie='29n', figura=0,
        descripcion='Crónica de la semana del 17 al 23 de octubre desde los mapas: Palencia, Badalona, Ceuta, Ferrol, La Revuelta, Teruel y el voto de los nietos. Los bloques apenas se mueven desde 2015; lo que decide son unos pocos cientos de votos en el sitio justo.',
        compara='Los márgenes de las generales y municipales de 2023 en los lugares de los que se habló durante la semana, con las cifras de las piezas de Actualidad publicadas entre el 17 y el 23 de octubre.',
        limites='Es una pieza de resumen: cada cifra procede de una pieza ya publicada, enlazada en el texto, donde se explica cómo se calcula. Los márgenes no son comparables entre sí (un voto en un municipio, votantes que cambian de papeleta en una provincia, cocientes D\'Hondt) y ninguno predice el resultado del 29N. La lectura conjunta del último apartado es una hipótesis.',
        calculo='Cada cifra, como se explica en su pieza de origen.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2015 a 2023 y de las municipales de 2023'),
                 ('https://www.ine.es/dyngs/Prensa/ECP2T26.htm', 'INE, Estadística Continua de Población'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares'),
                 ('https://www.cis.es/estudios/catalogo-estudios', 'CIS, barómetros de diciembre de 2025 a octubre de 2026'),
                 ('https://www.elespanol.com/castilla-y-leon/region/palencia/20261019/rebelion-psoe-palencia-ferraz-toda-lista-renuncia-imposicion-martinez-seijo/1003744426904_0.html', 'El Español, la lista del PSOE de Palencia renuncia (19-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/19/albiol-reclama-controlar-la-inmigracion-irregular-si-no-acabaremos-como-francia/', 'Europa Press, Albiol y la inmigración (19-10-2026)'),
                 ('https://www.infobae.com/america/agencias/2026/10/20/trump-afirma-que-espana-fue-invadida-por-migrantes-y-no-esta-haciendo-nada-al-respecto/', 'EFE, Trump dice que España fue «invadida» (20-10-2026)'),
                 ('https://elfarodeceuta.es/marlaska-niega-cni-avisara-entrada-masiva-ceuta-confirma-72-000-personas-cruzaron-marruecos/', 'El Faro de Ceuta, Marlaska y las 72.000 entradas'),
                 ('https://www.ondavasca.com/feijoo-garantiza-que-las-pensiones-subiran-con-el-ipc-si-gobierna-son-innegociables/', 'Europa Press, Feijóo y las pensiones (15-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/20/elma-saiz-contraataca-a-feijoo-con-la-hucha-de-las-pensiones-de-vaciarse-hasta-5000-millones-con-el-pp-a-cerrar-2026-con-20000/', 'Infobae, Elma Saiz y la hucha de las pensiones (20-10-2026)'),
                 ('https://www.rtve.es/noticias/20261023/pedro-sanchez-revuelta-frases-entrevista/17279243.shtml', 'RTVE, las frases de Sánchez en La Revuelta (23-10-2026)'),
                 ('https://www.publico.es/politica/cha-frente-amplio-aragon-anuncia-presentara-congreso-teruel.html', 'Público, CHA no se presenta al Congreso por Teruel'),
                 ('https://theobjective.com/espana/tribunales/2026-10-23/supremo-bolanos-albares-afectados-ley-nietos/', 'The Objective, el Supremo y la lista de afectados por la ley de nietos (23-10-2026)'),
                 ('https://www.ehu.eus/es/web/campusa/-/el-reparto-de-los-escanos-en-el-congreso', 'Annick Laruelle en Campusa (UPV/EHU), 24-5-2019'),
                 ('https://x.com/thewarroomblog', 'Iván Redondo, cuenta de X')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/cinco-semanas-29n-la-semana-en-el-mapa.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna transparente con sobres sobre el mapa de España, entre una ciudad y un pueblo: un collage.'),
    ),
    dict(
        slug='calle-que-parte-barcelona', fecha='2026-10-25',
        foto=dict(src='img/actualidad/fotos/calle-que-parte-barcelona.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una gran avenida de Barcelona con fachadas modernistas a cada lado y el cielo partido en dos colores: un collage.'),
        titulo='Las dos calles que parten Barcelona: la Diagonal en el voto a la derecha, la Meridiana en el independentismo', serie='29n',
        descripcion='En Barcelona, el PSC ganó en casi todas las secciones censales el 23 de julio de 2023, pero sus vecinas no votan igual. La Diagonal es la calle que más veces separa a dos ganadores. La Meridiana no cambia el ganador, pero separa a Porta, donde el independentismo sacó el 29% en las autonómicas de 2024, de Sant Andreu, donde sacó el 47%.',
        compara='Las 2.632 parejas de secciones censales contiguas de la ciudad de Barcelona (al menos 80 metros de límite común y 400 electores cada una): ganador y voto a PP y Vox en las generales de 2023, voto a ERC, Junts, CUP y Aliança Catalana en las autonómicas de 2024, la calle que las separa y su renta por unidad de consumo.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada lado vota distinto. Se mezclan dos elecciones: el ganador y PP más Vox son de las generales de 2023; la suma independentista, de las autonómicas de 2024. La calle de cada límite sale de un geocodificador en cinco puntos y puede no coincidir con el límite en todos sus metros. La renta de las secciones más ricas está topada en 58.752 euros. Sin voto exterior.',
        calculo='Voto: porcentaje sobre votos válidos. Pareja de secciones vecinas: comparten al menos 80 metros de límite (con 12 metros de tolerancia) y tienen al menos 400 electores cada una. Salto: diferencia en puntos entre las dos secciones. Calle: la que devuelve el geocodificador inverso de CartoCiudad en al menos tres de cinco puntos del límite común. Medias por distrito y por barrio: media simple de sus secciones.',
        fuentes=[INTERIOR, PARLAMENT, INE,
                 ('https://www.cartociudad.es/', 'CartoCiudad (IGN), geocodificador inverso para el nombre de cada calle'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap, nombres de barrio y trazado de las calles'),
                 ('https://beteve.cat/politica/mapa-on-concentra-vot-partits-barcelona-eleccions-generals-2023/', 'Betevé, Marcos Arizmendi: on es concentra el vot de cada partit a Barcelona (generales 2023)'),
                 ('https://beteve.cat/politica/la-renda-duna-famila-de-pedralbes-multiplica-per-sis-la-duna-de-ciutat-meridiana/', 'Betevé, la renda d\'una família de Pedralbes multiplica per sis la de Ciutat Meridiana'),
                 ('https://naciodigital.cat/politica/la-meridiana-de-la-via-lliure.html', 'Nació Digital, Pep Martí: la Meridiana de la Via Lliure (8-9-2015)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2-4-2023)')],
        enlaces=[],
        lugar='Barcelona',
    ),
    dict(
        slug='quien-vota-que-barrios-29n', fecha='2026-10-25',
        titulo='Quién vota qué, barrio a barrio: el PP sube 21 puntos donde pesan las rentas del capital, el PSOE 15 donde abundan los peones y Vox solo se mueve con los jubilados', serie='29n', figura=0,
        descripcion='Crónica del domingo: las piezas de la semana sobre de qué viven los vecinos de cada barrio, contadas de una vez con un gráfico que cambia al bajar. La renta del capital, los autónomos, el oficio y la pensión reparten el voto entre PP y PSOE; a Vox casi no lo mueven.',
        compara='El voto en las generales de 2023 en los grupos de secciones censales (o códigos postales) donde menos y donde más pesan las rentas del capital, los autónomos, los empleos elementales y los pensionistas, con las cifras de las piezas publicadas entre el 19 y el 23 de octubre.',
        limites='Es una pieza de resumen: cada cifra procede de una pieza ya publicada y enlazada, donde se explica el cálculo. Las cuatro preguntas no usan la misma unidad (códigos postales de 54 ciudades sin Cataluña para el capital; secciones censales para el resto) ni son independientes: en las ciudades, el barrio de los autónomos es también el de más renta. Una sección no es una persona: no se puede saber cómo vota cada rentista, autónomo, peón o pensionista.',
        calculo='Grupos de igual número de votantes, del que menos al que más tiene de cada característica; porcentajes sobre votos a candidaturas y participación sobre el censo.',
        fuentes=[('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, generales de 2023 por sección censal'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=70006', 'INE, censo anual 2023: ocupados por cuenta propia por sección censal'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=70004', 'INE, censo anual 2023: ocupados por ocupación y sección censal'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=66594', 'INE, censo anual 2023: pensionistas por sección censal'),
                 ('https://sede.agenciatributaria.gob.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfCodPostal/2023/home.html', 'Agencia Tributaria, IRPF 2023 por código postal'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares'),
                 ('http://piketty.pse.ens.fr/files/Piketty2018.pdf', 'Thomas Piketty, Brahmin Left vs Merchant Right (2018)'),
                 ('https://www.eldiario.es/opinion/tribuna-abierta/vota-clase-trabajadora-espana_129_1401496.html', 'Alberto Garzón, ¿A quién vota la clase trabajadora en España? (eldiario.es, 2019)'),
                 ('https://doi.org/10.3389/fpos.2025.1717586', 'Roig, Espinosa y Pavía, Who votes for Vox? (Frontiers in Political Science, 2025)'),
                 ('https://revistas.um.es/sh/article/download/451231/291101/1533611', 'Manuel Trujillo, Sociología Histórica (2020)'),
                 ('https://www.vozpopuli.com/espana/madrid/vox-encuentra-en-madrid-su-gran-caladero-de-afiliaciones-una-de-cada-cuatro-se-producen-en-la-region.html', 'Vozpópuli, la campaña de Vox en el sur de Madrid')],
        enlaces=[],
        lugar='España',
        actualizado='2026-10-25 10:56',
        foto=dict(src='img/actualidad/fotos/quien-vota-que-barrios-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un despacho, un taller y un banco con dos jubilados en la misma calle, cada uno con su sobre: un collage.'),
    ),
]

# Enlaces a las fuentes dentro del texto: (texto exacto, url)
ENLACES_TEXTO = {
    'adelante-andalucia-psoe-29n': [
        ('según EFE', 'https://www.infobae.com/espana/agencias/2026/10/23/adelante-logra-los-avales-para-las-elecciones-y-espera-parar-a-la-derecha-con-andalucismo/'),
        ('según el escrutinio de la Junta de Andalucía', 'https://resultadoseleccionesandalucia.es'),
        ('según explicó María Jesús Montero el 20 de octubre', 'https://www.europapress.es/andalucia/noticia-psoe-cedera-frente-amplio-numero-candidaturas-andaluzas-senado-29n-sevilla-huelva-20261020133736.html'),
        ('Según Europa Press', 'https://www.europapress.es/andalucia/noticia-vox-pp-partidos-mayor-fidelidad-17m-psoe-movilizaria-mas-generales-cis-20260627100950.html'),
    ],
    'lorca-fuente-vaqueros-viznar-1936': [
        ('Museo Reina Sofía', 'https://commons.wikimedia.org/wiki/File:Fotograf%C3%ADa_an%C3%B3nima_MNCARS_4.jpg'),
    ],
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
    # <title> con lo que se busca («qué partido gobierna…», «desde cuándo gobierna…»); el titular sigue en h1 y og:title
    corto = re.sub(r'^(La|El) ', '', h['corto'].replace(' en las urnas', ''))
    q['titulo_seo'] = f'¿Quién gobierna {corto}? Historia electoral y resultados desde 1977'
    if os.path.exists(os.path.join(SRC, '..', '..', 'img', 'actualidad', 'fotos', h['slug'] + '.jpg')):
        q['foto'] = dict(src=f"img/actualidad/fotos/{h['slug']}.jpg", ancho=1280, alto=720, ia=True,
                         pie=f"Collage sobre las elecciones en {h['lugar']}: la bandera, el mapa y vecinos votando.")
    COMUNIDADES.append(q)

PIEZAS = COMUNIDADES + HISTORIA + PIEZAS

# Serie «Girona, de prop»: peces escrites directament en català (idioma='ca'); textos i gràfics a
# /mnt/project-files/girona/peces/eines/ (p_*.py escriuen els <slug>.html de treball). Nacho, 15-10-2026.
SERIES['girona'] = 'Girona, de prop'
SERIES_CA = {'girona': 'Girona, de prop', '29n': 'Camí al 29N'}
INTERIOR_CA = (INTERIOR[0], "Ministeri de l'Interior, resultats electorals per mesa (Infoelectoral), via pollspaindata. Sense vot exterior (CERA)")
INE_CA = (INE[0], "INE, Atles de Distribució de Renda de les Llars (renda i edat per secció), via ineAtlas.data")
PIEZAS += [
    dict(
        slug='girona-barri-a-barri-29n', fecha='2026-10-15', idioma='ca', actualizado='2026-10-23 22:54',
        correcciones="23-10-2026: s'hi afegeixen el vot de Vox a la Font de la Pólvora i a Vila-roja comptat sobre el cens i en vots, la relació entre renda i vot a Vox a les 62 seccions, la cita d'un estudi acadèmic sobre el perfil del votant de Vox i un apartat final sobre com pesen la ciutat, els barris i el vot de la CUP en el repartiment dels sis escons de la demarcació el 29N.",
        titulo='Girona, barri a barri: el 2019 Junts guanyava en 36 seccions i el PSC en 13; el 2023, el PSC en 43 i Junts en 19', serie='girona',
        descripcion='A la Font de la Pólvora va votar el 33,4% dels electors; a Montjuïc, el 74,9%. Les 62 seccions de Girona, de les generals de 2019 a les de 2023, abans del 29N.',
        compara='Les 62 seccions censals de la ciutat de Girona a les generals de novembre de 2019 i juliol de 2023, agrupades per districte censal de l\'INE i per trams de renda per unitat de consum de 2023.',
        limites='Són dades de seccions, no de persones, i no expliquen per què cada barri vota com vota. Sense vot exterior, de manera que la participació surt més alta que l\'oficial. La comparació amb novembre de 2019 només inclou les 61 seccions que conserven el codi. Els districtes censals de l\'INE no coincideixen amb els barris municipals; els noms que els donem surten dels carrers de cada secció i són descriptius. Els límits de secció estan simplificats. El càlcul de quants votants més hi hauria hagut amb una altra participació és aritmètic, no una previsió, i no diu a qui haurien votat.',
        fuentes=[INTERIOR_CA, INE_CA,
                 ('https://www.girona.cat/opendata/dataset/sectors', 'Ajuntament de Girona, dades obertes: barris i sectors'),
                 ('https://intranet.colpis.cat/files/revista/101_articulo.pdf', 'Macià Serra, COLPIS, sobre el vot a Girona'),
                 ('https://www.3cat.cat/3catinfo/aixi-van-votar-els-barris-mes-pobres-i-els-mes-rics-a-catalunyael-14f/noticia/3078187/', '3Cat, el vot dels barris més pobres i més rics (2021)'),
                 ('https://www.ara.cat/comarquesgironines/l-xarxa-electrica-font-polvora-correcte-potencia-50-anys_1_4266052.html', 'Ara, la xarxa elèctrica de la Font de la Pólvora (2022)'),
                 ('https://seu.girona.cat/portal/dades/transparencia/docs/Auditoria-BaixaTensio-FontdelaPolvora.pdf', 'Ajuntament de Girona, auditoria de baixa tensió de la Font de la Pólvora'),
                 ('https://naciodigital.cat/girona/politica-girona/salellas-reclama-iniciativa-politica-mentre-la-militancia-de-la-cup-ratifica-el-no-al-29-n.html', 'Nació Digital, Salellas i el no de la CUP al 29N (11-10-2026)'),
                 ('https://naciodigital.cat/girona/politica-girona/lluc-salellas-alcalde-girona-junts-psc-mes-pendents-barcelona-madrid.html', 'Nació Digital, entrevista a Lluc Salellas (2-8-2026)'),
                 ('https://3cat.cat/3catinfo/junts-anunciara-aquest-mati-que-trenca-el-pacte-a-lajuntament-de-girona-amb-guanyem-i-erc/noticia/3420236/', '3Cat, Junts trenca el pacte de govern (14-7-2026)'),
                 ('https://naciodigital.cat/politica/junts-repetira-equip-a-madrid-sota-el-lideratge-de-miriam-nogueras.html', 'Nació Digital, les llistes de Junts (8-10-2026)'),
                 ('https://cdn.girona.cat/sgdap/carrers/19870322-06.pdf', 'Punt Diari, els carrers de Can Gibert (22-3-1987)'),
                 ('https://doi.org/10.3389/fpos.2025.1717586', 'Roig, Espinosa i Pavía, «Who votes for Vox?», Frontiers in Political Science (2025)'),
                 ('https://github.com/dadosdelaplace/pollspaindata', "pollspaindata (dades d'Interior per mesa): vots per candidatura a la ciutat i a la província el 2023")],
        enlaces=[],
        lugar='Girona',
        foto=dict(src='img/actualidad/fotos/girona-barri-a-barri-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie="Girona, l'Onyar i la Catedral, amb el mapa de les seccions: un collage."),
    ),
    dict(
        slug='girona-esco-285-vots-29n', fecha='2026-10-15', idioma='ca', actualizado='2026-10-23 23:15',
        titulo="L'escó més ajustat d'Espanya és a Girona: el PP se'n va quedar fora per 285 vots, menys gent de la que vota en una mesa", serie='girona',
        descripcion="Cap de les 536 seccions de la província no va donar 285 vots al PP: la que més, 188. A la Vajol, Susqueda, Meranges i Albanyà junts hi van votar 238 persones.",
        compara="El repartiment dels sis escons de la província de Girona a les generals de juliol del 2023 i de novembre del 2019, amb la llei D'Hondt, i els vots per mesa, secció i municipi.",
        limites="La distància de 285 vots és la que necessitava el PP perquè el seu primer quocient superés el segon de Junts sense que cap altre partit canviés; en una elecció real, si uns vots es mouen, se'n mouen d'altres, i els vots necessaris depenen de qui els perd (190 si venien de Junts). La comparació sense vot exterior resta els vots CERA de cada partit. Els vots per secció i per municipi no inclouen el vot exterior. Les dades no diuen per què ningú va votar o no va votar.",
        fuentes=[(INTERIOR[0], "Ministeri de l'Interior, resultats electorals per mesa (Infoelectoral), via pollspaindata, amb el vot exterior (CERA)"),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672', 'Llei orgànica del règim electoral general (LOREG), article 163'),
                 ('https://www.gutierrez-rubi.es/wp-content/uploads/2010/03/regimen-electoral.pdf', "Consell d'Estat, informe sobre el règim electoral (24-2-2009)"),
                 ('https://naciodigital.cat/girona/politica-girona/salellas-reclama-iniciativa-politica-mentre-la-militancia-de-la-cup-ratifica-el-no-al-29-n.html', 'Nació Digital, Salellas i el no de la CUP al 29N (11-10-2026)'),
                 ('https://naciodigital.cat/girona/politica-girona/lluc-salellas-alcalde-girona-junts-psc-mes-pendents-barcelona-madrid.html', 'Nació Digital, entrevista a Lluc Salellas (2-8-2026)'),
                 ('https://www.diariodeleon.es/nacional/261008/2099696/junts-confirma-miriam-nogueras-candidata-29n.html', 'EFE, les llistes de Junts (8-10-2026)'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-2022-16018', 'Llei orgànica 12/2022, que suprimeix el vot pregat'),
                 ('https://www.elindependiente.com/espana/madrid/2023/07/29/recuento-de-voto-cera-en-madrid-el-pp-casi-duplica-al-psoe-y-sumar-gana-a-vox/', 'El Independiente / Europa Press, el vot CERA a Madrid (29-7-2023)')],
        enlaces=[],
        lugar='Girona',
        foto=dict(src='img/actualidad/fotos/girona-esco-285-vots-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie="Una papereta amb el número 285 i el mapa de la província: un collage."),
    ),
    dict(
        slug='junts-girona-puigdemont-29n', fecha='2026-10-15', idioma='ca', actualizado='2026-10-23 23:15',
        correcciones="23-10-2026: s'hi afegeixen el recompte de vots per blocs sobre el cens (independentistes i no independentistes) i la participació secció a secció, la desmobilització independentista del 2023 i un apartat sobre el PSC. Es corregeixen xifres calculades abans amb una aproximació: Junts va treure el 19,2% a la ciutat el 2023, no el 19,1%; el 25,9% el 2019, no el 25,8%; el PSC, el 29,6% el 2023, no el 29,3%; a la província, Junts va treure el 19,8% el 2023 (no el 19,6%) i va guanyar en 181 seccions (no 180) i el PSC en 326 (no 327); al Parlament del 2024, el 35,3% i 426 de les 536 seccions sense comptar el vot exterior (abans 35,2% i 428 de 537). Els percentatges de les seccions del Mercadal, el Carme i Montjuïc del 2024 estaven calculats sobre vots vàlids i no sobre vots a candidatures, com la resta de la peça. Les conclusions no canvien.",
        titulo='A Girona, Junts gairebé duplica el vot del Congrés al Parlament: el 19,2% el 2023 i el 36,3% el 2024, amb Puigdemont de candidat', serie='girona',
        descripcion='Al Parlament, Junts va guanyar en 48 de les 62 seccions de la ciutat; a les generals, en 19. Però la distància ja hi era el 2021, sense Puigdemont a la papereta.',
        compara='Les 62 seccions censals de la ciutat de Girona i les 537 de la província a les generals de novembre del 2019 i juliol del 2023 i a les eleccions al Parlament del 2021 i el 2024.',
        limites="Són dades de seccions, no de persones: no diuen si els que van votar Junts el 2024 són els mateixos que el 2023, ni per què. Els censos del Parlament i del Congrés són lleugerament diferents, i el vot per secció no inclou el vot exterior. Percentatges sobre vots a candidatures, excepte on es diu que són sobre el cens. Els blocs independentista i no independentista són una convenció. Les relacions entre seccions són associacions, no proves de trasvasaments de vot. Límits de secció simplificats.",
        fuentes=[INTERIOR_CA,
                 ('https://github.com/dadosdelaplace/pollspaindata', "pollspaindata (dades d'Interior per mesa): vots, blancs i nuls de cada candidatura a les generals del 2019 i el 2023"),
                 ('https://analisi.transparenciacatalunya.cat/', 'Generalitat de Catalunya, dades obertes: resultats de les eleccions al Parlament per secció censal (2021 i 2024)'),
                 ('https://intranet.colpis.cat/files/revista/101_articulo.pdf', 'Macià Serra, COLPIS, sobre el vot a Girona'),
                 ('https://www.3cat.cat/324/puigdemont-renunciara-dema-a-lalcaldia-de-girona-en-un-ple-extraordinari/noticia/2706547/', "3Cat, Puigdemont deixa l'alcaldia (11-1-2016)"),
                 ('https://3cat.cat/3catinfo/junts-anunciara-aquest-mati-que-trenca-el-pacte-a-lajuntament-de-girona-amb-guanyem-i-erc/noticia/3420236/', '3Cat, Junts trenca el pacte de govern (14-7-2026)'),
                 ('https://naciodigital.cat/girona/politica-girona/lluc-salellas-alcalde-girona-junts-psc-mes-pendents-barcelona-madrid.html', 'Nació Digital, entrevista a Lluc Salellas (2-8-2026)'),
                 ('https://naciodigital.cat/politica/junts-repetira-equip-a-madrid-sota-el-lideratge-de-miriam-nogueras.html', 'Nació Digital, les llistes de Junts (8-10-2026)'),
                 ('https://ca.wikipedia.org/wiki/Eleccions_al_Parlament_de_Catalunya_de_2021', 'Viquipèdia, eleccions al Parlament del 2021'),
                 ('https://ca.wikipedia.org/wiki/Eleccions_al_Parlament_de_Catalunya_de_2024', 'Viquipèdia, eleccions al Parlament del 2024'),
                 ('https://www.3cat.cat/3catinfo/lanc-no-demanara-labstencio-ni-el-vot-nul-el-23j-perque-les-bases-ho-han-rebutjat/noticia/3238866/', "ACN a 3Cat, les bases de l'ANC rebutgen demanar l'abstenció el 23J (4-7-2023)"),
                 ('https://www.ara.cat/politica/independentistes-no-voler-votar-12-m_1_5031393.html', "Roger Palós i Xavi Tedó, Ara, sobre l'abstenció independentista el 12-M (21-5-2024), amb declaracions d'Ivan Serrano (UOC)"),
                 ('https://mapaelectoral.es/girona-ca.html', "Mapa Electoral, l'abstenció a Girona secció a secció")],
        enlaces=[],
        lugar='Girona',
        foto=dict(src='img/actualidad/fotos/junts-girona-puigdemont-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie="Puigdemont davant de l'Onyar i el mapa de les seccions de Girona: un collage."),
    ),
    dict(
        slug='alianca-catalana-ceo-mapa-ca', fecha='2026-10-15', idioma='ca', actualizado='2026-10-23 23:05',
        titulo="El CEO dona a Aliança Catalana fins a 25 escons: al Parlament del 2024 va treure el 3,8%, però el 24,9% al Ripollès i el 7,8% als pobles de menys de 1.000 electors", serie='girona',
        descripcion="Aliança no es presenta el 29N, però el baròmetre del CEO la situa com a tercera força en unes eleccions al Parlament. El seu únic resultat oficial dibuixa un mapa amb centre al Ripollès, fort al nord de Girona i a l'interior.",
        compara="El vot a Aliança Catalana a les eleccions al Parlament del 2024 als 947 municipis de Catalunya, per comarca, demarcació i mida del municipi, al costat del de Junts i Vox.",
        limites="El baròmetre del CEO és una enquesta amb un marge d'error de ±2,19 punts i pregunta per unes eleccions al Parlament: no és una previsió per al 29N, on Aliança no es presenta. El mapa és el del 2024, quan Aliança va treure el 3,8%: no diu on creixeria. Sense vot exterior. Les cites es reprodueixen com es van publicar, en català o en castellà. Versió en català de la peça publicada en castellà.",
        fuentes=[('https://analisi.transparenciacatalunya.cat/resource/ntc4-rnwr', 'Generalitat de Catalunya, resultats de les eleccions al Parlament del 2024 per municipi (dades obertes)'),
                 ('https://govern.cat/salapremsa/notes-premsa/880300/el-ceo-publica-els-resultats-de-la-2a-onada-del-bar-metre-de-2026', 'Govern, el CEO publica la segona onada del baròmetre del 2026 (14-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/14/el-psc-vence-pero-retrocede-en-el-parlament-y-alianca-estabiliza-su-ascenso-segun-el-ceo/', 'EFE via Infobae, el PSC guanya però retrocedeix, segons el CEO (14-10-2026)'),
                 ('https://www.diaridetarragona.com/catalunya/273081/psc-18-19-ganaria-elecciones-generales-catalunya-seguido-erc-10-11-ppc-vox.html', 'EFE via Diari de Tarragona, presentació del CEO (14-10-2026)'),
                 ('https://es.ara.cat/politica/alianca-catalana-no-presenta-elecciones-espanolas_1_5870081.html', 'Ara, per què Aliança no es presenta a les generals (5-10-2026)'),
                 ('https://www.ara.cat/politica/l-eix-transversal-l-extrema-dreta-l-herencia-carlista-xenofobia_130_5741966.html', "Jordi Muñoz, L'eix transversal de l'extrema dreta, Ara (23-5-2026)"),
                 ('https://www.ara.cat/politica/enquestes/alianca-catalana-sedueix-comarques-mes-desateses-lleida-girona_1_5575399.html', 'Ara, Aliança sedueix les comarques més desateses (29-11-2025)'),
                 ('https://www.ara.cat/politica/eleccions-catalunya/barris-pobres-rics-vox-classe-mitjana-alianca-catalana_1_5032813.html', 'Ara, anàlisi per secció censal del 12-M (19-5-2024)'),
                 ('https://naciodigital.cat/politica/on-anira-vot-alianca-catalana-29-n.html', "Nació Digital, on anirà el vot d'Aliança el 29-N (10-10-2026)"),
                 ('https://naciodigital.cat/politica/la-immigracio-i-no-la-independencia-explica-la-fuga-de-vots-de-junts-cap-a-alianca-catalana.html', "Nació Digital, estudi de Martínez-Cantó i Tudó a l'ICPS (10-6-2026)")],
        enlaces=[],
        lugar='Catalunya',
        foto=dict(src='img/actualidad/fotos/alianca-catalana-ceo-mapa.jpg', ancho=1280, alto=720, ia=True,
                  pie="Sílvia Orriols, un ajuntament, unes barres i un mapa de Catalunya: un collage."),
    ),
    dict(
        slug='blocs-i-cases-girona', fecha='2026-10-21', idioma='ca', actualizado='2026-10-23 23:10',
        titulo="Als barris de blocs dels anys seixanta i setanta de Girona vota un de cada tres adults; a les zones de cases, gairebé sis de cada deu", serie='girona',
        descripcion="La participació sobre el cens va ser del 50,9% als blocs i del 64,5% a les cases, segons els 511.090 habitatges del Cadastre situats secció a secció. Als blocs, el PSC va treure el 41,2% el 2023; a les cases, el 23,2%. Són els extrems: secció a secció, la relació és moderada, i la renda i la població estrangera hi diuen més que l'edifici.",
        compara="Els 205.879 edificis residencials del Cadastre a la província de Girona (any de construcció i nombre d'habitatges), agregats a les 536 seccions censals del 2023 i creuats amb la participació i el vot a les generals de juliol del 2023, la renda de l'INE i el cens del 2021.",
        limites="Són dades de seccions, no de persones. L'any del Cadastre és el de construcció, no el de l'última reforma, i els habitatges inclouen segones residències i pisos buits. Cada edifici es col·loca a la secció on cau el centre del seu contorn (un 0,12% cau en una secció d'un municipi veí). El Cadastre és d'agost del 2026 i les eleccions, de juliol del 2023 (els habitatges acabats des del 2023 són el 0,9%). «Sense dret a vot» és una estimació: adults residents menys cens electoral. El model estadístic descriu associacions, no causes. El padró és municipal i inclou els nuclis antics, no només les urbanitzacions. El cens no diu d'on ve cada veí ni quant temps fa que viu a la secció. Sense vot exterior. Límits de secció simplificats.",
        calculo="Participació sobre el cens; vot per partit sobre vot vàlid, ponderat per votants. «Blocs de 1960-1979»: seccions amb més del 60% dels habitatges construïts aquells anys; «zones de cases»: més del 80% dels habitatges en edificis d'un sol habitatge, separades en pobles vells (any mediana dels habitatges anterior al 1960) i urbanitzacions (1960 o posterior). Model: regressió ponderada amb variables estandarditzades, com a la peça de Girona (530 seccions amb totes les dades), amb validació fora de mostra per grups de municipis i una versió només dins de cada municipi.",
        fuentes=[('https://www.catastro.hacienda.gob.es/INSPIRE/buildings/ES.SDGC.BU.atom.xml', "Direcció General del Cadastre (Ministeri d'Hisenda), edificis INSPIRE per municipi, agost del 2026"),
                 INTERIOR_CA, INE_CA,
                 ('https://github.com/pablogguz/ineAtlas.data', "INE, Cens de Població i Habitatges 2021 i límits de secció del 2023, via ineAtlas.data"),
                 ('https://analisi.transparenciacatalunya.cat/', "Generalitat de Catalunya, participació per secció a les municipals del 2023 i al Parlament del 2024"),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', "Manuel Trujillo i Braulio Gómez Fortes, «La segregación electoral interurbana en España», VIII Informe FOESSA (2019)"),
                 ('https://seu.girona.cat/portal/dades/transparencia/docs/Auditoria-BaixaTensio-FontdelaPolvora.pdf', "Ajuntament de Girona, auditoria de baixa tensió de la Font de la Pólvora"),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=2870', "INE, padró continu per municipi, província de Girona (taula 2870), 1996 i 2023"),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-2009-5850', "Llei 3/2009, de 10 de març, de regularització i millora d'urbanitzacions amb dèficits urbanístics (preàmbul; derogada el 2025)"),
                 ('https://naciodigital.cat/baixmontseny/societat/viure-en-urbanitzacions-allegals-selva-problema-afegit.html', "Nació Digital, «Viure en urbanitzacions «al·legals» de la Selva, un problema afegit» (1 d'agost del 2024)")],
        enlaces=[],
        lugar='Girona',
        foto=dict(src='img/actualidad/fotos/blocs-i-cases-girona.jpg', ancho=1280, alto=720, ia=True,
                  pie="Blocs dels anys setanta, l'Onyar i la Catedral, cases amb jardí i una urna: un collage."),
    ),
    dict(
        slug='salaris-pensions-ajudes-girona', fecha='2026-10-21', idioma='ca', actualizado='2026-10-23 23:15',
        correcciones="23-10-2026: s'hi afegeix un apartat que separa, als barris on més pesen les prestacions, l'abstenció de qui pot votar i la barrera del cens (adults sense nacionalitat espanyola), amb un gràfic i la comparació entre la costa, Girona i Salt i la resta de l'interior. Es reforça l'avís que són dades de barris i no de persones. Les xifres anteriors no canvien.",
        titulo="Als barris de Girona on més pesa l'atur en la renda es vota 12 punts menys; on més pesen les pensions, igual que a la resta", serie='girona',
        descripcion="Dades d'Hisenda via l'INE, secció a secció. A la Font de la Pólvora, el 31,8% de la renda són prestacions i hi va votar el 33,4%. On més pesa l'atur, el PSC va treure el 37,5% i Junts l'11,0%.",
        compara="La composició de la renda bruta del 2023 (salaris, pensions, prestacions d'atur, altres prestacions i altres ingressos) de 534 de les 536 seccions censals de la província de Girona, creuada amb la participació i el vot a les generals de juliol del 2023, les municipals del 2023 i el Parlament del 2024.",
        limites="Són dades de seccions, no de persones. La renda per font surt de dades tributàries i de registres de prestacions agregats per l'INE i no inclou les rendes que no hi consten. Percentatges sobre la renda bruta. «Sense dret a vot» és una estimació: adults residents menys cens electoral. Els grups de seccions no tenen exactament la mateixa mida perquè l'INE dona els percentatges amb un decimal. El model estadístic descriu associacions, no causes; el pes de l'atur en la renda i l'atur del cens es mesuren gairebé igual. La separació entre abstenció i barrera del cens és una descomposició comptable, no una explicació. Costa: els 20 municipis amb litoral. La Vajol i Susqueda no tenen dades. Sense vot exterior.",
        calculo="Participació sobre el cens; vot per partit sobre vot vàlid, ponderat per votants. Grups: cinquens de seccions segons el pes de cada font. Barrera del cens i abstenció: la diferència d'adults que voten entre el primer i el cinquè grup es reparteix entre el canvi de la part d'adults al cens (per la participació mitjana) i el canvi de la participació (per la part mitjana d'adults al cens). Model: regressió ponderada amb variables estandarditzades (532 seccions), amb validació fora de mostra per grups de municipis i una versió només dins de cada municipi.",
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=30825', "INE, Atles de Distribució de Renda de les Llars: distribució per font d'ingressos, per secció censal (taula 30825), any 2023"),
                 ('https://ine.es/metodologia/metodologia_adrh.pdf', "INE, metodologia de l'Atles de Distribució de Renda de les Llars (definició de cada font)"),
                 INTERIOR_CA, INE_CA,
                 ('https://analisi.transparenciacatalunya.cat/', "Generalitat de Catalunya, participació per secció a les municipals del 2023 i al Parlament del 2024"),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', "Manuel Trujillo i Braulio Gómez Fortes, «La segregación electoral interurbana en España», VIII Informe FOESSA (2019)")],
        enlaces=[],
        lugar='Girona',
        foto=dict(src='img/actualidad/fotos/salaris-pensions-ajudes-girona.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mare amb el seu fill, d’esquena, davant les cases de l’Onyar i la catedral de Girona.'),
    ),
    dict(
        slug='polaritzacio-girona', fecha='2026-10-22', idioma='ca',
        actualizado='2026-10-23 23:00',
        correcciones="23-10-2026: s'afegeix el càlcul partit a partit dins del bloc independentista i el de Girona i Salt juntes. L'índex de Moran de Salt (0,20) s'havia calculat amb les 15 seccions, incloses les rurals; amb les 13 urbanes, com la resta de la peça, és de 0,03 i no és significatiu.",
        titulo='A Girona el vot independentista va del 4% al 75% segons la secció', serie='girona',
        descripcion="Girona és la sisena de 41 ciutats catalanes on els barris voten més diferent (índex de Duncan), però només la 22a on aquestes diferències formen blocs (índex de Moran). La Font de la Pólvora, una illa.",
        compara="Les 57 seccions censals urbanes de Girona a les eleccions al Parlament del 2024, partit a partit i en blocs, comparades amb els 41 municipis catalans amb 15 seccions urbanes o més, amb les 13 seccions urbanes de Salt (per separat i juntes amb Girona), amb la renda per unitat de consum i amb la població estrangera del 2023.",
        limites="Són dades de seccions, no de persones, i no expliquen per què s'agrupa el vot. El bloc independentista (Junts, ERC, CUP i Aliança Catalana) suma partits molt allunyats en l'eix esquerra-dreta: la relació amb la renda és sobretot de Junts, i a Girona l'eix nacional i l'eix esquerra-dreta coincideixen, de manera que no es poden separar. Sense Aliança l'índex amb prou feines canvia. Els índexs depenen de com dibuixa l'INE les seccions i de què es considera veí. Les seccions rurals (menys de 1.000 habitants per km²) queden fora. Els noms dels barris surten dels carrers de cada secció. Sense vot exterior. Límits de secció simplificats.",
        calculo="Percentatges sobre vots a candidatures. Índex de Moran global i local (9.999 permutacions, significació al 5%) amb veïnatge de tipus reina normalitzat per files. Índex de Duncan entre el bloc independentista i la resta. Pes del districte: part de la variància entre seccions explicada pel districte censal, ponderada per vots. Correlació de rangs de Spearman amb la renda. Girona i Salt juntes: mateix veïnatge sobre les 70 seccions urbanes; salts al límit, parelles de seccions de municipis diferents que comparteixen 50 metres de límit o més.",
        fuentes=[('https://analisi.transparenciacatalunya.cat/d/ntc4-rnwr', "Generalitat de Catalunya, Transparència Catalunya: resultats del Parlament 2024 per secció censal"),
                 INE_CA,
                 ('https://www.ine.es/prodyser/cartografia/seccionado_2023.zip', "INE, cartografia de seccions censals (1 de gener del 2023)"),
                 ('https://intranet.colpis.cat/files/revista/101_articulo.pdf', 'Macià Serra, COLPIS, sobre el vot a Girona')],
        enlaces=[],
        lugar='Girona',
    ),
    dict(
        slug='girona-1936-participacio', fecha='2026-10-22', idioma='ca', actualizado='2026-10-23 23:02',
        titulo="El 1936 Salt votava més que avui: 76 % de participació, contra el 55 % del 23J", serie='girona',
        descripcion="A 128 dels 219 municipis de la demarcació de Girona es va votar més el febrer del 1936 que a les generals del 2023: el 77 % a Girona ciutat, contra el 62 %; el 73 % a Figueres, contra el 55 %. El 1933, la primera vegada que van votar les dones, la participació va ser deu punts més baixa.",
        compara="Els 219 municipis actuals de la demarcació de Girona a les eleccions generals del 19 de novembre del 1933, del 16 de febrer del 1936 i del 23 de juliol del 2023: participació i candidatura guanyadora.",
        limites="El 1936 només votaven els majors de 23 anys, i el 2023, els de 18 en amunt; la participació és sobre el cens de cada elecció. Els municipis desapareguts des del 1936 se sumen a l'actual en què es van integrar, segons l'INE. El 1933 i el 1936 es votava amb llistes obertes i diversos vots per elector; el pes de cada candidatura és la seva part dels vots a candidats. Les dades per municipi no separen el vot per sexe. Les correlacions no expliquen per què es vota menys avui. Sense vot exterior el 2023. El pes dels joves en l'abstenció surt d'una enquesta estatal, no de dades de Girona. L'alçada és la del nucli segons Wikidata; set municipis no hi tenen dada i queden fora d'aquesta comparació. Els adults sense dret a vot de Salt surten de restar el cens electoral de la població adulta.",
        calculo="Participació: votants sobre cens de cada elecció. Mitjana de la demarcació ponderada pel cens. Correlació de Pearson entre municipis.",
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat i Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR_CA, INE_CA,
                 ('https://www.ine.es/intercensal/', "INE, alteracions dels municipis als censos de població des del 1842"),
                 ('https://es.ara.cat/politica/votaron-pueblo-elecciones-1936_1_5730095.html', "Aleix Moldes, «¿Qué votaron en tu pueblo en 1936?», Ara (8-5-2026)"),
                 ('https://naciodigital.cat/politica/que-es-va-votar-durant-la-segona-republica-al-teu-poble-aixi-funciona-el-nou-atles-interactiu.html', "Nació Digital, «Què es va votar durant la Segona República al teu poble?» (7-5-2026)"),
                 ('https://www.marxists.org/espanol/tematica/mujer/autores/campoamor/1931/oct01.htm', "Clara Campoamor, discurs a les Corts de l'1 d'octubre del 1931"),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_1933', "Viquipèdia en castellà, «Elecciones generales de España de 1933» (consultada el 22-10-2026)"),
                 ('https://www.cis.es/documents/d/cis/es3420vpMT_a', "CIS, estudi 3420, postelectoral de les generals del 2023 (recordatori de vot per edat)"),
                 ('https://www.wikidata.org/wiki/Property:P2044', "Wikidata, altitud dels municipis (consultada el 23-10-2026)")],
        enlaces=[],
        lugar='Girona',
    ),
]

# Serie «Bastiones y desiertos»: las cinco secciones de España con más y con menos voto de cada partido (generales 2023)
SERIES['bastiones'] = 'Bastiones y desiertos'
PIEZAS += [
    dict(
        slug='psoe-cinco-barrios-ceuta', fecha='2026-10-20',
        titulo='Los 5 barrios de España donde el PSOE saca más del 86% de los votos: todos están en Ceuta (y dónde no llega al 2,5%)', serie='bastiones',
        descripcion='En el Príncipe Alfonso, el PSOE sacó el 93,2% el 23J, con una participación del 44%. Seis de las ocho secciones de España donde pasó del 80% están en Ceuta. Y en Errezil, Amoroto o Kortezubi no llegó al 2%.',
        compara='Las secciones censales de España con al menos 300 electores en las generales de julio de 2023 (32.976), ordenadas por el porcentaje del PSOE, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los nombres de barrio salen de las calles de cada sección (CartoCiudad) y de la prensa local, no de una relación oficial. No hay datos de religión ni de origen por sección. La renta por unidad de consumo es la del INE para 2023; el paro, el del censo de 2021. Los ceros que parecen un error de clasificación (el voto de un partido contado como «otros») se descartan como mínimos. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta y edad por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles de cada sección)'),
                 ('https://www.diariosigloxxi.com/texto-ep/mostrar/20261017143131/ceuta-niega-vaya-concurrir-coalicion-psoe-otras-formaciones-izquierda-senado', 'Europa Press, Ceuta Ya! niega que vaya a concurrir en coalición con el PSOE al Senado (17-10-2026)'),
                 ('https://www.diariodeleon.es/nacional/261005/2099383/feijoo-elige-ceuta-primer-viaje-precampana-miercoles-junta-directiva-pp.html', 'Europa Press, Feijóo elige Ceuta para su primer viaje de precampaña (5-10-2026)'),
                 ('https://elfarodeceuta.es/ceuta-ya-elecciones-23j-ventaja-ultraderecha/', 'El Faro de Ceuta, Ceuta Ya! no concurrirá a las generales del 23J (8-6-2023)'),
                 ('https://elfarodeceuta.es/psoe-valora-localistas-busca-union/', 'El Faro de Ceuta, el PSOE valora la decisión de los localistas (12-6-2023)'),
                 ('https://elfarodeceuta.es/el-pp-gano-en-todos-los-distritos-salvo-principe-benzu-y-en-73-de-las-93-mesas/', 'El Faro de Ceuta, el voto por distritos en las generales de 2016 (28-6-2016)'),
                 ('https://www.ceutaldia.com/articulo/politica/votos-generales-mesa-mesa-dibujan-mapa-desigualdad-2-ceutas-claridad/20230725004623266945.html', 'Ceuta al Día, el voto mesa a mesa en las generales de 2023 (25-7-2023)'),
                 ('https://www.cepc.gob.es/sites/default/files/2021-12/27094carmengonzalezenriquezrep140.pdf', 'Carmen González Enríquez, Los frenos al pluralismo cultural en territorios de soberanía discutida: los casos de Ceuta y Melilla, Revista de Estudios Políticos 140 (2008)'),
                 ('https://seguridadinternacional.es/resi/html/representacion-politica-e-identidad-local-en-ceuta-1975-2023/', 'Alicia Fernández, Representación política e identidad local en Ceuta (1975-2023), Revista de Estudios en Seguridad Internacional 11-1 (2025)'),
                 ('https://silvanmiracle.com/informe/informe-postelectoral-elecciones-al-parlamento-vasco-2024/', 'Silván & Miracle, informe postelectoral de las elecciones al Parlamento Vasco de 2024')],
        enlaces=[],
        lugar='Ceuta y País Vasco',
        foto=dict(src='img/actualidad/fotos/psoe-cinco-barrios-ceuta.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones de España con más voto al PSOE en 2023, todas en Ceuta, y las cinco con menos, en el País Vasco.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='pp-cinco-pueblos-galicia', fecha='2026-10-20',
        titulo='Los 5 pueblos de España donde el PP saca hasta el 81,5% de los votos: todos en Galicia (y los dos rincones vascos donde no tuvo ni un voto)', serie='bastiones',
        descripcion='Avión (81,5%), Quintela de Leirado (81,3%) y Beariz (81,1%), en Ourense, son las únicas secciones de España donde el PP pasó del 80% el 23J. En Hernani y Amoroto, en cambio, no tuvo ni un voto.',
        compara='Las secciones censales de España con al menos 300 electores en las generales de julio de 2023 (32.976), ordenadas por el porcentaje del PP, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior (CERA), que no se puede asignar a una sección; por eso la participación sale más alta que la oficial y los porcentajes de Avión o Beariz no incluyen el voto de sus emigrantes. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La renta por unidad de consumo es la del INE para 2023. El estudio sobre clientelismo citado trata de las autonómicas gallegas de 2024, no de las generales. Los ceros que parecen un error de clasificación (el voto de un partido contado como «otros») se descartan como mínimos. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta y edad por sección), vía ineAtlas.data'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://www.elespanol.com/reportajes/20230722/avion-ourense-vota-mexico-pueblo-sufragios-espana-residentes/780672062_0.html', 'El Español, En Avión (Ourense) se vota desde México (22-7-2023)'),
                 ('https://ruralager.org/wp-content/uploads/04-Ager-42-GONZALEZ-02.pdf', 'Juan Jesús González Rodríguez y Luis Barreiro-Castro, El ecosistema electoral de Galicia: el papel de los territorios rurales en las elecciones autonómicas de 2024, Ager 42 (2025)'),
                 ('https://www.eldiario.es/galicia/politica/peares-pueblo-alcaldes-feijoo-estanquera_1_2727539.html', 'elDiario.es, Os Peares, el pueblo que elige cuatro alcaldes (24-5-2019)'),
                 ('https://www.diariodeleon.es/nacional/261005/2099383/feijoo-elige-ceuta-primer-viaje-precampana-miercoles-junta-directiva-pp.html', 'Europa Press, Feijóo, candidato del PP a la Presidencia del Gobierno, elige Ceuta para su primer viaje de precampaña (5-10-2026)'),
                 ('https://www.ultimahora.es/elecciones/23j/congreso/amoroto.html', 'Última Hora, resultados del 23J en Amoroto'),
                 ('https://silvanmiracle.com/informe/informe-postelectoral-elecciones-al-parlamento-vasco-2024/', 'Silván & Miracle, informe postelectoral de las elecciones al Parlamento Vasco de 2024')],
        enlaces=[],
        lugar='Galicia y País Vasco',
        foto=dict(src='img/actualidad/fotos/pp-cinco-pueblos-galicia.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones de España con más voto al PP en 2023, todas en Galicia, y las cinco con menos, en el País Vasco.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='vox-cinco-barrios-el-ejido-ceuta', fecha='2026-10-20',
        titulo='Los 5 barrios de España donde Vox saca más del 39% de los votos: El Ejido, Ceuta y el campo de Murcia (y los pueblos vascos donde no tuvo ni un voto)', serie='bastiones',
        descripcion='En el campo de El Ejido, Vox sacó el 43,7% el 23J, su máximo en España. Ninguna sección pasó del 45%. Las cinco primeras están en El Ejido, Ceuta y Fuente Álamo; en 18 secciones vascas y navarras no tuvo ni un voto.',
        compara='Las secciones censales de España con al menos 300 electores en las generales de julio de 2023 (32.976), ordenadas por el porcentaje de Vox, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los nombres de barrio salen de las calles de cada sección (CartoCiudad) y de la prensa local, no de una relación oficial. El porcentaje de extranjeros es del padrón e incluye a quienes no pueden votar en unas generales. La renta por unidad de consumo es la del INE para 2023. Santa Cruz de Tenerife se excluye de los mínimos porque Vox no tuvo lista al Congreso. Los ceros que parecen un error de clasificación (el voto de un partido contado como «otros») se descartan como mínimos. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles de cada sección)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/la-carrera-hacia-el-29n-avanza-tras-despejarse-las-incognitas-de-las-coaliciones/', 'EFE, la carrera hacia el 29N avanza tras despejarse las incógnitas de las coaliciones (18-10-2026)'),
                 ('https://www.democrata.es/encuestas/elecciones-generales/abascal-elecciones-29-n-ultima-oportunidad-vox-remigracion/', 'Demócrata, Abascal y la «remigración» en los ejes de Vox para el 29N'),
                 ('https://theobjective.com/espana/politica/2026-05-18/alvise-cuarta-fuerza-el-ejido-andalucia/', 'The Objective, resultados de las autonómicas andaluzas en El Ejido (18-5-2026)'),
                 ('https://www.ceutaldia.com/articulo/politica/votos-generales-mesa-mesa-dibujan-mapa-desigualdad-2-ceutas-claridad/20230725004623266945.html', 'Ceuta al Día, el voto mesa a mesa en las generales de 2023 (25-7-2023)'),
                 ('https://www.publico.es/politica/ejido-saint-denis-ultraderecha-busca-andalucia.html', 'Público, De El Ejido a Saint-Denis (16-6-2022)'),
                 ('https://www.elindependiente.com/espana/2025/07/17/realidad-electoral-comarca-torre-pacheco-vox-duplica-voto-municipales-generales/', 'El Independiente, la realidad electoral de la comarca de Torre-Pacheco (17-7-2025)'),
                 ('https://upo.es/upotec/contenidos/noticias/2021/feb/26/un-estudio-liderado-por-la-upo-analiza-las-causas-/', 'Universidad Pablo de Olavide, estudio sobre las causas del voto a Vox en las andaluzas de 2018 (26-2-2021)'),
                 ('https://doi.org/10.1177/2053168019851680', 'Stuart J. Turnbull-Dugarte, Explaining the end of Spanish exceptionalism and electoral support for Vox, Research & Politics (2019)'),
                 ('https://www.elsaltodiario.com/almeria/mar-de-plastico-desierto-institucional', 'El Salto, Un mar de plástico en un desierto institucional (análisis de Carlos Balaguer)'),
                 ('https://rtvc.es/vox-no-presenta-lista-electoral-por-la-provincia-de-santa-cruz-de-tenerife/', 'RTVC, Vox no presenta lista electoral por la provincia de Santa Cruz de Tenerife (2023)'),
                 ('https://rtvc.es/rechazan-recursos-vox-por-candidatura-santa-cruz-de-tenerife/', 'RTVC, la Junta Electoral Central rechaza los recursos de Vox (2023)')],
        enlaces=[],
        lugar='El Ejido, Ceuta y País Vasco',
        foto=dict(src='img/actualidad/fotos/vox-cinco-barrios-el-ejido-ceuta.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones de España con más voto a Vox en 2023, en El Ejido, Ceuta y Fuente Álamo, y las cinco mayores sin ningún voto, en el País Vasco.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='sumar-cinco-pueblos-marinaleda', fecha='2026-10-20',
        titulo='Los 5 pueblos de España donde Sumar saca más del 52% de los votos: Marinaleda, Trebujena y una pedanía de Córdoba (y dónde no llega al 0,5%)', serie='bastiones',
        descripcion='En Marinaleda, Sumar sacó el 68,6% el 23J, su máximo en España. Las cinco secciones donde pasó del 50% están en Marinaleda, Trebujena y Santa Cruz (Córdoba). En el Príncipe de Ceuta o en Los Navalucillos no llegó al 0,5%.',
        compara='Las secciones censales de España con al menos 300 electores en las generales de julio de 2023 (32.976), ordenadas por el porcentaje de Sumar, y la evolución de las cinco primeras en las generales desde 2004, con IU, Podemos y Unidas Podemos como antecedentes.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los nombres de barrio salen de las calles de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une a Sumar con IU, Podemos y Unidas Podemos, que no son el mismo partido. La renta por unidad de consumo es la del INE para 2023. Los ceros que parecen un error de clasificación (el voto de un partido contado como «otros») se descartan como mínimos. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles de cada sección)'),
                 ('https://rtvc.es/frente-amplio-acuerda-designar-a-ada-colau-como-cabeza-de-lista-12-octubre-2026/', 'EFE (vía RTVC), Frente Amplio acuerda designar a Ada Colau como cabeza de lista (12-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/la-carrera-hacia-el-29n-avanza-tras-despejarse-las-incognitas-de-las-coaliciones/', 'EFE, la carrera hacia el 29N avanza tras despejarse las incógnitas de las coaliciones (18-10-2026)'),
                 ('https://www.infobae.com/espana/2026/10/17/asi-quedan-los-acuerdos-de-la-izquierda-para-las-elecciones-generales-del-29-n-estas-son-las-listas-a-la-izquierda-del-psoe-en-cada-comunidad-autonoma/', 'Infobae, así quedan los acuerdos de la izquierda para el 29N (17-10-2026)'),
                 ('https://www.publico.es/politica/gomez-reyes-recoge-antorcha-sanchez-gordillo-marinaleda.html', 'Público, Gómez Reyes recoge la antorcha de Sánchez Gordillo en Marinaleda (29-5-2023)')],
        enlaces=[],
        lugar='Marinaleda, Trebujena y Córdoba',
        foto=dict(src='img/actualidad/fotos/sumar-cinco-pueblos-marinaleda.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones de España con más voto a Sumar en 2023, todas en Andalucía, y las cinco con menos.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='bildu-cinco-pueblos-lizartza', fecha='2026-10-20',
        titulo='Los 5 pueblos donde EH Bildu saca más del 68% de los votos: de Lizartza a Goizueta (y los barrios de Getxo donde no llega al 1%)', serie='bastiones',
        descripcion='En Lizartza, EH Bildu sacó el 78,2% el 23J, y en Goizueta, el 77,7%. Pasó del 60% en 25 secciones, el doble que en 2019. En Neguri y Algorta, en Getxo, se quedó en el 0,3%.',
        compara='Las secciones censales con al menos 300 electores de el País Vasco y Navarra (2.112) en las generales de julio de 2023, ordenadas por el porcentaje de EH Bildu, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en el País Vasco y Navarra, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://www.moncloa.com/2026/10/16/eh-bildu-candidatos-generales-29n-3449751/', 'Moncloa.com, EH Bildu sitúa a Oskar Matute como referencia al Congreso y renueva su grupo para el 29N (16-10-2026)'),
                 ('https://www.ondavasca.com/el-pnv-afronta-las-generales-con-sagastizabal-lopez-vaquero-goia-y-urtaran/', 'Onda Vasca, el PNV afronta las generales con Sagastizabal, López, Vaquero, Goia y Urtaran (octubre de 2026)'),
                 ('https://silvanmiracle.com/informe/informe-postelectoral-elecciones-al-parlamento-vasco-2024/', 'Silván & Miracle, informe postelectoral de las elecciones al Parlamento Vasco de 2024')],
        enlaces=[],
        lugar='País Vasco y Navarra',
        foto=dict(src='img/actualidad/fotos/bildu-cinco-pueblos-lizartza.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto a EH Bildu en 2023, en Gipuzkoa, Navarra y Bizkaia, y las cinco con menos, en Getxo y la Ribera.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='pnv-cinco-pueblos-bermeo', fecha='2026-10-20',
        titulo='Los 5 pueblos donde el PNV saca más del 52% de los votos: Bermeo y la costa de Bizkaia (y los barrios de Errenteria donde no llega al 8%)', serie='bastiones',
        descripcion='En un barrio de Bermeo, el PNV sacó el 55,7% el 23J, su máximo; en 2019 tenía allí el 65%. Pasó del 40% en 75 secciones, frente a 315 en 2019. Sus mínimos, en Errenteria y Vitoria, rondan el 6%.',
        compara='Las secciones censales con al menos 300 electores de el País Vasco (1.671) en las generales de julio de 2023, ordenadas por el porcentaje de el PNV, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en el País Vasco, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://www.ondavasca.com/el-pnv-afronta-las-generales-con-sagastizabal-lopez-vaquero-goia-y-urtaran/', 'Onda Vasca, el PNV afronta las generales con Sagastizabal, López, Vaquero, Goia y Urtaran (octubre de 2026)'),
                 ('https://www.ondavasca.com/el-pnv-lidera-bizkaia-con-las-mayores-alcaldias-pero-bildu-pacta-para-arrebatarle-plazas/', 'Onda Vasca, el PNV lidera Bizkaia con las mayores alcaldías pero Bildu pacta para arrebatarle plazas (junio de 2023)'),
                 ('https://silvanmiracle.com/informe/informe-postelectoral-elecciones-al-parlamento-vasco-2024/', 'Silván & Miracle, informe postelectoral de las elecciones al Parlamento Vasco de 2024')],
        enlaces=[],
        lugar='País Vasco',
        foto=dict(src='img/actualidad/fotos/pnv-cinco-pueblos-bermeo.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto al PNV en 2023, en Bizkaia, y las cinco con menos, en Errenteria y Vitoria.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='cc-cinco-barrios-la-orotava', fecha='2026-10-20',
        titulo='Los 5 barrios de Canarias donde Coalición Canaria saca más del 42%: El Paso y La Orotava (y el Gáldar de su nuevo socio, donde no llega al 2%)', serie='bastiones',
        descripcion='En El Paso, CC sacó el 46,6% el 23J, su máximo; le siguen tres secciones de La Orotava. En Gáldar, el pueblo de Teodoro Sosa, que ahora encabeza la lista conjunta en Las Palmas, se quedó en el 1,5%.',
        compara='Las secciones censales con al menos 300 electores de Canarias (1.396) en las generales de julio de 2023, ordenadas por el porcentaje de Coalición Canaria, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en Canarias, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. Los datos agrupan en «otros» a Nueva Canarias y a los demás partidos sin sigla propia en el mapa. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://rtvc.es/primero-canarias-coalicion-canaria-cierran-acuerdo-candidatura-unidad-canaria-29-n-14-octubre-2026/', 'RTVC, Primero Canarias y Coalición Canaria cierran el acuerdo para la candidatura de unidad canaria el 29-N (14-10-2026)'),
                 ('https://rtvc.es/teodoro-sosa-seguiremos-siendo-nacionalistas-y-progresistas/', 'RTVC, Teodoro Sosa dice que la ruptura con NC es consecuencia del «hartazgo» de los personalismos (29-1-2025)')],
        enlaces=[],
        lugar='Canarias',
        foto=dict(src='img/actualidad/fotos/cc-cinco-barrios-la-orotava.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto a Coalición Canaria en 2023, en La Palma y Tenerife, y las cinco con menos, en Gran Canaria.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='erc-cinco-pueblos-blancafort-flix', fecha='2026-10-20',
        titulo='Los 5 pueblos donde ERC saca más del 35% de los votos: Blancafort, Flix y Tortosa (y el barrio de Tarragona donde no tuvo ni un voto)', serie='bastiones',
        descripcion='En Blancafort, ERC sacó el 44,7% el 23J, su máximo en Cataluña, y en Flix, el 41,9%. Pasó del 30% en 42 secciones, frente a 734 en 2019. En una sección de Campclar, en Tarragona, no tuvo ni un voto.',
        compara='Las secciones censales con al menos 300 electores de Cataluña (4.832) en las generales de julio de 2023, ordenadas por el porcentaje de ERC, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en Cataluña, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://rtvc.es/podemos-erc-pactan-colaborar-generales-ufian-montero-juntos-campana-12-octubre-2026/', 'EFE (vía RTVC), Podemos y ERC pactan colaborar en las generales con Rufián y Montero juntos en campaña (12-10-2026)'),
                 ('https://www.canal21ebre.com/esquerra-lamenta-que-el-congres-dels-diputats-es-quedi-sense-representants-ebrencs', 'Canal 21 Ebre, Esquerra lamenta que el Congrés es quedi sense representants ebrencs (24-7-2023)'),
                 ('https://ebredigital.cat/2024/05/13/12m-albert-salvado-a-terres-de-lebre-tampoc-hem-pogut-resistir-la-polaritzacio-entre-psc-i-puigdemont', 'EbreDigital, Albert Salvadó tras las autonómicas del 12 de mayo (13-5-2024)'),
                 ('https://www.3cat.cat/3catinfo/eleccions-generals-23j-2023/blancafort/municipi/09431602900/', '3Cat, resultados del 23J en Blancafort')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/erc-cinco-pueblos-blancafort-flix.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto a ERC en 2023, en Tarragona y Lleida, y las cinco con menos, en Tarragona, Barcelona y Sabadell.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='junts-cinco-pueblos-amer', fecha='2026-10-20',
        titulo='Los 5 pueblos donde Junts saca más del 40% de los votos: encabeza Amer, el de Puigdemont (y los barrios del área de Barcelona donde no tuvo ni un voto)', serie='bastiones',
        descripcion='En Amer, el pueblo de Puigdemont, Junts sacó el 44,8% el 23J, su máximo en Cataluña. Pasó del 30% en 128 secciones, frente a 310 en 2019. En 14 secciones, casi todas del cinturón de Barcelona, no tuvo ni un voto.',
        compara='Las secciones censales con al menos 300 electores de Cataluña (4.832) en las generales de julio de 2023, ordenadas por el porcentaje de Junts, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en Cataluña, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. Los ceros de Junts no muestran el salto de «otros» que delata un error de clasificación, así que se cuentan como reales. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://www.diariodeleon.es/nacional/261008/2099696/junts-confirma-miriam-nogueras-candidata-29n.html', 'EFE, Junts confirma a Míriam Nogueras como candidata para el 29N (8-10-2026)'),
                 ('https://www.ultimahora.es/noticias/comunidades/2023/07/16/1977289/puigdemont-situa-junts-trinchera-defendiendo-catalunya-pide-unir-fuerzas.html', 'Europa Press, Puigdemont sitúa a Junts en la «trinchera» defendiendo a Catalunya (16-7-2023)'),
                 ('https://www.articulo14.es/politica/puede-puigdemont-presentarse-a-las-elecciones-generales-del-29n-20261007.html', 'Artículo 14, ¿Puede Puigdemont presentarse a las elecciones generales del 29N? (7-10-2026)'),
                 ('https://www.articulo14.es/politica/puigdemont-planea-su-regreso-tras-el-29-n-con-sanchez-ya-exprimido-y-los-poderes-espanoles-derrotados-20261007.html', 'Artículo 14, Puigdemont planea su regreso tras el 29N (7-10-2026)')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/junts-cinco-pueblos-amer.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto a Junts en 2023, encabezadas por Amer, y las cinco mayores sin ningún voto, en el área de Barcelona.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='bng-cinco-pueblos-allariz', fecha='2026-10-20',
        titulo='El BNG solo ganó en una sección de España: los 5 pueblos donde más le votan, de Vilar de Santos a Allariz (y los de Ourense donde no llega al 2%)', serie='bastiones',
        descripcion='El BNG solo fue el más votado en una sección de España, en Allariz, por 0,2 puntos. Su máximo es el 35,1% de Vilar de Santos, donde ganó el PP. En A Lama, Boborás, Padrenda o Avión no llegó al 2%.',
        compara='Las secciones censales con al menos 300 electores de Galicia (2.135) en las generales de julio de 2023, ordenadas por el porcentaje de el BNG, y la evolución de las cinco primeras en las generales desde 2004.',
        limites='Son datos de secciones, no de personas: no dicen quién votó a quién ni por qué. Sin voto exterior, de modo que la participación sale más alta que la oficial. Las secciones de menos de 300 electores quedan fuera porque unos pocos votos mueven mucho el porcentaje. Los mínimos se buscan solo en Galicia, donde se presenta el partido. Los nombres de barrio salen de las calles y lugares de cada sección (CartoCiudad), no de una relación oficial. La serie histórica une al partido con sus antecesores, que no siempre llevaban la misma sigla. La renta por unidad de consumo es la del INE para 2023. El voto exterior (CERA), muy alto en el interior de Ourense, no se puede asignar a una sección y no está incluido. Límites de sección simplificados.',
        calculo='Porcentajes sobre votos válidos (candidaturas y blancos), como los oficiales de Interior; la participación, sobre el censo de residentes.',
        fuentes=[('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados electorales por mesa (Infoelectoral), vía pollspaindata. Sin voto exterior (CERA)'),
                 ('https://www.ine.es/experimental/atlas/experimental_atlas.htm', 'INE, Atlas de Distribución de Renta de los Hogares (renta, edad y extranjeros por sección), vía ineAtlas.data'),
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (estudios y paro)'),
                 ('https://www.cartociudad.es/', 'IGN, CartoCiudad (calles y lugares de cada sección)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/ponton-bng-confia-en-ganar-capacidad-de-negociacion-en-madrid-y-llama-a-rueda-a-convocar-autonomicas/', 'Europa Press (vía Infobae), Pontón (BNG) confía en ganar «capacidad de negociación» en Madrid (18-10-2026)')],
        enlaces=[],
        lugar='Galicia',
        foto=dict(src='img/actualidad/fotos/bng-cinco-pueblos-allariz.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las cinco secciones con más voto al BNG en 2023, en Ourense y A Coruña, y las cinco con menos, en el interior de Ourense y Pontevedra.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='barrios-donde-vota-menos-de-la-mitad', fecha='2026-10-21',
        titulo='A seis semanas del 29N: en 534 barrios de España no votó ni la mitad del censo, y tres de cada cuatro están entre los más pobres', serie='29n',
        descripcion='En las generales de 2023, la participación no llegó al 50% en 534 secciones censales; en 2004 eran 92. Están en la Cañada Real, el Polígono Sur, Los Asperones, La Mina, Son Gotleu, La Línea, Ceuta o Melilla. 407 están en el 10% de secciones con menos renta.',
        compara='Las 32.976 secciones censales de España con al menos 300 electores en las generales de julio de 2023, y en concreto las 534 donde la participación no llegó al 50%: dónde están, su renta, paro, estudios y edad (medianas), cómo votaron y cómo ha evolucionado su participación desde 2004.',
        limites='Son datos de secciones, no de personas: dicen cuánto se vota en cada barrio, no quién deja de votar ni por qué. La participación se calcula sobre el censo de residentes, sin voto exterior, y sale más baja de lo real si el censo incluye a personas que ya no viven en la sección; algunas secciones incluyen residencias u hospitales. La renta es la de 2023 y el paro y los estudios, los del censo de 2021. La serie desde 2004 usa las secciones actuales; en 2004 había datos de 29.035 secciones. Los nombres de barrio salen de OpenStreetMap y no son oficiales. La explicación de los casos turísticos (población de paso) es una hipótesis que no hemos podido comprobar.',
        calculo='Participación: votantes sobre el censo de residentes de cada sección. Voto: porcentaje sobre votos válidos, sumando votos de todas las secciones del grupo. Perfil: medianas por sección. Tramos de renta: diez grupos de igual número de secciones según la renta media por unidad de consumo.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (paro y estudios)'),
                 ('https://www.ine.es/dyngs/Prensa/es/EG2026.htm', 'INE, Censo electoral para las elecciones a Cortes Generales del 29 de noviembre de 2026 (9-10-2026)'),
                 ('https://www.diariodeleon.es/nacional/261005/2099347/29n-censo-votantes-sera-cerrado-1-agosto-decision-supremo-sobre-ley-nietos.html', 'Europa Press vía Diario de León, el censo del 29N será el cerrado el 1 de agosto (5-10-2026)'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap (Nominatim), nombres de barrio de cada sección'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)'),
                 ('https://revistas.um.es/sh/article/download/451231/291101/1533611', 'Manuel Trujillo-Carmona, Exclusión social y abstención electoral en barrios de alta población gitana, Sociología Histórica 10 (2020), pp. 176 y 179'),
                 ('https://www.equaltimes.org/los-barrios-pobres-cada-vez-votan', 'María José Carmona, Los barrios pobres cada vez votan menos… y a nadie le importa, Equal Times (26-4-2019)'),
                 ('https://www.elespanol.com/malaga/20260518/vox-dispara-barrios-pobres-malaga-gana-zonas-vulnerables-sube-puntos/1003744249420_0.html', 'El Español (Alba Rosado), los barrios vulnerables de Málaga en las andaluzas (18-5-2026)'),
                 ('https://www.eldebate.com/espana/andalucia/sevilla/20260522/fortin-rojo-andalucia-voto-fiel-psoe-esta-tres-mil-viviendas_420152.html', 'El Debate, las Tres Mil Viviendas en las andaluzas (22-5-2026)'),
                 ('https://www.datadista.com/elecciones-29n-los-barrios-pobres-de-las-grandes-ciudades-doblan-la-abstencion-de-los-barrios-ricos/', 'Datadista (Antonio Delgado), los barrios pobres de las grandes ciudades doblan la abstención de los ricos (18-10-2026)'),
                 ('https://www.csjd.es/sites/default/files/ckfinder/userfiles/files/CSJD_Declaracion_Ambiental_2022_V2_231009_SELLADA.pdf', 'Centro San Juan de Dios de Ciempozuelos, Declaración ambiental 2022 (dirección del centro)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/barrios-donde-vota-menos-de-la-mitad.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las 534 secciones censales de España donde votó menos de la mitad del censo en las generales de 2023, coloreadas por el partido que ganó.',
                  fuente='Ministerio del Interior e INE'),
    ),
    dict(
        slug='salarios-pensiones-ayudas-espana', fecha='2026-10-21',
        actualizado='2026-10-23 23:15',
        titulo='Ante el 29N: del Polígono Sur a la Cañada Real, en 78 de los 93 barrios donde más pesan las ayudas sociales no votó ni la mitad', serie='29n',
        descripcion='Datos de Hacienda vía el INE, sección a sección: en esos 93 barrios las prestaciones pasan del 20% de la renta. En el quinto de secciones donde más pesan se votó 9,6 puntos menos y el PSOE sacó 10 más que el PP; donde más pesan las pensiones, casi igual que en el resto.',
        compara='La composición de la renta bruta de 2023 (salarios, pensiones, prestaciones por desempleo, otras prestaciones y otros ingresos) de 33.260 secciones censales de España, cruzada con la participación y el voto en las generales de julio de 2023; por secciones, por grupos de secciones y por provincias.',
        limites='Son datos de secciones, no de personas. La renta por fuente sale de datos tributarios y de registros de prestaciones que agrega el INE, y no incluye las rentas que no constan en ellos. Porcentajes sobre la renta bruta. En el País Vasco el INE no desglosa pensiones ni prestaciones (1.716 secciones) y faltan otras 1.436 secciones, casi todas rurales. «Con derecho a voto» es una estimación: adultos residentes menos censo electoral. El modelo estadístico describe asociaciones, no causas; el peso del paro en la renta y el paro del censo miden casi lo mismo. Los nombres de barrio salen de OpenStreetMap y no son oficiales. Sin voto exterior.',
        calculo='Participación sobre el censo; voto por partido sobre voto válido, ponderado por votantes. Peso de cada fuente en un grupo de secciones o en una provincia: ponderado por la renta total de cada sección. Grupos: quintos y deciles de secciones según el peso de cada fuente. Modelo: regresión ponderada con variables estandarizadas, validación fuera de muestra por grupos de municipios y una versión solo dentro de cada municipio.',
        fuentes=[('https://www.ine.es/jaxiT3/Tabla.htm?t=30825', 'INE, Atlas de Distribución de Renta de los Hogares: distribución por fuente de ingresos, por sección censal (tabla 30825), año 2023'),
                 ('https://ine.es/metodologia/metodologia_adrh.pdf', 'INE, metodología del Atlas de Distribución de Renta de los Hogares (definición de cada fuente)'),
                 INTERIOR, INE,
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (paro y estudios)'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap (Nominatim), nombres de barrio de cada sección'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/la-carrera-hacia-el-29n-avanza-tras-despejarse-las-incognitas-de-las-coaliciones/', 'EFE, la carrera hacia el 29N avanza tras despejarse las incógnitas de las coaliciones (18-10-2026)'),
                 ('https://revistas.um.es/sh/article/download/451231/291101/1533611', 'Manuel Trujillo-Carmona, Exclusión social y abstención electoral en barrios de alta población gitana, Sociología Histórica 10 (2020)'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/salarios-pensiones-ayudas-espana.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un bloque de pisos, una declaración de la renta, monedas, una madre con su hijo, un pensionista, el mapa de España y una urna: un collage.'),
    ),
    dict(
        slug='municipios-izquierda-1977-derecha-2023', fecha='2026-10-20',
        titulo='Con el PSOE andaluz en mínimos: Sevilla, Jerez y otros 170 municipios que votaron a la izquierda en todas las generales de 1977 a 2008 dieron en 2023 más votos a PP y Vox', serie='29n',
        descripcion='En 172 municipios con 2,23 millones de electores, la izquierda estatal sumó más que la derecha en las diez generales de 1977 a 2008 y en 2023 fue al revés: Sevilla, Jerez, Móstoles, Algeciras, Chiclana. 115 cambiaron en 2011. El camino contrario lo han hecho 147, casi todos pequeños.',
        compara='Los 7.845 municipios con datos de las 16 elecciones generales de 1977 a 2023, con el voto sumado en dos bloques: izquierda estatal (PSOE y PCE, IU, Podemos o Sumar) y derecha estatal (UCD, CDS, AP y PP, Ciudadanos, UPyD y Vox). Feudo: un bloque suma más en las diez generales de 1977 a 2008. Vuelco: el otro bloque suma más en 2023.',
        limites='Los bloques son una simplificación: UCD era un partido de centro, y sumarlo a AP en 1977 y 1979 agranda la derecha estatal de entonces. Los partidos nacionalistas y regionalistas (CiU y Junts, ERC, PNV, EH Bildu, BNG, CC, PA y otros) no cuentan en ningún bloque. UPN se cuenta con el PP en todas las elecciones. Quedan fuera los municipios sin datos en alguna de las 16 elecciones (entre ellos unos 139 que faltan en 1982 y los creados después de 1977). Sin voto exterior. Un municipio no son sus votantes: el censo de 2023 no es el de 1977.',
        calculo='Porcentaje de cada bloque sobre los votos a candidaturas en cada municipio y elección. Un municipio cambia de bloque cuando el otro bloque suma más votos.',
        fuentes=[INTERIOR,
                 ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/', 'Ministerio del Interior, resultados por municipio de las generales de 1977, 1979 y 1982 (Infoelectoral)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/18/la-carrera-hacia-el-29n-avanza-tras-despejarse-las-incognitas-de-las-coaliciones/', 'EFE, la carrera hacia el 29N avanza tras despejarse las incógnitas de las coaliciones (18-10-2026)'),
                 ('https://www.eldebate.com/espana/andalucia/20261019/psoe-sigue-perdiendo-fuerza-andalucia-montero-lider-peor-valoracion_471036.html', 'El Debate (Roberto Marbán), el barómetro del Centra de octubre (19-10-2026)'),
                 (INFOBAE_MONTERO, 'Europa Press vía Infobae, Montero descarta ir en las listas del PSOE el 29N (6-10-2026)'),
                 ('https://rio.upo.es/rest/api/core/bitstreams/a6bcd1fc-7296-44f6-9d41-3dd063e34bda/content', 'José Manuel Trujillo y Juan Montabes, Las elecciones autonómicas andaluzas de 2018: un resultado electoral imprevisto de consecuencias políticas innovadoras en la gobernabilidad (2019), repositorio de la Universidad Pablo de Olavide')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/municipios-izquierda-1977-derecha-2023.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Los 172 municipios donde la izquierda estatal sumó más en todas las generales de 1977 a 2008 y la derecha estatal sumó más en 2023, y la evolución de los dos bloques en Sevilla.',
                  fuente='Ministerio del Interior'),
    ),
    dict(
        slug='calle-que-parte-madrid', fecha='2026-10-21',
        titulo='A cinco semanas del 29N: en la calle de los Hermanos García Noblejas, en Madrid, PP y PSOE se cambian de acera 12 veces, y el PP siempre gana en el lado con más renta', serie='29n',
        descripcion='En Madrid, una de cada cinco parejas de secciones censales vecinas eligió un ganador distinto en 2023. Las calles donde más se repite son Hermanos García Noblejas, General Ricardos, la avenida de las Águilas y Hacienda de Pavones. En Sinesio Delgado, entre Tetuán y Fuencarral, el salto llega a 27 puntos.',
        compara='Las 6.112 parejas de secciones censales contiguas de la ciudad de Madrid (al menos 80 metros de límite común y 400 electores cada una) en las generales de 2023, con la calle que las separa y su renta por unidad de consumo de 2023.',
        limites='Son datos de secciones, no de personas, y no explican por qué cada lado vota distinto. La calle de cada límite sale de un geocodificador en cinco puntos y puede no coincidir con el límite en todos sus metros; las cuatro calles con plano se han revisado a mano. Algunos tramos se decidieron por menos de dos puntos. La renta de las secciones más ricas está topada en 58.752 euros. Sin voto exterior.',
        calculo='Voto: porcentaje sobre votos válidos. Pareja de secciones vecinas: comparten al menos 80 metros de límite (con 12 metros de tolerancia) y tienen al menos 400 electores cada una. Calle: la que devuelve el geocodificador inverso de CartoCiudad en al menos tres de cinco puntos del límite común. Lado del PP más rico: la sección donde ganó el PP tiene más renta por unidad de consumo que la de enfrente.',
        fuentes=[INTERIOR, INE,
                 ('https://www.cartociudad.es/', 'CartoCiudad (IGN), geocodificador inverso para el nombre de cada calle'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap, callejero y nombres de barrio (Nominatim)'),
                 ('https://www.elsaltodiario.com/desigualdad/madrid-no-es-ciudad-todos-gatos', 'El Salto, Madrid ya no es ciudad para todos los «gatos» (2-9-2020)'),
                 ('https://valenciaplaza.com/valenciaplaza/maroto-inicia-carrera-ayuntamiento-madrid-objetivo-reducir-desigualdad', 'Europa Press vía Valencia Plaza, Maroto inicia la carrera hacia el Ayuntamiento de Madrid (4-2-2023)'),
                 ('https://www.eldiario.es/madrid/somos/foto-desigualdad-madrid-ricos-tres-distritos-no-llegan-mes-ganan-doble-gastan_1_13137595.html', 'elDiario.es, informe de Más Madrid sobre la desigualdad (14-4-2026)'),
                 ('https://diario.madrid.es/blog/2020/07/03/sures-un-plan-vivo-que-cambiara-los-distritos-del-sur-y-del-este-de-madrid/', 'Ayuntamiento de Madrid, Plan SURES (3-7-2020)'),
                 ('https://www.eldiario.es/madrid/somos/estudio-descubre-influye-voto-madrid-efecto-alquiler-barrio-vivas_1_12961596.html', 'elDiario.es, Álvaro Sánchez García sobre alquiler y voto en Madrid (9-2-2026)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2-4-2023)')],
        enlaces=[],
        lugar='Madrid',
        foto=dict(src='img/actualidad/fotos/calle-que-parte-madrid.jpg', ancho=1280, alto=720, grafico=True,
                  pie='El mapa electoral de esta web en la calle de los Hermanos García Noblejas: en azul, las secciones donde ganó el PP en las generales de 2023; en rojo, donde ganó el PSOE. Más intenso cuanto mayor es el porcentaje del ganador.',
                  fuente='Ministerio del Interior; callejero © OpenStreetMap'),
    ),
    dict(
        slug='barrios-pobres-derecha-ricos-izquierda', fecha='2026-10-20',
        titulo='Vox busca el voto de los barrios obreros: en la Región de Murcia, nueve de cada diez secciones pobres ya votan más a PP y Vox que a PSOE y Sumar', serie='29n',
        descripcion='De las 3.289 secciones más pobres de España, 1.089 votaron más a PP y Vox en 2023, sobre todo en Murcia, Almería y Alicante. De las 3.290 más ricas, 924 votaron más a PSOE y Sumar: casi todas en Cataluña y el País Vasco, y un centenar en el centro de Madrid.',
        compara='Las 32.900 secciones censales con al menos 300 electores y dato de renta en las generales de 2023, agrupadas en diez tramos de igual tamaño según la renta media por unidad de consumo. Se comparan dos bloques: PP y Vox frente a PSOE y Sumar. Excepciones: secciones del tramo más pobre donde PP y Vox suman más, y del más rico donde PSOE y Sumar suman más; por provincias y, dentro de las 65 ciudades de al menos 75.000 electores, con los tramos de cada ciudad.',
        limites='Son datos de secciones, no de personas: dicen cómo votan los barrios con más o menos renta, no cómo votan los ricos o los pobres. Los bloques dejan fuera a Junts, ERC, PNV, EH Bildu, BNG, CC y otros, que en sus territorios reúnen buena parte del voto: una sección rica de Cataluña o el País Vasco puede votar más a PSOE y Sumar que a PP y Vox y aun así ganar un partido nacionalista. La renta es la de 2023; el paro y la población extranjera, del censo de 2021 y del padrón. Sin voto exterior. Los nombres de barrio salen de OpenStreetMap y no son oficiales. La relación con la agricultura intensiva es una explicación de un investigador, no algo que midan estos datos.',
        calculo='Voto: porcentaje sobre votos válidos. Bloques: PP+Vox y PSOE+Sumar (en Cataluña, PSC y Sumar-Comuns). Tramos de renta: diez grupos de igual número de secciones según la renta media por unidad de consumo; en la comparación por ciudad, el 10% de secciones más pobre y más rico de cada ciudad.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/censos2021/C2021_Indicadores.csv', 'INE, Censo de Población y Viviendas 2021, indicadores por sección censal (paro)'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap (Nominatim), nombres de barrio de cada sección'),
                 ('https://www.diariodeleon.es/nacional/261012/2099996/abascal-promete-recuperar-ciudadano.html', 'EFE vía Diario de León, Abascal promete recuperar «el poder para el ciudadano» (12-10-2026)'),
                 ('https://www.vozpopuli.com/espana/madrid/vox-encuentra-en-madrid-su-gran-caladero-de-afiliaciones-una-de-cada-cuatro-se-producen-en-la-region.html', 'Vozpópuli (Mario Cortijo), Vox encuentra en Madrid su gran caladero de afiliaciones (12-10-2026)'),
                 ('https://www.eldiario.es/murcia/politica/racismo-campo-redes-sociales-metamorfosis-torre-pacheco-caceria-ultras-mitin-vox_1_12465316.html', 'elDiario.es, Francisco Javier López Carvajal sobre Torre Pacheco y el voto a Vox (2025)'),
                 ('https://revistas.ucm.es/index.php/POSO/article/view/75974', 'Francisco Javier López Carvajal y Alberto Mora, artículo en Política y Sociedad (2022)'),
                 ('https://www.elsaltodiario.com/almeria/mar-de-plastico-desierto-institucional', 'El Salto, Un mar de plástico en un desierto institucional (análisis de Carlos Balaguer)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2023)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/barrios-pobres-derecha-ricos-izquierda.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Secciones del 10% más pobre de España donde PP y Vox suman más que PSOE y Sumar, y del 10% más rico donde pasa lo contrario. Generales de 2023.',
                  fuente='Ministerio del Interior e INE'),
    ),
    dict(
        slug='capitales-partidas-por-barrios', fecha='2026-10-22',
        actualizado='2026-10-23 23:15',
        titulo='Sevilla vota por barrios y Lugo, mezclada: el índice que mide qué capitales están partidas por el voto', serie='29n',
        descripcion='El índice de Moran del voto por sección censal en las 52 capitales: Ceuta, Sevilla, Barcelona, Madrid, Bilbao, Toledo y Granada votan por bloques de barrios; Soria, Lugo y Cuenca, mezcladas. Lo que más se repite es la distancia de renta entre barrios.',
        compara='Las 10.542 secciones censales urbanas (1.000 habitantes por km² o más) de las 50 capitales de provincia, Ceuta y Melilla en las generales de 2023, con la renta por unidad de consumo de 2023 y el índice de Gini y la ratio P80/P20 de cada ciudad. La clasificación se repite con las generales de 2008 a 2019.',
        limites='Son datos de secciones, no de personas, y no explican por qué se agrupa el voto. El índice de Moran depende de cómo dibuja el INE las secciones, de qué se considera vecino y del número de secciones: sube con el tamaño de la ciudad. En Soria (20 secciones urbanas) no es estadísticamente significativo. En Cataluña y el País Vasco la diferencia PP−PSOE no es el eje principal del voto. El peso de la vivienda unifamiliar se aproxima con los alquileres declarados (SERPAVI), sin País Vasco ni Navarra. La renta de las secciones más ricas está topada en 58.752 euros. Con 52 ciudades, las regresiones tienen pocos grados de libertad. Sin voto exterior.',
        calculo='Índice de Moran global de la diferencia de voto PP−PSOE (sobre voto válido) por sección, con vecindad de tipo reina (secciones que comparten lado o vértice) normalizada por filas y 9.999 permutaciones; robustez con vecindad por lados, con los seis vecinos más cercanos, con todas las secciones y con el eje principal de cada ciudad. Índice de Duncan entre PP+Vox+Cs y PSOE+Sumar con votos por sección. Peso del distrito: parte de la varianza del margen entre secciones explicada por el distrito censal. Regresiones de la ciudad: MCO con el logaritmo de la población, errores robustos y, como comprobación, efectos fijos de comunidad autónoma con errores agrupados por comunidad.',
        fuentes=[INTERIOR, INE,
                 ('https://www.ine.es/prodyser/cartografia/seccionado_2023.zip', 'INE, cartografía digitalizada de secciones censales (1 de enero de 2023)'),
                 ('https://www.ine.es/jaxiT3/Tabla.htm?t=37677', 'INE, Atlas de Distribución de Renta de los Hogares: índice de Gini y distribución P80/P20 por municipio (2023)'),
                 ('https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi', 'Ministerio de Vivienda, SERPAVI 2011-2024 (alquileres declarados de pisos y viviendas unifamiliares)'),
                 ('https://www.eldiario.es/sevilla/poligono-sur-pajaritos-repiten-barrios-pobres-espana_1_10225697.html', 'elDiario.es con datos consultados por Europa Press, Polígono Sur y Los Pajaritos (22-5-2023)'),
                 ('https://www.openstreetmap.org/', 'OpenStreetMap (Nominatim), nombres de calle y barrio'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)'),
                 ('https://www.revistas.ufrj.br/index.php/EspacoAberto/article/view/61567', 'Carme Bellet y Gonzalo Andrés, Manifestaciones actuales de la segregación residencial en ciudades medias españolas, Espaço Aberto (2024)'),
                 ('https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html', 'elDiario.es, entrevista a Toni Rodon (2-4-2023)')],
        enlaces=[],
        lugar='España',
    ),
]


# Segunda República (1933 y 1936), con los datos del Atlas Electoral de la UPF integrados en el mapa
PIEZAS += [
    dict(
        slug='republica-mapa-1936-hoy', fecha='2026-10-22',
        titulo='El mapa de 1936 apenas se parece al de hoy: 1.545 pueblos que votaron a las derechas eligen ahora a la izquierda', serie='historia',
        descripcion='De 7.494 municipios con datos de las generales de 1936 y 2023, 2.741 han cambiado de bloque. 1.545 pasaron de las derechas a la izquierda, sobre todo en Cataluña, Navarra y el País Vasco; 1.196, del Frente Popular a la derecha, entre ellos Madrid, Sevilla, Málaga, València y Zaragoza.',
        compara='Los 7.494 municipios actuales con datos de las generales del 16 de febrero de 1936 y del 23 de julio de 2023. En 1936, el Frente Popular frente a las derechas (la CEDA y sus aliados, con el Front Català d\'Ordre en Cataluña). En 2023, la izquierda (PSOE, Sumar, ERC, EH Bildu y BNG) frente a la derecha y el centroderecha (PP con UPN, Vox, Junts, PNV y Coalición Canaria).',
        limites='Los bloques de 1936 y los de 2023 no son los mismos partidos: comparamos coaliciones de entonces con sumas de partidos de ahora. Contar a Junts, PNV y CC con la derecha es una decisión; si solo se cuentan PP y Vox, los municipios que pasan de las derechas a la izquierda son 1.662. En 1936 se votaba con listas abiertas y varios votos por elector; el peso de cada bloque es su parte de los votos a candidatos. El censo de 1936 era de mayores de 23 años y el de 2023, de 18. Faltan Cuenca y Pontevedra en 1936 y hay huecos en otras provincias; los municipios desaparecidos se suman al actual en que se integraron, según el INE. Los datos de 1936 son los del Atlas, que no resuelven el debate sobre irregularidades en algunas provincias. Sin voto exterior en 2023.',
        calculo='Bloque ganador: el que suma más porcentaje de voto en el municipio (en 1936, sobre los votos a candidatos; en 2023, sobre los votos a candidaturas). Se excluyen 12 empates. Correlación de Pearson entre el porcentaje del Frente Popular en 1936 y el de la izquierda en 2023, municipio a municipio. Participación: votantes sobre censo de cada elección, en los 4.300 municipios con las dos cifras.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://www.ine.es/intercensal/', 'INE, Alteraciones de los municipios en los Censos de Población desde 1842'),
                 ('https://es.ara.cat/politica/votaron-pueblo-elecciones-1936_1_5730095.html', 'Aleix Moldes, «¿Qué votaron en tu pueblo en 1936? El mapa electoral de la Segunda República», Ara (8-5-2026)'),
                 ('https://ojs.ehu.eus/index.php/HC/article/download/19831/18135/76711', 'Eduardo González Calleja y Francisco Sánchez Pérez, «Revisando el revisionismo. A propósito del libro 1936. Fraude y violencia en las elecciones del Frente Popular», Historia Contemporánea 58 (2018)'),
                 ('https://proapi.planetadelibros.com/descargas/sala-prensa-libro/sinopsis-y-biografia/244062/1936-fraude-y-violencia-en-las-elecciones-del-frente-popular.pdf', 'Espasa, sinopsis de 1936. Fraude y violencia en las elecciones del Frente Popular, de Manuel Álvarez Tardío y Roberto Villa García (2017)'),
                 ('https://www.marxists.org/espanol/tematica/mujer/autores/campoamor/1931/oct01.htm', 'Clara Campoamor, discurso en las Cortes del 1 de octubre de 1931'),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_1936', 'Wikipedia, «Elecciones generales de España de 1936» (consultada el 22-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='lorca-fuente-vaqueros-viznar-1936', fecha='2026-10-23',
        titulo='Fuente Vaqueros, el pueblo de Lorca, dio el 77,5 % al Frente Popular; Víznar, donde lo mataron, el 63 % a las derechas', serie='historia',
        descripcion='Las urnas de febrero de 1936 en la provincia de Granada, pueblo a pueblo: la vega de Lorca votó a la izquierda y la sierra donde lo fusilaron, a las derechas. Unas elecciones que se anularon y se repitieron en mayo, y lo que queda de aquel mapa en 2023.',
        compara='Los municipios de la provincia de Granada en las generales del 19 de noviembre de 1933, del 16 de febrero de 1936 (primera vuelta, anulada) y del 23 de julio de 2023. En 1936, el Frente Popular frente a las derechas; en 2023, la izquierda (PSOE y Sumar) frente a la derecha (PP y Vox).',
        limites='Las elecciones de febrero de 1936 en Granada se anularon por injerencias del gobernador civil y se repitieron en mayo sin las derechas; el Atlas solo recoge la votación de febrero. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector; el peso de cada bloque es su parte de los votos a candidatos. La participación de 1936 en Granada es una estimación y no se usa. Sin datos de 1933 en Granada capital y Víznar. En 1936, Pinos Puente incluye Valderrubio (Asquerosa), segregado en 2013. El voto de un municipio no dice nada de los crímenes que se cometieron en él después. Sin voto exterior en 2023.',
        calculo='Bloque ganador: el que suma más porcentaje de voto en el municipio. Media provincial de 1933 y 1936 ponderada por el censo, y de 2023 por los votantes. Correlación de Pearson entre el porcentaje del Frente Popular en 1936 y el de la izquierda en 2023, municipio a municipio, en los 167 municipios comparables.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://www.cronica.com.mx/cultura/2026/08/17/la-busqueda-de-los-restos-de-garcia-lorca-una-historia-sin-final-que-suma-capitulos/', 'EFE, «La búsqueda de los restos de García Lorca, una historia sin final que suma capítulos» (17-8-2026)'),
                 ('https://www.lacapitalmdp.com/ian-gibson-encontrar-a-lorca-seria-un-simbolo-de-reconciliacion-para-espana/', 'EFE (Magdalena Tsanis), entrevista a Ian Gibson (23-5-2026)'),
                 ('https://semanariouniversidad.com/suplementos/los-dialogos-caricaturista-salvaje/', 'Luis Bagaría, «Diálogos de un caricaturista salvaje», conversación con Federico García Lorca, El Sol (10-6-1936), transcripción'),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_1936', 'Wikipedia, «Elecciones generales de España de 1936» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Valderrubio', 'Wikipedia, «Valderrubio» (consultada el 23-10-2026)')],
        enlaces=[],
        lugar='Granada',
        foto=dict(src='img/actualidad/fotos/lorca-fuente-vaqueros-viznar-1936.jpg', ancho=1280, alto=720,
                  pie='Federico García Lorca en la Huerta de San Vicente, Granada, en 1932 (autor anónimo, Museo Reina Sofía, dominio público), y cola de votantes en Granada el 16 de febrero de 1936.',
                  url='https://commons.wikimedia.org/wiki/File:Granada,_general_elections_of_1936.jpg', credito='Torres y Chinchilla (derecha), dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='pueblos-guerra-civil-voto-1936', fecha='2026-10-23',
        titulo='Gernika votó al PNV en 1936 y volvió a hacerlo en 2023, por 11 votos; Belchite tiene hoy menos electores que antes de su batalla', serie='historia',
        descripcion='Gernika, Badajoz, Paracuellos, Brunete y Belchite antes de la guerra: así votaron el 16 de febrero de 1936 y así votan ahora. Badajoz votó al Frente Popular y Paracuellos, a las derechas; Brunete vota casi igual que entonces, y Belchite ha perdido electores.',
        compara='Cinco municipios conocidos por la Guerra Civil (Gernika-Lumo, Badajoz, Paracuellos de Jarama, Brunete y Belchite) en las generales del 19 de noviembre de 1933, del 16 de febrero de 1936 y del 23 de julio de 2023.',
        limites='El voto de un municipio no explica lo que pasó en él durante la guerra: las víctimas de Paracuellos venían de las cárceles de Madrid y Gernika fue bombardeada por aviones alemanes e italianos. En 1936 se votaba con listas abiertas y varios votos por elector; el peso de cada candidatura es su parte de los votos a candidatos. En 1936, Gernika incluye los pueblos que entonces formaban su municipio (Ajangiz, Arratzu, Kortezubi, Forua, Murueta y Nabarniz); en 2023, solo Gernika-Lumo. El censo de 1936 era de mayores de 23 años y el de 2023, de 18. Las cifras de víctimas son estimaciones de historiadores y varían mucho. Sin voto exterior en 2023.',
        calculo='Porcentaje de voto de cada candidatura (1936) y de cada partido (2023) en el municipio; electores del censo de cada elección. Diferencia de votos entre PNV y EH Bildu en Gernika-Lumo en 2023, con los resultados por mesa.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://commons.wikimedia.org/wiki/File:The_tragedy_of_Guernica_(George_Steer).jpg', 'George Steer, «The tragedy of Guernica. Town destroyed in air attack», The Times (28-4-1937)'),
                 ('https://orain.eus/es/politica/2026/04/26/gernika-recuerda-las-victimas-del-bombardeo-en-su-89-aniversario/', 'EITB, «Gernika recuerda a las víctimas del bombardeo en su 89 aniversario» (26-4-2026)'),
                 ('https://www.elsaltodiario.com/memoria-historica/se-cumplen-85-anos-de-la-masacre-de-badajoz-contada-por-el-periodista-jay-allen', 'Félix Población, «Se cumplen 85 años de la masacre de Badajoz, contada por el periodista Jay Allen», El Salto (14-8-2021)'),
                 ('https://en.wikipedia.org/wiki/Badajoz_massacre', 'Wikipedia, «Badajoz massacre» (consultada el 23-10-2026)'),
                 ('https://en.wikipedia.org/wiki/Paracuellos_massacres', 'Wikipedia, «Paracuellos massacres» (consultada el 23-10-2026)'),
                 ('https://en.wikipedia.org/wiki/Battle_of_Brunete', 'Wikipedia, «Battle of Brunete» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Brunete', 'Wikipedia, «Brunete» (consultada el 23-10-2026)'),
                 ('https://www.elobservador.com.uy/espana/bbc-news-mundo/la-pompeya-espanola-el-pueblo-que-quedo-congelado-el-tiempo-sufrir-uno-los-asedios-mas-sangrientos-la-guerra-civil-n6012193', 'BBC News Mundo, «La Pompeya española: el pueblo que quedó congelado en el tiempo» (10-8-2025)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pueblos-guerra-civil-voto-1936.jpg', ancho=1280, alto=720,
                  pie='Gernika en ruinas tras el bombardeo del 26 de abril de 1937.',
                  url='https://commons.wikimedia.org/wiki/File:El_poblado_de_Guernica_en_ruinas_tras_el_bombardeo.jpg', credito='Autor anónimo, dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='mujeres-1933-frente-popular-1936', fecha='2026-10-23',
        titulo='Las mujeres votaron por primera vez en 1933 y ganaron las derechas; en 1936 volvieron a votar y 888 pueblos se pasaron al Frente Popular', serie='historia',
        descripcion='A las mujeres se les echó la culpa de la victoria de las derechas en 1933. En febrero de 1936, con las mismas votantes, 888 municipios pasaron de las derechas al Frente Popular y 393 hicieron el camino contrario. Lo que cambió fue la oferta: la izquierda unida y el centro hundido.',
        compara='Los 6.690 municipios actuales con datos de las generales del 19 de noviembre de 1933 (primera vuelta) y del 16 de febrero de 1936. En 1933, las izquierdas (PSOE, comunistas, ERC y republicanos de izquierda) frente a las derechas (con la Lliga); en 1936, el Frente Popular frente a las derechas.',
        limites='El Atlas no separa el voto por sexo: no dice a quién votaron las mujeres. En 1933 sumamos candidaturas de izquierda que fueron por separado y dejamos fuera al centro. En 1933 hubo segunda vuelta en algunas provincias; usamos la primera. Los resultados de febrero de 1936 en Granada y Cuenca se anularon y se repitieron en mayo. Listas abiertas y varios votos por elector: el peso de cada bloque es su parte de los votos a candidatos. La participación solo se conoce en las dos elecciones en 3.162 municipios. Se excluyen los empates.',
        calculo='Bloque ganador: el que suma más porcentaje de voto en el municipio. Media ponderada por el censo de cada elección. Participación: votantes sobre censo.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 ('https://es.ara.cat/cultura/falsos-topicos-sufragio-femenino-espana_130_4134771.html', 'Sílvia Marimon, «Los falsos tópicos del sufragio femenino en España», Ara (1-10-2021)'),
                 ('https://www.marxists.org/espanol/tematica/mujer/autores/campoamor/1931/oct01.htm', 'Clara Campoamor, discurso en las Cortes del 1 de octubre de 1931'),
                 ('https://es.wikipedia.org/wiki/Clara_Campoamor', 'Wikipedia, «Clara Campoamor» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Elecciones_generales_de_Espa%C3%B1a_de_1933', 'Wikipedia, «Elecciones generales de España de 1933» (consultada el 23-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/mujeres-1933-frente-popular-1936.jpg', ancho=1280, alto=720,
                  pie='Mesa electoral en las escuelas del ayuntamiento de Éibar en el referéndum del Estatuto vasco, el 5 de noviembre de 1933, presidida por Pastora Medina Corta.',
                  url='https://commons.wikimedia.org/wiki/File:01_eibar.jpg', credito='Indalecio Ojanguren, CC BY-SA 3.0, Diputación Foral de Gipuzkoa, vía Wikimedia Commons'),
    ),
    dict(
        slug='fieles-1936-izquierda-derecha', fecha='2026-10-23',
        titulo='256 pueblos han votado a la izquierda en 1936 y en las 16 generales de la democracia; 1.610, siempre a la derecha', serie='historia',
        descripcion="L'Hospitalet, Gijón, Sabadell y Dos Hermanas votaron al Frente Popular en 1936 y a la izquierda en todas las generales desde 1977; Burgos, Ávila y Zamora, a la derecha. Los fieles a la derecha son aldeas castellanas que han perdido electores; los de la izquierda, ciudades obreras y pueblos jornaleros.",
        compara='Los 7.365 municipios actuales con datos de las generales de febrero de 1936 y de las 16 generales de 1977 a 2023. En 1936, el Frente Popular frente a las derechas. Desde 1977, la izquierda (PSOE, PCE, IU, Podemos y Sumar, ERC, EH Bildu y BNG) frente a la derecha y el centroderecha (UCD, AP y PP, CDS, Ciudadanos, UPyD, Vox, CiU y Junts, PNV y CC).',
        limites='Los bloques no son los mismos partidos en 1936 y después: comparamos coaliciones de entonces con sumas de partidos de ahora. Contar a UCD, CDS, Ciudadanos, CiU, Junts, PNV y CC con la derecha es una decisión. Se excluyen los 127 municipios donde en 1936 ganó el PNV o el centro, y los empates. Faltan casi todos los municipios de Cuenca y Pontevedra en 1936. Los municipios desaparecidos se suman al actual en que se integraron. El censo de 1936 era de mayores de 23 años.',
        calculo='Bloque ganador en cada elección: el que suma más porcentaje de voto en el municipio. Fiel: el mismo bloque en las 17 elecciones. Electores: censo de 1936 y de 2023.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://es.ara.cat/politica/votaron-pueblo-elecciones-1936_1_5730095.html', 'Aleix Moldes, «¿Qué votaron en tu pueblo en 1936? El mapa electoral de la Segunda República», Ara (8-5-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/fieles-1936-izquierda-derecha.jpg', ancho=1280, alto=720,
                  pie='Cola para votar bajo la lluvia en La Guindalera, Madrid, el 16 de febrero de 1936.',
                  url='https://commons.wikimedia.org/wiki/File:1936_Spanish_general_elections.jpg', credito='Firmada «Videa y Cortés», dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='abstencion-anarquista-cnt-1933-1936', fecha='2026-10-23',
        titulo='Cuando la CNT pidió no votar, en Alcalá de Gurrea votaron 87 de 829 electores; dos años después, 517', serie='historia',
        descripcion='En noviembre de 1933, la CNT pidió a los obreros que no votaran. En los quince pueblos que tres semanas después proclamaron el comunismo libertario votó menos de la mitad del censo. En febrero de 1936, con los presos en la cárcel y sin campaña contra las urnas, votaron siete de cada diez. Así se ve la abstención anarquista en el Atlas electoral de la Segunda República.',
        compara='Participación y voto en las generales del 19 de noviembre de 1933 y del 16 de febrero de 1936 en los municipios y circunscripciones del Atlas; los 15 pueblos que proclamaron el comunismo libertario en diciembre de 1933, frente al resto.',
        limites='El Atlas da la participación de 1933 solo en una parte de los municipios. No sabemos quién se abstuvo por la consigna de la CNT y quién por otras razones. La cifra de Sevilla capital en 1936 se excluye por inverosímil. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector: el peso de cada candidatura es su parte de los votos a candidatos. El censo de entonces era de mayores de 23 años; el de 2023, de 18, sin voto exterior.',
        calculo='Participación: votantes sobre censo. Cambio de participación entre 1933 y 1936 en cada municipio con las dos cifras. Media ponderada por el censo.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 ('https://recyt.fecyt.es/index.php/Hyp/article/view/41667', 'Roberto Villa García, «La CNT contra la República: la insurrección revolucionaria de diciembre de 1933», Historia y Política (2011)'),
                 ('https://www.redalyc.org/articulo.oa?id=521551967009', 'Roberto Villa García, «Obreros, no votéis», Pasado y Memoria (2014)'),
                 ('https://www.publico.es/culturas/masacre-sucesos-casas-viejas-segunda-republica.html', 'Público, sobre los sucesos de Casas Viejas'),
                 ('https://en.wikipedia.org/wiki/Anarchist_insurrection_of_December_1933', 'Wikipedia, «Anarchist insurrection of December 1933» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Benalup-Casas_Viejas', 'Wikipedia, «Benalup-Casas Viejas» (consultada el 23-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/abstencion-anarquista-cnt-1933-1936.jpg', ancho=1280, alto=720,
                  pie='Ricardo Díez, Francisco Ascaso, Joaquín Combina, Buenaventura Durruti y Vicente Lorda, presos en el penal de El Puerto de Santa María, el 15 de agosto de 1933.',
                  url='https://commons.wikimedia.org/wiki/File:Puerto_de_Santa_Mar%C3%ADa_prisoners.png', credito='Autor desconocido, dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='pueblos-bajo-el-agua-1936', fecha='2026-10-23',
        titulo='Riaño dio el 86 % a las derechas en 1936; Mequinenza, el 89 % al Frente Popular. Así votaban los pueblos que se tragaron los pantanos', serie='historia',
        descripcion='Dieciocho pueblos que votaron en febrero de 1936 y que después quedaron bajo un embalse, o desalojados para hacerlo. Había 12.014 electores. Ganaron las derechas en 12 y el Frente Popular en 5. Hoy, donde quedan, se vota de otra manera, y en algunos ya no vota nadie.',
        compara='Dieciocho municipios de febrero de 1936 anegados o desalojados por un embalse, en las generales del 16 de febrero de 1936 y, en el municipio al que pertenecen hoy, en las del 23 de julio de 2023.',
        limites='Son los que hemos podido identificar en el Atlas con un embalse documentado, no todos: faltan las aldeas que no eran municipio. El voto no explica dónde se hizo un pantano. Los datos de 2023 son del municipio entero al que pertenece hoy cada pueblo. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector: el peso de cada candidatura es su parte de los votos a candidatos. El censo de entonces era de mayores de 23 años; el de 2023, de 18, sin voto exterior.',
        calculo='Porcentaje de cada bloque sobre los votos a candidatos (1936). En 2023, izquierda: PSOE, Sumar, ERC, EH Bildu y BNG; derecha: PP, Vox, Junts, PNV y CC.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://es.wikipedia.org/wiki/Embalse_de_Ria%C3%B1o', 'Wikipedia, «Embalse de Riaño» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Pueblo_Viejo_de_Mequinenza', 'Wikipedia, «Pueblo Viejo de Mequinenza» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Talavera_la_Vieja', 'Wikipedia, «Talavera la Vieja» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Granadilla_(C%C3%A1ceres)', 'Wikipedia, «Granadilla (Cáceres)» (consultada el 23-10-2026)'),
                 ('https://www.publico.es/sociedad/paca-castillo-mujer-mantuvo-vivo-pueblo.html', 'Eduardo Bayona, sobre Paca Castillo y Jánovas, Público'),
                 ('https://www.iagua.es/blogs/agueda-garcia-de-durango/pueblos-sumergidos', 'Águeda García de Durango, «Pueblos sumergidos», iAgua'),
                 ('https://www.penguin.co.nz/books/liquid-power-9780262548960', 'Erik Swyngedouw, Liquid Power (MIT Press), presentación del libro')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pueblos-bajo-el-agua-1936.jpg', ancho=1280, alto=720,
                  pie='Una calle de Riaño (León) en noviembre de 1984, tres años antes de que lo cubriera el embalse.',
                  url='https://commons.wikimedia.org/wiki/File:Ria%C3%B1o_antiguo.jpg', credito='Rafaelji, CC BY-SA 3.0, vía Wikimedia Commons'),
    ),
    dict(
        slug='pueblos-que-ya-no-existen-1936', fecha='2026-10-23',
        titulo='Vallecas dio el 86 % al Frente Popular y Franco la borró del mapa: los 1.334 pueblos que votaron en 1936 y ya no existen', serie='historia',
        descripcion='Uno de cada siete municipios que votaron en febrero de 1936 ya no existe. Trece se los tragó el Gran Madrid de la posguerra, y en nueve de ellos había ganado la izquierda. Más de mil desaparecieron en los años sesenta y setenta, por decreto y casi siempre por pobreza. Así votaban y así votan hoy los lugares donde estaban.',
        compara='Los 1.334 municipios de febrero de 1936 que ya no existen, según el Atlas y los censos del INE; los 13 anexionados por Madrid entre 1948 y 1954, comparados con los distritos que ocupan hoy su término en las generales del 23 de julio de 2023.',
        limites='La correspondencia entre pueblos de 1936 y distritos de hoy es aproximada. En Vigo y Ferrol, los datos de 2023 son de la ciudad entera. La fecha de desaparición es la del censo en que el municipio ya no aparece, no la del decreto. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector: el peso de cada candidatura es su parte de los votos a candidatos. El censo de entonces era de mayores de 23 años; el de 2023, de 18, sin voto exterior.',
        calculo='Ganador de 1936: el bloque con más porcentaje de voto. En 2023, izquierda: PSOE y Sumar (y ERC, EH Bildu y BNG); derecha: PP y Vox (y Junts, PNV y CC), por sección censal agregada por distrito.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://www.elsaltodiario.com/urbanismo/anexion-municipos-gran-madrid-superar-barcelona-13-pueblos', 'Pablo Rivas, «Gran Madrid: superar a Barcelona bien vale 13 pueblos», El Salto (2019)'),
                 ('https://es.ara.cat/cultura/gran-madrid-plan-franco-superar-barcelona_130_4626292.html', 'David Miró, sobre el Gran Madrid, Ara (14-2-2023)'),
                 ('https://www.boe.es/boe/dias/1966/05/31/pdfs/A06801-06802.pdf', 'BOE, decretos 1285/1966 y 1286/1966, de 5 de mayo (Almarza y Betesa)'),
                 ('https://es.wikipedia.org/wiki/Chamart%C3%ADn_de_la_Rosa', 'Wikipedia, «Chamartín de la Rosa» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Lavadores', 'Wikipedia, «Lavadores» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Serantes_(Ferrol)', 'Wikipedia, «Serantes (Ferrol)» (consultada el 23-10-2026)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pueblos-que-ya-no-existen-1936.jpg', ancho=1280, alto=720,
                  pie='Placa en memoria de la última corporación democrática de Chamartín de la Rosa, en la Junta Municipal de Chamartín (Madrid), descubierta el 15 de enero de 2019.',
                  url='https://commons.wikimedia.org/wiki/File:Chamart%C3%ADn_homenajea_con_una_placa_a_la_%C3%BAltima_corporaci%C3%B3n_democr%C3%A1tica_de_Chamart%C3%ADn_de_la_Rosa_01.jpg', credito='Ayuntamiento de Madrid (Diario de Madrid), CC BY 4.0, vía Wikimedia Commons'),
    ),
    dict(
        slug='asturias-1934-1936-revolucion-urnas', fecha='2026-10-23',
        titulo='Mieres votó en masa dieciséis meses después de la revolución: el 86 % fue a las urnas y el 79 % eligió al Frente Popular', serie='historia',
        descripcion='En octubre de 1934, los mineros asturianos se levantaron en armas y fueron vencidos en quince días. En febrero de 1936 volvieron a las urnas con miles de presos todavía en la cárcel. Las cuencas, que ya votaban a la izquierda, se movieron poco; lo que cambió Asturias fue Gijón, que dejó de abstenerse.',
        compara='Los concejos de Asturias en las generales del 19 de noviembre de 1933, del 16 de febrero de 1936 y del 23 de julio de 2023; los seis concejos mineros (Mieres, Langreo, San Martín del Rey Aurelio, Laviana, Aller y Lena) frente al resto.',
        limites='En 1933 la izquierda fue por separado y la sumamos nosotros. La participación de 1933 solo se conoce por circunscripción. Las cifras de muertos y presos de 1934 son estimaciones de historiadores. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector: el peso de cada candidatura es su parte de los votos a candidatos. El censo de entonces era de mayores de 23 años; el de 2023, de 18, sin voto exterior.',
        calculo='Porcentaje de cada bloque sobre los votos a candidatos; medias ponderadas por el censo. En 2023, izquierda: PSOE y Sumar; derecha: PP y Vox.',
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://es.wikipedia.org/wiki/Revoluci%C3%B3n_de_Asturias_de_1934', 'Wikipedia, «Revolución de Asturias de 1934» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Ram%C3%B3n_Gonz%C3%A1lez_Pe%C3%B1a', 'Wikipedia, «Ramón González Peña» (consultada el 23-10-2026)'),
                 ('https://www.boe.es/gazeta/dias/1936/02/22/pdfs/GMD-1936-53.pdf', 'Gaceta de Madrid, decreto-ley de amnistía de 21 de febrero de 1936 (22-2-1936)'),
                 ('https://www.elsaltodiario.com/comic/entrevista-alfonso-zapico-autor-balada-norte-cuenca-minera-asturias-revolucion-octubre', 'Entrevista a Alfonso Zapico, El Salto')],
        enlaces=[],
        lugar='Asturias',
        foto=dict(src='img/actualidad/fotos/asturias-1934-1936-revolucion-urnas.jpg', ancho=1280, alto=720,
                  pie='Obreros detenidos por la Guardia Civil y la Guardia de Asalto durante la revolución de Asturias, en octubre de 1934.',
                  url='https://commons.wikimedia.org/wiki/File:Arrested_workers_during_the_Asturian_Revolution,_1934.jpg', credito='Ilustrowany Kuryer Codzienny (Archivo Nacional Digital de Polonia), dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='cataluna-lliga-front-esquerres-1933-1936', fecha='2026-10-23',
        titulo="Vic dio el 69 % a la Lliga en 1933 y hoy es la gran ciudad de Junts; L'Hospitalet dio el 77 % al Front d'Esquerres de Companys y hoy vota al PSC", serie='historia',
        descripcion="En noviembre de 1933, la Lliga de Cambó ganó en Cataluña más diputados que Esquerra. Once meses después, Lluís Companys proclamó el Estado Catalán y acabó en la cárcel con todo su Gobierno. En febrero de 1936, con él todavía preso, el Front d'Esquerres sacó el 59%. Donde aquel frente ganó con más fuerza, hoy gana el PSC; donde ganaron las derechas, Junts y ERC sacan hoy sus mejores resultados.",
        compara="Los municipios de Cataluña en las generales del 19 de noviembre de 1933 (sin Barcelona ciudad, que el Atlas no tiene), del 16 de febrero de 1936 y del 23 de julio de 2023. En 1933, la Lliga frente a las izquierdas; en 1936, el Front d'Esquerres frente al Front Català d'Ordre.",
        limites='Comparar la Lliga con Junts o el Front con el PSC no quiere decir que sean el mismo partido. La relación entre 1936 y 2023 es una media por franjas, no una relación de causa. En 1933 las izquierdas fueron por separado y las sumamos nosotros. En 1933 y 1936 se votaba con listas abiertas y varios votos por elector: el peso de cada candidatura es su parte de los votos a candidatos. El censo de entonces era de mayores de 23 años; el de 2023, de 18, sin voto exterior.',
        calculo="Ganador de cada municipio: el bloque con más porcentaje. Franjas de voto al Front d'Esquerres en 1936 y media del voto de 2023 a PSC, ERC y Junts, ponderada por votantes.",
        fuentes=[('https://doi.org/10.34810/data3274', 'Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez, Electoral Atlas of the Spanish Second Republic (1931-1936), Universitat Pompeu Fabra, CORA Repositori de Dades de Recerca (CC BY-NC-SA 4.0)'),
                 INTERIOR,
                 ('https://es.wikipedia.org/wiki/Proclamaci%C3%B3n_del_Estado_Catal%C3%A1n_de_1934', 'Wikipedia, «Proclamación del Estado Catalán de 1934» (consultada el 23-10-2026)'),
                 ('https://es.wikipedia.org/wiki/Llu%C3%ADs_Companys', 'Wikipedia, «Lluís Companys» (consultada el 23-10-2026)'),
                 ('https://ca.wikipedia.org/wiki/Eleccions_generals_espanyoles_de_1933', 'Viquipèdia, «Eleccions generals espanyoles de 1933» (consultada el 23-10-2026)'),
                 ('https://ca.wikipedia.org/wiki/Eleccions_generals_espanyoles_de_1936', 'Viquipèdia, «Eleccions generals espanyoles de 1936» (consultada el 23-10-2026)'),
                 ('https://www.boe.es/gazeta/dias/1936/02/22/pdfs/GMD-1936-53.pdf', 'Gaceta de Madrid, decreto-ley de amnistía de 21 de febrero de 1936 (22-2-1936)'),
                 ('http://hemeroteca.lavanguardia.com/preview/1936/03/03/pagina-10/33123560/pdf.html', 'La Vanguardia, «El Presidente saluda al pueblo desde el balcón» (3-3-1936)')],
        enlaces=[],
        lugar='Cataluña',
        foto=dict(src='img/actualidad/fotos/cataluna-lliga-front-esquerres-1933-1936.jpg', ancho=1280, alto=720,
                  pie='Lluís Companys (en el centro), Joan Comorera y otros miembros del Gobierno de la Generalitat presos, en una foto publicada en 1936.',
                  url='https://commons.wikimedia.org/wiki/File:Companys,_Comorera_and_others_behind_bars.jpg', credito='Atribuida a Alfonso, dominio público, vía Wikimedia Commons'),
    ),
    dict(
        slug='pueblos-colonizacion-franquismo-voto', fecha='2026-10-23',
        titulo='Los pueblos que levantó Franco votan más a Vox que sus vecinos: en Tiétar, Rosalejo y Pueblonuevo de Miramontes pasó del 25 %', serie='historia',
        descripcion='Entre los años cuarenta y setenta, la dictadura construyó cerca de trescientos pueblos nuevos para colonos. Hemos buscado 267 en el mapa de secciones censales y seguido su voto en las generales desde 2004. Votan como la España rural de su provincia, con dos diferencias: participan menos y, desde 2019, votan más a Vox.',
        compara='Las 205 secciones censales de 2023 que contienen alguno de los 267 poblados nuevos del Instituto Nacional de Colonización, en las generales de 2004 a 2023, frente a las secciones de los municipios de menos de 5.000 habitantes de la misma provincia.',
        limites='La lista de poblados es la de la Wikipedia, no una oficial. Una sección puede incluir más que el poblado. La serie usa los códigos de sección actuales. No hay datos por sección antes de 2004. No sabemos cuántos votantes son colonos o hijos de colonos. Es una comparación, no una explicación.',
        calculo='Regresión del voto de cada sección (en puntos) sobre si contiene un poblado, con efecto fijo de provincia, ponderada por votantes y con errores agrupados por municipio; margen de error al 95%.',
        fuentes=[INTERIOR,
                 ('https://es.wikipedia.org/wiki/Anexo:Poblados_del_Instituto_Nacional_de_Colonizaci%C3%B3n', 'Wikipedia, «Anexo:Poblados del Instituto Nacional de Colonización» (consultada el 23-10-2026)'),
                 ('https://ctxt.es/es/20241001/Culturas/47582/colonizacion-agraria-antonio-cazorla-franquismo-memoria-crisis-democracia.htm', 'Esther Peñas, entrevista a Antonio Cazorla, Ctxt (6-10-2024)'),
                 ('https://www.elsaltodiario.com/memoria-historica/guadiana-despierta-frente-a-guadiana-del-caudillo-', 'El Salto, «Guadiana Despierta frente a Guadiana del Caudillo» (16-2-2019)'),
                 ('https://www.boe.es/boe/dias/2020/03/09/pdfs/BOE-A-2020-3329.pdf', 'BOE, cambio de denominación de Guadiana del Caudillo por Guadiana (9-3-2020)')],
        enlaces=[],
        lugar='España',
        foto=dict(src='img/actualidad/fotos/pueblos-colonizacion-franquismo-voto.jpg', ancho=1280, alto=720,
                  pie='Casas de colonos en Rosalejo (Cáceres), pueblo fundado por el Instituto Nacional de Colonización en 1956, en mayo de 2021.',
                  url='https://commons.wikimedia.org/wiki/File:Rosalejo_02.jpg', credito='19Tarrestnom65, CC BY-SA 4.0, vía Wikimedia Commons'),
    ),
    dict(
        slug='mujeres-jovenes-voto-29n', fecha='2026-10-25',
        foto=dict(src='img/actualidad/fotos/mujeres-jovenes-voto-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Tres mujeres jóvenes con su sobre camino de la urna: un collage.'),
        titulo='El voto a Vox de las mujeres jóvenes se ha triplicado desde 2023, y la izquierda ha perdido 13 puntos entre ellas', serie='29n', figura=0,
        descripcion='En los barómetros del CIS, Vox pasa del 4,4% al 13,6% entre las mujeres de 18 a 29 años. Los hombres de su edad siguen muy por delante: uno de cada cuatro dice que votaría a Vox. La brecha entre ellos y ellas se abrió en 2023, y desde entonces no se ha cerrado.',
        compara='El voto más simpatía a Vox y a la izquierda estatal por sexo y edad en los microdatos de 26 encuestas del CIS, de 2019 a octubre de 2026, y la ubicación ideológica de los entrevistados.',
        limites='Son encuestas: el voto más simpatía no es la estimación de voto del CIS ni una previsión, y los niveles pueden estar sesgados; las diferencias entre grupos de la misma encuesta son más fiables. Los barómetros de 2026 tienen pesos muy variables y los márgenes de error usan el tamaño efectivo de la muestra. Los partidos cambian de nombre entre 2019 y 2026, por eso la serie compara Vox y el bloque de la izquierda estatal. Los resultados reales no se pueden separar por sexo ni por edad. Las causas que proponen los expertos citados son hipótesis.',
        fuentes=[('https://www.cis.es/', 'CIS, microdatos de los barómetros de diciembre de 2025 a octubre de 2026 (estudios 3536 a 3582)'),
                 ('https://www.cis.es/documents/d/cis/MD3420', 'CIS, estudio 3420, barómetro de septiembre de 2023, y otros 16 estudios de 2019 a 2025'),
                 ('https://acento.com.do/politica/la-politica-abre-una-nueva-brecha-de-genero-entre-jovenes-de-todo-el-mundo-9595155.html', 'EFE, La política abre una nueva brecha de género entre jóvenes de todo el mundo (22-12-2025)'),
                 ('https://www.publico.es/mujer/brecha-ideologica-divide-juventud-derechas-nunca-cada-vez-izquierdas.html', 'Público, la brecha ideológica que divide a la juventud (7-3-2024)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='psoe-primera-fuerza-29n', fecha='2026-10-25',
        foto=dict(src='img/actualidad/fotos/psoe-primera-fuerza-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna llena de sobres con uno rojo delante, entre los escaños del Congreso y el sillón de la presidencia: un collage.'),
        titulo='El PP saca 6 puntos al PSOE en las encuestas: ni el mayor fallo de la última década, el de 2023, daría el sorpasso que anuncia Iván Redondo', serie='29n', figura=0,
        descripcion='En 2023, los sondeos de la última semana exageraron la ventaja del PP en 4,9 puntos. Si hoy se equivocaran igual, el PP seguiría por delante por algo más de un punto. Solo una de las trece encuestas privadas de octubre deja al PSOE a menos de dos puntos.',
        compara='La estimación del PP y del PSOE en la última encuesta de cada empresa privada publicada desde el 4 de octubre de 2026, y el error de las encuestas en la ventaja del PP sobre el PSOE en las generales de 2015 a 2023.',
        limites='El error se mide con la mediana de las encuestas publicadas con trabajo de campo terminado entre 14 y 6 días antes de votar, sin ponderar por tamaño ni por empresa, y el resultado sobre votos válidos. Las recopilaciones de Wikipedia y Electográfica pueden no estar completas. Cinco elecciones son pocas para sacar una regla. Aplicar el error de 2023 a las encuestas de hoy es una cuenta, no una previsión. Las frases de Redondo se citan de la prensa que recogió su entrevista en RNE.',
        fuentes=[('https://www.esdiario.com/nacional/261013/200111/ivan-redondo-psoe-sanchez-29n.html', 'ESdiario, entrevista de Iván Redondo en RNE (13-10-2026)'),
                 ('https://es.ara.cat/politica/exguru-pedro-sanchez-cree-psoe-primera-fuerza-29-n_1_5875719.html', 'Ara, El exgurú de Pedro Sánchez que cree que el PSOE puede ser primera fuerza el 29-N (10-10-2026)'),
                 ('https://www.electografica.com/', 'Electográfica, encuestas de las generales de noviembre de 2019, 2023 y 2026'),
                 ('https://en.wikipedia.org/wiki/Opinion_polling_for_the_2015_Spanish_general_election', 'Wikipedia, encuestas de las generales de 2015'),
                 ('https://en.wikipedia.org/wiki/Opinion_polling_for_the_2016_Spanish_general_election', 'Wikipedia, encuestas de las generales de 2016'),
                 ('https://en.wikipedia.org/wiki/Opinion_polling_for_the_April_2019_Spanish_general_election', 'Wikipedia, encuestas de las generales de abril de 2019'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las generales de 2015 a 2023'),
                 ('https://www.diaridetarragona.com/elecciones/198717/las-encuestas-vuelven-a-fallar-da16259794.html', 'EFE, Las encuestas vuelven a fallar (24-7-2023)'),
                 ('https://elespanol.com/espana/politica/20230724/michavila-hace-bueno-tezanos-arrastro-pp-creando-expectativas-condicionaron/781172083_0.html', 'El Español, sobre las encuestas de GAD3 en el 23J (24-7-2023)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='encuestas-semana-29n', fecha='2026-10-26', actualizado='2026-10-26 07:10',
        foto=dict(src='img/actualidad/fotos/encuestas-semana-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mano marca casillas en una hoja de encuesta junto a una urna transparente con sobres y un calendario de hojas que pasan: un collage.'),
        titulo='El PP baja en las cinco encuestas de la semana, pero con Vox sigue sumando mayoría absoluta en todas', serie='29n', figura=0,
        descripcion='Desde finales de septiembre, la mediana de las encuestas ha bajado al PP dos puntos, del 33,7% al 31,7%. El PSOE recupera menos de uno y Vox se queda cerca del 19%. Nuestro modelo da hoy a PP y Vox 195 escaños, 19 más de los que hacen falta.',
        compara='Las cinco encuestas nacionales publicadas entre el 19 y el 25 de octubre de 2026, cada una con la anterior de la misma empresa, y la mediana semanal de las encuestas desde finales de agosto.',
        limites='Comparar una encuesta con la anterior de la misma empresa no elimina el error de muestreo: cambios de menos de un punto están dentro del margen de casi todas. La mediana usa la última encuesta de cada empresa en las tres semanas anteriores, sin ponderar, e incluye el CIS; no recoge las encuestas que Electográfica y Wikipedia aún no han añadido. Los sondeos internos de los partidos no se cuentan. La estimación del modelo depende de la media de las encuestas y de cómo se reparte el voto por provincia; su método está publicado.',
        calculo='Diferencia, en puntos, entre la estimación de cada partido en la encuesta de la semana y en la anterior de la misma empresa. Frente Amplio incluye Compromís y Front Valencià cuando la encuesta los da aparte. Mediana semanal: la de la página de encuestas, tomada cada domingo.',
        fuentes=[('https://www.elmundo.es/espana/encuestas/2026/10/19/6ad4f168e9cf4a2c7a8b458b.html', 'Sigma Dos para El Mundo (19-10-2026)'),
                 ('https://www.imop.es/encuesta-pre-electoral-el-confidencial-ola-2/', 'IMOP Insights para El Confidencial, segunda ola (23-10-2026)'),
                 ('https://www.eldiario.es/politica/bloque-izquierdas-recorta-distancias-pp-vox-mantienen-mayoria-absoluta_1_13611052.html', 'Ateneo del Dato para elDiario.es (25-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261025/izquierda-no-remonta-sanchez-gana-escanos-costa-frente-podemos-sondeo-noche/1003744434105_0.html', 'SocioMétrica para El Español (25-10-2026)'),
                 ('https://electomania.es/electopanel-25-octubre-el-pp-baja-de-nuevo-frente-amplio-crece/', 'ElectoPanel de Electomanía (25-10-2026)'),
                 ('https://www.eldiario.es/politica/sanchez-saca-psoe-pesimismo-errores-feijoo-miedo-vox_1_13607713.html', 'elDiario.es, sobre los sondeos internos del PSOE (25-10-2026)'),
                 ('https://www.electografica.com/', 'Electográfica, encuestas de las generales de 2026'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='israel-elecciones-encuestas-knesset', fecha='2026-10-27', actualizado='2026-10-27 10:00',
        titulo='Solo una televisión le daba la mayoría a Netanyahu', serie='internacional',
        descripcion='En las 24 encuestas de las dos últimas semanas, su bloque se quedó en 52,5 escaños de media, ocho y medio por debajo de los 61. Solo las cinco de Canal 14 le daban la mayoría. Y el partido nuevo de Gadi Eisenkot iba por delante del Likud en 16 de ellas.',
        compara='Los escaños que daban a cada partido y a cada bloque las 24 encuestas publicadas en Israel en las dos semanas anteriores a las elecciones a la Knesset del 27 de octubre de 2026, su evolución semanal desde septiembre y el resultado de 2022.',
        limites='Son encuestas, no resultados. Se han tomado de la recopilación de Wikipedia, que enlaza cada una, y se han sumado los escaños por partido. El bloque de Netanyahu son los cinco partidos del Gobierno actual (Likud, Sionismo Religioso-Zehut, Otzma Yehudit, Shas y Judaísmo Unido de la Torá); Amcha Yisrael se deja fuera, aunque algunos medios lo incluyen. Un partido por debajo del umbral cuenta como 0 escaños. Canal 14 publicó cinco de las 24 encuestas, por eso se dan las medias con y sin ella.',
        calculo='Media simple de los escaños de cada partido en las encuestas con fin de trabajo de campo entre el 13 y el 26 de octubre de 2026 (la última, del 23). Bloques: suma de los partidos de cada encuesta. Serie semanal: media de las encuestas de cada semana, de lunes a domingo.',
        fuentes=[('https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Israeli_legislative_election', 'Wikipedia, Opinion polling for the 2026 Israeli legislative election (consultada el 27-10-2026)'),
                 ('https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_Israeli_legislative_election', 'Wikipedia, Opinion polling for the 2022 Israeli legislative election'),
                 ('https://en.wikipedia.org/wiki/2022_Israeli_legislative_election', 'Comité Central Electoral de Israel, resultados de 2022 (vía Wikipedia)'),
                 ('https://www.europapress.es/internacional/noticia-abren-urnas-israel-decisiva-jornada-electoral-20261027064413.html', 'Europa Press, Abren las urnas en Israel en una decisiva jornada electoral (27-10-2026)'),
                 ('https://www.europapress.es/internacional/noticia-israel-dividido-decide-si-avala-netanyahu-apuesta-cambio-primeras-elecciones-20261026173759.html', 'Europa Press, Un Israel dividido decide si avala a Netanyahu o apuesta por el cambio (26-10-2026)')],
        enlaces=[],
        lugar='Israel',
    ),
    dict(
        slug='alvise-salf-donde-vota-29n', fecha='2026-10-27', actualizado='2026-10-27 10:30',
        foto=dict(src='img/actualidad/fotos/alvise-salf-donde-vota-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un hombre mira el móvil junto a un sobre electoral y, al lado, una calle de bloques nuevos con una urna en la acera: un collage.'),
        titulo='Madrid es la puerta más cercana de Alvise al Congreso: le basta el 3% y las encuestas le dan el 2%', serie='29n',
        descripcion='Con su voto de las europeas habría sacado escaño también en Valencia y Málaga. Su voto es de ciudades dormitorio: le votó el 7,1% en los barrios más jóvenes y el 2,5% en los más envejecidos, con Cártama, Mijas y Roquetas a la cabeza. Se presenta en 47 provincias.',
        compara='El voto a Se Acabó La Fiesta y a Vox en las elecciones europeas de 2024 en las 36.000 secciones censales de España, según la edad media, la renta, el paro, los estudios y los nacidos fuera de cada sección, por tamaño de municipio y por provincia, y su estimación para el 29N con la media de encuestas y el modelo de Mapa Electoral.',
        limites='Las europeas son otro tipo de elección, con menos participación, y SALF se presentó entonces como agrupación de electores. Es una relación entre secciones, no entre personas: no dice quién votó a SALF. La edad media y la renta son del Atlas de distribución de renta del INE; el paro, los estudios y los nacidos fuera, del Censo de 2021. La regresión (mínimos cuadrados ponderados por votos válidos, efectos fijos por provincia, errores agrupados por municipio) describe asociaciones, no causas. Sin el voto desde el extranjero.',
        calculo='% de SALF sobre votos válidos por sección; deciles de secciones por edad media; regresión del % de SALF sobre edad media, renta por unidad de consumo, % de nacidos fuera, % con estudios superiores y % de paro, con efectos fijos por provincia: −0,24 puntos por año de edad media (error 0,006).',
        fuentes=[('https://theobjective.com/espana/politica/2026-10-27/alvise-senado-pp-vox-congreso/', 'The Objective, Alvise renuncia al Senado tras el pacto PP-Vox pero se presenta en 47 provincias al Congreso (27-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-alvise-presentara-elecciones-cabeza-lista-salf-madrid-20261005163400.html', 'Europa Press, Alvise se presentará a las elecciones como cabeza de lista de SALF por Madrid (5-10-2026)'),
                 ('https://www.ceutaldia.com/articulo/politica/acabo-fiesta-empieza-carlos-pavon-sera-candidato-ceuta-congreso/20261025203842323236.html', 'Ceuta al Día, Carlos Pavón será el candidato de SALF en Ceuta (25-10-2026)'),
                 ('https://www.ucm.es/icca/explorando-el-exito-politico-electoral-de-se', 'Imanol Negral Bravo y Álvaro Sánchez García, Explorando el éxito político-electoral de Se Acabó La Fiesta, ICCA (Universidad Complutense)'),
                 ('https://infoelectoral.interior.gob.es/', 'Ministerio del Interior, resultados de las elecciones al Parlamento Europeo de 2024 por sección censal'),
                 ('https://www.ine.es/dyngs/INEbase/es/operacion.htm?c=Estadistica_C&cid=1254736177088&menu=ultiDatos&idp=1254735976608', 'INE, Atlas de distribución de renta de los hogares'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='feijoo-albiol-barcelona-disturbios-29n', fecha='2026-10-28',
        foto=dict(src='img/actualidad/fotos/feijoo-albiol-barcelona-disturbios-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Feijóo y Albiol leen un papel; al lado, una esquina del Eixample con una valla metálica: un collage.'),
        titulo='Feijóo busca el voto del orden en la comunidad que más cita la inseguridad', serie='29n',
        descripcion='Antes de los disturbios del sábado, el 11% de los catalanes ya nombraba la inseguridad entre los grandes problemas de España, más del doble que en el resto. La citan más los simpatizantes de Junts y Vox que los del PP. Y Albiol arrastra votos en Badalona, pero Badalona es el 4% de la provincia.',
        compara='El porcentaje que cita la inseguridad ciudadana entre los tres principales problemas de España en Cataluña, en el resto de España y por partido dentro de Cataluña, en los barómetros del CIS de diciembre de 2025 a octubre de 2026; el voto de Albiol en Badalona en las municipales y del PP en las generales de 2023; y el PP en Barcelona en el modelo de encuestas.',
        limites='Los barómetros del CIS son anteriores a los disturbios del 24 de octubre. La pregunta es sobre los problemas de España, no sobre el voto. El voto más simpatía no es una estimación de voto; los márgenes por partido en Cataluña van de dos a cinco puntos. El cálculo de 1,3 puntos supone que todos los votantes municipales de Albiol votan al PP, un techo, no una previsión. Los estudios citados tratan de Estados Unidos (1960-1972) y Londres (2011).',
        calculo='CIS: porcentaje ponderado (PESO normalizado a media 1 en cada estudio) de entrevistados que citan «La inseguridad ciudadana» en PESPANNA1, PESPANNA2 o PESPANNA3, estudios 3536 a 3582; margen al 95% con n efectiva de Kish. Badalona: votos a candidaturas más blancos. Último escaño: cociente D\'Hondt del escaño 32 de Barcelona en 2023 sobre votos válidos.',
        fuentes=[('https://www.catalunyapress.es/articulo/politica-nacional/2026-10-27/6068322-feijoo-convirte-disturbios-barcelona-arma-29-n-visitara-tiendas-afectadas-miercoles', 'Catalunya Press, Feijóo visitará las tiendas afectadas por los disturbios (27-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/feijoo-seguridad-barcelona-albiol-vivienda/', 'Demócrata, Feijóo arranca en Barcelona su campaña por la seguridad (27-10-2026)'),
                 ('https://elpais.com/espana/elecciones-generales/2026-10-27/feijoo-hace-de-los-disturbios-de-barcelona-uno-de-los-ejes-de-su-campana-contra-sanchez.html', 'El País, Feijóo hace de los disturbios de Barcelona uno de los ejes de su campaña (27-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-128-detenidos-disturbios-barcelona-sabado-72-ellos-menores-edad-20261025090646.html', 'Europa Press, 128 detenidos por los disturbios de Barcelona (25-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-mossos-elevan-130-detenidos-disturbios-barcelona-cuales-76-menores-20261026120129.html', 'Europa Press, los Mossos elevan a 130 los detenidos (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-feijoo-acusa-sanchez-generar-tension-porque-sabe-pierde-promete-ser-implacable-violentos-20261027141144.html', 'Europa Press, Feijóo promete ser «implacable con los violentos» (27-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-albiol-pp-ve-absoluto-desprecio-sanchez-afectados-disturbios-barcelona-20261026131018.html', 'Europa Press, Albiol ve «absoluto desprecio» de Sánchez a los afectados (26-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-parlon-ve-voluntad-desestabilizacion-caos-organizadores-disturbios-barcelona-20261026092542.html', 'Europa Press, Parlon ve voluntad de desestabilización (26-10-2026)'),
                 ('https://doi.org/10.1017/S000305542000009X', 'Omar Wasow, Agenda Seeding: How 1960s Black Protests Moved Elites, Public Opinion and Voting, American Political Science Review 114 (2020)'),
                 ('https://doi.org/10.1017/psrm.2022.49', 'Gabriel León-Ablan y Peter John, How urban riots influence political behavior: vote choices after the 2011 London riots, Political Science Research and Methods (2022)'),
                 ('https://www.cis.es/', 'CIS, microdatos de los barómetros de diciembre de 2025 a octubre de 2026'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños')],
        enlaces=[],
        lugar='Barcelona',
    ),
    dict(
        slug='rufian-montero-la-revuelta-29n', fecha='2026-10-28',
        foto=dict(src='img/actualidad/fotos/rufian-montero-la-revuelta-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Rufián y Montero en un sofá rojo de plató, con Broncano de pie y una cámara de televisión: un collage.'),
        titulo='Rufián le guarda a Podemos el puesto 6: sale en 7 de cada 10 simulaciones', serie='29n',
        descripcion='Tras pasar por La Revuelta, el tándem de ERC y Podemos se juega en Barcelona el escaño de Alejandra Sandoval. Y el duelo que busca Rufián con el PSC está entre los jóvenes: entre los catalanes de menos de 45 años, ERC y el PSC empatan en el CIS.',
        compara='La probabilidad de salir elegido de cada puesto de la lista de ERC por Barcelona, donde van dos independientes de Podemos (puestos 6 y 10), con el modelo de Mapa Electoral; y el voto más simpatía a PSC, ERC, Sumar y Podemos en Cataluña por edad en los barómetros del CIS de diciembre de 2025 a octubre de 2026.',
        limites='El modelo de escaños reparte la media de encuestas por provincia y no distingue a los candidatos de Podemos dentro de la lista de ERC; cambiará con las encuestas. El voto más simpatía del CIS no es una estimación de voto. En Cataluña hay entre 335 y 1.153 entrevistas por grupo de edad, con márgenes de error de tres a cinco puntos. Que los simpatizantes de Podemos voten a ERC es una suposición.',
        calculo='Puestos: proporción de las 2.000 simulaciones del modelo (media de encuestas del 26 de octubre de 2026) en que ERC saca en Barcelona al menos tantos escaños como el número del puesto. CIS: porcentaje ponderado (PESO normalizado a media 1 en cada estudio) de entrevistados con residencia en Cataluña que citan cada partido en VOTOSIMG, sobre el total de la celda; estudios 3536, 3540, 3544, 3546, 3557, 3562, 3567, 3577 y 3582.',
        fuentes=[('https://www.europapress.es/nacional/noticia-montero-propone-prohibir-especulacion-expropiar-fondos-buitre-hacer-frente-problema-vivienda-20261028001153.html', 'Europa Press, Montero propone prohibir la especulación y expropiar a los fondos buitre (28-10-2026)'),
                 ('https://www.europapress.es/epsocial/igualdad/noticia-irene-montero-cree-bastante-gente-sabia-era-errejon-mientras-rufian-le-sorprendio-absolutamente-20261027231247.html', 'Europa Press, Montero y Rufián en La Revuelta (27-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-alejandra-sandoval-maria-pozuelo-candidatas-podemos-lista-erc-barcelona-20261016154616.html', 'Europa Press, Alejandra Sandoval y María Pozuelo, candidatas de Podemos en la lista de ERC por Barcelona (16-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-bases-podemos-avalan-acuerdo-erc-cataluna-pactos-coalicion-canarias-valencia-20261016170110.html', 'Europa Press, las bases de Podemos avalan el acuerdo con ERC (16-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-rufian-erc-defiende-colaboracion-someter-psoe-no-estar-sometidos-20261024132859.html', 'Europa Press, Rufián defiende colaborar para «someter al PSOE» (24-10-2026)'),
                 ('https://www.cis.es/', 'CIS, microdatos de los barómetros de diciembre de 2025 a octubre de 2026'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños')],
        enlaces=[],
        lugar='Cataluña',
    ),
    dict(
        slug='comuns-psc-senado-girona-lleida-tarragona-29n', fecha='2026-10-27',
        foto=dict(src='img/actualidad/fotos/comuns-psc-senado-girona-lleida-tarragona-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='La catedral de Girona, la Seu Vella de Lleida y el anfiteatro de Tarragona detrás de una papeleta rosa del Senado con dos franjas, roja y morada: un collage.'),
        titulo='Sin los Comuns, Vox podría ganar el Senado en Tarragona', serie='29n',
        descripcion='Con las encuestas, Vox con el voto del PP supera al PSC en Tarragona y se llevaría tres de sus cuatro senadores. Sumando a los Comuns, el PSC recupera el primer puesto. En Lleida, el acuerdo le quita la mayoría a ERC.',
        compara='La lista más votada al Senado en Girona, Lleida y Tarragona con el acuerdo PP-Vox (el PP no se presenta en Girona ni en Tarragona), con y sin el voto de los Comuns sumado al PSC, con los votos del Senado de 2023 y con el modelo de encuestas de Mapa Electoral del 22 de octubre de 2026.',
        limites='Es una simulación, no una previsión. Supone transferencia completa: los votantes del PP votan a los candidatos de Vox donde el PP se retira y los de los Comuns, a los del PSC. En el Senado mucha gente marca menos nombres o mezcla partidos. El modelo estima el voto al Congreso, no al Senado, y su margen es mayor que las diferencias que decide la simulación (en Tarragona, 1,8 puntos entre Vox y el PSC). No incluye a Aliança Catalana, cuyas candidaturas al Senado no se conocen hasta el BOE del 28 de octubre.',
        calculo='Cada provincia elige cuatro senadores y cada elector marca hasta tres: la lista más votada saca tres y la segunda, uno. Votos de 2023: votos de cada partido divididos entre sus candidatos. Encuestas: mediana del voto por provincia del modelo de Mapa Electoral (PSOE como PSC, Sumar como Comuns).',
        fuentes=[('https://www.europapress.es/catalunya/noticia-psc-comuns-acuerdan-retirada-colau-senado-girona-lleida-tarragona-20261027121115.html', 'Europa Press, PSC y Comuns acuerdan la retirada de Colau del Senado en Girona, Lleida y Tarragona (27-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-cid-comuns-defiende-acuerdo-psc-parar-pies-vox-pp-senado-20261027141502.html', 'Europa Press, Cid defiende el acuerdo con el PSC «para parar los pies a Vox y a PP» (27-10-2026)'),
                 ('https://www.europapress.es/catalunya/noticia-moret-psc-defiende-acuerdo-comuns-senado-contra-regresion-democratica-pp-vox-20261027123148.html', 'Europa Press, Moret defiende el acuerdo con los Comuns (27-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-pp-vox-esperan-lograr-140-senadores-gracias-pacto-concurrir-senado-20261026185958.html', 'Europa Press, PP y Vox esperan lograr hasta 140 senadores gracias a su pacto (26-10-2026)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907', 'Junta Electoral Central, resultados de las elecciones al Congreso y al Senado de 23 de julio de 2023, BOE de 1-9-2023'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños')],
        enlaces=[],
        lugar='Cataluña',
    ),
    dict(
        slug='pacto-pp-vox-senado-provincias-29n', fecha='2026-10-27', actualizado='2026-10-27 10:30',
        correcciones='27-10-2026: la simulación suponía la lista conjunta de PSOE y Sumar en 50 circunscripciones, incluidas las siete islas canarias y sin el País Vasco. Se ha recalculado con las circunscripciones reales de Senado de Progreso (sin Canarias y con el País Vasco). Con las encuestas el resultado no cambia: entre 130 y 135 senadores elegidos para PP y Vox, entre 158 y 163 con los designados. Con los votos de 2023 pasa de 87-104 a 90-107, y la lista única de PP y Vox, de 124 a 127 (de 137 a 135 con encuestas). En Álava, el acuerdo le daría a la derecha un senador con las encuestas, no dos.',
        foto=dict(src='img/actualidad/fotos/pacto-pp-vox-senado-provincias-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Un apretón de manos entre una manga azul y otra verde sobre una papeleta rosa del Senado, con el hemiciclo de la Cámara Alta al fondo: un collage.'),
        titulo='PP y Vox pactan el Senado: con las encuestas sumarían entre 158 y 163 senadores, alrededor de los 160 que necesitan para renovar el Constitucional sin el PSOE', serie='29n',
        descripcion='El acuerdo añade entre 8 y 13 senadores elegidos a la derecha. Ocho salen de Valencia y las islas, donde Vox se retira; el resto depende de que los votantes de Vox den sus otros dos votos al PP en Sevilla, Asturias y Álava.',
        compara='Los senadores elegidos de PP y Vox en las 59 circunscripciones del Senado sin pacto, con el acuerdo del 26 de octubre (Vox se retira en seis provincias, presenta un solo candidato en catorce y el PP se retira en tres) y con una lista única, frente a la lista conjunta de PSOE y Frente Amplio, con los votos del Senado de 2023 y con esos votos movidos según la media de encuestas del 25 de octubre de 2026.',
        limites='Es una simulación, no una previsión. Usa los votos por candidato del Senado de 2023 y, en la versión con encuestas, los mueve con el cambio de cada partido en la media nacional de encuestas, igual en todas las provincias. Supone transferencia completa: los votantes de Vox votan al PP donde Vox se retira, los del PP a Vox donde se retira el PP y los de PSOE y Sumar a la lista conjunta, en las circunscripciones donde va Senado de Progreso según el registro de la Junta Electoral Central: las 43 provincias de las comunidades salvo Cataluña, Baleares y Canarias, más las islas de Baleares, donde el PSOE va con Més, IU y Sumar. En Canarias, Ceuta y Melilla la cuenta trata a PSOE y Sumar por separado; tratar Ceuta y Melilla como lista conjunta no cambia ningún resultado. En las 14 provincias con un solo candidato de Vox se dan tres versiones del voto de sus electores. No dice cuántos senadores serían de Vox dentro de las listas del PP. Los 28 senadores designados de PP y Vox son los actuales y cambiarán con las elecciones autonómicas.',
        calculo='Votos por candidato: suma de los votos de los candidatos de cada partido en la circunscripción dividida entre el número de candidatos que presentó. Se eligen los candidatos con más votos (cuatro por provincia, tres en Gran Canaria, Tenerife y Mallorca, dos en Ceuta y Melilla y uno en las demás islas), presentando cada partido tantos candidatos como votos tiene el elector. Factores de encuestas: PP 31,7/33,05; PSOE 26,5/31,7; Vox 18,9/12,39; Sumar 6,5/12,31.',
        fuentes=[('https://www.europapress.es/nacional/noticia-pp-vox-esperan-lograr-140-senadores-gracias-pacto-concurrir-senado-20261026185958.html', 'Europa Press, PP y Vox esperan lograr hasta 140 senadores gracias a su pacto (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-abascal-ve-renuncia-vox-presentar-candidaturas-senado-gesto-patriotico-todo-espana-20261026203730.html', 'Europa Press, Abascal ve la renuncia de Vox un «gesto patriótico» (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-arcadi-espana-asegura-nace-nuevo-partido-pacto-pp-vox-senado-hoy-decidido-casarse-20261026235858.html', 'Europa Press, Arcadi España: «Hoy ha nacido un nuevo partido» (26-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-senado-tiene-casi-60-escanos-asignados-margen-elecciones-23-pp-19-psoe-vox-20261026175641.html', 'Europa Press, el Senado tiene casi 60 escaños asignados al margen de las elecciones (26-10-2026)'),
                 ('https://www.elespanol.com/espana/politica/20261026/pp-vox-llegan-acuerdo-listas-senado-abascal-retiran-provincias-feijoo/1003744434759_0.html', 'El Español, PP y Vox llegan a un acuerdo para las listas del Senado (26-10-2026)'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907', 'Junta Electoral Central, resultados de las elecciones al Congreso y al Senado de 23 de julio de 2023, BOE de 1-9-2023'),
                 ('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-19537', 'Junta Electoral Central, corrección de errores, BOE de 16-9-2023'),
                 ('https://www.boe.es/buscar/act.php?id=BOE-A-1978-31229#a159', 'Constitución Española, artículo 159'),
                 ('https://mapaelectoral.es/encuestas/', 'Mapa Electoral, media de encuestas'),
                 ('https://revista.cortesgenerales.es/rcg/article/download/98/91', 'Fabio Pascua Mateo, Cuarenta años de elecciones a las Cortes Generales, Revista de las Cortes Generales 103 (2018)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='listas-29n-quien-encabeza', fecha='2026-10-26', actualizado='2026-10-28 09:40',
        foto=dict(src='img/actualidad/fotos/listas-29n-quien-encabeza.jpg', ancho=1280, alto=720, ia=True,
                  pie='Dos papeletas, una morada y otra rosa, rasgadas a cada lado de un escaño vacío del Congreso, con dos sobres: un collage.'),
        titulo='¿Sale tu candidato? Con las listas oficiales del BOE, 250 escaños están casi decididos y 204 candidatos se juegan los otros 100', serie='29n', figura=0,
        descripcion='Las candidaturas ya son oficiales. Vox tiene más puestos en el aire que seguros, y 18 de sus cabezas de lista no tienen el escaño garantizado. Irene Montero sale en 95 de cada 100 simulaciones; su número dos, en 56.',
        compara='La probabilidad de salir elegido de cada puesto de cada lista al Congreso en las 52 circunscripciones, con el modelo de Mapa Electoral y la media de encuestas del 26 de octubre de 2026, y los nombres de las candidaturas presentadas que publicó el BOE el 28 de octubre de 2026.',
        limites='Las probabilidades dependen de la media de encuestas y del reparto por provincia del modelo, cuyo método está publicado; cambiarán con las encuestas. Los nombres son los de las candidaturas presentadas (BOE del 28 de octubre); las juntas electorales las proclaman el 2 de noviembre y pueden pedir correcciones. El modelo no mide como una sola lista las coaliciones UPN-PP (Navarra) y Unidad del Pueblo Canario (Canarias), y todavía reparte voto a la CUP, que no se presenta.',
        calculo='Para cada puesto k de cada lista y provincia, proporción de las 2.000 simulaciones en que la lista saca k escaños o más. Casi seguro: 90% o más; en el aire: entre 10% y 90%.',
        fuentes=[('https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-22607', 'BOE, candidaturas presentadas al Congreso y al Senado (28-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-boe-publica-listas-congreso-senado-29n-no-seran-definitivas-proxima-semana-20261028073650.html', 'Europa Press, el BOE publica las listas (28-10-2026)'),
                 ('https://www.democrata.es/politica/ampliacion-la-militancia-de-la-cup-avala-no-concurrir-al-29n-con-un-68-9-de-apoyos/', 'Demócrata, la CUP no se presenta el 29N'),
                 ('https://mapaelectoral.es/encuestas/metodo-modelo.html', 'Mapa Electoral, método del modelo de escaños'),
                 ('https://www.galiciapress.es/articulo/politica/2026-10-25/6065328-manana-ultimo-dia-registrar-listas-partidos-coaliciones-juntas-electorales-provinciales', 'Europa Press, último día para registrar las listas (25-10-2026)'),
                 ('https://www.diariosigloxxi.com/texto-s/mostrar/680244/feijoo-exige-cabezas-lista-pp-arquitectos-reconstruccion-frente-abalos-koldos-sanchez', 'Servimedia, Feijóo presenta a sus cabezas de lista (25-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/25/abascal-presenta-manana-en-un-acto-en-talavera-toledo-a-los-cabezas-de-lista-de-vox-para-las-elecciones-del-29n/', 'Infobae, cabezas de lista de Vox (25-10-2026)'),
                 ('https://www.diariosigloxxi.com/texto-ep/mostrar/20261025201442/frente-amplio-encara-cierre-listas-lunes-incognita-candidaturas-varias-provincias', 'Europa Press, listas de Frente Amplio y Podemos (25-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/21/la-lider-de-sumar-ira-de-numero-4-en-la-lista-por-madrid-de-frente-amplio-al-congreso/', 'EFE, lista de Frente Amplio por Madrid (21-10-2026)'),
                 ('https://www.democrata.es/elecciones-generales-espana/consulte-aqui-lista-psoe-por-madrid-elecciones-29n-estos-son-candidatos-congreso-senado/', 'Demócrata, lista del PSOE por Madrid (14-10-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/22/comuns-avala-con-el-59-de-votos-la-lista-de-colau-al-29n-en-la-que-no-estara-aina-vidal/', 'EFE, lista de los Comuns (22-10-2026)'),
                 ('https://www.elnacional.cat/es/politica/estos-candidatos-psc-elecciones-generales-2026-listas-completas_1710943_102.html', 'El Nacional, listas del PSC'),
                 ('https://www.diarimes.com/es/actualidad/cataluna/261020/erc-ratifica-listas-29-n-rufian-frente-junqueras-amnistiado-cierre_239317.html', 'Diari Més, listas de ERC (20-10-2026)'),
                 ('https://www.democrata.es/politica/feijoo-releva-al-60-de-sus-cabezas-de-lista-al-congreso-y-los-reunira-el-domingo-en-salamanca/', 'Demócrata, cabezas de lista del PP'),
                 ('https://eldiario.es/madrid/dimite-delegado-gobierno-madrid-quedarse-fuera-listas-psoe-elecciones_1_13613892.html', 'elDiario.es, dimisión de Francisco Martín (25-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='voto-correo-29n', fecha='2026-10-25',
        foto=dict(src='img/actualidad/fotos/voto-correo-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una cola ante el mostrador de Correos, sobres en la mano, y dos buzones amarillos junto al mapa de España: un collage.'),
        titulo='Siete de cada cien electores pidieron votar por correo en 2023, más del triple que en 2015: en Bizkaia, 14; en Girona, 3', serie='29n', figura=0,
        descripcion='Las dos generales con más voto por correo fueron las de verano, 2016 y 2023. El 29N cae en noviembre, como 2011 y 2019, cuando se pidió mucho menos. Y en 2023 no lo pidieron sobre todo los mayores: lo pidieron los electores de 25 a 44 años y los de las ciudades grandes.',
        compara='Las solicitudes de voto por correo aceptadas por la Oficina del Censo Electoral en las generales de 2004 a 2023, por cada 100 electores residentes en España, por provincia y, en 2023, por edad y tamaño del municipio.',
        limites='Son solicitudes, no votos, contadas por la provincia de inscripción del elector. El INE y Correos cuentan cosas distintas y sus totales no coinciden. Los votos emitidos solo están en notas de prensa de Correos y faltan o son provisionales en 2008, 2011 y 2015. No incluye a los residentes en el extranjero. Las razones de los cambios (vacaciones, pandemia) son hipótesis. El voto por correo no se puede separar en los resultados.',
        fuentes=[('https://www.ine.es/', 'INE, Oficina del Censo Electoral, solicitudes de voto por correo en las elecciones generales de 2004 a 2023 (tablas 59755, 59758, 59759, 59763 y 59764 para 2023)'),
                 ('https://www.correos.com/sala-prensa/exito-en-la-gestion-del-voto-por-correo-que-marca-record-historico-con-2-471-935-votos-admitidos-para-las-elecciones-generales/', 'Correos, récord histórico con 2.471.935 votos admitidos (22-7-2023)'),
                 ('https://www.correos.com/sala-prensa/ya-se-puede-solicitar-el-voto-por-correo-para-las-elecciones-generales-del-29-de-noviembre/', 'Correos, ya se puede solicitar el voto por correo para el 29N (6-10-2026)'),
                 ('https://www.europapress.es/nacional/noticia-abascal-ayuso-cuestionan-voto-correo-podra-solicitar-manana-29n-20261005151138.html', 'Europa Press, Abascal y Ayuso cuestionan el voto por correo (5-10-2026)'),
                 ('https://diariodeavisos.elespanol.com/2026/10/correos-canarias-voto-feijoo/', 'Diario de Avisos, Correos en Canarias responde a Feijóo (8-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='corrupcion-penaliza-voto-29n', fecha='2026-10-25',
        foto=dict(src='img/actualidad/fotos/corrupcion-penaliza-voto-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna roja resquebrajada que pierde sobres junto a una urna azul casi vacía: un collage.'),
        titulo='29N: la corrupción le cuesta votos al PSOE, pero apenas se los da al PP', serie='29n',
        descripcion='Quince años de barómetros del CIS, 528.018 entrevistas: quien cita la corrupción como problema deja más a su partido, pero el gran rival recoge poco de ese voto: la mayor parte va a la abstención o a terceros partidos. Hoy le cuesta al PSOE 9,5 puntos de fidelidad.',
        compara='La fidelidad de voto (voto más simpatía igual al recuerdo de voto en las últimas generales) de quienes citan la corrupción y el fraude entre los tres principales problemas de España y de quienes no, en 166 barómetros del CIS de diciembre de 2010 a octubre de 2026 (528.018 entrevistas), por año y por etapa de gobierno; el destino del voto de quienes la citan; la serie mensual de la corrupción como problema; la comparación con otros problemas en 2023-2026; y la repetición de voto en los poselectorales de 2015, 2016, noviembre de 2019 y 2023.',
        limites='Es una encuesta: mide intenciones, no votos. El recuerdo de voto del CIS sobrerrepresenta al PSOE e infrarrepresenta al PP y a Vox. Antes de septiembre de 2018 solo hay intención de voto en uno de cada tres barómetros, y algunos estudios antiguos no traen ponderación. Citar la corrupción puede ser consecuencia del desencanto y no su causa. En los poselectorales de 2015 y 2016 la pregunta es de lista cerrada y no es comparable en nivel con la pregunta abierta de los barómetros. Que un pico coincida con un caso judicial no prueba que el caso lo causara.',
        calculo='Regresiones lineales de la fidelidad (0 o 100) sobre citar la corrupción, con controles de edad, sexo, estudios e ideología (lineal y al cuadrado), efectos fijos de provincia y de barómetro y errores agrupados por provincia; margen de error al 95%. Porcentajes ponderados cuando el estudio trae ponderación. La serie mensual agregada se ajusta con tendencia lineal y errores HAC. Pruebas de robustez: sin controles, con y sin ponderación, errores agrupados por barómetro, sin Cataluña, País Vasco y Navarra, solo el primer problema, sin indecisos y logit (efecto marginal medio); ninguna cambia el signo ni el orden de las etapas.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, microdatos de 166 barómetros de diciembre de 2010 a octubre de 2026 (estudios 2856 a 3582)'),
                 ('https://www.cis.es/estudios/catalogo-estudios', 'CIS, microdatos de los barómetros de septiembre de 2001 a noviembre de 2010 (estudios 2429 a 2853), solo para la serie de problemas'),
                 ('https://www.cis.es/estudios/catalogo-estudios', 'CIS, estudios poselectorales 3126 (2015), 3145 (2016), 3269 (noviembre de 2019) y 3420 (2023), microdatos'),
                 ('https://econpapers.repec.org/paper/iebwpaper/doc2011-9.htm', 'Elena Costas-Pérez, Albert Solé-Ollé y Pilar Sorribas-Navarro, Corruption scandals, press reporting, and accountability. Evidence from Spanish mayors, IEB (2011)'),
                 ('https://doi.org/10.1017/psrm.2015.8', 'Pablo Fernández-Vázquez, Pablo Barberá y Gonzalo Rivero, Rooting Out Corruption or Rooting for Corruption?, Political Science Research and Methods (2016)'),
                 ('https://www.legaltoday.com/rincon-de-reuters/rajoy-admite-que-se-equivoco-al-confiar-en-barcenas-2013-08-01/', 'Reuters en Legal Today, Rajoy admite que se equivocó al confiar en Bárcenas (1-8-2013)'),
                 ('https://www.laprensa.hn/mundo/escandalo-en-espana-por-cuentas-del-partido-popular-IALP362794', 'AP en La Prensa, Escándalo en España por cuentas del Partido Popular (31-1-2013)'),
                 ('https://www.ultimahora.es/noticias/nacional/2014/10/27/136499/suspende-militancia-implicados-operacion-punica/relacionadas.html', 'Europa Press en Última Hora, el PP suspende de militancia a los detenidos en la operación Púnica (27-10-2014)'),
                 ('https://www.elsaltodiario.com/corrupcion/la-sentencia-de-la-gurtel-acredita-la-existencia-de-la-caja-b-del-pp-y-lo-condena-por-corrupcion', 'El Salto, la sentencia de la Gürtel (24-5-2018)'),
                 ('https://www.infobae.com/espana/2024/02/22/el-juez-deja-en-libertad-a-koldo-garcia-pero-le-prohibe-salir-del-pais-durante-la-investigacion-por-la-trama-de-mascarillas/', 'Infobae, el juez deja en libertad a Koldo García (22-2-2024)'),
                 ('https://www.infobae.com/espana/2025/06/12/las-15-frases-mas-destacadas-de-pedro-sanchez-en-la-rueda-de-prensa-tras-el-informe-de-la-uco-y-la-dimision-de-santos-cerdan/', 'Infobae, las frases de Pedro Sánchez tras el informe de la UCO sobre Santos Cerdán (12-6-2025)'),
                 ('https://www.infobae.com/espana/2025/07/01/el-psoe-entierra-a-santos-cerdan-en-menos-de-tres-semanas-tras-su-entrada-en-prision-de-poner-la-mano-en-el-fuego-por-el-a-decir-que-no-tiene-que-ver-con-ellos/', 'Infobae, Santos Cerdán entra en prisión (1-7-2025)'),
                 ('https://maldita.es/desinfo/20260520/preguntas-y-respuestas-imputacion-zapatero-plus-ultra/', 'Maldita.es, la imputación de Zapatero en el caso Plus Ultra (20-5-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/20/feijoo-cree-que-sanchez-convoca-elecciones-para-que-no-le-investiguen-y-apunta-a-dinero-de-prostitucion-en-sus-primarias/', 'Europa Press en Infobae, entrevista de Feijóo en la Cadena COPE (20-10-2026)')],
        enlaces=[],
        lugar='España',
    ),
    dict(
        slug='adelante-andalucia-psoe-29n', fecha='2026-10-26',
        foto=dict(src='img/actualidad/fotos/adelante-andalucia-psoe-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una urna, dos montones de papeletas, verdes y rojas, y una calle blanca de un pueblo andaluz: un collage.'),
        titulo='Uno de cada tres votantes de Adelante venía del PSOE, pero el mapa andaluz no muestra la fuga', serie='29n',
        descripcion='Adelante Andalucía pasó de 168.448 a 402.244 votos el 17M y va sola el 29N. Las encuestas dicen que entre un cuarto y un tercio de sus votantes había votado al PSOE en 2022, pero en los 785 municipios sube lo mismo donde el PSOE se hunde que donde crece.',
        compara='El voto de Adelante Andalucía, el PSOE-A y Por Andalucía en las autonómicas de 2022 y 2026 en los 785 municipios andaluces (resultados de la Junta), por provincia, por quintiles de cambio del PSOE y en los 52 municipios de más de 20.000 electores; el origen del voto de Adelante según el recuerdo de voto de las encuestas del CENTRA y del CIS; y el voto por edad en el postelectoral del CENTRA.',
        limites='Los resultados agregados por municipio no dicen quién cambió su voto: un trasvase del PSOE a Adelante repartido por igual en todo el territorio no se vería en la comparación entre municipios. El recuerdo de voto de las encuestas se desvía del resultado real (el postelectoral del CENTRA da a Adelante el 17,2 % de los votantes, frente al 9,6 % real) y las muestras provinciales son pequeñas. Las cifras del CIS vienen de la crónica de Europa Press, no de los microdatos. Las autonómicas no predicen las generales: el barómetro del CENTRA mide voto al Parlamento andaluz.',
        calculo='Porcentajes sobre voto válido, por municipio, con los resultados definitivos de la Junta de Andalucía. Regresión lineal del cambio de Adelante sobre el cambio del PSOE-A y el de Por Andalucía, con efectos fijos de provincia, ponderada por censo y con errores agrupados por provincia; repetida con porcentajes sobre censo y controlando el cambio de participación, con el mismo resultado. Encuestas del CENTRA: preelectoral ponderado con su coeficiente; postelectoral sin ponderar (muestra proporcional), solo quienes dicen haber votado.',
        fuentes=[('https://resultadoseleccionesandalucia.es', 'Junta de Andalucía, Sistema de Información Electoral (SIEL), resultados por municipio de las elecciones al Parlamento de Andalucía de 2022 y 2026'),
                 ('https://www.centrodeestudiosandaluces.es/encuestas/estudio-preelectoral-elecciones-autonomicas-2026', 'Fundación CENTRA, Estudio preelectoral elecciones autonómicas 2026, microdatos'),
                 ('https://www.centrodeestudiosandaluces.es/encuestas/cat/electorales', 'Fundación CENTRA, Estudio postelectoral elecciones autonómicas 2026, microdatos'),
                 ('https://www.centrodeestudiosandaluces.es/barometro/barometro-andaluz-de-septiembre-de-2026', 'Fundación CENTRA, Barómetro Andaluz de septiembre de 2026, estimación de voto y frecuencias'),
                 ('https://www.europapress.es/andalucia/' + 'noticia-vox-pp-partidos-mayor-fidelidad-17m-psoe-movilizaria-mas-generales-cis-20260627100950.html', 'Europa Press, el postelectoral del CIS en Andalucía (27-6-2026)'),
                 ('https://www.europapress.es/andalucia/' + 'noticia-moreno-pierde-mayoria-absoluta-no-evita-lio-vox-subida-adelante-nuevo-descenso-psoe-20260517230451.html', 'Europa Press, resultados del 17M (17-5-2026)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/23/adelante-logra-los-avales-para-las-elecciones-y-espera-parar-a-la-derecha-con-andalucismo/', 'EFE en Infobae, Adelante logra los avales para las elecciones (23-10-2026)'),
                 ('https://www.europapress.es/andalucia/' + 'noticia-adelante-andalucia-afea-criticas-ir-solitario-29n-no-cuestiona-cataluna-euskadi-galicia-20261009095337.html', 'Europa Press, José Ignacio García en La 1 de TVE (9-10-2026)'),
                 ('https://www.europapress.es/andalucia/' + 'cadiz-00351/noticia-adelante-defiende-papeleta-29n-frente-lio-izquierda-problema-no-division-20261013132040.html', 'Europa Press, José Ignacio García en Jerez de la Frontera (13-10-2026)'),
                 ('https://www.europapress.es/andalucia/' + 'noticia-maillo-afea-adelante-decida-ir-solitario-29n-hablar-nadie-fragmentacion-conviene-pp-vox-20261014095424.html', 'Europa Press, Antonio Maíllo en Canal Sur Televisión (14-10-2026)'),
                 ('https://www.europapress.es/andalucia/' + 'noticia-psoe-cedera-frente-amplio-numero-candidaturas-andaluzas-senado-29n-sevilla-huelva-20261020133736.html', 'Europa Press, el PSOE-A y el Frente Amplio en el Senado (20-10-2026)'),
                 ('https://www.eldiario.es/andalucia/generacion-mollete-caldo-cultivo-explica-sorpresa-adelante-andalucia_1_13228933.html', 'elDiario.es, «La generación mollete» (Carla Rivero, 18-5-2026)'),
                 ('https://www.idpbarcelona.net/docs/public/iccaa/2022/andalucia_2022.pdf', 'Mª Reyes Pérez Alberdi, Andalucía, en Informe Comunidades Autónomas 2022, Instituto de Derecho Público (2023)')],
        enlaces=[],
        lugar='Andalucía',
    ),
    dict(
        slug='inmigracion-cuesta-votos-psoe-29n', fecha='2026-10-26',
        foto=dict(src='img/actualidad/fotos/inmigracion-cuesta-votos-psoe-29n.jpg', ancho=1280, alto=720, ia=True,
                  pie='Una mano deposita un voto en una urna roja, junto a una calle de bloques con vecinos que vuelven de la compra: un collage.'),
        titulo='La inmigración ya le cuesta votos al PSOE, no solo al PP', serie='29n',
        descripcion='Veintiséis años de barómetros del CIS, 806.169 entrevistas: en 2006 la inmigración era el gran problema y no movía el voto; desde 2018 aleja del PP hacia Vox a quien la cita. En 2026 los votantes socialistas que la nombran son 13,6 puntos menos fieles, el peor dato de la serie, y se reparten entre el PP, Vox y la abstención.',
        compara='La fidelidad de voto (voto más simpatía igual al recuerdo de voto en las últimas generales) de quienes citan la inmigración entre los tres principales problemas de España y de quienes no, en 278 barómetros del CIS de septiembre de 2000 a octubre de 2026 (806.169 entrevistas), año a año, para los votantes del PSOE y del PP; el destino de ese voto desde 2018; el flujo de voto en 2026 de los votantes de PSOE, PP y Vox en 2023 que la citan; cuántos la citan según adónde va su voto; y el porcentaje de votantes del PSOE que la citan por provincia desde diciembre de 2023.',
        limites='Es una encuesta: mide intenciones, no votos. El recuerdo de voto del CIS sobrerrepresenta al PSOE e infrarrepresenta al PP y a Vox. Antes de septiembre de 2018 solo hay intención de voto en uno de cada tres barómetros, y algunos estudios antiguos no traen ponderación. Los ficheros de 2000 a 2010 no permiten controlar por ideología, edad ni estudios, así que para esos años el modelo es reducido y no es del todo comparable con el posterior. Citar la inmigración puede ser consecuencia del alejamiento de un partido y no su causa. Las muestras provinciales son pequeñas en las provincias menos pobladas y en Ceuta y Melilla.',
        calculo='Regresiones lineales de la fidelidad (0 o 100) sobre citar la inmigración, año a año y por partido del recuerdo de voto. Desde 2011, con controles de edad, sexo, estudios, ideología (lineal y al cuadrado) y otros cinco problemas citados (el Gobierno, la corrupción, el paro, la economía y los políticos), efectos fijos de provincia y de barómetro y errores agrupados por provincia; de 2000 a 2010, solo sexo, corrupción y efectos fijos. Margen de error al 95%. El destino del voto se estima con el mismo modelo usando el voto a cada opción como resultado. Porcentajes ponderados cuando el estudio trae ponderación. Pruebas de robustez para 2026 y para diciembre de 2023 a octubre de 2026: sin otros problemas, sin controles, ponderado, sin Cataluña, País Vasco y Navarra, solo el primer problema, sin indecisos y logit (efecto marginal medio); el efecto sobre el PSOE en 2026 va de −11,8 a −18,9 puntos.',
        fuentes=[('https://www.cis.es/estudios/catalogo-estudios', 'CIS, microdatos de 278 barómetros de septiembre de 2000 a octubre de 2026 (estudios 2398 a 3582)'),
                 ('https://www.realinstitutoelcano.org/comentarios/la-opinion-publica-espanyola-sobre-la-inmigracion-en-contexto/', 'Rut Bermejo Casado y Carmen González Enríquez, La opinión pública española sobre la inmigración en contexto, Real Instituto Elcano (3-10-2024)'),
                 ('https://eprints.gla.ac.uk/197637', 'Laura Morales, Sergi Pardos-Prado y Virginia Ros, Issue emergence and the dynamics of electoral competition around immigration in Spain, Acta Politica (2015)'),
                 ('https://www.vozpopuli.com/actualidad/canarias-supera-falta-dos-meses-record-inmigrantes-ilegales-2006.html', 'EFE en Vozpópuli, Canarias supera el récord de llegadas de 2006 (4-11-2023)'),
                 ('https://www.infobae.com/espana/agencias/2026/10/20/feijoo-cree-que-sanchez-convoca-elecciones-para-que-no-le-investiguen-y-apunta-a-dinero-de-prostitucion-en-sus-primarias/', 'Europa Press en Infobae, entrevista de Feijóo en la Cadena COPE (20-10-2026)'),
                 ('https://democrata.es/elecciones-generales-espana/visita-abascal-aviles-desata-protestas-obliga-establecer-cordon-policial', 'Demócrata, la visita de Abascal a Avilés (21-10-2026)'),
                 ('https://www.vozpopuli.com/espana/politica/sanchez-defiende-su-regularizacion-masiva-espana-es-hija-de-la-migracion-y-no-sera-madre-de-la-xenofobia.html', 'Vozpópuli, Sánchez defiende la regularización en Barcelona (18-4-2026)'),
                 ('https://www.elsalvador.com/noticias/internacional/espana-preve-regularizar-a-500-000-inmigrantes/1260209/2026/', 'AFP en El Salvador, España prevé regularizar a 500.000 inmigrantes (27-1-2026)'),
                 ('https://www.elsalvador.com/noticias/internacional/espana-regulariza-a-migrantes-sin-papeles/1269825/2026/', 'AFP en El Salvador, España regulariza a migrantes sin papeles (14-4-2026)')],
        enlaces=[],
        lugar='España',
    ),
]

# Serie «Internacional»: elecciones de otros países contadas con mapas (decisión de Nacho, 26-10-2026: en Actualidad y en /temas/internacional/)
SERIES['internacional'] = 'Internacional'
PIEZAS += [
    dict(
        slug='brasil-lula-remontada-mapa-estados', fecha='2026-10-26', actualizado='2026-10-27 06:55',
        titulo='Lula pasó de perder por 2,2 millones de votos a ganar por 4,4: en el mapa de Brasil solo Minas Gerais cambió de color', serie='internacional',
        descripcion='En tres semanas, Lula sumó 10,4 millones de votos y Flávio Bolsonaro, 3,7. Casi la mitad de la subida de Lula salió del Sudeste, donde aun así perdió. Frente a 2022, 25 de los 27 estados votaron al mismo candidato, y la región Norte se decidió por 1.079 votos.',
        compara='La primera y la segunda vuelta de las presidenciales de Brasil de 2026 en los 27 estados (26 estados y el Distrito Federal), frente a la segunda vuelta de 2022; la ventaja del más votado en cada vuelta desde 1989, y la abstención en las presidenciales desde 1994.',
        limites='Son totales por estado: no dicen quién cambió su voto entre las dos vueltas ni quién votó solo en una de ellas, así que los votos que suma cada candidato son saldos, no trasvases. El mapa no incluye el voto en el exterior, que sí está en los totales nacionales. Los datos de 2026 son del portal de resultados del TSE y los de 2022 y la abstención desde 1994, de sus datos abiertos. La abstención se calcula sobre los electores con derecho a voto para presidente. En la primera vuelta, el color del mapa compara solo a Lula y a Flávio.',
        fuentes=[('https://resultados.tse.jus.br/oficial/app/index.html', 'Tribunal Superior Electoral de Brasil, resultados oficiales de la primera y la segunda vuelta de 2026 por estado'),
                 ('https://dadosabertos.tse.jus.br/', 'TSE, datos abiertos: votación por candidato, municipio y zona de 2022, y detalle de la votación por municipio y zona de 1994 a 2022 (abstención)'),
                 ('https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais.html', 'IBGE, mallas territoriales de los estados (vía click_that_hood), simplificadas'),
                 ('https://es-us.noticias.yahoo.com/lula-gana-elecciones-presidenciales-remontada-001814404.html', 'EFE vía Yahoo Noticias, Lula gana las elecciones presidenciales tras una remontada inédita ante Flávio Bolsonaro (25-10-2026)'),
                 ('https://www.poder360.com.br/poder-eleicoes-2026/leia-a-integra-do-pronunciamento-da-vitoria-de-lula-2/', 'Poder360, íntegra del discurso de la victoria de Lula (25-10-2026)'),
                 ('https://www.poder360.com.br/poder-eleicoes-2026/leia-e-assista-a-integra-do-discurso-de-flavio-bolsonaro/', 'Poder360, íntegra del discurso de Flávio Bolsonaro (25-10-2026)'),
                 ('https://www.brasildefato.com.br/2026/09/30/governos-de-lula-transformaram-o-nordeste-e-explicam-vitoria-folgada-na-regiao-afirma-cientista-politico/', 'Brasil de Fato, entrevista al politólogo Benedito Tadeu César (UFRGS) (30-9-2026)'),
                 ('https://revistaoeste.com/politica/flavio-supera-lula-pela-1a-vez-em-minas-mostra-quaest/', 'Revista Oeste, Minas Gerais y el ganador de las presidenciales desde 1989'),
                 ('https://www.planalto.gov.br/ccivil_03/constituicao/constituicao.htm', 'Constitución de la República Federativa de Brasil, artículo 14'),
                 ('https://www.bahianoticias.com.br/noticia/321931-desde-1989-quem-ganha-o-primeiro-turno-para-presidente-vence-tambem-o-segundo-e-tabu-pode-ser-quebrado', 'Bahia Notícias, desde 1989 quien gana la primera vuelta gana también la segunda (resultados de 1989)'),
                 ('https://www.gazetasp.com.br/cotidiano/44528-desde-diretas-ja-brasil-nunca-teve-virada-no-segundo-tur/', 'Gazeta SP (Folhapress), Brasil nunca tuvo una remontada en segunda vuelta desde las Diretas Já (resultados de 1989)')],
        enlaces=[],
        lugar='Brasil',
        foto=dict(src='img/actualidad/fotos/brasil-lula-remontada-mapa-estados.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Quién ganó en cada estado de Brasil en la segunda vuelta.', fuente='TSE, resultados oficiales por estado; contornos de IBGE'),
    ),
]

PIEZAS += [
    dict(
        slug='serbia-estudiantes-vucic-mapa-distritos', fecha='2026-10-27',
        titulo='Vučić ganó en los 25 distritos de Serbia en 2023; los estudiantes le han ganado en 18 y en Zaječar el recuento va por 31 votos', serie='internacional',
        descripcion='La Lista Estudiantil saca el 53,4% de los votos válidos y la de Aleksandar Vučić, el 39,7%, con el 97,6% de los colegios escrutados. Vučić perdió menos de 100.000 votos frente a 2023: lo que cambió fue que fueron a votar casi medio millón de personas más. Belgrado aporta casi seis de cada diez votos de la ventaja.',
        compara='Las legislativas anticipadas de Serbia del 25 de octubre de 2026 en los 25 distritos (24 distritos y la ciudad de Belgrado), frente a las legislativas de diciembre de 2023, y la lista del SNS frente a la segunda más votada en todas las legislativas desde 2012.',
        limites='Los resultados de 2026 son provisionales: faltan 201 de los 8.392 colegios (85 de ellos en el extranjero), así que los votos de cada lista subirán algo. La participación de 2026 se calcula sobre los electores de los colegios ya escrutados. Los totales por distrito no dicen quién cambió su voto ni quién votó por primera vez: son saldos, no trasvases. El mapa no incluye Kosovo (60 colegios y unos 100.000 electores inscritos en Serbia), el voto en el extranjero ni el de las prisiones, que sí están en los totales nacionales. Los porcentajes se calculan sobre los votos válidos y pueden diferir unas décimas de los oficiales de la RIK, que usan todos los votantes.',
        fuentes=[('https://www.rik.parlament.gov.rs/542645/rezultati/', 'Comisión Electoral de la República de Serbia (RIK), resultados de las legislativas de 2026 por colegio electoral y de 2023 por municipio'),
                 ('https://en.wikipedia.org/wiki/2022_Serbian_general_election', 'Wikipedia, resultados oficiales de las legislativas de 2012, 2014, 2016, 2020 y 2022 (de la RIK)'),
                 ('https://www.openstreetmap.org/relation/1677007', 'OpenStreetMap, contornos de los distritos administrativos de Serbia (ODbL), vía polygons.openstreetmap.fr, simplificados'),
                 ('https://www.elfinanciero.com.mx/mundo/2026/10/26/estudiantes-ganan-elecciones-en-serbia-terminan-con-gobierno-del-conservador-aleksandar-vucic/', 'EFE vía El Financiero, Estudiantes ganan elecciones en Serbia (26-10-2026)'),
                 ('https://es-us.noticias.yahoo.com/vucic-reconoce-derrota-movimiento-estudiantil-070622339.html', 'Reuters vía Yahoo Noticias, Vucic reconoce su derrota ante el movimiento estudiantil (26-10-2026)'),
                 ('https://www.eldiario.es/internacional/movimiento-estudiantil-pone-reinado-autoritario-12-anos-vucic-serbia_1_13614161.html', 'elDiario.es, Un movimiento estudiantil pone fin al reinado autoritario de 12 años de Vucic (26-10-2026)')],
        enlaces=[],
        lugar='Serbia',
        foto=dict(src='img/actualidad/fotos/serbia-estudiantes-vucic-mapa-distritos.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Quién ganó en cada distrito de Serbia en las legislativas del 25 de octubre.', fuente='RIK, resultados provisionales por colegio; contornos de OpenStreetMap'),
    ),
    dict(
        slug='quien-vota-barrios-renta-edad-inmigracion', fecha='2026-10-28',
        titulo='En los barrios ricos se vota 15 puntos más que en los pobres, y en las europeas, 22: quién vota en España según la renta, la edad y la inmigración', serie='29n',
        descripcion='En el 10% de secciones censales con más renta votó el 77,8% en las generales de 2023; en el 10% más pobre, el 62,6%. La distancia era de 7,9 puntos en 2004. Vox saca más en los barrios jóvenes y la inmigración baja la participación, pero no sube el voto a Vox.',
        compara='La participación y el voto en las elecciones al Congreso de 2004 a 2023, y en las municipales y europeas recientes, en las 36.462 secciones censales de España, agrupadas en diez tramos con el mismo censo según la renta, la pobreza, la edad media, la población extranjera, los estudios y el paro que el INE mide en cada sección.',
        limites='Son datos por sección, no por persona: que en las secciones más pobres se vote más a un partido no significa que cada persona pobre lo vote. Los deciles mezclan territorios (el 10% más pobre pesa mucho en Andalucía, Canarias y Extremadura) y las relaciones son descriptivas, no causas. Sin voto exterior (CERA). Los adultos sin derecho a voto son una estimación (adultos del padrón menos censo electoral). Las elecciones antiguas solo cuentan en las secciones que conservan su código de 2023. Las cifras usan todas las secciones con dato de renta y pueden diferir en unas décimas de las de otras piezas que filtran secciones distintas. Este texto estuvo en la portada del sitio hasta el 28 de octubre de 2026.',
        fuentes=[INTERIOR, INE,
                 ('https://www.eldiario.es/politica/barrios-pobres-van-votar-elecciones_1_1162754.html', 'elDiario.es, Braulio Gómez (Universidad de Deusto) sobre los barrios que no votan (7-4-2019)'),
                 ('https://www.foessa.es/main-files/uploads/sites/16/2019/05/3.4.pdf', 'Manuel Trujillo y Braulio Gómez Fortes, La segregación electoral interurbana en España, VIII Informe FOESSA (2019)'),
                 ('https://www.elobservador.com.uy/nota/por-que-sera-decisivo-el-voto-joven-el-23j-202371961447', 'EFE vía El Observador, Manuel Mostaza sobre el voto joven (19-7-2023)'),
                 ('https://www.eldiario.es/desalambre/voto-inmigrante-extranjeros-legalmente-espana_1_1636823.html', 'elDiario.es, Rafael Naranjo (Universidad de Málaga) sobre el voto de los extranjeros (15-5-2019)'),
                 ('https://doi.org/10.21308/recp.62.01', 'Irene Delgado Sotillos, Revista Española de Ciencia Política, n.º 62 (2023)'),
                 ('https://www.eldiario.es/piedrasdepapel/Vox-derecha-populista-escision-PP_6_850474947.html', 'Héctor Meleiro, Piedras de Papel, elDiario.es (26-12-2018)')],
        enlaces=[],
        lugar='España',
    ),
]

PIEZAS += [
    dict(
        slug='israel-pactos-escanos-knesset', fecha='2026-10-28',
        titulo='Netanyahu se queda a cuatro escaños de la mayoría con el 40% escrutado, y la oposición solo llega a 61 con los partidos árabes', serie='internacional',
        descripcion='Con 2,1 millones de votos contados, los cinco partidos del Gobierno saliente suman 57 de los 120 escaños de la Knesset y los cuatro de la oposición sionista, 47. Los dos partidos árabes tienen 16, y su peso ha ido subiendo a medida que avanzaba el recuento. Estas son las combinaciones posibles.',
        compara='El reparto provisional de escaños de las legislativas de Israel del 27 de octubre de 2026, con cerca del 40% de los votos contados, las combinaciones de partidos que llegan a la mayoría de 61 y la evolución del recuento durante la madrugada; frente a los resultados de 2022.',
        limites='Resultados provisionales: el recuento oficial estaba en torno al 40% (2.122.846 votos válidos) y faltan, entre otros, los votos de los soldados. Los escaños cambiarán. Las cifras proceden del Comité Central Electoral, pero se han tomado de la prensa israelí porque la web del Comité no es accesible desde fuera de Israel. Las coaliciones del gráfico son sumas aritméticas, no escenarios probables: las posiciones de cada partido se citan en el texto. Los bloques son los declarados antes de la votación.',
        fuentes=[('https://www.kikar.co.il/political-news/israel-elections-voting-turnout', 'Kikar HaShabbat, recuento oficial del Comité Central Electoral de Israel a las 4.03, 4.47 y 5.57 del 28-10-2026 (votos por partido)'),
                 ('https://www.israelnationalnews.com/news/435272', 'Arutz Sheva, reparto provisional de escaños con el 37,4% de los votos contados (28-10-2026)'),
                 ('https://en.wikipedia.org/wiki/2026_Israeli_legislative_election', 'Wikipedia, resultados de 2022 y composición de las listas de 2026'),
                 ('https://www.telemundo40.com/noticias/mundo/israel-elecciones-kneset-resultados-gadi-eisenkot-benjamin-netanyahu/2554061/', 'EFE vía Telemundo, Aún sin resultados electorales, opositor Eisenkot afirma triunfo (27-10-2026)'),
                 ('https://www.elconfidencial.com/mundo/2026-10-28/netanyahu-castigado-su-bloque-cae-en-escanos_4454401/', 'El Confidencial, Israel castiga (a medias) a Netanyahu (28-10-2026)'),
                 ('https://es-us.noticias.yahoo.com/elecciones-israel-participaci%C3%B3n-r%C3%A9cord-sondeos-023026272.html', 'France 24 vía Yahoo Noticias, participación récord y encuestas a pie de urna (28-10-2026)'),
                 ('https://www.infobae.com/america/mundo/2026/10/27/el-bloque-de-eisenkot-aventaja-a-netanyahu-en-las-elecciones-de-israel-pero-ninguno-logra-mayoria/', 'Infobae, el proceso de formación de Gobierno (27-10-2026)')],
        enlaces=[],
        lugar='Israel',
        foto=dict(src='img/actualidad/fotos/israel-pactos-escanos-knesset.jpg', ancho=1280, alto=720, grafico=True,
                  pie='Las coaliciones posibles en la Knesset con el recuento provisional del 28 de octubre.', fuente='Comité Central Electoral de Israel, recuento provisional al 40%'),
    ),
]

# Antetítulo de cada pieza (portada, cabecera y «Sigue leyendo»): el tema o el gancho de actualidad de esa pieza,
# no el nombre de la serie, que se repetiría en todas. Las que no tienen uno usan la comunidad o la serie.
ANTETITULOS = {
    'quien-vota-barrios-renta-edad-inmigracion': 'Quién vota',
    'israel-elecciones-encuestas-knesset': 'Israel vota',
    'alvise-salf-donde-vota-29n': '¿Escaño para Alvise?',
    'feijoo-albiol-barcelona-disturbios-29n': 'Feijóo en Barcelona',
    'rufian-montero-la-revuelta-29n': 'El tándem de La Revuelta',
    'comuns-psc-senado-girona-lleida-tarragona-29n': 'Senado en Cataluña',
    'pacto-pp-vox-senado-provincias-29n': 'Tres quintos en el aire',
    'brasil-lula-remontada-mapa-estados': 'Brasil, estado a estado',
    'serbia-estudiantes-vucic-mapa-distritos': 'Serbia, distrito a distrito',
    'israel-pactos-escanos-knesset': 'Israel, las cuentas del 61',
    'calle-que-parte-barcelona': 'Dos fronteras',
    'voto-correo-29n': 'Votar desde casa',
    'mujeres-jovenes-voto-29n': 'Brecha de género',
    'adelante-andalucia-psoe-29n': 'La izquierda andaluza',
    'corrupcion-penaliza-voto-29n': 'Corrupción y 29N',
    'inmigracion-cuesta-votos-psoe-29n': 'Inmigración y 29N',
    'quien-vota-que-barrios-29n': 'Crónica del domingo',
    'psoe-primera-fuerza-29n': 'El sorpasso que no sale',
    'encuestas-semana-29n': 'Las encuestas, semana a semana',
    'listas-29n-quien-encabeza': 'Quién sale y quién no',
    'cinco-semanas-29n-la-semana-en-el-mapa': 'Crónica del sábado',
    'ganar-por-un-voto-29n': 'Un voto de diferencia',
    'barcelona-madrid-clasico-del-voto-29n': 'El otro Clásico',
    'asi-queda-el-mapa-29n': 'El mapa de partida',
    'coaliciones-quien-va-con-quien-29n': 'Quién va con quién',
    'provincias-en-el-filo-29n': 'Los escaños del filo',
    'pueblos-unanimes-empates-29n': 'Empates y unanimidades',
    'feijoo-aborto-eutanasia-sanidad-publica-29n': 'Aborto y eutanasia',
    'ivan-redondo-12-millones-derecha-29n': 'La aritmética del bloque',
    'salario-minimo-provincias-feijoo-29n': 'El sueldo del debate',
    'teruel-cha-izquierda-escano-29n': 'El voto útil en Teruel',
    'sanchez-revuelta-broncano-voto-joven-29n': 'La generación Broncano',
    'republica-mapa-1936-hoy': 'Noventa años después',
    'lorca-fuente-vaqueros-viznar-1936': 'Los pueblos de Lorca',
    'pueblos-guerra-civil-voto-1936': 'Antes de la guerra',
    'mujeres-1933-frente-popular-1936': 'El primer voto de las mujeres',
    'fieles-1936-izquierda-derecha': 'Noventa años en el mismo lado',
    'abstencion-anarquista-cnt-1933-1936': 'Obreros, no votéis',
    'pueblos-bajo-el-agua-1936': 'Bajo el embalse',
    'pueblos-que-ya-no-existen-1936': 'Municipios borrados',
    'asturias-1934-1936-revolucion-urnas': 'De las barricadas a las urnas',
    'cataluna-lliga-front-esquerres-1933-1936': 'Del balcón a la cárcel',
    'pueblos-colonizacion-franquismo-voto': 'Los pueblos de los colonos',
    'girona-1936-participacio': 'Les urnes del 1936',
    'capitales-partidas-por-barrios': 'Ciudades partidas',
    'polaritzacio-girona': "Una ciutat d'illes",
    'frontera-renta-pp-junts-pnv-29n': 'La frontera del dinero',
    'inmigracion-preocupa-voto-vox-29n': 'La inquietud y la papeleta',
    'termometro-temas-inmigracion-29n': 'El termómetro de los temas',
    'vivienda-preocupa-voto-sumar-29n': 'La casa en la urna',
    'barrios-rentistas-pp-psoe-29n': 'Dividendos y alquileres',
    'casas-vacias-segundas-residencias': 'La casa cerrada',
    'escanos-en-el-filo-29n': 'La aritmética del último escaño',
    'oficios-y-voto-municipios-29n': 'El despacho y la urna',
    'vox-barrios-obreros-clase-29n': 'El peón y la papeleta',
    'voto-jubilados-secciones-29n': 'El voto que no se mueve',
    'voto-autonomos-secciones-29n': 'La persiana y la urna',
    'ley-nietos-donde-estan-29n': 'Nietos sin papeleta',
    'pensiones-revalorizacion-29n': 'Dos Españas jubiladas',
    'vox-galicia-coruna-abascal-29n': 'La espina de Abascal',
    'funcionarios-pagas-extra-29n': 'La nómina de enero',
    'trump-espana-invadida-inmigracion-29n': 'Lo que se ve y lo que no',
    'vox-pp-senado-pacto-29n': 'Las 19 del pacto',
    'frente-amplio-podemos-madrid-escanos-29n': 'Dos papeletas en Madrid',
    'barrios-donde-vota-menos-de-la-mitad': 'Ni la mitad a las urnas',
    'salarios-pensiones-ayudas-espana': 'De qué vive cada barrio',
    'municipios-izquierda-1977-derecha-2023': 'De feudo a vuelco',
    'calle-que-parte-madrid': 'Dos aceras, dos ganadores',
    'barrios-pobres-derecha-ricos-izquierda': 'Ni tan ricos ni tan obreros',
    'psoe-cinco-barrios-ceuta': 'Un partido, dos extremos',
    'pp-cinco-pueblos-galicia': 'Del 81% al cero',
    'vox-cinco-barrios-el-ejido-ceuta': 'El techo de Vox',
    'sumar-cinco-pueblos-marinaleda': 'Del 68,6% al 0,3%',
    'bildu-cinco-pueblos-lizartza': 'Del 78% al 0,3%',
    'pnv-cinco-pueblos-bermeo': 'Un techo que baja',
    'cc-cinco-barrios-la-orotava': 'Dos islas, dos partidos',
    'erc-cinco-pueblos-blancafort-flix': 'De 734 a 42',
    'junts-cinco-pueblos-amer': 'El pueblo de Puigdemont',
    'bng-cinco-pueblos-allariz': 'Ganar en una sola',
    'palencia-psoe-lista-29n': 'Una lista vacía',
    'albiol-badalona-pp-29n': 'El alcalde y la marca',
    'senado-psoe-frente-amplio-29n': 'Tres de cuatro',
    'ley-nietos-voto-exterior-29n': 'Las papeletas que llegan de fuera',
    'canarias-unidad-pueblo-canario-29n': 'Una papeleta en las islas',
    'pactos-izquierda-mapa-final-29n': 'El mapa que dejó el plazo',
    'mapa-coaliciones-izquierda-29n': 'Juntos o separados, desde 2015',
    'rufian-fracaso-lista-unitaria-29n': 'Lo que valía la suma',
    'desahucios-ocupaciones-cgpj-29n': 'Dos verbos para una puerta',
    'cis-tezanos-estimacion-29n': 'La hemeroteca del CIS',
    'pensiones-censo-mayores-29n': 'El censo envejece',
    'ceuta-melilla-participacion-29n': 'Dos ciudades en cada ciudad',
    'minguez-lleida-29n': 'Un escaño por 3.500 votos',
    'madrid-barrio-a-barrio-29n': 'El sur aguanta, el resto cambia',
    'barcelona-barrio-a-barrio-29n': 'Adiós al amarillo',
    'valencia-barrio-a-barrio-29n': 'La izquierda que se encogió',
    'sevilla-barrio-a-barrio-29n': 'Ganar calles, perder votos',
    'zaragoza-barrio-a-barrio-29n': 'Una ciudad a cara o cruz',
    'malaga-barrio-a-barrio-29n': 'Dos Málagas en las urnas',
    'girona-barri-a-barri-29n': 'Dues Girones a les urnes',
    'girona-esco-285-vots-29n': 'Per una mesa de vots',
    'junts-girona-puigdemont-29n': 'El vot amb dues cares',
    'alianca-catalana-ceo-mapa-ca': 'El CEO i Aliança',
    'blocs-i-cases-girona': 'El Cadastre i les urnes',
    'salaris-pensions-ajudes-girona': 'De què viu cada barri',
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
    'precio-del-escano-29n': 'No todos los votos valen igual',
    'senado-29n': 'Tres votos, un escaño',
    'votos-sin-escano-29n': 'Papeletas que no eligen a nadie',
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
.tipo{font-family:var(--ui);font-size:.66rem;font-weight:600;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-right:6px;opacity:.85}
.tipo.t-patron,.tipo.t-hipotesis{color:var(--fg);opacity:1;border-bottom:1px dotted var(--muted)}
.etiquetas{font-family:var(--ui);font-size:.85rem;color:var(--muted);margin:.8rem 0 0}.etiquetas a{color:var(--muted)}
aside.municipios-pieza{background:var(--surface);border:1px solid var(--rule);border-radius:8px;padding:4px 16px 12px;margin:2rem 0;font-family:var(--ui)}
aside.municipios-pieza h2{font-size:1.1rem;margin:.8rem 0 .3rem}aside.municipios-pieza p{font-size:.92rem;color:var(--muted);margin:0 0 .5rem}
aside.municipios-pieza ul{columns:2 14rem;column-gap:2rem;margin:0;padding-left:1.1rem}aside.municipios-pieza li{break-inside:avoid;margin:2px 0}
aside.municipios-pieza .prov{color:var(--muted);font-size:.9em}
@media (min-width:1100px){main p[data-tipo]{position:relative}main p[data-tipo]>.tipo{position:absolute;right:100%;top:.45em;margin-right:18px;white-space:nowrap}}
</style>"""


def fecha_larga(f):
    # f: 'AAAA-MM-DD' o, en las actualizaciones, 'AAAA-MM-DD HH:MM' (hora peninsular)
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    dia, _, hora = f.partition(' ')
    a, m, d = dia.split('-')
    return f'{int(d)} de {meses[int(m) - 1]} de {a}' + (f', a las {hora.replace(":", ".")}' if hora else '')


def fecha_iso(f):
    """'AAAA-MM-DD HH:MM' (hora de Madrid) → ISO 8601 con zona; una fecha sola se deja como está."""
    if ' ' not in f:
        return f
    from zoneinfo import ZoneInfo
    return datetime.datetime.strptime(f, '%Y-%m-%d %H:%M').replace(tzinfo=ZoneInfo('Europe/Madrid')).isoformat()


def nav(prefijo, actual):
    items = [('', 'Mapa de resultados'), ('elecciones/', 'Por territorio'), ('municipio/', 'Municipios'), ('municipio/barrios/', 'Barrios'), ('temas/', 'Temas'), ('encuestas/', 'Encuestas'),
             ('atlas/index.html', 'Atlas'), ('actualidad/index.html', 'Actualidad'),
             ('actualidad/#comunidades', 'Comunidades'), ('actualidad/#historia', 'Historia electoral'),
             ('sobre-mi.html', 'Sobre mí')]
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
<link rel="alternate" type="application/rss+xml" title="Mapa Electoral · Actualidad" href="{BASE}/actualidad/feed.xml">
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


TIPOS = {'dato': 'Dato', 'patron': 'Patrón', 'hipotesis': 'Hipótesis', 'contexto': 'Contexto'}


# Peces escrites directament en català (idioma='ca'): el text ja ve en català del fitxer de treball;
# aquí es tradueix el que hi posa aquest script (capçalera, signatura, fitxa de mètode, «Segueix llegint»...).
MESOS_CA = ['de gener', 'de febrer', 'de març', "d'abril", 'de maig', 'de juny', 'de juliol', "d'agost", 'de setembre', "d'octubre", 'de novembre', 'de desembre']
CA = [
    ('<html lang="es">', '<html lang="ca">'), ('<meta property="og:locale" content="es_ES">', '<meta property="og:locale" content="ca_ES">'),
    ('"inLanguage": "es"', '"inLanguage": "ca"'),
    ('aria-label="Secciones del sitio"', 'aria-label="Seccions del lloc"'), ('>Mapa de resultados<', '>Mapa de resultats<'), ('elecciones/">Por territorio<', 'elecciones/">Per territori<'), ('municipio/">Municipios<', 'municipio/">Municipis<'), ('temas/">Temas<', 'temas/">Temes<'), ('encuestas/">Encuestas<', 'encuestas/">Enquestes<'), ('barrios/">Barrios<', 'barrios/">Barris<'),
    ('>Actualidad</a> · ', '>Actualitat</a> · '), ('<p class="firma">Por <a href="../../sobre-mi.html">', '<p class="firma">Per <a href="../../sobre-mi-ca.html">'),
    ('aria-current="page">Actualidad</a>', 'aria-current="page">Actualitat</a>'), ('href="../../abstencion.html">Cataluña<', 'href="../../ca.html">Catalunya<'),
    ('>Cataluña<', '>Catalunya<'), ('actualidad/#comunidades">Comunidades<', 'actualidad/#comunidades">Comunitats<'), ('actualidad/#historia">Historia electoral<', 'actualidad/#historia">Història electoral<'), ('href="../../sobre-mi.html">Sobre mí<', 'href="../../sobre-mi-ca.html">Sobre mi<'),
    ('Ilustración generada con IA para Mapa Electoral.', 'Il·lustració generada amb IA per a Mapa Electoral.'), ('>Uso de IA<', ">Ús d'IA<"),
    ('<p class="etiquetas">Cada párrafo lleva una etiqueta: <b>dato</b> (cifra comprobable con las fuentes), <b>patrón</b> (relación que se repite, sin afirmar la causa), <b>hipótesis</b> (explicación posible, sin dos fuentes independientes) o <b>contexto</b> (hechos y declaraciones publicados por otros, enlazados). <a href="../../atlas/politica-editorial/#verificacion">Cómo verificamos</a></p>',
     "<p class=\"etiquetas\">Cada paràgraf porta una etiqueta: <b>dada</b> (xifra comprovable amb les fonts), <b>patró</b> (relació que es repeteix, sense afirmar-ne la causa), <b>hipòtesi</b> (explicació possible, sense dues fonts independents) o <b>context</b> (fets i declaracions publicats per altres, enllaçats). <a href=\"../../atlas/politica-editorial/#verificacion\">Com verifiquem</a> (en castellà)</p>"),
    ('t-dato">Dato<', 't-dato">Dada<'), ('t-patron">Patrón<', 't-patron">Patró<'), ('t-hipotesis">Hipótesis<', 't-hipotesis">Hipòtesi<'), ('t-contexto">Contexto<', 't-contexto">Context<'),
    ('<h2>Método y fuentes</h2>', '<h2>Mètode i fonts</h2>'), ('<dt>Qué se compara</dt>', '<dt>Què es compara</dt>'), ('<dt>Límites</dt>', '<dt>Límits</dt>'),
    ('<dt>Cómo se calcula</dt><dd>Porcentajes sobre votos a candidaturas, salvo la participación, que es sobre el censo. Cifras reproducibles con los scripts del expediente de la pieza. <a href="../metodologia.html">Metodología de Actualidad</a> · <a href="../../atlas/metodologia/index.html">Metodología del Atlas</a></dd>',
     '<dt>Com es calcula</dt><dd>Percentatges sobre vots a candidatures, excepte la participació, que és sobre el cens. Xifres reproduïbles amb els scripts de l\'expedient de la peça. <a href="../metodologia.html">Metodologia d\'Actualitat</a> · <a href="../../atlas/metodologia/index.html">Metodologia de l\'Atles</a> (en castellà)</dd>'),
    ('<dt>Cómo se calcula</dt>', '<dt>Com es calcula</dt>'), (' Cifras reproducibles con los scripts del expediente de la pieza.', " Xifres reproduïbles amb els scripts de l'expedient de la peça."),
    ('>Metodología de Actualidad</a>', ">Metodologia d'Actualitat</a>"), ('>Metodología del Atlas</a></dd>', ">Metodologia de l'Atles</a> (en castellà)</dd>"),
    ('<p class="etiquetas">Cómo se hacen estas piezas: <a href="../metodologia.html">Metodología de Actualidad</a></p>', '<p class="etiquetas">Com es fan aquestes peces: <a href="../metodologia.html">Metodologia d\'Actualitat</a> (en castellà)</p>'),
    ('<dt>Fuentes</dt>', '<dt>Fonts</dt>'), ('<dt>Autoría</dt>', '<dt>Autoria</dt>'), ('<dt>Revisión de datos y texto</dt>', '<dt>Revisió de dades i text</dt>'),
    ('<dt>Publicado · actualizado</dt>', '<dt>Publicat · actualitzat</dt>'), ('<dt>Correcciones</dt><dd>Ninguna.</dd>', '<dt>Correccions</dt><dd>Cap.</dd>'), ('<dt>Correcciones</dt>', '<dt>Correccions</dt>'),
    ('<span class="kicker">Estás aquí</span>', '<span class="kicker">Ets aquí</span>'), ('<p class="mas-datos">Más datos: ', '<p class="mas-datos">Més dades (en castellà): '),
    ('<h2>Sigue leyendo</h2>', '<h2>Segueix llegint</h2>'),
    ('<h2>Ver datos de este municipio en el mapa</h2>', "<h2>Veure les dades d'aquest municipi al mapa</h2>"),
    ('<h2>Ver datos de estos municipios en el mapa</h2>', "<h2>Veure les dades d'aquests municipis al mapa</h2>"),
    ('<p>El municipio que aparece en esta pieza: resultados por sección censal, voto por renta y las generales desde 1977 en su página, o calle a calle en el mapa.</p>',
     '<p>El municipi que surt en aquesta peça: resultats per secció censal, vot per renda i les generals des del 1977 a la seva pàgina (en castellà), o carrer a carrer al mapa.</p>'),
    ('<p>Los municipios que aparecen en esta pieza: resultados por sección censal, voto por renta y las generales desde 1977 en su página, o calle a calle en el mapa.</p>',
     '<p>Els municipis que surten en aquesta peça: resultats per secció censal, vot per renda i les generals des del 1977 a la seva pàgina (en castellà), o carrer a carrer al mapa.</p>'), ('<span class="kicker">Encuestas</span><b>Encuestas de las elecciones generales del 29N: todas, con sus escaños, actualizadas cada día</b>', '<span class="kicker">Enquestes</span><b>Enquestes de les eleccions generals del 29N: totes, amb els escons, actualitzades cada dia (en castellà)</b>'), ('<b>Todas las piezas de actualidad</b>', "<b>Totes les peces d'actualitat</b>"),
    ('Datos con licencia', 'Dades amb llicència'), ('>Código y datos<', '>Codi i dades<'), ('>Política editorial<', '>Política editorial<'),
]


def en_catala(out, p):
    for es, ca in CA:
        out = out.replace(es, ca)
    out = re.sub(r'<h2>Serie «(.*?)»: (\d+) piezas</h2>', lambda m: f'<h2>Sèrie «{SERIES_CA.get(p["serie"], m.group(1))}»: {m.group(2)} peces</h2>', out)
    for f in {p['fecha'], p.get('actualizado', p['fecha'])}:
        dia, _, hora = f.partition(' ')
        a, m, d = dia.split('-')
        out = out.replace(fecha_larga(f), f'{int(d)} {MESOS_CA[int(m) - 1]} de {a}' + (f', a les {hora.replace(":", ".")}' if hora else ''))
    out = out.replace(' · Actualizado el <time', ' · Actualitzat el <time')
    out = re.sub(r'<b>Ver las (\d+) piezas de la serie</b>', r'<b>Veure les \1 peces de la sèrie</b>', out)
    return out


ENCUESTAS_SIGUE = ('<li><a href="../../encuestas/"><span class="kicker">Encuestas</span>'
                   '<b>Encuestas de las elecciones generales del 29N: todas, con sus escaños, actualizadas cada día</b></a></li>'
                   '<li><a href="../../encuestas/simulador-pactos/"><span class="kicker">Pactos</span>'
                   '<b>Simulador de pactos del 29N: ¿quién puede gobernar? Decide qué vota cada partido</b></a></li>')


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
                  f'<p class="firma">Por <a href="../../sobre-mi.html">{AUTOR}</a> · <time datetime="{p["fecha"]}">{f}</time>'
                  + (f' · Actualizado el <time datetime="{fecha_iso(p["actualizado"])}">{fecha_larga(p["actualizado"])}</time>' if p.get('actualizado', p['fecha']) != p['fecha'] else '')
                  + '</p>', main)
    fo = p.get('foto') or SERIES_FOTO.get(p['serie'])
    principal = fo or GRAFICO_PRINCIPAL.get(p['slug'])   # el gráfico principal ya está en la pieza: solo va en NewsArticle y en el RSS
    if fo:
        # fotos de Commons con autor y licencia; ilustraciones hechas con IA, siempre señaladas (política editorial, #ia)
        # gráficos de datos como imagen principal: nunca IA, con su fuente
        cred = (f'Ilustración generada con IA para Mapa Electoral. <a href="../../atlas/politica-editorial/#ia">Uso de IA</a>' if fo.get('ia')
                else f'Gráfico: Mapa Electoral con datos de {html.escape(fo["fuente"])}' if fo.get('grafico')
                else f'Foto: <a href="{fo["url"]}">{html.escape(fo["credito"])}</a>')
        main = main.replace('</time></p>', f'</time></p>\n<figure class="foto"><img src="../../{fo["src"]}" alt="{html.escape(fo["pie"]) if fo.get("ia") or fo.get("grafico") else ""}" width="{fo["ancho"]}" height="{fo["alto"]}">'
                            f'<figcaption>{html.escape(fo["pie"])} {cred}.</figcaption></figure>', 1)
    for texto, href in ENLACES_TEXTO.get(p['slug'], []):
        assert texto in main, (p['slug'], texto)
        main = main.replace(texto, f'<a href="{href}">{texto}</a>', 1)
    for texto, slug in ENLACES_INTERNOS.get(p['slug'], []):
        assert texto in main and any(q['slug'] == slug for q in todas), (p['slug'], texto)
        main = main.replace(texto, f'<a href="../{slug}/">{texto}</a>', 1)
    # etiquetas dato / patrón / hipótesis / contexto por párrafo, como en el Atlas (estándar de verificación)
    if 'data-tipo="' in main:
        main = re.sub(r'<p data-tipo="(dato|patron|hipotesis|contexto)"([^>]*)>',
                      lambda m: f'<p data-tipo="{m.group(1)}"{m.group(2)}><span class="tipo t-{m.group(1)}">{TIPOS[m.group(1)]}</span>', main)
        nota = ('<p class="etiquetas">Cada párrafo lleva una etiqueta: <b>dato</b> (cifra comprobable con las fuentes), '
                '<b>patrón</b> (relación que se repite, sin afirmar la causa), <b>hipótesis</b> (explicación posible, sin dos fuentes independientes) '
                'o <b>contexto</b> (hechos y declaraciones publicados por otros, enlazados). '
                '<a href="../../atlas/politica-editorial/#verificacion">Cómo verificamos</a></p>')
        ancla = r'(<figure class="foto">.*?</figure>)' if '<figure class="foto">' in main else r'(<p class="firma">.*?</p>)'
        main = re.sub(ancla, lambda m: m.group(1) + '\n' + nota, main, count=1, flags=re.S)
    fuentes = ''.join(f'<li><a href="{u}">{html.escape(t)}</a></li>' for u, t in p['fuentes'])
    # la serie entera, en orden, con la pieza actual marcada; después, las últimas de otras series
    serie = [q for q in todas if q['serie'] == p['serie']]
    # como mucho 20 piezas de la serie alrededor de la actual (Nacho, 25-10-2026: la del 29N pasaba de 80)
    i = serie.index(p); ini = max(0, min(i - 10, len(serie) - 20)); ventana = serie[ini:ini + 20]
    lista = ''.join(f'<li aria-current="page"><span class="kicker">Estás aquí</span><b>{html.escape(q["titulo"])}</b></li>' if q is p else
                    f'<li><a href="../{q["slug"]}/"><b>{html.escape(q["titulo"])}</b></a></li>' for q in ventana)
    if len(serie) > len(ventana):
        lista += f'<li class="todas"><a href="../index.html#{p["serie"]}"><b>Ver las {len(serie)} piezas de la serie</b></a></li>'
    otras = [q for q in todas if q['serie'] != p['serie']][::-1][:3]
    sigue = ''.join(f'<li><a href="../{q["slug"]}/"><span class="kicker">{antetitulo(q)}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in otras)
    if p['serie'] == '29n':   # las piezas del 29N enlazan primero a la página de encuestas, que se actualiza sola
        sigue = ENCUESTAS_SIGUE + sigue
    terr = enlaces_actualidad(p['slug'], '../../')
    municipios = bloque_municipios_pieza(main, p['slug'], '../../')   # «Ver datos de estos municipios en el mapa», con los que nombra la pieza
    mas = ('<p class="mas-datos">Más datos: ' + ' · '.join(f'<a href="{u}">{html.escape(t)}</a>' for u, t in terr) + '.</p>') if terr else ''
    ficha = f"""{municipios}
<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se compara</dt><dd>{p['compara']}</dd>
<dt>Límites</dt><dd>{p['limites']}</dd>
<dt>Cómo se calcula</dt><dd>{p.get('calculo', 'Porcentajes sobre votos a candidaturas, salvo la participación, que es sobre el censo.')} Cifras reproducibles con los scripts del expediente de la pieza. <a href="../metodologia.html">Metodología de Actualidad</a> · <a href="../../atlas/metodologia/index.html">Metodología del Atlas</a></dd>
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
    if '<dl class="ficha">' not in main:   # piezas sin bloque «Método y fuentes»: al menos, el enlace a la metodología general
        main = main.replace('</main>', '<p class="etiquetas">Cómo se hacen estas piezas: <a href="../metodologia.html">Metodología de Actualidad</a></p>\n</main>', 1)

    jsonld = {'@context': 'https://schema.org', '@type': 'AnalysisNewsArticle', '@id': url + '#articulo',
              'headline': p['titulo'], 'alternativeHeadline': re.sub('<[^>]+>', '', h1), 'description': p['descripcion'],
              'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': p['fecha'], 'dateModified': fecha_iso(p.get('actualizado', p['fecha'])),
              'image': ([f"{BASE}/{principal['src']}"] if principal else []) + [imagen],   # la imagen principal (1280x720) primero, para Discover
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
    cab = cabecera(p.get('titulo_seo') or p['titulo'], p['descripcion'], url, imagen, jsonld)
    if p.get('titulo_seo'):   # el título SEO solo va en <title>; en redes, el titular
        cab = cab.replace(f'<meta property="og:title" content="{html.escape(p["titulo_seo"])}">', f'<meta property="og:title" content="{html.escape(p["titulo"])}">', 1)
    out = (cab + estilos + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../../', 'Actualidad') + '\n' + main + '\n' + script + '\n</body>\n</html>\n')
    if p.get('idioma') == 'ca':
        out = en_catala(out, p)
    d = os.path.join(RAIZ, 'actualidad', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(sin_index(out))


def sin_index(html):
    """Enlaces internos a carpetas sin «index.html» (…/actualidad/ y no …/actualidad/index.html), para que Google no indexe dos direcciones por página."""
    return re.sub(r'href="((?:\.\./|[\w-]+/)*)index\.html', lambda m: f'href="{m.group(1) or "./"}', html)


def indice(todas, sitemap=None):
    url = BASE + '/actualidad/'
    desc = 'Piezas cortas que cruzan la actualidad del día con los datos electorales por sección censal. Cada cifra, con su fuente.'
    jsonld = {'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': 'Actualidad', 'url': url, 'description': desc,
              'hasPart': [{'@type': 'AnalysisNewsArticle', 'headline': p['titulo'], 'url': f"{url}{p['slug']}/", 'datePublished': p['fecha']} for p in todas]}
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
            return f'<img class="ilu" src="../{fo["src"]}" alt="{alt_tarjeta(q, fo)}" width="{fo["ancho"]}" height="{fo["alto"]}" loading="lazy">'
        return f'<img class="graf" src="../img/actualidad/{q["slug"]}.jpg" alt="{alt_tarjeta(q, None)}" width="600" height="400" loading="lazy">'
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
           + f'\n<main><p class="kicker">Mapa Electoral</p><h1>Actualidad</h1><p>{desc} Para las piezas de fondo, el <a href="../atlas/index.html">Atlas de las anomalías electorales</a>; para seguir la campaña, <a href="../encuestas/">todas las encuestas de las elecciones generales</a>, actualizadas cada día.</p>'
           + f'{items}<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>'
           + POLITICA + '</footer></main>\n</body>\n</html>\n')
    open(os.path.join(RAIZ, 'actualidad', 'index.html'), 'w', encoding='utf-8').write(sin_index(out))
    urls = [f'  <url><loc>{url}</loc><lastmod>{max(p["fecha"] for p in todas)}</lastmod></url>']
    urls.append(f'  <url><loc>{url}metodologia.html</loc><lastmod>{METODO_ACTUALIZADO}</lastmod></url>')
    urls += [f'  <url><loc>{url}{p["slug"]}/</loc><lastmod>{p.get("actualizado", p["fecha"])[:10]}</lastmod></url>' for p in (sitemap or todas)]
    open(os.path.join(RAIZ, 'actualidad', 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    # Google News: solo piezas de los dos últimos días (norma de Google), como atlas/sitemap-noticias.xml
    lim = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()
    noticias = ''.join(f'  <url>\n    <loc>{url}{p["slug"]}/</loc>\n    <news:news>\n      <news:publication><news:name>Mapa Electoral</news:name><news:language>es</news:language></news:publication>\n'
                       f'      <news:publication_date>{p["fecha"]}</news:publication_date>\n      <news:title>{html.escape(p["titulo"])}</news:title>\n    </news:news>\n  </url>\n'
                       for p in todas if p['fecha'] >= lim)
    open(os.path.join(RAIZ, 'actualidad', 'sitemap-noticias.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">\n' + noticias + '</urlset>\n')
    feed(todas)


def feed(todas, n=40):
    """RSS de Actualidad (Discover lo usa para «Seguir»): las últimas n piezas, con su imagen principal."""
    e = html.escape
    def fecha_rss(iso):
        return datetime.datetime.strptime(iso, '%Y-%m-%d').replace(hour=8, tzinfo=datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    items = []
    for p in sorted(todas, key=lambda q: q['fecha'], reverse=True)[:n]:
        u = f"{BASE}/actualidad/{p['slug']}/"
        fo = p.get('foto') or SERIES_FOTO.get(p['serie']) or GRAFICO_PRINCIPAL.get(p['slug'])
        img = f"{BASE}/{fo['src']}" if fo else f"{BASE}/img/compartir/actualidad-{p['slug']}.jpg"
        items.append(f'<item><title>{e(p["titulo"])}</title><link>{u}</link><guid isPermaLink="true">{u}</guid><pubDate>{fecha_rss(p["fecha"])}</pubDate>'
                     f'<dc:creator>{e(AUTOR)}</dc:creator><description>{e(p["descripcion"])}</description>'
                     f'<media:content url="{img}" medium="image" type="image/jpeg" width="{fo["ancho"] if fo else 1200}" height="{fo["alto"] if fo else 630}"/></item>')
    ult = max(p['fecha'] for p in todas)
    open(os.path.join(RAIZ, 'actualidad', 'feed.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/">\n'
        f'<channel><title>Mapa Electoral · Actualidad</title><link>{BASE}/actualidad/</link>'
        f'<atom:link href="{BASE}/actualidad/feed.xml" rel="self" type="application/rss+xml"/>'
        '<description>Piezas con datos al hilo de la actualidad electoral, por Nacho G. del Álamo.</description><language>es</language>'
        # icono del canal: lo muestran los lectores de RSS y los avisos de Chrome al seguir el sitio
        f'<image><url>{BASE}/favicon-96.png</url><title>Mapa Electoral · Actualidad</title><link>{BASE}/actualidad/</link><width>96</width><height>96</height></image>'
        f'<lastBuildDate>{fecha_rss(ult)}</lastBuildDate>\n' + '\n'.join(items) + '\n</channel></rss>\n')


def alt_tarjeta(q, fo):
    # texto alternativo de las miniaturas: el pie de la ilustración o, si no hay, de qué pieza es el gráfico
    if fo and fo.get('pie'):
        return html.escape(fo['pie'])
    return html.escape(f'Gráfico de la pieza «{q["titulo"]}»')


def imagen_carrusel(q, pre):
    # la ilustración de la pieza (o la de su serie) entera, sin recortar; si no hay, la miniatura del gráfico
    fo = q.get('foto') or SERIES_FOTO.get(q['serie'])
    if fo:
        return f'<img class="ilu" src="{pre}{fo["src"]}" alt="{alt_tarjeta(q, fo)}" loading="lazy" width="300" height="200">'
    return f'<img src="{pre}img/actualidad/{q["slug"]}.jpg" alt="{alt_tarjeta(q, None)}" loading="lazy" width="300" height="200">'


PORTADA_FIJAS = {   # slug: último día (incluido) en que va fija al principio del carrusel de la portada
    'albiol-badalona-pp-29n': '2026-10-28',
    'rufian-montero-la-revuelta-29n': '2026-10-28',
    'feijoo-albiol-barcelona-disturbios-29n': '2026-10-28',
}


def franja_portada(todas, pre=''):
    """Carrusel «Actualidad» de la portada del sitio, entre las marcas <!--actualidad:ultimas-->, encima del del Atlas.
    Mismo formato que la franja del Atlas (atlas/src/paginas.py): miniatura, serie y titular. Las miniaturas las hace miniaturas.mjs."""
    # Las piezas de ciudad «barrio a barrio» no van en el carrusel (Nacho, 15-10-2026)
    # Las más recientes por fecha, no por su sitio en PIEZAS: las piezas se añaden en bloques distintos (Nacho, 22-10-2026)
    recientes = sorted(todas[::-1], key=lambda q: q['fecha'], reverse=True)   # sorted es estable: en el mismo día, la última añadida primero
    # Las de Historia electoral solo van en su propio carrusel, no en el de Actualidad (Nacho, 23-10-2026)
    # Fijas delante, en este orden, hasta el día indicado (Nacho, 28-10-2026: Albiol, Broncano y Feijóo las primeras)
    hoy = datetime.date.today().isoformat()
    fijas = [s for s, hasta in PORTADA_FIJAS.items() if hoy <= hasta]
    recientes = sorted(recientes, key=lambda q: fijas.index(q['slug']) if q['slug'] in fijas else len(fijas))
    ult = [q for q in recientes if not q['slug'].endswith(('-barrio-a-barrio-29n', '-barri-a-barri-29n')) and q['serie'] != 'historia'][:10]
    return (f'<section class="wide del-atlas del-actualidad" aria-labelledby="h-del-actualidad"><div class="da-cab"><h2 id="h-del-actualidad"><a href="{pre}actualidad/">Actualidad</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Piezas anteriores">←</button><button type="button" class="da-next" aria-label="Más piezas">→</button></span></div>'
            '<ul class="carrusel">' +
            ''.join(f'<li><a href="{pre}actualidad/{q["slug"]}/">{imagen_carrusel(q, pre)}'
                    f'<span class="atlas-k">{antetitulo(q)}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in ult) +
            f'<li class="todas"><a href="{pre}actualidad/"><b>Todas las piezas de actualidad →</b><span>{" · ".join(SERIES[k] for k in SERIES if k not in NOMES_ENLLACADES)}</span></a></li></ul>'
            '<style>.del-actualidad .carrusel img{object-fit:contain;background:#fff}.del-actualidad .carrusel img.ilu{background:none}</style>'
            '<script>document.querySelectorAll(".del-actualidad").forEach(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})</script></section>')


FRANJAS = (('historia', 'Historia electoral · desde 1977', 'Todas las elecciones generales desde 1977'),
           ('comunidades', 'Las comunidades en las urnas', 'Un reportaje por comunidad, con su mapa municipal'))


def franja_serie(todas, clave, cabecera, sub, pre=''):
    """Carrusel de una serie en la portada, debajo del de Actualidad: la serie entera, en su orden."""
    serie = [q for q in todas if q['serie'] == clave]
    if clave == 'historia':   # las más nuevas delante: al final del carrusel no se veían (Nacho, 23-10-2026)
        serie = sorted(serie[::-1], key=lambda q: q['fecha'], reverse=True)
    return (f'<section class="wide del-atlas del-actualidad" aria-labelledby="h-del-{clave}"><div class="da-cab"><h2 id="h-del-{clave}"><a href="{pre}actualidad/#{clave}">{cabecera}</a></h2>'
            '<span class="da-nav"><button type="button" class="da-prev" aria-label="Piezas anteriores">←</button><button type="button" class="da-next" aria-label="Más piezas">→</button></span></div>'
            '<ul class="carrusel">' +
            ''.join(f'<li><a href="{pre}actualidad/{q["slug"]}/">{imagen_carrusel(q, pre)}'
                    f'<span class="atlas-k">{q["lugar"]}</span><b>{html.escape(q["titulo"])}</b></a></li>' for q in serie) +
            f'<li class="todas"><a href="{pre}actualidad/#{clave}"><b>Todas las piezas de la serie →</b><span>{sub}</span></a></li></ul>'
            '<script>(s=>{const u=s.querySelector(".carrusel"),m=d=>()=>u.scrollBy({left:d*u.querySelector("li").offsetWidth*1.05,behavior:"smooth"});'
            's.querySelector(".da-prev").onclick=m(-1);s.querySelector(".da-next").onclick=m(1)})(document.currentScript.parentNode)</script></section>')


# Metodología general de las piezas de Actualidad (Nacho, 22-10-2026): fuentes, cruces, controles, límites y verificación.
# Cada pieza la enlaza desde «Método y fuentes». Fecha de la última revisión del texto:
METODO_ACTUALIZADO = '2026-10-23'
METODO_HTML = """<p class="kicker"><a href="index.html">Actualidad</a> · Metodología</p>
<h1>Cómo se hacen las piezas de Actualidad</h1>
<p class="entradilla">Las piezas de esta sección cruzan resultados electorales con datos de renta, edad, empleo, vivienda u opinión, casi siempre por sección censal: las unidades de unos 1.300 vecinos de media en las que el INE divide España para votar.</p>
<p>Esta página explica de dónde salen los datos, cómo se comparan, qué herramientas estadísticas se usan y qué no se puede concluir de ellos. Lo particular de cada pieza está en su bloque «Método y fuentes».</p>
<nav class="indice" aria-label="En esta página"><a href="#fuentes">Fuentes</a> · <a href="#cruces">Cruces</a> · <a href="#controles">Controles</a> · <a href="#regresiones">Regresiones</a> · <a href="#encuestas">Encuestas</a> · <a href="#mapa">El mapa</a> · <a href="#escanos">Escaños</a> · <a href="#ponderacion">Ponderación</a> · <a href="#limites">Límites</a> · <a href="#excepciones">Dónde se rompe el patrón</a> · <a href="#verificacion">Verificación</a></nav>

<h2 id="fuentes">Fuentes</h2>
<p>Todas son públicas y cada pieza enlaza las que usa. Son más de veinte bases de datos, agrupadas aquí por tema.</p>

<h3>Elecciones</h3>
<ul>
<li><b>Ministerio del Interior</b> (<a href="https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/">Infoelectoral</a>). Resultados por mesa de las generales, municipales y europeas, que se suman por sección censal desde 2004 y por municipio desde 1977.</li>
<li><b>Junta Electoral Central</b>, resúmenes oficiales publicados en el BOE, para escaños, senadores y cifras definitivas por provincia.</li>
<li><b>Generalitat de Catalunya</b>, <a href="https://analisi.transparenciacatalunya.cat/d/ntc4-rnwr">datos abiertos</a> de las elecciones al Parlament por sección (2021 y 2024).</li>
<li><b>Segunda República.</b> El <a href="https://doi.org/10.34810/data3274">Atlas electoral de la Segunda República</a> de Toni Rodon, Pau Vall-Prat y Diego Martín Álvarez (Universitat Pompeu Fabra), para las generales de 1933 y 1936 por municipio.</li>
<li><b>INE, Oficina del Censo Electoral.</b> Electores por edad y provincia (2023 y 2026), censo de residentes en el extranjero (CERA) y Padrón de Españoles Residentes en el Extranjero.</li>
</ul>

<h3>Renta e impuestos</h3>
<ul>
<li><b>INE, <a href="https://www.ine.es/experimental/atlas/experimental_atlas.htm">Atlas de Distribución de Renta de los Hogares</a>.</b> Renta por unidad de consumo, fuentes de ingresos (salarios, pensiones, prestaciones, otros), índice de Gini y edad media, por sección. Empieza en 2015: nunca se usa para explicar elecciones anteriores.</li>
<li><b>Agencia Tributaria</b>, <a href="https://sede.agenciatributaria.gob.es/Sede/datosabiertos/catalogo/hacienda/Estadistica_de_los_declarantes_del_IRPF_por_municipios.shtml">estadística de los declarantes del IRPF</a> por municipio y, en las ciudades grandes, por código postal: rentas del trabajo, del capital y de actividades económicas. Los códigos postales se pasan a secciones con la cartografía de CartoCiudad (IGN).</li>
<li><b>Ministerio de Inclusión y Seguridad Social</b>, nómina mensual de pensiones.</li>
</ul>

<h3>Población y empleo</h3>
<ul>
<li><b>INE, <a href="https://www.ine.es/censos2021/C2021_Indicadores.csv">Censo de Población y Viviendas 2021</a></b>, indicadores por sección: estudios, paro, población nacida fuera, régimen de tenencia de la vivienda y viviendas no principales.</li>
<li><b>INE, Censo anual de población</b> (2021 a 2025): ocupados por grupo de ocupación, por situación profesional (asalariados, autónomos, empresarios) y por rama de actividad; población por país de nacimiento.</li>
<li><b>INE, Estadística Continua de Población, Encuesta de Población Activa y Encuesta de Condiciones de Vida</b>, para el contexto por provincia o comunidad.</li>
<li><b>Afiliación a la Seguridad Social por municipio</b>, donde las comunidades la publican, y el boletín estadístico del personal de las administraciones públicas, por provincia. No hay datos abiertos de funcionarios por municipio.</li>
</ul>

<h3>Vivienda</h3>
<ul>
<li><b>INE, Censo 2021</b>: viviendas principales y no principales (tabla 59525) y viviendas según su consumo eléctrico (tabla 59531), que es como el INE estima las vacías.</li>
<li><b>INE, viviendas turísticas</b> por sección (estadística experimental).</li>
<li><b>Ministerio de Vivienda, <a href="https://www.mivau.gob.es/vivienda/alquila-bien-es-tu-derecho/serpavi">SERPAVI</a></b>: precio de los alquileres declarados a Hacienda, de 2011 a 2024.</li>
<li><b>Dirección General del Catastro</b>, edificios en formato <a href="https://www.catastro.hacienda.gob.es/webinspire/index.html">INSPIRE</a>: año de construcción y viviendas por edificio.</li>
<li><b>Consejo General del Poder Judicial</b>, lanzamientos (desahucios) por territorio.</li>
</ul>

<h3>Opinión</h3>
<ul>
<li><b>CIS, microdatos</b> de los barómetros mensuales y de las encuestas preelectorales y postelectorales. Se usan las respuestas individuales, no solo las tablas publicadas.</li>
<li><b>Centre d'Estudis d'Opinió</b> de la Generalitat, para Cataluña.</li>
<li><b>Encuestas publicadas</b> por los medios, recopiladas en la sección de <a href="../encuestas/">encuestas</a>.</li>
</ul>

<h3>Mapas y nombres</h3>
<ul>
<li><b>INE</b>, contornos de las secciones censales y callejero del censo electoral.</li>
<li><b>IGN, CartoCiudad</b>, y <b>OpenStreetMap</b>, para poner nombre de calle y de barrio a cada sección.</li>
<li><b>Ayuntamientos</b> (Madrid, Málaga, Zaragoza, Sevilla, Palma, Girona…), para sus distritos y barrios oficiales.</li>
</ul>

<figure class="met"><figcaption><b>Qué años cubre cada fuente</b><br><span>Los puntos son años sueltos; las barras, series continuas</span></figcaption>
<svg viewBox="0 0 440 234" role="img" aria-labelledby="tl-t" style="width:100%;max-width:560px;display:block"><title id="tl-t">Años que cubre cada fuente</title><line x1="178.7" x2="178.7" y1="6" y2="206" stroke="var(--rule)"/><text x="178.7" y="222" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">1940</text><line x1="236.0" x2="236.0" y1="6" y2="206" stroke="var(--rule)"/><text x="236.0" y="222" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">1960</text><line x1="293.3" x2="293.3" y1="6" y2="206" stroke="var(--rule)"/><text x="293.3" y="222" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">1980</text><line x1="350.6" x2="350.6" y1="6" y2="206" stroke="var(--rule)"/><text x="350.6" y="222" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">2000</text><line x1="407.9" x2="407.9" y1="6" y2="206" stroke="var(--rule)"/><text x="407.9" y="222" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">2020</text><text x="0" y="23" font-size="13" font-family="var(--ui)" fill="var(--fg)">Generales, por municipio</text><circle cx="284.7" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="290.4" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="299.0" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="310.5" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="319.1" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="330.6" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="339.2" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="350.6" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="362.1" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="373.5" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="382.1" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="393.6" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="396.5" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="405.1" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="407.5" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="416.5" cy="18" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><text x="0" y="47" font-size="13" font-family="var(--ui)" fill="var(--fg)">Generales, por sección</text><circle cx="362.1" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="373.5" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="382.1" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="393.6" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="396.5" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="405.1" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="407.5" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="416.5" cy="42" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><text x="0" y="71" font-size="13" font-family="var(--ui)" fill="var(--fg)">Segunda República</text><circle cx="158.6" cy="66" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="167.2" cy="66" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><text x="0" y="95" font-size="13" font-family="var(--ui)" fill="var(--fg)">Renta (INE)</text><rect x="393.6" y="85" width="22.9" height="10" rx="3" fill="var(--fg)" opacity=".75"/><text x="0" y="119" font-size="13" font-family="var(--ui)" fill="var(--fg)">Censo 2021 y Censo anual</text><rect x="410.8" y="109" width="11.5" height="10" rx="3" fill="var(--fg)" opacity=".75"/><circle cx="410.8" cy="114" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><text x="0" y="143" font-size="13" font-family="var(--ui)" fill="var(--fg)">IRPF (Agencia Tributaria)</text><circle cx="416.5" cy="138" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><text x="0" y="167" font-size="13" font-family="var(--ui)" fill="var(--fg)">Alquiler (SERPAVI)</text><rect x="382.1" y="157" width="37.3" height="10" rx="3" fill="var(--fg)" opacity=".75"/><text x="0" y="191" font-size="13" font-family="var(--ui)" fill="var(--fg)">Encuestas del CIS</text><rect x="424.8" y="181" width="4.0" height="10" rx="3" fill="var(--fg)" opacity=".75"/><circle cx="393.6" cy="186" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="396.5" cy="186" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="405.1" cy="186" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/><circle cx="416.5" cy="186" r="3.2" fill="var(--fg)" stroke="var(--bg)" stroke-width="1"/></svg>
<p class="src">Por eso las piezas comparan casi siempre con las generales de 2023: es la elección más cercana a los datos de renta, censo e impuestos.</p></figure>

<h2 id="cruces">Cómo se cruzan los datos</h2>
<p>La mayoría de las piezas comparan dos cifras. Estas son las herramientas, de la más sencilla a la más compleja.</p>

<h3>De la mesa a la sección</h3>
<p>Interior publica los votos de cada mesa. Cada mesa pertenece a una sección censal, así que se suman los votos y el censo de todas las mesas de cada sección.</p>
<p>Las secciones cambian de límites de una elección a otra. Para comparar elecciones se usan las secciones con el mismo código, y antes de 2004 solo se compara por municipio, porque las secciones de entonces no se corresponden con las actuales.</p>

<h3>Grupos de igual tamaño</h3>
<p>Se ordenan las secciones por una variable, por ejemplo la renta, y se parten en cinco grupos (quintiles) o diez (deciles) con el mismo número de secciones o de votantes. Después se compara el voto de cada grupo.</p>
<p>Es la forma más habitual en los gráficos porque se entiende sin fórmulas: «en el 10% de barrios más ricos, el PP saca tanto; en el 10% más pobre, tanto».</p>

<h3>Comparación de medias</h3>
<p>El voto o la participación de un grupo frente a otro: las secciones con más alquiler frente a las de menos, la quinta parte con más pensionistas frente al resto.</p>

<h3>Correlación</h3>
<p>Cuando se da un coeficiente, es el de Pearson entre secciones o municipios. Va de −1 a 1 y mide si dos cifras suben y bajan juntas, no cuánto cambia una con la otra.</p>
<p>Una correlación de 0,3 entre secciones ya es notable; una de 0,8 es rara y suele esconder una variable común, como la renta o el tamaño del municipio.</p>

<h3>Curvas a lo largo del tiempo</h3>
<p>Para ver cómo cambia un patrón, se repite la misma cuenta por deciles en cada elección, con los mismos grupos de secciones, y se dibuja una curva por año. Así se ve, por ejemplo, cómo se ha movido la frontera de renta entre Junts y el PP.</p>

<h2 id="controles">Controles</h2>
<p>Una relación entre dos cifras puede deberse a una tercera. Antes de publicar un patrón, se comprueba que aguanta al menos alguno de estos controles, y la pieza dice cuál.</p>
<ul>
<li><b>A igual renta.</b> La comparación se repite dentro de cada tramo de renta o entre secciones de renta parecida. Es el control más frecuente, porque la renta va unida a casi todo: edad, estudios, vivienda, empleo.</li>
<li><b>A igual tamaño de municipio.</b> Las capitales, los pueblos pequeños y las ciudades medianas votan distinto. Cuando la variable cambia con el tamaño, se compara dentro de cada tramo de población.</li>
<li><b>Dentro de cada provincia.</b> Una tendencia del conjunto puede desaparecer o invertirse dentro de cada territorio: es la paradoja de Simpson. Por eso se repite la cuenta en cada provincia y se dice en cuántas se cumple: «en 50 de las 51 provincias».</li>
<li><b>Sin el caso que más pesa.</b> Si una provincia o una ciudad aporta buena parte del efecto, se repite sin ella («sin Almería»).</li>
</ul>

<h2 id="regresiones">Regresiones</h2>
<p>Cuando hay que descontar varias cosas a la vez (renta, paro, estudios, edad, población nacida fuera, tamaño), se usa una regresión.</p>

<h3>Mínimos cuadrados ponderados</h3>
<p>Es una regresión lineal (MCO) en la que cada sección pesa según sus votantes o su censo. El resultado se da en puntos de voto: «por cada 10 puntos más de mayores de 65, el PP sube 2 puntos».</p>
<p>El texto lo cuenta como «a igualdad de lo demás», nunca como causa.</p>

<h3>Efectos fijos</h3>
<p>Una regresión con secciones de toda España supondría que las reglas son las mismas en Sevilla, en Ourense y en Barcelona. No lo son: cada provincia tiene su historia, sus partidos y su oferta electoral.</p>
<p>Los efectos fijos de provincia resuelven eso. El modelo solo compara secciones de la misma provincia, nunca una de Sevilla con una de Ourense. Los de municipio van más allá: solo comparan barrios de la misma ciudad, y se usan en los municipios con al menos 20 secciones.</p>
<p>El gráfico muestra la misma pregunta con tres modelos: cuánto cambia el voto de 2023 por cada 1.000 euros más de renta por unidad de consumo.</p>

<figure class="met"><figcaption><b>Lo que cambia al comparar dentro de cada provincia</b><br><span>Puntos de voto en 2023 por cada 1.000 euros más de renta por unidad de consumo, con su intervalo del 95%. Pasa el dedo o el ratón por cada punto</span></figcaption>
<svg viewBox="0 0 440 362" role="img" aria-labelledby="fe-t" style="width:100%;max-width:560px;display:block"><title id="fe-t">Cambio en el voto de 2023 por cada 1.000 euros más de renta por unidad de consumo, según el modelo</title><line x1="97.2" x2="97.2" y1="36" y2="334" stroke="var(--rule)" /><text x="97.2" y="350" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">-1,00</text><line x1="165.3" x2="165.3" y1="36" y2="334" stroke="var(--rule)" /><text x="165.3" y="350" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">-0,50</text><line x1="233.4" x2="233.4" y1="36" y2="334" stroke="var(--rule)" stroke-width="1.5"/><text x="233.4" y="350" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">0</text><line x1="301.5" x2="301.5" y1="36" y2="334" stroke="var(--rule)" /><text x="301.5" y="350" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">+0,50</text><line x1="369.5" x2="369.5" y1="36" y2="334" stroke="var(--rule)" /><text x="369.5" y="350" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">+1,00</text><circle cx="75.0" cy="18" r="4.5" fill="var(--bg)" stroke="var(--fg)" stroke-width="2"/><text x="84" y="22" font-size="13" font-family="var(--ui)" fill="var(--fg)">Sin efectos fijos</text><circle cx="221.2" cy="18" r="5" fill="var(--fg)" stroke="var(--bg)" stroke-width="1.5"/><text x="230.2" y="22" font-size="13" font-family="var(--ui)" fill="var(--fg)">Provincia</text><rect x="310.1" y="13.5" width="9" height="9" fill="var(--fg)" stroke="var(--bg)" stroke-width="1.5"/><text x="323.6" y="22" font-size="13" font-family="var(--ui)" fill="var(--fg)">Municipio</text><text x="0" y="77.5" font-size="14" font-weight="600" font-family="var(--ui)" fill="var(--fg)">PP</text><g><title>PP, sin efectos fijos: +0,47 puntos por cada 1.000 euros (intervalo del 95%: de +0,13 a +0,80; 34.939 secciones)</title><line x1="251.1" x2="342.3" y1="53.5" y2="53.5" stroke="#1d84ce" stroke-width="2"/><circle cx="297.4" cy="53.5" r="4.5" fill="var(--bg)" stroke="#1d84ce" stroke-width="2"/><rect x="70" y="44.0" width="354" height="19" fill="transparent"/></g><g><title>PP, efectos fijos de provincia: +0,93 puntos por cada 1.000 euros (intervalo del 95%: de +0,84 a +1,01; 34.939 secciones)</title><line x1="347.8" x2="370.9" y1="72.5" y2="72.5" stroke="#1d84ce" stroke-width="2"/><circle cx="360.0" cy="72.5" r="5" fill="#1d84ce" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="63.0" width="354" height="19" fill="transparent"/></g><g><title>PP, efectos fijos de municipio: +1,04 puntos por cada 1.000 euros (intervalo del 95%: de +0,93 a +1,16; 20.265 secciones)</title><line x1="360.0" x2="391.3" y1="91.5" y2="91.5" stroke="#1d84ce" stroke-width="2"/><rect x="370.5" y="87.0" width="9" height="9" fill="#1d84ce" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="82.0" width="354" height="19" fill="transparent"/></g><text x="0" y="148.5" font-size="14" font-weight="600" font-family="var(--ui)" fill="var(--fg)">PSOE</text><g><title>PSOE, sin efectos fijos: -0,76 puntos por cada 1.000 euros (intervalo del 95%: de -0,85 a -0,68; 34.939 secciones)</title><line x1="117.7" x2="140.8" y1="124.5" y2="124.5" stroke="#e30613" stroke-width="2"/><circle cx="129.9" cy="124.5" r="4.5" fill="var(--bg)" stroke="#e30613" stroke-width="2"/><rect x="70" y="115.0" width="354" height="19" fill="transparent"/></g><g><title>PSOE, efectos fijos de provincia: -0,86 puntos por cada 1.000 euros (intervalo del 95%: de -0,96 a -0,76; 34.939 secciones)</title><line x1="102.7" x2="129.9" y1="143.5" y2="143.5" stroke="#e30613" stroke-width="2"/><circle cx="116.3" cy="143.5" r="5" fill="#e30613" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="134.0" width="354" height="19" fill="transparent"/></g><g><title>PSOE, efectos fijos de municipio: -0,89 puntos por cada 1.000 euros (intervalo del 95%: de -1,03 a -0,75; 20.265 secciones)</title><line x1="93.1" x2="131.3" y1="162.5" y2="162.5" stroke="#e30613" stroke-width="2"/><rect x="107.7" y="158.0" width="9" height="9" fill="#e30613" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="153.0" width="354" height="19" fill="transparent"/></g><text x="0" y="219.5" font-size="14" font-weight="600" font-family="var(--ui)" fill="var(--fg)">Vox</text><g><title>Vox, sin efectos fijos: -0,11 puntos por cada 1.000 euros (intervalo del 95%: de -0,23 a +0,02; 34.939 secciones)</title><line x1="202.1" x2="236.1" y1="195.5" y2="195.5" stroke="#63be21" stroke-width="2"/><circle cx="218.4" cy="195.5" r="4.5" fill="var(--bg)" stroke="#63be21" stroke-width="2"/><rect x="70" y="186.0" width="354" height="19" fill="transparent"/></g><g><title>Vox, efectos fijos de provincia: +0,02 puntos por cada 1.000 euros (intervalo del 95%: de -0,04 a +0,08; 34.939 secciones)</title><line x1="227.9" x2="244.3" y1="214.5" y2="214.5" stroke="#63be21" stroke-width="2"/><circle cx="236.1" cy="214.5" r="5" fill="#63be21" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="205.0" width="354" height="19" fill="transparent"/></g><g><title>Vox, efectos fijos de municipio: +0,07 puntos por cada 1.000 euros (intervalo del 95%: de -0,01 a +0,14; 20.265 secciones)</title><line x1="232.0" x2="252.4" y1="233.5" y2="233.5" stroke="#63be21" stroke-width="2"/><rect x="238.4" y="229.0" width="9" height="9" fill="#63be21" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="224.0" width="354" height="19" fill="transparent"/></g><text x="0" y="290.5" font-size="14" font-weight="600" font-family="var(--ui)" fill="var(--fg)">Sumar</text><g><title>Sumar, sin efectos fijos: -0,02 puntos por cada 1.000 euros (intervalo del 95%: de -0,08 a +0,03; 34.939 secciones)</title><line x1="222.5" x2="237.5" y1="266.5" y2="266.5" stroke="#a9205b" stroke-width="2"/><circle cx="230.7" cy="266.5" r="4.5" fill="var(--bg)" stroke="#a9205b" stroke-width="2"/><rect x="70" y="257.0" width="354" height="19" fill="transparent"/></g><g><title>Sumar, efectos fijos de provincia: -0,18 puntos por cada 1.000 euros (intervalo del 95%: de -0,28 a -0,09; 34.939 secciones)</title><line x1="195.3" x2="221.1" y1="285.5" y2="285.5" stroke="#a9205b" stroke-width="2"/><circle cx="208.9" cy="285.5" r="5" fill="#a9205b" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="276.0" width="354" height="19" fill="transparent"/></g><g><title>Sumar, efectos fijos de municipio: -0,27 puntos por cada 1.000 euros (intervalo del 95%: de -0,36 a -0,19; 20.265 secciones)</title><line x1="184.4" x2="207.5" y1="304.5" y2="304.5" stroke="#a9205b" stroke-width="2"/><rect x="192.1" y="300.0" width="9" height="9" fill="#a9205b" stroke="var(--bg)" stroke-width="1.5"/><rect x="70" y="295.0" width="354" height="19" fill="transparent"/></g><text x="424" y="350" text-anchor="end" font-size="0"></text></svg>
<p class="src">Fuente: Ministerio del Interior, generales de julio de 2023, e INE, Atlas de Distribución de Renta de los Hogares. 34.939 secciones; el modelo de municipio usa las 20.265 de los municipios con 20 secciones o más. Ponderado por votantes, errores agrupados por municipio. Cálculo propio.</p></figure>

<p>Sin efectos fijos, el PP sube medio punto por cada 1.000 euros. Dentro de cada provincia, casi un punto, y dentro de cada ciudad, algo más. Mezclar provincias escondía la mitad de la relación. Una explicación probable: hay provincias ricas donde el PP saca poco, como las vascas y las catalanas.</p>
<p>Con Sumar pasa algo parecido: en el conjunto de España no hay relación con la renta, pero dentro de cada ciudad los barrios más ricos le votan menos.</p>

<h3>Errores agrupados</h3>
<p>Las secciones vecinas no son independientes: comparten renta, tipo de barrio y costumbres de voto. Si el modelo las trata como si lo fueran, cree tener más información de la que tiene y da márgenes de error demasiado estrechos.</p>
<p>Por eso los errores se agrupan por municipio (por provincia cuando la unidad es el municipio). Un efecto que no se distingue de cero con esos errores no se publica como patrón.</p>

<figure class="met"><figcaption><b>El mismo efecto, dos márgenes de error</b><br><span>Puntos de voto a Vox en 2023 por cada 1.000 euros más de renta, con efectos fijos de provincia: intervalo del 95%</span></figcaption>
<svg viewBox="0 0 440 120" role="img" aria-labelledby="cl-t" style="width:100%;max-width:560px;display:block"><title id="cl-t">Intervalo del 95% del efecto de la renta en el voto a Vox, con errores sin agrupar y agrupados por municipio</title><line x1="167.1" x2="167.1" y1="8" y2="90" stroke="var(--rule)" /><text x="167.1" y="108" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">-0,05</text><line x1="252.8" x2="252.8" y1="8" y2="90" stroke="var(--rule)" stroke-width="1.5"/><text x="252.8" y="108" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">0</text><line x1="338.4" x2="338.4" y1="8" y2="90" stroke="var(--rule)" /><text x="338.4" y="108" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">+0,05</text><line x1="424.0" x2="424.0" y1="8" y2="90" stroke="var(--rule)" /><text x="424.0" y="108" text-anchor="middle" font-size="13" font-family="var(--ui)" fill="var(--muted)">+0,10</text><g><title>Sin agrupar: de +0,01 a +0,02 puntos</title><text x="0" y="33" font-size="13" font-family="var(--ui)" fill="var(--fg)">Sin agrupar</text><line x1="274.5" x2="295.4" y1="28" y2="28" stroke="#63be21" stroke-width="3" stroke-linecap="round"/><circle cx="284.9" cy="28" r="5" fill="#63be21" stroke="var(--bg)" stroke-width="1.5"/></g><g><title>Agrupados por municipio: de -0,04 a +0,08 puntos</title><text x="0" y="67" font-size="13" font-family="var(--ui)" fill="var(--fg)">Agrupados por municipio</text><line x1="180.1" x2="389.8" y1="62" y2="62" stroke="#63be21" stroke-width="3" stroke-linecap="round"/><circle cx="284.9" cy="62" r="5" fill="#63be21" stroke="var(--bg)" stroke-width="1.5"/></g></svg>
<p class="src">Fuente: Interior e INE. 34.939 secciones. Cálculo propio.</p></figure>

<p>Sin agrupar, parece que Vox sube un poco con la renta y que el resultado es firme. Agrupando por municipio, el margen se multiplica por siete y cruza el cero: no se puede decir que la renta mueva el voto a Vox dentro de cada provincia.</p>
<p>Las piezas anteriores a octubre de 2026 no daban márgenes de error; sus cifras de regresión se revisarán con este criterio si se actualizan.</p>

<h3>Intervalos de confianza</h3>
<p>Cuando un gráfico muestra una línea a cada lado de un punto, es el intervalo del 95%: el rango de valores compatibles con los datos. Si cruza el cero, el efecto no se distingue de la nada.</p>

<h2 id="encuestas">Encuestas</h2>
<p>Los datos por sección no dicen cómo vota cada persona. Para eso están las encuestas, sobre todo los microdatos del CIS.</p>
<ul>
<li><b>Pesos.</b> Siempre se usan los pesos que publica el propio CIS, que corrigen la muestra para que se parezca a la población.</li>
<li><b>Voto más simpatía.</b> Es la suma de quien dice que votaría a un partido y de quien, sin decidir, se siente más cercano a él. No es la estimación de voto del CIS, que aplica un modelo propio que no se reproduce aquí.</li>
<li><b>Varios barómetros juntos.</b> Para tener muestras grandes de grupos pequeños (los jóvenes de una comunidad, por ejemplo), se suman varios barómetros seguidos y se dice cuáles.</li>
<li><b>Margen de error.</b> Cada porcentaje lleva su intervalo del 95%. Con 1.000 entrevistas ronda los 3 puntos; con 100, los 10.</li>
<li><b>Submuestras pequeñas.</b> Cuando un grupo tiene muy pocas entrevistas (en general, menos de 100), no se pinta en el mapa ni se comenta como dato.</li>
<li><b>Recuerdo de voto.</b> Cuando se compara con el voto anterior, se tiene en cuenta que el recuerdo no coincide con el resultado real: en los barómetros del CIS, más gente dice haber votado al PSOE en 2023 de la que lo votó.</li>
</ul>

<h2 id="mapa">El mapa también cuenta</h2>
<p>Los barrios parecidos suelen estar juntos, y eso tiene sus propias herramientas.</p>
<ul>
<li><b>Índice de Moran.</b> Mide si los valores altos están cerca de otros altos y los bajos de otros bajos. Va de −1 a 1. Se usa para comprobar si lo que el modelo no explica sigue agrupado en el mapa: si es así, falta algo en el modelo.</li>
<li><b>Modelos espaciales.</b> Cuando los residuos siguen agrupados, se repite la regresión con un modelo que tiene en cuenta a los vecinos (de retardo o de error espacial) antes de publicar.</li>
<li><b>Focos locales (LISA).</b> Señalan en el mapa los grupos de barrios que votan muy parecido entre sí y muy distinto del resto de la ciudad.</li>
<li><b>Índice de disimilitud de Duncan.</b> Mide qué parte del voto de un partido tendría que cambiar de barrio para repartirse igual por toda la ciudad. Va de 0 (repartido por igual) a 100 (concentrado del todo).</li>
</ul>

<h2 id="escanos">Escaños</h2>
<ul>
<li><b>Ley D'Hondt.</b> Las simulaciones de escaños aplican la regla de la ley electoral en cada provincia, con la barrera del 3% de los votos válidos.</li>
<li><b>El último escaño.</b> Se calcula cuántos votos le faltaron al segundo partido para quitarle el último diputado al primero. Es lo que permite decir que un escaño se decidió por unos cientos de votos.</li>
<li><b>Coaliciones hipotéticas.</b> Cuando se suman los votos de dos partidos para ver qué habría sacado una lista conjunta, se dice siempre que es un ejercicio: los votantes de una lista conjunta no son la suma exacta de los de sus partidos por separado.</li>
</ul>

<h2 id="ponderacion">Cuánto pesa cada sección</h2>
<ul>
<li><b>Porcentajes de un grupo</b> (el voto del quintil más pobre, la participación de un distrito): se suman los votos y el censo de todas sus secciones. Equivale a una media ponderada por votantes o por censo.</li>
<li><b>Grupos.</b> Pueden tener el mismo número de secciones o de votantes; la nota del gráfico dice cuál.</li>
<li><b>Correlaciones y recuentos</b> («en 1.089 de las 3.289 secciones más pobres»): cada sección cuenta lo mismo, salvo que se diga lo contrario. Algunas piezas dejan fuera las secciones muy pequeñas, y lo dicen.</li>
<li><b>Regresiones:</b> ponderadas por votantes o por censo, para que un pueblo de 200 habitantes no pese lo mismo que un barrio de 3.000.</li>
</ul>

<h2 id="limites">Lo que estos datos no dicen</h2>
<ul>
<li><b>No dicen quién vota a quién.</b> Son datos de secciones y municipios, no de personas. Que las secciones con más pensionistas voten más al PP no significa que los pensionistas voten al PP: pueden ser sus vecinos. Es la falacia ecológica, descrita por William S. Robinson en 1950 («<a href="https://doi.org/10.2307/2087176">Ecological Correlations and the Behavior of Individuals</a>», <i>American Sociological Review</i>).</li>
<li><b>No dicen por qué.</b> «Donde más X, más Y» no es «X causa Y». Los controles descartan algunas explicaciones, no todas. Una explicación solo se da como tal con dos fuentes independientes; si no, se marca como hipótesis.</li>
<li><b>Las fronteras importan.</b> El resultado de un cruce puede cambiar según se agrupe por sección, por distrito o por municipio.</li>
<li><b>Las fechas no siempre coinciden.</b> Las elecciones son de 2023, el censo de 2021, la renta de 2023. Cada pieza dice qué año usa cada dato.</li>
<li><b>Los extranjeros no votan en las generales.</b> En las secciones con mucha población extranjera, el voto es el de sus vecinos con nacionalidad española.</li>
<li><b>Los pueblos pequeños tienen una sola sección.</b> En 881 municipios de más de 1.000 habitantes no hay barrios que comparar, y sus fichas lo dicen.</li>
</ul>

<h2 id="excepciones">Dónde se rompe el patrón</h2>
<p>Comparar dentro de cada provincia sirve también para encontrar los lugares donde la regla general no se cumple, que a menudo son la noticia.</p>
<ul>
<li>En el conjunto de España, las secciones pobres votan más a PSOE y Sumar. En la provincia de Murcia, 172 de sus 191 secciones del tramo más pobre votaron más a PP y Vox; en Almería, 117 de 141. En Sevilla, ninguna. <a href="barrios-pobres-derecha-ricos-izquierda/">La pieza</a>.</li>
<li>Al revés, la mayoría de las secciones ricas que votan más a PSOE y Sumar que a PP y Vox están en Cataluña y el País Vasco, donde buena parte del voto conservador va a Junts o al PNV.</li>
<li>En Madrid, el oficio del barrio parece decir menos del voto que en provincias donde se vive y se trabaja en el mismo sitio. Es una hipótesis. <a href="oficios-y-voto-municipios-29n/">La pieza</a>.</li>
</ul>

<h2 id="verificacion">Verificación</h2>
<ul>
<li>Cada párrafo lleva una etiqueta: <b>dato</b> (cifra comprobable con las fuentes), <b>patrón</b> (relación que se repite, sin afirmar la causa), <b>hipótesis</b> (explicación posible, sin dos fuentes independientes) o <b>contexto</b> (hechos y declaraciones publicados por otros, enlazados).</li>
<li>Cada pieza tiene un expediente interno con los scripts que reproducen sus cifras y una tabla que liga cada frase con su número y su fuente. Si una cifra no cuadra, la pieza no sale.</li>
<li>Ninguna conclusión se publica de forma automática: cada pieza la revisa una persona antes de publicarse.</li>
<li>Los errores se corrigen en la propia pieza, con fecha, y en el <a href="../atlas/correcciones/">registro de correcciones</a>.</li>
</ul>
<p>Más detalle en la <a href="../atlas/politica-editorial/#verificacion">política editorial</a> y en la <a href="../atlas/metodologia/">metodología del Atlas</a>. El código y los datos derivados están en <a href="https://github.com/nachotronic/abstencio-catalunya">GitHub</a>.</p>
"""


def metodologia():
    url = BASE + '/actualidad/metodologia.html'
    titulo = 'Metodología de Actualidad: fuentes, cruces, regresiones, encuestas y límites'
    desc = ('Cómo se hacen las piezas de Actualidad de Mapa Electoral: más de veinte fuentes (Interior, INE, Agencia Tributaria, Catastro, SERPAVI, CIS), '
            'comparaciones por grupos, controles, regresiones con efectos fijos y errores agrupados, encuestas, análisis espacial y límites de los datos agregados.')
    jsonld = {'@context': 'https://schema.org', '@type': 'WebPage', '@id': url, 'name': titulo, 'url': url, 'description': desc,
              'inLanguage': 'es', 'dateModified': METODO_ACTUALIZADO, 'publisher': MEDIO,
              'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'},
              'isPartOf': {'@type': 'CollectionPage', 'name': 'Actualidad', 'url': BASE + '/actualidad/'}}
    css = """<style>
:root{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.6}
main{max-width:46rem;margin:0 auto;padding-block:2rem 4rem;padding-inline:16px}
h1{font-size:clamp(1.8rem,5vw,2.4rem);line-height:1.15;margin:.6rem 0}
h2{font-size:1.3rem;margin:2.2rem 0 .6rem;scroll-margin-top:1rem}
h3{font-family:var(--ui);font-size:1.05rem;margin:1.6rem 0 .4rem}
a{color:var(--fg)}
.entradilla{font-size:1.1rem}
nav.indice{font-family:var(--ui);font-size:.9rem;color:var(--muted);border-block:1px solid var(--rule);padding:.6rem 0}
nav.indice a{color:var(--muted)}
main li{margin-bottom:.5rem}
figure.met{margin:1.6rem 0;padding:1rem 0;border-block:1px solid var(--rule)}
figure.met figcaption{font-family:var(--ui);font-size:1rem;line-height:1.35;margin-bottom:.7rem}
figure.met figcaption span{color:var(--muted);font-size:.92rem}
figure.met .src{font-family:var(--ui);font-size:.85rem;color:var(--muted);margin:.6rem 0 0}
figure.met svg g:hover line,figure.met svg g:hover circle,figure.met svg g:hover rect{opacity:.7}
</style>"""
    out = (cabecera(titulo, desc, url, BASE + '/img/compartir/atlas.jpg', jsonld) + css + CSS_SITIO + '\n</head>\n<body>\n'
           + nav('../', 'Actualidad') + '\n<main>' + METODO_HTML
           + f'<p class="firma">{AUTOR} · Actualizada el <time datetime="{METODO_ACTUALIZADO}">{fecha_larga(METODO_ACTUALIZADO)}</time></p>'
           + '<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a>'
           + POLITICA + '</footer></main>\n</body>\n</html>\n')
    open(os.path.join(RAIZ, 'actualidad', 'metodologia.html'), 'w', encoding='utf-8').write(sin_index(out))


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


# Series que només s'enllacen des de la seva peça (Girona, en català): fora de l'índex d'Actualidad, el carrusel,
# «Sigue leyendo» i les fitxes de territori (Nacho, 15-10-2026). Les pàgines es fan igual i van al sitemap.
NOMES_ENLLACADES = {'girona'}
PUBLICAS = [p for p in PIEZAS if p['serie'] not in NOMES_ENLLACADES]

if __name__ == '__main__':
    # Una fecha futura deja la pieza fija arriba del carrusel durante días (Nacho, 22-10-2026): la fecha es la de publicación
    futuras = [p['slug'] for p in PIEZAS if p['fecha'] > datetime.date.today().isoformat()]
    if futuras:
        sys.exit('Piezas con fecha futura (pon la fecha real de publicación): ' + ', '.join(futuras))
    for p in PIEZAS:
        pieza(p, PIEZAS if p['serie'] in NOMES_ENLLACADES else PUBLICAS)
    indice(PUBLICAS, PIEZAS)
    metodologia()
    portada(PUBLICAS)
    import esquema   # autor común, Dataset y migas de pan en todas las páginas (src/esquema.py)
    esquema.main()
    import ilustraciones   # ILUSTRACIONES.md: piezas que aún esperan su ilustración
    print('Actualidad:', len(PIEZAS), 'piezas;', ilustraciones.escribir(PIEZAS, SERIES_FOTO, RAIZ, BASE), 'sin ilustración')
