"""Fe de errores del Atlas: {slug: [(fecha ISO, texto)]}. paginas.py lo muestra en la propia pieza (ficha «Correcciones»),
le pone esa fecha como «actualizado» y lo lista en atlas/correcciones/. Añadir una línea cada vez que cambie un dato
o una conclusión de una pieza publicada; las erratas que no cambian el sentido no se anotan.
"""

D = '2026-10-08'
DATOS = ('Se recalculan las cifras de 2004 con la agrupación de partidos revisada el 8 de octubre (el PSA y otros partidos '
         'con «socialista» en el nombre que no son el PSOE pasan a Otros). ')

CORRECCIONES = {
    'los-palacios-y-villafranca': [(D, DATOS + 'El PSOE de 2004 en Los Palacios pasa del 65,5 % al 65,0 % (66 % → 65 % en el titular) '
                                       'y el de la provincia de Sevilla, del 58,7 % al 58,3 %. La conclusión no cambia.')],
    'manilva': [(D, DATOS + 'La izquierda de 2004 en Manilva pasa del 65,4 % al 64,9 %, su caída de 29,3 a 28,7 puntos, la de la provincia '
                    'de 13,9 a 13,5 y la diferencia de 15,3 a 15,2. Casares pasa del 74,6 % al 74,3 % y Estepona del 56,1 % al 55,8 %. '
                    'En la tabla de las diez mayores caídas entra La Carlota y sale Requena. Manilva sigue siendo la primera. '
                    'Además, la caída del texto se calcula ahora sin redondear antes, como en la tabla.')],
    'puerto-real': [(D, DATOS + 'La izquierda de 2004 pasa del 70,8 % al 69,7 % en Puerto Real y del 58,2 % al 56,7 % en la provincia; '
                        'la distancia de 2004, de 12,6 a 13,0 puntos. La conclusión no cambia.')],
    'arahal-marchena': [(D, DATOS + 'El PSOE de 2004 pasa del 70,9 % al 70,6 % en Arahal y del 57,4 % al 53,1 % en Marchena.')],
    'cabra-montilla': [(D, DATOS + 'El PSOE de 2004 pasa del 49,4 % al 49,0 % en Cabra y del 49,2 % al 49,0 % en Montilla.')],
    'pueblos-pequenos': [(D, 'Se recalcula con los datos de participación revisados el 8 de octubre: los municipios con dato en las dos '
                             'elecciones pasan de 8.086 a 8.082, los de menos de 2.000 habitantes de 5.821 a 5.817 (en 3.494 se votó más en las '
                             'municipales, antes 3.498) y la participación municipal de los pueblos de 250 a 500 habitantes, del 78,5 % al 78,4 %. '
                             'La conclusión no cambia.')],
    'sant-cugat-badia': [(D, 'La pregunta llamaba a Sant Cugat «el municipio más rico del Vallès». Según la propia tabla, Matadepera tiene más '
                             'renta. Ahora dice «uno de los municipios más ricos del Vallès». En el gráfico, el PSC en Terrassa pasa de 36 a 37 '
                             '(36,5 redondeado).')],
    'aranda-miranda': [(D, 'Se quita la frase «Aranda se ha movido con su provincia», que los datos de la pieza no sostienen: la derecha subió '
                           '7,7 puntos en Aranda y 1,6 en la provincia. Ahora se dan las tres subidas.')],
    'cuencas-mineras-asturianas': [(D, 'El ladillo «IU, por delante del PSOE» generalizaba: IU ganó las municipales en Mieres y Langreo, y el '
                                       'PSOE en Aller. Ahora dice «IU gana en Mieres y Langreo».')],
    'lalin-vilanova-de-arousa': [(D, 'El titular decía «el PP» por encima de lo previsto, pero lo que mide el modelo es el voto a PP, Vox y Cs. '
                                     'Ahora dice «la derecha». Las cifras no cambian.')],
    'paro-renta-participacion': [(D, 'El subtítulo decía que el desempleo «pesa más que el dinero en la abstención», una afirmación causal que '
                                     'la pieza no puede sostener; ahora dice que el paro marca más diferencias en la participación. '
                                     'La frase sobre los quintiles decía que la distancia «se encoge» al subir la renta, pero en el quinto '
                                     'quintil vuelve a subir (3,2 puntos); ahora se da también ese dato.')],
    'sur-de-madrid': [(D, 'Boadilla del Monte votó a la derecha 14,6 puntos más de lo previsto, no 14,5 (se restaban cifras ya redondeadas). '
                          'La pregunta decía que Madrid es «la provincia donde más gana el PP»; lo es en diputados, no en porcentaje, y '
                          'ahora lo dice así.')],
    'capitales-municipales': [(D, '«Ninguna capital se quedó a 10 puntos de su provincia» pasa a «a más de 10 puntos», que es lo que dicen los datos.')],
    'morrazo-sanxenxo': [(D, 'El ladillo «El Morrazo frente a la otra orilla» incluía a Marín, que está en la misma orilla que Bueu. '
                             'Ahora dice «frente a sus vecinos».')],
    'a-illa-vilanova-de-arousa': [(D, 'Se quita de «Lo que no sabemos» que la fecha de la segregación no estaba documentada: la pieza ya la '
                                      'documenta (1 de enero de 1997) con el Diario Oficial de Galicia.')],
}
