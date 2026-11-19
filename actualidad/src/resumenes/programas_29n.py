"""Programa electoral de PP, PSOE, Vox y Frente Amplio para el 29N: qué propone cada uno (pieza de servicio).

Título fijo desde la publicación: búsqueda «programa electoral» (Google Trends, semana previa del 28A: 33, igual que
«encuestas»). Plan: /mnt/project-files/audiencia/plan-10-dias-2026-11-19.md.
Citas literales de los cuatro programas, con la página del PDF. Las menciones por tema salen de
programas_29n_menciones.py (datos/programas_29n.json).
Uso, desde la raíz: python3 actualidad/src/resumenes/programas_29n.py
"""
import json

from comun import BASE, RAIZ, esc, figura, n, pieza
from mapa_ccaa import COL, grupos, p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'programa-electoral-29n'
M = json.loads((RAIZ / 'actualidad/src/resumenes/datos/programas_29n.json').read_text(encoding='utf-8'))
U = M['fuentes']
NOM = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'Vox', 'FA': 'Frente Amplio'}
DE = {'PP': 'del PP', 'PSOE': 'del PSOE', 'VOX': 'de Vox', 'FA': 'del Frente Amplio'}
COLP = {'PP': COL['PP'], 'PSOE': COL['PSOE'], 'VOX': COL['VOX'], 'FA': COL['SUMAR']}
ORDEN = ['PP', 'PSOE', 'VOX', 'FA']
# Datos de cada documento, comprobados en el PDF: medidas numeradas (o bloques) y título
DOC = {'PP': ('La reconstrucción nacional', '249 medidas'), 'PSOE': ('La fuerza de seguir avanzando', '500 compromisos'),
       'VOX': ('Es sentido común', '115 propuestas'), 'FA': ('programa electoral del Frente Amplio', '18 bloques')}
PAG = M['paginas']
assert PAG == {'PP': 64, 'PSOE': 114, 'VOX': 55, 'FA': 151}, PAG


def cita(k, pag, texto):
    """Cita literal enlazada al PDF, con la página."""
    return f'«{texto}» (<a href="{U[k]}#page={pag}">programa {DE[k]}, página {pag}</a>)'


T = M['tasa']
INM = T['Inmigración']
RAZON_INM = INM['VOX'] / INM['PSOE']
assert 5.5 < RAZON_INM < 6.5  # «seis veces»
TEMAS_G = ['Vivienda', 'Impuestos', 'Inmigración', 'Pensiones', 'Sanidad', 'Igualdad y violencia machista', 'Clima y energía']
MAXT = max(T[t][k] for t in TEMAS_G for k in ORDEN)

g_temas = figura('Vox es el que más habla de inmigración, y el PSOE, de vivienda, igualdad y clima',
                 'Veces que aparece cada tema por cada 10.000 palabras del programa',
                 grupos([(t.replace('Igualdad y violencia machista', 'Igualdad').replace('Clima y energía', 'Clima y energía'),
                          [(T[t][k], COLP[k], 1, NOM[k]) for k in ORDEN]) for t in TEMAS_G], MAXT * 1.1,
                        'Menciones de cada tema por cada 10.000 palabras en los programas del PP, PSOE, Vox y Frente Amplio', W=400, ml=118),
                 'Fuente: programas electorales del 29N de los cuatro partidos. Cálculo de mapaelectoral.es: palabras que empiezan por '
                 '«vivienda», «impuest», «fiscal», «IRPF», «IVA», «migra», «pensi», «sanid», «igualdad», «clima», «energía», «nuclear» y «renovable», entre otras.',
                 [(NOM[k], COLP[k]) for k in ORDEN],
                 (['Tema'] + [NOM[k] for k in ORDEN],
                  [[t] + [p(T[t][k]) for k in ORDEN] for t in TEMAS_G]))

