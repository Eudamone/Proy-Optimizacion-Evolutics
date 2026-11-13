# aptitud = 1 / (1 + Z + lambda * exceso); por defecto lambda = 2 x el costo por tonelada más alto.

from typing import Optional

from app.dominio.instancia import InstanciaTransporte
from app.genetico.cromosoma import Cromosoma
from app.genetico.decodificador import Decodificador


class FitnessPenalizado:
    def __init__(self, decodificador: Decodificador, lambda_: Optional[float] = None):
        self.decodificador = decodificador
        self.lambda_ = lambda_

    def lambdaPara(self, inst: InstanciaTransporte) -> float:
        if self.lambda_ is not None:
            return self.lambda_
        costos = [c for fila in inst.C for c in fila if c < inst.gran_m]
        return 2 * max(costos) if costos else 1.0

    def evaluar(self, c: Cromosoma, inst: InstanciaTransporte) -> float:
        x = self.decodificador.decodificar(c, inst)
        c.costo = inst.costo(x)
        c.exceso = self.decodificador.exceso(x, inst)
        c.aptitud = 1.0 / (1.0 + c.penalizado(self.lambdaPara(inst)))
        return c.aptitud
