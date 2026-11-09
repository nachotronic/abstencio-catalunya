"""«La huelga cárnica y los pueblos de la industria» (9-11-2026): del 9 al 13 de noviembre, CCOO de Industria y
UGT FICA convocan huelga en la industria cárnica (convenio estatal; 126.000 personas llamadas, según CCOO).
La pieza cruza el peso de la industria en el empleo de cada municipio con su voto en las generales de 2023.

Empleo: INE, Censo anual de población 2023, ocupados de 16 y más años por sector de actividad y municipio de residencia
(data/empleo/empleo_sector_municipios.csv, ver src/empleo_ine.py). «Industria» es el sector entero (CNAE B a E): el
censo no separa la industria cárnica. Voto: generales de julio de 2023 por municipio
(generales-2026/descargas/municipios.csv), porcentaje sobre votos a candidaturas y sin voto exterior (CERA).
Comparación dentro de cada provincia: a cada municipio se le resta la media de su provincia (ponderada por censo) en
peso de la industria y en voto; luego se agrupan en diez partes con el mismo censo según esa diferencia de industria.
Uso, desde la raíz: python3 actualidad/src/resumenes/huelga_carnica.py
"""
import json

import numpy as np
import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']

e = pd.read_csv(RAIZ / 'data/empleo/empleo_sector_municipios.csv', dtype={'mun_code': str})
e = e[e.anyo == 2023][['mun_code', 'municipio', 'ocupados', 'industria']]
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
cols = ['mun_code', '2023_07_censo', '2023_07_votantes', '2023_07_gana'] + [f'2023_07_v{f}' for f in F]
d = e.merge(m[cols], on='mun_code', how='inner')
d = d[d.ocupados > 0].copy()
NMUN = len(d)
assert NMUN == 7563, NMUN
d['val'] = d[[f'2023_07_v{f}' for f in F]].sum(axis=1)
d['ind'] = d.industria / d.ocupados * 100
d['prov'] = d.mun_code.str[:2]
for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'JUNTS', 'ERC'):
    d[k] = d[f'2023_07_v{k}'] / d.val * 100
d['part'] = d['2023_07_votantes'] / d['2023_07_censo'] * 100
W = '2023_07_censo'
IND_ES = d.industria.sum() / d.ocupados.sum() * 100

# Diferencia con la media de la provincia
VAR = ['ind', 'PP', 'PSOE', 'VOX', 'SUMAR', 'part']
for k in VAR:
    media = {pr: np.average(g[k], weights=g[W]) for pr, g in d.groupby('prov')}
    d[k + '_r'] = d[k] - d.prov.map(media)
d = d.sort_values('ind_r')
d['cum'] = d[W].cumsum() / d[W].sum()
d['dec'] = np.minimum((d.cum * 10).astype(int) + 1, 10)
DEC = {int(k): {v: float(np.average(g[v + '_r'], weights=g[W])) for v in VAR} for k, g in d.groupby('dec')}
for k, g in d.groupby('dec'):
    DEC[int(k)]['n'] = len(g)
D1, D10 = DEC[1], DEC[10]
assert D10['PP'] < 0 < D1['PP'] and max(abs(DEC[k]['VOX']) for k in DEC) < 1

# Municipios con más peso de la industria (2.000 ocupados o más)
TOP = d[d.ocupados >= 2000].sort_values('ind', ascending=False).head(12)
gana = dict(zip(d.mun_code, d['2023_07_gana']))
G = {c: d[d.mun_code == c].iloc[0] for c in ('25110', '37156')}   # Guissona, Guijuelo
assert G['25110'].municipio == 'Guissona' and G['37156'].municipio == 'Guijuelo'
assert TOP.iloc[0].mun_code == '25110'
POS_GUI = list(TOP.mun_code).index('37156') + 1
assert POS_GUI == 6, POS_GUI
MED_PROV = {pr: {k: float(np.average(g[k], weights=g[W])) for k in ('PP', 'PSOE', 'VOX', 'part', 'ind')} for pr, g in d.groupby('prov') if pr in ('25', '37')}

