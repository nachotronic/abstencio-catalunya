"""Una página por encuestadora: /encuestas/<casa>/ con su última encuesta, el cambio respecto a la anterior, cómo se
aparta de las demás, lo que dio antes de las generales de 2023 y todas sus encuestas desde entonces.

La llama construir.py (main) con las encuestas ya cargadas, así que se rehace sola cada vez que entra una encuesta.
Todo son cifras publicadas por la encuestadora o cálculos descriptivos sobre ellas (dato): nada de previsiones.
"""
import html, json, re, statistics
from datetime import date, timedelta

# Resultado oficial de las generales del 23-7-2023 (Ministerio del Interior), en % sobre voto válido
RESULTADO_2023 = {'PP': 33.05, 'PSOE': 31.70, 'VOX': 12.39, 'SUMAR': 12.31}
RESULTADO_2023_TXT = {'PP': '33,1\u00a0%', 'PSOE': '31,7\u00a0%', 'VOX': '12,4\u00a0%', 'SUMAR': '12,3\u00a0%'}
MIN_ENCUESTAS = 10        # encuestas desde las generales de 2023 para tener página propia
ACTIVA_DIAS = 120         # y al menos una con el trabajo de campo terminado en estos días
# nombre con que se busca cada casa; las demás usan el suyo tal cual. (ruta, nombre, quién la hace, título)
CASAS = {
    'emanalytics': ('electopanel', 'ElectoPanel', 'EM-Analytics para Electomanía',
                    'ElectoPanel de Electomanía hoy: última encuesta de las generales 2026'),
    'cis': ('cis', 'CIS', 'Centro de Investigaciones Sociológicas',
            'Encuesta del CIS {mes}: barómetro y estimación de voto para las generales 2026'),
    '40db': ('40db', '40dB.', None, None),
    'sigmados': ('sigma-dos', 'Sigma Dos', None, None),
    'sociometrica': ('sociometrica', 'SocioMétrica', None, None),
    'targetpoint': ('target-point', 'Target Point', None, None),
    'ncreport': ('nc-report', 'NC Report', None, None),
    'hamalgamametrica': ('hamalgama-metrica', 'Hamalgama Métrica', None, None),
    'dym': ('dym', 'DYM', None, None),
    'invymark': ('invymark', 'InvyMark', None, None),
    'celestetel': ('celeste-tel', 'Celeste-Tel', None, None),
    'gad3': ('gad3', 'GAD3', None, None),
    'gesop': ('gesop', 'GESOP', None, None),
    'simplelogica': ('simple-logica', 'Simple Lógica', None, None),
}
MESES_L = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


def ruta_de(k):
    return CASAS.get(k, (re.sub(r'[^a-z0-9]+', '-', k),))[0]


def nombre_de(k, casa):
    return CASAS[k][1] if k in CASAS else casa


def del_(nombre):
    return f'del {nombre}' if nombre == 'CIS' else f'de {nombre}'


def el(nombre, mayus=False):
    """«el CIS» (con artículo); el resto de casas, sin él."""
    return ('El ' if mayus else 'el ') + nombre if nombre == 'CIS' else nombre


def mediana_otras(encs, k, d, clave, ventana):
    """Mediana de cada partido con la última encuesta de cada una de las demás encuestadoras en los días anteriores a d."""
    ult = {}
    for e in encs:
        c = clave(e['casa'])
        f = date.fromisoformat(e['fin'])
        if c != k and not e['reest'] and d - timedelta(days=ventana) < f <= d and c not in ult:
            ult[c] = e
    out = {}
    for p in RESULTADO_2023:
        v = [e['voto'][p] for e in ult.values() if p in e['voto']]
        if len(v) >= 3:
            out[p] = statistics.median(v)
    return out


def ultima_2023(encs, clave):
    """Última encuesta de cada encuestadora antes de las generales de 2023 y su error medio en los cuatro grandes."""
    out = {}
    for e in encs:   # de más reciente a más antigua
        c = clave(e['casa'])
        if not e['reest'] and '2023-06-15' <= e['fin'] <= '2023-07-22' and c not in out and all(p in e['voto'] for p in RESULTADO_2023):
            out[c] = (e, sum(abs(e['voto'][p] - RESULTADO_2023[p]) for p in RESULTADO_2023) / len(RESULTADO_2023))
    return out


