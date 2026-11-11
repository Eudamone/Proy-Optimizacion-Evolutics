"""Configuración de pytest: permite importar el paquete `app` al ejecutar
`pytest` desde la carpeta backend y comparte datos de prueba entre archivos.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.dominio.instancia import InstanciaBuilder  # noqa: E402
from app.persistencia.cargaInicial import cargarRedSemilla  # noqa: E402


@pytest.fixture
def redSemilla():
    """Red de prueba: 10 agroempresas y 4 plantas del Meta."""
    return cargarRedSemilla()


@pytest.fixture
def instanciaSemilla(redSemilla):
    return InstanciaBuilder().construir(redSemilla)
