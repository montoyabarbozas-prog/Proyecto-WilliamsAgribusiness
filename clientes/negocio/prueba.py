import os

# La conexión de tu compañero lee estas variables al importar: se definen ANTES del import.
os.environ["PROD_DB_NOMBRE"] = "BDWilliamsAgribusiness"
# os.environ["PROD_DB_SERVIDOR"] = r"localhost\SQLEXPRESS"   # solo si tu servidor es otro

from clientes_service import (cargar_vista_clientes, cambiar_estado_cliente,
                              siguiente_codigo_cliente, consultar_segmentos,
                              crear_contrato)
from datetime import date

print("--- Vista de clientes activos ---")
print(cargar_vista_clientes("vw_ClientesActivos"))

print("--- Segmentos ---")
print(consultar_segmentos())

print("--- Siguiente código sugerido ---")
print(siguiente_codigo_cliente())          # CLI-0009

print("--- Cliente que no existe (debe dar False) ---")
print(cambiar_estado_cliente("CLI-9999", "Activo"))

print("--- Estado inválido, lo frena Python (False) ---")
print(cambiar_estado_cliente("CLI-0001", "Congelado"))

print("--- Contrato con fechas al revés, lo frena Python (False) ---")
print(crear_contrato("CT-2026-900", "CLI-0003", "Por volumen",
                     date(2027, 12, 31), date(2027, 1, 1), "Semanal",
                     5000000, 5, 2, 1, 100, "kg", 1500))