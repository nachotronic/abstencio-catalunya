"""Rutas de las páginas por territorio de /elecciones/, de los municipios en /municipio/ y de los temas en /temas/
(las genera src/territorios.py).

Módulo aparte, sin datos, para que otras secciones (el Atlas) puedan enlazar a esas páginas sin cargar nada.
"""
import json, pathlib, re, unicodedata

# INE: provincia → nombre corto para la URL
PROV_SLUG = {
    '01': 'alava', '02': 'albacete', '03': 'alicante', '04': 'almeria', '05': 'avila', '06': 'badajoz', '07': 'illes-balears',
    '08': 'barcelona', '09': 'burgos', '10': 'caceres', '11': 'cadiz', '12': 'castellon', '13': 'ciudad-real', '14': 'cordoba',
    '15': 'a-coruna', '16': 'cuenca', '17': 'girona', '18': 'granada', '19': 'guadalajara', '20': 'gipuzkoa', '21': 'huelva',
    '22': 'huesca', '23': 'jaen', '24': 'leon', '25': 'lleida', '26': 'la-rioja', '27': 'lugo', '28': 'madrid', '29': 'malaga',
    '30': 'murcia', '31': 'navarra', '32': 'ourense', '33': 'asturias', '34': 'palencia', '35': 'las-palmas', '36': 'pontevedra',
    '37': 'salamanca', '38': 'santa-cruz-de-tenerife', '39': 'cantabria', '40': 'segovia', '41': 'sevilla', '42': 'soria',
    '43': 'tarragona', '44': 'teruel', '45': 'toledo', '46': 'valencia', '47': 'valladolid', '48': 'bizkaia', '49': 'zamora',
    '50': 'zaragoza', '51': 'ceuta', '52': 'melilla'}
# comunidad: (nombre, «en ...», provincias). El slug coincide con el de su pieza «Historia electoral» de Actualidad.
CCAA = {
    'andalucia': ('Andalucía', 'en Andalucía', ['04', '11', '14', '18', '21', '23', '29', '41']),
    'aragon': ('Aragón', 'en Aragón', ['22', '44', '50']),
    'asturias': ('Asturias', 'en Asturias', ['33']),
    'baleares': ('Illes Balears', 'en las Illes Balears', ['07']),
    'canarias': ('Canarias', 'en Canarias', ['35', '38']),
    'cantabria': ('Cantabria', 'en Cantabria', ['39']),
    'castilla-y-leon': ('Castilla y León', 'en Castilla y León', ['05', '09', '24', '34', '37', '40', '42', '47', '49']),
    'castilla-la-mancha': ('Castilla-La Mancha', 'en Castilla-La Mancha', ['02', '13', '16', '19', '45']),
    'cataluna': ('Cataluña', 'en Cataluña', ['08', '17', '25', '43']),
    'comunidad-valenciana': ('Comunitat Valenciana', 'en la Comunitat Valenciana', ['03', '12', '46']),
    'extremadura': ('Extremadura', 'en Extremadura', ['06', '10']),
    'galicia': ('Galicia', 'en Galicia', ['15', '27', '32', '36']),
    'madrid': ('Comunidad de Madrid', 'en la Comunidad de Madrid', ['28']),
    'murcia': ('Región de Murcia', 'en la Región de Murcia', ['30']),
    'navarra': ('Navarra', 'en Navarra', ['31']),
    'pais-vasco': ('País Vasco', 'en el País Vasco', ['01', '20', '48']),
    'la-rioja': ('La Rioja', 'en La Rioja', ['26']),
    'ceuta': ('Ceuta', 'en Ceuta', ['51']),
    'melilla': ('Melilla', 'en Melilla', ['52']),
}
PROV_CCAA = {p: c for c, (_, _, ps) in CCAA.items() for p in ps}
PROV_NOMBRE = {'01': 'Araba/Álava', '02': 'Albacete', '03': 'Alicante', '04': 'Almería', '05': 'Ávila', '06': 'Badajoz', '07': 'Illes Balears', '08': 'Barcelona',
               '09': 'Burgos', '10': 'Cáceres', '11': 'Cádiz', '12': 'Castellón/Castelló', '13': 'Ciudad Real', '14': 'Córdoba', '15': 'A Coruña', '16': 'Cuenca',
               '17': 'Girona', '18': 'Granada', '19': 'Guadalajara', '20': 'Gipuzkoa', '21': 'Huelva', '22': 'Huesca', '23': 'Jaén', '24': 'León', '25': 'Lleida',
               '26': 'La Rioja', '27': 'Lugo', '28': 'Madrid', '29': 'Málaga', '30': 'Murcia', '31': 'Navarra', '32': 'Ourense', '33': 'Asturias', '34': 'Palencia',
               '35': 'Las Palmas', '36': 'Pontevedra', '37': 'Salamanca', '38': 'Santa Cruz de Tenerife', '39': 'Cantabria', '40': 'Segovia', '41': 'Sevilla',
               '42': 'Soria', '43': 'Tarragona', '44': 'Teruel', '45': 'Toledo', '46': 'Valencia/Valéncia', '47': 'Valladolid', '48': 'Bizkaia', '49': 'Zamora',
               '50': 'Zaragoza', '51': 'Ceuta', '52': 'Melilla'}

