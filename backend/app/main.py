"""Aplicación FastAPI (capa de lógica).

Al iniciar prepara la base SQLite y, si está vacía, carga los datos de prueba.
Ejecutar desde la carpeta backend:  uvicorn app.main:app --reload
Documentación interactiva:          http://localhost:8000/docs
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controladores import optimizacionController, redController, reportesController, sensibilidadController
from app.infraestructura.configuracion import obtenerConfiguracion
from app.persistencia.cargaInicial import cargarSiVacia
from app.persistencia.conexion import configurarBaseDatos, nuevaSesion
from app.servicios.errores import ErrorNegocio, NoEncontrado


def crearApp(urlBaseDatos: Optional[str] = None) -> FastAPI:
    config = obtenerConfiguracion()

    @asynccontextmanager
    async def ciclo(_: FastAPI):
        configurarBaseDatos(urlBaseDatos or config.urlBaseDatos)
        sesion = nuevaSesion()
        try:
            cargarSiVacia(sesion)
        finally:
            sesion.close()
        yield

    app = FastAPI(
        title="EcoResiduos del Llano · API de optimización",
        description="Red logística de residuos agropecuarios: método exacto (Vogel + MODI), "
                    "algoritmo genético, sensibilidad y escenarios.",
        version="1.0.0",
        lifespan=ciclo,
    )
    app.add_middleware(CORSMiddleware, allow_origins=config.origenesPermitidos,
                       allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(ErrorNegocio)
    async def manejarErrorNegocio(_: Request, error: ErrorNegocio):
        return JSONResponse(status_code=422, content={"errores": error.errores})

    @app.exception_handler(NoEncontrado)
    async def manejarNoEncontrado(_: Request, error: NoEncontrado):
        return JSONResponse(status_code=404, content={"errores": [str(error)]})

    @app.get("/salud", tags=["Sistema"], summary="Comprobar que la API responde")
    def salud():
        return {"estado": "ok"}

    for controlador in (redController, optimizacionController, sensibilidadController, reportesController):
        app.include_router(controlador.router)
    return app


app = crearApp()
