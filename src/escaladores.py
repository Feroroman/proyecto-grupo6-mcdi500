"""Fase 3 · Patrón Strategy aplicado al escalamiento.

En la Fase 2 el escalamiento eran tres funciones sueltas —`escalar_estandar`,
`escalar_minmax` y `escalar_robusto`— y elegir una significaba escribir su nombre
en el notebook. Funcionaba, pero tenía un problema de diseño: **el código que
escala decidía también CÓMO escalar**. Cambiar de criterio obligaba a tocar el
código que lo usa, y comparar dos criterios obligaba a duplicarlo.

El patrón **Strategy** separa esas dos responsabilidades:

- Una familia de algoritmos intercambiables, cada uno en su propia clase, todos
  cumpliendo la misma interfaz (`EstrategiaEscalado` y sus tres hijas).
- Un contexto que usa uno de ellos sin saber cuál es (`Escalador`), y que puede
  cambiarlo en tiempo de ejecución.

Qué gana el proyecto con esto, concretamente:

1. **Comparar es trivial.** `comparar_estrategias` recorre las tres sobre la misma
   serie sin un solo `if`. La decisión de la Fase 2 —usar el robusto— deja de ser
   una afirmación del informe y pasa a ser una tabla reproducible.
2. **Agregar un escalador nuevo no toca nada existente.** Basta otra subclase;
   ni `Escalador` ni el pipeline cambian una línea. Es el principio
   abierto/cerrado: abierto a extensión, cerrado a modificación.
3. **La estrategia viaja como dato.** Se puede leer de la configuración, elegir
   según el diagnóstico de los datos o intercambiar en una prueba.

Relación con el resto del proyecto: `src/pipeline.py` usa estas estrategias en su
etapa de escalado, de modo que el patrón no es un ejercicio aparte sino la pieza
que decide cómo se transforman las tres duraciones del dataset.

Autoría: Fernanda Ovalle Román · MCDI500 · Fase 3
"""
from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Type

import numpy as np
import pandas as pd


# ───────────────────────────────────────────────────────────────────────
#  La interfaz común: qué debe saber hacer toda estrategia de escalado
# ───────────────────────────────────────────────────────────────────────
class EstrategiaEscalado:
    """Interfaz que comparten todos los escaladores intercambiables.

    Cada estrategia separa aprender de aplicar, igual que los transformadores
    del pipeline: `ajustar` calcula los parámetros a partir de los datos y los
    guarda dentro del objeto; `aplicar` los usa. Esa separación es la que
    permite escalar datos nuevos con los parámetros de los originales.

    Atributos
    ---------
    nombre : str            etiqueta legible, aparece en las tablas comparativas
    centro_ : float         el valor que se resta (media, mínimo o mediana)
    escala_ : float         el valor por el que se divide (desviación, rango o RIC)
    """

    nombre: str = "base"
    #: Qué propiedad debe cumplir el resultado; se usa para verificarlo.
    propiedad: str = "—"

    def __init__(self) -> None:
        self.centro_: Optional[float] = None
        self.escala_: Optional[float] = None

    # -- lo que cada estrategia concreta define ---------------------------
    def _parametros(self, s: pd.Series) -> tuple:
        """Devuelve (centro, escala) calculados sobre `s`."""
        raise NotImplementedError("Cada estrategia define sus propios parámetros")

    def verificar(self, escalada: pd.Series) -> bool:
        """Comprueba que el resultado cumple la propiedad que la estrategia promete."""
        raise NotImplementedError("Cada estrategia define cómo verificarse")

    # -- interfaz pública, idéntica para todas ----------------------------
    def ajustar(self, s: pd.Series) -> "EstrategiaEscalado":
        """Calcula y guarda los parámetros. Devuelve self para encadenar."""
        s = _validar(s)
        centro, escala = self._parametros(s)
        if escala == 0:
            raise ValueError(
                f"'{s.name}' no admite {self.nombre}: la escala calculada es 0 "
                f"(la serie es constante o no tiene dispersión en este criterio)")
        self.centro_, self.escala_ = float(centro), float(escala)
        return self

    def aplicar(self, s: pd.Series) -> pd.Series:
        """Aplica los parámetros ya aprendidos. Exige haber llamado a `ajustar`."""
        if self.centro_ is None:
            raise RuntimeError(f"{self.nombre}: hay que llamar ajustar() antes que aplicar()")
        return (_validar(s) - self.centro_) / self.escala_

    def ajustar_aplicar(self, s: pd.Series) -> pd.Series:
        return self.ajustar(s).aplicar(s)

    def parametros(self) -> Dict[str, Optional[float]]:
        return {"estrategia": self.nombre, "centro": self.centro_, "escala": self.escala_}

    def __repr__(self) -> str:
        estado = "ajustada" if self.centro_ is not None else "sin ajustar"
        return f"<{type(self).__name__} ({estado})>"


