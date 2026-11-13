"""«El CIS, provincia a provincia» (13-11-2026): horquillas de escaños por provincia del preelectoral del CIS (estudio
3584) frente al reparto central del modelo de mapaelectoral.es/encuestas y a los escaños de julio de 2023.

Horquillas del CIS (P5-P95) y entrevistas por provincia: actualidad/src/resumenes/datos/cis_3584_provincias.json, copiado
del PDF «3584_estimacion» y del Excel «3584-multi_A» de cis.es (hoja «Provincia», fila (N)).
Modelo: previsiones/datos/publico/escenario-base.json (última versión del histórico; ya incluye este estudio del CIS).
Escaños de 2023: D'Hondt con barrera del 3 % sobre los votos oficiales por provincia (actualidad/src/sistema/simulador.json).
Comparación por espacio: el Frente Amplio del CIS, Compromís (Alicante, Castellón y Valencia), Ara Més-Front Ampli
(Baleares) y la Unidad del Pueblo Canario (Las Palmas y Santa Cruz de Tenerife) frente a «Sumar» del modelo y de 2023;
ERC-Podemos frente a ERC; en Navarra, el PP del CIS frente a UPN-PP del modelo y UPN + PP de 2023.
Uso, desde la raíz: python3 actualidad/src/resumenes/cis_provincias.py
"""
import unicodedata
import json
import math
import sys

from comun import BASE, RAIZ, esc, figura, mapa_provincias, n, pieza

sys.path.insert(0, str(RAIZ / 'src'))
from territorios_rutas import PROV_NOMBRE  # noqa: E402

SLUG = 'cis-preelectoral-provincias-29n'
A = BASE + 'actualidad/'
L = lambda s, t: f'<a href="{A}{s}/">{t}</a>'
p = lambda v: n(v, 1)
PDF = 'https://www.cis.es/documents/d/guest/3584_estimacion-pdf'
XLSX = 'https://www.cis.es/documents/d/guest/3584-multi_A-xlsx'
AVANCE = 'https://www.cis.es/es/w/avance-de-resultados-del-estudio-3584-preelectoral-elecciones-generales-2026-'
NUM = {1: 'una', 2: 'dos', 3: 'tres', 4: 'cuatro', 5: 'cinco', 6: 'seis', 7: 'siete', 8: 'ocho', 9: 'nueve', 10: 'diez', 11: 'once', 12: 'doce'}
NOM = dict(PROV_NOMBRE)
CORTO = {'Santa Cruz de Tenerife': 'S. C. de Tenerife', 'Alicante/Alacant': 'Alicante', 'Valencia/València': 'Valencia',
         'Castellón/Castelló': 'Castellón', 'Araba/Álava': 'Álava', 'Illes Balears': 'Baleares', 'Balears, Illes': 'Baleares'}
nom = lambda c: CORTO.get(NOM[c], NOM[c])

# ---------- CIS ----------
DC = json.load(open(RAIZ / 'actualidad/src/resumenes/datos/cis_3584_provincias.json'))['provincias']
assert len(DC) == 52 and sum(v['entrevistas'] for v in DC.values()) == 45074
ESP = {'PSOE': 'PSOE', 'PP': 'PP', 'Vox': 'Vox', 'Frente Amplio': 'Sumar', 'Compromís': 'Sumar', 'Ara Més-Front Ampli': 'Sumar', 'UPC': 'Sumar',
       'ERC-Podemos': 'ERC', 'Junts': 'Junts', 'BNG': 'BNG', 'PNV': 'PNV', 'EH Bildu': 'EH Bildu', 'Podemos': 'Podemos', 'Adelante Andalucía': 'Adelante Andalucía'}
# el espacio de Sumar va con un solo nombre por provincia en el CIS
for c, v in DC.items():
    assert sum(1 for k, (a, b) in v['escanos'].items() if ESP[k] == 'Sumar' and b > 0) <= 1, c
CIS = {}
for c, v in DC.items():
    s = {}
    for k, (a, b) in v['escanos'].items():
        x = s.setdefault(ESP[k], [0, 0]); x[0] += a; x[1] += b
    CIS[c] = s

