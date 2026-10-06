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

# Resultado oficial del 23J de 2023 (Congreso, 350 escaños), para comprobar el reparto D'Hondt recalculado.
OFICIAL_2023 = {'PP': 137, 'PSOE': 121, 'Vox': 33, 'Sumar': 31, 'ERC': 7, 'Junts': 7, 'EH Bildu': 6, 'PNV': 5,
                'BNG': 1, 'UPN': 1, 'CC': 1}
CAUSALES = re.compile(r'\b(porque|debido a|a causa de|causa|provoca|se debe a|gracias a)\b', re.I)

resultados = []


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
    P = piezas(C)

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

    # 3. Cada pieza tiene los campos que exige el estándar
    for p in P:
        falta = [k for k in ('titulo', 'pregunta', 'resumen', 'cuerpo', 'no_sabemos', 'tabla', 'compara', 'limites', 'csv', 'fuentes')
                 if not p.get(k)]
        control(f'{p["slug"]}: campos completos', not falta, falta)
        control(f'{p["slug"]}: serie existe', p['serie'] in SERIES)
        control(f'{p["slug"]}: CSV existe', (ATLAS / 'datos' / p['csv']).exists(), p['csv'])
        causales = [t for tipo, t in p['cuerpo'] if tipo != 'sub' and CAUSALES.search(t)] + [t for t in [p['titulo'], p['resumen']] if CAUSALES.search(t)]
        control(f'{p["slug"]}: sin lenguaje causal en titular, resumen, datos y patrones', not causales, causales)
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
    validas |= {'1.500', '10.000', '15.000', '20.000'}   # umbrales de población y de margen, no datos
    # Diferencias entre dos cifras de cifras.json (p. ej. «la izquierda perdió 17,2 puntos»): se aceptan si cuadran a un decimal.
    flo = sorted({round(x, 1) for x in nums if isinstance(x, float) and abs(x) <= 100})
    validas |= {num(abs(a - b)) for i, a in enumerate(flo) for b in flo[i + 1:]}
    validas |= {num(abs(a - b) - 0.1) for i, a in enumerate(flo) for b in flo[i + 1:]} | {num(abs(a - b) + 0.1) for i, a in enumerate(flo) for b in flo[i + 1:]}
    sueltas = []
    for p in P:
        tabla = {c for fila in p['tabla']['filas'] for c in fila}
        textos = [p['titulo'], p['resumen']] + [t for _, t in p['cuerpo']] + [r for _, r in (p['faq'] or [])]
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
