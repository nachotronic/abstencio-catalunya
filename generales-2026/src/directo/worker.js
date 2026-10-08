// Cloudflare Worker de resultados en directo para la pieza de generales.
// Cada minuto (cron) lee el escrutinio provisional oficial, lo convierte al JSON normalizado que
// entiende la pieza (formato en ../actualizar_29n.py) y lo guarda en KV. La pieza lo pide a
// GET /resultados.json, con CORS abierto y caché de 30 s.
//
// Configuración (wrangler.toml / panel de Cloudflare):
//   FUENTE  Una de dos:
//           - la raíz de la API de la web de resultados de Interior, la que acaba en /backend-difu
//             (en el 23J era https://resultados.generales23j.es/backend-difu); la del 29N se conoce
//             cuando Interior abre su web, normalmente con el simulacro de unos días antes;
//           - o la URL de un JSON ya normalizado (por ejemplo, el simulacro), que pasa tal cual.
//   MODO    'provincias' (por defecto): 52 peticiones, una por provincia con sus municipios dentro.
//           'municipios': una petición por municipio, por tandas de LOTE (por defecto 900) en cada
//           minuto. Es el plan B si la API no devuelve los municipios dentro de la provincia.
//   KV      espacio KV enlazado con el nombre RESULTADOS.
//   CLAVE   secreto para forzar una actualización a mano: GET /actualiza?clave=...
// Hace falta el plan de pago de Workers (5 $/mes): el gratuito corta a los 10 ms de CPU y 50 peticiones.

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(actualiza(env));
  },
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = { 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'public, max-age=30' };
    if (url.pathname === '/actualiza' && env.CLAVE && url.searchParams.get('clave') === env.CLAVE) {
      return new Response(await actualiza(env), { headers: cors });
    }
    if (url.pathname !== '/resultados.json') return new Response('No encontrado', { status: 404 });
    const json = await env.RESULTADOS.get('ultimo');
    if (!json) return new Response('{}', { status: 503, headers: { ...cors, 'Content-Type': 'application/json' } });
    return new Response(json, { headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8' } });
  },
};

export async function actualiza(env) {
  try {
    const out = await leeFuente(env);
    if (!out || !out.mun || !Object.keys(out.mun).length) return 'sin datos';
    out.actualizado = out.actualizado || new Date().toISOString();
    await env.RESULTADOS.put('ultimo', JSON.stringify(out));
    const esc = Object.values(out.mun).filter(a => a[1] > 0).length;
    return `ok ${Object.keys(out.mun).length} municipios, ${esc} con mesas escrutadas`;
  } catch (e) {
    return 'error: ' + e.message;     // se conserva el último resultado bueno
  }
}

async function leeFuente(env) {
  const base = env.FUENTE.replace(/\/+$/, '');
  if (!/\/backend-difu$/.test(base)) return transformar(await pide(base));
  return env.MODO === 'municipios' ? porMunicipios(base, env) : porProvincias(base, env);
}

// ---- JSON ya normalizado (simulacro u otra fuente preparada)
export function transformar(raw) {
  if (raw && raw.mun && raw.siglas) return { eleccion: '2026_11', ...raw };
  throw new Error('La fuente no es un JSON normalizado ni la API de Interior (/backend-difu)');
}

// ---- API de la web de resultados de Interior (la hace Indra; formato visto en la del 23J)
// GET /web/getConfig                                     -> versionNomenclator, grupo, elec[] (Congreso = 2)
// GET /nomenclator/getNomenclator?v=<versión>            -> ámbitos: provincias (l 30) y municipios (l 90)
// GET /scope/data/getScopeData/<scopeId>/<grupo>/<elec>/1/1/<nivel hijos>  -> {scope, mapa: [hijos]}
// GET /scope/data/getScopeData/<scopeId>/<grupo>/<elec>/1/0                 -> {scope} (un municipio)
// En cada ámbito: codigo (INE, 5 dígitos en municipios), censoNoche, escrutinio.{censoNocheEscrutado,
// votosTotales, votosBlancos, votosNulos, partidos[{siglas, votos}]}; las cifras van como {pro, def}.

async function pide(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'mapaelectoral.es (prensa)', Accept: 'application/json' }, cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error(`${r.status} en ${url}`);
  const b = new Uint8Array(await r.arrayBuffer());
  // El nomenclátor puede llegar comprimido sin la cabecera que lo anuncia
  if (b[0] === 0x1f && b[1] === 0x8b) return new Response(new Blob([b]).stream().pipeThrough(new DecompressionStream('gzip'))).json();
  return JSON.parse(new TextDecoder().decode(b));
}

