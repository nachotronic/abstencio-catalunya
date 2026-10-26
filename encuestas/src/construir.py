"""Genera /encuestas/: todas las encuestas publicadas de las generales del 29N, con su fuente original.

Lee los CSV que actualiza cada día el workflow «Encuestas» (previsiones/datos/encuestas/) y escribe
encuestas/index.html y encuestas/sitemap.xml. El workflow lo vuelve a ejecutar cuando llega una encuesta nueva, así
que la página se refresca sola. Solo usa la biblioteca estándar.

Qué publica: las cifras de cada encuesta tal como las publicó su encuestadora (voto y escaños), la mediana de las
encuestas recientes como resumen descriptivo y, en un bloque aparte, la estimación del modelo de previsiones/src si
el hilo del modelo ha dejado una salida publicable en previsiones/datos/publico/ (Nacho lo aprobó el 22-10-2026).
Esa estimación no se recalcula aquí: cambia cuando se copia una salida nueva a esa carpeta.

Fuentes: Electográfica (agregador, para localizar las encuestas y su ficha técnica) y la tabla de Wikipedia (CC BY-SA),
que añade los escaños de cada encuestadora y los sondeos que Electográfica no recoge (ElectoPanel de Electomanía).
Se enlaza siempre la publicación original.

También escribe encuestas/insertar.html (resumen para iframe) y, con Pillow, la tarjeta img/compartir/encuestas.jpg.

Uso, desde la raíz:  python3 encuestas/src/construir.py
"""
import csv, html, json, math, os, pathlib, re, statistics, sys, unicodedata
from datetime import date, timedelta

sys.dont_write_bytecode = True   # no ensuciar los .pyc que hay en el repositorio
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'actualidad' / 'src'))
from construir import AUTOR, BASE, CSS_SITIO, MEDIO, cabecera, fecha_larga, nav  # noqa: E402
try:   # tarjeta para redes; sin Pillow, la página se rehace igual y la imagen se queda como estaba
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    from tarjeta import tarjeta
except ImportError:
    tarjeta = None
import encuestadoras  # noqa: E402  (una página por encuestadora)
import calculadora  # noqa: E402  (calculadora de escaños)

DATOS = RAIZ / 'previsiones/datos/encuestas'
SALIDA = RAIZ / 'encuestas'
URL = BASE + '/encuestas/'
# los seis partidos de ámbito estatal que miden todas las encuestas, con su color (claro, oscuro)
PRINCIPALES = [('PP', 'PP', '#1d84ce', '#4fa8ea'), ('PSOE', 'PSOE', '#e30613', '#ff5a5f'), ('VOX', 'Vox', '#5ac035', '#74d651'),
               ('SUMAR', 'Sumar / Frente Amplio', '#a2275f', '#d0679a'), ('PODEMOS', 'Podemos', '#5a3c8f', '#8a6fe0'),
               ('SALF', 'SALF', '#785a46', '#a9876f')]
# el resto de partidos con escaño, para el hemiciclo
OTROS_ESC = [('ERC', 'ERC', '#f5b324', '#f7c454'), ('JUNTS', 'Junts', '#20c0b2', '#2fd0c2'), ('BILDU', 'EH Bildu', '#a5c400', '#b9d630'),
             ('PNV', 'PNV', '#2b8a3e', '#4caf63'), ('BNG', 'BNG', '#4a9fdc', '#7ab8e6'), ('CC', 'CC', '#f7d417', '#f9e04a'),
             ('UPN', 'UPN', '#0b3d91', '#5b7fd0'), ('ALIANCA', 'Aliança Catalana', '#064a81', '#4a86c0'), ('CS', 'Ciudadanos', '#eb6109', '#f28a45'),
             ('NC', 'Nueva Canarias', '#e08a2e', '#f0a050'), ('CUP', 'CUP', '#d4b200', '#f0d000')]
TODOS = PRINCIPALES + OTROS_ESC
# orden aproximado de izquierda a derecha en el hemiciclo
ORDEN_HEMI = ['BILDU', 'CUP', 'BNG', 'PODEMOS', 'SUMAR', 'ERC', 'NC', 'PSOE', 'PNV', 'JUNTS', 'CC', 'CS', 'UPN', 'PP', 'ALIANCA', 'SALF', 'VOX']
NOMBRE = {k: n for k, n, _, _ in TODOS}
NO_ENCUESTAS = {'keydata', 'sumar', 'psoe', 'pp', 'vox', 'podemos'}   # medias de otros medios y sondeos internos de partido
DESDE_GRAFICO = 365   # días que enseña el gráfico
VISIBLES = 10
# Estimación propia (motor de /previsiones/): solo se publica si existe esta carpeta, que el hilo del modelo llena
# cuando Nacho valida sus cifras. Sin ella, la página no enseña nada del modelo.
ESTIMACION = pathlib.Path(os.environ.get('ESTIMACION_DIR', RAIZ / 'previsiones/datos/publico'))
DEL_MODELO = {'PP': 'PP', 'PSOE': 'PSOE', 'Vox': 'VOX', 'Sumar': 'SUMAR', 'Podemos': 'PODEMOS', 'SALF': 'SALF', 'ERC': 'ERC',
              'Junts': 'JUNTS', 'EH Bildu': 'BILDU', 'PNV': 'PNV', 'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN', 'Aliança': 'ALIANCA',
              'Nueva Canarias': 'NC', 'CUP': 'CUP'}
VENTANA_MEDIANA = 21


