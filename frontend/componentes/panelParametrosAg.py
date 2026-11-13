import streamlit as st

SELECCIONES = {"Torneo (k = 3)": "torneo", "Ruleta": "ruleta"}
CRUCES = {"Un punto": "un_punto", "Dos puntos": "dos_puntos"}
MUTACIONES = {"Poda (cierra rutas)": "poda", "Uniforme": "uniforme"}


def mostrarPanelParametrosAg(clave: str = "ag") -> tuple[dict, int]:
    """Devuelve (parámetros del AG para la API, número de corridas)."""
    c1, c2, c3, c4, c5 = st.columns(5)
    poblacion = c1.slider("Tamaño de población", 20, 300, 80, 10, key=f"{clave}Poblacion")
    generaciones = c2.slider("Generaciones", 20, 600, 150, 10, key=f"{clave}Generaciones")
    pCruce = c3.slider("Probabilidad de cruce", 0.0, 1.0, 0.85, 0.05, key=f"{clave}PCruce")
    pMutacion = c4.slider("Probabilidad de mutación", 0.0, 0.3, 0.05, 0.01, key=f"{clave}PMutacion")
    seleccion = c5.selectbox("Selección", list(SELECCIONES), key=f"{clave}Seleccion")

    c6, c7, c8, _ = st.columns([1, 1, 1, 2])
    cruce = c6.selectbox("Cruce", list(CRUCES), key=f"{clave}Cruce")
    mutacion = c7.selectbox("Mutación", list(MUTACIONES), key=f"{clave}Mutacion")
    corridas = c8.number_input("Corridas con semillas distintas", 1, 30, 10, key=f"{clave}Corridas")

    with st.expander("Opciones avanzadas"):
        a1, a2, a3 = st.columns(3)
        elitismo = a1.number_input("Élite que pasa sin cambios", 0, 20, 2, key=f"{clave}Elitismo")
        kTorneo = a2.number_input("Tamaño del torneo", 2, 10, 3, key=f"{clave}KTorneo")
        semilla = a3.number_input("Primera semilla", 0, 10_000, 0, key=f"{clave}Semilla")

    parametros = {
        "poblacion": int(poblacion),
        "generaciones": int(generaciones),
        "p_cruce": float(pCruce),
        "p_mutacion": float(pMutacion),
        "elitismo": int(elitismo),
        "k_torneo": int(kTorneo),
        "seleccion": SELECCIONES[seleccion],
        "cruce": CRUCES[cruce],
        "mutacion": MUTACIONES[mutacion],
        "semilla": int(semilla),
    }
    return parametros, int(corridas)
