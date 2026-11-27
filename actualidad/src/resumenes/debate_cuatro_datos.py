"""El debate a cuatro del 26-11-2026, comprobado con datos: cinco frases de Sánchez, Feijóo, Abascal y Colau.

Pieza aprobada por Nacho el 27-11 («hazla»). Frases literales tal como las recogen elDiario.es y Verificat (no hay
transcripción de EFE ni de Europa Press). Cada dato se calcula aquí con la fuente oficial descargada:
- Migraciones: INE, Estadística de Migraciones y Cambios de Residencia (EMCR), tablas 69688 y 69703, 2021-2024
  (definitivos; la serie empieza en 2021 y no empalma con la Estadística de Migraciones anterior).
- Empleo: INE, EPA, tabla 65109, ocupados, 2002-2026 (3.er trimestre de 2026, el último).
- Vivienda: INE, Índice de Precios de Vivienda, tabla 80270, índice general nacional (2.º trimestre de 2026, el último).
- PIB: Eurostat, namq_10_gdp, variación interanual del PIB en volumen, corregido de estacionalidad y calendario
  (CLV_PCH_SM, SCA), actualizado el 25-11-2026.
- Gürtel: nota del Tribunal Supremo del 14-10-2020.
Veda (LOREG 69.7): sin cifras de encuestas.
Uso, desde la raíz: python3 actualidad/src/resumenes/debate_cuatro_datos.py
"""
import csv
import json

from comun import BASE, RAIZ, esc, figura, n, barras, pieza
from mapa_ccaa import p

A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
SLUG = 'verificacion-debate-a-cuatro-datos-29n'
DEBATE = 'debate-a-cuatro-sanchez-feijoo-abascal-colau-29n'
DATOS = RAIZ / 'actualidad/src/resumenes/datos'

ELDIARIO = 'https://www.eldiario.es/politica/mentiras-debate-cuatro_1_13697433.html'
ELDIARIO_DIR = 'https://www.eldiario.es/politica/ultima-hora-ultimo-debate-electoral-sanchez-feijoo-colau-abascal_6_13696999_1126925.html'
VERIFICAT = 'https://www.verificat.cat/es/debate-29n-verificaciones/'
INE_EMCR = 'https://www.ine.es/jaxiT3/Tabla.htm?t=69688'
INE_EMCR_E = 'https://www.ine.es/jaxiT3/Tabla.htm?t=69703'
INE_EPA = 'https://www.ine.es/jaxiT3/Tabla.htm?t=65109'
INE_IPV = 'https://www.ine.es/jaxiT3/Tabla.htm?t=80270'
EUROSTAT = 'https://ec.europa.eu/eurostat/databrowser/view/namq_10_gdp/default/table'
SUPREMO = 'https://www.poderjudicial.es/cgpj/en/Judiciary/Supreme-Court/Pressroom/Press-Archive/El-Tribunal-Supremo-confirma-penas-de-hasta-51-anos-de-prision-para-los-procesados-en-el--caso-Gurtel-'

leer = lambda f: list(csv.DictReader(open(DATOS / f, encoding='utf-8')))

# 1. Abascal: «seis millones de personas» en seis años
MIG = leer('debate_cuatro_migraciones_emcr.csv')
mig = lambda flujo, nac: {int(r['anyo']): int(r['valor']) for r in MIG if r['flujo'] == flujo and r['nacionalidad'] == nac}
IN, OUT = mig('inmigraciones', 'total'), mig('emigraciones', 'total')
IN_ES = mig('inmigraciones', 'española')
ANYOS = sorted(IN)
assert ANYOS == [2021, 2022, 2023, 2024] and sorted(OUT) == ANYOS
ENTRAN, SALEN = sum(IN.values()), sum(OUT.values())
SALDO = ENTRAN - SALEN
EXTR = ENTRAN - sum(IN_ES.values())
assert (ENTRAN, SALEN, SALDO, EXTR) == (4686407, 2499744, 2186663, 4115038), (ENTRAN, SALEN, SALDO, EXTR)
PSAL = 100 * SALEN / ENTRAN

