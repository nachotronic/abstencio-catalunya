// Imita la API de descargas para medios de Interior (manual «API de descargas · Elecciones Generales 29N 2026»)
// con los datos del simulacro (23J): registros de longitud fija separados por «;», CR LF, autenticación básica.
// Uso:  node interior_medios_simulado.mjs ../../../data/simulacro.json fraccion [usuario] [clave]
//       -> http://localhost:8898/descargas/csv
// El fichero «fraccion» (0 a 1) dice qué parte de los municipios lleva escrutinio; cada cambio es un envío nuevo.
import http from 'http'; import fs from 'fs';
const SIM = JSON.parse(fs.readFileSync(process.argv[2])), FR = process.argv[3] || 'fraccion';
const USU = process.argv[4] || 'medio', CLA = process.argv[5] || 'clave';
const META = JSON.parse(fs.readFileSync(new URL('../../../data/meta.json', import.meta.url)));
const h = s => { let x = 2166136261; for (const c of s) x = Math.imul(x ^ c.charCodeAt(0), 16777619) >>> 0; return x / 4294967296; };
const izq = (v, w) => String(v ?? '').slice(0, w).padEnd(w), num = (v, w) => String(Math.round(v || 0)).padStart(w, '0');
const pct = (a, b) => num(b ? a / b * 10000 : 0, 5);
let envio = 0, ultFr = null, peticiones = 0;
const fecha = () => { const d = new Date(Date.now() + 3600e3).toISOString(); return d.slice(2, 4) + d.slice(5, 7) + d.slice(8, 10) + d.slice(11, 13) + d.slice(14, 16); };
function estado() {
  const f = +fs.readFileSync(FR, 'utf8');
  if (f !== ultFr) { ultFr = f; envio++; }
  return f;
}
function municipio(cod, f) {
  const r = SIM.mun[cod]; const [ct, ce0, vot0, bl0, nu0, ...v0] = r;
  const esc = h(cod) <= f && ce0;
  const [ce, vot, bl, nu] = esc ? [ce0, vot0, bl0, nu0] : [0, 0, 0, 0], v = esc ? v0 : v0.map(() => 0);
  const val = v.reduce((s, x) => s + x, 0) + bl;
  const cands = SIM.siglas.map((s, k) => [String(k + 1).padStart(4, '0'), s, v[k]]).filter(x => x[2]).slice(0, 80);
  while (cands.length < 80) cands.push(['0000', '', 0]);
  return [fecha(), '00', cod.slice(0, 2), '9', cod.slice(2), '99', izq('Municipio ' + cod, 50), '99', '99', num(1, 5), num(ct, 8), num(ce, 8), pct(ce, ct),
    num(vot, 8), pct(vot, ce), num(ce - vot, 8), pct(ce - vot, ce), num(bl, 8), pct(bl, val), num(nu, 8), pct(nu, vot),
    ...cands.flatMap(([c, s, x]) => [c, izq(s, 55), num(x, 8), pct(x, val)])].join(';');
}
function dhondt(votos, n) {
  const tot = Object.values(votos).reduce((s, x) => s + x, 0), q = [];
  for (const [s, x] of Object.entries(votos)) if (x >= tot * 0.03) for (let d = 1; d <= n; d++) q.push([x / d, s]);
  q.sort((a, b) => b[0] - a[0]); const r = {}; for (const [, s] of q.slice(0, n)) r[s] = (r[s] || 0) + 1; return r;
}
function totales(f) {
  const out = [];
  for (let p = 1; p <= 52; p++) {
    const pp = String(p).padStart(2, '0'), filas = Object.keys(SIM.mun).filter(c => c.startsWith(pp)).map(c => municipio(c, f).split(';'));
    const sum = k => filas.reduce((s, c) => s + +c[k], 0), votos = {};
    for (const c of filas) for (let k = 21; k + 2 < c.length; k += 4) if (c[k + 1].trim()) votos[c[k + 1].trim()] = (votos[c[k + 1].trim()] || 0) + +c[k + 2];
    const n = META.escanos['2026_11'][pp], el = sum(12) ? dhondt(votos, n) : {};
    const cands = Object.entries(votos).filter(x => x[1]).slice(0, 80).map(([s, x], i) => [String(i + 1).padStart(4, '0'), izq(s, 55), num(x, 8), num(0, 5), num(el[s] || 0, 3)]);
    while (cands.length < 80) cands.push(['0000', izq('', 55), num(0, 8), num(0, 5), num(0, 3)]);
    out.push([fecha(), 'PR', '00', pp, '9', izq('Provincia ' + pp, 50), num(filas.length, 5), num(sum(10), 8), num(sum(11), 8), pct(sum(11), sum(10)),
      num(sum(13), 8), '00000', '00000000', '00000', num(sum(17), 8), '00000', num(sum(19), 8), '00000', num(n, 3), '0000', '0000', '00000000', ...cands.flat()].join(';'));
  }
  return out;
}
http.createServer((q, res) => {
  peticiones++; const u = new URL(q.url, 'http://x'), p = u.pathname.replace(/^\/descargas\/csv/, '');
  if (p === '/peticiones') { res.end(JSON.stringify({ peticiones, envio })); return; }
  const ok = q.headers.authorization === 'Basic ' + Buffer.from(`${USU}:${CLA}`).toString('base64');
  if (!ok) { res.writeHead(401, { 'WWW-Authenticate': 'Basic realm="descargas"' }); return res.end(); }
  const txt = l => { res.writeHead(200, { 'Content-Type': 'text/plain; charset=utf-8' }); res.end(l.join('\r\n') + '\r\n'); };
  const f = estado();
  if (p === '/data/getEnvio/2') return txt([String(envio)]);
  let m = p.match(/^\/data\/getEscrutinioMunicipios\/2\/(\d{2})\/(\d+)$/);
  if (m) {
    if (+m[2] !== envio) { res.writeHead(404); return res.end(); }   // envío caducado
    return txt(Object.keys(SIM.mun).filter(c => c.startsWith(m[1])).map(c => municipio(c, f)));
  }
  m = p.match(/^\/data\/getAvancesMunicipios\/2\/(\d{2})\/(\d+)$/);   // 1.er avance: entre el 20 y el 60 %, según el código
  if (m) return txt(Object.keys(SIM.mun).filter(c => c.startsWith(m[1])).map(c =>
    [fecha(), '00', c.slice(0, 2), '9', c.slice(2), '99', izq('Municipio ' + c, 50), '99', '99', '00010', '00010', '00000', '00001000', '00001000', '00000000',
      '00010', '00001000', String(2000 + (+c.slice(2) * 37) % 4000).padStart(5, '0'), '00000', '00000000', '00000'].join(';')));
  m = p.match(/^\/data\/getAvancesTotales\/2\/(\d+)$/);   // dos avances fijos: 25,00 % y 50,00 %
  if (m) return txt(['TO;99;99', ...Object.keys(META.escanos['2026_11']).map(pp => 'PR;00;' + pp)].map(t =>
    [fecha(), t, '9', izq('Ámbito', 50), '01000', '01000', '00000', '01000000', '01000000', '00000000', '01000', '01000000', '02500', '01000', '01000000', '05000'].join(';')));
  m = p.match(/^\/data\/getEscrutinioTotales\/2\/(\d+)$/);
  if (m) return txt(totales(f));
  res.writeHead(404); res.end();
}).listen(8898, () => console.log('API de medios simulada en :8898/descargas/csv'));
