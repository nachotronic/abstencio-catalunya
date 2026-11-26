"""Páginas «Voto útil en <provincia>» (elecciones/…/voto-util-29n/): una por circunscripción, con los votos de 2023 y los escaños de 2026.

Las llama territorios.py (main) con sus propias piezas de página (cabeza, migas, faq, PIE…), que recibe en T_. Los cálculos, en voto_util.py.
"""
from html import escape

import voto_util as VU

PUBLICADA = '2026-11-26'
ACTUALIZADA = '2026-11-26'
COLOR_EXTRA = {'OTROS': '#9a9a9a'}
ORD = {1: 'primero', 2: 'segundo', 3: 'tercero', 4: 'cuarto', 5: 'quinto', 6: 'sexto', 7: 'séptimo', 8: 'octavo', 9: 'noveno', 10: 'décimo'}
CSS = ('.vu-fila{display:flex;flex-wrap:wrap;gap:3px;align-items:center;margin:.4rem 0}'
       '.sq{display:inline-block;width:18px;height:18px;border-radius:3px;background:var(--c);box-sizing:border-box}'
       '.sq.prob{opacity:.5}'
       '.sq.jue{background:repeating-linear-gradient(135deg,var(--c) 0 3px,transparent 3px 6px);border:2px solid var(--c)}'
       '.sq.alc{background:none;border:2px dashed var(--c)}'
       '.sq.ult{outline:2px solid var(--fg);outline-offset:1px}'
       '.vu-sep{display:inline-block;width:1px;height:22px;background:var(--fg);margin:0 6px}'
       '.vu-et{font-family:var(--sans);font-size:.8rem;color:var(--muted);margin:0 4px}'
       'table.vu td .sq{width:14px;height:14px}table.vu td{vertical-align:middle}table.vu td.c{min-width:4.5rem}'
       '.vu-ley{font-family:var(--sans);font-size:.85rem;display:flex;flex-wrap:wrap;gap:.3rem 1rem;margin:.3rem 0}.vu-ley span{display:inline-flex;align-items:center;gap:5px}'
       '.vu-ley .sq{width:14px;height:14px}')


CON_ART = {'PP', 'PSOE', 'PNV', 'BNG', 'PRC', 'PAR', 'PACMA', 'PCTE', 'PUM+J', 'Frente Obrero'}


def el(l):
    return f'el {l}' if l in CON_ART else l


def del_(l):
    return f'del {l}' if l in CON_ART else f'de {l}'


def al(l):
    return f'al {l}' if l in CON_ART else f'a {l}'


def n(x):
    return f'{int(round(x)):,}'.replace(',', '.')


def pc(x, d=1):
    return f'{x:.{d}f}'.replace('.', ',') + ' %'


def ord_(k):
    return ORD.get(k, f'{k}.º')


def color(f, COLOR):
    return COLOR.get(f) or COLOR_EXTRA.get(f) or '#9a9a9a'


def sq(col, cls='', titulo=''):
    return f'<span class="sq {cls}" style="--c:{col}" title="{escape(titulo)}"></span>'


def ruta(p, ruta_provincia):
    return ruta_provincia(p) + 'voto-util-29n/'


