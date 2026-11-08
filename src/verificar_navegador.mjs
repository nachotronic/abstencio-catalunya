// Abre piezas en Chromium a 390 px y devuelve los errores de JavaScript y el scroll horizontal (control 3 de
// src/controles_calidad.py). Uso: node src/verificar_navegador.mjs 390 actualidad/<slug>/index.html ...
// Sirve el repositorio en un puerto local, así que funciona igual en la GitHub Action y en un hilo.
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)('playwright');   // también con Playwright instalado globalmente (NODE_PATH)

const RAIZ = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const [ancho, ...rutas] = process.argv.slice(2);
const TIPOS = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.geojson': 'application/json', '.topojson': 'application/json', '.woff2': 'font/woff2', '.csv': 'text/csv' };
// Errores de fuera del sitio que no dicen nada de la pieza (la analítica de Cloudflare no responde en local)
const CDN = /^https:\/\/(unpkg\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com)\//;
const AJENOS = /cloudflareinsights|beacon\.min\.js|static\.cloudflareinsights|googletagmanager|net::ERR_(?:NAME_NOT_RESOLVED|INTERNET_DISCONNECTED|FAILED|BLOCKED|CONNECTION)|Failed to load resource|CORS policy/i;

const servidor = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  let f = path.join(RAIZ, p);
  if (!f.startsWith(RAIZ)) { res.writeHead(403); return res.end(); }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': TIPOS[path.extname(f).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
});
await new Promise(r => servidor.listen(0, '127.0.0.1', r));
const base = `http://127.0.0.1:${servidor.address().port}/`;

const salida = { piezas: {} };
const nav = await chromium.launch();
try {
  for (const ruta of rutas) {
    const d = { errores: [], scroll: 0 };
    salida.piezas[ruta] = d;
    const ctx = await nav.newContext({ viewport: { width: +ancho, height: 800 }, deviceScaleFactor: 1 });
    // solo se sirve el repositorio y las bibliotecas de los CDN que usa el sitio (deck.gl, scrollama...): sin ellas,
    // «deck is not defined» sería un falso error. Las fuentes, la analítica y lo demás de fuera no cuentan.
    await ctx.route(u => !u.href.startsWith(base) && !u.href.startsWith('data:') && !CDN.test(u.href), r => r.abort());
    const pag = await ctx.newPage();
    pag.on('pageerror', e => d.errores.push(String(e.message || e).slice(0, 300)));
    pag.on('console', m => { if (m.type() === 'error' && !AJENOS.test(m.text())) d.errores.push(m.text().slice(0, 300)); });
    // un fichero del propio sitio que no carga (datos del mapa, imagen, script) sí es un fallo de la pieza
    pag.on('response', r => { if (r.url().startsWith(base) && r.status() >= 400) d.errores.push(`No carga ${r.url().slice(base.length - 1)} (${r.status()})`); });
    try {
      await pag.goto(base + ruta.replace(/index\.html$/, ''), { waitUntil: 'load', timeout: 45000 });
      // baja hasta el final para que se monten los gráficos y mapas que esperan al scroll
      await pag.evaluate(async () => {
        for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); }
        window.scrollTo(0, 0);
      });
      await pag.waitForTimeout(800);
      const m = await pag.evaluate(() => ({ ancho: document.documentElement.scrollWidth, vista: document.documentElement.clientWidth }));
      d.ancho = m.ancho;
      d.scroll = Math.max(0, m.ancho - m.vista);
    } catch (e) {
      d.fallo = String(e.message || e).slice(0, 300);
    }
    d.errores = [...new Set(d.errores)];
    await ctx.close();
  }
} finally {
  await nav.close();
  servidor.close();
}
console.log(JSON.stringify(salida));
