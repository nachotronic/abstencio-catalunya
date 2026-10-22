"""Extrae las encuestas del feed JSON de Electográfica descargado en <carpeta> (q*.json). Copia de
/mnt/project-files/previsiones/encuestas/extraer.py; escribe encuestas.json y encuestas_generales_espana.csv."""
import json, glob, re, html, sys, collections
D = sys.argv[1]
ents = {}
for f in glob.glob(D + '/q*.json'):
    for e in json.load(open(f))['feed'].get('entry', []):
        ents[e['id']['$t']] = e
rows, fallo = [], collections.Counter()
porano = collections.Counter()
for e in ents.values():
    t = html.unescape(e['title']['$t']); c = e['content']['$t']; pub = e['published']['$t'][:10]
    amb = re.sub(r'^\[[^]]*\]\s*', '', t.split('·')[0]).strip()
    porano[(pub[:4], 'tot')] += 1
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
        fallo[pub[:4]] += 1; continue
    porano[(pub[:4], 'ok')] += 1
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
    rows.append({'ambito': amb, 'publicado': pub, 'titulo': t, 'url': next(l['href'] for l in e['link'] if l['rel'] == 'alternate'),
                 'ficha': ficha, 'voto': {html.unescape(p).strip(): (float(v) or None) for p, v in pares if html.unescape(p).strip() != 'Participación'}})
print(len(ents), len(rows))
for a in sorted({k[0] for k in porano}):
    print(a, porano[(a, 'ok')], '/', porano[(a, 'tot')])
json.dump(rows, open(D + '/encuestas.json', 'w'), ensure_ascii=False)
esp = [r for r in rows if r['ambito'] == 'ESPAÑA']
print('España', len(esp)); print(sorted(esp, key=lambda r: r['publicado'])[-1])

import csv
with open(D + '/encuestas_generales_espana.csv', 'w', newline='') as fh:
    w = csv.writer(fh); w.writerow(['publicado', 'encuestadora', 'cliente', 'trabajo_campo', 'muestra', 'metodo', 'partido', 'voto', 'url_electografica', 'fuente_original'])
    for r in sorted(esp, key=lambda r: r['publicado']):
        f = r['ficha']
        for k, v in r['voto'].items():
            w.writerow([r['publicado'], f.get('Encuestadora', ''), f.get('Cliente', ''), f.get('Fecha realización', ''), f.get('Muestra', ''), f.get('Método', ''), k, v if v is not None else '', r['url'], f.get('Fuente original', '')])
print(collections.Counter(r['ficha'].get('Encuestadora','?') for r in esp if r['publicado']>='2023-08').most_common(15))
