import pyodbc

CADENA_CONEXION = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=SEBASTIÁN\\SQLDEVELOPER;"
    "DATABASE=BDWilliamsAgribusiness;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def obtener_conexion():
    return pyodbc.connect(CADENA_CONEXION)