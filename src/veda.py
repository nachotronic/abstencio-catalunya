"""Veda de encuestas del 29N (art. 69.7 de la LOREG): durante los cinco días anteriores a la votación no se pueden
publicar ni difundir sondeos. Para el domingo 29-11-2026, del martes 24 a las 0:00 en adelante.

Nacho, 18-11-2026: quitar los sondeos de la portada cuando lo exija la ley y dejar /encuestas/ congelada con los
últimos datos, sin borrar ni cambiar title, H1, description, canonical ni URL de ninguna página.

- DESDE: 23:30 del lunes 23, media hora antes del límite legal, porque GitHub retrasa las tareas programadas.
- HASTA: 21:00 del domingo 29, cuando cierran los colegios de Canarias (20:00 hora canaria). Criterio prudente: la
  ley habla de los cinco días anteriores, pero ese día tampoco se publica nada hasta que no se haya votado en toda España.
"""
import datetime, re
from zoneinfo import ZoneInfo

MADRID = ZoneInfo('Europe/Madrid')
DESDE = datetime.datetime(2026, 11, 23, 23, 30, tzinfo=MADRID)
HASTA = datetime.datetime(2026, 11, 29, 21, 0, tzinfo=MADRID)

# Piezas de Actualidad con cifras de encuestas: fuera del carrusel de la portada durante la veda (siguen publicadas en
# su URL y en /actualidad/). Por el slug; si alguna con encuestas no lo lleva, se añade a mano en PIEZAS_ENCUESTAS.
PATRON_ENCUESTAS = re.compile(r'encuesta|sondeo|^cis-')
PIEZAS_ENCUESTAS = set()
# Piezas que hablan de encuestas pero no dan cifras de ninguna: siguen en el carrusel durante la veda (Nacho, 23-11-2026: «Sí, primera»)
NO_SON_ENCUESTAS = {'encuestas-andorra-29n'}


def en_veda(ahora=None):
    ahora = ahora or datetime.datetime.now(MADRID)
    return DESDE <= ahora < HASTA


def es_pieza_de_encuestas(slug, titulo=''):
    """Por el slug, por la lista a mano o porque el titular habla de encuestas o sondeos."""
    if slug in NO_SON_ENCUESTAS:
        return False
    return bool(PATRON_ENCUESTAS.search(slug)) or slug in PIEZAS_ENCUESTAS or bool(re.search(r'encuesta|sondeo', titulo, re.I))
