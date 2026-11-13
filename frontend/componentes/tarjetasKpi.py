"""Titulares, avisos de estado, tarjetas KPI, barras de capacidad y rutas más cargadas."""

from html import escape
from typing import Optional

import streamlit as st

from componentes.tema import ICONOS, formatoToneladas


def mostrarTitular(titular: str, subtitulo: Optional[str] = None) -> None:
    """Cada pantalla abre con un titular que cuenta el resultado."""
    html = f'<p class="titular">{escape(titular)}</p>'
    if subtitulo:
        html += f'<p class="subtitular">{escape(subtitulo)}</p>'
    st.markdown(html, unsafe_allow_html=True)


def mostrarEstado(tipo: str, titulo: str, detalle: str = "") -> None:
    """tipo: bien, alerta o error. Siempre con ícono y texto, no solo color."""
    texto = f"<b>{escape(titulo)}</b> {escape(detalle)}" if detalle else f"<b>{escape(titulo)}</b>"
    st.markdown(f'<div class="estado {tipo}">{ICONOS[tipo]}<span>{texto}</span></div>', unsafe_allow_html=True)


def mostrarErrores(errores: list[str]) -> None:
    for error in errores:
        mostrarEstado("error", "", error)


ICONOS_KPI = {
    "ruta": '<svg width="22" height="20" viewBox="0 0 22 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
            '<circle cx="4" cy="16" r="2.5"/><circle cx="18" cy="4" r="2.5"/><path d="M6 15c6-1 3-9 10-10" stroke-dasharray="3 3"/></svg>',
    "camion": '<svg width="26" height="18" viewBox="0 0 26 18" aria-hidden="true"><path d="M1 3h14v10H1zM15 7h6l4 4v2h-10z" '
              'fill="currentColor"/><circle cx="6" cy="15" r="2.4" fill="currentColor"/><circle cx="20" cy="15" r="2.4" fill="currentColor"/></svg>',
    "planta": '<svg width="20" height="18" viewBox="0 0 22 20" aria-hidden="true"><path d="M1 19V9l5 3V9l5 3V9l5 3V2h4v17z" fill="currentColor"/></svg>',
    "reloj": '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
             '<circle cx="10" cy="11" r="7"/><path d="M10 11V7M8 2h4"/></svg>',
    "historial": '<svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
                 '<path d="M3 10a7 7 0 1 0 2-5M3 3v3h3M10 6v4l3 2"/></svg>',
    "tonelada": '<svg width="22" height="18" viewBox="0 0 22 18" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
                '<path d="M3 17h16l-2-10H5zM8 7a3 3 0 0 1 6 0"/></svg>',
}


def tarjetasKpi(tarjetas: list[dict]) -> None:
    """tarjetas: [{"etiqueta", "valor", "detalle", "destacada", "icono", "ag"}]; solo una debería ir destacada.
    icono: clave de ICONOS_KPI; ag=True pinta el valor con el color del algoritmo genético."""
    columnas = st.columns(len(tarjetas))
    for columna, t in zip(columnas, tarjetas):
        clase = "kpi" + (" destacada" if t.get("destacada") else "") + (" ag" if t.get("ag") else "")
        icono = f'<span class="kpi-icono">{ICONOS_KPI[t["icono"]]}</span>' if t.get("icono") else ""
        columna.markdown(
            f'<div class="{clase}">{icono}<div class="kpi-etiqueta">{escape(t["etiqueta"])}</div>'
            f'<div class="kpi-valor">{escape(t["valor"])}</div>'
            f'<div class="kpi-detalle">{escape(t.get("detalle", ""))}</div></div>',
            unsafe_allow_html=True,
        )


CHIP_LLENA = '<span class="chip">llena</span>'


def barrasCapacidad(plantas: list[dict]) -> None:
    """plantas: [{"nombre", "usada", "capacidad"}] -> "140 / 140 t · llena"."""
    html = ""
    for p in plantas:
        capacidad = p["capacidad"]
        uso = 0 if capacidad <= 0 else min(100.0, p["usada"] / capacidad * 100)
        llena = capacidad > 0 and p["usada"] >= capacidad - 1e-6
        if capacidad <= 0:
            estado = "inactiva"
        elif llena:
            estado = "llena"
        else:
            estado = f"{formatoToneladas(capacidad - p['usada'])} libres"
        html += (
            f'<div class="barra-capacidad"><div class="fila"><span><span class="ico-planta">{ICONOS_KPI["planta"]}</span>'
            f'{escape(p["nombre"])}{CHIP_LLENA if llena else ""}</span>'
            f'<span class="cifra">{formatoToneladas(p["usada"])} / {formatoToneladas(capacidad)}'
            f'{"" if llena else " · " + estado}</span></div>'
            f'<div class="pista"><div class="uso{" llena" if llena else ""}" style="width:{uso:.1f}%"></div></div></div>'
        )
    st.markdown(html, unsafe_allow_html=True)


