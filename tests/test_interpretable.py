"""Pruebas del dataset interpretable y de las tablas agregadas (Fase 4).

Escritas con `unittest`, de modo que las detecta cualquier ejecutor estándar:

    python tests/test_interpretable.py
    python -m unittest discover -s tests -v

Cubren los tres escenarios que pide el descriptor —caso normal, caso límite y
caso de excepción— y, además, las dos comprobaciones que esta fase necesita de
forma específica: que el dataset que se grafica sea legible, y que toda tabla
que alimenta una figura traiga el tamaño de su grupo.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 4
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.interpretable import cargar_interpretable, columnas_derivadas, resumen_interpretable  # noqa: E402
from src.tablas import (  # noqa: E402
    serie_por_grupo, tabla_anidada, tabla_distribucion, tabla_imputacion,
    tabla_por_grupo, tabla_tamanos, todas,
)

CSV = RAIZ / "data/processed/titulados_2025_pregrado_univ_limpio.csv"
FILAS_ESPERADAS = 105_060


def hay_datos() -> bool:
    """Los CSV no se versionan: sin ellos las pruebas se omiten, no fallan."""
    return CSV.exists()


# ═══════════════════════════════════════════════════════════════════════
class TestInterpretableCasoNormal(unittest.TestCase):
    """El dataset que se grafica debe ser legible, no el optimizado para el análisis."""

    @classmethod
    def setUpClass(cls):
        if not hay_datos():
            raise unittest.SkipTest("Falta el CSV limpio: ejecuta antes los notebooks F1 y F2")
        cls.d = cargar_interpretable()

    def test_no_quedan_columnas_escaladas_ni_codificadas(self):
        """Un valor escalado de -0,43 no admite interpretación sustantiva."""
        sobran = [c for c in self.d.columns if c.endswith(("_esc", "_ord"))]
        self.assertEqual(sobran, [])

    def test_no_quedan_columnas_one_hot(self):
        """Las 36 indicadoras sirven al modelo, no a la lectura."""
        sobran = [c for c in self.d.columns
                  if c.startswith(("jornada_", "region_sede_", "area_conocimiento_",
                                   "modalidad_", "tipo_inst_2_"))]
        self.assertEqual(sobran, [])

    def test_conserva_las_banderas_de_imputacion(self):
        """Son el insumo de la figura que declara el límite del análisis."""
        self.assertIn("anio_ing_carr_ori_imputada", self.d.columns)

    def test_conserva_las_categoricas_originales(self):
        for col in ("jornada", "area_conocimiento", "modalidad", "region_sede", "tipo_inst_2"):
            with self.subTest(columna=col):
                self.assertIn(col, self.d.columns)
                self.assertFalse(pd.api.types.is_numeric_dtype(self.d[col]))

    def test_conserva_las_unidades_originales(self):
        """La duración debe seguir en semestres, no reescalada."""
        self.assertGreater(self.d["dur_total_carr"].max(), 20)

    def test_el_sexo_viene_etiquetado(self):
        self.assertEqual(set(self.d["sexo"].dropna().unique()), {"Hombre", "Mujer"})

    def test_el_sexo_coincide_con_la_columna_derivada_en_la_fase_2(self):
        """Verificación cruzada contra `mujer`: gen_alu == 2 produce mujer == 1.

        Es un error silencioso — la figura sale igual de bien con las etiquetas
        invertidas — así que conviene comprobarlo y no confiar en el supuesto.
        """
        self.assertEqual(list(self.d[self.d["sexo"] == "Mujer"]["mujer"].unique()), [1])
        self.assertEqual(list(self.d[self.d["sexo"] == "Hombre"]["mujer"].unique()), [0])

    def test_las_ordinales_estan_declaradas_como_ordenadas(self):
        for col in ("rango_edad", "nivel_carrera_1"):
            with self.subTest(columna=col):
                self.assertTrue(self.d[col].dtype.ordered)

    def test_el_orden_de_rango_edad_no_es_alfabetico(self):
        """Alfabéticamente «40 y más años» iría primero: sería una escala falsa."""
        cats = list(self.d["rango_edad"].cat.categories)
        self.assertEqual(cats[0], "15 a 19 Años")
        self.assertEqual(cats[-1], "40 y más años")

    def test_no_modifica_el_numero_de_filas(self):
        self.assertEqual(len(self.d), FILAS_ESPERADAS)

    def test_el_resumen_describe_todas_las_columnas(self):
        r = resumen_interpretable(self.d)
        self.assertEqual(len(r), self.d.shape[1])
        self.assertIn("ordenada", set(r["tipo"]))


# ═══════════════════════════════════════════════════════════════════════
class TestTablasCasoNormal(unittest.TestCase):
    """Toda tabla que alimenta una figura debe traer el tamaño de su grupo."""

    @classmethod
    def setUpClass(cls):
        if not hay_datos():
            raise unittest.SkipTest("Falta el CSV limpio")
        cls.d = cargar_interpretable()
        cls.t = todas(cls.d)

    def test_se_generan_las_seis_tablas(self):
        self.assertEqual(len(self.t), 6)

    def test_todas_las_tablas_agregadas_traen_el_n(self):
        """Una barra sobre 543 casos ocupa lo mismo que una sobre 82.194."""
        for nombre in ("f2_tamanos", "f3_por_jornada", "f5_anidada", "f6_imputacion"):
            with self.subTest(tabla=nombre):
                self.assertIn("n", self.t[nombre].columns)

    def test_la_distribucion_informa_los_cuartiles(self):
        f1 = self.t["f1_distribucion"]
        self.assertEqual(f1["n"], FILAS_ESPERADAS)
        self.assertLessEqual(f1["p25"], f1["mediana"])
        self.assertLessEqual(f1["mediana"], f1["p75"])

    def test_los_tamanos_suman_el_total(self):
        self.assertEqual(self.t["f2_tamanos"]["n"].sum(), FILAS_ESPERADAS)
        self.assertAlmostEqual(self.t["f2_tamanos"]["porcentaje"].sum(), 100.0, places=0)

    def test_la_tabla_por_grupo_viene_ordenada_por_duracion(self):
        self.assertTrue(self.t["f3_por_jornada"]["mediana"].is_monotonic_decreasing)

    def test_la_serie_sin_agregar_conserva_todas_las_observaciones(self):
        self.assertEqual(len(self.t["f4_serie"]), FILAS_ESPERADAS)

    def test_la_tabla_anidada_compara_contra_su_area(self):
        a = self.t["f5_anidada"]
        self.assertIn("dif_vs_area", a.columns)
        self.assertIn("suficiente", a.columns)

    def test_la_tabla_anidada_marca_los_grupos_pequenos(self):
        """De 41 grupos, varios no alcanzan los 100 casos: hay que declararlos."""
        self.assertFalse(self.t["f5_anidada"]["suficiente"].all())

    def test_los_porcentajes_de_imputacion_suman_cien(self):
        f6 = self.t["f6_imputacion"]
        suma = (f6["observados_pct"] + f6["imputados_pct"]).round(1)
        self.assertTrue((suma == 100.0).all())

    def test_la_imputacion_se_concentra_fuera_de_la_jornada_diurna(self):
        """El hallazgo que condiciona la interpretación de toda la fase."""
        f6 = self.t["f6_imputacion"].set_index("jornada")
        self.assertLess(f6.loc["Diurna", "imputados_pct"], 5)
        self.assertGreater(f6.loc["A Distancia", "imputados_pct"], 50)


# ═══════════════════════════════════════════════════════════════════════
class TestCasoLimite(unittest.TestCase):
    """Comportamiento con subconjuntos mínimos y columnas constantes."""

    @classmethod
    def setUpClass(cls):
        if not hay_datos():
            raise unittest.SkipTest("Falta el CSV limpio")
        cls.d = cargar_interpretable()

    def test_una_sola_jornada(self):
        sub = self.d[self.d["jornada"] == "Diurna"]
        t = tabla_por_grupo(sub, "jornada")
        self.assertEqual(len(t), 1)
        self.assertEqual(t.iloc[0]["n"], len(sub))

    def test_un_solo_registro(self):
        t = tabla_por_grupo(self.d.head(1), "jornada")
        self.assertEqual(t.iloc[0]["n"], 1)

    def test_soporte_minimo_imposible_marca_todo_insuficiente(self):
        a = tabla_anidada(self.d, soporte_min=10_000_000)
        self.assertFalse(a["suficiente"].any())

    def test_soporte_minimo_uno_marca_todo_suficiente(self):
        a = tabla_anidada(self.d, soporte_min=1)
        self.assertTrue(a["suficiente"].all())

    def test_agrupar_por_una_ordinal_respeta_su_orden(self):
        t = tabla_tamanos(self.d, "rango_edad")
        self.assertEqual(set(t["rango_edad"]), set(self.d["rango_edad"].cat.categories))


# ═══════════════════════════════════════════════════════════════════════
class TestCasoExcepcion(unittest.TestCase):
    """Una entrada inválida debe producir un error explícito, no un resultado raro."""

    @classmethod
    def setUpClass(cls):
        if not hay_datos():
            raise unittest.SkipTest("Falta el CSV limpio")
        cls.d = cargar_interpretable()

    def test_archivo_inexistente_lanza_error_con_instruccion(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            cargar_interpretable("data/processed/no_existe.csv")
        self.assertIn("F1", str(ctx.exception))

    def test_columna_inexistente_en_tabla_por_grupo(self):
        with self.assertRaises(KeyError):
            tabla_por_grupo(self.d, "no_existe")

    def test_columna_inexistente_en_tabla_anidada(self):
        with self.assertRaises(KeyError):
            tabla_anidada(self.d, externo="no_existe")

    def test_columna_inexistente_en_tabla_de_imputacion(self):
        with self.assertRaises(KeyError):
            tabla_imputacion(self.d, "no_existe")

    def test_dataframe_sin_la_variable_de_respuesta(self):
        with self.assertRaises(KeyError):
            tabla_distribucion(self.d.drop(columns=["dur_total_carr"]))

    def test_dataframe_sin_la_bandera_de_imputacion(self):
        with self.assertRaises(KeyError):
            tabla_imputacion(self.d.drop(columns=["anio_ing_carr_ori_imputada"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
