"""Los pueblos que siempre aciertan, ante el 29N: cuánto ganó el PP en 2023 en los 24 que han votado al ganador en las 16 generales.

Pieza aprobada por Nacho el 26-11 («Venga con la pieza»). Título fijo desde la publicación; la noche del 29N se actualiza
con si siguieron acertando.
Datos: actualidad/src/resumenes/datos/pueblos_aciertan_2023.csv, sacado de generales/datos/historico (Interior,
municipios_largo y candidaturas_municipio) con el mismo criterio que actualidad/src/historia/datos.py (D['ohio']):
partido más votado de cada municipio frente al de España; un empate de los dos primeros no cuenta como acierto.
Porcentajes sobre los votos a candidaturas; España, sin voto exterior (suma de los municipios).
Fila de España: el PP es solo el PP (8.093.469); hasta el 26-11-2026 sumaba también a UPN (51.778), que en 2023 fue por separado en Navarra.
Veda (LOREG 69.7): sin encuestas.
Uso, desde la raíz: python3 actualidad/src/resumenes/pueblos_aciertan.py
"""
import csv
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
SLUG = 'pueblos-que-siempre-aciertan-29n'
INTERIOR = 'https://infoelectoral.interior.gob.es/'
PORTADA = 'https://www.laportadadeextremadura.com/extremadura/pedro-sanchez-participara-este-viernes-en-un-acto-en-plasencia_9984_102.html'
INFOBAE = 'https://www.infobae.com/espana/2026/11/26/el-debate-a-cuatro-definitivo-en-directo-ultima-hora-de-las-elecciones-generales-29-n-y-la-campana-electoral/'

F = list(csv.DictReader(open(RAIZ / 'actualidad/src/resumenes/datos/pueblos_aciertan_2023.csv', encoding='utf-8')))
for f in F:
    for k in ('censo', 'votantes', 'PP', 'PSOE', 'VOX', 'SUMAR', 'votos_candidaturas'):
        f[k] = int(f[k])
ESP = next(f for f in F if f['grupo'] == 'espana')
S = sorted([f for f in F if f['grupo'] == 'siempre'], key=lambda f: (f['PP'] - f['PSOE']) / f['votos_candidaturas'])
EMP = [f for f in F if f['grupo'] == 'empate']
assert len(S) == 24 and len(EMP) == 4 and all(f['PP'] > f['PSOE'] for f in S)
pct = lambda f, k: 100 * f[k] / f['votos_candidaturas']
dif = lambda f: f['PP'] - f['PSOE']
dpt = lambda f: pct(f, 'PP') - pct(f, 'PSOE')
M = {f['municipio']: f for f in S}
FILO = [f for f in S if dpt(f) < 3]
assert [f['municipio'] for f in FILO] == ['Ayerbe', 'Jaca', 'Los Navalmorales', 'Biescas', 'Villaquilambre', 'Plasencia']
POCOS = sorted(S, key=dif)[:3]
assert [f['municipio'] for f in POCOS] == ['Ayerbe', 'La Cañada de Verich', 'Jarque de Moncayo']
PLA = M['Plasencia']
assert max(S, key=lambda f: f['censo']) is PLA
ELECT = sum(f['censo'] for f in S)
ARAGON = sum(1 for f in S if f['provincia'] in ('Huesca', 'Zaragoza', 'Teruel'))
assert ARAGON == 12
JA = M['Jaca']
PARTIDOS = [('PP', 'PP'), ('PSOE', 'PSOE'), ('VOX', 'Vox'), ('SUMAR', 'Sumar')]

etq = lambda f: f"{f['municipio']}"
g_margen = figura('En seis de los 24, el PP ganó en 2023 por menos de tres puntos',
                  'Ventaja del PP sobre el PSOE en 2023 en los municipios que han votado al ganador en las 16 elecciones generales, en puntos (y en votos)',
                  barras([(etq(f), dpt(f), 'var(--pp)', f"{p(dpt(f))} ({n(dif(f))} {'voto' if dif(f) == 1 else 'votos'})") for f in S],
                         27, 'Ventaja del PP sobre el PSOE en 2023 en los 24 municipios que siempre aciertan', W=400, ml=185, fmt=p),
                  f'Fuente: <a href="{INTERIOR}">Ministerio del Interior</a>. Porcentajes sobre los votos a candidaturas. Sin los cuatro municipios que empataron alguna vez.',
                  None,
                  (['Municipio', 'Provincia', 'Electores 2023', 'PP', 'PSOE', 'Ventaja (votos)', 'Ventaja (puntos)'],
                   [[f['municipio'], f['provincia'], n(f['censo']), n(f['PP']), n(f['PSOE']), n(dif(f)), p(dpt(f))] for f in S]))

