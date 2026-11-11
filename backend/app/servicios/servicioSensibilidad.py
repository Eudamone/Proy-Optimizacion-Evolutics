"""ServicioSensibilidad: resuelve la red actual con el método exacto, calcula la
sensibilidad y, si se pide, simula un escenario.
"""

from typing import Optional

from app.analisis.escenarios import Escenario, PasoEscenario, SimuladorEscenarios, TipoEscenario
from app.analisis.sensibilidad import AnalizadorSensibilidad, ResultadoSensibilidad
from app.dominio.instancia import InstanciaBuilder, InstanciaTransporte
from app.dominio.red import RedLogistica
from app.dominio.solucion import Solucion
from app.dominio.validador import ValidadorRed
from app.persistencia.repositorios.interfaces import IRedRepository
from app.servicios.errores import ErrorNegocio
from app.transporte.solverTransporte import SolverTransporte


class ServicioSensibilidad:
    def __init__(self, repositorioRed: IRedRepository):
        self.repositorioRed = repositorioRed
        self.solver = SolverTransporte()
        self.analizador = AnalizadorSensibilidad()

    def analizar(self, escenario: Optional[dict] = None):
        """Devuelve (red, instancia, solucion, resultado, pasos del escenario o None).

        escenario: {"tipo", "objetivo_id", "delta_min", "delta_max", "pasos"}
        """
        red = self.repositorioRed.obtenerRed()
        errores = ValidadorRed().validar(red)
        if errores:
            raise ErrorNegocio(errores)
        inst = InstanciaBuilder().construir(red)
        sol = self.solver.resolver(inst)
        resultado = self.analizador.analizar(sol, inst)
        pasos = None
        if escenario is not None:
            pasos = SimuladorEscenarios(self.solver).simular(inst, self._crearEscenario(escenario, inst))
        return red, inst, sol, resultado, pasos

    @staticmethod
    def _crearEscenario(datos: dict, inst: InstanciaTransporte) -> Escenario:
        tipo = TipoEscenario(datos["tipo"])
        objetivoId = datos.get("objetivo_id")
        objetivo = None
        if objetivoId:
            lista = inst.fuentes if tipo == TipoEscenario.OFERTA else inst.plantas
            if objetivoId not in lista:
                raise ErrorNegocio([f"No existe {objetivoId} para un escenario de tipo {tipo.value}."])
            objetivo = lista.index(objetivoId)
        if tipo == TipoEscenario.CIERRE_PLANTA and objetivo is None:
            raise ErrorNegocio(["Para cerrar una planta hay que indicar cuál (objetivo_id)."])
        if datos.get("delta_min", -20) > datos.get("delta_max", 20):
            raise ErrorNegocio(["La variación mínima no puede ser mayor que la máxima."])
        return Escenario(tipo, objetivo, datos.get("delta_min", -20), datos.get("delta_max", 20),
                         datos.get("pasos", 5))
