// Cloudflare Worker de resultados en directo para la pieza de generales.
// Cada minuto (cron) lee el escrutinio provisional oficial, lo convierte al JSON normalizado que
// entiende la pieza (formato en ../actualizar_29n.py) y lo guarda en KV. La pieza lo pide a
// GET /resultados.json (el mapa, todo el país) y las fichas de municipio a GET /provincia/<pp>.json (solo su provincia,
// unos 30 KB en vez de 1,4 MB cada minuto), con CORS abierto y caché de 30 s.
//
// Configuración (wrangler.toml / panel de Cloudflare):
//   FUENTE  Una de dos:
//           - la raíz de la API de la web de resultados de Interior, la que acaba en /backend-difu
//             (en el 23J era https://resultados.generales23j.es/backend-difu); la del 29N se conoce
//             cuando Interior abre su web, normalmente con el simulacro de unos días antes;
//           - o la URL de un JSON ya normalizado (por ejemplo, el simulacro), que pasa tal cual.
//           - o la raíz de la API de descargas para medios acreditados (acaba en /descargas/csv; manual
//             «API de descargas · Elecciones Generales 29N 2026»), con MODO = 'medios' y los secretos
//             MEDIOS_USUARIO y MEDIOS_CLAVE que Interior da a cada medio;
//   MODO    'provincias' (por defecto): 52 peticiones, una por provincia con sus municipios dentro.
//           'municipios': una petición por municipio, por tandas de LOTE (por defecto 900) en cada
//           minuto. Es el plan B si la API no devuelve los municipios dentro de la provincia.
//   KV      espacio KV enlazado con el nombre RESULTADOS.
//   DIA     (opcional) AAMMDD del día que vale, 261129 la noche electoral: descarta registros de otros días (pruebas).
//   PUBLICA (opcional) hora ISO antes de la cual no se guarda ningún voto ni escaño (2026-11-29T20:00:00Z, las 21:00).
//   MESAS   (opcional) raíz de los ficheros por mesa si no es ninguna de las que se prueban (ver mesas()).
//   CLAVE   secreto para forzar una actualización a mano: GET /actualiza?clave=...
// Hace falta el plan de pago de Workers (5 $/mes): el gratuito corta a los 10 ms de CPU y 50 peticiones.
// Cómo desplegarlo y encenderlo: DESPLIEGUE.md (y el workflow .github/workflows/directo-worker.yml).

