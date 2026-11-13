from app.dominio.instancia import InstanciaTransporte
from app.dominio.tipos import Celda, matrizCeros


class TablaTransporte:
    def __init__(self, inst: InstanciaTransporte):
        self.inst = inst
        self.x = matrizCeros(inst.n(), inst.m())
        self.basicas: set[Celda] = set()

    def asignar(self, i: int, j: int, cantidad: float) -> None:
        self.x[i][j] = cantidad
        self.basicas.add((i, j))

    def costo(self) -> float:
        return self.inst.costo(self.x)

    def numeroBasicasRequeridas(self) -> int:
        return self.inst.n() + self.inst.m() - 1

    def completarBase(self) -> None:
        """Con degeneración agrega básicas en 0 (las más baratas) hasta tener n + m - 1."""
        n, m = self.inst.n(), self.inst.m()
        padre = list(range(n + m))  # nodos 0..n-1 = filas, n..n+m-1 = columnas

        def raiz(k: int) -> int:
            while padre[k] != k:
                padre[k] = padre[padre[k]]
                k = padre[k]
            return k

        def unir(i: int, j: int) -> bool:
            ri, rj = raiz(i), raiz(n + j)
            if ri == rj:
                return False
            padre[ri] = rj
            return True

        for (i, j) in sorted(self.basicas):
            unir(i, j)

        if len(self.basicas) >= self.numeroBasicasRequeridas():
            return

        candidatas = sorted(
            ((self.inst.C[i][j], i, j) for i in range(n) for j in range(m) if (i, j) not in self.basicas)
        )
        for _, i, j in candidatas:
            if len(self.basicas) == self.numeroBasicasRequeridas():
                break
            if unir(i, j):
                self.basicas.add((i, j))  # básica con x_ij = 0
