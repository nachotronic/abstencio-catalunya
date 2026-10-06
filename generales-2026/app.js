// Mapa de las generales: municipios para toda España y secciones censales al acercarse.
// Datos en data/: meta.json, municipios.json, provincias.json, resumen.json y sec/<prov>.json (generales).
// Municipales y europeas, aparte: e/<elección>.json y sec/<prov>_<elección>.json, que se cargan al elegirlas.
(async function () {
  const $ = s => document.querySelector(s);
  const get = f => fetch('data/' + f).then(r => { if (!r.ok) throw new Error(f); return r.json(); });
  const [META, MUN, PROV, RES] = await Promise.all([get('meta.json'), get('municipios.json'), get('provincias.json'), get('resumen.json')]);
  const FAM = META.familias, FCOD = FAM.map(f => f.cod);
  const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  FAM.forEach(f => f.rgb = hex(f.color));
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const pct = v => v == null ? '–' : (v * 100).toFixed(1).replace('.', ',') + '%';
  const eur = v => v == null ? '–' : v.toLocaleString('es-ES') + ' €';
  const num = v => v == null ? '–' : v.toLocaleString('es-ES');

  // ---------- geometría: anillos con coordenadas en deltas enteros
  function decode(d) {
    const out = [];
    d.poly.forEach((parts, i) => parts.forEach(f => {
      const r = []; let x = f[0], y = f[1]; r.push([x / d.S, y / d.S]);
      for (let k = 2; k < f.length; k += 2) { x += f[k]; y += f[k + 1]; r.push([x / d.S, y / d.S]); }
      out.push({ i, polygon: r, ring: [...r, r[0]] });
    }));
    return out;
  }
  const MUNP = decode(MUN);
  const PROVP = decode(PROV);
  const PROVBOX = {};
  PROVP.forEach(p => {
    const c = PROV.cod[p.i], b = PROVBOX[c] || (PROVBOX[c] = [180, 90, -180, -90]);
    p.polygon.forEach(([x, y]) => { b[0] = Math.min(b[0], x); b[1] = Math.min(b[1], y); b[2] = Math.max(b[2], x); b[3] = Math.max(b[3], y); });
  });
  const SEC = {};           // prov -> {d, polys}
  const loading = new Set();

  // ---------- estado
  const ELEC = META.elecciones;
  const tipoDe = y => (ELEC.find(e => e.cod === y) || {}).tipo || 'generales';
  const st = { y: ELEC.filter(e => tipoDe(e.cod) === 'generales').pop().cod, v: 'gana', party: 'PP' };
  // participación: la escala depende del tipo de elección (en europeas vota mucha menos gente)
  const PARTDOM = { generales: [.55, .85], municipales: [.45, .85], europeas: [.30, .75] };
  const VARS = {
    gana: { name: 'Partido más votado' },
    party: { name: 'Voto a un partido' },
    part: { name: 'Participación', key: y => y + '_part', dom: [.55, .85], fmt: pct, ramp: 'blue' },
    renta_uc: { name: 'Renta por unidad de consumo (2023)', dom: [11000, 30000], fmt: eur, ramp: 'green' },
    pobreza: { name: 'Población en riesgo de pobreza (2023)', dom: [.05, .40], fmt: pct, ramp: 'red' },
    edad_media: { name: 'Edad media (2023)', dom: [38, 54], fmt: v => v == null ? '–' : v.toFixed(1).replace('.', ',') + ' años', ramp: 'blue' },
    extranjeros: { name: 'Población extranjera (2023)', dom: [0, .30], fmt: pct, ramp: 'amber' },
    sin_derecho: { name: 'Adultos sin derecho a voto (2023)', dom: [0, .30], fmt: pct, ramp: 'amber' },
    estudios_sup_2021: { name: 'Adultos con estudios superiores (2021)', dom: [.10, .50], fmt: pct, ramp: 'green' },
    paro_2021: { name: 'Tasa de paro (2021)', dom: [.06, .30], fmt: pct, ramp: 'red' },
  };
  const RAMPS = {
    blue: ['#eef3fa', '#cfdff0', '#a7c4e3', '#78a3d2', '#4d82bd', '#2f63a0', '#1d4679', '#122c4f'],
    green: ['#eef6ef', '#cfe8d3', '#a6d3ae', '#77b984', '#4c9b5d', '#2f7c40', '#1d5b2c', '#123b1c'],
    red: ['#fbefec', '#f5d2ca', '#eaaa9c', '#da7c69', '#c4533f', '#a03526', '#76231a', '#4d150f'],
    amber: ['#fcf3e2', '#f6deb0', '#efc47b', '#e2a548', '#c98722', '#a26810', '#774b09', '#4c2f05'],
  };
  Object.keys(RAMPS).forEach(k => RAMPS[k] = RAMPS[k].map(hex));
  const NODATA = () => hex(css('--nodata') || '#d9d6cf');
  const BG = () => hex(css('--map-bg') || '#f4f1ea');
  const mix = (a, b, t) => [0, 1, 2].map(k => Math.round(a[k] + (b[k] - a[k]) * t));
  // En modo oscuro la rampa se invierte: el valor alto es el más claro, para que destaque sobre el fondo.
  const isDark = () => { const t = document.documentElement.dataset.theme; return t ? t === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches; };
  const rampa = name => isDark() ? RAMPS[name].slice().reverse() : RAMPS[name];
  const ramp = (name, t) => {
    const r = rampa(name), x = Math.max(0, Math.min(1, t)) * (r.length - 1), k = Math.min(r.length - 2, Math.floor(x));
    return mix(r[k], r[k + 1], x - k);
  };
  const partyMax = {};
  function domParty() {
    const k = st.y + '_' + st.party, v = (MUN[k] || []).filter(x => x != null).sort((a, b) => a - b);
    partyMax[k] = Math.max(.1, v[Math.floor(v.length * .97)] || .5);
    return partyMax[k];
  }

  function value(d, i) {
    if (st.v === 'part') return d[st.y + '_part'] ? d[st.y + '_part'][i] : null;
    if (st.v === 'party') return d[st.y + '_' + st.party] ? d[st.y + '_' + st.party][i] : null;
    return d[st.v] ? d[st.v][i] : null;
  }
  function color(d, i) {
    if (st.v === 'gana') {
      const g = d[st.y + '_gana'] ? d[st.y + '_gana'][i] : -1;
      if (g == null || g < 0) return NODATA();
      const f = FAM[g], s = d[st.y + '_' + f.cod][i] || 0;
      return mix(BG(), f.rgb, Math.max(.28, Math.min(1, (s - .15) / .35)));
    }
    const v = value(d, i);
    if (v == null) return NODATA();
    if (st.v === 'party') {
      const f = FAM[FCOD.indexOf(st.party)];
      return mix(BG(), f.rgb, Math.min(1, .06 + .94 * v / (partyMax[st.y + '_' + st.party] || domParty())));
    }
    const V = VARS[st.v], dom = st.v === 'part' ? PARTDOM[tipoDe(st.y)] : V.dom, t = (v - dom[0]) / (dom[1] - dom[0]);
    return ramp(V.ramp, t);
  }

  // ---------- mapa
  const narrow = () => window.innerWidth < 760;
  const HOME = () => {
    const el = $('#map'), W = el.clientWidth || 800, H = el.clientHeight || 600;
    const z = Math.min(Math.log2(W / (512 * 18.5 / 360)), Math.log2(H / (512 * 13.5 / 360)));
    return { longitude: -4.3, latitude: 38.6, zoom: Math.round(z * 100) / 100, pitch: 0, bearing: 0 };
  };
  let view = HOME();
  const LABELS = ['28079', '08019', '46250', '41091', '50297', '29067', '48020', '07040', '35016', '15030'];
  const lab = LABELS.map(c => { const i = MUN.cod.indexOf(c); return i < 0 ? null : { t: MUN.nombre[i], p: MUN.c[i] }; }).filter(Boolean);
  const [dx, dy] = META.canarias;
  const CANFRAME = [{ path: [[-18.5 + dx, 29.6 + dy], [-13.1 + dx, 29.6 + dy], [-13.1 + dx, 27.4 + dy]] }];
  let hover = null;

  function secVisible() { return view.zoom >= 7.3; }
  function secHas(p) { return SEC[p] && SEC[p].d[st.y + '_part']; }

  function layers() {
    const L = [];
    const trig = [st.y, st.v, st.party, document.documentElement.dataset.theme || ''];
    L.push(new deck.SolidPolygonLayer({
      id: 'mun', data: MUNP, getPolygon: o => o.polygon, getFillColor: o => color(MUN, o.i),
      pickable: true, updateTriggers: { getFillColor: trig },
    }));
    if (secVisible()) {
      Object.keys(SEC).forEach(p => {
        if (!secHas(p)) return;
        const S = SEC[p];
        L.push(new deck.SolidPolygonLayer({
          id: 'sec' + p, data: S.polys, getPolygon: o => o.polygon, getFillColor: o => color(S.d, o.i),
          pickable: true, updateTriggers: { getFillColor: trig },
        }));
      });
    }
    const line = hex(css('--map-line') || '#ffffff');
    if (view.zoom >= 6.6) {
      L.push(new deck.PathLayer({ id: 'munline', data: MUNP, getPath: o => o.ring, getColor: [...line, 150], widthUnits: 'pixels', getWidth: view.zoom >= 8.5 ? .9 : .4 }));
    }
    L.push(new deck.PathLayer({ id: 'prov', data: PROVP, getPath: o => o.ring, getColor: [...line, 255], widthUnits: 'pixels', getWidth: 1.2, widthMinPixels: 1 }));
    L.push(new deck.PathLayer({ id: 'canframe', data: CANFRAME, getPath: o => o.path, getColor: hex(css('--muted') || '#888'), widthUnits: 'pixels', getWidth: 1 }));
    if (hover) {
      L.push(new deck.PathLayer({ id: 'hl', data: hover.polys, getPath: o => o.ring, getColor: hex(css('--ink') || '#111'), widthUnits: 'pixels', getWidth: 2 }));
    }
    if (view.zoom < 8) {
      L.push(new deck.TextLayer({
        id: 'lab', data: lab, getPosition: o => o.p, getText: o => o.t, getSize: 12, fontFamily: 'IBM Plex Sans, system-ui, sans-serif', fontWeight: 600,
        getColor: hex(css('--ink') || '#111'), outlineWidth: 3, outlineColor: [...hex(css('--surface') || '#fff'), 230], fontSettings: { sdf: true },
        characterSet: 'auto', parameters: { depthCompare: 'always' },
      }));
    }
    return L;
  }

  const dk = new deck.Deck({
    parent: $('#map'), initialViewState: view, controller: { dragRotate: false, touchRotate: false, scrollZoom: { smooth: true } },
    views: new deck.MapView({ repeat: false }), layers: [], getCursor: ({ isHovering }) => isHovering ? 'pointer' : 'grab',
    onViewStateChange: ({ viewState }) => { view = viewState; loadVisible(); redraw(); return viewState; },
    onHover: info => { setHover(info); },
    onClick: info => { setHover(info, true); },
  });
  function redraw() { dk.setProps({ layers: layers() }); }

  // elecciones que viven en ficheros aparte: columnas que se añaden a MUN y a cada provincia al elegirlas
  const aparte = y => (ELEC.find(e => e.cod === y) || {}).aparte;
  const pedido = {};
  function asegura(y) {
    if (!aparte(y) || MUN[y + '_part']) return Promise.resolve();
    return pedido[y] || (pedido[y] = get('e/' + y + '.json').then(d => { Object.assign(MUN, d); }));
  }
  function aseguraSec(p, y) {
    const e = ELEC.find(e => e.cod === y);
    if (!e || !e.aparte || !e.secciones || !SEC[p] || SEC[p].d[y + '_part']) return;
    const k = p + '_' + y; if (pedido[k]) return;
    pedido[k] = get('sec/' + k + '.json').then(d => { Object.assign(SEC[p].d, d); redraw(); }).catch(() => delete pedido[k]);
  }
  async function loadVisible() {
    if (!secVisible()) return;
    const vp = dk.getViewports()[0]; if (!vp) return;
    const [w, s] = vp.unproject([0, vp.height]), [e, n] = vp.unproject([vp.width, 0]);
    for (const [p, b] of Object.entries(PROVBOX)) {
      if (b[0] > e || b[2] < w || b[1] > n || b[3] < s || loading.has(p)) continue;
      if (SEC[p]) { aseguraSec(p, st.y); continue; }
      loading.add(p);
      get('sec/' + p + '.json').then(d => { SEC[p] = { d, polys: decode(d) }; loading.delete(p); aseguraSec(p, st.y); redraw(); }).catch(() => loading.delete(p));
    }
  }

  // ---------- ficha (tooltip)
  const tip = $('#tip');
  function ficha(d, i, isSec) {
    const y = st.y, rows = FAM.map((f, k) => ({ f, v: d[y + '_' + f.cod] ? d[y + '_' + f.cod][i] : null }))
      .filter(r => r.v != null && r.v > 0.005).sort((a, b) => b.v - a.v).slice(0, 6);
    const e = ELEC.find(x => x.cod === y).nombre;
    const mi = isSec ? MUN.cod.indexOf(d.cod[i].slice(0, 5)) : i;
    const title = isSec ? `${MUN.nombre[mi]} · sección ${d.cod[i].slice(5, 7)}-${d.cod[i].slice(7)}` : MUN.nombre[i];
    const sub = isSec ? MUN.provs[MUN.prov[mi]] : MUN.provs[MUN.prov[i]];
    const max = rows.length ? rows[0].v : 1;
    let h = `<div class="t-h">${title}</div><div class="t-s">${sub || ''} · ${e}</div>`;
    if (!rows.length) h += `<p class="t-na">Sin resultados para esta elección con estos límites${isSec ? ' de sección' : ''}.</p>`;
    h += '<table class="t-bars">' + rows.map(r => `<tr><th>${r.f.nombre}</th><td><span class="bar" style="width:${Math.max(2, r.v / max * 100)}%;background:${r.f.color}"></span></td><td class="n">${pct(r.v)}</td></tr>`).join('') + '</table>';
    const part = d[y + '_part'] ? d[y + '_part'][i] : null;
    const esc = d[y + '_esc'] ? d[y + '_esc'][i] : null;
    h += `<dl class="t-kv">${esc != null ? `<dt>Escrutado</dt><dd>${pct(esc)}</dd>` : ''}<dt>Participación</dt><dd>${pct(part)}</dd>
      <dt>Renta por u. de consumo</dt><dd>${eur(d.renta_uc[i])}</dd>
      <dt>En riesgo de pobreza</dt><dd>${pct(d.pobreza[i])}</dd>
      <dt>Edad media</dt><dd>${VARS.edad_media.fmt(d.edad_media[i])}</dd>
      <dt>Población extranjera</dt><dd>${pct(d.extranjeros[i])}</dd>
      <dt>Habitantes</dt><dd>${num(d.poblacion[i])}</dd></dl>`;
    return h;
  }
  function setHover(info, pin) {
    const o = info.object;
    if (!o) { if (!pin) { tip.hidden = true; hover = null; redraw(); } return; }
    const id = info.layer.id, isSec = id.startsWith('sec');
    const d = isSec ? SEC[id.slice(3)].d : MUN, all = isSec ? SEC[id.slice(3)].polys : MUNP;
    tip.innerHTML = ficha(d, o.i, isSec); tip.hidden = false;
    const W = $('#map').clientWidth, H = $('#map').clientHeight, tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = info.x + 14, y = info.y + 14;
    if (x + tw > W - 8) x = info.x - tw - 14; if (y + th > H - 8) y = Math.max(8, H - th - 8);
    if (narrow()) { tip.style.left = '8px'; tip.style.top = 'auto'; tip.style.bottom = '8px'; }
    else { tip.style.left = Math.max(8, x) + 'px'; tip.style.top = y + 'px'; tip.style.bottom = 'auto'; }
    if (!hover || hover.key !== id + o.i) { hover = { key: id + o.i, polys: all.filter(p => p.i === o.i) }; redraw(); }
  }

  // ---------- leyenda
  function legend() {
    const el = $('#legend');
    if (st.v === 'gana') {
      const y = st.y, used = new Set(MUN[y + '_gana']);
      el.innerHTML = `<div class="lg-t">Partido más votado · ${ELEC.find(e => e.cod === y).nombre}</div><div class="lg-sw">` +
        FAM.filter((f, k) => used.has(k)).map(f => `<span><b style="background:${f.color}"></b>${f.nombre}</span>`).join('') +
        `</div><div class="lg-n">Más intenso cuanto mayor es su porcentaje de voto</div>`;
      return;
    }
    let lo, hi, cols, fmt, name;
    if (st.v === 'party') {
      const f = FAM[FCOD.indexOf(st.party)], mx = domParty(), bg = BG();
      cols = [0, .25, .5, .75, 1].map(t => `rgb(${mix(bg, f.rgb, .06 + .94 * t)})`); lo = 0; hi = mx; fmt = pct; name = 'Voto a ' + f.nombre + ' · ' + ELEC.find(e => e.cod === st.y).nombre;
    } else {
      const V = VARS[st.v]; cols = rampa(V.ramp).map(c => `rgb(${c})`); [lo, hi] = st.v === 'part' ? PARTDOM[tipoDe(st.y)] : V.dom; fmt = V.fmt;
      name = V.name + (st.v === 'part' ? ' · ' + ELEC.find(e => e.cod === st.y).nombre : '');
    }
    el.innerHTML = `<div class="lg-t">${name}</div><div class="lg-g" style="background:linear-gradient(90deg,${cols.join(',')})"></div><div class="lg-x"><span>${fmt(lo)} o menos</span><span>${fmt(hi)} o más</span></div><div class="lg-n"><b class="nd" style="background:rgb(${NODATA()})"></b>sin dato</div>`;
  }

  // ---------- controles
  const selE = $('#sel-elec'), selV = $('#sel-var'), selP = $('#sel-party');
  const GRUPOS = [['generales', 'Generales'], ['municipales', 'Municipales'], ['europeas', 'Europeas']];
  const opciones = () => {
    selE.innerHTML = GRUPOS.map(([t, nom]) => {
      const es = ELEC.filter(e => (e.tipo || 'generales') === t).sort((a, b) => b.cod.replace(/^\D/, '') < a.cod.replace(/^\D/, '') ? -1 : 1);
      if (!es.length) return '';
      const extra = t === 'generales' && !ELEC.some(e => e.cod.startsWith('2026')) ? '<option disabled>29N 2026 (la noche electoral)</option>' : '';
      return `<optgroup label="${nom}">${extra}${es.map(e => `<option value="${e.cod}">${e.nombre}</option>`).join('')}</optgroup>`;
    }).join('');
    selE.value = st.y;
  };
  opciones();
  selV.innerHTML = Object.entries(VARS).map(([k, v]) => `<option value="${k}">${v.name}</option>`).join('');
  selP.innerHTML = FAM.filter(f => f.cod !== 'OTROS').map(f => `<option value="${f.cod}">${f.nombre}</option>`).join('');
  const sync = () => { selP.parentElement.hidden = st.v !== 'party'; selE.disabled = !['gana', 'party', 'part'].includes(st.v); legend(); redraw(); tip.hidden = true; };
  const elige = async y => {
    st.y = y; selE.disabled = true;
    try { await asegura(y); } finally { selE.disabled = false; }
    Object.keys(SEC).forEach(p => aseguraSec(p, y)); sync();
  };
  selE.onchange = () => elige(selE.value);
  selV.onchange = () => { st.v = selV.value; sync(); };
  selP.onchange = () => { st.party = selP.value; sync(); };
  document.querySelectorAll('[data-go]').forEach(b => b.addEventListener('click', e => {
    e.preventDefault(); const [v, p, y] = b.dataset.go.split(':');
    st.v = v; if (p) st.party = p; selV.value = st.v; selP.value = st.party;
    if (y) { selE.value = y; elige(y); } else sync();
    $('#mapa').scrollIntoView({ behavior: 'smooth' });
  }));

  // búsqueda de municipio
  const dl = $('#munlist');
  const ORD = MUN.nombre.map((n, i) => i).sort((a, b) => (MUN.poblacion[b] || 0) - (MUN.poblacion[a] || 0));
  dl.innerHTML = ORD.map(i => `<option value="${MUN.nombre[i]} (${MUN.provs[MUN.prov[i]] || ''})">`).join('');
  $('#q').addEventListener('change', e => {
    const v = e.target.value.trim().toLowerCase(); if (!v) return;
    const i = ORD.find(i => `${MUN.nombre[i]} (${MUN.provs[MUN.prov[i]] || ''})`.toLowerCase() === v) ?? ORD.find(i => MUN.nombre[i].toLowerCase().startsWith(v));
    if (i == null) return;
    const big = (MUN.poblacion[i] || 0) > 200000;
    fly({ longitude: MUN.c[i][0], latitude: MUN.c[i][1], zoom: big ? 10.2 : 11 });
    const all = MUNP.filter(p => p.i === i); hover = { key: 'mun' + i, polys: all }; redraw();
  });
  $('#home').onclick = () => fly(HOME());
  function fly(to) {
    view = { ...view, ...to, transitionDuration: 'auto', transitionInterpolator: new deck.FlyToInterpolator({ speed: 1.6 }) };
    dk.setProps({ initialViewState: view });
  }
  window.addEventListener('resize', () => redraw());
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { legend(); redraw(); });
  sync();


  // ---------- directo (noche electoral): JSON normalizado (ver actualizar_29n.py) cada minuto
  const DIRURL = new URLSearchParams(location.search).get('directo') || (META.directo && META.directo.url);
  const REG = (META.reglas || []).map(([c, p]) => [c, new RegExp(p)]);
  const famDe = s => { const a = (s || '').toUpperCase().trim(); for (const [c, r] of REG) if (r.test(a)) return c; return 'OTROS'; };
  if (DIRURL) directo(DIRURL);
  async function directo(url) {
    let first = true;
    const tick = async () => {
      try {
        const r = await fetch(url + (url.includes('?') ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' });
        if (!r.ok) throw new Error(r.status);
        aplica(await r.json(), first); first = false;
      } catch (e) { $('#d-estado').textContent = 'sin conexión con los resultados, reintentando…'; }
    };
    await tick(); setInterval(tick, 60000);
  }
  function dhondt(votos, n) {
    const q = []; votos.forEach((v, k) => { for (let d = 1; d <= n; d++) q.push([v / d, k]); });
    q.sort((a, b) => b[0] - a[0]); const out = new Array(votos.length).fill(0);
    q.slice(0, n).forEach(([v, k]) => { if (v > 0) out[k]++; }); return out;
  }
  function aplica(F, first) {
    const y = F.eleccion || META.directo.eleccion, fam = F.siglas.map(famDe), fk = fam.map(c => FCOD.indexOf(c));
    const n = MUN.cod.length, idx = {}; MUN.cod.forEach((c, i) => idx[c] = i);
    const col = { part: new Array(n).fill(null), gana: new Array(n).fill(-1), esc: new Array(n).fill(null) };
    FCOD.forEach(c => col[c] = new Array(n).fill(null));
    const prov = {}, nat = { ct: 0, ce: 0, val: 0, f: new Array(FCOD.length).fill(0) };
    for (const [c, a] of Object.entries(F.mun)) {
      const [ct, ce, vot, bl, nu, ...v] = a, i = idx[c.padStart(5, '0')];
      nat.ct += ct; nat.ce += ce;
      const P = prov[c.slice(0, 2)] || (prov[c.slice(0, 2)] = { bl: 0, v: new Array(v.length).fill(0) });
      P.bl += bl; v.forEach((x, k) => P.v[k] += x);
      const val = v.reduce((s, x) => s + x, 0) + bl; nat.val += val;
      const f = new Array(FCOD.length).fill(0); v.forEach((x, k) => f[fk[k]] += x); f.forEach((x, k) => nat.f[k] += x);
      if (i == null) continue;
      col.esc[i] = ct ? ce / ct : null;
      if (!ce || !val) continue;
      col.part[i] = vot / ce;
      let g = -1; FCOD.forEach((c, k) => { col[c][i] = f[k] / val; if (c !== 'OTROS' && (g < 0 || f[k] > f[g])) g = k; });
      col.gana[i] = g;
    }
    Object.entries(col).forEach(([k, v]) => MUN[y + '_' + k] = v);
    delete partyMax[y + '_' + st.party]; Object.keys(partyMax).forEach(k => k.startsWith(y) && delete partyMax[k]);
    // escaños: D'Hondt por provincia con barrera del 3% del voto válido de la circunscripción
    const E = (META.escanos || {})[y] || {}, seats = new Array(FCOD.length).fill(0);
    for (const [p, P] of Object.entries(prov)) {
      const val = P.v.reduce((s, x) => s + x, 0) + P.bl;
      const s = dhondt(P.v.map(x => x >= .03 * val ? x : 0), E[p] || 0);
      s.forEach((x, k) => seats[fk[k]] += x);
    }
    if (!ELEC.some(e => e.cod === y)) {
      ELEC.push({ cod: y, nombre: META.directo.nombre || y, tipo: 'generales', secciones: false });
      opciones();
    }
    if (first) { st.y = y; if (!['gana', 'party', 'part'].includes(st.v)) st.v = 'gana'; selV.value = st.v; }
    selE.value = st.y;
    const box = $('#directo'); box.hidden = false;
    $('#d-nombre').textContent = (F.simulacro ? 'Simulacro con datos del 23J · ' : '') + (META.directo.nombre || y);
    $('#d-esc').textContent = pct(F.escrutado ?? (nat.ct ? nat.ce / nat.ct : 0));
    const t = F.actualizado ? new Date(F.actualizado) : new Date();
    $('#d-estado').textContent = 'actualizado a las ' + t.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    const ord = FCOD.map((c, k) => k).filter(k => seats[k] > 0 || nat.f[k] / nat.val > .01)
      .sort((a, b) => (seats[b] - seats[a]) || (nat.f[b] - nat.f[a]));
    const tot = seats.reduce((s, x) => s + x, 0) || 1;
    $('#d-seats').innerHTML = ord.filter(k => seats[k]).map(k => `<span title="${FAM[k].nombre}: ${seats[k]}" style="flex:${seats[k]};background:${FAM[k].color}"></span>`).join('') +
      (tot >= 350 ? '<i></i><em>176, mayoría absoluta</em>' : '');
    $('#d-leg').innerHTML = ord.map(k => `<span><b style="background:${FAM[k].color}"></b>${FAM[k].nombre} <span class="n">${seats[k]}</span> <span class="mut">${pct(nat.val ? nat.f[k] / nat.val : 0)}</span></span>`).join('');
    sync();
  }

  // ---------- gráficos: voto por decil
  const CH = ['PP', 'PSOE', 'VOX', 'SUMAR'];
  document.querySelectorAll('.chart[data-var]').forEach(el => drawChart(el, el.dataset.var));
  function drawChart(el, v) {
    const D = RES.variables[v].deciles, W = 320, H = 210, m = { l: 34, r: 74, t: 10, b: 28 };
    const x = d => m.l + (d - 1) / 9 * (W - m.l - m.r), max = .5, yv = p => m.t + (1 - p / max) * (H - m.t - m.b);
    let s = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="Voto por decil de ${RES.variables[v].nombre}">`;
    [0, .1, .2, .3, .4, .5].forEach(g => s += `<line class="grid" x1="${m.l}" x2="${W - m.r}" y1="${yv(g)}" y2="${yv(g)}"/><text class="ax" x="${m.l - 6}" y="${yv(g) + 4}" text-anchor="end">${g * 100}%</text>`);
    s += `<text class="ax" x="${m.l}" y="${H - 8}">${el.dataset.lo}</text><text class="ax" x="${W - m.r}" y="${H - 8}" text-anchor="end">${el.dataset.hi}</text>`;
    const ends = [];
    CH.forEach(c => {
      const f = FAM[FCOD.indexOf(c)];
      s += `<polyline fill="none" stroke="${f.color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" points="${D.map(d => x(d.d) + ',' + yv(d[c])).join(' ')}"/>`;
      ends.push({ c: f.nombre.split(' / ')[0], col: f.color, y: yv(D[9][c]), v: D[9][c] });
    });
    ends.sort((a, b) => a.y - b.y); for (let k = 1; k < ends.length; k++) if (ends[k].y - ends[k - 1].y < 12) ends[k].y = ends[k - 1].y + 12;
    ends.forEach(e => s += `<circle cx="${x(10)}" cy="${e.y}" r="0"/><text class="lbl" x="${x(10) + 6}" y="${e.y + 4}"><tspan fill="${e.col}">●</tspan> ${e.c}</text>`);
    s += `<line class="xh" visibility="hidden" y1="${m.t}" y2="${H - m.b}" x1="0" x2="0"/>`;
    D.forEach(d => s += `<rect class="hit" data-d="${d.d}" x="${x(d.d) - (W - m.l - m.r) / 18}" y="${m.t}" width="${(W - m.l - m.r) / 9}" height="${H - m.t - m.b}"/>`);
    s += '</svg>';
    el.innerHTML = s + '<div class="ctip" hidden></div>';
    const ct = el.querySelector('.ctip'), xh = el.querySelector('.xh'), V = VARS[v] || { fmt: pct };
    el.querySelectorAll('.hit').forEach(r => {
      const show = () => {
        const d = D[+r.dataset.d - 1]; xh.setAttribute('x1', x(d.d)); xh.setAttribute('x2', x(d.d)); xh.setAttribute('visibility', 'visible');
        ct.innerHTML = `<b>Decil ${d.d}</b> <span class="mut">(${V.fmt(d.lo)} – ${V.fmt(d.hi)})</span><br>` +
          CH.map(c => { const f = FAM[FCOD.indexOf(c)]; return `<span style="color:${f.color}">●</span> ${f.nombre} ${pct(d[c])}`; }).join('<br>') + `<br>Participación ${pct(d.part)}`;
        ct.hidden = false; ct.style.left = Math.min(el.clientWidth - 170, Math.max(0, x(d.d) / W * el.clientWidth - 80)) + 'px';
      };
      r.addEventListener('mouseenter', show); r.addEventListener('click', show);
    });
    el.addEventListener('mouseleave', () => { ct.hidden = true; xh.setAttribute('visibility', 'hidden'); });
  }
})().catch(err => {
  const f = document.querySelector('#fallback'); if (f) { f.hidden = false; f.textContent += ' (' + err.message + ')'; }
  console.error(err);
});
