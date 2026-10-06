"""Índice de calles para el buscador: cada vía de Cataluña con los tramos de numeración de cada sección censal.

Fuente: callejero del censo electoral del INE (caj_esp_012023, datos a 31-12-2022, mismas secciones que el mapa).
Uso: python3 src/calles.py TRAM.gz VIAS.gz tracts.json calles.json
     (TRAM y VIAS: ficheros del callejero ya filtrados a las provincias 08, 17, 25 y 43, comprimidos con gzip;
      tracts.json: lista de códigos de sección en el mismo orden que el mapa)

Salida: {"t": [tipos de vía], "m": {código de municipio: [[nombre, tipo, tramos], ...]}}
  tramos = índice de sección si toda la calle está en una, o lista de [sección, paridad, desde, hasta]
  (paridad 1 impares, 2 pares, 0 sin numeración).
"""
import sys, gzip, json, collections

TRAM, VIAS, TRACTS, OUT = sys.argv[1:5]
TIPOS = {'C': 'carrer', 'CARRE': 'carrer', 'C/': 'carrer', 'PL': 'plaça', 'PLAÇA': 'plaça', 'PTGE': 'passatge',
         'PRAGE': 'passatge', 'PSAJE': 'passatge', 'CAMI': 'camí', 'AV': 'avinguda', 'AVGDA': 'avinguda',
         'CTRA': 'carretera', 'CRA': 'carretera', 'PG': 'passeig', 'RONDA': 'ronda', 'RDA': 'ronda', 'TRAV': 'travessera',
         'TRVA': 'travessia', 'TRSSI': 'travessia', 'RBLA': 'rambla', 'VIA': 'via', 'URB': 'urbanització',
         'URBAT': 'urbanització', 'PLCET': 'placeta', 'RIERA': 'riera', 'BARRI': 'barri', 'PARC': 'parc', 'JARD': 'jardins',
         'JDIN': 'jardins', 'JDINS': 'jardins', 'PTDA': 'partida', 'PDA': 'partida', 'LLOC': 'lloc', 'POLIG': 'polígon',
         'BDA': 'barriada', 'G.V.': 'gran via', 'GV': 'gran via', 'GRUP': 'grup', 'RAVAL': 'raval', 'MOLL': 'moll', 'ESCA': 'escales', 'COSTA': 'costa',
         'PONT': 'pont', 'PROL': 'prolongació', 'BXDA': 'baixada', 'PUJA': 'pujada'}
MENORES = {'de', 'del', 'dels', 'la', 'les', 'el', 'els', 'i', 'y', 'a', 'al', 'en', 'lo', 'los', 'las', 'sa', 'ses', 'es'}


def titulo(n):
    out = []
    for k, w in enumerate(n.lower().split()):
        if k and w in MENORES:
            out.append(w); continue
        # d'en, l'església: apóstrofo en minúscula y la palabra que sigue en mayúscula
        if "'" in w and len(w) > 2 and w[1] == "'":
            out.append(w[:2] + w[2:].capitalize() if k else w[0].upper() + "'" + w[2:].capitalize()); continue
        out.append(w.capitalize())
    return ' '.join(out)


tracts = json.load(open(TRACTS))
idx = {t: i for i, t in enumerate(tracts)}
vias = {}
for l in gzip.open(VIAS):
    l = l.decode('latin-1')
    vias[(l[0:5], l[5:10])] = (titulo(l[33:83].strip()), l[27:32].strip())

seg = collections.defaultdict(list)
sin = 0
for l in gzip.open(TRAM):
    l = l.decode('latin-1')
    sec = idx.get(l[0:10])
    if sec is None:
        sin += 1; continue
    par = l[47]
    ein, esn = l[48:52], l[53:57]
    par = int(par) if par in '12' else 0
    a = int(ein) if ein.isdigit() else 0
    b = int(esn) if esn.isdigit() else 9999
    if par == 0: a, b = 0, 9999
    seg[(l[0:5], l[20:25])].append([sec, par, a, b])

tipos, tix = [], {}
mun = collections.defaultdict(list)
for (m, cv), ts in seg.items():
    nombre, tipo = vias.get((m, cv), (None, ''))
    if not nombre:
        continue
    t = TIPOS.get(tipo, '')
    if t not in tix:
        tix[t] = len(tipos); tipos.append(t)
    secs = {x[0] for x in ts}
    if len(secs) == 1:
        tr = ts[0][0]
    else:
        # une tramos contiguos de la misma sección y paridad
        ts.sort(key=lambda x: (x[1], x[2]))
        tr = []
        for x in ts:
            if tr and tr[-1][0] == x[0] and tr[-1][1] == x[1] and x[2] <= tr[-1][3] + 2:
                tr[-1][3] = max(tr[-1][3], x[3])
            else:
                tr.append(list(x))
    mun[m].append([nombre, tix[t], tr])

for m in mun:
    mun[m].sort(key=lambda r: r[0])
json.dump({'t': tipos, 'm': mun}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('vías', sum(len(v) for v in mun.values()), 'municipios', len(mun), 'tramos sin sección en el mapa', sin)
