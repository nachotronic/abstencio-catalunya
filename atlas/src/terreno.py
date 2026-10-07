"""Fotos y notas de color («Sobre el terreno») de cada pieza del Atlas (2026-10-07).

Fotos: Wikimedia Commons, gente en escenas de calle, sin playas y sin repetir. Se guardan en atlas/img/<slug>.jpg
(1.200 px de ancho como máximo); el crédito y la licencia se copian de la página del archivo en Commons.
Notas de color: datos descriptivos del lugar, no explicaciones del voto. Cada una lleva dos fuentes independientes
(nunca Wikipedia), abiertas y comprobadas; el fragmento literal que apoya cada nota está en el expediente.
Las piezas sin foto no tienen en Commons una escena de calle con gente del lugar.
"""

C = 'https://commons.wikimedia.org/wiki/File:'

FOTOS = {
    'cadiz-madrid-29n': ('Un coro del Carnaval de Cádiz canta en la plaza de Fedúchy, en 2023', 'NACLE', 'CC BY-SA 4.0', 'Coro_carnaval_cadiz_2023.jpg'),
    'madrid-voto-exterior': ('Gente en la Puerta del Sol de Madrid, en 2007', 'Dario Alvarez', 'CC BY 2.0', 'Puerta_del_Sol_CONVAR12_(1243488902).jpg'),
    'escanos-ajustados-2023': ('La Rambla de la Llibertat, en Girona, en 2025', 'Aktron', 'CC BY-SA 4.0', 'Girona_Rambla_de_la_Llibertat.jpg'),
    'capitales-frente-a-su-provincia': ('La calle Elvira de Granada, al anochecer, en 2012', 'Curimedia', 'CC BY 2.0', 'Elvira_Street_(8169708505).jpg'),
    'sur-de-madrid': ('La calle Madrid, en Getafe, en 2005', 'Miguel303xm', 'CC BY-SA 2.5', 'Calle-madrid.getafe.jpg'),
    'cabra-montilla': ('La calle Santa Rosalía, en Cabra, en 2010', 'Hugh Llewelyn', 'CC BY-SA 2.0', 'Calle_Santa_Rosalía,_Cabra.jpg'),
    'puerto-real': ('Puestos de pescado en el mercado de abastos de Puerto Real, en 2025', 'Zarateman', 'CC0', 'Puerto_Real_-_Mercado_1.jpg'),
    'badalona': ('La calle del Mar, en Badalona, en 2014', 'Zarateman', 'CC BY-SA 4.0', 'Badalona_-_10.JPG'),
    'paro-renta-participacion': ('Gente esperando en la puerta de una oficina del INEM, en 2009', 'Ekinez Sortu', 'CC BY-SA 2.0', 'En_la_puerta_de_una_oficina_del_INEM.jpg'),
    'cuencas-mineras-asturianas': ('Manifestación del Primero de Mayo de 1910 en Mieres', 'Álbum Fotográfico de Mieres', 'dominio público', 'Primero_de_Mayo_de_1910,_Mieres.jpg'),
    'getxo-portugalete': ('Terrazas en la calle Manuel Calvo, en Portugalete, en 2024', 'Zarateman', 'CC0', 'Portugalete_-_Calle_Manuel_Calvo_1.jpg'),
    'aranda-miranda': ('Desfile de las fiestas de San Juan del Monte en Miranda de Ebro, en 2007', 'DBP - Mr.Benq', 'CC BY-SA 2.5', 'Desfile_San_Juan_2007.JPG'),
    'castro-urdiales': ('Una calle comercial de Castro-Urdiales, en 2023', 'Zarateman', 'CC0', 'Castro_Urdiales_15.jpg'),
    'vigo': ('La rúa do Príncipe, en Vigo, en 2010', 'Certo Xornal', 'CC BY 2.0', 'Vigo_rua_Principe.jpg'),
    'pueblos-pequenos': ('Danzadores de zancos en la plaza de la Obra de Anguiano (La Rioja), en 2007', 'BigSus', 'CC BY-SA 3.0', 'Danzadores_de_zancos_en_la_plaza_de_la_Obra_de_Anguiano.JPG'),
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
