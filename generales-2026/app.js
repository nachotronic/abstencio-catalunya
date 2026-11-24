// Mapa de las generales: municipios para toda España y secciones censales al acercarse.
// Datos en data/: meta.json, municipios-ligero.json (municipios.json sin las generales anteriores, src/ligero.py), provincias.json, resumen.json y sec/<prov>.json (generales).
// Municipales y europeas, aparte: e/<elección>.json y sec/<prov>_<elección>.json, que se cargan al elegirlas.
(async function () {
  const $ = s => document.querySelector(s);
  // Ruta de los datos relativa a este script, para que la página funcione también como portada en la raíz.
  const RAIZ = ((document.currentScript && document.currentScript.src) || '').replace(/[^/]*$/, '');
  const get = f => fetch(RAIZ + 'data/' + f).then(r => { if (!r.ok) throw new Error(f); return r.json(); });
  // Día de elecciones (hay directo): la portada de la jornada se monta en cuanto llega meta.json, sin esperar al resto de
  // datos, para que no se vean las encuestas ni los bloques viejos mientras carga el mapa.
  let jornadaHecha = false;
  const pMeta = get('meta.json');
  pMeta.then(m => { if (new URLSearchParams(location.search).get('directo') || (m.directo && m.directo.url)) jornada(); }).catch(() => {});
  // Barrio de cada sección de las grandes ciudades (src/territorios.py): se pide al acercarse a las secciones
  let BAR = null, BARP = null;
  const pideBar = () => BARP || (BARP = get('barrios.json').then(j => { BAR = j; }).catch(() => { BAR = { r: [], s: {} }; }));
  const [META, MUN, PROV, RES] = await Promise.all([pMeta, get('municipios-ligero.json'), get('provincias.json'), get('resumen.json')]);
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
  let SECC = null, VERD = 0; const SECCV = {};
  let AGREG = '', AGD = null, AGMANO = false, HAG = null, HAGP = null; const AGUMBRAL = 0.10, HAGN = {};   // mapa por provincias ('PR') o comunidades ('CM') del directo (ver agregados)   // secciones del directo (ver seccDirecto) y versión de los datos del directo
  const loading = new Set();

  // ---------- estado
  const ELEC = META.elecciones;
  const tipoDe = y => (ELEC.find(e => e.cod === y) || {}).tipo || 'generales';
  const st = { y: ELEC.filter(e => tipoDe(e.cod) === 'generales').pop().cod, v: 'gana', party: 'PP' };
  // participación: la escala depende del tipo de elección (en europeas vota mucha menos gente)
  const PARTDOM = { generales: [.55, .85], municipales: [.45, .85], europeas: [.30, .75] };
  // el 29N antes del escrutinio pinta la participación de un avance de Interior, con su propia escala (ver aplica)
  const domPart = y => (ELEC.find(e => e.cod === y) || {}).dom || PARTDOM[tipoDe(y)];
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
  // empate a votos entre los dos primeros (_gana = -2, src/mapa_empates.py): gris oscuro, distinto del «sin dato»
  const EMPATE = -2, EMP = () => hex(css('--empate') || '#8a8486');
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
      if (g === EMPATE) return EMP();
      if (g == null || g < 0) return NODATA();
      const f = FAM[g], b = f.cod === 'SUMAR' && d[st.y + '_SUMAR_B'] ? d[st.y + '_SUMAR_B'][i] : null;
      const s = b ? Math.max(d[st.y + '_SUMAR_A'][i] || 0, b) : d[st.y + '_' + f.cod][i] || 0;   // dos listas: la de la más votada
      return mix(BG(), f.rgb, Math.max(.28, Math.min(1, (s - .15) / .35)));
    }
    const v = value(d, i);
    if (v == null) return NODATA();
    if (st.v === 'party') {
      const f = FAM[FCOD.indexOf(st.party)];
      return mix(BG(), f.rgb, Math.min(1, .06 + .94 * v / (partyMax[st.y + '_' + st.party] || domParty())));
    }
    const V = VARS[st.v], dom = st.v === 'part' ? domPart(st.y) : V.dom, t = (v - dom[0]) / (dom[1] - dom[0]);
    return ramp(V.ramp, t);
  }

  // ---------- mapa
  const narrow = () => window.innerWidth < 760;
  // Vista inicial: encaja la península, Baleares y el recuadro de Canarias con un 3 % de margen. Pantalla ancha:
  // lon −9,3 a 5,6 y lat 35,3 a 43,8; móvil: lon −9,3 a 4,4 y lat 33,2 a 43,8. El alto va en grados Mercator, no de latitud.
  // ?b=<lon0>,<lat0>,<lon1>,<lat1>: vista inicial encajada en esa caja (la usan las piezas «El mapa electoral de…»
  // para abrir el mapa insertado sobre una comunidad). Solo coordenadas de la península y Baleares, sin el recuadro de Canarias.
  const CAJA = (() => {
    const b = (new URLSearchParams(location.search).get('b') || '').split(',').map(Number);
    if (b.length !== 4 || !b.every(Number.isFinite) || b[0] >= b[2] || b[1] >= b[3]) return null;
    const mer = la => Math.log(Math.tan(Math.PI / 4 + la * Math.PI / 360)) * 180 / Math.PI;
    const ym = (mer(b[1]) + mer(b[3])) / 2;
    return [b[2] - b[0], mer(b[3]) - mer(b[1]), (b[0] + b[2]) / 2, Math.atan(Math.sinh(ym * Math.PI / 180)) * 180 / Math.PI];
  })();
  const HOME = () => {
    const el = $('#map'), W = el.clientWidth || 800, H = el.clientHeight || 600;
    const [ancho, alto, longitude, latitude] = CAJA || (ESTRECHO ? [13.7, 13.6, -2.49, 38.7] : [15, 11.1, -1.87, 39.68]);
    const z = Math.min(Math.log2(W / (512 * ancho * 1.03 / 360)), Math.log2(H / (512 * alto * 1.03 / 360)));
    return { longitude, latitude, zoom: Math.round(z * 100) / 100, pitch: 0, bearing: 0 };
  };
  let view = HOME();
  const [[x0, y0], [x1, y1]] = [canT([-18.4 + CDX, 27.4 + CDY]), canT([-13.2 + CDX, 29.6 + CDY])];
  const CANFRAME = [{ path: [[x0, y0], [x0, y1], [x1, y1], [x1, y0], [x0, y0]] }];
  let hover = null;
  let marca = null;       // dirección buscada: punto (y la calle entera si no hay número)

  function secVisible() { const v = view.zoom >= 7.3; if (v && !BARP) pideBar(); return v; }
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
      getAngle: r => r.a || 0, getColor: r => r.s > 11 ? tinta : [...tinta, 220], ...LETRA, outlineColor: [...fondo, 245] });
  }

  // Nombres de municipio (desde la vista de España): de más a menos habitantes, con un mínimo que baja con el zoom, sin que se pisen
  const ORDM = MUN.nombre.map((n, i) => i).sort((a, b) => (MUN.poblacion[b] || 0) - (MUN.poblacion[a] || 0));
  const MINPOB = z => z < 6 ? 150000 : z < 7 ? 50000 : z < 8 ? 15000 : z < 9 ? 5000 : z < 10 ? 1500 : z < 11 ? 300 : 0;
  // Nombres más legibles al acercarse (Nacho, 24-11: «cuando acercas el zoom los nombres se ven regular»): crecen hasta 3 px
  // desde el zoom 8, el atlas de letras se dibuja a más resolución y el halo es más ancho y opaco, para que se lean sobre
  // cualquier color (también los nombres de calles y barrios del callejero)
  const MASZ = z => Math.max(0, Math.min(3, (z - 8) * 1.2));
  const LETRA = { fontFamily: 'IBM Plex Sans, system-ui, sans-serif', fontWeight: 600, characterSet: 'auto',
    fontSettings: { sdf: true, fontSize: 96, buffer: 16, radius: 32, cutoff: .25 }, outlineWidth: 14, parameters: { depthCompare: 'always' } };
  function capaMunicipios() {
    let vp = null; const out = [];
    try { vp = dk.getViewports()[0]; } catch (e) { pideRedraw(); }   // la primera vez, antes de que deck.gl tenga el mapa montado
    if (vp && Math.abs(vp.width - $('#map').clientWidth) > 2) pideRedraw();   // deck.gl aún no se ha ajustado al tamaño del mapa
    if (vp) {
      const W = vp.width, H = vp.height, min = MINPOB(view.zoom), cajas = [];
      for (const i of ORDM) {
        if ((MUN.poblacion[i] || 0) < min) break;
        const q = MUN.c[i]; if (!q) continue;
        const [sx, sy] = vp.project(q);
        if (sx < 0 || sy < 0 || sx > W || sy > H) continue;
        const pob = MUN.poblacion[i] || 0, grande = pob >= 100000, s = (grande ? 13 : pob >= 20000 ? 11.5 : 10.5) + MASZ(view.zoom);
        const w = MUN.nombre[i].length * s * .58 + 10, h = s + 7, c = [sx - w / 2, sy - h / 2, sx + w / 2, sy + h / 2];
        if (cajas.some(o => c[0] < o[2] && c[2] > o[0] && c[1] < o[3] && c[3] > o[1])) continue;
        cajas.push(c); out.push({ t: MUN.nombre[i], p: q, s, g: grande });
        if (out.length > 300) break;
      }
    }
    const tinta = hex(css('--ink') || '#111'), fondo = hex(css('--surface') || '#fff');
    return new deck.TextLayer({ id: 'munlab', data: out, pickable: false, getPosition: o => o.p, getText: o => o.t, getSize: o => o.s,
      getColor: o => o.g ? tinta : [...tinta, 235], ...LETRA, outlineColor: [...fondo, 255] });
  }

  function layers() {
    const L = [];
    const trig = [st.y, st.v, st.party, document.documentElement.dataset.theme || '', VERD];   // VERD: datos nuevos del directo
    L.push(new deck.SolidPolygonLayer({
      id: 'mun', data: MUNP, getPolygon: o => o.polygon, getFillColor: o => color(MUN, o.i),
      pickable: true, updateTriggers: { getFillColor: trig },
    }));
    const conAg = agActivo();
    if (conAg) L.push(new deck.SolidPolygonLayer({   // provincias o comunidades del directo, encima de los municipios
      id: 'agreg', data: PROVP, getPolygon: o => o.polygon, getFillColor: o => agColor(PROV.cod[o.i]),
      pickable: true, updateTriggers: { getFillColor: [...trig, AGREG] },
    }));
    if (!conAg && secVisible()) {
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
    if (secVisible()) {   // con las secciones a la vista, el límite de cada municipio en oscuro para que se distinga de ellas
      L.push(new deck.PathLayer({ id: 'munline', data: MUNP, getPath: o => o.ring, getColor: [...hex(css('--ink') || '#111'), view.zoom >= 10 ? 170 : 110],
        widthUnits: 'pixels', getWidth: view.zoom >= 10 ? 1.6 : 1, updateTriggers: { getColor: [document.documentElement.dataset.theme || '', view.zoom >= 10] } }));
    } else if (view.zoom >= 6.6) {
      L.push(new deck.PathLayer({ id: 'munline', data: MUNP, getPath: o => o.ring, getColor: [...line, 150], widthUnits: 'pixels', getWidth: view.zoom >= 8.5 ? .9 : .4 }));
    }
    L.push(new deck.PathLayer({ id: 'prov', data: PROVP, getPath: o => o.ring, getColor: [...line, 255], widthUnits: 'pixels', getWidth: 1.2, widthMinPixels: 1 }));
    L.push(new deck.PathLayer({ id: 'canframe', data: CANFRAME, getPath: o => o.path, getColor: hex(css('--muted') || '#888'), widthUnits: 'pixels', getWidth: 1 }));
    const conRot = conCalles() && typeof pideOFM() === 'string';
    if (conRot) L.push(...callejero(OFM));
    if (hover) {
      L.push(new deck.PathLayer({ id: 'hl', data: hover.polys, getPath: o => o.ring, getColor: hex(css('--ink') || '#111'), widthUnits: 'pixels', getWidth: 2 }));
    }
    if (marca) {
      if (marca.via) L.push(new deck.PathLayer({ id: 'via', data: [marca.via], getPath: o => o, getColor: [...hex(css('--ink') || '#111'), 200], widthUnits: 'pixels', getWidth: 4 }));
      L.push(new deck.ScatterplotLayer({ id: 'marca', data: [marca.p], getPosition: o => o, getRadius: 7, radiusUnits: 'pixels', stroked: true,
        getFillColor: hex(css('--ink') || '#111'), getLineColor: hex(css('--surface') || '#fff'), lineWidthUnits: 'pixels', getLineWidth: 2 }));
    }
    if (conRot) L.push(capaRotulos());
    if (!(conRot && view.zoom >= 12)) L.push(capaMunicipios());   // con el callejero, los nombres los pone OpenFreeMap
    return L;
  }

  const dk = new deck.Deck({
    parent: $('#map'), initialViewState: view, controller: { dragRotate: false, touchRotate: false, scrollZoom: { smooth: true } },
    touchAction: 'pan-y',   // en el móvil, deslizar en vertical mueve la página; en horizontal y con dos dedos, el mapa
    views: new deck.MapView({ repeat: false }), layers: [], getCursor: ({ isHovering }) => isHovering ? 'pointer' : 'grab',
    onViewStateChange: ({ viewState }) => { view = viewState; loadVisible(); redraw(); return viewState; },
    onHover: info => { resalta(info); },   // al pasar el ratón solo se resalta el contorno; la ficha sale al hacer clic
    onClick: info => { setHover(info, true); },
  });
  const attr = document.createElement('div');
  attr.className = 'calles-attr';
  attr.innerHTML = '<a href="https://openfreemap.org" target="_blank" rel="noopener">OpenFreeMap</a> · © <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener">OpenMapTiles</a> · © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>' +
    '<span class="cc" hidden> · Direcciones: <a href="https://www.cartociudad.es/" target="_blank" rel="noopener">CartoCiudad (IGN)</a></span>';
  attr.style.cssText = 'position:absolute;right:0;bottom:0;z-index:2;font:11px/1.4 var(--sans,system-ui);padding:2px 6px;background:var(--surface);color:var(--muted);opacity:.85;border-top-left-radius:4px';
  $('#map').appendChild(attr);
  let bCal = null;        // botón «Ver calles / Quitar calles» (se crea con los controles)
  function redraw() {
    attr.hidden = !conCalles() && !marca;
    attr.querySelector('.cc').hidden = !marca;
    if (bCal) bCal.hidden = view.zoom < CALLE_Z - .5;
    dk.setProps({ layers: layers() });
  }

  // elecciones que viven en ficheros aparte: columnas que se añaden a MUN y a cada provincia al elegirlas
  // (municipios-ligero.json solo trae la última generales; las de 2004-2019 también llegan de e/<elección>.json, ver src/ligero.py)
  const aparte = y => (ELEC.find(e => e.cod === y) || {}).aparte;
  const pedido = {}, fuera = new Set(META.elecciones.filter(e => !MUN[e.cod + '_part']).map(e => e.cod));
  // Si la descarga falla (GitHub Pages devuelve a veces un 503, o el móvil pierde la conexión), se reintenta dos veces
  // y no se guarda la promesa fallida: al volver a elegir el año se pide otra vez.
  const espera = ms => new Promise(r => setTimeout(r, ms));
  const getR = async (f, n = 3) => { for (let k = 0; ; k++) { try { return await get(f); } catch (e) { if (k >= n - 1) throw e; await espera(800 * 2 ** k); } } };
  function asegura(y) {
    if (!fuera.has(y) || MUN[y + '_part']) return Promise.resolve();
    return pedido[y] || (pedido[y] = getR('e/' + y + '.json').then(d => { Object.assign(MUN, d); }).catch(e => { delete pedido[y]; throw e; }));
  }
  function aseguraSec(p, y) {
    if (SECC && SEC[p] && META.directo && (y === META.directo.eleccion || y.startsWith(META.directo.eleccion + 'a'))) return seccDirecto(p);
    const e = ELEC.find(e => e.cod === y);
    if (!e || !e.aparte || !e.secciones || !SEC[p] || SEC[p].d[y + '_part']) return;
    const k = p + '_' + y; if (pedido[k]) return;
    pedido[k] = getR('sec/' + k + '.json').then(d => { Object.assign(SEC[p].d, d); redraw(); }).catch(() => delete pedido[k]);
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
  pideNombres(st.y).then(() => { if (!tip.hidden && tipAbierta) tip.innerHTML = CERRAR + ficha(...tipAbierta); });
  const escH = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');

  // ---------- ficha (tooltip)
  const tip = $('#tip'), CERRAR = '<button class="t-x" type="button" aria-label="Cerrar">×</button>';
  tip.addEventListener('click', e => { if (e.target.closest('.t-x')) { tip.hidden = true; hover = null; redraw(); } });
  // 2011 y abril de 2019 (Comunitat Valenciana), 2015 y noviembre de 2019: el espacio de Sumar / Podemos / IU fue en dos
  // listas. <elección>_SUMAR_B es el voto de la segunda (src/mapa_listas_separadas.py); la ficha enseña las dos filas.
  const SEGUNDA = {
    '2011_11': [/Compromís/, () => 'Compromís-Q'],
    '2015_12': [/Unidad Popular|Unitat Popular|EUPV|Izquierda Unida|Esquerra Unida|Esquerda Unida|^IU$/, () => 'IU-Unidad Popular'],
    '2019_04': [/Compromís/, () => 'Compromís'],
    '2019_11': [/Más País|Més País|Compromís/, p => ['03', '12', '46'].includes(p) ? 'Més Compromís' : 'Más País'],
  };
  function dosListas(r, d, i, y, mi) {
    const b = d[y + '_SUMAR_B'] ? d[y + '_SUMAR_B'][i] : null, a = d[y + '_SUMAR_A'] ? d[y + '_SUMAR_A'][i] : null;
    if (!b || a == null || r.v == null || !SEGUNDA[y]) return [r];
    const [re, porDefecto] = SEGUNDA[y], partes = r.n.split(' + '), nb = partes.filter(x => re.test(x));
    const na = partes.length > 1 && nb.length === 1 ? partes.filter(x => !re.test(x)).join(' + ') : r.n;
    const A = { f: r.f, v: a, n: na }, B = { f: r.f, v: b, n: nb.length === 1 && partes.length > 1 ? nb[0] : porDefecto(MUN.cod[mi].slice(0, 2)), b: true, par: A };
    // A y B vienen ya de los votos (src/mapa_listas_separadas.py): restar dos redondeos daría 0,1 puntos de error
    A.a = B;   // cada fila sabe cuál es la otra lista, para saber cuál de las dos es la más votada
    return [A, B];
  }
  // avances del 23J por municipio ([% a las 14.00, % a las 18.00] del censo), de data/censo/avances_participacion.csv;
  // se cargan al llegar el primer avance del 29N, para comparar en la ficha
  let AV23 = null;
  // El 29N, una fila por partido con su barra de ahora y, debajo, la de 2023 (más fina y clara): compacto para el móvil
  function compara(d, i, y) {
    const v = (yy, f) => d[yy + '_' + f.cod] ? d[yy + '_' + f.cod][i] : null, ya = y ? [y, '2023_07'] : ['2023_07'];
    const rows = FAM.map(f => ({ f, a: y ? v(y, f) : null, b: v('2023_07', f) }))
      .filter(r => (r.a || 0) > .005 || (r.b || 0) > .005).sort((p, q) => ((q.a ?? q.b) || 0) - ((p.a ?? p.b) || 0)).slice(0, 7);
    if (!rows.length) return '<p class="t-na">Sin resultados.</p>';
    const max = Math.max(...rows.map(r => Math.max(r.a || 0, r.b || 0)));
    const bar = (x, col, alto, op) => `<span style="display:block;height:${alto}px;margin:1px 0;border-radius:0 3px 3px 0;width:${x ? Math.max(1.5, x / max * 100) : 0}%;background:${col};opacity:${op}"></span>`;
    return (y ? '<p class="t-na" style="margin:4px 0 2px">Barra gruesa, 29N; fina, 2023</p>' : '')
      + '<table class="t-bars">' + rows.map(r => `<tr><th><span style="display:inline-block;max-width:120px;line-height:1.15;white-space:normal">${escH(nomL(r.f, ya[0], i))}</span></th>`
      + `<td>${y ? bar(r.a, r.f.color, 9, 1) : ''}${bar(r.b, r.f.color, y ? 4 : 9, y ? .45 : 1)}</td>`
      + `<td class="n" style="line-height:1.1">${y ? `${pct(r.a)}<br><span class="mut" style="font-size:11px">${pct(r.b)}</span>` : pct(r.b)}</td></tr>`).join('') + '</table>';
  }
  function ficha(d, i, isSec, yo) {
    const eAv = !yo && !isSec && ELEC.find(x => x.cod === st.y && x.avance);
    if (eAv) {   // un avance del 29N: participación a esa hora, la del 23J a la misma hora y, debajo, el resultado de 2023
      const k = /a2$/.test(eAv.cod) ? 1 : 0, ahora = d[eAv.cod + '_part'] ? d[eAv.cod + '_part'][i] : null;
      const antes = AV23 && AV23[MUN.cod[i]] ? AV23[MUN.cod[i]][k] / 100 : null, hora = k ? '18.00' : '14.00';
      const dif = ahora != null && antes != null ? (ahora - antes) * 100 : null;
      return `<div class="t-h">${MUN.nombre[i]}</div><div class="t-s">${MUN.provs[MUN.prov[i]] || ''} · ${eAv.nombre}</div>`
        + `<table class="t-bars" style="font-size:13px;text-align:center"><tr class="mut"><td>Ahora</td><td>2023, ${hora} h</td><td>Diferencia, puntos</td></tr>`
        + `<tr style="font:700 17px var(--sans)"><td>${ahora != null ? pct(ahora) : '–'}</td><td>${pct(antes)}</td><td>${dif != null ? (dif > 0 ? '+' : dif < 0 ? '−' : '') + Math.abs(dif).toFixed(1).replace('.', ',') : '–'}</td></tr></table>`
        + '<div class="t-s" style="margin-top:8px">Resultado de 2023</div>' + compara(d, i, null);
    }
    const y = yo || st.y, mi = isSec ? MUN.cod.indexOf(d.cod[i].slice(0, 5)) : i;
    const rows = FAM.map((f, k) => ({ f, v: d[y + '_' + f.cod] ? d[y + '_' + f.cod][i] : null, n: nomL(f, y, mi) }))
      .flatMap(r => r.f.cod === 'SUMAR' ? dosListas(r, d, i, y, mi) : [r])
      .filter(r => r.v != null && r.v > 0.005).sort((a, b) => b.v - a.v).slice(0, 6);
    // los porcentajes van redondeados a tres decimales: si el más votado (que se calcula con los votos) empata en la
    // primera fila, va primero (Amurrio 2015: PNV 1.686 votos, Podemos 1.685)
    const g = d[y + '_gana'] ? d[y + '_gana'][i] : -1, w = rows.findIndex(r => r.f === FAM[g] && !(r.a && r.a.v > r.v) && !(r.b && r.par.v > r.v));
    if (w > 0 && rows[0].v - rows[w].v < .0015) rows.unshift(rows.splice(w, 1)[0]);
    const e = ELEC.find(x => x.cod === y).nombre;
    const title = isSec ? `${MUN.nombre[mi]} · sección ${d.cod[i].slice(5, 7)}-${d.cod[i].slice(7)}` : MUN.nombre[i];
    const sub = isSec ? MUN.provs[MUN.prov[mi]] : MUN.provs[MUN.prov[i]];
    const max = rows.length ? rows[0].v : 1;
    let h = `<div class="t-h">${title}</div><div class="t-s">${sub || ''} · ${e}</div>`;
    const vivo = !yo && !isSec && META.directo && y === META.directo.eleccion && d['2023_07_part'];
    if (vivo) {
      const part = d[y + '_part'] ? d[y + '_part'][i] : null, esc = d[y + '_esc'] ? d[y + '_esc'][i] : null;
      return h + compara(d, i, y) + `<dl class="t-kv">${esc != null ? `<dt>Escrutado</dt><dd>${pct(esc)}</dd>` : ''}`
        + `<dt>Participación</dt><dd>${pct(part)} <span class="mut" style="font-size:11px">(2023: ${pct(d['2023_07_part'][i])})</span></dd>`
        + `<dt>Habitantes</dt><dd>${num(d.poblacion[i])}</dd></dl>`;
    }
    if (g === EMPATE) h += '<p class="t-na">Empate: los dos primeros tuvieron los mismos votos.</p>';
    if (!rows.length) h += `<p class="t-na">Sin resultados para esta elección con estos límites${isSec ? ' de sección' : ''}.</p>`;
    h += '<table class="t-bars">' + rows.map(r => `<tr><th${r.n !== nomF(r.f, y) ? ` title="${escH(nomF(r.f, y))}"` : ''}><span style="display:inline-block;max-width:150px;line-height:1.2;white-space:${r.n.length > 16 ? 'normal' : 'nowrap'}">${escH(r.n)}</span></th><td><span class="bar" style="width:${Math.max(2, r.v / max * 100)}%;background:${r.f.color}"></span></td><td class="n">${pct(r.v)}</td></tr>`).join('') + '</table>';
    if (d[y + '_SUMAR_B'] && d[y + '_SUMAR_B'][i] && SEGUNDA[y]) h +=   // aunque la segunda lista no quepa entre las seis filas
      '<p class="t-na">En esta elección el espacio de Sumar / Podemos / IU fue en dos listas: van por separado, y el más votado se calcula lista a lista.</p>';
    if (REPUBLICA(y)) {
      const fus = !isSec && d[y + '_fus'] ? d[y + '_fus'][i] : null;
      h += `<p class="t-na">Listas abiertas: peso de cada bloque en los votos a candidatos.${fus ? ' Suma los municipios de entonces: ' + escH(fus) + '.' : ''}</p>`;
    }
    const part = d[y + '_part'] ? d[y + '_part'][i] : null;
    const esc = d[y + '_esc'] ? d[y + '_esc'][i] : null;
    h += `<dl class="t-kv">${esc != null ? `<dt>Escrutado</dt><dd>${pct(esc)}</dd>` : ''}<dt>Participación</dt><dd>${pct(part)}</dd>
      <dt>Renta por u. de consumo</dt><dd>${eur(d.renta_uc[i])}</dd>
      <dt>En riesgo de pobreza</dt><dd>${pct(d.pobreza[i])}</dd>
      <dt>Edad media</dt><dd>${VARS.edad_media.fmt(d.edad_media[i])}</dd>
      <dt>Población extranjera</dt><dd>${pct(d.extranjeros[i])}</dd>
      <dt>Habitantes</dt><dd>${num(d.poblacion[i])}</dd></dl>`;
    const b = isSec && BAR ? BAR.r[BAR.s[d.cod[i]]] : null;
    if (b) h += `<p class="t-bar"><a href="${new URL('../' + b[1], RAIZ || location.href).href}">Ver el barrio: ${escH(b[0])} →</a></p>`;
    return h;
  }
  function resalta(info) {
    if (!tip.hidden) return;   // con una ficha abierta se mantiene su contorno
    const o = info.object, id = o && info.layer.id;
    if (!o) { if (hover) { hover = null; redraw(); } return; }
    if (id === 'agreg') { const k = agKey(o); if (!hover || hover.key !== 'agreg' + k) { hover = { key: 'agreg' + k, polys: PROVP.filter(p => agKey(p) === k) }; redraw(); } return; }
    const all = id.startsWith('sec') ? SEC[id.slice(3)].polys : MUNP;
    if (!hover || hover.key !== id + o.i) { hover = { key: id + o.i, polys: all.filter(p => p.i === o.i) }; redraw(); }
  }
  function setHover(info, pin) {
    const o = info.object;
    if (!o) { tip.hidden = true; hover = null; redraw(); return; }   // clic fuera: se cierra la ficha
    const id = info.layer.id, isSec = id.startsWith('sec');
    if (id === 'agreg') {   // ficha de la provincia o comunidad, con las cifras de Interior de ese nivel
      const k = agKey(o); tipAbierta = null; tip.innerHTML = CERRAR + agFicha(k); tip.hidden = false; colocaTip(info);
      if (!hover || hover.key !== 'agreg' + k) { hover = { key: 'agreg' + k, polys: PROVP.filter(p => agKey(p) === k) }; redraw(); }
      return;
    }
    const d = isSec ? SEC[id.slice(3)].d : MUN, all = isSec ? SEC[id.slice(3)].polys : MUNP;
    tipAbierta = [d, o.i, isSec]; tip.innerHTML = CERRAR + ficha(d, o.i, isSec); tip.hidden = false;
    colocaTip(info);
    if (!hover || hover.key !== id + o.i) { hover = { key: id + o.i, polys: all.filter(p => p.i === o.i) }; redraw(); }
  }
  function colocaTip(info) {
    const W = $('#map').clientWidth, H = $('#map').clientHeight, tw = tip.offsetWidth, th = tip.offsetHeight;
    let x = info.x + 14, y = info.y + 14;
    if (x + tw > W - 8) x = info.x - tw - 14; if (y + th > H - 8) y = Math.max(8, H - th - 8);
    if (narrow()) { tip.style.left = '8px'; tip.style.top = 'auto'; tip.style.bottom = '8px'; }
    else { tip.style.left = Math.max(8, x) + 'px'; tip.style.top = y + 'px'; tip.style.bottom = 'auto'; }
  }

  // ---------- leyenda
  // elecciones sin resultados por sección (anteriores a 2004, municipales de 2007, directo): se avisa en la leyenda
  // nombre de una familia en una elección: antes de 1989 el PP era AP; antes de 2011, la izquierda abertzale era HB / EH
  // el 29N, la familia de Sumar es el Frente Amplio (Podemos va aparte, con su propia familia): META.directo.nombres
  const nomF = (f, y) => { const dn = (META.directo || {}).nombres; if (dn && dn[f.cod] && y.startsWith((META.directo || {}).eleccion || '-')) return dn[f.cod]; const a = (META.alias || {})[f.cod] || [], yr = y.replace(/^\D/, '').slice(0, 4), m = a.find(([hasta]) => yr < hasta); return m ? m[1] : f.nombre; };
  // Segunda República (1933 y 1936): se votaba a candidatos en listas abiertas, con varios votos por elector
  const REPUBLICA = y => /^19[23]\d_/.test(y);
  const nomE = y => { const e = ELEC.find(e => e.cod === y); return e.nombre + (e.secciones === false ? ' (solo por municipio)' : ''); };
  function legend() {
    const el = $('#legend');
    if (st.v === 'gana') {
      const y = st.y, ag = agActivo(), used = new Set(ag ? Object.values(agDatos()[AGREG]).map(o => o.gana) : MUN[y + '_gana']);
      const dir = META.directo && y === META.directo.eleccion;   // el 29N: en gris, lo que aún no tiene mesas escrutadas
      el.innerHTML = `<div class="lg-t">Partido más votado · ${ag ? `${(ELEC.find(e => e.cod === y) || {}).nombre || y} · por ${AGREG === 'PR' ? 'provincia' : 'comunidad'} (${agDatos() === AGD ? 'datos de Interior' : 'votos de Interior, con el extranjero'})` : nomE(y)}</div><div class="lg-sw">` +
        FAM.filter((f, k) => used.has(k)).map(f => `<span><b style="background:${f.color}"></b>${nomF(f, y)}</span>`).join('') +
        (used.has(EMPATE) ? `<span><b style="background:rgb(${EMP()})"></b>Empate a votos</span>` : '') +
        (dir && !ag ? `<span><b style="background:rgb(${NODATA()})"></b>Aún sin escrutar</span>` : '') +
        `</div><div class="lg-n">Más intenso cuanto mayor es su porcentaje de voto${REPUBLICA(y) ? '. Listas abiertas: peso de cada bloque en los votos a candidatos (Atlas Electoral de la Segunda República, UPF)' : ''}</div>`;
      return;
    }
    let lo, hi, cols, fmt, name;
    if (st.v === 'party') {
      const f = FAM[FCOD.indexOf(st.party)], mx = domParty(), bg = BG();
      cols = [0, .25, .5, .75, 1].map(t => `rgb(${mix(bg, f.rgb, .06 + .94 * t)})`); lo = 0; hi = mx; fmt = pct; name = 'Voto a ' + nomF(f, st.y) + ' · ' + nomE(st.y);
    } else {
      const V = VARS[st.v]; cols = rampa(V.ramp).map(c => `rgb(${c})`); [lo, hi] = st.v === 'part' ? domPart(st.y) : V.dom; fmt = V.fmt;
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
  // partidos: solo las familias con voto en la elección elegida (las de la República solo existen en 1933 y 1936)
  // ordenadas de más a menos votadas en esa elección (cuota de cada municipio por su población: orden aproximado)
  const PESO = {};
  const peso = (y, c) => { const k = y + '_' + c, a = MUN[k]; if (!a) return 0;
    if (PESO[k] == null || y === (META.directo && META.directo.eleccion)) { let t = 0; for (let i = 0; i < a.length; i++) if (a[i] > 0) t += a[i] * (MUN.poblacion[i] || 0); PESO[k] = t; }
    return PESO[k]; };
  const partidos = () => {
    const fs = FAM.filter(f => f.cod !== 'OTROS' && peso(st.y, f.cod) > 0).sort((a, b) => peso(st.y, b.cod) - peso(st.y, a.cod));
    if (fs.length && !fs.some(f => f.cod === st.party)) st.party = fs[0].cod;
    selP.innerHTML = fs.map(f => `<option value="${f.cod}">${nomF(f, st.y)}</option>`).join('');
    selP.value = st.party;
  };
  partidos();
  const sync = () => { partidos(); verPor(); selP.parentElement.hidden = st.v !== 'party'; selE.disabled = !['gana', 'party', 'part'].includes(st.v); legend(); redraw(); tip.hidden = true; };
  // El año nuevo solo se pinta cuando sus datos han llegado: mientras tanto (y si la descarga falla) el mapa sigue en el
  // año anterior. Antes st.y cambiaba antes de descargar, y cualquier redibujo (zoom, «Qué ver») pintaba todo de gris.
  let pide = 0;
  const elige = async y => {
    const k = ++pide; selE.disabled = true;
    try { await Promise.all([asegura(y), pideNombres(y)]); }
    catch (e) { if (k === pide) { selE.value = st.y; selE.disabled = false; } return; }
    if (k !== pide) return;
    selE.disabled = false; st.y = y; selE.value = y;
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
  const opMun = dl.innerHTML;
  $('#q').addEventListener('change', e => {
    const v = e.target.value.trim().toLowerCase(); if (!v) return;
    const dir = DIRS.get(v);
    if (dir) return buscaDir(dir);
    const i = ORD.find(i => `${MUN.nombre[i]} (${MUN.provs[MUN.prov[i]] || ''})`.toLowerCase() === v) ?? (/\d|,/.test(v) ? null : ORD.find(i => MUN.nombre[i].toLowerCase().startsWith(v)));
    if (i != null) { marca = null; return abre(i); }
    buscaDir({ q: e.target.value.trim() });       // texto libre («calle mayor 3, soria»): la primera dirección que encuentre
  });

  // ---------- búsqueda de calles y portales: geocodificador de CartoCiudad (IGN), público y sin clave. Lleva a la
  // sección censal donde está la dirección (o el centro de la calle, si no se pone número).
  const CC = 'https://www.cartociudad.es/geocoder/api/geocoder/';
  const DIRS = new Map();       // texto de la opción -> candidato de CartoCiudad
  let tq = null, nq = 0;
  const PEQ = new Set(['de', 'del', 'la', 'las', 'el', 'los', 'i', 'y', 'e', 'a', 'en', 'dels', 'les', 'els', 'do', 'da', 'dos', 'das']);
  const tit = t => t.toLowerCase().replace(/[^\s/-]+/g, (w, k) => k && PEQ.has(w.replace(/[()]/g, '')) ? w : w.replace(/^(\(?)(d'|l')?(.)/, (m, p, a, b) => p + (a || '') + b.toUpperCase()));
  const etiDir = c => { const [v, m] = c.address.split(/,\s*/); return tit(v) + ', ' + (m || c.muni); };
  $('#q').addEventListener('input', e => {
    const v = e.target.value.trim(); clearTimeout(tq);
    if (v.length < 4 || DIRS.has(v.toLowerCase()) || MUN.nombre.some(n => n.toLowerCase() === v.toLowerCase())) return;
    tq = setTimeout(async () => {
      const k = ++nq;
      try {
        const r = await fetch(CC + 'candidates?limit=8&no_process=municipio,poblacion,provincia,comunidad autonoma,toponimo,expendeduria,ngbe,codpost,refcatastral&q=' + encodeURIComponent(v));
        const cs = (await r.json()).filter(c => (c.type === 'portal' || c.type === 'callejero') && c.muniCode);
        if (k !== nq) return;
        DIRS.clear();
        const ops = cs.map(c => { const t = etiDir(c); DIRS.set(t.toLowerCase(), c); return `<option value="${escH(t)}">`; });
        dl.innerHTML = ops.join('') + opMun;
      } catch (err) { /* sin conexión con CartoCiudad: queda la búsqueda de municipios */ }
    }, 350);
  });
  async function buscaDir(c) {
    let lon = c.lng, lat = c.lat, via = null;
    try {
      if (!c.id || !lat) {     // calle sin número (o texto libre): «find» devuelve el punto o la línea de la calle
        const u = c.id ? `find?id=${encodeURIComponent(c.id)}&type=${c.type}` : 'find?q=' + encodeURIComponent(c.q);
        c = { ...c, ...await (await fetch(CC + u)).json() };
        lon = c.lng; lat = c.lat;
        const m = /LINESTRING\s*\(([^)]+)\)/.exec(c.geom || '');
        if (m) {
          via = m[1].split(',').map(t => t.trim().split(/\s+/).map(Number));
          if (!lat) [lon, lat] = via[via.length >> 1];
        }
      }
    } catch (err) { /* sin respuesta */ }
    const i = c.muniCode ? MUN.cod.indexOf(c.muniCode) : -1;
    if (!lat || i < 0) { $('#q').setCustomValidity('No encuentro esa dirección'); $('#q').reportValidity(); setTimeout(() => $('#q').setCustomValidity(''), 2500); return; }
    const p = c.muniCode.slice(0, 2), lleva = q => esCan(p) ? canT([q[0] + CDX, q[1] + CDY]) : q;
    const pt = lleva([lon, lat]);
    marca = { p: pt, via: via && via.map(q => lleva([...q])) };
    actual = i;
    fly({ longitude: pt[0], latitude: pt[1], zoom: Math.max(view.zoom, 14.5) });
    // la sección que contiene el punto (las secciones de la provincia se piden si aún no están)
    if (!SEC[p]) {
      loading.add(p);
      try { const d = await get('sec/' + p + '.json'); const polys = decode(d); if (esCan(p)) aCan(polys); SEC[p] = { d, polys }; } catch (err) { /* sin secciones */ }
      loading.delete(p);
    }
    aseguraSec(p, st.y);
    const S = SEC[p], o = S && S.polys.find(o => dentro(pt, o.polygon));
    const conSec = o && secHas(p);
    const [d, k, isSec] = conSec ? [S.d, o.i, true] : [MUN, i, false];
    hover = { key: (isSec ? 'sec' + p : 'mun') + k, polys: (isSec ? S.polys : MUNP).filter(q => q.i === k) };
    tipAbierta = [d, k, isSec]; tip.innerHTML = CERRAR + ficha(d, k, isSec); tip.hidden = false;
    tip.style.left = '8px'; tip.style.top = narrow() ? 'auto' : '8px'; tip.style.bottom = narrow() ? '8px' : 'auto';
    redraw();
  }
  function dentro([x, y], r) {      // punto en polígono (par-impar)
    let si = false;
    for (let a = 0, b = r.length - 1; a < r.length; b = a++) {
      const [xa, ya] = r[a], [xb, yb] = r[b];
      if ((ya > y) !== (yb > y) && x < (xb - xa) * (y - ya) / (yb - ya) + xa) si = !si;
    }
    return si;
  }
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
    tipAbierta = [MUN, qm, false]; tip.innerHTML = CERRAR + ficha(MUN, qm, false); tip.hidden = false;
    tip.style.left = '8px'; tip.style.top = narrow() ? 'auto' : '8px'; tip.style.bottom = narrow() ? '8px' : 'auto';
  } else if (Q.get('q')) {      // ?q=<calle y número>: el buscador de «Qué votó tu calle» (elecciones/que-voto-tu-calle/)
    $('#q').value = Q.get('q').slice(0, 120);
    buscaDir({ q: Q.get('q').slice(0, 120) });
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
    await tick(); setInterval(tick, 30000);   // cada 30 s: los primeros datos, lo antes posible (Nacho, 24-11)
  }
  // ---------- sondeo a pie de urna, la noche del 29N, del cierre de los colegios a los primeros datos de Interior. El titular lo
  // pone a mano el workflow «Directo 29N: sondeo a pie de urna» en el Worker, que no lo sirve antes de su hora (PIEURNA_DESDE);
  // aquí se quita solo en cuanto el escrutinio pasa del 30 % (o cuando se borra). Nunca toca el H1 ni el título.
  let ESCNAT = 0, PUP = null;
  const PUURL = new URLSearchParams(location.search).get('pieurna') || (DIRURL && /\/resultados\.json(\?|$)/.test(DIRURL) ? DIRURL.replace(/\/resultados\.json.*$/, '/pieurna.json') : null);
  if (PUURL) {
    const pu = async () => {
      try { const r = await fetch(PUURL + (PUURL.includes('?') ? '&' : '?') + 't=' + Date.now(), { cache: 'no-store' }); pieUrna(r.ok ? await r.json() : null); } catch (e) { /* sin red: se queda como está */ }
    };
    pu(); setInterval(pu, 60000);
  }
  function pieUrna(P) {
    let b = document.getElementById('pie-urna');
    PUP = P;
    if (!(P && P.titular && P.medio) || ESCNAT >= 0.3) { if (b) b.hidden = true; mapaEnEspera(false); return; }
    const mapa = document.getElementById('mapa'); if (!mapa) return;
    if (!b) {
      b = document.createElement('div'); b.id = 'pie-urna'; b.setAttribute('aria-live', 'polite');
      b.style.cssText = 'font-family:var(--sans);border:1px solid var(--line);border-left:4px solid var(--ink);background:var(--surface);border-radius:8px;padding:12px 14px;margin:6px 0 4px';
      mapa.insertBefore(b, document.getElementById('directo') || mapa.firstChild);
    }
    const fil = Array.isArray(P.filas) ? P.filas.filter(f => Array.isArray(f) && f[0] && f[1]) : [];
    const enl = /^https:\/\//.test(P.enlace || '') ? ` (<a href="${escH(P.enlace)}" rel="noopener" target="_blank">fuente</a>)` : '';
    // hemiciclo con el punto medio de cada horquilla (el resto hasta 350, en gris) y, debajo, el de 2023 (Nacho, 23-11)
    const pf = fil.map(([p, r]) => { const m = String(r).match(/(\d+)(?:\D+(\d+))?/); return [famPU(p), m ? (+m[1] + +(m[2] || m[1])) / 2 : 0]; });
    const E = {}; pf.forEach(([k, e]) => { if (k >= 0) E[k] = (E[k] || 0) + e; });
    const ahora = Object.entries(E).map(([k, e]) => [+k, Math.round(e)]), suma = ahora.reduce((t, x) => t + x[1], 0);
    let hemi = '';
    if (ahora.length && suma <= 350 && suma >= 300) {
      if (suma < 350) { const ko = FCOD.indexOf('OTROS'); const o = ahora.find(x => x[0] === ko); if (o) o[1] += 350 - suma; else ahora.push([ko, 350 - suma]); }
      const T = PUF && PUF.ant23 && PUF.ant23.ambitos && PUF.ant23.ambitos.TO;
      const y = (META.directo && META.directo.eleccion) || '2026_11';
      hemi = donuts(y, ahora, T ? porFamilia(T.c).map(([k, , e]) => [k, e]) : null)
        + `<p class="mut" style="font:12px/1.4 var(--sans);margin:4px 0 6px;text-align:center">Punto medio de cada horquilla del sondeo${suma < 350 ? '; en gris, el resto de escaños' : ''}${T ? '. Debajo, los escaños de 2023' : ''}.</p>`;
    }
    b.innerHTML = `<div style="font:700 12px var(--sans);letter-spacing:.06em;text-transform:uppercase">Sondeo a pie de urna${P.hora ? ' · ' + escH(P.hora) : ''}</div>`
      + `<p style="font:700 19px/1.25 var(--sans);margin:6px 0">${escH(P.titular)}</p>`
      + hemi
      + (fil.length ? `<p style="font:15px/1.5 var(--sans);margin:0 0 6px">${fil.map(([p, r]) => `${escH(p)} <b>${escH(r)}</b>`).join(' · ')}</p>` : '')
      + `<p class="mut" style="font:13px/1.4 var(--sans);margin:0">Sondeo de ${escH(P.medio)}${enl}. Es una estimación, no son resultados: los primeros datos del recuento de Interior llegan a partir de las 21:00.</p>`;
    b.hidden = false;
    mapaEnEspera(ESCNAT === 0); colocaPU();
  }
  // antes del escrutinio, el sondeo arriba; con los primeros datos, el mapa arriba con los escaños debajo, y el sondeo
  // baja detrás de ellos hasta que el escrutinio pasa del 30 % (Nacho, 23-11: «luego ya el mapa por municipios y debajo
  // el semicírculo con escaños»)
  function colocaPU() {
    const b = document.getElementById('pie-urna'); if (!b) return;
    const r = document.getElementById('resultados-29n'), d = document.getElementById('directo');
    if (ESCNAT > 0 && r) { if (b.previousElementSibling !== r) { r.after(b); b.classList.add('wide'); } }
    else if (ESCNAT === 0 && d && b.nextElementSibling !== d) { d.before(b); b.classList.remove('wide'); }
  }
  // nombres de partido del sondeo (como los escribe el medio) -> familia del mapa
  const famPU = p => { const a = String(p).toUpperCase().trim();
    const k = /^CC$|COALICI.N CANARIA/.test(a) ? 'CC' : /^SUMAR$|FRENTE AMPLIO|^FA$/.test(a) ? 'SUMAR' : /SE ACAB|^SALF$/.test(a) ? 'SALF' : /^ADELANTE/.test(a) ? 'AA'
      : /^JUNTS$|^JXCAT/.test(a) ? 'JUNTS' : /^EH ?BILDU$|^BILDU$/.test(a) ? 'BILDU' : famDe(a);
    return FCOD.indexOf(k); };
  // mientras está el sondeo y aún no hay escrutinio, el mapa espera (sin selectores ni mapa) hasta los primeros datos (Nacho, 23-11)
  let PUF = null, enEspera = false;
  function mapaEnEspera(si) {
    if (si === enEspera) return; enEspera = si;
    const m = document.getElementById('mapa'); if (!m) return;
    m.querySelectorAll(':scope > .controls, :scope > .mapwrap, :scope > details.hint').forEach(x => { x.hidden = si; });
    if (!si) setTimeout(() => window.dispatchEvent(new Event('resize')), 50);
  }
  function dhondt(votos, n) {
    const q = []; votos.forEach((v, k) => { for (let d = 1; d <= n; d++) q.push([v / d, k]); });
    q.sort((a, b) => b[0] - a[0]); const out = new Array(votos.length).fill(0);
    q.slice(0, n).forEach(([v, k]) => { if (v > 0) out[k]++; }); return out;
  }
  let modoAvance = false, avVisto = 0;
  // Portada del día de la votación (con el directo encendido y datos): el mapa arriba, Actualidad debajo y fuera lo caducado
  // (encuestas, «Votar el 29N, estos días», Internacional y vídeos). Solo en la portada; no toca títulos, H1 ni URL.
  // siglas de Interior -> partido del simulador de pactos (encuestas/simulador-pactos/); UPN-PP, lista conjunta, cuenta como PP
  const SIMK = [[/^(PP\b|PP-|P\.P\.|UPN-PP)/, 'PP'], [/PSOE(?! ?\(?H)|^PSC\b|^PSC-|^PSE-EE|^PSDEG|^PSIB|^PSN/, 'PSOE'], [/^VOX/, 'VOX'],
    [/SUMAR|FRENTE AMPLIO|FRONT AMPLI|FRONTE AMPLA|FRONTE ZABALA|^FA$|^COMUNS|^ARAM[EÉ]S|^COMPROM/, 'SUMAR'], [/PODEMOS/, 'PODEMOS'], [/^ERC|ESQUERRA/, 'ERC'], [/JUNTS|^JXCAT/, 'JUNTS'], [/BILDU/, 'BILDU'], [/PNV/, 'PNV'],
    [/^B\.?N\.?G/, 'BNG'], [/^CCA?\b|COALICI.N CANARIA|^1\.?ºCAN/, 'CC'], [/^U\.?P\.?N\.?$/, 'UPN'], [/SALF|SE ACAB/, 'SALF'], [/ADELANTE/, 'AA']];
  const NOMSIM = { PP: 'PP', PSOE: 'PSOE', VOX: 'Vox', SUMAR: 'Frente Amplio', PODEMOS: 'Podemos', ERC: 'ERC', JUNTS: 'Junts', BILDU: 'EH Bildu', PNV: 'PNV', BNG: 'BNG', CC: 'CC', UPN: 'UPN', SALF: 'SALF', AA: 'Adelante Andalucía' };
  // Debajo del mapa: medio dónut de escaños (y el de 2023, más pequeño) y barras de voto válido por partido
  const IZQDER = ['BILDU', 'BNG', 'CUP', 'ERC', 'PODEMOS', 'AA', 'SUMAR', 'NC', 'PSOE', 'GBAI', 'PRC', 'TE', 'SY', 'CC', 'PNV', 'JUNTS', 'UPL', 'OTROS', 'CS', 'UPN', 'PP', 'VOX', 'SALF'];
  // Medio dónut de escaños: L [[color, n, nombre]] de izquierda a derecha; grande y con el total, o pequeño y claro (2023)
  function semidonut(L, chico) {
    const N = L.reduce((t, x) => t + x[1], 0); if (!N) return '';
    const W = 400, H = chico ? 120 : 210, R = chico ? 105 : 190, r = R * .58, cx = 200, cy = H - 4;
    let a0 = Math.PI, svg = '';
    const pto = (a, rr) => `${(cx + Math.cos(a) * rr).toFixed(1)},${(cy - Math.sin(a) * rr).toFixed(1)}`;
    for (const [col, m, nom] of L) {
      const a1 = a0 - Math.PI * m / N, big = (a0 - a1) > Math.PI ? 1 : 0;
      svg += `<path d="M${pto(a0, R)} A${R},${R} 0 ${big} 1 ${pto(a1, R)} L${pto(a1, r)} A${r},${r} 0 ${big} 0 ${pto(a0, r)}Z" fill="${col}" stroke="var(--bg)" stroke-width="${chico ? 1 : 1.5}"${chico ? ' opacity=".5"' : ''}><title>${escH(nom)}: ${m}</title></path>`;
      if (m / N >= (chico ? .06 : .045)) { const am = (a0 + a1) / 2; svg += `<text x="${(cx + Math.cos(am) * (R + r) / 2).toFixed(1)}" y="${(cy - Math.sin(am) * (R + r) / 2 + (chico ? 4 : 6)).toFixed(1)}" text-anchor="middle" style="font:700 ${chico ? 12 : 17}px var(--sans);fill:${chico ? 'var(--ink)' : '#fff'}">${m}</text>`; }
      a0 = a1;
    }
    const may = Math.floor(N / 2) + 1;
    if (!chico && N >= 10) svg += `<line x1="${cx}" y1="${cy - r + 8}" x2="${cx}" y2="${cy - R - 4}" stroke="currentColor" stroke-width="2"/>`;
    return `<svg viewBox="0 0 ${W} ${H + (chico ? 0 : 8)}" role="img" aria-label="${chico ? 'Escaños en 2023' : 'Escaños'}: ${L.map(x => x[2] + ' ' + x[1]).join(', ')}" style="width:100%;max-width:${chico ? 300 : 520}px;display:block;margin:${chico ? '4px' : '0'} auto 0">${svg}`
      + `<text x="${cx}" y="${cy - (chico ? 6 : 10)}" text-anchor="middle" style="font:700 ${chico ? 18 : 34}px var(--sans);fill:currentColor">${chico ? '2023' : N}</text>`
      + (!chico && N >= 10 ? `<text x="${cx}" y="${cy + 6}" text-anchor="middle" style="font:12px var(--sans);fill:var(--muted)">mayoría: ${may}</text>` : '') + '</svg>';
  }
  const donuts = (y, ahora, antes) => {   // ahora/antes: [[k, escaños]] por familia
    const L = A => A.filter(x => x[1]).sort((a, b) => ordIzq(a[0], b[0])).map(([k, e]) => [FAM[k].color, e, nomF(FAM[k], y)]);
    return semidonut(L(ahora), false) + (antes && antes.some(x => x[1]) ? semidonut(L(antes), true) : '');
  };
  const ordIzq = (a, b) => { const i = x => { const p = IZQDER.indexOf(FCOD[x]); return p < 0 ? IZQDER.indexOf('OTROS') : p; }; return i(a) - i(b); };
  const SELR = { cam: 'C', amb: 'TO' }; let RESF = null;
  // filas [familia, votos, escaños] de una lista de candidaturas de Interior: [siglas, votos, escaños]
  const porFamilia = c => { const v = {}, e = {}; for (const [s, x, n] of c) { const k = FCOD.indexOf(famDe(s)); if (k < 0) continue; v[k] = (v[k] || 0) + (x || 0); e[k] = (e[k] || 0) + (n || 0); }
    return Object.keys(v).map(Number).map(k => [k, v[k], e[k]]); };
  function tablaRes(y, filas, val, conVotos, E23) {   // filas: [k, votos, escaños]; E23: escaños de 2023 por familia
    filas = filas.filter(([k, v, e]) => e || (conVotos && v / val >= .005))
      .sort((a, b) => (FCOD[a[0]] === 'OTROS') - (FCOD[b[0]] === 'OTROS') || (conVotos ? b[1] - a[1] : b[2] - a[2]));
    const mx = Math.max(...filas.map(f => conVotos ? f[1] : f[2]), 1);
    return '<table style="width:100%;border-collapse:collapse;font:15px/1.3 var(--sans);margin-top:10px"><thead><tr style="color:var(--muted);font-size:13px;text-align:left"><th style="font-weight:500;padding:4px 0">Partido</th><th></th>'
      + (conVotos ? '<th style="font-weight:500;text-align:right">% voto</th>' : '') + '<th style="font-weight:500;text-align:right;padding-left:8px">Escaños</th>' + (E23 ? '<th style="font-weight:500;text-align:right;padding-left:8px">2023</th>' : '') + '</tr></thead><tbody>'
      + filas.map(([k, v, e]) => `<tr style="border-top:1px solid var(--line)"><td style="padding:5px 8px 5px 0;white-space:nowrap">${escH(nomF(FAM[k], y))}</td>`
        + `<td style="width:55%"><span style="display:block;height:12px;border-radius:0 3px 3px 0;width:${Math.max(1, (conVotos ? v : e) / mx * 100).toFixed(1)}%;background:${FAM[k].color}"></span>${conVotos ? `<span class="mut" style="display:block;font-size:11px;line-height:1.2">${num(Math.round(v))} votos</span>` : ''}</td>`
        + (conVotos ? `<td style="text-align:right;font-family:var(--mono);font-size:13px">${pct(v / val)}</td>` : '') + `<td style="text-align:right;font-weight:700;padding-left:8px">${e}</td>${E23 ? `<td class="mut" style="text-align:right;padding-left:8px">${E23[k] || 0}</td>` : ''}</tr>`).join('')
      + '</tbody></table>';
  }
  function resultados(y, ord, seats, nat, esc, deInterior, F) {
    const sec = $('#resultados-29n'), c = $('#resultados-cuerpo'); if (!sec || !c) return;
    if (F) RESF = { y, ord, seats, nat, esc, deInterior, F };
    ({ y, ord, seats, nat, esc, deInterior, F } = RESF);
    const tot = seats.reduce((a, b) => a + b, 0);
    if (!nat.val || !tot) { sec.hidden = true; return; }
    sec.hidden = false;
    const A = F.ambitos, S = F.senado, cam = SELR.cam === 'S' && S ? 'S' : 'C', D = cam === 'S' ? S : A;
    const opt = (v, t) => `<option value="${v}"${SELR.amb === v ? ' selected' : ''}>${escH(t)}</option>`;
    const grupo = (t, O, pre) => O && Object.keys(O).length ? `<optgroup label="${t}">` + Object.entries(O).sort((a, b) => a[1].n.localeCompare(b[1].n, 'es')).map(([k, o]) => opt(pre + k, o.n)).join('') + '</optgroup>' : '';
    if (!D || !(SELR.amb === 'TO' || (SELR.amb.slice(0, 2) in { CM: 1, PR: 1, CI: 1 } && D[SELR.amb.slice(0, 2)] && D[SELR.amb.slice(0, 2)][SELR.amb.slice(2)]))) SELR.amb = 'TO';
    const sel = 'font:15px var(--sans);padding:6px 8px;border-radius:6px;border:1px solid var(--line);background:var(--surface);color:var(--ink);max-width:100%';
    let h = `<div style="display:flex;gap:8px;flex-wrap:wrap;margin:0 0 8px"><select id="r-cam" aria-label="Cámara" style="${sel}"><option value="C">Congreso</option><option value="S"${cam === 'S' ? ' selected' : ''}${S ? '' : ' disabled'}>Senado${S ? '' : ' (aún sin datos)'}</option></select>`
      + (D ? `<select id="r-amb" aria-label="Territorio" style="${sel};flex:1">${opt('TO', 'España')}${grupo('Comunidades', D.CM, 'CM')}${grupo(cam === 'S' ? 'Circunscripciones' : 'Provincias', cam === 'S' ? D.CI : D.PR, cam === 'S' ? 'CI' : 'PR')}</select>` : '') + '</div>';
    const X = SELR.amb === 'TO' ? D && D.TO : D && D[SELR.amb.slice(0, 2)][SELR.amb.slice(2)];
    const T = F.ant23 && F.ant23[cam === 'S' ? 'senado' : 'ambitos'], X23 = T && (SELR.amb === 'TO' ? T.TO : T[SELR.amb.slice(0, 2)] && T[SELR.amb.slice(0, 2)][SELR.amb.slice(2)]);
    const e23 = !X23 ? null : cam === 'S' ? porFamilia(X23.c.map(([s, e]) => [s, 0, e])).map(([k, , e]) => [k, e])
      : porFamilia(X23.c).map(([k, , e]) => [k, e]);
    const E23 = e23 ? Object.fromEntries(e23) : null;
    if (cam === 'C' && !X) {   // sin los totales de Interior: lo calculado con los municipios
      const hem = ord.filter(k => seats[k]).sort(ordIzq).map(k => [FAM[k].color, seats[k], nomF(FAM[k], y)]);
      h += `<p class="mut" style="font:14px/1.4 var(--sans);margin:0 0 6px">Con el ${pct(esc)} escrutado. ${deInterior ? 'Escaños provisionales de Interior' : 'Escaños calculados con el voto escrutado (sin el voto desde el extranjero)'}; la mayoría absoluta, 176.</p>`
        + donuts(y, ord.filter(k => seats[k]).map(k => [k, seats[k]]), e23) + tablaRes(y, FCOD.map((_, k) => [k, nat.f[k], seats[k]]), nat.val, true, E23);
    } else if (cam === 'C') {
      const fil = porFamilia(X.c), val = fil.reduce((t, f) => t + f[1], 0) + (X.bl || 0);
      h += `<p class="mut" style="font:14px/1.4 var(--sans);margin:0 0 6px">${escH(X.n)}: ${pct(X.esc / 100)} escrutado. Escaños provisionales de Interior${SELR.amb === 'TO' ? '; la mayoría absoluta, 176' : ` (${X.el} en juego)`}.</p>`
        + donuts(y, fil.map(([k, , e]) => [k, e]), e23) + tablaRes(y, fil, val, true, E23);
    } else if (SELR.amb.startsWith('CI')) {   // una circunscripción del Senado: candidatos, votos y electos
      const C = X.c.slice().sort((a, b) => b[2] - a[2]), mx = Math.max(...C.map(x => x[2]), 1);
      const col = s => FAM[FCOD.indexOf(famDe(s))] ? FAM[FCOD.indexOf(famDe(s))].color : '#999';
      h += `<p class="mut" style="font:14px/1.4 var(--sans);margin:0 0 6px">${escH(X.n)}: ${pct(X.esc / 100)} escrutado. ${X.el} senadores en juego; en negrita, los elegidos según Interior.</p>`
        + donuts(y, porFamilia(C.filter(x => x[3]).map(x => [x[0], 0, 1])).map(([k, , e]) => [k, e]), e23)
        + '<table style="width:100%;border-collapse:collapse;font:14px/1.3 var(--sans);margin-top:10px"><tbody>' + C.slice(0, 16).map(x => `<tr style="border-top:1px solid var(--line)${x[3] ? ';font-weight:700' : ''}">`
          + `<td style="padding:5px 8px 5px 0">${escH(x[1])}<br><span class="mut" style="font-weight:400;font-size:12px">${escH(x[0])}</span></td><td style="width:35%"><span style="display:block;height:10px;border-radius:0 3px 3px 0;width:${Math.max(1, x[2] / mx * 100).toFixed(1)}%;background:${col(x[0])}"></span></td>`
          + `<td style="text-align:right;font-family:var(--mono);font-size:13px">${num(x[2])}</td></tr>`).join('') + '</tbody></table>';
    } else {
      const fil = porFamilia(X.c.map(([s, e]) => [s, 0, e]));
      h += `<p class="mut" style="font:14px/1.4 var(--sans);margin:0 0 6px">${escH(X.n)}: ${pct(X.esc / 100)} escrutado. Senadores elegidos en las urnas según Interior${SELR.amb === 'TO' ? ` (${X.el}); faltan los que designan los parlamentos autonómicos` : ''}.</p>`
        + donuts(y, fil.map(([k, , e]) => [k, e]), e23) + tablaRes(y, fil, 1, false, E23);
    }
    c.innerHTML = h;
    const rc = $('#r-cam'), ra = $('#r-amb');
    if (rc) rc.onchange = () => { SELR.cam = rc.value; SELR.amb = 'TO'; resultados(); };
    if (ra) ra.onchange = () => { SELR.amb = ra.value; resultados(); };
  }
  // Diputados y senadores que salen por provincia. Interior da los escaños de cada lista, no los nombres: los diputados son
  // los primeros de cada lista del BOE (data/candidatos-congreso-29n.json, src/candidatos_directo.py) según esos escaños.
  // Los senadores sí los da Interior (candidato a candidato, en las circunscripciones del Senado).
  let LISTAS = null, LISTASP = null, PROVE = '28';
  function electos(F) {
    const sec = $('#electos-29n'), c = $('#electos-cuerpo'); if (!sec || !c) return;
    const A = F && F.ambitos && F.ambitos.PR; if (!A || !Object.values(A).some(o => o.c.some(x => x[2]))) { sec.hidden = true; return; }
    if (!LISTAS) { LISTASP = LISTASP || get('candidatos-congreso-29n.json').then(j => { LISTAS = j; electos(F); }).catch(() => {}); return; }
    sec.hidden = false;
    const nor = t => String(t || '').normalize('NFD').replace(/[^A-Za-z0-9]/g, '').toUpperCase();
    const pp = A[PROVE] ? PROVE : '28', X = A[pp], LP = LISTAS[pp] || {};
    const col = s => (FAM[FCOD.indexOf(famDe(s))] || { color: '#999' }).color;
    const lista = s => { const k = Object.keys(LP).find(x => nor(x) === nor(s)); if (k) return LP[k];
      const f = famDe(s), m = f === 'OTROS' ? [] : Object.keys(LP).filter(x => famDe(x) === f); return m.length === 1 ? LP[m[0]] : null; };
    const dip = X.c.filter(x => x[2]).sort((a, b) => b[2] - a[2] || b[1] - a[1]);
    const S = F.senado && F.senado.CI ? Object.entries(F.senado.CI).filter(([k]) => k.startsWith(pp)) : [];
    const sel = 'font:15px var(--sans);padding:6px 8px;border-radius:6px;border:1px solid var(--line);background:var(--surface);color:var(--ink);max-width:100%';
    let h = `<select id="e-prov" aria-label="Provincia" style="${sel}">` + Object.entries(A).sort((a, b) => a[1].n.localeCompare(b[1].n, 'es'))
      .map(([k, o]) => `<option value="${k}"${k === pp ? ' selected' : ''}>${escH(o.n)}</option>`).join('') + '</select>';
    h += `<p class="mut" style="font:14px/1.4 var(--sans);margin:8px 0">${escH(X.n)}, ${pct(X.esc / 100)} escrutado. Congreso: los primeros de cada lista según los escaños provisionales de Interior; pueden cambiar hasta el final del recuento.</p>`;
    const fila = (s, nombres) => `<div style="display:flex;gap:10px;padding:7px 0;border-top:1px solid var(--line);font:15px/1.35 var(--sans)"><b style="flex:0 0 auto;min-width:3.5em"><i style="display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;background:${col(s)}"></i>${escH(NOMBRE_CORTO(s))}</b><span>${nombres}</span></div>`;
    h += '<h3 style="font:700 14px var(--sans);margin:12px 0 4px">Diputados (' + dip.reduce((t, x) => t + x[2], 0) + ')</h3>'
      + dip.map(([s, , e]) => { const L = lista(s); return fila(s, L ? L.slice(0, e).map(escH).join(', ') : `${e} escaño${e > 1 ? 's' : ''} (no encuentro la lista en el BOE)`); }).join('');
    if (S.length) {
      const sen = S.flatMap(([, o]) => o.c.filter(x => x[3]).map(x => [x[0], x[1], o.n]));
      const g = {}; sen.forEach(([s, nom, ci]) => (g[s] ||= []).push(escH(nom) + (S.length > 1 ? ` <span class="mut">(${escH(ci)})</span>` : '')));
      h += `<h3 style="font:700 14px var(--sans);margin:14px 0 4px">Senadores (${sen.length})</h3>` + Object.entries(g).map(([s, L]) => fila(s, L.join(', '))).join('');
    }
    c.innerHTML = h;
    $('#e-prov').onchange = e => { PROVE = e.target.value; electos(F); };
  }
  const NOMBRE_CORTO = s => { const k = FCOD.indexOf(famDe(s)); return k >= 0 && FCOD[k] !== 'OTROS' ? nomF(FAM[k], META.directo.eleccion) : s; };
  function pactos(F, esc) {
    const c = $('#pactos-cuerpo'); if (!c || !F.escanos) return;
    const E = {}; let tot = 0;
    for (const d of Object.values(F.escanos)) for (const [s, n] of Object.entries(d)) {
      const a = (s || '').toUpperCase().trim(), m = SIMK.find(([r]) => r.test(a)), k = m ? m[1] : 'OTROS';
      E[k] = (E[k] || 0) + n; tot += n;
    }
    if (!tot) return;
    const suma = ks => ks.reduce((t, k) => t + (E[k] || 0), 0);
    const P = [['PP y Vox', ['PP', 'VOX', 'UPN']], ['PSOE, Frente Amplio, Podemos y los socios de 2023', ['PSOE', 'SUMAR', 'PODEMOS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC']],
      ['PP y PSOE', ['PP', 'PSOE']]].map(([n, ks]) => [n, suma(ks)]);
    const link = (RAIZ ? new URL('../encuestas/simulador-pactos/', RAIZ).href : 'encuestas/simulador-pactos/') + '#e='
      + Object.entries(E).filter(([k, n]) => k !== 'OTROS' && n).map(([k, n]) => k + '.' + n).join(',');
    c.innerHTML = `<div style="font:15px/1.4 var(--sans)"><p class="mut" style="margin:0 0 8px">Escaños provisionales de Interior con el ${pct(esc)} escrutado: pueden cambiar hasta el final del recuento.</p>`
      + P.map(([n, x]) => `<div style="display:flex;justify-content:space-between;gap:12px;padding:6px 0;border-top:1px solid var(--line)"><span>${n}</span>`
      + `<span style="white-space:nowrap"><b>${x}</b> · ${x >= 176 ? '<b>mayoría absoluta</b>' : `le faltan ${176 - x}`}</span></div>`).join('')
      + `<p style="margin:10px 0 0"><a href="${link}">Prueba otros pactos con estos escaños en el simulador →</a></p></div>`;
  }
  // la noche del 29N, en el desplegable del mapa solo las variables electorales (se llama con el directo ya cargado)
  function soloElectorales() {
    const E = ['gana', 'party', 'part'];
    [...selV.options].forEach(o => { if (!E.includes(o.value)) o.remove(); });
    if (!E.includes(st.v)) { st.v = 'gana'; selV.value = 'gana'; sync(); }
  }
  function jornada() {
    if (jornadaHecha) return; jornadaHecha = true;
    const mapa = document.getElementById('mapa'); if (!mapa || !mapa.parentNode || !document.querySelector('section.votar-29n')) return;
    const sec = id => { const h = document.getElementById(id); return h && h.closest('section'); };
    [document.querySelector('section.ep'), document.querySelector('section.votar-29n'), sec('h-del-internacional'), sec('h-del-videos'),
     sec('h-del-historia'), sec('h-del-comunidades'), sec('h-del-atlas')]   // la noche del 29N, solo los carruseles del día
      .forEach(x => { if (x) x.hidden = true; });
    document.querySelectorAll('nav.site a[href$="encuestas/"]').forEach(a => { a.hidden = true; });   // y el enlace del menú
    // bajo el titular, solo el enlace a los resultados del 29N (el de la guía previa habla de 2023)
    document.querySelectorAll('p.al29n a[href$="elecciones-29n-2026/"]').forEach(a => {
      if (a.nextElementSibling && a.nextElementSibling.tagName === 'BR') a.nextElementSibling.remove(); a.remove(); });
    // «Posibles pactos» justo debajo del mapa: con el escrutinio, los escaños provisionales de Interior; antes, solo el aviso
    const pac = document.createElement('section');
    pac.className = 'wide'; pac.id = 'pactos-29n';
    pac.innerHTML = '<h2 style="font:700 15px var(--sans);letter-spacing:.06em;text-transform:uppercase;margin:18px 0 8px">Posibles pactos</h2><div id="pactos-cuerpo">'
      + '<p>Cuando empiece el escrutinio, aquí verás qué pactos suman los 176 escaños de la mayoría absoluta con los escaños del recuento de Interior.</p></div>';
    const res = document.createElement('section');   // gráfico de votos y hemiciclo, con el escrutinio
    res.className = 'wide'; res.id = 'resultados-29n'; res.hidden = true;
    res.innerHTML = '<h2 style="font:700 15px var(--sans);letter-spacing:.06em;text-transform:uppercase;margin:18px 0 8px">Resultados del 29N</h2><div id="resultados-cuerpo"></div>';
    mapa.after(res); res.after(pac);
    // y ninguna pieza ni tarjeta de encuestas en la portada ese día (veda hasta las 21:00 y, después, ya no tocan)
    document.querySelectorAll('section.del-atlas a, section.del-atlas li, section.del-atlas article').forEach(a => {
      if (/encuesta|sondeo|40dB|\bCIS\b|simulador de pactos/i.test(a.textContent)) (a.closest('li') || a).hidden = true;
    });
    let tras = pac;
    // las listas, fuera: en su sitio, quién sale elegido en cada provincia (con el escrutinio)
    const lis = sec('h-del-listas'); if (lis) lis.hidden = true;
    const ele = document.createElement('section');
    ele.className = 'wide'; ele.id = 'electos-29n'; ele.hidden = true;
    ele.innerHTML = '<h2 style="font:700 15px var(--sans);letter-spacing:.06em;text-transform:uppercase;margin:18px 0 8px">Quién sale elegido</h2><div id="electos-cuerpo"></div>';
    pac.after(ele); tras = ele;
    ['h-del-actualidad', 'h-del-mapa', 'h-del-guias'].map(sec).forEach(x => { if (x) { tras.after(x); tras = x; } });
  }
  // botones de participación del recuadro del directo: 1.er avance, 2.º avance y final (esta, solo con escrutinio)
  function botonesAvance(y, disp, final) {
    const B = [[y + 'a1', '1.er avance'], [y + 'a2', '2.º avance'], [y, 'Participación final']];
    $('#d-leg').innerHTML = '<span class="mut" style="width:100%">Participación en el mapa:</span>' + B.map(([c, t]) => {
      const ok = c === y ? final : disp.includes(c), on = st.v === 'part' && st.y === c;
      return `<button type="button" data-av="${c}"${ok ? '' : ' disabled'} style="font:inherit;padding:4px 10px;border-radius:6px;border:1px solid currentColor;`
        + `background:${on ? 'var(--ink, #222)' : 'transparent'};color:${on ? 'var(--bg, #fff)' : 'inherit'};opacity:${ok ? 1 : .4};cursor:${ok ? 'pointer' : 'default'}">${t}</button>`;
    }).join('');
    $('#d-leg').querySelectorAll('button[data-av]').forEach(b => b.onclick = () => {
      st.y = b.dataset.av; st.v = 'part'; selV.value = 'part'; selE.value = st.y; sync(); botonesAvance(y, disp, final);
    });
  }
  // ---------- secciones del directo: el Worker suma por sección los ficheros por mesa de Interior (participación al acabar cada
  // avance; votos, al acabar el recuento provisional) y los sirve por provincia en /secciones/<pp>.json. Sin ellos, municipios.
  function seccDirecto(p) {
    const v = SECC.t || '';
    if (SECCV[p] === v || !DIRURL || (!(SECC.av || []).length && !(SECC.esc || []).includes(p))) return; SECCV[p] = v;
    fetch(DIRURL.replace(/resultados\.json.*$/, 'secciones/' + p + '.json') + '?t=' + encodeURIComponent(v), { cache: 'no-store' })
      .then(r => r.status === 404 ? null : r.ok ? r.json() : Promise.reject(r.status))   // 404: esa provincia aún no tiene mesas
      .then(D => { if (!D) return; llenaSecc(p, D); VERD++; redraw(); })
      .catch(() => { delete SECCV[p]; });   // fallo de red: se reintenta al mover el mapa
  }
  function llenaSecc(p, D) {
    const y = META.directo.eleccion, S = SEC[p], n = S.d.cod.length, idx = {}; S.d.cod.forEach((c, i) => idx[c] = i);
    const vacio = () => { const o = { part: new Array(n).fill(null), gana: new Array(n).fill(-1) }; FCOD.forEach(c => o[c] = new Array(n).fill(null)); return o; };
    if (D.av) [0, 1].forEach(k => {
      const o = vacio(); let hay = false;
      for (const [c, a] of Object.entries(D.av)) { const i = idx[c]; if (i != null && a[k] && a[k][0]) { o.part[i] = a[k][1] / a[k][0]; hay = true; } }
      if (hay) Object.entries(o).forEach(([c, v]) => S.d[y + 'a' + (k + 1) + '_' + c] = v);
    });
    if (D.s && D.siglas) {
      const fk = D.siglas.map(x => FCOD.indexOf(famDe(x))), o = vacio();
      for (const [c, a] of Object.entries(D.s)) {
        const i = idx[c]; if (i == null) continue;
        const [ce, vot, bl, , ...v] = a, val = v.reduce((s, x) => s + x, 0) + bl;
        if (!ce || !val) continue;
        o.part[i] = vot / ce;
        const f = new Array(FCOD.length).fill(0); v.forEach((x, k) => { if (fk[k] >= 0) f[fk[k]] += x; });
        FCOD.forEach((cc, k) => { o[cc][i] = f[k] / val; });
        let m = -1; v.forEach((x, k) => { if (m < 0 || x > v[m]) m = k; });
        let g = m >= 0 && v[m] > 0 ? fk[m] : -1;
        if (g >= 0 && v.some((x, k) => k !== m && x === v[m])) g = EMPATE;
        o.gana[i] = g;
      }
      Object.entries(o).forEach(([c, v]) => S.d[y + '_' + c] = v);
    }
  }
  function aplica(F, first) {
    VERD++;
    if (F.secc && (F.secc.av || []).length + (F.secc.esc || []).length) { const nuevo = !SECC || SECC.t !== F.secc.t; SECC = F.secc; if (nuevo) setTimeout(loadVisible, 0); }
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
      FCOD.forEach((c, k) => { col[c][i] = f[k] / val; });
      // el ganador, lista a lista (no la suma de la familia: PP y UPN, o dos listas del espacio de Sumar, van aparte);
      // una lista sin familia que gana se pinta como «Otros», nunca como la familia que quedó segunda
      let m = -1; v.forEach((x, k) => { if (m < 0 || x > v[m]) m = k; });
      let g = m >= 0 && v[m] > 0 ? fk[m] : -1;
      if (g >= 0 && v.some((x, k) => k !== m && x === v[m])) g = EMPATE;   // empate a votos
      col.gana[i] = g;
    }
    // sin ninguna mesa escrutada (el Worker ya encendido antes del cierre) el mapa sigue en 2023: no se cambia a un 29N vacío
    // España con el fichero de totales de Interior (mismo envío), no con la suma de municipios, si lo trae
    const TO = F.ambitos && F.ambitos.TO;
    if (TO && TO.ce && TO.c && TO.c.length) {
      nat.ct = TO.ct; nat.ce = TO.ce; nat.f.fill(0);
      TO.c.forEach(([s, v]) => { const k = FCOD.indexOf(famDe(s)); if (k >= 0) nat.f[k] += v; });
      nat.val = TO.c.reduce((t, x) => t + x[1], 0) + TO.bl;
    }
    ESCNAT = nat.ct ? nat.ce / nat.ct : 0;
    if (ESCNAT >= 0.3 && document.getElementById('pie-urna')) document.getElementById('pie-urna').hidden = true;   // el sondeo, fuera con el recuento
    if (ESCNAT > 0) mapaEnEspera(false);   // con los primeros datos, vuelve el mapa
    colocaPU();
    if (!PUF && F.ant23 && PUP) { PUF = F; pieUrna(PUP); } else PUF = F;   // el hemiciclo de 2023 del sondeo, en cuanto llega
    if (!nat.ce) {   // antes del escrutinio, el recuadro solo enseña los avances de participación, si los hay
      const av = F.avances && F.avances.es ? F.avances.es.filter(x => x != null) : [], me = F.avances && F.avances.mesas;
      if ((!av.length && !(me && me.constituidas)) || !$('#directo')) return;
      $('#directo').hidden = false; jornada(); soloElectorales();
      $('#d-nombre').textContent = META.directo.nombre || y;
      $('#d-esc').textContent = pct(0);
      $('#d-estado').textContent = av.length ? `participación en el ${av.length > 1 ? '2.º' : '1.er'} avance de Interior: ${pct(Math.round(av[av.length - 1] * 10) / 1000)}`
        : `mesas constituidas: ${me.constituidas.toLocaleString('es-ES')} de ${me.total.toLocaleString('es-ES')}`;
      $('#d-seats').innerHTML = ''; $('#d-seats').style.display = 'none'; $('#d-leg').innerHTML = '';
      // con los avances municipio a municipio, el mapa pinta la participación: un botón por avance (y la final, con el escrutinio)
      if (F.avmun && av.length) {
        const disp = [];
        [0, 1].forEach(k => {
          const part = new Array(n).fill(null); let hay = false;
          for (const [c, p] of Object.entries(F.avmun)) { const i = idx[c.padStart(5, '0')], x = Array.isArray(p) ? p[k] : (k ? null : p); if (i != null && x != null) { part[i] = x / 100; hay = true; } }
          if (!hay) return;
          const ya = F.avances.es[k] != null ? F.avances.es[k] / 100 : .4, cod = y + 'a' + (k + 1);
          const vacio = Object.fromEntries(Object.entries(col).map(([c, v]) => [c, v.slice()]));
          Object.entries({ ...vacio, part }).forEach(([c, v]) => MUN[cod + '_' + c] = v);
          const e = { cod, nombre: (META.directo.nombre || y) + (k ? ' · 2.º avance' : ' · 1.er avance'), tipo: 'generales', avance: true, secciones: !!(SECC && (SECC.av || []).includes(k + 1)),
            dom: [Math.max(0, ya - .15), Math.min(1, ya + .15)] };   // escala centrada en el dato de España de ese avance
          const i = ELEC.findIndex(x => x.cod === cod); if (i >= 0) ELEC[i] = e; else ELEC.push(e);
          disp.push(cod);
        });
        if (disp.length) {
          if (!AV23) { AV23 = {}; fetch(RAIZ + 'data/avances_2023.json').then(r => r.json()).then(j => { AV23 = j; }).catch(() => {}); }
          opciones();
          // al llegar un avance nuevo, el mapa pasa a él
          if (!modoAvance || disp.length > avVisto) { st.y = disp[disp.length - 1]; st.v = 'part'; selV.value = 'part'; }
          modoAvance = true; avVisto = disp.length;
          botonesAvance(y, disp, false);
          selE.value = st.y;
          sync();
        }
      }
      return;
    }
    // primer escrutinio después de los avances: el mapa pasa a «Partido más votado» del 29N; los avances siguen en el selector
    if (modoAvance) { modoAvance = false; first = true; st.v = 'gana'; }
    Object.entries(col).forEach(([k, v]) => MUN[y + '_' + k] = v);
    delete partyMax[y + '_' + st.party]; Object.keys(partyMax).forEach(k => k.startsWith(y) && delete partyMax[k]);
    // escaños: D'Hondt por provincia con barrera del 3% del voto válido de la circunscripción
    const E = (META.escanos || {})[y] || {}, seats = new Array(FCOD.length).fill(0);
    for (const [p, P] of Object.entries(prov)) {
      const val = P.v.reduce((s, x) => s + x, 0) + P.bl;
      const s = dhondt(P.v.map(x => x >= .03 * val ? x : 0), E[p] || 0);
      s.forEach((x, k) => seats[fk[k]] += x);
    }
    // si Interior da los escaños provisionales (campo «escanos» del Worker), mandan esos: el cálculo de arriba no lleva el voto CERA
    if (F.escanos && Object.keys(F.escanos).length) {
      seats.fill(0);
      for (const d of Object.values(F.escanos)) for (const [s, x] of Object.entries(d)) { const k = FCOD.indexOf(famDe(s)); if (k >= 0) seats[k] += x; }
    }
    const conSec = !!(SECC && (SECC.esc || []).length), e0 = ELEC.find(e => e.cod === y);
    if (!e0) {
      ELEC.push({ cod: y, nombre: META.directo.nombre || y, tipo: 'generales', secciones: conSec });
      opciones();
    } else if (e0.secciones !== conSec) { e0.secciones = conSec; opciones(); }
    if (first) { st.y = y; if (!['gana', 'party', 'part'].includes(st.v)) st.v = 'gana'; selV.value = st.v; }
    selE.value = st.y;
    // Si el mapa sigue en la vista inicial, se reencaja después de mostrar el recuadro, que le quita alto
    const h0 = HOME(), enCasa = Math.abs(view.zoom - h0.zoom) < .01 && Math.abs(view.longitude - h0.longitude) < 1e-6;
    const box = $('#directo'); box.hidden = false; jornada(); soloElectorales();
    const h1 = HOME(); if (enCasa && h1.zoom !== view.zoom) { view = { ...view, ...h1 }; dk.setProps({ initialViewState: view }); }
    $('#d-nombre').textContent = (F.simulacro ? 'Simulacro con datos del 23J · ' : '') + (META.directo.nombre || y);
    $('#d-esc').textContent = pct(F.escrutado ?? (nat.ct ? nat.ce / nat.ct : 0));
    const t = F.actualizado ? new Date(F.actualizado) : new Date();
    $('#d-estado').textContent = 'actualizado a las ' + t.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Madrid' });
    const ord = FCOD.map((c, k) => k).filter(k => seats[k] > 0 || nat.f[k] / nat.val > .01)
      .sort((a, b) => (seats[b] - seats[a]) || (nat.f[b] - nat.f[a]));
    const tot = seats.reduce((s, x) => s + x, 0) || 1;
    pactos(F, F.escrutado ?? (nat.ct ? nat.ce / nat.ct : 0));
    electos(F);
    resultados(y, ord, seats, nat, F.escrutado ?? (nat.ct ? nat.ce / nat.ct : 0), !!(F.escanos && Object.keys(F.escanos).length), F);
    $('#d-seats').style.display = ''; $('#d-seats').innerHTML = ord.filter(k => seats[k]).map(k => `<span title="${nomF(FAM[k], y)}: ${seats[k]}" style="flex:${seats[k]};background:${FAM[k].color}"></span>`).join('') +
      (tot >= 350 ? '<i></i><em>176, mayoría absoluta</em>' : '');
    agregados(F, y);
    $('#d-leg').innerHTML = ord.map(k => `<span><b style="background:${FAM[k].color}"></b>${nomF(FAM[k], y)} <span class="n">${seats[k]}</span> <span class="mut">${pct(nat.val ? nat.f[k] / nat.val : 0)}</span></span>`).join('');
    sync();
  }

  // ---------- mapas por provincia y por comunidad (Nacho, 24-11), con las cifras de Interior de cada nivel (ámbitos PR y CM).
  // Para que no se rompa nada: es una capa aparte encima del mapa de municipios, que no cambia; el selector solo sale si
  // Interior da todas las provincias y comunidades y cuadran (las provincias suman su comunidad y los municipios su
  // provincia); cualquier error o descuadre lo quita y deja municipios. Se apaga del todo con meta.json directo.agregados=false.
  const CMPR = { '01': ['04', '11', '14', '18', '21', '23', '29', '41'], '02': ['22', '44', '50'], '03': ['33'], '04': ['07'], '05': ['35', '38'],
    '06': ['39'], '07': ['02', '13', '16', '19', '45'], '08': ['05', '09', '24', '34', '37', '40', '42', '47', '49'], '09': ['08', '17', '25', '43'],
    '10': ['06', '10'], '11': ['15', '27', '32', '36'], '12': ['28'], '13': ['31'], '14': ['01', '20', '48'], '15': ['30'], '16': ['26'],
    '17': ['03', '12', '46'], '18': ['51'], '19': ['52'] };   // comunidades con el código de Interior -> provincias (INE)
  const PR2CM = {}; Object.entries(CMPR).forEach(([c, L]) => L.forEach(p => { PR2CM[p] = c; }));
  function agDatos() {   // el 29N, las cifras de Interior (AGD); otras generales, las históricas de data/agregados.json
    if (META.directo && st.y === META.directo.eleccion) return AGD;
    if (!HAG || !HAG[st.y]) return null;
    return HAGN[st.y] || (HAGN[st.y] = { PR: agNivel(HAG[st.y].PR), CM: agNivel(HAG[st.y].CM) });
  }
  // la vista por provincias automática de los primeros minutos (#703) es solo del 29N: en otra fecha, solo si la elige el lector
  function agNivelVisto() { return AGMANO || (META.directo && st.y === META.directo.eleccion) ? AGREG : ''; }
  function agActivo() { const D = agNivelVisto() && st.v === 'gana' ? agDatos() : null; return !!(D && D[AGREG]); }   // (funciones: layers() las usa antes de llegar aquí)
  function agKey(o) { const p = PROV.cod[o.i]; return AGREG === 'CM' ? PR2CM[p] : p; }
  function agColor(p) {
    try {
      const o = agDatos()[AGREG][AGREG === 'CM' ? PR2CM[p] : p];
      if (!o || o.gana == null || o.gana === -1) return NODATA();
      if (o.gana === EMPATE) return EMP();
      return mix(BG(), FAM[o.gana].rgb, Math.max(.28, Math.min(1, (o.s - .15) / .35)));
    } catch (e) { return NODATA(); }
  }
  function agFicha(k) {
    const D = agDatos(), o = D && D[AGREG] && D[AGREG][k]; if (!o) return '';
    const val = o.c.reduce((t, x) => t + x[1], 0) + (o.bl || 0), hist = D !== AGD;
    const fil = o.c.slice().sort((a, b) => b[1] - a[1]).filter((x, i) => i < 8 && (x[1] || x[2]));
    return `<b>${escH(o.n)}</b><br><span class="mut">${hist ? `${(ELEC.find(e => e.cod === st.y) || {}).nombre || st.y} · votos de cada lista, con el voto desde el extranjero (Interior)` : `${pct(o.esc / 100)} escrutado · ${o.el} escaños · datos de Interior`}</span>`
      + '<table style="border-collapse:collapse;margin-top:6px;font-size:13px">' + fil.map(([s, v, e, fm]) => {
        const k2 = FCOD.indexOf(hist ? fm || 'OTROS' : famDe(s)), col = FAM[k2] ? FAM[k2].color : '#999';
        return `<tr><td style="padding:2px 8px 2px 0"><span style="color:${col}">●</span> ${escH(hist ? s : NOMBRE_CORTO(s))}</td><td style="text-align:right;font-family:var(--mono)">${pct(val ? v / val : 0)}</td>${hist ? '' : `<td style="text-align:right;padding-left:8px;font-weight:700">${e || 0}</td>`}</tr>`;
      }).join('') + '</table>';
  }
  function agNivel(O) {   // {cod: {n, esc, el, bl, c: [[siglas, votos, escaños]]}} -> con el ganador lista a lista y su porcentaje
    const out = {};
    for (const [k, o] of Object.entries(O)) {
      const c = o.c || [], val = c.reduce((t, x) => t + x[1], 0) + (o.bl || 0);
      let m = -1; c.forEach((x, i) => { if (m < 0 || x[1] > c[m][1]) m = i; });
      let g = m >= 0 && c[m][1] > 0 ? FCOD.indexOf(c[m][3] || famDe(c[m][0])) : -1;   // históricos: la familia viene en el dato
      if (g >= 0 && c.some((x, i) => i !== m && x[1] === c[m][1])) g = EMPATE;
      out[k] = { ...o, gana: g, s: val && m >= 0 ? c[m][1] / val : 0 };
    }
    return out;
  }
  function agComprueba(F) {   // -> '' si todo cuadra; si no, el motivo (y el selector no sale)
    const A = F.ambitos, tv = o => (o.c || []).reduce((t, x) => t + (x[1] || 0), 0);
    if (!A || !A.PR || !A.CM) return 'sin ámbitos de Interior';
    if (Object.keys(PR2CM).some(p => !A.PR[p])) return 'faltan provincias';
    if (Object.keys(CMPR).some(c => !A.CM[c])) return 'faltan comunidades';
    for (const [c, L] of Object.entries(CMPR)) {
      const a = tv(A.CM[c]), b = L.reduce((t, p) => t + tv(A.PR[p]), 0);
      if (Math.abs(a - b) > Math.max(10, a * .001)) return `la comunidad ${c} no cuadra con sus provincias (${a} y ${b})`;
    }
    const mp = {}; for (const [m, a] of Object.entries(F.mun || {})) { const p = m.padStart(5, '0').slice(0, 2); mp[p] = (mp[p] || 0) + a.slice(5).reduce((t, x) => t + (x || 0), 0); }
    for (const p of Object.keys(PR2CM)) {
      const a = tv(A.PR[p]), b = mp[p] || 0;
      if (Math.abs(a - b) > Math.max(50, a * .005)) return `la provincia ${p} no cuadra con sus municipios (${a} y ${b})`;
    }
    return '';
  }
  // «Ver por» junto a «Elección»: comunidades, provincias o municipios y secciones, en el 29N (si cuadra con Interior) y en
  // las generales de 1982 a 2023 (data/agregados.json, que se descarga la primera vez que se pide). Nacho, 24-11.
  function verPor() {
    let w = document.getElementById('ver-por');
    if (!w) {
      const ctl = selE.closest('label'); if (!ctl) return;
      w = document.createElement('label'); w.id = 'ver-por';
      w.innerHTML = 'Ver por <select id="sel-nivel"><option value="">Municipios y secciones</option><option value="PR">Provincias</option><option value="CM">Comunidades</option></select>';
      ctl.after(w);
      w.querySelector('select').onchange = async e => {
        const v = e.target.value; AGMANO = true;
        if (v && !HAG) { try { await cargaHAG(); } catch (x) { e.target.value = ''; return; } }
        AGREG = v; tip.hidden = true; hover = null;
        document.querySelectorAll('#d-ver button[data-ag]').forEach(x => { const on = x.dataset.ag === AGREG;
          x.style.background = on ? 'var(--ink, #222)' : 'transparent'; x.style.color = on ? 'var(--bg, #fff)' : 'inherit'; });
        legend(); redraw();
      };
    }
    const dir = META.directo && st.y === META.directo.eleccion;
    const hay = st.v === 'gana' && (dir ? !!AGD : /^\d{4}_\d{2}$/.test(st.y) && st.y >= '1982' && st.y <= '2023_12');
    w.hidden = !hay; w.querySelector('select').value = agNivelVisto();
    if (hay && !dir && AGREG && !HAG) cargaHAG().then(() => { legend(); redraw(); }, () => {});
  }
  function cargaHAG() { return HAGP || (HAGP = get('agregados.json').then(d => { HAG = d; }, e => { HAGP = null; throw e; })); }
  function agregados(F, y) {
    let motivo = 'apagado en meta.json';
    try {
      if (META.directo.agregados !== false) motivo = agComprueba(F);
      AGD = motivo ? null : { PR: agNivel(F.ambitos.PR), CM: agNivel(F.ambitos.CM) };
    } catch (e) { AGD = null; motivo = 'error: ' + e.message; }
    window.__agregados = motivo || 'ok';   // para las pruebas
    // los primeros minutos del escrutinio, el mapa abre por provincias (Nacho, 24-11), que se ven enteras desde la primera
    // mesa; al pasar del 10 % escrutado vuelve solo a municipios. Si el lector ya ha tocado un botón, se respeta lo suyo
    if (AGD && !AGMANO) AGREG = ESCNAT < AGUMBRAL ? 'PR' : '';
    if (!AGD && AGREG) AGREG = '';
    let b = document.getElementById('d-ver');
    if (!AGD) { if (b) b.hidden = true; legend(); verPor(); redraw(); return; }
    if (!b) { b = document.createElement('div'); b.id = 'd-ver'; b.className = 'd-leg'; $('#d-leg').after(b); }
    const B = [['', 'Municipios y secciones'], ['PR', 'Provincias'], ['CM', 'Comunidades']];
    b.innerHTML = '<span class="mut" style="width:100%">Ver por:</span>' + B.map(([c, t]) => { const on = AGREG === c;
      return `<button type="button" data-ag="${c}" style="font:inherit;padding:4px 10px;border-radius:6px;border:1px solid currentColor;background:${on ? 'var(--ink, #222)' : 'transparent'};color:${on ? 'var(--bg, #fff)' : 'inherit'};cursor:pointer">${t}</button>`; }).join('');
    b.hidden = !!document.getElementById('ver-por');   // con «Ver por» junto a «Elección» (#704), sin botones repetidos en el recuadro
    b.querySelectorAll('button[data-ag]').forEach(x => x.onclick = () => {
      AGREG = x.dataset.ag; AGMANO = true; tip.hidden = true; hover = null;
      if (AGREG) { st.y = y; st.v = 'gana'; selV.value = 'gana'; selE.value = y; sync(); }
      agregados(F, y);
    });
    legend(); verPor(); redraw();
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
