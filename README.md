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
  No se versiona: lo regenera `notebooks/F1_definicion.ipynb` a partir del original.
- Informe del validador: `docs/validacion_subconjunto.md`.

## Estructura del repositorio
```
data/raw/          dato crudo descargado del portal; no se modifica ni se versiona
data/processed/    derivados regenerables: subconjunto (F1) y versiones limpias (F2)
notebooks/         F1_definicion.ipynb · F2_pipeline.ipynb
src/               funciones reutilizables (validar_dataset.py, bitacora.py)
docs/              informe de validación, bitácora de decisiones, informe técnico
requirements.txt   versiones declaradas del entorno
.gitignore         qué NO se versiona: .venv/, todos los CSV, salidas de notebooks
README.md          qué es el proyecto y cómo ejecutarlo desde cero
```

## Cómo ejecutar desde cero
```bash
git clone https://github.com/Feroroman/proyecto-grupo6-mcdi500.git
cd proyecto-grupo6-mcdi500
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name mcdi500 --display-name "Python (mcdi500)"
jupyter lab
```
Abrir `notebooks/F1_definicion.ipynb` con el kernel **Python (mcdi500)** y ejecutar *Restart Kernel and Run All Cells*.

## Criterios de reproducibilidad
- Entorno virtual propio y versiones declaradas en `requirements.txt`.
- Rutas relativas a la raíz del repositorio.
- `data/raw/` nunca se modifica; cada transformación escribe en `data/processed/`.
- Cada decisión de preprocesamiento queda registrada con sus cifras en `docs/bitacora.md`.

## Convención de commits
`docs:` documentación · `data:` datos · `feat:` nueva funcionalidad · `fix:` corrección · `test:` pruebas.
Ramas por integrante y fase, integradas por pull request.
