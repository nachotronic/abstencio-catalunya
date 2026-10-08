// Imita la API de la web de resultados de Interior (formato real del 23J, ver muestras_23j/) con los datos del simulacro.
// Uso:  node interior_simulado.mjs muestras_23j ../../../data/simulacro.json fraccion     -> http://localhost:8899/backend-difu
// El fichero «fraccion» (0 a 1) dice qué parte de los municipios lleva escrutinio; se puede cambiar con la prueba en marcha.
import http from 'http'; import fs from 'fs'; import zlib from 'zlib';
const D = process.argv[2], SIM = JSON.parse(fs.readFileSync(process.argv[3]));
const cfg = fs.readFileSync(D + '/getConfig.json'), nomGz = fs.readFileSync(D + '/getNomenclator.json.gz');
const nom = JSON.parse(zlib.gunzipSync(nomGz)); const amb = nom.amb.find(e => e.elec === 2).ambitos;
const porId = Object.fromEntries(amb.map(a => [a.c, a]));
const h = s => { let x = 2166136261; for (const c of s) x = Math.imul(x ^ c.charCodeAt(0), 16777619) >>> 0; return x / 4294967296; };
const P = v => ({ pro: v, def: v });
let peticiones = 0;
function ambito(a) {
  const f = +fs.readFileSync(process.argv[4] || 'fraccion', 'utf8'), r = SIM.mun[a.co];
  const base = { codigo: a.co, nombre: a.n, nivel: 90, numMesas: 1, censoINE: r ? r[0] : 0, censoNoche: r ? r[0] : 0, padres: [], apertura: null, avances: null };
  if (!r || h(a.co) > f || !r[1]) return { ...base, escrutinio: null };
  const [ct, ce, vot, bl, nu, ...v] = r, part = v.reduce((s, x) => s + x, 0);
  return { ...base, escrutinio: { envio: 11, fecha: new Date().toISOString(), censoNocheEscrutado: P(ce), mesasEscrutadas: P(1),
    votosValidos: P(part + bl), votosBlancos: P(bl), votosNulos: P(nu), votosPartidos: P(part), votosTotales: P(vot),
    partidos: SIM.siglas.map((s, k) => ({ siglas: s, codigo: String(k), nombre: s, votos: P(v[k]), cargos: P(0), porcentaje: P(0) })).filter(p => p.votos.pro || Math.random() < .1) } };
}
http.createServer((q, res) => {
  peticiones++; const u = new URL(q.url, 'http://x'), p = u.pathname.replace(/^\/backend-difu/, '');
  const js = o => { res.writeHead(200, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(o)); };
  if (p === '/web/getConfig') return res.end(cfg);
  if (p === '/nomenclator/getNomenclator') { res.writeHead(200, { 'Content-Type': 'application/json' }); return res.end(nomGz); }  // gzip sin cabecera, como en el archivo
  if (p === '/peticiones') return js({ peticiones });
  let m = p.match(/^\/scope\/data\/getScopeData\/(\w+)\/1\/2\/1\/1\/90$/);
  if (m && porId[m[1]] && porId[m[1]].l === 30) {
    const hijos = porId[m[1]].h.find(x => x.l === 90).p.map(i => amb[i]);
    return js({ scope: { codigo: porId[m[1]].co, nivel: 30 }, mapa: hijos.map(ambito) });
  }
  m = p.match(/^\/scope\/data\/getScopeData\/(\w+)\/1\/2\/1\/0$/);
  if (m && porId[m[1]]) return js({ scope: ambito(porId[m[1]]) });
  res.writeHead(404); res.end('{}');
}).listen(8899, () => console.log('Interior simulado en :8899'));
