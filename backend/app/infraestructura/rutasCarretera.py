"""Rutas por carretera entre agroempresas y plantas: servicio web OSRM y su caché en JSON.

OSRM (Open Source Routing Machine) es un servicio público y gratuito, con datos de
OpenStreetMap, que devuelve el trazado por carretera, la distancia y la duración entre
dos puntos. Aquí solo se usa para dibujar el mapa: el modelo de transporte sigue
usando las distancias de la red.

Los trazados quedan guardados en datos/semilla/rutasCarretera.json, así el mapa
muestra las carreteras aunque no haya internet.

Variables de entorno:
  ECORESIDUOS_OSRM   URL del servidor OSRM (por defecto el servidor público)
  ECORESIDUOS_RUTAS  archivo de la caché (por defecto datos/semilla/rutasCarretera.json)
"""

import json
import os
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import httpx

from app.infraestructura.configuracion import CARPETA_DATOS

URL_OSRM = os.getenv("ECORESIDUOS_OSRM", "https://router.project-osrm.org")
ARCHIVO_RUTAS = Path(os.getenv("ECORESIDUOS_RUTAS", str(CARPETA_DATOS / "semilla" / "rutasCarretera.json")))
FUENTE = "OSRM (router.project-osrm.org) con datos de OpenStreetMap"

Punto = tuple[float, float]  # (lat, lon)


@dataclass
class RutaCarretera:
    puntos: list[Punto]
    distancia_km: float
    duracion_min: float


class SinConexion(Exception):
    """El servicio de rutas no respondió (sin internet, caído o bloqueado)."""


class IProveedorRutas(ABC):
    @abstractmethod
    def trazar(self, origen: Punto, destino: Punto) -> Optional[RutaCarretera]:
        """Trazado por carretera; None si no hay carretera entre los puntos. Lanza SinConexion."""


class ProveedorOsrm(IProveedorRutas):
    """Cliente del servicio /route de OSRM. Tras un fallo de conexión no vuelve a
    intentar durante `esperaTrasFallo` segundos, para no demorar cada petición sin internet."""

    def __init__(self, urlBase: str = URL_OSRM, tiempoMaximo: float = 6.0, esperaTrasFallo: float = 15.0):
        self.urlBase = urlBase.rstrip("/")
        self.tiempoMaximo = tiempoMaximo
        self.esperaTrasFallo = esperaTrasFallo
        self._sinConexionHasta = 0.0

    def trazar(self, origen: Punto, destino: Punto) -> Optional[RutaCarretera]:
        if time.monotonic() < self._sinConexionHasta:
            raise SinConexion("El servicio de rutas no respondió hace poco.")
        url = f"{self.urlBase}/route/v1/driving/{origen[1]},{origen[0]};{destino[1]},{destino[0]}"
        try:
            respuesta = httpx.get(url, params={"overview": "simplified", "geometries": "geojson"},
                                  timeout=httpx.Timeout(self.tiempoMaximo, connect=3.0))
            if respuesta.status_code == 429:
                raise SinConexion("El servicio de rutas pidió esperar (demasiadas consultas).")
            datos = respuesta.json()
        except (httpx.HTTPError, ValueError) as error:
            self._sinConexionHasta = time.monotonic() + self.esperaTrasFallo
            raise SinConexion(f"No se pudo consultar el servicio de rutas: {error}") from error
        if datos.get("code") != "Ok" or not datos.get("routes"):
            return None
        ruta = datos["routes"][0]
        puntos = [(round(lat, 5), round(lon, 5)) for lon, lat in ruta["geometry"]["coordinates"]]
        return RutaCarretera(puntos, round(ruta["distance"] / 1000, 1), round(ruta["duration"] / 60, 1))


class CacheRutas:
    """Trazados ya descargados, por par de coordenadas (si se mueve un punto, se vuelve a trazar)."""

    def __init__(self, archivo: Path = ARCHIVO_RUTAS):
        self.archivo = Path(archivo)
        self._rutas: Optional[dict] = None

    @staticmethod
    def clave(origen: Punto, destino: Punto) -> str:
        return f"{origen[0]:.4f},{origen[1]:.4f};{destino[0]:.4f},{destino[1]:.4f}"

    def _cargar(self) -> dict:
        if self._rutas is None:
            try:
                self._rutas = json.loads(self.archivo.read_text(encoding="utf-8")).get("rutas", {})
            except (OSError, ValueError):
                self._rutas = {}
        return self._rutas

    def obtener(self, origen: Punto, destino: Punto) -> Optional[RutaCarretera]:
        datos = self._cargar().get(self.clave(origen, destino))
        if not datos:
            return None
        return RutaCarretera([tuple(p) for p in datos["puntos"]], datos["distancia_km"], datos["duracion_min"])

    def agregar(self, origen: Punto, destino: Punto, ruta: RutaCarretera) -> None:
        self._cargar()[self.clave(origen, destino)] = asdict(ruta)

    def escribir(self) -> None:
        self.archivo.parent.mkdir(parents=True, exist_ok=True)
        contenido = {"fuente": FUENTE, "rutas": dict(sorted(self._cargar().items()))}
        self.archivo.write_text(json.dumps(contenido, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
