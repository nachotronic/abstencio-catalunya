"""Carga diferida de los mapas interactivos (deck.gl) para que el texto se pinte primero.

Las páginas con mapa (portada, piezas de Cataluña y de Girona en los dos idiomas) llevan al final
deck.gl (~1 MB), el código del mapa y, en las piezas en 3D, varios MB de geometría dentro del propio
<script>. Mientras el navegador los descarga y ejecuta, el hilo principal está ocupado y el texto,
las tablas y los titulares tardan más en estar listos (LCP y TBT altos).

Este script pasa por esas páginas ya generadas y:

- cambia el tipo de los <script> del mapa (deck.gl y todo lo que va detrás, salvo la analítica y el
  JSON-LD) a `text/x-mapa`, para que el navegador no los descargue ni los ejecute al cargar;
- añade un cargador pequeño que los ejecuta en el mismo orden cuando la página ya ha cargado y el mapa
  está a menos de una pantalla, o antes si el lector toca, hace clic o usa el teclado sobre el mapa;
- deja un aviso «Cargando el mapa…» encima del hueco del mapa hasta que aparece el lienzo (o 15 s
  después de ejecutar el código del mapa, por si el navegador no tiene WebGL y sale el aviso de error).

El hueco del mapa ya tiene su alto fijado en el CSS, así que no hay saltos de diseño (CLS).
Es idempotente. src/seo.py lo llama al terminar; también se puede lanzar solo:

    python3 src/diferido.py
"""
import pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
# página -> contenedor del mapa (el que se vigila para saber si está a la vista)
PAGINAS = {'index.html': '#mapa', 'abstencion.html': '#scrolly', 'ca.html': '#scrolly',
           'girona.html': '#scrolly', 'girona-ca.html': '#scrolly'}
TIPO = 'text/x-mapa'
DECK = '<script src="https://unpkg.com/deck.gl'

CARGADOR = """<script id="mapa-diferido">
// Carga diferida del mapa (src/diferido.py): los <script type="text/x-mapa"> se ejecutan en orden cuando la
// página ya ha cargado y el mapa está cerca de la pantalla, o en cuanto el lector interactúa con él.
(function () {
  var C = document.querySelector('%(sel)s'), hecho = false;
  function corre() {
    if (hecho) return; hecho = true;
    var cola = [].slice.call(document.querySelectorAll('script[type="%(tipo)s"]'));
    (function sig() {
      var v = cola.shift();
      if (!v) { setTimeout(function () { var a = C && C.querySelector('.mapa-carga'); if (a) a.remove(); }, 15000); return; }
      var s = document.createElement('script');
      for (var i = 0; i < v.attributes.length; i++) { var a = v.attributes[i]; if (a.name !== 'type') s.setAttribute(a.name, a.value); }
      if (v.src) { s.async = false; s.onload = s.onerror = sig; } else s.text = v.text;
      v.parentNode.replaceChild(s, v);
      if (!v.src) sig();
    })();
  }
  function pronto() { (window.requestIdleCallback || function (f) { setTimeout(f, 1); })(corre, { timeout: 1500 }); }
  if (!C || !('IntersectionObserver' in window)) { addEventListener('load', pronto); return; }
  ['pointerdown', 'keydown', 'focusin', 'wheel', 'touchstart'].forEach(function (e) { C.addEventListener(e, corre, { once: true, passive: true }); });
  function vigila() {
    var io = new IntersectionObserver(function (es) { if (es.some(function (e) { return e.isIntersecting; })) { io.disconnect(); pronto(); } }, { rootMargin: '100%% 0px' });
    io.observe(C);
  }
  if (document.readyState === 'complete') vigila(); else addEventListener('load', vigila);
  // aviso mientras no hay lienzo (lo crea este script y no el HTML, para no tocar el cuerpo que compara src/build_ca.py)
  var H = C.querySelector('#map, #deck'), av = document.createElement('p');
  av.className = 'mapa-carga'; av.textContent = document.documentElement.lang === 'ca' ? 'Carregant el mapa…' : 'Cargando el mapa…';
  if (H) H.appendChild(av);
  if (H) new MutationObserver(function (m, o) { if (C.querySelector('canvas')) { av.remove(); o.disconnect(); } }).observe(C, { childList: true, subtree: true });
})();
</script>
"""
CSS = ('<style id="mapa-diferido-css">.mapa-carga{position:absolute;left:50%%;top:50%%;transform:translate(-50%%,-50%%);margin:0;'
       'font:14px/1.3 system-ui,sans-serif;color:#6b6b6b;pointer-events:none;z-index:1}</style>')


def procesa(f, sel):
    s0 = s = f.read_text(encoding='utf-8')
    if DECK not in s:
        return False
    if 'id="mapa-diferido"' not in s:
        i, j = s.index(DECK), s.rindex('</body>')
        cola = s[i:j]

        def marca(m):
            t = m.group(0)
            if re.search(r'\btype=|data-cf-beacon', t):   # JSON-LD, módulos y la analítica de Cloudflare se quedan como están
                return t
            return t[:-1] + f' type="{TIPO}">'
        cola = re.sub(r'<script\b[^>]*>', marca, cola)
        s = s[:i] + cola + CARGADOR % {'sel': sel, 'tipo': TIPO} + s[j:]
    if 'id="mapa-diferido-css"' not in s:
        s = s.replace('</head>', '<link rel="preconnect" href="https://unpkg.com">\n' + CSS % () + '\n</head>', 1)
    if s != s0:
        f.write_text(s, encoding='utf-8')
        return True
    return False


def main():
    n = sum(procesa(ROOT / p, sel) for p, sel in PAGINAS.items() if (ROOT / p).exists())
    print(f'diferido: {n} páginas con el mapa en carga diferida')


if __name__ == '__main__':
    main()
