// Gráficos de la serie «Historia electoral»: barras, barras horizontales, líneas, rejilla de ganadores y dispersión.
// Cada partido en su color (paleta del mapa: generales-2026/src/partidos.py).
const COL={PP:'#1d84ce',PSOE:'#e30613',VOX:'#5ac035',SUMAR:'#a2275f',CS:'#eb6109',UPYD:'#e5007d',ERC:'#f5b324',JUNTS:'#20c0b2',PNV:'#2b8a3e',BILDU:'#a5c400',BNG:'#7ab8e6',CC:'#f7d417',UCD:'#e07b22',CDS:'#7e57c2',OTROS:'#9a9a9a'};
const NOM={PP:'AP / PP',PSOE:'PSOE',VOX:'Vox',SUMAR:'PCE / IU / Podemos / Sumar',CS:'Ciudadanos',UPYD:'UPyD',ERC:'ERC',JUNTS:'CiU / Junts',PNV:'PNV',BILDU:'HB / EH Bildu',BNG:'BNG',CC:'Coalición Canaria',UCD:'UCD',CDS:'CDS',OTROS:'Otras listas'};
const NS='http://www.w3.org/2000/svg';
const num=(v,d=1)=>v==null?'—':v.toFixed(d).replace('.',',');
const pct=(v,d=1)=>v==null?'sin dato':num(v,d)+'%';
const miles=v=>v==null?'—':Math.round(v).toLocaleString('es-ES');
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
function txt(p,a,t){const e=el('text',a,p);e.textContent=t;return e}
function tipFor(box){const t=document.createElement('div');t.className='tip';t.hidden=true;box.appendChild(t);
 return {show(h,x,y){t.innerHTML=h;t.hidden=false;const bw=box.clientWidth,tw=t.offsetWidth;t.style.left=Math.min(Math.max(x,tw/2),bw-tw/2)+'px';t.style.top=y+'px'},hide(){t.hidden=true}}}
function pos(box,ev){const r=box.getBoundingClientRect();const p=ev.touches?ev.touches[0]:ev;return [p.clientX-r.left,p.clientY-r.top]}
function hover(node,box,tip,h){const f=ev=>{const [a,b]=pos(box,ev);tip.show(h,a,b)};node.addEventListener('mousemove',f);node.addEventListener('touchstart',f,{passive:true});node.addEventListener('mouseleave',()=>tip.hide())}
function tabla(id,cab,filas){const d=document.getElementById(id+'-tbl');if(!d)return;
 d.innerHTML='<table><thead><tr>'+cab.map((c,i)=>`<th${i?' class="n"':''}>${c}</th>`).join('')+'</tr></thead><tbody>'+filas.map(f=>'<tr>'+f.map((c,i)=>`<td${i?' class="n"':''}>${c}</td>`).join('')+'</tr>').join('')+'</tbody></table>'}
function caja(id){const box=document.getElementById(id);return [box,Math.max(320,box.clientWidth||640),tipFor(box)]}
function ejeY(svg,W,m,y,ticks,f){ticks.forEach(v=>{el('line',{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:'var(--grid)'},svg);txt(svg,{x:m.l-6,y:y(v)+4,'text-anchor':'end'},f(v))})}
function corta(l){return l.replace(/^(19|20)(\d\d)-?(.*)$/,"'$2$3")}
function etiquetasX(svg,labs,xc,H,m,W){const rot=W<560&&labs.length>8,paso=labs.length>20?(W<560?3:2):1;
 labs.forEach((l,i)=>{if(i%paso)return;const x=xc(i);txt(svg,{x,y:H-m.b+16,'text-anchor':rot?'end':'middle',transform:rot?`rotate(-55 ${x} ${H-m.b+12})`:''},rot?l:(labs.length>8?corta(l):l))})}
