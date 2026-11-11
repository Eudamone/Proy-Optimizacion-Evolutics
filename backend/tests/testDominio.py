"""Pruebas del dominio: carga de la red, validación y construcción de la instancia."""

import pytest

from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.dominio.red import Agroempresa, Planta
from app.dominio.tipos import TipoResiduo, matrizCeros
from app.dominio.validador import ValidadorRed


# ---- carga de la semilla ----

def testSemillaTieneDiezAgroempresasYCuatroPlantas(redSemilla):
    assert len(redSemilla.agroempresas) == 10
    assert len(redSemilla.plantas) == 4
    assert len(redSemilla.rutas) == 40


def testTotalesDeLaSemilla(redSemilla):
    assert redSemilla.totalOferta() == 373
    assert redSemilla.totalCapacidad() == 420


def testSemillaEsValida(redSemilla):
    assert ValidadorRed().validar(redSemilla) == []


# ---- validación ----

def testOfertaMayorQueCapacidadEsInfactible(redSemilla):
    redSemilla.planta("P01").activa = False  # quedan 280 t de capacidad para 373 t
    errores = ValidadorRed().validar(redSemilla)
    assert len(errores) == 1
    assert "supera la capacidad" in errores[0]


def testFaltaTarifa(redSemilla):
    redSemilla.parametros.tarifa_t_km = None
    assert any("tarifa" in e for e in ValidadorRed().validar(redSemilla))


def testOfertaNegativa(redSemilla):
    redSemilla.agroempresa("A01").oferta_t = -5
    assert any("negativa" in e for e in ValidadorRed().validar(redSemilla))


def testFaltaUnaRuta(redSemilla):
    redSemilla.rutas = [r for r in redSemilla.rutas if not (r.agroempresa_id == "A03" and r.planta_id == "P02")]
    assert any("Falta la distancia" in e for e in ValidadorRed().validar(redSemilla))


def testAgroempresaSinRutasHabilitadas(redSemilla):
    for r in redSemilla.rutas:
        if r.agroempresa_id == "A05":
            r.habilitada = False
    assert any("no tiene ninguna ruta" in e for e in ValidadorRed().validar(redSemilla))


# ---- cambios en la red ----

def testAgregarAgroempresaCreaUnaRutaPorPlanta(redSemilla):
    nueva = Agroempresa("A11", "Forestal El Dorado", "El Dorado", TipoResiduo.FORESTAL, 12)
    redSemilla.agregarAgroempresa(nueva, [60, 70, 90, 250])
    assert redSemilla.totalOferta() == 385
    assert redSemilla.distancia("A11", "P03") == 90


def testAgregarAgroempresaConDistanciasIncompletas(redSemilla):
    nueva = Agroempresa("A11", "Forestal El Dorado", "El Dorado", TipoResiduo.FORESTAL, 12)
    with pytest.raises(ValueError):
        redSemilla.agregarAgroempresa(nueva, [60, 70])


def testAgregarPlantaRepetida(redSemilla):
    repetida = Planta("P01", "Otra", "Villavicencio", 10, 1000)
    with pytest.raises(ValueError):
        redSemilla.agregarPlanta(repetida, [1.0] * 10)


def testQuitarPlantaEliminaSusRutas(redSemilla):
    redSemilla.quitarPlanta("P04")
    assert len(redSemilla.plantas) == 3
    assert all(r.planta_id != "P04" for r in redSemilla.rutas)


# ---- instancia ----

def testCostoUnitario(redSemilla, instanciaSemilla):
    # c_ij = d_ij * tarifa + costo de operación de la planta
    d = redSemilla.distancia("A03", "P02")
    esperado = d * 2500 + 15500
    i, j = instanciaSemilla.fuentes.index("A03"), instanciaSemilla.plantas.index("P02")
    assert instanciaSemilla.C[i][j] == pytest.approx(esperado)


def testRutaBloqueadaCuestaGranM(instanciaSemilla):
    i, j = instanciaSemilla.fuentes.index("A02"), instanciaSemilla.plantas.index("P04")
    assert instanciaSemilla.C[i][j] == instanciaSemilla.gran_m


def testPlantaInactivaQuedaConCapacidadCero(redSemilla):
    redSemilla.planta("P04").activa = False
    inst = InstanciaBuilder().construir(redSemilla)
    assert inst.b == [140, 70, 120, 0]


def testVerificarSolucionFactible():
    inst = InstanciaTransporte(["F1", "F2"], ["P1", "P2"], a=[10, 20], b=[15, 20], C=[[1, 2], [3, 4]])
    x = [[10, 0], [5, 15]]
    assert inst.verificar(x) == []
    assert inst.costo(x) == 10 * 1 + 5 * 3 + 15 * 4


def testVerificarDetectaOfertaIncompletaYExcesoDeCapacidad():
    inst = InstanciaTransporte(["F1", "F2"], ["P1", "P2"], a=[10, 20], b=[15, 20], C=[[1, 2], [3, 4]])
    x = [[10, 0], [10, 5]]  # P1 recibe 20 > 15 y F2 despacha 15 de 20
    errores = inst.verificar(x)
    assert any("capacidad" in e for e in errores)
    assert any("debe despachar" in e for e in errores)


def testVerificarDetectaRutaBloqueada(instanciaSemilla):
    x = matrizCeros(instanciaSemilla.n(), instanciaSemilla.m())
    i, j = instanciaSemilla.fuentes.index("A02"), instanciaSemilla.plantas.index("P04")
    x[i][j] = 1
    assert any("bloqueada" in e for e in instanciaSemilla.verificar(x))


def testConCambiosNoModificaLaOriginal(instanciaSemilla):
    copia = instanciaSemilla.conCambios(b=[0, 0, 0, 0])
    copia.C[0][0] = -1
    assert instanciaSemilla.b == [140, 70, 120, 90]
    assert instanciaSemilla.C[0][0] != -1
