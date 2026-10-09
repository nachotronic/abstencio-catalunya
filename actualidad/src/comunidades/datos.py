"""Datos de los reportajes «Las comunidades en las urnas»: junta la historia en generales (generales.json, de
datos_generales.py) con las autonómicas de Historia Electoral (he.json, de /mnt/project-files/tendencias/comunidades,
parse_he.py). Escribe datos.json junto a este fichero. Cada partido en su color: las familias con la paleta del mapa
y los regionales con el color de su marca."""
import json, math, os, re, sys

AQUI = os.path.dirname(os.path.abspath(__file__))
HE = '/mnt/project-files/tendencias/comunidades/he.json'
COL = {'PP': '#1d84ce', 'PSOE': '#e30613', 'VOX': '#5ac035', 'SUMAR': '#a2275f', 'CS': '#eb6109', 'UPYD': '#e5007d', 'ERC': '#f5b324',
       'JUNTS': '#20c0b2', 'PNV': '#2b8a3e', 'BILDU': '#a5c400', 'BNG': '#7ab8e6', 'CC': '#f7d417', 'UCD': '#e07b22', 'CDS': '#7e57c2', 'OTROS': '#9a9a9a'}
# (expresión sobre el nombre de la fila de Historia Electoral, nombre corto, color). El orden importa: lo más concreto antes.
REGLAS = [
 (r'Populares en Libertad', 'PPL', '#6fa8dc'), (r'Independiente de Melilla', 'PIM', '#8e7cc3'),
 (r'AECAD|Ceutí por un Ayunta', 'AECAD', '#8d6e63'), (r'Nacionalista Ceut', 'PNC', '#5d7fa3'), (r'Ceuta Unida', 'Ceuta Unida', '#c9a227'),
 (r'Progreso y Futuro', 'PFC', '#2d5757'), (r'PDSC|Democr[aá]tico y Social de C', 'PDSC', '#7cb342'), (r'UDCe|Democr[aá]tica Ceut', 'UDCe', '#66bb6a'),
 (r'Alternativa Galega|En Marea', 'AGE / En Marea', '#6b2c87'),
 (r'^Vox', 'Vox', COL['VOX']), (r'Aliança Catalana', 'Aliança Catalana', '#0c3c6b'),
 (r'Uni[oó]n del Pueblo Navarro', 'UPN', '#0f4c8a'), (r'Uni[oó]n del Pueblo Leon[eé]s', 'UPL', '#b0124a'),
 (r'Unión del Pueblo Melillense', 'UPM', '#3a6fb0'),
 (r'Foro Asturias', 'Foro', '#00467f'), (r'Uni[oó]n Renovadora Asturiana', 'URAS', '#4a7ab8'),
 (r'Unidad Alavesa', 'Unidad Alavesa', '#7a9cc6'),
 (r'Uni[oó]n Dem\. Foral', 'UDF', '#6d8fc0'), (r'P\. Dem[oó]crata Popular|Partido Dem[oó]crata Popular', 'PDP', '#5f8fd0'),
 (r'P\. Dem[oó]crata Liberal', 'PDL', '#8fb3e0'),
 (r'Alianza Popular|Partido Popular|Coalici[oó]n Popular|C\.Popular|A\. P\. /', 'PP', COL['PP']),
 (r'Centristes de Catalunya|Uni[oó]n de Centro Democr[aá]tico', 'UCD', COL['UCD']),
 (r'Centro Democr[aá]tico y Social|Centre Democr[aà]tic i Social', 'CDS', COL['CDS']),
 (r'Ciudadanos|Ciutadans', 'Cs', COL['CS']), (r'Uni[oó]n,? Progreso y Democracia', 'UPyD', COL['UPYD']),
 (r'Junts pel S[ií]', 'Junts pel Sí', '#3bb6a6'), (r'Junts per Catalunya|Converg[eè]ncia i Uni[oó]|Converg[eè]ncia Democr', 'CiU / Junts', COL['JUNTS']),
 (r'Uni[oó] Democr[aà]tica de Catalunya', 'Unió', '#2a4f9c'),
 (r'Solidaritat', 'SI', '#7d9c3b'), (r'Candidatura d.Unitat Popular', 'CUP', '#e8c400'),
 (r'Esquerra Republicana', 'ERC', COL['ERC']),
 (r'Partido Socialista de Andaluc[ií]a', 'PSA', '#00843d'),
 (r'P\.S\.A\. / Partido Andalucista|P\. Andaluz', 'PSA / PA', '#00843d'),
 (r'Socialistas Independientes de Extremadura', 'SIEx', '#d4554e'),
 (r'Socialista del Pueblo de Ceuta', 'PSPC', '#d4554e'),
 (r'Socialista de Mallorca|Socialista de Menorca|Bloc per Mallorca', 'PSM / Més', '#d6a21c'),
 (r'PSG - Esquerda Galega', 'PSG-EG', '#c24d4d'),
 (r'Alternativa Socialista Gomera', 'ASG', '#9b2d30'),
 (r'Socialista|Socialistes|PSPV', 'PSOE', COL['PSOE']),
 (r'Catalunya En Com|Catalunya S[ií] Que|En Com[uú] Podem', 'En Comú / Podem', '#6b2c87'), (r'Unidas por Extremadura', 'Unidas por Extremadura', '#6b2c87'),
 (r'Elkarrekin', 'Elkarrekin Podemos', '#6b2c87'), (r'Podemos|Podem', 'Podemos', '#6b2c87'),
 (r'M[aá]s Madrid', 'Más Madrid', '#2bb38d'), (r'Sumar', 'Sumar', COL['SUMAR']),
 (r'Comprom[ií]s', 'Compromís', '#f28c28'), (r'UPV / Bloc', 'Bloc', '#e5761b'),
 (r'Uni[oó] Valenciana', 'UV', '#1f5fa8'),
 (r'Chunta', 'CHA', '#1c7a3f'), (r'PAR / Partido Aragon[eé]s', 'PAR', '#e2b80c'), (r'Arag[oó]n Existe', 'Aragón-Teruel Existe', '#0d7f8a'),
 (r'Regionalista de Cantabria', 'PRC', '#a8c11c'), (r'Uni[oó]n para el Progreso de Cantabria', 'UPCA', '#5b7fb5'),
 (r'Partiu Asturianista', 'PAS', '#2f7ab9'),
 (r'Soria', 'Soria ¡Ya!', '#2f9e62'), (r'Por [AÁ]vila', 'Por Ávila', '#2e6d4f'), (r'Soluci[oó]n Independiente', 'SI', '#8a8a8a'),
 (r'Tierra Comunera', 'Tierra Comunera', '#7d2b8b'),
 (r'Regionalista Extreme|Extremadura Unida', 'Regionalistas extremeños', '#3b8f5a'),
 (r'Riojano', 'PR', '#3f8f3a'),
 (r'Partido Cantonal', 'Cantonal', '#c94a3a'),
 (r'Coalici[oó]n Canaria|Agrupaciones Independientes|Agrupaci[oó]n Herre|Agrupaci[oó]n Gomera|Plataforma Canaria|A\.I\.L\.|Convergencia Nacionalista de Canarias|Centro C\.Nac', 'CC y predecesores', COL['CC']),
 (r'Nueva Canarias', 'NC', '#7cad2d'), (r'Asamblea Majorera', 'AM', '#2d7fb2'), (r'P\.Nacionalista Canario', 'PNC', '#e2a21a'),
 (r'UPC - Asamblea Canaria', 'UPC / ICAN', '#b5432a'),
 (r'EAJ|Nacionalista Vasco', 'PNV', COL['PNV']), (r'Eusko Alkartasuna', 'EA', '#76a83a'),
 (r'Geroa Bai|Nafarroa Bai', 'Geroa Bai / NaBai', '#e05b2b'), (r'Aralar', 'Aralar', '#a03a2e'),
 (r'Bildu|Herri Batasuna|E\.H\.A\.K|Tierras Vascas', 'HB / EH Bildu', COL['BILDU']),
 (r'Euskadiko Ezkerra', 'EE', '#d95f1e'), (r'Batzarre', 'Batzarre', '#b84a7a'), (r'Carlista', 'Carlistas', '#a51e1e'),
 (r'Convergencia Dem[oó]cratas Navarros', 'CDN', '#5a8bd6'),
 (r'Bloque Nacionalista Galego', 'BNG', COL['BNG']), (r'Coalici[oó]n Galega', 'Coalición Galega', '#3f6fb5'),
 (r'Democracia Ourensana', 'DO', '#5d9ad6'),
 (r'El Pi|Uni[oó] Mallorquina', 'UM / El Pi', '#c9b21a'), (r'Pacte Progressista', 'Pacte d’Eivissa', '#d35f5f'),
 (r'Verds|Verdes|Berdeak', 'Verdes', '#3c9a3c'),
 (r'PCE|P\.C\.A|P\.C\.E|P\. C\. E|Izquierda Unida|IU Ezker|PSUC|Iniciativa per|Esquerra Unida|PCIB|PCPV|PCC / Izquierda|Comunista|P\.T\.E', 'PCE / IU', COL['SUMAR']),
 (r'Adelante Andaluc', 'Adelante Andalucía', '#1fb07a'), (r'Por Andaluc', 'Por Andalucía', COL['SUMAR']),
 (r'Caballas', 'Caballas', '#2ba34a'), (r'Dignidad', 'MDyC', '#2f9d77'), (r'Somos Melilla', 'Somos Melilla', '#25a275'),
 (r'Coalici[oó]n por Melilla', 'CpM', '#1d8a4a'),
 (r'Nacionalista Espa[nñ]ol de Melilla', 'PNEM', '#7b5b3a'), (r'Independiente de Melilla|Populares en Libertad', 'Independientes', '#9a9a9a'),
 (r'Grupo Independiente Liberal', 'GIL', '#2c6e2c'),
]


