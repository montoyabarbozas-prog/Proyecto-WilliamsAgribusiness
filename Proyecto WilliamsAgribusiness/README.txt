WILLIAM'S AGRIBUSINESS - INTERFAZ INICIAL

Instalación:
  py -m pip install -r requirements.txt

Ejecución:
  py main.py

Estructura:
  main.py                         Punto de entrada
  interfaz/app.py                 Ventana principal y navegación
  interfaz/config.py              Módulos, tablas y campos
  interfaz/vistas/dashboard.py    Panel principal
  interfaz/vistas/modulo.py       Pantalla reutilizable para los módulos

Esta versión es únicamente interfaz gráfica. No conecta a SQL Server ni realiza
operaciones reales de guardar, consultar, actualizar o eliminar. Los botones
muestran un aviso indicando que la conexión se agregará después.

Módulos incluidos:
  Clientes: SegmentoCliente, Cliente, ContactoCliente
  Contratos: Contrato, DetalleContrato
  Producción: Finca, Lote, Cultivo
  Inventario: Producto, Inventario, MovimientoInventario
  Ventas y entregas: Venta, DetalleVenta, Entrega
