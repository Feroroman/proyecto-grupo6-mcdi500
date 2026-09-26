"""Fase 3 · Algoritmos estructurados y recursivos.

Dos familias de algoritmos, cada una con su versión ingenua para poder comparar:

1. **Divide and conquer** — `merge_sort` y `quickselect`, con la recurrencia formal
   T(n) = 2·T(n/2) + O(n) y T(n) = T(n/2) + O(n) respectivamente. La contraparte
   ingenua es `cuantil_ordenando`, que ordena todo para leer un solo valor.

2. **Exploración jerárquica con poda** — `explorar_con_poda` recorre el árbol de
   combinaciones de factores académicos buscando las que producen sobreduración
   mediana crítica, y corta ramas que no pueden contener una respuesta.
   `explorar_exhaustivo` hace lo mismo sin podar, para medir cuánto ahorra la poda.

Todas las funciones devuelven, además del resultado, un diccionario de estadísticas
(`nodos_visitados`, `profundidad_maxima`, `ramas_podadas`) que es el insumo directo
del análisis de complejidad de `src/complejidad.py`.

Autoría: César Lorca Bacián · MCDI500 · Fase 3
"""
from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import pandas as pd


# ═══════════════════════════════════════════════════════════════════════
#  1 · DIVIDE AND CONQUER
# ═══════════════════════════════════════════════════════════════════════
def merge_sort(datos: Sequence[float], stats: Optional[Dict[str, int]] = None,
               _nivel: int = 0) -> List[float]:
    """Ordena por mezcla, dividiendo la lista en dos mitades iguales.

    Recurrencia: T(n) = 2·T(n/2) + O(n), que por el teorema maestro da O(n log n).
    Cada llamada divide en dos (2·T(n/2)) y la mezcla recorre los n elementos
    una vez (+ O(n)).

    Parámetros
    ----------
    datos : secuencia de números a ordenar. No se modifica.
    stats : diccionario opcional donde acumular nodos visitados y profundidad.
    _nivel : uso interno; nivel actual del árbol de recursión.

    Devuelve
    --------
    Lista nueva con los elementos ordenados de menor a mayor.

    Precondición: todos los elementos deben ser comparables entre sí.
    Complejidad: O(n log n) en tiempo, O(n) en espacio auxiliar.
    """
    if stats is not None:
        stats["nodos_visitados"] = stats.get("nodos_visitados", 0) + 1
        stats["profundidad_maxima"] = max(stats.get("profundidad_maxima", 0), _nivel)

    # CASO BASE: una lista de 0 o 1 elemento ya está ordenada.
    if len(datos) <= 1:
        return list(datos)

    medio = len(datos) // 2
    izquierda = merge_sort(datos[:medio], stats, _nivel + 1)
    derecha = merge_sort(datos[medio:], stats, _nivel + 1)
    return _mezclar(izquierda, derecha)


def _mezclar(a: List[float], b: List[float]) -> List[float]:
    """Combina dos listas ya ordenadas en una sola ordenada. O(n)."""
    salida: List[float] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            salida.append(a[i]); i += 1
        else:
            salida.append(b[j]); j += 1
    salida.extend(a[i:])
    salida.extend(b[j:])
    return salida


def quickselect(datos: Sequence[float], k: int, stats: Optional[Dict[str, int]] = None,
                semilla: Optional[int] = None) -> float:
    """Devuelve el k-ésimo menor elemento (k empieza en 0) sin ordenar la lista entera.

    Es divide and conquer con una diferencia clave respecto de merge_sort: después
    de partir alrededor del pivote, solo baja por UNA de las dos mitades, porque
    sabe de qué lado está el elemento buscado.

    Recurrencia: T(n) = T(n/2) + O(n) en promedio, que da O(n) — mejor que ordenar,
    que es O(n log n). En el peor caso (pivote siempre extremo) degenera a O(n²);
    por eso el pivote se elige al azar.

    Parámetros
    ----------
    datos : secuencia de números. No se modifica.
    k : posición buscada en el orden, de 0 a len(datos)-1.
    stats : diccionario opcional donde acumular estadísticas de recursión.
    semilla : fija el azar del pivote para que el resultado sea reproducible.

    Lanza ValueError si `datos` está vacío o si k queda fuera de rango.
    """
    if len(datos) == 0:
        raise ValueError("quickselect necesita al menos un elemento")
    if not 0 <= k < len(datos):
        raise ValueError(f"k={k} fuera de rango para {len(datos)} elementos")
    rng = random.Random(semilla)
    return _quickselect(list(datos), k, rng, stats, 0)


