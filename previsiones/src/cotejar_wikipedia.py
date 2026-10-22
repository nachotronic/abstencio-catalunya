"""Coteja las encuestas de Electográfica con la tabla de Wikipedia para encontrar las que faltan.

Lo ejecuta cada día el workflow `.github/workflows/encuestas.yml`, después de `actualizar_encuestas.py`. A mano:
    python3 previsiones/src/cotejar_wikipedia.py [wikitext.txt]

Fuente: el wikitexto de «Opinion polling for the 2026 Spanish general election» en la Wikipedia en inglés (CC BY-SA
4.0), secciones de estimación de voto desde las generales de 2023. Wikipedia recoge sondeos que Electográfica no
publica (paneles de Electomanía, trackings) y al revés; no sustituye a la fuente principal, sirve para no perder
encuestas.

Escribe en previsiones/datos/encuestas/:
- wikipedia_generales_espana.csv: una fila por encuesta, con encuestadora, medio, fechas de campo, muestra, una
  columna por partido del modelo y el enlace a la fuente original de la referencia.
- faltan_en_electografica.csv: las de Wikipedia de los últimos 120 días sin pareja en Electográfica (misma
  encuestadora y fin de campo a menos de 4 días).
"""
import csv, json, pathlib, re, sys, time, unicodedata, urllib.request
from datetime import date, timedelta

RAIZ = pathlib.Path(__file__).resolve().parents[2]
SALIDA = RAIZ / 'previsiones/datos/encuestas'
PAGINA = 'Opinion_polling_for_the_2026_Spanish_general_election'
URL = f'https://en.wikipedia.org/w/index.php?title={PAGINA}&action=raw'
UA = 'mapaelectoral.es/1.0 (https://mapaelectoral.es; descarga diaria de encuestas)'
MESES = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
# cabecera de Wikipedia -> partido del modelo (los mismos códigos que partidos_encuestas.csv)
PARTIDOS = {'PP': 'PP', 'PSOE': 'PSOE', 'Vox': 'VOX', 'Sumar': 'SUMAR', 'FA': 'SUMAR', 'FV': 'SUMAR', 'Compromís': 'SUMAR',
            'Podemos': 'PODEMOS', 'SALF': 'SALF', 'ERC': 'ERC', 'Junts': 'JUNTS', 'EH Bildu': 'BILDU', 'PNV': 'PNV',
            'BNG': 'BNG', 'CCa': 'CC', 'UPN': 'UPN', 'Aliança.cat': 'ALIANCA', 'CS': 'CS', "Cs": 'CS'}
