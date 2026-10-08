"""Controles automáticos del Atlas. Se ejecutan después de construir.py y antes de paginas.py.

Cada control comprueba una cifra o una afirmación de las piezas contra los datos. Si alguno falla, el script
termina con error y escribe el informe en atlas/src/controles.txt. Pasar los controles NO publica nada: la
revisión humana (muestra manual y campo `revisado`) sigue siendo obligatoria.
"""
import csv
import json
import math
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
ATLAS = SRC.parent
sys.path.insert(0, str(SRC))
from graficos import num  # noqa: E402
from piezas import piezas, SERIES  # noqa: E402
from piezas2 import piezas2  # noqa: E402
from piezas3 import piezas3  # noqa: E402
from titulares import TITULARES, titular  # noqa: E402

# Resultado oficial del 23J de 2023 (Congreso, 350 escaños), para comprobar el reparto D'Hondt recalculado.
OFICIAL_2023 = {'PP': 137, 'PSOE': 121, 'Vox': 33, 'Sumar': 31, 'ERC': 7, 'Junts': 7, 'EH Bildu': 6, 'PNV': 5,
                'BNG': 1, 'UPN': 1, 'CC': 1}
CAUSALES = re.compile(r'\b(porque|debido a|a causa de|causa|provoca|se debe a|gracias a)\b', re.I)

resultados = []
CONG3 = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']


def control(nombre, ok, detalle=''):
    resultados.append((bool(ok), nombre, detalle))


def planos(x, out):
    """Todos los números de cifras.json, para buscar las cifras citadas en el texto."""
    if isinstance(x, dict):
        for v in x.values():
            planos(v, out)
    elif isinstance(x, list):
        for v in x:
            planos(v, out)
    elif isinstance(x, (int, float)) and not isinstance(x, bool):
        out.add(x)
    return out


