"""
produccion_service.py  

Contiene Todo lo que habla con SQL Server (la interfaz no toca la base de datos directamente):
  1. Configuracion y conexion (se abre y se cierra en cada operación).
  2. Consultas a las vistas y tablas.
  3. Ejecución de procedimientos almacenados con commit / rollback.
  4. Validaciones de los formularios (se ejecutan ANTES de llamar a los procedimientos).


"""

import os
import re
from contextlib import contextmanager
from datetime import date

import pandas as pd
import pyodbc

# ==============================================================================
# 1. CONFIGURACIÓN LOCAL
# ==============================================================================
# Estos son tus datos de conexión. Si algún día cambian, puedes definir las variables
# de entorno PROD_DB_SERVIDOR / PROD_DB_NOMBRE sin tocar el código.
SERVIDOR = os.getenv("PROD_DB_SERVIDOR", r"localhost\SQLEXPRESS")
BASE_DATOS = os.getenv("PROD_DB_NOMBRE", "William’s Agribusiness")  # OJO: el apóstrofo es ’ (curvo), igual que en SSMS

# Lista blanca de vistas: evita armar SQL con nombres que no sean los tuyos.
VISTAS_VALIDAS = {
    "vw_Prod_Trazabilidad",
    "vw_Prod_CultivosActivos",
    "vw_Prod_KPI_Finca",
    "vw_Prod_KPI_Cultivo",
}


def _elegir_driver():
    """Usa el ODBC Driver más nuevo instalado (18, 17...). Si no hay, el driver antiguo 'SQL Server'."""
    drivers = sorted(
        [d for d in pyodbc.drivers() if d.startswith("ODBC Driver") and "SQL Server" in d],
        reverse=True,
    )
    return drivers[0] if drivers else "SQL Server"


def _cadena_conexion():
    # Las llaves {} permiten nombres con espacios/apóstrofos. Trusted_Connection = autenticación de Windows.
    return (
        "DRIVER={" + _elegir_driver() + "};"
        "SERVER=" + SERVIDOR + ";"
        "DATABASE={" + BASE_DATOS + "};"
        "Trusted_Connection=yes;TrustServerCertificate=yes;"
    )


@contextmanager
def conexion():
    """Abre una conexión y la CIERRA siempre al terminar (aunque ocurra un error)."""
    conn = pyodbc.connect(_cadena_conexion(), timeout=10)  # timeout: no se queda colgado si el servidor no responde
    try:
        yield conn
    finally:
        conn.close()


# ==============================================================================
# 2. CONSULTAS (solo lectura)
# ==============================================================================
def consultar(sql, params=None):
    """Ejecuta un SELECT parametrizado y devuelve un DataFrame (con columnas aunque no haya filas)."""
    with conexion() as conn:
        cur = conn.cursor()
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        columnas = [c[0] for c in cur.description]
        filas = [tuple(f) for f in cur.fetchall()]
    # coerce_float convierte Decimal de SQL Server a float (necesario para sumas y gráficos)
    return pd.DataFrame.from_records(filas, columns=columnas, coerce_float=True)


def cargar_vista(nombre_vista):
    """Lee una de las 4 vistas del módulo."""
    if nombre_vista not in VISTAS_VALIDAS:
        raise ValueError(f"Vista no permitida: {nombre_vista}")
    return consultar(f"SELECT * FROM dbo.{nombre_vista}")


def consultar_fincas():
    """Todas las fincas registradas (con todas sus columnas: área, estado, etc.)."""
    return consultar("SELECT * FROM dbo.Finca ORDER BY CodigoFinca")


def consultar_lotes():
    """Todos los lotes junto con el nombre de su finca."""
    try:
        return consultar(
            "SELECT l.*, f.NombreFinca FROM dbo.Lote AS l "
            "LEFT JOIN dbo.Finca AS f ON f.CodigoFinca = l.CodigoFinca "
            "ORDER BY l.CodigoLote"
        )
    except pyodbc.Error:
        # Si la tabla Lote relaciona la finca con otra columna, se muestran los lotes tal cual.
        return consultar("SELECT * FROM dbo.Lote ORDER BY CodigoLote")


def consultar_codigos_cultivo():
    """Códigos de cultivo existentes (para sugerir el siguiente código)."""
    return consultar("SELECT CodigoCultivo FROM dbo.Cultivo")


def siguiente_codigo(prefijo, codigos):
    """Sugiere el próximo código: FIN-004, LOT-005, CUL-005... (funciona con tablas vacías: FIN-001)."""
    numeros = [int(m.group(1)) for c in codigos if (m := re.fullmatch(rf"{prefijo}-(\d+)", str(c)))]
    return f"{prefijo}-{(max(numeros) + 1 if numeros else 1):03d}"


# ==============================================================================
# 3. EJECUCIÓN DE PROCEDIMIENTOS ALMACENADOS
# ==============================================================================
def _limpiar_error(e):
    """Deja solo el mensaje de SQL Server (el que escriben tus SP y triggers con RAISERROR/THROW)."""
    texto = str(e.args[-1]) if e.args else str(e)
    texto = texto.split("]")[-1].split("(SQLExecDirectW)")[0].strip()
    texto = re.sub(r"\(\d+\)\s*$", "", texto).strip()
    if "UX_Cultivo_UnActivoPorLote" in texto:
        return "Este lote ya tiene un cultivo activo."
    if "UNIQUE" in texto.upper() or "duplicate key" in texto.lower():
        return "Ese código ya existe. Usa uno diferente."
    return texto


