"""«El cinturón rojo de Madrid» (4-11-2026): el PSOE pasó de ganar en 16 de los 24 municipios madrileños de más de
50.000 habitantes en noviembre de 2019 a ganar en 4 en julio de 2023, aunque subió en los 16.

Cifras: generales por municipio (generales-2026/descargas/municipios_historico.csv hasta 2000 y municipios.csv desde 2004),
porcentaje sobre votos a candidaturas y sin voto exterior (CERA), como los resultados oficiales por municipio de Público.
Población: padrón más reciente de la descarga (la misma lista de 24 municipios en todas las elecciones).
En 2015 la familia «Sumar / Podemos / IU» suma Podemos e IU, que fueron por separado: esa elección no entra en el recuento
de municipios ganados (el ganador de la familia no es el de ninguna lista). En noviembre de 2019 pasa lo mismo: la familia
suma Unidas Podemos y Más País, que también fueron por separado, así que el ganador de 2019-N sale de los votos de cada lista
(datos/madrid_congreso_2019_11_listas.csv, microdatos de Interior vía dadosdelaplace/pollspaindata, sin CERA): Rivas lo ganó el PSOE.
Coslada 2023: en nuestra descarga el PP tiene 14.438 votos; el resultado oficial publicado es 14.437 frente a 14.430 del PSOE,
siete votos, y es el que da el texto (externa, Público).
Modelo de encuestas: previsiones/datos/publico/escenario-base.json del 3-11-2026, congelado en la pieza.
Uso, desde la raíz: python3 actualidad/src/resumenes/cinturon_madrid.py
"""
import json
import math

import pandas as pd

from comun import BASE, COLOR, RAIZ, esc, figura, n, barras, pieza

A = BASE + 'actualidad/'
p = lambda v: n(v, 1)
F = ['PP', 'PSOE', 'VOX', 'SUMAR', 'CS', 'UPYD', 'ERC', 'JUNTS', 'PNV', 'BILDU', 'BNG', 'CC', 'UCD', 'CDS', 'OTROS']
EL = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03', '2004_03', '2008_03',
      '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
ANIO = {'2019_04': '2019-A', '2019_11': '2019-N'}
an = lambda e: ANIO.get(e, e[:4])
COLOR_CS = '#eb6109'

h = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios_historico.csv', dtype={'mun_code': str})
m = pd.read_csv(RAIZ / 'generales-2026/descargas/municipios.csv', dtype={'mun_code': str})
h, m = h[h.mun_code.str[:2] == '28'], m[m.mun_code.str[:2] == '28'].copy()
assert len(m) == 179
a, b = '2019_11', '2023_07'


# Noviembre de 2019, lista a lista (la familia suma Unidas Podemos y Más País)
LIS = pd.read_csv(RAIZ / 'actualidad/src/resumenes/datos/madrid_congreso_2019_11_listas.csv', dtype={'mun_code': str})
psoe_l = LIS[LIS.lista == 'PSOE'].set_index('mun_code').votos
assert (psoe_l.reindex(m.mun_code).fillna(0).values == m[f'{a}_vPSOE'].values).all()
GAN19 = LIS.sort_values('votos').groupby('mun_code').tail(1).set_index('mun_code').lista.replace({'PODEMOS-IU': 'SUMAR'}).to_dict()
assert all(GAN19[c] == g for c, g in zip(m.mun_code, m[f'{a}_gana']) if g != 'SUMAR')
assert GAN19['28123'] == 'PSOE'   # Rivas: PSOE 13.812, Unidas Podemos 10.558, Más País 4.131
m['g19'] = m.mun_code.map(GAN19)
GRANDES = m[m.poblacion >= 50000].copy()
assert len(GRANDES) == 24
COD24 = set(GRANDES.mun_code)

# Ganador en cada municipio grande, elección a elección (2015 fuera: la familia suma Podemos e IU)
GANA24 = {}
for e in EL:
    if e == '2015_12':
        continue
    d = (h if e < '2004' else m)
    d = d[d.mun_code.isin(COD24)]
    GANA24[an(e)] = {k: int(v) for k, v in (d.g19 if e == a else d[f'{e}_gana']).value_counts().items()}
