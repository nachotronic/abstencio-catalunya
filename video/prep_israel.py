"""Short de las elecciones de Israel (pieza israel-pactos-escanos-knesset): escribe shorts/israel.json.
Uso: python3 video/prep_israel.py <carpeta israel-2026 de la pieza>   (datos/localidades_2026.json, datos/distritos.json, datos/mapa.json)
Los escaños son los de la pieza (recuento provisional del 28-10 a las 14.34, el «86 %»); actualizarlos aquí si cambia el recuento."""
import collections, json, os, sys
D = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/internacional/israel-2026'
loc = json.load(open(os.path.join(D, 'datos', 'localidades_2026.json')))['localidades']
dis = json.load(open(os.path.join(D, 'datos', 'distritos.json')))
mapa = json.load(open(os.path.join(D, 'datos', 'mapa.json')))
COD = {'מחל': 'likud', 'דרך': 'yashar', 'ודם': 'lc', 'רק': 'jun', 'אמת': 'dem', 'ג': 'utj', 'ל': 'yb', 'ב': 'otz', 'שס': 'shas', 'עם': 'raam', 'ט': 'sr', 'די': 'otros', 'ך': 'otros'}
# Colores de la pieza (versión oscura de estilo.css)
COL = {'likud': '#4f86d1', 'yashar': '#62b9f2', 'lc': '#01b2ac', 'jun': '#6b6bc9', 'utj': '#4f7fae', 'yb': '#23c2eb', 'dem': '#6673f0',
       'otz': '#ff6a33', 'shas': '#8a8a8a', 'sr': '#5fb0b7', 'raam': '#2fa35f', 'otros': '#4e4a52', 'ultra': '#8a8a8a'}
ESC = {'likud': 26, 'shas': 7, 'utj': 7, 'otz': 7, 'sr': 6, 'yashar': 21, 'jun': 12, 'yb': 7, 'dem': 8, 'lc': 12, 'raam': 7}
NOM = {'likud': 'Likud', 'yashar': 'Yashar', 'sr': 'Sionismo Religioso', 'lc': 'Lista Conjunta', 'raam': "Ra'am", 'dem': 'Demócratas', 'ultra': 'Ultraortodoxos'}
NET, EIS, AR = ['likud', 'shas', 'utj', 'sr', 'otz'], ['yashar', 'jun', 'yb', 'dem'], ['lc', 'raam']
suma = lambda ks: sum(ESC[k] for k in ks)
pila = lambda ks: [[k, ESC[k]] for k in ks]

pts, gana = [], collections.Counter()
for l in sorted(loc, key=lambda l: -l['v']):
    xy = mapa['loc'].get(str(l['c']))
    if not xy or not l['v'] or not l['gan']: continue
    p = COD[l['gan']]
    p = 'ultra' if p in ('utj', 'shas') else p   # Judaísmo Unido de la Torá y Shas (Jerusalén, Bnei Brak)
    p = p if p in NOM else 'otros'
    gana[p] += 1
    pts.append([xy[0], xy[1], p, l['v']])
mil = lambda n: f'{n:,}'.replace(',', '.')
ley = [[k, f'{NOM[k]} ({mil(gana[k])})'] for k in ['yashar', 'likud', 'sr', 'lc', 'dem', 'raam', 'ultra']] + [['otros', f'Otros ({gana["otros"]})']]
ley[2][1] = ley[2][1].replace('Sionismo Religioso', 'Sionismo Rel.')
d = {x['n']: x for x in dis['distritos']}
pares = [['Israel', 'lc', dis['nacional']['ar22c'], dis['nacional']['ar']]] + [[n, 'lc', d[n]['ar22c'], d[n]['ar']] for n in ['Norte', 'Haifa', 'Sur']]

G = {'plantilla': 'guia', 'kicker': 'ISRAEL · KNESSET · 86 % ESCRUTADO', 'colores': COL,
     'fuente': ['Comité Central Electoral de Israel, recuento', 'provisional del 28-10 · Kaplan Open Source · data.gov.il'],
     'escenas': [
  {'tipo': 'hook', 'dur': 3.0, 'lineas': ['A Netanyahu', 'le faltan', [['8 escaños', 'likud']], [['para gobernar', 'likud']]]},
  {'tipo': 'hemiciclo', 'dur': 5.6, 'titulo': ['Así queda', 'la Knesset'], 'sub': '120 escaños · 86 % escrutado (provisional)',
   'partidos': [[k, k, ESC[k]] for k in AR + ['dem', 'jun', 'yb', 'yashar'] + ['likud', 'shas', 'utj', 'sr', 'otz']],
   'bloques': [['Bloque de Netanyahu', 'likud', suma(NET)], ['Bloque de Eisenkot', 'yashar', suma(EIS)], ['Partidos árabes', 'lc', suma(AR)]]},
  {'tipo': 'puntos', 'dur': 5.6, 'titulo': ['Quién gana en', 'cada localidad'], 'sub': 'Norte y centro · tamaño según votos',
   'lienzo': [mapa['w'], 400], 'origen': [0, 0], 'prov': [mapa['paises']['Israel'], mapa['paises']['Palestine']], 'pts': pts, 'radio': 11, 'alto': 840, 'revelar': 2.0, 'leyenda': ley},
  {'tipo': 'parejas', 'dur': 5.0, 'titulo': ['El voto árabe', 'sube'], 'sub': "% Lista Conjunta + Ra'am, mismas localidades", 'claves': ['2022', '2026'], 'max': 50, 'pares': pares},
  {'tipo': 'apilado', 'dur': 6.4, 'titulo': ['¿Quién suma', '61?'], 'sub': 'Escaños de cada combinación', 'max': 72, 'linea': 61, 'lineaTxt': '61, mayoría', 'alto': 124,
   'filas': [['Netanyahu y sus socios', pila(NET)], ['… + Liberman', pila(NET + ['yb'])], ["… + Ra'am (islamistas)", pila(NET + ['raam'])],
             ['Likud + Yashar + Juntos', pila(['likud', 'yashar', 'jun'])], ['Bloque de Eisenkot', pila(EIS)], ['Eisenkot + partidos árabes', pila(EIS + AR)]]},
  {'tipo': 'cierre', 'dur': 3.4, 'lineas': ['Mapa, pactos', 'y recuento'], 'ruta': '/actualidad/israel-pactos-escanos-knesset/'}]}
json.dump(G, open(os.path.join(os.path.dirname(__file__), 'shorts', 'israel.json'), 'w'), ensure_ascii=False)
print(gana, [p[1:] for p in pares], suma(NET), suma(EIS), suma(AR))
