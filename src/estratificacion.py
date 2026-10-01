"""Fase 4 · Estratificación: ¿persiste la diferencia de jornada al controlar por área?

Divide la comparación de jornadas por área de conocimiento y compara el orden
resultante en cada área con el orden observado en el dataset completo. Es el
procedimiento estándar para detectar confusión y la paradoja de Simpson: si la
jornada con menor (o mayor) duración mediana cambia según el área, la diferencia
global puede deberse, en parte o del todo, a la composición por área y no a la
jornada en sí.

Se apoya en `agregacion_anidada` (src/algoritmos.py, Fase 3), que ya calcula la
mediana de cada combinación área-jornada junto con su soporte.

Autoría: César Lorca Bacián · MCDI500 · Fase 4
"""
from __future__ import annotations

from typing import Any, Dict, List, Sequence, Tuple

import pandas as pd

from src.algoritmos import agregacion_anidada


def _validar(df: pd.DataFrame, columnas: Sequence[str], respuesta: str) -> None:
    """Precondiciones comunes: DataFrame real, columnas presentes, respuesta numérica."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"se esperaba un DataFrame, llegó {type(df).__name__}")
    faltan = [c for c in list(columnas) + [respuesta] if c not in df.columns]
    if faltan:
        raise KeyError(f"columnas ausentes en el DataFrame: {faltan}")
    if not pd.api.types.is_numeric_dtype(df[respuesta]):
        raise TypeError(f"'{respuesta}' debe ser numérica para calcular medianas")


def estratificar_por_area(df: pd.DataFrame, respuesta: str,
                          col_area: str = "area", col_jornada: str = "jornada",
                          soporte_min: int = 100) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Compara el orden de jornadas por duración, global versus dentro de cada área.

    Primero calcula la mediana de `respuesta` por jornada sobre el DataFrame
    completo, para saber cuál jornada tiene la mediana más baja y cuál la más
    alta (los dos "extremos" de la comparación principal, p. ej. Diurna y
    A Distancia). Después usa `agregacion_anidada` para obtener la misma mediana
    pero dentro de cada área, y revisa si esos mismos dos extremos se mantienen
    en cada área que tenga al menos dos jornadas con soporte suficiente.

    Una comparación en la que los extremos coinciden en todas las áreas revisadas
    es evidencia de que la diferencia de jornada no se explica por el área. Si se
    invierten en alguna área, esa área queda señalada en el diagnóstico: es ahí
    donde el informe debe matizar la conclusión, no antes.

    Parámetros
    ----------
    df : DataFrame con las columnas de área, jornada y la variable de respuesta.
    respuesta : columna numérica a comparar (p. ej. 'dur_total_carr').
    col_area : nombre de la columna de área de conocimiento.
    col_jornada : nombre de la columna de jornada.
    soporte_min : mínimo de registros por combinación área-jornada para
        considerarla en el diagnóstico (se pasa tal cual a `agregacion_anidada`).

    Devuelve
    --------
    (tabla, diagnostico)
    · tabla: la salida completa de `agregacion_anidada` (una fila por combinación
      área-jornada, con su `n`, `mediana`, `dif_vs_area` y `suficiente`).
    · diagnostico: diccionario con
        - 'orden_global': jornadas ordenadas de menor a mayor mediana global
        - 'extremo_bajo_global' / 'extremo_alto_global': las dos jornadas extremas
        - 'areas_consistentes': áreas donde esos extremos se repiten
        - 'areas_invertidas': áreas donde el orden se invierte o cambia
        - 'persiste': True solo si hay al menos un área comparable y ninguna
          invierte el orden

    Lanza TypeError si `df` no es un DataFrame o `respuesta` no es numérica,
    KeyError si falta alguna columna.

    Nota: las áreas con menos de dos jornadas con soporte suficiente no entran
    en la comparación (no hay con qué contrastar un orden), y no cuentan ni como
    consistentes ni como invertidas.
    """
    _validar(df, [col_area, col_jornada], respuesta)

    tabla = agregacion_anidada(df, col_area, col_jornada, respuesta, soporte_min)

    orden_global = list(df.groupby(col_jornada)[respuesta].median().sort_values().index)

    # CASO LÍMITE: sin datos (o con una sola jornada) no hay un contraste que estratificar.
    if len(orden_global) < 2:
        extremo_bajo_global = orden_global[0] if orden_global else None
        extremo_alto_global = orden_global[-1] if orden_global else None
        return tabla, {
            "orden_global": orden_global,
            "extremo_bajo_global": extremo_bajo_global,
            "extremo_alto_global": extremo_alto_global,
            "areas_consistentes": [],
            "areas_invertidas": [],
            "persiste": False,
        }

    extremo_bajo_global = orden_global[0]
    extremo_alto_global = orden_global[-1]

    areas_consistentes: List[Any] = []
    areas_invertidas: List[Any] = []

    tabla_suficiente = tabla[tabla["suficiente"]]
    for area, grupo in tabla_suficiente.groupby(col_area):
        if len(grupo) < 2:
            continue                                    # nada que contrastar en esta área
        extremos_area = grupo.sort_values("mediana")
        bajo_area = extremos_area.iloc[0][col_jornada]
        alto_area = extremos_area.iloc[-1][col_jornada]
        if bajo_area == extremo_bajo_global and alto_area == extremo_alto_global:
            areas_consistentes.append(area)
        else:
            areas_invertidas.append(area)

    diagnostico: Dict[str, Any] = {
        "orden_global": orden_global,
        "extremo_bajo_global": extremo_bajo_global,
        "extremo_alto_global": extremo_alto_global,
        "areas_consistentes": areas_consistentes,
        "areas_invertidas": areas_invertidas,
        "persiste": len(areas_invertidas) == 0 and len(areas_consistentes) > 0,
    }
    return tabla, diagnostico
