"""«La generación de 2008» (15-11-2026): los nacidos en 2008, el año con más nacimientos en España desde 1981, que estrenan
su voto en unas generales el 29N, y el resto de electores que votan por primera vez en unas generales.

Datos (actualidad/src/resumenes/datos/generacion_2008.json, descargados del INE y del CIS el 15-11-2026):
- Censo electoral: nota de prensa del INE del 9-10-2026 (EG2026) y, para 2023, la del 5-6-2023 (elecgral_jul2023.pdf).
- Nacidos en 2008 que viven en cada provincia a 1 de enero de 2025: INE, Estadística Continua de Población (ECP), tabla 56946,
  «generación (edad a 31 de diciembre)»: a 1-1-2025, la generación de 16 años es la nacida en 2008 (la de 0 años, la de 2024).
  Nacionalidad y país de nacimiento, solo para el total nacional (tabla 56939).
- Nacimientos: INE, Estadística de Nacimientos, tabla 6524 (por residencia de la madre, mensual desde 1975).
- Municipios: INE, Estadística del Padrón Continuo, tabla 33575, a 1-1-2022 (el último año con la edad año a año por municipio):
  personas de 13 años, que son casi todas nacidas en 2008.
- CIS, estudio 3584 (preelectoral, campo del 7 al 30 de octubre de 2026), hoja «Edad» del Excel multi_A.
- Último escaño de 2023: pieza «Seis escaños que se decidieron por menos de mil votantes» (objeto F).
Uso, desde la raíz: python3 actualidad/src/resumenes/generacion_2008.py
"""
import json
import re
import sys
import unicodedata
from datetime import date

from comun import BASE, RAIZ, SRC, barras, esc, figura, mapa_provincias, n, pieza

sys.path.insert(0, str(RAIZ / 'src'))
from territorios_rutas import PROV_NOMBRE, PROV_SLUG, slug as slug_t  # noqa: E402

SLUG = 'generacion-2008-primer-voto-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
D0 = json.load(open(RAIZ / 'actualidad/src/resumenes/datos/generacion_2008.json'))
INE_NOTA = 'https://www.ine.es/dyngs/Prensa/es/EG2026.htm'
INE_NOTA23 = 'https://www.ine.es/prensa/elecgral_jul2023.pdf'
EFE = 'https://www.infobae.com/espana/agencias/2026/10/09/mas-de-387-millones-de-electores-estan-llamados-a-votar-en-las-elecciones-del-29n/'
ECP = 'https://www.ine.es/jaxiT3/Tabla.htm?t=56946'
ECP_NAC = 'https://www.ine.es/jaxiT3/Tabla.htm?t=56939'
NACIM = 'https://www.ine.es/jaxiT3/Tabla.htm?t=6524'
PADRON = 'https://www.ine.es/jaxiT3/Tabla.htm?t=33575'
XLSX = 'https://www.cis.es/documents/d/guest/3584-multi_A-xlsx'
NOM = dict(PROV_NOMBRE)
CORTO = {'Santa Cruz de Tenerife': 'S. C. de Tenerife', 'Alicante/Alacant': 'Alicante', 'Valencia/València': 'Valencia',
         'Castellón/Castelló': 'Castellón', 'Araba/Álava': 'Álava', 'Illes Balears': 'Baleares', 'Balears, Illes': 'Baleares'}
nom = lambda c: CORTO.get(NOM[c], NOM[c])
orden_alfa = lambda cs: sorted(cs, key=lambda c: unicodedata.normalize('NFKD', nom(c)))

# ---------- Censo electoral (INE) ----------
CEN = D0['censo26']
TOTAL26, CER26, CERA26 = CEN['Total general']
assert (TOTAL26, CER26, CERA26) == (38728356, 35958711, 2769645)
PRIMEROS26, PRIMEROS23 = 1615127, 1639179      # notas de prensa del INE (9-10-2026 y 5-6-2023)
CER23 = 35141122
assert sum(CEN[c][1] for c in CEN if re.fullmatch(r'\d\d', c)) == CER26
DIAS26 = (date(2026, 11, 29) - date(2023, 7, 23)).days
DIAS23 = (date(2023, 7, 23) - date(2019, 11, 10)).days
DIA26, DIA23 = PRIMEROS26 / DIAS26, PRIMEROS23 / DIAS23
PCT_PRIMEROS = 100 * PRIMEROS26 / CER26

# ---------- Nacimientos ----------
NAC = {int(k): v for k, v in D0['nac_anual'].items()}
assert NAC[2008] == 519779 and len(NAC) == 50
MAS_QUE_2008 = sorted(y for y in NAC if NAC[y] > NAC[2008])
assert MAS_QUE_2008 == list(range(1975, 1982))      # solo de 1975 a 1981 hubo más nacimientos
DESPUES = max(v for y, v in NAC.items() if y > 2008)
assert NAC[2009] == DESPUES
MES = {int(k): v for k, v in D0['nac08_mes'].items()}
assert sum(MES.values()) == NAC[2008]
DIC08 = MES[12]
SUBE_2008 = 100 * (NAC[2008] / NAC[2007] - 1)
VS_2024 = 100 * (NAC[2008] / NAC[2024] - 1)
assert all(NAC[y] > NAC[y - 1] for y in range(1999, 2009)) and NAC[1998] < NAC[1997]
assert [y for y in range(2009, 2025) if NAC[y] >= NAC[y - 1]] == [2014]
MIN = min(NAC.items(), key=lambda kv: kv[1])
assert MIN[0] == 2024