# 2. Sánchez: «jamás ha habido tantos trabajadores»
EPA = [(int(r['anyo']), int(r['trimestre']), float(r['ocupados_miles'])) for r in leer('debate_cuatro_epa_ocupados.csv')]
ULT_EPA = EPA[-1]
assert ULT_EPA[:2] == (2026, 3) and ULT_EPA[2] == max(v for _, _, v in EPA)
PICO07 = max((x for x in EPA if x[0] <= 2008), key=lambda x: x[2])
E18 = [x for x in EPA if x[:2] == (2018, 2)][0]
assert PICO07[:2] == (2007, 3) and E18[2] == 19344.1
OCUP, MAS18, MAS07 = ULT_EPA[2] * 1000, (ULT_EPA[2] - E18[2]) * 1000, (ULT_EPA[2] - PICO07[2]) * 1000

# 3. Sánchez: «es la que más crece de toda Europa»
PIB = leer('debate_cuatro_pib_eurostat.csv')
PER = max(r['trimestre'] for r in PIB)
assert PER == '2026-Q3'
UE = sorted(((float(r['pib_variacion_interanual']), r['geo']) for r in PIB if r['trimestre'] == PER and r['geo'] != 'EU27_2020'), reverse=True)
UE27 = [float(r['pib_variacion_interanual']) for r in PIB if r['trimestre'] == PER and r['geo'] == 'EU27_2020'][0]
NOM = {'PL': 'Polonia', 'IE': 'Irlanda', 'SI': 'Eslovenia', 'DK': 'Dinamarca', 'CY': 'Chipre', 'SE': 'Suecia', 'ES': 'España',
       'BG': 'Bulgaria', 'PT': 'Portugal', 'LT': 'Lituania', 'EE': 'Estonia', 'NL': 'Países Bajos', 'FI': 'Finlandia',
       'CZ': 'Chequia', 'HU': 'Hungría', 'DE': 'Alemania', 'IT': 'Italia', 'BE': 'Bélgica', 'AT': 'Austria', 'SK': 'Eslovaquia',
       'RO': 'Rumanía', 'FR': 'Francia'}
PUESTO = [g for _, g in UE].index('ES') + 1
NPAISES = len(UE)
DELANTE = [NOM[g] for _, g in UE[:PUESTO - 1]]
VAL = {g: v for v, g in UE}
assert (PUESTO, NPAISES, VAL['ES']) == (7, 22, 2.7) and VAL['ES'] > max(VAL['DE'], VAL['IT'], VAL['FR'])

# 4. Feijóo: «comprar es un 76% más caro»
IPV = {(int(r['anyo']), int(r['trimestre'])): float(r['indice']) for r in leer('debate_cuatro_ipv.csv')}
ULT_IPV = max(IPV)
assert ULT_IPV == (2026, 2)
SUBE = 100 * (IPV[ULT_IPV] / IPV[(2018, 2)] - 1)
assert round(SUBE, 1) == 69.5

# Recuento de veredictos
VER = [('Sánchez', 'jamás ha habido tantos trabajadores', 'Exacta'),
       ('Feijóo', 'comprar es un 76% más caro', 'Exagera'),
       ('Sánchez', 'es la que más crece de toda Europa', 'Falsa'),
       ('Abascal', 'seis millones de personas', 'Engañosa'),
       ('Colau', 'condenado por organización criminal', 'Falsa')]
NEXACTAS = sum(v == 'Exacta' for *_, v in VER)
assert (len(VER), NEXACTAS) == (5, 1)

