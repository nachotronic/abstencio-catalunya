"""¿Cuánto se equivoca la media de encuestas según los días que faltan? Tres fuentes, la misma medida.

El motor usa error ≈ c·raíz(voto en puntos). Hasta ahora c salía de dos generales (10N-2019 y 23J-2023): muy poco.
Aquí se mide c por distancia a la elección con:
  1. Generales españolas 2019 y 2023 (encuestas.py).
  2. Autonómicas españolas 2015-2026: encuestas de Electográfica (etiquetas A_*) frente al resultado de cada
     elección (ficha de Wikipedia, porcentaje sobre válidos). Solo PP, PSOE, Vox y Cs: las familias que se pueden
     emparejar sin ambigüedad entre encuesta y resultado (Navarra queda fuera para el PP por UPN y Navarra Suma).
  3. Jennings y Wlezien (2018, Nature Human Behaviour; Dataverse doi:10.7910/DVN/8421DX, CC0): media diaria de
     encuestas en elecciones legislativas de 44 países, 1942-2017.
La media de las autonómicas es la misma de encuestas.py (última de cada casa en 28 días, peso por antigüedad y muestra).
Partidos con al menos un 3 % de voto.

Uso:  python3 previsiones/src/error_encuestas.py
Escribe /mnt/project-files/previsiones/error_encuestas/{error_por_distancia.csv,errores_autonomicas.csv}.
"""
import glob, json, math, pathlib, re, sys, unicodedata
from datetime import date, timedelta

import numpy as np
import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import encuestas  # noqa: E402

ENC_AUT = pathlib.Path('/mnt/project-files/previsiones/encuestas/autonomicas/encuestas_autonomicas.json')
WIKI = pathlib.Path('/mnt/project-files/tendencias/comunidades/wiki')
JW = pathlib.Path('/mnt/project-files/previsiones/encuestas/jennings_wlezien/jw_polls.csv.gz')
SALIDA = pathlib.Path('/mnt/project-files/previsiones/error_encuestas')
DIAS = [3, 7, 14, 21, 28, 38, 50]
MIN_VOTO = 3.0
MESES = {m: i + 1 for i, m in enumerate(['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
                                         'septiembre', 'octubre', 'noviembre', 'diciembre'])}
# ámbito de Electográfica -> palabra del título del artículo de Wikipedia
CCAA = {'ANDALUCÍA': 'Andalucía', 'ARAGÓN': 'Aragón', 'ASTURIAS': 'Asturias', 'ILLES BALEARS': 'Islas Baleares',
        'CANARIAS': 'Canarias', 'CANTABRIA': 'Cantabria', 'CASTILLA-LA MANCHA': 'Castilla-La Mancha',
        'CASTILLA Y LEÓN': 'Castilla y León', 'CATALUÑA': 'Cataluña', 'COMUNITAT VALENCIANA': 'Cortes Valencianas',
        'COMUNIDAD VALENCIANA': 'Cortes Valencianas', 'EXTREMADURA': 'Extremadura', 'GALICIA': 'Galicia',
        'COMUNIDAD DE MADRID': 'Madrid', 'REGIÓN DE MURCIA': 'Murcia', 'NAVARRA': 'Navarra', 'PAÍS VASCO': 'Vasco',
        'LA RIOJA': 'La Rioja'}


