"""Pruebas de src/estratificacion.py (Fase 4).

Tres tipos de caso, igual que en la Fase 3:
  · caso normal    — la estratificación detecta persistencia e inversión
  · caso límite    — un área sin comparación posible, DataFrame vacío
  · caso excepción — columna inexistente, tipo inválido, respuesta no numérica

Se ejecuta con:  pytest tests/test_estratificacion.py
             o:  python tests/test_estratificacion.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.estratificacion import estratificar_por_area  # noqa: E402

superadas, fallidas = 0, 0
_MODO_SCRIPT = False


def check(titulo: str, condicion: bool, detalle: str = "") -> None:
    global superadas, fallidas
    if condicion:
        superadas += 1
        print(f"  OK    {titulo}")
    else:
        fallidas += 1
        print(f"  FALLA {titulo}  {detalle}")
        if not _MODO_SCRIPT:
            raise AssertionError(f"{titulo}  {detalle}".strip())


def espera_error(titulo: str, funcion, error) -> None:
    try:
        funcion()
    except error:
        check(titulo, True)
    except Exception as e:  # noqa: BLE001
        check(titulo, False, f"lanzó {type(e).__name__} en vez de {error.__name__}")
    else:
        check(titulo, False, "no lanzó ninguna excepción")


def _dataset_persistente() -> pd.DataFrame:
    """Diurna siempre más corta que Vespertina, en TODAS las áreas (sin confusión)."""
    filas = []
    for area, base in [("Salud", 12), ("Ingeniería", 10), ("Educación", 9)]:
        for _ in range(60):
            filas.append({"area": area, "jornada": "Diurna", "duracion": base})
            filas.append({"area": area, "jornada": "Vespertina", "duracion": base + 2})
    return pd.DataFrame(filas)


def _dataset_con_inversion() -> pd.DataFrame:
    """Igual que el anterior, pero en 'Arte' se invierte el orden (confusión simulada)."""
    df = _dataset_persistente()
    filas = []
    for _ in range(60):
        filas.append({"area": "Arte", "jornada": "Diurna", "duracion": 14})       # ahora MÁS larga
        filas.append({"area": "Arte", "jornada": "Vespertina", "duracion": 11})   # ahora MÁS corta
    return pd.concat([df, pd.DataFrame(filas)], ignore_index=True)


DF_PERSISTENTE = _dataset_persistente()
DF_INVERTIDO = _dataset_con_inversion()


# ═══════════════════════════════════════════════════════════════════════
#  CASO NORMAL
# ═══════════════════════════════════════════════════════════════════════
def test_normal_persiste_sin_confusion():
    tabla, diag = estratificar_por_area(DF_PERSISTENTE, "duracion", soporte_min=30)

    check("Detecta correctamente el extremo bajo global (Diurna)",
          diag["extremo_bajo_global"] == "Diurna")
    check("Detecta correctamente el extremo alto global (Vespertina)",
          diag["extremo_alto_global"] == "Vespertina")
    check("Las tres áreas quedan como consistentes",
          sorted(diag["areas_consistentes"]) == ["Educación", "Ingeniería", "Salud"],
          f"{diag['areas_consistentes']}")
    check("Ninguna área queda como invertida", diag["areas_invertidas"] == [])
    check("El diagnóstico marca que el patrón persiste", diag["persiste"] is True)
    check("La tabla trae una fila por combinación área-jornada", len(tabla) == 6)


def test_normal_detecta_inversion():
    tabla, diag = estratificar_por_area(DF_INVERTIDO, "duracion", soporte_min=30)

    check("Arte queda marcada como área invertida", "Arte" in diag["areas_invertidas"])
    check("Las otras tres áreas se mantienen consistentes",
          sorted(diag["areas_consistentes"]) == ["Educación", "Ingeniería", "Salud"])
    check("El diagnóstico marca que el patrón YA NO persiste en su totalidad",
          diag["persiste"] is False)


# ═══════════════════════════════════════════════════════════════════════
#  CASO LÍMITE
# ═══════════════════════════════════════════════════════════════════════
def test_limite_area_sin_comparacion_posible():
    # Un área con una sola jornada: no hay con qué contrastar el orden.
    extra = pd.DataFrame([{"area": "Derecho", "jornada": "Diurna", "duracion": 11}] * 40)
    df = pd.concat([DF_PERSISTENTE, extra], ignore_index=True)
    _, diag = estratificar_por_area(df, "duracion", soporte_min=30)

    check("El área con una sola jornada no se clasifica ni consistente ni invertida",
          "Derecho" not in diag["areas_consistentes"] and "Derecho" not in diag["areas_invertidas"])


def test_limite_sin_soporte_suficiente():
    # soporte_min más alto que cualquier grupo: ninguna área es comparable.
    _, diag = estratificar_por_area(DF_PERSISTENTE, "duracion", soporte_min=10_000)
    check("Sin soporte suficiente en ningún grupo, no hay áreas consistentes ni invertidas",
          diag["areas_consistentes"] == [] and diag["areas_invertidas"] == [])
    check("Sin ninguna área comparable, 'persiste' queda en False",
          diag["persiste"] is False)


def test_limite_una_sola_jornada_en_todo_el_dataset():
    df = DF_PERSISTENTE[DF_PERSISTENTE["jornada"] == "Diurna"]
    tabla, diag = estratificar_por_area(df, "duracion", soporte_min=30)
    check("Con una sola jornada global, no hay extremos que comparar",
          diag["extremo_bajo_global"] == "Diurna" and diag["extremo_alto_global"] == "Diurna")
    check("Sin segunda jornada, no se marca ninguna área ni consistente ni invertida",
          diag["areas_consistentes"] == [] and diag["areas_invertidas"] == [])
    check("'persiste' queda en False cuando no hay contraste posible", diag["persiste"] is False)


def test_limite_dataframe_vacio():
    vacio = DF_PERSISTENTE.iloc[0:0]
    tabla, diag = estratificar_por_area(vacio, "duracion", soporte_min=30)
    check("DataFrame vacío: tabla vacía y sin áreas comparables",
          len(tabla) == 0 and diag["areas_consistentes"] == [] and diag["areas_invertidas"] == [])


# ═══════════════════════════════════════════════════════════════════════
#  CASO EXCEPCIÓN
# ═══════════════════════════════════════════════════════════════════════
def test_excepcion_columna_inexistente():
    espera_error("Columna de área inexistente lanza KeyError",
                 lambda: estratificar_por_area(DF_PERSISTENTE, "duracion", col_area="no_existe"),
                 KeyError)
    espera_error("Columna de respuesta inexistente lanza KeyError",
                 lambda: estratificar_por_area(DF_PERSISTENTE, "no_existe"),
                 KeyError)


def test_excepcion_respuesta_no_numerica():
    espera_error("Respuesta de tipo texto lanza TypeError",
                 lambda: estratificar_por_area(DF_PERSISTENTE, "jornada"),
                 TypeError)


def test_excepcion_no_es_dataframe():
    espera_error("Pasar algo que no es DataFrame lanza TypeError",
                 lambda: estratificar_por_area([1, 2, 3], "duracion"),
                 TypeError)


# ═══════════════════════════════════════════════════════════════════════
#  EJECUCIÓN COMO SCRIPT
# ═══════════════════════════════════════════════════════════════════════
_ENCABEZADOS = {
    "test_normal": "\n── Caso normal ─────────────────────────────────────────────",
    "test_limite": "\n── Caso límite ─────────────────────────────────────────────",
    "test_excepcion": "\n── Caso excepción ──────────────────────────────────────────",
}


def _ejecutar_todo() -> int:
    global fallidas, _MODO_SCRIPT
    _MODO_SCRIPT = True
    grupo_actual = None
    for nombre, funcion in list(globals().items()):
        if not (nombre.startswith("test_") and callable(funcion)):
            continue
        grupo = "_".join(nombre.split("_")[:2])
        if grupo != grupo_actual:
            print(_ENCABEZADOS.get(grupo, f"\n── {grupo} ──"))
            grupo_actual = grupo
        try:
            funcion()
        except Exception as e:  # noqa: BLE001
            fallidas += 1
            print(f"  FALLA {nombre}  lanzó {type(e).__name__}: {e}")

    print("\n" + "─" * 60)
    print(f"{superadas}/{superadas + fallidas} pruebas superadas")
    return 0 if fallidas == 0 else 1


if __name__ == "__main__":
    sys.exit(_ejecutar_todo())