COL_ES, COL_OT = 'var(--accent)', 'var(--muted)'
g_pib = figura(f'España creció un {p(VAL["ES"])} %: la {PUESTO}.ª de los {NPAISES} países de la UE con dato',
               'Crecimiento del PIB en el tercer trimestre de 2026 frente al mismo trimestre de 2025, en %',
               barras([(NOM[g], v, COL_ES if g == 'ES' else COL_OT, p(v)) for v, g in UE], max(VAL.values()) * 1.1,
                      'Crecimiento interanual del PIB en el tercer trimestre de 2026 en los países de la UE', W=400, ml=110,
                      fmt=p, linea=None),
               f'Fuente: <a href="{EUROSTAT}">Eurostat</a>, PIB en volumen corregido de estacionalidad y calendario, datos del 25 de noviembre de 2026. '
               'Sin dato aún: Croacia, Grecia, Letonia, Luxemburgo y Malta. Francia cae un 0,1 %.',
               None,
               (['País', 'Crecimiento interanual (%)'], [[NOM[g], p(v)] for v, g in UE]))

g_mig = figura(f'De {n(ENTRAN / 1e6, 2)} millones de llegadas, {n(SALEN / 1e6, 2)} millones de salidas',
               'Migraciones con el extranjero registradas por el INE cada año, en miles',
               barras([(f'{a}, llegadas', IN[a] / 1000, COL_OT, n(IN[a] / 1000)) for a in ANYOS]
                      + [(f'{a}, salidas', OUT[a] / 1000, 'var(--ink)', n(OUT[a] / 1000)) for a in ANYOS],
                      max(IN.values()) / 1000 * 1.15, 'Inmigraciones y emigraciones con el extranjero en España, 2021 a 2024',
                      W=400, ml=110, fmt=lambda v: n(v)),
               f'Fuente: INE, Estadística de Migraciones y Cambios de Residencia (<a href="{INE_EMCR}">inmigraciones</a> y '
               f'<a href="{INE_EMCR_E}">emigraciones</a>), datos definitivos. Todas las nacionalidades. Son migraciones, no personas.',
               None,
               (['Año', 'Llegadas', 'Salidas', 'Saldo'], [[str(a), n(IN[a]), n(OUT[a]), n(IN[a] - OUT[a])] for a in ANYOS]))

tabla = ('<div class="tbl"><table><thead><tr><th>Candidato</th><th>Frase</th><th>Con los datos</th></tr></thead><tbody>'
         + ''.join(f'<tr><td>{c}</td><td>«{esc(f)}»</td><td>{v}</td></tr>' for c, f, v in VER) + '</tbody></table></div>')

