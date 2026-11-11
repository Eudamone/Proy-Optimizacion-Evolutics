"""AlgoritmoGeneticoSolver (implementa ISolver).

1. Población inicial: genes al azar en [0, 1], la mitad en 0 (repartos con pocas rutas).
2. Cada generación: pasan los `elitismo` mejores sin cambios; el resto nace de
   selección -> cruce (con probabilidad p_cruce) -> mutación.
3. Al final se decodifica el mejor individuo y se arma la SolucionGenetica.

Los operadores se reciben ya creados (la fábrica los arma); si no llegan, se
crean desde el registro de operadores según los parámetros.
"""

import time
from typing import Optional

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import SolucionGenetica
from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma, Poblacion
from app.genetico.cruce import ICruce
from app.genetico.decodificador import Decodificador
from app.genetico.fitness import FitnessPenalizado
from app.genetico.historial import HistorialConvergencia
from app.genetico.mutacion import IMutacion
from app.genetico.operadores import crearCruce, crearMutacion, crearSeleccion
from app.genetico.parametros import ParametrosAG
from app.genetico.seleccion import ISeleccion
from app.motores.interfaces import ISolver

DENSIDAD_INICIAL = 0.5  # probabilidad de que un gen inicial sea distinto de 0


class AlgoritmoGeneticoSolver(ISolver):
    def __init__(self, params: ParametrosAG = None, rng: Optional[GeneradorAleatorio] = None,
                 seleccion: Optional[ISeleccion] = None, cruce: Optional[ICruce] = None,
                 mutacion: Optional[IMutacion] = None, decodificador: Optional[Decodificador] = None,
                 fitness: Optional[FitnessPenalizado] = None):
        self.params = params or ParametrosAG()
        errores = self.params.validar()
        if errores:
            raise ValueError(" ".join(errores))
        self.rng = rng or GeneradorAleatorio(self.params.semilla)
        self.decodificador = decodificador or Decodificador()
        self.fitness = fitness or FitnessPenalizado(self.decodificador, self.params.lambda_)
        self.seleccion = seleccion or crearSeleccion(self.params.seleccion, self.rng, self.params)
        self.cruce = cruce or crearCruce(self.params.cruce, self.rng, self.params)
        self.mutacion = mutacion or crearMutacion(self.params.mutacion, self.rng, self.params)
        self.historial = HistorialConvergencia()

    def nombre(self) -> str:
        return "genetico"

    def resolver(self, inst: InstanciaTransporte) -> SolucionGenetica:
        inicio = time.perf_counter()
        self.historial = HistorialConvergencia()

        pob = self._poblacionInicial(inst)
        self.historial.registrar(pob)
        for _ in range(self.params.generaciones):
            pob = self._evolucionar(pob, inst)
            self.historial.registrar(pob)

        mejor = pob.mejor()
        x = self.decodificador.decodificar(mejor, inst)
        tiempo = time.perf_counter() - inicio
        return SolucionGenetica(
            metodo=self.nombre(),
            x=x,
            costo_total=inst.costo(x),
            tiempo_s=tiempo,
            iteraciones=self.params.generaciones,
            factible=inst.verificar(x) == [],
            historial=self.historial,
        )

    # ---- pasos del algoritmo ----

    def _poblacionInicial(self, inst: InstanciaTransporte) -> Poblacion:
        largo = inst.n() * inst.m()
        individuos = []
        for _ in range(self.params.poblacion):
            genes = [self.rng.uniforme() if self.rng.uniforme() < DENSIDAD_INICIAL else 0.0
                     for _ in range(largo)]
            c = Cromosoma(genes)
            self.fitness.evaluar(c, inst)
            individuos.append(c)
        return Poblacion(individuos)

    def _evolucionar(self, pob: Poblacion, inst: InstanciaTransporte) -> Poblacion:
        pob.ordenar()
        nuevos = [c.copiar() for c in pob.individuos[: self.params.elitismo]]
        while len(nuevos) < self.params.poblacion:
            padreA = self.seleccion.seleccionar(pob)
            padreB = self.seleccion.seleccionar(pob)
            if self.rng.uniforme() < self.params.p_cruce:
                hijoA, hijoB = self.cruce.cruzar(padreA, padreB)
            else:
                hijoA, hijoB = padreA.copiar(), padreB.copiar()
            for hijo in (hijoA, hijoB):
                if len(nuevos) == self.params.poblacion:
                    break
                self.mutacion.mutar(hijo)
                self.fitness.evaluar(hijo, inst)
                nuevos.append(hijo)
        return Poblacion(nuevos)
