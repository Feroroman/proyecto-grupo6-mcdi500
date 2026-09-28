"""Pruebas de src/algoritmos.py (Fase 3).

Tres tipos de caso, como en las pruebas de la Fase 2:
  · caso normal    — el algoritmo da el resultado correcto y no modifica la entrada
  · caso límite    — un elemento, elementos idénticos, valores extremos
  · caso excepción — entrada vacía, tipo inválido, columna inexistente

Se ejecuta con:  python tests/test_algoritmos.py
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.algoritmos import (  # noqa: E402
    agregacion_anidada, cuantil_ordenando, cuantil_quickselect,
    explorar_con_poda, explorar_exhaustivo, merge_sort, quickselect,
)

superadas, fallidas = 0, 0


def check(titulo: str, condicion: bool, detalle: str = "") -> None:
    global superadas, fallidas
    if condicion:
        superadas += 1
        print(f"  OK    {titulo}")
    else:
        fallidas += 1
        print(f"  FALLA {titulo}  {detalle}")


def espera_error(titulo: str, funcion, error) -> None:
    try:
        funcion()
    except error:
        check(titulo, True)
    except Exception as e:  # noqa: BLE001
        check(titulo, False, f"lanzó {type(e).__name__} en vez de {error.__name__}")
    else:
        check(titulo, False, "no lanzó ninguna excepción")


def datos_df() -> pd.DataFrame:
    """Muestra sintética que imita la estructura del dataset de titulados."""
    rng = random.Random(7)
    filas = []
    for area in ["Salud", "Educación", "Tecnología"]:
        for jornada in ["Diurno", "Vespertino"]:
            base = {"Salud": 13, "Educación": 10, "Tecnología": 11}[area]
            extra = 3 if jornada == "Vespertino" else 0
            for _ in range(120):
                filas.append({"area": area, "jornada": jornada,
                              "modalidad": rng.choice(["Presencial", "A distancia"]),
                              "duracion": base + extra + rng.randint(-2, 4)})
    # Un área pequeña (dispara la poda por soporte) y una corta (poda por cota)
    for _ in range(20):
        filas.append({"area": "Arte", "jornada": "Diurno", "modalidad": "Presencial",
                      "duracion": rng.randint(8, 11)})
    for _ in range(150):
        filas.append({"area": "Deportes", "jornada": rng.choice(["Diurno", "Vespertino"]),
                      "modalidad": "Presencial", "duracion": rng.randint(6, 9)})
    return pd.DataFrame(filas)


def main() -> int:
    """Ejecuta la suite completa y devuelve 0 si todo pasa."""
    print("\n── Caso normal ─────────────────────────────────────────────")

    rng = random.Random(42)
    muestra = [rng.randint(1, 500) for _ in range(300)]
    copia = list(muestra)

    ordenado = merge_sort(muestra)
    check("merge_sort ordena correctamente", ordenado == sorted(muestra))
    check("merge_sort no modifica la lista original", muestra == copia)

    stats = {}
    merge_sort(muestra, stats)
    check("merge_sort registra profundidad cercana a log2(n)",
          8 <= stats["profundidad_maxima"] <= 10, f"dio {stats['profundidad_maxima']}")

    for k in (0, 1, 150, 299):
        check(f"quickselect encuentra el elemento en la posición {k}",
              quickselect(muestra, k, semilla=1) == sorted(muestra)[k])

    check("quickselect no modifica la lista original", muestra == copia)

    for q in (0.0, 0.25, 0.5, 0.75, 1.0):
        a = cuantil_quickselect(muestra, q, semilla=3)
        b = cuantil_ordenando(muestra, q)
        check(f"quickselect y ordenar dan el mismo cuantil q={q}", a == b, f"{a} vs {b}")

    s_merge, s_quick = {}, {}
    merge_sort(muestra, s_merge)
    cuantil_quickselect(muestra, 0.5, s_quick, semilla=3)
    check("quickselect visita muchísimos menos nodos que merge_sort",
          s_quick["nodos_visitados"] * 10 < s_merge["nodos_visitados"],
          f"{s_quick['nodos_visitados']} vs {s_merge['nodos_visitados']}")

    df = datos_df()
    factores = ["area", "jornada", "modalidad"]

    con_poda, s_poda = explorar_con_poda(df, factores, "duracion", umbral=14, soporte_min=50)
    sin_poda, s_todo = explorar_exhaustivo(df, factores, "duracion", umbral=14, soporte_min=50)

    check("La poda encuentra exactamente los mismos hallazgos que la búsqueda completa",
          sorted(map(str, con_poda)) == sorted(map(str, sin_poda)),
          f"{len(con_poda)} vs {len(sin_poda)}")
    check("La poda visita menos nodos que la búsqueda completa",
          s_poda["nodos_visitados"] < s_todo["nodos_visitados"],
          f"{s_poda['nodos_visitados']} vs {s_todo['nodos_visitados']}")
    check("La poda registra las ramas que cortó", s_poda["ramas_podadas"] > 0)
    check("Los hallazgos vienen ordenados de mayor a menor mediana",
          all(con_poda[i]["mediana"] >= con_poda[i + 1]["mediana"] for i in range(len(con_poda) - 1)))
    check("Todos los hallazgos superan el umbral", all(h["mediana"] >= 14 for h in con_poda))
    check("Todos los hallazgos cumplen el soporte mínimo", all(h["n"] >= 50 for h in con_poda))

    grandes = df[df["area"].isin(["Salud", "Educación", "Tecnología"])]
    agg = agregacion_anidada(grandes, "area", "jornada", "duracion", soporte_min=50)
    check("La agregación anidada devuelve un grupo por combinación", len(agg) == 6)
    check("La agregación trae la diferencia respecto del área", "dif_vs_area" in agg.columns)
    check("La agregación marca los grupos con soporte suficiente", bool(agg["suficiente"].all()))
    check("El vespertino aparece por encima del promedio de su área",
          bool((agg[agg["jornada"] == "Vespertino"]["dif_vs_area"] > 0).all()))

    agg_todo = agregacion_anidada(df, "area", "jornada", "duracion", soporte_min=50)
    check("La agregación marca como insuficiente el grupo de 20 registros",
          not bool(agg_todo[agg_todo["area"] == "Arte"]["suficiente"].iloc[0]))


    print("\n── Caso límite ─────────────────────────────────────────────")

    check("merge_sort de una lista vacía", merge_sort([]) == [])
    check("merge_sort de un solo elemento", merge_sort([7]) == [7])
    check("merge_sort con todos los elementos idénticos", merge_sort([4] * 20) == [4] * 20)
    check("merge_sort de una lista ya ordenada", merge_sort([1, 2, 3, 4]) == [1, 2, 3, 4])
    check("merge_sort de una lista al revés", merge_sort([4, 3, 2, 1]) == [1, 2, 3, 4])

    check("quickselect con un solo elemento (caso base)", quickselect([9], 0) == 9)
    check("quickselect con todos los elementos idénticos", quickselect([5] * 30, 15) == 5)
    check("quickselect con valores negativos y extremos",
          quickselect([-1000, 0, 1000, -5], 0) == -1000)
    check("cuantil de un solo elemento", cuantil_quickselect([3.5], 0.5) == 3.5)

    stats = {}
    quickselect([5] * 30, 15, stats)
    check("Elementos idénticos no producen recursión profunda",
          stats["profundidad_maxima"] <= 2, f"dio {stats['profundidad_maxima']}")

    vacio = df.iloc[0:0]
    h, s = explorar_con_poda(vacio, factores, "duracion", umbral=14, soporte_min=50)
    check("Exploración sobre un DataFrame vacío no falla y no halla nada", h == [])

    h, s = explorar_con_poda(df, factores, "duracion", umbral=9999, soporte_min=50)
    check("Umbral inalcanzable: sin hallazgos y todo podado en la raíz",
          h == [] and s["nodos_visitados"] == 1)

    h, s = explorar_con_poda(df, factores, "duracion", umbral=14, soporte_min=100_000)
    check("Soporte imposible: sin hallazgos", h == [])

    h, s = explorar_con_poda(df, ["area"], "duracion", umbral=13, soporte_min=50)
    check("Exploración con un solo factor", all(set(x) >= {"area", "n", "mediana"} for x in h))


    print("\n── Caso excepción ──────────────────────────────────────────")

    espera_error("quickselect de una lista vacía lanza ValueError",
                 lambda: quickselect([], 0), ValueError)
    espera_error("quickselect con k negativo lanza ValueError",
                 lambda: quickselect([1, 2, 3], -1), ValueError)
    espera_error("quickselect con k fuera de rango lanza ValueError",
                 lambda: quickselect([1, 2, 3], 3), ValueError)
    espera_error("cuantil con q mayor que 1 lanza ValueError",
                 lambda: cuantil_quickselect([1, 2, 3], 1.5), ValueError)
    espera_error("cuantil de una secuencia vacía lanza ValueError",
                 lambda: cuantil_ordenando([], 0.5), ValueError)
    espera_error("Exploración sin factores lanza ValueError",
                 lambda: explorar_con_poda(df, [], "duracion", 14), ValueError)
    espera_error("Exploración con columna inexistente lanza KeyError",
                 lambda: explorar_con_poda(df, ["no_existe"], "duracion", 14), KeyError)
    espera_error("Exploración con respuesta inexistente lanza KeyError",
                 lambda: explorar_con_poda(df, factores, "no_existe", 14), KeyError)
    espera_error("Exploración con respuesta de texto lanza TypeError",
                 lambda: explorar_con_poda(df, ["jornada"], "area", 14), TypeError)
    espera_error("Exploración con algo que no es DataFrame lanza TypeError",
                 lambda: explorar_con_poda([1, 2, 3], factores, "duracion", 14), TypeError)


    print("\n" + "─" * 60)
    print(f"{superadas}/{superadas + fallidas} pruebas superadas")
    return 0 if fallidas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
