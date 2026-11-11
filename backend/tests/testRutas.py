"""Pruebas del trazado por carretera (sin internet: el servicio web se reemplaza por uno falso)."""

import json

import pytest
from fastapi.testclient import TestClient

from app.dependencias import obtenerServicioRutas
from app.infraestructura.rutasCarretera import CacheRutas, IProveedorRutas, ProveedorOsrm, RutaCarretera, SinConexion
from app.main import crearApp
from app.servicios.servicioRutas import ServicioRutas


class ProveedorFalso(IProveedorRutas):
    def __init__(self, fallarDesde: int = 10 ** 9):
        self.consultas = 0
        self.fallarDesde = fallarDesde

    def trazar(self, origen, destino):
        if self.consultas >= self.fallarDesde:
            raise SinConexion("sin internet")
        self.consultas += 1
        return RutaCarretera([origen, ((origen[0] + destino[0]) / 2, origen[1]), destino], 10.0, 12.0)


class RepositorioFalso:
    def __init__(self, red):
        self.red = red

    def obtenerRed(self):
        return self.red


def paresTrazables(red) -> int:
    """Pares con coordenadas distintas (en el mismo municipio no hay nada que trazar)."""
    return sum(1 for a in red.agroempresas for p in red.plantas if (a.lat, a.lon) != (p.lat, p.lon))


def testDescargaLoQueFaltaYLoGuarda(redSemilla, tmp_path):
    archivo = tmp_path / "rutas.json"
    proveedor = ProveedorFalso()
    servicio = ServicioRutas(RepositorioFalso(redSemilla), CacheRutas(archivo), proveedor, pausa_s=0)
    resultado = servicio.rutasDeLaRed()
    total = paresTrazables(redSemilla)
    assert len(resultado.tramos) == total and proveedor.consultas == total
    assert resultado.faltantes == 0 and not resultado.sin_conexion
    guardado = json.loads(archivo.read_text(encoding="utf-8"))
    assert len(guardado["rutas"]) == total and "OSRM" in guardado["fuente"]


def testUsaLaCacheSinVolverAConsultar(redSemilla, tmp_path):
    archivo = tmp_path / "rutas.json"
    ServicioRutas(RepositorioFalso(redSemilla), CacheRutas(archivo), ProveedorFalso(), pausa_s=0).rutasDeLaRed()
    proveedor = ProveedorFalso()
    resultado = ServicioRutas(RepositorioFalso(redSemilla), CacheRutas(archivo), proveedor, pausa_s=0).rutasDeLaRed()
    assert proveedor.consultas == 0
    assert len(resultado.tramos) == paresTrazables(redSemilla)


def testSinInternetDevuelveLoGuardadoYCuentaLoQueFalta(redSemilla, tmp_path):
    archivo = tmp_path / "rutas.json"
    servicio = ServicioRutas(RepositorioFalso(redSemilla), CacheRutas(archivo), ProveedorFalso(fallarDesde=5), pausa_s=0)
    resultado = servicio.rutasDeLaRed()
    assert resultado.sin_conexion
    assert len(resultado.tramos) == 5
    assert resultado.faltantes == paresTrazables(redSemilla) - 5
    assert len(json.loads(archivo.read_text(encoding="utf-8"))["rutas"]) == 5


def testProveedorOsrmSinServidorLanzaSinConexion():
    proveedor = ProveedorOsrm(urlBase="http://127.0.0.1:9", tiempoMaximo=1)
    with pytest.raises(SinConexion):
        proveedor.trazar((4.14, -73.62), (4.25, -73.56))
    with pytest.raises(SinConexion):  # no vuelve a esperar al servidor tras el fallo
        proveedor.trazar((4.14, -73.62), (4.25, -73.56))


def testEndpointRutasCarretera(tmp_path, redSemilla):
    app = crearApp("sqlite://")
    app.dependency_overrides[obtenerServicioRutas] = lambda: ServicioRutas(
        RepositorioFalso(redSemilla), CacheRutas(tmp_path / "rutas.json"), ProveedorFalso(), pausa_s=0)
    with TestClient(app) as cliente:
        soloCache = cliente.get("/red/rutas-carretera").json()
        respuesta = cliente.get("/red/rutas-carretera", params={"descargar": True})
    assert soloCache["tramos"] == [] and soloCache["faltantes"] == paresTrazables(redSemilla)
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert len(cuerpo["tramos"]) == paresTrazables(redSemilla)
    tramo = cuerpo["tramos"][0]
    assert {"agroempresa_id", "planta_id", "puntos", "distancia_km", "duracion_min"} <= tramo.keys()
    assert len(tramo["puntos"][0]) == 2