# ---------- Generación de 2008 hoy (ECP, 1-1-2025) ----------
N = D0['nacional']
G = lambda gen, nac='Total', pais='Total', sexo='Total': N[f'{sexo}|{gen}|{nac}|{pais}']
GEN08 = G('16 años')
assert GEN08 == D0['gen08_total'] == 551743
ESP08 = G('16 años', 'Española')
NACIDOS_ESP = G('16 años', pais='España')
NACIDOS_FUERA = G('16 años', pais='Extranjero')
EXTR08 = G('16 años', 'Extranjera')
assert ESP08 + EXTR08 == GEN08 and NACIDOS_ESP + NACIDOS_FUERA == GEN08
ESP_COH = {2008: ESP08, 2007: G('17 años', 'Española'), 2006: G('18 años', 'Española'), 2005: G('19 años', 'Española')}
assert max(ESP_COH, key=ESP_COH.get) == 2008
CREC_NAC = 100 * (GEN08 / NAC[2008] - 1)
HOMBRES08, MUJERES08 = G('16 años', sexo='Hombres'), G('16 años', sexo='Mujeres')
assert HOMBRES08 + MUJERES08 == GEN08

GP, POB, NP = D0['gen08'], D0['pob25'], D0['nac08']
assert sum(GP.values()) == GEN08
PESO = {c: 100 * GP[c] / POB[c] for c in GP}
PESO_ESP = 100 * GEN08 / D0['pob25_total']
VAR = {c: 100 * (GP[c] / NP[c] - 1) for c in GP}
MAS_PESO = sorted(GP, key=lambda c: -PESO[c])
MENOS_PESO = sorted(GP, key=lambda c: PESO[c])
GANA = sorted(GP, key=lambda c: -VAR[c])
PIERDE = [c for c in GP if VAR[c] < 0]
assert orden_alfa(PIERDE) == ['13', '23']        # Ciudad Real y Jaén: hoy viven menos nacidos en 2008 de los que nacieron allí
assert MAS_PESO[:6] == ['52', '51', '41', '30', '45', '19'] and MENOS_PESO[:5] == ['49', '27', '32', '24', '34']
MAD_VAR = VAR['28']
assert sorted(GP, key=lambda c: -GP[c])[:5] == ['28', '08', '46', '41', '03']
assert sum(VAR[c] > 0 for c in GP) == 50

# ---------- Municipios (padrón 2022, 13 años) ----------
MUN = D0['mun22']
TOTAL13 = D0['total13_2022']
UMBRAL = 5000


def nombre_mun(t):
    t = t.split(' ', 1)[1]
    t = t.split('/')[0].strip() if '/' in t and '(' not in t else t
    m = re.match(r'(.*), (La|El|Los|Las|L\'|A|O|Os|As|Es|Sa|Ses|Els|Les)$', t)
    return f'{m.group(2)} {m.group(1)}'.replace("L' ", "L'") if m else t


def enlace_mun(t):
    cod, nm = t[:2], nombre_mun(t)
    for cand in (slug_t(nm), slug_t(t.split(' ', 1)[1])):
        if (RAIZ / 'municipio' / PROV_SLUG[cod] / cand).is_dir():
            return f'<a href="{BASE}municipio/{PROV_SLUG[cod]}/{cand}/">{esc(nm)}</a>'
    return esc(nm)


corto_mun = lambda k: re.sub(r' \(.*', '', nombre_mun(k).split('/')[0]).strip()
GRANDES = {k: v for k, v in MUN.items() if v[1] >= UMBRAL}
PM = {k: 100 * v[0] / v[1] for k, v in GRANDES.items()}
MUN_MAS = sorted(GRANDES, key=lambda k: -PM[k])
MUN_MENOS = sorted(GRANDES, key=lambda k: PM[k])
PESO13 = 100 * TOTAL13 / D0['pob2022']
assert [k[:2] for k in MUN_MAS[:5]] == ['28', '41', '37', '17', '50']
assert MUN_MAS[0].startswith('28177') and MUN_MENOS[0].startswith('15043')
MAD13, BCN13 = MUN['28079 Madrid'][0], MUN['08019 Barcelona'][0]
SOBRE2 = [k for k in GRANDES if PM[k] >= 2]
assert len(SOBRE2) == 1

# ---------- Último escaño de 2023 ----------
F = json.loads(re.search(r'const F=(\{.*?\});', (SRC / 'escanos-en-el-filo-29n.html').read_text(encoding='utf-8'), re.S).group(1))
assert len(F) == 52
SUPERA = sorted([c for c in F if F[c]['f'] < GP[c]], key=lambda c: F[c]['f'])
assert len(SUPERA) == 21
CERCA = sorted(F, key=lambda c: F[c]['f'])[:10]

