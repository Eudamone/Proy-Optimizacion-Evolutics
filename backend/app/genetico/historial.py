"""HistorialConvergencia: mejor costo y costo promedio de cada generación."""

from dataclasses import dataclass, field

from app.genetico.cromosoma import Poblacion


@dataclass
class HistorialConvergencia:
    mejor_costo: list[float] = field(default_factory=list)
    costo_promedio: list[float] = field(default_factory=list)
    mejor_exceso: list[float] = field(default_factory=list)

    def registrar(self, pob: Poblacion) -> None:
        mejor = pob.mejor()
        self.mejor_costo.append(mejor.costo)
        self.costo_promedio.append(pob.costoPromedio())
        self.mejor_exceso.append(mejor.exceso)

    def generaciones(self) -> int:
        return len(self.mejor_costo)
