# Verificación y trazabilidad · Fase 3

Generado automáticamente por `scripts/evidencias.py` el 27-09-2026 22:53.
Todas las cifras de este documento salen del repositorio en el momento de generarlo; ninguna se transcribe de memoria.

## 1. Pruebas automatizadas

| Suite | Qué cubre | Comando | Resultado |
|---|---|---|---|
| `tests/test_proyecto.py` | Fase 1 · clase ProyectoF1 | `python tests/test_proyecto.py` | **OK** · 8/8 pruebas superadas |
| `tests/test_pipeline.py` | Fase 2 · funciones del pipeline | `python tests/test_pipeline.py` | **OK** · 11/11 pruebas superadas |
| `tests/test_pipeline_clases.py` | Fase 3 · jerarquía de clases | `python tests/test_pipeline_clases.py` | **OK** · 42/42 pruebas superadas |
| `tests/test_algoritmos.py` | Fase 3 · algoritmos recursivos | `python tests/test_algoritmos.py` | **OK** · 49/49 pruebas superadas |
| `tests/test_complejidad.py` | Fase 3 · medición de complejidad | `python tests/test_complejidad.py` | **OK** · OK |

Suites ejecutadas correctamente: **5 de 5**.

## 2. Historial del repositorio

- Commits totales en la rama actual: **67**
- Ramas: `fase3-sebastian-informe`, `main`, `origin`, `origin/fase3-cesar-algoritmos`, `origin/fase3-integracion`, `origin/fase3-patron-strategy`, `origin/fase3-sebastian-informe`, `origin/main`

| Autor | Commits |
|---|---|
| Fernanda Ovalle Román | 28 |
| Sebastian Cajales Cid | 14 |
| César Lorca Bacián | 10 |
| jaossandon | 5 |
| Feroroman | 4 |
| sebastiancajalescid | 3 |
| Sebastian Cajales | 2 |
| Cesar Antonio Lorca Bacian | 1 |

> **Atención:** hay más combinaciones nombre/correo que autores distintos, lo que significa que alguien commiteó con dos identidades:
> - `Cesar Antonio Lorca Bacian <154942382+cesarlorcabacian@users.noreply.github.com>`
> - `César Lorca Bacián <calorcab@gmail.com>`
> - `Fernanda Ovalle Román <p.ovalleroman@uandresbello.edu>`
> - `Feroroman <p.ovalleroman@uandresbello.edu>`
> - `Sebastian Cajales <s.cajalescid@uandresbello.edu>`
> - `Sebastian Cajales Cid <s.cajalescid@uandresbello.edu>`
> - `jaossandon <ossandonjorge81@gmail.com>`
> - `sebastiancajalescid <s,cajalescid@uandresbello.edu>`
> - `sebastiancajalescid <s.cajalescid@uandresbello.edu>`

Últimos commits:

```
8621a08 sebastiancajalescid Merge pull request #7 from Feroroman/fase3-patron-strategy
34c0f25 Fernanda Ovalle Román chore(f3): deja un solo informe en docs/
f2787cb Fernanda Ovalle Román test(f3): 24 pruebas del patron y suites descubribles por unittest
627f55e Fernanda Ovalle Román chore(f3): retira las marcas de referencia [cite: N] de los comentarios
5f343ab Fernanda Ovalle Román refactor(f3): la etapa de escalado delega en una estrategia intercambiable
8a912ba Fernanda Ovalle Román feat(f3): patron Strategy para el escalamiento, con fabrica de estrategias
d36f6db Feroroman Merge pull request #1 from Feroroman/fase3-sebastian-informe
0cbfd1e Sebastian Cajales Cid docs(f3): alinea informe institucional con rubrica oficial de Sumativa 2 y genera f3_s02_entregable_grupo6.pdf
d9601ab Sebastian Cajales Cid docs(f3): informe institucional final integrado, verificacion de 114 pruebas y figuras empiricas
8709a0e Sebastian Cajales Cid merge: integra origin/main con modulos de algoritmos, complejidad, pipeline y notebook F3
2ceb1ff sebastiancajalescid Merge pull request #6 from Feroroman/fase3-integracion
9d7c302 Fernanda Ovalle Román fix(f3): integra los modulos de Cesar y Jorge y ejecuta el notebook completo
```

## 3. Arquitectura de módulos

Leída directamente del código de `src/` con `ast`, no escrita a mano.

