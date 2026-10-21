// Prototipo de /previsiones/. Solo dibuja: todas las cifras salen de los ficheros que escribe previsiones/src/motor.py.
(() => {
  const DATOS = 'datos/v0-ficticio/';
  const NS = 'http://www.w3.org/2000/svg';
  const OSCURO = () => document.documentElement.dataset.theme === 'dark' ||
    (document.documentElement.dataset.theme !== 'light' && matchMedia('(prefers-color-scheme: dark)').matches);
  // Color propio de cada partido (claro, oscuro), igual que en las piezas de Actualidad
  const COL = {
    'PP': ['#1d84ce', '#4fa8ea'], 'PSOE': ['#e30613', '#ff5a5f'], 'Vox': ['#5ac035', '#74d651'], 'Sumar': ['#a2275f', '#d0679a'],
    'ERC': ['#f5b324', '#f7c454'], 'Junts': ['#20c0b2', '#2fd0c2'], 'PNV': ['#2b8a3e', '#4caf63'], 'EH Bildu': ['#a5c400', '#b9d630'],
    'BNG': ['#4a9fdc', '#7ab8e6'], 'CC': ['#f7d417', '#f9e04a'], 'UPN': ['#0b3d91', '#5b7fd0'], 'CUP': ['#d9b600', '#ecd13a'],
    'PACMA': ['#74a63a', '#93c45a'], 'Nueva Canarias': ['#c8a400', '#e0c23a']};
  const col = p => (COL[p] || ['#9a9a9a', '#7d7d7d'])[OSCURO() ? 1 : 0];
  // Orden de izquierda a derecha en los hemiciclos (el de los asientos del Congreso, aproximado)
  const ORDEN = ['CUP', 'EH Bildu', 'BNG', 'Sumar', 'ERC', 'PSOE', 'PNV', 'Junts', 'CC', 'Nueva Canarias', 'UPN', 'PP', 'Vox', 'PACMA'];
  const ord = (a, b) => ORDEN.indexOf(a) - ORDEN.indexOf(b);
  const pc = v => v.toFixed(1).replace('.', ',') + ' %';
  const n0 = v => Math.round(v).toLocaleString('es-ES');
  const $ = id => document.getElementById(id);
  const el = (n, a, p) => { const e = document.createElementNS(NS, n); for (const k in a) e.setAttribute(k, a[k]); if (p) p.appendChild(e); return e; };
  const get = f => fetch(DATOS + f).then(r => { if (!r.ok) throw new Error(f); return r.json(); });

  function tip(box) {
    let t = box.querySelector('.tip');
    if (!t) { t = document.createElement('div'); t.className = 'tip'; t.hidden = true; box.appendChild(t); }
    const show = (html, ev) => {
      const r = box.getBoundingClientRect(), p = ev.touches ? ev.touches[0] : ev;
      t.innerHTML = html; t.hidden = false;
      const x = Math.max(110, Math.min(r.width - 110, p.clientX - r.left));
      t.style.left = x + 'px'; t.style.top = (p.clientY - r.top) + 'px';
    };
    box.addEventListener('mouseleave', () => { t.hidden = true; });
    return show;
  }
  const marcaAgua = (svg, w, h) => { const t = el('text', { x: w / 2, y: h / 2, 'text-anchor': 'middle', class: 'marca-agua' }, svg); t.textContent = 'FICTICIO'; };

  let META, OBS, GEO, E, nivel = 'prov', capa = 'est', sel = null;

  // ---------- cifras clave
  function stats() {
    const b = Object.fromEntries(E.bloques.map(x => [x.bloque, x]));
    const prim = [...E.listas].sort((a, c) => c.escanos[2] - a.escanos[2])[0];
    const items = [
      ['Participación', pc(E.participacion[2]), `${pc(E.participacion[1])}–${pc(E.participacion[3])}`, 'var(--ink)'],
      ['Escaños de ' + prim.lista + ' (mediana)', Math.round(prim.escanos[2]), `${prim.escanos[1]}–${prim.escanos[3]}`, col(prim.lista)],
      ['PP + Vox llegan a 176', Math.round(b['PP + Vox'].p_mayoria * 100) + ' %', 'de las simulaciones', col('PP')],
      ['PSOE + Sumar llegan a 176', Math.round(b['PSOE + Sumar'].p_mayoria * 100) + ' %', 'de las simulaciones', col('PSOE')],
    ];
    $('stats').innerHTML = items.map(([l, v, r, c]) => `<div class="stat" style="--c:${c}"><div class="v">${v}</div><div class="l">${l}</div><div class="r">${r}</div></div>`).join('');
  }

  // ---------- voto con intervalos
  function voto() {
    const box = $('voto'); box.innerHTML = '';
    const rows = E.listas.filter(l => l.voto[2] >= 0.5).sort((a, b) => b.voto[2] - a.voto[2]);
    const W = box.clientWidth || 700, lw = W < 520 ? 92 : 130, rw = 64, rh = 30, H = rows.length * rh + 24;
    const max = Math.max(...rows.map(l => Math.max(l.voto[4], OBS.voto[l.lista] || 0))) * 1.05;
    const x = v => lw + (W - lw - rw) * v / max;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Voto estimado de cada candidatura con intervalos' }, box);
    marcaAgua(svg, W, H);
    for (let t = 0; t <= max; t += max > 25 ? 10 : 5) {
      el('line', { x1: x(t), x2: x(t), y1: 0, y2: H - 20, stroke: 'var(--grid)' }, svg);
      el('text', { x: x(t), y: H - 4, 'text-anchor': 'middle' }, svg).textContent = t + ' %';
    }
    const show = tip(box);
    rows.forEach((l, i) => {
      const y = i * rh + rh / 2, c = col(l.lista), g = el('g', {}, svg), o = OBS.voto[l.lista];
      el('text', { x: lw - 8, y: y + 4, 'text-anchor': 'end', class: 'lab' }, g).textContent = l.lista;
      el('line', { x1: x(l.voto[0]), x2: x(l.voto[4]), y1: y, y2: y, stroke: c, 'stroke-width': 2, opacity: .55 }, g);
      el('rect', { x: x(l.voto[1]), y: y - 6, width: Math.max(2, x(l.voto[3]) - x(l.voto[1])), height: 12, rx: 2, fill: c, opacity: .35 }, g);
      el('circle', { cx: x(l.voto[2]), cy: y, r: 5, fill: c, stroke: 'var(--bg)', 'stroke-width': 1.5 }, g);
      if (o != null) el('line', { x1: x(o), x2: x(o), y1: y - 10, y2: y + 10, stroke: 'var(--ink)', 'stroke-width': 2 }, g);
      el('text', { x: W - rw + 8, y: y + 4, class: 'num' }, g).textContent = pc(l.voto[2]);
      el('rect', { x: 0, y: y - rh / 2, width: W, height: rh, fill: 'transparent' }, g)
        .addEventListener('mousemove', ev => show(`<b>${l.lista}</b><br>Estimación: ${pc(l.voto[2])}<br>80 %: ${pc(l.voto[1])}–${pc(l.voto[3])}<br>95 %: ${pc(l.voto[0])}–${pc(l.voto[4])}${o != null ? `<br>2023 (dato): ${pc(o)}` : ''}`, ev));
    });
  }

  // ---------- hemiciclo: asientos en filas concéntricas, repartidos de izquierda a derecha
  function asientos(N) {
    const filas = Math.max(6, Math.round(Math.sqrt(N / 2.4))), r0 = 0.38, R = 1;
    const rad = [...Array(filas)].map((_, i) => r0 + (R - r0) * i / (filas - 1)), sr = rad.reduce((a, b) => a + b, 0);
    const n = rad.map(r => Math.floor(N * r / sr));
    for (let i = filas - 1, f = N - n.reduce((a, b) => a + b, 0); f > 0; i = (i - 1 + filas) % filas, f--) n[i]++;
    const out = [];
    rad.forEach((r, i) => { for (let k = 0; k < n[i]; k++) { const a = Math.PI * (1 - k / Math.max(1, n[i] - 1)); out.push({ a, r }); } });
    out.sort((p, q) => q.a - p.a || p.r - q.r);
    return { pts: out, size: (R - r0) / (filas - 1) * 0.42 };
  }
  function hemiciclo(id, leyId, partes, total, mayoria) {
    // partes: [{lista, n, hueco}] en orden; hueco = solo contorno (designados)
    const box = $(id); box.innerHTML = '';
    const W = 400, H = 220, cx = W / 2, cy = 205, S = 190, { pts, size } = asientos(total);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': partes.filter(p => p.n).map(p => `${p.lista} ${p.n}${p.hueco ? ' designados' : ''}`).join(', ') }, box);
    marcaAgua(svg, W, H * 0.7);
    const show = tip(box);
    let i = 0;
    partes.forEach(p => {
      for (let k = 0; k < p.n; k++, i++) {
        const q = pts[i], c = col(p.lista);
        const e = el('circle', { cx: cx + S * q.r * Math.cos(q.a), cy: cy - S * q.r * Math.sin(q.a), r: S * size,
          fill: p.hueco ? 'none' : c, stroke: c, 'stroke-width': p.hueco ? 1.6 : 0 }, svg);
        e.addEventListener('mousemove', ev => show(`<b>${p.lista}</b>: ${p.n} ${p.hueco ? 'designados (ficticio)' : 'escaños'}`, ev));
      }
    });
    if (mayoria) {
      el('line', { x1: cx, x2: cx, y1: cy - S - 8, y2: cy - S * 0.3, stroke: 'var(--ink)', 'stroke-dasharray': '3 3' }, svg);
      el('text', { x: cx, y: cy - S - 12, 'text-anchor': 'middle', class: 'num' }, svg).textContent = mayoria;
    }
    el('text', { x: cx, y: cy - 6, 'text-anchor': 'middle', class: 'lab', 'font-size': 28 }, svg).textContent = total;
    const tot = {}; partes.forEach(p => { tot[p.lista] = (tot[p.lista] || 0) + p.n; });
    $(leyId).innerHTML = Object.entries(tot).filter(([, v]) => v).map(([k, v]) => `<span><i class="sw" style="background:${col(k)}"></i>${k} ${v}</span>`).join('');
  }

  function congreso() {
    const h = E.hemiciclo.congreso;
    hemiciclo('hemi-c', 'ley-c', Object.keys(h).sort(ord).map(k => ({ lista: k, n: h[k] })), 350, META.mayoria);
    $('bloques').innerHTML = E.bloques.map(b => `<div class="bloque"><div><b>${b.bloque}</b><br><span class="rg" style="color:var(--muted)">mediana ${Math.round(b.escanos[2])} escaños · 80 %: ${b.escanos[1]}–${b.escanos[3]}</span>
      <svg viewBox="0 0 300 14" aria-hidden="true" style="margin-top:4px"><rect x="0" y="3" width="300" height="8" fill="var(--grid)"/><rect x="0" y="3" width="${300 * b.p_mayoria}" height="8" fill="${col(b.listas[0])}"/></svg></div><div class="p">${Math.round(b.p_mayoria * 100)} %</div></div>`).join('');
    // distribución de escaños por partido
    const box = $('dist'); box.innerHTML = '';
    const ls = E.listas.filter(l => l.escanos[4] >= 1).sort((a, b) => b.escanos[2] - a.escanos[2]);
    const W = box.clientWidth || 700, cols = W < 520 ? 2 : 4, cw = W / cols, ch = 96, H = Math.ceil(ls.length / cols) * (ch + 10);
    const svg = el('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': 'Distribución de escaños de cada partido en las simulaciones' }, box);
    marcaAgua(svg, W, H);
    const show = tip(box);
    ls.forEach((l, i) => {
      const gx = (i % cols) * cw, gy = Math.floor(i / cols) * (ch + 10), d = l.escanos_dist, o = OBS.escanos[l.lista] || 0;
      const lo = Math.min(d.desde, o), hi = Math.max(d.desde + d.p.length - 1, o), w = (cw - 16) / (hi - lo + 1), pm = Math.max(...d.p);
      const g = el('g', { transform: `translate(${gx},${gy})` }, svg);
      el('text', { x: 0, y: 14, class: 'lab' }, g).textContent = `${l.lista} · ${Math.round(l.escanos[2])}`;
      d.p.forEach((p, k) => {
        const v = d.desde + k, bh = (ch - 40) * p / pm;
        el('rect', { x: (v - lo) * w, y: ch - 20 - bh, width: Math.max(1, w - (w > 3 ? 1 : 0)), height: bh, fill: col(l.lista) }, g)
          .addEventListener('mousemove', ev => show(`<b>${l.lista}</b>: ${v} escaños en el ${(p * 100).toFixed(1).replace('.', ',')} % de las simulaciones`, ev));
      });
      el('line', { x1: (o - lo + .5) * w, x2: (o - lo + .5) * w, y1: 20, y2: ch - 16, stroke: 'var(--ink)', 'stroke-width': 1.5 }, g);
      el('text', { x: 0, y: ch - 4, class: 'num' }, g).textContent = lo;
      el('text', { x: cw - 16, y: ch - 4, 'text-anchor': 'end', class: 'num' }, g).textContent = hi;
    });
  }

  function senado() {
    const h = E.hemiciclo.senado, des = Object.fromEntries(E.listas.map(l => [l.lista, l.designados]));
    const ks = [...new Set([...Object.keys(h), ...Object.keys(des).filter(k => des[k])])].sort(ord);
    const partes = ks.flatMap(k => [{ lista: k, n: h[k] || 0 }, { lista: k, n: des[k] || 0, hueco: true }]);
    hemiciclo('hemi-s', 'ley-s', partes, META.senado.elegidos + META.senado.designados, 133);
    $('tabla-s').tBodies[0].innerHTML = E.listas.filter(l => l.senado[4] > 0 || l.designados)
      .sort((a, b) => b.senado[2] - a.senado[2])
      .map(l => `<tr><td><i class="sw" style="background:${col(l.lista)}"></i> ${l.lista}</td><td class="n">${Math.round(l.senado[2])}</td><td class="n"><span class="rg">${l.senado[1]}–${l.senado[3]}</span></td><td class="n">${l.designados}</td></tr>`).join('');
  }

  // ---------- mapa
  let POLY = null, CCAA_DE = {};
  function prepGeo() {
    const d = GEO, out = [];
    d.poly.forEach((parts, i) => parts.forEach(f => {
      const r = []; let x = f[0], y = f[1]; r.push([x / d.S, y / d.S]);
      for (let k = 2; k < f.length; k += 2) { x += f[k]; y += f[k + 1]; r.push([x / d.S, y / d.S]); }
      out.push({ cod: d.cod[i], r });
    }));
    POLY = out;
    Object.entries(META.ccaa).forEach(([c, ps]) => ps.forEach(p => { CCAA_DE[p] = c; }));
  }
  const datoDe = (cod) => {
    const k = nivel === 'ccaa' ? CCAA_DE[cod] : cod;
    if (capa === 'est') return { k, d: nivel === 'ccaa' ? E.ccaa[k] : E.provincias[k] };
    return { k, d: nivel === 'ccaa' ? OBS.ccaa[k] : OBS.provincias[k] };
  };
  const nombre = (k) => nivel === 'ccaa' ? k : META.provincias[k];
  function colorDe(cod) {
    const { d } = datoDe(cod);
    if (!d) return 'var(--grid)';
    if (capa === 'est') {
      const top = [...d.listas].sort((a, b) => b.voto[1] - a.voto[1])[0];
      return `color-mix(in srgb, ${col(top.lista)} ${Math.round(35 + 65 * top.p_primera)}%, var(--bg))`;
    }
    const top = Object.entries(d.voto).sort((a, b) => b[1] - a[1])[0];
    return col(top[0]);
  }
  function mapa() {
    const box = $('mapa'); box.innerHTML = '';
    const k = Math.cos(40 * Math.PI / 180);
    let b = [1e9, 1e9, -1e9, -1e9];
    POLY.forEach(p => p.r.forEach(([x, y]) => { b = [Math.min(b[0], x * k), Math.min(b[1], -y), Math.max(b[2], x * k), Math.max(b[3], -y)]; }));
    const W = 800, s = W / (b[2] - b[0]), H = (b[3] - b[1]) * s;
    const svg = el('svg', { viewBox: `0 0 ${W} ${H.toFixed(0)}`, role: 'img', 'aria-label': 'Mapa por ' + (nivel === 'ccaa' ? 'comunidades' : 'provincias') }, box);
    marcaAgua(svg, W * 0.62, H * 0.15);
    const show = tip(box);
    POLY.forEach(p => {
      const dd = 'M' + p.r.map(([x, y]) => ((x * k - b[0]) * s).toFixed(1) + ',' + ((-y - b[1]) * s).toFixed(1)).join('L') + 'Z';
      const { k: clave, d } = datoDe(p.cod);
      const e = el('path', { d: dd, fill: colorDe(p.cod), stroke: 'var(--bg)', 'stroke-width': nivel === 'ccaa' ? .3 : .8, tabindex: 0, 'data-k': clave, style: 'cursor:pointer' }, svg);
      if (sel === clave) { e.setAttribute('stroke', 'var(--ink)'); e.setAttribute('stroke-width', 2); }
      const txt = () => {
        if (!d) return nombre(clave);
        if (capa === 'est') { const t = [...d.listas].sort((a, c) => c.voto[1] - a.voto[1])[0]; return `<b>${nombre(clave)}</b><br>${t.lista}: ${pc(t.voto[1])} (${pc(t.voto[0])}–${pc(t.voto[2])})<br>Probabilidad de quedar primero: ${Math.round(t.p_primera * 100)} %`; }
        const t = Object.entries(d.voto).sort((a, c) => c[1] - a[1])[0]; return `<b>${nombre(clave)}</b><br>2023: ${t[0]} ${pc(t[1])}`;
      };
      e.addEventListener('mousemove', ev => show(txt(), ev));
      const elegir = () => { sel = clave; ficha(); mapa(); };
      e.addEventListener('click', elegir);
      e.addEventListener('keydown', ev => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); elegir(); } });
    });
    // recuadro de Canarias (las islas vienen desplazadas en la geometría)
    const can = POLY.filter(p => /^3[58]/.test(p.cod)); let cb = [1e9, 1e9, -1e9, -1e9];
    can.forEach(p => p.r.forEach(([x, y]) => { const X = (x * k - b[0]) * s, Y = (-y - b[1]) * s; cb = [Math.min(cb[0], X), Math.min(cb[1], Y), Math.max(cb[2], X), Math.max(cb[3], Y)]; }));
    el('rect', { x: cb[0] - 8, y: cb[1] - 8, width: cb[2] - cb[0] + 16, height: cb[3] - cb[1] + 16, fill: 'none', stroke: 'var(--line)' }, svg);
    $('mapa-t').textContent = capa === 'est' ? 'Partido más votado en la estimación' : 'Partido más votado en julio de 2023 (dato)';
    $('mapa-s').textContent = capa === 'est'
      ? 'Color del partido con más voto en la mediana; más intenso cuanto más probable es que quede primero. Toca un territorio para ver su ficha'
      : 'Resultado oficial de las generales de 2023. Toca un territorio para ver su ficha';
  }

  function ficha() {
    const f = $('ficha');
    if (!sel) { f.innerHTML = '<p class="pendiente" style="margin:0">Elige un territorio en el mapa para ver su ficha.</p>'; return; }
    const esCCAA = nivel === 'ccaa', est = (esCCAA ? E.ccaa : E.provincias)[sel], obs = (esCCAA ? OBS.ccaa : OBS.provincias)[sel];
    const filas = [...est.listas].sort((a, b) => b.voto[1] - a.voto[1]).map(l =>
      `<tr><td><i class="sw" style="background:${col(l.lista)}"></i> ${l.lista}</td>
       <td class="n">${obs.voto[l.lista] != null ? pc(obs.voto[l.lista]) : '–'}</td>
       <td class="n">${pc(l.voto[1])} <span class="rg">${pc(l.voto[0])}–${pc(l.voto[2])}</span></td>
       <td class="n">${obs.escanos[l.lista] || 0}</td>
       <td class="n">${l.escanos[1]} <span class="rg">${l.escanos[0]}–${l.escanos[2]}</span></td>
       <td class="n">${Math.round(l.p_primera * 100)} %</td></tr>`).join('');
    let sen = '';
    if (!esCCAA) {
      const cs = META.senado.circunscripciones.filter(c => c.provincia === sel);
      sen = '<h3 class="menor">Senado (mediana de las simulaciones)</h3><p class="pendiente" style="margin:0">' + cs.map(c => {
        const m = E.senado_circ[c.cod].mediana;
        return `${c.nombre} (${c.senadores}): ` + Object.entries(m).sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ${v}`).join(', ');
      }).join(' · ') + '</p>';
    }
    f.innerHTML = `<h3>${nombre(sel)}</h3><p class="sub">${est.escanos_total} diputados en 2026 · Escenario: ${E.titulo} · Estimación ficticia</p>
      <div class="tbl"><table><thead><tr><th>Partido</th><th class="n">Voto 2023 (dato)</th><th class="n">Voto estimado · 80 %</th><th class="n">Escaños 2023</th><th class="n">Escaños estimados · 80 %</th><th class="n">Prob. de ser primero</th></tr></thead><tbody>${filas}</tbody></table></div>${sen}`;
  }

  function descargas() {
    const fs = [['meta.json', 'Metadatos: versión, semilla, circunscripciones y escenarios'], ['observado-2023.json', 'Dato observado: voto y escaños de 2023 por provincia y comunidad'],
      ...META.escenarios.map(e => [`escenario-${e.id}.json`, `Escenario «${e.titulo}» (ficticio)`])];
    $('descargas').innerHTML = fs.map(([f, t]) => `<li><a href="${DATOS + f}" download>${f}</a>: ${t}</li>`).join('');
  }

  function todo() { stats(); voto(); congreso(); senado(); mapa(); ficha(); }

  async function carga(id) {
    E = await get(`escenario-${id}.json`);
    $('supuesto').textContent = 'Supuesto: ' + E.supuesto;
    todo();
  }

  Promise.all([get('meta.json'), get('observado-2023.json'), fetch('../generales-2026/data/provincias.json').then(r => r.json())])
    .then(([m, o, g]) => {
      META = m; OBS = o; GEO = g; prepGeo();
      $('m-ver').textContent = m.version; $('m-fecha').textContent = new Date(m.generado).toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
      $('m-sim').textContent = m.simulaciones.toLocaleString('es-ES');
      document.querySelectorAll('.ver').forEach(e => { e.textContent = m.version; });
      $('esc').innerHTML = m.escenarios.map(e => `<option value="${e.id}">${e.titulo}</option>`).join('');
      $('esc').addEventListener('change', ev => carga(ev.target.value));
      document.querySelectorAll('[data-nivel]').forEach(b => b.addEventListener('click', () => {
        nivel = b.dataset.nivel; sel = null;
        document.querySelectorAll('[data-nivel]').forEach(x => x.setAttribute('aria-pressed', x === b)); mapa(); ficha();
      }));
      document.querySelectorAll('[data-capa]').forEach(b => b.addEventListener('click', () => {
        capa = b.dataset.capa; document.querySelectorAll('[data-capa]').forEach(x => x.setAttribute('aria-pressed', x === b)); mapa();
      }));
      descargas();
      return carga('base');
    })
    .catch(err => { $('stats').innerHTML = `<p class="pendiente">No se han podido cargar los datos (${err.message}).</p>`; });

  let ancho = innerWidth;
  addEventListener('resize', () => { if (Math.abs(innerWidth - ancho) > 40 && E) { ancho = innerWidth; voto(); congreso(); } });
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => E && todo());
})();
