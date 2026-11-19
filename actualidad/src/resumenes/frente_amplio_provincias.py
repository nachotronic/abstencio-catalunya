"""Frente Amplio: las 17 provincias en las que aspira a sacar diputados (Público, 18-11-2026; elDiario.es daba 16 el 9-11, sin Bizkaia),
frente al modelo de escaños de /encuestas/ (pieza del 19-11-2026).

Modelo: previsiones/datos/publico/escenario-base.json, última actualización automática; reparto central de cada provincia con
reparto_provincia() de encuestas/src/construir.py (el mismo que publica /encuestas/<provincia>/) y horquilla del 80 % (P10-P90).
En el modelo la lista se llama «Sumar» (en /encuestas/, «Sumar / Frente Amplio»). 2023: escaños de Sumar por provincia,
actualidad/src/sistema/cifras.json.
Uso, desde la raíz: python3 actualidad/src/resumenes/frente_amplio_provincias.py
"""
import importlib.util
import json

from comun import BASE, RAIZ, esc, figura, n, pieza
from mapa_ccaa import COL, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'frente-amplio-17-provincias-29n'
ELDIARIO = 'https://www.eldiario.es/1_d04a08'
PUBLICO = 'https://www.publico.es/politica/ultima-hora-campana-electoral-29n-directo-2_1149.html'

_spec = importlib.util.spec_from_file_location('enc_construir', RAIZ / 'encuestas/src/construir.py')
enc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(enc)

ESC = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
META = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
C23 = json.load(open(RAIZ / 'actualidad/src/sistema/cifras.json'))['2023_07']['provincias']

# Las 17 de Público (18-11): las 16 de elDiario.es (9-11) más Bizkaia; con el código INE de provincia
OBJ = {'15': 'A Coruña', '03': 'Alicante', '33': 'Asturias', '07': 'Baleares', '08': 'Barcelona', '14': 'Córdoba', '18': 'Granada',
       '35': 'Las Palmas', '28': 'Madrid', '29': 'Málaga', '31': 'Navarra', '36': 'Pontevedra', '38': 'Santa Cruz de Tenerife',
       '41': 'Sevilla', '43': 'Tarragona', '50': 'Zaragoza', '48': 'Bizkaia'}
assert len(OBJ) == 17

F = []
for cod, v in ESC['provincias'].items():
    rc = enc.reparto_provincia(v)
    s = next(l for l in v['listas'] if l['lista'] == 'Sumar')
    F.append(dict(cod=cod, nom=OBJ.get(cod, C23[cod]['nombre']), obj=cod in OBJ, total=v['escanos_total'], voto=s['voto'][1],
                  lo=s['escanos'][0], hi=s['escanos'][2], central=rc['Sumar'], e23=C23[cod]['esc'].get('Sumar', 0)))
O = sorted((f for f in F if f['obj']), key=lambda f: (-f['central'], -f['hi'], -f['voto']))
CON = [f for f in O if f['central'] > 0]
PUERTAS = [f for f in O if f['central'] == 0 and f['hi'] > 0]
FUERA = [f for f in O if f['hi'] == 0]
FUERA23 = [f for f in FUERA if f['e23'] > 0]
assert len(CON) + len(PUERTAS) + len(FUERA) == 17
ESC_CON = sum(f['central'] for f in CON)
E23_OBJ = sum(f['e23'] for f in O)
TOT = sum(f['central'] for f in F)
TOT23 = sum(f['e23'] for f in F)
OTRAS = sorted((f for f in F if not f['obj'] and f['central'] > 0), key=lambda f: -f['central'])
MED_NAC = next(l for l in ESC['listas'] if l['lista'] == 'Sumar')['escanos'][2]
HEMI = ESC['hemiciclo']['congreso']['Sumar']   # el que publica /encuestas/ (media de las simulaciones)
VERSION = META['generado']

y = lambda xs: ', '.join(x for x in xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]
nl = lambda fs: y([f['nom'] for f in fs])

g = figura(f'De las 17 provincias en las que aspira a diputado, el modelo le da escaño en {len(CON)} y lo deja a las puertas en {len(PUERTAS)}',
           'Escaños de Sumar en las elecciones generales de 2023 y del Frente Amplio en el reparto central del modelo de encuestas, en las 17 provincias en las que aspira a sacar diputado',
           grupos([(f['nom'].replace('Santa Cruz de Tenerife', 'S. C. de Tenerife'), [(f['e23'], COL['SUMAR'], .45, f'2023: {f["e23"]}'), (f['central'], COL['SUMAR'], 1, f'Modelo: {f["central"]}')]) for f in O],
                  max(f['e23'] for f in O) * 1.1, 'Escaños del Frente Amplio por provincia: 2023 y modelo', W=400, ml=125, fmt=lambda v: n(v)),
           f'Fuente: Ministerio del Interior (2023) y modelo de <a href="{BASE}encuestas/">mapaelectoral.es/encuestas</a>. Provincias: <a href="{PUBLICO}">Público</a>.',
           [('2023 (Sumar)', f"color-mix(in srgb, {COL['SUMAR']} 45%, transparent)"), ('Modelo, reparto central', COL['SUMAR'])],
           (['Provincia', '2023', 'Modelo', 'Horquilla', 'Voto (%)'],
            [[f['nom'], n(f['e23']), n(f['central']), f'{f["lo"]}–{f["hi"]}', p(f['voto'])] for f in O]))

