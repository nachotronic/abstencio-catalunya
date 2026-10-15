// Utilidades comunes de las piezas de sistema electoral: colores de partido, tooltip, barras.
const NS='http://www.w3.org/2000/svg';
const OSCURO=()=>document.documentElement.dataset.theme==='dark'||(document.documentElement.dataset.theme!=='light'&&matchMedia('(prefers-color-scheme: dark)').matches);
// Color propio de cada partido (claro, oscuro); las listas pequeñas sin color propio, en gris como «Otros»
const COL={'PP':['#1d84ce','#4fa8ea'],'PSOE':['#e30613','#ff5a5f'],'Vox':['#5ac035','#74d651'],'Sumar':['#a2275f','#d0679a'],
 'Unidas Podemos':['#6b2e68','#a46ba1'],'Más País':['#0f9d7a','#2fc79f'],'Cs':['#eb6109','#ff8a3d'],'ERC':['#f5b324','#f7c454'],
 'Junts':['#20c0b2','#2fd0c2'],'PNV':['#2b8a3e','#4caf63'],'EH Bildu':['#a5c400','#b9d630'],'BNG':['#4a9fdc','#7ab8e6'],
 'CC':['#f7d417','#f9e04a'],'UPN':['#0b3d91','#5b7fd0'],'NA+':['#2a4a8a','#6b88c9'],'CUP':['#d9b600','#ecd13a'],
 'PACMA':['#74a63a','#93c45a'],'Teruel Existe':['#1f6f43','#3f9a68'],'PRC':['#7d9b2a','#a0bf47'],'Nueva Canarias':['#c8a400','#e0c23a'],
 'Soria ¡Ya!':['#2e7d32','#5aa95e'],'UPL':['#6d4c41','#a1887f'],'Por Ávila':['#00796b','#33a99a'],'Frente Obrero':['#b03030','#d96060'],
 'Coalición por Melilla':['#8d6e63','#b39a8f'],'Geroa Bai':['#d43c2f','#e8695e']};
const CORTO={'Santa Cruz de Tenerife':'S. C. Tenerife','Coalición por Melilla':'CPM'};
const col=p=>(COL[p]||['#9a9a9a','#7d7d7d'])[OSCURO()?1:0];
const n0=v=>Math.round(v).toLocaleString('es-ES');
const p1=v=>v.toFixed(1).replace('.',',')+' %';
function el(n,a,p){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}
function tipFor(box){const t=document.createElement('div');t.className='tip';t.hidden=true;box.appendChild(t);
  return {show(h,x,y){t.innerHTML=h;t.hidden=false;const bw=box.clientWidth,tw=t.offsetWidth;t.style.left=Math.min(Math.max(x,tw/2),bw-tw/2)+'px';t.style.top=y+'px'},hide(){t.hidden=true}}}
function pos(box,ev){const r=box.getBoundingClientRect();const p=ev.touches?ev.touches[0]:ev;return [p.clientX-r.left,p.clientY-r.top]}
function hov(box,tip,hit,h){const f=ev=>{const [a,b]=pos(box,ev);tip.show(typeof h==='function'?h():h,a,b)};hit.addEventListener('mousemove',f);hit.addEventListener('touchstart',f,{passive:true});hit.addEventListener('mouseleave',()=>tip.hide())}
// Filas horizontales: cada fila es una barra partida en segmentos de color de partido.
// rows: [{lab, total, segs:[{p, v, h}], txt}] ; total da la longitud de la barra
function filas(id,rows,o={}){const box=document.getElementById(id);box.innerHTML='';const tip=tipFor(box);
  const W=Math.max(box.clientWidth,300),lw=o.lw||(W<480?96:150),rw=o.rw||(W<480?62:84),rh=o.rh||18,gap=o.gap||5;
  const H=rows.length*(rh+gap)+6,s=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);
  const mx=o.max||Math.max(...rows.map(r=>r.total)),sc=v=>v/mx*(W-lw-rw-6);
  rows.forEach((r,i)=>{const y=i*(rh+gap)+3;
    el('text',{x:lw-6,y:y+rh*.72,'text-anchor':'end',class:r.bold?'lab':''},s).textContent=W<480?(CORTO[r.lab]||r.lab):r.lab;
    let x=lw;r.segs.forEach(g=>{const w=sc(g.v);if(w<=0)return;const rc=el('rect',{x,y,width:Math.max(w-(o.sep?1:0),.5),height:rh,fill:col(g.p)},s);hov(box,tip,rc,g.h);x+=w});
    if(r.segs.length===0)el('rect',{x:lw,y:y+rh/2-.5,width:1,height:1,fill:'var(--muted)'},s);
    el('text',{x:lw+sc(r.total)+5,y:y+rh*.72,class:'lab'},s).textContent=r.txt});
}
function leyenda(id,ps){document.getElementById(id).innerHTML=ps.map(p=>`<span><i class="sw" style="background:${col(p)}"></i>${p}</span>`).join('')}
function botones(id,ops,cb,ini=0){const b=document.getElementById(id);b.innerHTML=ops.map(([k,t],i)=>`<button type="button" data-k="${k}" aria-pressed="${i===ini?'true':'false'}">${t}</button>`).join('');
  b.querySelectorAll('button').forEach(x=>x.onclick=()=>{b.querySelectorAll('button').forEach(y=>y.setAttribute('aria-pressed',y===x));cb(x.dataset.k)})}
