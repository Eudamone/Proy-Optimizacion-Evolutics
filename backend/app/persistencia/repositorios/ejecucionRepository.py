"""EjecucionRepository: guarda las comparaciones y consulta el historial.

Aquí, y solo aquí, se decide cómo una Comparacion del dominio se convierte en una fila.
"""

from dataclasses import asdict
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.persistencia.modelos import EjecucionModelo
from app.persistencia.repositorios.interfaces import IEjecucionRepository

CAMPOS_RESUMEN = ("id", "fecha", "tipo", "z_exacto", "z_ag_mejor", "z_ag_promedio", "desv_estandar",
                  "gap_pct", "tiempo_exacto_s", "tiempo_ag_s", "corridas", "parametros")


class EjecucionRepository(IEjecucionRepository):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardarComparacion(self, comparacion, parametros, corridas: int, detalle: dict) -> int:
        return self.guardar({
            "tipo": "comparacion",
            "z_exacto": comparacion.z_exacto,
            "z_ag_mejor": comparacion.z_ag_mejor,
            "z_ag_promedio": comparacion.z_ag_promedio,
            "desv_estandar": comparacion.desv_estandar,
            "gap_pct": comparacion.gapPct(),
            "tiempo_exacto_s": comparacion.tiempos["exacto"],
            "tiempo_ag_s": comparacion.tiempos["genetico_promedio"],
            "corridas": corridas,
            "parametros": asdict(parametros),
            "resultado": detalle,
        })

    def guardar(self, datos: dict) -> int:
        fila = EjecucionModelo(**datos)
        self.sesion.add(fila)
        self.sesion.commit()
        return fila.id

    def listar(self, limite: int = 50) -> list[dict]:
        filas = self.sesion.scalars(select(EjecucionModelo).order_by(EjecucionModelo.id.desc()).limit(limite))
        return [self._resumen(f) for f in filas]

    def obtener(self, ejecucionId: int) -> Optional[dict]:
        fila = self.sesion.get(EjecucionModelo, ejecucionId)
        if fila is None:
            return None
        datos = self._resumen(fila)
        datos["resultado"] = fila.resultado
        return datos

    @staticmethod
    def _resumen(fila: EjecucionModelo) -> dict:
        return {campo: getattr(fila, campo) for campo in CAMPOS_RESUMEN}