# Piezas de Actualidad sobre un territorio concreto (provincias INE). Las de la serie «Historia electoral»
# se enlazan solas desde su comunidad.
ACTUALIDAD_LUGAR = {
    'avila-suarez-cds': ['05'], 'baltar-censo-y-participacion': ['32'], 'beiras-nacionalismo-gallego': ['15', '27', '32', '36'],
    'colau-barcelona-comuns': ['08'], 'europeas-arona': ['38'], 'euskadi-empate-a-tres': ['01', '20', '48'],
    'mont-roig-municipio-cambiante': ['43'], 'municipios-fieles': ['41'], 'pisos-turisticos-y-votantes': ['08'],
    'plasencia-acierta-siempre': ['10'], 'precio-del-alquiler-y-voto': ['46'], 'psa-andalucistas-1979': ['04', '11', '14', '18', '21', '23', '29', '41'],
    'psoe-andalucia-generales-autonomicas': ['04', '11', '14', '18', '21', '23', '29', '41'], 'psoe-madrid-municipales-generales': ['28'],
    'puigdemont-junts-congreso-parlament': ['08', '17', '25', '43'], 'rufian-erc-comuns': ['08', '17', '25', '43'], 'trebujena-pce-sumar': ['11'],
    'acampada-sol-distrito-centro': ['28'], 'aceituna-de-mesa-pueblos': ['41'], 'alianca-catalana-ceo-mapa': ['08', '17', '25', '43'],
    'almeida-feijoo-madrid': ['28'], 'barcelona-barrio-a-barrio-29n': ['08'], 'ceuta-melilla-participacion-29n': ['51', '52'],
    'ciudadanos-democracia21-29n': ['08', '28'], 'madrid-barrio-a-barrio-29n': ['28'], 'malaga-barrio-a-barrio-29n': ['29'],
    'minguez-lleida-29n': ['25'], 'murcia-barrio-a-barrio-29n': ['30'], 'palma-barrio-a-barrio-29n': ['07'],
    'sevilla-barrio-a-barrio-29n': ['41'], 'valencia-barrio-a-barrio-29n': ['46'], 'zaragoza-barrio-a-barrio-29n': ['50'],
}
# Piezas centradas en un municipio: código INE y nombre, para enlazar su página y el mapa centrado en él (?m=)
ACTUALIDAD_MUNICIPIO = {
    'acampada-sol-distrito-centro': ('28079', 'Madrid'), 'almeida-feijoo-madrid': ('28079', 'Madrid'),
    'barcelona-barrio-a-barrio-29n': ('08019', 'Barcelona'), 'madrid-barrio-a-barrio-29n': ('28079', 'Madrid'),
    'malaga-barrio-a-barrio-29n': ('29067', 'Málaga'), 'murcia-barrio-a-barrio-29n': ('30030', 'Murcia'),
    'palma-barrio-a-barrio-29n': ('07040', 'Palma'), 'sevilla-barrio-a-barrio-29n': ('41091', 'Sevilla'),
    'valencia-barrio-a-barrio-29n': ('46250', 'València'), 'zaragoza-barrio-a-barrio-29n': ('50297', 'Zaragoza'),
    'calle-que-parte-el-voto': ('46250', 'València'), 'calle-que-parte-madrid': ('28079', 'Madrid'),
    'girona-barri-a-barri-29n': ('17079', 'Girona'),
}
# Piezas de cada página temática
TEMA_RENTA = ['maricarmen-alquiler-y-voto', 'alquiler-ciudad-a-ciudad', 'psoe-barrios-de-alquiler', 'precio-del-alquiler-y-voto',
              'huelga-11n-paro-participacion', 'vox-poblacion-nacida-fuera', 'pisos-turisticos-y-votantes',
              'pobreza-participacion-barrios', 'pensiones-barrios-envejecidos', 'malaga-barrio-a-barrio-29n']
