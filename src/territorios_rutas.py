"""Rutas de las páginas por territorio de /elecciones/ (las genera src/territorios.py).

Módulo aparte, sin datos, para que otras secciones (el Atlas) puedan enlazar a esas páginas sin cargar nada.
"""
import json, pathlib

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
    'calle-que-parte-el-voto': ('46250', 'València'),
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
    return out


# Municipios con página propia (capitales y más de 1.000 habitantes): código INE → ruta. Lo escribe src/territorios.py.
_F = pathlib.Path(__file__).with_name('ciudades.json')
CIUDADES = json.loads(_F.read_text(encoding='utf-8')) if _F.exists() else {}
