import streamlit as st

from clienteApi.cliente import ErrorApi
from estado.estadoUi import EstadoUI


def simularEscenario(estado: EstadoUI, escenario: dict, descripcion: str) -> None:
    estado.limpiarMensajes()
    with st.spinner("Resolviendo cada paso del escenario…"):
        try:
            resultado = estado.apiSensibilidad.sensibilidad(escenario)
        except ErrorApi as error:
            estado.errores = error.errores
            return
    estado.ultimoEscenario = {"resultado": resultado, "descripcion": descripcion, "escenario": escenario}