# --- Gráficos ---
COLG = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'JUNTS': 'var(--junts)', 'ERC': 'var(--erc)', 'BILDU': 'var(--bildu)', 'PNV': 'var(--pnv)', 'VOX': COLOR['Vox']}
NOMG = {'PP': 'PP', 'PSOE': 'PSOE', 'JUNTS': 'Junts', 'ERC': 'ERC', 'BILDU': 'EH Bildu', 'PNV': 'PNV', 'VOX': 'Vox'}
for c in TOP.mun_code:
    assert gana[c] in COLG, gana[c]
g_top = figura('Guissona, el municipio con más peso de la industria en el empleo',
               'Porcentaje de los ocupados que trabajan en la industria, en los municipios con 2.000 ocupados o más. El color es el partido más votado en las generales de 2023',
               barras([(r.municipio, r.ind, COLG[gana[r.mun_code]], f'{p(r.ind)} %') for r in TOP.itertuples()], 60,
                      'Peso de la industria en el empleo de cada municipio', ml=150, linea=(IND_ES, f'España: {p(IND_ES)} %'), separar=True),
               'Fuente: INE, Censo anual de población 2023 (ocupados por municipio de residencia); Ministerio del Interior, generales de 2023.',
               sorted({(NOMG[gana[c]], COLG[gana[c]]) for c in TOP.mun_code}),
               (['Municipio', 'Ocupados', 'En la industria', 'Más votado en 2023'],
                [[esc(r.municipio), n(r.ocupados), f'{p(r.ind)} %', NOMG[gana[r.mun_code]]] for r in TOP.itertuples()]))


def grupos(W_=640, ml=150):
    """PP y PSOE: diferencia con la media de su provincia, en cada décima parte de municipios según el peso de la industria."""
    filas = [(f'{k}.ª' + (' (menos industria)' if k == 1 else ' (más industria)' if k == 10 else ''), DEC[k]['PP'], DEC[k]['PSOE']) for k in range(1, 11)]
    alto, H = 34, 34 * 10 + 30
    c0, esc_ = ml + (W_ - ml - 40) / 2, (W_ - ml - 40) / 2 / 3
    x = lambda v: c0 + v * esc_
    out = [f'<svg viewBox="0 0 {W_} {H}" role="img" aria-label="Voto al PP y al PSOE frente a la media de su provincia, según el peso de la industria">']
    for i, (nom, a, b) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 18}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for j, (v, col, par) in enumerate(((a, COLOR['PP'], 'PP'), (b, COLOR['PSOE'], 'PSOE'))):
            yy = y + 3 + j * 13
            x1, x2 = sorted((c0, x(v)))
            txt = f'{v:+.1f}'.replace('.', ',')
            out.append(f'<rect x="{x1:.1f}" y="{yy}" width="{max(1.5, x2 - x1):.1f}" height="11" fill="{col}" rx="2"><title>{esc(nom)}, {par}: {txt} puntos</title></rect>')
            xt = x(v) + (5 if v >= 0 else -5)
            out.append(f'<text x="{xt:.1f}" y="{yy + 10}" class="lab"{" text-anchor=\"end\"" if v < 0 else ""}>{txt}</text>')
    out.append(f'<line x1="{c0:.1f}" x2="{c0:.1f}" y1="0" y2="{H - 24}" stroke="var(--fg)" stroke-dasharray="3 3"/>'
               f'<text x="{c0:.1f}" y="{H - 8}" text-anchor="middle" class="lab">media de la provincia</text></svg>')
    return ''.join(out)


g_dec = figura(f'Donde más pesa la industria, el PP saca {p(-D10["PP"])} puntos menos que en el resto de su provincia',
               'Diferencia en puntos entre el voto de cada grupo de municipios y la media de su provincia, en las generales de 2023. '
               'Los municipios se ordenan por cuánto pesa la industria en su empleo frente a su provincia y se reparten en diez partes con el mismo censo',
               grupos(), 'Fuente: INE, Censo anual de población 2023; Ministerio del Interior, generales de 2023. Porcentajes sobre votos a candidaturas.',
               [('PP', COLOR['PP']), ('PSOE', COLOR['PSOE'])],
               (['Décima parte', 'Industria (puntos sobre su provincia)', 'PP', 'PSOE', 'Vox', 'Sumar', 'Participación'],
                [[str(k)] + [f'{DEC[k][v]:+.1f}'.replace('.', ',') for v in VAR] for k in range(1, 11)]))

