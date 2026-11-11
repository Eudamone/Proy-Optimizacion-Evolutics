"""GeneradorAleatorio: envuelve random.Random(semilla) para que las corridas se puedan repetir.

Con la misma semilla y los mismos parámetros, el AG da exactamente el mismo resultado.
"""

import random
from typing import Optional


class GeneradorAleatorio:
    def __init__(self, semilla: Optional[int] = None):
        self.semilla = semilla
        self._rng = random.Random(semilla)

    def uniforme(self) -> float:
        """Número real en [0, 1)."""
        return self._rng.random()

    def entero(self, a: int, b: int) -> int:
        """Entero en [a, b], ambos incluidos."""
        return self._rng.randint(a, b)

    def muestra(self, items: list, k: int) -> list:
        """k elementos distintos al azar."""
        return self._rng.sample(items, k)