TEMA_SECCION = ['como-voto-tu-calle', 'calle-que-parte-el-voto', 'madrid-barrio-a-barrio-29n', 'barcelona-barrio-a-barrio-29n',
                'valencia-barrio-a-barrio-29n', 'sevilla-barrio-a-barrio-29n', 'zaragoza-barrio-a-barrio-29n', 'malaga-barrio-a-barrio-29n',
                'murcia-barrio-a-barrio-29n', 'palma-barrio-a-barrio-29n',
                'izquierda-del-psoe-secciones', 'colau-barcelona-comuns', 'rufian-erc-comuns', 'mapa-derecha-1977-2023']

TEMA_PARTICIPACION = ['pobreza-participacion-barrios', 'maricarmen-alquiler-y-voto', 'huelga-11n-paro-participacion', 'votar-en-noviembre',
                      'ceuta-melilla-participacion-29n', 'palma-barrio-a-barrio-29n', 'malaga-barrio-a-barrio-29n', 'europeas-solo-con-municipales',
                      'baltar-censo-y-participacion', 'censo-electoral-desde-1977']
TEMA_MUNICIPIOS = ['nunca-gano-el-psoe', 'nunca-gano-la-derecha', 'psoe-1982-mas-del-60', 'pueblos-menos-votantes-que-en-1977',
                   'ucd-ciudadanos-hundimiento', 'municipios-fieles', 'plasencia-acierta-siempre', 'mont-roig-municipio-cambiante',
                   'trebujena-pce-sumar', 'aceituna-de-mesa-pueblos', 'mapa-derecha-1977-2023']
# Piezas sobre las generales del 29N que no llevan «29n» en la ruta
TEMA_29N = ['votar-en-noviembre', 'vivienda-inmigracion-economia-cis', 'alianca-catalana-ceo-mapa', 'almeida-feijoo-madrid']
# Diputados por provincia: 2023 y 2026 (Real Decreto 806/2026, BOE del 6 de octubre: Madrid gana uno y Cádiz lo pierde)
ESCANOS_2023 = {'01': 4, '02': 4, '03': 12, '04': 6, '05': 3, '06': 5, '07': 8, '08': 32, '09': 4, '10': 4, '11': 9, '12': 5,
                '13': 5, '14': 6, '15': 8, '16': 3, '17': 6, '18': 7, '19': 3, '20': 6, '21': 5, '22': 3, '23': 5, '24': 4,
                '25': 4, '26': 4, '27': 4, '28': 37, '29': 11, '30': 10, '31': 5, '32': 4, '33': 7, '34': 3, '35': 8, '36': 7,
                '37': 4, '38': 7, '39': 5, '40': 3, '41': 12, '42': 2, '43': 6, '44': 3, '45': 6, '46': 16, '47': 5, '48': 8,
                '49': 3, '50': 7, '51': 1, '52': 1}
ESCANOS_2026 = {**ESCANOS_2023, '28': 38, '11': 8}
assert sum(ESCANOS_2023.values()) == 350 and sum(ESCANOS_2026.values()) == 350