# ---------- Modelo ----------
MOD = json.load(open(RAIZ / 'previsiones/datos/publico/escenario-base.json'))
HIST = sorted((RAIZ / 'previsiones/datos/publico/historico').glob('*.json'))[-1]
assert json.load(open(HIST))['escenario'] == MOD
_a, _m, _d, _hm = HIST.stem.split('-')
VERSION = f'{int(_hm[:2])}.{_hm[2:]} del {int(_d)} de noviembre de {_a}'


def reparto_central(v):
    """Reparto central de la provincia, el que publican /encuestas/ y /encuestas/<provincia>/ (encuestas/src/construir.py,
    reparto_provincia): las medianas de cada lista, ajustadas con el voto mediano para que sumen los escaños de la provincia."""
    e = {l['lista']: l['escanos'][1] for l in v['listas']}
    voto = {l['lista']: l['voto'][1] for l in v['listas']}
    lo = {l['lista']: l['escanos'][0] for l in v['listas']}
    hi = {l['lista']: l['escanos'][2] for l in v['listas']}
    while sum(e.values()) < v['escanos_total']:
        cand = [k for k in e if e[k] < hi[k]] or list(e)
        k = max(cand, key=lambda k: voto[k] / (e[k] + 1)); e[k] += 1
    while sum(e.values()) > v['escanos_total']:
        cand = [k for k in e if 0 < e[k] and lo[k] < e[k]] or [k for k in e if e[k] > 0]
        k = min(cand, key=lambda k: voto[k] / e[k]); e[k] -= 1
    return e


MC = {c: reparto_central(MOD['provincias'][c]) for c in DC}
assert all(sum(MC[c].values()) == MOD['provincias'][c]['escanos_total'] for c in DC)
TOT = {c: MOD['provincias'][c]['escanos_total'] for c in DC}
for c in DC:   # cada horquilla del CIS deja sitio a los escaños de la provincia
    assert sum(a for a, b in CIS[c].values()) <= TOT[c] <= sum(b for a, b in CIS[c].values()), (c, CIS[c], TOT[c])

# ---------- 2023 ----------
SIM = json.load(open(RAIZ / 'actualidad/src/sistema/simulador.json'))


def dhondt23(c):
    v, val, k = SIM['elecciones']['2023_07'][c]['v'], SIM['elecciones']['2023_07'][c]['validos'], SIM['escanos']['2023_07'][c]
    vv = {q: x for q, x in v.items() if x >= 0.03 * val}
    e = {}
    for _, q in sorted(((x / d, q) for q, x in vv.items() for d in range(1, k + 1)), reverse=True)[:k]:
        e[q] = e.get(q, 0) + 1
    return e


E23 = {c: dhondt23(c) for c in DC}
CAMBIO = {c: (SIM['escanos']['2023_07'][c], TOT[c]) for c in DC if SIM['escanos']['2023_07'][c] != TOT[c]}
assert CAMBIO == {'11': (9, 8), '28': (37, 38)} and all(SIM['escanos']['2026'][c] == TOT[c] for c in DC)
assert sum(sum(e.values()) for e in E23.values()) == 350 and E23['28'] == {'PP': 16, 'PSOE': 10, 'Vox': 5, 'Sumar': 6}
E23['31']['PP'] = E23['31'].get('PP', 0) + E23['31'].pop('UPN', 0)   # Navarra: UPN-PP

# ---------- Comparación ----------
FILAS = []   # (prov, espacio, cis_min, cis_max, modelo, 2023)
for c in DC:
    for s in sorted(set(CIS[c]) | {k for k, v in MC[c].items() if v} | {k for k, v in E23[c].items() if v}):
        a, b = CIS[c].get(s, [0, 0])
        FILAS.append((c, s, a, b, MC[c].get(s, 0), E23[c].get(s, 0)))
F = {(f[0], f[1]): f for f in FILAS}
cuenta = lambda s, cond: sorted(f[0] for f in FILAS if f[1] == s and cond(f))
ARR = lambda f: f[2] > f[4]    # el CIS da más que el modelo (todo su tramo por encima)
ABA = lambda f: f[3] < f[4]
PSOE_MAS, PSOE_MENOS = cuenta('PSOE', ARR), cuenta('PSOE', ABA)
PP_MAS, PP_MENOS = cuenta('PP', ARR), cuenta('PP', ABA)
VOX_MENOS, VOX_MAS = cuenta('Vox', ABA), cuenta('Vox', ARR)
assert (len(PSOE_MAS), len(PSOE_MENOS), len(PP_MENOS), PP_MAS, len(VOX_MENOS), VOX_MAS) == (13, 0, 9, [], 3, []), \
    (len(PSOE_MAS), PSOE_MENOS, len(PP_MENOS), PP_MAS, VOX_MENOS, VOX_MAS)
