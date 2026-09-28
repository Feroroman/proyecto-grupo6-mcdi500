"""Expone las suites de las Fases 1 y 2 a un ejecutor estándar de pruebas.

`test_proyecto.py`, `test_pipeline.py`, `test_pipeline_clases.py` y
`test_algoritmos.py` se escribieron como scripts: imprimen su resultado y
terminan con código 0 si todo pasa. Esa forma es legible, pero `unittest` y
`pytest` no la descubren, porque buscan funciones que empiecen por `test_`.

Este módulo las envuelve sin reescribirlas: cada suite se ejecuta como
subproceso y se comprueba su código de salida. Así todo el conjunto corre con
un solo comando, y el informe puede citar ese comando y su salida:

    python -m unittest discover -s tests -v

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 3
"""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

SUITES = {
    "proyecto": "tests/test_proyecto.py",
    "pipeline_funciones": "tests/test_pipeline.py",
    "pipeline_clases": "tests/test_pipeline_clases.py",
    "algoritmos": "tests/test_algoritmos.py",
}


class TestSuitesHeredadas(unittest.TestCase):
    """Cada suite escrita como script debe terminar sin fallos."""

    maxDiff = None

    def _correr(self, ruta: str) -> None:
        archivo = RAIZ / ruta
        if not archivo.exists():
            self.skipTest(f"{ruta} no está en el repositorio")
        r = subprocess.run([sys.executable, str(archivo)], cwd=RAIZ,
                           capture_output=True, text=True, timeout=600)
        ultima = (r.stdout.strip().splitlines() or ["(sin salida)"])[-1]
        self.assertEqual(r.returncode, 0,
                         f"\n{ruta} terminó con fallos.\nÚltima línea: {ultima}\n{r.stdout[-2000:]}")
        print(f"\n    {ruta}: {ultima}")

    def test_suite_proyecto(self):
        self._correr(SUITES["proyecto"])

    def test_suite_pipeline_funciones(self):
        self._correr(SUITES["pipeline_funciones"])

    def test_suite_pipeline_clases(self):
        self._correr(SUITES["pipeline_clases"])

    def test_suite_algoritmos(self):
        self._correr(SUITES["algoritmos"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
