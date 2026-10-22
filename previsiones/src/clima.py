"""Lluvia y temperatura del día de cada elección general (1982-2023) por municipio, y su efecto en la participación.

Datos del tiempo: NASA POWER (power.larc.nasa.gov, API diaria regional, sin clave), que sirve el reanálisis MERRA-2
en una rejilla de 0,5° × 0,625°: lluvia del día (PRECTOTCORR, mm) y temperatura máxima (T2M_MAX, °C). Empieza en 1981,
así que quedan fuera 1977 y 1979. Cada municipio toma el punto de la rejilla más cercano a su centro.
(Primero se probó ERA5 horario por Open-Meteo, pero la cuota diaria de esa API, compartida, estaba agotada.)

Uso:  python3 previsiones/src/clima.py descarga   (una vez; guarda power_elecciones.csv)
      python3 previsiones/src/clima.py efecto      (regresión de la participación)
"""
import json, pathlib, sys, time, urllib.request

import numpy as np
import pandas as pd

CARPETA = pathlib.Path('/mnt/project-files/previsiones/clima')
MUNI_WEB = pathlib.Path('/mnt/project-files/generales/web/data/municipios.json')
LARGO = pathlib.Path('/mnt/project-files/generales/datos/historico/municipios_largo.csv.gz')
FECHAS = {'1977_06': '1977-06-15', '1979_03': '1979-03-01', '1982_10': '1982-10-28', '1986_06': '1986-06-22',
          '1989_10': '1989-10-29', '1993_06': '1993-06-06', '1996_03': '1996-03-03', '2000_03': '2000-03-12',
          '2004_03': '2004-03-14', '2008_03': '2008-03-09', '2011_11': '2011-11-20', '2015_12': '2015-12-20',
          '2016_06': '2016-06-26', '2019_04': '2019-04-28', '2019_11': '2019-11-10', '2023_07': '2023-07-23'}


def municipios():
    d = json.load(open(MUNI_WEB))
    c = np.array(d['c'])
    return pd.DataFrame({'mun_code': d['cod'], 'lon': c[:, 0], 'lat': c[:, 1]})


CAJAS = [(-9.5, 35.5, 0.0, 44.0), (0.0, 35.0, 4.5, 43.0), (-18.5, 27.5, -13.0, 29.5), (-5.5, 35.0, -2.5, 37.0)]   # la última, Ceuta y Melilla (mínimo 2° de latitud)
PARAMETROS = {'PRECTOTCORR': 'lluvia_dia', 'T2M_MAX': 'temp_max'}


def descarga():
    sal = CARPETA / 'power_elecciones.csv'
    hechas = set(pd.read_csv(sal).eleccion) if sal.exists() else set()
    for el, dia in FECHAS.items():
        if el in hechas or dia < '1981-01-01':
            continue
        puntos = {}
        for par, col in PARAMETROS.items():
            for lo0, la0, lo1, la1 in CAJAS:
                url = (f'https://power.larc.nasa.gov/api/temporal/daily/regional?parameters={par}&community=AG'
                       f'&longitude-min={lo0}&longitude-max={lo1}&latitude-min={la0}&latitude-max={la1}'
                       f'&start={dia.replace("-", "")}&end={dia.replace("-", "")}&format=JSON')
                r = None
                for intento in range(5):
                    try:
                        r = json.load(urllib.request.urlopen(url, timeout=120))
                        print(el, par, lo0, len(r['features']), flush=True)
                        break
                    except Exception as e:
                        print('reintento', el, par, e)
                        time.sleep(20 * (intento + 1))
                if r is None:
                    raise RuntimeError(f'Sin datos de NASA POWER: {el} {par} {lo0}')
                for f in r['features']:
                    lon, lat = f['geometry']['coordinates'][:2]
                    v = list(f['properties']['parameter'][par].values())[0]
                    puntos.setdefault((round(lat, 3), round(lon, 3)), {})[col] = None if v == -999 else v
        filas = [{'eleccion': el, 'lat': a, 'lon': b, **v} for (a, b), v in puntos.items()]
        pd.DataFrame(filas).to_csv(sal, mode='a', header=not sal.exists(), index=False)
        print(el, 'hecho', len(filas))


