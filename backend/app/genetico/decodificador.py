# Genes a toneladas: x_ij = a_i * g_ij / sum_k g_ik, así cada agroempresa despacha toda su oferta.

from app.dominio.instancia import InstanciaTransporte
from app.dominio.tipos import Matriz
from app.genetico.cromosoma import Cromosoma


class Decodificador:
    def decodificar(self, c: Cromosoma, inst: InstanciaTransporte) -> Matriz:
        n, m = inst.n(), inst.m()
        x = []
        for i in range(n):
            permitidas = [self._permitida(inst, i, j) for j in range(m)]
            pesos = [c.genes[i * m + j] if permitidas[j] else 0.0 for j in range(m)]
            total = sum(pesos)
            if total <= 0:  # todos los genes en 0: reparto parejo entre las rutas permitidas
                pesos = [1.0 if p else 0.0 for p in permitidas]
                total = sum(pesos)
            if total <= 0:
                raise ValueError(f"{inst.fuentes[i]} no tiene ninguna ruta permitida.")
            x.append([inst.a[i] * p / total for p in pesos])
        return x

    @staticmethod
    def _permitida(inst: InstanciaTransporte, i: int, j: int) -> bool:
        return inst.C[i][j] < inst.gran_m and inst.b[j] > 0

    @staticmethod
    def exceso(x: Matriz, inst: InstanciaTransporte) -> float:
        return sum(
            max(0.0, sum(x[i][j] for i in range(inst.n())) - inst.b[j])
            for j in range(inst.m())
        )