# ---------- CIS (18 a 24 años) ----------
C = D0['cis_3584_edad']
COLS = C['columnas']
V = C['P5a_voto_simpatia']
J = 1      # columna 18-24
assert COLS[J] == '18-24'
NJ = C['P5a_voto_simpatia']['(N)'][J]
VOX_J, PSOE_J, PP_J = V['VOX'][J], V['PSOE'][J], V['PP'][J]
assert VOX_J > PSOE_J > PP_J
VOX_T, PSOE_T, PP_T = V['VOX'][0], V['PSOE'][0], V['PP'][0]
FA_J, FA_T = V['Frente Amplio (CHA-FA en Aragón y Comuns-FA en Cataluña)'][J], V['Frente Amplio (CHA-FA en Aragón y Comuns-FA en Cataluña)'][0]
SALF_J, SALF_T = V['Se Acabó la Fiesta'][J], V['Se Acabó la Fiesta'][0]
VOX_PRIMERO = [COLS[i] for i in range(1, 8) if V['VOX'][i] == max(V['PSOE'][i], V['PP'][i], V['VOX'][i])]
assert VOX_PRIMERO == ['18-24', '25-34'], VOX_PRIMERO      # en 35-44 Vox (23,9) queda por debajo del PSOE (24,6)
assert all(V['PSOE'][i] > max(V['PP'][i], V['VOX'][i]) for i in range(3, 8))
R1 = C['P1_primer_lugar']
REDES_J, TV_J, REDES_T, TV_T, RADIO_J = R1['Redes sociales'][J], R1['Televisión'][J], R1['Redes sociales'][0], R1['Televisión'][0], R1['Radio'][J]
RS = C['P1a_red']
NRS = RS['(N)'][J]
TIKTOK_J, INSTA_J, X_J, FB_J, TIKTOK_T = RS['TikTok'][J], RS['Instagram'][J], RS['Twitter/X'][J], RS['Facebook'][J], RS['TikTok'][0]
assert sorted(RS, key=lambda k: -RS[k][0] if k != '(N)' else 0)[:2] == ['Instagram', 'Facebook']
PR = C['P2_probabilidad']
SEG_J, SEG_T = PR['10 Con toda seguridad, iría a votar'][J], PR['10 Con toda seguridad, iría a votar'][0]
SEG_MIN = min(range(1, 8), key=lambda i: PR['10 Con toda seguridad, iría a votar'][i])
assert COLS[SEG_MIN] == '18-24'
IDE = C['C3_ideologia']
DER_J, DER_T = IDE['10 Derecha'][J], IDE['10 Derecha'][0]
assert DER_J < DER_T
IZQ_J, IZQ_T, MED_J, MED_T = IDE['1 Izquierda'][J], IDE['1 Izquierda'][0], IDE['Media'][J], IDE['Media'][0]
ERRJ = 2 * (0.25 / NJ) ** .5 * 100

# ---------- Gráficos ----------
ROJO, NARANJA, GRIS, MARRON = '#d62728', '#f08c3a', '#a9a9a9', '#8f4410'   # fijos: se leen igual en modo claro y oscuro


def dobles(filas, maximo, W=400, ml=125, alto=38):
    """Dos barras por provincia con colores fijos: votos que faltaban (gris) y nacidos en 2008 (marrón)."""
    H = alto * len(filas) + 6
    x = lambda v: ml + v / maximo * (W - ml - 52)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Votos que faltaron para el último escaño frente a nacidos en 2008">']
    for i, (nm, a, b) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 6}" y="{y + 20}" text-anchor="end" class="lab">{esc(nm)}</text>')
        for k, (v, col, t) in enumerate(((a, GRIS, 'votos que faltaban'), (b, MARRON, 'nacidos en 2008'))):
            yy = y + 2 + k * 16
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="13" fill="{col}" rx="2"><title>{esc(nm)}, {t}: {n(v)}</title></rect>'
                       f'<text x="{x(v) + 4:.1f}" y="{yy + 11}">{n(v)}</text>')
    out.append('</svg>')
    return ''.join(out)

FUENTE_NAC = f'Fuente: INE, <a href="{NACIM}">Estadística de Nacimientos</a> (por residencia de la madre). Cálculo propio.'


def columnas_nacimientos():
    W, H, ml, mb, mt = 400, 210, 52, 24, 16
    ys = sorted(NAC)
    bw = (W - ml - 6) / len(ys)
    top = 700000
    y = lambda v: mt + (H - mt - mb) * (1 - v / top)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Nacimientos en España por año, de 1975 a 2024; 2008 destacado">']
    for t in (0, 200000, 400000, 600000):
        out.append(f'<line x1="{ml}" x2="{W}" y1="{y(t):.1f}" y2="{y(t):.1f}" stroke="var(--rule)"/>'
                   f'<text x="{ml - 6}" y="{y(t) + 4:.1f}" text-anchor="end" class="lab">{n(t // 1000)} mil</text>' if t else f'<text x="{ml - 6}" y="{y(t) + 4:.1f}" text-anchor="end" class="lab">0</text>')
    for i, a in enumerate(ys):
        x = ml + i * bw
        col = ROJO if a == 2008 else (NARANJA if a in (2005, 2006, 2007) else GRIS)
        op = '1' if a >= 2005 and a <= 2008 else '.55'
        out.append(f'<rect x="{x + 1:.1f}" y="{y(NAC[a]):.1f}" width="{bw - 2:.1f}" height="{y(0) - y(NAC[a]):.1f}" fill="{col}" fill-opacity="{op}"><title>{a}: {n(NAC[a])} nacimientos</title></rect>')
        if a % 10 == 0:
            out.append(f'<text x="{x + bw / 2:.1f}" y="{H - 8}" text-anchor="middle" class="lab">{a}</text>')
    x8 = ml + ys.index(2008) * bw + bw / 2
    out.append(f'<text x="{x8:.1f}" y="{y(NAC[2008]) - 6:.1f}" text-anchor="middle">2008: {n(NAC[2008])}</text>')
    out.append('</svg>')
    return ''.join(out)


g_nac = figura('2008, el año con más nacimientos desde 1981',
               'Nacimientos en España por año, de 1975 a 2024. En rojo, 2008; en naranja, 2005, 2006 y 2007, los otros años de nacimiento de quienes votan por primera vez en unas generales el 29N',
               columnas_nacimientos(), FUENTE_NAC,
               leyenda=[('2008', ROJO), ('2005 a 2007', NARANJA), ('Resto de años', GRIS)],
               tabla=(['Año', 'Nacimientos'], [(a, n(NAC[a])) for a in sorted(NAC, reverse=True)]))

COLS_MAPA = ['#f2e4d4', '#e8c39b', '#dc9a5c', '#c86b2a', '#8f4410']
CORTES = [0.95, 1.05, 1.15, 1.25]


