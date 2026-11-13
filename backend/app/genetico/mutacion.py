from abc import ABC, abstractmethod

from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma


class IMutacion(ABC):
    @abstractmethod
    def mutar(self, c: Cromosoma) -> None:
        ...


class MutacionUniforme(IMutacion):
    def __init__(self, rng: GeneradorAleatorio, prob: float):
        self.rng = rng
        self.prob = prob

    def mutar(self, c: Cromosoma) -> None:
        for k in range(len(c.genes)):
            if self.rng.uniforme() < self.prob:
                c.genes[k] = self.rng.uniforme()


class MutacionPoda(IMutacion):
    """Con probabilidad p el gen pasa a 0 (cierra la ruta) la mitad de las veces; si no, toma un valor al azar."""

    def __init__(self, rng: GeneradorAleatorio, prob: float):
        self.rng = rng
        self.prob = prob

    def mutar(self, c: Cromosoma) -> None:
        for k in range(len(c.genes)):
            if self.rng.uniforme() < self.prob:
                c.genes[k] = 0.0 if self.rng.uniforme() < 0.5 else self.rng.uniforme()
