# Verificación automática de las piezas

Regla de Nacho (3-11-2026, tras los nueve fallos de la previa de EE. UU.): **ninguna pieza se fusiona sin**

1. la revisión de un **hilo editor separado**, antes de fusionar, y
2. esta **comprobación automática**, que la GitHub Action «Verificar piezas» pasa en cada PR. Si sale en rojo, no se fusiona.

Se ejecuta a mano, desde la raíz, igual que en el PR:

```
python3 src/verificar_piezas.py                      # las piezas que cambian respecto a origin/main
python3 src/verificar_piezas.py --slug <slug>        # una pieza entera
python3 src/verificar_piezas.py --plantilla <slug>   # esqueleto de la declaración, con las cifras pendientes
```

## Qué comprueba

En cada pieza de Actualidad o Internacional que el PR crea o cambia (su `<slug>.html`, su `index.html`, su entrada en `construir.py`, su imagen o su declaración):

| | Error (bloquea) | Aviso (revisar a mano) |
|---|---|---|
| **Cifras** | Cifra de un párrafo nuevo o cambiado sin declarar; cálculo que no da la cifra del texto; frase declarada que ya no está; cifra del titular o la entradilla que no aparece en el cuerpo | |
| **Enlaces** | Enlace interno a una página que no existe; externo que da 404, 410 o un dominio inexistente | Web que no deja entrar a robots (403, 5xx, tiempo agotado) |
| **Imágenes** | `<img>`, foto de cabecera, Open Graph o `img/compartir/actualidad-<slug>.jpg` que falta, está vacía o no es una imagen | |
| **Internacional** | Partidos, líderes o comunidades españolas (no basta «elecciones generales», que también las hay en otros países), «29N», fuentes españolas (Interior, INE) o enlaces a municipios, generales o encuestas españolas, en el texto o en los datos del mapa | |
| **Actualización** | Pieza publicada que cambia de texto sin cambiar `actualizado` | |
| **Redondeo** | | Diferencia en puntos a ±0,1 de la resta de las cifras que ve el lector en la misma frase, o en la fila de la tabla que la frase nombra («nov. 2019» ↔ «noviembre de 2019»). La cifra buena es la del dato sin redondear: «14,0 puntos» con 62,9 % y 77,0 % es correcto si sale de 76,992 − 62,946. Las diferencias se calculan siempre desde el dato bruto, nunca restando cifras mostradas; si la pieza la declara en `cifras`, la Action la comprueba contra el dato y no avisa. La misma cifra con distinto redondeo en el texto y en la fila de una tabla con ese nombre («88 %» y «87,8 %» para Nevada) |
| **Tablas** | Columna «Diferencia» que se separa más de una décima de la resta de las dos de su izquierda (a una décima es aviso: puede venir del dato sin redondear); fila o columna «Total» (o «España», «Comunitat»…) que no es la suma de las demás | Filas de recuentos que suman distinto que la mayoría (un municipio que falta en 1977); «0,0» en una tabla que marca con «–» lo que no tiene dato |
| **Navegador** | Error de JavaScript, fichero del propio sitio que no carga o scroll horizontal al abrir la pieza a 390 px | Sin Node o sin Playwright no se abre (aviso) |

Los controles de redondeo, tablas y navegador (`src/controles_calidad.py` y `src/verificar_navegador.mjs`) salen de los fallos que el repaso diario encontró en piezas ya fusionadas. En una pieza ya publicada solo miran los párrafos y las tablas nuevos o cambiados. Una frase o una tabla que los dispara con motivo se declara en `"ignorar_calidad": [{"texto": "…", "motivo": "…"}]` (para una tabla, basta un trozo de su primera fila).

Cuentan como cifras los números (también «once», «nueve»…) de los párrafos con `data-tipo`, el titular, la entradilla, los intertítulos y los pies de gráfico. No cuentan los años, las fechas, las horas, los ordinales ni códigos como KY-6. En una pieza ya publicada solo se exigen las cifras de los párrafos nuevos o cambiados.