export default {
  async scheduled(event, env, ctx) {
    // el resultado de cada lectura (ok o el error) queda en KV para verlo en GET /estado, sin datos ni claves
    ctx.waitUntil(actualiza(env).then(m => { console.log(m); return env.RESULTADOS.get('mesas').then(ms => env.RESULTADOS.put('estado', JSON.stringify({ t: new Date().toISOString(), m, av: MUESTRA_AV, sen: MUESTRA_SEN, mesas: ms ? JSON.parse(ms) : null }))); }));
  },
  async fetch(req, env) {
    const url = new URL(req.url);
    const cors = { 'Access-Control-Allow-Origin': '*', 'Cache-Control': 'public, max-age=30' };
    if (url.pathname === '/actualiza' && env.CLAVE && url.searchParams.get('clave') === env.CLAVE) {
      return new Response(await actualiza(env), { headers: cors });
    }
    const pr = url.pathname.match(/^\/provincia\/(\d{2})\.json$/);
    // Vista previa (solo para revisar antes de fusionar; se quita después del 29N): la portada publicada con el app.js de un
    // commit de la rama, servido por este Worker desde GitHub. /vista?v=<sha> ; el directo es este mismo Worker.
    const gh = url.pathname.match(/^\/vista\/gh\/([0-9a-f]{7,40})\/(generales-2026\/[\w\/.-]+\.(js|json))$/);
    if (gh) {   // ficheros de la rama, sin el 403 que da jsDelivr a algunos navegadores
      const r = await fetch(`https://raw.githubusercontent.com/nachotronic/abstencio-catalunya/${gh[1]}/${gh[2]}`, { cf: { cacheTtl: 300 } });
      return new Response(r.body, { status: r.status, headers: { ...cors, 'Cache-Control': 'public, max-age=300',
        'Content-Type': gh[3] === 'js' ? 'text/javascript; charset=utf-8' : 'application/json; charset=utf-8', 'X-Robots-Tag': 'noindex' } });
    }
    const fuera = url.pathname.match(/^\/vista\/gh\/[0-9a-f]{7,40}\/(.*)$/);   // el resto de enlaces, a la web publicada
    if (fuera && !gh) return Response.redirect('https://mapaelectoral.es/' + fuera[1] + url.search + url.hash, 302);
    if (url.pathname === '/vista') {
      const v = /^[0-9a-f]{7,40}$/.test(url.searchParams.get('v') || '') ? url.searchParams.get('v') : null;
      if (!v) return new Response('Falta ?v=<commit>', { status: 400 });
      if (!url.searchParams.get('directo')) return Response.redirect(`${url.origin}/vista?v=${v}&directo=${url.origin}/resultados.json`, 302);
      const cdn = `${url.origin}/vista/gh/${v}/generales-2026/app.js`;
      const html = (await (await fetch('https://mapaelectoral.es/', { cf: { cacheTtl: 60 } })).text())
        .replace('<head>', '<head><base href="https://mapaelectoral.es/"><meta name="robots" content="noindex">')
        .replace('src="generales-2026/app.js"', `src="${cdn}"`)
        // como quedará la portada servida en la veda (src/quitar_encuestas_portada.py, hilo de /encuestas/): sin el bloque
        // de encuestas ni las tarjetas de encuestas de los carruseles, ya en el HTML
        .replace(/<!--encuestas:portada-->[\s\S]*?<!--\/encuestas:portada-->\n?/, '')
        // (y, como se ha propuesto en ese hilo, la tarjeta del simulador de pactos con encuestas y el enlace del menú)
        .replace(/<!--(actualidad:ultimas|actualidad:mapa|videos:portada|atlas:ultimas)-->[\s\S]*?<!--\/\1-->/g, b =>
          b.replace(/<li><a href="[^"]*"[^>]*>[\s\S]*?<\/li>/g, li => /encuesta|sondeo/i.test(li.replace(/<img[^>]*>|<source[^>]*>/g, '')) ? '' : li))
        .replace('<a href="encuestas/">Encuestas</a>', '')
        .replace(/<a class="atlas" href="encuestas\/simulador-pactos\/">[\s\S]*?<\/a>/, '');
      return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'X-Robots-Tag': 'noindex' } });
    }
    const sc = url.pathname.match(/^\/secciones\/(\d{2})\.json$/);
    if (sc) {
      const j = await env.RESULTADOS.get('secc:' + sc[1]);
      return new Response(j || '{}', { status: j ? 200 : 404, headers: { ...cors, 'Cache-Control': 'public, max-age=60', 'Content-Type': 'application/json; charset=utf-8' } });
    }
    // titular del sondeo a pie de urna (lo pone a mano el workflow directo-pieurna.yml): nunca antes de PIEURNA_DESDE
    if (url.pathname === '/pieurna.json') {
      const j = Date.now() >= Date.parse(env.PIEURNA_DESDE || PIEURNA_DESDE) ? await env.RESULTADOS.get('pieurna') : null;
      return new Response(j || '{}', { status: j ? 200 : 404, headers: { ...cors, 'Cache-Control': 'public, max-age=30', 'Content-Type': 'application/json; charset=utf-8' } });
    }
    if (url.pathname === '/estado') return new Response((await env.RESULTADOS.get('estado')) || '{}', { headers: { ...cors, 'Cache-Control': 'no-store', 'Content-Type': 'application/json' } });
    if (url.pathname !== '/resultados.json' && !pr) return new Response('No encontrado', { status: 404 });
    const json = await env.RESULTADOS.get(pr ? 'prov:' + pr[1] : 'ultimo');
    if (!json) return new Response('{}', { status: 503, headers: { ...cors, 'Content-Type': 'application/json' } });
    return new Response(json, { headers: { ...cors, 'Content-Type': 'application/json; charset=utf-8' } });
  },
};

// el cierre de los colegios de la Península, el 29N (20:00 en Madrid); las pruebas lo adelantan con la variable PIEURNA_DESDE
const PIEURNA_DESDE = '2026-11-29T19:00:00Z';

export async function actualiza(env) {
  try {
    const out = await leeFuente(env);
    if (!out || !out.mun || !Object.keys(out.mun).length) return 'sin datos';
    out.actualizado = out.actualizado || new Date().toISOString();
    const previo = await env.RESULTADOS.get('ultimo', 'json');
    out.hitos = hitos(out, (previo && previo.hitos) || []);
    await env.RESULTADOS.put('ultimo', JSON.stringify(out));
    await Promise.all(Object.entries(porProvincia(out)).map(([p, o]) => env.RESULTADOS.put('prov:' + p, JSON.stringify(o))));
    const esc = Object.values(out.mun).filter(a => a[1] > 0).length;
    return `ok ${Object.keys(out.mun).length} municipios, ${esc} con mesas escrutadas`;
  } catch (e) {
    return 'error: ' + e.message;     // se conserva el último resultado bueno
  }
}

// El JSON normalizado partido por provincia (dos primeras cifras del código INE), con solo las siglas que tienen votos allí
export function porProvincia(out) {
  const grupos = {};
  for (const [c, a] of Object.entries(out.mun)) (grupos[c.slice(0, 2)] ||= []).push([c, a]);
  const res = {};
  for (const [p, filas] of Object.entries(grupos)) {
    const k = out.siglas.map((_, i) => i).filter(i => filas.some(([, a]) => a[5 + i]));
    const mun = {};
    for (const [c, a] of filas) mun[c] = [...a.slice(0, 5), ...k.map(i => a[5 + i])];
    const { escanos, avances, avmun, hitos: _h, ambitos: _a, senado: _s, ant23: _t, ...resto } = out;   // los hitos solo van en el total de España
    res[p] = { ...resto, siglas: k.map(i => out.siglas[i]), mun, ...(escanos && escanos[p] ? { escanos: { [p]: escanos[p] } } : {}),
      ...(avances ? { avances: { es: avances.es, pr: avances.pr && avances.pr[p] ? { [p]: avances.pr[p] } : {} } } : {}),
      ...(avmun ? { avmun: Object.fromEntries(Object.entries(avmun).filter(([c]) => c.startsWith(p))) } : {}) };
  }
  return res;
}

