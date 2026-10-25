"""«El otro Clásico: Barcelona y Madrid, ciudad a ciudad» (pieza de domingo, 25-10-2026, día del Barça-Madrid).

Cifras: municipios y secciones de las descargas del mapa (generales-2026/data/municipios.json y data/e/<elección>.json para
1977-2000; generales-2026/descargas/secciones.csv para 2004-2023, con la renta del INE por sección); barrios de
data/barrios/secciones_barrio.csv; la frontera de la Travessera de les Corts, del análisis de polarización
(/mnt/project-files/moran/fronteras.csv, recalculada aquí). Regresión con efecto fijo de ciudad y errores agrupados por barrio.
Uso, desde la raíz: python3 actualidad/src/resumenes/clasico.py
"""
import json
import warnings

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from comun import BASE, COLOR, RAIZ, esc, figura, n, pares, pieza

warnings.filterwarnings('ignore')
A = BASE + 'actualidad/'
BCN, MAD = '08019', '28079'
E = '2023_07'

# --- Serie de la ciudad, 1977-2023 ---
m = json.load(open(RAIZ / 'generales-2026/data/municipios.json'))
idx = {c: i for i, c in enumerate(m['cod'])}
VIEJAS = ['1977_06', '1979_03', '1982_10', '1986_06', '1989_10', '1993_06', '1996_03', '2000_03']
NUEVAS = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
serie = {}
for c in (BCN, MAD):
    i, filas = idx[c], {}
    for e in VIEJAS:
        f = json.load(open(RAIZ / f'generales-2026/data/e/{e}.json'))
        filas[e] = {k[8:]: f[k][i] for k in f if k[8:] != 'gana'}
    for e in NUEVAS:
        filas[e] = {k[8:]: m[k][idx[c]] for k in m if k.startswith(e) and k[8:] != 'gana'}
    serie[c] = filas
FAMS = ['PP', 'PSOE', 'SUMAR', 'ERC', 'JUNTS', 'UCD', 'CDS', 'CS', 'VOX', 'UPYD']


def ganador(r):
    return max((k for k in FAMS if k in r), key=lambda k: r[k])


GAN = {c: {e: ganador(r) for e, r in serie[c].items()} for c in serie}
assert [GAN[BCN][e] for e in VIEJAS + NUEVAS] == ['PSOE', 'PSOE', 'PSOE', 'PSOE', 'JUNTS', 'JUNTS', 'PSOE', 'PSOE', 'PSOE', 'PSOE',
                                                 'JUNTS', 'SUMAR', 'SUMAR', 'ERC', 'ERC', 'PSOE'], GAN[BCN]
assert [GAN[MAD][e] for e in VIEJAS + NUEVAS] == ['UCD', 'UCD', 'PSOE', 'PSOE', 'PP', 'PP', 'PP', 'PP', 'PP', 'PP', 'PP', 'PP', 'PP',
                                                 'PSOE', 'PP', 'PP'], GAN[MAD]
# Madrid votó más que Barcelona en las 16 generales
assert all(serie[MAD][e]['part'] > serie[BCN][e]['part'] for e in VIEJAS + NUEVAS)
assert sum(GAN[BCN][e] == 'PSOE' for e in GAN[BCN]) == 9
assert [e for e in GAN[BCN] if GAN[BCN][e] == GAN[MAD][e]] == ['1982_10', '1986_06']
assert max(GAN[BCN], key=lambda e: serie[BCN][e].get('PP', 0)) == '2000_03'
assert max(VIEJAS + NUEVAS, key=lambda e: serie[MAD][e]['part'] - serie[BCN][e]['part']) == '1979_03'
assert min(VIEJAS + NUEVAS, key=lambda e: serie[MAD][e]['part'] - serie[BCN][e]['part']) == '2019_04'
pct = lambda c, e, k: serie[c][e].get(k, 0) * 100
p = lambda v: n(v, 1)
assert round(pct(MAD, E, 'PP'), 1) == 41.8 and round(pct(BCN, E, 'PSOE'), 1) == 33.2 and round(pct(BCN, E, 'PP'), 1) == 15.9

# --- Secciones ---
d = pd.read_csv(RAIZ / 'generales-2026/descargas/secciones.csv', dtype={'tract_code': str, 'mun_code': str})
d = d[d.mun_code.isin([BCN, MAD])].copy()
d['city'] = np.where(d.mun_code == BCN, 'BCN', 'MAD')
bar = pd.read_csv(RAIZ / 'data/barrios/secciones_barrio.csv', dtype=str)[['tract_code', 'barrio']]
d = d.merge(bar, on='tract_code', how='left')
assert d.barrio.notna().all()
NSEC = d.groupby('city').size().to_dict()
assert NSEC == {'BCN': 1068, 'MAD': 2450}, NSEC


def cuota(s, k, e=E):
    return (s[f'{e}_{k}'] * s[f'{e}_votantes']).sum() / s[f'{e}_votantes'].sum() * 100