const n = x => (x && typeof x === 'object' ? x.pro : x) || 0;

async function ambitos(base, env) {
  const cfg = await pide(`${base}/web/getConfig`);
  const ver = cfg.versionNomenclator;
  const congreso = (cfg.elec || []).find(e => /congreso/i.test(e.n)) || { elec: 2 };
  const clave = `nomenclator:${ver}`;
  let A = await env.RESULTADOS.get(clave, 'json');
  if (!A) {
    const nom = await pide(`${base}/nomenclator/getNomenclator?v=${ver}`);
    const amb = (nom.amb.find(e => e.elec === congreso.elec) || nom.amb[0]).ambitos;
    A = { prov: amb.filter(a => a.l === 30).map(a => a.c), mun: amb.filter(a => a.l === 90).map(a => [a.c, a.co]) };
    await env.RESULTADOS.put(clave, JSON.stringify(A), { expirationTtl: 86400 * 3 });
  }
  return { ...A, grupo: cfg.grupo || 1, elec: congreso.elec };
}

// Un ámbito de Interior -> fila del JSON normalizado (votos por siglas en un objeto aparte)
export function fila(s) {
  const e = s.escrutinio, votos = {};
  const ct = n(s.censoNoche) || n(s.censoINE);
  if (!e) return { cod: String(s.codigo).padStart(5, '0'), a: [ct, 0, 0, 0, 0], votos };
  for (const p of e.partidos || []) if (n(p.votos)) votos[p.siglas.trim()] = (votos[p.siglas.trim()] || 0) + n(p.votos);
  return { cod: String(s.codigo).padStart(5, '0'), a: [ct, n(e.censoNocheEscrutado), n(e.votosTotales), n(e.votosBlancos), n(e.votosNulos)], votos };
}

function normaliza(filas, previo) {
  // lo que no se haya podido leer esta vez se queda como estaba en la última lectura buena
  const leidos = new Set(filas.map(f => f.cod));
  if (previo && previo.mun) for (const [c, a] of Object.entries(previo.mun)) {
    if (leidos.has(c)) continue;
    const votos = {}; previo.siglas.forEach((s, k) => { if (a[5 + k]) votos[s] = a[5 + k]; });
    filas.push({ cod: c, a: a.slice(0, 5), votos });
  }
  const siglas = [...new Set(filas.flatMap(f => Object.keys(f.votos)))].sort(), mun = {};
  for (const f of filas) if (!/999$/.test(f.cod)) mun[f.cod] = [...f.a, ...siglas.map(s => f.votos[s] || 0)];   // CERA fuera
  return { eleccion: '2026_11', actualizado: new Date().toISOString(), siglas, mun };
}

async function enParalelo(lista, k, fn) {
  const out = []; let i = 0;
  await Promise.all(Array.from({ length: k }, async () => { while (i < lista.length) { const x = lista[i++]; out.push(await fn(x)); } }));
  return out;
}

async function porProvincias(base, env) {
  const A = await ambitos(base, env), filas = [], fallos = [];
  await enParalelo(A.prov, 8, async c => {
    try {
      const d = await pide(`${base}/scope/data/getScopeData/${c}/${A.grupo}/${A.elec}/1/1/90`);
      for (const m of d.mapa || []) if (m.nivel === 90 || String(m.codigo).length === 5) filas.push(fila(m));
    } catch (e) { fallos.push(c); }
  });
  if (!filas.length) throw new Error(`ninguna provincia trajo municipios (${fallos.length} fallos): prueba MODO=municipios`);
  return normaliza(filas, await env.RESULTADOS.get('ultimo', 'json'));
}

async function porMunicipios(base, env) {
  const A = await ambitos(base, env), lote = +env.LOTE || 900;
  const desde = +(await env.RESULTADOS.get('cursor')) || 0;
  const tanda = A.mun.slice(desde, desde + lote), filas = [];
  await enParalelo(tanda, 20, async ([c]) => {
    try { filas.push(fila((await pide(`${base}/scope/data/getScopeData/${c}/${A.grupo}/${A.elec}/1/0`)).scope)); } catch (e) { /* sigue */ }
  });
  await env.RESULTADOS.put('cursor', String(desde + lote >= A.mun.length ? 0 : desde + lote));
  return normaliza(filas, await env.RESULTADOS.get('ultimo', 'json'));
}
