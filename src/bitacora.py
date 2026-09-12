"""Bitácora de decisiones: registra cada decisión del pipeline con sus cifras.

Uso en un notebook:
    from src.bitacora import registrar, exportar
    registrar("F2 · limpieza", "anio_ing_carr_ori: 13.396 filas (12,7 %) con código 1900 tratadas como faltante")
    exportar("docs/bitacora.md")
"""
from datetime import datetime
from pathlib import Path

_ENTRADAS: list[str] = []


def registrar(etapa: str, decision: str) -> None:
    """Guarda una decisión y la imprime para que quede en la salida del notebook."""
    linea = f"[{etapa}] {decision}"
    _ENTRADAS.append(linea)
    print(linea)


def exportar(ruta: str = "docs/bitacora.md") -> None:
    """Escribe todas las decisiones registradas en un archivo Markdown."""
    salida = Path(ruta)
    salida.parent.mkdir(parents=True, exist_ok=True)
    texto = "# Bitácora de decisiones\n\n"
    texto += f"Generada el {datetime.now():%Y-%m-%d %H:%M}\n\n"
    texto += "\n".join(f"- {e}" for e in _ENTRADAS) + "\n"
    salida.write_text(texto, encoding="utf-8")
    print(f"Bitácora exportada a {salida} ({len(_ENTRADAS)} decisiones)")