def tono(v):
    return COLS_MAPA[sum(v >= c for c in CORTES)]


g_mapa = figura('Dónde vive la generación de 2008',
                'Nacidos en 2008 sobre la población de cada provincia, a 1 de enero de 2025 (en España, el ' + p(PESO_ESP) + ' %)',
                mapa_provincias({c: tono(PESO[c]) for c in GP},
                                {c: f'{NOM[c]}: {n(GP[c])} nacidos en 2008, el {p(PESO[c])} % de la población' for c in GP},
                                'Mapa de provincias: peso de los nacidos en 2008 en la población'),
                f'Fuente: INE, <a href="{ECP}">Estadística Continua de Población</a>, población a 1 de enero de 2025 por generación (nacidos en 2008) y provincia. Incluye a los residentes extranjeros. Cálculo propio.',
                leyenda=[('Menos del 0,95 %', COLS_MAPA[0]), ('0,95–1,05 %', COLS_MAPA[1]), ('1,05–1,15 %', COLS_MAPA[2]),
                         ('1,15–1,25 %', COLS_MAPA[3]), ('1,25 % o más', COLS_MAPA[4])],
                tabla=(['Provincia', 'Nacidos en 2008 que viven allí (1-1-2025)', '% de la población', 'Nacimientos en 2008', 'Diferencia'],
                       [(NOM[c], n(GP[c]), p(PESO[c]), n(NP[c]), ('+' if VAR[c] > 0 else '') + p(VAR[c]) + ' %') for c in MAS_PESO]))

filas_var = [(nom(c), VAR[c], '#8f4410', ('+' if VAR[c] > 0 else '') + p(VAR[c]) + ' %') for c in GANA[:10]]
filas_var += [(nom(c), max(VAR[c], 0.0001), '#e8c39b', ('+' if VAR[c] > 0 else '') + p(VAR[c]) + ' %') for c in GANA[-6:]]
g_var = figura('Las provincias que han ganado y las que han perdido generación de 2008',
               'Diferencia entre los nacidos en 2008 que viven en cada provincia a 1 de enero de 2025 y los niños que nacieron allí en 2008 (por residencia de la madre). Las diez que más ganan y las seis que menos',
               barras(filas_var, 20, 'Diferencia entre nacidos en 2008 que viven en la provincia y nacimientos de 2008', W=400, ml=110),
               f'Fuente: INE, <a href="{ECP}">Estadística Continua de Población</a> (1-1-2025) y <a href="{NACIM}">Estadística de Nacimientos</a> (2008). La diferencia suma la llegada y la salida de personas, del extranjero y de otras provincias, y los fallecimientos. Cálculo propio.',
               leyenda=[('Diez que más ganan', '#8f4410'), ('Seis que menos', '#e8c39b')])

filas_mun = [(MUN[k], k) for k in MUN_MAS[:15]]
g_mun = figura('Los municipios con más chicos de la generación de 2008',
               f'Personas de 13 años sobre la población, a 1 de enero de 2022, en los municipios de más de {n(UMBRAL)} habitantes (en España, el {p(PESO13)} %)',
               barras([(corto_mun(k), PM[k], '#c86b2a', p(PM[k]) + ' %') for k in MUN_MAS[:15]], 2.4,
                      'Municipios con más peso de las personas de 13 años en 2022', W=400, ml=160),
               f'Fuente: INE, <a href="{PADRON}">Estadística del Padrón Continuo</a>, población a 1 de enero de 2022 por edad año a año y municipio (la última con ese detalle). Quien tenía 13 años ese día nació entre el 2 de enero de 2008 y el 1 de enero de 2009. Cálculo propio.',
               tabla=(['Municipio', 'Provincia', 'Personas de 13 años', 'Población', '%'],
                      [(nombre_mun(k), nom(k[:2]), n(MUN[k][0]), n(MUN[k][1]), p(PM[k])) for k in MUN_MAS[:30]]))

g_filo = figura(f'En {len(SUPERA)} provincias viven más nacidos en 2008 que votos le faltaron al último escaño',
                'Las diez provincias más ajustadas: votos nuevos que habría necesitado en 2023 el partido que se quedó a las puertas del último escaño, con los escaños de 2026 (gris), y nacidos en 2008 que viven en la provincia (marrón)',
                dobles([(nom(c), F[c]['f'], GP[c]) for c in CERCA], max(GP[c] for c in CERCA)),
                f'Fuente: Ministerio del Interior, resultados de julio de 2023 con voto exterior, y escaños de 2026 (cálculo de {L("escanos-en-el-filo-29n", "«Seis escaños que se decidieron por menos de mil votantes»")}); INE, <a href="{ECP}">Estadística Continua de Población</a> (1-1-2025). Los nacidos en 2008 incluyen a los extranjeros, que no votan en las generales. Cálculo propio.',
                tabla=(['Provincia', 'Último escaño', 'A las puertas', 'Votos nuevos que faltaban', 'Nacidos en 2008 que viven allí'],
                       [(NOM[c], F[c]['u'], F[c]['a'], n(F[c]['f']), n(GP[c])) for c in SUPERA]))

EDADES = ['18–24', '25–34', '35–44', '45–54', '55–64', '65–74', '75 y más']


