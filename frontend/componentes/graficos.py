import math
from typing import Optional

import plotly.graph_objects as go
import plotly.io as pio

from componentes.tema import COLORES, formatoMillones, formatoNumero, formatoPesos, formatoPorcentaje, formatoToneladas

COLOR_EXACTO = COLORES["exacto"]
COLOR_AG = COLORES["genetico"]
COLOR_PLANTA = COLORES["primario"]
COLOR_AGRO = COLORES["agro"]
FONDO_TARJETA = "#FFFFFF"  # las gráficas van dentro de tarjetas blancas

pio.templates["despachoLlano"] = go.layout.Template(layout=dict(
    font=dict(family="Source Sans 3, Segoe UI, sans-serif", size=14, color=COLORES["tinta"]),
    colorway=[COLOR_EXACTO, COLOR_AG],
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(gridcolor=COLORES["linea"], zeroline=False, linecolor=COLORES["linea"]),
    yaxis=dict(gridcolor=COLORES["linea"], zeroline=False, linecolor=COLORES["linea"]),
    hovermode="closest",
    hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=COLORES["linea"], font=dict(color=COLORES["tinta"])),
    legend=dict(orientation="h", y=1.1, x=0),
    margin=dict(l=10, r=10, t=40, b=10),
    separators=",.",
))
pio.templates.default = "despachoLlano"

# Trazados aproximados, solo como referencia visual del mapa (lon, lat).
RIOS = {
    "Río Meta": [(-73.45, 4.00), (-73.20, 4.03), (-72.96, 4.09), (-72.62, 4.18), (-72.30, 4.27),
                 (-72.08, 4.33), (-71.85, 4.45)],
    "Río Guayuriba": [(-73.98, 3.95), (-73.80, 3.99), (-73.62, 4.00), (-73.45, 4.00)],
    "Río Ariari": [(-73.98, 3.42), (-73.80, 3.52), (-73.65, 3.50), (-73.45, 3.38), (-73.25, 3.22)],
}
ETIQUETAS_RIOS = {"Río Meta": (-72.45, 4.32), "Río Ariari": (-73.45, 3.30)}
POSICION_ETIQUETA = {"Restrepo": "top left", "Villavicencio": "bottom left", "Granada": "middle left",
                     "Puerto Gaitán": "top center"}


# ---- mapa de despacho ----