cuerpo = f'''
<p data-tipo="contexto">El Frente Amplio aspira a sacar diputados en 17 provincias en las elecciones generales del 29N, según publicó <a href="{PUBLICO}">Público</a> el 18 de noviembre: {nl(sorted(O, key=lambda f: f['nom']))}. Son las 16 en las que, según <a href="{ELDIARIO}">elDiario.es</a>, centra su campaña para pelear por el último escaño, más Bizkaia. «En esas provincias, en la mayoría de ellas, el escaño que se va a jugar el Frente Amplio se lo juega con el PP y con Vox», dijo el 9 de noviembre su portavoz de campaña, Pablo Bustinduy, según elDiario.es. En la Comunidad Valenciana y en Canarias se presenta en coalición con Podemos, Compromís y Nueva Canarias, recuerda Público.</p>
<p data-tipo="dato">El <a href="{BASE}encuestas/">modelo de encuestas de mapaelectoral.es</a> le da escaño en <strong>{len(CON)} de esas 17</strong> en su reparto central: {y([f"{f['nom']} ({f['central']})" for f in CON])}, {ESC_CON} diputados en total. En 2023, Sumar sacó {E23_OBJ} en esas mismas 17 provincias.</p>
<p data-tipo="dato">En otras {len(PUERTAS)}, {nl(PUERTAS)}, se queda a las puertas: el reparto central no le da escaño, pero sí la horquilla del 80 % del modelo. En las {len(FUERA)} restantes ({nl(FUERA)}), ni siquiera la horquilla le da diputado, aunque Sumar lo sacó en 2023 en {len(FUERA23)} de ellas.</p>
{g}
<p data-tipo="dato">Fuera de su lista, el modelo le da escaño en {y([f"{f['nom']} ({f['central']})" for f in OTRAS])}. En toda España, <a href="{BASE}encuestas/">el hemiciclo de /encuestas/</a> le da <strong>{HEMI} diputados</strong>, frente a los {TOT23} de Sumar en 2023, con Podemos dentro. El hemiciclo es la media de escaños de todas las simulaciones del modelo, así que cuenta también los escaños que gana solo en parte de ellas, como los de las provincias en las que se queda a las puertas; sumando el reparto central de cada provincia salen {TOT}.</p>
<p data-tipo="contexto">El modelo mezcla encuestas nacionales y resultados anteriores para estimar cada provincia, y en las que reparten pocos escaños un punto arriba o abajo cambia el último diputado. Por eso las horquillas son anchas: son las provincias en las que una campaña puede mover un escaño.</p>
'''

preguntas = [
    ('¿En qué provincias aspira a sacar diputados el Frente Amplio?',
     f'En 17, según Público: {nl(sorted(O, key=lambda f: f["nom"]))}.'),
    ('¿Cuántos diputados le dan las encuestas al Frente Amplio?',
     f'El hemiciclo del modelo de mapaelectoral.es le da {HEMI} en toda España. Sumar, con Podemos dentro, sacó {TOT23} en 2023.'),
]
enlaces = f'<a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a> · {L("provincias-en-el-filo-29n", "Las provincias en el filo")}'
foot = ('Datos: modelo de mapaelectoral.es/encuestas (reparto central y horquilla del 80 %); Ministerio del Interior, resultados de 2023. '
        'Cálculo: actualidad/src/resumenes/frente_amplio_provincias.py.')
DATOS = {'O': O, 'CON': len(CON), 'PUERTAS': len(PUERTAS), 'FUERA': len(FUERA), 'FUERA23': len(FUERA23), 'ESC_CON': ESC_CON,
         'E23_OBJ': E23_OBJ, 'TOT': TOT, 'HEMI': HEMI, 'TOT23': TOT23, 'OTRAS': OTRAS, 'VERSION': VERSION}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Frente Amplio',
      f'Elecciones generales: el modelo de encuestas da escaño al Frente Amplio en {len(CON)} de sus 17 provincias',
      f'En otras {len(PUERTAS)} se queda a las puertas. En toda España, el modelo le da {HEMI} diputados; Sumar sacó {TOT23} en 2023, con Podemos dentro.',
      '19 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(len(CON), [f['nom'] for f in CON], ESC_CON, E23_OBJ, len(PUERTAS), [f['nom'] for f in PUERTAS], len(FUERA), len(FUERA23), TOT, TOT23, [f['nom'] for f in OTRAS], MED_NAC, VERSION)
