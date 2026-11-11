"""ServicioOptimizacion: arma la instancia desde la red guardada, resuelve con un
método o compara ambos, y guarda cada comparación en el historial.
"""

from typing import Optional

from app.analisis.comparador import Comparacion, Comparador
from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.dominio.solucion import Solucion
from app.dominio.validador import ValidadorRed
from app.genetico.parametros import ParametrosAG
from app.motores.fabrica import SolverFactory
from app.persistencia.repositorios.interfaces import IEjecucionRepository, IRedRepository
from app.servicios.errores import ErrorNegocio


class ServicioOptimizacion:
    def __init__(self, repositorioRed: IRedRepository, repositorioEjecuciones: IEjecucionRepository,
                 fabrica: SolverFactory = None):
        self.repositorioRed = repositorioRed
        self.repositorioEjecuciones = repositorioEjecuciones
        self.fabrica = fabrica or SolverFactory()
        self.validador = ValidadorRed()
        self.builder = InstanciaBuilder()

    def instanciaActual(self) -> InstanciaTransporte:
        red = self.repositorioRed.obtenerRed()
        errores = self.validador.validar(red)
        if errores:
            raise ErrorNegocio(errores)
        return self.builder.construir(red)

    def resolver(self, metodo: str, parametros: Optional[ParametrosAG] = None) -> tuple[Solucion, InstanciaTransporte]:
        if parametros is not None:
            errores = parametros.validar()
            if errores:
                raise ErrorNegocio(errores)
        inst = self.instanciaActual()
        solver = self.fabrica.crear(metodo, parametros)
        return solver.resolver(inst), inst

    def comparar(self, parametros: ParametrosAG, corridas: int,
                 resultadoParaGuardar=None) -> tuple[Comparacion, InstanciaTransporte, int]:
        errores = parametros.validar()
        if errores:
            raise ErrorNegocio(errores)
        inst = self.instanciaActual()
        comparacion = Comparador(self.fabrica).comparar(inst, parametros, corridas)
        resultado = resultadoParaGuardar(comparacion, inst) if resultadoParaGuardar else {}
        ejecucionId = self.repositorioEjecuciones.guardar({
            "tipo": "comparacion",
            "z_exacto": comparacion.z_exacto,
            "z_ag_mejor": comparacion.z_ag_mejor,
            "z_ag_promedio": comparacion.z_ag_promedio,
            "desv_estandar": comparacion.desv_estandar,
            "gap_pct": comparacion.gapPct(),
            "tiempo_exacto_s": comparacion.tiempos["exacto"],
            "tiempo_ag_s": comparacion.tiempos["genetico_promedio"],
            "corridas": corridas,
            "parametros": vars(parametros).copy(),
            "resultado": resultado,
        })
        return comparacion, inst, ejecucionId