function recorta(l,W){const max=W<500?15:24;return l.length>max?l.slice(0,max-1)+'…':l}
// Barras verticales: d=[{l:etiqueta,v:valor,c:color,t:tooltip,lab:bool}]
function barras(id,d,o={}){const [box,W,tip]=caja(id);const rot=W<560&&d.length>8;const H=o.h||(W<500?250:290),m={l:o.ml||40,r:6,t:22,b:rot?52:28};
 const max=o.max||Math.max(...d.map(x=>x.v||0))*1.1,n=d.length,bw=(W-m.l-m.r)/n,y=v=>H-m.b-v/max*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);ejeY(svg,W,m,y,o.ticks,o.fy||(v=>v+'%'));
 d.forEach((x,i)=>{const X=m.l+i*bw;if(x.v!=null)el('rect',{x:X+Math.min(3,bw*.15),y:y(x.v),width:bw-2*Math.min(3,bw*.15),height:y(0)-y(x.v),rx:2,fill:x.c},svg);
  if(x.lab&&x.v!=null)txt(svg,{x:X+bw/2,y:y(x.v)-6,'text-anchor':'middle',class:'lab'},(o.fl||(v=>num(v)))(x.v));
  const h=el('rect',{x:X,y:m.t,width:bw,height:H-m.t-m.b,fill:'transparent'},svg);hover(h,box,tip,x.t)});
 etiquetasX(svg,d.map(x=>x.l),i=>m.l+i*bw+bw/2,H,m,W)}
// Barras horizontales: d=[{l,v,c,t,lab}]
function hbarras(id,d,o={}){const [box,W,tip]=caja(id);const rh=o.rh||22,m={l:o.ml||(W<500?130:170),r:46,t:4,b:22},H=m.t+m.b+rh*d.length;
 const max=o.max||Math.max(...d.map(x=>x.v))*1.05,x=v=>m.l+v/max*(W-m.l-m.r);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);
 o.ticks.forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);txt(svg,{x:x(v),y:H-5,'text-anchor':'middle'},(o.fy||(v=>v+'%'))(v))});
 d.forEach((r,i)=>{const yy=m.t+i*rh;txt(svg,{x:m.l-6,y:yy+rh/2+4,'text-anchor':'end',class:r.b?'lab':'','font-size':12.5},recorta(r.l,W));
  el('rect',{x:m.l,y:yy+3,width:Math.max(0,x(r.v)-m.l),height:rh-6,rx:2,fill:r.c},svg);
  txt(svg,{x:x(r.v)+5,y:yy+rh/2+4,'font-size':12},(o.fl||(v=>num(v)))(r.v));
  const h=el('rect',{x:0,y:yy,width:W,height:rh,fill:'transparent'},svg);hover(h,box,tip,r.t)})}
// Líneas: labs=[...], s=[{n,c,v:[...],w,dash}]
function lineas(id,labs,s,o={}){const [box,W,tip]=caja(id);const rot=W<560&&labs.length>8;const H=o.h||(W<500?260:300),m={l:o.ml||40,r:o.mr||(W<500?8:90),t:14,b:rot?52:28};
 const max=o.max,min=o.min||0,n=labs.length,xs=i=>m.l+i*(W-m.l-m.r)/(n-1),y=v=>H-m.b-(v-min)/(max-min)*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);ejeY(svg,W,m,y,o.ticks,o.fy||(v=>v+'%'));
 s.forEach(se=>{let dd='',pen=false;se.v.forEach((v,i)=>{if(v==null){pen=false;return}dd+=(pen?'L':'M')+xs(i)+','+y(v);pen=true});
  el('path',{d:dd,fill:'none',stroke:se.c,'stroke-width':se.w||2.5,'stroke-dasharray':se.dash||'','stroke-linejoin':'round'},svg);
  se.v.forEach((v,i)=>{if(v!=null&&(se.pts!==false))el('circle',{cx:xs(i),cy:y(v),r:se.w>3?3.5:2.8,fill:se.c},svg)});
  const last=se.v.length-1-[...se.v].reverse().findIndex(v=>v!=null);
  if(W>=500&&o.fin!==false)txt(svg,{x:xs(last)+7,y:y(se.v[last])+4+(se.dy||0),fill:se.c,'font-weight':600,'font-size':12.5},se.n)});
 etiquetasX(svg,labs,xs,H,m,W);
 labs.forEach((l,i)=>{const w=(W-m.l-m.r)/(n-1);const h=el('rect',{x:xs(i)-w/2,y:m.t,width:w,height:H-m.t-m.b,fill:'transparent'},svg);
  hover(h,box,tip,`<b>${l}</b><br>`+s.map(se=>`${se.n}: <b>${(o.fl||pct)(se.v[i])}</b>`).join('<br>'))})}
