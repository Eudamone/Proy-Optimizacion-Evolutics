import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.dominio.instancia import InstanciaBuilder  # noqa: E402
from app.persistencia.cargaInicial import cargarRedSemilla  # noqa: E402


@pytest.fixture
def redSemilla():
    return cargarRedSemilla()


@pytest.fixture
def instanciaSemilla(redSemilla):
    return InstanciaBuilder().construir(redSemilla)
