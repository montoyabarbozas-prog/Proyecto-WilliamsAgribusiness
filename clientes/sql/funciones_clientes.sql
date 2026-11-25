USE BDWilliamsAgribusiness;
GO

-- Función 1: días que le quedan a un contrato
CREATE OR ALTER FUNCTION dbo.fn_DiasRestantesContrato (@NumeroContrato VARCHAR(20))
RETURNS INT
AS
BEGIN
    DECLARE @Dias INT;

    SELECT @Dias = DATEDIFF(DAY, CAST(GETDATE() AS DATE), FechaFin)
    FROM Contrato
    WHERE NumeroContrato = @NumeroContrato;

    RETURN @Dias;   -- NULL si el contrato no existe
END
GO

-- Función 2: nombre del contacto principal activo de un cliente
CREATE OR ALTER FUNCTION dbo.fn_ContactoPrincipal (@IdCliente INT)
RETURNS VARCHAR(200)
AS
BEGIN
    DECLARE @Nombre VARCHAR(200);

    SELECT TOP 1 @Nombre = Nombre + ' ' + Apellidos
    FROM ContactoCliente
    WHERE IdCliente = @IdCliente
      AND EsContactoPrincipal = 1
      AND Activo = 1;

    RETURN @Nombre;   -- NULL si no tiene contacto principal activo
END
GO

-- Función 3: monto total de contratos vigentes de un cliente en una moneda
CREATE OR ALTER FUNCTION dbo.fn_MontoVigentePorCliente
    (@CodigoCliente VARCHAR(20), @Moneda CHAR(3))
RETURNS DECIMAL(14,2)
AS
BEGIN
    DECLARE @Total DECIMAL(14,2);

    SELECT @Total = ISNULL(SUM(k.MontoEstimado), 0)
    FROM Contrato k
    INNER JOIN Cliente c ON c.IdCliente = k.IdCliente
    WHERE c.CodigoCliente = @CodigoCliente
      AND k.Moneda = @Moneda
      AND k.EstadoContrato = 'Vigente';

    RETURN @Total;
END
GO

SELECT dbo.fn_DiasRestantesContrato('CT-2026-004') AS DiasRestantes;
SELECT dbo.fn_DiasRestantesContrato('CT-2026-005') AS DiasRestantes;
SELECT dbo.fn_DiasRestantesContrato('NO-EXISTE')   AS DiasRestantes;

SELECT CodigoCliente, RazonSocial,
       dbo.fn_ContactoPrincipal(IdCliente) AS ContactoPrincipal
FROM Cliente;

SELECT dbo.fn_MontoVigentePorCliente('CLI-0003', 'CRC') AS MontoCRC;
SELECT dbo.fn_MontoVigentePorCliente('CLI-0005', 'USD') AS MontoUSD;
SELECT dbo.fn_MontoVigentePorCliente('CLI-0005', 'CRC') AS MontoCRC;