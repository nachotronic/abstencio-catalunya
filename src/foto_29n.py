"""Foto fija del escrutinio del 29N en el HTML, para los buscadores que no ejecutan JavaScript (GPTBot, ClaudeBot,
PerplexityBot; Google sí lo ejecuta, pero más tarde). La noche del 29N, cada 15 minutos (.github/workflows/foto-29n.yml):

- en la página de resultados, dentro de la caja del escrutinio (.d-cuerpo, entre <!--foto29n--> y <!--/foto29n-->), el
  mismo resumen que pinta directo-resultados.js: escrutado, candidatura más votada, votos, % y escaños. El JavaScript lo
  sustituye por el dato al minuto en cuanto carga;
- en llms.txt, una línea con lo mismo (entre <!--foto29n--> y <!--/foto29n-->).

No toca title, description, H1, canonical, URL ni la fecha de la firma. Solo escribe con datos reales del 29 o 30-11 (ni
simulacro, ni retenidos antes de las 21:00, ni sin mesas escrutadas); si no, no hace nada.
Uso: python3 src/foto_29n.py [URL de resultados.json]   (por defecto, la de generales-2026/data/meta.json → directo.url)
"""
import datetime, html, json, os, pathlib, re, sys, urllib.request
from zoneinfo import ZoneInfo

RAIZ = pathlib.Path(__file__).resolve().parent.parent
PAGINA = RAIZ / 'elecciones/resultados-elecciones-generales-2026/index.html'
LLMS = RAIZ / 'llms.txt'
URL_PAGINA = 'https://mapaelectoral.es/elecciones/resultados-elecciones-generales-2026/'
MADRID = ZoneInfo('Europe/Madrid')

# Igual que directo-resultados.js
MISMO = {'PP': re.compile(r'^(PP\b|PP-|P\.P\.|UPN-PP)'), 'PSOE': re.compile(r'PSOE(?! ?\(?H)|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN')}
NOMBRE = {'B.N.G.': 'BNG', 'EAJ-PNV': 'PNV', 'JXCAT - JUNTS': 'Junts', 'JXCAT-JUNTS': 'Junts', 'JXCAT': 'Junts', 'TERUEL EXISTE': 'Teruel Existe',
          'EH BILDU': 'EH Bildu', 'VOX': 'Vox', 'CCA': 'Coalición Canaria', 'U.P.N.': 'UPN', 'SUMAR': 'Sumar', 'PODEMOS': 'Podemos',
          'CUP-PR': 'CUP', 'SALF': 'Se Acabó la Fiesta', 'FO': 'Frente Obrero'}
FA = re.compile(r'FRENTE AMPLIO|FRONT AMPLI|FRONTE AMPLA|FRONTE ZABALA|^FA$|^COMUNS|^ARAM[EÉ]S|PODEMOS, IU, SUMAR|^COMPROM')


def pct(x):
    return f'{x * 100:.1f}'.replace('.', ',') + ' %'


def miles(n):
    return f'{round(n):,}'.replace(',', '.')


DIAS = (datetime.date(2026, 11, 29), datetime.date(2026, 11, 30))
HORA = 21   # el primer día, nada antes de las 21:00 (cierre de Canarias)
CABECERAS = {'title': r'<title>(.*?)</title>', 'description': r'<meta name="description" content="([^"]*)"', 'h1': r'<h1[^>]*>(.*?)</h1>',
             'canonical': r'<link rel="canonical" href="([^"]*)"', 'og': r'<meta property="og:[^"]*" content="([^"]*)"',
             'robots': r'<meta name="robots" content="([^"]*)"'}


def cabeceras(t):
    return {k: re.findall(p, t, re.S) for k, p in CABECERAS.items()}


def fuera_de_marcas(t):
    return re.sub(r'<!--foto29n-->.*?<!--/foto29n-->', '', t, flags=re.S)


