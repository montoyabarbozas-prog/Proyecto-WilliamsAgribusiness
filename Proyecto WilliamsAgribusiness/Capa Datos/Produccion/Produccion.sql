/* ============================================================================
   WILLIAM'S AGRIBUSINESS - MODULO DE PRODUCCION (VERSION SIMPLIFICADA)
   SQL Server | BDWilliamsAgribusiness


   ORDEN: Tablas -> controles -> funciones -> triggers -> SP -> vistas -> consultas
   ============================================================================ */

USE [William’s Agribusiness];
GO
SET ANSI_NULLS ON;
SET QUOTED_IDENTIFIER ON;
SET ANSI_PADDING ON;
SET ANSI_WARNINGS ON;
SET ARITHABORT ON;
SET CONCAT_NULL_YIELDS_NULL ON;
SET NUMERIC_ROUNDABORT OFF;
GO

-----------------------------Tablas---------------------------------

-- Tabla 1: Finca (una finca tiene muchos lotes)
IF OBJECT_ID('dbo.Finca', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Finca (
        IdFinca INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        CodigoFinca VARCHAR(20) NOT NULL UNIQUE,
        NombreFinca VARCHAR(100) NOT NULL,
        Provincia VARCHAR(50) NOT NULL,
        Canton VARCHAR(50) NOT NULL,
        Distrito VARCHAR(50) NOT NULL,
        Direccion VARCHAR(250) NOT NULL,
        AreaTotalHectareas DECIMAL(10,2) NOT NULL,  -- Area total; la suma de las areas de sus lotes no puede superarla
        TipoProduccion VARCHAR(30) NOT NULL,
        Responsable VARCHAR(100) NOT NULL,
        FechaRegistro DATE NOT NULL,
        EstadoFinca VARCHAR(20) NOT NULL,  -- 'Activa', 'Inactiva'
        Observaciones VARCHAR(500) NULL,
        CONSTRAINT CK_Finca_Area CHECK (AreaTotalHectareas > 0)
    );
END;
GO
-- Tabla 2: Lote (cada lote pertenece a una finca y tiene muchos cultivos)
IF OBJECT_ID('dbo.Lote', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Lote (
        IdLote INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        CodigoLote VARCHAR(20) NOT NULL UNIQUE,
        IdFinca INT NOT NULL,
        NombreLote VARCHAR(100) NOT NULL,
        AreaHectareas DECIMAL(10,2) NOT NULL,  -- Area del lote; la valida el trigger contra el area de la finca
        TipoSuelo VARCHAR(50) NULL,
        SistemaRiego VARCHAR(50) NULL,
        TipoAmbiente VARCHAR(30) NOT NULL,
        EstadoLote VARCHAR(20) NOT NULL,  -- 'Disponible', 'Ocupado', 'Descanso', 'Inactivo'
        FechaRegistro DATE NOT NULL,
        Observaciones VARCHAR(500) NULL,
        CONSTRAINT FK_Lote_Finca FOREIGN KEY (IdFinca) REFERENCES dbo.Finca(IdFinca),
        CONSTRAINT CK_Lote_Area CHECK (AreaHectareas > 0)
    );
END;
GO
-- Tabla 3: Cultivo (cada cultivo se siembra en un lote)
IF OBJECT_ID('dbo.Cultivo', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.Cultivo (
        IdCultivo INT IDENTITY(1,1) NOT NULL PRIMARY KEY,
        CodigoCultivo VARCHAR(20) NOT NULL UNIQUE,
        IdLote INT NOT NULL,
        NombreCultivo VARCHAR(100) NOT NULL,
        Variedad VARCHAR(100) NULL,
        FechaSiembra DATE NOT NULL,
        FechaCosechaEstimada DATE NOT NULL,
        FechaCosechaReal DATE NULL,  -- NULL hasta que se registra la cosecha
        CantidadSembrada INT NOT NULL,
        ProduccionEstimadaKg DECIMAL(12,2) NOT NULL,  -- Meta de produccion
        ProduccionRealKg DECIMAL(12,2) NULL,  -- KPI: se llena al cosechar
        CostoProduccion DECIMAL(14,2) NOT NULL,  -- KPI de costos
        EstadoCultivo VARCHAR(30) NOT NULL,  -- 'Sembrado', 'En crecimiento', 'Cosechado', 'Perdido'
        MetodoCultivo VARCHAR(50) NULL,
        Observaciones VARCHAR(500) NULL,
        CONSTRAINT FK_Cultivo_Lote FOREIGN KEY (IdLote) REFERENCES dbo.Lote(IdLote),
        CONSTRAINT CK_Cultivo_Cantidad CHECK (CantidadSembrada > 0),
        CONSTRAINT CK_Cultivo_Costo CHECK (CostoProduccion >= 0),
        CONSTRAINT CK_Cultivo_Produccion CHECK (
            ProduccionEstimadaKg >= 0 AND
            (ProduccionRealKg IS NULL OR ProduccionRealKg >= 0)
        ),
        CONSTRAINT CK_Cultivo_Fechas CHECK (
            FechaCosechaEstimada >= FechaSiembra AND
            (FechaCosechaReal IS NULL OR FechaCosechaReal >= FechaSiembra)
        )
    );
END;
GO

--------------------------Fin de tablas------------------------

---------------------------Restricciones----------------------------
-- 2. VALIDACIONES ADICIONALES (sin alterar las relaciones).
-- Restriccion 1: la finca solo puede estar Activa o Inactiva
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID('dbo.Finca') AND name = 'CK_Finca_Estado'
)
    ALTER TABLE dbo.Finca ADD CONSTRAINT CK_Finca_Estado
        CHECK (EstadoFinca IN ('Activa','Inactiva'));

-- Restriccion 2: estados permitidos del lote
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID('dbo.Lote') AND name = 'CK_Lote_Estado'
)
    ALTER TABLE dbo.Lote ADD CONSTRAINT CK_Lote_Estado
        CHECK (EstadoLote IN ('Disponible','Ocupado','Descanso','Inactivo'));

-- Restriccion 3: estados permitidos del cultivo
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID('dbo.Cultivo') AND name = 'CK_Cultivo_Estado'
)
    ALTER TABLE dbo.Cultivo ADD CONSTRAINT CK_Cultivo_Estado
        CHECK (EstadoCultivo IN ('Sembrado','En crecimiento','Cosechado','Perdido'));