def svg_serie(propias, otras, partidos, pc):
    """Voto de cada partido en cada encuesta de la casa (puntos y línea) y, a trazos, la mediana de las demás en esas fechas."""
    W, H, m = 640, 300, {'l': 34, 'r': 70, 't': 10, 'b': 24}
    t = lambda iso: date.fromisoformat(iso).toordinal()
    t0, t1 = t(propias[-1]['fin']), t(propias[0]['fin'])
    if t1 == t0:
        t0 -= 30
    hi = 40
    x = lambda iso: m['l'] + (t(iso) - t0) / (t1 - t0) * (W - m['l'] - m['r'])
    y = lambda v: m['t'] + (1 - v / hi) * (H - m['t'] - m['b'])
    out = ''.join(f'<line x1="{m["l"]}" x2="{W - m["r"]}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="var(--grid)"/>'
                  f'<text x="{m["l"] - 6}" y="{y(v) + 4:.1f}" text-anchor="end">{v}%</text>' for v in range(0, hi + 1, 10))
    d0 = date.fromordinal(t0)
    mes = date(d0.year + (d0.month // 12), d0.month % 12 + 1, 1)
    paso = 3 if t1 - t0 > 400 else 2 if t1 - t0 > 200 else 1
    while mes.toordinal() <= t1:
        out += f'<text x="{x(mes.isoformat()):.1f}" y="{H - 6}" text-anchor="middle">{["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"][mes.month - 1]}{" " + str(mes.year) if mes.month <= paso else ""}</text>'
        mes = date(mes.year + (mes.month + paso - 1) // 12, (mes.month + paso - 1) % 12 + 1, 1)
    fin = []
    for k, n, *_ in partidos:
        pts = [(e['fin'], e['voto'][k]) for e in reversed(propias) if k in e['voto']]
        if not pts:
            continue
        med = [(e['fin'], o[k]) for e, o in zip(reversed(propias), reversed(otras)) if k in o]
        if len(med) > 1:
            out += f'<path class="s-{k}" d="' + ''.join(f'{"L" if i else "M"}{x(f):.1f},{y(v):.1f}' for i, (f, v) in enumerate(med)) + '" fill="none" stroke-width="1.5" stroke-dasharray="4 3" opacity=".55"/>'
        if len(pts) > 1:
            out += f'<path class="s-{k}" d="' + ''.join(f'{"L" if i else "M"}{x(f):.1f},{y(v):.1f}' for i, (f, v) in enumerate(pts)) + '" fill="none" stroke-width="2.2" stroke-linejoin="round"/>'
        out += ''.join(f'<circle class="f-{k}" cx="{x(f):.1f}" cy="{y(v):.1f}" r="2.6"><title>{n} {pc(v)}, {date.fromisoformat(f).strftime("%d-%m-%Y")}</title></circle>' for f, v in pts)
        fin.append([y(pts[-1][1]) + 4, k, 'Sumar' if k == 'SUMAR' else n])
    fin.sort()
    for i in range(1, len(fin)):
        fin[i][0] = max(fin[i][0], fin[i - 1][0] + 13)
    out += ''.join(f'<text class="f-{k}" x="{W - m["r"] + 6}" y="{yy:.1f}" style="font-weight:600">{n}</text>' for yy, k, n in fin)
    return f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Voto estimado de cada partido en cada encuesta y mediana de las demás encuestadoras">{out}</svg>'


def css_partidos(partidos):
    claro = ''.join(f'.s-{k}{{stroke:{c}}}.f-{k}{{fill:{c}}}' for k, _, c, _ in partidos)
    oscuro = ''.join(f'.s-{k}{{stroke:{o}}}.f-{k}{{fill:{o}}}' for k, _, _, o in partidos)
    return (f'<style>{claro}@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]) {oscuro.replace("}.", "} :root:not([data-theme=light]) .")}}}'
            f':root[data-theme="dark"] {oscuro.replace("}.", "} :root[data-theme=dark] .")}'
            '.casas{columns:2;font-family:var(--ui);font-size:.95rem;padding-left:1.1rem}.casas li{margin:.15rem 0}'
            '@media (max-width:520px){.casas{columns:1}}</style>')


def genera(encs, salida, c):
    """Escribe encuestas/<casa>/index.html de cada encuestadora con datos suficientes. c es el módulo construir
    (colores, formato y cabecera comunes). Devuelve [(ruta, nombre, n encuestas, fecha última)] para el índice."""
    clave, pc, hoy = c.clave, c.pc, date.today()
    desde23 = [e for e in encs if e['fin'] >= '2023-07-24' and not e['reest']]
    grupos = {}
    for e in desde23:
        grupos.setdefault(clave(e['casa']), []).append(e)
    activas = {k: v for k, v in grupos.items() if len(v) >= MIN_ENCUESTAS and k not in c.NO_ENCUESTAS
               and date.fromisoformat(v[0]['fin']) > hoy - timedelta(days=ACTIVA_DIAS)}
    de2023 = ultima_2023(encs, clave)
    ranking = sorted(de2023, key=lambda k: de2023[k][1])
    casas = sorted(activas, key=lambda k: -len(activas[k]))
    indice = [(ruta_de(k), nombre_de(k, activas[k][0]['casa']), len(activas[k]), activas[k][0].get('publicado') or activas[k][0]['fin']) for k in casas]
    PRIN = c.PRINCIPALES
    for k in casas:
        propias = activas[k]
        ruta, nombre = ruta_de(k), nombre_de(k, propias[0]['casa'])
        quien = CASAS.get(k, (None, None, None))[2]
        u = propias[0]
        pub = u.get('publicado') or u['fin']
        medio = u['medio'] if u['medio'] and u['medio'] not in ('los grupos',) else ''
        orden = sorted(u['voto'], key=u['voto'].get, reverse=True)
        art = lambda p: '' if p in ('VOX', 'SUMAR', 'PODEMOS', 'SALF') else 'el '
        nom = lambda p: 'Sumar' if p == 'SUMAR' else c.NOMBRE[p]
        cifras = lambda e, ps: ', '.join(f'{nom(p)} {pc(e["voto"][p])}' + (f' ({e["esc"][p]} escaño{"" if e["esc"][p] == "1" else "s"})' if p in e['esc'] else '') for p in ps if p in e['voto'])
        h1 = f'Última encuesta {del_(nombre)}: ' + ', '.join(f'{nom(p)} {pc(u["voto"][p])}' for p in orden[:3])
        mes = f'{MESES_L[date.fromisoformat(pub).month - 1]} {date.fromisoformat(pub).year}'
        titulo = (CASAS.get(k, (0, 0, 0, None))[3] or 'Encuesta {nombre} {mes}: última estimación para las generales del 29N').format(nombre=nombre, mes=mes)
        muestra = f'{int(u["muestra"]):,}'.replace(',', '.') if str(u['muestra']).isdigit() else ''
        p1 = (f'{el(nombre, True)} publicó su última encuesta de las elecciones generales el {c.fecha_larga(pub)}'
              + (f', para {medio}' if medio else '') + (f', con {muestra} entrevistas' if muestra else '') + '. '
              + f'Da como primer partido {"al " if art(orden[0]) else "a "}{nom(orden[0])}: ' + cifras(u, [p for p, *_ in PRIN]) + '.')
        if 'PP' in u['esc'] and 'VOX' in u['esc']:
            lo, hi = c.suma_pv(u)
            p1 += f' PP y Vox suman {lo if lo == hi else f"entre {lo} y {hi}"} escaños; la mayoría absoluta está en 176.'
        p2 = ''
        if len(propias) > 1:
            a = propias[1]
            cambios = []
            for p, *_ in PRIN[:4]:
                if p in u['voto'] and p in a['voto']:
                    dlt = round(u['voto'][p] - a['voto'][p], 1)
                    cambios.append(f'{nom(p)} se queda igual' if dlt == 0 else f'{nom(p)} {"sube" if dlt > 0 else "baja"} {pc(abs(dlt)).replace(chr(160) + "%", "")} puntos')
            p2 = f'Respecto a su encuesta anterior, publicada el {c.fecha_larga(a.get("publicado") or a["fin"])}: ' + ', '.join(cambios[:-1]) + f' y {cambios[-1]}.' if len(cambios) > 1 else ''
        # cómo se aparta del resto: diferencia media con la mediana de las demás en el último año
        anio = [e for e in propias if date.fromisoformat(e['fin']) > hoy - timedelta(days=365)]
        otras = [mediana_otras(encs, k, date.fromisoformat(e['fin']), clave, c.VENTANA_MEDIANA) for e in anio]
        p3, dif = '', {}
        if len(anio) >= 5:
            for p in ('PP', 'PSOE', 'VOX', 'SUMAR'):
                v = [e['voto'][p] - o[p] for e, o in zip(anio, otras) if p in e['voto'] and p in o]
                if len(v) >= 5:
                    dif[p] = sum(v) / len(v)
            if dif:
                frase = lambda p: (f'{"al " if p in ("PP", "PSOE") else "a "}{nom(p)} lo mismo' if abs(dif[p]) < .25 else
                                   f'{"al " if p in ("PP", "PSOE") else "a "}{nom(p)} {pc(abs(dif[p])).replace(chr(160) + "%", "")} puntos {"más" if dif[p] > 0 else "menos"}')
                ps = list(dif)
                p3 = (f'En sus {len(anio)} encuestas del último año, {el(nombre)} da de media ' + ', '.join(frase(p) for p in ps[:-1]) + f' y {frase(ps[-1])}'
                      + ' que la mediana de las demás encuestadoras en las mismas fechas (la última de cada una en las tres semanas anteriores).')
        p4 = ''
        if k in de2023:
            e23, err = de2023[k]
            pos = ranking.index(k) + 1
            p4 = (f'Su última encuesta antes de las generales de 2023, del {c.fecha_larga(e23.get("publicado") or e23["fin"])}, daba '
                  + ', '.join(f'{nom(p)} {pc(e23["voto"][p])} (sacó {RESULTADO_2023_TXT[p]})' for p in RESULTADO_2023)
                  + f'. Se equivocó de media {pc(err).replace(chr(160) + "%", "")} puntos en esos cuatro partidos: '
                  + (f'fue la que más se acercó de las {len(ranking)} con encuesta final.' if pos == 1 else
                     f'la {pos}.ª de {len(ranking)} encuestadoras con encuesta final, de más a menos acertada.'))
        dek = (f'Todas las encuestas {del_(nombre)} para las elecciones generales desde 2023, con su fuente: la última, cómo cambia y cómo se compara con las demás encuestadoras.')
        descripcion = (f'Última encuesta {del_(nombre)} ({c.dia(pub, True)}): ' + cifras(u, orden[:4]).replace(' escaños)', ')')
                       + '. Cambio respecto a la anterior, comparación con las demás y todas sus encuestas desde 2023.')[:300]
        faq = [(f'¿Qué dice la última encuesta {del_(nombre)}?', p1),
               (f'¿Cómo ha cambiado respecto a su encuesta anterior?', p2) if p2 else None,
               (f'¿{el(nombre, True)} da más o menos voto que las demás encuestas?', p3) if p3 else None,
               (f'¿Acertó {el(nombre)} en las generales de 2023?', p4) if p4 else None,
               (f'¿Cuántas encuestas ha publicado {el(nombre)}?',
                f'{len(propias)} encuestas de ámbito estatal para el Congreso desde las generales de julio de 2023, que están todas en la tabla de esta página con el enlace a su publicación.')]
        faq = [x for x in faq if x]
        url = f'{c.URL}{ruta}/'
        imagen = f'{c.BASE}/img/compartir/encuestas.jpg?v={hoy.isoformat()}'
        jsonld = [{'@context': 'https://schema.org', '@type': 'AnalysisNewsArticle', '@id': url + '#articulo', 'headline': h1, 'description': descripcion,
                   'url': url, 'mainEntityOfPage': url, 'inLanguage': 'es', 'datePublished': '2026-10-26', 'dateModified': pub if pub > '2026-10-26' else '2026-10-26',
                   'image': [imagen], 'about': [{'@type': 'Thing', 'name': 'Elecciones generales de España de 2026'},
                                                {'@type': 'Organization', 'name': quien or nombre}],
                   'author': {'@type': 'Person', 'name': c.AUTOR, 'url': c.BASE + '/sobre-mi.html'}, 'publisher': c.MEDIO, 'isAccessibleForFree': True},
                  {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
                   'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
        cab = ''.join(f'<th class="n"><i class="pt" style="background:{col}"></i>{"Sumar" if p == "SUMAR" else n}</th>' for p, n, col, _ in PRIN)
        tabla = (f'<div class="tbl"><table><thead><tr><th>Encuesta y medio</th><th class="n">Publicada</th><th class="n">Muestra</th>{cab}</tr></thead>'
                 f'<tbody>{"".join(c.fila_tabla(e) for e in propias)}</tbody></table></div>')
        grafico = (f'<figure><figcaption><span class="t">Voto estimado en cada encuesta {del_(nombre)}</span><span class="s">Cada punto es una encuesta {del_(nombre)} del último año; '
                   f'a trazos, la mediana de las demás encuestadoras en las mismas fechas. Porcentaje sobre voto válido.</span></figcaption>'
                   f'<div class="chart">{svg_serie(anio, otras, PRIN[:4], pc)}</div>'
                   f'<div class="legend">{"".join(f"<span><i class=sw style=background:{col}></i>{n}</span>" for _, n, col, _ in PRIN[:4])}</div></figure>') if len(anio) >= 2 else ''
        otras_casas = ''.join(f'<li><a href="../{r}/">{html.escape(n)}</a></li>' for r, n, *_ in indice if r != ruta)
        extra_cis = ('<p>La estimación del CIS se aparta del resto de encuestadoras, sobre todo en el PSOE: '
                     '<a href="../../actualidad/cis-tezanos-estimacion-29n/">así le fue en elecciones anteriores</a>.</p>') if k == 'cis' else ''
        cuerpo = f"""<main>
<p class="kicker"><a href="../">Encuestas elecciones generales 2026</a> · 29N</p>
<h1 data-miga="{html.escape(nombre)}">{html.escape(h1)}</h1>
<p class="dek">{html.escape(dek)}</p>
<p class="firma">Por <a href="../../sobre-mi.html">{c.AUTOR}</a> · Actualizado el <time datetime="{pub}">{c.fecha_larga(pub)}</time></p>
<p data-tipo="dato">{html.escape(p1)} <a href="{html.escape(u['url'])}">Publicación original</a>.</p>
{f'<p data-tipo="dato">{html.escape(p2)}</p>' if p2 else ''}
{grafico}
{f'<h2>¿Da {el(nombre)} más o menos voto que las demás?</h2><p data-tipo="dato">{html.escape(p3)}</p>' if p3 else ''}
{f'<h2>¿Acertó {el(nombre)} en las generales de 2023?</h2><p data-tipo="dato">{html.escape(p4)}</p>' if p4 else ''}
{extra_cis}
<h2>Todas las encuestas {del_(nombre)} desde 2023</h2>
<p>Voto estimado en porcentaje y, debajo, escaños cuando la encuestadora los publica. Cada fila enlaza a la publicación original.</p>
{tabla}
<p><a href="../">Todas las encuestas de las elecciones generales 2026, su promedio y nuestra estimación →</a></p>
<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
<h2>Las demás encuestadoras</h2>
<ul class="casas">{otras_casas}</ul>
<p class="src">Fuentes: cada encuesta enlaza a su publicación original; <a href="https://www.electografica.com/">Electográfica</a> y <a href="https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Spanish_general_election">Wikipedia</a> (CC BY-SA 4.0) para localizarlas. Resultado de 2023: Ministerio del Interior. Se actualiza sola cuando entra una encuesta nueva.</p>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
        pagina = (c.cabecera(titulo, descripcion, url, imagen, jsonld) + c.ESTILOS + css_partidos(PRIN) + c.CSS_SITIO
                  + '\n</head>\n<body>\n' + c.nav('../../', 'Encuestas') + '\n' + cuerpo + '\n</body>\n</html>\n')
        (salida / ruta).mkdir(exist_ok=True)
        (salida / ruta / 'index.html').write_text(pagina, encoding='utf-8')
    return indice
