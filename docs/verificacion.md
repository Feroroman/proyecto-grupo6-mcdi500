# Registro de verificación

Trazabilidad del proceso de verificación del código: qué se verificó, cómo, cuándo y con qué resultado.
Se actualiza en cada ejecución completa antes de un commit de entrega.

| Fecha | Qué se verificó | Comando / procedimiento | Resultado | Evidencia |
|---|---|---|---|---|
| 2026-09-12 | Funciones del pipeline F2 (src/exploracion, limpieza, transformacion, escalado, validacion): casos normales, límite y excepciones | `python tests/test_pipeline.py` | 11/11 pruebas superadas | Anexo C del informe; salida en notebooks/F2 (celda 17) |
| 2026-09-12 | Clase ProyectoF1 y validador (src/proyecto, src/validar_dataset): filtro, subconjunto, README, estructura, excepciones | `python tests/test_proyecto.py` | 8/8 pruebas superadas | Anexo C del informe |
| 2026-09-12 | Notebook F1 completo con el kernel del proyecto | Kernel → Restart Kernel and Run All Cells | 8 celdas de código sin errores; subconjunto 105.063 × 40 (55,8 MB); validador OK | docs/evidencias/F1_Definicion_ejecutado.pdf |
| 2026-09-12 | Notebook F2 completo (obtención → persistencia) | Kernel → Restart Kernel and Run All Cells | 18 celdas sin errores; 5 asserts del dataset final OK; propiedad del escalador OK; 105.060 × 84 guardado y releído | docs/evidencias/F2_Pipeline_ejecutado.pdf; docs/bitacora.md |
| 2026-09-12 | Resultados intermedios del pipeline (faltantes, atípicos, comparación de imputaciones y de escaladores) | Celdas 3–14 del notebook F2 con salida impresa y figuras | Cifras coincidentes con la bitácora y con el informe (cap. X) | docs/figuras/*.png; docs/bitacora.md |
| 2026-09-12 | Reproducibilidad del entorno | `python -m pip install -r requirements.txt`; `verificar_entorno()` en F1 | Kernel Python (mcdi500) dentro de .venv | Celda 2 del notebook F1 |
| 2026-09-12 | Integridad del repositorio | `git status` limpio; ningún CSV versionado; historial con mensajes por convención | 11 commits, 2 autores | GitHub: historial de main |

## Cómo repetir la verificación

```bash
source .venv/bin/activate
python tests/test_proyecto.py && python tests/test_pipeline.py
jupyter lab   # F1 y F2 con Restart Kernel and Run All Cells
git status    # working tree clean; sin .csv
```

Cada fila nueva debe citar el commit en que se hizo la verificación (`git log --oneline -1`).
