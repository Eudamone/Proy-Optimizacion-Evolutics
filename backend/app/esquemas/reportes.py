from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class EjecucionDTO(BaseModel):
    id: int
    fecha: datetime
    tipo: str
    z_exacto: float
    z_ag_mejor: float
    z_ag_promedio: float
    desv_estandar: float
    gap_pct: float
    tiempo_exacto_s: float
    tiempo_ag_s: float
    corridas: int
    parametros: dict[str, Any]


class EjecucionDetalleDTO(EjecucionDTO):
    resultado: Optional[dict[str, Any]] = None
