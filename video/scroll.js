// Vídeo de scroll de una pieza de Actualidad: baja por la página en móvil (540x960 @2x) siguiendo unos fotogramas clave
// [segundo, scrollY] (con suavizado entre ellos; "lineal" en el tercer valor para un tramo a velocidad constante) y guarda un JPG por fotograma.
// Sirve antes el repo:  python3 -m http.server 8765
// Uso: node video/scroll.js <slug> '<[[0,0],[1.8,0],[4,1500,"lineal"],...]>' <carpeta> ['<[[segundo, "texto del botón"],...]>']
// (los clics opcionales cambian pestañas de un mapa: año, candidato…)
// Después: ffmpeg -framerate 30 -i <carpeta>/f%04d.jpg + un cierre de la plantilla guia (p. ej. shorts/eeuu-scroll-cierre.json).
const { chromium } = require('playwright');
const [slug, kf, dir, clics] = process.argv.slice(2);
const K = JSON.parse(kf), C = JSON.parse(clics || '[]');
const ease = x => x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3)/2;
const yAt = t => {
  for (let i = 0; i < K.length - 1; i++) if (t <= K[i+1][0]) {
    const [a, ya] = K[i], [b, yb, modo] = K[i+1], k = (t - a) / (b - a);
    return ya + (yb - ya) * (modo === 'lineal' ? k : ease(k));
  }
  return K[K.length - 1][1];
};
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  await p.goto(`http://localhost:8765/actualidad/${slug}/`, { waitUntil: 'networkidle' });
  await p.waitForTimeout(1000);
  const fps = 30, N = Math.round(K[K.length - 1][0] * fps);
  for (let f = 0; f < N; f++) {
    const y = Math.round(yAt(f / fps));
    for (const [t, txt] of C) if (Math.round(t * fps) === f)
      await p.evaluate(txt => { const el = [...document.querySelectorAll('button')].find(b => b.textContent.trim() === txt && b.getBoundingClientRect().top > 0 && b.getBoundingClientRect().top < innerHeight); if (el) el.click(); }, txt);
    await p.evaluate(y => new Promise(r => { window.scrollTo(0, y); requestAnimationFrame(() => requestAnimationFrame(r)); }), y);
    await p.screenshot({ path: `${dir}/f${String(f).padStart(4, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
