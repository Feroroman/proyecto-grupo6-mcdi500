"""Fase 3 · Análisis de Complejidad y Rendimiento.

Módulo encargado de medir empíricamente el tiempo de ejecución y la cantidad de
nodos visitados de los algoritmos estructurados y recursivos desarrollados en
`src/algoritmos.py`, generando los gráficos comparativos de eficiencia para
el informe de la Fase 3.

Autoría: Jorge Álvarez Ossandón · MCDI500 · Fase 3
"""
from __future__ import annotations

import os
import random
import time
from statistics import median
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from algoritmos import (
    cuantil_ordenando,
    cuantil_quickselect,
    explorar_con_poda,
    explorar_exhaustivo,
)


# ═══════════════════════════════════════════════════════════════════════
#  1 · MEDICIÓN DIVIDE AND CONQUER (CUANTILES)
# ═══════════════════════════════════════════════════════════════════════
def medir_divide_y_venceras(tamaños: List[int] | None = None) -> None:
    """Compara el rendimiento empírico entre el enfoque ingenuo (ordenar todo)
    y el enfoque optimizado (Quickselect) para la obtención de cuantiles.

    Se realizan varias repeticiones para reducir el efecto del ruido
    producido por el sistema operativo y se utiliza la mediana de los tiempos.

    Guarda el gráfico resultante en docs/figuras/.
    """
    if tamaños is None:
        tamaños = [1000, 5000, 10000, 20000, 50000, 100000]

    repeticiones = 5

    tiempos_ingenua: List[float] = []
    tiempos_optimizada: List[float] = []

    generador = random.Random(42)

    for n in tamaños:
        datos = [generador.random() for _ in range(n)]

        tiempos_ingenua_n: List[float] = []
        tiempos_optimizada_n: List[float] = []

        for _ in range(repeticiones):

            # Versión ingenua: O(n log n)
            inicio = time.perf_counter()
            cuantil_ordenando(datos, 0.5)
            fin = time.perf_counter()

            tiempos_ingenua_n.append(fin - inicio)

            # Versión optimizada con Quickselect: O(n) promedio
            inicio = time.perf_counter()
            cuantil_quickselect(datos, 0.5, semilla=42)
            fin = time.perf_counter()

            tiempos_optimizada_n.append(fin - inicio)

        tiempos_ingenua.append(median(tiempos_ingenua_n))
        tiempos_optimizada.append(median(tiempos_optimizada_n))

    _guardar_grafico(
        tamaños,
        tiempos_ingenua,
        tiempos_optimizada,
        titulo="Comparación: Cuantil Ingenuo vs Quickselect",
        etiqueta_ingenuo="Ingenuo (Ordena todo O(n log n))",
        etiqueta_optimizado="Quickselect (O(n) promedio)",
        nombre_archivo="rendimiento_divide_y_venceras.png",
        eje_y="Tiempo de ejecución (segundos)"
    )


# ═══════════════════════════════════════════════════════════════════════
#  2 · MEDICIÓN EXPLORACIÓN JERÁRQUICA CON PODA
# ═══════════════════════════════════════════════════════════════════════
def medir_exploracion(tamaños: List[int] | None = None) -> None:
    """Compara la exploración exhaustiva con la exploración con poda.

    Se registran dos métricas:

    1. Cantidad de nodos visitados.
    2. Tiempo de ejecución.

    La primera permite observar directamente el efecto de la poda sobre
    el árbol de búsqueda. La segunda permite observar el comportamiento
    empírico frente al aumento del tamaño del DataFrame.

    Guarda los gráficos resultantes en docs/figuras/.
    """
    if tamaños is None:
        tamaños = [1000, 5000, 10000, 20000]

    repeticiones = 5

    nodos_exhaustivos: List[int] = []
    nodos_con_poda: List[int] = []

    tiempos_exhaustivos: List[float] = []
    tiempos_con_poda: List[float] = []

    factores = ["sede", "area", "jornada"]

    for n in tamaños:

        df = _generar_dataframe_prueba(n)

        # ---------------------------------------------------------------
        # MEDICIÓN DE NODOS
        # ---------------------------------------------------------------

        _, stats_ex = explorar_exhaustivo(
            df,
            factores,
            "dur_total_carr",
            umbral=21,
            soporte_min=100
        )

        _, stats_poda = explorar_con_poda(
            df,
            factores,
            "dur_total_carr",
            umbral=21,
            soporte_min=100
        )

        nodos_exhaustivos.append(stats_ex["nodos_visitados"])
        nodos_con_poda.append(stats_poda["nodos_visitados"])

        # ---------------------------------------------------------------
        # MEDICIÓN DE TIEMPO
        # ---------------------------------------------------------------

        tiempos_ex_n: List[float] = []
        tiempos_poda_n: List[float] = []

        for _ in range(repeticiones):

            inicio = time.perf_counter()

            explorar_exhaustivo(
                df,
                factores,
                "dur_total_carr",
                umbral=21,
                soporte_min=100
            )

            fin = time.perf_counter()

            tiempos_ex_n.append(fin - inicio)

            inicio = time.perf_counter()

            explorar_con_poda(
                df,
                factores,
                "dur_total_carr",
                umbral=21,
                soporte_min=100
            )

            fin = time.perf_counter()

            tiempos_poda_n.append(fin - inicio)

        tiempos_exhaustivos.append(median(tiempos_ex_n))
        tiempos_con_poda.append(median(tiempos_poda_n))

    # ---------------------------------------------------------------
    # GRÁFICO 1: NODOS VISITADOS
    # ---------------------------------------------------------------

    _guardar_grafico(
        tamaños,
        nodos_exhaustivos,
        nodos_con_poda,
        titulo="Comparación: Exploración Exhaustiva vs Con Poda",
        etiqueta_ingenuo="Exhaustivo (Sin podar)",
        etiqueta_optimizado="Con Poda (Optimizado)",
        nombre_archivo="rendimiento_exploracion_poda.png",
        eje_y="Nodos visitados"
    )

    # ---------------------------------------------------------------
    # GRÁFICO 2: TIEMPO DE EJECUCIÓN
    # ---------------------------------------------------------------

    _guardar_grafico(
        tamaños,
        tiempos_exhaustivos,
        tiempos_con_poda,
        titulo="Tiempo de ejecución: Exploración Exhaustiva vs Con Poda",
        etiqueta_ingenuo="Exhaustivo (Sin podar)",
        etiqueta_optimizado="Con Poda (Optimizado)",
        nombre_archivo="tiempo_exploracion_poda.png",
        eje_y="Tiempo de ejecución (segundos)"
    )

    # ---------------------------------------------------------------
    # INFORMACIÓN DE REDUCCIÓN
    # ---------------------------------------------------------------

    print("\nResultados de la poda:")

    for n, exhaustivo, poda in zip(
        tamaños,
        nodos_exhaustivos,
        nodos_con_poda
    ):
        reduccion = (
            (exhaustivo - poda) / exhaustivo * 100
            if exhaustivo > 0
            else 0
        )

        print(
            f"N={n:>6}: "
            f"Exhaustivo={exhaustivo:>3} nodos | "
            f"Poda={poda:>3} nodos | "
            f"Reducción={reduccion:>6.2f}%"
        )


