# Exacto una vez contra varias corridas del AG; gap % = (Z_AG - Z*) / Z* * 100.

import statistics
from dataclasses import dataclass, field, replace

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import Solucion
from app.genetico.parametros import ParametrosAG
from app.motores.fabrica import SolverFactory


@dataclass
class Comparacion:
    z_exacto: float
    z_ag_mejor: float
    z_ag_promedio: float
    desv_estandar: float
    tiempos: dict[str, float]
    costos_ag: list[float] = field(default_factory=list)
    semillas: list[int] = field(default_factory=list)
    solucion_exacta: Solucion = None
    mejor_genetica: Solucion = None

    def gapPct(self) -> float:
        return self._gap(self.z_ag_mejor)

    def gapPromedioPct(self) -> float:
        return self._gap(self.z_ag_promedio)

    def gapsPorCorrida(self) -> list[float]:
        return [self._gap(z) for z in self.costos_ag]

    def _gap(self, z: float) -> float:
        if self.z_exacto == 0:
            return 0.0
        return (z - self.z_exacto) / self.z_exacto * 100


class Comparador:
    def __init__(self, fabrica: SolverFactory = None):
        self.fabrica = fabrica or SolverFactory()

    def comparar(self, inst: InstanciaTransporte, p: ParametrosAG = None, corridas: int = 10) -> Comparacion:
        if corridas < 1:
            raise ValueError("Debe haber al menos una corrida del AG.")
        p = p or ParametrosAG()
        semillaBase = p.semilla if p.semilla is not None else 0

        exacta = self.fabrica.exacto().resolver(inst)

        soluciones = []
        semillas = []
        for k in range(corridas):
            semilla = semillaBase + k
            solver = self.fabrica.genetico(replace(p, semilla=semilla))
            soluciones.append(solver.resolver(inst))
            semillas.append(semilla)

        costos = [s.costo_total for s in soluciones]
        mejor = min(soluciones, key=lambda s: s.costo_total)
        return Comparacion(
            z_exacto=exacta.costo_total,
            z_ag_mejor=mejor.costo_total,
            z_ag_promedio=statistics.mean(costos),
            desv_estandar=statistics.pstdev(costos),
            tiempos={
                "exacto": exacta.tiempo_s,
                "genetico_promedio": statistics.mean(s.tiempo_s for s in soluciones),
            },
            costos_ag=costos,
            semillas=semillas,
            solucion_exacta=exacta,
            mejor_genetica=mejor,
        )
