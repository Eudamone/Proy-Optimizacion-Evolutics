"""ServicioReportes: consulta el historial de comparaciones guardadas."""

from app.persistencia.repositorios.interfaces import IEjecucionRepository
from app.servicios.errores import NoEncontrado


class ServicioReportes:
    def __init__(self, repositorio: IEjecucionRepository):
        self.repositorio = repositorio

    def listar(self, limite: int = 50) -> list[dict]:
        return self.repositorio.listar(limite)

    def obtener(self, ejecucionId: int) -> dict:
        ejecucion = self.repositorio.obtener(ejecucionId)
        if ejecucion is None:
            raise NoEncontrado(f"No existe la ejecución {ejecucionId}.")
        return ejecucion