def clave(nombre):
    s = unicodedata.normalize('NFKD', str(nombre)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def carga():
    """Encuestas nacionales: las de Electográfica más las que solo están en Wikipedia; escaños de Wikipedia."""
    wp = list(csv.DictReader(open(DATOS / 'wikipedia_generales_espana.csv'))) if (DATOS / 'wikipedia_generales_espana.csv').exists() else []
    eg = [r for r in csv.DictReader(open(DATOS / 'encuestas_limpias.csv')) if r['ambito'] == 'ESPAÑA']
    usadas, out = set(), []

    def pareja(casa, fin):
        for i, w in enumerate(wp):
            c = clave(w['encuestadora'])
            if i not in usadas and not w.get('reestimacion') and (c.startswith(casa) or casa.startswith(c)) and abs((date.fromisoformat(w['campo_fin']) - fin).days) <= 4:
                return i
        return None

    for r in eg:
        fin = date.fromisoformat(r['campo_fin']) if r['campo_fin'] else date.fromisoformat(r['publicado']) - timedelta(days=3)
        i = pareja(clave(r['encuestadora']), fin)
        w = wp[i] if i is not None else {}
        if i is not None:
            usadas.add(i)
        out.append({'reest': False, 'casa': r['encuestadora'], 'medio': '' if r['cliente'] in ('', 'n/a') else r['cliente'],
                    'inicio': r['campo_inicio'] or w.get('campo_inicio', ''), 'fin': fin.isoformat(), 'fin_aprox': not r['campo_fin'] and not w,
                    'publicado': r['publicado'], 'muestra': r['muestra'] or w.get('muestra', ''),
                    'voto': {k: num(r[k]) for k, *_ in PRINCIPALES if num(r[k]) is not None},
                    'esc': {k: w.get(f'esc_{k}', '') for k, *_ in TODOS if w.get(f'esc_{k}')},
                    'url': r['fuente_original'] or w.get('fuente_original', '') or r['url_agregador']})
    for i, w in enumerate(wp):
        if i in usadas:
            continue
        if w.get('reestimacion'):   # datos brutos del CIS recalculados por otra empresa: solo en la tabla, con su nombre
            w = dict(w, encuestadora=f'{w["encuestadora"]} reestimado por {w["reestimacion"]}')
        out.append({'reest': bool(w.get('reestimacion')), 'casa': w['encuestadora'], 'medio': w['cliente'], 'inicio': w['campo_inicio'], 'fin': w['campo_fin'], 'fin_aprox': False,
                    'publicado': '', 'muestra': w['muestra'], 'voto': {k: num(w[k]) for k, *_ in PRINCIPALES if num(w[k]) is not None},
                    'esc': {k: w[f'esc_{k}'] for k, *_ in TODOS if w.get(f'esc_{k}')}, 'url': w['fuente_original']})
    out = [e for e in out if clave(e['casa']) not in NO_ENCUESTAS and 'PP' in e['voto'] and 'PSOE' in e['voto']]
    return sorted(out, key=lambda e: (e['fin'], e['casa']), reverse=True)


def medianas(encs, hasta):
    """Mediana diaria de cada partido con la última encuesta de cada encuestadora en los 21 días anteriores."""
    serie = []
    d = hasta - timedelta(days=DESDE_GRAFICO)
    while d <= hasta:
        ult = {}
        for e in encs:
            f = date.fromisoformat(e['fin'])
            if d - timedelta(days=VENTANA_MEDIANA) < f <= d and not e['reest'] and clave(e['casa']) not in ult:
                ult[clave(e['casa'])] = e   # encs va de más reciente a más antigua
        fila = {'d': d.isoformat()}
        for k, *_ in PRINCIPALES:
            v = [e['voto'][k] for e in ult.values() if k in e['voto']]
            if len(v) >= 3:
                fila[k] = round(statistics.median(v), 1)
        serie.append(fila)
        d += timedelta(days=1)
    return serie


def rango_esc(t):
    a, _, b = t.partition('-')
    return int(a), int(b or a)


def suma_pv(e):
    """Escaños de PP + Vox en una encuesta: (extremo bajo, extremo alto)."""
    (a, b), (c, d) = rango_esc(e['esc']['PP']), rango_esc(e['esc']['VOX'])
    return a + c, b + d


def promedio_escanos(con_esc):
    """Promedio de los escaños que publica cada encuestadora (centro del intervalo), solo las que dan el reparto
    completo (suman entre 345 y 350), redondeado por restos mayores al total promediado."""
    completas = []
    for e in con_esc:
        mid = {k: sum(rango_esc(v)) / 2 for k, v in e['esc'].items()}
        if 345 <= sum(mid.values()) <= 350:
            completas.append(mid)
    if len(completas) < 3:
        return None, 0
    media = {k: sum(m.get(k, 0) for m in completas) / len(completas) for k in ORDEN_HEMI}
    total = round(sum(media.values()))
    base = {k: int(v) for k, v in media.items()}
    for k in sorted(media, key=lambda k: media[k] - base[k], reverse=True)[:total - sum(base.values())]:
        base[k] += 1
    return {k: v for k, v in base.items() if v}, len(completas)


MODELO_JS = {}   # datos de los gráficos de horquillas del modelo, que estimacion() deja para el script


def estimacion():
    """Bloque «Estimación de Mapa Electoral» y escaños centrales para su hemiciclo; (None, None) si no hay salida publicable."""
    if not (ESTIMACION / 'escenario-base.json').exists():
        return None, None
    d = json.load(open(ESTIMACION / 'escenario-base.json'))
    meta = json.load(open(ESTIMACION / 'meta.json'))
    if meta.get('interno', True) or meta.get('ficticio'):   # salida interna o de prueba: no se publica
        return None, None
    hemi = {DEL_MODELO[k]: v for k, v in d['hemiciclo']['congreso'].items() if k in DEL_MODELO and v}
    filas = ''
    central = d['hemiciclo']['congreso']   # el mismo reparto que el hemiciclo
    for l in sorted(d['listas'], key=lambda l: (-central.get(l['lista'], 0), -l['escanos'][2])):
        if l['lista'] not in DEL_MODELO or l['escanos'][3] < 1:
            continue
        k = DEL_MODELO[l['lista']]
        c = next(c for kk, _, c, _ in TODOS if kk == k)
        filas += (f'<tr><td><i class="pt" style="background:{c}"></i>{NOMBRE[k]}</td><td class="n">{pc(l["voto"][2])}</td>'
                  f'<td class="n"><b>{central.get(l["lista"], 0)}</b></td><td class="n">{round(l["escanos"][1])}-{round(l["escanos"][3])}</td></tr>')
    pv = next((b for b in d['bloques'] if b['listas'] == ['PP', 'Vox']), None)
    izq = next((b for b in d['bloques'] if b['bloque'].startswith('PSOE + Sumar + Podemos + ERC')), None)
    prob = lambda p: f'{round(p * 100)} %' if 0.01 <= p <= 0.99 else ('menos del 1 %' if p < 0.01 else 'más del 99 %')
    frase = ''
    if pv:
        frase += (f'PP y Vox suman {round(pv["escanos"][2])} escaños en el escenario central (entre {round(pv["escanos"][1])} y {round(pv["escanos"][3])} '
                  f'en el 80 % de las simulaciones) y llegan a 176 en el {prob(pv["p_mayoria"])} de ellas.')
    if izq:
        frase += f' Los socios de la investidura de 2023 llegan a 176 en el {prob(izq["p_mayoria"])}.'
    color = lambda l: next((c, o) for kk, _, c, o in TODOS if kk == DEL_MODELO[l])
    r0 = lambda a: [round(x) for x in a]
    # horquillas: percentiles 2,5 / 10 / 50 / 90 / 97,5 de las simulaciones (motor.py)
    MODELO_JS['bloques'] = [[n, *color(cl), r0(b['escanos']), round(b['p_mayoria'] * 100)] for b, n, cl in
                            ((pv, 'PP + Vox', 'PP'), (izq, 'Socios de 2023', 'PSOE')) if b]
    MODELO_JS['partidos'] = [[NOMBRE[DEL_MODELO[l['lista']]].replace(' / Frente Amplio', ''), *color(l['lista']), r0(l['escanos'])]
                             for l in sorted(d['listas'], key=lambda l: -l['escanos'][2]) if l['lista'] in DEL_MODELO and l['escanos'][3] >= 1]
    MODELO_JS['dist_bloques'] = [[n, *color(cl), b['escanos_dist']['desde'], b['escanos_dist']['p'], r0(b['escanos'])] for b, n, cl in
                                 ((pv, 'PP + Vox', 'PP'), (izq, 'Socios de 2023', 'PSOE')) if b and 'escanos_dist' in b]
    MODELO_JS['dist'] = [[NOMBRE[DEL_MODELO[l['lista']]].replace(' / Frente Amplio', ''), *color(l['lista']), l['escanos_dist']['desde'], l['escanos_dist']['p'], r0(l['escanos'])]
                         for l in sorted(d['listas'], key=lambda l: -l['escanos'][2])[:4] if l['lista'] in DEL_MODELO]
    html_b = f"""<h2>Estimación propia de Mapa Electoral</h2>
<p class="propio"><b>Modelo propio, no es una encuesta.</b> Todo lo anterior son cifras publicadas por las encuestadoras. Esto es un cálculo de Mapa Electoral: junta esas encuestas, las reparte por provincia y simula el resultado miles de veces.</p>
<div class="prob">{''.join(f'<div><b style="color:{c}">{prob(b["p_mayoria"])}</b><span>de las simulaciones: {n} llegan a 176 escaños</span></div>'
                          for b, n, c in ((pv, 'PP y Vox', '#1d84ce'), (izq, 'los socios de investidura de 2023', '#e30613')) if b)}</div>
<p>{frase}</p>
<p><a href="calculadora-escanos/">Prueba tus propios porcentajes en la calculadora de escaños</a>: reparte los 350 diputados provincia a provincia con la ley D'Hondt.</p>
<figure><figcaption><span class="t">Cuántos escaños suma cada bloque</span><span class="s">Cada columna es un número de escaños y su altura, el porcentaje de las {meta['simulaciones']:,} simulaciones en que sale. La línea marca la mayoría absoluta; en color intenso, la horquilla del 80 %.</span></figcaption>
<div class="chart" id="dist-bloques"></div></figure>
<figure><figcaption><span class="t">¿Llegan a la mayoría absoluta? Escaños de cada bloque</span><span class="s">La barra gruesa recoge el 80 % de las simulaciones; la fina, el 95 %; el punto es la mediana. A la derecha, en qué porcentaje de simulaciones llega a 176.</span></figcaption>
<div class="chart" id="horq-bloques"></div></figure>
<figure><figcaption><span class="t">Congreso según nuestro modelo: escaños en el escenario central</span><span class="s">Media de encuestas repartida por provincia y simulada {meta['simulaciones']:,} veces con el error histórico de las encuestas. Generado el {fecha_larga(meta['generado'])}.</span></figcaption>
<div class="chart" id="hemi-modelo"></div></figure>
<div class="tbl"><table><thead><tr><th>Partido</th><th class="n">Voto</th><th class="n">Escaños (central)</th><th class="n">Horquilla 80 %</th></tr></thead><tbody>{filas}</tbody></table></div>
<figure><figcaption><span class="t">Horquilla de escaños de cada partido</span><span class="s">Barra gruesa: 80 % de las simulaciones; fina: 95 %; punto: mediana.</span></figcaption>
<div class="chart" id="horq-partidos"></div></figure>
<figure><figcaption><span class="t">Cuántas veces sale cada resultado</span><span class="s">Cada columna es un número de escaños y su altura, el porcentaje de las simulaciones en que sale. En color intenso, la horquilla del 80 %.</span></figcaption>
<div class="chart" id="dist-modelo"></div></figure>
<p><a href="provincias.html">Escaños provincia a provincia según el modelo, con las más disputadas →</a></p>
<p class="src">Es una estimación, no un resultado: una de cada cinco veces el resultado real de un partido caerá fuera de su horquilla. {html.escape(meta.get('aviso', ''))} <a href="metodo-modelo.html">Cómo se calcula</a> · <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/previsiones">código</a>.</p>""".replace(f"{meta['simulaciones']:,}", f"{meta['simulaciones']:,}".replace(',', '.'))
    return html_b, hemi


def pc(v):
    return f'{v:.1f}'.replace('.', ',') + '\u00a0%'


def textos(encs, hoy):
    """Titular, entradilla y párrafos calculados con las encuestas (todo dato, sin interpretación)."""
    mes = [e for e in encs if date.fromisoformat(e['fin']) > hoy - timedelta(days=30) and not e['reest']]
    ultimas, vistos = [], set()
    for e in mes:
        if clave(e['casa']) not in vistos:
            vistos.add(clave(e['casa'])); ultimas.append(e)
    lider = lambda e: max(e['voto'], key=e['voto'].get)
    from collections import Counter
    cuenta = Counter(lider(e) for e in ultimas)
    primero, n1 = cuenta.most_common(1)[0]
    n = len(ultimas)
    tercero_vox = sum(1 for e in ultimas if sorted(e['voto'], key=e['voto'].get, reverse=True)[2:3] == ['VOX'])
    art = '' if primero in ('VOX', 'SUMAR', 'PODEMOS', 'SALF') else 'El '
    gana = f'{art}{NOMBRE[primero]} gana en las {n} encuestas' if n1 == n else f'{art}{NOMBRE[primero]} gana en {n1} de {n} encuestas'
    rangos = {k: (min(e['voto'][k] for e in ultimas if k in e['voto']), max(e['voto'][k] for e in ultimas if k in e['voto']))
              for k in ('PP', 'PSOE', 'VOX')}
    entradilla = (f'Últimas encuestas de las elecciones generales: con la última de cada encuestadora en los últimos 30 días, el PP va del {pc(rangos["PP"][0])} al {pc(rangos["PP"][1])}, '
                  f'el PSOE del {pc(rangos["PSOE"][0])} al {pc(rangos["PSOE"][1])} y Vox del {pc(rangos["VOX"][0])} al {pc(rangos["VOX"][1])}. '
                  'Todas las encuestas publicadas, con su fuente, actualizadas cada día.')
    disidentes = [e for e in ultimas if lider(e) != primero]
    p1 = (f'{n} encuestadoras han publicado al menos una encuesta de las generales con trabajo de campo terminado en los últimos 30 días. '
          + (f'Todas dan ganador al {NOMBRE[primero]}. ' if not disidentes else
             f'{n1} dan ganador al {NOMBRE[primero]}; ' + '; '.join(f'{"el " if e["casa"] == "CIS" else ""}{e["casa"]}, al {NOMBRE[lider(e)]}' for e in disidentes) + '. ')
          + ('Vox queda tercero en todas.' if tercero_vox == n else f'Vox queda tercero en {tercero_vox}.' if tercero_vox else ''))
    con_esc = [e for e in ultimas if 'PP' in e['esc'] and 'VOX' in e['esc']]
    mayoria = sum(1 for e in con_esc if rango_esc(e['esc']['PP'])[0] + rango_esc(e['esc']['VOX'])[0] >= 176)
    # titular breve: última encuesta de cada encuestadora en 30 días; la mayoría, solo en las que dan escaños
    if con_esc:
        con_vox = 'con Vox' if primero == 'PP' else 'PP y Vox'
        en = f'las {mayoria} con escaños' if mayoria == len(con_esc) else f'{mayoria} de {len(con_esc)} con escaños'
        titular = f'{gana}; {con_vox}, mayoría absoluta en {en}'
    else:
        titular = gana
    p2 = ((f'Las {mayoria} que publican escaños dan' if mayoria == len(con_esc) else f'De las {len(con_esc)} que publican escaños, {mayoria} dan')
          + ' al PP y a Vox juntos 176 o más, la mayoría absoluta del Congreso (con un intervalo, se cuenta el extremo bajo).') if con_esc else ''
    return titular, entradilla, p1, p2, ultimas, con_esc, mayoria


MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']


def dia(iso, anio=False):
    d = date.fromisoformat(iso)
    return f'{d.day} {MESES[d.month - 1]}' + (f' {d.year}' if anio else '')


def fechas_celda(e):
    """Fecha de publicación; si no consta (encuestas que solo recoge Wikipedia), fin del trabajo de campo con asterisco."""
    iso = e.get('publicado') or e['fin']
    return dia(iso, date.fromisoformat(iso).year != date.today().year) + ('' if e.get('publicado') else '*')


def fila_tabla(e):
    casa = html.escape(e['casa']) + (f'<span class="medio">{html.escape(e["medio"])}</span>' if e['medio'] else '')
    enlace = f'<a href="{html.escape(e["url"])}">{casa}</a>' if e['url'] else casa
    campo = fechas_celda(e)
    muestra = f'{int(e["muestra"]):,}'.replace(',', '.') if str(e['muestra']).isdigit() else '–'
    celdas = ''.join(f'<td class="n">{str(e["voto"][k]).replace(".", ",") if k in e["voto"] else "–"}'
                     + (f'<small>{e["esc"][k]}</small>' if k in e['esc'] else '') + '</td>' for k, *_ in PRINCIPALES)
    return f'<tr><td>{enlace}</td><td class="n fecha">{campo}</td><td class="n">{muestra}</td>{celdas}</tr>'


ESTILOS = """<style>
:root{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf;--grid:#ebe7e8;--acc:#1d84ce;--tipbg:#1d1a1c;--tipfg:#fbfaf8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;--grid:#2c282e;--acc:#4fa8ea;--tipbg:#f1edef;--tipfg:#18161a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;--grid:#2c282e;--acc:#4fa8ea;--tipbg:#f1edef;--tipfg:#18161a;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.62}
main{max-width:46rem;margin:0 auto;padding-block:2.5rem 4rem;padding-inline:16px}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.12;font-weight:800;text-wrap:balance;margin:.8rem 0 .9rem}
.dek{font-size:1.15rem;line-height:1.5;color:var(--muted);margin:0 0 1rem}
h2{font-size:1.35rem;line-height:1.25;margin:2.4rem 0 .6rem;text-wrap:balance}
p{margin:0 0 1rem}
figure{margin:1.8rem 0 2rem;font-family:var(--ui)}
figcaption .t{font-weight:600;font-size:1.1rem;display:block;line-height:1.25}
figcaption .s{color:var(--muted);font-size:.95rem;display:block;margin-top:.15rem}
.src{color:var(--muted);font-size:.85rem;margin-top:.4rem;font-family:var(--ui)}
.chart{position:relative;margin-top:.7rem}
svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:var(--ui);fill:var(--muted);font-size:12px}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-size:.92rem;margin-top:.4rem;font-family:var(--ui)}
.legend span{display:inline-flex;align-items:center;gap:.35rem}
.sw{width:12px;height:12px;border-radius:50%;display:inline-block}
.tip{position:absolute;pointer-events:none;background:var(--tipbg);color:var(--tipfg);font-family:var(--ui);font-size:.85rem;line-height:1.35;padding:.35rem .55rem;border-radius:4px;white-space:nowrap;z-index:5;transform:translate(-50%,-110%)}
.tbl{overflow-x:auto;margin:0 -16px;padding:0 16px}
table{border-collapse:collapse;font-family:var(--ui);font-size:.9rem;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.35rem .4rem;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:600;font-size:.8rem;color:var(--muted);white-space:nowrap}
td.n,th.n{text-align:right;white-space:nowrap}
td.fecha{font-size:.85rem}
td small{display:block;color:var(--muted);font-size:.75rem}
td .medio{display:block;color:var(--muted);font-size:.8rem}
td a{color:var(--fg);text-decoration-color:var(--rule)}
th .pt,td .pt{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
tr.mayoria td.suma{font-weight:700}
details{font-family:var(--ui);margin-top:.6rem} summary{cursor:pointer;color:var(--muted)}
a{color:var(--acc)}
.faq details{border-bottom:1px solid var(--rule);margin:0;padding:.2rem 0}
.faq summary{color:var(--fg)}
.faq h3{display:inline;font-family:var(--ui);font-size:1.05rem;margin:0}
.faq details p{margin:.3rem 0 .8rem}
.descargas{font-family:var(--ui);font-size:.95rem}
.insertar textarea{width:100%;font:12px/1.45 monospace;color:var(--fg);background:var(--bg);border:1px solid var(--rule);border-radius:6px;padding:8px;margin-top:.4rem}
.prob{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:1rem 0;font-family:var(--ui)}.prob div{border:1px solid var(--rule);border-radius:6px;padding:.7rem .9rem}
.prob b{display:block;font-size:2.4rem;line-height:1.05;font-variant-numeric:tabular-nums}.prob span{display:block;color:var(--muted);font-size:.9rem;margin-top:.2rem}
.caja{font-family:var(--ui);font-size:.95rem;border:1px solid var(--rule);border-radius:6px;padding:.5rem .9rem;margin:1rem 0}.caja summary{color:var(--fg);font-weight:600}.caja ul{margin:.5rem 0;padding-left:1.1rem}.caja li{margin:.3rem 0}
@media (max-width:520px){.prob{grid-template-columns:1fr}}
.propio{font-family:var(--ui);font-size:.95rem;background:var(--grid);border-left:3px solid var(--acc);padding:.6rem .8rem;border-radius:4px}
@media (max-width:520px){body{font-size:17px}table{font-size:.82rem}}
</style>"""

SCRIPT = """<script>
(()=>{const D=window.__ENC=__DATOS__;
const NS='http://www.w3.org/2000/svg',box=document.getElementById('graf');
const osc=()=>document.documentElement.dataset.theme==='dark'||(document.documentElement.dataset.theme!=='light'&&matchMedia('(prefers-color-scheme: dark)').matches);
const col=p=>p[osc()?3:2];
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
const pc=v=>v.toFixed(1).replace('.',',')+' %';
const M=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
function dibuja(){box.innerHTML='';const W=Math.max(320,box.clientWidth||640),H=W<500?320:380,m={l:34,r:W<500?8:70,t:10,b:24};
 const t0=Date.parse(D.serie[0].d),t1=Date.parse(D.serie[D.serie.length-1].d),hi=40;
 const x=t=>m.l+(t-t0)/(t1-t0)*(W-m.l-m.r),y=v=>m.t+(1-v/hi)*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Voto estimado de cada partido en cada encuesta y mediana de las encuestas recientes'},box);
 for(let v=0;v<=hi;v+=10){el('line',{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:'var(--grid)'},svg);el('text',{x:m.l-6,y:y(v)+4,'text-anchor':'end'},svg).textContent=v+'%'}
 const ini=new Date(t0);for(let d=new Date(ini.getFullYear(),ini.getMonth()+1,1);d<=t1;d.setMonth(d.getMonth()+(W<500?3:2))){
  el('text',{x:x(+d),y:H-6,'text-anchor':'middle'},svg).textContent=M[d.getMonth()]+(d.getMonth()===0?' '+d.getFullYear():'')}
 const fin=[];for(const p of D.partidos){const c=col(p);
  for(const e of D.encuestas){const t=Date.parse(e.f);if(t<t0||e.v[p[0]]==null)continue;el('circle',{cx:x(t),cy:y(e.v[p[0]]),r:2.3,fill:c,'fill-opacity':.35},svg)}
  let d='';for(const s of D.serie){if(s[p[0]]==null){d+='';continue}d+=(d&&!d.endsWith(' ')?'L':'M')+x(Date.parse(s.d)).toFixed(1)+','+y(s[p[0]]).toFixed(1)}
  el('path',{d,fill:'none',stroke:c,'stroke-width':2.5,'stroke-linejoin':'round'},svg);
  const u=[...D.serie].reverse().find(s=>s[p[0]]!=null);if(u)fin.push({y:y(u[p[0]])+4,c,t:p[0]==='SUMAR'?'Sumar':p[1]})}
 if(W>=500){fin.sort((a,b)=>a.y-b.y);for(let i=1;i<fin.length;i++)fin[i].y=Math.max(fin[i].y,fin[i-1].y+13);   // etiquetas sin solaparse
  for(const f of fin)el('text',{x:W-m.r+6,y:f.y,style:'fill:'+f.c+';font-weight:600'},svg).textContent=f.t}
 const tip=document.createElement('div');tip.className='tip';tip.hidden=true;box.appendChild(tip);
 const g=el('line',{y1:m.t,y2:H-m.b,stroke:'var(--muted)','stroke-dasharray':'2 3',visibility:'hidden'},svg);
 const mover=ev=>{const r=box.getBoundingClientRect(),pt=ev.touches?ev.touches[0]:ev,px=pt.clientX-r.left;
  const t=t0+(px-m.l)/(W-m.l-m.r)*(t1-t0);let s=D.serie.reduce((a,b)=>Math.abs(Date.parse(b.d)-t)<Math.abs(Date.parse(a.d)-t)?b:a);
  const f=new Date(s.d);g.setAttribute('x1',x(Date.parse(s.d)));g.setAttribute('x2',x(Date.parse(s.d)));g.setAttribute('visibility','visible');
  tip.innerHTML='<b>'+f.getDate()+' '+M[f.getMonth()]+' '+f.getFullYear()+'</b> · mediana<br>'+D.partidos.filter(p=>s[p[0]]!=null).map(p=>'<span style="color:'+col(p)+'">●</span> '+p[1]+' '+pc(s[p[0]])).join('<br>');
  tip.hidden=false;tip.style.left=Math.min(Math.max(px,90),W-90)+'px';tip.style.top=(pt.clientY-r.top)+'px'};
 svg.addEventListener('mousemove',mover);svg.addEventListener('touchstart',mover,{passive:true});svg.addEventListener('mouseleave',()=>{tip.hidden=true;g.setAttribute('visibility','hidden')})}
function hemi(id,H0){const hb=document.getElementById(id);if(!hb||!H0.length)return;hb.innerHTML='';const D={hemi:H0};
 const W=Math.min(640,Math.max(300,hb.clientWidth||600)),R=W/2-4,H=R+30,filas=W<420?9:11,r0=R*.38;
 const total=D.hemi.reduce((a,p)=>a+p[1],0);const radios=[...Array(filas)].map((_,i)=>r0+(R-r0)*(i+.5)/filas);
 const suma=radios.reduce((a,b)=>a+b,0);let n=radios.map(r=>Math.round(total*r/suma));n[filas-1]+=total-n.reduce((a,b)=>a+b,0);
 const pts=[];radios.forEach((r,i)=>{for(let j=0;j<n[i];j++){const a=Math.PI*(1-(n[i]>1?j/(n[i]-1):.5));pts.push({a,x:W/2+r*Math.cos(a),y:R+4-r*Math.sin(a)})}});
 pts.sort((p,q)=>q.a-p.a);const dot=Math.min(R*.5/filas,(R-r0)/filas*.42);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Hemiciclo con el promedio de escaños de las encuestadoras'},hb);svg.style.maxWidth=W+'px';svg.style.margin='0 auto';
 let k=0;for(const p of D.hemi)for(let j=0;j<p[1];j++){const q=pts[k++];el('circle',{cx:q.x,cy:q.y,r:dot,fill:osc()?p[3]:p[2]},svg)}
 el('line',{x1:W/2,x2:W/2,y1:4,y2:R+4-r0+6,stroke:'var(--muted)','stroke-dasharray':'3 3'},svg);
 el('text',{x:W/2,y:R+24,'text-anchor':'middle',style:'font-size:13px'},svg).textContent='176 escaños: mayoría absoluta';
 const lg=document.createElement('div');lg.className='legend';lg.innerHTML=D.hemi.map(p=>'<span><i class="sw" style="background:'+(osc()?p[3]:p[2])+'"></i>'+p[4]+' '+p[1]+'</span>').join('');hb.appendChild(lg)}
const hemis=()=>{hemi('hemi',D.hemi);hemi('hemi-modelo',D.hemi_modelo)};dibuja();hemis();let w=box.clientWidth;addEventListener('resize',()=>{if(box.clientWidth!==w){w=box.clientWidth;dibuja();hemis()}});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',()=>{dibuja();hemis()})})();
</script>
<script>
(()=>{const D=window.__ENC,NS='http://www.w3.org/2000/svg';
const osc=()=>document.documentElement.dataset.theme==='dark'||(document.documentElement.dataset.theme!=='light'&&matchMedia('(prefers-color-scheme: dark)').matches);
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
const pct=v=>(v*100).toFixed(1).replace('.',',')+' %';
function tipDe(box){let t=box.querySelector('.tip');if(!t){t=document.createElement('div');t.className='tip';t.hidden=true;box.appendChild(t)}return t}
function muestra(box,ev,html){const t=tipDe(box),r=box.getBoundingClientRect(),pt=ev.touches?ev.touches[0]:ev;t.innerHTML=html;t.hidden=false;
 t.style.left=Math.min(Math.max(pt.clientX-r.left,90),r.width-90)+'px';t.style.top=(pt.clientY-r.top)+'px'}
// horquillas: una fila por serie; a = [p2,5, p10, p50, p90, p97,5]; der = texto a la derecha
function rangos(id,filas,minX,maxX,linea,der){const box=document.getElementById(id);if(!box||!filas.length)return;box.innerHTML='';
 const W=Math.max(300,box.clientWidth||640),mov=W<500,lab=mov?118:150,mr=der?(mov?44:60):16,fh=30,top=22,H=top+filas.length*fh+6;
 const x=v=>lab+(v-minX)/(maxX-minX)*(W-lab-mr);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Horquillas de escaños'},box);
 const paso=[5,10,25,50].find(v=>v*(W-lab-mr)/(maxX-minX)>=38)||100;   // marcas a 38 px como mínimo
 for(let v=minX;v<=maxX;v+=paso){el('line',{x1:x(v),x2:x(v),y1:top-4,y2:H-4,stroke:'var(--grid)'},svg);if(linea&&Math.abs(x(v)-x(linea))<30)continue;el('text',{x:x(v),y:12,'text-anchor':'middle'},svg).textContent=v}
 if(linea){el('line',{x1:x(linea),x2:x(linea),y1:top-6,y2:H-2,stroke:'var(--fg)','stroke-dasharray':'3 3'},svg);
  el('text',{x:x(linea)+4,y:12,style:'fill:var(--fg);font-weight:600'},svg).textContent=linea}
 filas.forEach((f,i)=>{const y=top+i*fh+fh/2,c=osc()?f.o:f.c,a=f.a;
  el('text',{x:lab-8,y:y+4,'text-anchor':'end',style:'fill:var(--fg)'},svg).textContent=f.n;
  if(a.length>3)el('line',{x1:x(a[0]),x2:x(a[4]),y1:y,y2:y,stroke:c,'stroke-width':2,'stroke-opacity':.55},svg);
  const lo=a.length>3?a[1]:a[0],hi=a.length>3?a[3]:a[a.length-1];
  el('rect',{x:x(lo),y:y-6,width:Math.max(8,x(hi)-x(lo)),transform:x(hi)-x(lo)<8?`translate(-4,0)`:'',height:12,rx:4,fill:c},svg);
  if(a.length>3){el('circle',{cx:x(a[2]),cy:y,r:5,fill:'var(--bg)',stroke:c,'stroke-width':2.5},svg)}
  if(der)el('text',{x:W-4,y:y+4,'text-anchor':'end',style:'fill:var(--fg);font-weight:600'},svg).textContent=der(f);
  const hit=el('rect',{x:0,y:y-fh/2,width:W,height:fh,fill:'transparent'},svg);
  const txt=f.tip||('<b>'+f.n+'</b><br>Mediana '+a[2]+' escaños<br>80 %: '+a[1]+'-'+a[3]+' · 95 %: '+a[0]+'-'+a[4]);
  hit.addEventListener('mousemove',ev=>muestra(box,ev,txt));hit.addEventListener('touchstart',ev=>muestra(box,ev,txt),{passive:true});
  hit.addEventListener('mouseleave',()=>{tipDe(box).hidden=true})})}
// columnas: distribución de escaños de cada partido en las simulaciones, en paneles
function columnas(id,series,linea){const box=document.getElementById(id);if(!box||!series.length)return;box.innerHTML='';
 const W=Math.max(300,box.clientWidth||640),por=W<500?1:2,pw=(W-(por-1)*20)/por,ph=130,filasP=Math.ceil(series.length/por),H=filasP*(ph+44);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Distribución de escaños de cada partido en las simulaciones'},box);
 series.forEach((s,i)=>{let [n,c0,o0,desde,p0,a]=s;const k=p0.length>60?3:1,p=[];desde=desde-desde%k;   // de 3 en 3 escaños si hay muchos
  p0.forEach((v,j)=>{const b=Math.floor((s[3]+j-desde)/k);p[b]=(p[b]||0)+v});for(let j=0;j<p.length;j++)p[j]=p[j]||0;const c=osc()?o0:c0,ox=(i%por)*(pw+20),oy=Math.floor(i/por)*(ph+44)+18;
  const mx=Math.max(...p),bw=pw/p.length,y=v=>oy+ph-v/mx*ph;
  el('text',{x:ox,y:oy-4,style:'fill:var(--fg);font-weight:600'},svg).textContent=n+' · mediana '+a[2];
  el('line',{x1:ox,x2:ox+pw,y1:oy+ph,y2:oy+ph,stroke:'var(--rule)'},svg);
  p.forEach((v,j)=>{const e=desde+j*k,e2=e+k-1;if(!v)return;const dentro=e2>=a[1]&&e<=a[3];
   const r=el('rect',{x:ox+j*bw+.5,y:y(v),width:Math.max(1,bw-1),height:oy+ph-y(v),fill:c,'fill-opacity':dentro?1:.3},svg);
   const txt='<b>'+n+': '+(k>1?e+'-'+e2:e)+' escaños</b><br>'+pct(v)+' de las simulaciones';
   const hit=el('rect',{x:ox+j*bw,y:oy,width:bw,height:ph,fill:'transparent'},svg);
   hit.addEventListener('mousemove',ev=>muestra(box,ev,txt));hit.addEventListener('touchstart',ev=>muestra(box,ev,txt),{passive:true});
   hit.addEventListener('mouseleave',()=>{tipDe(box).hidden=true})});
  if(linea&&linea>=desde&&linea<desde+p.length*k){const lx=ox+(linea-desde)/k*bw;el('line',{x1:lx,x2:lx,y1:oy-2,y2:oy+ph+2,stroke:'var(--fg)','stroke-dasharray':'3 3'},svg);
   el('text',{x:lx+4,y:oy+10,style:'fill:var(--fg);font-weight:600'},svg).textContent=linea}
  const paso=p.length*k>80?20:p.length*k>30?10:5;
  for(let e=Math.ceil(desde/paso)*paso;e<desde+p.length*k-paso/2;e+=paso)el('text',{x:ox+((e-desde)/k+.5)*bw,y:oy+ph+15,'text-anchor':'middle'},svg).textContent=e})}
function todo(){const M=D.modelo||{};
 if(M.bloques)rangos('horq-bloques',M.bloques.map(b=>({n:b[0],c:b[1],o:b[2],a:b[3],p:b[4]})),100,250,176,f=>f.p+' %');
 if(M.partidos)rangos('horq-partidos',M.partidos.map(b=>({n:b[0],c:b[1],o:b[2],a:b[3]})),0,Math.ceil(Math.max(...M.partidos.map(b=>b[3][4]))/25)*25,0,null);
 if(M.dist)columnas('dist-modelo',M.dist);if(M.dist_bloques)columnas('dist-bloques',M.dist_bloques,176);
 if(D.pv&&D.pv.length)rangos('horq-encuestas',D.pv.map(e=>({n:e[0],c:'#1d84ce',o:'#4fa8ea',a:[e[1],e[2]],
  tip:'<b>'+e[0]+'</b><br>PP + Vox: '+(e[1]===e[2]?e[1]:e[1]+'-'+e[2])+' escaños'})),170,230,176,null)}
todo();let w=document.body.clientWidth;addEventListener('resize',()=>{if(document.body.clientWidth!==w){w=document.body.clientWidth;todo()}});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',todo)})();
</script>"""


def franja_portada(titular, med, actual, pre):
    """Franja «Encuestas» de la portada, entre <!--encuestas:portada-->, justo debajo del mapa: titular y mediana de cada partido."""
    cifras = ''.join(f'<li><i style="background:{c}"></i>{"Sumar" if k == "SUMAR" else n} <b>{pc(med[k])}</b></li>'
                     for k, n, c, _ in PRINCIPALES if k in med)
    return (f'<section class="wide del-atlas del-encuestas" aria-labelledby="h-del-encuestas"><div class="da-cab"><h2 id="h-del-encuestas">'
            f'<a href="{pre}encuestas/">Encuestas de las elecciones generales</a></h2><span class="de-act">Actualizado el {actual}</span></div>'
            f'<a class="de-tit" href="{pre}encuestas/">{html.escape(titular)}</a><ul class="de-med">{cifras}</ul>'
            f'<p class="de-pie">Mediana de la última encuesta de cada encuestadora en las tres últimas semanas. '
            f'<a href="{pre}encuestas/">Todas las encuestas, los escaños y nuestra estimación →</a></p>'
            '<style>.del-encuestas .de-act{font:13px var(--sans);color:var(--muted)}.del-encuestas .de-tit{display:block;font:700 clamp(19px,2.4vw,24px)/1.25 var(--serif);color:var(--ink);text-decoration:none;margin:2px 0 8px}'
            '.del-encuestas .de-tit:hover{text-decoration:underline}.del-encuestas .de-med{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:4px 16px;font:14px var(--sans)}'
            '.del-encuestas .de-med i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px}.del-encuestas .de-pie{font:13px/1.4 var(--sans);color:var(--muted);margin:8px 0 0}</style></section>')


def post_x(titular, med, hoy):
    """Texto del post para X/Bluesky con la cifra del día; el enlace saca la tarjeta (og:image) como imagen.
    X cuenta cualquier enlace como 23 caracteres: el texto queda por debajo de 280."""
    d = date.fromisoformat(hoy)
    cifras = ' · '.join(f'{"Sumar" if k == "SUMAR" else n} {pc(med[k]).replace(chr(160), " ")}' for k, n, *_ in PRINCIPALES[:3] if k in med)
    texto = (f'Encuestas del 29N ({d.day} {MESES[d.month - 1]}): {titular[0].lower() + titular[1:] if titular.startswith("El ") else titular}.\n\n'
             f'Mediana: {cifras}.\n\n'
             'Todas las encuestas y nuestro modelo:')
    etiquetas = '#29N #EleccionesGenerales #Encuestas'
    while len(texto) + 23 + len(etiquetas) + 4 > 280 and '\n\nMediana' in texto:   # si no cabe, fuera la línea de cifras
        texto = texto.split('\n\nMediana')[0] + '\n\nTodas las encuestas, con su fuente, y nuestro modelo:'
    return texto, URL, etiquetas


def portada(titular, med, actual):
    for f, pre in ((RAIZ / 'index.html', ''), (RAIZ / 'generales-2026/src/plantilla.html', '../')):
        if not f.exists():
            continue
        t = f.read_text(encoding='utf-8')
        if '<!--encuestas:portada-->' not in t:   # la franja va justo encima de la de Actualidad
            t = t.replace('<!--actualidad:ultimas-->', '<!--encuestas:portada--><!--/encuestas:portada-->\n<!--actualidad:ultimas-->', 1)
        t = re.sub(r'<!--encuestas:portada-->.*?<!--/encuestas:portada-->',
                   lambda m: '<!--encuestas:portada-->' + franja_portada(titular, med, actual, pre) + '<!--/encuestas:portada-->', t, flags=re.S)
        f.write_text(t, encoding='utf-8')


def svg_hemiciclo(hemi):
    """Hemiciclo del promedio de escaños en SVG estático (el de insertar.html, que no lleva JavaScript)."""
    asientos = [(k, hemi[k], next(c for kk, _, c, _ in TODOS if kk == k)) for k in ORDEN_HEMI if k in hemi]
    W, R, filas = 600, 296, 11
    r0 = R * .38
    radios = [r0 + (R - r0) * (i + .5) / filas for i in range(filas)]
    total = sum(n for _, n, _ in asientos)
    n = [round(total * r / sum(radios)) for r in radios]
    n[-1] += total - sum(n)
    pts = sorted(((math.pi * (1 - (j / (k - 1) if k > 1 else .5)), r) for r, k in zip(radios, n) for j in range(k)), key=lambda p: -p[0])
    dot = min(R * .5 / filas, (R - r0) / filas * .42)
    puntos, i = '', 0
    for _, k, c in asientos:
        for _ in range(k):
            a, r = pts[i]; i += 1
            puntos += f'<circle cx="{W / 2 + r * math.cos(a):.1f}" cy="{R + 4 - r * math.sin(a):.1f}" r="{dot:.1f}" fill="{c}"/>'
    return (f'<svg viewBox="0 0 {W} {R + 30}" role="img" aria-label="Hemiciclo con el promedio de escaños de las encuestadoras">{puntos}'
            f'<line x1="{W / 2}" x2="{W / 2}" y1="4" y2="{R + 10 - r0:.0f}" stroke="currentColor" stroke-dasharray="3 3" opacity=".6"/>'
            f'<text x="{W / 2}" y="{R + 26}" text-anchor="middle" style="font-size:20px">176 escaños: mayoría absoluta</text></svg>')


def insertable(h1, med, hemi, n_hemi, actual, hoy):
    """encuestas/insertar.html: resumen para poner en otra web con un iframe. noindex, con canonical a /encuestas/."""
    maxv = max(med[k] for k, *_ in PRINCIPALES if k in med)
    barras = ''.join(f'<li><span class="n">{"Sumar" if k == "SUMAR" else n}</span><span class="b"><i style="width:{med[k] / maxv * 100:.1f}%;background:{c}"></i></span>'
                     f'<b>{pc(med[k])}</b></li>' for k, n, c, _ in PRINCIPALES if k in med)
    bloque = ''
    if hemi:
        ley = ' · '.join(f'<span><i style="background:{next(c for kk, _, c, _ in TODOS if kk == k)}"></i>{NOMBRE[k]} {hemi[k]}</span>'
                         for k in sorted(hemi, key=hemi.get, reverse=True))
        bloque = (f'<h2>Promedio de escaños de {n_hemi} encuestadoras</h2>{svg_hemiciclo(hemi)}<p class="ley">{ley}</p>')
    pagina = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Encuestas de las elecciones generales · Mapa Electoral</title>
<meta name="robots" content="noindex, follow"><link rel="canonical" href="{URL}">
<style>
:root{{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf}}
@media (prefers-color-scheme: dark){{:root{{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;color-scheme:dark}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 "IBM Plex Sans",system-ui,sans-serif}}
main{{padding:14px 16px}} a{{color:inherit}}
.k{{font-size:12px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:#1d84ce;margin:0}}
h1{{font-size:19px;line-height:1.25;margin:4px 0 2px}} h2{{font-size:14px;color:var(--muted);margin:16px 0 6px}}
.f{{font-size:12px;color:var(--muted);margin:0 0 10px}}
ul{{list-style:none;margin:0;padding:0}} li{{display:grid;grid-template-columns:5.5em 1fr 4em;align-items:center;gap:8px;margin:3px 0}}
.b{{height:12px}} .b i{{display:block;height:100%;border-radius:2px}} li b{{text-align:right;font-variant-numeric:tabular-nums}}
svg{{display:block;width:100%;max-width:440px;height:auto;margin:0 auto;color:var(--muted)}} svg text{{fill:var(--muted);font-size:13px}}
.ley{{font-size:12px;margin:6px 0 0}} .ley i{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:3px}}
footer{{border-top:1px solid var(--rule);margin-top:12px;padding-top:8px;font-size:12px;color:var(--muted)}}
</style></head><body><main>
<p class="k">Encuestas · Elecciones generales del 29N</p>
<h1><a href="{URL}" target="_blank" rel="noopener">{html.escape(h1)}</a></h1>
<p class="f">Actualizado el {actual}</p>
<h2>Mediana de las encuestas (última de cada encuestadora, tres semanas)</h2>
<ul>{barras}</ul>
{bloque}
<footer>Fuente: <a href="{URL}" target="_blank" rel="noopener">Mapa Electoral · todas las encuestas, con su fuente</a>. Cifras publicadas por las encuestadoras; no es una previsión. CC BY-SA 4.0.</footer>
</main></body></html>
"""
    (SALIDA / 'insertar.html').write_text(pagina, encoding='utf-8')


TIP_MAPA = """<script>
(()=>{const box=document.getElementById('mapa-prov');if(!box)return;const t=document.createElement('div');t.className='tip';t.hidden=true;box.appendChild(t);
const ver=ev=>{const p=ev.target.closest('path');if(!p){t.hidden=true;return}const r=box.getBoundingClientRect(),pt=ev.touches?ev.touches[0]:ev;
 t.textContent=p.dataset.t;t.hidden=false;t.style.left=Math.min(Math.max(pt.clientX-r.left,120),r.width-120)+'px';t.style.top=(pt.clientY-r.top)+'px'};
box.addEventListener('mousemove',ver);box.addEventListener('touchstart',ver,{passive:true});box.addEventListener('mouseleave',()=>{t.hidden=true})})();
</script>"""
COLOR_EXTRA = {'PACMA': '#8a8486'}   # listas del modelo sin color en TODOS


def color_lista(l):
    return next(c for k, _, c, _ in TODOS if k == DEL_MODELO[l]) if l in DEL_MODELO else COLOR_EXTRA.get(l, '#8a8486')


def nombre_lista(l):
    return NOMBRE[DEL_MODELO[l]] if l in DEL_MODELO else l


def nivel(p):
    """Intensidad del color según la probabilidad de quedar primero (tres escalones, los de la leyenda del mapa)."""
    return 1 if p >= .8 else .62 if p >= .6 else .3


def svg_mapa_provincias(primero, nombres):
    """Mapa de provincias coloreado por el partido con más probabilidades de quedar primero; geometría de la portada
    (generales-2026/data/provincias.json, anillos en deltas enteros, Canarias ya desplazada al suroeste)."""
    g = json.load(open(RAIZ / 'generales-2026/data/provincias.json'))
    S, kx = g['S'], math.cos(math.radians(39.5))
    anillos = []
    for c, partes in zip(g['cod'], g['poly']):
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            anillos.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    xs = [x for _, r in anillos for x, _ in r]; ys = [y for _, r in anillos for _, y in r]
    W = 640; esc = W / (max(xs) - min(xs)); H = round((max(ys) - min(ys)) * esc)
    caminos = {}
    for c, r in anillos:
        d, ult = '', None
        for x, y in r:
            q = (round((x - min(xs)) * esc, 1), round((y - min(ys)) * esc, 1))
            if ult and abs(q[0] - ult[0]) + abs(q[1] - ult[1]) < .8:   # puntos a menos de un píxel: fuera
                continue
            d += ('L' if d else 'M') + f'{q[0]:g},{q[1]:g}'; ult = q
        caminos[c] = caminos.get(c, '') + d + 'Z'
    out = ''
    for c, d in caminos.items():
        pr = primero.get(c)
        if not pr:
            continue
        t = f'{nombres[c]}: {nombre_lista(pr["lista"])} primero en el {round(pr["p_primera"] * 100)} % de las simulaciones'
        out += (f'<path d="{d}" fill="{color_lista(pr["lista"])}" fill-opacity="{nivel(pr["p_primera"])}" data-t="{html.escape(t)}">'
                f'<title>{html.escape(t)}</title></path>')
    # recuadro de Canarias, que no está en su sitio
    cx = [(x - min(xs)) * esc for c, r in anillos if c in ('35', '38') for x, _ in r]
    cy = [(y - min(ys)) * esc for c, r in anillos if c in ('35', '38') for _, y in r]
    marco = f'<rect x="{min(cx) - 8:.0f}" y="{min(cy) - 8:.0f}" width="{max(cx) - min(cx) + 16:.0f}" height="{max(cy) - min(cy) + 16:.0f}" fill="none" stroke="var(--rule)"/>'
    return (f'<svg class="mapa-prov" viewBox="-2 -2 {W + 4} {H + 4}" role="img" aria-label="Mapa de provincias según el partido con más probabilidades de quedar primero">'
            f'{marco}<g stroke="var(--bg)" stroke-width=".8" stroke-linejoin="round">{out}</g></svg>')


PROV_PAGINAS = []   # [(ruta, nombre)] de las páginas /encuestas/<provincia>/ que escribe provincias()


def provincias():
    """encuestas/provincias.html: escaños de cada provincia según el modelo (mediana y horquilla del 80 %) y las más
    disputadas. Solo si hay salida publicable del modelo, como el bloque de la estimación. Devuelve True si la escribe."""
    if not (ESTIMACION / 'escenario-base.json').exists():
        return False
    d = json.load(open(ESTIMACION / 'escenario-base.json'))
    meta = json.load(open(ESTIMACION / 'meta.json'))
    if meta.get('interno', True) or meta.get('ficticio'):
        return False
    sys.path.insert(0, str(RAIZ / 'src'))
    from territorios_rutas import ruta_provincia, PROV_SLUG
    import provincias_paginas
    PROV_PAGINAS[:] = provincias_paginas.genera(d, meta, sys.modules[__name__], ruta_provincia, PROV_SLUG.get)
    nombres, prov = meta['provincias'], d['provincias']
    primero = {c: max(v['listas'], key=lambda l: l['p_primera']) for c, v in prov.items()}
    from collections import Counter
    cuenta = Counter(l['lista'] for l in primero.values())
    lider, n_lider = cuenta.most_common(1)[0]
    art = 'el ' if lider in ('PP', 'PSOE', 'PNV', 'BNG') else ''
    titular = f'Encuesta por provincias: {art}{nombre_lista(lider)} saldría primero en {n_lider} de {len(prov)}, según nuestro modelo'
    partes = [f'{"el " if l in ("PP", "PSOE", "PNV", "BNG") else ""}{nombre_lista(l)} en {n}' for l, n in cuenta.most_common()]
    partes[0] += ' provincias'
    reparto = ', '.join(partes[:-1]) + ' y ' + partes[-1] if len(partes) > 1 else partes[0]
    p1 = (f'Con la media de las encuestas del {fecha_larga(meta["generado"])} repartida por provincia, el partido con más probabilidades de quedar primero '
          f'es {reparto}. «Primero» es el que queda delante en más simulaciones.')
    reñidas = sorted(prov, key=lambda c: primero[c]['p_primera'])[:6]

    def segundo(c):
        return sorted(prov[c]['listas'], key=lambda l: -l['p_primera'])[1]
    p2 = ('Las provincias donde el primer puesto está menos claro: '
          + '; '.join(f'{nombres[c]} ({nombre_lista(primero[c]["lista"])} {round(primero[c]["p_primera"] * 100)} %, '
                      f'{nombre_lista(segundo(c)["lista"])} {round(segundo(c)["p_primera"] * 100)} %)' for c in reñidas) + '.')
    # duelos: probabilidad de quedar primero de los dos primeros en las provincias más reñidas
    duelos = ''
    for c in sorted(prov, key=lambda c: primero[c]['p_primera'])[:8]:
        a, b = primero[c], segundo(c)
        pa, pb = round(a['p_primera'] * 100), round(b['p_primera'] * 100)
        duelos += (f'<div class="duelo"><span class="dn">{html.escape(nombres[c])}</span><span class="db">'
                   f'<i style="width:{pa}%;background:{color_lista(a["lista"])}" title="{html.escape(nombre_lista(a["lista"]))} {pa} %"></i>'
                   f'<i style="width:{pb}%;background:{color_lista(b["lista"])}" title="{html.escape(nombre_lista(b["lista"]))} {pb} %"></i></span>'
                   f'<span class="dl">{html.escape(nombre_lista(a["lista"]))} <b>{pa} %</b> · {html.escape(nombre_lista(b["lista"]))} <b>{pb} %</b></span></div>')
    presentes = sorted({l['lista'] for l in primero.values()}, key=lambda l: -cuenta[l])
    leyenda = (''.join(f'<span><i class="sw" style="background:{color_lista(l)}"></i>{html.escape(nombre_lista(l))} ({cuenta[l]})</span>' for l in presentes)
               + '<span class="int">Probabilidad: <i style="opacity:.3"></i>menos del 60 % <i style="opacity:.62"></i>60-80 % <i></i>más del 80 %</span>')
    filas = ''
    for ca, cods in meta['ccaa'].items():
        for c in cods:
            v = prov[c]
            con = [l for l in sorted(v['listas'], key=lambda l: (-l['escanos'][1], -l['voto'][1])) if l['escanos'][2] > 0]
            chips = ''.join(f'<span class="chip"><i style="background:{color_lista(l["lista"])}"></i>{html.escape(nombre_lista(l["lista"]).replace(" / Frente Amplio", ""))} <b>{l["escanos"][1]}</b>'
                            + (f'<small>{l["escanos"][0]}-{l["escanos"][2]}</small>' if l['escanos'][0] != l['escanos'][2] else '') + '</span>' for l in con)
            # un cuadrado por escaño con la mediana de cada partido; los que no reparten las medianas, en gris
            cuad, n = '', 0
            for l in con:
                k = min(l['escanos'][1], v['escanos_total'] - n); n += k
                cuad += f'<i style="background:{color_lista(l["lista"])}"></i>' * k
            cuad += '<i class="aire"></i>' * (v['escanos_total'] - n)
            chips = f'<span class="esc" aria-hidden="true">{cuad}</span>' + chips
            pr = primero[c]
            # «Primero» antes del reparto para que se vea en el móvil sin desplazar la tabla
            filas += (f'<tr><td><a href="{PROV_SLUG[c]}/">{html.escape(nombres[c])}</a><span class="medio">{html.escape(ca)} · {v["escanos_total"]} escaños · <a href="../{ruta_provincia(c)}">2023</a></span></td>'
                      f'<td class="n"><i class="pt" style="background:{color_lista(pr["lista"])}"></i>{html.escape(nombre_lista(pr["lista"]))}<small>{round(pr["p_primera"] * 100)} %</small></td>'
                      f'<td>{chips}</td></tr>')
    faq = [('¿Es esto una encuesta por provincias?',
            'No. Las encuestadoras casi nunca publican sus datos por provincia. Esto es un cálculo de Mapa Electoral: toma la media de las encuestas nacionales, '
            'la reparte por provincia a partir de los resultados de 2023 y las europeas de 2024, y simula el resultado '
            f'{meta["simulaciones"]:,} veces con el error histórico de las encuestas.'.replace(',', '.')),
           ('¿Qué provincias están más disputadas?', p2),
           ('¿Qué significa la horquilla de escaños?',
            'En el 80 % de las simulaciones, el partido saca un número de escaños dentro de ese intervalo. La cifra grande es la mediana. '
            'Por eso la suma de las medianas de una provincia puede no coincidir exactamente con sus escaños.'),
           ('¿Cada cuánto se actualiza?', 'Cada vez que entra una encuesta nueva en la página de encuestas, el modelo se vuelve a calcular y esta tabla cambia con él. '
            'Del 24 al 28 de noviembre no se actualiza: la ley electoral prohíbe publicar sondeos esos días.')]
    actual = fecha_larga(meta['generado'])
    url = URL + 'provincias.html'
    desc = f'Escaños de cada una de las 52 circunscripciones según la media de encuestas de las generales del 29N, con su horquilla y las provincias más disputadas. Modelo propio, actualizado el {actual}.'
    jsonld = [{'@context': 'https://schema.org', '@type': 'AnalysisNewsArticle', '@id': url + '#articulo', 'headline': titular, 'description': desc,
               'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': '2026-10-23', 'dateModified': meta['generado'],
               'image': [f'{BASE}/img/compartir/encuestas.jpg?v={meta["generado"]}'], 'about': {'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'},
               'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'}, 'publisher': MEDIO, 'isAccessibleForFree': True},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    cuerpo = f"""<main>
<p class="kicker">Modelo propio · Elecciones generales del 29N</p>
<h1 data-miga="Por provincias">{html.escape(titular)}</h1>
<p class="dek">Los escaños de cada circunscripción con la media de las encuestas, su horquilla y quién tiene más opciones de quedar primero.</p>
<p class="firma">Por <a href="../sobre-mi.html">{AUTOR}</a> · Actualizado el <time datetime="{meta['generado']}">{actual}</time></p>
<p class="propio"><b>Modelo propio, no es una encuesta.</b> Las encuestadoras no publican sus datos por provincia. Estas cifras salen del modelo de Mapa Electoral, que reparte por provincia la media de las <a href="./">encuestas publicadas</a>. <a href="metodo-modelo.html">Cómo se calcula</a>.</p>
<p data-tipo="dato">{html.escape(p1)}</p>
<figure><figcaption><span class="t">Quién saldría primero en cada provincia</span><span class="s">Partido que queda delante en más simulaciones; cuanto más intenso el color, más claro lo tiene. Entre paréntesis, en cuántas provincias.</span></figcaption>
<div class="chart" id="mapa-prov">{svg_mapa_provincias(primero, nombres)}</div>
<div class="legend">{leyenda}</div></figure>
<p data-tipo="dato">{html.escape(p2)}</p>
<figure><figcaption><span class="t">Las provincias más disputadas</span><span class="s">Porcentaje de simulaciones en que queda primero cada uno de los dos partidos con más opciones.</span></figcaption>
<div class="duelos">{duelos}</div></figure>
<h2>Escaños por provincia según la media de encuestas</h2>
<p>Cada cuadrado es un escaño, con el color del partido que lo saca en la mediana; en gris, los que quedan en el aire. La cifra grande es la mediana de escaños de cada partido en {meta['simulaciones']:,} simulaciones y, debajo, la horquilla del 80 %. «Primero» es el partido con más probabilidades de quedar delante, con esa probabilidad. Cada provincia enlaza a su página con el detalle y, al lado, a sus resultados de 2023, sección a sección.</p>
<div class="tbl"><table class="prov"><thead><tr><th>Provincia</th><th class="n">Primero</th><th>Escaños: mediana y horquilla</th></tr></thead><tbody>{filas}</tbody></table></div>
<p class="src">{html.escape(meta.get('aviso', ''))} Modelo v{html.escape(meta['version'].split('-')[0].lstrip('v'))}; <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/previsiones">código</a>.</p>
<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="./"><span class="kicker">Encuestas</span><b>Todas las encuestas de las generales y su promedio</b></a></li><li><a href="calculadora-escanos/"><span class="kicker">Calculadora</span><b>Reparte tú los 350 escaños</b></a></li><li><a href="../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li><li><a href="../elecciones/elecciones-29n-2026/"><span class="kicker">29N</span><b>Escaños por provincia: cómo se reparten</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../atlas/politica-editorial/">Política editorial</a></footer>
</main>""".replace(f"{meta['simulaciones']:,}", f"{meta['simulaciones']:,}".replace(',', '.'))
    estilos = ESTILOS.replace('</style>', '.prov td{vertical-align:middle}.chip{display:inline-block;margin:1px 8px 1px 0;white-space:nowrap}.chip i{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:3px}'
                              '.chip small{display:inline;margin-left:3px;color:var(--muted);font-size:.72rem}'
                              '.esc{display:flex;flex-wrap:wrap;gap:2px;margin:2px 0 4px;max-width:330px}.esc i{width:9px;height:9px;border-radius:2px;display:block}.esc i.aire{background:var(--grid);outline:1px solid var(--rule);outline-offset:-1px}'
                              '.mapa-prov{max-width:640px;margin:0 auto}.mapa-prov path:hover{stroke:var(--fg);stroke-width:1.5}'
                              '.legend .int{color:var(--muted)}.legend .int i{display:inline-block;width:12px;height:12px;border-radius:2px;background:var(--fg);margin:0 3px 0 8px;vertical-align:-1px}'
                              '.duelo{display:grid;grid-template-columns:8.5em 1fr;gap:2px 10px;align-items:center;font-family:var(--ui);font-size:.9rem;margin:6px 0}'
                              '.duelo .db{display:flex;height:14px;background:var(--grid);border-radius:3px;overflow:hidden;gap:2px}.duelo .db i{display:block;height:100%}'
                              '.duelo .dl{grid-column:2;color:var(--muted);font-size:.8rem}'
                              '@media (max-width:520px){.duelo{grid-template-columns:6.5em 1fr}}</style>')
    pagina = (cabecera('Encuestas por provincias: escaños en cada provincia (29N)', desc, url, f'{BASE}/img/compartir/encuestas.jpg?v={meta["generado"]}', jsonld)
              .replace('<meta property="og:title" content="Encuestas por provincias: escaños en cada provincia (29N)">', f'<meta property="og:title" content="{html.escape(titular)}">')
              + estilos + CSS_SITIO + '\n</head>\n<body>\n' + nav('../', 'Encuestas') + '\n' + cuerpo + '\n' + TIP_MAPA + '\n</body>\n</html>\n')
    (SALIDA / 'provincias.html').write_text(pagina, encoding='utf-8')
    return True


def main():
    encs = carga()
    resumen = json.load(open(DATOS / 'resumen.json'))
    hoy = date.fromisoformat(resumen['descargado'][:10])
    ultima = date.fromisoformat(encs[0]['fin'])
    serie = medianas(encs, max(ultima, hoy))
    titular, entradilla, p1, p2, ultimas, con_esc, mayoria = textos(encs, hoy)
    desde_g = (hoy - timedelta(days=DESDE_GRAFICO)).isoformat()
    hemi, n_hemi = promedio_escanos(con_esc)
    bloque_modelo, hemi_m = estimacion()
    hay_provincias = provincias()
    hay_calculadora = calculadora.genera(sys.modules[__name__])
    casas = encuestadoras.genera(encs, SALIDA, sys.modules[__name__])
    asientos = lambda h: [[k, h[k], *next((c, o, n) for kk, n, c, o in TODOS if kk == k)] for k in ORDEN_HEMI if k in (h or {})]
    pv_casas = [[e['casa'], *suma_pv(e)] for e in sorted(con_esc, key=lambda e: -sum(suma_pv(e)))]
    datos = {'modelo': MODELO_JS, 'pv': pv_casas, 'partidos': PRINCIPALES, 'serie': serie, 'hemi': asientos(hemi), 'hemi_modelo': asientos(hemi_m),
             'encuestas': [{'f': e['fin'], 'v': e['voto']} for e in encs if e['fin'] >= desde_g and not e['reest']]}
    desde23 = sorted((e for e in encs if e['fin'] >= '2023-07-24'), key=lambda e: e.get('publicado') or e['fin'], reverse=True)
    recientes, anteriores = desde23[:VISIBLES], desde23[VISIBLES:]   # las últimas a la vista; el resto, plegado
    cab_partidos = ''.join(f'<th class="n"><i class="pt" style="background:{c}"></i>{"Sumar" if k == "SUMAR" else n}</th>' for k, n, c, _ in PRINCIPALES)
    tabla = (f'<div class="tbl"><table><thead><tr><th>Encuestadora y medio</th><th class="n">Publicada</th><th class="n">Muestra</th>{cab_partidos}</tr></thead>'
             f'<tbody>{"".join(fila_tabla(e) for e in recientes)}</tbody></table></div>')
    tabla_ant = (f'<details><summary>Ver las {len(anteriores)} encuestas anteriores, desde las generales de 2023</summary><div class="tbl"><table><thead><tr>'
                 f'<th>Encuestadora y medio</th><th class="n">Publicada</th><th class="n">Muestra</th>{cab_partidos}</tr></thead>'
                 f'<tbody>{"".join(fila_tabla(e) for e in anteriores)}</tbody></table></div></details>')
    filas_esc = ''
    for e in sorted(con_esc, key=lambda e: -rango_esc(e['esc']['PP'])[0]):
        lo, hi = suma_pv(e)
        suma = str(lo) if lo == hi else f'{lo}-{hi}'
        nombre = (html.escape(e['casa']) + (f'<span class="medio">{html.escape(e["medio"])}</span>' if e['medio'] else '')
                  + f'<span class="medio">Publicada el {fechas_celda(e)}</span>')
        # PP + Vox justo después del nombre, para que se vea en el móvil sin desplazar la tabla
        filas_esc += (f'<tr{" class=mayoria" if lo >= 176 else ""}><td>{nombre}</td><td class="n suma">{suma}</td>'
                      + ''.join(f'<td class="n">{e["esc"].get(k, "–")}</td>' for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS')) + '</tr>')
    if hemi:
        pv = hemi.get('PP', 0) + hemi.get('VOX', 0)
        lista = ', '.join(f'{NOMBRE[k]} {hemi[k]}' for k in sorted(hemi, key=hemi.get, reverse=True))
        bloque_hemi = (f'<figure><figcaption><span class="t">Promedio de escaños de las {n_hemi} encuestadoras</span>'
                       f'<span class="s">Media de los escaños que publica cada encuestadora en su última encuesta del último mes (el centro, si da un intervalo). '
                       f'Solo las que publican el reparto completo de los 350.</span></figcaption><div class="chart" id="hemi"></div>'
                       f'<p class="src">{lista}. PP y Vox suman {pv}; la mayoría absoluta está en 176. Es el promedio de lo que publican las encuestadoras, no una previsión de Mapa Electoral.</p></figure>')
    else:
        bloque_hemi = ''
    tabla_esc = ('<div class="tbl"><table><thead><tr><th>Encuestadora</th><th class="n">PP + Vox</th>'
                 + ''.join(f'<th class="n"><i class="pt" style="background:{c}"></i>{"Sumar" if k == "SUMAR" else n}</th>' for k, n, c, _ in PRINCIPALES[:5])
                 + f'</tr></thead><tbody>{filas_esc}</tbody></table></div>') if con_esc else ''
    ult = next(e for e in desde23 if not e['reest'])
    cis = next((e for e in encs if e['casa'] == 'CIS' and not e['reest']), None)
    med = serie[-1]
    n_desde23 = sum(1 for e in desde23 if not e['reest'])
    faq = [('¿Quién gana las elecciones generales según las encuestas?', p1.strip()),
           ('¿Cuál es la última encuesta de las generales?',
            f'La última publicada es la de {ult["casa"]}{" para " + ult["medio"] if ult["medio"] else ""}'
            + (f', del {fecha_larga(ult["publicado"])}' if ult.get('publicado') else '') + f': PP {pc(ult["voto"]["PP"])}, PSOE {pc(ult["voto"]["PSOE"])}'
            + (f', Vox {pc(ult["voto"]["VOX"])}' if 'VOX' in ult['voto'] else '') + '.'),
           ('¿Suman mayoría absoluta PP y Vox en las encuestas?', p2 or 'Las encuestas recientes no publican escaños.'),
           ('¿Qué encuestas dan mayoría absoluta a PP y Vox?',
            (f'Con la última encuesta de cada encuestadora en los últimos 30 días, dan a PP y Vox juntos 176 escaños o más: '
             + ', '.join(f'{e["casa"]}{" (" + e["medio"] + ")" if e["medio"] else ""}' for e in con_esc if suma_pv(e)[0] >= 176) + '. '
             + (('No llegan: ' + ', '.join(e['casa'] for e in con_esc if suma_pv(e)[0] < 176) + '. ') if mayoria < len(con_esc) else '')
             + 'Si la encuestadora da un intervalo, se cuenta su extremo bajo.') if mayoria else None),
           ('¿Cómo se calcula el promedio de escaños?',
            f'Se toma la última encuesta del último mes de cada encuestadora que publica el reparto completo de los 350 diputados ({n_hemi} ahora), '
            'se usa el centro del intervalo cuando da una horquilla y se hace la media de cada partido. Los decimales se reparten por restos mayores '
            'para que el total sume lo mismo que la media. Es un resumen de lo que publican las encuestadoras, no una previsión.') if hemi else None,
           ('¿Cuánto saca cada partido de media?',
            'La mediana de la última encuesta de cada encuestadora en las tres últimas semanas da: '
            + ', '.join(f'{n} {pc(med[k])}' for k, n, *_ in PRINCIPALES if k in med) + '. Es un resumen de las encuestas, no una previsión.'),
           ('¿Qué dice la última encuesta del CIS?',
            f'El CIS publicó su última estimación el {fecha_larga(cis["publicado"] or cis["fin"])}: '
            + ', '.join(f'{n} {pc(cis["voto"][k])}' for k, n, *_ in PRINCIPALES[:4] if k in cis['voto'])
            + '. Su estimación suele apartarse del resto de encuestadoras, sobre todo en el PSOE.') if cis else None,
           ('¿Qué estima el modelo de Mapa Electoral?',
            f'Nuestro modelo propio, que junta las encuestas y simula el reparto por provincia, da en su escenario central '
            + ', '.join(f'{NOMBRE[k]} {v}' for k, v in sorted(hemi_m.items(), key=lambda x: -x[1])[:5])
            + f' escaños; PP y Vox sumarían {hemi_m.get("PP", 0) + hemi_m.get("VOX", 0)}. Es una estimación con margen amplio, no una encuesta.') if hemi_m else None,
           ('¿Hay encuestas por provincias?',
            'Las encuestadoras casi nunca publican sus datos por provincia. Nuestro modelo reparte la media de las encuestas por provincia: '
            'la tabla con los escaños de cada una y las más disputadas está en mapaelectoral.es/encuestas/provincias.html.') if hay_provincias else None,
           ('¿Cuándo son las próximas elecciones generales?',
            'El domingo 29 de noviembre de 2026. Se eligen los 350 diputados del Congreso y los senadores; la mayoría absoluta del Congreso está en 176 escaños.'),
           ('¿Hasta cuándo se pueden publicar encuestas?',
            'La ley electoral (artículo 69.7 de la LOREG) prohíbe publicar o difundir sondeos en los cinco días anteriores a la votación: del 24 al 28 de noviembre. '
            'Esta página dejará de añadir encuestas nuevas esos días.'),
           ('¿Por qué cada encuesta da un resultado distinto?',
            'Cada encuestadora pregunta a una muestra diferente (por teléfono, internet o panel), en fechas distintas, y aplica su propia «cocina» para '
            'pasar de lo que responde la gente a una estimación de voto. Por eso conviene mirar el conjunto y la tendencia, no una sola encuesta.'),
           ('¿Son fiables las encuestas?',
            'Aciertan el orden general, pero no el detalle: en las generales de 2019 y 2023 la media de las encuestas se equivocó hasta en 3,4 puntos en algún partido. '
            'Un partido puede ganar o perder varios escaños por diferencias de un punto en algunas provincias.'),
           ('¿Cuántas encuestas se han publicado desde las últimas generales?',
            f'Esta página recoge {n_desde23:,} encuestas de ámbito estatal publicadas desde las generales de julio de 2023, sin contar las reestimaciones del CIS hechas por otras empresas.'.replace(',', '.')),
           ('¿Cada cuánto se actualiza esta página?',
            'Una vez al día, por la mañana. Cuando aparece una encuesta nueva, la tabla, el gráfico y las cifras de esta página se recalculan solos.')]
    faq = [x for x in faq if x]
    faq_html = '<div class="faq">' + ''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq) + '</div>'
    actual = fecha_larga(hoy.isoformat())
    descripcion = re.sub(r'\s+', ' ', entradilla)[:300]
    # h1 con los términos que se buscan («encuestas», «generales») sin perder la cifra del titular
    h1 = 'Encuestas de las generales: ' + (titular[0].lower() + titular[1:] if titular.startswith('El ') else titular).replace(' encuestas;', ';', 1)
    imagen = f'{BASE}/img/compartir/encuestas.jpg?v={hoy.isoformat()}'   # la tarjeta cambia: versión para que las redes no usen la vieja
    if tarjeta:
        tarjeta(RAIZ / 'img/compartir/encuestas.jpg', titular,
                [('Sumar' if k == 'SUMAR' else n, med[k], c) for k, n, c, _ in PRINCIPALES if k in med],
                [(k, hemi[k], next(c for kk, _, c, _ in TODOS if kk == k)) for k in ORDEN_HEMI if k in (hemi or {})],
                f'PP + Vox: {hemi.get("PP", 0) + hemi.get("VOX", 0)} · mayoría, 176' if hemi else '', fecha_larga(hoy.isoformat()))
    insertable(h1, med, hemi, n_hemi, actual, hoy)
    jsonld = [{'@context': 'https://schema.org', '@type': 'AnalysisNewsArticle', '@id': URL + '#articulo', 'headline': h1,
               'description': descripcion, 'url': URL, 'mainEntityOfPage': URL, 'inLanguage': 'es',
               'datePublished': '2026-10-22', 'dateModified': hoy.isoformat(), 'image': [imagen],
               'about': {'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'},   # no Event: Search Console lo marca (PR #52)
               'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'}, 'publisher': MEDIO,
               'isAccessibleForFree': True},
              {'@context': 'https://schema.org', '@type': 'Dataset', '@id': URL + '#datos',
               'name': 'Encuestas de las elecciones generales de España (29 de noviembre de 2026)',
               'alternateName': ['Encuestas elecciones generales 2026', 'Sondeos de las generales del 29N'],
               'description': (f'Estimación de voto y escaños de cada encuesta de ámbito estatal publicada desde las generales de julio de 2023 '
                               f'({n_desde23} encuestas a {actual}), con encuestadora, medio, fechas de trabajo de campo, tamaño de la muestra y '
                               'enlace a la publicación original. Se actualiza cada día con Electográfica y la tabla de Wikipedia.'),
               'url': URL, 'license': 'https://creativecommons.org/licenses/by-sa/4.0/', 'isAccessibleForFree': True,
               'inLanguage': 'es', 'datePublished': '2026-10-22', 'dateModified': hoy.isoformat(),
               'temporalCoverage': f'2023-07-24/{hoy.isoformat()}', 'spatialCoverage': {'@type': 'Place', 'name': 'España'},
               'keywords': ['encuestas', 'sondeos', 'elecciones generales', 'España', '29N', 'estimación de voto', 'escaños', 'Congreso'],
               'measurementTechnique': 'Encuestas de opinión publicadas por cada encuestadora (teléfono, internet o panel), recogidas tal como se publicaron',
               'variableMeasured': ['Encuestadora', 'Medio', 'Inicio y fin del trabajo de campo', 'Fecha de publicación', 'Tamaño de la muestra']
                                   + [f'Estimación de voto de {n} (%)' for _, n, *_ in PRINCIPALES] + ['Escaños de cada partido en el Congreso'],
               'isBasedOn': ['https://www.electografica.com/', 'https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Spanish_general_election'],
               'creator': MEDIO, 'distribution': [{'@type': 'DataDownload', 'name': 'Todas las encuestas', 'encodingFormat': 'text/csv',
                                                   'contentUrl': f'{BASE}/previsiones/datos/encuestas/encuestas_limpias.csv'},
                                                  {'@type': 'DataDownload', 'name': 'Encuestas con escaños, según Wikipedia', 'encodingFormat': 'text/csv',
                                                   'contentUrl': f'{BASE}/previsiones/datos/encuestas/wikipedia_generales_espana.csv'}]},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': URL + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    titulo = 'Encuestas elecciones generales 2026: sondeos y promedio del 29N'
    main_html = f"""<main>
<p class="kicker">Elecciones generales · 29 de noviembre</p>
<h1 data-miga="Encuestas">{html.escape(h1)}</h1>
<p class="dek">{html.escape(entradilla)}</p>
<p class="firma">Por <a href="../sobre-mi.html">{AUTOR}</a> · Actualizado el <time datetime="{hoy.isoformat()}">{actual}</time></p>
<p data-tipo="dato">{html.escape(p1)}</p>
<p data-tipo="dato">{html.escape(p2)}</p>
<figure>
<figcaption><span class="t">Voto estimado en cada encuesta, último año</span><span class="s">Cada punto es una encuesta; la línea es la mediana de la última encuesta de cada encuestadora en los {VENTANA_MEDIANA} días anteriores (con tres o más). Porcentaje sobre voto válido. Sumar incluye el Frente Amplio y sus socios.</span></figcaption>
<div class="chart" id="graf"></div>
<div class="legend">{''.join(f'<span><i class="sw" style="background:{c}"></i>{n}</span>' for _, n, c, _ in PRINCIPALES)}</div>
<p class="src">Encuestas publicadas, vía Electográfica y Wikipedia. La mediana resume las encuestas: no es una previsión de Mapa Electoral.</p>
</figure>
<details class="caja"><summary>Cómo se hace la media: qué pesa más y qué hemos descartado</summary><ul>
<li><b>En el gráfico y las cifras de arriba</b>, la línea es la mediana de la última encuesta de cada encuestadora en las tres últimas semanas. Es un resumen descriptivo: cada encuestadora cuenta igual.</li>
<li><b>En nuestro modelo</b>, la media es ponderada. Entra la última encuesta de cada encuestadora de los últimos 28 días, y pesa más cuanto más reciente es y cuanto mayor es su muestra: una encuesta de hace diez días pesa algo más de un tercio que una de hoy, y una de 3.000 entrevistas, 1,7 veces una de 1.000.</li>
<li><b>Lo que hemos probado y descartado</b>: corregir el sesgo de cada encuestadora y el sesgo histórico del conjunto. Con las generales de 2019 y 2023 y las autonómicas desde 2015, ninguna de las dos correcciones reducía el error de la media. Tampoco ponderamos por técnica (teléfono o internet): no hay datos que muestren que una acierte más que otra.</li>
</ul><p><a href="metodo-modelo.html">Método completo del modelo</a></p></details>
<h2>Promedio de escaños: lo que da cada encuestadora</h2>
{bloque_hemi}
{'<figure><figcaption><span class="t">PP + Vox en cada encuesta</span><span class="s">Escaños que dan juntos en la última encuesta de cada encuestadora del último mes; la barra es la horquilla de la propia encuestadora. La línea marca la mayoría absoluta (176).</span></figcaption><div class="chart" id="horq-encuestas"></div></figure>' if pv_casas else ''}
<p>Última encuesta de cada una en los últimos 30 días, con los escaños que publica. Un intervalo («132-137») es la horquilla de la propia encuestadora; la mayoría absoluta está en 176.</p>
{tabla_esc}
{bloque_modelo or ''}
<h2>Últimas encuestas de las elecciones generales</h2>
<p>Voto estimado en porcentaje y, debajo, escaños cuando la encuestadora los publica. Cada nombre enlaza a la publicación original. «CIS reestimado por…» son los datos brutos del CIS recalculados por otra empresa: no cuentan como encuesta propia ni entran en el gráfico. La fecha es la de publicación; con asterisco, la del final del trabajo de campo cuando la publicación no consta.</p>
{tabla}
{tabla_ant}
<h2>Encuestas de cada encuestadora</h2>
<p>La última encuesta de cada una, cómo ha cambiado, cuánto se aparta de las demás y cuánto acertó en 2023.</p>
<ul class="casas">{''.join(f'<li><a href="{r}/">{html.escape(n)}</a> <small>{k} encuestas</small></li>' for r, n, k, _ in casas)}</ul>
<h2>Preguntas frecuentes sobre las encuestas</h2>
{faq_html}
<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se recoge</dt><dd>Todas las encuestas de ámbito estatal con estimación de voto para el Congreso publicadas desde las generales de julio de 2023, tal como las publicó cada encuestadora. No se recogen medias de otros medios ni sondeos internos de los partidos.</dd>
<dt>Límites</dt><dd>Las encuestas no son resultados. Cada encuestadora usa su método (teléfono, internet, panel), su muestra y su forma de estimar, y en las generales de 2019 y 2023 la media de las encuestas se equivocó hasta en 3,4 puntos en un partido. La estimación del CIS se aparta del resto (<a href="../actualidad/cis-tezanos-estimacion-29n/">así le fue en elecciones anteriores</a>). La mediana del gráfico es un resumen, no una previsión.</dd>
<dt>Fuentes</dt><dd><ul><li>Cada encuesta enlaza a su publicación original (medio o encuestadora).</li><li><a href="https://www.electografica.com/">Electográfica</a>, para localizar las encuestas y su ficha técnica.</li><li><a href="https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Spanish_general_election">Wikipedia, «Opinion polling for the 2026 Spanish general election»</a> (CC BY-SA 4.0), para los escaños y los sondeos que no recoge Electográfica.</li></ul></dd>
<dt>Actualización</dt><dd>Automática, una vez al día (código en <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/previsiones/src">previsiones/src</a>). Última: {actual}.</dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
</dl>
<p class="descargas">Descargar los datos: <a href="../previsiones/datos/encuestas/encuestas_limpias.csv">todas las encuestas (CSV)</a> · <a href="../previsiones/datos/encuestas/wikipedia_generales_espana.csv">con escaños, según Wikipedia (CSV)</a> · <a href="../img/compartir/encuestas.jpg" download="encuestas-generales-{hoy.isoformat()}.jpg">resumen de hoy en imagen, para redes</a></p>
<!--compartir-->
<details class="insertar"><summary>Insertar este resumen en tu web</summary><p>Copia este código: muestra la mediana de las encuestas y el promedio de escaños, se actualiza solo y enlaza a esta página. Datos con licencia CC BY-SA 4.0.</p>
<textarea rows="3" readonly onclick="this.select()" aria-label="Código para insertar el resumen de encuestas">&lt;iframe src="{URL}insertar.html" title="Encuestas de las elecciones generales · Mapa Electoral" width="100%" height="680" style="border:0;max-width:640px" loading="lazy"&gt;&lt;/iframe&gt;</textarea></details>
<h2>Sigue leyendo</h2><ul class="sigue">{'<li><a href="provincias.html"><span class="kicker">Por provincias</span><b>Los escaños de cada provincia según la media de encuestas</b></a></li>' if hay_provincias else ''}<li><a href="../"><span class="kicker">Mapa</span><b>El mapa de las generales, sección a sección</b></a></li><li><a href="../actualidad/cis-tezanos-estimacion-29n/"><span class="kicker">Encuestas</span><b>El CIS y sus estimaciones frente a los resultados</b></a></li><li><a href="../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a> · <a href="../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    pagina = (cabecera(titulo, descripcion, URL, imagen, jsonld)
              .replace('<meta property="og:title" content="' + html.escape(titulo) + '">', '<meta property="og:title" content="' + html.escape(titular) + '">')
              + ESTILOS + encuestadoras.css_partidos(PRINCIPALES) + CSS_SITIO + '\n</head>\n<body>\n' + nav('../', 'Encuestas') + '\n' + main_html + '\n'
              + SCRIPT.replace('__DATOS__', json.dumps(datos, ensure_ascii=False, separators=(',', ':'))) + '\n</body>\n</html>\n')
    SALIDA.mkdir(exist_ok=True)
    from urllib.parse import quote
    texto, enlace, etiquetas = post_x(titular, med, hoy.isoformat())
    intento = f'https://x.com/intent/post?text={quote(texto + chr(10) + chr(10) + etiquetas)}&url={quote(enlace)}'
    bsky = f'https://bsky.app/intent/compose?text={quote(texto + " " + enlace + chr(10) + chr(10) + etiquetas)}'
    pagina = pagina.replace('<!--compartir-->', f'<p class="descargas">Compartir el resumen de hoy: <a href="{html.escape(intento)}" target="_blank" rel="noopener">en X</a> · '
                            f'<a href="{html.escape(bsky)}" target="_blank" rel="noopener">en Bluesky</a></p>', 1)
    (SALIDA / 'index.html').write_text(pagina, encoding='utf-8')
    (SALIDA / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                        f'  <url><loc>{URL}</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n  <url><loc>{URL}metodo-modelo.html</loc></url>\n'
                                        + (f'  <url><loc>{URL}provincias.html</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n' if hay_provincias else '')
                                        + (f'  <url><loc>{URL}calculadora-escanos/</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n' if hay_calculadora else '')
                                        + ''.join(f'  <url><loc>{URL}{r}/</loc><lastmod>{f}</lastmod></url>\n' for r, _, _, f in casas)
                                        + ''.join(f'  <url><loc>{URL}{r}/</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n' for r, _ in PROV_PAGINAS) + '</urlset>\n', encoding='utf-8')
    portada(titular, med, actual)
    # post para redes de esta actualización: el workflow solo vuelve a escribirlo cuando entra una encuesta nueva
    texto, enlace, etiquetas = post_x(titular, med, hoy.isoformat())
    (SALIDA / 'post-redes.txt').write_text(f'{texto}\n{enlace}\n\n{etiquetas}\n', encoding='utf-8')
    # autor común y migas de pan (BreadcrumbList), como en el resto del sitio: la página se regenera sola dos veces al día
    sys.path.insert(0, str(RAIZ / 'src'))
    import esquema
    for f in [SALIDA / 'index.html', SALIDA / 'metodo-modelo.html', SALIDA / 'provincias.html'] + [SALIDA / r / 'index.html' for r, *_ in casas + PROV_PAGINAS]:
        if f.exists():
            esquema.procesa(f)
    print(f'encuestas: {len(encs)} encuestas, {len(recientes)} en la tabla; {titular}')


if __name__ == '__main__':
    main()
