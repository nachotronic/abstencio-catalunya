"""Barrios de las grandes ciudades: qué secciones censales caen en cada barrio (para las fichas de src/territorios.py).

Ciudades: las 50 capitales de provincia y los municipios de más de 100.000 habitantes (sin Ceuta y Melilla).
Límites de barrio y distrito: OpenStreetMap (relaciones boundary=administrative de nivel 10 y 9 dentro del municipio,
buscado por su código INE, ine:municipio), © colaboradores de OpenStreetMap, licencia ODbL. Donde el municipio no tiene
barrios en OSM se usan los distritos; donde no tiene ninguno de los dos, no hay fichas.
En las grandes ciudades que no tienen barrios en OSM se usan los límites que publica el ayuntamiento (OFICIALES).
Cada sección va al barrio con el que comparte más superficie (geometría de secciones del INE de 2023, vía ineAtlas).

Salida (en el repositorio, para que las páginas se regeneren sin red):
- data/barrios/secciones_barrio.csv: tract_code, mun_code, barrio, distrito, nivel, osm_id, solape (fracción de la sección dentro del barrio)
  (osm_id es el identificador de la relación de OSM, u «of-N» en los barrios de fuente municipal)
- data/barrios/fuentes.json: fuente de los límites de las ciudades que no salen de OSM
- data/barrios/geo/<mun_code>.json: secciones de la ciudad simplificadas (metros, ETRS89 UTM 30N) para los mapas de las fichas

Uso: python3 src/barrios_osm.py [códigos INE...]   (descarga en caché; vuelve a descargar solo lo que falte)
"""
import glob, json, os, re, pathlib, sys, time, urllib.parse, urllib.request
import geopandas as gpd
import pandas as pd
from shapely.geometry import LineString
from shapely.ops import polygonize, unary_union

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'data' / 'barrios'
CACHE = pathlib.Path(os.environ.get('CACHE', '/tmp/claude-0/cache'))
SERVIDORES = ['https://maps.mail.ru/osm/tools/overpass/api/interpreter', 'https://overpass-api.de/api/interpreter',
              'https://overpass.private.coffee/api/interpreter']
CAPITALES = {'01059', '02003', '03014', '04013', '05019', '06015', '07040', '08019', '09059', '10037', '11012', '12040', '13034', '14021',
             '15030', '16078', '17079', '18087', '19130', '20069', '21041', '22125', '23050', '24089', '25120', '26089', '27028', '28079',
             '29067', '30030', '31201', '32054', '33044', '34120', '35016', '36038', '37274', '38038', '39075', '40194', '41091', '42173',
             '43148', '44216', '45168', '46250', '47186', '48020', '49275', '50297'}
MINIMO = 100_000
COBERTURA = 0.7   # parte de las secciones que tiene que caer en algún barrio