def grupos_edad():
    W, H, ml, mt = 400, 300, 62, 6
    partidos = [('PSOE', 'var(--psoe)'), ('PP', 'var(--pp)'), ('VOX', 'var(--vox)')]
    gh = (H - mt) / 7
    x = lambda v: ml + v / 50 * (W - ml - 40)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto más simpatía al PSOE, el PP y Vox por edad, CIS 3584">']
    for i, e in enumerate(EDADES):
        y0 = mt + i * gh
        out.append(f'<text x="{ml - 8}" y="{y0 + gh / 2 + 4:.1f}" text-anchor="end" class="lab"{" font-weight=\"700\"" if i == 0 else ""}>{e}</text>')
        for k, (pt, col) in enumerate(partidos):
            v = V[pt][i + 1]
            yy = y0 + 3 + k * (gh - 6) / 3
            out.append(f'<rect x="{ml}" y="{yy:.1f}" width="{x(v) - ml:.1f}" height="{(gh - 6) / 3 - 1.5:.1f}" fill="{col}" rx="1.5"><title>{e}: {pt.title() if pt == "VOX" else pt} {p(v)} %</title></rect>'
                       f'<text x="{x(v) + 4:.1f}" y="{yy + (gh - 6) / 3 - 2:.1f}">{p(v)}</text>')
    out.append('</svg>')
    return ''.join(out)


g_cis = figura('Entre los votantes de 18 a 24 años, Vox va primero en el CIS',
               'Voto más simpatía declarado al PSOE, el PP y Vox por grupo de edad, en % de los entrevistados de cada grupo. No es estimación de voto',
               grupos_edad(),
               f'Fuente: CIS, estudio 3584 (preelectoral, del 7 al 30 de octubre de 2026), <a href="{XLSX}">resultados por edad</a>, pregunta 5a. Solo entrevista a mayores de 18 años: muchos de los nacidos en 2008 aún no lo eran.',
               leyenda=[('PSOE', 'var(--psoe)'), ('PP', 'var(--pp)'), ('Vox', 'var(--vox)')],
               tabla=(['Edad', 'PSOE', 'PP', 'Vox', 'Frente Amplio', 'SALF', 'Entrevistas']
                      , [((['Total'] + EDADES)[i], p(V['PSOE'][i]), p(V['PP'][i]), p(V['VOX'][i]),
                          p(V['Frente Amplio (CHA-FA en Aragón y Comuns-FA en Cataluña)'][i]), p(V['Se Acabó la Fiesta'][i]), n(round(V['(N)'][i])))
                         for i in range(8)]))

g_info = figura('Cómo se informan de política los de 18 a 24 años',
                'Primer medio por el que se informan de política y de la campaña, en % de los de 18 a 24 años. En la tabla, frente al total',
                barras([(t, R1[k][J], '#c86b2a', f'{p(R1[k][J])} %') for t, k in
                        [('Redes sociales', 'Redes sociales'), ('Televisión', 'Televisión'), ('Prensa', 'Prensa, en formato impreso o digital'),
                         ('Contactos personales', 'Contactos personales, reuniones, mítines, etc.'), ('Radio', 'Radio')]], 60,
                       'Primer medio de información política de los jóvenes de 18 a 24 años', W=400, ml=150),
                f'Fuente: CIS, estudio 3584, <a href="{XLSX}">resultados por edad</a>, pregunta 1 (primer lugar).',
                tabla=(['Medio o red social', '18–24', 'Total'],
                       [(f'Primer medio: {t}', p(R1[k][J]), p(R1[k][0])) for t, k in [('redes sociales', 'Redes sociales'), ('televisión', 'Televisión'), ('prensa', 'Prensa, en formato impreso o digital'), ('radio', 'Radio')]]
                       + [(f'Red que más sigue (quien se informa por redes): {k}', p(RS[k][J]), p(RS[k][0])) for k in ('Instagram', 'TikTok', 'Twitter/X', 'YouTube', 'Facebook')]))

SEGS = [PR['10 Con toda seguridad, iría a votar'][i] for i in range(1, 8)]
g_part = figura('Los más jóvenes, los menos seguros de ir a votar',
                '«Con toda seguridad iría a votar» (10 en una escala de 0 a 10), en % de cada grupo de edad',
                barras([(e, v, NARANJA if i == 0 else GRIS, p(v) + ' %') for i, (e, v) in enumerate(zip(EDADES, SEGS))], 100,
                       'Porcentaje que irá a votar con toda seguridad, por edad', W=400, ml=70, linea=(SEG_T, f'Total, {p(SEG_T)} %'), separar=True),
                f'Fuente: CIS, estudio 3584, <a href="{XLSX}">resultados por edad</a>, pregunta 2.')

