"""Pruebas de la clase ProyectoF1 (Fase 1): caso normal, caso límite y excepción.

Ejecutar desde la raíz: python tests/test_proyecto.py
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.proyecto import ProyectoF1  # noqa: E402
from src.validar_dataset import detectar_separador, validar  # noqa: E402


def _proyecto(tmp: Path) -> ProyectoF1:
    return ProyectoF1(grupo="Grupo 6", integrantes=["A", "B", "C"], repositorio="https://github.com/x/y",
                      pregunta="¿Qué factores se asocian a la duración?", fuente_nombre="Mineduc", fuente_url="https://x",
                      fuente_licencia="abierta", archivo_original=tmp / "raw.csv", archivo_subconjunto=tmp / "sub.csv",
                      filtro={"nivel_global": "Pregrado", "tipo_inst_1": "Universidades"})


def _datos() -> pd.DataFrame:
    return pd.DataFrame({"nivel_global": ["Pregrado", "Pregrado", "Posgrado"],
                         "tipo_inst_1": ["Universidades", "Institutos Profesionales", "Universidades"],
                         "dur_total_carr": [10, 8, 4]})


# ---- caso normal
def test_filtro_conserva_solo_pregrado_universitario():
    with tempfile.TemporaryDirectory() as t:
        out = _proyecto(Path(t)).aplicar_filtro(_datos())
        assert len(out) == 1 and out["dur_total_carr"].iloc[0] == 10


def test_generar_subconjunto_escribe_archivo():
    with tempfile.TemporaryDirectory() as t:
        p = _proyecto(Path(t)); _datos().to_csv(p.archivo_original, sep=";", index=False)
        df, msg = p.generar_subconjunto()
        assert p.archivo_subconjunto.exists() and len(df) == 1 and "subconjunto" in msg


def test_readme_contiene_pregunta_e_integrantes():
    with tempfile.TemporaryDirectory() as t:
        r = _proyecto(Path(t)).generar_readme()
        assert "¿Qué factores" in r and "- A" in r and "Grupo 6" in r and "TU_USUARIO" not in r


def test_verificar_estructura_detecta_faltantes():
    with tempfile.TemporaryDirectory() as t:
        (Path(t) / "README.md").write_text("x")
        est = _proyecto(Path(t)).verificar_estructura(Path(t))
        assert est["README.md"] is True and est["src/"] is False


def test_validador_detecta_separador_y_alertas():
    with tempfile.TemporaryDirectory() as t:
        ruta = Path(t) / "d.csv"
        pd.DataFrame({"a": [1, 1, 1], "b": [1, 2, 2]}).to_csv(ruta, sep=";", index=False)
        assert detectar_separador(ruta, "utf-8") == ";"
        lineas, alertas = validar(ruta, ";", "utf-8")
        assert any("constante" in a for a in alertas) and any("duplicadas" in a for a in alertas)


# ---- caso límite
def test_filtro_sin_coincidencias_devuelve_vacio():
    with tempfile.TemporaryDirectory() as t:
        p = _proyecto(Path(t)); p.filtro = {"nivel_global": "Doctorado"}
        assert len(p.aplicar_filtro(_datos())) == 0


def test_subconjunto_existente_se_reutiliza_sin_original():
    with tempfile.TemporaryDirectory() as t:
        p = _proyecto(Path(t)); _datos().to_csv(p.archivo_subconjunto, sep=";", index=False)
        df, msg = p.generar_subconjunto()
        assert len(df) == 3 and "ya generado" in msg


# ---- excepciones
def _raises(fn, exc):
    try:
        fn()
    except exc:
        return True
    return False


def test_excepciones():
    with tempfile.TemporaryDirectory() as t:
        p = _proyecto(Path(t))
        assert _raises(lambda: p.generar_subconjunto(), FileNotFoundError)
        assert _raises(lambda: p.aplicar_filtro(pd.DataFrame({"x": [1]})), KeyError)
        p2 = _proyecto(Path(t)); _datos().to_csv(p2.archivo_original, sep=";", index=False)
        assert _raises(lambda: p2.generar_subconjunto(limite_mb=0.0), ValueError)
        assert _raises(lambda: p.verificar_entorno(exigir_venv=True) if ".venv" not in sys.executable else (_ for _ in ()).throw(EnvironmentError()), EnvironmentError)


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