# Ciudades grandes sin barrios en OSM: límites del ayuntamiento. url de descarga, campo del nombre y, si lo hay, cómo sacar el distrito.
OFICIALES = {
    '01059': {'url': 'https://www.vitoria-gasteiz.org/docs/j34/catalogo/01/87/BarriosSep2019.json', 'campo': 'TEXTO',
              'fuente': 'los límites de barrios del Ayuntamiento de Vitoria-Gasteiz (datos abiertos, septiembre de 2019)',
              'web': 'https://www.vitoria-gasteiz.org/wb021/was/contenidoAction.do?idioma=es&uid=app_j34_0187'},
    '15030': {'url': 'https://ide.coruna.gal/server/rest/services/Publica/CB_DIVISIONES_ADMINISTRATIVAS/MapServer/3/query'
                     '?where=1%3D1&outFields=*&outSR=4326&f=geojson', 'campo': 'nom_barrio',
              'fuente': 'la IDE municipal del Concello da Coruña (capa «Barrios / AA VV»)',
              'web': 'https://ide.coruna.gal/server/rest/services/Publica/CB_DIVISIONES_ADMINISTRATIVAS/MapServer'},
    '30030': {'url': 'https://geoserver.murcia.es/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature'
                     '&typeNames=Murcia:pedanias_barrios&outputFormat=application/json&srsName=EPSG:4326', 'campo': 'nombre',
              'distrito': ('https://geoserver.murcia.es/geoserver/wfs?service=WFS&version=2.0.0&request=GetFeature'
                           '&typeNames=Murcia:barrios&outputFormat=application/json&srsName=EPSG:4326', 'Casco urbano', 'Pedanías'),
              'fuente': 'el geoportal del Ayuntamiento de Murcia (barrios y pedanías)',
              'web': 'https://geoserver.murcia.es/geoserver/wfs?service=WFS&request=GetCapabilities'},
    '03014': {'url': 'https://gist.githubusercontent.com/josemamira/fb7206917d82be27cbdfa5d2b1fc1b22/raw/'
                     '3defaa7fdb725e37d017dc7496778fa49e7945cf/barrios_Alicante.geojson', 'campo': 'barrio',
              'fuente': 'los barrios de Alicante digitalizados por José Manuel Mira (no es una publicación del ayuntamiento)',
              'web': 'https://gist.github.com/josemamira/fb7206917d82be27cbdfa5d2b1fc1b22'},
}
# Los nombres oficiales vienen en mayúsculas y a menudo sin tildes
TILDES = {'MARIA': 'María', 'JOSE': 'José', 'XOSE': 'Xosé', 'RINCON': 'Rincón', 'CORONACION': 'Coronación', 'MARTIN': 'Martín',
          'CRISTOBAL': 'Cristóbal', 'ESTACION': 'Estación', 'FABRICA': 'Fábrica', 'POLIGONO': 'Polígono', 'DARSENA': 'Dársena',
          'CASTRILLON': 'Castrillón', 'NOSTIAN': 'Nostián', 'PURISIMA': 'Purísima', 'ANTON': 'Antón', 'ANDRES': 'Andrés',
          'GINES': 'Ginés', 'BARTOLOME': 'Bartolomé', 'NICOLAS': 'Nicolás', 'PIO': 'Pío', 'ANTOLIN': 'Antolín', 'BENIAJAN': 'Beniaján',
          'JAVALI': 'Javalí', 'JERONIMO': 'Jerónimo', 'MARTINEZ': 'Martínez', 'ANGEL': 'Ángel', 'ALQUERIAS': 'Alquerías',
          'LUCIA': 'Lucía', 'FLOREZ': 'Flórez', 'BREOGAN': 'Breogán', 'ANIMAS': 'Ánimas', 'BATERIA': 'Batería',
          'TRASATLANTICOS': 'Trasatlánticos', 'REFINERIA': 'Refinería', 'PETROLEO': 'Petróleo', 'RIO': 'Río', 'ASIS': 'Asís',
          'ORZAN': 'Orzán', 'EIRIS': 'Eirís', 'UNIV.': 'Universitario de', 'URB.': 'Urbanización', 'NTRA.': 'Nuestra', 'SRA.': 'Señora de la',
          'STA.': 'Santa', 'PAU': 'PAU', 'GURUGU': 'Gurugú', 'BENALUA': 'Benalúa'}
MINUSCULAS = {'de', 'del', 'la', 'las', 'los', 'el', 'y', 'e', 'da', 'do', 'das', 'dos', 'a'}


def nombre_propio(t):
    """«SANTA MARIA DE OZA» -> «Santa María de Oza»."""
    out = []
    for i, w in enumerate(t.split()):
        a, w, z = ('(' if w.startswith('(') else ''), w.strip('()'), (')' if w.endswith(')') else '')   # «AGRELA (PARQUE EMPRESARIAL)»
        x = TILDES.get(w) or (w if re.fullmatch(r'[IVXL]+', w) else w.capitalize())
        if '-' in w and w not in TILDES:
            x = '-'.join(TILDES.get(p) or p.capitalize() for p in w.split('-'))
        if "'" in w:   # CABEÇÓ D'OR
            x = "'".join(p.capitalize() if j else p.lower() for j, p in enumerate(w.split("'")))
        out.append(a + (x.lower() if i and not a and x.lower() in MINUSCULAS and out[-1] != '-' else x) + z)
    return ' '.join(out)


def descarga(url, cod, sufijo=''):
    f = CACHE / 'oficial' / f'{cod}{sufijo}.json'
    if not f.exists():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'mapaelectoral.es'}), timeout=120).read())
    d = json.loads(f.read_text())
    if 'features' in d and d['features'] and 'attributes' in d['features'][0]:   # Esri JSON (Vitoria)
        from shapely.geometry import Polygon
        from shapely.ops import unary_union as uu
        wkid = d.get('spatialReference', {}).get('wkid', 4326)
        filas = [{**x['attributes'], 'geometry': uu([Polygon(r).buffer(0) for r in x['geometry']['rings']]) if len(x['geometry']['rings']) > 1
                  else Polygon(x['geometry']['rings'][0]).buffer(0)} for x in d['features']]
        return gpd.GeoDataFrame(filas, crs=wkid).to_crs(25830)
    return gpd.read_file(f).to_crs(25830)