def part(s, e=E):
    return s[f'{e}_votantes'].sum() / s[f'{e}_censo'].sum() * 100


# Tramos de renta por unidad de consumo comunes a las dos ciudades (el INE topa la renta en 58.752 euros)
TRAMOS = [(0, 20000, 'Menos de 20.000 €'), (20000, 25000, '20.000-25.000 €'), (25000, 30000, '25.000-30.000 €'),
          (30000, 35000, '30.000-35.000 €'), (35000, 40000, '35.000-40.000 €'), (40000, 50000, '40.000-50.000 €'),
          (50000, 99999, 'Más de 50.000 €')]
tr = {}
for a, b, nom in TRAMOS:
    for c in ('BCN', 'MAD'):
        s = d[(d.city == c) & (d.renta_uc > a) & (d.renta_uc <= b)]
        tr[(nom, c)] = dict(n=len(s), PP=cuota(s, 'PP'), PSOE=cuota(s, 'PSOE'), VOX=cuota(s, 'VOX'), JUNTS=cuota(s, 'JUNTS'),
                            ERC=cuota(s, 'ERC'), SUMAR=cuota(s, 'SUMAR'), part=part(s))
MED = '25.000-30.000 €'
assert round(tr[(MED, 'MAD')]['PP'], 1) == 38.1 and round(tr[(MED, 'BCN')]['PP'], 1) == 12.7
assert round(tr[('30.000-35.000 €', 'MAD')]['PP'] / tr[('30.000-35.000 €', 'BCN')]['PP'], 1) == 3.0
assert all(tr[(t[2], 'MAD')]['part'] > tr[(t[2], 'BCN')]['part'] for t in TRAMOS)
assert all(2 <= tr[(t[2], 'MAD')]['PP'] / tr[(t[2], 'BCN')]['PP'] < 3.05 for t in TRAMOS[:-1])
assert all(4 <= tr[(t[2], 'BCN')]['PSOE'] - tr[(t[2], 'MAD')]['PSOE'] < 7.5 for t in TRAMOS)
assert all(12 <= tr[(t[2], 'BCN')]['PP'] <= 15 for t in TRAMOS[:4])
TOP = 'Más de 50.000 €'

# Deciles de renta dentro de cada ciudad (para Vox)
dec = {}
for c, x in d.groupby('city'):
    x = x.copy(); x['dec'] = pd.qcut(x.renta_uc, 10, labels=False) + 1
    dec[c] = {k: dict(VOX=cuota(s, 'VOX'), PP=cuota(s, 'PP'), PSOE=cuota(s, 'PSOE'), part=part(s)) for k, s in x.groupby('dec')}
vox_b = [round(dec['BCN'][k]['VOX'], 1) for k in range(1, 11)]
vox_m = [round(dec['MAD'][k]['VOX'], 1) for k in range(1, 11)]
assert vox_b[0] == 9.1 and min(vox_b) == 4.2 and vox_b[-1] == 8.1, vox_b
assert vox_m[0] == 11.1 and vox_m[-1] == 17.1, vox_m

# Regresión: cuota ~ efecto fijo de ciudad + log(renta) por ciudad, ponderada por censo, errores agrupados por barrio
d['lr'] = np.log(d.renta_uc)
grupos = pd.factorize(d.city + d.barrio)[0]
NCL = (d.city + d.barrio).groupby(d.city).nunique().to_dict()
reg = {}
for y, col in (('PP', f'{E}_PP'), ('PSOE', f'{E}_PSOE'), ('VOX', f'{E}_VOX'), ('JUNTS', f'{E}_JUNTS'), ('part', f'{E}_part')):
    d['y'] = d[col] * 100
    r = smf.wls('y ~ C(city) + lr:C(city)', data=d, weights=d[f'{E}_censo']).fit(cov_type='cluster', cov_kwds={'groups': grupos})
    r2 = smf.wls('y ~ C(city) * lr', data=d, weights=d[f'{E}_censo']).fit(cov_type='cluster', cov_kwds={'groups': grupos})
    k = np.log(2)
    reg[y] = dict(b=r.params['lr:C(city)[BCN]'] * k, m=r.params['lr:C(city)[MAD]'] * k,
                  eb=r.bse['lr:C(city)[BCN]'] * k, em=r.bse['lr:C(city)[MAD]'] * k, pdif=r2.pvalues['C(city)[T.MAD]:lr'])
print({y: {k: round(v, 4) for k, v in x.items()} for y, x in reg.items()}, NCL)
assert round(reg['PP']['m'], 1) == 20.5 and round(reg['PP']['b'], 1) == 11.5 and reg['PP']['pdif'] < .001
assert round(reg['PSOE']['m'], 1) == -15.7 and round(reg['PSOE']['b'], 1) == -16.3 and reg['PSOE']['pdif'] > .1
assert reg['part']['pdif'] > .1

