"""Pruebas de sensibilidad, escenarios y comparador.

Los precios sombra y los rangos se comprueban volviendo a resolver el problema
con el dato cambiado: el resultado debe coincidir con lo que predice el análisis.
"""

import math

import pytest

from app.analisis.comparador import Comparador
from app.analisis.escenarios import Escenario, SimuladorEscenarios, TipoEscenario
from app.analisis.sensibilidad import AnalizadorSensibilidad, Rango
from app.genetico.parametros import ParametrosAG
from app.transporte.solverTransporte import SolverTransporte


@pytest.fixture
def base(instanciaSemilla):
    sol = SolverTransporte().resolver(instanciaSemilla)
    resultado = AnalizadorSensibilidad().analizar(sol, instanciaSemilla)
    return instanciaSemilla, sol, resultado


def resolver(inst):
    return SolverTransporte().resolver(inst).costo_total


# ---- precios sombra ----

def testPrecioSombraDeCapacidadPrediceElCambioDeCosto(base):
    inst, sol, r = base
    for j in range(inst.m()):
        if r.rangos_capacidad[j].maximo >= inst.b[j] + 1:
            modificada = inst.conCambios()
            modificada.b[j] += 1
            assert resolver(modificada) - sol.costo_total == pytest.approx(r.precio_sombra_capacidad[j])


def testPrecioSombraDeOfertaPrediceElCambioDeCosto(base):
    inst, sol, r = base
    for i in range(inst.n()):
        if r.rangos_oferta[i].maximo >= inst.a[i] + 1:
            modificada = inst.conCambios()
            modificada.a[i] += 1
            assert resolver(modificada) - sol.costo_total == pytest.approx(r.precio_sombra_oferta[i])


def testPlantasConHolguraTienenPrecioSombraCero(base):
    inst, sol, r = base
    for j in range(inst.m()):
        recibido = sum(fila[j] for fila in sol.x)
        if recibido < inst.b[j] - 1e-9:
            assert r.precio_sombra_capacidad[j] == 0


def testAhorroPorCapacidadEsPositivoEnPlantasLlenas(base):
    _, _, r = base
    assert all(ahorro >= 0 for ahorro in r.ahorroPorCapacidad())


# ---- rangos de costo ----

def testRutaNoUsadaEntraSiSuCostoBajaMasQueSuCostoReducido(base):
    inst, sol, r = base
    i, j = inst.fuentes.index("A01"), inst.plantas.index("P03")  # ruta no usada
    rango = r.rangos_costo[(i, j)]
    assert rango.maximo == math.inf
    assert rango.minimo == pytest.approx(inst.C[i][j] - r.costos_reducidos[i][j])

    dentro = inst.conCambios()
    dentro.C[i][j] = rango.minimo + 1000
    assert resolver(dentro) == pytest.approx(sol.costo_total)  # sigue sin usarse

    fuera = inst.conCambios()
    fuera.C[i][j] = rango.minimo - 1000
    assert resolver(fuera) < sol.costo_total  # ahora conviene usarla


def testDentroDelRangoElCostoCambiaLinealmente(base):
    inst, sol, r = base
    for (i, j), rango in r.rangos_costo.items():
        if sol.x[i][j] <= 0 or math.isinf(rango.minimo):
            continue
        nuevo = (rango.minimo + rango.actual) / 2
        modificada = inst.conCambios()
        modificada.C[i][j] = nuevo
        esperado = sol.costo_total + sol.x[i][j] * (nuevo - rango.actual)
        assert resolver(modificada) == pytest.approx(esperado)


def testRangoContiene():
    rango = Rango(actual=10, minimo=5, maximo=math.inf)
    assert rango.contiene(5) and rango.contiene(1e9)
    assert not rango.contiene(4.9)


def testSensibilidadNecesitaElMetodoExacto(instanciaSemilla):
    from app.genetico.solverGenetico import AlgoritmoGeneticoSolver
    sol = AlgoritmoGeneticoSolver(ParametrosAG(poblacion=10, generaciones=5, semilla=1)).resolver(instanciaSemilla)
    with pytest.raises(ValueError):
        AnalizadorSensibilidad().analizar(sol, instanciaSemilla)


# ---- escenarios ----

def testDeltasDelEscenario():
    esc = Escenario(TipoEscenario.CAPACIDAD, objetivo=0, delta_min=-30, delta_max=40, pasos=8)
    assert esc.deltas() == [-30, -20, -10, 0, 10, 20, 30, 40]


def testAplicarNoModificaLaInstanciaOriginal(instanciaSemilla):
    esc = Escenario(TipoEscenario.CAPACIDAD, objetivo=0)
    nueva = esc.aplicar(instanciaSemilla, 50)
    assert nueva.b[0] == 210
    assert instanciaSemilla.b[0] == 140


def testCostoDeTransporteRespetaGranM(instanciaSemilla):
    nueva = Escenario(TipoEscenario.COSTO_TRANSPORTE).aplicar(instanciaSemilla, 10)
    i, j = instanciaSemilla.fuentes.index("A02"), instanciaSemilla.plantas.index("P04")
    assert nueva.C[i][j] == instanciaSemilla.gran_m
    assert nueva.C[0][0] == pytest.approx(instanciaSemilla.C[0][0] * 1.1)


def testSimularCapacidadDeVillavicencio(instanciaSemilla):
    esc = Escenario(TipoEscenario.CAPACIDAD, objetivo=0, delta_min=-30, delta_max=40, pasos=8)
    pasos = SimuladorEscenarios().simular(instanciaSemilla, esc)
    porDelta = {p.delta: p for p in pasos}
    assert porDelta[0].cambia_base is False
    assert porDelta[0].costo_total == pytest.approx(resolver(instanciaSemilla))
    assert porDelta[-30].cambia_base is True
    assert porDelta[-30].costo_total > porDelta[0].costo_total  # menos capacidad, más caro


def testCerrarUnaPlantaPuedeVolverInfactibleLaRed(instanciaSemilla):
    esc = Escenario(TipoEscenario.CIERRE_PLANTA, objetivo=instanciaSemilla.plantas.index("P04"))
    [paso] = SimuladorEscenarios().simular(instanciaSemilla, esc)
    assert paso.factible is False   # quedan 330 t de capacidad para 373 t
    assert paso.costo_total is None
    assert "supera la capacidad" in paso.mensaje


# ---- comparador ----

def testComparadorResumeLasCorridas(instanciaSemilla):
    p = ParametrosAG(poblacion=30, generaciones=40, semilla=10)
    comp = Comparador().comparar(instanciaSemilla, p, corridas=3)
    assert comp.semillas == [10, 11, 12]
    assert len(comp.costos_ag) == 3
    assert comp.z_ag_mejor == min(comp.costos_ag)
    assert comp.z_ag_mejor >= comp.z_exacto - 1e-6
    assert comp.gapPct() >= 0
    assert comp.gapPromedioPct() >= comp.gapPct()
    assert set(comp.tiempos) == {"exacto", "genetico_promedio"}
    assert comp.mejor_genetica.historial is not None


def testComparadorSinCorridas(instanciaSemilla):
    with pytest.raises(ValueError):
        Comparador().comparar(instanciaSemilla, ParametrosAG(), corridas=0)
