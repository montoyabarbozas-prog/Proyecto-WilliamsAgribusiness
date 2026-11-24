USE BDWilliamsAgribusiness;
GO

-- =====================================================
-- CONSULTAS DE CLIENTES
-- =====================================================

BEGIN TRANSACTION;

-- ----------------------- 3 UPDATE -----------------------

-- UPDATE 1: subir el límite de crédito de un cliente
UPDATE Cliente
SET LimiteCredito = 9000000.00,
    FechaModificacion = GETDATE()
WHERE CodigoCliente = 'CLI-0003';

-- UPDATE 2: cambiar el medio preferido y el teléfono de un contacto
UPDATE ContactoCliente
SET MedioPreferido = 'WhatsApp',
    Telefono = '2288-9999'
WHERE Correo = 'dalfaro@gourmetfresh-ejemplo.com';

-- UPDATE 3: renovar un contrato vencido
UPDATE Contrato
SET FechaFin = '2027-09-30',
    EstadoContrato = 'Vigente',
    Observaciones = 'Contrato renovado'
WHERE NumeroContrato = 'CT-2026-005'
  AND EstadoContrato = 'Vencido';

SELECT CodigoCliente, LimiteCredito, FechaModificacion
FROM Cliente WHERE CodigoCliente = 'CLI-0003';

SELECT Nombre, MedioPreferido, Telefono
FROM ContactoCliente WHERE Correo = 'dalfaro@gourmetfresh-ejemplo.com';

SELECT NumeroContrato, FechaFin, EstadoContrato
FROM Contrato WHERE NumeroContrato = 'CT-2026-005';

-- ----------------------- 2 DELETE -----------------------

-- DELETE 1: eliminar un contacto secundario
DELETE FROM ContactoCliente
WHERE Correo = 'msoto@gourmetfresh-ejemplo.com'
  AND EsContactoPrincipal = 0;

-- DELETE 2: eliminar un contrato en Borrador 
DELETE FROM DetalleContrato
WHERE IdContrato = (SELECT IdContrato FROM Contrato
                    WHERE NumeroContrato = 'CT-2026-007'
                      AND EstadoContrato = 'Borrador');

DELETE FROM Contrato
WHERE NumeroContrato = 'CT-2026-007'
  AND EstadoContrato = 'Borrador';

SELECT * FROM ContactoCliente WHERE Correo = 'msoto@gourmetfresh-ejemplo.com';
SELECT * FROM Contrato WHERE NumeroContrato = 'CT-2026-007';

ROLLBACK;

-- ----------------------- 3 SELECT -----------------------

-- SELECT 1: cantidad de clientes y crédito por segmento y moneda
SELECT s.NombreSegmento, c.Moneda,
       COUNT(*) AS TotalClientes,
       SUM(c.LimiteCredito) AS CreditoTotal
FROM Cliente c
INNER JOIN SegmentoCliente s ON s.IdSegmento = c.IdSegmento
GROUP BY s.NombreSegmento, c.Moneda
ORDER BY s.NombreSegmento;

-- SELECT 2: contratos de un cliente 
DECLARE @Codigo VARCHAR(20) = 'CLI-0003';
SELECT c.RazonSocial, k.NumeroContrato, k.TipoContrato,
       k.EstadoContrato, k.FechaInicio, k.FechaFin, k.MontoEstimado
FROM Cliente c
INNER JOIN Contrato k ON k.IdCliente = c.IdCliente
WHERE c.CodigoCliente = @Codigo;

-- SELECT 3: contratos vigentes que vencen en los próximos 90 días
SELECT c.RazonSocial, k.NumeroContrato, k.FechaFin,
       DATEDIFF(DAY, CAST(GETDATE() AS DATE), k.FechaFin) AS DiasRestantes
FROM Contrato k
INNER JOIN Cliente c ON c.IdCliente = k.IdCliente
WHERE k.EstadoContrato = 'Vigente'
  AND k.FechaFin BETWEEN CAST(GETDATE() AS DATE)
                     AND DATEADD(DAY, 90, CAST(GETDATE() AS DATE))
ORDER BY k.FechaFin;