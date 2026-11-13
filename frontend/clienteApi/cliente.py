import os
from abc import ABC, abstractmethod
from typing import Optional

import httpx

# 127.0.0.1 y no "localhost": en Windows "localhost" intenta primero IPv6 y cada petición tarda ~2 s más.
URL_API = os.getenv("ECORESIDUOS_API", "http://127.0.0.1:8000")


class ErrorApi(Exception):
    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class IRedApi(ABC):
    @abstractmethod
    def obtenerRed(self) -> dict: ...

    @abstractmethod
    def obtenerResumen(self) -> dict: ...

    @abstractmethod
    def guardarRed(self, red: dict) -> dict: ...

    @abstractmethod
    def restablecerRed(self) -> dict: ...

    @abstractmethod
    def rutasCarretera(self, descargar: bool = False) -> dict: ...


class IOptimizacionApi(ABC):
    @abstractmethod
    def resolver(self, metodo: str, parametros: Optional[dict] = None) -> dict: ...

    @abstractmethod
    def comparar(self, parametros: dict, corridas: int) -> dict: ...


class ISensibilidadApi(ABC):
    @abstractmethod
    def sensibilidad(self, escenario: Optional[dict] = None) -> dict: ...


class IReportesApi(ABC):
    @abstractmethod
    def listarReportes(self) -> list[dict]: ...

    @abstractmethod
    def obtenerReporte(self, ejecucionId: int) -> dict: ...


class HttpApiClient(IRedApi, IOptimizacionApi, ISensibilidadApi, IReportesApi):
    def __init__(self, urlBase: str = URL_API, tiempoMaximo: float = 300):
        self.urlBase = urlBase.rstrip("/")
        self.tiempoMaximo = tiempoMaximo
        self._http = httpx.Client(timeout=tiempoMaximo)  # conexión reutilizable entre peticiones

    # ---- red ----

    def obtenerRed(self) -> dict:
        return self._pedir("GET", "/red")

    def obtenerResumen(self) -> dict:
        return self._pedir("GET", "/red/resumen")

    def guardarRed(self, red: dict) -> dict:
        return self._pedir("PUT", "/red", red)

    def restablecerRed(self) -> dict:
        return self._pedir("POST", "/red/restablecer")

    def rutasCarretera(self, descargar: bool = False) -> dict:
        return self._pedir("GET", f"/red/rutas-carretera?descargar={'true' if descargar else 'false'}")

    # ---- optimización ----

    def resolver(self, metodo: str, parametros: Optional[dict] = None) -> dict:
        return self._pedir("POST", "/optimizacion/resolver", {"metodo": metodo, "parametros": parametros})

    def comparar(self, parametros: dict, corridas: int) -> dict:
        return self._pedir("POST", "/optimizacion/comparar", {"parametros": parametros, "corridas": corridas})

    def sensibilidad(self, escenario: Optional[dict] = None) -> dict:
        return self._pedir("POST", "/sensibilidad", {"escenario": escenario})

    # ---- reportes ----

    def listarReportes(self) -> list[dict]:
        return self._pedir("GET", "/reportes")

    def obtenerReporte(self, ejecucionId: int) -> dict:
        return self._pedir("GET", f"/reportes/{ejecucionId}")

    # ---- transporte ----

    def _pedir(self, metodo: str, ruta: str, cuerpo: Optional[dict] = None):
        try:
            respuesta = self._http.request(metodo, self.urlBase + ruta, json=cuerpo)
        except httpx.ConnectError:
            raise ErrorApi([
                f"No hay conexión con la API en {self.urlBase}. "
                "Ábrela en otra terminal: cd backend y luego uvicorn app.main:app --reload"
            ])
        except httpx.TimeoutException:
            raise ErrorApi(["La API tardó demasiado en responder. Prueba con menos generaciones o corridas."])

        if respuesta.status_code >= 400:
            raise ErrorApi(self._mensajes(respuesta))
        return respuesta.json()

    @staticmethod
    def _mensajes(respuesta: httpx.Response) -> list[str]:
        try:
            cuerpo = respuesta.json()
        except ValueError:
            return [f"La API respondió con un error {respuesta.status_code}."]
        if isinstance(cuerpo, dict) and "errores" in cuerpo:
            return cuerpo["errores"]
        if isinstance(cuerpo, dict) and isinstance(cuerpo.get("detail"), list):
            # Errores de validación de FastAPI: campo y motivo
            return [f"{' > '.join(str(p) for p in d.get('loc', [])[1:])}: {d.get('msg', '')}" for d in cuerpo["detail"]]
        return [f"La API respondió con un error {respuesta.status_code}."]