ORDEN = ['PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS', 'SALF', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN', 'ALIANCA', 'CS', 'OTROS']
# KeyData (Público) es una media de encuestas, no una encuesta: no cuenta como falta
AGREGADORES = {'keydata'}


def clave(nombre):
    """Nombre de encuestadora comparable (la misma regla que encuestas.py, sin depender de pandas)."""
    s = unicodedata.normalize('NFKD', str(nombre)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def descarga():
    for intento in range(4):
        try:
            return urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': UA}), timeout=60).read().decode()
        except Exception as ex:
            if intento == 3:
                raise
            print('reintento', ex); time.sleep(5 * 2 ** intento)


def celdas(fila):
    """Celdas de una fila de wikitabla: (atributos, texto). Cada «|» de inicio de línea o «||» abre una celda."""
    out = []
    for linea in fila.split('\n'):
        if not linea.startswith('|') or linea.startswith('|-') or linea.startswith('|}'):
            if out and not linea.startswith(('|', '!')):
                out[-1] = (out[-1][0], out[-1][1] + '\n' + linea)   # continuación de la celda anterior
            continue
        for c in re.split(r'\|\|', linea[1:]):
            # «atributos| valor»: el primer «|» fuera de [[ ]] y {{ }}
            prof, corte = 0, None
            for i, ch in enumerate(c):
                if c[i:i + 2] in ('[[', '{{'): prof += 1
                elif c[i:i + 2] in (']]', '}}'): prof -= 1
                elif ch == '|' and prof == 0:
                    corte = i; break
            attr, val = (c[:corte], c[corte + 1:]) if corte is not None else ('', c)
            if corte is not None and '=' not in attr and 'Party shading' not in attr and 'span' not in attr:
                attr, val = '', c   # el «|» era parte del contenido
            out.append((attr, val.strip()))
    return out


def cabecera(tabla):
    """Nombres de las columnas de partido de la primera fila de cabecera."""
    nombres = []
    for linea in tabla.split('|-')[1].split('\n'):
        if linea.startswith('!'):
            m = re.findall(r'\[\[[^]]*\|([^]|]+)\]\]', linea)
            nombres.append(m[-1].strip() if m else re.sub(r'.*\|', '', linea).strip())
    return nombres


def numero(txt):
    m = re.search(r"(\d+(?:\.\d+)?)", re.sub(r'<ref.*?(</ref>|/>)', '', txt.split('<br')[0]))
    return float(m.group(1)) if m else None


def fechas(txt, anio):
    """«15–17 Oct», «28 Sep–3 Oct», «30 Dec 2025–3 Jan», «12 Oct» -> (inicio, fin) en ISO."""
    t = re.sub(r'<ref.*?(</ref>|/>)|\{\{[^}]*\}\}|\[\[|\]\]', '', txt).replace('&ndash;', '–').replace('-', '–')
    partes = [p.strip() for p in t.split('–') if p.strip()]
    if not partes:
        return '', ''
    def una(p, mes_def=None, anio_def=anio):
        m = re.match(r'(\d{1,2})(?:\s+([A-Z][a-z]{2}))?(?:\s+(\d{4}))?', p)
        if not m:
            return None
        return int(m.group(1)), MESES.get(m.group(2)) or mes_def, int(m.group(3)) if m.group(3) else anio_def
    fin = una(partes[-1])
    if not fin or not fin[1]:
        return '', ''
    ini = una(partes[0], fin[1], fin[2]) if len(partes) > 1 else fin
    try:
        f = date(fin[2], fin[1], fin[0]); i = date(ini[2], ini[1], ini[0])
    except (TypeError, ValueError):
        return '', ''
    if i > f:
        i = i.replace(year=i.year - 1)
    return i.isoformat(), f.isoformat()


def parsea(texto):
    ini = texto.index('====Voting intention estimates====')
    seccion = texto[ini:texto.index('====Voting preferences====', ini)]
    filas_out = []
    for bloque in re.split(r'\n=====', seccion)[1:]:
        m = re.match(r'(\d{4})', bloque)
        if not m or '{|' not in bloque:
            continue
        anio = int(m.group(1))
        tabla = bloque[bloque.index('{|'):bloque.index('\n|}')]
        cols = cabecera(tabla)   # Polling firm, Fieldwork date, Sample size, Turnout, partidos..., Lead
        partidos = cols[4:-1]
        pend = {}   # rowspan: columna -> (valor, filas que quedan)
        for fila in tabla.split('\n|-')[1:]:
            cs = celdas(fila)
            if not cs or fila.lstrip().startswith('!'):
                continue
            vals, k = [], 0
            while cs or any(c >= len(vals) for c in pend):
                col = len(vals)
                if col in pend:
                    v, n = pend[col]; vals.append(v)
                    pend[col] = (v, n - 1) if n > 1 else None
                    if pend[col] is None: del pend[col]
                    continue
                if not cs:
                    break
                attr, val = cs.pop(0)
                span = int(re.search(r'colspan="?(\d+)', attr).group(1)) if 'colspan' in attr else 1
                rs = int(re.search(r'rowspan="?(\d+)', attr).group(1)) if 'rowspan' in attr else 1
                for _ in range(span):
                    if rs > 1:
                        pend[len(vals)] = (val, rs - 1)
                    vals.append(val)
            if len(vals) < 4 or 'election' in vals[0].lower() and '[[' in vals[0]:
                continue
            firma = re.sub(r'<ref.*?(</ref>|/>)|\{\{[^}]*\}\}|\[\[(?:[^]|]*\|)?|\]\]|\'\'+', '', vals[0]).strip()
            if not firma or 'background' in vals[0]:
                continue
            url = re.search(r'url\s*=\s*([^\s|}]+)', vals[0])
            casa, _, medio = firma.partition('/')
            ci, cf = fechas(vals[1], anio)
            n = re.sub(r'[^\d]', '', re.sub(r'<ref.*?(</ref>|/>)', '', vals[2]))
            votos = {}
            for p, v in zip(partidos, vals[4:4 + len(partidos)]):
                x = numero(v) if '–' not in v.split('<br')[0] else None
                if x is not None:
                    mod = PARTIDOS.get(p, 'OTROS')
                    votos[mod] = round(votos.get(mod, 0) + x, 2)
            if not votos or not cf:
                continue
            filas_out.append({'encuestadora': casa.strip(), 'cliente': medio.strip(), 'campo_inicio': ci, 'campo_fin': cf,
                              'muestra': n, **{p: votos.get(p, '') for p in ORDEN}, 'fuente_original': url.group(1) if url else ''})
    return filas_out


def main():
    texto = open(sys.argv[1]).read() if len(sys.argv) > 1 else descarga()
    wp = parsea(texto)
    if len(wp) < 50:
        sys.exit(f'Solo {len(wp)} encuestas leídas de Wikipedia: ha cambiado el formato. No se escribe nada.')
    SALIDA.mkdir(parents=True, exist_ok=True)
    with open(SALIDA / 'wikipedia_generales_espana.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(wp[0])); w.writeheader(); w.writerows(wp)
    eg = [r for r in csv.DictReader(open(SALIDA / 'encuestas_limpias.csv')) if r['ambito'] == 'ESPAÑA']
    casas = {}
    for r in eg:
        f = r['campo_fin'] or (date.fromisoformat(r['publicado']) - timedelta(days=3)).isoformat()
        casas.setdefault(clave(r['encuestadora']), []).append(date.fromisoformat(f))
    desde = date.today() - timedelta(days=120)
    faltan = []
    for r in wp:
        f = date.fromisoformat(r['campo_fin'])
        c = clave(r['encuestadora'])
        # «IMOP» en Wikipedia es «IMOP Insights» en Electográfica: basta con que un nombre empiece por el otro
        fechas_eg = [g for k, v in casas.items() if k.startswith(c) or c.startswith(k) for g in v]
        if f >= desde and c not in AGREGADORES and not any(abs((f - g).days) <= 4 for g in fechas_eg):
            faltan.append(r)
    with open(SALIDA / 'faltan_en_electografica.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(wp[0])); w.writeheader(); w.writerows(faltan)
    print(len(wp), 'encuestas en Wikipedia;', len(faltan), 'de los últimos 120 días sin pareja en Electográfica')
    resumen = SALIDA / 'resumen.json'
    if resumen.exists():
        r = json.load(open(resumen))
        r['wikipedia'] = {'encuestas': len(wp), 'ultima_fin_campo': max(x['campo_fin'] for x in wp), 'faltan_en_electografica_120_dias': len(faltan)}
        json.dump(r, open(resumen, 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