def oficial(cod):
    """Barrios de fuente municipal con las mismas columnas que relaciones() (todos a nivel 10, o 9 el distrito)."""
    o = OFICIALES[cod]
    g = descarga(o['url'], cod)
    g['nombre'] = g[o['campo']].astype(str).str.strip().map(nombre_propio)
    g = g.dissolve('nombre', as_index=False)[['nombre', 'geometry']]   # barrios en varios polígonos con el mismo nombre
    g['osm_id'] = [f'of-{i + 1}' for i in range(len(g))]
    g['nivel'] = 10
    if 'distrito' in o:
        url, dentro, fuera = o['distrito']
        b = descarga(url, cod, '-distritos').union_all()
        dis = g.copy()
        dis['nombre'] = [dentro if x.intersection(b).area > 0.5 * x.area else fuera for x in g.geometry]
        dis = dis.dissolve('nombre', as_index=False)
        dis['osm_id'], dis['nivel'] = [f'of-d{i}' for i in range(len(dis))], 9
        g = pd.concat([g, dis[['nombre', 'geometry', 'osm_id', 'nivel']]], ignore_index=True)
    return gpd.GeoDataFrame(g, crs=25830)


def ciudades():
    m = pd.read_csv(ROOT / 'generales-2026' / 'descargas' / 'municipios.csv', dtype={'mun_code': str}, usecols=['mun_code', 'poblacion'])
    return sorted(set(m[m.poblacion >= MINIMO].mun_code) | CAPITALES)


def overpass(cod):
    f = CACHE / 'osm' / f'{cod}.json'
    if f.exists():
        return json.loads(f.read_text())
    q = (f'[out:json][timeout:120];rel["ine:municipio"="{cod}"]["boundary"="administrative"];map_to_area->.a;'
         'rel(area.a)["boundary"="administrative"]["admin_level"~"^(9|10)$"];out geom;')
    for intento in range(8):
        url = SERVIDORES[intento % len(SERVIDORES)]
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, urllib.parse.urlencode({'data': q}).encode(),
                                                              headers={'User-Agent': 'mapaelectoral.es'}), timeout=150)
            d = json.loads(r.read())
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(json.dumps(d))
            return d
        except Exception as e:  # servidores públicos saturados: se reintenta en otro
            print(f'  {cod}: {url.split("/")[2]} falla ({str(e)[:60]}), reintento', file=sys.stderr)
            time.sleep(5 + 5 * intento)
    raise RuntimeError(f'Overpass no responde para {cod}')


def poligono(rel):
    lineas = [LineString([(p['lon'], p['lat']) for p in m['geometry']]) for m in rel.get('members', [])
              if m['type'] == 'way' and m.get('role', 'outer') in ('outer', '') and len(m.get('geometry') or []) > 1]
    pol = list(polygonize(unary_union(lineas))) if lineas else []
    return unary_union(pol) if pol else None


def relaciones(d):
    filas = []
    for e in d['elements']:
        g = poligono(e)
        if g is not None and not g.is_empty:
            t = e['tags']
            filas.append({'osm_id': e['id'], 'nombre': t.get('name') or t.get('name:es'),
                          'nivel': int(t['admin_level']), 'geometry': g})
    return gpd.GeoDataFrame(filas, crs=4326).to_crs(25830) if filas else None


def asigna(sec, rel, nivel):
    """Barrio (o distrito) de cada sección: el de mayor superficie compartida."""
    r = rel[rel.nivel == nivel][['osm_id', 'nombre', 'geometry']]
    x = gpd.overlay(sec[['tract_code', 'area', 'geometry']], r, how='intersection', keep_geom_type=True)
    x['solape'] = x.area / x['area']
    return x.sort_values('solape').drop_duplicates('tract_code', keep='last')[['tract_code', 'osm_id', 'nombre', 'solape']]