g_mapa_viejo = g_mapa
# ---------- Texto ----------
lista = lambda xs: ', '.join(xs[:-1]) + ' y ' + xs[-1] if len(xs) > 1 else xs[0]
cita_ine = (f'De los electores residentes en España, {n(PRIMEROS26)} podrán participar por primera vez en unas elecciones generales, '
            'por haber cumplido 18 años desde la anterior votación a Cortes Generales, celebrada el 23 de julio de 2023')
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">En 2008 vinieron al mundo en España <strong>{n(NAC[2008])} niños</strong>, una cifra que ningún año había alcanzado desde 1981, según la Estadística de Nacimientos del INE. Aquella cosecha cerró una racha de crecimiento iniciada en 1999. Al año siguiente los alumbramientos ya habían caído a {n(NAC[2009])}, y desde entonces solo repuntaron en 2014: en 2024 se registraron {n(NAC[2024])}, el mínimo desde que arranca la serie, en 1975. Los bebés de 2008 superan en un {p(VS_2024)} % a los de 2024.</p>
<p data-tipo="dato">Dieciocho años después, esa generación llega a las urnas. El 29 de noviembre estrenarán su voto en unas generales {n(PRIMEROS26)} españoles que viven en España, todos los que han alcanzado la mayoría de edad desde la cita del 23 de julio de 2023: el {p(PCT_PRIMEROS)} % de los {n(CER26)} electores residentes en el país. El Instituto Nacional de Estadística dio la cifra el 9 de octubre en su nota sobre el censo electoral, de la que <a href="{EFE}">se hizo eco EFE</a>:</p>
<blockquote class="cita"><p>«{cita_ine}»</p><footer>INE, <a href="{INE_NOTA}">nota de prensa de las elecciones a Cortes Generales del 29 de noviembre de 2026</a> (9-10-2026).</footer></blockquote>
<p data-tipo="contexto">Por fecha de nacimiento, ese grupo abarca desde quienes nacieron el 24 de julio de 2005 hasta quienes lo hicieron el 29 de noviembre de 2008. Los de 2008 son los últimos en incorporarse y proceden del año con más nacimientos desde principios de los ochenta.</p>
{g_nac}
<p data-tipo="dato">No todos llegarán a tiempo. Quien nació a partir del 30 de noviembre de 2008 cumplirá los 18 años al día siguiente de la votación o más tarde. Solo en diciembre de aquel año nacieron {n(DIC08)} niños, el {p(100 * DIC08 / NAC[2008])} % del total anual; a ellos se añaden los del 30 de noviembre, un recuento diario que el INE no publica.</p>
<h2>Más que cuando nacieron</h2>
<p data-tipo="dato">La generación ha crecido desde la cuna. A 1 de enero de 2025, la fecha más reciente de la Estadística Continua de Población del INE, residían en España <strong>{n(GEN08)} personas nacidas en 2008</strong> ({n(HOMBRES08)} hombres y {n(MUJERES08)} mujeres), un {p(CREC_NAC)} % más que los bebés registrados aquel año: las llegadas han superado a las marchas y a las defunciones. De ellas, {n(NACIDOS_FUERA)} vinieron al mundo en el extranjero.</p>
<p data-tipo="dato">Para votar en unas generales hace falta la nacionalidad española, y la tienen {n(ESP08)}; los {n(EXTR08)} restantes son extranjeros. Ni siquiera con ese descuento pierden el primer puesto: de las cuatro cohortes que se estrenan, es la que reúne más españoles. Los nacidos en 2007 con nacionalidad que residen en España suman {n(ESP_COH[2007])}; los de 2006, {n(ESP_COH[2006])}, y los de 2005, {n(ESP_COH[2005])}, siempre a 1 de enero de 2025 (<a href="{ECP_NAC}">ECP, tabla por nacionalidad</a>).</p>
<p data-tipo="dato">Frente a 2023, el contingente es algo menor, aunque se ha reunido más deprisa. En aquellas generales, el INE cifró en {n(PRIMEROS23)} los españoles residentes que votaban por primera vez, quienes habían cumplido 18 años desde el 10 de noviembre de 2019 (<a href="{INE_NOTA23}">nota de prensa del 5 de junio de 2023</a>). Entre una cita y otra mediaron {n(DIAS23)} días; esta vez han sido {n(DIAS26)}. El ritmo medio pasa así de {n(round(DIA23))} nuevos electores diarios a {n(round(DIA26))}.</p>
<h2>El mapa de los nacidos en 2008</h2>
<p data-tipo="dato">En el conjunto del país representan el {p(PESO_ESP)} % de la población. Su huella es mayor en las dos ciudades autónomas, Melilla ({p(PESO['52'])} %) y Ceuta ({p(PESO['51'])} %), y en Sevilla ({p(PESO['41'])} %), Murcia ({p(PESO['30'])} %), Toledo ({p(PESO['45'])} %) y Guadalajara ({p(PESO['19'])} %). En el noroeste, en cambio, se diluyen: Zamora ({p(PESO['49'])} %), Lugo ({p(PESO['27'])} %), Ourense ({p(PESO['32'])} %), León ({p(PESO['24'])} %) y Palencia ({p(PESO['34'])} %).</p>
{g_mapa}
<p data-tipo="dato">En números absolutos, Madrid encabeza la lista con {n(GP['28'])}, por delante de Barcelona ({n(GP['08'])}), Valencia ({n(GP['46'])}), Sevilla ({n(GP['41'])}) y Alicante ({n(GP['03'])}). Casi todas las provincias cuentan hoy con más jóvenes de 2008 de los que vieron nacer aquel año. Ourense suma un {p(VAR['32'])} %; Alicante, un {p(VAR['03'])} %; Lugo, un {p(VAR['27'])} %; Santa Cruz de Tenerife, un {p(VAR['38'])} %, y Toledo, un {p(VAR['45'])} %. Únicamente Ciudad Real ({p(VAR['13'])} %) y Jaén ({p(VAR['23'])} %) conservan menos de los que nacieron allí, y Madrid se queda prácticamente igual: {('+' if MAD_VAR > 0 else '') + p(MAD_VAR)} %.</p>
{g_var}
<p data-tipo="contexto">La paradoja gallega tiene explicación. Ourense y Lugo, donde la generación de 2008 pesa menos, figuran entre las que más han ganado porque partían de muy poco: allí nacieron aquel año {n(NP['32'])} y {n(NP['27'])} niños, respectivamente, según la residencia de la madre, y cada recién llegado cuenta mucho sobre una base tan estrecha.</p>
<h2>Municipio a municipio</h2>
<p data-tipo="contexto">Para bajar al detalle local hay que retroceder en el tiempo. La Estadística Continua de Población se detiene en la provincia, y el último padrón continuo con la edad año a año por municipio es el del 1 de enero de 2022, cuando estos chicos tenían 13 años. Ese día se contaban en España {n(TOTAL13)} personas de esa edad, el {p(PESO13)} % de la población: {n(MAD13)} en el municipio de Madrid y {n(BCN13)} en el de Barcelona.</p>
<p data-tipo="dato">Entre las localidades de más de {n(UMBRAL)} habitantes, la mayor proporción de chicos de 13 años aparecía en el entorno de Madrid, Sevilla, Salamanca, Girona y Zaragoza: {enlace_mun(MUN_MAS[0])} ({p(PM[MUN_MAS[0]])} %, la única por encima del 2 %), {enlace_mun(MUN_MAS[1])} ({p(PM[MUN_MAS[1]])} %), {enlace_mun(MUN_MAS[2])} ({p(PM[MUN_MAS[2]])} %), {enlace_mun(MUN_MAS[3])} ({p(PM[MUN_MAS[3]])} %) y {enlace_mun(MUN_MAS[4])} ({p(PM[MUN_MAS[4]])} %). En el extremo opuesto figuraban {enlace_mun(MUN_MENOS[0])} ({nom(MUN_MENOS[0][:2])}, {p(PM[MUN_MENOS[0]])} %), {enlace_mun(MUN_MENOS[1])} ({nom(MUN_MENOS[1][:2])}, {p(PM[MUN_MENOS[1]])} %), {enlace_mun(MUN_MENOS[2])} ({nom(MUN_MENOS[2][:2])}, {p(PM[MUN_MENOS[2]])} %) y {enlace_mun(MUN_MENOS[3])} ({nom(MUN_MENOS[3][:2])}, {p(PM[MUN_MENOS[3]])} %).</p>
{g_mun}
<h2>Su voz en el CIS</h2>
<p data-tipo="contexto">El CIS no entrevista a menores, de modo que en su preelectoral, realizado del 7 al 30 de octubre, solo aparecen los nacidos en 2008 que ya habían cumplido 18 años. Su franja más joven, de 18 a 24 años, agrupa a los nacidos entre 2001 y 2008 y suma {n(round(NJ))} entrevistas ponderadas, con un error teórico de ±{p(ERRJ)} puntos según la fórmula del propio instituto. Lo que sigue refleja lo que declara ese grupo, no una estimación de voto: el CIS no la publica por edades.</p>
<p data-tipo="dato">En voto más simpatía, que agrega a quienes dicen a qué partido votarán y a quienes, sin desvelarlo, confiesan por cuál sienten más afinidad, <strong>Vox encabeza la franja de 18 a 24 años con el {p(VOX_J)} %</strong>, seguido del PSOE ({p(PSOE_J)} %) y del PP ({p(PP_J)} %). Entre el conjunto de entrevistados, el orden es otro: PSOE ({p(PSOE_T)} %), PP ({p(PP_T)} %) y Vox ({p(VOX_T)} %). Vox mantiene la cabeza entre los de 25 a 34 años; a partir de los 35, el PSOE toma el relevo. El Frente Amplio obtiene el {p(FA_J)} % entre los más jóvenes (el {p(FA_T)} % en total), y Se Acabó la Fiesta, el {p(SALF_J)} % ({p(SALF_T)} %).</p>
{g_cis}
<p data-tipo="dato">En la escala ideológica del CIS, que va del 1 (izquierda) al 10 (derecha), los de 18 a 24 años se colocan de media en el {p(MED_J)}; el conjunto, en el {p(MED_T)}. Rehúyen los extremos más que el resto de los entrevistados: en el 1, el más escorado a la izquierda, se sitúa el {p(IZQ_J)} %, frente al {p(IZQ_T)} % del total, y en el 10, el más escorado a la derecha, el {p(DER_J)} %, frente al {p(DER_T)} %.</p>
<p data-tipo="dato">También se informan por otros canales. La mitad ({p(REDES_J)} %) sigue la política y la campaña sobre todo a través de las redes sociales, frente al {p(REDES_T)} % del total. La televisión, primera ventana para el {p(TV_T)} % de los entrevistados, solo lo es para el {p(TV_J)} % de los jóvenes, y la radio, para el {p(RADIO_J)} %. Entre quienes se informan por redes, Instagram es la más seguida ({p(INSTA_J)} %), por delante de TikTok ({p(TIKTOK_J)} %, frente al {p(TIKTOK_T)} % en el total) y X ({p(X_J)} %). Facebook, segunda plataforma en el conjunto de la muestra, cae al {p(FB_J)} % en esta franja.</p>
{g_info}
<p data-tipo="dato">Y son los menos convencidos de acudir a las urnas. El {p(SEG_J)} % de los de 18 a 24 años se otorga un 10 («con toda seguridad iría a votar»), la proporción más baja de todas las edades, frente al {p(SEG_T)} % del total.</p>
{g_part}
<h2>Lo que pesan frente al último escaño</h2>
<p data-tipo="dato">En {L("escanos-en-el-filo-29n", "«Seis escaños que se decidieron por menos de mil votantes»")} calculamos cuántos votos adicionales le habrían hecho falta en 2023 al partido que se quedó a las puertas del último escaño de cada provincia, con el reparto de diputados del 29N. En <strong>{len(SUPERA)} de las 52 provincias</strong>, esa distancia es menor que el número de nacidos en 2008 que residen allí. En Girona faltaban {n(F['17']['f'])} votos y viven {n(GP['17'])} jóvenes de esa generación; en Cantabria, {n(F['39']['f'])} frente a {n(GP['39'])}; en Tarragona, {n(F['43']['f'])} frente a {n(GP['43'])}.</p>
<p data-tipo="contexto">Nada de esto significa que vayan a inclinar la balanza. Ni todos son españoles ni todos votarán; los nacidos en diciembre aún no pueden hacerlo, y quienes acudan no elegirán la misma papeleta. La comparación solo sirve de escala: en las provincias más ajustadas, un único año de nacimiento supera la distancia que separó el último escaño del siguiente.</p>
{g_filo}
<h2>Cómo se ha hecho</h2>
<p data-tipo="contexto">El número de electores que votan por primera vez en unas generales es el que da el INE en su <a href="{INE_NOTA}">nota del 9 de octubre</a> para los residentes en España. Los nacidos en 2008 que viven en cada provincia salen de la <a href="{ECP}">Estadística Continua de Población</a> a 1 de enero de 2025, que da la población por «generación» (el año de nacimiento) y provincia; la nacionalidad y el país de nacimiento solo están para el total de España. Incluye a los extranjeros, que no votan en las generales, y no descuenta a quienes nacieron en diciembre. Los nacimientos son los de la <a href="{NACIM}">Estadística de Nacimientos</a>, por provincia de residencia de la madre. El dato municipal es el del <a href="{PADRON}">padrón continuo a 1 de enero de 2022</a>, el último con la edad año a año por municipio. Los datos del CIS son los de la hoja «Edad» del <a href="{XLSX}">Excel de resultados</a> del estudio 3584.</p>
'''
g_mapa = g_mapa.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')
cuerpo = cuerpo.replace(g_mapa_viejo, g_mapa)
preguntas = [
    ('¿Cuántos jóvenes votan por primera vez en las generales del 29N?',
     f'{n(PRIMEROS26)} electores residentes en España, según el <a href="{INE_NOTA}">INE</a>: los que han cumplido 18 años desde las generales del 23 de julio de 2023. Son el {p(PCT_PRIMEROS)} % del censo de residentes.'),
    ('¿Pueden votar el 29N los nacidos en 2008?',
     f'Sí, los que cumplan 18 años como tarde el día de la votación: los nacidos hasta el 29 de noviembre de 2008. Los nacidos en diciembre de 2008 ({n(DIC08)}) y el 30 de noviembre no podrán.'),
    ('¿Por qué se habla de la generación de 2008?',
     f'Porque 2008 fue el año con más nacimientos en España desde 1981: {n(NAC[2008])}. Hoy viven en España {n(GEN08)} personas nacidas ese año, {n(ESP08)} con nacionalidad española.'),
    ('¿A quién votan los jóvenes según el CIS?',
     f'En el preelectoral del CIS, entre los de 18 a 24 años, Vox es el primero en voto más simpatía ({p(VOX_J)} %), seguido del PSOE ({p(PSOE_J)} %) y del PP ({p(PP_J)} %). No es estimación de voto y el CIS solo pregunta a mayores de edad.'),
]
enlaces = (f'{L("escanos-en-el-filo-29n", "Seis escaños que se decidieron por menos de mil votantes")} · {L("cis-preelectoral-29n", "El CIS preelectoral")} · '
           f'<a href="{BASE}encuestas/">Todas las encuestas del 29N</a>')
foot = ('Datos: INE (censo electoral del 29N, Estadística Continua de Población, Estadística de Nacimientos y padrón continuo de 2022); '
        'CIS, estudio 3584; Ministerio del Interior, resultados de 2023. Cálculo: actualidad/src/resumenes/generacion_2008.py.')
r4 = lambda x: round(float(x), 4)
DATOS = {'PRIMEROS26': PRIMEROS26, 'PRIMEROS23': PRIMEROS23, 'CER26': CER26, 'PCT_PRIMEROS': r4(PCT_PRIMEROS), 'DIAS23': DIAS23, 'DIAS26': DIAS26,
         'DIA23': r4(DIA23), 'DIA26': r4(DIA26), 'NAC': NAC, 'MES': MES, 'VS_2024': r4(VS_2024), 'GEN08': GEN08, 'ESP08': ESP08, 'EXTR08': EXTR08,
         'NACIDOS_FUERA': NACIDOS_FUERA, 'H08': HOMBRES08, 'M08': MUJERES08, 'ESP_COH': ESP_COH, 'CREC_NAC': r4(CREC_NAC),
         'GP': GP, 'NP': NP, 'PESO': {c: r4(v) for c, v in PESO.items()}, 'VAR': {c: r4(v) for c, v in VAR.items()}, 'PESO_ESP': r4(PESO_ESP),
         'TOTAL13': TOTAL13, 'PESO13': r4(PESO13), 'MAD13': MAD13, 'BCN13': BCN13,
         'PM': {k[:5]: r4(PM[k]) for k in MUN_MAS[:30] + MUN_MENOS[:10]}, 'UMBRAL': UMBRAL,
         'SUPERA': SUPERA, 'FF': {c: F[c]['f'] for c in F}, 'V': V, 'R1': R1, 'RS': RS, 'PR': PR, 'IDE': IDE, 'NJ': r4(NJ), 'ERRJ': r4(ERRJ)}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
H1 = 'La generación de 2008, la de más nacimientos desde 1981, estrena su voto en unas generales el 29N'
DEK = (f'En 2008 nacieron en España {n(NAC[2008])} niños. Son los más jóvenes de los {n(PRIMEROS26)} electores que votan por primera vez '
       f'en unas generales, según el INE. En el CIS, los de 18 a 24 años ponen a Vox primero.')
if __name__ == '__main__':
    pieza(SLUG, 'La generación de 2008', H1, DEK, '15 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print(H1); print(DEK)
    print('SUPERA', [NOM[c] for c in SUPERA])
    print('MUN_MAS', [(nombre_mun(k), round(PM[k], 2)) for k in MUN_MAS[:8]])
    print('MUN_MENOS', [(nombre_mun(k), round(PM[k], 2)) for k in MUN_MENOS[:5]])
    print('GANA', [(nom(c), round(VAR[c], 1)) for c in GANA[:8]], 'PIERDE', [(nom(c), round(VAR[c], 1)) for c in GANA[-6:]])
    print('día', DIA23, DIA26, 'ERRJ', ERRJ, 'NJ', NJ)
