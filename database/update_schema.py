# database/update_schema.py
from database.conexion import Database
import os

def actualizar_base_datos():
    """Añade las tablas de ventas a la base de datos existente."""
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()

    # Crear tabla ventas si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            folio TEXT UNIQUE NOT NULL,
            usuario_id INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0 CHECK (total >= 0),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE RESTRICT
        )
    """)

    # Crear tabla detalle_venta si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detalle_venta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            precio_unitario REAL NOT NULL CHECK (precio_unitario > 0),
            subtotal REAL NOT NULL CHECK (subtotal > 0),
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE RESTRICT
        )
    """)

    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ventas_folio ON ventas(folio)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ventas_fecha ON ventas(fecha)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ventas_usuario ON ventas(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detalle_venta ON detalle_venta(venta_id)")

    conn.commit()
    print("✅ Tablas de ventas añadidas correctamente")

if __name__ == "__main__":
    actualizar_base_datos()