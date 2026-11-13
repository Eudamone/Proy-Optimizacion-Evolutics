from abc import ABC, abstractmethod

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import Solucion


class ISolver(ABC):
    @abstractmethod
    def nombre(self) -> str:
        """Devuelve "exacto" o "genetico"."""

    @abstractmethod
    def resolver(self, inst: InstanciaTransporte) -> Solucion:
        """Devuelve los flujos x_ij en el tamaño original n x m."""
