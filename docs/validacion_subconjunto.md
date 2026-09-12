# Informe de validación: `titulados_2025_pregrado_univ.csv`

## Resumen general

- Ruta: `data/processed/titulados_2025_pregrado_univ.csv`
- Tamaño en disco: 55.8 MB
- Separador: `';'` · Encoding: `utf-8`
- Filas: 105,063 · Columnas: 40
- Memoria en pandas: 208.2 MB
- Filas duplicadas: 3

## Columnas

| Columna | Tipo | Nulos | % nulos | Únicos | Ejemplo |
|---|---|---:|---:|---:|---|
| `cat_periodo` | int64 | 0 | 0.0% | 1 | 2025 |
| `mrun` | float64 | 7 | 0.0% | 104,595 | 523.0 |
| `gen_alu` | int64 | 0 | 0.0% | 2 | 1 |
| `fec_nac_alu` | int64 | 0 | 0.0% | 585 | 199012 |
| `rango_edad` | object | 0 | 0.0% | 6 | 30 a 34 Años |
| `anio_ing_carr_ori` | int64 | 0 | 0.0% | 45 | 2015 |
| `sem_ing_carr_ori` | int64 | 0 | 0.0% | 3 | 1 |
| `anio_ing_carr_act` | int64 | 0 | 0.0% | 42 | 2022 |
| `sem_ing_carr_act` | int64 | 0 | 0.0% | 2 | 1 |
| `nombre_titulo` | object | 2,997 | 2.9% | 1,741 | INGENIERO CIVIL INDUSTRIAL |
| `nombre_grado` | object | 8,437 | 8.0% | 936 | LICENCIADO EN CIENCIAS DE LA INGENIERIA  |
| `fecha_obtencion_titulo` | int64 | 0 | 0.0% | 355 | 20251105 |
| `tipo_inst_1` | object | 0 | 0.0% | 1 | Universidades |
| `tipo_inst_2` | object | 0 | 0.0% | 2 | Universidades CRUCH |
| `tipo_inst_3` | object | 0 | 0.0% | 3 | Universidades Privadas CRUCH |
| `cod_inst` | int64 | 0 | 0.0% | 55 | 88 |
| `nomb_inst` | object | 0 | 0.0% | 55 | UNIVERSIDAD TECNICA FEDERICO SANTA MARIA |
| `cod_sede` | int64 | 0 | 0.0% | 26 | 1 |
| `nomb_sede` | object | 0 | 0.0% | 109 | CAMPUS CASA CENTRAL VALPARAISO |
| `cod_carrera` | float64 | 300 | 0.3% | 602 | 15.0 |
| `nomb_carrera` | object | 0 | 0.0% | 1,096 | INGENIERIA CIVIL INDUSTRIAL |
| `nivel_global` | object | 0 | 0.0% | 1 | Pregrado |
| `nivel_carrera_1` | object | 0 | 0.0% | 4 | Profesional Con Licenciatura |
| `nivel_carrera_2` | object | 0 | 0.0% | 2 | Carreras Profesionales |
| `dur_estudio_carr` | int64 | 0 | 0.0% | 15 | 7 |
| `dur_proceso_tit` | int64 | 0 | 0.0% | 7 | 0 |
| `dur_total_carr` | int64 | 0 | 0.0% | 16 | 7 |
| `region_sede` | object | 0 | 0.0% | 16 | Valparaíso |
| `provincia_sede` | object | 0 | 0.0% | 34 | VALPARAISO |
| `comuna_sede` | object | 0 | 0.0% | 56 | VALPARAISO |
| `jornada` | object | 0 | 0.0% | 5 | Vespertina |
| `modalidad` | object | 0 | 0.0% | 3 | Presencial |
| `version` | float64 | 290 | 0.3% | 8 | 1.0 |
| `tipo_plan_carr` | object | 0 | 0.0% | 3 | Plan Regular de Continuidad |
| `area_conocimiento` | object | 0 | 0.0% | 10 | Tecnología |
| `cine_f_97_area` | object | 0 | 0.0% | 8 | Ingeniería, Industria y Construcción |
| `cine_f_97_subarea` | object | 0 | 0.0% | 22 | Ingeniería y Profesiones Afines |
| `area_generica` | object | 0 | 0.0% | 213 | Ingeniería Civil Industrial |
| `cine_f_13_area` | object | 0 | 0.0% | 10 | Ingeniería, Industria y Construcción |
| `cine_f_13_subarea` | object | 0 | 0.0% | 28 | Ingeniería y Profesiones Afines |

## Estadísticas numéricas

| Columna | Media | Desv. | Mín | Máx |
|---|---:|---:|---:|---:|
| `cat_periodo` | 2025.0 | 0.0 | 2025.0 | 2025.0 |
| `mrun` | 12607588.63 | 7303202.58 | 523.0 | 28721953.0 |
| `gen_alu` | 1.56 | 0.5 | 1.0 | 2.0 |
| `fec_nac_alu` | 199729.32 | 642.87 | 194409.0 | 200608.0 |
| `anio_ing_carr_ori` | 2004.22 | 39.91 | 1900.0 | 2025.0 |
| `sem_ing_carr_ori` | 0.89 | 0.37 | 0.0 | 2.0 |
| `anio_ing_carr_act` | 2020.08 | 2.54 | 1972.0 | 2025.0 |
| `sem_ing_carr_act` | 1.05 | 0.22 | 1.0 | 2.0 |
| `fecha_obtencion_titulo` | 20252744.42 | 3803.78 | 20250301.0 | 20260228.0 |
| `cod_inst` | 56.1 | 66.51 | 1.0 | 896.0 |
| `cod_sede` | 2.64 | 2.86 | 1.0 | 34.0 |
| `cod_carrera` | 124.87 | 172.16 | 1.0 | 1140.0 |
| `dur_estudio_carr` | 9.03 | 2.44 | 1.0 | 24.0 |
| `dur_proceso_tit` | 0.39 | 0.62 | 0.0 | 9.0 |
| `dur_total_carr` | 9.07 | 2.44 | 1.0 | 24.0 |
| `version` | 1.29 | 0.62 | 1.0 | 8.0 |

## Alertas

- ⚠️ Hay 3 filas duplicadas.
- ⚠️ `cat_periodo` es constante (un solo valor).
- ⚠️ `tipo_inst_1` es constante (un solo valor).
- ⚠️ `nivel_global` es constante (un solo valor).
