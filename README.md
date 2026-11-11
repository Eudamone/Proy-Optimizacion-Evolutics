# Proy-Optimizacion-Evolutics

Sistema de optimización de la red logística de recepción y procesamiento de residuos
agropecuarios de **EcoResiduos del Llano S.A.S.** Proyecto final de la asignatura
Optimización, Ingeniería de Sistemas, Universidad de los Llanos.

La red tiene 10 agroempresas (fuentes) y 4 plantas de procesamiento (Villavicencio,
Restrepo, Granada y Puerto Gaitán). El sistema resuelve el problema de transporte con
dos métodos programados sin librerías de optimización:

- **Método exacto:** solución inicial por Vogel y optimización con MODI.
- **Algoritmo genético:** codificación real, decodificación proporcional y aptitud
  penalizada por exceso de capacidad.

También calcula la sensibilidad (precios sombra, costos reducidos y rangos), simula
escenarios y compara los dos métodos por costo, tiempo y gap %.

## Arquitectura

Arquitectura cliente-servidor en tres capas; cada capa se comunica solo con la siguiente.

| Capa | Carpeta | Tecnología | Conexión |
|---|---|---|---|
| 1 · Presentación | `frontend/` | Streamlit + Plotly | HTTP · REST con JSON hacia la lógica (httpx) |
| 2 · Lógica | `backend/app/` | FastAPI | SQL hacia los datos, con SQLAlchemy |
| 3 · Datos | `backend/app/persistencia/` y `backend/datos/` | SQLite | |

Los paquetes `transporte`, `genetico` y `analisis` usan solo la biblioteca estándar de
Python (abc, dataclasses, enum, random, time y math).

## Estructura

```
Proy-Optimizacion-Evolutics/
├── frontend/                     1 · Capa de presentación (Streamlit)
│   ├── app.py                    navegación entre pantallas
│   ├── vistas/                   una pantalla por boceto
│   ├── componentes/              tablas editables, panel del AG, gráficos, KPI
│   ├── estado/                   EstadoUI (st.session_state)
│   ├── eventosUi/                callbacks de la interfaz
│   └── clienteApi/               cliente HTTP (httpx) hacia el backend
├── backend/
│   ├── app/                      2 · Capa de lógica (FastAPI)
│   │   ├── main.py               aplicación y routers
│   │   ├── controladores/        endpoints REST
│   │   ├── esquemas/             JSON de entrada y salida (Pydantic)
│   │   ├── servicios/            casos de uso
│   │   ├── dominio/              red, instancia y solución
│   │   ├── motores/              ISolver y SolverFactory
│   │   ├── transporte/           método exacto propio (Vogel + MODI)
│   │   ├── genetico/             algoritmo genético propio
│   │   ├── analisis/             sensibilidad, escenarios y comparador
│   │   ├── persistencia/         3 · Capa de datos: SQLAlchemy y repositorios
│   │   └── infraestructura/      configuración, eventos y tareas
│   ├── datos/                    base SQLite y datos de prueba (semilla/)
│   └── tests/                    pruebas unitarias
└── docs/                         diagramas, bocetos e informe
```

## Convenciones de nombres

| Elemento | Convención | Ejemplo |
|---|---|---|
| Archivos y carpetas | camelCase | `solverTransporte.py`, `eventosUi/` |
| Funciones y métodos | camelCase | `completarBase()`, `obtenerRed()` |
| Clases | PascalCase | `SolverTransporte`, `MetodoVogel` |
| Pruebas | `test` + camelCase | `testTransporte.py`, `testVogel()` |

`__init__.py` y `conftest.py` conservan el nombre que exigen Python y pytest.
`backend/pytest.ini` le indica a pytest que recoja los archivos `test*.py`.

## Correspondencia con los diagramas

| Paquete del diagrama de clases | Carpeta |
|---|---|
| dominio | `backend/app/dominio/` |
| motores | `backend/app/motores/` |
| transporte | `backend/app/transporte/` |
| genetico | `backend/app/genetico/` |
| analisis | `backend/app/analisis/` |

| Pantalla de los bocetos | Archivo |
|---|---|
| 1 · Parametrización | `frontend/vistas/parametrizacion.py` |
| 2 · Resolver y comparar | `frontend/vistas/resolverComparar.py` |
| 3 · Sensibilidad | `frontend/vistas/sensibilidad.py` |
| 4 · Reportes | `frontend/vistas/reportes.py` |

Los diagramas de secuencia siguen el recorrido controlador -> servicio -> dominio y
motores -> repositorio, con los mismos nombres de clase que usa el código.

## Cómo ejecutar

Instalación (una vez, desde la carpeta del proyecto):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Terminal 1, la API:

```bash
cd backend
uvicorn app.main:app --reload       # http://localhost:8000
```

Terminal 2, la interfaz:

```bash
cd frontend
streamlit run app.py                # http://localhost:8501
```

Pruebas: `pytest` desde la carpeta `backend`.

## Datos de prueba

`backend/datos/semilla/` trae una red de ejemplo con 10 agroempresas y 4 plantas del Meta
(373 t/semana de oferta y 420 t/semana de capacidad). Las coordenadas de los municipios son
aproximadas y las distancias se estimaron como la distancia en línea recta por 1,3 (mínimo 5 km
dentro del mismo municipio). La ruta Palmas del Ariari -> Planta Puerto Gaitán está bloqueada
para probar el caso de Gran M. Hay que reemplazarlos por los datos reales del caso cuando estén.

## Avance

- [x] Estructura de carpetas
- [x] Dominio y datos de prueba
- [ ] Método exacto (Vogel + MODI)
- [ ] Algoritmo genético
- [ ] Sensibilidad, escenarios y comparador
- [ ] Persistencia y API
- [ ] Interfaz en Streamlit
