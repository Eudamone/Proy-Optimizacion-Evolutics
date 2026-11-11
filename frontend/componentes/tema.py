"""Tema "Despacho del Llano": colores, tipografías, CSS mínimo y formatos de cifras.

Los colores salen de la skill de dirección creativa: verde sabana para acciones
y plantas, ocre para agroempresas, azul río para el método exacto y rojo
tierra para el algoritmo genético y las rutas.
"""

import streamlit as st

COLORES = {
    "fondo": "#EEF2EB",
    "superficie": "#FFFFFF",
    "linea": "#D5DDD2",
    "tinta": "#1B2620",
    "tintaSuave": "#55645A",
    "verdeSabana": "#1E5B43",
    "ocre": "#D49A2A",
    "rio": "#9CC2CF",
    "contorno": "#D6DFD2",
    "exacto": "#2B78B4",
    "genetico": "#C2582A",
    "bien": "#1F7A3E",
    "bienSuave": "#E1F2E6",
    "alerta": "#9A5B00",
    "alertaSuave": "#FBEFD6",
    "error": "#B42318",
    "errorSuave": "#FBE4E1",
}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=Source+Sans+3:wght@400;600;700&display=swap');
h1, h2, h3, .titular {{ font-family: 'Bricolage Grotesque', 'Source Sans 3', sans-serif !important; letter-spacing: -0.02em; }}
[data-testid="stMarkdownContainer"] p.titular, .titular {{ font-size: 2.4rem !important; font-weight: 800; line-height: 1.08; color: {COLORES['tinta']}; margin: 0 0 .2rem 0; }}
[data-testid="stMarkdownContainer"] p.subtitular, .subtitular {{ font-size: 1.1rem !important; color: {COLORES['tintaSuave']}; margin: 0 0 1rem 0; }}
.cifra, .kpi-valor {{ font-variant-numeric: tabular-nums; }}
.kpi {{ background: {COLORES['superficie']}; border: 1px solid {COLORES['linea']}; border-radius: 10px;
        padding: 14px 16px; height: 100%; }}