# ═══════════════════════════════════════════════════════════════════════
#  3 · FUNCIONES AUXILIARES
# ═══════════════════════════════════════════════════════════════════════
def _generar_dataframe_prueba(n: int) -> pd.DataFrame:
    """Genera un DataFrame reproducible con la estructura requerida.

    La distribución de duraciones se construye de forma controlada para
    que determinadas ramas puedan ser descartadas mediante la poda por
    cota superior.

    Las categorías corresponden a los factores utilizados por la
    exploración jerárquica.
    """

    generador = random.Random(42 + n)

    sedes = []
    areas = []
    jornadas = []
    duraciones = []

    for _ in range(n):

        sede = generador.choice(
            ["S1", "S2", "S3", "S4"]
        )

        area = generador.choice(
            ["Ingeniería", "Salud", "Ciencias", "Artes"]
        )

        jornada = generador.choice(
            ["Diurna", "Vespertina"]
        )

        # -----------------------------------------------------------
        # Rama crítica controlada:
        # S3/S4 + Salud/Ciencias + cualquier jornada
        #
        # Estas ramas contienen duraciones sobre el umbral.
        # Las demás ramas contienen solamente valores bajos.
        # -----------------------------------------------------------
        if (
            sede in ["S3", "S4"]
            and area in ["Salud", "Ciencias"]
        ):
            duracion = generador.randint(21, 22)
        else:
            duracion = generador.randint(8, 14)

        sedes.append(sede)
        areas.append(area)
        jornadas.append(jornada)
        duraciones.append(duracion)

    return pd.DataFrame({
        "sede": sedes,
        "area": areas,
        "jornada": jornadas,
        "dur_total_carr": duraciones
    })


def _guardar_grafico(
    x: List[int],
    y_ingenuo: List[float] | List[int],
    y_optimizado: List[float] | List[int],
    titulo: str,
    etiqueta_ingenuo: str,
    etiqueta_optimizado: str,
    nombre_archivo: str,
    eje_y: str
) -> None:
    """Genera, formatea y guarda la figura en la ruta institucional
    docs/figuras/.
    """

    plt.figure(figsize=(8, 5))

    plt.plot(
        x,
        y_ingenuo,
        marker="o",
        label=etiqueta_ingenuo,
        linewidth=2
    )

    plt.plot(
        x,
        y_optimizado,
        marker="s",
        label=etiqueta_optimizado,
        linewidth=2
    )

    plt.title(titulo)
    plt.xlabel("Tamaño de los datos (N)")
    plt.ylabel(eje_y)

    plt.xticks(x)

    plt.legend()

    plt.grid(
        True,
        linestyle="--",
        alpha=0.7
    )

    plt.tight_layout()

    ruta_figuras = os.path.join(
        os.path.dirname(__file__),
        "..",
        "docs",
        "figuras"
    )

    os.makedirs(
        ruta_figuras,
        exist_ok=True
    )

    ruta_final = os.path.join(
        ruta_figuras,
        nombre_archivo
    )

    plt.savefig(
        ruta_final,
        bbox_inches="tight",
        dpi=300
    )

    plt.close()

    print(
        f"[Éxito] Gráfico guardado en: {ruta_final}"
    )


# ═══════════════════════════════════════════════════════════════════════
#  4 · EJECUCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    print(
        "Iniciando análisis de complejidad y rendimiento (Fase 3)..."
    )

    medir_divide_y_venceras()

    medir_exploracion()

    print(
        "\nAnálisis finalizado correctamente."
    )