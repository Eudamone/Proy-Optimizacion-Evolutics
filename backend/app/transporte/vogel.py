# Vogel: asigna en la celda más barata de la línea con mayor penalización.

from abc import ABC, abstractmethod

from app.dominio.instancia import InstanciaTransporte
from app.transporte.tabla import TablaTransporte


class ISolucionInicial(ABC):
    @abstractmethod
    def construir(self, inst: InstanciaTransporte) -> TablaTransporte:
        ...


class MetodoVogel(ISolucionInicial):
    def __init__(self, tolerancia: float = 1e-9):
        self.tolerancia = tolerancia

    def construir(self, inst: InstanciaTransporte) -> TablaTransporte:
        tabla = TablaTransporte(inst)
        oferta = list(inst.a)
        demanda = list(inst.b)
        filas = set(range(inst.n()))
        columnas = set(range(inst.m()))

        while filas and columnas:
            penFilas, penColumnas = self.penalizaciones(inst, filas, columnas)
            i, j = self._elegirCelda(inst, filas, columnas, penFilas, penColumnas)

            cantidad = min(oferta[i], demanda[j])
            tabla.asignar(i, j, cantidad)
            oferta[i] -= cantidad
            demanda[j] -= cantidad

            # Si se agotan fila y columna a la vez solo se tacha una (degeneración).
            if oferta[i] <= self.tolerancia and (demanda[j] > self.tolerancia or len(filas) > 1):
                filas.discard(i)
            else:
                columnas.discard(j)

        tabla.completarBase()
        return tabla

    def penalizaciones(self, inst, filas, columnas) -> tuple[dict, dict]:
        """Segundo costo más bajo - costo más bajo de cada línea activa."""
        penFilas = {i: self._diferencia([inst.C[i][j] for j in columnas]) for i in filas}
        penColumnas = {j: self._diferencia([inst.C[i][j] for i in filas]) for j in columnas}
        return penFilas, penColumnas

    @staticmethod
    def _diferencia(costos: list[float]) -> float:
        if len(costos) == 1:
            return costos[0]
        menores = sorted(costos)[:2]
        return menores[1] - menores[0]

    @staticmethod
    def _elegirCelda(inst, filas, columnas, penFilas, penColumnas) -> tuple[int, int]:
        # Mayor penalización; en empate, la línea cuyo costo mínimo sea menor.
        candidatos = []
        for i, pen in penFilas.items():
            j = min(columnas, key=lambda c: (inst.C[i][c], c))
            candidatos.append((-pen, inst.C[i][j], 0, i, i, j))
        for j, pen in penColumnas.items():
            i = min(filas, key=lambda f: (inst.C[f][j], f))
            candidatos.append((-pen, inst.C[i][j], 1, j, i, j))
        _, _, _, _, i, j = min(candidatos)
        return i, j
