"""Pantalla "Sensibilidad".

Precios sombra de la solución óptima y simulación de escenarios: se cambia un
dato en varios pasos y se vuelve a resolver en cada uno.
"""

import pandas as pd
import streamlit as st

from clienteApi.cliente import ErrorApi
from componentes.graficos import graficarAhorroCapacidad, graficarCostoVsVariacion
from componentes.tarjetasKpi import encabezado, estadoVacio, mostrarErrores, mostrarEstado, tarjeta, tarjetasKpi
from componentes.tema import formatoDiferencia, formatoMillones, formatoPesos, formatoToneladas
from estado.estadoUi import obtenerEstado
from eventosUi.sensibilidadEventos import simularEscenario

TIPOS = {
    "Capacidad de una planta": ("CAPACIDAD", "plantas"),
    "Oferta de una agroempresa": ("OFERTA", "agroempresas"),
    "Costo de las rutas hacia una planta": ("COSTO_TRANSPORTE", "plantas"),
    "Cerrar una planta": ("CIERRE_PLANTA", "plantas"),
}


def _toneladas(rango, campo: str) -> str:
    """Valor de un rango en toneladas; sin rango o sin tope se lee "sin límite"."""
    if not rango or rango[campo] is None:
        return "sin límite" if campo == "maximo" else "—"
    return formatoToneladas(rango[campo])


estado = obtenerEstado()
try:
    red = estado.red()
    base = estado.sensibilidadBase()
except ErrorApi as error:
    encabezado("Sensibilidad")
    mostrarErrores(error.errores)
    st.stop()

capacidades = base["capacidades"]
llena = max(capacidades, key=lambda c: c["ahorro_por_tonelada"])
if llena["ahorro_por_tonelada"] > 0:
    subtitulo = (f"{llena['nombre'].replace('Planta ', '')} está al tope: cada tonelada más de capacidad "
                 f"ahorraría {formatoPesos(llena['ahorro_por_tonelada'])} por semana.")
else:
    subtitulo = "Ninguna planta está al tope: ampliar la capacidad no bajaría el costo."
pulsado = encabezado("Sensibilidad", subtitulo, "Simular escenario", clave="botonSimular", icono=":material/science:")

libre = sum((c["rango"]["actual"] if c["rango"] else 0) - c["usada_t"] for c in capacidades)
alTope = [c for c in capacidades if c["ahorro_por_tonelada"] > 0]
tarjetasKpi([
    {"icono": "ruta", "etiqueta": "Costo óptimo actual", "valor": formatoPesos(base["costo_total"]), "detalle": "por semana",
     "destacada": True},
    {"icono": "planta", "etiqueta": "Plantas al tope", "valor": f"{len(alTope)} de {len(capacidades)}",
     "detalle": ", ".join(c["nombre"].replace("Planta ", "") for c in alTope) or "ninguna"},
    {"icono": "tonelada", "etiqueta": "Mayor ahorro por tonelada", "valor": formatoPesos(llena["ahorro_por_tonelada"]),
     "detalle": f"ampliando {llena['nombre'].replace('Planta ', '')}"},
    {"icono": "planta", "etiqueta": "Capacidad libre en la red", "valor": formatoToneladas(libre), "detalle": "por semana"},
])
st.write("")

# ---- escenario ----
with tarjeta("escenario", "Escenario", ayuda="Se cambia un dato en varios pasos y se vuelve a resolver en cada uno."):
    c1, c2, c3, c4 = st.columns([1.3, 1.3, 1.2, 0.8])
    tipoTexto = c1.selectbox("Qué cambia", list(TIPOS))
    tipo, lista = TIPOS[tipoTexto]
    opciones = {f"{x['id']} · {x['nombre']}": x["id"] for x in red[lista]}
    if tipo != "CIERRE_PLANTA":
        opciones = {"Todas": None} | opciones
    objetivoTexto = c2.selectbox("A cuál", list(opciones))
    if tipo == "CIERRE_PLANTA":
        variacion, pasos = (100.0, 100.0), 1
        c3.caption("La planta queda con capacidad 0.")
    else:
        variacion = c3.slider("Variación (%)", -50, 50, (-30, 40), 5)
        pasos = c4.slider("Pasos", 3, 15, 8)

if pulsado:
    escenario = {"tipo": tipo, "objetivo_id": opciones[objetivoTexto], "delta_min": float(variacion[0]),
                 "delta_max": float(variacion[1]), "pasos": int(pasos)}
    simularEscenario(estado, escenario, f"{tipoTexto.lower()} ({objetivoTexto})")