# Barrios de los estadios
def barrio(nom):
    s = d[d.barrio == nom]
    return dict(n=len(s), renta=(s.renta_uc * s.poblacion).sum() / s.poblacion.sum(), part=part(s),
                **{k: cuota(s, k) for k in ('PP', 'PSOE', 'VOX', 'SUMAR', 'ERC', 'JUNTS')},
                pp04=cuota(s, 'PP', '2004_03'), psoe04=cuota(s, 'PSOE', '2004_03'))


CN, BE = barrio('la Maternitat i Sant Ramon'), barrio('Hispanoamérica')
assert round(CN['PSOE'], 1) == 30.8 and round(CN['PP'], 1) == 20.8 and round(BE['PP'], 1) == 62.1 and round(BE['VOX'], 1) == 16.7
print('Camp Nou', CN, 'Bernabéu', BE)

# Distritos de los estadios: les Corts (04) y Chamartín (05)
d['dist'] = d.tract_code.str[5:7]
dist = {(c, k): dict(PP=cuota(s, 'PP'), PSOE=cuota(s, 'PSOE')) for (c, k), s in d.groupby(['city', 'dist'])}
pp_mad = sorted(((v['PP'], k) for (c, k), v in dist.items() if c == 'MAD'), reverse=True)
assert pp_mad[0][1] == '05', pp_mad[:3]
assert round(dist[('MAD', '05')]['PP'], 1) == 59.0

# La frontera de la Travessera de les Corts (dos secciones vecinas de la Maternitat)
fa, fb = d[d.tract_code == '0801904049'].iloc[0], d[d.tract_code == '0801904041'].iloc[0]
FA = dict(PP=fa[f'{E}_PP'] * 100, PSOE=fa[f'{E}_PSOE'] * 100, renta=fa.renta_uc)
FB = dict(PP=fb[f'{E}_PP'] * 100, PSOE=fb[f'{E}_PSOE'] * 100, renta=fb.renta_uc)
assert round(FA['PP'], 1) == 38.9 and round(FB['PSOE'], 1) == 37.2 and FA['renta'] == 47101 and FB['renta'] == 25651

# Cambios de ganador entre noviembre de 2019 y julio de 2023
flip = {c: pd.crosstab(x['2019_11_gana'], x[f'{E}_gana']) for c, x in d.groupby('city')}
ERC_PSC = int(flip['BCN'].loc['ERC', 'PSOE'])
PSOE_PP = int(flip['MAD'].loc['PSOE', 'PP'])
assert ERC_PSC == 540 and PSOE_PP == 521
G23 = {c: x[f'{E}_gana'].value_counts().to_dict() for c, x in d.groupby('city')}
assert G23['BCN']['PSOE'] == 956 and G23['MAD']['PP'] == 1603

# --- Gráficos ---
NOMF = {'PP': 'PP', 'PSOE': 'PSOE', 'SUMAR': 'Sumar', 'ERC': 'ERC', 'JUNTS': 'Junts', 'UCD': 'UCD', 'VOX': 'Vox'}
ALIAS = {('BCN', 'PSOE'): 'PSC', ('MAD', 'PP'): 'PP', ('BCN', 'JUNTS'): 'CiU', ('BCN', 'SUMAR'): 'En Comú'}
COLF = {'PP': COLOR['PP'], 'PSOE': COLOR['PSOE'], 'SUMAR': COLOR['Sumar'], 'ERC': COLOR['ERC'], 'JUNTS': COLOR['Junts'],
        'UCD': '#2e9a49', 'VOX': COLOR['Vox']}
ANIO = {'1977_06': '1977', '1979_03': '1979', '1982_10': '1982', '1986_06': '1986', '1989_10': '1989', '1993_06': '1993',
        '1996_03': '1996', '2000_03': '2000', '2004_03': '2004', '2008_03': '2008', '2011_11': '2011', '2015_12': '2015',
        '2016_06': '2016', '2019_04': 'abr. 2019', '2019_11': 'nov. 2019', '2023_07': '2023'}


def nombre_partido(c, e, k):
    if k == 'PP' and e < '1989':
        return 'AP'
    if k == 'JUNTS' and e >= '2019':
        return 'Junts'
    if k == 'SUMAR' and c == BCN and e in ('2015_12', '2016_06'):
        return 'En Comú Podem'
    return {'PSOE': 'PSC' if c == BCN else 'PSOE', 'JUNTS': 'CiU'}.get(k, NOMF[k])


