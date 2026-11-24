// Escrutinio del 29N en toda España, en /elecciones/resultados-elecciones-generales-2026/.
//
// Lee el mismo JSON normalizado que el mapa y las fichas (formato en src/actualizar_29n.py):
//   - la URL sale de generales-2026/data/meta.json (directo.url); para ensayar: ?directo=data/simulacro.json o una URL completa;
//   - sin URL no hace nada: la página enseña solo el aviso con la hora de los primeros datos.
// Suma los municipios (sin el voto desde el extranjero, CERA). PP y PSOE se agrupan con sus listas territoriales (PSC,
// UPN-PP…), pero no con otros partidos; el resto de candidaturas va por separado, porque el 29N listas que en
// 2023 iban juntas (Sumar y Podemos) se presentan por separado. Los escaños solo salen si los publica Interior
// (campo «escanos» del Worker, por provincia): aquí no se calculan. Refresca cada minuto.
// Con datos reales añade la banda «En directo», los hitos que escribe el Worker («hitos») y el LiveBlogPosting.
(function () {
  const caja = document.getElementById('directo-esp');
  if (!caja) return;
  const BASE = new URL('generales-2026/', new URL(caja.dataset.raiz || './', location.href));
  const pct = x => (x * 100).toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
  const nf = n => String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  fetch(new URL('data/meta.json', BASE)).then(r => r.json()).then(META => {
    const q = new URLSearchParams(location.search).get('directo') || (META.directo && META.directo.url);
    if (!q) return;
    const url = /^(https?:)?\/\//.test(q) ? q : new URL(q.replace(/^\.?\//, ''), BASE).href;
    const REG = (META.reglas || []).map(([c, p]) => [c, new RegExp(p)]);
    const FAM = {}; (META.familias || []).forEach(f => FAM[f.cod] = f);
    const famDe = s => { const a = (s || '').toUpperCase().trim(); for (const x of [a, a.replace(/\./g, '')]) for (const [c, r] of REG) if (r.test(x)) return c; return 'OTROS'; };
    // grupo de una candidatura: PP y PSOE juntan sus listas territoriales; el resto, cada una con sus siglas
    // (solo las listas del mismo partido: UPN, que en 2023 fue por su cuenta, sale aparte aunque el mapa la sume al PP)
    const MISMO = { PP: /^(PP\b|PP-|P\.P\.|UPN-PP)/, PSOE: /PSOE(?! ?\(?H)|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN/ };
    // siglas de Interior -> nombre de lectura (las que no están aquí salen tal cual; revisar con getCandidaturas antes del 29N)
    const NOMBRE = { 'B.N.G.': 'BNG', 'EAJ-PNV': 'PNV', 'JXCAT - JUNTS': 'Junts', 'JXCAT-JUNTS': 'Junts', 'JXCAT': 'Junts', 'TERUEL EXISTE': 'Teruel Existe', 'EH BILDU': 'EH Bildu', 'VOX': 'Vox', 'CCA': 'Coalición Canaria',
    'U.P.N.': 'UPN', 'SUMAR': 'Sumar', 'PODEMOS': 'Podemos', 'CUP-PR': 'CUP', 'SALF': 'Se Acabó la Fiesta', 'FO': 'Frente Obrero',
    'ADELANTE ANDALUCÍA': 'Adelante Andalucía', 'GBAI': 'Geroa Bai', 'SY': 'Soria ¡Ya!' };
    const FA = /FRENTE AMPLIO|FRONT AMPLI|FRONTE AMPLA|FRONTE ZABALA|^FA$|^COMUNS|^ARAM[EÉ]S|PODEMOS, IU, SUMAR|^COMPROM/;   // Frente Amplio: un nombre distinto en cada comunidad, se suman (Podemos va aparte, salvo en las conjuntas de Canarias y la C. Valenciana)
    const grupo = s => { const f = famDe(s), a = (s || '').toUpperCase().trim();
      if (FA.test(a)) return { k: 'FA', n: 'Frente Amplio', col: (FAM.SUMAR || {}).color || '#999' };
      if (/^CCA\b|^1\.?ºCAN/.test(a)) return { k: 'CC', n: 'Coalición Canaria', col: (FAM.CC || {}).color || '#999' };   // «CCa-1ºCAN» y «1.ºCAN-CCa»
      if (/^EH ?BILDU/.test(a)) return { k: 'BILDU', n: 'EH Bildu', col: (FAM.BILDU || {}).color || '#999' };   // con «EH BILDU-ERC» de Navarra
      return MISMO[f] && MISMO[f].test(a) ? { k: f, n: FAM[f].nombre, col: FAM[f].color } : { k: 's:' + (NOMBRE[a] || a), n: NOMBRE[a] || s, col: (FAM[f] || {}).color || '#999' }; };
    const nombre = (META.directo && META.directo.nombre) || '29N';
    const tick = () => fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(F => pinta(F, grupo, nombre))
      .catch(() => { const e = caja.querySelector('.d-estado'); if (e) e.textContent = 'Sin conexión con los resultados, reintentando…'; });
    tick(); setInterval(tick, 30000);   // cada 30 s: los primeros datos, lo antes posible (Nacho, 24-11)
  }).catch(() => {});

  function pinta(F, grupo, nombre) {
    if (!F.mun || !F.siglas) return;
    let ct = 0, ce = 0, vot = 0, bl = 0;
    const votos = F.siglas.map(() => 0);
    for (const a of Object.values(F.mun)) {
      ct += a[0]; ce += a[1]; vot += a[2]; bl += a[3];
      for (let k = 0; k < F.siglas.length; k++) votos[k] += a[5 + k] || 0;
    }
    // España: con el fichero de totales de Interior si lo trae (mismo envío; no depende de que lleguen las 52 provincias)
    const TO = F.ambitos && F.ambitos.TO;
    let sig = F.siglas, totEsc = null;
    if (TO && TO.c && TO.c.length && TO.ce) {
      sig = TO.c.map(x => x[0]); votos.length = 0; TO.c.forEach(x => votos.push(x[1])); totEsc = TO.c.map(x => x[2]);
      ct = TO.ct; ce = TO.ce; vot = TO.vo; bl = TO.bl;
    }
    // Avances de participación de Interior (en %): España en el total; la provincia, en su fichero
    const AV = F.avances && F.avances.es;
    const ME = F.avances && F.avances.mesas;
    const meTxt = ME && ME.constituidas ? `<p data-tipo="dato">Mesas constituidas: ${ME.constituidas.toLocaleString('es-ES')} de ${ME.total.toLocaleString('es-ES')}`
      + (ME.suspendidas ? ` (${ME.suspendidas.toLocaleString('es-ES')} suspendidas)` : '') + '.</p>' : '';
    const avTxt = meTxt + (AV && AV.some(x => x != null) ? '<p data-tipo="dato">Participación según los avances de Interior: '
      + AV.map((x, i) => x == null ? '' : `${i ? '2.º' : '1.er'} avance, ${pct(x / 100)}`).filter(Boolean).join(' · ') + '.</p>' : '');
    if (!ce) { caja.querySelector('.d-cuerpo').innerHTML = `<p class="d-estado">${esc(nombre)} · todavía no hay mesas escrutadas.</p>` + avTxt; return; }
    const G = {};
    sig.forEach((s, k) => { if (!votos[k] && !(totEsc && totEsc[k])) return; const g = grupo(s); (G[g.k] ||= { ...g, v: 0, e: 0 }).v += votos[k]; });
    let conEsc = false;
    if (totEsc) sig.forEach((s, k) => { if (totEsc[k]) { G[grupo(s).k].e += totEsc[k]; conEsc = true; } });
    else if (F.escanos) for (const d of Object.values(F.escanos)) for (const [s, n] of Object.entries(d)) { const g = grupo(s); (G[g.k] ||= { ...g, v: 0, e: 0 }).e += n; conEsc = conEsc || n > 0; }
    const val = Object.values(G).reduce((t, x) => t + x.v, 0) + bl;
    const L = Object.values(G).sort((x, y) => (y.e - x.e) || (y.v - x.v));
    const ord = L.filter(x => x.v / val >= 0.005 || x.e), resto = L.filter(x => !ord.includes(x)).reduce((t, x) => t + x.v, 0);
    const t = F.actualizado ? new Date(F.actualizado) : new Date();
    const hora = t.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
    caja.querySelector('.d-aviso').hidden = true;
    const vivo = !F.simulacro && ce < ct * 0.999;   // la banda «En directo» solo con datos reales y mientras falte escrutar
    let h = (vivo ? `<p class="d-vivo"><span class="d-punto"></span>En directo · última actualización a las ${hora}</p>` : '')
      + `<p class="d-estado">${F.simulacro ? '<b>Simulacro con datos del 23J.</b> ' : ''}${esc(nombre)} · escrutado el ${pct(ce / ct)} del censo · actualizado a las ${hora}</p>`;
    const mas = ord.reduce((m, x) => x.v > m.v ? x : m, ord[0]);   // la más votada (ord va por escaños)
    h += `<p data-tipo="dato">Con el ${pct(ce / ct)} del censo escrutado, ${esc(mas.n)} es la candidatura más votada, con el ${pct(mas.v / val)} del voto válido. `
      + `Participación en las mesas escrutadas: ${pct(vot / ce)}.</p>`;
    const mx = Math.max(...ord.map(x => x.v));
    h += '<div class="d-barras">' + ord.slice(0, 12).map(x => `<div class="d-fila"><span class="d-et">${esc(x.n)}</span>`
      + `<span class="d-bar"><i style="width:${(x.v / mx * 100).toFixed(1)}%;background:${x.col}"></i></span><span class="d-va">${pct(x.v / val)}</span></div>`).join('') + '</div>';
    h += '<table class="d-tabla"><caption>Votos' + (conEsc ? ' y escaños' : '') + ` del 29N en España (${pct(ce / ct)} escrutado)</caption><thead><tr><th>Candidatura</th><th>Votos</th><th>% voto válido</th>`
      + (conEsc ? '<th>Escaños</th>' : '') + '</tr></thead><tbody>'
      + ord.map(x => `<tr><td><i class="d-pt" style="background:${x.col}"></i>${esc(x.n)}</td><td>${nf(x.v)}</td><td>${pct(x.v / val)}</td>${conEsc ? `<td>${x.e}</td>` : ''}</tr>`).join('')
      + (resto ? `<tr><td>Otras</td><td>${nf(resto)}</td><td>${pct(resto / val)}</td>${conEsc ? '<td>0</td>' : ''}</tr>` : '')
      + `<tr><td>En blanco</td><td>${nf(bl)}</td><td>${pct(bl / val)}</td>${conEsc ? '<td></td>' : ''}</tr></tbody></table>`;
    h += '<p class="leyenda">Escrutinio provisional del Ministerio del Interior, sobre voto válido (candidaturas más blancos) y sin el voto desde el extranjero (CERA). '
      + (conEsc ? 'Escaños provisionales según Interior; mayoría absoluta, 176. ' : 'Los escaños aparecerán cuando Interior los publique. ')
      + 'PP y PSOE incluyen sus listas territoriales (como PSC). Cambia hasta el escrutinio definitivo de las juntas electorales.</p>';
    const H = (F.hitos || []).slice().reverse();
    const hm = x => new Date(x).toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
    if (H.length) h += '<h3 class="d-h3">Minuto a minuto</h3><ol class="d-hitos" reversed>'
      + H.map(x => `<li><time datetime="${esc(x.t)}">${hm(x.t)}</time> ${esc(x.texto)}</li>`).join('') + '</ol>';
    caja.querySelector('.d-cuerpo').innerHTML = h;
    ld(F, H);
  }

  // Datos estructurados de directo (LiveBlogPosting), solo con datos reales: una entrada por hito
  function ld(F, H) {
    if (F.simulacro || !H.length) return;
    const url = location.origin + location.pathname, n = document.getElementById('ld-directo') || document.head.appendChild(Object.assign(document.createElement('script'), { type: 'application/ld+json', id: 'ld-directo' }));
    n.textContent = JSON.stringify({
      '@context': 'https://schema.org', '@type': 'LiveBlogPosting', '@id': url + '#directo', url,
      headline: 'Resultados elecciones generales 2026: escrutinio del 29N en directo',
      coverageStartTime: '2026-11-29T20:00:00+01:00', coverageEndTime: '2026-11-30T03:00:00+01:00',
      datePublished: H[H.length - 1].t, dateModified: F.actualizado || H[0].t,
      author: { '@type': 'Person', name: 'Nacho G. del Álamo', url: location.origin + '/sobre-mi.html' },
      publisher: { '@id': location.origin + '/#medio' },
      about: { '@type': 'Event', name: 'Elecciones generales de España de 2026', startDate: '2026-11-29', location: { '@type': 'Country', name: 'España' } },
      liveBlogUpdate: H.slice(0, 30).map(x => ({ '@type': 'BlogPosting', headline: x.texto.slice(0, 110), articleBody: x.texto, datePublished: x.t }))
    });
  }
})();
