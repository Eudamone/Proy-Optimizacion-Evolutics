"""Esquemas de optimización: parámetros del AG, soluciones y comparación."""

from dataclasses import asdict
from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.analisis.comparador import Comparacion
from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import Solucion
from app.genetico.parametros import ParametrosAG


class ParametrosAGDTO(BaseModel):
    poblacion: int = Field(100, ge=2)
    generaciones: int = Field(300, ge=1)
    p_cruce: float = Field(0.8, ge=0, le=1)
    p_mutacion: float = Field(0.05, ge=0, le=1)
    elitismo: int = Field(2, ge=0)
    k_torneo: int = Field(3, ge=1)
    lambda_: Optional[float] = Field(None, gt=0)
    seleccion: Literal["torneo", "ruleta"] = "torneo"
    cruce: Literal["un_punto", "dos_puntos"] = "un_punto"
    mutacion: Literal["uniforme", "poda"] = "poda"
    semilla: Optional[int] = None

    def aDominio(self) -> ParametrosAG:
        return ParametrosAG(**self.model_dump())


class SolicitudResolver(BaseModel):
    metodo: Literal["exacto", "genetico"] = "exacto"
    parametros: Optional[ParametrosAGDTO] = None


class SolicitudComparacion(BaseModel):
    parametros: ParametrosAGDTO = Field(default_factory=ParametrosAGDTO)
    corridas: int = Field(10, ge=1, le=50)


class FlujoDTO(BaseModel):
    agroempresa_id: str
    planta_id: str
    toneladas: float
    costo_unitario: float


class HistorialDTO(BaseModel):
    mejor_costo: list[float]
    costo_promedio: list[float]


class SolucionDTO(BaseModel):
    metodo: str
    costo_total: float
    tiempo_s: float
    iteraciones: int
    factible: bool
    fuentes: list[str]
    plantas: list[str]
    x: list[list[float]]
    flujos: list[FlujoDTO]
    costo_inicial: Optional[float] = Field(None, description="Costo de Vogel (solo método exacto)")
    historial: Optional[HistorialDTO] = Field(None, description="Convergencia (solo AG)")


class ComparacionDTO(BaseModel):
    ejecucion_id: Optional[int] = None
    z_exacto: float
    z_ag_mejor: float
    z_ag_promedio: float
    desv_estandar: float
    gap_pct: float
    gap_promedio_pct: float
    tiempos: dict[str, float]
    costos_ag: list[float]
    gaps_ag: list[float]
    semillas: list[int]
    exacta: SolucionDTO
    mejor_genetica: SolucionDTO


def solucionADto(sol: Solucion, inst: InstanciaTransporte) -> SolucionDTO:
    flujos = [
        FlujoDTO(agroempresa_id=f, planta_id=p, toneladas=t,
                 costo_unitario=inst.C[inst.fuentes.index(f)][inst.plantas.index(p)])
        for f, p, t in sol.flujos(inst.fuentes, inst.plantas)
    ]
    historial = None
    if sol.historial is not None:
        historial = HistorialDTO(mejor_costo=sol.historial.mejor_costo,
                                 costo_promedio=sol.historial.costo_promedio)
    return SolucionDTO(
        metodo=sol.metodo,
        costo_total=sol.costo_total,
        tiempo_s=sol.tiempo_s,
        iteraciones=sol.iteraciones,
        factible=sol.factible,
        fuentes=inst.fuentes,
        plantas=inst.plantas,
        x=sol.x,
        flujos=flujos,
        costo_inicial=sol.dual.costoInicial if sol.dual is not None else None,
        historial=historial,
    )


def comparacionADto(comp: Comparacion, inst: InstanciaTransporte, ejecucionId: Optional[int] = None) -> ComparacionDTO:
    return ComparacionDTO(
        ejecucion_id=ejecucionId,
        z_exacto=comp.z_exacto,
        z_ag_mejor=comp.z_ag_mejor,
        z_ag_promedio=comp.z_ag_promedio,
        desv_estandar=comp.desv_estandar,
        gap_pct=comp.gapPct(),
        gap_promedio_pct=comp.gapPromedioPct(),
        tiempos=comp.tiempos,
        costos_ag=comp.costos_ag,
        gaps_ag=comp.gapsPorCorrida(),
        semillas=comp.semillas,
        exacta=solucionADto(comp.solucion_exacta, inst),
        mejor_genetica=solucionADto(comp.mejor_genetica, inst),
    )


def parametrosADict(p: ParametrosAG) -> dict:
    return asdict(p)
