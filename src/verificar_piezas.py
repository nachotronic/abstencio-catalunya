"""Comprobación automática de las piezas de Actualidad e Internacional antes de fusionar un PR.

Regla de Nacho (3-11-2026, tras los nueve fallos de la previa de EE. UU., PR #416): ninguna pieza se fusiona
sin (a) la revisión de un hilo editor separado y (b) esta comprobación automática. La GitHub Action
`.github/workflows/verificar-piezas.yml` la ejecuta en cada PR y, si algo falla, el PR queda en rojo.

Qué comprueba en cada pieza que el PR crea o cambia:

1. Cifras. Cada número de un párrafo nuevo o cambiado (párrafos con data-tipo, titular, entradilla,
   intertítulos y pies de gráfico) tiene que estar declarado en `actualidad/verificacion/<slug>.json`:
   - «cifras»: la frase, la cifra y el cálculo que la saca de los datos de la pieza (los `const` del
     <script>, que son los que dibujan el mapa y los gráficos) o de un CSV/JSON del repositorio.
     El cálculo se ejecuta y tiene que dar la cifra del texto, con el redondeo del texto.
   - «externas»: la frase y la fuente (un enlace que esté en la pieza) de una cifra que no sale de
     nuestros datos (encuestas, agencias, informes). No se puede recalcular: el editor la revisa.
   - «ignorar»: la frase y el motivo (horas, citas literales, «dos años después»...).
   Cada frase declarada tiene que seguir apareciendo en la pieza: si el texto cambia, hay que revisar.
   Además, cada cifra del titular y de la entradilla tiene que aparecer en el cuerpo de la pieza.
2. Enlaces. Los internos tienen que existir en el repositorio; los externos, responder (un 404, 410 o
   un dominio que no existe es error; un 403 o un 5xx de una web que bloquea robots, aviso).
3. Imágenes. Toda <img>, la foto de cabecera, la imagen para compartir (img/compartir/actualidad-<slug>.jpg)
   y la de Open Graph existen, no están vacías y son imágenes de verdad.
4. Internacional. Las piezas de la serie «internacional» no pueden llevar datos españoles: partidos,
   comunidades, fuentes (Interior, INE), enlaces a páginas de municipios o de las generales. Una mención
   justificada se declara en «permitir_espana» con su motivo.
5. Actualización. Si una pieza ya publicada cambia de texto, su `actualizado` tiene que cambiar.

Uso, desde la raíz:
    python3 src/verificar_piezas.py                      # piezas cambiadas respecto a origin/main
    python3 src/verificar_piezas.py --slug <slug> ...    # piezas concretas (todas sus cifras)
    python3 src/verificar_piezas.py --plantilla <slug>   # escribe el esqueleto de la declaración
    --sin-red  no comprueba los enlaces externos (para trabajar sin conexión)
"""
import argparse, concurrent.futures, html, importlib.util, json, os, re, subprocess, sys, unicodedata
import urllib.error, urllib.parse, urllib.request

sys.dont_write_bytecode = True   # no ensuciar los __pycache__ del repositorio al importar construir.py

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACT = os.path.join(RAIZ, 'actualidad')
VERIF = os.path.join(ACT, 'verificacion')
BASE_URL = 'https://mapaelectoral.es'


# ---------------------------------------------------------------- piezas

def cargar_construir(codigo=None):
    """PIEZAS de actualidad/src/construir.py (el de la rama o, con codigo, el de main)."""
    ruta = os.path.join(ACT, 'src', 'construir.py')
    sys.path.insert(0, os.path.join(ACT, 'src'))
    if codigo is None:
        spec = importlib.util.spec_from_file_location('construir_rama', ruta)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {p['slug']: p for p in mod.PIEZAS}
    ns = {'__file__': ruta, '__name__': 'construir_base'}
    try:
        exec(compile(codigo, ruta, 'exec'), ns)
    except Exception as e:   # main antiguo roto o distinto: se compara sin él
        print('Aviso: no se pudo cargar construir.py de la base:', e)
        return {}
    return {p['slug']: p for p in ns.get('PIEZAS', [])}


