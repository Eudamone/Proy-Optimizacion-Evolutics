from fastapi import APIRouter, Depends, Query

from app.dependencias import obtenerServicioReportes
from app.esquemas.reportes import EjecucionDetalleDTO, EjecucionDTO
from app.servicios.servicioReportes import ServicioReportes

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("", response_model=list[EjecucionDTO], summary="Historial de comparaciones (más reciente primero)")
def listar(limite: int = Query(50, ge=1, le=500), servicio: ServicioReportes = Depends(obtenerServicioReportes)):
    return servicio.listar(limite)


@router.get("/{ejecucionId}", response_model=EjecucionDetalleDTO, summary="Detalle de una comparación")
def obtener(ejecucionId: int, servicio: ServicioReportes = Depends(obtenerServicioReportes)):
    return servicio.obtener(ejecucionId)
