from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.dominio.red import Agroempresa, ParametrosEconomicos, Planta, RedLogistica, Ruta
from app.dominio.tipos import TipoResiduo
from app.persistencia.modelos import AgroempresaModelo, ParametrosModelo, PlantaModelo, RutaModelo
from app.persistencia.repositorios.interfaces import IRedRepository


class RedRepository(IRedRepository):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def estaVacia(self) -> bool:
        return self.sesion.scalar(select(AgroempresaModelo.id).limit(1)) is None

    def obtenerRed(self) -> RedLogistica:
        agroempresas = [
            Agroempresa(f.id, f.nombre, f.municipio, TipoResiduo(f.tipo_residuo), f.oferta_t, f.lat, f.lon)
            for f in self.sesion.scalars(select(AgroempresaModelo).order_by(AgroempresaModelo.orden))
        ]
        plantas = [
            Planta(f.id, f.nombre, f.municipio, f.capacidad_t, f.costo_operacion, f.activa, f.lat, f.lon)
            for f in self.sesion.scalars(select(PlantaModelo).order_by(PlantaModelo.orden))
        ]
        rutas = [
            Ruta(f.agroempresa_id, f.planta_id, f.distancia_km, f.habilitada)
            for f in self.sesion.scalars(select(RutaModelo))
        ]
        fila = self.sesion.get(ParametrosModelo, 1)
        parametros = (
            ParametrosEconomicos(fila.tarifa_t_km, fila.precio_tonelada, fila.gran_m)
            if fila else ParametrosEconomicos()
        )
        return RedLogistica(agroempresas, plantas, rutas, parametros)

    def guardar(self, red: RedLogistica) -> None:
        for modelo in (RutaModelo, AgroempresaModelo, PlantaModelo, ParametrosModelo):
            self.sesion.execute(delete(modelo))
        self.sesion.add_all(
            AgroempresaModelo(orden=k, id=a.id, nombre=a.nombre, municipio=a.municipio,
                              tipo_residuo=a.tipo_residuo.value, oferta_t=a.oferta_t, lat=a.lat, lon=a.lon)
            for k, a in enumerate(red.agroempresas)
        )
        self.sesion.add_all(
            PlantaModelo(orden=k, id=p.id, nombre=p.nombre, municipio=p.municipio, capacidad_t=p.capacidad_t,
                         costo_operacion=p.costo_operacion, activa=p.activa, lat=p.lat, lon=p.lon)
            for k, p in enumerate(red.plantas)
        )
        self.sesion.add_all(
            RutaModelo(agroempresa_id=r.agroempresa_id, planta_id=r.planta_id,
                       distancia_km=r.distancia_km, habilitada=r.habilitada)
            for r in red.rutas
        )
        self.sesion.add(ParametrosModelo(id=1, tarifa_t_km=red.parametros.tarifa_t_km,
                                         precio_tonelada=red.parametros.precio_tonelada,
                                         gran_m=red.parametros.gran_m))
        self.sesion.commit()
