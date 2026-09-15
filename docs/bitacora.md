# Bitácora de decisiones

Generada el 2026-09-15 14:22

- [F2 · obtención] lectura de data/processed/titulados_2025_pregrado_univ.csv → 105,063 filas × 40 columnas (sep ';', UTF-8)
- [F2 · exploración] código 1900 en anio_ing_carr_ori: 13,396 registros (12,8 %) con duración mediana 6 vs 10 semestres → no es un faltante aleatorio
- [F2 · exploración] dur_total_carr: mediana 10 semestres, RIC 2, 9,845 atípicos (9.4 %) por regla 1,5·RIC → hay valores extremos
- [F2 · limpieza] duplicados exactos: 3 filas eliminadas (0.003 %) → 105,060 filas
- [F2 · limpieza] columnas constantes eliminadas (un solo valor tras el filtro de F1): ['cat_periodo', 'tipo_inst_1', 'nivel_global']
- [F2 · limpieza] anio_ing_carr_ori: código 1900 tratado como faltante en 13,396 filas (12.8 %); sem_ing_carr_ori: código 0 tratado como faltante en 13,396 filas (12.8 %)
- [F2 · limpieza] anio_ing_carr_ori: 13,396 nulos (12.75 %) imputados con mediana por anio_ing_carr_act; cambio en la desviación estándar +2.82 %; bandera anio_ing_carr_ori_imputada
- [F2 · limpieza] sem_ing_carr_ori: 13,396 nulos (12.75 %) imputados con la mediana = 1
- [F2 · limpieza] nombre_titulo (2,9 % nulos) y nombre_grado (8,0 %) se conservan sin imputar: son etiquetas de texto, no variables de análisis; mrun con 7 nulos se conserva porque el análisis no cuenta personas sino títulos
- [F2 · transformación] ordinales codificadas con orden declarado: rango_edad (6 niveles) y nivel_carrera_1 (4 niveles); 0 registros con rango_edad [] quedan como faltante
- [F2 · transformación] fechas: fecha_obtencion_titulo y fec_nac_alu parseadas; derivadas mes_titulacion y edad_titulacion (mediana 25.6 años); 0 'Sin Información' de rango_edad recuperados desde edad_titulacion
- [F2 · transformación] one-hot encoding de 5 nominales → 36 columnas 0/1
- [F2 · transformación] nomb_carrera: 968 categorías con < 100 registros agrupadas en 'OTRA' → 129 categorías
- [F2 · transformación] gen_alu recodificada como mujer (0/1): 56.3% mujeres
- [F2 · escalamiento] RobustScaler (mediana 0, RIC 1) aplicado a ['dur_total_carr', 'dur_estudio_carr', 'edad_titulacion']: coherente con la imputación por mediana y con los atípicos detectados; MinMax comprimiría el 90 % de los datos en un rango estrecho por el máximo de 24 semestres
- [F2 · validación] 5 comprobaciones superadas sobre 48 columnas de análisis; propiedad mediana 0 / RIC 1 verificada
- [F2 · validación] pruebas unitarias de src/ (tests/test_pipeline.py): 11/11 pruebas superadas
- [F2 · persistencia] titulados_2025_pregrado_univ_limpio.csv: 105,060 × 84, releído y verificado (forma y columnas)