// ---- Hitos del directo: frases que se añaden solas cuando el escrutinio cruza un umbral o cambia el primero.
// Van en resultados.json («hitos», el más reciente al final) y la página de resultados las enseña como entradas del directo.
// Solo describen datos (escrutado, porcentajes sobre voto válido sin CERA y escaños si los da Interior); nada de proyecciones.
const UMBRALES = [5, 10, 25, 50, 75, 90, 95, 99];
const fmt = x => x.toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
// PP y PSOE con sus listas territoriales (PSC, PSE-EE, UPN-PP…), como en la página; el resto, cada candidatura con sus siglas
// Frente Amplio (Sumar, IU y otros) va con nombres distintos en cada comunidad: se suman. Podemos va aparte, salvo en las listas
// conjuntas de Canarias (NC-BC, Podemos, IU y Sumar) y la Comunitat Valenciana (Compromís, EUPV y Podem), que van con el Frente Amplio
const MISMO = [['Frente Amplio', /FRENTE AMPLIO|FRONT AMPLI|FRONTE AMPLA|FRONTE ZABALA|^FA$|^COMUNS|^ARAM[EÉ]S|PODEMOS, IU, SUMAR|^COMPROM/], ['PP', /^(PP\b|PP-|P\.P\.|UPN-PP)/], ['PSOE', /PSOE(?! ?\(?H)|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN/]];
const NOMBRE = { 'B.N.G.': 'BNG', 'EAJ-PNV': 'PNV', 'JXCAT - JUNTS': 'Junts', 'JXCAT-JUNTS': 'Junts', 'JXCAT': 'Junts', 'TERUEL EXISTE': 'Teruel Existe', 'EH BILDU': 'EH Bildu', 'VOX': 'Vox', 'CCA': 'Coalición Canaria',
    'U.P.N.': 'UPN', 'SUMAR': 'Sumar', 'PODEMOS': 'Podemos', 'CUP-PR': 'CUP', 'SALF': 'Se Acabó la Fiesta' };
export const grupoSiglas = s => { const a = (s || '').toUpperCase().trim(); for (const [g, r] of MISMO) if (r.test(a)) return g; return NOMBRE[a] || s; };
export function resumenEspana(out) {
  let ct = 0, ce = 0, bl = 0; const v = out.siglas.map(() => 0);
  for (const a of Object.values(out.mun)) { ct += a[0]; ce += a[1]; bl += a[3]; for (let k = 0; k < v.length; k++) v[k] += a[5 + k] || 0; }
  const val = v.reduce((t, x) => t + x, 0) + bl;
  const g = {}; out.siglas.forEach((s, k) => { if (v[k]) g[grupoSiglas(s)] = (g[grupoSiglas(s)] || 0) + v[k]; });
  const orden = Object.entries(g).sort((a, b) => b[1] - a[1]);
  const esc = {};
  if (out.escanos) for (const d of Object.values(out.escanos)) for (const [s, n] of Object.entries(d)) esc[grupoSiglas(s)] = (esc[grupoSiglas(s)] || 0) + n;
  return { esc: ct ? ce / ct * 100 : 0, val, orden, escanos: Object.entries(esc).filter(x => x[1]).sort((a, b) => b[1] - a[1]) };
}
export function hitos(out, previos) {
  const H = previos.slice(), R = resumenEspana(out);
  if (!R.val || !R.orden.length) return H;
  const hora = out.actualizado, ult = H[H.length - 1];
  const top = R.orden.slice(0, 3).map(([s, n]) => `${s}, ${fmt(n / R.val * 100)} %`).join('; ');
  const asientos = R.escanos.length ? ` Escaños provisionales de Interior: ${R.escanos.slice(0, 5).map(([s, n]) => `${s} ${n}`).join(', ')}.` : '';
  const nuevo = (tipo, texto) => H.push({ t: hora, tipo, esc: Math.round(R.esc * 10) / 10, primero: R.orden[0][0], texto });
  if (!ult) nuevo('inicio', `Primeros datos del escrutinio: escrutado el ${fmt(R.esc)} % del censo. ${top}.${asientos}`);
  else {
    if (ult.primero !== R.orden[0][0]) nuevo('lider', `Con el ${fmt(R.esc)} % escrutado, ${R.orden[0][0]} pasa a ser la candidatura más votada. ${top}.${asientos}`);
    const u = UMBRALES.filter(x => (ult.esc || 0) < x && R.esc >= x).pop();
    if (u) nuevo('umbral', `Escrutado el ${fmt(R.esc)} % del censo. ${top}.${asientos}`);
  }
  return H.slice(-60);
}

async function leeFuente(env) {
  const base = env.FUENTE.replace(/\/+$/, '');
  if (env.MODO === 'medios' || /\/descargas\/csv$/.test(base)) return porMedios(base, env);
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
  const A = await ambitos(base, env), filas = [], fallos = [], escanos = {};
  await enParalelo(A.prov, 8, async c => {
    try {
      const d = await pide(`${base}/scope/data/getScopeData/${c}/${A.grupo}/${A.elec}/1/1/90`);
      // Si la provincia trae los diputados provisionales de cada candidatura («cargos», sin confirmar con datos reales:
      // la muestra del 23J es de un municipio), se guardan; el código de provincia sale de sus municipios.
      const pe = d.scope && d.scope.escrutinio, m0 = (d.mapa || [])[0];
      if (pe && pe.partidos && m0) { const e = {}; for (const p of pe.partidos) if (n(p.cargos)) e[p.siglas.trim()] = n(p.cargos); if (Object.keys(e).length) escanos[String(m0.codigo).padStart(5, '0').slice(0, 2)] = e; }
      for (const m of d.mapa || []) if (m.nivel === 90 || String(m.codigo).length === 5) filas.push(fila(m));
    } catch (e) { fallos.push(c); }
  });
  if (!filas.length) throw new Error(`ninguna provincia trajo municipios (${fallos.length} fallos): prueba MODO=municipios`);
  const out = normaliza(filas, await env.RESULTADOS.get('ultimo', 'json'));
  return Object.keys(escanos).length ? { ...out, escanos } : out;
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

// ---- API de descargas para medios acreditados (manual de Interior para el 29N)
// GET <base>/data/getEnvio/2                               -> número del último envío del Congreso
// GET <base>/data/getEscrutinioTotales/2/<envío>           -> TO, CM y PR (con diputados electos por candidatura)
// GET <base>/data/getEscrutinioMunicipios/2/<pp>/<envío>   -> municipios (distrito 99) y distritos de 7 ciudades
// Registros de texto con campos separados por «;» (las longitudes del manual no cuentan el separador) y CR LF;
// porcentajes con dos decimales implícitos. Todas las llamadas de una lectura usan el mismo envío, como pide el manual.
// Un envío que ya se leyó no se vuelve a pedir: así, entre envío y envío, el Worker solo hace una petición por minuto.
const ANCHO_MUN = [10, 2, 2, 1, 3, 2, 50, 2, 2, 5, 8, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5], CAND_MUN = [4, 55, 8, 5];
const ANCHO_TOT = [10, 2, 2, 2, 1, 50, 5, 8, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5, 3, 4, 4, 8], CAND_TOT = [4, 55, 8, 5, 3];

// Una línea -> campos. Con «;» se parte por el separador; si no lo trae, por las longitudes del manual.
export function campos(linea, fijo, cand) {
  if (linea.includes(';')) return linea.split(';').map(x => x.trim());
  const out = []; let i = 0;
  for (const w of fijo) { out.push(linea.slice(i, i + w).trim()); i += w; }
  while (i < linea.length) for (const w of cand) { out.push(linea.slice(i, i + w).trim()); i += w; }
  return out;
}
const lineas = t => t.split(/\r?\n/).filter(l => l.trim());
const ent = x => parseInt(x, 10) || 0;

// Registro de municipio -> fila normalizada (null para los distritos, que van aparte del total del municipio)
export function filaMedios(linea) {
  const c = campos(linea, ANCHO_MUN, CAND_MUN);
  if (c[5] !== '99') return null;
  const votos = {};
  for (let k = ANCHO_MUN.length; k + 2 < c.length; k += CAND_MUN.length) {
    const s = c[k + 1], v = ent(c[k + 2]);
    if (s && v) votos[s] = (votos[s] || 0) + v;
  }
  return { cod: c[2].padStart(2, '0') + c[4].padStart(3, '0'), fecha: c[0], a: [ent(c[10]), ent(c[11]), ent(c[13]), ent(c[17]), ent(c[19])], votos };
}

// Registros PR del fichero de totales -> {pp: {siglas: diputados}}
export function escanosMedios(texto) {
  const esc = {};
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_TOT, CAND_TOT);
    if (c[1] !== 'PR') continue;
    const d = {};
    for (let k = ANCHO_TOT.length; k + 4 < c.length; k += CAND_TOT.length) if (c[k + 1] && ent(c[k + 4])) d[c[k + 1]] = ent(c[k + 4]);
    esc[c[3].padStart(2, '0')] = d;
  }
  return esc;
}