FUERA = [f for f in FILAS if not f[2] <= f[4] <= f[3]]
assert len(FUERA) == 30
OTROS_FUERA = [f for f in FUERA if f[1] not in ('PSOE', 'PP', 'Vox')]
# frente a 2023
PP_BAJO23 = cuenta('PP', lambda f: f[3] < f[5]); PP_SOBRE23 = cuenta('PP', lambda f: f[2] > f[5])
PSOE_SOBRE23 = cuenta('PSOE', lambda f: f[2] > f[5]); PSOE_BAJO23 = cuenta('PSOE', lambda f: f[3] < f[5])
VOX_SOBRE23 = cuenta('Vox', lambda f: f[2] > f[5])
assert (len(PP_BAJO23), PP_SOBRE23, len(PSOE_SOBRE23), PSOE_BAJO23, len(VOX_SOBRE23)) == (20, [], 7, [], 12)
# quién va delante en escaños
PSOE_DELANTE = sorted(c for c in DC if F[(c, 'PSOE')][2] > F[(c, 'PP')][3])
PP_DELANTE = sorted(c for c in DC if F[(c, 'PP')][2] > F[(c, 'PSOE')][3])
SOLAPAN = len(DC) - len(PSOE_DELANTE) - len(PP_DELANTE)
MOD_PP = sorted(c for c in DC if MC[c].get('PP', 0) > MC[c].get('PSOE', 0))
MOD_PSOE = sorted(c for c in DC if MC[c].get('PSOE', 0) > MC[c].get('PP', 0))
assert (len(PSOE_DELANTE), PP_DELANTE, len(MOD_PP), len(MOD_PSOE)) == (11, ['51', '52'], 21, 9), (len(PSOE_DELANTE), PP_DELANTE, len(MOD_PP), len(MOD_PSOE))
# Madrid y Barcelona
MAD, BCN = F[('28', 'PSOE')], F[('08', 'ERC')]
assert MAD[2:] == (12, 14, 10, 10) and F[('28', 'PP')][2:] == (12, 14, 16, 16) and F[('28', 'Vox')][2:] == (6, 8, 8, 5) and F[('28', 'Sumar')][2:] == (4, 5, 3, 6)
assert BCN[2:] == (7, 9, 6, 4)
CC_TF = F[('38', 'CC')]
assert CC_TF[2:] == (0, 0, 1, 1)

# ---------- Muestra ----------
ENT = {c: DC[c]['entrevistas'] for c in DC}
ERR = {c: 2 * math.sqrt(0.25 / ENT[c]) * 100 for c in DC}   # error teórico, 95,5 %, p = q, muestreo aleatorio simple
MENOS = sorted(DC, key=lambda c: ENT[c])
GRANDES = sorted(DC, key=lambda c: -ENT[c])
SIN_CM = [c for c in MENOS if c not in ('51', '52')]
assert [NOM[c] for c in MENOS[:3]] == ['Melilla', 'Ceuta', 'Soria'] and NOM[GRANDES[0]] == 'Madrid' and NOM[GRANDES[1]] == 'Barcelona'
assert min(ENT[c] for c in SIN_CM) >= 300

