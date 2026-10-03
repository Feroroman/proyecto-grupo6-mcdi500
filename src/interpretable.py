"""Fase 4 · Versión interpretable del dataset.

El conjunto que produjo la Fase 2 está optimizado para el análisis numérico, no
para la lectura humana: las categóricas se convirtieron en 36 columnas de ceros
y unos, y las continuas se reescalaron, de modo que un valor de -0,43 no admite
interpretación sustantiva.

Este módulo devuelve la versión legible. No invierte ninguna transformación,
porque no hace falta: el pipeline de la Fase 2 fue no destructivo y agregó
columnas en vez de reemplazarlas, así que las 41 originales siguen presentes.
Lo que sí hace es descartar las derivadas y corregir dos cosas que impiden
graficar bien: el sexo codificado como 1/2 y el orden de las variables
ordinales.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd

from src.transformacion import ORDEN_RANGO_EDAD, ORDEN_NIVEL_CARRERA

RUTA_LIMPIO = "data/processed/titulados_2025_pregrado_univ_limpio.csv"

NOMINALES_ONEHOT = ["tipo_inst_2", "jornada", "modalidad", "area_conocimiento", "region_sede"]

SEXO = {1: "Hombre", 2: "Mujer"}


def columnas_derivadas(df: pd.DataFrame) -> List[str]:
    """Las columnas que existen para el análisis y estorban al graficar."""
    fuera = [c for c in df.columns if c.endswith("_esc") or c.endswith("_ord")]
    for p in NOMINALES_ONEHOT:
        fuera += [c for c in df.columns if c.startswith(p + "_") and c != p
                  and not c.endswith("_imputada")]
    return sorted(set(fuera))


def cargar_interpretable(ruta: str = RUTA_LIMPIO) -> pd.DataFrame:
    """Devuelve el dataset con categorías y unidades originales, listo para graficar.

    Lanza FileNotFoundError si el archivo no existe: hay que generarlo antes
    ejecutando los notebooks F1 y F2.
    """
    p = Path(ruta)
    if not p.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Ejecuta antes notebooks/F1 y notebooks/F2 "
            f"para generarlo: los CSV no se versionan.")

    df = pd.read_csv(p, sep=";", low_memory=False)
    df = df.drop(columns=columnas_derivadas(df))

    # 1 · El sexo viene como 1 y 2. Sin etiqueta, la figura dice "1" y "2".
    #     Verificado contra la columna 'mujer' que derivó la Fase 2:
    #     gen_alu == 2 produce mujer == 1.
    if "gen_alu" in df.columns:
        df["sexo"] = df["gen_alu"].map(SEXO)

    # 2 · Las ordinales necesitan su orden declarado, o pandas las ordena
    #     alfabéticamente y "40 y más años" aparece antes que "15 a 19 Años".
    for col, orden in [("rango_edad", ORDEN_RANGO_EDAD),
                       ("nivel_carrera_1", ORDEN_NIVEL_CARRERA)]:
        if col in df.columns:
            df[col] = pd.Categorical(df[col], categories=orden, ordered=True)

    return df


def resumen_interpretable(df: pd.DataFrame) -> pd.DataFrame:
    """Qué quedó en el dataset, por tipo. Para citar en el informe."""
    filas = []
    for c in df.columns:
        t = ("ordenada" if isinstance(df[c].dtype, pd.CategoricalDtype)
             else "numérica" if pd.api.types.is_numeric_dtype(df[c]) else "texto")
        filas.append({"columna": c, "tipo": t, "valores_unicos": df[c].nunique(),
                      "nulos": int(df[c].isna().sum())})
    return pd.DataFrame(filas)