def rutasCargadas(rutas: list[tuple[str, str, float]], cuantas: int = 3) -> None:
    """rutas: [(origen, destino, toneladas)] ya ordenadas de mayor a menor."""
    html = "".join(
        f'<div class="ruta-cargada"><span>{escape(o)} → {escape(d)}</span>'
        f'<b>{formatoToneladas(t)}<span class="ico-camion">{ICONOS_KPI["camion"]}</span></b></div>'
        for o, d, t in rutas[:cuantas]
    )
    st.markdown(html, unsafe_allow_html=True)


# ---- estructura de página ----

def encabezado(titulo: str, subtitulo: str = "", textoBoton: Optional[str] = None, clave: str = "accion",
               icono: Optional[str] = None) -> bool:
    """Título a la izquierda y la acción principal de la pantalla a la derecha. Devuelve True si se pulsa."""
    if textoBoton is None:
        st.markdown(f'<p class="titulo-pagina">{escape(titulo)}</p><p class="sub-pagina">{escape(subtitulo)}</p>',
                    unsafe_allow_html=True)
        return False
    izquierda, derecha = st.columns([3.2, 1], vertical_alignment="center")
    izquierda.markdown(f'<p class="titulo-pagina">{escape(titulo)}</p><p class="sub-pagina">{escape(subtitulo)}</p>',
                       unsafe_allow_html=True)
    return derecha.button(textoBoton, type="primary", key=clave, icon=icono, width="stretch")


def tarjeta(clave: str, titulo: Optional[str] = None, nota: Optional[str] = None, ayuda: Optional[str] = None):
    """Contenedor blanco con borde. Uso: with tarjeta("convergencia", "Título"): ...
    ayuda: explicación que aparece al pasar el mouse por el ícono ⓘ junto al título."""
    contenedor = st.container(key=f"tarjeta{clave[0].upper()}{clave[1:]}")
    html = ""
    if titulo:
        icono = f' <span class="ayuda" title="{escape(ayuda)}">ⓘ</span>' if ayuda else ""
        html += f'<p class="titulo-tarjeta">{escape(titulo)}{icono}</p>'
    if nota:
        html += f'<p class="nota-tarjeta">{escape(nota)}</p>'
    if html:
        contenedor.markdown(html, unsafe_allow_html=True)
    return contenedor


def estadoVacio(texto: str) -> None:
    st.markdown(f'<div class="vacio">{escape(texto)}</div>', unsafe_allow_html=True)


# ---- tablas propias ----

def tablaResumenComparacion(comparacion: dict, colores: dict) -> None:
    """Exacto, mejor del AG y promedio del AG: costo, gap, desviación, tiempo y restricciones."""
    from componentes.tema import formatoMillones, formatoNumero, formatoPesos, formatoPorcentaje

    exacta, ag = comparacion["exacta"], comparacion["mejor_genetica"]
    filas = [
        (colores["exacto"], 1.0, "Exacto (Vogel + MODI)", comparacion["z_exacto"], "0,00 %", "—",
         f"{formatoNumero(comparacion['tiempos']['exacto'] * 1000, 1)} ms", exacta["factible"], "Cumple"),
        (colores["genetico"], 1.0, f"AG, mejor de {len(comparacion['costos_ag'])}", comparacion["z_ag_mejor"],
         formatoPorcentaje(comparacion["gap_pct"]), "—",
         f"{formatoNumero(comparacion['tiempos']['genetico_promedio'], 2)} s", ag["factible"], "Cumple"),
        (colores["genetico"], 0.5, f"AG, promedio de {len(comparacion['costos_ag'])}", comparacion["z_ag_promedio"],
         formatoPorcentaje(comparacion["gap_promedio_pct"]), formatoMillones(comparacion["desv_estandar"], 3),
         f"{formatoNumero(comparacion['tiempos']['genetico_promedio'], 2)} s", None, ""),
    ]
    html = ('<table class="tabla"><thead><tr><th>Método</th><th class="n">Costo semanal</th><th class="n">Gap</th>'
            '<th class="n">Desviación</th><th class="n">Tiempo</th><th>Restricciones</th></tr></thead><tbody>')
    for color, opacidad, nombre, costo, gap, desv, tiempo, factible, texto in filas:
        if factible is None:
            pastilla = "—"
        elif factible:
            pastilla = f'<span class="pastilla">{texto}</span>'
        else:
            pastilla = '<span class="pastilla mal">No cumple</span>'
        html += (f'<tr><td><span class="metodo"><i style="background:{color};opacity:{opacidad}"></i>{escape(nombre)}</span></td>'
                 f'<td class="n">{formatoPesos(costo)}</td><td class="n">{gap}</td><td class="n">{desv}</td>'
                 f'<td class="n">{tiempo}</td><td>{pastilla}</td></tr>')
    st.markdown(html + "</tbody></table>", unsafe_allow_html=True)


