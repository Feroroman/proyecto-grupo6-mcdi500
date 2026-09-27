"""Fase 3 · Jerarquía de clases del pipeline de datos.

Reescritura orientada a objetos del pipeline de funciones de la Fase 2
(`src/limpieza.py`, `src/transformacion.py`, `src/escalado.py`).

El resultado numérico es EXACTAMENTE el mismo que el de la Fase 2: lo que cambia
es la forma de organizarlo. Cada etapa deja de ser una función suelta y pasa a
ser una clase que hereda de `Transformador` y responde siempre a la misma
interfaz:

    t.fit(df)        aprende de los datos lo que necesite (medianas, categorías…)
    t.apply(df)      aplica lo aprendido y devuelve un DataFrame NUEVO
    t.fit_apply(df)  las dos cosas seguidas

`Pipeline` encadena transformadores y los ejecuta en orden, midiendo tiempo y
memoria de cada uno. Eso responde a tres cosas a la vez:

  · POO real: herencia (todas heredan de `Transformador`), polimorfismo (el
    Pipeline llama `fit_apply` sin saber de qué clase es cada etapa) y
    encapsulamiento (lo aprendido queda dentro del objeto, en `self`).
  · Separar aprender de aplicar: las medianas y las categorías se calculan una
    sola vez y se pueden reaplicar a datos nuevos sin recalcularlas.
  · Eficiencia medible: `Pipeline.resumen()` entrega tiempo y memoria por etapa,
    que es el insumo directo del análisis de complejidad.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 3
"""
from __future__ import annotations

import time
import tracemalloc
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd


# ───────────────────────────────────────────────────────────────────────────
#  Clase base
# ───────────────────────────────────────────────────────────────────────────
class Transformador:
    """Clase base de toda etapa del pipeline.

    Define el contrato que cumplen todas las subclases. No se usa directamente:
    `_aprender` y `_transformar` están vacíos aquí y cada subclase los escribe.

    Atributos
    ---------
    nombre : str
        Etiqueta legible de la etapa; aparece en el resumen del pipeline.
    cifras : dict
        Números que justifican la decisión de esta etapa (cuántos nulos se
        imputaron, con qué valor, cuántas categorías se agruparon…). Es lo que
        después se cita en el informe y en la bitácora.
    ajustado : bool
        True una vez que `fit` corrió. `apply` falla si todavía es False.
    """

    def __init__(self, nombre: str) -> None:
        self.nombre: str = nombre
        self.cifras: Dict[str, Any] = {}
        self.ajustado: bool = False

    # -- métodos que cada subclase reescribe -------------------------------
    def _aprender(self, df: pd.DataFrame) -> None:
        """Calcula y guarda en `self` lo que la etapa necesite de los datos."""
        return None

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Devuelve un DataFrame NUEVO con la transformación aplicada."""
        raise NotImplementedError("Cada subclase debe implementar _transformar")

    # -- interfaz pública, igual para todas --------------------------------
    def fit(self, df: pd.DataFrame) -> "Transformador":
        """Aprende de `df`. Devuelve self para poder encadenar."""
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"{self.nombre}: se esperaba un DataFrame, llegó {type(df).__name__}")
        self._aprender(df)
        self.ajustado = True
        return self

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica la transformación. Exige haber llamado antes a `fit`."""
        if not self.ajustado:
            raise RuntimeError(f"{self.nombre}: hay que llamar fit() antes que apply()")
        return self._transformar(df)

    def fit_apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """Atajo para `fit` seguido de `apply`."""
        return self.fit(df).apply(df)

    def __repr__(self) -> str:
        estado = "ajustado" if self.ajustado else "sin ajustar"
        return f"<{type(self).__name__} '{self.nombre}' ({estado})>"


# ───────────────────────────────────────────────────────────────────────────
#  Etapas de limpieza
# ───────────────────────────────────────────────────────────────────────────
class EliminadorDuplicados(Transformador):
    """Elimina filas exactamente duplicadas (equivale a `eliminar_duplicados`)."""

    def __init__(self) -> None:
        super().__init__("Eliminar duplicados")

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.drop_duplicates().reset_index(drop=True)
        self.cifras = {"filas_antes": len(df), "filas_despues": len(out),
                       "eliminadas": len(df) - len(out)}
        return out


