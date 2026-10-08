// Ejecuta worker.js en Node con un KV en memoria y lo sirve en http://localhost:8787/resultados.json (como wrangler dev).
// Uso:  CADA=15000 node worker_local.mjs ../worker.js http://localhost:8899/backend-difu [provincias|municipios] [lote]
import http from 'http';
const W = (await import(process.argv[2])).default, { actualiza } = await import(process.argv[2]);
const mem = new Map();
const env = { FUENTE: process.argv[3], MODO: process.argv[4] || 'provincias', LOTE: process.argv[5], CLAVE: 'k',
  RESULTADOS: { get: async (k, t) => { const v = mem.get(k); return v == null ? null : t === 'json' ? JSON.parse(v) : v; }, put: async (k, v) => mem.set(k, v) } };
const run = async () => { const t = Date.now(); console.log(new Date().toISOString().slice(11, 19), await actualiza(env), (Date.now() - t) + ' ms'); };
await run(); setInterval(run, +process.env.CADA || 60000);
http.createServer(async (q, res) => {
  const r = await W.fetch(new Request('http://localhost:8787' + q.url), env);
  res.writeHead(r.status, Object.fromEntries(r.headers)); res.end(Buffer.from(await r.arrayBuffer()));
}).listen(8787);
