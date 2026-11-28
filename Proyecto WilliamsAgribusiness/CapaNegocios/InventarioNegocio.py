from CapaDatos.InventarioDatos import InventarioDatos

class InventarioNegocio:

    # REGISTRAR ENTRADA
    @staticmethod
    def registrar_entrada(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        if not isinstance(id_inventario, int) or id_inventario <= 0:
            raise ValueError("El inventario seleccionado no es válido.")

        if cantidad is None or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        if not motivo or not motivo.strip():
            raise ValueError("Debe indicar el motivo de la entrada.")

        return InventarioDatos.registrar_entrada(
            id_inventario, cantidad, motivo.strip(), referencia, observaciones
        )

    # REGISTRAR SALIDA
    @staticmethod
    def registrar_salida(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        if not isinstance(id_inventario, int) or id_inventario <= 0:
            raise ValueError("El inventario seleccionado no es válido.")

        if cantidad is None or cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que cero.")

        if not motivo or not motivo.strip():
            raise ValueError("Debe indicar el motivo de la salida.")

        return InventarioDatos.registrar_salida(
            id_inventario, cantidad, motivo.strip(), referencia, observaciones
        )

    # REGISTRAR AJUSTE
    @staticmethod
    def registrar_ajuste(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        if not isinstance(id_inventario, int) or id_inventario <= 0:
            raise ValueError("El inventario seleccionado no es válido.")

        if cantidad is None or cantidad < 0:
            raise ValueError("La cantidad del ajuste no puede ser negativa.")

        if not motivo or not motivo.strip():
            raise ValueError("Debe indicar el motivo del ajuste.")

        return InventarioDatos.registrar_ajuste(
            id_inventario, cantidad, motivo.strip(), referencia, observaciones
        )

    # CONSULTAR INVENTARIO
    @staticmethod
    def consultar_inventario(id_producto=None, id_cultivo=None):

        if id_producto is not None and (
            not isinstance(id_producto, int) or id_producto <= 0
        ):
            raise ValueError("El producto seleccionado no es válido.")

        if id_cultivo is not None and (
            not isinstance(id_cultivo, int) or id_cultivo <= 0
        ):
            raise ValueError("El cultivo seleccionado no es válido.")

        return InventarioDatos.consultar_inventario(id_producto, id_cultivo)

    # CONSULTAR MOVIMIENTOS
    @staticmethod
    def consultar_movimientos(id_inventario=None, fecha_inicio=None, fecha_fin=None):

        if id_inventario is not None and (
            not isinstance(id_inventario, int) or id_inventario <= 0
        ):
            raise ValueError("El inventario seleccionado no es válido.")

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise ValueError("La fecha inicial no puede ser posterior a la fecha final.")

        return InventarioDatos.consultar_movimientos(
            id_inventario, fecha_inicio, fecha_fin
        )
