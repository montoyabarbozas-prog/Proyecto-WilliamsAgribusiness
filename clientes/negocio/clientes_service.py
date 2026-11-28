import re
from datetime import date

from produccion_service import consultar, ejecutar_sp

# ==============================================================================
# CONSTANTES
# ==============================================================================
ESTADOS_CLIENTE = ("Prospecto", "Piloto", "Activo", "Inactivo")
TIPOS_CONTRATO = ("Piloto", "Abastecimiento programado", "Por volumen")
MONEDAS = ("CRC", "USD")

# Lista blanca de vistas.
VISTAS_CLIENTES = {
    "vw_ClientesActivos",
    "vw_ContratosVigentes",
    "vw_ResumenContratosPorCliente",
}


# ==============================================================================
# 1. CONSULTAS (solo lectura)
# ==============================================================================
def cargar_vista_clientes(nombre_vista):
    """Lee una de las 3 vistas del módulo de clientes."""
    if nombre_vista not in VISTAS_CLIENTES:
        raise ValueError(f"Vista no permitida: {nombre_vista}")
    return consultar(f"SELECT * FROM dbo.{nombre_vista}")


def consultar_clientes():
    """Todos los clientes (para listas y combos)."""
    return consultar(
        "SELECT CodigoCliente, RazonSocial, EstadoCliente "
        "FROM dbo.Cliente ORDER BY CodigoCliente"
    )


def consultar_segmentos():
    """Nombres de los segmentos (para el combo del formulario)."""
    return consultar(
        "SELECT NombreSegmento FROM dbo.SegmentoCliente ORDER BY NombreSegmento"
    )


def consultar_productos():
    """Productos disponibles (para el combo al crear un contrato)."""
    return consultar(
        "SELECT IdProducto, CodigoProducto, NombreProducto, UnidadMedida "
        "FROM dbo.Producto ORDER BY NombreProducto"
    )


def consultar_contratos_cliente(codigo_cliente):
    """Contratos de un cliente."""
    return consultar(
        "SELECT k.NumeroContrato, k.TipoContrato, k.EstadoContrato, "
        "       k.FechaInicio, k.FechaFin, k.Moneda, k.MontoEstimado "
        "FROM dbo.Contrato k "
        "INNER JOIN dbo.Cliente c ON c.IdCliente = k.IdCliente "
        "WHERE c.CodigoCliente = ? ORDER BY k.FechaInicio DESC",
        (codigo_cliente,),
    )


def siguiente_codigo_cliente():
    """Sugiere el próximo código de cliente con el formato de la base: CLI-0009."""
    codigos = consultar("SELECT CodigoCliente FROM dbo.Cliente")["CodigoCliente"]
    numeros = [
        int(m.group(1))
        for c in codigos
        if (m := re.fullmatch(r"CLI-(\d+)", str(c)))
    ]
    return f"CLI-{(max(numeros) + 1 if numeros else 1):04d}"


# ==============================================================================
# 2. VALIDACIONES 
# ==============================================================================
def _vacio(valor):
    return valor is None or not str(valor).strip()


def _correo_valido(correo):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(correo).strip()))


def validar_cambio_estado(codigo, nuevo_estado):
    errores = []
    if _vacio(codigo):
        errores.append("Debes seleccionar un cliente.")
    if nuevo_estado not in ESTADOS_CLIENTE:
        errores.append("Debes seleccionar un estado válido.")
    return errores


def validar_cliente(codigo, tipo_id, numero_id, razon_social, segmento, direccion,
                    provincia, canton, correo_facturacion, moneda, limite_credito,
                    dias_credito, nombre_contacto, apellidos_contacto, rol_contacto,
                    correo_contacto):
    errores = []
    if _vacio(codigo) or not re.fullmatch(r"[A-Za-z0-9_-]{1,20}", str(codigo).strip()):
        errores.append("El código del cliente es obligatorio (letras, números, guion; máx. 20).")
    for etiqueta, valor in {
        "El tipo de identificación": tipo_id,
        "El número de identificación": numero_id,
        "La razón social": razon_social,
        "El segmento": segmento,
        "La dirección fiscal": direccion,
        "La provincia": provincia,
        "El cantón": canton,
        "El nombre del contacto": nombre_contacto,
        "Los apellidos del contacto": apellidos_contacto,
        "El rol del contacto": rol_contacto,
    }.items():
        if _vacio(valor):
            errores.append(f"{etiqueta} es obligatorio.")
    if _vacio(correo_facturacion) or not _correo_valido(correo_facturacion):
        errores.append("El correo de facturación no es válido.")
    if _vacio(correo_contacto) or not _correo_valido(correo_contacto):
        errores.append("El correo del contacto no es válido.")
    if moneda not in MONEDAS:
        errores.append("La moneda debe ser CRC o USD.")
    if limite_credito is None or limite_credito < 0:
        errores.append("El límite de crédito no puede ser negativo.")
    if dias_credito is None or dias_credito < 0:
        errores.append("Los días de crédito no pueden ser negativos.")
    return errores


