"""Genera /encuestas/: todas las encuestas publicadas de las generales del 29N, con su fuente original.

Lee los CSV que actualiza dos veces al día el workflow «Encuestas» (previsiones/datos/encuestas/) y escribe
encuestas/index.html y encuestas/sitemap.xml. El workflow lo vuelve a ejecutar cuando llega una encuesta nueva, así
que la página se refresca sola. Solo usa la biblioteca estándar.

Qué publica: las cifras de cada encuesta tal como las publicó su encuestadora (voto y escaños), y la mediana de las
encuestas recientes como resumen descriptivo. No publica estimaciones propias: el modelo de /previsiones/ va aparte.

Fuentes: Electográfica (agregador, para localizar las encuestas y su ficha técnica) y la tabla de Wikipedia (CC BY-SA),
que añade los escaños de cada encuestadora y los sondeos que Electográfica no recoge (ElectoPanel de Electomanía).
Se enlaza siempre la publicación original.

Uso, desde la raíz:  python3 encuestas/src/construir.py
"""
import csv, html, json, os, pathlib, re, statistics, sys, unicodedata
from datetime import date, timedelta

sys.dont_write_bytecode = True   # no ensuciar los .pyc que hay en el repositorio
RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / 'actualidad' / 'src'))
from construir import AUTOR, BASE, CSS_SITIO, MEDIO, cabecera, fecha_larga, nav  # noqa: E402

DATOS = RAIZ / 'previsiones/datos/encuestas'
SALIDA = RAIZ / 'encuestas'
URL = BASE + '/encuestas/'
# los seis partidos de ámbito estatal que miden todas las encuestas, con su color (claro, oscuro)
PRINCIPALES = [('PP', 'PP', '#1d84ce', '#4fa8ea'), ('PSOE', 'PSOE', '#e30613', '#ff5a5f'), ('VOX', 'Vox', '#5ac035', '#74d651'),
               ('SUMAR', 'Sumar / Frente Amplio', '#a2275f', '#d0679a'), ('PODEMOS', 'Podemos', '#5a3c8f', '#8a6fe0'),
               ('SALF', 'SALF', '#785a46', '#a9876f')]
NOMBRE = {k: n for k, n, _, _ in PRINCIPALES}
NO_ENCUESTAS = {'keydata', 'sumar'}   # medias de otros medios y sondeos internos de partido
DESDE_GRAFICO = 365   # días que enseña el gráfico
DIAS_TABLA = 60
VENTANA_MEDIANA = 21


