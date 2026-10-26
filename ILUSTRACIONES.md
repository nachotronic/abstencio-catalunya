# Ilustraciones pendientes

**Este fichero se genera solo** (`actualidad/src/ilustraciones.py`, cada vez que se construye Actualidad). No lo edites a mano.

Son las piezas de Actualidad que aún llevan un gráfico de datos como imagen de cabecera, o ninguna, de la más reciente a la más antigua. Cuando llega su ilustración, la pieza sale sola de esta lista.

## Cómo se hace una ilustración

1. **Nacho** le dice a ChatGPT qué pieza ilustrar (por ejemplo: «haz la ilustración de `escanos-en-el-filo-29n`»).
2. **ChatGPT** la hace siguiendo la guía de estilo de abajo y **la sube él mismo** al repositorio: rama `chatgpt/ilustracion-<slug>`, un único fichero `img/actualidad/buzon/<slug>.jpg` (JPG, 16:9) y un PR contra `main` titulado «Ilustración: <slug>». Nada más: no toca `construir.py` ni ningún HTML. Si no consigue subir el binario, lo dice en el chat y no da la ilustración por entregada.
3. **Claude** recoge los PR de `chatgpt/ilustracion-*`, mueve la imagen a `img/actualidad/fotos/`, la pone de cabecera con `ia=True`, enseña a Nacho cómo queda y publica cuando Nacho da el OK. Si Nacho la rechaza, se pide otra.

El buzón (`img/actualidad/buzon/`) existe para no pisar nunca un gráfico: algunas piezas ya tienen en `img/actualidad/fotos/<slug>.jpg` su gráfico de cabecera.

## Guía de estilo

- Collage editorial horizontal, 16:9 (se publica a 1280 × 720). Tonos apagados, fondo claro, mucho aire.
- **Sin texto, cifras, gráficos ni mapas con datos** dentro de la imagen. Los datos se dibujan aparte, a partir de los datos.
- Sin logotipos de partidos ni de medios. Políticos reconocibles solo si la pieza va de esa persona; si no, objetos y lugares (urnas, papeletas, fachadas, calles).
- Nada de violencia ni de imitar una fotografía: en la web sale con el pie «Ilustración generada con IA para Mapa Electoral».
- Una ilustración por pieza, sin repetir otra ya publicada.

## Pendientes (57)

