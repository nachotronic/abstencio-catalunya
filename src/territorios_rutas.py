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
}
# Piezas de cada página temática
TEMA_RENTA = ['maricarmen-alquiler-y-voto', 'alquiler-ciudad-a-ciudad', 'psoe-barrios-de-alquiler', 'precio-del-alquiler-y-voto',
              'huelga-11n-paro-participacion', 'vox-poblacion-nacida-fuera', 'pisos-turisticos-y-votantes']
TEMA_SECCION = ['izquierda-del-psoe-secciones', 'colau-barcelona-comuns', 'rufian-erc-comuns', 'mapa-derecha-1977-2023']


def ruta_provincia(p):
    """Ruta desde la raíz del sitio de la página de una provincia (o de su comunidad, si es uniprovincial)."""
    c = PROV_CCAA[p]
    return f'elecciones/{c}/{PROV_SLUG[p]}/' if len(CCAA[c][2]) > 1 else f'elecciones/{c}/'


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
        out += [(f'{raiz}{ruta_provincia(p)}', f'elecciones en {PROV_NOMBRE[p]}') for p in ps]
    if slug in TEMA_RENTA:
        out.append((f'{raiz}elecciones/voto-y-renta-por-barrios/', 'voto y renta por barrios en toda España'))
    if slug in TEMA_SECCION:
        out.append((f'{raiz}elecciones/mapa-electoral-seccion-censal/', 'mapa electoral de España por sección censal'))
    return out


# Ciudades con página propia (capitales y más de 50.000 habitantes): código INE → ruta. Lo escribe src/territorios.py.
_F = pathlib.Path(__file__).with_name('ciudades.json')
CIUDADES = json.loads(_F.read_text(encoding='utf-8')) if _F.exists() else {}