def _quickselect(datos: List[float], k: int, rng: random.Random,
                 stats: Optional[Dict[str, int]], nivel: int) -> float:
    if stats is not None:
        stats["nodos_visitados"] = stats.get("nodos_visitados", 0) + 1
        stats["profundidad_maxima"] = max(stats.get("profundidad_maxima", 0), nivel)

    # CASO BASE: un solo elemento, necesariamente es el buscado.
    if len(datos) == 1:
        return datos[0]

    pivote = datos[rng.randrange(len(datos))]
    menores = [x for x in datos if x < pivote]
    iguales = [x for x in datos if x == pivote]
    mayores = [x for x in datos if x > pivote]

    if k < len(menores):
        return _quickselect(menores, k, rng, stats, nivel + 1)
    if k < len(menores) + len(iguales):
        return pivote                                   # cae dentro del bloque del pivote
    return _quickselect(mayores, k - len(menores) - len(iguales), rng, stats, nivel + 1)


def cuantil_quickselect(datos: Sequence[float], q: float,
                        stats: Optional[Dict[str, int]] = None,
                        semilla: Optional[int] = None) -> float:
    """Cuantil q (entre 0 y 1) calculado con quickselect. O(n) en promedio."""
    if not 0 <= q <= 1:
        raise ValueError(f"q debe estar entre 0 y 1, llegó {q}")
    if len(datos) == 0:
        raise ValueError("no se puede calcular un cuantil de una secuencia vacía")
    k = min(int(q * len(datos)), len(datos) - 1)
    return quickselect(datos, k, stats, semilla)


def cuantil_ordenando(datos: Sequence[float], q: float) -> float:
    """Versión ingenua: ordena TODO para leer un solo valor. O(n log n).

    Es la contraparte contra la que se compara `cuantil_quickselect`. Da el mismo
    resultado; hace mucho más trabajo del necesario.
    """
    if not 0 <= q <= 1:
        raise ValueError(f"q debe estar entre 0 y 1, llegó {q}")
    if len(datos) == 0:
        raise ValueError("no se puede calcular un cuantil de una secuencia vacía")
    ordenados = sorted(datos)
    k = min(int(q * len(ordenados)), len(ordenados) - 1)
    return ordenados[k]


