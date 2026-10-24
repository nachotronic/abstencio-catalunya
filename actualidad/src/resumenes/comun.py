"""Piezas de resumen de fin de semana («Así queda el mapa», las coaliciones, las provincias en el filo).

Piezas reportajeadas que resumen lo ya publicado en Mapa Electoral con sus mismas cifras. Los gráficos son SVG estáticos
(sin JavaScript): se leen igual sin cargar nada y los buscadores ven el texto de cada barra. Colores de partido, siempre.
"""
import html
import json
import math
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[3]
SRC = RAIZ / 'actualidad' / 'src'
BASE = 'https://mapaelectoral.es/'

COLOR = {'PP': 'var(--pp)', 'PSOE': 'var(--psoe)', 'Vox': 'var(--vox)', 'Sumar': 'var(--sumar)', 'Podemos': 'var(--pod)',
         'ERC': 'var(--erc)', 'Junts': 'var(--junts)', 'PNV': 'var(--pnv)', 'EH Bildu': 'var(--bildu)', 'BNG': 'var(--bng)',
         'CC': 'var(--cc)', 'Otros': 'var(--otros)'}

CABEZA = '''<title>{titulo}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Literata:opsz,wght@7..72,400;7..72,600;7..72,800&family=Barlow+Semi+Condensed:wght@400;500;600&display=swap">
<style>
:root{
  --bg:#fbfaf8; --fg:#1d1a1c; --muted:#5d585b; --rule:#e2dddf; --grid:#ebe7e8; --acc:#a2275f;
  --serif:"Literata",Georgia,"Times New Roman",serif;
  --ui:"Barlow Semi Condensed","Arial Narrow",Arial,sans-serif;
  --pp:#1d84ce;--psoe:#e30613;--vox:#5ac035;--sumar:#a2275f;--pod:#6a3d9a;--erc:#f5b324;--junts:#20c0b2;--pnv:#2b8a3e;
  --bildu:#a5c400;--bng:#7ab8e6;--cc:#f7d417;--otros:#b7b1b4;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#18161a; --fg:#f1edef; --muted:#b5aeb2; --rule:#343036; --grid:#2c282e; --acc:#d0679a;
  --pp:#4fa8ea;--psoe:#ff5a5f;--vox:#74d651;--sumar:#d0679a;--pod:#9a72c9;--otros:#5a5458; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#18161a; --fg:#f1edef; --muted:#b5aeb2; --rule:#343036; --grid:#2c282e; --acc:#d0679a;
  --pp:#4fa8ea;--psoe:#ff5a5f;--vox:#74d651;--sumar:#d0679a;--pod:#9a72c9;--otros:#5a5458; color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.62}
main{max-width:46rem;margin:0 auto;padding-block:2.5rem 4rem;padding-inline:16px}
.draft{font-family:var(--ui);font-size:.85rem;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);border:1px solid var(--rule);display:inline-block;padding:.15rem .5rem;border-radius:3px}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.12;font-weight:800;text-wrap:balance;margin:.8rem 0 .9rem}
.dek{font-size:1.15rem;line-height:1.5;color:var(--muted);margin:0 0 1rem}
.byline{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);padding-top:.6rem}
h2{font-size:1.35rem;line-height:1.25;margin:2.4rem 0 .6rem;text-wrap:balance}
p{margin:0 0 1rem}
figure{margin:1.8rem 0 2rem;font-family:var(--ui)}
figcaption .t{font-weight:600;font-size:1.1rem;display:block;line-height:1.25}
figcaption .s{color:var(--muted);font-size:.98rem;display:block;margin-top:.15rem}
.src{color:var(--muted);font-size:.85rem;margin-top:.4rem}
.chart{margin-top:.7rem}
svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:var(--ui);fill:var(--muted);font-size:13px}
svg .lab{fill:var(--fg);font-weight:600}
.legend{display:flex;flex-wrap:wrap;gap:.4rem 1.1rem;font-size:.95rem;color:var(--fg);margin-top:.4rem}
.legend span{display:inline-flex;align-items:center;gap:.4rem}
.sw{width:14px;height:14px;border-radius:3px;display:inline-block}
.tbl{overflow-x:auto} table{border-collapse:collapse;font-family:var(--ui);font-size:.98rem;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.3rem .5rem;border-bottom:1px solid var(--rule)} td.n,th.n{text-align:right}
details{font-family:var(--ui);margin-top:.5rem} summary{cursor:pointer;color:var(--muted)}
a{color:var(--acc)} a:focus-visible,summary:focus-visible{outline:2px solid var(--acc);outline-offset:2px}
blockquote.cita{margin:1.8rem 0;padding:.2rem 0 .2rem 1.1rem;border-left:3px solid var(--rule)}
blockquote.cita p{font-size:1.12rem;line-height:1.5;margin:0 0 .4rem}
blockquote.cita footer{font-family:var(--ui);font-size:.95rem;color:var(--muted)}
.faq h3{font-size:1.05rem;margin:1.2rem 0 .3rem}
.resumen{font-family:var(--ui);border:1px solid var(--rule);border-radius:6px;padding:.8rem 1rem;margin:1.6rem 0}
.resumen b{display:block;margin-bottom:.3rem}
.resumen ul{margin:0;padding-left:1.1rem} .resumen li{margin-bottom:.25rem}
.foot{font-family:var(--ui);font-size:.95rem;color:var(--muted);border-top:1px solid var(--rule);margin-top:2.5rem;padding-top:.8rem}
@media (max-width:520px){body{font-size:17px}}
</style>
'''


