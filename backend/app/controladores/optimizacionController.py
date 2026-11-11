"""OptimizacionController: resolver con un método y comparar el exacto con el AG."""

from fastapi import APIRouter, Depends

from app.dependencias import obtenerServicioOptimizacion
from app.esquemas.optimizacion import (ComparacionDTO, SolicitudComparacion, SolicitudResolver, SolucionDTO,
                                       comparacionADto, solucionADto)
from app.servicios.servicioOptimizacion import ServicioOptimizacion

router = APIRouter(prefix="/optimizacion", tags=["Optimización"])


@router.post("/resolver", response_model=SolucionDTO, summary="Resolver con el método exacto o con el AG")
def resolver(solicitud: SolicitudResolver, servicio: ServicioOptimizacion = Depends(obtenerServicioOptimizacion)):
    parametros = solicitud.parametros.aDominio() if solicitud.parametros else None
    sol, inst = servicio.resolver(solicitud.metodo, parametros)
    return solucionADto(sol, inst)


@router.post("/comparar", response_model=ComparacionDTO,
             summary="Comparar el método exacto con varias corridas del AG (se guarda en el historial)")
def comparar(solicitud: SolicitudComparacion, servicio: ServicioOptimizacion = Depends(obtenerServicioOptimizacion)):
    def resultadoParaGuardar(comp, inst):
        return comparacionADto(comp, inst).model_dump(mode="json")

    comp, inst, ejecucionId = servicio.comparar(solicitud.parametros.aDominio(), solicitud.corridas,
                                                resultadoParaGuardar)
    return comparacionADto(comp, inst, ejecucionId)