g_jaca = figura('Jaca votó en 2023 casi como el conjunto de España',
                'Porcentaje de cada partido sobre los votos a candidaturas en las elecciones generales de 2023',
                barras([(f'{nom} · Jaca', pct(JA, k), f'var(--{nom.lower()})', p(pct(JA, k))) for k, nom in PARTIDOS for _ in [0]] +
                       [(f'{nom} · España', pct(ESP, k), 'var(--muted)', p(pct(ESP, k))) for k, nom in PARTIDOS], 40,
                       'Voto de Jaca y de España en 2023', W=400, ml=120, fmt=p),
                f'Fuente: <a href="{INTERIOR}">Ministerio del Interior</a>. España, sin voto exterior.',
                None,
                (['Partido', 'Jaca (%)', 'España (%)'], [[nom, p(pct(JA, k)), p(pct(ESP, k))] for k, nom in PARTIDOS]))

# Perfil (correlacional): los 24 juntos, ponderados por población, frente a toda España. generales-2026/descargas/municipios.csv
import pandas as pd
_m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str},
                 usecols=['mun_code', 'poblacion', 'renta_uc', 'edad_media', 'mayores65', 'extranjeros', 'estudios_sup_2021', 'paro_2021'])
_c24 = {f['mun_code'] for f in S}
assert len(_c24 & set(_m.mun_code)) == 24


def _pond(df, v):
    ok = df[v].notna() & df.poblacion.notna()
    return float((df.loc[ok, v] * df.loc[ok, 'poblacion']).sum() / df.loc[ok, 'poblacion'].sum())


PERFIL = {v: (_pond(_m[_m.mun_code.isin(_c24)], v), _pond(_m, v)) for v in
          ('renta_uc', 'edad_media', 'mayores65', 'extranjeros', 'estudios_sup_2021', 'paro_2021')}
POB24 = int(_m[_m.mun_code.isin(_c24)].poblacion.sum())

# Cuántos siguen acertando de una elección a la siguiente (actualidad/src/historia/datos.json, D['ohio']['supervivientes'])
SUP = json.load(open(RAIZ / 'actualidad/src/historia/datos.json', encoding='utf-8'))['ohio']['supervivientes']
CAMBIO = [2, 6, 8, 10, 13, 15]   # índices de 1982, 1996, 2004, 2011, abril de 2019 y 2023: cambia el partido ganador
assert len(SUP) == 16 and SUP[-1] == 24
TASA = [100 * SUP[i] / SUP[i - 1] for i in range(1, 16)]
T_CAMBIO = [TASA[i - 1] for i in CAMBIO]
T_IGUAL = [TASA[i - 1] for i in range(1, 16) if i not in CAMBIO]
PIERDE_MIN = min(SUP[i - 1] - SUP[i] for i in range(1, 16))
assert PIERDE_MIN >= 1