def tira():
    W, ml, lado, gap = 640, 92, 30, 3
    ES = VIEJAS + NUEVAS
    H = 2 * (lado + 18) + 46
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Partido más votado en Barcelona y en Madrid en cada elección general desde 1977">']
    for j, (c, nom) in enumerate(((BCN, 'Barcelona'), (MAD, 'Madrid'))):
        y = 6 + j * (lado + 18)
        out.append(f'<text x="{ml - 8}" y="{y + lado / 2 + 5}" text-anchor="end" class="lab">{nom}</text>')
        for i, e in enumerate(ES):
            x = ml + i * (lado + gap)
            k = GAN[c][e]
            out.append(f'<rect x="{x}" y="{y}" width="{lado}" height="{lado}" rx="3" fill="{COLF[k]}">'
                       f'<title>{nom}, {ANIO[e]}: {nombre_partido(c, e, k)} ({p(pct(c, e, k))} %)</title></rect>')
    for i, e in enumerate(ES):
        x = ml + i * (lado + gap) + lado / 2
        if e[:4] in ('1977', '1982', '1989', '1996', '2004', '2011', '2023'):
            out.append(f'<text x="{x}" y="{H - 22}" text-anchor="middle">{e[:4]}</text>')
    out.append('</svg>')
    return ''.join(out)


fig_tira = figura('Medio siglo sin coincidir casi nunca',
                  'El partido más votado en Barcelona y en Madrid capital en cada una de las 16 elecciones generales desde 1977',
                  tira(),
                  'Fuente: Ministerio del Interior, resultados por municipio (1977-2000, Infoelectoral y pollspaindata) y por sección (2004-2023). '
                  'Familias de partidos del mapa: AP antes de 1989; PSC en Barcelona; CiU y después Junts; En Comú Podem en 2015 y 2016.',
                  leyenda=[('PSC / PSOE', COLOR['PSOE']), ('AP / PP', COLOR['PP']), ('UCD', '#2e9a49'), ('CiU', COLOR['Junts']),
                           ('En Comú', COLOR['Sumar']), ('ERC', COLOR['ERC'])],
                  tabla=(['Elección', 'Barcelona', 'Madrid', 'Participación Barcelona', 'Participación Madrid'],
                         [(ANIO[e], f'{nombre_partido(BCN, e, GAN[BCN][e])} {p(pct(BCN, e, GAN[BCN][e]))} %',
                           f'{nombre_partido(MAD, e, GAN[MAD][e])} {p(pct(MAD, e, GAN[MAD][e]))} %',
                           p(pct(BCN, e, 'part')) + ' %', p(pct(MAD, e, 'part')) + ' %') for e in VIEJAS + NUEVAS]))

fig_pp = figura('Con la misma renta, el PP saca en Madrid el doble o el triple',
                'Voto al PP en las generales de 2023 en las secciones de cada tramo de renta. Arriba, Barcelona (tono claro); abajo, Madrid',
                pares([(t[2], tr[(t[2], 'BCN')]['PP'], tr[(t[2], 'MAD')]['PP'], COLOR['PP']) for t in TRAMOS], 70,
                      'Voto al PP por tramo de renta de la sección en Barcelona y en Madrid, 2023', ['Barcelona', 'Madrid'], ml=150),
                'Fuente: Ministerio del Interior (resultados por sección, sin voto exterior) e INE, Atlas de Distribución de Renta de los Hogares 2023 '
                '(renta neta por unidad de consumo; el INE la topa en 58.752 euros). Cálculo propio.',
                tabla=(['Renta de la sección', 'Secciones BCN', 'PP BCN', 'Secciones MAD', 'PP MAD'],
                       [(t[2], n(tr[(t[2], 'BCN')]['n']), p(tr[(t[2], 'BCN')]['PP']) + ' %', n(tr[(t[2], 'MAD')]['n']),
                         p(tr[(t[2], 'MAD')]['PP']) + ' %') for t in TRAMOS]))

fig_psoe = figura('El voto socialista cae igual en las dos ciudades',
                  'Voto al PSC (Barcelona, tono claro) y al PSOE (Madrid) en 2023 en las secciones de cada tramo de renta',
                  pares([(t[2], tr[(t[2], 'BCN')]['PSOE'], tr[(t[2], 'MAD')]['PSOE'], COLOR['PSOE']) for t in TRAMOS], 70,
                        'Voto al PSC y al PSOE por tramo de renta de la sección en Barcelona y en Madrid, 2023', ['Barcelona', 'Madrid'], ml=150),
                  'Fuente: Ministerio del Interior e INE (ADRH 2023). Cálculo propio.',
                  tabla=(['Renta de la sección', 'PSC BCN', 'PSOE MAD', 'Participación BCN', 'Participación MAD'],
                         [(t[2], p(tr[(t[2], 'BCN')]['PSOE']) + ' %', p(tr[(t[2], 'MAD')]['PSOE']) + ' %',
                           p(tr[(t[2], 'BCN')]['part']) + ' %', p(tr[(t[2], 'MAD')]['part']) + ' %') for t in TRAMOS]))

