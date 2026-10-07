"""Expediente interno del Atlas: fuentes, fórmulas, resultado de los controles y la muestra para la comprobación
manual. No se publica. Se escribe en ATLAS_EXPEDIENTE (por defecto /mnt/project-files/atlas/expedientes)."""
import csv
import json
import os
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))
from graficos import num, ANYO  # noqa: E402
from piezas import piezas  # noqa: E402
from piezas2 import piezas2  # noqa: E402
from paginas import FUENTES  # noqa: E402
from lugares import COLOR  # noqa: E402

OUT = Path(os.environ.get('ATLAS_EXPEDIENTE', '/mnt/project-files/atlas/expedientes'))
INFO = 'https://infoelectoral.interior.gob.es/es/elecciones-celebradas/resultados-electorales/'
DESCARGA = {'interior': '2026-10-06 (municipales); pollspaindata commit ee5ecda', 'pollspain': 'commit ee5ecda',
            'ine_adrh': '2026-10-06 (ineAtlas.data)', 'ine_censo': '2026-10-06', 'transparencia': '2026-10-06',
            'decreto29n': 'pendiente: BOE no accesible desde el entorno, enlace por añadir'}
FORMULAS = {
    'cadiz-madrid-29n': "D'Hondt sobre los votos del 23J (con CERA) con 8 escaños en Cádiz y 38 en Madrid; barrera del 3 % sobre voto válido (candidaturas + blanco).",
    'madrid-voto-exterior': "D'Hondt en Madrid con y sin voto CERA; «votos que faltaban» = mínimo de votos adicionales para superar el último cociente.",
    'escanos-ajustados-2023': "Para cada provincia, votos adicionales mínimos que necesitaba la candidatura con el mejor cociente siguiente para quitar el último escaño.",
    'capitales-frente-a-su-provincia': "% PP capital − % PP resto de la provincia (Σ votos / Σ voto válido de los demás municipios).",
    'sur-de-madrid': "% sobre voto válido por municipio; izquierda = PSOE + familia Sumar/Podemos/IU; derecha = PP + Vox + Cs.",
    'a-illa-vilanova-de-arousa': "% PP sobre voto válido en cada elección; brecha = Vilanova − A Illa.",
    'cabra-montilla': "Distancia euclídea entre seis indicadores estandarizados; % sobre voto válido.",
    'puerto-real': "MCO ponderado por √censo con efectos fijos de provincia; residuo = real − previsto (PP + Vox + Cs).",
    'badalona': "% sobre voto válido en municipales y generales; diferencia PP municipales − generales en municipios ≥ 20.000 hab.",
    'cuencas-mineras-asturianas': "Modelo municipal (MCO ponderado por √censo con efectos fijos de provincia); izquierda = PSOE + familia Sumar/Podemos/IU; lista ganadora de mayo desde los ficheros por mesa de Interior.",
    'lalin-vilanova-de-arousa': "Modelo municipal; ranking de residuos al alza entre los municipios ≥ 10.000 hab.",
    'cuenca-de-pamplona': "Modelo municipal; PP incluye UPN; distancia entre centroides de los términos (fórmula equirrectangular).",
    'getxo-portugalete': "% sobre voto válido; agregados de Bizkaia = Σ votos / Σ voto válido; distancia entre centroides.",
    'aranda-miranda': "% sobre voto válido en las ocho generales; modelo municipal; mayores municipios de Burgos por población del INE.",
    'los-palacios-y-villafranca': "% sobre voto válido; lista ganadora de mayo = máximo de votos por candidatura / voto válido (candidaturas + blanco).",
    'castro-urdiales': "Modelo municipal; derecha Cantabria = Σ votos PP + Vox + Cs / Σ voto válido.",
    'vigo': "% sobre voto válido; ciudades gallegas ≥ 60.000 hab. y municipios ≥ 20.000 hab. según el padrón del INE.",
    'pueblos-pequenos': "Participación por tramo = Σ votantes / Σ censo; «más en municipales» = participación de mayo > participación de julio en cada municipio.",
    'paro-renta-participacion': "Participación por sección censal; MCO con log renta, paro, estudios, edad y extranjeros; correlación ecológica.",
}


