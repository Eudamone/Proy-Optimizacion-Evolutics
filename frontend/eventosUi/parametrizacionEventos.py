import io

import pandas as pd

from clienteApi.cliente import ErrorApi
from estado.estadoUi import EstadoUI


def cargarRed(estado: EstadoUI, forzar: bool = False) -> None:
    if estado.redEditada is None or forzar:
        estado.redEditada = estado.apiRed.obtenerRed()
        estado.reiniciarTablas()


def guardarRed(estado: EstadoUI, red: dict) -> None:
    estado.limpiarMensajes()
    try:
        resumen = estado.apiRed.guardarRed(red)
    except ErrorApi as error:
        estado.errores = error.errores
        return
    estado.redEditada = red
    estado.redCambio()
    estado.aviso = (f"Red guardada: {resumen['agroempresas']} agroempresas y "
                    f"{resumen['plantas_activas']} plantas activas.")


def restablecerRed(estado: EstadoUI) -> None:
    estado.limpiarMensajes()
    try:
        estado.apiRed.restablecerRed()
        cargarRed(estado, forzar=True)
    except ErrorApi as error:
        estado.errores = error.errores
        return
    estado.redCambio()
    estado.aviso = "Se cargaron otra vez los datos de prueba."


def leerCsv(archivo, columnasRequeridas: list[str]) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(archivo.getvalue()))
    faltan = [c for c in columnasRequeridas if c not in df.columns]
    if faltan:
        raise ErrorApi([f"Al archivo {archivo.name} le faltan las columnas: {', '.join(faltan)}."])
    return df
