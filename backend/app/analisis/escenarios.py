# Escenarios ¿qué pasa si...?: cambia un dato en varios pasos y vuelve a resolver en cada uno.

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.dominio.instancia import InstanciaTransporte
from app.motores.interfaces import ISolver


class TipoEscenario(Enum):
    COSTO_TRANSPORTE = "COSTO_TRANSPORTE"   # costo por tonelada de las rutas hacia una planta (o todas), en %
    OFERTA = "OFERTA"                       # oferta de una agroempresa (o todas), en %
    CAPACIDAD = "CAPACIDAD"                 # capacidad de una planta (o todas), en %
    CIERRE_PLANTA = "CIERRE_PLANTA"         # la planta objetivo queda con capacidad 0


# ---- modificadores (uno por tipo de escenario) ----

class IModificador(ABC):
    unPasoSolo = False      # True si el escenario no se recorre por porcentajes
    sobreFuentes = False    # True si el objetivo es una agroempresa (fila); si no, una planta (columna)

    @abstractmethod
    def aplicar(self, inst: InstanciaTransporte, indices: list[int], factor: float) -> None:
        ...


class ModificadorCostoTransporte(IModificador):
    def aplicar(self, inst, indices, factor):
        for i in range(inst.n()):
            for j in indices:
                if inst.C[i][j] < inst.gran_m:
                    inst.C[i][j] *= factor


class ModificadorOferta(IModificador):
    sobreFuentes = True

    def aplicar(self, inst, indices, factor):
        for i in indices:
            inst.a[i] *= factor


class ModificadorCapacidad(IModificador):
    def aplicar(self, inst, indices, factor):
        for j in indices:
            inst.b[j] *= factor


class ModificadorCierrePlanta(IModificador):
    unPasoSolo = True

    def aplicar(self, inst, indices, factor):
        for j in indices:
            inst.b[j] = 0.0


MODIFICADORES: dict[TipoEscenario, IModificador] = {
    TipoEscenario.COSTO_TRANSPORTE: ModificadorCostoTransporte(),
    TipoEscenario.OFERTA: ModificadorOferta(),
    TipoEscenario.CAPACIDAD: ModificadorCapacidad(),
    TipoEscenario.CIERRE_PLANTA: ModificadorCierrePlanta(),
}


@dataclass
class Escenario:
    tipo: TipoEscenario
    objetivo: Optional[int] = None   # índice de la fila o columna; None = todas
    delta_min: float = -20.0         # en %
    delta_max: float = 20.0          # en %
    pasos: int = 5

    @property
    def modificador(self) -> IModificador:
        return MODIFICADORES[self.tipo]

    def deltas(self) -> list[float]:
        if self.modificador.unPasoSolo:
            return [100.0]
        if self.pasos <= 1:
            return [self.delta_min]
        paso = (self.delta_max - self.delta_min) / (self.pasos - 1)
        return [round(self.delta_min + k * paso, 10) for k in range(self.pasos)]

    def aplicar(self, inst: InstanciaTransporte, delta: float) -> InstanciaTransporte:
        if self.modificador.unPasoSolo and self.objetivo is None:
            raise ValueError("Para este escenario hay que indicar a qué planta se aplica.")
        nueva = inst.conCambios()
        total = nueva.n() if self.modificador.sobreFuentes else nueva.m()
        indices = list(range(total)) if self.objetivo is None else [self.objetivo]
        self.modificador.aplicar(nueva, indices, 1 + delta / 100)
        return nueva


@dataclass
class PasoEscenario:
    delta: float
    costo_total: Optional[float]     # None si el escenario no es factible
    cambia_base: bool                # True si cambian las rutas en uso respecto a la base
    factible: bool = True
    mensaje: str = ""


class SimuladorEscenarios:
    def __init__(self, solver: ISolver):
        self.solver = solver

    def simular(self, inst: InstanciaTransporte, esc: Escenario) -> list[PasoEscenario]:
        rutasBase = self._rutasEnUso(self.solver.resolver(inst).x)
        pasos = []
        for delta in esc.deltas():
            modificada = esc.aplicar(inst, delta)
            try:
                sol = self.solver.resolver(modificada)
            except ValueError as error:
                pasos.append(PasoEscenario(delta, None, True, False, str(error)))
                continue
            pasos.append(PasoEscenario(delta, sol.costo_total, self._rutasEnUso(sol.x) != rutasBase))
        return pasos

    @staticmethod
    def _rutasEnUso(x) -> set[tuple[int, int]]:
        return {(i, j) for i, fila in enumerate(x) for j, valor in enumerate(fila) if valor > 1e-9}
