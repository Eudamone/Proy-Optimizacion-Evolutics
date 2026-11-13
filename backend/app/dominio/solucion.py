# SolucionExacta agrega los duales (para sensibilidad) y SolucionGenetica el historial.

from dataclasses import dataclass
from typing import Any

from app.dominio.tipos import Matriz


@dataclass
class Solucion:
    metodo: str                 # "exacto" o "genetico"
    x: Matriz                   # flujos x_ij en t/semana
    costo_total: float          # Z en $/semana
    tiempo_s: float             # tiempo de cómputo en segundos
    iteraciones: int = 0        # iteraciones MODI o generaciones del AG
    factible: bool = True

    def flujos(self, fuentes: list[str], plantas: list[str], minimo: float = 1e-9) -> list[tuple[str, str, float]]:
        rutas = [
            (fuentes[i], plantas[j], self.x[i][j])
            for i in range(len(fuentes))
            for j in range(len(plantas))
            if self.x[i][j] > minimo
        ]
        return sorted(rutas, key=lambda r: r[2], reverse=True)


@dataclass
class SolucionExacta(Solucion):
    dual: Any = None            # InfoDual (u, v, d_ij, base óptima); obligatorio

    def __post_init__(self):
        if self.dual is None:
            raise ValueError("Una SolucionExacta necesita la información dual del tablero óptimo.")


@dataclass
class SolucionGenetica(Solucion):
    historial: Any = None       # HistorialConvergencia
