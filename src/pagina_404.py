"""Página 404 («Voto nulo») y el índice del buscador de municipios y barrios.

Escribe 404.html en la raíz (GitHub Pages la sirve para cualquier ruta que no exista)
y municipio/buscador.json, que la 404 carga solo cuando el lector usa el buscador.
Se ejecuta a mano después de regenerar las fichas: python3 src/pagina_404.py
"""
import glob
import json
import os
import re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIGAS = re.compile(r'"BreadcrumbList", "itemListElement": (\[.*?\])\}</script>')


def indice():
    filas = []
    for f in sorted(glob.glob(os.path.join(RAIZ, 'municipio', '*', '*', '**', 'index.html'), recursive=True)):
        with open(f, encoding='utf-8') as fh:
            m = MIGAS.search(fh.read(20000))
        if not m:
            continue
        migas = json.loads(m.group(1))
        if len(migas) < 4:
            continue
        ruta = migas[-1]['item'].replace('https://mapaelectoral.es', '')
        nombre = migas[-1]['name']
        contexto = migas[-2]['name'] if len(migas) == 5 else migas[2]['name']
        filas.append([nombre, contexto, ruta, 1 if len(migas) == 5 else 0])
    return filas


def paginas_totales():
    n = 0
    for f in glob.glob(os.path.join(RAIZ, '**', 'sitemap*.xml'), recursive=True):
        if f.endswith('sitemap_index.xml') or 'noticias' in f:
            continue
        with open(f, encoding='utf-8') as fh:
            n += fh.read().count('<loc>')
    return n


NAV = [('/', 'Mapa de resultados'), ('/elecciones/', 'Por territorio'), ('/municipio/', 'Municipios'), ('/municipio/barrios/', 'Barrios'),
       ('/temas/', 'Temas'), ('/encuestas/', 'Encuestas'), ('/atlas/', 'Atlas'), ('/actualidad/', 'Actualidad'),
       ('/actualidad/#comunidades', 'Comunidades'), ('/actualidad/#historia', 'Historia electoral'), ('/sobre-mi.html', 'Sobre mí')]


def miles(n):
    return f'{n:,}'.replace(',', '.')


def pagina(total):
    nav = ('<nav class="site" aria-label="Secciones del sitio"><a class="marca" href="/">Mapa Electoral</a>'
           + ''.join(f'<a href="{h}">{t}</a>' for h, t in NAV) + '</nav>')
    return PLANTILLA.replace('{{NAV}}', nav).replace('{{TOTAL}}', miles(total))


