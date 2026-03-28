
from database.conexion import Database
from database.init_db import inicializar_base_datos

if __name__ == "__main__":
    # 1. Inicializar (crear las tablas si no existen)
    print("--- Inicializando DB ---")
    inicializar_base_datos()

    # 2. Probar la conexión y una consulta simple
    print("\n--- Probando Consulta ---")
    db = Database()

    # Obtener todos los usuarios
    usuarios = db.fetch_all("SELECT * FROM usuarios")
    print("Usuarios en la DB:")
    for user in usuarios:
        # Como usamos row_factory, podemos acceder por el nombre de la columna
        print(f"  ID: {user['id']}, Usuario: {user['username']}, Nombre: {user['nombre_completo']}, Rol: {user['rol']}")

    # Obtener todos los productos
    productos = db.fetch_all("SELECT * FROM productos")
    print("\nProductos en la DB:")
    for prod in productos:
        print(f"  {prod['codigo']} - {prod['nombre']} - ${prod['precio_venta']} - Stock: {prod['stock']}")

    # 3. Cerrar conexión
    db.close_connection()