// Mapa de las generales: municipios para toda España y secciones censales al acercarse.
// Datos en data/: meta.json, municipios.json, provincias.json, resumen.json y sec/<prov>.json (generales).
// Municipales y europeas, aparte: e/<elección>.json y sec/<prov>_<elección>.json, que se cargan al elegirlas.
(async function () {
  const $ = s => document.querySelector(s);
  // Ruta de los datos relativa a este script, para que la página funcione también como portada en la raíz.
  const RAIZ = ((document.currentScript && document.currentScript.src) || '').replace(/[^/]*$/, '');
  const get = f => fetch(RAIZ + 'data/' + f).then(r => { if (!r.ok) throw new Error(f); return r.json(); });
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
  // Canarias llega en los datos ya desplazada al suroeste de la península (META.canarias). Aquí se mueve otra vez para que
  // el recuadro no ensanche el mapa y España se vea más grande: en pantallas anchas, al mar entre Alicante y Argelia;
  // en el móvil, debajo de Almería y Murcia. Se decide al cargar la página.
  const ESTRECHO = window.innerWidth < 760;
  const CAN = ESTRECHO ? [11.16, -0.74] : [13.16, 1.46], esCan = c => /^3[58]/.test(String(c));
  // El traslado se hace en Mercator y en teselas enteras de zoom 10 (no en grados), para que el callejero de las islas
  // se pueda poner encima del recuadro desplazando las teselas: la forma de las islas es la real.
  const [CDX, CDY] = META.canarias, T10 = 1024;
  const mY = lat => (1 - Math.log(Math.tan(Math.PI / 4 + lat * Math.PI / 360)) / Math.PI) / 2;
  const mLat = t => Math.atan(Math.sinh(Math.PI * (1 - 2 * t))) * 180 / Math.PI;
  const CANT = [Math.round((CDX + CAN[0]) / 360 * T10), Math.round((mY(28.3 + CDY + CAN[1]) - mY(28.3)) * T10)];
  const canT = q => { const t = mY(q[1] - CDY) + CANT[1] / T10; q[0] = q[0] - CDX + CANT[0] * 360 / T10; q[1] = mLat(t); return q; };
  const aCan = rings => rings.forEach(o => { o.polygon.forEach(canT); });
  MUN.c.forEach((q, i) => { if (q && esCan(MUN.cod[i])) MUN.c[i] = canT([q[0], q[1]]); });
  const MUNP = decode(MUN);
  aCan(MUNP.filter(o => esCan(MUN.cod[o.i])));
  const PROVP = decode(PROV);
  aCan(PROVP.filter(o => esCan(PROV.cod[o.i])));
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
  // Vista inicial: encaja la península, Baleares y el recuadro de Canarias con un 3 % de margen. Pantalla ancha:
  // lon −9,3 a 5,6 y lat 35,3 a 43,8; móvil: lon −9,3 a 4,4 y lat 33,2 a 43,8. El alto va en grados Mercator, no de latitud.
  const HOME = () => {
    const el = $('#map'), W = el.clientWidth || 800, H = el.clientHeight || 600;
    const [ancho, alto, longitude, latitude] = ESTRECHO ? [13.7, 13.6, -2.49, 38.7] : [15, 11.1, -1.87, 39.68];
    const z = Math.min(Math.log2(W / (512 * ancho * 1.03 / 360)), Math.log2(H / (512 * alto * 1.03 / 360)));
    return { longitude, latitude, zoom: Math.round(z * 100) / 100, pitch: 0, bearing: 0 };
  };
  let view = HOME();
  const LABELS = ['28079', '08019', '46250', '41091', '50297', '29067', '48020', '07040', '35016', '15030'];
  const lab = LABELS.map(c => { const i = MUN.cod.indexOf(c); return i < 0 ? null : { t: MUN.nombre[i], p: MUN.c[i] }; }).filter(Boolean);
  const [[x0, y0], [x1, y1]] = [canT([-18.4 + CDX, 27.4 + CDY]), canT([-13.2 + CDX, 29.6 + CDY])];
  const CANFRAME = [{ path: [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]] }];
  let hover = null;

  function secVisible() { return view.zoom >= 7.3; }
  function secHas(p) { return SEC[p] && SEC[p].d[st.y + '_part']; }

  // ---------- callejero: calles, nombres de calles y de barrios encima de las secciones al acercarse (OpenFreeMap,
  // teselas vectoriales con datos de OpenStreetMap, sin clave). Se puede quitar con el botón «Quitar calles».
  const CALLE_Z = 12;
  let calles = true;
  try { calles = localStorage.getItem('mapa-calles') !== 'no'; } catch (e) { /* sin almacenamiento: activado */ }
  const conCalles = () => calles && view.zoom >= CALLE_Z;
  // plantilla de las teselas: la da el TileJSON de OpenFreeMap, que cambia de versión cada semana. Si falla, sin calles.
  let OFM;
  const pideOFM = () => {
    if (OFM === undefined) OFM = fetch('https://tiles.openfreemap.org/planet').then(r => r.json()).then(j => j.tiles[0])
      .catch(() => false).then(u => { OFM = u; redraw(); });
    return OFM;
  };
  const enRecuadro = ([[w, s], [e, n]]) => !(e < x0 || w > x1 || n < y0 || s > y1);
  // [grosor en px, zoom de tesela desde el que se dibuja, zoom del mapa desde el que se rotula, prioridad del rótulo]
  const VIA = { motorway: [2.6, 12, 13, 40], trunk: [2.6, 12, 13, 40], primary: [2.4, 12, 13, 30], secondary: [1.8, 12, 13.5, 20],
    tertiary: [1.5, 13, 14, 15], minor: [1, 14, 15, 5], pedestrian: [.8, 14, 15.5, 2] };
  // nombres de lugar: prioridad (los barrios por encima de las calles)
  const BARRIO = { suburb: 120, quarter: 110, neighbourhood: 100, town: 130, village: 125, hamlet: 90 };
  // De cada tesela se queda lo que se pinta: las vías, y como puntos los nombres de barrios y calles (en el centro de
  // la calle y girados como ella). Coordenadas locales de la tesela, con la y hacia abajo.
  function prepara(F, z) {
    const out = [];
    for (const f of F || []) {
      const P = f.properties, g = f.geometry, ln = P.layerName;
      if (ln === 'transportation') {
        const v = VIA[P.class]; if (v && z >= v[1] && P.brunnel !== 'tunnel') { P.w = v[0]; out.push(f); }
      } else if (ln === 'place') {
        if (P.name && P.class in BARRIO && g.type === 'Point') out.push({ type: 'Feature', geometry: g, properties: { t: P.name, s: 13, p: BARRIO[P.class], z: 0 } });
      } else if (ln === 'transportation_name' && z >= 13 && P.name && VIA[P.class]) {
        const c = g.type === 'MultiLineString' ? g.coordinates.reduce((a, b) => b.length > a.length ? b : a, []) : g.coordinates;
        if (!c || c.length < 2) continue;
        const k = Math.max(0, Math.floor(c.length / 2) - 1), [ax, ay] = c[k], [bx, by] = c[k + 1];
        let a = -Math.atan2(by - ay, bx - ax) * 180 / Math.PI; if (a > 90) a -= 180; if (a < -90) a += 180;
        out.push({ type: 'Feature', geometry: { type: 'Point', coordinates: [(ax + bx) / 2, (ay + by) / 2] }, properties: { t: P.name, s: 11, a, p: VIA[P.class][3], z: VIA[P.class][2] } });
      }
    }
    return out;
  }
  class Calles extends deck.MVTLayer {
    getTileData(t) {
      // en Canarias se piden las teselas de las islas y se pintan en el recuadro, desplazadas como él
      const k = this.props.canarias ? 2 ** (t.index.z - 10) : 0;
      const index = { ...t.index, x: t.index.x - CANT[0] * k, y: t.index.y - CANT[1] * k };
      return super.getTileData({ ...t, index }).then(F => {
        const out = prepara(F, t.index.z), { x, y, z } = t.index, n = 2 ** z;
        // los rótulos van aparte, en grados y en la posición en la que se pinta la tesela (ver rotulos())
        // (los de la península no entran en el recuadro de Canarias, y los de Canarias solo van dentro de él)
        const dentro = ([lo, la]) => lo >= x0 && lo <= x1 && la >= y0 && la <= y1;
        ROT.set(this.id + z + '/' + x + '/' + y, { z, r: out.filter(f => f.geometry.type === 'Point').map(f => {
          const [lx, ly] = f.geometry.coordinates;
          return { ...f.properties, pos: [(x + lx) / n * 360 - 180, mLat((y + ly) / n)] };
        }).filter(r => dentro(r.pos) === !!this.props.canarias) });
        if (ROT.size > 400) ROT.delete(ROT.keys().next().value);
        pideRedraw();
        return out.filter(f => f.geometry.type !== 'Point');
      });
    }
  }
  Calles.layerName = 'Calles';
  Calles.defaultProps = { canarias: false };
  // Rótulos de las teselas cargadas (clave: capa + tesela). Se colocan todos juntos en cada fotograma, de más a menos
  // importante y sin que se pisen (los barrios primero, luego avenidas y calles), en una sola capa de texto.
  const ROT = new Map();
  let pendiente = false;
  const pideRedraw = () => { if (!pendiente) { pendiente = true; requestAnimationFrame(() => { pendiente = false; redraw(); }); } };
  function rotulos() {
    const vp = dk.getViewports()[0]; if (!vp) return [];
    const zt = Math.max(12, Math.min(14, Math.round(view.zoom))), W = vp.width, H = vp.height;
    let cand = [];
    for (const { z, r } of ROT.values()) if (z === zt) cand = cand.concat(r);
    cand = cand.filter(r => view.zoom >= r.z).sort((a, b) => b.p - a.p);
    const cajas = [], vistos = new Set(), out = [];
    for (const r of cand) {
      const [sx, sy] = vp.project(r.pos);
      if (sx < 0 || sy < 0 || sx > W || sy > H) continue;
      const k = r.t + Math.round(sx / 40) + ',' + Math.round(sy / 40); if (vistos.has(k)) continue;
      const w = r.t.length * r.s * .56 + 8, h = r.s + 6, a = (r.a || 0) * Math.PI / 180;
      const bw = (Math.abs(w * Math.cos(a)) + Math.abs(h * Math.sin(a))) / 2, bh = (Math.abs(w * Math.sin(a)) + Math.abs(h * Math.cos(a))) / 2;
      const c = [sx - bw, sy - bh, sx + bw, sy + bh];
      if (cajas.some(o => c[0] < o[2] && c[2] > o[0] && c[1] < o[3] && c[3] > o[1])) continue;
      cajas.push(c); vistos.add(k); out.push(r);
    }
    return out;
  }
  function callejero(url) {
    const linea = isDark() ? [20, 20, 20, 150] : [255, 255, 255, 190];
    const sub = p => p.data && enRecuadro(p.tile.boundingBox) === !!p.canarias ? new deck.GeoJsonLayer({ ...p, pickable: false,
      filled: false, stroked: true, getLineColor: linea, getLineWidth: f => f.properties.w, lineWidthUnits: 'pixels', lineCapRounded: true, lineJointRounded: true }) : null;
    const base = { data: url, minZoom: 12, maxZoom: 14, binary: false, maxRequests: 6, renderSubLayers: sub, pickable: false,
      loadOptions: { mvt: { layers: ['transportation', 'transportation_name', 'place'] } }, updateTriggers: { renderSubLayers: [isDark()] } };
    return [new Calles({ ...base, id: 'calles' }), new Calles({ ...base, id: 'calles-can', canarias: true, extent: [x0, y0, x1, y1] })];
  }
  function capaRotulos() {
    const tinta = hex(css('--ink') || '#111'), fondo = hex(css('--surface') || '#fff');
    return new deck.TextLayer({ id: 'rotulos', data: rotulos(), pickable: false, getPosition: r => r.pos, getText: r => r.t, getSize: r => r.s,
      getAngle: r => r.a || 0, getColor: r => r.s > 11 ? tinta : [...tinta, 210], fontFamily: 'IBM Plex Sans, system-ui, sans-serif', fontWeight: 600,
      characterSet: 'auto', fontSettings: { sdf: true }, outlineWidth: 3, outlineColor: [...fondo, 230], parameters: { depthCompare: 'always' } });
  }

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
    const conRot = conCalles() && typeof pideOFM() === 'string';
    if (conRot) L.push(...callejero(OFM));
    if (hover) {
      L.push(new deck.PathLayer({ id: 'hl', data: hover.polys, getPath: o => o.ring, getColor: hex(css('--ink') || '#111'), widthUnits: 'pixels', getWidth: 2 }));
    }
    if (conRot) L.push(capaRotulos());
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
    touchAction: 'pan-y',   // en el móvil, deslizar en vertical mueve la página; en horizontal y con dos dedos, el mapa
    views: new deck.MapView({ repeat: false }), layers: [], getCursor: ({ isHovering }) => isHovering ? 'pointer' : 'grab',
    onViewStateChange: ({ viewState }) => { view = viewState; loadVisible(); redraw(); return viewState; },
    onHover: info => { setHover(info); },
    onClick: info => { setHover(info, true); },
  });
  const attr = document.createElement('div');
  attr.className = 'calles-attr';
  attr.innerHTML = '<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> · © <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener">OpenMapTiles</a> · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>';
  attr.style.cssText = 'position:absolute;right:0;bottom:0;z-index:2;font:11px/1.4 var(--sans,system-ui);padding:2px 6px;background:var(--surface);color:var(--muted);opacity:.85;border-top-left-radius:4px';
  $('#map').appendChild(attr);
  let bCal = null;        // botón «Ver calles / Quitar calles» (se crea con los controles)
  function redraw() {
    attr.hidden = !conCalles();
    if (bCal) bCal.hidden = view.zoom < CALLE_Z - .5;
    dk.setProps({ layers: layers() });
  }

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
      get('sec/' + p + '.json').then(d => { const polys = decode(d); if (esCan(p)) aCan(polys); SEC[p] = { d, polys }; loading.delete(p); aseguraSec(p, st.y); redraw(); }).catch(() => loading.delete(p));
    }
  }

  // ---------- nombre real de cada candidatura (PSC, PSdeG, UPN, En Comú Podem...) en cada elección y municipio:
  // data/nombres/<elección>.json, de src/nombres.py. Sin fichero (el directo), el de la familia.
  const NOMB = {};
  let tipAbierta = null;   // la ficha a la vista, para rehacerla cuando lleguen los nombres
  const pideNombres = y => NOMB[y] !== undefined ? Promise.resolve() :
    (NOMB[y] = null, get('nombres/' + y + '.json').then(d => { NOMB[y] = d; }).catch(() => {}));
  const nomL = (f, y, mi) => {
    const N = NOMB[y], c = MUN.cod[mi];
    if (N) { const m = N.m[f.cod], p = N.p[f.cod], k = m && c in m ? m[c] : p && p[c.slice(0, 2)]; if (k) return N.n[k]; }
    return nomF(f, y);
  };
  pideNombres(st.y).then(() => { if (!tip.hidden && tipAbierta) tip.innerHTML = ficha(...tipAbierta); });
  const escH = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

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
    h += '<table class="t-bars">' + rows.map(r => `<tr><th${nomL(r.f, y, mi) !== nomF(r.f, y) ? ` title="${escH(nomF(r.f, y))}"` : ''}><span style="display:inline-block;max-width:150px;line-height:1.2;white-space:${nomL(r.f, y, mi).length > 16 ? 'normal' : 'nowrap'}">${escH(nomL(r.f, y, mi))}</span></th><td><span class="bar" style="width:${Math.max(2, r.v / max * 100)}%;background:${r.f.color}"></span></td><td class="n">${pct(r.v)}</td></tr>`).join('') + '</table>';
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
    tipAbierta = [d, o.i, isSec]; tip.innerHTML = ficha(d, o.i, isSec); tip.hidden = false;
    const W = $('#map').clientWidth, H = $('#map').clientHeight, tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = info.x + 14, y = info.y + 14;
    if (x + tw > W - 8) x = info.x - tw - 14; if (y + th > H - 8) y = Math.max(8, H - th - 8);
    if (narrow()) { tip.style.left = '8px'; tip.style.top = 'auto'; tip.style.bottom = '8px'; }
    else { tip.style.left = Math.max(8, x) + 'px'; tip.style.top = y + 'px'; tip.style.bottom = 'auto'; }
    if (!hover || hover.key !== id + o.i) { hover = { key: id + o.i, polys: all.filter(p => p.i === o.i) }; redraw(); }
  }

  // ---------- leyenda
  // elecciones sin resultados por sección (anteriores a 2004, municipales de 2007, directo): se avisa en la leyenda
  // nombre de una familia en una elección: antes de 1989 el PP era AP; antes de 2011, la izquierda abertzale era HB / EH
  const nomF = (f, y) => { const a = (META.alias || {})[f.cod] || [], yr = y.replace(/^\D/, '').slice(0, 4), m = a.find(([hasta]) => yr < hasta); return m ? m[1] : f.nombre; };
  const nomE = y => { const e = ELEC.find(e => e.cod === y); return e.nombre + (e.secciones === false ? ' (solo por municipio)' : ''); };
  function legend() {
    const el = $('#legend');
    if (st.v === 'gana') {
      const y = st.y, used = new Set(MUN[y + '_gana']);
      el.innerHTML = `<div class="lg-t">Partido más votado · ${nomE(y)}</div><div class="lg-sw">` +
        FAM.filter((f, k) => used.has(k)).map(f => `<span><b style="background:${f.color}"></b>${nomF(f, y)}</span>`).join('') +
        `</div><div class="lg-n">Más intenso cuanto mayor es su porcentaje de voto</div>`;
      return;
    }
    let lo, hi, cols, fmt, name;
    if (st.v === 'party') {
      const f = FAM[FCOD.indexOf(st.party)], mx = domParty(), bg = BG();
      cols = [0, .25, .5, .75, 1].map(t => `rgb(${mix(bg, f.rgb, .06 + .94 * t)})`); lo = 0; hi = mx; fmt = pct; name = 'Voto a ' + nomF(f, st.y) + ' · ' + nomE(st.y);
    } else {
      const V = VARS[st.v]; cols = rampa(V.ramp).map(c => `rgb(${c})`); [lo, hi] = st.v === 'part' ? PARTDOM[tipoDe(st.y)] : V.dom; fmt = V.fmt;
      name = V.name + (st.v === 'part' ? ' · ' + nomE(st.y) : '');
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
    try { await Promise.all([asegura(y), pideNombres(y)]); } finally { selE.disabled = false; }
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
    if (i != null) abre(i);
  });
  let actual = null;        // último municipio abierto (para el código de «Insertar»)
  function abre(i) {
    actual = i;
    const big = (MUN.poblacion[i] || 0) > 200000;
    fly({ longitude: MUN.c[i][0], latitude: MUN.c[i][1], zoom: big ? 10.2 : 11 });
    const all = MUNP.filter(p => p.i === i); hover = { key: 'mun' + i, polys: all }; redraw();
  }
  $('#home').onclick = () => fly(HOME());
  bCal = document.createElement('button');
  bCal.type = 'button'; bCal.id = 'calles'; bCal.textContent = 'Calles';
  bCal.title = 'Muestra las calles y los nombres de los barrios al acercarte';
  // dentro del mapa, arriba a la izquierda, y solo cuando ya se está cerca (no quita sitio a los controles en el móvil)
  bCal.style.cssText = 'position:absolute;left:8px;top:8px;z-index:2;font:600 12px/1 var(--sans,system-ui);padding:6px 9px;border-radius:6px;cursor:pointer;background:var(--surface);color:var(--ink);border:1px solid var(--line);box-shadow:0 1px 4px rgba(0,0,0,.12)';
  const marcaCal = () => { bCal.setAttribute('aria-pressed', calles); bCal.textContent = calles ? 'Quitar calles' : 'Ver calles'; };
  bCal.onclick = () => {
    calles = !calles; marcaCal(); redraw();
    try { localStorage.setItem('mapa-calles', calles ? 'si' : 'no'); } catch (e) { /* sin almacenamiento */ }
  };
  marcaCal(); $('#map').appendChild(bCal);
  function fly(to) {
    view = { ...view, ...to, transitionDuration: 'auto', transitionInterpolator: new deck.FlyToInterpolator({ speed: 1.6 }) };
    dk.setProps({ initialViewState: view });
  }
  window.addEventListener('resize', () => redraw());
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { legend(); redraw(); });
  sync();
  // Con la leyenda ya pintada, el mapa puede haber cambiado de alto (en el insertable estrecho va debajo): se reencaja.
  const h0 = HOME(); if (h0.zoom !== view.zoom) { view = { ...view, ...h0 }; dk.setProps({ initialViewState: view }); }

  // ---------- «Insertar en tu web»: código <iframe> de insertar/ con la elección y el municipio elegidos
  const bIns = $('#insertar');
  if (bIns) {
    const caja = $('#insertar-caja'), code = $('#insertar-codigo'), bCop = $('#insertar-copiar');
    bIns.onclick = () => {
      const p = new URLSearchParams({ e: st.y }); if (actual != null) p.set('m', MUN.cod[actual]);
      code.value = `<iframe src="https://mapaelectoral.es/insertar/?${p}" width="100%" height="620" style="border:0;max-width:100%" loading="lazy" title="Mapa electoral de España por municipio y sección censal"></iframe>`;
      bCop.textContent = 'Copiar'; caja.hidden = false; code.focus(); code.select();
    };
    bCop.onclick = async () => {
      code.select();
      try { await navigator.clipboard.writeText(code.value); } catch (e) { document.execCommand('copy'); }
      bCop.textContent = 'Copiado';
    };
    $('#insertar-cerrar').onclick = () => { caja.hidden = true; bIns.focus(); };
  }

  // ---------- enlace a un municipio (?m=<código INE>&e=<elección>), el que usan las piezas del Atlas
  const Q = new URLSearchParams(location.search), qm = MUN.cod.indexOf(Q.get('m'));
  if (qm >= 0) {
    const qe = Q.get('e');
    if (qe && qe !== st.y && ELEC.some(e => e.cod === qe)) { selE.value = qe; await elige(qe); }
    $('#q').value = `${MUN.nombre[qm]} (${MUN.provs[MUN.prov[qm]] || ''})`;
    abre(qm);
    tipAbierta = [MUN, qm, false]; tip.innerHTML = ficha(MUN, qm, false); tip.hidden = false;
    tip.style.left = '8px'; tip.style.top = narrow() ? 'auto' : '8px'; tip.style.bottom = narrow() ? '8px' : 'auto';
  }


  // ---------- directo (noche electoral): JSON normalizado (ver actualizar_29n.py) cada minuto
  // Una ruta relativa (?directo=data/simulacro.json) se busca junto a los datos, como el resto: así el ensayo funciona igual
  // en la portada, en generales-2026/ y en el mapa insertado (insertar/).
  const DIR0 = new URLSearchParams(location.search).get('directo') || (META.directo && META.directo.url);
  const DIRURL = DIR0 && (/^(https?:)?\/\//.test(DIR0) ? DIR0 : new URL(DIR0.replace(/^\.?\//, ''), RAIZ || location.href).href);
  const REG = (META.reglas || []).map(([c, p]) => [c, new RegExp(p)]);
  // Como familia() de partidos.py: se prueba con las siglas tal cual y sin puntos (U.P.N. es UPN, con el PP).
  const famDe = s => { const a = (s || '').toUpperCase().trim(); for (const x of [a, a.replace(/\./g, '')]) for (const [c, r] of REG) if (r.test(x)) return c; return 'OTROS'; };
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
    // Si el mapa sigue en la vista inicial, se reencaja después de mostrar el recuadro, que le quita alto
    const h0 = HOME(), enCasa = Math.abs(view.zoom - h0.zoom) < .01 && Math.abs(view.longitude - h0.longitude) < 1e-6;
    const box = $('#directo'); box.hidden = false;
    const h1 = HOME(); if (enCasa && h1.zoom !== view.zoom) { view = { ...view, ...h1 }; dk.setProps({ initialViewState: view }); }
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
