from app.dominio.red import RedLogistica


class ValidadorRed:
    def __init__(self, tolerancia: float = 1e-9):
        self.tolerancia = tolerancia

    def validar(self, red: RedLogistica) -> list[str]:
        errores: list[str] = []
        errores += self._validarElementos(red)
        errores += self._validarRutas(red)
        errores += self._validarParametros(red)
        if not errores:
            errores += self._validarFactibilidad(red)
        return errores

    def _validarElementos(self, red: RedLogistica) -> list[str]:
        errores = []
        if not red.agroempresas:
            errores.append("La red no tiene agroempresas.")
        if not red.plantas:
            errores.append("La red no tiene plantas de procesamiento.")

        idsAgro = [a.id for a in red.agroempresas]
        idsPlanta = [p.id for p in red.plantas]
        for repetido in sorted({i for i in idsAgro if idsAgro.count(i) > 1}):
            errores.append(f"El id de agroempresa {repetido} está repetido.")
        for repetido in sorted({i for i in idsPlanta if idsPlanta.count(i) > 1}):
            errores.append(f"El id de planta {repetido} está repetido.")

        for a in red.agroempresas:
            if a.oferta_t < 0:
                errores.append(f"{a.nombre}: la oferta no puede ser negativa ({a.oferta_t} t).")
        for p in red.plantas:
            if p.capacidad_t <= 0:
                errores.append(f"{p.nombre}: la capacidad debe ser mayor que 0 ({p.capacidad_t} t).")
            if p.costo_operacion < 0:
                errores.append(f"{p.nombre}: el costo de operación no puede ser negativo.")
        return errores

    def _validarRutas(self, red: RedLogistica) -> list[str]:
        errores = []
        existentes = {(r.agroempresa_id, r.planta_id) for r in red.rutas}
        for a in red.agroempresas:
            for p in red.plantas:
                if (a.id, p.id) not in existentes:
                    errores.append(f"Falta la distancia de {a.nombre} a {p.nombre}.")
        for r in red.rutas:
            if r.distancia_km < 0:
                errores.append(f"La distancia {r.agroempresa_id} -> {r.planta_id} no puede ser negativa.")
        return errores

    def _validarParametros(self, red: RedLogistica) -> list[str]:
        tarifa = red.parametros.tarifa_t_km
        if tarifa is None:
            return ["Falta definir la tarifa de transporte ($ por tonelada-km)."]
        if tarifa <= 0:
            return ["La tarifa de transporte debe ser mayor que 0."]
        return []

    def _validarFactibilidad(self, red: RedLogistica) -> list[str]:
        errores = []
        oferta = red.totalOferta()
        capacidad = red.totalCapacidad()
        if oferta > capacidad + self.tolerancia:
            errores.append(
                f"La oferta ({oferta:g} t) supera la capacidad de las plantas activas "
                f"({capacidad:g} t) por {oferta - capacidad:g} t: activa una planta o sube su capacidad."
            )

        activas = {p.id for p in red.plantasActivas()}
        for a in red.agroempresas:
            if a.oferta_t <= 0:
                continue
            tieneSalida = any(
                r.habilitada and r.planta_id in activas
                for r in red.rutas
                if r.agroempresa_id == a.id
            )
            if not tieneSalida:
                errores.append(f"{a.nombre} no tiene ninguna ruta habilitada hacia una planta activa.")
        return errores
