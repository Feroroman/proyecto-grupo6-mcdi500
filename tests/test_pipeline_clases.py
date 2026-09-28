"""Pruebas de la jerarquía de clases del pipeline (src/pipeline.py · Fase 3).

Tres tipos de caso, como en las pruebas de la Fase 2:
  · caso normal    — la clase hace lo esperado y NO modifica el DataFrame original
  · caso límite    — sin nulos, una sola categoría, una sola fila
  · caso excepción — columna inexistente, tipo equivocado, apply sin fit

Se ejecuta con:  python tests/test_pipeline_clases.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.pipeline import (  # noqa: E402
    AgrupadorRaras, CodificadorOneHot, CodificadorOrdinal, CodigoAFaltante,
    EliminadorConstantes, EliminadorDuplicados, EscaladorRobusto,
    ImputadorMedianaPorGrupo, Pipeline, Transformador,
)

superadas, fallidas = 0, 0


def check(titulo: str, condicion: bool, detalle: str = "") -> None:
    global superadas, fallidas
    if condicion:
        superadas += 1
        print(f"  OK    {titulo}")
    else:
        fallidas += 1
        print(f"  FALLA {titulo}  {detalle}")


def espera_error(titulo: str, funcion, error) -> None:
    try:
        funcion()
    except error:
        check(titulo, True)
    except Exception as e:  # noqa: BLE001
        check(titulo, False, f"lanzó {type(e).__name__} en vez de {error.__name__}")
    else:
        check(titulo, False, "no lanzó ninguna excepción")


def datos() -> pd.DataFrame:
    """Muestra sintética que imita la estructura del dataset de titulados."""
    return pd.DataFrame({
        "anio_ing": [2015, 1900, 2016, 1900, 2017, 2015, 2016, 2018],
        "jornada":  ["Diurno", "Diurno", "Vespertino", "Vespertino", "Diurno", "Diurno", "Vespertino", "Diurno"],
        "rango_edad": ["20 a 24 Años", "25 a 29 Años", "20 a 24 Años", "30 a 34 Años",
                       "20 a 24 Años", "25 a 29 Años", "20 a 24 Años", "20 a 24 Años"],
        "carrera":  ["Derecho", "Derecho", "Derecho", "Rara1", "Derecho", "Rara2", "Derecho", "Derecho"],
        "duracion": [10.0, 12.0, 11.0, 24.0, 9.0, 10.0, 13.0, 8.0],
        "constante": ["X"] * 8,
    })


def main() -> int:
    """Ejecuta la suite completa y devuelve 0 si todo pasa."""
    print("\n── Caso normal ─────────────────────────────────────────────")

    df = datos()
    copia = df.copy()

    t = EliminadorDuplicados().fit(df)
    out = t.apply(pd.concat([df, df.iloc[[0]]], ignore_index=True))
    check("EliminadorDuplicados quita la fila repetida", len(out) == len(df))
    check("EliminadorDuplicados no toca el original", df.equals(copia))

    t = CodigoAFaltante("anio_ing", 1900)
    out = t.fit_apply(df)
    check("CodigoAFaltante convierte los dos 1900 en NaN", out["anio_ing"].isna().sum() == 2)
    check("CodigoAFaltante informa las cifras", t.cifras["reemplazos"] == 2)
    check("CodigoAFaltante no toca el original", df.equals(copia))

    t = ImputadorMedianaPorGrupo("anio_ing", "jornada")
    imputado = t.fit_apply(out)
    check("ImputadorMedianaPorGrupo no deja nulos", imputado["anio_ing"].isna().sum() == 0)
    check("ImputadorMedianaPorGrupo deja la bandera", "anio_ing_imputada" in imputado.columns)
    check("La bandera marca exactamente los 2 imputados", imputado["anio_ing_imputada"].sum() == 2)
    check("Las medianas quedan guardadas tras fit", t.medianas_ is not None)

    t = EliminadorConstantes()
    out = t.fit_apply(df)
    check("EliminadorConstantes elimina 'constante'", "constante" not in out.columns)
    check("EliminadorConstantes informa cuál eliminó", t.cifras["columnas"] == ["constante"])

    orden = ["20 a 24 Años", "25 a 29 Años", "30 a 34 Años"]
    t = CodificadorOrdinal("rango_edad", orden)
    out = t.fit_apply(df)
    check("CodificadorOrdinal respeta el orden declarado", out.loc[0, "rango_edad_ord"] == 0)
    check("CodificadorOrdinal codifica el nivel más alto", out["rango_edad_ord"].max() == 2)

    t = AgrupadorRaras("carrera", min_frec=2)
    out = t.fit_apply(df)
    check("AgrupadorRaras agrupa las 2 categorías raras", (out["carrera_agrupada"] == "OTRA").sum() == 2)
    check("AgrupadorRaras conserva la frecuente", (out["carrera_agrupada"] == "Derecho").sum() == 6)
    check("AgrupadorRaras no toca la columna original", out["carrera"].equals(df["carrera"]))

    t = CodificadorOneHot(["jornada"])
    out = t.fit_apply(df)
    check("CodificadorOneHot crea una columna por categoría", t.cifras["columnas_generadas"] == 2)
    check("Cada fila suma exactamente 1 en el grupo one-hot",
          bool((out[["jornada__Diurno", "jornada__Vespertino"]].sum(axis=1) == 1).all()))

    t = EscaladorRobusto(["duracion"])
    out = t.fit_apply(df)
    q1, q3 = out["duracion_esc"].quantile(0.25), out["duracion_esc"].quantile(0.75)
    check("EscaladorRobusto deja mediana 0", abs(out["duracion_esc"].median()) < 1e-9)
    check("EscaladorRobusto deja RIC 1", abs((q3 - q1) - 1) < 1e-9)

    pipe = Pipeline([
        EliminadorDuplicados(),
        CodigoAFaltante("anio_ing", 1900),
        ImputadorMedianaPorGrupo("anio_ing", "jornada"),
        EliminadorConstantes(),
        AgrupadorRaras("carrera", min_frec=2),
        CodificadorOneHot(["jornada", "carrera"]),
        EscaladorRobusto(["duracion"]),
    ], nombre="Pipeline de prueba")

    final = pipe.fit_apply(df, verboso=False)
    check("El pipeline ejecuta las 7 etapas", len(pipe.mediciones_) == 7)
    check("El resumen trae una fila por etapa", len(pipe.resumen()) == 7)
    check("El resumen trae tiempo y memoria",
          {"segundos", "memoria_pico_mb", "pct_tiempo"} <= set(pipe.resumen().columns))
    check("etapa_dominante() devuelve una etapa real",
          pipe.etapa_dominante()["etapa"] in [e.nombre for e in pipe.etapas])
    check("El pipeline no modifica el DataFrame original", df.equals(copia))
    check("cifras() devuelve una tabla no vacía", len(pipe.cifras()) > 0)

    # La prueba que importa: la clase y las funciones de la Fase 2 dan lo mismo
    from src.limpieza import eliminar_duplicados  # noqa: E402

    por_funcion, _ = eliminar_duplicados(df)
    por_clase = EliminadorDuplicados().fit_apply(df)
    check("La clase da el MISMO resultado que la función de la Fase 2",
          por_funcion.equals(por_clase))


    print("\n── Caso límite ─────────────────────────────────────────────")

    una_fila = df.iloc[[0]].copy()
    check("EliminadorDuplicados sobre una sola fila", len(EliminadorDuplicados().fit_apply(una_fila)) == 1)

    sin_codigo = df[df["anio_ing"] != 1900].copy()
    t = CodigoAFaltante("anio_ing", 1900)
    t.fit_apply(sin_codigo)
    check("CodigoAFaltante con cero coincidencias informa 0", t.cifras["reemplazos"] == 0)

    una_cat = df.copy()
    una_cat["carrera"] = "Derecho"
    t = AgrupadorRaras("carrera", min_frec=2)
    out = t.fit_apply(una_cat)
    check("AgrupadorRaras con una sola categoría no agrupa nada", (out["carrera_agrupada"] == "OTRA").sum() == 0)

    sin_nulos = df.copy()
    t = ImputadorMedianaPorGrupo("anio_ing", "jornada")
    out = t.fit_apply(sin_nulos)
    check("ImputadorMediana sin nulos imputa 0 casos", t.cifras["imputados"] == 0)

    check("Pipeline de una sola etapa funciona",
          len(Pipeline([EliminadorConstantes()]).fit_apply(df, verboso=False)) == len(df))


    print("\n── Caso excepción ──────────────────────────────────────────")

    espera_error("apply() sin fit() lanza RuntimeError",
                 lambda: EliminadorDuplicados().apply(df), RuntimeError)
    espera_error("fit() con algo que no es DataFrame lanza TypeError",
                 lambda: EliminadorDuplicados().fit([1, 2, 3]), TypeError)
    espera_error("Columna inexistente lanza KeyError",
                 lambda: CodigoAFaltante("no_existe", 1900).fit(df), KeyError)
    espera_error("Escalar una columna de texto lanza TypeError",
                 lambda: EscaladorRobusto(["jornada"]).fit(df), TypeError)
    espera_error("Ordinal con categoría fuera del orden lanza ValueError",
                 lambda: CodificadorOrdinal("rango_edad", ["20 a 24 Años"]).fit(df), ValueError)
    espera_error("One-hot con columna ausente lanza KeyError",
                 lambda: CodificadorOneHot(["no_existe"]).fit(df), KeyError)
    espera_error("Pipeline vacío lanza ValueError",
                 lambda: Pipeline([]), ValueError)
    espera_error("Pipeline con algo que no es Transformador lanza TypeError",
                 lambda: Pipeline(["no soy un transformador"]), TypeError)
    espera_error("resumen() antes de ejecutar lanza RuntimeError",
                 lambda: Pipeline([EliminadorConstantes()]).resumen(), RuntimeError)

    const = pd.DataFrame({"x": [5.0] * 6})
    espera_error("Escalar una columna sin dispersión lanza ValueError",
                 lambda: EscaladorRobusto(["x"]).fit(const), ValueError)


    print("\n" + "─" * 60)
    print(f"{superadas}/{superadas + fallidas} pruebas superadas")
    return 0 if fallidas == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