def pagina(p, a, T_):
    """T_: dict con cabeza, migas_html, faq, ld_pagina, PIE, ruta_provincia, PROV_NOMBRE, PROV_CCAA, CCAA, PROV_SLUG, COLOR, nombre_t, fecha, esquema, LASTMOD, PUBLICADA."""
    COLOR = T_['COLOR']
    r = ruta(p, T_['ruta_provincia'])
    nivel = r.count('/')
    raiz = '../' * nivel
    nom = T_['PROV_NOMBRE'][p]
    nom_t = T_['nombre_t'](p)
    c_ = T_['PROV_CCAA'][p]
    ccaa_nom = T_['CCAA'][c_][0]
    uni = len(T_['CCAA'][c_][2]) == 1
    e = a['e']
    u, s = a['ultimo'], a['siguiente']
    col = {x['l']: color(x['f'], COLOR) for x in a['listas']}
    listas = sorted(a['listas'], key=lambda x: -x['v'])
    con = [x for x in listas if x['esc']]
    sin = a['sin_escano_listas']
    desc_esc = 'su único escaño' if e == 1 else f'el último de sus {e} escaños'
    frase_ult = (f'{desc_esc[0].upper() + desc_esc[1:]} fue el {ord_(u["k"])} {del_(u["l"])}' if e > 1
                 else f'Su único escaño fue para {el(u["l"])}')
    titulo = f'Voto útil en {nom_t} el 29N: a cuántos votos quedó cada escaño en 2023'
    desc = (f'Con los votos de 2023 y los {e} escaños de 2026, el último escaño de {nom} fue para {el(u["l"])}; {al(s["l"])} le habrían bastado {n(a["cambian"])} votantes. '
            f'{n(a["sin_escano"])} votos ({pc(a["sin_escano_pct"])}) no eligieron a nadie.') if e > 1 else (
            f'Con los votos de 2023, el único escaño de {nom} fue para {el(u["l"])}; {al(s["l"])} le habrían bastado {n(a["cambian"])} votantes. '
            f'{n(a["sin_escano"])} votos ({pc(a["sin_escano_pct"])}) no eligieron a nadie.')
    qs = [(f'¿Cuántos diputados elige {nom} el 29N?',
           f'{e}. Se reparten con la regla D\'Hondt entre las candidaturas que pasan del 3 % de los votos válidos de la circunscripción.'),
          (f'¿Cuántos votos hace falta para sacar un escaño en {nom}?',
           f'La ley pide al menos el 3 % de los votos válidos: con la participación de 2023, unos {n(a["barrera"])}. Pero el listón real es el último cociente: '
           f'en 2023, el último escaño de {nom} se repartió con {n(u["q"])} votos por escaño.'),
          ('¿Qué es el voto útil?',
           'Votar a una candidatura con opciones de sacar escaño en tu provincia en vez de a la preferida, para que el voto cuente en el reparto. '
           'Esta página no recomienda ningún voto: muestra, con los votos de 2023, qué escaños estuvieron más ajustados y qué votos no eligieron a nadie.')]
    faq_html, faq_ld = T_['faq'](qs)
    about = {'@type': 'AdministrativeArea', 'name': nom, 'containedInPlace': {'@type': 'Country', 'name': 'España'}}
    ld = T_['ld_pagina'](titulo, desc, r, about)
    ld['datePublished'] = PUBLICADA
    ld['dateModified'] = T_['LASTMOD'][r] = ACTUALIZADA
    h = [T_['cabeza'](titulo, desc, r, [ld, faq_ld], nivel, f'Voto útil en {nom}')]
    h.append(f'<style>{CSS}</style>')
    pasos = [(raiz, 'Inicio'), (raiz + 'elecciones/', 'Elecciones'), (raiz + f'elecciones/{c_}/', ccaa_nom)]
    if not uni:
        pasos.append(('../', nom))
    h.append(T_['migas_html'](pasos))
    h.append(f'<p class="kicker">Elecciones generales · 29 de noviembre de 2026</p><h1 data-miga="Voto útil">Voto útil en {escape(nom_t)}: a cuántos votos estuvo cada escaño en 2023</h1>')
    h.append('<p class="subtitulo">Quién se llevó cada escaño, cuáles estaban seguros y cuáles en juego, quién se quedó a las puertas y qué votos no eligieron a nadie, '
             'con los votos de 2023 y los escaños de 2026</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{T_["esquema"].FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADA}">{T_["fecha"](ACTUALIZADA)}</time></p>')
    reparto_txt = ', '.join(f'{x["l"]} {x["esc"]}' for x in con)
    h.append(f'<p class="resumen"><span class="tipo t-dato">Dato</span>{escape(nom)} elige {e} {"diputado" if e == 1 else "diputados"} el 29 de noviembre. '
             f'Con los votos de las generales de 2023 se habrían repartido así: {escape(reparto_txt)}. '
             f'{escape(frase_ult)}, y quien se quedó a las puertas fue {escape(el(s["l"]))}: le habrían bastado {n(a["cambian"])} votantes que se pasaran {escape(del_(u["l"]))} {escape(al(s["l"]))}, '
             f'o {n(a["nuevos_sig"])} votos nuevos. {n(a["sin_escano"])} votos a candidaturas, el {pc(a["sin_escano_pct"])} de los válidos, no eligieron a nadie.</p>')

    # Figura 1: los escaños en el orden del reparto y los que se quedaron a las puertas
    orden = a['orden']
    sqs = []
    for i, o in enumerate(orden, 1):
        sqs.append(sq(col[o['l']], 'ult' if i == e else '', f'{i}.º escaño del reparto: {o["l"]} ({o["k"]}.º de su lista), {n(o["q"])} votos por escaño'))
    sqs.append('<span class="vu-sep" aria-hidden="true"></span><span class="vu-et">A las puertas</span>')
    for o in a['puertas']:
        sqs.append(sq(col[o['l']], 'alc', f'{o["l"]}, {o["k"]}.º de su lista: {n(o["q"])} votos por escaño'))
    ley = ''.join(f'<span>{sq(col[x["l"]])}{escape(x["l"])} {x["esc"]}</span>' for x in con)
    ley_p = ''.join(f'<span>{sq(col[l], "alc")}{escape(l)}</span>' for l in dict.fromkeys(o['l'] for o in a['puertas']))
    tabla1 = ''.join(f'<tr><td>{i}.º</td><td>{escape(o["l"])} ({o["k"]}.º)</td><td class="n">{n(o["q"])}</td></tr>' for i, o in enumerate(orden, 1))
    tabla1 += ''.join(f'<tr><td>A las puertas</td><td>{escape(o["l"])} ({o["k"]}.º)</td><td class="n">{n(o["q"])}</td></tr>' for o in a['puertas'])
    h.append(f'<h2>Los {e} {"escaños" if e > 1 else "escaño"}, uno a uno</h2>'
             f'<p>Cada cuadrado es un escaño, en el orden en que los reparte la regla D\'Hondt: primero, el cociente más alto. El último, recuadrado, es el que se lleva el cociente más bajo de los que entran. '
             f'Detrás, con borde de puntos, los tres cocientes siguientes: los que se quedaron a las puertas.</p>'
             f'<figure><div class="vu-fila" role="img" aria-label="Escaños de {escape(nom)} en el orden del reparto con los votos de 2023">{"".join(sqs)}</div>'
             f'<div class="vu-ley">{ley}</div><div class="vu-ley">{ley_p}</div>'
             f'<details><summary>Ver los datos</summary><table><caption>Orden del reparto en {escape(nom)}, con los votos de 2023 y los escaños de 2026</caption>'
             f'<thead><tr><th>Escaño</th><th>Candidatura (puesto en su lista)</th><th>Votos por escaño</th></tr></thead><tbody>{tabla1}</tbody></table></details>'
             f'<figcaption>Fuente: Ministerio del Interior, resultados definitivos de las generales de julio de 2023 con el voto exterior (CERA); escaños de 2026 (Real Decreto 806/2026). Cálculo propio.</figcaption></figure>')

    # Figura 2: seguros, probables y en juego, por candidatura
    filas = []
    for x in a['escanos']:
        if not x['esc'] and not x['alcance']:
            continue
        c = col[x['l']]
        g = {'seguro': [], 'probable': [], 'juego': []}
        for j, cat, pct_ in x['esc']:
            t = f'{x["l"]}, {j}.º escaño: ' + ('aguanta aunque pierda más del 25 % de sus votos' if cat == 'seguro'
                                                 else f'lo perdería si perdiera el {pc(pct_)} de sus votos')
            g[cat].append(sq(c, {'seguro': '', 'probable': 'prob', 'juego': 'jue'}[cat], t))
        for j, pct_ in x['alcance']:
            g['juego'].append(sq(c, 'alc', f'{x["l"]}, {j}.º escaño: lo ganaría con un {pc(pct_)} más de votos'))
        celda = lambda L: (f'<span class="vu-fila">{"".join(L)}</span> ' + str(sum('"sq alc"' not in z for z in L))
                           + (' + 1 al alcance' if any('"sq alc"' in z for z in L) else '')) if L else '0'
        filas.append(f'<tr><th scope="row" style="color:{c}">{escape(x["l"])}<br><span style="color:var(--muted);font-weight:400">{len([1 for _ in x["esc"]])} esc.</span></th>'
                     f'<td class="c">{celda(g["seguro"])}</td><td class="c">{celda(g["probable"])}</td><td class="c">{celda(g["juego"])}</td></tr>')
    juego = [(x['l'], j, pct_) for x in a['escanos'] for j, cat, pct_ in x['esc'] if cat == 'juego']
    alc = [(x['l'], j, pct_) for x in a['escanos'] for j, pct_ in x['alcance']]
    if juego:
        txt_j = ('En juego: ' + '; '.join(f'el {ord_(j)} {del_(l)}, que perdería con un {pc(p_)} menos de votos' for l, j, p_ in juego) + '.')
    else:
        txt_j = f'Ningún escaño de {nom} cambiaba de manos con menos de un 10 % de votos menos para su partido.'
    if alc:
        txt_j += ' Al alcance: ' + '; '.join(f'el {ord_(j)} {del_(l)}, con un {pc(p_)} más' for l, j, p_ in alc) + '.'
    h.append('<h2>Seguros, probables y en juego</h2>'
             f'<p><span class="tipo t-dato">Dato</span>{escape(txt_j)}</p>'
             '<figure><table class="vu"><caption>Escaños de cada candidatura en ' + escape(nom) + ' con los votos de 2023, según cuánto voto podría perder antes de que cambien</caption>'
             '<thead><tr><th>Candidatura</th><th>Seguros</th><th>Probables</th><th>En juego</th></tr></thead><tbody>' + ''.join(filas) + '</tbody></table>'
             f'<div class="vu-ley"><span>{sq("var(--fg)")}Seguro</span><span>{sq("var(--fg)", "prob")}Probable</span><span>{sq("var(--fg)", "jue")}En juego</span><span>{sq("var(--fg)", "alc")}Al alcance</span></div>'
             '<figcaption>Seguro: el escaño aguanta aunque la candidatura pierda el 25 % de sus votos de 2023. Probable: lo perdería con una caída de entre el 10 % y el 25 %. '
             'En juego: lo perdería con menos de un 10 % menos de votos. Al alcance: un escaño más que ganaría con menos de un 10 % más de votos. '
             'Cada cálculo mueve solo los votos de esa candidatura y deja igual los del resto. Fuente: Ministerio del Interior (2023, con CERA); escaños de 2026. Cálculo propio.</figcaption></figure>'
             '<p>Por qué un 10 %: a pocos días de votar, el error típico de las encuestas para un partido grande ronda los tres puntos, una décima parte de su voto. '
             'Es un umbral orientativo, no una probabilidad.</p>')

    # El último escaño
    p_l = [f'el {ord_(o["k"])} {del_(o["l"])} ({n(o["q"])})' for o in a['puertas']]
    p_list = ', '.join(p_l[:-1]) + ' y ' + p_l[-1] if len(p_l) > 1 else p_l[0]
    h.append('<h2>El último escaño</h2>'
             f'<p><span class="tipo t-dato">Dato</span>{escape(frase_ult)}, con {n(u["q"])} votos por escaño. Los siguientes cocientes eran {escape(p_list)}. '
             f'Para quitarle el escaño {escape(al(u["l"]))}, {escape(al(s["l"]))} le habrían bastado {n(a["cambian"])} votantes que cambiaran de papeleta, el {pc(100 * a["cambian"] / a["val"], 2)} de los votos válidos, '
             f'o {n(a["nuevos_sig"])} votos nuevos de gente que no votó.</p>')

    # Votos que no eligieron a nadie
    if sin:
        li = ', '.join(f'{l} ({n(v)})' for l, v in sin[:6])
        h.append('<h2>Los votos que no eligieron a nadie</h2>'
                 f'<p><span class="tipo t-dato">Dato</span>En 2023, {n(a["sin_escano"])} votos de {escape(nom)}, el {pc(a["sin_escano_pct"])} de los válidos, fueron a candidaturas que no sacaron escaño: {escape(li)}'
                 f'{" y otras" if len(sin) > 6 else ""}. Además hubo {n(a["bl"])} votos en blanco, que no eligen a nadie pero cuentan para calcular la barrera del 3 %: '
                 f'con la participación de 2023, unos {n(a["barrera"])} votos.</p>')
    filas = ''.join(
        f'<tr><td>{escape(x["l"])}</td><td class="n">{n(x["v"])}</td><td class="n">{pc(x["pct"])}</td><td class="n">{x["esc"]}</td>'
        f'<td class="n">{n(x["nuevos"]) if x["nuevos"] is not None else "—"}</td></tr>' for x in listas)
    h.append(f'<h2>Todas las candidaturas</h2><figure><div style="overflow-x:auto"><table><caption>Votos de 2023 en {escape(nom)} y escaños con el reparto de 2026</caption>'
             '<thead><tr><th>Candidatura</th><th>Votos</th><th>% válidos</th><th>Escaños</th><th>Votos nuevos para un escaño más</th></tr></thead>'
             f'<tbody>{filas}</tbody></table></div><figcaption>Votos nuevos: los que le harían falta a cada candidatura, sin que cambien los del resto, para sacar un escaño más; '
             'en las que no llegaron al 3 %, incluyen los que necesitaban para pasar la barrera. Fuente: Ministerio del Interior (2023, con CERA). Cálculo propio.</figcaption></figure>')

    h.append('<h2>Qué no dicen estos datos</h2>'
             '<p>Esto no es una previsión del 29N. Es el reparto de 2023 con los escaños de 2026: dice qué escaños estuvieron más ajustados la última vez, no cuáles lo estarán ahora. '
             'Desde entonces han cambiado los votos y algunas candidaturas: el espacio de Sumar, por ejemplo, se presenta dividido en la mayoría de provincias '
             f'(<a href="{raiz}actualidad/coaliciones-quien-va-con-quien-29n/">quién va con quién el 29N</a>). Los votantes no se mueven en bloque de un partido a otro: '
             'las cifras de votantes que cambian de papeleta son el mínimo, el mejor caso para quien aspira. Y desde el 24 de noviembre la ley prohíbe publicar encuestas, '
             'así que aquí no hay ninguna.</p>')
    h.append(faq_html)
    prov_url = raiz + T_['ruta_provincia'](p)
    h.append('<h2>Más datos</h2><ul>'
             f'<li><a href="{prov_url}">Elecciones en {escape(nom)}: cómo votó cada municipio</a></li>'
             f'<li><a href="{raiz}listas-electorales-29n/">Listas electorales del 29N</a></li>'
             f'<li><a href="{raiz}actualidad/provincias-en-el-filo-29n/">Las provincias que deciden el 29N: el último escaño de las 52</a></li>'
             f'<li><a href="{raiz}actualidad/votos-sin-escano-29n/">Los votos que no eligieron a nadie en 2023</a></li>'
             f'<li><a href="{raiz}actualidad/precio-del-escano-29n/">Cuántos votos cuesta un diputado en cada provincia</a></li>'
             f'<li><a href="{raiz}elecciones/voto-util-29n/">Voto útil en las 52 circunscripciones</a></li></ul>')
    h.append('<h2>Método y fuentes</h2><dl class="ficha"><dt>Datos</dt><dd>Resultados definitivos de las generales de julio de 2023 por circunscripción, con el voto exterior (CERA), '
             'sumados mesa a mesa desde los microdatos del Ministerio del Interior. Escaños de 2026: Real Decreto 806/2026 (Madrid, 38; Cádiz, 8; el resto, como en 2023).</dd>'
             '<dt>Cómo se calcula</dt><dd>Regla D\'Hondt con la barrera del 3 % de los votos válidos (candidaturas más blancos), artículo 163 de la LOREG; '
             'si dos cocientes empatan, el escaño va a la candidatura con más votos. Los votantes que cambian de papeleta, los votos nuevos y los que puede perder cada candidatura '
             'se calculan repartiendo de nuevo los escaños, no con fórmulas aproximadas. Código: src/voto_util.py.</dd>'
             f'<dt>Autoría</dt><dd><a href="{raiz}sobre-mi.html">{T_["esquema"].FIRMA}</a>. Publicado el {T_["fecha"](PUBLICADA)}. '
             f'<a href="{raiz}atlas/politica-editorial/">Política editorial</a> · <a href="{raiz}atlas/correcciones/">Correcciones</a></dd></dl>')
    h.append(T_['PIE'])
    return r, ''.join(h)