def _validar(s: pd.Series) -> pd.Series:
    """Precondiciones comunes: numérica y sin nulos."""
    if not isinstance(s, pd.Series):
        raise TypeError(f"se esperaba una Series, llegó {type(s).__name__}")
    if not pd.api.types.is_numeric_dtype(s):
        raise TypeError(f"'{s.name}' no es numérica")
    if s.isna().any():
        raise ValueError(f"'{s.name}' tiene nulos: hay que imputar antes de escalar")
    return s.astype(float)


# ───────────────────────────────────────────────────────────────────────
#  Las tres estrategias concretas
# ───────────────────────────────────────────────────────────────────────
class EstandarizacionZ(EstrategiaEscalado):
    """(x − media) / desviación. Deja media 0 y desviación 1.

    Supone que los extremos son informativos y deben pesar. En este proyecto es
    la que NO se eligió, porque la media y la desviación son sensibles a los
    9,4 % de atípicos detectados en las duraciones.
    """

    nombre = "estandar"
    propiedad = "media 0 y desviación 1"

    def _parametros(self, s: pd.Series) -> tuple:
        return s.mean(), s.std(ddof=0)

    def verificar(self, escalada: pd.Series) -> bool:
        return abs(escalada.mean()) < 1e-9 and abs(escalada.std(ddof=0) - 1) < 1e-9


class NormalizacionMinMax(EstrategiaEscalado):
    """(x − mínimo) / (máximo − mínimo). Deja el rango en [0, 1].

    Útil cuando el rango importa en sí mismo. Su debilidad es que un único valor
    extremo fija el denominador: en estas duraciones, el máximo de 24 semestres
    comprime el 90 % de los datos en una franja estrecha.
    """

    nombre = "minmax"
    propiedad = "mínimo 0 y máximo 1"

    def _parametros(self, s: pd.Series) -> tuple:
        return s.min(), s.max() - s.min()

    def verificar(self, escalada: pd.Series) -> bool:
        return abs(escalada.min()) < 1e-9 and abs(escalada.max() - 1) < 1e-9


class EscaladoRobusto(EstrategiaEscalado):
    """(x − mediana) / rango intercuartílico. Deja mediana 0 y RIC 1.

    Es la estrategia elegida en este proyecto, y la razón es de coherencia: ya se
    habían reconocido valores extremos e imputado con mediana, de modo que
    centrar con la media al escalar habría contradicho esa decisión.
    """

    nombre = "robusto"
    propiedad = "mediana 0 y RIC 1"

    def _parametros(self, s: pd.Series) -> tuple:
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        return s.median(), q3 - q1

    def verificar(self, escalada: pd.Series) -> bool:
        ric = escalada.quantile(0.75) - escalada.quantile(0.25)
        return abs(escalada.median()) < 1e-9 and abs(ric - 1) < 1e-9


