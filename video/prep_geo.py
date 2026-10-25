"""Proyecta las secciones de Cataluña a coordenadas planas para el vídeo."""
import json, math, sys
src, dst = sys.argv[1], sys.argv[2]
g = json.load(open(src))
LAT0 = 41.7
k = math.cos(math.radians(LAT0))
def proj(lon, lat):
    return (lon * k, -lat)
feats = []
for f in g['features']:
    p = f['properties']
    geom = f['geometry']
    polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    rings = []
    for poly in polys:
        ring = poly[0]
        pts, last = [], None
        for lon, lat in ring:
            x, y = proj(lon, lat)
            q = (round(x, 4), round(y, 4))
            if q != last:
                pts.extend(q); last = q
        if len(pts) >= 6:
            rings.append(pts)
    feats.append({'c': p['tract_code'], 'm': p['mun_name'], 't': p.get('turnout'), 'v': p.get('pct_ad_vota'),
                  's': p.get('pct_ad_sinderecho'), 'a': p.get('pct_ad_abst'), 'r': rings})
json.dump(feats, open(dst, 'w'), separators=(',', ':'))
print(len(feats))
