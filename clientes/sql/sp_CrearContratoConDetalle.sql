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
    BEGIN
        PRINT 'Error: el cliente indicado no existe.';
        RETURN;
    END

    IF @EstadoCliente NOT IN ('Activo', 'Piloto')
    BEGIN
        PRINT 'Error: solo se pueden crear contratos a clientes Activos o Piloto.';
        RETURN;
    END

    IF EXISTS (SELECT 1 FROM Contrato WHERE NumeroContrato = @NumeroContrato)
    BEGIN
        PRINT 'Error: ya existe un contrato con ese número.';
        RETURN;
    END

    IF @TipoContrato NOT IN ('Piloto', 'Abastecimiento programado', 'Por volumen')
    BEGIN
        PRINT 'Error: el tipo de contrato no es válido.';
        RETURN;
    END

    IF @FechaFin <= @FechaInicio
    BEGIN
        PRINT 'Error: la fecha de fin debe ser posterior a la de inicio.';
        RETURN;
    END

    IF @MontoEstimado <= 0
    BEGIN
        PRINT 'Error: el monto estimado debe ser mayor a cero.';
        RETURN;
    END

    IF @PorcentajeAnticipo NOT BETWEEN 0 AND 100
       OR @DescuentoVolumen NOT BETWEEN 0 AND 100
    BEGIN
        PRINT 'Error: los porcentajes deben estar entre 0 y 100.';
        RETURN;
    END

    IF NOT EXISTS (SELECT 1 FROM Producto WHERE IdProducto = @IdProducto)
    BEGIN
        PRINT 'Error: el producto indicado no existe.';
        RETURN;
    END

    IF @CantidadPactada <= 0 OR @PrecioPactado <= 0
    BEGIN
        PRINT 'Error: la cantidad y el precio deben ser mayores a cero.';
        RETURN;
    END

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
        PRINT 'Contrato ' + @NumeroContrato + ' creado en estado Borrador.';
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        PRINT 'Error al crear el contrato: ' + ERROR_MESSAGE();
    END CATCH
END
GO