docs = '; '.join(f'el {DE[k]}, «{DOC[k][0]}», {DOC[k][1]} en {PAG[k]} páginas' for k in ORDEN[:3])
cuerpo = f'''
<h2>Los cuatro programas</h2>
<p data-tipo="dato">Los cuatro partidos con más intención de voto en <a href="{BASE}encuestas/">las encuestas de las elecciones generales</a> ya han publicado su programa electoral para el 29N: {docs}, y el del Frente Amplio, {DOC['FA'][1]} en {PAG['FA']} páginas. El del PP está en su web; los del PSOE y Vox, en las copias que publicó <a href="{U['PSOE']}">El Independiente</a>, y el del Frente Amplio, en la de <a href="{U['FA']}">Demócrata</a>. Podemos, que se presenta por separado del Frente Amplio, no ha publicado el suyo.</p>
<p data-tipo="contexto">Aquí está lo que dice cada uno sobre los cuatro temas que más se discuten en esta campaña: vivienda, impuestos, pensiones e inmigración. Son citas literales, con la página del documento: un programa es una promesa, no una ley.</p>

<h2>Vivienda: un millón, 100.000 o 1,5 millones</h2>
<p data-tipo="contexto"><strong>PP.</strong> Su medida 144 se titula «Construiremos un millón de viviendas». Para ello propone {cita('PP', 41, 'Movilizaremos suelo público y privado en colaboración con las Comunidades Autónomas y las entidades locales')} y una nueva Ley del Suelo.</p>
<p data-tipo="contexto"><strong>PSOE.</strong> Su compromiso 42 es {cita('PSOE', 28, 'Constituir un parque público estatal de 100.000 viviendas mediante la construcción y adquisición')}, que se sumarían a las de las comunidades autónomas y los ayuntamientos.</p>
<p data-tipo="contexto"><strong>Vox.</strong> No da una cifra de viviendas. Pide {cita('VOX', 19, 'Prioridad nacional para acceder a una vivienda protegida, social o a una ayuda al alquiler')}, la derogación de la Ley de Vivienda y un {cita('VOX', 20, 'Tipo 0% de IVA para la compra de tu primera vivienda habitual')} si es nueva.</p>
<p data-tipo="contexto"><strong>Frente Amplio.</strong> Promete un parque público con el que {cita('FA', 10, 'se incorporarán 1,5 millones de viviendas públicas en 12 años')}, pagado con el 1 % del PIB cada año, y topar los alquileres {cita('FA', 7, 'vinculándolas al 25 % de los ingresos del hogar')}.</p>

<h2>Impuestos: bajar el IRPF o subirlo a las rentas altas</h2>
<p data-tipo="contexto"><strong>PP.</strong> {cita('PP', 47, 'Quien cobre el salario mínimo no pagará IRPF')}, y además promete deflactar la tarifa del impuesto para que la inflación no suba lo que se paga.</p>
<p data-tipo="contexto"><strong>PSOE.</strong> Sube los impuestos a las rentas del capital más altas: {cita('PSOE', 48, 'llegando progresivamente a un tipo máximo del 35% para rentas del capital superiores a 300.000€')}, sin tocar los dos primeros tramos.</p>
<p data-tipo="contexto"><strong>Vox.</strong> Propone una {cita('VOX', 7, 'Simplificación y bajada del IRPF')}, con un tipo más bajo según el número de hijos, y bajar el IVA y el impuesto de Sociedades. No dice cuánto.</p>
<p data-tipo="contexto"><strong>Frente Amplio.</strong> Plantea un tipo mínimo real del 20 % en Sociedades y un impuesto a los «ultrarricos». En herencias, {cita('FA', 46, 'Limitaremos las herencias de los ultrarricos a un máximo de 10 millones de euros por heredero')}.</p>

<h2>Pensiones: tres de los cuatro las atan al IPC</h2>
<p data-tipo="contexto"><strong>PP.</strong> {cita('PP', 34, 'Aseguraremos que mantengan su poder adquisitivo y suban cada año con el IPC')}.</p>
<p data-tipo="contexto"><strong>PSOE.</strong> Quiere {cita('PSOE', 40, 'Blindar constitucionalmente el sistema público de pensiones y su revalorización conforme al IPC')}.</p>
<p data-tipo="contexto"><strong>Vox.</strong> Le dedica una medida: {cita('VOX', 8, 'Garantizar la sostenibilidad del sistema de pensiones')}, que fía al crecimiento de la economía. No habla del IPC.</p>
<p data-tipo="contexto"><strong>Frente Amplio.</strong> Pide llevar a la Constitución {cita('FA', 57, 'su revalorización automática con arreglo al IPC')}, con una pensión mínima igual al SMI. Además, {cita('FA', 57, 'Devolveremos la edad de jubilación a los 65 años')}.</p>

<h2>Inmigración: de «ni uno más» a regularizar</h2>
<p data-tipo="contexto"><strong>PP.</strong> {cita('PP', 19, 'Fijaremos cupos anuales que determinen cuántos trabajadores pueden venir y para qué sectores')}, y reformar la Ley de Extranjería para prohibir las regularizaciones masivas.</p>
<p data-tipo="contexto"><strong>PSOE.</strong> {cita('PSOE', 92, 'España necesita una migración ordenada, legal y segura, que responda a sus necesidades demográficas y económicas')}. Propone un plan de integración de 500 millones de euros.</p>
<p data-tipo="contexto"><strong>Vox.</strong> Su medida 9: {cita('VOX', 13, 'Ni uno más. Después de recibir a 5 millones de personas en 5 años España no puede acoger a más inmigrantes')}. Incluye también la «remigración» y la prohibición de alquilar a inmigrantes en situación irregular.</p>
<p data-tipo="contexto"><strong>Frente Amplio.</strong> Quiere {cita('FA', 126, 'Culminar la regularización extraordinaria de 2026')} y un procedimiento estable de regularización.</p>

<h2>De qué habla más cada programa</h2>
<p data-tipo="dato">Contando palabras, el programa de Vox nombra la inmigración unas <strong>{n(RAZON_INM)} veces más</strong> que el del PSOE en proporción a su longitud: {p(INM['VOX'])} veces por cada 10.000 palabras, frente a {p(INM['PSOE'])}. El del PSOE es el que más habla de vivienda ({p(T['Vivienda']['PSOE'])}), de igualdad ({p(T['Igualdad y violencia machista']['PSOE'])}) y de clima y energía ({p(T['Clima y energía']['PSOE'])}). El de Vox es el más corto, con unas {n(round(M['palabras']['VOX'], -2))} palabras, según nuestro recuento, frente a unas {n(round(M['palabras']['FA'], -2))} del Frente Amplio, así que en él cada mención pesa más.</p>
{g_temas}
'''

