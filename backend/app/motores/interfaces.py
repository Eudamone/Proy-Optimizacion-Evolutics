"""ISolver: contrato común del método exacto y del algoritmo genético (patrón Strategy)."""

from abc import ABC, abstractmethod

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import Solucion


class ISolver(ABC):
    @abstractmethod
    def nombre(self) -> str:
        """Nombre corto del método: "exacto" o "genetico"."""

    @abstractmethod
    def resolver(self, inst: InstanciaTransporte) -> Solucion:
        """Resuelve la instancia y devuelve los flujos x_ij en el tamaño original n x m."""