def esc(t):
    return html.escape(str(t), quote=True)


def n(v, dec=0):
    """Número con punto de miles y coma decimal, como en el resto de piezas."""
    s = f'{v:,.{dec}f}'
    return s.replace(',', 'X').replace('.', ',').replace('X', '.')


def figura(titulo, sub, cuerpo, fuente, leyenda=None, tabla=None):
    ley = ''
    if leyenda:
        ley = '<div class="legend">' + ''.join(f'<span><i class="sw" style="background:{c}"></i>{esc(t)}</span>' for t, c in leyenda) + '</div>'
    tab = ''
    if tabla:
        cab, filas = tabla
        tab = ('<details><summary>Ver la tabla</summary><div class="tbl"><table><thead><tr>'
               + ''.join(f'<th{" class=\"n\"" if i else ""}>{esc(h)}</th>' for i, h in enumerate(cab)) + '</tr></thead><tbody>'
               + ''.join('<tr>' + ''.join(f'<td{" class=\"n\"" if i else ""}>{esc(c)}</td>' for i, c in enumerate(f)) + '</tr>' for f in filas)
               + '</tbody></table></div></details>')
    return (f'<figure>\n<figcaption><span class="t">{esc(titulo)}</span><span class="s">{esc(sub)}</span></figcaption>\n'
            f'<div class="chart">{cuerpo}</div>\n{ley}\n<div class="src">{fuente}</div>{tab}\n</figure>\n')


def barras(filas, maximo, etiqueta, W=640, ml=150, alto=26, fmt=None, linea=None):
    """Barras horizontales. filas: [(nombre, valor, color, texto_al_final)]."""
    fmt = fmt or (lambda v: n(v))
    H = alto * len(filas) + 8
    x = lambda v: ml + v / maximo * (W - ml - 70)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom, v, col, txt) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + alto / 2 + 4:.1f}" text-anchor="end" class="lab">{esc(nom)}</text>')
        out.append(f'<rect x="{ml}" y="{y + 4}" width="{max(1.5, x(v) - ml):.1f}" height="{alto - 9}" fill="{col}" rx="2"><title>{esc(nom)}: {esc(txt or fmt(v))}</title></rect>')
        out.append(f'<text x="{x(v) + 6:.1f}" y="{y + alto / 2 + 4:.1f}">{esc(txt or fmt(v))}</text>')
    if linea is not None:
        out.append(f'<line x1="{x(linea[0]):.1f}" x2="{x(linea[0]):.1f}" y1="0" y2="{H}" stroke="var(--fg)" stroke-dasharray="3 3"/>'
                   f'<text x="{x(linea[0]) + 4:.1f}" y="{H - 2}" class="lab">{esc(linea[1])}</text>')
    out.append('</svg>')
    return ''.join(out)


def pares(filas, maximo, etiqueta, nombres, W=640, ml=110):
    """Dos barras por fila (por ejemplo, 2019 y 2023): filas = [(nombre, v1, v2, color)]. La primera, más clara."""
    alto = 40
    H = alto * len(filas) + 30
    x = lambda v: ml + v / maximo * (W - ml - 70)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{esc(etiqueta)}">']
    for i, (nom, a, b, col) in enumerate(filas):
        y = 4 + i * alto
        out.append(f'<text x="{ml - 8}" y="{y + 22}" text-anchor="end" class="lab">{esc(nom)}</text>')
        for k, (v, op) in enumerate(((a, .38), (b, 1))):
            yy = y + 4 + k * 16
            out.append(f'<rect x="{ml}" y="{yy}" width="{max(1.5, x(v) - ml):.1f}" height="13" fill="{col}" fill-opacity="{op}" rx="2">'
                       f'<title>{esc(nom)}, {esc(nombres[k])}: {n(v)}</title></rect>')
            out.append(f'<text x="{x(v) + 6:.1f}" y="{yy + 11}">{n(v)}{" (" + nombres[k] + ")" if i == 0 else ""}</text>')
    out.append('</svg>')
    return ''.join(out)