# ═══════════════════════════════════════════════════════════════════════
#  2 · EXPLORACIÓN JERÁRQUICA CON PODA
# ═══════════════════════════════════════════════════════════════════════
def explorar_con_poda(df: pd.DataFrame, factores: Sequence[str], respuesta: str,
                      umbral: float, soporte_min: int = 100) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Busca combinaciones de factores cuya duración mediana supere `umbral`.

    Recorre el árbol de combinaciones en profundidad: el nivel 0 fija el primer
    factor, el nivel 1 el segundo, y así. Cada nodo es un subconjunto del DataFrame.

    Dos podas, y las dos son demostrablemente correctas:

    · **Poda por soporte.** Si un nodo tiene menos de `soporte_min` registros, todos
      sus descendientes tendrán aún menos (son subconjuntos). Ninguno puede cumplir
      el soporte mínimo, así que la rama entera se descarta sin visitarla.

    · **Poda por cota superior.** Si el máximo de `respuesta` en el nodo es menor que
      `umbral`, ningún descendiente puede tener una mediana mayor que `umbral`,
      porque los valores de un subconjunto nunca superan el máximo del conjunto.

    Sin estas dos podas el árbol crece como el producto de las cardinalidades de los
    factores; con ellas se recorre una fracción. Cuánto exactamente lo dice el
    campo `ramas_podadas` del diccionario de estadísticas.

    Parámetros
    ----------
    df : DataFrame con los factores y la variable de respuesta.
    factores : nombres de las columnas categóricas, en el orden de exploración.
    respuesta : nombre de la columna numérica (p. ej. 'dur_total_carr').
    umbral : duración mediana a partir de la cual la combinación es crítica.
    soporte_min : mínimo de registros para que un grupo se considere.

    Devuelve
    --------
    (hallazgos, stats) donde hallazgos es una lista de diccionarios con la
    combinación, su n y su mediana, ordenada de mayor a menor mediana.

    Lanza KeyError si alguna columna no existe, ValueError si `factores` está vacío.
    """
    _validar(df, factores, respuesta)
    hallazgos: List[Dict[str, Any]] = []
    stats: Dict[str, int] = {"nodos_visitados": 0, "ramas_podadas": 0, "profundidad_maxima": 0}

    def bajar(sub: pd.DataFrame, combinacion: Dict[str, Any], nivel: int) -> None:
        stats["nodos_visitados"] += 1
        stats["profundidad_maxima"] = max(stats["profundidad_maxima"], nivel)

        # PODA 1 · soporte insuficiente: ningún descendiente puede recuperarlo
        if len(sub) < soporte_min:
            stats["ramas_podadas"] += 1
            return

        # PODA 2 · cota superior: si el máximo no llega al umbral, la mediana tampoco
        if sub[respuesta].max() < umbral:
            stats["ramas_podadas"] += 1
            return

        mediana = float(sub[respuesta].median())
        if combinacion and mediana >= umbral:
            hallazgos.append({**combinacion, "n": len(sub), "mediana": round(mediana, 2),
                              "nivel": nivel})

        # CASO BASE: no quedan factores por fijar
        if nivel >= len(factores):
            return

        factor = factores[nivel]
        for valor in sorted(sub[factor].dropna().unique()):
            bajar(sub[sub[factor] == valor], {**combinacion, factor: valor}, nivel + 1)

    bajar(df, {}, 0)
    hallazgos.sort(key=lambda h: h["mediana"], reverse=True)
    return hallazgos, stats


def explorar_exhaustivo(df: pd.DataFrame, factores: Sequence[str], respuesta: str,
                        umbral: float, soporte_min: int = 100) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Misma búsqueda SIN podar: recorre el árbol completo.

    Existe solo para comparar. Devuelve exactamente los mismos hallazgos que
    `explorar_con_poda` —eso es lo que demuestra que las podas son correctas— pero
    visitando muchos más nodos.
    """
    _validar(df, factores, respuesta)
    hallazgos: List[Dict[str, Any]] = []
    stats: Dict[str, int] = {"nodos_visitados": 0, "ramas_podadas": 0, "profundidad_maxima": 0}

    def bajar(sub: pd.DataFrame, combinacion: Dict[str, Any], nivel: int) -> None:
        stats["nodos_visitados"] += 1
        stats["profundidad_maxima"] = max(stats["profundidad_maxima"], nivel)

        if len(sub) > 0:
            mediana = float(sub[respuesta].median())
            if combinacion and len(sub) >= soporte_min and mediana >= umbral:
                hallazgos.append({**combinacion, "n": len(sub), "mediana": round(mediana, 2),
                                  "nivel": nivel})

        if nivel >= len(factores):
            return

        factor = factores[nivel]
        for valor in sorted(sub[factor].dropna().unique()):
            bajar(sub[sub[factor] == valor], {**combinacion, factor: valor}, nivel + 1)

    bajar(df, {}, 0)
    hallazgos.sort(key=lambda h: h["mediana"], reverse=True)
    return hallazgos, stats


def _validar(df: pd.DataFrame, factores: Sequence[str], respuesta: str) -> None:
    """Comprueba las precondiciones comunes a las dos exploraciones."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"se esperaba un DataFrame, llegó {type(df).__name__}")
    if len(factores) == 0:
        raise ValueError("hay que indicar al menos un factor de exploración")
    faltan = [c for c in list(factores) + [respuesta] if c not in df.columns]
    if faltan:
        raise KeyError(f"columnas ausentes en el DataFrame: {faltan}")
    if not pd.api.types.is_numeric_dtype(df[respuesta]):
        raise TypeError(f"'{respuesta}' debe ser numérica para calcular medianas")


# ═══════════════════════════════════════════════════════════════════════
#  3 · AGREGACIÓN ANIDADA
# ═══════════════════════════════════════════════════════════════════════
def agregacion_anidada(df: pd.DataFrame, externo: str, interno: str,
                       respuesta: str, soporte_min: int = 100) -> pd.DataFrame:
    """Duración mediana de `interno` dentro de cada `externo` (p. ej. jornada dentro de área).

    Además de la mediana por grupo, entrega la diferencia respecto de la mediana
    del grupo externo completo: eso es lo que permite decir «en esta área, la
    jornada vespertina se titula N semestres más tarde que el promedio del área».

    Los grupos con menos de `soporte_min` registros se marcan en la columna
    `suficiente`, porque una mediana sobre doce personas no es comparable con una
    sobre nueve mil.
    """
    _validar(df, [externo, interno], respuesta)

    base = (df.groupby([externo, interno])[respuesta]
              .agg(n="size", mediana="median")
              .reset_index())
    ref = df.groupby(externo)[respuesta].median().rename("mediana_area")
    out = base.merge(ref, on=externo)
    out["dif_vs_area"] = (out["mediana"] - out["mediana_area"]).round(2)
    out["suficiente"] = out["n"] >= soporte_min
    return out.sort_values("dif_vs_area", ascending=False).reset_index(drop=True)