"""Piezas comunes a los reportajes de «Las comunidades en las urnas»."""
import urllib.parse

INTERIOR_HIST = ('https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/',
                 'Ministerio del Interior (Infoelectoral), resultados de las elecciones generales desde 1977 por municipio y por mesa; '
                 'de 1986 a 2003, vía pollspaindata. Sin voto exterior (CERA)')
POLLSPAIN = ('https://github.com/dadosdelaplace/pollspaindata',
             'pollspaindata (datos de Interior por mesa): votos de cada candidatura en las generales de 2015, 2019 y 2023, para el ganador lista a lista')
FUENTES_COMUNES = [INTERIOR_HIST, POLLSPAIN]
PIE = ('Datos: autonómicas, Historia Electoral (historiaelectoral.com), con los resultados oficiales de cada parlamento; generales, Ministerio del Interior '
       '(Infoelectoral), por municipio y por mesa desde 1977, sin voto exterior. Borrador: pendiente de revisión antes de publicar.')
LIMITES = ('Las generales se cuentan sin voto exterior (CERA), así que la participación sale algo por encima de la oficial. Hasta 2000 el ganador de cada '
           'provincia y municipio es la candidatura más votada de todas; desde 2004, la familia de partidos más votada (los regionalistas van en «Otras listas»). '
           'La familia PCE / IU / Podemos / Sumar suma listas que en 2015 y 2019 se presentaron por separado en algunas comunidades (Podemos, IU, Compromís, Más País): en el gráfico de voto su línea es la suma, pero el ganador de cada provincia, ciudad y municipio de esos años se ha calculado lista a lista con los datos por mesa de Interior (vía pollspaindata). '
           'En 1982 faltan en el fichero de Interior unos 139 municipios de toda España. Los escaños autonómicos son los de Historia Electoral, '
           'comprobados con Wikipedia en las elecciones que se citan en el texto.')


def he_fuente(pagina, nombre):
    return (f'https://www.historiaelectoral.com/{pagina}.html', f'Historia Electoral, elecciones autonómicas en {nombre} (escaños, votos e investiduras)')


def wiki(titulo):
    return 'https://es.wikipedia.org/wiki/' + urllib.parse.quote(titulo.replace(' ', '_'))
