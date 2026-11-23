"""Datos de las biografías de las fichas de candidato (/listas-electorales-29n/<provincia>/<nombre>/), de fuentes oficiales.

Para cada candidato con ficha reúne, sin escribir nada a mano:
- Congreso: fecha y lugar de nacimiento de la ficha de cada diputado de la XV legislatura en congreso.es, y en qué
  legislaturas (de la I a la XV) se sentó, por qué circunscripción y formación, del buscador de diputados del Congreso.
- Senado: si salió elegido senador en las generales de julio de 2023 (Infoelectoral, Ministerio del Interior, ya leído
  en actualidad/src/senado/senado_2023.csv).

Homonimia: la persona se ata a la ficha que ya tiene, que sale del BOE (provincia + candidatura + puesto). Un diputado
de la XV se identifica por su código en el Congreso (el mismo cruce que ya usa construir.py). Para las legislaturas
anteriores y para quien no es diputado de la XV hacen falta los mismos apellidos y un nombre de pila en común
(sin contar María, José…) y, además, la misma formación o la misma circunscripción. Lo que no cumple eso no entra;
se apunta en «dudosos» para mirarlo a mano. Un senador de 2023 tiene que ser de la misma provincia y del mismo partido.

Escribe listas-electorales-29n/datos/biografias-oficiales.json. biografias.py lo convierte en texto.

Uso, desde la raíz:  python3 listas-electorales-29n/src/bios_datos.py
"""
import csv, html, importlib.util, json, pathlib, re, sys, time, unicodedata, urllib.parse, urllib.request
from collections import defaultdict

sys.dont_write_bytecode = True
RAIZ = pathlib.Path(__file__).resolve().parents[2]
DATOS = RAIZ / 'listas-electorales-29n/datos'
CACHE = RAIZ / 'listas-electorales-29n/datos/.cache-congreso'   # fuera de git (.gitignore): fichas descargadas
BUSCADOR = ('https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=2&p_p_state=normal&p_p_mode=view'
            '&p_p_resource_id=searchDiputados&p_p_cacheability=cacheLevelPage')
FICHA = ('https://www.congreso.es/es/busqueda-de-diputados?p_p_id=diputadomodule&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view'
         '&_diputadomodule_mostrarFicha=true&codParlamentario={}&idLegislatura={}&mostrarAgenda=false')
UA = {'User-Agent': 'Mozilla/5.0 (mapaelectoral.es)'}
ROMANOS = ['', 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'XIII', 'XIV', 'XV']
MES = {m: i + 1 for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])}
NOMBRES_COMUNES = {'maria', 'jose', 'de', 'del', 'la', 'las', 'los', 'y', 'i', 'carmen', 'juan', 'antonio', 'luis', 'manuel',
                   'francisco', 'angel', 'jesus', 'miguel', 'pilar', 'dolores', 'mar'}


