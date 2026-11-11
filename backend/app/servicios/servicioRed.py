"""ServicioRed: consulta y actualiza la red; la valida con ValidadorRed antes de guardarla."""

from app.dominio.red import RedLogistica
from app.dominio.validador import ValidadorRed
from app.persistencia.cargaInicial import cargarRedSemilla
from app.persistencia.repositorios.interfaces import IRedRepository
from app.servicios.errores import ErrorNegocio


class ServicioRed:
    def __init__(self, repositorio: IRedRepository, validador: ValidadorRed = None):
        self.repositorio = repositorio
        self.validador = validador or ValidadorRed()

    def obtenerRed(self) -> RedLogistica:
        return self.repositorio.obtenerRed()

    def validar(self, red: RedLogistica) -> list[str]:
        return self.validador.validar(red)

    def actualizarRed(self, red: RedLogistica) -> RedLogistica:
        """Guarda la red solo si cumple todas las reglas."""
        errores = self.validador.validar(red)
        if errores:
            raise ErrorNegocio(errores)
        self.repositorio.guardar(red)
        return red

    def restablecer(self) -> RedLogistica:
        """Vuelve a los datos de prueba de backend/datos/semilla."""
        red = cargarRedSemilla()
        self.repositorio.guardar(red)
        return red
