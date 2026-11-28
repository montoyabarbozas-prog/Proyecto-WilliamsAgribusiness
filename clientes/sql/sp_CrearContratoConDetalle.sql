USE BDWilliamsAgribusiness;
GO

CREATE OR ALTER PROCEDURE sp_CrearContratoConDetalle
    @NumeroContrato VARCHAR(20),
    @CodigoCliente VARCHAR(20),
    @TipoContrato VARCHAR(25),
    @FechaInicio DATE,
    @FechaFin DATE,
    @FrecuenciaEntrega VARCHAR(15),
    @MontoEstimado DECIMAL(14,2),
    @PorcentajeAnticipo DECIMAL(5,2),
    @DescuentoVolumen DECIMAL(5,2),
    @IdProducto INT,
    @CantidadPactada DECIMAL(10,2),
    @UnidadMedida VARCHAR(20),
    @PrecioPactado DECIMAL(12,2),
    @EspecificacionCalibre VARCHAR(100) = NULL,
    @ClausulaAjustePrecio VARCHAR(500) = NULL,
    @Observaciones VARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @IdCliente INT;
    DECLARE @EstadoCliente VARCHAR(15);
    DECLARE @Moneda CHAR(3);
    DECLARE @DiasCredito INT;
    DECLARE @IdContrato INT;

    SELECT @IdCliente = IdCliente,
           @EstadoCliente = EstadoCliente,
           @Moneda = Moneda,
           @DiasCredito = DiasCredito
    FROM Cliente
    WHERE CodigoCliente = @CodigoCliente;

    IF @IdCliente IS NULL
        THROW 50401, 'El cliente indicado no existe.', 1;

    IF @EstadoCliente NOT IN ('Activo', 'Piloto')
        THROW 50402, 'Solo se pueden crear contratos a clientes Activos o Piloto.', 1;

    IF EXISTS (SELECT 1 FROM Contrato WHERE NumeroContrato = @NumeroContrato)
        THROW 50403, 'Ya existe un contrato con ese número.', 1;

    IF @TipoContrato NOT IN ('Piloto', 'Abastecimiento programado', 'Por volumen')
        THROW 50404, 'El tipo de contrato no es válido.', 1;

    IF @FechaFin <= @FechaInicio
        THROW 50405, 'La fecha de fin debe ser posterior a la de inicio.', 1;

    IF @MontoEstimado <= 0
        THROW 50406, 'El monto estimado debe ser mayor a cero.', 1;

    IF @PorcentajeAnticipo NOT BETWEEN 0 AND 100
       OR @DescuentoVolumen NOT BETWEEN 0 AND 100
        THROW 50407, 'Los porcentajes deben estar entre 0 y 100.', 1;

    IF NOT EXISTS (SELECT 1 FROM Producto WHERE IdProducto = @IdProducto)
        THROW 50408, 'El producto indicado no existe.', 1;

    IF @CantidadPactada <= 0 OR @PrecioPactado <= 0
        THROW 50409, 'La cantidad y el precio deben ser mayores a cero.', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT INTO Contrato
        (NumeroContrato, IdCliente, TipoContrato, FechaInicio, FechaFin,
         EstadoContrato, FrecuenciaEntrega, Moneda, MontoEstimado,
         DiasCredito, PorcentajeAnticipo, DescuentoVolumen,
         ClausulaAjustePrecio, FechaCreacion, Observaciones)
        VALUES
        (@NumeroContrato, @IdCliente, @TipoContrato, @FechaInicio, @FechaFin,
         'Borrador', @FrecuenciaEntrega, @Moneda, @MontoEstimado,
         @DiasCredito, @PorcentajeAnticipo, @DescuentoVolumen,
         @ClausulaAjustePrecio, GETDATE(), @Observaciones);

        SET @IdContrato = SCOPE_IDENTITY();

        INSERT INTO DetalleContrato
        (IdContrato, IdProducto, CantidadPactada, UnidadMedida,
         PrecioPactado, EspecificacionCalibre)
        VALUES
        (@IdContrato, @IdProducto, @CantidadPactada, @UnidadMedida,
         @PrecioPactado, @EspecificacionCalibre);

        COMMIT TRANSACTION;

        SELECT 'Contrato ' + @NumeroContrato + ' creado en estado Borrador.' AS Mensaje;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO