"""Fase 2 · Paso 7: limpieza e imputación.

Cada función recibe un DataFrame, devuelve uno NUEVO (nunca modifica el original)
y entrega además las cifras que justifican la decisión.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def eliminar_duplicados(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Elimina filas exactamente duplicadas. Devuelve (df_limpio, n_eliminadas)."""
    n_antes = len(df)
    out = df.drop_duplicates().reset_index(drop=True)
    return out, n_antes - len(out)


def codigo_a_nulo(df: pd.DataFrame, columna: str, codigo: object) -> tuple[pd.DataFrame, int]:
    """Reemplaza un código de relleno (p. ej. 1900 = sin información) por NaN.

    Devuelve (df_nuevo, n_reemplazos). Lanza KeyError si la columna no existe.
    """
    if columna not in df.columns:
        raise KeyError(f"La columna '{columna}' no existe en el DataFrame")
    out = df.copy()
    mascara = out[columna] == codigo
    out.loc[mascara, columna] = np.nan
    return out, int(mascara.sum())


def eliminar_columnas_constantes(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Elimina columnas con un único valor (no aportan información)."""
    constantes = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]
    return df.drop(columns=constantes), constantes


def comparar_imputaciones(df: pd.DataFrame, columna: str, grupo: str | None = None) -> pd.DataFrame:
    """Compara cuatro estrategias para los nulos de `columna`: eliminar, media, mediana, mediana por grupo.

    Para cada una informa filas resultantes, media, desviación estándar y el cambio
    porcentual de la desviación respecto de los datos observados (sin nulos).
    """
    s = df[columna]
    base = s.dropna()
    if base.empty:
        raise ValueError(f"'{columna}' no tiene valores observados para comparar")
    std0 = base.std()
    filas = [{"estrategia": "observados (referencia)", "n": len(base), "media": base.mean(), "desv": std0, "cambio_desv_pct": 0.0}]

    def fila(nombre, serie):
        return {"estrategia": nombre, "n": int(serie.notna().sum()), "media": serie.mean(), "desv": serie.std(),
                "cambio_desv_pct": 100 * (serie.std() - std0) / std0}

    filas.append(fila("eliminar filas", base))
    filas.append(fila("imputar media", s.fillna(base.mean())))
    filas.append(fila("imputar mediana", s.fillna(base.median())))
    if grupo is not None:
        med_grupo = df.groupby(grupo)[columna].transform("median")
        filas.append(fila(f"imputar mediana por {grupo}", s.fillna(med_grupo).fillna(base.median())))
    out = pd.DataFrame(filas).set_index("estrategia")
    return out.round(3)


def imputar_mediana(df: pd.DataFrame, columna: str, grupo: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Imputa nulos con la mediana (global o por grupo) y crea la bandera <columna>_imputada.

    Devuelve (df_nuevo, cifras) con n_imputados, valor usado y cambio en la desviación.
    """
    if columna not in df.columns:
        raise KeyError(f"La columna '{columna}' no existe en el DataFrame")
    out = df.copy()
    nulos = out[columna].isna()
    std_antes = out[columna].std()
    if grupo:
        valores = out.groupby(grupo)[columna].transform("median")
        valores = valores.fillna(out[columna].median())
        out.loc[nulos, columna] = valores[nulos]
        valor = "mediana por " + grupo
    else:
        valor = float(out[columna].median())
        out.loc[nulos, columna] = valor
    out[f"{columna}_imputada"] = nulos.astype(int)
    std_despues = out[columna].std()
    cifras = {"n_imputados": int(nulos.sum()), "pct": round(100 * nulos.mean(), 2), "valor": valor,
              "cambio_desv_pct": round(100 * (std_despues - std_antes) / std_antes, 2) if std_antes else 0.0}
    return out, cifras