PARTS = [('PP', 'PP'), ('PSOE', 'PSC / PSOE'), ('VOX', 'Vox'), ('SUMAR', 'Sumar'), ('ERC', 'ERC'), ('JUNTS', 'Junts')]
fig_est = figura('Los barrios de los dos estadios',
                 'Voto en 2023 en la Maternitat i Sant Ramon, el barrio del Camp Nou (tono claro), y en Hispanoamérica, el del Bernabéu',
                 pares([(nom, CN[k], BE[k], COLOR[{'VOX': 'Vox', 'SUMAR': 'Sumar', 'JUNTS': 'Junts'}.get(k, k)]) for k, nom in PARTS], 70,
                       'Voto por partido en los barrios del Camp Nou y del Bernabéu, 2023', ['Camp Nou', 'Bernabéu'], ml=110),
                 f'Fuente: Ministerio del Interior, resultados por sección; barrios de OpenStreetMap ({CN["n"]} secciones en la Maternitat i Sant Ramon, '
                 f'{BE["n"]} en Hispanoamérica). Cálculo propio.',
                 tabla=(['Partido', 'la Maternitat i Sant Ramon', 'Hispanoamérica'], [(nom, p(CN[k]) + ' %', p(BE[k]) + ' %') for k, nom in PARTS]))