class CodigoAFaltante(Transformador):
    """Convierte un código de relleno en NaN (equivale a `codigo_a_nulo`).

    En este proyecto: `anio_ing_carr_ori` == 1900 no es un año real, es el
    código de «sin información» del Mineduc.
    """

    def __init__(self, columna: str, codigo: Any) -> None:
        super().__init__(f"Código {codigo!r} → faltante en '{columna}'")
        self.columna = columna
        self.codigo = codigo

    def _aprender(self, df: pd.DataFrame) -> None:
        if self.columna not in df.columns:
            raise KeyError(f"La columna '{self.columna}' no existe en el DataFrame")

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        mascara = out[self.columna] == self.codigo
        out.loc[mascara, self.columna] = np.nan
        n = int(mascara.sum())
        self.cifras = {"reemplazos": n, "porcentaje": round(100 * n / len(df), 2)}
        return out


class ImputadorMedianaPorGrupo(Transformador):
    """Imputa los nulos de `columna` con la mediana dentro de cada `grupo`.

    Aquí se ve por qué separar fit de apply: las medianas se APRENDEN en `fit`
    y quedan guardadas en `self.medianas_`. Si mañana llegan datos nuevos, se
    imputan con las mismas medianas y no con otras recalculadas.

    Deja además una columna bandera `<columna>_imputada` (True/False) para poder
    rehacer después el análisis excluyendo los casos imputados.
    """

    def __init__(self, columna: str, grupo: str) -> None:
        super().__init__(f"Imputar '{columna}' con mediana por '{grupo}'")
        self.columna = columna
        self.grupo = grupo
        self.medianas_: Optional[pd.Series] = None
        self.mediana_global_: Optional[float] = None

    def _aprender(self, df: pd.DataFrame) -> None:
        for c in (self.columna, self.grupo):
            if c not in df.columns:
                raise KeyError(f"La columna '{c}' no existe en el DataFrame")
        self.medianas_ = df.groupby(self.grupo)[self.columna].median()
        self.mediana_global_ = float(df[self.columna].median())

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        faltantes = out[self.columna].isna()
        desv_antes = out[self.columna].std()

        relleno = out[self.grupo].map(self.medianas_).fillna(self.mediana_global_)
        out[f"{self.columna}_imputada"] = faltantes
        out[self.columna] = out[self.columna].fillna(relleno)

        desv_despues = out[self.columna].std()
        self.cifras = {
            "imputados": int(faltantes.sum()),
            "porcentaje": round(100 * faltantes.mean(), 2),
            "desv_antes": round(float(desv_antes), 4),
            "desv_despues": round(float(desv_despues), 4),
            "cambio_desv_pct": round(100 * (desv_despues - desv_antes) / desv_antes, 2),
        }
        return out


class EliminadorConstantes(Transformador):
    """Elimina columnas con un único valor: no aportan información."""

    def __init__(self) -> None:
        super().__init__("Eliminar columnas constantes")
        self.constantes_: List[str] = []

    def _aprender(self, df: pd.DataFrame) -> None:
        self.constantes_ = [c for c in df.columns if df[c].nunique(dropna=True) <= 1]

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        self.cifras = {"eliminadas": len(self.constantes_), "columnas": list(self.constantes_)}
        return df.drop(columns=self.constantes_)


# ───────────────────────────────────────────────────────────────────────────
#  Etapas de transformación
# ───────────────────────────────────────────────────────────────────────────
class CodificadorOrdinal(Transformador):
    """Codifica una variable ordinal respetando un orden DECLARADO.

    El orden se pasa a mano justamente para no dejar que la librería ordene
    alfabéticamente: «40 y más años» quedaría antes que «15 a 19 Años» y la
    escala sería inventada.
    """

    def __init__(self, columna: str, orden: Sequence[str]) -> None:
        super().__init__(f"Codificar ordinal '{columna}'")
        self.columna = columna
        self.orden = list(orden)
        self.mapa_: Dict[str, int] = {}

    def _aprender(self, df: pd.DataFrame) -> None:
        if self.columna not in df.columns:
            raise KeyError(f"La columna '{self.columna}' no existe en el DataFrame")
        self.mapa_ = {categoria: i for i, categoria in enumerate(self.orden)}
        observadas = set(df[self.columna].dropna().unique())
        sin_mapear = observadas - set(self.mapa_)
        if sin_mapear:
            raise ValueError(f"'{self.columna}' tiene categorías fuera del orden declarado: {sorted(sin_mapear)}")

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out[f"{self.columna}_ord"] = out[self.columna].map(self.mapa_)
        self.cifras = {"niveles": len(self.mapa_), "mapa": dict(self.mapa_)}
        return out


