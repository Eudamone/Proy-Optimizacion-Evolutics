import random
from typing import Optional


class GeneradorAleatorio:
    def __init__(self, semilla: Optional[int] = None):
        self.semilla = semilla
        self._rng = random.Random(semilla)

    def uniforme(self) -> float:
        return self._rng.random()

    def entero(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def muestra(self, items: list, k: int) -> list:
        return self._rng.sample(items, k)
