"""Descarga las encuestas de generales de Electográfica y las deja en CSV dentro del repositorio.

Lo ejecuta cada día el workflow `.github/workflows/encuestas.yml` y solo hace commit si cambia algo. Se puede lanzar a
mano igual:  python3 previsiones/src/actualizar_encuestas.py

Fuente: el feed JSON público de Blogger de https://www.electografica.com, etiquetas «Generales» (ámbito España) y
«Generales_CCAA» (generales por comunidad o provincia). Se guardan solo las cifras de cada encuesta y su ficha
técnica; al usarlas se cita la encuestadora y el medio original (columna `fuente_original`), nunca el agregador.

Escribe en previsiones/datos/encuestas/:
- generales_espana.csv: formato largo, una fila por encuesta y partido, tal como lo publica la fuente (lo lee
  encuestas.py).
- generales_infraestatales.csv: lo mismo para encuestas de generales por comunidad o provincia, con columna `ambito`.
- encuestas_limpias.csv: una fila por encuesta, con fechas de campo separadas, muestra numérica y una columna por
  partido del modelo (nombres unificados con previsiones/datos/partidos_encuestas.csv; las siglas del mismo espacio,
  como FA + Compromís, se suman).
- resumen.json: fecha de la descarga, número de encuestas, la última y las siglas sin equivalencia.
"""
import csv, json, pathlib, re, sys, time, urllib.request
from collections import defaultdict
from datetime import date, datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from extraer_electografica import COLUMNAS, filas_largas, parsea  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SALIDA = RAIZ / 'previsiones/datos/encuestas'
EQUIV = RAIZ / 'previsiones/datos/partidos_encuestas.csv'
FEED = 'https://www.electografica.com/feeds/posts/default/-/{}?alt=json&max-results=150&start-index={}'
UA = 'mapaelectoral.es (descarga diaria de encuestas; https://mapaelectoral.es)'
PARTIDOS = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'SALF', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN',
            'ALIANCA', 'CS', 'OTROS']


def descarga(etiqueta):
    """Todas las entradas de una etiqueta. Blogger corta cada página por tamaño, así que se avanza por lo recibido."""
    ents, i, total = {}, 1, None
    while total is None or i <= total:
        for intento in range(4):
            try:
                req = urllib.request.Request(FEED.format(etiqueta, i), headers={'User-Agent': UA})
                feed = json.load(urllib.request.urlopen(req, timeout=60))['feed']
                break
            except Exception as ex:   # red inestable: reintenta con espera creciente
                if intento == 3:
                    raise
                print('reintento', etiqueta, i, ex); time.sleep(2 ** (intento + 1))
        total = int(feed['openSearch$totalResults']['$t'])
        lote = feed.get('entry', [])
        if not lote:
            break
        for e in lote:
            ents[e['id']['$t']] = e
        i += len(lote)
        time.sleep(0.5)
    print(etiqueta, len(ents), 'entradas de', total)
    return list(ents.values())


def campo(txt):
    """Inicio y fin del trabajo de campo en ISO: «01-14/10/2026», «29/09-01/10/2026», «07/09/2026»."""
    m = re.search(r'(?:(\d{1,2})(?:/(\d{1,2}))?(?:/(\d{4}))?\s*[-–]\s*)?(\d{1,2})/(\d{1,2})/(\d{4})\s*$', txt or '')
    if not m:
        return '', ''
    d1, m1, a1, d2, m2, a2 = m.groups()
    try:
        fin = date(int(a2), int(m2), int(d2))
        ini = date(int(a1 or a2), int(m1 or m2), int(d1)) if d1 else fin
        if ini > fin:   # «28/12-03/01/2027»: el inicio es del año anterior
            ini = ini.replace(year=ini.year - 1)
        return ini.isoformat(), fin.isoformat()
    except ValueError:
        return '', ''


def muestra(txt):
    m = re.search(r'([\d.]+)\s*entrevistas', txt or '')
    return int(m.group(1).replace('.', '')) if m else ''


def slug_casa(url):
    m = re.search(r'encuesta-(.+?)-\d{6}', url)
    return m.group(1).replace('-', ' ').title() if m else ''


