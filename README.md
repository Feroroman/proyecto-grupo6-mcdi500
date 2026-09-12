# Duración de la titulación en el pregrado universitario chileno (2025)

**MCDI500 · Programación para la Ciencia de Datos** · Grupo 6

## Integrantes
- Fernanda Ovalle Román
- Sebastián Cajales Cid
- César Lorca Bacián

## Problemática y pregunta
La duración real de las carreras universitarias en Chile suele superar la formal. Este proyecto analiza qué
factores observables acompañan una titulación más larga.

**Pregunta analizable:** ¿Qué factores observables (tipo de universidad, jornada, modalidad, área de conocimiento, región de la sede, sexo y rango etario) se asocian a un mayor número de semestres hasta la obtención del título entre los titulados de pregrado universitario de 2025?

**Alcance:** solo pregrado en universidades; análisis descriptivo y de asociación, sin modelos predictivos.

## Conjunto de datos
- Fuente: Titulados de Educación Superior 2025 – Datos Abiertos Mineduc — https://datosabiertos.mineduc.cl/
- Licencia: Datos públicos del Estado de Chile, de acceso libre y gratuito, publicados por el Centro de Estudios del Mineduc; el portal no declara una licencia Creative Commons específica y se reutilizan con atribución a la fuente conforme a la Ley 20.285 sobre acceso a la información pública
- Archivo original (dato crudo): `20260817_Titulados_Ed_Superior_2025_WEB.csv` (328.998 filas × 40 columnas, 175,6 MB; separador `;`, UTF-8).
  Descargar desde https://datosabiertos.mineduc.cl/ → «Titulados en educación superior» → año 2025, y dejarlo en `data/raw/` sin modificar.
  No se versiona (supera los 100 MB de GitHub).
- Subconjunto derivado: `data/processed/titulados_2025_pregrado_univ.csv` — filtro {'nivel_global': 'Pregrado', 'tipo_inst_1': 'Universidades'} → 105.063 filas, 55,8 MB.
  No se versiona: lo regenera `notebooks/F1/F1_Definicion.ipynb` a partir del original.
- Dataset procesado (Fase 2): `data/processed/titulados_2025_pregrado_univ_limpio.csv`, lo regenera `notebooks/F2/F2_Pipeline.ipynb`.
- Informe del validador: `docs/validacion_subconjunto.md` · Bitácora de decisiones: `docs/bitacora.md` · Registro de verificación: `docs/verificacion.md`.

## Estructura del repositorio
```
data/raw/          dato crudo descargado del portal; no se modifica ni se versiona
data/processed/    derivados regenerables: subconjunto (F1) y versiones limpias (F2)
notebooks/         F1/F1_Definicion.ipynb · F2/F2_Pipeline.ipynb
src/               módulos: proyecto, exploracion, limpieza, transformacion, escalado, validacion, bitacora
tests/             pruebas de las funciones (caso normal, límite, excepción)
docs/              validación del dataset, bitácora, verificación, figuras, evidencias
requirements.txt   versiones declaradas del entorno
.gitignore         qué NO se versiona: .venv/, todos los CSV, salidas de notebooks, .idea/
README.md          qué es el proyecto y cómo ejecutarlo desde cero
```
`notebooks/F2/F2_borrador_exploracion.ipynb` es un borrador de trabajo del equipo; el pipeline oficial es `F2_Pipeline.ipynb`.

## Cómo ejecutar desde cero
```bash
git clone https://github.com/Feroroman/proyecto-grupo6-mcdi500.git
cd proyecto-grupo6-mcdi500
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
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

## Ejecución verificada
- César Lorca Bacián · macOS · Python 3.14.7 · 13-09-2026: pruebas 8/8 y 11/11, notebooks F1 y F2 ejecutados sin errores.