from typing import Callable, Optional

from app.analisis.comparador import Comparacion, Comparador
from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.dominio.solucion import Solucion
from app.dominio.validador import ValidadorRed
from app.genetico.parametros import ParametrosAG
from app.motores.fabrica import SolverFactory
from app.persistencia.repositorios.interfaces import IEjecucionRepository, IRedRepository
from app.servicios.errores import ErrorNegocio

Serializador = Callable[[Comparacion, InstanciaTransporte], dict]


class ServicioOptimizacion:
    def __init__(self, repositorioRed: IRedRepository, repositorioEjecuciones: IEjecucionRepository,
                 fabrica: SolverFactory, validador: ValidadorRed, builder: InstanciaBuilder,
                 serializador: Optional[Serializador] = None):
        self.repositorioRed = repositorioRed
        self.repositorioEjecuciones = repositorioEjecuciones
        self.fabrica = fabrica
        self.validador = validador
        self.builder = builder
        self.serializador = serializador or (lambda comparacion, inst: {})

    def instanciaActual(self) -> InstanciaTransporte:
        red = self.repositorioRed.obtenerRed()
        errores = self.validador.validar(red)
        if errores:
            raise ErrorNegocio(errores)
        return self.builder.construir(red)

    def resolver(self, metodo: str, parametros: Optional[ParametrosAG] = None) -> tuple[Solucion, InstanciaTransporte]:
        self._validarParametros(parametros)
        inst = self.instanciaActual()
        return self.fabrica.crear(metodo, parametros).resolver(inst), inst

    def comparar(self, parametros: ParametrosAG, corridas: int) -> tuple[Comparacion, InstanciaTransporte, int]:
        self._validarParametros(parametros)
        inst = self.instanciaActual()
        comparacion = Comparador(self.fabrica).comparar(inst, parametros, corridas)
        ejecucionId = self.repositorioEjecuciones.guardarComparacion(
            comparacion, parametros, corridas, self.serializador(comparacion, inst))
        return comparacion, inst, ejecucionId

    @staticmethod
    def _validarParametros(parametros: Optional[ParametrosAG]) -> None:
        if parametros is not None:
            errores = parametros.validar()
            if errores:
                raise ErrorNegocio(errores)