def norma(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper()
    return re.sub(r'\s+', ' ', s).strip()


def familia(etiqueta, ccaa=''):
    """PP, PSOE, VOX o CS; None si la etiqueta es de otro partido o una coalición ambigua."""
    e = norma(etiqueta)
    if re.match(r"^(VOX)\b", e):
        return 'VOX'
    if re.match(r"^(CS|C'S|CIUDADANOS)\b", e):
        return 'CS'
    if 'Navarra' not in ccaa and (re.match(r'^PP(\b|[A-Z]{1,3}\b|-)', e) or e.startswith('PARTIDO POPULAR')):
        return 'PP'
    if (re.match(r'^(PSOE|PSC|PSPV|PSIB|PSDEG|PSE|PSM|PSN|PSCM|PSRM|FSA|PSA)\b', e) or 'PSOE' in e
            or e.startswith(('PARTIDO SOCIALISTA', 'PARTIT SOCIALISTA', 'PARTIT DELS SOCIALISTES', 'PARTIDO DE LOS SOCIALISTAS'))):
        return 'PSOE'
    return None


def resultados():
    """{(clave de comunidad, fecha): {familia: % sobre válidos}} desde las fichas de Wikipedia (2015 en adelante)."""
    out = {}
    for f in glob.glob(str(WIKI / '*.txt')):
        if int(re.search(r'(\d{4})\.txt$', f).group(1)) < 2015:
            continue
        s = open(f).read()
        m = re.search(r'fecha_elecci[oó]n\s*=\s*[^|\n]*?(\d{1,2}) de (\w+) de (\d{4})', s)
        if not m:
            m2 = re.search(r'fecha_elecci[oó]n\s*=[^|\n]*?\{\{[Ff]echa\|(\d{1,2})\|(\d{1,2})\|(\d{4})', s)
            if not m2:
                continue
            dia = date(int(m2.group(3)), int(m2.group(2)), int(m2.group(1)))
        else:
            dia = date(int(m.group(3)), MESES[m.group(2).lower()], int(m.group(1)))
        clave = next((v for v in CCAA.values() if v in pathlib.Path(f).name), None)
        if not clave or dia > date.today():
            continue
        # solo la primera aparición de cada número (la ficha); más abajo hay tablas con la misma clave
        partidos, pct = {}, {}
        for n, p in re.findall(r'\|\s*partido(\d+)\s*=\s*((?:\[\[[^\]]*\]\]|[^|\n])*)', s):
            partidos.setdefault(n, p)
        for n, p in re.findall(r'porcentaje(\d+)\s*=\s*([\d.,]+)', s):
            pct.setdefault(n, p)
        r = {}
        for n, p in partidos.items():
            p = re.sub(r'\[\[(?:[^|\]]*\|)?([^\]]*)\]\]', r'\1', p)
            p = re.split(r'<ref|\{\{', p)[0].strip()
            k = familia(p, clave)
            if k and n in pct:
                r[k] = r.get(k, 0) + float(pct[n].replace(',', '.'))
        if r:
            out[(clave, dia)] = r
    return out


def encuestas_autonomicas():
    """Formato largo compatible con encuestas.media(), con la comunidad y la familia de cada cifra."""
    filas = []
    for e in json.load(open(ENC_AUT)):
        amb = norma(e['ambito'].split('(')[0].split('▪')[0].split(',')[0])
        clave = next((v for k, v in CCAA.items() if norma(k) == amb), None)
        if not clave or 'Generales' in e['titulo'] or 'Municip' in e['ambito']:
            continue
        f = e['ficha']
        fecha = encuestas._fin_campo(f.get('Fecha realización', ''), e['publicado'])
        for p, v in e['voto'].items():
            k = familia(p, clave)
            if k and v:
                filas.append({'ccaa': clave, 'url_electografica': e['url'], 'encuestadora': f.get('Encuestadora'),
                              'cliente': f.get('Cliente'), 'casa': encuestas.clave(f.get('Encuestadora') or e['titulo']),
                              'fecha': fecha, 'n': encuestas._muestra(f.get('Muestra', '')), 'partido_modelo': k, 'voto': v})
    d = pd.DataFrame(filas)
    # dos etiquetas de la misma familia en una encuesta (PSOE y PSC, por ejemplo) se suman, como en encuestas.carga()
    return d.groupby(['ccaa', 'url_electografica', 'casa', 'encuestadora', 'cliente', 'fecha', 'n', 'partido_modelo'],
                     dropna=False).voto.sum().reset_index()


def errores_autonomicas():
    R, d = resultados(), encuestas_autonomicas()
    filas = []
    for (clave, dia), res in sorted(R.items(), key=lambda t: t[0][1]):
        x = d[d.ccaa == clave]
        for h in DIAS:
            m, usadas = encuestas.media(x, dia - timedelta(days=h))
            for k, v in res.items():
                if k in m and v >= MIN_VOTO:
                    filas.append({'fuente': 'autonómicas', 'eleccion': f'{clave} {dia}', 'dias': h, 'partido': k,
                                  'media': m[k], 'resultado': v, 'error': m[k] - v, 'encuestas': len(usadas)})
    return pd.DataFrame(filas)


def errores_generales():
    d = encuestas.carga()
    filas = []
    for h in DIAS:
        e, _ = encuestas.error_historico(d, h)
        for r in e.itertuples():
            if r.media is not None and r.resultado >= MIN_VOTO:
                filas.append({'fuente': 'generales', 'eleccion': r.eleccion, 'dias': h, 'partido': r.partido,
                              'media': r.media, 'resultado': r.resultado, 'error': r.error, 'encuestas': r.encuestas})
    return pd.DataFrame(filas)


def errores_jw():
    j = pd.read_csv(JW)
    j = j[(j.election == 'Legislative') & (j.vote_ >= MIN_VOTO)]
    j['eleccion'] = j.country + ' ' + j.elecdate.astype(str).str[:10]
    filas = []
    for h in DIAS:   # el día disponible más cercano a h (±3 días) de cada elección
        x = j[(j.daysbeforeED - h).abs() <= 3].copy()
        x['dist'] = (x.daysbeforeED - h).abs()
        x = x[x.dist == x.groupby('eleccion').dist.transform('min')].drop_duplicates(['eleccion', 'partyid'])
        filas.append(pd.DataFrame({'fuente': 'internacional', 'eleccion': x.eleccion, 'dias': h, 'partido': x.partyid.astype(str),
                                   'media': x.poll_, 'resultado': x.vote_, 'error': x.poll_ - x.vote_, 'encuestas': x.npolls}))
    return pd.concat(filas)


def c_de(e):
    """c de error ≈ c·raíz(voto), con su intervalo bootstrap del 90 % remuestreando elecciones (no partidos)."""
    c = math.sqrt((e.error ** 2 / e.resultado).mean())
    rng = np.random.default_rng(1)
    els = e.eleccion.unique()
    g = {k: v for k, v in e.groupby('eleccion')}
    boot = []
    for _ in range(500):
        b = pd.concat([g[k] for k in rng.choice(els, len(els))])
        boot.append(math.sqrt((b.error ** 2 / b.resultado).mean()))
    return c, *np.percentile(boot, [5, 95])


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    aut = errores_autonomicas()
    aut.to_csv(SALIDA / 'errores_autonomicas.csv', index=False)
    gen = errores_generales()
    # «españa» = generales + autonómicas juntas: la que usa el motor (25-30 elecciones por distancia)
    todo = pd.concat([gen, aut, errores_jw(), pd.concat([gen, aut]).assign(fuente='españa')])
    filas = []
    for (fuente, h), e in todo.groupby(['fuente', 'dias']):
        c, lo, hi = c_de(e)
        filas.append({'fuente': fuente, 'dias': h, 'c': round(c, 3), 'c_p5': round(lo, 3), 'c_p95': round(hi, 3),
                      'elecciones': e.eleccion.nunique(), 'cifras': len(e),
                      'error_medio_abs': round(e.error.abs().mean(), 2), 'sesgo_medio': round(e.error.mean(), 2)})
    t = pd.DataFrame(filas)
    t.to_csv(SALIDA / 'error_por_distancia.csv', index=False)
    print(t.pivot_table(index='dias', columns='fuente', values=['c', 'elecciones']).to_string())
    # sesgo medio por partido (media − resultado) en España a 38 días, con intervalo bootstrap por elecciones
    e = pd.concat([gen, aut])
    e = e[e.dias == 38]
    rng, filas = np.random.default_rng(1), []
    for p, x in e.groupby('partido'):
        x = x.set_index('eleccion')
        els = x.index.unique()
        b = [x.loc[rng.choice(els, len(els))].error.mean() for _ in range(1000)]
        filas.append({'partido': p, 'sesgo': round(x.error.mean(), 2), 'p5': round(np.percentile(b, 5), 2),
                      'p95': round(np.percentile(b, 95), 2), 'elecciones': len(els)})
    s = pd.DataFrame(filas)
    s.to_csv(SALIDA / 'sesgo_por_partido_38dias.csv', index=False)
    print('\nSesgo por partido a 38 días (media − resultado, puntos):')
    print(s.to_string(index=False))


if __name__ == '__main__':
    main()
