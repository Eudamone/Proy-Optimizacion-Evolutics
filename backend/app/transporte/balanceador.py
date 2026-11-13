# Agrega una fuente ficticia de costo 0 para que la oferta iguale la capacidad.

from app.dominio.instancia import InstanciaTransporte
from app.dominio.tipos import Matriz
from app.transporte.tabla import TablaTransporte

FUENTE_FICTICIA = "FICTICIA"


class Balanceador:
    def __init__(self, tolerancia: float = 1e-9):
        self.tolerancia = tolerancia

    def balancear(self, inst: InstanciaTransporte) -> InstanciaTransporte:
        oferta, capacidad = sum(inst.a), sum(inst.b)
        if oferta > capacidad + self.tolerancia:
            raise ValueError(
                f"La oferta ({oferta:g} t) supera la capacidad ({capacidad:g} t): el problema no es factible."
            )
        if capacidad - oferta <= self.tolerancia:
            return inst.conCambios()
        return inst.conCambios(
            fuentes=inst.fuentes + [FUENTE_FICTICIA],
            a=inst.a + [capacidad - oferta],
            C=[list(fila) for fila in inst.C] + [[0.0] * inst.m()],
            ficticia="fila",
        )

    def quitarFicticia(self, tabla: TablaTransporte) -> Matriz:
        x = [list(fila) for fila in tabla.x]
        if tabla.inst.ficticia == "fila":
            x = x[:-1]
        return x