assert GANA24['2019-N'] == {'PSOE': 16, 'PP': 7, 'VOX': 1}, GANA24['2019-N']
assert GANA24['2023'] == {'PP': 20, 'PSOE': 4}, GANA24['2023']
assert GANA24['2011'] == {'PP': 24} and GANA24['2016'] == {'PP': 22, 'SUMAR': 2}
PSOE24 = {k: v.get('PSOE', 0) for k, v in GANA24.items()}
RACHAS_PP = [k for k, v in GANA24.items() if v.get('PP', 0) > 12]
assert RACHAS_PP == ['1996', '2000', '2008', '2011', '2016', '2023'], RACHAS_PP
RACHAS_PP = RACHAS_PP[:-1]
assert max(PSOE24.values()) == 21 and PSOE24['1982'] == 21

# Los 15 que ganó el PSOE en 2019-N
Q = GRANDES[GRANDES.g19 == 'PSOE']
tot = lambda d, e: sum(d[f'{e}_v{f}'].sum() for f in F)
cuota = lambda d, e, k: float(d[f'{e}_v{k}'].sum() / tot(d, e) * 100)
BLOQUE = {e: {k: round(cuota(Q, e, k), 2) for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'CS')} for e in (a, b)}
SUBE_PSOE = int(sum((r[f'{b}_vPSOE'] / sum(r[f'{b}_v{f}'] for f in F)) > (r[f'{a}_vPSOE'] / sum(r[f'{a}_v{f}'] for f in F))
                    for _, r in Q.iterrows()))
assert SUBE_PSOE == 16 == len(Q)
# las sumas, de las cifras ya redondeadas a un decimal que da el texto, para que cuadren a la vista
r1 = lambda v: round(v + 1e-9, 1)
DER = {e: round(r1(BLOQUE[e]['PP']) + r1(BLOQUE[e]['VOX']) + r1(BLOQUE[e]['CS']), 1) for e in (a, b)}
IZQ = {e: round(r1(BLOQUE[e]['PSOE']) + r1(BLOQUE[e]['SUMAR']), 1) for e in (a, b)}


def fila(nombre):
    r = m[m.municipio == nombre].iloc[0]
    out = {'pob': int(r.poblacion), 'g19': r.g19, 'g23': r[f'{b}_gana']}
    for e, s in ((a, '19'), (b, '23')):
        t = sum(r[f'{e}_v{f}'] for f in F)
        for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'CS'):
            out[f'{k}{s}'] = round(r[f'{e}_v{k}'] / t * 100, 2)
        out[f'v{s}'] = {k: int(r[f'{e}_v{k}']) for k in ('PP', 'PSOE')}
    return out


NOMBRES = ['Fuenlabrada', 'Parla', 'Leganés', 'Getafe', 'Coslada', 'Pinto', 'Móstoles', 'Alcorcón', 'Alcalá de Henares',
           'Torrejón de Ardoz', 'Rivas-Vaciamadrid', 'Valdemoro', 'Madrid', 'Pozuelo de Alarcón']
MUN = {k: fila(k) for k in NOMBRES}
assert all(MUN[k]['g23'] == 'PSOE' for k in ('Fuenlabrada', 'Parla', 'Leganés', 'Getafe'))
assert MUN['Coslada']['g23'] == 'PP' and MUN['Coslada']['v23'] == {'PP': 14438, 'PSOE': 14430}
assert MUN['Rivas-Vaciamadrid']['g19'] == 'PSOE' and MUN['Valdemoro']['g19'] == 'VOX'
COSLADA_OFICIAL = {'PP': 14437, 'PSOE': 14430}   # Público, escrutinio al 100 %; nuestra descarga da 14.438 al PP

# Toda la Comunidad: municipios ganados
C19 = {k: int(v) for k, v in m.g19.value_counts().items()}
C23 = {k: int(v) for k, v in m[f'{b}_gana'].value_counts().items()}
assert C19 == {'PSOE': 68, 'VOX': 61, 'PP': 47, 'SUMAR': 3} and C23 == {'PP': 158, 'PSOE': 19, 'SUMAR': 2}, (C19, C23)
POB24 = int(GRANDES.poblacion.sum())
POBT = int(m.poblacion.sum())
POB4 = int(GRANDES[GRANDES[f'{b}_gana'] == 'PSOE'].poblacion.sum())

