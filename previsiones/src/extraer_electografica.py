"""Lee las entradas del feed JSON de Electográfica (Blogger) y saca de cada una la ficha técnica y la estimación.

Lo usa `actualizar_encuestas.py`, que descarga el feed. También funciona suelto sobre una carpeta con los q*.json
descargados a mano (como la primera extracción, /mnt/project-files/previsiones/encuestas/extraer.py):

    python3 previsiones/src/extraer_electografica.py <carpeta>      # escribe encuestas.json y encuestas_generales_espana.csv
"""
import collections, csv, glob, html, json, re, sys

COLUMNAS = ['publicado', 'encuestadora', 'cliente', 'trabajo_campo', 'muestra', 'metodo', 'partido', 'voto',
            'url_electografica', 'fuente_original']


def parsea(e):
    """Una entrada del feed -> dict con ámbito, ficha y {partido: voto}; None si no trae estimación."""
    t = html.unescape(e['title']['$t']); c = e['content']['$t']; pub = e['published']['$t'][:10]
    amb = re.sub(r'^\[[^]]*\]\s*', '', t.split('·')[0]).strip()
    # panel de estimación: hasta el siguiente tab-panel
    i = c.find('tab-panel'); j = c.find('tab-panel', i + 20)
    panel = c[i:j] if i > 0 else ''
    pares = re.findall(r'font-weight:500;[^>]*>([^<]+)</div>.*?data-w="([\d.]+)"', panel, re.S)
    if not pares:   # formato antiguo: «PARTIDO 9,1% (21/23) | ...» en el título o en div.extra
        m = re.search(r'<div class="extra">(.*?)<', c, re.S)
        txt = html.unescape(m.group(1)) if m else t.split(':', 1)[-1]
        limpia = lambda p: re.sub(r'^[^\wÀ-ÿ]+', '', re.sub(r'^\s*\([^)]*\)', '', p.split(':')[-1]).strip())
        pares = [(limpia(p), v.replace(',', '.')) for p, v in re.findall(r'([^|%]+?)\s+(\d+(?:,\d+)?)\s*%', txt)]
    if not pares:
        return None
    ficha = {}
    for k, v in re.findall(r'<td[^>]*>\s*(Encuestadora|Cliente|Fecha realizaci[^<]*|M[^<]*todo|Muestra|Margen de error)\s*</td>\s*<td[^>]*>(.*?)</td>', c, re.S):
        ficha[html.unescape(k).strip()] = re.sub(r'<[^>]+>|\s+', ' ', html.unescape(v)).strip()
    for k, v in re.findall(r'field-label">([^<]+)</span><span class="field-value">(.*?)</span></div>', c, re.S):
        ficha[html.unescape(k).strip()] = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', v))).strip()
    m = re.search(r'realizada por (?:<a[^>]*>)?([^<]+?)(?:</a>)?\s+para (?:<a[^>]*>)?([^<.]+)', c)
    if m and not ficha:
        ficha = {'Encuestadora': html.unescape(m.group(1)).strip(), 'Cliente': html.unescape(m.group(2)).strip()}
    m = re.search(r'Fuente:\s*<a href="([^"]+)"', c)
    if m: ficha['Fuente original'] = m.group(1)
    return {'ambito': amb, 'publicado': pub, 'titulo': t, 'url': next(l['href'] for l in e['link'] if l['rel'] == 'alternate'),
            'ficha': ficha, 'voto': {html.unescape(p).strip(): (float(v) or None) for p, v in pares if html.unescape(p).strip() != 'Participación'}}


def filas_largas(rows, ambito=False):
    """Formato largo (una fila por encuesta y partido), ordenado por publicación; con `ambito`, añade esa columna."""
    for r in sorted(rows, key=lambda r: (r['publicado'], r['url'])):
        f = r['ficha']
        for k, v in r['voto'].items():
            fila = [r['publicado'], f.get('Encuestadora', ''), f.get('Cliente', ''), f.get('Fecha realización', ''), f.get('Muestra', ''),
                    f.get('Método', ''), k, v if v is not None else '', r['url'], f.get('Fuente original', '')]
            yield ([r['ambito']] + fila) if ambito else fila


def main(D):
    ents = {}
    for f in glob.glob(D + '/q*.json'):
        for e in json.load(open(f))['feed'].get('entry', []):
            ents[e['id']['$t']] = e
    porano = collections.Counter()
    rows = []
    for e in ents.values():
        r = parsea(e); a = e['published']['$t'][:4]
        porano[(a, 'tot')] += 1
        if r:
            porano[(a, 'ok')] += 1; rows.append(r)
    print(len(ents), len(rows))
    for a in sorted({k[0] for k in porano}):
        print(a, porano[(a, 'ok')], '/', porano[(a, 'tot')])
    json.dump(rows, open(D + '/encuestas.json', 'w'), ensure_ascii=False)
    esp = [r for r in rows if r['ambito'] == 'ESPAÑA']
    print('España', len(esp))
    with open(D + '/encuestas_generales_espana.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(COLUMNAS); w.writerows(filas_largas(esp))


if __name__ == '__main__':
    main(sys.argv[1])