def partido(n):
    for rx, corto, c in REGLAS:
        if re.search(rx, n, re.I):
            return corto, c
    return None, '#9a9a9a'


MUNIS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(AQUI))), 'generales-2026', 'data', 'municipios.json')


def mapa(gana_mun, M, idx):
    """Trazados SVG de los municipios de una comunidad (de generales-2026/data/municipios.json, en lon/lat*S con
    deltas) proyectados a un lienzo de 1000 px de ancho, con el ganador de cada municipio en cada elección."""
    S = M['S']
    pol = {}
    for c in gana_mun:
        if c not in idx: continue
        partes = []
        for flat in M['poly'][idx[c]]:
            x, y = flat[0], flat[1]; pts = [(x, y)]
            for k in range(2, len(flat), 2):
                x += flat[k]; y += flat[k + 1]; pts.append((x, y))
            partes.append([(a / S, b / S) for a, b in pts])
        pol[c] = partes
    lats = [p[1] for ps in pol.values() for parte in ps for p in parte]
    lons = [p[0] for ps in pol.values() for parte in ps for p in parte]
    k = math.cos(math.radians((min(lats) + max(lats)) / 2))
    x0, x1, y0, y1 = min(lons) * k, max(lons) * k, -max(lats), -min(lats)
    W = 1000; esc = W / (x1 - x0); H = round((y1 - y0) * esc)
    if H > 1100:  # comunidades muy altas: limitar el alto
        esc *= 1100 / H; W = round((x1 - x0) * esc); H = 1100
    filas = []
    for c, ps in pol.items():
        d = ''
        for parte in ps:
            q, last = [], None
            for lon, lat in parte:
                X, Y = round((lon * k - x0) * esc, 1), round((-lat - y0) * esc, 1)
                if last and abs(X - last[0]) + abs(Y - last[1]) < 1.2: continue
                q.append((X, Y)); last = (X, Y)
            if len(q) < 3: continue
            d += 'M' + 'L'.join(f'{X:g},{Y:g}' for X, Y in q) + 'Z'
        if d: filas.append([c, M['nombre'][idx[c]], d, gana_mun[c]])
    return {'w': W, 'h': H, 'm': filas}


