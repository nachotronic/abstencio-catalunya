"""Media de encuestas para el motor de previsiones, y su error histórico en 2019 y 2023.

Entrada: el CSV largo que `actualizar_encuestas.py` descarga cada día del feed de Electográfica a
previsiones/datos/encuestas/generales_espana.csv (una fila por encuesta y partido) y la tabla de equivalencias
`previsiones/datos/partidos_encuestas.csv`. Se citan siempre la encuestadora y el medio original, no el agregador.

Método (deliberadamente simple y explicable):
- Fecha de cada encuesta: fin del trabajo de campo; si no consta (encuestas antiguas), publicación menos 3 días.
- Ventana de 28 días antes de la fecha de referencia; de cada encuestadora, solo su última encuesta.
- Peso = exp(-días / 10) × raíz(muestra / 1.000), con la muestra acotada entre 500 y 3.000 (sin dato, 1.000).
- Cada partido se promedia solo con las encuestas que lo publican (un hueco no es un cero).
- Error histórico: la media cinco días antes de 10N-2019 y 23J-2023 frente al resultado. Se resume como
  error ≈ c · raíz(voto), una sola constante para todos los partidos, porque dos elecciones no dan para más.

Uso:  python3 previsiones/src/encuestas.py [csv]
"""
import json, math, os, pathlib, re, sys, unicodedata
from datetime import date, timedelta

import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
CSV = RAIZ / 'previsiones/datos/encuestas/generales_espana.csv'
EQUIV = RAIZ / 'previsiones/datos/partidos_encuestas.csv'
# Encuestas de Wikipedia de los últimos 120 días sin pareja en Electográfica (sobre todo ElectoPanel), de
# cotejar_wikipedia.py. Formato ancho: una fila por encuesta, una columna por partido del modelo.
FALTAN = RAIZ / 'previsiones/datos/encuestas/faltan_en_electografica.csv'
VENTANA, VIDA_MEDIA, MUESTRA_DEF = 28, 10, 1000
# Resultados oficiales sobre voto válido (blanco incluido), con CERA, desde actualidad/src/sistema/simulador.json.
# En 2019 el espacio «SUMAR» de las encuestas es Unidas Podemos + Más País (como en la tabla de equivalencias).
RESULTADOS = {
    '2019-11-10': {'PSOE': 28.00, 'PP': 20.81, 'VOX': 15.08, 'SUMAR': 12.86 + 2.40, 'CS': 6.80},
    '2023-07-23': {'PP': 33.06, 'PSOE': 31.68, 'VOX': 12.38, 'SUMAR': 12.33},
}


def clave(nombre):
    """Nombre de encuestadora comparable: sin tildes, mayúsculas ni signos («Sigma Dos» = «SigmaDos»)."""
    s = unicodedata.normalize('NFKD', str(nombre)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', s)


def _fin_campo(txt, publicado):
    """Último día del trabajo de campo («01-08/10/2026», «29/09-01/10/2026», «07/09/2026»)."""
    m = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})\s*$', str(txt))
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            pass
    return date.fromisoformat(publicado) - timedelta(days=3)


def _muestra(txt):
    m = re.search(r'([\d.]+)\s*entrevistas', str(txt))
    n = int(m.group(1).replace('.', '')) if m else MUESTRA_DEF
    return min(max(n, 500), 3000)


def carga(csv=CSV):
    """Una fila por encuesta y partido del modelo, con fecha, encuestadora normalizada y muestra."""
    d = pd.read_csv(csv, dtype={'muestra': str, 'trabajo_campo': str})
    eq = pd.read_csv(EQUIV, dtype=str).fillna('')
    d = d.merge(eq[['nombre_encuesta', 'partido_modelo', 'desde', 'hasta']], left_on='partido', right_on='nombre_encuesta', how='left')
    sin = d[d.partido_modelo.isna()].partido.unique()
    if len(sin):
        print('Sin equivalencia (se descartan):', ', '.join(map(str, sin)))
    d = d[d.partido_modelo.notna() & ((d.desde == '') | (d.publicado >= d.desde)) & ((d.hasta == '') | (d.publicado <= d.hasta))]
    slug = d.url_electografica.str.extract(r'encuesta-(.+?)-\d{6}', expand=False)
    d['casa'] = d.encuestadora.where(d.encuestadora.notna(), slug).map(clave)
    d['fecha'] = [_fin_campo(t, p) for t, p in zip(d.trabajo_campo, d.publicado)]
    d['n'] = d.muestra.map(_muestra)
    # varias siglas del mismo espacio en una encuesta (FA + Compromís) se suman; un partido sin cifra queda fuera
    d = d[d.voto.notna()]
    return (d.groupby(['url_electografica', 'casa', 'encuestadora', 'cliente', 'fecha', 'n', 'partido_modelo'], dropna=False)
             .voto.sum().reset_index())


