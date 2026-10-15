"""Cifras de la pieza del Senado (julio de 2023): reparto de senadores frente al voto, electores por senador
y panachage (cuántos candidatos marca cada votante y si mezcla partidos).
Uso: python3 actualidad/src/senado/analizar.py <carpeta con los .DAT descomprimidos de 03202307_MESA.zip>
Lee senado_2023.csv (de leer.py) y ../sistema/cifras.json (voto al Congreso); escribe cifras_senado.json."""
import collections, csv, json, pathlib, sys

AQUI = pathlib.Path(__file__).resolve().parent
D = pathlib.Path(sys.argv[1])
SISTEMA = json.loads((AQUI.parent / 'sistema' / 'cifras.json').read_text())

FAM = {'PP': 'PP', 'PSOE': 'PSOE', 'PSC': 'PSOE', 'PSE-EE (PSOE)': 'PSOE', 'PSdeG-PSOE': 'PSOE', 'PSN-PSOE': 'PSOE',
       'PSIB-PSOE': 'PSOE', 'PSOE-SUMAR-EUIB-ARA EIVISSA': 'Ara Eivissa', 'VOX': 'Vox', 'SUMAR': 'Sumar', 'SUMAR - ECP': 'Sumar',
       'SUMAR - COMPROMÍS': 'Sumar', 'SUMAR ARAGÓN': 'Sumar', 'MÉS PER MALLORCA-SUMAR': 'Sumar', 'MÉS PER MENORCA-SUMAR': 'Sumar',
       'ERC-ESQUERRES PER LA INDEPENDÈNCIA': 'ERC', 'ERC': 'ERC', 'JxCAT - JUNTS': 'Junts', 'EH BILDU-INDEPENDENTZIA EZKERRETIK': 'EH Bildu',
       'EAJ-PNV': 'PNV', 'B.N.G.': 'BNG', 'U.P.N.': 'UPN', 'CCa': 'CC', 'ASG': 'ASG', 'A.H.I.': 'AHI', 'EXISTE': 'Teruel Existe',
       'SY': 'Soria ¡Ya!', 'U.P.L.': 'UPL', 'PACMA': 'PACMA'}
fam = lambda s: FAM.get(s, s)

# Datos globales por circunscripción (fichero 07): censo, votos en blanco, nulos y papeletas a candidaturas
glob = {}
for l in (D / '07032307.DAT').read_text(encoding='latin-1').splitlines():
    prov, dist = l[11:13], l[13]
    if prov == '99' or int(l[149:155]) == 0:
        continue
    glob[(prov, dist)] = dict(nombre=l[14:64].strip(), censo=int(l[85:93]), blancos=int(l[125:133]), nulos=int(l[133:141]),
                              papeletas=int(l[141:149]), escanos=int(l[149:155]))

cand = list(csv.DictReader(open(AQUI / 'senado_2023.csv', encoding='utf-8')))
for c in cand:
    c['votos'] = int(c['votos']); c['orden_papeleta'] = int(c['orden_papeleta']); c['fam'] = fam(c['siglas'])
por_circ = collections.defaultdict(list)
for c in cand:
    por_circ[(c['prov'], c['distrito'])].append(c)

# Electos: los más votados de cada circunscripción (voto limitado). El fichero 04 de Interior no marca a Manuel Blasco
# (PP, Teruel), tercero más votado; el resultado oficial (PP 120) sí lo cuenta, así que se usa el orden de votos.
circs = {}
for k, v in sorted(por_circ.items()):
    g = glob[k]
    v.sort(key=lambda c: -c['votos'])
    for i, c in enumerate(v):
        c['electo'] = i < g['escanos']
    marcas = sum(c['votos'] for c in v)
    electos = collections.Counter(c['fam'] for c in v if c['electo'])
    # Listas de cada partido en la circunscripción, por orden en la papeleta
    listas = collections.defaultdict(list)
    for c in sorted(v, key=lambda c: c['orden_papeleta']):
        listas[c['candidatura']].append(c)
    circs['%s%s' % k] = dict(prov=k[0], distrito=k[1], nombre=g['nombre'], escanos=g['escanos'], censo=g['censo'],
                             papeletas=g['papeletas'], blancos=g['blancos'], marcas=marcas,
                             marcas_por_papeleta=round(marcas / g['papeletas'], 3),
                             electos=dict(electos.most_common()),
                             listas=[dict(fam=l[0]['fam'], siglas=l[0]['siglas'], votos=[c['votos'] for c in l],
                                          nombres=['%s %s' % (c['nombre'], c['apellido1']) for c in l],
                                          electos=[c['electo'] for c in l]) for l in listas.values()])