# Modelo de encuestas del 3-11-2026 (congelado)
esc_ = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
meta = json.load(open(RAIZ / 'previsiones/datos/publico/meta.json'))
assert meta['generado'] == '2026-11-03', meta['generado']
v28 = esc_['provincias']['28']
MODELO = {l['lista']: {'voto': l['voto'], 'esc': l['escanos'], 'p1': round(l['p_primera'] * 100, 1)} for l in v28['listas'] if l['voto'][1] >= 2}
assert v28['escanos_total'] == 38
assert MODELO['PP']['voto'][1] == 37.5 and MODELO['PSOE']['voto'][1] == 23.5 and MODELO['Vox']['voto'][1] == 21.4, MODELO
SIMS = meta['simulaciones']
PROV23 = {k: round(cuota(m, b, k), 2) for k in ('PP', 'PSOE')}
assert round(PROV23['PSOE'], 1) == 28.1
assert max(v for k, v in PSOE24.items() if k > '1986') == PSOE24['2019-A'] == 18 and PSOE24['1986'] == 19

# --- Mapa de municipios (geometría de generales-2026/data/municipios.json) ---
G = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
COLM = {'PSOE': COLOR['PSOE'], 'PP': COLOR['PP'], 'VOX': COLOR['Vox'], 'SUMAR': COLOR['Sumar']}
ETQ = {'PSOE': 'PSOE', 'PP': 'PP', 'VOX': 'Vox', 'SUMAR': 'Unidas Podemos (2019) / Sumar (2023)'}
gan = {a: GAN19, b: dict(zip(m.mun_code, m[f'{b}_gana']))}
nom = dict(zip(m.mun_code, m.municipio))


def anillos():
    S, kx = G['S'], math.cos(math.radians(40.4))
    out = []
    for c, partes in zip(G['cod'], G['poly']):
        if not c.startswith('28'):
            continue
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            out.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    return out


AN = anillos()
XS = [x for _, r in AN for x, _ in r]; YS = [y for _, r in AN for _, y in r]


def mapa(e, W):
    s = W / (max(XS) - min(XS)); H = round((max(YS) - min(YS)) * s)
    camino = {}
    for c, r in AN:
        d = ''.join(('L' if i else 'M') + f'{(x - min(XS)) * s:.1f},{(y - min(YS)) * s:.1f}' for i, (x, y) in enumerate(r))
        camino[c] = camino.get(c, '') + d + 'Z'
    out = ''.join(f'<path d="{d}" fill="{COLM.get(gan[e].get(c), "var(--otros)")}"><title>{esc(nom.get(c, c))}: '
                  f'{esc(ETQ.get(gan[e].get(c), "sin datos"))}</title></path>' for c, d in camino.items())
    return W, H, out


def dos_mapas():
    W = 310
    _, H, m1 = mapa(a, W)
    _, _, m2 = mapa(b, W)
    gap = 20
    return (f'<svg viewBox="0 -30 {2 * W + gap} {H + 30}" role="img" aria-label="Municipios de la Comunidad de Madrid por partido más votado en 2019 y en 2023">'
            f'<text x="0" y="-10" class="lab" style="font-size:16px">Noviembre de 2019</text>'
            f'<g stroke="var(--bg)" stroke-width=".5" stroke-linejoin="round">{m1}</g>'
            f'<text x="{W + gap}" y="-10" class="lab" style="font-size:16px">Julio de 2023</text>'
            f'<g transform="translate({W + gap},0)" stroke="var(--bg)" stroke-width=".5" stroke-linejoin="round">{m2}</g></svg>')


