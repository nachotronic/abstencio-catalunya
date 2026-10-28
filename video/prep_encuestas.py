"""Guion del Short «Encuestas, hoy» (shorts/encuestas-hoy.json) con los mismos cálculos que /encuestas/."""
import json, os, sys
from datetime import date
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
import importlib.util
# se carga con otro nombre: construir.py importa a su vez el construir de actualidad/src
spec = importlib.util.spec_from_file_location('encuestas_construir', os.path.join(RAIZ, 'encuestas', 'src', 'construir.py'))
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)

MES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
COL = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'PODEMOS': 'Podemos'}
pc = lambda v: f'{v:.1f}'.replace('.', ',') + ' %'

encs = K.carga()
hoy = date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else date.today()
med = K.medianas(encs, hoy)[-1]
_, _, _, _, ultimas, con_esc, mayoria = K.textos(encs, hoy)
lider = lambda e: max(e['voto'], key=e['voto'].get)
n, n_pp = len(ultimas), sum(1 for e in ultimas if lider(e) == 'PP')
otros = [{'PSOE': 'un sondeo del propio PSOE', 'CIS': 'el CIS'}.get(e['casa'], e['casa']) for e in ultimas if lider(e) != 'PP']
ult = max((e for e in encs if e.get('publicado') and not e['reest']), key=lambda e: (e['publicado'], e['fin']))
dias = (date(2026, 11, 29) - hoy).days
pv = sorted(([e['casa'], *K.suma_pv(e)] for e in con_esc), key=lambda r: -(r[1] + r[2]))
fp = date.fromisoformat(ult['publicado'])
dia_n = max(e['publicado'] for e in encs if e.get('publicado') and e['publicado'] <= hoy.isoformat())
nuevas = [e for e in encs if e.get('publicado') == dia_n and not e['reest'] and 'VOX' in e['voto']]
dn = date.fromisoformat(dia_n)
cuando = 'publicadas hoy' if dn == hoy else 'publicadas ayer' if (hoy - dn).days == 1 else f'del {dn.day} de {MES[dn.month - 1]}'

escenas = [
    {'tipo': 'hook', 'dur': 2.8, 'lineas': [f'A {dias} días del 29N,', '¿qué dicen', [['las encuestas?', 'vote']]]},
    {'tipo': 'numeros', 'dur': 3.8, 'titulo': [f'El PP gana en', f'{n_pp} de {n} encuestas'], 'items': [
        [str(n_pp), 'PP', [f'de las {n} encuestadoras del último', 'mes dan ganador al PP']],
        [str(n - n_pp), 'PSOE', [('da' if n - n_pp == 1 else 'dan') + ' ganador al PSOE:', ' y '.join(otros)]]]},
    {'tipo': 'barrasH', 'dur': 4.2, 'titulo': ['La mediana', 'de las encuestas'], 'sub': '% de voto estimado, últimas 3 semanas', 'max': 36,
     'filas': [[COL[k], COL[k], med[k]] for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS') if k in med]},
    {'tipo': 'horquillas', 'dur': 5.4, 'titulo': ['PP + Vox, escaños', 'en cada encuesta'], 'sub': 'Horquilla de cada encuestadora', 'eje': [150, 220],
     'linea': 176, 'lineaTxt': '176: mayoría', 'color': 'PP', 'filas': [[c[:18], a, b] for c, a, b in pv],
     'nota': [f'{mayoria} de {len(con_esc)} les dan mayoría absoluta']},
] + ([{'tipo': 'tabla', 'dur': 4.6, 'titulo': [f'{len(nuevas)} encuestas', cuando], 'sub': '% de voto estimado',
        'cols': [['PP', 'PP'], ['PSOE', 'PSOE'], ['Vox', 'Vox']],
        'filas': [[e['casa'], e['medio'], e['voto']['PP'], e['voto']['PSOE'], e['voto']['VOX']] for e in nuevas]}] if len(nuevas) > 1 else [
    {'tipo': 'numeros', 'dur': 4.2, 'titulo': ['La última:', ult['casa']], 'sub': f'{ult["medio"] + ", " if ult["medio"] else ""}publicada el {fp.day} de {MES[fp.month - 1]}',
     'items': [[pc(ult['voto'][k]), COL[k], [COL[k]]] for k in ('PP', 'PSOE', 'VOX') if k in ult['voto']]}]) + [
    {'tipo': 'cierre', 'dur': 3.2, 'lineas': ['Todas las', 'encuestas,', 'cada día'], 'ruta': '/encuestas/'},
]
# las encuestas del día van justo después de la pregunta inicial
escenas.insert(1, escenas.pop(next(i for i, e in enumerate(escenas) if e['tipo'] in ('tabla', 'numeros') and e['titulo'][0] != 'El PP gana en')))
guion = {'plantilla': 'guia', 'kicker': f'ENCUESTAS DEL 29N · {hoy.day} DE {MES[hoy.month - 1].upper()}',
         'colores': {'PP': '#1d84ce', 'PSOE': '#e30613', 'Vox': '#5ac035', 'Sumar': '#a2275f', 'Podemos': '#5a3c8f'},
         'escenas': escenas,
         'fuente': ['Encuestas publicadas, vía Electográfica y Wikipedia.', 'La mediana resume encuestas: no es una previsión.']}
json.dump(guion, open(os.path.join(RAIZ, 'video', 'shorts', 'encuestas-hoy.json'), 'w'), ensure_ascii=False, indent=1)
print(n, n_pp, otros, med, ult['casa'], ult['publicado'], pv)