def main():
    C = json.load(open(SRC / 'cifras.json'))
    P = piezas(C) + piezas2(C) + piezas3(C)

    # 1. Universo y reparto de escaños
    control('8.131 municipios en la base', C['fuente_datos']['n_municipios'] == 8131, C['fuente_datos']['n_municipios'])
    control('D\'Hondt con CERA reproduce los 350 escaños oficiales de 2023', C['escanos_2023_con_cera'] == OFICIAL_2023,
            C['escanos_2023_con_cera'])
    m = C['madrid']
    control('Madrid con CERA reproduce el reparto oficial (PP 16, PSOE 10, Sumar 6, Vox 5)',
            m['con_cera'] == {'PP': 16, 'PSOE': 10, 'Sumar': 6, 'Vox': 5}, m['con_cera'])
    for prov, d in C['escanos_29n'].items():
        control(f'29N provincia {prov}: 2026 suma un escaño {"más" if prov == "28" else "menos"} que 2023',
                sum(d['2026'].values()) - sum(d['2023'].values()) == (1 if prov == '28' else -1))
    control('Márgenes ordenados de menor a mayor', all(a['votos_que_faltaban'] <= b['votos_que_faltaban']
                                                     for a, b in zip(C['margenes'], C['margenes'][1:])))

    # 2. Afirmaciones con nombre propio en el texto
    cp = {f['capital']: f for f in C['capitales']}
    orden = sorted(C['capitales'], key=lambda f: f['dif_pp'])
    control('50 capitales', len(cp) == 50, len(cp))
    control('Capitales: más PP + menos PP = 50', C['capitales_resumen']['mas_pp'] + C['capitales_resumen']['menos_pp'] == 50)
    control('Granada es la capital con más PP respecto a su provincia', orden[-1]['capital'] == 'Granada', orden[-1]['capital'])
    top3 = [f['capital'] for f in orden[-3:]]
    control('Donostia y Vitoria van detrás de Granada', any('Donostia' in c for c in top3) and any('Vitoria' in c for c in top3), top3)
    control('Ourense y Soria, las que menos PP, con la misma cifra redondeada',
            {orden[0]['capital'], orden[1]['capital']} == {'Ourense', 'Soria'} and num(orden[0]['dif_pp']) == num(orden[1]['dif_pp']),
            [(f['capital'], f['dif_pp']) for f in orden[:2]])
    for c in ['Ourense', 'Soria', 'Lugo', 'Palencia']:
        control(f'{c}: menos PP y más PSOE que su provincia', cp[c]['dif_pp'] < 0 and cp[c]['dif_psoe'] > 0, (cp[c]['dif_pp'], cp[c]['dif_psoe']))
    for c in ['Granada', 'Badajoz', 'Córdoba', 'Sevilla']:
        control(f'{c}: más PP que su provincia', cp[c]['dif_pp'] > 0, cp[c]['dif_pp'])
    for c in ['Granada', 'Badajoz', 'Córdoba']:
        control(f'{c}: PSOE por debajo de su provincia', cp[c]['dif_psoe'] < 0, cp[c]['dif_psoe'])
    vascas_cat = [c for c in cp if any(k in c for k in ('Bilbao', 'Donostia', 'Vitoria', 'Barcelona', 'Girona', 'Lleida', 'Tarragona'))]
    control('Capitales vascas y catalanas: más PP que su entorno', len(vascas_cat) == 7 and all(cp[c]['dif_pp'] > 0 for c in vascas_cat),
            {c: cp[c]['dif_pp'] for c in vascas_cat})

    ms = {f['municipio']: f for f in C['madrid_sur']['municipios']}
    for c, g in [('Parla', 'PSOE'), ('Fuenlabrada', 'PSOE'), ('Leganés', 'PSOE'), ('Getafe', 'PSOE'), ('Móstoles', 'PP'), ('Alcorcón', 'PP')]:
        control(f'Sur de Madrid: {c} lo gana el {g}', c in ms and ms[c]['gana'] == g, ms.get(c, {}).get('gana'))
    control('Madrid provincia: PP por delante del PSOE', C['madrid_sur']['prov_pp'] > C['madrid_sur']['prov_psoe'])

    # Afirmaciones nuevas de la versión larga de los textos
    mg = C['margenes']
    seis = mg[:C['margenes_menos_1500']]
    control('Escaños ajustados: los seis primeros son Girona, Cantabria, Tarragona, Madrid, Albacete y Salamanca',
            [f['provincia'] for f in seis] == ['Girona', 'Cantabria', 'Tarragona', 'Madrid', 'Albacete', 'Salamanca'], [f['provincia'] for f in seis])
    control('Escaños ajustados: Junts tiene el último escaño en Girona y Tarragona', sorted(f['provincia'] for f in seis if f['ultimo_escano'] == 'Junts') == ['Girona', 'Tarragona'])
    control('Escaños ajustados: en Girona y Cantabria aspira el PP; en Madrid y Salamanca, el PSOE frente al PP',
            all(f['aspirante'] == 'PP' for f in seis[:2]) and all(f['aspirante'] == 'PSOE' and f['ultimo_escano'] == 'PP' for f in seis if f['provincia'] in ('Madrid', 'Salamanca')))
    control('Madrid es el cuarto margen más estrecho', mg[3]['provincia'] == 'Madrid')
    control('Cádiz 2026: empate PP-PSOE', C['escanos_29n']['11']['2026']['PP'] == C['escanos_29n']['11']['2026']['PSOE'])
    control('Madrid: el CERA del PP es casi el doble que el del PSOE (entre 1,7 y 2)', 1.7 <= m['cera_pp'] / m['cera_psoe'] < 2)
    msm = {r['municipio']: r for r in C['madrid_sur']['municipios']}
    s4 = ['Parla', 'Fuenlabrada', 'Leganés', 'Getafe']
    control('Sur de Madrid: la izquierda superaba el 60 % en 2004 en las cuatro', all(msm[n]['izq_2004'] > 60 for n in s4))
    control('Sur de Madrid: en 2023 la izquierda estaba entre el 52 y el 54 % en las cuatro', all(52 <= msm[n]['izq_2023'] < 54 for n in s4))
    control('Móstoles y Alcorcón: derecha por encima de la izquierda', all(msm[n]['der_2023'] > msm[n]['izq_2023'] for n in ('Móstoles', 'Alcorcón')))
    sur6 = [r for r in C['madrid_sur']['municipios'] if r['grupo'] == 'sur']
    control('Parla: mayor caída de la izquierda y la más alta en 2004', max(sur6, key=lambda r: r['izq_2004'] - r['izq_2023'])['municipio'] == 'Parla' == max(sur6, key=lambda r: r['izq_2004'])['municipio'])
    control('Noroeste de Madrid: derecha por encima del 70 %', all(r['der_2023'] > 70 for r in C['madrid_sur']['municipios'] if r['grupo'] == 'noroeste'))
    a = C['arousa']
    for k in ('illa', 'vilanova'):
        control(f'Arousa {k}: mejor año del PP 2011 y peor abril de 2019', max(a[k]['pp'], key=a[k]['pp'].get) == '2011_11' and min(a[k]['pp'], key=a[k]['pp'].get) == '2019_04')
    control('A Illa: menos paro y menos extranjeros que Vilanova', a['illa']['paro'] < a['vilanova']['paro'] and a['illa']['extranjeros'] < a['vilanova']['extranjeros'])
    control('A Illa: el PSOE fue primero en 2023 y el BNG duplica al de Vilanova', a['illa']['psoe_2023'] > a['illa']['pp']['2023_07'] and a['illa']['bng_2023'] > 2 * a['vilanova']['bng_2023'])
    cm2 = C['cabra_montilla']
    control('Cabra: Vox en noviembre de 2019 en torno a uno de cada cuatro votos (23-27 %)', 23 <= cm2['cabra']['vox']['2019_11'] <= 27)
    control('Cabra gana el PP y Montilla el PSOE en 2023', cm2['cabra']['gana_2023'] == 'PP' and cm2['montilla']['gana_2023'] == 'PSOE')
    for n in ('Ourense', 'Soria', 'Ávila', 'Lugo', 'Palencia', 'Zamora', 'A Coruña'):
        control(f'{n}: la capital vota menos al PP', cp[n]['dif_pp'] < 0)
    control('Ávila: menos PP y menos PSOE en la capital', cp['Ávila']['dif_pp'] < 0 and cp['Ávila']['dif_psoe'] < 0)
    control('Vitoria y Lleida: más PP y más PSOE en la capital', all(cp[c]['dif_pp'] > 0 and cp[c]['dif_psoe'] > 0 for c in ('Vitoria-Gasteiz', 'Lleida')))
    control('Málaga, Cádiz, Almería y Huelva: menos de 1,5 puntos de diferencia', all(abs(cp[c]['dif_pp']) < 1.5 for c in ('Málaga', 'Cádiz', 'Almería', 'Huelva')))
    control('Madrid, Barcelona y València: algo más de PP que su provincia (0-5 puntos)', all(0 < cp[c]['dif_pp'] < 5 for c in ('Madrid', 'Barcelona', 'València')))
    for c in ('Sevilla', 'Cáceres', 'Jaén'):
        control(f'{c}: más PP y menos PSOE que su provincia', cp[c]['dif_pp'] > 0 and cp[c]['dif_psoe'] < 0)
    bb = C['badalona']
    control('Badalona julio: PP por delante de Sumar', bb['2023_07']['PP'] > bb['2023_07']['SUMAR'])
    control('Badalona: la brecha PP municipales-generales crece en cada ciclo',
            bb['M2015']['PP'] - bb['2015_12']['PP'] < bb['M2019']['PP'] - bb['2019_11']['PP'] < bb['M2023']['PP'] - bb['2023_07']['PP'])
    pa = C['paro']
    qq = pa['quintil_renta_tercil_paro']
    control('Paro: la diferencia por paro se encoge del quintil 1 al 4', all((qq[str(k)]['1'] - qq[str(k)]['3']) > (qq[str(k + 1)]['1'] - qq[str(k + 1)]['3']) for k in range(1, 4)))
    ct = pa['cataluna']
    control('Cataluña: el paro pesa casi el doble en municipales y Parlament que en generales (1,7-2,1 veces)',
            all(1.7 <= ct[e]['paro'] / ct['g2023']['paro'] <= 2.1 for e in ('m2023', 'p2024')))
    control('Cataluña: la renta, una vez controlado lo demás, por debajo de 1 punto en las tres', all(abs(ct[e]['renta']) < 1 for e in ct))
    pr = C['puerto_real']
    rk = C['ranking_residuo_derecha_10k']
    control('Puerto Real es la mayor excepción a la baja (≥10.000 hab.)', rk[0]['municipio'] == 'Puerto Real' and pr['rank'] == 1)
    control('Puerto Real: diferencia = real − previsto', abs(pr['der'] - pr['previsto'] - pr['diferencia']) <= 0.11)
    control('Puerto Real: el PSOE ganó allí y el PP en la provincia', pr['psoe'] > pr['pp'] and pr['prov_pp'] > pr['prov_psoe'])

    cm = C['cabra_montilla']
    control('Cabra y Montilla partían del mismo voto a la derecha en 2004',
            abs(cm['cabra']['der']['2004_03'] - cm['montilla']['der']['2004_03']) < 2,
            (cm['cabra']['der']['2004_03'], cm['montilla']['der']['2004_03']))

    b = C['badalona']
    for e, v in b.items():
        if not isinstance(v, dict) or 'part' not in v:
            continue
        s = sum(x for k, x in v.items() if k != 'part')
        control(f'Badalona {e}: las candidaturas suman entre 97 y 100 % del voto válido (el resto es voto en blanco)', 97 <= s <= 100.05, round(s, 1))
    control('Badalona: primera en diferencia PP municipales − generales', b['top'][0]['municipio'] == 'Badalona' and b['rank_pp_20k'] == 1)

    control('Modelo municipal: R² entre 0 y 1', 0 < C['modelo_municipal']['r2_derecha'] < 1)
    control('Participación: R² del modelo por secciones mayor que el de la renta sola', C['paro']['r2'] > C['paro']['r2_solo_renta'])

    # Segunda tanda (2026-10-07)
    cu = C['cuencas']
    cmm = {x['municipio']: x for x in cu['municipios']}
    seis = [r['municipio'] for r in cu['asturias_modelo'][:6]]
    control('Asturias: los seis municipios más por debajo del modelo son de las cuencas',
            set(seis) == {'San Martín del Rey Aurelio', 'Mieres', 'Langreo', 'Laviana', 'Lena', 'Aller'}, seis)
    control('Cuencas: el PSOE fue primero en los cinco municipios el 23J', all(x['gana'] == 'PSOE' for x in cu['municipios']))
    control('Asturias: el PP ganó la comunidad', cu['asturias_pp'] > cu['asturias_psoe'])
    control('Cuencas: Mieres y Langreo las ganó IU en mayo; San Martín, Laviana y Aller, el PSOE',
            all('IU' in cmm[n]['m2023_lista'] for n in ('Mieres', 'Langreo')) and all('SOCIALISTA' in cmm[n]['m2023_lista'] for n in ('San Martín del Rey Aurelio', 'Laviana', 'Aller')))
    la = C['lalin']
    control('Lalín y Vilanova: primera y segunda mayores diferencias al alza, ambas en Pontevedra',
            la['rango_lalin'] == 1 and la['rango_vilanova'] == 2 and all(r['provincia'] == 'Pontevedra' for r in la['top'][:2]))
    control('Lalín: mejor año del PP 2011 y peor abril de 2019', max(la['lalin']['pp'], key=la['lalin']['pp'].get) == '2011_11' and min(la['lalin']['pp'], key=la['lalin']['pp'].get) == '2019_04')
    control('A Illa vota al PP más de 20 puntos menos que Vilanova en todas las generales', all(C['arousa']['vilanova']['pp'][e] - C['arousa']['illa']['pp'][e] > 20 for e in C['arousa']['illa']['pp']))
    pmm = {x['municipio']: x for x in C['pamplona']['municipios']}
    control('Cuenca de Pamplona: Cizur tiene la renta más alta', max(C['pamplona']['municipios'], key=lambda x: x['renta'])['municipio'] == 'Cizur')
    control('Cuenca de Pamplona: Villava la gana EH Bildu y Ansoáin el PSOE', pmm['Villava/Atarrabia']['gana'] == 'BILDU' and pmm['Ansoáin/Antsoain']['gana'] == 'PSOE')
    control('Cuenca de Pamplona: Ansoáin, Villava y Burlada por debajo de lo previsto; Egüés y Cizur por encima',
            all(pmm[n]['diferencia'] < 0 for n in ('Ansoáin/Antsoain', 'Villava/Atarrabia', 'Burlada/Burlata')) and all(pmm[n]['diferencia'] > 0 for n in ('Cizur', 'Valle de Egüés/Eguesibar')))
    gmm = {x['municipio']: x for x in C['getxo']['municipios']}
    ge, po = gmm['Getxo'], gmm['Portugalete']
    control('Ría: el PSOE gana en las cuatro de la margen izquierda y el PNV en Getxo y Leioa',
            all(gmm[n]['gana'] == 'PSOE' for n in ('Portugalete', 'Santurtzi', 'Sestao', 'Barakaldo')) and all(gmm[n]['gana'] == 'PNV' for n in ('Getxo', 'Leioa')))
    control('Ría: Getxo, más renta y menos paro de la tabla', ge['renta'] == max(x['renta'] for x in gmm.values()) and ge['paro'] == min(x['paro'] for x in gmm.values()))
    control('Ría: PP de Getxo más del doble que en Portugalete y que en Bizkaia', ge['pp']['2023_07'] > 2 * po['pp']['2023_07'] and ge['pp']['2023_07'] > 2 * C['getxo']['bizkaia']['pp'])
    am = C['aranda_miranda']
    ar, mi = am['aranda'], am['miranda']
    control('Burgos: Miranda y Aranda, las más pobladas después de la capital', am['burgos_mayores'] == ['Burgos', 'Miranda de Ebro', 'Aranda de Duero'], am['burgos_mayores'])
    control('Aranda y Miranda: mismo previsto redondeado', num(ar['previsto']) == num(mi['previsto']), (ar['previsto'], mi['previsto']))
    control('Aranda la gana el PP y Miranda el PSOE (23J); en mayo, PP por poco en Aranda y PSOE en Miranda',
            ar['gana'] == 'PP' and mi['gana'] == 'PSOE' and ar['m2023']['gana'] == 'PP' and 0 < ar['m2023']['pp'] - ar['m2023']['psoe'] < 1 and mi['m2023']['gana'] == 'PSOE')
    control('Aranda y Miranda: la distancia en el voto a la derecha creció de 2004 a 2023', ar['der']['2023_07'] - mi['der']['2023_07'] > ar['der']['2004_03'] - mi['der']['2004_03'])
    lpz = C['los_palacios']
    lp = lpz['lp']
    control('Los Palacios: en 2004 el PSOE por encima de su provincia y la derecha por debajo; en 2023 la derecha por encima',
            lp['psoe']['2004_03'] > lpz['sevilla_psoe']['2004_03'] and lp['der']['2004_03'] < lpz['sevilla_der']['2004_03'] and lp['der']['2023_07'] > lpz['sevilla_der']['2023_07'])
    control('Los Palacios: el PSOE no sube desde 2015 y gana el PP el 23J',
            all(lp['psoe'][a] >= lp['psoe'][b] for a, b in zip(['2015_12', '2016_06', '2019_04', '2019_11'], ['2016_06', '2019_04', '2019_11', '2023_07'])) and lp['gana'] == 'PP')
    control('Los Palacios: en mayo ganó una lista de IU con casi la mitad; en julio la derecha pasó de la mitad',
            'IZQUIERDA UNIDA' in lp['m2023_lista'] and 45 <= lp['m2023_lista_pct'] < 50 and lp['der']['2023_07'] > 50)
    ca = C['castro']
    cs = ca['castro']
    control('Castro: 2.ª mayor diferencia a la baja, detrás de Puerto Real', ca['rango'] == 2 and C['ranking_residuo_derecha_10k'][0]['municipio'] == 'Puerto Real')
    control('Castro: la derecha, al menos 10 puntos por debajo de Cantabria en las ocho generales', all(ca['cantabria_der'][e] - cs['der'][e] >= 10 for e in cs['der']))
    control('Castro: PSOE por delante del PP en 2004, 2008, 2019 y 2023; PP en 2011, 2015 y 2016',
            all(cs['psoe'][e] > cs['pp'][e] for e in ('2004_03', '2008_03', '2019_04', '2019_11', '2023_07')) and all(cs['pp'][e] > cs['psoe'][e] for e in ('2011_11', '2015_12', '2016_06')))
    control('Castro: el PSOE fue primero en las municipales', cs['m2023']['gana'] == 'PSOE')
    vg = C['vigo']
    v = vg['vigo']
    control('Galicia: el PP gana en las seis grandes ciudades salvo Vigo', vg['ciudades'][0]['municipio'] == 'Vigo' and vg['ciudades'][0]['gana'] == 'PSOE' and all(c['gana'] == 'PP' for c in vg['ciudades'][1:]))
    control('Galicia: de los municipios de más de 20.000, el PSOE solo gana en dos', len(vg['psoe_gana_20k']) == 2)
    control('Vigo: PSOE por delante del PP desde abril de 2019 y PP por delante en 2011', all(v['psoe'][e] > v['pp'][e] for e in ('2019_04', '2019_11', '2023_07')) and v['pp']['2011_11'] > v['psoe']['2011_11'])
    t = {x['tamano']: x for x in C['pequenos']['tamanos']}
    pq = C['pequenos']
    control('Participación: en el conjunto se votó más en julio', pq['total_generales'] > pq['total_municipales'])
    control('Participación: por debajo de 2.000 habitantes, más en municipales en todos los tramos; por encima, más en generales',
            all(t[k]['part_municipales'] > t[k]['part_generales'] for k in ('<100', '100-249', '250-499', '500-999', '1.000-1.999'))
            and all(t[k]['part_municipales'] < t[k]['part_generales'] for k in list(t)[5:]))
    control('Participación: en 250-1.000 hab., en torno a dos de cada tres (60-70 %); en +100.000, ninguna',
            all(60 <= t[k]['pct_mas_municipales'] <= 70 for k in ('250-499', '500-999')) and t['100.000+']['pct_mas_municipales'] == 0)

    # Tercera tanda (2026-10-07)
    jj = C['jodar']
    jo, jp = jj['jodar'], jj['jaen_part']
    control('Jódar: mayor diferencia a la baja en participación (≥10.000 hab.)', jo['rango_part'] == 1 and jj['top'][0]['municipio'] == 'Jódar')
    control('Jódar: diferencia de participación = real − previsto', abs(jo['part_serie']['2023_07'] - jo['previsto_part'] - jo['diferencia_part']) <= 0.11)
    control('Jódar: votó más que su provincia en 2004 y menos en todas las generales desde 2008',
            jo['part_serie']['2004_03'] > jp['2004_03'] and all(jo['part_serie'][e] < jp[e] for e in CONG3[1:]))
    control('Jódar: la participación en las generales baja en cada elección desde 2004 salvo empates',
            all(jo['part_serie'][a] >= jo['part_serie'][b] for a, b in zip(CONG3, CONG3[1:])))
    rh = jj['res_hist']
    control('Jódar: segunda mayor diferencia en abril y noviembre de 2019 y primera en 2023',
            rh['2019_04']['rango'] == 2 and rh['2019_11']['rango'] == 2 and rh['2023_07']['rango'] == 1)
    control('Jódar: en las municipales de 2023 votó más que en las generales de julio y menos que su provincia',
            jo['part_serie']['M2023'] > jo['part_serie']['2023_07'] and jo['part_serie']['M2023'] < jp['M2023'])
    j10 = {x['municipio']: x for x in jj['jaen_10k']}
    control('Jódar: Úbeda vota lo previsto (±0,5) y Baeza algo más', abs(j10['Úbeda']['diferencia']) <= 0.5 and j10['Baeza']['diferencia'] > 0)
    control('Jódar: Mancha Real tiene una población parecida (±5 %)', abs(j10['Mancha Real']['poblacion'] / jo['poblacion'] - 1) <= 0.05)
    va = {x['municipio']: x for x in C['valles']['municipios']}
    sc, ba, mt, te = va['Sant Cugat del Vallès'], va['Badia del Vallès'], va['Matadepera'], va['Terrassa']
    control('Vallès: el PSC gana en Sant Cugat y Badia; Junts en Matadepera; PSC en Terrassa',
            sc['gana'] == 'PSOE' and ba['gana'] == 'PSOE' and mt['gana'] == 'JUNTS' and te['gana'] == 'PSOE')
    control('Vallès: en Sant Cugat el PSC por delante del PP y el PP por delante de Junts', sc['psoe']['2023_07'] > sc['pp']['2023_07'] > sc['junts']['2023_07'])
    control('Vallès: renta de Sant Cugat al menos el doble que la de Badia', sc['renta'] >= 2 * ba['renta'])
    control('Vallès: derecha casi igual en Sant Cugat y Badia (menos de 2 puntos)', abs(sc['der']['2023_07'] - ba['der']['2023_07']) < 2)
    control('Vallès: PP más alto en Sant Cugat y Vox más alto en Badia', sc['pp']['2023_07'] > ba['pp']['2023_07'] and ba['vox']['2023_07'] > sc['vox']['2023_07'])
    control('Vallès: el modelo acierta en Sant Cugat (±3) y se queda corto en Badia', abs(sc['diferencia']) <= 3 and ba['diferencia'] > 5)
    control('Vallès: en mayo ganó el PSC en Badia y Junts en Sant Cugat', 'SOCIALISTES' in ba['m2023_lista'] and 'JUNTS' in sc['m2023_lista'])
    oo = C['ontigola']
    om = {x['municipio']: x for x in oo['municipios']}
    on, arj = om['Ontígola'], om['Aranjuez']
    control('Ontígola: Vox gana el 23J y es el segundo municipio más poblado de los que ganó', on['gana'] == 'VOX' and oo['vox_gana_mayores'][1] == 'Ontígola')
    control('Ontígola: en Aranjuez gana el PP', arj['gana'] == 'PP')
    control('Ontígola: renta casi igual a la de Aranjuez (menos de 1.000 euros)', abs(on['renta'] - arj['renta']) < 1000)
    control('Ontígola: Vox por encima del PP; derecha total por debajo de lo previsto', on['vox']['2023_07'] > on['pp']['2023_07'] and on['diferencia'] < 0)
    control('Ontígola: en mayo ganó el PSOE', 'SOCIALISTA' in on['m2023_lista'] and on['m2023']['gana'] == 'PSOE')
    control('Ontígola: la Sagra toledana da a Vox más que la media de España', all(p['vox']['2023_07'] > oo['espana_vox'] for p in oo['municipios'] if p['provincia'] == 'Toledo'))
    control('Ontígola: vecinos de Aranjuez algo mayores', arj['edad'] > on['edad'])
    rr = {x['municipio']: x for x in C['ria']['municipios']}
    control('Morrazo: el PP gana las generales en los seis', all(p['gana'] == 'PP' for p in rr.values()))
    control('Morrazo: Moaña y Cangas por debajo de lo previsto (entre −5 y −7); Sanxenxo, Marín y Poio por encima; Bueu en medio',
            all(-7 <= rr[n]['diferencia'] <= -5 for n in ('Moaña', 'Cangas')) and all(rr[n]['diferencia'] > 5 for n in ('Sanxenxo', 'Marín', 'Poio'))
            and rr['Moaña']['diferencia'] < rr['Bueu']['diferencia'] < rr['Poio']['diferencia'])
    control('Morrazo: Cangas el menor voto a la derecha y Sanxenxo el mayor', min(rr.values(), key=lambda p: p['der']['2023_07'])['municipio'] == 'Cangas'
            and max(rr.values(), key=lambda p: p['der']['2023_07'])['municipio'] == 'Sanxenxo')
    control('Morrazo: el BNG gana en mayo en Moaña y Bueu; el PP en Cangas, Sanxenxo y Marín (más del 55 % en estos dos)',
            'BLOQUE' in rr['Moaña']['m2023_lista'] and 'BLOQUE' in rr['Bueu']['m2023_lista'] and all('POPULAR' in rr[n]['m2023_lista'] for n in ('Cangas', 'Sanxenxo', 'Marín'))
            and all(rr[n]['m2023']['pp'] > 55 for n in ('Sanxenxo', 'Marín')))
    control('Morrazo: el BNG de Moaña cae hasta 2016 y vuelve a subir', min(rr['Moaña']['bng'], key=rr['Moaña']['bng'].get) == '2016_06')
    cc = {x['municipio']: x for x in C['campina']['municipios']}
    ah, mc = cc['Arahal'], cc['Marchena']
    control('Campiña: renta de Arahal y Marchena a menos de 200 euros', abs(ah['renta'] - mc['renta']) < 200)
    control('Campiña: el PSOE gana el 23J en Arahal y Marchena; Écija la gana el PP', ah['gana'] == mc['gana'] == 'PSOE' and cc['Écija']['gana'] == 'PP')
    control('Campiña: en mayo IU gana en Arahal y el PSOE en Marchena', 'IZQUIERDA UNIDA' in ah['m2023_lista'] and 'SOCIALISTA' in mc['m2023_lista'])
    control('Campiña: la distancia de la derecha entre Marchena y Arahal crece de 2004 a 2023', mc['der']['2023_07'] - ah['der']['2023_07'] > mc['der']['2004_03'] - ah['der']['2004_03'])
    control('Campiña: Osuna más cerca de Arahal que de Marchena', abs(cc['Osuna']['der']['2023_07'] - ah['der']['2023_07']) < abs(cc['Osuna']['der']['2023_07'] - mc['der']['2023_07']))
    mn = C['manilva']
    mv = mn['municipios'][0]
    control('Manilva: mayor caída relativa de la izquierda (≥10.000 hab.) y Los Palacios segunda', mn['top'][0]['municipio'] == 'Manilva' and mn['top'][1]['municipio'] == 'Los Palacios y Villafranca')
    control('Manilva: ganadores PSOE 2004, 2015, abr. 2019; PP 2008, 2011, 2016, 2023; Vox nov. 2019',
            list(mv['gana_serie'].values()) == ['PSOE', 'PP', 'PP', 'PSOE', 'PP', 'PSOE', 'VOX', 'PP'], mv['gana_serie'])
    control('Manilva: Estepona entre los municipios de Málaga que ganó Vox en noviembre de 2019', mn['vox_gana_2019_11_malaga'] >= 2)
    control('Manilva: el municipio con más extranjeros de Málaga entre los de más de 10.000', mn['rango_extranjeros_malaga_10k'] == 1)
    control('Manilva: en mayo ganó una candidatura local', 'MANILVA' in mv['m2023_lista'])
    ac = C['alcoi']
    al = ac['alcoi']
    control('Alcoi: el PSOE gana y el PP gana la provincia', al['gana'] == 'PSOE' and ac['margen_provincia'] < 0)
    control('Alcoi: mayor ventaja del PSOE entre los municipios alicantinos de más de 20.000; Elda y Dénia detrás',
            [x['municipio'] for x in ac['alicante_20k'][:3]] == ['Alcoi/Alcoy', 'Elda', 'Dénia'])
    control('Alcoi: izquierda sube de 2004 a 2023 y en la provincia baja', al['izq']['2023_07'] > al['izq']['2004_03'] and ac['alicante_izq']['2023_07'] < ac['alicante_izq']['2004_03'])
    control('Alcoi: Sumar y afines ganan en 2015 y 2016; el PP solo en 2011', al['sumar']['2015_12'] > max(al['pp']['2015_12'], al['psoe']['2015_12'])
            and al['sumar']['2016_06'] > max(al['pp']['2016_06'], al['psoe']['2016_06']) and al['pp']['2011_11'] > al['psoe']['2011_11'])
    control('Alcoi: en mayo el PSOE por delante del PP por menos de 1 punto', 'SOCIALISTA' in al['m2023_lista'] and 0 < al['m2023']['psoe'] - al['m2023']['pp'] < 1)
    km_ = C['capitales_mun']
    kc = {x['capital']: x for x in km_['capitales']}
    control('Capitales: 50 capitales', len(km_['capitales']) == 50)
    control('Capitales: las seis con más distancia a la baja son Zamora, Soria, Cuenca, Badajoz y, empatadas, Ávila y Salamanca',
            [x['capital'] for x in km_['capitales'][:4]] == ['Zamora', 'Soria', 'Cuenca', 'Badajoz'] and {x['capital'] for x in km_['capitales'][4:6]} == {'Ávila', 'Salamanca'}
            and kc['Ávila']['m23_dif'] == kc['Salamanca']['m23_dif'])
    control('Capitales: Zamora y Soria más de 14 puntos por debajo en las municipales', kc['Zamora']['m23_dif'] < -14 and kc['Soria']['m23_dif'] < -14)
    control('Capitales: ninguna a más de 10 puntos de su provincia en las generales', km_['n_menos_10_g23'] == 0)
    control('Capitales: las 50 votaron menos en mayo que en julio', km_['n_mun_menor_gen'] == 50)
    control('Capitales: cinco votaron más que su provincia (Barcelona, Cádiz, València, Murcia, Toledo)',
            sorted(x['capital'] for x in km_['capitales'] if x['m23_dif'] >= 0) == sorted(['Barcelona', 'Cádiz', 'València', 'Murcia', 'Toledo']))
    eu = C['europeas']
    dr, dl = eu['deciles_renta'], eu['deciles_renta_pocos_extranjeros']
    control('Europeas: la participación sube tramo a tramo con la renta en las dos elecciones',
            all(a['g2023'] < b['g2023'] and a['e2024'] < b['e2024'] for a, b in zip(dr, dr[1:])))
    control('Europeas: la brecha crece también en las secciones con pocos extranjeros', eu['brecha_e2024_pe'] > eu['brecha_g2023_pe'] + 5)
    control('Europeas: la caída es mayor en el tramo más pobre que en el más rico', dr[0]['e2024'] - dr[0]['g2023'] < dr[-1]['e2024'] - dr[-1]['g2023'])
    control('Europeas: al menos ocho de las diez mayores caídas en Andalucía', eu['andalucia_top10'] >= 8)
    control('Europeas: Arcos con menos del 5 % de extranjeros', any(r['municipio'] == 'Arcos de la Frontera' and r['extranjeros'] < 5 for r in eu['mayores_caidas']))

    # 3. Cada pieza tiene los campos que exige el estándar
    for p in P:
        falta = [k for k in ('titulo', 'pregunta', 'resumen', 'cuerpo', 'no_sabemos', 'tabla', 'compara', 'limites', 'csv', 'fuentes')
                 if not p.get(k)]
        control(f'{p["slug"]}: campos completos', not falta, falta)
        control(f'{p["slug"]}: serie existe', p['serie'] in SERIES)
        control(f'{p["slug"]}: CSV existe', (ATLAS / 'datos' / p['csv']).exists(), p['csv'])
        causales = [t for tipo, t in p['cuerpo'] if tipo != 'sub' and CAUSALES.search(t)] + [t for t in [titular(p), p['titulo'], p['resumen']] if CAUSALES.search(t)]
        control(f'{p["slug"]}: titular corto (60 caracteres como máximo)', p['slug'] in TITULARES and len(titular(p)) <= 60, titular(p))
        control(f'{p["slug"]}: sin lenguaje causal en titular, resumen, datos y patrones', not causales, causales)
        if p['serie'] != 'bisagras' and p['lugares']:
            from paginas import enlaces_mapa
            sin = set(p['lugares']) - {l for l, _ in enlaces_mapa(p)}
            control(f'{p["slug"]}: cada lugar enlaza a un solo municipio del mapa de resultados', not sin, sin)
        if p.get('revisado') is None:
            pagina = (ATLAS / p['serie'] / p['slug'] / 'index.html')
            if pagina.exists():
                control(f'{p["slug"]}: sin revisar → noindex', 'noindex' in pagina.read_text())

    # 4. CSV sin huecos
    for f in sorted((ATLAS / 'datos').glob('*.csv')):
        filas = list(csv.DictReader(open(f)))
        vacios = sum(1 for r in filas for v in r.values() if v in ('', 'nan', 'NaN', 'None'))
        control(f'{f.name}: {len(filas)} filas sin valores vacíos', filas and vacios == 0, f'{vacios} vacíos')

    # 5. Cada cifra decimal del texto está en cifras.json (o es resta/valor absoluto de una de ellas)
    nums = planos(C, set())
    validas = {num(abs(x)) for x in nums if isinstance(x, float)} | {num(abs(x) * 100, 0) for x in nums if isinstance(x, float) and abs(x) < 1}
    validas |= {num(x, 0) for x in nums}
    validas |= {num(round(x, 1)) for x in nums}
    # Cifras derivadas que el texto cita: se recalculan aquí y se aceptan como válidas.
    sur_psoe = [f for f in C['madrid_sur']['municipios'] if f['gana'] == 'PSOE' and f['grupo'] == 'sur']
    derivadas = {'suma de habitantes de las ciudades del sur que gana el PSOE': sum(f['poblacion'] for f in sur_psoe),
                 'ventaja del PP sobre el PSOE en el voto CERA de Madrid': m['cera_pp'] - m['cera_psoe']}
    for k, v in derivadas.items():
        control(f'Cifra derivada: {k} = {num(v, 0)}', v > 0)
        validas.add(num(v, 0))
    validas |= {'1.000', '1.500', '2.000', '5.000', '9.000', '10.000', '15.000', '20.000', '50.000', '60.000', '100.000'}   # umbrales de población y de margen, no datos
    # Diferencias entre dos cifras de cifras.json (p. ej. «la izquierda perdió 17,2 puntos»): se aceptan si cuadran a un decimal.
    flo = sorted({round(x, 1) for x in nums if isinstance(x, float) and abs(x) <= 100})
    validas |= {num(abs(a - b)) for i, a in enumerate(flo) for b in flo[i + 1:]}
    validas |= {num(abs(a - b) - 0.1) for i, a in enumerate(flo) for b in flo[i + 1:]} | {num(abs(a - b) + 0.1) for i, a in enumerate(flo) for b in flo[i + 1:]}
    sueltas = []
    for p in P:
        tabla = {c for fila in p['tabla']['filas'] for c in fila}
        textos = [titular(p), p['titulo'], p['resumen']] + [t for _, t in p['cuerpo']] + [r for _, r in (p['faq'] or [])]
        for t in textos:
            for n in re.findall(r'\d{1,3}(?:\.\d{3})+|\d+,\d', t):
                if n not in validas and n not in tabla and not any(n in str(c) for c in tabla):
                    sueltas.append((p['slug'], n))
    control('Todas las cifras decimales y de miles del texto salen de cifras.json o de la tabla', not sueltas, sueltas)

    ok = sum(r[0] for r in resultados)
    lineas = [f'Controles del Atlas: {ok} de {len(resultados)} superados', '']
    lineas += [f'{"OK " if r[0] else "FALLA"}  {r[1]}' + ('' if r[0] else f'  →  {r[2]}') for r in resultados]
    (SRC / 'controles.txt').write_text('\n'.join(lineas) + '\n')
    print('\n'.join(l for l in lineas if not l.startswith('OK')))
    sys.exit(0 if ok == len(resultados) else 1)


if __name__ == '__main__':
    main()