def ambito(a):
    """«GALICIA (Congreso)», «GALICIA» y «GALICIA ▪ Elecciones generales ▪ Sondeo…» (2017-18) son lo mismo."""
    a = re.split(r'\s*(?:▪|\||Sondeo|Encuesta|\(Congreso\))', a)[0].strip()
    return {'COMUNIDAD VALENCIANA': 'COMUNITAT VALENCIANA', 'ISLAS BALEARES': 'ILLES BALEARS'}.get(a, a)


def limpias(rows, equiv):
    """Una fila por encuesta, con partidos unificados; devuelve también las siglas que no están en la tabla."""
    sin = defaultdict(int)
    out = []
    for r in sorted(rows, key=lambda r: (r['publicado'], r['url'])):
        f = r['ficha']
        ini, fin = campo(f.get('Fecha realización', ''))
        votos = defaultdict(float)
        for p, v in r['voto'].items():
            e = [x for x in equiv.get(p, []) if (not x['desde'] or r['publicado'] >= x['desde']) and (not x['hasta'] or r['publicado'] <= x['hasta'])]
            if not e:
                sin[p] += 1; continue
            if v is not None:
                votos[e[0]['partido_modelo']] += v
        out.append({'ambito': r['ambito'], 'publicado': r['publicado'], 'encuestadora': f.get('Encuestadora') or slug_casa(r['url']),
                    'cliente': f.get('Cliente', ''), 'campo_inicio': ini, 'campo_fin': fin, 'muestra': muestra(f.get('Muestra')),
                    'metodo': f.get('Método', ''), **{p: round(votos[p], 2) if p in votos else '' for p in PARTIDOS},
                    'fuente_original': f.get('Fuente original', ''), 'url_agregador': r['url']})
    return out, dict(sin)


def escribe(ruta, cabecera, filas):
    with open(ruta, 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(cabecera); w.writerows(filas)


def main():
    rows = []
    for etiqueta in ('Generales', 'Generales_CCAA'):
        rows += [dict(r, etiqueta=etiqueta) for r in map(parsea, descarga(etiqueta)) if r]
    rows = list({r['url']: r for r in rows}.values())
    # ámbito España: desde 2018 (antes las entradas estaban en inglés y otro formato y no se leen bien)
    esp = [r for r in rows if r['ambito'] == 'ESPAÑA']
    infra = [dict(r, ambito=ambito(r['ambito'])) for r in rows if r['etiqueta'] == 'Generales_CCAA' and r['ambito'] != 'ESPAÑA']
    rows = esp + infra
    # salvaguarda: si la descarga sale mucho más corta que lo guardado, no se pisa nada
    previa = SALIDA / 'resumen.json'
    if previa.exists():
        antes = json.load(open(previa))['encuestas_espana']
        if len(esp) < 0.95 * antes:
            sys.exit(f'Descarga incompleta: {len(esp)} encuestas de España frente a {antes} guardadas. No se escribe nada.')
    equiv = defaultdict(list)
    for x in csv.DictReader(open(EQUIV)):
        equiv[x['nombre_encuesta']].append(x)
    SALIDA.mkdir(parents=True, exist_ok=True)
    escribe(SALIDA / 'generales_espana.csv', COLUMNAS, filas_largas(esp))
    escribe(SALIDA / 'generales_infraestatales.csv', ['ambito'] + COLUMNAS, filas_largas(infra, ambito=True))
    tabla, sin = limpias(rows, equiv)
    with open(SALIDA / 'encuestas_limpias.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(tabla[0])); w.writeheader(); w.writerows(tabla)
    ult = max(esp, key=lambda r: (r['publicado'], r['url']))
    resumen = {'descargado': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'fuente': 'https://www.electografica.com',
               'encuestas_espana': len(esp), 'encuestas_infraestatales': len(infra),
               'desde': min(r['publicado'] for r in esp), 'ultima': {'publicado': ult['publicado'],
               'encuestadora': ult['ficha'].get('Encuestadora', ''), 'cliente': ult['ficha'].get('Cliente', '')},
               'siglas_sin_equivalencia': dict(sorted(sin.items(), key=lambda t: -t[1]))}
    json.dump(resumen, open(previa, 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(resumen, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