ord_ = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1]
cuerpo = f'''
<p data-tipo="dato">De los 7.870 municipios con resultados en las 16 elecciones generales desde 1977, solo <strong>24</strong> han votado siempre como primera fuerza al partido que ganó en España, como contamos en {L("plasencia-acierta-siempre", "la pieza de Plasencia")}. El domingo 29 votan por decimoséptima vez. Y en varios de ellos la racha depende de muy pocos votos: en 2023, el PP ganó en <strong>Ayerbe</strong> (Huesca) por {n(dif(M["Ayerbe"]))} votos, en Biescas (Huesca) por {n(dif(M["Biescas"]))}, en Los Navalmorales (Toledo) por {n(dif(M["Los Navalmorales"]))} y en Jaca (Huesca) por {n(dif(JA))}.</p>
{g_margen}
<h2>Los seis que están en el filo</h2>
<p data-tipo="dato">En seis de los 24, la ventaja del PP sobre el PSOE en 2023 fue de menos de tres puntos: Ayerbe ({p(dpt(M["Ayerbe"]))}), Jaca ({p(dpt(JA))}), Los Navalmorales ({p(dpt(M["Los Navalmorales"]))}), Biescas ({p(dpt(M["Biescas"]))}), Villaquilambre, en León ({p(dpt(M["Villaquilambre"]))}), y Plasencia, en Cáceres ({p(dpt(PLA))}). En el conjunto de España, sin el voto exterior, fue de {p(dpt(ESP))} puntos.</p>
<p data-tipo="dato"><strong>Plasencia</strong> es el mayor de los 24, con {n(PLA["censo"])} electores. En 2023 el PP sacó {n(PLA["PP"])} votos y el PSOE, {n(PLA["PSOE"])}: {n(dif(PLA))} de diferencia. Pedro Sánchez tiene previsto un acto allí el viernes a las 12.00, último día de campaña, según <a href="{INFOBAE}">Infobae</a> y <a href="{PORTADA}">La Portada de Extremadura</a>, que cita al PSOE extremeño.</p>
<h2>Jaca, el que más se parece a España</h2>
<p data-tipo="dato">Acertar el ganador no es votar como la media del país, pero Jaca hace las dos cosas. En 2023 dio al PP el {p(pct(JA, "PP"))} %, al PSOE el {p(pct(JA, "PSOE"))} %, a Vox el {p(pct(JA, "VOX"))} % y a Sumar el {p(pct(JA, "SUMAR"))} %. En el conjunto de España fueron el {p(pct(ESP, "PP"))}, el {p(pct(ESP, "PSOE"))}, el {p(pct(ESP, "VOX"))} y el {p(pct(ESP, "SUMAR"))} %.</p>
{g_jaca}
<h2>Cuatro que empataron</h2>
<p data-tipo="dato">Otros cuatro municipios votaron al ganador en todas las generales menos en una, en la que los dos primeros sacaron los mismos votos: {ord_([f"{f['municipio']} ({f['provincia']}) en {f['empate_en'][:4]}" for f in sorted(EMP, key=lambda f: f['empate_en'])])}. En Belmonte de San José, el PP y el PSOE sacaron {n(next(f for f in EMP if f['municipio'] == 'Belmonte de San José')['PP'])} votos cada uno en 2023. Un empate no es acertar, así que no están en la lista.</p>
<h2>Por qué aciertan, y si seguirán</h2>
<p data-tipo="dato">Los datos no dicen por qué aciertan, pero sí en qué se parecen a España. Tomados juntos, y ponderados por población, los 24 tienen una edad media de {p(PERFIL["edad_media"][0])} años (España, {p(PERFIL["edad_media"][1])}), un {p(100 * PERFIL["mayores65"][0])} % de mayores de 65 (España, {p(100 * PERFIL["mayores65"][1])} %), un {p(100 * PERFIL["estudios_sup_2021"][0])} % de población con estudios superiores ({p(100 * PERFIL["estudios_sup_2021"][1])} %) y un {p(100 * PERFIL["paro_2021"][0])} % de paro en 2021 ({p(100 * PERFIL["paro_2021"][1])} %). Su renta por unidad de consumo es de {n(PERFIL["renta_uc"][0])} euros, frente a {n(PERFIL["renta_uc"][1])}. Donde más se separan es en la población extranjera: un {p(100 * PERFIL["extranjeros"][0])} %, frente al {p(100 * PERFIL["extranjeros"][1])} % del conjunto del país.</p>
<p data-tipo="contexto">También comparten lo que no tienen: ninguno es una gran ciudad (entre los 24 suman {n(POB24)} habitantes) y ninguno está en Cataluña, el País Vasco, Galicia o Canarias, donde los partidos nacionalistas y regionales ganan a menudo en los municipios. Estos parecidos acompañan a los aciertos, pero no los explican: los datos no permiten decir que sean la causa.</p>
<p data-tipo="dato">Sobre si seguirán, la historia de la lista da una pista. En ninguna de las 15 elecciones desde 1979 se ha quedado igual: cada vez ha perdido al menos {PIERDE_MIN}. Cuando el partido ganador en España repitió, siguió acertando entre el {p(min(T_IGUAL))} % y el {p(max(T_IGUAL))} % de los que llevaban pleno. Cuando cambió, entre el {p(min(T_CAMBIO))} % y el {p(max(T_CAMBIO))} %: en 1996, cuando ganó el PP por primera vez, solo siguió uno de cada cuatro; en 2023, algo más de la mitad, {SUP[-1]} de {SUP[-2]}.</p>
<h2>Qué no dicen estos datos</h2>
<p data-tipo="contexto">Que un pueblo haya acertado 16 veces no dice quién ganará el domingo. Con casi 8.000 municipios y 16 elecciones, es esperable que unos pocos coincidan siempre por acumulación de casualidades. Y que el PP ganara por poco en 2023 tampoco anticipa que vaya a perder: solo indica qué municipios pueden salir de la lista con un cambio pequeño. La mitad, {ARAGON}, están en Aragón. Entre los 24 suman {n(ELECT)} electores.</p>
<p data-tipo="contexto">La noche del 29N, en la página de <a href="{BASE}elecciones/resultados-elecciones-generales-2026/">resultados de las elecciones generales 2026</a> se podrá ver, municipio a municipio, si los 24 siguen acertando. Esta pieza se actualizará con el resultado.</p>
'''