def main(cods):
    geo = gpd.read_file(glob.glob(str(CACHE / 'geo' / '*.gpkg'))[0])[['tract_code', 'geometry']]
    geo['mun_code'] = geo.tract_code.str[:5]
    filas = []
    previo = pd.read_csv(OUT / 'secciones_barrio.csv', dtype=str) if (OUT / 'secciones_barrio.csv').exists() else None
    for cod in cods:
        sec = geo[geo.mun_code == cod].copy()
        sec['area'] = sec.area
        rel = oficial(cod) if cod in OFICIALES else relaciones(overpass(cod))
        if rel is None:
            print(f'{cod}: sin barrios ni distritos en OSM')
            continue
        niveles = rel.nivel.value_counts()
        opciones = {}
        for nv in (10, 9):   # barrios si cubren la ciudad; si no, distritos
            if niveles.get(nv, 0) >= 4:
                x = asigna(sec, rel, nv)
                x = x[x.solape >= 0.5]   # secciones que caen sobre todo fuera de los barrios cartografiados (puerto, monte...) se quedan sin barrio
                opciones[nv] = x
        nivel = next((nv for nv, x in opciones.items() if len(x) >= COBERTURA * len(sec)), None)
        if nivel is None:
            print(f'{cod}: sin división útil ({ {k: int(v) for k, v in niveles.items()} }, cobertura '
                  + ', '.join(f'nivel {nv}: {len(x) / len(sec):.0%}' for nv, x in opciones.items()) + ')')
            continue
        a = opciones[nivel].rename(columns={'nombre': 'barrio'})
        a['barrio'] = a.barrio.str.replace(r'^(Distrito|Districte) (de |del )?', '', regex=True)   # «Distrito Centro» -> «Centro»
        if a.osm_id.value_counts(normalize=True).iloc[0] > 0.4:   # parroquias gallegas: la del casco urbano se lleva casi toda la ciudad
            print(f'{cod}: una sola unidad reúne más del 40 % de las secciones')
            continue
        if a.barrio.nunique() < 4:
            print(f'{cod}: solo {a.barrio.nunique()} barrios con secciones')
            continue
        if a.barrio.fillna('').str.fullmatch(r'(?i)(distrito|districte|barrutia)?\s*(\d+|[IVXL]+)').mean() > 0.5:
            print(f'{cod}: los distritos de OSM solo tienen número, sin nombre de barrio')
            continue
        if nivel == 10 and niveles.get(9, 0) >= (2 if cod not in OFICIALES else 1):
            dist = asigna(sec, rel, 9)[['tract_code', 'nombre']].rename(columns={'nombre': 'distrito'})
            a = a.merge(dist, on='tract_code', how='left')
        else:
            a['distrito'] = None
        a['mun_code'], a['nivel'] = cod, nivel
        cubiertas = len(a) / len(sec)
        print(f'{cod}: nivel {nivel}, {a.barrio.nunique()} barrios, {len(a)}/{len(sec)} secciones ({cubiertas:.0%})')
        filas.append(a)
        s = sec[['tract_code', 'geometry']].copy()
        s['geometry'] = s.geometry.simplify(8, preserve_topology=True)
        js = {'cod': s.tract_code.tolist(), 'poly': [[[[round(x), round(y)] for x, y in r.exterior.coords]
                                                      for r in (g.geoms if g.geom_type == 'MultiPolygon' else [g])] for g in s.geometry]}
        (OUT / 'geo').mkdir(parents=True, exist_ok=True)
        (OUT / 'geo' / f'{cod}.json').write_text(json.dumps(js, separators=(',', ':')))
    nuevo = pd.concat(filas)[['tract_code', 'mun_code', 'barrio', 'distrito', 'nivel', 'osm_id', 'solape']]
    nuevo['solape'] = nuevo.solape.round(3)
    if previo is not None:
        nuevo = pd.concat([previo[~previo.mun_code.isin(cods)], nuevo.astype(str)])
    for f in (OUT / 'geo').glob('*.json'):   # geometría solo de las ciudades con fichas
        if f.stem not in set(nuevo.mun_code):
            f.unlink()
    nuevo.sort_values('tract_code').to_csv(OUT / 'secciones_barrio.csv', index=False)
    (OUT / 'fuentes.json').write_text(json.dumps({c: {'fuente': o['fuente'], 'web': o['web']} for c, o in OFICIALES.items()
                                                  if c in set(nuevo.mun_code)}, ensure_ascii=False, indent=1) + '\n')


if __name__ == '__main__':
    main(sys.argv[1:] or ciudades())
