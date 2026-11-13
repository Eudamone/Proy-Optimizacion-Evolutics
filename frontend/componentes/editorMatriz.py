import math
from typing import Optional

import pandas as pd
import streamlit as st

TIPOS_RESIDUO = ["PALMA", "ARROZ", "GANADERIA", "AGRICOLA", "FORESTAL"]


# ---- de la red (JSON) a tablas ----

def tablaAgroempresas(red: dict) -> pd.DataFrame:
    columnas = ["id", "nombre", "municipio", "tipo_residuo", "oferta_t", "lat", "lon"]
    return pd.DataFrame([{c: a.get(c) for c in columnas} for a in red["agroempresas"]], columns=columnas)


def tablaPlantas(red: dict) -> pd.DataFrame:
    columnas = ["id", "nombre", "municipio", "capacidad_t", "costo_operacion", "activa", "lat", "lon"]
    return pd.DataFrame([{c: p.get(c) for c in columnas} for p in red["plantas"]], columns=columnas)


def diccionarioRutas(red: dict) -> tuple[dict, dict]:
    distancias = {(r["agroempresa_id"], r["planta_id"]): r["distancia_km"] for r in red["rutas"]}
    habilitadas = {(r["agroempresa_id"], r["planta_id"]): r["habilitada"] for r in red["rutas"]}
    return distancias, habilitadas


# ---- editores ----

def editarAgroempresas(df: pd.DataFrame, clave: str) -> pd.DataFrame:
    return st.data_editor(
        df, key=clave, num_rows="dynamic", width="stretch", hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("Código", required=True, help="Por ejemplo A11"),
            "nombre": st.column_config.TextColumn("Agroempresa", required=True, width="large"),
            "municipio": st.column_config.TextColumn("Municipio", required=True),
            "tipo_residuo": st.column_config.SelectboxColumn("Residuo", options=TIPOS_RESIDUO, required=True),
            "oferta_t": st.column_config.NumberColumn("Oferta (t/semana)", min_value=0, step=1, required=True),
            "lat": st.column_config.NumberColumn("Latitud", format="%.4f"),
            "lon": st.column_config.NumberColumn("Longitud", format="%.4f"),
        },
    )


def editarPlantas(df: pd.DataFrame, clave: str) -> pd.DataFrame:
    return st.data_editor(
        df, key=clave, num_rows="dynamic", width="stretch", hide_index=True,
        column_config={
            "id": st.column_config.TextColumn("Código", required=True, help="Por ejemplo P05"),
            "nombre": st.column_config.TextColumn("Planta", required=True, width="large"),
            "municipio": st.column_config.TextColumn("Municipio", required=True),
            "capacidad_t": st.column_config.NumberColumn("Capacidad (t/semana)", min_value=0, step=1, required=True),
            "costo_operacion": st.column_config.NumberColumn("Operación ($/t)", min_value=0, step=100,
                                                             format="$%d", required=True),
            "activa": st.column_config.CheckboxColumn("Activa", default=True),
            "lat": st.column_config.NumberColumn("Latitud", format="%.4f"),
            "lon": st.column_config.NumberColumn("Longitud", format="%.4f"),
        },
    )


def editarRutas(agroempresas: pd.DataFrame, plantas: pd.DataFrame, distancias: dict, habilitadas: dict,
                clave: str) -> tuple[dict, dict]:
    idsAgro = [i for i in agroempresas["id"].tolist() if isinstance(i, str) and i]
    idsPlanta = [i for i in plantas["id"].tolist() if isinstance(i, str) and i]
    nombres = dict(zip(agroempresas["id"], agroempresas["nombre"]))
    etiquetas = {pid: f"{pid} · {mun}" for pid, mun in zip(plantas["id"], plantas["municipio"])}
    estructura = f"{clave}-{hash((tuple(idsAgro), tuple(idsPlanta)))}"

    filas = [{"Agroempresa": f"{a} · {nombres.get(a, '')}",
              **{p: distancias.get((a, p)) for p in idsPlanta}} for a in idsAgro]
    st.caption("Distancia por carretera en km. Una celda vacía hace que la red no se pueda guardar.")
    editadas = st.data_editor(
        pd.DataFrame(filas, columns=["Agroempresa"] + idsPlanta), key=f"{estructura}-km",
        width="stretch", hide_index=True, disabled=["Agroempresa"],
        column_config={p: st.column_config.NumberColumn(etiquetas.get(p, p), min_value=0, step=0.1, format="%.1f")
                       for p in idsPlanta},
    )

    filasHab = [{"Agroempresa": f"{a} · {nombres.get(a, '')}",
                 **{p: habilitadas.get((a, p), True) for p in idsPlanta}} for a in idsAgro]
    st.caption("Rutas habilitadas. Una ruta deshabilitada no se usa (su costo pasa a ser Gran M).")
    editadasHab = st.data_editor(
        pd.DataFrame(filasHab, columns=["Agroempresa"] + idsPlanta), key=f"{estructura}-hab",
        width="stretch", hide_index=True, disabled=["Agroempresa"],
        column_config={p: st.column_config.CheckboxColumn(etiquetas.get(p, p)) for p in idsPlanta},
    )

    nuevasDistancias, nuevasHabilitadas = {}, {}
    for k, a in enumerate(idsAgro):
        for p in idsPlanta:
            valor = editadas.iloc[k][p]
            if valor is not None and not (isinstance(valor, float) and math.isnan(valor)):
                nuevasDistancias[(a, p)] = float(valor)
            nuevasHabilitadas[(a, p)] = bool(editadasHab.iloc[k][p])
    return nuevasDistancias, nuevasHabilitadas


# ---- de tablas a la red (JSON) ----

def _limpio(valor) -> Optional[float]:
    if valor is None or (isinstance(valor, float) and math.isnan(valor)):
        return None
    return float(valor)


def construirRed(agroempresas: pd.DataFrame, plantas: pd.DataFrame, distancias: dict, habilitadas: dict,
                 parametros: dict) -> dict:
    agro = [
        {"id": str(f["id"]).strip(), "nombre": f["nombre"], "municipio": f["municipio"],
         "tipo_residuo": f["tipo_residuo"], "oferta_t": _limpio(f["oferta_t"]) or 0.0,
         "lat": _limpio(f["lat"]), "lon": _limpio(f["lon"])}
        for _, f in agroempresas.iterrows() if isinstance(f["id"], str) and f["id"].strip()
    ]
    plantasLista = [
        {"id": str(f["id"]).strip(), "nombre": f["nombre"], "municipio": f["municipio"],
         "capacidad_t": _limpio(f["capacidad_t"]) or 0.0, "costo_operacion": _limpio(f["costo_operacion"]) or 0.0,
         "activa": bool(f["activa"]) if f["activa"] is not None else True,
         "lat": _limpio(f["lat"]), "lon": _limpio(f["lon"])}
        for _, f in plantas.iterrows() if isinstance(f["id"], str) and f["id"].strip()
    ]
    rutas = [
        {"agroempresa_id": a["id"], "planta_id": p["id"], "distancia_km": distancias[(a["id"], p["id"])],
         "habilitada": habilitadas.get((a["id"], p["id"]), True)}
        for a in agro for p in plantasLista if (a["id"], p["id"]) in distancias
    ]
    return {"agroempresas": agro, "plantas": plantasLista, "rutas": rutas, "parametros": parametros}