## La declaración: `actualidad/verificacion/<slug>.json`

```json
{
  "pieza": "eeuu-elecciones-medio-mandato-mapa",
  "cifras": [
    {"texto": "en 284 distritos el ganador sacó 20 puntos o más", "cifra": "284",
     "calculo": "sum(d[7] is not None and abs(d[7]) >= 20 for d in DIS)"},
    {"texto": "su saldo ha sido de 25,7 escaños menos", "cifra": "25,7", "calculo": "-mean([h[2] for h in HIS])"},
    {"texto": "todos por menos de 4 puntos", "condicion": "all(m < 4 for m in ...)"}
  ],
  "externas": [
    {"texto": "más de 52,8 millones de estadounidenses ya han votado",
     "fuente": "https://election.lab.ufl.edu/early-vote/2026-general-election-early-vote/"}
  ],
  "ignorar": [
    {"texto": "cerca de 20 mítines telefónicos", "motivo": "cita literal de la fuente de EFE"}
  ],
  "permitir_espana": [
    {"texto": "hora peninsular española", "motivo": "la guía da las horas de cierre en hora de España"}
  ]
}
```

- **`cifras`**: la cifra sale de nuestros datos. `texto` es un trozo literal de la pieza que contiene la cifra; `cifra`, cómo aparece escrita («52,8 millones», «once»; si el trozo solo tiene un número, se puede omitir); `calculo`, una expresión de Python que la recalcula. El resultado tiene que coincidir con el redondeo del texto (25,65 vale para «25,7»; 6,7 vale para «casi 7»). Con `condicion` en vez de `cifra` y `calculo`, la expresión tiene que dar `True`.
  - Datos disponibles: cada `const`/`let` del `<script>` de la pieza, por su nombre (`DIS`, `HIS`, `MAPAS`…), que son los mismos datos que dibujan el mapa y los gráficos; también `D['NOMBRE']`.
  - Ficheros del repositorio: `csv('ruta/fichero.csv')` (lista de filas, con los números ya convertidos) y `json('ruta/fichero.json')`.
  - Funciones: `len`, `sum`, `min`, `max`, `abs`, `round`, `sorted`, `mean`, `median`, `any`, `all`, `set`, `dict`, `zip`…
- **Cuidado con el redondeo de los datos**: si la cifra depende de un umbral («menos de 5 puntos») y los datos de la pieza están redondeados, un caso en el límite puede caer del lado equivocado. Ejemplo: en la previa de EE. UU., Colorado 3 figura con 5,0 en `DIS`, pero Hurd ganó por 4,98 puntos según el Clerk; «37 distritos por menos de 5 puntos» es correcto. Esas cifras van en `externas`, con la fuente oficial sin redondear, no recalculadas desde los datos redondeados.
- **`externas`**: la cifra viene de otra fuente (encuestas, agencias, informes oficiales). `fuente` tiene que ser un enlace que esté en la pieza (en el texto o en «Método y fuentes»). No se puede recalcular: el informe la lista para que el editor la compruebe a mano.
- **`ignorar`**: números que no son datos (una cita literal, «dos años después»…), con su `motivo`.
- **`permitir_espana`**: en una pieza internacional, una mención española justificada, con su `motivo`.

Si el texto cambia y una frase declarada deja de aparecer, la comprobación falla: obliga a revisar la cifra otra vez.

## El flujo

1. Escribe la pieza y constrúyela como siempre.
2. `python3 src/verificar_piezas.py --plantilla <slug>` crea o completa la declaración con cada cifra pendiente; rellena el `calculo` o pásala a `externas` o `ignorar`.
3. `python3 src/verificar_piezas.py --slug <slug>` hasta que salga en verde; abre el PR.
4. El hilo editor revisa la pieza y la lista de cifras externas del informe de la Action.
5. Con la Action en verde y el visto bueno del editor, Nacho fusiona.
