"""Segunda tanda de piezas del Atlas (2026-10-07). Mismas reglas que piezas.py: cada cifra sale de cifras.json (C),
cada párrafo se marca como dato o patrón, y las explicaciones sin dos fuentes van a «Lo que no sabemos».

Campos opcionales para cuando haya fuentes accesibles (se rellenan a mano, con su fuente):
  foto   dict(src, alt, autor, licencia, url)   foto de Wikimedia Commons con su crédito
  color  [(texto, [url1, url2])]                notas de color local, cada una con dos fuentes independientes
"""
from graficos import num, lineas, barras_previsto, barras_agrupadas, ANYO

CONG = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
P = lambda x: num(x) + ' %'
N = lambda x: num(x, 0)
D = lambda x: num(abs(x))
S = lambda x: ('+' if x > 0 else '−' if x < 0 else '') + num(abs(x))
SIGLAS = {'IU', 'IAS', 'PSOE', 'PP', 'BNG', 'IU-MÁS', 'PAÍS-IAS'}


def lista(nombre):
    """«CONVOCATORIA POR MIERES IU-MÁS PAÍS-IAS» -> «Convocatoria por Mieres IU-Más País-IAS»."""
    pal = []
    for i, w in enumerate(nombre.split()):
        partes = []
        for p in w.split('-'):
            if p in ('IU', 'IAS', 'PSOE', 'PP', 'BNG'):
                partes.append(p)
            elif i and p.lower() in ('por', 'y', 'de', 'la', 'el', 'del', 'los', 'las', 'con'):
                partes.append(p.lower())
            else:
                partes.append(p.capitalize())
        pal.append('-'.join(partes))
    return ' '.join(pal)