-- Restriccion 4: un cultivo Cosechado siempre tiene fecha y produccion real
IF NOT EXISTS (
    SELECT 1 FROM sys.check_constraints
    WHERE parent_object_id = OBJECT_ID('dbo.Cultivo') AND name = 'CK_Cultivo_CosechaCompleta'
)
    ALTER TABLE dbo.Cultivo ADD CONSTRAINT CK_Cultivo_CosechaCompleta
        CHECK (EstadoCultivo <> 'Cosechado' OR
               (FechaCosechaReal IS NOT NULL AND ProduccionRealKg IS NOT NULL));
GO

-- Indice unico filtrado: un lote no puede tener dos cultivos activos a la vez
-- Protege contra dos cultivos activos simultaneos en el mismo lote.
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('dbo.Cultivo') AND name = 'UX_Cultivo_UnActivoPorLote'
)
    CREATE UNIQUE INDEX UX_Cultivo_UnActivoPorLote
    ON dbo.Cultivo(IdLote)
    WHERE EstadoCultivo IN ('Sembrado','En crecimiento');
GO

------------------------Fin de Restricciones-------------------------

--------------------------Funciones---------------------
-- 3. FUNCIONES: calculos para reportes.
-- Funcion 1: Calcular el rendimiento (kg por hectarea); devuelve NULL si faltan datos
CREATE OR ALTER FUNCTION dbo.fn_RendimientoKgHa
(
    @Kg DECIMAL(14,2), @Hectareas DECIMAL(10,2)
)
RETURNS DECIMAL(14,2)
AS
BEGIN
    RETURN CASE WHEN @Kg IS NULL OR @Hectareas IS NULL OR @Hectareas <= 0
                THEN NULL ELSE @Kg / @Hectareas END;