# Páginas nodales de /temas/: título, entradilla, piezas de Actualidad, páginas de datos y secciones del Atlas
# (rutas desde la raíz). Una pieza puede estar en varios temas.
HISTORIA_CCAA = [f'{c}-historia-electoral' for c in CCAA]
TEMAS = {
    'renta-y-voto': dict(
        nombre='Renta y voto',
        titulo='Renta y voto: cómo votan los barrios ricos y los pobres de España',
        intro='Las piezas que cruzan el voto de cada sección censal con la renta de sus hogares, el paro, las pensiones, '
              'los salarios o el oficio de sus vecinos. Para comparar una sola sección con el resto, el mapa de la portada.',
        piezas=TEMA_RENTA + ['barrios-rentistas-pp-psoe-29n', 'barrios-pobres-derecha-ricos-izquierda', 'salarios-pensiones-ayudas-espana',
                             'salaris-pensions-ajudes-girona', 'oficios-y-voto-municipios-29n', 'voto-autonomos-secciones-29n',
                             'voto-jubilados-secciones-29n', 'pensiones-revalorizacion-29n', 'funcionarios-pagas-extra-29n', 'blocs-i-cases-girona', 'vox-barrios-obreros-clase-29n', 'salario-minimo-provincias-feijoo-29n'],
        datos=[('elecciones/voto-y-renta-por-barrios/', 'Voto y renta por barrios en toda España'),
               ('elecciones/mapa-electoral-seccion-censal/', 'Mapa electoral de España por sección censal')],
        atlas=[]),
    'participacion': dict(
        nombre='Participación y abstención',
        titulo='Participación y abstención: quién no vota en España y dónde',
        intro='Dónde se vota menos y quién se queda en casa: participación por barrio, por renta y por tipo de elección, '
              'el censo electoral y el voto de los residentes en el extranjero.',
        piezas=TEMA_PARTICIPACION + ['barrios-donde-vota-menos-de-la-mitad', 'alquiler-ciudad-a-ciudad', 'europeas-arona', 'voto-en-blanco',
                                     'pensiones-censo-mayores-29n', 'ley-nietos-voto-exterior-29n', 'ley-nietos-donde-estan-29n',
                                     'blocs-i-cases-girona', 'salaris-pensions-ajudes-girona', 'vox-barrios-obreros-clase-29n', 'girona-1936-participacio'],
        datos=[('elecciones/participacion-electoral-por-barrio/', 'Participación electoral por barrio en toda España'),
               ('elecciones/censo-electoral-2026/', 'Censo electoral de 2026 por provincia y municipio'),
               ('abstencion.html', '¿Quién no vota en Cataluña? La abstención sección a sección')],
        atlas=[('atlas/quien-no-vota/', 'Atlas: quién no vota')]),
    'historico': dict(
        nombre='Historia electoral',
        titulo='Historia electoral de España: las elecciones desde 1977, comunidad a comunidad',
        intro='Las generales de la Segunda República (1933 y 1936), las 16 desde 1977 y las autonómicas de cada comunidad: quién ganó, qué partidos desaparecieron '
              'y qué municipios votan siempre igual o cambian siempre de ganador.',
        piezas=HISTORIA_CCAA + ['mapa-derecha-1977-2023', 'psoe-1982-mas-del-60', 'ucd-ciudadanos-hundimiento', 'psa-andalucistas-1979',
                                'avila-suarez-cds', 'municipios-izquierda-1977-derecha-2023', 'pueblos-menos-votantes-que-en-1977',
                                'censo-electoral-desde-1977', 'nunca-gano-el-psoe', 'nunca-gano-la-derecha', 'municipios-fieles',
                                'plasencia-acierta-siempre', 'mont-roig-municipio-cambiante', 'trebujena-pce-sumar', 'voto-en-blanco',
                                'izquierda-del-psoe-secciones', 'beiras-nacionalismo-gallego', 'psoe-andalucia-generales-autonomicas',
                                'psoe-madrid-municipales-generales', 'europeas-solo-con-municipales', 'euskadi-empate-a-tres',
                                'republica-mapa-1936-hoy', 'girona-1936-participacio', 'lorca-fuente-vaqueros-viznar-1936', 'pueblos-guerra-civil-voto-1936',
                                'mujeres-1933-frente-popular-1936', 'fieles-1936-izquierda-derecha',
                                'abstencion-anarquista-cnt-1933-1936', 'pueblos-bajo-el-agua-1936', 'pueblos-que-ya-no-existen-1936',
                                'asturias-1934-1936-revolucion-urnas', 'cataluna-lliga-front-esquerres-1933-1936', 'pueblos-colonizacion-franquismo-voto', 'asi-queda-el-mapa-29n'],
        datos=[('elecciones/resultados-elecciones-por-municipio/', 'Resultados de las elecciones por municipio desde 1977'),
               ('elecciones/', 'Elecciones por comunidad y provincia, con las 16 generales desde 1977')],
        atlas=[('atlas/el-municipio-que-cambio/', 'Atlas: el municipio que cambió')]),
    'vivienda': dict(
        nombre='Vivienda y voto',
        titulo='Vivienda y voto: alquiler, pisos turísticos y casas vacías en el mapa electoral',
        intro='Cómo votan los barrios de inquilinos y los de propietarios, qué pasa con el censo donde crecen los pisos turísticos '
              'y dónde hay más casas vacías que vecinos.',
        piezas=['maricarmen-alquiler-y-voto', 'alquiler-ciudad-a-ciudad', 'pisos-turisticos-y-votantes', 'psoe-barrios-de-alquiler',
                'precio-del-alquiler-y-voto', 'acampada-sol-distrito-centro', 'casas-vacias-segundas-residencias',
                'vivienda-preocupa-voto-sumar-29n', 'desahucios-ocupaciones-cgpj-29n', 'vivienda-inmigracion-economia-cis', 'barrios-rentistas-pp-psoe-29n', 'sanchez-revuelta-broncano-voto-joven-29n'],
        datos=[('elecciones/voto-y-renta-por-barrios/', 'Voto y renta por barrios en toda España')],
        atlas=[]),
    'sanidad-y-derechos': dict(
        nombre='Aborto, eutanasia y sanidad',
        titulo='Aborto, eutanasia y sanidad pública: el mapa de los derechos comunidad a comunidad',
        intro='Dónde se aborta en un hospital público y dónde en una clínica privada, dónde se pide la eutanasia '
              'y cómo encaja cada mapa con el voto.',
        piezas=['feijoo-aborto-eutanasia-sanidad-publica-29n'],
        datos=[],
        atlas=[]),
    'inmigracion': dict(
        nombre='Inmigración y voto',
        titulo='Inmigración y voto: población nacida fuera, preocupación y voto a Vox',
        intro='Dónde vive la población nacida fuera de España, cómo votan esos barrios y qué relación hay entre la preocupación '
              'por la inmigración que mide el CIS y el voto a cada partido.',
        piezas=['vox-poblacion-nacida-fuera', 'inmigracion-preocupa-voto-vox-29n', 'trump-espana-invadida-inmigracion-29n',
                'termometro-temas-inmigracion-29n', 'vivienda-inmigracion-economia-cis', 'vox-cinco-barrios-el-ejido-ceuta',
                'ley-nietos-donde-estan-29n', 'sanchez-revuelta-broncano-voto-joven-29n'],
        datos=[('elecciones/mapa-electoral-seccion-censal/', 'Mapa electoral de España por sección censal')],
        atlas=[]),
    'barrio-a-barrio': dict(
        nombre='Barrio a barrio',
        titulo='Elecciones barrio a barrio: el voto de cada sección censal en las grandes ciudades',
        intro='Las grandes ciudades contadas sección a sección: dónde gana cada partido, qué calles parten el voto en dos '
              'y los barrios donde un partido saca sus mejores resultados.',
        piezas=TEMA_SECCION + ['calle-que-parte-madrid', 'girona-barri-a-barri-29n', 'psoe-cinco-barrios-ceuta', 'cc-cinco-barrios-la-orotava',
                               'vox-cinco-barrios-el-ejido-ceuta', 'ciudadanos-democracia21-29n', 'albiol-badalona-pp-29n', 'asi-queda-el-mapa-29n'],
        datos=[('elecciones/mapa-electoral-seccion-censal/', 'Mapa electoral de España por sección censal'),
               ('', 'Mapa de resultados calle a calle')],
        atlas=[('atlas/ciudad-y-entorno/', 'Atlas: la ciudad y su entorno')]),
    'pueblos': dict(
        nombre='Pueblos y municipios',
        titulo='Pueblos y municipios: los que siempre votan igual, los que cambian y los bastiones de cada partido',
        intro='Los municipios que han votado lo mismo desde 1977, los que aciertan siempre el ganador, los que se vacían de electores '
              'y los pueblos donde cada partido saca sus mejores resultados.',
        piezas=TEMA_MUNICIPIOS + ['bildu-cinco-pueblos-lizartza', 'bng-cinco-pueblos-allariz', 'erc-cinco-pueblos-blancafort-flix',
                                  'junts-cinco-pueblos-amer', 'pnv-cinco-pueblos-bermeo', 'pp-cinco-pueblos-galicia', 'sumar-cinco-pueblos-marinaleda',
                                  'baltar-censo-y-participacion', 'europeas-arona', 'casas-vacias-segundas-residencias', 'oficios-y-voto-municipios-29n',
                                  'municipios-izquierda-1977-derecha-2023', 'pueblos-unanimes-empates-29n', 'ganar-por-un-voto-29n'],
        datos=[('elecciones/resultados-elecciones-por-municipio/', 'Resultados de las elecciones por municipio desde 1977'),
               ('municipio/', 'Elecciones en cada municipio de más de 1.000 habitantes')],
        atlas=[('atlas/excepciones/', 'Atlas: las excepciones'), ('atlas/contra-su-provincia/', 'Atlas: contra su provincia'),
               ('atlas/gemelos/', 'Atlas: municipios gemelos')]),
    'sistema-electoral': dict(
        nombre='Escaños y sistema electoral',
        titulo='Escaños y sistema electoral: el precio de un diputado, los restos y las coaliciones',
        intro='Cómo se convierten los votos en escaños: los diputados que se decidieron por unos cientos de votos, '
              'lo que cuesta un escaño en cada provincia, el Senado y lo que habrían sacado las coaliciones.',
        piezas=['escanos-en-el-filo-29n', 'cinco-semanas-29n-la-semana-en-el-mapa', 'precio-del-escano-29n', 'ultimo-escano-29n', 'votos-sin-escano-29n', 'girona-esco-285-vots-29n',
                'senado-29n', 'senado-psoe-frente-amplio-29n', 'vox-pp-senado-pacto-29n', 'izquierda-dividida-29n', 'pactos-izquierda-mapa-final-29n',
                'mapa-coaliciones-izquierda-29n', 'rufian-fracaso-lista-unitaria-29n', 'rufian-erc-comuns', 'canarias-unidad-pueblo-canario-29n',
                'frente-amplio-podemos-madrid-escanos-29n', 'ministros-listas-29n', 'teruel-cha-izquierda-escano-29n', 'ivan-redondo-12-millones-derecha-29n',
                'coaliciones-quien-va-con-quien-29n', 'provincias-en-el-filo-29n', 'asi-queda-el-mapa-29n'],
        datos=[('elecciones/como-se-vota/', 'Cómo se vota: el precio de un escaño por provincia'),
               ('elecciones/elecciones-29n-2026/', 'Elecciones generales del 29N de 2026: diputados por provincia')],
        atlas=[('atlas/bisagras/', 'Atlas: las bisagras')]),
}
SLUG_TEMA = {s: t for t, d in TEMAS.items() for s in d['piezas']}