def muestra(C):
    """Valores con nombre propio que Nacho comprueba a mano en la web oficial."""
    f = []
    add = lambda pieza, lugar, eleccion, indicador, valor, donde=INFO: f.append(
        dict(pieza=pieza, lugar=lugar, eleccion=eleccion, indicador=indicador, valor_atlas=valor, donde_comprobar=donde,
             valor_oficial='', coincide=''))
    pr = C['puerto_real']
    add('puerto-real', 'Puerto Real', 'Congreso 23J 2023', '% PSOE sobre voto válido', num(pr['psoe']))
    add('puerto-real', 'Puerto Real', 'Congreso 23J 2023', '% PP sobre voto válido', num(pr['pp']))
    add('puerto-real', 'Puerto Real', 'Municipales 2023', f'% {pr["m2023_lista"]}', num(pr['m2023_lista_pct']))
    add('puerto-real', 'Puerto Real', 'INE ADRH', 'Renta media por unidad de consumo (€)', num(pr['renta'], 0), FUENTES['ine_adrh'][1])
    m = C['madrid']
    add('madrid-voto-exterior', 'Madrid (provincia)', 'Congreso 23J 2023', 'Votos PP', num(m['votos_pp'], 0))
    add('madrid-voto-exterior', 'Madrid (provincia)', 'Congreso 23J 2023', 'Votos CERA PP', num(m['cera_pp'], 0))
    add('madrid-voto-exterior', 'Madrid (provincia)', 'Congreso 23J 2023', 'Escaños PP / PSOE', f'{m["con_cera"]["PP"]} / {m["con_cera"]["PSOE"]}')
    g = C['margenes'][0]
    add('escanos-ajustados-2023', g['provincia'], 'Congreso 23J 2023', f'Último escaño ({g["ultimo_escano"]}); votos que faltaban a {g["aspirante"]}',
        num(g['votos_que_faltaban'], 0))
    cp = {x['capital']: x for x in C['capitales']}
    for c in ('Granada', 'Ourense'):
        add('capitales-frente-a-su-provincia', c, 'Congreso 23J 2023', '% PP capital / % PP resto de la provincia',
            f'{num(cp[c]["pp_capital"])} / {num(cp[c]["pp_resto"])}')
    ms = {x['municipio']: x for x in C['madrid_sur']['municipios']}
    for c in ('Parla', 'Móstoles'):
        add('sur-de-madrid', c, 'Congreso 23J 2023', '% PP / % PSOE', f'{num(ms[c]["pp"])} / {num(ms[c]["psoe"])}')
    a = C['arousa']
    add('a-illa-vilanova-de-arousa', 'A Illa de Arousa', 'Congreso 23J 2023', '% PP', num(a['illa']['pp']['2023_07']))
    add('a-illa-vilanova-de-arousa', 'Vilanova de Arousa', 'Congreso 23J 2023', '% PP', num(a['vilanova']['pp']['2023_07']))
    add('a-illa-vilanova-de-arousa', 'A Illa de Arousa', 'Congreso 2004', '% PP', num(a['illa']['pp']['2004_03']))
    cm = C['cabra_montilla']
    for k, n in (('cabra', 'Cabra'), ('montilla', 'Montilla')):
        add('cabra-montilla', n, 'Congreso 23J 2023', '% PP + Vox + Cs', num(cm[k]['der']['2023_07']))
    b = C['badalona']
    add('badalona', 'Badalona', 'Municipales 2023', '% PP', num(b['M2023']['PP']))
    add('badalona', 'Badalona', 'Congreso 23J 2023', '% PP', num(b['2023_07']['PP']))
    cu = {x['municipio']: x for x in C['cuencas']['municipios']}
    add('cuencas-mineras-asturianas', 'Mieres', 'Congreso 23J 2023', '% PSOE', num(cu['Mieres']['psoe']['2023_07']))
    add('cuencas-mineras-asturianas', 'Mieres', 'Municipales 2023', f'% {cu["Mieres"]["m2023_lista"]}', num(cu['Mieres']['m2023_lista_pct']))
    li = C['lalin']['lalin']
    add('lalin-vilanova-de-arousa', 'Lalín', 'Congreso 23J 2023', '% PP', num(li['pp']['2023_07']))
    pm = {x['municipio']: x for x in C['pamplona']['municipios']}
    add('cuenca-de-pamplona', 'Cizur', 'Congreso 23J 2023', '% PP (UPN en la lista del PP)', num(pm['Cizur']['pp']['2023_07']))
    add('cuenca-de-pamplona', 'Villava/Atarrabia', 'Congreso 23J 2023', '% EH Bildu', num(pm['Villava/Atarrabia']['bildu_2023']))
    gm = {x['municipio']: x for x in C['getxo']['municipios']}
    add('getxo-portugalete', 'Portugalete', 'Congreso 23J 2023', '% PSOE', num(gm['Portugalete']['psoe']['2023_07']))
    add('getxo-portugalete', 'Getxo', 'Congreso 23J 2023', '% PP', num(gm['Getxo']['pp']['2023_07']))
    am = C['aranda_miranda']
    add('aranda-miranda', 'Miranda de Ebro', 'Congreso 23J 2023', '% PSOE', num(am['miranda']['psoe']['2023_07']))
    add('aranda-miranda', 'Aranda de Duero', 'Municipales 2023', '% PP / % PSOE', f"{num(am['aranda']['m2023']['pp'])} / {num(am['aranda']['m2023']['psoe'])}")
    lp = C['los_palacios']['lp']
    add('los-palacios-y-villafranca', 'Los Palacios y Villafranca', 'Congreso 2004', '% PSOE', num(lp['psoe']['2004_03']))
    add('los-palacios-y-villafranca', 'Los Palacios y Villafranca', 'Municipales 2023', f'% {lp["m2023_lista"]}', num(lp['m2023_lista_pct']))
    cs = C['castro']['castro']
    add('castro-urdiales', 'Castro-Urdiales', 'Congreso 23J 2023', '% PSOE / % PP', f"{num(cs['psoe']['2023_07'])} / {num(cs['pp']['2023_07'])}")
    v = C['vigo']['vigo']
    add('vigo', 'Vigo', 'Municipales 2023', '% PSOE', num(v['m2023']['psoe']))
    add('vigo', 'Vigo', 'Congreso 23J 2023', '% PSOE', num(v['psoe']['2023_07']))
    return f


