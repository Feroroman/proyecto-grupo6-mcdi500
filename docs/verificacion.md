# Verificación y trazabilidad · Fase 3

Generado automáticamente por `scripts/evidencias.py` el 24-09-2026 08:34.
Todas las cifras de este documento salen del repositorio en el momento de generarlo; ninguna se transcribe de memoria.

## 1. Pruebas automatizadas

| Suite | Qué cubre | Comando | Resultado |
|---|---|---|---|
| `tests/test_proyecto.py` | Fase 1 · clase ProyectoF1 | `python tests/test_proyecto.py` | **OK** · 8/8 pruebas superadas |
| `tests/test_pipeline.py` | Fase 2 · funciones del pipeline | `python tests/test_pipeline.py` | **OK** · 11/11 pruebas superadas |
| `tests/test_pipeline_clases.py` | Fase 3 · jerarquía de clases | `python tests/test_pipeline_clases.py` | **NO EXISTE** · — |
| `tests/test_algoritmos.py` | Fase 3 · algoritmos recursivos | `python tests/test_algoritmos.py` | **NO EXISTE** · — |
| `tests/test_complejidad.py` | Fase 3 · medición de complejidad | `python tests/test_complejidad.py` | **NO EXISTE** · — |

Suites ejecutadas correctamente: **2 de 5**.

## 2. Historial del repositorio

- Commits totales en la rama actual: **34**
- Ramas: `fase3-sebastian-informe`, `main`, `origin`, `origin/main`

| Autor | Commits |
|---|---|
| Fernanda Ovalle Román | 16 |
| Sebastian Cajales Cid | 7 |
| César Lorca Bacián | 5 |
| Sebastian Cajales | 2 |
| jaossandon | 2 |
| Feroroman | 1 |
| sebastiancajalescid | 1 |

Últimos commits:

```
f804b40 Sebastian Cajales Cid feat(f3): generador automatico de evidencias y verificacion
65ae8c7 Sebastian Cajales docs: versiona copias ejecutadas de notebooks F1 y F2 excluidas de nbstripout
3be3202 Sebastian Cajales docs: mueve el borrador de exploracion a docs/evidencias
d6dec22 Sebastian Cajales Cid correccion nombre de los archivos de evaluacion
cb11a6c Sebastian Cajales Cid Fusion Documentos descritos en Anexo D de informe de evalucion  en PDF
a405527 Fernanda Ovalle Román Merge branch 'main' of https://github.com/Feroroman/proyecto-grupo6-mcdi500
ef09de9 Sebastian Cajales Cid Cambio de nombre de evaluacion, limpieza de archivos temporales, inclusion de nuevo integrante a README.md
6a0f17f jaossandon Revisión y actualización de commits
11a4f0b jaossandon Correción de informe realizado sobre 5 puntos pendientes
575828a Fernanda Ovalle Román docs: reejecuta notebooks F1 y F2 y actualiza bitacora y figuras
e2bb5b1 Feroroman Remove kernel restart instruction from notebook
ad03375 Sebastian Cajales Cid docs: Nombre de nuevo integrante añadido
```

## 3. Arquitectura de módulos

Leída directamente del código de `src/` con `ast`, no escrita a mano.

| Módulo | Propósito | Clases | Funciones públicas | Depende de | Líneas |
|---|---|---|---|---|---|
| `bitacora.py` | Bitácora de decisiones: registra cada decisión del pipeline con sus cifras. | — | 2 | — | 29 |
| `escalado.py` | Fase 2 · Paso 9: escalamiento. Tres escaladores implementados con NumPy/pandas. | — | 4 | — | 59 |
| `exploracion.py` | Fase 2 · Paso 6: medir antes de tocar nada. | — | 3 | — | 65 |
| `limpieza.py` | Fase 2 · Paso 7: limpieza e imputación. | — | 6 | — | 87 |
| `proyecto.py` | Fase 1 · Configuración del proyecto como objeto. | `ProyectoF1` | 5 | — | 155 |
| `transformacion.py` | Fase 2 · Paso 8: transformación por tipo de variable. | — | 5 | — | 61 |
| `validacion.py` | Fase 2 · Paso 10: validar es demostrar, no afirmar. | — | 2 | — | 39 |
| `validar_dataset.py` |  | — | 3 | — | 136 |

Dependencias internas (lo que va en el diagrama del informe):

```
  (los módulos son independientes entre sí)
```

## 4. Archivos versionados

| Carpeta | Archivos |
|---|---|
| `(raíz)` | 4 |
| `data` | 2 |
| `docs` | 12 |
| `notebooks` | 5 |
| `scripts` | 1 |
| `src` | 9 |
| `tests` | 2 |

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