# ---------- Figuras ----------
COL = {'PSOE': 'var(--psoe)', 'PP': 'var(--pp)', 'Vox': 'var(--vox)', 'Sumar': 'var(--sumar)', 'ERC': 'var(--erc)'}
TXT_MAS = 'El CIS le da más escaños que la media'
colores = {c: ('var(--psoe)' if c in PSOE_MAS else 'var(--otros)') for c in DC}
titulos = {c: f'{NOM[c]}: PSOE, CIS {F[(c, "PSOE")][2]}–{F[(c, "PSOE")][3]}, media de encuestas {F[(c, "PSOE")][4]}, 2023 {F[(c, "PSOE")][5]}' for c in DC}
g_mapa = figura(f'El CIS da al PSOE más escaños que la media de encuestas en {len(PSOE_MAS)} provincias, y menos en ninguna',
                'Provincias en las que todo el tramo de escaños del PSOE del CIS (P5-P95) queda por encima del reparto central de la media de encuestas',
                mapa_provincias(colores, titulos, 'Mapa de provincias donde el CIS da más escaños al PSOE que la media de encuestas'),
                f'Fuente: CIS, estudio 3584, <a href="{PDF}">estimación de escaños por provincias</a>; <a href="{BASE}encuestas/">media de encuestas de mapaelectoral.es</a>, versión de las {VERSION}. Cálculo propio.',
                leyenda=[(TXT_MAS, 'var(--psoe)'), ('El reparto central de la media cae dentro del tramo del CIS', 'var(--otros)')],
                tabla=(['Provincia', 'Escaños', 'PSOE, CIS', 'PSOE, media', 'PSOE, 2023'],
                       [[NOM[c], str(TOT[c]), f'{F[(c, "PSOE")][2]}–{F[(c, "PSOE")][3]}', str(F[(c, "PSOE")][4]), str(F[(c, "PSOE")][5])]
                        for c in sorted(PSOE_MAS, key=lambda c: NOM[c])]))


def tramos(provs, partidos, W=360, ml=92):
    """Tramo del CIS (barra), reparto central de la media (punto) y escaños de 2023 (raya) por provincia y partido."""
    mx = max(max(F[(c, s)][3], F[(c, s)][4], F[(c, s)][5]) for c in provs for s in partidos)
    x = lambda v: ml + v / mx * (W - ml - 14)
    fila, sep = 15, 10
    H = 20 + len(provs) * (fila * len(partidos) + sep)
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Escaños del CIS, de la media de encuestas y de 2023 en las provincias con más escaños">']
    for v in range(0, mx + 1, 4):
        out.append(f'<line x1="{x(v):.1f}" x2="{x(v):.1f}" y1="14" y2="{H}" stroke="var(--grid)"/><text x="{x(v):.1f}" y="10" text-anchor="middle" style="font-size:11px">{v}</text>')
    y = 20
    for c in provs:
        out.append(f'<text x="{ml - 8}" y="{y + fila * len(partidos) / 2 + 4:.1f}" text-anchor="end" class="lab">{esc(nom(c))}</text>')
        for s in partidos:
            _, _, a, b, m, e = F[(c, s)]
            col = COL[s]
            out.append(f'<rect x="{x(a) - 3:.1f}" y="{y + 3}" width="{x(b) - x(a) + 6:.1f}" height="9" rx="4.5" fill="{col}" fill-opacity=".35">'
                       f'<title>{esc(NOM[c])}, {s}: CIS {a}–{b}, media {m}, 2023 {e}</title></rect>')
            out.append(f'<line x1="{x(e):.1f}" x2="{x(e):.1f}" y1="{y + 1}" y2="{y + 14}" stroke="var(--fg)" stroke-width="1.5"/>')
            out.append(f'<circle cx="{x(m):.1f}" cy="{y + 7.5}" r="3.6" fill="{col}" stroke="var(--bg)" stroke-width="1"/>')
            y += fila
        y += sep
    out.append('</svg>')
    return ''.join(out)


TOP = sorted(DC, key=lambda c: (-TOT[c], NOM[c]))[:10]
assert [NOM[c] for c in TOP[:2]] == ['Madrid', 'Barcelona']
g_tramos = figura('En Madrid, el CIS da 12–14 escaños al PSOE y otros tantos al PP; la media de encuestas, 10 y 16',
                  'Las diez provincias con más escaños: tramo de escaños del CIS (barra), reparto central de la media de encuestas (punto) y escaños de julio de 2023 (raya vertical)',
                  tramos(TOP, ['PSOE', 'PP', 'Vox']),
                  f'Fuente: CIS, estudio 3584, <a href="{PDF}">estimación de escaños por provincias</a>; media de encuestas de mapaelectoral.es ({VERSION}); 2023, Ministerio del Interior. Cálculo propio.',
                  leyenda=[('PSOE', 'var(--psoe)'), ('PP', 'var(--pp)'), ('Vox', 'var(--vox)')],
                  tabla=(['Provincia', 'Partido', 'CIS', 'Media', '2023'],
                         [[NOM[c], s, f'{F[(c, s)][2]}–{F[(c, s)][3]}', str(F[(c, s)][4]), str(F[(c, s)][5])] for c in TOP for s in ('PSOE', 'PP', 'Vox')]))