def _curva(x1, y1, x2, y2, puntos=24, curvatura=0.18):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    cx, cy = mx - (y2 - y1) * curvatura, my + (x2 - x1) * curvatura
    xs, ys = [], []
    for k in range(puntos + 1):
        t = k / puntos
        xs.append((1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2)
        ys.append((1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2)
    return xs, ys


def _posicionesAgroempresas(agroempresas: list[dict], plantas: list[dict]) -> dict[str, tuple[float, float]]:
    posiciones = {}
    for a in agroempresas:
        lon, lat = a.get("lon"), a.get("lat")
        if lon is None or lat is None:
            continue
        if any(p.get("lon") is not None and abs(p["lon"] - lon) < 0.02 and abs(p["lat"] - lat) < 0.02
               for p in plantas):
            lon, lat = lon + 0.045, lat - 0.035
        posiciones[a["id"]] = (lon, lat)
    return posiciones


def _datosMapa(red: dict, solucion: dict, rutas: Optional[dict]) -> dict:
    agroempresas, plantas = red["agroempresas"], red["plantas"]
    usada: dict[str, float] = {}
    for f in solucion["flujos"]:
        usada[f["planta_id"]] = usada.get(f["planta_id"], 0) + f["toneladas"]
    return {
        "posAgro": _posicionesAgroempresas(agroempresas, plantas),
        "posPlanta": {p["id"]: (p["lon"], p["lat"]) for p in plantas if p.get("lon") is not None},
        "nombres": {a["id"]: a["nombre"] for a in agroempresas} | {p["id"]: p["nombre"] for p in plantas},
        "usada": usada,
        "tramos": {(t["agroempresa_id"], t["planta_id"]): t for t in (rutas or {}).get("tramos", [])},
    }


def _duracion(minutos: float) -> str:
    horas, resto = divmod(round(minutos), 60)
    return f"{horas} h {resto:02d} min" if horas else f"{resto} min"


def _recorrido(datos: dict, flujo: dict, curva: bool) -> tuple[list[float], list[float], str]:
    aid, pid = flujo["agroempresa_id"], flujo["planta_id"]
    (x1, y1), (x2, y2) = datos["posAgro"][aid], datos["posPlanta"][pid]
    tramo = datos["tramos"].get((aid, pid))
    if tramo:
        xs = [x1] + [lon for _, lon in tramo["puntos"]] + [x2]
        ys = [y1] + [lat for lat, _ in tramo["puntos"]] + [y2]
        extra = f"<br>{formatoNumero(tramo['distancia_km'], 0)} km por carretera · {_duracion(tramo['duracion_min'])}"
    elif curva:
        xs, ys = _curva(x1, y1, x2, y2)
        extra = ""
    else:
        xs, ys, extra = [x1, x2], [y1, y2], ""
    texto = (f"{datos['nombres'][aid]} → {datos['nombres'][pid]}<br>{formatoToneladas(flujo['toneladas'])} por semana"
             f"<br>{formatoPesos(flujo['costo_unitario'])} por tonelada{extra}")
    return xs, ys, texto


def _flujosDibujables(datos: dict, solucion: dict) -> list[dict]:
    return [f for f in sorted(solucion["flujos"], key=lambda f: f["toneladas"])
            if f["agroempresa_id"] in datos["posAgro"] and f["planta_id"] in datos["posPlanta"]]


def _grosor(toneladas: float) -> float:
    return 1.5 + toneladas / 5


def graficarMapaDespacho(red: dict, solucion: dict, alto: int = 520, rutas: Optional[dict] = None) -> go.Figure:
    """Mapa esquemático: funciona sin internet."""
    agroempresas, plantas = red["agroempresas"], red["plantas"]
    datos = _datosMapa(red, solucion, rutas)
    posAgro, posPlanta, usada = datos["posAgro"], datos["posPlanta"], datos["usada"]

    fig = go.Figure()
    for nombre, puntos in RIOS.items():
        fig.add_scatter(x=[p[0] for p in puntos], y=[p[1] for p in puntos], mode="lines",
                        line=dict(color=COLORES["rio"], width=4), hoverinfo="skip", showlegend=False)
        if nombre in ETIQUETAS_RIOS:
            x, y = ETIQUETAS_RIOS[nombre]
            fig.add_annotation(x=x, y=y, text=f"<i>{nombre}</i>", showarrow=False,
                               font=dict(size=12, color="#4A7D88"))

    for f in _flujosDibujables(datos, solucion):
        xs, ys, texto = _recorrido(datos, f, curva=True)
        fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=COLOR_AG, width=_grosor(f["toneladas"])),
                        opacity=0.85, hovertemplate=texto + "<extra></extra>", showlegend=False)

    fig.add_scatter(
        x=[posAgro[a["id"]][0] for a in agroempresas if a["id"] in posAgro],
        y=[posAgro[a["id"]][1] for a in agroempresas if a["id"] in posAgro],
        mode="markers", name="Agroempresa (tamaño según oferta)",
        marker=dict(color=COLOR_AGRO, size=[8 + math.sqrt(a["oferta_t"]) * 2.2 for a in agroempresas if a["id"] in posAgro],
                    line=dict(color="#FFFFFF", width=2)),
        text=[f"{a['nombre']}<br>{a['municipio']} · {formatoToneladas(a['oferta_t'])} por semana"
              for a in agroempresas if a["id"] in posAgro],
        hovertemplate="%{text}<extra></extra>",
    )
    fig.add_scatter(
        x=[posPlanta[p["id"]][0] for p in plantas if p["id"] in posPlanta],
        y=[posPlanta[p["id"]][1] for p in plantas if p["id"] in posPlanta],
        mode="markers+text", name="Planta de procesamiento",
        marker=dict(color=[COLOR_PLANTA if p["activa"] else "#9AA8A0" for p in plantas if p["id"] in posPlanta],
                    symbol="square", size=22, line=dict(color="#FFFFFF", width=2)),
        text=[f"<b>{p['municipio']}</b><br>{formatoToneladas(usada.get(p['id'], 0))} / {formatoToneladas(p['capacidad_t'])}"
              for p in plantas if p["id"] in posPlanta],
        textposition=[POSICION_ETIQUETA.get(p["municipio"], "middle left") for p in plantas if p["id"] in posPlanta],
        textfont=dict(size=13),
        hovertemplate="%{text}<extra></extra>",
    )
    fig.add_scatter(x=[None], y=[None], mode="lines", name="Ruta (grosor según toneladas)",
                    line=dict(color=COLOR_AG, width=6))

    fig.update_xaxes(visible=False, range=[-74.15, -71.85])
    fig.update_yaxes(visible=False, range=[3.2, 4.55], scaleanchor="x", scaleratio=1)
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=alto, legend=dict(orientation="h", y=-0.02, x=0, yanchor="top"),
                      margin=dict(l=0, r=0, t=10, b=40), dragmode="pan")
    return fig


