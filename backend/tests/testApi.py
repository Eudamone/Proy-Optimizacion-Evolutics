"""Pruebas de la API y la persistencia, con una base SQLite en memoria."""

import pytest
from fastapi.testclient import TestClient

from app.main import crearApp
from app.persistencia.cargaInicial import cargarRedSemilla
from app.persistencia.conexion import configurarBaseDatos, nuevaSesion
from app.persistencia.repositorios.ejecucionRepository import EjecucionRepository
from app.persistencia.repositorios.redRepository import RedRepository

AG_RAPIDO = {"poblacion": 20, "generaciones": 20, "semilla": 1}


@pytest.fixture
def cliente():
    with TestClient(crearApp("sqlite://")) as c:
        yield c


# ---- persistencia ----

def testRepositorioGuardaYLeeLaRed():
    configurarBaseDatos("sqlite://")
    sesion = nuevaSesion()
    repositorio = RedRepository(sesion)
    assert repositorio.estaVacia()
    original = cargarRedSemilla()
    repositorio.guardar(original)
    leida = repositorio.obtenerRed()
    assert [a.id for a in leida.agroempresas] == [a.id for a in original.agroempresas]
    assert leida.totalOferta() == original.totalOferta()
    assert leida.ruta("A02", "P04").habilitada is False
    assert leida.parametros.tarifa_t_km == 2500
    sesion.close()


def testRepositorioDeEjecuciones():
    configurarBaseDatos("sqlite://")
    sesion = nuevaSesion()
    repositorio = EjecucionRepository(sesion)
    nuevoId = repositorio.guardar({
        "tipo": "comparacion", "z_exacto": 100, "z_ag_mejor": 101, "z_ag_promedio": 102, "desv_estandar": 1,
        "gap_pct": 1, "tiempo_exacto_s": 0.01, "tiempo_ag_s": 1, "corridas": 3,
        "parametros": {"poblacion": 20}, "resultado": {"nota": "prueba"},
    })
    assert repositorio.listar()[0]["id"] == nuevoId
    assert repositorio.obtener(nuevoId)["resultado"] == {"nota": "prueba"}
    assert repositorio.obtener(999) is None
    sesion.close()


# ---- red ----

def testSalud(cliente):
    assert cliente.get("/salud").json() == {"estado": "ok"}


def testAlIniciarCargaLosDatosDePrueba(cliente):
    red = cliente.get("/red").json()
    assert len(red["agroempresas"]) == 10
    assert len(red["plantas"]) == 4
    assert len(red["rutas"]) == 40


def testResumenDeLaRed(cliente):
    resumen = cliente.get("/red/resumen").json()
    assert resumen["total_oferta_t"] == 373
    assert resumen["total_capacidad_t"] == 420
    assert resumen["factible"] is True


def testActualizarRedValida(cliente):
    red = cliente.get("/red").json()
    red["plantas"][1]["capacidad_t"] = 80
    respuesta = cliente.put("/red", json=red)
    assert respuesta.status_code == 200
    assert respuesta.json()["total_capacidad_t"] == 430
    assert cliente.get("/red").json()["plantas"][1]["capacidad_t"] == 80


def testActualizarRedInfactibleDevuelve422YNoGuarda(cliente):
    red = cliente.get("/red").json()
    red["plantas"][0]["activa"] = False
    respuesta = cliente.put("/red", json=red)
    assert respuesta.status_code == 422
    assert "supera la capacidad" in respuesta.json()["errores"][0]
    assert cliente.get("/red").json()["plantas"][0]["activa"] is True


def testRestablecerRed(cliente):
    red = cliente.get("/red").json()
    red["plantas"][1]["capacidad_t"] = 80
    cliente.put("/red", json=red)
    assert cliente.post("/red/restablecer").json()["total_capacidad_t"] == 420


# ---- optimización ----

def testResolverConElMetodoExacto(cliente):
    sol = cliente.post("/optimizacion/resolver", json={"metodo": "exacto"}).json()
    assert sol["costo_total"] == pytest.approx(33_263_400)
    assert sol["factible"] is True
    assert sol["costo_inicial"] >= sol["costo_total"]
    assert sum(f["toneladas"] for f in sol["flujos"]) == pytest.approx(373)


def testResolverConElGenetico(cliente):
    sol = cliente.post("/optimizacion/resolver", json={"metodo": "genetico", "parametros": AG_RAPIDO}).json()
    assert sol["metodo"] == "genetico"
    assert len(sol["historial"]["mejor_costo"]) == 21


def testParametrosInvalidosDevuelven422(cliente):
    respuesta = cliente.post("/optimizacion/resolver",
                             json={"metodo": "genetico", "parametros": {"poblacion": 5, "elitismo": 5}})
    assert respuesta.status_code == 422


def testCompararGuardaEnElHistorial(cliente):
    comp = cliente.post("/optimizacion/comparar", json={"parametros": AG_RAPIDO, "corridas": 2}).json()
    assert comp["z_ag_mejor"] >= comp["z_exacto"] - 1e-6
    assert len(comp["costos_ag"]) == 2
    historial = cliente.get("/reportes").json()
    assert len(historial) == 1
    assert historial[0]["id"] == comp["ejecucion_id"]
    detalle = cliente.get(f"/reportes/{comp['ejecucion_id']}").json()
    assert detalle["resultado"]["z_exacto"] == comp["z_exacto"]


def testReporteInexistenteDevuelve404(cliente):
    assert cliente.get("/reportes/999").status_code == 404


# ---- sensibilidad ----

def testSensibilidadSinEscenario(cliente):
    r = cliente.post("/sensibilidad", json={}).json()
    restrepo = next(c for c in r["capacidades"] if c["id"] == "P02")
    assert restrepo["ahorro_por_tonelada"] == pytest.approx(18_000)
    assert r["escenario"] is None
    assert all(ruta["rango"]["maximo"] is None for ruta in r["rutas"] if ruta["toneladas"] == 0)


def testSensibilidadConEscenarioDeCierre(cliente):
    cuerpo = {"escenario": {"tipo": "CIERRE_PLANTA", "objetivo_id": "P04"}}
    [paso] = cliente.post("/sensibilidad", json=cuerpo).json()["escenario"]
    assert paso["factible"] is False


def testEscenarioConPlantaInexistente(cliente):
    cuerpo = {"escenario": {"tipo": "CAPACIDAD", "objetivo_id": "P99"}}
    assert cliente.post("/sensibilidad", json=cuerpo).status_code == 422
