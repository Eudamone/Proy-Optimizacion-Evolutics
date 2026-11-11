"""ParametrosAG: configuración del algoritmo genético."""

from dataclasses import dataclass
from typing import Optional

SELECCIONES = ("torneo", "ruleta")
CRUCES = ("un_punto", "dos_puntos")
MUTACIONES = ("uniforme", "poda")


@dataclass
class ParametrosAG:
    poblacion: int = 100
    generaciones: int = 300
    p_cruce: float = 0.8
    p_mutacion: float = 0.05
    elitismo: int = 2
    k_torneo: int = 3
    lambda_: Optional[float] = None   # penalización por tonelada sobre la capacidad; None = automática
    seleccion: str = "torneo"
    cruce: str = "un_punto"
    mutacion: str = "poda"
    semilla: Optional[int] = None

    def validar(self) -> list[str]:
        errores = []
        if self.poblacion < 2:
            errores.append("La población debe tener al menos 2 individuos.")
        if self.generaciones < 1:
            errores.append("Debe haber al menos 1 generación.")
        if not 0 <= self.p_cruce <= 1:
            errores.append("La probabilidad de cruce debe estar entre 0 y 1.")
        if not 0 <= self.p_mutacion <= 1:
            errores.append("La probabilidad de mutación debe estar entre 0 y 1.")
        if not 0 <= self.elitismo < self.poblacion:
            errores.append("El elitismo debe ser menor que el tamaño de la población.")
        if not 1 <= self.k_torneo <= self.poblacion:
            errores.append("El tamaño del torneo debe estar entre 1 y el tamaño de la población.")
        if self.lambda_ is not None and self.lambda_ <= 0:
            errores.append("La penalización lambda debe ser mayor que 0.")
        if self.seleccion not in SELECCIONES:
            errores.append(f"Selección desconocida: {self.seleccion}. Use {', '.join(SELECCIONES)}.")
        if self.cruce not in CRUCES:
            errores.append(f"Cruce desconocido: {self.cruce}. Use {', '.join(CRUCES)}.")
        if self.mutacion not in MUTACIONES:
            errores.append(f"Mutación desconocida: {self.mutacion}. Use {', '.join(MUTACIONES)}.")
        return errores