def temas_de(slug):
    return [t for t, d in TEMAS.items() if slug in d['piezas']]


def slug(t):
    t = unicodedata.normalize('NFKD', t.lower()).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')


def ruta_municipio(p, nombre):
    """Ruta desde la raíz del sitio de la página de un municipio: municipio/<provincia>/<municipio>/."""
    return f'municipio/{PROV_SLUG[p]}/{slug(nombre)}/'


def ruta_municipio_antigua(p, nombre):
    """Dónde estuvo la página de cada municipio hasta octubre de 2026 (ahí queda una redirección)."""
    return f'{ruta_provincia(p)}{slug(nombre)}/'


def es_29n(slug):
    return '29n' in slug.split('-') or slug in TEMA_29N


def ruta_provincia(p):
    """Ruta desde la raíz del sitio de la página de una provincia (o de su comunidad, si es uniprovincial)."""
    c = PROV_CCAA[p]
    return f'elecciones/{c}/{PROV_SLUG[p]}/' if len(CCAA[c][2]) > 1 else f'elecciones/{c}/'


def en_provincia(p):
    """«en …» de la página de una provincia: el de su comunidad si es uniprovincial («en la Comunidad de Madrid», no «en Madrid», que es la ciudad)."""
    c = PROV_CCAA[p]
    return CCAA[c][1] if len(CCAA[c][2]) == 1 else f'en {PROV_NOMBRE[p]}'