def pares_dec(filas, maximo, etiqueta, nombres, W=640, ml=110):
    """Como comun.pares, con un decimal: filas = [(nombre, v1, v2, color)]."""
    alto = 40
    H = alto * len(filas) + 8
    x = lambda v: ml + v / maximo * (W - ml - 90)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom_, v1, v2, col) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 22}" text-anchor="end" class="lab">{esc(nom_)}</text>')
        for k, (v, op) in enumerate(((v1, .38), (v2, 1))):
            yy = y + 4 + k * 16
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="13" fill="{col}" fill-opacity="{op}" rx="2">'
                       f'<title>{esc(nom_)}, {esc(nombres[k])}: {p(v)} %</title></rect>')
            out.append(f'<text x="{x(v) + 6:.1f}" y="{yy + 11}">{p(v)} %{" (" + nombres[k] + ")" if i == 0 else ""}</text>')
    out.append('</svg>')
    return ''.join(out)


SIN_CERA = 'Porcentaje sobre votos a candidaturas, sin voto exterior (CERA).'
g_mapa = figura('De un mapa rojo, azul y verde a uno casi todo azul',
                'Partido más votado en cada uno de los 179 municipios de la Comunidad de Madrid en las generales de noviembre de 2019 y de julio de 2023',
                dos_mapas(), 'Fuente: Ministerio del Interior, resultados por municipio. En 2019, ganador por lista: Unidas Podemos y Más País fueron por separado.',
                [('PSOE', COLOR['PSOE']), ('PP', COLOR['PP']), ('Vox', COLOR['Vox']), ('Unidas Podemos / Sumar', COLOR['Sumar'])],
                (['Partido', 'Municipios en 2019-N', 'Municipios en 2023'],
                 [[ETQ[k], str(C19.get(k, 0)), str(C23.get(k, 0))] for k in ('PP', 'PSOE', 'VOX', 'SUMAR')]))
AN24 = list(GANA24)
g_serie = figura('El PSOE, en los grandes municipios de Madrid', 'Municipios de más de 50.000 habitantes (24) donde el PSOE fue el más votado en cada elección general',
                 barras([(t, PSOE24[t], COLOR['PSOE'], str(PSOE24[t])) for t in AN24], 24, 'Municipios grandes ganados por el PSOE', ml=70, alto=24),
                 'Fuente: Ministerio del Interior. Los mismos 24 municipios en todas las elecciones (Tres Cantos no existía hasta 1991, y de 1977 nuestra serie no tiene los datos de Fuenlabrada). '
                 'Falta 2015: nuestra serie suma Podemos e IU, que fueron por separado, y no permite saber quién ganó cada municipio.', None,
                 (['Elección', 'PSOE', 'PP', 'Otros'], [[t, str(PSOE24[t]), str(GANA24[t].get('PP', 0)),
                                                       str(sum(v for k, v in GANA24[t].items() if k not in ('PSOE', 'PP')))] for t in AN24]))
FIL = [('PP', 'PP', COLOR['PP']), ('PSOE', 'PSOE', COLOR['PSOE']), ('SUMAR', 'Unidas Podemos, Más País / Sumar', COLOR['Sumar']),
       ('VOX', 'Vox', COLOR['Vox']), ('CS', 'Ciudadanos', COLOR_CS)]
g_bloque = figura('El PSOE subió; el PP subió mucho más', f'Voto en los {len(Q)} municipios grandes que ganó el PSOE en noviembre de 2019, sumados',
                  pares_dec([(t if k != 'SUMAR' else 'Izq. del PSOE', BLOQUE[a][k], BLOQUE[b][k], c) for k, t, c in FIL], 40,
                            'Voto en 2019 y 2023 en esos municipios', ['2019-N', '2023'], ml=120),
                  'Fuente: Ministerio del Interior. «Izq. del PSOE»: Unidas Podemos y Más País en 2019, Sumar en 2023. Ciudadanos no se presentó en 2023. ' + SIN_CERA,
                  [('Noviembre de 2019 (claro)', 'var(--otros)'), ('Julio de 2023', 'var(--fg)')],
                  (['Partido', '2019-N', '2023'], [[t, p(BLOQUE[a][k]), p(BLOQUE[b][k])] for k, t, _ in FIL]))
