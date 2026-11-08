"""Controles de calidad que «Verificar piezas» pasa además de las cifras declaradas (propuesta del repaso diario, 7-11-2026).

Salen de los fallos que el repaso diario encontró en piezas ya fusionadas:

1. Redondeo. La cifra buena es la que sale del dato sin redondear: una diferencia se calcula restando los datos
   brutos, nunca restando las cifras ya redondeadas que se muestran. Por eso la resta de las cifras mostradas
   puede separarse una décima de la diferencia publicada sin que haya error:
   - «del 62,9 % al 77,0 %, 14,0 puntos más» (76,992 − 62,946 = 14,046): correcto aunque 77,0 − 62,9 dé 14,1.
   - Si la pieza declara la diferencia en «cifras», la Action ya la recalcula contra el dato y aquí no se mira.
   - Si no la declara, una diferencia a ±0,1 de la resta de las cifras que se ven (en la misma frase, o en la
     fila de una tabla que la frase nombra: «nov. 2019» ↔ «noviembre de 2019») da aviso, nunca error.
   - «Nevada, con el 88 %» en el texto y 87,8 % en la fila «Nevada» de una tabla (aviso).
2. Tablas.
   - Columna «Diferencia»: la resta de las dos columnas de su izquierda (aviso a una décima, error si se separa más).
   - Fila o columna «Total» (o «Suma», «Comunitat», «España»...): tiene que ser la suma de las demás (error).
   - Filas de recuentos que suman distinto que la mayoría (aviso: puede estar explicado en una nota).
   - «0,0» en una tabla que marca con «–» lo que no tiene dato (aviso).
3. Navegador (src/verificar_navegador.mjs): cada pieza se abre a 390 px; un error de JavaScript o el scroll
   horizontal es error.

Una frase que dispara el control por un motivo justificado se declara en la declaración de la pieza
(`actualidad/verificacion/<slug>.json`), en «ignorar_calidad»: [{"texto": "…", "motivo": "…"}].
"""
import html, json, os, re, shutil, subprocess, unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MESES_ABR = {'ene': 'enero', 'feb': 'febrero', 'mar': 'marzo', 'abr': 'abril', 'may': 'mayo', 'jun': 'junio',
             'jul': 'julio', 'ago': 'agosto', 'sep': 'septiembre', 'sept': 'septiembre', 'oct': 'octubre',
             'nov': 'noviembre', 'dic': 'diciembre'}
TOTALES = r'^(total|totales|suma|en total|todos|todas|españa|comunitat|comunidad|conjunto|cataluña|catalunya|andalucía|euskadi|país vasco)\b'


def _txt(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace(' ', ' ').replace(' ', ' ')
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s)).strip()


def _num(s):
    """«32,4 %» -> (32.4, 1); «+1.974» -> (1974.0, 0); «−1.911» -> (-1911.0, 0); otra cosa -> None."""
    s = s.strip().replace('−', '-').replace('–', '-')
    m = re.fullmatch(r'([+-]?)\s*(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?\s*(?:%|esc\.?|puntos|p\.|votos|€)?', s)
    if not m:
        return None
    entero = m.group(2).replace('.', '')
    dec = m.group(3) or ''
    v = float(entero + ('.' + dec if dec else ''))
    return (-v if m.group(1) == '-' else v), len(dec)


def _fmt(v, dec):
    return f'{v:,.{dec}f}'.replace(',', ' ').replace('.', ',').replace(' ', '.')


def _r(v, dec):
    """Redondeo como en el texto (mitad hacia arriba), sin los errores de coma flotante de round()."""
    f = 10 ** dec
    return (int(abs(v) * f + 0.5 + 1e-9) / f) * (1 if v >= 0 else -1)


def tablas(main):
    """[{'cab': [..], 'filas': [[..], ..]}] de las <table> de la pieza, con el texto de cada celda."""
    out = []
    for t in re.findall(r'<table\b.*?</table>', main, re.S):
        filas = []
        cab = []
        for tr in re.findall(r'<tr\b.*?</tr>', t, re.S):
            celdas = [_txt(c) for c in re.findall(r'<t[hd]\b[^>]*>(.*?)</t[hd]>', tr, re.S)]
            if not cab and '<th' in tr and '<td' not in tr:
                cab = celdas
            else:
                filas.append(celdas)
        if filas:
            out.append({'cab': cab, 'filas': filas})
    return out


