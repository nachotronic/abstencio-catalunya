// Vídeo automático de una pieza para X, sin guion: la pieza baja en móvil (540x960 @2x), se para en el titular y en
// cada mapa o gráfico, y acaba con el cierre de la marca (plantilla guia) y la ruta de la pieza.
// Lo lanza .github/workflows/videos.yml para cada pieza nueva del feed; a mano:
//   node video/auto.js /actualidad/<slug>/ salida.mp4
// Sirve el propio repositorio, así que graba lo que hay en la rama, no la web publicada.
// Salida: H.264 1066x1896 (máximo vertical de X), 30 fps, sin audio, por debajo de 9,5 MB.
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), os = require('os'), path = require('path');
const { spawnSync } = require('child_process');

const [ruta, out] = process.argv.slice(2);
if (!ruta || !out) { console.error('Uso: node video/auto.js /actualidad/<slug>/ salida.mp4'); process.exit(2); }
const RAIZ = path.join(__dirname, '..');
const FPS = 30, ALTO = 960, MAX_VISUALES = 4, MAX_BYTES = 9.5e6;
const types = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'text/javascript', '.mjs': 'text/javascript',
  '.svg': 'image/svg+xml', '.css': 'text/css', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp',
  '.avif': 'image/avif', '.geojson': 'application/json', '.woff2': 'font/woff2', '.xml': 'application/xml' };

const srv = http.createServer((q, r) => {
  let f = path.join(RAIZ, decodeURIComponent(q.url.split('?')[0]));
  if (!f.startsWith(RAIZ)) { r.writeHead(403); return r.end(); }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  fs.readFile(f, (e, b) => {
    if (e) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { 'Content-Type': types[path.extname(f).toLowerCase()] || 'application/octet-stream' }); r.end(b);
  });
}).listen(0);

const ease = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
function yEn(K, t) {
  for (let i = 0; i < K.length - 1; i++) if (t <= K[i + 1][0]) {
    const [a, ya] = K[i], [b, yb] = K[i + 1], k = b > a ? (t - a) / (b - a) : 1;
    return ya + (yb - ya) * ease(k);
  }
  return K[K.length - 1][1];
}

// Líneas del cierre: el titular en trozos de ≤17 caracteres si cabe en tres; si no, una frase fija.
function lineasCierre(titulo) {
  const palabras = titulo.replace(/\s+/g, ' ').trim().split(' '), lineas = [''];
  for (const p of palabras) {
    const l = lineas[lineas.length - 1];
    if (!l) lineas[lineas.length - 1] = p;
    else if ((l + ' ' + p).length <= 17) lineas[lineas.length - 1] = l + ' ' + p;
    else lineas.push(p);
  }
  return lineas.length <= 3 && lineas.every(l => l.length <= 18) ? lineas : ['La pieza,', 'con todos', 'sus mapas'];
}

function ff(args) {
  const r = spawnSync('ffmpeg', ['-nostdin', '-y', '-loglevel', 'error', ...args], { stdio: 'inherit' });
  if (r.status !== 0) throw new Error('ffmpeg falló');
}