def git(*args):
    r = subprocess.run(['git', *args], cwd=RAIZ, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def slugs_cambiados(base, piezas):
    nombres = (git('diff', '--name-only', f'{base}...HEAD') or '').split()
    slugs = set()
    for n in nombres:
        m = (re.match(r'actualidad/src/([^/]+)\.html$', n) or re.match(r'actualidad/([^/]+)/index\.html$', n)
             or re.match(r'actualidad/verificacion/([^/]+)\.json$', n) or re.match(r'img/compartir/actualidad-([^/]+)\.jpg$', n)
             or re.match(r'img/actualidad/fotos/([^/]+)\.jpg$', n))
        if m and m.group(1) in piezas:
            slugs.add(m.group(1))
    # líneas de construir.py cambiadas: la pieza es la del dict que las contiene
    diff = git('diff', '-U0', f'{base}...HEAD', '--', 'actualidad/src/construir.py') or ''
    lineas = open(os.path.join(ACT, 'src', 'construir.py'), encoding='utf-8').read().split('\n')
    for a, b in re.findall(r'^@@ -\S+ \+(\d+)(?:,(\d+))? @@', diff, re.M):
        ini, n = int(a), int(b) if b != '' else 1
        for ln in range(ini, ini + max(n, 1)):
            for k in range(min(ln, len(lineas)) - 1, max(ln - 60, 0) - 1, -1):
                m = re.search(r"\bslug='([^']+)'", lineas[k])
                if m:
                    if m.group(1) in piezas:
                        slugs.add(m.group(1))
                    break
                if re.match(r'\s*dict\($', lineas[k]) or lineas[k].startswith(('PIEZAS', 'def ', ']')):
                    break
    return sorted(slugs)


# ---------------------------------------------------------------- texto y números

def limpio(s):
    s = re.sub(r'<(script|style)\b.*?</\1>', ' ', s, flags=re.S)
    s = re.sub(r'</?(?:a|b|i|em|strong|span|abbr|small|sup|sub|mark|q|cite)\b[^>]*>', '', s)   # en línea: sin espacio
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s).replace(' ', ' ').replace(' ', ' ')
    return re.sub(r'\s+', ' ', s).strip()


def norm(s):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', s.replace(' ', ' ').replace(' ', ' '))).strip()


def bloques(main):
    """Trozos de texto que cuentan: párrafos con data-tipo, intertítulos y pies de gráfico (antes de «Método y fuentes»)."""
    main = re.split(r'<h2>(?:Método y fuentes|Mètode i fonts)</h2>', main)[0]
    main = re.sub(r'<span class="tipo[^"]*">.*?</span>', '', main)   # la etiqueta «Dato», «Contexto»...
    out = []
    for m in re.finditer(r'<p\b[^>]*data-tipo="([a-z]+)"[^>]*>(.*?)</p>', main, re.S):
        out.append((m.group(1), limpio(m.group(2))))
    for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', main, re.S):
        t = limpio(m.group(1))
        if t not in ('Método y fuentes', 'Sigue leyendo', 'Mètode i fonts', 'Continua llegint'):
            out.append(('intertítulo', t))
    for m in re.finditer(r'<figcaption[^>]*>(.*?)</figcaption>', main, re.S):
        sin_fuente = re.sub(r'<(div|p|span) class="src".*?</\1>', ' ', m.group(1), flags=re.S)
        out.append(('pie', limpio(sin_fuente)))
    return out


PALABRAS = {'tres': 3, 'cuatro': 4, 'cinco': 5, 'seis': 6, 'siete': 7, 'ocho': 8, 'nueve': 9, 'diez': 10,
            'once': 11, 'doce': 12, 'trece': 13, 'catorce': 14, 'quince': 15, 'dieciséis': 16, 'diecisiete': 17,
            'dieciocho': 18, 'diecinueve': 19, 'veinte': 20, 'treinta': 30, 'cuarenta': 40, 'cincuenta': 50,
            'sesenta': 60, 'setenta': 70, 'ochenta': 80, 'noventa': 90}
MESES = 'enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre'
NUM = r'(?<![\w.,])(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)(?![\w])'
ESCALA = r'(?:\s+(mil millones|millones|millón|mil))?'


