from typing import Optional

from app.analisis.escenarios import MODIFICADORES, Escenario, SimuladorEscenarios, TipoEscenario
from app.analisis.sensibilidad import AnalizadorSensibilidad
from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.dominio.validador import ValidadorRed
from app.motores.interfaces import ISolver
from app.persistencia.repositorios.interfaces import IRedRepository
from app.servicios.errores import ErrorNegocio


class ServicioSensibilidad:
    def __init__(self, repositorioRed: IRedRepository, solverExacto: ISolver, analizador: AnalizadorSensibilidad,
                 simulador: SimuladorEscenarios, validador: ValidadorRed, builder: InstanciaBuilder):
        self.repositorioRed = repositorioRed
        self.solverExacto = solverExacto
        self.analizador = analizador
        self.simulador = simulador
        self.validador = validador
        self.builder = builder

    def analizar(self, escenario: Optional[dict] = None):
        """Devuelve (red, instancia, solución, resultado, pasos del escenario o None)."""
        red = self.repositorioRed.obtenerRed()
        errores = self.validador.validar(red)
        if errores:
            raise ErrorNegocio(errores)
        inst = self.builder.construir(red)
        sol = self.solverExacto.resolver(inst)
        resultado = self.analizador.analizar(sol, inst)
        pasos = None
        if escenario is not None:
            pasos = self.simulador.simular(inst, self._crearEscenario(escenario, inst))
        return red, inst, sol, resultado, pasos

    @staticmethod
    def _crearEscenario(datos: dict, inst: InstanciaTransporte) -> Escenario:
        tipo = TipoEscenario(datos["tipo"])
        modificador = MODIFICADORES[tipo]
        objetivoId = datos.get("objetivo_id")
        objetivo = None
        if objetivoId:
            lista = inst.fuentes if modificador.sobreFuentes else inst.plantas
            if objetivoId not in lista:
                raise ErrorNegocio([f"No existe {objetivoId} para un escenario de tipo {tipo.value}."])
            objetivo = lista.index(objetivoId)
        if modificador.unPasoSolo and objetivo is None:
            raise ErrorNegocio(["Para cerrar una planta hay que indicar cuál (objetivo_id)."])
        if datos.get("delta_min", -20) > datos.get("delta_max", 20):
            raise ErrorNegocio(["La variación mínima no puede ser mayor que la máxima."])
        return Escenario(tipo, objetivo, datos.get("delta_min", -20), datos.get("delta_max", 20),
                         datos.get("pasos", 5))
