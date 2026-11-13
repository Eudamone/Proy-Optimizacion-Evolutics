# Método exacto: balancear -> Vogel -> MODI -> quitar la ficticia.

import time

from app.dominio.instancia import InstanciaTransporte
from app.dominio.solucion import SolucionExacta
from app.motores.interfaces import ISolver
from app.transporte.balanceador import Balanceador
from app.transporte.modi import MetodoMODI
from app.transporte.vogel import ISolucionInicial, MetodoVogel


class SolverTransporte(ISolver):
    def __init__(self, inicial: ISolucionInicial = None, balanceador: Balanceador = None,
                 modi: MetodoMODI = None):
        self.inicial = inicial or MetodoVogel()
        self.balanceador = balanceador or Balanceador()
        self.modi = modi or MetodoMODI()

    def nombre(self) -> str:
        return "exacto"

    def resolver(self, inst: InstanciaTransporte) -> SolucionExacta:
        inicio = time.perf_counter()
        balanceada = self.balanceador.balancear(inst)
        tabla = self.inicial.construir(balanceada)
        dual = self.modi.optimizar(tabla)
        x = self.balanceador.quitarFicticia(tabla)
        x = [[0.0 if abs(valor) < 1e-9 else valor for valor in fila] for fila in x]
        tiempo = time.perf_counter() - inicio
        return SolucionExacta(
            metodo=self.nombre(),
            x=x,
            costo_total=inst.costo(x),
            tiempo_s=tiempo,
            iteraciones=dual.iteraciones,
            factible=inst.verificar(x) == [],
            dual=dual,
        )
