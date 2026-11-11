"""SolverFactory: crea el solver exacto (SolverTransporte) o el genético
(AlgoritmoGeneticoSolver, HU-04) a partir de su nombre.
"""

from app.motores.interfaces import ISolver


class SolverFactory:
    def exacto(self) -> ISolver:
        from app.transporte.solverTransporte import SolverTransporte
        return SolverTransporte()

    def genetico(self, parametros=None) -> ISolver:
        raise NotImplementedError("El algoritmo genético se implementa en HU-04.")

    def crear(self, metodo: str, parametros=None) -> ISolver:
        if metodo == "exacto":
            return self.exacto()
        if metodo == "genetico":
            return self.genetico(parametros)
        raise ValueError(f"Método desconocido: {metodo}. Use 'exacto' o 'genetico'.")
