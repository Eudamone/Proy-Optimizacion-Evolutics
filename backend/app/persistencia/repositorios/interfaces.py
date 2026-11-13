from abc import ABC, abstractmethod
from typing import Optional

from app.dominio.red import RedLogistica


class IRedRepository(ABC):
    @abstractmethod
    def obtenerRed(self) -> RedLogistica: ...

    @abstractmethod
    def guardar(self, red: RedLogistica) -> None: ...

    @abstractmethod
    def estaVacia(self) -> bool: ...


class IEjecucionRepository(ABC):
    @abstractmethod
    def guardarComparacion(self, comparacion, parametros, corridas: int, detalle: dict) -> int:
        """Guarda una comparación y devuelve su id."""

    @abstractmethod
    def listar(self, limite: int = 50) -> list[dict]: ...

    @abstractmethod
    def obtener(self, ejecucionId: int) -> Optional[dict]: ...
