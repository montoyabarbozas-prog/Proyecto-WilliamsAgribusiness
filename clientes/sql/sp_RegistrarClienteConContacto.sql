USE BDWilliamsAgribusiness;
GO

CREATE OR ALTER PROCEDURE sp_RegistrarClienteConContacto
    @CodigoCliente VARCHAR(20),
    @TipoIdentificacion VARCHAR(20),
    @NumeroIdentificacion VARCHAR(20),
    @RazonSocial VARCHAR(150),
    @NombreSegmento VARCHAR(50),
    @DireccionFiscal VARCHAR(250),
    @Provincia VARCHAR(50),
    @Canton VARCHAR(50),
    @CorreoFacturacion VARCHAR(100),
    @Moneda CHAR(3),
    @LimiteCredito DECIMAL(12,2),
    @DiasCredito INT,
    @RequiereTrazabilidad BIT,
    @NombreContacto VARCHAR(80),
    @ApellidosContacto VARCHAR(100),
    @RolContacto VARCHAR(30),
    @CorreoContacto VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @IdSegmento INT;
    DECLARE @IdCliente INT;

    IF EXISTS (SELECT 1 FROM Cliente
               WHERE NumeroIdentificacion = @NumeroIdentificacion)
        THROW 50201, 'Ya existe un cliente con esa identificación.', 1;

    IF EXISTS (SELECT 1 FROM Cliente WHERE CodigoCliente = @CodigoCliente)
        THROW 50202, 'Ya existe un cliente con ese código.', 1;

    SELECT @IdSegmento = IdSegmento
    FROM SegmentoCliente
    WHERE NombreSegmento = @NombreSegmento;

    IF @IdSegmento IS NULL
        THROW 50203, 'El segmento indicado no existe.', 1;

    IF @LimiteCredito < 0 OR @DiasCredito < 0
        THROW 50204, 'El crédito y los días de crédito no pueden ser negativos.', 1;

    IF @CorreoFacturacion NOT LIKE '%_@_%._%'
        THROW 50205, 'El correo de facturación no es válido.', 1;

    BEGIN TRY
        BEGIN TRANSACTION;

        INSERT INTO Cliente
        (CodigoCliente, TipoIdentificacion, NumeroIdentificacion,
         RazonSocial, IdSegmento, EstadoCliente, FechaRegistro,
         DireccionFiscal, Provincia, Canton, CorreoFacturacion,
         Moneda, LimiteCredito, DiasCredito, RequiereTrazabilidad)
        VALUES
        (@CodigoCliente, @TipoIdentificacion, @NumeroIdentificacion,
         @RazonSocial, @IdSegmento, 'Activo', CAST(GETDATE() AS DATE),
         @DireccionFiscal, @Provincia, @Canton, @CorreoFacturacion,
         @Moneda, @LimiteCredito, @DiasCredito, @RequiereTrazabilidad);

        SET @IdCliente = SCOPE_IDENTITY();

        INSERT INTO ContactoCliente
        (IdCliente, Nombre, Apellidos, RolContacto, Correo,
         EsContactoPrincipal, Activo, FechaRegistro)
        VALUES
        (@IdCliente, @NombreContacto, @ApellidosContacto, @RolContacto,
         @CorreoContacto, 1, 1, CAST(GETDATE() AS DATE));

        COMMIT TRANSACTION;

        SELECT 'Cliente registrado correctamente.' AS Mensaje;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END
GO