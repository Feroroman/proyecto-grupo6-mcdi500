"""Pruebas del patrón Strategy aplicado al escalamiento (src/escaladores.py).

Escritas con `unittest`, de modo que las detecta cualquier ejecutor estándar:

    python tests/test_escaladores.py
    python -m unittest discover -s tests -v
    pytest tests/

Cubre los tres escenarios que pide el descriptor —caso normal, caso límite y
caso de excepción— y, además, las dos propiedades que justifican el patrón:
que el contexto no dependa de la estrategia concreta, y que agregar una
estrategia nueva no obligue a tocar el contexto.
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.escaladores import (  # noqa: E402
    ESTRATEGIAS, EscaladoRobusto, Escalador, EstandarizacionZ, EstrategiaEscalado,
    NormalizacionMinMax, comparar_estrategias, crear_estrategia,
)


def serie(valores=None) -> pd.Series:
    """Serie con un extremo marcado, como las duraciones del proyecto."""
    return pd.Series(valores if valores is not None else
                     [8, 9, 10, 10, 10, 11, 11, 12, 12, 24], name="dur_total_carr", dtype=float)


# ═══════════════════════════════════════════════════════════════════════
class TestCasoNormal(unittest.TestCase):
    """Cada estrategia cumple exactamente la propiedad que promete."""

    def test_estandarizacion_deja_media_cero_y_desviacion_uno(self):
        y = Escalador(EstandarizacionZ()).ajustar_aplicar(serie())
        self.assertAlmostEqual(y.mean(), 0.0, places=9)
        self.assertAlmostEqual(y.std(ddof=0), 1.0, places=9)

    def test_minmax_deja_el_rango_entre_cero_y_uno(self):
        y = Escalador(NormalizacionMinMax()).ajustar_aplicar(serie())
        self.assertAlmostEqual(y.min(), 0.0, places=9)
        self.assertAlmostEqual(y.max(), 1.0, places=9)

    def test_robusto_deja_mediana_cero_y_ric_uno(self):
        y = Escalador(EscaladoRobusto()).ajustar_aplicar(serie())
        self.assertAlmostEqual(y.median(), 0.0, places=9)
        self.assertAlmostEqual(y.quantile(0.75) - y.quantile(0.25), 1.0, places=9)

    def test_cada_estrategia_se_verifica_a_si_misma(self):
        for nombre in ESTRATEGIAS:
            with self.subTest(estrategia=nombre):
                esc = Escalador(crear_estrategia(nombre))
                self.assertTrue(esc.verificar(esc.ajustar_aplicar(serie())))

    def test_no_modifica_la_serie_original(self):
        s = serie(); copia = s.copy()
        Escalador(EscaladoRobusto()).ajustar_aplicar(s)
        pd.testing.assert_series_equal(s, copia)

    def test_ajustar_y_aplicar_estan_separados(self):
        """Los parámetros aprendidos sobre una serie se reaplican a otra."""
        est = EscaladoRobusto().ajustar(serie())
        centro, escala = est.centro_, est.escala_
        est.aplicar(serie([100, 200, 300]))
        self.assertEqual((est.centro_, est.escala_), (centro, escala))

    def test_el_robusto_resiste_el_extremo_mejor_que_el_minmax(self):
        """La justificación de la Fase 2, comprobada en vez de afirmada."""
        tabla = comparar_estrategias(serie())
        self.assertLess(tabla.loc["minmax", "ric"], tabla.loc["robusto", "ric"])

    def test_comparar_devuelve_una_fila_por_estrategia_mas_el_original(self):
        tabla = comparar_estrategias(serie())
        self.assertEqual(len(tabla), len(ESTRATEGIAS) + 1)
        self.assertTrue(tabla["cumple"].all())


# ═══════════════════════════════════════════════════════════════════════
class TestPatron(unittest.TestCase):
    """Las propiedades que hacen que esto sea Strategy y no tres funciones."""

    def test_el_contexto_no_contiene_formulas_de_escalado(self):
        """`Escalador` delega: no menciona media, mediana ni cuantiles."""
        import inspect
        from src import escaladores
        fuente = inspect.getsource(escaladores.Escalador)
        for termino in ("mean(", "median(", "quantile(", "std("):
            self.assertNotIn(termino, fuente,
                             f"el contexto no debería calcular {termino} por su cuenta")

    def test_la_estrategia_se_cambia_en_tiempo_de_ejecucion(self):
        esc = Escalador(EscaladoRobusto())
        a = esc.ajustar_aplicar(serie())
        esc.cambiar_estrategia(EstandarizacionZ())
        b = esc.ajustar_aplicar(serie())
        self.assertFalse(a.equals(b))
        self.assertEqual(len(esc.historial_), 2)

    def test_una_estrategia_nueva_funciona_sin_tocar_el_contexto(self):
        """Principio abierto/cerrado: se extiende sin modificar."""

        class EscaladoPorMaximo(EstrategiaEscalado):
            nombre = "por_maximo"
            propiedad = "máximo 1"

            def _parametros(self, s):
                return 0.0, s.max()

            def verificar(self, escalada):
                return abs(escalada.max() - 1) < 1e-9

        esc = Escalador(EscaladoPorMaximo())          # el contexto no cambió
        y = esc.ajustar_aplicar(serie())
        self.assertTrue(esc.verificar(y))
        self.assertAlmostEqual(y.max(), 1.0, places=9)

    def test_la_fabrica_construye_por_nombre(self):
        for nombre, clase in ESTRATEGIAS.items():
            with self.subTest(estrategia=nombre):
                self.assertIsInstance(crear_estrategia(nombre), clase)


# ═══════════════════════════════════════════════════════════════════════
class TestCasoLimite(unittest.TestCase):

    def test_serie_de_un_solo_valor_repetido_no_admite_escalado(self):
        with self.assertRaises(ValueError):
            Escalador(EscaladoRobusto()).ajustar_aplicar(pd.Series([5.0] * 10, name="x"))

    def test_serie_de_dos_elementos(self):
        y = Escalador(NormalizacionMinMax()).ajustar_aplicar(pd.Series([1.0, 3.0], name="x"))
        self.assertAlmostEqual(y.min(), 0.0)
        self.assertAlmostEqual(y.max(), 1.0)

    def test_valores_negativos(self):
        y = Escalador(EstandarizacionZ()).ajustar_aplicar(
            pd.Series([-50.0, -10, 0, 10, 50], name="x"))
        self.assertAlmostEqual(y.mean(), 0.0, places=9)

    def test_ric_cero_aunque_haya_dispersion(self):
        """El 80 % idéntico deja RIC 0: el robusto no aplica, el estándar sí."""
        s = pd.Series([5.0] * 8 + [1.0, 99.0], name="x")
        with self.assertRaises(ValueError):
            Escalador(EscaladoRobusto()).ajustar_aplicar(s)
        self.assertIsNotNone(Escalador(EstandarizacionZ()).ajustar_aplicar(s))

    def test_comparar_informa_la_estrategia_que_no_aplica(self):
        tabla = comparar_estrategias(pd.Series([5.0] * 8 + [1.0, 99.0], name="x"))
        self.assertFalse(bool(tabla.loc["robusto", "cumple"]))


# ═══════════════════════════════════════════════════════════════════════
class TestCasoExcepcion(unittest.TestCase):

    def test_aplicar_sin_ajustar_lanza_runtime_error(self):
        with self.assertRaises(RuntimeError):
            EscaladoRobusto().aplicar(serie())

    def test_serie_de_texto_lanza_type_error(self):
        with self.assertRaises(TypeError):
            Escalador(EscaladoRobusto()).ajustar_aplicar(pd.Series(["a", "b"], name="x"))

    def test_serie_con_nulos_lanza_value_error(self):
        with self.assertRaises(ValueError):
            Escalador(EscaladoRobusto()).ajustar_aplicar(pd.Series([1.0, None, 3.0], name="x"))

    def test_algo_que_no_es_series_lanza_type_error(self):
        with self.assertRaises(TypeError):
            Escalador(EscaladoRobusto()).ajustar_aplicar([1, 2, 3])

    def test_el_contexto_rechaza_lo_que_no_es_una_estrategia(self):
        with self.assertRaises(TypeError):
            Escalador("robusto")

    def test_la_clase_base_no_se_usa_directamente(self):
        with self.assertRaises(NotImplementedError):
            EstrategiaEscalado().ajustar(serie())

    def test_estrategia_desconocida_lanza_key_error(self):
        with self.assertRaises(KeyError):
            crear_estrategia("no_existe")


if __name__ == "__main__":
    unittest.main(verbosity=2)
