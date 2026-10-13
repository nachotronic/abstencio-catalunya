"""Rutas de las páginas por territorio de /elecciones/ (las genera src/territorios.py).

Módulo aparte, sin datos, para que otras secciones (el Atlas) puedan enlazar a esas páginas sin cargar nada.
"""
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


def ruta_provincia(p):
    """Ruta desde la raíz del sitio de la página de una provincia (o de su comunidad, si es uniprovincial)."""
    c = PROV_CCAA[p]
    return f'elecciones/{c}/{PROV_SLUG[p]}/' if len(CCAA[c][2]) > 1 else f'elecciones/{c}/'
