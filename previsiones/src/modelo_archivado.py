"""El modelo de /encuestas/ tal como estaba un día concreto.

El modelo se recalcula cuando entra una encuesta nueva y previsiones/datos/publico/escenario-base.json se
sobrescribe. Para que una pieza que cita «el modelo del 5 de noviembre» se pueda comprobar después, motor.py
guarda una copia por día en previsiones/datos/publico/historico/AAAA-MM-DD.json (la última de ese día).
Los días sin encuesta nueva no hay copia: vale la última anterior, que es la que se veía en la web ese día.

    from modelo_archivado import modelo
    m = modelo('2026-11-05')                 # {'meta': {...}, 'escenario': {...}}
    psoe = next(l for l in m['escenario']['provincias']['46']['listas'] if l['lista'] == 'PSOE')
    psoe['escanos']                          # [p10, mediana, p90] -> [4, 5, 6]
"""
import json, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HIST = os.path.join(RAIZ, 'previsiones', 'datos', 'publico', 'historico')


def fechas():
    return sorted(f[:-5] for f in os.listdir(HIST) if re.fullmatch(r'\d{4}-\d{2}-\d{2}\.json', f)) if os.path.isdir(HIST) else []


def fecha_vigente(fecha):
    """La copia que estaba publicada el día `fecha` (AAAA-MM-DD): la de ese día o la última anterior."""
    previas = [f for f in fechas() if f <= fecha]
    return previas[-1] if previas else None


def modelo(fecha):
    f = fecha_vigente(fecha)
    if not f:
        raise LookupError(f'no hay modelo archivado del {fecha} ni de antes (el primero es del {(fechas() or ["—"])[0]})')
    return json.load(open(os.path.join(HIST, f + '.json'), encoding='utf-8'))


def provincia(fecha, cod, lista):
    """La lista `lista` en la provincia `cod` («46») del modelo vigente el día `fecha`."""
    return next(l for l in modelo(fecha)['escenario']['provincias'][cod]['listas'] if l['lista'] == lista)