END;
GO
-- Funcion 2: Calcular el porcentaje de cumplimiento (produccion real vs estimada)
CREATE OR ALTER FUNCTION dbo.fn_CumplimientoProduccionPct
(
    @KgReal DECIMAL(14,2), @KgEstimado DECIMAL(14,2)
)
RETURNS DECIMAL(12,2)
AS
BEGIN
    RETURN CASE WHEN @KgReal IS NULL OR @KgEstimado IS NULL OR @KgEstimado <= 0
                THEN NULL ELSE @KgReal * 100.0 / @KgEstimado END;
END;
GO
-- Funcion 3: Calcular el costo de produccion por cada kilo cosechado
CREATE OR ALTER FUNCTION dbo.fn_CostoPorKg
(
    @Costo DECIMAL(14,2), @KgReal DECIMAL(14,2)
)
RETURNS DECIMAL(14,2)
AS
BEGIN
    RETURN CASE WHEN @Costo IS NULL OR @KgReal IS NULL OR @KgReal <= 0
                THEN NULL ELSE @Costo / @KgReal END;
END;
GO

--------------------------Fin de Funciones---------------------


--------------------------Triggers----------------------
-- 4. TRIGGERS: validan superficies y actualizan el estado del lote.

IF OBJECT_ID('dbo.trg_Cultivo_AlertaRendimiento', 'TR') IS NOT NULL
    DROP TRIGGER dbo.trg_Cultivo_AlertaRendimiento;
GO
-- Trigger 1: Impide reducir el area de una finca por debajo de la suma de las areas de sus lotes
CREATE OR ALTER TRIGGER dbo.trg_Finca_ValidarArea
ON dbo.Finca
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    -- Solo revisa cuando se modifico el area
    IF NOT UPDATE(AreaTotalHectareas) RETURN;

    IF EXISTS (
        SELECT 1 FROM inserted i
        WHERE i.AreaTotalHectareas < (
            SELECT COALESCE(SUM(l.AreaHectareas),0)
            FROM dbo.Lote l WHERE l.IdFinca = i.IdFinca
        )
    )
    BEGIN
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW 51001, 'No puedes reducir la finca por debajo del area de sus lotes.', 1;
    END;
END;
GO
-- Trigger 2: Valida que los lotes no superen el area de su finca y que un lote con cultivo activo siga Ocupado
CREATE OR ALTER TRIGGER dbo.trg_Lote_ValidarArea
ON dbo.Lote
AFTER INSERT, UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Revision 1: la suma del area de los lotes no puede superar el area de la finca
    IF EXISTS (
        SELECT 1
        FROM dbo.Finca f WITH (UPDLOCK, HOLDLOCK)
        INNER JOIN (SELECT DISTINCT IdFinca FROM inserted) x ON f.IdFinca = x.IdFinca
        WHERE f.AreaTotalHectareas < (
            SELECT COALESCE(SUM(l.AreaHectareas),0)
            FROM dbo.Lote l WHERE l.IdFinca = f.IdFinca
        )
    )
    BEGIN
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW 51002, 'La suma del area de los lotes supera el area de la finca.', 1;
    END;

    -- Revision 2: un lote con cultivo activo no puede pasar a Disponible, Descanso o Inactivo
    IF EXISTS (
        SELECT 1 FROM inserted i
        WHERE i.EstadoLote IN ('Disponible','Descanso','Inactivo')
          AND EXISTS (SELECT 1 FROM dbo.Cultivo c
                      WHERE c.IdLote = i.IdLote
                        AND c.EstadoCultivo IN ('Sembrado','En crecimiento'))
    )
    BEGIN
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW 51003, 'Un lote con cultivo activo debe permanecer Ocupado.', 1;
    END;
