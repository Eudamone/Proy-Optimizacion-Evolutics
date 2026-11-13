from dataclasses import dataclass, field
from typing import Optional

from app.dominio.tipos import TipoResiduo


@dataclass
class Agroempresa:
    id: str
    nombre: str
    municipio: str
    tipo_residuo: TipoResiduo
    oferta_t: float
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class Planta:
    id: str
    nombre: str
    municipio: str
    capacidad_t: float
    costo_operacion: float
    activa: bool = True
    lat: Optional[float] = None
    lon: Optional[float] = None


@dataclass
class Ruta:
    agroempresa_id: str
    planta_id: str
    distancia_km: float
    habilitada: bool = True


@dataclass
class ParametrosEconomicos:
    tarifa_t_km: Optional[float] = None
    precio_tonelada: Optional[float] = None
    gran_m: float = 1e8


@dataclass
class RedLogistica:
    agroempresas: list[Agroempresa] = field(default_factory=list)
    plantas: list[Planta] = field(default_factory=list)
    rutas: list[Ruta] = field(default_factory=list)
    parametros: ParametrosEconomicos = field(default_factory=ParametrosEconomicos)

    # ---- consultas ----

    def agroempresa(self, agroempresaId: str) -> Agroempresa:
        for a in self.agroempresas:
            if a.id == agroempresaId:
                return a
        raise KeyError(f"No existe la agroempresa {agroempresaId}")

    def planta(self, plantaId: str) -> Planta:
        for p in self.plantas:
            if p.id == plantaId:
                return p
        raise KeyError(f"No existe la planta {plantaId}")

    def ruta(self, agroempresaId: str, plantaId: str) -> Ruta:
        for r in self.rutas:
            if r.agroempresa_id == agroempresaId and r.planta_id == plantaId:
                return r
        raise KeyError(f"No existe la ruta {agroempresaId} -> {plantaId}")

    def distancia(self, agroempresaId: str, plantaId: str) -> float:
        return self.ruta(agroempresaId, plantaId).distancia_km

    def totalOferta(self) -> float:
        return sum(a.oferta_t for a in self.agroempresas)

    def totalCapacidad(self) -> float:
        return sum(p.capacidad_t for p in self.plantas if p.activa)

    def plantasActivas(self) -> list[Planta]:
        return [p for p in self.plantas if p.activa]

    # ---- cambios ----

    def agregarAgroempresa(self, agroempresa: Agroempresa, distancias: list[float]) -> None:
        if any(a.id == agroempresa.id for a in self.agroempresas):
            raise ValueError(f"Ya existe la agroempresa {agroempresa.id}")
        if len(distancias) != len(self.plantas):
            raise ValueError(
                f"Se esperaban {len(self.plantas)} distancias (una por planta) y llegaron {len(distancias)}"
            )
        self.agroempresas.append(agroempresa)
        for planta, d in zip(self.plantas, distancias):
            self.rutas.append(Ruta(agroempresa.id, planta.id, float(d)))

    def agregarPlanta(self, planta: Planta, distancias: list[float]) -> None:
        if any(p.id == planta.id for p in self.plantas):
            raise ValueError(f"Ya existe la planta {planta.id}")
        if len(distancias) != len(self.agroempresas):
            raise ValueError(
                f"Se esperaban {len(self.agroempresas)} distancias (una por agroempresa) y llegaron {len(distancias)}"
            )
        self.plantas.append(planta)
        for agro, d in zip(self.agroempresas, distancias):
            self.rutas.append(Ruta(agro.id, planta.id, float(d)))

    def quitarPlanta(self, plantaId: str) -> None:
        self.planta(plantaId)
        self.plantas = [p for p in self.plantas if p.id != plantaId]
        self.rutas = [r for r in self.rutas if r.planta_id != plantaId]

    def quitarAgroempresa(self, agroempresaId: str) -> None:
        self.agroempresa(agroempresaId)
        self.agroempresas = [a for a in self.agroempresas if a.id != agroempresaId]
        self.rutas = [r for r in self.rutas if r.agroempresa_id != agroempresaId]
