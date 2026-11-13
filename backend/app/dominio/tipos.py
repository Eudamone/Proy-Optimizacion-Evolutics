from enum import Enum

Matriz = list[list[float]]
"""Matriz de n filas (fuentes) por m columnas (plantas)."""

Celda = tuple[int, int]
"""Posición (i, j) de una celda en la tabla de transporte."""

Nodo = tuple[str, int]
"""Nodo del árbol de la base: ('u', i) para una fila o ('v', j) para una columna."""


class TipoResiduo(Enum):
    PALMA = "PALMA"
    ARROZ = "ARROZ"
    GANADERIA = "GANADERIA"   # pecuario: avícola, porcícola, lácteos, bovino
    AGRICOLA = "AGRICOLA"     # frutales y otros cultivos (cítricos, cacao)
    FORESTAL = "FORESTAL"


def matrizCeros(n: int, m: int) -> Matriz:
    return [[0.0] * m for _ in range(n)]


def copiarMatriz(matriz: Matriz) -> Matriz:
    return [list(fila) for fila in matriz]
