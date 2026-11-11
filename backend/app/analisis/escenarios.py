"""Escenarios "¿qué pasa si...?": se cambia un dato en varios pasos y se vuelve a
resolver con el método exacto en cada uno.
"""

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


@dataclass
class Escenario:
    tipo: TipoEscenario
    objetivo: Optional[int] = None   # índice de la fila o columna; None = todas
    delta_min: float = -20.0         # en %
    delta_max: float = 20.0          # en %
    pasos: int = 5

    def deltas(self) -> list[float]:
        if self.tipo == TipoEscenario.CIERRE_PLANTA:
            return [100.0]
        if self.pasos <= 1:
            return [self.delta_min]
        paso = (self.delta_max - self.delta_min) / (self.pasos - 1)
        return [round(self.delta_min + k * paso, 10) for k in range(self.pasos)]

    def aplicar(self, inst: InstanciaTransporte, delta: float) -> InstanciaTransporte:
        """Copia de la instancia con el cambio aplicado (delta en %)."""
        factor = 1 + delta / 100
        nueva = inst.conCambios()
        if self.tipo == TipoEscenario.COSTO_TRANSPORTE:
            for i in range(nueva.n()):
                for j in self._indices(nueva.m()):
                    if nueva.C[i][j] < nueva.gran_m:
                        nueva.C[i][j] *= factor
        elif self.tipo == TipoEscenario.OFERTA:
            for i in self._indices(nueva.n()):
                nueva.a[i] *= factor
        elif self.tipo == TipoEscenario.CAPACIDAD:
            for j in self._indices(nueva.m()):
                nueva.b[j] *= factor
        elif self.tipo == TipoEscenario.CIERRE_PLANTA:
            if self.objetivo is None:
                raise ValueError("Para cerrar una planta hay que indicar cuál.")
            nueva.b[self.objetivo] = 0.0
        return nueva

    def _indices(self, total: int) -> list[int]:
        return list(range(total)) if self.objetivo is None else [self.objetivo]


@dataclass
class PasoEscenario:
    delta: float
    costo_total: Optional[float]     # None si el escenario no es factible
    cambia_base: bool                # True si cambian las rutas en uso respecto a la base
    factible: bool = True
    mensaje: str = ""


class SimuladorEscenarios:
    def __init__(self, solver: ISolver = None):
        if solver is None:
            from app.transporte.solverTransporte import SolverTransporte
            solver = SolverTransporte()
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