NOMESP = {'Sumar': 'Sumar / Frente Amplio', 'ERC': 'ERC (ERC-Podemos en el CIS)', 'CC': 'Coalición Canaria'}
filas_todas = []
for c in sorted(DC, key=lambda c: unicodedata.normalize('NFKD', NOM[c])):
    otros = [f for f in FUERA if f[0] == c and f[1] not in ('PSOE', 'PP', 'Vox')]
    filas_todas.append([NOM[c], n(ENT[c]), '±' + p(ERR[c])] + [f'{F[(c, s)][2]}–{F[(c, s)][3]} / {F[(c, s)][4]}' for s in ('PSOE', 'PP', 'Vox')]
                       + ['; '.join(f'{NOMESP.get(f[1], f[1])}: CIS {f[2]}–{f[3]}, media {f[4]}' for f in otros) or '–'])
g_tabla = figura('Las 52 provincias: el CIS, la media de encuestas y la muestra de cada una',
                 'Entrevistas del CIS en cada provincia, error teórico de esa muestra y escaños del PSOE, el PP y Vox: tramo del CIS / reparto central de la media',
                 '', f'Fuente: CIS, estudio 3584, <a href="{PDF}">estimación de escaños</a> y <a href="{XLSX}">resultados por provincia</a> (entrevistas); media de encuestas de mapaelectoral.es ({VERSION}). '
                 'Error teórico: el del CIS para la muestra total (95,5 %, p = q, muestreo aleatorio simple) aplicado a las entrevistas de cada provincia. Cálculo propio.',
                 tabla=(['Provincia', 'Entrevistas', 'Error teórico (puntos)', 'PSOE', 'PP', 'Vox', 'Otros partidos fuera del tramo'], filas_todas))
g_tabla = g_tabla.replace('<div class="chart"></div>', '').replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>')
assert '<details open>' in g_tabla

# ---------- Texto ----------
lista = lambda cs: ', '.join(nom(c) for c in cs[:-1]) + ' y ' + nom(cs[-1]) if len(cs) > 1 else nom(cs[0])
cita = ('Debe advertirse expresamente que los percentiles no son aditivos entre provincias: sumar los percentiles provinciales '
        'no equivale a calcular los percentiles de la suma nacional')