// Fichero de totales del Congreso -> {TO, CM: {cc}, PR: {pp}}: nombre, % escrutado, a elegir y [siglas, votos, escaños]
export function ambitosMedios(texto) {
  const R = { TO: null, CM: {}, PR: {} };
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_TOT, CAND_TOT), t = c[1];
    if (!['TO', 'CM', 'PR'].includes(t)) continue;
    const cand = [];
    for (let k = ANCHO_TOT.length; k + 4 < c.length; k += CAND_TOT.length) if (c[k + 1] && (ent(c[k + 2]) || ent(c[k + 4]))) cand.push([c[k + 1], ent(c[k + 2]), ent(c[k + 4])]);
    // ct: censo, ce: censo de las mesas escrutadas, vo: votantes, nu: nulos (para la participación con el total de Interior)
    const o = { n: c[5], esc: ent(c[9]) / 100, el: ent(c[18]), bl: ent(c[14]), ct: ent(c[7]), ce: ent(c[8]), vo: ent(c[10]), nu: ent(c[16]), c: cand };
    if (t === 'TO') R.TO = o; else if (t === 'CM') R.CM[c[2].padStart(2, '0')] = o; else R.PR[c[3].padStart(2, '0')] = o;
  }
  return R;
}
// Senado (getEscrutinioTotales/3): TO y CM, senadores electos por candidatura; CI (circunscripción), cada candidato con sus
// votos y si sale elegido. Elemento: código, siglas, orden, nombre, votos, %, electo(s).
const ANCHO_SEN = [10, 2, 2, 2, 1, 50, 5, 8, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5, 3], CAND_SEN = [4, 55, 3, 90, 8, 5, 3];
export function senadoMedios(texto) {
  const R = { TO: null, CM: {}, CI: {} };
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_SEN, CAND_SEN), t = c[1];
    if (!['TO', 'CM', 'CI'].includes(t)) continue;
    const cand = [];
    for (let k = ANCHO_SEN.length; k + 6 < c.length; k += CAND_SEN.length) if (c[k + 1]) {
      if (t === 'CI') cand.push([c[k + 1], c[k + 3], ent(c[k + 4]), ent(c[k + 6])]);
      else if (ent(c[k + 6])) cand.push([c[k + 1], ent(c[k + 6])]);
    }
    const o = { n: c[5], esc: ent(c[9]) / 100, el: ent(c[18]), c: cand };
    if (t === 'TO') R.TO = o; else if (t === 'CM') R.CM[c[2].padStart(2, '0')] = o; else R.CI[c[3].padStart(2, '0') + c[4]] = o;
  }
  return R;
}
// Senado 2023 (fijos/…/ANT/3/07-23): cada elemento es código, siglas y senadores electos, en todos los niveles
export function senado23Medios(texto) {
  const R = { TO: null, CM: {}, CI: {} };
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_SEN, [4, 55, 3]), t = c[1];
    if (!['TO', 'CM', 'CI'].includes(t)) continue;
    const cand = [];
    for (let k = ANCHO_SEN.length; k + 2 < c.length; k += 3) if (c[k + 1] && ent(c[k + 2])) cand.push([c[k + 1], ent(c[k + 2])]);
    const o = { n: c[5], el: ent(c[18]), c: cand };
    if (t === 'TO') R.TO = o; else if (t === 'CM') R.CM[c[2].padStart(2, '0')] = o; else R.CI[c[3].padStart(2, '0') + c[4]] = o;
  }
  return R;
}
let MUESTRA_SEN = '';