# --- Texto ---
L = lambda slug, t: f'<a href="{A}{slug}/">{t}</a>'
tm, tb = tr[(MED, 'MAD')], tr[(MED, 'BCN')]
t3m, t3b = tr[('30.000-35.000 €', 'MAD')], tr[('30.000-35.000 €', 'BCN')]
xm, xb = tr[(TOP, 'MAD')], tr[(TOP, 'BCN')]
lm, lb = tr[('Menos de 20.000 €', 'MAD')], tr[('Menos de 20.000 €', 'BCN')]
cuerpo = f'''<div class="resumen"><b>En corto</b><ul>
<li>En las secciones de Madrid con una renta de 25.000 a 30.000 euros por unidad de consumo, el PP sacó en 2023 el {p(tm["PP"])} %. En las de Barcelona con la misma renta, el {p(tb["PP"])} %.</li>
<li>El voto socialista baja con la renta casi exactamente igual en las dos ciudades. Lo que cambia es quién recoge el voto de los barrios ricos: en Madrid, el PP y Vox; en Barcelona se reparte entre el PP, el PSC, Junts y Vox.</li>
<li>En las 16 generales desde 1977, el PP o su antecesora AP nunca ha sido el más votado en Barcelona, y Madrid ha votado siempre más que Barcelona.</li>
<li>En el barrio del Camp Nou ganó el PSC con el {p(CN["PSOE"])} %; en el del Bernabéu, el PP con el {p(BE["PP"])} %.</li>
</ul></div>
<p data-tipo="contexto">Esta noche, a las nueve, el Barça recibe al Real Madrid en el Spotify Camp Nou en la décima jornada de Liga, según <a href="https://www.fcbarcelona.es/es/noticias/4570226/el-horario-del-clasico-de-liga-en-el-spotify-camp-nou-confirmado">el propio club</a>. El estadio tiene su dirección en el carrer d'Arístides Maillol, en el barrio de la Maternitat i Sant Ramon, en el distrito de les Corts, según la <a href="https://guia.barcelona.cat/en/detall/spotify-camp-nou_95152103742.html">guía municipal de Barcelona</a>. El Santiago Bernabéu está en la otra punta del mapa, en el extremo suroeste de Hispanoamérica, un barrio de algo más de 31.000 vecinos del distrito de Chamartín, como lo describe <a href="https://www.timeout.es/madrid/es/que-hacer/descubre-hispanoamerica-el-barrio-del-buen-vivir">Time Out</a>.</p>
<p data-tipo="contexto">El partido nunca ha sido solo fútbol. Manuel Vázquez Montalbán dejó para el Barça la fórmula del «ejército simbólico desarmado de la catalanidad», que el club recuerda al presentar la antología de sus textos <a href="https://www.fcbarcelona.es/es/ficha/778212/manuel-vazquez-montalban-barca-cultura-i-esport"><i>Barça, cultura i esport</i></a>. Al otro lado, Isabel Díaz Ayuso definía en 2023 a Madrid como «una España dentro de otra», en el 40 aniversario del Estatuto de Autonomía, según Europa Press, que recogió <a href="https://www.ultimahora.es/noticias/comunidades/2023/02/24/1888457/ayuso-defiende-madrid-eleva-muros-derriba-aniversario-del-estatuto-espana-dentro-otra.html">Última Hora</a>.</p>
<p data-tipo="contexto">A cinco semanas de las generales del 29 de noviembre, Mapa Electoral ha puesto una ciudad al lado de la otra, sección censal a sección censal. Son las {n(NSEC["BCN"])} secciones de Barcelona y las {n(NSEC["MAD"])} de Madrid, con su renta y con su voto desde 1977. Este es el otro Clásico, el que no se juega en el césped.</p>
<h2>Dos barrios, dos estadios</h2>
<p data-tipo="dato">En las generales de julio de 2023, en la Maternitat i Sant Ramon ganó el PSC con el {p(CN["PSOE"])} % de los votos, por delante del PP ({p(CN["PP"])} %), Sumar ({p(CN["SUMAR"])} %), Junts ({p(CN["JUNTS"])} %) y ERC ({p(CN["ERC"])} %). Votó el {p(CN["part"])} % del censo. En Hispanoamérica, el PP sacó el {p(BE["PP"])} %, Vox el {p(BE["VOX"])} % y el PSOE el {p(BE["PSOE"])} %, con una participación del {p(BE["part"])} %.</p>
{fig_est}
<p data-tipo="dato">No son barrios de la misma renta. La renta media por unidad de consumo de las secciones de Hispanoamérica es de {n(BE["renta"])} euros, y la de la Maternitat i Sant Ramon, de {n(CN["renta"])}. Pero en las secciones de Madrid de una renta parecida a la del barrio del Camp Nou, entre 30.000 y 35.000 euros, el PP sacó el {p(t3m["PP"])} %, más del doble que en la Maternitat.</p>
<p data-tipo="dato">El distrito del Bernabéu, Chamartín, es el que más votó al PP de los 21 de Madrid: el {p(dist[("MAD", "05")]["PP"])} %. Les Corts, el del Camp Nou, fue el segundo de Barcelona, con el {p(dist[("BCN", "04")]["PP"])} %, detrás de Sarrià-Sant Gervasi. Y en el mismo barrio del estadio pasa una de las fronteras de voto más bruscas de Barcelona. A un lado de la Travessera de les Corts, una sección con {n(FA["renta"])} euros de renta dio al PP el {p(FA["PP"])} % y al PSC el {p(FA["PSOE"])} %. Al otro, una con {n(FB["renta"])} euros dio al PSC el {p(FB["PSOE"])} % y al PP el {p(FB["PP"])} %. Lo contamos en {L("capitales-partidas-por-barrios", "las capitales partidas por el voto")}.</p>
<h2>Medio siglo sin cruzarse</h2>
<p data-tipo="dato">Las dos ciudades llevan votando distinto desde 1977. Barcelona ha dado la victoria al PSC en nueve de las 16 generales, a CiU en tres (1989, 1993 y 2011), a En Comú Podem en dos (2015 y 2016) y a ERC en las dos de 2019. Madrid votó a UCD en 1977 y 1979, al PSOE en 1982, 1986 y abril de 2019, y a AP y después al PP en las otras once.</p>
{fig_tira}
<p data-tipo="dato">Solo han coincidido dos veces, en 1982 y 1986, y las dos con los socialistas delante. El PP no ha ganado nunca en Barcelona: es el mayor de los {L("nunca-gano-la-derecha", "864 municipios donde la derecha estatal nunca ha sido la más votada")}. Su mejor resultado allí fue el {p(pct(BCN, "2000_03", "PP"))} % de 2000, el año de la mayoría absoluta de José María Aznar, cuando en Madrid sacó el {p(pct(MAD, "2000_03", "PP"))} %.</p>
<p data-tipo="dato">Hay otra constante: Madrid ha votado más que Barcelona en las 16 generales. En 2023, la participación fue del {p(pct(MAD, E, "part"))} % en Madrid y del {p(pct(BCN, E, "part"))} % en Barcelona. La distancia más corta fue la de abril de 2019, {p(pct(MAD, "2019_04", "part"))} % frente a {p(pct(BCN, "2019_04", "part"))} %, y la más larga, la de 1979.</p>
<h2>La misma renta, otro voto</h2>
<p data-tipo="dato">Para comparar como se compara un partido, en igualdad de condiciones, hemos agrupado las secciones de las dos ciudades por tramos de renta. En las de 25.000 a 30.000 euros por unidad de consumo, que son {n(tb["n"])} en Barcelona y {n(tm["n"])} en Madrid, el PP sacó el {p(tb["PP"])} % en Barcelona y el {p(tm["PP"])} % en Madrid, tres veces más. En el tramo siguiente, de 30.000 a 35.000, el {p(t3b["PP"])} % frente al {p(t3m["PP"])} %.</p>
{fig_pp}
<p data-tipo="dato">En Barcelona, el voto al PP es casi plano en los barrios pobres y medios: está entre el 12 % y el 15 % en todos los tramos de menos de 35.000 euros. Solo despega arriba del todo. En las secciones de más de 50.000 euros llega al {p(xb["PP"])} %, por debajo de lo que el PP saca en Madrid en las secciones de 30.000 a 35.000. En Madrid sube en cada escalón, del {p(lm["PP"])} % en las secciones de menos de 20.000 euros al {p(xm["PP"])} % en las de más de 50.000.</p>
<p data-tipo="dato">Con el voto socialista pasa lo contrario: casi no hay diferencia. El PSC en Barcelona y el PSOE en Madrid bajan con la renta al mismo ritmo, del {p(lb["PSOE"])} % y el {p(lm["PSOE"])} % en los barrios de menos de 20.000 euros al {p(xb["PSOE"])} % y el {p(xm["PSOE"])} % en los de más de 50.000. En cada tramo, el PSC saca entre cuatro y siete puntos más, o algo más que el PSOE en Madrid.</p>
{fig_psoe}
<p data-tipo="patron">Una regresión con las {n(NSEC["BCN"] + NSEC["MAD"])} secciones lo confirma. Con un efecto fijo para cada ciudad y los errores agrupados por barrio ({NCL["BCN"]} en Barcelona y {NCL["MAD"]} en Madrid), una sección con el doble de renta que otra de su misma ciudad vota al PP {p(reg["PP"]["m"])} puntos más en Madrid y {p(reg["PP"]["b"])} puntos más en Barcelona. La diferencia entre las dos pendientes es estadísticamente significativa. Al PSOE, {p(-reg["PSOE"]["m"])} puntos menos en Madrid y {p(-reg["PSOE"]["b"])} en Barcelona, una diferencia que no es significativa. La participación sube con la renta en las dos ciudades a un ritmo parecido.</p>
<p data-tipo="dato">Los barrios ricos de Barcelona reparten su voto entre más partidos. En las secciones de más de 50.000 euros, el PP sacó el {p(xb["PP"])} %, Junts el {p(xb["JUNTS"])} %, Vox el {p(xb["VOX"])} % y el PSC el {p(xb["PSOE"])} %. En las de Madrid con la misma renta, el PP sacó el {p(xm["PP"])} % y Vox el {p(xm["VOX"])} %: entre los dos, cuatro de cada cinco votos.</p>
<p data-tipo="patron">Vox dibuja dos curvas distintas. En Madrid sube con la renta, del {p(vox_m[0])} % en el 10 % de secciones más pobres de la ciudad al {p(vox_m[-1])} % en el 10 % más rico. En Barcelona hace una U: el {p(vox_b[0])} % en el 10 % más pobre, el {p(min(vox_b))} % en los barrios de renta media alta y el {p(vox_b[-1])} % en el 10 % más rico. Es el mismo dibujo que Maldita encontró en 2019, cuando los mejores distritos de Vox en Barcelona fueron <a href="https://maldita.es/malditodato/20191115/vox-obtiene-peores-resultados-en-los-lugares-con-rentas-intermedias-y-logra-los-mejores-en-las-zonas-mas-pobres-y-en-las-mas-ricas/">Sarrià-Sant Gervasi y Nou Barris</a>, el más rico y el más pobre. Y el que el Ara vio en Cataluña en las autonómicas de 2024: Vox entra «en los barrios más ricos, pero sobre todo en los más pobres», escribía <a href="https://es.ara.cat/politica/elecciones-catalunya/barrios-pobres-ricos-vox-clase-media-alianca-catalana_1_5034199.html">Aleix Moldes</a>.</p>
<p data-tipo="hipotesis">Una explicación posible es que en Barcelona el voto se ordena con dos ejes a la vez, la renta y la cuestión nacional, y en Madrid sobre todo con uno. El voto de renta alta que en Madrid va al PP se reparte en Barcelona con Junts, y antes con CiU, y el de renta media que en Madrid también va al PP se queda en Barcelona en el PSC, ERC o los Comunes. Es compatible con los datos, pero no está demostrado: son datos de lugares, no de personas. En 2011, CiU ganaba al PP en el 65 % de las secciones de Cataluña y en 2023 Junts solo en el 40 %, como contamos en {L("frontera-renta-pp-junts-pnv-29n", "la frontera de renta entre el PP y Junts")}.</p>
<p data-tipo="contexto">Las dos ciudades se parecen en otra cosa: las dos votan por bloques de barrios. Con el índice de Moran, que mide si las secciones vecinas votan parecido, Barcelona (0,83) y Madrid (0,82) están entre las cuatro capitales más agrupadas de España. El politólogo Toni Rodon (Universitat Pompeu Fabra) lo resumía para Barcelona: «[...] los pobres están cada vez más juntos y los ricos viven cada vez más entre ricos. Los dos polos se van separando» (<a href="https://www.eldiario.es/catalunya/toni-rodon-politologo-segregacion-favorece-voto-extrema-derecha_1_10076472.html">elDiario.es</a>).</p>
<h2>De 2019 a 2023, en direcciones opuestas</h2>
<p data-tipo="dato">Entre las generales de noviembre de 2019 y las de julio de 2023 cambió el ganador de más de la mitad de las secciones de Barcelona y de más de una de cada cuatro de Madrid, y lo hizo hacia lados opuestos. En Barcelona, el PSC pasó a ganar en {n(ERC_PSC)} secciones donde antes ganaba ERC, y acabó primero en {n(G23["BCN"]["PSOE"])} de las {n(NSEC["BCN"])}. Lo contamos en {L("barcelona-barrio-a-barrio-29n", "Barcelona barrio a barrio")}.</p>
<p data-tipo="dato">En Madrid, el PP pasó a ganar en {n(PSOE_PP)} secciones donde antes ganaba el PSOE y acabó primero en {n(G23["MAD"]["PP"])} de {n(NSEC["MAD"])}. El PSOE solo resistió en cuatro distritos del sur, como explicamos en {L("madrid-barrio-a-barrio-29n", "Madrid barrio a barrio")}.</p>
<p data-tipo="contexto">Ninguna de las dos es una circunscripción: los diputados se eligen por provincia. Barcelona reparte 32 escaños y Madrid, 38 a partir de este año, uno más que en 2023, por el <a href="https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-20742">Real Decreto 806/2026</a>. Pero las dos capitales ponen una parte muy grande de esos votos: {n(serie[BCN][E]["censo"])} electores en Barcelona y {n(serie[MAD][E]["censo"])} en Madrid, sin contar el voto exterior.</p>
<p data-tipo="contexto">No hay encuestas públicas por ciudad para el 29N. Lo que dicen las encuestas para el conjunto de España y para cada provincia está en {L("asi-queda-el-mapa-29n", "así queda el mapa antes del 29N")} y en {L("provincias-en-el-filo-29n", "las provincias que deciden el 29N")}. Esta noche, a las nueve, el Camp Nou y el Bernabéu vuelven a medirse. Dentro de cinco domingos, también sus barrios.</p>
'''

