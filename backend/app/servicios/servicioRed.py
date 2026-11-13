from typing import Callable

from app.dominio.red import RedLogistica
from app.dominio.validador import ValidadorRed
from app.persistencia.repositorios.interfaces import IRedRepository
from app.servicios.errores import ErrorNegocio


class ServicioRed:
    def __init__(self, repositorio: IRedRepository, validador: ValidadorRed,
                 fuenteSemilla: Callable[[], RedLogistica]):
        self.repositorio = repositorio
        self.validador = validador
        self.fuenteSemilla = fuenteSemilla

    def obtenerRed(self) -> RedLogistica:
        return self.repositorio.obtenerRed()

    def validar(self, red: RedLogistica) -> list[str]:
        return self.validador.validar(red)

    def actualizarRed(self, red: RedLogistica) -> RedLogistica:
        errores = self.validador.validar(red)
        if errores:
            raise ErrorNegocio(errores)
        self.repositorio.guardar(red)
        return red

    def restablecer(self) -> RedLogistica:
        red = self.fuenteSemilla()
        self.repositorio.guardar(red)
        return red
