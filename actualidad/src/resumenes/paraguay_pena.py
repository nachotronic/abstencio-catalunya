"""«Paraguay destituye a Santiago Peña» (10-11-2026). Serie Internacional.

Cronología (fuentes enlazadas en el texto): el BCP dispuso la resolución de Ueno Bank el martes 3-11-2026; Peña anunció su
renuncia el jueves 5 y el Congreso no la trató por falta de quórum; Diputados aprobó la acusación el 5 (78 diputados en
activo) y el Senado, constituido en tribunal, rechazó el viernes 6 a las 11.42 la prórroga de 72 horas (39 votos en
contra, 3 a favor y 2 abstenciones) y a las 18.55 lo destituyó por mal desempeño de funciones con 44 votos (45 senadores,
Enrique Riera ausente). Pedro Alliana juró a las 19.45 (ABC Color, en vivo del 6-11; Vozpópuli, 7-11).

Votos de 2023 por departamento: tabla «Resultados por departamento» de Wikipedia (cita al TSJE), copiada en
datos/paraguay_2023.json. El cómputo definitivo del TSJE (Acuerdo y Sentencia 15/2023) no se puede descargar hoy de
tsje.gov.py. Los porcentajes se recalculan sobre los votos emitidos que suman las columnas (en Boquerón y Caazapá la columna
«Emitidos» de la tabla no cuadra con la suma; los porcentajes de la tabla sí cuadran con ella). Resultado nacional: TSJE en
la proclamación (Última Hora, 24-5-2023): Peña 1.292.079 votos; 3.022.946 votos emitidos.
Uso, desde la raíz: python3 actualidad/src/resumenes/paraguay_pena.py
"""
import json
import math

from comun import RAIZ, esc, figura, n, barras, cuadrados, pieza

p = lambda v: n(v, 1)
J = json.load(open(RAIZ / 'actualidad/src/resumenes/datos/paraguay_2023.json'))
DEP = J['departamentos']
assert len(DEP) == 18
CAND = ['pena', 'alegre', 'cubas', 'acevedo', 'chilavert', 'otros']
NOMC = {'pena': 'Santiago Peña (ANR)', 'alegre': 'Efraín Alegre (Concertación)', 'cubas': 'Paraguayo Cubas (Cruzada Nacional)'}
CORTO = {'pena': 'Peña', 'alegre': 'Alegre', 'cubas': 'Cubas'}
COLC = {'pena': 'var(--anr)', 'alegre': 'var(--conc)', 'cubas': 'var(--cn)'}
EST = ('<style>:root{--anr:#d7191f;--conc:#2e3092;--cn:#2b2b2b}'
       '@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--anr:#f0474c;--conc:#7f83e0;--cn:#cfcfcf}}'
       ':root[data-theme="dark"]{--anr:#f0474c;--conc:#7f83e0;--cn:#cfcfcf}</style>')

for d in DEP:
    d['emitidos'] = sum(d[k] for k in CAND) + d['blanco'] + d['nulos']
    for k in CAND:
        d['%' + k] = d[k] / d['emitidos'] * 100
    d['part'] = d['emitidos'] / d['electores'] * 100
    d['gana'] = max(('pena', 'alegre', 'cubas'), key=lambda k: d[k])
DESCUADRE = sorted(d['nombre'] for d in DEP if d['emitidos'] != d['emitidos_wiki'])
assert DESCUADRE == ['Boquerón', 'Caazapá'], DESCUADRE
D = {d['nombre']: d for d in DEP}
GANA = {k: sorted(d['nombre'] for d in DEP if d['gana'] == k) for k in ('pena', 'alegre', 'cubas')}
assert GANA['cubas'] == ['Alto Paraná'] and not GANA['alegre'] and len(GANA['pena']) == 17
assert max(DEP, key=lambda d: d['cubas'] / (d['pena'] + d['alegre'] + d['cubas'] + 1e-9)) ['nombre'] == 'Alto Paraná'
assert max(DEP, key=lambda d: d['electores'])['nombre'] == 'Central'
TOT = {k: sum(d[k] for d in DEP) for k in CAND + ['blanco', 'nulos', 'emitidos', 'electores']}
# Resultado nacional proclamado por el TSJE (con el voto en el exterior)
NAC = {'pena': 1292079, 'alegre': 830842, 'emitidos': 3022946}
NAC_PCT = NAC['pena'] / NAC['emitidos'] * 100
assert round(NAC_PCT, 2) == 42.74
ORD = sorted(DEP, key=lambda d: -d['%pena'])
MAS50 = [d['nombre'] for d in DEP if d['%pena'] > 50]
CENTRAL, ALTO = D['Central'], D['Alto Paraná']
print('gana', {k: len(v) for k, v in GANA.items()}, 'mas50', len(MAS50), MAS50, 'pena central', round(CENTRAL['%pena'], 1),
      'max', ORD[0]['nombre'], round(ORD[0]['%pena'], 1), 'part', round(TOT['emitidos'] / TOT['electores'] * 100, 1))