# Cartograma: cada circunscripción, un bloque de cuadrados en una rejilla que imita el mapa (columna, fila)
REJILLA = {'15': (0, 0), '27': (1, 0), '33': (2, 0), '39': (3, 0), '48': (4, 0), '20': (5, 0),
           '36': (0, 1), '32': (1, 1), '24': (2, 1), '34': (3, 1), '09': (4, 1), '01': (5, 1), '31': (6, 1), '22': (7, 1), '25': (8, 1), '08': (9, 1), '17': (10, 1),
           '49': (1, 2), '47': (2, 2), '40': (3, 2), '42': (4, 2), '26': (5, 2), '50': (6, 2), '43': (8, 2),
           '37': (1, 3), '05': (2, 3), '28': (3, 3), '19': (4, 3), '16': (5, 3), '44': (6, 3), '12': (7, 3), '07': (9, 3),
           '10': (1, 4), '45': (2, 4), '13': (3, 4), '02': (4, 4), '46': (6, 4),
           '06': (1, 5), '14': (2, 5), '23': (3, 5), '30': (5, 5), '03': (6, 5),
           '21': (1, 6), '41': (2, 6), '18': (4, 6), '04': (5, 6),
           '11': (2, 7), '29': (3, 7),
           '38': (0, 8), '35': (1, 8), '51': (3, 8), '52': (5, 8)}
