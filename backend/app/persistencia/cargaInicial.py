import csv
import json
from pathlib import Path
from typing import Optional

from app.dominio.red import Agroempresa, ParametrosEconomicos, Planta, RedLogistica, Ruta
from app.dominio.tipos import TipoResiduo

CARPETA_SEMILLA = Path(__file__).resolve().parents[2] / "datos" / "semilla"


def _leerCsv(ruta: Path) -> list[dict]:
    with open(ruta, encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def _aBool(valor: str) -> bool:
    return str(valor).strip().lower() in ("true", "1", "si", "sí")


def _aFloatOpcional(valor: Optional[str]) -> Optional[float]:
    return float(valor) if valor not in (None, "") else None


def cargarRedSemilla(carpeta: Optional[Path] = None) -> RedLogistica:
    carpeta = Path(carpeta) if carpeta else CARPETA_SEMILLA

    agroempresas = [
        Agroempresa(
            id=f["id"],
            nombre=f["nombre"],
            municipio=f["municipio"],
            tipo_residuo=TipoResiduo(f["tipo_residuo"]),
            oferta_t=float(f["oferta_t"]),
            lat=_aFloatOpcional(f.get("lat")),
            lon=_aFloatOpcional(f.get("lon")),
        )
        for f in _leerCsv(carpeta / "agroempresas.csv")
    ]
    plantas = [
        Planta(
            id=f["id"],
            nombre=f["nombre"],
            municipio=f["municipio"],
            capacidad_t=float(f["capacidad_t"]),
            costo_operacion=float(f["costo_operacion"]),
            activa=_aBool(f["activa"]),
            lat=_aFloatOpcional(f.get("lat")),
            lon=_aFloatOpcional(f.get("lon")),
        )
        for f in _leerCsv(carpeta / "plantas.csv")
    ]
    rutas = [
        Ruta(
            agroempresa_id=f["agroempresa_id"],
            planta_id=f["planta_id"],
            distancia_km=float(f["distancia_km"]),
            habilitada=_aBool(f["habilitada"]),
        )
        for f in _leerCsv(carpeta / "distancias.csv")
    ]
    with open(carpeta / "parametros.json", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    parametros = ParametrosEconomicos(
        tarifa_t_km=datos.get("tarifa_t_km"),
        precio_tonelada=datos.get("precio_tonelada"),
        gran_m=float(datos.get("gran_m", 1e8)),
    )
    return RedLogistica(agroempresas, plantas, rutas, parametros)


def cargarSiVacia(sesion) -> bool:
    """Guarda la red de prueba si la base está vacía; devuelve True si cargó."""
    from app.persistencia.repositorios.redRepository import RedRepository

    repositorio = RedRepository(sesion)
    if not repositorio.estaVacia():
        return False
    repositorio.guardar(cargarRedSemilla())
    return True
