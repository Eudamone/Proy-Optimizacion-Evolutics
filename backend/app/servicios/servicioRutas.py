import math
import time
from dataclasses import dataclass, field
from typing import Optional

from app.dominio.red import RedLogistica
from app.infraestructura.rutasCarretera import CacheRutas, IProveedorRutas, RutaCarretera, SinConexion
from app.persistencia.repositorios.interfaces import IRedRepository

DISTANCIA_MINIMA_KM = 0.5  # agroempresa y planta en el mismo punto: no hay nada que trazar


@dataclass
class TramoCarretera:
    agroempresa_id: str
    planta_id: str
    ruta: RutaCarretera


@dataclass
class ResultadoRutas:
    tramos: list[TramoCarretera] = field(default_factory=list)
    faltantes: int = 0
    sin_conexion: bool = False


def _distanciaKm(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distancia en línea recta (haversine)."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(h))


class ServicioRutas:
    def __init__(self, repositorio: IRedRepository, cache: CacheRutas, proveedor: IProveedorRutas,
                 presupuesto_s: Optional[float] = None, pausa_s: float = 0.4):
        self.repositorio = repositorio
        self.cache = cache
        self.proveedor = proveedor
        self.presupuesto_s = presupuesto_s
        self.pausa_s = pausa_s

    def rutasDeLaRed(self, red: Optional[RedLogistica] = None, descargar: bool = True,
                     alAvanzar=None) -> ResultadoRutas:
        red = red or self.repositorio.obtenerRed()
        pares = [(a, p) for a in red.agroempresas for p in red.plantas
                 if None not in (a.lat, a.lon, p.lat, p.lon)
                 and _distanciaKm((a.lat, a.lon), (p.lat, p.lon)) >= DISTANCIA_MINIMA_KM]
        resultado = ResultadoRutas()
        pendientes = []
        for a, p in pares:
            ruta = self.cache.obtener((a.lat, a.lon), (p.lat, p.lon))
            if ruta:
                resultado.tramos.append(TramoCarretera(a.id, p.id, ruta))
            else:
                pendientes.append((a, p))

        if not descargar:
            resultado.faltantes = len(pendientes)
            return resultado
        inicio, nuevas = time.monotonic(), 0
        for i, (a, p) in enumerate(pendientes):
            if self.presupuesto_s is not None and time.monotonic() - inicio > self.presupuesto_s:
                resultado.faltantes = len(pendientes) - i
                break
            try:
                ruta = self.proveedor.trazar((a.lat, a.lon), (p.lat, p.lon))
            except SinConexion:
                resultado.sin_conexion = True
                resultado.faltantes = len(pendientes) - i
                break
            if ruta:
                self.cache.agregar((a.lat, a.lon), (p.lat, p.lon), ruta)
                resultado.tramos.append(TramoCarretera(a.id, p.id, ruta))
                nuevas += 1
            if alAvanzar:
                alAvanzar(i + 1, len(pendientes))
            if i < len(pendientes) - 1:
                time.sleep(self.pausa_s)  # el servidor público pide no saturarlo
        if nuevas:
            self.cache.escribir()
        return resultado