def main():
    C = json.load(open(SRC / 'cifras.json'))
    OUT.mkdir(parents=True, exist_ok=True)
    filas = muestra(C)
    with open(OUT / 'muestra_manual.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    controles = (SRC / 'controles.txt').read_text() if (SRC / 'controles.txt').exists() else 'controles.py no ejecutado'
    L = ['# Expediente del Atlas de las anomalías electorales', '',
         'Documento interno. No se publica. Generado por `atlas/src/expediente.py`.', '',
         '## Flujo', '', 'datos (`construir.py`) → validación automática (`controles.py`) → comprobación humana (`muestra_manual.csv`) '
         '→ redacción (`piezas.py`) → revisión de datos y texto (Nacho) → publicación (campo `revisado` con fecha).', '',
         'Una pieza sin `revisado` sale con «Revisión pendiente», `noindex` y fuera del sitemap y de llms.txt.', '',
         '## Fuentes', '']
    for k, (t, u) in FUENTES.items():
        L.append(f'- **{k}**: {t}. URL: {u or "sin enlace"}. Descarga: {DESCARGA.get(k, "")}')
    L += ['', '## Piezas', '']
    for p in piezas(C) + piezas2(C):
        L += [f'### {p["titulo"]}', '', f'- Ruta: /atlas/{p["serie"]}/{p["slug"]}/', f'- Estado: {p["estado"]}; revisado: {p["revisado"] or "pendiente"}',
              f'- Fórmula: {FORMULAS.get(p["slug"], "")}', f'- CSV: atlas/datos/{p["csv"]}', f'- Fuentes: {", ".join(p["fuentes"])}',
              f'- Hipótesis sin dos fuentes: {len(p["no_sabemos"])}',
              f'- Foto: {p["foto"]["url"]} ({p["foto"]["autor"]}, {p["foto"]["licencia"]})' if p.get('foto') else '- Foto: ninguna', '- Coherencia titular / texto / tabla / gráfico: las cifras salen de cifras.json (control 5 en controles.txt); revisión humana pendiente.', '']
    L += ['## Notas de color («Sobre el terreno»)', '', 'Cada nota, con sus dos fuentes, el extracto literal que la respalda y la fecha de consulta.', '']
    for slug, notas in COLOR.items():
        L.append(f'### {slug}')
        for n in notas:
            L += ['', f'- {n["texto"]}'] + [f'  - {s["url"]} (consultado {s["consultado"]}): «{s["extracto"]}»' for s in n['fuentes']]
        L.append('')
    L += ['## Pendientes conocidos', '',
          '- Enlace al Real Decreto del 29N (BOE no accesible desde el entorno de trabajo).',
          '- Las explicaciones locales siguen como hipótesis hasta tener dos fuentes independientes.', '',
          '## Resultado de los controles automáticos', '', '```', controles.strip(), '```', '']
    (OUT / 'expediente.md').write_text('\n'.join(L))
    print(f'{OUT}/expediente.md y muestra_manual.csv ({len(filas)} valores)')


if __name__ == '__main__':
    main()
