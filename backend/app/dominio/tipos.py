"""Tipos comunes del dominio y de los modelos de optimización."""

from enum import Enum

Matriz = list[list[float]]
"""Matriz de n filas (fuentes) por m columnas (plantas)."""

Celda = tuple[int, int]
"""Posición (i, j) de una celda en la tabla de transporte."""

Nodo = tuple[str, int]
"""Nodo del árbol de la base: ('u', i) para una fila o ('v', j) para una columna."""


class TipoResiduo(Enum):
    """Origen del residuo agropecuario que entrega cada agroempresa."""

    PALMA = "PALMA"
    ARROZ = "ARROZ"
    GANADERIA = "GANADERIA"   # pecuario: avícola, porcícola, lácteos, bovino
    AGRICOLA = "AGRICOLA"     # frutales y otros cultivos (cítricos, cacao)
    FORESTAL = "FORESTAL"


def matrizCeros(n: int, m: int) -> Matriz:
    """Devuelve una matriz n x m llena de ceros."""
    return [[0.0] * m for _ in range(n)]


def copiarMatriz(matriz: Matriz) -> Matriz:
    """Copia independiente de una matriz (las filas no se comparten)."""
    return [list(fila) for fila in matriz]
