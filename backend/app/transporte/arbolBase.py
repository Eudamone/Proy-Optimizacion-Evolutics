"""ArbolBase: la base de la tabla vista como un árbol.

Los nodos son las filas ('u', i) y las columnas ('v', j); cada celda básica (i, j)
es una arista entre ('u', i) y ('v', j). Con n + m - 1 celdas básicas sin ciclos,
el grafo es un árbol: entre dos nodos hay exactamente un camino.

Lo usan MODI (potenciales y ciclo de la celda entrante) y el análisis de
sensibilidad (rangos de costos y de oferta/capacidad).
"""

from collections import deque

from app.dominio.tipos import Celda, Matriz, Nodo


class ArbolBase:
    def __init__(self, basicas: set[Celda], n: int, m: int):
        self.n, self.m = n, m
        self.adyacencia: dict[Nodo, list[Nodo]] = {("u", i): [] for i in range(n)}
        self.adyacencia.update({("v", j): [] for j in range(m)})
        for (i, j) in basicas:
            self.adyacencia[("u", i)].append(("v", j))
            self.adyacencia[("v", j)].append(("u", i))

    def potenciales(self, C: Matriz, filaReferencia: int = 0) -> tuple[list[float], list[float]]:
        """Resuelve u_i + v_j = c_ij en las celdas básicas con u[filaReferencia] = 0."""
        u: list = [None] * self.n
        v: list = [None] * self.m
        u[filaReferencia] = 0.0
        cola = deque([("u", filaReferencia)])
        while cola:
            tipo, k = cola.popleft()
            for vecino in self.adyacencia[(tipo, k)]:
                _, h = vecino
                if tipo == "u" and v[h] is None:
                    v[h] = C[k][h] - u[k]
                    cola.append(vecino)
                elif tipo == "v" and u[h] is None:
                    u[h] = C[h][k] - v[k]
                    cola.append(vecino)
        if any(val is None for val in u) or any(val is None for val in v):
            raise ValueError("La base no es un árbol conexo: falta completar la base.")
        return u, v

    def camino(self, origen: Nodo, destino: Nodo) -> list[Nodo]:
        """Nodos del único camino del árbol entre origen y destino (incluidos)."""
        anterior = {origen: None}
        cola = deque([origen])
        while cola:
            nodo = cola.popleft()
            if nodo == destino:
                break
            for vecino in self.adyacencia[nodo]:
                if vecino not in anterior:
                    anterior[vecino] = nodo
                    cola.append(vecino)
        if destino not in anterior:
            raise ValueError(f"No hay camino entre {origen} y {destino}.")
        nodos = [destino]
        while nodos[-1] != origen:
            nodos.append(anterior[nodos[-1]])
        return list(reversed(nodos))

    @staticmethod
    def celdasDelCamino(nodos: list[Nodo]) -> list[Celda]:
        """Convierte un camino de nodos en las celdas básicas que recorre."""
        celdas = []
        for a, b in zip(nodos, nodos[1:]):
            fila = a[1] if a[0] == "u" else b[1]
            columna = a[1] if a[0] == "v" else b[1]
            celdas.append((fila, columna))
        return celdas

    def ciclo(self, entrante: Celda) -> list[tuple[Celda, int]]:
        """Ciclo de la celda entrante con sus signos: [((i, j), +1), (celda, -1), ...].

        El ciclo es la celda entrante más el camino del árbol que une su columna con su fila.
        Los signos se alternan empezando con + en la celda entrante.
        """
        i, j = entrante
        celdas = self.celdasDelCamino(self.camino(("v", j), ("u", i)))
        ciclo = [(entrante, +1)]
        signo = -1
        for celda in celdas:
            ciclo.append((celda, signo))
            signo = -signo
        return ciclo
