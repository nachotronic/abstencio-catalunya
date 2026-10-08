"""Tercera tanda de piezas del Atlas (2026-10-07). Mismas reglas que piezas.py y piezas2.py: cada cifra sale de
cifras.json (C), cada párrafo se marca como dato o patrón, y las explicaciones sin dos fuentes van a «Lo que no sabemos».
Las fotos y las notas de color («Sobre el terreno») están en terreno.py, con sus fuentes en el expediente.
"""
from terreno import terreno
from graficos import num, lineas, barras_previsto, divergente, barras_agrupadas, ANYO

CONG = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
P = lambda x: num(x) + ' %'
N = lambda x: num(x, 0)
D = lambda x: num(abs(x))
S = lambda x: ('+' if x > 0 else '−' if x < 0 else '') + num(abs(x))
NOMBRE_ELEC = {**ANYO, 'M2007': 'mun. 2007', 'M2011': 'mun. 2011', 'M2015': 'mun. 2015', 'M2019': 'mun. 2019', 'M2023': 'mun. 2023',
               'E2019': 'eur. 2019', 'E2024': 'eur. 2024'}


def lista(nombre):
    """«CON ANDALUCIA IZQUIERDA UNIDA CON ARAHAL» -> «Con Andalucía Izquierda Unida con Arahal»."""
    fijas = {'ANDALUCIA': 'Andalucía', 'ESPAÑOL': 'Español', 'ANDALUCÍA': 'Andalucía', 'PROGRÉS': 'Progrés', 'COMPROMÍS': 'Compromís'}
    pal = []
    for i, w in enumerate(nombre.split()):
        if w in fijas:
            pal.append(fijas[w])
        elif i and w.lower() in ('por', 'y', 'de', 'la', 'el', 'del', 'los', 'las', 'con', 'per', 'dels', 'i'):
            pal.append(w.lower())
        elif w == '-':
            pal.append('-')
        else:
            pal.append(w.capitalize())
    return ' '.join(pal)