| Fecha | Pieza (slug = nombre del fichero) | Titular | Cabecera ahora |
|---|---|---|---|
| 2026-10-26 | [`encuestas-semana-29n`](https://mapaelectoral.es/actualidad/encuestas-semana-29n/) | El PP baja en las cinco encuestas de la semana, pero con Vox sigue sumando mayoría absoluta en todas | primer gráfico de la pieza |
| 2026-10-26 | [`listas-29n-quien-encabeza`](https://mapaelectoral.es/actualidad/listas-29n-quien-encabeza/) | Las listas del 29N, puesto a puesto: 251 escaños casi decididos y 210 candidatos en el aire para los otros 99 | primer gráfico de la pieza |
| 2026-10-23 | [`salario-minimo-provincias-feijoo-29n`](https://mapaelectoral.es/actualidad/salario-minimo-provincias-feijoo-29n/) | Huelva, Almería y Jaén: más de la mitad de sus asalariados cobró en 2024 menos de un salario mínimo al año | gráfico |
| 2026-10-22 | [`ley-nietos-donde-estan-29n`](https://mapaelectoral.es/actualidad/ley-nietos-donde-estan-29n/) | El Constitucional deja sin voto a los nietos: los españoles adultos de América Latina crecen casi cinco veces más rápido y uno de cada tres está inscrito en Madrid | gráfico |
| 2026-10-22 | [`escanos-en-el-filo-29n`](https://mapaelectoral.es/actualidad/escanos-en-el-filo-29n/) | Seis escaños que se decidieron por menos de mil votantes | gráfico |
| 2026-10-22 | [`casas-vacias-segundas-residencias`](https://mapaelectoral.es/actualidad/casas-vacias-segundas-residencias/) | En 4.441 municipios hay más casas sin vecinos que con ellos | gráfico |
| 2026-10-22 | [`vox-barrios-obreros-clase-29n`](https://mapaelectoral.es/actualidad/vox-barrios-obreros-clase-29n/) | Vox no gana en los barrios obreros: saca casi lo mismo donde viven peones que donde viven directivos, y el que sube es el PSOE | primer gráfico de la pieza |
| 2026-10-22 | [`termometro-temas-inmigracion-29n`](https://mapaelectoral.es/actualidad/termometro-temas-inmigracion-29n/) | La inmigración preocupa más, salvo a los votantes de Vox | gráfico |
| 2026-10-22 | [`inmigracion-preocupa-voto-vox-29n`](https://mapaelectoral.es/actualidad/inmigracion-preocupa-voto-vox-29n/) | Donde más preocupa la inmigración, más votó Vox, salvo en Cataluña | gráfico |
| 2026-10-22 | [`frontera-renta-pp-junts-pnv-29n`](https://mapaelectoral.es/actualidad/frontera-renta-pp-junts-pnv-29n/) | El PP ya gana a Junts en seis de cada diez barrios catalanes | gráfico |
| 2026-10-22 | [`polaritzacio-girona`](https://mapaelectoral.es/actualidad/polaritzacio-girona/) | A Girona el vot independentista va del 4% al 75% segons la secció | primer gráfico de la pieza |
| 2026-10-22 | [`girona-1936-participacio`](https://mapaelectoral.es/actualidad/girona-1936-participacio/) | El 1936 Salt votava més que avui: 76 % de participació, contra el 55 % del 23J | primer gráfico de la pieza |
| 2026-10-22 | [`capitales-partidas-por-barrios`](https://mapaelectoral.es/actualidad/capitales-partidas-por-barrios/) | Sevilla vota por barrios y Lugo, mezclada: el índice que mide qué capitales están partidas por el voto | primer gráfico de la pieza |
| 2026-10-22 | [`republica-mapa-1936-hoy`](https://mapaelectoral.es/actualidad/republica-mapa-1936-hoy/) | El mapa de 1936 apenas se parece al de hoy: 1.545 pueblos que votaron a las derechas eligen ahora a la izquierda | primer gráfico de la pieza |
| 2026-10-21 | [`vox-pp-senado-pacto-29n`](https://mapaelectoral.es/actualidad/vox-pp-senado-pacto-29n/) | PP y Vox negocian el Senado: con los votos de 2023, sumar a Vox le devolvería a la derecha 19 provincias frente a la lista de PSOE y Frente Amplio | gráfico |
| 2026-10-21 | [`barrios-donde-vota-menos-de-la-mitad`](https://mapaelectoral.es/actualidad/barrios-donde-vota-menos-de-la-mitad/) | A seis semanas del 29N: en 534 barrios de España no votó ni la mitad del censo, y tres de cada cuatro están entre los más pobres | gráfico |
| 2026-10-21 | [`calle-que-parte-madrid`](https://mapaelectoral.es/actualidad/calle-que-parte-madrid/) | A cinco semanas del 29N: en la calle de los Hermanos García Noblejas, en Madrid, PP y PSOE se cambian de acera 12 veces, y el PP siempre gana en el lado con más renta | gráfico |
| 2026-10-20 | [`senado-29n`](https://mapaelectoral.es/actualidad/senado-29n/) | El Senado de 2023: 120 senadores para el PP con un tercio de los votos | gráfico |
| 2026-10-20 | [`frente-amplio-podemos-madrid-escanos-29n`](https://mapaelectoral.es/actualidad/frente-amplio-podemos-madrid-escanos-29n/) | Delgado contra Montero en Madrid: con los votos de 2023, Podemos necesitaría uno de cada cinco votos de Sumar para sacar escaño | gráfico |
| 2026-10-20 | [`psoe-cinco-barrios-ceuta`](https://mapaelectoral.es/actualidad/psoe-cinco-barrios-ceuta/) | Los 5 barrios de España donde el PSOE saca más del 86% de los votos: todos están en Ceuta (y dónde no llega al 2,5%) | gráfico |
| 2026-10-20 | [`pp-cinco-pueblos-galicia`](https://mapaelectoral.es/actualidad/pp-cinco-pueblos-galicia/) | Los 5 pueblos de España donde el PP saca hasta el 81,5% de los votos: todos en Galicia (y los dos rincones vascos donde no tuvo ni un voto) | gráfico |
| 2026-10-20 | [`vox-cinco-barrios-el-ejido-ceuta`](https://mapaelectoral.es/actualidad/vox-cinco-barrios-el-ejido-ceuta/) | Los 5 barrios de España donde Vox saca más del 39% de los votos: El Ejido, Ceuta y el campo de Murcia (y los pueblos vascos donde no tuvo ni un voto) | gráfico |
| 2026-10-20 | [`sumar-cinco-pueblos-marinaleda`](https://mapaelectoral.es/actualidad/sumar-cinco-pueblos-marinaleda/) | Los 5 pueblos de España donde Sumar saca más del 52% de los votos: Marinaleda, Trebujena y una pedanía de Córdoba (y dónde no llega al 0,5%) | gráfico |
| 2026-10-20 | [`bildu-cinco-pueblos-lizartza`](https://mapaelectoral.es/actualidad/bildu-cinco-pueblos-lizartza/) | Los 5 pueblos donde EH Bildu saca más del 68% de los votos: de Lizartza a Goizueta (y los barrios de Getxo donde no llega al 1%) | gráfico |
| 2026-10-20 | [`pnv-cinco-pueblos-bermeo`](https://mapaelectoral.es/actualidad/pnv-cinco-pueblos-bermeo/) | Los 5 pueblos donde el PNV saca más del 52% de los votos: Bermeo y la costa de Bizkaia (y los barrios de Errenteria donde no llega al 8%) | gráfico |
| 2026-10-20 | [`cc-cinco-barrios-la-orotava`](https://mapaelectoral.es/actualidad/cc-cinco-barrios-la-orotava/) | Los 5 barrios de Canarias donde Coalición Canaria saca más del 42%: El Paso y La Orotava (y el Gáldar de su nuevo socio, donde no llega al 2%) | gráfico |
| 2026-10-20 | [`erc-cinco-pueblos-blancafort-flix`](https://mapaelectoral.es/actualidad/erc-cinco-pueblos-blancafort-flix/) | Los 5 pueblos donde ERC saca más del 35% de los votos: Blancafort, Flix y Tortosa (y el barrio de Tarragona donde no tuvo ni un voto) | gráfico |
| 2026-10-20 | [`junts-cinco-pueblos-amer`](https://mapaelectoral.es/actualidad/junts-cinco-pueblos-amer/) | Los 5 pueblos donde Junts saca más del 40% de los votos: encabeza Amer, el de Puigdemont (y los barrios del área de Barcelona donde no tuvo ni un voto) | gráfico |
| 2026-10-20 | [`bng-cinco-pueblos-allariz`](https://mapaelectoral.es/actualidad/bng-cinco-pueblos-allariz/) | El BNG solo ganó en una sección de España: los 5 pueblos donde más le votan, de Vilar de Santos a Allariz (y los de Ourense donde no llega al 2%) | gráfico |
| 2026-10-20 | [`municipios-izquierda-1977-derecha-2023`](https://mapaelectoral.es/actualidad/municipios-izquierda-1977-derecha-2023/) | Con el PSOE andaluz en mínimos: Sevilla, Jerez y otros 170 municipios que votaron a la izquierda en todas las generales de 1977 a 2008 dieron en 2023 más votos a PP y Vox | gráfico |
| 2026-10-20 | [`barrios-pobres-derecha-ricos-izquierda`](https://mapaelectoral.es/actualidad/barrios-pobres-derecha-ricos-izquierda/) | Vox busca el voto de los barrios obreros: en la Región de Murcia, nueve de cada diez secciones pobres ya votan más a PP y Vox que a PSOE y Sumar | gráfico |
| 2026-10-17 | [`pactos-izquierda-mapa-final-29n`](https://mapaelectoral.es/actualidad/pactos-izquierda-mapa-final-29n/) | Frente Amplio y Podemos solo irán juntos en cinco provincias: en las otras 47, Sumar sacó 26 de sus 31 diputados en 2023 | gráfico |
| 2026-10-17 | [`canarias-unidad-pueblo-canario-29n`](https://mapaelectoral.es/actualidad/canarias-unidad-pueblo-canario-29n/) | Nueva Canarias, Podemos, IU y Sumar se unen en Canarias: con los votos de 2023, la suma habría pasado de uno a tres diputados | gráfico |
| 2026-10-15 | [`precio-del-escano-29n`](https://mapaelectoral.es/actualidad/precio-del-escano-29n/) | Un diputado cuesta 25.300 votos en Teruel y 97.500 en Madrid: el precio del escaño, provincia a provincia | primer gráfico de la pieza |
| 2026-10-15 | [`votos-sin-escano-29n`](https://mapaelectoral.es/actualidad/votos-sin-escano-29n/) | 1,9 millones de votos no eligieron a nadie en 2023: en Teruel, Lleida y Soria, uno de cada tres | primer gráfico de la pieza |
| 2026-10-14 | [`ultimo-escano-29n`](https://mapaelectoral.es/actualidad/ultimo-escano-29n/) | Qué provincias pueden decidir el 29N: en 17, el último escaño se resolvió en 2023 por menos de 5.000 votos | primer gráfico de la pieza |
| 2026-10-14 | [`izquierda-dividida-29n`](https://mapaelectoral.es/actualidad/izquierda-dividida-29n/) | Dónde puede costar más la división a la izquierda: en ocho provincias, Sumar ganó o perdió un escaño en 2023 por menos de 5.000 votos | primer gráfico de la pieza |
| 2026-10-13 | [`aceituna-de-mesa-pueblos`](https://mapaelectoral.es/actualidad/aceituna-de-mesa-pueblos/) | La aceituna de mesa, por debajo de coste: en sus dos grandes comarcas, el PP no ganó en ninguno de los 23 pueblos en 2023 | primer gráfico de la pieza |
| 2026-10-09 | [`ceuta-historia-electoral`](https://mapaelectoral.es/actualidad/ceuta-historia-electoral/) | Ceuta es uno de los dos sitios donde Vox ha ganado unas generales | primer gráfico de la pieza |
| 2026-10-09 | [`melilla-historia-electoral`](https://mapaelectoral.es/actualidad/melilla-historia-electoral/) | Melilla tuvo cuatro años un presidente con un solo escaño de 25 | primer gráfico de la pieza |
| 2026-10-09 | [`izquierda-del-psoe-secciones`](https://mapaelectoral.es/actualidad/izquierda-del-psoe-secciones/) | El espacio a la izquierda del PSOE fue el más votado en 9.810 secciones en 2015; en 2023, en 182 | primer gráfico de la pieza |
| 2026-10-08 | [`plasencia-acierta-siempre`](https://mapaelectoral.es/actualidad/plasencia-acierta-siempre/) | 16 de 16: Plasencia ha votado al ganador en todas las elecciones generales desde 1977 | primer gráfico de la pieza |
| 2026-10-08 | [`municipios-fieles`](https://mapaelectoral.es/actualidad/municipios-fieles/) | Dos Hermanas ha votado al PSOE en las 16 generales; solo 11 pueblos, ninguno grande, lo han hecho con el PP | primer gráfico de la pieza |
| 2026-10-08 | [`ucd-ciudadanos-hundimiento`](https://mapaelectoral.es/actualidad/ucd-ciudadanos-hundimiento/) | De 5.990 municipios a 762 en tres años: así se hundió UCD, y así cayó Ciudadanos en solo seis meses | primer gráfico de la pieza |
| 2026-10-08 | [`avila-suarez-cds`](https://mapaelectoral.es/actualidad/avila-suarez-cds/) | Ávila dio a Suárez el 46 % en 1986, cuando su partido sacaba el 9 % en España | primer gráfico de la pieza |
| 2026-10-08 | [`trebujena-pce-sumar`](https://mapaelectoral.es/actualidad/trebujena-pce-sumar/) | Trebujena dio al PCE dos de cada tres votos en 1977 y aún da a Sumar uno de cada dos | primer gráfico de la pieza |
| 2026-10-08 | [`psoe-1982-mas-del-60`](https://mapaelectoral.es/actualidad/psoe-1982-mas-del-60/) | En 1982 el PSOE pasaba del 60 % en al menos 748 municipios; en 2023, en 67 | primer gráfico de la pieza |
| 2026-10-08 | [`nunca-gano-la-derecha`](https://mapaelectoral.es/actualidad/nunca-gano-la-derecha/) | Barcelona, Terrassa o Dos Hermanas: 864 municipios donde la derecha estatal nunca ha ganado unas generales | primer gráfico de la pieza |
| 2026-10-08 | [`mont-roig-municipio-cambiante`](https://mapaelectoral.es/actualidad/mont-roig-municipio-cambiante/) | Siete partidos distintos han ganado en Mont-roig del Camp: ha cambiado 11 veces de ganador en 16 generales | primer gráfico de la pieza |
| 2026-10-08 | [`baltar-censo-y-participacion`](https://mapaelectoral.es/actualidad/baltar-censo-y-participacion/) | En Baltar votó el 16 % en 1979; hoy vota el 79 %. La participación imposible del interior gallego | primer gráfico de la pieza |
| 2026-10-08 | [`europeas-arona`](https://mapaelectoral.es/actualidad/europeas-arona/) | En Arona votó uno de cada cinco electores en las europeas de 2014 | primer gráfico de la pieza |
| 2026-10-08 | [`euskadi-empate-a-tres`](https://mapaelectoral.es/actualidad/euskadi-empate-a-tres/) | Tres partidos en 1,3 puntos: el empate a tres de Euskadi en 2023 no tiene precedentes | primer gráfico de la pieza |
| 2026-10-08 | [`voto-en-blanco`](https://mapaelectoral.es/actualidad/voto-en-blanco/) | El voto en blanco se multiplicó por seis entre 1977 y 2000, y desde entonces se ha reducido a la mitad | primer gráfico de la pieza |
| 2026-10-08 | [`psa-andalucistas-1979`](https://mapaelectoral.es/actualidad/psa-andalucistas-1979/) | Antes de Teruel Existe: los cinco diputados andalucistas de 1979 y el 19,7 % de Cádiz | primer gráfico de la pieza |
| 2026-10-08 | [`censo-electoral-desde-1977`](https://mapaelectoral.es/actualidad/censo-electoral-desde-1977/) | De 23,6 a 35,1 millones: el censo electoral ha crecido un 49 % desde 1977 | primer gráfico de la pieza |
| 2026-10-08 | [`europeas-solo-con-municipales`](https://mapaelectoral.es/actualidad/europeas-solo-con-municipales/) | Las europeas solo superan el 60 % de participación cuando coinciden con las municipales | primer gráfico de la pieza |
| 2026-10-08 | [`votar-en-noviembre`](https://mapaelectoral.es/actualidad/votar-en-noviembre/) | El 29N repite mes con mal recuerdo: el último noviembre dejó la participación más baja de la democracia | primer gráfico de la pieza |
