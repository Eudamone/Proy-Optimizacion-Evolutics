from abc import ABC, abstractmethod

from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma


class ICruce(ABC):
    @abstractmethod
    def cruzar(self, a: Cromosoma, b: Cromosoma) -> tuple[Cromosoma, Cromosoma]:
        ...


class CruceUnPunto(ICruce):
    def __init__(self, rng: GeneradorAleatorio):
        self.rng = rng

    def cruzar(self, a: Cromosoma, b: Cromosoma) -> tuple[Cromosoma, Cromosoma]:
        largo = len(a.genes)
        if largo < 2:
            return a.copiar(), b.copiar()
        corte = self.rng.entero(1, largo - 1)
        return (
            Cromosoma(a.genes[:corte] + b.genes[corte:]),
            Cromosoma(b.genes[:corte] + a.genes[corte:]),
        )


class CruceDosPuntos(ICruce):
    def __init__(self, rng: GeneradorAleatorio):
        self.rng = rng

    def cruzar(self, a: Cromosoma, b: Cromosoma) -> tuple[Cromosoma, Cromosoma]:
        largo = len(a.genes)
        if largo < 3:
            return CruceUnPunto(self.rng).cruzar(a, b)
        p1, p2 = sorted(self.rng.muestra(list(range(1, largo)), 2))
        return (
            Cromosoma(a.genes[:p1] + b.genes[p1:p2] + a.genes[p2:]),
            Cromosoma(b.genes[:p1] + a.genes[p1:p2] + b.genes[p2:]),
        )
