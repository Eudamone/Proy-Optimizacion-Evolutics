# Se configura con las variables de entorno ECORESIDUOS_DB y ECORESIDUOS_CORS.

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
