MODULES = {
    'Clientes': {
        'icon': '👥', 'description': 'Administración de clientes, segmentos y contactos.',
        'tables': {
            'SegmentoCliente': ['IdSegmento', 'NombreSegmento', 'Descripcion'],
            'Cliente': ['IdCliente', 'CodigoCliente', 'TipoIdentificacion', 'NumeroIdentificacion', 'RazonSocial', 'NombreComercial', 'IdSegmento', 'EstadoCliente', 'FechaRegistro', 'DireccionFiscal', 'Provincia', 'Canton', 'TelefonoPrincipal', 'CorreoFacturacion', 'Moneda', 'LimiteCredito', 'DiasCredito', 'RequiereTrazabilidad', 'RequisitosEspeciales', 'FechaModificacion', 'Observaciones'],
            'ContactoCliente': ['IdContacto', 'IdCliente', 'Nombre', 'Apellidos', 'Cargo', 'RolContacto', 'Telefono', 'WhatsApp', 'Correo', 'MedioPreferido', 'EsContactoPrincipal', 'Activo', 'FechaRegistro']
        }
    },
    'Contratos': {
        'icon': '📄', 'description': 'Gestión de contratos y productos pactados.',
        'tables': {
            'Contrato': ['IdContrato', 'NumeroContrato', 'IdCliente', 'TipoContrato', 'FechaInicio', 'FechaFin', 'EstadoContrato', 'FrecuenciaEntrega', 'Moneda', 'MontoEstimado', 'DiasCredito', 'PorcentajeAnticipo', 'DescuentoVolumen', 'ClausulaAjustePrecio', 'FechaCreacion', 'Observaciones'],
            'DetalleContrato': ['IdDetalleContrato', 'IdContrato', 'IdProducto', 'CantidadPactada', 'UnidadMedida', 'PrecioPactado', 'EspecificacionCalibre']
        }
    },
    'Producción': {
        'icon': '🌱', 'description': 'Control de fincas, lotes y ciclos de cultivo.',
        'tables': {
            'Finca': ['IdFinca', 'CodigoFinca', 'NombreFinca', 'Provincia', 'Canton', 'Distrito', 'Direccion', 'AreaTotalHectareas', 'TipoProduccion', 'Responsable', 'FechaRegistro', 'EstadoFinca', 'Observaciones'],
            'Lote': ['IdLote', 'CodigoLote', 'IdFinca', 'NombreLote', 'AreaHectareas', 'TipoSuelo', 'SistemaRiego', 'TipoAmbiente', 'EstadoLote', 'FechaRegistro', 'Observaciones'],
            'Cultivo': ['IdCultivo', 'CodigoCultivo', 'IdLote', 'NombreCultivo', 'Variedad', 'FechaSiembra', 'FechaCosechaEstimada', 'FechaCosechaReal', 'CantidadSembrada', 'ProduccionEstimadaKg', 'ProduccionRealKg', 'CostoProduccion', 'EstadoCultivo', 'MetodoCultivo', 'Observaciones']
        }
    },
    'Inventario': {
        'icon': '📦', 'description': 'Productos, existencias por cultivo y movimientos.',
        'tables': {
            'Producto': ['IdProducto', 'CodigoProducto', 'NombreProducto', 'Categoria', 'Descripcion', 'UnidadMedida', 'PrecioVentaBase', 'EstadoProducto', 'FechaRegistro', 'Observaciones'],
            'Inventario': ['IdInventario', 'IdProducto', 'IdCultivo', 'CantidadDisponible', 'StockMinimo', 'Ubicacion', 'FechaActualizacion'],
            'MovimientoInventario': ['IdMovimiento', 'IdInventario', 'TipoMovimiento', 'Cantidad', 'FechaMovimiento', 'Motivo', 'ReferenciaDocumento', 'Observaciones']
        }
    },
    'Ventas y entregas': {
        'icon': '🚚', 'description': 'Registro de ventas, líneas de venta y entregas.',
        'tables': {
            'Venta': ['IdVenta', 'NumeroVenta', 'IdCliente', 'IdContrato', 'FechaVenta', 'TipoVenta', 'EstadoVenta', 'Moneda', 'Subtotal', 'MontoDescuento', 'MontoImpuesto', 'TotalVenta', 'DiasCredito', 'FechaVencimientoPago', 'FechaCreacion', 'Observaciones'],
            'DetalleVenta': ['IdDetalleVenta', 'IdVenta', 'IdProducto', 'LoteProduccion', 'Cantidad', 'UnidadMedida', 'PrecioUnitario', 'PorcentajeDescuento', 'SubtotalLinea', 'EspecificacionCalibre'],
            'Entrega': ['IdEntrega', 'CodigoEntrega', 'IdVenta', 'FechaProgramada', 'FechaEntregaReal', 'EstadoEntrega', 'DireccionEntrega', 'VentanaRecibo', 'NombreRecibe', 'PlacaVehiculo', 'NombreChofer', 'TemperaturaDespacho', 'CajasRetornablesEntregadas', 'FechaCreacion', 'Observaciones']
        }
    }
}
