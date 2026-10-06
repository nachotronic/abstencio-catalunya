// Cloudflare Worker de resultados en directo para la pieza de generales.
// Cada minuto (cron) lee el escrutinio provisional oficial, lo convierte al JSON normalizado que
// entiende la pieza (formato en ../actualizar_29n.py) y lo guarda en KV. La pieza lo pide a
// GET /resultados.json, con CORS abierto y caché de 30 s.
//
// Configuración (wrangler.toml / panel de Cloudflare):
//   FUENTE  URL de la fuente oficial. Se conoce unos días antes del 29N (simulacro de Interior).
//   KV      espacio KV enlazado con el nombre RESULTADOS.

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(actualiza(env));
  },
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = { 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'public, max-age=30' };
    if (url.pathname === '/actualiza' && url.searchParams.get('clave') === env.CLAVE) {
      return new Response(await actualiza(env), { headers: cors });
    }
    if (url.pathname !== '/resultados.json') return new Response('No encontrado', { status: 404 });
    const json = await env.RESULTADOS.get('ultimo');
    if (!json) return new Response('{}', { status: 503, headers: { ...cors, 'Content-Type': 'application/json' } });
    return new Response(json, { headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8' } });
  },
};

async function actualiza(env) {
  const r = await fetch(env.FUENTE, { headers: { 'User-Agent': 'mapa-generales (prensa)' }, cf: { cacheTtl: 0 } });
  if (!r.ok) return `fuente ${r.status}`;
  const out = transformar(await r.json());
  if (!out || !out.mun || !Object.keys(out.mun).length) return 'sin datos';
  out.actualizado = out.actualizado || new Date().toISOString();
  await env.RESULTADOS.put('ultimo', JSON.stringify(out));
  return `ok ${Object.keys(out.mun).length} municipios`;
}

// ADAPTADOR: lo único que hay que tocar cuando se conozca el formato oficial del 29N.
// Debe devolver {eleccion, actualizado, siglas: [...], mun: {"28079": [censo_total, censo_escrutado,
// votantes, blancos, nulos, votos_siglas0, votos_siglas1, ...]}}.
// Si la fuente ya es ese JSON (por ejemplo, el simulacro), pasa tal cual.
function transformar(raw) {
  if (raw && raw.mun && raw.siglas) return { eleccion: '2026_11', ...raw };
  throw new Error('Falta escribir el adaptador para el formato de la fuente oficial');
}