def numeros(t):
    """[(inicio, fin, texto, valor, decimales)] de las cifras de un texto, sin años, horas, fechas ni ordinales."""
    tapado = t
    def tapa(m):
        return ' ' * (m.end() - m.start())
    for pat in (rf'\b\d{{1,2}}(?:\s*(?:y|,|-|al?)\s*\d{{1,2}})*\s+de\s+(?:{MESES})\b',   # 3 de noviembre, 3 y 4 de mayo
                r'\b\d{1,2}-\d{1,2}-\d{2,4}\b', r'\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b',          # 3-11-2026
                r'\b\d{1,2}[.:]\d{2}\b(?!\.\d)',                                              # las 2.00
                r'\b\d+\s*(?:\.?\s*[ºª]|\.ª|\.º)', r'\b\d+(?:er|º|ª)\b',                       # 13.º, 1.ª
                r'\b[A-Z]{1,3}-\d+\b', r'\b\d+[A-Za-z]{1,2}\b',                                # KY-6, 3D, 23J
                r'\b(?:1[89]|20)\d{2}(?:-(?:\d{2}|\d{4}))?\b(?![.,]\d)'):                     # años y 2025-26
        tapado = re.sub(pat, tapa, tapado, flags=re.I)
    out = []
    for m in re.finditer(NUM + ESCALA, tapado):
        txt = t[m.start():m.end()]
        cifra = m.group(1)
        dec = len(cifra.split(',')[1]) if ',' in cifra else 0
        v = float(cifra.replace('.', '').replace(',', '.'))
        esc = {'mil': 1e3, 'millones': 1e6, 'millón': 1e6, 'mil millones': 1e9}.get(m.group(2) or '', 1)
        out.append((m.start(), m.end(), txt, v * esc, dec, esc))
    for m in re.finditer(r'\b(' + '|'.join(PALABRAS) + r')\b', tapado, re.I):
        out.append((m.start(), m.end(), t[m.start():m.end()], PALABRAS[m.group(1).lower()], 0, 1))
    return sorted(out)


def tolerancia(txt, dec, esc):
    """Medio punto de la última cifra escrita: «25,7» ±0,05; «52,8 millones» ±50.000; «25.300» ±50 (redondeo a centenas)."""
    if dec:
        return 0.5 * 10 ** -dec * esc + 1e-9
    entero = re.match(r'[\d.]+', txt).group(0).replace('.', '') if txt[:1].isdigit() else ''
    ceros = len(entero) - len(entero.rstrip('0')) if len(entero) >= 4 else 0
    return 0.5 * 10 ** ceros * esc + 1e-9


def valor_cifra(c):
    """«52,8 millones» -> (52800000.0, 1, 1e6); «once» -> (11, 0, 1)."""
    ns = numeros(' ' + c + ' ')
    if len(ns) != 1:
        return None
    _, _, _, v, dec, esc = ns[0]
    return v, dec, esc


# ---------------------------------------------------------------- datos de la pieza

def literal(s, i):
    """El literal JS/JSON que empieza en s[i] ([ o {), con corchetes equilibrados y cadenas respetadas."""
    abre = s[i]; cierra = ']' if abre == '[' else '}'
    prof = 0; j = i; q = None
    while j < len(s):
        c = s[j]
        if q:
            if c == '\\':
                j += 1
            elif c == q:
                q = None
        elif c in '"\'`':
            q = c
        elif c in '[{':
            prof += 1
        elif c in ']}':
            prof -= 1
            if prof == 0:
                return s[i:j + 1]
        j += 1
    return None


def datos_pieza(pagina):
    D = {}
    for sc in re.findall(r'<script>(.*?)</script>', pagina, re.S):
        for m in re.finditer(r'\b(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*([\[{])', sc):
            lit = literal(sc, m.start(2))
            if not lit:
                continue
            try:
                D[m.group(1)] = json.loads(lit)
            except ValueError:
                pass
    return D


def leer_csv(ruta):
    import csv
    with open(os.path.join(RAIZ, ruta), encoding='utf-8') as f:
        filas = list(csv.DictReader(f))
    for fila in filas:
        for k, v in fila.items():
            try:
                fila[k] = float(v) if re.fullmatch(r'-?\d+(\.\d+)?(e-?\d+)?', v or '') else v
            except (TypeError, ValueError):
                pass
    return filas


def leer_json(ruta):
    return json.load(open(os.path.join(RAIZ, ruta), encoding='utf-8'))


def entorno(D):
    import statistics
    seguro = dict(len=len, sum=sum, min=min, max=max, abs=abs, round=round, sorted=sorted, any=any, all=all,
                  set=set, list=list, dict=dict, tuple=tuple, zip=zip, range=range, enumerate=enumerate,
                  float=float, int=int, str=str, bool=bool, filter=filter, map=map, isinstance=isinstance,
                  mean=statistics.mean, median=statistics.median, True_=True)
    return {'__builtins__': seguro, 'D': D, 'csv': leer_csv, 'json': leer_json, **D}


