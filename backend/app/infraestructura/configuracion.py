"""Configuración: ruta de la base de datos y orígenes permitidos para la interfaz.

Se puede cambiar con variables de entorno:
  ECORESIDUOS_DB    URL de SQLAlchemy (por defecto sqlite en backend/datos/ecoresiduos.db)
  ECORESIDUOS_CORS  orígenes separados por coma (por defecto la interfaz de Streamlit)
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

CARPETA_DATOS = Path(__file__).resolve().parents[2] / "datos"


@dataclass
class Configuracion:
    urlBaseDatos: str = field(
        default_factory=lambda: os.getenv("ECORESIDUOS_DB", f"sqlite:///{CARPETA_DATOS / 'ecoresiduos.db'}")
    )
    origenesPermitidos: list[str] = field(
        default_factory=lambda: os.getenv("ECORESIDUOS_CORS", "http://localhost:8501").split(",")
    )
    corridasPorDefecto: int = 10


def obtenerConfiguracion() -> Configuracion:
    return Configuracion()