# ───────────────────────────────────────────────────────────────────────
#  El contexto: usa una estrategia sin saber cuál
# ───────────────────────────────────────────────────────────────────────
class Escalador:
    """Escala series delegando el cómo a la estrategia que recibe.

    Esta clase es el corazón del patrón: **no contiene ni una sola fórmula de
    escalamiento ni un solo `if` sobre el tipo de escalador**. Recibe la
    estrategia por constructor y le delega. Si mañana hace falta un escalador
    nuevo, esta clase no cambia.

    Uso
    ---
    >>> esc = Escalador(EscaladoRobusto())
    >>> y = esc.ajustar_aplicar(df["dur_total_carr"])
    >>> esc.verificar(y)               # True: mediana 0 y RIC 1
    >>> esc.cambiar_estrategia(EstandarizacionZ())   # otro criterio, misma interfaz
    """

    def __init__(self, estrategia: EstrategiaEscalado) -> None:
        self.cambiar_estrategia(estrategia)
        self.historial_: List[Dict[str, Optional[float]]] = []

    def cambiar_estrategia(self, estrategia: EstrategiaEscalado) -> "Escalador":
        """Sustituye la estrategia en tiempo de ejecución."""
        if not isinstance(estrategia, EstrategiaEscalado):
            raise TypeError(
                f"{estrategia!r} no es una EstrategiaEscalado; "
                f"el contexto solo trabaja con esa interfaz")
        self.estrategia = estrategia
        return self

    def ajustar(self, s: pd.Series) -> "Escalador":
        self.estrategia.ajustar(s)
        return self

    def aplicar(self, s: pd.Series) -> pd.Series:
        return self.estrategia.aplicar(s)

    def ajustar_aplicar(self, s: pd.Series) -> pd.Series:
        y = self.estrategia.ajustar_aplicar(s)
        self.historial_.append(self.estrategia.parametros())
        return y

    def verificar(self, escalada: pd.Series) -> bool:
        """¿El resultado cumple la propiedad que la estrategia promete?"""
        return bool(self.estrategia.verificar(escalada))

    def __repr__(self) -> str:
        return f"<Escalador con estrategia '{self.estrategia.nombre}'>"


# ───────────────────────────────────────────────────────────────────────
#  Registro de estrategias: una fábrica mínima
# ───────────────────────────────────────────────────────────────────────
ESTRATEGIAS: Dict[str, Type[EstrategiaEscalado]] = {
    "estandar": EstandarizacionZ,
    "minmax": NormalizacionMinMax,
    "robusto": EscaladoRobusto,
}


def crear_estrategia(nombre: str) -> EstrategiaEscalado:
    """Devuelve una estrategia a partir de su nombre.

    Permite que la elección venga de la configuración del proyecto o de un
    archivo, en vez de estar escrita en el código que escala.
    """
    if nombre not in ESTRATEGIAS:
        raise KeyError(f"estrategia '{nombre}' desconocida; disponibles: {sorted(ESTRATEGIAS)}")
    return ESTRATEGIAS[nombre]()


def comparar_estrategias(s: pd.Series,
                         nombres: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """Aplica varias estrategias a la MISMA serie y tabula el resultado.

    Es la demostración práctica de para qué sirve el patrón: el bucle no sabe
    qué escalador está usando, solo que todos responden a la misma interfaz.
    Sin Strategy, esta comparación exigiría un `if` por escalador.

    Devuelve una tabla con media, desviación, mediana, RIC, mínimo, máximo y si
    el resultado cumple la propiedad que la estrategia promete.
    """
    nombres = list(nombres) if nombres else list(ESTRATEGIAS)
    filas = []

    base = _validar(s)
    filas.append({"estrategia": "original", "propiedad": "—", "media": base.mean(),
                  "desv": base.std(ddof=0), "mediana": base.median(),
                  "ric": base.quantile(0.75) - base.quantile(0.25),
                  "min": base.min(), "max": base.max(), "cumple": True})

    escalador = Escalador(crear_estrategia(nombres[0]))
    for nombre in nombres:
        escalador.cambiar_estrategia(crear_estrategia(nombre))   # el contexto no cambia
        try:
            y = escalador.ajustar_aplicar(s)
            filas.append({"estrategia": nombre, "propiedad": escalador.estrategia.propiedad,
                          "media": y.mean(), "desv": y.std(ddof=0), "mediana": y.median(),
                          "ric": y.quantile(0.75) - y.quantile(0.25),
                          "min": y.min(), "max": y.max(),
                          "cumple": escalador.verificar(y)})
        except ValueError as err:
            filas.append({"estrategia": nombre, "propiedad": str(err), "media": np.nan,
                          "desv": np.nan, "mediana": np.nan, "ric": np.nan,
                          "min": np.nan, "max": np.nan, "cumple": False})

    return pd.DataFrame(filas).set_index("estrategia").round(4)
