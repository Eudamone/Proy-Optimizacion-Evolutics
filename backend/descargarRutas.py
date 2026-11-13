# Descarga los trazados de todas las rutas (necesita internet): python descargarRutas.py

from app.infraestructura.configuracion import obtenerConfiguracion
from app.infraestructura.rutasCarretera import ARCHIVO_RUTAS, CacheRutas, ProveedorOsrm
from app.persistencia.cargaInicial import cargarRedSemilla
from app.persistencia.conexion import configurarBaseDatos, nuevaSesion
from app.persistencia.repositorios.redRepository import RedRepository
from app.servicios.servicioRutas import ServicioRutas


def main() -> None:
    configurarBaseDatos(obtenerConfiguracion().urlBaseDatos)
    sesion = nuevaSesion()
    try:
        repositorio = RedRepository(sesion)
        red = cargarRedSemilla() if repositorio.estaVacia() else repositorio.obtenerRed()
        servicio = ServicioRutas(repositorio, CacheRutas(), ProveedorOsrm(esperaTrasFallo=0),
                                 presupuesto_s=None, pausa_s=1.0)
        resultado = servicio.rutasDeLaRed(red, alAvanzar=lambda hechas, total: print(f"  {hechas}/{total}", end="\r"))
    finally:
        sesion.close()
    print(f"Rutas con trazado: {len(resultado.tramos)}")
    if resultado.sin_conexion:
        print(f"Faltan {resultado.faltantes}: el servicio de rutas no respondió. Revise la conexión y vuelva a ejecutar.")
    print(f"Archivo: {ARCHIVO_RUTAS}")


if __name__ == "__main__":
    main()
