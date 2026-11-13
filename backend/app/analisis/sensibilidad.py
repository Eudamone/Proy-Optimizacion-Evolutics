# Precios sombra, costos reducidos y rangos leídos del tablero óptimo de MODI, sin volver a resolver.

import math
from dataclasses import dataclass, field

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import SolucionExacta
from app.dominio.tipos import Celda, Matriz
from app.transporte.arbolBase import ArbolBase
from app.transporte.modi import InfoDual


@dataclass
class Rango:
    actual: float
    minimo: float
    maximo: float

    def contiene(self, valor: float) -> bool:
        return self.minimo - 1e-9 <= valor <= self.maximo + 1e-9


@dataclass
class ResultadoSensibilidad:
    precio_sombra_oferta: list[float]       # u_i por agroempresa
    precio_sombra_capacidad: list[float]    # v_j por planta (<= 0)
    costos_reducidos: Matriz                # d_ij sin la fila ficticia
    rangos_costo: dict[Celda, Rango] = field(default_factory=dict)
    rangos_oferta: list[Rango] = field(default_factory=list)
    rangos_capacidad: list[Rango] = field(default_factory=list)

    def ahorroPorCapacidad(self) -> list[float]:
        return [-v if v != 0 else 0.0 for v in self.precio_sombra_capacidad]


class AnalizadorSensibilidad:
    def analizar(self, sol: SolucionExacta, inst: InstanciaTransporte) -> ResultadoSensibilidad:
        if not isinstance(sol, SolucionExacta):
            raise ValueError("La sensibilidad necesita la solución del método exacto (SolucionExacta).")
        dual: InfoDual = sol.dual
        n, m = inst.n(), inst.m()
        hayFicticia = len(dual.u) > n
        arbol = ArbolBase(dual.basicas, len(dual.u), m)

        resultado = ResultadoSensibilidad(
            precio_sombra_oferta=list(dual.u[:n]),
            precio_sombra_capacidad=list(dual.v),
            costos_reducidos=[list(fila) for fila in dual.d[:n]],
        )
        ciclos = self._ciclosNoBasicas(dual, arbol)
        for i in range(n):
            for j in range(m):
                resultado.rangos_costo[(i, j)] = self._rangoCosto(dual, inst, ciclos, (i, j))
        if hayFicticia:
            resultado.rangos_oferta = [self._rangoOferta(dual, arbol, inst, i) for i in range(n)]
            resultado.rangos_capacidad = [self._rangoCapacidad(dual, arbol, inst, j) for j in range(m)]
        return resultado

    # ---- costos ----

    @staticmethod
    def _ciclosNoBasicas(dual: InfoDual, arbol: ArbolBase) -> dict[Celda, list[tuple[Celda, int]]]:
        return {
            (k, l): arbol.ciclo((k, l))
            for k in range(len(dual.u))
            for l in range(len(dual.v))
            if (k, l) not in dual.basicas
        }

    def _rangoCosto(self, dual: InfoDual, inst: InstanciaTransporte, ciclos, celda: Celda) -> Rango:
        i, j = celda
        actual = inst.C[i][j]
        if celda not in dual.basicas:
            # No básica: entra a la base si su costo baja más de d_ij.
            return Rango(actual, actual - dual.d[i][j], math.inf)

        # Básica: todo d_kl cuyo ciclo pasa por (i, j) cambia en signo * delta y debe seguir >= 0.
        bajada, subida = -math.inf, math.inf
        for (k, l), ciclo in ciclos.items():
            for celdaCiclo, signo in ciclo[1:]:
                if celdaCiclo == celda:
                    if signo > 0:
                        bajada = max(bajada, -dual.d[k][l])
                    else:
                        subida = min(subida, dual.d[k][l])
        return Rango(actual, actual + bajada, actual + subida)

    # ---- oferta y capacidad ----

    @staticmethod
    def _limitesPorCamino(dual: InfoDual, celdas: list[Celda]) -> tuple[float, float]:
        """El flujo extra recorre el camino alternando +delta y -delta; ningún x puede quedar < 0."""
        abajo, arriba = -math.inf, math.inf
        signo = +1
        for i, j in celdas:
            x = dual.x[i][j]
            if signo > 0:
                abajo = max(abajo, -x)
            else:
                arriba = min(arriba, x)
            signo = -signo
        return abajo, arriba

    def _rangoOferta(self, dual: InfoDual, arbol: ArbolBase, inst: InstanciaTransporte, i: int) -> Rango:
        # La agroempresa i entrega delta más y la fuente ficticia delta menos.
        celdas = arbol.celdasDelCamino(arbol.camino(("u", i), ("u", dual.filaReferencia)))
        abajo, arriba = self._limitesPorCamino(dual, celdas)
        actual = inst.a[i]
        return Rango(actual, max(0.0, actual + abajo), actual + arriba)

    def _rangoCapacidad(self, dual: InfoDual, arbol: ArbolBase, inst: InstanciaTransporte, j: int) -> Rango:
        # La planta j recibe delta más de capacidad y la fuente ficticia la "llena".
        celdas = arbol.celdasDelCamino(arbol.camino(("u", dual.filaReferencia), ("v", j)))
        abajo, arriba = self._limitesPorCamino(dual, celdas)
        actual = inst.b[j]
        return Rango(actual, max(0.0, actual + abajo), actual + arriba)