# Correcciones a Historia Electoral comprobadas con Wikipedia (2026-10-09)
CORR = {('murcia', 1983, 'PSOE'): 26, ('murcia', 1983, None): 43, ('madrid', 2019, 'Cs'): 26}
# Madrid: HE no trae las dos elecciones de 2003 (mayo y la repetición de octubre, tras el «tamayazo»)
EXTRA = {'madrid': [(1999, '2003', {'PP': 55, 'PSOE': 47, 'PCE / IU': 9}, 111), ('2003', '2003 oct.', {'PP': 57, 'PSOE': 45, 'PCE / IU': 9}, 111)]}


# 2015: en estas provincias la suma de Podemos, IU y sus aliados superaba al ganador real
PROV_CORR = {('canarias', 'Las Palmas', '2015_12'): ('PP', 28.2), ('pais-vasco', 'Bizkaia', '2015_12'): ('PNV', 28.1),
             ('comunidad-valenciana', 'Valencia/Valéncia', '2015_12'): ('PP', 30.4),
             ('pais-vasco', 'Araba/Álava', '2015_12'): ('SUMAR', 27.0), ('pais-vasco', 'Gipuzkoa', '2015_12'): ('SUMAR', 25.3)}


# Filas que faltan en Historia Electoral: (comunidad, año) -> [(nombre corto, color, escaños)]
FALTAN = {('navarra', 1979): [('HB / EH Bildu', '#a5c400', 9), ('Amaiur', '#6d8f1f', 7), ('Nacionalistas Vascos', '#2b8a3e', 3),
                              ('Independientes Forales', '#9a9a9a', 1)]}