| Módulo | Propósito | Clases | Funciones públicas | Depende de | Líneas |
|---|---|---|---|---|---|
| `algoritmos.py` | Fase 3 · Algoritmos estructurados y recursivos. | — | 9 | — | 304 |
| `bitacora.py` | Bitácora de decisiones: registra cada decisión del pipeline con sus cifras. | — | 2 | — | 29 |
| `complejidad.py` | Fase 3 · Análisis de Complejidad y Rendimiento. | `MedidorComplejidad`, `TestMedidorComplejidad` | 11 | `algoritmos` | 215 |
| `escalado.py` | Fase 2 · Paso 9: escalamiento. Tres escaladores implementados con NumPy/pandas. | — | 4 | — | 59 |
| `escaladores.py` | Fase 3 · Patrón Strategy aplicado al escalamiento. | `EstrategiaEscalado`, `EstandarizacionZ`, `NormalizacionMinMax`, `EscaladoRobusto`, `Escalador` | 15 | — | 283 |
| `exploracion.py` | Fase 2 · Paso 6: medir antes de tocar nada. | — | 3 | — | 65 |
| `limpieza.py` | Fase 2 · Paso 7: limpieza e imputación. | — | 6 | — | 87 |
| `pipeline.py` | Fase 3 · Jerarquía de clases del pipeline de datos. | `Transformador`, `EliminadorDuplicados`, `CodigoAFaltante`, `ImputadorMedianaPorGrupo`, `EliminadorConstantes`, `CodificadorOrdinal`, `AgrupadorRaras`, `CodificadorOneHot`, `EscaladorPorEstrategia`, `EscaladorRobusto`, `Pipeline` | 8 | `escaladores` | 447 |
| `proyecto.py` | Fase 1 · Configuración del proyecto como objeto. | `ProyectoF1` | 5 | — | 155 |
| `transformacion.py` | Fase 2 · Paso 8: transformación por tipo de variable. | — | 5 | — | 61 |
| `validacion.py` | Fase 2 · Paso 10: validar es demostrar, no afirmar. | — | 2 | — | 39 |
| `validar_dataset.py` |  | — | 3 | — | 136 |

Dependencias internas (lo que va en el diagrama del informe):

```
  algoritmos.py  ──>  complejidad.py
  escaladores.py  ──>  pipeline.py
```

## 4. Archivos versionados

| Carpeta | Archivos |
|---|---|
| `(raíz)` | 4 |
| `data` | 2 |
| `docs` | 25 |
| `notebooks` | 5 |
| `scripts` | 2 |
| `src` | 13 |
| `tests` | 7 |

CSV versionados: **0** (correcto: ninguno).

## 5. Salida completa de las pruebas

### `tests/test_proyecto.py`

```
OK    test_excepciones
OK    test_filtro_conserva_solo_pregrado_universitario
OK    test_filtro_sin_coincidencias_devuelve_vacio
OK    test_generar_subconjunto_escribe_archivo
OK    test_readme_contiene_pregunta_e_integrantes
OK    test_subconjunto_existente_se_reutiliza_sin_original
OK    test_validador_detecta_separador_y_alertas
OK    test_verificar_estructura_detecta_faltantes

8/8 pruebas superadas
```

### `tests/test_pipeline.py`

```
OK    test_atipicos_ric_detecta_extremo
OK    test_atipicos_serie_vacia
OK    test_codigo_a_nulo_normal
OK    test_columna_sin_nulos_no_imputa_nada
OK    test_eliminar_duplicados_sin_duplicados
OK    test_escaladores_cumplen_propiedad
OK    test_excepciones
OK    test_imputar_mediana_crea_bandera
OK    test_one_hot_suma_uno
OK    test_ordinal_respeta_orden_declarado
OK    test_una_sola_categoria_one_hot

11/11 pruebas superadas
```

### `tests/test_pipeline_clases.py`

