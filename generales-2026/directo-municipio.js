// Escrutado del 29N en la ficha de un municipio (/municipio/<provincia>/<municipio>/).
//
// Lee el mismo JSON normalizado que el mapa de la portada (formato en src/actualizar_29n.py):
//   - la URL sale de generales-2026/data/meta.json (directo.url), la misma que enciende el mapa la noche electoral;
//   - si esa URL es la del Worker (…/resultados.json), pide solo su provincia: …/provincia/<pp>.json;
//   - para ensayar sin datos reales: ?directo=data/simulacro.json (ruta relativa a generales-2026/) o una URL completa.
// Sin URL no hace nada: la ficha solo muestra el aviso estático de que el escrutinio aparecerá ahí.
// Refresca cada minuto. Muestra cada candidatura por separado (no por familias) y compara con 2023 solo la participación.
(function () {
  const caja = document.getElementById('directo-mun');
  if (!caja) return;
  const COD = caja.dataset.mun, RAIZ = new URL(caja.dataset.raiz || './', location.href);
  const BASE = new URL('generales-2026/', RAIZ);
  const A23 = JSON.parse(caja.dataset.r23 || '{}');   // {"part": participación de 2023 sobre el censo residente}
  const pct = x => (x * 100).toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 }) + ' %';
  const pts = x => (Math.round(x * 1000) === 0 ? '' : x > 0 ? '+' : '−') + Math.abs(x * 100).toLocaleString('es-ES', { minimumFractionDigits: 1, maximumFractionDigits: 1 });
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  fetch(new URL('data/meta.json', BASE)).then(r => r.json()).then(META => {
    const q = new URLSearchParams(location.search).get('directo') || (META.directo && META.directo.url);
    if (!q) return;
    let url = /^(https?:)?\/\//.test(q) ? q : new URL(q.replace(/^\.?\//, ''), BASE).href;
    // Del Worker basta la provincia del municipio (unos 30 KB por minuto en vez del país entero, 1,4 MB)
    if (/\/resultados\.json$/.test(url) && /^https?:/.test(url)) url = url.replace(/\/resultados\.json$/, `/provincia/${String(COD).padStart(5, '0').slice(0, 2)}.json`);
    const REG = (META.reglas || []).map(([c, p]) => [c, new RegExp(p)]);
    const FAM = {}; (META.familias || []).forEach(f => FAM[f.cod] = f);
    // Como familia() de partidos.py y famDe() de app.js: siglas tal cual y sin puntos.
    const famDe = s => { const a = (s || '').toUpperCase().trim(); for (const x of [a, a.replace(/\./g, '')]) for (const [c, r] of REG) if (r.test(x)) return c; return 'OTROS'; };
    const nombre = META.directo.nombre || '29N';
    const tick = () => fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' })
      .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(F => pinta(F, famDe, FAM, nombre))
      .catch(() => { const e = caja.querySelector('.d-estado'); if (e) e.textContent = 'Sin conexión con los resultados, reintentando…'; });
    tick(); setInterval(tick, 60000);
  }).catch(() => {});

  function pinta(F, famDe, FAM, nombre) {
    const a = F.mun && (F.mun[COD] || F.mun[String(+COD)]);
    if (!a) return;
    const [ct, ce, vot, bl, , ...v] = a;
    // Por candidatura, no por familia: el 29N listas que en 2023 iban juntas (Sumar y Podemos) se presentan por separado.
    const L = F.siglas.map((s, k) => ({ s, n: v[k] || 0, col: (FAM[famDe(s)] || {}).color || '#999' }));
    const val = L.reduce((t, x) => t + x.n, 0) + bl;
    caja.querySelector('.d-aviso').hidden = true;
    const t = F.actualizado ? new Date(F.actualizado) : new Date();
    const hora = t.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
    const escr = ct ? ce / ct : 0;
    let h = `<p class="d-estado">${F.simulacro ? '<b>Simulacro con datos del 23J.</b> ' : ''}${esc(nombre)} · escrutado el ${pct(escr)} del censo · actualizado a las ${hora}</p>`;
    if (!ce || !val) {
      caja.querySelector('.d-cuerpo').innerHTML = h + '<p>Todavía no hay mesas escrutadas en el municipio.</p>';
      return;
    }
    const ord = L.filter(x => x.n / val >= 0.005).sort((x, y) => y.n - x.n);
    const resto = L.filter(x => x.n / val < 0.005).reduce((t, x) => t + x.n, 0);
    if (resto) ord.push({ s: 'Otras', n: resto, col: '#999' });
    const mx = Math.max(...ord.map(x => x.n));
    const part = vot / ce;
    h += `<p data-tipo="dato">Con el ${pct(escr)} del censo escrutado, la candidatura más votada es ${esc(ord[0].s)}, con el ${pct(ord[0].n / val)} del voto válido. `
      + `Participación: ${pct(part)}` + (A23.part ? ` (${pts(part - A23.part)} puntos frente a 2023, sobre las mesas escrutadas).` : '.') + '</p>';
    h += '<div class="d-barras">' + ord.map(x => `<div class="d-fila"><span class="d-et">${esc(x.s)}</span>`
      + `<span class="d-bar"><i style="width:${(x.n / mx * 100).toFixed(1)}%;background:${x.col}"></i></span><span class="d-va">${pct(x.n / val)}</span></div>`).join('') + '</div>';
    h += '<p class="leyenda">Escrutinio provisional del Ministerio del Interior, sobre voto válido (candidaturas más blancos) y sin el voto desde el extranjero (CERA). '
      + 'Cambia hasta el escrutinio definitivo de las juntas electorales. El resultado de 2023, más abajo.</p>';
    caja.querySelector('.d-cuerpo').innerHTML = h;
  }
})();