def enlaces_actualidad(slug, raiz):
    """Enlaces de una pieza de Actualidad a las páginas de su territorio y de su tema: [(href, texto)]."""
    out = []
    if slug.endswith('-historia-electoral') and slug[:-len('-historia-electoral')] in CCAA:
        c = slug[:-len('-historia-electoral')]
        out.append((f'{raiz}elecciones/{c}/', f'elecciones en {CCAA[c][0]} por provincia y por barrios'))
    ps = ACTUALIDAD_LUGAR.get(slug, [])
    ccaa = {PROV_CCAA[p] for p in ps}
    if len(ps) > 2 and len(ccaa) == 1:   # toda una comunidad: su página, no la de cada provincia
        c = ccaa.pop()
        out.append((f'{raiz}elecciones/{c}/', f'elecciones en {CCAA[c][0]}'))
    else:
        out += [(f'{raiz}{ruta_provincia(p)}', f'elecciones {en_provincia(p)}') for p in ps]
    if slug in ACTUALIDAD_MUNICIPIO:   # pieza de una ciudad: su página y el mapa centrado en ella
        cod, nombre = ACTUALIDAD_MUNICIPIO[slug]
        if cod in CIUDADES:
            out.append((f'{raiz}{CIUDADES[cod]}', f'elecciones en {nombre} barrio a barrio desde 1977'))
        out.append((f'{raiz}?m={cod}', f'{nombre} calle a calle en el mapa electoral'))
    if es_29n(slug):
        out.append((f'{raiz}elecciones/elecciones-29n-2026/', 'elecciones generales del 29N de 2026: fecha y escaños por provincia'))
    if slug in TEMA_PARTICIPACION:
        out.append((f'{raiz}elecciones/participacion-electoral-por-barrio/', 'participación electoral por barrio en toda España'))
    if slug in TEMA_MUNICIPIOS:
        out.append((f'{raiz}elecciones/resultados-elecciones-por-municipio/', 'resultados de las elecciones por municipio desde 1977'))
    if slug in TEMA_RENTA:
        out.append((f'{raiz}elecciones/voto-y-renta-por-barrios/', 'voto y renta por barrios en toda España'))
    if slug in TEMA_SECCION:
        out.append((f'{raiz}elecciones/mapa-electoral-seccion-censal/', 'mapa electoral de España por sección censal'))
    out += [(f'{raiz}temas/{t}/', f'más piezas sobre {TEMAS[t]["nombre"].lower()}') for t in temas_de(slug)]
    return out


# Municipios con página propia (capitales y más de 1.000 habitantes): código INE → ruta, y código → nombre.
# Los escribe src/territorios.py.
_F = pathlib.Path(__file__).with_name('ciudades.json')
CIUDADES = json.loads(_F.read_text(encoding='utf-8')) if _F.exists() else {}
_N = pathlib.Path(__file__).with_name('ciudades_nombres.json')
NOMBRES = json.loads(_N.read_text(encoding='utf-8')) if _N.exists() else {}