class AgrupadorRaras(Transformador):
    """Agrupa bajo una etiqueta común las categorías con menos de `min_frec` casos.

    Es la técnica estándar para alta cardinalidad: `nomb_carrera` tiene 1.096
    valores distintos; sin agrupar, el one-hot produciría más de mil columnas
    casi vacías.

    Las categorías frecuentes se APRENDEN en `fit` (`self.frecuentes_`), así que
    la agrupación es reproducible sobre cualquier subconjunto.
    """

    def __init__(self, columna: str, min_frec: int, etiqueta: str = "OTRA") -> None:
        super().__init__(f"Agrupar categorías raras de '{columna}'")
        self.columna = columna
        self.min_frec = min_frec
        self.etiqueta = etiqueta
        self.frecuentes_: set = set()

    def _aprender(self, df: pd.DataFrame) -> None:
        if self.columna not in df.columns:
            raise KeyError(f"La columna '{self.columna}' no existe en el DataFrame")
        conteo = df[self.columna].value_counts()
        self.frecuentes_ = set(conteo[conteo >= self.min_frec].index)
        self.cifras = {"categorias_originales": int(conteo.size),
                       "agrupadas": int((conteo < self.min_frec).sum()),
                       "categorias_finales": len(self.frecuentes_) + 1}

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        # Vectorizado: una sola pasada con `where`, no un bucle fila por fila.
        out[self.columna] = out[self.columna].where(
            out[self.columna].isin(self.frecuentes_), self.etiqueta)
        return out


class CodificadorOneHot(Transformador):
    """Convierte variables nominales en columnas 0/1, una por categoría.

    Las categorías de cada columna se aprenden en `fit`, de modo que el
    DataFrame transformado siempre tiene las mismas columnas en el mismo orden,
    aunque un subconjunto no contenga alguna categoría.
    """

    def __init__(self, columnas: Sequence[str]) -> None:
        super().__init__("Codificación one-hot")
        self.columnas = list(columnas)
        self.categorias_: Dict[str, List[Any]] = {}

    def _aprender(self, df: pd.DataFrame) -> None:
        faltan = [c for c in self.columnas if c not in df.columns]
        if faltan:
            raise KeyError(f"Columnas ausentes para one-hot: {faltan}")
        self.categorias_ = {c: sorted(df[c].dropna().unique().tolist()) for c in self.columnas}

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        nuevas: List[str] = []
        for col, cats in self.categorias_.items():
            for cat in cats:
                nombre = f"{col}__{cat}"
                out[nombre] = (out[col] == cat).astype(int)
                nuevas.append(nombre)
        self.cifras = {"columnas_origen": len(self.columnas), "columnas_generadas": len(nuevas)}
        return out


