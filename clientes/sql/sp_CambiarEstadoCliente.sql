USE BDWilliamsAgribusiness;
GO

CREATE OR ALTER PROCEDURE sp_CambiarEstadoCliente
    @CodigoCliente VARCHAR(20),
    @NuevoEstado VARCHAR(15)
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @IdCliente INT;
    DECLARE @EstadoActual VARCHAR(15);

    SELECT @IdCliente = IdCliente, @EstadoActual = EstadoCliente
    FROM Cliente
    WHERE CodigoCliente = @CodigoCliente;

    IF @IdCliente IS NULL
        THROW 50301, 'El cliente indicado no existe.', 1;

    IF @NuevoEstado NOT IN ('Prospecto', 'Piloto', 'Activo', 'Inactivo')
        THROW 50302, 'El estado debe ser Prospecto, Piloto, Activo o Inactivo.', 1;

    IF @EstadoActual = @NuevoEstado
    BEGIN
        SELECT 'El cliente ya tiene ese estado, no se hizo ningún cambio.' AS Mensaje;
        RETURN;
    END

    IF @NuevoEstado = 'Inactivo'
       AND EXISTS (SELECT 1 FROM Contrato
                   WHERE IdCliente = @IdCliente
                     AND EstadoContrato = 'Vigente')
        THROW 50303, 'No se puede inactivar un cliente con contratos vigentes.', 1;

    BEGIN TRY
        UPDATE Cliente
        SET EstadoCliente = @NuevoEstado,
            FechaModificacion = GETDATE()
        WHERE IdCliente = @IdCliente;

        SELECT 'Estado actualizado: ' + @EstadoActual + ' -> ' + @NuevoEstado AS Mensaje;
    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END
GO