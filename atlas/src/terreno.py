"""Fotos y notas de color («Sobre el terreno») de cada pieza del Atlas (2026-10-07).

Fotos: Wikimedia Commons, gente en escenas de calle, sin playas y sin repetir. Se guardan en atlas/img/<slug>.jpg
(1.200 px de ancho como máximo); el crédito y la licencia se copian de la página del archivo en Commons.
Notas de color: datos descriptivos del lugar, no explicaciones del voto. Cada una lleva dos fuentes independientes
(nunca Wikipedia), abiertas y comprobadas; el fragmento literal que apoya cada nota está en el expediente.
Las piezas sin foto no tienen en Commons una escena de calle con gente del lugar.
"""

C = 'https://commons.wikimedia.org/wiki/File:'

FOTOS = {
    'cadiz-madrid-29n': ('Paseantes y terrazas en una calle peatonal del centro de Cádiz al anochecer, en 2025', 'Jorge Franganillo', 'CC BY 4.0', 'Cádiz_(Spain).jpg'),
    'madrid-voto-exterior': ('Gente en la Puerta del Sol de Madrid, en 2007', 'Dario Alvarez', 'CC BY 2.0', 'Puerta_del_Sol_CONVAR12_(1243488902).jpg'),
    'escanos-ajustados-2023': ('La Rambla de la Llibertat, en Girona, en 2025', 'Aktron', 'CC BY-SA 4.0', 'Girona_Rambla_de_la_Llibertat.jpg'),
    'capitales-frente-a-su-provincia': ('La calle Elvira de Granada, al anochecer, en 2012', 'Curimedia', 'CC BY 2.0', 'Elvira_Street_(8169708505).jpg'),
    'sur-de-madrid': ('La calle Madrid, en Getafe, en 2005', 'Miguel303xm', 'CC BY-SA 2.5', 'Calle-madrid.getafe.jpg'),
    'cabra-montilla': ('La calle Santa Rosalía, en Cabra, en 2010', 'Hugh Llewelyn', 'CC BY-SA 2.0', 'Calle_Santa_Rosalía,_Cabra.jpg'),
    'lalin-vilanova-de-arousa': ('Vecinos en la feria de la rúa Serafín Tubío de Marín, en la misma provincia que Lalín y Vilanova de Arousa, en 2025', 'Bene Riobó', 'CC BY-SA 4.0', 'Feira_de_Marín_02.jpg'),
    'cuenca-de-pamplona': ('Terraza en una plaza de Zizur Mayor, en 2012', 'Zarateman', 'CC0', 'Zizur_Mayor_08.jpg'),
    'puerto-real': ('Puestos de pescado en el mercado de abastos de Puerto Real, en 2025', 'Zarateman', 'CC0', 'Puerto_Real_-_Mercado_1.jpg'),
    'badalona': ('La calle del Mar, en Badalona, en 2014', 'Zarateman', 'CC BY-SA 4.0', 'Badalona_-_10.JPG'),
    'paro-renta-participacion': ('Gente esperando en la puerta de una oficina del INEM, en 2009', 'Ekinez Sortu', 'CC BY-SA 2.0', 'En_la_puerta_de_una_oficina_del_INEM.jpg'),
    'cuencas-mineras-asturianas': ('Manifestación del Primero de Mayo de 1910 en Mieres', 'Álbum Fotográfico de Mieres', 'dominio público', 'Primero_de_Mayo_de_1910,_Mieres.jpg'),
    'getxo-portugalete': ('Terrazas en la calle Manuel Calvo, en Portugalete, en 2024', 'Zarateman', 'CC0', 'Portugalete_-_Calle_Manuel_Calvo_1.jpg'),
    'aranda-miranda': ('Vecinos en el mercadillo de los sábados de Miranda de Ebro, en 2024', 'Zarateman', 'CC0', 'Miranda_de_Ebro_-_Mercadillo_de_los_sábados_01.jpg'),
    'castro-urdiales': ('Una calle comercial de Castro-Urdiales, en 2023', 'Zarateman', 'CC0', 'Castro_Urdiales_15.jpg'),
    'vigo': ('La rúa do Príncipe, en Vigo, en 2010', 'Certo Xornal', 'CC BY 2.0', 'Vigo_rua_Principe.jpg'),
    'pueblos-pequenos': ('Vecinos en el mercado de los domingos en una calle de Benlloc (Castellón), en 2016', 'Juan Emilio Prades Bel', 'CC BY-SA 4.0', 'Mercado_urbano_de_los_domingos_(Benlloch,_Castellón).JPG'),
    # tercera tanda (2026-10-07)
    'jodar': ('Vecinos en la plaza de la Corredera de Cazorla, en la misma provincia que Jódar, en 2012', 'Martin Haisch', 'CC BY-SA 2.0', 'Cazorla_Plaza_Corredera.jpg'),
    'sant-cugat-badia': ('Paseantes en el carrer de Santa Maria de Sant Cugat del Vallès, en 2023', 'Enric', 'CC BY-SA 4.0', '03_Cases_al_carrer_de_Santa_Maria,_25-35_(Sant_Cugat_del_Vallès).jpg'),
    'ontigola-aranjuez': ('Viajeros ante la estación de tren de Aranjuez, en 2021', 'Emijrp', 'CC BY-SA 4.0', 'Aranjuez_en_noviembre_de_2021_02.jpg'),
    'morrazo-sanxenxo': ('Vecinos paseando por una calle del centro de Cangas, en el Morrazo, en 2013', 'Luis Miguel Bugallo Sánchez (Lmbuga)', 'CC BY-SA 3.0', 'Cangas._Galiza-7.jpg'),
    'arahal-marchena': ('Vecinos en la calle Mesones de Constantina, en la misma provincia que Arahal y Marchena, en 2005', 'Phillip Capper', 'CC BY 2.0', 'Calle_Mesones,_Constantina.jpg'),
    'manilva': ('Paseantes en el mercadillo del puerto deportivo de Estepona, vecina de Manilva, en 2014', 'Turista Inglesa', 'CC BY-SA 4.0', 'Mercadillo_puerto_de_Estepona.jpg'),
    'alcoi': ('Terrazas en la plaça de Dins de Alcoi, en 2015', 'chisloup', 'CC BY 3.0', 'Alcoi_-_panoramio_(15).jpg'),
    'capitales-municipales': ('Paseantes en la calle Sierpes de Sevilla, en 2016', 'CarlosVdeHabsburgo', 'CC BY-SA 4.0', 'Calle_Sierpes_02.jpg'),
    'europeas-2024': ('Vecinos en la calle Ancha de Sanlúcar de Barrameda, en 2010', 'Frobles', 'CC BY-SA 3.0', 'Calle_Ancha_de_Sanlucar_de_Barrameda.JPG'),
}