END;
GO
-- Trigger 3: Pone el lote Ocupado al sembrar y Disponible al cosechar o perder el cultivo
CREATE OR ALTER TRIGGER dbo.trg_Cultivo_SincronizarEstadoLote
ON dbo.Cultivo
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Evita activar cultivos en lotes que estan inactivos o en descanso.
    IF EXISTS (
        SELECT 1 FROM inserted i
        INNER JOIN dbo.Lote l ON i.IdLote = l.IdLote
        WHERE i.EstadoCultivo IN ('Sembrado','En crecimiento')
          AND l.EstadoLote IN ('Inactivo','Descanso')
    )
    BEGIN
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        THROW 51004, 'No se puede sembrar en un lote inactivo o en descanso.', 1;
    END;

    -- Recalcula el estado: con cultivo activo queda Ocupado; sin cultivo activo vuelve a Disponible
    UPDATE l
    SET EstadoLote = x.NuevoEstado
    FROM dbo.Lote l
    CROSS APPLY (SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM dbo.Cultivo c
            WHERE c.IdLote = l.IdLote
              AND c.EstadoCultivo IN ('Sembrado','En crecimiento')
        ) THEN 'Ocupado'
        WHEN l.EstadoLote = 'Ocupado' THEN 'Disponible'
        ELSE l.EstadoLote END AS NuevoEstado) x
    WHERE l.IdLote IN (
        SELECT IdLote FROM inserted UNION SELECT IdLote FROM deleted
    ) AND l.EstadoLote <> 'Inactivo'
      AND l.EstadoLote <> x.NuevoEstado;
END;
GO

--------------------------Fin de Triggers----------------------


---------------Procedimientos almacenados----------------
-- 5. PROCEDIMIENTOS: operaciones principales desde una interfaz.
-- SP 1: Registrar una finca nueva (valida area, nombre y codigo)
CREATE OR ALTER PROCEDURE dbo.sp_RegistrarFinca
    @CodigoFinca VARCHAR(20),
    @NombreFinca VARCHAR(100),
    @Provincia VARCHAR(50),
    @Canton VARCHAR(50),
    @Distrito VARCHAR(50),
    @Direccion VARCHAR(250),
    @AreaTotalHectareas DECIMAL(10,2),
    @TipoProduccion VARCHAR(30),
    @Responsable VARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    IF @AreaTotalHectareas IS NULL OR @AreaTotalHectareas <= 0
        THROW 51010, 'El area de la finca debe ser positiva.', 1;
    IF NULLIF(LTRIM(RTRIM(@NombreFinca)), '') IS NULL
        THROW 51029, 'Debes indicar el nombre de la finca.', 1;
    IF NULLIF(LTRIM(RTRIM(@CodigoFinca)), '') IS NULL
        THROW 51011, 'Debes indicar un codigo de finca.', 1;

    INSERT INTO dbo.Finca
        (CodigoFinca, NombreFinca, Provincia, Canton, Distrito, Direccion,
         AreaTotalHectareas, TipoProduccion, Responsable, FechaRegistro, EstadoFinca)
    VALUES
        (@CodigoFinca, @NombreFinca, @Provincia, @Canton, @Distrito, @Direccion,
         @AreaTotalHectareas, @TipoProduccion, @Responsable, CAST(GETDATE() AS DATE), 'Activa');

    SELECT SCOPE_IDENTITY() AS IdFinca, @CodigoFinca AS CodigoFinca;
