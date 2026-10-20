"""Lee los ficheros de Infoelectoral del Senado de julio de 2023 (03202307_MESA.zip) y escribe senado_2023.csv:
un registro por candidato y circunscripción con sus votos (con CERA) y si salió elegido.

Uso: python3 actualidad/src/senado/leer.py <carpeta con los .DAT descomprimidos>
"""
import csv, pathlib, sys

D = pathlib.Path(sys.argv[1])
AQUI = pathlib.Path(__file__).resolve().parent
lat = lambda f: (D / f).read_text(encoding='latin-1').splitlines()

cand = {}
for l in lat('03032307.DAT'):
    cand[l[8:14]] = (l[14:64].strip(), l[64:214].strip())

personas = {}
for l in lat('04032307.DAT'):
    if l[24] != 'T':
        continue
    cod = l[9:11] + l[11] + l[12:15]        # provincia + distrito + orden en la circunscripción
    personas[cod] = dict(prov=l[9:11], distrito=l[11], orden_papeleta=int(l[12:15]), candidatura=l[15:21],
                         orden_lista=int(l[21:24]), nombre=l[25:50].strip(), ap1=l[50:75].strip(), ap2=l[75:100].strip(),
                         sexo=l[100], elegido=l[119] == 'S')

# Fichero 08: votos de cada senador en su circunscripción (provincia o isla), con CERA
votos = {}
for l in lat('08032307.DAT'):
    prov, dist, cod = l[11:13], l[13], l[14:20]
    if prov == '99' or cod not in personas:
        continue
    votos[cod] = int(l[20:28])

with open(AQUI / 'senado_2023.csv', 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(['codigo', 'prov', 'distrito', 'orden_papeleta', 'candidatura', 'siglas', 'orden_lista', 'nombre', 'apellido1', 'apellido2', 'sexo', 'votos', 'elegido'])
    for cod, p in sorted(personas.items()):
        w.writerow([cod, p['prov'], p['distrito'], p['orden_papeleta'], p['candidatura'], cand[p['candidatura']][0], p['orden_lista'],
                    p['nombre'], p['ap1'], p['ap2'], p['sexo'], votos.get(cod), int(p['elegido'])])
print(len(personas), 'candidatos;', sum(p['elegido'] for p in personas.values()), 'elegidos;', sum(v is None for v in [votos.get(c) for c in personas]), 'sin votos')