(async () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'auto-'));
  const base = `http://localhost:${srv.address().port}`;
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 540, height: ALTO }, deviceScaleFactor: 2 });
  await page.goto(base + ruta, { waitUntil: 'networkidle', timeout: 90000 });
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(1200);

  // Titular, antetítulo y los mapas o gráficos de la pieza, de arriba abajo
  const info = await page.evaluate(({ ALTO, MAX }) => {
    const meta = n => (document.querySelector(`meta[property="${n}"],meta[name="${n}"]`) || {}).content || '';
    const raiz = document.querySelector('article') || document.querySelector('main') || document.body;
    const h1 = raiz.querySelector('h1') || document.querySelector('h1');
    const top0 = h1 ? h1.getBoundingClientRect().top + scrollY : 0;
    const cand = [...raiz.querySelectorAll('figure, svg, canvas, .mapa, [id*="mapa"], [class*="grafico"], [class*="chart"], table')]
      .filter(el => !el.closest('header, nav, footer, aside, .compartir, .share'))
      .map(el => { const r = el.getBoundingClientRect(); return { el, top: r.top + scrollY, h: r.height, w: r.width }; })
      .filter(c => c.h >= 160 && c.w >= 260 && c.top > top0 + 200);
    // solo los de más fuera (un <svg> dentro de un <figure> elegido no cuenta otra vez) y separados al menos media pantalla
    const elegidos = [];
    for (const c of cand.sort((a, b) => a.top - b.top)) {
      if (elegidos.some(e => e.el.contains(c.el) || c.el.contains(e.el))) continue;
      if (elegidos.length && c.top - elegidos[elegidos.length - 1].top < ALTO / 2) continue;
      elegidos.push(c);
      if (elegidos.length >= MAX) break;
    }
    const ante = raiz.querySelector('[class*="antetitulo"], [class*="kicker"], .ante');
    return {
      titulo: meta('og:title') || (h1 ? h1.textContent.trim() : document.title),
      ante: ante ? ante.textContent.trim() : '',
      top0: Math.max(0, top0 - 120),
      alto: document.documentElement.scrollHeight,
      visuales: elegidos.map(c => ({ top: c.top, h: c.h })),
    };
  }, { ALTO, MAX: MAX_VISUALES });

  // Fotogramas clave [segundo, scrollY]: titular 2,4 s; cada visual, 1,4 s de viaje y 2,6 s quieto
  const maxY = Math.max(0, info.alto - ALTO);
  const K = [[0, info.top0], [2.4, info.top0]];
  let t = 2.4;
  for (const v of info.visuales) {
    const y = Math.min(maxY, Math.max(0, Math.round(v.h > ALTO - 80 ? v.top - 40 : v.top - (ALTO - v.h) / 2)));
    K.push([t += 1.4, y], [t += 2.6, y]);
  }
  if (!info.visuales.length) K.push([t += 9, Math.min(maxY, info.top0 + 2600)], [t += 1, Math.min(maxY, info.top0 + 2600)]);
  const N = Math.round(t * FPS);
  console.log(`${ruta}: ${info.visuales.length} mapas o gráficos, ${t.toFixed(1)} s de scroll`);
  for (let f = 0; f < N; f++) {
    const y = Math.round(yEn(K, f / FPS));
    await page.evaluate(y => new Promise(r => { window.scrollTo(0, y); requestAnimationFrame(() => requestAnimationFrame(r)); }), y);
    await page.screenshot({ path: path.join(tmp, `f${String(f).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 90 });
  }
  await browser.close();

  // Cierre con la plantilla de las guías
  const nombre = '_auto-cierre-' + process.pid;
  const guion = path.join(__dirname, 'shorts', nombre + '.json');
  const kicker = (info.ante || 'Mapa Electoral').toUpperCase().slice(0, 42);
  fs.writeFileSync(guion, JSON.stringify({ plantilla: 'guia', kicker, fuente: ['Datos y fuentes, en la pieza.'],
    escenas: [{ tipo: 'cierre', dur: 3.0, lineas: lineasCierre(info.titulo), ruta }] }));
  try {
    const r = spawnSync('node', [path.join(__dirname, 'render.js'), nombre, path.join(tmp, 'cierre.mp4')], { stdio: 'inherit' });
    if (r.status !== 0) throw new Error('render.js falló en el cierre');
  } finally { fs.unlinkSync(guion); }

  // Unir, escalar al máximo vertical de X y comprimir hasta que pese menos de 9,5 MB
  for (const crf of [23, 26, 29, 32]) {
    ff(['-framerate', String(FPS), '-i', path.join(tmp, 'f%04d.jpg'), '-i', path.join(tmp, 'cierre.mp4'),
      '-filter_complex', '[0:v]scale=1080:1920,setsar=1,fps=30[a];[1:v]scale=1080:1920,setsar=1,fps=30[b];[a][b]concat=n=2:v=1[c];[c]scale=1066:1896:flags=lanczos[v]',
      '-map', '[v]', '-c:v', 'libx264', '-crf', String(crf), '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', out]);
    const bytes = fs.statSync(out).size;
    console.log(`crf ${crf}: ${(bytes / 1e6).toFixed(1)} MB`);
    if (bytes <= MAX_BYTES) break;
  }
  fs.rmSync(tmp, { recursive: true, force: true });
  srv.close();
})().catch(e => { console.error(e); srv.close(); process.exit(1); });