def _ignorada(frase, decl):
    for e in decl.get('ignorar_calidad', []):
        f = re.sub(r'\s+', ' ', e.get('texto', '')).strip()
        if f and f in frase:
            return True
    return False


def frases(texto):
    return [f.strip() for f in re.split(r'(?<=[.;:])\s+(?=[A-ZÁÉÍÓÚÑ«¿(])', texto) if f.strip()]


PCT = r'(?<![\d,.])(\d{1,3}(?:,\d+)?)\s?%'
PUNTOS = r'(?<![\d,.])(\d{1,3}(?:,\d+)?)\s+puntos?\b'


def _etiqueta_en_frase(etq, frase):
    """¿La etiqueta de una fila («nov. 2019», «2016», «Nevada») está nombrada en la frase?"""
    e = etq.lower().strip()
    if not e:
        return False
    f = frase.lower()
    m = re.fullmatch(r'([a-zé]{3,4})\.?\s+(\d{4})', e)
    if m and m.group(1) in MESES_ABR:
        return bool(re.search(rf'{MESES_ABR[m.group(1)]}(?:\s+de)?\s+{m.group(2)}', f)) or e in f
    if re.fullmatch(r'\d{4}', e):
        # un año solo cuenta si no va con un mes que lo convierta en otra fila (abril de 2019 / noviembre de 2019)
        return bool(re.search(rf'(?<![\w-]){e}(?![\w-])', f))
    return bool(re.search(rf'(?<!\w){re.escape(e)}(?!\w)', f))


def _declarada(txt, frase, decl):
    """La cifra está en «cifras» de la declaración: la Action ya la recalcula desde el dato sin redondear."""
    f = _txt(frase).lower()
    for e in decl.get('cifras', []):
        t = _txt(e.get('texto', '')).lower()
        c = str(e.get('cifra', '')).strip()
        if t and t in f and (c == txt or (not c and txt in t)):
            return True
    return False


AVISO_BRUTO = ('Si sale del dato sin redondear, es correcta (la resta de cifras ya redondeadas puede moverse ±0,1): '
               'declárala en «cifras» con su cálculo para que la Action la compruebe contra el dato.')


def comprobar_redondeo(inf, textos, main, decl):
    """textos: [(dónde, texto)] del titular, la entradilla y los párrafos.

    La cifra correcta es la que sale del dato sin redondear. Si la pieza la declara en «cifras», la Action ya la
    comprueba contra el dato y aquí no se mira. Si no, solo tenemos las cifras que se ven: una diferencia que se
    separa ±0,1 de su resta puede ser correcta, así que da aviso (el editor lo explica), nunca error."""
    tbs = tablas(main)
    for donde, t in textos:
        for fr in frases(t):
            if _ignorada(fr, decl):
                continue
            pts = [(m.group(1), _num(m.group(1))) for m in re.finditer(PUNTOS, fr)]
            pcs = [_num(m.group(1)) for m in re.finditer(PCT, fr)]
            for txt, (n, dec) in pts:
                if _declarada(txt, fr, decl):
                    continue
                tol = 0.5 * 10 ** -dec + 0.05   # lo que se puede mover una resta por el redondeo de sus dos cifras
                # a) dos porcentajes en la misma frase y una diferencia en puntos
                if len(pcs) == 2 and pcs[0][1] == pcs[1][1] and pcs[0][1] >= dec:   # «en torno al 32 %» no da décimas
                    d = abs(pcs[0][0] - pcs[1][0])
                    if _r(d, dec) == n:
                        continue
                    if abs(d - n) <= tol:
                        inf.aviso('Redondeo: la diferencia no es la resta de las cifras que se ven',
                                  f'«{txt} puntos», y {_fmt(pcs[0][0], pcs[0][1])} − {_fmt(pcs[1][0], pcs[1][1])} = '
                                  f'{_fmt(_r(d, dec), dec)} ({donde}): «{fr[:220]}». {AVISO_BRUTO}')
                        continue
                # b) un porcentaje en la frase y el otro en una tabla: misma columna, fila nombrada en la frase
                for a, da in pcs:
                    if da < dec:
                        continue
                    for tb in tbs:
                        for j in range(1, max(len(f) for f in tb['filas'])):
                            col = [(f[0], _num(f[j])) for f in tb['filas'] if len(f) > j]
                            if not any(v and v[1] == da and v[0] == a for _, v in col):
                                continue
                            for etq, v in col:
                                if not v or v[1] != da or v[0] == a or not _etiqueta_en_frase(etq, fr):
                                    continue
                                d = abs(a - v[0])
                                if abs(d - n) <= tol and _r(d, dec) != n:
                                    inf.aviso('Redondeo: la diferencia no es la resta de la tabla de la pieza',
                                              f'«{txt} puntos», y {_fmt(a, da)} − {_fmt(v[0], v[1])} ({etq}, en la tabla) = '
                                              f'{_fmt(_r(d, dec), dec)} ({donde}): «{fr[:220]}». {AVISO_BRUTO}')
            # c) la misma cifra con distinto redondeo en el texto y en la fila de una tabla con ese nombre
            todos = re.findall(PCT, fr)
            for m in re.finditer(PCT, fr):
                x, dx = _num(m.group(1))
                otros = {o for o in todos if o != m.group(1)}
                for tb in tbs:
                    for f in tb['filas']:
                        if not f or not _etiqueta_en_frase(f[0], fr) or len(f[0]) < 4:
                            continue
                        # si la frase tiene más porcentajes, la fila tiene que ser la misma carrera: comparte alguno
                        if otros and not otros & {c.replace('%', '').strip() for c in f[1:]}:
                            continue
                        for c in f[1:]:
                            v = _num(c)
                            if v and c.strip().endswith('%') and v[1] > dx and _r(v[0], dx) == x and v[0] != x:
                                if True:
                                    inf.aviso('La misma cifra con distinto redondeo en el texto y en la tabla',
                                              f'«{m.group(0)}» en el texto y «{c}» en la fila «{f[0]}» ({donde}). Mejor la misma cifra en los dos.')


