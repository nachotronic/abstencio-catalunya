"""Mapas estáticos en SVG (sin JavaScript) para las páginas de /elecciones/: provincias y municipios de España.

Lee la geometría del mapa de resultados (generales-2026/data/provincias.json y municipios.json: anillos en
deltas enteros, Canarias ya desplazada al suroeste de la península) y la dibuja en una proyección
equirectangular corregida por la latitud media. Los municipios se simplifican quitando los vértices a menos
de medio píxel del anterior, para que el mapa de 8.131 municipios pese poco.
"""
import json, math, pathlib
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / 'generales-2026' / 'data'
W = 800                      # ancho del SVG en píxeles de viewBox
LAT0 = 40.0                  # latitud de referencia para la corrección de la longitud
K = math.cos(math.radians(LAT0))
CAN = (10.2, 0.0)            # traslado extra de Canarias (grados): al mar entre Almería y Argelia, como el mapa en el móvil
es_can = lambda cod: cod[:2] in ('35', '38')


def _anillos(fichero):
    d = json.loads((DATA / fichero).read_text(encoding='utf-8'))
    out = {}
    for cod, partes in zip(d['cod'], d['poly']):
        dx, dy = CAN if es_can(cod) else (0, 0)
        rs = []
        for f in partes:
            x, y = f[0], f[1]
            r = [(x / d['S'] + dx, y / d['S'] + dy)]
            for k in range(2, len(f), 2):
                x += f[k]
                y += f[k + 1]
                r.append((x / d['S'] + dx, y / d['S'] + dy))
            rs.append(r)
        out[cod] = rs
    return out


_CACHE = {}


def geometria(nivel):
    if nivel not in _CACHE:
        _CACHE[nivel] = _anillos('provincias.json' if nivel == 'prov' else 'municipios.json')
    return _CACHE[nivel]


def _marco():
    pts = [p for rs in geometria('prov').values() for r in rs for p in r]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    M = 10   # margen en píxeles, para el recuadro de Canarias
    esc = (W - 2 * M) / ((x1 - x0) * K)
    return x0 - M / (K * esc), y1 + M / esc, esc, round((y1 - y0) * esc + 2 * M)


def _proy():
    x0, y1, esc, h = _marco()
    return (lambda p: ((p[0] - x0) * K * esc, (y1 - p[1]) * esc)), h


def _ruta(rs, P, tol, dec=1):
    out = []
    for r in rs:
        q, last = [], None
        for p in r:
            x, y = P(p)
            if last is None or abs(x - last[0]) + abs(y - last[1]) >= tol:
                q.append((x, y))
                last = (x, y)
        if len(q) >= 3:
            out.append('M' + 'L'.join(f'{x:.{dec}f},{y:.{dec}f}' for x, y in q) + 'Z')
    return ''.join(out)


def centro(cod, nivel='prov'):
    """Centro aproximado (media de los vértices del anillo mayor), ya proyectado."""
    P, _ = _proy()
    r = max(geometria(nivel)[cod], key=len)
    xs, ys = zip(*(P(p) for p in r))
    return sum(xs) / len(xs), sum(ys) / len(ys)


def mapa(colores, titulo, nivel='prov', etiquetas=None, trazo='var(--bg, #fff)', tol=None, xmlns=False):
    """SVG con cada territorio de `colores` ({código: color}) relleno de su color; los demás, en gris claro.
    `etiquetas`: {código: texto} que se escribe en el centro de cada provincia."""
    P, h = _proy()
    tol = tol if tol is not None else (1.2 if nivel == 'prov' else 1.5)
    por_color = {}   # un solo <path> por color: el SVG de 8.131 municipios pesa la mitad
    dec = 1 if nivel == 'prov' else 0
    for cod, rs in geometria(nivel).items():
        por_color.setdefault(colores.get(cod, '#e4e4e4'), []).append(_ruta(rs, P, tol, dec))
    g = [f'<path d="{"".join(ds)}" fill="{col}"/>' for col, ds in por_color.items()]
    sw = 0.6 if nivel == 'prov' else 0.15
    # Ceuta y Melilla apenas se ven a esta escala: un círculo de su color encima
    puntos = ''.join(f'<circle cx="{centro(c, nivel)[0]:.0f}" cy="{centro(c, nivel)[1]:.0f}" r="5" fill="{colores.get(c, "#e4e4e4")}" stroke="#fff" stroke-width="1"/>'
                     for c in geometria(nivel) if c in ('51', '52', '51001', '52001'))
    txt = []
    for cod, t in (etiquetas or {}).items():
        x, y = centro(cod)
        if cod in ('51', '52'):
            x += 12
        txt.append(f'<text x="{x:.0f}" y="{y + 4:.0f}" text-anchor="middle">{escape(str(t))}</text>')
    cpts = [P(p) for c, rs in geometria('prov').items() if es_can(c) for r in rs for p in r]
    bx0, by0 = min(p[0] for p in cpts) - 8, min(p[1] for p in cpts) - 8
    bx1, by1 = max(p[0] for p in cpts) + 8, max(p[1] for p in cpts) + 8
    caja = f'<path d="M{bx0:.0f},{by0:.0f}H{bx1:.0f}V{by1:.0f}H{bx0:.0f}Z" fill="none" stroke="#999" stroke-width="0.8"/>'
    ns = ' xmlns="http://www.w3.org/2000/svg"' if xmlns else ''
    return (f'<svg{ns} viewBox="0 0 {W} {h}" role="img" aria-label="{escape(titulo)}" class="graf mapa">'
            + caja + f'<g stroke="{trazo}" stroke-width="{sw}" stroke-linejoin="round">{"".join(g)}</g>' + puntos
            + (f'<g font-family="IBM Plex Mono, monospace" font-size="10" font-weight="600" fill="#111" paint-order="stroke" stroke="#fff" stroke-width="2.5">{"".join(txt)}</g>' if txt else '')
            + '</svg>')


def leyenda(items):
    """Leyenda en HTML: [(color, texto)]."""
    return ('<p class="leyenda-mapa">' + ' '.join(f'<span><i style="background:{c}"></i>{escape(t)}</span>' for c, t in items) + '</p>')


CSS = ('.mapa{width:100%;height:auto;display:block}.leyenda-mapa{font-family:var(--sans);font-size:.85rem;display:flex;flex-wrap:wrap;gap:.3rem 1rem;margin:.4rem 0 0}'
       '.leyenda-mapa i{display:inline-block;width:.8rem;height:.8rem;border-radius:2px;margin-right:.35rem;vertical-align:-1px}'
       'figure img.mapa{border:0}')
