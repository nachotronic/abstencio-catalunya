"""Textos de las piezas del Atlas. Cada cifra sale de cifras.json (C); ninguna está escrita a mano.

Cada afirmación se marca en el cuerpo con su tipo:
  dato        resultado verificable (fórmula sobre una fuente)
  patrón      relación descriptiva, sin causa
  hipótesis   explicación posible que todavía no tiene dos fuentes independientes
La sección «Lo que no sabemos» recoge las hipótesis; nunca se presentan como causa.
Los elementos ('sub', texto) del cuerpo son ladillos: no contienen afirmaciones.

`revisado` es la fecha (AAAA-MM-DD) en que Nacho comprueba la muestra manual y firma la revisión de datos y texto.
Mientras esté vacío, la página se genera con «Revisión pendiente», con noindex y fuera del sitemap.
"""
from terreno import terreno
from graficos import yl, num, lineas, barras_previsto, divergente, barras_agrupadas, margenes, ANYO

SERIES = {
    'excepciones': ('Las excepciones', 'Lugares que votan muy distinto de lo que predicen su renta, su edad, su paro y su tamaño.'),
    'fronteras': ('Fronteras que votan distinto', 'Municipios vecinos, separados por pocos kilómetros y muchos puntos de voto.'),
    'gemelos': ('Gemelos electorales', 'Municipios casi idénticos en sus datos que votan de forma opuesta.'),
    'contra-su-provincia': ('Contra su provincia', 'Lugares donde gana quien pierde en su provincia, y al revés.'),
    'ciudad-y-entorno': ('Ciudad, corona e interior', 'La distancia entre la ciudad y el territorio que la rodea.'),
    'voto-doble': ('Voto doble', 'El mismo electorado vota distinto según qué se elige.'),
    'bisagras': ('Bisagras', 'Votos y lugares que deciden algo mucho mayor que su peso.'),
    'el-municipio-que-cambio': ('El municipio que cambió', 'Lugares que han dado la vuelta a su voto en veinte años.'),
    'quien-no-vota': ('Quién no vota', 'Quién se queda fuera de las urnas, y por qué grupos de razones.'),
}

CONG = ['2004_03', '2008_03', '2011_11', '2015_12', '2016_06', '2019_04', '2019_11', '2023_07']
P = lambda x: num(x) + ' %'          # 43.2 -> '43,2 %'
N = lambda x: num(x, 0)              # 1340 -> '1.340'
D = lambda x: num(abs(x))            # diferencia en puntos, sin signo
S = lambda x: ('+' if x > 0 else '−' if x < 0 else '') + num(abs(x))   # con signo


def art(partido, prep=''):
    """Artículo delante de un partido: 'el PP', 'a la lista de Teruel Existe'; con prep='a ', 'al PSOE'."""
    if partido in ('PP', 'PSOE', 'PSC', 'PNV', 'BNG'):
        return ('al ' if prep == 'a ' else 'el ') + partido
    if partido in ('Vox', 'Sumar', 'Junts', 'ERC', 'EH Bildu', 'CC', 'UPN'):
        return prep + partido
    return prep + 'la lista de ' + partido


