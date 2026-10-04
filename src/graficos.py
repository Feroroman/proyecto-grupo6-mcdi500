import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path

# Importaciones ajustadas a los nombres reales que usó Fernanda
from src.interpretable import cargar_interpretable
from src.tablas import todas

def configurar_estilo():
    sns.set_theme(style="whitegrid")
    return {"acento": "#d95f02", "neutro": "#cccccc"}

colores = configurar_estilo()

def graficar_f1_distribucion(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(data=df, x="dur_total_carr", bins=20, color=colores["neutro"], ax=ax)
    mediana = df["dur_total_carr"].median()
    ax.axvline(mediana, color=colores["acento"], linestyle="--", linewidth=2, label=f"Mediana: {mediana} semestres")
    
    ax.set_title("La mayor parte de los titulados demora 10 o más semestres en graduarse", fontsize=14, pad=15)
    ax.set_xlabel("Duración total de la carrera (semestres)")
    ax.set_ylabel("Cantidad de titulados")
    ax.legend()
    
    plt.tight_layout()
    plt.savefig("docs/figuras/f4_01_distribucion.png")
    plt.close()

def graficar_f2_tamano_grupos(tabla_tamanos):
    fig, ax = plt.subplots(figsize=(10, 6))
    # Fernanda agrupó por 'area_conocimiento' por defecto
    sns.barplot(data=tabla_tamanos, y="area_conocimiento", x="n", color=colores["neutro"], ax=ax)
    
    ax.set_title("Distribución de registros de titulación por área de conocimiento", fontsize=14, pad=15)
    ax.set_xlabel("Cantidad de observaciones (n)")
    ax.set_ylabel("Área de Conocimiento")
    ax.set_xlim(left=0) 
    
    plt.tight_layout()
    plt.savefig("docs/figuras/f4_02_tamanos.png")
    plt.close()

def graficar_f3_duracion_jornada(tabla_jornada):
    fig, ax = plt.subplots(figsize=(10, 6))
    paleta = [colores["acento"] if j == "Diurna" else colores["neutro"] for j in tabla_jornada["jornada"]]
    # La tabla de Fernanda ya trae la columna calculada como 'mediana'
    sns.barplot(data=tabla_jornada, y="jornada", x="mediana", palette=paleta, ax=ax)
    
    ax.set_title("La jornada diurna registra mayor duración mediana que la vespertina", fontsize=14, pad=15)
    ax.set_xlabel("Mediana de duración (semestres)")
    ax.set_ylabel("Jornada")
    ax.set_xlim(left=0)
    
    plt.tight_layout()
    plt.savefig("docs/figuras/f4_03_duracion_jornada.png")
    plt.close()

def graficar_f4_dispersion(df_serie):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df_serie, y="jornada", x="dur_total_carr", color=colores["neutro"], fliersize=0, ax=ax)
    
    muestra = df_serie.sample(min(3000, len(df_serie)))
    sns.stripplot(data=muestra, y="jornada", x="dur_total_carr", color=colores["acento"], alpha=0.4, size=3, ax=ax)
    
    ax.set_title("La duración en la jornada diurna presenta una mayor amplitud de dispersión", fontsize=14, pad=15)
    ax.set_xlabel("Duración total (semestres)")
    ax.set_ylabel("Jornada")
    
    plt.tight_layout()
    plt.savefig("docs/figuras/f4_04_dispersion.png")
    plt.close()

def graficar_f5_paneles_area(df):
    g = sns.catplot(
        data=df, x="dur_total_carr", y="jornada", col="area_conocimiento", col_wrap=3,
        kind="bar", estimator="median", errorbar=None, color=colores["neutro"], height=4, aspect=1.2
    )
    
    g.figure.subplots_adjust(top=0.88)
    g.figure.suptitle("El patrón de mayor duración persiste en todas las áreas de conocimiento", fontsize=14)
    g.set_axis_labels("Duración (semestres)", "Jornada")
    
    for ax in g.axes.flat:
        ax.set_xlim(left=0)
        
    plt.savefig("docs/figuras/f4_05_paneles_area.png")
    plt.close()

def graficar_f6_imputacion(tabla_imputacion):
    fig, ax = plt.subplots(figsize=(10, 6))
    # Nombres de columnas de Fernanda: observados_pct e imputados_pct
    tabla_imputacion.set_index('jornada')[['observados_pct', 'imputados_pct']].plot(
        kind='barh', stacked=True, color=[colores["neutro"], colores["acento"]], ax=ax
    )
    
    ax.set_title("La imputación por falta de ingreso original se concentra en las modalidades a distancia", fontsize=14, pad=15)
    ax.set_xlabel("Proporción de los registros (%)")
    ax.set_ylabel("Jornada")
    ax.legend(["Dato Observado", "Dato Imputado"], loc="lower right")
    ax.set_xlim(0, 100) # Ajustado a escala de 100% usada en tablas.py
    
    plt.tight_layout()
    plt.savefig("docs/figuras/f4_06_imputacion.png")
    plt.close()

if __name__ == "__main__":
    Path("docs/figuras").mkdir(parents=True, exist_ok=True)
    
    print("Cargando datos interpretables...")
    # Llamadas exactas a las funciones de Fernanda
    df_interpretable = cargar_interpretable()
    # Su función requiere que le pases el dataframe como argumento
    tablas = todas(df_interpretable) 
    
    print("Generando las seis figuras...")
    graficar_f1_distribucion(df_interpretable)
    
    # Referenciamos los diccionarios con las llaves que ella definió
    graficar_f2_tamano_grupos(tablas["f2_tamanos"])
    graficar_f3_duracion_jornada(tablas["f3_por_jornada"])
    graficar_f4_dispersion(tablas["f4_serie"])
    graficar_f5_paneles_area(df_interpretable)
    graficar_f6_imputacion(tablas["f6_imputacion"])
    
    print("[Éxito] Figuras exportadas a docs/figuras/")