# --- Texto ---
CCOO = ('https://industria.ccoo.es/noticia:772073--Huelga_en_la_industria_carnica_del_9_al_13N_Neveras_vacias_hasta_que_las_'
        'patronales_entiendan_que_deben_transformar_sus_beneficios_en_mas_salario_y_en_mejores_condiciones&opc_id=7b0815797cd81939bb3cdca8b4b06f4d')
ANAFRIC = 'https://www.agronewscastillayleon.com/anafric-huelga-industria-carnica-noviembre-2026-salarios'
BONAREA = 'https://www.bonarea.com'
GARZON = 'https://www.eldiario.es/opinion/tribuna-abierta/vota-clase-trabajadora-espana_129_1401496.html'
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
gs, gj = G['25110'], G['37156']
lle, sal = MED_PROV['25'], MED_PROV['37']
assert gs.part < lle['part'] and gj.PP > sal['PP'] - 5

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">La industria cárnica está llamada desde este lunes a cinco días de huelga, del 9 al 13 de noviembre, convocados por CCOO de Industria y UGT FICA tras fracasar la mediación en el SIMA sobre el convenio estatal del sector, según <a href="{ANAFRIC}">Agronews Castilla y León</a>. CCOO cifra en 126.000 las personas llamadas a parar y pide una subida salarial mínima del 4 % con revisión según el IPC y reducir la jornada anual, hoy de 1.748 horas, según su <a href="{CCOO}">convocatoria</a>. La patronal Anafric ofrece un 3,8 % para 2026, según el mismo medio.</p>
<blockquote class="cita"><p>«La huelga de quienes alimentan el país ya está aquí, por más salario y por mejores condiciones laborales»</p><footer>CCOO de Industria, en su <a href="{CCOO}">convocatoria</a> del 6 de noviembre de 2026</footer></blockquote>
<p data-tipo="dato">En España, el {p(IND_ES)} % de los ocupados trabaja en la industria, según el censo de 2023 del INE, que cuenta a cada trabajador en el municipio donde vive. Entre los municipios con al menos 2.000 ocupados, donde más pesa es en Guissona (Lleida), con el {p(gs.ind)} %. Allí tiene su sede la empresa alimentaria <a href="{BONAREA}">bonÀrea</a>. Guijuelo (Salamanca), con el {p(gj.ind)} %, es el sexto. El censo no separa la industria cárnica del resto de la industria, así que la lista mezcla la alimentación con otras ramas.</p>
{g_top}
<p data-tipo="dato">Para no confundir la industria con la geografía, la comparación se hace dentro de cada provincia. En la décima parte de municipios donde la industria pesa más que en el resto de su provincia, de media {p(D10["ind"])} puntos más, el PP sacó en las generales de 2023 {p(-D10["PP"])} puntos menos que la media provincial. En la décima parte con menos industria, {p(D1["PP"])} puntos más. El PSOE va al revés, aunque con menos distancia: {p(D1["PSOE"]).replace("-", "−")} puntos en los menos industriales y {"+" if D10["PSOE"] >= 0 else ""}{p(D10["PSOE"]).replace("-", "−")} en los más. El voto a Vox apenas cambia: {p(D1["VOX"]).replace("-", "−")} y {p(D10["VOX"]).replace("-", "−")} puntos, y en ninguna de las diez partes se separa un punto de la media de su provincia.</p>
{g_dec}
<p data-tipo="dato">En Guissona ganó el PSOE con el {p(gs.PSOE)} %, por delante de Junts ({p(gs.JUNTS)} %) y ERC ({p(gs.ERC)} %). El PP sacó el {p(gs.PP)} %. Votó el {p(gs.part)} % del censo, frente al {p(lle["part"])} % de la provincia de Lleida. En Guijuelo ganó el PP con el {p(gj.PP)} %, frente al {p(sal["PP"])} % de la provincia de Salamanca; el PSOE sacó el {p(gj.PSOE)} % y Vox, el {p(gj.VOX)} %.</p>
<blockquote class="cita"><p>«Vox es más votado particularmente entre directivos y cuadros, profesionales tradicionales, otras profesiones y pequeños propietarios y autónomos, mientras que no es apoyado por agricultores, supervisores y el conjunto de la clase trabajadora»</p><footer>Alberto Garzón, economista y entonces coordinador federal de IU, <a href="{GARZON}">«¿A quién vota la clase trabajadora en España?»</a>, eldiario.es (9 de agosto de 2019)</footer></blockquote>
<p data-tipo="contexto">El propio Garzón advierte en ese artículo que «la falta de significación puede estar motivada por la escasez de datos» y que solo «puede servir de indicio el signo de los coeficientes», así que su conclusión es una pista, no una prueba.</p>
<p data-tipo="hipotesis">Que los municipios más industriales voten algo menos al PP que su provincia es una correlación, no una explicación: estos municipios también se distinguen por su tamaño, su renta o su edad, y los datos por municipio no dicen qué votan quienes trabajan en una fábrica. Lo que sí muestran es que el voto a Vox no se aleja de la media provincial en ningún grupo, tenga más o menos industria.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">El censo cuenta a cada ocupado donde vive, no donde trabaja, y reúne en «industria» todas las ramas, de la alimentación a la química. Los porcentajes de voto son sobre votos a candidaturas y sin el voto exterior. Ver también {L("oficios-y-voto-municipios-29n", "el oficio de cada municipio y su voto")} y {L("huelga-11n-paro-participacion", "la huelga del 11-N y el paro")}.</p>'''