# El mapa base usa las fuentes del estilo de CARTO, no las de la página.
FUENTE_MAPA = "Open Sans Bold"
POSICION_ETIQUETA_REAL = {"Restrepo": "top left", "Villavicencio": "bottom left", "Granada": "bottom left",
                          "Puerto Gaitán": "top left"}


def graficarMapaReal(red: dict, solucion: dict, rutas: Optional[dict] = None, alto: int = 520) -> go.Figure:
    """Mapa real con fondo de CARTO / OpenStreetMap: necesita internet."""
    agroempresas, plantas = red["agroempresas"], red["plantas"]
    datos = _datosMapa(red, solucion, rutas)
    posAgro, posPlanta, usada = datos["posAgro"], datos["posPlanta"], datos["usada"]

    fig = go.Figure()
    for i, f in enumerate(_flujosDibujables(datos, solucion)):
        xs, ys, texto = _recorrido(datos, f, curva=False)
        fig.add_scattermap(lon=xs, lat=ys, mode="lines", line=dict(color=COLOR_AG, width=_grosor(f["toneladas"])),
                           opacity=0.85, hovertemplate=texto + "<extra></extra>",
                           name="Ruta (grosor según toneladas)", legendgroup="rutas", showlegend=i == 0)

    agros = [a for a in agroempresas if a["id"] in posAgro]
    tamanos = [8 + math.sqrt(a["oferta_t"]) * 2.2 for a in agros]
    lon, lat = [posAgro[a["id"]][0] for a in agros], [posAgro[a["id"]][1] for a in agros]
    fig.add_scattermap(lon=lon, lat=lat, mode="markers", marker=dict(size=[t + 4 for t in tamanos], color="#FFFFFF"),
                       hoverinfo="skip", showlegend=False)  # borde blanco
    fig.add_scattermap(
        lon=lon, lat=lat, mode="markers", name="Agroempresa (tamaño según oferta)",
        marker=dict(size=tamanos, color=COLOR_AGRO),
        text=[f"{a['nombre']}<br>{a['municipio']} · {formatoToneladas(a['oferta_t'])} por semana" for a in agros],
        hovertemplate="%{text}<extra></extra>",
    )

    lista = [p for p in plantas if p["id"] in posPlanta]
    lon, lat = [posPlanta[p["id"]][0] for p in lista], [posPlanta[p["id"]][1] for p in lista]
    fig.add_scattermap(lon=lon, lat=lat, mode="markers", marker=dict(size=26, color="#FFFFFF"),
                       hoverinfo="skip", showlegend=False)  # borde blanco
    etiquetas = [f"{p['municipio']}  {formatoToneladas(usada.get(p['id'], 0))} / {formatoToneladas(p['capacidad_t'])}"
                 for p in lista]
    fig.add_scattermap(
        lon=lon, lat=lat, mode="markers", name="Planta de procesamiento",
        marker=dict(size=21, color=[COLOR_PLANTA if p["activa"] else "#9AA8A0" for p in lista]),
        text=etiquetas, hovertemplate="%{text}<extra></extra>",
    )
    for p, x, y, etiqueta in zip(lista, lon, lat, etiquetas):  # en el mapa real la posición del texto es una por traza
        fig.add_scattermap(lon=[x], lat=[y], mode="markers+text", text=[etiqueta], hoverinfo="skip", showlegend=False,
                           marker=dict(size=24, color="rgba(0,0,0,0)"),  # el texto se separa según este tamaño
                           textposition=POSICION_ETIQUETA_REAL.get(p["municipio"], "top left"),
                           textfont=dict(family=FUENTE_MAPA, size=13, color=COLORES["tinta"]))

    fig.update_layout(
        map=dict(style="carto-positron", center=dict(lat=3.9, lon=-72.98), zoom=7.9),
        height=alto, paper_bgcolor=FONDO_TARJETA, margin=dict(l=0, r=0, t=0, b=40),
        legend=dict(orientation="h", y=-0.02, x=0, yanchor="top"),
    )
    return fig