def comprobar_tablas(inf, main, decl):
    for k, tb in enumerate(tablas(main), 1):
        cab, filas = tb['cab'], tb['filas']
        nombre = f'tabla {k}' + (f' («{" · ".join(cab[:3])}…»)' if cab else '')
        if any(_ignorada(nombre, decl) or _ignorada(' '.join(f), decl) for f in filas[:1]):
            continue
        ancho = max(len(f) for f in filas)
        # columna «Diferencia» = las dos de su izquierda
        for j, h in enumerate(cab):
            if j >= 3 and re.match(r'(diferencia|dif\.|cambio|variación)', h.lower()) and 'punto' not in h.lower() and '%' not in h:
                pares = []
                for f in filas:
                    if len(f) > j:
                        a, b, d = _num(f[j - 2]), _num(f[j - 1]), _num(f[j])
                        if a and b and d:
                            pares.append((f, a[0] - b[0], d[0], d[1]))
                buenos = [p for p in pares if _r(p[1], p[3]) == p[2]]
                if pares and len(buenos) >= len(pares) / 2:
                    for f, calc, d, dec in pares:
                        if _r(calc, dec) != d:
                            cerca = abs(_r(calc, dec) - d) <= 10 ** -dec + 1e-9
                            (inf.aviso if cerca else inf.error)(
                                'Tabla: la diferencia no es la resta de sus columnas',
                                f'{nombre}, fila «{f[0]}»: {f[j - 2]} − {f[j - 1]} = {_fmt(_r(calc, dec), dec)}, y la tabla pone {f[j]}'
                                + (f'. {AVISO_BRUTO}' if cerca else ''))
        # fila de total
        for i, f in enumerate(filas):
            if re.match(TOTALES, f[0].lower()) and i > 1:
                for j in range(1, len(f)):
                    t = _num(f[j])
                    vals = [_num(g[j]) for g in filas if g is not f and len(g) > j and not re.match(TOTALES, g[0].lower())]
                    if not t or not vals or any(v is None for v in vals) or '%' in f[j]:
                        continue
                    s = sum(v[0] for v in vals)
                    tol = 0.5 * 10 ** -t[1] * len(vals) + 1e-9
                    if abs(s - t[0]) > tol:
                        inf.error('Tabla: el total no es la suma de las filas',
                                  f'{nombre}, columna «{cab[j] if j < len(cab) else j}»: la suma da {_fmt(s, t[1])} y la fila «{f[0]}» pone {f[j]}')
        # columna de total
        for j, h in enumerate(cab):
            if j >= 3 and re.match(TOTALES, h.lower()):
                for f in filas:
                    if len(f) <= j:
                        continue
                    t, vals = _num(f[j]), [_num(c) for c in f[1:j]]
                    if t and vals and all(vals) and '%' not in f[j]:
                        s = sum(v[0] for v in vals)
                        if abs(s - t[0]) > 0.5 * 10 ** -t[1] * len(vals) + 1e-9:
                            inf.error('Tabla: el total de la fila no es la suma de sus columnas',
                                      f'{nombre}, fila «{f[0]}»: la suma da {_fmt(s, t[1])} y la columna «{h}» pone {f[j]}')
        # filas de recuentos (enteros, sin %) que suman distinto que la mayoría
        if ancho >= 4 and len(filas) >= 5:
            sumas = []
            for f in filas:
                vals = [_num(c) for c in f[1:]]
                if vals and all(v and v[1] == 0 for v in vals) and not any('%' in c or '€' in c for c in f[1:]) \
                        and all(0 <= v[0] < 1000 for v in vals):
                    sumas.append((f[0], int(sum(v[0] for v in vals))))
            if len(sumas) >= 5 and len(sumas) >= 0.8 * len(filas):
                moda = max(set(s for _, s in sumas), key=lambda s: sum(1 for _, x in sumas if x == s))
                if sum(1 for _, s in sumas if s == moda) >= 0.6 * len(sumas):
                    raras = [(e, s) for e, s in sumas if s != moda]
                    if raras:
                        inf.aviso('Tabla: filas que suman distinto que las demás',
                                  f'{nombre}: casi todas suman {moda}, pero ' + ', '.join(f'«{e}» suma {s}' for e, s in raras[:6]) +
                                  '. Si una nota lo explica, está bien; si no, falta una fila o un dato.')
        # «0,0» en una tabla que usa «–» para lo que no tiene dato
        celdas = [c for f in filas for c in f[1:]]
        if any(c.strip() in ('–', '—', '-') for c in celdas):
            ceros = [(f[0], cab[j + 1] if j + 1 < len(cab) else '') for f in filas for j, c in enumerate(f[1:]) if re.fullmatch(r'0(,0+)?\s*%?', c.strip())]
            if ceros:
                inf.aviso('Tabla: «0,0» donde quizá no hay dato',
                          f'{nombre} marca con «–» lo que no tiene dato, pero pone 0 en ' +
                          ', '.join(f'«{e}»{(" · " + h) if h else ""}' for e, h in ceros[:5]) + '. ¿Es un cero de verdad?')


