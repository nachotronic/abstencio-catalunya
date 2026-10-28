"""Lee del BOE las candidaturas al Congreso y al Senado de unas generales y las guarda en listas-electorales-29n/datos/<eleccion>.json.

El BOE publica dos veces las listas: las *presentadas* (día 22 tras la convocatoria; para el 29N, el 28 de octubre de
2026) y las *proclamadas* por cada junta electoral provincial (día 28; para el 29N, el 3 de noviembre). Las dos llegan
en un único documento con una sección por junta. Se lee la versión XML (https://www.boe.es/diario_boe/xml.php?id=...),
que trae cada candidato en su propio párrafo.

Uso, desde la raíz:
  python3 listas-electorales-29n/src/boe.py 2023 BOE-A-2023-15066 proclamadas
  python3 listas-electorales-29n/src/boe.py 2026 BOE-A-2026-XXXXX presentadas
  python3 listas-electorales-29n/src/boe.py 2026 --buscar 20261028     (busca en el sumario de ese día el documento de candidaturas)
"""
import html, json, pathlib, re, sys, time, unicodedata, urllib.request

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'src'))
from territorios_rutas import PROV_SLUG  # noqa: E402

DESTINO = RAIZ / 'listas-electorales-29n' / 'datos'
SLUG_PROV = {s: c for c, s in PROV_SLUG.items()}
OTRAS = {'araba': '01', 'alava': '01', 'balears': '07', 'baleares': '07', 'illes-balears': '07', 'castello': '12', 'castellon': '12',
         'coruna': '15', 'la-coruna': '15', 'girona': '17', 'gerona': '17', 'lerida': '25', 'orense': '32', 'valencia': '46', 'valencia-valencia': '46',
         'vizcaya': '48', 'guipuzcoa': '20', 'tenerife': '38', 'santa-cruz-de-tenerife': '38'}


def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def provincia(junta):
    s = slug(re.sub(r'(?i)^junta electoral (provincial )?de ', '', junta))
    return SLUG_PROV.get(s) or OTRAS.get(s) or OTRAS.get(s.split('-')[-1])


def descarga(url, intentos=6):
    for i in range(intentos):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': 'application/json, application/xml', 'User-Agent': 'mapaelectoral.es'}), timeout=90).read()
        except Exception:
            time.sleep(4 * (i + 1))
    raise SystemExit(f'No se pudo descargar {url}')


def buscar(dia):
    """Identificadores del sumario del BOE de ese día (AAAAMMDD) cuyo título habla de candidaturas al Congreso."""
    j = json.loads(descarga(f'https://www.boe.es/datosabiertos/api/boe/sumario/{dia}'))
    out = []

    def anda(o):
        if isinstance(o, dict):
            if 'titulo' in o and 'identificador' in o and 'andidaturas' in o['titulo'] and 'Congreso' in o['titulo']:
                out.append((o['identificador'], o['titulo']))
            for v in o.values():
                anda(v)
        elif isinstance(o, list):
            for v in o:
                anda(v)
    anda(j)
    return out


def texto(p):
    p = re.sub(r'<span class="no_partir">(.*?)</span>', r'\1', p)   # «CH<span>A-IU</span>»: sin espacio
    t = re.sub(r'<[^>]+>', ' ', p)
    return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def nombre_limpio(t):
    return re.sub(r'\s+', ' ', t.strip().rstrip('.').strip())


