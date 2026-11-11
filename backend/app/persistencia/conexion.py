"""Motor y sesión de SQLAlchemy.

La aplicación llama a configurarBaseDatos(url) al iniciar; las pruebas usan
una base en memoria ("sqlite://").
"""

from typing import Iterator, Optional

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


_motor: Optional[Engine] = None
_fabricaSesiones: Optional[sessionmaker] = None


def configurarBaseDatos(url: str) -> Engine:
    """Crea el motor, las tablas y la fábrica de sesiones."""
    global _motor, _fabricaSesiones
    opciones = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
    if url in ("sqlite://", "sqlite:///:memory:"):
        opciones["poolclass"] = StaticPool  # una sola conexión: la base en memoria no se pierde
    _motor = create_engine(url, **opciones)
    _fabricaSesiones = sessionmaker(bind=_motor, expire_on_commit=False)

    from app.persistencia import modelos  # noqa: F401  registra las tablas en Base

    Base.metadata.create_all(_motor)
    return _motor


def nuevaSesion() -> Session:
    if _fabricaSesiones is None:
        raise RuntimeError("La base de datos no está configurada: llame a configurarBaseDatos().")
    return _fabricaSesiones()


def obtenerSesion() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por petición."""
    sesion = nuevaSesion()
    try:
        yield sesion
    finally:
        sesion.close()