electos = collections.Counter(c['fam'] for c in cand if c['electo'])
total = sum(electos.values())
congreso = {p['partido']: p for p in SISTEMA['2023_07']['partidos']}
# Voto al Senado de cada partido: su candidato más votado en cada circunscripción (aproximación habitual)
mejor = collections.Counter()
for v in por_circ.values():
    vistos = set()
    for c in v:  # ya ordenados por votos
        if c['candidatura'] not in vistos:
            vistos.add(c['candidatura']); mejor[c['fam']] += c['votos']
papeletas = sum(g['papeletas'] for g in glob.values())
partidos = []
for p, n in electos.most_common():
    partidos.append(dict(partido=p, senadores=n, pct_senadores=round(100 * n / total, 2),
                         pct_congreso=congreso.get(p, {}).get('pct'), escanos_congreso=congreso.get(p, {}).get('escanos'),
                         pct_senado_mejor=round(100 * mejor[p] / papeletas, 2)))
for p in ('Vox', 'Sumar'):
    partidos.append(dict(partido=p, senadores=0, pct_senadores=0.0, pct_congreso=congreso[p]['pct'],
                         escanos_congreso=congreso[p]['escanos'], pct_senado_mejor=round(100 * mejor[p] / papeletas, 2)))

# Panachage: votantes que no marcan a todos los candidatos de un mismo partido
prov4 = [c for c in circs.values() if c['escanos'] == 4]
mezcla = []
for c in prov4:
    top = c['listas']
    patron = sorted(c['electos'].values(), reverse=True)
    if patron != [3, 1]:
        mezcla.append(dict(nombre=c['nombre'], electos=c['electos']))
# Caída dentro de cada lista de tres: 3.º frente al 1.º
caidas = []
for c in prov4:
    for l in c['listas']:
        if len(l['votos']) == 3 and l['fam'] in ('PP', 'PSOE', 'Vox', 'Sumar'):
            caidas.append(dict(circ=c['nombre'], fam=l['fam'], primero=l['votos'][0], tercero=l['votos'][2],
                               caida_pct=round(100 * (1 - l['votos'][2] / l['votos'][0]), 2), nombres=l['nombres'],
                               votos=l['votos'], electos=l['electos']))
decrece = sum(all(a >= b for a, b in zip(l['votos'], l['votos'][1:])) for c in circs.values() for l in c['listas'] if len(l['votos']) > 1)
n_listas = sum(1 for c in circs.values() for l in c['listas'] if len(l['votos']) > 1)
# Cruces: candidato electo con menos votos que un no electo de otro partido no existe por definición; buscamos
# circunscripciones donde el 4.º electo (minoría) gana por menos votos al 3.º del partido mayoritario o al revés
filo = []
for c in prov4:
    todos = sorted([(v, l['fam'], n, e) for l in c['listas'] for v, n, e in zip(l['votos'], l['nombres'], l['electos'])], reverse=True)
    ult, prim = todos[3], todos[4]
    filo.append(dict(circ=c['nombre'], ultimo=ult[2], ultimo_fam=ult[1], ultimo_votos=ult[0], siguiente=prim[2],
                     siguiente_fam=prim[1], siguiente_votos=prim[0], margen=ult[0] - prim[0]))
filo.sort(key=lambda f: f['margen'])

marcas_tot = sum(c['marcas'] for c in prov4); pap_tot = sum(c['papeletas'] for c in prov4)
cens = {c['nombre']: c['censo'] / c['escanos'] for c in circs.values() if c['escanos'] == 4}
out = dict(total=total, electos=dict(electos.most_common()), partidos=partidos, papeletas=papeletas,
           marcas_por_papeleta_prov=round(marcas_tot / pap_tot, 3),
           marcas_por_papeleta=sorted(((c['nombre'], c['marcas_por_papeleta']) for c in prov4), key=lambda x: x[1]),
           patron_no_3_1=mezcla, caidas=sorted(caidas, key=lambda x: -x['caida_pct']), listas_decrecientes=[decrece, n_listas],
           filo=filo[:12], electores_por_senador=sorted(cens.items(), key=lambda x: x[1]),
           circunscripciones=circs)
(AQUI / 'cifras_senado.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(json.dumps({k: out[k] for k in ('total', 'electos', 'partidos', 'marcas_por_papeleta_prov', 'patron_no_3_1', 'listas_decrecientes')}, ensure_ascii=False, indent=0))
print(out['marcas_por_papeleta'][:6], out['marcas_por_papeleta'][-6:])
print(out['caidas'][:6]); print(out['filo'][:8]); print(out['electores_por_senador'][:3], out['electores_por_senador'][-3:])
