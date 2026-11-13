import streamlit as st

from clienteApi.cliente import ErrorApi
from estado.estadoUi import EstadoUI


def ejecutarComparacion(estado: EstadoUI, parametros: dict, corridas: int) -> None:
    estado.limpiarMensajes()
    with st.spinner(f"Despachando: método exacto y {corridas} corridas del algoritmo genético…"):
        try:
            estado.ultimaComparacion = estado.apiOptimizacion.comparar(parametros, corridas)
        except ErrorApi as error:
            estado.errores = error.errores