preguntas = [
    ('¿Ha ganado alguna vez el PP en Barcelona en unas elecciones generales?',
     f'No. En las 16 generales desde 1977, ni el PP ni su antecesora AP han sido nunca el partido más votado en Barcelona. Su mejor resultado fue el {p(pct(BCN, "2000_03", "PP"))} % de 2000.'),
    ('¿Qué partido ganó en Barcelona y en Madrid en las generales de 2023?',
     f'En Barcelona, el PSC, con el {p(pct(BCN, E, "PSOE"))} % de los votos; en Madrid, el PP, con el {p(pct(MAD, E, "PP"))} %.'),
    ('¿Cómo votan los barrios ricos de Barcelona y de Madrid?',
     f'En las secciones de más de 50.000 euros de renta por unidad de consumo, el PP sacó en 2023 el {p(xm["PP"])} % en Madrid y el {p(xb["PP"])} % en Barcelona, donde Junts sacó el {p(xb["JUNTS"])} % y Vox el {p(xb["VOX"])} %.'),
    ('¿Cómo votó el barrio del Camp Nou?',
     f'En la Maternitat i Sant Ramon, el barrio del Camp Nou, ganó el PSC con el {p(CN["PSOE"])} % en 2023, seguido del PP ({p(CN["PP"])} %).'),
    ('¿Cómo votó el barrio del Bernabéu?',
     f'En Hispanoamérica, el barrio del Santiago Bernabéu, el PP sacó el {p(BE["PP"])} % en 2023, Vox el {p(BE["VOX"])} % y el PSOE el {p(BE["PSOE"])} %.'),
    ('¿Se vota más en Madrid o en Barcelona?',
     f'En Madrid, en las 16 generales desde 1977. En 2023, la participación fue del {p(pct(MAD, E, "part"))} % en Madrid y del {p(pct(BCN, E, "part"))} % en Barcelona.'),
    ('¿Dónde puedo ver cómo votó mi calle de Barcelona o de Madrid?',
     f'En el <a href="{BASE}">mapa electoral de la portada</a>, escribiendo la dirección, o en las fichas de <a href="{BASE}municipio/barcelona/barcelona/">Barcelona</a> y <a href="{BASE}municipio/madrid/madrid/">Madrid</a>, barrio a barrio.'),
]

