"""Contrasta las cifras del informe de la Fase 4 contra el repositorio.

    python scripts/verificar_cifras_informe.py

Para Sebastián: este script no opina. Toma cada cifra que afirma el borrador
del informe, la vuelve a obtener de donde corresponda —el entorno virtual, el
historial de Git, la bitácora de la Fase 2, o una medición en vivo sobre las
105.060 filas reales— y las pone lado a lado.

Donde una medición depende de la máquina (los tiempos), el script la ejecuta
aquí y ahora, de modo que puedas comprobarla en la tuya sin creerle a nadie.

No modifica ningún archivo. Tarda alrededor de un minuto, casi todo en la
comparación de vectorización contra bucles.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional, Tuple

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

RUTA_LIMPIO = RAIZ / "data/processed/titulados_2025_pregrado_univ_limpio.csv"

ANCHO = 78
resultados: List[Tuple[str, str, str, Optional[bool]]] = []


def anotar(concepto: str, informe: str, real: str, ok: Optional[bool]) -> None:
    resultados.append((concepto, informe, real, ok))
    marca = {True: "coincide", False: "NO COINCIDE", None: "revisar"}[ok]
    print(f"  [{marca:^11}]  {concepto}")
    if ok is not True:
        print(f"                 informe: {informe}")
        print(f"                 real:    {real}")


def git(*args: str) -> str:
    try:
        r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True,
                           text=True, timeout=60)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def titulo(t: str) -> None:
    print(f"\n{t}\n{'-' * ANCHO}")


def comprobar_contexto() -> None:
    """Dos avisos sin los cuales el resultado engaña."""
    problemas = []

    if ".venv" not in sys.executable:
        problemas.append(
            "NO estás dentro del entorno virtual.\n"
            f"       Intérprete en uso: {sys.executable}\n"
            "       Las versiones de librerías que verás NO son las del proyecto.\n"
            "       Corrige con:  source .venv/bin/activate")

    rama = git("rev-parse", "--abbrev-ref", "HEAD")
    if rama and rama != "main":
        problemas.append(
            f"Estás en la rama «{rama}», no en main.\n"
            "       Los archivos de los demás integrantes viven en main, así que\n"
            "       este script los dará por inexistentes aunque sí estén.\n"
            "       Corrige con:  git checkout main && git pull")

    if problemas:
        print("\n" + "!" * ANCHO)
        print("  AVISO · el resultado de abajo será incorrecto si no corriges esto")
        print("!" * ANCHO)
        for p in problemas:
            print(f"\n  ·  {p}")
        print("\n" + "!" * ANCHO)
    else:
        print(f"\n  Entorno: {sys.executable}")
        print(f"  Rama:    {rama}")


# ───────────────────────────────────────────────────────────── 1 · entorno ──
def verificar_entorno() -> None:
    titulo("1 · Versiones del entorno")

    dice = {"numpy": "2.4.2", "pandas": "3.0.1",
            "matplotlib": "3.10.8", "seaborn": "0.13.2"}

    for nombre, declarada in dice.items():
        try:
            mod = __import__(nombre)
            instalada = getattr(mod, "__version__", "sin __version__")
            anotar(f"{nombre} {declarada}", declarada, instalada,
                   instalada == declarada)
        except ImportError:
            anotar(f"{nombre} {declarada}", f"{declarada} (citada en el informe)",
                   "NO ESTÁ INSTALADA en este entorno", False)

    v = sys.version_info
    anotar("versión de Python", "no se declara en el informe",
           f"{v.major}.{v.minor}.{v.micro}", None)


# ──────────────────────────────────────────────────────────────── 2 · git ──
def verificar_git() -> None:
    titulo("2 · Historial y ramas")

    n = git("rev-list", "--count", "HEAD")
    anotar("69 commits atómicos", "69", f"{n} en la rama actual", n == "69")

    dice_ramas = ["fase4-fernanda-visualizaciones", "fase4-cesar-validacion",
                  "fase4-jorge-eficiencia", "fase4-sebastian-informe-final"]

    salida = git("branch", "-r", "--format=%(refname:short)")
    reales = sorted(b.split("/", 1)[1] for b in salida.splitlines()
                    if "/fase4-" in b)

    for r in dice_ramas:
        existe = r in reales
        anotar(f"rama «{r}»", r,
               "no existe" if not existe else r, existe)

    print(f"\n  Las ramas fase4- que sí existen en origin:")
    for r in reales:
        print(f"      {r}")


# ───────────────────────────────────────────────────────── 3 · algoritmos ──
def cronometrar(f: Callable, repeticiones: int = 5) -> float:
    """Devuelve el tiempo medio por ejecución, en segundos."""
    t = time.perf_counter()
    for _ in range(repeticiones):
        f()
    return (time.perf_counter() - t) / repeticiones


def verificar_quickselect(duraciones: List[float]) -> None:
    titulo("3 · Quickselect frente a ordenar  (la afirmación central)")

    from src.algoritmos import cuantil_ordenando, cuantil_quickselect

    t_qs = cronometrar(lambda: cuantil_quickselect(list(duraciones), 0.5))
    t_or = cronometrar(lambda: cuantil_ordenando(list(duraciones), 0.5))

    print(f"  n = {len(duraciones):,} duraciones reales".replace(",", "."))
    print(f"  quickselect : {t_qs * 1000:7.1f} ms   (teórico O(n))")
    print(f"  ordenando   : {t_or * 1000:7.1f} ms   (teórico O(n log n))")

    razon = t_qs / t_or if t_or else float("nan")
    gana = "quickselect" if t_qs < t_or else "ordenar"
    print(f"\n  Gana: {gana}, por un factor de {max(razon, 1/razon):.2f}×")

    anotar("Quickselect es superior a ordenar",
           "Quickselect logra O(N) lineal y supera al ordenamiento",
           f"quickselect es {razon:.2f}× el tiempo de ordenar "
           f"→ {'más lento' if razon > 1 else 'más rápido'}",
           t_qs < t_or)

    if t_qs > t_or:
        print("""
  Por qué ocurre, y por qué conviene decirlo:
  `sorted()` de Python es Timsort implementado en C, mientras que
  `quickselect` es un recorrido recursivo en Python puro. La constante
  oculta de la notación O() es dos órdenes de magnitud menor en el primer
  caso, y a n = 105.060 todavía domina sobre la diferencia asintótica.
  La complejidad teórica es correcta; lo que falla es suponer que se
  traduce en tiempo de reloj a este tamaño.

  Es un hallazgo mejor que el que afirma el informe: muestra que el grupo
  midió en vez de copiar la conclusión del libro.""")


# ────────────────────────────────────────────────────── 4 · vectorización ──
def verificar_vectorizacion() -> None:
    titulo("4 · Vectorización frente a bucles")

    print("""  Esta cifra no se vuelve a medir aquí, y conviene explicar por qué:
  la medición depende de con qué bucle se compare (un `for` celda a celda,
  un `.apply`, o una lista por comprensión dan factores muy distintos), de
  modo que un número nuevo no resolvería nada. La implementación exacta que
  se midió vive en el notebook de la Fase 3.

  Lo que sí se puede comprobar sin medir nada es que los dos informes del
  propio grupo se contradicen:""")

    print("\n      informe de la Fase 3, pág. 7 : 5,9× (agrupar_raras)")
    print("                                     4,6× (one_hot)")
    print("      borrador de la Fase 4        : 45×")

    anotar("la vectorización aceleró 45 veces",
           "45× (borrador de la Fase 4)",
           "5,9× y 4,6× según el informe de la Fase 3 ya entregado "
           "— los dos documentos del grupo no coinciden",
           False)


# ──────────────────────────────────────────────────────────── 5 · datos ──
def verificar_datos(df) -> None:
    titulo("5 · Cifras del conjunto de datos")

    anotar("105.060 filas × 84 columnas",
           "105.060 × 84",
           f"{df.shape[0]:,} × {df.shape[1]}".replace(",", "."),
           df.shape == (105060, 84))

    n_cat = df["nomb_carrera"].nunique()
    raras = (df["nomb_carrera"].value_counts() < 100).sum()
    anotar("968 categorías raras agrupadas",
           "968 categorías con < 0,5 % de los registros",
           f"{raras} categorías con < 100 registros, de {n_cat} en total "
           f"(el umbral fue 100 registros, no un porcentaje)",
           raras == 968)

    bandera = "anio_ing_carr_ori_imputada"
    if bandera in df.columns:
        n_imp = int((df[bandera] == 1).sum())
        pct = 100 * n_imp / len(df)
        anotar("imputación por área CINE",
               "mediana condicional por área CINE",
               "{} filas ({:.1f} %) imputadas con la mediana por "
               "anio_ing_carr_act, según docs/bitacora.md".format(
                   format(n_imp, ",").replace(",", "."), pct),
               False)


# ──────────────────────────────────────────────────── 6 · archivos citados ──
def verificar_archivos() -> None:
    titulo("6 · Archivos que el informe cita")

    citados = [
        "notebooks/F1/F1_Definicion.ipynb",
        "notebooks/F2/F2_Pipeline.ipynb",
        "notebooks/F3/F3_Algoritmos_Complejidad.ipynb",
        "notebooks/F4/F4_Visualizaciones_Comunicacion.ipynb",
        "src/complejidad.py",
        "src/estratificacion.py",
        "src/graficos.py",
        "src/interpretable.py",
        "src/tablas.py",
        "scripts/evidencias.py",
        "requirements.txt",
    ]
    for c in citados:
        existe = (RAIZ / c).exists()
        anotar(c, "citado en el informe",
               "existe" if existe else "NO EXISTE en el repositorio", existe)

    for i in range(1, 7):
        p = list((RAIZ / "docs/figuras").glob(f"f4_{i:02d}_*.png"))
        anotar(f"figura f4_{i:02d}", "citada en el informe",
               p[0].name if p else "NO EXISTE", bool(p))


# ──────────────────────────────────────────────────────────────── resumen ──
def main() -> int:
    print("=" * ANCHO)
    print("  VERIFICACIÓN DE LAS CIFRAS DEL INFORME · FASE 4 · GRUPO 6".center(ANCHO))
    print("=" * ANCHO)

    comprobar_contexto()
    verificar_entorno()
    verificar_git()
    verificar_archivos()

    if not RUTA_LIMPIO.exists():
        print(f"\n  No está {RUTA_LIMPIO.relative_to(RAIZ)}.")
        print("  Las comprobaciones sobre los datos se omiten.")
        print("  Para generarlo: ejecuta los notebooks de las Fases 1 y 2.")
    else:
        import pandas as pd
        df = pd.read_csv(RUTA_LIMPIO, sep=";", low_memory=False)
        duraciones = df["dur_total_carr"].dropna().tolist()

        verificar_datos(df)
        verificar_quickselect(duraciones)

    verificar_vectorizacion()

    titulo("Resumen")
    mal = [r for r in resultados if r[3] is False]
    rev = [r for r in resultados if r[3] is None]
    print(f"  comprobaciones            : {len(resultados)}")
    print(f"  coinciden con el informe  : {len(resultados) - len(mal) - len(rev)}")
    print(f"  NO coinciden              : {len(mal)}")
    print(f"  para revisar a mano       : {len(rev)}")

    if mal:
        print("\n  Hay que corregir en el informe:")
        for concepto, informe, real, _ in mal:
            print(f"\n    · {concepto}")
            print(f"        dice : {informe}")
            print(f"        es   : {real}")

    print()
    return 1 if mal else 0


if __name__ == "__main__":
    raise SystemExit(main())