class EscaladorRobusto(Transformador):
    """Escala columnas numéricas restando la mediana y dividiendo por el RIC.

    Se elige el robusto por coherencia con lo decidido antes: ya se reconocieron
    valores extremos (9,4 % de atípicos) y se imputó con mediana; centrar con la
    media al escalar sería contradictorio.

    Mediana y RIC se aprenden en `fit` y quedan en `self.mediana_` / `self.ric_`.
    Propiedad verificable del resultado: mediana 0 y RIC 1.
    """

    def __init__(self, columnas: Sequence[str]) -> None:
        super().__init__("Escalado robusto")
        self.columnas = list(columnas)
        self.mediana_: Dict[str, float] = {}
        self.ric_: Dict[str, float] = {}

    def _aprender(self, df: pd.DataFrame) -> None:
        for c in self.columnas:
            if c not in df.columns:
                raise KeyError(f"La columna '{c}' no existe en el DataFrame")
            if not pd.api.types.is_numeric_dtype(df[c]):
                raise TypeError(f"'{c}' no es numérica; no se puede escalar")
            q1, q3 = df[c].quantile(0.25), df[c].quantile(0.75)
            ric = q3 - q1
            if ric == 0:
                raise ValueError(f"'{c}' tiene rango intercuartílico 0; no se puede escalar")
            self.mediana_[c] = float(df[c].median())
            self.ric_[c] = float(ric)

    def _transformar(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for c in self.columnas:
            out[f"{c}_esc"] = (out[c] - self.mediana_[c]) / self.ric_[c]
        self.cifras = {"columnas": len(self.columnas),
                       "mediana": dict(self.mediana_), "ric": dict(self.ric_)}
        return out


# ───────────────────────────────────────────────────────────────────────────
#  El pipeline
# ───────────────────────────────────────────────────────────────────────────
class Pipeline:
    """Encadena transformadores y los ejecuta en orden, midiendo cada etapa.

    Aquí se ve el polimorfismo: el bucle de `fit_apply` llama al mismo método
    en objetos de clases distintas sin preguntar de qué clase es cada uno. Para
    agregar una etapa nueva basta escribir otra subclase de `Transformador`; el
    Pipeline no cambia ni una línea.

    Uso
    ---
    >>> pipe = Pipeline([EliminadorDuplicados(), EliminadorConstantes()])
    >>> limpio = pipe.fit_apply(df)
    >>> pipe.resumen()        # tiempo, memoria y forma resultante por etapa
    >>> pipe.cifras()         # las cifras que justifican cada decisión
    """

    def __init__(self, etapas: Sequence[Transformador], nombre: str = "Pipeline F2") -> None:
        if not etapas:
            raise ValueError("El pipeline necesita al menos una etapa")
        for e in etapas:
            if not isinstance(e, Transformador):
                raise TypeError(f"{e!r} no es un Transformador")
        self.nombre = nombre
        self.etapas: List[Transformador] = list(etapas)
        self.mediciones_: List[Dict[str, Any]] = []

    def fit_apply(self, df: pd.DataFrame, verboso: bool = True) -> pd.DataFrame:
        """Ejecuta todas las etapas en orden sobre una COPIA de `df`."""
        actual = df.copy()
        self.mediciones_ = []

        for i, etapa in enumerate(self.etapas, start=1):
            tracemalloc.start()
            t0 = time.perf_counter()
            actual = etapa.fit_apply(actual)
            segundos = time.perf_counter() - t0
            _, pico = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            self.mediciones_.append({
                "orden": i,
                "etapa": etapa.nombre,
                "clase": type(etapa).__name__,
                "segundos": round(segundos, 4),
                "memoria_pico_mb": round(pico / 1_048_576, 2),
                "filas": len(actual),
                "columnas": actual.shape[1],
            })
            if verboso:
                print(f"  {i:>2}. {etapa.nombre:<48} {segundos:>7.3f}s   "
                      f"{pico/1_048_576:>7.1f} MB   {actual.shape[0]:>7,} × {actual.shape[1]:<3}")

        return actual

    def resumen(self) -> pd.DataFrame:
        """Tabla de tiempo, memoria y forma por etapa, ordenada por costo."""
        if not self.mediciones_:
            raise RuntimeError("Hay que ejecutar fit_apply() antes de pedir el resumen")
        tabla = pd.DataFrame(self.mediciones_)
        total = tabla["segundos"].sum()
        tabla["pct_tiempo"] = (100 * tabla["segundos"] / total).round(1)
        return tabla

    def etapa_dominante(self) -> Dict[str, Any]:
        """La etapa que más tiempo consume: el punto donde optimizar rinde."""
        tabla = self.resumen()
        fila = tabla.loc[tabla["segundos"].idxmax()]
        return fila.to_dict()

    def cifras(self) -> pd.DataFrame:
        """Las cifras que justifican cada decisión, para citar en el informe."""
        filas = [{"etapa": e.nombre, "clave": k, "valor": v}
                 for e in self.etapas for k, v in e.cifras.items()
                 if not isinstance(v, (dict, list))]
        return pd.DataFrame(filas)

    def __len__(self) -> int:
        return len(self.etapas)

    def __repr__(self) -> str:
        return f"<Pipeline '{self.nombre}' con {len(self.etapas)} etapas>"
