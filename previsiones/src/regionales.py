"""Señal de las encuestas de generales por comunidad o provincia («infraestatales»).

Una encuesta de Galicia o de Cataluña dice dónde sube o baja cada partido, algo que la media nacional no ve. Para cada
territorio con encuestas recientes se compara la media de esas encuestas con lo que el modelo ya da en ese territorio,
y cada lista se multiplica, en sus provincias, por (encuesta / modelo) elevado a beta (0 = no se usa; 1 = se cree la
encuesta del todo). Después el motor vuelve a clavar la media nacional, así que la señal solo mueve voto entre
territorios. Para las listas que no salen en la media nacional (ERC, PNV, BNG... en 2019 y 2023), la encuesta
regional es la única cifra: su meta nacional pasa a ser la que queda tras el ajuste.

Media regional: ventana de VENTANA días antes de la fecha de referencia; peso exp(-días / 10) × raíz(muestra / 1.000),
como la nacional; sin fecha de campo, publicación menos 3 días. Factor acotado entre 1/TOPE y TOPE.
Fuente: previsiones/datos/encuestas/encuestas_limpias.csv (actualizar_encuestas.py, columna `ambito`).
"""
import math, os, pathlib, re, unicodedata
from datetime import date, timedelta

import numpy as np
import pandas as pd

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LIMPIAS = pathlib.Path(os.environ.get('ENCUESTAS_LIMPIAS', RAIZ / 'previsiones/datos/encuestas/encuestas_limpias.csv'))
VENTANA, VIDA_MEDIA, TOPE = 90, 10, 2.0
CCAA = {'ANDALUCIA': '04 11 14 18 21 23 29 41', 'ARAGON': '22 44 50', 'ASTURIAS': '33', 'ILLES BALEARS': '07',
        'ISLAS BALEARES': '07', 'CANARIAS': '35 38', 'CANTABRIA': '39', 'CASTILLA Y LEON': '05 09 24 34 37 40 42 47 49',
        'CASTILLA-LA MANCHA': '02 13 16 19 45', 'CATALUNA': '08 17 25 43', 'COMUNITAT VALENCIANA': '03 12 46',
        'COMUNIDAD VALENCIANA': '03 12 46', 'EXTREMADURA': '06 10', 'GALICIA': '15 27 32 36', 'COMUNIDAD DE MADRID': '28',
        'REGION DE MURCIA': '30', 'NAVARRA': '31', 'PAIS VASCO': '01 20 48', 'LA RIOJA': '26', 'CEUTA': '51',
        'MELILLA': '52', 'SEVILLA': '41', 'ALMERIA': '04', 'VALENCIA-VALENCIA': '46', 'CASTELLON-CASTELLO': '12'}


def _norm(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().upper().strip()


def carga(fich=LIMPIAS):
    """Encuestas por territorio: una fila por encuesta, con `provs` (tupla de códigos) y `fecha`."""
    d = pd.read_csv(fich)
    d['amb'] = d.ambito.map(_norm)
    d = d[d.amb.isin(CCAA)].copy()
    d['provs'] = d.amb.map(lambda a: tuple(CCAA[a].split()))
    fin = pd.to_datetime(d.campo_fin, errors='coerce').dt.date
    pub = pd.to_datetime(d.publicado).dt.date - timedelta(days=3)
    d['fecha'] = fin.where(fin.notna(), pub)
    d['n'] = pd.to_numeric(d.muestra, errors='coerce').fillna(1000).clip(500, 3000)
    return d


def medias(d, ref, partidos, juntar=None):
    """{provs: {partido: cuota}} con las encuestas de cada territorio en los VENTANA días anteriores a `ref`.
    `juntar` = {partido: [columnas]} suma columnas (Sumar + Podemos en 2019 y 2023)."""
    juntar = juntar or {}
    x = d[(d.fecha <= ref) & (d.fecha > ref - timedelta(days=VENTANA))]
    out = {}
    for provs, g in x.groupby('provs'):
        w = np.array([math.exp(-(ref - f).days / VIDA_MEDIA) * math.sqrt(n / 1000) for f, n in zip(g.fecha, g.n)])
        m = {}
        for k in partidos:
            cols = [c for c in juntar.get(k, [k]) if c in g]
            if not cols:
                continue
            v = g[cols].sum(1, min_count=1)
            ok = v.notna().values
            if ok.any():
                m[k] = float((v.values[ok] * w[ok]).sum() / w[ok].sum()) / 100
        if m:
            out[provs] = m
    return out


def ajusta(c, provs, validos, med, listas, beta):
    """Multiplica cada lista en las provincias de cada territorio por (encuesta / modelo) ** beta."""
    if not beta:
        return c
    c = c.copy()
    idx = {p: i for i, p in enumerate(provs)}
    for territorio, m in med.items():
        filas = [idx[p] for p in territorio if p in idx]
        if not filas:
            continue
        w = validos[filas] / validos[filas].sum()
        for k, r in m.items():
            if k not in listas:
                continue
            j = listas.index(k)
            mod = (c[filas, j] * w).sum()
            if mod > 0 and r > 0:
                c[filas, j] *= min(max((r / mod) ** beta, 1 / TOPE), TOPE)
    return c
