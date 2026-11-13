from dataclasses import dataclass, field


@dataclass
class Cromosoma:
    genes: list[float]
    costo: float = float("inf")    # Z del reparto decodificado
    exceso: float = 0.0            # toneladas por encima de la capacidad (suma de todas las plantas)
    aptitud: float = 0.0           # 1 / (1 + Z + lambda * exceso); mayor es mejor

    def copiar(self) -> "Cromosoma":
        return Cromosoma(list(self.genes), self.costo, self.exceso, self.aptitud)

    def penalizado(self, lambda_: float) -> float:
        return self.costo + lambda_ * self.exceso


@dataclass
class Poblacion:
    individuos: list[Cromosoma] = field(default_factory=list)

    def ordenar(self) -> None:
        self.individuos.sort(key=lambda c: c.aptitud, reverse=True)

    def mejor(self) -> Cromosoma:
        return max(self.individuos, key=lambda c: c.aptitud)

    def costoPromedio(self) -> float:
        return sum(c.costo for c in self.individuos) / len(self.individuos)

    def __len__(self) -> int:
        return len(self.individuos)
