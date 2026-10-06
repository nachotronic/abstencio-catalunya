"""Textos de las piezas del Atlas. Cada cifra sale de cifras.json (C); ninguna está escrita a mano.

Cada afirmación se marca en el cuerpo con su tipo:
  dato        resultado verificable (fórmula sobre una fuente)
  patrón      relación descriptiva, sin causa
  hipótesis   explicación posible que todavía no tiene dos fuentes independientes
La sección «Lo que no sabemos» recoge las hipótesis; nunca se presentan como causa.

`revisado` es la fecha (AAAA-MM-DD) en que Nacho comprueba la muestra manual y firma la revisión de datos y texto.
Mientras esté vacío, la página se genera con «Revisión pendiente», con noindex y fuera del sitemap.
"""
from graficos import num, lineas, barras_previsto, divergente, barras_agrupadas, margenes, ANYO

SERIES = {
    'excepciones': ('Las excepciones', 'Lugares que votan muy distinto de lo que predicen su renta, su edad, su paro y su tamaño.'),
    'fronteras': ('Fronteras que votan distinto', 'Municipios vecinos, separados por pocos kilómetros y muchos puntos de voto.'),
    'gemelos': ('Gemelos electorales', 'Municipios casi idénticos en sus datos que votan de forma opuesta.'),
    'contra-su-provincia': ('Contra su provincia', 'Lugares donde gana quien pierde en su provincia, y al revés.'),
    'ciudad-y-entorno': ('Ciudad, corona e interior', 'La distancia entre la ciudad y el territorio que la rodea.'),
    'voto-doble': ('Voto doble', 'El mismo electorado vota distinto según qué se elige.'),
    'bisagras': ('Bisagras', 'Votos y lugares que deciden algo mucho mayor que su peso.'),
    'quien-no-vota': ('Quién no vota', 'Quién se queda fuera de las urnas, y por qué grupos de razones.'),
}

CONG = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
P = lambda x: num(x) + ' %'          # 43.2 -> '43,2 %'
PP_ = lambda x: num(abs(x)) + ' puntos'


