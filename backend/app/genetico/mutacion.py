"""IMutacion, MutacionUniforme y MutacionPoda."""

from abc import ABC, abstractmethod

from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma


class IMutacion(ABC):
    @abstractmethod
    def mutar(self, c: Cromosoma) -> None:
        """Modifica los genes del cromosoma en el mismo objeto."""


class MutacionUniforme(IMutacion):
    """Cada gen, con probabilidad p, se reemplaza por un valor al azar en [0, 1]."""

    def __init__(self, rng: GeneradorAleatorio, prob: float):
        self.rng = rng
        self.prob = prob

    def mutar(self, c: Cromosoma) -> None:
        for k in range(len(c.genes)):
            if self.rng.uniforme() < self.prob:
                c.genes[k] = self.rng.uniforme()


class MutacionPoda(IMutacion):
    """Cada gen, con probabilidad p, se poda a 0 (mitad de las veces) o toma un valor al azar.

    Podar cierra rutas: así aparecen repartos que usan pocas rutas, como las
    soluciones óptimas del modelo de transporte.
    """

    def __init__(self, rng: GeneradorAleatorio, prob: float):
        self.rng = rng
        self.prob = prob

    def mutar(self, c: Cromosoma) -> None:
        for k in range(len(c.genes)):
            if self.rng.uniforme() < self.prob:
                c.genes[k] = 0.0 if self.rng.uniforme() < 0.5 else self.rng.uniforme()