# ---------- municipios citados en una pieza ----------
# Nombres que en una pieza casi nunca son el municipio: palabras corrientes, apellidos, partidos.
NO_MUNICIPIO = {'Mayor', 'Sumar', 'Valle', 'Real', 'Casas', 'Moral', 'Mora', 'Torres', 'Castillo', 'Puente', 'Campo', 'Vera',
                'Montero', 'Sanz', 'Sant', 'Alcalá', 'Villa', 'Navas', 'Herrera', 'Pinto', 'Toro', 'Cabra',
                'Vox', 'Salas', 'Pozo', 'Prado', 'Cuevas', 'Ribera', 'Montes', 'Arenas', 'Vega', 'Guardia', 'Calzada', 'Nava',
                'Gata', 'Muro', 'Puig', 'Roda', 'Ares',
                # comprobados en las piezas publicadas: personas, barrios, calles, medios, fuentes o palabras con el nombre de un municipio
                'Voto', 'Manuel', 'María', 'Cortes', 'La Unión', 'Rioja', 'Trujillo', 'Cañada', 'Dolores', 'Segura', 'Serra', 'Consell', 'Fraga',
                'Lerma', 'Ibarra', 'Rueda', 'Valdés', 'Cifuentes', 'Simancas', 'Noblejas', 'Arcos', 'San Isidro', 'Almenara', 'Águilas', 'Los Silos',
                'Valmojado', 'Palmera', 'La Alberca', 'Guadalupe', 'Los Barrios', 'Quinto', 'Selva', 'Santa Eugènia', 'Sant Jordi', 'San Jorge',
                'Borja', 'Montilla', 'Pantoja', 'Marín', 'Padrón', 'Onda', 'Ceutí', 'Torreblanca', 'Almagro', 'Cañaveral', 'Moraleja', 'Comillas',
                'Humilladero', 'Nalda', 'Los Corrales'}
# Municipios mal detectados en una pieza concreta (código INE): «Álvaro Bilbao» o «Bilbao Ubillos» no son la ciudad
EXCLUIR_PIEZA = {'palencia-psoe-lista-29n': {'48020'}, 'castilla-y-leon-historia-electoral': {'48020'},
                 'lorca-fuente-vaqueros-viznar-1936': {'30024', '27012'}, 'pueblos-guerra-civil-voto-1936': {'30024', '48020'}, 'mujeres-1933-frente-popular-1936': {'17155'}, 'republica-mapa-1936-hoy': {'17155'},
                 'abstencion-anarquista-cnt-1933-1936': {'45071'}, 'asturias-1934-1936-revolucion-urnas': {'45071'},
                 'pueblos-bajo-el-agua-1936': {'23055', '48027'}, 'pueblos-colonizacion-franquismo-voto': {'23028', '50008'}}
# Comunidades y provincias con el mismo nombre que su capital: solo cuentan como municipio con «ciudad de» delante
# o si la pieza es de esa ciudad (ACTUALIDAD_MUNICIPIO). Así «la Comunidad de Madrid» o «la provincia de Sevilla» no enlazan la ciudad.
AMBIGUOS = {slug(x) for n in PROV_NOMBRE.values() for x in n.split('/')} | {'valencia', 'castellon', 'alicante'}
# Palabras con mayúscula que pueden ir delante de un municipio («En Arona», «Y Getxo»); cualquier otra delante es casi siempre
# un nombre de pila o parte de otro nombre propio («José Montilla», «Gran Bilbao»)
ANTES_OK = {'En', 'Y', 'E', 'A', 'De', 'Del', 'Desde', 'Entre', 'Como', 'Con', 'Para', 'Por', 'Sin', 'Hasta', 'Tras', 'Fuera', 'Al', 'Le', 'Les',
            'Los', 'Las', 'Ni', 'O', 'I', 'Als', 'Dels', 'Sobre', 'Frente', 'Pero', 'Solo', 'Incluso', 'Allí', 'Aquí', 'Ya',
            'Dato', 'Patrón', 'Hipótesis', 'Contexto', 'Dada', 'Patró', 'Hipòtesi', 'Context'}   # etiquetas de párrafo
_NOMBRE_PROPIO = re.compile(r"[A-ZÁÉÍÓÚÑÀÈÒÇÜ][\w'’-]*")


def _variantes(nombre):
    out = set()
    for parte in nombre.split('/'):
        parte = parte.strip()
        out.add(parte)
        m = re.match(r"(El|La|Els|Les|Los|Las|Es|Sa|Ses|O|A|Os|As) (.+)|(L')(.+)", parte)
        if m:   # «L'Hospitalet» también como «l'Hospitalet»; «El Prat», como «el Prat»
            out.add(parte[0].lower() + parte[1:])
    return {v for v in out if len(v) >= 4 and v[0].upper() + v[1:] not in NO_MUNICIPIO}