END;
GO
-- SP 2: Registrar un lote en una finca activa (el trigger controla que no supere el area de la finca)
CREATE OR ALTER PROCEDURE dbo.sp_RegistrarLote
    @CodigoLote VARCHAR(20),
    @CodigoFinca VARCHAR(20),
    @NombreLote VARCHAR(100),
    @AreaHectareas DECIMAL(10,2),
    @TipoAmbiente VARCHAR(30),
    @TipoSuelo VARCHAR(50) = NULL,
    @SistemaRiego VARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    DECLARE @IdFinca INT, @Estado VARCHAR(20);

    BEGIN TRAN;
    SELECT @IdFinca = IdFinca, @Estado = EstadoFinca
    FROM dbo.Finca WITH (UPDLOCK, HOLDLOCK)
    WHERE CodigoFinca = @CodigoFinca;

    IF @IdFinca IS NULL OR @Estado <> 'Activa'
    BEGIN
        ROLLBACK;
        THROW 51012, 'La finca no existe o esta inactiva.', 1;
    END;

    IF NULLIF(LTRIM(RTRIM(@NombreLote)), '') IS NULL
    BEGIN
        ROLLBACK;
        THROW 51030, 'Debes indicar el nombre del lote.', 1;
    END;

    IF NULLIF(LTRIM(RTRIM(@CodigoLote)), '') IS NULL
    BEGIN
        ROLLBACK;
        THROW 51032, 'Debes indicar un codigo de lote.', 1;
    END;

    IF @AreaHectareas IS NULL OR @AreaHectareas <= 0
    BEGIN
        ROLLBACK;
        THROW 51013, 'El area del lote debe ser positiva.', 1;
    END;

    INSERT INTO dbo.Lote
        (CodigoLote, IdFinca, NombreLote, AreaHectareas, TipoSuelo,
         SistemaRiego, TipoAmbiente, EstadoLote, FechaRegistro)
    VALUES
        (@CodigoLote, @IdFinca, @NombreLote, @AreaHectareas, @TipoSuelo,
         @SistemaRiego, @TipoAmbiente, 'Disponible', CAST(GETDATE() AS DATE));

    DECLARE @IdLote INT = SCOPE_IDENTITY();
    COMMIT;
    SELECT @IdLote AS IdLote, @CodigoLote AS CodigoLote;
END;
GO
-- SP 3: Registrar la siembra de un cultivo en un lote (el lote pasa a Ocupado)
CREATE OR ALTER PROCEDURE dbo.sp_RegistrarSiembra
    @CodigoCultivo VARCHAR(20),
    @CodigoLote VARCHAR(20),
    @NombreCultivo VARCHAR(100),
    @FechaSiembra DATE,
    @FechaCosechaEstimada DATE,
    @CantidadSembrada INT,
    @ProduccionEstimadaKg DECIMAL(12,2),
    @CostoProduccion DECIMAL(14,2),
    @Variedad VARCHAR(100) = NULL,
    @MetodoCultivo VARCHAR(50) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    DECLARE @IdLote INT, @EstadoLote VARCHAR(20), @EstadoFinca VARCHAR(20);

    IF NULLIF(LTRIM(RTRIM(@CodigoCultivo)), '') IS NULL
        THROW 51033, 'Debes indicar un codigo de cultivo.', 1;
    IF NULLIF(LTRIM(RTRIM(@NombreCultivo)), '') IS NULL
        THROW 51031, 'Debes indicar el nombre del cultivo.', 1;
    IF @FechaSiembra IS NULL OR @FechaCosechaEstimada IS NULL OR @FechaCosechaEstimada < @FechaSiembra
        THROW 51014, 'Fechas de siembra y cosecha estimada invalidas.', 1;
    IF @CantidadSembrada IS NULL OR @CantidadSembrada <= 0 OR
       @ProduccionEstimadaKg IS NULL OR @ProduccionEstimadaKg <= 0 OR
       @CostoProduccion IS NULL OR @CostoProduccion < 0
        THROW 51015, 'Cantidad, produccion estimada o costo invalidos.', 1;

    BEGIN TRAN;
    SELECT @IdLote = l.IdLote, @EstadoLote = l.EstadoLote,
           @EstadoFinca = f.EstadoFinca
    FROM dbo.Lote l WITH (UPDLOCK, HOLDLOCK)
    INNER JOIN dbo.Finca f ON l.IdFinca = f.IdFinca
    WHERE l.CodigoLote = @CodigoLote;

    IF @IdLote IS NULL OR @EstadoFinca <> 'Activa' OR
       @EstadoLote IN ('Descanso','Inactivo')
    BEGIN
        ROLLBACK;
        THROW 51016, 'El lote no existe o no permite siembras.', 1;
    END;

    -- Un lote solo puede tener un cultivo activo
    IF EXISTS (SELECT 1 FROM dbo.Cultivo
               WHERE IdLote = @IdLote AND EstadoCultivo IN ('Sembrado','En crecimiento'))
    BEGIN
        ROLLBACK;
        THROW 51017, 'Este lote ya tiene un cultivo activo.', 1;
    END;

    INSERT INTO dbo.Cultivo
        (CodigoCultivo, IdLote, NombreCultivo, Variedad,
         FechaSiembra, FechaCosechaEstimada, FechaCosechaReal,
         CantidadSembrada, ProduccionEstimadaKg, ProduccionRealKg,
         CostoProduccion, EstadoCultivo, MetodoCultivo)
    VALUES
        (@CodigoCultivo, @IdLote, @NombreCultivo, @Variedad,
         @FechaSiembra, @FechaCosechaEstimada, NULL,
         @CantidadSembrada, @ProduccionEstimadaKg, NULL,
         @CostoProduccion, 'En crecimiento', @MetodoCultivo);

    DECLARE @IdCultivo INT = SCOPE_IDENTITY();
    COMMIT;
    SELECT @IdCultivo AS IdCultivo, @CodigoCultivo AS CodigoCultivo;
