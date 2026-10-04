"""Corrige la configuración de nbstripout en este clon del repositorio.

    python scripts/configurar_git.py

Cada integrante debe ejecutarlo una vez. Hay que explicar por qué.

El repositorio limpia las salidas de los cuadernos antes de cada commit, con el
filtro `nbstripout`. Es necesario: un `.ipynb` guarda los resultados dentro del
propio archivo, de modo que dos personas que solo ejecutan el cuaderno ya
producen versiones distintas, y Git no puede resolver esos conflictos porque el
formato es JSON.

Pero las copias ejecutadas de `docs/evidencias/` son la excepción: su contenido
ES la salida. Si el filtro también las limpia, el archivo que prueba que el
cuaderno se ejecutó queda sin ninguna prueba de que se ejecutó.

El `.gitattributes` versionado declara esa excepción. El problema es que
`nbstripout --install` escribe `*.ipynb filter=nbstripout` en
`.git/info/attributes`, un archivo **local y no versionado** que Git consulta
**antes** que `.gitattributes`. Gana el local, la excepción nunca se aplica, y
las copias ejecutadas se suben vacías sin que nadie lo note: el commit pasa sin
error y el archivo sigue ahí, solo que sin salidas.

Este script agrega la excepción a `.git/info/attributes` de este clon.

Para comprobarlo a mano, en cualquier momento:

    git check-attr filter -- docs/evidencias/F3_Algoritmos_Complejidad_ejecutado.ipynb

Debe decir `filter: unset`. Si dice `filter: nbstripout`, falta ejecutar esto.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ATRIBUTOS = RAIZ / ".git/info/attributes"
EXCEPCION = "*_ejecutado.ipynb -filter"

CABECERA = [
    "# nbstripout limpia las salidas de los cuadernos de trabajo.",
    "# Las copias ejecutadas de docs/evidencias/ quedan fuera: su contenido ES",
    "# la salida, y sin ella el archivo no prueba nada.",
]

MUESTRAS = [
    ("docs/evidencias/F3_Algoritmos_Complejidad_ejecutado.ipynb", "unset"),
    ("docs/evidencias/F4_Visualizaciones_Comunicacion_ejecutado.ipynb", "unset"),
    ("notebooks/F4/F4_Visualizaciones_Comunicacion.ipynb", "nbstripout"),
]


def filtro_de(ruta: str) -> str:
    r = subprocess.run(["git", "check-attr", "filter", "--", ruta],
                       cwd=RAIZ, capture_output=True, text=True)
    return r.stdout.strip().rsplit(": ", 1)[-1] if r.returncode == 0 else "?"


def main() -> int:
    if not (RAIZ / ".git").exists():
        print("Hay que ejecutarlo desde el repositorio.")
        return 1

    print("Antes:")
    for ruta, _ in MUESTRAS:
        print(f"  {filtro_de(ruta):<12} {ruta}")

    ATRIBUTOS.parent.mkdir(parents=True, exist_ok=True)
    lineas = (ATRIBUTOS.read_text(encoding="utf-8").splitlines()
              if ATRIBUTOS.exists() else [])

    if EXCEPCION in lineas:
        print(f"\nLa excepción ya estaba en {ATRIBUTOS.relative_to(RAIZ)}.")
    else:
        # La excepción va al final: dentro de un mismo archivo gana la última
        # regla que coincide.
        if not lineas or not lineas[0].startswith("#"):
            lineas = CABECERA + lineas
        lineas.append(EXCEPCION)
        ATRIBUTOS.write_text("\n".join(lineas) + "\n", encoding="utf-8")
        print(f"\nExcepción agregada a {ATRIBUTOS.relative_to(RAIZ)}")

    print("\nDespués:")
    fallos = []
    for ruta, esperado in MUESTRAS:
        real = filtro_de(ruta)
        ok = real == esperado
        print(f"  {real:<12} {ruta}" + ("" if ok else f"   <- se esperaba {esperado}"))
        if not ok:
            fallos.append(ruta)

    if fallos:
        print("\nAlgo no quedó bien. Revisa .gitattributes y .git/info/attributes.")
        return 1

    print("""
Listo.

Si ya habías subido una copia ejecutada vacía, hay que volver a agregarla para
que Git la guarde con sus salidas:

    git add -f docs/evidencias/*_ejecutado.ipynb
    git status --short          # debe aparecer como modificada
    git commit -m "docs: restaura las salidas de las copias ejecutadas"
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