# ---------------------------------------------------------------- comprobaciones

class Informe:
    def __init__(self, slug):
        self.slug, self.errores, self.avisos, self.notas = slug, [], [], []

    def error(self, que, detalle):
        self.errores.append((que, detalle))

    def aviso(self, que, detalle):
        self.avisos.append((que, detalle))


def comprobar_cifras(inf, p, main, decl, parrafos_base, completa):
    cuerpo = norm(limpio(main))
    trozos = bloques(main)
    # titular y entradilla: sus cifras tienen que estar en el cuerpo (con su redondeo) o recalcularse en «cifras»
    cuerpo_sin_cabeza = re.split(r'<h2>(?:Método y fuentes|Mètode i fonts)</h2>', main)[0]
    cuerpo_sin_cabeza = re.sub(r'<h1\b.*?</h1>|<p class="(?:dek|kicker|byline)[^"]*">.*?</p>', ' ', cuerpo_sin_cabeza, flags=re.S)
    valores_cuerpo = [x for n in numeros(limpio(cuerpo_sin_cabeza)) for x in (n[3], n[3] / n[5])]   # «4,4» = «4,4 millones»
    calculadas = [norm(e.get('texto', '')) for e in decl.get('cifras', [])]
    for etiqueta, t in (('del titular', p['titulo']), ('de la entradilla', p['descripcion'])):
        nt = norm(t)
        for ini, fin, txt, v, dec, esc in numeros(nt):
            tol = tolerancia(txt, dec, esc)
            if any(abs(b - v) <= tol for b in valores_cuerpo) or any(_cubre(nt, f, ini, fin) for f in calculadas if f):
                continue
            inf.error('Cifra ' + etiqueta + ' que no está en el texto', f'«{txt}» en «{t}» (repítela en el cuerpo o recalcúlala en «cifras»)')
    trozos = [('titular', p['titulo']), ('entradilla', p['descripcion'])] + trozos
    # frases declaradas: tienen que seguir en la pieza
    declaradas = []
    for clase in ('cifras', 'externas', 'ignorar', 'permitir_espana'):
        for e in decl.get(clase, []):
            f = norm(e.get('texto', ''))
            if not f:
                inf.error('Declaración sin «texto»', f'{clase}: {e}')
                continue
            dentro = f in cuerpo or f in norm(p['titulo']) or f in norm(p['descripcion'])
            if not dentro:
                inf.error('Frase declarada que ya no está en la pieza (¿ha cambiado el texto?)', f'{clase}: «{f}»')
            if clase != 'permitir_espana':
                declaradas.append((clase, f, e))
    # cada cifra de un párrafo nuevo o cambiado tiene que estar dentro de una frase declarada
    sin_declarar = []
    for tipo, t in trozos:
        if not completa and norm(t) in parrafos_base:
            continue
        nt = norm(t)
        for ini, fin, txt, *_ in numeros(nt):
            if not any(_cubre(nt, f, ini, fin) for _, f, _ in declaradas):
                sin_declarar.append((tipo, txt, nt[max(0, ini - 60):fin + 40]))
    for tipo, txt, ctx in sin_declarar:
        inf.error('Cifra sin verificar', f'«{txt}» ({tipo}): …{ctx}…')
    # los cálculos
    D = datos_pieza(main_y_script(p))
    env = entorno(D)
    enlaces = set(re.findall(r'href="([^"]+)"', main)) | {u for u, _ in p.get('fuentes', [])}
    for e in decl.get('cifras', []):
        f = norm(e.get('texto', ''))
        if 'condicion' in e:   # afirmaciones sin cifra exacta: «todos por menos de 4 puntos», «el mayor desde 1946»
            try:
                ok = eval(e['condicion'], env)
            except Exception as ex:
                inf.error('La condición falla', f'«{f}»: {e["condicion"]} → {type(ex).__name__}: {ex}')
                continue
            if ok is not True:
                inf.error('La afirmación no se cumple en los datos', f'«{f}»: {e["condicion"]} → {ok!r}')
            else:
                inf.notas.append(f'✔ «{f}» se cumple')
            continue
        cifra = e.get('cifra')
        if cifra is None:
            ns = numeros(f)
            if len(ns) != 1:
                inf.error('Falta «cifra» (la frase tiene más de un número)', f'«{f}»')
                continue
            cifra = ns[0][2]
        if norm(cifra) not in f:
            inf.error('La «cifra» no está en su frase', f'«{cifra}» en «{f}»')
            continue
        vc = valor_cifra(cifra)
        if vc is None:
            inf.error('No entiendo la cifra', f'«{cifra}»')
            continue
        v, dec, esc = vc
        if 'calculo' not in e:
            inf.error('Cifra sin «calculo»', f'«{f}»')
            continue
        try:
            r = eval(e['calculo'], env)
        except Exception as ex:
            inf.error('El cálculo falla', f'«{cifra}»: {e["calculo"]} → {type(ex).__name__}: {ex}')
            continue
        try:
            r = float(r)
        except (TypeError, ValueError):
            inf.error('El cálculo no da un número', f'«{cifra}»: {e["calculo"]} → {r!r}')
            continue
        tol = e.get('tolerancia', tolerancia(norm(cifra), dec, esc))
        if abs(abs(r) - v) > tol if e.get('valor_absoluto') else abs(r - v) > tol:
            inf.error('La cifra no cuadra con los datos', f'el texto dice «{cifra}» y el cálculo da {r:,.4f} ({e["calculo"]}) en «{f}»')
        else:
            inf.notas.append(f'✔ «{cifra}» = {r:,.4f}')
    for e in decl.get('externas', []):
        fu = e.get('fuente', '')
        if not fu:
            inf.error('Cifra externa sin «fuente»', f'«{e.get("texto")}»')
        elif fu not in enlaces:
            inf.error('La fuente de una cifra externa no está enlazada en la pieza', f'{fu} («{e.get("texto")}»)')
        else:
            inf.notas.append(f'◦ externa, revisar a mano: «{e.get("texto")}» ({fu})')
    for e in decl.get('ignorar', []) + decl.get('permitir_espana', []):
        if not e.get('motivo'):
            inf.error('Excepción sin «motivo»', f'«{e.get("texto")}»')