def cuadrados(grupos, etiqueta, por_fila=16, lado=22):
    """Un cuadrado por escaño, agrupados: grupos = [(nombre, n, color, opacidad)]."""
    out, y = [], 0
    filas_svg = []
    for nom, k, col, op in grupos:
        filas_svg.append(f'<text x="0" y="{y + 14}" class="lab">{esc(nom)} · {k}</text>')
        y += 22
        for i in range(k):
            cx, cy = (i % por_fila) * (lado + 4), y + (i // por_fila) * (lado + 4)
            filas_svg.append(f'<rect x="{cx}" y="{cy}" width="{lado}" height="{lado}" rx="3" fill="{col}" fill-opacity="{op}"><title>{esc(nom)}</title></rect>')
        y += math.ceil(k / por_fila) * (lado + 4) + 12
    W = por_fila * (lado + 4)
    out.append(f'<svg viewBox="0 0 {max(W, 420)} {y}" style="max-width:{max(W, 420)}px" role="img" aria-label="{esc(etiqueta)}">')
    out += filas_svg
    out.append('</svg>')
    return ''.join(out)


def mapa_provincias(colores, titulos, etiqueta, opacidad=None):
    """Mapa de provincias (geometría de la portada, generales-2026/data/provincias.json; Canarias en recuadro)."""
    g = json.load(open(RAIZ / 'generales-2026/data/provincias.json'))
    S, kx = g['S'], math.cos(math.radians(39.5))
    anillos = []
    for c, partes in zip(g['cod'], g['poly']):
        for f in partes:
            x, y, pts = f[0], f[1], [(f[0], f[1])]
            for k in range(2, len(f), 2):
                x += f[k]; y += f[k + 1]; pts.append((x, y))
            anillos.append((c, [(px / S * kx, -py / S) for px, py in pts]))
    xs = [x for _, r in anillos for x, _ in r]; ys = [y for _, r in anillos for _, y in r]
    W = 640; e = W / (max(xs) - min(xs)); H = round((max(ys) - min(ys)) * e)
    caminos = {}
    for c, r in anillos:
        d, ult = '', None
        for x, y in r:
            q = (round((x - min(xs)) * e, 1), round((y - min(ys)) * e, 1))
            if ult and abs(q[0] - ult[0]) + abs(q[1] - ult[1]) < .8:
                continue
            d += ('L' if d else 'M') + f'{q[0]:g},{q[1]:g}'; ult = q
        caminos[c] = caminos.get(c, '') + d + 'Z'
    out = ''
    for c, d in caminos.items():
        op = (opacidad or {}).get(c, 1)
        out += f'<path d="{d}" fill="{colores.get(c, "var(--otros)")}" fill-opacity="{op}"><title>{esc(titulos.get(c, ""))}</title></path>'
    cx = [(x - min(xs)) * e for c, r in anillos if c in ('35', '38') for x, _ in r]
    cy = [(y - min(ys)) * e for c, r in anillos if c in ('35', '38') for _, y in r]
    marco = f'<rect x="{min(cx) - 8:.0f}" y="{min(cy) - 8:.0f}" width="{max(cx) - min(cx) + 16:.0f}" height="{max(cy) - min(cy) + 16:.0f}" fill="none" stroke="var(--rule)"/>'
    return (f'<svg viewBox="-2 -2 {W + 4} {H + 4}" role="img" aria-label="{esc(etiqueta)}">'
            f'{marco}<g stroke="var(--bg)" stroke-width=".8" stroke-linejoin="round">{out}</g></svg>')


def pieza(slug, titulo_corto, h1, dek, fecha_larga, cuerpo, preguntas, enlaces, foot):
    faq = ('<h2>Preguntas frecuentes</h2>\n<div class="faq">'
           + ''.join(f'<h3>{esc(q)}</h3><p>{r}</p>' for q, r in preguntas) + '</div>\n')
    htmlp = (CABEZA.replace('{titulo}', esc(titulo_corto)) + '<main>\n<span class="draft">Borrador para revisión · no publicado</span>\n'
             f'<h1>{h1}</h1>\n<p class="dek">{dek}</p>\n<div class="byline">Nacho G. del Álamo · {fecha_larga}</div>\n'
             + cuerpo + faq + f'<p>{enlaces}</p>' + f'<div class="foot">{foot}</div>\n</main>\n'
             '<script>/* Gráficos en SVG estático: sin interacción */</script>\n')
    (SRC / f'{slug}.html').write_text(htmlp, encoding='utf-8')
    print('escrito', slug, len(htmlp))