```
── Caso normal ─────────────────────────────────────────────
  OK    EliminadorDuplicados quita la fila repetida
  OK    EliminadorDuplicados no toca el original
  OK    CodigoAFaltante convierte los dos 1900 en NaN
  OK    CodigoAFaltante informa las cifras
  OK    CodigoAFaltante no toca el original
  OK    ImputadorMedianaPorGrupo no deja nulos
  OK    ImputadorMedianaPorGrupo deja la bandera
  OK    La bandera marca exactamente los 2 imputados
  OK    Las medianas quedan guardadas tras fit
  OK    EliminadorConstantes elimina 'constante'
  OK    EliminadorConstantes informa cuál eliminó
  OK    CodificadorOrdinal respeta el orden declarado
  OK    CodificadorOrdinal codifica el nivel más alto
  OK    AgrupadorRaras agrupa las 2 categorías raras
  OK    AgrupadorRaras conserva la frecuente
  OK    AgrupadorRaras no toca la columna original
  OK    CodificadorOneHot crea una columna por categoría
  OK    Cada fila suma exactamente 1 en el grupo one-hot
  OK    EscaladorRobusto deja mediana 0
  OK    EscaladorRobusto deja RIC 1
  OK    El pipeline ejecuta las 7 etapas
  OK    El resumen trae una fila por etapa
  OK    El resumen trae tiempo y memoria
  OK    etapa_dominante() devuelve una etapa real
  OK    El pipeline no modifica el DataFrame original
  OK    cifras() devuelve una tabla no vacía
  OK    La clase da el MISMO resultado que la función de la Fase 2

── Caso límite ─────────────────────────────────────────────
  OK    EliminadorDuplicados sobre una sola fila
  OK    CodigoAFaltante con cero coincidencias informa 0
  OK    AgrupadorRaras con una sola categoría no agrupa nada
  OK    ImputadorMediana sin nulos imputa 0 casos
  OK    Pipeline de una sola etapa funciona

── Caso excepción ──────────────────────────────────────────
  OK    apply() sin fit() lanza RuntimeError
  OK    fit() con algo que no es DataFrame lanza TypeError
  OK    Columna inexistente lanza KeyError
  OK    Escalar una columna de texto lanza TypeError
  OK    Ordinal con categoría fuera del orden lanza ValueError
  OK    One-hot con columna ausente lanza KeyError
  OK    Pipeline vacío lanza ValueError
  OK    Pipeline con algo que no es Transformador lanza TypeError
  OK    resumen() antes de ejecutar lanza RuntimeError
  OK    Escalar una columna sin dispersión lanza ValueError

────────────────────────────────────────────────────────────
42/42 pruebas superadas
```

### `tests/test_algoritmos.py`

```
── Caso normal ─────────────────────────────────────────────
  OK    merge_sort ordena correctamente
  OK    merge_sort no modifica la lista original
  OK    merge_sort registra profundidad cercana a log2(n)
  OK    quickselect encuentra el elemento en la posición 0
  OK    quickselect encuentra el elemento en la posición 1
  OK    quickselect encuentra el elemento en la posición 150
  OK    quickselect encuentra el elemento en la posición 299
  OK    quickselect no modifica la lista original
  OK    quickselect y ordenar dan el mismo cuantil q=0.0
  OK    quickselect y ordenar dan el mismo cuantil q=0.25
  OK    quickselect y ordenar dan el mismo cuantil q=0.5
  OK    quickselect y ordenar dan el mismo cuantil q=0.75
  OK    quickselect y ordenar dan el mismo cuantil q=1.0
  OK    quickselect visita muchísimos menos nodos que merge_sort
  OK    La poda encuentra exactamente los mismos hallazgos que la búsqueda completa
  OK    La poda visita menos nodos que la búsqueda completa
  OK    La poda registra las ramas que cortó
  OK    Los hallazgos vienen ordenados de mayor a menor mediana
  OK    Todos los hallazgos superan el umbral
  OK    Todos los hallazgos cumplen el soporte mínimo
  OK    La agregación anidada devuelve un grupo por combinación
  OK    La agregación trae la diferencia respecto del área
  OK    La agregación marca los grupos con soporte suficiente
  OK    El vespertino aparece por encima del promedio de su área
  OK    La agregación marca como insuficiente el grupo de 20 registros

── Caso límite ─────────────────────────────────────────────
  OK    merge_sort de una lista vacía
  OK    merge_sort de un solo elemento
  OK    merge_sort con todos los elementos idénticos
  OK    merge_sort de una lista ya ordenada
  OK    merge_sort de una lista al revés
  OK    quickselect con un solo elemento (caso base)
  OK    quickselect con todos los elementos idénticos
  OK    quickselect con valores negativos y extremos
  OK    cuantil de un solo elemento
  OK    Elementos idénticos no producen recursión profunda
  OK    Exploración sobre un DataFrame vacío no falla y no halla nada
  OK    Umbral inalcanzable: sin hallazgos y todo podado en la raíz
  OK    Soporte imposible: sin hallazgos
  OK    Exploración con un solo factor

── Caso excepción ──────────────────────────────────────────
  OK    quickselect de una lista vacía lanza ValueError
  OK    quickselect con k negativo lanza ValueError
  OK    quickselect con k fuera de rango lanza ValueError
  OK    cuantil con q mayor que 1 lanza ValueError
  OK    cuantil de una secuencia vacía lanza ValueError
  OK    Exploración sin factores lanza ValueError
  OK    Exploración con columna inexistente lanza KeyError
  OK    Exploración con respuesta inexistente lanza KeyError
  OK    Exploración con respuesta de texto lanza TypeError
  OK    Exploración con algo que no es DataFrame lanza TypeError

────────────────────────────────────────────────────────────
49/49 pruebas superadas
```

### `tests/test_complejidad.py`

```
....
----------------------------------------------------------------------
Ran 4 tests in 0.032s

OK
```