# ---- algoritmo genético ----

def graficarConvergencia(mejorCosto: list[float], costoPromedio: list[float], zExacto: float) -> go.Figure:
    generaciones = list(range(len(mejorCosto)))
    fig = go.Figure()
    fig.add_scatter(x=generaciones, y=[c / 1e6 for c in costoPromedio], name="Promedio de la población",
                    mode="lines", line=dict(color=COLOR_AG, width=2, dash="dot"), opacity=0.5,
                    hovertemplate="Generación %{x}<br>Promedio %{y:,.2f} M<extra></extra>")
    fig.add_scatter(x=generaciones, y=[c / 1e6 for c in mejorCosto], name="Mejor del algoritmo genético",
                    mode="lines", line=dict(color=COLOR_AG, width=2.5),
                    hovertemplate="Generación %{x}<br>Mejor %{y:,.2f} M<extra></extra>")
    fig.add_scatter(x=[0, generaciones[-1]], y=[zExacto / 1e6] * 2, name="Óptimo del método exacto (Z*)",
                    mode="lines", line=dict(color=COLOR_EXACTO, width=2, dash="dash"),
                    hovertemplate="Z* %{y:,.2f} M<extra></extra>")
    fig.update_xaxes(title="Generación")
    fig.update_yaxes(title="Costo semanal (millones de pesos)", tickformat=",.1f")
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=360)
    return fig


def graficarCorridas(costosAg: list[float], semillas: list[int], zExacto: float) -> go.Figure:
    """Puntos y no barras: el eje no empieza en 0."""
    fig = go.Figure()
    fig.add_scatter(x=[str(s) for s in semillas], y=[c / 1e6 for c in costosAg], mode="markers",
                    name="Corrida del algoritmo genético",
                    marker=dict(color=COLOR_AG, size=13, line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="Semilla %{x}<br>%{y:,.3f} M<extra></extra>")
    fig.add_hline(y=zExacto / 1e6, line=dict(color=COLOR_EXACTO, width=2, dash="dash"),
                  annotation_text=f"Z* {formatoMillones(zExacto)}", annotation_position="bottom right",
                  annotation_font_color=COLOR_EXACTO)
    fig.update_xaxes(title="Semilla de la corrida", type="category")
    fig.update_yaxes(title="Costo semanal (millones de pesos)", tickformat=",.2f")
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=320, showlegend=False)
    return fig


def graficarReglaCercania(gaps: list[float]) -> go.Figure:
    mejor, promedio, peor = min(gaps), sum(gaps) / len(gaps), max(gaps)
    tope = max(peor * 1.25, 0.5)
    fig = go.Figure()
    fig.add_scatter(x=[0, tope], y=[0, 0], mode="lines", line=dict(color=COLORES["linea"], width=2),
                    hoverinfo="skip", showlegend=False)
    fig.add_scatter(x=[0], y=[0], mode="markers+text", text=["Óptimo"], textposition="bottom center",
                    marker=dict(symbol="line-ns", size=26, line=dict(color=COLOR_EXACTO, width=4)),
                    hovertemplate="Método exacto: 0 %<extra></extra>", showlegend=False)
    etiquetas = [("Mejor", mejor, 1.0), ("Promedio", promedio, 0.45), ("Peor", peor, 0.45)]
    fig.add_scatter(x=[e[1] for e in etiquetas], y=[0, 0, 0], mode="markers+text",
                    text=[f"{e[0]}<br>{formatoPorcentaje(e[1])}" for e in etiquetas], textposition="top center",
                    marker=dict(color=COLOR_AG, size=16, opacity=[e[2] for e in etiquetas],
                                line=dict(color="#FFFFFF", width=2)),
                    hovertemplate="%{text}<extra></extra>", showlegend=False)
    fig.update_xaxes(range=[-tope * 0.05, tope], ticksuffix=" %", title="Distancia al óptimo (gap)", showgrid=False)
    fig.update_yaxes(visible=False, range=[-1.4, 1.6])
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=170, margin=dict(l=10, r=10, t=10, b=10))
    return fig