def comprobar_navegador(informes, rutas, ancho=390):
    """Abre cada pieza con src/verificar_navegador.mjs. Sin Node o sin Playwright, aviso (no bloquea)."""
    script = os.path.join(RAIZ, 'src', 'verificar_navegador.mjs')
    if not shutil.which('node'):
        for inf in informes.values():
            inf.aviso('Navegador', 'no hay Node: no se han abierto las piezas en el navegador')
        return
    try:
        r = subprocess.run(['node', script, str(ancho)] + [rutas[s] for s in informes if s in rutas],
                           capture_output=True, text=True, timeout=600, cwd=RAIZ)
        res = json.loads(r.stdout.strip().splitlines()[-1]) if r.stdout.strip() else None
    except Exception as e:
        res, r = None, None
        err = str(e)
    if not isinstance(res, dict) or 'piezas' not in res:
        motivo = ((r.stderr.strip().splitlines() or [''])[0][:300] if r is not None else err) or 'sin salida'
        for inf in informes.values():
            inf.aviso('Navegador', f'no se pudo abrir el navegador: {motivo}')
        return
    por_ruta = {v: k for k, v in rutas.items()}
    for ruta, d in res['piezas'].items():
        inf = informes.get(por_ruta.get(ruta))
        if not inf:
            continue
        for e in d.get('errores', []):
            inf.error('Error de JavaScript en el navegador', e)
        if d.get('scroll', 0) > 0:
            inf.error(f'Scroll horizontal a {ancho} px', f'la página mide {d["ancho"]} px, {d["scroll"]} más que la pantalla')
        if d.get('fallo'):
            inf.error('La página no carga en el navegador', d['fallo'])
