# Registro de cambios · de los datos del modelo a los datos del lector

Fase 4 · Fernanda Ovalle Román · MCDI500 · Grupo 6

Este documento responde a una pregunta que la Fase 4 no puede esquivar: si el
conjunto que entregó la Fase 2 está optimizado para el análisis numérico, ¿sobre
qué datos se construyen las visualizaciones y las tablas que debe leer una
persona?

La respuesta corta es que no hace falta deshacer nada. La larga ocupa el resto
de este documento, porque la razón es una propiedad del diseño del pipeline que
conviene dejar por escrito.

---

## 1 · El problema

El archivo `data/processed/titulados_2025_pregrado_univ_limpio.csv` tiene
105.060 filas y **84 columnas**. De esas 84, cuarenta y una existen para que un
modelo las consuma y estorban a cualquiera que quiera leerlas:

| Qué son | Cuántas | Por qué no se pueden leer |
|---|---|---|
| Columnas `_esc` | 3 | `dur_total_carr_esc = -0,43` no significa nada en semestres. El escalador robusto llevó la mediana a 0 y el rango intercuartílico a 1. |
| Columnas `_ord` | 2 | `rango_edad_ord = 2` es un entero sin etiqueta; el lector necesita «25 a 29 años». |
| Columnas one-hot | 36 | Cinco variables nominales se abrieron en 36 columnas de ceros y unos. Un gráfico de barras por jornada no se arma con cuatro columnas binarias. |

Hay además dos codificaciones que sí están en las columnas originales pero que
no se pueden graficar tal cual:

- `gen_alu` vale **1 o 2**. Un eje que diga «1» y «2» no comunica nada.
- `rango_edad` y `nivel_carrera_1` son texto. Pandas las ordena
  alfabéticamente, de modo que «18 a 24» queda después de «15 a 17» por
  casualidad y «50 y más» cae en medio de la serie.

---

## 2 · El hallazgo: el pipeline fue no destructivo

La hipótesis de partida era que la Fase 4 tendría que **invertir** las
transformaciones de la Fase 2: desescalar, decodificar, recomponer las
categóricas desde las columnas one-hot. Esa inversión no fue necesaria, y la
comprobación es directa.

El pipeline de la Fase 2 **nunca reemplazó una columna**: siempre agregó una
nueva al lado. `EscaladorRobusto` escribe en `dur_total_carr_esc` y deja intacta
`dur_total_carr`. `CodificadorOrdinal` escribe en `rango_edad_ord` y deja
intacta `rango_edad`. `AgrupadorRaras` escribe en `nomb_carrera_agrupada` y deja
intacta `nomb_carrera`.

La consecuencia es que las columnas originales siguen presentes en el archivo
limpio, con una sola excepción documentada. La aritmética cierra:

```
 40 columnas que entregó la Fase 1
−  3 constantes eliminadas en la limpieza   (cat_periodo, tipo_inst_1, nivel_global)
───────────────────────
 37 columnas originales que sobreviven
+  6 nuevas no derivadas    (2 banderas de imputación, mes_titulacion,
                             edad_titulacion, nomb_carrera_agrupada, mujer)
+ 41 derivadas              (3 _esc + 2 _ord + 36 one-hot)
───────────────────────
 84 columnas del archivo limpio
```

Las tres columnas que sí desaparecieron no son una pérdida: tenían **un solo
valor** en todas las filas después del filtro de la Fase 1, de modo que no
distinguen a nadie de nadie. Ninguna transformación las tocó; la limpieza las
descartó por constantes, y queda constancia en `docs/bitacora.md`.

Por eso `src/interpretable.py` **no invierte nada**. Es una **selección**, no una
inversión: descarta las 41 derivadas y se queda con lo que ya estaba ahí.

Esto no es un detalle de implementación. Es la justificación de una decisión de
diseño que la Fase 2 tomó y que conviene poder defender: un pipeline que
sobrescribe sus entradas obliga a guardar el original aparte o a escribir código
de inversión que puede equivocarse. Uno que solo agrega columnas cuesta memoria
y no cuesta nada más.

---

## 3 · Qué hace exactamente `cargar_interpretable()`

Tres operaciones, en este orden:

**1 · Descarta las 41 derivadas.** `columnas_derivadas()` las identifica por su
forma, no por una lista escrita a mano: sufijo `_esc`, sufijo `_ord`, o prefijo
de una de las cinco nominales que se abrieron en one-hot. Si la Fase 2 agregara
otra columna escalada mañana, esta función la reconocería sin cambios.

