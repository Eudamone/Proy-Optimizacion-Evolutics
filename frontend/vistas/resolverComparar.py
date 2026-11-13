"""Pantalla "Resolver y comparar".

Método exacto (Vogel + MODI) contra varias corridas del algoritmo genético:
indicadores, convergencia, costo por corrida, asignación óptima, mapa de rutas
y resumen de la comparación.
"""

from datetime import datetime

import streamlit as st

from clienteApi.cliente import ErrorApi
from componentes.graficos import graficarConvergencia, graficarCorridas, graficarMapaDespacho, graficarMapaReal
from componentes.panelParametrosAg import mostrarPanelParametrosAg
from componentes.tarjetasKpi import (barrasCapacidad, encabezado, estadoVacio, matrizAsignacion, mostrarErrores,
                                     mostrarEstado, rutasCargadas, tablaResumenComparacion, tarjeta, tarjetasKpi)
from componentes.tema import COLORES, formatoMillones, formatoNumero, formatoPesos, formatoPorcentaje
from estado.estadoUi import obtenerEstado
from eventosUi.ejecucionEventos import ejecutarComparacion

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]



def _notaFuentes(rutas, tipoMapa: str) -> str:
    """De dónde salen el fondo y los trazados, y qué falta si no hay conexión."""
    fondo = "Mapa base: CARTO y OpenStreetMap. " if tipoMapa == "Mapa real" else ""
    if rutas is None:
        return fondo + "No se pudieron leer los trazados por carretera: las rutas van sin seguir las carreteras."
    if not rutas["tramos"]:
        return fondo + ("Las rutas todavía no siguen las carreteras. Con internet, pulsa «Descargar rutas»: "
                        "quedan guardadas y sirven sin conexión.")
    if rutas["faltantes"]:
        return fondo + (f"Rutas por carretera de OSRM; faltan {rutas['faltantes']}, que van sin seguir las "
                        "carreteras hasta descargarlas.")
    return fondo + "Rutas por carretera: OSRM con datos de OpenStreetMap (guardadas, sirven sin conexión)."


estado = obtenerEstado()
previa = estado.ultimaComparacion
subtitulo = (f"El genético quedó a {formatoPorcentaje(previa['gap_pct'])} del óptimo en {len(previa['costos_ag'])} corridas."
             if previa else "Método exacto (Vogel + MODI) contra el algoritmo genético.")
pulsado = encabezado("Resolver y comparar", subtitulo,
                     "Resolver y comparar", clave="botonComparar", icono=":material/play_arrow:")

try:
    red = estado.red()
    exacta = estado.solucionExacta()
except ErrorApi as error:
    mostrarErrores(error.errores)
    st.page_link("vistas/parametrizacion.py", label="Revisar la red", icon=":material/tune:")
    st.stop()

with st.expander("Parámetros del algoritmo genético", expanded=estado.ultimaComparacion is None):
    parametros, corridas = mostrarPanelParametrosAg("comparar")

if pulsado:
    ejecutarComparacion(estado, parametros, corridas)
    if estado.ultimaComparacion:
        st.session_state["horaComparacion"] = datetime.now()
        st.rerun()  # para que el subtítulo muestre el resultado nuevo
mostrarErrores(estado.errores)

comparacion = estado.ultimaComparacion
nombres = {a["id"]: a["nombre"] for a in red["agroempresas"]} | {p["id"]: p["municipio"] for p in red["plantas"]}

# ---- aviso e indicadores ----
if comparacion:
    hora = st.session_state.get("horaComparacion", datetime.now())
    mostrarEstado("bien", "Comparación guardada.",
                  f"1 corrida exacta y {len(comparacion['costos_ag'])} del AG, ejecución #{comparacion['ejecucion_id']} "
                  f"del {hora.day} de {MESES[hora.month - 1]}, {hora:%H:%M}.")
    tiempoAg = comparacion["tiempos"]["genetico_promedio"]
    tarjetasKpi([
        {"icono": "ruta", "etiqueta": "Costo óptimo · método exacto", "valor": formatoPesos(comparacion["z_exacto"]),
         "detalle": f"por semana · {len(comparacion['exacta']['flujos'])} rutas",
         "destacada": True},
        {"icono": "camion", "ag": True, "etiqueta": "Mejor costo del AG", "valor": formatoPesos(comparacion["z_ag_mejor"]),
         "detalle": f"+{formatoPesos(comparacion['z_ag_mejor'] - comparacion['z_exacto'])} sobre el óptimo"},
        {"icono": "planta", "etiqueta": "Gap del mejor AG", "valor": formatoPorcentaje(comparacion["gap_pct"]),
         "detalle": f"promedio: {formatoPorcentaje(comparacion['gap_promedio_pct'])}"},
        {"icono": "reloj", "etiqueta": "Tiempo por corrida del AG", "valor": f"{formatoNumero(tiempoAg, 2)} s",
         "detalle": f"exacto: {formatoNumero(comparacion['tiempos']['exacto'] * 1000, 1)} ms"},
    ])