ORD = sorted(MODELO, key=lambda k: -MODELO[k]['voto'][1])
NOMM = lambda k: 'Frente Amplio (Sumar)' if k == 'Sumar' else k
g_modelo = figura('Madrid, en la media de encuestas',
                  f'Voto estimado en la circunscripción de Madrid para el 29N (modelo de Mapa Electoral, {n(SIMS)} simulaciones, 3 de noviembre)',
                  barras([(NOMM(k), MODELO[k]['voto'][1], COLOR.get(k, COLOR['Otros']), f'{p(MODELO[k]["voto"][1])} % · {MODELO[k]["esc"][1]} esc.') for k in ORD],
                         40, 'Voto estimado en Madrid', ml=170),
                  'Fuente: modelo de Mapa Electoral con la media de las encuestas nacionales repartida por provincia. No es una encuesta de Madrid ni da datos por municipio.', None,
                  (['Lista', 'Voto', 'Intervalo 80 %', 'Escaños', 'Horquilla', 'Primero en'],
                   [[NOMM(k), p(MODELO[k]['voto'][1]), f'{p(MODELO[k]["voto"][0])}-{p(MODELO[k]["voto"][2])}', str(MODELO[k]['esc'][1]),
                     f'{MODELO[k]["esc"][0]}-{MODELO[k]["esc"][2]}', f'{n(MODELO[k]["p1"])} %'] for k in ORD]))

L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
MU = lambda path, t: f'<a href="{BASE}municipio/madrid/{path}/">{t}</a>'
PUB_COS = 'https://www.publico.es/resultados-elecciones/generales/2023/comunidad-de-madrid/madrid/coslada'
SALTO = 'https://www.elsaltodiario.com/analisis/despertar-derecha-cinturon-rojo-madrid'
ED_LOPEZ = 'https://www.estrelladigital.es/articulo/madrid/oscar-lopez-sera-candidato-psoe-comunidad-madrid-quedarse-rival-primarias/20260712140653448621.html'
U = MUN
DATOS = {'SIMS': SIMS, 'GANA24': GANA24, 'PSOE24': PSOE24, 'BLOQUE': BLOQUE, 'DER': DER, 'IZQ': IZQ, 'SUBE_PSOE': SUBE_PSOE,
         'C19': C19, 'PROV23': PROV23, 'C23': C23, 'POB24': POB24, 'POBT': POBT, 'POB4': POB4, 'MODELO': MODELO, 'MUN': MUN}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
dcos = COSLADA_OFICIAL['PP'] - COSLADA_OFICIAL['PSOE']
assert dcos == 7

cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="dato">En las generales de julio de 2023, el PP ganó en {MU("coslada", "Coslada")} por siete votos: {n(COSLADA_OFICIAL["PP"])} frente a {n(COSLADA_OFICIAL["PSOE"])} del PSOE, según los <a href="{PUB_COS}">resultados oficiales</a>. Cuatro años antes, en noviembre de 2019, el PSOE había sacado allí {n(U['Coslada']['PSOE19'] - U['Coslada']['PP19'])} puntos de ventaja. Coslada fue el más ajustado de los {PSOE24["2019-N"] - PSOE24["2023"]} municipios grandes que el PSOE perdió en la Comunidad de Madrid entre una elección y otra. De los 24 municipios madrileños de más de 50.000 habitantes, el PSOE fue el más votado en {PSOE24["2019-N"]} en 2019 y en {PSOE24["2023"]} en 2023: {MU("fuenlabrada", "Fuenlabrada")}, {MU("parla", "Parla")}, {MU("leganes", "Leganés")} y {MU("getafe", "Getafe")}.</p>
{g_mapa}
<p data-tipo="dato">El cambio se ve en toda la región. En noviembre de 2019, el PSOE ganó en {C19["PSOE"]} de los 179 municipios, Vox en {C19["VOX"]}, el PP en {C19["PP"]} y Unidas Podemos en {C19["SUMAR"]}. En 2023, el PP ganó en {C23["PP"]}, el PSOE en {C23["PSOE"]} y Sumar en {C23["SUMAR"]}. Los cuatro grandes que le quedan al PSOE suman {n(POB4)} habitantes, el {n(POB4 / POBT * 100)} % de la Comunidad.</p>