def lee(xml):
    """Devuelve la lista de candidaturas: provincia, cámara, circunscripción (islas en el Senado), número de orden en el
    BOE, denominación, siglas, titulares y suplentes (en el Senado, los dos suplentes de cada candidato)."""
    cuerpo = xml.split('<texto>', 1)[1]
    parrafos = re.findall(r'<p class="([a-z_0-9]+)"[^>]*>(.*?)</p>', cuerpo, re.S)
    out, prov, camara, circ, cand, en_suplentes = [], None, None, None, None, False
    for clase, contenido in parrafos:
        t = texto(contenido)
        if not t:
            continue
        if clase == 'centro_negrita':
            if t.upper().startswith('JUNTA ELECTORAL'):
                prov, camara, circ, cand = provincia(t), None, None, None
                if not prov:
                    raise SystemExit(f'Junta sin provincia reconocida: {t}')
            elif t.lower().startswith('circunscripción electoral'):
                circ, cand = t.split(':', 1)[1].strip(), None
            continue
        if clase == 'centro_cursiva':
            u = slug(t)
            if u.startswith('congreso'):
                camara, circ = 'congreso', None
            elif u.startswith('senado'):
                camara, circ = 'senado', None
            cand = None
            continue
        if clase == 'centro_redonda' and camara:
            m = re.match(r'(\d+)\.\s*(.+)$', t)
            if not m:
                continue
            den = m.group(2).strip()
            sig = ''
            mm = re.search(r'\(([^()]*)\)\s*(\[.*\])?\s*$', den)
            if mm:
                sig = mm.group(1).strip()
                br = re.search(r'\[(.+?)\s*\(([^()]*)\)\]\s*$', den)
                if br:   # «PARTIDO SOCIALISTA DE EUSKADI-EUSKADIKO EZKERRA (PSOE) [PSE-EE (PSOE)]»: siglas propias delante
                    sig = br.group(1).strip()
            cand = {'prov': prov, 'camara': camara, 'circ': circ or '', 'orden': int(m.group(1)), 'denominacion': den, 'siglas': sig,
                    'titulares': [], 'suplentes': []}
            out.append(cand)
            en_suplentes = False
            continue
        if cand is None or clase not in ('parrafo', 'parrafo_2'):
            continue
        if re.match(r'(?i)^no proclamada\.?$', t):
            cand['no_proclamada'] = True
            continue
        if re.match(r'(?i)^suplentes?\s*:?$', t):
            en_suplentes = True
            continue
        ms = re.match(r'(?i)^suplente\s*(\d*)\s*:\s*(.+)$', t)
        if ms and camara == 'senado' and cand['titulares']:
            cand['titulares'][-1].setdefault('suplentes', []).append(re.sub(r'(?i)\s*\(independ\w*\)$', '', nombre_limpio(ms.group(2))))
            continue
        m = re.match(r'^(\d+)\.\s*(.+)$', t)
        if not m:
            continue
        persona = {'n': int(m.group(1)), 'nombre': nombre_limpio(m.group(2))}
        ind = re.search(r'\s*\((independiente|independent|independentea)\)$', persona['nombre'], re.I)
        if ind:   # «Ana Gil Perdices (Independiente)»: la etiqueta va aparte
            persona['nombre'], persona['independiente'] = persona['nombre'][:ind.start()].rstrip(' .'), True
        (cand['suplentes'] if en_suplentes else cand['titulares']).append(persona)
    return out


def guarda(eleccion, idents, fase):
    """Descarga uno o varios documentos del BOE (si una junta sale aparte), junta sus candidaturas y las guarda en
    datos/<eleccion>-<fase>.json. Devuelve las candidaturas y las provincias que faltan."""
    cands, xml0 = [], None
    for ident in idents:
        xml = descarga(f'https://www.boe.es/diario_boe/xml.php?id={ident}').decode('utf-8')
        xml0 = xml0 or xml
        cands += lee(xml)
    fecha = re.search(r'<fecha_publicacion>(\d{8})</fecha_publicacion>', xml0).group(1)
    falta = sorted(set(PROV_SLUG) - {c['prov'] for c in cands})
    DESTINO.mkdir(parents=True, exist_ok=True)
    salida = {'eleccion': eleccion, 'fase': fase, 'boe': idents[0], 'otros_boe': idents[1:], 'fecha_boe': f'{fecha[:4]}-{fecha[4:6]}-{fecha[6:]}',
              'url': f'https://www.boe.es/diario_boe/txt.php?id={idents[0]}', 'pdf': re.search(r'<url_pdf>(.*?)</url_pdf>', xml0).group(1),
              'candidaturas': cands}
    (DESTINO / f'{eleccion}-{fase}.json').write_text(json.dumps(salida, ensure_ascii=False, separators=(',', ':')))
    cands_ok = [c for c in cands if not c.get('no_proclamada')]
    cong = [c for c in cands_ok if c['camara'] == 'congreso']
    print(f'{", ".join(idents)}: {len(cong)} candidaturas al Congreso, {sum(len(c["titulares"]) for c in cong)} titulares y '
          f'{sum(len(c["suplentes"]) for c in cong)} suplentes; {len(cands_ok) - len(cong)} al Senado; {len(cands) - len(cands_ok)} no proclamadas.')
    if falta:
        print('Aviso: faltan provincias', falta)
    return cands, falta


def main():
    eleccion = sys.argv[1]
    if sys.argv[2] == '--buscar':
        for i, t in buscar(sys.argv[3]):
            print(i, t)
        return
    guarda(eleccion, [sys.argv[2]], sys.argv[3])


if __name__ == '__main__':
    main()