def _patron():
    vistos = {}
    for c, (n, p) in NOMBRES.items():
        for v in _variantes(n):
            vistos.setdefault(v, set()).add(c)
    unicos = {v: cs.pop() for v, cs in vistos.items() if len(cs) == 1}   # nombres repetidos en varias provincias: no se enlazan
    if not unicos:
        return None, {}
    alt = '|'.join(re.escape(v) for v in sorted(unicos, key=len, reverse=True))
    return re.compile(r"(?<![\w'’-])(" + alt + r")(?![\w'’-])"), unicos


_PATRON, _UNICOS = _patron()


def texto_visible(html):
    """Texto de una pieza sin scripts, estilos, ficha de método, fuentes ni pie."""
    for etq in ('script', 'style', 'nav', 'footer'):
        html = re.sub(rf'<{etq}\b.*?</{etq}>', ' ', html, flags=re.S)
    html = re.sub(r'<(dl|div) class="(ficha|foot)".*?</\1>', ' ', html, flags=re.S)
    html = re.sub(r'<[^>]+>', ' ', html)
    return ' '.join(html.replace('&nbsp;', ' ').replace('&#x27;', "'").replace('&#39;', "'").split())


def municipios_citados(html, slug_pieza=None):
    """Municipios con página propia que nombra una pieza: [(código, veces)], los más citados primero."""
    if not _PATRON:
        return []
    texto = texto_visible(html)
    propio = ACTUALIDAD_MUNICIPIO.get(slug_pieza, (None,))[0]
    cuenta, primero = {}, {}
    for m in _PATRON.finditer(texto):
        c = _UNICOS[m.group(1)]
        if c in EXCLUIR_PIEZA.get(slug_pieza, ()):
            continue
        art, _, resto = m.group(1).partition(' ')
        if art in ('la', 'el', 'les', 'els', 'los', 'las', 'lo') and resto in _UNICOS:
            continue   # «la Granada nazarí» es Granada, no La Granada (Barcelona)
        antes = texto[:m.start()].split()[-1:] or ['']
        despues = texto[m.end():].split()[:1] or ['']
        if c != propio and ((_NOMBRE_PROPIO.fullmatch(antes[0]) and antes[0] not in ANTES_OK) or antes[0] in ('La', 'la', 'El', 'el')
                            or (_NOMBRE_PROPIO.fullmatch(despues[0]) and despues[0] not in ('Y', 'I', 'O', 'E'))):
            continue   # «José Montilla», «Gran Bilbao», «la Palma», «Onda Vasca»
        if propio and c[:2] == propio[:2] and c != propio:
            continue   # en la pieza de una ciudad, los nombres de su provincia suelen ser barrios («La Alberca», «Torreblanca»)
        if slug(m.group(1)) in AMBIGUOS and c != propio:
            antes = texto[max(0, m.start() - 12):m.start()].lower()
            if not re.search(r'(ciudad de|capital,?|municipio de) $', antes):
                continue
        cuenta[c] = cuenta.get(c, 0) + 1
        primero.setdefault(c, m.start())
    if propio and propio in NOMBRES:
        cuenta[propio] = cuenta.get(propio, 0) + 100   # la ciudad de la pieza, siempre la primera
        primero.setdefault(propio, -1)
    return sorted(cuenta.items(), key=lambda x: (-x[1], primero[x[0]]))


def bloque_municipios_pieza(html, slug_pieza, raiz, maximo=12):
    """«Ver datos de este municipio en el mapa»: enlaces a la página y al mapa de cada municipio que cita la pieza."""
    cs = [c for c, _ in municipios_citados(html, slug_pieza)][:maximo]
    if not cs:
        return ''
    uno = len(cs) == 1
    li = ''.join(f'<li data-mun="{c}"><a href="{raiz}{CIUDADES[c]}">{NOMBRES[c][0]}</a> <span class="prov">({PROV_NOMBRE[NOMBRES[c][1]]})</span>'
                 f' · <a href="{raiz}?m={c}">mapa</a></li>' for c in cs)
    return (f'<aside class="municipios-pieza"><h2>{"Ver datos de este municipio en el mapa" if uno else "Ver datos de estos municipios en el mapa"}</h2>'
            f'<p>{"El municipio que aparece" if uno else "Los municipios que aparecen"} en esta pieza: resultados por sección censal, '
            f'voto por renta y las generales desde 1977 en su página, o calle a calle en el mapa.</p><ul>{li}</ul></aside>')
