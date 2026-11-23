USE BDWilliamsAgribusiness;
GO

CREATE OR ALTER PROCEDURE sp_CambiarEstadoCliente
    @CodigoCliente VARCHAR(20),
    @NuevoEstado VARCHAR(15)
AS
BEGIN
    DECLARE @IdCliente INT;
    DECLARE @EstadoActual VARCHAR(15);

    SELECT @IdCliente = IdCliente, @EstadoActual = EstadoCliente
    FROM Cliente
    WHERE CodigoCliente = @CodigoCliente;

    IF @IdCliente IS NULL
    BEGIN
        PRINT 'Error: el cliente indicado no existe.';
        RETURN;
    END

    IF @NuevoEstado NOT IN ('Prospecto', 'Piloto', 'Activo', 'Inactivo')
    BEGIN
        PRINT 'Error: el estado debe ser Prospecto, Piloto, Activo o Inactivo.';
        RETURN;
    END

    IF @EstadoActual = @NuevoEstado
    BEGIN
        PRINT 'El cliente ya tiene ese estado, no se hizo ningún cambio.';
        RETURN;
    END

    IF @NuevoEstado = 'Inactivo'
       AND EXISTS (SELECT 1 FROM Contrato
                   WHERE IdCliente = @IdCliente
                     AND EstadoContrato = 'Vigente')
    BEGIN
        PRINT 'Error: no se puede inactivar un cliente con contratos vigentes.';
        RETURN;
    END

    BEGIN TRY
        UPDATE Cliente
        SET EstadoCliente = @NuevoEstado,
            FechaModificacion = GETDATE()
        WHERE IdCliente = @IdCliente;

        PRINT 'Estado actualizado: ' + @EstadoActual + ' -> ' + @NuevoEstado;
    END TRY
    BEGIN CATCH
        PRINT 'Error al cambiar el estado: ' + ERROR_MESSAGE();
    END CATCH
END
GO