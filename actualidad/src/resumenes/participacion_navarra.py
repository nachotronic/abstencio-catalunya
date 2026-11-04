"""«Quién vota en Navarra» (5-11-2026): participación en las generales de 2023 en los 86 municipios navarros de más de 1.000
habitantes, con Pamplona y los municipios de su alrededor, y su relación con el voto a EH Bildu y con la renta.

Cifras: generales-2026/descargas/municipios.csv (generales de 2019-N y 2023 por municipio) y
resultados_secciones_largo_municipales_europeas.csv (municipales de 2023 por sección, sumadas por municipio).
Participación = votantes (candidaturas, blancos y nulos) entre censo de residentes en España, sin CERA, como en el resto del mapa.
El voto a EH Bildu es su porcentaje del voto a candidaturas y blancos en 2023 (la familia BILDU de 2023 es solo EH Bildu).
Renta neta por unidad de consumo del Atlas de Distribución de Renta del INE (ADRH 2023).
Uso, desde la raíz: python3 actualidad/src/resumenes/participacion_navarra.py
"""
import json

import pandas as pd

from comun import BASE, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
E = '2023_07'
C_ALTA, C_BAJA, C_GRIS = '#2f6f8f', '#c2581b', 'var(--otros)'   # no son colores de partido: la participación no es de nadie

