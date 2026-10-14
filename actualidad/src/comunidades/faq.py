"""Preguntas rápidas al final de cada reportaje de «Las comunidades en las urnas»: quién gobierna y desde cuándo.

Responde a las búsquedas que traen lectores a la serie («qué partido gobierna en Madrid», «desde cuándo gobierna el PP
en Castilla y León»). Las respuestas salen de la tabla de presidentes de cada pieza, así que no dicen nada que la pieza
no verifique. construir.py convierte el bloque en FAQPage (schema.org).
"""
import html

INSTITUCION = {
    'andalucia': 'la Junta de Andalucía', 'aragon': 'el Gobierno de Aragón', 'asturias': 'el Principado de Asturias',
    'baleares': 'el Govern de les Illes Balears', 'canarias': 'el Gobierno de Canarias', 'cantabria': 'el Gobierno de Cantabria',
    'castilla-la-mancha': 'la Junta de Comunidades de Castilla-La Mancha', 'castilla-y-leon': 'la Junta de Castilla y León',
    'cataluna': 'la Generalitat de Catalunya', 'comunidad-valenciana': 'la Generalitat Valenciana', 'extremadura': 'la Junta de Extremadura',
    'galicia': 'la Xunta de Galicia', 'madrid': 'la Comunidad de Madrid', 'murcia': 'la Región de Murcia', 'navarra': 'el Gobierno de Navarra',
    'pais-vasco': 'el Gobierno Vasco', 'la-rioja': 'el Gobierno de La Rioja', 'ceuta': 'la Ciudad Autónoma de Ceuta',
    'melilla': 'la Ciudad Autónoma de Melilla'}
# Nombre de la comunidad tal como se busca («qué partido gobierna en Madrid»), cuando no es el de la pieza
LUGAR = {'baleares': 'Baleares', 'comunidad-valenciana': 'la Comunidad Valenciana', 'madrid': 'Madrid', 'murcia': 'Murcia'}
# Partido con artículo, tal como se escribe en la respuesta
CON_ARTICULO = {'PP': 'el PP', 'PSOE': 'el PSOE', 'PSC': 'el PSC', 'PNV': 'el PNV', 'PSN-PSOE': 'el PSN-PSOE', 'CC': 'Coalición Canaria (CC)'}
# Mismo partido a efectos de «sin interrupción»: AP pasó a ser el PP; PSC, PSdeG, PSE y PSN son el PSOE en cada comunidad
FAMILIA = {'AP': 'PP', 'AP / PP': 'PP', 'PSdeG-PSOE': 'PSOE', 'PSN-PSOE': 'PSOE', 'PSE-EE': 'PSOE', 'PSC': 'PSOE'}


def preguntas(cc, lugar, filas):
    """filas: [(desde, hasta, nombre, partido)] de la tabla de presidentes, la última con hasta='hoy'."""
    lugar = LUGAR.get(cc, lugar)
    desde, hasta, nombre, partido = filas[-1]
    if hasta != 'hoy' or partido not in CON_ARTICULO:
        raise ValueError(f'{cc}: la última fila de presidentes no es el gobierno actual con partido conocido: {filas[-1]}')
    fam = lambda p: FAMILIA.get(p, p)
    i = len(filas) - 1
    while i > 0 and fam(filas[i - 1][3]) == fam(partido):
        i -= 1
    inicio = filas[i][0]
    quien, inst = CON_ARTICULO[partido], INSTITUCION[cc]
    Q = lambda s: s[0].upper() + s[1:]
    r1 = f'{Q(quien)}. {nombre} preside {inst} desde {desde}.'
    if inicio != desde:
        r1 += f' {Q(quien)} gobierna sin interrupción desde {inicio}.'
    r2 = f'Sin interrupción desde {inicio}' + (f', con {nombre}.' if inicio == desde else '.')
    if i > 0:
        a, b, n, p = filas[i - 1]
        r2 += f' Antes, {n} ({p}) presidió {inst} ' + (f'de {a} a {b}.' if a != b else f'en {a}.')
    corto = quien.split(' (')[0] if partido != 'CC' else 'Coalición Canaria'
    return [(f'¿Qué partido gobierna en {lugar}?', r1), (f'¿Desde cuándo gobierna {corto} en {lugar}?', r2)]


def bloque(qs):
    return ('<h2 id="preguntas">Preguntas rápidas</h2>\n<div class="faq">'
            + ''.join(f'<h3>{html.escape(q)}</h3><p>{html.escape(r)}</p>' for q, r in qs) + '</div>')
