"""Pruebas del AG: decodificación, aptitud, operadores y reproducibilidad con semilla."""

import pytest

from app.dominio.instancia import InstanciaTransporte
from app.genetico.aleatorio import GeneradorAleatorio
from app.genetico.cromosoma import Cromosoma, Poblacion
from app.genetico.cruce import CruceDosPuntos, CruceUnPunto
from app.genetico.decodificador import Decodificador
from app.genetico.fitness import FitnessPenalizado
from app.genetico.mutacion import MutacionPoda, MutacionUniforme
from app.genetico.parametros import ParametrosAG
from app.genetico.seleccion import SeleccionTorneo
from app.genetico.solverGenetico import AlgoritmoGeneticoSolver
from app.motores.fabrica import SolverFactory
from app.transporte.solverTransporte import SolverTransporte

GRAN_M = 1e8


def instanciaPequena() -> InstanciaTransporte:
    # F2 -> P3 está bloqueada y P4 está inactiva (capacidad 0)
    return InstanciaTransporte(
        fuentes=["F1", "F2"],
        plantas=["P1", "P2", "P3", "P4"],
        a=[30, 20],
        b=[25, 20, 30, 0],
        C=[[4, 6, 9, 1], [5, 3, GRAN_M, 1]],
        gran_m=GRAN_M,
    )


# ---- decodificación ----

def testDecodificarCumpleLaOfertaDeCadaFuente():
    inst = instanciaPequena()
    x = Decodificador().decodificar(Cromosoma([0.2, 0.5, 0.3, 0.9, 0.7, 0.1, 0.8, 0.6]), inst)
    assert sum(x[0]) == pytest.approx(30)
    assert sum(x[1]) == pytest.approx(20)


def testDecodificarRespetaRutasBloqueadasYPlantasInactivas():
    inst = instanciaPequena()
    x = Decodificador().decodificar(Cromosoma([0.2, 0.5, 0.3, 0.9, 0.7, 0.1, 0.8, 0.6]), inst)
    assert x[1][2] == 0          # ruta bloqueada
    assert x[0][3] == x[1][3] == 0  # planta inactiva


def testDecodificarProporcional():
    inst = instanciaPequena()
    x = Decodificador().decodificar(Cromosoma([1, 1, 2, 0, 0, 1, 0, 0]), inst)
    assert x[0][:3] == pytest.approx([7.5, 7.5, 15])
    assert x[1][:3] == pytest.approx([0, 20, 0])


def testGenesEnCeroRepartenParejo():
    inst = instanciaPequena()
    x = Decodificador().decodificar(Cromosoma([0.0] * 8), inst)
    assert x[0][:3] == pytest.approx([10, 10, 10])
    assert x[1][:3] == pytest.approx([10, 10, 0])


# ---- aptitud ----

def testExcesoDeCapacidadBajaLaAptitud():
    inst = instanciaPequena()
    fitness = FitnessPenalizado(Decodificador(), lambda_=1000)
    conExceso = Cromosoma([1, 0, 0, 0, 0, 1, 0, 0])  # F1 manda 30 a P1 (capacidad 25)
    sinExceso = Cromosoma([5, 0, 1, 0, 0, 1, 0, 0])  # F1: 25 a P1 y 5 a P3; F2: 20 a P2
    fitness.evaluar(conExceso, inst)
    fitness.evaluar(sinExceso, inst)
    assert conExceso.exceso == pytest.approx(5)
    assert sinExceso.exceso == pytest.approx(0)
    assert sinExceso.aptitud > conExceso.aptitud


def testLambdaAutomaticoIgnoraGranM():
    inst = instanciaPequena()
    assert FitnessPenalizado(Decodificador()).lambdaPara(inst) == 2 * 9


# ---- operadores ----