<h2>El PSOE no bajó</h2>
<p data-tipo="dato">Lo llamativo es que el PSOE no perdió esos municipios porque bajara. En los {len(Q)} grandes que ganó en 2019, subió en los {SUBE_PSOE}: sumados, pasó del {p(BLOQUE[a]["PSOE"])} % al {p(BLOQUE[b]["PSOE"])} % de los votos a candidaturas. En Fuenlabrada llegó al {p(U["Fuenlabrada"]["PSOE23"])} %, desde el {p(U["Fuenlabrada"]["PSOE19"])} %. Lo que cambió fue el PP, que en esos mismos municipios pasó del {p(BLOQUE[a]["PP"])} % al {p(BLOQUE[b]["PP"])} %.</p>
{g_bloque}
<p data-tipo="patron">El crecimiento del PP coincide con la desaparición de Ciudadanos, que en noviembre de 2019 sacó el {p(BLOQUE[a]["CS"])} % en esos {len(Q)} municipios y no se presentó en 2023, y con la bajada de Vox, del {p(BLOQUE[a]["VOX"])} % al {p(BLOQUE[b]["VOX"])} %. PP, Vox y Ciudadanos sumaban el {p(DER[a])} % en 2019; PP y Vox, el {p(DER[b])} % en 2023. A la izquierda pasó lo contrario: el PSOE subió, pero lo que había a su izquierda bajó del {p(BLOQUE[a]["SUMAR"])} % al {p(BLOQUE[b]["SUMAR"])} %, y los dos juntos se quedaron casi igual ({p(IZQ[a])} % y {p(IZQ[b])} %).</p>
<p data-tipo="hipotesis">Una lectura posible es que, más que un vuelco de votantes del PSOE al PP, lo que cambió fue el reparto dentro de cada bloque: la derecha se concentró en el PP y la izquierda en el PSOE, y con bloques casi iguales, el PP pasó por delante en municipios como {MU("mostoles", "Móstoles")}, {MU("alcorcon", "Alcorcón")} o {MU("alcala-de-henares", "Alcalá de Henares")}. Los datos por municipio no siguen a los votantes: no dicen quién votó a quién, solo cómo cambiaron los totales. Para saberlo harían falta encuestas postelectorales como las del CIS.</p>
{g_serie}
<blockquote class="cita"><p>«Mientras que en 2019 la izquierda se imponía en prácticamente todos los vecindarios, independientemente de su nivel de renta, en 2021 sólo ha conseguido hacer esto en las zonas más pobres».</p><footer>Alejandro Solís Rodríguez, politólogo, sobre las autonómicas de 2021 en el cinturón rojo, en <a href="{SALTO}">El Salto</a></footer></blockquote>
<p data-tipo="contexto">El llamado cinturón rojo, los municipios obreros del sur y del corredor del Henares, fue del PSOE en las generales de los años ochenta: en 1982 ganó en {PSOE24["1982"]} de estos 24 municipios. Desde entonces ha ido a rachas. El PP ganó en la mayoría en {", ".join(RACHAS_PP[:-1])} y {RACHAS_PP[-1]}; en 2011, con Mariano Rajoy, en los 24, y en 2016 ningún gran municipio madrileño votó primero al PSOE. 2019 fue un regreso: {PSOE24["2019-A"]} municipios en abril, su mejor resultado desde 1986, y {PSOE24["2019-N"]} en noviembre.</p>

<h2>El 29N</h2>
<p data-tipo="dato">Nuestro modelo, que reparte la media de las encuestas nacionales por provincia y la simula {n(SIMS)} veces, da hoy al PP el {p(MODELO["PP"]["voto"][1])} % en la circunscripción de Madrid, al PSOE el {p(MODELO["PSOE"]["voto"][1])} % y a Vox el {p(MODELO["Vox"]["voto"][1])} %. El PP queda primero en el {n(MODELO["PP"]["p1"])} % de las simulaciones. El modelo no baja a municipios, pero deja al PSOE {p(PROV23['PSOE'] - MODELO['PSOE']['voto'][1])} puntos por debajo de su resultado de 2023 en la provincia, el {p(PROV23['PSOE'])} %.</p>
{g_modelo}
<p data-tipo="contexto">El PSOE madrileño tiene el sur como objetivo. Su candidato a la Comunidad para 2027, el ministro Óscar López, defendió al formalizar su candidatura en julio una reducción de las diferencias entre municipios, barrios y zonas del norte y el sur de la región, y presentó su proyecto en un acto en Fuenlabrada, según <a href="{ED_LOPEZ}">Estrella Digital</a>. Las candidaturas de cada partido por Madrid para el 29N están en las <a href="{BASE}listas-electorales-29n/madrid/">listas del 29N en Madrid</a>.</p>