m = pd.read_csv('generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
ES_PART = round(float(m[f'{E}_votantes'].sum() / m[f'{E}_censo'].sum() * 100), 6)
nv = m[m.mun_code.str[:2] == '31']
assert len(nv) == 272
NAV_PART = round(float(nv[f'{E}_votantes'].sum() / nv[f'{E}_censo'].sum() * 100), 6)
g = nv[nv.poblacion >= 1000].copy()
assert len(g) == 86
g['part'] = g[f'{E}_votantes'] / g[f'{E}_censo'] * 100
g['part19'] = g['2019_11_votantes'] / g['2019_11_censo'] * 100
g['bildu'] = g[f'{E}_BILDU'] * 100
NOM = lambda s: s.split('/')[0].replace(' (Valle de Elorz)', '')
g['nom'] = g.municipio.map(NOM)

# municipales de 2023, mismos municipios
s = pd.read_csv('generales-2026/descargas/resultados_secciones_largo_municipales_europeas.csv', dtype={'mun_code': str, 'tract_code': str},
                usecols=['mun_code', 'censo', 'votantes', 'eleccion'])
s = s[(s.mun_code.str[:2] == '31') & (s.eleccion == 'M2023')].groupby('mun_code')[['censo', 'votantes']].sum()
assert set(g.mun_code) <= set(s.index)

def part(df, cv='votantes', cc='censo'):
    return round(float(df[cv].sum() / df[cc].sum() * 100), 6)

ALTO = g[g.bildu >= 40]
BAJO = g[g.bildu < 15]
GRUPOS = {'alto': {'n': len(ALTO), 'gen': part(ALTO, f'{E}_votantes', f'{E}_censo'), 'mun': part(s.loc[ALTO.mun_code])},
          'bajo': {'n': len(BAJO), 'gen': part(BAJO, f'{E}_votantes', f'{E}_censo'), 'mun': part(s.loc[BAJO.mun_code])}}
assert GRUPOS['alto']['n'] == 7 and GRUPOS['bajo']['n'] == 47
assert round(GRUPOS['alto']['gen'], 0) == 64 and round(GRUPOS['bajo']['gen'], 0) == 71, GRUPOS
CORR_B = round(float(g[['part', 'bildu']].corr().iloc[0, 1]), 2)
CORR_R = round(float(g[['part', 'renta_uc']].corr().iloc[0, 1]), 2)
assert CORR_B == -0.59 and CORR_R == -0.07, (CORR_B, CORR_R)
SUBEN = int((g.part > g.part19).sum())
assert SUBEN == 55

MUN = {r.nom: {'part': round(r.part, 6), 'part19': round(r.part19, 6), 'bildu': round(r.bildu, 6), 'pob': int(r.poblacion),
               'renta': None if pd.isna(r.renta_uc) else int(r.renta_uc), 'cod': r.mun_code} for r in g.itertuples()}
ORD = sorted(MUN, key=lambda k: MUN[k]['part'])
BAJOS, ALTOS = ORD[:10], ORD[-10:][::-1]
assert BAJOS[:3] == ['Olazti', 'Ultzama', 'Irurtzun'] and ALTOS[:2] == ['Fontellas', 'Monteagudo'], (BAJOS, ALTOS)

# Pamplona y los municipios de su alrededor con ficha propia
PAMPLONA = ['Pamplona', 'Valle de Egüés', 'Ansoáin', 'Huarte', 'Zizur Mayor', 'Noáin', 'Berrioplano', 'Aranguren', 'Barañáin',
            'Villava', 'Burlada', 'Berriozar', 'Orkoien', 'Cizur']
assert all(k in MUN for k in PAMPLONA), [k for k in PAMPLONA if k not in MUN]
PAM = {k: MUN[k] for k in sorted(PAMPLONA, key=lambda k: -MUN[k]['part'])}
PAM_MAX, PAM_MIN = max(PAM, key=lambda k: PAM[k]['part']), min(PAM, key=lambda k: PAM[k]['part'])
assert PAM_MAX == 'Cizur' and PAM_MIN == 'Berriozar', (PAM_MAX, PAM_MIN)
PAM_BAJAN = sorted(k for k in PAM if round(PAM[k]['part'], 1) < round(PAM[k]['part19'], 1))   # a un decimal, como en la tabla (Berriozar: 63,7 y 63,7)

import sys
sys.path.insert(0, 'src')
from territorios_rutas import ruta_municipio   # noqa: E402
MU = lambda k: f'<a href="{BASE}{ruta_municipio("31", nv.loc[nv.mun_code == MUN[k]["cod"], "municipio"].iloc[0])}">{esc(k)}</a>'


# --- gráficos ---
SIN_CERA = 'Participación: votantes entre censo de residentes en España, sin voto exterior (CERA).'
fil = ([(k, MUN[k]['part'], C_ALTA, f'{p(MUN[k]["part"])} %') for k in ALTOS]
       + [(k, MUN[k]['part'], C_BAJA, f'{p(MUN[k]["part"])} %') for k in BAJOS[::-1]])
g_ext = figura('Los diez que más votaron y los diez que menos', 'Participación en las generales de 2023 en los municipios navarros de 1.000 habitantes o más',
               barras(fil, 100, 'Participación en los diez municipios navarros que más votaron y en los diez que menos', ml=150, alto=22,
                      linea=(NAV_PART, f'Navarra, {p(NAV_PART)} %'), separar=True),
               'Fuente: Ministerio del Interior. ' + SIN_CERA, [('Los diez que más', C_ALTA), ('Los diez que menos', C_BAJA)],
               (['Municipio', 'Participación', 'Voto a EH Bildu'], [[k, p(MUN[k]['part']), p(MUN[k]['bildu'])] for k in ALTOS + BAJOS[::-1]]))
g_pam = figura('Pamplona y su alrededor', 'Participación en las generales de 2023 en Pamplona y en los municipios de su alrededor con 1.000 habitantes o más',
               barras([(k, v['part'], C_GRIS, f'{p(v["part"])} %') for k, v in PAM.items()], 100, 'Participación en Pamplona y los municipios de su alrededor',
                      ml=150, alto=22, linea=(NAV_PART, f'Navarra, {p(NAV_PART)} %'), separar=True),
               'Fuente: Ministerio del Interior. ' + SIN_CERA, None,
               (['Municipio', '2023', 'Noviembre de 2019', 'Voto a EH Bildu en 2023'],
                [[k, p(v['part']), p(v['part19']), p(v['bildu'])] for k, v in PAM.items()]))
g_gru = figura('Donde más vota EH Bildu, menos se vota en las generales', 'Participación en 2023 según el voto a EH Bildu del municipio, en las generales y en las municipales',
               barras([('EH Bildu, 40 % o más · generales', GRUPOS['alto']['gen'], C_BAJA, f'{p(GRUPOS["alto"]["gen"])} %'),
                       ('EH Bildu, 40 % o más · municipales', GRUPOS['alto']['mun'], C_BAJA, f'{p(GRUPOS["alto"]["mun"])} %'),
                       ('EH Bildu, menos del 15 % · generales', GRUPOS['bajo']['gen'], C_ALTA, f'{p(GRUPOS["bajo"]["gen"])} %'),
                       ('EH Bildu, menos del 15 % · municipales', GRUPOS['bajo']['mun'], C_ALTA, f'{p(GRUPOS["bajo"]["mun"])} %')],
                      100, 'Participación según el voto a EH Bildu', ml=250, alto=26),
               f'Fuente: Ministerio del Interior, generales del 23 de julio y municipales del 28 de mayo de 2023. {GRUPOS["alto"]["n"]} municipios con el 40 % o más de voto a EH Bildu '
               f'en las generales y {GRUPOS["bajo"]["n"]} con menos del 15 %, entre los 86 de 1.000 habitantes o más. El censo de las municipales incluye a los vecinos de la UE. ' + SIN_CERA)

DATOS = {'MUN': MUN, 'GRUPOS': GRUPOS, 'NAV_PART': NAV_PART, 'ES_PART': ES_PART, 'CORR_B': CORR_B, 'CORR_R': CORR_R, 'SUBEN': SUBEN}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
ga, gb = GRUPOS['alto'], GRUPOS['bajo']
F, Mo, O, U, I = MUN['Fontellas'], MUN['Monteagudo'], MUN['Olazti'], MUN['Ultzama'], MUN['Irurtzun']

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">En las generales de julio de 2023 votó en Navarra el {p(NAV_PART)} % de sus electores residentes, casi lo mismo que en el conjunto de España ({p(ES_PART)} %). Pero dentro de Navarra hay más de veinte puntos de distancia entre pueblos. Entre los 86 municipios de 1.000 habitantes o más, el que más votó fue {MU("Fontellas")}, en la Ribera, con el {p(F["part"])} %, seguido de {MU("Monteagudo")} ({p(Mo["part"])} %). El que menos, {MU("Olazti")}, en la Sakana, con el {p(O["part"])} %, por delante de {MU("Ultzama")} ({p(U["part"])} %) e {MU("Irurtzun")} ({p(I["part"])} %).</p>
{g_ext}
<p data-tipo="dato">Los diez que menos votaron están casi todos en el norte y el noroeste, donde EH Bildu tiene su voto más alto. En los {ga["n"]} municipios donde EH Bildu pasó del 40 % votó el {p(ga["gen"])} %; en los {gb["n"]} donde no llegó al 15 %, el {p(gb["gen"])} %. La correlación entre participación y voto a EH Bildu en los 86 municipios es de {n(CORR_B, 2)}.</p>
{g_gru}
<p data-tipo="patron">La diferencia no es solo de las generales. En las municipales de mayo de 2023, esos mismos {ga["n"]} municipios votaron el {p(ga["mun"])} % y los {gb["n"]} de menos voto a EH Bildu, el {p(gb["mun"])} %. La distancia se estrecha algo, de {p(gb["gen"] - ga["gen"])} a {p(gb["mun"] - ga["mun"])} puntos, pero no desaparece.</p>
<p data-tipo="contexto">En Navarra la renta no ordena la participación como en otros sitios: la correlación entre renta y participación en estos 86 municipios es de {n(CORR_R, 2)}, prácticamente nula. En la Comunidad de Madrid, con el mismo cálculo, es de 0,69 ({L("participacion-renta-municipios-madrid-29n", "quién no vota en Madrid")}).</p>
<p data-tipo="hipotesis">Los datos no dicen por qué. Una posibilidad es que parte del electorado de esas zonas se sienta menos llamado a unas elecciones a las Cortes que a las municipales, pero las municipales también muestran la brecha, así que no basta. Otra es que la abstención responda a la distancia de una parte de esos vecinos con las instituciones del Estado, pero tampoco eso se puede comprobar con resultados. Para saberlo harían falta encuestas a electores, no resultados por municipio.</p>

<h2>Pamplona y su alrededor</h2>
<p data-tipo="dato">{MU("Pamplona")} votó el {p(MUN["Pamplona"]["part"])} %. A su alrededor, el que más votó fue {MU("Cizur")} ({p(PAM["Cizur"]["part"])} %), seguido de {MU("Zizur Mayor")} ({p(PAM["Zizur Mayor"]["part"])} %) y {MU("Aranguren")} ({p(PAM["Aranguren"]["part"])} %). {MU("Valle de Egüés")} votó el {p(PAM["Valle de Egüés"]["part"])} %, {MU("Huarte")} el {p(PAM["Huarte"]["part"])} %, {MU("Ansoáin")} el {p(PAM["Ansoáin"]["part"])} %, {MU("Noáin")} el {p(PAM["Noáin"]["part"])} % y {MU("Berrioplano")} el {p(PAM["Berrioplano"]["part"])} %. El que menos, {MU("Berriozar")}, con el {p(PAM["Berriozar"]["part"])} %.</p>
{g_pam}
<p data-tipo="dato">Frente a la repetición de noviembre de 2019, la participación subió en {SUBEN} de los 86 municipios. Alrededor de Pamplona fue al revés: bajó en {len(PAM_BAJAN)} de los {len(PAM)}, entre ellos {MU("Valle de Egüés")}, que pasó del {p(PAM["Valle de Egüés"]["part19"])} % al {p(PAM["Valle de Egüés"]["part"])} %, y {MU("Aranguren")}, del {p(PAM["Aranguren"]["part19"])} % al {p(PAM["Aranguren"]["part"])} %.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">La participación de esta pieza es la de los residentes en España, sin el voto exterior; por eso sale algo más alta que la oficial. Son datos de municipios, no de personas: que un pueblo con mucho voto a EH Bildu vote menos no significa que los votantes de EH Bildu se abstengan más. Cada ficha de municipio tiene además el resultado sección a sección, dónde votar y qué hacer si te ha tocado mesa el 29N.</p>
'''

preguntas = [
    ('¿Qué municipio de Navarra vota más?', f'Entre los de 1.000 habitantes o más, Fontellas: el {p(F["part"])} % en las generales de 2023, sin contar el voto exterior. El que menos, Olazti, con el {p(O["part"])} %.'),
    ('¿Cuánto votó Pamplona en las generales de 2023?', f'El {p(MUN["Pamplona"]["part"])} % de sus electores residentes, frente al {p(NAV_PART)} % de toda Navarra.'),
    ('¿Votan menos los pueblos con más voto a EH Bildu?', f'En 2023, sí: el {p(ga["gen"])} % en los {ga["n"]} municipios donde EH Bildu pasó del 40 % y el {p(gb["gen"])} % en los {gb["n"]} donde no llegó al 15 %. Es una relación entre municipios, no entre personas.'),
]
enlaces = (f'<a href="{BASE}municipio/navarra/">Los municipios de Navarra</a> · <a href="{BASE}elecciones/navarra/">Elecciones en Navarra</a> · '
           f'<a href="{BASE}encuestas/navarra/">Encuesta de Navarra</a> · {L("navarra-historia-electoral", "Historia electoral de Navarra")} · '
           f'<a href="{BASE}elecciones/tarjeta-censal-29n/">Cómo votó tu sección</a>')
foot = ('Datos: Ministerio del Interior, generales de noviembre de 2019 y de 2023 y municipales de 2023 por municipio; INE, Atlas de Distribución de Renta de los Hogares 2023. '
        'Cálculo: actualidad/src/resumenes/participacion_navarra.py.')

pieza('participacion-navarra-municipios-29n', 'Quién vota en Navarra',
      f'En la Navarra donde EH Bildu pasa del 40 % votó el {n(ga["gen"])} %; donde no llega al 15 %, el {n(gb["gen"])} %: el mapa de la participación, pueblo a pueblo',
      f'Fontellas votó un {p(F["part"])} % y Olazti un {p(O["part"])} %. En Navarra la participación apenas va ligada a la renta; al voto a EH Bildu, bastante más. '
      f'Pamplona votó el {p(MUN["Pamplona"]["part"])} %, y a su alrededor la participación bajó respecto a 2019.',
      '4 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
