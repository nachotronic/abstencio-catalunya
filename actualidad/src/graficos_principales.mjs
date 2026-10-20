// Primeros gráficos de cada pieza, a 1100 px de ancho, para la imagen principal (lo llama graficos_principales.py)
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium'});
const out={};
for (const slug of process.argv.slice(2)){
  const pg=await b.newPage({viewport:{width:1400,height:2400},deviceScaleFactor:1.2});
  await pg.goto(`http://localhost:8765/actualidad/${slug}/`,{waitUntil:'networkidle'});
  await pg.addStyleTag({content:'main,article,.wrap,.col{max-width:none!important;width:auto!important} main figure.cand{width:1100px!important;max-width:none!important;margin:0!important;padding:24px!important;box-sizing:border-box} nav.site,header{display:none!important}'});
  const info=await pg.evaluate(()=>{
    const figs=[...document.querySelectorAll('main figure')].filter(f=>!f.classList.contains('foto')&&f.querySelector('svg,canvas,.chart')).slice(0,4);
    const bg=getComputedStyle(document.body).backgroundColor;
    return figs.map((f,i)=>{f.classList.add('cand');f.id='cand'+i;f.style.background=bg;f.querySelectorAll('details').forEach(d=>d.remove());
      const t=f.querySelector('figcaption .t')||f.querySelector('figcaption b, figcaption strong')||f.querySelector('figcaption'); const src=f.querySelector('.src, .fuente');
      return {titulo:t?t.textContent.trim():'', fuente:src?src.textContent.trim():''}});
  });
  await pg.evaluate(()=>window.dispatchEvent(new Event('resize'))); await pg.waitForTimeout(1200);
  const res=[];
  for (let i=0;i<info.length;i++){const el=await pg.$('#cand'+i); const bb=await el.boundingBox(); await el.screenshot({path:`${process.env.DIR_GRAFICOS}/${slug}-${i}.png`}); res.push({...info[i],w:bb.width,h:bb.height});}
  out[slug]=res; await pg.close();
}
console.log(JSON.stringify(out)); await b.close();