enlaces = (f'<a href="{BASE}municipio/barcelona/barcelona/">Barcelona, barrio a barrio</a> · <a href="{BASE}municipio/madrid/madrid/">Madrid, barrio a barrio</a> · '
           f'{L("capitales-partidas-por-barrios", "Las capitales partidas por el voto")} · {L("frontera-renta-pp-junts-pnv-29n", "La frontera de renta entre el PP y Junts")}')
foot = ('Datos: Ministerio del Interior, generales de 1977 a 2023 (por municipio hasta 2000 y por sección desde 2004, sin voto exterior), '
        'vía Infoelectoral y pollspaindata; INE, Atlas de Distribución de Renta de los Hogares 2023; barrios de OpenStreetMap. Cálculo propio.')

pieza('barcelona-madrid-clasico-del-voto-29n', 'El otro Clásico: Barcelona y Madrid, ciudad a ciudad',
      'El otro Clásico: en los barrios de renta media, el PP saca el triple de votos en Madrid que en Barcelona',
      f'Barcelona y Madrid, sección a sección, el día del Barça-Madrid: con la misma renta, el PP sacó en 2023 el {p(tm["PP"])} % en Madrid y el {p(tb["PP"])} % en Barcelona. El voto socialista cae igual en las dos; lo que cambia es quién recoge el de los barrios ricos. Y en 16 generales, el PP nunca ha ganado en Barcelona.',
      '25 de octubre de 2026', cuerpo, preguntas, enlaces, foot)
