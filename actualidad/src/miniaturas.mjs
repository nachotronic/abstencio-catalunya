// Miniaturas (600 × 400) de las piezas de Actualidad para la franja de la portada.
// Fotografía un gráfico de cada pieza ya construida y lo guarda en img/actualidad/<slug>.jpg.
// Uso, después de construir.py:  node actualidad/src/miniaturas.mjs
// Necesita Playwright con Chromium (en el entorno de Claude ya está instalado).
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

let chromium;
try { ({ chromium } = createRequire(import.meta.url)('playwright')); }
catch { ({ chromium } = createRequire(execSync('npm root -g').toString().trim() + '/')('playwright')); }

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const OUT = path.join(ROOT, 'img', 'actualidad');
// construir.py escribe la lista: [{slug, figura}], figura = índice del gráfico que se fotografía
const lista = JSON.parse(fs.readFileSync(path.join(ROOT, 'actualidad', 'src', 'miniaturas.json'), 'utf8'));
fs.mkdirSync(OUT, { recursive: true });

const exe = fs.existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined;
const b = await chromium.launch(exe ? { executablePath: exe } : {});
for (const { slug, figura } of lista) {
  const salida = path.join(OUT, slug + '.jpg');
  const p = await b.newPage({ viewport: { width: 1000, height: 900 }, deviceScaleFactor: 1.5, colorScheme: 'light' });
  await p.goto('file://' + path.join(ROOT, 'actualidad', slug, 'index.html'));
  await p.waitForTimeout(600);
  await p.evaluate(() => document.querySelectorAll('figure details, figure .src').forEach((d) => d.remove()));
  // el recuadro del gráfico entero: algunos elementos se salen de la caja de <figure>
  const clip = await p.evaluate((i) => {
    const fs = document.querySelectorAll('main figure:not(.foto)'), f = fs[Math.min(i, fs.length - 1)];
    const r = [f, ...f.querySelectorAll('*')].map((e) => e.getBoundingClientRect()).filter((r) => r.width && r.height);
    const x = Math.max(0, Math.min(...r.map((r) => r.left)) - 8), y = Math.min(...r.map((r) => r.top)) - 8 + scrollY;
    return { x, y, width: Math.max(...r.map((r) => r.right)) + 8 - x, height: Math.max(...r.map((r) => r.bottom)) + 8 - y + scrollY };
  }, figura);
  const png = await p.screenshot({ clip, fullPage: true });
  await p.close();
  const m = await b.newPage({ viewport: { width: 600, height: 400 } });
  await m.setContent(`<body style="margin:0;background:#fff"><div style="width:600px;height:400px;background:#fff url(data:image/png;base64,${png.toString('base64')}) center/contain no-repeat;border:14px solid #fff;box-sizing:border-box"></div></body>`);
  await m.screenshot({ path: salida, type: 'jpeg', quality: 82 });
  await m.close();
  console.log('miniatura', slug);
}
await b.close();
