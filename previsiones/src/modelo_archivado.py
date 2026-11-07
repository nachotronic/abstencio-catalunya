"""El modelo de /encuestas/ tal como estaba publicado en un momento concreto.

El modelo se recalcula cuando entra una encuesta nueva y previsiones/datos/publico/escenario-base.json se
sobrescribe. Para que una pieza que cita «el modelo del 5 de noviembre» se pueda comprobar después, motor.py
guarda cada versión en previsiones/datos/publico/historico/AAAA-MM-DD-HHMM.json, con la hora de Madrid en que
se publicó. Un día puede tener varias versiones (el 6-11 hubo una a las 0.39 y otra a las 15.16). Sin hora vale
la última de ese día; los días sin encuesta nueva no hay copia y vale la última anterior, que es la que se veía.
Las copias anteriores al 7-11-2026 salen del historial de git, con la hora de Madrid de cada commit.

    from modelo_archivado import modelo
    m = modelo('2026-11-06')                 # la de las 15.16: {'meta': {...}, 'escenario': {...}}
    m = modelo('2026-11-06', '10:00')        # la de las 0.39, la que se veía a las 10.00
    psoe = next(l for l in m['escenario']['provincias']['46']['listas'] if l['lista'] == 'PSOE')
    psoe['escanos']                          # [p10, mediana, p90] -> [4, 5, 6]
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HIST = os.path.join(RAIZ, 'previsiones', 'datos', 'publico', 'historico')


def versiones():
    """Nombres AAAA-MM-DD-HHMM de todas las copias, de la más antigua a la más reciente."""
    if not os.path.isdir(HIST):
        return []
    return sorted(f[:-5] for f in os.listdir(HIST) if re.fullmatch(r'\d{4}-\d{2}-\d{2}-\d{4}\.json', f))


def fechas():
    """Días (AAAA-MM-DD) que tienen alguna copia."""
    return sorted({v[:10] for v in versiones()})


def version_vigente(fecha, hora=None):
    """La versión publicada el día `fecha` (AAAA-MM-DD) a la hora `hora` («HH:MM»; sin hora, al final del día):
    la última anterior a ese momento."""
    hasta = f"{fecha}-{(hora or '23:59').replace(':', '').replace('.', '').zfill(4)}"
    previas = [v for v in versiones() if v <= hasta]
    return previas[-1] if previas else None


def fecha_vigente(fecha, hora=None):
    """El día de la copia vigente el día `fecha`: el mismo si ese día hubo modelo nuevo, o uno anterior."""
    v = version_vigente(fecha, hora)
    return v[:10] if v else None


def modelo(fecha, hora=None):
    v = version_vigente(fecha, hora)
    if not v:
        raise LookupError(f'no hay modelo archivado del {fecha} ni de antes (el primero es del {(versiones() or ["—"])[0]})')
    return json.load(open(os.path.join(HIST, v + '.json'), encoding='utf-8'))


def provincia(fecha, cod, lista, hora=None):
    """La lista `lista` en la provincia `cod` («46») del modelo vigente el día `fecha` (y a la hora `hora`)."""
    return next(l for l in modelo(fecha, hora)['escenario']['provincias'][cod]['listas'] if l['lista'] == lista)