mostrarErrores(estado.errores)
st.write("")

resultado = estado.ultimoEscenario
titulo = resultado["descripcion"].capitalize() if resultado else "Resultado del escenario"
with tarjeta("resultadoEscenario", titulo):
    if not resultado:
        estadoVacio("Elige qué cambia y pulsa «Simular escenario».")
    else:
        pasosEscenario = resultado["resultado"]["escenario"]
        if len(pasosEscenario) == 1:
            paso = pasosEscenario[0]
            if paso["factible"]:
                mostrarEstado("bien", f"Se puede despachar: {formatoPesos(paso['costo_total'])} por semana.",
                              f"{formatoDiferencia(paso['costo_total'] - base['costo_total'])} frente a hoy.")
            else:
                mostrarEstado("error", "Así no se puede despachar.", paso["mensaje"])
        else:
            izquierda, derecha = st.columns([3, 2], gap="medium")
            izquierda.plotly_chart(graficarCostoVsVariacion(pasosEscenario, tipoTexto.lower()), width="stretch",
                                   config={"displayModeBar": False})
            derecha.dataframe(pd.DataFrame([{
                "Variación": f"{p['delta']:+.0f} %",
                "Costo semanal": formatoPesos(p["costo_total"]) if p["factible"] else "sin solución",
                "Frente a hoy": formatoDiferencia(p["costo_total"] - base["costo_total"]) if p["factible"] else "",
                "Cambia ruta": ("sí" if p["cambia_base"] else "no") if p["factible"] else ""}
                for p in pasosEscenario]), hide_index=True, width="stretch")
st.write("")

# ---- precios sombra ----
izquierda, derecha = st.columns([3, 2], gap="medium")
with izquierda:
    with tarjeta("ahorro", "Cuánto vale una tonelada más de capacidad"):
        st.plotly_chart(graficarAhorroCapacidad(capacidades), width="stretch", config={"displayModeBar": False})
with derecha:
    with tarjeta("rangosCapacidad", "Hasta dónde vale ese ahorro",
                 ayuda="Dentro de este rango las rutas óptimas no cambian."):
        st.dataframe(pd.DataFrame([{
            "Planta": c["nombre"].replace("Planta ", ""), "Usada": formatoToneladas(c["usada_t"]),
            "Capacidad": _toneladas(c["rango"], "actual"), "Desde": _toneladas(c["rango"], "minimo"),
            "Hasta": _toneladas(c["rango"], "maximo")} for c in capacidades]),
            hide_index=True, width="stretch")
st.write("")

# ---- detalle ----
izquierda, derecha = st.columns(2, gap="medium")
with izquierda:
    with tarjeta("ofertas", "Precio sombra por agroempresa", ayuda="Cuánto sube el costo si entrega una tonelada más."):
        st.dataframe(pd.DataFrame([{
            "Agroempresa": o["nombre"], "Una tonelada más": formatoPesos(o["precio_sombra"]),
            "Desde": _toneladas(o["rango"], "minimo"), "Hasta": _toneladas(o["rango"], "maximo")}
            for o in base["ofertas"]]),
            hide_index=True, width="stretch", height=390)
with derecha:
    with tarjeta("rutas", "Rangos de costo de las rutas",
                 ayuda=f"Una ruta sin uso empieza a convenir si su costo baja más que su costo reducido "
                 f"(costo de referencia {formatoMillones(base['costo_total'])})."):
        nombres = {a["id"]: a["nombre"] for a in red["agroempresas"]} | {p["id"]: p["municipio"] for p in red["plantas"]}
        st.dataframe(pd.DataFrame([{
            "Ruta": f"{nombres[r['agroempresa_id']]} → {nombres[r['planta_id']]}", "En uso": r["toneladas"],
            "Costo": formatoPesos(r["costo_unitario"]), "Costo reducido": formatoPesos(r["costo_reducido"]),
            "Mínimo": formatoPesos(r["rango"]["minimo"]) if r["rango"]["minimo"] is not None else "sin límite",
            "Máximo": formatoPesos(r["rango"]["maximo"]) if r["rango"]["maximo"] is not None else "sin límite"}
            for r in base["rutas"]]),
            hide_index=True, width="stretch", height=360,
            column_config={"En uso": st.column_config.NumberColumn(format="%.1f t")})