def _cubre(nt, f, ini, fin):
    i = nt.find(f)
    while i != -1:
        if i <= ini and fin <= i + len(f):
            return True
        i = nt.find(f, i + 1)
    return False


_PAGINAS = {}


def main_y_script(p):
    return _PAGINAS[p['slug']]


def ruta_local(url, desde):
    """Ruta en el repositorio de un enlace interno, o None si es externo."""
    if url.startswith(('mailto:', 'tel:', 'javascript:', 'data:', '#')):
        return ''
    u = urllib.parse.urlsplit(url)
    if u.scheme in ('http', 'https'):
        if u.netloc not in ('mapaelectoral.es', 'www.mapaelectoral.es'):
            return None
        ruta = os.path.join(RAIZ, urllib.parse.unquote(u.path).lstrip('/'))
    elif u.scheme:
        return ''
    elif u.path.startswith('/'):
        ruta = os.path.join(RAIZ, urllib.parse.unquote(u.path).lstrip('/'))
    else:
        ruta = os.path.normpath(os.path.join(os.path.dirname(desde), urllib.parse.unquote(u.path)))
    if ruta.endswith('/') or os.path.isdir(ruta):
        ruta = os.path.join(ruta, 'index.html')
    return ruta


FIRMAS = {b'\xff\xd8\xff': 'jpg', b'\x89PNG': 'png', b'GIF8': 'gif', b'RIFF': 'webp', b'<svg': 'svg', b'<?xm': 'svg'}


def comprobar_imagen(inf, ruta, de_donde):
    if not os.path.isfile(ruta):
        inf.error('Imagen que no existe', f'{os.path.relpath(ruta, RAIZ)} ({de_donde})')
        return
    cab = open(ruta, 'rb').read(16)
    if os.path.getsize(ruta) < 200 or not any(cab.lstrip().startswith(k) for k in FIRMAS):
        inf.error('Imagen vacía o rota', f'{os.path.relpath(ruta, RAIZ)} ({de_donde})')


