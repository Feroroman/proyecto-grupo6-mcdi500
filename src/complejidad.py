"""Fase 3 · Análisis de Complejidad y Rendimiento.

Módulo encargado de medir empíricamente el tiempo de ejecución y el consumo
máximo de memoria de los algoritmos desarrollados en `src/algoritmos.py`.
Genera los gráficos comparativos de eficiencia para el informe de la Fase 3.

Autoría: Jorge Álvarez Ossandón · MCDI500 · Fase 3
"""
from __future__ import annotations

import os
import time
import tracemalloc
import unittest
from typing import Any, Callable, Dict, List, Tuple

import matplotlib.pyplot as plt
import pandas as pd

# Corrección crítica 3: Importación absoluta desde la raíz del repositorio
from src.algoritmos import (
    cuantil_ordenando,
    cuantil_quickselect,
    explorar_con_poda,
    explorar_exhaustivo,
)


# ═══════════════════════════════════════════════════════════════════════
#  CLASE MEDIDOR DE COMPLEJIDAD (POO JUSTIFICADA)
# ═══════════════════════════════════════════════════════════════════════
class MedidorComplejidad:
    """Clase para encapsular la lógica de evaluación de rendimiento,
    midiendo tiempo, memoria y llamadas recursivas de distintas funciones.
    """
    def __init__(self, repeticiones: int = 5):
        self.repeticiones = repeticiones

    def medir(self, funcion: Callable, *args: Any) -> Dict[str, float]:
        """Ejecuta una función múltiples veces y devuelve sus métricas de rendimiento."""
        if not callable(funcion):
            raise TypeError("El argumento 'funcion' debe ser ejecutable (callable).")

        tiempos: List[float] = []
        memorias: List[int] = []

        for _ in range(self.repeticiones):
            tracemalloc.start()  # Captura de memoria exigida
            inicio = time.time()
            
            resultado = funcion(*args)
            
            fin = time.time()
            _, pico_memoria = tracemalloc.get_traced_memory()  # Extracción del pico de memoria
            tracemalloc.stop()  # Detención del rastreo

            tiempos.append(fin - inicio)
            memorias.append(pico_memoria)

        # Captura de nodos visitados si la función es de exploración y los devuelve
        nodos_visitados = 0
        if isinstance(resultado, tuple) and len(resultado) == 2 and isinstance(resultado[1], dict):
            nodos_visitados = resultado[1].get("nodos_visitados", 0)

        return {
            "tiempo_promedio": sum(tiempos) / self.repeticiones,
            "memoria_pico_bytes": max(memorias),
            "nodos_visitados": nodos_visitados
        }

    def comparar(self, candidatos: Dict[str, Callable], tamaños: List[int], generador_args: Callable) -> pd.DataFrame:
        """Mide y compara un diccionario de funciones sobre distintos tamaños de datos."""
        if sorted(tamaños) != tamaños:
            raise ValueError("La lista de tamaños debe estar ordenada de menor a mayor.")

        resultados: List[Dict[str, Any]] = []
        
        for n in tamaños:
            args_n = generador_args(n)
            for nombre, funcion in candidatos.items():
                if isinstance(args_n, tuple):
                    metricas = self.medir(funcion, *args_n)
                else:
                    metricas = self.medir(funcion, args_n)
                
                resultados.append({
                    "Tamaño (N)": n,
                    "Algoritmo": nombre,
                    "Tiempo (s)": metricas["tiempo_promedio"],
                    "Memoria (Bytes)": metricas["memoria_pico_bytes"],
                    "Nodos Visitados": metricas["nodos_visitados"]
                })
                
        return pd.DataFrame(resultados)

    def graficar(self, tabla: pd.DataFrame, ruta: str, metrica: str = "Tiempo (s)", titulo: str = "") -> str:
        """Construye y exporta un gráfico comparativo a partir de los resultados medidos."""
        plt.figure(figsize=(9, 5))
        for algoritmo in tabla["Algoritmo"].unique():
            sub_df = tabla[tabla["Algoritmo"] == algoritmo]
            # Seleccionar marcador según el algoritmo para mejor visualización
            marcador = 'o' if "Ingenuo" in algoritmo or "Exhaustivo" in algoritmo else 's'
            plt.plot(sub_df["Tamaño (N)"], sub_df[metrica], marker=marcador, label=algoritmo, linewidth=2)
        
        plt.title(titulo or f"Comparación de {metrica}")
        plt.xlabel("Tamaño de los datos (N)")
        plt.ylabel(metrica)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        plt.savefig(ruta, bbox_inches='tight')
        plt.close()
        return ruta