ABREV = {'01': 'VI', '02': 'AB', '03': 'A', '04': 'AL', '05': 'AV', '06': 'BA', '07': 'IB', '08': 'B', '09': 'BU', '10': 'CC', '11': 'CA', '12': 'CS', '13': 'CR',
         '14': 'CO', '15': 'C', '16': 'CU', '17': 'GI', '18': 'GR', '19': 'GU', '20': 'SS', '21': 'H', '22': 'HU', '23': 'J', '24': 'LE', '25': 'L', '26': 'LO',
         '27': 'LU', '28': 'M', '29': 'MA', '30': 'MU', '31': 'NA', '32': 'OU', '33': 'O', '34': 'P', '35': 'GC', '36': 'PO', '37': 'SA', '38': 'TF', '39': 'S',
         '40': 'SG', '41': 'SE', '42': 'SO', '43': 'T', '44': 'TE', '45': 'TO', '46': 'V', '47': 'VA', '48': 'BI', '49': 'ZA', '50': 'Z', '51': 'CE', '52': 'ML'}


def cartograma(A, COLOR, ruta_provincia, raiz):
    """SVG: un bloque por circunscripción; dentro, un cuadrado por escaño (lleno: seguro; claro: probable; rayado: en juego), por candidatura."""
    cel, pad = 36, 2
    W, H = 11 * cel, 9 * cel + 4
    defs, usados, out = [], set(), []
    for p, (cx, cy) in REJILLA.items():
        a = A[p]
        cats = []
        for x in sorted(a['escanos'], key=lambda x: -sum(1 for _ in x['esc'])):
            for j, cat, _ in sorted(x['esc']):
                cats.append((color(x['f'], COLOR), cat, x['l'], j))
        e = len(cats)
        k = 1
        while k * k < e:
            k += 1
        s = min(9.0, (cel - 2 * pad - 9) / k)
        x0, y0 = cx * cel + pad, cy * cel + pad
        out.append(f'<a href="{raiz}{ruta(p, ruta_provincia)}"><title>{escape(a["n"])}: {e} {"escaño" if e == 1 else "escaños"}; ver el voto útil</title>'
                   f'<rect x="{x0}" y="{y0}" width="{cel - 2 * pad}" height="{cel - 2 * pad}" rx="3" fill="var(--bg)" stroke="var(--rule)"/>'
                   f'<text x="{x0 + (cel - 2 * pad) / 2}" y="{y0 + 7}" text-anchor="middle" font-size="6.5" fill="var(--muted)">{ABREV[p]}</text>')
        for i, (c, cat, l, j) in enumerate(cats):
            xx = x0 + ((cel - 2 * pad) - k * s) / 2 + (i % k) * s
            yy = y0 + 9 + (i // k) * s
            if cat == 'juego':
                pid = 'vu' + ''.join(ch for ch in c if ch.isalnum())
                if pid not in usados:
                    usados.add(pid)
                    defs.append(f'<pattern id="{pid}" width="3" height="3" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="1.5" height="3" fill="{c}"/></pattern>')
                out.append(f'<rect x="{xx + .4:.1f}" y="{yy + .4:.1f}" width="{s - .8:.1f}" height="{s - .8:.1f}" fill="url(#{pid})" stroke="{c}" stroke-width=".7"/>')
            else:
                out.append(f'<rect x="{xx + .4:.1f}" y="{yy + .4:.1f}" width="{s - .8:.1f}" height="{s - .8:.1f}" fill="{c}"{" fill-opacity=\".5\"" if cat == "probable" else ""}/>')
        out.append('</a>')
    return (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Cartograma de las 52 circunscripciones: un cuadrado por escaño, seguro, probable o en juego, con los votos de 2023" '
            f'style="width:100%;height:auto;font-family:var(--sans)"><defs>{"".join(defs)}</defs>{"".join(out)}</svg>')


def indice(A, T_):
    COLOR = T_['COLOR']
    r = 'elecciones/voto-util-29n/'
    raiz = '../../'
    juego = sorted(((pct_, a['n'], x['l'], j, p) for p, a in A.items() for x in a['escanos'] for j, cat, pct_ in x['esc'] if cat == 'juego'))
    n_j = len(juego)
    titulo = f'Voto útil el 29N en cada provincia: {n_j} escaños de 2023 cambiaban con menos de un 10 % de votos'
    desc = (f'Con los votos de 2023 y los escaños de 2026, {n_j} de los 350 escaños se perderían si su partido perdiera menos del 10 % de sus votos. '
            'Elige tu provincia: quién se llevó cada escaño, cuáles estaban en juego y qué votos no eligieron a nadie.')
    ld = T_['ld_pagina'](titulo, desc, r, {'@type': 'Country', 'name': 'España'},
                         [{'@type': 'WebPage', 'name': f'Voto útil en {a["n"]}', 'url': T_['BASE'] + ruta(p, T_['ruta_provincia'])} for p, a in A.items()])
    ld['@type'] = 'CollectionPage'
    ld['datePublished'] = PUBLICADA
    ld['dateModified'] = T_['LASTMOD'][r] = ACTUALIZADA
    h = [T_['cabeza'](titulo, desc, r, ld, 2, 'Voto útil')]
    h.append(f'<style>{CSS}.vu-sel{{font:inherit;font-family:var(--sans);font-size:1rem;padding:.4rem .6rem;border:1px solid var(--rule);border-radius:6px;background:var(--bg);color:var(--fg);max-width:100%}}</style>')
    h.append(T_['migas_html']([(raiz, 'Inicio'), ('../', 'Elecciones')]))
    h.append(f'<p class="kicker">Elecciones generales · 29 de noviembre de 2026</p><h1 data-miga="Voto útil">Voto útil el 29N: qué escaños estaban en juego en cada provincia</h1>')
    h.append('<p class="subtitulo">Un cuadrado por escaño, con los votos de 2023 y los escaños de 2026: cuáles estaban seguros, cuáles en juego y quién se quedó a las puertas</p>')
    h.append(f'<p class="firma">Por <a href="{raiz}sobre-mi.html">{T_["esquema"].FIRMA}</a> · Actualizado el <time datetime="{ACTUALIZADA}">{T_["fecha"](ACTUALIZADA)}</time></p>')
    opts = ''.join(f'<option value="{raiz}{ruta(p, T_["ruta_provincia"])}">{escape(a["n"])} ({a["e"]} esc.)</option>' for p, a in sorted(A.items(), key=lambda t: T_['clave'](t[1]['n'])))
    h.append('<p><label for="vu-prov" style="font-family:var(--sans)">Elige tu provincia</label><br>'
             f'<select id="vu-prov" class="vu-sel" onchange="if(this.value)location.href=this.value"><option value="">Provincia…</option>{opts}</select></p>')
    top = juego[:8]
    h.append(f'<p class="resumen"><span class="tipo t-dato">Dato</span>Con los votos de las generales de 2023 y el reparto de 2026, {n_j} de los 350 escaños se habrían perdido '
             f'si su partido hubiera perdido menos del 10 % de sus votos. Los más ajustados: '
             + escape('; '.join(f'el {ord_(j)} {del_(l)} en {nom} ({pc(p_)})' for p_, nom, l, j, _ in top)) + '.</p>')
    h.append('<figure>' + cartograma(A, COLOR, T_['ruta_provincia'], raiz)
             + f'<div class="vu-ley"><span>{sq("var(--fg)")}Seguro</span><span>{sq("var(--fg)", "prob")}Probable</span><span>{sq("var(--fg)", "jue")}En juego</span></div>'
             '<figcaption>Cada bloque es una circunscripción y cada cuadrado, un escaño, con el color de la candidatura que lo ganaría con los votos de 2023. '
             'Seguro: aguanta aunque su candidatura pierda el 25 % de los votos. Probable: lo perdería con una caída de entre el 10 % y el 25 %. En juego: con menos de un 10 %. '
             'Pulsa una provincia para ver el detalle. Fuente: Ministerio del Interior (2023, con CERA); escaños de 2026 (Real Decreto 806/2026). Cálculo propio.</figcaption></figure>')
    por_partido = {}
    for p_, nom, l, j, p in juego:
        por_partido[l] = por_partido.get(l, 0) + 1
    h.append('<h2>Quién tenía más escaños en juego</h2><p><span class="tipo t-dato">Dato</span>'
             + escape('; '.join(f'{l}, {k}' for l, k in sorted(por_partido.items(), key=lambda t: -t[1]))) + '. El resto de los 350 estaban seguros o eran probables.</p>')
    filas = ''.join(
        f'<tr><td><a href="{raiz}{ruta(p, T_["ruta_provincia"])}">{escape(a["n"])}</a></td><td class="n">{a["e"]}</td>'
        f'<td>{escape(a["ultimo"]["l"])} ({a["ultimo"]["k"]}.º)</td><td>{escape(a["siguiente"]["l"])} ({a["siguiente"]["k"]}.º)</td>'
        f'<td class="n">{n(a["cambian"])}</td><td class="n">{pc(a["sin_escano_pct"])}</td></tr>'
        for p, a in sorted(A.items(), key=lambda t: t[1]['cambian']))
    h.append('<h2>Las 52 circunscripciones</h2><figure><div style="overflow-x:auto"><table><caption>Último escaño, quién se quedó a las puertas y votos sin escaño, con los votos de 2023 y los escaños de 2026</caption>'
             '<thead><tr><th>Provincia</th><th>Escaños</th><th>Último escaño</th><th>A las puertas</th><th>Votantes que bastaban</th><th>Votos sin escaño</th></tr></thead>'
             f'<tbody>{filas}</tbody></table></div><figcaption>Votantes que bastaban: los que tendrían que pasar de la candidatura del último escaño a la que se quedó a las puertas. '
             'Votos sin escaño: los de candidaturas que no sacaron ninguno, sobre los válidos. Fuente: Ministerio del Interior (2023, con CERA). Cálculo propio.</figcaption></figure>')
    h.append('<h2>Qué no dicen estos datos</h2><p>No es una previsión del 29N: es el reparto de 2023 con los escaños de 2026. Las candidaturas han cambiado y los votantes no se mueven en bloque. '
             'Desde el 24 de noviembre la ley prohíbe publicar encuestas, así que aquí no hay ninguna. Más contexto en '
             f'<a href="{raiz}actualidad/provincias-en-el-filo-29n/">las provincias que deciden el 29N</a> y en <a href="{raiz}actualidad/votos-sin-escano-29n/">los votos que no eligieron a nadie</a>.</p>')
    h.append(T_['PIE'])
    return r, ''.join(h)
