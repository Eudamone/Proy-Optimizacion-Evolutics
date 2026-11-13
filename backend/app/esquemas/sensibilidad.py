import math
from typing import Optional

from pydantic import BaseModel, Field

from app.analisis.escenarios import PasoEscenario, TipoEscenario
from app.analisis.sensibilidad import Rango, ResultadoSensibilidad
from app.dominio.instancia import InstanciaTransporte
from app.dominio.red import RedLogistica
from app.dominio.solucion import Solucion


class EscenarioDTO(BaseModel):
    tipo: TipoEscenario
    objetivo_id: Optional[str] = Field(None, description="Id de la planta o agroempresa; vacío = todas")
    delta_min: float = -20
    delta_max: float = 20
    pasos: int = Field(5, ge=1, le=41)


class SolicitudSensibilidad(BaseModel):
    escenario: Optional[EscenarioDTO] = None


class RangoDTO(BaseModel):
    actual: float
    minimo: Optional[float]
    maximo: Optional[float]


class OfertaSensibilidadDTO(BaseModel):
    id: str
    nombre: str
    precio_sombra: float
    rango: Optional[RangoDTO]


class CapacidadSensibilidadDTO(BaseModel):
    id: str
    nombre: str
    precio_sombra: float
    ahorro_por_tonelada: float
    usada_t: float
    rango: Optional[RangoDTO]


class RutaSensibilidadDTO(BaseModel):
    agroempresa_id: str
    planta_id: str
    costo_unitario: float
    costo_reducido: float
    toneladas: float
    rango: RangoDTO


class PasoEscenarioDTO(BaseModel):
    delta: float
    costo_total: Optional[float]
    cambia_base: bool
    factible: bool
    mensaje: str = ""


class ResultadoSensibilidadDTO(BaseModel):
    costo_total: float
    ofertas: list[OfertaSensibilidadDTO]
    capacidades: list[CapacidadSensibilidadDTO]
    rutas: list[RutaSensibilidadDTO]
    escenario: Optional[list[PasoEscenarioDTO]] = None


def _limite(valor: float) -> Optional[float]:
    return None if math.isinf(valor) else valor


def rangoADto(rango: Optional[Rango]) -> Optional[RangoDTO]:
    if rango is None:
        return None
    return RangoDTO(actual=rango.actual, minimo=_limite(rango.minimo), maximo=_limite(rango.maximo))


def sensibilidadADto(red: RedLogistica, inst: InstanciaTransporte, sol: Solucion, r: ResultadoSensibilidad,
                     pasos: Optional[list[PasoEscenario]] = None) -> ResultadoSensibilidadDTO:
    nombresAgro = {a.id: a.nombre for a in red.agroempresas}
    nombresPlanta = {p.id: p.nombre for p in red.plantas}
    ofertas = [
        OfertaSensibilidadDTO(id=f, nombre=nombresAgro.get(f, f), precio_sombra=r.precio_sombra_oferta[i],
                              rango=rangoADto(r.rangos_oferta[i] if r.rangos_oferta else None))
        for i, f in enumerate(inst.fuentes)
    ]
    ahorros = r.ahorroPorCapacidad()
    capacidades = [
        CapacidadSensibilidadDTO(id=p, nombre=nombresPlanta.get(p, p), precio_sombra=r.precio_sombra_capacidad[j],
                                 ahorro_por_tonelada=ahorros[j], usada_t=sum(fila[j] for fila in sol.x),
                                 rango=rangoADto(r.rangos_capacidad[j] if r.rangos_capacidad else None))
        for j, p in enumerate(inst.plantas)
    ]
    rutas = [
        RutaSensibilidadDTO(agroempresa_id=inst.fuentes[i], planta_id=inst.plantas[j],
                            costo_unitario=inst.C[i][j], costo_reducido=r.costos_reducidos[i][j],
                            toneladas=sol.x[i][j], rango=rangoADto(rango))
        for (i, j), rango in sorted(r.rangos_costo.items())
        if inst.C[i][j] < inst.gran_m
    ]
    escenario = None
    if pasos is not None:
        escenario = [PasoEscenarioDTO(delta=p.delta, costo_total=p.costo_total, cambia_base=p.cambia_base,
                                      factible=p.factible, mensaje=p.mensaje) for p in pasos]
    return ResultadoSensibilidadDTO(costo_total=sol.costo_total, ofertas=ofertas, capacidades=capacidades,
                                    rutas=rutas, escenario=escenario)