async function pideTexto(url, env) {
  const r = await fetch(url, { headers: cabeceras(env), cf: { cacheTtl: 0 } });
  if (!r.ok) throw new Error(`${r.status} en ${url}`);
  const b = new Uint8Array(await r.arrayBuffer());
  let t;
  if (/latin|8859|1252/i.test(env.MEDIOS_CODIFICACION || '')) { t = ''; for (const x of b) t += String.fromCharCode(x); } else t = new TextDecoder().decode(b);
  // DIA (AAMMDD, por ejemplo 261129): solo valen los registros totalizados ese día. Así, si Interior aún sirve los datos de una
  // prueba anterior, el Worker no los toma por los de la noche electoral (se quedan fuera y la web sigue como estaba).
  if (env.DIA && !/getEnvio|\/fijos\//.test(url)) t = t.split(/\r?\n/).filter(l => l.trim() && (!/^\d{6}/.test(l) || l.startsWith(env.DIA))).join('\n');   // fuera solo lo fechado otro día
  return t;
}

// Avances de participación (getAvancesTotales/2/<envío>): registros TO, CM y PR con dos avances
// (mesas, censo y participación con dos decimales implícitos). -> {fecha, es: [p1, p2], pr: {pp: [p1, p2]}, mesas}, en %;
// mesas: total, constituidas y suspendidas de España (constitución de mesas, a las 9:30 el 29N).
const ANCHO_AV = [10, 2, 2, 2, 1, 50, 5, 5, 5, 8, 8, 8], CAND_AV = [5, 8, 5];
export function avancesMedios(texto) {
  const out = { fecha: '', es: null, pr: {} };
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_AV, CAND_AV);
    const av = [0, 1].map(i => { const m = ent(c[12 + 3 * i]), p = ent(c[14 + 3 * i]); return m ? p / 100 : null; });
    if (c[0] > out.fecha) out.fecha = c[0];
    if (c[1] === 'TO') { out.es = av; out.mesas = { total: ent(c[6]), constituidas: ent(c[7]), suspendidas: ent(c[8]) }; }
    else if (c[1] === 'PR') out.pr[c[3].padStart(2, '0')] = av;
  }
  return out;
}
// Avances por municipio (getAvancesMunicipios/2/<pp>/<envío>), distrito 99 -> {cod5: [1.er avance, 2.º avance]}, en % (null si falta)
const ANCHO_AVM = [10, 2, 2, 1, 3, 2, 50, 2, 2, 5, 5, 5, 8, 8, 8];
export function avancesMunicipios(texto) {
  const out = {};
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_AVM, CAND_AV);
    if (c[5] !== '99') continue;
    const av = [0, 1].map(i => ent(c[15 + 3 * i]) ? ent(c[17 + 3 * i]) / 100 : null);
    if (av.some(x => x != null)) out[c[2].padStart(2, '0') + c[4].padStart(3, '0')] = av;
  }
  return out;
}
// ---- Mesas (manual final del 23-11): /mesas/getAvances/2/<pp>.csv al acabar cada avance y /mesas/getEscrutinio/2/<pp>.csv
// al acabar el recuento provisional. Cada mesa trae distrito y sección: se suman por sección censal, con el código INE de 10
// cifras (provincia, municipio, distrito, sección) que usan las secciones del mapa.
const ANCHO_MESA = [10, 2, 2, 1, 3, 2, 3, 1, 50, 2, 2];
const ANCHO_AVMESA = [...ANCHO_MESA, 5, 5, 5, 8, 8, 8];
const ANCHO_ESCMESA = [...ANCHO_MESA, 5, 8, 8, 5, 8, 5, 8, 5, 8, 5, 8, 5];
const secDe = c => c[2].padStart(2, '0') + c[4].padStart(3, '0') + c[5].padStart(2, '0') + c[6].padStart(3, '0');
// -> {cod10: [[censo de las mesas que dieron el 1.er avance, votantes], [lo mismo del 2.º]]}
export function avancesMesas(texto) {
  const out = {};
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_AVMESA, CAND_AV); if (!/^\d+$/.test(c[6] || '') || !/^\d+$/.test(c[2] || '')) continue;
    const s = out[secDe(c)] ||= [[0, 0], [0, 0]];
    [0, 1].forEach(k => { const m = ent(c[17 + 3 * k]), ce = ent(c[18 + 3 * k]), p = ent(c[19 + 3 * k]); if (m && ce) { s[k][0] += ce; s[k][1] += Math.round(ce * p / 10000); } });
  }
  return out;
}
// -> {siglas: [...], s: {cod10: [censo de las mesas totalizadas, votantes, blancos, nulos, votos de cada sigla]}, completa}
export function escrutinioMesas(texto) {
  const sec = {}, sig = new Map(); let total = 0, hecho = 0;
  for (const l of lineas(texto)) {
    const c = campos(l, ANCHO_ESCMESA, CAND_MUN); if (!/^\d+$/.test(c[6] || '') || !/^\d+$/.test(c[2] || '')) continue;
    total += ent(c[12]); hecho += ent(c[13]);
    if (!ent(c[13])) continue;   // mesa aún sin totalizar
    const s = sec[secDe(c)] ||= [0, 0, 0, 0, {}];
    s[0] += ent(c[13]); s[1] += ent(c[15]); s[2] += ent(c[19]); s[3] += ent(c[21]);
    for (let k = ANCHO_ESCMESA.length; k + 2 < c.length; k += CAND_MUN.length) {
      const g = c[k + 1], v = ent(c[k + 2]); if (!g || !v) continue;
      s[4][g] = (s[4][g] || 0) + v; sig.set(g, (sig.get(g) || 0) + v);
    }
  }
  const siglas = [...sig.keys()].sort((a, b) => sig.get(b) - sig.get(a));
  const s = Object.fromEntries(Object.entries(sec).map(([k, [ce, vo, bl, nu, v]]) => [k, [ce, vo, bl, nu, ...siglas.map(g => v[g] || 0)]]));
  return { siglas, s, completa: total > 0 && hecho >= total, mesas: total > 0 };
}
// Cada 5 minutos como mucho, y solo lo que falta: los avances de mesa cuando Interior ya ha dado ese avance y el escrutinio
// de mesa de las provincias que aún no lo tienen completo. Guarda 'secc:<pp>' en KV y devuelve el resumen para resultados.json.
async function mesas(base, env, F) {
  const st = (await env.RESULTADOS.get('mesas', 'json')) || { av: [], esc: {}, base: null, t: 0 };
  const res = () => ({ t: st.ver || '', av: st.av, esc: Object.keys(st.esc).sort(), base: st.base ? 'ok' : (st.prueba || '') });
  const quiereAv = [1, 2].filter(k => F.avances && F.avances.es && F.avances.es[k - 1] != null && !st.av.includes(k));
  const quiereEsc = !!(F.mun && Object.values(F.mun).some(a => a[1] > 0)) && PROVINCIAS.some(p => st.esc[p] !== 'completa');
  if ((!quiereAv.length && !quiereEsc) || Date.now() - st.t < 5 * 60e3) return res();
  st.t = Date.now();
  if (!st.base) {   // el manual da la ruta /mesas/… sin decir la raíz: se prueba con las tres posibles y se apunta la que responde
    const o = new URL(base).origin, prueba = [];
    for (const b of env.MESAS ? [env.MESAS] : [o + '/mesas', base + '/mesas', o + '/descargas/mesas', base + '/data/mesas']) {
      const r = await fetch(`${b}/${quiereAv.length ? 'getAvances' : 'getEscrutinio'}/2/28.csv`, { headers: cabeceras(env), cf: { cacheTtl: 0 } }).catch(() => null);
      const t = r && !r.ok ? (await r.text().catch(() => '')).replace(/\s+/g, ' ').slice(0, 60) : '';
      prueba.push((r ? r.status : 'x') + ' ' + b.replace(o, '') + (t ? ' «' + t + '»' : ''));
      if (r && r.ok) { st.base = b; break; }
    }
    st.prueba = prueba.join(' · ');
    if (!st.base) { await env.RESULTADOS.put('mesas', JSON.stringify(st)); return res(); }
  }
  let cambio = false;
  await enParalelo(PROVINCIAS, 6, async p => {
    const viejo = (await env.RESULTADOS.get('secc:' + p, 'json')) || {};
    let nuevo = null;
    if (quiereAv.length) try { const av = avancesMesas(await pideTexto(`${st.base}/getAvances/2/${p}.csv`, env)); if (Object.keys(av).length) nuevo = { ...(nuevo || viejo), av }; } catch (e) { /* sigue */ }
    if (quiereEsc && st.esc[p] !== 'completa') try {
      const e = escrutinioMesas(await pideTexto(`${st.base}/getEscrutinio/2/${p}.csv`, env));
      if (Object.keys(e.s).length) { nuevo = { ...(nuevo || viejo), siglas: e.siglas, s: e.s }; st.esc[p] = e.completa ? 'completa' : 'parcial'; }
    } catch (e) { /* aún no está */ }
    if (nuevo) { cambio = true; await env.RESULTADOS.put('secc:' + p, JSON.stringify({ ...nuevo, eleccion: F.eleccion || '2026_11' })); }
  });
  if (quiereAv.length && cambio) {   // un avance se da por leído cuando alguna sección lo trae
    const m = await env.RESULTADOS.get('secc:28', 'json');
    for (const k of quiereAv) if (m && m.av && Object.values(m.av).some(a => a[k - 1][0] > 0)) st.av.push(k);
  }
  if (cambio) st.ver = new Date().toISOString();
  await env.RESULTADOS.put('mesas', JSON.stringify(st));
  return res();
}
const cabeceras = env => { const h = { 'User-Agent': 'mapaelectoral.es (prensa)' }; if (env.MEDIOS_USUARIO) h.Authorization = 'Basic ' + btoa(`${env.MEDIOS_USUARIO}:${env.MEDIOS_CLAVE || ''}`); return h; };
const horaMedios = f => /^\d{10}$/.test(f) ? `20${f.slice(0, 2)}-${f.slice(2, 4)}-${f.slice(4, 6)}T${f.slice(6, 8)}:${f.slice(8, 10)}:00+01:00` : null;

