"""SolverFactory: único lugar que conoce las clases concretas de los métodos.

Cada método se registra con un creador; para agregar uno nuevo se registra
sin modificar la fábrica (registrar("otro", creador)).
"""

from typing import Callable, Optional

from app.motores.interfaces import ISolver


def _crearExacto(parametros=None) -> ISolver:
    from app.transporte.solverTransporte import SolverTransporte
    return SolverTransporte()


def _crearGenetico(parametros=None) -> ISolver:
    from app.genetico.aleatorio import GeneradorAleatorio
    from app.genetico.operadores import crearCruce, crearMutacion, crearSeleccion
    from app.genetico.parametros import ParametrosAG
    from app.genetico.solverGenetico import AlgoritmoGeneticoSolver

    p = parametros or ParametrosAG()
    errores = p.validar()
    if errores:
        raise ValueError(" ".join(errores))
    rng = GeneradorAleatorio(p.semilla)
    return AlgoritmoGeneticoSolver(
        p, rng=rng,
        seleccion=crearSeleccion(p.seleccion, rng, p),
        cruce=crearCruce(p.cruce, rng, p),
        mutacion=crearMutacion(p.mutacion, rng, p),
    )


class SolverFactory:
    def __init__(self):
        self._creadores: dict[str, Callable[..., ISolver]] = {
            "exacto": _crearExacto,
            "genetico": _crearGenetico,
        }

    def registrar(self, metodo: str, creador: Callable[..., ISolver]) -> None:
        self._creadores[metodo] = creador

    def metodos(self) -> list[str]:
        return list(self._creadores)

    def crear(self, metodo: str, parametros=None) -> ISolver:
        if metodo not in self._creadores:
            raise ValueError(f"Método desconocido: {metodo}. Use {' o '.join(self._creadores)}.")
        return self._creadores[metodo](parametros)

    def exacto(self) -> ISolver:
        return self.crear("exacto")

    def genetico(self, parametros: Optional[object] = None) -> ISolver:
        return self.crear("genetico", parametros)