def comprobar_enlaces_e_imagenes(inf, p, pagina, ruta_pagina, externos):
    main = re.search(r'<main>.*?</main>', pagina, re.S)
    main = main.group(0) if main else pagina
    # imágenes
    for src in re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', main):
        r = ruta_local(src, ruta_pagina)
        if r is None:
            externos.add((src, inf.slug, 'imagen'))
        elif r:
            comprobar_imagen(inf, r, '<img>')
    for src in re.findall(r'<meta\s+(?:property|name)="(?:og:image|twitter:image)"\s+content="([^"]+)"', pagina):
        r = ruta_local(src, ruta_pagina)
        if r:
            comprobar_imagen(inf, r, 'Open Graph')
    comprobar_imagen(inf, os.path.join(RAIZ, 'img', 'compartir', f'actualidad-{p["slug"]}.jpg'), 'imagen para compartir')
    if p.get('foto'):
        comprobar_imagen(inf, os.path.join(RAIZ, p['foto']['src']), 'foto de cabecera')
    # enlaces
    for href in set(re.findall(r'<a\b[^>]*\bhref="([^"]+)"', main)) | {u for u, _ in p.get('fuentes', [])}:
        href = html.unescape(href)
        r = ruta_local(href, ruta_pagina)
        if r is None:
            externos.add((href, inf.slug, 'enlace'))
        elif r and not os.path.exists(r):
            inf.error('Enlace interno roto', href)


UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36 MapaElectoral-verificador'


def probar_url(url):
    import socket, ssl
    for metodo in ('HEAD', 'GET'):
        try:
            req = urllib.request.Request(url, method=metodo, headers={'User-Agent': UA, 'Accept': '*/*', 'Accept-Language': 'es,en'})
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status, ''
        except urllib.error.HTTPError as e:
            if metodo == 'HEAD' and e.code in (400, 403, 404, 405, 429, 500, 501, 503):
                continue   # muchas webs no aceptan HEAD: se repite con GET
            return e.code, ''
        except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError) as e:
            razon = getattr(e, 'reason', e)
            if isinstance(razon, socket.gaierror):
                return 'dns', str(razon)
            if metodo == 'HEAD':
                continue
            return 'red', str(razon)
    return 'red', ''


def comprobar_externos(externos, informes):
    urls = sorted({u for u, _, _ in externos})
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        res = dict(zip(urls, ex.map(probar_url, urls)))
    for u, slug, que in sorted(externos):
        cod, det = res[u]
        inf = informes[slug]
        if cod in (404, 410, 'dns'):
            inf.error('Imagen externa rota' if que == 'imagen' else 'Enlace roto', f'{u} → {cod} {det}'.strip())
        elif cod == 'red' or (isinstance(cod, int) and cod >= 400):
            inf.aviso('Enlace que no responde a robots (revisar a mano)', f'{u} → {cod} {det}'.strip())


# Datos españoles en piezas internacionales (fallo que Nacho no quiere ver: 1-11-2026)
ESPANA = [r'\bPSOE\b', r'\bPP\b', r'\bVox\b', r'\bSumar\b', r'\bPodemos\b', r'\bERC\b', r'\bJunts\b', r'\bPNV\b',
          r'\bBildu\b', r'\bBNG\b', r'\bCompromís\b', r'\bCoalición Canaria\b', r'\bUPN\b', r'\bCUP\b', r'\bSALF\b',
          r'\bFeijóo\b', r'\bAbascal\b', r'\bPedro Sánchez\b', r'\bYolanda Díaz\b', r'\bPuigdemont\b',
          r'\b29N\b', r'\b29-N\b', r'\b23J\b', r'\b23-J\b', r'Congreso de los Diputados', r'\bMoncloa\b',
          r'\bAndalucía\b', r'\bCataluña\b', r'\bCatalunya\b', r'\bComunidad de Madrid\b', r'\bGalicia\b', r'\bEuskadi\b',
          r'\bPaís Vasco\b', r'\bComunidad Valenciana\b', r'\bCastilla y León\b', r'\bCastilla-La Mancha\b', r'\bExtremadura\b',
          r'\bAragón\b', r'\bAsturias\b', r'\bCantabria\b', r'\bNavarra\b', r'\bLa Rioja\b', r'\bRegión de Murcia\b',
          r'\bBaleares\b', r'\bCanarias\b', r'\bCeuta\b', r'\bMelilla\b']   # «elecciones generales» sola no: también las hay en Nueva Zelanda (#420)