# ═══════════════════════════════════════════════════════════════════════
#  PRUEBAS UNITARIAS (TESTING BÁSICO)
# ═══════════════════════════════════════════════════════════════════════
class TestMedidorComplejidad(unittest.TestCase):
    """Pruebas unitarias para validar la integridad del Medidor de Complejidad."""
    def setUp(self):
        self.medidor = MedidorComplejidad(repeticiones=1)
        
    def funcion_dummy(self, n: int) -> List[int]:
        time.sleep(0.01)
        return list(range(n))
        
    def test_medir_devuelve_tiempo_positivo(self):
        """Verifica que el medidor devuelva un tiempo de ejecución mayor a cero."""
        resultado = self.medidor.medir(self.funcion_dummy, 100)
        self.assertGreater(resultado["tiempo_promedio"], 0.0)
        self.assertGreaterEqual(resultado["memoria_pico_bytes"], 0)
        
    def test_falla_con_algo_que_no_es_funcion(self):
        """Verifica que se lance un TypeError si el objetivo no es ejecutable."""
        with self.assertRaises(TypeError):
            self.medidor.medir("un_string_cualquiera", 10)
            
    def test_comparar_falla_con_tamanos_desordenados(self):
        """Verifica que comparar rechace listas de tamaño sin orden ascendente."""
        with self.assertRaises(ValueError):
            self.medidor.comparar({"f": self.funcion_dummy}, [5000, 1000], lambda x: (x,))
            
    def test_comparar_devuelve_una_fila_por_tamano(self):
        """Verifica que la salida de comparar tenga tantas filas como tamaños por algoritmo."""
        tamanos = [10, 20]
        df = self.medidor.comparar({"f": self.funcion_dummy}, tamanos, lambda x: (x,))
        self.assertEqual(len(df), len(tamanos))


# ═══════════════════════════════════════════════════════════════════════
#  EJECUCIÓN PRINCIPAL CON DATOS REALES
# ═══════════════════════════════════════════════════════════════════════
def ejecutar_auditoria() -> None:
    """Función orquestadora que lee el dataset real y genera los gráficos."""
    ruta_datos = os.path.join("data", "processed", "titulados_2025_pregrado_univ_limpio.csv")
    
    try:
        # Carga del dataset real exigida en los criterios
        df_real = pd.read_csv(ruta_datos, sep=";")
        duraciones = df_real["dur_total_carr"].dropna().tolist()
    except FileNotFoundError:
        print(f"[Error] No se encontró {ruta_datos}. Ejecute desde la raíz del repositorio.")
        return

    medidor = MedidorComplejidad(repeticiones=3)
    tamanos = [1000, 5000, 10000, 20000, 50000]
    ruta_figuras = os.path.join("docs", "figuras")

    # 1. Preparar funciones candidatas
    candidatos_cuantiles = {
        "Ingenuo (Ordena todo O(n log n))": cuantil_ordenando,
        "Quickselect (Optimizado O(n))": cuantil_quickselect
    }

    # 2. Generador de argumentos para inyectar porciones del dataset real
    def inyectar_datos_reales(n: int) -> Tuple[List[float], float]:
        porcion = duraciones[:n] if n <= len(duraciones) else duraciones
        return (porcion, 0.5)

    print("Midiendo tiempos y memoria sobre el dataset real...")
    resultados_df = medidor.comparar(candidatos_cuantiles, tamanos, inyectar_datos_reales)

    # 3. Exportar figuras con los nombres solicitados por Sebastián
    rutas_generadas = [
        medidor.graficar(
            resultados_df,
            ruta=os.path.join(ruta_figuras, "f3_01_complejidad_temporal.png"),
            metrica="Tiempo (s)",
            titulo="Complejidad Temporal: Cuantil Ingenuo vs Quickselect"
        ),
        medidor.graficar(
            resultados_df,
            ruta=os.path.join(ruta_figuras, "f3_02_consumo_memoria.png"),
            metrica="Memoria (Bytes)",
            titulo="Consumo de Memoria: Cuantil Ingenuo vs Quickselect"
        )
    ]
    
    print("\n[Éxito] Gráficos exportados correctamente:")
    for r in rutas_generadas:
        print(f" -> {r}")


if __name__ == "__main__":
    print("Iniciando conjunto de pruebas unitarias...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMedidorComplejidad)
    resultado_tests = unittest.TextTestRunner(verbosity=2).run(suite)
    
    if resultado_tests.wasSuccessful():
        print("\nPruebas aprobadas. Procediendo con el análisis del dataset...")
        ejecutar_auditoria()
    else:
        print("\n[Alerta] Las pruebas unitarias fallaron. Revise el código antes de medir.")