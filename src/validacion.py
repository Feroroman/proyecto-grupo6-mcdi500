"""Fase 2 · Paso 10: validar es demostrar, no afirmar."""
from __future__ import annotations

import pandas as pd


def validar_dataset_final(df: pd.DataFrame, columnas_analisis: list[str], grupos_onehot: dict[str, list[str]],
                          n_filas_esperado: int) -> list[str]:
    """Ejecuta las comprobaciones del dataset procesado y devuelve la lista de checks superados.

    Lanza AssertionError con un mensaje claro en el primer check que falle.
    """
    ok: list[str] = []
    sub = df[columnas_analisis]
    assert sub.isna().sum().sum() == 0, f"Quedan nulos en columnas de análisis: {sub.isna().sum()[sub.isna().sum() > 0].to_dict()}"
    ok.append("sin nulos en columnas de análisis")
    no_num = [c for c in columnas_analisis if not pd.api.types.is_numeric_dtype(df[c])]
    assert not no_num, f"Columnas de análisis no numéricas: {no_num}"
    ok.append("todas las columnas de análisis son numéricas")
    for grupo, cols in grupos_onehot.items():
        sumas = df[cols].sum(axis=1)
        assert (sumas == 1).all(), f"El grupo one-hot '{grupo}' no suma 1 en {(sumas != 1).sum()} filas"
    ok.append(f"cada grupo one-hot suma 1 por fila ({len(grupos_onehot)} grupos)")
    assert not df.duplicated().any(), "Hay filas duplicadas"
    ok.append("sin filas duplicadas")
    assert len(df) == n_filas_esperado, f"Se esperaban {n_filas_esperado:,} filas y hay {len(df):,}"
    ok.append(f"se conservó el número de filas esperado ({n_filas_esperado:,})")
    return ok


def verificar_propiedad_escalador(serie: pd.Series, escalador: str, tol: float = 1e-6) -> bool:
    """Comprueba la propiedad que garantiza cada escalador."""
    if escalador == "estandar":
        return abs(serie.mean()) < tol and abs(serie.std(ddof=0) - 1) < tol
    if escalador == "minmax":
        return abs(serie.min()) < tol and abs(serie.max() - 1) < tol
    if escalador == "robusto":
        return abs(serie.median()) < tol and abs((serie.quantile(0.75) - serie.quantile(0.25)) - 1) < tol
    raise ValueError(f"Escalador desconocido: {escalador}")