COLOR = {
    'cadiz-madrid-29n': [
        ('La ciudad de Cádiz es la capital de provincia española que más población ha perdido en lo que va de siglo: tenía 140.061 habitantes en 2000 y 109.950 en 2025, más de un 20 % menos, según el padrón del INE.',
         ['https://theobjective.com/espana/andalucia/2025-08-19/cadiz-20-habitantes-espana-ocho-millones/',
          'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP5356?nult=30'])],
    'madrid-voto-exterior': [
        ('En octubre de 2022 una reforma de la ley electoral suprimió el «voto rogado»: desde entonces, los españoles inscritos como residentes en el extranjero ya no tienen que solicitar el voto para poder votar en unas generales.',
         ['https://www.exteriores.gob.es/Embajadas/londres/es/Comunicacion/Noticias/Paginas/Articulos/20221005_NOT01.aspx',
          'https://theobjective.com/espana/politica/2022-10-03/final-voto-rogado-boe/'])],
    'escanos-ajustados-2023': [
        ('La ciudad de Girona ha ganado más de 30.000 vecinos en lo que va de siglo: tenía 75.256 habitantes en 2001 y unos 109.000 en 2025.',
         ['https://umat.girona.cat/shared/imatges/observatori_estudis/185/fitxers/Basic_padro_2025.pdf',
          'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP7627?nult=30'])],
    'sur-de-madrid': [
        ('Parla es uno de los municipios que más han crecido de España en este siglo: pasó de 74.203 habitantes en 2000 a 134.833 en 2024, más de un 80 % más, según el padrón del INE.',
         ['https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP13225?nult=30',
          'https://vivirediciones.es/?p=882591'])],
    'a-illa-vilanova-de-arousa': [
        ('A Illa de Arousa se separó de Vilanova de Arousa el 1 de enero de 1997 y está unida a tierra firme por un puente de unos 2 kilómetros, inaugurado en 1985.',
         ['https://elespanol.com/treintayseis/cultura/conoce-o-salnes/20201201/illa-arousa-municipio-joven-galicia/540197805_0.amp.html',
          'https://www.xunta.gal/dog/Publicados/1996/19961128/AnuncioC4AA_es.html',
          'https://www.ailladearousa.es/turismo/descargas/223'])],
    'cabra-montilla': [
        ('Montilla es la ciudad natal de Gonzalo Fernández de Córdoba, el Gran Capitán, nacido en 1453.',
         ['https://www.montillaturismo.es/node/238', 'https://www.upo.es/patio-colorado/?p=6712']),
        ('Cabra es la cuna del novelista Juan Valera, autor de «Pepita Jiménez», que nació allí el 18 de octubre de 1824.',
         ['https://journals.uco.es/CODEX/article/view/17954',
          'https://www.centrodeestudiosandaluces.es/contenido/datos/publicaciones/documentos/AH_Valera_especial.pdf'])],
    'puerto-real': [
        ('Puerto Real nació por decisión de los Reyes Católicos, que le dieron carta puebla el 18 de junio de 1483 para tener un puerto bajo jurisdicción directa de la Corona en la bahía de Cádiz.',
         ['https://puertoreal.es/webs/Revista-Matagorda/N05-Art01.pdf',
          'https://revistas.ucm.es/index.php/DOCU/article/download/81326/4564456560498/4564456642973'])],
    'badalona': [
        ('Badalona se levanta sobre Baetulo, una ciudad romana fundada hacia el año 100 a. C.; su yacimiento, bajo el centro histórico, es bien cultural de interés nacional desde 1995 y sus termas se visitan en el Museu de Badalona.',
         ['https://www.boe.es/boe/dias/1996/01/08/pdfs/A00495-00496.pdf',
          'https://www.spain.info/es/lugares-interes/museo-municipal-badalona'])],
    'cuencas-mineras-asturianas': [
        ('En la primavera de 1962 empezó en el pozo Nicolasa de Mieres la «huelgona», un paro de picadores que se extendió a las cuencas mineras asturianas y a otras zonas de España.',
         ['https://www.eldiario.es/opinion/tribuna-abierta/huelgas-vencieron-franco_129_8997810.html',
          'https://revistas.uned.es/index.php/REI/article/download/24682/20852/57854'])],
    'lalin-vilanova-de-arousa': [
        ('Vilanova de Arousa es la cuna oficial de Ramón María del Valle-Inclán, nacido el 28 de octubre de 1866; su casa natal, el pazo de O Cuadrante, es hoy casa-museo.',
         ['https://www.spain.info/es/lugares-interes/pazo-cuadrante-casa-museo-valle-inclan/',
          'https://www.eldebate.com/cultura/20260105/cuatro-datos-valleinclan-recordar-padre-esperpento-90-aniversario-muerte_371382.html']),
        ('Lalín celebra desde 1969 la Feira do Cocido, que en 2020 fue declarada Fiesta de Interés Turístico Internacional.',
         ['https://convenios.xunta.gal/consultaconvenios/documento/f2258198-9253-4609-9658-6a513b9b2100',
          'https://www.spain.info/es/agenda/feria-cocido/'])],
    'cuenca-de-pamplona': [
        ('Zizur Mayor formó parte de la Cendea de Cizur hasta el 6 de noviembre de 1992, cuando se separó de ella y se constituyó en municipio propio.',
         ['https://www.noticiasdenavarra.com/navarra/comarca-de-pamplona/2022/11/10/zizur-mayor-30-anos-paticas-6216439.html',
          'https://dialnet.unirioja.es/descarga/articulo/9594994.pdf'])],
    'getxo-portugalete': [
        ('Getxo y Portugalete están unidos desde 1893 por el Puente de Bizkaia, el puente colgante transbordador más antiguo del mundo, que la UNESCO declaró Patrimonio de la Humanidad en 2006.',
         ['https://www.euskadi.eus/puente-colgante/portugalete-getxo/camino-de-santiago/web01-a2donjak/es/',
          'https://www.spain.info/es/lugares-interes/puente-colgante-vizcaya/'])],
    'aranda-miranda': [
        ('Miranda de Ebro es desde el siglo XIX un nudo ferroviario: en ella se cruzan las líneas Madrid-Irún y Castejón-Bilbao.',
         ['https://www.adif.es/w/miranda-de-ebro', 'https://mirandadeebro.es/wp-content/uploads/FMS/05/B0/expocentenario.pdf']),
        ('Bajo el casco histórico de Aranda de Duero se extiende una red de bodegas y túneles excavados para guardar el vino, declarada Bien de Interés Cultural por la Junta de Castilla y León en 2015.',
         ['https://www.arandadeduero.es/archivos/MEMORIA%20ANEJO%20Y%20PLANOS.pdf',
          'https://www.agronewscastillayleon.com/las-bodegas-subterraneas-de-aranda-de-duero-declaradas-bien-de-interes-cultural'])],
    'los-palacios-y-villafranca': [
        ('El municipio nació en 1836 de la unión de dos pueblos vecinos, Los Palacios y Villafranca de la Marisma.',
         ['https://www.lavozdelsur.es/ediciones/sevilla/palacios-no-tenia-historia-pero-ya-sabe-dia-nacio-hace-654-anos_336242_102.html',
          'https://www.adelquivir.org/municipio/los-palacios-y-villafranca/'])],
    'castro-urdiales': [
        ('Junto al castillo-faro de Castro-Urdiales se alza la iglesia de Santa María de la Asunción, comenzada en el siglo XIII y considerada la principal muestra del gótico en Cantabria.',
         ['https://www.spain.info/es/destino/castro-urdiales/',
          'https://micastro.castro-urdiales.net/recursosWEB/publicaciones/folletos-digitales/Folleto_Digital_Recorrido_Historico.pdf'])],
    'vigo': [
        ('Vigo tiene desde 1958 una fábrica de automóviles, abierta por Citroën y hoy de Stellantis.',
         ['https://www.vozpopuli.com/economia/fabrica-vigo-citroen-grand-c4.html',
          'https://www.hibridosyelectricos.com/furgonetas/citroen-e-berlingo-electrica-15-millones-pasa-historia-vigo_57712_102.html'])],
    'pueblos-pequenos': [
        ('Unos seis de cada diez municipios de España tienen menos de 1.000 habitantes, y en ellos vive en torno al 3 % de la población.',
         ['https://ine.es/infografias/infografia_padron.pdf',
          'https://api.infogen.uvigo.es/uploads/REDLOCALIS/originals/29b65ca0-ae44-4aff-b9fa-3bb4f2aa16f0.pdf'])],
    # tercera tanda (2026-10-07)
    'jodar': [
        ('Cada primavera, vecinos de Jódar, a veces con sus hijos, se desplazan a Navarra como temporeros para la campaña del espárrago.',
         ['https://www.noticiasdenavarra.com/economia/2021/04/17/agricultores-temporeros-barco-2146872.html',
          'https://agroinformacion.com/la-recogida-del-esparrago-de-navarra-arranca-con-pruebas-pcr-a-los-temporeros-y-jornadas-de-muchas-horas-agachados/']),
        ('El esparto fue durante generaciones el gran oficio de Jódar; entró en declive en los años sesenta, con la llegada de los materiales sintéticos, aunque el pueblo conserva talleres que lo trabajan.',
         ['https://www.eldebate.com/espana/andalucia/20260924/pueblo-jaen-fabrica-mano-sombrillas-esparto-llegan-playas-toda-espana_461973.html',
          'https://iesjuanlopezmorillas.es/index.php/informacion/localidad-y-entorno'])],
    'sant-cugat-badia': [
        ('Badia del Vallès nació como un polígono de vivienda protegida: sus bloques se levantaron en los años setenta y, hasta 1994, la entonces llamada Ciutat Badia la gestionó una mancomunidad de Barberà del Vallès y Cerdanyola del Vallès, de cuyos términos se segregó para ser municipio.',
         ['https://www.boe.es/boe/dias/2015/09/09/pdfs/BOE-A-2015-9724.pdf',
          'https://www.3cat.cat/3catinfo/de-2200-euros-fa-50-anys-a-180000-ara-adeu-als-pisos-protegits-de-badia-del-valles/noticia/3327188/']),
        ('Badia del Vallès ocupa 0,93 kilómetros cuadrados, y en ellos viven unas 13.000 personas.',
         ['https://api.idescat.cat/emex/v1/dades.json?id=089045&i=f271,f171&lang=es',
          'https://www.3cat.cat/3catinfo/de-2200-euros-fa-50-anys-a-180000-ara-adeu-als-pisos-protegits-de-badia-del-valles/noticia/3327188/'])],
    'ontigola-aranjuez': [
        ('Ontígola ha multiplicado su población en lo que va de siglo: el padrón del INE le contaba 1.250 vecinos en 2000 y 5.101 en 2025, y su ayuntamiento recordaba en 2022 que una década antes apenas llegaba a 3.000.',
         ['https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP20797?nult=30',
          'https://www.ontigola.es/ontigola-la-realidad-del-pueblo-en-el-que-vivimos/']),
        ('El Mar de Ontígola, el humedal que da nombre al pueblo, está en término de Aranjuez: Felipe II mandó crearlo en 1552 para atraer aves de cetrería, acabó abasteciendo de agua los jardines del Real Sitio y hoy es reserva natural.',
         ['https://www.eldiario.es/viajes/humedal-madrid-nacio-orden-felipe-ii-hoy-alberga-mayores-reservas-mariposas-europa-pm_1_13395962.html',
          'https://www.telemadrid.es/programas/madrid-desde-el-aire/mar-Madrid-Aranjuez-2-2333786607--20210420103200.html'])],
    'morrazo-sanxenxo': [
        ('En 1617 un millar de corsarios berberiscos asaltaron Cangas; en 1622 la Inquisición condenó por brujería a la vecina María Soliña, a quien la villa recuerda cada año.',
         ['https://cangas.gal/es/areas/turismo/nuestra-historia/invasion-de-piratas-berberiscos-en-1617',
          'https://atlantico.net/articulo/morrazo/maria-solina-enfrenta-hoy-paseillo-antes-juicio-final-cangas/202409291124161052685.html'])],
    'arahal-marchena': [
        ('Arahal celebra a principios de septiembre la Fiesta del Verdeo, dedicada a la campaña de recogida de la aceituna de mesa.',
         ['https://www.elpespunte.es/articulo/provincia/lvi-fiesta-del-verdeo-de-arahal-la-unica-de-la-provincia-dedicada-a-la-campana-de-recogida-de-aceitunas/20240829110546067981.html',
          'https://www.andalucia.org/blog/post/la-cosecha-de-la-aceituna-del-verdeo-al-botifuera/']),
        ('La iglesia de San Juan Bautista de Marchena guarda en su sacristía una serie de lienzos de Francisco de Zurbarán encargados en la década de 1630.',
         ['https://www.juntadeandalucia.es/cultura/agendaculturaldeandalucia/evento/museo-zurbaran-en-la-iglesia-de-san-juan-bautista-de-marchena',
          'https://www.archisevilla.org/el-cristo-crucificado-de-zurbaran-de-san-juan-bautista-marchena/'])],
    'manilva': [
        ('Manilva casi triplicó su población en veinte años: pasó de 6.270 habitantes empadronados en 2002 a 17.157 en 2022.',
         ['https://www.elespanol.com/malaga/20221227/boom-poblacion-malaga-municipios-duplicado-triplicado-residentes/728677160_0.html',
          'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP13666?nult=30']),
        ('Antes del turismo, la caña de azúcar y la viña fueron durante siglos los motores de la economía de Manilva.',
         ['https://manilva.es/manilva-el-municipio/',
          'https://ws089.juntadeandalucia.es/institutodeestadisticaycartografia/blog/2016/03/sabinillas-manilva/'])],
    'alcoi': [
        ('En julio de 1873 los obreros del textil y del papel de Alcoi fueron a la huelga general y protagonizaron la llamada Revolución del Petróleo, en la que se hicieron con el ayuntamiento durante unos días.',
         ['https://www.elsaltodiario.com/memoria-historica/revolucion-del-petroleo-alcoi',
          'https://www.elespanol.com/alacant/alcoi/20220713/alcoy-prepara-aniversario-revolucion-petroleo-revuelta-espana/687181426_0.html']),
        ('Los Moros i Cristians de Alcoi, en honor de Sant Jordi, conmemoran la batalla de 1276 contra el caudillo Al-Azraq y son fiesta de Interés Turístico Internacional desde 1980.',
         ['https://cvcultura.es/wp-content/uploads/634-2.pdf', 'https://www.upv.es/entidades/epsa/?p=19359'])],
    'capitales-municipales': [
        ('Soria es la provincia menos poblada de España: a 1 de enero de 2025 tenía 90.234 habitantes empadronados, 41.025 de ellos en la capital.',
         ['https://elmirondesoria.es/soria/capital/el-ine-certifica-poblacion-oficial-de-soria-en-2025-90-234-habiantes',
          'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP18616?nult=30']),
        ('La ciudad de Zamora alcanzó en 2008 su máximo de población del siglo XXI, 66.672 empadronados; en 2025 tenía 59.815.',
         ['https://www.elespanol.com/castilla-y-leon/region/zamora/20241213/capital-zamorana-gana-poblacion-primera-vez-ano/908409343_0.html',
          'https://servicios.ine.es/wstempus/js/ES/DATOS_SERIE/DPOP23602?nult=30'])],
    'europeas-2024': [
        ('Contando el voto de los españoles residentes en el extranjero, la participación oficial de las europeas del 9 de junio de 2024 fue del 46,39 % (17.652.007 votantes de 38.050.286 electores), frente al 60,73 % de 2019. Esta pieza usa la participación de los residentes en España.',
         ['https://www.boe.es/boe/dias/2024/06/28/pdfs/BOE-A-2024-13092.pdf',
          'https://results.elections.europa.eu/es/resultados-nacionales/espana/2024-2029/'])],
}


def terreno(p):
    """Añade a la pieza `foto` y `color` si los tiene."""
    s = p['slug']
    if s in FOTOS:
        alt, autor, lic, archivo = FOTOS[s]
        p['foto'] = dict(src=f'../../img/{s}.jpg', alt=alt, autor=autor, licencia=lic, url=C + archivo)
    if s in COLOR:
        p['color'] = COLOR[s]
    return p
