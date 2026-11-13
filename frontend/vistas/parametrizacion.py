import pandas as pd
import streamlit as st

from clienteApi.cliente import ErrorApi
from componentes.editorMatriz import (construirRed, diccionarioRutas, editarAgroempresas, editarPlantas, editarRutas,
                                      tablaAgroempresas, tablaPlantas)
from componentes.tarjetasKpi import encabezado, mostrarErrores, mostrarEstado, tarjeta, tarjetasKpi
from componentes.tema import formatoPesos, formatoToneladas
from estado.estadoUi import obtenerEstado
from eventosUi.parametrizacionEventos import cargarRed, guardarRed, leerCsv, restablecerRed

estado = obtenerEstado()
pulsadoGuardar = encabezado("Parametrización",
                            "Agroempresas, plantas, distancias y tarifa de la red.", "Guardar red", clave="botonGuardar", icono=":material/save:")
try:
    cargarRed(estado)
except ErrorApi as error:
    mostrarErrores(error.errores)
    st.stop()

red = estado.redEditada
version = estado.versionTablas

if estado.aviso:
    mostrarEstado("bien", estado.aviso)
mostrarErrores(estado.errores)
indicadores = st.container()
st.write("")

tablas = tarjeta("tablas")
with tablas:
    pestanas = st.tabs(["Agroempresas", "Plantas", "Distancias y rutas", "Tarifa", "Importar CSV"])

    with pestanas[0]:
        dfAgro = editarAgroempresas(tablaAgroempresas(red), f"agro-{version}")
        st.caption("Para agregar una agroempresa usa la última fila de la tabla y luego completa sus distancias.")
    with pestanas[1]:
        dfPlantas = editarPlantas(tablaPlantas(red), f"plantas-{version}")
        st.caption("Una planta inactiva queda con capacidad 0 para el despacho.")
    with pestanas[2]:
        claveRutas = f"rutas-{version}"
        distancias, habilitadas = st.session_state.get(claveRutas) or diccionarioRutas(red)
        distancias, habilitadas = editarRutas(dfAgro, dfPlantas, distancias, habilitadas, claveRutas)
        st.session_state[claveRutas] = (distancias, habilitadas)
    with pestanas[3]:
        p = red["parametros"]
        c1, c2 = st.columns(2)
        tarifa = c1.number_input("Tarifa de transporte ($ por tonelada-km)", min_value=0.0, step=100.0,
                                 value=float(p.get("tarifa_t_km") or 0), key=f"tarifa-{version}")
        granM = c2.number_input("Gran M para rutas bloqueadas ($ por tonelada)", min_value=1.0, step=1e6,
                                value=float(p.get("gran_m") or 1e8), format="%.0f", key=f"granM-{version}")
        st.caption(f"Costo de una ruta = distancia × tarifa + costo de operación de la planta. "
                   f"Ejemplo: 50 km a {formatoPesos(tarifa)} por t·km son {formatoPesos(50 * tarifa)} por tonelada.")
    with pestanas[4]:
        st.write("Sube los archivos con el mismo formato de `backend/datos/semilla`. "
                 "Reemplazan las tablas de esta pantalla; nada se guarda hasta pulsar **Guardar red**.")
        c1, c2, c3 = st.columns(3)
        archivoAgro = c1.file_uploader("agroempresas.csv", type="csv", key=f"csvAgro-{version}")
        archivoPlantas = c2.file_uploader("plantas.csv", type="csv", key=f"csvPlantas-{version}")
        archivoDist = c3.file_uploader("distancias.csv", type="csv", key=f"csvDist-{version}")
        if st.button("Usar estos archivos", disabled=not (archivoAgro and archivoPlantas and archivoDist)):
            try:
                agro = leerCsv(archivoAgro, ["id", "nombre", "municipio", "tipo_residuo", "oferta_t"])
                plantas = leerCsv(archivoPlantas, ["id", "nombre", "municipio", "capacidad_t", "costo_operacion", "activa"])
                dist = leerCsv(archivoDist, ["agroempresa_id", "planta_id", "distancia_km", "habilitada"])
            except ErrorApi as error:
                mostrarErrores(error.errores)
            else:
                for df in (agro, plantas):
                    for columna in ("lat", "lon"):
                        if columna not in df.columns:
                            df[columna] = None
                plantas["activa"] = plantas["activa"].astype(str).str.lower().isin(["true", "1", "si", "sí"])
                dist["habilitada"] = dist["habilitada"].astype(str).str.lower().isin(["true", "1", "si", "sí"])
                estado.redEditada = {
                    "agroempresas": agro.astype(object).where(pd.notna(agro), None).to_dict("records"),
                    "plantas": plantas.astype(object).where(pd.notna(plantas), None).to_dict("records"),
                    "rutas": dist.to_dict("records"),
                    "parametros": red["parametros"],
                }
                estado.reiniciarTablas()
                estado.aviso = "Archivos cargados. Revisa las tablas y pulsa Guardar red."
                st.rerun()

# ---- indicadores de lo que se está editando ----
oferta = float(dfAgro["oferta_t"].fillna(0).sum())
activas = dfPlantas[dfPlantas["activa"].fillna(True).astype(bool)]
capacidad = float(activas["capacidad_t"].fillna(0).sum())
with indicadores:
    tarjetasKpi([
        {"icono": "tonelada", "etiqueta": "Oferta total", "valor": formatoToneladas(oferta), "detalle": f"{len(dfAgro)} agroempresas · por semana",
         "destacada": True},
        {"icono": "planta", "etiqueta": "Capacidad activa", "valor": formatoToneladas(capacidad),
         "detalle": f"{len(activas)} de {len(dfPlantas)} plantas activas"},
        {"icono": "planta", "etiqueta": "Capacidad libre", "valor": formatoToneladas(capacidad - oferta),
         "detalle": "la absorbe una fuente ficticia de costo 0"},
        {"icono": "camion", "etiqueta": "Rutas", "valor": str(len(distancias)),
         "detalle": f"{sum(1 for v in habilitadas.values() if not v)} bloqueadas"},
    ])
    if oferta > capacidad:
        st.write("")
        mostrarEstado("alerta", "Así no se puede despachar.",
                      f"La oferta supera la capacidad por {formatoToneladas(oferta - capacidad)}: "
                      "activa una planta o sube su capacidad.")

st.write("")
c1, _ = st.columns([1, 3])
if c1.button("Restablecer datos de prueba", icon=":material/restart_alt:", width="stretch"):
    restablecerRed(estado)
    st.rerun()

if pulsadoGuardar:
    nueva = construirRed(dfAgro, dfPlantas, distancias, habilitadas,
                         {"tarifa_t_km": tarifa or None, "precio_tonelada": red["parametros"].get("precio_tonelada"),
                          "gran_m": granM})
    guardarRed(estado, nueva)
    if not estado.errores:
        estado.reiniciarTablas()
    st.rerun()