cuerpo = f'''
<p data-tipo="contexto">El debate a cuatro del jueves 26 dejó decenas de cifras. Hemos escogido cinco frases, al menos una de cada candidato, que se pueden comprobar con una fuente oficial, y las hemos contrastado con el último dato publicado. Las frases son literales, tal como las recogen <a href="{ELDIARIO}">elDiario.es</a> y <a href="{VERIFICAT}">Verificat</a>. De las cinco, <strong>{NEXACTAS} es exacta</strong>.</p>
{tabla}
<h2>Sánchez y el empleo: exacta</h2>
<p data-tipo="dato">Pedro Sánchez dijo: «Récord histórico, jamás ha habido tantos trabajadores en nuestro país», según <a href="{ELDIARIO_DIR}">elDiario.es</a>. Es cierto. En el tercer trimestre de 2026 había <strong>{n(OCUP)} ocupados</strong>, según la <a href="{INE_EPA}">Encuesta de Población Activa del INE</a>: el máximo de la serie, que empieza en 2002. Son {n(MAS18)} más que en el segundo trimestre de 2018, cuando llegó al Gobierno, y {n(MAS07)} más que en el tercero de 2007, el máximo antes de la crisis.</p>
<p data-tipo="contexto">Que haya más ocupados que nunca no dice por sí solo cómo es ese empleo ni cuánto se cobra: es lo que mide la frase y lo que se comprueba aquí. España también tiene hoy más habitantes que en 2007.</p>
<h2>Feijóo y el precio de la vivienda: exagera</h2>
<p data-tipo="dato">Alberto Núñez Feijóo dijo: «Desde que empezó la legislatura de Sánchez comprar es un 76% más caro y alquilar un 45% más caro», según <a href="{VERIFICAT}">Verificat</a>. El índice oficial del precio de compra, el <a href="{INE_IPV}">Índice de Precios de Vivienda del INE</a>, que mide compraventas reales, subió un <strong>{p(SUBE)} %</strong> del segundo trimestre de 2018 al segundo de 2026, el último publicado. La subida es grande, pero menor que la que dio Feijóo. Su cifra coincide con la de los precios que piden los anuncios de Idealista, según Verificat, que no es lo mismo que lo que se acaba pagando.</p>
<h2>Sánchez y el crecimiento: falsa</h2>
<p data-tipo="dato">Sánchez dijo que la economía española «es la que más crece de toda Europa», según <a href="{ELDIARIO}">elDiario.es</a>. No lo es. En el tercer trimestre de 2026, el PIB de España creció un <strong>{p(VAL["ES"])} %</strong> frente al mismo trimestre del año anterior, según <a href="{EUROSTAT}">Eurostat</a>. Es el {PUESTO}.º puesto de los {NPAISES} países de la UE que ya han dado el dato: por delante quedan {", ".join(DELANTE[:-1])} y {DELANTE[-1]}. La media de la UE fue del {p(UE27)} %.</p>
{g_pib}
<p data-tipo="contexto">Lo que sí es cierto es que España crece más que las otras grandes economías del euro: Alemania, un {p(VAL["DE"])} %; Italia, un {p(VAL["IT"])} %, y Francia, que cae un {p(-VAL["FR"])} %.</p>
<h2>Abascal y los «seis millones»: engañosa</h2>
<p data-tipo="dato">Santiago Abascal dijo: «En los últimos seis años han entrado en España seis millones de personas según el INE», según <a href="{ELDIARIO}">elDiario.es</a>. Los datos definitivos del INE llegan hasta 2024 y la serie actual empieza en 2021. En esos cuatro años, la <a href="{INE_EMCR}">Estadística de Migraciones del INE</a> registró <strong>{n(ENTRAN)} llegadas</strong> desde el extranjero, {n(EXTR)} de ellas de personas con nacionalidad extranjera. Pero en los mismos cuatro años hubo <strong>{n(SALEN)} salidas</strong> hacia el extranjero, el {p(PSAL)} % de las llegadas. El saldo, lo que de verdad sumó la población por la migración, fue de <strong>{n(SALDO)}</strong>.</p>
{g_mig}
<p data-tipo="contexto">Hablar solo de entradas da una cifra mucho mayor que la gente que se queda. Además, el INE cuenta migraciones, no personas: quien entra, sale y vuelve a entrar cuenta dos veces. En las mismas llegadas están los españoles que vuelven del extranjero.</p>
<h2>Colau y la condena del PP: falsa</h2>
<p data-tipo="dato">Ada Colau le dijo a Feijóo: «O sea, le han condenado [al PP] por organización criminal, señor Feijóo», según <a href="{VERIFICAT}">Verificat</a>. No es así. En la sentencia firme del caso Gürtel, la nota del <a href="{SUPREMO}">Tribunal Supremo</a> del 14 de octubre de 2020 dice que el tribunal «confirma lo establecido por la Audiencia Nacional en cuanto a las responsabilidades civiles y a la responsabilidad como partícipes a título lucrativo del Partido Popular». Es una responsabilidad civil: el PP tuvo que devolver el dinero de unos actos electorales que pagaron las empresas de la trama. No es una condena penal ni por organización criminal.</p>
<p data-tipo="contexto">La misma nota del Supremo dice que entre el «Grupo CORREA» y «personas del Partido Popular se tejió una estructura de colaboración estable», y confirma la condena «por asociación ilícita para varios de los acusados». Son condenas a personas, no al partido.</p>
<h2>Cómo lo hemos comprobado</h2>
<p data-tipo="contexto">Hemos elegido frases con una cifra o un hecho que se puede contrastar con una fuente oficial, sin entrar en opiniones ni promesas, y al menos una de cada candidato. Cada dato está calculado con la última cifra publicada por el INE, Eurostat o el Tribunal Supremo. Las frases son las que recogen elDiario.es y Verificat. Otros verificadores, como Newtral, VerificaRTVE y Maldita, revisaron más frases del debate.</p>
<p data-tipo="contexto">Lo que se dijo en el debate, quién participó y cuánta gente lo vio está en {L(DEBATE, "la pieza del debate a cuatro")}.</p>
'''