def piezas(C):
    out = []

    # ------------------------------------------------------------------ bisagras: Cádiz y Madrid el 29N
    z = C['escanos_29n']
    e23 = C['escanos_2023_con_cera']
    cad, mad = z['11'], z['28']
    out.append(dict(
        slug='cadiz-madrid-29n', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='Si el 29N se votara como en 2023, el escaño que pierde Cádiz sería del PP y el que gana Madrid, del PSOE',
        pregunta='¿Qué habría cambiado en 2023 con el reparto de escaños que se aplica el 29 de noviembre de 2026?',
        resumen=(f'Para las generales del 29 de noviembre de 2026, Madrid elige 38 diputados (uno más) y Cádiz 8 (uno menos). '
                 f'Si se aplica ese reparto a los votos del 23 de julio de 2023, el PP pierde un escaño en Cádiz '
                 f'(de {cad["2023"]["PP"]} a {cad["2026"]["PP"]}) y el PSOE gana uno en Madrid '
                 f'(de {mad["2023"]["PSOE"]} a {mad["2026"]["PSOE"]}). '
                 f'Es un ejercicio aritmético, no una previsión: los votos de 2026 serán otros.'),
        estado='Dato',
        cuerpo=[
            ('dato', 'El Congreso seguirá teniendo 350 diputados el 29 de noviembre, pero uno de ellos cambia de provincia. '
                     'El decreto de convocatoria reparte los escaños según la población de cada circunscripción, y esta vez Madrid sube de 37 a 38 y Cádiz baja de 9 a 8. '
                     'Las otras 50 circunscripciones eligen los mismos diputados que en 2023.'),
            ('dato', 'Un escaño que se mueve parece poca cosa, pero no es neutro: el que sale de una provincia y el que entra en otra no tienen por qué ser del mismo partido. '
                     'Para saber de quién serían, basta con repetir el reparto de 2023 con los escaños nuevos y los mismos votos.'),
            ('sub', 'Cádiz: de una victoria del PP a un empate'),
            ('dato', f'Con 9 escaños, Cádiz eligió en 2023 a {cad["2023"]["PP"]} diputados del PP, {cad["2023"]["PSOE"]} del PSOE, {cad["2023"]["Vox"]} de Vox y {cad["2023"]["Sumar"]} de Sumar. '
                     f'Si esos mismos votos se reparten entre 8, el escaño que desaparece es el último que obtuvo el PP. '
                     f'La provincia pasaría de un {cad["2023"]["PP"]} a {cad["2023"]["PSOE"]} a favor del PP a un empate a {cad["2026"]["PP"]} con el PSOE.'),
            ('sub', 'Madrid: el escaño que el PSOE rozó'),
            ('dato', f'En Madrid ocurre lo contrario. Con 37 escaños, el reparto de 2023 fue PP {mad["2023"]["PP"]}, PSOE {mad["2023"]["PSOE"]}, Sumar {mad["2023"]["Sumar"]} y Vox {mad["2023"]["Vox"]}. '
                     f'El escaño número 38 va a la candidatura con el siguiente cociente más alto, que es el PSOE: pasaría a {mad["2026"]["PSOE"]}.'),
            ('dato', f'No es casualidad aritmética. En 2023, el último escaño de Madrid se lo llevó el PP y al PSOE le faltaron {N(C["madrid"]["faltaban_psoe_con_cera"])} votos para quitárselo. '
                     f'Con un escaño más en juego, ese cociente que se quedó fuera entra.'),
            ('sub', 'El saldo'),
            ('dato', f'Con los votos de 2023 y el reparto de 2026, el PP habría tenido {e23["PP"] - 1} diputados en lugar de {e23["PP"]}, y el PSOE {e23["PSOE"] + 1} en lugar de {e23["PSOE"]}. '
                     f'La distancia entre los dos grandes partidos se reduciría de {e23["PP"] - e23["PSOE"]} a {e23["PP"] - e23["PSOE"] - 2} escaños, '
                     f'y PP y Vox juntos sumarían {e23["PP"] + e23["Vox"] - 1} en vez de {e23["PP"] + e23["Vox"]}.'),
            ('dato', 'Todo esto es una cuenta hecha con votos del pasado. El 29N los votos serán otros, y un cambio pequeño en Madrid o en Cádiz basta para que el escaño que se mueve caiga de otro lado.'),
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
    mg = C['margenes']
    pos_madrid = next(i for i, f in enumerate(mg) if f['provincia'] == 'Madrid') + 1
    out.append(dict(
        slug='madrid-voto-exterior', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='El último escaño de Madrid en 2023 lo decidió el voto desde el extranjero',
        pregunta='¿Cuántos votos separaron el último escaño de Madrid el 23J?',
        resumen=(f'Con los votos emitidos en España, el último escaño de Madrid era del PSOE: al PP le faltaban {N(md["faltaban_pp_sin_cera"])} votos. '
                 f'El voto de los residentes en el extranjero (CERA) dio al PP {N(md["cera_pp"])} votos y al PSOE {N(md["cera_psoe"])}, '
                 f'y el escaño pasó al PP: {md["con_cera"]["PP"]} para el PP y {md["con_cera"]["PSOE"]} para el PSOE. '
                 f'Con todos los votos contados, al PSOE le faltaron {N(md["faltaban_psoe_con_cera"])}.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'El recuento de la noche y el definitivo'),
            ('dato', 'La noche electoral no se cuentan todos los votos. Los de los españoles que viven en el extranjero y están inscritos en el Censo Electoral de Residentes Ausentes (CERA) se suman días después, en el escrutinio general. '
                     'Casi nunca cambian nada. En Madrid, en 2023, cambiaron un diputado.'),
            ('dato', f'Con los votos emitidos en España, Madrid repartía sus 37 escaños así: PP {md["sin_cera"]["PP"]}, PSOE {md["sin_cera"]["PSOE"]}, Sumar {md["sin_cera"]["Sumar"]} y Vox {md["sin_cera"]["Vox"]}. '
                     f'El último escaño era del PSOE, y al PP le faltaban {N(md["faltaban_pp_sin_cera"])} votos para arrebatárselo.'),
            ('sub', 'Lo que llegó desde fuera'),
            ('dato', f'El voto exterior de Madrid sumó {N(md["cera_total_candidaturas"])} votos a candidaturas. El PP recibió {N(md["cera_pp"])}, casi el doble que el PSOE, que recibió {N(md["cera_psoe"])}. '
                     f'Esa ventaja de {N(md["cera_pp"] - md["cera_psoe"])} votos era más que suficiente para cubrir los {N(md["faltaban_pp_sin_cera"])} que le faltaban al PP.'),
            ('dato', f'Con todos los votos contados, el reparto final fue PP {md["con_cera"]["PP"]}, PSOE {md["con_cera"]["PSOE"]}, Sumar {md["con_cera"]["Sumar"]} y Vox {md["con_cera"]["Vox"]}. '
                     f'En el conjunto de España, ese escaño dejó al PP con {C["escanos_2023_con_cera"]["PP"]} diputados y al PSOE con {C["escanos_2023_con_cera"]["PSOE"]}.'),
            ('sub', 'Uno de los márgenes más estrechos del 23J'),
            ('dato', f'Después del escrutinio, la distancia se dio la vuelta: al PSOE le faltaron {N(md["faltaban_psoe_con_cera"])} votos para recuperar el escaño. '
                     f'Es el {["", "primer", "segundo", "tercer", "cuarto", "quinto", "sexto"][pos_madrid]} margen más estrecho de las 52 circunscripciones, en la provincia donde el PP sumó {N(md["votos_pp"])} votos.'),
            ('dato', 'Ese escaño tiene una segunda vida. Para el 29N, Madrid elige 38 diputados en vez de 37, y si se repitieran los votos de 2023, el escaño nuevo sería precisamente el que el PSOE rozó.'),
        ],
        no_sabemos=['Por qué el voto exterior madrileño fue más favorable al PP que el voto emitido en España. Requiere datos del perfil de los residentes en el extranjero que esta pieza no tiene.'],
        tabla=dict(caption='Escaños de Madrid el 23J de 2023, sin y con el voto de los residentes en el extranjero (CERA)',
                   cabecera=['Partido', 'Sin CERA', 'Con CERA', 'Votos CERA'],
                   filas=[['PP', md['sin_cera']['PP'], md['con_cera']['PP'], N(md['cera_pp'])],
                          ['PSOE', md['sin_cera']['PSOE'], md['con_cera']['PSOE'], N(md['cera_psoe'])],
                          ['Sumar', md['sin_cera']['Sumar'], md['con_cera']['Sumar'], '—'],
                          ['Vox', md['sin_cera']['Vox'], md['con_cera']['Vox'], '—']]),
        grafico=None,
        compara='El reparto D\'Hondt de los 37 escaños de Madrid con y sin los votos emitidos desde el extranjero.',
        limites='Datos del escrutinio por mesa de Interior. «Votos que faltaban» es el mínimo de votos adicionales con el que una lista habría superado el último cociente, sin restar votos a nadie.',
        csv='escanos-ajustados-2023.csv', fuentes=['interior'], lugares=['Madrid'],
        faq=[('¿Qué es el voto CERA?', 'El de los españoles inscritos en el Censo Electoral de Residentes Ausentes, es decir, que viven en el extranjero. Se cuenta días después de la jornada electoral.')],
    ))

    # ------------------------------------------------------------------ bisagras: escaños ajustados
    seis = mg[:C['margenes_menos_1500']]
    junts = [f for f in seis if f['ultimo_escano'] == 'Junts']
    out.append(dict(
        slug='escanos-ajustados-2023', serie='bisagras', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'{C["margenes_menos_1500"]} escaños del 23J se decidieron por menos de 1.500 votos; en Girona bastaban {N(mg[0]["votos_que_faltaban"])}',
        pregunta='¿En qué provincias el último escaño estuvo a punto de cambiar de manos?',
        resumen=(f'En {C["margenes_menos_1500"]} de las 52 circunscripciones, a la lista que se quedó sin el último escaño le faltaron menos de 1.500 votos para lograrlo. '
                 f'Los dos casos más ajustados fueron Girona, donde al PP le faltaron {N(mg[0]["votos_que_faltaban"])} votos para quitar el escaño a Junts, '
                 f'y Cantabria, donde le faltaron {N(mg[1]["votos_que_faltaban"])} para quitárselo a Vox.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Cómo se mide lo cerca que estuvo un escaño'),
            ('dato', 'En cada provincia, la ley D\'Hondt divide los votos de cada candidatura entre 1, 2, 3… y entrega los escaños a los cocientes más altos. '
                     'El último escaño va al último cociente que entra; el primero que se queda fuera es el de la lista aspirante. '
                     'La diferencia entre los dos se puede traducir en votos: los que habría necesitado la aspirante, sin quitarle ninguno a nadie, para pasar por delante.'),
            ('sub', 'Seis provincias en el filo'),
            ('dato', f'El escaño más barato de 2023 estuvo en Girona. El sexto diputado de la provincia fue para Junts, y al PP le faltaron {N(mg[0]["votos_que_faltaban"])} votos para llevárselo. '
                     f'En Cantabria, el quinto fue para Vox; al PP le faltaron {N(mg[1]["votos_que_faltaban"])}.'),
            ('dato', '; '.join(f'{"En" if i == 0 else "en"} {f["provincia"]}, el último escaño fue para {art(f["ultimo_escano"])} y {art(f["aspirante"], "a ")} le faltaron {N(f["votos_que_faltaban"])} votos' for i, f in enumerate(seis[2:])) + '.'),
            ('dato', f'Los márgenes van en las dos direcciones. En Girona y Cantabria el PP fue el que se quedó a las puertas; en Madrid y Salamanca, fue el PSOE el que se quedó a menos de 1.500 votos del PP.'),
            ('sub', 'Lo que habría cambiado'),
            ('dato', f'{len(junts)} de los {C["escanos_2023_con_cera"]["Junts"]} diputados de Junts salieron de estos márgenes: el de Girona y el de Tarragona. '
                     f'Con {N(mg[0]["votos_que_faltaban"])} votos más para el PP en Girona, Junts habría tenido {C["escanos_2023_con_cera"]["Junts"] - 1} escaños.'),
            ('dato', f'El de Cantabria muestra que no todos los vuelcos cambian los bloques. Si el PP le hubiera quitado ese escaño a Vox, PP y Vox habrían seguido sumando {C["escanos_2023_con_cera"]["PP"] + C["escanos_2023_con_cera"]["Vox"]}.'),
            ('dato', f'Justo por encima de los 1.500 votos quedaron {mg[6]["provincia"]} ({N(mg[6]["votos_que_faltaban"])}), {mg[7]["provincia"]} ({N(mg[7]["votos_que_faltaban"])}), '
                     f'{mg[8]["provincia"]}, donde a {mg[8]["aspirante"]} le faltaron {N(mg[8]["votos_que_faltaban"])}, y {mg[9]["provincia"]} ({N(mg[9]["votos_que_faltaban"])}).'),
        ],
        no_sabemos=['Si estos márgenes se repetirán el 29N. Un margen pequeño en 2023 no significa que la provincia vaya a ser decisiva en 2026.'],
        tabla=dict(caption='Las diez circunscripciones con el último escaño más ajustado el 23J de 2023 (con voto CERA)',
                   cabecera=['Provincia', 'Escaños', 'Último escaño', 'Aspirante', 'Votos que le faltaban'],
                   filas=[[f['provincia'], f['escanos'], f['ultimo_escano'], f['aspirante'], N(f['votos_que_faltaban'])] for f in mg]),
        grafico=(margenes(mg, 'Votos que le faltaron a la lista aspirante para el último escaño'), 'Votos que le faltaron a la lista aspirante para ganar el último escaño, 23J de 2023.'),
        compara='Las 52 circunscripciones del Congreso en 2023: el último escaño asignado y la lista que más cerca estuvo de lograrlo.',
        limites='Calculado con los votos por mesa de Interior, incluido el CERA; el reparto completo reproduce los 350 escaños oficiales. Los votos que faltaban suponen que la lista suma votos sin que nadie los pierda.',
        csv='escanos-ajustados-2023.csv', fuentes=['interior'], lugares=[f['provincia'] for f in mg[:4]],
        faq=None,
    ))

    # ------------------------------------------------------------------ ciudad y entorno: capitales
    cp = C['capitales']
    cc = {f['capital']: f for f in cp}
    menos = [f for f in cp if f['dif_pp'] < 0]
    top = sorted(cp, key=lambda f: -f['dif_pp'])[:6]
    sur = ['Granada', 'Badajoz', 'Sevilla', 'Cáceres', 'Córdoba', 'Jaén']
    norte = ['Ourense', 'Soria', 'Ávila', 'Lugo', 'Palencia', 'Zamora', 'A Coruña']
    lista = lambda ns, k: yl(f'{n} ({S(cc[n][k])})' for n in ns)
    out.append(dict(
        slug='capitales-frente-a-su-provincia', serie='ciudad-y-entorno', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'La capital no es la isla progresista de su provincia: en {C["capitales_resumen"]["mas_pp"]} de 50 vota más al PP que el resto',
        pregunta='¿Votan las capitales de provincia más a la izquierda que su entorno?',
        resumen=(f'No en la mayoría de España. El 23J, la capital dio al PP un porcentaje mayor que el resto de su provincia en {C["capitales_resumen"]["mas_pp"]} de 50 casos, '
                 f'con Granada (+{num(cc["Granada"]["dif_pp"])} puntos), Donostia y Vitoria a la cabeza. '
                 f'La imagen de la ciudad progresista frente al campo conservador solo se cumple en {C["capitales_resumen"]["menos_pp"]} provincias, '
                 f'sobre todo en Galicia y Castilla y León: Ourense y Soria votaron {D(cp[0]["dif_pp"])} puntos menos al PP que su entorno.'),
        estado='Patrón',
        cuerpo=[
            ('sub', 'Un tópico que no se cumple'),
            ('dato', 'La idea de que las ciudades votan a la izquierda y los pueblos a la derecha se repite en cada noche electoral. '
                     'Para comprobarla, esta pieza compara el voto de cada capital de provincia con el del resto de municipios de su provincia, sumados, en las generales de 2023.'),
            ('dato', f'El resultado lleva la contraria al tópico. En {C["capitales_resumen"]["mas_pp"]} de las 50 provincias, la capital dio al PP un porcentaje mayor que su entorno. '
                     f'Las diferencias más grandes: {lista([f["capital"] for f in top], "dif_pp")} puntos.'),
            ('sub', 'El sur: capitales más conservadoras que su campo'),
            ('dato', f'En Andalucía y Extremadura la distancia es mayor y tiene un reverso claro. Las capitales votan más al PP: {lista(sur, "dif_pp")}. '
                     f'Y votan menos al PSOE que sus pueblos: {lista(["Badajoz", "Córdoba", "Granada", "Jaén", "Cáceres", "Sevilla"], "dif_psoe")}.'),
            ('patrón', 'En buena parte del sur, el voto socialista es más rural que urbano. El campo es el bastión del PSOE y la ciudad, el del PP.'),
            ('dato', f'No todo el sur sigue ese dibujo. Málaga, Cádiz, Almería y Huelva votan casi igual que su provincia: las diferencias de voto al PP están entre {D(max(cc[n]["dif_pp"] for n in ("Málaga", "Cádiz", "Almería", "Huelva")))} y {D(min(cc[n]["dif_pp"] for n in ("Málaga", "Cádiz", "Almería", "Huelva")))} puntos.'),
            ('sub', 'El noroeste: aquí sí, la ciudad vota menos al PP'),
            ('dato', f'Donde el tópico se cumple es, sobre todo, en Galicia y Castilla y León. La capital vota menos al PP que su provincia en {lista(norte, "dif_pp")}.'),
            ('dato', f'En casi todas ellas la capital vota, además, más al PSOE: Ourense {S(cc["Ourense"]["dif_psoe"])}, Soria {S(cc["Soria"]["dif_psoe"])}, Palencia {S(cc["Palencia"]["dif_psoe"])}, Lugo {S(cc["Lugo"]["dif_psoe"])}. '
                     f'Ávila es la excepción: su capital vota menos al PP ({S(cc["Ávila"]["dif_pp"])}) y también menos al PSOE ({S(cc["Ávila"]["dif_psoe"])}) que el resto de la provincia.'),
            ('sub', 'Euskadi y Cataluña: otra lógica'),
            ('dato', f'En el País Vasco y Cataluña la capital también da más voto al PP, pero la cifra engaña si se lee con ojos andaluces. '
                     f'En Vitoria, el PP saca {num(cc["Vitoria-Gasteiz"]["dif_pp"])} puntos más que en el resto de Álava y el PSOE, {num(cc["Vitoria-Gasteiz"]["dif_psoe"])} más. '
                     f'En Lleida, los dos suben {num(cc["Lleida"]["dif_pp"])} puntos.'),
            ('patrón', 'Cuando la capital vota más a los dos grandes partidos estatales a la vez, lo que cambia no es el equilibrio entre izquierda y derecha, sino el peso de las demás candidaturas, que es mayor fuera de la capital.'),
            ('dato', f'Las tres ciudades más grandes del país votan algo más al PP que su provincia, sin grandes distancias: Madrid {S(cc["Madrid"]["dif_pp"])}, Barcelona {S(cc["Barcelona"]["dif_pp"])} y València {S(cc["València"]["dif_pp"])} puntos de voto al PP frente al resto de su provincia.'),
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
    sur6 = [r for r in ms['municipios'] if r['grupo'] == 'sur']
    no = [r for r in ms['municipios'] if r['grupo'] == 'noroeste']
    caida = {r['municipio']: r['izq_2004'] - r['izq_2023'] for r in sur6}
    rng = lambda xs, d=1: (num(min(xs), d), num(max(xs), d))
    out.append(dict(
        slug='sur-de-madrid', serie='contra-su-provincia', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'El PSOE ganó en cuatro grandes ciudades del sur de Madrid mientras el PP ganaba la provincia por {N(ms["prov_pp"] - ms["prov_psoe"])} puntos',
        pregunta='¿Dónde resiste el PSOE en la provincia que más diputados da al PP, y por cuánto?',
        resumen=(f'El PP ganó la provincia de Madrid el 23J con el {P(ms["prov_pp"])} frente al {P(ms["prov_psoe"])} del PSOE. '
                 f'Pero el PSOE fue primero en Parla, Fuenlabrada, Leganés y Getafe, cuatro ciudades que suman {N(sum(mm[n]["poblacion"] for n in sur4))} habitantes. '
                 f'La ventaja se estrecha: en 2004 la izquierda (PSOE más Sumar, Podemos o IU) sacó entre el {P(min(mm[n]["izq_2004"] for n in sur4))} y el {P(max(mm[n]["izq_2004"] for n in sur4))} en las cuatro; en 2023, entre el {P(min(mm[n]["izq_2023"] for n in sur4))} y el {P(max(mm[n]["izq_2023"] for n in sur4))}, '
                 f'y en Móstoles y Alcorcón ya ganó el PP.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Cuatro ciudades a contracorriente'),
            ('dato', f'En la provincia de Madrid el PP ganó el 23J con holgura: {P(ms["prov_pp"])} de los votos frente al {P(ms["prov_psoe"])} del PSOE. '
                     f'Pero en el cinturón sur, el mapa cambia de color. El PSOE fue el partido más votado en cuatro de sus grandes ciudades.'),
            ('dato', '; '.join(f'{"En" if i == 0 else "en"} {n}, PSOE {P(mm[n]["psoe"])} y PP {P(mm[n]["pp"])}' for i, n in enumerate(sur4)) + '. '
                     f'Entre las cuatro suman {N(sum(mm[n]["poblacion"] for n in sur4))} habitantes.'),
            ('sub', 'Una ventaja que se estrecha'),
            ('dato', f'Hace veinte años, la izquierda estatal (el PSOE más el espacio de IU, Podemos y Sumar) superaba el 60 % en esas cuatro ciudades: Parla {P(mm["Parla"]["izq_2004"])}, Fuenlabrada {P(mm["Fuenlabrada"]["izq_2004"])}, Getafe {P(mm["Getafe"]["izq_2004"])}, Leganés {P(mm["Leganés"]["izq_2004"])}. '
                     f'En 2023 rondaba el 52 o 53 %: entre el {P(min(mm[n]["izq_2023"] for n in sur4))} y el {P(max(mm[n]["izq_2023"] for n in sur4))}.'),
            ('dato', f'En las dos grandes ciudades vecinas, el vuelco ya se ha producido. En Móstoles, el PP sacó el {P(mm["Móstoles"]["pp"])} y el PSOE el {P(mm["Móstoles"]["psoe"])}; en Alcorcón, {P(mm["Alcorcón"]["pp"])} frente a {P(mm["Alcorcón"]["psoe"])}. '
                     f'Allí PP, Vox y Cs juntos ({P(mm["Móstoles"]["der_2023"])} y {P(mm["Alcorcón"]["der_2023"])}) superan ya a la izquierda ({P(mm["Móstoles"]["izq_2023"])} y {P(mm["Alcorcón"]["izq_2023"])}).'),
            ('patrón', f'En las seis ciudades del sur, la izquierda ha perdido entre {D(min(caida.values()))} y {D(max(caida.values()))} puntos desde 2004. La caída más fuerte es la de Parla, que era la más roja.'),
            ('sub', 'El otro Madrid, en el noroeste'),
            ('dato', f'Al otro lado de la capital, en Boadilla del Monte, Pozuelo de Alarcón, Majadahonda, Las Rozas y Villanueva de la Cañada, el PP saca entre el {rng([r["pp"] for r in no])[0]} y el {rng([r["pp"] for r in no])[1]} % y el PSOE entre el {rng([r["psoe"] for r in no])[0]} y el {rng([r["psoe"] for r in no])[1]} %. '
                     f'PP, Vox y Cs juntos pasan del 70 %.'),
            ('patrón', f'La renta separa los dos Madrid. En las cuatro ciudades del sur donde gana el PSOE, la renta por unidad de consumo está entre {N(min(mm[n]["renta"] for n in sur4))} y {N(max(mm[n]["renta"] for n in sur4))} euros; '
                       f'en los cinco municipios del noroeste, entre {N(min(r["renta"] for r in no))} y {N(max(r["renta"] for r in no))}.'),
            ('patrón', f'La renta no lo resume todo. Boadilla del Monte votó a la derecha {num(next(x["diferencia"] for x in C["lalin"]["top"] if x["municipio"] == "Boadilla del Monte"))} puntos más de lo que predice su perfil de renta, edad, estudios, paro, extranjeros y tamaño.'),
            ('dato', f'Y el retroceso de la izquierda tampoco es solo cosa del sur: en Boadilla bajó del {P(mm["Boadilla del Monte"]["izq_2004"])} en 2004 al {P(mm["Boadilla del Monte"]["izq_2023"])} en 2023, y en Pozuelo del {P(mm["Pozuelo de Alarcón"]["izq_2004"])} al {P(mm["Pozuelo de Alarcón"]["izq_2023"])}.'),
        ],
        no_sabemos=['Si el estrechamiento en el sur se debe a cambios de voto de los mismos vecinos o a la llegada de población nueva a barrios recientes. Los datos agregados por municipio no lo distinguen; el análisis por sección censal es el paso siguiente.'],
        tabla=dict(caption='Voto al PP y al PSOE y bloque de izquierda estatal (PSOE + Sumar/Podemos/IU) en el sur y el noroeste de Madrid (% del voto válido)',
                   cabecera=['Municipio', 'Zona', 'PP 2023', 'PSOE 2023', 'Izquierda 2004', 'Izquierda 2023', 'Renta (€/u.c.)'],
                   filas=[[r['municipio'], r['grupo'], num(r['pp']), num(r['psoe']), num(r['izq_2004']), num(r['izq_2023']), N(r['renta'])] for r in ms['municipios']]),
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
    e_min, e_max = min(br, key=br.get), max(br, key=br.get)
    out.append(dict(
        slug='a-illa-vilanova-de-arousa', serie='fronteras', fecha_datos='2004-2023', revisado='2026-10-06',
        titulo=f'A Illa de Arousa vota {N(br["2023_07"])} puntos menos al PP que Vilanova, al otro lado del puente, y así desde hace veinte años',
        pregunta='¿Por qué dos municipios vecinos con la misma renta y la misma edad votan tan distinto?',
        resumen=(f'El 23J de 2023, el PP sacó el {P(il["pp"]["2023_07"])} en A Illa de Arousa y el {P(vi["pp"]["2023_07"])} en Vilanova de Arousa, '
                 f'el municipio vecino al otro lado del puente. Tienen casi la misma renta ({N(il["renta"])} y {N(vi["renta"])} euros por unidad de consumo) '
                 f'y una edad media parecida. La distancia no es nueva: en las ocho generales desde 2004 ha estado entre {N(min(br.values()))} y {N(max(br.values()))} puntos.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos orillas, dos votos'),
            ('dato', f'A Illa de Arousa y Vilanova de Arousa comparten ría, puente y casi todo lo que miden las estadísticas. Lo que no comparten es el voto. '
                     f'El 23J, el PP sacó el {P(vi["pp"]["2023_07"])} en Vilanova y el {P(il["pp"]["2023_07"])} en A Illa. '
                     f'En A Illa el partido más votado fue el PSOE, con el {P(il["psoe_2023"])}, y el BNG sacó el {P(il["bng_2023"])}, más del doble que en Vilanova ({P(vi["bng_2023"])}).'),
            ('dato', f'Los datos del INE no ofrecen una pista fácil. La renta por unidad de consumo es de {N(il["renta"])} euros en A Illa y {N(vi["renta"])} en Vilanova; '
                     f'la edad media, {num(il["edad"])} y {num(vi["edad"])} años. Donde sí difieren, la diferencia no apunta hacia donde cabría esperar: '
                     f'A Illa tiene menos paro ({P(il["paro"])} frente a {P(vi["paro"])} en 2021) y menos población extranjera ({P(il["extranjeros"])} frente a {P(vi["extranjeros"])}).'),
            ('sub', 'Veinte años de distancia'),
            ('dato', f'La brecha no es de una elección. En las ocho generales desde 2004, el PP ha sacado en Vilanova entre {N(min(br.values()))} y {N(max(br.values()))} puntos más que en A Illa. '
                     f'La distancia más corta fue la de {ANYO[e_min]} ({num(br[e_min])}) y la más larga, la de {ANYO[e_max]} ({num(br[e_max])}).'),
            ('dato', f'El mejor año del PP en los dos municipios fue el mismo, 2011: {P(vi["pp"]["2011_11"])} en Vilanova y {P(il["pp"]["2011_11"])} en A Illa. '
                     f'El peor, abril de 2019: {P(vi["pp"]["2019_04"])} y {P(il["pp"]["2019_04"])}.'),
            ('patrón', 'Las dos curvas suben y bajan a la vez, al ritmo del voto general al PP. Lo que no cambia es la distancia entre ellas.'),
            ('sub', 'También en las municipales'),
            ('dato', f'La frontera se mantiene cuando lo que se elige es el alcalde. En las municipales de mayo de 2023, el PP sacó el {P(il["pp_m2023"])} en A Illa y el {P(vi["pp_m2023"])} en Vilanova; '
                     f'el BNG, el {P(il["bng_m2023"])} y el {P(vi["bng_m2023"])}.'),
            ('dato', f'A Illa es un municipio pequeño, de {N(il["poblacion"])} habitantes, frente a los {N(vi["poblacion"])} de Vilanova. Unos pocos cientos de votos mueven su porcentaje, pero una distancia que se repite en ocho elecciones seguidas no es ruido.'),
        ],
        no_sabemos=['Qué explica la diferencia. Hay hipótesis por comprobar: la historia de la separación entre los dos municipios, la economía del marisqueo y las cofradías en A Illa, o la implantación local del BNG. Ninguna está respaldada todavía por dos fuentes independientes.',
                    'Si la segregación de 1997 tuvo que ver con la distancia en el voto: esta pieza no tiene datos para saberlo.'],
        tabla=dict(caption='Voto al PP en A Illa de Arousa y Vilanova de Arousa en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'A Illa de Arousa', 'Vilanova de Arousa', 'Diferencia'],
                   filas=[[ANYO[e], num(il['pp'][e]), num(vi['pp'][e]), num(br[e])] for e in CONG]),
        grafico=(lineas([('Vilanova', vi['pp'], 'var(--ppl)', True), ('A Illa', il['pp'], 'var(--pp)', True)], CONG,
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
        titulo=f'En 2004 Cabra y Montilla votaban igual; en 2023 las separaban {N(cb["der"]["2023_07"] - mo["der"]["2023_07"])} puntos de voto a la derecha',
        pregunta='¿Cuándo y cómo empezaron a votar distinto dos ciudades cordobesas con el mismo perfil?',
        resumen=(f'Cabra y Montilla, en el sur de Córdoba, tienen casi la misma renta ({N(cb["renta"])} y {N(mo["renta"])} euros), la misma edad media y el mismo paro. '
                 f'En 2004 el PP sacó en las dos casi lo mismo ({P(cb["der"]["2004_03"])} y {P(mo["der"]["2004_03"])}). '
                 f'Desde entonces se han ido separando: en 2023 la derecha sacó el {P(cb["der"]["2023_07"])} en Cabra, donde ganó el PP, y el {P(mo["der"]["2023_07"])} en Montilla, donde ganó el PSOE.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Dos ciudades casi idénticas'),
            ('dato', f'Si se buscan en Andalucía dos municipios medianos que se parezcan en todo lo que mide el INE, salen Cabra y Montilla, en la campiña y la Subbética de Córdoba. '
                     f'Renta por unidad de consumo: {N(cb["renta"])} y {N(mo["renta"])} euros. Edad media: {num(cb["edad"])} y {num(mo["edad"])} años. '
                     f'Paro: {P(cb["paro"])} y {P(mo["paro"])}. Estudios superiores: {P(cb["estudios"])} y {P(mo["estudios"])}. Población: {N(cb["poblacion"])} y {N(mo["poblacion"])} habitantes.'),
            ('sub', '2004: el mismo punto de partida'),
            ('dato', f'En las generales de 2004 votaron como gemelas. El PSOE sacó el {P(cb["psoe"]["2004_03"])} en Cabra y el {P(mo["psoe"]["2004_03"])} en Montilla; '
                     f'el PP, el {P(cb["pp"]["2004_03"])} y el {P(mo["pp"]["2004_03"])}.'),
            ('sub', 'Cómo se abrió la brecha'),
            ('dato', f'La primera grieta llegó en 2008. El PP subió en Cabra hasta el {P(cb["pp"]["2008_03"])} y en Montilla apenas se movió ({P(mo["pp"]["2008_03"])}), '
                     f'mientras el PSOE crecía más en Montilla ({P(mo["psoe"]["2008_03"])}) que en Cabra ({P(cb["psoe"]["2008_03"])}). '
                     f'En 2011, el año de la mayoría absoluta del PP, la distancia se mantuvo: {P(cb["pp"]["2011_11"])} frente a {P(mo["pp"]["2011_11"])}.'),
            ('dato', f'Ciudadanos no la ensanchó. En 2015 sacó casi lo mismo en las dos ciudades ({P(cb["cs"]["2015_12"])} y {P(mo["cs"]["2015_12"])}), y en abril de 2019, {P(cb["cs"]["2019_04"])} y {P(mo["cs"]["2019_04"])}.'),
            ('dato', f'Vox, sí. En abril de 2019 sacó el {P(cb["vox"]["2019_04"])} en Cabra y el {P(mo["vox"]["2019_04"])} en Montilla. En noviembre de ese año, el {P(cb["vox"]["2019_11"])} y el {P(mo["vox"]["2019_11"])}: '
                     f'uno de cada cuatro votos en Cabra. En 2023 bajó al {P(cb["vox"]["2023_07"])} y al {P(mo["vox"]["2023_07"])}.'),
            ('dato', f'El resultado de 2023 es el de dos ciudades que ya no se parecen en las urnas. En Cabra ganó el PP, con el {P(cb["pp"]["2023_07"])} frente al {P(cb["psoe"]["2023_07"])} del PSOE. '
                     f'En Montilla ganó el PSOE, con el {P(mo["psoe"]["2023_07"])} frente al {P(mo["pp"]["2023_07"])} del PP.'),
            ('patrón', f'Sumados PP, Vox y Cs, la distancia pasó de {num(cb["der"]["2004_03"] - mo["der"]["2004_03"])} puntos en 2004 a {num(cb["der"]["2023_07"] - mo["der"]["2023_07"])} en 2023. '
                       f'Se abrió en dos tiempos, con el PP desde 2008 y con Vox desde 2019, y no se ha vuelto a cerrar.'),
        ],
        no_sabemos=['Por qué el PP y Vox crecieron más en una ciudad que en la otra. Hipótesis por contrastar: estructura productiva (la economía del vino en Montilla), historia municipal y liderazgos locales. Sin dos fuentes, ninguna se afirma.'],
        tabla=dict(caption='PP + Vox + Cs en Cabra y Montilla en las elecciones generales, 2004-2023 (% del voto válido)',
                   cabecera=['Elección', 'Cabra', 'Montilla', 'Diferencia'],
                   filas=[[ANYO[e], num(cb['der'][e]), num(mo['der'][e]), num(cb['der'][e] - mo['der'][e])] for e in CONG]),
        grafico=(lineas([('Cabra', cb['der'], 'var(--ppl)', True), ('Montilla', mo['der'], 'var(--pp)', True)], CONG,
                        'PP + Vox + Cs en Cabra y Montilla, 2004-2023', 20, 60),
                 'PP, Vox y Cs juntos en Cabra y Montilla, generales de 2004 a 2023 (% del voto válido).'),
        compara='Dos municipios de entre 19.000 y 23.000 habitantes de la provincia de Córdoba, elegidos por ser de los más parecidos de Andalucía en renta, edad, extranjeros, estudios, paro y tamaño.',
        limites='«Gemelos» según seis indicadores del INE; pueden diferir en otros (estructura económica, historia, oferta electoral local) que los datos no recogen.',
        csv='cabra-montilla.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Cabra', 'Montilla'],
        faq=[('¿Cómo se eligen los gemelos?', 'Se estandarizan seis indicadores (renta, edad media, porcentaje de extranjeros, estudios superiores, paro y tamaño) y se buscan pares de municipios de más de 15.000 habitantes de la misma comunidad con la menor distancia entre ellos.')],
    ))

    # ------------------------------------------------------------------ excepciones: Puerto Real
    pr = C['puerto_real']
    bh = {b['municipio']: b for b in pr['bahia']}
    rk = C['ranking_residuo_derecha_10k']
    dist = {e: pr['izq_serie'][e] - pr['izq_prov_serie'][e] for e in CONG}
    out.append(dict(
        slug='puerto-real', serie='excepciones', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo=f'Puerto Real vota {N(abs(pr["diferencia"]))} puntos menos a la derecha de lo que predicen sus datos: la mayor excepción de España',
        pregunta='¿Qué municipio se aparta más de lo que su perfil social haría esperar?',
        resumen=(f'Por su renta, edad, paro, estudios, extranjeros y tamaño, a Puerto Real (Cádiz) le correspondería dar a PP, Vox y Cs alrededor del {P(pr["previsto"])} del voto. '
                 f'El 23J les dio el {P(pr["der"])}. Es la mayor diferencia entre los {C["n_municipios_10k"]} municipios de más de 10.000 habitantes. '
                 f'El PSOE ganó allí con el {P(pr["psoe"])} en una provincia que ganó el PP.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Lo que dicen sus datos y lo que dicen sus urnas'),
            ('dato', f'Con seis datos del INE (renta, edad media, paro, estudios superiores, población extranjera y tamaño) y la provincia, se puede estimar con bastante acierto cuánto vota a la derecha un municipio español. '
                     f'El modelo de esta serie explica el {N(C["modelo_municipal"]["r2_derecha"] * 100)} % de las diferencias entre municipios. Lo interesante es el resto: los lugares donde falla.'),
            ('dato', f'Ninguno falla tanto como Puerto Real. Es un municipio de {N(pr["poblacion"])} habitantes en la bahía de Cádiz, con una renta de {N(pr["renta"])} euros por unidad de consumo y un paro del {P(pr["paro"])} en 2021. '
                     f'Con ese perfil, a PP, Vox y Cs les correspondería alrededor del {P(pr["previsto"])} del voto. El 23J sacaron el {P(pr["der"])}: {D(pr["diferencia"])} puntos menos.'),
            ('dato', f'El reparto fue PSOE {P(pr["psoe"])}, Sumar {P(pr["sumar"])}, PP {P(pr["pp"])} y Vox {P(pr["vox"])}. '
                     f'En el conjunto de la provincia, el PP fue primero con el {P(pr["prov_pp"])} y el PSOE sacó el {P(pr["prov_psoe"])}.'),
            ('sub', 'Un caso único en la bahía'),
            ('dato', f'Lo que pasa en Puerto Real no pasa en sus vecinos. San Fernando ({S(bh["San Fernando"]["diferencia"])} puntos), El Puerto de Santa María ({S(bh["El Puerto de Santa María"]["diferencia"])}), '
                     f'Jerez ({S(bh["Jerez de la Frontera"]["diferencia"])}) y Chiclana ({S(bh["Chiclana de la Frontera"]["diferencia"])}) votan prácticamente lo que predice su perfil. '
                     f'Solo Cádiz capital se queda claramente por debajo, a {D(bh["Cádiz"]["diferencia"])} puntos, menos de la mitad que Puerto Real.'),
            ('dato', 'En el resto de España, las siguientes excepciones son ' + yl(f'{r["municipio"]} ({r["provincia"]}, {S(r["diferencia"])})' for r in rk[1:6]) + '. '
                     'Ninguna se aparta tanto como Puerto Real.'),
            ('sub', 'No es de ahora'),
            ('dato', f'La izquierda estatal (PSOE más el espacio de IU, Podemos y Sumar) sacó en Puerto Real el {P(pr["izq_serie"]["2004_03"])} en 2004 y el {P(pr["izq_serie"]["2023_07"])} en 2023. '
                     f'Solo en 2011 bajó con fuerza, al {P(pr["izq_serie"]["2011_11"])}, el año en que en toda la provincia cayó al {P(pr["izq_prov_serie"]["2011_11"])}.'),
            ('patrón', f'Mientras la provincia se movía a la derecha, Puerto Real se quedó donde estaba. La izquierda bajó en el conjunto de Cádiz del {P(pr["izq_prov_serie"]["2004_03"])} al {P(pr["izq_prov_serie"]["2023_07"])}, '
                       f'y la distancia de Puerto Real con su provincia creció de {num(dist["2004_03"])} a {num(dist["2023_07"])} puntos.'),
            ('dato', f'El voto local va en la misma dirección. En las municipales de 2023 fue primera la lista «{pr["m2023_lista"]}», con el {P(pr["m2023_lista_pct"])} del voto válido.'),
        ],
        no_sabemos=['Por qué. La hipótesis más citada en la conversación pública es la tradición obrera y sindical ligada a la industria naval de la bahía. Esta pieza aún no la ha contrastado con dos fuentes independientes (hemeroteca, estudios sobre el movimiento obrero en la bahía, entrevistas), así que la deja como hipótesis.'],
        tabla=dict(caption='Voto a PP + Vox + Cs real y previsto por el perfil en los municipios de más de 20.000 habitantes de Cádiz, 23J de 2023',
                   cabecera=['Municipio', 'Real', 'Previsto', 'Diferencia', 'Renta (€/u.c.)'],
                   filas=[[b['municipio'], num(b['real']), num(b['previsto']), ('+' if b['diferencia'] > 0 else '') + num(b['diferencia']), N(b['renta'])] for b in pr['bahia']]),
        grafico=(barras_previsto(pr['bahia'], 'Voto a PP, Vox y Cs real y previsto en los grandes municipios de Cádiz', 'Puerto Real'),
                 'Voto a PP, Vox y Cs previsto por el perfil (círculo vacío) y real (círculo lleno) en los municipios de más de 20.000 habitantes de Cádiz, 23J de 2023.'),
        compara=f'Los {C["n_municipios_10k"]} municipios españoles de más de 10.000 habitantes con todos los indicadores disponibles, frente a lo que predice para cada uno un modelo estadístico estimado con {N(C["modelo_municipal"]["n"])} municipios.',
        limites='Un modelo estadístico no es una explicación: la diferencia indica dónde mirar, no por qué. «Derecha» suma PP, Vox y Cs; los partidos regionalistas quedan fuera, lo que afecta a Cantabria (PRC).',
        csv='puerto-real.csv', fuentes=['interior', 'ine_adrh', 'ine_censo'], lugares=['Puerto Real'],
        faq=[('¿Qué significa «lo que predicen sus datos»?', 'Es el porcentaje que estima un modelo de regresión a partir de la renta, la edad media, el porcentaje de extranjeros, los estudios superiores, el paro, el tamaño del municipio y su provincia. La metodología completa está enlazada al final.')],
    ))

    # ------------------------------------------------------------------ voto doble: Badalona
    bd = C['badalona']
    gap = {a: bd[m]['PP'] - bd[g]['PP'] for a, m, g in (('2015', 'M2015', '2015_12'), ('2019', 'M2019', '2019_11'), ('2023', 'M2023', '2023_07'))}
    out.append(dict(
        slug='badalona', serie='voto-doble', fecha_datos='mayo y julio de 2023', revisado='2026-10-06',
        titulo=f'Badalona dio al PP el {N(bd["M2023"]["PP"])} % en mayo y el {N(bd["2023_07"]["PP"])} % en julio: la mayor distancia de España entre voto local y estatal',
        pregunta='¿Dónde se separa más el voto a un mismo partido entre las municipales y las generales?',
        resumen=(f'En las municipales del 28 de mayo de 2023, el PP sacó en Badalona el {P(bd["M2023"]["PP"])} del voto válido. '
                 f'En las generales del 23 de julio, dos meses después, el {P(bd["2023_07"]["PP"])}, y el PSC ganó con el {P(bd["2023_07"]["PSOE"])}. '
                 f'Son {N(bd["M2023"]["PP"] - bd["2023_07"]["PP"])} puntos de diferencia, la mayor entre los {bd["n_20k"]} municipios de más de 20.000 habitantes.'),
        estado='Dato',
        cuerpo=[
            ('sub', 'Mayo y julio'),
            ('dato', f'Badalona votó dos veces en dos meses y pareció dos ciudades distintas. El 28 de mayo de 2023, en las municipales, el PP sacó el {P(bd["M2023"]["PP"])} del voto válido. '
                     f'El PSC se quedó en el {P(bd["M2023"]["PSOE"])}, el espacio de los comuns y Podemos en el {P(bd["M2023"]["SUMAR"])} y ERC en el {P(bd["M2023"]["ERC"])}.'),
            ('dato', f'El 23 de julio, en las generales, el orden se dio la vuelta. El PSC ganó con el {P(bd["2023_07"]["PSOE"])}; el PP cayó al {P(bd["2023_07"]["PP"])}, apenas por delante de Sumar ({P(bd["2023_07"]["SUMAR"])}). '
                     f'Vox, que en mayo apenas existía en la ciudad ({P(bd["M2023"]["VOX"])}), sacó el {P(bd["2023_07"]["VOX"])}.'),
            ('dato', f'Entre las dos citas, la participación subió del {P(bd["M2023"]["part"])} al {P(bd["2023_07"]["part"])}: las dos fotos no las hicieron exactamente los mismos votantes.'),
            ('sub', 'La mayor distancia de España'),
            ('dato', f'Ningún municipio de más de 20.000 habitantes separa tanto su voto local y su voto estatal al PP. En Badalona fueron {num(gap["2023"])} puntos. '
                     'Le siguen ' + yl(f'{t["municipio"]} ({t["provincia"]}, {num(t["dif"])})' for t in bd['top'][1:5]) + '.'),
            ('sub', 'Una distancia que viene de lejos y crece'),
            ('dato', f'No es una rareza de 2023. En 2015 el PP sacó en Badalona el {P(bd["M2015"]["PP"])} en las municipales y el {P(bd["2015_12"]["PP"])} en las generales; '
                     f'en 2019, el {P(bd["M2019"]["PP"])} y el {P(bd["2019_11"]["PP"])}.'),
            ('patrón', f'La brecha ha crecido en cada ciclo: {num(gap["2015"])} puntos en 2015, {num(gap["2019"])} en 2019 y {num(gap["2023"])} en 2023.'),
            ('patrón', f'Los datos sugieren por dónde va el cambio, aunque no quién lo hace. En julio el PSC sube {num(bd["2023_07"]["PSOE"] - bd["M2023"]["PSOE"])} puntos y Vox {num(bd["2023_07"]["VOX"] - bd["M2023"]["VOX"])} respecto a mayo, justo cuando el PP pierde. '
                       'Con datos agregados no se puede saber qué vecinos cambian de papeleta; solo que el saldo cambia.'),
        ],
        no_sabemos=['Cuánto se debe al candidato del PP en la ciudad y cuánto a otros factores locales. Es la hipótesis evidente, pero requiere encuestas postelectorales o estudios que esta pieza no ha incorporado.'],
        tabla=dict(caption='Voto en Badalona en las municipales y las generales de 2015, 2019 y 2023 (% del voto válido)',
                   cabecera=['Elección', 'PP', 'PSC', 'Comuns / Sumar', 'ERC', 'Junts', 'Cs', 'Vox', 'Participación'],
                   filas=[[n, num(bd[e]['PP']), num(bd[e]['PSOE']), num(bd[e]['SUMAR']), num(bd[e]['ERC']), num(bd[e]['JUNTS']), num(bd[e]['CS']), num(bd[e]['VOX']), num(bd[e]['part'])]
                          for e, n in (('M2015', 'Municipales 2015'), ('2015_12', 'Generales 2015'), ('M2019', 'Municipales 2019'), ('2019_11', 'Generales nov. 2019'),
                                       ('M2023', 'Municipales 2023'), ('2023_07', 'Generales 2023'))]),
        grafico=(barras_agrupadas([(n, {'Municipales': bd[a]['PP'], 'Generales': bd[b]['PP']}) for n, a, b in
                                   (('2015', 'M2015', '2015_12'), ('2019', 'M2019', '2019_11'), ('2023', 'M2023', '2023_07'))],
                                  [('Municipales', 'var(--pp)'), ('Generales', 'var(--ppl)')], 'Voto al PP en Badalona, municipales y generales', ymax=60),
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
    ct = pa.get('cataluna')
    out.append(dict(
        slug='paro-renta-participacion', serie='quien-no-vota', fecha_datos='23 de julio de 2023', revisado='2026-10-06',
        titulo='A igual renta, los barrios con más paro votan menos: el paro marca más diferencias en la participación que el dinero',
        pregunta='¿Es la pobreza o el desempleo lo que más se asocia a no votar?',
        resumen=(f'En las {N(pa["n_secciones"])} secciones censales de España, la participación del 23J sube con la renta: del {P(dr[0]["part"])} en el 10 % de secciones más pobres al {P(dr[-1]["part"])} en el 10 % más rico. '
                 f'Pero cuando se comparan secciones con la misma renta, la que tiene más paro vota menos: en el quintil más pobre, del {P(q["1"]["1"])} con poco paro al {P(q["1"]["3"])} con mucho. '
                 f'Teniendo en cuenta a la vez renta, paro, estudios, edad y extranjeros, el paro es la variable que más resta.'),
        estado='Patrón',
        cuerpo=[
            ('sub', 'La renta importa…'),
            ('dato', f'Los barrios ricos votan más que los pobres, y el 23J no fue una excepción. '
                     f'Ordenadas las {N(pa["n_secciones"])} secciones censales de España por renta, la participación sube del {P(dr[0]["part"])} en el 10 % más pobre al {P(dr[-1]["part"])} en el 10 % más rico.'),
            ('patrón', f'Pero la subida no es pareja. Buena parte de la diferencia se concentra en los extremos: del primer al segundo decil, la participación salta del {P(dr[0]["part"])} al {P(dr[1]["part"])}, '
                       f'y del noveno al décimo, del {P(dr[8]["part"])} al {P(dr[9]["part"])}. Entre medias, del segundo al octavo decil, apenas se mueve: del {P(dr[1]["part"])} al {P(dr[7]["part"])}.'),
            ('sub', '…pero el paro importa más'),
            ('dato', f'Si se ordenan las mismas secciones por paro, la pendiente es igual de clara en sentido contrario: del {P(dp[0]["part"])} en el 10 % con menos paro al {P(dp[-1]["part"])} en el 10 % con más. '
                     f'El último escalón es el más brusco: del {P(dp[8]["part"])} al {P(dp[9]["part"])}.'),
            ('dato', f'La comparación más clara es la de barrios con la misma renta. Entre las secciones más pobres, las que tienen poco paro votaron un {P(q["1"]["1"])}; las que tienen mucho, un {P(q["1"]["3"])}. '
                     f'Son {num(q["1"]["1"] - q["1"]["3"])} puntos de diferencia sin que cambie el dinero.'),
            ('patrón', f'Esa distancia es menor en los barrios con más renta: {num(q["2"]["1"] - q["2"]["3"])} puntos en el segundo quintil, {num(q["3"]["1"] - q["3"]["3"])} en el tercero, {num(q["4"]["1"] - q["4"]["3"])} en el cuarto y {num(q["5"]["1"] - q["5"]["3"])} en el quinto. '
                       f'El paro se asocia a mucha más abstención en los barrios pobres que en los acomodados.'),
            ('patrón', f'Un modelo que tiene en cuenta a la vez renta, paro, estudios, edad, extranjeros y provincia lo confirma. Una sección con una desviación típica más de paro vota {D(pa["coef"]["paro_2021"])} puntos menos. '
                       f'La renta, sola, se asocia a {num(pa["solo_renta"])} puntos por desviación típica; con las demás variables en el modelo, su peso cae a {num(pa["coef"]["lrenta"])}.'),
            ('sub', 'Cataluña: cuanto menos se vota, más pesa el paro'),
            ('patrón', f'Con los datos de la Generalitat por sección se puede repetir el ejercicio en tres elecciones distintas. En las generales de 2023, cada desviación típica de paro resta {D(ct["g2023"]["paro"])} puntos; '
                       f'en las municipales de 2023, {D(ct["m2023"]["paro"])}; en el Parlament de 2024, {D(ct["p2024"]["paro"])}. '
                       f'En las elecciones con menos participación, el paro pesa casi el doble. La renta, una vez tenido en cuenta lo demás, casi no pesa en ninguna de las tres.') if ct else None,
        ],
        no_sabemos=['Si el desempleo causa la abstención. Es una correlación entre barrios (ecológica), no entre personas: no dice que los parados voten menos, sino que votan menos los barrios con más paro. La literatura académica sobre desempleo y participación es el contraste pendiente.'],
        tabla=dict(caption='Participación el 23J de 2023 por quintil de renta y tercil de paro de la sección censal (%)',
                   cabecera=['Quintil de renta', 'Poco paro', 'Paro medio', 'Mucho paro', 'Diferencia'],
                   filas=[[k, num(v['1']), num(v['2']), num(v['3']), num(v['1'] - v['3'])] for k, v in q.items()]),
        grafico=(lineas([('Mucho paro', {str(k): v['3'] for k, v in q.items()}, 'var(--accent2)', True),
                         ('Poco paro', {str(k): v['1'] for k, v in q.items()}, 'var(--accent)', True)],
                        [str(k) for k in q], 'Participación por quintil de renta, secciones con poco y mucho paro', 55, 80, ' %'),
                 'Participación el 23J por quintil de renta de la sección (1 = más pobre, 5 = más rico), en las secciones con menos y más paro de cada quintil.'),
        compara=f'Las {N(pa["n_secciones"])} secciones censales de España con datos de renta, paro, estudios, edad y extranjeros; participación del 23J sin voto CERA.',
        limites='Paro y estudios son del censo de 2021; renta de 2023. Correlación ecológica: no permite hablar de individuos.',
        csv='participacion-renta-paro.csv', fuentes=['interior', 'ine_adrh', 'ine_censo', 'transparencia'], lugares=[],
        faq=[('¿Votan menos los parados?', 'Estos datos no lo pueden decir: comparan barrios, no personas. Lo que muestran es que los barrios con más paro votan menos que otros con la misma renta.')],
    ))
    for p in out:
        p['cuerpo'] = [c for c in p['cuerpo'] if c]
    return [terreno(p) for p in out]