def validar_contrato(numero_contrato, codigo_cliente, tipo_contrato, f_inicio, f_fin,
                     frecuencia, monto, anticipo, descuento, id_producto, cantidad,
                     unidad, precio):
    errores = []
    if _vacio(numero_contrato):
        errores.append("El número de contrato es obligatorio.")
    if _vacio(codigo_cliente):
        errores.append("Debes seleccionar un cliente.")
    if tipo_contrato not in TIPOS_CONTRATO:
        errores.append("Debes seleccionar un tipo de contrato válido.")
    if f_fin <= f_inicio:
        errores.append("La fecha de fin debe ser posterior a la de inicio.")
    if _vacio(frecuencia):
        errores.append("La frecuencia de entrega es obligatoria.")
    if monto is None or monto <= 0:
        errores.append("El monto estimado debe ser mayor que 0.")
    if anticipo is None or not 0 <= anticipo <= 100:
        errores.append("El anticipo debe estar entre 0 y 100.")
    if descuento is None or not 0 <= descuento <= 100:
        errores.append("El descuento debe estar entre 0 y 100.")
    if id_producto is None:
        errores.append("Debes seleccionar un producto.")
    if cantidad is None or cantidad <= 0:
        errores.append("La cantidad pactada debe ser mayor que 0.")
    if _vacio(unidad):
        errores.append("La unidad de medida es obligatoria.")
    if precio is None or precio <= 0:
        errores.append("El precio pactado debe ser mayor que 0.")
    return errores


# ==============================================================================
# 3. PROCEDIMIENTOS ALMACENADOS
# ==============================================================================
def mensaje_de(resultado):
    """Saca el texto de la columna 'Mensaje' que devuelven los procedimientos."""
    if resultado is not None and not resultado.empty and "Mensaje" in resultado.columns:
        return str(resultado.iloc[0]["Mensaje"])
    return "Operación realizada."


def cambiar_estado_cliente(codigo, nuevo_estado):
    """Devuelve (True, mensaje) o (False, mensaje de error)."""
    errores = validar_cambio_estado(codigo, nuevo_estado)
    if errores:
        return False, " ".join(errores)
    ok, res = ejecutar_sp(
        "EXEC dbo.sp_CambiarEstadoCliente @CodigoCliente = ?, @NuevoEstado = ?",
        (codigo, nuevo_estado),
    )
    return (True, mensaje_de(res)) if ok else (False, res)


def registrar_cliente(codigo, tipo_id, numero_id, razon_social, segmento, direccion,
                      provincia, canton, correo_facturacion, moneda, limite_credito,
                      dias_credito, requiere_trazabilidad, nombre_contacto,
                      apellidos_contacto, rol_contacto, correo_contacto):
    """Registra el cliente y su contacto principal. Devuelve (True, mensaje) o (False, error)."""
    errores = validar_cliente(codigo, tipo_id, numero_id, razon_social, segmento,
                              direccion, provincia, canton, correo_facturacion, moneda,
                              limite_credito, dias_credito, nombre_contacto,
                              apellidos_contacto, rol_contacto, correo_contacto)
    if errores:
        return False, " ".join(errores)
    ok, res = ejecutar_sp(
        "EXEC dbo.sp_RegistrarClienteConContacto "
        "@CodigoCliente = ?, @TipoIdentificacion = ?, @NumeroIdentificacion = ?, "
        "@RazonSocial = ?, @NombreSegmento = ?, @DireccionFiscal = ?, "
        "@Provincia = ?, @Canton = ?, @CorreoFacturacion = ?, @Moneda = ?, "
        "@LimiteCredito = ?, @DiasCredito = ?, @RequiereTrazabilidad = ?, "
        "@NombreContacto = ?, @ApellidosContacto = ?, @RolContacto = ?, "
        "@CorreoContacto = ?",
        (str(codigo).strip(), tipo_id, numero_id, razon_social, segmento, direccion,
         provincia, canton, correo_facturacion, moneda, limite_credito, dias_credito,
         1 if requiere_trazabilidad else 0, nombre_contacto, apellidos_contacto,
         rol_contacto, correo_contacto),
    )
    return (True, mensaje_de(res)) if ok else (False, res)


def crear_contrato(numero_contrato, codigo_cliente, tipo_contrato, f_inicio, f_fin,
                   frecuencia, monto, anticipo, descuento, id_producto, cantidad,
                   unidad, precio, especificacion_calibre=None,
                   clausula_ajuste=None, observaciones=None):
    """Crea el contrato (en Borrador) con su detalle. Devuelve (True, mensaje) o (False, error)."""
    errores = validar_contrato(numero_contrato, codigo_cliente, tipo_contrato, f_inicio,
                               f_fin, frecuencia, monto, anticipo, descuento,
                               id_producto, cantidad, unidad, precio)
    if errores:
        return False, " ".join(errores)
    ok, res = ejecutar_sp(
        "EXEC dbo.sp_CrearContratoConDetalle "
        "@NumeroContrato = ?, @CodigoCliente = ?, @TipoContrato = ?, "
        "@FechaInicio = ?, @FechaFin = ?, @FrecuenciaEntrega = ?, "
        "@MontoEstimado = ?, @PorcentajeAnticipo = ?, @DescuentoVolumen = ?, "
        "@IdProducto = ?, @CantidadPactada = ?, @UnidadMedida = ?, "
        "@PrecioPactado = ?, @EspecificacionCalibre = ?, "
        "@ClausulaAjustePrecio = ?, @Observaciones = ?",
        (str(numero_contrato).strip(), codigo_cliente, tipo_contrato, f_inicio, f_fin,
         frecuencia, monto, anticipo, descuento, int(id_producto), cantidad, unidad,
         precio, especificacion_calibre, clausula_ajuste, observaciones),
    )
    return (True, mensaje_de(res)) if ok else (False, res)