def clave(nombre):
    s = unicodedata.normalize('NFKD', str(nombre)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def carga():
    """Encuestas nacionales: las de Electográfica más las que solo están en Wikipedia; escaños de Wikipedia."""
    wp = list(csv.DictReader(open(DATOS / 'wikipedia_generales_espana.csv'))) if (DATOS / 'wikipedia_generales_espana.csv').exists() else []
    eg = [r for r in csv.DictReader(open(DATOS / 'encuestas_limpias.csv')) if r['ambito'] == 'ESPAÑA']
    usadas, out = set(), []

    def pareja(casa, fin):
        for i, w in enumerate(wp):
            c = clave(w['encuestadora'])
            if i not in usadas and not w.get('reestimacion') and (c.startswith(casa) or casa.startswith(c)) and abs((date.fromisoformat(w['campo_fin']) - fin).days) <= 4:
                return i
        return None

    for r in eg:
        fin = date.fromisoformat(r['campo_fin']) if r['campo_fin'] else date.fromisoformat(r['publicado']) - timedelta(days=3)
        i = pareja(clave(r['encuestadora']), fin)
        w = wp[i] if i is not None else {}
        if i is not None:
            usadas.add(i)
        out.append({'reest': False, 'casa': r['encuestadora'], 'medio': '' if r['cliente'] in ('', 'n/a') else r['cliente'],
                    'inicio': r['campo_inicio'] or w.get('campo_inicio', ''), 'fin': fin.isoformat(), 'fin_aprox': not r['campo_fin'] and not w,
                    'publicado': r['publicado'], 'muestra': r['muestra'] or w.get('muestra', ''),
                    'voto': {k: num(r[k]) for k, *_ in PRINCIPALES if num(r[k]) is not None},
                    'esc': {k: w.get(f'esc_{k}', '') for k, *_ in PRINCIPALES if w.get(f'esc_{k}')},
                    'url': r['fuente_original'] or w.get('fuente_original', '') or r['url_agregador']})
    for i, w in enumerate(wp):
        if i in usadas:
            continue
        if w.get('reestimacion'):   # datos brutos del CIS recalculados por otra empresa: solo en la tabla, con su nombre
            w = dict(w, encuestadora=f'{w["encuestadora"]} reestimado por {w["reestimacion"]}')
        out.append({'reest': bool(w.get('reestimacion')), 'casa': w['encuestadora'], 'medio': w['cliente'], 'inicio': w['campo_inicio'], 'fin': w['campo_fin'], 'fin_aprox': False,
                    'publicado': '', 'muestra': w['muestra'], 'voto': {k: num(w[k]) for k, *_ in PRINCIPALES if num(w[k]) is not None},
                    'esc': {k: w[f'esc_{k}'] for k, *_ in PRINCIPALES if w.get(f'esc_{k}')}, 'url': w['fuente_original']})
    out = [e for e in out if clave(e['casa']) not in NO_ENCUESTAS and 'PP' in e['voto'] and 'PSOE' in e['voto']]
    return sorted(out, key=lambda e: (e['fin'], e['casa']), reverse=True)


def medianas(encs, hasta):
    """Mediana diaria de cada partido con la última encuesta de cada encuestadora en los 21 días anteriores."""
    serie = []
    d = hasta - timedelta(days=DESDE_GRAFICO)
    while d <= hasta:
        ult = {}
        for e in encs:
            f = date.fromisoformat(e['fin'])
            if d - timedelta(days=VENTANA_MEDIANA) < f <= d and not e['reest'] and clave(e['casa']) not in ult:
                ult[clave(e['casa'])] = e   # encs va de más reciente a más antigua
        fila = {'d': d.isoformat()}
        for k, *_ in PRINCIPALES:
            v = [e['voto'][k] for e in ult.values() if k in e['voto']]
            if len(v) >= 3:
                fila[k] = round(statistics.median(v), 1)
        serie.append(fila)
        d += timedelta(days=1)
    return serie


def rango_esc(t):
    a, _, b = t.partition('-')
    return int(a), int(b or a)


def pc(v):
    return f'{v:.1f}'.replace('.', ',') + ' %'


def textos(encs, hoy):
    """Titular, entradilla y párrafos calculados con las encuestas (todo dato, sin interpretación)."""
    mes = [e for e in encs if date.fromisoformat(e['fin']) > hoy - timedelta(days=30) and not e['reest']]
    ultimas, vistos = [], set()
    for e in mes:
        if clave(e['casa']) not in vistos:
            vistos.add(clave(e['casa'])); ultimas.append(e)
    lider = lambda e: max(e['voto'], key=e['voto'].get)
    from collections import Counter
    cuenta = Counter(lider(e) for e in ultimas)
    primero, n1 = cuenta.most_common(1)[0]
    n = len(ultimas)
    tercero_vox = sum(1 for e in ultimas if sorted(e['voto'], key=e['voto'].get, reverse=True)[2:3] == ['VOX'])
    art = '' if primero in ('VOX', 'SUMAR', 'PODEMOS', 'SALF') else 'El '
    gana = f'{art}{NOMBRE[primero]} gana según las {n} encuestadoras del último mes' if n1 == n else f'{art}{NOMBRE[primero]} gana según {n1} de las {n} encuestadoras del último mes'
    rangos = {k: (min(e['voto'][k] for e in ultimas if k in e['voto']), max(e['voto'][k] for e in ultimas if k in e['voto']))
              for k in ('PP', 'PSOE', 'VOX')}
    entradilla = (f'Cada encuestadora con su última encuesta de los últimos 30 días: el PP va del {pc(rangos["PP"][0])} al {pc(rangos["PP"][1])}, '
                  f'el PSOE del {pc(rangos["PSOE"][0])} al {pc(rangos["PSOE"][1])} y Vox del {pc(rangos["VOX"][0])} al {pc(rangos["VOX"][1])}. '
                  'Todas las encuestas publicadas, con su fuente, actualizadas cada día.')
    disidentes = [e for e in ultimas if lider(e) != primero]
    p1 = (f'{n} encuestadoras han publicado al menos una encuesta de las generales con trabajo de campo terminado en los últimos 30 días. '
          + (f'Todas dan ganador al {NOMBRE[primero]}. ' if not disidentes else
             f'{n1} dan ganador al {NOMBRE[primero]}; ' + '; '.join(f'{"el " if e["casa"] == "CIS" else ""}{e["casa"]}, al {NOMBRE[lider(e)]}' for e in disidentes) + '. ')
          + ('Vox queda tercero en todas.' if tercero_vox == n else f'Vox queda tercero en {tercero_vox}.' if tercero_vox else ''))
    con_esc = [e for e in ultimas if 'PP' in e['esc'] and 'VOX' in e['esc']]
    mayoria = sum(1 for e in con_esc if rango_esc(e['esc']['PP'])[0] + rango_esc(e['esc']['VOX'])[0] >= 176)
    if con_esc and mayoria == len(con_esc):
        titular = f'{gana}, y las {mayoria} que publican escaños dan mayoría absoluta a PP y Vox'
    elif con_esc:
        titular = f'{gana}; {mayoria} de las {len(con_esc)} que publican escaños dan mayoría absoluta a PP y Vox'
    else:
        titular = gana
    p2 = ((f'Las {mayoria} que publican escaños dan' if mayoria == len(con_esc) else f'De las {len(con_esc)} que publican escaños, {mayoria} dan')
          + ' al PP y a Vox juntos 176 o más, la mayoría absoluta del Congreso (con un intervalo, se cuenta el extremo bajo).') if con_esc else ''
    return titular, entradilla, p1, p2, ultimas, con_esc, mayoria


def fila_tabla(e):
    casa = html.escape(e['casa']) + (f'<span class="medio">{html.escape(e["medio"])}</span>' if e['medio'] else '')
    enlace = f'<a href="{html.escape(e["url"])}">{casa}</a>' if e['url'] else casa
    f = date.fromisoformat(e['fin'])
    campo = f'{f.day}/{f.month}' + ('*' if e['fin_aprox'] else '')
    muestra = f'{int(e["muestra"]):,}'.replace(',', '.') if str(e['muestra']).isdigit() else '–'
    celdas = ''.join(f'<td class="n">{str(e["voto"][k]).replace(".", ",") if k in e["voto"] else "–"}'
                     + (f'<small>{e["esc"][k]}</small>' if k in e['esc'] else '') + '</td>' for k, *_ in PRINCIPALES)
    return f'<tr><td>{enlace}</td><td class="n">{campo}</td><td class="n">{muestra}</td>{celdas}</tr>'


ESTILOS = """<style>
:root{--bg:#fbfaf8;--fg:#1d1a1c;--muted:#5d585b;--rule:#e2dddf;--grid:#ebe7e8;--acc:#1d84ce;--tipbg:#1d1a1c;--tipfg:#fbfaf8}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;--grid:#2c282e;--acc:#4fa8ea;--tipbg:#f1edef;--tipfg:#18161a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#18161a;--fg:#f1edef;--muted:#b5aeb2;--rule:#343036;--grid:#2c282e;--acc:#4fa8ea;--tipbg:#f1edef;--tipfg:#18161a;color-scheme:dark}
body{background:var(--bg);color:var(--fg);font-family:var(--serif);font-size:18px;line-height:1.62}
main{max-width:46rem;margin:0 auto;padding-block:2.5rem 4rem;padding-inline:16px}
h1{font-size:clamp(1.8rem,5vw,2.6rem);line-height:1.12;font-weight:800;text-wrap:balance;margin:.8rem 0 .9rem}
.dek{font-size:1.15rem;line-height:1.5;color:var(--muted);margin:0 0 1rem}
h2{font-size:1.35rem;line-height:1.25;margin:2.4rem 0 .6rem;text-wrap:balance}
p{margin:0 0 1rem}
figure{margin:1.8rem 0 2rem;font-family:var(--ui)}
figcaption .t{font-weight:600;font-size:1.1rem;display:block;line-height:1.25}
figcaption .s{color:var(--muted);font-size:.95rem;display:block;margin-top:.15rem}
.src{color:var(--muted);font-size:.85rem;margin-top:.4rem;font-family:var(--ui)}
.chart{position:relative;margin-top:.7rem}
svg{display:block;width:100%;height:auto;overflow:visible}
svg text{font-family:var(--ui);fill:var(--muted);font-size:12px}
.legend{display:flex;flex-wrap:wrap;gap:.3rem 1rem;font-size:.92rem;margin-top:.4rem;font-family:var(--ui)}
.legend span{display:inline-flex;align-items:center;gap:.35rem}
.sw{width:12px;height:12px;border-radius:50%;display:inline-block}
.tip{position:absolute;pointer-events:none;background:var(--tipbg);color:var(--tipfg);font-family:var(--ui);font-size:.85rem;line-height:1.35;padding:.35rem .55rem;border-radius:4px;white-space:nowrap;z-index:5;transform:translate(-50%,-110%)}
.tbl{overflow-x:auto;margin:0 -16px;padding:0 16px}
table{border-collapse:collapse;font-family:var(--ui);font-size:.9rem;width:100%;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:.35rem .4rem;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-weight:600;font-size:.8rem;color:var(--muted);white-space:nowrap}
td.n,th.n{text-align:right;white-space:nowrap}
td small{display:block;color:var(--muted);font-size:.75rem}
td .medio{display:block;color:var(--muted);font-size:.8rem}
td a{color:var(--fg);text-decoration-color:var(--rule)}
th .pt{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
tr.mayoria td.suma{font-weight:700}
details{font-family:var(--ui);margin-top:.6rem} summary{cursor:pointer;color:var(--muted)}
a{color:var(--acc)}
.faq h3{font-family:var(--ui);font-size:1.05rem;margin:1.2rem 0 .3rem}
.descargas{font-family:var(--ui);font-size:.95rem}
@media (max-width:520px){body{font-size:17px}table{font-size:.82rem}}
</style>"""

SCRIPT = """<script>
(()=>{const D=__DATOS__;
const NS='http://www.w3.org/2000/svg',box=document.getElementById('graf');
const osc=()=>document.documentElement.dataset.theme==='dark'||(document.documentElement.dataset.theme!=='light'&&matchMedia('(prefers-color-scheme: dark)').matches);
const col=p=>p[osc()?3:2];
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
const pc=v=>v.toFixed(1).replace('.',',')+' %';
const M=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
function dibuja(){box.innerHTML='';const W=Math.max(320,box.clientWidth||640),H=W<500?320:380,m={l:34,r:W<500?8:70,t:10,b:24};
 const t0=Date.parse(D.serie[0].d),t1=Date.parse(D.serie[D.serie.length-1].d),hi=40;
 const x=t=>m.l+(t-t0)/(t1-t0)*(W-m.l-m.r),y=v=>m.t+(1-v/hi)*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Voto estimado de cada partido en cada encuesta y mediana de las encuestas recientes'},box);
 for(let v=0;v<=hi;v+=10){el('line',{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:'var(--grid)'},svg);el('text',{x:m.l-6,y:y(v)+4,'text-anchor':'end'},svg).textContent=v+'%'}
 const ini=new Date(t0);for(let d=new Date(ini.getFullYear(),ini.getMonth()+1,1);d<=t1;d.setMonth(d.getMonth()+(W<500?3:2))){
  el('text',{x:x(+d),y:H-6,'text-anchor':'middle'},svg).textContent=M[d.getMonth()]+(d.getMonth()===0?' '+d.getFullYear():'')}
 const fin=[];for(const p of D.partidos){const c=col(p);
  for(const e of D.encuestas){const t=Date.parse(e.f);if(t<t0||e.v[p[0]]==null)continue;el('circle',{cx:x(t),cy:y(e.v[p[0]]),r:2.3,fill:c,'fill-opacity':.35},svg)}
  let d='';for(const s of D.serie){if(s[p[0]]==null){d+='';continue}d+=(d&&!d.endsWith(' ')?'L':'M')+x(Date.parse(s.d)).toFixed(1)+','+y(s[p[0]]).toFixed(1)}
  el('path',{d,fill:'none',stroke:c,'stroke-width':2.5,'stroke-linejoin':'round'},svg);
  const u=[...D.serie].reverse().find(s=>s[p[0]]!=null);if(u)fin.push({y:y(u[p[0]])+4,c,t:p[0]==='SUMAR'?'Sumar':p[1]})}
 if(W>=500){fin.sort((a,b)=>a.y-b.y);for(let i=1;i<fin.length;i++)fin[i].y=Math.max(fin[i].y,fin[i-1].y+13);   // etiquetas sin solaparse
  for(const f of fin)el('text',{x:W-m.r+6,y:f.y,style:'fill:'+f.c+';font-weight:600'},svg).textContent=f.t}
 const tip=document.createElement('div');tip.className='tip';tip.hidden=true;box.appendChild(tip);
 const g=el('line',{y1:m.t,y2:H-m.b,stroke:'var(--muted)','stroke-dasharray':'2 3',visibility:'hidden'},svg);
 const mover=ev=>{const r=box.getBoundingClientRect(),pt=ev.touches?ev.touches[0]:ev,px=pt.clientX-r.left;
  const t=t0+(px-m.l)/(W-m.l-m.r)*(t1-t0);let s=D.serie.reduce((a,b)=>Math.abs(Date.parse(b.d)-t)<Math.abs(Date.parse(a.d)-t)?b:a);
  const f=new Date(s.d);g.setAttribute('x1',x(Date.parse(s.d)));g.setAttribute('x2',x(Date.parse(s.d)));g.setAttribute('visibility','visible');
  tip.innerHTML='<b>'+f.getDate()+' '+M[f.getMonth()]+' '+f.getFullYear()+'</b> · mediana<br>'+D.partidos.filter(p=>s[p[0]]!=null).map(p=>'<span style="color:'+col(p)+'">●</span> '+p[1]+' '+pc(s[p[0]])).join('<br>');
  tip.hidden=false;tip.style.left=Math.min(Math.max(px,90),W-90)+'px';tip.style.top=(pt.clientY-r.top)+'px'};
 svg.addEventListener('mousemove',mover);svg.addEventListener('touchstart',mover,{passive:true});svg.addEventListener('mouseleave',()=>{tip.hidden=true;g.setAttribute('visibility','hidden')})}
dibuja();let w=box.clientWidth;addEventListener('resize',()=>{if(box.clientWidth!==w){w=box.clientWidth;dibuja()}});
matchMedia('(prefers-color-scheme: dark)').addEventListener('change',dibuja)})();
</script>"""


def main():
    encs = carga()
    resumen = json.load(open(DATOS / 'resumen.json'))
    hoy = date.fromisoformat(resumen['descargado'][:10])
    ultima = date.fromisoformat(encs[0]['fin'])
    serie = medianas(encs, max(ultima, hoy))
    titular, entradilla, p1, p2, ultimas, con_esc, mayoria = textos(encs, hoy)
    desde_g = (hoy - timedelta(days=DESDE_GRAFICO)).isoformat()
    datos = {'partidos': PRINCIPALES, 'serie': serie,
             'encuestas': [{'f': e['fin'], 'v': e['voto']} for e in encs if e['fin'] >= desde_g and not e['reest']]}
    recientes = [e for e in encs if date.fromisoformat(e['fin']) > hoy - timedelta(days=DIAS_TABLA)]
    cab_partidos = ''.join(f'<th class="n"><i class="pt" style="background:{c}"></i>{"Sumar" if k == "SUMAR" else n}</th>' for k, n, c, _ in PRINCIPALES)
    tabla = (f'<div class="tbl"><table><thead><tr><th>Encuestadora y medio</th><th class="n">Fin campo</th><th class="n">Muestra</th>{cab_partidos}</tr></thead>'
             f'<tbody>{"".join(fila_tabla(e) for e in recientes)}</tbody></table></div>')
    anteriores = [e for e in encs if date.fromisoformat(e['fin']) <= hoy - timedelta(days=DIAS_TABLA) and e['fin'] >= '2023-07-24']
    tabla_ant = (f'<details><summary>Ver las {len(anteriores)} encuestas anteriores, desde las generales de 2023</summary><div class="tbl"><table><thead><tr>'
                 f'<th>Encuestadora y medio</th><th class="n">Fin campo</th><th class="n">Muestra</th>{cab_partidos}</tr></thead>'
                 f'<tbody>{"".join(fila_tabla(e) for e in anteriores)}</tbody></table></div></details>')
    filas_esc = ''
    for e in sorted(con_esc, key=lambda e: -rango_esc(e['esc']['PP'])[0]):
        lo = rango_esc(e['esc']['PP'])[0] + rango_esc(e['esc']['VOX'])[0]
        hi = rango_esc(e['esc']['PP'])[1] + rango_esc(e['esc']['VOX'])[1]
        suma = str(lo) if lo == hi else f'{lo}-{hi}'
        nombre = html.escape(e['casa']) + (f'<span class="medio">{html.escape(e["medio"])}</span>' if e['medio'] else '')
        # PP + Vox justo después del nombre, para que se vea en el móvil sin desplazar la tabla
        filas_esc += (f'<tr{" class=mayoria" if lo >= 176 else ""}><td>{nombre}</td><td class="n suma">{suma}</td>'
                      + ''.join(f'<td class="n">{e["esc"].get(k, "–")}</td>' for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'PODEMOS')) + '</tr>')
    tabla_esc = ('<div class="tbl"><table><thead><tr><th>Encuestadora</th><th class="n">PP + Vox</th>'
                 + ''.join(f'<th class="n"><i class="pt" style="background:{c}"></i>{"Sumar" if k == "SUMAR" else n}</th>' for k, n, c, _ in PRINCIPALES[:5])
                 + f'</tr></thead><tbody>{filas_esc}</tbody></table></div>') if con_esc else ''
    ult = encs[0]
    faq = [('¿Quién gana las elecciones generales según las encuestas?', p1.strip()),
           ('¿Cuál es la última encuesta de las generales?',
            f'La última encuesta con trabajo de campo terminado es la de {ult["casa"]}{" para " + ult["medio"] if ult["medio"] else ""}, '
            f'cerrada el {fecha_larga(ult["fin"])}: PP {pc(ult["voto"]["PP"])}, PSOE {pc(ult["voto"]["PSOE"])}'
            + (f', Vox {pc(ult["voto"]["VOX"])}' if 'VOX' in ult['voto'] else '') + '.'),
           ('¿Suman mayoría absoluta PP y Vox en las encuestas?', p2 or 'Las encuestas recientes no publican escaños.'),
           ('¿Cada cuánto se actualiza esta página?',
            'Dos veces al día. Cuando aparece una encuesta nueva, la tabla, el gráfico y las cifras de esta página se recalculan solos.')]
    faq_html = '<div class="faq">' + ''.join(f'<h3>{html.escape(q)}</h3><p>{html.escape(a)}</p>' for q, a in faq) + '</div>'
    actual = fecha_larga(hoy.isoformat())
    descripcion = re.sub(r'\s+', ' ', entradilla)[:300]
    jsonld = [{'@context': 'https://schema.org', '@type': 'NewsArticle', '@id': URL + '#articulo', 'headline': titular,
               'description': descripcion, 'url': URL, 'mainEntityOfPage': URL, 'inLanguage': 'es',
               'datePublished': '2026-10-22', 'dateModified': hoy.isoformat(), 'image': [f'{BASE}/img/compartir/encuestas.jpg'],
               'author': {'@type': 'Person', 'name': AUTOR, 'url': BASE + '/sobre-mi.html'}, 'publisher': MEDIO,
               'isAccessibleForFree': True},
              {'@context': 'https://schema.org', '@type': 'Dataset', '@id': URL + '#datos',
               'name': 'Encuestas de las elecciones generales de España (29 de noviembre de 2026)',
               'description': 'Estimación de voto y escaños de cada encuesta publicada desde las generales de 2023, con encuestadora, medio, fechas de campo, muestra y enlace a la publicación original.',
               'url': URL, 'license': 'https://creativecommons.org/licenses/by-sa/4.0/', 'dateModified': hoy.isoformat(),
               'creator': MEDIO, 'distribution': [{'@type': 'DataDownload', 'encodingFormat': 'text/csv',
                                                   'contentUrl': f'{BASE}/previsiones/datos/encuestas/encuestas_limpias.csv'}]},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': URL + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    titulo = 'Encuestas de las elecciones generales 2026 (29N)'
    main_html = f"""<main>
<p class="kicker">Elecciones generales · 29 de noviembre</p>
<h1>{html.escape(titular)}</h1>
<p class="dek">{html.escape(entradilla)}</p>
<p class="firma">Por <a href="../sobre-mi.html">{AUTOR}</a> · Actualizado el <time datetime="{hoy.isoformat()}">{actual}</time></p>
<p data-tipo="dato">{html.escape(p1)}</p>
<p data-tipo="dato">{html.escape(p2)}</p>
<figure>
<figcaption><span class="t">Voto estimado en cada encuesta, último año</span><span class="s">Cada punto es una encuesta; la línea es la mediana de la última encuesta de cada encuestadora en los {VENTANA_MEDIANA} días anteriores (con tres o más). Porcentaje sobre voto válido. Sumar incluye el Frente Amplio y sus socios.</span></figcaption>
<div class="chart" id="graf"></div>
<div class="legend">{''.join(f'<span><i class="sw" style="background:{c}"></i>{n}</span>' for _, n, c, _ in PRINCIPALES)}</div>
<p class="src">Encuestas publicadas, vía Electográfica y Wikipedia. La mediana resume las encuestas: no es una previsión de Mapa Electoral.</p>
</figure>
<h2>Escaños que da cada encuestadora</h2>
<p>Última encuesta de cada una en los últimos 30 días, con los escaños que publica. Un intervalo («132-137») es la horquilla de la propia encuestadora; la mayoría absoluta está en 176.</p>
{tabla_esc}
<h2>Todas las encuestas de los últimos {DIAS_TABLA} días</h2>
<p>Voto estimado en porcentaje y, debajo, escaños cuando la encuestadora los publica. Cada nombre enlaza a la publicación original. «CIS reestimado por…» son los datos brutos del CIS recalculados por otra empresa: no cuentan como encuesta propia ni entran en el gráfico. Un asterisco en la fecha indica que no consta el trabajo de campo y se toma la publicación menos tres días.</p>
{tabla}
{tabla_ant}
<h2>Preguntas rápidas</h2>
{faq_html}
<h2>Método y fuentes</h2>
<dl class="ficha">
<dt>Qué se recoge</dt><dd>Todas las encuestas de ámbito estatal con estimación de voto para el Congreso publicadas desde las generales de julio de 2023, tal como las publicó cada encuestadora. No se recogen medias de otros medios ni sondeos internos de los partidos.</dd>
<dt>Límites</dt><dd>Las encuestas no son resultados. Cada encuestadora usa su método (teléfono, internet, panel), su muestra y su forma de estimar, y en las generales de 2019 y 2023 la media de las encuestas se equivocó hasta en 3,4 puntos en un partido. La estimación del CIS se aparta del resto (<a href="../actualidad/cis-tezanos-estimacion-29n/">así le fue en elecciones anteriores</a>). La mediana del gráfico es un resumen, no una previsión.</dd>
<dt>Fuentes</dt><dd><ul><li>Cada encuesta enlaza a su publicación original (medio o encuestadora).</li><li><a href="https://www.electografica.com/">Electográfica</a>, para localizar las encuestas y su ficha técnica.</li><li><a href="https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Spanish_general_election">Wikipedia, «Opinion polling for the 2026 Spanish general election»</a> (CC BY-SA 4.0), para los escaños y los sondeos que no recoge Electográfica.</li></ul></dd>
<dt>Actualización</dt><dd>Automática, dos veces al día (código en <a href="https://github.com/nachotronic/abstencio-catalunya/tree/main/previsiones/src">previsiones/src</a>). Última: {actual}.</dd>
<dt>Autoría</dt><dd>{AUTOR}</dd>
</dl>
<p class="descargas">Descargar los datos: <a href="../previsiones/datos/encuestas/encuestas_limpias.csv">todas las encuestas (CSV)</a> · <a href="../previsiones/datos/encuestas/wikipedia_generales_espana.csv">con escaños, según Wikipedia (CSV)</a></p>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../"><span class="kicker">Mapa</span><b>El mapa de las generales, sección a sección</b></a></li><li><a href="../actualidad/cis-tezanos-estimacion-29n/"><span class="kicker">Encuestas</span><b>El CIS y sus estimaciones frente a los resultados</b></a></li><li><a href="../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="https://github.com/nachotronic/abstencio-catalunya">Código y datos</a> · <a href="../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    pagina = (cabecera(titulo, descripcion, URL, f'{BASE}/img/compartir/encuestas.jpg', jsonld)
              .replace('<meta property="og:title" content="' + titulo + '">', '<meta property="og:title" content="' + html.escape(titular) + '">')
              + ESTILOS + CSS_SITIO + '\n</head>\n<body>\n' + nav('../', '') + '\n' + main_html + '\n'
              + SCRIPT.replace('__DATOS__', json.dumps(datos, ensure_ascii=False, separators=(',', ':'))) + '\n</body>\n</html>\n')
    SALIDA.mkdir(exist_ok=True)
    (SALIDA / 'index.html').write_text(pagina, encoding='utf-8')
    (SALIDA / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                        f'  <url><loc>{URL}</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n</urlset>\n', encoding='utf-8')
    print(f'encuestas: {len(encs)} encuestas, {len(recientes)} en la tabla; {titular}')


if __name__ == '__main__':
    main()