# --- Mapa por departamento ---
KX = math.cos(math.radians(23.4))


def proy(W):
    pts = [(x * KX, -y) for d in DEP for a in d['anillos'] for x, y in a]
    x0, x1 = min(x for x, _ in pts), max(x for x, _ in pts)
    y0, y1 = min(y for _, y in pts), max(y for _, y in pts)
    s = W / (x1 - x0)
    return (lambda x, y: ((x * KX - x0) * s, (-y - y0) * s)), round((y1 - y0) * s)


def tono(d):
    v = d['%' + d['gana']]
    return .45 if v < 40 else (.72 if v < 50 else 1)


def mapa(W=520):
    f, H = proy(W)
    out = []
    for d in DEP:
        dd = ''.join('M' + 'L'.join(f'{f(x, y)[0]:.1f},{f(x, y)[1]:.1f}' for x, y in a) + 'Z' for a in d['anillos'])
        out.append(f'<path d="{dd}" fill="{COLC[d["gana"]]}" fill-opacity="{tono(d)}"><title>{esc(d["nombre"])}: '
                   f'{CORTO[d["gana"]]}, {p(d["%" + d["gana"]])} %</title></path>')
    # Asunción, ampliada en un recuadro abajo a la izquierda
    a = D['Asunción']
    xs = [x for r in a['anillos'] for x, _ in r]; ys = [y for r in a['anillos'] for _, y in r]
    cx, cy = f((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
    bx, by, bw = 18, H - 150, 120
    g, _ = proy(W * 9)
    gx = [g(x, y) for r in a['anillos'] for x, y in r]
    ox, oy = min(x for x, _ in gx), min(y for _, y in gx)
    sw, sh = max(x for x, _ in gx) - ox, max(y for _, y in gx) - oy
    k = (bw - 20) / max(sw, sh)
    ins = ''.join('M' + 'L'.join(f'{bx + 10 + (g(x, y)[0] - ox) * k:.1f},{by + 24 + (g(x, y)[1] - oy) * k:.1f}' for x, y in r) + 'Z' for r in a['anillos'])
    caja = (f'<rect x="{bx}" y="{by}" width="{bw}" height="{bw + 14}" fill="none" stroke="var(--rule)"/>'
            f'<text x="{bx + 8}" y="{by + 16}" class="lab">Asunción</text>'
            f'<path d="{ins}" fill="{COLC[a["gana"]]}" fill-opacity="{tono(a)}" stroke="var(--bg)"><title>Asunción: '
            f'{CORTO[a["gana"]]}, {p(a["%" + a["gana"]])} %</title></path>'
            f'<line x1="{bx + bw}" y1="{by + 10}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="var(--muted)" stroke-width=".8"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3" fill="none" stroke="var(--fg)"/>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Candidato más votado en cada departamento de Paraguay en las presidenciales de 2023" '
            f'style="max-width:{W}px;margin:0 auto"><g stroke="var(--bg)" stroke-width=".8" stroke-linejoin="round">{"".join(out)}</g>{caja}</svg>')


def apiladas(W=430, ml=112, alto=24):
    H = alto * len(ORD) + 8
    x = lambda v: ml + v / 100 * (W - ml - 8)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto a Peña, Alegre y Cubas por departamento en 2023">']
    for i, d in enumerate(ORD):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + alto / 2 + 4:.1f}" text-anchor="end" class="lab">{esc(d["nombre"])}</text>')
        x0 = ml
        for k in ('pena', 'alegre', 'cubas'):
            w = x(d['%' + k]) - ml
            out.append(f'<rect x="{x0:.1f}" y="{y + 4}" width="{w:.1f}" height="{alto - 9}" fill="{COLC[k]}"><title>{esc(d["nombre"])}, '
                       f'{CORTO[k]}: {p(d["%" + k])} %</title></rect>')
            if w > 24:
                out.append(f'<text x="{x0 + 4:.1f}" y="{y + alto / 2 + 4:.1f}" style="fill:var(--bg);font-weight:600">{p(d["%" + k])}</text>')
            x0 += w
    out.append('</svg>')
    return ''.join(out)


TABLA = (['Departamento', 'Peña (%)', 'Alegre (%)', 'Cubas (%)', 'Más votado', 'Votos emitidos'],
         [[d['nombre'], p(d['%pena']), p(d['%alegre']), p(d['%cubas']), CORTO[d['gana']], n(d['emitidos'])] for d in ORD])
FUENTE_V = ('Fuente: Tribunal Superior de Justicia Electoral (TSJE), resultados de 2023 por departamento según la tabla de '
            '<a href="https://es.wikipedia.org/wiki/Elecciones_generales_de_Paraguay_de_2023">Wikipedia</a>; sin el voto en el exterior. '
            'Porcentajes sobre votos emitidos (incluidos blancos y nulos), como los da el TSJE. Cálculo propio.')

g_mapa = figura(f'Peña ganó en {len(GANA["pena"])} de los 18 departamentos; Cubas, solo en Alto Paraná',
                'Candidato más votado en cada departamento y en Asunción en las presidenciales del 30 de abril de 2023. '
                'Tono claro: menos del 40 % de los votos; medio, del 40 % al 50 %; intenso, más del 50 %',
                mapa(), FUENTE_V + ' Contornos: geoBoundaries (DGEEC), CC BY 4.0.',
                [(NOMC[k], COLC[k]) for k in ('pena', 'alegre', 'cubas')], TABLA)
g_apil = figura(f'Peña superó el 50 % en {len(MAS50)} departamentos; en Central, el de más electores, se quedó en el {p(CENTRAL["%pena"])} %',
                'Porcentaje de votos de Santiago Peña, Efraín Alegre y Paraguayo Cubas en cada departamento en 2023, ordenados por el voto a Peña',
                apiladas(), FUENTE_V, [(NOMC[k], COLC[k]) for k in ('pena', 'alegre', 'cubas')], TABLA)

# --- Las votaciones del Congreso ---
g_votos = figura('El Senado lo destituyó con 44 de sus 45 votos',
                 'Votación del Senado, constituido en tribunal, el 6 de noviembre de 2026. Un cuadrado por senador',
                 cuadrados([('A favor de destituirlo', 44, 'var(--fg)', .85), ('Ausente: Enrique Riera', 1, 'var(--otros)', 1)],
                           'Votación del Senado sobre la destitución de Peña', por_fila=15, lado=20)
                 + cuadrados([('En contra de darle 72 horas más para su defensa', 39, 'var(--fg)', .85), ('A favor', 3, 'var(--fg)', .35),
                              ('Abstenciones', 2, 'var(--otros)', 1)], 'Votación del Senado sobre la prórroga pedida por Peña', por_fila=15, lado=20),
                 'Fuente: <a href="{ABC_VIVO}">ABC Color</a>, directo del juicio político (6-11-2026). La prórroga se votó a las 11.42; la destitución, a las 18.55. '
                 'El Senado tiene 45 miembros; hacían falta dos tercios.',
                 None,
                 (['Votación', 'A favor', 'En contra', 'Abstenciones', 'Ausentes'],
                  [['Prórroga de 72 horas para la defensa', '3', '39', '2', '1'], ['Destitución', '44', '0', '0', '1']]))

# --- Los fondos del IPS en Ueno ---
IPS = [('Sept. 2023', 70_000), ('Dic. 2023', 250_170), ('Dic. 2024', 1_770_000), ('Abr. 2026', 2_150_000)]
X_IPS = IPS[-1][1] / IPS[0][1]
fmt_g = lambda v: (f'{n(v / 1e6, 2)} billones' if v >= 1e6 else f'{n(v)} millones')
g_ips = figura(f'El dinero del IPS en Ueno se multiplicó por más de {math.floor(X_IPS / 10) * 10} con Peña en el Gobierno, según la acusación',
               'Saldo de la caja de pensiones pública (Instituto de Previsión Social) en Ueno Bank, en guaraníes',
               barras([(a, v, 'var(--acc)', fmt_g(v)) for a, v in IPS], IPS[-1][1] * 1.3, 'Saldo del IPS en Ueno Bank', W=430, ml=78, separar=True),
               'Fuente: datos presentados en el juicio político por el diputado acusador Raúl Benítez, según <a href="{ABC_VIVO}">ABC Color</a> (6-11-2026). '
               'No son cifras auditadas: son las de la acusación.',
               None, (['Fecha', 'Saldo (guaraníes)'], [[a, fmt_g(v)] for a, v in IPS])).replace('{ABC_VIVO}', '__ABC__')
g_votos = g_votos.replace('{ABC_VIVO}', '__ABC__')

# --- Texto ---
SLUG = 'paraguay-pena-destituido-mapa-departamentos'
ABC_VIVO = 'https://www.abc.com.py/politica/2026/11/06/en-vivo-juicio-politico-a-pena-senado-retoma-proceso-en-medio-de-renuncia-trabada-y-pedido-de-prorroga/'
ABC_DEST = 'https://www.abc.com.py/politica/2026/11/06/santiago-pena-destituido-el-segundo-presidente-echado-por-juicio-politico-y-el-primero-casi-por-unanimidad/'
ABC_REN = 'https://www.abc.com.py/politica/2026/11/05/renuncio-santiago-pena-la-caida-del-presidente-por-el-caso-ueno-bank/'
LT = 'https://www.latercera.com/mundo/noticia/senado-de-paraguay-inicia-juicio-politico-contra-santiago-pena-tras-frustrarse-votacion-de-su-renuncia/'
VOZ = 'https://www.vozpopuli.com/internacional/santiago-pena-es-destituido-como-presidente-de-paraguay-y-detenido-pedro-alliana-asume-el-liderazgo-del-pais.html'
SEM = 'https://www.semana.com/mundo/articulo/fiscalia-de-paraguay-toma-decision-final-sobre-el-caso-del-expresidente-santiago-pena/202611/'
UH = 'https://www.ultimahora.com/tsje-proclamara-esta-tarde-ganadores-las-elecciones-2023-n3064211'
WIKI = 'https://es.wikipedia.org/wiki/Elecciones_generales_de_Paraguay_de_2023'
g_votos = g_votos.replace('__ABC__', ABC_VIVO)
g_ips = g_ips.replace('__ABC__', ABC_VIVO)

H1 = ('Paraguay destituye a Santiago Peña, el presidente que en 2023 ganó en 17 de los 18 departamentos')
DEK = ('El Senado lo condenó el viernes por mal desempeño de funciones, con 44 votos de 45, por el hundimiento de Ueno Bank, '
       'un banco del que fue accionista. Pedro Alliana, su vicepresidente, gobernará hasta 2028. Peña había ganado con el '
       f'{p(NAC_PCT)} % de los votos; solo perdió en Alto Paraná.')
cuerpo = f"""{EST}
{g_mapa}
<p data-tipo="dato">El Senado de Paraguay destituyó el viernes 6 de noviembre al presidente Santiago Peña por mal desempeño de funciones. Votaron a favor 44 de los 45 senadores; el único ausente fue Enrique Riera, que acababa de dejar el Ministerio del Interior de Peña, según <a href="{ABC_DEST}">ABC Color</a>. Hacían falta dos tercios, 30 votos, según <a href="{LT}">La Tercera</a>. El día antes, la Cámara de Diputados había aprobado la acusación con sus 78 miembros en activo. Pedro Alliana, vicepresidente desde 2023, juró el cargo esa misma noche en una sesión extraordinaria del Congreso y gobernará hasta agosto de 2028, cuando acaba el mandato, según <a href="{VOZ}">Vozpópuli</a>.</p>
<p data-tipo="contexto">Peña es el segundo presidente elegido desde la caída de la dictadura de Alfredo Stroessner, en 1989, que el Congreso destituye en un juicio político, después de Fernando Lugo en junio de 2012. ABC Color subraya la diferencia: con Lugo el voto estuvo más dividido y con Peña hubo casi unanimidad, pese a que tenía mayoría propia en las dos cámaras.</p>
<h2>Un banco y cuatro días</h2>
<p data-tipo="dato">Todo pasó en cuatro días. El martes 3, el Banco Central del Paraguay (BCP) dispuso la resolución de Ueno Bank porque su índice de solvencia había caído por debajo del 50 % del mínimo exigido. Las aplicaciones y las tarjetas del banco dejaron de funcionar para casi tres millones de clientes, según <a href="{ABC_REN}">ABC Color</a>, en un país de 6,1 millones de habitantes, según <a href="{VOZ}">Vozpópuli</a>. Peña había sido accionista de Ueno Holding hasta 2025.</p>
<p data-tipo="dato">El jueves 5, Peña anunció su renuncia en un vídeo grabado en la residencia presidencial. El Congreso no llegó a aceptarla: los diputados colorados se retiraron y la sesión se quedó sin quórum, según <a href="{LT}">La Tercera</a>. La oposición no quería que Peña se fuera como dimitido, porque los expresidentes son senadores vitalicios, con fueros, salvo que hayan sido «sometidos a juicio político y hallados culpables», como dice el artículo 189 de la Constitución que recoge <a href="{VOZ}">Vozpópuli</a>.</p>
<blockquote class="cita"><p>«He tomado la decisión de presentar mi renuncia a la Presidencia de la República. Lo hago pensando en la estabilidad de nuestro país, en la paz social y en la necesidad de preservar nuestras instituciones democráticas»</p><footer>Santiago Peña, en un vídeo el 5 de noviembre. Recogido por <a href="{ABC_REN}">ABC Color</a></footer></blockquote>
<p data-tipo="dato">Esa misma noche, el Senado se constituyó en tribunal. El viernes, Peña pidió 72 horas más para preparar su defensa y el Senado se las negó a las 11.42, con 39 votos en contra, 3 a favor y 2 abstenciones, según el directo de <a href="{ABC_VIVO}">ABC Color</a>. Peña no se presentó: lo defendieron sus abogados Ricardo Preda y Adolfo Ferreiro, que denunciaron indefensión. A las 18.55 llegó la condena.</p>
{g_votos}
<h2>El dinero de las pensiones</h2>
<p data-tipo="dato">El centro de la acusación fue el dinero público depositado en Ueno. En septiembre de 2026, los fondos de organismos públicos en el banco sumaban unos 3,6 billones de guaraníes, casi 233 millones de dólares, según la Fiscalía, que recoge <a href="{SEM}">Semana</a>. Durante el juicio, el diputado acusador Raúl Benítez mostró cómo creció el saldo del Instituto de Previsión Social (IPS), la principal caja de pensiones pública: de 70.000 millones de guaraníes en septiembre de 2023, un mes después de que Peña llegara al poder, a 2,15 billones en abril de 2026, según <a href="{ABC_VIVO}">ABC Color</a>. Unos 32.000 jubilados del IPS estaban entre los ahorradores que no podían sacar su dinero, según <a href="{VOZ}">Vozpópuli</a>.</p>
{g_ips}
<p data-tipo="contexto">La diputada Rocío Vallejo dijo en el juicio que Peña «creó un agujero de 1.200 millones de dólares al pueblo paraguayo», según <a href="{VOZ}">Vozpópuli</a>. Es la cifra de la acusación, no una cuenta oficial. Los gremios de asegurados hablaban de más de 860 millones de dólares de fondos públicos y previsionales, según <a href="{ABC_REN}">ABC Color</a>.</p>
<p data-tipo="dato">A las 19.41, la Fiscalía pidió su detención, y la Policía la ejecutó en su casa a las 20.05, según <a href="{ABC_VIVO}">ABC Color</a>. El sábado 7, el Ministerio Público lo imputó por lesión de confianza, como instigador, y administración en provecho propio, como autor, y pidió prisión preventiva para él y para el expresidente del BCP Carlos Carvallo, según <a href="{SEM}">Semana</a>. Según la Fiscalía, Peña «habría intervenido en decisiones vinculadas a la colocación, renovación y permanencia de fondos públicos y previsionales en Ueno Bank». Peña había dicho que se defendería.</p>
<blockquote class="cita"><p>«Ante la continuidad del juicio político, me presentaré y ejerceré mi derecho a la defensa. Lo haré con argumentos y pruebas, con respeto a la Constitución y a las instituciones de la República»</p><footer>Santiago Peña, el 5 de noviembre. Recogido por <a href="{LT}">La Tercera</a></footer></blockquote>
<h2>El mapa que ganó en 2023</h2>
<p data-tipo="dato">Peña llegó a la presidencia en agosto de 2023 con una victoria amplia. En las elecciones del 30 de abril sacó {n(NAC["pena"])} votos, el {p(NAC_PCT)} % de los emitidos, frente a los {n(NAC["alegre"])} de Efraín Alegre, de la Concertación opositora, según el cómputo que proclamó el Tribunal Superior de Justicia Electoral (TSJE) y recogió <a href="{UH}">Última Hora</a>. Paraguayo Cubas, de Cruzada Nacional, quedó tercero. En Paraguay no hay segunda vuelta: gana el más votado.</p>
<p data-tipo="dato">Peña fue el más votado en {len(GANA["pena"])} de los 18 departamentos, contando Asunción. Solo perdió en Alto Paraná, en la frontera con Brasil y Argentina, donde Cubas sacó el {p(ALTO["%cubas"])} % y Peña, el {p(ALTO["%pena"])} %. Superó el 50 % en {len(MAS50)} departamentos; su mejor resultado fue Alto Paraguay, en el Chaco, con el {p(D["Alto Paraguay"]["%pena"])} %. En Asunción, la capital, sacó el {p(D["Asunción"]["%pena"])} %. En Central, el departamento con más votantes, que rodea la capital, se quedó en el {p(CENTRAL["%pena"])} %, frente al {p(CENTRAL["%alegre"])} % de Alegre y el {p(CENTRAL["%cubas"])} % de Cubas.</p>
{g_apil}
<p data-tipo="hipotesis">Ese mapa no dice nada de cómo votarían hoy los paraguayos: las próximas generales son en 2028. Lo que sí muestra es que Peña no ganó con un país partido en dos regiones, sino con un voto repartido por casi todo el territorio. La única excepción, Alto Paraná, es también el departamento donde Cubas logró su mejor resultado.</p>
<p data-tipo="contexto">Alliana prometió compensar a los afectados en su primer discurso.</p>
<blockquote class="cita"><p>«Lo que vengo a prometer es concreto: los compatriotas que hoy atraviesan un momento difícil a consecuencia del descalabro financiero serán compensados plenamente. No los vamos a dejar solos»</p><footer>Pedro Alliana, tras jurar como presidente el 6 de noviembre. Recogido por <a href="{VOZ}">Vozpópuli</a></footer></blockquote>
"""
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')
preguntas = [
    ('¿Por qué destituyeron a Santiago Peña?', 'El Senado lo condenó por mal desempeño de funciones por el caso Ueno Bank, un banco del que había sido accionista y en el que se depositaron fondos públicos y de pensiones. El BCP dispuso su resolución el 3 de noviembre de 2026.'),
    ('¿Quién gobierna ahora Paraguay?', 'Pedro Alliana, que era vicepresidente. Juró el 6 de noviembre de 2026 y gobernará hasta agosto de 2028.'),
    ('¿Por qué no aceptaron su renuncia?', 'El Congreso no llegó a votarla porque la sesión se quedó sin quórum. Con la destitución, Peña no será senador vitalicio y no tendrá fueros.'),
    ('¿Cuánto votó Paraguay a Peña en 2023?', f'El {p(NAC_PCT)} % de los votos emitidos: {n(NAC["pena"])}. Ganó en {len(GANA["pena"])} de los 18 departamentos; solo perdió en Alto Paraná.'),
]
enlaces = ('Más mapas electorales del mundo en <a href="../../temas/internacional/">Internacional</a>.')
foot = ('Datos: resultados de las presidenciales de 2023 del TSJE por departamento, según la tabla de Wikipedia; el cómputo definitivo '
        '(Acuerdo y Sentencia 15/2023) no se puede descargar hoy de la web del TSJE. Sin el voto en el exterior. Cronología: ABC Color, '
        'La Tercera, Semana y Vozpópuli.')
DATOS = {'DEP': {d['nombre']: {k: d[k] for k in ('pena', 'alegre', 'cubas', 'emitidos', '%pena', '%alegre', '%cubas', 'gana')} for d in DEP},
         'NAC': NAC, 'NAC_PCT': NAC_PCT, 'GANA': GANA, 'MAS50': MAS50, 'IPS': IPS}
scripts = f'<script>const D={json.dumps(DATOS, ensure_ascii=False)};</script>\n'
pieza(SLUG, 'Paraguay destituye a Peña', H1, DEK, '10 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts)
