"""Fase 3 · Generador de evidencias para el informe.

Un solo comando produce todo lo que el informe necesita citar y que hoy se
recopila a mano:

  1. Ejecuta las tres suites de pruebas y captura su salida completa.
  2. Cuenta los commits del repositorio y los reparte por integrante.
  3. Lista las ramas y los archivos versionados de cada carpeta.
  4. Dibuja el diagrama de módulos de src/ a partir de los imports reales.
  5. Escribe todo en docs/verificacion.md con fecha y comando de cada prueba.

La ventaja sobre hacerlo a mano: las cifras del informe salen siempre del
repositorio en el momento de generarlas, y no de lo que alguien recordaba. Fue
exactamente ahí donde la Sumativa 1 perdió consistencia, con dos cifras
distintas de commits en el mismo documento.

Uso
---
    python scripts/evidencias.py

Se ejecuta desde la raíz del repositorio, con el entorno virtual activado.

Autoría: Sebastián Cajales Cid · MCDI500 · Fase 3
"""
from __future__ import annotations

import ast
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SUITES = [
    ("tests/test_proyecto.py", "Fase 1 · clase ProyectoF1"),
    ("tests/test_pipeline.py", "Fase 2 · funciones del pipeline"),
    ("tests/test_pipeline_clases.py", "Fase 3 · jerarquía de clases"),
    ("tests/test_algoritmos.py", "Fase 3 · algoritmos recursivos"),
    ("tests/test_complejidad.py", "Fase 3 · medición de complejidad"),
]


def correr(comando: List[str]) -> Tuple[int, str]:
    """Ejecuta un comando y devuelve (código de salida, salida combinada)."""
    try:
        r = subprocess.run(comando, capture_output=True, text=True, timeout=600)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, f"comando no encontrado: {comando[0]}"
    except subprocess.TimeoutExpired:
        return 124, "el comando superó el tiempo máximo (10 min)"


# ───────────────────────────────────────────────────────────────────
def probar_todo() -> List[Dict[str, object]]:
    """Ejecuta cada suite de pruebas que exista y captura su resultado."""
    resultados = []
    for ruta, descripcion in SUITES:
        if not Path(ruta).exists():
            resultados.append({"suite": ruta, "descripcion": descripcion,
                               "estado": "NO EXISTE", "resumen": "—", "salida": ""})
            continue
        codigo, salida = correr([sys.executable, ruta])
        resumen = next((l for l in reversed(salida.splitlines())
                        if "superadas" in l or "pruebas" in l), salida.splitlines()[-1] if salida else "")
        resultados.append({
            "suite": ruta, "descripcion": descripcion,
            "estado": "OK" if codigo == 0 else "FALLA",
            "resumen": resumen.strip(), "salida": salida,
        })
    return resultados


def historial_git() -> Dict[str, object]:
    """Cifras del repositorio: commits totales, reparto por autor y ramas."""
    _, total = correr(["git", "rev-list", "--count", "HEAD"])
    _, autores = correr(["git", "log", "--format=%an"])
    _, ramas = correr(["git", "branch", "-a", "--format=%(refname:short)"])
    _, ultimos = correr(["git", "log", "--format=%h %an %s", "-12"])
    _, correos = correr(["git", "log", "--format=%an <%ae>"])

    conteo: Dict[str, int] = {}
    for linea in autores.splitlines():
        if linea.strip():
            conteo[linea.strip()] = conteo.get(linea.strip(), 0) + 1

    identidades = sorted(set(l.strip() for l in correos.splitlines() if l.strip()))
    return {
        "total": total.strip(),
        "por_autor": sorted(conteo.items(), key=lambda x: -x[1]),
        "identidades": identidades,
        "ramas": [r for r in ramas.splitlines() if r.strip()],
        "ultimos": ultimos.splitlines(),
    }


def archivos_versionados() -> Dict[str, List[str]]:
    """Qué archivos hay versionados en cada carpeta del repositorio."""
    _, salida = correr(["git", "ls-files"])
    por_carpeta: Dict[str, List[str]] = {}
    for ruta in salida.splitlines():
        carpeta = ruta.split("/")[0] if "/" in ruta else "(raíz)"
        por_carpeta.setdefault(carpeta, []).append(ruta)
    return dict(sorted(por_carpeta.items()))


def diagrama_modulos(carpeta: str = "src") -> Dict[str, Dict[str, object]]:
    """Lee los imports reales de cada módulo de src/ y arma el mapa de dependencias.

    Se hace leyendo el código, no de memoria: así el diagrama del informe no puede
    quedar desactualizado respecto del repositorio, que es el error clásico.
    """
    mapa: Dict[str, Dict[str, object]] = {}
    for archivo in sorted(Path(carpeta).glob("*.py")):
        if archivo.name == "__init__.py":
            continue
        try:
            arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        except SyntaxError as e:
            mapa[archivo.stem] = {"error": f"no se pudo leer: {e}"}
            continue

        internos, externos, clases, funciones = set(), set(), [], []
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom) and nodo.module:
                (internos if nodo.module.startswith("src") else externos).add(nodo.module.split(".")[-1])
            elif isinstance(nodo, ast.Import):
                for a in nodo.names:
                    externos.add(a.name.split(".")[0])
            elif isinstance(nodo, ast.ClassDef):
                clases.append(nodo.name)
            elif isinstance(nodo, ast.FunctionDef) and not nodo.name.startswith("_"):
                funciones.append(nodo.name)

        doc = (ast.get_docstring(arbol) or "").split("\n")[0]
        mapa[archivo.stem] = {
            "proposito": doc,
            "depende_de": sorted(internos),
            "librerias": sorted(externos - {"__future__", "typing"}),
            "clases": clases,
            "funciones": funciones,
            "lineas": len(archivo.read_text(encoding="utf-8").splitlines()),
        }
    return mapa


