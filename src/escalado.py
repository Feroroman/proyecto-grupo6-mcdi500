"""Fase 2 · Paso 9: escalamiento. Tres escaladores implementados con NumPy/pandas.

Equivalentes a StandardScaler, MinMaxScaler y RobustScaler de scikit-learn; se
implementan aquí para que sus propiedades se puedan verificar de forma explícita.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _check(s: pd.Series) -> pd.Series:
    if not pd.api.types.is_numeric_dtype(s):
        raise TypeError(f"'{s.name}' no es numérica")
    if s.isna().any():
        raise ValueError(f"'{s.name}' tiene nulos: imputar antes de escalar")
    return s.astype(float)


def escalar_estandar(s: pd.Series) -> pd.Series:
    """(x - media) / desviación → media 0, desviación 1."""
    s = _check(s)
    sd = s.std(ddof=0)
    if sd == 0:
        raise ValueError(f"'{s.name}' es constante: no se puede escalar")
    return (s - s.mean()) / sd


def escalar_minmax(s: pd.Series) -> pd.Series:
    """(x - min) / (max - min) → rango [0, 1]."""
    s = _check(s)
    rango = s.max() - s.min()
    if rango == 0:
        raise ValueError(f"'{s.name}' es constante: no se puede escalar")
    return (s - s.min()) / rango


def escalar_robusto(s: pd.Series) -> pd.Series:
    """(x - mediana) / RIC → mediana 0, rango intercuartílico 1."""
    s = _check(s)
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    ric = q3 - q1
    if ric == 0:
        raise ValueError(f"'{s.name}' tiene RIC = 0: no se puede escalar con RobustScaler")
    return (s - s.median()) / ric


def comparar_escaladores(s: pd.Series) -> pd.DataFrame:
    """Tabla con media, desviación, mediana, RIC, mín y máx de la serie bajo los tres escaladores."""
    filas = {}
    for nombre, f in [("original", lambda x: x.astype(float)), ("estandar", escalar_estandar),
                      ("minmax", escalar_minmax), ("robusto", escalar_robusto)]:
        try:
            e = f(s)
            filas[nombre] = {"media": e.mean(), "desv": e.std(ddof=0), "mediana": e.median(),
                             "ric": e.quantile(0.75) - e.quantile(0.25), "min": e.min(), "max": e.max()}
        except ValueError as err:
            filas[nombre] = {"media": np.nan, "desv": np.nan, "mediana": np.nan, "ric": np.nan, "min": np.nan, "max": str(err)}
    return pd.DataFrame(filas).T.round(3)