def resumen(F, meta):
    """-> dict con escrutado, hora, filas [(nombre, votos, %, escaños)], blancos, o None si no hay datos que publicar."""
    if F.get('simulacro') or F.get('retenido') or not F.get('mun') or not F.get('siglas'):
        return None
    act = F.get('actualizado') or ''
    t = datetime.datetime.fromisoformat(act.replace('Z', '+00:00')).astimezone(MADRID) if act else None
    if not t or t.date() not in DIAS or (t.date() == DIAS[0] and t.hour < HORA):
        return None
    reglas = [(c, re.compile(p)) for c, p in meta.get('reglas', [])]
    fam = {f['cod']: f for f in meta.get('familias', [])}

    def familia(s):
        a = (s or '').upper().strip()
        for x in (a, a.replace('.', '')):
            for c, r in reglas:
                if r.search(x):
                    return c
        return 'OTROS'

    def grupo(s):
        a, f = (s or '').upper().strip(), familia(s)
        if FA.search(a):
            return 'FA', 'Frente Amplio'
        if f in MISMO and MISMO[f].search(a):
            return f, fam[f]['nombre']
        return 's:' + NOMBRE.get(a, a), NOMBRE.get(a, s)

    ct = ce = vot = bl = 0
    votos = [0] * len(F['siglas'])
    for a in F['mun'].values():
        ct += a[0]; ce += a[1]; vot += a[2]; bl += a[3]
        for k in range(len(F['siglas'])):
            votos[k] += a[5 + k] if 5 + k < len(a) else 0
    TO = (F.get('ambitos') or {}).get('TO')
    sig, tot_esc = F['siglas'], None
    if TO and TO.get('c') and TO.get('ce'):   # España con el fichero de totales de Interior, como directo-resultados.js
        sig = [x[0] for x in TO['c']]; votos = [x[1] for x in TO['c']]; tot_esc = [x[2] for x in TO['c']]
        ct, ce, vot, bl = TO['ct'], TO['ce'], TO['vo'], TO['bl']
    if not ce or not ct:
        return None
    G = {}
    for k, (s, v) in enumerate(zip(sig, votos)):
        if v or (tot_esc and tot_esc[k]):
            g, n = grupo(s); G.setdefault(g, [n, 0, 0])[1] += v
    con_esc = False
    if tot_esc:
        for s, n in zip(sig, tot_esc):
            if n:
                G[grupo(s)[0]][2] += n; con_esc = True
    else:
        for d in (F.get('escanos') or {}).values():
            for s, n in d.items():
                k, nom = grupo(s); G.setdefault(k, [nom, 0, 0])[2] += n; con_esc = con_esc or n > 0
    val = sum(x[1] for x in G.values()) + bl
    # comprobaciones de cordura: si algo no cuadra, no se publica nada (se queda la foto anterior)
    if not (0 < ce <= ct) or not val or vot > ce or sum(x[2] for x in G.values()) > 350:
        print(f'Datos que no cuadran (escrutado {ce}/{ct}, votantes {vot}, escaños {sum(x[2] for x in G.values())}): no se publica'); return None
    L = sorted(G.values(), key=lambda x: (-x[2], -x[1]))
    filas = [x for x in L if x[1] / val >= 0.005 or x[2]]
    return {'esc': ce / ct, 'hora': t.strftime('%H:%M'), 'fecha': t, 'filas': filas, 'otras': sum(x[1] for x in L if x not in filas),
            'bl': bl, 'val': val, 'part': vot / ce, 'con_esc': con_esc}


def bloque_html(R):
    e = html.escape
    mas = max(R['filas'], key=lambda x: x[1])   # la más votada (las filas van por escaños)
    p = (f'<p class="d-estado">Escrutado el {pct(R["esc"])} del censo · datos de las {R["hora"]}</p>'
         f'<p data-tipo="dato">Con el {pct(R["esc"])} del censo escrutado, {e(mas[0])} es la candidatura más votada, '
         f'con el {pct(mas[1] / R["val"])} del voto válido. Participación en las mesas escrutadas: {pct(R["part"])}.</p>')
    cab = '<th>Escaños</th>' if R['con_esc'] else ''
    t = (f'<table class="d-tabla"><caption>Votos{" y escaños" if R["con_esc"] else ""} del 29N en España ({pct(R["esc"])} escrutado)</caption>'
         f'<thead><tr><th>Candidatura</th><th>Votos</th><th>% voto válido</th>{cab}</tr></thead><tbody>')
    for n, v, s in R['filas']:
        t += f'<tr><td>{e(n)}</td><td>{miles(v)}</td><td>{pct(v / R["val"])}</td>' + (f'<td>{s}</td>' if R['con_esc'] else '') + '</tr>'
    if R['otras']:
        t += f'<tr><td>Otras</td><td>{miles(R["otras"])}</td><td>{pct(R["otras"] / R["val"])}</td>' + ('<td>0</td>' if R['con_esc'] else '') + '</tr>'
    t += f'<tr><td>En blanco</td><td>{miles(R["bl"])}</td><td>{pct(R["bl"] / R["val"])}</td>' + ('<td></td>' if R['con_esc'] else '') + '</tr></tbody></table>'
    ley = ('<p class="leyenda">Escrutinio provisional del Ministerio del Interior, sobre voto válido (candidaturas más blancos) y sin el '
           'voto desde el extranjero (CERA). ' + ('Escaños provisionales según Interior; mayoría absoluta, 176. ' if R['con_esc'] else '')
           + 'Cambia hasta el escrutinio definitivo de las juntas electorales.</p>')
    return '<!--foto29n-->' + p + t + ley + '<!--/foto29n-->'


