import random

import pytest

from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.motores.fabrica import SolverFactory
from app.transporte.arbolBase import ArbolBase
from app.transporte.balanceador import Balanceador
from app.transporte.solverTransporte import SolverTransporte
from app.transporte.vogel import MetodoVogel


def ejercicioClasico() -> InstanciaTransporte:
    """Ejercicio de libro: Vogel da 779 y el óptimo es 743."""
    return InstanciaTransporte(
        fuentes=["F1", "F2", "F3"],
        plantas=["D1", "D2", "D3", "D4"],
        a=[7, 9, 18],
        b=[5, 8, 7, 14],
        C=[[19, 30, 50, 10],
           [70, 30, 40, 60],
           [40, 8, 70, 20]],
    )


def verificarOptimalidad(sol, tolerancia=1e-6):
    escala = max(1.0, max(abs(x) for fila in sol.dual.d for x in fila))
    assert min(min(fila) for fila in sol.dual.d) >= -tolerancia * escala


# ---- Vogel ----

def testVogelEjercicioClasico():
    tabla = MetodoVogel().construir(Balanceador().balancear(ejercicioClasico()))
    assert tabla.costo() == 779
    assert len(tabla.basicas) == 3 + 4 - 1


def testVogelDegeneradoCompletaLaBase():
    # La primera asignación agota a la vez la fila 1 y la columna 1.
    inst = InstanciaTransporte(["F1", "F2"], ["P1", "P2"], a=[10, 20], b=[10, 20], C=[[1, 9], [9, 1]])
    tabla = MetodoVogel().construir(Balanceador().balancear(inst))
    assert len(tabla.basicas) == 3
    assert tabla.costo() == 30


# ---- MODI ----

def testModiLlegaAlOptimoDelEjercicioClasico():
    sol = SolverTransporte().resolver(ejercicioClasico())
    assert sol.costo_total == 743
    assert sol.dual.costoInicial == 779
    assert sol.factible
    verificarOptimalidad(sol)


def testPotencialesCumplenLasCeldasBasicas():
    inst = ejercicioClasico()
    sol = SolverTransporte().resolver(inst)
    u, v = sol.dual.u, sol.dual.v
    for i, j in sol.dual.basicas:
        assert u[i] + v[j] == pytest.approx(inst.C[i][j])


def testCicloAlternaSignos():
    arbol = ArbolBase({(0, 0), (0, 1), (1, 1)}, n=2, m=2)
    ciclo = arbol.ciclo((1, 0))
    assert ciclo == [((1, 0), +1), ((0, 0), -1), ((0, 1), +1), ((1, 1), -1)]


# ---- problema desbalanceado y casos especiales ----

def testCapacidadMayorQueOfertaUsaFuenteFicticia():
    inst = InstanciaTransporte(["F1", "F2"], ["P1", "P2", "P3"], a=[30, 25], b=[20, 30, 40], C=[[4, 6, 9], [5, 3, 8]])
    sol = SolverTransporte().resolver(inst)
    assert len(sol.x) == 2 and len(sol.x[0]) == 3   # sin la fila ficticia
    assert inst.verificar(sol.x) == []
    # Óptimo a mano: F2 -> P2 25 t; F1 -> P1 20 t, P2 5 t y P3 5 t = 75 + 80 + 30 + 45
    assert sol.costo_total == 230
    verificarOptimalidad(sol)


def testOfertaMayorQueCapacidadNoEsFactible():
    inst = InstanciaTransporte(["F1"], ["P1"], a=[50], b=[40], C=[[1]])
    with pytest.raises(ValueError):
        SolverTransporte().resolver(inst)


def testPlantaInactivaNoRecibeResiduos(redSemilla):
    redSemilla.planta("P04").activa = False
    redSemilla.planta("P04").capacidad_t = 90
    redSemilla.planta("P01").capacidad_t = 240  # para que siga siendo factible
    inst = InstanciaBuilder().construir(redSemilla)
    sol = SolverTransporte().resolver(inst)
    j = inst.plantas.index("P04")
    assert all(fila[j] == 0 for fila in sol.x)
    assert sol.factible


# ---- red de prueba ----

def testRedSemillaOptima(instanciaSemilla):
    sol = SolverTransporte().resolver(instanciaSemilla)
    assert sol.factible
    assert sol.costo_total == pytest.approx(33_263_400)
    assert sol.costo_total <= sol.dual.costoInicial
    verificarOptimalidad(sol)


def testRedSemillaNoUsaLaRutaBloqueada(instanciaSemilla):
    sol = SolverTransporte().resolver(instanciaSemilla)
    i, j = instanciaSemilla.fuentes.index("A02"), instanciaSemilla.plantas.index("P04")
    assert sol.x[i][j] == 0


# ---- instancias aleatorias: siempre factible y con certificado de óptimo ----

@pytest.mark.parametrize("semilla", range(30))
def testInstanciasAleatorias(semilla):
    rnd = random.Random(semilla)
    n, m = rnd.randint(2, 8), rnd.randint(2, 8)
    a = [rnd.randint(0, 50) for _ in range(n)]
    b = [rnd.randint(0, 60) for _ in range(m)]
    if sum(b) < sum(a):
        b[0] += sum(a) - sum(b) + rnd.choice([0, 7])
    C = [[rnd.randint(1, 20) for _ in range(m)] for _ in range(n)]
    inst = InstanciaTransporte([f"F{i}" for i in range(n)], [f"P{j}" for j in range(m)], a, b, C)
    sol = SolverTransporte().resolver(inst)
    assert inst.verificar(sol.x) == []
    verificarOptimalidad(sol)


# ---- fábrica ----

def testFabricaCreaElSolverExacto():
    solver = SolverFactory().crear("exacto")
    assert solver.nombre() == "exacto"


def testFabricaPermiteRegistrarUnMetodoNuevo():
    fabrica = SolverFactory()
    fabrica.registrar("vogelSolo", lambda parametros=None: SolverTransporte())
    assert "vogelSolo" in fabrica.metodos()
    assert fabrica.crear("vogelSolo").nombre() == "exacto"


def testSolucionExactaExigeLaInformacionDual():
    from app.dominio.solucion import SolucionExacta
    with pytest.raises(ValueError):
        SolucionExacta(metodo="exacto", x=[[1.0]], costo_total=1.0, tiempo_s=0.0)
