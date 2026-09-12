"""Fase 1 · Configuración del proyecto como objeto.

La clase ProyectoF1 encapsula la configuración (pregunta, fuente, filtro, rutas) y las
operaciones técnicas iniciales del flujo reproducible: verificar el entorno, verificar la
estructura del repositorio, generar el subconjunto a partir del dato crudo y componer el README.
Así el notebook F1 orquesta y documenta; la lógica vive aquí y se prueba en tests/test_proyecto.py.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

ESTRUCTURA_BASE: dict[str, str] = {
    "data/raw/":        "dato crudo descargado del portal; no se modifica ni se versiona",
    "data/processed/":  "derivados regenerables: subconjunto (F1) y versiones limpias (F2)",
    "notebooks/":       "F1/F1_Definicion.ipynb · F2/F2_Pipeline.ipynb",
    "src/":             "módulos: proyecto, exploracion, limpieza, transformacion, escalado, validacion, bitacora",
    "tests/":           "pruebas de las funciones (caso normal, límite, excepción)",
    "docs/":            "validación del dataset, bitácora, verificación, figuras, evidencias",
    "requirements.txt": "versiones declaradas del entorno",
    ".gitignore":       "qué NO se versiona: .venv/, todos los CSV, salidas de notebooks, .idea/",
    "README.md":        "qué es el proyecto y cómo ejecutarlo desde cero",
}


@dataclass
class ProyectoF1:
    """Configuración y operaciones iniciales del proyecto (Fase 1)."""

    grupo: str
    integrantes: list[str]
    repositorio: str
    pregunta: str
    fuente_nombre: str
    fuente_url: str
    fuente_licencia: str
    archivo_original: Path
    archivo_subconjunto: Path
    filtro: dict[str, object]
    separador: str = ";"
    encoding: str = "utf-8"
    variable_respuesta: str = "dur_total_carr"
    factores: list[str] = field(default_factory=list)
    estructura: dict[str, str] = field(default_factory=lambda: dict(ESTRUCTURA_BASE))

    # ---- verificación del entorno y la estructura
    def verificar_entorno(self, exigir_venv: bool = True) -> dict[str, str]:
        """Devuelve versión de Python, intérprete y pandas; falla si el kernel no es el del proyecto."""
        info = {"python": sys.version.split()[0], "interprete": sys.executable, "pandas": pd.__version__}
        if exigir_venv and ".venv" not in sys.executable:
            raise EnvironmentError("El kernel no es el del entorno virtual del proyecto: selecciona 'Python (mcdi500)'")
        return info

    def verificar_estructura(self, raiz: Path = Path(".")) -> dict[str, bool]:
        """Comprueba qué rutas de la estructura existen bajo `raiz`."""
        return {ruta: (raiz / ruta).exists() for ruta in self.estructura}

    # ---- datos
    def aplicar_filtro(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica el filtro declarado (todas las condiciones a la vez) y devuelve una copia."""
        faltan = [c for c in self.filtro if c not in df.columns]
        if faltan:
            raise KeyError(f"Columnas del filtro ausentes en los datos: {faltan}")
        mascara = pd.Series(True, index=df.index)
        for col, val in self.filtro.items():
            mascara &= df[col] == val
        return df[mascara].copy()

    def generar_subconjunto(self, limite_mb: float = 100.0) -> tuple[pd.DataFrame, str]:
        """Lee el dato crudo, aplica el filtro y escribe el subconjunto en data/processed/.

        Si el original no está pero el subconjunto sí, lo lee. Si no hay ninguno, lanza FileNotFoundError.
        Devuelve (df, mensaje) y verifica que el archivo quede bajo `limite_mb`.
        """
        if self.archivo_original.exists():
            df_full = pd.read_csv(self.archivo_original, sep=self.separador, encoding=self.encoding, low_memory=False)
            df = self.aplicar_filtro(df_full)
            self.archivo_subconjunto.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.archivo_subconjunto, sep=self.separador, index=False, encoding=self.encoding)
            msg = f"Base completa: {len(df_full):,} filas → subconjunto: {len(df):,} filas guardado en {self.archivo_subconjunto}"
        elif self.archivo_subconjunto.exists():
            df = pd.read_csv(self.archivo_subconjunto, sep=self.separador, encoding=self.encoding, low_memory=False)
            msg = f"Subconjunto ya generado: {len(df):,} filas × {df.shape[1]} columnas"
        else:
            raise FileNotFoundError(f"Descarga el archivo original del portal Mineduc y déjalo en {self.archivo_original}")
        mb = self.archivo_subconjunto.stat().st_size / 1_048_576
        if mb >= limite_mb:
            raise ValueError(f"El subconjunto pesa {mb:.1f} MB y supera el límite de {limite_mb} MB")
        return df, msg

    # ---- documentación
    def generar_readme(self, filas_original: str = "328.998", filas_subconjunto: str = "105.063", mb: str = "55,8") -> str:
        """Compone el README desde la configuración, para que no se desactualice respecto del código."""
        integrantes_md = "\n".join("- " + n for n in self.integrantes)
        estructura_md = "\n".join(f"{k:<18} {v}" for k, v in self.estructura.items())
        return f"""# Duración de la titulación en el pregrado universitario chileno (2025)

**MCDI500 · Programación para la Ciencia de Datos** · {self.grupo}

## Integrantes
{integrantes_md}

## Problemática y pregunta
La duración real de las carreras universitarias en Chile suele superar la formal. Este proyecto analiza qué
factores observables acompañan una titulación más larga.

**Pregunta analizable:** {self.pregunta}

**Alcance:** solo pregrado en universidades; análisis descriptivo y de asociación, sin modelos predictivos.

## Conjunto de datos
- Fuente: {self.fuente_nombre} — {self.fuente_url}
- Licencia: {self.fuente_licencia}
- Archivo original (dato crudo): `{self.archivo_original.name}` ({filas_original} filas × 40 columnas, 175,6 MB; separador `;`, UTF-8).
  Descargar desde {self.fuente_url} → «Titulados en educación superior» → año 2025, y dejarlo en `data/raw/` sin modificar.
  No se versiona (supera los 100 MB de GitHub).
- Subconjunto derivado: `{self.archivo_subconjunto}` — filtro {self.filtro} → {filas_subconjunto} filas, {mb} MB.
  No se versiona: lo regenera `notebooks/F1/F1_Definicion.ipynb` a partir del original.
- Dataset procesado (Fase 2): `data/processed/titulados_2025_pregrado_univ_limpio.csv`, lo regenera `notebooks/F2/F2_Pipeline.ipynb`.
- Informe del validador: `docs/validacion_subconjunto.md` · Bitácora de decisiones: `docs/bitacora.md` · Registro de verificación: `docs/verificacion.md`.

## Estructura del repositorio
```
{estructura_md}
```
`notebooks/F2/F2_borrador_exploracion.ipynb` es un borrador de trabajo del equipo; el pipeline oficial es `F2_Pipeline.ipynb`.

## Cómo ejecutar desde cero
```bash
git clone {self.repositorio}.git
cd proyecto-grupo6-mcdi500
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name mcdi500 --display-name "Python (mcdi500)"
python tests/test_proyecto.py && python tests/test_pipeline.py
jupyter lab
```
Abrir `notebooks/F1/F1_Definicion.ipynb` con el kernel **Python (mcdi500)** y ejecutar *Restart Kernel and Run All Cells*;
luego `notebooks/F2/F2_Pipeline.ipynb` de la misma forma.

## Criterios de reproducibilidad
- Entorno virtual propio y versiones declaradas en `requirements.txt`.
- Rutas relativas a la raíz del repositorio.
- `data/raw/` nunca se modifica; cada transformación escribe en `data/processed/`.
- Cada decisión de preprocesamiento queda registrada con sus cifras en `docs/bitacora.md`.
- Cada verificación (pruebas, ejecución completa de notebooks) queda registrada en `docs/verificacion.md`.

## Convención de commits
`docs:` documentación · `data:` datos · `feat:` nueva funcionalidad · `fix:` corrección · `test:` pruebas.
Ramas por integrante y fase, integradas por pull request.
"""
