from abc import ABC, abstractmethod

from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma, Poblacion


class ISeleccion(ABC):
    @abstractmethod
    def seleccionar(self, pob: Poblacion) -> Cromosoma:
        """Devuelve el mismo objeto; quien lo use debe copiarlo."""


class SeleccionTorneo(ISeleccion):
    def __init__(self, rng: GeneradorAleatorio, k: int = 3):
        self.rng = rng
        self.k = k

    def seleccionar(self, pob: Poblacion) -> Cromosoma:
        participantes = self.rng.muestra(pob.individuos, min(self.k, len(pob)))
        return max(participantes, key=lambda c: c.aptitud)


class SeleccionRuleta(ISeleccion):
    def __init__(self, rng: GeneradorAleatorio):
        self.rng = rng

    def seleccionar(self, pob: Poblacion) -> Cromosoma:
        total = sum(c.aptitud for c in pob.individuos)
        objetivo = self.rng.uniforme() * total
        acumulado = 0.0
        for c in pob.individuos:
            acumulado += c.aptitud
            if acumulado >= objetivo:
                return c
        return pob.individuos[-1]
