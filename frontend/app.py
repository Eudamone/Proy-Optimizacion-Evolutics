"""Punto de entrada de la capa de presentación (Streamlit).

Arma la barra lateral (marca, menú de las cuatro pantallas y resumen de la red
activa) y ejecuta la pantalla elegida.

Ejecutar desde la carpeta frontend (con la API corriendo):  streamlit run app.py
"""

import streamlit as st

from clienteApi.cliente import ErrorApi
from componentes.tarjetasKpi import marcaLateral, redActiva
from componentes.tema import aplicarTema
from estado.estadoUi import obtenerEstado

st.set_page_config(page_title="EcoResiduos del Llano", layout="wide", initial_sidebar_state="expanded")
aplicarTema()

PAGINAS = [
    st.Page("vistas/parametrizacion.py", title="Parametrización", icon=":material/tune:"),
    st.Page("vistas/resolverComparar.py", title="Resolver y comparar", icon=":material/bar_chart:", default=True),
    st.Page("vistas/sensibilidad.py", title="Sensibilidad", icon=":material/show_chart:"),
    st.Page("vistas/reportes.py", title="Reportes", icon=":material/description:"),
]
pagina = st.navigation(PAGINAS, position="hidden")

with st.sidebar:
    marcaLateral()
    for p in PAGINAS:
        activa = p.title == pagina.title
        with st.container(key="navActiva" if activa else f"nav{p.title.replace(' ', '')}"):
            st.page_link(p, label=p.title, icon=p.icon)
    st.divider()
    estado = obtenerEstado()
    try:
        redActiva(estado.resumenRed())
    except ErrorApi as error:
        redActiva(None, error.errores[0])

pagina.run()
