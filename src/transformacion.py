"""Fase 2 · Paso 8: transformación por tipo de variable."""
from __future__ import annotations

import pandas as pd

ORDEN_RANGO_EDAD = ["15 a 19 Años", "20 a 24 Años", "25 a 29 Años", "30 a 34 Años", "35 a 39 Años", "40 y más años"]
ORDEN_NIVEL_CARRERA = ["Técnico de Nivel Superior", "Licenciatura No Conducente a Título",
                       "Profesional Sin Licenciatura", "Profesional Con Licenciatura"]


def codificar_ordinal(df: pd.DataFrame, columna: str, orden: list[str]) -> tuple[pd.DataFrame, dict[str, int]]:
    """Codifica una variable ordinal con el orden DECLARADO por el equipo (0, 1, 2, ...).

    Los valores fuera del orden (p. ej. 'Sin Información') quedan como NaN.
    Devuelve (df_nuevo, mapa) y crea la columna <columna>_ord.
    """
    faltan = set(df[columna].dropna().unique()) - set(orden)
    mapa = {cat: i for i, cat in enumerate(orden)}
    out = df.copy()
    out[f"{columna}_ord"] = out[columna].map(mapa)
    if faltan:
        out.attrs[f"{columna}_fuera_de_orden"] = sorted(faltan)
    return out, mapa


def one_hot(df: pd.DataFrame, columnas: list[str]) -> tuple[pd.DataFrame, list[str]]:
    """One-hot encoding (una columna 0/1 por categoría). Devuelve (df_nuevo, columnas_creadas)."""
    dummies = pd.get_dummies(df[columnas], prefix=columnas, dtype=int)
    out = pd.concat([df, dummies], axis=1)
    return out, list(dummies.columns)


def agrupar_raras(df: pd.DataFrame, columna: str, min_frec: int, etiqueta: str = "OTRA") -> tuple[pd.DataFrame, int]:
    """Agrupa las categorías con menos de `min_frec` registros bajo `etiqueta`.

    Devuelve (df_nuevo, n_categorias_agrupadas) y crea la columna <columna>_agrupada.
    """
    if min_frec < 1:
        raise ValueError("min_frec debe ser >= 1")
    vc = df[columna].value_counts()
    raras = vc[vc < min_frec].index
    out = df.copy()
    out[f"{columna}_agrupada"] = out[columna].where(~out[columna].isin(raras), etiqueta)
    return out, int(len(raras))


def derivar_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Parsea fecha_obtencion_titulo (AAAAMMDD) y fec_nac_alu (AAAAMM); deriva mes de titulación y edad al titularse."""
    out = df.copy()
    fecha = pd.to_datetime(out["fecha_obtencion_titulo"].astype("Int64").astype(str), format="%Y%m%d", errors="coerce")
    nac = pd.to_datetime(out["fec_nac_alu"].astype("Int64").astype(str) + "01", format="%Y%m%d", errors="coerce")
    out["mes_titulacion"] = fecha.dt.month
    out["edad_titulacion"] = ((fecha - nac).dt.days / 365.25).round(1)
    return out


def binaria_01(df: pd.DataFrame, columna: str, valor_uno: object, nombre: str) -> pd.DataFrame:
    """Crea una columna 0/1 a partir de una binaria codificada de otra forma (p. ej. gen_alu 1/2)."""
    out = df.copy()
    out[nombre] = (out[columna] == valor_uno).astype(int)
    return out