def asigna(m, t):
    """Punto de la rejilla más cercano a cada municipio (la rejilla es la misma en todas las elecciones)."""
    g = t[['lat', 'lon']].drop_duplicates().values
    dist = (m.lat.values[:, None] - g[None, :, 0]) ** 2 + ((m.lon.values[:, None] - g[None, :, 1]) * np.cos(np.radians(40))) ** 2
    j = dist.argmin(1)
    return m.assign(celda_lat=g[j, 0], celda_lon=g[j, 1])


def panel():
    """Municipio × elección general: participación, voto del PP y del PSOE sobre votantes, y el tiempo de su celda."""
    t = pd.read_csv(CARPETA / 'power_elecciones.csv').rename(columns={'lat': 'celda_lat', 'lon': 'celda_lon'})
    m = asigna(municipios(), t.rename(columns={'celda_lat': 'lat', 'celda_lon': 'lon'}))
    d = pd.read_csv(LARGO, dtype={'mun_code': str})
    d = d[(d.tipo == 'generales') & d.eleccion.isin(FECHAS) & (d.censo >= 100) & (d.votantes > 0)]
    d = d.merge(m, on='mun_code').merge(t, on=['eleccion', 'celda_lat', 'celda_lon'])
    d['part'] = d.votantes / d.censo * 100
    d = d[(d.part > 20) & (d.part <= 100)]
    for k in ('PP', 'PSOE'):
        d[k.lower()] = d[k].fillna(0) / d.votantes * 100
    d['prov'] = d.mun_code.str[:2]
    d['llueve'] = (d.lluvia_dia >= 1).astype(float)   # al menos 1 mm en el día
    d['log_lluvia'] = np.log1p(d.lluvia_dia)
    return d


def fe(d, y, xs, grupos, peso):
    """MCO ponderado con efectos fijos (proyecciones alternas) y errores agrupados por celda × elección."""
    cols = [y] + xs
    Z = d[cols].astype(float).copy()
    w = d[peso].values.astype(float)
    for _ in range(100):
        antes = Z.values.copy()
        for g in grupos:
            mg = (Z.mul(w, axis=0)).groupby(d[g].values).transform('sum').div(pd.Series(w).groupby(d[g].values).transform('sum').values, axis=0)
            Z = Z - mg
        if np.abs(Z.values - antes).max() < 1e-8:
            break
    Y, X = Z[y].values, Z[xs].values
    XtWX = X.T @ (X * w[:, None])
    b = np.linalg.solve(XtWX, X.T @ (w * Y))
    u = Y - X @ b
    cl = (d.celda_lat.astype(str) + d.celda_lon.astype(str) + d.eleccion).values
    S = pd.DataFrame(X * (w * u)[:, None]).groupby(cl).sum().values
    inv = np.linalg.inv(XtWX)
    se = np.sqrt(np.diag(inv @ (S.T @ S) @ inv))
    return dict(zip(xs, b)), dict(zip(xs, se)), len(np.unique(cl))


def efecto():
    d = panel()
    d['w'] = d.censo
    d['prov_el'] = d.prov + d.eleccion
    filas = []
    for y in ('part', 'pp', 'psoe'):
        for nombre, grupos in (('municipio + provincia×elección', ['mun_code', 'prov_el']),
                               ('municipio + elección', ['mun_code', 'eleccion'])):
            for x in ('llueve', 'log_lluvia'):
                b, se, ncl = fe(d, y, [x, 'temp_max'], grupos, 'w')
                filas.append({'variable': y, 'efectos_fijos': nombre, 'lluvia': x, 'coef': round(b[x], 3),
                              'ee': round(se[x], 3), 'temp_coef': round(b['temp_max'], 3), 'temp_ee': round(se['temp_max'], 3),
                              'observaciones': len(d), 'grupos_ee': ncl})
    r = pd.DataFrame(filas)
    r.to_csv(CARPETA / 'efecto_lluvia.csv', index=False)
    print(r.to_string(index=False))
    print('\nLluvia por elección (% del censo en municipios con ≥ 1 mm en el día):')
    print(d.groupby('eleccion').apply(lambda x: round((x.llueve * x.censo).sum() / x.censo.sum() * 100, 1)).to_string())


if __name__ == '__main__':
    {'descarga': descarga, 'efecto': efecto}[sys.argv[1]]()