# ───────────────────────────────────────────────────────────────────
def escribir(destino: str = "docs/verificacion.md") -> str:
    """Genera el documento de verificación completo."""
    ahora = datetime.now().strftime("%d-%m-%Y %H:%M")
    pruebas = probar_todo()
    git = historial_git()
    modulos = diagrama_modulos()
    archivos = archivos_versionados()

    L: List[str] = []
    L.append("# Verificación y trazabilidad · Fase 3")
    L.append("")
    L.append(f"Generado automáticamente por `scripts/evidencias.py` el {ahora}.")
    L.append("Todas las cifras de este documento salen del repositorio en el momento "
             "de generarlo; ninguna se transcribe de memoria.")
    L.append("")

    # --- pruebas ---
    L.append("## 1. Pruebas automatizadas")
    L.append("")
    L.append("| Suite | Qué cubre | Comando | Resultado |")
    L.append("|---|---|---|---|")
    for p in pruebas:
        L.append(f"| `{p['suite']}` | {p['descripcion']} | `python {p['suite']}` | "
                 f"**{p['estado']}** · {p['resumen']} |")
    L.append("")
    total_ok = sum(1 for p in pruebas if p["estado"] == "OK")
    L.append(f"Suites ejecutadas correctamente: **{total_ok} de {len(pruebas)}**.")
    L.append("")

    # --- historial ---
    L.append("## 2. Historial del repositorio")
    L.append("")
    L.append(f"- Commits totales en la rama actual: **{git['total']}**")
    L.append(f"- Ramas: {', '.join(f'`{r}`' for r in git['ramas'])}")
    L.append("")
    L.append("| Autor | Commits |")
    L.append("|---|---|")
    for autor, n in git["por_autor"]:
        L.append(f"| {autor} | {n} |")
    L.append("")
    if len(git["identidades"]) > len(git["por_autor"]):
        L.append("> **Atención:** hay más combinaciones nombre/correo que autores distintos, "
                 "lo que significa que alguien commiteó con dos identidades:")
        for i in git["identidades"]:
            L.append(f"> - `{i}`")
        L.append("")
    L.append("Últimos commits:")
    L.append("")
    L.append("```")
    L.extend(git["ultimos"])
    L.append("```")
    L.append("")

    # --- arquitectura ---
    L.append("## 3. Arquitectura de módulos")
    L.append("")
    L.append("Leída directamente del código de `src/` con `ast`, no escrita a mano.")
    L.append("")
    L.append("| Módulo | Propósito | Clases | Funciones públicas | Depende de | Líneas |")
    L.append("|---|---|---|---|---|---|")
    for nombre, info in modulos.items():
        if "error" in info:
            L.append(f"| `{nombre}.py` | {info['error']} | — | — | — | — |")
            continue
        clases = ", ".join(f"`{c}`" for c in info["clases"]) or "—"
        funcs = len(info["funciones"])
        dep = ", ".join(f"`{d}`" for d in info["depende_de"]) or "—"
        L.append(f"| `{nombre}.py` | {info['proposito']} | {clases} | {funcs} | {dep} | {info['lineas']} |")
    L.append("")
    L.append("Dependencias internas (lo que va en el diagrama del informe):")
    L.append("")
    L.append("```")
    hubo = False
    for nombre, info in modulos.items():
        for dep in info.get("depende_de", []):
            L.append(f"  {dep}.py  ──>  {nombre}.py")
            hubo = True
    if not hubo:
        L.append("  (los módulos son independientes entre sí)")
    L.append("```")
    L.append("")

    # --- archivos ---
    L.append("## 4. Archivos versionados")
    L.append("")
    L.append("| Carpeta | Archivos |")
    L.append("|---|---|")
    for carpeta, rutas in archivos.items():
        L.append(f"| `{carpeta}` | {len(rutas)} |")
    L.append("")
    csvs = [r for rs in archivos.values() for r in rs if r.lower().endswith(".csv")]
    L.append(f"CSV versionados: **{len(csvs)}**" + (f" — {csvs}" if csvs else " (correcto: ninguno)."))
    L.append("")

    # --- salidas completas ---
    L.append("## 5. Salida completa de las pruebas")
    L.append("")
    for p in pruebas:
        if not p["salida"]:
            continue
        L.append(f"### `{p['suite']}`")
        L.append("")
        L.append("```")
        L.append(str(p["salida"]))
        L.append("```")
        L.append("")

    Path(destino).parent.mkdir(parents=True, exist_ok=True)
    Path(destino).write_text("\n".join(L), encoding="utf-8")
    return destino


def main() -> int:
    if not Path("README.md").exists():
        print("Hay que ejecutarlo desde la raíz del repositorio.", file=sys.stderr)
        return 1

    print("Generando evidencias...\n")
    destino = escribir()

    git = historial_git()
    print(f"\n  Commits totales        : {git['total']}   <-- esta es la cifra del informe")
    for autor, n in git["por_autor"]:
        print(f"    {autor:<32} {n:>3}")
    if len(git["identidades"]) > len(git["por_autor"]):
        print("\n  ATENCIÓN: hay identidades duplicadas en el historial:")
        for i in git["identidades"]:
            print(f"    {i}")

    print(f"\n  Escrito en: {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
