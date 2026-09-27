"""Pruebas unitarias para MedidorComplejidad (Fase 3).

Autoría: Jorge Álvarez Ossandón / MCDI500 · Fase 3
"""
from __future__ import annotations

import sys
from pathlib import Path
import unittest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.complejidad import TestMedidorComplejidad

if __name__ == "__main__":
    unittest.main()