def con_wikipedia(d, fich=FALTAN):
    """Añade a `d` (salida de carga()) las encuestas de Wikipedia que no están en Electográfica."""
    if not pathlib.Path(fich).exists():
        print('Sin', fich, '(solo Electográfica)')
        return d
    w = pd.read_csv(fich, dtype={'muestra': str})
    partidos = [c for c in w.columns if c.isupper() and c != 'OTROS']
    w = w.assign(url_electografica=w.fuente_original, casa=w.encuestadora.map(clave),
                 fecha=pd.to_datetime(w.campo_fin).dt.date,
                 n=pd.to_numeric(w.muestra, errors='coerce').fillna(MUESTRA_DEF).clip(500, 3000).astype(int))
    w = w.melt(id_vars=['url_electografica', 'casa', 'encuestadora', 'cliente', 'fecha', 'n'], value_vars=partidos,
               var_name='partido_modelo', value_name='voto').dropna(subset=['voto'])
    return pd.concat([d, w[d.columns]], ignore_index=True)


def media(d, ref, ventana=VENTANA, excluir=()):
    """Media ponderada en la fecha `ref` (date). Devuelve ({partido: %}, encuestas usadas)."""
    x = d[(d.fecha <= ref) & (d.fecha > ref - timedelta(days=ventana)) & ~d.casa.isin([clave(e) for e in excluir])]
    ultima = x.groupby('casa').fecha.transform('max')
    x = x[x.fecha == ultima]
    x = x[x.url_electografica.isin(x.groupby('casa').url_electografica.max())]   # dos el mismo día: la última entrada
    edad = x.fecha.map(lambda f: (ref - f).days)
    x = x.assign(w=[math.exp(-a / VIDA_MEDIA) * math.sqrt(n / 1000) for a, n in zip(edad, x.n)])
    m = (x.voto * x.w).groupby(x.partido_modelo).sum() / x.w.groupby(x.partido_modelo).sum()
    usadas = (x.drop_duplicates('url_electografica')[['encuestadora', 'cliente', 'fecha', 'n', 'w', 'url_electografica']]
               .sort_values('fecha', ascending=False))
    return {k: round(float(v), 2) for k, v in m.items() if k != 'OTROS'}, usadas


def error_historico(d, dias=5):
    """Error de la media `dias` días antes de cada elección y constante c de error ≈ c·raíz(voto)."""
    filas = []
    for dia, res in RESULTADOS.items():
        m, usadas = media(d, date.fromisoformat(dia) - timedelta(days=dias))
        m['SUMAR'] = m.get('SUMAR', 0) + m.pop('PODEMOS', 0)   # en 2019 y 2023 no se presentó por separado
        for k, v in res.items():
            filas.append({'eleccion': dia, 'partido': k, 'media': m.get(k), 'resultado': v, 'error': round(m[k] - v, 2),
                          'encuestas': len(usadas)})
    e = pd.DataFrame(filas)
    c = math.sqrt((e.error ** 2 / e.resultado).mean())   # error cuadrático medio relativo a raíz(voto)
    return e, round(c, 3)


def main():
    d = carga(sys.argv[1] if len(sys.argv) > 1 else CSV)
    e, c = error_historico(d)
    d = con_wikipedia(d)
    print(e.to_string(index=False))
    print(f'c = {c}  (p. ej. error típico {c * math.sqrt(30):.1f} puntos para un partido del 30 %, {c * math.sqrt(3):.1f} para uno del 3 %)')
    hoy = date.today()
    m, usadas = media(d, hoy)
    sin_cis, _ = media(d, hoy, excluir=['CIS'])
    print('\nMedia a', hoy, {k: v for k, v in sorted(m.items(), key=lambda t: -t[1])})
    print('Sin CIS     ', {k: v for k, v in sorted(sin_cis.items(), key=lambda t: -t[1])})
    print(usadas.to_string(index=False))
    sal = pathlib.Path(os.environ.get('SALIDAS', '/mnt/project-files/previsiones/salidas'))
    sal.mkdir(parents=True, exist_ok=True)
    json.dump({'fecha': hoy.isoformat(), 'media': m, 'media_sin_cis': sin_cis, 'c_error': c,
               'error_historico': e.to_dict('records'), 'metodo': __doc__.split('Uso:')[0].strip(),
               'encuestas': [{'encuestadora': r.encuestadora, 'medio': None if pd.isna(r.cliente) else r.cliente,
                              'fin_campo': r.fecha.isoformat(), 'muestra': int(r.n), 'peso': round(r.w, 3)}
                             for r in usadas.itertuples()]},
              open(sal / f'media-encuestas-{hoy:%Y%m%d}.json', 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