def linea_llms(R):
    partes = [f'{n} {pct(v / R["val"])}' + (f' y {s} escaños' if R['con_esc'] else '') for n, v, s in R['filas'][:8]]
    return (f'<!--foto29n-->- [Resultados de las elecciones generales del 29N de 2026]({URL_PAGINA}): escrutinio provisional del '
            f'Ministerio del Interior, {pct(R["esc"])} escrutado a las {R["hora"]} del {R["fecha"].day} de noviembre de 2026 (hora peninsular). '
            + '; '.join(partes) + '.<!--/foto29n-->')


def escribe(R):
    cambios = []
    t = PAGINA.read_text(encoding='utf-8')
    previo = re.search(r'<!--foto29n--><p class="d-estado">Escrutado el ([\d,]+) %', t)
    if previo and R['esc'] * 100 < float(previo.group(1).replace(',', '.')) - 0.1:   # nunca hacia atrás (dato viejo o caché)
        print(f'El escrutado baja de {previo.group(1)} % a {pct(R["esc"])}: no se publica'); return []
    b = bloque_html(R)
    if '<!--foto29n-->' in t:
        n = re.sub(r'<!--foto29n-->.*?<!--/foto29n-->', lambda m: b, t, count=1, flags=re.S)
    else:
        m = re.search(r'<div class="d-cuerpo"[^>]*>', t)
        if not m:
            sys.exit('No encuentro la caja .d-cuerpo en la página de resultados')
        n = t[:m.end()] + b + t[m.end():]
    # seguro: fuera del bloque marcado, la página tiene que quedar igual byte a byte, y las cabeceras, idénticas
    if fuera_de_marcas(n) != fuera_de_marcas(t) or cabeceras(n) != cabeceras(t):
        sys.exit('La foto cambiaría algo fuera de su bloque o en las cabeceras: no se escribe nada')
    if n != t:
        PAGINA.write_text(n, encoding='utf-8'); cambios.append(str(PAGINA.relative_to(RAIZ)))
    t = LLMS.read_text(encoding='utf-8')
    l = linea_llms(R)
    if '<!--foto29n-->' in t:
        n = re.sub(r'<!--foto29n-->.*?<!--/foto29n-->', lambda m: l, t, count=1, flags=re.S)
    else:   # justo antes de la línea de la portada, en «Secciones del sitio»
        i = t.index('- [Mapa de resultados de España (portada)]')
        n = t[:i] + l + '\n' + t[i:]
    if fuera_de_marcas(n).replace('\n', '') != fuera_de_marcas(t).replace('\n', ''):
        sys.exit('La línea de llms.txt cambiaría algo más: no se escribe nada')
    if n != t:
        LLMS.write_text(n, encoding='utf-8'); cambios.append('llms.txt')
    return cambios


def main():
    if os.environ.get('FOTO_29N', '').lower() == 'no':   # interruptor: variable del repositorio FOTO_29N = no
        print('FOTO_29N = no: apagada'); return
    args = sys.argv[1:]
    if '--ensayo' in args:   # solo para probar en local con datos de otro día (la prueba de medios del 25-11); nunca en la Action
        i = args.index('--ensayo'); global DIAS, HORA; HORA = 0; d = datetime.date.fromisoformat(args[i + 1]); DIAS = (d, d + datetime.timedelta(days=1)); del args[i:i + 2]
    meta = json.loads((RAIZ / 'generales-2026/data/meta.json').read_text(encoding='utf-8'))
    url = args[0] if args else (meta.get('directo') or {}).get('url')
    if not url:
        print('Sin directo.url en meta.json: nada que hacer'); return
    if url.startswith('http'):
        req = urllib.request.Request(url + ('&' if '?' in url else '?') + 't=foto', headers={'User-Agent': 'mapaelectoral.es (foto 29N)'})
        F = json.load(urllib.request.urlopen(req, timeout=60))
    else:
        F = json.loads(pathlib.Path(url).read_text(encoding='utf-8'))
    R = resumen(F, meta)
    if not R:
        print('Sin datos publicables del 29N (simulacro, antes de las 21:00, otro día o sin escrutinio): nada que hacer'); return
    c = escribe(R)
    print(f'Escrutado {pct(R["esc"])} a las {R["hora"]}:', ', '.join(c) or 'sin cambios')


if __name__ == '__main__':
    main()