ENLACES_ESPANA = [r'infoelectoral\.interior\.gob\.es', r'(?<![\w.])ine\.es/', r'(?:\.\./)+municipio/', r'(?:\.\./)+generales-2026/',
                  r'(?:\.\./)+listas-electorales-29n/', r'(?:\.\./)+encuestas/', r'(?:\.\./)+29n/', r'(?:\.\./)+elecciones/']


def comprobar_internacional(inf, p, main, script, decl):
    permitidas = [norm(e.get('texto', '')) for e in decl.get('permitir_espana', [])]
    textos = [('titular', p['titulo']), ('entradilla', p['descripcion']), ('compara', p.get('compara', '')),
              ('límites', p.get('limites', ''))] + bloques(main)
    for donde, t in textos:
        t = norm(t)
        for pat in ESPANA:
            for m in re.finditer(pat, t):
                if not any(_cubre(t, f, m.start(), m.end()) for f in permitidas if f):
                    inf.error('Dato español en una pieza internacional', f'«{m.group(0)}» ({donde}): …{t[max(0, m.start() - 60):m.end() + 40]}…')
    for pat in ESPANA[:20]:   # partidos y líderes en los datos del mapa y los gráficos
        for m in re.finditer(r'"' + pat.replace(r'\b', '') + r'"', script):
            inf.error('Dato español en los datos de una pieza internacional', f'«{m.group(0)}» en el <script>')
    hrefs = re.findall(r'href="([^"]+)"', main) + [u for u, _ in p.get('fuentes', [])]
    for h in hrefs:
        for pat in ENLACES_ESPANA:
            if re.search(pat, h) and not any(h in f for f in permitidas):
                inf.error('Enlace o fuente española en una pieza internacional', h)


def comprobar_actualizado(inf, p, pb, parrafos, parrafos_base):
    if pb is None:
        return
    if set(parrafos) != parrafos_base and p.get('actualizado') == pb.get('actualizado'):
        inf.error('La pieza ya publicada cambia y su «actualizado» no', "pon actualizado='AAAA-MM-DD HH:MM' (hora de Madrid) en construir.py")
    if p['titulo'] != pb['titulo'] or p['descripcion'] != pb['descripcion']:
        if p.get('actualizado') == pb.get('actualizado'):
            inf.error('Cambia el titular o la entradilla y «actualizado» no', p['slug'])


# ---------------------------------------------------------------- plantilla

