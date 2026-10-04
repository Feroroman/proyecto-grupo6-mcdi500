"""Genera la copia ejecutada del cuaderno de la Fase 4.

    python scripts/exportar_evidencia_f4.py

El repositorio versiona dos copias de cada cuaderno, y la distinción es
deliberada. La copia de trabajo, en `notebooks/`, se versiona **sin salidas**:
un `.ipynb` guarda los resultados dentro del propio archivo, de modo que dos
integrantes que solo ejecutan el cuaderno ya producen versiones distintas y
provocan conflictos que Git no puede resolver, porque el formato es JSON. El
filtro `nbstripout` las limpia antes de cada commit.

La evidencia de la ejecución vive aparte, en `docs/evidencias/`, con el sufijo
`_ejecutado`. El archivo `.gitattributes` excluye ese sufijo del filtro:

    *.ipynb            filter=nbstripout
    *_ejecutado.ipynb  !filter

Este script ejecuta el cuaderno de principio a fin con un kernel limpio
—equivale a *Restart Kernel and Run All Cells*— y deja la copia ejecutada en
`.ipynb` y en `.html`, igual que las Fases 1 y 2.

Después comprueba lo que el informe necesita poder afirmar: que los contadores
de celda van del 1 al N sin saltos, prueba de que se ejecutó entero y en orden,
y no por partes.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ORIGEN = RAIZ / "notebooks/F4/F4_Visualizaciones_Comunicacion.ipynb"
DESTINO = RAIZ / "docs/evidencias/F4_Visualizaciones_Comunicacion_ejecutado.ipynb"
DESTINO_HTML = DESTINO.with_suffix(".html")

TIEMPO_MAXIMO = 1800  # segundos por celda; las figuras tardan


def main() -> int:
    try:
        import nbformat
        from nbconvert.preprocessors import ExecutePreprocessor
        from nbconvert import HTMLExporter
    except ImportError:
        print("Falta nbconvert. Instálalo dentro del entorno virtual:\n")
        print("    source .venv/bin/activate")
        print("    pip install nbconvert ipykernel\n")
        return 1

    if not ORIGEN.exists():
        print(f"No está {ORIGEN.relative_to(RAIZ)}")
        return 1

    nb = nbformat.read(ORIGEN, as_version=4)
    celdas = sum(1 for c in nb.cells if c.cell_type == "code")
    print(f"Cuaderno: {ORIGEN.relative_to(RAIZ)}")
    print(f"Celdas de código: {celdas}")
    print("\nEjecutando con un kernel limpio (equivale a Restart & Run All)...")

    t0 = time.perf_counter()
    try:
        ExecutePreprocessor(timeout=TIEMPO_MAXIMO, kernel_name="python3").preprocess(
            nb, {"metadata": {"path": str(RAIZ)}})
    except Exception as e:
        print(f"\nLa ejecución falló: {type(e).__name__}")
        print(f"{e}\n")
        print("La copia ejecutada NO se escribió. Corrige el cuaderno y repite.")
        return 1
    print(f"Terminó en {time.perf_counter() - t0:.0f} s")

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, DESTINO)

    cuerpo, _ = HTMLExporter().from_notebook_node(nb)
    DESTINO_HTML.write_text(cuerpo, encoding="utf-8")

    # ── Comprobación: la copia debe servir como evidencia ────────────────
    print("\nComprobando la copia ejecutada:")
    codigo = [c for c in nb.cells if c.cell_type == "code"]
    contadores = [c.get("execution_count") for c in codigo]
    con_salida = sum(1 for c in codigo if c.get("outputs"))

    problemas = []
    if None in contadores:
        problemas.append("hay celdas sin ejecutar")
    elif contadores != list(range(1, len(codigo) + 1)):
        problemas.append(f"los contadores no van de 1 a {len(codigo)}: {contadores}")

    print(f"  contadores de celda : 1 a {len(codigo)} sin saltos"
          if not problemas else f"  contadores de celda : {problemas[-1]}")
    print(f"  celdas con salida   : {con_salida} de {len(codigo)}")
    print(f"  tamaño del .ipynb   : {DESTINO.stat().st_size // 1024} KB")
    print(f"  tamaño del .html    : {DESTINO_HTML.stat().st_size // 1024} KB")

    print(f"\nEscrito:")
    print(f"  {DESTINO.relative_to(RAIZ)}")
    print(f"  {DESTINO_HTML.relative_to(RAIZ)}")

    if problemas:
        print("\nAVISO: " + "; ".join(problemas))
        return 1

    print("\nListo. Para versionarlo:")
    print("  git add docs/evidencias/F4_Visualizaciones_Comunicacion_ejecutado.*")
    print('  git commit -m "docs(f4): copia ejecutada del cuaderno de visualizaciones"')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