def piezas(C):
    out = []

    # ------------------------------------------------------------------ bisagras: Cádiz y Madrid el 29N
    z = C['escanos_29n']
    out.append(dict(
        slug='cadiz-madrid-29n', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='Con los votos de 2023, el escaño que pierde Cádiz sería del PP y el que gana Madrid, del PSOE',
        pregunta='¿Qué habría cambiado en 2023 con el reparto de escaños que se aplica el 29 de noviembre de 2026?',
        resumen=(f'Para las generales del 29 de noviembre de 2026, Madrid elige 38 diputados (uno más) y Cádiz 8 (uno menos). '
                 f'Si se aplica ese reparto a los votos del 23 de julio de 2023, el PP pierde un escaño en Cádiz '
                 f'(de {z["11"]["2023"]["PP"]} a {z["11"]["2026"]["PP"]}) y el PSOE gana uno en Madrid '
                 f'(de {z["28"]["2023"]["PSOE"]} a {z["28"]["2026"]["PSOE"]}). '
                 f'Es un ejercicio aritmético, no una previsión: los votos de 2026 serán otros.'),
        estado='Dato',
        cuerpo=[
            ('dato', 'El cambio de escaños entre provincias lo fija el decreto de convocatoria según la población de cada una. '
                     'Para el 29N, Madrid pasa de 37 a 38 diputados y Cádiz de 9 a 8; el resto de provincias no cambia.'),
            ('dato', f'Con los votos de 2023 (incluido el voto de los residentes en el extranjero, CERA), Cádiz repartió sus 9 escaños así: '
                     f'PP {z["11"]["2023"]["PP"]}, PSOE {z["11"]["2023"]["PSOE"]}, Vox {z["11"]["2023"]["Vox"]} y Sumar {z["11"]["2023"]["Sumar"]}. '
                     f'Con 8 escaños, el que desaparece es el último que obtuvo el PP.'),
            ('dato', f'En Madrid, con 37 escaños: PP {z["28"]["2023"]["PP"]}, PSOE {z["28"]["2023"]["PSOE"]}, Sumar {z["28"]["2023"]["Sumar"]} y Vox {z["28"]["2023"]["Vox"]}. '
                     f'Con 38, el escaño nuevo es para el PSOE.'),
            ('dato', 'El saldo, con los votos de 2023, sería de un diputado menos para el PP y uno más para el PSOE. '
                     f'En 2023 el PSOE se quedó a {num(C["madrid"]["faltaban_psoe_con_cera"], 0)} votos del último escaño de Madrid, así que cualquier cambio de voto en 2026 puede alterar este resultado.'),
        ],
        no_sabemos=['Cómo votarán Cádiz y Madrid el 29N. Esta pieza solo aplica el nuevo reparto a votos pasados.'],
        tabla=dict(caption='Escaños con los votos del 23J de 2023: reparto real y reparto con los escaños de 2026',
                   cabecera=['Provincia', 'Partido', 'Escaños 2023', 'Con el reparto de 2026'],
                   filas=[[p, f, z[c]['2023'].get(f, 0), z[c]['2026'].get(f, 0)] for c, p in (('11', 'Cádiz'), ('28', 'Madrid'))
                          for f in ('PP', 'PSOE', 'Vox', 'Sumar')]),
        grafico=None,
        compara='Los votos del 23 de julio de 2023 por provincia, repartidos con la ley D\'Hondt y la barrera del 3 % con 37 y 38 escaños en Madrid y con 9 y 8 en Cádiz.',
        limites='Usa los votos de 2023, incluido el CERA. El reparto recalculado con estos datos reproduce los 350 escaños oficiales de 2023. No anticipa el resultado de 2026.',
        csv='cadiz-madrid-29n.csv', fuentes=['interior', 'decreto29n'], lugares=['Cádiz', 'Madrid'],
        faq=[('¿Por qué Madrid gana un escaño y Cádiz lo pierde?', 'El número de diputados de cada provincia se recalcula en cada convocatoria según su población; el decreto del 29N asigna 38 a Madrid y 8 a Cádiz.')],
    ))

    # ------------------------------------------------------------------ bisagras: Madrid y el voto exterior
    md = C['madrid']
    out.append(dict(
        slug='madrid-voto-exterior', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='El último escaño de Madrid en 2023 lo decidió el voto desde el extranjero',
        pregunta='¿Cuántos votos separaron el último escaño de Madrid el 23J?',
        resumen=(f'Con los votos emitidos en España, el último escaño de Madrid era del PSOE: al PP le faltaban {num(md["faltaban_pp_sin_cera"], 0)} votos. '
                 f'El voto de los residentes en el extranjero (CERA) dio al PP {num(md["cera_pp"], 0)} votos y al PSOE {num(md["cera_psoe"], 0)}, '
                 f'y el escaño pasó al PP: {md["con_cera"]["PP"]} para el PP y {md["con_cera"]["PSOE"]} para el PSOE. '
                 f'Con todos los votos contados, al PSOE le faltaron {num(md["faltaban_psoe_con_cera"], 0)}.'),
        estado='Dato',
        cuerpo=[
            ('dato', f'Sin el voto exterior, Madrid repartía sus 37 escaños así: PP {md["sin_cera"]["PP"]}, PSOE {md["sin_cera"]["PSOE"]}, Sumar {md["sin_cera"]["Sumar"]} y Vox {md["sin_cera"]["Vox"]}.'),
            ('dato', f'El voto CERA de Madrid sumó {num(md["cera_total_candidaturas"], 0)} votos a candidaturas. El PP recibió {num(md["cera_pp"], 0)} y el PSOE {num(md["cera_psoe"], 0)}: '
                     f'una diferencia de {num(md["cera_pp"] - md["cera_psoe"], 0)} votos, suficiente para mover el último cociente.'),
            ('dato', f'Con el voto exterior, el reparto final fue PP {md["con_cera"]["PP"]}, PSOE {md["con_cera"]["PSOE"]}, Sumar {md["con_cera"]["Sumar"]} y Vox {md["con_cera"]["Vox"]}. '
                     f'En el total de España, eso dejó al PP con {C["escanos_2023_con_cera"]["PP"]} diputados y al PSOE con {C["escanos_2023_con_cera"]["PSOE"]}.'),
            ('dato', f'Para recuperar ese escaño, al PSOE le habrían bastado {num(md["faltaban_psoe_con_cera"], 0)} votos más en una provincia en la que el PP sumó {num(md["votos_pp"], 0)} votos.'),
        ],
        no_sabemos=['Por qué el voto exterior madrileño fue más favorable al PP que el voto emitido en España. Requiere datos del perfil de los residentes en el extranjero que esta pieza no tiene.'],
        tabla=dict(caption='Escaños de Madrid el 23J de 2023, sin y con el voto de los residentes en el extranjero (CERA)',
                   cabecera=['Partido', 'Sin CERA', 'Con CERA', 'Votos CERA'],
                   filas=[['PP', md['sin_cera']['PP'], md['con_cera']['PP'], num(md['cera_pp'], 0)],
                          ['PSOE', md['sin_cera']['PSOE'], md['con_cera']['PSOE'], num(md['cera_psoe'], 0)],
                          ['Sumar', md['sin_cera']['Sumar'], md['con_cera']['Sumar'], '—'],
                          ['Vox', md['sin_cera']['Vox'], md['con_cera']['Vox'], '—']]),
        grafico=None,
        compara='El reparto D\'Hondt de los 37 escaños de Madrid con y sin los votos emitidos desde el extranjero.',
        limites='Datos del escrutinio por mesa de Interior. «Votos que faltaban» es el mínimo de votos adicionales con el que una lista habría superado el último cociente, sin restar votos a nadie.',
        csv='escanos-ajustados-2023.csv', fuentes=['interior'], lugares=['Madrid'],
        faq=[('¿Qué es el voto CERA?', 'El de los españoles inscritos en el Censo Electoral de Residentes Ausentes, es decir, que viven en el extranjero. Se cuenta días después de la jornada electoral.')],
    ))

    # ------------------------------------------------------------------ bisagras: escaños ajustados
    mg = C['margenes']
    out.append(dict(
        slug='escanos-ajustados-2023', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'{C["margenes_menos_1500"]} escaños del 23J se decidieron por menos de 1.500 votos; en Girona, por {num(mg[0]["votos_que_faltaban"], 0)}',
        pregunta='¿En qué provincias el último escaño estuvo a punto de cambiar de manos?',
        resumen=(f'En {C["margenes_menos_1500"]} de las 52 circunscripciones, a la lista que se quedó sin el último escaño le faltaron menos de 1.500 votos para lograrlo. '
                 f'Los dos casos más ajustados fueron Girona, donde al PP le faltaron {num(mg[0]["votos_que_faltaban"], 0)} votos para quitar el escaño a Junts, '
                 f'y Cantabria, donde le faltaron {num(mg[1]["votos_que_faltaban"], 0)} para quitárselo a Vox.'),
        estado='Dato',
        cuerpo=[
            ('dato', 'Cada provincia reparte sus escaños por la ley D\'Hondt. El último escaño va a la lista con el mayor cociente restante, y la siguiente lista se queda a una distancia que se puede medir en votos.'),
            ('dato', f'Girona: el sexto escaño fue para Junts. Al PP le faltaron {num(mg[0]["votos_que_faltaban"], 0)} votos.'),
            ('dato', f'Cantabria: el quinto escaño fue para Vox. Al PP le faltaron {num(mg[1]["votos_que_faltaban"], 0)} votos.'),
            ('dato', f'{mg[2]["provincia"]}, {mg[3]["provincia"]}, {mg[4]["provincia"]} y {mg[5]["provincia"]} tuvieron márgenes de entre '
                     f'{num(mg[2]["votos_que_faltaban"], 0)} y {num(mg[5]["votos_que_faltaban"], 0)} votos.'),
        ],
        no_sabemos=['Si estos márgenes se repetirán el 29N. Un margen pequeño en 2023 no significa que la provincia vaya a ser decisiva en 2026.'],
        tabla=dict(caption='Las diez circunscripciones con el último escaño más ajustado el 23J de 2023 (con voto CERA)',
                   cabecera=['Provincia', 'Escaños', 'Último escaño', 'Aspirante', 'Votos que le faltaban'],
                   filas=[[f['provincia'], f['escanos'], f['ultimo_escano'], f['aspirante'], num(f['votos_que_faltaban'], 0)] for f in mg]),
        grafico=(margenes(mg, 'Votos que le faltaron a la lista aspirante para el último escaño'), 'Votos que le faltaron a la lista aspirante para ganar el último escaño, 23J de 2023.'),
        compara='Las 52 circunscripciones del Congreso en 2023: el último escaño asignado y la lista que más cerca estuvo de lograrlo.',
        limites='Calculado con los votos por mesa de Interior, incluido el CERA; el reparto completo reproduce los 350 escaños oficiales. Los votos que faltaban suponen que la lista suma votos sin que nadie los pierda.',
        csv='escanos-ajustados-2023.csv', fuentes=['interior'], lugares=[f['provincia'] for f in mg[:4]],
        faq=None,
    ))

    # ------------------------------------------------------------------ ciudad y entorno: capitales
    cp = C['capitales']
    menos = [f for f in cp if f['dif_pp'] < 0]
    mas = [f for f in cp if f['dif_pp'] > 0]
    out.append(dict(
        slug='capitales-frente-a-su-provincia', serie='ciudad-y-entorno', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'En {C["capitales_resumen"]["mas_pp"]} de las 50 provincias, la capital vota más al PP que el resto de su provincia',
        pregunta='¿Votan las capitales de provincia más a la izquierda que su entorno?',
        resumen=(f'No en la mayoría de España. El 23J, la capital dio al PP un porcentaje mayor que el resto de su provincia en {C["capitales_resumen"]["mas_pp"]} de 50 casos, '
                 f'con Granada (+{num(cp[-1]["dif_pp"])} puntos), Donostia y Vitoria a la cabeza. '
                 f'La imagen de la ciudad progresista frente al campo conservador solo se cumple en {C["capitales_resumen"]["menos_pp"]} provincias, '
                 f'sobre todo en Galicia y Castilla y León: Ourense y Soria votaron {num(abs(cp[0]["dif_pp"]))} puntos menos al PP que su entorno.'),
        estado='Patrón',
        cuerpo=[
            ('dato', f'Diferencia entre el porcentaje del PP en la capital y en el resto de municipios de la provincia (23J, sobre voto válido). '
                     f'Capitales que votan menos al PP que su entorno: {", ".join(f["capital"] for f in menos)}.'),
            ('dato', f'Varias capitales andaluzas y extremeñas votan bastante más al PP que su provincia: Granada +{num(next(f["dif_pp"] for f in cp if f["capital"] == "Granada"))}, '
                     f'Badajoz +{num(next(f["dif_pp"] for f in cp if f["capital"] == "Badajoz"))}, Sevilla +{num(next(f["dif_pp"] for f in cp if f["capital"] == "Sevilla"))}, '
                     f'Córdoba +{num(next(f["dif_pp"] for f in cp if f["capital"] == "Córdoba"))} puntos.'),
            ('patrón', 'En Euskadi y Cataluña la capital también da más voto al PP que su entorno, pero por otro motivo visible en los datos: allí el PP es pequeño en todas partes y el voto rural va sobre todo a partidos nacionalistas. Es un patrón distinto del andaluz y conviene no mezclarlos.'),
            ('patrón', 'Donde la capital vota menos al PP, suele votar más al PSOE que su provincia (Ourense, Soria, Lugo, Palencia). Donde vota más al PP, el PSOE suele estar por debajo de su provincia (Granada, Badajoz, Córdoba).'),
        ],
        no_sabemos=['Por qué el voto rural del sur es más socialista que el urbano. Hay explicaciones en la literatura de geografía electoral (el peso histórico del PSOE en el campo andaluz y extremeño, el empleo público en las capitales), pero esta pieza no las ha contrastado con dos fuentes y las deja como hipótesis.'],
        tabla=dict(caption='Voto al PP y al PSOE en cada capital de provincia y en el resto de su provincia, 23J de 2023 (% del voto válido)',
                   cabecera=['Capital', 'Provincia', 'PP capital', 'PP resto', 'Diferencia PP', 'PSOE capital', 'PSOE resto'],
                   filas=[[f['capital'], f['provincia'], num(f['pp_capital']), num(f['pp_resto']), ('+' if f['dif_pp'] > 0 else '') + num(f['dif_pp']),
                           num(f['psoe_capital']), num(f['psoe_resto'])] for f in cp]),
        grafico=(divergente(cp, 'dif_pp', 'capital', 'Diferencia de voto al PP entre la capital y el resto de su provincia'),
                 'Puntos de voto al PP de la capital menos los del resto de su provincia, 23J de 2023.'),
        compara='Las 50 capitales de provincia (sin Ceuta y Melilla, que son una sola ciudad) frente a la suma del resto de municipios de su provincia.',
        limites='Compara capitales administrativas, no las ciudades más grandes (Vigo, Gijón o Jerez no son capitales). El resto de la provincia incluye áreas metropolitanas y pueblos rurales juntos.',
        csv='capitales-2023.csv', fuentes=['interior'], lugares=[f['capital'] for f in (cp[0], cp[1], cp[-1])],
        faq=None,
    ))

    # ------------------------------------------------------------------ contra su provincia: sur de Madrid
    ms = C['madrid_sur']
    mm = {r['municipio']: r for r in ms['municipios']}
    sur4 = ['Parla', 'Fuenlabrada', 'Leganés', 'Getafe']
    out.append(dict(
        slug='sur-de-madrid', serie='contra-su-provincia', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'El PSOE ganó en cuatro grandes ciudades del sur de Madrid mientras el PP ganaba la provincia por {num(ms["prov_pp"] - ms["prov_psoe"], 0)} puntos',
        pregunta='¿Dónde resiste el PSOE en la provincia donde más gana el PP, y por cuánto?',
        resumen=(f'El PP ganó la provincia de Madrid el 23J con el {P(ms["prov_pp"])} frente al {P(ms["prov_psoe"])} del PSOE. '
                 f'Pero el PSOE fue primero en Parla, Fuenlabrada, Leganés y Getafe, cuatro ciudades que suman {num(sum(mm[n]["poblacion"] for n in sur4), 0)} habitantes. '
                 f'La ventaja se estrecha: en 2004 la izquierda (PSOE más Sumar, Podemos o IU) sacó entre el {P(min(mm[n]["izq_2004"] for n in sur4))} y el {P(max(mm[n]["izq_2004"] for n in sur4))} en las cuatro; en 2023, entre el {P(min(mm[n]["izq_2023"] for n in sur4))} y el {P(max(mm[n]["izq_2023"] for n in sur4))}, '
                 f'y en Móstoles y Alcorcón ya ganó el PP.'),
        estado='Dato',
        cuerpo=[
            ('dato', '; '.join(f'{n}: PSOE {P(mm[n]["psoe"])}, PP {P(mm[n]["pp"])}' for n in sur4) + '.'),
            ('dato', f'En Móstoles (PP {P(mm["Móstoles"]["pp"])}, PSOE {P(mm["Móstoles"]["psoe"])}) y Alcorcón (PP {P(mm["Alcorcón"]["pp"])}, PSOE {P(mm["Alcorcón"]["psoe"])}) el PP ya fue primero.'),
            ('dato', f'La izquierda estatal bajó en Parla del {P(mm["Parla"]["izq_2004"])} en 2004 al {P(mm["Parla"]["izq_2023"])} en 2023, y en Fuenlabrada del {P(mm["Fuenlabrada"]["izq_2004"])} al {P(mm["Fuenlabrada"]["izq_2023"])}.'),
            ('dato', f'En el otro extremo de la provincia, Boadilla del Monte y Pozuelo de Alarcón dieron a PP, Vox y Cs juntos el {P(mm["Boadilla del Monte"]["der_2023"])} y el {P(mm["Pozuelo de Alarcón"]["der_2023"])}. Boadilla votó a la derecha {num(mm["Boadilla del Monte"]["der_2023"] - ms["boadilla_previsto"])} puntos más de lo que predice su perfil (renta, edad, estudios, paro, extranjeros y tamaño).'),
            ('patrón', f'La renta separa los dos grupos: entre {num(min(mm[n]["renta"] for n in sur4), 0)} y {num(max(mm[n]["renta"] for n in sur4), 0)} euros por unidad de consumo en las cuatro ciudades del sur donde gana el PSOE, y desde {num(min(r["renta"] for r in ms["municipios"] if r["grupo"] == "noroeste"), 0)} en los municipios del noroeste de la tabla.'),
        ],
        no_sabemos=['Si el estrechamiento en el sur se debe a cambios de voto de los mismos vecinos o a la llegada de población nueva a barrios recientes. Los datos agregados por municipio no lo distinguen; el análisis por sección censal es el paso siguiente.'],
        tabla=dict(caption='Voto al PP y al PSOE y bloque de izquierda estatal (PSOE + Sumar/Podemos/IU) en el sur y el noroeste de Madrid (% del voto válido)',
                   cabecera=['Municipio', 'Zona', 'PP 2023', 'PSOE 2023', 'Izquierda 2004', 'Izquierda 2023', 'Renta (€/u.c.)'],
                   filas=[[r['municipio'], r['grupo'], num(r['pp']), num(r['psoe']), num(r['izq_2004']), num(r['izq_2023']), num(r['renta'], 0)] for r in ms['municipios']]),
        grafico=(barras_agrupadas([(r['municipio'].replace(' del Monte', '').replace(' de Alarcón', '').replace(' de Madrid', '').replace('Villanueva de la Cañada', 'V. Cañada'),
                                    {'PP': r['pp'], 'PSOE': r['psoe']}) for r in ms['municipios']],
                                  [('PP', 'var(--pp)'), ('PSOE', 'var(--psoe)')], 'Voto al PP y al PSOE en el sur y el noroeste de Madrid, 23J de 2023', ymax=60),
                 'PP y PSOE en seis municipios del sur y cinco del noroeste de Madrid, 23J de 2023 (% del voto válido).'),
        compara='Seis grandes municipios del sur metropolitano y cinco del noroeste frente al total de la provincia de Madrid.',
        limites='La selección de municipios es editorial: los seis mayores del sur y cinco del noroeste de renta alta. «Izquierda» suma PSOE y el espacio Sumar/Podemos/IU (incluido Más Madrid).',
        csv='madrid-sur-noroeste.csv', fuentes=['interior', 'ine_adrh'], lugares=sur4 + ['Boadilla del Monte'],
        faq=None,
    ))

    # ------------------------------------------------------------------ fronteras: A Illa y Vilanova
    ar = C['arousa']
    il, vi, br = ar['illa'], ar['vilanova'], ar['brechas']
    out.append(dict(
        slug='a-illa-vilanova-de-arousa', serie='fronteras', fecha_datos='2004-2023', revisado='2026-10-06',
        titulo=f'A Illa de Arousa vota {num(br["2023_07"], 0)} puntos menos al PP que Vilanova, a seis kilómetros, y así desde hace veinte años',
        pregunta='¿Por qué dos municipios vecinos con la misma renta y la misma edad votan tan distinto?',
        resumen=(f'El 23J de 2023, el PP sacó el {P(il["pp"]["2023_07"])} en A Illa de Arousa y el {P(vi["pp"]["2023_07"])} en Vilanova de Arousa, '
                 f'el municipio vecino al otro lado del puente. Tienen casi la misma renta ({num(il["renta"], 0)} y {num(vi["renta"], 0)} euros por unidad de consumo) '
                 f'y una edad media parecida. La distancia no es nueva: en las ocho generales desde 2004 ha estado entre {num(min(br.values()), 0)} y {num(max(br.values()), 0)} puntos.'),
        estado='Dato',
        cuerpo=[
            ('dato', f'Voto al PP en A Illa y en Vilanova en cada elección general: ' + '; '.join(f'{ANYO[e]}: {num(il["pp"][e])} y {num(vi["pp"][e])}' for e in CONG) + '.'),
            ('dato', f'En A Illa el PSOE fue primero en 2023 ({P(il["psoe_2023"])}) y el BNG sacó el {P(il["bng_2023"])}, frente al {P(vi["bng_2023"])} en Vilanova.'),
            ('dato', f'En las municipales de mayo de 2023 la diferencia se repite: PP {P(il["pp_m2023"])} en A Illa y {P(vi["pp_m2023"])} en Vilanova; BNG {P(il["bng_m2023"])} y {P(vi["bng_m2023"])}.'),
            ('dato', f'Renta por unidad de consumo: {num(il["renta"], 0)} € en A Illa y {num(vi["renta"], 0)} € en Vilanova. Edad media: {num(il["edad"])} y {num(vi["edad"])} años. Paro (2021): {P(il["paro"])} y {P(vi["paro"])}.'),
            ('patrón', 'La brecha es estable: sube y baja con el voto general al PP, pero las dos curvas se mueven en paralelo desde 2004.'),
        ],
        no_sabemos=['Qué explica la diferencia. Hay hipótesis por comprobar: la historia de la separación entre los dos municipios, la economía del marisqueo y las cofradías en A Illa, o la implantación local del BNG. Ninguna está respaldada todavía por dos fuentes independientes.',
                    'La fecha y el proceso de la segregación municipal, que esta pieza no ha podido documentar con la fuente oficial.'],
        tabla=dict(caption='Voto al PP en A Illa de Arousa y Vilanova de Arousa en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'A Illa de Arousa', 'Vilanova de Arousa', 'Diferencia'],
                   filas=[[ANYO[e], num(il['pp'][e]), num(vi['pp'][e]), num(br[e])] for e in CONG]),
        grafico=(lineas([('Vilanova', vi['pp'], 'var(--pp)', True), ('A Illa', il['pp'], 'var(--accent)', True)], CONG,
                        'Voto al PP en A Illa y Vilanova de Arousa, 2004-2023', 0, 70),
                 'Voto al PP en las generales de 2004 a 2023 en A Illa de Arousa y Vilanova de Arousa (% del voto válido).'),
        compara='Dos municipios vecinos de la ría de Arousa (Pontevedra) en las ocho elecciones generales de 2004 a 2023 y en las municipales de 2023.',
        limites='Datos por municipio. A Illa tiene unos 4.900 habitantes: pequeños cambios en número de votos mueven su porcentaje más que el de Vilanova.',
        csv='a-illa-vilanova.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['A Illa de Arousa', 'Vilanova de Arousa'],
        faq=None,
    ))

    # ------------------------------------------------------------------ gemelos: Cabra y Montilla
    cb, mo = C['cabra_montilla']['cabra'], C['cabra_montilla']['montilla']
    out.append(dict(
        slug='cabra-montilla', serie='gemelos', fecha_datos='2004-2023', revisado='2026-10-06',
        titulo=f'En 2004 Cabra y Montilla votaban igual; en 2023 las separaban {num(cb["der"]["2023_07"] - mo["der"]["2023_07"], 0)} puntos de voto a la derecha',
        pregunta='¿Cuándo y cómo empezaron a votar distinto dos ciudades cordobesas con el mismo perfil?',
        resumen=(f'Cabra y Montilla, en el sur de Córdoba, tienen casi la misma renta ({num(cb["renta"], 0)} y {num(mo["renta"], 0)} euros), la misma edad media y el mismo paro. '
                 f'En 2004 el PP sacó en las dos casi lo mismo ({P(cb["der"]["2004_03"])} y {P(mo["der"]["2004_03"])}). '
                 f'Desde entonces se han ido separando: en 2023 la derecha sacó el {P(cb["der"]["2023_07"])} en Cabra, donde ganó el PP, y el {P(mo["der"]["2023_07"])} en Montilla, donde ganó el PSOE.'),
        estado='Dato',
        cuerpo=[
            ('dato', f'Perfil: renta {num(cb["renta"], 0)} € y {num(mo["renta"], 0)} €; edad media {num(cb["edad"])} y {num(mo["edad"])} años; paro {P(cb["paro"])} y {P(mo["paro"])}; '
                     f'extranjeros {P(cb["extranjeros"])} y {P(mo["extranjeros"])}; estudios superiores {P(cb["estudios"])} y {P(mo["estudios"])}.'),
            ('dato', f'PP + Vox + Cs, por elección: ' + '; '.join(f'{ANYO[e]}: {num(cb["der"][e])} y {num(mo["der"][e])}' for e in CONG) + '.'),
            ('dato', f'La distancia se abrió en dos tiempos. En 2008 el PP subió en Cabra hasta el {P(cb["pp"]["2008_03"])} y en Montilla se quedó en el {P(mo["pp"]["2008_03"])}. '
                     f'En noviembre de 2019, Vox sacó el {P(cb["vox"]["2019_11"])} en Cabra y el {P(mo["vox"]["2019_11"])} en Montilla; en 2023, el {P(cb["vox"]["2023_07"])} y el {P(mo["vox"]["2023_07"])}.'),
            ('dato', f'Ciudadanos, en cambio, tuvo resultados casi iguales en las dos: {P(cb["cs"]["2015_12"])} y {P(mo["cs"]["2015_12"])} en 2015.'),
            ('dato', f'El PSOE mantiene en Montilla un suelo más alto desde 2019: {P(mo["psoe"]["2023_07"])} en 2023, frente al {P(cb["psoe"]["2023_07"])} en Cabra.'),
            ('patrón', 'Las dos ciudades partían del mismo punto en 2004. La diferencia sale sobre todo del voto al PP desde 2008 y a Vox desde 2019, no de Ciudadanos.'),
        ],
        no_sabemos=['Por qué el PP y Vox crecieron más en una ciudad que en la otra. Hipótesis por contrastar: estructura productiva (la economía del vino en Montilla), historia municipal y liderazgos locales. Sin dos fuentes, ninguna se afirma.'],
        tabla=dict(caption='PP + Vox + Cs en Cabra y Montilla en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'Cabra', 'Montilla', 'Diferencia'],
                   filas=[[ANYO[e], num(cb['der'][e]), num(mo['der'][e]), num(cb['der'][e] - mo['der'][e])] for e in CONG]),
        grafico=(lineas([('Cabra', cb['der'], 'var(--pp)', True), ('Montilla', mo['der'], 'var(--accent)', True)], CONG,
                        'PP + Vox + Cs en Cabra y Montilla, 2004-2023', 20, 60),
                 'PP, Vox y Cs juntos en Cabra y Montilla, generales de 2004 a 2023 (% del voto válido).'),
        compara='Dos municipios de entre 19.000 y 23.000 habitantes de la provincia de Córdoba, elegidos por ser de los más parecidos de Andalucía en renta, edad, extranjeros, estudios, paro y tamaño.',
        limites='«Gemelos» según seis indicadores del INE; pueden diferir en otros (estructura económica, historia, oferta electoral local) que los datos no recogen.',
        csv='cabra-montilla.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Cabra', 'Montilla'],
        faq=[('¿Cómo se eligen los gemelos?', 'Se estandarizan seis indicadores (renta, edad media, porcentaje de extranjeros, estudios superiores, paro y tamaño) y se buscan pares de municipios de más de 15.000 habitantes de la misma comunidad con la menor distancia entre ellos.')],
    ))

    # ------------------------------------------------------------------ excepciones: Puerto Real
    pr = C['puerto_real']
    out.append(dict(
        slug='puerto-real', serie='excepciones', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'Puerto Real vota {num(abs(pr["diferencia"]), 0)} puntos menos a la derecha de lo que predicen sus datos: la mayor excepción de España',
        pregunta='¿Qué municipio se aparta más de lo que su perfil social haría esperar?',
        resumen=(f'Por su renta, edad, paro, estudios, extranjeros y tamaño, a Puerto Real (Cádiz) le correspondería dar a PP, Vox y Cs alrededor del {P(pr["previsto"])} del voto. '
                 f'El 23J les dio el {P(pr["der"])}. Es la mayor diferencia entre los {C["n_municipios_10k"]} municipios de más de 10.000 habitantes. '
                 f'El PSOE ganó allí con el {P(pr["psoe"])} en una provincia que ganó el PP.'),
        estado='Dato',
        cuerpo=[
            ('dato', f'El modelo estima el voto a PP, Vox y Cs de cada municipio a partir de seis indicadores del INE y de su provincia. Explica el {num(C["modelo_municipal"]["r2_derecha"] * 100, 0)} % de las diferencias entre municipios. Lo que no explica es la materia prima de esta serie.'),
            ('dato', f'Puerto Real: previsto {P(pr["previsto"])}, real {P(pr["der"])}; diferencia de {num(abs(pr["diferencia"]))} puntos. Detrás vienen Castro-Urdiales (Cantabria), Jódar (Jaén) y las cuencas mineras asturianas.'),
            ('dato', f'En la provincia de Cádiz, el PP sacó el {P(pr["prov_pp"])} y el PSOE el {P(pr["prov_psoe"])}. En Puerto Real: PSOE {P(pr["psoe"])}, Sumar {P(pr["sumar"])}, PP {P(pr["pp"])} y Vox {P(pr["vox"])}.'),
            ('dato', f'El resto de grandes municipios de la bahía votan cerca de lo previsto: Cádiz capital {num(abs(next(b["diferencia"] for b in pr["bahia"] if b["municipio"] == "Cádiz")))} puntos por debajo, San Fernando y El Puerto de Santa María un poco por encima.'),
            ('patrón', f'La desviación es antigua. La izquierda estatal (PSOE más Sumar, Podemos o IU) sacó el {P(pr["izq_serie"]["2004_03"])} en 2004 y el {P(pr["izq_serie"]["2023_07"])} en 2023; en el conjunto de la provincia, el {P(pr["izq_prov_serie"]["2004_03"])} y el {P(pr["izq_prov_serie"]["2023_07"])}. Puerto Real ha perdido mucho menos voto de izquierda que su provincia.'),
            ('dato', f'En las municipales de 2023 fue primera la lista «{pr["m2023_lista"]}», con el {P(pr["m2023_lista_pct"])} del voto válido.'),
        ],
        no_sabemos=['Por qué. La hipótesis más citada en la conversación pública es la tradición obrera y sindical ligada a la industria naval de la bahía. Esta pieza aún no la ha contrastado con dos fuentes independientes (hemeroteca, estudios sobre el movimiento obrero en la bahía, entrevistas), así que la deja como hipótesis.'],
        tabla=dict(caption='Voto a PP + Vox + Cs real y previsto por el perfil en los municipios de más de 20.000 habitantes de Cádiz, 23J de 2023',
                   cabecera=['Municipio', 'Real', 'Previsto', 'Diferencia', 'Renta (€/u.c.)'],
                   filas=[[b['municipio'], num(b['real']), num(b['previsto']), ('+' if b['diferencia'] > 0 else '') + num(b['diferencia']), num(b['renta'], 0)] for b in pr['bahia']]),
        grafico=(barras_previsto(pr['bahia'], 'Voto a PP, Vox y Cs real y previsto en los grandes municipios de Cádiz', 'Puerto Real'),
                 'Voto a PP, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno) en los municipios de más de 20.000 habitantes de Cádiz, 23J de 2023.'),
        compara=f'Los {C["n_municipios_10k"]} municipios españoles de más de 10.000 habitantes con todos los indicadores disponibles, frente a lo que predice para cada uno un modelo estadístico estimado con {num(C["modelo_municipal"]["n"], 0)} municipios.',
        limites='Un modelo estadístico no es una explicación: la diferencia indica dónde mirar, no por qué. «Derecha» suma PP, Vox y Cs; los partidos regionalistas quedan fuera, lo que afecta a Cantabria (PRC).',
        csv='puerto-real.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Puerto Real'],
        faq=[('¿Qué significa «lo que predicen sus datos»?', 'Es el porcentaje que estima un modelo de regresión a partir de la renta, la edad media, el porcentaje de extranjeros, los estudios superiores, el paro, el tamaño del municipio y su provincia. La metodología completa está enlazada al final.')],
    ))

    # ------------------------------------------------------------------ voto doble: Badalona
    bd = C['badalona']
    out.append(dict(
        slug='badalona', serie='voto-doble', fecha_datos='mayo y julio de 2023', revisado='2026-10-06',
        titulo=f'Badalona dio al PP el {num(bd["M2023"]["PP"], 0)} % en mayo y el {num(bd["2023_07"]["PP"], 0)} % en julio: la mayor distancia de España entre voto local y estatal',
        pregunta='¿Dónde se separa más el voto a un mismo partido entre las municipales y las generales?',
        resumen=(f'En las municipales del 28 de mayo de 2023, el PP sacó en Badalona el {P(bd["M2023"]["PP"])} del voto válido. '
                 f'En las generales del 23 de julio, dos meses después, el {P(bd["2023_07"]["PP"])}, y el PSC ganó con el {P(bd["2023_07"]["PSOE"])}. '
                 f'Son {num(bd["M2023"]["PP"] - bd["2023_07"]["PP"], 0)} puntos de diferencia, la mayor entre los {bd["n_20k"]} municipios de más de 20.000 habitantes.'),
        estado='Dato',
        cuerpo=[
            ('dato', f'Municipales de 2023: PP {P(bd["M2023"]["PP"])}, PSC {P(bd["M2023"]["PSOE"])}, espacio comuns/Podemos {P(bd["M2023"]["SUMAR"])}, ERC {P(bd["M2023"]["ERC"])}. Participación {P(bd["M2023"]["part"])}.'),
            ('dato', f'Generales de 2023: PSC {P(bd["2023_07"]["PSOE"])}, PP {P(bd["2023_07"]["PP"])}, Sumar {P(bd["2023_07"]["SUMAR"])}, ERC {P(bd["2023_07"]["ERC"])}, Vox {P(bd["2023_07"]["VOX"])}. Participación {P(bd["2023_07"]["part"])}.'),
            ('dato', f'La distancia no es de 2023: en las municipales de 2019 el PP sacó el {P(bd["M2019"]["PP"])} y en las generales de noviembre de 2019, el {P(bd["2019_11"]["PP"])}; en 2015, {P(bd["M2015"]["PP"])} y {P(bd["2015_12"]["PP"])}.'),
            ('dato', 'Le siguen, por distancia entre el voto al PP en las municipales y en las generales de 2023: ' +
                     ', '.join(f'{t["municipio"]} ({num(t["dif"])})' for t in bd['top'][1:5]) + '.'),
            ('patrón', f'En Badalona el voto a Vox en las municipales ({P(bd["M2023"]["VOX"])}) es mucho menor que en las generales ({P(bd["2023_07"]["VOX"])}): parte del electorado que vota a Vox o al PSC en julio parece votar al PP en mayo. Con datos agregados no se puede saber quién cambia; solo que el saldo cambia.'),
        ],
        no_sabemos=['Cuánto se debe al candidato del PP en la ciudad y cuánto a otros factores locales. Es la hipótesis evidente, pero requiere encuestas postelectorales o estudios que esta pieza no ha incorporado.'],
        tabla=dict(caption='Voto en Badalona en las municipales y las generales de 2015, 2019 y 2023 (% del voto válido)',
                   cabecera=['Elección', 'PP', 'PSC', 'Comuns / Sumar', 'ERC', 'Junts', 'Cs', 'Vox', 'Participación'],
                   filas=[[n, num(bd[e]['PP']), num(bd[e]['PSOE']), num(bd[e]['SUMAR']), num(bd[e]['ERC']), num(bd[e]['JUNTS']), num(bd[e]['CS']), num(bd[e]['VOX']), num(bd[e]['part'])]
                          for e, n in (('M2015', 'Municipales 2015'), ('2015_12', 'Generales 2015'), ('M2019', 'Municipales 2019'), ('2019_11', 'Generales nov. 2019'),
                                       ('M2023', 'Municipales 2023'), ('2023_07', 'Generales 2023'))]),
        grafico=(barras_agrupadas([(n, {'Municipales': bd[a]['PP'], 'Generales': bd[b]['PP']}) for n, a, b in
                                   (('2015', 'M2015', '2015_12'), ('2019', 'M2019', '2019_11'), ('2023', 'M2023', '2023_07'))],
                                  [('Municipales', 'var(--pp)'), ('Generales', 'var(--muted)')], 'Voto al PP en Badalona, municipales y generales', ymax=60),
                 'Voto al PP en Badalona en las municipales y en las generales de 2015, 2019 y 2023 (% del voto válido).'),
        compara=f'Las municipales y las generales de 2015, 2019 y 2023 en Badalona, y la diferencia de voto al PP entre municipales y generales de 2023 en los {bd["n_20k"]} municipios de más de 20.000 habitantes.',
        limites='El censo de las municipales incluye a residentes de la Unión Europea, que no votan en las generales. En Badalona su peso es pequeño, pero los dos censos no son idénticos.',
        csv='badalona.csv', fuentes=['interior'], lugares=['Badalona'],
        faq=None,
    ))

    # ------------------------------------------------------------------ quién no vota: paro y renta
    pa = C['paro']
    q = pa['quintil_renta_tercil_paro']
    dr, dp = pa['deciles_renta_uc'], pa['deciles_paro_2021']
    out.append(dict(
        slug='paro-renta-participacion', serie='quien-no-vota', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='A igual renta, los barrios con más paro votan menos: el desempleo pesa más que el dinero en la abstención',
        pregunta='¿Es la pobreza o el desempleo lo que más se asocia a no votar?',
        resumen=(f'En las {num(pa["n_secciones"], 0)} secciones censales de España, la participación del 23J sube con la renta: del {P(dr[0]["part"])} en el 10 % de secciones más pobres al {P(dr[-1]["part"])} en el 10 % más rico. '
                 f'Pero cuando se comparan secciones con la misma renta, la que tiene más paro vota menos: en el quintil más pobre, del {P(q["1"]["1"])} con poco paro al {P(q["1"]["3"])} con mucho. '
                 f'Teniendo en cuenta a la vez renta, paro, estudios, edad y extranjeros, el paro es la variable que más resta.'),
        estado='Patrón',
        cuerpo=[
            ('dato', f'Participación por decil de renta de la sección: ' + ', '.join(num(d['part']) for d in dr) + ' (del más pobre al más rico).'),
            ('dato', f'Participación por decil de paro: ' + ', '.join(num(d['part']) for d in dp) + ' (de menos a más paro).'),
            ('dato', 'Dentro de cada quinto de renta, participación de las secciones con menos, medio y más paro: ' +
                     '; '.join(f'quintil {k}: {num(v["1"])}, {num(v["2"])} y {num(v["3"])}' for k, v in q.items()) + '.'),
            ('patrón', f'En un modelo con las cinco variables a la vez (y la provincia), una sección con una desviación típica más de paro vota {num(abs(pa["coef"]["paro_2021"]))} puntos menos. La renta, sola, se asocia a {num(pa["solo_renta"])} puntos por desviación típica; con las demás variables en el modelo, su efecto baja a {num(pa["coef"]["lrenta"])}.'),
            ('patrón', f'El mismo orden aparece en Cataluña con datos de la Generalitat: el paro resta {num(abs(pa["cataluna"]["m2023"]["paro"]))} puntos por desviación típica en las municipales de 2023 y {num(abs(pa["cataluna"]["p2024"]["paro"]))} en el Parlament de 2024, y la renta, una vez controlado lo demás, casi no pesa.') if pa.get('cataluna') else None,
        ],
        no_sabemos=['Si el desempleo causa la abstención. Es una correlación entre barrios (ecológica), no entre personas: no dice que los parados voten menos, sino que votan menos los barrios con más paro. La literatura académica sobre desempleo y participación es el contraste pendiente.'],
        tabla=dict(caption='Participación el 23J de 2023 por quintil de renta y tercil de paro de la sección censal (%)',
                   cabecera=['Quintil de renta', 'Poco paro', 'Paro medio', 'Mucho paro', 'Diferencia'],
                   filas=[[k, num(v['1']), num(v['2']), num(v['3']), num(v['1'] - v['3'])] for k, v in q.items()]),
        grafico=(lineas([('Mucho paro', {str(k): v['3'] for k, v in q.items()}, 'var(--accent2)', True),
                         ('Poco paro', {str(k): v['1'] for k, v in q.items()}, 'var(--accent)', True)],
                        [str(k) for k in q], 'Participación por quintil de renta, secciones con poco y mucho paro', 55, 80, ' %'),
                 'Participación el 23J por quintil de renta de la sección (1 = más pobre, 5 = más rico), en las secciones con menos y más paro de cada quintil.'),
        compara=f'Las {num(pa["n_secciones"], 0)} secciones censales de España con datos de renta, paro, estudios, edad y extranjeros; participación del 23J sin voto CERA.',
        limites='Paro y estudios son del censo de 2021; renta de 2023. Correlación ecológica: no permite hablar de individuos.',
        csv='participacion-renta-paro.csv', fuentes=['interior', 'ine_adrh', 'ine_censo', 'transparencia'], lugares=[],
        faq=[('¿Votan menos los parados?', 'Estos datos no lo pueden decir: comparan barrios, no personas. Lo que muestran es que los barrios con más paro votan menos que otros con la misma renta.')],
    ))
    for p in out:
        p['cuerpo'] = [c for c in p['cuerpo'] if c]
    return out
