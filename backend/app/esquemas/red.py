"""Esquemas de la red y su conversión desde y hacia el dominio."""

from typing import Optional

from pydantic import BaseModel, Field

from app.dominio.red import Agroempresa, ParametrosEconomicos, Planta, RedLogistica, Ruta
from app.dominio.tipos import TipoResiduo


class AgroempresaDTO(BaseModel):
    id: str
    nombre: str
    municipio: str
    tipo_residuo: TipoResiduo
    oferta_t: float = Field(description="Toneladas por semana")
    lat: Optional[float] = None
    lon: Optional[float] = None


class PlantaDTO(BaseModel):
    id: str
    nombre: str
    municipio: str
    capacidad_t: float = Field(description="Toneladas por semana")
    costo_operacion: float = Field(description="Pesos por tonelada")
    activa: bool = True
    lat: Optional[float] = None
    lon: Optional[float] = None


class RutaDTO(BaseModel):
    agroempresa_id: str
    planta_id: str
    distancia_km: float
    habilitada: bool = True


class ParametrosDTO(BaseModel):
    tarifa_t_km: Optional[float] = Field(None, description="Pesos por tonelada-km")
    precio_tonelada: Optional[float] = None
    gran_m: float = 1e8


class RedDTO(BaseModel):
    agroempresas: list[AgroempresaDTO]
    plantas: list[PlantaDTO]
    rutas: list[RutaDTO]
    parametros: ParametrosDTO


class ResumenRedDTO(BaseModel):
    agroempresas: int
    plantas_activas: int
    total_oferta_t: float
    total_capacidad_t: float
    factible: bool
    errores: list[str]


def redADto(red: RedLogistica) -> RedDTO:
    return RedDTO(
        agroempresas=[AgroempresaDTO(**vars(a)) for a in red.agroempresas],
        plantas=[PlantaDTO(**vars(p)) for p in red.plantas],
        rutas=[RutaDTO(**vars(r)) for r in red.rutas],
        parametros=ParametrosDTO(**vars(red.parametros)),
    )


def dtoARed(dto: RedDTO) -> RedLogistica:
    return RedLogistica(
        agroempresas=[Agroempresa(**a.model_dump()) for a in dto.agroempresas],
        plantas=[Planta(**p.model_dump()) for p in dto.plantas],
        rutas=[Ruta(**r.model_dump()) for r in dto.rutas],
        parametros=ParametrosEconomicos(**dto.parametros.model_dump()),
    )


def resumenRed(red: RedLogistica, errores: list[str]) -> ResumenRedDTO:
    return ResumenRedDTO(
        agroempresas=len(red.agroempresas),
        plantas_activas=len(red.plantasActivas()),
        total_oferta_t=red.totalOferta(),
        total_capacidad_t=red.totalCapacidad(),
        factible=not errores,
        errores=errores,
    )
