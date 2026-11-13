# MODI: potenciales, costos reducidos d_ij = c_ij - u_i - v_j y pivoteo hasta que todo d_ij >= 0.

from dataclasses import dataclass, field
from typing import Optional

from app.dominio.tipos import Celda, Matriz
from app.transporte.arbolBase import ArbolBase
from app.transporte.tabla import TablaTransporte


@dataclass
class InfoDual:
    u: list[float]                 # potencial de cada fila (incluida la ficticia)
    v: list[float]                 # potencial de cada columna
    d: Matriz                      # costos reducidos (0 en las básicas)
    basicas: set[Celda]
    x: Matriz                      # asignaciones de la tabla balanceada
    filaReferencia: int            # fila con u = 0 (la ficticia si existe)
    iteraciones: int = 0
    costoInicial: float = 0.0      # costo de la solución de Vogel
    historialCostos: list[float] = field(default_factory=list)


class MetodoMODI:
    def __init__(self, tolerancia: float = 1e-9, maxIteraciones: int = 10_000):
        self.tolerancia = tolerancia
        self.maxIteraciones = maxIteraciones

    def optimizar(self, tabla: TablaTransporte) -> InfoDual:
        inst = tabla.inst
        n, m = inst.n(), inst.m()
        # u = 0 en la fila ficticia: u_i y v_j quedan como precios sombra.
        filaReferencia = n - 1 if inst.ficticia == "fila" else 0
        costoInicial = tabla.costo()
        historial = [costoInicial]

        for iteracion in range(self.maxIteraciones + 1):
            arbol = ArbolBase(tabla.basicas, n, m)
            u, v = arbol.potenciales(inst.C, filaReferencia)
            d = self.costosReducidos(inst.C, u, v, tabla.basicas)
            entrante = self._celdaEntrante(d, tabla.basicas)
            if entrante is None:
                return InfoDual(u, v, d, set(tabla.basicas), [list(f) for f in tabla.x],
                                filaReferencia, iteracion, costoInicial, historial)
            self.pivotear(tabla, arbol.ciclo(entrante))
            historial.append(tabla.costo())

        raise RuntimeError("MODI no terminó: se alcanzó el máximo de iteraciones.")

    @staticmethod
    def costosReducidos(C: Matriz, u: list[float], v: list[float], basicas: set[Celda]) -> Matriz:
        return [
            [0.0 if (i, j) in basicas else C[i][j] - u[i] - v[j] for j in range(len(v))]
            for i in range(len(u))
        ]

    def _celdaEntrante(self, d: Matriz, basicas: set[Celda]) -> Optional[Celda]:
        mejor, celda = -self.tolerancia * max(1.0, max(abs(x) for fila in d for x in fila)), None
        for i, fila in enumerate(d):
            for j, valor in enumerate(fila):
                if (i, j) not in basicas and valor < mejor:
                    mejor, celda = valor, (i, j)
        return celda

    @staticmethod
    def pivotear(tabla: TablaTransporte, ciclo: list[tuple[Celda, int]]) -> None:
        """Mueve theta por el ciclo: entra la celda nueva y sale una con signo -."""
        negativas = [celda for celda, signo in ciclo if signo < 0]
        theta = min(tabla.x[i][j] for i, j in negativas)
        sale = min((c for c in negativas if tabla.x[c[0]][c[1]] == theta),
                   key=lambda c: (-tabla.inst.C[c[0]][c[1]], c))
        for (i, j), signo in ciclo:
            tabla.x[i][j] += signo * theta
        entrante = ciclo[0][0]
        tabla.basicas.add(entrante)
        tabla.basicas.discard(sale)
        tabla.x[sale[0]][sale[1]] = 0.0
