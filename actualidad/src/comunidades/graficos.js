// Añadidos para «Las comunidades en las urnas» (se carga detrás de historia/graficos.js).
// Escaños apilados por elección: labs=[años], filas=[{n,c,v:[escaños],lab:[siglas de ese año]}], tot=[escaños de la cámara]
function apiladas(id,labs,filas,tot,o={}){const [box,W,tip]=caja(id);const rot=W<560&&labs.length>8;const H=o.h||(W<500?280:330),m={l:34,r:8,t:18,b:rot?40:28};
 const max=Math.max(...tot),n=labs.length,bw=(W-m.l-m.r)/n,y=v=>H-m.b-v/max*(H-m.t-m.b),pad=Math.min(5,bw*.18);
 const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':o.aria||''},box);
 const tk=[0,Math.round(max/4),Math.round(max/2),Math.round(3*max/4),max];ejeY(svg,W,m,y,tk,v=>v);
 labs.forEach((l,i)=>{const X=m.l+i*bw;let acc=0;
  filas.forEach(f=>{const v=f.v[i];if(!v)return;el('rect',{x:X+pad,y:y(acc+v),width:bw-2*pad,height:y(acc)-y(acc+v),fill:f.c,stroke:'var(--bg)','stroke-width':.6},svg);acc+=v});
  const may=Math.floor(tot[i]/2)+1;el('line',{x1:X+pad-2,x2:X+bw-pad+2,y1:y(may),y2:y(may),stroke:'var(--fg)','stroke-width':1.4,'stroke-dasharray':'3 2'},svg);
  const ord=filas.filter(f=>f.v[i]).sort((a,b)=>b.v[i]-a.v[i]);
  const h=el('rect',{x:X,y:m.t,width:bw,height:H-m.t-m.b,fill:'transparent'},svg);
  hover(h,box,tip,`<b>${l}</b> · ${tot[i]} escaños, mayoría ${may}<br>`+ord.map(f=>`<span style="color:${f.c}">■</span> ${f.lab&&f.lab[i]?f.lab[i]:f.n}: <b>${f.v[i]}</b>`).join('<br>'))});
 labs.forEach((l,i)=>{const x=m.l+i*bw+bw/2;txt(svg,{x,y:H-m.b+16,'text-anchor':rot?'end':'middle',transform:rot?`rotate(-55 ${x} ${H-m.b+12})`:''},rot?String(l):("'"+String(l).slice(2)))});
 tabla(id,['Elección'].concat(filas.map(f=>f.n),['Total']),labs.map((l,i)=>[l].concat(filas.map(f=>f.v[i]||''),[tot[i]])))}
// Mapa municipal: M={w,h,m:[[cod,nombre,trazado,[ganador por elección]]]}, labs=etiquetas de elección; botones para cambiar de elección
function mapa(id,M,labs,o={}){const box=document.getElementById(id);const tip=tipFor(box);
 const bar=document.createElement('div');bar.className='mapa-el';box.appendChild(bar);
 const svg=el('svg',{viewBox:`0 0 ${M.w} ${M.h}`,role:'img','aria-label':o.aria||''},box);svg.style.maxHeight='80vh';
 const res=document.createElement('div');res.className='mapa-res';box.appendChild(res);
 const ps=M.m.map(r=>{const p=el('path',{d:r[2],stroke:'var(--bg)','stroke-width':Math.max(.25,M.w/2500),'stroke-linejoin':'round'},svg);p._r=r;
  const f=ev=>{const [a,b]=pos(box,ev);const g=r[3][cur];tip.show(`<b>${r[1]}</b><br>${labs[cur]}: ${g?'gana '+NOM[g]:'sin dato'}`,a,b)};
  p.addEventListener('mousemove',f);p.addEventListener('touchstart',f,{passive:true});p.addEventListener('mouseleave',()=>tip.hide());return p});
 let cur=labs.length-1;
 const pinta=i=>{cur=i;const n={};ps.forEach(p=>{const g=p._r[3][i];p.setAttribute('fill',g?COL[g]:'var(--other)');if(g)n[g]=(n[g]||0)+1});
  [...bar.children].forEach((b,j)=>b.setAttribute('aria-pressed',j==i));
  res.innerHTML=`<b>${labs[i]}</b>: `+Object.entries(n).sort((a,b)=>b[1]-a[1]).map(([g,v])=>`<span class="sw" style="background:${COL[g]}"></span> ${NOM[g]} ${v}`).join(' · ')+' municipios'};
 labs.forEach((l,i)=>{const b=document.createElement('button');b.type='button';b.textContent=l;b.onclick=()=>pinta(i);bar.appendChild(b)});
 pinta(cur)}