assert len(PSOE_MAS) == 13
cuerpo = f'''<div style="margin-top:1.4rem"></div>
<p data-tipo="contexto">El preelectoral del CIS, publicado el jueves, no solo da escaños para toda España. En su <a href="{PDF}">estimación</a> incluye una tabla con la horquilla de escaños de cada partido en las 52 provincias, el tramo que va del percentil 5 al 95 de sus simulaciones. No publica el porcentaje de voto estimado en cada provincia, solo el nacional, como contamos en {L('cis-preelectoral-29n', 'la pieza del CIS preelectoral')}.</p>
<p data-tipo="dato">Comparadas con el reparto central de <a href="{BASE}encuestas/">la media de encuestas</a> (versión de las {VERSION}, que ya incluye este estudio del CIS), las horquillas del CIS dan al PSOE más escaños en <strong>{len(PSOE_MAS)} de las 52 provincias</strong> y menos en ninguna. Al PP le dan menos en {len(PP_MENOS)} y más en ninguna. A Vox le dan menos en {len(VOX_MENOS)}: {lista(VOX_MENOS)}.</p>
{g_mapa}
<p data-tipo="dato">Madrid es donde más se separan. El CIS da al PSOE entre {MAD[2]} y {MAD[3]} escaños, los mismos que al PP ({F[('28', 'PP')][2]}–{F[('28', 'PP')][3]}); la media de encuestas, {MAD[4]} al PSOE y {F[('28', 'PP')][4]} al PP, los mismos que sacaron en 2023, cuando Madrid elegía un diputado menos. A Vox, el CIS le da entre {F[('28', 'Vox')][2]} y {F[('28', 'Vox')][3]} (la media, {F[('28', 'Vox')][4]}), y al Frente Amplio, entre {F[('28', 'Sumar')][2]} y {F[('28', 'Sumar')][3]} (la media, {F[('28', 'Sumar')][4]}). En Barcelona, ERC, a la que el CIS mide junto a Podemos porque hacen campaña juntos en Cataluña, saca entre {BCN[2]} y {BCN[3]} en el CIS; la media le da {BCN[4]} y en 2023 tuvo {BCN[5]}.</p>
{g_tramos}
<h2>Frente a 2023</h2>
<p data-tipo="dato">Con los resultados de julio de 2023, el PP sale peor en el CIS en {len(PP_BAJO23)} provincias, en las que todo su tramo queda por debajo de los escaños que sacó, y mejor en ninguna. El PSOE mejora en {len(PSOE_SOBRE23)} y no empeora en ninguna. Vox mejora en {len(VOX_SOBRE23)}. Dos provincias reparten distinto número de escaños que en 2023: Madrid elige {CAMBIO['28'][1]}, uno más, y Cádiz, {CAMBIO['11'][1]}, uno menos.</p>
<p data-tipo="dato">El PSOE va por delante del PP en escaños en {len(PSOE_DELANTE)} provincias, en las que el mínimo de su horquilla supera el máximo de la del PP: entre ellas, {lista([c for c in PSOE_DELANTE if c in ('08', '18', '43', '48', '35', '38')])}. El PP solo va claramente por delante en Ceuta y Melilla, que eligen un diputado cada una. En las otras {SOLAPAN}, las horquillas de los dos se tocan. En el reparto central de la media de encuestas, el PP saca más escaños que el PSOE en {len(MOD_PP)} provincias y el PSOE más que el PP en {len(MOD_PSOE)}.</p>
<p data-tipo="dato">El CIS tampoco da escaño a Coalición Canaria en Santa Cruz de Tenerife, donde lo tuvo en 2023 y donde la media de encuestas lo mantiene: no la incluye en la tabla de escaños, y en el total nacional le da el {p(0.2)} % sin escaños.</p>
<h2>Cuántas entrevistas hay detrás de cada provincia</h2>
<p data-tipo="contexto">El CIS hizo {n(45074)} entrevistas del 7 al 30 de octubre. Según su <a href="{XLSX}">ficha técnica</a>, partió de un reparto proporcional y lo ajustó para que cada provincia tuviera al menos 300 entrevistas, y Ceuta y Melilla, al menos 50. Madrid tiene {n(ENT['28'])} y Barcelona, {n(ENT['08'])}; Soria, {n(ENT['42'])}; Ceuta, {n(ENT['51'])}, y Melilla, {n(ENT['52'])}. Con la fórmula del propio CIS para el total de la muestra, el error teórico va de ±{p(ERR['28'])} puntos en Madrid a ±{p(ERR['42'])} en Soria y ±{p(ERR['52'])} en Melilla.</p>
<p data-tipo="contexto">En una provincia que reparte tres o cuatro escaños, un punto de diferencia puede mover uno, y la nota metodológica del CIS avisa de que las horquillas provinciales no se suman:</p>
<blockquote class="cita"><p>«{cita}»</p><footer>CIS, nota metodológica del reparto de escaños del <a href="{PDF}">estudio 3584</a> (12-11-2026).</footer></blockquote>
{g_tabla}
<h2>Cómo se ha hecho</h2>
<p data-tipo="contexto">Las horquillas son las de la tabla «Estimación de escaños por provincias» del CIS. Se comparan por espacio: el Frente Amplio del CIS, Compromís en Alicante, Castellón y Valencia, Ara Més-Front Ampli en Baleares y la Unidad del Pueblo Canario en Canarias, con la candidatura de Sumar / Frente Amplio del modelo; ERC-Podemos, con ERC; en Navarra, el PP con UPN-PP. El reparto central es el que publica cada <a href="{BASE}encuestas/provincias.html">página provincial de /encuestas/</a>: la mediana de las simulaciones de cada partido, ajustada para que sume los escaños de la provincia. Una horquilla queda por encima del modelo cuando su mínimo supera el reparto central, y por debajo cuando su máximo no lo alcanza. Los escaños de 2023 salen de los votos oficiales con la ley D'Hondt; en Navarra se suman los de UPN y PP.</p>
'''
cuerpo = cuerpo.replace('<details><summary>Ver la tabla</summary>', '<details open><summary>Tabla</summary>', 1)
preguntas = [
    ('¿Da el CIS escaños por provincia para el 29N?',
     f'Sí: una horquilla (percentil 5 a 95) para cada partido en las 52 provincias, en la <a href="{PDF}">estimación del estudio 3584</a>. No da el porcentaje de voto estimado por provincia.'),
    ('¿En qué se diferencia el CIS de la media de encuestas por provincia?',
     f'Da al PSOE más escaños que el reparto central de la media en {len(PSOE_MAS)} provincias y menos en ninguna; al PP, menos en {len(PP_MENOS)}. La mayor diferencia, en Madrid: PSOE {MAD[2]}–{MAD[3]} en el CIS y {MAD[4]} en la media.'),
    ('¿Cuántas entrevistas hizo el CIS en cada provincia?',
     f'Al menos 300 por provincia y 50 en Ceuta y Melilla, según su ficha técnica. Van de {n(ENT["52"])} en Melilla a {n(ENT["28"])} en Madrid.'),
]
enlaces = (f'{L("cis-preelectoral-29n", "El CIS preelectoral")} · {L("cis-tezanos-estimacion-29n", "El CIS frente a los resultados")} · '
           f'<a href="{BASE}encuestas/">Todas las encuestas del 29N</a> · <a href="{BASE}encuestas/cis/">Las encuestas del CIS</a>')
