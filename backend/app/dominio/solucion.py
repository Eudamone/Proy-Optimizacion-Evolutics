"""Solucion: resultado de cualquier método (exacto o genético) sobre una instancia."""

from dataclasses import dataclass
from typing import Any, Optional

from app.dominio.tipos import Matriz


@dataclass
class Solucion:
    metodo: str                 # "exacto" o "genetico"
    x: Matriz                   # flujos x_ij en t/semana
    costo_total: float          # Z en $/semana
    tiempo_s: float             # tiempo de cómputo en segundos
    iteraciones: int = 0        # iteraciones MODI o generaciones del AG
    factible: bool = True
    dual: Optional[Any] = None  # InfoDual (u, v, d_ij) cuando la produce el método exacto
    historial: Optional[Any] = None  # HistorialConvergencia cuando la produce el AG

    def flujos(self, fuentes: list[str], plantas: list[str], minimo: float = 1e-9) -> list[tuple[str, str, float]]:
        """Rutas usadas como (fuente, planta, toneladas), de mayor a menor."""
        rutas = [
            (fuentes[i], plantas[j], self.x[i][j])
            for i in range(len(fuentes))
            for j in range(len(plantas))
            if self.x[i][j] > minimo
        ]
        return sorted(rutas, key=lambda r: r[2], reverse=True)
