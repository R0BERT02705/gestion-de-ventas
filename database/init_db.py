# database/init_db.py
import sqlite3
import os
from pathlib import Path

def init_database():
    """Inicializa la base de datos con el schema.sql"""
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / "gestion_ventas.db"
    schema_path = Path(__file__).parent / "schema.sql"
    
    print(f"Inicializando base de datos en: {db_path}")
    
    # Eliminar base de datos existente si quieres empezar fresco
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Base de datos anterior eliminada")
    
    # Conectar a la nueva base de datos
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    
    # Leer y ejecutar schema.sql
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Ejecutar el script SQL
    conn.executescript(schema)
    conn.commit()
    
    print("Base de datos inicializada correctamente")
    
    # Verificar datos
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM usuarios")
    usuarios_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) as count FROM productos")
    productos_count = cursor.fetchone()['count']
    
    print(f"Usuarios creados: {usuarios_count}")
    print(f"Productos creados: {productos_count}")
    
    conn.close()
    return True

if __name__ == "__main__":
    init_database()