.kpi.destacada {{ border-color: {COLORES['verdeSabana']}; background: #E3EFE7; }}
.kpi-etiqueta {{ font-size: .9rem; color: {COLORES['tintaSuave']}; }}
.kpi-valor {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.9rem; line-height: 1.15;
              color: {COLORES['tinta']}; }}
.kpi-detalle {{ font-size: .85rem; color: {COLORES['tintaSuave']}; }}
.estado {{ display: flex; gap: .55rem; align-items: flex-start; padding: .65rem .9rem; border-radius: 8px;
           font-size: .98rem; margin-bottom: .8rem; }}
.estado.bien {{ background: {COLORES['bienSuave']}; color: {COLORES['bien']}; }}
.estado.alerta {{ background: {COLORES['alertaSuave']}; color: {COLORES['alerta']}; }}
.estado.error {{ background: {COLORES['errorSuave']}; color: {COLORES['error']}; }}
.estado b {{ color: {COLORES['tinta']}; }}
.barra-capacidad {{ display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; font-size: .95rem; }}
.barra-capacidad .fila {{ display: flex; justify-content: space-between; gap: 8px; }}
.barra-capacidad .pista {{ height: 8px; background: #DCE3D8; border-radius: 4px; overflow: hidden; }}
.barra-capacidad .uso {{ height: 8px; background: {COLORES['verdeSabana']}; border-radius: 4px; }}
.ruta-cargada {{ display: flex; justify-content: space-between; gap: 10px; padding: 7px 0;
                 border-bottom: 1px solid {COLORES['linea']}; font-size: .95rem; }}
.ruta-cargada b {{ font-variant-numeric: tabular-nums; }}
.marca-lateral {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.25rem; line-height: 1.1; }}
.marca-lateral small {{ display: block; font-family: 'Source Sans 3', sans-serif; font-weight: 400; font-size: .85rem;
                        color: {COLORES['tintaSuave']}; }}
/* ---- distribución general ---- */
.block-container {{ padding-top: 2.2rem !important; padding-bottom: 3rem !important; max-width: 1240px; }}
[data-testid="stSidebar"] {{ background: #EAF0EC; border-right: 1px solid {COLORES['linea']}; }}
[data-testid="stSidebarHeader"] {{ display: none; }}
/* barra lateral fija: siempre visible, sin botones para ocultarla ni borde para cambiar su ancho */
[data-testid="stSidebar"] {{ width: 300px !important; min-width: 300px !important; max-width: 300px !important;
    transform: none !important; margin-left: 0 !important; visibility: visible !important; }}
[data-testid="stSidebarCollapseButton"], [data-testid="stExpandSidebarButton"],
[data-testid="stSidebarResizeHandle"] {{ display: none !important; }}
@media (max-width: 1279px) {{ .block-container {{ padding-left: 2rem !important; padding-right: 2rem !important; }} }}
/* en pantallas angostas Streamlit pone la barra encima del contenido: se corre el contenido a su derecha */
@media (max-width: 767px) {{ [data-testid="stMain"] {{ margin-left: 300px; max-width: calc(100vw - 300px); }} }}
/* ---- tarjetas: st.container(key="tarjeta...") ---- */
[class*="st-key-tarjeta"] {{ background: {COLORES['superficie']}; border: 1px solid {COLORES['linea']};
    border-radius: 12px; padding: 18px 20px 14px 20px; }}
.titulo-tarjeta {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.15rem;
    color: {COLORES['tinta']}; margin: 0 0 .1rem 0; }}
.nota-tarjeta {{ font-size: .9rem; color: {COLORES['tintaSuave']}; margin: 0 0 .4rem 0; }}
/* ---- encabezado de página ---- */
[data-testid="stMarkdownContainer"] p.titulo-pagina {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
    font-size: 2.3rem !important; line-height: 1.1; letter-spacing: -0.02em; color: {COLORES['tinta']}; margin: 0; }}
[data-testid="stMarkdownContainer"] p.sub-pagina {{ font-size: 1.08rem !important; color: {COLORES['tintaSuave']};
    margin: .3rem 0 .9rem 0; }}
/* ---- barra lateral ---- */
.marca {{ display: flex; gap: 12px; align-items: center; padding: 6px 4px 14px 4px; }}
.marca .logo {{ width: 40px; height: 40px; flex: none; }}
.marca b {{ font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.02rem; line-height: 1.15; display: block; }}
.marca span {{ font-size: .85rem; color: {COLORES['tintaSuave']}; }}
.red-activa {{ font-size: .9rem; color: {COLORES['tintaSuave']}; display: grid; gap: 9px; padding: 4px 4px; }}
.red-activa .fila {{ display: flex; justify-content: space-between; }}
.red-activa .fila b {{ color: {COLORES['tinta']}; font-weight: 600; font-variant-numeric: tabular-nums; }}
.red-activa .titulo {{ color: {COLORES['tinta']}; font-weight: 600; }}
.red-activa .ok {{ display: flex; gap: 6px; align-items: center; color: {COLORES['bien']}; font-weight: 600; }}
.red-activa .mal {{ display: flex; gap: 6px; align-items: center; color: {COLORES['error']}; font-weight: 600; }}
/* ---- tablas propias ---- */
.tabla {{ width: 100%; border-collapse: collapse; font-size: .95rem; font-variant-numeric: tabular-nums; }}
.tabla th {{ text-align: left; font-weight: 600; color: {COLORES['tintaSuave']}; padding: 8px; border-bottom: 1px solid {COLORES['linea']}; }}
.tabla td {{ padding: 9px 8px; border-bottom: 1px solid #E4EAE6; }}
.tabla tr:last-child td {{ border-bottom: none; }}
.tabla .n {{ text-align: right; }}
.metodo {{ display: inline-flex; gap: 8px; align-items: center; }}
.metodo i {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; }}
.pastilla {{ background: {COLORES['bienSuave']}; color: {COLORES['bien']}; font-weight: 600; font-size: .82rem;
    padding: 2px 10px; border-radius: 999px; white-space: nowrap; }}
.pastilla.mal {{ background: {COLORES['errorSuave']}; color: {COLORES['error']}; }}
.matriz {{ border-collapse: separate; border-spacing: 3px; width: 100%; font-size: .86rem; font-variant-numeric: tabular-nums; }}
.matriz th {{ font-weight: 600; color: {COLORES['tintaSuave']}; padding: 2px 6px; text-align: center; }}
.matriz th.fila {{ text-align: left; font-weight: 400; color: {COLORES['tinta']}; white-space: nowrap; }}
.matriz td {{ text-align: center; padding: 6px 4px; border-radius: 3px; }}
.escala {{ display: flex; gap: 8px; align-items: center; font-size: .8rem; color: {COLORES['tintaSuave']}; margin-top: 6px; }}
.escala span.barra {{ display: flex; height: 10px; width: 160px; border-radius: 3px; overflow: hidden; }}
.escala span.barra i {{ flex: 1; }}
[data-testid="stExpander"] details {{ background: {COLORES['superficie']}; border-radius: 12px !important; }}
[data-testid="stExpander"] summary p {{ font-weight: 600; font-size: 1rem; }}
.vacio {{ border: 1px dashed {COLORES['linea']}; border-radius: 12px; padding: 22px; color: {COLORES['tintaSuave']};
    text-align: center; background: rgba(255,255,255,.5); }}
</style>
"""

ICONOS = {
    "bien": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" style="flex:none;margin-top:3px">'
            '<circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/>'
            '<path d="M5 8.3l2 2 4-4.3" fill="none" stroke="currentColor" stroke-width="1.6"/></svg>',
    "alerta": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" style="flex:none;margin-top:3px">'
              '<path d="M8 1.8l6.6 12H1.4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>'
              '<path d="M8 6.3v3.6M8 11.7v.3" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    "error": '<svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" style="flex:none;margin-top:3px">'
             '<circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.6"/>'
             '<path d="M5.6 5.6l4.8 4.8M10.4 5.6l-4.8 4.8" stroke="currentColor" stroke-width="1.6"/></svg>',
}


def aplicarTema() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ---- formatos colombianos ----

def formatoPesos(valor: float) -> str:
    """$33.263.400"""
    return "$" + f"{valor:,.0f}".replace(",", ".")


def formatoDiferencia(valor: float) -> str:
    """+$318.000 / -$652.000"""
    return ("+" if valor > 0 else "-" if valor < 0 else "") + formatoPesos(abs(valor))


def formatoMillones(valor: float, decimales: int = 2) -> str:
    """$33,26 M"""
    return "$" + f"{valor / 1e6:,.{decimales}f}".replace(",", "X").replace(".", ",").replace("X", ".") + " M"


def formatoNumero(valor: float, decimales: int = 0) -> str:
    texto = f"{valor:,.{decimales}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def formatoPorcentaje(valor: float, decimales: int = 2) -> str:
    if 0 < valor < 10 ** -decimales:
        return "< " + formatoNumero(10 ** -decimales, decimales) + " %"
    return formatoNumero(valor, decimales) + " %"


def formatoToneladas(valor: float) -> str:
    return formatoNumero(valor, 0 if abs(valor - round(valor)) < 1e-6 else 1) + " t"
