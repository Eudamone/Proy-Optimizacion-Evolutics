"""Registro de operadores del AG.

Para agregar un operador nuevo basta con crear su clase y registrarla aquí;
ni el solver ni los parámetros cambian.
"""

from typing import Callable

from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cruce import CruceDosPuntos, CruceUnPunto, ICruce
from app.genetico.mutacion import IMutacion, MutacionPoda, MutacionUniforme
from app.genetico.seleccion import ISeleccion, SeleccionRuleta, SeleccionTorneo

# Cada creador recibe el generador aleatorio y los parámetros del AG.
SELECCIONES: dict[str, Callable[..., ISeleccion]] = {
    "torneo": lambda rng, p: SeleccionTorneo(rng, p.k_torneo),
    "ruleta": lambda rng, p: SeleccionRuleta(rng),
}
CRUCES: dict[str, Callable[..., ICruce]] = {
    "un_punto": lambda rng, p: CruceUnPunto(rng),
    "dos_puntos": lambda rng, p: CruceDosPuntos(rng),
}
MUTACIONES: dict[str, Callable[..., IMutacion]] = {
    "uniforme": lambda rng, p: MutacionUniforme(rng, p.p_mutacion),
    "poda": lambda rng, p: MutacionPoda(rng, p.p_mutacion),
}


def crearSeleccion(nombre: str, rng: GeneradorAleatorio, params) -> ISeleccion:
    return SELECCIONES[nombre](rng, params)


def crearCruce(nombre: str, rng: GeneradorAleatorio, params) -> ICruce:
    return CRUCES[nombre](rng, params)


def crearMutacion(nombre: str, rng: GeneradorAleatorio, params) -> IMutacion:
    return MUTACIONES[nombre](rng, params)
