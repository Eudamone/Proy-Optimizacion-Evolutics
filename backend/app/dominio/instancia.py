# c_ij = d_ij * tarifa + costo de operación; ruta bloqueada = Gran M, planta inactiva = b_j 0.

from dataclasses import dataclass, field, replace
from typing import Optional

from app.dominio.red import RedLogistica
from app.dominio.tipos import Matriz, copiarMatriz


@dataclass
class InstanciaTransporte:
    fuentes: list[str]
    plantas: list[str]
    a: list[float]
    b: list[float]
    C: Matriz
    gran_m: float = 1e8
    ficticia: Optional[str] = None  # "fila" o "columna" si el balanceador agregó una

    def n(self) -> int:
        return len(self.fuentes)

    def m(self) -> int:
        return len(self.plantas)

    def costo(self, x: Matriz) -> float:
        return sum(self.C[i][j] * x[i][j] for i in range(self.n()) for j in range(self.m()))

    def verificar(self, x: Matriz, tolerancia: float = 1e-6) -> list[str]:
        """Revisa que x cumpla las restricciones; lista vacía = factible."""
        if len(x) != self.n() or any(len(fila) != self.m() for fila in x):
            return [f"La matriz x debe ser de {self.n()} x {self.m()}."]

        errores = []
        for i in range(self.n()):
            for j in range(self.m()):
                if x[i][j] < -tolerancia:
                    errores.append(f"x[{self.fuentes[i]}][{self.plantas[j]}] es negativo.")
                if x[i][j] > tolerancia and self.C[i][j] >= self.gran_m:
                    errores.append(f"Se usa la ruta bloqueada {self.fuentes[i]} -> {self.plantas[j]}.")

        for i in range(self.n()):
            enviado = sum(x[i])
            if abs(enviado - self.a[i]) > tolerancia:
                errores.append(
                    f"{self.fuentes[i]} despacha {enviado:g} t y debe despachar {self.a[i]:g} t."
                )
        for j in range(self.m()):
            recibido = sum(x[i][j] for i in range(self.n()))
            if recibido > self.b[j] + tolerancia:
                errores.append(
                    f"{self.plantas[j]} recibe {recibido:g} t y su capacidad es {self.b[j]:g} t."
                )
        return errores

    def conCambios(self, **cambios) -> "InstanciaTransporte":
        copia = replace(
            self,
            fuentes=list(self.fuentes),
            plantas=list(self.plantas),
            a=list(self.a),
            b=list(self.b),
            C=copiarMatriz(self.C),
        )
        return replace(copia, **cambios) if cambios else copia


class InstanciaBuilder:
    def construir(self, red: RedLogistica) -> InstanciaTransporte:
        if red.parametros.tarifa_t_km is None:
            raise ValueError("Falta definir la tarifa de transporte para calcular los costos.")
        return InstanciaTransporte(
            fuentes=[a.id for a in red.agroempresas],
            plantas=[p.id for p in red.plantas],
            a=[float(a.oferta_t) for a in red.agroempresas],
            b=[float(p.capacidad_t) if p.activa else 0.0 for p in red.plantas],
            C=self._matrizCostos(red),
            gran_m=red.parametros.gran_m,
        )

    def _matrizCostos(self, red: RedLogistica) -> Matriz:
        tarifa = red.parametros.tarifa_t_km
        granM = red.parametros.gran_m
        C = []
        for a in red.agroempresas:
            fila = []
            for p in red.plantas:
                ruta = red.ruta(a.id, p.id)
                if ruta.habilitada:
                    fila.append(ruta.distancia_km * tarifa + p.costo_operacion)
                else:
                    fila.append(granM)
            C.append(fila)
        return C