ESCALA_AZUL = [(0, "#F1F2F7", "#A3A7C2"), (20, "#CBD5EE", "#1A1C33"), (35, "#98ACDB", "#1A1C33"),
               (50, "#5B79BC", "#FFFFFF"), (float("inf"), "#2B2F6B", "#FFFFFF")]


def matrizAsignacion(red: dict, solucion: dict) -> None:
    """Toneladas x_ij como tabla de calor de un solo tono (más oscuro, más toneladas)."""
    plantas = red["plantas"]
    toneladas = {(f["agroempresa_id"], f["planta_id"]): f["toneladas"] for f in solucion["flujos"]}
    maximo = max(toneladas.values(), default=0)

    def colores(valor: float) -> tuple[str, str]:
        if valor <= 1e-9:
            return ESCALA_AZUL[0][1], ESCALA_AZUL[0][2]
        for tope, fondo, texto in ESCALA_AZUL[1:]:
            if valor < tope:
                return fondo, texto
        return ESCALA_AZUL[-1][1], ESCALA_AZUL[-1][2]

    html = '<div style="overflow-x:auto"><table class="matriz"><thead><tr><th class="fila">Agroempresa</th>'
    html += "".join(f"<th>{escape(p['municipio'])}</th>" for p in plantas) + "</tr></thead><tbody>"
    for a in red["agroempresas"]:
        html += f'<tr><th class="fila">{escape(a["nombre"])}</th>'
        for p in plantas:
            valor = toneladas.get((a["id"], p["id"]), 0)
            fondo, texto = colores(valor)
            etiqueta = "·" if valor <= 1e-9 else formatoToneladas(valor).replace(" t", "")
            peso = 400 if valor <= 1e-9 else 600
            html += f'<td style="background:{fondo};color:{texto};font-weight:{peso}">{etiqueta}</td>'
        html += "</tr>"
    html += "</tbody></table></div>"
    barra = "".join(f'<i style="background:{c[1]}"></i>' for c in ESCALA_AZUL)
    html += f'<div class="escala"><span>0 t</span><span class="barra">{barra}</span><span>{formatoToneladas(maximo)}</span></div>'
    st.markdown(html, unsafe_allow_html=True)


# ---- barra lateral ----

LOGO = ('<svg class="logo" viewBox="0 0 40 40" aria-hidden="true"><defs><radialGradient id="solLogo" cx=".5" cy=".7" r=".7">'
        '<stop offset="0" stop-color="#F7C068"/><stop offset="1" stop-color="#E4572E"/></radialGradient></defs>'
        '<circle cx="20" cy="20" r="20" fill="url(#solLogo)"/></svg>')


def marcaLateral() -> None:
    st.markdown(f'<div class="marca">{LOGO}<div><b>EcoResiduos del Llano</b>'
                '<span>Red logística de residuos</span></div></div>', unsafe_allow_html=True)


def redActiva(resumen: Optional[dict], error: Optional[str] = None) -> None:
    if resumen is None:
        st.markdown(f'<div class="red-activa"><div class="mal">{ICONOS["error"]}API sin conexión</div>'
                    f'<div>{escape(error or "")}</div></div>', unsafe_allow_html=True)
        return
    estado = (f'<div class="ok">{ICONOS["bien"]}API conectada</div>' if resumen["factible"]
              else f'<div class="mal">{ICONOS["alerta"]}Red no factible</div>')
    st.markdown(
        '<div class="red-activa"><div class="titulo">Red activa</div>'
        f'<div class="fila"><span>Agroempresas</span><b>{resumen["agroempresas"]}</b></div>'
        f'<div class="fila"><span>Plantas activas</span><b>{resumen["plantas_activas"]}</b></div>'
        f'<div class="fila"><span>Oferta semanal</span><b>{formatoToneladas(resumen["total_oferta_t"])}</b></div>'
        f'<div class="fila"><span>Capacidad</span><b>{formatoToneladas(resumen["total_capacidad_t"])}</b></div>'
        f'{estado}</div>', unsafe_allow_html=True)
