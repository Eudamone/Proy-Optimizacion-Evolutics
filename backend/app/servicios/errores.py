"""ErrorNegocio: la petición es válida como JSON pero rompe una regla del negocio.

Los controladores la convierten en una respuesta 422 con la lista de errores.
"""


class ErrorNegocio(Exception):
    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class NoEncontrado(Exception):
    """El recurso pedido no existe (respuesta 404)."""
