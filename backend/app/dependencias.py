"""Inyección de dependencias (Depends): una sesión por petición y, con ella, los
repositorios y servicios que usan los controladores.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.persistencia.conexion import obtenerSesion
from app.persistencia.repositorios.ejecucionRepository import EjecucionRepository
from app.persistencia.repositorios.redRepository import RedRepository
from app.servicios.servicioOptimizacion import ServicioOptimizacion
from app.servicios.servicioRed import ServicioRed
from app.servicios.servicioReportes import ServicioReportes
from app.servicios.servicioSensibilidad import ServicioSensibilidad


def obtenerServicioRed(sesion: Session = Depends(obtenerSesion)) -> ServicioRed:
    return ServicioRed(RedRepository(sesion))


def obtenerServicioOptimizacion(sesion: Session = Depends(obtenerSesion)) -> ServicioOptimizacion:
    return ServicioOptimizacion(RedRepository(sesion), EjecucionRepository(sesion))


def obtenerServicioSensibilidad(sesion: Session = Depends(obtenerSesion)) -> ServicioSensibilidad:
    return ServicioSensibilidad(RedRepository(sesion))


def obtenerServicioReportes(sesion: Session = Depends(obtenerSesion)) -> ServicioReportes:
    return ServicioReportes(EjecucionRepository(sesion))