def plantilla(slug, piezas):
    p = piezas[slug]
    pagina = open(os.path.join(ACT, slug, 'index.html'), encoding='utf-8').read()
    main = re.search(r'<main>.*?</main>', pagina, re.S).group(0)
    ruta = os.path.join(VERIF, slug + '.json')
    previa = json.load(open(ruta, encoding='utf-8')) if os.path.exists(ruta) else {}
    hechas = [norm(e['texto']) for k in ('cifras', 'externas', 'ignorar') for e in previa.get(k, [])]
    nuevas = []
    for tipo, t in [('titular', p['titulo']), ('entradilla', p['descripcion'])] + bloques(main):
        nt = norm(t)
        for ini, fin, txt, *_ in numeros(nt):
            if any(_cubre(nt, f, ini, fin) for f in hechas):
                continue
            a = max(nt.rfind(' ', 0, max(ini - 25, 0)) + 1, 0)
            b = nt.find(' ', min(fin + 20, len(nt)))
            frase = nt[a:b if b != -1 else len(nt)]
            nuevas.append({'texto': frase, 'cifra': txt, 'calculo': 'POR HACER (o pásala a «externas» con su fuente, o a «ignorar» con su motivo)', '_donde': tipo})
    D = datos_pieza(pagina)
    salida = {'pieza': slug,
              '_datos_disponibles': {k: (f'lista de {len(v)}: ' + json.dumps(v[0], ensure_ascii=False)[:120]) if isinstance(v, list) and v else type(v).__name__ for k, v in D.items()},
              'cifras': previa.get('cifras', []) + nuevas, 'externas': previa.get('externas', []),
              'ignorar': previa.get('ignorar', []), 'permitir_espana': previa.get('permitir_espana', [])}
    os.makedirs(VERIF, exist_ok=True)
    json.dump(salida, open(ruta, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{os.path.relpath(ruta, RAIZ)}: {len(nuevas)} cifras por declarar')


# ---------------------------------------------------------------- principal

def principal():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='origin/main')
    ap.add_argument('--slug', nargs='*')
    ap.add_argument('--plantilla')
    ap.add_argument('--sin-red', action='store_true')
    ap.add_argument('--resumen', help='fichero Markdown donde escribir el informe (GITHUB_STEP_SUMMARY)')
    a = ap.parse_args()
    piezas = cargar_construir()
    if a.plantilla:
        return plantilla(a.plantilla, piezas)
    completa = bool(a.slug)
    slugs = a.slug if a.slug else slugs_cambiados(a.base, piezas)
    if not slugs:
        print('Ningún PR de piezas: nada que comprobar.')
        return 0
    codigo_base = git('show', f'{a.base}:actualidad/src/construir.py')
    base = cargar_construir(codigo_base) if codigo_base else {}
    informes, externos = {}, set()
    for slug in slugs:
        inf = informes[slug] = Informe(slug)
        if slug not in piezas:
            inf.error('La pieza no está en construir.py', slug)
            continue
        p = piezas[slug]
        ruta_pag = os.path.join(ACT, slug, 'index.html')
        if not os.path.exists(ruta_pag):
            inf.error('Falta la página construida', f'actualidad/{slug}/index.html: ejecuta python3 actualidad/src/construir.py')
            continue
        pagina = open(ruta_pag, encoding='utf-8').read()
        _PAGINAS[slug] = pagina
        main = re.search(r'<main>.*?</main>', pagina, re.S).group(0)
        script = ''.join(re.findall(r'<script>(.*?)</script>', pagina, re.S))
        ruta_decl = os.path.join(VERIF, slug + '.json')
        if os.path.exists(ruta_decl):
            try:
                decl = json.load(open(ruta_decl, encoding='utf-8'))
            except ValueError as e:
                inf.error('La declaración no es JSON válido', f'{os.path.relpath(ruta_decl, RAIZ)}: {e}')
                decl = {}
        else:
            decl = {}
        pagina_base = git('show', f'{a.base}:actualidad/{slug}/index.html') if not completa else None
        mb = re.search(r'<main>.*?</main>', pagina_base or '', re.S)
        pb = base.get(slug)
        parrafos_base = set()
        if mb and pb:
            parrafos_base = {norm(t) for _, t in bloques(mb.group(0))} | {norm(pb['titulo']), norm(pb['descripcion'])}
        parrafos = {norm(t) for _, t in bloques(main)} | {norm(p['titulo']), norm(p['descripcion'])}
        nueva = pb is None
        cambia_texto = completa or nueva or parrafos != parrafos_base
        if cambia_texto and not decl and any(numeros(t) for t in parrafos - parrafos_base):
            inf.error('Falta la declaración de cifras', f'actualidad/verificacion/{slug}.json (créala con: python3 src/verificar_piezas.py --plantilla {slug})')
        if cambia_texto:
            comprobar_cifras(inf, p, main, decl, parrafos_base, completa or nueva)
        comprobar_enlaces_e_imagenes(inf, p, pagina, ruta_pag, externos)
        if p.get('serie') == 'internacional':
            comprobar_internacional(inf, p, main, script, decl)
        if not completa:
            comprobar_actualizado(inf, p, pb, parrafos, parrafos_base)
    if externos and not a.sin_red:
        comprobar_externos(externos, informes)
    # informe
    lineas = ['# Comprobación automática de las piezas', '']
    total = 0
    for slug, inf in informes.items():
        total += len(inf.errores)
        estado = '❌' if inf.errores else '✅'
        lineas.append(f'## {estado} {slug}')
        lineas.append(f'{len(inf.errores)} errores, {len(inf.avisos)} avisos, {sum(n.startswith("✔") for n in inf.notas)} cifras recalculadas, '
                      f'{sum(n.startswith("◦") for n in inf.notas)} cifras externas para el editor.')
        for que, det in inf.errores:
            lineas.append(f'- ❌ **{que}**: {det}')
        for que, det in inf.avisos:
            lineas.append(f'- ⚠️ {que}: {det}')
        if inf.notas:
            lineas.append('<details><summary>Cifras comprobadas</summary>\n')
            lineas += [f'- {n}' for n in inf.notas]
            lineas.append('\n</details>')
        lineas.append('')
    texto = '\n'.join(lineas)
    print(texto)
    if a.resumen:
        with open(a.resumen, 'a', encoding='utf-8') as f:
            f.write(texto + '\n')
    return 1 if total else 0


if __name__ == '__main__':
    sys.exit(principal())