preguntas = [
    ('¿Cuándo es la huelga de la industria cárnica?', 'Del lunes 9 al viernes 13 de noviembre de 2026, convocada por CCOO de Industria y UGT FICA por el convenio estatal del sector.'),
    ('¿Qué municipio tiene más empleo en la industria?', f'Entre los que tienen al menos 2.000 ocupados, Guissona (Lleida), con el {p(gs.ind)} % de sus ocupados en la industria, según el censo de 2023 del INE.'),
    ('¿Votan distinto los municipios industriales?', f'Dentro de cada provincia, la décima parte con más peso de la industria dio al PP {p(-D10["PP"])} puntos menos que la media provincial en 2023. El voto a Vox apenas cambia.'),
]
enlaces = (f'{L("oficios-y-voto-municipios-29n", "Oficios y voto")} · {L("huelga-11n-paro-participacion", "La huelga del 11-N")} · '
           f'{L("vox-barrios-obreros-clase-29n", "Vox y los barrios obreros")} · <a href="{BASE}encuestas/">Encuestas del 29N</a>')
foot = ('Datos: INE, Censo anual de población 2023, ocupados por sector de actividad y municipio de residencia; Ministerio del Interior, '
        'generales de julio de 2023 por municipio. Cálculo: actualidad/src/resumenes/huelga_carnica.py.')

DATOS = {'IND_ES': IND_ES, 'NMUN': NMUN, 'DEC': DEC, 'POS_GUI': POS_GUI, 'MED_PROV': MED_PROV,
         'G': {c: {k: float(G[c][k]) for k in ('ind', 'PP', 'PSOE', 'VOX', 'JUNTS', 'ERC', 'part')} for c in G},
         'TOP': [[r.municipio, int(r.ocupados), float(r.ind), gana[r.mun_code]] for r in TOP.itertuples()]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza('huelga-carnica-pueblos-industria-29n', 'La huelga cárnica y los pueblos de la industria',
      f'En los municipios donde más pesa la industria, el PP saca {p(-D10["PP"])} puntos menos que en el resto de su provincia, y el voto a Vox apenas cambia',
      f'La industria cárnica para del 9 al 13 de noviembre. El {p(IND_ES)} % de los ocupados de España trabaja en la industria; en Guissona, sede de bonÀrea, el {p(gs.ind)} %. '
      'Dentro de cada provincia, los municipios más industriales votan algo menos al PP, y el voto a Vox no cambia.',
      '9 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