preguntas = [
    ('¿Qué pueblos de España siempre aciertan en las elecciones generales?',
     f'24 de 7.870 municipios han votado siempre como primera fuerza al partido que ganó en España en las 16 generales desde 1977. El mayor es Plasencia (Cáceres), con {n(PLA["censo"])} electores; la mitad están en Aragón.'),
    ('¿Por cuántos votos ganó el PP en Plasencia en 2023?',
     f'Por {n(dif(PLA))}: {n(PLA["PP"])} votos frente a {n(PLA["PSOE"])} del PSOE, {p(dpt(PLA))} puntos.'),
    ('¿Qué pueblo que siempre acierta ganó el PP por menos votos en 2023?',
     f'Ayerbe (Huesca), por {n(dif(M["Ayerbe"]))} votos: {n(M["Ayerbe"]["PP"])} frente a {n(M["Ayerbe"]["PSOE"])}.'),
    ('¿Sirven estos pueblos para saber quién ganará el 29N?',
     'No. Que acierten siempre es en buena parte casualidad acumulada; no es una predicción.'),
]
enlaces = (f'{L("plasencia-acierta-siempre", "Plasencia acierta siempre")} · '
           f'<a href="{BASE}elecciones/resultados-elecciones-generales-2026/">Resultados de las elecciones generales 2026</a>')
foot = ('Datos: Ministerio del Interior, resultados por municipio de las elecciones generales de 1977 a 2023. '
        'Perfil: INE (padrón y Atlas de Distribución de Renta de los Hogares, 2023; censo de 2021). Cálculo: actualidad/src/resumenes/pueblos_aciertan.py.')
DATOS = {'SUP': SUP, 'PERFIL': PERFIL, 'POB24': POB24, 'S': [[f['municipio'], f['provincia'], f['censo'], f['PP'], f['PSOE'], f['VOX'], f['SUMAR'], f['votos_candidaturas']] for f in S],
         'EMP': [[f['municipio'], f['provincia'], f['empate_en'], f['PP'], f['PSOE']] for f in EMP],
         'ESP': [ESP['PP'], ESP['PSOE'], ESP['VOX'], ESP['SUMAR'], ESP['votos_candidaturas']]}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

pieza(SLUG, 'Los pueblos que siempre aciertan',
      'Los pueblos que siempre aciertan se juegan la racha por un puñado de votos: en Ayerbe, el PP ganó en 2023 por 2',
      f'Solo 24 municipios han votado al ganador en las 16 elecciones generales. En seis, el PP ganó en 2023 por menos de tres puntos; en Plasencia, el mayor, por {n(dif(PLA))} votos.',
      '26 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(len(S), [(f['municipio'], dif(f), round(dpt(f), 1)) for f in FILO], round(dpt(ESP), 1))
