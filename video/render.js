// Graba una composición HTML fotograma a fotograma y la codifica a MP4.
// Uso: node render.js <guion> <salida.mp4> [fps] [--stills t1,t2,...]   (guion = nombre en shorts/, p. ej. salt)
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const { spawn } = require('child_process');

const [name, out, fpsArg, flag, list] = process.argv.slice(2);
const dir = path.join(__dirname, '..');  // raíz del repo, para servir también /favicon.svg
const plantilla = JSON.parse(fs.readFileSync(path.join(__dirname, 'shorts', name + '.json'))).plantilla || 'short';
const fps = +(fpsArg || 30);
const types = { '.html': 'text/html', '.json': 'application/json', '.js': 'text/javascript', '.svg': 'image/svg+xml' };
const srv = http.createServer((q, r) => {
  const f = path.join(dir, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { 'Content-Type': types[path.extname(f)] || 'application/octet-stream' }); r.end(b); } });
}).listen(0);

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(`http://localhost:${srv.address().port}/video/plantilla/${plantilla}.html?c=${encodeURIComponent(name)}`);
  await page.evaluate(() => window.ready);
  const canvas = await page.$('canvas');
  if (flag === '--stills') {
    for (const t of list.split(',')) {
      await page.evaluate(t => window.render(t), +t);
      await canvas.screenshot({ path: out.replace('%t', t) });
    }
  } else {
    const dur = await page.evaluate(() => window.DUR);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round(dur * fps);
    for (let i = 0; i < n; i++) {
      const png = await page.evaluate(t => { window.render(t); return document.querySelector('canvas').toDataURL('image/png').split(',')[1]; }, i / fps);
      if (!ff.stdin.write(Buffer.from(png, 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
      if (i % 150 === 0) console.log(`fotograma ${i}/${n}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close(); srv.close();
})();
