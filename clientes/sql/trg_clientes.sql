use BDWilliamsAgribusiness
go

-- TRIGGER 1: actualiza solo la fecha de modificación del cliente
CREATE TRIGGER trg_Cliente_FechaModificacion
ON Cliente
AFTER UPDATE
AS
BEGIN
    UPDATE c
    SET FechaModificacion = GETDATE()
    FROM Cliente c
    INNER JOIN inserted i ON i.IdCliente = c.IdCliente;
END
GO

-- TRIGGER 2: un solo contacto principal activo por cliente
CREATE OR ALTER TRIGGER trg_ContactoCliente_UnicoPrincipal
ON ContactoCliente
AFTER INSERT, UPDATE
AS
BEGIN
    IF EXISTS (
        SELECT 1
        FROM ContactoCliente cc
        WHERE cc.IdCliente IN (SELECT IdCliente FROM inserted)
          AND cc.EsContactoPrincipal = 1
          AND cc.Activo = 1
        GROUP BY cc.IdCliente
        HAVING COUNT(*) > 1
    )
    BEGIN
        ROLLBACK TRANSACTION;
        THROW 50010, 'Un cliente solo puede tener un contacto principal activo.', 1;
    END
END
GO