END;
GO
-- SP 4: Actualizar produccion estimada, fecha estimada o costo de un cultivo activo
CREATE OR ALTER PROCEDURE dbo.sp_ActualizarCultivo
    @CodigoCultivo VARCHAR(20),
    @ProduccionEstimadaKg DECIMAL(12,2) = NULL,
    @FechaCosechaEstimada DATE = NULL,
    @CostoProduccion DECIMAL(14,2) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM dbo.Cultivo
                   WHERE CodigoCultivo = @CodigoCultivo AND EstadoCultivo IN ('Sembrado','En crecimiento'))
        THROW 51018, 'Solo puedes editar cultivos activos existentes.', 1;
    IF @ProduccionEstimadaKg IS NOT NULL AND @ProduccionEstimadaKg <= 0
        THROW 51019, 'La produccion estimada debe ser positiva.', 1;
    IF @CostoProduccion IS NOT NULL AND @CostoProduccion < 0
        THROW 51020, 'El costo no puede ser negativo.', 1;
    IF @FechaCosechaEstimada IS NOT NULL AND EXISTS (
        SELECT 1 FROM dbo.Cultivo
        WHERE CodigoCultivo = @CodigoCultivo AND FechaSiembra > @FechaCosechaEstimada
    ) THROW 51021, 'La cosecha estimada no puede preceder a la siembra.', 1;

    UPDATE dbo.Cultivo
    SET ProduccionEstimadaKg = COALESCE(@ProduccionEstimadaKg, ProduccionEstimadaKg),
        FechaCosechaEstimada = COALESCE(@FechaCosechaEstimada, FechaCosechaEstimada),
        CostoProduccion = COALESCE(@CostoProduccion, CostoProduccion)
    WHERE CodigoCultivo = @CodigoCultivo
      AND EstadoCultivo IN ('Sembrado','En crecimiento');
    IF @@ROWCOUNT = 0 THROW 51027, 'El cultivo dejo de estar activo antes de actualizarse.', 1;