# Ciudades donde la suma de Podemos e IU superaba en 2015 a la primera lista real
CIU_CORR = {('pais-vasco', 'Bilbao', '2015_12'): 'PNV'}


def corregir(k, ys, filas, total):
    """Une filas con el mismo nombre, quita las vacías, aplica CORR y añade las elecciones de EXTRA."""
    for (cc, y, n), v in CORR.items():
        if cc != k or y not in ys: continue
        i = ys.index(y)
        if n is None: total[i] = v
        else: next(f for f in filas if f['n'] == n)['v'][i] = v
    for (cc, y), nuevas in FALTAN.items():
        if cc != k or y not in ys: continue
        i = ys.index(y)
        for n, c, v in nuevas:
            f = next((f for f in filas if f['n'] == n), None)
            if f is None:
                f = {'n': n, 'largo': n, 'c': c, 'v': [0] * len(ys), 'lab': [None] * len(ys)}; filas.append(f)
            f['v'][i] += v
    unidas = {}
    for f in filas:
        if f['n'] in unidas:
            g = unidas[f['n']]
            g['v'] = [a + b for a, b in zip(g['v'], f['v'])]
            g['lab'] = [a or b for a, b in zip(g['lab'], f['lab'])]
        else:
            unidas[f['n']] = f
    filas = list(unidas.values())
    for tras, lab, esc, tot in EXTRA.get(k, []):
        i = ys.index(tras) + 1
        ys.insert(i, lab); total.insert(i, tot)
        for f in filas:
            f['v'].insert(i, esc.get(f['n'], 0)); f['lab'].insert(i, None)
    return ys, [f for f in filas if any(f['v'])], total


SUMAR_CORR = json.load(open(os.path.join(AQUI, 'sumar_corr.json')))