def piezas2(C):
    out = []

    # ------------------------------------------------------------------ excepciones: cuencas mineras
    cu = C['cuencas']
    mm = {x['municipio']: x for x in cu['municipios']}
    cinco = ['San Martín del Rey Aurelio', 'Mieres', 'Langreo', 'Laviana', 'Aller']
    izq04 = [mm[n]['izq']['2004_03'] for n in cinco]
    izq23 = [mm[n]['izq']['2023_07'] for n in cinco]
    am = {r['municipio']: r for r in cu['asturias_modelo']}
    out.append(dict(
        slug='cuencas-mineras-asturianas', serie='excepciones', fecha_datos='2004-2023', revisado=None,
        titulo=f'Las cuencas mineras de Asturias votan a la derecha hasta {N(abs(mm["San Martín del Rey Aurelio"]["diferencia"]))} puntos menos de lo que predice su perfil, y a la izquierda como hace veinte años',
        pregunta='¿Qué queda del voto de las cuencas mineras asturianas, y cuánto se aparta de lo que su perfil haría esperar?',
        resumen=(f'En San Martín del Rey Aurelio, Mieres, Langreo y Laviana, PP, Vox y Cs sacaron el 23J entre el {P(min(mm[n]["der"]["2023_07"] for n in cinco[:4]))} y el {P(max(mm[n]["der"]["2023_07"] for n in cinco[:4]))}, '
                 f'entre {D(mm["Laviana"]["diferencia"])} y {D(mm["San Martín del Rey Aurelio"]["diferencia"])} puntos menos de lo que predicen su renta, su edad, su paro y su tamaño. '
                 f'La izquierda estatal sigue donde estaba en 2004: entre el {P(min(izq23))} y el {P(max(izq23))} del voto, frente al {P(cu["asturias_izq"]["2023_07"])} del conjunto de Asturias.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Valles que no se movieron'),
            ('dato', f'En los valles del Nalón y del Caudal, la izquierda estatal (el PSOE más el espacio de IU, Podemos y Sumar) sacó en 2004 entre el {P(min(izq04))} y el {P(max(izq04))} del voto. '
                     f'Veinte años, ocho elecciones generales y dos partidos nuevos después, en 2023 sacó entre el {P(min(izq23))} y el {P(max(izq23))}.'),
            ('dato', f'En el mismo periodo, el conjunto de Asturias pasó de dar a la derecha el {P(cu["asturias_der"]["2004_03"])} al {P(cu["asturias_der"]["2023_07"])}. '
                     f'El 23J el PP ganó en la comunidad con el {P(cu["asturias_pp"])}, frente al {P(cu["asturias_psoe"])} del PSOE. En las cuencas, el PSOE fue primero en los cinco municipios.'),
            ('sub', 'Lo que dice el modelo'),
            ('dato', f'El modelo de esta serie estima el voto a PP, Vox y Cs de cada municipio a partir de su renta, edad, paro, estudios, población extranjera, tamaño y provincia. '
                     f'Para San Martín del Rey Aurelio predice el {P(mm["San Martín del Rey Aurelio"]["previsto"])}; el 23J fue el {P(mm["San Martín del Rey Aurelio"]["der"]["2023_07"])}. '
                     f'Es la {mm["San Martín del Rey Aurelio"]["rango"]}.ª mayor diferencia a la baja de los municipios españoles de más de 10.000 habitantes. Mieres es la {mm["Mieres"]["rango"]}.ª ({S(mm["Mieres"]["diferencia"])} puntos).'),
            ('dato', f'Langreo ({S(mm["Langreo"]["diferencia"])}), Laviana ({S(mm["Laviana"]["diferencia"])}), Lena ({S(am["Lena"]["diferencia"])}) y Aller ({S(mm["Aller"]["diferencia"])}) completan la lista: '
                     f'los seis municipios asturianos que más se apartan del modelo a la baja son de las cuencas.'),
            ('dato', f'Las ciudades de la costa votan casi lo que predice su perfil: Gijón ({S(am["Gijón"]["diferencia"])}) y Avilés ({S(am["Avilés"]["diferencia"])}). Oviedo se aparta en sentido contrario ({S(am["Oviedo"]["diferencia"])}).'),
            ('sub', 'El voto local: IU, por delante del PSOE'),
            ('dato', f'En las municipales de mayo de 2023, la lista más votada en Mieres fue «{lista(mm["Mieres"]["m2023_lista"])}», con el {P(mm["Mieres"]["m2023_lista_pct"])}. '
                     f'En Langreo ganó «{lista(mm["Langreo"]["m2023_lista"])}», con el {P(mm["Langreo"]["m2023_lista_pct"])}. En Aller, el PSOE sacó el {P(mm["Aller"]["m2023_lista_pct"])}.'),
            ('patrón', f'En las cuencas, el espacio a la izquierda del PSOE es más fuerte que en el resto de España. En 2015, Podemos e IU sumaron el {P(mm["Mieres"]["sumar"]["2015_12"])} en Mieres y el {P(mm["Langreo"]["sumar"]["2015_12"])} en Langreo.'),
            ('dato', f'Son también municipios con mucho paro (entre el {P(min(mm[n]["paro"] for n in cinco))} y el {P(max(mm[n]["paro"] for n in cinco))} en 2021). El modelo ya tiene en cuenta ese dato y el resto del perfil; la diferencia es lo que queda después.'),
        ],
        no_sabemos=['Por qué. La historia minera y sindical de los valles es la hipótesis obvia, pero esta pieza todavía no la ha contrastado con dos fuentes independientes, así que la deja como hipótesis.'],
        tabla=dict(caption='Voto a PP + Vox + Cs real y previsto en los municipios asturianos de más de 9.000 habitantes, 23J de 2023 (%)',
                   cabecera=['Municipio', 'Real', 'Previsto', 'Diferencia'],
                   filas=[[r['municipio'], num(r['real']), num(r['previsto']), S(r['diferencia'])] for r in cu['asturias_modelo']]),
        grafico=(barras_previsto(cu['asturias_modelo'], 'Voto a PP, Vox y Cs real y previsto en Asturias', 'San Martín del Rey Aurelio'),
                 'Voto a PP, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno) en los municipios asturianos de más de 9.000 habitantes, 23J de 2023.'),
        compara='Cinco municipios de las cuencas del Nalón y del Caudal frente al resto de Asturias y frente a lo que predice el modelo municipal de esta serie.',
        limites='El modelo no es una explicación: la diferencia indica dónde mirar, no por qué. «Izquierda» suma el PSOE y el espacio de IU, Podemos y Sumar; «derecha», PP, Vox y Cs (Foro Asturias, aliado del PP, queda en otros).',
        csv='cuencas-mineras.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=cinco,
        faq=None,
    ))

    # ------------------------------------------------------------------ excepciones: Lalín y Vilanova
    la = C['lalin']
    li, vi = la['lalin'], la['vilanova']
    out.append(dict(
        slug='lalin-vilanova-de-arousa', serie='excepciones', fecha_datos='23 de julio de 2023', revisado=None,
        titulo=f'Lalín y Vilanova de Arousa, los dos municipios donde el PP saca más voto por encima de lo que predicen sus datos',
        pregunta='¿Dónde vota la derecha mucho más de lo que su perfil social haría esperar?',
        resumen=(f'Por su renta, su edad, su paro y su tamaño, a Lalín le correspondería dar a PP, Vox y Cs el {P(li["previsto"])} del voto. El 23J les dio el {P(li["der"]["2023_07"])}. '
                 f'En Vilanova de Arousa, el {P(vi["der"]["2023_07"])} frente a un {P(vi["previsto"])} previsto. '
                 f'Son las dos mayores diferencias al alza entre los municipios de más de 10.000 habitantes de España, y las dos están en Pontevedra.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'La otra cara de las excepciones'),
            ('dato', 'Esta serie empezó con Puerto Real, el municipio que menos vota a la derecha en relación con su perfil. Este es el extremo contrario: '
                     f'los lugares donde PP, Vox y Cs sacan mucho más de lo que predice el modelo. Los dos primeros de la lista son gallegos y de la misma provincia.'),
            ('dato', f'Lalín, en el interior de Pontevedra, tiene {N(li["poblacion"])} habitantes, una renta de {N(li["renta"])} euros por unidad de consumo y un paro del {P(li["paro"])} en 2021. '
                     f'El modelo le asigna un {P(li["previsto"])} de voto a la derecha. Votó un {P(li["der"]["2023_07"])}: {D(li["diferencia"])} puntos más. El PP, por sí solo, sacó el {P(li["pp"]["2023_07"])}.'),
            ('dato', f'Vilanova de Arousa, en la costa, tiene {N(vi["poblacion"])} habitantes, {N(vi["renta"])} euros de renta y un paro del {P(vi["paro"])}. Previsto: {P(vi["previsto"])}. Real: {P(vi["der"]["2023_07"])}.'),
            ('sub', 'Un PP más fuerte que su provincia'),
            ('dato', f'En el conjunto de la provincia de Pontevedra, el PP sacó el {P(la["pontevedra_pp"])}; en Galicia, el {P(la["galicia_pp"])}. En Lalín sacó el {P(li["pp"]["2023_07"])} y en Vilanova, el {P(vi["pp"]["2023_07"])}.'),
            ('dato', f'No es un año aislado. El PP no ha bajado del {P(min(li["pp"].values()))} en Lalín en ninguna de las ocho generales desde 2004, y su mejor resultado fue el de 2011, con el {P(li["pp"]["2011_11"])}. '
                     f'Su peor resultado fue el de abril de 2019, con el {P(li["pp"]["2019_04"])}.'),
            ('dato', f'En las municipales también gana con holgura: {P(li["m2023"]["pp"])} en Lalín y {P(vi["m2023"]["pp"])} en Vilanova en mayo de 2023.'),
            ('sub', 'El resto de la lista'),
            ('dato', 'Detrás vienen ' + ', '.join(f'{r["municipio"]} ({r["provincia"]}, {S(r["diferencia"])})' for r in la['top'][2:7]) + '. '
                     'Son municipios muy distintos entre sí, sin un patrón geográfico claro.'),
            ('dato', 'Vilanova de Arousa ya aparece en el Atlas: es el vecino de A Illa de Arousa, que vota más de 20 puntos menos al PP. La frontera entre los dos es, a la vez, la frontera entre una de las mayores excepciones al alza de España y un municipio que vota mucho más a la izquierda.'),
        ],
        no_sabemos=['Por qué. Las hipótesis habituales en Galicia (la implantación territorial del PP, el peso de los liderazgos municipales) no están contrastadas en esta pieza con dos fuentes independientes.'],
        tabla=dict(caption='Los diez municipios de más de 10.000 habitantes con más voto a PP + Vox + Cs por encima de lo previsto, 23J de 2023 (%)',
                   cabecera=['Municipio', 'Provincia', 'Real', 'Previsto', 'Diferencia'],
                   filas=[[r['municipio'], r['provincia'], num(r['real']), num(r['previsto']), S(r['diferencia'])] for r in la['top']]),
        grafico=(barras_previsto(la['top'], 'Voto a PP, Vox y Cs real y previsto: las diez mayores diferencias al alza', 'Lalín'),
                 'Voto a PP, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno), diez municipios con más voto por encima de lo previsto, 23J de 2023.'),
        compara=f'Los {C["n_municipios_10k"]} municipios españoles de más de 10.000 habitantes, frente a lo que predice el modelo municipal de esta serie.',
        limites='El modelo no es una explicación. «Derecha» suma PP, Vox y Cs. Los municipios gallegos son extensos y dispersos: el tamaño en habitantes no recoge bien su estructura en parroquias.',
        csv='lalin-vilanova.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Lalín', 'Vilanova de Arousa'],
        faq=None,
    ))

    # ------------------------------------------------------------------ fronteras: Cuenca de Pamplona
    pa = C['pamplona']
    pm = {x['municipio']: x for x in pa['municipios']}
    ci, zi = pm['Cizur'], pm['Zizur Mayor/Zizur Nagusia']
    fil = sorted(pa['municipios'], key=lambda x: x['diferencia'])
    out.append(dict(
        slug='cuenca-de-pamplona', serie='fronteras', fecha_datos='23 de julio de 2023', revisado=None,
        titulo=f'Cizur y Zizur Mayor, a {num(pa["km_cizur_zizur"])} kilómetros: {N(ci["der"]["2023_07"] - zi["der"]["2023_07"])} puntos de diferencia en el voto a la derecha',
        pregunta='¿Cuánto cambia el voto de un municipio a otro dentro de la Cuenca de Pamplona?',
        resumen=(f'En Cizur, PP (con UPN), Vox y Cs sacaron el 23J el {P(ci["der"]["2023_07"])} del voto. En Zizur Mayor, su vecino, el {P(zi["der"]["2023_07"])}. '
                 f'Los centros de sus términos municipales están a {num(pa["km_cizur_zizur"])} kilómetros. '
                 f'En la misma corona de Pamplona, Ansoáin y Villava votan a la derecha {D(pm["Ansoáin/Antsoain"]["diferencia"])} y {D(pm["Villava/Atarrabia"]["diferencia"])} puntos menos de lo que predice su perfil, y en Villava ganó EH Bildu.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Un mosaico alrededor de la capital'),
            ('dato', f'Pamplona votó el 23J casi lo que predice su perfil: un {P(pm["Pamplona/Iruña"]["der"]["2023_07"])} para PP y UPN, Vox y Cs, frente a un {P(pm["Pamplona/Iruña"]["previsto"])} previsto. '
                     f'El conjunto de Navarra, un {P(pa["navarra_der"])}. Alrededor de la capital, en un radio de pocos kilómetros, el voto se reparte de forma mucho más desigual.'),
            ('sub', 'Cizur y Zizur Mayor'),
            ('dato', f'Cizur es un municipio de {N(ci["poblacion"])} habitantes con la renta más alta de la tabla, {N(ci["renta"])} euros por unidad de consumo. '
                     f'Allí PP y UPN sacaron el {P(ci["pp"]["2023_07"])} y Vox el {P(ci["vox"]["2023_07"])}. El modelo le asigna a la derecha un {P(ci["previsto"])}; votó un {P(ci["der"]["2023_07"])}.'),
            ('dato', f'Zizur Mayor, con {N(zi["poblacion"])} habitantes y {N(zi["renta"])} euros de renta, votó un {P(zi["der"]["2023_07"])} a la derecha, casi lo previsto ({P(zi["previsto"])}). '
                     f'Allí EH Bildu sacó el {P(zi["bildu_2023"])} y el PSOE el {P(zi["psoe"]["2023_07"])}.'),
            ('patrón', f'Parte de la distancia acompaña a la renta, que es más alta en Cizur. Pero el modelo ya cuenta con ella, y aun así Cizur vota {D(ci["diferencia"])} puntos más a la derecha de lo previsto.'),
            ('sub', 'El otro lado: Ansoáin y Villava'),
            ('dato', f'En Ansoáin, PP y UPN sacaron el {P(pm["Ansoáin/Antsoain"]["pp"]["2023_07"])} y la derecha sumó un {P(pm["Ansoáin/Antsoain"]["der"]["2023_07"])}, frente a un {P(pm["Ansoáin/Antsoain"]["previsto"])} previsto. Ganó el PSOE con el {P(pm["Ansoáin/Antsoain"]["psoe"]["2023_07"])}.'),
            ('dato', f'En Villava, EH Bildu fue el partido más votado, con el {P(pm["Villava/Atarrabia"]["bildu_2023"])}. La derecha se quedó en el {P(pm["Villava/Atarrabia"]["der"]["2023_07"])}.'),
            ('dato', f'Burlada ({S(pm["Burlada/Burlata"]["diferencia"])}) también vota menos a la derecha de lo previsto; Barañáin ({S(pm["Barañáin/Barañain"]["diferencia"])}), Zizur Mayor y Berrioplano ({S(pm["Berrioplano/Berriobeiti"]["diferencia"])}), casi lo previsto; '
                     f'el Valle de Egüés ({S(pm["Valle de Egüés/Eguesibar"]["diferencia"])}) y Cizur, más.'),
        ],
        no_sabemos=['Qué separa a estos municipios además de la renta: la composición por origen de sus vecinos, la historia de su crecimiento urbano o la presencia del euskera. Ninguna de esas hipótesis está contrastada aquí con dos fuentes.'],
        tabla=dict(caption='Voto en Pamplona y ocho municipios de su cuenca, 23J de 2023 (% del voto válido)',
                   cabecera=['Municipio', 'Habitantes', 'Renta (€/u.c.)', 'PP + UPN', 'PSOE', 'EH Bildu', 'Derecha', 'Previsto', 'Diferencia', 'Gana'],
                   filas=[[x['municipio'], N(x['poblacion']), N(x['renta']), num(x['pp']['2023_07']), num(x['psoe']['2023_07']), num(x['bildu_2023']),
                           num(x['der']['2023_07']), num(x['previsto']), S(x['diferencia']), {'BILDU': 'EH Bildu'}.get(x['gana'], x['gana'])] for x in fil]),
        grafico=(barras_previsto([{'municipio': x['municipio'].split('/')[0], 'real': x['der']['2023_07'], 'previsto': x['previsto']} for x in fil],
                                 'Voto a la derecha real y previsto en la Cuenca de Pamplona', 'Cizur'),
                 'Voto a PP y UPN, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno), Pamplona y ocho municipios de su cuenca, 23J de 2023.'),
        compara='Pamplona y ocho municipios de su área metropolitana, entre sí y frente a lo que predice el modelo municipal de esta serie.',
        limites=f'La distancia ({num(pa["km_cizur_zizur"])} km) es entre los centroides de los dos términos municipales, no entre sus cascos urbanos. «PP» incluye a UPN, que en 2023 se presentó por separado. Cizur es pequeño ({N(ci["poblacion"])} habitantes).',
        csv='cuenca-de-pamplona.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Cizur', 'Zizur Mayor', 'Ansoáin', 'Villava'],
        faq=None,
    ))

    # ------------------------------------------------------------------ fronteras: Getxo y Portugalete
    gx = C['getxo']
    gm = {x['municipio']: x for x in gx['municipios']}
    ge, po = gm['Getxo'], gm['Portugalete']
    out.append(dict(
        slug='getxo-portugalete', serie='fronteras', fecha_datos='23 de julio de 2023', revisado=None,
        titulo=f'Getxo y Portugalete, a los dos lados de la ría: el PSOE saca {N(po["psoe"]["2023_07"] - ge["psoe"]["2023_07"])} puntos más en una orilla que en la otra',
        pregunta='¿Cuánto cambia el voto de una orilla a otra de la desembocadura de la ría de Bilbao?',
        resumen=(f'El 23J, el PSOE sacó el {P(po["psoe"]["2023_07"])} en Portugalete y el {P(ge["psoe"]["2023_07"])} en Getxo, al otro lado de la ría. '
                 f'En Getxo ganó el PNV y el PP sacó el {P(ge["pp"]["2023_07"])}, más del doble que en Portugalete ({P(po["pp"]["2023_07"])}). '
                 f'La renta de Getxo ({N(ge["renta"])} euros por unidad de consumo) es la más alta de la ría; la de Portugalete, {N(po["renta"])}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos orillas'),
            ('dato', f'La desembocadura de la ría de Bilbao separa la margen derecha, con Getxo y Leioa, de la margen izquierda, con Portugalete, Santurtzi, Sestao y Barakaldo. '
                     f'Los centros de los términos de Getxo y Portugalete están a {num(gx["km_getxo_portugalete"])} kilómetros.'),
            ('dato', f'En la margen izquierda ganó el PSOE en los cuatro municipios, con entre el {P(min(gm[n]["psoe"]["2023_07"] for n in ("Portugalete", "Santurtzi", "Sestao", "Barakaldo")))} y el {P(max(gm[n]["psoe"]["2023_07"] for n in ("Portugalete", "Santurtzi", "Sestao", "Barakaldo")))}. '
                     f'En la derecha ganó el PNV: {P(ge["pnv_2023"])} en Getxo y {P(gm["Leioa"]["pnv_2023"])} en Leioa.'),
            ('dato', f'El conjunto de Bizkaia votó así: PNV {P(gx["bizkaia"]["pnv"])}, PSOE {P(gx["bizkaia"]["psoe"])}, EH Bildu {P(gx["bizkaia"]["bildu"])}, PP {P(gx["bizkaia"]["pp"])} y Sumar {P(gx["bizkaia"]["sumar"])}.'),
            ('sub', 'Getxo, un caso aparte'),
            ('dato', f'Getxo es el municipio de la tabla con más renta y menos paro ({P(ge["paro"])} en 2021). El PP sacó allí el {P(ge["pp"]["2023_07"])}, más del doble que en el conjunto de Bizkaia. '
                     f'El modelo de esta serie le asigna a PP, Vox y Cs un {P(ge["previsto"])}; votaron un {P(ge["der"]["2023_07"])}.'),
            ('dato', f'En Portugalete, la derecha sumó un {P(po["der"]["2023_07"])}, casi lo previsto ({P(po["previsto"])}).'),
            ('sub', 'Veinte años de la misma frontera'),
            ('dato', f'La distancia en el voto al PSOE no es nueva. En 2004, el PSOE sacó el {P(po["psoe"]["2004_03"])} en Portugalete y el {P(ge["psoe"]["2004_03"])} en Getxo; el PP, el {P(po["pp"]["2004_03"])} y el {P(ge["pp"]["2004_03"])}.'),
            ('patrón', 'En la margen izquierda, el voto socialista ha resistido el paso de los años con pocos cambios; en Getxo, el voto se reparte sobre todo entre el PNV y el PP.'),
        ],
        no_sabemos=['Qué parte de la frontera responde a la historia industrial de la margen izquierda y qué parte a la renta. Es la hipótesis evidente, pero esta pieza no la ha contrastado con dos fuentes independientes.'],
        tabla=dict(caption='Voto en los municipios de las dos márgenes de la ría de Bilbao, 23J de 2023 (% del voto válido)',
                   cabecera=['Municipio', 'Renta (€/u.c.)', 'PNV', 'PSOE', 'PP', 'EH Bildu', 'Sumar', 'Gana'],
                   filas=[[x['municipio'], N(x['renta']), num(x['pnv_2023']), num(x['psoe']['2023_07']), num(x['pp']['2023_07']), num(x['bildu_2023']),
                           num(x['sumar']['2023_07']), x['gana']] for x in gx['municipios']]),
        grafico=(barras_agrupadas([(x['municipio'], {'PNV': x['pnv_2023'], 'PSOE': x['psoe']['2023_07'], 'PP': x['pp']['2023_07']}) for x in gx['municipios']],
                                  [('PNV', 'var(--accent2)'), ('PSOE', 'var(--psoe)'), ('PP', 'var(--pp)')], 'PNV, PSOE y PP en las dos márgenes de la ría', ymax=50),
                 'PNV, PSOE y PP en Getxo y Leioa (margen derecha) y en Portugalete, Santurtzi, Sestao y Barakaldo (margen izquierda), 23J de 2023 (% del voto válido).'),
        compara='Seis municipios de las dos márgenes de la desembocadura de la ría de Bilbao, entre sí y frente al conjunto de Bizkaia.',
        limites=f'La distancia ({num(gx["km_getxo_portugalete"])} km) es entre los centroides de los términos municipales. Datos por municipio: dentro de cada uno hay barrios muy distintos.',
        csv='getxo-portugalete.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Getxo', 'Portugalete'],
        faq=None,
    ))

    # ------------------------------------------------------------------ gemelos: Aranda y Miranda
    am2 = C['aranda_miranda']
    ar, mi = am2['aranda'], am2['miranda']
    out.append(dict(
        slug='aranda-miranda', serie='gemelos', fecha_datos='2004-2023', revisado=None,
        titulo=f'Aranda y Miranda, las dos Burgos: misma renta y mismo paro, y {N(ar["der"]["2023_07"] - mi["der"]["2023_07"])} puntos de distancia en el voto a la derecha',
        pregunta='¿Votan igual las dos grandes ciudades de la provincia de Burgos después de la capital?',
        resumen=(f'Aranda de Duero y Miranda de Ebro tienen casi la misma población ({N(ar["poblacion"])} y {N(mi["poblacion"])} habitantes), la misma renta ({N(ar["renta"])} y {N(mi["renta"])} euros) y el mismo paro ({P(ar["paro"])} y {P(mi["paro"])}). '
                 f'El 23J, Aranda dio a PP, Vox y Cs el {P(ar["der"]["2023_07"])} y la ganó el PP; Miranda, el {P(mi["der"]["2023_07"])}, y la ganó el PSOE con el {P(mi["psoe"]["2023_07"])}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos ciudades gemelas'),
            ('dato', f'Después de la capital, las dos ciudades más pobladas de la provincia de Burgos se parecen en casi todo lo que mide el INE. '
                     f'Renta por unidad de consumo: {N(ar["renta"])} euros en Aranda y {N(mi["renta"])} en Miranda. Paro en 2021: {P(ar["paro"])} y {P(mi["paro"])}. '
                     f'Edad media: {num(ar["edad"])} y {num(mi["edad"])} años. Estudios superiores: {P(ar["estudios"])} y {P(mi["estudios"])}.'),
            ('dato', f'Con ese perfil, el modelo de esta serie predice para las dos lo mismo: un {P(ar["previsto"])} de voto a PP, Vox y Cs. Aranda se queda cerca ({P(ar["der"]["2023_07"])}). '
                     f'Miranda, {D(mi["diferencia"])} puntos por debajo, es la {am2["rango_miranda"]}.ª mayor diferencia a la baja de España entre los municipios de más de 10.000 habitantes.'),
            ('sub', 'Una distancia que ha crecido'),
            ('dato', f'En 2004 ya votaban distinto, pero menos. La derecha sacó el {P(ar["der"]["2004_03"])} en Aranda y el {P(mi["der"]["2004_03"])} en Miranda; el PSOE, el {P(ar["psoe"]["2004_03"])} y el {P(mi["psoe"]["2004_03"])}.'),
            ('dato', f'Desde entonces, la derecha creció en Aranda hasta el {P(ar["der"]["2023_07"])} y en Miranda apenas se movió ({P(mi["der"]["2023_07"])}). '
                     f'En el conjunto de la provincia pasó del {P(am2["burgos_der"]["2004_03"])} al {P(am2["burgos_der"]["2023_07"])}.'),
            ('patrón', f'La distancia entre las dos ciudades pasó de {num(ar["der"]["2004_03"] - mi["der"]["2004_03"])} puntos en 2004 a {num(ar["der"]["2023_07"] - mi["der"]["2023_07"])} en 2023. '
                       'Miranda se ha quedado donde estaba; Aranda se ha movido con su provincia.'),
            ('dato', f'Vox muestra la misma brecha: en noviembre de 2019 sacó el {P(ar["vox"]["2019_11"])} en Aranda y el {P(mi["vox"]["2019_11"])} en Miranda; en 2023, el {P(ar["vox"]["2023_07"])} y el {P(mi["vox"]["2023_07"])}.'),
            ('sub', 'En las municipales'),
            ('dato', f'En mayo de 2023 el PSOE fue la lista más votada en Miranda ({P(mi["m2023"]["psoe"])}). En Aranda, el PP ({P(ar["m2023"]["pp"])}) superó por poco al PSOE ({P(ar["m2023"]["psoe"])}), y las listas locales y otras sumaron el {P(ar["m2023"]["otros"])}.'),
        ],
        no_sabemos=['Por qué se separaron. Miranda está en el límite con Álava y La Rioja, y Aranda en la ribera del Duero; las diferencias de estructura económica o de historia local son hipótesis que esta pieza no ha contrastado con dos fuentes.'],
        tabla=dict(caption='PP + Vox + Cs y PSOE en Aranda de Duero y Miranda de Ebro en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'Derecha Aranda', 'Derecha Miranda', 'PSOE Aranda', 'PSOE Miranda'],
                   filas=[[ANYO[e], num(ar['der'][e]), num(mi['der'][e]), num(ar['psoe'][e]), num(mi['psoe'][e])] for e in CONG]),
        grafico=(lineas([('Aranda', ar['der'], 'var(--pp)', True), ('Miranda', mi['der'], 'var(--accent)', True), ('Prov. Burgos', am2['burgos_der'], 'var(--muted)', False)],
                        CONG, 'PP + Vox + Cs en Aranda, Miranda y la provincia de Burgos', 30, 60),
                 'PP, Vox y Cs juntos en Aranda de Duero, Miranda de Ebro y el conjunto de la provincia de Burgos, generales de 2004 a 2023 (% del voto válido).'),
        compara='Las dos ciudades de la provincia de Burgos con más población después de la capital, en las ocho generales de 2004 a 2023.',
        limites='«Gemelos» según los indicadores del INE; pueden diferir en otros que los datos no recogen. «Derecha» suma PP, Vox y Cs.',
        csv='aranda-miranda.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Aranda de Duero', 'Miranda de Ebro'],
        faq=None,
    ))

    # ------------------------------------------------------------------ el municipio que cambió: Los Palacios y Villafranca
    lpz = C['los_palacios']
    lp = lpz['lp']
    out.append(dict(
        slug='los-palacios-y-villafranca', serie='el-municipio-que-cambio', fecha_datos='2004-2023', revisado=None,
        titulo=f'Los Palacios y Villafranca: el PSOE pasó del {N(lp["psoe"]["2004_03"])} % al {N(lp["psoe"]["2023_07"])} % en veinte años, y en mayo ganó una lista de IU',
        pregunta='¿Cómo cambia de voto un antiguo feudo socialista andaluz?',
        resumen=(f'En las generales de 2004, el PSOE sacó en Los Palacios y Villafranca (Sevilla) el {P(lp["psoe"]["2004_03"])} del voto. En 2023, el {P(lp["psoe"]["2023_07"])}, y ganó el PP con el {P(lp["pp"]["2023_07"])}. '
                 f'PP, Vox y Cs pasaron del {P(lp["der"]["2004_03"])} al {P(lp["der"]["2023_07"])}. '
                 f'Dos meses antes, en las municipales, la lista más votada fue la de IU, con el {P(lp["m2023_lista_pct"])}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'De feudo a municipio disputado'),
            ('dato', f'Los Palacios y Villafranca, en la campiña del sur de Sevilla, tiene {N(lp["poblacion"])} habitantes. En 2004 votaba al PSOE más que su provincia: '
                     f'el PSOE sacó el {P(lp["psoe"]["2004_03"])}, frente al {P(lpz["sevilla_psoe"]["2004_03"])} del conjunto de Sevilla.'),
            ('dato', f'La caída llegó de golpe en 2011: el PSOE bajó al {P(lp["psoe"]["2011_11"])} y el PP subió al {P(lp["pp"]["2011_11"])}. '
                     f'Desde 2015, el voto socialista no ha vuelto a subir: {P(lp["psoe"]["2015_12"])} en 2015, {P(lp["psoe"]["2019_11"])} en noviembre de 2019 y {P(lp["psoe"]["2023_07"])} en 2023.'),
            ('dato', f'Vox llegó fuerte. Sacó el {P(lp["vox"]["2019_04"])} en abril de 2019, el {P(lp["vox"]["2019_11"])} en noviembre de ese año y el {P(lp["vox"]["2023_07"])} en 2023.'),
            ('sub', 'Más deprisa que su provincia'),
            ('dato', f'En el conjunto de la provincia de Sevilla, la derecha pasó del {P(lpz["sevilla_der"]["2004_03"])} al {P(lpz["sevilla_der"]["2023_07"])}. En Los Palacios, del {P(lp["der"]["2004_03"])} al {P(lp["der"]["2023_07"])}: '
                     f'empezó por debajo de su provincia y ha terminado por encima.'),
            ('dato', f'El modelo de esta serie, que tiene en cuenta renta, edad, paro, estudios, extranjeros y tamaño, le asigna a la derecha un {P(lp["previsto"])}. El 23J votó {D(lp["diferencia"])} puntos más. '
                     f'Es un municipio de renta baja ({N(lp["renta"])} euros por unidad de consumo) y con mucho paro ({P(lp["paro"])} en 2021).'),
            ('sub', 'Mayo y julio de 2023'),
            ('dato', f'En las municipales del 28 de mayo de 2023, la lista más votada fue «{lista(lp["m2023_lista"])}», con el {P(lp["m2023_lista_pct"])}. El PP sacó el {P(lp["m2023"]["pp"])} y el PSOE, el {P(lp["m2023"]["psoe"])}.'),
            ('patrón', f'El mismo municipio que en mayo dio casi la mitad de sus votos a una lista de IU dio en julio más de la mitad a PP, Vox y Cs. Con datos agregados no se puede saber cuántos vecinos cambiaron de papeleta y cuántos solo votaron en una de las dos citas: '
                       f'la participación fue del {P(lp["m2023"]["part"])} en mayo y del {P(lp["part"])} en julio.'),
        ],
        no_sabemos=['Qué explica el giro: los cambios en el empleo agrícola, la llegada de vecinos nuevos o el peso del gobierno municipal en el voto local. Son hipótesis sin contrastar con dos fuentes.'],
        tabla=dict(caption='Voto en Los Palacios y Villafranca en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'PSOE', 'PP', 'Vox', 'Derecha', 'Derecha (prov. Sevilla)'],
                   filas=[[ANYO[e], num(lp['psoe'][e]), num(lp['pp'][e]), num(lp['vox'][e]), num(lp['der'][e]), num(lpz['sevilla_der'][e])] for e in CONG]),
        grafico=(lineas([('PSOE', lp['psoe'], 'var(--psoe)', True), ('PP+Vox+Cs', lp['der'], 'var(--pp)', True), ('Derecha prov.', lpz['sevilla_der'], 'var(--muted)', False)],
                        CONG, 'PSOE y derecha en Los Palacios y Villafranca, 2004-2023', 0, 70),
                 'PSOE y PP + Vox + Cs en Los Palacios y Villafranca y voto a la derecha en el conjunto de la provincia de Sevilla, generales de 2004 a 2023 (% del voto válido).'),
        compara='Las ocho generales de 2004 a 2023 y las municipales de 2023 en Los Palacios y Villafranca, frente al conjunto de la provincia de Sevilla.',
        limites='El censo de las municipales incluye a residentes de la Unión Europea. «Derecha» suma PP, Vox y Cs.',
        csv='los-palacios.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Los Palacios y Villafranca'],
        faq=None,
    ))

    # ------------------------------------------------------------------ contra su provincia: Castro-Urdiales
    ca = C['castro']
    cs = ca['castro']
    out.append(dict(
        slug='castro-urdiales', serie='contra-su-provincia', fecha_datos='2004-2023', revisado=None,
        titulo=f'Castro-Urdiales, el municipio cántabro donde el PSOE ganó por {N(cs["psoe"]["2023_07"] - cs["pp"]["2023_07"])} puntos mientras el PP ganaba Cantabria',
        pregunta='¿Por qué vota tan distinto de su comunidad el municipio cántabro más cercano a Bizkaia?',
        resumen=(f'El 23J, el PP ganó en Cantabria con el {P(ca["cantabria_pp"])}, frente al {P(ca["cantabria_psoe"])} del PSOE. En Castro-Urdiales el resultado fue el contrario: PSOE {P(cs["psoe"]["2023_07"])}, PP {P(cs["pp"]["2023_07"])}. '
                 f'Por su perfil, a Castro le correspondería dar a PP, Vox y Cs un {P(cs["previsto"])}; les dio el {P(cs["der"]["2023_07"])}. '
                 f'Es la {ca["rango"]}.ª mayor diferencia a la baja de los municipios españoles de más de 10.000 habitantes.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Una isla en el mapa cántabro'),
            ('dato', f'Castro-Urdiales es el municipio más oriental de la costa de Cantabria, en el límite con Bizkaia, y tiene {N(cs["poblacion"])} habitantes. '
                     f'El 23J votó así: PSOE {P(cs["psoe"]["2023_07"])}, PP {P(cs["pp"]["2023_07"])}, Sumar {P(cs["sumar"]["2023_07"])} y Vox {P(cs["vox"]["2023_07"])}.'),
            ('dato', f'En el conjunto de Cantabria, PP, Vox y Cs sumaron el {P(ca["cantabria_der"]["2023_07"])}. En Castro, el {P(cs["der"]["2023_07"])}: {num(ca["cantabria_der"]["2023_07"] - cs["der"]["2023_07"])} puntos menos.'),
            ('sub', 'Lo que dice el modelo'),
            ('dato', f'Castro tiene una renta de {N(cs["renta"])} euros por unidad de consumo y un {P(cs["estudios"])} de vecinos con estudios superiores. Con ese perfil y su provincia, el modelo de esta serie le asigna a la derecha un {P(cs["previsto"])}. '
                     f'Votó {D(cs["diferencia"])} puntos menos. Solo Puerto Real se aparta más en toda España.'),
            ('sub', 'Siempre por debajo de Cantabria'),
            ('dato', f'La distancia no es nueva. En 2004, la derecha sacó el {P(cs["der"]["2004_03"])} en Castro y el {P(ca["cantabria_der"]["2004_03"])} en Cantabria. En ninguna de las ocho generales desde entonces ha bajado de 10 puntos.'),
            ('dato', f'El PSOE quedó por delante del PP en Castro en 2004 ({P(cs["psoe"]["2004_03"])}), en 2008 ({P(cs["psoe"]["2008_03"])}), en las dos generales de 2019 y en 2023 ({P(cs["psoe"]["2023_07"])}); el PP, en 2011, 2015 y 2016. En 2015, el espacio de Podemos e IU sacó allí el {P(cs["sumar"]["2015_12"])}.'),
            ('sub', 'El voto local'),
            ('dato', f'En las municipales de 2023 el PSOE fue la lista más votada, con el {P(cs["m2023"]["psoe"])}, y las candidaturas locales y otras sumaron el {P(cs["m2023"]["otros"])}.'),
        ],
        no_sabemos=['Si la cercanía a Bilbao y la llegada de vecinos desde Bizkaia explican la diferencia. Es la hipótesis más citada, pero esta pieza no tiene datos de procedencia de los vecinos ni dos fuentes que la confirmen.'],
        tabla=dict(caption='PP + Vox + Cs y PSOE en Castro-Urdiales y voto a la derecha en Cantabria, generales 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'Derecha Castro', 'Derecha Cantabria', 'PSOE Castro', 'PP Castro'],
                   filas=[[ANYO[e], num(cs['der'][e]), num(ca['cantabria_der'][e]), num(cs['psoe'][e]), num(cs['pp'][e])] for e in CONG]),
        grafico=(lineas([('Cantabria', ca['cantabria_der'], 'var(--pp)', True), ('Castro', cs['der'], 'var(--accent)', True)], CONG,
                        'PP + Vox + Cs en Castro-Urdiales y en Cantabria, 2004-2023', 20, 60),
                 'PP, Vox y Cs juntos en Castro-Urdiales y en el conjunto de Cantabria, generales de 2004 a 2023 (% del voto válido).'),
        compara='Castro-Urdiales frente al conjunto de Cantabria en las ocho generales de 2004 a 2023, y frente a lo que predice el modelo municipal de esta serie.',
        limites='El PRC no se presentó a las generales de 2023; en años anteriores su voto queda en «otros». «Derecha» suma PP, Vox y Cs.',
        csv='castro-urdiales.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Castro-Urdiales'],
        faq=None,
    ))

    # ------------------------------------------------------------------ contra su provincia: Vigo
    vg = C['vigo']
    v = vg['vigo']
    out.append(dict(
        slug='vigo', serie='contra-su-provincia', fecha_datos='2004-2023', revisado=None,
        titulo=f'Vigo, la única gran ciudad gallega donde ganó el PSOE el 23J, y donde en mayo le dio el {N(v["m2023"]["psoe"])} %',
        pregunta='¿Dónde gana el PSOE en la Galicia del PP?',
        resumen=(f'El 23J el PP ganó en Galicia con el {P(vg["galicia"]["pp"])}, frente al {P(vg["galicia"]["psoe"])} del PSOE. '
                 f'De los {vg["n_20k"]} municipios gallegos de más de 20.000 habitantes, el PSOE solo fue primero en dos: {" y ".join(vg["psoe_gana_20k"])}. '
                 f'En Vigo sacó el {P(v["psoe"]["2023_07"])} en las generales y el {P(v["m2023"]["psoe"])} en las municipales de mayo.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Una excepción en el mapa gallego'),
            ('dato', f'Galicia es territorio del PP: en las generales de 2023 sacó el {P(vg["galicia"]["pp"])} del voto, {num(vg["galicia"]["pp"] - vg["galicia"]["psoe"])} puntos por encima del PSOE. '
                     f'Ganó en las otras seis grandes ciudades: ' + ', '.join(f'{c["municipio"]} ({P(c["pp"])})' for c in vg['ciudades'][1:]) + '.'),
            ('dato', f'Vigo, la ciudad más poblada de Galicia, con {N(v["poblacion"])} habitantes, votó al revés: PSOE {P(v["psoe"]["2023_07"])}, PP {P(v["pp"]["2023_07"])}, Sumar {P(v["sumar"]["2023_07"])} y BNG {P(v["bng_2023"])}.'),
            ('sub', 'Mayo: un voto local aún más socialista'),
            ('dato', f'En las municipales del 28 de mayo de 2023, el PSOE sacó en Vigo el {P(v["m2023"]["psoe"])} del voto válido. El PP se quedó en el {P(v["m2023"]["pp"])} y el BNG en el {P(v["m2023"]["bng"])}.'),
            ('patrón', f'Entre mayo y julio, el PSOE perdió en Vigo {num(v["m2023"]["psoe"] - v["psoe"]["2023_07"])} puntos y el PP ganó {num(v["pp"]["2023_07"] - v["m2023"]["pp"])}. '
                       f'Parte de los vigueses que eligen al PSOE para el ayuntamiento no lo eligen para el Congreso. La participación también cambió: {P(v["m2023"]["part"])} en mayo y {P(v["part"])} en julio.'),
            ('sub', 'No siempre fue así'),
            ('dato', f'En las generales de 2011, Vigo dio al PP el {P(v["pp"]["2011_11"])} y al PSOE el {P(v["psoe"]["2011_11"])}. '
                     f'Desde abril de 2019, el PSOE ha quedado siempre por delante: {P(v["psoe"]["2019_04"])}, {P(v["psoe"]["2019_11"])} y {P(v["psoe"]["2023_07"])}.'),
            ('dato', f'El modelo de esta serie le asigna a PP, Vox y Cs un {P(v["previsto"])} en Vigo; votaron un {P(v["der"]["2023_07"])}, {D(v["diferencia"])} puntos menos.'),
        ],
        no_sabemos=['Cuánto del voto municipal de Vigo se debe a su alcalde y cuánto a la ciudad. Es la hipótesis evidente, pero necesita encuestas postelectorales o estudios que esta pieza no ha incorporado.'],
        tabla=dict(caption='PP y PSOE en las siete ciudades gallegas de más de 60.000 habitantes, 23J de 2023 (% del voto válido)',
                   cabecera=['Ciudad', 'PP', 'PSOE', 'Gana'],
                   filas=[[c['municipio'], num(c['pp']), num(c['psoe']), c['gana']] for c in vg['ciudades']]),
        grafico=(lineas([('PSOE', v['psoe'], 'var(--psoe)', True), ('PP', v['pp'], 'var(--pp)', True)], CONG, 'PP y PSOE en Vigo, 2004-2023', 10, 50),
                 'PP y PSOE en Vigo, generales de 2004 a 2023 (% del voto válido).'),
        compara=f'Vigo frente al conjunto de Galicia y a las otras grandes ciudades gallegas; las municipales y las generales de 2023.',
        limites='El censo de las municipales incluye a residentes de la Unión Europea. Las siete ciudades de la tabla son las de más de 60.000 habitantes.',
        csv='vigo-galicia.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Vigo'],
        faq=None,
    ))

    # ------------------------------------------------------------------ quién no vota: pueblos pequeños
    pq = C['pequenos']
    t = {x['tamano']: x for x in pq['tamanos']}
    out.append(dict(
        slug='pueblos-pequenos', serie='quien-no-vota', fecha_datos='mayo y julio de 2023', revisado=None,
        titulo='Los pueblos pequeños son los únicos que votan más para elegir alcalde que para elegir al Gobierno',
        pregunta='¿Dónde se vota más en las municipales que en las generales?',
        resumen=(f'En las ciudades se vota mucho menos en las municipales que en las generales: en las de más de 100.000 habitantes, un {P(t["100.000+"]["part_municipales"])} en mayo de 2023 frente a un {P(t["100.000+"]["part_generales"])} en julio. '
                 f'En los pueblos de menos de 2.000 habitantes ocurre al revés. '
                 f'De los {N(pq["n_menos_2000"])} municipios de ese tamaño, en {N(pq["n_menos_2000_mas_mun"])} se votó más para elegir el ayuntamiento que para el Congreso; de los {pq["n_mas_20000"]} de más de 20.000, solo en {pq["n_mas_20000_mas_mun"]}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos elecciones en dos meses'),
            ('dato', 'Mayo y julio de 2023 ofrecen una comparación poco habitual: unas municipales y unas generales con solo ocho semanas de distancia. '
                     'Los mismos municipios, casi los mismos censos y dos preguntas distintas: quién gobierna el pueblo y quién gobierna el país.'),
            ('dato', f'En el conjunto de España se votó más en julio ({P(pq["total_generales"])}) que en mayo ({P(pq["total_municipales"])}). Pero la diferencia depende del tamaño del municipio. En las ciudades de más de 100.000 habitantes, la participación fue del {P(t["100.000+"]["part_municipales"])} en las municipales y del {P(t["100.000+"]["part_generales"])} en las generales. '
                     f'En las de 20.000 a 50.000, del {P(t["20.000-49.999"]["part_municipales"])} y del {P(t["20.000-49.999"]["part_generales"])}.'),
            ('sub', 'El punto de giro, en torno a los 2.000 habitantes'),
            ('dato', f'A medida que el municipio se hace más pequeño, la distancia se cierra. En los pueblos de 2.000 a 5.000 habitantes las dos participaciones casi coinciden ({P(t["2.000-4.999"]["part_municipales"])} y {P(t["2.000-4.999"]["part_generales"])}). '
                     f'Por debajo de los 2.000, las municipales ganan: {P(t["250-499"]["part_municipales"])} frente a {P(t["250-499"]["part_generales"])} en los de 250 a 500 habitantes.'),
            ('dato', f'En los pueblos de 250 a 1.000 habitantes, alrededor de dos de cada tres votaron más en mayo que en julio ({P(t["250-499"]["pct_mas_municipales"])} y {P(t["500-999"]["pct_mas_municipales"])}). En las ciudades de más de 100.000, ninguna.'),
            ('patrón', 'Cuanto más cerca está el ayuntamiento, más se vota para elegirlo. En una ciudad, las municipales son una elección menor; en un pueblo pequeño, la que más se vota.'),
            ('dato', f'En los municipios de menos de 100 habitantes las dos participaciones son casi iguales ({P(t["<100"]["part_municipales"])} y {P(t["<100"]["part_generales"])}), y la mitad de ellos votó más en mayo y la otra mitad, más en julio.'),
        ],
        no_sabemos=['Por qué. La cercanía a los candidatos, la ausencia de alternativa en muchos pueblos con una sola lista o la movilización vecinal son explicaciones plausibles que esta pieza no ha contrastado con dos fuentes.'],
        tabla=dict(caption='Participación en las municipales de mayo y las generales de julio de 2023 por tamaño del municipio (%)',
                   cabecera=['Habitantes', 'Municipios', 'Municipales', 'Generales', '% con más participación en municipales'],
                   filas=[[x['tamano'], N(x['municipios']), num(x['part_municipales']), num(x['part_generales']), num(x['pct_mas_municipales'])] for x in pq['tamanos']]),
        grafico=(lineas([('Municipales', {x['tamano']: x['part_municipales'] for x in pq['tamanos']}, 'var(--accent2)', True),
                         ('Generales', {x['tamano']: x['part_generales'] for x in pq['tamanos']}, 'var(--accent)', True)],
                        [x['tamano'] for x in pq['tamanos']], 'Participación por tamaño del municipio, mayo y julio de 2023', 50, 90,
                        etiquetas={'<100': '<100', '100-249': '', '250-499': '250', '500-999': '', '1.000-1.999': '1.000', '2.000-4.999': '',
                                   '5.000-9.999': '5.000', '10.000-19.999': '', '20.000-49.999': '20.000', '50.000-99.999': '', '100.000+': '100.000+'}),
                 'Participación en las municipales del 28 de mayo y las generales del 23 de julio de 2023 según el número de habitantes del municipio. El eje marca el inicio de cada tramo; los once tramos están en la tabla.'),
        compara=f'Los {N(pq["n"])} municipios con datos de participación en las dos elecciones de 2023, agrupados por tamaño.',
        limites='El censo de las municipales incluye a los residentes de la Unión Europea, que no votan en las generales y participan menos; eso rebaja algo la participación municipal, sobre todo en zonas turísticas. La participación de las generales es sobre el censo de residentes en España.',
        csv='participacion-por-tamano.csv', fuentes=['interior'], lugares=[],
        faq=None,
    ))

    for p in out:
        p['cuerpo'] = [c for c in p['cuerpo'] if c]
    return out
