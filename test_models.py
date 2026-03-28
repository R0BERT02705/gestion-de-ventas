# test_models.py
from database.init_db import inicializar_base_datos
from database.update_schema import actualizar_base_datos
from models import Usuario, Producto, Venta

def probar_modelos():
    print("=== INICIALIZANDO BASE DE DATOS ===")
    inicializar_base_datos()
    actualizar_base_datos()

    print("\n=== PROBANDO MODELO USUARIO ===")
    # Autenticar
    usuario = Usuario.autenticar("admin", "admin123")
    print(f"Login admin: {usuario}")

    # Listar usuarios
    print("\nUsuarios activos:")
    for u in Usuario.listar_activos():
        print(f"  - {u}")

    print("\n=== PROBANDO MODELO PRODUCTO ===")
    # Buscar productos
    productos = Producto.buscar("laptop")
    print(f"Búsqueda 'laptop': {len(productos)} resultados")
    for p in productos:
        print(f"  - {p}")

    # Productos con stock bajo
    print("\nProductos con stock bajo (<=5):")
    for p in Producto.listar_con_stock_bajo(5):
        print(f"  - {p} - Stock: {p.stock}")

    print("\n=== PROBANDO CREACIÓN DE VENTA ===")
    # Crear una venta de ejemplo
    vendedor = Usuario.obtener_por_id(1)  # admin
    venta = Venta(usuario=vendedor)

    # Agregar productos
    laptop = Producto.obtener_por_codigo("P001")
    mouse = Producto.obtener_por_codigo("P002")

    if laptop and mouse:
        venta.agregar_producto(laptop, 1)
        venta.agregar_producto(mouse, 2)

        print(f"Venta creada con {len(venta.detalles)} productos")
        print(f"Total: ${venta.total:.2f}")

        # Guardar venta
        try:
            venta.guardar()
            print(f"✅ Venta guardada con folio: {venta.folio}")
        except Exception as e:
            print(f"❌ Error al guardar venta: {e}")

    print("\n=== PROBANDO ESTADÍSTICAS ===")
    stats = Venta.obtener_estadisticas()
    print("Estadísticas del período:")
    print(f"  Total ventas: {stats['resumen'].get('total_ventas', 0)}")
    print(f"  Ingresos totales: ${stats['resumen'].get('ingresos_totales', 0):.2f}")
    print(f"  Ticket promedio: ${stats['resumen'].get('ticket_promedio', 0):.2f}")

    if stats['top_productos']:
        print("\nTop productos vendidos:")
        for p in stats['top_productos']:
            print(f"  - {p['nombre']}: {p['cantidad_vendida']} unidades")

if __name__ == "__main__":
    probar_modelos()