else:
    toneladas = sum(f["toneladas"] for f in exacta["flujos"])
    tarjetasKpi([
        {"icono": "ruta", "etiqueta": "Costo óptimo · método exacto", "valor": formatoPesos(exacta["costo_total"]),
         "detalle": f"por semana · Vogel + MODI · {formatoNumero(exacta['tiempo_s'] * 1000, 1)} ms", "destacada": True},
        {"icono": "historial", "etiqueta": "Costo inicial de Vogel", "valor": formatoPesos(exacta["costo_inicial"]),
         "detalle": f"MODI lo mejoró en {exacta['iteraciones']} iteraciones"},
        {"icono": "tonelada", "etiqueta": "Toneladas despachadas", "valor": formatoNumero(toneladas) + " t", "detalle": "por semana"},
        {"icono": "camion", "etiqueta": "Rutas en uso", "valor": str(len(exacta["flujos"])),
         "detalle": f"de {len(red['agroempresas']) * len(red['plantas'])} posibles"},
    ])
st.write("")

# ---- convergencia ----
with tarjeta("convergencia", "Convergencia del algoritmo genético"):
    if comparacion:
        historial = comparacion["mejor_genetica"]["historial"]
        st.plotly_chart(graficarConvergencia(historial["mejor_costo"], historial["costo_promedio"],
                                             comparacion["z_exacto"]), width="stretch", config={"displayModeBar": False})
    else:
        estadoVacio("Pulsa «Resolver y comparar» para ver cómo el algoritmo genético se acerca al óptimo "
                    "generación tras generación.")
st.write("")

# ---- corridas y asignación ----
izquierda, derecha = st.columns(2, gap="medium")
with izquierda:
    with tarjeta("corridas", "Costo de cada corrida del AG",
                 ayuda="Cada punto es una semilla; la línea punteada es el óptimo del método exacto."):
        if comparacion:
            st.plotly_chart(graficarCorridas(comparacion["costos_ag"], comparacion["semillas"], comparacion["z_exacto"]),
                            width="stretch", config={"displayModeBar": False})
        else:
            estadoVacio("Aquí aparecerá el costo de cada corrida.")
with derecha:
    with tarjeta("asignacion", "Asignación óptima (t por semana)"):
        matrizAsignacion(red, exacta)
st.write("")

# ---- mapa y capacidad ----
izquierda, derecha = st.columns([3, 2], gap="medium")
with izquierda:
    try:
        rutas = estado.rutasCarretera()
    except ErrorApi:
        rutas = None
    tramos = {(t["agroempresa_id"], t["planta_id"]): t for t in (rutas or {}).get("tramos", [])}
    enUso = [tramos.get((f["agroempresa_id"], f["planta_id"])) for f in exacta["flujos"]]
    nota = f"{len(exacta['flujos'])} rutas · {formatoMillones(exacta['costo_total'])} por semana"
    if rutas and not rutas["faltantes"] and any(enUso):  # sin trazado = mismo municipio, 0 km
        nota += f" · {formatoNumero(sum(t['distancia_km'] for t in enUso if t))} km por carretera"
    hayInternet = estado.hayInternet()
    with tarjeta("mapa", "Rutas del despacho óptimo", nota, ayuda="El grosor de cada ruta es proporcional a las toneladas."):
        tipoMapa = st.segmented_control("Tipo de mapa", ["Mapa real", "Esquemático"], key="tipoMapa",
                                        default="Mapa real" if hayInternet else "Esquemático",
                                        label_visibility="collapsed") or "Esquemático"
        if tipoMapa == "Mapa real":
            if not hayInternet:
                mostrarEstado("alerta", "Sin internet el mapa real queda sin fondo.", "Cambia a «Esquemático».")
            st.plotly_chart(graficarMapaReal(red, exacta, rutas, alto=440), width="stretch",
                            config={"displayModeBar": False, "scrollZoom": True})
        else:
            st.plotly_chart(graficarMapaDespacho(red, exacta, alto=440, rutas=rutas), width="stretch",
                            config={"displayModeBar": False})
        nota, boton = st.columns([3, 1.3], vertical_alignment="center")
        nota.caption(_notaFuentes(rutas, tipoMapa))
        if rutas and rutas["faltantes"] and boton.button("Descargar rutas", icon=":material/download:",
                                                          key="descargarRutas", width="stretch"):
            with st.spinner(f"Consultando OSRM: {rutas['faltantes']} rutas, unos segundos cada una…"):
                try:
                    rutas = estado.descargarRutasCarretera()
                except ErrorApi as error:
                    mostrarErrores(error.errores)
                    st.stop()
            if rutas["sin_conexion"]:
                mostrarEstado("alerta", "El servicio de rutas no respondió.",
                              "Revisa la conexión a internet; mientras tanto las rutas van sin seguir las carreteras.")
            else:
                st.rerun()
with derecha:
    with tarjeta("capacidad", "Capacidad usada por planta"):
        usada = {p["id"]: 0.0 for p in red["plantas"]}
        for f in exacta["flujos"]:
            usada[f["planta_id"]] += f["toneladas"]
        barrasCapacidad([{"nombre": p["municipio"], "usada": usada[p["id"]],
                          "capacidad": p["capacidad_t"] if p["activa"] else 0} for p in red["plantas"]])
        st.markdown('<p class="titulo-tarjeta" style="margin-top:.6rem">Rutas más cargadas</p>', unsafe_allow_html=True)
        rutasCargadas([(nombres[f["agroempresa_id"]], nombres[f["planta_id"]], f["toneladas"])
                       for f in exacta["flujos"]])
st.write("")

# ---- resumen ----
with tarjeta("resumen", "Resumen de la comparación"):
    if comparacion:
        tablaResumenComparacion(comparacion, COLORES)
        st.page_link("vistas/reportes.py", label="Ver en Reportes", icon=":material/arrow_forward:")
    else:
        estadoVacio("Todavía no hay comparación en esta sesión.")
