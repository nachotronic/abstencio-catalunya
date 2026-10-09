// Imágenes para redes sociales (1200 × 630) de la serie «Historia electoral» de Actualidad, con el diseño de atlas/src/compartir.mjs.
// Lee actualidad/src/historia/compartir.json (lo escribe paginas.py) y guarda los JPG en img/compartir/actualidad-<slug>.jpg.
// Uso, después de construir.py y miniaturas.mjs:  node actualidad/src/historia/compartir.mjs
// Necesita Playwright con Chromium (en el entorno de Claude ya está instalado).
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// Playwright puede estar instalado en el proyecto o de forma global
let chromium;
try { ({ chromium } = createRequire(import.meta.url)('playwright')); }
catch { ({ chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright')); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../../..');
const OUT = path.join(ROOT, 'img', 'compartir');
const lista = JSON.parse(fs.readFileSync(path.join(ROOT, 'actualidad', 'src', 'historia', 'compartir.json'), 'utf8'));
fs.mkdirSync(OUT, { recursive: true });

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function html(t) {
  const foto = t.foto && fs.existsSync(path.join(ROOT, t.foto)) ? 'data:image/jpeg;base64,' + fs.readFileSync(path.join(ROOT, t.foto)).toString('base64') : null;
  const largo = t.titular.length > 48;
  return `<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=Newsreader:opsz,wght@6..72,400&display=swap">
<style>
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;background:#faf8f3;color:#1a1a1a;font-family:"IBM Plex Sans",system-ui,sans-serif;display:flex;overflow:hidden}
.txt{flex:1;display:flex;flex-direction:column;padding:56px 60px 48px;border-top:10px solid #b3261e}
.marca{font-weight:700;font-size:20px;letter-spacing:.08em;text-transform:uppercase}
.marca span{color:#5f5d58;font-weight:400}
.serie{margin-top:auto;font-weight:600;font-size:22px;letter-spacing:.06em;text-transform:uppercase;color:#b3261e}
h1{font-weight:700;font-size:${foto ? (largo ? 50 : 58) : (largo ? 62 : 72)}px;line-height:1.05;letter-spacing:-.015em;margin:14px 0 18px;text-wrap:balance}
p{font-family:"Newsreader",Georgia,serif;font-size:${foto ? 25 : 29}px;line-height:1.3;color:#44423d;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.pie{margin-top:28px;font-size:19px;color:#5f5d58}
.foto{width:430px;height:630px;background:#fff center/contain no-repeat}
</style></head><body>
<div class="txt"><div class="marca">Mapa Electoral <span>· Actualidad</span></div>
<div class="serie">${esc(t.serie)}</div><h1>${esc(t.titular)}</h1><p>${esc(t.subtitulo)}</p>
<div class="pie">mapaelectoral.es · Nacho G. del Álamo</div></div>
${foto ? `<div class="foto" style="background-image:url('${foto}')"></div>` : ''}
</body></html>`;
}

const browser = await chromium.launch(fs.existsSync('/opt/pw-browsers/chromium') ? { executablePath: '/opt/pw-browsers/chromium' } : {});
const page = await browser.newPage({ viewport: { width: 1200, height: 630 } });
for (const t of lista) {
  await page.setContent(html(t), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: path.join(OUT, t.archivo), type: 'jpeg', quality: 82 });
}
await browser.close();
console.log(lista.length, 'imágenes en', path.relative(ROOT, OUT));
