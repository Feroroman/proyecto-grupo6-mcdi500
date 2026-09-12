#!/usr/bin/env python3
from __future__ import annotations
"""
validar_dataset.py — Validación rápida de un dataset CSV.

Uso:
    python validar_dataset.py data/raw/mi_dataset.csv
    python validar_dataset.py datos.csv --sep ";" --encoding latin-1
    python validar_dataset.py datos.csv --informe docs/validacion_dataset.md
"""
import argparse
import csv
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    sys.exit("Falta pandas. Instálalo con: pip install pandas")


def detectar_separador(ruta: Path, encoding: str) -> str:
    """Intenta adivinar el separador leyendo las primeras líneas."""
    with open(ruta, "r", encoding=encoding, errors="replace") as f:
        muestra = f.read(20000)
    try:
        return csv.Sniffer().sniff(muestra, delimiters=",;\t|").delimiter
    except csv.Error:
        return ","


def validar(ruta: Path, sep: str | None, encoding: str) -> tuple[list[str], list[str]]:
    lineas: list[str] = []
    alertas: list[str] = []

    if not ruta.exists():
        sys.exit(f"ERROR: no se encontró el archivo {ruta}")

    if sep is None:
        sep = detectar_separador(ruta, encoding)

    try:
        df = pd.read_csv(ruta, sep=sep, encoding=encoding, low_memory=False)
    except UnicodeDecodeError:
        sys.exit(f"ERROR: no se pudo leer con encoding '{encoding}'. Prueba --encoding latin-1")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR al leer el archivo: {e}")

    tam_mb = ruta.stat().st_size / 1_048_576
    mem_mb = df.memory_usage(deep=True).sum() / 1_048_576

    lineas.append(f"# Informe de validación: `{ruta.name}`\n")
    lineas.append("## Resumen general\n")
    lineas.append(f"- Ruta: `{ruta}`")
    lineas.append(f"- Tamaño en disco: {tam_mb:,.1f} MB")
    lineas.append(f"- Separador: `{sep!r}` · Encoding: `{encoding}`")
    lineas.append(f"- Filas: {df.shape[0]:,} · Columnas: {df.shape[1]}")
    lineas.append(f"- Memoria en pandas: {mem_mb:,.1f} MB")

    if df.shape[1] == 1:
        alertas.append("Solo se detectó 1 columna: probablemente el separador es incorrecto (usa --sep).")

    # Duplicados
    dup = int(df.duplicated().sum())
    lineas.append(f"- Filas duplicadas: {dup:,}")
    if dup:
        alertas.append(f"Hay {dup:,} filas duplicadas.")

    # Columnas
    lineas.append("\n## Columnas\n")
    lineas.append("| Columna | Tipo | Nulos | % nulos | Únicos | Ejemplo |")
    lineas.append("|---|---|---:|---:|---:|---|")
    n = len(df)
    for col in df.columns:
        s = df[col]
        nulos = int(s.isna().sum())
        pct = 100 * nulos / n if n else 0
        unicos = int(s.nunique(dropna=True))
        ejemplo = s.dropna().iloc[0] if unicos else ""
        ejemplo = str(ejemplo).replace("|", "\\|")[:40]
        lineas.append(f"| `{col}` | {s.dtype} | {nulos:,} | {pct:.1f}% | {unicos:,} | {ejemplo} |")
        if pct > 50:
            alertas.append(f"`{col}` tiene {pct:.0f}% de valores nulos.")
        if unicos == 1:
            alertas.append(f"`{col}` es constante (un solo valor).")
        if unicos == 0:
            alertas.append(f"`{col}` está completamente vacía.")

    # Nombres de columnas problemáticos
    raros = [c for c in df.columns if c != c.strip() or " " in c or str(c).startswith("Unnamed")]
    if raros:
        alertas.append(f"Columnas con nombres problemáticos (espacios/sin nombre): {raros}")

    # Estadísticas numéricas
    num = df.select_dtypes("number")
    if not num.empty:
        lineas.append("\n## Estadísticas numéricas\n")
        desc = num.describe().T[["mean", "std", "min", "max"]].round(2)
        lineas.append("| Columna | Media | Desv. | Mín | Máx |")
        lineas.append("|---|---:|---:|---:|---:|")
        for col, r in desc.iterrows():
            lineas.append(f"| `{col}` | {r['mean']} | {r['std']} | {r['min']} | {r['max']} |")

    # Alertas
    lineas.append("\n## Alertas\n")
    if alertas:
        lineas.extend(f"- ⚠️ {a}" for a in alertas)
    else:
        lineas.append("- ✅ Sin problemas detectados.")

    return lineas, alertas


def main() -> None:
    p = argparse.ArgumentParser(description="Valida un dataset CSV y genera un informe.")
    p.add_argument("archivo", help="Ruta al archivo CSV")
    p.add_argument("--sep", default=None, help="Separador (por defecto se detecta automáticamente)")
    p.add_argument("--encoding", default="utf-8", help="Codificación del archivo (por defecto utf-8)")
    p.add_argument("--informe", default=None, help="Ruta del informe Markdown a generar")
    args = p.parse_args()

    lineas, alertas = validar(Path(args.archivo), args.sep, args.encoding)
    texto = "\n".join(lineas) + "\n"

    if args.informe:
        salida = Path(args.informe)
        salida.parent.mkdir(parents=True, exist_ok=True)
        salida.write_text(texto, encoding="utf-8")
        print(f"Informe guardado en {salida}")
        print(f"Alertas: {len(alertas)}")
    else:
        print(texto)


if __name__ == "__main__":
    main()
