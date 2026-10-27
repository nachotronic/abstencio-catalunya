"""Calculadora de escaños: /encuestas/calculadora-escanos/.

El lector mueve el porcentaje de voto de cada partido en toda España y la página reparte los 350 escaños en las 52
circunscripciones con la ley D'Hondt y la barrera del 3 % de cada provincia. Parte del escenario central del modelo
(la media de encuestas repartida por provincia) y aplica a cada provincia el mismo cambio proporcional que el lector
hace en el total de España.

La llama construir.py (main) después del modelo, así que se rehace sola con cada encuesta nueva. Si no hay salida
publicable del modelo, no escribe nada.
"""
import html, json


def genera(m):
    if not (m.ESTIMACION / 'escenario-base.json').exists():
        return False
    d = json.load(open(m.ESTIMACION / 'escenario-base.json'))
    meta = json.load(open(m.ESTIMACION / 'meta.json'))
    if meta.get('interno', True) or meta.get('ficticio'):
        return False
    import sys
    sys.path.insert(0, str(m.RAIZ / 'src'))
    from territorios_rutas import ruta_provincia
    col = {k: (c, o) for k, _, c, o in m.TODOS}
    partidos = []
    for l in sorted(d['listas'], key=lambda l: -l['voto'][2]):
        k = m.DEL_MODELO.get(l['lista'])
        if not k or k not in col:
            continue
        partidos.append([l['lista'], m.NOMBRE[k].replace(' / Frente Amplio', ''), *col[k], round(l['voto'][2], 1), round(l['escanos'][2])])
    claves = {p[0] for p in partidos}
    provs = [[c, meta['provincias'][c], v['escanos_total'], '../../' + ruta_provincia(c),
              {l['lista']: l['voto'][1] for l in v['listas'] if l['lista'] in claves}]
             for c, v in sorted(d['provincias'].items(), key=lambda x: meta['provincias'][x[0]])]
    orden = [next(l for l, k in m.DEL_MODELO.items() if k == o) for o in m.ORDEN_HEMI if o in m.DEL_MODELO.values()]
    bloques = [[b['bloque'], b['listas']] for b in d['bloques']]
    datos = {'partidos': partidos, 'provs': provs, 'orden': [o for o in orden if o in claves], 'bloques': bloques}
    actual = m.fecha_larga(meta['generado'])
    url = m.URL + 'calculadora-escanos/'
    titulo = 'Calculadora de escaños del 29N: reparte los 350 diputados con tus porcentajes'
    desc = ('Mueve el voto de cada partido y mira cuántos escaños saca en cada provincia con la ley D\'Hondt, si PP y Vox suman mayoría absoluta '
            f'y qué provincias cambian de manos. Parte de la media de encuestas del {actual}.')
    faq = [('¿Cómo se reparten los escaños en las elecciones generales?',
            'Cada provincia elige un número fijo de diputados (Madrid 38, Barcelona 32, Soria 2...). En cada una, los partidos que pasan del 3 % de los votos válidos '
            'se reparten esos escaños con la ley D\'Hondt: se divide el voto de cada partido entre 1, 2, 3... y se dan los escaños a los cocientes más altos.'),
           ('¿De dónde salen los porcentajes de partida?',
            f'De la media de las encuestas publicadas, actualizada el {actual}, que el modelo de Mapa Electoral reparte por provincia a partir del resultado de 2023.'),
           ('¿Qué pasa en cada provincia cuando muevo un porcentaje?',
            'Se aplica el mismo cambio proporcional en todas: si un partido pasa del 20 % al 22 % en España, sube un 10 % en cada provincia. '
            'Es una simplificación: en la realidad unos territorios se mueven más que otros.'),
           ('¿Cuántos escaños hacen falta para la mayoría absoluta?', '176 de los 350 del Congreso.')]
    jsonld = [{'@context': 'https://schema.org', '@type': 'WebApplication', '@id': url + '#calculadora', 'name': titulo, 'description': desc, 'url': url,
               'applicationCategory': 'EducationalApplication', 'operatingSystem': 'Todos', 'inLanguage': 'es', 'isAccessibleForFree': True,
               'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}, 'dateModified': meta['generado'],
               'author': {'@type': 'Person', 'name': m.AUTOR, 'url': m.BASE + '/sobre-mi.html'}, 'publisher': m.MEDIO},
              {'@context': 'https://schema.org', '@type': 'FAQPage', '@id': url + '#preguntas', 'inLanguage': 'es',
               'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}]
    cuerpo = f"""<main>
<p class="kicker">Calculadora · Elecciones generales del 29N</p>
<h1 data-miga="Calculadora de escaños">Calculadora de escaños: reparte tú los 350 diputados</h1>
<p class="dek">Mueve el voto de cada partido en toda España y mira cuántos diputados saca en cada provincia con la ley D'Hondt y la barrera del 3 %.</p>
<p class="firma">Por <a href="../../sobre-mi.html">{m.AUTOR}</a> · Datos de partida del <time datetime="{meta['generado']}">{actual}</time></p>
<p class="propio"><b>Esto es un juego con reglas reales, no una previsión.</b> Arranca con la <a href="../">media de las encuestas</a> repartida por provincia por nuestro <a href="../metodo-modelo.html">modelo</a>; lo que salga después depende de los porcentajes que pongas tú.</p>

<section class="calc" aria-label="Calculadora">
<div class="res">
  <div class="total"><span id="titular" aria-live="polite"></span></div>
  <div class="barra" id="barra" role="img" aria-label="Reparto de los 350 escaños"></div>
  <div class="eje"><span>0</span><span class="mayoria">Mayoría: 176</span><span>350</span></div>
</div>
<div class="bloques" id="bloques"></div>
<div class="mandos">
  <div class="cab"><b>Voto en toda España</b><button type="button" id="reset">Volver a la media de encuestas</button></div>
  <div id="sliders"></div>
  <p class="suma" id="suma"></p>
  <button type="button" id="compartir" class="compartir">Copiar enlace con mi reparto</button> <a class="compartir" id="a-pactos" href="../simulador-pactos/">Probar pactos con estos escaños</a>
</div>
</section>

<h2>Escaños por partido</h2>
<div class="tbl"><table class="part"><thead><tr><th>Partido</th><th class="n">Voto</th><th class="n">Escaños</th><th class="n">Con la media</th></tr></thead><tbody id="tabla"></tbody></table></div>

<h2>Provincia a provincia</h2>
<p>Cada cuadrado es un escaño. Las provincias en las que tu reparto cambia algún escaño respecto a la media de encuestas van marcadas con un punto.</p>
<label class="filtro"><input type="checkbox" id="solo"> Ver solo las provincias que cambian</label>
<div class="provs" id="provs"></div>

<h2>Preguntas frecuentes</h2>
<div class="faq">{''.join(f'<details><summary><h3>{html.escape(q)}</h3></summary><p>{html.escape(a)}</p></details>' for q, a in faq)}</div>
<p class="src">Reglas: ley D'Hondt y barrera del 3 % de los votos válidos en cada circunscripción (artículos 162 y 163 de la LOREG), con los diputados de cada provincia para 2026. No incluye el voto exterior por separado ni el Senado. Datos de partida: escenario central del modelo de Mapa Electoral del {actual}.</p>
<h2>Sigue leyendo</h2><ul class="sigue"><li><a href="../"><span class="kicker">Encuestas</span><b>Todas las encuestas de las elecciones generales 2026 y su promedio</b></a></li><li><a href="../simulador-pactos/"><span class="kicker">Simulador</span><b>¿Quién suma 176? Haz tú los pactos del 29N</b></a></li><li><a href="../provincias.html"><span class="kicker">Modelo</span><b>Encuestas por provincias: escaños en cada provincia</b></a></li><li><a href="../../actualidad/precio-del-escano-29n/"><span class="kicker">Sistema electoral</span><b>El precio de un escaño en cada provincia</b></a></li><li><a href="../../actualidad/ultimo-escano-29n/"><span class="kicker">Escaños</span><b>El último escaño de cada provincia</b></a></li></ul>
<footer>Mapa Electoral · Datos con licencia <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a> · <a href="../../atlas/politica-editorial/">Política editorial</a></footer>
</main>"""
    estilos = m.ESTILOS.replace('</style>', CSS + '</style>')
    pagina = (m.cabecera(titulo, desc, url, f'{m.BASE}/img/compartir/encuestas.jpg?v={meta["generado"]}', jsonld)
              + estilos + m.CSS_SITIO + '\n</head>\n<body>\n' + m.nav('../../', 'Encuestas') + '\n' + cuerpo + '\n'
              + JS.replace('__DATOS__', json.dumps(datos, ensure_ascii=False, separators=(',', ':'))) + '\n</body>\n</html>\n')
    salida = m.SALIDA / 'calculadora-escanos'
    salida.mkdir(exist_ok=True)
    (salida / 'index.html').write_text(pagina, encoding='utf-8')
    return True


CSS = """
.calc{display:grid;gap:1rem;font-family:var(--ui);margin:1.6rem 0}
.res{position:sticky;top:0;z-index:2;background:var(--bg);padding:.5rem 0 .4rem;box-shadow:0 6px 8px -8px rgba(0,0,0,.35)}
.total{font-size:1.05rem;line-height:1.35;text-wrap:balance}
.total b{font-weight:700}
.barra{display:flex;height:30px;border-radius:4px;overflow:hidden;position:relative;background:var(--grid);margin:.4rem 0 .15rem}
.barra i{display:block;height:100%;transition:flex-basis .25s ease}
.barra::after{content:"";position:absolute;left:50.29%;top:-4px;bottom:-4px;width:2px;background:var(--fg)}
.eje{display:flex;justify-content:space-between;font-size:.75rem;color:var(--muted)}
.eje .mayoria{color:var(--fg);font-weight:600}
.bloques{display:grid;gap:4px;font-size:.85rem;padding-bottom:.8rem;border-bottom:1px solid var(--rule)}
.bloques div{display:flex;justify-content:space-between;gap:10px}
.bloques .si b{color:var(--acc)}
.mandos .cab{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:.4rem;flex-wrap:wrap}
.mandos button,.compartir{display:inline-block;text-decoration:none;font:600 .85rem var(--ui);border:1px solid var(--rule);background:transparent;color:var(--fg);border-radius:6px;padding:6px 10px;cursor:pointer}
.mandos button:hover{border-color:var(--fg)}
.sl{display:grid;grid-template-columns:7.5em 1fr 4.6em;align-items:center;gap:10px;margin:4px 0}
.sl label{font-weight:600;font-size:.92rem;display:flex;align-items:center;gap:6px}
.sl label i{width:10px;height:10px;border-radius:50%;flex:none}
.sl input[type=range]{width:100%;min-width:0;margin:0;accent-color:var(--c)}
.sl input[type=number]{width:100%;box-sizing:border-box;min-width:0;font:500 .9rem var(--ui);padding:3px 4px;border:1px solid var(--rule);border-radius:4px;background:transparent;color:var(--fg);text-align:right}
.sl.cambia label{text-decoration:underline;text-decoration-color:var(--c);text-underline-offset:3px}
details.mas summary{cursor:pointer;font-size:.9rem;color:var(--muted);margin:.4rem 0}
.suma{font-size:.82rem;color:var(--muted);margin:.4rem 0 .6rem}
.suma.aviso{color:#b3261e}
.part .d{font-size:.8rem;margin-left:4px}
.part .d.up{color:#2b8a3e}.part .d.dn{color:#b3261e}
.part i.pt{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px}
.filtro{font:500 .9rem var(--ui);display:flex;gap:6px;align-items:center;margin:.2rem 0 .8rem}
.provs{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px 18px;font-family:var(--ui)}
.pv{font-size:.85rem;border-top:1px solid var(--rule);padding-top:6px}
.pv a{color:var(--fg);font-weight:600;text-decoration:none}
.pv a:hover{text-decoration:underline}
.pv .n{color:var(--muted);font-weight:400}
.pv .cm{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--acc);margin-left:5px;vertical-align:1px}
.pv .esc{display:flex;flex-wrap:wrap;gap:2px;margin-top:4px}
.pv .esc i{width:10px;height:10px;border-radius:2px;display:block}
@media (max-width:520px){.sl{grid-template-columns:6.2em 1fr 4.2em}.total{font-size:.98rem}}
"""

JS = """<script>
(()=>{
const D=__DATOS__;
const oscuro=()=>matchMedia('(prefers-color-scheme: dark)').matches&&document.documentElement.dataset.theme!=='light'||document.documentElement.dataset.theme==='dark';
const P={};D.partidos.forEach(([k,n,c,o,v,e],i)=>P[k]={k,n,c,o,v,e,i});
const col=k=>oscuro()?P[k].o:P[k].c;
const base={};D.partidos.forEach(p=>base[p[0]]=p[4]);
let nat={...base};
const fmt=(x,d=1)=>x.toLocaleString('es-ES',{minimumFractionDigits:d,maximumFractionDigits:d});
const el=(t,a={},...h)=>{const e=document.createElement(t);for(const[k,v]of Object.entries(a)){if(k==='style')e.style.cssText=v;else if(k in e)e[k]=v;else e.setAttribute(k,v)}e.append(...h);return e};
function reparto(n){
  const total={},porProv=[];
  for(const k in P)total[k]=0;
  for(const[c,nom,esc,url,v]of D.provs){
    const voto={};let s=0;
    for(const k in v){voto[k]=base[k]>0?v[k]*n[k]/base[k]:0;s+=voto[k]}
    const f=s>100?100/s:1,cand=[];
    for(const k in voto){voto[k]*=f;if(voto[k]>=3)cand.push(k)}
    const q=[];for(const k of cand)for(let i=1;i<=esc;i++)q.push([voto[k]/i,k]);
    q.sort((a,b)=>b[0]-a[0]||voto[b[1]]-voto[a[1]]);
    const r={};for(let i=0;i<esc&&i<q.length;i++){r[q[i][1]]=(r[q[i][1]]||0)+1;total[q[i][1]]++}
    porProv.push([c,nom,esc,url,r]);
  }
  return{total,porProv};
}
const REF=reparto(base);
const sl=document.getElementById('sliders'),mas=el('details',{className:'mas'},el('summary',{},'Más partidos (de ámbito autonómico y pequeños)'));
const inputs={};
D.partidos.forEach(([k,n,c,o,v],i)=>{
  const max=v>15?50:v>4?20:8,id='p-'+i;
  const r=el('input',{type:'range',min:0,max,step:0.1,value:v,id,'aria-label':'Voto de '+n+' en toda España, en porcentaje'});
  const num=el('input',{type:'number',min:0,max:60,step:0.1,value:v,'aria-label':'Voto de '+n+', en porcentaje'});
  const row=el('div',{className:'sl',style:'--c:'+c},el('label',{htmlFor:id},el('i',{style:'background:'+c}),n),r,num);
  const set=x=>{x=Math.max(0,Math.min(60,+x||0));nat[k]=Math.round(x*10)/10;pinta()};
  r.addEventListener('input',()=>set(r.value));num.addEventListener('change',()=>set(num.value));
  inputs[k]={r,num,row};
  (v>=4?sl:mas).append(row);
});
sl.append(mas);
function pinta(){
  const{total,porProv}=reparto(nat);
  for(const k in inputs){const{r,num,row}=inputs[k];r.value=nat[k];if(+num.value!==nat[k])num.value=nat[k];row.classList.toggle('cambia',Math.abs(nat[k]-base[k])>0.05)}
  const s=Object.values(nat).reduce((a,b)=>a+b,0),su=document.getElementById('suma');
  su.textContent=s>100?`Los partidos suman el ${fmt(s)} %: en cada provincia se reduce todo en proporción hasta el 100 %.`:`Los partidos suman el ${fmt(s)} %; el ${fmt(100-s)} % restante es voto en blanco y de otros partidos.`;
  su.classList.toggle('aviso',s>100);
  const barra=document.getElementById('barra');barra.replaceChildren(...D.orden.filter(k=>total[k]).map(k=>el('i',{title:P[k].n+': '+total[k],style:`flex:0 0 ${total[k]/3.5}%;background:${col(k)}`})));
  const bl=document.getElementById('bloques');
  bl.replaceChildren(...D.bloques.map(([n,ks])=>{const t=ks.reduce((a,k)=>a+(total[k]||0),0);return el('div',{className:t>=176?'si':''},el('span',{},n),el('span',{},el('b',{},String(t)),t>=176?' · mayoría':` · faltan ${176-t}`))}));
  const pv=(D.bloques[0][1]).reduce((a,k)=>a+(total[k]||0),0);
  const top=D.partidos.map(p=>p[0]).sort((a,b)=>total[b]-total[a]);
  document.getElementById('titular').innerHTML=`<b>${P[top[0]].n}</b> ${total[top[0]]} escaños, <b>${P[top[1]].n}</b> ${total[top[1]]}. `+(pv>=176?`PP y Vox suman <b>${pv}</b>: mayoría absoluta.`:`PP y Vox suman <b>${pv}</b>: se quedan a ${176-pv} de la mayoría.`);
  const tb=document.getElementById('tabla');
  tb.replaceChildren(...D.partidos.filter(p=>total[p[0]]||REF.total[p[0]]).sort((a,b)=>total[b[0]]-total[a[0]]||b[4]-a[4]).map(([k,n])=>{const dlt=total[k]-REF.total[k];
    return el('tr',{},el('td',{},el('i',{className:'pt',style:'background:'+col(k)}),n),el('td',{className:'n'},fmt(nat[k])+' %'),
      el('td',{className:'n'},el('b',{},String(total[k])),dlt?el('span',{className:'d '+(dlt>0?'up':'dn')},(dlt>0?'+':'')+dlt):''),el('td',{className:'n'},String(REF.total[k])))}));
  const solo=document.getElementById('solo').checked,ref={};REF.porProv.forEach(p=>ref[p[0]]=p[4]);
  const difiere=(c,r)=>D.orden.some(k=>(r[k]||0)!==(ref[c][k]||0));
  document.getElementById('provs').replaceChildren(...porProv.filter(([c,,,,r])=>!solo||difiere(c,r)).map(([c,nom,esc,url,r])=>{
    const cambia=difiere(c,r);
    const sq=[];D.orden.forEach(k=>{for(let i=0;i<(r[k]||0);i++)sq.push(el('i',{title:P[k].n,style:'background:'+col(k)}))});
    return el('div',{className:'pv'},el('a',{href:url},nom),el('span',{className:'n'},' · '+esc),cambia?el('span',{className:'cm',title:'Cambia respecto a la media'}):'',el('div',{className:'esc'},...sq),
      el('div',{className:'n'},D.orden.filter(k=>r[k]).sort((a,b)=>r[b]-r[a]).map(k=>P[k].n+' '+r[k]).join(' · ')))}));
  document.getElementById('a-pactos').href='../simulador-pactos/#e='+D.orden.filter(k=>total[k]).map(k=>encodeURIComponent(k)+'.'+total[k]).join(',');
  try{history.replaceState(null,'',Object.keys(nat).some(k=>Math.abs(nat[k]-base[k])>0.05)?'#'+Object.keys(nat).filter(k=>Math.abs(nat[k]-base[k])>0.05).map(k=>encodeURIComponent(k)+'='+nat[k]).join('&'):location.pathname)}catch(e){}
}
document.getElementById('reset').onclick=()=>{nat={...base};pinta()};
document.getElementById('solo').onchange=pinta;
document.getElementById('compartir').onclick=e=>{const b=e.target;navigator.clipboard?.writeText(location.href).then(()=>{b.textContent='Enlace copiado';setTimeout(()=>b.textContent='Copiar enlace con mi reparto',1800)})};
if(location.hash)decodeURIComponent(location.hash.slice(1)).split('&').forEach(x=>{const[k,v]=x.split('=');if(k in nat&&!isNaN(+v))nat[k]=Math.max(0,Math.min(60,+v))});
matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change',pinta);
pinta();
})();
</script>"""
