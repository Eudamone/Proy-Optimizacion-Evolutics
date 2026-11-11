"""Tablas ORM: agroempresas, plantas, rutas, parametros y ejecuciones."""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.persistencia.conexion import Base


class AgroempresaModelo(Base):
    __tablename__ = "agroempresas"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    orden: Mapped[int] = mapped_column(Integer)
    nombre: Mapped[str] = mapped_column(String(120))
    municipio: Mapped[str] = mapped_column(String(80))
    tipo_residuo: Mapped[str] = mapped_column(String(20))
    oferta_t: Mapped[float] = mapped_column(Float)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class PlantaModelo(Base):
    __tablename__ = "plantas"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    orden: Mapped[int] = mapped_column(Integer)
    nombre: Mapped[str] = mapped_column(String(120))
    municipio: Mapped[str] = mapped_column(String(80))
    capacidad_t: Mapped[float] = mapped_column(Float)
    costo_operacion: Mapped[float] = mapped_column(Float)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)


class RutaModelo(Base):
    __tablename__ = "rutas"

    agroempresa_id: Mapped[str] = mapped_column(ForeignKey("agroempresas.id", ondelete="CASCADE"), primary_key=True)
    planta_id: Mapped[str] = mapped_column(ForeignKey("plantas.id", ondelete="CASCADE"), primary_key=True)
    distancia_km: Mapped[float] = mapped_column(Float)
    habilitada: Mapped[bool] = mapped_column(Boolean, default=True)


class ParametrosModelo(Base):
    __tablename__ = "parametros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)  # una sola fila
    tarifa_t_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precio_tonelada: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    gran_m: Mapped[float] = mapped_column(Float)


class EjecucionModelo(Base):
    __tablename__ = "ejecuciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    tipo: Mapped[str] = mapped_column(String(20))            # "comparacion"
    z_exacto: Mapped[float] = mapped_column(Float)
    z_ag_mejor: Mapped[float] = mapped_column(Float)
    z_ag_promedio: Mapped[float] = mapped_column(Float)
    desv_estandar: Mapped[float] = mapped_column(Float)
    gap_pct: Mapped[float] = mapped_column(Float)
    tiempo_exacto_s: Mapped[float] = mapped_column(Float)
    tiempo_ag_s: Mapped[float] = mapped_column(Float)
    corridas: Mapped[int] = mapped_column(Integer)
    parametros: Mapped[dict] = mapped_column(JSON)            # ParametrosAG usados
    resultado: Mapped[dict] = mapped_column(JSON)             # detalle completo para los reportes
