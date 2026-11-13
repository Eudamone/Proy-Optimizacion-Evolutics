class ErrorNegocio(Exception):
    def __init__(self, errores: list[str]):
        super().__init__("; ".join(errores))
        self.errores = errores


class NoEncontrado(Exception):
    pass
