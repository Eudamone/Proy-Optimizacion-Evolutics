from typing import Any, Optional

import httpx
import streamlit as st

from clienteApi.cliente import HttpApiClient, IOptimizacionApi, IRedApi, IReportesApi, ISensibilidadApi

URL_MAPA_BASE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


class EstadoUI:
    def __init__(self):
        self._s = st.session_state

    def _obtener(self, clave: str, defecto: Any = None) -> Any:
        return self._s.get(clave, defecto)

    def _poner(self, clave: str, valor: Any) -> None:
        self._s[clave] = valor

    # ---- clientes de la API: cada pantalla usa solo el que necesita ----

    def _cliente(self) -> HttpApiClient:
        if "cliente" not in self._s:
            self._s["cliente"] = HttpApiClient()
        return self._s["cliente"]

    @property
    def apiRed(self) -> IRedApi:
        return self._cliente()

    @property
    def apiOptimizacion(self) -> IOptimizacionApi:
        return self._cliente()

    @property
    def apiSensibilidad(self) -> ISensibilidadApi:
        return self._cliente()

    @property
    def apiReportes(self) -> IReportesApi:
        return self._cliente()

    # ---- red en edición ----

    @property
    def redEditada(self) -> Optional[dict]:
        return self._obtener("redEditada")

    @redEditada.setter
    def redEditada(self, red: Optional[dict]) -> None:
        self._poner("redEditada", red)

    @property
    def versionTablas(self) -> int:
        return self._obtener("versionTablas", 0)

    def reiniciarTablas(self) -> None:
        self._poner("versionTablas", self.versionTablas + 1)

    # ---- resultados ----

    @property
    def ultimaComparacion(self) -> Optional[dict]:
        return self._obtener("ultimaComparacion")

    @ultimaComparacion.setter
    def ultimaComparacion(self, comparacion: Optional[dict]) -> None:
        self._poner("ultimaComparacion", comparacion)

    @property
    def ultimoEscenario(self) -> Optional[dict]:
        return self._obtener("ultimoEscenario")

    @ultimoEscenario.setter
    def ultimoEscenario(self, resultado: Optional[dict]) -> None:
        self._poner("ultimoEscenario", resultado)

    # ---- mensajes ----

    @property
    def errores(self) -> list[str]:
        return self._obtener("errores", [])

    @errores.setter
    def errores(self, errores: list[str]) -> None:
        self._poner("errores", errores)

    @property
    def aviso(self) -> Optional[str]:
        return self._obtener("aviso")

    @aviso.setter
    def aviso(self, texto: Optional[str]) -> None:
        self._poner("aviso", texto)

    def limpiarMensajes(self) -> None:
        self.errores = []
        self.aviso = None

    def redCambio(self) -> None:
        """Después de guardar la red, los resultados anteriores ya no valen."""
        self.ultimaComparacion = None
        self.ultimoEscenario = None
        self._poner("cache", {})

    # ---- caché por sesión: cambiar de pantalla no vuelve a pedir lo mismo a la API ----

    def enCache(self, clave: str, calcular):
        """Valor guardado o lo calcula una vez; se borra cuando la red cambia."""
        cache = self._obtener("cache")
        if cache is None:
            cache = {}
            self._poner("cache", cache)
        if clave not in cache:
            cache[clave] = calcular()
        return cache[clave]

    def red(self) -> dict:
        return self.enCache("red", self.apiRed.obtenerRed)

    def resumenRed(self) -> dict:
        return self.enCache("resumen", self.apiRed.obtenerResumen)

    def solucionExacta(self) -> dict:
        return self.enCache("exacta", lambda: self.apiOptimizacion.resolver("exacto"))

    def sensibilidadBase(self) -> dict:
        return self.enCache("sensibilidad", lambda: self.apiSensibilidad.sensibilidad(None))

    def rutasCarretera(self) -> dict:
        return self.enCache("rutasCarretera", self.apiRed.rutasCarretera)

    def descargarRutasCarretera(self) -> dict:
        rutas = self.apiRed.rutasCarretera(descargar=True)
        cache = self._obtener("cache") or {}
        cache["rutasCarretera"] = rutas
        self._poner("cache", cache)
        return rutas

    def hayInternet(self) -> bool:
        """¿Carga el mapa base de CARTO? Se revisa una vez por sesión."""
        def probar() -> bool:
            try:
                return httpx.head(URL_MAPA_BASE, timeout=2.0).status_code < 500
            except httpx.HTTPError:
                return False
        return self.enCache("internet", probar)


def obtenerEstado() -> EstadoUI:
    return EstadoUI()
