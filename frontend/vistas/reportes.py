import pandas as pd
import streamlit as st

from clienteApi.cliente import ErrorApi
from componentes.graficos import graficarConvergencia, graficarCostoPorEjecucion
from componentes.tarjetasKpi import encabezado, estadoVacio, mostrarErrores, tarjeta, tarjetasKpi
from componentes.tema import formatoNumero, formatoPesos, formatoPorcentaje
from estado.estadoUi import obtenerEstado

estado = obtenerEstado()
try:
    ejecuciones = estado.apiReportes.listarReportes()
except ErrorApi as error:
    encabezado("Reportes")
    mostrarErrores(error.errores)
    st.stop()

if not ejecuciones:
    encabezado("Reportes", "Cada comparación del método exacto contra el algoritmo genético queda guardada aquí.")
    st.write("")
    estadoVacio("Todavía no hay comparaciones guardadas.")
    st.page_link("vistas/resolverComparar.py", label="Ir a Resolver y comparar", icon=":material/play_arrow:")
    st.stop()

mejor = min(ejecuciones, key=lambda e: e["gap_pct"])
encabezado("Reportes", f"{len(ejecuciones)} comparaciones guardadas · mejor gap "
                       f"{formatoPorcentaje(mejor['gap_pct'])} (#{mejor['id']})")
tarjetasKpi([
    {"icono": "historial", "etiqueta": "Comparaciones guardadas", "valor": str(len(ejecuciones)),
     "detalle": f"{sum(e['corridas'] for e in ejecuciones)} corridas del AG en total", "destacada": True},
    {"icono": "camion", "ag": True, "etiqueta": "Mejor gap", "valor": formatoPorcentaje(mejor["gap_pct"]), "detalle": f"comparación #{mejor['id']}"},
    {"icono": "camion", "etiqueta": "Gap promedio", "valor": formatoPorcentaje(sum(e["gap_pct"] for e in ejecuciones) / len(ejecuciones)),
     "detalle": "del mejor AG de cada comparación"},
    {"icono": "reloj", "etiqueta": "Tiempo por corrida del AG", "valor":
        f"{formatoNumero(sum(e['tiempo_ag_s'] for e in ejecuciones) / len(ejecuciones), 2)} s", "detalle": "promedio"},
])
st.write("")

tabla = pd.DataFrame([{
    "#": e["id"], "Fecha": pd.to_datetime(e["fecha"]).strftime("%Y-%m-%d %H:%M"),
    "Corridas": e["corridas"], "Población": e["parametros"].get("poblacion"),
    "Generaciones": e["parametros"].get("generaciones"),
    "Selección": e["parametros"].get("seleccion"), "Cruce": e["parametros"].get("cruce"),
    "Mutación": e["parametros"].get("mutacion"),
    "Óptimo exacto": e["z_exacto"], "Mejor AG": e["z_ag_mejor"], "Promedio AG": e["z_ag_promedio"],
    "Gap %": e["gap_pct"], "Tiempo exacto (s)": e["tiempo_exacto_s"], "Tiempo AG (s)": e["tiempo_ag_s"],
} for e in ejecuciones])

izquierda, derecha = st.columns([2, 3], gap="medium")
with izquierda:
    with tarjeta("costoMetodo", "Costo por método en cada comparación"):
        st.plotly_chart(graficarCostoPorEjecucion(ejecuciones), width="stretch", config={"displayModeBar": False})
with derecha:
    with tarjeta("historial", "Historial de comparaciones"):
        vista = tabla.copy()
        for columna in ("Óptimo exacto", "Mejor AG", "Promedio AG"):
            vista[columna] = vista[columna].map(formatoPesos)
        vista["Gap %"] = vista["Gap %"].map(formatoPorcentaje)
        st.dataframe(vista, hide_index=True, width="stretch", height=300,
                     column_config={"Tiempo exacto (s)": st.column_config.NumberColumn(format="%.4f"),
                                    "Tiempo AG (s)": st.column_config.NumberColumn(format="%.2f")})
        st.download_button("Descargar historial (CSV)", tabla.to_csv(index=False).encode("utf-8-sig"),
                           file_name="historialComparaciones.csv", mime="text/csv", icon=":material/download:")
st.write("")

# ---- detalle de una comparación ----
with tarjeta("detalle", "Detalle de una comparación"):
    elegida = st.selectbox("Comparación", [e["id"] for e in ejecuciones],
                           format_func=lambda i: f"#{i} · " + next(
                               pd.to_datetime(e["fecha"]).strftime("%Y-%m-%d %H:%M") for e in ejecuciones
                               if e["id"] == i))
    try:
        detalle = estado.apiReportes.obtenerReporte(elegida)
    except ErrorApi as error:
        mostrarErrores(error.errores)
        st.stop()

    r = detalle["resultado"]
    tarjetasKpi([
        {"icono": "ruta", "etiqueta": "Óptimo · método exacto", "valor": formatoPesos(r["z_exacto"]), "detalle": "por semana",
         "destacada": True},
        {"icono": "camion", "ag": True, "etiqueta": "Mejor del AG", "valor": formatoPesos(r["z_ag_mejor"]), "detalle": f"gap {formatoPorcentaje(r['gap_pct'])}"},
        {"icono": "camion", "etiqueta": "Promedio del AG", "valor": formatoPesos(r["z_ag_promedio"]),
         "detalle": f"gap {formatoPorcentaje(r['gap_promedio_pct'])} · {len(r['costos_ag'])} corridas"},
        {"icono": "reloj", "etiqueta": "Tiempo por corrida del AG", "valor": f"{formatoNumero(r['tiempos']['genetico_promedio'], 2)} s",
         "detalle": f"exacto: {formatoNumero(r['tiempos']['exacto'] * 1000, 1)} ms"},
    ])
    historial = r["mejor_genetica"]["historial"]
    st.plotly_chart(graficarConvergencia(historial["mejor_costo"], historial["costo_promedio"], r["z_exacto"]),
                    width="stretch", config={"displayModeBar": False})

    flujos = pd.DataFrame(
        [{"Método": "Exacto", "Agroempresa": f["agroempresa_id"], "Planta": f["planta_id"], "Toneladas": f["toneladas"],
          "Costo por tonelada": f["costo_unitario"]} for f in r["exacta"]["flujos"]]
        + [{"Método": "Algoritmo genético", "Agroempresa": f["agroempresa_id"], "Planta": f["planta_id"],
            "Toneladas": f["toneladas"], "Costo por tonelada": f["costo_unitario"]} for f in r["mejor_genetica"]["flujos"]]
    )
    with st.expander("Rutas de cada método"):
        st.dataframe(flujos.assign(**{"Costo por tonelada": flujos["Costo por tonelada"].map(formatoPesos)}),
                     hide_index=True, width="stretch",
                     column_config={"Toneladas": st.column_config.NumberColumn(format="%.2f t")})
    st.download_button("Descargar rutas de esta comparación (CSV)", flujos.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"rutasComparacion{elegida}.csv", mime="text/csv", icon=":material/download:")