let MUESTRA_AV = '';   // primera línea TO de los avances, para /estado (diagnóstico)
const PROVINCIAS = Array.from({ length: 52 }, (_, i) => String(i + 1).padStart(2, '0'));

// 2023 (ficheros fijos de Interior), para comparar: se leen una vez y se guardan en KV; si fallan, no se reintenta en 10 minutos
async function ant23(base, env) {
  const g = await env.RESULTADOS.get('ant23b', 'json'); if (g) return g;
  if (await env.RESULTADOS.get('ant23_fallo')) return null;
  try {
    const ant = { v: 2, ambitos: ambitosMedios(await pideTexto(`${base}/fijos/getEscrutinioTotales/ANT/2/07-23`, env)),
      senado: senado23Medios(await pideTexto(`${base}/fijos/getEscrutinioTotales/ANT/3/07-23`, env)) };
    if (!ant.ambitos.TO) throw new Error('sin TO');
    await env.RESULTADOS.put('ant23b', JSON.stringify(ant)); return ant;
  } catch (e) { await env.RESULTADOS.put('ant23_fallo', e.message.slice(0, 100), { expirationTtl: 600 }); return null; }
}

async function porMedios(base, env) {
  const envio = (await pideTexto(`${base}/data/getEnvio/2`, env)).trim().split(/[;\s]/)[0];
  if (!/^\d+$/.test(envio)) throw new Error('getEnvio no devolvió un número: ' + envio.slice(0, 40));
  const previo = await env.RESULTADOS.get('ultimo', 'json');
  let e3 = null; try { e3 = (await pideTexto(`${base}/data/getEnvio/3`, env)).trim().split(/[;\s]/)[0]; } catch (e) { /* sin Senado */ }
  if (previo && !previo.retenido && previo.envio === envio && previo.mun && previo.ambitos && (!e3 || (previo.senado && previo.senado.envio === e3))) {   // nada nuevo
    const a = previo.ant23 && previo.ant23.v === 2 ? previo.ant23 : await ant23(base, env);
    return { ...previo, ...(a ? { ant23: a } : {}), secc: await mesas(base, env, previo).catch(e => ({ error: e.message })) };
  }
  const filas = [], fallos = [];
  await enParalelo(PROVINCIAS, 8, async p => {
    try { for (const l of lineas(await pideTexto(`${base}/data/getEscrutinioMunicipios/2/${p}/${envio}`, env))) { const f = filaMedios(l); if (f) filas.push(f); } }
    catch (e) { fallos.push(p); }
  });
  if (!filas.length) throw new Error(`ninguna provincia trajo municipios en el envío ${envio} (${fallos.length} fallos)`);
  let escanos = null, avances = null;
  let ambitos = null, senado = null;
  try { const t = await pideTexto(`${base}/data/getEscrutinioTotales/2/${envio}`, env); escanos = escanosMedios(t); ambitos = ambitosMedios(t); } catch (e) { /* sin escaños esta vez */ }
  try {
    if (!/^\d+$/.test(e3 || '')) throw new Error('getEnvio/3: ' + String(e3).slice(0, 40));
    const t = await pideTexto(`${base}/data/getEscrutinioTotales/3/${e3}`, env);
    MUESTRA_SEN = e3 + ' · ' + (lineas(t)[0] || '').slice(0, 160); senado = { envio: e3, ...senadoMedios(t) };
  } catch (e) { MUESTRA_SEN = 'error: ' + e.message; }
  try { const t = await pideTexto(`${base}/data/getAvancesTotales/2/${envio}`, env); MUESTRA_AV = (lineas(t).find(l => /^\d{10};?TO/.test(l)) || lineas(t)[0] || '').slice(0, 200); avances = avancesMedios(t); }
  catch (e) { MUESTRA_AV = 'error: ' + e.message; }
  // PUBLICA (hora ISO; la noche, 2026-11-29T20:00:00Z = 21:00 en Madrid, cierre de Canarias): antes de esa hora no se
  // guarda ningún voto ni escaño, aunque la API ya los diera; la participación de los avances sí (Interior la publica a las
  // 14:00 y a las 18:00). Es un seguro: el manual dice que Interior publica los resultados a las 21:00, hora peninsular.
  const retenido = !!(env.PUBLICA && Date.now() < Date.parse(env.PUBLICA));
  if (retenido) { for (const f of filas) { f.a = [f.a[0], 0, 0, 0, 0]; f.votos = {}; } escanos = ambitos = senado = null; }
  const out = normaliza(filas, previo);
  if (retenido) out.retenido = true;
  // Hora: la del último registro con mesas escrutadas; sin escrutinio, la de los avances; sin nada, la de la lectura.
  const conVotos = filas.filter(x => x.a[1] > 0).map(x => x.fecha || '').sort().pop();   // YYMMddHHmm, hora peninsular (UTC+1)
  out.actualizado = horaMedios(conVotos) || (avances && avances.es && avances.es.some(x => x != null) && horaMedios(avances.fecha)) || new Date().toISOString();
  if (avances) out.avances = { es: avances.es, pr: avances.pr, mesas: avances.mesas };
  // Antes del escrutinio, la participación del último avance municipio a municipio, para pintar el mapa (52 peticiones más)
  if (avances && avances.es && avances.es.some(x => x != null) && !filas.some(x => x.a[1] > 0)) {
    const avmun = {};
    await enParalelo(PROVINCIAS, 8, async p => {
      try { Object.assign(avmun, avancesMunicipios(await pideTexto(`${base}/data/getAvancesMunicipios/2/${p}/${envio}`, env))); } catch (e) { /* sigue */ }
    });
    if (Object.keys(avmun).length) out.avmun = avmun;
  }
  // si falló alguna provincia, no se marca el envío como leído: el minuto siguiente se vuelve a intentar
  const ant = await ant23(base, env);
  out.secc = await mesas(base, env, { ...out, avances }).catch(e => ({ error: e.message }));
  return { ...out, envio: fallos.length ? 'incompleto-' + envio : envio, ...(escanos ? { escanos } : {}), ...(ambitos && ambitos.TO ? { ambitos } : {}), ...(senado && senado.TO ? { senado } : {}), ...(ant ? { ant23: ant } : {}) };
}