PLANTILLA = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Voto nulo: esta página no está en el censo · Mapa Electoral</title>
<meta name="description" content="Error 404: la página que buscas no existe o se ha mudado. Busca tu municipio o tu barrio.">
<meta name="robots" content="noindex, follow">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{--bg:#faf8f3;--surface:#fff;--fg:#1a1a1a;--muted:#5f5d58;--rule:#e3dfd6;--accent:#b3261e;--sobre:#efe3c4;--sobre2:#d9c79c;--urna:#eef3f6;--urna2:#9fb3c0;
  --sans:"IBM Plex Sans",system-ui,sans-serif;--body:"Newsreader",Georgia,serif;--mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#15161a;--surface:#1e2025;--fg:#ecebe7;--muted:#a5a39b;--rule:#33363d;--accent:#ff8a80;--sobre:#cdbb8f;--sobre2:#a8956a;--urna:#262a31;--urna2:#56636e;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#15161a;--surface:#1e2025;--fg:#ecebe7;--muted:#a5a39b;--rule:#33363d;--accent:#ff8a80;--sobre:#cdbb8f;--sobre2:#a8956a;--urna:#262a31;--urna2:#56636e;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.55 var(--body);padding:0 16px 48px}
nav.site{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 16px;max-width:72ch;margin:0 auto 1.4rem;padding:12px 0 10px;border-bottom:1px solid var(--rule);font:500 14px/1.4 var(--sans)}
nav.site a{color:var(--muted);text-decoration:none}
nav.site a:hover{color:var(--accent)}
.marca{color:var(--fg)!important;font-weight:700;letter-spacing:.06em;text-transform:uppercase;font-size:13px;margin-right:6px}
@media (max-width:760px){nav.site{flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;scrollbar-width:none}}
main{max-width:640px;margin:0 auto}
.escena{display:flex;justify-content:center;margin:1.5rem 0 .5rem}
.escena svg{width:min(260px,70vw);height:auto;overflow:visible}
.urna-cuerpo{fill:var(--urna);stroke:var(--urna2);stroke-width:2}
.urna-tapa{fill:var(--surface);stroke:var(--urna2);stroke-width:2}
.ranura{fill:var(--fg);opacity:.75}
.sobre rect{fill:var(--sobre);stroke:var(--sobre2);stroke-width:1.5}
.sobre path{fill:none;stroke:var(--sobre2);stroke-width:1.5}
.sobre text{font:600 22px var(--mono);fill:var(--fg);letter-spacing:.08em}
.sello{font:700 26px var(--sans);fill:none;stroke:var(--accent);stroke-width:1.4;letter-spacing:.12em}
.sello-marco{fill:none;stroke:var(--accent);stroke-width:3}
.sobre{animation:cae 2.4s cubic-bezier(.5,0,.4,1) .3s both}
.sello-g{transform-origin:130px 62px;animation:sella .35s ease-out 2.35s both}
@keyframes cae{0%{transform:translate(0,-70px) rotate(-8deg);opacity:0}15%{opacity:1}55%{transform:translate(0,22px) rotate(0)}63%{transform:translate(0,4px) rotate(3deg)}75%{transform:translate(0,10px) rotate(-1deg)}100%{transform:translate(0,8px) rotate(-4deg)}}
@keyframes sella{0%{transform:scale(2.4) rotate(-14deg);opacity:0}100%{transform:scale(1) rotate(-14deg);opacity:.92}}
@media (prefers-reduced-motion:reduce){.sobre,.sello-g{animation:none}.sello-g{transform:rotate(-14deg);opacity:.92}}
.kicker{font:600 13px/1.3 var(--sans);letter-spacing:.08em;text-transform:uppercase;color:var(--accent);text-align:center;margin:0}
h1{font:600 clamp(40px,9vw,64px)/1.05 var(--body);text-align:center;margin:.2em 0 .3em;letter-spacing:-.01em}
.lead{text-align:center;color:var(--muted);margin:0 auto 1.6rem;max-width:34em}
.lead a{color:var(--fg)}
.quizas{text-align:center;font:500 16px var(--sans);margin:0 0 1.4rem}
.quizas a{color:var(--accent);font-weight:700}
.acta{font:14px/1.6 var(--mono);background:var(--surface);border:1px solid var(--rule);border-radius:6px;padding:16px 18px;margin:0 0 2rem;position:relative}
.acta h2{font:600 12px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 8px}
.acta dl{display:grid;grid-template-columns:1fr auto;gap:2px 16px;margin:0}
.acta dt{color:var(--muted)}
.acta dd{margin:0;text-align:right;font-weight:500}
.acta .nulo{color:var(--accent)}
.acta p{margin:10px 0 0;font:italic 15px var(--body);color:var(--muted)}
.busca label{display:block;font:600 15px var(--sans);margin-bottom:6px}
.busca input{width:100%;font:17px var(--sans);padding:12px 14px;border:1.5px solid var(--rule);border-radius:6px;background:var(--surface);color:var(--fg)}
.busca input:focus{outline:none;border-color:var(--accent)}
.busca ul{list-style:none;margin:6px 0 0;padding:0;border-radius:6px;overflow:hidden}
.busca li a{display:flex;justify-content:space-between;gap:12px;padding:9px 14px;text-decoration:none;color:var(--fg);font:16px var(--sans);border-bottom:1px solid var(--rule);background:var(--surface)}
.busca li a:hover,.busca li a:focus{background:var(--bg);color:var(--accent)}
.busca li span{color:var(--muted);font-size:14px}
.busca .vacio{font:15px var(--sans);color:var(--muted);padding:8px 2px}
.salidas{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:2rem 0 0;padding:0;list-style:none}
.salidas a{display:block;padding:12px 14px;border:1px solid var(--rule);border-radius:6px;text-decoration:none;color:var(--fg);font:600 15px/1.3 var(--sans);background:var(--surface);height:100%}
.salidas a:hover{border-color:var(--accent);color:var(--accent)}
.salidas small{display:block;font-weight:400;color:var(--muted);font-size:13px;margin-top:3px}
</style>
</head>
<body>
{{NAV}}
<main>
<div class="escena" aria-hidden="true">
<svg viewBox="0 0 260 230">
  <g class="sobre"><rect x="80" y="18" width="100" height="66" rx="3"/><path d="M80 21l50 34 50-34"/>
    <g class="sello-g"><rect class="sello-marco" x="88" y="44" width="84" height="34" rx="4"/><text class="sello" x="130" y="71" text-anchor="middle">NULO</text></g></g>
  <rect class="urna-cuerpo" x="40" y="104" width="180" height="116" rx="6"/>
  <rect class="urna-tapa" x="30" y="92" width="200" height="16" rx="4"/>
  <rect class="ranura" x="88" y="97" width="84" height="5" rx="2.5"/>
  <text x="130" y="176" text-anchor="middle" style="font:500 52px var(--mono);letter-spacing:.06em;fill:var(--fg)">404</text>
  <text x="130" y="204" text-anchor="middle" style="font:600 12px var(--sans);letter-spacing:.24em;fill:var(--muted)">CONGRESO</text>
</svg>
</div>
<p class="kicker">Página no encontrada · Escrutado el 100 %</p>
<h1>Voto nulo</h1>
<p class="lead">La página que buscas no figura en el censo. Puede que se haya mudado de barrio: las fichas de municipio viven ahora en <a href="/municipio/">/municipio/</a>.</p>
<p class="quizas" id="quizas" hidden></p>

<section class="acta" aria-labelledby="h-acta">
  <h2 id="h-acta">Acta de escrutinio de esta dirección</h2>
  <dl>
    <dt>Electores (páginas del sitio)</dt><dd>{{TOTAL}}</dd>
    <dt>Votantes</dt><dd>1</dd>
    <dt>Votos válidos</dt><dd>0</dd>
    <dt>Votos nulos</dt><dd class="nulo">1 (100,0 %)</dd>
    <dt>Participación</dt><dd>100,0 %</dd>
  </dl>
  <p>Récord histórico de participación. Lástima del resultado.</p>
</section>

<form class="busca" role="search" onsubmit="return false">
  <label for="q">Vota de nuevo: busca tu municipio o tu barrio</label>
  <input id="q" type="search" autocomplete="off" placeholder="Por ejemplo, Getafe o Lavapiés" aria-describedby="h-res" aria-controls="res">
  <ul id="res" aria-live="polite"></ul>
  <p id="h-res" class="vacio" hidden></p>
</form>

<ul class="salidas">
  <li><a href="/">Mapa de resultados<small>España, calle a calle</small></a></li>
  <li><a href="/elecciones/elecciones-29n-2026/">Elecciones del 29N<small>Escaños, fecha y campaña</small></a></li>
  <li><a href="/encuestas/">Encuestas<small>La media, al día</small></a></li>
  <li><a href="/actualidad/">Actualidad<small>Las últimas piezas</small></a></li>
</ul>
</main>
<script>
(()=>{
const norm=s=>s.toLowerCase().normalize("NFD").replace(/[\\u0300-\\u036f]/g,"").replace(/[^a-z0-9]+/g," ").trim();
let datos=null,carga=null;
const cargar=()=>carga||(carga=fetch("/municipio/buscador.json").then(r=>r.json()).then(d=>datos=d.map(x=>[x,norm(x[0])])));
const q=document.getElementById("q"),res=document.getElementById("res"),aviso=document.getElementById("h-res");
const buscar=t=>{t=norm(t);if(!t||!datos)return[];const a=[],b=[];for(const[x,n]of datos){if(n.startsWith(t))a.push(x);else if(n.includes(" "+t)||(t.length>3&&n.includes(t)))b.push(x)}
  const orden=(p,r)=>p[3]-r[3]||p[0].length-r[0].length;return a.sort(orden).concat(b.sort(orden)).slice(0,8)};
const pinta=()=>{const r=buscar(q.value);res.innerHTML="";for(const x of r){const li=document.createElement("li"),a=document.createElement("a"),s=document.createElement("span");
  a.href=x[2];a.textContent=x[0];s.textContent=x[3]?"barrio de "+x[1]:x[1];a.append(s);li.append(a);res.append(li)}
  aviso.hidden=!(q.value.trim().length>1&&!r.length);aviso.textContent="Ni rastro en el censo. Prueba con otro nombre o ve al índice de municipios."};
q.addEventListener("focus",cargar,{once:true});
q.addEventListener("input",()=>cargar().then(pinta));
// Si la dirección rota acaba en algo parecido a un municipio, lo proponemos.
const trozos=location.pathname.split("/").filter(Boolean);
let ultimo="";try{ultimo=trozos.length?norm(decodeURIComponent(trozos[trozos.length-1]).replace(/\\.html?$/,"").replace(/index$/,"")):""}catch(e){}
if(ultimo.length>2)cargar().then(()=>{let r=buscar(ultimo);if(!r.length)for(const w of ultimo.split(" ").reverse())if(w.length>3&&(r=buscar(w)).length)break;if(!r.length)return;const x=r[0],p=document.getElementById("quizas"),a=document.createElement("a");
  a.href=x[2];a.textContent=x[0]+(x[3]?" ("+x[1]+")":"");p.append("¿Buscabas ",a,"? Tu voto aún cuenta.");p.hidden=false}).catch(()=>{});
})();
</script>
<script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "cf0453d1d8f247d4a5dd55aff7b685ae"}'></script>
</body>
</html>
"""


if __name__ == '__main__':
    filas = indice()
    with open(os.path.join(RAIZ, 'municipio', 'buscador.json'), 'w', encoding='utf-8') as fh:
        json.dump(filas, fh, ensure_ascii=False, separators=(',', ':'))
    with open(os.path.join(RAIZ, '404.html'), 'w', encoding='utf-8') as fh:
        fh.write(pagina(paginas_totales()))
    print(len(filas), 'entradas en el buscador')
