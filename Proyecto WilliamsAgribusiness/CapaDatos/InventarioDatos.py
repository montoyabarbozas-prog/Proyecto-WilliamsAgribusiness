from CapaDatos.Conexion import obtener_conexion


class InventarioDatos:

    ## Métodos para ejecutar procedimientos almacenados sin obtener resultados
    @staticmethod
    def ejecutar_procedimiento(sql, parametros=()):
        conexion = None

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)

            conexion.commit()
            return True

        except Exception:
            if conexion:
                conexion.rollback()
            raise

        finally:
            if conexion:
                conexion.close()



    # Metódos para consultar procedimientos almacenados y obtener resultados
    @staticmethod
    def consultar_procedimiento(sql, parametros=()):
        conexion = None

        try:
            conexion = obtener_conexion()
            cursor = conexion.cursor()
            cursor.execute(sql, parametros)

            columnas = [columna[0] for columna in cursor.description]
            resultados = []

            for fila in cursor.fetchall():
                resultados.append(
                    dict(zip(columnas, fila))
                )

            return resultados

        finally:
            if conexion:
                conexion.close()

    # Registrar entrada de inventario
    @staticmethod
    def registrar_entrada(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        sql = """
            EXEC dbo.sp_RegistrarEntradaInventario
                @IdInventario = ?,
                @Cantidad = ?,
                @Motivo = ?,
                @ReferenciaDocumento = ?,
                @Observaciones = ?
        """

        return InventarioDatos.ejecutar_procedimiento(sql,(id_inventario, cantidad, motivo, referencia, observaciones))

    # Registrar salida de inventario
    @staticmethod
    def registrar_salida(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        sql = """
            EXEC dbo.sp_RegistrarSalidaInventario
                @IdInventario = ?,
                @Cantidad = ?,
                @Motivo = ?,
                @ReferenciaDocumento = ?,
                @Observaciones = ?
        """

        return InventarioDatos.ejecutar_procedimiento(sql,(id_inventario, cantidad, motivo, referencia, observaciones))

    # Registrar ajuste de inventario
    @staticmethod
    def registrar_ajuste(id_inventario, cantidad, motivo, referencia=None, observaciones=None):

        sql = """
            EXEC dbo.sp_RegistrarAjusteInventario
                @IdInventario = ?,
                @Cantidad = ?,
                @Motivo = ?,
                @ReferenciaDocumento = ?,
                @Observaciones = ?
        """

        return InventarioDatos.ejecutar_procedimiento(
            sql,(id_inventario, cantidad, motivo, referencia, observaciones))

    # Consulta inventario
    @staticmethod
    def consultar_inventario(id_producto=None, id_cultivo=None):

        sql = """
            EXEC dbo.sp_ConsultarInventario
                @IdProducto = ?,
                @IdCultivo = ?
        """

        return InventarioDatos.consultar_procedimiento(sql, (id_producto, id_cultivo))

    # Consultar movimientos de inventario
    @staticmethod
    def consultar_movimientos(id_inventario=None, fecha_inicio=None, fecha_fin=None):
        sql = """
            EXEC dbo.sp_ConsultarMovimientosInventario
                @IdInventario = ?,
                @FechaInicio = ?,
                @FechaFin = ?
        """
        return InventarioDatos.consultar_procedimiento(sql,(id_inventario, fecha_inicio, fecha_fin))