"""Fase 4 · Las tablas agregadas que alimentan cada figura.

Ninguna figura se construye sobre las 105.060 observaciones: se construye sobre
una tabla resumen. Calcularlas en un paso separado permite verificarlas antes de
dibujarlas, y es lo que recibe quien hace las figuras.

Todas incluyen el tamaño del grupo. Una barra calculada sobre 543 observaciones
ocupa el mismo espacio visual que una sobre 82.194 y transmite una certeza que
no tiene: el n es una advertencia, no un dato accesorio.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

import pandas as pd

RESPUESTA = "dur_total_carr"
BANDERA = "anio_ing_carr_ori_imputada"


def _verificar(df: pd.DataFrame, columnas) -> None:
    faltan = [c for c in columnas if c not in df.columns]
    if faltan:
        raise KeyError(f"El dataset no tiene las columnas {faltan}; "
                       f"¿se cargó con cargar_interpretable()?")


def tabla_distribucion(df: pd.DataFrame) -> dict:
    """F1 · Cifras de la distribución de la duración total."""
    _verificar(df, [RESPUESTA])
    s = df[RESPUESTA].dropna()
    return {"n": len(s), "mediana": s.median(), "media": round(s.mean(), 2),
            "p25": s.quantile(.25), "p75": s.quantile(.75),
            "min": s.min(), "max": s.max()}


def tabla_tamanos(df: pd.DataFrame, columna: str = "area_conocimiento") -> pd.DataFrame:
    """F2 · Cuántos titulados hay en cada categoría, de mayor a menor."""
    _verificar(df, [columna])
    t = df[columna].value_counts().rename_axis(columna).reset_index(name="n")
    t["porcentaje"] = (100 * t["n"] / t["n"].sum()).round(1)
    return t


def tabla_por_grupo(df: pd.DataFrame, columna: str = "jornada") -> pd.DataFrame:
    """F3 · Duración mediana por categoría, con su n, ordenada por duración."""
    _verificar(df, [columna, RESPUESTA])
    t = (df.groupby(columna, observed=True)[RESPUESTA]
           .agg(n="size", mediana="median", media="mean", p25=lambda s: s.quantile(.25),
                p75=lambda s: s.quantile(.75))
           .round(2).reset_index())
    return t.sort_values("mediana", ascending=False).reset_index(drop=True)


def serie_por_grupo(df: pd.DataFrame, columna: str = "jornada") -> pd.DataFrame:
    """F4 · Las observaciones sin agregar, para la caja con puntos."""
    _verificar(df, [columna, RESPUESTA])
    return df[[columna, RESPUESTA]].dropna()


def tabla_anidada(df: pd.DataFrame, externo: str = "area_conocimiento",
                  interno: str = "jornada", soporte_min: int = 100) -> pd.DataFrame:
    """F5 · Duración mediana de `interno` dentro de cada `externo`.

    Marca en `suficiente` los grupos que no alcanzan el soporte mínimo, para
    que la figura pueda declararlos o agruparlos en vez de dibujarlos como si
    fueran comparables.
    """
    _verificar(df, [externo, interno, RESPUESTA])
    t = (df.groupby([externo, interno], observed=True)[RESPUESTA]
           .agg(n="size", mediana="median").round(2).reset_index())
    ref = df.groupby(externo, observed=True)[RESPUESTA].median().rename("mediana_area")
    t = t.merge(ref, on=externo)
    t["dif_vs_area"] = (t["mediana"] - t["mediana_area"]).round(2)
    t["suficiente"] = t["n"] >= soporte_min
    return t.sort_values([externo, "mediana"], ascending=[True, False]).reset_index(drop=True)


def tabla_imputacion(df: pd.DataFrame, columna: str = "jornada") -> pd.DataFrame:
    """F6 · Qué porcentaje de cada categoría tiene el año de ingreso imputado.

    Es la figura que declara el límite del análisis: si la imputación se
    concentra en unas categorías y no en otras, la comparación entre ellas
    arrastra una variable de confusión.
    """
    _verificar(df, [columna, BANDERA])
    t = (pd.crosstab(df[columna], df[BANDERA], normalize="index")
           .mul(100).round(1))
    t.columns = ["observados_pct", "imputados_pct"]
    t["n"] = df[columna].value_counts()
    return t.sort_values("imputados_pct", ascending=False).reset_index()


def todas(df: pd.DataFrame) -> dict:
    """Las seis tablas de una vez, para pasárselas a quien hace las figuras."""
    return {"f1_distribucion": tabla_distribucion(df),
            "f2_tamanos": tabla_tamanos(df),
            "f3_por_jornada": tabla_por_grupo(df, "jornada"),
            "f4_serie": serie_por_grupo(df, "jornada"),
            "f5_anidada": tabla_anidada(df),
            "f6_imputacion": tabla_imputacion(df)}