END;
GO
-- SP 5: Registrar la cosecha de un cultivo (pasa a Cosechado y el lote queda Disponible)
CREATE OR ALTER PROCEDURE dbo.sp_RegistrarCosecha
    @CodigoCultivo VARCHAR(20),
    @ProduccionRealKg DECIMAL(12,2),
    @FechaCosechaReal DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    SET @FechaCosechaReal = COALESCE(@FechaCosechaReal, CAST(GETDATE() AS DATE));

    IF @ProduccionRealKg IS NULL OR @ProduccionRealKg < 0
        THROW 51022, 'La cosecha no puede tener kilos negativos.', 1;
    IF @FechaCosechaReal > CAST(GETDATE() AS DATE)
        THROW 51023, 'No puedes registrar una cosecha futura.', 1;

    BEGIN TRAN;
    DECLARE @FechaSiembra DATE, @EstadoCultivo VARCHAR(30);
    SELECT @FechaSiembra = FechaSiembra, @EstadoCultivo = EstadoCultivo
    FROM dbo.Cultivo WITH (UPDLOCK, HOLDLOCK)
    WHERE CodigoCultivo = @CodigoCultivo;

    IF @EstadoCultivo IS NULL OR @EstadoCultivo NOT IN ('Sembrado','En crecimiento')
    BEGIN
        ROLLBACK;
        THROW 51024, 'El cultivo no existe o ya no esta activo.', 1;
    END;
    IF @FechaCosechaReal < @FechaSiembra
    BEGIN
        ROLLBACK;
        THROW 51025, 'La cosecha no puede preceder a la siembra.', 1;
    END;

    -- Guarda la produccion real y cambia el estado del cultivo a Cosechado
    UPDATE dbo.Cultivo
    SET FechaCosechaReal = @FechaCosechaReal,
        ProduccionRealKg = @ProduccionRealKg,
        EstadoCultivo = 'Cosechado'
    WHERE CodigoCultivo = @CodigoCultivo;

    COMMIT;
    SELECT CodigoCultivo, EstadoCultivo, ProduccionRealKg, FechaCosechaReal
    FROM dbo.Cultivo WHERE CodigoCultivo = @CodigoCultivo;
END;
GO
-- SP 6: Marcar un cultivo activo como perdido (libera el lote)
CREATE OR ALTER PROCEDURE dbo.sp_MarcarCultivoPerdido
    @CodigoCultivo VARCHAR(20)
AS
BEGIN
    SET NOCOUNT ON;
    IF NOT EXISTS (SELECT 1 FROM dbo.Cultivo
                   WHERE CodigoCultivo = @CodigoCultivo AND EstadoCultivo IN ('Sembrado','En crecimiento'))
        THROW 51026, 'Solo puedes marcar como perdido un cultivo activo.', 1;

    UPDATE dbo.Cultivo
    SET EstadoCultivo = 'Perdido'
    WHERE CodigoCultivo = @CodigoCultivo AND EstadoCultivo IN ('Sembrado','En crecimiento');
    IF @@ROWCOUNT = 0 THROW 51028, 'El cultivo ya no esta activo.', 1;
END;
GO

---------------Fin de Procedimientos almacenados----------------


------------------------Vistas---------------------------
-- 6. VISTAS: reportes listos para SELECT y graficos en Python.
-- Vista 1: Trazabilidad de cada cultivo (finca, lote, fechas, produccion) y alerta de rendimiento (< 85% de lo estimado)
CREATE OR ALTER VIEW dbo.vw_Prod_Trazabilidad
AS
SELECT c.CodigoCultivo, c.NombreCultivo, c.Variedad,
       f.CodigoFinca, f.NombreFinca, f.Provincia,
       l.CodigoLote, l.NombreLote, l.AreaHectareas,
       c.FechaSiembra, c.FechaCosechaEstimada, c.FechaCosechaReal,
       c.EstadoCultivo, c.ProduccionEstimadaKg, c.ProduccionRealKg,
       c.CostoProduccion,
       dbo.fn_CumplimientoProduccionPct(c.ProduccionRealKg, c.ProduccionEstimadaKg) AS CumplimientoPct,
       CASE WHEN c.EstadoCultivo <> 'Cosechado' THEN 'Sin cosechar'
            WHEN c.ProduccionRealKg < c.ProduccionEstimadaKg * 0.85 THEN 'Bajo rendimiento'
            ELSE 'Rendimiento aceptable' END AS AlertaRendimiento
