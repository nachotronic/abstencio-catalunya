"""Gráficos SVG estáticos del Atlas: se dibujan al generar la página, sin JavaScript, para que se lean en cualquier
navegador, en buscadores y en asistentes. Colores con variables CSS de la página (modo claro y oscuro)."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape

W = 680
ANYO = {'2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015', '2016_06': '2016',
        '2019_04': 'abr. 2019', '2019_11': 'nov. 2019', '2023_07': '2023'}


def num(x, d=1):
    """43.2 -> '43,2'; 1340 -> '1.340'."""
    if isinstance(x, int) or d == 0:
        # redondeo «hacia arriba» en el 5, como en las tablas (round() de Python redondea 36,5 a 36)
        return f'{int(Decimal(str(x)).quantize(Decimal(1), ROUND_HALF_UP)):,}'.replace(',', '.')
    return f'{x:.{d}f}'.replace('.', ',')


def yl(xs):
    """['a', 'b', 'c'] -> 'a, b y c'."""
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ', '.join(xs[:-1]) + ' y ' + xs[-1]


def _svg(h, titulo, cuerpo):
    return (f'<svg viewBox="0 0 {W} {h}" role="img" aria-label="{escape(titulo)}" class="graf" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="var(--mono)" font-size="12">{cuerpo}</svg>')


def lineas(series, elecciones, titulo, ymin=0, ymax=70, unidad='%', etiquetas=None):
    """series: [(nombre, {eleccion: valor}, color_var, destacado)]. Etiqueta el último punto de cada serie."""
    x0, x1, y0, y1 = 48, W - 150, 20, 250
    X = lambda i: x0 + i * (x1 - x0) / (len(elecciones) - 1)
    Y = lambda v: y1 - (v - ymin) / (ymax - ymin) * (y1 - y0)
    out = []
    for t in range(ymin, ymax + 1, 10):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="var(--rule)"/>'
                   f'<text x="{x0 - 8}" y="{Y(t) + 4:.1f}" text-anchor="end" fill="var(--muted)">{t}{unidad if t == ymax else ""}</text>')
    for i, e in enumerate(elecciones):
        et = (etiquetas or {}).get(e, ANYO.get(e, e))
        if et:
            out.append(f'<text x="{X(i):.1f}" y="{y1 + 20}" text-anchor="middle" fill="var(--muted)">{et}</text>')
    usados = []
    for nombre, vals, color, fuerte in series:
        pts = [(X(i), Y(vals[e])) for i, e in enumerate(elecciones) if vals.get(e) is not None]
        out.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{color}" '
                   f'stroke-width="{3 if fuerte else 2}"{"" if fuerte else " stroke-dasharray=\"5 4\""}/>')
        out.extend(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{3.5 if fuerte else 2.5}" fill="{color}"/>' for a, b in pts)
        ly = pts[-1][1]
        while any(abs(ly - u) < 16 for u in usados):
            ly += 16
        usados.append(ly)
        out.append(f'<text x="{pts[-1][0] + 10:.1f}" y="{ly + 4:.1f}" fill="{color}" font-weight="600">{escape(nombre)} '
                   f'{num(vals[elecciones[-1]])}%</text>')
    return _svg(y1 + 32, titulo, ''.join(out))


def barras_previsto(filas, titulo, destacado):
    """filas: [{'municipio', 'real', 'previsto'}]. Punto = real, marca = previsto, línea entre ambos."""
    x0, x1 = 210, W - 60
    lo = min(min(f['real'], f['previsto']) for f in filas) // 10 * 10
    hi = max(max(f['real'], f['previsto']) for f in filas) // 10 * 10 + 10
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    h, paso = 40 + 26 * len(filas), 26
    out = [f'<text x="{x0}" y="14" fill="var(--muted)">○ previsto por su perfil   ● real</text>']
    for t in range(int(lo), int(hi) + 1, 10):
        out.append(f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="24" y2="{h - 18}" stroke="var(--rule)"/>'
                   f'<text x="{X(t):.1f}" y="{h - 4}" text-anchor="middle" fill="var(--muted)">{t}%</text>')
    for i, f in enumerate(filas):
        y = 38 + i * paso
        c = 'var(--accent)' if f['municipio'] == destacado else 'var(--fg)'
        out.append(f'<text x="{x0 - 10}" y="{y + 4}" text-anchor="end" fill="{c}"{" font-weight=\"600\"" if c != "var(--fg)" else ""}>{escape(f["municipio"])}</text>'
                   f'<line x1="{X(f["previsto"]):.1f}" x2="{X(f["real"]):.1f}" y1="{y}" y2="{y}" stroke="{c}" stroke-width="2"/>'
                   f'<circle cx="{X(f["previsto"]):.1f}" cy="{y}" r="5" fill="var(--surface)" stroke="{c}" stroke-width="1.5"/>'
                   f'<circle cx="{X(f["real"]):.1f}" cy="{y}" r="5" fill="{c}"/>')
    return _svg(h, titulo, ''.join(out))


def divergente(filas, clave, etiqueta, titulo, sufijo=' p.'):
    """Barras a izquierda y derecha de cero. filas: [{etiqueta: str, clave: float}]."""
    xm, ancho = 340, 260
    m = max(abs(f[clave]) for f in filas)
    paso = 18
    h = 30 + paso * len(filas)
    out = [f'<line x1="{xm}" x2="{xm}" y1="8" y2="{h - 6}" stroke="var(--muted)"/>',
           f'<text x="{xm - 8}" y="14" text-anchor="end" fill="var(--muted)">menos que su provincia</text>',
           f'<text x="{xm + 8}" y="14" fill="var(--muted)">más que su provincia</text>']
    for i, f in enumerate(filas):
        y = 26 + i * paso
        v = f[clave]
        w = abs(v) / m * ancho
        x = xm if v >= 0 else xm - w
        col = 'var(--pp)' if v >= 0 else 'var(--accent2)'
        tx = xm - 8 if v >= 0 else xm + 8
        anc = 'end' if v >= 0 else 'start'
        out.append(f'<rect x="{x:.1f}" y="{y - 6}" width="{w:.1f}" height="12" fill="{col}"/>'
                   f'<text x="{tx}" y="{y + 4}" text-anchor="{anc}" fill="var(--fg)" font-size="11">{escape(f[etiqueta])}</text>'
                   f'<text x="{(x + w + 6) if v >= 0 else (x - 6):.1f}" y="{y + 4}" text-anchor="{"start" if v >= 0 else "end"}" '
                   f'fill="var(--muted)" font-size="11">{"+" if v > 0 else ""}{num(v)}{sufijo}</text>')
    return _svg(h, titulo, ''.join(out))


def barras_agrupadas(grupos, series, titulo, ymax=60):
    """grupos: [(etiqueta, {serie: valor})]; series: [(serie, color)]. Barras verticales agrupadas."""
    x0, x1, y0, y1 = 40, W - 10, 30, 230
    Y = lambda v: y1 - v / ymax * (y1 - y0)
    gw = (x1 - x0) / len(grupos)
    bw = min(34, (gw - 20) / len(series))
    out = []
    for t in range(0, ymax + 1, 10):
        out.append(f'<line x1="{x0}" x2="{x1}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="var(--rule)"/>'
                   f'<text x="{x0 - 6}" y="{Y(t) + 4:.1f}" text-anchor="end" fill="var(--muted)">{t}</text>')
    for j, (s, col) in enumerate(series):
        out.append(f'<rect x="{x0 + j * 130}" y="4" width="12" height="12" fill="{col}"/><text x="{x0 + 18 + j * 130}" y="14" fill="var(--fg)">{escape(s)}</text>')
    for i, (g, vals) in enumerate(grupos):
        gx = x0 + i * gw + (gw - bw * len(series)) / 2
        for j, (s, col) in enumerate(series):
            v = vals.get(s, 0) or 0
            out.append(f'<rect x="{gx + j * bw:.1f}" y="{Y(v):.1f}" width="{bw - 3:.1f}" height="{y1 - Y(v):.1f}" fill="{col}"/>'
                       f'<text x="{gx + j * bw + (bw - 3) / 2:.1f}" y="{Y(v) - 4:.1f}" text-anchor="middle" font-size="11" fill="var(--fg)">{num(v, 0) if v >= 1 else ""}</text>')
        out.append(f'<text x="{x0 + i * gw + gw / 2:.1f}" y="{y1 + 18}" text-anchor="middle" fill="var(--muted)">{escape(g)}</text>')
    return _svg(y1 + 28, titulo, ''.join(out))


def margenes(filas, titulo):
    """Barras horizontales con los votos que faltaron para el último escaño."""
    x0, x1 = 230, W - 70
    m = max(f['votos_que_faltaban'] for f in filas)
    paso = 24
    h = 20 + paso * len(filas)
    out = []
    for i, f in enumerate(filas):
        y = 18 + i * paso
        w = f['votos_que_faltaban'] / m * (x1 - x0)
        out.append(f'<text x="{x0 - 10}" y="{y + 4}" text-anchor="end" fill="var(--fg)">{escape(f["provincia"])}</text>'
                   f'<rect x="{x0}" y="{y - 7}" width="{w:.1f}" height="14" fill="var(--accent)"/>'
                   f'<text x="{x0 + w + 6:.1f}" y="{y + 4}" fill="var(--muted)">{num(f["votos_que_faltaban"], 0)}</text>')
    return _svg(h, titulo, ''.join(out))
