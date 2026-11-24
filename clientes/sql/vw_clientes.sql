USE BDWilliamsAgribusiness;
GO

-- Vista 1: clientes activos con su segmento y su contacto principal
CREATE OR ALTER VIEW vw_ClientesActivos
AS
SELECT
    c.CodigoCliente,
    c.RazonSocial,
    c.NombreComercial,
    s.NombreSegmento AS Segmento,
    c.Provincia,
    c.Moneda,
    c.LimiteCredito,
    c.DiasCredito,
    ct.Nombre + ' ' + ct.Apellidos AS ContactoPrincipal,
    ct.Correo AS CorreoContacto
FROM Cliente c
INNER JOIN SegmentoCliente s ON s.IdSegmento = c.IdSegmento
LEFT JOIN ContactoCliente ct ON ct.IdCliente = c.IdCliente
                            AND ct.EsContactoPrincipal = 1
                            AND ct.Activo = 1
WHERE c.EstadoCliente = 'Activo';
GO

-- Vista 2: contratos vigentes con cliente y días restantes
CREATE OR ALTER VIEW vw_ContratosVigentes
AS
SELECT
    k.NumeroContrato,
    c.CodigoCliente,
    c.RazonSocial,
    k.TipoContrato,
    k.FechaInicio,
    k.FechaFin,
    DATEDIFF(DAY, CAST(GETDATE() AS DATE), k.FechaFin) AS DiasRestantes,
    k.FrecuenciaEntrega,
    k.Moneda,
    k.MontoEstimado
FROM Contrato k
INNER JOIN Cliente c ON c.IdCliente = k.IdCliente
WHERE k.EstadoContrato = 'Vigente';
GO

-- Vista 3: resumen de contratos por cliente y moneda
CREATE OR ALTER VIEW vw_ResumenContratosPorCliente
AS
SELECT
    c.CodigoCliente,
    c.RazonSocial,
    k.Moneda,
    COUNT(*) AS TotalContratos,
    SUM(CASE WHEN k.EstadoContrato = 'Vigente' THEN 1 ELSE 0 END) AS ContratosVigentes,
    SUM(k.MontoEstimado) AS MontoTotalEstimado
FROM Cliente c
INNER JOIN Contrato k ON k.IdCliente = c.IdCliente
GROUP BY c.CodigoCliente, c.RazonSocial, k.Moneda;
GO

select * from vw_ClientesActivos;
select * from vw_ContratosVigentes;
select * from vw_ResumenContratosPorCliente