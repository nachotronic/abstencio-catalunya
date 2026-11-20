"""Veda de encuestas: hasta cuándo se pueden publicar las del 29N (pieza de servicio del 20-11-2026).

- Ley: LOREG, art. 69.7 (texto vigente desde la Ley Orgánica 2/2011, que añadió «o reproducción»; texto original de 1985 sin esas
  palabras), art. 145 (delito) y art. 153.2 (multa). Instrucción 3/2019 de la Junta Electoral Central.
- 2023: encuestas nacionales de previsiones/datos/encuestas/encuestas_limpias.csv (Electográfica, fecha de publicación), desde la
  convocatoria (30-5-2023) hasta el último día permitido (17-7-2023). Se cuentan empresas distintas por día, no filas, porque
  Electográfica recoge a veces dos entregas de la misma empresa el mismo día.
- Andorra y Australia: Diario de León / El Periódico (20-12-2015), La Marea (15-12-2015), Libertad Digital (6-11-2019),
  GESOP (25-7-2023), Diari Més (7-5-2024).
Uso, desde la raíz: python3 actualidad/src/resumenes/veda_encuestas_29n.py
"""
import json
from datetime import date, timedelta

import pandas as pd

from comun import BASE, RAIZ, barras, figura, n, pieza

SLUG = 'veda-encuestas-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
LOREG = 'https://www.boe.es/buscar/act.php?id=BOE-A-1985-11672'
L69 = LOREG + '#asesentaynueve'
L145 = LOREG + '#acientocuarentaycinco'
L153 = LOREG + '#acientocincuentaytres'
LO2011 = 'https://www.boe.es/buscar/doc.php?id=BOE-A-2011-1639'
JEC2019 = 'https://www.boe.es/buscar/doc.php?id=BOE-A-2019-3191'
ELECTO = 'https://www.electografica.com/'
LEON = 'https://www.diariodeleon.es/nacional/151219/579930/encuesta-prohibida-elecciones-generales-penultimo-sondeo.html'
MAREA = 'https://www.lamarea.com/?p=79733'
LD = 'https://www.libertaddigital.com/espana/politica/2019-11-06/encuesta-andorrana-pedro-sanchez-pierde-un-punto-cae-debajo-resultado-28a-vox-15-1276647519/'
GESOP = 'https://gesop.net/es/2023/07/25/el-sondeo-de-gesop-del-23j-de-los-mas-acertados/'
MES = 'https://www.diarimes.com/es/actualidad/cataluna/240507/primer-sondeo-prohibido-diario-andorra-12-m-votos-escanos_144339.html'
ENC = f'{BASE}encuestas/'

# ---------- Calendario del 29N ----------
VOTO = date(2026, 11, 29)
VEDA = [VOTO - timedelta(days=k) for k in range(5, 0, -1)]
ULTIMO = VOTO - timedelta(days=6)
assert VEDA[0] == date(2026, 11, 24) and VEDA[-1] == date(2026, 11, 28) and ULTIMO == date(2026, 11, 23)
assert ULTIMO.weekday() == 0 and VOTO.weekday() == 6        # lunes y domingo
DIAS = ['lun', 'mar', 'mié', 'jue', 'vie', 'sáb', 'dom']

