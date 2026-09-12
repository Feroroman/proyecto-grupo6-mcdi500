"""Pruebas de las funciones del pipeline: caso normal, caso límite y excepción.

Ejecutar desde la raíz del repositorio:
    python tests/test_pipeline.py          (sin dependencias extra)
    python -m pytest tests/                (si pytest está instalado)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import escalado, exploracion, limpieza, transformacion, validacion  # noqa: E402


def _df():
    return pd.DataFrame({"anio": [2020, 1900, 2021, 2021, 1900, 2022],
                         "dur": [8.0, 10.0, 12.0, 9.0, 40.0, 10.0],
                         "jornada": ["Diurna", "Diurna", "Vespertina", "Diurna", "A Distancia", "Diurna"],
                         "edad": ["20 a 24 Años", "25 a 29 Años", "40 y más años", "20 a 24 Años", "Sin Información", "30 a 34 Años"]})


# ---- caso normal
def test_codigo_a_nulo_normal():
    out, n = limpieza.codigo_a_nulo(_df(), "anio", 1900)
    assert n == 2 and out["anio"].isna().sum() == 2
    assert (_df()["anio"] == 1900).sum() == 2, "la función no debe modificar el original"


def test_imputar_mediana_crea_bandera():
    df, _ = limpieza.codigo_a_nulo(_df(), "anio", 1900)
    out, cifras = limpieza.imputar_mediana(df, "anio")
    assert out["anio"].isna().sum() == 0 and out["anio_imputada"].sum() == 2 and cifras["n_imputados"] == 2


def test_atipicos_ric_detecta_extremo():
    r = exploracion.atipicos_ric(_df()["dur"])
    assert r["n_atipicos"] == 1  # el 40


def test_ordinal_respeta_orden_declarado():
    out, mapa = transformacion.codificar_ordinal(_df(), "edad", transformacion.ORDEN_RANGO_EDAD)
    assert mapa["20 a 24 Años"] < mapa["40 y más años"]
    assert out["edad_ord"].isna().sum() == 1  # 'Sin Información' queda fuera


def test_one_hot_suma_uno():
    out, cols = transformacion.one_hot(_df(), ["jornada"])
    assert (out[cols].sum(axis=1) == 1).all() and len(cols) == 3


def test_escaladores_cumplen_propiedad():
    s = _df()["dur"]
    assert validacion.verificar_propiedad_escalador(escalado.escalar_estandar(s), "estandar")
    assert validacion.verificar_propiedad_escalador(escalado.escalar_minmax(s), "minmax")
    assert validacion.verificar_propiedad_escalador(escalado.escalar_robusto(s), "robusto")


# ---- caso límite
def test_columna_sin_nulos_no_imputa_nada():
    out, cifras = limpieza.imputar_mediana(_df(), "dur")
    assert cifras["n_imputados"] == 0 and out["dur_imputada"].sum() == 0


def test_una_sola_categoria_one_hot():
    df = pd.DataFrame({"x": ["a", "a", "a"]})
    out, cols = transformacion.one_hot(df, ["x"])
    assert cols == ["x_a"] and (out["x_a"] == 1).all()


def test_eliminar_duplicados_sin_duplicados():
    out, n = limpieza.eliminar_duplicados(_df())
    assert n == 0 and len(out) == 6


def test_atipicos_serie_vacia():
    r = exploracion.atipicos_ric(pd.Series([], dtype=float, name="v"))
    assert r["n_atipicos"] == 0


# ---- excepciones
def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


def test_excepciones():
    assert _raises(lambda: limpieza.codigo_a_nulo(_df(), "no_existe", 1900), KeyError)
    assert _raises(lambda: exploracion.atipicos_ric(_df()["jornada"]), TypeError)
    assert _raises(lambda: escalado.escalar_estandar(pd.Series([1.0, np.nan], name="z")), ValueError)
    assert _raises(lambda: escalado.escalar_minmax(pd.Series([3.0, 3.0], name="c")), ValueError)
    assert _raises(lambda: exploracion.perfil_faltantes(pd.DataFrame()), ValueError)
    assert _raises(lambda: transformacion.agrupar_raras(_df(), "jornada", 0), ValueError)


if __name__ == "__main__":
    pruebas = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    fallos = 0
    for nombre, f in pruebas:
        try:
            f(); print(f"OK    {nombre}")
        except AssertionError as e:
            fallos += 1; print(f"FALLA {nombre}: {e}")
    print(f"\n{len(pruebas) - fallos}/{len(pruebas)} pruebas superadas")
    sys.exit(1 if fallos else 0)