<h2>Lo que estos datos no dicen</h2>
<p data-tipo="contexto">Los porcentajes de esta pieza son sobre votos a candidaturas y sin el voto de los madrileños que viven en el extranjero, como los resultados oficiales por municipio. En Coslada, nuestra descarga da un voto más al PP que el resultado publicado; el texto usa el oficial. «Municipios grandes» son los 24 que hoy pasan de 50.000 habitantes, con la misma lista en todas las elecciones. 2015 no está en el recuento porque nuestra serie suma Podemos e IU, que se presentaron por separado; en noviembre de 2019, que también suma Unidas Podemos y Más País, el ganador de cada municipio sale de los votos de cada lista. Y el ganador de un municipio no dice cuántos votos pesa: Madrid capital tiene casi la mitad de los habitantes de la Comunidad.</p>'''

preguntas = [
    ('¿Quién ganó las elecciones generales de 2023 en Coslada?', f'El PP, por siete votos: {n(COSLADA_OFICIAL["PP"])} frente a {n(COSLADA_OFICIAL["PSOE"])} del PSOE, según los resultados oficiales. En noviembre de 2019 había ganado el PSOE.'),
    ('¿En qué municipios grandes de Madrid ganó el PSOE en 2023?', 'En cuatro de los 24 que tienen más de 50.000 habitantes: Fuenlabrada, Parla, Leganés y Getafe. En noviembre de 2019 había ganado en 16.'),
    ('¿Qué dicen las encuestas del 29N en Madrid?', f'En la media de encuestas de Mapa Electoral del 3 de noviembre, el PP tiene el {p(MODELO["PP"]["voto"][1])} % en la provincia, el PSOE el {p(MODELO["PSOE"]["voto"][1])} % y Vox el {p(MODELO["Vox"]["voto"][1])} %. Las cifras del día están en la <a href="{BASE}encuestas/madrid/">encuesta de Madrid</a>.'),
]
enlaces = (f'<a href="{BASE}elecciones/madrid/">Elecciones en la Comunidad de Madrid</a> · <a href="{BASE}municipio/madrid/">Los municipios de Madrid</a> · '
           f'<a href="{BASE}encuestas/madrid/">Encuesta de Madrid</a> · {L("madrid-barrio-a-barrio-29n", "Madrid capital, barrio a barrio")} · '
           f'{L("psoe-madrid-municipales-generales", "El PSOE en Madrid: municipales frente a generales")} · '
           f'{L("acampada-sol-alquiler-madrid-distritos-29n", "El alquiler sube más deprisa en el sur de Madrid")}')
foot = ('Datos: Ministerio del Interior, generales de 1977 a 2023 por municipio; resultado oficial de Coslada en 2023 (Público); '
        'modelo de encuestas de Mapa Electoral del 3 de noviembre de 2026. Cálculo: actualidad/src/resumenes/cinturon_madrid.py.')

pieza('cinturon-rojo-madrid-29n', 'El cinturón rojo de Madrid',
      f'El PP ganó Coslada por siete votos: el PSOE pasó de ganar en {PSOE24["2019-N"]} de los 24 grandes municipios de Madrid a {PSOE24["2023"]}, aunque subió en todos',
      f'Fuenlabrada, Parla, Leganés y Getafe son lo que queda del cinturón rojo en las generales. En los {SUBE_PSOE} municipios que el PSOE ganaba en 2019, '
      f'subió del {p(BLOQUE[a]["PSOE"])} % al {p(BLOQUE[b]["PSOE"])} %; el PP, del {p(BLOQUE[a]["PP"])} % al {p(BLOQUE[b]["PP"])} %, tras la desaparición de Ciudadanos.',
      '4 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
