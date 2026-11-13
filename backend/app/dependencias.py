from fastapi import Depends
from sqlalchemy.orm import Session

from app.analisis.escenarios import SimuladorEscenarios
from app.analisis.sensibilidad import AnalizadorSensibilidad
from app.dominio.instancia import InstanciaBuilder
from app.dominio.validador import ValidadorRed
from app.esquemas.optimizacion import comparacionADto
from app.infraestructura.rutasCarretera import CacheRutas, ProveedorOsrm
from app.motores.fabrica import SolverFactory
from app.persistencia.cargaInicial import cargarRedSemilla
from app.persistencia.conexion import obtenerSesion
from app.persistencia.repositorios.ejecucionRepository import EjecucionRepository
from app.persistencia.repositorios.redRepository import RedRepository
from app.servicios.servicioOptimizacion import ServicioOptimizacion
from app.servicios.servicioRed import ServicioRed
from app.servicios.servicioReportes import ServicioReportes
from app.servicios.servicioRutas import ServicioRutas
from app.servicios.servicioSensibilidad import ServicioSensibilidad

fabrica = SolverFactory()
cacheRutas = CacheRutas()
proveedorRutas = ProveedorOsrm()


def serializarComparacion(comparacion, inst) -> dict:
    return comparacionADto(comparacion, inst).model_dump(mode="json")


def obtenerServicioRed(sesion: Session = Depends(obtenerSesion)) -> ServicioRed:
    return ServicioRed(RedRepository(sesion), ValidadorRed(), cargarRedSemilla)


def obtenerServicioOptimizacion(sesion: Session = Depends(obtenerSesion)) -> ServicioOptimizacion:
    return ServicioOptimizacion(RedRepository(sesion), EjecucionRepository(sesion), fabrica, ValidadorRed(),
                                InstanciaBuilder(), serializarComparacion)


def obtenerServicioSensibilidad(sesion: Session = Depends(obtenerSesion)) -> ServicioSensibilidad:
    solverExacto = fabrica.exacto()
    return ServicioSensibilidad(RedRepository(sesion), solverExacto, AnalizadorSensibilidad(),
                                SimuladorEscenarios(solverExacto), ValidadorRed(), InstanciaBuilder())


def obtenerServicioReportes(sesion: Session = Depends(obtenerSesion)) -> ServicioReportes:
    return ServicioReportes(EjecucionRepository(sesion))


def obtenerServicioRutas(sesion: Session = Depends(obtenerSesion)) -> ServicioRutas:
    return ServicioRutas(RedRepository(sesion), cacheRutas, proveedorRutas)