def testCruceUnPuntoMezclaLosPadres():
    rng = GeneradorAleatorio(1)
    a, b = Cromosoma([0.0] * 6), Cromosoma([1.0] * 6)
    hijoA, hijoB = CruceUnPunto(rng).cruzar(a, b)
    corte = hijoA.genes.index(1.0)
    assert hijoA.genes == [0.0] * corte + [1.0] * (6 - corte)
    assert hijoB.genes == [1.0] * corte + [0.0] * (6 - corte)
    assert a.genes == [0.0] * 6  # los padres no cambian


def testCruceDosPuntosConservaLosGenes():
    rng = GeneradorAleatorio(2)
    a, b = Cromosoma([0.0] * 8), Cromosoma([1.0] * 8)
    hijoA, hijoB = CruceDosPuntos(rng).cruzar(a, b)
    assert len(hijoA.genes) == 8
    assert [x + y for x, y in zip(hijoA.genes, hijoB.genes)] == [1.0] * 8


def testMutacionConProbabilidadCeroNoCambiaNada():
    c = Cromosoma([0.5] * 10)
    MutacionUniforme(GeneradorAleatorio(3), prob=0).mutar(c)
    assert c.genes == [0.5] * 10


def testMutacionPodaDejaGenesEnCero():
    c = Cromosoma([0.5] * 200)
    MutacionPoda(GeneradorAleatorio(4), prob=1).mutar(c)
    assert c.genes.count(0.0) > 50
    assert all(0 <= g <= 1 for g in c.genes)


def testTorneoConTodaLaPoblacionEligeAlMejor():
    pob = Poblacion([Cromosoma([0], aptitud=a) for a in (0.1, 0.9, 0.5)])
    elegido = SeleccionTorneo(GeneradorAleatorio(5), k=3).seleccionar(pob)
    assert elegido.aptitud == 0.9


# ---- parámetros ----

def testParametrosInvalidos():
    errores = ParametrosAG(p_cruce=1.5, seleccion="azar").validar()
    assert len(errores) == 2
    with pytest.raises(ValueError):
        AlgoritmoGeneticoSolver(ParametrosAG(generaciones=0))


# ---- algoritmo completo ----

def testMismaSemillaMismoResultado(instanciaSemilla):
    p = ParametrosAG(poblacion=30, generaciones=40, semilla=7)
    sol1 = AlgoritmoGeneticoSolver(p).resolver(instanciaSemilla)
    sol2 = AlgoritmoGeneticoSolver(p).resolver(instanciaSemilla)
    assert sol1.costo_total == sol2.costo_total
    assert sol1.historial.mejor_costo == sol2.historial.mejor_costo


def testHistorialRegistraCadaGeneracionYNoEmpeora(instanciaSemilla):
    p = ParametrosAG(poblacion=30, generaciones=40, semilla=3)
    solver = AlgoritmoGeneticoSolver(p)
    sol = solver.resolver(instanciaSemilla)
    h = sol.historial
    assert h.generaciones() == 41  # población inicial + 40 generaciones
    lam = solver.fitness.lambdaPara(instanciaSemilla)
    penalizado = [c + lam * e for c, e in zip(h.mejor_costo, h.mejor_exceso)]
    assert all(b <= a + 1e-6 for a, b in zip(penalizado, penalizado[1:]))  # el elitismo guarda al mejor


def testRedSemillaCercaDelOptimo(instanciaSemilla):
    exacto = SolverTransporte().resolver(instanciaSemilla)
    sol = AlgoritmoGeneticoSolver(ParametrosAG(semilla=1)).resolver(instanciaSemilla)
    gap = (sol.costo_total - exacto.costo_total) / exacto.costo_total * 100
    assert sol.factible
    assert sol.costo_total >= exacto.costo_total - 1e-6  # nunca mejor que el óptimo
    assert gap < 5


def testFabricaCreaElGenetico():
    solver = SolverFactory().crear("genetico", ParametrosAG(semilla=1))
    assert solver.nombre() == "genetico"