**2 · Traduce `gen_alu` a una columna `sexo` legible.** El mapa es
`{1: "Hombre", 2: "Mujer"}`. No se adivinó: se verificó contra la columna
`mujer` que la Fase 2 derivó de `gen_alu`, en las dos direcciones. Las cifras
son 45.940 hombres y 59.120 mujeres, consistentes con el 56,3 % de mujeres que
registró la bitácora de la Fase 2. Una prueba automatizada lo comprueba en cada
ejecución (`test_el_sexo_coincide_con_la_columna_derivada_en_la_fase_2`).

**3 · Declara el orden de las dos ordinales.** `rango_edad` y
`nivel_carrera_1` pasan a ser `pd.Categorical` con el orden declarado en
`src/transformacion.py` — el mismo que usó la Fase 2 para codificarlas, no uno
nuevo. A partir de ahí, cualquier `groupby` o cualquier eje sale ordenado por
edad creciente y por nivel creciente, sin ordenar a mano en cada gráfico.

Resultado: **105.060 filas × 44 columnas** (43 que sobreviven de las 84, más
`sexo`).

---

## 4 · Lo que no se revierte, y por qué

Tres cosas quedan como están. Las tres son decisiones, no omisiones.

**La imputación no se deshace.** Las 13.396 filas con `anio_ing_carr_ori`
imputado por mediana siguen imputadas. Deshacerlo significaría devolver 13.396
nulos al conjunto y perder el 12,8 % de los datos en cualquier agregación por
año de ingreso. Lo que sí se conserva es la **bandera**
`anio_ing_carr_ori_imputada`, y `tablas.py` incluye una tabla dedicada a ella
(`tabla_imputacion`) precisamente para que el informe pueda declarar cuánto de
cada grupo es dato observado y cuánto es dato imputado.

Esto importa más de lo que parece. La imputación **no está repartida al azar**:
el 75,9 % de los titulados a distancia tiene el año de ingreso imputado, contra
el 1,5 % de los diurnos. Cualquier conclusión sobre modalidad que use el año de
ingreso está mirando, en buena medida, una mediana que pusimos nosotros. Una
prueba deja constancia de esa concentración
(`test_la_imputacion_se_concentra_fuera_de_la_jornada_diurna`), de modo que si
una revisión futura del pipeline la cambiara, la suite lo diría.

**Las 3 filas duplicadas no vuelven.** Eran duplicados exactos: 0,003 % del
conjunto. No hay nada que recuperar.

**`nomb_carrera_agrupada` se conserva junto a `nomb_carrera`.** La original
tiene 1.096 categorías y la agrupada 129, con las 968 menos frecuentes bajo la
etiqueta «OTRA». Las dos sirven para cosas distintas: la agrupada para
cualquier gráfico que no pueda mostrar mil barras, la original para responder
por una carrera concreta. Descartar cualquiera de las dos sería perder una
pregunta que el análisis puede querer hacer.

---

## 5 · Cómo se usa

```python
from src.interpretable import cargar_interpretable, resumen_interpretable
from src.tablas import todas

df = cargar_interpretable()        # 105.060 × 44, listo para graficar
print(resumen_interpretable(df))   # control rápido de forma y categorías

tablas = todas(df)                 # las seis tablas agregadas, todas con el n
```

Si el archivo limpio no existe, `cargar_interpretable()` lanza
`FileNotFoundError` con el mensaje que indica ejecutar antes los notebooks de
las Fases 1 y 2. Es deliberado: un `None` silencioso o un DataFrame vacío
produciría gráficos vacíos que nadie notaría hasta el informe.

Las seis tablas de `src/tablas.py` **llevan todas el tamaño del grupo**. No es
un adorno: una diferencia de dos semestres entre dos grupos significa algo
distinto si los grupos tienen 40.000 y 38.000 filas que si tienen 12 y 9. La
tabla anidada incluye además una bandera `suficiente`, que marca como
insuficientes las celdas con menos de 100 registros — el mismo umbral que usó
la Fase 2 para agrupar carreras raras y el mismo que usa `explorar_con_poda` en
la Fase 3 como soporte mínimo.

---

## 6 · Verificación

`tests/test_interpretable.py` · **32 pruebas** en cuatro clases:

| Clase | Qué cubre |
|---|---|
| `TestInterpretableCasoNormal` | Forma, columnas descartadas, mapa de sexo contrastado contra la Fase 2, orden de las ordinales |
| `TestTablasCasoNormal` | Las seis tablas; que todas traigan el n; que los porcentajes sumen 100 |
| `TestCasoLimite` | Grupos de una sola fila, columnas constantes, celdas bajo el soporte mínimo |
| `TestCasoExcepcion` | Archivo inexistente, columna inexistente, DataFrame vacío |

Se ejecutan con el resto de la suite:

```
python -m unittest discover -s tests -v
```