foot = ('Datos: CIS, estudio 3584 (estimación de escaños por provincias y resultados por provincia); media de encuestas de mapaelectoral.es/encuestas; '
        'resultados de julio de 2023 del Ministerio del Interior. Cálculo: actualidad/src/resumenes/cis_provincias.py.')
r4 = lambda x: round(float(x), 4)
DATOS = {'F': {f'{f[0]}|{f[1]}': list(f[2:]) for f in FILAS}, 'ENT': ENT, 'ERR': {c: r4(v) for c, v in ERR.items()}, 'TOT': TOT,
         'PSOE_MAS': PSOE_MAS, 'PSOE_MENOS': PSOE_MENOS, 'PP_MENOS': PP_MENOS, 'PP_MAS': PP_MAS, 'VOX_MENOS': VOX_MENOS,
         'PP_BAJO23': PP_BAJO23, 'PSOE_SOBRE23': PSOE_SOBRE23, 'VOX_SOBRE23': VOX_SOBRE23, 'PSOE_DELANTE': PSOE_DELANTE, 'PP_DELANTE': PP_DELANTE,
         'SOLAPAN': SOLAPAN, 'MOD_PP': MOD_PP, 'MOD_PSOE': MOD_PSOE, 'N': 45074}
datos_js = '<script>const D=' + json.dumps(DATOS, ensure_ascii=False, separators=(',', ':')) + ';</script>\n'
H1 = (f'El CIS da al PSOE más escaños que la media de encuestas en {len(PSOE_MAS)} provincias y menos en ninguna; '
      f'en Madrid, entre {MAD[2]} y {MAD[3]} frente a {MAD[4]}')
DEK = (f'Al PP, el preelectoral le da menos escaños que en 2023 en {len(PP_BAJO23)} provincias. Las horquillas provinciales del CIS salen de '
       f'muestras que van de {n(ENT["52"])} entrevistas en Melilla a {n(ENT["28"])} en Madrid.')
if __name__ == '__main__':
    pieza(SLUG, 'El CIS, provincia a provincia', H1, DEK, '13 de noviembre de 2026', cuerpo, preguntas, enlaces, foot, scripts=datos_js)
    print(H1); print(DEK)
    print('PSOE_MAS', [NOM[c] for c in PSOE_MAS]); print('PP_MENOS', [NOM[c] for c in PP_MENOS]); print('VOX_MENOS', [NOM[c] for c in VOX_MENOS])
    print('OTROS', OTROS_FUERA); print('PSOE_DELANTE', [NOM[c] for c in PSOE_DELANTE]); print('PP_BAJO23', [NOM[c] for c in PP_BAJO23])