# ---- sensibilidad ----

def graficarCostoVsVariacion(pasos: list[dict], etiqueta: str) -> go.Figure:
    factibles = [p for p in pasos if p["factible"]]
    fig = go.Figure()
    fig.add_scatter(
        x=[p["delta"] for p in factibles], y=[p["costo_total"] / 1e6 for p in factibles],
        mode="lines+markers", name="Costo total (método exacto)",
        line=dict(color=COLOR_EXACTO, width=2.5),
        marker=dict(size=12, color=["#FFFFFF" if p["cambia_base"] else COLOR_EXACTO for p in factibles],
                    line=dict(color=COLOR_EXACTO, width=2.5)),
        customdata=[["sí" if p["cambia_base"] else "no"] for p in factibles],
        hovertemplate="Variación %{x} %<br>Costo %{y:,.2f} M<br>Cambian las rutas: %{customdata[0]}<extra></extra>",
    )
    for p in pasos:
        if not p["factible"]:
            fig.add_vline(x=p["delta"], line=dict(color=COLORES["error"], width=1, dash="dot"),
                          annotation_text="sin solución", annotation_font_color=COLORES["error"])
    fig.update_xaxes(title=f"Variación de {etiqueta} (%)", ticksuffix=" %")
    fig.update_yaxes(title="Costo semanal (millones de pesos)", tickformat=",.1f")
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=360, showlegend=False)
    return fig


def graficarAhorroCapacidad(capacidades: list[dict]) -> go.Figure:
    datos = sorted(capacidades, key=lambda c: c["ahorro_por_tonelada"])
    fig = go.Figure()
    fig.add_bar(y=[c["nombre"] for c in datos], x=[c["ahorro_por_tonelada"] for c in datos], orientation="h",
                marker=dict(color=COLOR_EXACTO), width=0.5,
                text=[formatoPesos(c["ahorro_por_tonelada"]) for c in datos], textposition="outside",
                cliponaxis=False, hovertemplate="%{y}: %{text} por tonelada<extra></extra>")
    tope = max([c["ahorro_por_tonelada"] for c in datos] + [1])
    fig.update_xaxes(title="Ahorro semanal por tonelada adicional de capacidad (pesos)", range=[0, tope * 1.3],
                     tickformat=",d")
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=280, showlegend=False, margin=dict(l=10, r=30, t=10, b=10))
    return fig


# ---- bitácora ----

def graficarCostoPorEjecucion(ejecuciones: list[dict]) -> go.Figure:
    orden = sorted(ejecuciones, key=lambda e: e["id"])
    etiquetas = [f"#{e['id']}" for e in orden]
    fig = go.Figure()
    fig.add_scatter(x=etiquetas, y=[e["z_exacto"] / 1e6 for e in orden], mode="markers+lines",
                    name="Método exacto", line=dict(color=COLOR_EXACTO, width=2),
                    marker=dict(size=11, color=COLOR_EXACTO), hovertemplate="%{x}<br>Exacto %{y:,.2f} M<extra></extra>")
    fig.add_scatter(x=etiquetas, y=[e["z_ag_mejor"] / 1e6 for e in orden], mode="markers+lines",
                    name="Mejor del algoritmo genético", line=dict(color=COLOR_AG, width=2),
                    marker=dict(size=11, color=COLOR_AG), hovertemplate="%{x}<br>AG %{y:,.2f} M<extra></extra>")
    fig.update_xaxes(title="Comparación", type="category")
    fig.update_yaxes(title="Costo semanal (millones de pesos)", tickformat=",.3f")
    fig.update_layout(paper_bgcolor=FONDO_TARJETA, plot_bgcolor=FONDO_TARJETA, height=320)
    return fig