def main():
    M = json.load(open(MUNIS))
    idx = {c: i for i, c in enumerate(M['cod'])}
    gen = json.load(open(os.path.join(AQUI, 'generales.json')))
    he = json.load(open(HE))
    els = gen['elecciones']
    out = {}
    for k, r in gen['ccaa'].items():
        h = he[k]
        fams = [f for f in COL if f != 'OTROS' and max(r['serie'][e]['pct'][f] for e in els) >= 6]
        g = {'labs': [e[:4] + ('A' if e == '2019_04' else 'N' if e == '2019_11' else '') for e in els],
             'fams': fams, 'pct': {f: [r['serie'][e]['pct'][f] if r['serie'][e]['pct'][f] >= 0.5 else None for e in els] for f in fams + ['OTROS']},
             'esp': {f: [gen['espana'][e]['pct'][f] for e in els] for f in ('PSOE', 'PP')},
             'part': [r['serie'][e]['part'] for e in els], 'part_esp': [gen['espana'][e]['part'] for e in els],
             'censo': [r['serie'][e]['censo'] for e in els]}
        prov = [{'l': p, 'g': [r['prov'][p][e]['fam'] for e in els],
                 'pct': [r['prov'][p][e]['pct'] for e in els], 'sig': [r['prov'][p][e].get('siglas') for e in els]} for p in r['provincias']]
        for q in prov:  # la familia SUMAR sumaba listas separadas: ganador real (resultado oficial, Wikipedia)
            for (cc, pv, el), (fam, pc) in PROV_CORR.items():  # noqa
                if cc == k and q['l'] == pv:
                    i = els.index(el); q['g'][i] = fam; q['pct'][i] = pc; q['sig'][i] = fam
        # autonómicas: escaños por partido
        ys = h['años']
        filas = []
        sin = []
        for f in h['escanos']:
            if f['partido'].lower().startswith('total'):
                total = [int(f['v'][str(y)]['n']) if str(y) in f['v'] else None for y in ys]; continue
            if f['partido'].lower().startswith(('altres', 'independientes')) and k != 'melilla':
                pass
            corto, c = partido(f['partido'])
            if corto is None: sin.append(f['partido'])
            filas.append({'n': corto or f['partido'], 'largo': f['partido'], 'c': c,
                          'v': [int(f['v'][str(y)]['n']) if str(y) in f['v'] else 0 for y in ys],
                          'lab': [f['v'][str(y)]['lab'] if str(y) in f['v'] else None for y in ys]})
        if sin: print(k, 'SIN COLOR:', sin, file=sys.stderr)
        ys, filas, total = corregir(k, list(ys), filas, list(total))
        pcts = {}
        partic = None
        for f in h['pct']:
            if f['partido'].lower().startswith('particip'):
                partic = [f['v'][str(y)]['n'] if str(y) in f['v'] else None for y in ys]
            pcts[f['partido']] = {y: f['v'][str(y)]['n'] for y in ys if str(y) in f['v']}
        # 2004-2023: donde las familias SUMAR u OTROS sumaban listas separadas (Podemos, IU, Compromís, Más País, regionalistas), ganador real por candidatura
        for el, cambios in SUMAR_CORR.items():
            i = els.index(el)
            for c, w in cambios.items():
                if c in r['gana_mun'] and r['gana_mun'][c][i] in ('SUMAR', 'OTROS'): r['gana_mun'][c][i] = w
            cuenta = {}
            for c in r['gana_mun']: cuenta[r['gana_mun'][c][i]] = cuenta.get(r['gana_mun'][c][i], 0) + 1
            r['munis'][el] = cuenta
            cod = {M['nombre'][idx[c]]: c for c in r['gana_mun'] if c in idx}
            for m in r['mayores_hist']:
                if m['mun'] in cod: m['g'][i] = r['gana_mun'][cod[m['mun']]][i]
        if k == 'navarra':  # 2023: UPN y PP por separado; la familia sumaba sus votos (ganador real por candidatura)
            nv = json.load(open(os.path.join(AQUI, 'navarra_2023.json')))
            for c, w in nv['gana'].items():
                if c in r['gana_mun']: r['gana_mun'][c][-1] = w
            cuenta = {}
            for c in r['gana_mun']: cuenta[r['gana_mun'][c][-1]] = cuenta.get(r['gana_mun'][c][-1], 0) + 1
            r['munis'][els[-1]] = cuenta
            prov[0]['g'][-1] = 'PSOE'; prov[0]['pct'][-1] = round(nv['psn_pct'], 1); prov[0]['sig'][-1] = 'PSN-PSOE'
            cod = {M['nombre'][idx[c]]: c for c in r['gana_mun'] if c in idx}
            for m in r['mayores_hist']:
                if m['mun'] in cod: m['g'][-1] = r['gana_mun'][cod[m['mun']]][-1]
        for m in r['mayores_hist']:
            for (cc, mun, el), fam in CIU_CORR.items():
                if cc == k and m['mun'] == mun: m['g'][els.index(el)] = fam
        out[k] = {'nombre': r['nombre'], 'gen': g, 'prov': prov, 'uni': len(r['provincias']) == 1,
                  'aut': {'labs': ys, 'filas': filas, 'total': total, 'part': partic, 'fuente': h['pagina']},
                  'munis': {e: r['munis'][e] for e in els}, 'n_munis': r['n_munis'], 'fieles': r['fieles'][:15], 'n_fieles': r['n_fieles'],
                  'n_completos': r['n_completos'], 'mayores': r['mayores'], 'mayores_hist': r['mayores_hist'], 'mapa': mapa(r['gana_mun'], M, idx)}
    json.dump(out, open(os.path.join(AQUI, 'datos.json.tmp'), 'w'), ensure_ascii=False)
    os.replace(os.path.join(AQUI, 'datos.json.tmp'), os.path.join(AQUI, 'datos.json'))
    print('ok', len(out))


if __name__ == '__main__':
    main()