FROM dbo.Cultivo c
INNER JOIN dbo.Lote l ON l.IdLote = c.IdLote
INNER JOIN dbo.Finca f ON f.IdFinca = l.IdFinca;
GO
-- Vista 2: Cultivos activos y dias que faltan para su cosecha
CREATE OR ALTER VIEW dbo.vw_Prod_CultivosActivos
AS
SELECT c.CodigoCultivo, c.NombreCultivo, f.NombreFinca, l.CodigoLote,
       c.FechaSiembra, c.FechaCosechaEstimada, c.EstadoCultivo,
       c.ProduccionEstimadaKg,
       DATEDIFF(DAY, CAST(GETDATE() AS DATE), c.FechaCosechaEstimada) AS DiasParaCosecha
FROM dbo.Cultivo c
INNER JOIN dbo.Lote l ON l.IdLote = c.IdLote
INNER JOIN dbo.Finca f ON f.IdFinca = l.IdFinca
WHERE c.EstadoCultivo IN ('Sembrado','En crecimiento');
GO
-- Vista 3: KPI de produccion por finca (lotes, cultivos, kg cosechados y costos)
CREATE OR ALTER VIEW dbo.vw_Prod_KPI_Finca
AS
SELECT f.CodigoFinca, f.NombreFinca,
       COUNT(DISTINCT l.IdLote) AS TotalLotes,
       COUNT(DISTINCT c.IdCultivo) AS TotalCultivos,
       COUNT(DISTINCT CASE WHEN c.EstadoCultivo IN ('Sembrado','En crecimiento')
                            THEN c.IdCultivo END) AS CultivosActivos,
       SUM(CASE WHEN c.EstadoCultivo = 'Cosechado' THEN c.ProduccionRealKg ELSE 0 END) AS KgCosechados,
       SUM(CASE WHEN c.EstadoCultivo = 'Cosechado' THEN c.CostoProduccion ELSE 0 END) AS CostoCosechas
FROM dbo.Finca f
LEFT JOIN dbo.Lote l ON l.IdFinca = f.IdFinca
LEFT JOIN dbo.Cultivo c ON c.IdLote = l.IdLote
GROUP BY f.CodigoFinca, f.NombreFinca;
GO
-- Vista 4: KPI por tipo de cultivo (cumplimiento, costo por kg y rendimiento por hectarea)
CREATE OR ALTER VIEW dbo.vw_Prod_KPI_Cultivo
AS
SELECT c.NombreCultivo,
       COUNT(*) AS NumeroCosechas,
       SUM(c.ProduccionEstimadaKg) AS KgEstimados,
       SUM(c.ProduccionRealKg) AS KgReales,
       dbo.fn_CumplimientoProduccionPct(SUM(c.ProduccionRealKg), SUM(c.ProduccionEstimadaKg)) AS CumplimientoPct,
       dbo.fn_CostoPorKg(SUM(c.CostoProduccion), SUM(c.ProduccionRealKg)) AS CostoPorKg,
       dbo.fn_RendimientoKgHa(SUM(c.ProduccionRealKg), SUM(l.AreaHectareas)) AS RendimientoKgHa
FROM dbo.Cultivo c
INNER JOIN dbo.Lote l ON l.IdLote = c.IdLote
WHERE c.EstadoCultivo = 'Cosechado'
GROUP BY c.NombreCultivo;
GO

------------------------Fin de Vistas---------------------------

-- 7. COMPROBACIONES (solo lectura: no generan datos ficticios).
SELECT * FROM dbo.Finca;
SELECT * FROM dbo.Lote;
SELECT * FROM dbo.Cultivo;
SELECT * FROM dbo.vw_Prod_Trazabilidad;
SELECT * FROM dbo.vw_Prod_CultivosActivos;
SELECT * FROM dbo.vw_Prod_KPI_Finca;
SELECT * FROM dbo.vw_Prod_KPI_Cultivo;
GO