def construir():
    spec = importlib.util.spec_from_file_location('listas_construir', RAIZ / 'listas-electorales-29n/src/construir.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def k(n):
    s = unicodedata.normalize('NFKD', n).encode('ascii', 'ignore').decode().lower()
    return ' '.join(re.sub(r'[^a-z ]+', ' ', s).split())


def familia(formacion):
    """Formación del Congreso o siglas del Senado → la familia de construir.py (Podemos y Sumar juntos: «IZQ»)."""
    f = k(formacion)
    for pat, v in [(r'psoe|\bpsc\b|psdeg|\bpse\b|socialist', 'PSOE'), (r'\bvox\b', 'VOX'), (r'\bpp\b|popular|\bupn\b|\bna\b', 'PP'),
                   (r'bildu|amaiur', 'BILDU'), (r'pnv|\beaj\b', 'PNV'), (r'\bbng\b', 'BNG'), (r'\berc\b|esquerra', 'ERC'),
                   (r'junts|jxcat|\bciu\b|\bcdc\b|pdecat|\bdl\b', 'JUNTS'),
                   (r'sumar|\bup\b|podemos|\becp\b|comu|compromis|\biu\b|mas pais|en marea|izquierda unida', 'IZQ'),
                   (r'\bcc\b|\bcca\b|coalicion canaria', 'CC'), (r'\bcs\b|ciudadanos', 'CS')]:
        if re.search(pat, f):
            return v
    return f


def fam_lista(fam):
    return 'IZQ' if fam in ('SUMAR', 'PODEMOS') else fam


def buscador(leg):
    datos = urllib.parse.urlencode({'_diputadomodule_idLegislatura': leg, '_diputadomodule_genero': 0, '_diputadomodule_grupo': 'all',
                                    '_diputadomodule_tipo': 2, '_diputadomodule_nombre': '', '_diputadomodule_apellidos': '',
                                    '_diputadomodule_formacion': 'all', '_diputadomodule_filtroProvincias': '[]',
                                    '_diputadomodule_nombreCircunscripcion': ''}).encode()
    return json.load(urllib.request.urlopen(urllib.request.Request(BUSCADOR, datos, UA), timeout=60))['data']


def fecha_java(s):
    """«Sun Sep 10 00:00:00 CET 1961» → '1961-09-10'."""
    m = re.search(r'\w{3} (\w{3}) (\d{2}) \d\d:\d\d:\d\d \w+ (\d{4})', s)
    return f'{m.group(3)}-{MES[m.group(1)]:02d}-{m.group(2)}' if m else None


def ficha_personal(cod, leg=15):
    """Nacimiento de la ficha de congreso.es en esa legislatura: fecha y, si la da, lugar."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / (f'{cod}.html' if leg == 15 else f'{ROMANOS[leg]}-{cod}.html')
    if not f.exists() or f.stat().st_size < 50000:
        f.write_bytes(urllib.request.urlopen(urllib.request.Request(FICHA.format(cod, ROMANOS[leg]), headers=UA), timeout=60).read())
        time.sleep(0.3)
    t = f.read_text(encoding='utf-8', errors='replace')
    i = t.find('<h3>Ficha personal</h3>')
    if i < 0:
        return {}
    m = re.search(r'Nacid([oa]) el ([^<\n]+?)\s*(?:en ([^<]+?))?\s*</p>', t[i:i + 5000], re.S)
    if not m:
        return {}
    return {'nacimiento': fecha_java(m.group(2)), 'lugar': re.sub(r'\s+', ' ', html.unescape(m.group(3))).strip() if m.group(3) else None}


def main():
    m = construir()
    datos, avance = m.carga()
    cands = m.prepara(datos, avance)
    fichas = m.elige_fichas(cands, avance)
    legs = {leg: buscador(leg) for leg in range(1, 16)}
    cod15 = {str(d['codParlamentario']): d for d in legs[15]}
    por_apellidos = defaultdict(list)
    for leg, arr in legs.items():
        for d in arr:
            por_apellidos[k(d['apellidos'])].append((leg, d))
    senado = [s for s in csv.DictReader(open(RAIZ / 'actualidad/src/senado/senado_2023.csv', encoding='utf-8')) if s['elegido'] == '1']
    sen_nombre = defaultdict(list)
    for s in senado:
        sen_nombre[k(f"{s['nombre']} {s['apellido1']} {s['apellido2']}")].append(s)

    out, dudosos = {}, []
    for c, p in fichas:
        clave = f"{m.PROV_SLUG[c['prov']]}/{p['ficha']}"
        fam = fam_lista(c['fam'])
        x = {'nombre': p['nombre'], 'prov': c['prov'], 'siglas': c['siglas'], 'n': p['n']}
        d = p.get('dipx')
        candidatas = []
        if d and d.get('ficha'):
            cod = re.search(r'codParlamentario=(\d+)', d['ficha']).group(1)
            d15 = cod15.get(cod)
            if d15:
                x['genero'] = 'f' if d15['genero'] == 2 else 'm'
                x.update({k_: v for k_, v in ficha_personal(cod).items() if v})
                x['ficha_congreso'] = d['ficha']
                nom = set(k(d15['nombre']).split()) - NOMBRES_COMUNES
                for leg, e in por_apellidos[k(d15['apellidos'])]:
                    if (set(k(e['nombre']).split()) - NOMBRES_COMUNES) & nom or k(e['nombre']) == k(d15['nombre']):
                        candidatas.append((leg, e, leg == 15 and e['codParlamentario'] == d15['codParlamentario']))
        else:
            w = k(p['nombre']).split()
            for i in range(1, len(w)):
                nom = set(w[:i]) - NOMBRES_COMUNES
                for leg, e in por_apellidos.get(' '.join(w[i:]), []):
                    if (set(k(e['nombre']).split()) - NOMBRES_COMUNES) & nom or k(e['nombre']) == ' '.join(w[:i]):
                        candidatas.append((leg, e, False))
        congreso, ultima = [], None
        for leg, e, seguro in candidatas:
            fila = {'leg': leg, 'circ': e['nombreCircunscripcion'], 'formacion': e['formacion'], 'alta': e['fchAlta'], 'baja': e.get('fchBaja', '')}
            if seguro or familia(e['formacion']) == fam or m.prov_de_circ(e['nombreCircunscripcion']) == c['prov']:
                congreso.append(fila)
                if ultima is None or leg > ultima[0]:
                    ultima = (leg, e['codParlamentario'])
                x.setdefault('genero', 'f' if e['genero'] == 2 else 'm')
            else:
                dudosos.append({'clave': clave, 'motivo': 'congreso: otra formación y otra circunscripción', **fila, 'nombre_congreso': e['apellidosNombre']})
        if congreso and 'nacimiento' not in x:   # exdiputado: nacimiento de la ficha de su última legislatura
            ficha = ficha_personal(ultima[1], ultima[0])
            if ficha.get('nacimiento'):
                x.update({k_: v for k_, v in ficha.items() if v})
                x['ficha_congreso'] = FICHA.format(ultima[1], ROMANOS[ultima[0]])
        if congreso:
            x['congreso'] = sorted({json.dumps(f, sort_keys=True) for f in congreso})
            x['congreso'] = [json.loads(f) for f in x['congreso']]
            x['congreso'].sort(key=lambda f: f['leg'])
        for s in sen_nombre.get(k(p['nombre']), []):
            if s['prov'] == c['prov'] and familia(s['siglas']) == fam:
                x['senado_2023'] = {'prov': s['prov'], 'distrito': s['distrito'], 'siglas': s['siglas']}
                x.setdefault('genero', 'f' if s['sexo'] == 'F' else 'm')
            else:
                dudosos.append({'clave': clave, 'motivo': 'senado 2023: otra provincia o partido', 'prov': s['prov'], 'siglas': s['siglas']})
        if len(x) > 4:
            out[clave] = x
    (DATOS / 'biografias-oficiales.json').write_text(json.dumps({
        'fuentes': {'congreso': 'https://www.congreso.es/es/busqueda-de-diputados',
                    'senado_2023': 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/area-de-descargas/'},
        'personas': out, 'dudosos': dudosos}, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'bios_datos: {len(out)} de {len(fichas)} fichas con datos oficiales; {len(dudosos)} cruces dudosos fuera')


if __name__ == '__main__':
    main()
