"""Cards con imagen en los «Sigue leyendo» de las páginas de /encuestas/ (Nacho, 28-10-2026).

Pasa por una página ya generada y, en cada <ul class="sigue">, pone arriba de cada enlace la imagen de la página
de destino: la primera <img> local (la ilustración de cabecera de una pieza) o, si no tiene, su og:image. Usa la
copia WebP de 640 px de img/movil/ (src/movil.py) para que pese poco. Es idempotente: la lista queda como
<ul class="sigue cards"> y no se vuelve a tocar.
"""
import html as html_mod
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
try:
    import movil
except ImportError:   # sin Pillow: cards con la imagen original
    movil = None

BASE = 'https://mapaelectoral.es/'
LISTA = re.compile(r'<ul class="sigue">(.*?)</ul>', re.S)
ENLACE = re.compile(r'<li><a href="([^"]+)">')
CSS = ('<style id="sigue-cards">.sigue.cards{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}'
       '.sigue.cards a{padding:0;overflow:hidden;height:100%}.sigue.cards img{display:block;width:100%;height:auto;aspect-ratio:1200/630;object-fit:cover;'
       'background:var(--grid)}.sigue.cards .txt{display:block;padding:10px 14px 12px}</style>')


def destino(pagina, href):
    """Fichero de la página a la que lleva href desde pagina, o None si es externa o no existe."""
    if href.startswith(('http', '#', 'mailto:')):
        return None
    f = (pagina.parent / href.split('#')[0].split('?')[0]).resolve()
    if f.is_dir() or href.endswith('/'):
        f = f / 'index.html'
    return f if f.exists() and ROOT in f.parents else None


def imagen(f):
    """Ruta desde la raíz de la imagen que representa la página f."""
    t = f.read_text(encoding='utf-8')
    for src in re.findall(r'<img\b[^>]*?\bsrc="([^"]+)"', t):
        if not src.startswith(('http', 'data:', '/')) and src.lower().endswith(('.jpg', '.jpeg', '.png')):
            p = (f.parent / src).resolve()
            if p.exists():
                return p.relative_to(ROOT).as_posix()
    m = re.search(r'<meta property="og:image" content="([^"]+)"', t)
    if m and m.group(1).startswith(BASE):
        p = ROOT / m.group(1)[len(BASE):].split('?')[0]
        if p.exists():
            return p.relative_to(ROOT).as_posix()
    return None


def procesa(pagina):
    pagina = pathlib.Path(pagina).resolve()
    t = pagina.read_text(encoding='utf-8')
    rel = '../' * len(pagina.parent.relative_to(ROOT).parts)

    def lista(m):
        def li(mm):
            f = destino(pagina, html_mod.unescape(mm.group(1)))
            src = imagen(f) if f else None
            if src and movil:
                src = movil.miniatura(src) or src
            img = f'<img src="{rel}{src}" alt="" loading="lazy" width="640" height="336">' if src else ''
            return f'<li><a href="{mm.group(1)}">{img}<span class="txt">'
        cuerpo = ENLACE.sub(li, m.group(1)).replace('</b></a></li>', '</b></span></a></li>')
        return f'<ul class="sigue cards">{cuerpo}</ul>'

    n = LISTA.sub(lista, t)
    if n != t:
        if 'id="sigue-cards"' not in n:
            n = n.replace('</head>', CSS + '\n</head>', 1)
        pagina.write_text(n, encoding='utf-8')


if __name__ == '__main__':
    for a in sys.argv[1:]:
        procesa(a)
