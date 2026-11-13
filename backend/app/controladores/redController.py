from fastapi import APIRouter, Depends

from app.dependencias import obtenerServicioRed, obtenerServicioRutas
from app.esquemas.red import RedDTO, ResumenRedDTO, RutasCarreteraDTO, dtoARed, redADto, resumenRed, rutasCarreteraADto
from app.infraestructura.rutasCarretera import FUENTE
from app.servicios.servicioRed import ServicioRed
from app.servicios.servicioRutas import ServicioRutas

router = APIRouter(prefix="/red", tags=["Red"])


@router.get("", response_model=RedDTO, summary="Red actual")
def obtenerRed(servicio: ServicioRed = Depends(obtenerServicioRed)):
    return redADto(servicio.obtenerRed())


@router.get("/resumen", response_model=ResumenRedDTO, summary="Totales y validación de la red actual")
def obtenerResumen(servicio: ServicioRed = Depends(obtenerServicioRed)):
    red = servicio.obtenerRed()
    return resumenRed(red, servicio.validar(red))


@router.get("/rutas-carretera", response_model=RutasCarreteraDTO,
            summary="Trazado por carretera de cada agroempresa a cada planta (para el mapa)")
def obtenerRutasCarretera(descargar: bool = False, servicio: ServicioRutas = Depends(obtenerServicioRutas)):
    """Con descargar=true pide a OSRM los trazados que falten y los guarda."""
    return rutasCarreteraADto(servicio.rutasDeLaRed(descargar=descargar), FUENTE)


@router.put("", response_model=ResumenRedDTO, summary="Reemplazar la red (se valida antes de guardar)")
def actualizarRed(dto: RedDTO, servicio: ServicioRed = Depends(obtenerServicioRed)):
    red = servicio.actualizarRed(dtoARed(dto))
    return resumenRed(red, [])


@router.post("/restablecer", response_model=ResumenRedDTO, summary="Volver a los datos de prueba")
def restablecerRed(servicio: ServicioRed = Depends(obtenerServicioRed)):
    red = servicio.restablecer()
    return resumenRed(red, servicio.validar(red))