preguntas = [
    ('¿Dónde se puede leer el programa electoral de cada partido?',
     f'El del PP, en <a href="{U["PP"]}">su web</a>. Los del PSOE y Vox, en las copias de El Independiente (<a href="{U["PSOE"]}">PSOE</a>, <a href="{U["VOX"]}">Vox</a>), y el del Frente Amplio, en la de <a href="{U["FA"]}">Demócrata</a>.'),
    ('¿Cuántas medidas tiene cada programa?',
     f'El del PP, 249 medidas; el del PSOE, 500 compromisos; el de Vox, 115 propuestas, y el del Frente Amplio se ordena en 18 bloques.'),
    ('¿Qué propone cada partido sobre vivienda?',
     'El PP, construir un millón de viviendas; el PSOE, un parque público estatal de 100.000; el Frente Amplio, 1,5 millones de viviendas públicas en 12 años, y Vox, prioridad para los españoles en la vivienda protegida y un IVA del 0 % en la primera vivienda nueva.'),
    ('¿Tiene Podemos programa electoral para el 29N?',
     'No lo ha publicado. Se presenta por separado del Frente Amplio.'),
]
enlaces = (f'<a href="{BASE}encuestas/">Las encuestas de las elecciones generales del 29N</a> · '
           f'{L("debate-sanchez-feijoo-29n", "Debate Sánchez Feijóo")} · {L("coaliciones-quien-va-con-quien-29n", "Quién va con quién el 29N")}')
foot = ('Datos: programas electorales del 29N del PP, el PSOE, Vox y el Frente Amplio. '
        'Cálculo: programas_29n_menciones.py y programas_29n.py, en actualidad/src/resumenes/.')
DATOS = {'paginas': PAG, 'palabras': M['palabras'], 'tasa': T, 'RAZON_INM': RAZON_INM}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Programa electoral 29N',
      'Programa electoral de PP, PSOE, Vox y Frente Amplio: qué propone cada uno el 29N',
      'El PP promete construir un millón de viviendas; el PSOE, un parque público de 100.000, y el Frente Amplio, 1,5 millones de viviendas públicas en 12 años. Vox no da cifra y pide «prioridad nacional». Lo que dicen los cuatro programas de las elecciones generales del 29N sobre vivienda, impuestos, pensiones e inmigración, con sus palabras.',
      '19 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(round(RAZON_INM, 2))
