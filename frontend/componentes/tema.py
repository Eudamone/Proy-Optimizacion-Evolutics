"""Tema "Atardecer llanero": colores, tipografías, CSS y formatos de cifras.

Índigo de la noche llanera para la navegación, el indicador principal y las
plantas; naranja quemado del atardecer para la acción principal, el algoritmo
genético y las rutas; azul para el método exacto y naranja claro para las
agroempresas. Al pie de cada pantalla va el paisaje de la red (static/paisajeLlano.png).
"""

import streamlit as st

COLORES = {
    "fondo": "#EEF0F5",
    "superficie": "#FFFFFF",
    "linea": "#DCDFEA",
    "tinta": "#1A1C33",
    "tintaSuave": "#5C6080",
    "primario": "#2B2F6B",
    "acento": "#E4572E",
    "agro": "#F2A541",
    "rio": "#B7C4E0",
    "contorno": "#DCDFEA",
    "lateral": "#E6E8F1",
    "opcion": "#D4D8E8",
    "exacto": "#3A5BA0",
    "genetico": "#E4572E",
    "bien": "#1F7A4A",
    "bienSuave": "#E1F2E8",
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
.kpi {{ background: {COLORES['superficie']}; border: 1px solid {COLORES['linea']}; border-radius: 14px; transition: transform .15s, box-shadow .15s;
        padding: 14px 16px; height: 100%; }}
.kpi.destacada {{ border: none; background: linear-gradient(135deg, {COLORES['primario']}, #3A3F86); position: relative; overflow: hidden; }}
.kpi.destacada:after {{ content: ''; position: absolute; right: -40px; bottom: -70px; width: 160px; height: 160px; border-radius: 50%;
    background: radial-gradient(circle, #F2A541 0%, rgba(228,87,46,.6) 45%, transparent 70%); opacity: .5; }}
.kpi.destacada > * {{ position: relative; z-index: 1; }}
.kpi.destacada .kpi-etiqueta, .kpi.destacada .kpi-detalle {{ color: #D3D5EE; }}
.kpi:hover {{ transform: translateY(-2px); box-shadow: 0 6px 16px rgba(26,28,51,.08); }}
.kpi.destacada .kpi-valor {{ color: #FFFFFF; }}
.kpi-icono {{ float: right; color: #9A9EC4; }} .kpi.destacada .kpi-icono {{ color: #F2A541; position: relative; z-index: 1; }}
.kpi.ag .kpi-icono, .kpi.ag .kpi-valor {{ color: {COLORES['genetico']}; }}
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
.barra-capacidad .pista {{ height: 8px; background: #ECEEF4; border-radius: 5px; overflow: hidden; }}
.barra-capacidad .uso {{ height: 8px; background: {COLORES['primario']}; border-radius: 4px; }}
.barra-capacidad .uso.llena {{ background: linear-gradient(90deg, {COLORES['primario']}, {COLORES['acento']}); }}
.chip {{ font-size: .72rem; font-weight: 700; border-radius: 999px; padding: 1px 8px; margin-left: 6px; background: #FDE7DF; color: #B23F1C; }}
.ico-planta {{ color: {COLORES['primario']}; margin-right: 7px; vertical-align: -3px; }}
.ico-camion {{ color: {COLORES['acento']}; margin-left: 8px; vertical-align: -3px; }}
.ruta-cargada {{ display: flex; justify-content: space-between; gap: 10px; padding: 7px 0;
                 border-bottom: 1px solid {COLORES['linea']}; font-size: .95rem; }}
.ruta-cargada b {{ font-variant-numeric: tabular-nums; }}
.marca-lateral {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800; font-size: 1.25rem; line-height: 1.1; }}
.marca-lateral small {{ display: block; font-family: 'Source Sans 3', sans-serif; font-weight: 400; font-size: .85rem;
                        color: {COLORES['tintaSuave']}; }}
/* ---- distribución general ---- */
.block-container {{ padding-top: 2.2rem !important; padding-bottom: 3rem !important; max-width: 1240px; }}
[data-testid="stSidebar"] {{ background: {COLORES['lateral']}; border-right: 1px solid #D5D8E6; }}
/* opciones del menú: recuadro más oscuro; la activa en índigo con raya naranja */
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] {{ background: {COLORES['opcion']}; border: 1px solid #C6CBE0;
    border-radius: 10px; padding: 9px 12px; margin-bottom: 4px; transition: background .15s, transform .15s; }}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"]:hover {{ background: #C8CDE2; transform: translateX(2px); }}
[data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] span, [data-testid="stSidebar"] a[data-testid="stPageLink-NavLink"] p {{
    color: {COLORES['primario']} !important; font-weight: 600; }}
[data-testid="stSidebar"] .st-key-navActiva a[data-testid="stPageLink-NavLink"] {{
    background: {COLORES['primario']}; border-color: {COLORES['primario']};
    box-shadow: inset 4px 0 0 {COLORES['acento']}, 0 3px 10px rgba(43,47,107,.25); }}
[data-testid="stSidebar"] .st-key-navActiva a[data-testid="stPageLink-NavLink"] span, [data-testid="stSidebar"] .st-key-navActiva a[data-testid="stPageLink-NavLink"] p {{
    color: #FFFFFF !important; }}
/* botón principal con sombra cálida */
button[kind="primary"] {{ box-shadow: 0 4px 14px rgba(228,87,46,.32); transition: transform .15s, box-shadow .15s; }}
button[kind="primary"]:hover {{ transform: translateY(-1px); box-shadow: 0 6px 18px rgba(228,87,46,.4); }}
/* paisaje de la red al pie del contenido: detrás de las tarjetas, nunca encima */
[data-testid="stMain"] {{ background: url('app/static/paisajeLlano.png') center bottom / 100% auto no-repeat; }}
.block-container {{ padding-bottom: 210px !important; }}
@media (max-height: 700px) {{ [data-testid="stMain"] {{ background-image: none; }} .block-container {{ padding-bottom: 3rem !important; }} }}
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
    border-radius: 14px; padding: 18px 20px 14px 20px; }}
.titulo-tarjeta {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.15rem;
    color: {COLORES['tinta']}; margin: 0 0 .1rem 0; }}
.ayuda {{ font-family: 'Source Sans 3', sans-serif; font-weight: 400; font-size: .95rem; color: #9A9EC4; cursor: help; }}
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
.tabla td {{ padding: 9px 8px; border-bottom: 1px solid #ECEEF4; }}
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