# ---------- 2023 ----------
VOTO23 = date(2023, 7, 23)
ULT23 = VOTO23 - timedelta(days=6)
assert ULT23 == date(2023, 7, 17) and ULT23.weekday() == 0
E = pd.read_csv(RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv')
E = E[E.ambito == 'ESPAÑA']
C23 = E[(E.publicado >= '2023-05-30') & (E.publicado <= ULT23.isoformat())]
POR_DIA = C23.groupby('publicado').encuestadora.nunique()
assert POR_DIA.idxmax() == '2023-07-17' and POR_DIA.max() == 12
assert sorted(POR_DIA.values)[-2] == 11                      # el segundo día con más, el domingo 16
VEDA23 = E[(E.publicado > ULT23.isoformat()) & (E.publicado < VOTO23.isoformat())]
assert len(VEDA23) == 0
INI = date(2023, 7, 4)
SERIE = []
d = INI
while d < VOTO23:
    k = d.isoformat()
    SERIE.append((d, int(POR_DIA.get(k, 0)), d > ULT23))
    d += timedelta(days=1)
DOS_SEM = C23[C23.publicado >= INI.isoformat()].encuestadora.nunique()
assert DOS_SEM == 21
ULT_DIA = int(POR_DIA['2023-07-17'])


def calendario():
    W, H, x0, w = 380, 96, 4, 53
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Calendario de la veda de encuestas del 29N">']
    for i in range(7):
        dia = ULTIMO + timedelta(days=i)
        x = x0 + i * w
        if dia == ULTIMO:
            fill, op, txt = 'var(--acc)', '0.85', 'último día'
        elif dia in VEDA:
            fill, op, txt = 'var(--muted)', '0.35', 'veda'
        else:
            fill, op, txt = 'var(--fg)', '0.85', 'votación'
        out.append(f'<rect x="{x}" y="20" width="{w - 4}" height="44" rx="4" fill="{fill}" fill-opacity="{op}"><title>{dia.day} de noviembre: {txt}</title></rect>')
        out.append(f'<text x="{x + (w - 4) / 2:.1f}" y="14" text-anchor="middle" class="lab">{DIAS[dia.weekday()]}</text>')
        out.append(f'<text x="{x + (w - 4) / 2:.1f}" y="49" text-anchor="middle" class="lab" style="font-size:16px">{dia.day}</text>')
        out.append(f'<text x="{x + (w - 4) / 2:.1f}" y="82" text-anchor="middle" class="lab" style="font-weight:400">{txt}</text>')
    out.append('</svg>')
    return ''.join(out)


g_cal = figura('Las encuestas del 29N se pueden publicar hasta el lunes 23',
               'Del martes 24 al sábado 28 de noviembre, los cinco días anteriores a la votación, la ley prohíbe publicarlas, difundirlas o reproducirlas',
               calendario(),
               f'Fuente: <a href="{L69}">artículo 69.7 de la Ley Orgánica del Régimen Electoral General</a>.')

mes = lambda d: f'{d.day} jul'
g_23 = figura(f'En 2023, el último día permitido fue el de más encuestas: {ULT_DIA} empresas publicaron la suya',
              'Empresas con una encuesta nacional publicada cada día, del 4 al 22 de julio de 2023. Del 18 al 22, la veda; las elecciones fueron el 23',
              barras([(f'{DIAS[d.weekday()]} {mes(d)}', v, 'var(--acc)' if d == ULT23 else 'var(--muted)', 'veda' if veda else n(v)) for d, v, veda in SERIE],
                     ULT_DIA * 1.15, 'Empresas con encuesta publicada por día en julio de 2023', W=380, ml=90, alto=22),
              f'Fuente: <a href="{ELECTO}">Electográfica</a>, encuestas de las elecciones generales de 2023 por fecha de publicación. Se cuenta cada empresa una vez al día. Cálculo propio.',
              None,
              (['Día', 'Empresas con encuesta publicada'], [[f'{d.day} de julio de 2023', 'veda' if veda else str(v)] for d, v, veda in SERIE]))

cuerpo = f'''
<p data-tipo="contexto">Las encuestas de las elecciones generales del 29N se pueden publicar hasta el lunes 23 de noviembre. Del martes 24 al sábado 28, los cinco días anteriores a la votación, la ley electoral prohíbe «la publicación y difusión o reproducción de sondeos electorales por cualquier medio de comunicación» (<a href="{L69}">artículo 69.7 de la LOREG</a>). Hasta el lunes, las últimas encuestas y su mediana están en <a href="{ENC}">la página de encuestas de las elecciones generales 2026</a>, que no incorporará ninguna nueva durante la veda.</p>
{g_cal}
<p data-tipo="contexto">La prohibición está en la ley desde 1985. La <a href="{LO2011}">reforma de 2011</a> le añadió dos palabras, «o reproducción», para que tampoco se puedan repetir encuestas publicadas en otro sitio. Saltársela tiene castigo: una multa de 3.000 a 30.000 euros (<a href="{L153}">artículo 153</a>), y el <a href="{L145}">artículo 145</a> castiga como delito, con prisión de tres meses a un año, multa e inhabilitación, a quien infrinja la normativa de encuestas electorales. La Junta Electoral Central vela por que se cumpla, y en 2019, con generales en abril y municipales, autonómicas y europeas en mayo, <a href="{JEC2019}">aclaró</a> que la veda de unas elecciones alcanza a las encuestas de todas las demás convocadas. Lo que no se prohíbe es hacer encuestas: los partidos pueden seguir encargándolas, pero no se pueden publicar, recuerda el <a href="{MES}">Diari Més</a>.</p>
<p data-tipo="dato">La veda produce un atasco el último día. En las generales de 2023, que se votaron el domingo 23 de julio, el último día para publicar fue el lunes 17. Ese día, {ULT_DIA} empresas publicaron encuesta nacional, más que en ningún otro día desde la convocatoria, según las recogidas por <a href="{ELECTO}">Electográfica</a>. En las dos semanas anteriores a la veda publicaron {DOS_SEM} empresas distintas.</p>
{g_23}
<h2>Las encuestas de Andorra</h2>
<p data-tipo="contexto">La ley española no llega a los medios de otros países, y algunos lo han aprovechado. El Periòdic d'Andorra publicó en las generales de 2008, en las catalanas de 2010 y en las municipales de Barcelona de 2015 una encuesta diaria del Gabinet d'Estudis Socials i Opinió Pública (GESOP) durante la veda, y repitió en las generales de diciembre de 2015, con una entrega cada día hasta la jornada de reflexión, según El Periódico, en un texto reproducido por <a href="{LEON}">Diario de León</a>, y <a href="{MAREA}">La Marea</a>. En noviembre de 2019, El Periódico publicó la encuesta de GESOP en su edición de Andorra, según <a href="{LD}">Libertad Digital</a>.</p>
<p data-tipo="contexto">En 2023 el destino fue Australia: <a href="{GESOP}">GESOP</a>, la empresa que hace las encuestas de El Periódico, cuenta que su sondeo del sábado 22 de julio se publicó «en el portal web australiano The Adelaide Review el mismo día de las elecciones». En las autonómicas catalanas de 2024 volvió a Andorra: el Diari d'Andorra publicó una encuesta diaria de Feedback durante la veda, según el <a href="{MES}">Diari Més</a>.</p>
<p data-tipo="contexto">Cuánto se equivocaron las últimas encuestas antes de la veda de 2023 está en {L("encuestas-error-2023-2019-29n", "esta pieza sobre el error de las encuestas")}, y cuánto discrepan las de ahora, en {L("cuanto-discrepan-encuestas-29n", "esta otra")}.</p>
'''

preguntas = [
    ('¿Hasta cuándo se pueden publicar encuestas de las elecciones generales del 29N?',
     f'Hasta el lunes 23 de noviembre. Del martes 24 al sábado 28 está prohibido publicarlas, difundirlas o reproducirlas (<a href="{L69}">artículo 69.7 de la LOREG</a>).'),
    ('¿Por qué no se pueden publicar encuestas la última semana de campaña?',
     'Porque la ley electoral lo prohíbe desde 1985 en los cinco días anteriores a la votación. La reforma de 2011 añadió la prohibición de reproducirlas.'),
    ('¿Qué son las encuestas de Andorra?',
     f'Encuestas publicadas por medios de fuera de España durante la veda, a los que no alcanza la ley española. El Periòdic d\'Andorra lo hizo con sondeos de GESOP en varias elecciones desde 2008, según <a href="{LEON}">El Periódico</a>, reproducido por Diario de León.'),
    ('¿Qué multa hay por publicar encuestas durante la veda?',
     f'De 3.000 a 30.000 euros, según el <a href="{L153}">artículo 153 de la LOREG</a>.'),
]
enlaces = (f'<a href="{ENC}">Encuestas de las elecciones generales 2026</a> · {L("encuestas-error-2023-2019-29n", "Cuánto fallaron las encuestas en 2023")} · '
           f'{L("cuanto-discrepan-encuestas-29n", "Cuánto discrepan las encuestas")}')
foot = ('Datos: Ley Orgánica del Régimen Electoral General, artículos 69, 145 y 153; Ley Orgánica 2/2011; Junta Electoral Central, Instrucción 3/2019; '
        'Electográfica, encuestas nacionales de 2023 por fecha de publicación. Cálculo: actualidad/src/resumenes/veda_encuestas_29n.py.')

DATOS = {'ULT_DIA': ULT_DIA, 'DOS_SEM': DOS_SEM, 'SEGUNDO': int(sorted(POR_DIA.values)[-2]),
         'SERIE': [[d.isoformat(), v, veda] for d, v, veda in SERIE]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Veda de encuestas',
      'Veda de encuestas: hasta cuándo se pueden publicar las del 29N',
      f'Las encuestas de las elecciones generales se pueden publicar hasta el lunes 23 de noviembre; del 24 al 28, la ley lo prohíbe. '
      f'En 2023, el último día permitido fue el de más encuestas: {ULT_DIA} empresas publicaron la suya.',
      '20 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print('ULT_DIA', ULT_DIA, 'DOS_SEM', DOS_SEM, [(d.isoformat(), v) for d, v, _ in SERIE])