def ejecutar_sp(sql, params):
    """
    Ejecuta un procedimiento almacenado con parámetros (?) dentro de una transacción.
      - Éxito  -> commit  -> devuelve (True, DataFrame o None)
      - Error  -> rollback -> devuelve (False, mensaje legible)
    La conexión se cierra siempre.
    """
    try:
        with conexion() as conn:
            try:
                cur = conn.cursor()
                cur.execute(sql, params)

                # Se recorren todos los resultados del SP: así pyodbc también reporta los errores
                # que ocurran después de la primera instrucción (por ejemplo, desde un trigger).
                resultado = None
                while True:
                    if cur.description and resultado is None:
                        filas = [tuple(f) for f in cur.fetchall()]
                        resultado = pd.DataFrame.from_records(
                            filas, columns=[c[0] for c in cur.description], coerce_float=True
                        )
                    if not cur.nextset():
                        break

                conn.commit()
                return True, resultado
            except Exception:
                conn.rollback()  # deshace todo lo que alcanzó a hacer el SP
                raise
    except pyodbc.Error as e:
        return False, _limpiar_error(e)
    except Exception as e:  # cualquier otro fallo inesperado
        return False, f"Error inesperado: {e}"


# ==============================================================================
# 4. VALIDACIONES (devuelven una lista de mensajes; lista vacía = todo correcto)
# ==============================================================================
def _vacio(valor):
    return valor is None or not str(valor).strip()


def _validar_codigo(codigo, etiqueta, errores):
    if _vacio(codigo):
        errores.append(f"El {etiqueta} es obligatorio.")
    elif not re.fullmatch(r"[A-Za-z0-9_-]{1,20}", str(codigo).strip()):
        errores.append(f"El {etiqueta} solo puede tener letras, números, guion y guion bajo (máx. 20 caracteres).")


def _validar_textos(campos, errores):
    """campos = {'Nombre de la finca': valor, ...}: todos son obligatorios."""
    for etiqueta, valor in campos.items():
        if _vacio(valor):
            errores.append(f"{etiqueta} es obligatorio.")


def validar_finca(codigo, nombre, provincia, canton, distrito, direccion, area, responsable):
    errores = []
    _validar_codigo(codigo, "código de finca", errores)
    _validar_textos({"El nombre de la finca": nombre, "La provincia": provincia, "El cantón": canton,
                     "El distrito": distrito, "La dirección": direccion, "El responsable": responsable}, errores)
    if area is None or area <= 0:
        errores.append("El área total debe ser mayor que 0.")
    return errores


def validar_lote(codigo, codigo_finca, nombre, area):
    errores = []
    _validar_codigo(codigo, "código de lote", errores)
    if _vacio(codigo_finca):
        errores.append("Debes seleccionar una finca.")
    _validar_textos({"El nombre del lote": nombre}, errores)
    if area is None or area <= 0:
        errores.append("El área del lote debe ser mayor que 0.")
    return errores


def validar_siembra(codigo, codigo_lote, nombre, variedad, f_siembra, f_estimada, cantidad, prod_estimada, costo):
    errores = []
    _validar_codigo(codigo, "código de cultivo", errores)
    if _vacio(codigo_lote):
        errores.append("Debes seleccionar un lote disponible.")
    _validar_textos({"El nombre del cultivo": nombre, "La variedad": variedad}, errores)
    if f_estimada <= f_siembra:
        errores.append("La cosecha estimada debe ser posterior a la fecha de siembra.")
    if cantidad is None or cantidad < 1:
        errores.append("La cantidad sembrada debe ser al menos 1.")
    if prod_estimada is None or prod_estimada <= 0:
        errores.append("La producción estimada debe ser mayor que 0.")
    if costo is None or costo < 0:
        errores.append("El costo de producción no puede ser negativo.")
    return errores


def validar_cosecha(codigo_cultivo, kg_reales, fecha):
    errores = []
    if _vacio(codigo_cultivo):
        errores.append("Debes seleccionar un cultivo.")
    if kg_reales is None or kg_reales <= 0:
        errores.append("La producción real debe ser mayor que 0 kg.")
    if fecha > date.today():
        errores.append("La fecha de cosecha no puede ser futura.")
    return errores


def validar_actualizacion(codigo_cultivo, nueva_prod, nuevo_costo, cambiar_fecha, nueva_fecha):
    errores = []
    if _vacio(codigo_cultivo):
        errores.append("Debes seleccionar un cultivo activo.")
    if not nueva_prod and not nuevo_costo and not cambiar_fecha:
        errores.append("Indica al menos un cambio (producción, costo o fecha estimada).")
    if nueva_prod < 0 or nuevo_costo < 0:
        errores.append("Los valores no pueden ser negativos.")
    if cambiar_fecha and nueva_fecha < date.today():
        errores.append("La nueva fecha de cosecha estimada no puede ser anterior a hoy.")
    return errores