def piezas3(C):
    out = []

    # ------------------------------------------------------------------ excepciones: Jódar
    jj = C['jodar']
    jo, jp = jj['jodar'], jj['jaen_part']
    ps = jo['part_serie']
    rh = jj['res_hist']
    j10 = {x['municipio']: x for x in jj['jaen_10k']}
    out.append(dict(
        slug='jodar', serie='excepciones', fecha_datos='2004-2024', revisado='2026-10-07',
        titulo=f'Jódar, el municipio de España que menos vota en relación con su perfil: {N(abs(jo["diferencia_part"]))} puntos por debajo en las generales',
        pregunta='¿Dónde se vota mucho menos de lo que predicen la renta, la edad, el paro y el tamaño de un municipio?',
        resumen=(f'Con su perfil, a Jódar (Jaén) le correspondería una participación del {P(jo["previsto_part"])} en las generales de julio de 2023. Votó el {P(ps["2023_07"])}, '
                 f'la mayor diferencia a la baja de los {N(jj["n_10k"])} municipios españoles de más de 10.000 habitantes. '
                 f'No siempre fue así: en 2004 Jódar votó más que su provincia ({P(ps["2004_03"])} frente a {P(jp["2004_03"])}). '
                 f'En las municipales sigue votando casi como el resto de Jaén.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'El primero de la lista'),
            ('dato', f'Jódar, en la Sierra Mágina, tiene {N(jo["poblacion"])} habitantes, una renta de {N(jo["renta"])} euros por unidad de consumo y una edad media de {num(jo["edad"])} años. '
                     f'El modelo de participación de esta serie, que estima cuánto vota cada municipio a partir de su renta, edad, paro, estudios, población extranjera, tamaño y provincia, '
                     f'le asigna un {P(jo["previsto_part"])}. El 23 de julio de 2023 votó el {P(ps["2023_07"])}: {D(jo["diferencia_part"])} puntos menos.'),
            ('dato', f'Ningún municipio español de más de 10.000 habitantes se queda tan lejos de lo previsto. Detrás vienen ' +
                     ', '.join(f'{r["municipio"]} ({r["provincia"]}, {S(r["diferencia"])})' for r in jj['top'][1:4]) + f' y {jj["top"][4]["municipio"]} ({jj["top"][4]["provincia"]}, {S(jj["top"][4]["diferencia"])}).'),
            ('sub', 'Una caída de veinte años'),
            ('dato', f'En 2004, Jódar votó el {P(ps["2004_03"])}, algo más que el conjunto de la provincia de Jaén ({P(jp["2004_03"])}). '
                     f'Desde entonces, su participación en las generales no ha dejado de bajar: {P(ps["2011_11"])} en 2011, {P(ps["2016_06"])} en 2016, {P(ps["2019_04"])} en abril de 2019 y {P(ps["2023_07"])} en 2023. '
                     f'La de la provincia bajó mucho menos, hasta el {P(jp["2023_07"])}.'),
            ('dato', f'La distancia con lo que predice el modelo se abrió en 2019. En las generales de 2004 a 2016, Jódar votaba entre {D(max(rh[e]["diferencia"] for e in CONG[:5]))} y {D(min(rh[e]["diferencia"] for e in CONG[:5]))} puntos menos de lo previsto. '
                     f'En abril y noviembre de 2019 la diferencia fue de {D(rh["2019_04"]["diferencia"])} y {D(rh["2019_11"]["diferencia"])} puntos, la segunda mayor de España en las dos elecciones; en 2023, la mayor.'),
            ('sub', 'En mayo, como su provincia'),
            ('dato', f'En las municipales la imagen cambia. En mayo de 2023 Jódar votó el {P(ps["M2023"])}, algo menos que el conjunto de Jaén ({P(jp["M2023"])}), pero más que en las generales de dos meses después. '
                     f'En las municipales de 2019, el {P(ps["M2019"])} frente al {P(jp["M2019"])} de la provincia.'),
            ('patrón', 'Jódar no es un municipio que haya dejado de votar en general: es un municipio que vota en sus elecciones locales como el resto de su provincia y que se queda muy por debajo en las generales.'),
            ('dato', f'En las europeas de junio de 2024 votó el {P(ps["E2024"])}, frente al {P(jp["E2024"])} de la provincia.'),
            ('sub', 'Sus vecinos'),
            ('dato', f'Entre los municipios de Jaén de más de 10.000 habitantes, ninguno se aparta tanto. Úbeda votó lo que predice su perfil ({P(j10["Úbeda"]["g2023"])}), Baeza algo más ({P(j10["Baeza"]["g2023"])}) y Mancha Real, de tamaño parecido a Jódar, el {P(j10["Mancha Real"]["g2023"])}.'),
        ],
        no_sabemos=['Por qué. Muchos vecinos de Jódar trabajan como temporeros fuera del municipio (ver «Sobre el terreno»), y una hipótesis es que parte del censo esté lejos de casa en las fechas de algunas elecciones. '
                    'Pero noviembre de 2019 y julio de 2023 son meses distintos, y esta pieza no ha encontrado dos fuentes independientes que relacionen esa movilidad con la participación. Queda como hipótesis.',
                    'Si influye el voto por correo: los datos por mesa no separan cuánta gente votó por correo en cada municipio.'],
        tabla=dict(caption='Participación en Jódar y en el conjunto de la provincia de Jaén, 2004-2024 (% del censo de residentes en España)',
                   cabecera=['Elección', 'Jódar', 'Provincia de Jaén', 'Diferencia'],
                   filas=[[NOMBRE_ELEC[e], num(ps[e]), num(jp[e]), S(round(ps[e] - jp[e], 1))]
                          for e in CONG + ['M2007', 'M2011', 'M2015', 'M2019', 'M2023', 'E2019', 'E2024']]),
        grafico=(lineas([('Jódar', {e: ps[e] for e in CONG}, 'var(--accent)', True), ('Prov. Jaén', {e: jp[e] for e in CONG}, 'var(--muted)', False)],
                        CONG, 'Participación en las generales en Jódar y en la provincia de Jaén', 50, 90),
                 'Participación en las elecciones generales de 2004 a 2023 en Jódar y en el conjunto de la provincia de Jaén (% del censo de residentes en España).'),
        compara=f'Los {N(jj["n_10k"])} municipios españoles de más de 10.000 habitantes, frente a lo que predice el modelo de participación de esta serie; y Jódar frente a su provincia en quince elecciones.',
        limites='La participación es sobre el censo de residentes en España (sin CERA). El censo de las municipales y las europeas incluye a residentes de la Unión Europea; en Jódar son muy pocos. El modelo no es una explicación: indica dónde mirar.',
        csv='jodar.csv', fuentes=['interior', 'europeas', 'ine_adrh', 'ine_censo'], lugares=['Jódar'],
        faq=None,
    ))

    # ------------------------------------------------------------------ fronteras: Sant Cugat y Badia
    va = {x['municipio']: x for x in C['valles']['municipios']}
    sc, ba = va['Sant Cugat del Vallès'], va['Badia del Vallès']
    mt, te = va['Matadepera'], va['Terrassa']
    vb = C['valles']['barcelona']
    out.append(dict(
        slug='sant-cugat-badia', serie='fronteras', fecha_datos='23 de julio de 2023', revisado='2026-10-07',
        titulo=f'Sant Cugat y Badia del Vallès, a {num(C["valles"]["km_santcugat_badia"])} kilómetros: el PSC saca {N(ba["psoe"]["2023_07"] - sc["psoe"]["2023_07"])} puntos más en uno que en otro',
        pregunta='¿Qué separa en las urnas al municipio más rico del Vallès de uno de sus vecinos más pobres?',
        resumen=(f'El 23J, el PSC sacó el {P(ba["psoe"]["2023_07"])} en Badia del Vallès y el {P(sc["psoe"]["2023_07"])} en Sant Cugat, a {num(C["valles"]["km_santcugat_badia"])} kilómetros. '
                 f'Junts, el {P(ba["junts"]["2023_07"])} y el {P(sc["junts"]["2023_07"])}. En cambio, PP, Vox y Cs juntos sacaron casi lo mismo en los dos ({P(ba["der"]["2023_07"])} y {P(sc["der"]["2023_07"])}). '
                 f'La renta por unidad de consumo de Sant Cugat ({N(sc["renta"])} euros) duplica la de Badia ({N(ba["renta"])}).'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos municipios en cinco kilómetros'),
            ('dato', f'Sant Cugat del Vallès tiene {N(sc["poblacion"])} habitantes; Badia del Vallès, {N(ba["poblacion"])}. Entre los centros de sus términos municipales hay {num(C["valles"]["km_santcugat_badia"])} kilómetros. '
                     f'En casi todo lo que mide el INE están en extremos opuestos: el {P(sc["estudios"])} de los adultos de Sant Cugat tiene estudios superiores, frente al {P(ba["estudios"])} en Badia; el paro era del {P(sc["paro"])} y del {P(ba["paro"])} en 2021.'),
            ('dato', f'El PSC ganó en los dos el 23J. En Badia, con el {P(ba["psoe"]["2023_07"])}; en Sant Cugat, con el {P(sc["psoe"]["2023_07"])}, por delante de PP ({P(sc["pp"]["2023_07"])}) y Junts ({P(sc["junts"]["2023_07"])}). '
                     f'Junts sacó en Badia el {P(ba["junts"]["2023_07"])} y ERC, el {P(ba["erc"]["2023_07"])}.'),
            ('sub', 'La frontera no es izquierda y derecha'),
            ('dato', f'PP, Vox y Cs sumaron el {P(sc["der"]["2023_07"])} en Sant Cugat y el {P(ba["der"]["2023_07"])} en Badia. Por dentro, el reparto es distinto: el PP sacó más en Sant Cugat ({P(sc["pp"]["2023_07"])} frente a {P(ba["pp"]["2023_07"])}) y Vox, más en Badia ({P(ba["vox"]["2023_07"])} frente a {P(sc["vox"]["2023_07"])}).'),
            ('patrón', f'Además del PSC, lo que más separa a los dos municipios es el voto independentista: Junts y ERC suman el {num(sc["junts"]["2023_07"] + sc["erc"]["2023_07"])} % en Sant Cugat y el {num(ba["junts"]["2023_07"] + ba["erc"]["2023_07"])} % en Badia. '
                       'En esta parte del Vallès, la renta, los estudios y el voto independentista apuntan en la misma dirección.'),
            ('dato', f'El modelo de esta serie, que predice el voto a PP, Vox y Cs, acierta en Sant Cugat ({P(sc["previsto"])} previsto) y se queda corto en Badia, donde predice un {P(ba["previsto"])} y la derecha sacó {D(ba["diferencia"])} puntos más.'),
            ('sub', 'También se vota distinto'),
            ('dato', f'La participación fue del {P(sc["part"])} en Sant Cugat y del {P(ba["part"])} en Badia. En las municipales de mayo, del {P(sc["m2023"]["part"])} y del {P(ba["m2023"]["part"])}.'),
            ('dato', f'En mayo, Badia volvió a dar la mayoría al PSC ({P(ba["m2023_lista_pct"])}). En Sant Cugat ganó la lista de Junts ({P(sc["m2023_lista_pct"])}).'),
            ('sub', 'Una línea que se repite'),
            ('dato', f'Matadepera y Terrassa, también vecinas ({num(C["valles"]["km_matadepera_terrassa"])} kilómetros), repiten el patrón. En Matadepera, con {N(mt["renta"])} euros de renta, ganó Junts ({P(mt["junts"]["2023_07"])}) y el PSC sacó el {P(mt["psoe"]["2023_07"])}. '
                     f'En Terrassa, con {N(te["renta"])} euros, ganó el PSC con el {P(te["psoe"]["2023_07"])} y Junts sacó el {P(te["junts"]["2023_07"])}.'),
        ],
        no_sabemos=['Por qué el voto independentista se reparte así. El origen de la población, la lengua habitual y la historia urbanística de Badia, construida como polígono de vivienda, son hipótesis que esta pieza no ha contrastado con datos ni con dos fuentes independientes.'],
        tabla=dict(caption='Voto en las generales del 23J de 2023, renta y estudios en nueve municipios del Vallès Occidental (%, salvo renta en euros)',
                   cabecera=['Municipio', 'Renta', 'Estudios sup.', 'PSC', 'PP', 'Sumar', 'Junts', 'ERC', 'Vox', 'Participación'],
                   filas=[[p['municipio'], N(p['renta']), num(p['estudios']), num(p['psoe']['2023_07']), num(p['pp']['2023_07']), num(p['sumar']['2023_07']),
                           num(p['junts']['2023_07']), num(p['erc']['2023_07']), num(p['vox']['2023_07']), num(p['part'])]
                          for p in sorted(C['valles']['municipios'], key=lambda p: -p['renta'])]),
        grafico=(barras_agrupadas([(p['municipio'].replace(' del Vallès', ''), {'PSC': p['psoe']['2023_07'], 'Junts + ERC': p['junts']['2023_07'] + p['erc']['2023_07'],
                                                                                 'PP + Vox + Cs': p['der']['2023_07']})
                                   for p in (mt, sc, te, ba)],
                                  [('PSC', 'var(--psoe)'), ('Junts + ERC', 'var(--accent)'), ('PP + Vox + Cs', 'var(--pp)')],
                                  'Voto en Matadepera, Sant Cugat, Terrassa y Badia del Vallès, 23J de 2023', 60),
                 'PSC, Junts más ERC y PP más Vox más Cs en Matadepera, Sant Cugat del Vallès, Terrassa y Badia del Vallès, ordenados de más a menos renta, generales del 23J de 2023 (% del voto válido).'),
        compara=f'Nueve municipios del Vallès Occidental, con Sant Cugat y Badia, separados por {num(C["valles"]["km_santcugat_badia"])} kilómetros, como pareja principal.',
        limites='Distancia entre los centroides de los términos municipales. «Derecha» suma PP, Vox y Cs. Los datos agregados por municipio no dicen quién vota a quién dentro de cada municipio.',
        csv='sant-cugat-badia.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Sant Cugat del Vallès', 'Badia del Vallès'],
        faq=None,
    ))

    # ------------------------------------------------------------------ fronteras: Ontígola y Aranjuez
    oo = C['ontigola']
    om = {x['municipio']: x for x in oo['municipios']}
    on, ar = om['Ontígola'], om['Aranjuez']
    out.append(dict(
        slug='ontigola-aranjuez', serie='fronteras', fecha_datos='2019-2023', revisado='2026-10-07',
        titulo=f'Ontígola, a {num(oo["km_ontigola_aranjuez"])} kilómetros de Aranjuez, es uno de los {oo["vox_gana_n"]} municipios de España donde Vox ganó el 23J',
        pregunta='¿Por qué Vox gana a un lado del límite entre Madrid y Castilla-La Mancha y no al otro?',
        resumen=(f'El 23 de julio de 2023, Vox fue la lista más votada en Ontígola (Toledo), con el {P(on["vox"]["2023_07"])}. En Aranjuez, al otro lado del límite con la Comunidad de Madrid, sacó el {P(ar["vox"]["2023_07"])} y ganó el PP. '
                 f'Los dos municipios tienen casi la misma renta ({N(on["renta"])} y {N(ar["renta"])} euros). Ontígola es el segundo municipio más poblado de los {oo["vox_gana_n"]} que ganó Vox en esas elecciones.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Una victoria rara'),
            ('dato', f'Vox ganó el 23J en {oo["vox_gana_n"]} de los {N(C["fuente_datos"]["n_municipios"])} municipios de España, y solo {oo["vox_gana_mas_1000"]} de ellos superan los 1.000 habitantes. El mayor es {oo["vox_gana_mayores"][0]} (Guadalajara); el segundo, Ontígola, con {N(on["poblacion"])} habitantes.'),
            ('dato', f'En Ontígola, Vox sacó el {P(on["vox"]["2023_07"])}, por delante del PSOE ({P(on["psoe"]["2023_07"])}) y del PP ({P(on["pp"]["2023_07"])}). '
                     f'En el conjunto de la provincia de Toledo, Vox se quedó en el {P(oo["toledo_vox"])}; en la de Madrid, en el {P(oo["madrid_vox"])}; en España, en el {P(oo["espana_vox"])}.'),
            ('sub', 'Al otro lado del límite'),
            ('dato', f'Aranjuez, con {N(ar["poblacion"])} habitantes, está a {num(oo["km_ontigola_aranjuez"])} kilómetros. Su renta es casi la misma ({N(ar["renta"])} euros por unidad de consumo frente a {N(on["renta"])}), y sus vecinos son algo mayores ({num(ar["edad"])} años de edad media frente a {num(on["edad"])}). '
                     f'Allí ganó el PP con el {P(ar["pp"]["2023_07"])} y Vox sacó el {P(ar["vox"]["2023_07"])}.'),
            ('dato', f'El modelo de esta serie para el voto a Vox, que tiene en cuenta renta, edad, paro, estudios, población extranjera, tamaño y provincia, predice un {P(on["previsto_vox"])} para Ontígola: Vox sacó {D(on["diferencia_vox"])} puntos más. Para Aranjuez predice un {P(ar["previsto_vox"])}.'),
            ('patrón', f'La diferencia no está tanto en el voto a la derecha en su conjunto como en su reparto. PP, Vox y Cs sumaron el {P(on["der"]["2023_07"])} en Ontígola y el {P(ar["der"]["2023_07"])} en Aranjuez; en Ontígola, Vox sacó más que el PP.'),
            ('sub', 'Desde 2019'),
            ('dato', f'No es la primera vez. En noviembre de 2019, Vox sacó en Ontígola el {P(on["vox"]["2019_11"])} y en Aranjuez, el {P(ar["vox"]["2019_11"])}. En abril de 2019, el {P(on["vox"]["2019_04"])} y el {P(ar["vox"]["2019_04"])}.'),
            ('dato', f'En las municipales de mayo de 2023 Vox sacó en Ontígola el {P(on["m2023"]["vox"])}, pero la lista más votada fue la del PSOE, con el {P(on["m2023_lista_pct"])}.'),
            ('sub', 'La Sagra y la frontera madrileña'),
            ('dato', f'Los municipios toledanos de la Sagra, cerca del límite con Madrid, dan a Vox bastante más que la media de España ({P(oo["espana_vox"])}): ' +
                     ', '.join(f'{p["municipio"]} ({P(p["vox"]["2023_07"])})' for p in oo['municipios'] if p['provincia'] == 'Toledo' and p['municipio'] != 'Ontígola') +
                     f'. Al otro lado, Valdemoro dio a Vox el {P(om["Valdemoro"]["vox"]["2023_07"])} y Ciempozuelos, el {P(om["Ciempozuelos"]["vox"]["2023_07"])}.'),
        ],
        no_sabemos=['Por qué. El crecimiento de población de estos municipios toledanos y la llegada de vecinos desde la Comunidad de Madrid son hipótesis habituales; esta pieza no tiene datos de procedencia de los nuevos residentes ni dos fuentes que las respalden.'],
        tabla=dict(caption='Voto a Vox real y previsto, PP y PSOE en Ontígola, Aranjuez y municipios cercanos, 23J de 2023 (%)',
                   cabecera=['Municipio', 'Provincia', 'Vox', 'Vox previsto', 'PP', 'PSOE', 'Gana'],
                   filas=[[p['municipio'], p['provincia'], num(p['vox']['2023_07']), num(p['previsto_vox']), num(p['pp']['2023_07']), num(p['psoe']['2023_07']),
                           {'VOX': 'Vox', 'PSOE': 'PSOE', 'PP': 'PP'}.get(p['gana'], p['gana'])] for p in oo['municipios']]),
        grafico=(barras_previsto([{'municipio': p['municipio'], 'real': p['vox']['2023_07'], 'previsto': p['previsto_vox']} for p in sorted(oo['municipios'], key=lambda p: -p['vox']['2023_07'])],
                                 'Voto a Vox real y previsto en Ontígola y su entorno', 'Ontígola'),
                 'Voto a Vox previsto por el perfil (círculo vacío) y real (círculo lleno) en Ontígola, Aranjuez y municipios cercanos de Toledo y Madrid, 23J de 2023.'),
        compara='Ontígola y Aranjuez, separados por el límite entre Castilla-La Mancha y la Comunidad de Madrid, y siete municipios cercanos a los dos lados.',
        limites='Ontígola tiene menos de 5.000 habitantes: unos cientos de votos mueven varios puntos. El modelo no es una explicación. Distancia entre centroides de los términos municipales.',
        csv='ontigola-aranjuez.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Ontígola', 'Aranjuez'],
        faq=None,
    ))

    # ------------------------------------------------------------------ gemelos: ría de Pontevedra
    rr = {x['municipio']: x for x in C['ria']['municipios']}
    mo, cg, bu, sx, ma, po = rr['Moaña'], rr['Cangas'], rr['Bueu'], rr['Sanxenxo'], rr['Marín'], rr['Poio']
    out.append(dict(
        slug='morrazo-sanxenxo', serie='gemelos', fecha_datos='2004-2023', revisado='2026-10-07',
        titulo=f'Moaña y Sanxenxo, la misma renta y la misma edad: {N(sx["der"]["2023_07"] - mo["der"]["2023_07"])} puntos de distancia en el voto a la derecha',
        pregunta='¿Por qué municipios gallegos con el mismo perfil, a pocos kilómetros, votan tan distinto?',
        resumen=(f'Moaña y Sanxenxo tienen casi la misma renta ({N(mo["renta"])} y {N(sx["renta"])} euros por unidad de consumo), la misma edad media ({num(mo["edad"])} y {num(sx["edad"])} años) y el mismo paro. '
                 f'El 23J, PP, Vox y Cs sacaron el {P(mo["der"]["2023_07"])} en Moaña y el {P(sx["der"]["2023_07"])} en Sanxenxo. '
                 f'En las municipales de mayo, el BNG ganó Moaña con el {P(mo["m2023"]["bng"])}; en Sanxenxo, el PP sacó el {P(sx["m2023"]["pp"])}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Seis municipios casi iguales'),
            ('dato', f'En las Rías Baixas hay seis municipios de entre {N(min(p["poblacion"] for p in rr.values()))} y {N(max(p["poblacion"] for p in rr.values()))} habitantes que el INE describe casi igual: Moaña, Cangas y Bueu, en la península do Morrazo, y Sanxenxo, Marín y Poio.'),
            ('dato', f'Sus rentas van de {N(min(p["renta"] for p in rr.values()))} a {N(max(p["renta"] for p in rr.values()))} euros; '
                     f'su edad media, de {num(min(p["edad"] for p in rr.values()))} a {num(max(p["edad"] for p in rr.values()))} años; el paro de 2021, del {P(min(p["paro"] for p in rr.values()))} al {P(max(p["paro"] for p in rr.values()))}.'),
            ('dato', f'Con ese perfil, el modelo de esta serie les asigna a todos un voto a la derecha parecido, entre el {P(min(p["previsto"] for p in rr.values()))} y el {P(max(p["previsto"] for p in rr.values()))}. '
                     f'El resultado real va del {P(cg["der"]["2023_07"])} de Cangas al {P(sx["der"]["2023_07"])} de Sanxenxo.'),
            ('sub', 'El Morrazo frente a la otra orilla'),
            ('dato', f'Moaña y Cangas, en la comarca do Morrazo, votan a la derecha unos 6 puntos menos de lo previsto ({S(mo["diferencia"])} y {S(cg["diferencia"])}). '
                     f'Sanxenxo, Marín y Poio votan por encima ({S(sx["diferencia"])}, {S(ma["diferencia"])} y {S(po["diferencia"])}). Bueu, también en el Morrazo, queda en medio ({S(bu["diferencia"])}).'),
            ('dato', f'El PP ganó las generales en los seis. La diferencia está en cuánto: {P(mo["pp"]["2023_07"])} en Moaña y {P(cg["pp"]["2023_07"])} en Cangas, frente al {P(sx["pp"]["2023_07"])} en Sanxenxo y el {P(po["pp"]["2023_07"])} en Poio.'),
            ('sub', 'El BNG marca la diferencia'),
            ('dato', f'El BNG sacó el 23J el {P(mo["bng"]["2023_07"])} en Moaña y el {P(cg["bng"]["2023_07"])} en Cangas, frente al {P(sx["bng"]["2023_07"])} en Sanxenxo y el {P(ma["bng"]["2023_07"])} en Marín. En el conjunto de la provincia de Pontevedra, el {P(C["ria"]["pontevedra_bng"])}.'),
            ('dato', f'En las municipales la distancia se agranda. El BNG ganó Moaña ({P(mo["m2023"]["bng"])}) y Bueu ({P(bu["m2023"]["bng"])}); en Cangas, ganó el PP ({P(cg["m2023"]["pp"])}) y el BNG sacó el {P(cg["m2023"]["bng"])}. '
                     f'En Sanxenxo y Marín, el PP pasó del 55 % ({P(sx["m2023"]["pp"])} y {P(ma["m2023"]["pp"])}).'),
            ('sub', 'Una distancia de veinte años'),
            ('dato', f'En 2004, la derecha sacaba el {P(mo["der"]["2004_03"])} en Moaña y el {P(sx["der"]["2004_03"])} en Sanxenxo: ya votaban distinto. En 2023, la distancia era de {num(sx["der"]["2023_07"] - mo["der"]["2023_07"])} puntos. '
                     f'El BNG llegó a sacar el {P(mo["bng"]["2004_03"])} en Moaña en las generales de 2004, cayó al {P(mo["bng"]["2016_06"])} en 2016 y volvió a subir hasta el {P(mo["bng"]["2023_07"])}.'),
        ],
        no_sabemos=['Por qué. La tradición marinera y sindical del Morrazo y el peso histórico del nacionalismo en sus ayuntamientos son hipótesis frecuentes en la prensa gallega; esta pieza no las ha contrastado con dos fuentes independientes.'],
        tabla=dict(caption='Perfil y voto en seis municipios de las Rías Baixas, 23J de 2023 (%, salvo renta en euros y edad en años)',
                   cabecera=['Municipio', 'Renta', 'Edad', 'Paro', 'Derecha', 'Previsto', 'PP', 'BNG', 'BNG municipales'],
                   filas=[[p['municipio'], N(p['renta']), num(p['edad']), num(p['paro']), num(p['der']['2023_07']), num(p['previsto']), num(p['pp']['2023_07']),
                           num(p['bng']['2023_07']), num(p['m2023']['bng'])] for p in sorted(C['ria']['municipios'], key=lambda p: p['der']['2023_07'])]),
        grafico=(barras_previsto([{'municipio': p['municipio'], 'real': p['der']['2023_07'], 'previsto': p['previsto']} for p in sorted(C['ria']['municipios'], key=lambda p: p['der']['2023_07'])],
                                 'Voto a PP, Vox y Cs real y previsto en el Morrazo y la ría de Pontevedra', 'Moaña'),
                 'Voto a PP, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno) en seis municipios de las Rías Baixas, 23J de 2023.'),
        compara='Moaña, Cangas y Bueu (comarca do Morrazo) frente a Sanxenxo, Marín y Poio, con perfiles casi idénticos según el INE.',
        limites='«Derecha» suma PP, Vox y Cs. Los municipios gallegos son extensos y se organizan en parroquias; el promedio municipal oculta diferencias internas. El modelo no es una explicación.',
        csv='morrazo-sanxenxo.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Moaña', 'Cangas', 'Sanxenxo', 'Marín'],
        faq=None,
    ))

    # ------------------------------------------------------------------ gemelos: Arahal y Marchena
    cc = {x['municipio']: x for x in C['campina']['municipios']}
    ah, mc, os_ = cc['Arahal'], cc['Marchena'], cc['Osuna']
    sv = C['campina']['sevilla_der']
    out.append(dict(
        slug='arahal-marchena', serie='gemelos', fecha_datos='2004-2023', revisado='2026-10-07',
        titulo=f'Arahal y Marchena, a {num(C["campina"]["km_arahal_marchena"])} kilómetros y con la misma renta: {N(mc["der"]["2023_07"] - ah["der"]["2023_07"])} puntos de distancia en el voto a la derecha',
        pregunta='¿Por qué dos pueblos casi idénticos de la campiña sevillana votan tan distinto?',
        resumen=(f'Arahal y Marchena tienen casi la misma población ({N(ah["poblacion"])} y {N(mc["poblacion"])} habitantes), la misma renta ({N(ah["renta"])} y {N(mc["renta"])} euros) y un paro parecido. '
                 f'El 23J, PP, Vox y Cs sacaron el {P(ah["der"]["2023_07"])} en Arahal y el {P(mc["der"]["2023_07"])} en Marchena. '
                 f'En las municipales de mayo de 2023, Arahal eligió una lista de Izquierda Unida ({P(ah["m2023_lista_pct"])}); Marchena, al PSOE ({P(mc["m2023_lista_pct"])}).'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Gemelos de la campiña'),
            ('dato', f'Arahal y Marchena están a {num(C["campina"]["km_arahal_marchena"])} kilómetros, en la campiña de Sevilla. Por población, renta, edad y paro se parecen mucho: '
                     f'{N(ah["renta"])} y {N(mc["renta"])} euros de renta por unidad de consumo, {num(ah["edad"])} y {num(mc["edad"])} años de edad media, un paro del {P(ah["paro"])} y del {P(mc["paro"])} en 2021.'),
            ('dato', f'El modelo de esta serie les asigna casi el mismo voto a la derecha: {P(ah["previsto"])} y {P(mc["previsto"])}. Arahal votó {D(ah["diferencia"])} puntos menos; Marchena, {D(mc["diferencia"])} puntos más.'),
            ('sub', 'Dos caminos desde 2004'),
            ('dato', f'En 2004, el PSOE sacaba el {P(ah["psoe"]["2004_03"])} en Arahal y el {P(mc["psoe"]["2004_03"])} en Marchena. La derecha, el {P(ah["der"]["2004_03"])} y el {P(mc["der"]["2004_03"])}.'),
            ('dato', f'Desde entonces la derecha creció en los dos, como en toda la provincia (del {P(sv["2004_03"])} al {P(sv["2023_07"])}), pero más en Marchena: hasta el {P(mc["der"]["2023_07"])}, frente al {P(ah["der"]["2023_07"])} de Arahal. '
                     f'La distancia pasó de {num(mc["der"]["2004_03"] - ah["der"]["2004_03"])} puntos en 2004 a {num(mc["der"]["2023_07"] - ah["der"]["2023_07"])} en 2023.'),
            ('dato', f'El PSOE ganó en los dos el 23J: {P(ah["psoe"]["2023_07"])} en Arahal y {P(mc["psoe"]["2023_07"])} en Marchena. Vox sacó el {P(ah["vox"]["2023_07"])} y el {P(mc["vox"]["2023_07"])}.'),
            ('sub', 'En el ayuntamiento, otro mapa'),
            ('dato', f'En las municipales de mayo de 2023, la lista más votada en Arahal fue la de Izquierda Unida, «{lista(ah["m2023_lista"])}», con el {P(ah["m2023_lista_pct"])}. '
                     f'En Marchena ganó el PSOE con el {P(mc["m2023_lista_pct"])} y el PP sacó el {P(mc["m2023"]["pp"])}.'),
            ('sub', 'Un tercer pueblo'),
            ('dato', f'Osuna, con {N(os_["poblacion"])} habitantes y {N(os_["renta"])} euros de renta, completa el trío: su voto a la derecha ({P(os_["der"]["2023_07"])}) está más cerca de Arahal que de Marchena. '
                     f'Más allá, Écija ({P(cc["Écija"]["der"]["2023_07"])}, ganó el PP) y Paradas ({P(cc["Paradas"]["der"]["2023_07"])}) muestran que en la campiña el perfil es casi uniforme y el voto no.'),
        ],
        no_sabemos=['Por qué. La historia jornalera de la campiña, la implantación de Izquierda Unida en algunos ayuntamientos y la duración de las alcaldías son hipótesis que esta pieza no ha contrastado con dos fuentes independientes.'],
        tabla=dict(caption='Perfil y voto a PP + Vox + Cs real y previsto en nueve municipios de la campiña de Sevilla, 23J de 2023 (%, salvo renta en euros)',
                   cabecera=['Municipio', 'Habitantes', 'Renta', 'Paro', 'Derecha', 'Previsto', 'Diferencia', 'PSOE', 'Gana'],
                   filas=[[p['municipio'], N(p['poblacion']), N(p['renta']), num(p['paro']), num(p['der']['2023_07']), num(p['previsto']), S(p['diferencia']),
                           num(p['psoe']['2023_07']), p['gana']] for p in sorted(C['campina']['municipios'], key=lambda p: p['der']['2023_07'])]),
        grafico=(lineas([('Marchena', mc['der'], 'var(--pp)', True), ('Arahal', ah['der'], 'var(--accent)', True), ('Prov. Sevilla', sv, 'var(--muted)', False)],
                        CONG, 'PP + Vox + Cs en Arahal, Marchena y la provincia de Sevilla', 10, 60),
                 'PP, Vox y Cs juntos en Arahal, Marchena y el conjunto de la provincia de Sevilla, generales de 2004 a 2023 (% del voto válido).'),
        compara='Arahal y Marchena, dos municipios casi iguales de la campiña sevillana según el INE, y otros siete municipios de la campiña.',
        limites='«Gemelos» según los indicadores del INE; pueden diferir en otros que los datos no recogen. «Derecha» suma PP, Vox y Cs. Distancia entre centroides de los términos municipales.',
        csv='arahal-marchena.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Arahal', 'Marchena', 'Osuna'],
        faq=None,
    ))

    # ------------------------------------------------------------------ el municipio que cambió: Manilva
    mn = C['manilva']
    mv, cs_, es_ = mn['municipios']
    mz, md = mn['malaga_izq'], mn['malaga_der']
    out.append(dict(
        slug='manilva', serie='el-municipio-que-cambio', fecha_datos='2004-2023', revisado='2026-10-07',
        titulo=f'Manilva, el municipio de España donde más ha caído la izquierda en veinte años respecto a su provincia: del {P(mv["izq"]["2004_03"])} al {P(mv["izq"]["2023_07"])}',
        pregunta='¿Qué municipios de la Costa del Sol han cambiado su voto mucho más que su provincia?',
        resumen=(f'En 2004, el PSOE y el espacio de IU sacaban el {P(mv["izq"]["2004_03"])} del voto en Manilva (Málaga). En 2023, el {P(mv["izq"]["2023_07"])}: '
                 f'{D(mv["izq"]["2023_07"] - mv["izq"]["2004_03"])} puntos menos, cuando en el conjunto de la provincia la caída fue de {D(mz["2023_07"] - mz["2004_03"])}. '
                 f'Es la mayor diferencia de España entre los municipios de más de 10.000 habitantes. En noviembre de 2019, Vox fue allí la lista más votada.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'La medida'),
            ('dato', 'Esta serie no mide cuánto cambia un municipio, sino cuánto cambia más que su provincia. Así se separa la ola general, que afecta a todos, de lo que es propio de cada lugar.'),
            ('dato', f'Entre 2004 y 2023, la izquierda estatal (el PSOE más el espacio de IU, Podemos y Sumar) perdió {D(mv["izq"]["2023_07"] - mv["izq"]["2004_03"])} puntos en Manilva y {D(mz["2023_07"] - mz["2004_03"])} en el conjunto de la provincia de Málaga. '
                     f'La diferencia, {D(mn["top"][0]["cambio_relativo"])} puntos, es la mayor de los {N(mn["n_10k"])} municipios españoles de más de 10.000 habitantes. '
                     f'Le sigue Los Palacios y Villafranca ({S(mn["top"][1]["cambio_relativo"])}), que el Atlas ya contó en esta serie.'),
            ('sub', 'Tres ganadores en ocho elecciones'),
            ('dato', f'Manilva no ha tenido un ganador estable. El PSOE ganó en 2004, 2015 y abril de 2019; el PP, en 2008, 2011, 2016 y 2023. En noviembre de 2019, la lista más votada fue Vox, con el {P(mv["vox"]["2019_11"])}.'),
            ('dato', f'Vox ganó aquellas elecciones en {mn["vox_gana_2019_11_n"]} municipios de España, {mn["vox_gana_2019_11_malaga"]} de ellos en la provincia de Málaga, entre ellos Estepona, su vecina. En 2023 bajó en Manilva al {P(mv["vox"]["2023_07"])} y el PP ganó con el {P(mv["pp"]["2023_07"])}.'),
            ('dato', f'La derecha (PP, Vox y Cs) pasó del {P(mv["der"]["2004_03"])} en 2004 al {P(mv["der"]["2023_07"])} en 2023. En la provincia, del {P(md["2004_03"])} al {P(md["2023_07"])}.'),
            ('sub', 'Sus vecinas'),
            ('dato', f'Casares, su vecino, siguió un camino parecido aunque partía de más arriba: la izquierda pasó del {P(cs_["izq"]["2004_03"])} al {P(cs_["izq"]["2023_07"])}. '
                     f'En Estepona, del {P(es_["izq"]["2004_03"])} al {P(es_["izq"]["2023_07"])}.'),
            ('dato', f'Manilva es también el municipio de la provincia de Málaga con más población extranjera entre los de más de 10.000 habitantes: el {P(mn["extranjeros"])} de sus vecinos en el padrón, según el INE. En las generales solo votan los españoles; los ciudadanos de la Unión Europea pueden votar en las municipales si se inscriben.'),
            ('sub', 'El voto local'),
            ('dato', f'En las municipales de mayo de 2023 la lista más votada fue una candidatura local, «{lista(mv["m2023_lista"])}», con el {P(mv["m2023_lista_pct"])}. El PP sacó el {P(mv["m2023"]["pp"])} y el PSOE, el {P(mv["m2023"]["psoe"])}.'),
        ],
        no_sabemos=['Por qué. El crecimiento urbanístico de la costa occidental de Málaga y el cambio de población son las hipótesis más citadas; esta pieza no tiene el padrón por procedencia ni dos fuentes que relacionen esos cambios con el voto.'],
        tabla=dict(caption='Los diez municipios de más de 10.000 habitantes donde más cayó la izquierda estatal respecto a su provincia, 2004-2023 (puntos)',
                   cabecera=['Municipio', 'Provincia', 'Izquierda 2004', 'Izquierda 2023', 'Cambio', 'Cambio de la provincia', 'Diferencia'],
                   filas=[[r['municipio'], r['provincia'], num(r['izq_2004']), num(r['izq_2023']), S(r['cambio']), S(r['cambio_provincia']), S(r['cambio_relativo'])] for r in mn['top']]),
        grafico=(lineas([('Manilva', mv['izq'], 'var(--accent)', True), ('Prov. Málaga', mz, 'var(--muted)', False)],
                        CONG, 'Izquierda estatal en Manilva y en la provincia de Málaga', 20, 70),
                 'PSOE más el espacio de IU, Podemos y Sumar en Manilva y en el conjunto de la provincia de Málaga, generales de 2004 a 2023 (% del voto válido).'),
        compara=f'Los {N(mn["n_10k"])} municipios españoles de más de 10.000 habitantes, por el cambio de la izquierda estatal entre 2004 y 2023 menos el cambio de su provincia.',
        limites='«Izquierda» suma el PSOE y el espacio de IU, Podemos y Sumar (con Compromís y Más País). Los datos agregados no dicen quién cambió su voto: un municipio que crece cambia también de votantes.',
        csv='manilva.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Manilva', 'Casares', 'Estepona'],
        faq=None,
    ))

    # ------------------------------------------------------------------ contra su provincia: Alcoi
    ac = C['alcoi']
    al = ac['alcoi']
    a20 = {x['municipio']: x for x in ac['alicante_20k']}
    out.append(dict(
        slug='alcoi', serie='contra-su-provincia', fecha_datos='2004-2023', revisado='2026-10-07',
        titulo=f'Alcoi, la ciudad que vota a la izquierda en la provincia de Alicante: el PSOE le sacó {num(al["psoe"]["2023_07"] - al["pp"]["2023_07"])} puntos al PP',
        pregunta='¿Cuánto se aparta Alcoi del voto de su provincia, y desde cuándo?',
        resumen=(f'El 23J, el PSOE ganó en Alcoi con el {P(al["psoe"]["2023_07"])}, frente al {P(al["pp"]["2023_07"])} del PP. En el conjunto de la provincia de Alicante ganó el PP, con {D(ac["margen_provincia"])} puntos de ventaja. '
                 f'Ningún municipio alicantino de más de 20.000 habitantes vota tan a la izquierda. La izquierda estatal sacó allí el {P(al["izq"]["2023_07"])}, más que en 2004 ({P(al["izq"]["2004_03"])}), mientras en la provincia bajaba.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'La excepción de la provincia'),
            ('dato', f'De los {ac["n_20k"]} municipios alicantinos de más de 20.000 habitantes, el PSOE ganó el 23J en {ac["n_20k_psoe"]}. En ninguno con tanta ventaja como en Alcoi: {num(a20["Alcoi/Alcoy"]["margen"])} puntos sobre el PP. '
                     f'Le siguen, de lejos, Elda ({S(a20["Elda"]["margen"])}) y Dénia ({S(a20["Dénia"]["margen"])}).'),
            ('dato', f'La izquierda estatal (PSOE más el espacio de Sumar, que en la Comunitat Valenciana incluye a Compromís) sacó en Alcoi el {P(al["izq"]["2023_07"])}. En la provincia, el {P(ac["alicante_izq"]["2023_07"])}.'),
            ('sub', 'Más que lo que predice su perfil'),
            ('dato', f'Con {N(al["poblacion"])} habitantes, una renta de {N(al["renta"])} euros y un paro del {P(al["paro"])} en 2021, el modelo de esta serie predice para Alcoi un {P(al["previsto"])} de voto a PP, Vox y Cs. '
                     f'Sacaron el {P(al["der"]["2023_07"])}: {D(al["diferencia"])} puntos menos, la {ac["rango_residuo"]}.ª mayor diferencia a la baja de España entre los municipios de más de 10.000 habitantes.'),
            ('sub', 'Veinte años a contracorriente'),
            ('dato', f'En 2004, la izquierda estatal sacaba el {P(al["izq"]["2004_03"])} en Alcoi y el {P(ac["alicante_izq"]["2004_03"])} en la provincia: una distancia de {num(al["izq"]["2004_03"] - ac["alicante_izq"]["2004_03"])} puntos. '
                     f'En 2023, la distancia era de {num(al["izq"]["2023_07"] - ac["alicante_izq"]["2023_07"])}.'),
            ('dato', f'En 2015 y 2016, la candidatura del espacio de Podemos y Compromís fue la más votada en Alcoi, con el {P(al["sumar"]["2015_12"])} y el {P(al["sumar"]["2016_06"])}. El PP solo ganó en 2011, con el {P(al["pp"]["2011_11"])}.'),
            ('patrón', f'La derecha, en cambio, se ha movido poco: entre el {P(min(al["der"].values()))} y el {P(max(al["der"].values()))} en las ocho generales. Lo que ha cambiado es el reparto dentro de la izquierda.'),
            ('sub', 'En el ayuntamiento'),
            ('dato', f'En las municipales de mayo de 2023 el PSOE fue la lista más votada con el {P(al["m2023_lista_pct"])}, casi empatado con el PP ({P(al["m2023"]["pp"])}). Compromís y el resto del espacio de Sumar sacaron el {P(al["m2023"]["sumar"])}.'),
        ],
        no_sabemos=['Por qué. Alcoi tiene una larga historia industrial y obrera (ver «Sobre el terreno»), y es la explicación que más se repite; esta pieza no ha encontrado dos fuentes independientes que la relacionen con el voto actual.'],
        tabla=dict(caption='Voto en las generales en Alcoi y en el conjunto de la provincia de Alicante, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'PSOE Alcoi', 'PP Alcoi', 'Sumar y afines Alcoi', 'Izquierda Alcoi', 'Izquierda provincia', 'Derecha Alcoi', 'Derecha provincia'],
                   filas=[[ANYO[e], num(al['psoe'][e]), num(al['pp'][e]), num(al['sumar'][e]), num(al['izq'][e]), num(ac['alicante_izq'][e]), num(al['der'][e]), num(ac['alicante_der'][e])] for e in CONG]),
        grafico=(lineas([('Izq. Alcoi', al['izq'], 'var(--psoe)', True), ('Izq. provincia', ac['alicante_izq'], 'var(--psoe)', False),
                         ('Der. Alcoi', al['der'], 'var(--pp)', True), ('Der. provincia', ac['alicante_der'], 'var(--pp)', False)],
                        CONG, 'Izquierda y derecha en Alcoi y en la provincia de Alicante', 30, 60),
                 'Izquierda estatal (PSOE más el espacio de Sumar) y derecha (PP, Vox y Cs) en Alcoi (línea continua) y en el conjunto de la provincia de Alicante (discontinua), generales de 2004 a 2023 (% del voto válido).'),
        compara=f'Alcoi frente a la provincia de Alicante y a sus {ac["n_20k"]} municipios de más de 20.000 habitantes, y frente al modelo municipal de esta serie.',
        limites='«Izquierda» suma el PSOE y el espacio de IU, Podemos, Compromís y Sumar; «derecha», PP, Vox y Cs. El modelo no es una explicación.',
        csv='alcoi.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Alcoi'],
        faq=None,
    ))

    # ------------------------------------------------------------------ ciudad y entorno: capitales en las municipales
    km_ = C['capitales_mun']
    kc = {x['capital']: x for x in km_['capitales']}
    gm = max(km_['capitales'], key=lambda f: f['g23_capital'] - f['m23_capital'])
    out.append(dict(
        slug='capitales-municipales', serie='ciudad-y-entorno', fecha_datos='2015-2023', revisado='2026-10-07',
        titulo=f'{km_["n_menos_m23"]} de las 50 capitales votan menos que el resto de su provincia para elegir alcalde; Zamora y Soria, más de 14 puntos menos',
        pregunta='¿Dónde se queda la ciudad en casa en las elecciones municipales mientras su provincia vota?',
        resumen=(f'En las municipales de mayo de 2023, Zamora votó el {P(kc["Zamora"]["m23_capital"])} y el resto de su provincia, el {P(kc["Zamora"]["m23_resto"])}. Soria, el {P(kc["Soria"]["m23_capital"])} frente al {P(kc["Soria"]["m23_resto"])}. '
                 f'En {km_["n_menos_m23"]} de las 50 capitales de provincia la participación municipal fue menor que en el resto de la provincia, y en {km_["n_menos_10_m23"]} la diferencia pasó de 10 puntos. '
                 f'En las generales de julio, ninguna capital se quedó a 10 puntos de su provincia.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'La ciudad que no va a votar'),
            ('dato', f'El 28 de mayo de 2023 se eligieron todos los ayuntamientos de España. En {km_["n_menos_m23"]} de las 50 capitales de provincia se votó menos que en el resto de los municipios de su provincia. '
                     f'Las mayores distancias, en Zamora ({S(kc["Zamora"]["m23_dif"])} puntos), Soria ({S(kc["Soria"]["m23_dif"])}), Cuenca ({S(kc["Cuenca"]["m23_dif"])}), Badajoz ({S(kc["Badajoz"]["m23_dif"])}) y, empatadas, Ávila y Salamanca ({S(kc["Salamanca"]["m23_dif"])}).'),
            ('dato', f'Dos meses después, en las generales del 23 de julio, la distancia casi desapareció. Zamora votó el {P(kc["Zamora"]["g23_capital"])} y el resto de su provincia, el {P(kc["Zamora"]["g23_resto"])}: {D(kc["Zamora"]["g23_dif"])} puntos de diferencia. '
                     f'En Soria, {D(kc["Soria"]["g23_dif"])}. En {km_["n_menos_g23"]} capitales se votó menos que en su provincia, pero en ninguna a más de 10 puntos.'),
            ('patrón', 'En buena parte de España, lo que moviliza en las municipales es el pueblo, no la ciudad. Las capitales votan para el Congreso casi como su provincia y se quedan muy atrás cuando lo que se elige es el alcalde.'),
            ('sub', 'No es un año aislado'),
            ('dato', f'El patrón se repite en las municipales anteriores. En 2019, {km_["n_menos_m19"]} capitales votaron menos que su provincia; en 2015, {km_["n_menos_m15"]}. '
                     f'Zamora estuvo {D(kc["Zamora"]["m19_dif"])} puntos por debajo en 2019 y {D(kc["Zamora"]["m15_dif"])} en 2015; Badajoz, {D(kc["Badajoz"]["m19_dif"])} y {D(kc["Badajoz"]["m15_dif"])}.'),
            ('dato', f'Las 50 capitales votaron menos en las municipales de mayo que en las generales de julio. La diferencia más grande, en {gm["capital"]}: {P(gm["m23_capital"])} frente a {P(gm["g23_capital"])}.'),
            ('sub', 'Las excepciones'),
            ('dato', f'En cinco capitales se votó más que en el resto de su provincia. Barcelona ({S(kc["Barcelona"]["m23_dif"])}) y Cádiz ({S(kc["Cádiz"]["m23_dif"])}) son los casos más claros; '
                     f'València, Murcia y Toledo votaron más o menos lo mismo que su entorno ({S(kc["València"]["m23_dif"])}, {S(kc["Murcia"]["m23_dif"])} y {S(kc["Toledo"]["m23_dif"])}).'),
            ('dato', 'El Atlas ya mostró el otro lado de esta historia en la serie «Quién no vota»: los pueblos de menos de 2.000 habitantes son los únicos que votan más para elegir alcalde que para elegir al Gobierno.'),
        ],
        no_sabemos=['Por qué. La competencia entre listas, la cercanía a los candidatos en los pueblos y el peso de los vecinos inscritos que no viven allí son hipótesis que esta pieza no ha contrastado con dos fuentes.'],
        tabla=dict(caption='Participación en las municipales de mayo de 2023 y en las generales de julio en las 50 capitales de provincia y en el resto de su provincia (%)',
                   cabecera=['Capital', 'Municipales capital', 'Municipales resto', 'Diferencia', 'Generales capital', 'Generales resto', 'Diferencia '],
                   filas=[[f['capital'], num(f['m23_capital']), num(f['m23_resto']), S(f['m23_dif']), num(f['g23_capital']), num(f['g23_resto']), S(f['g23_dif'])] for f in km_['capitales']]),
        grafico=(divergente([{'capital': f['capital'], 'dif': f['m23_dif']} for f in km_['capitales'][:12] + km_['capitales'][-5:]], 'dif', 'capital',
                            'Participación de la capital menos la del resto de su provincia, municipales de 2023'),
                 'Diferencia entre la participación de la capital y la del resto de su provincia en las municipales de mayo de 2023 (puntos): las doce capitales con más distancia a la baja y las cinco que votaron más que su entorno.'),
        compara='Cada una de las 50 capitales de provincia frente al resto de los municipios de su provincia, en las municipales de 2015, 2019 y 2023 y en las generales de 2023. Ceuta y Melilla quedan fuera porque la ciudad es toda la circunscripción.',
        limites='Participación = votantes / censo. El censo de las municipales incluye a los residentes de la Unión Europea inscritos, que votan menos; el de las generales, solo a los españoles residentes. La comparación capital-provincia no se ve afectada por ese cambio, pero la comparación municipales-generales sí, algo.',
        csv='capitales-municipales.csv', fuentes=['interior'], lugares=['Zamora', 'Soria', 'Cuenca', 'Badajoz', 'Ávila', 'Salamanca'],
        faq=None,
    ))

    # ------------------------------------------------------------------ voto doble: europeas 2024
    eu = C['europeas']
    dr, dl = eu['deciles_renta'], eu['deciles_renta_pocos_extranjeros']
    mc_ = eu['mayores_caidas']
    ac_ = next(r for r in mc_ if r['municipio'] == 'Arcos de la Frontera')
    out.append(dict(
        slug='europeas-2024', serie='voto-doble', fecha_datos='julio de 2023 y junio de 2024', revisado='2026-10-07',
        titulo=f'En las europeas de 2024 la brecha de participación entre las zonas más ricas y las más pobres pasó de {N(eu["brecha_g2023"])} a {N(eu["brecha_e2024"])} puntos',
        pregunta='¿Quién deja de votar cuando la elección parece lejana?',
        resumen=(f'En las europeas del 9 de junio de 2024 votó el {P(eu["total_e2024"])} del censo de residentes, frente al {P(eu["total_g2023"])} de las generales de 2023. La caída no fue igual en todas partes. '
                 f'En las secciones censales con más renta, la participación bajó de {P(dr[-1]["g2023"])} a {P(dr[-1]["e2024"])}; en las de menos renta, de {P(dr[0]["g2023"])} a {P(dr[0]["e2024"])}. '
                 f'La distancia entre unas y otras pasó de {num(eu["brecha_g2023"])} a {num(eu["brecha_e2024"])} puntos.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Menos de un año, veinte puntos menos'),
            ('dato', f'Entre las generales de julio de 2023 y las europeas de junio de 2024 pasaron menos de once meses. La participación sobre el censo de residentes en España cayó del {P(eu["total_g2023"])} al {P(eu["total_e2024"])}.'),
            ('dato', f'Esta pieza ordena las {N(eu["n_secciones"])} secciones censales de España por su renta media y las agrupa en diez tramos iguales. En el tramo más rico, la participación cayó {D(dr[-1]["e2024"] - dr[-1]["g2023"])} puntos; en el más pobre, {D(dr[0]["e2024"] - dr[0]["g2023"])}.'),
            ('patrón', f'En las dos elecciones la participación sube tramo a tramo con la renta, pero en las europeas la diferencia se agranda. En las generales, el tramo más rico votó {num(eu["brecha_g2023"])} puntos más que el más pobre; en las europeas, {num(eu["brecha_e2024"])}.'),
            ('sub', 'No es un efecto del censo'),
            ('dato', f'El censo de las europeas incluye a los ciudadanos de otros países de la Unión que se inscriben para votar, y en algunas zonas son muchos. Para descartar que eso explique la brecha, la pieza repite el cálculo solo con las {N(eu["n_secciones_pocos_extranjeros"])} secciones donde los extranjeros son menos del 5 % de la población. '
                     f'El resultado es el mismo: la distancia entre el tramo más rico y el más pobre pasa de {num(eu["brecha_g2023_pe"])} puntos en las generales a {num(eu["brecha_e2024_pe"])} en las europeas.'),
            ('sub', 'Dónde cayó más'),
            ('dato', f'Entre los {eu["n_20k"]} municipios de más de 20.000 habitantes, las mayores caídas están en Andalucía: {eu["andalucia_top10"]} de los diez primeros. '
                     + ', '.join(f'{r["municipio"]} ({S(r["caida"])})' for r in mc_[:5]) + ' puntos.'),
            ('dato', f'En Arcos de la Frontera, donde casi no hay extranjeros ({P(ac_["extranjeros"])} de la población), votó el {P(ac_["g2023"])} en julio de 2023 y el {P(ac_["e2024"])} en junio de 2024.'),
            ('dato', 'Donde menos cayó, entre los municipios de más de 20.000 habitantes: ' +
                     ', '.join(f'{r["municipio"]} ({S(r["caida"])})' for r in eu['menores_caidas'][:4]) + '.'),
            ('sub', 'La comparación con 2019'),
            ('dato', f'En las europeas de 2019 votó el {P(eu["total_e2019"])}, mucho más que en las de 2024, pero no son comparables: se celebraron el mismo día que las municipales, el 26 de mayo de 2019.'),
        ],
        no_sabemos=['Por qué la brecha de renta crece en unas elecciones que movilizan menos. Esta pieza no ha contrastado ninguna explicación con dos fuentes independientes.',
                    'Si influyen la fecha de la elección o el interés por la campaña: son hipótesis sin comprobar.'],
        tabla=dict(caption='Participación por tramos de renta de las secciones censales en las generales de 2023 y las europeas de 2024 (%)',
                   cabecera=['Tramo de renta (de menos a más)', 'Renta desde (€)', 'Generales 2023', 'Europeas 2024', 'Caída'],
                   filas=[[str(x['decil']), N(x['min']), num(x['g2023']), num(x['e2024']), S(round(x['e2024'] - x['g2023'], 1))] for x in dr]),
        grafico=(lineas([('Generales 2023', {str(x['decil']): x['g2023'] for x in dr}, 'var(--accent)', True),
                         ('Europeas 2024', {str(x['decil']): x['e2024'] for x in dr}, 'var(--accent2)', True)],
                        [str(x['decil']) for x in dr], 'Participación por tramo de renta, generales de 2023 y europeas de 2024', 30, 80,
                        etiquetas={str(x['decil']): ('menos renta' if x['decil'] == 1 else 'más renta' if x['decil'] == 10 else str(x['decil'])) for x in dr}),
                 'Participación en las generales de julio de 2023 y en las europeas de junio de 2024 según la renta de la sección censal, de los tramos con menos renta (1) a los de más (10).'),
        compara=f'Las {N(eu["n_secciones"])} secciones censales de España con datos de las dos elecciones, en diez tramos de renta, y los {eu["n_20k"]} municipios de más de 20.000 habitantes.',
        limites='Participación sobre el censo de residentes en España (sin CERA). El censo de las europeas incluye a ciudadanos de la Unión inscritos; por eso se repite el cálculo en las secciones con pocos extranjeros. Correlación ecológica: no dice qué personas dejaron de votar.',
        csv='europeas-2024.csv', fuentes=['interior', 'europeas', 'ine_adrh'], lugares=[r['municipio'] for r in mc_[:3]],
        faq=None,
    ))

    for p in out:
        p['cuerpo'] = [c for c in p['cuerpo'] if c]
    return [terreno(p) for p in out]