// Rejilla de ganadores: cols=etiquetas, filas=[{l,s:subtítulo,g:[familias]}]
function rejilla(id,cols,filas,o={}){const [box,W,tip]=caja(id);const m={l:W<500?112:170,r:12,t:W<560?44:24,b:6},cw=(W-m.l-m.r)/cols.length,rh=o.rh||(W<500?24:26),H=m.t+m.b+rh*filas.length;
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);
 cols.forEach((c,j)=>{const x=m.l+j*cw+cw/2;txt(svg,{x,y:m.t-8,'text-anchor':W<560?'start':'middle',transform:W<560?`rotate(-60 ${x} ${m.t-8})`:'','font-size':11.5},W<560?c:c.replace(/^19|^20/,"'"))});
 filas.forEach((f,i)=>{const yy=m.t+i*rh;txt(svg,{x:m.l-6,y:yy+rh/2+4,'text-anchor':'end',class:f.b?'lab':'','font-size':12.5},recorta(f.l,W));
  f.g.forEach((g,j)=>{const r=el('rect',{x:m.l+j*cw+1,y:yy+2,width:cw-2,height:rh-4,rx:2,fill:g?COL[g]:'var(--other)',stroke:f.ok&&f.ok[j]===false?'var(--fg)':'none','stroke-width':2},svg);
   hover(r,box,tip,`<b>${f.l}</b> · ${cols[j]}<br>${g?'Gana '+NOM[g]:'Sin dato'}${f.t?'<br>'+f.t:''}`)})})}
// Dispersión: p=[[x,y,etiqueta,tamaño]]
function dispersion(id,p,o={}){const [box,W,tip]=caja(id);const H=o.h||Math.min(W,440),m={l:44,r:10,t:10,b:40};const x=v=>m.l+v/o.max*(W-m.l-m.r),y=v=>H-m.b-v/o.max*(H-m.t-m.b);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);
 o.ticks.forEach(v=>{el('line',{x1:x(v),x2:x(v),y1:m.t,y2:H-m.b,stroke:'var(--grid)'},svg);el('line',{x1:m.l,x2:W-m.r,y1:y(v),y2:y(v),stroke:'var(--grid)'},svg);
  txt(svg,{x:x(v),y:H-m.b+15,'text-anchor':'middle'},v+'%');txt(svg,{x:m.l-6,y:y(v)+4,'text-anchor':'end'},v+'%')});
 txt(svg,{x:(m.l+W-m.r)/2,y:H-4,'text-anchor':'middle',class:'lab'},o.xl);txt(svg,{x:12,y:(m.t+H-m.b)/2,'text-anchor':'middle',class:'lab',transform:`rotate(-90 12 ${(m.t+H-m.b)/2})`},o.yl);
 p.forEach(d=>{const c=el('circle',{cx:x(d[0]),cy:y(d[1]),r:Math.max(2.2,Math.min(9,Math.sqrt(d[3])/45)),fill:o.c,'fill-opacity':.45,stroke:o.c,'stroke-width':.6},svg);
  hover(c,box,tip,`<b>${d[2]}</b><br>${o.xn}: ${pct(d[0])}<br>${o.yn}: ${pct(d[1])}`)})}
