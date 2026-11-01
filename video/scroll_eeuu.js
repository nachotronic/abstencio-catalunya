// Vídeo de scroll de una pieza (guía de la noche electoral de EE. UU., 1-11-2026): baja por la página en móvil (540x960 @2x) con
// fotogramas clave [segundo, scrollY] y guarda un JPG por fotograma. Sirve el repo antes: python3 -m http.server 8765.
// Uso: node video/scroll_eeuu.js <carpeta>; luego ffmpeg -framerate 30 -i <carpeta>/f%04d.jpg + cierre (shorts/eeuu-scroll-cierre.json).
const { chromium } = require('playwright');
const ease = x => x < .5 ? 4*x*x*x : 1 - Math.pow(-2*x + 2, 3)/2;
// [t, y] keyframes, eased between
const K = [[0,0],[1.8,0],[4.4,1500],[5.2,1500],[6.2,1798],[7.2,1798],[19.2,3420],[21.2,3420]];
const yAt = t => { for (let i = 0; i < K.length-1; i++) if (t <= K[i+1][0]) { const [a,ya]=K[i],[b,yb]=K[i+1]; const k=(t-a)/(b-a); return ya+(yb-ya)*((ya===yb)?0:(i===5?k:ease(k))); } return K[K.length-1][1]; };
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2 });
  await p.goto('http://localhost:8765/actualidad/eeuu-noche-electoral-guia-horarios/', { waitUntil: 'networkidle' });
  await p.waitForTimeout(1000);
  const fps = 30, N = Math.round(21.2 * fps);
  for (let f = 0; f < N; f++) {
    const y = Math.round(yAt(f / fps));
    await p.evaluate(y => new Promise(r => { window.scrollTo(0, y); requestAnimationFrame(() => requestAnimationFrame(r)); }), y);
    await p.screenshot({ path: `${process.argv[2]}/f${String(f).padStart(4,'0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  await b.close();
})();