preguntas = [
    ('¿Qué frases del debate a cuatro eran ciertas?',
     f'De las cinco que hemos comprobado, solo es exacta la de Sánchez sobre el empleo: en el tercer trimestre de 2026 había {n(OCUP)} ocupados, el máximo de la EPA.'),
    ('¿Es verdad que han entrado seis millones de inmigrantes en seis años?',
     f'Cuenta solo las llegadas. De 2021 a 2024, el INE registró {n(ENTRAN)} llegadas y {n(SALEN)} salidas: el saldo fue de {n(SALDO)}.'),
    ('¿Es España la economía que más crece de Europa?',
     f'No. En el tercer trimestre de 2026 creció un {p(VAL["ES"])} %, el {PUESTO}.º puesto de los {NPAISES} países de la UE con dato, según Eurostat. Sí crece más que Alemania, Francia e Italia.'),
    ('¿Cuánto ha subido la vivienda desde 2018?',
     f'Un {p(SUBE)} % del segundo trimestre de 2018 al segundo de 2026, según el Índice de Precios de Vivienda del INE. Feijóo dijo un 76 %.'),
    ('¿Ha sido condenado el PP por organización criminal?',
     'No. En el caso Gürtel, el Supremo confirmó en 2020 su responsabilidad civil como partícipe a título lucrativo, no una condena penal.'),
]
enlaces = (f'{L(DEBATE, "Debate a cuatro: hora, dónde verlo y en qué orden hablan")} · '
           f'<a href="{BASE}elecciones/resultados-elecciones-generales-2026/">Resultados de las elecciones generales 2026</a>')
foot = ('Datos: INE (Estadística de Migraciones y Cambios de Residencia, EPA e Índice de Precios de Vivienda), Eurostat (PIB trimestral) '
        'y Tribunal Supremo. Frases: elDiario.es y Verificat. Cálculo: actualidad/src/resumenes/debate_cuatro_datos.py.')
D = {'ENTRAN': ENTRAN, 'SALEN': SALEN, 'SALDO': SALDO, 'EXTR': EXTR, 'PSAL': PSAL, 'OCUP': OCUP, 'MAS18': MAS18, 'MAS07': MAS07,
     'VAL': VAL, 'UE27': UE27, 'PUESTO': PUESTO, 'NPAISES': NPAISES, 'SUBE': SUBE, 'NEXACTAS': NEXACTAS,
     'IN': IN, 'OUT': OUT}
datos_js = '<script>const D=' + json.dumps(D, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'

TITULO = 'El debate a cuatro, comprobado con datos: de cinco frases de Sánchez, Feijóo, Abascal y Colau, solo una es exacta'
DEK = (f'Abascal habló de seis millones de entradas: con las salidas, el saldo de 2021 a 2024 fue de {n(SALDO / 1e6, 1)} millones. '
       f'España crece un {p(VAL["ES"])} %, la {PUESTO}.ª de la UE, no la primera. La vivienda subió un {p(SUBE)} %, no un 76 %.')
pieza(SLUG, 'El debate, con datos', TITULO, DEK, '27 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
print(ENTRAN, SALEN, SALDO, EXTR, round(PSAL, 1), OCUP, MAS18, MAS07, PUESTO, NPAISES, round(SUBE, 1), UE27)
