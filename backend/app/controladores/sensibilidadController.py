from fastapi import APIRouter, Depends

from app.dependencias import obtenerServicioSensibilidad
from app.esquemas.sensibilidad import ResultadoSensibilidadDTO, SolicitudSensibilidad, sensibilidadADto
from app.servicios.servicioSensibilidad import ServicioSensibilidad

router = APIRouter(prefix="/sensibilidad", tags=["Sensibilidad"])


@router.post("", response_model=ResultadoSensibilidadDTO,
             summary="Sensibilidad de la solución óptima y, opcionalmente, un escenario")
def analizar(solicitud: SolicitudSensibilidad = SolicitudSensibilidad(),
             servicio: ServicioSensibilidad = Depends(obtenerServicioSensibilidad)):
    escenario = solicitud.escenario.model_dump(mode="json") if solicitud.escenario else None
    red, inst, sol, resultado, pasos = servicio.analizar(escenario)
    return sensibilidadADto(red, inst, sol, resultado, pasos)
