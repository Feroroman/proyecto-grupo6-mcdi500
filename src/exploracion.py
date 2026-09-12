"""Fase 2 · Paso 6: medir antes de tocar nada.

Funciones puras que describen un DataFrame sin modificarlo. Todas devuelven
DataFrames o diccionarios para que el notebook los muestre y la bitácora los cite.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def perfil_faltantes(df: pd.DataFrame, codigos: dict[str, object] | None = None) -> pd.DataFrame:
    """Cuenta nulos reales y códigos de relleno (p. ej. 1900) por columna.

    Parameters
    ----------
    df : DataFrame a perfilar (no se modifica).
    codigos : {columna: valor} que debe contarse como faltante encubierto.

    Returns
    -------
    DataFrame con columnas nulos, pct_nulos, codigo, pct_codigo, ordenado por total.
    """
    if df.empty:
        raise ValueError("El DataFrame está vacío: no hay nada que perfilar")
    codigos = codigos or {}
    n = len(df)
    filas = []
    for col in df.columns:
        nulos = int(df[col].isna().sum())
        cod = int((df[col] == codigos[col]).sum()) if col in codigos else 0
        filas.append({"columna": col, "nulos": nulos, "pct_nulos": round(100 * nulos / n, 2),
                      "codigo_relleno": cod, "pct_codigo": round(100 * cod / n, 2)})
    out = pd.DataFrame(filas).set_index("columna")
    out["pct_total"] = out["pct_nulos"] + out["pct_codigo"]
    return out.sort_values("pct_total", ascending=False)


def atipicos_ric(serie: pd.Series, k: float = 1.5) -> dict[str, float]:
    """Cuenta valores atípicos con la regla del rango intercuartílico.

    Devuelve q1, q3, ric, límites y el número y porcentaje de atípicos.
    Lanza TypeError si la serie no es numérica.
    """
    if not pd.api.types.is_numeric_dtype(serie):
        raise TypeError(f"'{serie.name}' no es numérica")
    s = serie.dropna()
    if s.empty:
        return {"q1": np.nan, "q3": np.nan, "ric": np.nan, "lim_inf": np.nan, "lim_sup": np.nan, "n_atipicos": 0, "pct": 0.0}
    q1, q3 = float(s.quantile(0.25)), float(s.quantile(0.75))
    ric = q3 - q1
    lim_inf, lim_sup = q1 - k * ric, q3 + k * ric
    n_at = int(((s < lim_inf) | (s > lim_sup)).sum())
    return {"q1": q1, "q3": q3, "ric": ric, "lim_inf": lim_inf, "lim_sup": lim_sup,
            "n_atipicos": n_at, "pct": round(100 * n_at / len(s), 2)}


def resumen_categorias(df: pd.DataFrame, columnas: list[str], top: int = 8) -> pd.DataFrame:
    """Tabla con número de categorías y las más frecuentes por columna."""
    filas = []
    for c in columnas:
        vc = df[c].value_counts(dropna=False)
        filas.append({"columna": c, "n_categorias": int(df[c].nunique(dropna=True)),
                      "mas_frecuentes": ", ".join(f"{k} ({v:,})" for k, v in vc.head(top).items())})
    return pd.DataFrame(filas).set_index("columna")
